"""
Extract West Henderson Level 3 budget from the source Excel into schema-shaped
JSON seed files. Re-runnable: edit and re-run to regenerate /data.

Source of truth: Excel-Docs-Projects/Budget - West Henderson - Level 3.xlsx
Target schema:   docs/database/schema.md  (Schema A, canonical)

Self-validates: sum of line items + markups must equal the Excel grand total.
"""
import json, re, os

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
XLSX = os.path.join(ROOT, "Excel-Docs-Projects", "Budget - West Henderson - Level 3.xlsx")
OUT = os.path.join(HERE, "data")

PROJECT_ID = "west-henderson"
BUDGET_LEVEL_ID = "west-henderson-l3"
GRAND_TOTAL = 77376747.91649443  # Excel "Total Hard Costs" (incl. markups)

wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
L3 = wb["Level 3"]
rows = list(L3.iter_rows(min_row=1, max_row=520, values_only=True))


def cell(r, c):
    """1-based row, 0-based col -> value or None."""
    row = rows[r - 1]
    return row[c] if c < len(row) else None


def num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def s(v):
    return "" if v is None else str(v).strip()


# ---------------------------------------------------------------- project header
def date_str(v):
    return v.date().isoformat() if hasattr(v, "date") else s(v)


project = {
    "project_id": PROJECT_ID,
    "name": "West Henderson Apartments",
    "product_type": "Affordable",          # schema enum: Affordable|Senior|Workforce|MarketRate
    "status": "Active",                    # schema enum: Active|OnHold|Closed
    "current_level": 3,
    "city": "Henderson",
    "state": "NV",
    "floors_label": s(cell(7, 1)),         # "2 & 3 Levels" - free text, NOT the SMALLINT Floors col
    "buildings": int(num(cell(11, 1)) or 0),
    "timeline_months": int(num(cell(6, 1)) or 0),
    "livable_sf": num(cell(8, 1)),         # "Bldg. SF" 422,635
    "site_sf": num(cell(10, 1)),
    "site_acres": num(cell(9, 1)),
    "total_units": 390,
    "updated": date_str(cell(5, 1)),
    "total_cost": num(cell(14, 11)),       # 77,376,747.92
    "cost_per_unit": num(cell(15, 11)),
    "cost_per_gsf": num(cell(16, 11)),
}

# ----------------------------------------------------------------- unit mix
unit_mix = []
for r in range(3, 8):  # Studios .. 3Br-2Ba
    label = s(cell(r, 3))
    count = num(cell(r, 4))
    if label and count is not None:
        unit_mix.append({
            "project_id": PROJECT_ID,
            "unit_type": label,
            "count": int(count),
            "pct": round(num(cell(r, 5)) or 0, 6),
            "sort_order": r - 3,
        })

# ----------------------------------------------------------------- parking
park_labels = {
    10: "Garage", 11: "Covered", 12: "Open", 13: "Accessible",
    14: "PrivateGarages", 15: "TotalProvided", 16: "Ratio",
}
parking = {"project_id": PROJECT_ID}
for r, key in park_labels.items():
    parking[key] = num(cell(r, 4))

# ----------------------------------------------------------------- budget level
budget_level = {
    "budget_level_id": BUDGET_LEVEL_ID,
    "project_id": PROJECT_ID,
    "level": 3,
    "sub_level": 1,
    "display_name": "Level 3 — Construction Documents",
    "status": "Draft",
    "parent_budget_level_id": None,
}

# ----------------------------------------------------------------- line items
# Body line items live in rows 20..290 (divisions 01..49) and the FFE Extra
# block rows 294..307. A LINE ITEM has a cost code containing '-'. Rows whose
# cost code is a bare division number are SUBTOTAL rows (captured for validation).
DIV_NAMES = {}          # code -> name (from subtotal rows)
expected_div_total = {} # code -> subtotal value from Excel
line_items = []
seq = 0
current_div = None
MARKUP_DIVS = {"01", "50", "51", "55", "98", "99", "BR"}

def div_from_code(code):
    code = code.strip()
    m = re.match(r"^([0-9]{1,2}|FFE)", code)
    return m.group(1) if m else code

def emit(r, code, div, ffe):
    global seq
    seq += 1
    sub_col = num(cell(r, 10))
    line_items.append({
        "line_item_id": f"whl3-{seq:04d}",
        "budget_level_id": BUDGET_LEVEL_ID,
        "division_code": div,
        "cost_code": code or None,
        "description": s(cell(r, 0)),
        "category": s(cell(r, 2)) or None,     # S|A|RR|...
        "sub_job": s(cell(r, 3)) or None,
        "source": s(cell(r, 4)) or None,
        "uom": s(cell(r, 5)) or None,
        "qty": num(cell(r, 6)),
        "unit_cost": num(cell(r, 7)),
        "escalation": num(cell(r, 8)) or 0,
        "line_total": round(sub_col, 2) if sub_col is not None else 0,
        "notes": s(cell(r, 12)) or None,
        "is_ffe": ffe,
    })


def harvest(r_start, r_end, ffe=False):
    global current_div
    for r in range(r_start, r_end + 1):
        code = s(cell(r, 1))
        desc = s(cell(r, 0))
        total_col = num(cell(r, 11))   # division subtotal column
        sub_col = num(cell(r, 10))     # per-line amount column
        has_dash = "-" in code
        if has_dash:
            div = "FFE" if ffe else div_from_code(code)
            if not ffe:
                current_div = div
            emit(r, code, div, ffe)
            continue
        # no dash: subtotal row, GR/markup row, or a blank-code line item
        if code and total_col is not None and sub_col is None:
            DIV_NAMES.setdefault(code, desc)         # subtotal/divider row
            expected_div_total[code] = total_col
            continue
        if code in MARKUP_DIVS:                       # e.g. GR "01" handled as markup
            continue
        if sub_col is not None and desc and current_div:   # blank-code line item
            emit(r, code, "FFE" if ffe else current_div, ffe)

harvest(20, 290)        # divisions 01..49
harvest(294, 307, ffe=True)  # FFE Extra block

# ----------------------------------------------------------------- markups
# Mapped from the Excel's markup rows to the canonical 7-kind schema model.
# Excel quirks resolved here:
#   - Excel "56" = Overhead + Contractor Fee  -> split to canonical 99 / 98
#   - Excel "50" = Sub Bonds + GL Insurance   -> split to canonical 50 / 51
#   - Bid Risk real rate is 1% (0.01), NOT 2%
markups = [
    {"kind": "general_requirements", "label": "General Requirements",     "cost_code": "01", "mode": "pct",   "rate": 0.06,  "fixed_amount": None, "amount": round(num(cell(20, 10)), 2)},
    {"kind": "bid_risk",             "label": "Bid Risk",                  "cost_code": "BR", "mode": "pct",   "rate": 0.01,  "fixed_amount": None, "amount": round(num(cell(292, 10)), 2)},
    {"kind": "contingency",          "label": "Construction Contingency",  "cost_code": "55", "mode": "pct",   "rate": 0.05,  "fixed_amount": None, "amount": round(num(cell(309, 10)), 2)},
    {"kind": "bonds",                "label": "Sub Bonds",                 "cost_code": "50", "mode": "pct",   "rate": num(cell(311, 6)), "fixed_amount": None, "amount": round(num(cell(311, 10)), 2)},
    {"kind": "insurance",            "label": "GL Insurance",              "cost_code": "51", "mode": "fixed", "rate": None,  "fixed_amount": round(num(cell(313, 10)), 2), "amount": round(num(cell(313, 10)), 2)},
    {"kind": "overhead",             "label": "Overhead",                  "cost_code": "99", "mode": "pct",   "rate": 0.02,  "fixed_amount": None, "amount": round(num(cell(317, 10)), 2)},
    {"kind": "fee",                  "label": "Contractor Fee",            "cost_code": "98", "mode": "pct",   "rate": 0.06,  "fixed_amount": None, "amount": round(num(cell(318, 10)), 2)},
]
for i, m in enumerate(markups):
    m["budget_level_id"] = BUDGET_LEVEL_ID
    m["sort_order"] = i

# ----------------------------------------------------------------- divisions master
CANON_NAMES = {
    "50": "Sub Bonds", "51": "GL Insurance", "55": "Construction Contingency",
    "98": "Contractor Fee", "99": "Overhead", "BR": "Bid Risk",
}
codes = sorted({li["division_code"] for li in line_items} | MARKUP_DIVS,
               key=lambda c: (c.isdigit() is False, c.zfill(2)))
divisions = []
for i, code in enumerate(codes):
    name = DIV_NAMES.get(code) or CANON_NAMES.get(code) or ("FFE" if code == "FFE" else code)
    name = re.sub(r"\s+", " ", name).strip()
    divisions.append({
        "code": code,
        "name": name,
        "is_markup": code in MARKUP_DIVS,
        "is_ffe": code == "FFE",
        "sort_order": i,
    })

# ----------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)
def dump(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

dump("projects.json", [project])
dump("unit_mix.json", unit_mix)
dump("parking.json", [parking])
dump("budget_levels.json", [budget_level])
dump("divisions.json", divisions)
dump("budget_line_items.json", line_items)
dump("markups.json", markups)

# ----------------------------------------------------------------- validate
li_sum = sum(li["line_total"] for li in line_items)
mk_sum = sum(m["amount"] for m in markups)
grand = li_sum + mk_sum
print(f"line items     : {len(line_items)}")
print(f"  sum line_total: {li_sum:,.2f}")
print(f"markups        : {len(markups)}  sum {mk_sum:,.2f}")
print(f"computed grand : {grand:,.2f}")
print(f"excel grand    : {GRAND_TOTAL:,.2f}")
print(f"delta          : {grand - GRAND_TOTAL:,.2f}")

print("\nper-division check (computed vs excel subtotal):")
from collections import defaultdict
comp = defaultdict(float)
for li in line_items:
    comp[li["division_code"]] += li["line_total"]
for code in sorted(expected_div_total):
    exp = expected_div_total[code]
    got = comp.get(code, 0.0)
    flag = "" if abs(got - exp) < 1.0 else "  <-- MISMATCH"
    if code not in MARKUP_DIVS and code not in ("Bid Risk", "FFE Extra"):
        print(f"  div {code:>3}: excel {exp:>16,.2f}  computed {got:>16,.2f}{flag}")
