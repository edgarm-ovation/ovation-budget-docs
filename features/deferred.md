# Deferred Features

Features intentionally excluded from the 8-week Phase 1 demo. Each entry includes a summary, the rationale for deferral, and the target phase.

Use this doc when scoping future sprints, responding to stakeholder asks, or deciding what to promise next.

---

**Quick links:** [Phase 2](#phase-2--months-34) · [Phase 3](#phase-3--months-56) · [Year 2+](#year-2-and-beyond)

---

## Phase 2 — Months 3–4

### Real-Time Multi-User Conflict Resolution

**What it does:** When two estimators edit the same cell simultaneously, the platform detects the conflict, surfaces it to both users, and provides a merge or override decision — rather than silently overwriting one person's work.

**Why deferred:** SignalR (the WebSocket layer) ships in Phase 1, but the conflict resolution logic — detecting concurrent writes, presenting the conflict UI, and resolving gracefully — adds significant complexity. The 8-week demo has a single active estimator per project, so this is safe to defer.

**Target:** Phase 2 — after all active Ovation projects are migrated.

**Related features:** [03 — Budget Table Editing](./in-scope/03-budget-editing.md), [08 — Notifications](./in-scope/08-notifications.md)

---

### L0 / L1 Data Entry Flows

**What it does:** Structured input screens for Pre-Schematic (L0) and Schematic Design (L1) budgets — the earliest, roughest estimates that use historical unit costs and division-level lump sums rather than trade-package bids.

**Why deferred:** The demo focuses on L2 (Robindale) and L3 (West Henderson), the two most complex and highest-value levels. L0/L1 are simpler in structure but require different UX patterns (no bid leveling, no file import, just high-level cost entry). Adding them to Phase 1 would spread the build too thin.

**Target:** Phase 2.

**Related features:** [02 — Project & Budget Navigation](./in-scope/02-project-navigation.md), [03 — Budget Table Editing](./in-scope/03-budget-editing.md)

---

### Advanced Formula Overrides

**What it does:** Lets managers override individual markup percentages per line item or per division, rather than applying a single rate across the whole budget level. Includes a UI for managing markup rate tables used by the formula engine.

**Why deferred:** The Phase 1 formula engine applies markups at the budget level. Division- or line-item-level overrides add a new dimension of complexity to the data model and UI that isn't needed for the two demo projects.

**Target:** Phase 2.

**Related features:** [06 — Markup Formula Engine](./in-scope/06-markup-engine.md)

---

### Cross-Project Benchmarking

**What it does:** Aggregates historical cost data across multiple Ovation projects to generate benchmarks (e.g., "typical $/SF for Mechanical in a 200-unit multifamily in Las Vegas"). Estimators can compare their current budget against the benchmark range.

**Why deferred:** Requires data from multiple projects to be useful. With only two seed projects in Phase 1, there's nothing meaningful to benchmark against.

**Target:** Phase 2 — once all active projects are migrated.

**Related features:** [05 — Bid Leveling](./in-scope/05-bid-leveling.md), [10 — Variance Summary](./in-scope/10-variance-summary.md)

---

### All Historical Projects Migration

**What it does:** Import of Ovation's full back-catalog of completed project budgets into the platform, making them searchable and available for benchmarking.

**Why deferred:** Data cleanup and migration of historical Excel files is labor-intensive and can run in parallel with Phase 2 development. The demo only needs the two seed projects.

**Target:** Phase 2 (migration runs alongside development).

---

### Infrastructure Scale-Up (B2 → S2)

**What it does:** Upgrade Azure App Service from Basic B2 tier to Standard S2, add a staging deployment slot, and enable auto-scaling rules.

**Why deferred:** Demo runs fine on B2. The upgrade is triggered by production load from real projects, not demo traffic.

**Target:** Phase 2, when all active projects go live.

---

## Phase 3 — Months 5–6

### Historical Project Archive & Search

**What it does:** Searchable archive of all completed Ovation projects — budget snapshots, approval records, bid tabs — accessible to any authorized user. Includes filters by project type, year, location, and cost range.

**Why deferred:** Depends on the historical migration from Phase 2 being complete. Building search before the data exists is premature.

**Target:** Phase 3.

---

### Advanced Reporting & Dashboards

**What it does:** Leadership-facing dashboards showing portfolio-wide metrics — total committed costs across all active projects, budget-vs-actual tracking, bid hit rates, trade cost trends over time.

**Why deferred:** Requires data from multiple projects and a stable data model before meaningful aggregations are possible.

**Target:** Phase 3.

**Related features:** [10 — Variance Summary](./in-scope/10-variance-summary.md)

---

### PDF Approval Snapshots & Audit Exports

**What it does:** Generates a formatted PDF of the budget at the moment of approval — a legally-defensible, signed snapshot that can be attached to contract files. Includes the SHA-256 hash, approver signature block, and full line item detail.

**Why deferred:** The Phase 1 approval workflow stores the hash and locks the budget. The PDF rendering adds complexity (library choice, formatting, signature capture) that isn't required for the demo.

**Target:** Phase 3.

**Related features:** [07 — Approval Workflow](./in-scope/07-approval-workflow.md), [09 — Excel Export](./in-scope/09-excel-export.md)

---

### User Management UI

**What it does:** In-app admin screen for Admins to add/remove users, assign roles, and manage project access — without needing to touch the database directly.

**Why deferred:** For Phase 1, user and role setup is done at the database/Azure AD level during onboarding. A self-serve UI isn't needed until the platform has enough users to justify it.

**Target:** Phase 3.

**Related features:** [01 — Authentication & Roles](./in-scope/01-authentication.md)

---

### Project Templates

**What it does:** Saves a budget structure (divisions, line items, standard markups) as a reusable template for new projects of a similar type. Reduces the setup time for new projects from scratch.

**Why deferred:** Templates are only valuable once patterns emerge from multiple projects. Can't identify the right templates until Phase 2 data is in.

**Target:** Phase 3.

**Related features:** [03 — Budget Table Editing](./in-scope/03-budget-editing.md)

---

### Full Production Security Audit

**What it does:** Third-party penetration test, code audit, dependency vulnerability scan, and security hardening pass before the platform is considered production-ready for sensitive financial data.

**Why deferred:** The 8-week demo is an internal stakeholder demo, not a production-hardened system. Security hardening is budgeted as a Phase 3 activity before go-live with all projects.

**Target:** Phase 3, before full production go-live.

---

### Infrastructure Premium Tier + Geo-Replication

**What it does:** Azure SQL premium tier with geo-redundant replication, automated backup verification, and disaster recovery runbooks. Targets 99.9% uptime SLA.

**Why deferred:** Demo and early Phase 2 traffic doesn't justify premium infrastructure costs. Upgrade triggered by production load and data criticality.

**Target:** Phase 3.

---

### Full File-Parser Coverage for Legacy Formats

**What it does:** Extended file import support for legacy and non-standard formats — older .xls files, complex multi-sheet workbooks, PDF bid tabs (via OCR), and subcontractor-specific formats that don't follow standard column conventions.

**Why deferred:** Phase 1 import targets standard .xlsx and .csv with reasonable column naming. Edge-case formats can be handled with manual mapping as a fallback in the short term.

**Target:** Phase 3 (or ongoing, as new formats surface).

**Related features:** [04 — File Import](./in-scope/04-file-import.md)

---

### Mobile Optimization

**What it does:** Fully responsive layouts for tablet and phone — touch-friendly bid leveling, swipeable table views, and a mobile-first notification experience for field managers who aren't at a desktop.

**Why deferred:** The primary users (estimators, managers) work at desks. Mobile is a nice-to-have for field check-ins but not a Phase 1 requirement.

**Target:** Phase 3 (or Year 2, depending on demand signals).

---

## Year 2 and Beyond

### Subcontractor Portal

**What it does:** External-facing web interface where subcontractors can log in, submit their proposals directly, respond to RFIs, and track bid status — eliminating email-based bid collection.

**Why deferred:** Requires external authentication (separate from Azure AD), a subcontractor onboarding flow, and significant trust/security work for external users. Well outside Phase 1–3 scope.

**Target:** Year 2.

---

### Accounting / GL Integration

**What it does:** Bi-directional sync with Ovation's accounting system — pushing awarded contract values as committed costs and pulling actuals back for budget-vs-actual tracking.

**Why deferred:** Requires mapping the platform's budget structure to the GL chart of accounts, coordinating with the finance team on data ownership, and likely a formal integration project. High value, high complexity.

**Target:** Year 2.

---

### Schedule Integration

**What it does:** Links budget line items to project schedule activities — surfaces cost-loaded schedules and flags when scope changes in the schedule would affect the budget.

**Why deferred:** Requires a scheduling system integration (Primavera, MS Project, or Procore). Not a current Ovation system dependency.

**Target:** Year 2.

---

### AI-Assisted Estimating

**What it does:** LLM-powered suggestions for unit costs and quantities based on similar historical line items, project type, and location. Flags anomalies in submitted budgets (e.g., a mechanical bid that's 40% above the historical benchmark).

**Why deferred:** Requires a mature historical dataset (from Phase 2–3 migrations) to be useful. Premature without that foundation.

**Target:** Year 2+ — revisit after Phase 3 data is established.

---

### Multi-Company / White-Label

**What it does:** Extends the platform to support multiple construction companies under separate tenant configurations — each with their own branding, user base, and data isolation. Positions the platform as a sellable product.

**Why deferred:** Current scope is Ovation-internal. Multi-tenancy is a major architectural change that would require rethinking the data model, auth, and billing.

**Target:** Year 2+ — only if there's a strategic decision to productize.

---

## Related Docs

- [Feature Index](./README.md) — all in-scope features
- [Product Roadmap](../ovation-platform-docs/product/roadmap.md)
- [Scaling Plan](../ovation-platform-docs/scaling/)
- [Owner Demo Doc](../ovation-platform-owner-demo-8-week%20claude/)
