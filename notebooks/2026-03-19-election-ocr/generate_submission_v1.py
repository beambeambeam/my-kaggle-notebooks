from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from preview_constituency_votes import (
    DOC_ID_PATTERN,
    PreviewError,
    best_party_suggestion,
    build_candidate_lookup,
    load_area_lookup,
    load_candidate_rows,
    normalize_party_name,
    resolve_constituency,
)


@dataclass(frozen=True)
class UnresolvedMatch:
    doc_id: str
    row_num: str
    party_name: str
    suggestion_name: str | None
    suggestion_score: float | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate submission_v1.csv from constituency candidate CSV files."
    )
    parser.add_argument(
        "--input",
        default="data/submission_template.csv",
        help="Input submission template CSV path.",
    )
    parser.add_argument(
        "--output",
        default="data/submission_v1.csv",
        help="Output CSV path to write.",
    )
    parser.add_argument(
        "--unresolved-limit",
        type=int,
        default=20,
        help="How many unresolved rows to print in the summary.",
    )
    return parser


def load_submission_table(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise PreviewError(f"Missing header row in {path}")
        return list(reader)


def group_constituency_rows(
    rows: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        doc_id = row["doc_id"]
        if DOC_ID_PATTERN.fullmatch(doc_id):
            grouped[doc_id].append(row)
    return grouped


def write_submission_table(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "votes"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    input_path = (base_dir / args.input).resolve()
    output_path = (base_dir / args.output).resolve()
    data_dir = base_dir / "data"

    try:
        rows = load_submission_table(input_path)
        province_names, area_names = load_area_lookup(data_dir / "area" / "areas.csv")
        all_constituency_dir = data_dir / "all_constituency"
        constituency_rows = group_constituency_rows(rows)

        lookup_by_doc_id: dict[str, dict[str, dict[str, str]]] = {}
        unresolved: list[UnresolvedMatch] = []

        for doc_id in sorted(constituency_rows):
            resolved = resolve_constituency(
                doc_id=doc_id,
                province_names=province_names,
                area_names=area_names,
                all_constituency_dir=all_constituency_dir,
            )
            candidate_rows = load_candidate_rows(resolved.candidate_csv_path)
            lookup_by_doc_id[doc_id] = build_candidate_lookup(candidate_rows)

        exact_match_count = 0
        constituency_row_count = 0
        untouched_non_constituency = 0

        output_rows: list[dict[str, str]] = []
        for row in rows:
            output_row = {"id": row["id"], "votes": row["votes"]}
            doc_id = row["doc_id"]

            if not DOC_ID_PATTERN.fullmatch(doc_id):
                untouched_non_constituency += 1
                output_rows.append(output_row)
                continue

            constituency_row_count += 1
            party_name = row["party_name"].strip()
            matched = lookup_by_doc_id[doc_id].get(normalize_party_name(party_name))

            if matched is not None:
                output_row["votes"] = matched["totalVotes"]
                exact_match_count += 1
            else:
                suggestion = best_party_suggestion(party_name, lookup_by_doc_id[doc_id])
                unresolved.append(
                    UnresolvedMatch(
                        doc_id=doc_id,
                        row_num=row["row_num"],
                        party_name=party_name,
                        suggestion_name=None if suggestion is None else suggestion[0],
                        suggestion_score=None if suggestion is None else suggestion[1],
                    )
                )

            output_rows.append(output_row)

        write_submission_table(output_path, output_rows)

        print(f"wrote           : {output_path}")
        print(f"input rows      : {len(rows)}")
        print(f"constituency docs: {len(constituency_rows)}")
        print(f"constituency rows: {constituency_row_count}")
        print(f"exact matches   : {exact_match_count}")
        print(f"unresolved rows : {len(unresolved)}")
        print(f"untouched rows  : {untouched_non_constituency}")

        if unresolved:
            print()
            print("Unresolved sample")
            for item in unresolved[: max(args.unresolved_limit, 0)]:
                if item.suggestion_name is None or item.suggestion_score is None:
                    suggestion_text = "no suggestion"
                else:
                    suggestion_text = (
                        f"closest='{item.suggestion_name}' score={item.suggestion_score:.3f}"
                    )
                print(
                    f"{item.doc_id} row {item.row_num}: "
                    f"{item.party_name} -> UNRESOLVED ({suggestion_text})"
                )

        return 0
    except PreviewError as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
