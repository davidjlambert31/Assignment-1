"""Run the retail pipeline from the command line."""

import argparse
import csv
from pathlib import Path

from pipeline.reporter import RetailReport, format_report
from pipeline.validator import REQUIRED_FIELDS, validate_record


DEFAULT_CSV = Path(__file__).resolve().parent / "data" / "transactions.csv"


def load_transactions(csv_path):
    """Read and validate CSV rows; preserve explanations for rejected rows."""
    records = []
    rejected = []
    total_rows = 0

    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("CSV is empty or has no header row")

        headers = {name.strip().lower() for name in reader.fieldnames}
        missing_headers = [name for name in REQUIRED_FIELDS if name not in headers]
        if missing_headers:
            raise ValueError("CSV missing headers: " + ", ".join(missing_headers))

        for line_number, row in enumerate(reader, start=2):
            total_rows += 1
            record, reason = validate_record(row)
            if reason:
                rejected.append((line_number, reason))
            else:
                records.append(record)

    return records, rejected, total_rows


def main():
    """Parse the input path, run the pipeline, and print the final report."""
    parser = argparse.ArgumentParser(description="Analyze retail transactions")
    parser.add_argument(
        "csv_file",
        nargs="?",
        type=Path,
        default=DEFAULT_CSV,
        help="Path to a CSV file (defaults to data/transactions.csv)",
    )
    args = parser.parse_args()

    try:
        records, rejected, total_rows = load_transactions(args.csv_file)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(status=1, message=f"Unable to load transactions: {error}\n")

    report = RetailReport(records, rejected, total_rows)
    print(format_report(report))


if __name__ == "__main__":
    main()
