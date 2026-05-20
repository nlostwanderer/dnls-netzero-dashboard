#!/usr/bin/env python3
"""
Constraint costs splicer.

Takes records.json (all FYs, produced by the scraper), slices to the latest
complete UK financial year, sums Thermal constraints cost, and writes
headline.json with the figure, caveats, and card metadata.

Decisions baked in (see methodology-changelog.md):
  - Headline FY = latest complete FY (end-date before today). v0.2 M-5.
  - Headline figure = sum of Thermal constraints cost only. v0.2 M-2.
  - No traffic light. Constraint costs is a context card. v0.2 M-1.
  - Missing-day caveat surfaced if row count != expected. v0.4 M-10.
  - Delta logged to stdout if headline figure changes between runs. ADR-002.

Usage:
    python3 splicer.py
    python3 splicer.py --records-path /path/to/records.json
    python3 splicer.py --records-path /path/to/records.json --output-path /path/to/headline.json
"""

from __future__ import annotations

import argparse
import calendar
import json
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

DEFAULT_RECORDS_PATH = Path("data/processed/constraint-costs/records.json")
DEFAULT_OUTPUT_PATH = Path("site/data/constraint-costs/headline.json")

THERMAL_COL = "Thermal constraints cost"
NESO_SOURCE_URL = (
    "https://www.neso.energy/data-portal/constraint-breakdown-costs-and-volume"
)

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def bail(msg: str) -> None:
    """Print a human error and exit non-zero. No tracebacks for known failure modes."""
    print(f"\n  {msg}\n", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_records(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        bail(
            "Oh deary me, I couldn't find any data — is it missing, is it empty?\n"
            "  I don't know, you better have a look.\n"
            f"  (looked here: {path})"
        )
    with path.open() as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# FY helpers
# ---------------------------------------------------------------------------

def fy_end_date(fy_label: str) -> date:
    """'2025-2026' -> date(2026, 3, 31)"""
    parts = fy_label.split("-")
    if len(parts) != 2:
        bail(f"Unexpected FY label format: {fy_label!r}")
    end_year = int(parts[1])
    return date(end_year, 3, 31)


def expected_row_count(fy_label: str) -> int:
    """365 or 366 depending on whether February falls in a leap year.
    For April-March FYs, February is always in the end calendar year."""
    end_year = int(fy_label.split("-")[1])
    return 366 if calendar.isleap(end_year) else 365


def is_complete(fy_label: str, today: date) -> bool:
    return fy_end_date(fy_label) < today


# ---------------------------------------------------------------------------
# Casting
# ---------------------------------------------------------------------------

def cast_thermal(value, row_index: int) -> float:
    """2025-26 returns strings; other FYs return JSON numbers. Handle both.
    Hard-fails on anything that won't parse — don't silently drop bad data."""
    if value is None:
        bail(
            f"Null value in '{THERMAL_COL}' at row {row_index}. "
            "This shouldn't happen — check the scraper output."
        )
    try:
        return float(value)
    except (ValueError, TypeError):
        bail(
            f"Could not cast '{THERMAL_COL}' value {value!r} (type: {type(value).__name__}) "
            f"to float at row {row_index}. Schema may have changed."
        )


# ---------------------------------------------------------------------------
# FY totals (sparkline data)
# ---------------------------------------------------------------------------

def build_fy_totals(records: list[dict], complete_fys: list[str]) -> list[dict]:
    """Sum thermal cost per complete FY, in chronological order.

    Returns a list of dicts: [{"fy": "2017-2018", "total": 412000000.0, "row_count": 365}, ...]

    List preserves order (chronological) so the sparkline can iterate without sorting.
    Only complete FYs are included — in-progress FY is excluded.
    Same cast logic as the headline sum: handles string and numeric values.
    """
    # Group records by FY label first (one pass)
    by_fy: dict[str, list[dict]] = {fy: [] for fy in complete_fys}
    for r in records:
        label = r.get("_fy_label")
        if label in by_fy:
            by_fy[label].append(r)

    totals = []
    for fy in complete_fys:  # already sorted chronologically
        fy_records = by_fy[fy]
        row_total = 0.0
        for i, r in enumerate(fy_records):
            row_total += cast_thermal(r.get(THERMAL_COL), i)
        totals.append({
            "fy": fy,
            "total": row_total,
            "row_count": len(fy_records),
        })
        print(f"[splicer] fy_totals: {fy}  £{row_total:,.0f}  ({len(fy_records)} rows)")

    return totals


# ---------------------------------------------------------------------------
# Delta logging
# ---------------------------------------------------------------------------

def log_delta(output_path: Path, new_total: float, headline_fy: str) -> None:
    """If a previous headline.json exists for the same FY, log any change in the figure."""
    if not output_path.exists():
        return
    try:
        with output_path.open() as f:
            prev = json.load(f)
    except (json.JSONDecodeError, OSError):
        print("[splicer] WARNING: could not read previous headline.json for delta check — skipping.")
        return

    if prev.get("fy_label") != headline_fy:
        print(f"[splicer] previous headline.json was for FY {prev.get('fy_label')!r}, "
              f"now producing FY {headline_fy!r} — no delta logged (FY rollover).")
        return

    prev_total = prev.get("thermal_cost_gbp")
    if prev_total is None:
        return

    delta = new_total - prev_total
    if delta == 0:
        print("[splicer] headline figure unchanged from previous run — no delta.")
    else:
        pct = (delta / prev_total) * 100 if prev_total else float("inf")
        direction = "UP" if delta > 0 else "DOWN"
        print(
            f"[splicer] DELTA: headline figure changed {direction} by "
            f"£{abs(delta):,.0f} ({pct:+.2f}%) since last run. "
            f"Previous: £{prev_total:,.0f} — New: £{new_total:,.0f}. "
            f"NESO revised historical data for FY {headline_fy}."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Constraint costs splicer.")
    parser.add_argument(
        "--records-path",
        type=Path,
        default=DEFAULT_RECORDS_PATH,
        help="Path to records.json (default: relative to repo root)",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to write headline.json (default: relative to repo root)",
    )
    args = parser.parse_args()

    today = date.today()
    print(f"[splicer] running on {today.isoformat()}")
    print(f"[splicer] records: {args.records_path.resolve()}")
    print(f"[splicer] output:  {args.output_path.resolve()}")

    # --- Load ---
    records = load_records(args.records_path)
    print(f"[splicer] loaded {len(records)} records")

    # --- Identify FYs ---
    fy_counts: dict[str, int] = {}
    for r in records:
        label = r.get("_fy_label", "UNKNOWN")
        fy_counts[label] = fy_counts.get(label, 0) + 1

    complete_fys = sorted(
        label for label in fy_counts if is_complete(label, today)
    )
    if not complete_fys:
        bail(
            "Oh deary me, I couldn't find any complete financial years in the data.\n"
            "  Is the scraper fresh off the boat? Has it even run yet? Have a look."
        )

    headline_fy = complete_fys[-1]
    print(f"[splicer] headline FY: {headline_fy} "
          f"(latest complete of {len(complete_fys)} complete FYs)")

    # --- Slice ---
    fy_records = [r for r in records if r.get("_fy_label") == headline_fy]
    actual_rows = len(fy_records)
    expected_rows = expected_row_count(headline_fy)
    print(f"[splicer] rows in FY: {actual_rows} (expected {expected_rows})")

    caveats = []
    if actual_rows != expected_rows:
        caveat = (
            f"Source returned {actual_rows} rows for FY {headline_fy}, "
            f"not the expected {expected_rows}. "
            f"One or more days may be missing from the NESO dataset (see neso-feedback F-3). "
            f"The headline figure is a sum of {actual_rows} days only."
        )
        caveats.append(caveat)
        print(f"[splicer] ⚠ {caveat}")

    # --- Sum ---
    total = 0.0
    for i, r in enumerate(fy_records):
        total += cast_thermal(r.get(THERMAL_COL), i)

    print(f"[splicer] headline figure: £{total:,.0f}")

    # --- Date range ---
    dates = sorted(r.get("Date", "") for r in fy_records if r.get("Date"))
    if not dates:
        bail("No Date values found in headline FY records. Something is very wrong.")

    data_through = dates[-1]
    first_date = dates[0]
    print(f"[splicer] date range: {first_date} → {data_through}")

    # --- FY totals for sparkline ---
    print(f"[splicer] building fy_totals for {len(complete_fys)} complete FYs...")
    fy_totals = build_fy_totals(records, complete_fys)

    # --- Delta check against previous run ---
    log_delta(args.output_path, total, headline_fy)

    # --- Build output ---
    output = {
        "fy_label": headline_fy,
        "thermal_cost_gbp": total,
        "thermal_cost_gbp_formatted": f"£{total / 1_000_000_000:.2f}bn",
        "row_count": actual_rows,
        "expected_row_count": expected_rows,
        "first_date": first_date,
        "data_through": data_through,
        "generated_on": today.isoformat(),
        "source_url": NESO_SOURCE_URL,
        "source_column": THERMAL_COL,
        "scoring": None,
        "card_type": "context",
        "caveats": caveats,
        "fy_totals": fy_totals,
        "methodology_ref": "methodology-changelog.md v0.2 M-1, M-2, M-5; v0.4 M-10",
    }

    # --- Write ---
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_path.open("w") as f:
        json.dump(output, f, indent=2)

    print(f"[splicer] wrote {args.output_path.resolve()}")
    print("[splicer] done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
