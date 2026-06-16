# API — Markups

**Base:** `/api/v1/projects/{projectId}/budget-levels/{budgetLevelId}/markups`

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/markups` | Get all markup rows for the budget level |
| `PUT` | `/markups/{kind}` | Update one markup row by kind |
| `GET` | `/markups/preview` | Preview calculated totals with current markup rates |

---

## Markup Object

```json
{
  "id": "uuid",
  "kind": "contingency",
  "label": "Construction Contingency",
  "costCode": "55",
  "mode": "pct",          // 'pct' | 'fixed'
  "rate": 0.05,           // null when mode = 'fixed'
  "fixedAmount": null,    // null when mode = 'pct'
  "computedAmount": 1677256.00,  // calculated from current hard cost
  "sortOrder": 2,
  "isActive": true
}
```

---

## GET /markups

Returns all 7 markup rows with their computed amounts based on current line item totals.

**Response 200:**
```json
{
  "data": {
    "markups": [
      {
        "kind": "general_requirements",
        "label": "General Requirements",
        "costCode": "01",
        "mode": "pct",
        "rate": 0.06,
        "fixedAmount": null,
        "computedAmount": 1765533.00
      },
      {
        "kind": "bid_risk",
        "label": "Bid Risk",
        "costCode": "BR",
        "mode": "pct",
        "rate": 0.02,
        "fixedAmount": null,
        "computedAmount": 550345.00
      },
      {
        "kind": "contingency",
        "label": "Construction Contingency",
        "costCode": "55",
        "mode": "pct",
        "rate": 0.05,
        "fixedAmount": null,
        "computedAmount": 1677256.00
      },
      {
        "kind": "bonds",
        "label": "Sub Bonds",
        "costCode": "50",
        "mode": "pct",
        "rate": 0.011,
        "fixedAmount": null,
        "computedAmount": 357724.00
      },
      {
        "kind": "insurance",
        "label": "GL Insurance",
        "costCode": "51",
        "mode": "fixed",
        "rate": null,
        "fixedAmount": 292005.00,
        "computedAmount": 292005.00
      },
      {
        "kind": "overhead",
        "label": "Overhead",
        "costCode": "99",
        "mode": "pct",
        "rate": 0.02,
        "fixedAmount": null,
        "computedAmount": 588511.00
      },
      {
        "kind": "fee",
        "label": "Contractor Fee",
        "costCode": "98",
        "mode": "pct",
        "rate": 0.06,
        "fixedAmount": null,
        "computedAmount": 1765533.00
      }
    ],
    "bases": {
      "hardCost": 29425560.00,
      "generalRequirements": 1765533.00,
      "markupBase": 31191093.00,
      "totalMarkups": 5231374.00,
      "totalProjectCost": 35222376.00,
      "costPerUnit": 185380.93,
      "costPerSF": 184.19
    }
  }
}
```

---

## PUT /markups/{kind}

Update one markup by its `kind` value.

**Path values for `{kind}`:** `general_requirements`, `bid_risk`, `contingency`, `bonds`, `insurance`, `overhead`, `fee`

**Request body (change rate):**
```json
{
  "mode": "pct",
  "rate": 0.06
}
```

**Request body (switch insurance to fixed):**
```json
{
  "mode": "fixed",
  "fixedAmount": 315000.00
}
```

**Response 200:** Returns the updated markup object plus recalculated `bases`.

**Constraints:**
- Cannot update markups on a `Locked` budget level (returns 409)
- `rate` is required when `mode = 'pct'`; `fixedAmount` is required when `mode = 'fixed'`
- `rate` must be between 0 and 1 (0% to 100%)

---

## GET /markups/preview

Returns what the totals would look like if you changed a rate — without saving.

**Query params:**

| Param | Type | Description |
|-------|------|-------------|
| `kind` | string | Which markup to preview |
| `mode` | string | `pct` or `fixed` |
| `rate` | number | New rate (for `pct` mode) |
| `fixedAmount` | number | New amount (for `fixed` mode) |

**Response 200:** Same shape as the `bases` object in GET /markups.
