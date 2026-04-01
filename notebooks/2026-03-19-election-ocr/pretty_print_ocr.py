import argparse
import csv
from pathlib import Path


DEFAULT_CSV_PATH = Path(__file__).with_name("ocr_documents.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pretty-print one OCR document from ocr_documents.csv."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help=f"Path to the OCR CSV file. Default: {DEFAULT_CSV_PATH}",
    )
    parser.add_argument(
        "--id",
        dest="doc_id",
        help="Document id to print, for example constituency_10_1.",
    )
    parser.add_argument(
        "--row",
        type=int,
        default=1,
        help="1-based data row number to print when --id is not provided. Default: 1.",
    )
    return parser


def read_rows(csv_path: Path) -> list[dict[str, str]]:
    csv.field_size_limit(10**9)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def pick_row(rows: list[dict[str, str]], doc_id: str | None, row_number: int) -> dict[str, str]:
    if doc_id:
        for row in rows:
            if row.get("id") == doc_id:
                return row
        raise SystemExit(f"Document id not found: {doc_id}")

    if row_number < 1 or row_number > len(rows):
        raise SystemExit(f"Row must be between 1 and {len(rows)}. Received: {row_number}")

    return rows[row_number - 1]


def format_document(row: dict[str, str], row_number: int | None = None) -> str:
    title = row.get("id", "<missing id>")
    parts = ["=" * 80, f"Document: {title}"]
    if row_number is not None:
        parts.append(f"Row: {row_number}")
    parts.extend(["=" * 80, "", row.get("text", "").strip(), ""])
    return "\n".join(parts)


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.csv)
    row = pick_row(rows, args.doc_id, args.row)
    row_number = None if args.doc_id else args.row
    print(format_document(row, row_number=row_number))


if __name__ == "__main__":
    main()
