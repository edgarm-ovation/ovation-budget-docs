# Backend Tech Stack

**Status:** `[COMPLETE]`
**Decision record:** [ADR-002 — Backend Framework](../architecture/decisions/ADR-002-backend-framework.md)

---

## Summary

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Framework | ASP.NET Core | .NET 8 (Minimal APIs) | REST API, middleware |
| Language | C# | 12 | Business logic, data models |
| ORM | Entity Framework Core | 8.x | Azure SQL, migrations |
| Real-time | SignalR | Built into .NET 8 | Collaboration, file progress |
| Excel parsing | ClosedXML | 0.102+ | Read .xlsx / .xls files |
| CSV parsing | CsvHelper | 30.x | Read .csv files |
| Background jobs | IHostedService | Built into .NET 8 | File processing queue |
| Auth | Microsoft.Identity.Web | 3.x | Azure AD JWT validation |
| Email | Azure Communication Services SDK | Latest | Notification emails |
| Validation | FluentValidation | 11.x | Request model validation |
| API docs | Swashbuckle (Swagger) | 6.x | OpenAPI spec generation |
| Logging | Serilog | 3.x | Structured logging to Azure |

---

## Why Each Choice

### .NET 8 Minimal APIs
Minimal APIs reduce boilerplate — an endpoint is a single function call in `Program.cs` or a small file in `/Endpoints`. For a 2-developer team, this means less scaffolding and faster iteration. The tradeoff (less structure than Controllers) is mitigated by consistent naming conventions and folder organization.

We use **.NET 8 LTS specifically** — not .NET 9 (non-LTS). The next upgrade target is .NET 10 LTS (late 2026).

### Entity Framework Core 8
EF Core handles all database interactions. Advantages for this project:
- Migration-based schema changes — every schema change is tracked, versioned, and reversible
- LINQ queries are type-safe — no raw SQL strings that can silently break
- Works identically with Azure SQL in production and SQLite in local dev
- Strongly typed models match the TypeScript types on the frontend

We do **not** use the EF Core scaffolding from an existing database — all models are code-first.

### SignalR
Two use cases: (1) real-time bid table collaboration — when user A changes a line item, user B's table updates without refreshing. (2) File parsing progress — when a background job finishes parsing an Excel file, the frontend receives a notification immediately.

SignalR uses WebSockets with automatic fallback to Server-Sent Events → Long Polling. No external infrastructure (Redis, etc.) required at current scale.

### ClosedXML
The most capable .NET library for reading Excel files without Excel installed on the server. Handles:
- .xlsx (OpenXML format)
- .xls (legacy format via NPOI bridge)
- Merged cells
- Named ranges
- Multiple worksheets
- Non-standard formatting that breaks simpler parsers

### IHostedService (Background Jobs)
File parsing runs as a background job — the API endpoint returns immediately (202 Accepted) and a hosted service processes the file asynchronously. This prevents large uploads from timing out the API response. No external queue infrastructure (Azure Service Bus, etc.) needed at current scale.

If job volume grows (Phase 3+), the `IHostedService` implementation is replaced with Azure Service Bus + Azure Functions with no change to the API contract.

### FluentValidation
All API request bodies are validated before reaching business logic. Validation rules are defined in separate `Validator` classes, keeping endpoint code clean. Returns structured 400 errors the frontend can display field-by-field.

---

## Folder Structure

```
backend/
├── Ovation.Api/
│   ├── Program.cs                    ← App bootstrap, middleware, DI
│   ├── appsettings.json              ← Base config (no secrets)
│   ├── appsettings.Development.json  ← Local dev config (gitignored)
│   │
│   ├── Endpoints/                    ← Minimal API endpoint definitions
│   │   ├── ProjectEndpoints.cs
│   │   ├── BudgetLevelEndpoints.cs
│   │   ├── LineItemEndpoints.cs
│   │   ├── BidEndpoints.cs
│   │   ├── FileEndpoints.cs
│   │   ├── UserEndpoints.cs
│   │   └── NotificationEndpoints.cs
│   │
│   ├── Services/                     ← Business logic
│   │   ├── FileParserService.cs      ← Orchestrates Excel + CSV parsing
│   │   ├── ExcelParserService.cs     ← ClosedXML implementation
│   │   ├── CsvParserService.cs       ← CsvHelper implementation
│   │   ├── FieldMapperService.cs     ← Auto-detect + manual mapping
│   │   ├── FormulaService.cs         ← Markup calculations + rollups
│   │   ├── ApprovalService.cs        ← Workflow state machine
│   │   ├── NotificationService.cs    ← In-app + email notifications
│   │   └── AuditService.cs           ← Change logging
│   │
│   ├── BackgroundJobs/
│   │   └── FileProcessingJob.cs      ← IHostedService for file parsing
│   │
│   ├── Hubs/
│   │   └── BudgetHub.cs              ← SignalR hub
│   │
│   ├── Models/                       ← EF Core entities
│   │   ├── Project.cs
│   │   ├── BudgetLevel.cs
│   │   ├── Division.cs
│   │   ├── LineItem.cs
│   │   ├── BudgetLevelLineItem.cs
│   │   ├── Proposal.cs
│   │   ├── Markup.cs
│   │   ├── User.cs
│   │   ├── Role.cs
│   │   ├── AuditLog.cs
│   │   ├── UploadedFile.cs
│   │   └── Notification.cs
│   │
│   ├── DTOs/                         ← Request/response shapes (not DB models)
│   │   ├── Requests/
│   │   └── Responses/
│   │
│   ├── Validators/                   ← FluentValidation rules
│   │
│   ├── Data/
│   │   ├── OvationDbContext.cs       ← EF Core DbContext
│   │   ├── Migrations/               ← EF Core migration files
│   │   └── SeedData.cs               ← Division + LineItem master data
│   │
│   └── Middleware/
│       ├── AuthMiddleware.cs         ← Azure AD JWT validation
│       ├── RoleMiddleware.cs         ← Role-based access checks
│       └── ErrorHandlingMiddleware.cs
```

---

## API Response Conventions

All API responses follow a consistent envelope:

```json
// Success
{
  "data": { ... },
  "meta": { "total": 100, "page": 1 }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid",
    "details": [
      { "field": "takeoffAmount", "message": "Must be greater than 0" }
    ]
  }
}
```

HTTP status codes:
- `200` — success (GET, PUT)
- `201` — created (POST)
- `202` — accepted (file upload — processing async)
- `400` — validation error
- `401` — not authenticated
- `403` — authenticated but not authorized
- `404` — resource not found
- `409` — conflict (e.g. approving an already-approved level)
- `500` — server error

---

## Environment Variables

```json
// appsettings.Development.json (gitignored)
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=OvationDev;..."
  },
  "AzureAd": {
    "TenantId": "...",
    "ClientId": "...",
    "ClientSecret": "..."
  },
  "Azure": {
    "BlobStorageConnectionString": "...",
    "CommunicationServicesConnectionString": "..."
  }
}
```

In production, all values come from Azure Key Vault via Managed Identity — nothing is stored in `appsettings.json`.

---

## Performance Targets

| Operation | Target |
|---|---|
| `GET /projects` | < 100ms |
| `GET /levels/:id/line-items` (50 rows) | < 200ms |
| `PUT /line-items/:id` (single cell save) | < 150ms |
| File upload response (202) | < 500ms |
| Excel parse (100 rows) | < 5s (background) |
| Excel parse (1000 rows) | < 30s (background) |
