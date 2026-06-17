# Seed Package — West Henderson Level 3

Everything needed to load the **real** West Henderson Level 3 budget into the
database: schema-shaped data extracted from the source Excel, the table DDL, the
relationship/load-order map, and a reproducible extraction script.

**Source of truth:** `../Excel-Docs-Projects/Budget - West Henderson - Level 3.xlsx`
(sheet `Level 3`, stamped UPDATED 2025-12-29).
**Canonical schema:** `../docs/database/schema.md` (Schema A).

> ⚠️ The old `../jsons/` files are **dummy data** and disagree with the Excel on
> actual dollar values. This package supersedes them for West Henderson.

---

## Contents

```
seed-package/
├── README.md            ← you are here
├── relationships.md     ← FK graph, load order, Excel→schema transform rules
├── extract.py           ← re-runnable extractor (Excel → data/*.json)
├── schema/
│   └── seed-tables.sql  ← DDL for just the tables this seed populates
└── data/
    ├── projects.json            (1)   project header + units/SF/cost summary
    ├── unit_mix.json            (5)   unit type breakdown
    ├── parking.json             (1)   parking counts + ratio
    ├── budget_levels.json       (1)   West Henderson L3.1
    ├── divisions.json           (31)  CSI division master (incl. markup divs)
    ├── budget_line_items.json   (258) the real line items
    └── markups.json             (7)   the 7 canonical markup rows w/ real rates
```

## Validation (proves the extraction is faithful)

`extract.py` reconciles the data against the Excel's own grand total:

```
line items     : 258   sum 63,295,390.65
markups        : 7     sum 14,081,357.25
computed grand : 77,376,747.90
excel grand    : 77,376,747.92   (delta -$0.02, cent-rounding only)
```

Every CSI division subtotal also matches the Excel to the penny. Re-run anytime:

```
pip install openpyxl
python extract.py
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

This is the **budget**, not the bid leveling. Not included, needs a separate
source: **Bidders / Proposals / TradePackages** (and the critical
`TradePackages.GroupKeys` join glue), **ComparableProjects** benchmark costs,
and **Robindale 215 (L2)**, the second seed project. See `relationships.md` →
*What is NOT in this package*.

## Regenerating / extending

- Re-extract after the Excel changes: `python extract.py`.
- To add **Robindale 215**, point a second pass at its workbook and parameterize
  `PROJECT_ID` / `BUDGET_LEVEL_ID` / sheet name in `extract.py`.
