# 02 — Project & Budget Navigation

**Verdict:** 🟢 Core | **Sprint:** Weeks 1–2 | **Status:** Confirmed 2026-06-17

---

> **H0 scope note:** L0/L1 are **read-only display** only. The notifications bell is in-app only (see 08). Project list is not role-filtered in H0 (no real auth — see 01); it shows all seeded projects.

---

## Summary

The app shell and navigation layer — the skeleton every other feature lives inside. Users land on a project list, select a project, then choose a budget level (L0–L3). This sets the context for all editing, importing, and approving.

---

## What It Does

- Persistent top nav with user identity, notifications bell, and logout
- Project list page showing all projects the current user has access to
- Per-project overview with budget level tabs (L0 → L1 → L2 → L3)
- Level selector communicates the current budget phase and locks state
- Breadcrumb trail so users always know where they are
- Responsive layout built with Tailwind CSS + shadcn/ui

---

## Key Workflows

1. Login → project list (filtered by role via `ProjectUsers`)
2. Select project → project overview with level tabs
3. Select budget level → budget table for that level loads
4. Locked levels show read-only banner; approved levels show approval badge

**Demo projects:**

| Project | Level | Notes |
|---------|-------|-------|
| West Henderson Apartments | L3 | Full bid-based budget with subcontractor proposals |
| Robindale 215 | L2 | Design development budget with markups |

---

## Technical Notes

- Framework: Next.js 14 App Router
- State: URL-driven (`/projects/[id]/budget/[level]`) — shareable deep links
- Tables involved: `Projects`, `BudgetLevels`, `ProjectUsers`
- Layout components: persistent shell with sidebar + top nav

---

## Dependencies

- [01 — Authentication](../later/01-authentication.md) — *deferred from H0; project list is not role-gated in the demo*

---

## Related Features

- [03 — Budget Table Editing](./03-budget-editing.md) — loads inside the level view
- [07 — Approval Workflow](./07-approval-workflow.md) — lock state displayed in level tabs
- [10 — Variance Summary](./10-variance-summary.md) — summary chart lives on project overview

## Related Docs

- [ovation-platform-docs/docs/](../../ovation-platform-docs/docs/)
- [ovation-platform-docs/product/budget-levels.md](../../ovation-platform-docs/product/budget-levels.md)
- [ovation-platform-mockup Open Ai/](../../ovation-platform-mockup%20Open%20Ai/)
