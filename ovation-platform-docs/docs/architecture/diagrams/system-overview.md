# System Overview

**Status:** `[COMPLETE]`

---

## Full Stack Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER                              │
│                                                             │
│   Next.js 14 (App Router) + TypeScript                      │
│   ┌──────────────┐  ┌───────────────┐  ┌────────────────┐  │
│   │  shadcn/ui   │  │ TanStack Table│  │    Recharts    │  │
│   │  Tailwind    │  │  (Bid tables) │  │   (Charts)     │  │
│   └──────────────┘  └───────────────┘  └────────────────┘  │
│   ┌──────────────┐  ┌───────────────┐                       │
│   │   Zustand    │  │  React Query  │                       │
│   │ (UI state)   │  │(Server state) │                       │
│   └──────────────┘  └───────────────┘                       │
└─────────────────────┬───────────────────────────────────────┘
                      │  HTTPS / REST + WebSocket (SignalR)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AZURE APP SERVICE                          │
│                                                             │
│   .NET 8 Web API (Minimal APIs)                             │
│   ┌──────────────┐  ┌───────────────┐  ┌────────────────┐  │
│   │  Endpoints   │  │   Services    │  │  Background    │  │
│   │  (REST API)  │  │ (Biz Logic)   │  │  Jobs (Files)  │  │
│   └──────────────┘  └───────────────┘  └────────────────┘  │
│   ┌──────────────┐  ┌───────────────┐  ┌────────────────┐  │
│   │  EF Core 8   │  │   SignalR     │  │  ClosedXML /   │  │
│   │  (ORM)       │  │  (Real-time)  │  │  CsvHelper     │  │
│   └──────────────┘  └───────────────┘  └────────────────┘  │
└───────┬──────────────────┬─────────────────┬───────────────┘
        │                  │                 │
        ▼                  ▼                 ▼
┌──────────────┐  ┌────────────────┐  ┌──────────────────┐
│  AZURE SQL   │  │  AZURE BLOB    │  │    AZURE AD      │
│              │  │  STORAGE       │  │                  │
│  Projects    │  │                │  │  SSO / JWT       │
│  BudgetLevel │  │  Raw uploads   │  │  Role claims     │
│  LineItems   │  │  (Excel/CSV)   │  │                  │
│  Users       │  │  Export files  │  └──────────────────┘
│  AuditLog    │  │                │
│  etc.        │  └────────────────┘
└──────────────┘
        │
        ▼
┌──────────────────────────────┐
│  AZURE COMMUNICATION SERVICES│
│  Email notifications         │
└──────────────────────────────┘
```

---

## Data Flow — File Upload

```
User uploads Excel file
        │
        ▼
Next.js FileUploadZone
        │  multipart/form-data
        ▼
POST /api/files/upload
        │
        ├── Save raw file → Azure Blob Storage
        ├── Create UploadedFile record in Azure SQL (status: "queued")
        └── Return 202 Accepted + fileId
                │
                ▼  (async — background job picks up)
        FileProcessingJob (IHostedService)
                │
                ├── ExcelParserService / CsvParserService
                │     └── FieldMapperService (auto-detect columns)
                │           └── If no match → return unmapped columns
                │
                ├── Save parsed rows → BudgetLevelLineItem
                ├── Update UploadedFile status: "complete" | "needs-mapping"
                └── SignalR → BudgetHub → Frontend
                        │
                        ▼
        Frontend receives SignalR event
                │
                ├── If "complete" → refresh table data
                └── If "needs-mapping" → open ColumnMapper modal
```

---

## Data Flow — Real-time Collaboration

```
User A edits a line item cell
        │
        ▼
React Query optimistic update (instant UI)
        │
        ▼
PUT /api/line-items/:id
        │
        ├── Validate + save to Azure SQL
        ├── Write to AuditLog
        └── SignalR broadcast to project group
                │
                ▼
All other users in the same project/level
receive SignalR event → React Query cache update → UI updates
```

---

## Data Flow — Approval Workflow

```
Estimator clicks "Submit for Approval"
        │
        ▼
POST /api/budget-levels/:id/submit
        │
        ├── Validate: level is in "Draft" status
        ├── Update BudgetLevel.status → "Submitted"
        ├── Create Notification for all Managers on this project
        ├── Send email via Azure Communication Services
        └── Return updated level
                │
                ▼
Manager opens notification → reviews budget
        │
        ├── POST /api/budget-levels/:id/approve
        │     ├── Update status → "Approved"
        │     ├── Lock all BudgetLevelLineItems (is_locked = true)
        │     └── Notify Estimator
        │
        └── POST /api/budget-levels/:id/reject
              ├── Update status → "Draft"
              ├── Save rejection comment
              └── Notify Estimator
```

---

## Authentication Flow

```
User opens the app
        │
        ▼
NextAuth.js checks session cookie
        │
        ├── Session valid → proceed
        └── No session → redirect to /login
                │
                ▼
User clicks "Sign in with Microsoft"
        │
        ▼
Azure AD OAuth 2.0 flow (Microsoft login page)
        │
        ▼
Azure AD returns JWT token + user claims
        │
        ▼
NextAuth.js creates session
        │
        ▼
.NET API validates JWT on every request
via Microsoft.Identity.Web middleware
        │
        ├── Token valid → extract user ID + role claims
        └── Token invalid → 401 Unauthorized
```
