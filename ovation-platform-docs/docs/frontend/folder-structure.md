# Frontend Folder Structure

**Framework:** Next.js 14+ (App Router)
**Language:** TypeScript
**UI:** Tailwind CSS + shadcn/ui
**State:** React Query (server state) + Zustand (UI state)
**Forms:** React Hook Form + Zod

---

## Directory Layout

```
src/
├── app/
│   ├── layout.tsx                          # Root layout (auth wrapper, nav)
│   ├── page.tsx                            # Redirect to /projects
│   │
│   ├── (auth)/
│   │   └── login/
│   │       └── page.tsx                    # Azure AD sign-in page
│   │
│   └── projects/
│       ├── page.tsx                        # Project list / dashboard home
│       ├── new/
│       │   └── page.tsx                    # Create new project form
│       │
│       └── [projectId]/
│           ├── layout.tsx                  # Project shell (sidebar, breadcrumb)
│           ├── page.tsx                    # Project dashboard (summary cards)
│           │
│           ├── budget-levels/
│           │   ├── page.tsx                # Budget level selector / history
│           │   └── new/
│           │       └── page.tsx            # Create new budget level
│           │
│           └── [budgetLevelId]/
│               ├── layout.tsx              # Budget level shell (tab nav)
│               ├── page.tsx                # Redirect to /master
│               │
│               ├── master/
│               │   └── page.tsx            # Master budget view (all divisions + line items)
│               │
│               ├── proposals/
│               │   └── page.tsx            # L3 proposal view (dual-track budget)
│               │
│               ├── trades/
│               │   ├── page.tsx            # Trade package list
│               │   └── [tradeId]/
│               │       └── page.tsx        # Trade detail / bid leveling / summary sheet
│               │
│               ├── takeoffs/
│               │   └── page.tsx            # Site work QTO table (L2 vs L3)
│               │
│               ├── benchmark/
│               │   └── page.tsx            # Per-unit cost benchmark comparison
│               │
│               └── approval/
│                   └── page.tsx            # Budget approval workflow + sign-off
│
├── components/
│   ├── budget/
│   │   ├── BudgetTable.tsx                 # Full master budget table (all divisions)
│   │   ├── DivisionSection.tsx             # Collapsible division group
│   │   ├── LineItemRow.tsx                 # Single line item row with inline edit
│   │   ├── LineItemForm.tsx                # Add/edit line item drawer
│   │   ├── MarkupSection.tsx               # Markup rows at bottom of budget
│   │   ├── BudgetSummaryBar.tsx            # Sticky footer: hard cost, total, $/unit, $/SF
│   │   └── BudgetStatusBadge.tsx           # Draft / Submitted / Approved / Locked pill
│   │
│   ├── trades/
│   │   ├── TradePackageList.tsx            # Trade package grid with status
│   │   ├── TradePackageCard.tsx            # Single trade card (bid count, variance)
│   │   ├── BidLevelingTable.tsx            # Side-by-side bidder comparison table
│   │   ├── ProposalCard.tsx                # Bidder proposal detail (scope breakdown)
│   │   ├── AwardTradeDialog.tsx            # Award trade confirmation modal
│   │   └── AddProposalDrawer.tsx           # Add a new bid form
│   │
│   ├── takeoffs/
│   │   ├── TakeoffTable.tsx                # L2 vs L3 quantity table
│   │   └── TakeoffRow.tsx                  # Editable row with variance highlight
│   │
│   ├── benchmark/
│   │   ├── BenchmarkChart.tsx              # Bar chart: this project vs comparables
│   │   └── BenchmarkTable.tsx              # Table version of benchmark data
│   │
│   ├── approval/
│   │   ├── ApprovalTimeline.tsx            # Draft → Submitted → Approved steps
│   │   ├── SignatureCanvas.tsx             # Digital signature pad (canvas)
│   │   ├── ApprovalSummaryCard.tsx         # Budget totals snapshot at approval
│   │   └── HashVerifier.tsx               # SHA-256 verification display
│   │
│   ├── markups/
│   │   ├── MarkupTable.tsx                 # 7-row markup configuration table
│   │   └── MarkupEditRow.tsx               # Inline edit for rate / mode / fixed amount
│   │
│   └── ui/                                 # shadcn/ui re-exports and overrides
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Table.tsx
│       ├── Badge.tsx
│       ├── Dialog.tsx
│       ├── Drawer.tsx
│       └── ...
│
├── lib/
│   ├── api/
│   │   ├── client.ts                       # Axios instance with auth interceptor
│   │   ├── projects.ts                     # Project CRUD functions
│   │   ├── budget-levels.ts               # BudgetLevel CRUD
│   │   ├── line-items.ts                   # Line item read/write
│   │   ├── markups.ts                      # Markup read/write
│   │   ├── trades.ts                       # Trade packages + proposals
│   │   ├── budget.ts                       # Summary, takeoffs, benchmark, export
│   │   └── approval.ts                     # Approval workflow
│   │
│   ├── hooks/
│   │   ├── useProject.ts                   # useQuery wrapper for project detail
│   │   ├── useBudgetLevel.ts              # useQuery for budget level
│   │   ├── useLineItems.ts                # useQuery + useMutation for line items
│   │   ├── useMarkups.ts                  # useQuery + useMutation for markups
│   │   ├── useTrades.ts                   # useQuery + useMutation for trade packages
│   │   ├── useBudgetSummary.ts            # useQuery for computed totals
│   │   └── useApproval.ts                 # useQuery + useMutation for approval
│   │
│   ├── types/
│   │   ├── project.ts                      # Project, UnitMix, Parking types
│   │   ├── budget-level.ts                 # BudgetLevel type
│   │   ├── line-item.ts                    # LineItem, SubJob, Category enums
│   │   ├── markup.ts                       # Markup, MarkupKind types
│   │   ├── trade.ts                        # TradePackage, Proposal, Bidder types
│   │   ├── budget.ts                       # BudgetSummary, DivisionSubtotal types
│   │   └── approval.ts                     # BudgetApproval type
│   │
│   └── utils/
│       ├── format-currency.ts              # Intl.NumberFormat wrapper for USD
│       ├── format-pct.ts                   # Percent formatting (0.05 → "5.00%")
│       ├── budget-level-gate.ts            # Feature availability by budget level
│       └── sha256.ts                       # Client-side SHA-256 for verification
│
└── middleware.ts                           # Azure AD auth guard — protect all /projects routes
```

---

## Key Patterns

### Feature Gating by Budget Level

The `budget-level-gate.ts` utility exports a `canAccess(level, feature)` function used by layout components to show/hide tabs:

```typescript
// lib/utils/budget-level-gate.ts
export const FEATURE_GATES: Record<Feature, MinLevel> = {
  'trades':     3,
  'proposals':  3,
  'takeoffs':   2,
  'benchmark':  2,
  'approval':   2,
  'soft-bids':  2,
}

export function canAccess(budgetLevel: number, feature: Feature): boolean {
  return budgetLevel >= FEATURE_GATES[feature]
}
```

### Inline Editing

Line items use an inline-edit pattern: click a cell to activate an input, blur/Enter to save. Saves fire `PUT /line-items/{id}` immediately (optimistic update via React Query).

### Budget Summary Footer

A sticky `BudgetSummaryBar` sits at the bottom of all budget views. It subscribes to the React Query cache for `/summary` and auto-updates when any mutation invalidates it.

### Locked State

When `BudgetLevel.Status = 'Locked'`, the frontend disables all edit inputs, hides add/delete buttons, and shows a "Locked" banner. The API enforces this server-side as well (409 on any mutation).

---

## Environment Variables

```env
NEXT_PUBLIC_API_URL=https://api.ovation-budget.com
NEXT_PUBLIC_AZURE_AD_CLIENT_ID=...
NEXT_PUBLIC_AZURE_AD_TENANT_ID=...
AZURE_AD_CLIENT_SECRET=...       # server-side only
NEXTAUTH_SECRET=...
NEXTAUTH_URL=https://budget.ovationco.com
```
