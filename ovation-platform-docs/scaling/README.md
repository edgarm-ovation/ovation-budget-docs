# Scaling Strategy

**Status:** `[COMPLETE]`

---

## Overview

The platform is built in three distinct phases, each with a clear trigger for moving to the next. We do not over-engineer for Phase 3 while building Phase 1 — but we make decisions in Phase 1 that do not block Phase 3.

```
Phase 1           Phase 2              Phase 3
────────────────────────────────────────────────────────
2 projects        All active projects  Historical + reporting
2 devs            Full team onboard    Platform maturity
MVP features      Full feature set     Integrations + AI
~50 users         ~100 users           200+ users
Azure B2 tier     Azure S2 tier        Azure P2 tier
```

---

## Phase 1 — Foundation (Current)

**Trigger to start:** Now
**Trigger to end:** 8-week demo delivered + approved by ownership

### What we build
- Authentication, roles, core bid tables
- File upload + parser (Excel + CSV)
- Approval workflow
- Notifications
- Export to Excel
- 2 seed projects

### Infrastructure
```
Azure App Service (B2)      ← .NET API
Azure Static Web Apps       ← Next.js frontend
Azure SQL (General Purpose, 2 vCores)
Azure Blob Storage (LRS)
Azure AD (existing tenant)
Azure Communication Services
```

### What we intentionally defer
- Staging environment (deploy straight to prod from main)
- Read replicas (single DB is fine for 2 projects)
- CDN (not needed at this traffic level)
- Redis cache (not needed)
- Automated performance testing

### Known tech debt accepted in Phase 1
See [tech-debt.md](./tech-debt.md) for the full list.

---

## Phase 2 — Growth (Months 3–4)

**Trigger to start:** Demo approved + decision to expand to all projects
**Trigger to end:** All active projects migrated, full team using it daily

### What we add
- L0 and L1 data entry flows
- Operations module
- Advanced formula overrides
- Real-time conflict detection
- Cross-project benchmarking
- Bulk file import
- Mobile responsive polish

### Infrastructure changes
```
Azure App Service (S2)      ← Scale up from B2
Azure SQL (General Purpose, 4 vCores)  ← Scale up
Add: Azure App Service Staging Slot    ← staging → prod deploy
Add: Azure CDN                         ← Static asset delivery
Add: Azure Application Insights        ← Performance monitoring
```

### Database changes
- Add read replica for reporting queries
- Add AuditLog table partitioning (by month)
- Add indexes based on Phase 1 query patterns
- Migrate any accepted tech debt from Phase 1

### Team changes
- Document all onboarding materials
- Add automated tests for critical paths (formula engine, file parser)
- Add CI/CD pipeline checks (lint, build, test before merge)

---

## Phase 3 — Scale (Months 5–6+)

**Trigger to start:** All active projects live + leadership requests historical data
**Trigger to end:** Platform is stable enough to run without daily developer attention

### What we add
- Historical project archive
- Advanced reporting dashboard
- Budget snapshot PDF exports
- Audit report exports
- User management UI
- Project templates
- Security audit
- Disaster recovery runbook

### Infrastructure changes
```
Azure App Service (P2)      ← Premium tier for guaranteed performance
Azure SQL (Business Critical, 4 vCores)  ← Higher SLA
Add: Azure SQL geo-replication           ← Disaster recovery
Add: Azure Backup                        ← Verified backup strategy
Add: Azure Key Vault (already exists)    ← Rotate secrets on schedule
Review: Azure cost optimization          ← Reserved instances if staying long-term
```

### Architecture evolution checkpoints

At Phase 3, revisit these decisions:

**Background jobs:** If file processing volume is high (50+ uploads/day), replace `IHostedService` with **Azure Service Bus + Azure Functions**. The API contract does not change — only the job runner changes.

**Caching:** If `GET /projects/:id/levels/:level/line-items` becomes slow under load, add **Azure Cache for Redis** as a read-through cache. EF Core query caching handles most cases before this is needed.

**Search:** If users need full-text search across projects and line items, add **Azure AI Search** (formerly Cognitive Search). Start with SQL `LIKE` queries — upgrade only when they're insufficient.

**Real-time scale:** If SignalR has more than 500 concurrent connections, add **Azure SignalR Service** (managed SignalR). The code change is a 2-line config change — the hub code does not change.

---

## Year 2+ — Platform Expansion

See [product/roadmap.md](../product/roadmap.md) for potential future modules.

From a technical scaling perspective:

**Multi-tenancy:** If Ovation's affiliated companies or partners want to use the platform, the database schema needs a `tenant_id` on every table. This is a significant migration. If multi-tenancy is likely, add `tenant_id` in Phase 2, not Phase 3.

**Microservices:** We intentionally start with a monolith (.NET single project). If the team grows to 10+ developers and independent deployment of the file parser or formula engine becomes valuable, extract them to separate services. Do not split early — a well-structured monolith scales to millions of requests/day.

**Mobile app:** If Ovation field staff need native mobile (iOS/Android), the .NET API is already the backend — add React Native or Flutter frontend. The API does not change.

---

## Scaling Principles

These guide every architectural decision:

1. **Scale the database last.** Application servers are cheap to scale. Databases are expensive. Optimize queries before adding hardware.

2. **Monolith first, microservices never (until necessary).** The overhead of microservices is not justified until the team and traffic demand it. A well-structured monolith is not a failure — it's the right tool.

3. **Don't build for Phase 3 in Phase 1.** Every piece of premature infrastructure adds complexity and slows Phase 1 delivery. The 8-week demo is the priority.

4. **Leave the escape hatches.** `IHostedService` → Azure Service Bus is a 1-day migration. Azure SignalR Service → managed is a 2-line change. Build the simple version, but build it so the upgrade path is clear.

5. **Document the tech debt.** Every shortcut accepted in Phase 1 is written in [tech-debt.md](./tech-debt.md) with a Phase target for addressing it. Unwritten tech debt becomes forgotten tech debt.
