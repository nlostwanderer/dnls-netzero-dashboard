# Net Zero Dashboard — Project Plan (POC)

**Constraints:** Solo build · £50/month budget · Public-facing but expert-credible · Soft 8–12 week deadline with ship/shelve decision at the end

---

## 1. Project Definition & Success Criteria

### What this dashboard actually is
A **status tracker** for UK net zero infrastructure delivery, scored against published targets, with traffic-light indicators and a transparent methodology. Two sections:

- **Section A — Infrastructure tracker.** Battery storage, offshore wind, onshore wind, solar, grid transmission, grid connections queue. These have measurable data.
- **Section B — Opportunities tracker.** Overproduction tariffs, industrial co-location, energy export. These are *policy/proposal status*, not infrastructure metrics. Treated separately and flagged as such — different evidence type, different cadence, different rubric.

### Success criteria for the POC
The POC is successful if, at the end of ~10 weeks, you can answer "yes" to all of these:

1. Every metric has a documented source and refresh cadence. Every scored metric has a written rubric for its traffic light. Context cards (metrics that are not scored) are documented separately and explicitly carry no scoring.
2. Data refreshes happen automatically (or with one manual command) without breaking when sources change format — or the failure is detected, not silent.
3. An expert reader (CCC analyst, RenewableUK staffer) could read the methodology page and not laugh.
4. A non-expert reader gets the headline in under 30 seconds.
5. You've made a clear-eyed call on whether to ship publicly or shelve.

### Anti-criteria (what this is NOT)
- Not a real-time dashboard. Most sources update monthly/quarterly.
- Not a forecasting tool. No modelling — just measured progress vs published targets.
- Not editorial commentary. Opinion goes in a separate "analysis" section, not in the traffic lights.
- Not comprehensive. Coverage starts narrow and expands only if the narrow version works.

---

## 2. The Rubric Problem (do this first, before anything else)

The biggest weakness in the example output you shared was that traffic lights were assigned without a defined methodology. Fix this before writing a line of code.

### Proposed traffic-light rubric (challenge this)

For each infrastructure metric, score against the **trajectory needed to hit the 2030 target**, not the absolute number:

| Light | Meaning |
|-------|---------|
| 🟢 Green | Current build rate ≥ required rate to hit 2030 target |
| 🟡 Amber | Current build rate is 60–99% of required rate |
| 🔴 Red | Current build rate < 60% of required rate |
| ⚫ Grey | Insufficient/disputed data; methodology pending |

**Required rate** = (2030 target − current capacity) ÷ years remaining.
**Current rate** = trailing 12-month build, from the most recent reliable data point.

### Why this rubric is contestable
- Linear extrapolation is a simplification. Build rates accelerate as supply chains mature — early years lagging the line isn't necessarily fatal.
- "Required by 2030" is itself a moving target as government revises ambition.
- Mitigate by showing **both** the rubric score AND the underlying numbers, with a "methodology" link on every card. Don't let the traffic light do the thinking for the reader.

### For the "opportunities" section
Different rubric — these are policy proposals, not infrastructure:
- 🟢 Implemented / in regulation
- 🟡 Consultation open or pilot running
- 🔴 No active policy
- ⚫ Disputed scope

**Action item for week 1:** Write the rubric down formally, get one external sanity-check on it (post on a relevant subreddit, ask in an industry Slack, whatever), revise once, then freeze it for the POC.

---

## 3. Per-Metric Sourcing Strategy

For each metric: primary source, refresh approach, what breaks when source changes, fallback.

### Infrastructure metrics

**Battery storage (operational GW)**
- Primary: RenewableUK EnergyPulse storage report (PDF, quarterly)
- Secondary: Modo Energy buildout reports (also PDF, quarterly)
- Refresh: Manual quarterly download → extract figure → commit to repo
- Fragility: PDFs with no schema. If they restructure the report, your extraction breaks.
- Fallback: NESO TEC register filtered by "battery" + "operational" status (CSV, automatable)

**Offshore wind (operational GW)**
- Primary: BEIS/DESNZ Renewable Energy Planning Database (REPD) — monthly CSV
- Secondary: Crown Estate offshore wind dashboard
- Refresh: Scheduled scrape, monthly
- Fragility: Government dataset URLs change after machinery-of-government shuffles. Cache the URL in config.

**Onshore wind (operational GW)**
- Primary: REPD, same as above
- Secondary: RenewableUK monthly stats
- Refresh: Same pipeline as offshore — share the scraper

**Solar (operational GW)**
- Primary: REPD again, plus Solar Energy UK monthly figures
- Refresh: Same pipeline
- Caveat: Rooftop solar reporting lags badly. Note this on the methodology page.

**Grid transmission (km of new lines / GW of TEC delivered)**
- Primary: National Grid "Great Grid Upgrade" project pages — but these are HTML, no API
- Secondary: NESO Beyond 2030 plan progress (annual)
- Refresh: Quarterly manual update — there's no clean automation path here
- Honest assessment: This metric will be the messiest. Consider whether to track it at project-level (binary: built / in construction / consented / planned) rather than aggregate GW.

**Grid connections queue (TEC register)**
- Primary: NESO TEC register (CSV, monthly)
- Refresh: Automated monthly
- Caveat: Raw queue size is misleading post-Gate 2 reform. Track *Gate 2 approved* capacity once that data publishes, not total queue size.

### Constraint costs / curtailment

- Primary: NESO Data Portal "Constraint Breakdown Costs and Volume" — CSV, updated monthly with a lag
- Refresh: Automated monthly
- This one has the cleanest data path. Build it first as your POC test case.

### Opportunities section

**Overproduction tariffs / zonal pricing**
- Source: DESNZ REMA programme updates, Ofgem consultations
- Refresh: Manual on consultation announcements (rare events, set up Google Alerts)

**Industrial co-location near generation**
- Source: Industrial strategy announcements, freeport designations, specific project news
- Refresh: Manual, irregular — this is essentially news monitoring

**Energy export (interconnectors, hydrogen)**
- Source: NESO interconnector list, DESNZ hydrogen strategy updates
- Refresh: Quarterly manual

**Honest assessment of the opportunities section:** This is editorial work dressed as tracking. The data is qualitative, the cadence is irregular, and "status" is judgement-call territory. Two options:
1. Drop it from the POC. Ship the infrastructure tracker only. Add opportunities in v2.
2. Keep it but explicitly frame it as "policy watch" with a different visual treatment so users don't conflate it with hard infrastructure data.

**Recommendation: option 1 for the POC.** You can mention opportunities exist on a "coming soon" panel without committing to tracking them yet.

---

## 4. Handling Source Changes Over Time

This is the question most dashboards get wrong and is the single biggest reason they go stale.

### The problem
- PDFs restructure between editions
- CSV column names change
- URLs move
- Targets get revised by new governments
- New data sources appear that are better than your current ones

### Mitigations to build in from day one

1. **Source registry as code.** A single config file (YAML or JSON) listing each source with: URL, format, last-known-schema, last-successful-fetch date, fallback URL, expected cadence. Don't hardcode any of this in the scraper.

2. **Validation on fetch.** Every scheduled fetch validates the data shape before committing. If columns changed or values are wildly outside expected range, log a failure and keep the old data. Never silently overwrite with broken data.

3. **Notifications, not auto-recovery.** Failures email/Slack you. Don't try to be clever about recovery — a human (you) needs to look at it.

4. **Methodology versioning.** The rubric and target values are themselves data. Store them in the same repo, dated. When a target changes (e.g. government revises 2030 storage target), you commit a new methodology version and the dashboard shows "methodology updated" on affected cards.

5. **A "last verified" stamp on every metric.** Public-facing. If something hasn't refreshed in >2× expected cadence, the card auto-shows a warning.

6. **Annual methodology review.** Calendared. Force yourself to revisit the rubric and sources once a year minimum.

---

## 5. Risks, Trade-offs, Honest Pitfalls

### Risks (ranked by likelihood × impact)

1. **You lose motivation around week 5–6 and it stalls.** Highest risk for solo open-ended projects. Mitigation: the 10-week soft deadline, public commitment to ship-or-shelve, narrow scope.

2. **An expert publicly disputes a traffic light.** Will happen if you ship publicly. Mitigation: rigorous methodology page, willingness to update, version-controlled rubric so you can show how things have evolved.

3. **A primary data source disappears or restructures.** ~40% chance over a 12-month horizon for at least one source. Mitigation: validation-on-fetch, fallbacks, alerts.

4. **Targets get revised by government and you look out of date.** ~70% chance of at least one revision in 12 months. Mitigation: methodology versioning baked in from the start.

5. **You get accused of editorialising / political bias.** Net zero is contested politically. Mitigation: stick to published targets and published data, no commentary in traffic lights, separate "analysis" section if you do commentary at all.

6. **Hosting costs balloon if it gets popular.** Static-site approach mostly mitigates, but image-heavy dashboards on Cloudflare free tier can still hit limits. Mitigation: optimise images, monitor bandwidth, have a "donations to keep this running" button ready.

### Trade-offs to make explicitly

| Trade-off | The two sides | My recommendation |
|---|---|---|
| Breadth vs depth | Track 6 metrics shallowly, or 3 metrics rigorously | 3 deep for POC. Constraint costs, battery storage, offshore wind. |
| Automation vs manual | More automation = less ongoing work but more upfront work | Mixed. Automate what's already CSV; accept manual for PDFs in POC; revisit in v2. |
| Public-facing vs internal | Public adds credibility pressure & accountability | Build as if public from day one even if you decide not to ship |
| Live data vs cached | Static rebuild nightly is cheaper but less impressive | Static rebuild. £50/month doesn't cover live infra and it's not needed. |
| Generality vs UK focus | Easy to scope-creep to "EU" or "global" | Hard no. UK only. Bake the UK-specificity into the data model so expansion later requires an explicit decision. |

---

## 6. Tech Stack Recommendation (for the constraints)

- **Frontend:** Astro or Next.js static export. Astro probably better — content-focused, less JS.
- **Hosting:** Cloudflare Pages free tier or Netlify free tier.
- **Data refresh:** GitHub Actions on a cron schedule. Free for public repos.
- **Data storage:** JSON/CSV files in the same repo as the site. No database.
- **Scraping:** Python scripts in a separate `/data` folder, run by Actions, output to `/site/data/`.
- **Charts:** Observable Plot or Chart.js. Avoid heavy dashboarding libraries.
- **Methodology page:** Just markdown. Versioned in git, which is the methodology audit trail.

Total cost: ~£0/month. Domain name £10–15/year. Buffer your £50 budget for unexpected (paid API access if a key source moves behind a paywall).

**Defer:** auth, comments, user accounts, email signups. None of these belong in the POC.

---

## 7. Phased Plan (10 weeks)

**Week 1 — Methodology**
- Write rubric, target table, source registry. Get one external sanity-check.
- Output: `methodology.md` committed to repo. No code yet.

**Weeks 2–3 — Single-metric end-to-end slice**
- Build the constraint costs pipeline only: NESO CSV fetch → validate → store → render one card on a static page.
- Output: deployed at a temporary URL with one working card.

**Weeks 4–5 — Add two more metrics**
- Battery storage and offshore wind. Now you have 3 cards.
- First chance to find out where the abstraction is wrong. Refactor.

**Weeks 6–7 — Methodology page, accessibility, design pass**
- Write the public methodology page properly.
- Get an actual designer to look at it for a few hours of paid work (£50–150) — comes from outside the monthly budget but is worth it.
- Test with two non-expert and one expert reader.

**Week 8 — Add remaining infrastructure metrics**
- Onshore wind, solar, grid (project-level), connections queue.
- Stop here on infrastructure. Resist the temptation to keep adding.

**Week 9 — Resilience pass**
- Failure handling, alerts, "last verified" stamps, methodology versioning UI.

**Week 10 — Ship/shelve decision**
- Re-read the success criteria from section 1.
- Honestly score yourself.
- If shipping: domain, launch post, monitoring. If shelving: write a postmortem on why and archive the repo publicly.

---

## 8. Using Projects Well — When to Use This Project vs New Chat

This is the question you actually asked at the end of your message and it's the most useful one.

### Keep in this Project
Anything where context about your specific dashboard, your rubric, your sourcing decisions, or your code is relevant:
- Refining the rubric
- Adding/changing sources
- Code review of your scrapers
- Writing methodology copy
- Design feedback on cards
- Deciding edge cases ("how do we handle a target revision?")

### Start a new chat (still in this Project) when
- The current chat is getting long and slow
- You're switching between very different parts of the work (e.g., from sourcing logic to design copy) — fresh chat keeps each focused
- You hit a topic that needs a clean slate to think about clearly

### Start a new chat OUTSIDE this Project when
- The question is genuinely generic ("how does GitHub Actions cron syntax work" — no project context needed, faster outside the project)
- You're researching a tangentially related topic (e.g., reading up on zonal pricing for your own understanding, not for the dashboard)
- You're working on something else entirely

### Project hygiene tips
- Keep this plan document in the Project's knowledge so every new chat starts informed.
- When you make a methodology decision, update the plan or write a short ADR (architecture decision record) and add it to the Project. Don't rely on chat history to remember why you chose something.
- Every 3–4 weeks, ask me to summarise what's been decided so far. Treat that summary as a checkpoint.
- When you ship or shelve at week 10, write a postmortem and put it in the Project. Future-you will want it.

### A specific anti-pattern
Don't try to use a single chat for "the whole project." It'll get unwieldy and slow, and Claude's context budget is finite. One chat per ~focused task is the right grain.

---

## 9. Things I Pushed Back On (and might still be wrong about)

For your records, so you can revisit:

- **"Open-ended" timeline → soft 10-week deadline.** I might be wrong if you genuinely thrive without deadlines, but solo + open-ended is statistically a graveyard.
- **Markdown plan over Word doc.** I assumed wrong initially; corrected.
- **Drop opportunities section from POC.** You may disagree — if the opportunities angle is the *point* of the project for you (i.e., the editorial argument matters more than the infrastructure tracking), this recommendation is wrong.
- **3 metrics deep, not 6 shallow.** Standard POC advice but you might value coverage over depth for a different reason.
- **Static rebuild, not live.** If you're imagining real-time, push back — but "live" net zero data isn't really a thing; sources just don't update that fast.
- **Public-facing from day one even if you don't ship.** Builds discipline. If you'd rather build a scrappy internal version first and only later think about public, that's defensible too.

---

## 10. Immediate Next Actions (this week)

1. Decide whether to keep the opportunities section in scope. (My vote: drop for POC.)
2. Decide whether to accept the 10-week soft deadline. (My vote: yes.)
3. Write the rubric — first draft. We can iterate it together in this Project.
4. Pick the first metric for the end-to-end slice. (My vote: constraint costs from NESO — cleanest data, good headline figure, validates the whole pipeline.)
5. Set up the GitHub repo (public, MIT licence) and add this plan to it.

When you've made calls on 1–4, start a new chat in this Project titled "Rubric draft" and we'll do the rubric together properly.
