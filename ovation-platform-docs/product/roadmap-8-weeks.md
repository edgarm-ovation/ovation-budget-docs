# 8-Week Demo Roadmap

**Status:** `[PLANNED]`

---

## Objective

Deliver a production-backed, stakeholder-ready Ovation Budget Platform demo in 8 weeks. The demo must prove the platform’s value by showing end-to-end budget management for two real projects: West Henderson Apartments (L3) and Robindale 215 (L2).

**Demo target:** A functioning Azure-hosted web app with project setup, bid leveling, file import, markup calculations, approval workflow, export, and a budget dashboard.

---

## Success Criteria

- Platform is deployed and accessible in Azure
- Users can authenticate with Azure AD and see role-appropriate screens
- Two seeded projects are available and navigable
- Budget line items can be edited, saved, and calculated correctly
- File upload successfully imports Excel/CSV budget data
- Approval workflow works end-to-end and locks approved levels
- Stakeholders can export a budget level and view variance summary
- Demo can be run smoothly in 20 minutes with clear talking points

---

## 8-Week Scope

### Core must-have features

- Azure-hosted Next.js frontend and .NET 8 backend
- Azure AD authentication with Estimator, Manager, and Admin roles
- Project navigation and budget level selection (L0–L3)
- Bid leveling tables with divisions, line item details, and awarded bid selection
- Excel / CSV file upload and auto-mapping
- Manual field mapping fallback UI
- Markup formula engine: contingency, fee, overhead, insurance, bonds
- Approval workflow with submit/reject/approve and lock state
- In-app notifications and email alerts for key events
- Export budget data to Excel
- Budget variance summary screen or chart
- Two seed projects with realistic L2/L3 budget data

### Important secondary features

- Read-only display of L0 and L1 budget levels
- Approval comments and rejection reasons
- Audit trail summary panel
- Demo-ready styling and workflow copy
- Basic performance satisfaction for demo dataset sizes

---

## Week-by-Week Plan

### Weeks 1–2: Foundation and architecture

**Goals:** Establish the platform skeleton, access control, and core data model.

Tasks:
- Create the Next.js frontend and .NET 8 API repositories in Azure
- Wire up Azure AD authentication and role-based authorization
- Define database models for projects, budget levels, trades, line items, bids, and approvals
- Create seed data templates for West Henderson and Robindale
- Build project list and budget level navigation pages
- Implement core budget table layout and field definitions
- Validate Azure deployment path and environment configuration

Acceptance criteria:
- Users can log in and reach the main app shell
- Project list displays sample projects
- Budget level pages load with placeholder columns
- Deployment mechanism is proven with a staging slot or dev environment

### Weeks 3–4: Budget editing and file import

**Goals:** Support realistic budget entry, bid comparison, and file ingestion.

Tasks:
- Implement editable budget table rows with cost, quantity, trade, and notes fields
- Build bid selection UI and award status controls
- Add file upload component for Excel and CSV import
- Build auto-detection logic for common column names
- Add manual column mapping UI for fallback cases
- Parse uploaded files into line item records and persist them
- Add seed project data for West Henderson and Robindale
- Add budget summary cards for total cost, contingency, and markup amounts

Acceptance criteria:
- Budget table edits save successfully and persist on reload
- Uploaded Excel/CSV budgets import without errors for at least one sample file each
- Manual mapping works for one non-standard file format
- Awarded bid selection updates project totals correctly

### Weeks 5–6: Approval workflow and notifications

**Goals:** Complete the approval process and make key state transitions visible.

Tasks:
- Build submit-for-approval flow from Estimator to Manager
- Implement approval/rejection actions and lock state enforcement
- Add approval status badges, reviewer comments, and approval history
- Add in-app notifications for file import completion and approval events
- Add email notification templates for approval requests and decisions
- Implement export-to-Excel for a selected budget level
- Add a basic variance chart or summary table comparing budget vs. awarded costs

Acceptance criteria:
- Estimators can submit a budget for approval
- Managers can approve or reject with comments
- Approved budgets become read-only until a new version is created
- Excel export downloads a formatted budget file
- Notifications appear in the app and trigger emails for demo accounts

### Weeks 7–8: Demo polish, testing, and presentation

**Goals:** Finalize the product experience and prepare the stakeholder demo.

Tasks:
- Refine UI layout, labels, and navigation flow for demo clarity
- Add branded styling and consistent visual hierarchy
- Fix bugs found in end-to-end workflows
- Add demo guidance notes and an internal walkthrough page
- Validate seeded project data and populate any missing sample values
- Create a short demo script and 20-minute runbook
- Conduct a pre-demo dry run and capture any time or flow issues

Acceptance criteria:
- Demo can be executed end-to-end in under 20 minutes
- Key workflows have no blocking bugs
- Stakeholder-facing flows are easy to follow and readable
- Demo notes are available for the presenter

---

## Detailed Deliverables

### Platform deliverables

- Azure-hosted frontend and backend
- Core budget management UI
- File import for Excel and CSV budgets
- Markup and cost calculation engine
- Approval workflow with lock state
- Export to Excel
- Project seed data for two live demos
- Budget variance dashboard or summary

### Project/demos deliverables

- West Henderson Apartments (L3 project) with real construction document budget data
- Robindale 215 (L2 project) with design development budget data
- Clear walkthrough of how to compare bids, approve a budget, and export results
- Stakeholder presentation notes and demo script

---

## Roadmap Milestones

| Week | Focus | Milestone |
|---|---|---|
| 1 | Setup | App deployed, Azure AD auth connected, sample projects loaded |
| 2 | Data model | Project/budget data model validated, budget table rendered |
| 3 | Edit + bids | Line item editing works, bid awarding is visible |
| 4 | Import | Excel and CSV import works for sample budgets |
| 5 | Approval | Submit/approve workflow implemented and tested |
| 6 | Export | Budget export and variance summary completed |
| 7 | Demo polish | UI refined, documentation added, bugs fixed |
| 8 | Stakeholder prep | Dry run complete, demo ready for presentation |

---

## What the Demo Must Show

- Secure login and role-based access
- Selection of a project and budget level
- Uploading a subcontractor budget file
- Mapping file columns and importing budget line items
- Editing bids, selecting an awarded bid, and recalculating totals
- Submitting a budget for approval and approving it
- Downloading an Excel export and reviewing budget variance

---

## Assumptions

- Azure AD and Azure deployment access are available immediately
- Team members can split work across frontend, backend, and data model tasks
- Demo data can be prepared using existing Ovation budget files or templates
- File parsing can focus on the most common internal formats first
- There is a single primary stakeholder group for the demo presentation

---

## Risks and Mitigations

- Risk: Azure AD integration delays
  - Mitigation: Build a temporary local auth fallback and switch to Azure AD once ready
- Risk: File import edge cases consume too much time
  - Mitigation: Focus on high-value file patterns and implement manual mapping for exceptions
- Risk: Scope creep beyond demo goals
  - Mitigation: Use the 8-week plan as a strict boundary; defer advanced features to post-demo work
- Risk: Insufficient seed data for live projects
  - Mitigation: Use a combination of real and synthetic budget data to support the demo

---

## Demo Presentation Plan

1. Start with the Ovation problem statement and the current Excel workflow pain points.
2. Show login and role-based access.
3. Navigate to West Henderson and Robindale projects.
4. Upload a sample subcontractor budget file and map columns.
5. Edit line items, compare bids, and award a bid.
6. Submit a budget for approval and show the approval flow.
7. Export a budget and open the Excel file.
8. Review the budget variance summary and close with next-phase vision.

---

## Post-Demo Follow-up

- Capture stakeholder feedback and identify top 3 must-have improvements
- Document gaps and assumptions discovered during the demo
- Prioritize a follow-up 4-week plan for production hardening and Phase 2 growth

---

## Notes

This roadmap is intentionally more detailed than a high-level timeline. It is meant to help the team execute the 8-week demo with clearly defined weekly tasks, measurable outcomes, and a polished stakeholder presentation.
