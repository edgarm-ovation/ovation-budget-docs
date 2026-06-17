# Manager Alignment Review

**Status:** `[DRAFT]`  
**Reviewed against:** West Henderson L3 prototype v94 and Ovation Budget Levels App  
**Date:** 2026-06-16

---

## Executive Summary

The docs are directionally aligned with the manager's idea: an internal Ovation budget platform that replaces Excel, tracks L0-L3 budget levels, supports West Henderson L3 bid leveling, keeps L2/L3 comparisons visible, manages markups, handles approvals, and exports stakeholder-ready reports.

Clarification from the team: Azure is the persistence direction. Structured app data should be stored in Azure SQL, while uploaded files, renderings, approval packages, and generated exports should be stored in Azure Blob Storage. West Henderson and Robindale are example/seed datasets for proving the app, not the full long-term project scope.

The strongest alignment is in:

- Product vision and 8-week demo scope.
- L0-L3 definitions and workflow.
- West Henderson L3 UI patterns.
- Core database schema for projects, budget levels, line items, markups, trades, proposals, takeoffs, approvals, audit, uploads, and notifications.
- Frontend route/component direction.

The main risk is not the concept. The risk is that several files still say `[STUB]` even when they contain important content, and several high-risk implementation specs are missing or incomplete. Before building, the team should close the gaps below.

---

## What Matches The Manager's Prototype

### West Henderson L3 UI

The docs capture the prototype's main UI structure:

- Fixed left sidebar and scrollable main content.
- Dashboard, renderings, awarded trades, master budget, proposal L3 budget, significant changes, approval, benchmark, takeoffs, and trade views.
- KPI card row, panels, status pills, modals, bid cell buttons, summary sheet modal, takeoff layouts, and print/report behavior.
- The `groupKey` concept as the core bid-mapping unit.
- L2 locked baseline compared against L3 selected bids and recommended adjustments.

Source doc: `docs/frontend/ui-patterns.md`

### Budget Level Concept

The docs match the Budget Levels reference app at a high level:

- L0: pre-schematic / conceptual ROM.
- L1: schematic design.
- L2: design development with detailed takeoffs, soft bids, markups, approval.
- L3: construction documents with hard proposals, bid leveling, takeoff backup, and final approval.

Source doc: `product/budget-levels.md`

### Core Product Scope

The docs correctly describe:

- Budget level management.
- Bid leveling.
- File import.
- Formula engine.
- Approval workflow.
- Real-time collaboration.
- Audit trail.
- Export.
- Notifications.

Source docs: `product/overview.md`, `product/roadmap-8-weeks.md`

### Data Model

The schema covers most prototype requirements:

- Projects, unit mix, parking.
- Budget levels and sub-level revisions.
- Master line item library plus per-budget-level line items.
- Markups.
- Trade packages, bidders, proposals, proposal line items.
- Takeoffs, takeoff configs, takeoff plans.
- Historical trade benchmarks.
- Budget approvals with SHA-256 hash and snapshot JSON.
- Uploaded files, notifications, audit log.

Source docs: `docs/database/schema.md`, `schemas/data_base_schema.dbml`

---

## Gaps To Fix Before Build

### 1. Important Docs Are Marked As Stubs

Many docs contain real implementation content but still have `Status: [STUB]`. This makes the repo look less ready than it is and can confuse the team about what is authoritative.

Update statuses for at least:

- `docs/api/projects.md`
- `docs/api/line-items.md`
- `docs/api/markups.md`
- `docs/api/trades.md`
- `docs/api/budget.md`
- `docs/api/approval.md`
- `docs/api/reference.md`
- `docs/architecture/system-overview.md`
- `docs/backend/formula-engine.md`
- `docs/frontend/folder-structure.md`
- `product/budget-levels.md`

Keep true stubs as stubs.

### 2. API Index References Need Ongoing Link Checks

`docs/api/README.md` previously linked to missing files:

- `budget-levels-api.md`, but the repo has `budget-levels.md`.
- `takeoffs.md`, but takeoff endpoints are currently inside `budget.md`.

Those links have been corrected to point to existing docs. Keep checking this index whenever new API docs are added or split out.

### 3. Azure Persistence Needs To Stay Consistent

`docs/architecture/system-overview.md` previously said PostgreSQL 15+, while the rest of the repo says Azure SQL via EF Core 8.

Use Azure SQL consistently for structured data because it matches:

- `docs/database/schema.md`
- `schemas/data_base_schema.dbml`
- `docs/backend/tech-stack.md`
- `scaling/README.md`
- `OPENAI_README.md`

Use Azure Blob Storage for uploaded budget files, renderings, generated approval packages, and PDF/Excel exports.

### 4. Markup Model Needs One Clear Rule

The prototype's visible Markup Controls panel edits 5 rows:

- Sub Bonds
- GL Insurance
- Construction Contingency
- Contractor Fee
- Overhead

The backend/docs model defines 7 markups:

- General Requirements
- Bid Risk
- Construction Contingency
- Sub Bonds
- GL Insurance
- Overhead
- Contractor Fee

This can work, but the docs should explicitly state:

- General Requirements and Bid Risk are computed/managed outside the visible L3 markup controls, or
- they should also be editable in the app.

Right now this is implied, not cleanly decided.

### 5. Formula Engine Conflicts With Prototype Behavior

The backend doc says the frontend never computes totals. The West Henderson prototype computes totals live in the browser for interactivity.

Recommended implementation rule:

- API is the financial source of truth.
- Frontend may compute temporary preview totals for instant UI feedback.
- Saved values and approval hashes must use server-calculated canonical totals.

Add this to `docs/backend/formula-engine.md` and `docs/frontend/state-management.md`.

### 6. Bid Picker Needs A Backend Contract

The prototype's bid picker supports per-`groupKey` selection and can use cost-code-aware summary sheet amounts. The current API mostly awards at the trade level.

Add an endpoint or extend the trade API for group-level bid overrides:

- `groupKey`
- selected proposal/bidder
- status: proposed / awarded
- pricing tier if applicable
- amount source: summary-sheet scoped amount vs fallback total

Without this, the most distinctive part of the manager's UI will not persist correctly.

### 7. Summary Sheet Data Model Is Too Thin

The prototype's summary sheet includes:

- Historical benchmark rows.
- Scope rows.
- Multiple bidder columns.
- Winner/proposed styling.
- Budget variance row.
- Optional price per SF and locked pricing rows.
- Notes.

The current schema has proposal line items and historical benchmarks, but not enough structure for the exact summary sheet behavior.

Add fields/tables for:

- Summary sheet row type.
- `groupKey` per scope row.
- bidder-column values per scope row.
- optional pricing tier labels.
- winner/current/proposed marker.

### 8. File Import Is In Scope But Not Specified

File upload/import is a must-have in the roadmap, but both API and backend parser docs are stubs:

- `docs/api/files.md`
- `docs/backend/file-parser.md`
- `docs/backend/background-jobs.md`
- `docs/integrations/azure-blob.md`

These need to be completed before development starts. Minimum spec:

- Upload endpoint.
- Async parse job status.
- Supported file types.
- Auto-mapping rules.
- Manual mapping schema.
- Error handling.
- How parsed rows map to line items, proposals, takeoffs, or trade summary sheets.

### 9. Approval UX Is Richer Than The API

The prototype approval tab supports:

- Include checklist.
- Live SHA-256 hash.
- Signature canvas.
- Approval history.
- Full package print.
- Certificate PDF.
- Snapshot JSON download.

The approval API covers hash, signature, snapshot, and approve/reject, but does not fully specify:

- included sections checklist,
- certificate generation,
- full package generation,
- snapshot download,
- version naming for approval records.

Add this to `docs/api/approval.md` and `docs/database/schema.md`.

### 10. Example Seed Data Is Critical But Underdocumented

The demo depends on realistic example data from West Henderson L3 and Robindale L2. `docs/database/seed-data.md` is still a stub.

Define:

- West Henderson project header values.
- West Henderson L2 locked baseline.
- West Henderson L3 trades/proposals/takeoffs/renderings.
- Robindale L2 dataset shape.
- comparable projects.
- line item template list.
- default markups.

---

## Suggested Build Priority

1. Clean up status labels and broken links.
2. Keep Azure SQL and Azure Blob Storage decisions consistent across docs.
3. Complete file import specs.
4. Complete group-level bid override API.
5. Complete summary sheet schema/API.
6. Clarify markup editability and calculation rules.
7. Finish approval package/snapshot API.
8. Write seed data spec.
9. Convert 8-week roadmap into sprint tickets.
10. Build a thin vertical slice for West Henderson L3:
   project dashboard -> master budget -> bid picker -> proposal adjustments -> approval snapshot.

---

## Readiness Assessment

| Area | Status | Notes |
|---|---|---|
| Product vision | Good | Clear and aligned. |
| Manager UI match | Good | `ui-patterns.md` captures the prototype well. |
| Budget levels | Good | Needs status update from stub. |
| Database schema | Good | Mostly covers core domain. |
| API docs | Partial | Several real docs marked stub; broken links exist. |
| Frontend plan | Partial | Strong route/component direction; missing state-management details. |
| File import | Not ready | Must-have feature but docs are stubs. |
| Summary sheets | Partial | UI captured; backend persistence needs more detail. |
| Approval lock/package | Partial | Core flow exists; package/certificate/checklist gaps remain. |
| Seed data | Not ready | Critical for demo. |

---

## Bottom Line

The project is on the right track. The docs understand what the manager wants, especially the West Henderson L3 workflow and the L0-L3 budget philosophy.

Before implementation starts, the team should tighten the incomplete specs above. The highest-risk gaps are file import, group-level bid selection, summary sheet persistence, approval package generation, and seed data. Those are the features most likely to expose a mismatch between the prototype and the real app if left vague.
