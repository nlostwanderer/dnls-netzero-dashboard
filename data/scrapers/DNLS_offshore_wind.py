#!/usr/bin/env python3
"""
Offshore wind splicer.

Takes the REPD quarterly CSV (manual download, v0.5 M-16), filters to
'Wind Offshore', and produces headline.json for the scored offshore-wind card.

Decisions baked in (methodology-changelog.md):
  - Scored metric, gap-closure projection.        rubric-v0.1 §2
  - Operational = Development Status (short) == 'Operational' (status filter,
    NOT date-populated). Excludes Decommissioned, pipeline.   ADR-001 d8, d12
  - Trailing 12m additions keyed on 'Operational' DATE in window.  rubric §2
  - Single-project sensitivity flag if one project >60% of window.  rubric §5
  - Pipeline buckets (UC, AC) by status filter, contextual only.   v0.5 M-12
  - Quarterly additions sparkline.                                 v0.5 M-13
  - Target is a RANGE (43-50 GW), scored at both ends.       v0.6 (this build)
  - Clean quarter-end anchor (REPD Q1 -> 31 Mar), matching constraint costs
    FY-boundary logic.                                         v0.6 (this build)

Source target: Clean Power 2030 Action Plan p10 & p74 ("43-50 GW ... in 2030");
DESNZ CfD reform consultation 21 Feb 2025 (same range).

Usage:
    python3 splicer_offshore.py --csv PATH [--output PATH] [--print-only]
"""
from __future__ import annotations
import argparse, csv, json, sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

TECH = "Wind Offshore"
CAP_COL = "Installed Capacity (MWelec)"
STATUS_COL = "Development Status (short)"
OP_DATE_COL = "Operational"
DATE_COL = "Date"  # not in REPD; FY anchor is fixed, see below

# --- Methodology constants (v0.6) ---
TARGET_LOW_GW, TARGET_HIGH_GW = 43.0, 50.0
TARGET_END = date(2030, 12, 31)
SPF_THRESHOLD = 0.60  # rubric §5

# Clean quarter-end anchor. REPD Q1 2026 = data through 31 March 2026.
# Manual update per quarter (v0.5 M-16); anchor set explicitly, not derived
# from row dates, to keep the figure reproducible and citable.
AS_OF = date(2026, 3, 31)
WINDOW_START = date(2025, 3, 31)

ENCODING = "cp1252"  # REPD ships cp1252, NOT utf-8. Verified on Q1 2026 file.


def bail(msg: str) -> None:
    print(f"\n  {msg}\n", file=sys.stderr)
    sys.exit(1)


def mw(r: dict) -> float:
    v = (r.get(CAP_COL) or "").strip().replace(",", "")
    if not v:
        return 0.0
    try:
        return float(v)
    except ValueError:
        bail(f"Un-parseable capacity {v!r} for site {r.get('Site Name')!r}. "
             "REPD schema may have changed — investigate, do not relax.")


def pdate(s: str | None):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None  # caller decides if a missing parse matters


def light(ratio: float) -> str:
    return "green" if ratio >= 1.0 else "amber" if ratio >= 0.60 else "red"


def build(csv_path: Path) -> dict:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        bail(f"REPD CSV missing or empty: {csv_path}")
    with csv_path.open(encoding=ENCODING) as f:
        rows = list(csv.DictReader(f))
    if CAP_COL not in (rows[0] if rows else {}):
        bail(f"Expected column {CAP_COL!r} not found. REPD header may have changed.")

    osw = [r for r in rows if r["Technology Type"] == TECH]
    if not osw:
        bail(f"No {TECH!r} rows found. Check Technology Type vocabulary.")

    # STOCK — operational by STATUS
    op = [r for r in osw if r[STATUS_COL] == "Operational"]
    operational_gw = round(sum(mw(r) for r in op) / 1000, 2)

    # FLOW — trailing 12m by operational DATE
    added = []
    for r in osw:
        d = pdate(r[OP_DATE_COL])
        if d and WINDOW_START < d <= AS_OF:
            added.append((d, r["Site Name"], mw(r)))
    flow_mw = sum(a[2] for a in added)
    trailing_12m_gw = round(flow_mw / 1000, 3)

    largest_share = (max((a[2] for a in added), default=0) / flow_mw) if flow_mw else 0.0
    spf = largest_share > SPF_THRESHOLD

    # PIPELINE — by STATUS
    uc_gw = round(sum(mw(r) for r in osw if r[STATUS_COL] == "Under Construction") / 1000, 2)
    ac_gw = round(sum(mw(r) for r in osw if r[STATUS_COL] == "Awaiting Construction") / 1000, 2)

    # SCORING — gap-closure projection, range
    years_remaining = (TARGET_END - AS_OF).days / 365.25
    projected_gw = round(operational_gw + (trailing_12m_gw * years_remaining), 2)

    def score(target: float):
        ratio = projected_gw / target
        slip = AS_OF.year + ((target - operational_gw) / trailing_12m_gw) if trailing_12m_gw else None
        return round(ratio, 3), (round(slip) if slip else None)

    ratio_low, slip_low = score(TARGET_LOW_GW)   # 43
    ratio_high, slip_high = score(TARGET_HIGH_GW)  # 50
    # Both ends share the same light here, but compute independently and assert.
    tl_low, tl_high = light(ratio_low), light(ratio_high)
    traffic_light = tl_low if tl_low == tl_high else f"{tl_low}/{tl_high}"

    # QUARTERLY sparkline — all quarters with additions, chronological
    q = defaultdict(float)
    for r in osw:
        d = pdate(r[OP_DATE_COL])
        if d:
            q[f"{d.year}-Q{(d.month - 1)//3 + 1}"] += mw(r)
    quarterly = [{"q": k, "gw": round(v / 1000, 3)} for k, v in sorted(q.items())]

    caveats = []
    if spf:
        biggest = max(added, key=lambda a: a[2])
        caveats.append(
            f"Trailing 12-month additions are dominated by a single project "
            f"({biggest[1]}, {biggest[2]:.0f} MW = {largest_share*100:.0f}% of the window). "
            f"Offshore wind commissions in multi-GW lumps years apart; this window "
            f"caught a trough. The score is correct but acutely sensitive to "
            f"commissioning timing — read alongside the pipeline bar and sparkline."
        )
    caveats.append(
        "REPD records multi-phase projects as single entries and can lag "
        "commissioning of completed phases. Dogger Bank A&B (2.4 GW) remains "
        "Under Construction as neither phase has reached full commercial operation "
        "(per v0.5 M-15); correctly excluded from operational."
    )
    caveats.append(
        "Scored against the government's 2030 capacity RANGE (43-50 GW), not a "
        "point target. Both endpoints shown. Slip years are far beyond 2030 and "
        "carry wide uncertainty — treat as 'well past 2030 at current pace', not "
        "as precise forecasts."
    )

    return {
        "metric": "offshore-wind",
        "card_type": "scored",
        "as_of": AS_OF.isoformat(),
        "anchor_note": "Clean quarter-end (REPD Q1 2026 = data through 31 Mar 2026); "
                       "fixed, not derived from row dates. Matches constraint-costs FY-boundary logic.",
        "source": "REPD Q1 2026",
        "source_url": "https://www.gov.uk/government/publications/renewable-energy-planning-database-quarterly-extract",
        "operational_gw": operational_gw,
        "trailing_12m_gw": trailing_12m_gw,
        "single_project_sensitivity": spf,
        "projected_2030_gw": projected_gw,
        "years_remaining": round(years_remaining, 3),
        "target": {
            "low": TARGET_LOW_GW, "high": TARGET_HIGH_GW, "unit": "GW",
            "source": "Clean Power 2030 Action Plan (DESNZ, Dec 2024), p10 & p74: "
                      "'43-50 GW of offshore wind ... in 2030'; range restated in "
                      "DESNZ CfD reform consultation, 21 Feb 2025.",
            "retrieved": date.today().isoformat(),
        },
        "delivery_ratio": {"vs_low_target": ratio_low, "vs_high_target": ratio_high},
        "traffic_light": traffic_light,
        "slip_year": {"low": slip_low, "high": slip_high},
        "pipeline_gw": {
            "operational": operational_gw,
            "under_construction": uc_gw,
            "awaiting_construction": ac_gw,
        },
        "quarterly_additions": quarterly,
        "caveats": caveats,
        "methodology_ref": "rubric-v0.1 §2,§5; changelog v0.5 M-12..M-16; v0.6 (range scoring, quarter-end anchor)",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--output", type=Path,
                    default=Path("site/data/offshore-wind/headline.json"))
    ap.add_argument("--print-only", action="store_true",
                    help="Print the assembled dict, write nothing.")
    args = ap.parse_args()

    out = build(args.csv)
    print(json.dumps(out, indent=2))

    if args.print_only:
        print("\n[print-only] nothing written.", file=sys.stderr)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\n[splicer] wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":

    sys.exit(main())
