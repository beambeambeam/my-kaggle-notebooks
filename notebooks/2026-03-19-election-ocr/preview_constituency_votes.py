from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


DOC_ID_PATTERN = re.compile(r"^constituency_(\d+)_(\d+)$")


class PreviewError(Exception):
    """Raised when the preview cannot be produced safely."""


@dataclass(frozen=True)
class ResolvedConstituency:
    province_id: int
    area_id: int
    province_name: str
    expected_area_name: str
    province_dir: Path
    area_dir: Path
    candidate_csv_path: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview constituency vote rows by resolving the matching candidate CSV."
    )
    parser.add_argument(
        "--doc-id",
        required=True,
        help="Constituency document id, for example constituency_10_1",
    )
    return parser


def normalize_party_name(name: str) -> str:
    normalized = name.strip()
    if normalized.startswith("พรรค"):
        normalized = normalized.removeprefix("พรรค").strip()
    return normalized


def similarity_ratio(left: str, right: str) -> float:
    return SequenceMatcher(None, left, right).ratio()


def load_submission_rows(submission_csv_path: Path, doc_id: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with submission_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["doc_id"] == doc_id:
                rows.append(row)
    if not rows:
        raise PreviewError(f"doc_id '{doc_id}' was not found in {submission_csv_path}")
    return rows


def load_area_lookup(areas_csv_path: Path) -> tuple[dict[int, str], dict[tuple[int, int], str]]:
    province_names: dict[int, str] = {}
    area_names: dict[tuple[int, int], str] = {}

    with areas_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            province_id = int(row["provinceId"])
            area_id = int(row["areaId"])
            province_names.setdefault(province_id, row["provinceWord"].strip())
            area_names.setdefault((province_id, area_id), row["areaWords"].strip())

    return province_names, area_names


def choose_best_path(expected_name: str, candidates: list[Path]) -> tuple[Path, float]:
    if not candidates:
        raise PreviewError(f"No candidates available to match '{expected_name}'")

    best_path = max(candidates, key=lambda candidate: similarity_ratio(expected_name, candidate.name))
    return best_path, similarity_ratio(expected_name, best_path.name)


def resolve_constituency(
    doc_id: str,
    province_names: dict[int, str],
    area_names: dict[tuple[int, int], str],
    all_constituency_dir: Path,
) -> ResolvedConstituency:
    province_id, area_id = parse_constituency_doc_id(doc_id)

    province_name = province_names.get(province_id)
    if province_name is None:
        raise PreviewError(f"province_id {province_id} was not found in area lookup data")

    expected_area_name = area_names.get((province_id, area_id))
    if expected_area_name is None:
        raise PreviewError(
            f"area_id {area_id} is not valid for province_id {province_id} in area lookup data"
        )

    province_dirs = [path for path in all_constituency_dir.iterdir() if path.is_dir()]
    province_dir, _province_score = choose_best_path(province_name, province_dirs)

    area_dirs = [path for path in province_dir.iterdir() if path.is_dir()]
    numbered_area_dirs = [path for path in area_dirs if path.name.endswith(f"เขต {area_id}")]
    matching_pool = numbered_area_dirs or area_dirs
    area_dir, _area_score = choose_best_path(expected_area_name, matching_pool)

    candidate_csv_path = area_dir / "constituency_candidates.csv"
    if not candidate_csv_path.exists():
        raise PreviewError(f"Candidate CSV not found at {candidate_csv_path}")

    return ResolvedConstituency(
        province_id=province_id,
        area_id=area_id,
        province_name=province_name,
        expected_area_name=expected_area_name,
        province_dir=province_dir,
        area_dir=area_dir,
        candidate_csv_path=candidate_csv_path,
    )


def parse_constituency_doc_id(doc_id: str) -> tuple[int, int]:
    match = DOC_ID_PATTERN.fullmatch(doc_id)
    if match is None:
        raise PreviewError(
            "doc_id must match 'constituency_<province_id>_<area_id>'; "
            f"got '{doc_id}'"
        )
    return int(match.group(1)), int(match.group(2))


def load_candidate_rows(candidate_csv_path: Path) -> list[dict[str, str]]:
    with candidate_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_candidate_lookup(
    candidate_rows: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []

    for row in candidate_rows:
        normalized = normalize_party_name(row["party.name"])
        if normalized in lookup:
            duplicates.append(normalized)
        lookup[normalized] = row

    if duplicates:
        duplicate_list = ", ".join(sorted(set(duplicates)))
        raise PreviewError(
            "Duplicate normalized party names found in candidate CSV: "
            f"{duplicate_list}"
        )

    return lookup


def best_party_suggestion(
    party_name: str, candidate_lookup: dict[str, dict[str, str]]
) -> tuple[str, float] | None:
    if not candidate_lookup:
        return None

    best_normalized = max(
        candidate_lookup,
        key=lambda candidate_name: similarity_ratio(party_name, candidate_name),
    )
    return best_normalized, similarity_ratio(party_name, best_normalized)


def print_preview(
    doc_id: str,
    submission_rows: list[dict[str, str]],
    resolved: ResolvedConstituency,
    candidate_rows: list[dict[str, str]],
    candidate_lookup: dict[str, dict[str, str]],
) -> None:
    print(f"Preview for {doc_id}")
    print(f"submission rows : {len(submission_rows)}")
    print(f"candidate rows  : {len(candidate_rows)}")
    print(f"province id     : {resolved.province_id}")
    print(f"province name   : {resolved.province_name}")
    print(f"province folder : {resolved.province_dir.name}")
    print(f"area id         : {resolved.area_id}")
    print(f"expected area   : {resolved.expected_area_name}")
    print(f"area folder     : {resolved.area_dir.name}")
    print(f"candidate csv   : {resolved.candidate_csv_path}")
    print()
    print("Rows")

    exact_matches = 0
    unresolved = 0

    for row in sorted(submission_rows, key=lambda item: int(item["row_num"])):
        party_name = row["party_name"].strip()
        matched_row = candidate_lookup.get(normalize_party_name(party_name))

        if matched_row is not None:
            exact_matches += 1
            print(
                f"[row {row['row_num']:>2}] "
                f"{party_name} -> {matched_row['party.name']} -> {matched_row['totalVotes']}"
            )
            continue

        unresolved += 1
        suggestion = best_party_suggestion(party_name, candidate_lookup)
        if suggestion is None:
            suggestion_text = "no suggestion available"
        else:
            suggestion_name, score = suggestion
            suggestion_text = f"closest='{suggestion_name}' score={score:.3f}"

        print(f"[row {row['row_num']:>2}] {party_name} -> UNRESOLVED ({suggestion_text})")

    print()
    print("Summary")
    print(f"exact matches   : {exact_matches}")
    print(f"unresolved rows : {unresolved}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        base_dir = Path(__file__).resolve().parent
        data_dir = base_dir / "data"
        submission_csv_path = data_dir / "submission_template.csv"
        areas_csv_path = data_dir / "area" / "areas.csv"
        all_constituency_dir = data_dir / "all_constituency"

        parse_constituency_doc_id(args.doc_id)
        submission_rows = load_submission_rows(submission_csv_path, args.doc_id)
        province_names, area_names = load_area_lookup(areas_csv_path)
        resolved = resolve_constituency(
            doc_id=args.doc_id,
            province_names=province_names,
            area_names=area_names,
            all_constituency_dir=all_constituency_dir,
        )
        candidate_rows = load_candidate_rows(resolved.candidate_csv_path)
        candidate_lookup = build_candidate_lookup(candidate_rows)
        print_preview(
            doc_id=args.doc_id,
            submission_rows=submission_rows,
            resolved=resolved,
            candidate_rows=candidate_rows,
            candidate_lookup=candidate_lookup,
        )
        return 0
    except PreviewError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
