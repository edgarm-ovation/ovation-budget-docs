# QUICK REFERENCE — ESTIMATION ASSISTANT SCHEMA

## Table Directory

| Table | Purpose | Key Fields | Relationships |
|-------|---------|-----------|---|
| **Projects** | Master record | ProjectId, ProjectName, ProductType, Location, TimelineMonths | 1→N Budgets, Scenarios, ComparableProjects |
| **Budgets** | Budget versions by level | BudgetId, ProjectId, BudgetLevel (0–3), BudgetVersion, IsSubmitted, ApprovedBy | 1→N LineItems, PropertyDetails (1:1), Proposals, AuditLog |
| **PropertyDetails** | Site & building params | PropertyDetailId, BudgetId, BuildingGSF, AcreageSize, SiteSF, NumberOfBuildings, NumberOfFloors, TotalUnits | 1→N UnitMix, ParkingBreakdown |
| **UnitMix** | Unit type breakdown | UnitMixId, PropertyDetailId, UnitType, NumberOfUnits, AvgUnitSF | Supports unit-level costing |
| **ParkingBreakdown** | Parking by type | ParkingId, PropertyDetailId, ParkingType, Count | Supports parking takeoff |
| **LineItems** | CSI budget structure | LineItemId, BudgetId, LineItemCode, LineItemName, LineItemLevel (1–3), ParentLineItemId, EstimatedAmount, Contingency, TotalAmount | 1→N TakeoffItems, self-join (tree) |
| **TakeoffItems** | Qty takeoffs & unit costs | TakeoffId, LineItemId, BudgetId, Quantity, UnitOfMeasure, UnitCost, ExtensionAmount, Source (Proposal/Historical/Estimate), IsProposalBased | Links to Proposals |
| **Proposals** | Vendor bids | ProposalId, BudgetId, VendorName, TradeScope, ProposalAmount, ProposalDate, Status | Maps to LineItems via TakeoffItems |
| **BudgetSummary** | Pre-calc totals | SummaryId, BudgetId, TotalHardCost, TotalSoftCost, TotalContingency, TotalProjectCost, CostPerUnit, CostPerGSF, ContingencyPercent | Denormalized from LineItems |
| **BudgetComparisons** | Level variance | ComparisonId, ProjectId, Level1/2/3BudgetIds, Level1/2/3Costs, VarianceDollars, VariancePercent | Tracks progression 0→1→2→3 |
| **BudgetAccessControl** | Role-based access | AccessId, BudgetId, UserId, Role (Viewer/Editor/Approver/Admin), CanEdit, CanDelete, CanApprove | Enforced by app layer |
| **AuditLog** | Change history | AuditLogId, BudgetId, UserId, ActionType (Create/Update/Delete), TableName, FieldName, OldValue, NewValue, ChangeDate, IPAddress | Compliance & dispute resolution |
| **BudgetAssumptions** | Budget rules & params | AssumptionId, BudgetId, AssumptionCategory, AssumptionName, Value, UnitOfMeasure | Stores contingency %, markups, etc. |
| **HistoricalProjects** | Past project data | HistoricalProjectId, ProjectName, ProductType, CompletionYear, TotalUnits, BuildingGSF, TotalCost, CostPerUnit, CostPerGSF, ConstructionTimeline | AI training data |
| **HistoricalCosts** | Cost benchmarks | HistoricalCostId, LineItemCode, LineItemName, HistoricalProjectId, Amount, UnitOfMeasure, UnitCost, ProjectYear | Supports estimation |
| **ComparableProjects** | Market data | ComparableId, ProjectId, ComparableProjectName, Location, TotalUnits, BuildingGSF, TotalCost, CostPerUnit, CostPerGSF, ConstructionYear | Feasibility validation |
| **Scenarios** | Budget scenarios | ScenarioId, ProjectId, ScenarioName (Phase 1, Phase 2), IsActive | Groups budgets by phase |
| **ScenarioBudgets** | Scenario budget links | ScenarioBudgetId, ScenarioId, BudgetId | N:N join |

---

## Common Queries

### Get Latest Budget for Project (All Levels)
```sql
SELECT b.BudgetId, b.BudgetLevel, b.BudgetVersion, bs.TotalProjectCost, bs.CostPerUnit
FROM Budgets b
LEFT JOIN BudgetSummary bs ON b.BudgetId = bs.BudgetId
WHERE b.ProjectId = @ProjectId
  AND b.IsSubmitted = 1
ORDER BY b.BudgetLevel DESC, b.BudgetVersion DESC;
```

### Get Full LineItem Hierarchy for Budget
```sql
WITH RECURSIVE LineItemTree AS (
  SELECT LineItemId, BudgetId, LineItemCode, LineItemName, LineItemLevel, 
         ParentLineItemId, EstimatedAmount, TotalAmount, 0 AS Depth
  FROM LineItems
  WHERE BudgetId = @BudgetId AND ParentLineItemId IS NULL
  
  UNION ALL
  
  SELECT li.LineItemId, li.BudgetId, li.LineItemCode, li.LineItemName, li.LineItemLevel,
         li.ParentLineItemId, li.EstimatedAmount, li.TotalAmount, Depth + 1
  FROM LineItems li
  INNER JOIN LineItemTree lit ON li.ParentLineItemId = lit.LineItemId
)
SELECT * FROM LineItemTree ORDER BY LineItemLevel, LineItemCode;
```

### Compare Takeoff vs. Proposal for Trade
```sql
SELECT
  li.LineItemCode,
  li.LineItemName,
  SUM(ti.ExtensionAmount) AS TakeoffTotal,
  p.ProposalAmount,
  (p.ProposalAmount - SUM(ti.ExtensionAmount)) AS Variance,
  CAST(ROUND(((p.ProposalAmount - SUM(ti.ExtensionAmount)) / SUM(ti.ExtensionAmount) * 100), 2) AS DECIMAL) AS VariancePercent
FROM LineItems li
LEFT JOIN TakeoffItems ti ON li.LineItemId = ti.LineItemId
LEFT JOIN Proposals p ON p.BudgetId = ti.BudgetId 
  AND p.TradeScope LIKE '%' + SUBSTRING(li.LineItemName, 1, 20) + '%'
WHERE li.BudgetId = @BudgetId AND li.LineItemLevel = 3
GROUP BY li.LineItemCode, li.LineItemName, p.ProposalAmount;
```

### Get Audit Trail for Budget
```sql
SELECT UserId, ActionType, TableName, FieldName, OldValue, NewValue, ChangeDate, IPAddress
FROM AuditLog
WHERE BudgetId = @BudgetId
ORDER BY ChangeDate DESC;
```

### Calculate CostPerUnit & CostPerGSF (for BudgetSummary trigger)
```sql
UPDATE BudgetSummary
SET 
  CostPerUnit = bs.TotalProjectCost / pd.TotalUnits,
  CostPerGSF = bs.TotalProjectCost / pd.BuildingGSF,
  ContingencyPercent = CAST(ROUND((bs.TotalContingency / bs.TotalHardCost * 100), 2) AS DECIMAL),
  LastCalculatedDate = GETDATE()
FROM BudgetSummary bs
INNER JOIN Budgets b ON bs.BudgetId = b.BudgetId
INNER JOIN PropertyDetails pd ON b.BudgetId = pd.BudgetId
WHERE bs.BudgetId = @BudgetId;
```

### Check User Permissions (Before Any Write)
```sql
SELECT CanEdit, CanDelete, CanApprove
FROM BudgetAccessControl
WHERE BudgetId = @BudgetId AND UserId = @UserId;
```

### Get Historical Average Cost (for Estimation)
```sql
SELECT
  ProductType,
  COUNT(*) AS ProjectCount,
  AVG(CostPerUnit) AS AvgCostPerUnit,
  AVG(CostPerGSF) AS AvgCostPerGSF,
  MIN(CostPerUnit) AS MinCostPerUnit,
  MAX(CostPerUnit) AS MaxCostPerUnit
FROM HistoricalProjects
WHERE ProductType = @ProductType
  AND CompletionYear >= YEAR(GETDATE()) - 3
GROUP BY ProductType;
```

### Find Outlier Line Items (>10% from Budget)
```sql
SELECT
  li.LineItemCode,
  li.LineItemName,
  SUM(ti.ExtensionAmount) AS TakeoffTotal,
  (SELECT SUM(ExtensionAmount) FROM TakeoffItems WHERE LineItemId = li.LineItemId) 
    * 0.10 AS TenPercentBand
FROM LineItems li
INNER JOIN TakeoffItems ti ON li.LineItemId = ti.LineItemId
WHERE li.BudgetId = @BudgetId
  AND ABS(SUM(ti.ExtensionAmount) - (SELECT AVG(ExtensionAmount) FROM TakeoffItems ti2 
    WHERE ti2.LineItemId = li.LineItemId)) > (SELECT AVG(ExtensionAmount) FROM TakeoffItems ti3 
    WHERE ti3.LineItemId = li.LineItemId) * 0.10
GROUP BY li.LineItemCode, li.LineItemName, li.LineItemId;
```

---

## Views

### vw_BudgetOverview
Fast lookup for dashboard: project name, budget level, total cost, cost per unit, approval status.

```sql
SELECT ProjectId, ProjectName, ProductType, BudgetId, BudgetLevel, TotalProjectCost, 
       CostPerUnit, CostPerGSF, ContingencyPercent, TotalUnits, BuildingGSF, 
       IsSubmitted, ApprovedBy, ApprovedDate
FROM vw_BudgetOverview
WHERE ProjectId = @ProjectId;
```

### vw_LineItemDetail
Line item with rollup counts and takeoff totals.

```sql
SELECT LineItemId, BudgetId, LineItemCode, LineItemName, TotalAmount, 
       TakeoffCount, ProposalCount, TakeoffTotal
FROM vw_LineItemDetail
WHERE BudgetId = @BudgetId;
```

### vw_BudgetLevelComparison
Level 0 vs. 1 vs. 2 vs. 3 comparison.

```sql
SELECT ProjectId, ProjectName, Level1_Total, Level2_Total, Level3_Total,
       Level1_PerUnit, Level2_PerUnit, Level3_PerUnit
FROM vw_BudgetLevelComparison
WHERE ProjectId = @ProjectId;
```

---

## Indexes (For Performance)

```sql
CREATE INDEX idx_Budgets_ProjectId ON Budgets(ProjectId);
CREATE INDEX idx_Budgets_Level ON Budgets(BudgetLevel);
CREATE INDEX idx_LineItems_BudgetId ON LineItems(BudgetId);
CREATE INDEX idx_LineItems_ParentId ON LineItems(ParentLineItemId);
CREATE INDEX idx_TakeoffItems_BudgetId ON TakeoffItems(BudgetId);
CREATE INDEX idx_TakeoffItems_LineItemId ON TakeoffItems(LineItemId);
CREATE INDEX idx_Proposals_BudgetId ON Proposals(BudgetId);
CREATE INDEX idx_AuditLog_BudgetId ON AuditLog(BudgetId);
CREATE INDEX idx_AuditLog_ChangeDate ON AuditLog(ChangeDate);
CREATE INDEX idx_BudgetAccessControl_UserId ON BudgetAccessControl(UserId);
CREATE INDEX idx_PropertyDetails_BudgetId ON PropertyDetails(BudgetId);
CREATE INDEX idx_UnitMix_PropertyDetailId ON UnitMix(PropertyDetailId);
CREATE INDEX idx_Scenarios_ProjectId ON Scenarios(ProjectId);
```

---

## Stored Procedures (To Build)

### sp_CreateBudgetFromTemplate
Copy a budget from one level to the next; auto-creates PropertyDetails, LineItems, TakeoffItems.

```sql
EXEC sp_CreateBudgetFromTemplate 
  @SourceBudgetId = 'X', 
  @TargetLevel = 2, 
  @TargetVersion = 1;
```

### sp_RecalculateBudgetSummary
Recalculate totals after any LineItem/TakeoffItem change.

```sql
EXEC sp_RecalculateBudgetSummary @BudgetId = 'X';
```

### sp_LogChange
Auto-called trigger; logs all changes to AuditLog.

```sql
EXEC sp_LogChange 
  @BudgetId = 'X',
  @UserId = 'jsmith',
  @TableName = 'LineItems',
  @ActionType = 'Update',
  @FieldName = 'EstimatedAmount',
  @OldValue = '500000',
  @NewValue = '485000';
```

### sp_CheckAccess
Verify user role before any write.

```sql
EXEC sp_CheckAccess 
  @BudgetId = 'X', 
  @UserId = 'jsmith', 
  @RequiredRole = 'Editor';
  -- Returns 1 (allowed) or 0 (denied)
```

---

## Constraints & Rules

### Not-Null Fields (Business Rules)
- `Projects`: ProjectName, ProductType
- `Budgets`: ProjectId, BudgetLevel, BudgetVersion, CreatedDate
- `PropertyDetails`: BudgetId, BuildingGSF, TotalUnits
- `LineItems`: BudgetId, LineItemCode, LineItemName, LineItemLevel
- `TakeoffItems`: LineItemId, BudgetId, Quantity, UnitOfMeasure, UnitCost

### Unique Constraints
- `Budgets(ProjectId, BudgetLevel, BudgetVersion)` — Only one "Level 2 Version 1" per project
- `PropertyDetails(BudgetId)` — One property record per budget
- `BudgetAccessControl(BudgetId, UserId)` — One role per user per budget
- `Scenarios(ProjectId, ScenarioName)` — No duplicate scenario names per project

### Check Constraints
- `Budgets.BudgetLevel IN (0, 1, 2, 3)`
- `LineItems.LineItemLevel IN (1, 2, 3)`
- `LineItems.Contingency >= 0`
- `TakeoffItems.Quantity > 0`
- `BudgetAccessControl.Role IN ('Viewer', 'Editor', 'Approver', 'Admin')`

---

## Data Types & Sizing

| Field | Type | Size | Notes |
|-------|------|------|-------|
| `ProjectId`, `BudgetId`, etc. | NVARCHAR(36) | GUID | Universally unique, sortable |
| `ProjectName`, `LineItemName` | NVARCHAR(255) | — | Sufficient for CSI + project names |
| `EstimatedAmount`, `ProposalAmount` | DECIMAL(14,2) | — | Supports up to $99,999,999.99 |
| `Quantity` | DECIMAL(12,3) | — | Supports 999,999,999.999 units |
| `UnitCost` | DECIMAL(12,2) | — | Supports up to $9,999,999.99 per unit |
| `CreatedAt`, `ChangeDate` | DATETIME2 | — | Millisecond precision |
| `IsActive`, `IsSubmitted`, `CanEdit` | BIT | — | 0 or 1 |

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Violates UNIQUE constraint on Budgets" | Duplicate level/version | Check if budget already exists for this project+level+version |
| "Foreign key constraint fails" | Deleting a budget with children | Must delete LineItems first, or use CASCADE (not recommended) |
| "PropertyDetails not found" | Budget created without property | INSERT PropertyDetails after budget creation |
| "User not in BudgetAccessControl" | Access denied | Add user to BudgetAccessControl with appropriate role |
| "AuditLog not updated" | Trigger failed | Check trigger syntax; ensure all mandatory fields provided |
| "CostPerUnit is NULL" | BudgetSummary not recalculated | Run sp_RecalculateBudgetSummary; check PropertyDetails.TotalUnits is not NULL |

---

## Setup Checklist

- [ ] Deploy schema to Azure SQL (`Ovation_Estimation_Assistant_Schema.sql`)
- [ ] Create all indexes
- [ ] Create all views
- [ ] Create stored procedures (sp_CreateBudgetFromTemplate, sp_RecalculateBudgetSummary, etc.)
- [ ] Load historical project data from past Ovation projects
- [ ] Test role-based access control with sample users
- [ ] Verify audit logging with test change
- [ ] Load sample budget from `App_Sample_Budget.xlsx` to validate schema
- [ ] Brief development team on schema design & common queries
- [ ] Document any customizations or deviations from this baseline schema

---

**Last Updated:** June 17, 2026  
**Schema Version:** 1.0  
**Contact:** Development Team Lead

