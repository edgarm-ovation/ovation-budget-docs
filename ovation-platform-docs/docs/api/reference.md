# API — Reference Data

**Base:** `/api/v1/reference`

Static lookup tables used throughout the app. These are seeded on deployment and rarely change. Frontend should cache these at app startup.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/reference/divisions` | All CSI divisions |
| `GET` | `/reference/line-item-templates` | Master line item library |
| `GET` | `/reference/comparable-projects` | Ovation comparable projects |
| `GET` | `/reference/sub-jobs` | Sub-job enum values |
| `GET` | `/reference/categories` | Category enum values |
| `GET` | `/reference/sources` | Valid source values |
| `GET` | `/reference/unit-types` | Unit type options |

---

## GET /reference/divisions

```json
{
  "data": [
    { "code": "01",  "name": "Div 1 — General Requirements",       "isMarkup": false, "isFfe": false, "sortOrder": 1 },
    { "code": "02",  "name": "Div 2 — Existing Conditions",        "isMarkup": false, "isFfe": false, "sortOrder": 2 },
    { "code": "03",  "name": "Div 3 — Concrete",                   "isMarkup": false, "isFfe": false, "sortOrder": 3 },
    { "code": "04",  "name": "Div 4 — Masonry",                    "isMarkup": false, "isFfe": false, "sortOrder": 4 },
    { "code": "05",  "name": "Div 5 — Metals",                     "isMarkup": false, "isFfe": false, "sortOrder": 5 },
    { "code": "06",  "name": "Div 6 — Wood, Plastics & Composites","isMarkup": false, "isFfe": false, "sortOrder": 6 },
    { "code": "07",  "name": "Div 7 — Thermal & Moisture Prot.",   "isMarkup": false, "isFfe": false, "sortOrder": 7 },
    { "code": "08",  "name": "Div 8 — Openings",                   "isMarkup": false, "isFfe": false, "sortOrder": 8 },
    { "code": "09",  "name": "Div 9 — Finishes",                   "isMarkup": false, "isFfe": false, "sortOrder": 9 },
    { "code": "10",  "name": "Div 10 — Specialties",               "isMarkup": false, "isFfe": false, "sortOrder": 10 },
    { "code": "11",  "name": "Div 11 — Equipment",                 "isMarkup": false, "isFfe": false, "sortOrder": 11 },
    { "code": "12",  "name": "Div 12 — Furnishings",               "isMarkup": false, "isFfe": false, "sortOrder": 12 },
    { "code": "13",  "name": "Div 13 — Special Construction",      "isMarkup": false, "isFfe": false, "sortOrder": 13 },
    { "code": "14",  "name": "Div 14 — Conveying Equipment",       "isMarkup": false, "isFfe": false, "sortOrder": 14 },
    { "code": "21",  "name": "Div 21 — Fire Suppression",          "isMarkup": false, "isFfe": false, "sortOrder": 15 },
    { "code": "22",  "name": "Div 22 — Plumbing",                  "isMarkup": false, "isFfe": false, "sortOrder": 16 },
    { "code": "23",  "name": "Div 23 — HVAC",                      "isMarkup": false, "isFfe": false, "sortOrder": 17 },
    { "code": "26",  "name": "Div 26 — Electrical",                "isMarkup": false, "isFfe": false, "sortOrder": 18 },
    { "code": "27",  "name": "Div 27 — Communications",            "isMarkup": false, "isFfe": false, "sortOrder": 19 },
    { "code": "28",  "name": "Div 28 — Electronic Safety",         "isMarkup": false, "isFfe": false, "sortOrder": 20 },
    { "code": "31",  "name": "Div 31 — Earthwork",                 "isMarkup": false, "isFfe": false, "sortOrder": 21 },
    { "code": "32",  "name": "Div 32 — Exterior Improvements",     "isMarkup": false, "isFfe": false, "sortOrder": 22 },
    { "code": "33",  "name": "Div 33 — Utilities",                 "isMarkup": false, "isFfe": false, "sortOrder": 23 },
    { "code": "34",  "name": "Div 34 — Transportation",            "isMarkup": false, "isFfe": false, "sortOrder": 24 },
    { "code": "48",  "name": "Div 48 — Electrical Power Gen.",     "isMarkup": false, "isFfe": false, "sortOrder": 25 },
    { "code": "49",  "name": "Div 49 — Field Surveys & Staking",   "isMarkup": false, "isFfe": false, "sortOrder": 26 },
    { "code": "FFE", "name": "FF&E",                               "isMarkup": false, "isFfe": true,  "sortOrder": 27 },
    { "code": "01",  "name": "General Requirements",               "isMarkup": true,  "isFfe": false, "sortOrder": 28 },
    { "code": "BR",  "name": "Bid Risk",                           "isMarkup": true,  "isFfe": false, "sortOrder": 29 },
    { "code": "55",  "name": "Construction Contingency",           "isMarkup": true,  "isFfe": false, "sortOrder": 30 },
    { "code": "50",  "name": "Sub Bonds",                          "isMarkup": true,  "isFfe": false, "sortOrder": 31 },
    { "code": "51",  "name": "GL Insurance",                       "isMarkup": true,  "isFfe": false, "sortOrder": 32 },
    { "code": "99",  "name": "Overhead",                           "isMarkup": true,  "isFfe": false, "sortOrder": 33 },
    { "code": "98",  "name": "Contractor Fee",                     "isMarkup": true,  "isFfe": false, "sortOrder": 34 }
  ]
}
```

---

## GET /reference/comparable-projects

```json
{
  "data": [
    { "id": "uuid", "name": "Bruner",       "totalUnits": 240, "contractDate": "2023-06-01", "city": "Las Vegas", "state": "NV", "productType": "Affordable" },
    { "id": "uuid", "name": "Durango",      "totalUnits": 320, "contractDate": "2024-03-01", "city": "Las Vegas", "state": "NV", "productType": "Affordable" },
    { "id": "uuid", "name": "Torrey Pines", "totalUnits": 180, "contractDate": "2024-01-15", "city": "Las Vegas", "state": "NV", "productType": "Affordable" },
    { "id": "uuid", "name": "Pebble",       "totalUnits": 210, "contractDate": "2023-11-01", "city": "Las Vegas", "state": "NV", "productType": "Affordable" },
    { "id": "uuid", "name": "Decatur",      "totalUnits": 200, "contractDate": "2023-09-01", "city": "Las Vegas", "state": "NV", "productType": "Affordable" },
    { "id": "uuid", "name": "Flamingo",     "totalUnits": 160, "contractDate": "2024-06-01", "city": "Las Vegas", "state": "NV", "productType": "Senior"    },
    { "id": "uuid", "name": "South Nellis", "totalUnits": 150, "contractDate": "2023-04-01", "city": "Las Vegas", "state": "NV", "productType": "Affordable" },
    { "id": "uuid", "name": "West Henderson","totalUnits": 390, "contractDate": "2025-08-01", "city": "Henderson", "state": "NV", "productType": "Affordable" }
  ]
}
```

---

## GET /reference/sub-jobs

```json
{
  "data": [
    { "value": "BUILDING",     "label": "Building" },
    { "value": "ON-SITE",      "label": "On-Site" },
    { "value": "OFFSITE",      "label": "Off-Site" },
    { "value": "POOL AREA",    "label": "Pool Area" },
    { "value": "POOL EQUIP",   "label": "Pool Equipment" },
    { "value": "PUMPHOUSE",    "label": "Pump House" },
    { "value": "CARPORT",      "label": "Carport" },
    { "value": "COMMON AREA",  "label": "Common Area" },
    { "value": "DUMPSTERS",    "label": "Dumpsters" },
    { "value": "OTHER SITE",   "label": "Other Site" },
    { "value": "WET UTIL",     "label": "Wet Utilities" },
    { "value": "EV",           "label": "EV Charging" },
    { "value": "FFE",          "label": "FF&E" }
  ]
}
```

---

## GET /reference/categories

```json
{
  "data": [
    { "value": "S",  "label": "Standard",        "description": "Normal construction cost" },
    { "value": "A",  "label": "Allowance",        "description": "Estimated; final scope TBD" },
    { "value": "RR", "label": "Repair & Replace", "description": "Remediation of existing conditions" },
    { "value": "B",  "label": "Bond/Insurance",   "description": "Markup item (bonds, insurance)" },
    { "value": "F",  "label": "Fee",              "description": "Contractor fee markup" },
    { "value": "R",  "label": "Risk",             "description": "Bid risk or contingency" }
  ]
}
```

---

## GET /reference/sources

```json
{
  "data": [
    { "value": "Bruner",        "type": "comparable",  "level": 1 },
    { "value": "Durango",       "type": "comparable",  "level": 1 },
    { "value": "Torrey Pines",  "type": "comparable",  "level": 1 },
    { "value": "Pebble",        "type": "comparable",  "level": 1 },
    { "value": "Decatur",       "type": "comparable",  "level": 1 },
    { "value": "Flamingo",      "type": "comparable",  "level": 1 },
    { "value": "South Nellis",  "type": "comparable",  "level": 1 },
    { "value": "West Henderson","type": "comparable",  "level": 1 },
    { "value": "Soft Bid",      "type": "bid",         "level": 2 },
    { "value": "Proposal",      "type": "bid",         "level": 3 },
    { "value": "Budget",        "type": "takeoff",     "level": 0 },
    { "value": "Allowance",     "type": "allowance",   "level": 0 },
    { "value": "Historical",    "type": "historical",  "level": 0 },
    { "value": "N/A",           "type": "na",          "level": 0 }
  ]
}
```

The `level` field indicates the minimum budget level where this source type is appropriate.
