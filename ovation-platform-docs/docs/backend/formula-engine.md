# Formula Engine

The formula engine runs server-side in the .NET API. It is the single source of truth for all budget calculations. The frontend **never** computes totals — it only displays what the API returns.

---

## Inputs

- `BudgetLevelLineItems` — all line items with their amounts
- `Markups` — the 7 markup rows (mode + rate/fixedAmount) for this budget level
- `BudgetLevel.Level` — determines which amounts are used (takeoff vs proposal)

---

## Step 1: Resolve Effective Amount Per Line Item

For each `BudgetLevelLineItem`:

```
if Level == 3 AND ProposalAmount IS NOT NULL AND PreferredSource == 'proposal':
    effectiveAmount = ProposalAmount
else:
    effectiveAmount = TakeoffAmount  (= TakeoffQuantity × TakeoffUnitPrice × (1 + EscalationPct))
```

If `TakeoffAmount` is null, use 0.

---

## Step 2: Compute Division Subtotals

Group line items by `DivisionCode`. Sum `effectiveAmount` within each group.

Excluded from hard cost computation:
```
ExcludedCodes = { '01', 'BR', '50', '51', '55', '98', '99' }
```

---

## Step 3: Hard Cost

```
HardCost = SUM(effectiveAmount for all lineItems WHERE division NOT IN ExcludedCodes)
```

---

## Step 4: General Requirements (Division 01)

GR is stored as a markup row, NOT as a line item (the Div 01 line item subtotal is the GR calculation result).

```
GR_markup = Markups WHERE kind = 'general_requirements'

if GR_markup.Mode == 'pct':
    GeneralRequirements = HardCost × GR_markup.Rate
else:
    GeneralRequirements = GR_markup.FixedAmount
```

---

## Step 5: Markup Base

```
MarkupBase = HardCost + GeneralRequirements
```

All remaining markups apply to `MarkupBase`.

---

## Step 6: Remaining Markups

For each of: `bid_risk`, `contingency`, `bonds`, `insurance`, `overhead`, `fee`:

```
if markup.Mode == 'pct':
    markup.ComputedAmount = MarkupBase × markup.Rate
else:
    markup.ComputedAmount = markup.FixedAmount
```

---

## Step 7: Total Project Cost

```
TotalProjectCost = HardCost
                 + GeneralRequirements
                 + BidRisk
                 + Contingency
                 + SubBonds
                 + GlInsurance
                 + Overhead
                 + ContractorFee
```

---

## Step 8: Per-Unit and Per-SF Metrics

```
CostPerUnit    = TotalProjectCost / Project.TotalUnits
CostPerGrossSF = TotalProjectCost / Project.GrossSF

HardCostPerUnit    = HardCost / Project.TotalUnits
HardCostPerGrossSF = HardCost / Project.GrossSF
```

---

## L3 Proposal Coverage Metric

Shown on the L3 dashboard to indicate how much of the L2 budget has been replaced by actual proposals.

```
L2HardCost = SUM of L2 takeoff amounts (equivalent run of formula using L2 data)

CoveredByProposals = SUM(TakeoffAmount for lineItems WHERE ProposalAmount IS NOT NULL
                         AND GroupKey maps to an active TradePackage)

ProposalCoveragePct = CoveredByProposals / L2HardCost
```

Proposal coverage excludes: GR, markups, bid risk.

---

## Escalation

Escalation is applied per line item at the `BudgetLevelLineItems` level, not globally.

```
TakeoffAmount = TakeoffQuantity × TakeoffUnitPrice × (1 + EscalationPct)
```

EscalationPct is stored as a decimal: `0.05` = 5%, `0.10` = 10%.

---

## Rounding

- All intermediate values: 4 decimal places
- All stored and returned amounts: 2 decimal places (round half-up)
- Rates: stored at 6 decimal places (e.g., `0.060000`)
- Per-unit and per-SF metrics: 2 decimal places

---

## Trigger Points

The formula engine re-runs on every:
- `PUT /line-items/{id}` — any field change
- `POST /line-items/batch`
- `PUT /markups/{kind}`
- `PUT /takeoffs/{id}`
- `POST /trades/{id}/award`

The computed summary is **not** cached — it is recalculated on each call to `/summary`, `/markups`, or `/budget`. Redis caches the result for 30 seconds with a project+budgetLevel key; any write to those tables busts the cache.

---

## C# Service Interface

```csharp
public interface IBudgetFormulaService
{
    Task<BudgetSummaryDto> ComputeAsync(
        Guid budgetLevelId,
        CancellationToken ct = default);

    Task<MarkupPreviewDto> PreviewMarkupChangeAsync(
        Guid budgetLevelId,
        string kind,
        string mode,
        decimal? rate,
        decimal? fixedAmount,
        CancellationToken ct = default);
}
```

The service is injected into all API controllers that need totals. It never writes to the DB — only reads and computes.
