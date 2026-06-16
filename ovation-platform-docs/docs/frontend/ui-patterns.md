# UI Patterns & Component Reference

Extracted directly from the West Henderson L3 HTML prototype (v94).
This file is the UI/UX source of truth for the app.

---

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar (260px fixed)  │  Main content (flex: 1, scrollable) │
│  ─────────────────────  │  ─────────────────────────────────  │
│  Brand / project name   │  page-header (title + actions)      │
│  Nav sections           │  .cards row (KPI pills)              │
│  Nav items w/ badges    │  .panel blocks                       │
│  Print button           │  tables / modals                     │
└──────────────────────────────────────────────────────────────┘
```

- Sidebar background: linear-gradient navy → navy-2 (`#0a2540` → `#0f3460`)
- Active nav item: teal left border + teal-tinted background
- Body background: `#ffffff` / `var(--bg)`

---

## Navigation Views (exact list from prototype)

| Route / View | Description |
|---|---|
| `dashboard` | KPI cards + hero rendering + totals summary |
| `renderings` | Grid of rendering images |
| `awarded` | Awarded trades list |
| `master` | Read-only L2 Master Budget (locked baseline) |
| `proposal-l3` | Editable Recommended Adj. + live markup recalc |
| `changes` | Summary of Significant Changes (threshold filter) |
| `approval` | SHA-256 Budget Approval & Lock + signature canvas |
| `benchmark` | Per-unit cost vs previous Ovation projects |
| `takeoff/{key}` | Site work takeoffs — L2 vs L3 side-by-side |
| `trade/{key}` | Individual trade proposal: bidders + summary sheet |

**Site Work Takeoffs** is a collapsible nav section, not a single view.
Clicking a takeoff nav item sets the active takeoff key.

---

## Card Component (`.card`)

Used in "KPI row" at top of every view. Variants:

| Class | Color meaning |
|---|---|
| `.card` (plain) | Neutral metric |
| `.card.hi-green` | Good / under budget |
| `.card.hi-red` | Over budget / alert |
| `.card.hi-blue` | Informational (L2 budget, counts) |
| `.card.hi-amber` | Warning / pending |

```html
<div class="card hi-blue">
  <div class="label">Level 2 Budget (Locked)</div>
  <div class="value">$35,222,376</div>
  <div class="sub">$185,381/unit · $184/GSF</div>
</div>
```

`.cards-tight` = 5-column grid with smaller value font (used on Takeoffs).

---

## Panel Component (`.panel`)

Every section is a panel:

```html
<div class="panel">
  <div class="panel-head">
    <h3>Divisions & Line Items</h3>
    <span class="muted">Click a division row to expand</span>
    <div class="summary-actions"><!-- action buttons --></div>
  </div>
  <div class="panel-body" style="overflow-x:auto">
    <table>...</table>
  </div>
</div>
```

---

## Master Budget Table Structure

```
Division row (clickable → expand/collapse)
├── Cost Code Group row (line item)
│   ├── Label (with "View N included items" link if grouped)
│   ├── Cost Code badge (Courier New, accent color)
│   ├── L2 Budget (locked)
│   ├── Selected Bid (clickable Bid Cell Button)
│   ├── Variance (Bid − L2)
│   ├── Recommended Adj. (read-only on Master, editable on Proposal tab)
│   └── Level 3 Budget
└── ... more groups
```

**Division row** is toggled by clicking anywhere on the row except inputs/buttons.
Expand state persists in `state.expandedDivs[]`.

**Markup divisions** (01, 55, 50, 51, 98, 99, BR) show "COMPUTED" pill and
their L3 value drives from the rate inputs in the Markup Controls panel above
the table — not from per-line adjustments.

---

## Bid Cell Button

The most distinctive UX element: **every Selected Bid cell in the Master Budget
and Proposal L3 Budget tables is a clickable button** that opens the Bid Picker modal.

```html
<button class="bid-cell-btn" onclick="openBidPicker('06-1100-framing')">
  $7,053,263
  <span class="prop-pill">PROPOSED</span>
  <span class="bid-edit-hint">▾</span>
</button>
```

Status pills inside bid cells:
- `.award-pill` — amber/yellow — "AWARDED"
- `.prop-pill` — blue — "PROPOSED"
- `.lowest-pill` — green — "lowest" (not selected yet)

---

## Bid Picker Modal

Opens on click of any Bid Cell Button. Contains:

1. **Status toggle** — "Proposed (not yet awarded)" | "Awarded"
2. **Pricing Tier toggle** (optional) — only for trades that publish pricing tiers
   (e.g. Framing: "Current Proposal" vs "Locked Pricing")
3. **Bidder list** — radio buttons showing company name + submitted by + revision date + amount
   - Selected bidder row gets `.sel` class (blue tinted background)
   - Amounts are **cost-code aware** — when a trade's Summary Sheet has `scopeHasCostCode: true`,
     the amount shown per bidder is the sub-amount for that specific cost code, not the total bid
4. **Reset to default** button
5. **Cancel / Apply** buttons

On Apply → updates `state.bidOverrides[groupKey]` → re-renders Master Budget.

---

## Markup Controls Panel

Appears at the top of the **Proposal L3 Budget** tab only.
Collapsible via the panel header click.

5 markup rows (in this order):
1. Sub Bonds (50)
2. GL Insurance (51) — supports fixed $ mode
3. Construction Contingency (55)
4. Contractor Fee (98)
5. Overhead (99)

Each row has:
- **Mode toggle**: `% rate` | `$ fixed`
- **Rate input** (active when mode = %)
- **$ Override input** (active when mode = fixed)
- **Computed L3 Amount** (read-only, recomputes live)

Each markup kind uses its own **base** (different exclusion sets):
- Bonds + Insurance: exclude OH(99), Fee(98), Bonds(50), GL(51)
- Contingency + Fee + Overhead: exclude GR(01), Contingency(55), Fee(98), OH(99)

---

## Summary Sheet Modal

Opens from:
- The ⭐ star button next to a bid amount in any table
- The "Summary Sheet" button in the trade award banner

Contains (per trade):
1. Historical benchmark table (project, year, company, per-UOM cost)
2. Scope table (line items × bidder columns)
   - Winner column gets `.winner-col` class (green tinted)
   - "Budget" column always first
   - Total Proposal row
   - Budget Variance row (colored: over/under)
   - Optional: Price per SF, Locked Pricing rows
3. Winner banner at top (green for awarded, blue for proposed)
4. Notes row at bottom

---

## Takeoff Tab

Two layouts depending on takeoff type:

**Standard** (`hasL3: true, hasSeparateL2L3: false`):
- Single table with L2 columns on left + L3 columns on right
- L3 Qty and Unit Cost are **editable inputs** (inline, amber background)
- Variance column shows L3 − L2 per row

**Split** (`hasSeparateL2L3: true`):
- Two side-by-side tables (L2 on left, L3 on right)
- L2 is read-only; L3 Qty + Unit Cost are editable
- Each row has a Comment input at the far right
- Plans Library panel below: L2 PDFs + L3 PDFs, opens in iframe modal

Section totals shown in amber-highlighted subtotal rows.

---

## Trade Tab Layout

```
page-header (Trade name + status pill + actions)
│
Award/Proposed banner (full-width, colored)
│
.cards (4 KPI: L2 Estimate, Lowest Bid, Bidder count, Lowest vs L2)
│
.panel "Bidder Summary" (table of all bidders)
│
.panel "Leveling Summary Sheet" (if summarySheets[tradeKey] exists)
│
.panel "Notes" (if trade.notes exist)
```

---

## Status Pills

| Component | HTML | Color |
|---|---|---|
| `.award-pill` | `<span class="award-pill">AWARDED</span>` | Amber bg, amber text |
| `.prop-pill` | `<span class="prop-pill">PROPOSED</span>` | Blue bg, blue text |
| `.lowest-pill` | `<span class="lowest-pill">lowest</span>` | Green bg, green text |

---

## Modals

All modals render into `<div id="modal-host">`. Patterns:

- **Image viewer** — full-size rendering with close button
- **Bid Picker** — described above
- **Summary Sheet** — trade leveling sheet
- **Group Details** — shows N included line items for a grouped cost code
- **Major Variances** — filtered list of bids with |variance| ≥ $100k
- **Plan Viewer** — `<iframe>` for PDF takeoff plans
- **Print Dialog** — checklist of sections to include

All modals close on Escape key or clicking outside.

---

## Significant Changes Tab

- Threshold filter input (default $50k, persists in state)
- Only shows lines where |Recommended Adj.| ≥ threshold
- Sorted by absolute dollar value desc
- Note/explanation input per row (persists in `state.changeNotes`)
- CSV export button
- "Clear adjustment" × button per row

---

## Budget Approval Tab

1. **Current Snapshot panel** — live SHA-256 hash + match badge vs last signature
2. **Include checklist** — 9 sections, user picks what gets hashed/locked
3. **Sign & Lock form**:
   - Signer dropdown (4 Ovation names with roles)
   - Date input
   - Signature canvas (draw with mouse or touch)
4. **Approval History table** — per-signing: name, date, sig image, hash, L3 total, action buttons
   - "Full Package" → generates complete printable PDF of the entire model
   - "Certificate" → generates certificate-only PDF
   - "Snapshot" → downloads the locked JSON snapshot

---

## Color System (CSS Variables)

```css
--bg: #ffffff
--panel: #ffffff
--panel2: #f4f6fa
--border: #e2e6ee
--text: #1a2236
--muted: #6b7585
--accent: #0066cc
--ok: #047857
--over: #b91c1c      /* cost OVER budget → red */
--under: #047857     /* cost UNDER budget → green */
--navy: #0a2540
--navy-2: #0f3460
--teal: #00c2a8
--blue: #0066cc
--hi-bg: #ecfdf5          /* green highlight bg */
--hi-border: #10b981
--hi-text: #065f46
--hi-blue-bg: #eff6ff
--hi-blue-border: #0066cc
--hi-blue-text: #1e3a8a
--hi-amber-bg: #fffbeb
--hi-amber-border: #f59e0b
--hi-amber-text: #92400e
--hi-red-bg: #fef2f2
--hi-red-border: #ef4444
--hi-red-text: #991b1b
--shadow: 0 1px 2px rgba(15,23,42,0.05), 0 4px 12px rgba(15,23,42,0.06)
```

**Variance coloring rule** (used everywhere):
- Bid > L2 → `.over` (red) — costs MORE than budgeted
- Bid < L2 → `.under` (green) — costs LESS than budgeted

---

## Group Key Concept (critical for implementation)

The `groupKey` is the fundamental unit of the bid-mapping system.

Multiple L2 line items can share one `groupKey` (e.g. all grading items map to
`31-MASS-GRADING`). The Master Budget table shows ONE row per group, aggregating
the L2 totals. The Selected Bid and Recommended Adj. are tracked at the group level.

`lineItemBidMap[groupKey]` → `{ tradeKey, amount?, status? }` or just `"tradeKey"`

When a user opens the Bid Picker for a group:
- The modal shows bidder amounts computed per cost code (not the full trade total)
- Uses `summarySheets[tradeKey].scope` rows where `row.groupKey === groupKey` to find the sub-amount
- If no row matches, falls back to the bidder's total leveled bid

---

## State Architecture (what persists locally)

```typescript
interface AppState {
  currentView: string;
  selectedTrade: string | null;
  selectedTakeoff: string | null;
  expandedDivs: string[];           // division codes currently expanded
  masterExpandAll: boolean;
  takeoffsExpanded: boolean;        // sidebar takeoffs section open/closed

  // Adjustments (two-track system)
  lineAdjustments: Record<string, number>;      // COMMITTED → Master Budget
  proposedAdjustments: Record<string, number>;  // WORKING DRAFT → Proposal L3 Budget tab

  // Bid selection
  bidOverrides: Record<string, {               // per groupKey
    bidderCompany: string;
    status: 'proposed' | 'awarded' | 'bid';
    tier?: string;
  }>;

  // Markup rates
  markups: Record<MarkupKind, {
    mode: 'pct' | 'fixed';
    pct: number;
    fixed: number | null;
  }>;
  markupPanelOpen: boolean;

  // Notes / change log
  changeNotes: Record<string, string>;          // per groupKey
  changeThreshold: number;                      // default 50000

  // Takeoffs
  takeoffOverrides: Record<string, {qty?: number; unitCost?: number}>;
  takeoffComments: Record<string, string>;

  // Benchmark
  benchmarkOverrides: Record<number, {uom?: string; u?: number}>;

  // Approval
  approvals: ApprovalRecord[];
  approvalIncludes: Record<string, boolean>;    // 9 section checkboxes

  // Trade-level edits
  tradeOverrides: Record<string, {
    edits: Record<number, {label?: string; values?: number[]}>;
    deletedIndices: number[];
    customLineItems: any[];
  }>;
}
```
