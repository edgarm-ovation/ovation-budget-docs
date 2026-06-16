# Product Overview

**Status:** `[COMPLETE]`

---

## What is the Ovation Budget Platform?

The Ovation Budget Platform is an internal construction budget management tool built for Ovation's development, construction, and asset management teams. It replaces a fragmented Excel-based workflow with a centralized, multi-user web application.

The platform manages construction budgets from the earliest feasibility stage through final construction contracts — a process Ovation defines across four budget levels (L0 through L3).

---

## The Problem It Solves

Before this platform, Ovation's budget process looked like this:

- Budget files lived in individual Excel workbooks per project
- Multiple people edited the same file, creating version conflicts
- No audit trail — no record of who changed what or when
- Moving from one budget level to the next meant manually copying data between files
- Old files from subcontractors had inconsistent column structures — mapping them was manual and error-prone
- Leadership had no real-time visibility into budget status across projects
- Bid leveling (comparing multiple subcontractor proposals) was done manually in Excel

---

## What the Platform Does

**Budget level management** — Create and manage budgets at L0, L1, L2, and L3 for any project. Each level is preserved as a versioned snapshot; levels are never overwritten.

**Bid leveling** — Compare multiple subcontractor proposals per trade. Select the awarded bid. Track proposal, bid, and awarded status per line item.

**File import** — Upload Excel or CSV files from subcontractors and Ovation estimators. The system auto-detects columns and maps them to the canonical field structure. A manual mapping UI handles old files with non-standard formats.

**Formula engine** — Calculate markups (contingency, fee, overhead, insurance, bonds) as percentages of base cost. Override individual line items. See totals update in real time.

**Approval workflow** — Estimators submit budget levels for Manager review. Managers approve or reject with comments. Approved levels lock — no further edits without a new version.

**Real-time collaboration** — Multiple users can work on the same project simultaneously. Changes appear live. Conflict warnings prevent overwriting each other's work.

**Audit trail** — Every change to every field is logged: who changed it, when, and what the value was before.

**Export** — Export any budget level to a formatted Excel file matching Ovation's standard structure.

**Notifications** — In-app and email notifications for approvals, rejections, and file parsing completion.

---

## Who Uses It

| Role | Division | What they do in the platform |
|---|---|---|
| Estimator | Development / OCI | Build and maintain budget line items, upload files, submit levels for approval |
| Manager | Development / OCI | Review and approve budget levels, oversee project budgets |
| Admin | Engineering | Manage users, roles, and project setup |
| Viewer | Asset Management / Finance | Read-only access to budget data for reporting |

See [user-roles.md](./user-roles.md) for the full permission matrix.

---

## Projects in Scope

**Phase 1 (current):** Two active projects
- West Henderson Apartments — Level 3 (Construction Documents)
- Robindale 215 — Level 2 (Design Development)

**Phase 2:** All active Ovation projects
**Phase 3:** Historical project archive + cross-project reporting

See [roadmap.md](./roadmap.md) for the full timeline.

---

## What It Is Not

- Not a project management tool (no Gantt charts, schedules, or tasks)
- Not an accounting system (no invoices, payments, or GL integration — yet)
- Not a subcontractor portal (subs do not log in; their files are uploaded by Ovation staff)
- Not a document management system (no general file storage beyond budget-related uploads)

These may become future modules. See [roadmap.md](./roadmap.md).
