# OVATION ESTIMATION ASSISTANT — DATA SCHEMA ANALYSIS

**Date:** June 17, 2026  
**Status:** Foundation Design (Ready for Implementation)  
**Environment:** Azure SQL Database  

---

## EXECUTIVE SUMMARY

The Estimation Assistant manages budgets across four distinct levels (0–3), with each level representing increasing refinement and scope definition. The schema is designed to:

- **Store** historical project data, assumptions, and takeoffs
- **Protect** budget integrity through role-based access control and audit logging
- **Support** AI-assisted estimation by providing clean, normalized cost data
- **Track** changes across budget versions and scenarios
- **Enable** comparison of estimates to actuals and between comparable projects

---

## SCHEMA ARCHITECTURE

### Core Principle: Budget Hierarchy

```
Project (1)
  ├─ Scenarios (N) — Phase 1, Phase 2, alternative mixes
  │   └─ Budgets (N) — Level 0, 1, 2, 3 per scenario
  │       ├─ PropertyDetails (1) — Site/building characteristics
  │       │   ├─ UnitMix (N) — Unit types and counts
  │       │   └─ ParkingBreakdown (N) — Parking by type
  │       ├─ LineItems (N) — CSI divisions (hierarchical)
  │       │   └─ TakeoffItems (N) — Quantities and unit costs
  │       ├─ Proposals (N) — Vendor pricing
  │       ├─ BudgetSummary (1) — Totals and metrics
  │       └─ BudgetAccessControl (N) — User roles and permissions
  └─ BudgetComparisons (N) — Level-to-level tracking
```

---

## TABLE DESCRIPTIONS & RATIONALE

### 1. PROJECTS
**Purpose:** Master record for all budgets

| Field | Type | Notes |
|-------|------|-------|
| ProjectId | GUID | Primary key |
| ProjectName | String | e.g., "Bruner Senior", "Robindale & 215" |
| ProductType | Enum | Senior, Workforce, Market Rate, Tax Credit |
| Location | String | Project location (e.g., Las Vegas, NV) |
| TimelineMonths | Int | Construction duration |
| CreatedAt, UpdatedAt | DateTime | Audit trail |
| IsActive | Bit | Soft delete; inactive projects still queryable |

**Rationale:**  
- Soft delete (`IsActive`) allows historical lookup without losing data
- `ProductType` enables filtering and comparable project selection
- One project can have multiple budgets at different levels

---

### 2. BUDGETS
**Purpose:** Version control for budgets at each level

| Field | Type | Notes |
|-------|------|-------|
| BudgetId | GUID | Primary key |
| ProjectId | GUID | FK to Projects |
| BudgetLevel | Int | 0–3; defines detail and estimation approach |
| BudgetVersion | Int | Version within level (e.g., Level 2 v1, Level 2 v2) |
| IsSubmitted | Bit | Indicates frozen state |
| ApprovedBy, ApprovedDate | String, DateTime | Sign-off audit trail |

**Rationale:**  
- Supports multiple revisions within each level (e.g., Level 2 revised after first bid round)
- `BudgetLevel` + `BudgetVersion` is unique; enforces one canonical budget per level-version pair
- Separation from Projects enables side-by-side comparison across levels

**Key Relationships:**
- **1:N with Projects** — One project has multiple budgets across levels
- **1:N with PropertyDetails** — Each budget has one set of property characteristics
- **1:N with LineItems** — Budget owns the full line item hierarchy
- **N:1 with Budgets (self-join)** — Can optionally reference prior version for delta tracking

---

### 3. PROPERTYDETAILS
**Purpose:** Capture site and building parameters that drive estimation

| Field | Type | Notes |
|-------|------|-------|
| PropertyDetailId | GUID | Primary key |
| BudgetId | GUID | FK to Budgets; 1:1 relationship |
| BuildingGSF | Decimal | Gross Square Footage |
| AcreageSize | Decimal | Land acreage |
| NumberOfFloors | Int | Number of stories |
| NumberOfBuildings | Int | Single vs. multi-building |
| TotalUnits | Int | Total unit count (sum of UnitMix) |
| ReportsAvailable | JSON | Geotechnical, environmental, survey status |

**Rationale:**  
- 1:1 with Budgets ensures each budget has one definitive set of property data
- Numeric fields (GSF, acreage) enable per-unit and per-SF cost calculations
- JSON field for reports (`geotechnical: "Y", environmental: "N"`) avoids additional tables for optional documents
- **Example calculation:** `CostPerGSF = TotalProjectCost / BuildingGSF`

**Dependent Tables:**
- **UnitMix** — Itemizes unit types and counts; supports unit-level costing
- **ParkingBreakdown** — Parking by type (covered, open, accessible) for takeoff estimation

---

### 4. UNITMI & PARKINGBREAKDOWN
**Purpose:** Sub-details of PropertyDetails; support granular takeoff

| Field (UnitMix) | Type | Notes |
|---|---|---|
| UnitMixId | GUID | PK |
| PropertyDetailId | GUID | FK |
| UnitType | String | '1BR-1BA', '2BR-2BA', etc. |
| NumberOfUnits | Int | Count for this type |
| AvgUnitSF | Decimal | Average SF per unit type |

**Rationale:**  
- Allows AI/estimation engine to propose costs by unit type, then sum
- Example: "1BR units at $X, 2BR at $Y" → total cost by composition
- Supports "what-if" scenario: change unit mix, recalculate budget

---

### 5. LINEITEM HIERARCHY
**Purpose:** Budget's P&L structure (CSI-based)

| Field | Type | Notes |
|-------|------|-------|
| LineItemId | GUID | Primary key |
| BudgetId | GUID | FK; all items belong to a budget |
| LineItemCode | String | CSI code: '03 00 00' (Concrete), '05 01 00' (Steel) |
| LineItemName | String | 'Concrete', 'Framing', 'HVAC Standard' |
| LineItemLevel | Int | 1 (Division), 2 (Section), 3 (Item) |
| ParentLineItemId | GUID | FK to parent; NULL for divisions |
| EstimatedAmount | Decimal | Rollup or direct estimate |
| Contingency | Decimal | Contingency $ allocated to this line |
| TotalAmount | Decimal | EstimatedAmount + Contingency |

**Rationale:**  
- **Hierarchical structure:** Divisions → Sections → Line items
  - Division: "General Requirements" (rolled up from sections)
  - Section: "Site Mobilization" (rolled up from items)
  - Item: "Survey Stakes" (direct cost)
- **Self-referencing FK** (`ParentLineItemId`) enables tree queries without additional tables
- **Contingency at each level** allows granular contingency management (e.g., higher on mechanical trades vs. site work)
- **CSI coding** ensures consistency with industry standards and comparable data

**Example Hierarchy:**
```
03 00 00 — Concrete (Division) ← EstimatedAmount = SUM(children)
  03 10 00 — Concrete Forming (Section)
    03 10 01 — Slab Forming (Item) ← Direct estimate from takeoff
    03 10 02 — Stair Forming (Item) ← Direct estimate
  03 20 00 — Concrete Reinforcing (Section)
    03 20 01 — Rebar (Item) ← Direct estimate
```

---

### 6. TAKEOFFITEMS
**Purpose:** Quantity takeoffs and unit pricing (especially for Level 3)

| Field | Type | Notes |
|-------|------|-------|
| TakeoffId | GUID | Primary key |
| LineItemId | GUID | FK; multiple takeoffs per line item possible |
| BudgetId | GUID | FK; for direct query without join |
| Quantity | Decimal | E.g., 5,000 (SF), 200 (EA), 150 (LF) |
| UnitOfMeasure | String | SF, LF, EA, LS, Count, SQ, etc. |
| UnitCost | Decimal | Cost per unit; refreshed by AI/manually |
| ExtensionAmount | Decimal | Qty × UnitCost; denormalized for perf |
| Source | String | 'Proposal', 'Historical', 'Estimate', 'Comparable' |
| IsProposalBased | Bit | 1 if from actual vendor proposal |
| ProposalRef | String | Link to Proposals table or external ID |

**Rationale:**  
- **Dual-track pricing** (proposal vs. estimate) matches Level 3 reality
  - When subcontractor proposes $X, populate `IsProposalBased = 1` and `Source = 'Proposal'`
  - Estimate stays as fallback/validation
- **Denormalized `ExtensionAmount`** speeds up budget total calculations
- **Source tracking** enables audit and identifies which estimates are validated by proposals
- **Multiple takeoffs per line item** supports breaking down complex items:
  - Framing → Roof Framing (SF), Wall Framing (SF), Floor Framing (SF)
  - Each takeoff can have separate source and timing

**Data Flow:**
1. **Level 0/1:** Takeoffs estimated from historical comparables
2. **Level 2:** Takeoffs based on detailed plans + soft bids
3. **Level 3:** Takeoffs refined to match 100% permit set; proposals replace estimates

---

### 7. PROPOSALS
**Purpose:** Track vendor bids and compare to estimate

| Field | Type | Notes |
|-------|------|-------|
| ProposalId | GUID | Primary key |
| BudgetId | GUID | FK |
| VendorName | String | Subcontractor/vendor name |
| TradeScope | String | 'Framing', 'HVAC', 'Electrical', 'Drywall' |
| ProposalAmount | Decimal | Total bid amount |
| ProposalDate | Date | When bid received |
| Status | String | 'Pending', 'Accepted', 'Rejected', 'Negotiating' |

**Rationale:**  
- Separate from takeoffs to avoid commingling estimate-based and proposal-based costs
- Enables QA: compare `Proposals.ProposalAmount` to sum of related takeoff items
- **Example logic:**
  - If proposal < estimate: opportunity to save or reallocate contingency
  - If proposal > estimate: review scope, negotiate, or draw contingency
- Timestamp fields enable historical tracking of bid environment

---

### 8. BUDGETSUMMARY
**Purpose:** Pre-calculated aggregates for fast reporting

| Field | Type | Notes |
|-------|------|-------|
| BudgetId | GUID | PK & FK; 1:1 with Budgets |
| TotalHardCost | Decimal | Sum of all line items (no soft costs) |
| TotalSoftCost | Decimal | A&E, permits, interest reserve, etc. |
| TotalContingency | Decimal | Sum of all contingencies |
| TotalProjectCost | Decimal | Hard + Soft + Contingency |
| CostPerUnit | Decimal | TPC / Units |
| CostPerGSF | Decimal | TPC / Building GSF |
| ContingencyPercent | Decimal | (Contingency / Hard) × 100 |

**Rationale:**  
- **Denormalized for performance** — avoids expensive aggregations on every report
- Triggers (or batch job) recalculate after budget changes
- Enables fast dashboard loads and comparisons
- Standard metrics for all reporting and estimation logic

---

### 9. BUDGETCOMPARISONS
**Purpose:** Cross-level and scenario comparison

| Field | Type | Notes |
|-------|------|-------|
| Level1BudgetId, Level2BudgetId, Level3BudgetId | GUID | FK to budgets at each level |
| Level1Cost, Level2Cost, Level3Cost | Decimal | Totals at each level |
| Level1To2Change, Level2To3Change | Decimal | Dollar variance |
| Level1To2ChangePercent, Level2To3ChangePercent | Decimal | % variance |

**Rationale:**  
- Supports standard reporting: "Level 2 came in 8% higher than Level 1 due to geotechnical findings"
- Single row per project; enables fast trend analysis
- Enables AI to learn why estimates change at each level

---

### 10. HISTORICALPROJECTS & COMPARABLES
**Purpose:** Data for AI estimation training and validation

**HistoricalProjects:**
- Past Ovation projects; used as training set for cost models
- Captured at completion: actual total cost, per-unit, per-GSF
- By product type (Senior, Workforce, etc.)

**ComparableProjects:**
- Other market projects (competitor, other developer)
- Used for sanity checks and benchmarking
- May come from market databases or public data

**Rationale:**  
- AI can learn: "Senior housing at this market averages $X/unit; our estimate is $Y, which is Z% above/below"
- Supports feasibility: "Is this estimate realistic vs. market?"
- Enables proposal validation: "Framing at $Y/SF is high vs. recent market at $X/SF"

---

### 11. BUDGETACCESSCONTROL & AUDITLOG
**Purpose:** Security and compliance

**AccessControl:**
- Role-based permissions per budget
- Roles: Viewer (read), Editor (read+write), Approver (sign-off), Admin (all)
- Auditable: who can do what and when

**AuditLog:**
- Every change logged: user, table, field, old/new value, timestamp, IP
- Supports regulatory requirements and dispute resolution
- Enables rollback of accidental changes

**Rationale:**  
- Budgets contain financial decisions; audit trail is critical
- Role separation protects budget integrity:
  - Field staff view only their property
  - Finance edits budget totals and contingency
  - Leadership approves and locks for submission

---

## KEY RELATIONSHIPS & INTEGRITY CONSTRAINTS

### Referential Integrity

```
Projects
  ├─→ Budgets (1:N) — Project has multiple budgets (one per level)
  │    ├─→ PropertyDetails (1:1) — Budget owns one property record
  │    │    ├─→ UnitMix (1:N) — Property has multiple unit types
  │    │    └─→ ParkingBreakdown (1:N) — Property has parking types
  │    ├─→ LineItems (1:N) — Budget owns line items (hierarchical)
  │    │    └─→ TakeoffItems (1:N) — Line items have takeoffs
  │    ├─→ Proposals (1:N) — Budget references vendor bids
  │    └─→ BudgetSummary (1:1) — Budget has one summary record
  ├─→ Scenarios (1:N) — Project has scenarios
  │    └─→ ScenarioBudgets (1:N) — Scenarios reference budgets
  └─→ BudgetComparisons (1:N) — Comparisons across budgets

LineItems (self-join)
  └─→ LineItems (ParentLineItemId) — Forms tree hierarchy

HistoricalProjects (1:N)
  └─→ HistoricalCosts — Cost data per project

BudgetAccessControl
  └─→ Budgets — Role assignment per budget
```

### Business Rules (Constraints)

1. **Budget Level Uniqueness**
   - Only one "Level 2 Version 1" per project
   - Prevents duplicate budget versions
   - ```sql
     UNIQUE(ProjectId, BudgetLevel, BudgetVersion)
     ```

2. **Property Uniqueness**
   - One PropertyDetails per Budget
   - Ensures single source of truth for site parameters

3. **Contingency Must Be Positive**
   - `CHECK (Contingency >= 0)`
   - Prevents negative contingencies

4. **Total = Estimated + Contingency**
   - Application enforces: `TotalAmount = EstimatedAmount + Contingency`
   - Audit trail captures changes

5. **Takeoff Quantity Must Be Positive**
   - `CHECK (Quantity > 0)`
   - Prevents absurd data

6. **Line Item Hierarchy**
   - Division level: ParentLineItemId IS NULL
   - Section level: ParentLineItemId references a Division
   - Item level: ParentLineItemId references a Section
   - No circular references (enforced by app logic)

---

## DATA FLOW EXAMPLES

### Example 1: Creating Level 1 Budget

```
1. Insert Projects("Bruner Senior")
2. Insert Budgets(ProjectId, Level=1, Version=1)
3. Insert PropertyDetails(BudgetId, BuildingGSF=196289, Acres=4.9, Units=194)
4. Insert UnitMix rows:
   - 1BR-1BA: 126 units, 663 SF avg
   - 2BR-1BA: 68 units, 675 SF avg
5. Insert LineItems (hierarchical):
   - Division: "03 00 00 Concrete" → EstimatedAmount = SUM(children)
     - Section: "03 10 00 Concrete Forming"
       - Item: "Slabs" → EstimatedAmount = 100,000 (from historical comparable)
       - Item: "Stairs" → EstimatedAmount = 50,000
6. Insert TakeoffItems (if detailed):
   - For "Slabs": Qty=5000 SF, UnitCost=$20, Extension=$100,000, Source="Historical"
7. Calculate & Insert BudgetSummary:
   - TotalHardCost = sum of all Items
   - TotalSoftCost = A&E + Permits
   - TotalContingency = 15% of Hard
   - TotalProjectCost = 82,500,000
   - CostPerUnit = 82,500,000 / 194 = 425,258
```

### Example 2: Level 2 → Level 3 Transition

```
1. Copy Level 2 budget structure to Level 3
2. For each LineItem, add/update TakeoffItems based on 100% CD set
3. For major trades, insert Proposals from subcontractors
4. Compare ProposalAmount to sum of TakeoffItems for each trade
5. If proposal < estimate: update TakeoffItems to match proposal, flag IsProposalBased=1
6. If proposal > estimate: flag for review; option to negotiate or adjust contingency
7. Recalculate BudgetSummary
8. Insert entry in BudgetComparisons with variance data
```

### Example 3: Feasibility Check (AI-Assisted)

```
1. Query HistoricalProjects WHERE ProductType='Senior' ORDER BY CompletionYear DESC
2. Calculate average CostPerUnit and CostPerGSF from recent projects
3. For new Level 0 budget:
   - Retrieve latest PropertyDetails and UnitMix
   - Apply historical $/unit and $/GSF to estimate total cost
4. Compare to manually entered Level 0 estimate
5. Flag if variance > 10%: "Your estimate is X% above/below similar projects"
6. Surface outlier line items for review
```

---

## PERFORMANCE CONSIDERATIONS

### Indexing Strategy

Primary indexes (already in schema):
- `Budgets(ProjectId, BudgetLevel)` — Fast lookup of level-specific budgets
- `LineItems(BudgetId, ParentLineItemId)` — Efficient tree traversal
- `TakeoffItems(BudgetId, LineItemId)` — Quick cost aggregation
- `AuditLog(BudgetId, ChangeDate)` — Audit trail queries
- `BudgetAccessControl(UserId)` — Permission checks

### Query Examples

**Total project cost by level:**
```sql
SELECT BudgetLevel, SUM(TotalAmount) AS TotalCost
FROM LineItems
WHERE BudgetId = @BudgetId AND ParentLineItemId IS NULL
GROUP BY BudgetLevel;
```

**Line item detail with takeoff summary:**
```sql
SELECT
  li.LineItemName,
  SUM(t.ExtensionAmount) AS TotalTakeoff,
  COUNT(DISTINCT t.TakeoffId) AS TakeoffCount,
  SUM(CASE WHEN t.IsProposalBased = 1 THEN t.ExtensionAmount ELSE 0 END) AS ProposalAmount
FROM LineItems li
LEFT JOIN TakeoffItems t ON li.LineItemId = t.LineItemId
WHERE li.BudgetId = @BudgetId
GROUP BY li.LineItemName;
```

**Access control check:**
```sql
SELECT CanEdit, CanApprove
FROM BudgetAccessControl
WHERE BudgetId = @BudgetId AND UserId = @UserId;
```

---

## SCALABILITY & FUTURE EXTENSIONS

### Partitioning Strategy (If Needed)
- Partition `AuditLog` by `ChangeDate` (monthly or quarterly)
- Partition `HistoricalCosts` by `ProjectYear`
- Keeps large tables responsive as data grows

### Future Tables (Out of Scope for v1)
- **ChangeOrders** — Track cost changes during construction
- **ActualCosts** — Post-completion actuals tied to line items
- **RFQs/Quotes** — Pre-proposal vendor interactions
- **DocumentAttachments** — Links to PDF specs, bid docs, etc.
- **ScheduleLinks** — Tie budget items to critical path schedule activities

---

## SUMMARY TABLE

| Table | Purpose | Cardinality | Key Relationship |
|-------|---------|-------------|------------------|
| Projects | Master project record | — | Root |
| Budgets | Budget versions by level | 1:N per project | Core |
| PropertyDetails | Site/building parameters | 1:1 per budget | Detail |
| UnitMix | Unit type breakdown | 1:N per property | Detail |
| ParkingBreakdown | Parking by type | 1:N per property | Detail |
| LineItems | Budget structure (hierarchical) | 1:N per budget | Core |
| TakeoffItems | Quantities & unit costs | 1:N per line item | Detail |
| Proposals | Vendor bids | 1:N per budget | Validation |
| BudgetSummary | Pre-calculated totals | 1:1 per budget | Reporting |
| BudgetComparisons | Level-to-level variance | N per project | Analysis |
| BudgetAccessControl | Role-based permissions | 1:N per budget | Security |
| AuditLog | Change history | 1:N per budget | Compliance |
| HistoricalProjects | Past project data | — | Reference |
| HistoricalCosts | Historical cost lines | 1:N per project | Reference |
| ComparableProjects | Market benchmarks | 1:N per project | Reference |

---

## IMPLEMENTATION ROADMAP

**Phase 1 (Week 1–2):**
- Deploy schema to Azure SQL
- Create views for dashboard/reporting
- Implement role-based access control in app

**Phase 2 (Week 3–4):**
- Load historical project data
- Build estimation engine (AI logic) using historical averages
- Create line item templates for standard CSI codes

**Phase 3 (Week 5–6):**
- Implement audit logging and compliance reporting
- Build comparative analysis dashboard
- User acceptance testing with budgeting staff

**Phase 4 (Week 7+):**
- Production deployment
- Change order and actuals tracking (future enhancements)
- Integration with accounting system

---

**End of Document**
