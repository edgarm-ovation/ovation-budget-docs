# 03 — Budget Table Editing

**Verdict:** 🟢 Core — the Excel-replacement spine | **Sprint:** Week 3 | **Status:** Confirmed 2026-06-17

---

> **H0 scope note:** This is the heart of the demo. Edits **persist to Azure SQL and survive reload** (real, not browser-only). Data is **seeded**, not imported (04 deferred). Server-side formula engine owns totals (06).

---

## Summary

The core work surface of the platform. Replaces the Excel workbook with an interactive, multi-user table where estimators can edit divisions, line items, quantities, unit costs, and bid amounts. Changes are saved to the database in real time via the API.

---

## What It Does

- Tabular view organized by CSI divisions and line items
- Inline cell editing — click a cell, type, tab to the next
- Auto-calculated subtotals per division and grand total
- Markup rows (contingency, fee, overhead, etc.) computed on top of the raw subtotal
- Awarded bid column highlights the selected proposal for each trade
- Change tracking — every edit logged to `AuditLog` with user + timestamp
- Optimistic UI updates via React Query; backend confirms or rolls back

---

## Budget Structure

```
Project
└── Budget Level (L0 / L1 / L2 / L3)
    └── Divisions (CSI format)
        └── Line Items
            ├── Description
            ├── Quantity + Unit
            ├── Unit Cost
            ├── Bidder Proposals (L3 only)
            └── Awarded Bid
```

---

## Key Workflows

1. Estimator opens a budget level → table loads with existing data
2. Click any editable cell → input activates in place
3. Tab/Enter moves to the next cell; Escape cancels
4. Subtotals and markups recalculate immediately on save
5. Locked budget (post-approval) shows all cells as read-only

---

## Technical Notes

- Table library: TanStack Table (virtual scrolling for large budgets)
- State management: React Query with optimistic mutations
- API: `PATCH /api/lineitems/{id}` per cell change
- Tables involved: `Divisions`, `LineItems`, `Proposals`, `Markups`
- Formula resolution: server-side (backend owns all calculations — no client-side formula engine in production)

---

## Dependencies

- [02 — Project & Budget Navigation](./02-project-navigation.md) — table loads inside the level view
- [06 — Markup Formula Engine](./06-markup-engine.md) — markups appear as rows below the subtotal
- [07 — Approval Workflow](./07-approval-workflow.md) — locked state disables all editing

---

## Related Features

- [04 — File Import](../later/04-file-import.md) — *deferred from H0; this table is populated by seed data instead*
- [05 — Bid Leveling](./05-bid-leveling.md) — awarded bid selection shown in the table

## Related Docs

- [ovation-platform-docs/docs/](../../ovation-platform-docs/docs/)
- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
