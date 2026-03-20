import argparse
import csv
import re
from pathlib import Path


DEFAULT_INPUT_CSV = Path(__file__).with_name("ocr_documents.csv")
DEFAULT_OUTPUT_CSV = Path(__file__).with_name("ocr_table.csv")

SECTION_RE = re.compile(
    r"---\n(?P<meta>.*?)\n---\n(?P<body>.*?)(?=(?:\n---\n)|\Z)",
    re.DOTALL,
)
TABLE_RE = re.compile(r"<table>.*?</table>", re.DOTALL)
TR_RE = re.compile(r"<tr>.*?</tr>", re.DOTALL)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract HTML table sections from OCR documents into ocr_table.csv."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_CSV,
        help=f"Input OCR CSV path. Default: {DEFAULT_INPUT_CSV}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_CSV,
        help=f"Output CSV path. Default: {DEFAULT_OUTPUT_CSV}",
    )
    return parser


def read_rows(csv_path: Path) -> list[dict[str, str]]:
    csv.field_size_limit(10**9)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def extract_table_rows(rows: list[dict[str, str]]) -> list[dict[str, str | int]]:
    extracted: list[dict[str, str | int]] = []

    for row in rows:
        doc_id = row.get("id", "")
        text = row.get("text", "")
        section_index = 0

        for match in SECTION_RE.finditer(text):
            meta = match.group("meta")
            body = match.group("body").strip()
            if "is_table: True" not in meta:
                continue

            tables = TABLE_RE.findall(body)
            if not tables:
                continue

            section_index += 1

            for table_index, table_html in enumerate(tables, start=1):
                tr_matches = TR_RE.findall(table_html)
                extracted.append(
                    {
                        "id": doc_id,
                        "section_index": section_index,
                        "table_index": table_index,
                        "tr_count": len(tr_matches),
                        "table_html": table_html.strip(),
                    }
                )

    return extracted


def write_rows(csv_path: Path, rows: list[dict[str, str | int]]) -> None:
    fieldnames = ["id", "section_index", "table_index", "tr_count", "table_html"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.input)
    extracted = extract_table_rows(rows)
    write_rows(args.output, extracted)
    print(f"Wrote {len(extracted)} table rows to {args.output}")


if __name__ == "__main__":
    main()
