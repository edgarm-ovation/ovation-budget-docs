# Ovation Budget Platform — Feature Index

**8-Week Demo Sprint** | Phase 1 | Projects: West Henderson Apartments (L3) · Robindale 215 (L2)

This folder is the single source of truth for feature planning on the Ovation Budget Platform. Features are split into two buckets:

- **In-Scope** — Being built during the 8-week demo sprint (see table below)
- **[Deferred](./deferred.md)** — Intentionally excluded from Phase 1; documented for future reference

---

## In-Scope Features

| # | Feature | Sprint Week | Description |
|---|---------|-------------|-------------|
| 01 | [Authentication & Roles](./in-scope/01-authentication.md) | 1–2 | Azure AD SSO with four role tiers |
| 02 | [Project & Budget Navigation](./in-scope/02-project-navigation.md) | 1–2 | App shell, project list, L0–L3 level selector |
| 03 | [Budget Table Editing](./in-scope/03-budget-editing.md) | 3–4 | Inline editing of divisions, line items, and bid cells |
| 04 | [File Import](./in-scope/04-file-import.md) | 3–4 | Excel/CSV upload with auto-mapping and manual fallback |
| 05 | [Bid Leveling](./in-scope/05-bid-leveling.md) | 3–4 | Side-by-side proposal comparison and awarded bid selection |
| 06 | [Markup Formula Engine](./in-scope/06-markup-engine.md) | 3–4 | Contingency, fee, overhead, insurance, and bonds calculation |
| 07 | [Approval Workflow](./in-scope/07-approval-workflow.md) | 5–6 | Submit → Approve/Reject → Lock state machine |
| 08 | [Notifications](./in-scope/08-notifications.md) | 5–6 | In-app bell + Azure email alerts on key events |
| 09 | [Excel Export](./in-scope/09-excel-export.md) | 5–6 | Formatted budget export via ClosedXML |
| 10 | [Budget Variance Summary](./in-scope/10-variance-summary.md) | 5–6 | L2 vs L3 delta chart and summary sheet |
| 11 | [Seed Data](./in-scope/11-seed-data.md) | 7–8 | Realistic demo data for both pilot projects |

---

## 8-Week Timeline at a Glance

```
Weeks 1–2  │ Foundation & Auth        │ Features 01, 02
Weeks 3–4  │ Budget Editing & Import  │ Features 03, 04, 05, 06
Weeks 5–6  │ Approval & Notifications │ Features 07, 08, 09, 10
Weeks 7–8  │ Polish & Demo Prep       │ Feature 11 + QA + dry run
```

---

## Deferred Features

Everything intentionally out of scope for Phase 1 is documented in **[deferred.md](./deferred.md)**, organized by phase target (Phase 2, Phase 3, Year 2+). Use that doc when scoping future sprints or responding to stakeholder asks.

---

## Related Docs

| Document | Path |
|----------|------|
| Product Overview | [ovation-platform-docs/product/](../ovation-platform-docs/product/) |
| Full Roadmap | [ovation-platform-docs/product/roadmap.md](../ovation-platform-docs/product/roadmap.md) |
| Database Schema | [ovation-platform-docs/schemas/](../ovation-platform-docs/schemas/) |
| API Reference | [ovation-platform-docs/docs/](../ovation-platform-docs/docs/) |
| Sprint Tracker | [ovation-platform-docs/sprints/](../ovation-platform-docs/sprints/) |
| UI Mockup | [ovation-platform-mockup Open Ai/](../ovation-platform-mockup%20Open%20Ai/) |
| Owner Demo Doc | [ovation-platform-owner-demo-8-week claude/](../ovation-platform-owner-demo-8-week%20claude/) |
