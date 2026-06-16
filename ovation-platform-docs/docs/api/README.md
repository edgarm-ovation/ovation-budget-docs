# API Reference

**Base URL:** `/api/v1`
**Auth:** Bearer token (Azure AD JWT) on every request.
**Format:** JSON. All amounts in USD dollars as `number`. All dates as `YYYY-MM-DD` strings.

---

## Endpoint Index

| Resource | Endpoints |
|----------|-----------|
| [Projects](./projects.md) | CRUD for project headers, unit mix, parking |
| [Budget Levels](./budget-levels-api.md) | Create/read budget level snapshots per project |
| [Line Items](./line-items.md) | Read/write line items within a budget level |
| [Markups](./markups.md) | Read/write markup configuration per budget level |
| [Trades](./trades.md) | L3 trade packages, bidders, proposals, bid leveling |
| [Budget Summary](./budget.md) | Computed totals, per-unit/SF metrics |
| [Takeoffs](./takeoffs.md) | Site work quantity takeoffs (L2 vs L3) |
| [Approval](./approval.md) | Budget sign-off, SHA-256 fingerprint, locked snapshots |
| [Reference Data](./reference.md) | Divisions, comparable projects, sub-jobs, sources |

---

## Common Response Shapes

### Success

```json
{
  "data": { ... },
  "meta": {
    "requestId": "uuid",
    "timestamp": "2025-08-01T00:00:00Z"
  }
}
```

### Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "TakeoffQuantity must be a positive number",
    "field": "takeoffQuantity",
    "requestId": "uuid"
  }
}
```

### Paginated List

```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "pageSize": 50,
    "total": 243
  }
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | Deleted (no body) |
| `400` | Validation error |
| `401` | Missing / invalid token |
| `403` | Insufficient role |
| `404` | Resource not found |
| `409` | Conflict (e.g., budget already locked) |
| `422` | Business rule violation |
| `500` | Server error |

---

## Auth & Roles

| Role | Permissions |
|------|------------|
| `viewer` | GET all endpoints they have project access to |
| `editor` | GET + PUT/POST on line items, markups, trades |
| `approver` | editor + POST /approval |
| `admin` | all endpoints + user/project management |

---

## Global Query Parameters

Available on list endpoints:

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default: 1) |
| `pageSize` | int | Results per page (default: 50, max: 200) |
| `sort` | string | Field name to sort by |
| `dir` | `asc` \| `desc` | Sort direction |
