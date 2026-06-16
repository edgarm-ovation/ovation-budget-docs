# API — Line Items

**Base:** `/api/v1/projects/{projectId}/budget-levels/{budgetLevelId}/line-items`

Line items are scoped to a specific `BudgetLevel`, not to the project directly.
A project with L2 and L3 budgets has two independent sets of line items.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/line-items` | Get all line items for the budget level |
| `GET` | `/line-items?divisionCode=03` | Filter by CSI division |
| `GET` | `/line-items/{lineItemId}` | Get one line item |
| `PUT` | `/line-items/{lineItemId}` | Update a line item |
| `POST` | `/line-items` | Add a custom line item |
| `DELETE` | `/line-items/{lineItemId}` | Remove a custom line item |
| `POST` | `/line-items/batch` | Update multiple line items in one call |

---

## Line Item Object

```json
{
  "id": "uuid",
  "budgetLevelId": "uuid",
  "lineItemId": 42,           // null if custom
  "isCustom": false,
  "costCode": "06-1100",
  "description": "Framing",
  "divisionCode": "06",
  "divisionName": "Div 6 — Wood, Plastics & Composites",
  "category": "S",            // 'S' | 'A' | 'RR' | 'B' | 'F' | 'R'
  "subJob": "BUILDING",       // see SubJob enum
  "source": "Bruner",         // comparable project name or 'Allowance' | 'Budget' | 'Proposal' | etc.
  "unitOfMeasure": "SF",
  "takeoffQuantity": 423131,
  "takeoffUnitPrice": 12.50,
  "escalationPct": 0.0,
  "takeoffAmount": 5289137.50,
  "proposalAmount": 5150000.00,    // L3 only; null for L0–L2
  "preferredSource": "proposal",   // L3 only: 'takeoff' | 'proposal'
  "effectiveAmount": 5150000.00,   // = proposalAmount if preferredSource='proposal', else takeoffAmount
  "groupKey": "06-1100-framing",   // used for trade package mapping in L3
  "assumption": null,
  "notes": null,
  "section": "standard",
  "isLocked": false,
  "updatedAt": "2025-08-01T00:00:00Z"
}
```

---

## GET /line-items

Returns all line items grouped by division.

**Query params:**

| Param | Type | Description |
|-------|------|-------------|
| `divisionCode` | string | Filter to a single division, e.g. `03` |
| `subJob` | string | Filter by sub-job, e.g. `BUILDING` |
| `category` | string | Filter by category: `S`, `A`, `RR`, `B` |
| `includeMarkups` | bool | Include markup rows (default `true`) |

**Response 200:**
```json
{
  "data": {
    "divisions": [
      {
        "code": "03",
        "name": "Div 3 — Concrete",
        "subtotal": 4821000.00,
        "lineItems": [
          {
            "id": "uuid",
            "costCode": "03-3101",
            "description": "Slabs",
            "category": "S",
            "subJob": "BUILDING",
            "source": "Bruner",
            "unitOfMeasure": "SF",
            "takeoffQuantity": 423131,
            "takeoffUnitPrice": 9.50,
            "escalationPct": 0.0,
            "takeoffAmount": 4019744.50,
            "proposalAmount": null,
            "preferredSource": "takeoff",
            "effectiveAmount": 4019744.50,
            "groupKey": "03-3101-slabs",
            "isLocked": false
          }
        ]
      }
    ],
    "summary": {
      "hardCost": 28900000.00,
      "generalRequirements": 1734000.00,
      "markupBase": 30634000.00,
      "totalCost": 35222376.00,
      "costPerUnit": 185381.98,
      "costPerSF": 184.19
    }
  }
}
```

---

## PUT /line-items/{lineItemId}

Update any editable field on a line item. All fields optional — send only what changed.
**Cannot update locked line items** (returns 409 if `isLocked = true`).

**Request body:**
```json
{
  "category": "A",
  "subJob": "POOL AREA",
  "source": "Allowance",
  "unitOfMeasure": "LS",
  "takeoffQuantity": 1,
  "takeoffUnitPrice": 150000.00,
  "escalationPct": 0.05,
  "proposalAmount": null,
  "preferredSource": "takeoff",
  "assumption": "Allowance pending contractor quote",
  "notes": "Covers labor and materials for pool deck tile"
}
```

**Response 200:** Returns the updated line item object.

---

## POST /line-items

Add a custom line item not in the master template.

**Request body:**
```json
{
  "divisionCode": "33",
  "costCode": "33-0171",
  "description": "Start Up Utilities",
  "category": "A",
  "subJob": "ON-SITE",
  "source": "Allowance",
  "unitOfMeasure": "LS",
  "takeoffQuantity": 1,
  "takeoffUnitPrice": 15000.00,
  "escalationPct": 0.0,
  "notes": "Utility activation fees"
}
```

**Response 201:** Returns the created line item with `isCustom: true`.

---

## POST /line-items/batch

Update multiple line items in one transaction. Useful for pasting data from Excel.

**Request body:**
```json
{
  "updates": [
    {
      "id": "uuid-1",
      "takeoffQuantity": 423131,
      "takeoffUnitPrice": 9.50
    },
    {
      "id": "uuid-2",
      "takeoffQuantity": 190,
      "takeoffUnitPrice": 5500.00,
      "escalationPct": 0.10
    }
  ]
}
```

**Response 200:**
```json
{
  "data": {
    "updated": 2,
    "failed": 0,
    "errors": []
  }
}
```

---

## DELETE /line-items/{lineItemId}

Only allowed for custom line items (`isCustom: true`).
Standard (seeded) line items can be zeroed out but not deleted.

**Response 204:** No body.
