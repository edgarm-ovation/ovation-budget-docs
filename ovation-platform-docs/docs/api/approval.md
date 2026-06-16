# API — Budget Approval

**Base:** `/api/v1/projects/{projectId}/budget-levels/{budgetLevelId}/approval`

The approval workflow locks a budget level and creates an immutable signed snapshot.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/approval` | Get current approval status |
| `POST` | `/approval/submit` | Submit budget for approval review |
| `POST` | `/approval/approve` | Approve and lock the budget (requires `approver` role) |
| `POST` | `/approval/reject` | Reject — auto-creates next sub-level as new Draft |
| `GET` | `/approval/verify` | Verify the SHA-256 hash of the locked snapshot |
| `POST` | `/promote` | Promote approved level to next major level (e.g., L2 → L3) |

---

## Approval Status Object

```json
{
  "budgetLevelId": "uuid",
  "status": "Approved",
  "submittedAt": "2025-07-30T15:00:00Z",
  "submittedBy": "Edgar Martinez",
  "approvedAt": "2025-08-01T09:00:00Z",
  "approvedBy": "Reinier Santana",
  "sha256Hash": "a1b2c3d4...64chars...",
  "approvalId": "uuid",
  "version": "v94"
}
```

---

## POST /approval/submit

Moves the budget level to `Status = 'Submitted'` and notifies all users with `approver` role on this project.

**Request body:**
```json
{
  "notes": "Ready for executive review — all trades reconciled against L2 baseline."
}
```

**Response 200:**
```json
{
  "data": {
    "budgetLevelId": "uuid",
    "status": "Submitted",
    "submittedAt": "2025-07-30T15:00:00Z",
    "notifiedUsers": ["user1@ovationco.com", "user2@ovationco.com"]
  }
}
```

---

## POST /approval/approve

Requires `approver` role. Signs the budget and creates an immutable `BudgetApprovals` record.

1. Computes SHA-256 of the full budget JSON snapshot
2. Stores the snapshot in `BudgetApprovals.SnapshotJson`
3. Sets `BudgetLevels.Status = 'Locked'`
4. Sets `BudgetLevelLineItems.IsLocked = 1` for all rows

**Request body:**
```json
{
  "approvedBy": "Reinier Santana",
  "signatureData": "data:image/png;base64,iVBORw0...",
  "notes": "Approved for bidding. Do not modify without re-approval."
}
```

**Response 200:**
```json
{
  "data": {
    "approvalId": "uuid",
    "sha256Hash": "a1b2c3d4e5f6...64chars...",
    "approvedAt": "2025-08-01T09:00:00Z",
    "budgetLevelStatus": "Locked",
    "totalProjectCost": 35222376.00
  }
}
```

---

## POST /approval/reject

Rejects the current sub-level and **automatically creates the next sub-level** as a new `Draft`, copying all line items, markups, and takeoffs from the rejected version. The rejected sub-level becomes immutable.

**Request body:**
```json
{
  "comment": "Framing contingency needs to be increased to 8% per risk review."
}
```

**Response 200:**
```json
{
  "data": {
    "rejectedBudgetLevelId": "uuid",
    "rejectedSubLevel": 1,
    "rejectionComment": "Framing contingency needs to be increased to 8% per risk review.",
    "newBudgetLevelId": "uuid",
    "newSubLevel": 2,
    "newStatus": "Draft",
    "displayName": "Level 2.2"
  }
}
```

The `newBudgetLevelId` is the ID the frontend should redirect to for continued editing.

---

## POST /promote

Available only when the current sub-level `Status = 'Approved'`.
Creates the first sub-level of the next major level (e.g., L2.x → L3.1), copying all line items and freezing `BaselineAmount` from the approved level's `TakeoffAmount`.

**Request body:** _(none required)_

**Response 201:**
```json
{
  "data": {
    "sourceBudgetLevelId": "uuid",
    "sourceLevel": 2,
    "sourceSubLevel": 2,
    "newBudgetLevelId": "uuid",
    "newLevel": 3,
    "newSubLevel": 1,
    "newStatus": "Draft",
    "displayName": "Level 3.1",
    "lineItemsCopied": 243,
    "baselineAmountFrozen": true
  }
}
```

**What the API does on promote:**
1. Creates a new `BudgetLevels` row: `Level = source.Level + 1`, `SubLevel = 1`, `ParentBudgetLevelId = source.Id`
2. Copies every `BudgetLevelLineItems` row from the source: sets `BaselineAmount = source.TakeoffAmount`, `ProposalAmount = null`, `PreferredSource = 'takeoff'`, `IsLocked = 0`
3. Copies all `Markups` rows with the same rates
4. Copies all `Takeoffs` rows into the `QuantityL2`/`UnitPriceL2`/`TotalL2` columns, leaving L3 columns null
5. Does NOT copy `TradePackages` or `Proposals` — those are entered fresh at L3

---

## GET /approval/verify

Verifies the integrity of the locked snapshot by recomputing the SHA-256 hash.
Use this to confirm a budget has not been tampered with after approval.

**Response 200:**
```json
{
  "data": {
    "isValid": true,
    "storedHash": "a1b2c3d4...64chars...",
    "recomputedHash": "a1b2c3d4...64chars...",
    "approvedAt": "2025-08-01T09:00:00Z",
    "approvedBy": "Reinier Santana"
  }
}
```

If hashes don't match, `isValid` is `false` and the response returns `422`.

---

## State Machine

```
                    ┌──────────────────────────────────────────┐
                    │  Per Sub-Level (e.g., L2.1)              │
                    │                                          │
  L2.1: Draft ──► Submitted ──► Approved ──► Locked           │
                      │                         │              │
                   Rejected                  promote           │
                      │                         ↓              │
              auto-create L2.2              L3.1: Draft        │
              (copy of L2.1)                                   │
                      │                                        │
              L2.2: Draft ──► ...                              │
                    └──────────────────────────────────────────┘

Rules:
- Only one sub-level per project+level can be Draft or Submitted at a time.
- Locked sub-levels are permanently immutable — no edits, ever.
- Promote is only available from an Approved (Locked) sub-level.
- Reject always auto-creates the next sub-level (SubLevel + 1).
```
