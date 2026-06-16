# Database Schema

**Status:** `[COMPLETE]`
**Decision record:** [ADR-003](../architecture/decisions/ADR-003-cloud-and-database.md) | [ADR-004](../architecture/decisions/ADR-004-budget-level-data-model.md)
**Database:** Azure SQL (code-first via EF Core 8)

---

## Table Index

| Table | Description |
|---|---|
| [Projects](#projects) | Construction projects |
| [UnitMix](#unitmix) | Unit type breakdown per project |
| [Parking](#parking) | Parking counts per project |
| [BudgetLevels](#budgetlevels) | L0–L3 budget snapshots per project |
| [Divisions](#divisions) | CSI division master list (seeded) |
| [LineItems](#lineitems) | Line item master list per division (seeded) |
| [BudgetLevelLineItems](#budgetlevellineitems) | Actual budget data per line item per level |
| [Markups](#markups) | Per-budget-level markup rows (one row per kind) |
| [ComparableProjects](#comparableprojects) | Reference projects used as cost sources |
| [ComparableProjectCosts](#comparableprojectcosts) | Per-division cost data for each comparable project |
| [TradePackages](#tradepackages) | L3 subcontractor trade scopes |
| [Bidders](#bidders) | Subcontractor / vendor companies |
| [Proposals](#proposals) | Subcontractor bid proposals per trade |
| [ProposalLineItems](#proposallineitems) | Scope line items within a proposal |
| [Takeoffs](#takeoffs) | Site work quantity takeoffs (L2 vs L3 dual-track) |
| [Renderings](#renderings) | Project rendering images |
| [TakeoffConfigs](#takeoffconfigs) | Per-trade takeoff metadata (layout, L2/L3 flags) |
| [TakeoffPlans](#takeoffplans) | PDF plan files linked to takeoff trades |
| [TradeHistoricalBenchmarks](#tradehistoricalbenchmarks) | Per-trade historical cost benchmarks for leveling sheets |
| [BudgetApprovals](#budgetapprovals) | Signed approval records with SHA-256 fingerprint |
| [Users](#users) | Ovation team members |
| [Roles](#roles) | Permission roles |
| [UserRoles](#userroles) | User ↔ Role assignments |
| [ProjectUsers](#projectusers) | User ↔ Project access |
| [AuditLog](#auditlog) | Every field change, ever |
| [UploadedFiles](#uploadedfiles) | File upload metadata |
| [Notifications](#notifications) | In-app notification records |

---

## Projects

```sql
CREATE TABLE Projects (
  Id                UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  Name              NVARCHAR(200)     NOT NULL,
  Address           NVARCHAR(500)     NULL,
  City              NVARCHAR(100)     NULL,
  State             NCHAR(2)          NULL,
  Zip               NVARCHAR(10)      NULL,
  ProductType       NVARCHAR(50)      NOT NULL,
  -- 'Affordable' | 'Senior' | 'Workforce' | 'MarketRate'
  Status            NVARCHAR(50)      NOT NULL DEFAULT 'Active',
  -- 'Active' | 'OnHold' | 'Closed'

  -- Unit & building data
  TotalUnits        INT               NULL,
  GrossSF           DECIMAL(12,2)     NULL,   -- total GSF
  LivableSF         DECIMAL(12,2)     NULL,   -- livable/net SF
  SiteSF            DECIMAL(12,2)     NULL,
  SiteAcres         DECIMAL(8,4)      NULL,
  Floors            SMALLINT          NULL,
  Buildings         SMALLINT          NULL,
  EfficiencyPct     DECIMAL(5,4)      NULL,   -- e.g. 0.8742 = 87.42%

  -- Schedule
  StartDate         DATE              NULL,
  TimelineMonths    SMALLINT          NULL,

  -- Metadata
  PreparedBy        NVARCHAR(200)     NULL,
  Version           NVARCHAR(20)      NULL,   -- e.g. 'v94', '4.13.26'

  CreatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  CreatedByUserId   UNIQUEIDENTIFIER  NOT NULL REFERENCES Users(Id)
)
```

---

## UnitMix

Unit type breakdown per project.

```sql
CREATE TABLE UnitMix (
  Id          UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId   UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id) ON DELETE CASCADE,
  UnitType    NVARCHAR(50)      NOT NULL,
  -- 'Studio' | '1BR-1BA' | '2BR-1BA' | '2BR-2BA' | '3BR-2BA'
  Count       INT               NOT NULL,
  Pct         DECIMAL(5,4)      NULL,   -- computed: Count / Projects.TotalUnits
  SortOrder   SMALLINT          NOT NULL DEFAULT 0
)
```

---

## Parking

Parking configuration per project (one row per project).

```sql
CREATE TABLE Parking (
  Id                  UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId           UNIQUEIDENTIFIER  NOT NULL UNIQUE REFERENCES Projects(Id) ON DELETE CASCADE,
  Covered             INT               NOT NULL DEFAULT 0,
  CoveredAccessible   INT               NOT NULL DEFAULT 0,
  Open                INT               NOT NULL DEFAULT 0,
  OpenAccessible      INT               NOT NULL DEFAULT 0,
  Waiver              INT               NOT NULL DEFAULT 0,
  -- Total = Covered + CoveredAccessible + Open + OpenAccessible - Waiver (computed in app)
  Ratio               DECIMAL(5,3)      NULL    -- Total / Projects.TotalUnits
)
```

---

## BudgetLevels

One project can have multiple budget level documents. Each major level (0–3) can have multiple sub-level revisions (e.g., L2.1, L2.2, L2.3) before approval. A sub-level is always a copy of the previous one — editors work on the new sub-level and resubmit.

```sql
CREATE TABLE BudgetLevels (
  Id                    UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProjectId             UNIQUEIDENTIFIER  NOT NULL REFERENCES Projects(Id),
  Level                 INT               NOT NULL,   -- 0 | 1 | 2 | 3
  SubLevel              INT               NOT NULL DEFAULT 1,
  -- Revision number within the level: 1, 2, 3 ...
  -- Displayed as "Level 2.1", "Level 2.2", etc.
  -- Increments automatically on each rejection + re-draft cycle.
  DisplayName           NVARCHAR(100)     NULL,
  -- Optional override label, e.g. "Level 2.2 — Value Engineering Round"
  -- If null, UI shows auto-generated "Level {Level}.{SubLevel}"
  ParentBudgetLevelId   UNIQUEIDENTIFIER  NULL REFERENCES BudgetLevels(Id),
  -- Points to the BudgetLevel this was copied from.
  -- L2.2 → L2.1 | L3.1 → L2.x (the approved L2 it was promoted from)
  -- NULL only for the very first budget level of a project (L0.1).
  Status                NVARCHAR(50)      NOT NULL DEFAULT 'Draft',
  -- 'Draft' | 'Submitted' | 'Approved' | 'Locked' | 'Rejected'
  SubmittedAt           DATETIME2         NULL,
  SubmittedByUserId     UNIQUEIDENTIFIER  NULL REFERENCES Users(Id),
  ApprovedAt            DATETIME2         NULL,
  ApprovedByUserId      UNIQUEIDENTIFIER  NULL REFERENCES Users(Id),
  RejectionComment      NVARCHAR(1000)    NULL,
  CreatedAt             DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedAt             DATETIME2         NOT NULL DEFAULT GETUTCDATE(),

  CONSTRAINT UQ_ProjectLevelSubLevel UNIQUE (ProjectId, Level, SubLevel)
  -- Enforces: only one L2.1, one L2.2, etc. per project.
)
```

### Sub-Level Revision Workflow

```
Project created
  └── L0.1 (Draft)
        ↓ submit
      L0.1 (Submitted)
        ↓ approved
      L0.1 (Approved → Locked)
        ↓ promote  [API copies all line items; BaselineAmount frozen]
      L1.1 (Draft)
        ↓ submit
      L1.1 (Submitted)
        ↓ rejected
      L1.1 (Rejected)   → API auto-creates L1.2 (Draft, copy of L1.1)
      L1.2 (Draft)       [editor makes changes]
        ↓ submit
      L1.2 (Submitted)
        ↓ approved
      L1.2 (Approved → Locked)
        ↓ promote
      L2.1 (Draft) ...and so on through L3
```

**Rules:**
- Only one sub-level per project+level can be `Draft` or `Submitted` at a time.
- Rejected sub-levels are immutable (Status = 'Rejected', all rows locked).
- Promotion to the next major level is only available when the current level's latest sub-level is `Approved`.
- Promotion calls `POST /budget-levels/{id}/promote` which creates the next level's first sub-level (e.g., L3.1) and copies all line items, freezing `BaselineAmount` from the parent's `TakeoffAmount`.

### API Endpoints for Sub-Level Lifecycle

| Action | Endpoint |
|--------|----------|
| Submit for approval | `POST /budget-levels/{id}/approval/submit` |
| Approve + lock | `POST /budget-levels/{id}/approval/approve` |
| Reject (auto-creates next sub-level) | `POST /budget-levels/{id}/approval/reject` |
| Promote to next major level | `POST /budget-levels/{id}/promote` |

---

## Divisions

Seeded once. Shared across all projects. Do not modify after deployment.

```sql
CREATE TABLE Divisions (
  Id        INT           PRIMARY KEY IDENTITY,
  CsiCode   NVARCHAR(10)  NOT NULL UNIQUE,
  -- '01','02','03','04','05','06','07','08','09','10','11','12',
  -- '13','14','21','22','23','26','27','28','31','32','33','34','48','49',
  -- 'FFE','50','51','55','98','99','BR'
  Name      NVARCHAR(100) NOT NULL,   -- e.g. 'Div 3 — Concrete'
  IsMarkup  BIT           NOT NULL DEFAULT 0,   -- TRUE for 50,51,55,98,99,BR
  IsFfe     BIT           NOT NULL DEFAULT 0,
  SortOrder INT           NOT NULL
)
```

> ⚠️ **Division 29 vs Division 31 — Decision Required Before Seeding**
>
> The Budget Levels reference app lists `Div 29 — Site Work / Grading` for the Grading line item. Standard CSI does not have a Division 29 — Earthwork is **Division 31** in CSI MasterFormat. Both the West Henderson HTML and the Gagnier Sr PDF use Division 31.
>
> **Decision:** Use **Division 31** (standard CSI) for all earthwork and grading line items. The label "Div 29" in the Budget Levels App is a legacy reference and will NOT be seeded as a separate division. Seed `CsiCode = '31'` with name `'Div 31 — Earthwork'`.
>
> Update the Budget Levels reference app HTML if needed so the UI stays consistent with the database.

---

## LineItems

Seeded master list. Not project-specific. Projects reference these; custom rows are created inline.

```sql
CREATE TABLE LineItems (
  Id              INT           PRIMARY KEY IDENTITY,
  DivisionId      INT           NOT NULL REFERENCES Divisions(Id),
  CostCode        NVARCHAR(20)  NOT NULL,     -- e.g. '03-3101', '06-1100'
  Name            NVARCHAR(200) NOT NULL,     -- e.g. 'Framing', 'Slabs'
  DefaultCategory NVARCHAR(5)   NULL,         -- 'S' | 'A' | 'RR' | 'B'
  DefaultSubJob   NVARCHAR(30)  NULL,         -- see SubJob enum below
  DefaultUom      NVARCHAR(20)  NULL,         -- 'SF' | 'Unit' | 'LF' | 'LS' | 'EA' | 'SY' | 'SQ' | 'LBS' | 'CY' | 'GAL'
  DefaultSource   NVARCHAR(100) NULL,         -- 'Allowance' | 'Historical' | 'N/A'
  GroupKey        NVARCHAR(100) NULL,         -- links to TradePackages for bid mapping in L3
  SortOrder       INT           NOT NULL,
  IsActive        BIT           NOT NULL DEFAULT 1
)
```

### SubJob Enum Values

| Value | Description |
|-------|-------------|
| `BUILDING` | Main building structure and interiors |
| `ON-SITE` | On-site improvements (paving, landscaping, utilities) |
| `OFFSITE` | Off-site utility connections, street work |
| `POOL AREA` | Pool deck, hardscape, fence |
| `POOL EQUIP` | Pool mechanical equipment |
| `PUMPHOUSE` | Fire pump house structure |
| `CARPORT` | Covered parking structure |
| `COMMON AREA` | Leasing office, rec room, shared spaces |
| `DUMPSTERS` | Trash enclosures and hauling |
| `OTHER SITE` | Miscellaneous site items |
| `WET UTIL` | Wet utility work (water, sewer, storm, gas) |
| `EV` | EV charging infrastructure |
| `FFE` | Furniture, Fixtures & Equipment |

### Category Enum Values

| Value | Meaning |
|-------|---------|
| `S` | Standard — normal construction cost |
| `A` | Allowance — estimated, final scope TBD |
| `RR` | Repair & Replace — remediation work |
| `B` | Bond / Insurance — markup item |
| `F` | Fee — contractor fee markup |
| `R` | Risk — bid risk or contingency |

---

## BudgetLevelLineItems

The core data table. One row per line item per budget level.

```sql
CREATE TABLE BudgetLevelLineItems (
  Id                UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId     UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  LineItemId        INT               NULL REFERENCES LineItems(Id),
  -- NULL if IsCustom = true

  -- Custom line item fields (when LineItemId is null)
  IsCustom          BIT               NOT NULL DEFAULT 0,
  CustomLabel       NVARCHAR(200)     NULL,
  CustomDivisionId  INT               NULL REFERENCES Divisions(Id),

  -- Budget metadata (displayed in master budget table)
  CostCode          NVARCHAR(20)      NULL,   -- copied from LineItem or entered for custom
  Category          NVARCHAR(5)       NULL,   -- 'S' | 'A' | 'RR' | 'B' — see Category enum
  SubJob            NVARCHAR(30)      NULL,   -- see SubJob enum
  Source            NVARCHAR(100)     NULL,
  -- 'Bruner' | 'Durango' | 'Torrey Pines' | 'Pebble' | 'Decatur' | 'Flamingo'
  -- | 'South Nellis' | 'West Henderson' | 'Allowance' | 'Budget' | 'Proposal'
  -- | 'Soft Bid' | 'Historical' | 'N/A'

  -- Unit of measure (level-dependent)
  UnitOfMeasure     NVARCHAR(100)     NULL,

  -- Takeoff (all levels)
  TakeoffQuantity   DECIMAL(18,4)     NULL,
  TakeoffUnitPrice  DECIMAL(18,4)     NULL,
  EscalationPct     DECIMAL(6,4)      NOT NULL DEFAULT 0,  -- e.g. 0.05 = 5%
  TakeoffAmount     DECIMAL(18,2)     NULL,
  -- Stored (not computed) to allow manual override

  -- Baseline (frozen at promotion time — never changes after set)
  BaselineAmount    DECIMAL(18,2)     NULL,
  -- Set once when this BudgetLevel is created via promotion from a parent level.
  -- = parent's TakeoffAmount at the moment of promotion.
  -- Used for L2 vs L3 variance comparison and the "Changes" view.
  -- NULL on L0.1 (no parent), NULL if line item had no value in parent.

  -- Proposal / Bid amount (Level 3 dual-track)
  ProposalAmount    DECIMAL(18,2)     NULL,
  PreferredSource   NVARCHAR(20)      NULL DEFAULT 'takeoff',
  -- 'takeoff' | 'proposal' — which value the L3 budget uses

  -- Trade package link (Level 3)
  GroupKey          NVARCHAR(100)     NULL,   -- matches TradePackages.GroupKey for bid mapping
  SelectedProposalId UNIQUEIDENTIFIER NULL REFERENCES Proposals(Id),
  -- Per-group-key selected bidder override. NULL = use TradePackages.AwardedBidderId as default.
  -- Enables the Bid Picker to select a different bidder for one cost-code group within a trade.

  -- Two-track adjustment (L3 only)
  CommittedAdjustmentAmount  DECIMAL(18,2)  NULL,
  -- "Recommended Adj." shown in Master Budget tab (read-only after commit).
  -- Committed = approved by estimator, shows in the locked master view.
  ProposedAdjustmentAmount   DECIMAL(18,2)  NULL,
  -- Working draft in Proposal L3 Budget tab (editable).
  -- When estimator clicks "Commit Adjustments", ProposedAdjustmentAmount → CommittedAdjustmentAmount.
  ChangeNote         NVARCHAR(1000)   NULL,
  -- Explanation text shown in the "Summary of Significant Changes" tab.
  -- Populated per group key when |ProposedAdjustmentAmount| ≥ threshold (default $50k).

  -- Notes
  Assumption        NVARCHAR(500)     NULL,
  Notes             NVARCHAR(1000)    NULL,
  Section           NVARCHAR(30)      NULL,   -- 'standard' | 'alternate'

  IsLocked          BIT               NOT NULL DEFAULT 0,
  CreatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),

  INDEX IX_BLLI_LevelId (BudgetLevelId),
  INDEX IX_BLLI_LineItemId (LineItemId),
  INDEX IX_BLLI_GroupKey (GroupKey) WHERE GroupKey IS NOT NULL
)
```

---

## Markups

One row per markup kind per budget level. Replaces the single-row approach to support both fixed and percentage modes independently per line.

```sql
CREATE TABLE Markups (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId   UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  Kind            NVARCHAR(30)      NOT NULL,
  -- 'general_requirements' | 'bid_risk' | 'contingency' | 'bonds' | 'insurance' | 'overhead' | 'fee'
  Label           NVARCHAR(100)     NOT NULL,   -- display name, e.g. 'Construction Contingency'
  CostCode        NVARCHAR(10)      NOT NULL,   -- '01' | 'BR' | '55' | '50' | '51' | '99' | '98'
  Mode            NVARCHAR(10)      NOT NULL,   -- 'pct' | 'fixed'
  Rate            DECIMAL(8,6)      NULL,       -- e.g. 0.060000 = 6%; NULL when Mode = 'fixed'
  FixedAmount     DECIMAL(18,2)     NULL,       -- NULL when Mode = 'pct'
  SortOrder       SMALLINT          NOT NULL DEFAULT 0,
  IsActive        BIT               NOT NULL DEFAULT 1,
  UpdatedAt       DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedByUserId UNIQUEIDENTIFIER  NOT NULL REFERENCES Users(Id),

  CONSTRAINT UQ_Markups_LevelKind UNIQUE (BudgetLevelId, Kind)
)
```

### Default Markup Rows (seeded per BudgetLevel)

| Kind | Label | CostCode | Mode | Default Rate |
|------|-------|----------|------|--------------|
| `general_requirements` | General Requirements | `01` | `pct` | 6.00% |
| `bid_risk` | Bid Risk | `BR` | `pct` | 2.00% |
| `contingency` | Construction Contingency | `55` | `pct` | 5.00% |
| `bonds` | Sub Bonds | `50` | `pct` | 1.10% |
| `insurance` | GL Insurance | `51` | `fixed` | project-specific |
| `overhead` | Overhead | `99` | `pct` | 2.00% |
| `fee` | Contractor Fee | `98` | `pct` | 6.00% |

### Markup Calculation Order

Markups apply to the **Markup Base** = Hard Cost + General Requirements.
Exclusions: `01`, `50`, `51`, `55`, `98`, `99`, `BR` divisions are excluded from all markup bases.

```
Hard Cost = SUM(all BudgetLevelLineItems where Division NOT IN excluded codes)
General Requirements (01) = Hard Cost × GR rate
Markup Base = Hard Cost + General Requirements

Bid Risk       = Markup Base × bid_risk rate  (or FixedAmount)
Contingency    = Markup Base × contingency rate
Sub Bonds      = Markup Base × bonds rate
GL Insurance   = FixedAmount  (or Markup Base × insurance rate)
Overhead       = Markup Base × overhead rate
Contractor Fee = Markup Base × fee rate

Total = Hard Cost + GR + Bid Risk + Contingency + Bonds + Insurance + Overhead + Fee
```

---

## ComparableProjects

Reference projects used as cost source benchmarks. Seeded from Ovation's project history.

```sql
CREATE TABLE ComparableProjects (
  Id            UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  Name          NVARCHAR(200)     NOT NULL UNIQUE,
  -- 'Bruner' | 'Durango' | 'Torrey Pines' | 'Pebble' | 'Decatur'
  -- | 'Flamingo' | 'South Nellis' | 'West Henderson'
  TotalUnits    INT               NULL,
  TotalGsf      DECIMAL(12,2)     NULL,
  ContractDate  DATE              NULL,
  City          NVARCHAR(100)     NULL,
  State         NCHAR(2)          NULL,
  ProductType   NVARCHAR(50)      NULL,
  IsActive      BIT               NOT NULL DEFAULT 1,
  CreatedAt     DATETIME2         NOT NULL DEFAULT GETUTCDATE()
)
```

---

## ComparableProjectCosts

Per-division cost data for each comparable project. Used to power the benchmark comparison view.
Seeded manually from Ovation's historical project records (one-time data entry per comparable project).

```sql
CREATE TABLE ComparableProjectCosts (
  Id                    UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ComparableProjectId   UNIQUEIDENTIFIER  NOT NULL REFERENCES ComparableProjects(Id) ON DELETE CASCADE,
  DivisionId            INT               NOT NULL REFERENCES Divisions(Id),
  TotalAmount           DECIMAL(18,2)     NULL,   -- total cost for this division
  CostPerUnit           DECIMAL(18,2)     NULL,   -- TotalAmount ÷ ComparableProject.TotalUnits
  CostPerGrossSF        DECIMAL(18,4)     NULL,   -- TotalAmount ÷ ComparableProject.TotalGsf
  Notes                 NVARCHAR(500)     NULL,

  CONSTRAINT UQ_ComparableProjectCosts UNIQUE (ComparableProjectId, DivisionId),
  INDEX IX_ComparableProjectCosts_DivisionId (DivisionId)
)
```

> **How the benchmark view uses this:**
> For each CSI division in the current project, the API fetches `CostPerUnit` from each active `ComparableProject` and renders them side by side against the current project's `CostPerUnit`. This requires `ComparableProjectCosts` rows to exist for each division × comparable project combination before the benchmark tab shows meaningful data.

---

## TradePackages

L3 only. One row per subcontractor trade scope. Links to BudgetLevelLineItems via `GroupKey`.

```sql
CREATE TABLE TradePackages (
  Id                UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId     UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  TradeKey          NVARCHAR(100)     NOT NULL,
  -- e.g. 'framing', 'concrete-slab', 'electrical', 'wet-utilities'
  Title             NVARCHAR(200)     NOT NULL,   -- display name, e.g. 'Framing'
  EstimatedCostL2   DECIMAL(18,2)     NULL,       -- L2 baseline for variance tracking
  Status            NVARCHAR(20)      NOT NULL DEFAULT 'Open',
  -- 'Open' | 'Proposed' | 'Awarded'
  AwardedBidderId   UNIQUEIDENTIFIER  NULL REFERENCES Bidders(Id),
  AwardedAmount     DECIMAL(18,2)     NULL,
  GroupKeys         NVARCHAR(MAX)     NULL,
  -- JSON array of BudgetLevelLineItems.GroupKey values this trade covers
  -- e.g. '["06-1100-framing","06-1109-cabana-framing"]'
  SortOrder         SMALLINT          NOT NULL DEFAULT 0,
  Notes             NTEXT             NULL,

  CONSTRAINT UQ_TradePackages_LevelKey UNIQUE (BudgetLevelId, TradeKey)
)
```

---

## Bidders

Subcontractor / vendor company records. Shared reference — not per project.

```sql
CREATE TABLE Bidders (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  CompanyName     NVARCHAR(200)     NOT NULL,
  ContactName     NVARCHAR(200)     NULL,
  Email           NVARCHAR(256)     NULL,
  Phone           NVARCHAR(30)      NULL,
  LicenseNumber   NVARCHAR(100)     NULL,
  IsActive        BIT               NOT NULL DEFAULT 1,
  CreatedAt       DATETIME2         NOT NULL DEFAULT GETUTCDATE()
)
```

---

## Proposals

One bid from one bidder for one trade package.

```sql
CREATE TABLE Proposals (
  Id                UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  TradePackageId    UNIQUEIDENTIFIER  NOT NULL REFERENCES TradePackages(Id) ON DELETE CASCADE,
  BudgetLevelId     UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  BidderId          UNIQUEIDENTIFIER  NOT NULL REFERENCES Bidders(Id),
  BaseBid           DECIMAL(18,2)     NULL,
  LeveledBid        DECIMAL(18,2)     NULL,   -- adjusted during leveling session
  SubmittedBy       NVARCHAR(200)     NULL,
  RevisionDate      DATE              NULL,
  Status            NVARCHAR(20)      NOT NULL DEFAULT 'Submitted',
  -- 'Submitted' | 'Proposed' | 'Awarded' | 'Declined'
  IsSelected        BIT               NOT NULL DEFAULT 0,
  AwardedAmount     DECIMAL(18,2)     NULL,
  Notes             NVARCHAR(1000)    NULL,
  SourceFileId      UNIQUEIDENTIFIER  NULL REFERENCES UploadedFiles(Id),
  CreatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  UpdatedAt         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),

  INDEX IX_Proposals_TradePackageId (TradePackageId),
  INDEX IX_Proposals_BudgetLevelId (BudgetLevelId)
)
```

---

## ProposalLineItems

Scope line items within a proposal — used in the summary sheet / bid leveling view.

```sql
CREATE TABLE ProposalLineItems (
  Id          UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  ProposalId  UNIQUEIDENTIFIER  NOT NULL REFERENCES Proposals(Id) ON DELETE CASCADE,
  Label       NVARCHAR(300)     NOT NULL,
  Section     NVARCHAR(30)      NOT NULL DEFAULT 'LINE ITEMS',
  -- 'LINE ITEMS' | 'ADDITIONAL ITEMS' | 'ALTERNATES'
  Amount      DECIMAL(18,2)     NULL,
  SortOrder   SMALLINT          NOT NULL DEFAULT 0,
  Notes       NVARCHAR(500)     NULL
)
```

---

## Takeoffs

Site work quantity takeoffs. Dual-track L2 vs L3 side-by-side for the takeoff view.

```sql
CREATE TABLE Takeoffs (
  Id            UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id) ON DELETE CASCADE,
  TradeKey      NVARCHAR(100)     NOT NULL,
  -- 'grading-pavings' | 'wet-utilities' | 'site-concrete' | 'site-iron' | 'masonry'
  Description   NVARCHAR(300)     NOT NULL,
  Uom           NVARCHAR(20)      NULL,

  -- L2 baseline
  QuantityL2    DECIMAL(18,4)     NULL,
  UnitPriceL2   DECIMAL(18,4)     NULL,
  TotalL2       DECIMAL(18,2)     NULL,   -- stored: QuantityL2 × UnitPriceL2

  -- L3 recommended
  QuantityL3    DECIMAL(18,4)     NULL,
  UnitPriceL3   DECIMAL(18,4)     NULL,
  TotalL3       DECIMAL(18,2)     NULL,   -- stored: QuantityL3 × UnitPriceL3

  SortOrder     SMALLINT          NOT NULL DEFAULT 0,
  Notes         NVARCHAR(500)     NULL,

  INDEX IX_Takeoffs_BudgetLevel_Trade (BudgetLevelId, TradeKey)
)
```

---

## BudgetApprovals

Immutable record. Created when an authorized user signs off on a budget.
Once created, never update or delete.

```sql
CREATE TABLE BudgetApprovals (
  Id              UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId   UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  ApprovedBy      NVARCHAR(200)     NOT NULL,
  ApprovedAt      DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  SignatureData   NVARCHAR(MAX)     NULL,   -- base64-encoded canvas PNG
  Sha256Hash      NCHAR(64)         NOT NULL,  -- SHA-256 of SnapshotJson
  SnapshotJson    NVARCHAR(MAX)     NOT NULL,  -- full budget state at approval time
  Version         NVARCHAR(20)      NULL,
  Notes           NVARCHAR(1000)    NULL,

  INDEX IX_BudgetApprovals_BudgetLevelId (BudgetLevelId)
)
```

---

## Users

```sql
CREATE TABLE Users (
  Id          UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  AzureOid    NVARCHAR(100)     NOT NULL UNIQUE,
  Email       NVARCHAR(256)     NOT NULL UNIQUE,
  Name        NVARCHAR(200)     NOT NULL,
  Department  NVARCHAR(50)      NULL,
  -- 'Development' | 'Design' | 'Purchasing' | 'Finance' | 'Entitlements' | 'FieldOps'
  IsActive    BIT               NOT NULL DEFAULT 1,
  CreatedAt   DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  LastLoginAt DATETIME2         NULL
)
```

---

## AuditLog

Append-only. Never update or delete rows.

```sql
CREATE TABLE AuditLog (
  Id           BIGINT            PRIMARY KEY IDENTITY,
  UserId       UNIQUEIDENTIFIER  NOT NULL REFERENCES Users(Id),
  EntityType   NVARCHAR(100)     NOT NULL,  -- e.g. 'BudgetLevelLineItem'
  EntityId     NVARCHAR(100)     NOT NULL,  -- GUID as string
  Field        NVARCHAR(100)     NOT NULL,  -- e.g. 'TakeoffAmount'
  OldValue     NVARCHAR(MAX)     NULL,
  NewValue     NVARCHAR(MAX)     NULL,
  ChangedAt    DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  IpAddress    NVARCHAR(45)      NULL,

  INDEX IX_AuditLog_EntityType_EntityId (EntityType, EntityId),
  INDEX IX_AuditLog_UserId (UserId),
  INDEX IX_AuditLog_ChangedAt (ChangedAt)
)
```

---

## UploadedFiles

```sql
CREATE TABLE UploadedFiles (
  Id               UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  BudgetLevelId    UNIQUEIDENTIFIER  NOT NULL REFERENCES BudgetLevels(Id),
  OriginalName     NVARCHAR(500)     NOT NULL,
  BlobPath         NVARCHAR(1000)    NOT NULL,
  FileType         NVARCHAR(10)      NOT NULL,  -- 'xlsx' | 'xls' | 'csv' | 'pdf'
  FileSizeBytes    BIGINT            NOT NULL,
  Status           NVARCHAR(50)      NOT NULL DEFAULT 'Queued',
  -- 'Queued' | 'Processing' | 'Complete' | 'NeedsMapping' | 'Error'
  RowsParsed       INT               NULL,
  ErrorMessage     NVARCHAR(MAX)     NULL,
  UploadedByUserId UNIQUEIDENTIFIER  NOT NULL REFERENCES Users(Id),
  UploadedAt       DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  ProcessedAt      DATETIME2         NULL
)
```

---

## Notifications

```sql
CREATE TABLE Notifications (
  Id          UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
  UserId      UNIQUEIDENTIFIER  NOT NULL REFERENCES Users(Id),
  Type        NVARCHAR(100)     NOT NULL,
  -- 'BudgetSubmitted' | 'BudgetApproved' | 'BudgetRejected'
  -- | 'FileParsed' | 'FileNeedsMapping' | 'TradeAwarded'
  Title       NVARCHAR(200)     NOT NULL,
  Body        NVARCHAR(500)     NOT NULL,
  IsRead      BIT               NOT NULL DEFAULT 0,
  EntityType  NVARCHAR(100)     NULL,
  EntityId    NVARCHAR(100)     NULL,
  CreatedAt   DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
  ReadAt      DATETIME2         NULL
)
```

---

## Conventions

- **Primary keys:** `UNIQUEIDENTIFIER` (GUID) for all user-facing entities. `INT IDENTITY` for seeded master data (Divisions, LineItems) and high-volume tables (AuditLog).
- **Timestamps:** Always `DATETIME2` in UTC. Never `DATETIME`.
- **Soft deletes:** Not used. Records are deactivated via `IsActive` flag where applicable.
- **Naming:** PascalCase table and column names. Foreign keys named `{Entity}Id`.
- **Indexes:** Defined in EF Core `OnModelCreating` — not raw SQL.
- **Markup cost codes:** `01` = GR, `BR` = Bid Risk, `55` = Contingency, `50` = Bonds, `51` = Insurance, `99` = Overhead, `98` = Fee.
- **Approved budgets:** Immutable. Append a new `BudgetApprovals` row; set `BudgetLevels.Status = 'Locked'`. Never update line items on a Locked budget level.
- **Sub-levels:** Displayed as `Level {Level}.{SubLevel}` (e.g., "Level 2.3"). Unique per project+level+sublevel. Only one sub-level per project+level may be in `Draft` or `Submitted` status at any time.
- **BaselineAmount:** Set once at promotion time (copied from parent's `TakeoffAmount`). Never written again. Used exclusively for variance comparison — not for budget calculation.
- **Division 31 = Earthwork / Grading.** Do not seed a Division 29. The Budget Levels reference app uses "Div 29" as a legacy label; the canonical code is 31.
- **ComparableProjectCosts** must be manually seeded per comparable project before the benchmark view returns meaningful data. This is a one-time data entry task, not automated.
