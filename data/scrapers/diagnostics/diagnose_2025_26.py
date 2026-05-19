#!/usr/bin/env python3
"""
One-shot diagnostic: why is Thermal constraints cost typed as `text` for FY 2025-26?

Not part of the production pipeline. Standalone investigation tool.
Prints actual values to determine whether:
  (a) values are number-as-string (CKAN type quirk, no real data issue)
  (b) values contain non-numeric content (real data quality problem)
"""

import json
import urllib.request
from collections import Counter

RESOURCE_ID = "6afe1c2b-6d70-4e76-8e74-0952b0a2beab"  # 2025-26
URL = (
    "https://api.neso.energy/api/3/action/datastore_search"
    f"?resource_id={RESOURCE_ID}&limit=1000"
)

print(f"GET {URL}")
with urllib.request.urlopen(URL, timeout=30) as resp:
    payload = json.loads(resp.read())

result = payload["result"]
records = result["records"]
print(f"Fetched {len(records)} of {result['total']} total rows")
print()

# First 10 rows verbatim
print("=== First 10 rows of Thermal constraints cost ===")
for r in records[:10]:
    val = r.get("Thermal constraints cost")
    print(f"  Date={r.get('Date')!r:<14}  value={val!r:<20}  python_type={type(val).__name__}")

print()

# Distribution of Python types across the whole resource
print("=== Python type distribution across all rows ===")
type_counts = Counter(type(r.get("Thermal constraints cost")).__name__ for r in records)
for t, n in type_counts.most_common():
    print(f"  {t}: {n}")

print()

# If any are strings, can they all be parsed as float?
str_values = [r.get("Thermal constraints cost") for r in records
              if isinstance(r.get("Thermal constraints cost"), str)]
if str_values:
    print(f"=== String values: {len(str_values)} found ===")
    print("First 5 string values verbatim:")
    for v in str_values[:5]:
        print(f"  {v!r}")
    unparseable = []
    for v in str_values:
        try:
            float(v)
        except (ValueError, TypeError):
            unparseable.append(v)
    print(f"Unparseable as float: {len(unparseable)}")
    if unparseable:
        print("First 10 unparseable values:")
        for v in unparseable[:10]:
            print(f"  {v!r}")
    else:
        print("All string values parse cleanly as float.")

# Also sanity-check the other columns for comparison
print()
print("=== Other cost columns: Python type for first row ===")
first = records[0] if records else {}
for col in ["Reducing largest loss cost", "Increasing system inertia cost",
            "Voltage constraints cost", "Thermal constraints cost"]:
    val = first.get(col)
    print(f"  {col}: value={val!r}  type={type(val).__name__}")