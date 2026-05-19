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

---

## v0.3 — 5 May 2026 — Schema validation: type equivalence rule

**Trigger:** First production run of the constraint costs scraper (5 May 2026) failed validation against the 2019-20 resource. Root cause was not a real schema breakage but per-resource variation in CKAN's `type` metadata: the 2017-18 and 2018-19 resources type the `Date` column as `timestamp`, while 2019-20 onwards type it as `date`. Same column, same unit, same value shape. The original validation rule in `ADR-002` decision 7 treated this as drift and hard-failed; this entry refines the definition of drift.

### Changes

#### M-6. CKAN type equivalence rule

The schema validation rule introduced in `ADR-002` decision 7 is refined as follows. Two field types are treated as **equivalent** for validation purposes if they are documented in the equivalence table below. Any drift between equivalent types is not flagged.

Initial equivalence table:

| Class | Equivalent CKAN types |
|-------|----------------------|
| Date-like | `date`, `timestamp` |

Additions to this table require a methodology changelog entry. The equivalence table lives in the scraper source (`data/scrapers/scrape.py`, `TYPE_EQUIVALENCE` constant) and is referenced from this changelog as the methodology source of truth.

**What still counts as drift (unchanged):**

- A column being added, removed, or renamed.
- A column's `unit` changing.
- A column's `type` changing to one outside its current equivalence class (e.g. `numeric` → `text`).
- A change in the number of fields.

**Reasoning:**

- The discovery work supporting `ADR-002` sampled only two FY resources (2024-25 and 2026-27). Both happened to use `date` for the Date column. The variation in older resources was not visible at the time the validation rule was written.
- The values returned in the records are JSON-typed (string for both `date` and `timestamp` cases, parsed by downstream code), so there is no operational impact from the type variation. Treating it as drift would block the scraper without a real underlying problem.
- Throwing the type check away entirely (which was the alternative considered) would lose the ability to catch genuine type changes — e.g. a column being re-typed from numeric to string. The equivalence-class approach keeps that signal while accommodating known-benign variation.

**Operational cleanup:** The schema reference file at `data/state/constraint-costs-schema.json` was frozen from the first resource fetched (2017-18) during the failed run, capturing the minority `timestamp` typing. The file must be deleted before the next scraper run so it is re-frozen against any of the 10 resources — the equivalence rule means whichever one freezes first no longer matters.

#### Implications

- `ADR-002` decision 7's text continues to read "validates the field schema against a frozen reference on every fetch." This remains accurate; the equivalence rule is a refinement of *what counts as a match*, not a removal of validation.
- The schema reference file format is unchanged.
- The cross-FY consistency alternative (Option C in the 5 May 2026 chat) was considered and not adopted; revisit at week 10 review if the equivalence-table approach is found insufficient.

### Items deferred

- No additional equivalence classes are added pre-emptively. The current table contains only the one observed case. If further per-resource type variation appears, each addition will be a discrete changelog entry with the observed evidence.

### Items that do NOT change

- The thresholds, three-tracker architecture, opportunities rubric, and major projects tracker are all unchanged. v0.3 is a refinement to the data-acquisition validation layer only.
- The constraint costs methodology choices in v0.2 (M-1 through M-5) are unchanged.

### Review trigger for v0.3

Re-examined at week 10 ship/shelve decision alongside the rest of the rubric and `ADR-002`. Specific questions:

- Did the equivalence table need extending during the build? If so, what was added?
- Did the equivalence rule ever cause a real schema breakage to slip through (false negative)?
- Did `ADR-002` decision 7's text need updating to reference the equivalence rule explicitly?
