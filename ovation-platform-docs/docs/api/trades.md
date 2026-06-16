# API — Trades (L3 Only)

**Base:** `/api/v1/projects/{projectId}/budget-levels/{budgetLevelId}/trades`

Trade packages are available only when `BudgetLevel.Level = 3`.
Attempting to access these endpoints on L0–L2 returns `403`.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/trades` | List all trade packages |
| `GET` | `/trades/{tradeId}` | Get trade detail with all proposals |
| `POST` | `/trades` | Create a trade package |
| `PUT` | `/trades/{tradeId}` | Update trade metadata |
| `POST` | `/trades/{tradeId}/award` | Award a trade to a bidder |
| `GET` | `/trades/{tradeId}/proposals` | List proposals for a trade |
| `POST` | `/trades/{tradeId}/proposals` | Add a proposal (bid) |
| `PUT` | `/trades/{tradeId}/proposals/{proposalId}` | Update a proposal |
| `DELETE` | `/trades/{tradeId}/proposals/{proposalId}` | Remove a proposal |
| `GET` | `/bidders` | List all bidder companies |
| `POST` | `/bidders` | Add a new bidder company |

---

## Trade Package Object

```json
{
  "id": "uuid",
  "tradeKey": "framing",
  "title": "Framing",
  "estimatedCostL2": 5289137.50,
  "status": "Awarded",          // 'Open' | 'Proposed' | 'Awarded'
  "awardedBidderId": "uuid",
  "awardedBidderName": "ABC Framing LLC",
  "awardedAmount": 5150000.00,
  "proposalCount": 3,
  "lowestBid": 5150000.00,
  "highestBid": 5620000.00,
  "varianceVsL2": -139137.50,   // awardedAmount - estimatedCostL2
  "groupKeys": ["06-1100-framing", "06-1109-cabana-framing"],
  "sortOrder": 5,
  "notes": null
}
```

---

## GET /trades

Returns all trade packages with summary data.

**Response 200:**
```json
{
  "data": {
    "trades": [
      {
        "id": "uuid",
        "tradeKey": "concrete-slab",
        "title": "Concrete Slab",
        "estimatedCostL2": 4019744.50,
        "status": "Awarded",
        "awardedAmount": 4100000.00,
        "proposalCount": 2,
        "varianceVsL2": 80255.50
      },
      {
        "id": "uuid",
        "tradeKey": "framing",
        "title": "Framing",
        "estimatedCostL2": 5289137.50,
        "status": "Open",
        "awardedAmount": null,
        "proposalCount": 3,
        "varianceVsL2": null
      }
    ],
    "summary": {
      "totalTrades": 26,
      "awarded": 2,
      "proposed": 8,
      "open": 16,
      "totalAwardedAmount": 5632041.00,
      "proposalCoverageL2Pct": 0.42
      // covered L2 ÷ hard cost L2 (excl. GR, markups)
    }
  }
}
```

---

## GET /trades/{tradeId}

Returns the full trade detail with all proposals and their line items (summary sheet view).

**Response 200:**
```json
{
  "data": {
    "id": "uuid",
    "tradeKey": "framing",
    "title": "Framing",
    "estimatedCostL2": 5289137.50,
    "status": "Open",
    "groupKeys": ["06-1100-framing"],
    "proposals": [
      {
        "id": "uuid",
        "bidderId": "uuid",
        "bidderName": "ABC Framing LLC",
        "baseBid": 5150000.00,
        "leveledBid": 5150000.00,
        "submittedBy": "John Smith",
        "revisionDate": "2025-07-15",
        "status": "Submitted",
        "isSelected": false,
        "lineItems": [
          {
            "label": "Labor — Wood Framing",
            "section": "LINE ITEMS",
            "amount": 3200000.00
          },
          {
            "label": "Materials — Lumber",
            "section": "LINE ITEMS",
            "amount": 1750000.00
          },
          {
            "label": "Crane Allowance",
            "section": "ADDITIONAL ITEMS",
            "amount": 200000.00
          }
        ]
      }
    ],
    "historicalBenchmark": {
      "costPerUnit": 13562.00,
      "source": "Bruner"
    }
  }
}
```

---

## POST /trades/{tradeId}/award

Awards the trade to a specific bidder and locks the amount into the L3 budget.
Updates the corresponding `BudgetLevelLineItems` with `ProposalAmount` = `awardedAmount`
and `PreferredSource = 'proposal'` for all group keys belonging to this trade.

**Request body:**
```json
{
  "proposalId": "uuid",
  "awardedAmount": 5150000.00,
  "notes": "Awarded to ABC Framing per bid leveling 2025-07-20"
}
```

**Response 200:**
```json
{
  "data": {
    "tradeId": "uuid",
    "status": "Awarded",
    "awardedBidderName": "ABC Framing LLC",
    "awardedAmount": 5150000.00,
    "lineItemsUpdated": 2
  }
}
```

---

## POST /trades/{tradeId}/proposals

Add a bidder's proposal to a trade package.

**Request body:**
```json
{
  "bidderId": "uuid",
  "baseBid": 5620000.00,
  "submittedBy": "Jane Doe",
  "revisionDate": "2025-07-10",
  "lineItems": [
    { "label": "Labor", "section": "LINE ITEMS", "amount": 3500000.00 },
    { "label": "Materials", "section": "LINE ITEMS", "amount": 1920000.00 },
    { "label": "Bond", "section": "ADDITIONAL ITEMS", "amount": 200000.00 }
  ],
  "notes": null
}
```

**Response 201:** Returns the created proposal object.

---

## GET /bidders

Returns all bidder companies in the system.

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "companyName": "NRC Concrete",
      "contactName": "Mike Johnson",
      "email": "mike@nrcconcrete.com",
      "phone": "702-555-0101",
      "isActive": true
    }
  ]
}
```

---

## POST /bidders

Creates a new bidder company (shared across all projects).

**Request body:**
```json
{
  "companyName": "Desert Steel Erectors",
  "contactName": "Carlos Ruiz",
  "email": "carlos@desertsteelerectors.com",
  "phone": "702-555-0200",
  "licenseNumber": "NV-C-12345"
}
```

**Response 201:** Returns the created bidder.
