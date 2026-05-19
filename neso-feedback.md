# NESO data feedback log

Running record of friction, ambiguities, and improvement requests observed while building against NESO open data sources. Intended as:

- A record for ourselves of where the source has caused real work, so we can track whether things improve over time.
- A list of concrete questions and requests we could put to NESO if we get the chance (data portal feedback, public engagement events, direct contact).

Each entry is dated, scoped to a specific dataset, and describes what we observed and what would help. Entries are not deleted when resolved; they're marked resolved with a date and a note. The audit trail matters.

---

## Constraint Breakdown Costs and Volume

Source: `https://www.neso.energy/data-portal/constraint-breakdown-costs-and-volume`
Package id: `fb56b46e-cef3-4eb8-9294-0ca19769b7eb`

### F-1 (5 May 2026) — Inconsistent CKAN `type` metadata across resources in the same package

**Observed:** The same logical columns are typed differently across FY resources. Specifically:

- `Date` column is CKAN type `timestamp` in the 2017-18 and 2018-19 resources, and `date` in 2019-20 onwards. Values are identical ISO 8601 date strings in all cases.
- `Thermal constraints cost` is CKAN type `numeric` in nine of ten FY resources but `text` in the 2025-26 resource. All 364 values in 2025-26 are number-as-string and parse cleanly as float; the other nine FYs return JSON numbers.

**Impact on consumers:** Any consumer that trusts CKAN's `type` field to write strongly-typed code will hit an exception when iterating across FYs. We worked around this by treating CKAN type as advisory and validating against value shape (`float()`-parseable for numeric columns). This is more code than should be necessary for a well-published dataset.

**Request:** Consistent CKAN typing across resources within a package. Ideally `numeric` for all cost and volume columns regardless of FY, and `date` (or `timestamp`, but one of them, consistently) for the Date column.

**Status:** Open.

### F-2 (5 May 2026) — Sign convention for volume columns is undocumented

**Observed:** The four volume columns (`Reducing largest loss volume`, `Increasing system inertia volume`, `Voltage constraints volume`, `Thermal constraints volume`) include negative values without explanation. For example, `Thermal constraints volume` on 2026-04-01 is -59,177 MWh. The CKAN field metadata documents the unit (MWh) but not the sign convention.

**Impact on consumers:** Volume data is unusable for downstream visualisation or analysis without knowing whether negative means "turn-down action," "net flow direction," "imbalance," or something else. We have deliberately not published the volume columns on our dashboard as a result (see methodology changelog v0.2, M-4).

**Request:** Either (a) extend the CKAN field `info.comment` to document the sign convention for each volume column, or (b) publish a short methodology note alongside the dataset describing how to interpret negative values.

**Status:** Open. We will reach out for clarification at some point during the POC build.

### F-3 (5 May 2026) — Missing day in 2025-26 resource

**Observed:** The 2025-26 resource returned 364 records where 365 are expected for a non-leap UK financial year (1 April 2025 to 31 March 2026). All other closed FYs returned the expected count (365 or 366 in leap years). The specific missing day has not been identified yet.

**Impact on consumers:** A reader summing the FY column to a headline figure will be summing 364 days, not 365. The difference is presumably small if the missing day is a low-action day, but we don't know that without identifying which day is missing.

**Request:** Either (a) publish missing days as zero-valued rows where no constraint actions occurred, or (b) include a note alongside the dataset explaining when rows are omitted vs published as zero.

**Status:** Open. To be investigated when we next have time — not blocking POC build. Flagged on the card as a data caveat in v0.4 changelog entry.
