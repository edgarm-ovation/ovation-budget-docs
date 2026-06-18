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
├── extract_bids.py      ← authors the bid-leveling seed (group_key + bidders/proposals/packages)
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
    ├── parking_options.json           (4)    parking / landscape option scenarios
    │
    │   ── bid-leveling seed (authored by extract_bids.py, see note below) ──
    ├── trade_packages.json            (38)   L3 trade scopes; GroupKeys array = the join glue
    ├── bidders.json                   (114)  subcontractors (7 real from workbook, 107 placeholder)
    └── proposals.json                 (114)  3 bids per trade (Low/2nd/3rd); low = awarded
    │   proposal_line_items.json       (240)  awarded-bid allocation across each trade's lines
```

> **`budget_line_items.json` is also updated by `extract_bids.py`:** the 240
> biddable L3 lines now carry a `group_key` (was null). FFE and no-cost-code GC
> soft-cost lines stay ungrouped on purpose.

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

## Bid-leveling seed (authored, not extracted — read this)

The workbook contains **no structured bid data** — only anonymous Low/2nd/3rd
benchmark pricing (`Comparison to Other`) and a few sub names in narrative
(`What changed`, `Risk`). So the Bidders / Proposals / TradePackages seed is
**authored by `extract_bids.py`**, anchored to that real material:

- **Trade packages** — 38 trades derived from the L3 cost-code structure. Each
  carries a `GroupKeys` array (the join glue) listing the `group_key`s it covers.
- **`group_key` tagging** — written back onto 240 L3 line items as
  `{trade-slug}-{cost_code}`. This is the side the original gap note assumed
  existed but didn't (every line was `null`).
- **Bidders** — 7 **real** subs lifted from the workbook (NRC, Gilmore, NV Gypsum,
  Otis, Sigma, NFP, Alpha) + 107 clearly-flagged placeholders (`is_placeholder:true`).
- **Proposals** — 3 per trade. Where a benchmark exists, bids = real Low/2nd/3rd
  $/UOM × quantity; otherwise derived from the trade's budgeted total ±spread. The
  low bid is marked `is_selected` / awarded.
- **Proposal line items** — the awarded bid allocated across the trade's budget
  lines (sums to the bid ±$0.02).

`extract_bids.py` self-validates the join **both directions** (no orphan package
keys, no orphan line keys) and that every awarded allocation reconciles to its bid.

> ⚠️ **Placeholder bidder names need a once-over from estimating/construction-ops
> (Lloyd's side) before this is shown to anyone who'd recognize real Vegas subs.**
> The 7 real names are safe; the 107 generated ones are demo filler.

**Still genuinely missing:** **Robindale 215 (L2)**, the second seed project.

**Now closed:** ComparableProjects benchmark costs and the **bid-leveling seed**
(`TradePackages.GroupKeys` join glue) — both were flagged as missing. See
`relationships.md` → *What is NOT in this package* for the full status.

## Regenerating / extending

- Re-extract after the Excel changes: `python extract_full.py`.
- Each pass is **marker-driven** (it scans column-A labels), so it survives row
  inserts/deletes between budget versions — no hardcoded row numbers per sheet.
- To add **Robindale 215**, point a second pass at its workbook: add its budget
  sheets to `BUDGET_SHEETS` with a new `PROJECT_ID`, and re-aim the comparables
  passes at its sheet names.
- To add more comparable projects, extend `NORM_COMPS` (CSI columns on
  `Normalize`) and `OFF_COMPS` (trade columns on `Offsite Comp`).
