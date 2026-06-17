-- ============================================================================
-- Ovation Budget Platform — DDL for the tables covered by this seed package
-- Faithful subset of docs/database/schema.md (Schema A, canonical).
-- Azure SQL / EF Core 8. PascalCase. GUID PKs for entities, INT IDENTITY for
-- seeded master data (Divisions, LineItems).
--
-- This file is ONLY the tables the seed data populates. The full schema (bid
-- leveling, approvals, audit, notifications, etc.) lives in schema.md.
-- ============================================================================

-- Minimal seed user is required because Projects/Markups have NOT NULL user FKs.
CREATE TABLE Users (
  Id          UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  AzureOid    NVARCHAR(100)     NOT NULL UNIQUE,
  Email       NVARCHAR(256)     NOT NULL UNIQUE,
  Name        NVARCHAR(200)     NOT NULL,
  Department  NVARCHAR(50)      NULL,
  IsActive    BIT               NOT NULL DEFAULT 1,
  CreatedAt   DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  LastLoginAt DATETIME2         NULL
);

CREATE TABLE Projects (
  Id                UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  Name              NVARCHAR(200)     NOT NULL,
  Address           NVARCHAR(500)     NULL,
  City              NVARCHAR(100)     NULL,
  State             NCHAR(2)          NULL,
  Zip               NVARCHAR(10)      NULL,
  ProductType       NVARCHAR(50)      NOT NULL,   -- Affordable|Senior|Workforce|MarketRate
  Status            NVARCHAR(50)      NOT NULL DEFAULT 'Active',  -- Active|OnHold|Closed
  TotalUnits        INT               NULL,
  GrossSF           DECIMAL(12,2)     NULL,
  LivableSF         DECIMAL(12,2)     NULL,
  SiteSF            DECIMAL(12,2)     NULL,
  SiteAcres         DECIMAL(8,4)      NULL,
  Floors            SMALLINT          NULL,
  FloorsLabel       NVARCHAR(50)      NULL,   -- ADDED: Excel stores "2 & 3 Levels" (free text)
  Buildings         SMALLINT          NULL,
  EfficiencyPct     DECIMAL(5,4)      NULL,
  StartDate         DATE              NULL,
  TimelineMonths    SMALLINT          NULL,
  PreparedBy        NVARCHAR(200)     NULL,
  Version           NVARCHAR(20)      NULL,
  CreatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  CreatedByUserId   UNIQUEIDENTIFIER  NOT NULL REFERENCES Users(Id)
);

CREATE TABLE UnitMix (
  Id          UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId   UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id) ON DELETE CASCADE,
  UnitType    NVARCHAR(50)      NOT NULL,
  Count       INT               NOT NULL,
  Pct         DECIMAL(5,4)      NULL,
  SortOrder   SMALLINT          NOT NULL DEFAULT 0
);

CREATE TABLE Parking (
  Id                  UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId           UNIQUEIDENTIFIER  NOT NULL UNIQUE REFERENCES Projects(Id) ON DELETE CASCADE,
  Covered             INT               NOT NULL DEFAULT 0,
  CoveredAccessible   INT               NOT NULL DEFAULT 0,
  Open                INT               NOT NULL DEFAULT 0,
  OpenAccessible      INT               NOT NULL DEFAULT 0,
  Waiver              INT               NOT NULL DEFAULT 0,
  Ratio               DECIMAL(5,3)      NULL
);

CREATE TABLE BudgetLevels (
  Id                    UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId             UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id),
  Level                 INT               NOT NULL,            -- 0|1|2|3
  SubLevel              INT               NOT NULL DEFAULT 1,
  DisplayName           NVARCHAR(100)     NULL,
  ParentBudgetLevelId   UNIQUEIDENTIFIER  NULL REFERENCES BudgetLevels(Id),
  Status                NVARCHAR(50)      NOT NULL DEFAULT 'Draft',
  SubmittedAt           DATETIME2         NULL,
  SubmittedByUserId     UNIQUEIDENTIFIER  NULL REFERENCES Users(Id),
  ApprovedAt            DATETIME2         NULL,
  ApprovedByUserId      UNIQUEIDENTIFIER  NULL REFERENCES Users(Id),
  RejectionComment      NVARCHAR(1000)    NULL,
  CreatedAt             DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedAt             DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  CONSTRAINT UQ_ProjectLevelSubLevel UNIQUE (ProjectId, Level, SubLevel)
);

CREATE TABLE Divisions (
  Id        INT           PRIMARY KEY IDENTITY,
  CsiCode   NVARCHAR(10)  NOT NULL UNIQUE,
  Name      NVARCHAR(100) NOT NULL,
  IsMarkup  BIT           NOT NULL DEFAULT 0,    -- TRUE for 50,51,55,98,99,BR
  IsFfe     BIT           NOT NULL DEFAULT 0,
  SortOrder INT           NOT NULL
);

CREATE TABLE BudgetLevelLineItems (
  Id                UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId     UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  LineItemId        INT               NULL,   -- NULL: data carried inline (see README)
  IsCustom          BIT               NOT NULL DEFAULT 0,
  CustomLabel       NVARCHAR(200)     NULL,
  CustomDivisionId  INT               NULL REFERENCES Divisions(Id),
  CostCode          NVARCHAR(20)      NULL,
  Category          NVARCHAR(5)       NULL,   -- S|A|RR|B|F|R
  SubJob            NVARCHAR(30)      NULL,
  Source            NVARCHAR(100)     NULL,
  UnitOfMeasure     NVARCHAR(100)     NULL,
  TakeoffQuantity   DECIMAL(18,4)     NULL,
  TakeoffUnitPrice  DECIMAL(18,4)     NULL,
  EscalationPct     DECIMAL(6,4)      NOT NULL DEFAULT 0,
  TakeoffAmount     DECIMAL(18,2)     NULL,   -- stored line total (= line_total in seed)
  BaselineAmount    DECIMAL(18,2)     NULL,
  ProposalAmount    DECIMAL(18,2)     NULL,
  PreferredSource   NVARCHAR(20)      NULL DEFAULT 'takeoff',
  GroupKey          NVARCHAR(100)     NULL,   -- bid-leveling join glue (see README §missing)
  SelectedProposalId UNIQUEIDENTIFIER NULL,
  CommittedAdjustmentAmount  DECIMAL(18,2)  NULL,
  ProposedAdjustmentAmount   DECIMAL(18,2)  NULL,
  ChangeNote         NVARCHAR(1000)   NULL,
  Assumption        NVARCHAR(500)     NULL,
  Notes             NVARCHAR(1000)    NULL,
  Section           NVARCHAR(30)      NULL,
  IsLocked          BIT               NOT NULL DEFAULT 0,
  CreatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE()
);

CREATE TABLE Markups (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId   UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  Kind            NVARCHAR(30)      NOT NULL,
  -- general_requirements|bid_risk|contingency|bonds|insurance|overhead|fee
  Label           NVARCHAR(100)     NOT NULL,
  CostCode        NVARCHAR(10)      NOT NULL,   -- 01|BR|55|50|51|99|98
  Mode            NVARCHAR(10)      NOT NULL,   -- pct|fixed
  Rate            DECIMAL(8,6)      NULL,
  FixedAmount     DECIMAL(18,2)     NULL,
  SortOrder       SMALLINT          NOT NULL DEFAULT 0,
  IsActive        BIT               NOT NULL DEFAULT 1,
  UpdatedAt       DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedByUserId UNIQUEIDENTIFIER  NOT NULL REFERENCES Users(Id),
  CONSTRAINT UQ_Markups_LevelKind UNIQUE (BudgetLevelId, Kind)
);

-- ============================================================================
-- EXPANSION TABLES (added 2026-06-17 with the full-workbook extraction)
-- Populated by extract_full.py. Create AFTER Projects/Divisions/BudgetLevels
-- exist (they carry the FKs these tables resolve against).
-- A couple of columns (SiteAcres, SourceSheet, CsiLabel) are seed-provenance
-- additions beyond schema.md — kept so no extracted data is dropped at load.
-- ============================================================================

CREATE TABLE ComparableProjects (
  Id            UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  Name          NVARCHAR(200)     NOT NULL UNIQUE,
  -- 'West Henderson'|'Bruner'|'Torrey Pines'|'Decatur / Rome'|'Pebble'|'Russell IV'
  TotalUnits    INT               NULL,
  TotalGsf      DECIMAL(12,2)     NULL,
  SiteAcres     DECIMAL(8,4)      NULL,   -- seed addition (not in schema.md)
  ContractDate  DATE              NULL,
  City          NVARCHAR(100)     NULL,
  State         NCHAR(2)          NULL,
  ProductType   NVARCHAR(50)      NULL,
  SourceSheet   NVARCHAR(50)      NULL,   -- provenance: 'Normalize'|'Offsite Comp'
  IsActive      BIT               NOT NULL DEFAULT 1,
  CreatedAt     DATETIME2         NOT NULL DEFAULT GETUTCDATE()
);

CREATE TABLE ComparableProjectCosts (
  Id                    UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ComparableProjectId   UNIQUEIDENTIFIER  NOT NULL REFERENCES ComparableProjects(Id) ON DELETE CASCADE,
  DivisionId            INT               NOT NULL REFERENCES Divisions(Id),
  CsiLabel              NVARCHAR(200)     NULL,   -- division label as it appeared on the sheet
  TotalAmount           DECIMAL(18,2)     NULL,
  CostPerUnit           DECIMAL(18,2)     NULL,   -- computed later
  CostPerGrossSF        DECIMAL(18,4)     NULL,   -- computed later
  SourceSheet           NVARCHAR(50)      NULL,
  Notes                 NVARCHAR(500)     NULL,
  CONSTRAINT UQ_ComparableProjectCosts UNIQUE (ComparableProjectId, DivisionId)
);

CREATE TABLE ComparableTradeCosts (
  Id                    UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ComparableProjectId   UNIQUEIDENTIFIER  NOT NULL REFERENCES ComparableProjects(Id) ON DELETE CASCADE,
  Trade                 NVARCHAR(200)     NOT NULL,   -- 'Slabs'|'Framing'|'Water'|...
  Section               NVARCHAR(30)      NULL,        -- 'Building'|'Offsite'
  TotalAmount           DECIMAL(18,2)     NULL,
  CostPerUnit           DECIMAL(18,2)     NULL,
  SourceSheet           NVARCHAR(50)      NULL
);

CREATE TABLE TradeBenchmarks (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId       UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id) ON DELETE CASCADE,
  Trade           NVARCHAR(200)     NOT NULL,
  Uom             NVARCHAR(30)      NULL,
  Quantity        DECIMAL(18,4)     NULL,
  CurrentCost     DECIMAL(18,2)     NULL,   -- this project's budgeted cost for the trade
  CurrentPerUnit  DECIMAL(18,4)     NULL,
  ProposalLow     DECIMAL(18,4)     NULL,
  Proposal2nd     DECIMAL(18,4)     NULL,
  Proposal3rd     DECIMAL(18,4)     NULL,
  ProposalAvg     DECIMAL(18,4)     NULL
);

CREATE TABLE MenuPricingOptions (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId       UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id) ON DELETE CASCADE,
  Category        NVARCHAR(100)     NOT NULL,   -- 'Lightweight Flooring'|'Unit Cabinets'
  Product         NVARCHAR(200)     NOT NULL,
  Spec            NVARCHAR(200)     NULL,
  UnitPrice       DECIMAL(18,4)     NULL,        -- per SF or per box
  Budget          DECIMAL(18,2)     NULL,
  Delta           DECIMAL(18,2)     NULL,        -- cost above the base ("$0") tier
  CostPerUnit     DECIMAL(18,2)     NULL,
  SortOrder       SMALLINT          NOT NULL DEFAULT 0
);

CREATE TABLE InsuranceBondDetail (
  Id                          UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId               UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id) ON DELETE CASCADE,
  GlRatePer1000               DECIMAL(10,4)     NULL,   -- e.g. 3.7395
  GcContract                  DECIMAL(18,2)     NULL,   -- base = total hard costs
  AnnualInflationPct          DECIMAL(6,4)      NULL,   -- e.g. 0.10
  TotalGlInsurancePreInfl     DECIMAL(18,2)     NULL,
  TotalGlInsurancePostInfl    DECIMAL(18,2)     NULL,   -- = Markups.insurance FixedAmount
  PpBond                      DECIMAL(18,2)     NULL,   -- P&P bond (excluded from budget)
  SubBonds                    DECIMAL(18,2)     NULL,   -- = Markups.bonds
  Notes                       NVARCHAR(1000)    NULL
);

CREATE TABLE RiskItems (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId       UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id) ON DELETE CASCADE,
  Category        NVARCHAR(50)      NOT NULL,   -- 'Utilities'|'Unfavorable Bid'|'Favorable Bid'
  Item            NVARCHAR(200)     NOT NULL,
  Amount          DECIMAL(18,2)     NULL,        -- utility-risk rows
  Budget          DECIMAL(18,2)     NULL,        -- bid-risk rows
  Proposal        DECIMAL(18,2)     NULL,
  Deficit         DECIMAL(18,2)     NULL,        -- Budget − Proposal (neg = over budget)
  Subcontractor   NVARCHAR(200)     NULL,
  Note            NVARCHAR(500)     NULL,
  HasRefError     BIT               NOT NULL DEFAULT 0,   -- TRUE where source cell was #REF!
  SortOrder       SMALLINT          NOT NULL DEFAULT 0
);

CREATE TABLE ValueEngineeringItems (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId       UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id) ON DELETE CASCADE,
  VeNo            INT               NULL,
  Item            NVARCHAR(200)     NOT NULL,
  BudgetAmount    DECIMAL(18,2)     NULL,
  ReductionPct    DECIMAL(6,4)      NULL,
  UpdatedBudget   DECIMAL(18,2)     NULL,
  Savings         DECIMAL(18,2)     NULL,
  SortOrder       SMALLINT          NOT NULL DEFAULT 0
);

CREATE TABLE ParkingOptions (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId       UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id) ON DELETE CASCADE,
  OptionLabel     NVARCHAR(100)     NOT NULL,   -- 'Option 1'..'Option 4'
  TotalProposal   DECIMAL(18,2)     NULL,
  ScopeJson       NVARCHAR(MAX)     NULL,        -- JSON array of {description, amount}
  SortOrder       SMALLINT          NOT NULL DEFAULT 0
);
