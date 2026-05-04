# ADR-002: Data acquisition design for constraint costs

**Status:** Accepted
**Date:** 4 May 2026
**Decision-maker:** Project owner (solo build)
**Related:** `ADR-001-rubric-design.md`, `rubric-v0.1.md`, `net-zero-dashboard-plan.md`
**Affected metric(s):** Constraint costs (POC pilot metric). Pattern intended to inform — not bind — subsequent CKAN-based metrics.

---

## Context

Constraint costs is the POC pilot metric. It was selected as the first end-to-end slice on the assumption that NESO's "Constraint Breakdown Costs and Volume" dataset was the cleanest data path on the dashboard.

A discovery pass against the NESO data portal (early May 2026) confirmed the data is clean in delivery (single CSV per FY, well-typed CKAN datastore, machine-readable field metadata) but introduced four design questions that needed resolving before writing a production scraper:

1. The dataset is split per UK financial year, not as a single rolling file. How should the scraper handle multi-FY windows?
2. NESO updates not only the current FY file but also previous FYs after they have closed. How aggressively should the scraper re-fetch?
3. NESO's API is at `api.neso.energy`, not `www.neso.energy` (the original plan implied otherwise). What does the source registry record?
4. The dataset contains four cost categories and four volume categories. The card has chosen to publish thermal constraint cost only. How does the data layer represent this?

This ADR captures those decisions and their reasoning. Methodology choices (what gets *shown* on the card) are out of scope and tracked separately.

---

## Decisions

### 1. FY-aligned files, splicer in the data layer

**Decision:** The scraper fetches per-FY CSVs. A separate splicer concatenates and slices into whatever window the dashboard renders. Fetch and slice are distinct steps with a stable intermediate (a unioned long-format dataset, sorted by date).

**Alternative considered:** Fetch and concatenate in one pass; render directly from the result.

**Why split:**
- Different cards may want different windows (latest complete FY for the headline, trailing 12 months for a sparkline, all-time for context). Doing the slicing once at fetch time bakes a choice into the cache that we may not want to bake in.
- Splicer is testable in isolation. A bug in date handling shouldn't require re-hitting the API.
- The intermediate (union of all FYs) is small enough that caching it costs nothing.

**Trade-off accepted:** One extra processing step. Marginal complexity for the POC; pays off the moment we want a second view from the same data.

### 2. Headline window: latest complete UK FY

**Decision:** The headline figure is the sum of `Thermal constraints cost` over the most recent UK financial year that has fully closed (April → March). As of May 2026, that's FY 2025-26.

**Alternative considered:** Trailing 12 months (sliding window).

**Why latest-complete-FY won:**
- It's what most published commentary uses; readers don't have to mentally translate.
- "Last FY" is unambiguous; "trailing 12 months" requires the reader to know the end date.
- Splicing across FY boundaries for a sliding window is a real engineering chore at POC stage and not worth the complexity for the headline view.
- Trailing 12 months remains valuable as a *secondary* view (e.g. "still in progress" indicator). Deferring it does not foreclose adding it later — the FY-aligned splicer makes adding a sliding window straightforward.

**Trade-off accepted:** The headline goes stale for up to a few weeks each April while the just-closed FY is still being revised by NESO (see decision 3). Mitigation: the card shows the FY label clearly (e.g. "FY 2025-26") and a "data through" date stamp. A reader can see the figure is from a complete window, not a partial one.

### 3. Re-fetch all FYs whose `last_modified` has changed

**Decision:** On every scheduled run, the scraper calls `package_show` on the parent dataset, compares each resource's `last_modified` timestamp to its cached value, and re-fetches any resource whose timestamp has advanced.

**Alternatives considered:**
- Re-fetch current FY only (trust prior FYs as immutable).
- Re-fetch current FY + previous FY only.
- Re-fetch every FY every run.

**Why timestamp-based won:**
- NESO's package notes explicitly state that historical data may be revised when action tags change post-event. Direct quote from the package: *"Please note that tags applied to actions can occasionally be changed post event and in this instance the information in this dataset would be refreshed to reflect the up to date information."*
- Observed evidence: the FY 2019-20 file was last modified in March 2024 (~4 years after the FY closed), and the FY 2024-25 file was last modified in June 2025 (over 2 months after that FY closed). n=small, but consistent with the package note.
- "Trust prior FYs as immutable" therefore creates a real risk of the dashboard showing figures NESO no longer publishes.
- "Refetch everything every run" works but wastes bandwidth (10 FYs and counting) and offers no advantage over the timestamp check.
- The CKAN API gives us `last_modified` per resource for free in a single `package_show` call. The check itself is cheap.

**Trade-off accepted:** The scraper has to maintain a small state file (one timestamp per resource_id). This is now a real artefact in the repo, versioned alongside the data. Documented in the source registry.

### 4. Source registry treats NESO as a CKAN source, not a URL list

**Decision:** The source registry entry for constraint costs records: the API base URL (`https://api.neso.energy/api/3/action`), the parent package_id (`fb56b46e-cef3-4eb8-9294-0ca19769b7eb`), the field schema reference, the active resource_ids per FY, and the last-known `last_modified` per resource. It does not hardcode CSV URLs.

**Alternative considered:** A flat list of CSV download URLs, one per FY, refreshed manually each year.

**Why CKAN-first won:**
- New FY resources appear automatically each April (observed: 2025-26 created 2025-04-04; 2026-27 created 2026-04-07). A package-walk discovers them; a hardcoded URL list does not.
- The CKAN field metadata is the data dictionary. Validating against it on every fetch is the basis for the validation-on-fetch rule from plan §4.
- If NESO changes their CDN URL pattern, the package_show response gives us the new URL automatically. Hardcoded URLs would silently break.

**Trade-off accepted:** This decision is specific to CKAN sources. Other source types (BEIS REPD, RenewableUK PDFs, National Grid project pages) will need their own registry shapes. The registry schema therefore needs a `source_type` discriminator from day one. Flagged for the source registry design — not in scope for this ADR.

### 5. Empty / zero-only columns are kept in the pipeline, surfaced in methodology

**Decision:** All eight measurement columns are fetched and stored, including `Reducing largest loss cost`, `Increasing system inertia cost`, and the corresponding volume columns, which are observed to be zero across all current data. They are not filtered or hidden at the data layer. The card publishes thermal constraint cost only; methodology discloses that the other categories exist and are typically zero in current data.

**Alternative considered:** Drop columns we don't intend to publish.

**Why keep:**
- A reader downloading the underlying CSV will see all eight columns. Hiding them at the data layer would create a discrepancy between what we store and what NESO publishes.
- If "Reducing largest loss cost" becomes non-zero in future (e.g. a low-inertia event triggers RoCoF actions), our pipeline already handles it; otherwise we'd silently drop a real signal.
- The methodology page is the right place to explain why three of the four categories are typically zero, not the data layer.

**Trade-off accepted:** Slightly larger stored dataset; trivial in practice.

### 6. Volume columns are stored but not published at POC

**Decision:** Volume columns are fetched and stored but are not surfaced on the card or in the methodology beyond a footnote acknowledging the fields exist. The negative values observed in `Thermal constraints volume` reflect a sign convention that is not documented in the field metadata; until that convention is understood, publishing the column risks misrepresentation.

**Alternative considered:** Publish volume alongside cost on the card; flag the sign convention with a caveat.

**Why hold:**
- Sign convention undocumented = methodology risk. Plan §1 success criterion 3 ("an expert reader could read the methodology page and not laugh") is the binding constraint here.
- POC scope is constraint *costs*; volumes are useful future context but not required for the card to ship.
- Storing them now means we can publish later without re-fetching once we understand them.

**Trade-off accepted:** A reader who sees the underlying data may notice volume columns exist and ask why they're not on the card. The methodology footnote handles that case.

### 7. Treat NESO API as moderately stable; validate on every fetch

**Decision:** The scraper validates the field schema against a frozen reference on every fetch. Any drift (renamed column, new column, removed column, type change) triggers a hard failure and an alert; the existing cached data is preserved.

**Why:**
- The schema-stability check showed identical schemas across the FYs we sampled (2024-25 and 2026-27). Plus n=1 across the package's 10-year span we didn't sample. We have moderate confidence the schema is stable, not high confidence.
- Plan §4 mitigation 2 is "validation on fetch." This decision is the local instantiation of that rule.
- Hard failure rather than silent fallback is consistent with plan §4 mitigation 3 ("notifications, not auto-recovery").

**Trade-off accepted:** Manual intervention required when NESO changes the schema. Acceptable given the alternative is silent drift.

---

## Consequences

**Good:**
- Mutable-history risk is handled correctly without polling more than necessary.
- The data layer is clean enough that a second card (different window, different category) costs almost nothing to add.
- The CKAN-first source registry shape works for any other CKAN source we add later (e.g. NESO TEC register).

**Bad / costly:**
- Maintaining `last_modified` state is now a small but real piece of infrastructure. State file goes in the repo, versioned, alongside the data. Failure mode: state file gets out of sync with NESO and we re-fetch unnecessarily — annoying, not broken.
- The data layer carries fields we don't publish (zero-valued cost columns, volumes). Defensible but wider than strictly needed.
- Eight FYs of historical data is a real archive (FY 2024-25 has 365 rows; full history is ~3,300 rows so far). Trivial in absolute terms but worth noting that "total dataset size" grows by a year of daily rows every April.

**Reversible vs irreversible:**
- All decisions in this ADR are reversible. The data layer can be rebuilt from NESO at any point.
- The state file is the only piece of locally-authoritative state, and it's regenerable if lost (just refetches everything once).

---

## Out of scope for this ADR

The following decisions were touched on in the discovery work but belong in other documents:

- **What gets shown on the card** (headline = thermal cost only; no traffic light; "what this means" panel pending). These are methodology choices, not data acquisition. They should land in `methodology-changelog.md` as the next versioned entry, alongside their reasoning.
- **The "what this means" explainer copy.** Pending — explicitly deferred until the card has been rendered.
- **The thermal-cost-≠-curtailment-payments framing.** Methodology, not data. Will be addressed when the explainer is drafted.
- **Source registry schema for non-CKAN sources** (PDFs, HTML pages). Will be addressed when a non-CKAN source is implemented; over-designing the registry now would be premature.

---

## Review trigger

Re-read alongside ADR-001 at the week 10 ship/shelve decision. Specific items to re-examine:

- Did the FY-aligned splicer pay off (i.e. did we actually add a second view that used it), or did it stay overbuilt for one card?
- Did the `last_modified` timestamp tracking detect any real revisions to closed FYs during the build period?
- Did NESO change the schema or break the API at any point during the build, and did the validation-on-fetch rule catch it?
- Were the held-back columns (volumes, zero-valued cost columns) ever asked about by a reader / reviewer?
