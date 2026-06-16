# Tech Debt

**Status:** `[COMPLETE]`

> Tech debt is not failure — it is a deliberate trade of long-term quality for short-term speed. The rule is: write it down, assign a phase to address it, and never let it grow silently.

---

## Active Tech Debt

### TD-001 — No staging environment in Phase 1
**Accepted in:** Phase 1
**Address in:** Phase 2
**Risk:** Low — internal tool, 2 projects, small team
**What it means:** All deployments go directly from `main` to production. There is no staging slot for testing before release.
**Fix:** Add Azure App Service Deployment Slot (`staging`) in Phase 2. PR merges deploy to staging; a manual "swap" promotes to production.

---

### TD-002 — No automated tests in Phase 1
**Accepted in:** Phase 1
**Address in:** Phase 2
**Risk:** Medium — formula engine and file parser have no regression safety net
**What it means:** No unit tests, integration tests, or end-to-end tests are written in the first 8 weeks.
**Fix:** Phase 2 adds unit tests for `FormulaService` and `FileParserService` (the two highest-risk services). Integration tests for critical API endpoints. E2E tests with Playwright for the approval workflow.

---

### TD-003 — SignalR runs in-process (not managed)
**Accepted in:** Phase 1
**Address in:** Phase 3 (only if concurrent users exceed ~200)
**Risk:** Low at current scale
**What it means:** SignalR connections are managed by the .NET process itself. If the App Service restarts, active connections drop.
**Fix:** Add Azure SignalR Service (managed). Code change is 2 lines in `Program.cs`.

---

### TD-004 — Background job queue is in-memory
**Accepted in:** Phase 1
**Address in:** Phase 3 (only if upload volume exceeds ~20/day)
**Risk:** Low at current scale — if the API restarts during a file parse, the job is lost and the user re-uploads
**What it means:** `IHostedService` uses a `Channel<T>` (in-memory queue). Jobs do not survive an API restart.
**Fix:** Replace with Azure Service Bus queue. Job is persisted in the queue; restarting the API does not lose it.

---

### TD-005 — No rate limiting on the API
**Accepted in:** Phase 1
**Address in:** Phase 2
**Risk:** Low — internal users only, no external access
**What it means:** No protection against accidental or malicious repeated requests.
**Fix:** Add ASP.NET Core rate limiting middleware in Phase 2.

---

### TD-006 — AuditLog has no archiving strategy
**Accepted in:** Phase 1
**Address in:** Phase 3
**Risk:** Low in Phase 1 (2 projects), Medium in Phase 2 (all projects)
**What it means:** The AuditLog table grows unbounded. At high change volume across many projects, it will become the largest table in the database.
**Fix:** Add monthly partitioning in Phase 3. Records older than 2 years are moved to Azure Blob Storage as JSON files (cold archive) and removed from the live table.

---

### TD-007 — No OpenAPI type sharing with frontend
**Accepted in:** Phase 1
**Address in:** Phase 2
**Risk:** Medium — if an API response shape changes and the frontend type isn't updated, it's a silent bug
**What it means:** TypeScript types in `/frontend/types/api.ts` are written manually and must be kept in sync with the .NET DTOs by hand.
**Fix:** Generate TypeScript types from the .NET OpenAPI spec using `openapi-typescript`. Run as part of CI — any type mismatch fails the build.

---

## Resolved Tech Debt

*(Move items here when addressed, with the sprint/date they were fixed.)*

| ID | Description | Resolved in | Notes |
|---|---|---|---|
| — | — | — | — |
