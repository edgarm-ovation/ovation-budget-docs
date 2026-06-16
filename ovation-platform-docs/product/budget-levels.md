# Budget Levels

There are four budget levels (L0–L3). Each represents a phase of design development with increasing precision and data sources. A project progresses through levels; each level is a separate `BudgetLevel` record linked to the same project.

---

## Level 0 — Pre-Schematic (Conceptual)

**Purpose:** ROM (Rough Order of Magnitude) estimate before any design work.
**Timing:** Project inception. Delivery: 1 week.
**Accuracy:** ±30–40%

**Data Sources:**
- Historical unit costs from prior Ovation projects
- Comparable project $/unit benchmarks only
- No site-specific data

**What's included:**
- Project header (units, site acres, rough GSF estimate)
- Division-level lump sums only (no line item detail)
- Default markup rates (GR 6%, Contingency 5%, Fee 6%, OH 2%)

**What's NOT available:**
- Comparable project source tracking
- Soft bids
- Trade packages / proposals
- Takeoffs
- Benchmark comparison
- Budget approval / lock

**Department tasks:**
- Development: provide unit count, target AMI %, site location
- Design: schematic site plan only
- Purchasing: n/a
- Finance: review for pro forma
- Entitlements: n/a

---

## Level 1 — Schematic Design

**Purpose:** Schematic-level budget based on site reports and design intent.
**Timing:** After schematic design package. Delivery: 1–2 weeks.
**Accuracy:** ±20–30%

**Data Sources:**
- Historical Ovation project costs (comparable projects)
- Geotech, Environmental, Survey reports available
- Architect schematic design package

**What's included:**
- All Level 0 content
- Line-item detail by CSI division
- Comparable project source per line item (Bruner, Torrey Pines, Decatur, etc.)
- Site-specific utility and earthwork estimates

**What's NOT available:**
- Soft bids
- Trade packages
- Takeoffs
- Benchmark comparison
- Budget approval

**Department tasks:**
- Development: confirm product type, unit mix
- Design: deliver schematic package
- Purchasing: identify long-lead items
- Finance: pro forma update
- Entitlements: confirm zoning, parking ratios

---

## Level 2 — Design Development

**Purpose:** Design development budget. Basis for GMP negotiation and equity raise.
**Timing:** ~90% CD set, 6–8 months to groundbreaking. Delivery: 2–3 weeks.
**Accuracy:** ±10–15%

**Data Sources:**
- Comparable project contracted costs (primary)
- Soft bids for key trades (windows, drywall, stucco, paint, finish carpentry)
- Quantity takeoffs for site work
- Allowances for scope TBD items

**What's included:**
- Full line item detail with cost code, category, sub-job, source
- Escalation percentage per line item
- Site work quantity takeoffs (L2 column)
- Markup configuration (all 7 markups editable)
- Benchmark comparison vs. comparables
- Budget approval / lock workflow

**Key line items with escalation:**
- Elevators: +5% escalation standard
- Unit Finish Carpentry: +10% escalation when lead time is extended
- HVAC, Electrical: escalation if bid date is 6+ months out

**Department tasks:**
- Development: confirm FF&E scope, finalize unit mix
- Design: deliver DD set, coordinate with Civil for site
- Purchasing: collect soft bids (windows, drywall, stucco, painting)
- Finance: finalize construction loan draws
- Entitlements: confirm all permits in progress

---

## Level 3 — Construction Documents (Bid-Based)

**Purpose:** Hard bid budget. Basis for contract award and construction start.
**Timing:** 100% permit set (or 100% CD set). Delivery: 3–4 weeks.
**Accuracy:** ±5%

**Data Sources (Dual-Track):**
- Actual subcontractor proposals (preferred) — from bid leveling
- Quantity takeoffs (backup) — used when no proposal exists
- Line items use whichever source gives better coverage

**What's included:**
- All Level 2 content
- Trade packages with 2–3 bidder proposals per trade
- Bid leveling / summary sheets per trade
- Proposal line item detail (scope breakdown per bidder)
- Trade award tracking (Awarded / Proposed / Open)
- L2 vs L3 side-by-side takeoff comparison
- Proposal coverage metric (% of L2 hard cost covered by actual bids)

**Coverage rule:**
A trade shows as "covered" once at least one proposal exists.
The budget uses `ProposalAmount` for line items mapped to awarded/proposed trades.
Remaining line items use `TakeoffAmount`.

**Department tasks:**
- Development: finalize scope inclusions (EV charging, solar, pool scope)
- Design: issue 100% bid set
- Purchasing: run formal bid process, collect at least 2 bids per trade
- Finance: confirm insurance and bond requirements with GC
- Entitlements: confirm building permit issued

---

## Cross-Level Unit of Measure Reference

Key line items change UOM as design precision increases:

| Line Item | L0 | L1 | L2 | L3 |
|-----------|----|----|----|----|
| Framing | $/Unit (hist.) | $/Unit (hist.) | SF (comparable) | LS (proposal) |
| Concrete Slab | $/Unit | $/Unit | SF | SF (takeoff) |
| Structural Steel | LS (similar proj.) | LS (similar proj.) | LS (similar proj.) | LBS |
| Roofing | $/Unit | SQ | SQ | Soft Bid |
| Elevators | $/stop | $/stop | $/stop (comparable) | LS (quote) |
| HVAC | $/Unit | $/Unit | $/Unit | LS (proposal) |
| Electrical | $/Unit | $/Unit | $/SF | LS (proposal) |
| Plumbing | $/Unit | $/Unit | $/Unit | LS (proposal) |
| Landscaping | $/Acre | $/Acre | LS (comparable) | LS (proposal) |
| Site Paving | $/SY | $/SY | SY (takeoff) | SY (takeoff) |
| Windows/Doors | $/Unit | $/Unit | LS (soft bid) | LS (proposal) |

---

## Source Hierarchy

When multiple sources exist, priority order for line item values:

1. **Awarded proposal** — actual contract amount (highest confidence)
2. **Submitted proposal** — formal bid (high confidence)
3. **Soft bid / Comparable** — informal quote or comparable project cost
4. **Budget / Takeoff** — quantity × unit price from takeoff
5. **Allowance** — estimate, scope TBD
6. **Historical** — per-unit cost from prior project, inflated if needed
7. **N/A** — not applicable to this project (enter $0)
