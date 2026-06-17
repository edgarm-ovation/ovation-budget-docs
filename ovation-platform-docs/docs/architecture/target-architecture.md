# Target Architecture — 8 Weeks to 10 Years

**Status:** `[DRAFT — for owner + manager ratification]`
**Last reviewed:** 2026-06-17
**Supersedes ambiguity in:** [system-overview.md](./system-overview.md), [schemas/Data_Model_Analysis.md](../../schemas/Data_Model_Analysis.md)
**Decision record:** [ADR-005 — Canonical Data Model](./decisions/ADR-005-canonical-data-model.md)

This document is the single authority for how the Ovation Budget Platform is structured, from the 8-week demo through a 10-year horizon. It ratifies three decisions, resolves the discrepancies found in the two readiness reviews, and defines the invariants that let the same codebase grow without a rewrite.

---

## 1. Ratified Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | **Schema A (`docs/database/schema.md`) is the canonical data model.** | It is faithful to the manager's West Henderson prototype (the agreed behavior spec), carries the high-value logic — `group_key` bid leveling, the 7-kind `Markups` table, SHA-256 `BudgetApprovals` snapshots — and the seed JSONs already target it. |
| D2 | **Schema B (`estimation_assistant.dbml` / `.sql`) is retired as a core model; its ideas are salvaged for the analytics/AI tier.** | Schema B drops bid leveling, markups, and approval snapshots — building on it would mean re-deriving the prototype's hardest logic. But its `Scenarios`, denormalized `BudgetSummary`, `BudgetComparisons`, and `HistoricalProjects/Comparables` are the right shape for later reporting and estimation. See §3. |
| D3 | **`OrgId` ships on root tables from day one, defaulting to a single Ovation tenant.** | A 10-year horizon includes possible affiliated-company / Beckley Group partner use. Adding a tenant key to every table later is a flagged "significant migration." A nullable/defaulted column now is nearly free and removes that risk. No tenant-isolation UI is built yet. |
| D4 | **AI-assisted estimation is not actively designed now, but not foreclosed.** | Cost data is kept clean and queryable (reference data normalized, comparables first-class) so an estimation engine can be added later without restructuring. Decision to build it is deferred. |

---

## 2. Layered Architecture

The platform is a **modular monolith**: one deployable .NET API internally organized into clear layers and feature modules. This is deliberate — a well-structured monolith carries the team for years; services are extracted only when a specific seam demands it (§6, Horizon 3).

```
┌──────────────────────────────────────────────────────────────┐
│  Next.js 14 (App Router) — TypeScript, Tailwind, shadcn/ui     │
│  TanStack Table (budget grid) · TanStack Query (server state)  │
│  Zustand (unsaved edits / selections) · SignalR client         │
│  Computes PREVIEW totals only — never the source of truth      │
└───────────────────────────┬──────────────────────────────────┘
                            │  HTTPS / REST (JSON), Bearer (Entra ID)
                            │  Versioned: /api/v1/...
┌───────────────────────────▼──────────────────────────────────┐
│  .NET 8 Web API — Modular Monolith                             │
│                                                                │
│  Endpoints (Minimal API)  →  thin, validation + routing only   │
│  Services (business logic) →  FormulaService is the CANONICAL  │
│       FormulaService · ApprovalService · FileParserService     │
│       BidLevelingService · NotificationService · AuditService  │
│  Domain (entities, rules) →  pure, no infrastructure deps      │
│  Data (EF Core 8)         →  OvationDbContext, migrations       │
│                                                                │
│  Cross-cutting: Auth (Entra ID JWT) · RBAC · Audit · Tenancy   │
│  Escape hatches: IHostedService(jobs) · SignalR(realtime)      │
└──────┬───────────────────┬───────────────────┬────────────────┘
       │                   │                   │
┌──────▼──────┐   ┌────────▼────────┐   ┌──────▼──────────┐
│  Azure SQL  │   │ Azure Blob Stg  │   │ Azure Comms Svc │
│ (structured │   │ (uploads, PDFs, │   │ (email alerts)  │
│  records)   │   │  exports, sigs) │   └─────────────────┘
└─────────────┘   └─────────────────┘
       ▲
       │  (deferred — Horizon 2+, behind interfaces today)
┌──────┴──────────────────────────────────────────────────┐
│  Redis cache · Read replica · Service Bus · AI Search     │
└───────────────────────────────────────────────────────────┘
```

---

## 3. Disposition of Schema B (what to keep, when)

Schema B is not deleted blindly — it is reduced to a salvage list and the active `.sql` work is stopped.

| Schema B concept | Verdict | Where it lands |
|---|---|---|
| `Scenarios` / `ScenarioBudgets` | **Salvage — Horizon 2** | Multiple budget scenarios per project (phasing, alt unit mixes). Add as a layer above `BudgetLevels` when multi-scenario is requested. |
| `BudgetSummary` (denormalized totals) | **Salvage — Horizon 1** | A materialized summary per budget level for fast dashboards/reporting. The `FormulaService` writes it on save. |
| `BudgetComparisons` (level-to-level variance) | **Salvage — Horizon 2** | Powers cross-level trend reporting. Schema A's `BaselineAmount` already captures the underlying data. |
| `HistoricalProjects` / `HistoricalCosts` | **Salvage — Horizon 3** | The clean cost corpus an estimation engine would learn from. Schema A's `ComparableProjects` / `ComparableProjectCosts` cover the demo need today. |
| Self-referencing `LineItems` hierarchy | **Reject** | Schema A's flat master list + `BudgetLevelLineItems` is simpler and matches the prototype. |
| `Proposals` (trade-scope string, no group_key) | **Reject** | Loses bid-leveling fidelity. Schema A's `TradePackages` + `Proposals` + `GroupKey` is canonical. |
| All-GUID `nvarchar(36)` keys | **Reject** | Use Schema A's `UNIQUEIDENTIFIER` + `INT IDENTITY` for seeded/high-volume tables. |

**Action:** move `estimation_assistant.dbml`, `Ovation_Estimation_Assistant_Schema.sql`, and `Data_Model_Analysis.md` into `schemas/_archive/` with a README pointing here, so the salvage list survives but no one builds against them by accident.

---

## 4. Multi-Tenancy (D3) — concrete shape

- Add `OrgId UNIQUEIDENTIFIER NOT NULL DEFAULT '<ovation-org-guid>'` to the **root** tables only: `Projects`, `Users`, `Bidders`, `ComparableProjects`. Child rows inherit tenancy through their parent — no need to stamp every table.
- Seed a single `Organizations` row (`Ovation`). One extra table, one column per root entity.
- All queries filter by `OrgId` through a single EF Core global query filter wired to the authenticated user's org — so tenant scoping is enforced in one place, not per query.
- **Not built now:** per-tenant branding, tenant admin UI, row-level security policies. Those are Horizon 4 if partner onboarding becomes real.

This is the cheapest possible hedge: if Ovation never goes multi-tenant, the column sits at one value and costs nothing. If a partner onboards in Year 3, the painful part is already done.

---

## 5. Architectural Invariants (the things that must never break)

These are why the 8-week build and the 10-year platform can be the same codebase:

1. **The server is the financial source of truth.** `FormulaService` computes all canonical totals on save. The frontend may compute preview totals for instant feedback, but saved values and approval hashes use server output only. *(Resolves the formula-ownership conflict from both reviews.)*
2. **Approved budgets are immutable.** Approval writes a SHA-256 hash over a canonical snapshot to `BudgetApprovals` and sets the level `Locked`. Changes start a new sub-level. Never mutate a locked level.
3. **Audit is append-only.** Every budget-critical field change writes to `AuditLog` (who/what/when/old/new). Never updated, never deleted.
4. **The API is versioned (`/api/v1`).** Breaking changes go to `/v2`; old clients keep working. Non-negotiable for a 10-year client surface.
5. **Reference data is separated from transactional data.** `Divisions`, `LineItems`, `Bidders`, `ComparableProjects` are seeded reference; projects copy from them. Keeps the cost corpus clean (and AI-ready per D4).
6. **Structured data in SQL, files in Blob.** Never store file bytes in SQL; never store financial records only in a file.
7. **Business logic lives in Services, never in endpoints or the frontend.** Endpoints validate and route. This is the seam that lets a module become a service later (§6) without rewriting callers.
8. **Escape hatches are documented, not pre-built.** `IHostedService`→Service Bus, in-proc SignalR→Azure SignalR Service, SQL `LIKE`→AI Search. Build the simple version; know the upgrade is a config-level change.

---

## 6. Ten-Year Scaling Horizons

Extends the existing 3-phase plan ([scaling/README.md](../../scaling/README.md)) into a full horizon map. Each horizon has a trigger, not a fixed date — we move when the trigger fires.

| Horizon | Trigger | Scope | Infra | Key architecture move |
|---|---|---|---|---|
| **H0 — Demo** (Wk 1–8) | Now | West Henderson L3 + Robindale L2 vertical slice | App Service B2, Static Web Apps, Azure SQL GP 2-vCore, Blob LRS | Schema A subset, single-tenant, monolith, deploy-to-prod-from-main |
| **H1 — Growth** (Mo 3–6) | Demo approved | All active projects; full feature set; L0/L1 entry | Scale to S2 / 4-vCore; staging slot; App Insights; CDN | Add `BudgetSummary` materialization; automated tests on formula/parser/approval; CI gates |
| **H2 — Maturity** (Yr 1–2) | All projects live; leadership wants history + reporting | Reporting dashboards, historical archive, project templates, user-mgmt UI | P2 tier; Business Critical SQL; read replica; geo-replication; Redis if needed | Add `Scenarios` + `BudgetComparisons`; partition `AuditLog` by month; activate `OrgId` if a partner onboards |
| **H3 — Extensibility** (Yr 2–5) | Integration / volume pressure | Accounting/ERP integration (e.g. Sage, Yardi, Procore); bulk import; richer analytics | Service Bus + Functions for file/job volume; AI Search for cross-project search | Extract **FileParser** and/or **FormulaEngine** to services *only if* a real seam demands it; event-driven audit. AI estimation engine **if greenlit (D4)** — built on the salvaged `HistoricalProjects` corpus |
| **H4 — Ecosystem** (Yr 5–10) | Partner/SaaS demand; analytics scale | Multi-tenant partner access; data warehouse/lakehouse; partner API platform | Azure SignalR Service; full geo-redundancy; reserved instances; warehouse (Fabric/Synapse) | Activate full tenant isolation (RLS, per-tenant config); separate OLAP from OLTP; public API surface on `/v2` |

**Scaling principles (unchanged, restated):** scale the database last; monolith until a seam genuinely demands a service; don't build H3 infra in H0; leave escape hatches; write down every accepted shortcut as tech debt with a horizon target.

---

## 7. Resolution of the Smaller Discrepancies

These were flagged across both reviews and the README; this is the ruling for each so the team stops re-debating them.

| Discrepancy | Resolution |
|---|---|
| PostgreSQL vs Azure SQL | **Azure SQL**, everywhere. `system-overview.md` already corrected; no Postgres references remain valid. |
| Markups: 5 visible (prototype panel) vs 7 (schema) | Schema keeps all 7. **General Requirements and Bid Risk are computed and shown read-only** in the L3 markup panel; the other 5 are editable. Document in `formula-engine.md`. |
| Group-level bid override contract | Lives on **`BudgetLevelLineItems.SelectedProposalId`** (already in Schema A), keyed by `GroupKey`. No separate `BidSelections` table for the demo. |
| Summary-sheet persistence too thin | Use `ProposalLineItems` (section/label/amount) + `TradeHistoricalBenchmarks`; add bidder-column + winner/proposed marker fields in H1 if the demo exposes gaps. |
| Approval package richer than API | API must add: included-sections checklist, certificate PDF generation, full-package export, snapshot download, version naming. Spec before building the approval module. |
| File import unspecified | Highest-risk feature. Complete `files.md`, `file-parser.md`, `background-jobs.md`, `azure-blob.md` before H0 Week 4. Support one known format first. |
| Seed data underdocumented | Complete `seed-data.md` (West Henderson L3 + Robindale L2) — gates the whole demo. |
| Docs marked `[STUB]` with real content | Bulk status pass to `[DRAFT]`/`[COMPLETE]`. |
| ADR files referenced but missing (`decisions/ADR-002..004`) | Create the `decisions/` folder; backfill the ADRs that are referenced. ADR-005 (this schema decision) is the first written. |
| `OPENAI_README` points to `data_base_schema.dbml` (gone) | Repoint to `docs/database/schema.md` once Schema B is archived. |

---

## 8. Immediate Next Actions (to make the architecture real)

1. Ratify D1–D4 with the manager/owner (this doc).
2. Archive Schema B → `schemas/_archive/` with a pointer README (§3 action).
3. Repoint `OPENAI_README` and the memory schema-mapping note to `docs/database/schema.md`.
4. Create `docs/architecture/decisions/` and write ADR-005 (done alongside this doc).
5. Add `OrgId` + `Organizations` to `schema.md` (D3 shape, §4).
6. Add the formula-ownership and markup-visibility rulings to `formula-engine.md`.
7. Complete the four P0 file-import docs and `seed-data.md` before Week 4.

---

## Cross-Functional Flags

- **Finance / CFO (Heather Grech):** the immutability + append-only audit + SHA-256 approval invariants (§5.2–5.3) are what make this defensible for lender/ownership review packages. Worth a sign-off that the approval snapshot contents meet finance's audit needs before H0 Week 6.
- **Construction Ops (Lloyd Hoppel) / Development (Armen Hadjimanoukian):** the canonical-schema decision (D1) preserves the West Henderson bid-leveling workflow exactly as prototyped — confirm the 7-vs-5 markup ruling (§7) matches how estimators actually work the panel.
- **Partner exposure (Beckley Group):** D3 (tenancy hedge) is driven by the *possibility* of partner use. If partner access is explicitly off the table for 10 years, D3 can be downgraded and §4 skipped — worth a one-line confirmation.
- **AI direction:** D4 leaves AI-assisted estimation open. If leadership wants it as a stated goal, it promotes from "don't foreclose" to an H3 deliverable with the `HistoricalProjects` corpus built earlier (H2 instead of H3).
