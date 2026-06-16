# System Architecture Overview

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Next.js 14+ (App Router) | TypeScript, Tailwind CSS, shadcn/ui |
| Backend | .NET 8 Web API | C#, REST, OpenAPI/Swagger |
| Database | PostgreSQL 15+ | via Entity Framework Core |
| Auth | Azure AD / NextAuth.js | SSO with Ovation M365 tenant |
| File Storage | Azure Blob Storage | Renderings, approval PDF exports |
| Cache | Redis | Budget calculation results, session data |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Next.js (Frontend)                │
│                                                      │
│  /projects        → Project list                    │
│  /projects/[id]   → Dashboard                       │
│  /projects/[id]/budget      → Master budget         │
│  /projects/[id]/proposals   → L3 bid leveling       │
│  /projects/[id]/trades/[id] → Trade detail          │
│  /projects/[id]/benchmark   → Benchmarking          │
│  /projects/[id]/takeoffs    → Site work QTOs        │
│  /projects/[id]/approval    → Approval workflow     │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS / REST (JSON)
                     │ Bearer Token (Azure AD)
┌────────────────────▼────────────────────────────────┐
│                  .NET 8 Web API                      │
│                                                      │
│  /api/v1/projects                                    │
│  /api/v1/projects/{id}/budget                        │
│  /api/v1/projects/{id}/line-items                    │
│  /api/v1/projects/{id}/markups                       │
│  /api/v1/projects/{id}/trades                        │
│  /api/v1/projects/{id}/trades/{id}/proposals         │
│  /api/v1/projects/{id}/approval                      │
│  /api/v1/projects/{id}/benchmark                     │
│  /api/v1/projects/{id}/takeoffs                      │
│  /api/v1/reference/*                                 │
└──────────┬────────────────────┬───────────────────── ┘
           │                    │
┌──────────▼──────┐   ┌────────▼──────────┐
│   PostgreSQL    │   │   Redis Cache     │
│   (primary DB)  │   │   (budget calcs)  │
└─────────────────┘   └───────────────────┘
```

---

## Budget Level Feature Gates

The app enforces feature availability based on the project's current `budget_level`. The API returns the project's level in every response; the frontend gates UI accordingly.

| Feature | L0 | L1 | L2 | L3 |
|---------|----|----|----|----|
| Project header / unit mix | ✅ | ✅ | ✅ | ✅ |
| Line items (manual entry) | ✅ | ✅ | ✅ | ✅ |
| Historical / allowance sources | ✅ | ✅ | ✅ | ✅ |
| Markup configuration | ✅ | ✅ | ✅ | ✅ |
| Comparable project sources | ❌ | ✅ | ✅ | ✅ |
| Soft bid sources | ❌ | ❌ | ✅ | ✅ |
| Trade packages (bid leveling) | ❌ | ❌ | ❌ | ✅ |
| Proposal entry / bidder comparison | ❌ | ❌ | ❌ | ✅ |
| Site work takeoffs | ❌ | ❌ | ✅ | ✅ |
| Benchmark comparison | ❌ | ❌ | ✅ | ✅ |
| Budget approval + lock | ❌ | ❌ | ✅ | ✅ |
| SHA-256 tamper fingerprint | ❌ | ❌ | ✅ | ✅ |

---

## Calculation Flow

Budget totals are computed server-side on every save. The hierarchy is:

```
Line Items (each division)
    ↓
Division Subtotals
    ↓
Hard Cost Subtotal  =  all divisions EXCLUDING [01, 50, 51, 55, 98, 99, BR]
    ↓
General Requirements  =  hard cost × GR rate (6% default)
    ↓
Markup Base  =  hard cost + GR
    ↓
Bid Risk       =  markup_base × bid_risk_rate  (or fixed)
Contingency    =  markup_base × contingency_rate
Sub Bonds      =  markup_base × bonds_rate
GL Insurance   =  fixed_amount  (or markup_base × ins_rate)
Overhead       =  markup_base × oh_rate
Contractor Fee =  markup_base × fee_rate
    ↓
Total Project Cost  =  hard cost + GR + all markups
    ↓
Per-Unit Cost  =  total / total_units
Per-SF Cost    =  total / total_gsf
```

---

## Key Design Decisions

1. **Markup rates are project-level** — not global constants. Each project can have different rates.
2. **GL Insurance supports both modes** — percentage-based or fixed dollar amount, toggled per project.
3. **Cost codes are reference data** — the master CSI line item list lives in the DB and is seeded; projects copy from it.
4. **L3 trade mapping** — each line item's `group_key` links it to a trade package for bid leveling. If no trade maps to a group, the line item uses its stored value.
5. **Approved budgets are immutable** — once approved, a snapshot is SHA-256 hashed and stored. Any subsequent changes start a new version.
