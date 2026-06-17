# Ovation Budget Platform - Project Overview

**Purpose:** Internal reference summary for planning, reviews, and AI-assisted work on the Ovation Construction Budget Management Platform.

---

## Project Summary

The Ovation Budget Platform is an internal web application for managing construction budgets from early concept through final construction-document pricing. It replaces manually maintained Excel files with a centralized, multi-user system for budget levels, bid leveling, file import, approvals, audit history, and exports.

The first demo uses two real Ovation example datasets:

- **West Henderson Apartments** - Level 3 construction-document budget with bid/proposal workflows.
- **Robindale 215** - Level 2 design-development budget.

These are seed/demo examples for proving the workflow. The long-term product is intended to support all active Ovation projects, then historical archive and reporting.

For the current gap review, see [`product/foundation-readiness-review.md`](product/foundation-readiness-review.md). That file tracks missing docs, flexibility requirements, tech-stack assumptions, and weekly review gates for the 8-week build.

---

## Core Product Goals

- Track budget levels from **L0 through L3**.
- Preserve every approved budget level as an immutable snapshot.
- Compare L2 baseline budgets against L3 proposals and takeoffs.
- Support bid leveling by trade, bidder, proposal, and `groupKey`.
- Upload and parse Excel/CSV files from estimators and subcontractors.
- Calculate hard costs, general requirements, bid risk, contingency, bonds, insurance, overhead, contractor fee, cost per unit, and cost per GSF.
- Support review, approval, rejection, lock state, signature, SHA-256 snapshot hash, and approval history.
- Export budgets and approval packages for ownership, lenders, and internal review.
- Store structured data in Azure SQL and uploaded/generated files in Azure Blob Storage.

---

## Architecture Direction

| Area | Direction |
|---|---|
| Frontend | Next.js 14 App Router, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | .NET 8 Web API, EF Core, SignalR |
| Database | Azure SQL as the structured system of record |
| File storage | Azure Blob Storage for uploads, renderings, approval packages, PDF/Excel exports |
| Auth | Azure AD / Microsoft Entra ID, role-based access |
| Email | Azure Communication Services |
| Real-time updates | SignalR for collaboration and file-processing progress |

---

## Main Users

| Role | Primary Work |
|---|---|
| Estimator | Build and edit budgets, upload files, manage line items, submit for approval |
| Manager / Approver | Review budgets, approve/reject, lock final versions |
| Admin | Manage users, roles, reference data, and project setup |
| Viewer | Read-only access for finance, ownership, and reporting |

---

## Budget Levels

| Level | Name | Purpose | Demo Scope |
|---|---|---|---|
| L0 | Pre-Schematic / Conceptual | Rough order-of-magnitude feasibility budget | Display/reference only for demo |
| L1 | Schematic Design | Early project baseline based on schematic design and historical data | Display/reference only for demo |
| L2 | Design Development | Detailed budget using DD plans, comparable costs, soft bids, and takeoffs | Full workflow for Robindale example |
| L3 | Construction Documents | Bid/proposal-based final pre-construction budget | Full workflow for West Henderson example |

---

## 8-Week Demo Roadmap

### Weeks 1-2: Foundation

**Goal:** Establish the working app skeleton and core data model.

- Create Next.js frontend and .NET 8 API projects.
- Configure Azure AD authentication and role checks.
- Set up Azure SQL and EF Core models.
- Define projects, budget levels, line items, markups, trades, proposals, takeoffs, approvals, files, notifications, and audit tables.
- Build project list, budget level navigation, and first budget table shell.
- Prepare seed-data templates for West Henderson and Robindale.
- Validate Azure deployment path.

**Review gate:** Confirm architecture matches Azure direction, data model supports West Henderson L3 UI, and no old PostgreSQL/database assumptions remain.

### Weeks 3-4: Budget Editing, Bids, And Import

**Goal:** Make the budget workflow feel real with editable data and file ingestion.

- Build expandable division and line-item budget tables.
- Add inline editing for quantities, unit prices, notes, source, category, and adjustments.
- Build bid picker behavior for selected bids and awarded/proposed status.
- Add Excel/CSV upload to Azure Blob Storage.
- Create file parse records in Azure SQL.
- Implement common auto-mapping rules and manual field mapping fallback.
- Save imported rows into line items, proposals, takeoffs, or staging records.
- Add budget summary cards and live recalculation after edits.

**Review gate:** Test at least one standard file and one non-standard file. Confirm group-level bid selection persists correctly.

### Weeks 5-6: Approval, Export, And Notifications

**Goal:** Complete the end-to-end approval story.

- Build submit, approve, reject, and lock workflows.
- Add reviewer comments and approval history.
- Generate canonical server-side budget snapshot.
- Store SHA-256 hash, signature image, snapshot JSON, and approval metadata.
- Add in-app notifications and email alerts.
- Export budget data to Excel.
- Add variance summary or chart.

**Review gate:** Confirm locked budgets cannot be edited, approval snapshots are repeatable, and exported totals match the server formula engine.

### Weeks 7-8: Demo Polish And Dry Run

**Goal:** Prepare a clean ownership-ready demo.

- Refine UI to follow the West Henderson prototype patterns.
- Validate West Henderson and Robindale seed data.
- Fix workflow bugs found during testing.
- Add demo notes and a 20-minute runbook.
- Run a full dry run: login, open projects, edit budget, choose bid, import file, approve, export.

**Review gate:** Demo can run end-to-end without blocking bugs and with clear talking points.

---

## 6-Month Roadmap

### Months 1-2: Demo Foundation

Deliver the 8-week stakeholder demo.

- Azure-hosted frontend and backend.
- Azure AD login.
- West Henderson and Robindale seed datasets.
- Core budget table and bid leveling.
- File upload and import.
- Markup formula engine.
- Approval workflow.
- Export and variance summary.

### Months 3-4: Growth

Expand from demo to broader internal use.

- Migrate additional active Ovation projects.
- Add full L0 and L1 data entry flows.
- Improve group-level bid overrides and summary sheet persistence.
- Add bulk file import.
- Add cross-project benchmarking.
- Add real-time conflict detection.
- Improve mobile/tablet responsiveness.
- Add staging deployment slot and stronger monitoring.
- Start automated tests for formula engine, file parser, approval workflow, and key API endpoints.

### Months 5-6: Production Hardening

Make the platform ready for daily team use.

- Historical project archive.
- Advanced reporting and cross-project dashboards.
- PDF approval packages and audit exports.
- User management UI.
- Project templates.
- Verified backups and disaster recovery runbook.
- Security review for roles, financial data, and file access.
- Azure SQL performance tuning and indexing.
- Production support process and incident response docs.

---

## Current Known Discrepancies To Review

These are not blockers to writing docs, but they should be resolved before or during implementation.

| Area | Discrepancy / Risk | Recommended Action |
|---|---|---|
| Document statuses | Several files with real content still say `[STUB]` | Update statuses to `[DRAFT]` or `[COMPLETE]` after review |
| API index | Link mismatch was found and corrected; takeoff docs currently live in `budget.md` | Keep checking links when new API docs are added |
| File import | File API, parser, background job, and Azure Blob docs are mostly empty | Fill these before building upload/import |
| Seed data | West Henderson and Robindale data strategy is not fully documented | Complete `docs/database/seed-data.md` |
| Bid picker | Prototype supports per-`groupKey` bid selection; API is more trade-level | Add group-level bid override contract |
| Summary sheets | Prototype summary sheets are richer than current schema | Add schema/API for summary rows, bidder values, tiers, and group keys |
| Approval package | Prototype includes checklist, certificate, full package, and snapshot download | Extend approval API/schema docs |
| Formula ownership | Prototype computes live totals client-side; backend docs say server only | Use API as source of truth, allow frontend preview only |
| Roles | User-role docs are still stubbed | Define Estimator, Manager/Approver, Admin, Viewer permissions |
| Azure integrations | Azure SQL, Blob, AD, and Communications docs are mostly stubs | Fill integration setup before deployment |

---

## Review Process

Use these reviews to keep the project on track and catch discrepancies early.

### Weekly Documentation Review

- Confirm roadmap tasks match current implementation priorities.
- Check that any changed API behavior is reflected in docs.
- Review newly completed docs and update `[STUB]`, `[DRAFT]`, or `[COMPLETE]`.
- Keep West Henderson and Robindale labeled as seed/demo examples.

### Feature Readiness Review

Before implementation starts on a feature, confirm:

- User workflow is described.
- API contract exists.
- Database persistence is clear.
- Azure storage needs are defined.
- Permissions are defined.
- Edge cases and validation rules are listed.

### Demo Readiness Review

Before stakeholder demo, confirm:

- West Henderson L3 workflow runs end to end.
- Robindale L2 workflow loads correctly.
- Totals match formula engine outputs.
- Approval lock prevents edits.
- Exports open and contain expected data.
- Demo script fits within 20 minutes.

### 6-Month Production Review

Before production rollout, confirm:

- Active project migration plan exists.
- Backup and restore process is tested.
- Security and role permissions are reviewed.
- Audit trail and approval snapshots are immutable.
- Monitoring, incident response, and deployment process are documented.

---

## Key Source Docs

- `product/overview.md` - product vision and scope.
- `product/budget-levels.md` - L0-L3 definitions.
- `product/roadmap-8-weeks.md` - detailed 8-week demo plan.
- `product/roadmap.md` - full product roadmap through production and scale.
- `product/manager-alignment-review.md` - current alignment and discrepancy review.
- `docs/frontend/ui-patterns.md` - West Henderson UI reference.
- `docs/database/schema.md` - Azure SQL schema.
- `schemas/data_base_schema.dbml` - DBML schema reference.
- `docs/architecture/system-overview.md` - system architecture.
- `docs/backend/formula-engine.md` - calculation rules.

---

## Open Questions

- Which uploaded file formats should be supported first: internal budget workbook, subcontractor proposal, takeoff sheet, or summary sheet?
- Should General Requirements and Bid Risk be editable in the UI, or computed/managed outside the visible L3 markup panel?
- Should group-level bid overrides live on `BudgetLevelLineItems`, a separate `BidSelections` table, or both?
- What exact fields from West Henderson and Robindale must be seeded for the first demo?
- Who are the named approvers for the approval workflow demo?

---

## Bottom Line

The project direction is solid: build the Azure-backed system, prove it with West Henderson and Robindale, then expand to all active projects and production hardening over 6 months.

The biggest items to review next are file import, seed data, group-level bid selection, summary sheet persistence, approval packages, and role permissions.
