# ADR-001: Rubric design for Net Zero Dashboard POC

**Status:** Accepted
**Date:** 4 May 2026
**Decision-maker:** Project owner (solo build)
**Related:** `rubric-v0.1.md`, `net-zero-dashboard-plan.md`

---

## Context

The dashboard scores UK net zero infrastructure progress against published targets using traffic lights. The original plan flagged that traffic lights without a defined methodology were the single biggest weakness of the example output that prompted this project. Before any code is written, the rubric needs to be defensible to expert readers (CCC analysts, RenewableUK staff, National Grid people) while remaining legible to non-experts in 30 seconds.

This ADR captures the reasoning behind the rubric decisions made in v0.1, so that future revisions and reviewers can see *why* each choice was made rather than just *what* was chosen.

---

## Decisions

### 1. Gap-closure projection, not build-rate ratio

**Decision:** Score each infrastructure metric by projecting current trailing 12-month build rate forward to 2030, comparing projected delivery to target, and lighting the card based on the resulting delivery ratio.

**Alternative considered:** Build-rate ratio — current rate ÷ required rate.

**Why gap-closure won:**
- Answers the question the reader actually wants answered: "at this rate, will we get there?"
- Output is a percentage of target delivered, which is more intuitive than "you're at 73% of the required pace."
- Slightly more computation but the same inputs, so no real cost.

**Trade-off accepted:** Linear extrapolation is a simplification. Build rates accelerate as supply chains mature, so early-years lag against linear isn't necessarily fatal. Mitigated by showing underlying numbers alongside the light, and by surfacing slip view (see decision 3).

### 2. Thresholds: green ≥100%, amber 60–100%, red <60%

**Decision:** Green requires projected delivery to meet or exceed target. Amber covers 60–100%. Red is below 60%.

**Why 100% for green:** These are large, long-lead programmes. A 5% projected shortfall in mid-build is "narrowly missing," not "on track." Given typical ramp-up uncertainty, narrowly missing usually means properly missing. Green should mean on or ahead of pace, not "close enough."

**Why 60% for the red/amber cut:** Below 60%, catch-up requires more than doubling current build rate — step-change territory requiring external intervention (policy, supply chain, capital), not trend continuation. This matches the project owner's intuition ("impossible without exponential growth") and provides a defensible computational floor.

**Trade-off accepted:** Threshold not pressure-tested against real data yet. Will revisit at week 3 when the first metric pipeline is up and a real delivery ratio can be computed. If everything ends up red, the threshold isn't doing useful discrimination and we'll re-tune.

### 3. Slip view, not 2040 targets

**Decision:** A secondary view answers "at the current build rate, when do we actually hit the 2030 target?" — expressed as a year, not a colour.

**Alternative considered:** Toggle to a 2040 target.

**Why slip view won:**
- The UK has no formal 2040 commitments for most of these metrics. Inventing 2040 targets would create a credibility problem.
- The slip view uses the same arithmetic, rearranged. No new targets needed, no FES pathway argument.
- For amber/red metrics, a year is more informative than a colour. "50 GW solar arrives in 2037 at current pace" tells the reader more than "amber against 2030."
- Side-steps the FES central-vs-high-vs-low pathway dispute entirely.

**Trade-off accepted:** Slip view doesn't have an obvious traffic-light analogue, so it's a different visual treatment from the headline view. Manageable.

### 4. Three-tracker architecture

**Decision:** Dashboard contains three structurally distinct trackers — infrastructure (delivery ratio), opportunities (qualitative policy status), major projects (lifecycle status, no scoring) — presented separately with distinct visual treatment.

**Alternative considered:** Force everything into one rubric, or drop the things that don't fit.

**Why three trackers won:**
- Each evidence type genuinely requires different scoring logic. Forcing them into one rubric would either dumb down the infrastructure scoring or fake quantitative rigour for the qualitative content.
- Dropping opportunities and transmission was considered (and was the original plan's recommendation for POC) but project owner judged that grid connections without transmission, and infrastructure without policy context, would be tracking the wrong thing.

**Trade-off accepted:** Three different evidence types on one page increases cognitive load on readers. Mitigated by visual separation, methodology page work, and explicit reader instruction not to aggregate across trackers. This is now a real design problem to solve in weeks 6–7, not a styling one.

### 5. Transmission as project-level status, not scored

**Decision:** Major transmission projects (NESO Beyond 2030 list) tracked individually with lifecycle status (planned / consented / in construction / operational) plus a "delayed" flag. No aggregate score.

**Alternative considered:** Either drop transmission entirely (with strong methodology caveat), or compute a delivery ratio against an aggregate GW or project-count target.

**Why project-level status won:**
- A delivery ratio for transmission would require either aggregating GW across heterogeneous projects (obscures reality) or picking a target that doesn't exist in any government commitment (invents a rubric the data can't support).
- Dropping transmission entirely was the largest credibility risk in the POC — the connections queue is meaningless if the underlying network reinforcement isn't being built.
- Project-level status is honest: here are the named projects, here's where each one is, here's whether their published dates have slipped.

**Trade-off accepted:** "Delayed" flag requires storing historical milestone dates so slippage can be detected against previously published commitments. This is a feature to build deliberately; it doesn't fall out of the data automatically.

**Project list is itself editorialising:** Mitigated by using NESO Beyond 2030 as the inclusion rule. If a project isn't on Beyond 2030, it doesn't go in the tracker. Saves "why isn't X included" arguments.

### 6. REMA / zonal pricing as single POC opportunity

**Decision:** Track one opportunity at POC (REMA / zonal pricing) to prove the pattern. Industrial co-location and energy export deferred until post-POC review.

**Why REMA:**
- Live and active — REMA decision late 2025, ongoing workstreams. Dated documents exist.
- Directly relevant to where infrastructure gets built. Tells a coherent story alongside the infrastructure cards.
- Industrial co-location is news monitoring more than tracking — too qualitative for a first proof.
- Energy export splits across interconnectors and hydrogen — would need its own scoping.

**Trade-off accepted:** One opportunity is a small sample to test whether the opportunities rubric works. If REMA tracks well at POC, the pattern scales. If it doesn't, we learn that on one metric rather than three.

### 7. Lumpiness handled visually, not in the rubric

**Decision:** Trailing 12-month figure remains the headline rate for all metrics. Lumpiness (single large project commissioning) is exposed via a quarterly-additions sparkline on each card, not by changing the scoring window.

**Alternative considered:** Different windows for lumpy sectors (e.g. quarterly for battery, annual for solar).

**Why visual won:**
- Quarterly windows amplify lumpiness rather than expose it — a single big project makes one quarter look spectacular and three look dead.
- Different windows per metric makes the rubric inconsistent and harder to defend.
- Sparkline shows the truth directly; reader sees the lumpiness without the rubric making editorial calls about it.

**Additional mitigation:** Cards flag "single-project sensitivity" when one project dominates >60% of the trailing 12-month additions.

### 8. Operational capacity only

**Decision:** "Current capacity" means installed and operational. Excludes consented, under construction, and connection-queue capacity.

**Why:** The dashboard exists to reflect what's actually delivering, not political ambition. Including pipeline capacity would let a reader conclude progress is on track when actual delivery is lagging.

**Trade-off accepted:** None of consequence. Pipeline data is useful context but belongs in supporting visualisation, not in the headline figure.

### 9. Targets: government where committed, NESO central pathway where not, labelled per card

**Decision:** Each metric's reference target is the latest official government commitment if one exists. Where no government target exists, NESO central FES pathway is used. The methodology note on each card states which applies and cites the source.

**Why mixed:**
- Government targets carry political weight and are what the country is publicly committed to — the dashboard should score against these where they exist.
- For metrics without committed targets (battery storage notably), NESO central pathway is the most defensible technical reference.
- Mixing is honest as long as it's labelled. Picking only one source would either ignore real commitments or invent commitments that don't exist.

**Trade-off accepted:** Targets will get revised by government over time. Methodology versioning baked in from the start: if a target changes, a new methodology version is committed and the card flags "methodology updated."

### 10. Decimal years remaining, not integer

**Decision:** "Years remaining" computed as decimal years from the most recent data point to 31 December 2030.

**Why:** Integer years create cliff effects — required rate jumps when the integer ticks down. Decimal is mathematically cleaner.

**Trade-off accepted:** Technically the rubric value shifts continuously, but in practice it's only recomputed when underlying data refreshes (monthly at fastest). Week-to-week noise is a non-issue.

### 11. No aggregate "net zero score"

**Decision:** Each metric stands alone. There is no headline number that combines them.

**Why:** A single aggregate score would require weighting metrics by importance — an editorial judgement that opens significant credibility risk. It's also exactly the kind of feature that would get the dashboard mocked by experts.

**Trade-off accepted:** Less shareable in headlines and social media. Acceptable cost for credibility.

### 12. No retirements in POC

**Decision:** Track gross operational capacity. Retirements ignored at POC.

**Why:** For battery and solar, retirements are immaterial. For onshore wind, some early-2000s farms are reaching end-of-life — material enough to revisit at v2 but not at POC.

**Trade-off accepted:** Slight overstatement of progress. Disclosed on methodology page.

---

## Consequences

**Good:**
- The rubric is defensible to expert readers. Each scoring choice has a stated reason and a stated trade-off.
- Three-tracker architecture honestly represents three different evidence types rather than faking parity.
- Methodology versioning protects against silent drift when targets change.

**Bad / costly:**
- Three trackers means more design work in weeks 6–7. Cognitive load on readers is higher than single-rubric alternatives.
- 60% threshold is not yet pressure-tested. Genuinely possible the rubric needs re-tuning at week 3.
- "Delayed" flag for transmission requires deliberate historical date tracking — a real feature to build, not a free output.
- 10-week timeline is now tight. Design pass compression assumed; further slippage may require deadline extension.

**Reversible vs irreversible:**
- All threshold values are reversible — tuning them is cheap.
- Three-tracker architecture is reversible but expensive (visual treatment, methodology page restructuring).
- Operational-only capacity definition is reversible but would invalidate historical data — would require methodology version bump.

---

## Review trigger

Post-POC review (week 10 ship/shelve decision) will revisit this ADR alongside the rubric. External reviewers have agreed to a second round of feedback at that point. Specific items to re-examine:

- Did the 60% red/amber threshold do useful discrimination, or did everything end up the same colour?
- Did the three-tracker architecture confuse readers or did the visual separation work?
- Did the REMA opportunity tracking pattern work well enough to scale to industrial co-location and energy export?
- Did the "Delayed" flag for transmission projects get correctly populated, or did historical date tracking fail in practice?
