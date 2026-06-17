# Ovation Budget Platform — Demo Mockup

**For:** Leadership review · **Prepared by:** Edgar M. · **Status:** Clickable visual mockup (no backend)

---

## How to open it

Double-click **`index.html`** — it opens in any browser (Chrome/Edge). No install, no internet, no login required. Click **Sign in with Microsoft** to enter the demo.

> It is a single self-contained HTML file, the same approach as the manager's West Henderson prototype, so it is easy to email and open anywhere.

---

## 1. What this is (and is not)

This is a **clickable mockup** — a realistic, on-brand walkthrough of what the **Ovation Budget Platform** will look and feel like. Its job is to make the 8-week plan concrete so leadership can react to *screens*, not paragraphs.

- ✅ It **is**: the look, the navigation, the screen-by-screen flow, the brand, the story.
- ❌ It is **not**: a working application. Nothing saves, there is no database, the numbers are illustrative, and there is no real login.

Think of it as the architectural rendering — it shows the building before we pour concrete.

---

## 2. The purpose — why we're building this

Ovation budgets construction projects in **scattered Excel workbooks** today. That causes:

- Version conflicts when multiple people edit the same file
- No audit trail (who changed what, when)
- Manual, error-prone copying between budget levels (L0 → L1 → L2 → L3)
- Painful bid leveling (comparing subcontractor proposals by hand)
- No real-time budget visibility for leadership

The platform replaces that with **one centralized, multi-user web app** that tracks budgets across the four Ovation budget levels, levels bids, calculates markups, runs an approval workflow, and exports stakeholder-ready reports.

**Goal:** a **demo-ready app in 8 weeks**, then a ~6-month production rollout.

---

## 3. What's in the mockup (screen by screen)

| Screen | What it shows |
|---|---|
| **Sign-in** | Microsoft (Azure AD) sign-on — mocked to enter the demo |
| **Role switcher** | Top-bar selector (Estimator / Manager / Admin / Viewer) that **actually changes what you can do** — Viewer is read-only, only a Manager can approve/reject |
| **Notifications** | Live bell + dropdown with the real notification types (BudgetSubmitted, TradeAwarded, FileParsed, BudgetApproved) |
| **Projects dashboard** | All projects in one place, with budget level, workflow status, and committed-budget bars |
| **Project workspace** | Left sidebar that **gates features by budget level** (Trades, Proposal L3 & Significant Changes only appear at L3) |
| **Overview** | Per-project KPIs, **proposal-coverage** meter, and the L0→L3 version history with accuracy bands |
| **Master Budget** | Divisions → line items, L2 locked baseline vs. selected L3 bids, with variance |
| **Proposal L3** | The **editable working draft** of recommended adjustments (two-track: working vs. committed) |
| **Trades & Bid Leveling** | Trade list → **per-trade leveling Summary Sheet**: scope rows × bidder columns, winner highlighted, historical per-unit benchmark |
| **Markups** | All **7 markup kinds** (GR & Bid Risk computed; Bonds, GL Insurance, Contingency, Fee, Overhead editable) |
| **File Import** | Drag-and-drop Excel/CSV with a **simulated parse progress bar** and the column-mapping step |
| **Takeoffs** | **L2-vs-L3 side-by-side** quantities/unit-costs with live variance (editable L3 units) |
| **Benchmark** | West Henderson vs. comparable Ovation projects (Bruner, South Nellis, Torrey Pines, Decatur, Pebble) per unit |
| **Significant Changes** | Auto-surfaces every line that moved more than a **$50k threshold**, with a rationale note per line |
| **Variance** | L2-vs-L3 by-division bar chart for the leadership read |
| **Approval & Lock** | Full state machine (Draft → Submitted → Approved/Locked, or Rejected → new revision), include-checklist, live SHA-256 seal, **working signature pad**, certificate |

Seed projects in the mockup: **West Henderson Apartments (L3, Submitted for approval)** and **Robindale 215 (L2, Draft)** — the same two we'll use for the real demo.

> **Try the workflow live:** open West Henderson → Approval & Lock. As an *Estimator* you can only **Submit**. Switch the top-bar role to *Manager* and the **Approve & Lock** / **Reject** buttons appear (approve requires signing the pad; reject spins up the next revision, e.g. L3.1 → L3.2).

---

## 4. What we were missing (and added/decided)

The product docs were reviewed against the manager's prototype. The mockup folds in the **decisions that closed the biggest gaps**:

| Was missing / unclear | What we resolved for the mockup & plan |
|---|---|
| Whether this was one project or a platform | Mockup shows the **multi-project shell** — the prototype was West Henderson only |
| Persistence direction | **Azure SQL** for structured data, **Azure Blob Storage** for files/exports/approval packages |
| Bid selection only at trade level | Mockup shows the **trade leveling Summary Sheet** (scope × bidders, winner highlighted, historical benchmark) — the prototype's signature feature |
| Markups: 5 vs 7 | Shows all **7 markup kinds** — GR (01) & Bid Risk (BR) flagged *computed*; the 5 leadership-facing rates are editable |
| File import unspecified | Mockup makes the **upload → parse progress → auto-map → confirm** flow tangible |
| Approval was thin | Full **state machine** (Draft → Submitted → Approved/Locked / Rejected→new revision) with checklist, SHA-256 seal, working signature pad, certificate |
| Roles were just labels | Role switcher is **functional** — Viewer read-only, only Manager/Admin can approve/reject, Estimator submits |
| Budget-level gating | Sidebar visibly **locks features that don't apply** at a project's current level (Robindale L2 hides Trades / Proposal L3 / Significant Changes) |
| No leadership analytics | Added **Benchmark** (vs comparable projects), **Significant Changes** ($50k threshold), **Takeoffs** (L2 vs L3), **proposal coverage** |

Full detail lives in `../ovation-platform-docs/product/manager-alignment-review.md`.

---

## 5. Technologies we'll use (real build)

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, TanStack Table + Query, Recharts |
| **Backend** | .NET 8 Web API (C#), Entity Framework Core 8, SignalR (live sync), ClosedXML + CsvHelper (file parsing) |
| **Database** | **Azure SQL** (structured budget data) + **Azure Blob Storage** (uploads, exports, approval PDFs) |
| **Auth** | Azure AD single sign-on (Ovation M365 tenant), role-based access |
| **Hosting** | Azure |

The mockup itself is plain HTML/CSS/JS so it stays easy to share — none of the above is wired up yet.

---

## 6. The 8-week build plan

| Weeks | Focus | Outcome |
|---|---|---|
| **1–2** | Foundation | Azure-hosted Next.js + .NET 8 scaffold, Azure AD login, data model, project list, seed both projects |
| **3–4** | Editing & import | Editable budget tables, bid selection, **Excel/CSV import + column mapping**, summary cards |
| **5–6** | Approval & export | Submit → approve/reject → **lock**, in-app + email notifications, Excel export, variance chart |
| **7–8** | Polish & demo | Brand styling, bug fixes, seed-data validation, 20-minute demo script + dry run |

Each mockup screen maps directly to a week, so the demo we present then is the demo we're promising now.

---

## 7. Scope: what we WILL and will NOT do in 8 weeks

This is the most important slide for expectations. **8 weeks buys a convincing, end-to-end demo on real Azure infrastructure — not a hardened production system.**

### ✅ In scope for the 8-week demo
- Two real seed projects (West Henderson L3, Robindale L2)
- Budget editing, bid leveling, and the bid picker
- Excel/CSV import with auto + manual column mapping
- Markup calculations and budget summary cards
- Approval workflow with lock state + notifications
- Excel export and a budget-variance chart
- Azure AD login with Estimator / Manager / Admin / Viewer roles

### ⏳ Intentionally deferred (time-boxed, not forgotten)
> We are cutting these *on purpose* to protect the 8-week date — they are Phase-2 / production-hardening items, not surprises.

- **Hardened auth & security** — Azure AD login works in the demo, but full security review, granular permissions, penetration testing, and SSO edge cases come in production. *(If Azure AD setup is delayed, we use a temporary local login and switch over — the demo never blocks on it.)*
- **Real-time multi-user editing** — the architecture (SignalR) supports it; full live collaboration with conflict resolution is post-demo.
- **Full file-parser coverage** — we handle the common Ovation file formats first; rare/legacy layouts fall back to manual mapping.
- **Accounting / GL, invoices, payments** — out of scope (this is a budgeting tool, not an accounting system).
- **Subcontractor portal** — subs don't log in; Ovation staff upload their files.
- **All historical projects** — Phase 2/3; the demo proves the workflow on two projects.
- **Mobile / tablet optimization** — desktop-first for the demo.

### ⚠️ Things to watch (risks)
- **Azure AD access** must be available early, or auth slips → mitigation: temporary local login.
- **File-import edge cases** can eat time → mitigation: prioritize common formats, manual mapping for the rest.
- **Scope creep** is the #1 threat to the date → the 8-week plan is the boundary; new asks go to Phase 2.
- **Seed data quality** drives the demo → we prep real + synthetic data up front.

---

## 8. Bottom line for the presentation

> The prototype proved the *idea*. This mockup proves the *product*. The 8-week plan turns it into a working, Azure-hosted demo on two real projects — with auth and production hardening deliberately scoped to follow.

**Files in this folder**
- `index.html` — the clickable mockup (open this)
- `README.md` — this document
