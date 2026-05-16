#!/usr/bin/env python3
"""Genera payload per output CSV -> Google Sheet via google-personal MCP.

NB: questo script NON chiama Google API direttamente. Genera il payload (CSV rows + metadata)
che il subagent passera al MCP google-personal per create/append.

Usage:
  python scripts/csv_to_sheet.py --input-csv leads.csv --create-with-name "Lead Finder Pro Run 2026-04-30"
  python scripts/csv_to_sheet.py --input-csv leads.csv --sheet-id ABC123 --tab-name "leads_2026_04_30"

Author: Filippo Greco / lead-finder-pro 2026
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)


def csv_to_rows(csv_path: Path) -> list[list[str]]:
    """Read CSV and return list of rows (first row = header)."""
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate google-personal MCP payload from CSV"
    )
    parser.add_argument("--input-csv", required=True, help="Path to input CSV")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--create-with-name", help="Create new spreadsheet with this title"
    )
    target.add_argument("--sheet-id", help="Existing spreadsheet ID to append to")
    parser.add_argument(
        "--tab-name",
        default=None,
        help="Tab name (default: leads_<timestamp>)",
    )
    args = parser.parse_args()

    csv_path = Path(args.input_csv).expanduser()
    if not csv_path.exists():
        print(
            json.dumps({"error": f"Input CSV not found: {csv_path}"}), file=sys.stderr
        )
        return 1

    rows = csv_to_rows(csv_path)
    if len(rows) < 2:
        print(
            json.dumps({"error": "CSV has no data rows (only header or empty)"}),
            file=sys.stderr,
        )
        return 1

    tab_name = args.tab_name or f"leads_{datetime.now().strftime('%Y%m%d_%H%M')}"

    if args.create_with_name:
        action = "create"
        payload = {
            "action": action,
            "title": args.create_with_name,
            "tab": tab_name,
            "rows_to_write": len(rows),
            "header_row": rows[0],
            "csv_data": rows,
            "_mcp_call": {
                "tool": "mcp__google-personal__create_spreadsheet",
                "args": {"title": args.create_with_name},
                "next_step": "After spreadsheet created, call modify_sheet_values with returned spreadsheetId.",
            },
        }
    else:
        action = "append"
        payload = {
            "action": action,
            "sheet_id": args.sheet_id,
            "tab": tab_name,
            "rows_to_write": len(rows),
            "header_row": rows[0],
            "csv_data": rows,
            "_mcp_call": {
                "tool": "mcp__google-personal__modify_sheet_values",
                "args": {
                    "spreadsheet_id": args.sheet_id,
                    "range": f"{tab_name}!A1",
                    "values": rows,
                },
            },
        }

    log.info(f"Action: {action} | Tab: {tab_name} | Rows: {len(rows)}")
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
