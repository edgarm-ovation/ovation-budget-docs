# 01 — Authentication & Roles

**Sprint:** Weeks 1–2 | **Status:** Planned

---

## Summary

Secure login via Azure AD (Ovation's existing M365 tenant) with four role tiers that control what each user can see and do. No separate credential management — users log in with their Ovation email.

---

## What It Does

- Single sign-on via Azure AD OAuth 2.0 / OIDC
- JWT-based session after login, passed on every API request
- Role assignment stored in the database; roles are project-scoped (a user can be Manager on one project and Viewer on another)
- Middleware on the backend enforces role checks per endpoint
- Frontend hides or disables actions the current user cannot perform

---

## Roles

| Role | What They Can Do |
|------|-----------------|
| **Admin** | Full access — manage users, all projects, all budget levels |
| **Manager** | Submit budgets for approval, approve/reject, view all data on assigned projects |
| **Estimator** | Edit budget data, upload files, select awarded bids |
| **Viewer** | Read-only — see budgets and exports, no edits |

---

## Key Workflows

1. User navigates to the app → redirected to Azure AD login
2. Azure AD returns token → backend validates and maps to internal User + Role records
3. User lands on project list filtered to their assigned projects
4. Every action (edit cell, upload file, approve) re-checks role server-side before executing

---

## Technical Notes

- Auth provider: Azure AD (Ovation M365 tenant)
- Token: JWT passed in `Authorization: Bearer` header
- Tables involved: `Users`, `Roles`, `UserRoles`, `ProjectUsers`
- Role check pattern: attribute-based middleware on .NET 8 API controllers

---

## Dependencies

- Requires Azure AD app registration (done outside the codebase)
- Feeds into every other feature — role gates are enforced app-wide

---

## Related Features

- [02 — Project & Budget Navigation](./02-project-navigation.md) — project list is filtered by `ProjectUsers`
- [07 — Approval Workflow](./07-approval-workflow.md) — approve/reject actions require Manager role

## Related Docs

- [ovation-platform-docs/security/](../../ovation-platform-docs/security/)
- [ovation-platform-docs/product/user-roles.md](../../ovation-platform-docs/product/user-roles.md)
