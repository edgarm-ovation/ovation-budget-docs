-- ═════════════════════════════════════════════════════════════════════════════
-- OVATION ESTIMATION ASSISTANT — AZURE SQL DATABASE SCHEMA
-- ═════════════════════════════════════════════════════════════════════════════
-- Purpose: Foundation schema for storing, accessing, and updating project
--          budgets from Level 0 (Conceptual) through Level 3 (Construction Docs)
-- Date: 2026-06-17
-- Environment: Azure SQL Database
-- ═════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. CORE ENTITY TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Core reference table for all projects
CREATE TABLE Projects (
  ProjectId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  ProjectName NVARCHAR(255) NOT NULL,
  ProductType NVARCHAR(50) NOT NULL, -- 'Senior', 'Workforce', 'Market Rate', 'Tax Credit'
  Location NVARCHAR(255),
  StartDate DATE,
  EstimatedCompletionDate DATE,
  TimelineMonths INT, -- Construction timeline in months
  CreatedAt DATETIME2 DEFAULT GETDATE(),
  UpdatedAt DATETIME2 DEFAULT GETDATE(),
  IsActive BIT DEFAULT 1,
  Notes NVARCHAR(MAX),
  CONSTRAINT chk_ProductType CHECK (ProductType IN ('Senior', 'Workforce', 'Market Rate', 'Tax Credit'))
);

-- Master budget versions tied to budget levels (0, 1, 2, 3)
CREATE TABLE Budgets (
  BudgetId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  ProjectId NVARCHAR(36) NOT NULL,
  BudgetLevel INT NOT NULL, -- 0 (Conceptual), 1 (Schematic), 2 (Design Dev), 3 (Construction Docs)
  BudgetVersion INT NOT NULL, -- Version number within a level (1.0, 1.1, 2.0, etc.)
  CreatedDate DATETIME2 DEFAULT GETDATE(),
  LastModifiedDate DATETIME2 DEFAULT GETDATE(),
  SubmittedDate DATETIME2,
  IsSubmitted BIT DEFAULT 0,
  ApprovedBy NVARCHAR(100),
  ApprovedDate DATETIME2,
  Notes NVARCHAR(MAX),
  FOREIGN KEY (ProjectId) REFERENCES Projects(ProjectId),
  CONSTRAINT chk_BudgetLevel CHECK (BudgetLevel IN (0, 1, 2, 3)),
  CONSTRAINT chk_BudgetVersion CHECK (BudgetVersion >= 1),
  UNIQUE(ProjectId, BudgetLevel, BudgetVersion)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. PROJECT PARAMETERS & ASSUMPTIONS
-- ─────────────────────────────────────────────────────────────────────────────

-- Property-level characteristics
CREATE TABLE PropertyDetails (
  PropertyDetailId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36) NOT NULL,
  BuildingGSF DECIMAL(12,2), -- Gross Square Footage
  AcreageSize DECIMAL(8,3),
  SiteSF DECIMAL(12,2), -- Site Square Footage
  NumberOfBuildings INT,
  NumberOfFloors INT,
  TotalUnits INT,
  ParkingProvidedCount INT,
  ReportsAvailable NVARCHAR(MAX), -- JSON: {geotechnical, environmental, alta_survey, etc}
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId),
  UNIQUE(BudgetId)
);

-- Unit mix breakdown
CREATE TABLE UnitMix (
  UnitMixId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  PropertyDetailId NVARCHAR(36) NOT NULL,
  UnitType NVARCHAR(50), -- e.g., 'Studio', '1BR-1BA', '1BR-1BA', '2BR-2BA', '3BR-2BA'
  NumberOfUnits INT,
  AvgUnitSF DECIMAL(8,2),
  FOREIGN KEY (PropertyDetailId) REFERENCES PropertyDetails(PropertyDetailId)
);

-- Parking breakdown
CREATE TABLE ParkingBreakdown (
  ParkingId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  PropertyDetailId NVARCHAR(36) NOT NULL,
  ParkingType NVARCHAR(50), -- 'Covered', 'Open', 'Accessible', 'Private Garage', 'Carport'
  Count INT,
  FOREIGN KEY (PropertyDetailId) REFERENCES PropertyDetails(PropertyDetailId)
);

-- Budget-level assumptions & parameters
CREATE TABLE BudgetAssumptions (
  AssumptionId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36) NOT NULL,
  AssumptionCategory NVARCHAR(100), -- 'Schedule', 'Pricing', 'Market', 'Scope', 'Contingency', etc.
  AssumptionName NVARCHAR(255),
  Value NVARCHAR(MAX),
  UnitOfMeasure NVARCHAR(50),
  IsEditable BIT DEFAULT 1,
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. COST BREAKDOWN STRUCTURE (Hierarchical)
-- ─────────────────────────────────────────────────────────────────────────────

-- CSI divisions and line items (the budget P&L structure)
CREATE TABLE LineItems (
  LineItemId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36) NOT NULL,
  LineItemCode NVARCHAR(50), -- CSI code (e.g., '03 00 00', '05 01 00')
  LineItemName NVARCHAR(255) NOT NULL,
  LineItemLevel INT, -- Hierarchy: 1 (Division), 2 (Section), 3 (Item)
  ParentLineItemId NVARCHAR(36), -- NULL for divisions, FK to parent for sections/items
  SequenceOrder INT,
  Description NVARCHAR(MAX),
  EstimatedAmount DECIMAL(14,2),
  Contingency DECIMAL(14,2),
  TotalAmount DECIMAL(14,2), -- EstimatedAmount + Contingency
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId),
  FOREIGN KEY (ParentLineItemId) REFERENCES LineItems(LineItemId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. TAKEOFF & QUANTITY DATA (Level 3 specific)
-- ─────────────────────────────────────────────────────────────────────────────

-- Individual take-off line items with quantities & unit pricing
CREATE TABLE TakeoffItems (
  TakeoffId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  LineItemId NVARCHAR(36) NOT NULL,
  BudgetId NVARCHAR(36) NOT NULL,
  TakeoffDescription NVARCHAR(255),
  Quantity DECIMAL(12,3),
  UnitOfMeasure NVARCHAR(20), -- 'SF', 'LF', 'EA', 'Count', 'LS', 'SQ', etc.
  UnitCost DECIMAL(12,2),
  ExtensionAmount DECIMAL(14,2), -- Qty × UnitCost
  Source NVARCHAR(100), -- 'Proposal', 'Historical', 'Estimate', 'Comparable'
  ProposalRef NVARCHAR(100), -- Subcontractor proposal ID/reference
  IsProposalBased BIT, -- 1 if from actual proposal, 0 if estimate
  Notes NVARCHAR(MAX),
  FOREIGN KEY (LineItemId) REFERENCES LineItems(LineItemId),
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. PROPOSAL & VENDOR MANAGEMENT
-- ─────────────────────────────────────────────────────────────────────────────

-- Vendor/Subcontractor proposals
CREATE TABLE Proposals (
  ProposalId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36) NOT NULL,
  VendorId NVARCHAR(36),
  VendorName NVARCHAR(255),
  TradeScope NVARCHAR(100), -- 'Framing', 'HVAC', 'Electrical', 'Drywall', etc.
  ProposalAmount DECIMAL(14,2),
  ProposalDate DATE,
  ExpirationDate DATE,
  Status NVARCHAR(50), -- 'Pending', 'Accepted', 'Rejected', 'Negotiating'
  Notes NVARCHAR(MAX),
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. COST METRICS & REPORTING
-- ─────────────────────────────────────────────────────────────────────────────

-- Summary metrics per budget (used in reports & dashboards)
CREATE TABLE BudgetSummary (
  SummaryId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36) NOT NULL,
  TotalHardCost DECIMAL(14,2),
  TotalSoftCost DECIMAL(14,2),
  TotalContingency DECIMAL(14,2),
  TotalProjectCost DECIMAL(14,2),
  CostPerUnit DECIMAL(12,2), -- TotalProjectCost / TotalUnits
  CostPerGSF DECIMAL(12,2), -- TotalProjectCost / BuildingGSF
  ContingencyPercent DECIMAL(5,2),
  LastCalculatedDate DATETIME2,
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId),
  UNIQUE(BudgetId)
);

-- Cost comparisons across budget levels and scenarios
CREATE TABLE BudgetComparisons (
  ComparisonId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  ProjectId NVARCHAR(36) NOT NULL,
  Level1BudgetId NVARCHAR(36),
  Level2BudgetId NVARCHAR(36),
  Level3BudgetId NVARCHAR(36),
  Level1Cost DECIMAL(14,2),
  Level2Cost DECIMAL(14,2),
  Level3Cost DECIMAL(14,2),
  Level1To2Change DECIMAL(14,2),
  Level2To3Change DECIMAL(14,2),
  Level1To2ChangePercent DECIMAL(5,2),
  Level2To3ChangePercent DECIMAL(5,2),
  ComparisonNotes NVARCHAR(MAX),
  FOREIGN KEY (ProjectId) REFERENCES Projects(ProjectId),
  FOREIGN KEY (Level1BudgetId) REFERENCES Budgets(BudgetId),
  FOREIGN KEY (Level2BudgetId) REFERENCES Budgets(BudgetId),
  FOREIGN KEY (Level3BudgetId) REFERENCES Budgets(BudgetId)
);

-- Per-unit and per-GSF cost metrics for historical comparison
CREATE TABLE UnitCostBenchmarks (
  BenchmarkId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36) NOT NULL,
  LineItemCode NVARCHAR(50),
  LineItemName NVARCHAR(255),
  TotalCost DECIMAL(14,2),
  CostPerUnit DECIMAL(12,2),
  CostPerGSF DECIMAL(12,2),
  UOM NVARCHAR(50), -- e.g., 'Per Unit', 'Per SF', 'Per LF'
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. SCENARIOS & VERSIONS
-- ─────────────────────────────────────────────────────────────────────────────

-- Multiple budget scenarios (Phase 1 vs Phase 2, different unit mixes, etc.)
CREATE TABLE Scenarios (
  ScenarioId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  ProjectId NVARCHAR(36) NOT NULL,
  ScenarioName NVARCHAR(255), -- e.g., 'Scenario 1 - Phase 1', 'Scenario 2 - Phase 2'
  ScenarioDescription NVARCHAR(MAX),
  IsActive BIT DEFAULT 1,
  CreatedDate DATETIME2 DEFAULT GETDATE(),
  FOREIGN KEY (ProjectId) REFERENCES Projects(ProjectId),
  UNIQUE(ProjectId, ScenarioName)
);

-- Link budgets to scenarios
CREATE TABLE ScenarioBudgets (
  ScenarioBudgetId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  ScenarioId NVARCHAR(36) NOT NULL,
  BudgetId NVARCHAR(36) NOT NULL,
  FOREIGN KEY (ScenarioId) REFERENCES Scenarios(ScenarioId),
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId),
  UNIQUE(ScenarioId, BudgetId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 8. AUDIT & ACCESS CONTROL
-- ─────────────────────────────────────────────────────────────────────────────

-- Budget access control by role
CREATE TABLE BudgetAccessControl (
  AccessId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36) NOT NULL,
  UserId NVARCHAR(100),
  Role NVARCHAR(50), -- 'Viewer', 'Editor', 'Approver', 'Admin'
  CanEdit BIT DEFAULT 0,
  CanDelete BIT DEFAULT 0,
  CanApprove BIT DEFAULT 0,
  GrantedDate DATETIME2 DEFAULT GETDATE(),
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId),
  CONSTRAINT chk_Role CHECK (Role IN ('Viewer', 'Editor', 'Approver', 'Admin')),
  UNIQUE(BudgetId, UserId)
);

-- Audit log for all budget changes
CREATE TABLE AuditLog (
  AuditLogId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  BudgetId NVARCHAR(36),
  LineItemId NVARCHAR(36),
  TakeoffId NVARCHAR(36),
  UserId NVARCHAR(100),
  ActionType NVARCHAR(50), -- 'Create', 'Update', 'Delete', 'Submit', 'Approve'
  TableName NVARCHAR(100),
  FieldName NVARCHAR(100),
  OldValue NVARCHAR(MAX),
  NewValue NVARCHAR(MAX),
  ChangeDate DATETIME2 DEFAULT GETDATE(),
  IPAddress NVARCHAR(50),
  Notes NVARCHAR(MAX),
  FOREIGN KEY (BudgetId) REFERENCES Budgets(BudgetId),
  FOREIGN KEY (LineItemId) REFERENCES LineItems(LineItemId),
  FOREIGN KEY (TakeoffId) REFERENCES TakeoffItems(TakeoffId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 9. HISTORICAL & COMPARABLE DATA
-- ─────────────────────────────────────────────────────────────────────────────

-- Historical project data for estimation support
CREATE TABLE HistoricalProjects (
  HistoricalProjectId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  ProjectName NVARCHAR(255),
  ProductType NVARCHAR(50),
  CompletionYear INT,
  Location NVARCHAR(255),
  TotalUnits INT,
  BuildingGSF DECIMAL(12,2),
  TotalCost DECIMAL(14,2),
  CostPerUnit DECIMAL(12,2),
  CostPerGSF DECIMAL(12,2),
  ConstructionTimeline INT,
  Notes NVARCHAR(MAX)
);

-- Historical cost line items by CSI code
CREATE TABLE HistoricalCosts (
  HistoricalCostId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  LineItemCode NVARCHAR(50),
  LineItemName NVARCHAR(255),
  HistoricalProjectId NVARCHAR(36),
  Amount DECIMAL(14,2),
  UnitOfMeasure NVARCHAR(20),
  UnitCost DECIMAL(12,2),
  ProjectYear INT,
  FOREIGN KEY (HistoricalProjectId) REFERENCES HistoricalProjects(HistoricalProjectId)
);

-- Comparable project data for benchmarking
CREATE TABLE ComparableProjects (
  ComparableId NVARCHAR(36) PRIMARY KEY DEFAULT NEWID(),
  ProjectId NVARCHAR(36),
  ComparableProjectName NVARCHAR(255),
  Relationship NVARCHAR(100), -- 'Senior', 'Workforce', 'Market Rate', 'Affordable'
  Location NVARCHAR(255),
  TotalUnits INT,
  BuildingGSF DECIMAL(12,2),
  TotalCost DECIMAL(14,2),
  CostPerUnit DECIMAL(12,2),
  CostPerGSF DECIMAL(12,2),
  ConstructionYear INT,
  Notes NVARCHAR(MAX),
  FOREIGN KEY (ProjectId) REFERENCES Projects(ProjectId)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10. INDEXES FOR PERFORMANCE
-- ─────────────────────────────────────────────────────────────────────────────

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

-- ─────────────────────────────────────────────────────────────────────────────
-- 11. VIEWS FOR REPORTING
-- ─────────────────────────────────────────────────────────────────────────────

-- Comprehensive budget overview
CREATE VIEW vw_BudgetOverview AS
SELECT
  p.ProjectId,
  p.ProjectName,
  p.ProductType,
  b.BudgetId,
  b.BudgetLevel,
  b.BudgetVersion,
  bs.TotalProjectCost,
  bs.CostPerUnit,
  bs.CostPerGSF,
  bs.ContingencyPercent,
  pd.TotalUnits,
  pd.BuildingGSF,
  b.IsSubmitted,
  b.ApprovedBy,
  b.ApprovedDate
FROM Projects p
INNER JOIN Budgets b ON p.ProjectId = b.ProjectId
LEFT JOIN BudgetSummary bs ON b.BudgetId = bs.BudgetId
LEFT JOIN PropertyDetails pd ON b.BudgetId = pd.BudgetId;

-- Line item detail with roll-up
CREATE VIEW vw_LineItemDetail AS
SELECT
  li.LineItemId,
  li.BudgetId,
  li.LineItemCode,
  li.LineItemName,
  li.LineItemLevel,
  li.EstimatedAmount,
  li.Contingency,
  li.TotalAmount,
  COUNT(DISTINCT t.TakeoffId) as TakeoffCount,
  SUM(CASE WHEN t.IsProposalBased = 1 THEN 1 ELSE 0 END) as ProposalCount,
  SUM(t.ExtensionAmount) as TakeoffTotal
FROM LineItems li
LEFT JOIN TakeoffItems t ON li.LineItemId = t.LineItemId
GROUP BY li.LineItemId, li.BudgetId, li.LineItemCode, li.LineItemName,
         li.LineItemLevel, li.EstimatedAmount, li.Contingency, li.TotalAmount;

-- Budget level comparison across project
CREATE VIEW vw_BudgetLevelComparison AS
SELECT
  p.ProjectId,
  p.ProjectName,
  MAX(CASE WHEN b.BudgetLevel = 1 THEN bs.TotalProjectCost END) as Level1_Total,
  MAX(CASE WHEN b.BudgetLevel = 2 THEN bs.TotalProjectCost END) as Level2_Total,
  MAX(CASE WHEN b.BudgetLevel = 3 THEN bs.TotalProjectCost END) as Level3_Total,
  MAX(CASE WHEN b.BudgetLevel = 1 THEN bs.CostPerUnit END) as Level1_PerUnit,
  MAX(CASE WHEN b.BudgetLevel = 2 THEN bs.CostPerUnit END) as Level2_PerUnit,
  MAX(CASE WHEN b.BudgetLevel = 3 THEN bs.CostPerUnit END) as Level3_PerUnit
FROM Projects p
INNER JOIN Budgets b ON p.ProjectId = b.ProjectId
LEFT JOIN BudgetSummary bs ON b.BudgetId = bs.BudgetId
GROUP BY p.ProjectId, p.ProjectName;

-- ═════════════════════════════════════════════════════════════════════════════
-- END SCHEMA
-- ═════════════════════════════════════════════════════════════════════════════
