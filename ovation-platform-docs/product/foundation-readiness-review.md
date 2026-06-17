# Foundation Readiness Review

Status: Draft for owner and manager review  
Last reviewed: 2026-06-17  
Primary goal: confirm that the 8-week plan is honest, flexible, and aligned with the longer 6+ month product direction.

## Executive Summary

The current foundation is directionally correct. The docs describe the right product: a construction budget platform that starts from spreadsheet-style budget levels, bid proposals, takeoffs, and owner-facing approval packages, then moves toward a flexible system of record backed by Azure.

The biggest risk is not the mockup. The biggest risk is making the first build too rigid around the West Henderson example. The app needs to treat West Henderson and Robindale as seed/demo examples, not as the shape of the entire product. Budget divisions, line items, proposals, adjustments, markups, takeoffs, approval groups, and summary views all need to be configurable per project and persisted in the database.

For 8 weeks, the realistic target is a clean owner-ready mockup plus a working vertical slice. The vertical slice should prove that users can import or enter budget data, adjust it, select proposals, save changes to Azure SQL, and generate a simple owner-facing approval view. It should not promise a complete production estimating platform.

## Current Foundation Review

| Area | Current state | Readiness | Review notes |
| --- | --- | --- | --- |
| Product direction | Clear | Good | The docs correctly position the platform around budget levels, bids, takeoffs, approvals, and variance tracking. |
| UI reference | Clear | Good | West Henderson gives a strong visual direction: dense spreadsheet-style budget management with summary panels and proposal selection. |
| Mockups | In progress | Good for demo | There are mockup folders for owner/demo review. They need clean folder naming and clear README language that explains what is prototype vs working behavior. |
| Tech stack | Mostly defined | Good | Next.js, TypeScript, Tailwind, shadcn/ui, TanStack Table/Query, Zustand, .NET 8, EF Core, Azure SQL, Blob Storage, and Azure AD are a reasonable foundation. |
| Azure persistence | Intended | Needs detail | Azure SQL and Blob Storage are the right direction, but the docs need clearer save/update/import flows. |
| Data flexibility | Partially defined | Needs review | The database docs already include custom line items and proposal selection concepts, but edit/version/audit rules need to be made explicit. |
| File import | Stubbed | High risk | This is one of the largest unknowns. Spreadsheet import rules, column mapping, validation, staging, and error handling need early definition. |
| Roles and security | Stubbed | High risk | Owner, estimator, project manager, admin, and viewer permissions need definition before real data is used. |
| API contracts | Stubbed | Medium risk | Budget, files, users, and project APIs need at least draft request/response contracts before implementation. |
| Review cadence | Mentioned | Needs structure | Weekly discrepancy reviews should be formal so the team does not accidentally overpromise. |

## Tech Stack Recommendation

The proposed stack is suitable for the project:

| Layer | Recommended choice | Why it fits |
| --- | --- | --- |
| Frontend | Next.js, React, TypeScript | Good for a web app with dashboards, forms, tables, and future owner portals. |
| UI | Tailwind CSS, shadcn/ui | Fast to build clean operational UI without locking into a heavy design system. |
| Data tables | TanStack Table | Needed for spreadsheet-like budget interactions, sorting, grouping, and editable rows. |
| Server state | TanStack Query | Helps keep saved Azure data, loading states, and cache invalidation organized. |
| Local UI state | Zustand | Good for temporary edits, filters, selected proposals, unsaved changes, and review panels. |
| Backend | .NET 8 Minimal APIs | Strong fit for business rules, Azure integration, authentication, and structured API contracts. |
| ORM | EF Core | Good match for Azure SQL and migrations. |
| Database | Azure SQL | Correct choice for budget records, projects, users, audit history, approval snapshots, and proposal selections. |
| File storage | Azure Blob Storage | Correct choice for Excel/PDF uploads, proposal files, generated exports, and approval packets. |
| Auth | Microsoft Entra ID / Azure AD | Good enterprise direction, but the 8-week build should include a simple fallback plan if identity setup is delayed. |
| Realtime | SignalR | Useful later for import job progress and collaboration, but should be stretch scope for the first 8 weeks. |

Do not add extra infrastructure unless it directly supports the 8-week vertical slice. Redis, complex event buses, advanced reporting warehouses, and multi-tenant enterprise controls can wait unless a real requirement forces them earlier.

## Flexibility Requirements

The app should not be rigid. These are the minimum flexibility rules the foundation should support:

| Requirement | Needed by 8 weeks? | Notes |
| --- | --- | --- |
| Create and edit projects | Yes | Project name, location, owner, type, status, and basic metadata should be editable. |
| Edit budget line items | Yes | Description, division, category, quantity, unit, unit cost, total, notes, and source should be editable. |
| Add custom line items | Yes | Users must be able to add rows not found in the original spreadsheet. |
| Import spreadsheet data | Yes, limited | Support one or two known formats first, with a manual correction path. |
| Store imported source rows | Yes | Keep raw/staged import data so mismatches can be reviewed. |
| Select proposals/bids | Yes | Users should be able to choose a bid/proposal and save that decision. |
| Override values manually | Yes | Manual overrides need notes and audit history. |
| Group line items | Yes | Proposal groups, alternates, and related line items should not be hardcoded. |
| Configure markups/adjustments | Partial | Basic percentage and fixed adjustments should be supported. Full rule engines can wait. |
| Approval snapshots | Yes | Owner-facing approval views should be saved as a point-in-time snapshot. |
| Audit changes | Yes, basic | Track who changed what, when, and why for budget-critical fields. |
| Multi-project templates | Later | Useful for 6 months, but not required for the first vertical slice. |
| Advanced permissions | Later | Basic roles now; detailed field-level permissions later. |

## Data Model Items To Confirm

These questions should be answered before the first backend implementation sprint:

1. Are budget levels immutable snapshots after approval, or can they be revised with version history?
2. Can one line item belong to multiple owner approval groups, or only one?
3. How should alternates be represented: separate line items, proposal options, or approval package sections?
4. Are markups global to a budget level, specific to a division, or specific to a line item?
5. Does the app need to preserve original spreadsheet formulas, or only calculated results?
6. What fields are required before a budget level can be marked ready for owner review?
7. What is the source of truth when imported data conflicts with a manually edited value?
8. What should happen when a bid proposal is revised after it has already been selected?
9. Which values must be locked after an approval package is sent?
10. What data must be visible to the owner versus internal users only?

## Important Missing Documentation

These are the highest-priority gaps found in the docs:

| Priority | Missing or stubbed doc | Why it matters |
| --- | --- | --- |
| P0 | `docs/database/seed-data.md` | Defines the sample West Henderson and Robindale data that prove the app is flexible. |
| P0 | `docs/api/files.md` | Needed for upload, import, validation, storage, and generated export workflows. |
| P0 | `docs/backend/file-parser.md` | Spreadsheet import is one of the riskiest parts of the project. |
| P0 | `product/user-roles.md` | The team needs to know who can edit, approve, upload, view, and export. |
| P0 | `security/auth-and-roles.md` | Needed before Azure AD and owner-facing access are implemented. |
| P1 | `docs/frontend/state-management.md` | The app needs clear rules for unsaved edits, proposal selections, filters, and review mode. |
| P1 | `docs/api/budget-levels.md` | Budget create/update/approve/version APIs should be drafted before coding. |
| P1 | `docs/api/users.md` | Needed for role assignments and ownership. |
| P1 | `docs/integrations/azure-sql.md` | Should document environments, connection strategy, migrations, backups, and access control. |
| P1 | `docs/integrations/azure-blob.md` | Should document upload paths, file naming, retention, and permissions. |
| P2 | Sprint docs | Helpful for tracking what is actually delivered each week. |
| P2 | Mockup READMEs | Should clearly state what is working, simulated, and planned. |

## Mockup Review

The current mockup direction is useful for the owner meeting. The UI should continue to follow the West Henderson example: clean, dense, table-first, and focused on real budget review work.

Keep:

- Budget table as the primary experience.
- Project summary and approval status visible without feeling like a marketing page.
- Editable rows, proposal selection, adjustments, notes, and variance indicators.
- Clear separation between internal estimator controls and owner-facing review mode.

Improve before presenting:

- Use clean folder names without extra spaces, for example `ovation-platform-owner-demo-8-week` and `ovation-platform-mockup-openai`.
- Make README language explicit that the demo is a prototype unless connected to the backend.
- Avoid showing features as finished unless they are actually planned for the 8-week vertical slice.
- Add a short demo script: open project, review budget level, change a line item, select a bid, save, show approval view.

## Realistic 8-Week Plan

Assumption: 8 hours per day, 5 days per week. That equals about 320 hours per person. A one-person plan should be scoped tightly. A two-person plan can include more polish, but still needs weekly review gates.

### Week 1 - Foundation and Alignment

Deliverables:

- Finalize product scope for the 8-week demo.
- Clean mockup folder structure and README files.
- Complete seed data outline for West Henderson and Robindale.
- Confirm tech stack and development environments.
- Draft budget, file, project, and user API contracts.

Review gate:

- Confirm the demo does not promise full production behavior.
- Confirm West Henderson is a sample project, not hardcoded product logic.

### Week 2 - Database and Backend Skeleton

Deliverables:

- Azure SQL schema draft and EF Core migrations.
- Project, budget level, line item, proposal, file, user, and audit tables.
- Basic .NET API project with OpenAPI.
- Local development database seeded with sample data.

Review gate:

- Confirm custom line items, overrides, and proposal selections can be stored.

### Week 3 - Frontend App Shell and Budget Table

Deliverables:

- Next.js app shell with project dashboard.
- Budget level detail screen.
- Editable budget table with grouping, totals, filters, and unsaved-change state.
- Basic mock auth or local role switcher for demo.

Review gate:

- Confirm table structure matches manager expectations from West Henderson.

### Week 4 - Import and File Handling

Deliverables:

- Upload Excel/PDF files to Azure Blob or local equivalent for development.
- Parse one known spreadsheet format.
- Store imported rows in staging tables.
- Show validation errors and allow correction before committing.

Review gate:

- Confirm import scope is honest. This should support known examples first, not every possible spreadsheet.

### Week 5 - Bid/Proposal Selection and Adjustments

Deliverables:

- Proposal list and selected-bid workflow.
- Manual overrides with notes.
- Basic markups and adjustments.
- Recalculated totals saved to database.

Review gate:

- Confirm proposal selection and manual changes persist correctly.

### Week 6 - Approval View and Export

Deliverables:

- Owner-facing approval package view.
- Approval snapshot saved to database.
- Basic export to PDF or Excel.
- Internal notes hidden from owner view.

Review gate:

- Confirm owner view is clean, accurate, and not overloaded.

### Week 7 - Polish, Validation, and Demo Data

Deliverables:

- Clean UI states: loading, saving, validation, empty states, errors.
- Seed West Henderson and Robindale examples.
- Add basic audit history view.
- Tighten formulas and totals.

Review gate:

- Run discrepancy review against source spreadsheets and manager UI expectations.

### Week 8 - Demo Hardening and Handoff

Deliverables:

- Final owner demo mockup and working vertical slice.
- Demo script and talking points.
- Known limitations list.
- 6-month roadmap update based on what was learned.

Review gate:

- Owner review package is accurate, not overstated, and ready to present.

## What To Promise For 8 Weeks

Safe to promise if the team stays focused:

- Clean owner-facing mockup.
- Working budget level screen for sample projects.
- Editable line items and saved changes.
- Basic Azure SQL persistence.
- Basic file upload and limited spreadsheet import.
- Proposal selection and manual overrides.
- Approval snapshot view.
- Simple export.
- Clear review process and limitation list.

Do not promise for 8 weeks unless staffing is strong and requirements are stable:

- Perfect import for every spreadsheet format.
- Full accounting/ERP integration.
- Advanced permissions and external owner portal hardening.
- Real-time collaboration across multiple users.
- Full mobile estimating workflow.
- Automated bid leveling intelligence.
- Complete reporting suite.
- Production-ready multi-tenant SaaS controls.

## 6-Month Direction

The 6+ month project should expand from the 8-week vertical slice into a flexible platform:

| Month | Focus | Outcome |
| --- | --- | --- |
| Month 1-2 | Vertical slice | Budget levels, imports, proposal selection, and approval snapshots work for sample projects. |
| Month 3 | Flexible project configuration | Templates, custom divisions, reusable cost codes, stronger import mapping, and versioning. |
| Month 4 | Collaboration and controls | Role-based permissions, review workflows, notifications, and audit history. |
| Month 5 | Reporting and integrations | Better exports, dashboards, owner reporting, and possible accounting/ERP integration planning. |
| Month 6 | Production hardening | Security review, performance, backups, monitoring, deployment process, and user training. |

## Weekly Review Checklist

Use this at the end of every week:

1. What did we build that is actually working?
2. What is still simulated in the mockup?
3. Did any feature become more complex than expected?
4. Did we hardcode anything from West Henderson that should be configurable?
5. Are all budget edits saved to the database?
6. Are manual overrides tracked with reason and user?
7. Do totals match the source spreadsheet or reviewed example?
8. Are owner-facing views hiding internal-only data?
9. Did we update the roadmap based on what we learned?
10. What should we stop promising until it is proven?

## Immediate Next Actions

1. Complete `product/user-roles.md`.
2. Complete `docs/backend/file-parser.md`.
3. Complete `docs/api/files.md`.
4. Complete `docs/database/seed-data.md`.
5. Clean the mockup folder names.
6. Create a short demo script for the owner meeting.
7. Review the 8-week roadmap every Friday and update scope honestly.

