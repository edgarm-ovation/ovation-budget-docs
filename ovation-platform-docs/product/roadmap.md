# Product Roadmap

**Status:** `[COMPLETE]`

---

## Timeline Overview

```
NOW          Week 8         Month 3        Month 6        Year 2+
 │              │              │              │              │
 ▼              ▼              ▼              ▼              ▼
Foundation  ──► Demo       ──► Growth     ──► Production ──► Scale
2–3 projects    Owner         All active     Full team      Platform
Seed + calc     presentation  projects       features       expansion
```

---

## Phase 1 — Foundation (Weeks 1–8)

**Goal:** A real, data-backed application that **replaces the Excel budget workflow** for 2–3 seeded projects — and shows ownership the full vision. Confirmed scope 2026-06-17; see [roadmap-8-weeks.md](./roadmap-8-weeks.md) and [features/](../../features/) for the week-by-week detail.

**In scope (built for real, persisted to Azure SQL):**
- Next.js + .NET 8 scaffold deployed to Azure
- Seed data for 2–3 projects (West Henderson L3 + Robindale 215 L2) — **the data source for the demo**
- Cost-code / division structure and budget-level navigation (L0/L1 read-only)
- Core bid leveling tables (expandable divisions, inline editing, `group_key` bid picker)
- Markup formula engine (contingency, fee, OH, insurance, bonds) — **calculates the budget proposal amount**, server-side
- Approval workflow (submit → approve → lock + SHA-256 snapshot)
- In-app notifications (bell + feed)
- Budget variance summary (L2 vs L3)
- Foundation invariants in place (server = source of truth, append-only audit, `OrgId` hedge)

**Deferred from the 8-week build → Phase 2** (specs preserved in [features/later/](../../features/later/)):
- **Real Azure AD / Entra ID authentication + role-based access** (demo uses a simple role switcher only)
- **File import** — Excel/CSV with field mapping (data is seeded instead)
- **Excel export** (ClosedXML) — browser-print of the approval view covers any demo need
- **Email notifications** (Azure Communication Services) — in-app bell only for the demo

**Also not in scope for demo (unchanged):**
- L0 and L1 data entry flows (display only)
- Real-time conflict resolution (SignalR sync yes, conflict UI no)
- Cross-project reporting · Mobile optimization · Historical archive

**Demo target:** Present to Reinier Santana and ownership with live, persisted data from West Henderson and Robindale.

---

## Phase 2 — Growth (Months 3–4)

**Goal:** Expand from 2 projects to all active Ovation projects. Full team onboarded.

**Features:**
- **Real Azure AD / Entra ID authentication + role-based access** (carried over from Phase 1 — replaces the demo role switcher)
- **File import** — Excel/CSV with auto field mapping + manual fallback (carried over from Phase 1)
- **Excel export** (ClosedXML) and **email notifications** (Azure Communication Services) (carried over from Phase 1)
- All active Ovation projects migrated into the platform
- L0 and L1 data entry flows (full budget level support)
- Operations module — track construction progress against budget
- Advanced formula engine (custom markup overrides per division)
- Real-time conflict detection (two users editing same cell — show warning)
- Cross-project cost benchmarking (cost per unit across projects)
- Bulk file import (upload multiple files at once)
- Mobile-responsive polish
- Performance optimization for larger datasets

**Infrastructure:**
- Add Azure App Service staging slot (staging → production deploy flow)
- Add Azure SQL read replica for reporting queries
- Set up Azure Monitor alerts and cost budgets

---

## Phase 3 — Production (Months 5–6)

**Goal:** Fully hardened, production-grade platform. All Ovation divisions using it daily.

**Features:**
- Historical project archive — completed projects preserved and searchable
- Advanced reporting — variance reports, cost trend analysis, division benchmarks
- Cross-project comparison dashboard for leadership
- Budget snapshot exports (PDF for lender/ownership reporting)
- Audit report export (full change history per project for compliance)
- User management UI (Admin can add/remove users, change roles)
- Project templates (start a new project from a previous project's structure)

**Infrastructure:**
- Automated database backups verified and tested
- Disaster recovery runbook documented and tested
- Security audit completed
- Azure AD group-based role assignment (manage roles in Azure, not the app)

---

## Year 2+ — Platform Expansion

These are not committed — they represent the direction if the platform succeeds and Ovation decides to invest further.

**Potential modules:**

**Subcontractor Portal**
Allow subcontractors to log in and submit their proposals directly. Eliminates the file upload step entirely. Requires external user authentication (Azure AD B2C or similar).

**Accounting Integration**
Connect budget line items to Ovation's accounting system. Track committed costs, invoices, and payments against the budget. Shows real-time budget vs. actual spend.

**Schedule Integration**
Link budget milestones to a construction schedule. Show cost exposure by timeline. Alert when a trade is behind schedule and budget risk increases.

**Procore / Autodesk Integration**
Pull subcontractor data, RFIs, and submittals from Procore or Autodesk Construction Cloud into the budget context.

**AI-Assisted Estimating**
Use historical Ovation project data to suggest unit costs for new L0/L1 budgets. Flag line items that deviate significantly from historical norms.

**Multi-Company / White Label**
If Ovation's affiliated companies or partners want to use the platform, extend it to support multiple organizations in a single deployment.

---

## What We Are Not Building (Intentional Exclusions)

These are things that might seem like natural additions but are out of scope to keep the platform focused:

| Not building | Reason |
|---|---|
| General document management | Use SharePoint — it already exists |
| HR or payroll integration | Out of scope for construction budgeting |
| Tenant/resident portal | Different product entirely (Property Management domain) |
| Public-facing website | No external users in scope |
| Native mobile app | Responsive web covers mobile needs |
