# Migrating the Seed Package → Azure SQL

How to load the validated West Henderson seed data into Azure SQL and serve it to
the app. Companion to [`README.md`](README.md) (what's in the package) and
[`relationships.md`](relationships.md) (FK graph, load order, field mapping).

**Status:** data is migrate-ready and validated; DDL exists for all tables; the
loader just needs the field-mapping rules below.

---

## Readiness at a glance

| Area | State |
|---|---|
| Data values | ✅ Clean; all 5 budget levels reconcile to their Excel total to the cent |
| DDL | ✅ `schema/seed-tables.sql` — **17 tables** (8 original + 9 expansion) |
| Data files | ✅ 16 JSON in `data/` (map 1:1 to 16 tables; `Users` is seeded manually) |
| Loader | ⚠️ Must apply snake→Pascal mapping + slug→GUID resolution (see below) |
| Anomalies | ⚠️ `Risk` sheet `#REF!` cells stored as `NULL` + `HasRefError = 1` |

---

## Migration sequence

### 1. Create the tables
Run [`schema/seed-tables.sql`](schema/seed-tables.sql) against the Azure SQL
database (Azure Portal query editor, SSMS, or `sqlcmd`). Tables are ordered so FKs
resolve. The file has **no `IF NOT EXISTS` guards** (matches the original style) —
if you may re-run it, wrap each statement in `IF OBJECT_ID('dbo.Table') IS NULL`.

### 2. Insert one seed user
Required because `Projects.CreatedByUserId` and `Markups.UpdatedByUserId` are
**NOT NULL**. The JSON deliberately omits user FKs — the loader sets them.

```sql
INSERT INTO Users (AzureOid, Email, Name, Department)
VALUES ('seed-system', 'seed@ovationco.com', 'Seed System', 'Purchasing');
```

### 3. Load the 16 JSON files in order
Follow `relationships.md` → *Load order*. Summary:

```
Users (manual) → Projects → Divisions → UnitMix → Parking
→ BudgetLevels (resolve parent_budget_level_id) → BudgetLevelLineItems → Markups
→ ComparableProjects → ComparableProjectCosts → ComparableTradeCosts
→ TradeBenchmarks → InsuranceBondDetail → MenuPricingOptions
→ RiskItems → ValueEngineeringItems → ParkingOptions
```

Resolve slug keys to GUIDs as you go and keep a slug→GUID dictionary for the FKs.

---

## What the loader must handle

1. **snake_case → PascalCase** on every field. Key remaps:
   - `line_total` → `TakeoffAmount`
   - `qty` → `TakeoffQuantity`
   - `unit_cost` → `TakeoffUnitPrice`
   - `escalation` → `EscalationPct`
   - `division_code` → resolve to `CustomDivisionId` (FK to `Divisions.Id`)
   - full table in `relationships.md`
2. **Slug → GUID resolution** for: `project_id`, `budget_level_id`
   (incl. the `parent_budget_level_id` self-reference), `division_code`, and
   comparable-project `name`. Build the dictionary during load.
3. **`parking_options.scope`** (a JSON array) → serialize into the `ScopeJson`
   string column.
4. **`csi_label` / `source_sheet`** → columns `CsiLabel` / `SourceSheet` exist so
   no extracted data is dropped.
5. **Markup user FK** — set `UpdatedByUserId` = the seed user on every `Markups` row.

---

## Two judgment calls before fetching from the DB

- **`"Decatur / Rome"` vs `"Decatur"`** — `schema.md` documents the comparable name
  as `Decatur`; the workbook says `Decatur / Rome`. It loads either way (`NVARCHAR`,
  not a CHECK constraint), but an app filter on `"Decatur"` won't match. Pick one
  spelling and normalize in the extractor or the loader.
- **EF Core sync** — the app is **code-first (EF Core 8)**. These 9 new tables need
  matching `DbContext` entity classes, or EF will flag the DB as out of sync on the
  next migration. The SQL is the source of truth for *seeding*; the entities are the
  source of truth for the *app* — keep them in agreement.

---

## Still missing (needs a separate source — not in this workbook)

- **Bidders / Proposals / TradePackages** + the `TradePackages.GroupKeys` join glue
  (the bid-picker feature). The `Risk` sheet names subs (Northstar, JMAC, NRC,
  Gilmore…) but carries no structured multi-bidder leveling.
- **Robindale 215 (L2)** — the second seed project.

---

## Regenerating the data

```
pip install openpyxl
python extract_full.py        # re-reads the Excel, rewrites data/*.json, revalidates
```

`extract_full.py` is marker-driven (scans column-A labels), so it survives row
inserts/deletes between budget versions. The level/sub-level mapping is an editable
table at the top of the script (`BUDGET_SHEETS`) — sub-levels are expected to vary
per project (e.g. a 2.1 and a 2.3 with no 2.2); edit and re-run to re-key.
