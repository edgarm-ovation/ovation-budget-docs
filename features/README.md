# Ovation Budget Platform — Feature Index

**8-Week Build (H0 Demo)** | 2 devs · real Azure SQL persistence | Projects: West Henderson (L3) · Robindale 215 (L2) · optional 3rd

This folder is the single source of truth for feature planning. **Scope confirmed 2026-06-17** (see [roadmap-8-weeks.md](../ovation-platform-docs/product/roadmap-8-weeks.md)): build a real, data-backed thin app that **replaces the Excel budget workflow** — cost codes, line-item editing, bid selection, markup calculation — persisted to Azure SQL.

Folder layout:
- **[`in-scope/`](./in-scope/)** — the 8 features being built in the 8 weeks
- **[`later/`](./later/)** — features deferred to a future phase (specs preserved, not built now)
- **[`deferred.md`](./deferred.md)** — the broader future-phase backlog (narrative)

Verdict legend: 🟢 core (real & persisted) · 🟡 high-value add-on · 🔵 stretch (only if time)

---

## In-Scope — being built (weeks 1–8)

| # | Feature | Verdict | Week | Notes |
|---|---------|---------|------|-------|
| 11 | [Seed Data](./in-scope/11-seed-data.md) | 🟢 | **1–2** | **Critical path — pulled forward.** Replaces import; gates everything |
| 02 | [Project & Budget Navigation](./in-scope/02-project-navigation.md) | 🟢 | 1–2 | App shell, project list, L0–L3 selector (L0/L1 read-only) |
| 03 | [Budget Table Editing](./in-scope/03-budget-editing.md) | 🟢 | 3 | Cost-code rows, inline editing, live totals — the Excel-replacement spine |
| 05 | [Bid Leveling](./in-scope/05-bid-leveling.md) | 🟢 | 4 | `group_key` proposal selection + awarded bid |
| 06 | [Markup Formula Engine](./in-scope/06-markup-engine.md) | 🟢 | 4–5 | Server-side `FormulaService` → calculated budget proposal amount |
| 10 | [Budget Variance Summary](./in-scope/10-variance-summary.md) | 🟡 | 6 | L2 vs L3 delta — data already in `BaselineAmount` |
| 07 | [Approval Workflow](./in-scope/07-approval-workflow.md) | 🟡 | 7 | Submit → approve → lock + SHA-256 snapshot |
| 08 | [Notifications](./in-scope/08-notifications.md) | 🟡 | 7 | In-app bell only — email deferred |

---

## Later — deferred to a future phase

Specs preserved in [`later/`](./later/) — not built during the 8 weeks.

| # | Feature | Why deferred |
|---|---------|--------------|
| 01 | [Authentication & Roles](./later/01-authentication.md) | Real SSO/RBAC is heavy; a demo role switcher (🔵 stretch) covers H0 |
| 04 | [File Import](./later/04-file-import.md) | Highest-risk feature; data is seeded instead |
| 09 | [Excel Export](./later/09-excel-export.md) | ClosedXML plumbing; browser-print (🔵 stretch) covers any demo need |

---

## 8-Week Timeline at a Glance

```
Weeks 1–2  │ Foundation + Seed Data     │ 11, 02 + invariants + Azure SQL
Weeks 3–6  │ The Budget Engine          │ 03, 05, 06, 10 (the real build)
Weeks 7–8  │ Approval + Polish + Demo   │ 07, 08 + dry run + 2nd/3rd project
```

---

## Related Docs

| Document | Path |
|----------|------|
| Confirmed 8-Week Plan | [roadmap-8-weeks.md](../ovation-platform-docs/product/roadmap-8-weeks.md) |
| Foundation Readiness Review | [foundation-readiness-review.md](../ovation-platform-docs/product/foundation-readiness-review.md) |
| Target Architecture (H0–H4) | [target-architecture.md](../ovation-platform-docs/docs/architecture/target-architecture.md) |
| Canonical Schema (A) | [docs/database/schema.md](../ovation-platform-docs/docs/database/schema.md) |
| Seed Data Spec (P0 — still a stub) | [docs/database/seed-data.md](../ovation-platform-docs/docs/database/seed-data.md) |
