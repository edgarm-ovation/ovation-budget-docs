# ovation-platform-docs

> Documentation repository for the **Ovation Construction Budget Management Platform**.
> All architecture decisions, technical specs, sprint records, and team processes live here.
> No source code — that lives in `ovation-platform`.

---

## What is this platform?

Ovation's internal construction budget management platform replaces manually maintained Excel files with a structured, multi-user web application. It tracks construction budgets across four levels (L0–L3) from pre-schematic concept through final construction documents, with full bid leveling, file parsing, approval workflows, and audit history.

**Current phase:** Foundation build — 8-week demo target, 6-month full production.
**Phase 1 seed/demo examples:** West Henderson Apartments (L3), Robindale 215 (L2).

---

## Repository Map

```
ovation-platform-docs/
│
├── README.md                          ← You are here
│
├── docs/
│   ├── architecture/
│   │   ├── decisions/                 ← Architecture Decision Records (ADRs)
│   │   │   ├── README.md              ← ADR index
│   │   │   ├── ADR-001-frontend-framework.md
│   │   │   ├── ADR-002-backend-framework.md
│   │   │   ├── ADR-003-cloud-and-database.md
│   │   │   └── ADR-004-budget-level-data-model.md
│   │   └── diagrams/
│   │       ├── system-overview.md     ← Full stack diagram + narrative
│   │       ├── data-flow.md           ← How data moves through the system
│   │       └── database-erd.md        ← Entity relationship diagram
│   │
│   ├── api/
│   │   ├── README.md                  ← API overview + versioning policy
│   │   ├── projects.md                ← /api/projects endpoints
│   │   ├── budget-levels.md           ← /api/projects/:id/levels endpoints
│   │   ├── line-items.md              ← /api/line-items endpoints
│   │   ├── bids.md                    ← /api/bids endpoints
│   │   ├── files.md                   ← /api/files upload + parse endpoints
│   │   ├── users.md                   ← /api/users + roles endpoints
│   │   └── notifications.md           ← /api/notifications endpoints
│   │
│   ├── database/
│   │   ├── README.md                  ← Database overview + conventions
│   │   ├── schema.md                  ← Full schema with all tables + fields
│   │   ├── migrations.md              ← Migration log + how to run
│   │   └── seed-data.md               ← What gets seeded at deployment
│   │
│   ├── frontend/
│   │   ├── README.md                  ← Frontend overview
│   │   ├── tech-stack.md              ← Next.js, shadcn, TanStack, etc.
│   │   ├── folder-structure.md        ← App Router structure + conventions
│   │   ├── components.md              ← Component library + usage guide
│   │   ├── state-management.md        ← Zustand + React Query patterns
│   │   └── styling.md                 ← Tailwind + Ovation brand guidelines
│   │
│   ├── backend/
│   │   ├── README.md                  ← Backend overview
│   │   ├── tech-stack.md              ← .NET 8, EF Core, SignalR, etc.
│   │   ├── folder-structure.md        ← Project layout + conventions
│   │   ├── auth.md                    ← Azure AD + roles + middleware
│   │   ├── file-parser.md             ← Excel/CSV parsing + field mapping
│   │   ├── formula-engine.md          ← Markup calculations + rollups
│   │   └── background-jobs.md         ← IHostedService + SignalR notifications
│   │
│   └── integrations/
│       ├── README.md                  ← All external integrations overview
│       ├── azure-ad.md                ← Azure AD SSO setup + config
│       ├── azure-sql.md               ← Azure SQL connection + EF Core setup
│       ├── azure-blob.md              ← Blob Storage for file uploads
│       └── azure-communications.md    ← Email notifications setup
│
├── sprints/
│   ├── backlog/
│   │   └── README.md                  ← Full product backlog (all stories)
│   ├── sprint-01/
│   │   └── README.md                  ← Sprint 1: Foundation & Auth
│   ├── sprint-02/
│   │   └── README.md                  ← Sprint 2: Core Bid Tables
│   ├── sprint-03/
│   │   └── README.md                  ← Sprint 3: File Upload Engine
│   └── sprint-04/
│       └── README.md                  ← Sprint 4: Approval + Demo Ready
│
├── product/
│   ├── overview.md                    ← What the platform does + who uses it
│   ├── user-roles.md                  ← Role definitions + permission matrix
│   ├── budget-levels.md               ← L0–L3 definitions + workflow
│   ├── features.md                    ← Full feature list (current + planned)
│   └── roadmap.md                     ← 8-week demo → 6-month production → beyond
│
├── scaling/
│   ├── README.md                      ← Scaling strategy overview
│   ├── phase-1-foundation.md          ← 0–2 projects, 2 devs, MVP
│   ├── phase-2-growth.md              ← All active projects, full team features
│   ├── phase-3-scale.md               ← Historical data, reporting, integrations
│   └── tech-debt.md                   ← Known shortcuts + when to address them
│
├── security/
│   ├── README.md                      ← Security overview
│   ├── auth-and-roles.md              ← Authentication + authorization model
│   └── data-handling.md               ← PII, financial data, audit requirements
│
├── processes/
│   ├── branching-and-pr.md            ← Git branching + PR rules
│   ├── deployment.md                  ← How to deploy to Azure
│   ├── incident-response.md           ← What to do when something breaks
│   └── adding-a-new-adr.md            ← How to write and submit an ADR
│
└── onboarding/
    ├── README.md                      ← New developer setup guide
    ├── local-setup.md                 ← Step-by-step local environment
    └── first-pr.md                    ← Guide to your first contribution
```

---

## Quick Links

| I want to... | Go to |
|---|---|
| Understand why we made a tech decision | [ADRs](./docs/architecture/decisions/README.md) |
| See the full API reference | [API Docs](./docs/api/README.md) |
| Understand the database schema | [Database](./docs/database/schema.md) |
| Review foundation gaps before the 8-week build | [Foundation Readiness Review](./product/foundation-readiness-review.md) |
| Know what the frontend stack is | [Frontend Tech Stack](./docs/frontend/tech-stack.md) |
| Know what the backend stack is | [Backend Tech Stack](./docs/backend/tech-stack.md) |
| See the current sprint | [Sprint 01](./sprints/sprint-01/README.md) |
| See all upcoming work | [Backlog](./sprints/backlog/README.md) |
| Understand the product vision | [Product Overview](./product/overview.md) |
| See the scaling plan | [Scaling](./scaling/README.md) |
| Set up my local environment | [Onboarding](./onboarding/local-setup.md) |
| Deploy to Azure | [Deployment](./processes/deployment.md) |

---

## Document Status Legend

| Badge | Meaning |
|---|---|
| `[COMPLETE]` | Written and reviewed |
| `[DRAFT]` | Written, needs review |
| `[STUB]` | File exists, content pending |
| `[PLANNED]` | Not yet created |

---

## Two Repositories

| Repo | Purpose |
|---|---|
| [`ovation-platform`](https://github.com/ovation/ovation-platform) | All source code |
| [`ovation-platform-docs`](https://github.com/ovation/ovation-platform-docs) | All documentation (this repo) |

---

*Last updated: June 2026 — Victor Alvarez*
