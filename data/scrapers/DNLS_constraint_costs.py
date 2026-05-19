#!/usr/bin/env python3
"""
NESO Constraint Costs — production scraper.

Implements ADR-002 decisions 3, 4, 5, 6, 7:
  - CKAN-first source registry (decision 4): hits package_show, walks resources.
  - last_modified state tracking (decision 3): re-fetches only resources whose
    timestamp has advanced since the previous run. State file is the source
    of truth for "what we have."
  - All eight measurement columns stored (decisions 5, 6): we keep volumes and
    zero-valued cost columns even though only thermal cost is currently published.
  - Schema validation on every fetch (decision 7): hard fail on drift, preserve
    cached data, exit non-zero.

Design choices baked in:
  - Stdlib only (urllib, json, csv). No requests, no pandas.
  - Exit non-zero on any failure. Caller (GitHub Actions) handles alerting.
  - Verbose output by default — POC stage, prefer noise to silence.
  - String comparison on ISO 8601 timestamps (lexicographic == chronological).
  - State file missing = clean first run, not an error.

Files written:
  data/state/constraint-costs.json     — {resource_id: last_modified} map
  data/processed/constraint-costs/
    schema.json                         — frozen field schema (validation reference)
    records.json                        — typed records, all FYs concatenated
  data/raw/constraint-costs/
    constraint-breakdown-YYYY-YYYY.csv  — one CSV per FY, archived as published

Run:
    python3 scrape.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration. Per ADR-002 decision 4: CKAN base + package_id, not URL list.
# ---------------------------------------------------------------------------

API_BASE = "https://api.neso.energy/api/3/action"
PACKAGE_ID = "fb56b46e-cef3-4eb8-9294-0ca19769b7eb"  # Constraint Breakdown Costs and Volume

# Paths are relative to repo root. Caller must `cd` to repo root before running,
# or pass --repo-root (not implemented yet — POC uses cwd).
REPO_ROOT = Path.cwd()
STATE_DIR = REPO_ROOT / "data" / "state"
STATE_FILE = STATE_DIR / "constraint-costs.json"
SCHEMA_FILE = STATE_DIR / "constraint-costs-schema.json"
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "constraint-costs"
RAW_DIR = REPO_ROOT / "data" / "raw" / "constraint-costs"
RECORDS_FILE = PROCESSED_DIR / "records.json"

# CKAN datastore default page size is 100. We bump it for fewer round-trips on
# large historical FYs (365 rows). 1000 is well under CKAN's 32000 ceiling.
PAGE_SIZE = 1000

# Polite, identifiable User-Agent. NESO data is open but we identify ourselves.
USER_AGENT = "net-zero-dashboard-poc/0.1 (constraint-costs scraper)"

# Network timeout in seconds. Anything beyond this and we'd rather fail loudly
# and let the next scheduled run try again than hang an Actions runner.
HTTP_TIMEOUT = 30


# ---------------------------------------------------------------------------
# HTTP helpers. Stdlib urllib because: one less dependency, plenty for a JSON API.
# ---------------------------------------------------------------------------

def http_get_json(url: str) -> dict[str, Any]:
    """Fetch a JSON URL. Raise on any failure — no silent fallbacks."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} from {url}")
        body = resp.read()
    return json.loads(body)


def http_get_bytes(url: str) -> bytes:
    """Fetch raw bytes (used for CSV archive)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} from {url}")
        return resp.read()


# ---------------------------------------------------------------------------
# State file. Tracks last_modified per resource_id from the previous run.
# Missing file = clean first run, not an error. Decision baked in: regenerable.
# ---------------------------------------------------------------------------

def load_state() -> dict[str, str]:
    if not STATE_FILE.exists():
        print(f"[state] no state file at {STATE_FILE} — first run.")
        return {}
    with STATE_FILE.open() as f:
        state = json.load(f)
    print(f"[state] loaded {len(state)} resource timestamps from {STATE_FILE}")
    return state


def save_state(state: dict[str, str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    print(f"[state] wrote {len(state)} resource timestamps to {STATE_FILE}")


# ---------------------------------------------------------------------------
# CKAN package walk. Returns the resource list, sorted by `position` so the
# splicer downstream gets deterministic ordering (oldest FY first).
# ---------------------------------------------------------------------------

def list_resources() -> list[dict[str, Any]]:
    url = f"{API_BASE}/package_show?id={PACKAGE_ID}"
    print(f"[package] GET {url}")
    payload = http_get_json(url)
    if not payload.get("success"):
        raise RuntimeError(f"package_show failed: {payload!r}")
    resources = payload["result"]["resources"]
    # Filter to CSV format only — defensive against future non-CSV resources
    # (e.g. PDFs, dashboards) being added to the package.
    csv_resources = [r for r in resources if (r.get("format") or "").upper() == "CSV"]
    csv_resources.sort(key=lambda r: r.get("position", 0))
    print(f"[package] found {len(csv_resources)} CSV resources "
          f"(of {len(resources)} total)")
    return csv_resources


# ---------------------------------------------------------------------------
# Datastore fetch. Pages through with limit/offset until len(records) < PAGE_SIZE,
# which signals the end. Returns (fields, records).
# ---------------------------------------------------------------------------

def fetch_datastore(resource_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_records: list[dict[str, Any]] = []
    fields: list[dict[str, Any]] | None = None
    offset = 0
    while True:
        params = urllib.parse.urlencode({
            "resource_id": resource_id,
            "limit": PAGE_SIZE,
            "offset": offset,
        })
        url = f"{API_BASE}/datastore_search?{params}"
        payload = http_get_json(url)
        if not payload.get("success"):
            raise RuntimeError(f"datastore_search failed for {resource_id}: {payload!r}")
        result = payload["result"]
        if fields is None:
            fields = result["fields"]
        page = result["records"]
        all_records.extend(page)
        if len(page) < PAGE_SIZE:
            # Last page. Sanity-check against `total` if present.
            total = result.get("total")
            if total is not None and len(all_records) != total:
                print(f"[fetch]   WARNING: fetched {len(all_records)} records but "
                      f"datastore reports total={total}")
            break
        offset += PAGE_SIZE
    assert fields is not None
    return fields, all_records


# ---------------------------------------------------------------------------
# Schema reference. First run writes it; subsequent runs validate against it.
#
# Validation rule (changelog v0.4, M-7): we validate value SHAPE, not CKAN's
# `type` field. CKAN reports the same logical column with different `type`
# values across resources in this package — Date as `date` or `timestamp`,
# Thermal constraints cost as `numeric` or `text` — without the underlying
# values changing shape. CKAN's type metadata is not a reliable signal in
# this dataset, so we infer a `value_class` from observed values on freeze
# and validate values against that class on every subsequent fetch.
#
# value_class is one of: "integer", "numeric", "date", "text".
# Inference is conservative — ambiguous columns fall through to "text" and
# become no-op for validation purposes.
#
# What still counts as drift (hard-fail):
#   - column added / removed / renamed
#   - column unit changed
#   - column value_class changed
#   - a value failing its value_class rule
#
# What doesn't count as drift any more:
#   - CKAN `type` changing (numeric ↔ text, date ↔ timestamp, etc.)
#   - values returned as strings rather than JSON numbers, if parseable
#
# Methodology source of truth: changelog v0.4 M-7 through M-9.
# ---------------------------------------------------------------------------

import re

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_integer_value(v: Any) -> bool:
    """Whole-number value: JSON int, or string parseable as int."""
    if isinstance(v, bool):  # bool is a subclass of int; exclude it.
        return False
    if isinstance(v, int):
        return True
    if isinstance(v, str):
        try:
            int(v)
            return True
        except ValueError:
            return False
    return False


def is_numeric_value(v: Any) -> bool:
    """Numeric value: JSON int/float, or string parseable as float."""
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        try:
            float(v)
            return True
        except ValueError:
            return False
    return False


def is_date_value(v: Any) -> bool:
    """YYYY-MM-DD string. Accepts an optional T-suffix (CKAN timestamp form)
    but only checks the leading 10 chars."""
    if not isinstance(v, str):
        return False
    return bool(DATE_RE.match(v[:10])) and (len(v) == 10 or v[10] == "T")


def infer_value_class(values: list[Any]) -> str:
    """Infer the value_class of a column from observed non-null values.

    Order matters: integer is tested before numeric because every int is also
    float-parseable. Conservative fallback to text for mixed/ambiguous columns.
    """
    non_null = [v for v in values if v is not None]
    if not non_null:
        # No data to infer from. Mark as text (no-op validation).
        return "text"
    if all(is_integer_value(v) for v in non_null):
        return "integer"
    if all(is_numeric_value(v) for v in non_null):
        return "numeric"
    if all(is_date_value(v) for v in non_null):
        return "date"
    return "text"


VALUE_CHECKERS = {
    "integer": is_integer_value,
    "numeric": is_numeric_value,
    "date": is_date_value,
    "text": lambda v: True,
}


def schema_signature(fields: list[dict[str, Any]],
                     records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce CKAN field metadata + observed values to validation signature.

    Stores ckan_type for audit but not validation. value_class is the source
    of truth for what shape the column actually holds.
    """
    sig = []
    for f in fields:
        col_id = f["id"]
        values = [r.get(col_id) for r in records]
        sig.append({
            "id": col_id,
            "unit": f.get("info", {}).get("unit"),
            "value_class": infer_value_class(values),
            "ckan_type": f["type"],
        })
    return sig


def validate_values(frozen_sig: list[dict[str, Any]],
                    records: list[dict[str, Any]],
                    resource_label: str) -> list[str]:
    """Check every value in records against its frozen value_class.

    Returns list of error strings (empty if all pass).
    """
    errors = []
    for entry in frozen_sig:
        col_id = entry["id"]
        vc = entry["value_class"]
        checker = VALUE_CHECKERS.get(vc, lambda v: True)
        for i, r in enumerate(records):
            v = r.get(col_id)
            if v is None:
                continue  # null values are allowed; revisit if it generates noise
            if not checker(v):
                errors.append(
                    f"{resource_label}: row {i} column {col_id!r} expected "
                    f"value_class={vc} but got value={v!r} ({type(v).__name__})"
                )
                # Stop reporting more errors for this column after the first.
                break
    return errors


def schemas_match(frozen: list[dict[str, Any]],
                  current: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Compare frozen vs current signature. Returns (match, diffs).

    Only the structural fields are compared here (id, unit, value_class).
    ckan_type is recorded but not validated against.
    """
    diffs = []
    if len(frozen) != len(current):
        diffs.append(f"field count: frozen={len(frozen)} current={len(current)}")
        return False, diffs
    for f, c in zip(frozen, current):
        if f["id"] != c["id"]:
            diffs.append(f"column rename: {f['id']!r} → {c['id']!r}")
        if f["unit"] != c["unit"]:
            diffs.append(f"unit change on {f['id']!r}: {f['unit']!r} → {c['unit']!r}")
        if f["value_class"] != c["value_class"]:
            diffs.append(
                f"value_class change on {f['id']!r}: "
                f"{f['value_class']!r} → {c['value_class']!r}"
            )
    return len(diffs) == 0, diffs


def validate_or_freeze_schema(fields: list[dict[str, Any]],
                              records: list[dict[str, Any]],
                              resource_label: str) -> None:
    """First run: write schema reference inferred from values.
    Later runs: validate structure (ids, units, value_class) and per-row values.
    Hard-fails on any drift, preserving cached data.
    """
    current = schema_signature(fields, records)
    if not SCHEMA_FILE.exists():
        SCHEMA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with SCHEMA_FILE.open("w") as f:
            json.dump(current, f, indent=2)
        print(f"[schema] froze schema reference at {SCHEMA_FILE} "
              f"({len(current)} fields, inferred from {resource_label})")
        for entry in current:
            print(f"[schema]   {entry['id']!r}: value_class={entry['value_class']} "
                  f"(ckan_type={entry['ckan_type']}, unit={entry['unit']!r})")
        return
    with SCHEMA_FILE.open() as f:
        frozen = json.load(f)
    # Structural check
    ok, diffs = schemas_match(frozen, current)
    if not ok:
        print(f"[schema] STRUCTURAL DRIFT on {resource_label}:")
        for d in diffs:
            print(f"[schema]   {d}")
        print("[schema] frozen signature:")
        print(json.dumps(frozen, indent=2))
        print("[schema] current signature:")
        print(json.dumps(current, indent=2))
        raise RuntimeError(
            f"Schema structural drift on {resource_label}. Cached data preserved. "
            f"Investigate manually before next run."
        )
    # Value-shape check
    errors = validate_values(frozen, records, resource_label)
    if errors:
        print(f"[schema] VALUE DRIFT on {resource_label}:")
        for e in errors[:10]:  # cap noise
            print(f"[schema]   {e}")
        if len(errors) > 10:
            print(f"[schema]   ... and {len(errors) - 10} more")
        raise RuntimeError(
            f"Value-shape drift on {resource_label}. Cached data preserved. "
            f"Investigate manually before next run."
        )


# ---------------------------------------------------------------------------
# CSV archive. Per ADR-002 decision 4: we keep the raw CSV as-published
# alongside the typed JSON. Two artefacts, same data, different audiences.
# ---------------------------------------------------------------------------

def archive_csv(resource: dict[str, Any]) -> Path:
    """Download the resource's CSV file and write to data/raw/constraint-costs/."""
    url = resource["url"]
    # Filename from the URL path — stable, matches NESO's published name.
    filename = url.rsplit("/", 1)[-1]
    if not filename.endswith(".csv"):
        # Defensive: if NESO ever changes URL pattern, fail loudly.
        raise RuntimeError(f"Expected .csv URL, got: {url}")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_DIR / filename
    body = http_get_bytes(url)
    target.write_bytes(body)
    print(f"[csv]   archived {filename} ({len(body)} bytes)")
    return target


# ---------------------------------------------------------------------------
# Records file. All FYs concatenated, sorted by Date. Splicer downstream slices
# this into headline windows. We also tag each record with its source resource
# so the splicer can detect "which FY does this row come from?" without parsing
# the date.
# ---------------------------------------------------------------------------

def write_records(records_by_resource: dict[str, list[dict[str, Any]]],
                  resource_meta: dict[str, dict[str, Any]]) -> None:
    """
    Combine per-FY records into one sorted file.

    records_by_resource: resource_id -> list of records
    resource_meta: resource_id -> {name, last_modified, fy_label}
    """
    combined = []
    for resource_id, recs in records_by_resource.items():
        meta = resource_meta[resource_id]
        for rec in recs:
            tagged = dict(rec)
            tagged["_resource_id"] = resource_id
            tagged["_fy_label"] = meta["fy_label"]
            combined.append(tagged)
    # Sort by Date. CKAN returns ISO date strings, so lexicographic == chronological.
    combined.sort(key=lambda r: r.get("Date", ""))
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with RECORDS_FILE.open("w") as f:
        json.dump(combined, f, indent=2)
    print(f"[records] wrote {len(combined)} records to {RECORDS_FILE}")


# ---------------------------------------------------------------------------
# FY label extraction from URL. Brittle on `name` (free-text), stable on URL.
# Verified in discovery: every URL is .../constraint-breakdown-YYYY-YYYY.csv
# ---------------------------------------------------------------------------

def fy_label_from_url(url: str) -> str:
    fname = url.rsplit("/", 1)[-1]
    # constraint-breakdown-2026-2027.csv -> 2026-2027
    # Defensive parsing: if the pattern changes, fail loudly.
    if not fname.startswith("constraint-breakdown-") or not fname.endswith(".csv"):
        raise RuntimeError(f"Unexpected resource filename: {fname}")
    label = fname[len("constraint-breakdown-"):-len(".csv")]
    # Sanity: should be YYYY-YYYY.
    parts = label.split("-")
    if len(parts) != 2 or not all(p.isdigit() and len(p) == 4 for p in parts):
        raise RuntimeError(f"Unexpected FY label parsed from filename: {label!r}")
    return label


# ---------------------------------------------------------------------------
# Main loop.
# ---------------------------------------------------------------------------

def main() -> int:
    print(f"[run] cwd={REPO_ROOT}")
    state_before = load_state()
    state_after: dict[str, str] = dict(state_before)  # copy; updated as we go

    resources = list_resources()
    fetched: list[str] = []
    skipped: list[str] = []
    records_by_resource: dict[str, list[dict[str, Any]]] = {}
    resource_meta: dict[str, dict[str, Any]] = {}

    for r in resources:
        rid = r["id"]
        last_mod = r["last_modified"]
        fy = fy_label_from_url(r["url"])
        label = f"{fy} ({rid})"
        resource_meta[rid] = {
            "name": r["name"],
            "last_modified": last_mod,
            "fy_label": fy,
        }

        prev = state_before.get(rid)
        # String compare is correct here: ISO 8601 sorts lexicographically.
        if prev is not None and prev >= last_mod:
            print(f"[skip] {label} unchanged since {prev}")
            skipped.append(rid)
            # We still need the records for this FY in records.json, so re-load
            # from previous run? Or trust that the caller will splice from raw?
            # Decision: skip means skip — records.json is rebuilt only from
            # currently-fetched data. To avoid losing unchanged FYs, we ALSO
            # need to fetch them. Re-think:
            # Option A: skip fetch but include previously-cached records.
            # Option B: always fetch, only short-circuit on identical hash.
            # Option C: fetch only changed, but also re-emit unchanged from CSV archive.
            #
            # For POC simplicity: if nothing changed across ALL resources,
            # records.json is left alone. If anything changed, we re-fetch
            # everything to rebuild records.json cleanly. See below.
            continue

        print(f"[fetch] {label} (was {prev or 'never'}, now {last_mod})")
        fields, records = fetch_datastore(rid)
        validate_or_freeze_schema(fields, records, label)
        archive_csv(r)
        records_by_resource[rid] = records
        state_after[rid] = last_mod
        fetched.append(rid)
        print(f"[fetch]   got {len(records)} records")

    # If anything was fetched but some resources were skipped, we need the
    # skipped resources' records too — otherwise records.json loses FYs.
    # Simplest correct behaviour: if ANY resource changed, refetch all.
    # This is a deliberate POC trade-off (bandwidth for simplicity).
    if fetched and skipped:
        print(f"[refetch] {len(fetched)} changed, {len(skipped)} unchanged — "
              f"refetching unchanged to rebuild records.json")
        for rid in skipped:
            r = next(x for x in resources if x["id"] == rid)
            fields, records = fetch_datastore(rid)
            validate_or_freeze_schema(fields, records, f"{resource_meta[rid]['fy_label']} ({rid})")
            records_by_resource[rid] = records
            print(f"[refetch] {resource_meta[rid]['fy_label']}: {len(records)} records")

    if not fetched:
        print("[run] no resources changed since last run — nothing to do.")
        return 0

    write_records(records_by_resource, resource_meta)
    save_state(state_after)
    print(f"[run] done. fetched={len(fetched)} skipped={len(skipped)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # ADR-002 decision 7: hard failure, no auto-recovery. Cached data is
        # untouched because we only write at the end of a successful run.
        print(f"[FATAL] {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
