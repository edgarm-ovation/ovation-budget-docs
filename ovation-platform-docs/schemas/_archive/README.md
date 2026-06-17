# Archived — Schema B (Estimation Assistant)

These files are the **retired** "Estimation Assistant" data model (Schema B). They are kept for reference only. **Do not build against them.**

Per [ADR-005](../../docs/architecture/decisions/ADR-005-canonical-data-model.md) and [target-architecture.md §3](../../docs/architecture/target-architecture.md), the canonical data model is **Schema A**, which lives at **[`docs/database/schema.md`](../../docs/database/schema.md)** (with the seed JSONs in [`jsons/`](../../jsons/)).

## Why retired

Schema B drops the prototype's hardest, highest-value logic: `group_key` bid leveling, the 7-kind `Markups` table, and SHA-256 approval snapshots. Building on it would mean re-deriving all of that. Schema A is faithful to the West Henderson prototype and is what every other doc, the seed JSONs, and the feature specs assume.

## Salvage list (these ideas come back later)

| Concept | Returns at |
|---|---|
| `BudgetSummary` (denormalized totals) | Horizon 1 |
| `Scenarios` + `BudgetComparisons` | Horizon 2 |
| `HistoricalProjects` / `HistoricalCosts` corpus | Horizon 3 (AI estimation, if greenlit) |

## Files

- `estimation_assistant.dbml`
- `Ovation_Estimation_Assistant_Schema.sql`
- `Data_Model_Analysis.md`
- `Quick_Reference_Schema.md`
- `Executive_Summary_Data_Schema.md`
