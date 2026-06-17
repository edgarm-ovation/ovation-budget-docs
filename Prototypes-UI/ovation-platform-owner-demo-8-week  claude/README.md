# Ovation Budget Platform - 8 Week Owner Demo Mockup

**Purpose:** Owner-facing mockup and honest 8-week delivery plan for tomorrow's meeting.  
**Status:** Static HTML prototype. No backend, no database, no real login.

---

## Open The Mockup

Open `index.html` in a browser.

This folder is separate from the existing `ovation-platform-mockup` folder so the current mockup stays untouched.

---

## What This Mockup Shows

The mockup uses the manager's West Henderson L3 prototype as the visual reference:

- Navy sidebar with project navigation.
- KPI cards across the top.
- Panel-based layout.
- L2 locked baseline vs L3 selected bids.
- Selected bid cells that open a bid picker.
- Proposed / awarded status pills.
- File import and column mapping.
- Approval lock with signature and SHA-256 hash.
- 8-week roadmap and honest scope page for owner discussion.

The numbers are illustrative but based around the West Henderson and Robindale seed/demo concept.

---

## What We Can Honestly Present For 8 Weeks

8 weeks at 8 hours/day and 5 days/week is:

- **320 hours per developer**
- **640 hours for 2 developers**

The realistic promise is a working Azure-hosted demo, not a fully hardened production platform.

### Commit For 8 Week Demo

- Azure-hosted app shell.
- Azure SQL schema and seed/demo data.
- West Henderson L3 budget workflow.
- Robindale L2 overview/workflow.
- Project dashboard.
- L2/L3 budget table.
- Bid picker for selected bids.
- Proposed / awarded trade status.
- Excel/CSV upload for common file formats.
- Manual column mapping fallback.
- Server-side formula engine for demo totals.
- Submit / approve / reject / lock workflow.
- Signature and SHA-256 approval snapshot.
- Excel export and variance summary.
- Demo script and dry run.

### Stretch If Time Remains

- More West Henderson divisions and line items.
- Richer trade summary sheets.
- More polished approval package PDF.
- More charts.
- Better mobile/tablet layout.
- More file templates supported by auto-mapping.

### Do Not Promise For 8 Weeks

- Full production hardening.
- Perfect parser for every old workbook.
- All active projects migrated.
- Historical archive.
- Accounting / GL integration.
- Invoices, payments, or commitments.
- Subcontractor portal.
- Full real-time conflict resolution.
- Native mobile app.
- Full security audit.

---

## 8 Week Roadmap

| Week | Focus | Owner-visible outcome | Review gate |
|---|---|---|---|
| 1 | Setup | App shell, repo, Azure plan, first pages | Confirm Azure SQL / Blob direction |
| 2 | Data model + auth | Project list, roles, seed data structure | Confirm West Henderson L3 model supports bid picker |
| 3 | Budget table | L2/L3 budget view, inline edits, summary cards | Check totals and locked baseline behavior |
| 4 | Bids + import | Bid picker, file upload, manual mapping | Test one standard and one non-standard file |
| 5 | Formula + approval | Server totals, submit/reject/approve workflow | Confirm formulas match expected values |
| 6 | Export + notifications | Excel export, variance chart, basic notifications | Confirm locked budgets cannot mutate |
| 7 | Polish + seed data | West Henderson and Robindale demo data cleaned | Run first full demo rehearsal |
| 8 | Final demo | 20-minute owner walkthrough ready | Dry run and final discrepancy review |

---

## 6 Month Roadmap

### Months 1-2: Demo Foundation

Deliver the 8-week stakeholder demo:

- Azure-hosted frontend and backend.
- Azure AD login target.
- West Henderson and Robindale seed data.
- Budget table, bid leveling, import, approval, export.

### Months 3-4: Growth

Expand toward team usage:

- Add more active Ovation projects.
- Full L0 and L1 data entry.
- Bulk file import.
- Better summary sheet persistence.
- Cross-project benchmarking.
- Real-time conflict detection.
- Staging environment and monitoring.
- Automated tests for formula engine, file parser, approval workflow.

### Months 5-6: Production Hardening

Prepare for daily operation:

- Historical project archive.
- Advanced reporting.
- PDF approval packages and audit exports.
- User management UI.
- Project templates.
- Backup/restore verification.
- Security review.
- Azure SQL performance tuning.
- Incident response and deployment runbooks.

---

## Review Process To Avoid Discrepancies

Run reviews every week, not only at the end.

### Weekly Friday Review

- Compare implementation against docs and mockup.
- Update discrepancy list.
- Confirm next week's promises are still realistic.
- Review open blockers.

### Feature Readiness Review

Before a feature starts, confirm:

- User workflow.
- API contract.
- Azure SQL persistence.
- Azure Blob storage needs.
- Permissions.
- Validation rules.
- Demo data needed.

### Demo Readiness Review

Before owner presentation, confirm:

- West Henderson L3 opens and tells the bid-leveling story.
- Robindale L2 opens and shows the L2 workflow.
- File import demo path works.
- Approval lock and export path works.
- Totals are believable and explained.
- Demo can be completed in 20 minutes.

---

## Biggest Risks

| Risk | Why It Could Take Longer | Mitigation |
|---|---|---|
| Azure AD access | Can block real authentication setup | Use local role switch in demo, replace with Azure AD when available |
| File import | Legacy files have inconsistent columns | Build common mappings first, manual mapping fallback |
| Seed data | Bad data makes the demo weak | Prep West Henderson and Robindale in Weeks 1-2 |
| Group-level bids | More complex than trade-level totals | Keep demo path focused on key cost codes first |
| Scope creep | New asks can break the 8-week date | Move non-demo asks to 6-month roadmap |

---

## Bottom Line

For the owner meeting, the safe message is:

> In 8 weeks, we can deliver a working Azure-hosted demo that proves the core Ovation budget workflow on West Henderson and Robindale. It will show budget levels, bid leveling, import, formula totals, approval lock, and export. Full production hardening, all historical projects, and rare file-format coverage are part of the 6-month roadmap, not the 8-week promise.
