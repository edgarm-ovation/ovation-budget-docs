# 06 — Markup Formula Engine

**Verdict:** 🟢 Core — calculates the budget proposal amount | **Sprint:** Weeks 4–5 | **Status:** Confirmed 2026-06-17

---

> **H0 scope note:** This is the "calculate the proposal amount" engine — server-side `FormulaService` is the source of truth. Per ratified architecture (target-architecture §7): keep all **7 markups**; **General Requirements + Bid Risk are computed read-only**, the other 5 are editable. The markup table below is illustrative — reconcile names to `docs/backend/formula-engine.md`.

---

## Summary

Automated calculation layer that applies standard construction cost markups on top of the raw trade subtotal. Produces the fully-burdened project cost used in approval and reporting. Eliminates formula errors from manual spreadsheet maintenance.

---

## What It Does

- Applies up to 7 markup types as percentage or fixed additions to the base cost
- Some markups are user-editable (contingency, fee); others are computed automatically (bonds, insurance)
- Cascade recalculation — changing any value upstream re-runs all markups instantly
- Stored and audited per budget level, not hardcoded
- Displayed as markup rows at the bottom of the budget table

---

## Markup Types

| # | Markup | Editable? | Applies To |
|---|--------|-----------|------------|
| 1 | Contingency | Yes — % | Base cost subtotal |
| 2 | General Conditions | Yes — % or $ | Base cost subtotal |
| 3 | Overhead & Profit (Fee) | Yes — % | Subtotal + contingency |
| 4 | Builder's Risk Insurance | Computed | Subtotal |
| 5 | General Liability Insurance | Computed | Subtotal |
| 6 | Payment & Performance Bond | Computed | Subtotal + GCs + fee |
| 7 | Escalation | Yes — % | Subtotal (L2 only) |

---

## Key Workflows

1. Estimator edits line item costs in the budget table
2. Subtotal updates → markup engine recalculates all markup rows server-side
3. Estimator can override any editable markup percentage
4. Grand total (base + all markups) is the value submitted for approval

---

## Technical Notes

- Calculations run server-side (not in the browser) — backend owns the formula engine
- Tables involved: `Markups` (per budget level), `LineItems`, `BudgetLevels`
- API: `POST /api/budgetlevels/{id}/recalculate` (or triggered on save)
- Open question: which of the 7 markups are editable vs. computed — UI shows 5 editable fields but spec lists 7; needs clarity before build

---

## Open Spec Gap

> The docs define 7 markup types, but the UI prototype shows 5 editable fields. Which markups are user-editable vs. auto-computed (e.g., insurance and bonds pulled from a rate table) needs to be resolved before implementation.

---

## Dependencies

- [03 — Budget Table Editing](./03-budget-editing.md) — markups are rendered as rows inside the budget table
- [07 — Approval Workflow](./07-approval-workflow.md) — the post-markup grand total is the value reviewed for approval

---

## Related Features

- [10 — Variance Summary](./10-variance-summary.md) — markup-adjusted totals feed the L2 vs L3 comparison

## Related Docs

- [ovation-platform-docs/product/features.md](../../ovation-platform-docs/product/features.md)
- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
