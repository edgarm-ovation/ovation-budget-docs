# 05 — Bid Leveling

**Verdict:** 🟢 Core | **Sprint:** Week 4 | **Status:** Confirmed 2026-06-17

---

> **H0 scope note:** Build the `group_key` proposal selection + awarded-bid persistence (the manager's signature workflow). Proposals are **seeded**, not loaded via import (04 deferred). Full summary-sheet richness (all bidder columns, winner markers) is a 🟡 add-on if time allows — see README.

---

## Summary

Side-by-side comparison of multiple subcontractor proposals for a single trade package. Estimators can see each bidder's line items, totals, and exclusions in one view, then select the awarded bid. Replaces the manual Excel comparison sheets that are currently the industry norm.

---

## What It Does

- Per-trade package view with 2–3 bidder columns side by side
- Each bidder column shows line items, quantities, unit costs, and totals
- Variance highlighting — cells that differ significantly from the lowest bid are flagged
- Inclusion/exclusion notes field per bidder
- "Award" button per bidder column — selecting one marks it as the awarded bid
- Awarded bid flows back into the main budget table as the accepted cost
- Proposal coverage metric — shows what percentage of the budget has an awarded bid

---

## Key Workflows

1. Estimator opens a trade package (e.g., "Mechanical" under L3)
2. Sees bidder proposals loaded (from file import or manual entry)
3. Reviews line-by-line differences across bidder columns
4. Clicks "Award" on the winning bidder
5. System writes `awardedBidderId` to the `TradePackages` table
6. Budget table updates awarded bid column automatically

---

## Bid Leveling Layout

```
Trade Package: Mechanical — West Henderson L3

                  │ Bidder A   │ Bidder B   │ Bidder C
──────────────────┼────────────┼────────────┼──────────
HVAC Units        │ $240,000   │ $235,000   │ $255,000
Ductwork          │  $85,000   │  $90,000   │  $82,000
Controls          │  $30,000   │  $28,500   │  $31,000
──────────────────┼────────────┼────────────┼──────────
TOTAL             │ $355,000   │ $353,500   │ $368,000
──────────────────┼────────────┼────────────┼──────────
                  │            │  [Award]   │
```

---

## Technical Notes

- Tables involved: `TradePackages`, `Bidders`, `Proposals`, `ProposalLineItems`
- Award endpoint: `PATCH /api/tradepackages/{id}/award` — needs full spec (marked as gap in docs)
- Group-level bid selection (awarding at division level, not just line-item) not fully specified yet
- Charts library: Recharts (optional — total comparison bar chart per trade)

---

## Open Spec Gap

> Group-level bid selection (awarding at the trade package level vs. individual line items) is not fully specified in the API. Needs resolution before Weeks 3–4 build.

---

## Dependencies

- [04 — File Import](../later/04-file-import.md) — *deferred from H0; proposals are seeded instead*
- [03 — Budget Table Editing](./03-budget-editing.md) — awarded bid result flows back to the main table
- [01 — Authentication](../later/01-authentication.md) — *deferred from H0*

---

## Related Features

- [10 — Variance Summary](./10-variance-summary.md) — L2 vs L3 comparison builds on awarded bid data

## Related Docs

- [ovation-platform-docs/product/budget-levels.md](../../ovation-platform-docs/product/budget-levels.md)
- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
- [ovation-platform-mockup Open Ai/](../../ovation-platform-mockup%20Open%20Ai/)
