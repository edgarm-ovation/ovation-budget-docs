# API — Projects

**Base:** `/api/v1/projects`

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/projects` | List all projects the caller has access to |
| `POST` | `/projects` | Create a new project |
| `GET` | `/projects/{projectId}` | Get project detail |
| `PUT` | `/projects/{projectId}` | Update project header |
| `DELETE` | `/projects/{projectId}` | Soft-delete a project |
| `GET` | `/projects/{projectId}/unit-mix` | Get unit type breakdown |
| `PUT` | `/projects/{projectId}/unit-mix` | Replace unit mix rows |
| `GET` | `/projects/{projectId}/parking` | Get parking config |
| `PUT` | `/projects/{projectId}/parking` | Update parking config |

---

## GET /projects

Returns all projects the caller can access.

**Query params:** `page`, `pageSize`, `status` (`Active` | `OnHold` | `Closed`), `productType`

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "West Henderson Apartments",
      "address": "Henderson, NV 89002",
      "productType": "Affordable",
      "status": "Active",
      "totalUnits": 390,
      "grossSF": 423131,
      "budgetLevelCount": 2,
      "latestBudgetLevel": {
        "id": "uuid",
        "level": 3,
        "name": "Level 3 — August 2025",
        "status": "Draft"
      },
      "updatedAt": "2025-08-01T00:00:00Z"
    }
  ],
  "pagination": { "page": 1, "pageSize": 50, "total": 12 }
}
```

---

## POST /projects

Creates a project with a default L0 BudgetLevel and seeded line items.

**Request body:**
```json
{
  "name": "Gagnier Senior",
  "address": "Las Vegas, NV",
  "city": "Las Vegas",
  "state": "NV",
  "zip": "89101",
  "productType": "Senior",
  "totalUnits": 190,
  "grossSF": 191224,
  "livableSF": null,
  "siteSF": 180338,
  "siteAcres": 4.14,
  "floors": 4,
  "buildings": 1,
  "efficiencyPct": null,
  "startDate": "2026-01-01",
  "timelineMonths": 18,
  "preparedBy": "Edgar M.",
  "version": "4.13.26"
}
```

**Response 201:**
```json
{
  "data": {
    "id": "uuid",
    "name": "Gagnier Senior",
    "productType": "Senior",
    "status": "Active",
    "defaultBudgetLevelId": "uuid",
    "createdAt": "2025-08-01T00:00:00Z"
  }
}
```

> On creation, the API automatically:
> 1. Seeds a BudgetLevel at Level 0 with Status = 'Draft'
> 2. Clones all active LineItem templates into BudgetLevelLineItems with null values
> 3. Seeds default Markup rows (GR 6%, Contingency 5%, etc.)

---

## GET /projects/{projectId}

**Response 200:**
```json
{
  "data": {
    "id": "uuid",
    "name": "Gagnier Senior",
    "address": "Las Vegas, NV",
    "city": "Las Vegas",
    "state": "NV",
    "zip": "89101",
    "productType": "Senior",
    "status": "Active",
    "totalUnits": 190,
    "grossSF": 191224,
    "livableSF": null,
    "siteSF": 180338,
    "siteAcres": 4.14,
    "floors": 4,
    "buildings": 1,
    "efficiencyPct": null,
    "startDate": "2026-01-01",
    "timelineMonths": 18,
    "preparedBy": "Edgar M.",
    "version": "4.13.26",
    "budgetLevels": [
      { "id": "uuid", "level": 0, "name": "Level 0 — Initial", "status": "Draft" },
      { "id": "uuid", "level": 2, "name": "Level 2 — April 2026", "status": "Approved" }
    ],
    "createdAt": "2025-08-01T00:00:00Z",
    "updatedAt": "2025-08-01T00:00:00Z"
  }
}
```

---

## PUT /projects/{projectId}/unit-mix

Replaces all unit mix rows for the project. Send the full array each time.

**Request body:**
```json
{
  "unitMix": [
    { "unitType": "1BR-1BA", "count": 125 },
    { "unitType": "2BR-1BA", "count": 65 }
  ]
}
```

**Response 200:**
```json
{
  "data": {
    "unitMix": [
      { "id": "uuid", "unitType": "1BR-1BA", "count": 125, "pct": 0.6579 },
      { "id": "uuid", "unitType": "2BR-1BA", "count": 65,  "pct": 0.3421 }
    ],
    "totalUnits": 190
  }
}
```

---

## PUT /projects/{projectId}/parking

**Request body:**
```json
{
  "covered": 128,
  "coveredAccessible": 3,
  "open": 44,
  "openAccessible": 20,
  "waiver": 0
}
```

**Response 200:**
```json
{
  "data": {
    "covered": 128,
    "coveredAccessible": 3,
    "open": 44,
    "openAccessible": 20,
    "waiver": 0,
    "total": 195,
    "ratio": 1.03
  }
}
```
