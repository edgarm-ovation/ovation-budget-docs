# 10 — Budget Variance Summary

**Sprint:** Weeks 5–6 | **Status:** Planned

---

## Summary

Side-by-side comparison of the L2 (Design Development) budget against the L3 (Construction Documents / bid-based) budget for the same project. Surfaces where actual bids came in above or below the earlier estimate — the number leadership cares most about at the end of the bid process.

---

## What It Does

- Loads L2 and L3 budget totals for the same project
- Shows variance by division: dollar delta and percentage swing
- Color-coded indicators — green for under-budget, red for over
- Summary-level chart (bar or waterfall) showing total L2 vs L3 delta
- Variance data available in-app and as a tab in the Excel export
- Grand total variance shown prominently at the project overview level

---

## Variance Breakdown

```
Division             │ L2 Budget   │ L3 Awarded  │ Delta       │  %
─────────────────────┼─────────────┼─────────────┼─────────────┼──────
Concrete             │  $1,200,000 │  $1,185,000 │   -$15,000  │  -1.3%
Structural Steel     │    $890,000 │    $940,000 │   +$50,000  │  +5.6%
Mechanical           │    $355,000 │    $353,500 │    -$1,500  │  -0.4%
Electrical           │    $420,000 │    $438,000 │   +$18,000  │  +4.3%
─────────────────────┼─────────────┼─────────────┼─────────────┼──────
TOTAL                │  $4,210,000 │  $4,261,500 │   +$51,500  │  +1.2%
```

---

## Key Workflows

1. User views project overview — variance summary widget shows L2 vs L3 delta at a glance
2. User drills into the variance detail view for a division-by-division breakdown
3. Download Excel export → variance included as Sheet 3

---

## Technical Notes

- Requires both L2 and L3 budget levels to exist for the same project
- L3 uses awarded bid amounts; L2 uses line item costs
- Chart library: Recharts (bar or waterfall chart)
- Data computed server-side: `GET /api/projects/{id}/variance`
- Tables involved: `BudgetLevels`, `LineItems`, `Proposals` (awarded bids)

---

## Open Spec Gap

> The summary sheet schema in the database supports basic totals, but the UI mockup shows richer behavior (division-level drill-down, chart). Backend schema may need extensions before the full UI can be built.

---

## Dependencies

- [05 — Bid Leveling](./05-bid-leveling.md) — awarded bids are the L3 side of the comparison
- [03 — Budget Table Editing](./03-budget-editing.md) — L2 line item data is the other side
- [09 — Excel Export](./09-excel-export.md) — variance included as a sheet in the export

---

## Related Features

- [02 — Project & Budget Navigation](./02-project-navigation.md) — summary widget lives on the project overview page

## Related Docs

- [ovation-platform-docs/product/budget-levels.md](../../ovation-platform-docs/product/budget-levels.md)
- [ovation-platform-mockup Open Ai/](../../ovation-platform-mockup%20Open%20Ai/)
