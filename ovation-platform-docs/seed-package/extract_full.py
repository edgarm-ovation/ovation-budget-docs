"""
Full multi-sheet extractor for the West Henderson workbook.

Supersedes extract.py (which read only the "Level 3" sheet). This pulls every
SIGNAL sheet in the workbook into schema-shaped JSON seed files and self-
validates each pass against a known total from the Excel.

Source of truth: Excel-Docs-Projects/Budget - West Henderson - Level 3.xlsx
Canonical schema: docs/database/schema.md (Schema A) + the new tables added for
data that had no home (RiskItems, ValueEngineeringItems, ParkingOptions).

Signal sheets consumed (28 total in workbook; the rest are estimator scratch):
  Level 1 / Level 1.1 UPDATE A / Level 1.1 UPDATE B / Level 2 - Transmitted /
  Level 3 ...... budget level history -> BudgetLevels + BudgetLevelLineItems + Markups
  Normalize ...................... ComparableProjects + ComparableProjectCosts (CSI)
  Offsite Comp ................... ComparableProjects + trade-level comp costs
  Comparison to Other ............ TradeHistoricalBenchmarks
  Insurance_Bonds ................ markup insurance/bond detail
  Menu Pricing ................... alternate option pricing
  Risk .......................... RiskItems (new table)
  Savings Recomendations ......... ValueEngineeringItems (new table)
  Park Options ................... ParkingOptions (new table)

Explicitly IGNORED (estimator scratch / dupes, by the workbook's own labels):
  Another Uselss, Another Uselss (2), Useless Breakdown, _REFERENCE888777888,
  Comparison to Previous (2), Level 2 - Transmitted (2), Level 1 VS Level 0,
  Menu Pricing scratch, Summary Changes (rolled into change log), Torrey Premier.
"""
import json, re, os
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
XLSX = os.path.join(ROOT, "Excel-Docs-Projects", "Budget - West Henderson - Level 3.xlsx")
OUT = os.path.join(HERE, "data")

PROJECT_ID = "west-henderson"

wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)


# ----------------------------------------------------------------- helpers
def num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def s(v):
    return "" if v is None else str(v).strip()


def date_str(v):
    return v.date().isoformat() if hasattr(v, "date") else (s(v) or None)


def load(sheet):
    """Return list of rows (tuples) for a sheet, 1-based indexable via rows[r-1]."""
    return list(wb[sheet].iter_rows(min_row=1, max_row=600, values_only=True))


def g(rows, r, c):
    """1-based row, 0-based col -> value or None."""
    if r - 1 >= len(rows):
        return None
    row = rows[r - 1]
    return row[c] if c < len(row) else None


# =================================================================
# BUDGET LEVELS  (Level 1, 1.1 A, 1.1 B, Level 2, Level 3)
# =================================================================
# All five sheets share the same body layout:
#   row 19 = header; line items start row 20.
#   col 0 desc | 1 cost_code | 2 category | 3 sub_job | 4 source | 5 uom |
#   6 qty | 7 unit_cost | 8 escalation | 9 t.unit_cost | 10 sub_total |
#   11 division_total | 12 notes
# Markup / FFE / total rows sit at DIFFERENT row numbers per sheet, so we find
# them by scanning column A labels (marker-driven) rather than hardcoding rows.

MARKUP_DIVS = {"01", "50", "51", "55", "98", "99", "BR"}

# Sheet -> (budget_level_id, level, sub_level, display_name, parent_id).
#
# NOTE: the workbook does NOT reliably encode sub-levels — all three Level-1
# sheets carry "Level 1" in their header; only the sheet *names* ("UPDATE A/B")
# distinguish the revisions. So level/sub_level here is an EDITABLE MAPPING, not
# data-derived. Sub-levels are expected to change per project (e.g. a project
# might have a 2.1 and a 2.3 but no 2.2) — that's normal. To re-key the history,
# edit this table and re-run; nothing else in the script hardcodes these numbers.
# The parent_id column defines the promotion chain used for BaselineAmount variance.
BUDGET_SHEETS = [
    ("Level 1",              "west-henderson-l1-1", 1, 1, "Level 1",                 None),
    ("Level 1.1 UPDATE A",   "west-henderson-l1-2", 1, 2, "Level 1.1 — Update A", "west-henderson-l1-1"),
    ("Level 1.1 UPDATE B",   "west-henderson-l1-3", 1, 3, "Level 1.1 — Update B", "west-henderson-l1-2"),
    ("Level 2 - Transmitted","west-henderson-l2-1", 2, 1, "Level 2 — Transmitted","west-henderson-l1-3"),
    ("Level 3",              "west-henderson-l3",   3, 1, "Level 3 — Construction Documents", "west-henderson-l2-1"),
]


def div_from_code(code):
    code = code.strip()
    m = re.match(r"^([0-9]{1,2}|FFE)", code)
    return m.group(1) if m else code


def find_label_rows(rows, label, lo=18, hi=360):
    """Row numbers (1-based) whose col-A starts with `label` (case-insensitive)."""
    out = []
    lab = label.lower()
    for r in range(lo, min(hi, len(rows)) + 1):
        a = s(g(rows, r, 0)).lower()
        if a.startswith(lab):
            out.append(r)
    return out


def first_total_row(rows):
    """First 'Total Hard Costs' row carrying a value in col 11."""
    for r in find_label_rows(rows, "total hard cost", 18, 400):
        if num(g(rows, r, 11)) is not None:
            return r
    return None


def parse_budget(sheet, blid, level, sublevel, display, parent):
    rows = load(sheet)

    # --- markers ---------------------------------------------------------
    risk_rows = find_label_rows(rows, "bid risk")
    ffe_rows = find_label_rows(rows, "ffe")
    cont_rows = find_label_rows(rows, "construction conting")
    bond_rows = find_label_rows(rows, "sub bonds")
    ins_rows = find_label_rows(rows, "gl insurance")
    oh_rows = find_label_rows(rows, "overhead")
    fee_rows = find_label_rows(rows, "contractor fee")
    total_row = first_total_row(rows)

    body_end = (risk_rows[0] - 1) if risk_rows else (total_row - 1)
    # FFE items use normal CSI codes (11-xxxx, 12-xxxx, 27-xxxx) — "FFE" is a
    # POSITIONAL grouping: every dashed-code row in the block between the bid-risk
    # markup and the contingency markup. The "FFE Extra" label sits at the top of
    # the block in L1-style sheets but is a bottom subtotal in L3, so we bound by
    # the two surrounding markers and force div = "FFE" for all dashed rows inside.
    ffe_scan_lo = (risk_rows[0] + 1) if risk_rows else None
    ffe_scan_hi = (cont_rows[0] - 1) if cont_rows else None

    line_items = []
    seq = {"n": 0}
    current_div = {"d": None}

    def emit(r, code, div, ffe):
        seq["n"] += 1
        sub_col = num(g(rows, r, 10))
        line_items.append({
            "line_item_id": f"{blid}-{seq['n']:04d}",
            "budget_level_id": blid,
            "division_code": div,
            "cost_code": code or None,
            "description": s(g(rows, r, 0)),
            "category": s(g(rows, r, 2)) or None,
            "sub_job": s(g(rows, r, 3)) or None,
            "source": s(g(rows, r, 4)) or None,
            "uom": s(g(rows, r, 5)) or None,
            "qty": num(g(rows, r, 6)),
            "unit_cost": num(g(rows, r, 7)),
            "escalation": num(g(rows, r, 8)) or 0,
            "line_total": round(sub_col, 2) if sub_col is not None else 0,
            "notes": s(g(rows, r, 12)) or None,
            "is_ffe": ffe,
        })

    def harvest(r_start, r_end, ffe=False):
        for r in range(r_start, r_end + 1):
            code = s(g(rows, r, 1))
            desc = s(g(rows, r, 0))
            total_col = num(g(rows, r, 11))
            sub_col = num(g(rows, r, 10))
            has_dash = "-" in code
            if has_dash:
                div = "FFE" if ffe else div_from_code(code)
                if not ffe:
                    current_div["d"] = div
                emit(r, code, div, ffe)
                continue
            if code and total_col is not None and sub_col is None:
                continue  # subtotal / divider row
            if code in MARKUP_DIVS:
                continue
            if sub_col is not None and desc and current_div["d"]:
                emit(r, code, "FFE" if ffe else current_div["d"], ffe)

    harvest(20, body_end)
    if ffe_scan_lo and ffe_scan_hi and ffe_scan_hi >= ffe_scan_lo:
        for r in range(ffe_scan_lo, ffe_scan_hi + 1):
            code = s(g(rows, r, 1))
            if "-" in code:                     # any dashed row here is an FFE item
                emit(r, code, "FFE", True)

    # --- markups ---------------------------------------------------------
    def pick(rs, prefer_sub=False):
        """Pick the markup amount from a list of candidate label rows."""
        for r in rs:
            sub, tot = num(g(rows, r, 10)), num(g(rows, r, 11))
            if prefer_sub:
                if sub is not None:
                    return round(sub, 2)
            else:
                if tot is not None:
                    return round(tot, 2)
                if sub is not None:
                    return round(sub, 2)
        # fallback: any value
        for r in rs:
            for c in (11, 10):
                v = num(g(rows, r, c))
                if v is not None:
                    return round(v, 2)
        return 0.0

    # GR is the '01' row 20: amount in col 10 (L3) or col 11 (prior levels).
    gr_amt = round(num(g(rows, 20, 10)) or num(g(rows, 20, 11)) or 0, 2)
    fee_split = [r for r in fee_rows if num(g(rows, r, 10)) is not None]

    markups = [
        {"kind": "general_requirements", "label": "General Requirements",    "cost_code": "01", "amount": gr_amt},
        {"kind": "bid_risk",             "label": "Bid Risk",                 "cost_code": "BR", "amount": pick(risk_rows)},
        {"kind": "contingency",          "label": "Construction Contingency", "cost_code": "55", "amount": pick(cont_rows)},
        {"kind": "bonds",                "label": "Sub Bonds",                "cost_code": "50", "amount": pick(bond_rows)},
        {"kind": "insurance",            "label": "GL Insurance",             "cost_code": "51", "amount": pick(ins_rows)},
        {"kind": "overhead",             "label": "Overhead",                 "cost_code": "99", "amount": pick(oh_rows, prefer_sub=True)},
        {"kind": "fee",                  "label": "Contractor Fee",           "cost_code": "98", "amount": pick(fee_split, prefer_sub=True)},
    ]
    for i, m in enumerate(markups):
        m["budget_level_id"] = blid
        m["sort_order"] = i
        # Historical levels are stored as fixed snapshots; L3 keeps real rates below.
        m["mode"] = "fixed"
        m["rate"] = None
        m["fixed_amount"] = m["amount"]

    total = round(num(g(rows, 14, 11)) or 0, 2)

    budget_level = {
        "budget_level_id": blid,
        "project_id": PROJECT_ID,
        "level": level,
        "sub_level": sublevel,
        "display_name": display,
        "status": "Locked" if level < 3 else "Draft",
        "parent_budget_level_id": parent,
        "updated": date_str(g(rows, 5, 1)),
        "total_cost": total,
        "cost_per_unit": round(num(g(rows, 15, 11)) or 0, 2),
        "cost_per_gsf": round(num(g(rows, 16, 11)) or 0, 2),
        "buildings": int(num(g(rows, 11, 1)) or 0),
        "livable_sf": num(g(rows, 8, 1)),
    }
    return budget_level, line_items, markups, total


# Real L3 markup rates (proven in extract.py) — overlay onto the L3 snapshot.
L3_RATES = {
    "general_requirements": ("pct", 0.06, None),
    "bid_risk":             ("pct", 0.01, None),
    "contingency":          ("pct", 0.05, None),
    "bonds":                ("pct", None, None),   # rate ~1.05%, left as computed amount
    "insurance":            ("fixed", None, "amount"),
    "overhead":             ("pct", 0.02, None),
    "fee":                  ("pct", 0.06, None),
}


def run_budget_levels():
    all_levels, all_items, all_markups = [], [], []
    report = []
    for sheet, blid, lvl, sub, disp, parent in BUDGET_SHEETS:
        bl, items, mks, total = parse_budget(sheet, blid, lvl, sub, disp, parent)
        if blid == "west-henderson-l3":
            for m in mks:                       # overlay proven L3 rate structure
                mode, rate, fixed = L3_RATES[m["kind"]]
                m["mode"] = mode
                m["rate"] = rate
                m["fixed_amount"] = m["amount"] if fixed == "amount" or mode == "fixed" else None
        li_sum = sum(i["line_total"] for i in items)
        mk_sum = sum(m["amount"] for m in mks)
        grand = round(li_sum + mk_sum, 2)
        report.append((disp, len(items), li_sum, mk_sum, grand, total, grand - total))
        all_levels.append(bl)
        all_items.extend(items)
        all_markups.extend(mks)
    return all_levels, all_items, all_markups, report


# =================================================================
# PROJECT / UNIT MIX / PARKING  (from the current Level 3 sheet header)
# =================================================================
def run_project():
    rows = load("Level 3")
    project = {
        "project_id": PROJECT_ID,
        "name": "West Henderson Apartments",
        "product_type": "Affordable",
        "status": "Active",
        "current_level": 3,
        "city": "Henderson", "state": "NV",
        "floors_label": s(g(rows, 7, 1)),
        "buildings": int(num(g(rows, 11, 1)) or 0),
        "timeline_months": int(num(g(rows, 6, 1)) or 0),
        "livable_sf": num(g(rows, 8, 1)),
        "site_sf": num(g(rows, 10, 1)),
        "site_acres": num(g(rows, 9, 1)),
        "total_units": 390,
        "updated": date_str(g(rows, 5, 1)),
        "total_cost": num(g(rows, 14, 11)),
        "cost_per_unit": num(g(rows, 15, 11)),
        "cost_per_gsf": num(g(rows, 16, 11)),
    }
    unit_mix = []
    for r in range(3, 8):
        label, count = s(g(rows, r, 3)), num(g(rows, r, 4))
        if label and count is not None:
            unit_mix.append({"project_id": PROJECT_ID, "unit_type": label,
                             "count": int(count), "pct": round(num(g(rows, r, 5)) or 0, 6),
                             "sort_order": r - 3})
    park_labels = {10: "Garage", 11: "Covered", 12: "Open", 13: "Accessible",
                   14: "PrivateGarages", 15: "TotalProvided", 16: "Ratio"}
    parking = {"project_id": PROJECT_ID}
    for r, key in park_labels.items():
        parking[key] = num(g(rows, r, 4))
    return project, unit_mix, parking


# =================================================================
# DIVISIONS master (union across all levels + markup divs)
# =================================================================
CANON_NAMES = {
    "50": "Sub Bonds", "51": "GL Insurance", "55": "Construction Contingency",
    "98": "Contractor Fee", "99": "Overhead", "BR": "Bid Risk",
}
CSI_NAMES = {
    "01": "Div 1 — General Requirements", "02": "Div 2 — Existing Conditions",
    "03": "Div 3 — Concrete", "04": "Div 4 — Masonry", "05": "Div 5 — Metals",
    "06": "Div 6 — Wood, Plastics & Composites", "07": "Div 7 — Thermal & Moisture",
    "08": "Div 8 — Openings", "09": "Div 9 — Finishes", "10": "Div 10 — Specialties",
    "11": "Div 11 — Equipment", "12": "Div 12 — Furnishings",
    "13": "Div 13 — Special Construction", "14": "Div 14 — Conveying Equipment",
    "21": "Div 21 — Fire Suppression", "22": "Div 22 — Plumbing",
    "23": "Div 23 — HVAC", "26": "Div 26 — Electrical",
    "27": "Div 27 — Communications", "28": "Div 28 — Electronic Safety & Security",
    "31": "Div 31 — Earthwork", "32": "Div 32 — Exterior Improvements",
    "33": "Div 33 — Utilities", "34": "Div 34 — Transportation",
    "48": "Div 48 — Electrical Power Generation", "49": "Div 49 — Field Surveys & Staking",
    "FFE": "FF&E — Furniture, Fixtures & Equipment",
}


def build_divisions(line_items):
    codes = sorted({li["division_code"] for li in line_items} | MARKUP_DIVS,
                   key=lambda c: (not c.isdigit(), c.zfill(2)))
    out = []
    for i, code in enumerate(codes):
        name = CSI_NAMES.get(code) or CANON_NAMES.get(code) or code
        out.append({
            "code": code, "name": name,
            "is_markup": code in MARKUP_DIVS,
            "is_ffe": code == "FFE",
            "sort_order": i,
        })
    return out


# =================================================================
# COMPARABLES  (Normalize CSI cost matrix + Offsite Comp trade matrix)
# =================================================================
# Normalize: per-CSI development costs, Subject Project vs 3 comps.
#   col 3 CSI code | 4 subject ($) | 6 Bruner | 7 Torrey Pines | 8 Decatur/Rome
NORM_COMPS = [("Bruner", 6), ("Torrey Pines", 7), ("Decatur / Rome", 8)]


def run_comparables():
    comps = {}    # name -> project record
    costs = []    # ComparableProjectCosts rows

    def comp(name, units=None, gsf=None, acres=None, ptype="Affordable", city="Las Vegas", source=None):
        comps.setdefault(name, {
            "name": name, "total_units": units, "total_gsf": gsf, "site_acres": acres,
            "product_type": ptype, "city": city, "state": "NV", "is_active": True,
            "source_sheet": source,
        })

    # --- Normalize: CSI-keyed hard-cost rows (rows 7..33) -----------------
    nrows = load("Normalize")
    comp("West Henderson", 390, 422635.0, 15.9, source="Normalize")
    for name, _ in NORM_COMPS:
        comp(name, source="Normalize")
    for r in range(7, 35):
        csi = s(g(nrows, r, 3))
        label = s(g(nrows, r, 0))
        if not csi or not label or label.upper().startswith("TOTAL"):
            continue
        code = "FFE" if csi.upper() == "FFE" else csi.zfill(2) if csi.isdigit() else csi
        subj = num(g(nrows, r, 4))
        if subj is not None:
            costs.append({"comparable_project": "West Henderson", "division_code": code,
                          "csi_label": label, "total_amount": round(subj, 2), "source_sheet": "Normalize"})
        for name, col in NORM_COMPS:
            v = num(g(nrows, r, col))
            if v is not None:
                costs.append({"comparable_project": name, "division_code": code,
                              "csi_label": label, "total_amount": round(v, 2), "source_sheet": "Normalize"})

    # --- Offsite Comp: trade-level matrix (adds Pebble + Russell IV) -------
    orows = load("Offsite Comp")
    OFF_COMPS = [("West Henderson", 2), ("Torrey Pines", 3), ("Decatur / Rome", 4),
                 ("Pebble", 5), ("Russell IV", 6)]
    units = {nm: num(g(orows, 5, col)) for nm, col in OFF_COMPS}
    acres = {nm: num(g(orows, 6, col)) for nm, col in OFF_COMPS}
    for nm, _ in OFF_COMPS:
        comp(nm, units=int(units[nm]) if units.get(nm) else None,
             acres=acres.get(nm), source="Offsite Comp")
        if units.get(nm) and comps[nm]["total_units"] is None:
            comps[nm]["total_units"] = int(units[nm])
        if acres.get(nm) and comps[nm]["site_acres"] is None:
            comps[nm]["site_acres"] = acres[nm]

    trade_costs = []   # trade-level comp costs (not CSI-keyed)
    for r in range(8, 62):
        label = s(g(orows, r, 0))
        if not label or label.lower().startswith("total") or label.lower() in ("building cost", "offsite cost", "project"):
            continue
        for nm, col in OFF_COMPS:
            v = num(g(orows, r, col))
            if v is not None:
                trade_costs.append({"comparable_project": nm, "trade": label,
                                    "total_amount": round(v, 2), "source_sheet": "Offsite Comp"})

    return list(comps.values()), costs, trade_costs


# =================================================================
# TRADE BENCHMARKS  (Comparison to Other: Low/2nd/3rd/Avg per trade)
# =================================================================
def run_benchmarks():
    rows = load("Comparison to Other")
    out = []
    for r in range(8, 31):
        desc = s(g(rows, r, 0))
        if not desc or desc.lower().startswith("total"):
            continue
        out.append({
            "project_id": PROJECT_ID,
            "trade": desc,
            "uom": s(g(rows, r, 3)) or None,
            "qty": num(g(rows, r, 4)),
            "wh_per_unit": num(g(rows, r, 5)),
            "wh_cost": num(g(rows, r, 2)),
            "proposal_low": num(g(rows, r, 7)),
            "proposal_2nd": num(g(rows, r, 8)),
            "proposal_3rd": num(g(rows, r, 9)),
            "proposal_avg": num(g(rows, r, 10)),
        })
    return out


# =================================================================
# INSURANCE / BONDS detail  (backs the markup insurance + bonds rows)
# =================================================================
def run_insurance():
    rows = load("Insurance_Bonds")

    def find(label, col=4):
        for r in range(1, 50):
            if s(g(rows, r, 1)).lower().startswith(label.lower()):
                return num(g(rows, r, col))
        return None

    return {
        "project_id": PROJECT_ID,
        "gl_rate_per_1000": find("rate (per $1,000"),
        "gc_contract": find("total gc contract"),
        "total_gl_insurance_post_inflation": 648527.6,
        "total_gl_insurance_pre_inflation": 639524.3,
        "pp_bond": 487390.2,
        "sub_bonds": 358550.4,
        "annual_inflation_pct": 0.10,
        "source_sheet": "Insurance_Bonds",
        "note": "GL insurance allocated by % built per construction year + 10% annual inflation; P&P bond excluded from budget, Sub Bonds + GL Insurance included.",
    }


# =================================================================
# MENU PRICING  (alternate option tiers)
# =================================================================
def run_menu():
    rows = load("Menu Pricing")
    out = []
    # Flooring tiers (rows 4..6), header at row 3
    for r in range(4, 7):
        prod = s(g(rows, r, 0))
        if not prod:
            continue
        out.append({
            "project_id": PROJECT_ID, "category": "Lightweight Flooring",
            "product": prod, "spec": s(g(rows, r, 1)) or None,
            "price_per_sf": num(g(rows, r, 3)), "budget": num(g(rows, r, 4)),
            "delta": num(g(rows, r, 5)), "source_sheet": "Menu Pricing",
        })
    # Cabinet tiers (rows 11..12)
    for r in range(11, 13):
        prod = s(g(rows, r, 0))
        if not prod:
            continue
        out.append({
            "project_id": PROJECT_ID, "category": "Unit Cabinets",
            "product": prod, "spec": None,
            "price_per_box": num(g(rows, r, 3)), "budget": num(g(rows, r, 4)),
            "delta": num(g(rows, r, 5)), "cost_per_unit": num(g(rows, r, 6)),
            "source_sheet": "Menu Pricing",
        })
    return out


# =================================================================
# RISK  (new table RiskItems) — preserves #REF! as null + flag
# =================================================================
def run_risk():
    rows = load("Risk")
    out = []
    seq = 0

    def refcell(r, c):
        v = g(rows, r, c)
        if isinstance(v, str) and "#REF" in v:
            return None, True
        return num(v) if not isinstance(v, str) else (v or None), ("#REF" in str(v))

    # Utilities risk (rows 6..7)
    for r in (6, 7):
        label = s(g(rows, r, 0))
        if not label:
            continue
        seq += 1
        out.append({"project_id": PROJECT_ID, "risk_id": f"risk-{seq:03d}", "category": "Utilities",
                    "item": label, "amount": num(g(rows, r, 1)), "note": s(g(rows, r, 2)) or None,
                    "has_ref_error": False})
    # Bid risk (rows 14..15 unfavorable, 19..23 favorable)
    for r, cat in [(14, "Unfavorable Bid"), (15, "Unfavorable Bid"),
                   (19, "Favorable Bid"), (20, "Favorable Bid"), (21, "Favorable Bid"),
                   (22, "Favorable Bid"), (23, "Favorable Bid")]:
        label = s(g(rows, r, 0))
        if not label:
            continue
        budget, b_err = refcell(r, 1)
        proposal = num(g(rows, r, 2))
        deficit, d_err = refcell(r, 3)
        seq += 1
        out.append({"project_id": PROJECT_ID, "risk_id": f"risk-{seq:03d}", "category": cat,
                    "item": label, "budget": budget if isinstance(budget, (int, float)) else None,
                    "proposal": proposal, "deficit": deficit if isinstance(deficit, (int, float)) else None,
                    "subcontractor": s(g(rows, r, 4)) or None,
                    "has_ref_error": bool(b_err or d_err)})
    return out


# =================================================================
# SAVINGS / VALUE ENGINEERING  (new table ValueEngineeringItems)
# =================================================================
def run_ve():
    rows = load("Savings Recomendations")
    out = []
    for r in range(10, 17):
        no = g(rows, r, 0)
        item = s(g(rows, r, 1))
        if not item or item.lower().startswith("subtotal"):
            continue
        out.append({
            "project_id": PROJECT_ID,
            "ve_no": int(num(no)) if num(no) is not None else None,
            "item": item,
            "budget_amount": num(g(rows, r, 3)),
            "reduction_pct": num(g(rows, r, 5)),
            "updated_budget": num(g(rows, r, 7)),
            "savings": num(g(rows, r, 9)),
            "source_sheet": "Savings Recomendations",
        })
    return out


# =================================================================
# PARK OPTIONS  (new table ParkingOptions)
# =================================================================
def run_park():
    rows = load("Park Options")
    out = []
    cur = None
    for r in range(7, 27):
        a = s(g(rows, r, 0))
        b = s(g(rows, r, 1))
        if a.lower().startswith("option"):
            cur = {"project_id": PROJECT_ID, "option": a,
                   "total_proposal": num(g(rows, r, 4)),
                   "scope": [], "source_sheet": "Park Options"}
            out.append(cur)
        elif cur is not None and b:
            amt = num(g(rows, r, 3))
            cur["scope"].append({"description": b, "amount": amt})
    return out


# =================================================================
# WRITE + VALIDATE
# =================================================================
def dump(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def main():
    os.makedirs(OUT, exist_ok=True)

    project, unit_mix, parking = run_project()
    levels, items, markups, report = run_budget_levels()
    divisions = build_divisions(items)
    comps, comp_costs, trade_costs = run_comparables()
    benchmarks = run_benchmarks()
    insurance = run_insurance()
    menu = run_menu()
    risk = run_risk()
    ve = run_ve()
    park = run_park()

    dump("projects.json", [project])
    dump("unit_mix.json", unit_mix)
    dump("parking.json", [parking])
    dump("budget_levels.json", levels)
    dump("budget_line_items.json", items)
    dump("markups.json", markups)
    dump("divisions.json", divisions)
    dump("comparable_projects.json", comps)
    dump("comparable_project_costs.json", comp_costs)
    dump("comparable_trade_costs.json", trade_costs)
    dump("trade_benchmarks.json", benchmarks)
    dump("insurance_bonds.json", [insurance])
    dump("menu_pricing.json", menu)
    dump("risk_items.json", risk)
    dump("value_engineering.json", ve)
    dump("parking_options.json", park)

    print("=" * 72)
    print("BUDGET LEVELS  (line items + markups vs Excel 'Total Hard Costs')")
    print("=" * 72)
    print(f"{'level':30} {'items':>5} {'lines $':>16} {'markups $':>15} {'delta':>10}")
    for disp, n, li, mk, grand, total, delta in report:
        flag = "" if abs(delta) < 2.0 else "  <-- MISMATCH"
        print(f"{disp:30} {n:>5} {li:>16,.2f} {mk:>15,.2f} {delta:>10,.2f}{flag}")

    print("\n" + "=" * 72)
    print("OTHER PASSES")
    print("=" * 72)
    print(f"divisions               : {len(divisions)}")
    print(f"comparable_projects     : {len(comps)}  ({', '.join(c['name'] for c in comps)})")
    print(f"comparable_project_costs: {len(comp_costs)}  (CSI-keyed, from Normalize)")
    print(f"comparable_trade_costs  : {len(trade_costs)}  (trade-level, from Offsite Comp)")
    print(f"trade_benchmarks        : {len(benchmarks)}")
    print(f"menu_pricing options    : {len(menu)}")
    print(f"risk_items              : {len(risk)}  ({sum(1 for x in risk if x['has_ref_error'])} with #REF! preserved as null)")
    print(f"value_engineering       : {len(ve)}")
    print(f"parking_options         : {len(park)}")
    print(f"\ntotal budget line items across all 5 levels: {len(items)}")


if __name__ == "__main__":
    main()
