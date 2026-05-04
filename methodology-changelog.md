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
