import csv
import os
from config import CSV_PATH, CSV_FIELDS, log

def init_csv() -> int:
    """
    Open (or create) the CSV file and write the header if the file is new.
    Returns the current last row index (0 = header only, N = N data rows).
    """
    if os.path.exists(CSV_PATH):
        # File already exists (e.g. resuming) – count existing data rows
        with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            # count existing data rows (subtract header)
            # using list() to consume generator for easier count if needed, but sum(1) is memory efficient
            try:
                row_count = sum(1 for _ in reader) - 1
            except StopIteration:
                row_count = -1
        log.info(f"CSV already exists with {row_count} data rows: {CSV_PATH}")
        return max(row_count, 0)
    else:
        # Create the file and write the header
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
        log.info(f"Created new CSV: {CSV_PATH}")
        return 0

def append_to_csv(rows: list[dict]) -> int:
    """
    Append rows to the CSV file.
    Returns the number of rows written.
    """
    if not rows:
        return 0
    with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writerows(rows)
    return len(rows)