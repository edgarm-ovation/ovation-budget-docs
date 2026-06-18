"""
extract_bids.py — Authors the bid-leveling seed for West Henderson L3.

WHY THIS EXISTS
---------------
The bid-selection feature (group_key leveling) is the highest-value logic in the
platform, but NO bid data exists in the source workbook -- only anonymous
Low/2nd/3rd benchmark pricing ('Comparison to Other' sheet) and a handful of real
sub names mentioned in narrative ('What changed' sheet). So this seed is AUTHORED,
not extracted -- but anchored to that real material wherever possible.

WHAT IT PRODUCES (writes into ./data/)
  - budget_line_items.json   (UPDATED: group_key populated on L3 lines)
  - trade_packages.json       (NEW)
  - bidders.json              (NEW)
  - proposals.json            (NEW)
  - proposal_line_items.json  (NEW)

Re-runnable / idempotent: it re-reads budget_line_items.json and re-derives keys.

GROUP_KEY MODEL
  group_key = f"{trade_slug}-{cost_code}"  on each biddable L3 line.
  TradePackages.GroupKeys = JSON array of the distinct group_keys a trade covers.
  This matches the prototype example: framing -> ["06-1100-framing","06-1109-..."]
"""
import json, os

DATA = os.path.join(os.path.dirname(__file__), "data")
L3_LEVEL_ID = "west-henderson-l3"
PROJECT_ID = "west-henderson"

# ---------------------------------------------------------------------------
# 1. TRADE DEFINITIONS  (full coverage)
#    matcher(cost_code, division, desc_lower) -> True if line belongs to trade.
#    First matching trade in this ordered list wins.
#    benchmark = trade name in trade_benchmarks.json (for realistic proposal $),
#                or None -> proposals derived from the trade's budgeted total.
#    real_bidder = company name pulled from the workbook narrative, or None.
# ---------------------------------------------------------------------------
def cc_pre(*prefixes):
    return lambda cc, dv, d: cc is not None and cc.startswith(prefixes)

TRADES = [
    # slug,                 title,                    matcher,                                                          benchmark,                       real_bidder
    ("earthwork",           "Earthwork & Grading",    lambda cc,dv,d: dv in ("31","34") or cc=="02-3213",               None,                            None),
    ("slabs",               "Concrete - Slabs",       lambda cc,dv,d: cc_pre("03-31")(cc,dv,d) and cc!="03-3116",        "Slabs",                         "NRC Concrete"),
    ("lightweight-concrete","Lightweight Concrete",   lambda cc,dv,d: cc in ("03-3116","03-5001"),                       "Lightweight Concrete",          "NV Gypsum"),
    ("masonry",             "Masonry",                cc_pre("04-"),                                                     None,                            None),
    ("structural-steel",    "Structural Steel",       cc_pre("05-12"),                                                   None,                            None),
    ("ornamental-iron",     "Ornamental Iron",        lambda cc,dv,d: dv=="05" and not (cc or "").startswith("05-12"),   None,                            None),
    ("framing",             "Framing",                cc_pre("06-11"),                                                   "Framing",                       "Gilmore Construction"),
    ("finish-carpentry",    "Finish Carpentry",       cc_pre("06-2","06-4"),                                             "Finish Carpentry - Units",      None),
    ("insulation",          "Insulation",             cc_pre("07-21"),                                                   "Insulation",                    None),
    ("roofing",             "Roofing",                lambda cc,dv,d: dv=="07" and not (cc or "").startswith("07-21"),   "Roofing",                       None),
    ("doors-windows",       "Doors, Windows & Glazing",cc_pre("08-"),                                                    "Windows and Sliding Glass Doors",None),
    ("stucco",              "Stucco",                 cc_pre("09-24"),                                                   "Stucco",                        None),
    ("drywall",             "Drywall",                cc_pre("09-29"),                                                   "Drywall",                       None),
    ("tile",                "Tile",                   cc_pre("09-30"),                                                   None,                            None),
    ("flooring",            "Flooring",               cc_pre("09-6"),                                                    "Flooring - Units",              None),
    ("painting",            "Painting & Wall Covering",cc_pre("09-9"),                                                   "Painting",                      None),
    ("final-clean",         "Final Clean",            cc_pre("09-01"),                                                   None,                            None),
    ("specialties",         "Specialties",            cc_pre("10-"),                                                     None,                            None),
    ("appliances",          "Appliances",             cc_pre("11-3"),                                                    "Appliances",                    None),
    ("cabinets",            "Cabinets",               cc_pre("12-35"),                                                   "Cabinets Units",                None),
    ("countertops",         "Countertops",            cc_pre("12-36"),                                                   "Counter Tops Units",            None),
    ("window-coverings",    "Window Coverings",       cc_pre("12-21"),                                                   None,                            None),
    ("pools-spas",          "Pools & Spas",           lambda cc,dv,d: cc_pre("13-11")(cc,dv,d) or cc=="13-3402",         "Pools and Spas",                None),
    ("carports",            "Carports",               lambda cc,dv,d: cc=="13-3401",                                     None,                            None),
    ("elevator",            "Elevator",               cc_pre("14-"),                                                     None,                            "Otis Elevator"),
    ("fire-sprinkler",      "Fire Sprinkler",         cc_pre("21-"),                                                     "Sprinkler System",              None),
    ("plumbing",            "Plumbing",               cc_pre("22-"),                                                     "Plumbing",                      None),
    ("hvac",                "HVAC",                   cc_pre("23-"),                                                     "HVAC Standard",                 None),
    ("electrical",          "Electrical",             cc_pre("26-"),                                                     "Electrical",                    "Sigma Electric"),
    ("fire-alarm",          "Fire Alarm",             cc_pre("28-46"),                                                   "Fire Alarm / Two Way Comm AOR", "NFP"),
    ("low-voltage",         "Low Voltage / DAS",      cc_pre("27-"),                                                     None,                            None),
    ("security",            "Security",               lambda cc,dv,d: dv=="28" and not (cc or "").startswith("28-46"),   None,                            None),
    ("site-flatwork",       "Site Concrete & Paving", lambda cc,dv,d: dv=="32" and (cc or "")[:4] in ("32-0","32-1"),    None,                            None),
    ("site-walls-iron",     "Site Walls & Fencing",   lambda cc,dv,d: dv=="32" and (cc or "").startswith("32-3"),        None,                            None),
    ("landscaping",         "Landscaping",            lambda cc,dv,d: dv=="32" and (cc or "").startswith("32-9"),        "Site Landscaping",              "Alpha Landscaping"),
    ("wet-utilities",       "Wet Utilities",          cc_pre("33-"),                                                     None,                            None),
    ("solar",               "Solar PV",               cc_pre("48-"),                                                     None,                            None),
    ("testing-inspection",  "Testing & Inspection",   cc_pre("49-"),                                                     None,                            None),
]
# FFE (division == 'FFE') and util lines with no cost code are intentionally
# left UNGROUPED (group_key = null): FFE is typically owner-supplied, not bid.

def classify(line):
    cc = line.get("cost_code")
    dv = line.get("division_code")
    d = (line.get("description") or "").lower()
    if dv == "FFE":
        return None
    for slug, title, match, *_ in TRADES:
        if match(cc, dv, d):
            return slug
    return None

# ---------------------------------------------------------------------------
# 2. LOAD
# ---------------------------------------------------------------------------
with open(os.path.join(DATA, "budget_line_items.json"), encoding="utf-8") as f:
    line_items = json.load(f)
with open(os.path.join(DATA, "trade_benchmarks.json"), encoding="utf-8") as f:
    benchmarks = {b["trade"]: b for b in json.load(f)}

l3 = [x for x in line_items if x["budget_level_id"] == L3_LEVEL_ID]

# ---------------------------------------------------------------------------
# 3. ASSIGN group_key to L3 lines  (group_key is L3-only per schema)
# ---------------------------------------------------------------------------
trade_lines = {slug: [] for slug, *_ in TRADES}
for ln in l3:
    slug = classify(ln)
    if slug is None:
        ln["group_key"] = None
        continue
    cc = ln.get("cost_code") or "misc"
    gk = f"{slug}-{cc}"
    ln["group_key"] = gk
    trade_lines[slug].append(ln)

# ---------------------------------------------------------------------------
# 4. BIDDERS  (real names anchored to the workbook + clear placeholders)
# ---------------------------------------------------------------------------
PLACEHOLDER_PREFIXES = ["Desert", "Mojave", "Silver State", "Red Rock", "Sunrise", "Valley"]
PLACEHOLDER_SUFFIX = ["LLC", "Inc.", "Co.", "Contractors"]
bidders = []
bidder_id_by = {}  # (slug, rank) -> bidder_id

def add_bidder(bid_id, company, real):
    bidders.append({
        "bidder_id": bid_id, "company_name": company,
        "contact_name": None, "email": None, "phone": None,
        "license_number": None, "is_active": True,
        "is_placeholder": (not real),
    })

for ti, (slug, title, match, benchmark, real) in enumerate(TRADES):
    for rank in range(3):  # Low / 2nd / 3rd  -> three bidders per trade
        if rank == 0 and real:
            bid_id, company = f"bidder-{slug}-1", real
            add_bidder(bid_id, company, True)
        else:
            pfx = PLACEHOLDER_PREFIXES[(ti + rank) % len(PLACEHOLDER_PREFIXES)]
            sfx = PLACEHOLDER_SUFFIX[(ti + rank) % len(PLACEHOLDER_SUFFIX)]
            bid_id, company = f"bidder-{slug}-{rank+1}", f"{pfx} {title} {sfx}"
            add_bidder(bid_id, company, False)
        bidder_id_by[(slug, rank)] = bid_id

# ---------------------------------------------------------------------------
# 5. TRADE PACKAGES + PROPOSALS + PROPOSAL LINE ITEMS
# ---------------------------------------------------------------------------
trade_packages, proposals, proposal_line_items = [], [], []

def r2(x):
    return round(float(x), 2)

for sort_order, (slug, title, match, benchmark, real) in enumerate(TRADES):
    lines = trade_lines[slug]
    group_keys = sorted({ln["group_key"] for ln in lines})
    budget_total = r2(sum(ln["line_total"] for ln in lines))

    # --- three bid amounts ---
    bm = benchmarks.get(benchmark) if benchmark else None
    if bm and bm.get("proposal_low") and bm.get("qty"):
        qty = bm["qty"]
        lo = bm.get("proposal_low"); s2 = bm.get("proposal_2nd"); s3 = bm.get("proposal_3rd")
        amts = [r2(lo * qty),
                r2((s2 or lo * 1.04) * qty),
                r2((s3 or lo * 1.10) * qty)]
        bid_source = f"benchmark:{benchmark}"
    else:
        base = budget_total if budget_total > 0 else 50000.0
        amts = [r2(base * 0.96), r2(base * 1.00), r2(base * 1.08)]
        bid_source = "derived-from-budget"

    # Low bid (rank 0) is the awarded/selected default.
    awarded_bidder = bidder_id_by[(slug, 0)]
    awarded_amount = amts[0]

    trade_packages.append({
        "trade_package_id": f"tp-wh-{slug}",
        "budget_level_id": L3_LEVEL_ID,
        "trade_key": slug,
        "title": title,
        "estimated_cost_l2": budget_total,         # L2 baseline stand-in
        "status": "Awarded",
        "awarded_bidder_id": awarded_bidder,
        "awarded_amount": awarded_amount,
        "group_keys": group_keys,                   # serialize to JSON string at load time
        "sort_order": sort_order,
        "notes": None if real is None else f"Awarded to real sub from workbook narrative ({real}).",
        "bid_source": bid_source,
    })

    for rank, amt in enumerate(amts):
        pid = f"prop-wh-{slug}-{rank+1}"
        selected = (rank == 0)
        proposals.append({
            "proposal_id": pid,
            "trade_package_id": f"tp-wh-{slug}",
            "budget_level_id": L3_LEVEL_ID,
            "bidder_id": bidder_id_by[(slug, rank)],
            "base_bid": amt,
            "leveled_bid": amt,
            "submitted_by": None,
            "revision_date": None,
            "status": "Awarded" if selected else "Submitted",
            "is_selected": selected,
            "awarded_amount": amt if selected else None,
            "notes": ["Low", "2nd", "3rd"][rank] + " bid",
        })
        # Proposal line items: only for the selected (awarded) bid -> the
        # allocation of the lump bid across the trade's budget lines.
        if selected and lines:
            denom = sum(ln["line_total"] for ln in lines) or len(lines)
            running = 0.0
            for i, ln in enumerate(lines):
                share = (ln["line_total"] / denom) if denom else (1.0 / len(lines))
                alloc = r2(amt * share)
                running += alloc
                proposal_line_items.append({
                    "proposal_line_item_id": f"pli-{pid}-{i+1:03d}",
                    "proposal_id": pid,
                    "label": ln.get("description") or ln.get("cost_code") or "Scope",
                    "section": "LINE ITEMS",
                    "amount": alloc,
                    "group_key": ln["group_key"],
                    "sort_order": i,
                    "notes": None,
                })
            # absorb rounding drift into last line so allocation == bid exactly
            if proposal_line_items and lines:
                drift = r2(amt - running)
                proposal_line_items[-1]["amount"] = r2(proposal_line_items[-1]["amount"] + drift)

# ---------------------------------------------------------------------------
# 6. VALIDATE (both directions of the join)
# ---------------------------------------------------------------------------
errors = []
all_pkg_keys = {gk for tp in trade_packages for gk in tp["group_keys"]}
line_keys = {ln["group_key"] for ln in l3 if ln["group_key"]}

orphan_pkg = all_pkg_keys - line_keys
if orphan_pkg:
    errors.append(f"{len(orphan_pkg)} package group_keys have no line: {sorted(orphan_pkg)[:5]}")
orphan_line = line_keys - all_pkg_keys
if orphan_line:
    errors.append(f"{len(orphan_line)} line group_keys have no package: {sorted(orphan_line)[:5]}")

# every selected proposal's allocation must sum to its bid (±$0.02)
alloc_by_prop = {}
for pli in proposal_line_items:
    alloc_by_prop[pli["proposal_id"]] = alloc_by_prop.get(pli["proposal_id"], 0) + pli["amount"]
for p in proposals:
    if p["is_selected"] and p["proposal_id"] in alloc_by_prop:
        diff = abs(alloc_by_prop[p["proposal_id"]] - p["base_bid"])
        if diff > 0.02:
            errors.append(f"{p['proposal_id']} allocation off by ${diff:.2f}")

# ---------------------------------------------------------------------------
# 7. WRITE
# ---------------------------------------------------------------------------
def dump(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

dump("budget_line_items.json", line_items)   # group_key now populated on L3
dump("trade_packages.json", trade_packages)
dump("bidders.json", bidders)
dump("proposals.json", proposals)
dump("proposal_line_items.json", proposal_line_items)

# ---------------------------------------------------------------------------
# 8. REPORT
# ---------------------------------------------------------------------------
grouped = sum(1 for ln in l3 if ln["group_key"])
print("=" * 64)
print("BID-LEVELING SEED  (West Henderson L3)")
print("=" * 64)
print(f"L3 lines:            {len(l3)}")
print(f"  tagged group_key:  {grouped}")
print(f"  left ungrouped:    {len(l3)-grouped}  (FFE / no-cost-code)")
print(f"Trade packages:      {len(trade_packages)}")
print(f"Distinct group_keys: {len(line_keys)}")
print(f"Bidders:             {len(bidders)}  ({sum(not b['is_placeholder'] for b in bidders)} real, "
      f"{sum(b['is_placeholder'] for b in bidders)} placeholder)")
print(f"Proposals:           {len(proposals)}  (3 per trade)")
print(f"Proposal line items: {len(proposal_line_items)}")
print(f"Awarded total (low): ${sum(tp['awarded_amount'] for tp in trade_packages):,.2f}")
print(f"Budgeted (grouped):  ${sum(ln['line_total'] for ln in l3 if ln['group_key']):,.2f}")
print("-" * 64)
print("VALIDATION:", "PASS" if not errors else "FAIL")
for e in errors:
    print("  -", e)
