# Seed Package — West Henderson (full workbook)

Everything needed to load the **real** West Henderson budget into the database:
schema-shaped data extracted from the source Excel, the table DDL, the
relationship/load-order map, and a reproducible extraction script.

**Scope upgrade (2026-06-17):** this package previously held only the `Level 3`
sheet. It now extracts **every signal sheet** in the 28-sheet workbook — all five
budget-level versions (history), the comparable-project benchmark costs, trade
benchmarks, insurance/bond detail, alternate (menu) pricing, the risk register,
value-engineering recommendations, and parking options. The estimator's scratch
sheets (`Another Uselss`, `Useless Breakdown`, `_REFERENCE888777888`, dupes) are
deliberately skipped.

**Source of truth:** `../Excel-Docs-Projects/Budget - West Henderson - Level 3.xlsx`
(28 sheets; `Level 3` stamped UPDATED 2025-12-29).
**Canonical schema:** `../docs/database/schema.md` (Schema A).
**Extractor:** `extract_full.py` (multi-sheet, self-validating) — **supersedes**
the original single-sheet `extract.py`, which is kept for reference.

> ⚠️ The old `../jsons/` files are **dummy data** and disagree with the Excel on
> actual dollar values. This package supersedes them for West Henderson.

---

## Contents

```
seed-package/
├── README.md            ← you are here
├── relationships.md     ← FK graph, load order, Excel→schema transform rules
├── extract_full.py      ← re-runnable multi-sheet extractor (canonical)
├── extract.py           ← original single-sheet extractor (Level 3 only, kept for reference)
├── schema/
│   └── seed-tables.sql  ← DDL for just the tables this seed populates
└── data/
    ├── projects.json                  (1)    project header + units/SF/cost summary
    ├── unit_mix.json                  (5)    unit type breakdown
    ├── parking.json                   (1)    parking counts + ratio
    ├── budget_levels.json             (5)    L1.1, L1.2, L1.3, L2.1, L3.1 (history chain)
    ├── divisions.json                 (33)   CSI division master (incl. markup divs)
    ├── budget_line_items.json         (1337) line items across all 5 levels
    ├── markups.json                   (35)   7 markup kinds × 5 levels
    ├── comparable_projects.json       (6)    West Henderson + 5 comps
    ├── comparable_project_costs.json  (108)  per-CSI-division comp costs (Normalize)
    ├── comparable_trade_costs.json    (165)  per-trade comp costs (Offsite Comp)
    ├── trade_benchmarks.json          (22)   WH trade $/UOM vs proposal Low/2nd/3rd/Avg
    ├── insurance_bonds.json           (1)    GL insurance / bond computation detail
    ├── menu_pricing.json              (5)    alternate / upgrade tier pricing
    ├── risk_items.json                (9)    risk register (#REF! preserved as null)
    ├── value_engineering.json         (7)    VE / savings recommendations
    └── parking_options.json           (4)    parking / landscape option scenarios
```

## Validation (proves the extraction is faithful)

`extract_full.py` reconciles **every** budget level against that sheet's own Excel
"Total Hard Costs". All five tie out to the cent:

```
level                              items    lines $         markups $        delta
Level 1                            266      67,743,763.56   16,847,217.80     0.01
Level 1.1 — Update A               268      66,229,739.58   16,321,798.81     0.02
Level 1.1 — Update B               272      62,805,417.14   15,326,205.89     0.02
Level 2 — Transmitted              272      64,163,505.07   15,684,403.95     0.01
Level 3 — Construction Documents   259      63,295,390.65   14,081,357.25    -0.02
```

(L3 reproduces the original `extract.py` output exactly: line items
$63,295,390.65, markups $14,081,357.25, −$0.02 cent-rounding.) Re-run anytime:

```
pip install openpyxl
python extract_full.py
```

---

## How to use this for the database load

1. Create tables from `schema/seed-tables.sql` (or your EF Core migration of the
   full `schema.md`).
2. Insert **one seed user** — required by the NOT NULL user FKs.
3. Load `data/*.json` in the order in `relationships.md` → *Load order*,
   resolving slug keys (`project_id`, `budget_level_id`, `division_code`) to
   GUIDs as you go.
4. Field mapping: `data/*.json` uses snake_case slugs; columns are PascalCase.
   Notable: line item `line_total` → `TakeoffAmount`, `qty` → `TakeoffQuantity`,
   `unit_cost` → `TakeoffUnitPrice`, `escalation` → `EscalationPct`,
   `division_code` → resolve to `CustomDivisionId`.

`relationships.md` has the full FK table, the slug→GUID ID strategy, and every
Excel→schema transform decision (markup splits, real rates, preserved cost-code
anomalies).

## Known gaps (read before building bid features)

This is the **budget**, not the bid leveling. Still not included, needs a separate
source: **Bidders / Proposals / TradePackages** (and the critical
`TradePackages.GroupKeys` join glue) and **Robindale 215 (L2)**, the second seed
project. The `Risk` sheet hints at bidders (Northstar, JMAC, NRC, Gilmore…) but
carries no structured multi-bidder leveling.

**Now closed:** ComparableProjects benchmark costs (were flagged as missing) are
extracted from the `Normalize` + `Offsite Comp` sheets. See `relationships.md` →
*What is NOT in this package* for the full status.

## Regenerating / extending

- Re-extract after the Excel changes: `python extract_full.py`.
- Each pass is **marker-driven** (it scans column-A labels), so it survives row
  inserts/deletes between budget versions — no hardcoded row numbers per sheet.
- To add **Robindale 215**, point a second pass at its workbook: add its budget
  sheets to `BUDGET_SHEETS` with a new `PROJECT_ID`, and re-aim the comparables
  passes at its sheet names.
- To add more comparable projects, extend `NORM_COMPS` (CSI columns on
  `Normalize`) and `OFF_COMPS` (trade columns on `Offsite Comp`).
