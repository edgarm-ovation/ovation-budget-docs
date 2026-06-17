# 8-Week Build Plan (H0 — Demo)

**Status:** `[CONFIRMED 2026-06-17]`
**Team:** 2 developers · from zero (no app code yet) · ~16 person-weeks
**Supersedes:** the earlier 11-feature "production" framing of this doc
**Aligned with:** [foundation-readiness-review.md](./foundation-readiness-review.md), [target-architecture.md](../docs/architecture/target-architecture.md) (H0)

---

## Objective

Build a **real, Azure SQL–backed thin application that replaces the Excel budget workflow** for 2–3 seeded projects. An estimator opens a project, works the budget by **cost code (division)**, edits line items, selects **proposals/bids**, applies **markups**, and the app **calculates the budget proposal amount** — and every change **persists to Azure SQL and survives reload.**

This is a working vertical slice on real data, presented alongside a polished UI that shows the full vision. It is **not** a production estimating platform, and it intentionally does **not** include the highest-cost peripheral features (see *Out of Scope*).

**Seed projects:** West Henderson Apartments (L3, primary) · Robindale 215 (L2) · optional 3rd.

---

## Scope Decisions (confirmed)

| Decision | Ruling |
|---|---|
| Persistence | **Real Azure SQL.** Edits/bids/markups save server-side and survive reload. Not browser-only. |
| Source of data | **Seeded directly** from West Henderson L3 + Robindale L2. No file import in this build. |
| Auth | **No Entra ID SSO.** A simple role/user switcher for the demo only (stretch). |
| Export / email | **Out.** Browser-print of the approval view is the only "export" (stretch). |
| Calculation ownership | **Server is the source of truth** — `FormulaService` computes canonical totals. Frontend shows preview totals only. |

---

## Success Criteria

- App is deployed to Azure and reachable.
- 2–3 seeded projects load with real budget data; totals match the source spreadsheet.
- An estimator can **edit a line item, select an awarded bid by `group_key`, and see markups recalculate** the budget proposal amount.
- **Edits persist to Azure SQL and survive a page reload.**
- A budget level can be **submitted, approved, and locked** with a SHA-256 snapshot (add-on).
- The demo runs end-to-end in under 20 minutes with clear "real vs. shown-as-roadmap" labeling.

---

## In Scope

### 🟢 Core — this IS the product

- Seeded data for 2–3 projects (no import)
- Cost code / division structure — the organizing spine
- Line-item editing (qty, unit, unit cost, notes) with live totals
- Proposal / bid selection by `group_key` (the manager's signature workflow)
- Markup engine (construction contingency, contractor fee, overhead, GL insurance, sub bonds) — server-side `FormulaService`; General Requirements + Bid Risk computed read-only
- Manual overrides with notes
- Azure SQL persistence + EF Core migrations
- App shell, project list, L0–L3 navigation (L0/L1 read-only)

### 🟡 High-value add-ons — funded by the cut peripheral features

- Variance summary (L2 vs L3) — data already in `BaselineAmount`
- Approval snapshot + lock (SHA-256 over canonical snapshot)
- Audit trail (who/what/when) — cheap **only if built in from day 1**
- In-app notification bell
- Summary-sheet richness (bidder columns, winner/proposed markers)

### 🔵 Stretch — only if weeks 5–6 hold

- Simple role/user switcher (not real SSO)
- Browser-print of the approval view
- L0/L1 read-only display

---

## Out of Scope (deferred — the project extends later)

These are deferred **on purpose** because each is a large time-sink that doesn't prove the core value:

- **File import / spreadsheet parsing** (highest-risk feature — data is seeded instead)
- **Entra ID / Azure AD SSO** and full role-based access
- **Excel export** (ClosedXML)
- **Email notifications** (Azure Communication Services)
- Real-time multi-user collaboration, cross-project benchmarking, historical migration

See [features/deferred.md](../../features/deferred.md) for the full deferred list and target phases.

---

## Foundation Invariants (lock in weeks 1–2 — this is "right foundation")

These are what let the same codebase grow from this demo to the 10-year platform without a rewrite ([target-architecture.md §5](../docs/architecture/target-architecture.md)):

1. **Server is the financial source of truth** — `FormulaService` computes canonical totals on save; frontend previews only.
2. **Approved budgets are immutable** — SHA-256 snapshot + lock; changes start a new sub-level.
3. **Audit is append-only.**
4. **`OrgId` on root tables from day one** (defaults to single Ovation tenant).
5. **Business logic lives in Services**, never in endpoints or the frontend.
6. **Build against Schema A only** — finish archiving Schema B; build against [docs/database/schema.md](../docs/database/schema.md).

---

## Week-by-Week Plan

### Weeks 1–2 — Foundation + Seed Data
**Goal:** a deployable skeleton with real data to build against.

- .NET 8 modular-monolith API + Next.js app shell, deploy path proven (App Service B2 / Static Web Apps / Azure SQL).
- Schema A subset in Azure SQL + EF Core migrations; `OrgId` hedge in place.
- **Seed data loaded for West Henderson L3** (this is critical path — see below).
- Project list + L0–L3 navigation render real seeded projects.
- Invariants 1–6 wired in.

**Gate:** custom line items, overrides, and bid selections can be stored and re-read. WH L3 totals match the source spreadsheet.

### Weeks 3–6 — The Budget Engine (the real work)
**Goal:** do the Excel work in the app, persisted.

- Editable budget table by cost code/division, live totals (wk 3).
- `group_key` bid/proposal selection + awarded-bid state (wk 4).
- `FormulaService` markup engine → calculated budget proposal amount, saved server-side (wk 4–5).
- Manual overrides with notes; audit on budget-critical fields (wk 5).
- Variance summary (L2 vs L3) + summary-sheet richness (wk 6).

**Gate:** edit → pick bid → recalc markups → reload → values persisted and correct.

### Weeks 7–8 — Approval, Polish, Demo
**Goal:** make it owner-ready.

- Approval snapshot + lock (SHA-256); approval view.
- Seed 2nd/3rd project; clean loading/saving/empty/error states.
- Discrepancy review against source spreadsheets.
- Demo script + 20-minute runbook; pre-demo dry run.
- Known-limitations list ("real vs. roadmap").

**Gate:** end-to-end demo under 20 minutes, no blocking bugs, honest labeling.

---

## Critical Path & Risks

| Risk | Mitigation |
|---|---|
| **Seed data is the gating dependency but `seed-data.md` is still a stub.** | Write the spec first; load WH L3 by end of week 2. You cannot build/test the calculator without it. |
| Markup base-exclusion logic is subtle | Port directly from the prototype's `DATA` object; verify totals against the spreadsheet in week 5. |
| Scope creep back toward import/auth/export | This doc is the boundary. Anything in *Out of Scope* is a Phase 2 ticket, not a week-7 surprise. |
| 2 devs, from zero | Weeks 1–2 and 7–8 are mostly non-feature work; only weeks 3–6 are real build time. Protect them. |

---

## What the Demo Shows

1. The Excel pain point, then: open West Henderson in the app.
2. Work the budget by cost code; edit a line item; totals update live.
3. Compare proposals and award a bid by `group_key`.
4. Watch markups recalculate the budget proposal amount.
5. Reload — **the data is still there** (this is the "it's real" moment).
6. Submit → approve → lock with a snapshot.
7. Review the variance summary; close with the roadmap (import, roles, export, reporting).
