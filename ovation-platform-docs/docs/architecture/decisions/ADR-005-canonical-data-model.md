# ADR-005 — Canonical Data Model

**Status:** Accepted (2026-06-17)
**Context owner:** Platform / Edgar
**Related:** [target-architecture.md](../target-architecture.md), [schema.md](../../database/schema.md)

## Context

The repo contained two incompatible data models:

- **Schema A** — `docs/database/schema.md` plus the seed JSONs in `jsons/`. PascalCase, `UNIQUEIDENTIFIER` + `INT IDENTITY` keys. Faithful to the West Henderson L3 prototype: `BudgetLevels` with sub-level revisions, a flat seeded `LineItems` master + `BudgetLevelLineItems`, `TradePackages`/`Proposals`/`GroupKey` bid leveling, a 7-kind `Markups` table, and `BudgetApprovals` with SHA-256 snapshot.
- **Schema B** — `schemas/estimation_assistant.dbml`, `Ovation_Estimation_Assistant_Schema.sql`, `Data_Model_Analysis.md`. All-GUID `nvarchar(36)`. An estimation-focused model: `Scenarios`, self-referencing hierarchical `LineItems`, `TakeoffItems`, denormalized `BudgetSummary`, `BudgetComparisons`, `HistoricalProjects`. No `group_key` bid leveling, no `Markups` table, no approval snapshot.

Every doc, the prototype (the agreed behavior spec), the feature gates, and the seed JSONs assume Schema A. Schema B was the file actively being edited, creating a fork the team cannot build across.

## Decision

**Schema A is canonical.** Schema B is retired as a core model and archived to `schemas/_archive/`. Its genuinely useful concepts are salvaged on a defined timeline (see `target-architecture.md` §3): `BudgetSummary` (H1), `Scenarios` + `BudgetComparisons` (H2), `HistoricalProjects` corpus (H3).

## Consequences

- **Positive:** preserves the prototype's hardest, highest-value logic (bid allocation by `group_key`, the markup base-exclusion engine, immutable approval snapshots) instead of re-deriving it. Seed JSONs and all current docs stay valid.
- **Positive:** the estimation/AI ambition behind Schema B is not lost — it is sequenced as a later analytics tier on clean reference data.
- **Negative / cost:** the `.sql` work invested in Schema B is paused. Mitigated by the salvage list, so the design thinking is reused rather than discarded.
- **Follow-up:** repoint `OPENAI_README` (which references the now-removed `data_base_schema.dbml`) and the project memory note to `docs/database/schema.md`.
