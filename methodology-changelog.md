# Methodology Changelog

This document records every change to the dashboard's methodology since the rubric was frozen for the POC build (`rubric-v0.1.md`, 4 May 2026).

The rubric document itself remains at v0.1 until the post-POC review (week 10 ship/shelve decision per `ADR-001`). Entries below are the running log of decisions that will be folded into the next rubric version at that review.

Format for each entry: dated, with reasoning, with link to the ADR or chat decision that authorised it. Cosmetic-only edits to the rubric (typo fixes, wording clarifications that don't change meaning) are permitted in-place without a changelog entry. Anything that changes what gets shown, what gets scored, or how a metric is sourced gets an entry.

---

## v0.2 — 4 May 2026 — First metric-specific methodology layer (constraint costs)

**Trigger:** End-to-end discovery work on the constraint costs metric (the POC pilot card) revealed methodology choices that the rubric did not cover. Decisions made during chat session of 4 May 2026; data acquisition aspects captured separately in `ADR-002-data-acquisition-constraint-costs.md`.

### Changes

#### M-1. Constraint costs is a context card, not a scored metric

The constraint costs card carries no traffic light. It shows the figure, a sparkline of historical values, and an explainer.

**Reasoning:** The rubric in v0.1 §2 scores capacity metrics against 2030 targets via gap-closure projection. Constraint costs is a £/year operational cost figure with no government 2030 target to score against. Forcing it into the rubric would either invent a target or distort what the metric represents.

**Implication for plan §1 success criterion 1:** The success criterion previously read *"Every metric has a documented source, refresh cadence, and a written rubric for its traffic light."* It has been amended to *"Every metric has a documented source and refresh cadence. Every scored metric has a written rubric for its traffic light. Context cards (metrics that are not scored) are documented separately and explicitly carry no scoring."* This preserves the source-and-cadence requirement for all metrics (including context cards) while restricting the rubric requirement to scored metrics only. Wording correction, not a substantive change. Applied to `net-zero-dashboard-plan.md` on 5 May 2026.

**Implication for the dashboard:** A third visual treatment is now in scope, alongside the three trackers in `ADR-001` decision 4. Context cards exist as a fourth pattern. They appear within the infrastructure tracker section but are visually distinct from scored cards. Cognitive-load risk noted in `ADR-001` consequences is therefore mildly worse than originally documented; mitigated by clear visual separation and methodology page copy.

#### M-2. Headline figure for constraint costs is thermal constraints cost only

The headline figure on the card is `Thermal constraints cost`, the single column from the NESO source. The other three cost categories (`Reducing largest loss cost`, `Increasing system inertia cost`, `Voltage constraints cost`) are not the headline.

**Reasoning:**
- Thermal constraints cost is the figure that maps onto the public conversation about grid bottlenecks and the build-out of transmission. Aligned with the dashboard's net-zero-infrastructure framing.
- Aggregating the four categories into a single "total constraint cost" would conflate four mechanically distinct types of system action and weaken the explainer that has to accompany the figure.
- Two of the three non-headline categories (`Reducing largest loss`, `Increasing system inertia`) are observed to be zero across all current data. Aggregating them with thermal would not change the headline materially but would invite "what are these zeros" questions on the underlying data download.

**Editorial constraint baked in:** Thermal constraints cost is the *system cost of managing thermal network constraints* — including both turn-down payments to constrained-out generation and turn-up payments to alternative generation. It is **not** the same as "money paid to wind farms to switch off," which is the simplified version that appears in tabloid coverage. The card explainer copy must respect this distinction. If the explainer ever drifts into "wind paid to switch off" framing, that is a methodology violation, not a stylistic choice. Drafting of the explainer is deferred until the card has been rendered.

#### M-3. Non-headline cost categories deferred from display

`Reducing largest loss cost`, `Increasing system inertia cost`, and `Voltage constraints cost` are not displayed on the card at POC. They are fetched and stored in the underlying data (per `ADR-002` decision 5) but do not appear in the visible figure or sparkline.

**Reasoning:** Units and definitions are now confirmed (£ for cost columns; clear definitions in NESO's field metadata), so the original "defer until we have units and definitions confirmed" reason has expired. The new reason for deferring display is editorial focus: the card has one job (publish a credible thermal constraint cost figure with explainer), and adding three more cost columns multiplies the explainer surface area without adding a metric the dashboard's net-zero-infrastructure thesis depends on.

**Reversibility:** All four cost columns are stored. Adding the others to the card later is a display change, not a data change.

#### M-4. Volume columns held from publication

The four volume columns (`Reducing largest loss volume`, `Increasing system inertia volume`, `Voltage constraints volume`, `Thermal constraints volume`) are fetched and stored but not published in any form on the card or in the methodology beyond a footnote acknowledging the columns exist.

**Reasoning:** NESO's field metadata documents the volumes as MWh but does not document the sign convention. Observed values include negatives (e.g. `Thermal constraints volume` = -59,177 MWh on 2026-04-01) without an accompanying explanation in the field metadata or package notes. Publishing a column whose sign convention we do not understand is a methodology credibility risk — see plan §1 success criterion 3.

**Trigger to revisit:** Either (a) finding documentation that defines the sign convention, or (b) reaching out to NESO for clarification. Either should be logged here when it happens.

#### M-5. Time window for headline figure: latest complete UK FY

The headline figure is the sum of `Thermal constraints cost` over the most recent UK financial year that has fully closed (April → March). As of v0.2 (May 2026), that is FY 2025-26.

**Reasoning:** Captured in `ADR-002` decision 2. Briefly: unambiguous, aligns with public commentary, deferring trailing-12-month is acceptable POC scope.

**Implication for the card:** The card displays the FY label prominently (e.g. "FY 2025-26") and a "data through" date stamp showing the most recent NESO refresh. Readers should be able to tell at a glance whether the figure is from a closed or in-progress window.

**Annual rollover behaviour:** Each April, the headline FY rolls forward to the just-closed year. This is a known stale-period: the figure does not refresh between April rollovers within a given FY. Acceptable for POC; if we add a "current FY in progress" secondary view post-POC, that becomes the live figure.

### Items deferred to a later changelog entry

The following items were touched on during the 4 May 2026 session but are not yet locked-in and will appear in subsequent entries when they are:

- The card explainer copy ("what this means" panel). Drafting deferred until the card has been rendered, per project owner's call.
- The dashboard methodology page text (the public-facing version of these decisions). To be drafted in plan weeks 6-7.
- Whether the non-headline cost categories ever return to the card (e.g. as a "show all categories" toggle).
- Whether volume columns ever get published, conditional on resolving the sign convention.

### Items that do NOT change

- Rubric thresholds for scored metrics (`rubric-v0.1` §3) are unchanged. v0.2 adds a context-card pattern; it does not modify scoring.
- The three-tracker architecture (`ADR-001` decision 4) is unchanged. Context cards live within the infrastructure tracker, distinguished visually but not architecturally.
- The opportunities and major projects rubrics are unchanged.

### Review trigger for v0.2

Re-examined at week 10 ship/shelve decision alongside the rest of the rubric. Specific questions:

- Did the context-card pattern actually look distinct enough from scored cards to readers, or did the visual separation fail?
- Did the explainer copy hold the editorial line on thermal-cost ≠ curtailment-payments, or did it drift?
- Did the held-back columns (volumes, non-headline costs) generate reader friction?
- Did anyone find documentation of the volume sign convention during the build, and if so what does the methodology say about it now?

---

## v0.3 — 5 May 2026 — Schema validation: type equivalence rule

**Trigger:** First production run of the constraint costs scraper (5 May 2026) failed validation against the 2019-20 resource. Root cause was not a real schema breakage but per-resource variation in CKAN's `type` metadata: the 2017-18 and 2018-19 resources type the `Date` column as `timestamp`, while 2019-20 onwards type it as `date`. Same column, same unit, same value shape. The original validation rule in `ADR-002` decision 7 treated this as drift and hard-failed; this entry refines the definition of drift.

**Note:** This entry is superseded by v0.4 (M-7) the same day. Left in place as historical record of the intermediate approach.

### Changes

#### M-6. CKAN type equivalence rule (SUPERSEDED by v0.4 M-7)

The schema validation rule introduced in `ADR-002` decision 7 was refined to treat certain CKAN types as equivalent for validation purposes. Initial equivalence table contained one class: `date` ↔ `timestamp`.

This approach was abandoned within hours when a second, different CKAN type inconsistency surfaced on the 2025-26 resource (`numeric` ↔ `text` on `Thermal constraints cost`). The pattern revealed that CKAN's per-resource type metadata is not a reliable signal in this dataset, so an equivalence table would have required indefinite extension. v0.4 supersedes this approach with value-shape validation that doesn't rely on CKAN's type field at all.

See v0.4 M-7 for the replacement rule. See `neso-feedback.md` F-1 for the underlying NESO data quality observation.

### Review trigger for v0.3

Subsumed into v0.4 review trigger.

---

## v0.4 — 5 May 2026 — Validation rule rewritten: value-shape, not CKAN type

**Trigger:** Second production run of the constraint costs scraper (5 May 2026, after the v0.3 equivalence rule was in place) failed validation against the 2025-26 resource. CKAN reports `Thermal constraints cost` as type `text` for that resource; for all other FYs it reports `numeric`. Diagnostic against the actual values showed 364 of 364 values are string-encoded but parse cleanly as float. The data is operationally numeric; only NESO's metadata disagrees.

This is the second case in 24 hours where CKAN's `type` field has changed without the underlying values changing shape. v0.3 (M-6) added a single equivalence class to handle `date` ↔ `timestamp`. Adding a second equivalence class for `numeric` ↔ `text` would be defensible but treats the symptom rather than the cause: CKAN's per-resource type metadata is not a reliable signal in this dataset. v0.4 supersedes M-6 with a value-shape rule that validates what the data actually looks like, not what CKAN says it is.

This is the **third** revision to the validation logic in two days. We resist a fourth: if a value-shape rule fails on a future fetch, the next response is to investigate the values themselves, not to relax the rule again.

### Changes

#### M-7. Value-shape validation supersedes type-equivalence

The schema validation rule is rewritten. CKAN's `type` field is no longer the source of truth for validation; values are.

The frozen schema reference now stores, per column:

- `id` — column name (unchanged).
- `unit` — from CKAN field `info.unit` (unchanged).
- `value_class` — one of `numeric`, `date`, `integer`, `text`. Inferred from observed values on first freeze (see M-9).
- `ckan_type` — recorded for audit but not used for validation.

The validation rule on every subsequent fetch is:

| `value_class` | Rule for each non-null value |
|---|---|
| `numeric` | Value is either a JSON number, or a string that `float(v)` parses without raising. |
| `integer` | Value is either a JSON integer, or a string that `int(v)` parses without raising. |
| `date` | Value matches `YYYY-MM-DD` (regex `^\d{4}-\d{2}-\d{2}$`). |
| `text` | No content check; any value passes. |

Drift signals (these still hard-fail):

- A column added, removed, or renamed.
- A column's `unit` changing.
- A column's `value_class` changing.
- A value failing its `value_class` rule.

What is **not** drift any more (these now pass):

- CKAN `type` changing within or across `value_class` (e.g. `numeric` ↔ `text`, `date` ↔ `timestamp`).
- Records appearing as strings rather than JSON-typed numbers, as long as they're parseable.

#### M-8. M-6 (type equivalence rule) is superseded

The TYPE_EQUIVALENCE table introduced in v0.3 M-6 is removed from the scraper. The `date` ≈ `timestamp` case it handled is now covered by `value_class = date` accepting either CKAN typing transparently.

M-6 is left in this changelog as historical record. It is not in force.

#### M-9. value_class inference rules

On first freeze, `value_class` is inferred from the observed values in the first fetched resource:

1. If every non-null value is a JSON integer, or every non-null value is a string that `int(v)` parses without raising → `integer`.
2. Else if every non-null value is a JSON number, or every non-null value is a string that `float(v)` parses without raising → `numeric`.
3. Else if every non-null value matches `^\d{4}-\d{2}-\d{2}$` → `date`.
4. Else → `text`.

Order matters: `integer` is tested before `numeric` because every int is float-parseable. The inference is deliberately conservative — if a column is mixed or ambiguous, it falls through to `text` and validation becomes a no-op for that column.

**Known limitation:** if the first resource fetched happens to have an entirely-integer-valued column (e.g. all zeros, or all whole-pound costs), the column gets typed as `integer` and a later fractional value would fail validation. The fix is a manual re-freeze, deliberate not automatic. We do not silently widen.

#### M-10. Missing day in 2025-26 resource — flagged as data caveat

The 2025-26 resource returns 364 records where a non-leap UK financial year has 365. The other closed FYs (2017-18 through 2024-25) all returned the expected count (365, or 366 for the leap years 2019-20 and 2023-24). The specific missing day has not been identified.

This is logged in `neso-feedback.md` entry F-3 with the request for NESO to either publish zero-valued rows or document when rows are omitted.

**Implication for the card:** when the 2025-26 FY becomes the headline window (per v0.2 M-5), the card displays the headline figure but appends a data caveat noting that the source returned 364 rows for the FY, not 365, and links to F-3 for context. Caveat copy to be drafted alongside the card explainer.

#### M-11. NESO feedback log introduced

`neso-feedback.md` added to the project. A running record of friction, ambiguities, and improvement requests observed while building against NESO sources. Seeded with three entries from week 1 discovery:

- F-1: inconsistent CKAN `type` across FY resources (the trigger for v0.3 and v0.4).
- F-2: undocumented sign convention on volume columns (from v0.2 M-4).
- F-3: missing day in 2025-26 (above).

Entries are dated, scoped to a dataset, and not deleted when resolved (marked resolved instead). The audit trail is the point.

### Implications

- `ADR-002` decision 7 text still reads "validates the field schema against a frozen reference on every fetch." Accurate; the rule is refined, not removed. Worth updating ADR-002 prose at the v1 ship review to reference value-shape validation explicitly. Not in scope for POC build.
- Schema reference file format changes (new fields: `value_class`, `ckan_type`; same overall structure). Existing schema file at `data/state/constraint-costs-schema.json` is now obsolete and must be deleted before the next run so it freezes against the new format. This is the second forced deletion in two days; both expected, both cheap.
- The TYPE_EQUIVALENCE constant is removed from `scrape.py`. The methodology source of truth for what counts as drift is this v0.4 entry.

### Items deferred

- Value-shape inference is hard-coded to the four classes above. If a future column needs a different shape (e.g. boolean, enum, currency-prefixed string) we add a new value_class with a changelog entry.
- ADR-002 prose update to reference v0.4. Defer to ship review.

### Items that do NOT change

- Thresholds, three-tracker architecture, opportunities rubric, major projects tracker — all unchanged.
- Constraint costs methodology choices in v0.2 (M-1 through M-5) — unchanged.
- The headline window definition (latest complete UK FY; v0.2 M-5) — unchanged. The missing day in 2025-26 is flagged as a caveat on the card, not as a reason to change the window.

### Review trigger for v0.4

Re-examined at week 10 ship/shelve decision. Specific questions:

- Did the value-shape rule hold across all sources added during the POC, or did we need a v0.5?
- Did the missing-day caveat on the card cause reader confusion?
- Did any of the NESO feedback entries (F-1, F-2, F-3) get resolved by NESO during the build?

v0.6 --- 8 June 2026 --- Offshore wind output: range scoring, quarter-end anchor, full-history sparkline
----------------------------------------------------------------------------------------------------

**Trigger:** Building the offshore wind splicer (first scored metric) against REPD Q1 2026 surfaced three decisions the rubric and prior changelog did not cover: the 2030 target is published as a range not a point figure; the trailing-window anchor needed fixing explicitly; and the §5 sparkline window needed a per-metric call. v0.5 (M-12 through M-16) settled the card *design* (pipeline bar, lumpiness, REPD as source); v0.6 settles the *scoring inputs and output shape*.

### Changes

#### M-17. Offshore wind 2030 target scored as a range (43--50 GW), not a point

The offshore wind delivery ratio and slip year are computed against both ends of the government's 2030 capacity range, 43 GW and 50 GW, and both are surfaced on the card.

**Reasoning:** The Clean Power 2030 Action Plan (DESNZ, December 2024) states the target as a range in two places --- p10 ("43-50 GW of offshore wind ... in 2030") and p74 ("This will need to rise to 43-50 GW in 2030"), where it is labelled the "DESNZ Clean Power Capacity Range". The DESNZ CfD reform consultation (21 February 2025) restates the same 43--50 GW range. The government has not published a point target. Scoring against a single 50 GW figure would misrepresent the source by inventing a precision the commitment does not contain; scoring against 43 alone would understate stated ambition. A range is the honest treatment.

**Departure from rubric §4:** rubric-v0.1 §4 refers to "the 2030 target" in the singular and the gap-closure method in §2 assumes a single target value. v0.6 generalises this to permit a target *range* where the source publishes one. The scoring method is unchanged --- gap-closure projection is simply run twice, once per endpoint. Where a metric has a genuine point target (as constraint costs would, were it scored), the singular form still applies. This is the first metric to use a range; the generalisation is logged here rather than folded silently into §4.

**Output:** `delivery_ratio` and `slip_year` are objects with `low`/`high` keys. Against Q1 2026 data: 40.2% (vs 43 GW) / 34.5% (vs 50 GW); both red. Projected 2030 capacity is target-independent (17.27 GW) and stored once.

**Citation discipline:** the target source string cites CP2030 p10 & p74 directly (document verified 4 June 2026), with the CfD consultation as corroborating reference. The press release's "30.7 GW installed or committed" progress figure is explicitly NOT used --- it is pipeline-inclusive and would contradict the operational-only rule (ADR-001 d8).

#### M-18. Trailing-window anchor: fixed clean quarter-end

The trailing-12-month window and the "as of" date are anchored to a fixed quarter-end (REPD Q1 2026 = 31 March 2026), not derived from the maximum `Record Last Updated` value in the CSV.

**Reasoning:** Matches the constraint-costs decision to anchor on a clean FY boundary (ADR-002 d2, v0.2 M-5) rather than a sliding data-currency date. Fixed anchor is reproducible and citable; a reader can verify the window. Trade-off: the figure can go stale between quarterly REPD publications --- handled by the staleness warning (v0.5 M-16, >4 months old).

#### M-19. Sparkline shows full commissioning history, not trailing 2--3 years

The offshore wind quarterly-additions sparkline shows the full commissioning record (37 quarters, 2000--2025), not the trailing 2--3 years specified in rubric §5.

**Reasoning:** §5's purpose is to expose lumpiness the trailing-12-month figure hides. For offshore wind specifically, the lumpiness only becomes legible across the full record: the 2024 commissioning gap (zero quarters between 2023-Q4 and 2025-Q3) and the 2022 wave (3.1 GW across three quarters) are what make the current trough readable as a trough rather than a collapse. Truncating to 3 years would remove the context that justifies reading the red light as window-sensitive. This is a deliberate per-metric deviation from §5's literal window, consistent with §5's intent. Matches the full-history treatment already used on the constraint-costs sparkline (9 FYs).

### Output shape (offshore wind headline.json)

Scored-card shape, distinct from the constraint-costs context-card shape: adds `traffic_light`, `delivery_ratio`, `slip_year`, `projected_2030_gw`, `target`, `pipeline_gw`, `single_project_sensitivity`. `card_type` is `"scored"` (vs `"context"`).

### Items that do NOT change

-   Rubric thresholds (green ≥100%, amber 60--99%, red <60%) --- unchanged. Offshore wind is red at both range endpoints.
-   Operational-only capacity definition (ADR-001 d8) --- unchanged. Scored on status == 'Operational' (15.13 GW); pipeline shown contextually only.
-   Trailing 12-month build rate as scoring input (rubric §2) --- unchanged.
-   Single-project sensitivity flag at >60% (rubric §5) --- unchanged; fires here (Neart na Gaoithe, 100%).
-   v0.5 card-design decisions (M-12 pipeline bar, M-13 sparkline retained, M-14 CfD split deferred, M-15 REPD lag/Dogger Bank, M-16 manual quarterly source) --- unchanged.

### Review trigger for v0.6

Re-examined at week 10 ship/shelve. Specific questions:

-   Did range-scoring read clearly on the card, or did two ratios/two slip years confuse readers vs a single figure?
-   Did the full-history sparkline (§5 deviation) help readers see the trough-not-collapse story, or just look noisy?
-   Did the fixed quarter-end anchor cause a stale figure that the staleness warning failed to catch?
-   Should rubric §4 be formally rewritten to accommodate ranges at the v1 review, rather than carrying the generalisation only in this changelog entry?