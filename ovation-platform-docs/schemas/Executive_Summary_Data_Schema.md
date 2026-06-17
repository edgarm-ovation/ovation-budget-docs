# ESTIMATION ASSISTANT — DATA SCHEMA EXECUTIVE SUMMARY

**Date:** June 17, 2026  
**Prepared for:** Ovation Leadership, Budgeting Staff, Development Team  
**Status:** Foundation Design (Ready for Implementation)  

---

## ONE-PAGE OVERVIEW

The Estimation Assistant's database foundation supports budgets across four levels (Level 0 = conceptual, Level 3 = construction docs), with role-based access control, audit logging, and AI-assisted estimation powered by historical project data.

**Core principle:** One project → multiple scenarios → multiple budgets per scenario. Each budget owns its property details, cost structure (LineItems), quantity takeoffs, vendor proposals, and access controls.

---

## WHAT THE SCHEMA STORES

### Primary Records
- **Projects** (master) — Project name, location, timeline, product type (Senior, Workforce, etc.)
- **Budgets** — Four versions (Level 0, 1, 2, 3) per project, each versioned (1.0, 1.1, etc.)
- **PropertyDetails** — Site acreage, building GSF, unit count, floor count, parking
- **LineItems** — CSI-structured budget hierarchy (Concrete, Framing, HVAC, etc.)
- **TakeoffItems** — Granular quantities & unit costs; tied to proposals when available
- **Proposals** — Vendor bids on major scopes (Framing, HVAC, Electrical, etc.)

### Audit & Security
- **BudgetAccessControl** — Role assignment (Viewer, Editor, Approver, Admin) per user per budget
- **AuditLog** — Every change: user, table, field, old/new value, timestamp, IP address

### Reporting & Intelligence
- **BudgetSummary** — Pre-calculated totals (hard cost, soft cost, contingency, per-unit, per-GSF)
- **BudgetComparisons** — Variance between budget levels (Level 1 vs. 2 vs. 3)
- **HistoricalProjects & HistoricalCosts** — Past Ovation project data for estimation benchmarking
- **ComparableProjects** — Market projects for validation and feasibility checks

---

## WHY THIS DESIGN

### 1. Supports Budget Evolution (Level 0 → 3)
Each level represents increasing detail and decreasing estimation risk:

| Level | Focus | Estimation Method | Takeoff Detail |
|-------|-------|-------------------|---|
| **0** | Feasibility | Historical comparables | None; order-of-magnitude only |
| **1** | Project commitment | Comparable projects + soft bids | High-level items only |
| **2** | Detailed planning | Detailed plans + soft bids | Moderate detail; validates Level 1 |
| **3** | Construction docs | 100% plans + vendor proposals | Full takeoff; proposal-based |

The schema **allows side-by-side comparison** and **tracks variance** as scope and pricing evolve.

### 2. Protects Budget Integrity
- **Role-based access** — Field staff can't change contingency; finance can't add line items
- **Audit trail** — Every change logged with user, timestamp, IP, old/new value
- **Version control** — Each level and version is immutable once submitted/approved
- **No deletion** — Soft deletes only; historical data always available for dispute resolution

### 3. Enables AI-Assisted Estimation
- **HistoricalProjects & HistoricalCosts** provide training data
- AI engine can propose cost per unit, per GSF based on product type and comparable projects
- **BudgetAssumptions** table captures rules (contingency %, markups) for consistent estimation
- **TakeoffItems** labeled by source (Proposal, Historical, Estimate) enable validation

### 4. Supports Rapid Reporting
- **BudgetSummary** is denormalized and pre-calculated → fast dashboard loads
- **Indexes on common queries** (BudgetId, ProjectId, BudgetLevel, LineItemId)
- **Views** for standard reports (BudgetOverview, LineItemDetail, LevelComparison)
- **Dual-track takeoff** (proposal vs. estimate) visible side-by-side for QC

---

## KEY TECHNICAL DECISIONS

### Hierarchical LineItems (Self-Join)
```
Division (Level 1)
  ├─ Section (Level 2)
  │   ├─ Item (Level 3)
  │   └─ Item (Level 3)
  └─ Section (Level 2)
      └─ Item (Level 3)
```
**Why:** Supports unlimited nesting and CSI coding; avoids separate "sections" and "items" tables; enables tree queries with single recursive CTE.

### 1:1 PropertyDetails per Budget
Each budget captures its own property state (GSF, unit mix, parking). When you create Level 2, you inherit from Level 1 but can update if plans change.

**Why:** Budgets at different levels can have different site assumptions (e.g., Level 1 estimated 5 acres, Level 2 confirmed 4.9 acres); change is auditable.

### Dual-Track Takeoff (Proposal-Based vs. Estimate)
Every TakeoffItem has `Qty × UnitCost` AND a link to `Proposals.ProposalAmount`.

**Why:** Level 3 reality — estimate stays as validation, but proposal becomes the contract basis. Both visible for audit and change management.

### Denormalized BudgetSummary
Pre-calculates and stores `TotalHardCost`, `TotalSoftCost`, `CostPerUnit`, `CostPerGSF`.

**Why:** Dashboard performance. Recalculated after each budget change by application trigger. Avoids expensive SUM/GROUP queries on LineItems and TakeoffItems.

### Soft Delete (`IsActive` Bit)
Projects and budgets are never deleted; marked `IsActive = 0`.

**Why:** Compliance and dispute resolution. Regulators and investors need to see historical versions. Accidental deletes are recoverable.

---

## EXAMPLE WORKFLOWS

### New Project Budget (Level 0)
```
1. INSERT Projects("Bruner Senior", ProductType="Senior", Location="Las Vegas", TimelineMonths=20)
2. INSERT Budgets(ProjectId, Level=0, Version=1)
3. INSERT PropertyDetails(BuildingGSF=196289, Acres=4.9, Units=194)
4. INSERT UnitMix:
   - 1BR-1BA: 126 units
   - 2BR-1BA: 68 units
5. INSERT LineItems hierarchy (CSI divisions → sections → items)
   - Division: "03 00 00 Concrete" → Estimate=$2,900,000
     - Section: "03 20 00 Concrete Reinforcing" → Estimate=$500,000
       - Item: "Rebar placement" → Estimate (from historical similar projects)
6. AI engine:
   - Proposes cost per unit based on Historical data: Senior housing ~$425k/unit → 194 units = $82.5M
   - Compares to manual estimate; flags outliers
7. INSERT BudgetSummary: TotalProjectCost=$82.5M, CostPerUnit=$425,258, CostPerGSF=$420
8. INSERT BudgetAccessControl: Admin role for project manager; Editor role for finance
```

### Level 1 → Level 2 Refinement
```
1. Copy all LineItems and TakeoffItems from Level 1 budget
2. INSERT Budgets(ProjectId, Level=2, Version=1)
3. With 90% design plans in hand, update TakeoffItems:
   - "Slab Forming": Qty refined from estimated 5,000 SF to 4,850 SF (from plans)
   - "Rebar": Qty refined from estimated 200 tons to 187 tons
4. Request soft bids from framing, HVAC, electrical subcontractors
5. INSERT Proposals for each trade
6. Compare each proposal to Level 1 estimate; request clarification if >10% variance
7. Recalculate BudgetSummary
8. INSERT BudgetComparisons(Level1BudgetId, Level2BudgetId, Variance$, VariancePercent)
   - "Level 2 is 3.2% below Level 1 due to tighter takeoff and market softening"
```

### Level 3: Proposals Override Estimates
```
1. Distribute 100% permit plans to all major trades
2. Subcontractors submit formal proposals (CSI scope + lump sum)
3. For each proposal:
   - INSERT Proposal(VendorName, TradeScope, ProposalAmount, Status="Pending")
   - Map proposal to existing LineItem/TakeoffItems
   - If ProposalAmount > sum of TakeoffItems:
     - Flag for review: "Framing proposal $X exceeds estimate by $Y"
     - Option to negotiate, redesign, or draw contingency
   - If ProposalAmount < estimate:
     - Option to reallocate savings or improve other scopes
4. Update TakeoffItems:
   - Set IsProposalBased=1
   - Set Source="Proposal"
   - Set ProposalRef to the Proposals.ProposalId
5. Recalculate BudgetSummary
6. Lock budget for construction planning: INSERT approval record, set IsSubmitted=1
```

### Feasibility Check (AI-Assisted)
```
1. User enters Level 0 budget details (project name, unit count, location, product type)
2. AI engine queries HistoricalProjects and ComparableProjects:
   - Senior housing in Vegas: avg $420k/unit, range $380k–$460k
   - Regional projects: avg $430k/unit
3. Proposes total budget: 194 units × $430k = $83.4M
4. Compares to user's manual estimate; highlights outliers
5. Surfaces key cost drivers: "HVAC is 12% of total, above typical 10% for senior housing"
6. Recommends comparable for benchmarking: "Similar project completed in Nevada at $425k/unit"
```

---

## SECURITY & COMPLIANCE

### Role-Based Access Control
Every budget has a role matrix:

| Role | Read | Edit | Delete | Approve |
|------|------|------|--------|---------|
| **Viewer** | ✓ | — | — | — |
| **Editor** | ✓ | ✓ | — | — |
| **Approver** | ✓ | ✓ | — | ✓ |
| **Admin** | ✓ | ✓ | ✓ | ✓ |

**Application enforces:** Before any write, check `BudgetAccessControl` for current user's role.

### Audit Trail
Every change logged:

```
AuditLogId | BudgetId | UserId | ActionType | TableName | FieldName | OldValue | NewValue | ChangeDate | IPAddress
```

**Example entry:**
```
1a2b3c | BudgetId_X | jsmith | Update | LineItems | EstimatedAmount | 500000 | 485000 | 2026-06-17 14:22:15 | 192.168.1.100
```

**Compliance use:** "Who changed the contingency? When? Why?" Fully traceable.

### Data Protection
- All PII (if any: addresses, contact info) stored encrypted at rest
- Soft deletes — no hard delete available
- Backup retention: minimum 7 years (regulatory for construction finance)

---

## PERFORMANCE & SCALABILITY

### Indexing Strategy
**Primary indexes (automatic on foreign keys):**
- `Budgets(ProjectId, BudgetLevel)` — Fast budget lookup
- `LineItems(BudgetId, ParentLineItemId)` — Tree traversal
- `TakeoffItems(BudgetId, LineItemId)` — Cost aggregation
- `AuditLog(BudgetId, ChangeDate)` — Audit queries

**Result:** Most common queries (get budget, list line items, sum costs) execute in <100ms on Azure SQL.

### Denormalization Strategy
**BudgetSummary table** stores pre-calculated totals — avoids expensive SUM() operations on every dashboard load.

**When to recalculate:** After any LineItem or TakeoffItem change (via app trigger or batch job).

### Estimated Data Volume (Year 1)
- **Projects:** ~50
- **Budgets:** ~150 (3 levels × 50 projects, with versions)
- **LineItems:** ~6,000 (40 per budget × 150)
- **TakeoffItems:** ~18,000 (120 per budget × 150)
- **AuditLog:** ~180,000 (12 changes/day × 365 days × ~50 users)

**Storage footprint:** ~500 MB (well within Azure SQL free tier; scale as needed).

---

## IMPLEMENTATION TIMELINE

### Phase 1: Infrastructure (Week 1)
- Deploy schema to Azure SQL
- Create indexes
- Load historical project data (200+ past projects)
- Write stored procedures for common operations

### Phase 2: Application Integration (Weeks 2–3)
- Connect app to database
- Implement role-based access checks
- Build line item editor UI
- Test audit logging

### Phase 3: Reporting & AI (Weeks 4–5)
- Build BudgetSummary calculation triggers
- Create dashboard views (project overview, level comparison, cost per unit)
- Integrate estimation engine (queries historical data, proposes costs)
- AI-powered outlier detection

### Phase 4: Testing & Deployment (Weeks 6–8)
- UAT with budgeting staff
- Data migration (import existing budgets from Excel)
- Go-live with training

---

## SUCCESS METRICS

1. **Budget creation time:** Reduce from 2 weeks (manual Excel) to 2 days (database + UI)
2. **Estimation accuracy:** Decrease Level 1 → Level 3 variance to <5% (historically 8–12%)
3. **Audit trail:** 100% of changes logged and recoverable
4. **User adoption:** >90% of budgeting staff using system within 3 months
5. **Proposal variance:** Proposals come in within ±5% of estimate 80% of the time (vs. ±10% today)

---

## NEXT STEPS

1. **Approve schema design** — Review with database architect and CFO
2. **Schedule kickoff** — Team alignment on terminology and workflows
3. **Assign data steward** — Owner of historical project data quality
4. **Create user stories** — Translate schema into feature backlog for UI developers
5. **Plan data migration** — Identify existing Excel budgets to import

---

**Questions?** Contact the development team or your project manager for clarification on any aspect of this design.

