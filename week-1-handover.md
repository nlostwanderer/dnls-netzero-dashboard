# Week 1 handover — end of 5 May 2026

This document captures the state of the project at the end of week 1 of the POC build. It's intended as the starting context for the next chat (the splicer), and as a checkpoint per plan §8 ("every 3–4 weeks, ask me to summarise what's been decided so far").

**Where we are against the 10-week deadline:** end of day 2 of week 1. The plan's week 1 deliverable was "rubric, target table, source registry — no code yet." We are ahead of that — rubric is frozen, ADRs are in place, and the constraint costs scraper is working against real NESO data. We are roughly at the threshold of plan weeks 2–3 ("deployed at a temporary URL with one working card").

---

## What exists in the repo

Local git repo at `/Users/tino/DNLS_Net zero tracking/`. GitHub remote not set up yet (deferred — explicit decision).

```
/
├── .gitignore
├── ADR-001-rubric-design.md
├── ADR-002-data-acquisition-constraint-costs.md
├── methodology-changelog.md          ← versioned methodology, v0.4 current
├── net-zero-dashboard-plan.md        ← plan §1 amended per v0.2 M-1
├── neso-feedback.md                  ← running log of data quality observations
├── rubric-v0.1.md                    ← frozen for POC build
└── data/
    ├── scrapers/
    │   ├── DNLS_constraint_costs.py  ← production scraper (was scrape.py)
    │   └── diagnostics/
    │       └── diagnose_2025_26.py   ← one-off, kept as evidence behind v0.4
    ├── state/                        ← committed to git
    │   ├── constraint-costs.json     ← {resource_id: last_modified}
    │   └── constraint-costs-schema.json  ← frozen schema, value-shape format
    ├── raw/                          ← gitignored, regenerable
    │   └── constraint-costs/
    │       └── constraint-breakdown-YYYY-YYYY.csv  ← 10 FY archives
    └── processed/                    ← gitignored, regenerable
        └── constraint-costs/
            └── records.json          ← typed, all FYs, sorted by Date
```

Two commits in git history:

1. Initial commit (4 May): plan, rubric, ADRs, scraper as `scrape.py`.
2. v0.4 commit (5 May): value-shape validation, scraper renamed, neso-feedback.md added.

---

## Methodology state

**Rubric** — `rubric-v0.1.md`. Frozen for POC build. Three trackers, distinct scoring:

- **Infrastructure tracker:** gap-closure projection against 2030 targets. Green ≥100% delivery ratio, amber 60–100%, red <60%, grey for insufficient data.
- **Opportunities tracker:** policy status (implemented / consultation / no action / disputed). Single POC opportunity: REMA / zonal pricing.
- **Major projects tracker:** lifecycle status for named transmission projects, no scoring.

Plus a fourth pattern added in v0.2 M-1:

- **Context cards** (added v0.2 M-1): metrics that are not scored. Carry no traffic light. Show the figure plus an explainer. **Constraint costs is a context card.**

**Plan §1 success criteria** (amended in v0.2 M-1, applied):

1. Every metric has a documented source and refresh cadence. Every scored metric has a written rubric for its traffic light. Context cards are documented separately and explicitly carry no scoring.
2. Data refreshes happen automatically (or with one manual command) without breaking when sources change format — or the failure is detected, not silent.
3. An expert reader could read the methodology page and not laugh.
4. A non-expert reader gets the headline in under 30 seconds.
5. A clear-eyed call on ship-or-shelve at week 10.

---

## What the constraint costs metric looks like

This is the POC pilot card. It's a **context card** (not scored).

**Headline figure:** sum of `Thermal constraints cost` over the most recent complete UK FY (v0.2 M-5).
- As of May 2026, that's **FY 2025-26**.
- Sum is ~~365~~ **364 days** (NESO returned 364 rows; see M-10 / neso-feedback F-3).

**Data scope decisions** (already locked in, do not revisit without changelog entry):

- **One column only on the card:** `Thermal constraints cost`. Other three cost categories stored but not displayed (v0.2 M-2, M-3).
- **Volume columns held from publication entirely** — sign convention undocumented (v0.2 M-4, neso-feedback F-2).
- **Editorial constraint baked in:** thermal cost ≠ "wind paid to switch off." This distinction must hold in any explainer copy.

**What still needs to be built for the card to ship:**

- The **splicer** — takes records.json, slices to FY 2025-26, sums thermal cost, produces an output file with the figure plus caveats. **This is the next chat's job.**
- The **render** — Astro page (or simpler) with one card showing the number, FY label, data-through date, sparkline, caveats. Subsequent chat.
- The **explainer copy** — deferred until the card is rendered (per v0.2). Cannot drift into curtailment-payments framing.

---

## What the scraper does (and what it does NOT do)

**Does:**

- Hits NESO CKAN package `fb56b46e-cef3-4eb8-9294-0ca19769b7eb` via `api.neso.energy/api/3/action/`.
- Walks all 10 FY resources (2017-18 through 2026-27).
- Tracks `last_modified` per resource in `data/state/constraint-costs.json`. Only fetches resources whose timestamp has advanced.
- If any resource changed, refetches all 10 to rebuild records.json cleanly (POC simplification — bandwidth trade-off accepted).
- Validates each fetched resource against the frozen schema (`data/state/constraint-costs-schema.json`).
- Hard-fails on schema drift, preserving cached data, exits non-zero.
- Writes typed JSON (`data/processed/constraint-costs/records.json`) and raw CSV archives (`data/raw/constraint-costs/`).

**Does not:**

- Compute any figures. Pure data acquisition layer.
- Slice records to any window (not FY 2025-26, not trailing 12 months, nothing). Records.json is the union of all FYs sorted by Date.
- Render anything.
- Filter columns. All eight measurement columns (4 cost + 4 volume) are stored.
- Make decisions about what to publish. That's the splicer's job.

---

## The validation rule (v0.4)

This took two iterations to land. Key fact for the next chat: **CKAN's `type` metadata is not trustworthy in this dataset.** The validator uses *value shape* instead.

Frozen schema per column stores:

- `id` — column name
- `unit` — from CKAN `info.unit`
- `value_class` — one of `integer`, `numeric`, `date`, `text` (inferred from observed values on first freeze)
- `ckan_type` — recorded for audit only, not used in validation

Validation rule on every fetch:

- `integer`: value is JSON int, or string parseable as int
- `numeric`: value is JSON number, or string parseable as float
- `date`: value matches `^\d{4}-\d{2}-\d{2}$` (optionally with `T...` suffix)
- `text`: no content check

Drift signals (hard-fail):

- Column added / removed / renamed
- Unit changed
- value_class changed
- A value failing its value_class rule

Methodology source of truth: changelog v0.4 M-7 through M-9.

---

## Known data quirks (relevant for the splicer)

1. **2025-26 `Thermal constraints cost` values are strings**, not JSON numbers, in the NESO datastore response. All 364 parse as `float()`. The splicer must cast.
2. **2025-26 file has 364 rows, not 365.** Missing day not yet identified. Card displays the caveat (v0.4 M-10, neso-feedback F-3).
3. **Other FYs return JSON numbers**, not strings. So the splicer cannot assume one shape across all years — code defensively.
4. **All 10 FY resources are in records.json**, each row tagged with `_resource_id` and `_fy_label`. The splicer can slice on either.
5. **The 2026-27 resource is the current in-progress FY.** It has fewer than 365 rows by design (it's not done yet). The headline FY is the most recent *complete* one — currently 2025-26.

---

## NESO feedback log

Three open entries in `neso-feedback.md`:

- **F-1** — Inconsistent CKAN `type` across resources (triggered v0.3 and v0.4).
- **F-2** — Sign convention on volume columns is undocumented.
- **F-3** — Missing day in 2025-26 resource.

None are blocking. All would be useful to put to NESO at some point.

---

## What the next chat (splicer) should do

**Task:** Build the splicer. Takes records.json as input, produces a single output file (suggested name: `data/processed/constraint-costs/headline.json`) containing:

- The headline figure (sum of thermal cost over FY 2025-26).
- The FY label.
- The data-through date (latest Date in the FY).
- Row count (expected 365, actual 364 — the caveat).
- The data source URL.

**Constraints to respect (no need to re-litigate):**

- The headline FY is the latest *complete* UK FY (per v0.2 M-5).
- Only `Thermal constraints cost` is summed (per v0.2 M-2).
- The splicer must cast string values to float (per v0.4 known quirks).
- No traffic light is computed (constraint costs is a context card — v0.2 M-1).

**Methodology questions the splicer may surface** (don't pre-decide, let the splicer's first run surface them):

- What does the splicer do if records.json doesn't yet contain a complete FY (e.g. before the scraper has been run)? Crash, or produce an empty headline?
- What does the splicer do if NESO has revised historical data and the headline figure changes between runs? Log the delta? Just overwrite?
- Should the splicer also produce a quarterly sparkline data file, or is that a separate step?

**Print-first applies.** Splicer is small — maybe 80 lines. Should start with a script that loads records.json, identifies FYs, prints what it would do, before any output file is written.

**Suggested file location:** `data/scrapers/splicer.py` or `data/processed/constraint-costs/build_headline.py`. Let the next chat decide.

---

## Things deferred / not yet done

- **GitHub remote.** Local git only. Set up when convenient — not blocking.
- **External sanity-check on the rubric.** Plan §10 next-action 3. Outstanding. Worth doing whenever you have 10 minutes spare. A Reddit post or DM to one industry contact.
- **Card explainer copy.** Drafted only after the card is rendered (v0.2 deferred items).
- **Public methodology page.** Plan week 6–7.
- **Claude Code integration.** Discussed in this chat — recommendation: not yet, revisit week 4 when starting metric #2.
- **Slack alerting.** Deferred — GitHub Actions email-on-failure is sufficient for POC.
- **Investigation of missing day in 2025-26.** Logged in F-3, deferred.

---

## Open methodology questions to revisit at week 10 ship/shelve

From v0.4 review trigger:

- Did the value-shape rule hold across all sources added during the POC, or did we need a v0.5?
- Did the missing-day caveat on the card cause reader confusion?
- Did any NESO feedback entries (F-1, F-2, F-3) get resolved during the build?

From earlier versions, all still open:

- Did the 60% red/amber threshold (rubric §3) do useful discrimination?
- Did the three-tracker architecture confuse readers?
- Did the REMA opportunity tracking pattern work?
- Did the "Delayed" flag for transmission projects get correctly populated?

---

## How to use this document

Add to project knowledge. Reference at the start of the next chat — something like *"continuing the constraint costs work, see week-1-handover.md"* — and that chat will start informed without us re-litigating today's decisions.

Future handover docs will follow this same shape: where we are, what's been built, what's been decided, what's next, what's deferred. One every ~2 weeks or after any major methodology version bump.
