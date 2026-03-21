from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

from preview_constituency_votes import DOC_ID_PATTERN, PreviewError, normalize_party_name as base_normalize_party_name


THAI_DIGIT_TRANS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
NUMBER_RE = re.compile(r"([0-9๐-๙][0-9๐-๙,]*)")
PARTY_LIST_DOC_ID_RE = re.compile(r"^party_list_(\d+)_(\d+)$")
LEADING_ROW_NUMBER_RE = re.compile(r"^[0-9๐-๙]+\s*")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate submission_v2.csv from OCR cache by parsing constituency vote tables."
    )
    parser.add_argument(
        "--ocr-cache",
        default="ocr_cache.csv",
        help="Input OCR cache CSV path.",
    )
    parser.add_argument(
        "--input",
        default="data/submission_template.csv",
        help="Input submission template CSV path.",
    )
    parser.add_argument(
        "--output",
        default="data/submission_v2.csv",
        help="Output CSV path to write.",
    )
    return parser


def read_rows(path: Path) -> list[dict[str, str]]:
    csv.field_size_limit(sys.maxsize)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise PreviewError(f"Missing header row in {path}")
        return list(reader)


def write_submission_table(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "votes"])
        writer.writeheader()
        writer.writerows(rows)


def normalize_party_name(name: str) -> str:
    normalized = base_normalize_party_name(name)
    normalized = normalized.replace("\u200b", "").replace("\ufeff", "")
    normalized = LEADING_ROW_NUMBER_RE.sub("", normalized)
    normalized = re.sub(r"\s+", "", normalized)
    return normalized


def is_supported_doc_id(doc_id: str) -> bool:
    return DOC_ID_PATTERN.fullmatch(doc_id) is not None or PARTY_LIST_DOC_ID_RE.fullmatch(doc_id) is not None


def normalize_vote_token(value: str) -> str | None:
    match = NUMBER_RE.search(value)
    if match is None:
        return None
    digits = match.group(1).translate(THAI_DIGIT_TRANS).replace(",", "")
    return digits if digits.isdigit() else None


def is_summary_text(value: str) -> bool:
    compact = re.sub(r"\s+", "", value)
    return "รวมคะแนนทั้งสิ้น" in compact


def extract_vote_from_cells(
    cells: list[str], expected_parties: set[str]
) -> tuple[str, str] | None:
    normalized_cells = [normalize_party_name(cell) for cell in cells]
    party_index: int | None = None
    party_name: str | None = None

    for index, normalized_cell in enumerate(normalized_cells):
        if normalized_cell in expected_parties:
            party_index = index
            party_name = normalized_cell
            break

    if party_index is None or party_name is None:
        return None

    for cell in cells[party_index + 1 :]:
        vote_value = normalize_vote_token(cell)
        if vote_value is not None:
            return party_name, vote_value

    return None


def parse_delimited_table_votes(
    text: str, expected_parties: set[str]
) -> dict[str, str]:
    votes_by_party: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if "|" not in line:
            continue

        cells = [cell.strip() for cell in line.split("|")]
        cells = [cell for cell in cells if cell]
        if len(cells) < 2:
            continue
        if all(set(cell) <= {"-"} for cell in cells):
            continue
        if any("หมายเลข" in cell or "ได้คะแนน" in cell for cell in cells):
            continue
        if any(is_summary_text(cell) for cell in cells):
            continue

        extracted = extract_vote_from_cells(cells, expected_parties)
        if extracted is not None:
            party_name, vote_value = extracted
            votes_by_party[party_name] = vote_value

    return votes_by_party


def clean_plain_lines(text: str) -> list[str]:
    cleaned: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip().strip("`").strip()
        if not line:
            continue
        cleaned.append(line)
    return cleaned


def parse_plain_votes(text: str, expected_parties: set[str]) -> dict[str, str]:
    votes_by_party: dict[str, str] = {}
    lines = clean_plain_lines(text)

    for index, line in enumerate(lines):
        inline_match = extract_vote_from_cells([cell.strip() for cell in line.split("|")], expected_parties)
        if inline_match is not None:
            party_name, vote_value = inline_match
            votes_by_party[party_name] = vote_value
            continue

        party_name = normalize_party_name(line)
        if party_name not in expected_parties:
            continue
        if is_summary_text(line):
            continue

        for offset in range(1, 5):
            next_index = index + offset
            if next_index >= len(lines):
                break

            next_line = lines[next_index]
            if normalize_party_name(next_line) in expected_parties:
                break
            if is_summary_text(next_line):
                break

            vote_value = normalize_vote_token(next_line)
            if vote_value is not None:
                votes_by_party[party_name] = vote_value
                break

    return votes_by_party


def build_expected_parties(
    template_rows: list[dict[str, str]],
) -> dict[str, set[str]]:
    expected_by_doc_id: dict[str, set[str]] = defaultdict(set)
    for row in template_rows:
        doc_id = row["doc_id"]
        if not is_supported_doc_id(doc_id):
            continue
        expected_by_doc_id[doc_id].add(normalize_party_name(row["party_name"]))
    return expected_by_doc_id


def group_ocr_rows(ocr_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ocr_rows:
        doc_id = row["doc_id"]
        if is_supported_doc_id(doc_id):
            grouped[doc_id].append(row)
    return grouped


def parse_doc_votes(
    doc_rows: list[dict[str, str]], expected_parties: set[str]
) -> dict[str, str]:
    votes_by_party: dict[str, str] = {}

    for row in sorted(doc_rows, key=lambda item: int(item["page"])):
        text = row.get("ocr_text", "")
        for party_name, vote_value in parse_delimited_table_votes(
            text, expected_parties
        ).items():
            votes_by_party[party_name] = vote_value

        for party_name, vote_value in parse_plain_votes(text, expected_parties).items():
            votes_by_party[party_name] = vote_value

    return votes_by_party


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    ocr_cache_path = (base_dir / args.ocr_cache).resolve()
    input_path = (base_dir / args.input).resolve()
    output_path = (base_dir / args.output).resolve()

    try:
        template_rows = read_rows(input_path)
        ocr_rows = read_rows(ocr_cache_path)
        expected_by_doc_id = build_expected_parties(template_rows)
        ocr_rows_by_doc_id = group_ocr_rows(ocr_rows)

        parsed_votes_by_doc_id: dict[str, dict[str, str]] = {}
        docs_with_votes = 0
        for doc_id, expected_parties in expected_by_doc_id.items():
            parsed_votes = parse_doc_votes(
                ocr_rows_by_doc_id.get(doc_id, []),
                expected_parties=expected_parties,
            )
            if parsed_votes:
                docs_with_votes += 1
            parsed_votes_by_doc_id[doc_id] = parsed_votes

        matched_rows = 0
        zero_rows = 0
        output_rows: list[dict[str, str]] = []
        for row in template_rows:
            doc_id = row["doc_id"]
            votes = "0"
            if is_supported_doc_id(doc_id):
                party_name = normalize_party_name(row["party_name"])
                matched_vote = parsed_votes_by_doc_id.get(doc_id, {}).get(party_name)
                if matched_vote is not None:
                    votes = matched_vote

            if votes == "0":
                zero_rows += 1
            else:
                matched_rows += 1

            output_rows.append({"id": row["id"], "votes": votes})

        write_submission_table(output_path, output_rows)

        print(f"wrote          : {output_path}")
        print(f"template rows  : {len(template_rows)}")
        print(f"ocr rows       : {len(ocr_rows)}")
        print(f"supported docs : {len(expected_by_doc_id)}")
        print(f"docs with votes: {docs_with_votes}")
        print(f"matched rows   : {matched_rows}")
        print(f"zero rows      : {zero_rows}")
        return 0
    except PreviewError as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
