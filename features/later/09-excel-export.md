# 09 — Excel Export

**Verdict:** ⛔ DEFERRED from H0 build | **Target:** Phase 2 | **Status:** Deferred 2026-06-17

---

> **H0 scope note:** Excel export (ClosedXML) is **deferred** from the 8-week build — it's plumbing that doesn't prove core value. If any "export" is shown in the demo, it's a **browser print** of the approval view (🔵 stretch). This spec is the **Phase 2 target**. See [roadmap-8-weeks.md](../../ovation-platform-docs/product/roadmap-8-weeks.md).

---

## Summary

One-click download of a formatted Excel workbook from any budget level. The output mirrors what estimators were previously maintaining by hand in Excel — formatted, print-ready, and consistent across all projects. Critical for the demo handoff moment.

---

## What It Does

- Generates a formatted `.xlsx` file from the current budget level data
- Includes divisions, line items, quantities, unit costs, bid columns, and markup rows
- Totals and subtotals auto-calculated and formatted in the export
- Column widths and cell styles applied for readability
- Available at any budget status (Draft, Submitted, Approved, Locked)
- For locked budgets, export includes approval metadata (approver, date, hash)

---

## Export Sheet Structure

```
Sheet 1: Budget Summary
  ├── Project info header
  ├── Division subtotals
  ├── Markup rows
  └── Grand total

Sheet 2: Line Item Detail
  ├── All line items with quantities and unit costs
  └── Bidder proposal columns (L3 only)

Sheet 3: Variance (if L2 vs L3 available)
  └── [See Feature 10 — Variance Summary]
```

---

## Key Workflows

1. User navigates to any budget level
2. Clicks "Export to Excel" button
3. Backend generates the workbook server-side via ClosedXML
4. File downloaded directly to browser — no intermediate storage for standard exports
5. For locked budgets: export includes an approval certificate tab

---

## Technical Notes

- Library: ClosedXML (.NET) — server-side generation
- Endpoint: `GET /api/budgetlevels/{id}/export` → returns `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- No client-side Excel generation — all formatting happens on the backend
- For large budgets (1000+ line items), generation may take a few seconds — consider a loading state

---

## Dependencies

- [03 — Budget Table Editing](../in-scope/03-budget-editing.md) — export reflects the current saved state of the table
- [06 — Markup Formula Engine](../in-scope/06-markup-engine.md) — markup rows included in the export
- [07 — Approval Workflow](../in-scope/07-approval-workflow.md) — approval metadata appended to locked budget exports

---

## Related Features

- [10 — Variance Summary](../in-scope/10-variance-summary.md) — variance data optionally included as a third sheet

## Related Docs

- [ovation-platform-docs/docs/](../../ovation-platform-docs/docs/)
- [ovation-platform-docs/product/features.md](../../ovation-platform-docs/product/features.md)
