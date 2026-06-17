# Ovation Budget Platform - Updated 8-Week Mockup

**For:** Owner / manager review and developer architecture planning  
**Status:** Clickable visual mockup, no backend  
**Created from:** `Prototypes-UI/ovation-platform-mockup Open Ai`

---

## Why this copy exists

The original OpenAI mockup is preserved as a reference. This folder is the updated version that reflects the latest planning docs:

- `ovation-platform-docs/product/foundation-readiness-review.md`
- `features/README.md`
- `features/in-scope/*.md`
- `features/deferred.md`
- `ovation-platform-docs/OPENAI_README.md`

Use this version when showing the current 8-week direction or when explaining the architecture foundation before implementation.

---

## How to open it

Open `index.html` in a browser. It is a self-contained HTML/CSS/JS prototype.

No install, internet, login, or backend is required.

---

## What changed from the reference mockup

The original budget screens are still here:

- Projects dashboard
- Project workspace
- Master budget
- Proposal L3 adjustments
- Trades and bid leveling
- Markups
- File import
- Takeoffs
- Benchmark
- Significant changes
- Variance
- Approval and lock

This updated copy adds:

- Top-level `8-Week Scope` screen.
- Top-level `Architecture Review` screen.
- Project workspace `Budget Edits & Saves` screen with real state-changing mock actions.
- West Henderson Level 3 workbook data loaded into `Master Budget`.
- Clearer 8-week feature grouping.
- In-scope versus deferred expectations.
- Flexible data model reminders.
- Azure SQL / Azure Blob save-path explanation.
- Weekly review-gate checklist.

---

## What to click for the new work examples

Open `index.html`, sign in, then either:

- Click `8-Week Scope` -> `Try Editing Workflow`, or
- Open `Project Workspace` -> `Budget Edits & Saves`.

That screen now lets you:

- Add a custom budget line item.
- Override a budget value.
- Stage imported spreadsheet rows.
- Select a proposal.
- Save the changes to a simulated Azure SQL commit.
- See unsaved/saved counters update.
- See the audit trail update with user, time, action, and detail.

These interactions are still a mockup, but they show the actual app behavior we need to build.

---

## Workbook data now included

Source file:

`Excel-Docs-Projects/Budget - West Henderson - Level 3.xlsx`

Loaded into the mockup:

- `Level 3` sheet budget table.
- 30 workbook division summary rows.
- 265 extracted line items.
- Description, cost code, cost category, sub job, source, UOM, quantity, unit cost, escalation, subtotal, and details where present.
- West Henderson project GSF and current L3 total updated from the workbook.

Not fully modeled as separate workflows yet:

- `Menu Pricing`
- `Insurance_Bonds`
- `Summary Changes`
- `Comparison to Previous`
- `Comparison to Other`
- `Normalize`
- `Offsite Comp`
- Historical comparison sheets such as Torrey, Pebble, Decatur, and Russell

For the 8-week demo, the realistic promise is to show the Level 3 budget data, editable rows, import mapping, selected proposals, markups, variance summary, and approval snapshot. Full formula parity with every workbook tab should be treated as a post-demo validation/hardening task unless the team makes it a priority early.

---

## Main message for the meeting

The goal for 8 weeks is a clean, working vertical slice, not the full 6-month production platform.

Safe 8-week promise:

- Azure-backed project and budget data foundation.
- West Henderson L3 and Robindale L2 seed/demo examples.
- Editable budget table and custom line items.
- Limited Excel/CSV import with manual mapping fallback.
- Bid leveling and selected proposal workflow.
- Markup calculations.
- Approval snapshot and lock state.
- Excel export and variance summary.

Not safe to promise for 8 weeks:

- Perfect import for every spreadsheet format.
- Full accounting or GL integration.
- Subcontractor portal.
- Full real-time multi-user collaboration.
- Advanced field-level permissions.
- Complete production reporting suite.
- Production-grade multi-tenant SaaS controls.

---

## Developer reminder

Do not build a West Henderson-only app.

West Henderson and Robindale are seed/demo examples. The real architecture needs to support configurable projects, budget levels, divisions, trades, line items, proposals, markups, overrides, approval snapshots, uploaded files, and audit history.

Structured data belongs in Azure SQL. Uploaded and generated files belong in Azure Blob Storage.
