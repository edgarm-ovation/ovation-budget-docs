# API — Budget Summary

**Base:** `/api/v1/projects/{projectId}/budget-levels/{budgetLevelId}`

These endpoints return computed totals, comparisons, and exports.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/summary` | Computed budget totals and per-unit/SF metrics |
| `GET` | `/dashboard` | Dashboard card data (for the project overview) |
| `GET` | `/takeoffs` | Site work QTO table (L2 vs L3 side-by-side) |
| `PUT` | `/takeoffs/{takeoffId}` | Update a takeoff row quantity or price |
| `GET` | `/benchmark` | Per-unit cost comparison vs comparable projects |
| `POST` | `/export` | Generate PDF or Excel export |

---

## GET /summary

Returns the full cost breakdown with division subtotals and markups.

**Response 200:**
```json
{
  "data": {
    "projectId": "uuid",
    "budgetLevelId": "uuid",
    "level": 2,
    "status": "Draft",
    "updatedAt": "2025-08-01T00:00:00Z",

    "divisions": [
      { "code": "01", "name": "General Requirements", "total": 1765533.00 },
      { "code": "02", "name": "Existing Conditions",  "total": 18000.00 },
      { "code": "03", "name": "Concrete",             "total": 4821000.00 },
      { "code": "04", "name": "Masonry",              "total": 310000.00 },
      { "code": "05", "name": "Metals",               "total": 980000.00 },
      { "code": "06", "name": "Wood / Plastics",      "total": 5289000.00 },
      { "code": "07", "name": "Thermal & Moisture",   "total": 2100000.00 },
      { "code": "08", "name": "Openings",             "total": 1450000.00 },
      { "code": "09", "name": "Finishes",             "total": 3200000.00 },
      { "code": "10", "name": "Specialties",          "total": 320000.00 },
      { "code": "11", "name": "Equipment",            "total": 180000.00 },
      { "code": "12", "name": "Furnishings",          "total": 620000.00 },
      { "code": "13", "name": "Special Construction", "total": 890000.00 },
      { "code": "14", "name": "Conveying Equipment",  "total": 750000.00 },
      { "code": "21", "name": "Fire Suppression",     "total": 480000.00 },
      { "code": "22", "name": "Plumbing",             "total": 1820000.00 },
      { "code": "23", "name": "HVAC",                 "total": 1150000.00 },
      { "code": "26", "name": "Electrical",           "total": 2980000.00 },
      { "code": "27", "name": "Communications",       "total": 210000.00 },
      { "code": "28", "name": "Electronic Safety",    "total": 190000.00 },
      { "code": "31", "name": "Earthwork",            "total": 820000.00 },
      { "code": "32", "name": "Exterior Improvements","total": 1240000.00 },
      { "code": "33", "name": "Utilities",            "total": 890000.00 },
      { "code": "48", "name": "Electrical Power Gen", "total": 120000.00 },
      { "code": "49", "name": "Field Surveys",        "total": 95000.00 },
      { "code": "FFE","name": "FF&E",                 "total": 708200.00 }
    ],

    "totals": {
      "hardCost": 29425560.00,
      "generalRequirements": 1765533.00,
      "markupBase": 31191093.00,
      "bidRisk": 550345.00,
      "contingency": 1677256.00,
      "subBonds": 357724.00,
      "glInsurance": 292005.00,
      "overhead": 588511.00,
      "contractorFee": 1765533.00,
      "totalMarkups": 5231374.00,
      "totalProjectCost": 35222376.00
    },

    "metrics": {
      "costPerUnit": 185380.93,
      "costPerGrossSF": 184.19,
      "hardCostPerUnit": 154871.37,
      "hardCostPerGrossSF": 153.92
    }
  }
}
```

---

## GET /takeoffs

Returns the site work quantity takeoff table with L2 vs L3 side-by-side.

**Response 200:**
```json
{
  "data": {
    "trades": [
      {
        "tradeKey": "grading-pavings",
        "title": "Grading & Paving",
        "totalL2": 1240000.00,
        "totalL3": 1185000.00,
        "variance": -55000.00,
        "rows": [
          {
            "id": "uuid",
            "description": "Mass Grading",
            "uom": "CY",
            "quantityL2": 45000,
            "unitPriceL2": 12.00,
            "totalL2": 540000.00,
            "quantityL3": 42000,
            "unitPriceL3": 12.00,
            "totalL3": 504000.00
          }
        ]
      },
      {
        "tradeKey": "wet-utilities",
        "title": "Wet Utilities",
        "totalL2": 890000.00,
        "totalL3": 920000.00,
        "variance": 30000.00,
        "rows": [ ... ]
      }
    ]
  }
}
```

---

## PUT /takeoffs/{takeoffId}

Update quantity or price on a single takeoff row.

**Request body:**
```json
{
  "quantityL3": 42000,
  "unitPriceL3": 12.50
}
```

**Response 200:** Returns the updated takeoff row.

---

## GET /benchmark

Returns per-unit cost comparison against comparable Ovation projects.

**Response 200:**
```json
{
  "data": {
    "currentProject": {
      "name": "Gagnier Senior",
      "totalUnits": 190,
      "costPerUnit": 185381,
      "hardCostPerUnit": 154871
    },
    "comparables": [
      {
        "name": "Bruner",
        "totalUnits": 240,
        "costPerUnit": 178000,
        "hardCostPerUnit": 148000,
        "contractDate": "2023-06-01"
      },
      {
        "name": "Torrey Pines",
        "totalUnits": 180,
        "costPerUnit": 192000,
        "hardCostPerUnit": 160000,
        "contractDate": "2024-01-15"
      },
      {
        "name": "Decatur",
        "totalUnits": 200,
        "costPerUnit": 181000,
        "hardCostPerUnit": 151000,
        "contractDate": "2023-09-01"
      }
    ]
  }
}
```

---

## POST /export

Generates a PDF or Excel export of the budget.

**Request body:**
```json
{
  "format": "pdf",            // 'pdf' | 'xlsx'
  "sections": ["master", "markups", "benchmark"],
  // 'master' | 'markups' | 'benchmark' | 'takeoffs' | 'trades' | 'approval'
  "includeLineItemDetail": true
}
```

**Response 202:**
```json
{
  "data": {
    "jobId": "uuid",
    "statusUrl": "/api/v1/exports/uuid/status"
  }
}
```

Poll `statusUrl` until `status = 'complete'`, then download from `downloadUrl`.
