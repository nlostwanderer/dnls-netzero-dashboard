#!/usr/bin/env python3
"""
NESO constraint costs — discovery script v2.

What we learned from v1:
  - NESO's CKAN API is at api.neso.energy, NOT www.neso.energy.
  - The dataset is split per UK financial year (Apr-Mar), with a separate
    resource per FY. The known 2026-2027 resource_id is hardcoded below.

What this script does (and ONLY this — not the production scraper):
  1. Hits the CKAN datastore_search endpoint for the known 2026-27 resource_id.
     Prints the raw response so we can see what fields and metadata come back.
  2. Hits resource_show for the same resource_id. This is CKAN's metadata
     endpoint and should give us the human-readable description, last update
     time, and parent dataset (package).
  3. Walks back from the parent package to list ALL its resources — this is
     how we find the prior FY's resource_id without hardcoding it.
  4. If a prior-FY resource is found, fetches its field schema and prints a
     side-by-side comparison with 2026-27, so we can see if the schema is
     stable across years (and therefore safe to splice for trailing-12-month).

Anti-scope:
  - No parsing into pandas, no aggregation, no rendering.
  - No fallbacks, no retries, no schedule logic.
  - We are looking, not building.

Run:
    python3 fetch_constraint_costs_discovery_v2.py

Stdlib only.
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.neso.energy/api/3/action"
KNOWN_2026_27_RESOURCE_ID = "4136a8e2-07c5-4784-8096-28999447a16e"

HEADERS = {
    "User-Agent": "net-zero-dashboard-poc/0.1 (discovery; contact: <your email here>)",
    "Accept": "application/json",
}

OUT_DIR = Path("./neso_discovery_output_v2")
OUT_DIR.mkdir(exist_ok=True)


def fetch_json(url: str, label: str, save_as: str) -> dict | None:
    """Fetch a URL expected to return JSON. Print diagnostics. Save raw body. Return parsed dict or None."""
    print(f"\n{'=' * 70}")
    print(f"STEP: {label}")
    print(f"URL:  {url}")
    print("=" * 70)

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"STATUS: {resp.status}")
            print(f"FINAL URL: {resp.url}")
            ct = resp.headers.get("Content-Type", "<missing>")
            print(f"CONTENT-TYPE: {ct}")
            body = resp.read()
            print(f"BODY LENGTH: {len(body)} bytes")
            (OUT_DIR / save_as).write_bytes(body)
            print(f"SAVED RAW TO: {OUT_DIR / save_as}")

            # Show first 1500 chars of raw body so we can SEE what we got
            preview = body[:1500].decode("utf-8", errors="replace")
            print(f"\nFIRST 1500 CHARS OF RAW BODY:\n{preview}")
            if len(body) > 1500:
                print(f"... ({len(body) - 1500} more bytes in saved file)")

            # Now attempt to parse — if this fails, we've learned something
            try:
                return json.loads(body)
            except json.JSONDecodeError as e:
                print(f"\nWARNING: response is not JSON ({e}). Endpoint may not exist or may be returning HTML.")
                return None

    except urllib.error.HTTPError as e:
        print(f"HTTP ERROR: {e.code} {e.reason}")
        print("RESPONSE HEADERS:")
        for k, v in e.headers.items():
            print(f"  {k}: {v}")
        try:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"ERROR BODY (first 500): {err_body[:500]}")
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"OTHER ERROR: {type(e).__name__}: {e}")
        return None


def print_field_schema(fields: list, label: str) -> list[tuple[str, str]]:
    """Print a CKAN field list and return [(id, type), ...] tuples for comparison."""
    print(f"\n--- FIELD SCHEMA: {label} ---")
    schema = []
    for f in fields:
        fid = f.get("id", "<no id>")
        ftype = f.get("type", "<no type>")
        info = f.get("info", {}) or {}
        flabel = info.get("label", "")
        funit = info.get("units", "")
        print(f"  {fid!r}  type={ftype}  label={flabel!r}  unit={funit!r}")
        schema.append((fid, ftype))
    return schema


def main() -> int:
    print("NESO constraint costs — discovery script v2")
    print(f"Output directory: {OUT_DIR.resolve()}")

    # --- STEP 1: datastore_search on the known 2026-27 resource_id ---
    # limit=3 keeps the response small. The fields metadata comes back regardless of limit.
    ds_url = (
        f"{API_BASE}/datastore_search"
        f"?resource_id={KNOWN_2026_27_RESOURCE_ID}&limit=3"
    )
    ds_resp = fetch_json(ds_url, "datastore_search (2026-27, limit=3)", "01_datastore_2026_27.json")
    if ds_resp is None or not ds_resp.get("success"):
        print("\nFATAL: datastore_search failed for the known resource_id.")
        print("This is the API call the dashboard's whole pipeline depends on.")
        print("Paste the output above back to me.")
        return 1

    result = ds_resp.get("result", {})
    fields_2026 = result.get("fields", [])
    schema_2026 = print_field_schema(fields_2026, "2026-27")
    sample_records = result.get("records", [])
    print(f"\nSAMPLE RECORDS (first {len(sample_records)}):")
    for r in sample_records:
        print(f"  {r}")
    print(f"\nTOTAL ROW COUNT (per API): {result.get('total', '<not provided>')}")

    # --- STEP 2: resource_show for the parent package_id ---
    rs_url = f"{API_BASE}/resource_show?id={KNOWN_2026_27_RESOURCE_ID}"
    rs_resp = fetch_json(rs_url, "resource_show (2026-27)", "02_resource_show_2026_27.json")
    if rs_resp is None or not rs_resp.get("success"):
        print("\nWARNING: resource_show failed. Cannot walk to parent package.")
        print("We can still build the POC pipeline against the known resource_id, but")
        print("multi-FY discovery will need to be done manually.")
        return 0

    rs_result = rs_resp.get("result", {})
    package_id = rs_result.get("package_id")
    last_modified = rs_result.get("last_modified") or rs_result.get("created", "<unknown>")
    print(f"\nPARENT PACKAGE_ID: {package_id}")
    print(f"RESOURCE LAST_MODIFIED: {last_modified}")
    print(f"RESOURCE NAME: {rs_result.get('name', '<no name>')}")
    print(f"RESOURCE FORMAT: {rs_result.get('format', '<no format>')}")

    if not package_id:
        print("\nNo package_id on the resource. Cannot find sibling FY resources via API.")
        return 0

    # --- STEP 3: package_show to list sibling resources (other FYs) ---
    ps_url = f"{API_BASE}/package_show?id={package_id}"
    ps_resp = fetch_json(ps_url, f"package_show ({package_id})", "03_package_show.json")
    if ps_resp is None or not ps_resp.get("success"):
        print("\nWARNING: package_show failed. Cannot enumerate sibling FYs from API.")
        return 0

    ps_result = ps_resp.get("result", {})
    print(f"\nPACKAGE TITLE: {ps_result.get('title', '<no title>')}")
    print(f"PACKAGE NAME:  {ps_result.get('name', '<no name>')}")
    print(f"PACKAGE METADATA_MODIFIED: {ps_result.get('metadata_modified', '<unknown>')}")

    siblings = ps_result.get("resources", [])
    print(f"\nSIBLING RESOURCES IN PACKAGE: {len(siblings)}")
    prior_fy_resource_id = None
    for r in siblings:
        rid = r.get("id", "<no id>")
        rname = r.get("name", "<no name>")
        rfmt = (r.get("format") or "").upper()
        rmod = r.get("last_modified") or r.get("created", "<no date>")
        marker = "  <-- KNOWN 2026-27" if rid == KNOWN_2026_27_RESOURCE_ID else ""
        print(f"  - id={rid}  name={rname!r}  format={rfmt}  last_modified={rmod}{marker}")
        # Heuristic: pick a CSV resource that ISN'T the 2026-27 one and mentions 2025
        # in the name. Print-first: we'll see if the heuristic works in the output.
        if (
            prior_fy_resource_id is None
            and rid != KNOWN_2026_27_RESOURCE_ID
            and rfmt == "CSV"
            and "2025" in rname
        ):
            prior_fy_resource_id = rid

    if not prior_fy_resource_id:
        print("\nNo obvious 2025-26 sibling found by name heuristic.")
        print("Look at the sibling list above and tell me which (if any) is the 2025-26 file.")
        return 0

    # --- STEP 4: schema-stability check against the prior FY ---
    print(f"\nFOUND CANDIDATE 2025-26 RESOURCE: {prior_fy_resource_id}")
    ds2_url = f"{API_BASE}/datastore_search?resource_id={prior_fy_resource_id}&limit=1"
    ds2_resp = fetch_json(ds2_url, "datastore_search (prior FY, limit=1)", "04_datastore_prior_fy.json")
    if ds2_resp is None or not ds2_resp.get("success"):
        print("\nWARNING: datastore_search failed on the prior FY candidate.")
        print("Schema-stability check skipped.")
        return 0

    fields_prior = ds2_resp.get("result", {}).get("fields", [])
    schema_prior = print_field_schema(fields_prior, "prior FY (candidate)")

    # --- STEP 5: print a stark schema diff ---
    print("\n--- SCHEMA STABILITY CHECK ---")
    set_2026 = set(schema_2026)
    set_prior = set(schema_prior)
    if set_2026 == set_prior:
        print("OK: schemas are IDENTICAL (same field names and types).")
        print("Splicing across years is safe at the schema level.")
    else:
        print("WARNING: schemas differ between FYs.")
        only_2026 = set_2026 - set_prior
        only_prior = set_prior - set_2026
        if only_2026:
            print(f"  Only in 2026-27: {sorted(only_2026)}")
        if only_prior:
            print(f"  Only in prior FY: {sorted(only_prior)}")
        print("Splicer will need to handle column drift. Document in methodology.")

    print(f"\nAll output saved to {OUT_DIR.resolve()}")
    print("Paste the printed output back and we'll design the production pipeline from there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
