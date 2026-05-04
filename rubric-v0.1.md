# Net Zero Dashboard — Rubric v0.1 (DRAFT)

**Status:** First draft, pre-external-review.
**Scope:** Three trackers, deliberately distinct:
- **Infrastructure tracker** (rubric in §2–§9): operational capacity scored against 2030 targets via gap-closure projection.
- **Opportunities tracker** (rubric in §10): policy status of regulatory enablers.
- **Major projects tracker** (rubric in §11): status of named transmission projects, no scoring.

Each tracker uses a different evidence type and is presented separately on the dashboard. Readers are explicitly told not to aggregate across them.
**Last updated:** 4 May 2026.

---

## 1. What we're scoring

For each infrastructure metric, the rubric answers one question:

> **At the current build rate, will we hit the 2030 target?**

We don't score absolute capacity. We don't score year-on-year change. We score the projected outcome at the deadline against the committed (or referenced) figure for that deadline.

## 2. The scoring method — gap-closure projection

For each metric:

1. Take the trailing 12 months of additions (operational capacity only — not consented, not under construction).
2. Take the gap between current operational capacity and the 2030 target.
3. Take the years remaining until end of 2030.
4. Project: `projected 2030 capacity = current capacity + (trailing 12-month rate × years remaining)`.
5. Score: `projected 2030 capacity ÷ 2030 target = delivery ratio`.

The delivery ratio determines the traffic light.

## 3. Thresholds

| Light | Delivery ratio | Plain English |
|-------|---------------|---------------|
| 🟢 Green | ≥ 100% | At current pace, target is met or exceeded. |
| 🟡 Amber | 60% – <100% | At current pace, target is missed but significant progress is made. |
| 🔴 Red | < 60% | At current pace, target is missed badly. Recovery would need a step-change in build rate. |
| ⚫ Grey | n/a | Insufficient or disputed data; see methodology note on the card. |

**Why 100% for green:** these are large, long-lead infrastructure programmes. A 5% projected shortfall is not "on track" — it's narrowly missing, and given typical ramp-up uncertainty, narrowly missing usually means properly missing. Green requires being on or ahead of pace.

**Why 60% for amber/red:** below 60% delivery, the catch-up requires more than doubling current build rate for the remaining years. That's the "step-change" territory — not impossible, but it requires an external intervention (policy, supply chain, capital), not just continuation of trend.

**Overshoot:** there is no separate "well ahead" category. If projected delivery exceeds 100%, the light is green. If a metric ever projects above 150% we'll revisit; for now, no metric is plausibly in that range.

## 4. Inputs and definitions

**Current capacity.** Installed and operational only. Excludes consented, under construction, and connection-queue capacity. The dashboard exists to reflect what's actually delivering, not political ambition. Where a source reports a mix, we filter to operational status before scoring.

**Trailing 12 months.** The 12 months ending at the most recent reliable data point from the primary source. Not calendar year. Not financial year. The window slides as new data lands.

**Years remaining.** Decimal years from the most recent data point to 31 December 2030. As of May 2026, that's roughly 4.6 years; by end of POC build it'll be ~3.5. The decimal value shifts continuously as time passes, but in practice the rubric is recomputed only when underlying data refreshes — monthly at fastest, quarterly for several metrics. Week-to-week noise is therefore a non-issue.

**2030 target.** Government commitment where one exists. NESO central FES pathway where not. The source for each metric's target is listed in the per-metric methodology and cited on the card. Targets are versioned in the repo — if a number changes, we commit a new version with date and justification, and the card flags "methodology updated."

## 5. Lumpiness — handled visually, not in the rubric

Battery storage and offshore wind in particular deliver in lumpy chunks (a 1.6 GW farm commissioning in one quarter). The trailing 12-month figure smooths this, which is correct for the rubric (you don't want a single quiet quarter to flip the light), but it hides reality from the reader.

Mitigation: every metric card shows a sparkline of quarterly additions for the trailing 2–3 years alongside the headline rate. The reader sees the lumpiness directly. The rubric stays consistent across metrics.

If a metric's trailing 12-month figure is dominated by a single project (>60% of the period's additions), the card additionally flags "single-project sensitivity" in the methodology note.

## 6. The 2030 view and the slip view

The default view scores against the 2030 target as described above.

A secondary **slip view** answers a different question:

> **At the current build rate, when do we actually hit the 2030 target?**

Same arithmetic, rearranged: `slip year = current year + (gap to target ÷ trailing 12-month rate)`.

This is shown as a year, not a colour. It exists because for amber/red metrics it's more informative than the traffic light alone — "50 GW solar arrives in 2037 at current pace" tells the reader more than "amber."

The slip view is explicitly **not** a 2040 target. The UK has no formal 2040 commitments for most of these metrics; framing it that way would invent a commitment that doesn't exist. The slip view is a projection of the 2030 target, deferred.

## 7. Disputed or insufficient data — going grey

Grey is a judgement call by the maintainer (currently: me, solo). It applies when:

- A primary source has not refreshed within 2× expected cadence and no fallback is producing reliable data, or
- The methodology for a metric is under active revision (e.g. target has been revised by government and we haven't yet updated our reference), or
- There's an unresolved definitional dispute (e.g. how to count co-located battery + solar).

The methodology note on each grey card discloses which of these applies and what the next refresh attempt looks like. There is no automated trigger; grey is a deliberate, owned editorial decision.

## 8. Versioning

This rubric is v0.1. Changes get a version bump and a dated entry in `methodology-changelog.md`. The dashboard footer shows the active rubric version.

The rubric will be **frozen for the POC** after one external sanity-check round and one revision. Material changes during the 10-week build will be resisted; cosmetic clarifications are fine.

Annual review thereafter, calendared.

## 9. Things this rubric deliberately doesn't do

- It doesn't model supply chain ramp-up or learning curves. Linear projection is a simplification; it's also the most defensible thing to do without inventing a forecasting model.
- It doesn't weight metrics. A red on grid transmission and a red on solar both look the same on the dashboard, even if one is a bigger problem for net zero overall. Weighting opens an editorial can of worms; we don't open it.
- It doesn't aggregate to a single "net zero score." Each metric stands alone. There is no headline number.
- It doesn't account for retirements. We track gross operational capacity; for the POC, retirements are small enough to ignore. Revisit at v2 if it becomes material (notably for older onshore wind).

---

## 10. Opportunities rubric

The opportunities section tracks **policy proposals**, not infrastructure. It is structurally different from the infrastructure tracker and is presented separately on the dashboard with distinct visual treatment. The methodology page makes the difference in evidence type explicit so a reader doesn't conflate "amber on battery storage" (a measured shortfall against a numerical target) with "amber on zonal pricing" (a qualitative status of an active consultation).

### What we're scoring

> **What is the live policy status of this opportunity, against the option of having it implemented?**

We are not scoring whether the policy *should* be implemented — that's editorial. We're scoring whether the regulatory machinery to enable it exists, is being actively developed, or is absent.

### Thresholds

| Light | Meaning |
|-------|---------|
| 🟢 Green | Implemented in regulation or primary legislation, with operational mechanism in place. |
| 🟡 Amber | Active formal consultation, pilot, or government commitment with published timeline. Not yet operational. |
| 🔴 Red | No active policy development. Discussion only, or stalled after consultation closure with no follow-through. |
| ⚫ Grey | Disputed scope, conflicting government signals, or in transition between defined states. |

### Why these thresholds

The infrastructure rubric has a defensible numerical floor for each light. The opportunities rubric does not — these are judgement calls and the methodology must own that.

What protects the rubric from drifting into editorial:

- **The light scores process status, not desirability.** A reader may think zonal pricing is a terrible idea and still agree with an "amber" call if a consultation is genuinely live.
- **Each card cites the documents.** Specific consultation references, dated commitments, named regulations. No light without a citation.
- **The rubric does not weight opportunities by importance.** A green on a minor regulatory tweak and a green on a major market reform look the same on the card. We don't editorialise via colour intensity.

### Refresh cadence

Opportunities don't have monthly data. Refresh is event-driven — when a consultation opens, closes, or a regulation is laid. Methodology note on each card lists the documents being watched and the next expected event with a date if known.

If no event has occurred in 6 months and the status hasn't changed, the card is still considered current. We don't flag staleness for opportunities the way we do for infrastructure (where staleness implies a broken pipeline). For opportunities, no news is news.

### POC scope

One opportunity tracked at POC: **REMA / zonal pricing**. Selected because it has dated documents (REMA decision late 2025, ongoing workstreams), is directly relevant to where infrastructure gets built, and is concrete enough to test the rubric pattern. If the pattern works for REMA, additional opportunities (industrial co-location, energy export) get added post-POC using the same rubric.

### Things this rubric deliberately doesn't do

- It doesn't predict whether a policy will be implemented. "Amber" is a description of current state, not a forecast.
- It doesn't grade policy design quality. A badly-designed regulation that has been laid is still 🟢.
- It doesn't claim parity with the infrastructure rubric. The two sections answer different questions and a reader should not aggregate them.

---

## 11. Major projects tracker (transmission)

Transmission infrastructure does not fit either rubric above. There is no clean monthly capacity dataset to score against a 2030 target, and it's not a policy proposal. Instead, we track the named major transmission projects individually, with status only — no scoring, no traffic light against a delivery ratio.

This is included because connections queue progress is meaningless if the underlying network reinforcement isn't being built. Tracking only the queue would let a reader conclude "grid is fine" when the physical wires required to honour those connection dates may be slipping. Major projects tracking closes that gap, honestly, without inventing a rubric the data can't support.

### What we're scoring

> **Where is each named transmission project in its delivery lifecycle?**

We track each project against a defined set of milestones, not against a numerical target.

### Project statuses

| Status | Meaning |
|--------|---------|
| Planned | Project announced, route options under development, pre-consent. |
| Consented | Development consent order granted (or equivalent for Scotland). |
| In construction | Physical works started. |
| Operational | Energised and carrying load. |
| Delayed | Most recent published milestone date has slipped from a previously published date. Persists until the project advances to the next status. |

"Delayed" is a flag layered on the other statuses, not a replacement — a project can be "in construction, delayed" or "consented, delayed." This keeps the lifecycle status visible while surfacing slippage.

### Projects in scope for POC

The major transmission projects identified in the NESO Beyond 2030 plan and the National Grid Great Grid Upgrade. Initial list to be finalised in week 1 alongside source registry; expected to include:

- Eastern Green Link 1, 2, 3, 4
- Norwich to Tilbury
- North Wales upgrade
- Scotland-England HVDC links

The list is itself versioned — adding or removing a project requires a methodology changelog entry.

### Why no scoring

A delivery ratio for transmission would require either (a) aggregating GW across heterogeneous project types, which obscures the underlying reality, or (b) picking a target (e.g. "X projects operational by 2030") that doesn't exist in any government commitment. Either approach invents a rubric the data doesn't support. Project-level status tracking is the most honest treatment available given the evidence.

### Refresh cadence

Quarterly manual update from National Grid project pages and NESO publications. The methodology note on the section flags this as the lowest-cadence tracker on the dashboard.

### Things this tracker deliberately doesn't do

- It doesn't score the projects collectively. There is no "transmission overall" light.
- It doesn't predict completion dates. We surface the published milestone dates and flag slippage; we don't model whether published dates are realistic.
- It doesn't cover distribution network upgrades. Distribution is a separate problem with separate data and is out of POC scope.
