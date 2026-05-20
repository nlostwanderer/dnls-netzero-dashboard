#!/usr/bin/env python3
"""
Constraint costs splicer — print-first diagnostic pass.

Loads records.json, identifies all FYs present, picks the latest complete one
(FY end-date before today), prints what it found and what the headline figure
would be. Writes nothing. Make sure this looks right before the full splicer runs.

Usage:
    python3 splicer_diag.py
    python3 splicer_diag.py --records-path /path/to/records.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULT_RECORDS_PATH = Path("data/processed/constraint-costs/records.json")
THERMAL_COL = "Thermal constraints cost"


def load_records(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        print(
            "\n  Oh deary me, I couldn't find any data — is it missing, is it empty?\n"
            "  I don't know, you better have a look.\n"
            f"  (looked here: {path})\n"
        )
        sys.exit(1)
    with path.open() as f:
        return json.load(f)


def fy_end_date(fy_label: str) -> date:
    """'2025-2026' -> date(2026, 3, 31)"""
    end_year = int(fy_label.split("-")[1])
    return date(end_year, 3, 31)


def is_complete(fy_label: str, today: date) -> bool:
    return fy_end_date(fy_label) < today


def cast_thermal(value) -> float:
    """2025-26 resource returns strings; other FYs return JSON numbers. Handle both."""
    if value is None:
        raise ValueError("null thermal cost value")
    return float(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--records-path",
        type=Path,
        default=DEFAULT_RECORDS_PATH,
        help="Path to records.json (default: relative to repo root)",
    )
    args = parser.parse_args()

    today = date.today()
    print(f"\n[diag] running on {today.isoformat()}")
    print(f"[diag] records path: {args.records_path.resolve()}")

    records = load_records(args.records_path)
    print(f"[diag] loaded {len(records)} records")

    # --- What FYs are present? ---
    fy_counts: dict[str, int] = {}
    for r in records:
        label = r.get("_fy_label", "UNKNOWN")
        fy_counts[label] = fy_counts.get(label, 0) + 1

    print(f"\n[diag] FYs present in records.json ({len(fy_counts)} total):")
    for label in sorted(fy_counts):
        end = fy_end_date(label)
        complete = is_complete(label, today)
        status = "COMPLETE" if complete else "IN PROGRESS"
        expected = 366 if end.year % 4 == 0 else 365
        actual = fy_counts[label]
        row_note = f"{actual} rows" + (f" ⚠ expected {expected}" if actual != expected else "")
        print(f"  {label}  ends {end}  [{status}]  {row_note}")

    # --- Pick headline FY ---
    complete_fys = sorted(
        [label for label in fy_counts if is_complete(label, today)]
    )
    if not complete_fys:
        print("\n[diag] ERROR: no complete FYs found. Cannot produce a headline figure.")
        sys.exit(1)

    headline_fy = complete_fys[-1]  # latest complete
    print(f"\n[diag] headline FY selected: {headline_fy}")

    # --- Slice to headline FY ---
    fy_records = [r for r in records if r.get("_fy_label") == headline_fy]
    print(f"[diag] records in headline FY: {len(fy_records)}")

    # --- Check for nulls in thermal column ---
    nulls = [i for i, r in enumerate(fy_records) if r.get(THERMAL_COL) is None]
    if nulls:
        print(f"[diag] WARNING: {len(nulls)} null values in '{THERMAL_COL}' — rows {nulls[:5]}{'...' if len(nulls) > 5 else ''}")

    # --- Spot-check value type (the string/float quirk from handover) ---
    sample = fy_records[0].get(THERMAL_COL) if fy_records else None
    print(f"[diag] sample '{THERMAL_COL}' value: {sample!r}  (type: {type(sample).__name__})")

    # --- Compute headline figure ---
    try:
        values = [cast_thermal(r.get(THERMAL_COL)) for r in fy_records if r.get(THERMAL_COL) is not None]
        total = sum(values)
    except (ValueError, TypeError) as e:
        print(f"[diag] ERROR: failed to cast thermal cost values: {e}")
        sys.exit(1)

    print(f"\n[diag] headline figure (sum of '{THERMAL_COL}', FY {headline_fy}):")
    print(f"  £{total:,.0f}")
    print(f"  ({len(values)} of {len(fy_records)} rows included, {len(fy_records) - len(values)} nulls excluded)")

    # --- Date range in this FY ---
    dates = sorted(r.get("Date", "") for r in fy_records if r.get("Date"))
    if dates:
        print(f"\n[diag] date range in headline FY:")
        print(f"  first: {dates[0]}")
        print(f"  last:  {dates[-1]}")
        print(f"  data-through date (for card stamp): {dates[-1]}")

    # --- Flag if row count is unexpected ---
    end = fy_end_date(headline_fy)
    expected_rows = 366 if end.year % 4 == 0 else 365
    if len(fy_records) != expected_rows:
        print(f"\n[diag] ⚠ CAVEAT: expected {expected_rows} rows for FY {headline_fy}, got {len(fy_records)}.")
        print(f"  Headline figure is a sum of {len(fy_records)} days, not {expected_rows}.")
        print(f"  This matches neso-feedback F-3. Will be flagged on the card.")

    print("\n[diag] done — nothing written. Check the above looks right before running the full splicer.\n")


if __name__ == "__main__":
    main()
