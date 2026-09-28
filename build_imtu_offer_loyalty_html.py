"""Build the IMTU offer loyalty analysis page (IMTU_Offer_Loyalty_Analysis.html).

Question: do IMTU buyers purchase the same offer regularly, or do they jump between
offers from one purchase to the next?

Source: Amplitude BR app Prod (650506), event MTUOrderStatusSuccessScr. Every number
below is copied from a saved chart on dashboard fcw7gsdb; the chart id sits next to
each input so any figure can be re-run. Pulled 28 Sep 2026.

Method: step 1 = a buyer's 1st purchase since 30 Jun (Nth-time filter, 1-day lookback),
1 Jul to 28 Aug 2026; step 2 = their 2nd purchase within 30 days. Holding a property
constant across the two steps gives the share of buyers whose very next purchase kept it.
"""

from html import escape

AMP = "https://app.amplitude.com/analytics/BOSS"
DASH = f"{AMP}/dashboard/fcw7gsdb"
EVENT_URL = "https://app.amplitude.com/data/BOSS/650506/events/main/latest/MTUOrderStatusSuccessScr"
AUDIT_URL = "https://claude.ai/code/artifact/4658de01-5f22-408f-bfd7-f4cb63805cb5"
DCS_4011 = "https://idtjira.atlassian.net/browse/DCS-4011"


def chart(cid):
    return f"{AMP}/chart/{cid}"


def a(href, text):
    return f'<a href="{href}" target="_blank" rel="noopener">{text}</a>'


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


def num(x):
    return f"{x:,}"


# ---------------------------------------------------------------------------
# Inputs (Amplitude chart outputs)
# ---------------------------------------------------------------------------
# Consecutive pair funnels: users at step 1 and users converting, per segment.
SEGS = ["all", "est", "light", "new"]
N = dict(all=422042, est=201967, light=111171, new=108904)
FUN = {
    "any": (dict(all=237041, est=147750, light=48049, new=41242), "dmmwysk6"),
    "recip": (dict(all=71334, est=41727, light=15857, new=13750), "as44pz1v"),
    "recip_offer": (dict(all=50627, est=31073, light=10894, new=8660), "h5r3f3a0"),
    "offer": (dict(all=107522, est=67625, light=21887, new=18010), "g6r3txzr"),
    "recip_carrier": (dict(all=71302, est=41715, light=15851, new=13736), "ghgqoyi8"),
    "recip_carrier_amount": (dict(all=51171, est=31317, light=11063, new=8791), "5mo4xk68"),
    "recip_type": (dict(all=65465, est=39125, light=14346, new=11994), "s2n5xug7"),
    "per_recip": (dict(all=109736, est=71708, light=20099, new=17929), "p7xgzbsm"),
    "per_recip_offer": (dict(all=80120, est=54556, light=13979, new=11585), "tk7wnx2b"),
}
CARRIER_ALL, CARRIER_CID = 180877, "9j7xo0af"
COUNTRY_ALL, COUNTRY_CID = 225720, "ww8pz7gw"
REG = dict(n=302867, any=161719, recip=51674, recip_offer=39041, offer=76980)
REG_CID = dict(any="d69if8w3", recip="5yijrvol", recip_offer="meud2gwg", offer="0v5oa4mp")
W60 = dict(n=305197, any=232172, recip=79602, recip_offer=58223)
W60_CID = dict(any="h3siw1qb", recip="zsflzpb2", recip_offer="tiwder3b")

# Same-recipient next amount, given the previous amount (top 40 step-2 values).
AMOUNT_CID = {5: "v0m0hb27", 10: "rvsgy8i0", 15: "e3n8o63t", 20: "182uqmpr", 25: "ztd3udoq"}
AMOUNTS = {
    5: {5: 3679, 10: 255, 6: 190, 4: 115, 8: 75, 7: 71, 15: 56, 20: 55, 9: 31, 12: 27, 24: 20, 11.25: 19, 5.12: 19, 9.5: 15, 3.4: 14, 18: 12, 30: 10, 13: 9, 1.75: 8, 11: 6, 14: 6, 1.2: 6, 25: 6, 5.35: 5, 4.25: 5, 3.55: 5, 2: 5, 3: 5, 5.5: 5, 9.13: 5, 16: 4, 21: 4, 17: 3, 10.5: 3, 5.25: 2, 2.75: 2, 9.75: 2, 3.5: 2, 31: 2},
    10: {10: 12528, 20: 660, 15: 486, 8: 432, 5: 336, 6: 333, 12: 328, 25: 285, 7: 104, 9: 75, 13.2: 59, 6.6: 55, 4: 35, 14: 32, 30: 31, 11.25: 29, 6.35: 28, 11: 28, 5.1: 24, 4.5: 24, 5.25: 20, 12.75: 18, 13: 17, 5.12: 17, 21: 14, 19.1: 12, 4.15: 11, 9.13: 11, 4.25: 10, 23: 10, 24: 10, 18: 9, 2.85: 8, 16.5: 7, 16.25: 6, 2: 5, 1.55: 5, 40: 5, 19: 4},
    15: {15: 3008, 10: 523, 20: 290, 25: 237, 12: 225, 7: 125, 8: 54, 5: 38, 6: 38, 14: 27, 30: 23, 23: 11, 11: 7, 18: 4, 7.75: 4, 11.5: 4, 12.75: 3, 6.35: 3, 5.25: 3, 13: 3, 19: 3, 16.95: 3, 35: 3, 11.25: 2, 16: 2, 17: 2, 4: 2, 9: 2, 3.7: 2, 12.5: 2, 6.25: 2, 38: 2, 40: 2, 15.25: 1, 4.15: 1, 1.75: 1, 14.2: 1, 31.5: 1, 18.5: 1},
    20: {20: 3715, 10: 358, 25: 268, 15: 183, 5: 74, 19.1: 56, 30: 44, 12: 43, 8: 42, 6: 34, 13.2: 34, 12.75: 27, 14: 17, 6.35: 16, 23: 16, 5.25: 14, 11.25: 14, 6.6: 14, 7: 13, 34: 13, 4: 12, 33: 11, 40: 10, 5.75: 8, 21: 8, 19: 7, 17.8: 7, 50: 6, 16: 6, 9: 6, 45: 5, 13: 5, 18: 5, 2.85: 5, 1.25: 5, 5.1: 5, 24: 5, 19.5: 5, 4.15: 4},
    25: {25: 1430, 20: 166, 10: 149, 15: 137, 7: 65, 12: 63, 30: 43, 8: 27, 20.49: 18, 13: 9, 5: 9, 40: 9, 23: 6, 24: 4, 6.35: 3, 50: 3, 35: 3, 6: 3, 46: 2, 11: 2, 33: 2, 58: 2, 18: 2, 19: 2, 22: 1, 36: 1, 16.25: 1, 4: 1, 16.5: 1, 21: 1},
}

# Breakdowns: (step-1 users, same recipient, same recipient + offer)
PTYPE_CID = ("1lhm7pul", "wn7690u2")
PTYPE = {"Mobile Bundle": (215727, 34496, 25727), "Mobile Top Up (airtime)": (180445, 30871, 21383), "Mobile Data": (25868, 5967, 3517)}
CTRY_CID = ("fkgq1v9e", "yqr0zftt")
CTRY = {
    "Guatemala": (94033, 14225, 11217), "Haiti": (72163, 9100, 5757), "Honduras": (50625, 7881, 5393),
    "Dominican Rep.": (46838, 10413, 7382), "Mexico": (26142, 4834, 3393), "El Salvador": (26104, 4852, 3818),
    "Jamaica": (25184, 4656, 3004), "Nicaragua": (11560, 2315, 1877), "Nigeria": (11332, 1920, 1177),
    "Ethiopia": (10056, 1457, 925), "Liberia": (5674, 1277, 1036), "Afghanistan": (4798, 968, 692),
}
# Entry point of the repeat purchase (top_up_started_from on step 2): (same recipient, same recipient + offer)
SRC_CID = ("bh7kkfk9", "5ebyk35f")
SRC = {
    "quick-send": (17904, 16865), "calling-home-quick-send": (5546, 5257), "people-page-quick-send": (341, 307),
    "chat-send-again": (284, 253), "hub-send-again": (278, 273),
    "recents-people-list": (22360, 12133), "people-page": (11653, 6825), "search": (4715, 1817),
    "people-page-offers": (1199, 591), "post-call": (372, 220), "empty": (6185, 5812),
}
ONE_TAP = ["quick-send", "calling-home-quick-send", "people-page-quick-send", "chat-send-again", "hub-send-again"]
BROWSE = ["recents-people-list", "people-page", "search", "people-page-offers", "post-call"]

# Per-buyer distinct values over 1 Jul to 27 Sep 2026, by purchase count.
Q_CID = dict(users="qoa8llpm", offers="tyiyf209", recips="iv81w3kq", carriers="in1hm5p3", amounts="kntuco9b")
BUCKETS = ["1", "2", "3", "4", "5-7", "8-12", "13+"]
Q_USERS = [170973, 97224, 62076, 41841, 66961, 40391, 27277]
Q_PURCH = [172182, 195469, 187257, 168203, 390465, 387395, 569658]
Q_OFFERS = [1.0036, 1.5193, 1.9155, 2.2768, 2.7861, 3.6091, 4.9784]
Q_RECIPS = [1.0040, 1.5854, 2.0686, 2.5409, 3.2722, 4.6612, 8.3911]
Q_CARR = [1.0013, 1.1926, 1.3147, 1.4176, 1.5337, 1.7202, 1.9866]
Q_AMT = [1.0032, 1.4707, 1.8124, 2.1167, 2.5277, 3.1366, 4.0326]

# ---------------------------------------------------------------------------
# Derived figures
# ---------------------------------------------------------------------------
F = {k: v[0] for k, v in FUN.items()}
ANY, RECIP, RO, OFFER = F["any"]["all"], F["recip"]["all"], F["recip_offer"]["all"], F["offer"]["all"]
RC, RCA, RT = F["recip_carrier"]["all"], F["recip_carrier_amount"]["all"], F["recip_type"]["all"]
OTHER = ANY - RECIP
OTHER_SAME_CARRIER = CARRIER_ALL - RC
OTHER_SAME_OFFER = OFFER - RO
OTHER_DIFF_OFFER = OTHER_SAME_CARRIER - OTHER_SAME_OFFER
OTHER_DIFF_CARRIER = OTHER - OTHER_SAME_CARRIER
assert RO + (RECIP - RO) + OTHER_SAME_OFFER + OTHER_DIFF_OFFER + OTHER_DIFF_CARRIER == ANY

SAME_RECIP_SPLIT = [
    ("Same offer", RO),
    ("Same product type, different offer", RT - RO),
    ("Different product type", RECIP - RT),
]
assert sum(v for _, v in SAME_RECIP_SPLIT) == RECIP
SAME_AMOUNT_NEW_ID = RCA - RO   # same carrier and amount, new offer ID (catalog change); overlaps the rows above
CARRIER_CHANGED = RECIP - RC    # recipient's carrier changed; overlaps the rows above


def amount_split(start):
    d = AMOUNTS[start]
    conv = sum(d.values())
    same = d.get(start, 0)
    up = sum(v for k, v in d.items() if k > start)
    down = sum(v for k, v in d.items() if k < start)
    avg = sum(k * v for k, v in d.items()) / conv
    return conv, down, same, up, avg


AMT_ROWS = {s: amount_split(s) for s in AMOUNTS}
AMT_TOT = [sum(r[i] for r in AMT_ROWS.values()) for i in range(4)]


def grp(keys):
    return sum(SRC[k][0] for k in keys), sum(SRC[k][1] for k in keys)


SRC_TOTAL = sum(v[0] for v in SRC.values())
SRC_SAME = sum(v[1] for v in SRC.values())
OT, BR = grp(ONE_TAP), grp(BROWSE)

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


def stacked(row_label, sub, parts, cid=None):
    """parts: list of (label, value, css_var, on_color_var)."""
    total = sum(p[1] for p in parts)
    segs = []
    for label, v, var, on in parts:
        share = v / total
        tip = f"{label}: {pct(share)} ({num(v)} buyers)"
        inner = f'<span class="in" style="color:var({on})">{pct(share)}</span>' if share >= 0.2 else ""
        segs.append(f'<span class="seg" style="flex:{v} 1 0;background:var({var})" data-tip="{escape(tip)}" tabindex="0">{inner}</span>')
    link = f' · {a(chart(cid), "chart")}' if cid else ""
    return f'''<div class="sb">
  <div class="sb-h"><span class="sb-l">{row_label}</span><span class="sb-s">{sub}{link}</span></div>
  <div class="sb-bar">{"".join(segs)}</div>
</div>'''


def hbar_rows(rows, maxv=1.0, fmt=pct, var="--s1"):
    """rows: list of (label, value, note, tip, color_var or None, extra_class)."""
    out = []
    for label, v, note, tip, color, cls in rows:
        w = v / maxv * 100
        out.append(f'''<div class="hb {cls}">
  <div class="hb-l">{label}</div>
  <div class="hb-t"><span class="hb-b" style="width:{w:.2f}%;background:var({color or var})" data-tip="{escape(tip)}" tabindex="0"></span><span class="hb-v">{fmt(v)}</span></div>
  <div class="hb-n">{note}</div>
</div>''')
    return "\n".join(out)


def legend(items):
    return '<div class="lg">' + "".join(f'<span class="lg-i"><span class="sw" style="background:var({v})"></span>{t}</span>' for t, v in items) + "</div>"


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
seg_names = dict(all="All buyers", est="Established (3+ purchases Apr-Jun)", light="Light (1-2 purchases Apr-Jun)", new="New or lapsed (0 purchases Apr-Jun)")

fig1 = f'''<figure>
  <div class="fig-t">Where the next top-up went, for {num(ANY)} buyers who bought again within 30 days</div>
  {legend([("Same offer as last time", "--s1"), ("Different offer, same carrier", "--s2"), ("Different carrier, so the offer had to change", "--s3")])}
  {stacked("To the same recipient", f"{num(RECIP)} next purchases ({pct(RECIP / ANY)})", [
      ("Same offer", RO, "--s1", "--on-s1"),
      ("Different offer, same carrier", RC - RO, "--s2", "--on-s2"),
      ("Recipient changed carrier", RECIP - RC, "--s3", "--on-s3")], "h5r3f3a0")}
  {stacked("To a different recipient", f"{num(OTHER)} next purchases ({pct(OTHER / ANY)})", [
      ("Same offer", OTHER_SAME_OFFER, "--s1", "--on-s1"),
      ("Different offer, same carrier", OTHER_DIFF_OFFER, "--s2", "--on-s2"),
      ("Different carrier", OTHER_DIFF_CARRIER, "--s3", "--on-s3")], "g6r3txzr")}
  <figcaption><b>Read it as:</b> when the next top-up goes to the same person, {pct(RO / RECIP)} of the time it is the exact same offer. Seven in ten next top-ups go to someone else, and a third of those land on another carrier, where no offer can carry over. Built from {a(chart("dmmwysk6"), "any repeat")}, {a(chart("as44pz1v"), "same recipient")}, {a(chart("h5r3f3a0"), "same recipient + offer")}, {a(chart("g6r3txzr"), "same offer")}, {a(chart(CARRIER_CID), "same carrier")} and {a(chart("ghgqoyi8"), "same recipient + carrier")}.</figcaption>
</figure>'''

decomp_rows = [
    ("Same recipient, same offer", RO),
    ("Same recipient, different offer", RECIP - RO),
    ("Different recipient, same offer", OTHER_SAME_OFFER),
    ("Different recipient, same carrier, different offer", OTHER_DIFF_OFFER),
    ("Different recipient on another carrier", OTHER_DIFF_CARRIER),
]
table1 = '<div class="tw"><table><thead><tr><th>Next purchase</th><th class="n">Buyers</th><th class="n">Share</th></tr></thead><tbody>' + "".join(
    f"<tr><td>{l}</td><td class=\"n\">{num(v)}</td><td class=\"n\">{pct(v / ANY)}</td></tr>" for l, v in decomp_rows
) + f'<tr class="tot"><td>All next purchases within 30 days</td><td class="n">{num(ANY)}</td><td class="n">100.0%</td></tr></tbody></table></div>'

# Fig 2: same offer given same recipient, by segment + robustness
rows2 = []
for s in ["new", "light", "est", "all"]:
    r, ro = F["recip"][s], F["recip_offer"][s]
    rows2.append((seg_names[s], ro / r, f"{num(ro)} of {num(r)}", f"{seg_names[s]}: {pct(ro / r)} same offer ({num(ro)} of {num(r)} same-recipient repeats)", None, "strong" if s == "all" else ""))
rob = [
    ("Regular purchases only (no subscription creations)", REG["recip_offer"] / REG["recip"], f"{num(REG['recip_offer'])} of {num(REG['recip'])}"),
    ("60-day window instead of 30", W60["recip_offer"] / W60["recip"], f"{num(W60['recip_offer'])} of {num(W60['recip'])}"),
    ("Other recipients allowed in between", F["per_recip_offer"]["all"] / F["per_recip"]["all"], f"{num(F['per_recip_offer']['all'])} of {num(F['per_recip']['all'])}"),
]
rows2b = [(l, v, n, f"{l}: {pct(v)} same offer ({n})", "--s1", "") for l, v, n in rob]

fig2 = f'''<figure>
  <div class="fig-t">Same recipient, same offer: share of repeat top-ups to the same person that used the exact same offer</div>
  <div class="hbs">{hbar_rows(rows2)}</div>
  <div class="sub-h">Robustness checks, all buyers</div>
  <div class="hbs">{hbar_rows(rows2b)}</div>
  <figcaption><b>Loyalty grows with tenure.</b> New or lapsed buyers repeat the same offer {pct(F["recip_offer"]["new"] / F["recip"]["new"])} of the time, established buyers {pct(F["recip_offer"]["est"] / F["recip"]["est"])}. The answer holds when subscription creations are excluded ({a(chart(REG_CID["recip"]), "same recipient")}, {a(chart(REG_CID["recip_offer"]), "same offer")}), over 60 days ({a(chart(W60_CID["recip"]), "same recipient")}, {a(chart(W60_CID["recip_offer"]), "same offer")}) and when purchases to other people happen in between ({a(chart("p7xgzbsm"), "same recipient")}, {a(chart("tk7wnx2b"), "same offer")}).</figcaption>
</figure>'''

table_switch = '<div class="tw"><table><thead><tr><th>Same-recipient repeat</th><th class="n">Buyers</th><th class="n">Share</th></tr></thead><tbody>' + "".join(
    f"<tr><td>{l}</td><td class=\"n\">{num(v)}</td><td class=\"n\">{pct(v / RECIP, 2 if v / RECIP < 0.01 else 1)}</td></tr>" for l, v in SAME_RECIP_SPLIT
) + f'<tr class="tot"><td>All repeat top-ups to the same recipient</td><td class="n">{num(RECIP)}</td><td class="n">100.0%</td></tr></tbody></table></div>'

# Fig 3: amount direction
amt_bars = []
for s, (conv, down, same, up, avg) in AMT_ROWS.items():
    amt_bars.append(stacked(f"After a ${s} top-up", f"{num(conv)} repeats · average next ${avg:.2f}", [
        ("Lower amount", down, "--down", "--on-down"),
        ("Same amount", same, "--neutral", "--on-neutral"),
        ("Higher amount", up, "--s1", "--on-s1")], AMOUNT_CID[s]))
amt_table = '<div class="tw"><table><thead><tr><th>Previous top-up</th><th class="n">Repeats</th><th class="n">Lower</th><th class="n">Same</th><th class="n">Higher</th><th class="n">Avg next</th></tr></thead><tbody>' + "".join(
    f'<tr><td>{a(chart(AMOUNT_CID[s]), f"${s}")}</td><td class="n">{num(c)}</td><td class="n">{pct(d / c)}</td><td class="n">{pct(sm / c)}</td><td class="n">{pct(u / c)}</td><td class="n">${av:.2f}</td></tr>'
    for s, (c, d, sm, u, av) in AMT_ROWS.items()
) + f'<tr class="tot"><td>Pooled</td><td class="n">{num(AMT_TOT[0])}</td><td class="n">{pct(AMT_TOT[1] / AMT_TOT[0])}</td><td class="n">{pct(AMT_TOT[2] / AMT_TOT[0])}</td><td class="n">{pct(AMT_TOT[3] / AMT_TOT[0])}</td><td class="n"></td></tr></tbody></table></div>'
fig3 = f'''<figure>
  <div class="fig-t">Amount of the next top-up to the same recipient, by the amount of the previous one (USD)</div>
  {legend([("Lower amount", "--down"), ("Same amount", "--neutral"), ("Higher amount", "--s1")])}
  {"".join(amt_bars)}
  <figcaption><b>No drift up or down.</b> {pct(AMT_TOT[2] / AMT_TOT[0])} of same-recipient repeats keep the denomination. The rest split almost evenly: {pct(AMT_TOT[3] / (AMT_TOT[1] + AMT_TOT[3]))} of changes go up and {pct(AMT_TOT[1] / (AMT_TOT[1] + AMT_TOT[3]))} go down. Small amounts tend to move up and large ones down, toward the $10 to $20 band.</figcaption>
</figure>'''

# Fig 4: entry points
def src_row(label, keys, color, note_extra=""):
    r, s = grp(keys)
    return (label, s / r, f"{num(s)} of {num(r)}{note_extra}", f"{label}: {pct(s / r)} same offer ({num(s)} of {num(r)})", color, "")


rows4 = [
    src_row("<code>quick-send</code>", ["quick-send"], "--s1"),
    src_row("<code>calling-home-quick-send</code>", ["calling-home-quick-send"], "--s1"),
    src_row("Send-again buttons (people page, chat, hub)", ["people-page-quick-send", "chat-send-again", "hub-send-again"], "--s1"),
    src_row("<code>people-page</code>", ["people-page"], "--s2"),
    src_row("<code>recents-people-list</code>", ["recents-people-list"], "--s2"),
    src_row("People page offers, post-call", ["people-page-offers", "post-call"], "--s2"),
    src_row("<code>search</code>", ["search"], "--s2"),
    src_row("Entry point not tracked (<code>\"empty\"</code>)", ["empty"], "--neutral"),
]
fig4 = f'''<figure>
  <div class="fig-t">Same recipient, same offer, by where the repeat top-up started (<code>top_up_started_from</code>)</div>
  {legend([("One-tap repeat", "--s1"), ("Browse the offer list", "--s2"), ("Not tracked", "--neutral")])}
  <div class="hbs">{hbar_rows(rows4)}</div>
  <figcaption><b>One-tap repeats are {pct(OT[0] / SRC_TOTAL)} of same-recipient repeats and land on the same offer {pct(OT[1] / OT[0])} of the time.</b> Browse flows are {pct(BR[0] / SRC_TOTAL)} of repeats, and even after seeing the full list, {pct(BR[1] / BR[0])} of those buyers pick the offer they bought last time. Charts: {a(chart(SRC_CID[0]), "same recipient by entry point")}, {a(chart(SRC_CID[1]), "same offer by entry point")}.</figcaption>
</figure>'''

# Fig 5: product type and country
rows5a = [(k, ro / r, f"{num(ro)} of {num(r)}", f"{k}: {pct(ro / r)} same offer", None, "") for k, (n, r, ro) in PTYPE.items()]
rows5b = [(k, ro / r, f"{num(ro)} of {num(r)}", f"{k}: {pct(ro / r)} same offer ({num(n)} buyers)", None, "")
          for k, (n, r, ro) in sorted(CTRY.items(), key=lambda x: -x[1][2] / x[1][1])]
fig5 = f'''<div class="two">
<figure>
  <div class="fig-t">Same recipient, same offer, by product type of the previous top-up</div>
  <div class="hbs">{hbar_rows(rows5a)}</div>
  <figcaption>Bundles are the stickiest; data packs are the most switched. Charts: {a(chart(PTYPE_CID[0]), "same recipient")}, {a(chart(PTYPE_CID[1]), "same offer")}.</figcaption>
</figure>
<figure>
  <div class="fig-t">Same recipient, same offer, by destination country (top 12 by buyers)</div>
  <div class="hbs">{hbar_rows(rows5b)}</div>
  <figcaption>Central America repeats most; Haiti, Jamaica, Nigeria and Ethiopia switch most. Charts: {a(chart(CTRY_CID[0]), "same recipient")}, {a(chart(CTRY_CID[1]), "same offer")}.</figcaption>
</figure>
</div>'''

# Fig 6: quarter view dumbbell (0..9 scale)
QMAX = 9.0
dumb = []
for i, b in enumerate(BUCKETS):
    pts = [(Q_CARR[i], "--s3", "Carriers"), (Q_OFFERS[i], "--s1", "Offers"), (Q_RECIPS[i], "--s2", "Recipients")]
    lo, hi = min(p[0] for p in pts), max(p[0] for p in pts)
    dots = "".join(
        f'<span class="dot" style="left:{v / QMAX * 100:.2f}%;background:var({c})" data-tip="{b} purchases: {t.lower()} {v:.2f} per buyer" tabindex="0"></span>' for v, c, t in pts
    )
    dumb.append(f'''<div class="db">
  <div class="db-l">{b} <span>purchase{"s" if b != "1" else ""}</span></div>
  <div class="db-t"><span class="db-r" style="left:{lo / QMAX * 100:.2f}%;width:{(hi - lo) / QMAX * 100:.2f}%"></span>{dots}</div>
  <div class="db-n">{num(Q_USERS[i])} buyers</div>
</div>''')
ticks = "".join(f'<span style="left:{t / QMAX * 100:.2f}%">{t}</span>' for t in range(0, 10))
q_table = '<div class="tw"><table><thead><tr><th>Purchases, 1 Jul to 27 Sep</th><th class="n">Buyers</th><th class="n">Purchases per buyer</th><th class="n">Recipients</th><th class="n">Offers</th><th class="n">Amounts</th><th class="n">Carriers</th></tr></thead><tbody>' + "".join(
    f'<tr><td>{b}</td><td class="n">{num(Q_USERS[i])}</td><td class="n">{Q_PURCH[i] / Q_USERS[i]:.2f}</td><td class="n">{Q_RECIPS[i]:.2f}</td><td class="n">{Q_OFFERS[i]:.2f}</td><td class="n">{Q_AMT[i]:.2f}</td><td class="n">{Q_CARR[i]:.2f}</td></tr>'
    for i, b in enumerate(BUCKETS)
) + "</tbody></table></div>"
fig6 = f'''<figure>
  <div class="fig-t">Distinct recipients, offers and carriers per buyer over 89 days, by how many times they bought</div>
  {legend([("Distinct carriers", "--s3"), ("Distinct offers", "--s1"), ("Distinct recipients", "--s2")])}
  <div class="dbs">{"".join(dumb)}
    <div class="db axis"><div class="db-l"></div><div class="db-t ticks">{ticks}</div><div class="db-n">per buyer</div></div>
  </div>
  <figcaption><b>Buyers use fewer distinct offers than they have recipients, at every frequency.</b> A buyer with 13 or more purchases tops up 8.4 people but uses only 5.0 offers, so the same offer goes to several people. Charts: {a(chart(Q_CID["users"]), "buyers")}, {a(chart(Q_CID["recips"]), "recipients")}, {a(chart(Q_CID["offers"]), "offers")}, {a(chart(Q_CID["carriers"]), "carriers")}, {a(chart(Q_CID["amounts"]), "amounts")}.</figcaption>
</figure>'''

TOTAL_Q_USERS = sum(Q_USERS)
TOTAL_Q_PURCH = sum(Q_PURCH)

CSS = """
:root{
  --paper:#F5F7FA; --surface:#FFFFFF; --surface-2:#EDF1F6;
  --ink:#0F141C; --ink-2:#39424F; --ink-3:#6B7484;
  --rule:#D9E0EA; --rule-soft:#E8EDF3; --track:#EDF1F6;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --neutral:#cdd5df; --down:#e34948;
  --on-s1:#FFFFFF; --on-s2:#0F141C; --on-s3:#0F141C; --on-neutral:#0F141C; --on-down:#0F141C;
  --link:#1f63b8;
  --sans:"Public Sans","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --paper:#0C1016; --surface:#141A22; --surface-2:#1B222C;
  --ink:#E8ECF2; --ink-2:#B4BDCA; --ink-3:#7F8A9A;
  --rule:#26303C; --rule-soft:#1E2630; --track:#1B222C;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --neutral:#3a4654; --down:#e66767;
  --on-s1:#0C1016; --on-s2:#0C1016; --on-s3:#0C1016; --on-neutral:#E8ECF2; --on-down:#0C1016;
  --link:#6da7ec;
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --paper:#0C1016; --surface:#141A22; --surface-2:#1B222C;
  --ink:#E8ECF2; --ink-2:#B4BDCA; --ink-3:#7F8A9A;
  --rule:#26303C; --rule-soft:#1E2630; --track:#1B222C;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --neutral:#3a4654; --down:#e66767;
  --on-s1:#0C1016; --on-s2:#0C1016; --on-s3:#0C1016; --on-neutral:#E8ECF2; --on-down:#0C1016;
  --link:#6da7ec;
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;margin:0}
.wrap{max-width:1040px;margin:0 auto;padding-block:40px 90px;padding-left:20px;padding-right:20px}
a{color:var(--link);text-underline-offset:2px}
a:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--link);outline-offset:2px}
code{font-family:var(--mono);font-size:.86em;background:var(--surface-2);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--s2);margin:0 0 10px;font-weight:600}
h1{font-size:clamp(28px,4.6vw,42px);line-height:1.1;letter-spacing:-.022em;font-weight:700;margin:0;text-wrap:balance;max-width:24ch}
.stand{margin:16px 0 0;max-width:66ch;color:var(--ink-2);font-size:18px}
.meta{display:flex;flex-wrap:wrap;gap:4px 24px;margin:22px 0 0;font-family:var(--mono);font-size:11.5px;color:var(--ink-3);border-top:1px solid var(--rule);padding-top:14px}
.meta b{color:var(--ink-2);font-weight:500}
h2{font-size:23px;font-weight:700;letter-spacing:-.015em;margin:0;text-wrap:balance}
section{margin-top:56px}
.sh{border-bottom:2px solid var(--ink);padding-bottom:8px;margin-bottom:18px}
p{margin:0 0 14px;max-width:70ch}
ul,ol{margin:0 0 14px;padding-left:22px;max-width:70ch}
li{margin:0 0 8px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:10px;overflow:hidden;margin:28px 0 0}
.tile{background:var(--surface);padding:16px 18px}
.tile .k{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin:0 0 8px;font-weight:500}
.tile .v{font-size:34px;font-weight:700;letter-spacing:-.025em;line-height:1;color:var(--ink)}
.tile .s{font-size:13.5px;color:var(--ink-2);margin:8px 0 0;line-height:1.45}
figure{margin:24px 0;background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:18px 18px 14px;min-width:0}
.fig-t{font-weight:600;font-size:15px;line-height:1.35;margin:0 0 12px;text-wrap:balance}
figcaption{font-size:13.5px;color:var(--ink-2);margin-top:14px;line-height:1.5;border-top:1px solid var(--rule-soft);padding-top:10px}
figcaption b{color:var(--ink);font-weight:600}
.sub-h{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin:18px 0 8px;font-weight:500}
.lg{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--ink-2);margin:0 0 14px}
.lg-i{display:inline-flex;align-items:center;gap:7px}
.sw{width:12px;height:12px;border-radius:3px;flex:none}
.sb{margin:0 0 16px}
.sb-h{display:flex;flex-wrap:wrap;justify-content:space-between;gap:2px 12px;margin:0 0 6px}
.sb-l{font-weight:600;font-size:14px}
.sb-s{font-family:var(--mono);font-size:11.5px;color:var(--ink-3)}
.sb-bar{display:flex;gap:2px;height:30px;background:var(--surface)}
.seg{display:flex;align-items:center;justify-content:center;min-width:2px;cursor:default}
.seg:first-child{border-radius:4px 0 0 4px}.seg:last-child{border-radius:0 4px 4px 0}
.seg .in{font-family:var(--mono);font-size:12px;font-weight:600;white-space:nowrap}
.hbs{display:grid;gap:8px}
.hb{display:grid;grid-template-columns:minmax(0,15rem) minmax(0,1fr) 7.5rem;align-items:center;gap:12px;font-size:13.5px}
.hb.strong .hb-l,.hb.strong .hb-v{font-weight:700;color:var(--ink)}
.hb-l{color:var(--ink-2);line-height:1.3}
.hb-t{display:flex;align-items:center;gap:8px;min-width:0}
.hb-b{display:block;height:16px;border-radius:0 4px 4px 0;min-width:2px}
.hb-v{font-family:var(--mono);font-size:12.5px;font-weight:600;color:var(--ink);white-space:nowrap}
.hb-n{font-family:var(--mono);font-size:11px;color:var(--ink-3);text-align:right;white-space:nowrap}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:0 20px}
.two .hb{grid-template-columns:minmax(0,9.5rem) minmax(0,1fr) 6.8rem}
.dbs{display:grid;gap:10px}
.db{display:grid;grid-template-columns:6.5rem minmax(0,1fr) 7rem;align-items:center;gap:12px;font-size:13.5px}
.db-l{font-family:var(--mono);font-weight:600;color:var(--ink)}
.db-l span{font-family:var(--sans);font-weight:400;color:var(--ink-3);font-size:12px}
.db-t{position:relative;height:18px;background:linear-gradient(var(--rule-soft),var(--rule-soft)) center/100% 1px no-repeat}
.db-r{position:absolute;top:7px;height:4px;background:var(--rule);border-radius:2px}
.dot{position:absolute;top:1px;width:16px;height:16px;margin-left:-8px;border-radius:50%;border:2px solid var(--surface);cursor:default}
.db-n{font-family:var(--mono);font-size:11px;color:var(--ink-3);text-align:right;white-space:nowrap}
.db.axis .db-t{background:none;height:16px}
.ticks span{position:absolute;transform:translateX(-50%);font-family:var(--mono);font-size:10.5px;color:var(--ink-3)}
.tw{overflow-x:auto;margin:16px 0;border:1px solid var(--rule);border-radius:10px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:520px}
th,td{padding:9px 13px;text-align:left;border-bottom:1px solid var(--rule-soft);vertical-align:top}
th{background:var(--surface-2);font-weight:600;font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2)}
td.n,th.n{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tr.tot td{background:var(--surface-2);font-weight:600}
details{margin:10px 0 0}
summary{cursor:pointer;font-size:13.5px;color:var(--link);font-weight:500}
.callout{border-left:3px solid var(--s1);background:var(--surface);padding:15px 18px;margin:22px 0;border-radius:0 8px 8px 0}
.callout p:last-child{margin-bottom:0}
.callout .lab{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;color:var(--s1);margin:0 0 6px}
.recs{display:grid;gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:10px;overflow:hidden;margin:20px 0}
.rec{background:var(--surface);padding:16px 18px;display:grid;grid-template-columns:minmax(0,15rem) minmax(0,1fr);gap:6px 22px}
.rec h3{font-size:15.5px;margin:0;line-height:1.35;text-wrap:balance}
.rec p{margin:0;font-size:14.5px;color:var(--ink-2);max-width:none}
.method{font-size:14.5px}
.method dt{font-weight:600;margin-top:12px}
.method dd{margin:2px 0 0;color:var(--ink-2);max-width:72ch}
.sku{display:inline-flex;flex-wrap:wrap;gap:6px;margin:4px 0 0}
#tip{position:fixed;z-index:10;pointer-events:none;background:var(--ink);color:var(--paper);font-size:12.5px;line-height:1.35;padding:6px 9px;border-radius:6px;max-width:260px;box-shadow:0 4px 14px rgba(0,0,0,.18)}
@media (max-width:640px){
  .hb,.two .hb{grid-template-columns:minmax(0,1fr) auto;gap:4px 10px}
  .hb-l{grid-column:1/-1}
  .hb-n{text-align:right}
  .db{grid-template-columns:4.2rem minmax(0,1fr);gap:4px 10px}
  .db-n{display:none}
  .db-l span{display:none}
  .rec{grid-template-columns:1fr}
  .tile .v{font-size:30px}
}
@media (prefers-reduced-motion:no-preference){.seg,.hb-b,.dot{transition:opacity .15s}}
"""

JS = """
(function(){
  var tip=document.getElementById('tip');
  function show(e){var t=e.target.closest('[data-tip]');if(!t)return;tip.textContent=t.getAttribute('data-tip');tip.hidden=false;move(e,t)}
  function move(e,t){var x,y;if(e.clientX!==undefined&&e.type!=='focusin'){x=e.clientX;y=e.clientY}else{var r=(t||e.target).getBoundingClientRect();x=r.left+r.width/2;y=r.top}
    var w=tip.offsetWidth,h=tip.offsetHeight;var nx=Math.min(Math.max(8,x-w/2),window.innerWidth-w-8);var ny=y-h-12;if(ny<8)ny=y+18;tip.style.left=nx+'px';tip.style.top=ny+'px'}
  function hide(){tip.hidden=true}
  document.addEventListener('mouseover',show);document.addEventListener('focusin',show);
  document.addEventListener('mousemove',function(e){if(!tip.hidden&&e.target.closest('[data-tip]'))move(e)});
  document.addEventListener('mouseout',function(e){if(e.target.closest('[data-tip]'))hide()});
  document.addEventListener('focusout',hide);
})();
"""

same_offer_share_recip = RO / RECIP
html = f'''<title>IMTU Offer Loyalty</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <p class="eyebrow">IMTU · Amplitude analysis · 28 Sep 2026</p>
  <h1>Buyers keep their offer. What changes is who they top up.</h1>
  <p class="stand">When a BOSS Revolution user tops up the same person again, {pct(same_offer_share_recip, 0)} of the time it is the exact same offer and {pct(RT / RECIP, 0)} of the time the same product type. Most offer changes between one purchase and the next happen because the next top-up is for someone else, often on another carrier.</p>
  <div class="meta">
    <span><b>Source</b> Amplitude BR app Prod (650506), {a(EVENT_URL, "MTUOrderStatusSuccessScr")}</span>
    <span><b>Cohort</b> {num(N["all"])} buyers, 1 Jul to 28 Aug 2026</span>
    <span><b>Window</b> next purchase within 30 days</span>
    <span><b>Evidence</b> {a(DASH, "dashboard fcw7gsdb")} (34 charts)</span>
  </div>
</header>

<div class="tiles">
  <div class="tile"><p class="k">Same person, same offer</p><div class="v">{pct(same_offer_share_recip)}</div><p class="s">of repeat top-ups to the same recipient use the exact same offer ID ({num(RO)} of {num(RECIP)}).</p></div>
  <div class="tile"><p class="k">Same person, same product type</p><div class="v">{pct(RT / RECIP)}</div><p class="s">stay on bundle, airtime or data. Most of the rest is a different denomination.</p></div>
  <div class="tile"><p class="k">Next top-up, same person</p><div class="v">{pct(RECIP / ANY)}</div><p class="s">of next purchases go to the same recipient. {pct(OTHER / ANY)} go to someone else.</p></div>
  <div class="tile"><p class="k">Next top-up, same offer</p><div class="v">{pct(OFFER / ANY)}</div><p class="s">of next purchases reuse the previous offer, whoever the recipient is.</p></div>
</div>

<section>
  <div class="sh"><h2>The answer: repeat for the same person, change for a different one</h2></div>
  <p>For each buyer, we took their first successful top-up after 30 June and looked at the very next one. {pct(ANY / N["all"], 0)} bought again within 30 days. The next purchase went to the same recipient only {pct(RECIP / ANY, 0)} of the time, and those repeats are highly loyal. Next purchases for a different recipient still reuse the same offer {pct(OTHER_SAME_OFFER / OTHER, 0)} of the time, and {pct(OTHER_SAME_OFFER / OTHER_SAME_CARRIER, 0)} of the time when the new recipient is on the same carrier.</p>
  {fig1}
  <details><summary>Show the table</summary>{table1}</details>
</section>

<section>
  <div class="sh"><h2>For the same person, the offer rarely changes</h2></div>
  <p>The share of same-recipient repeats that keep the offer ID stays between {pct(min(F["recip_offer"][s] / F["recip"][s] for s in SEGS), 0)} and {pct(REG["recip_offer"] / REG["recip"], 0)} across tenure segments and every robustness check. It is lowest for new buyers, who are still finding their offer, and highest for established buyers and for regular (non-subscription) purchases.</p>
  {fig2}
  <p>When the offer does change for the same person, it is mostly a different denomination within the same product type. Catalog churn and carrier changes are negligible: only {num(SAME_AMOUNT_NEW_ID)} switches kept the same carrier and amount under a new offer ID, and {num(CARRIER_CHANGED)} followed a change of the recipient's carrier ({a(chart("5mo4xk68"), "same recipient, carrier and amount")}, {a(chart("ghgqoyi8"), "same recipient and carrier")}, {a(chart("s2n5xug7"), "same recipient and type")}).</p>
  {table_switch}
</section>

<section>
  <div class="sh"><h2>When the amount changes, it moves both ways</h2></div>
  <p>We checked the next same-recipient top-up after the five most common USD amounts. Denomination loyalty matches offer loyalty, and changes show no upward trend.</p>
  {fig3}
  <details><summary>Show the table</summary>{amt_table}</details>
</section>

<section>
  <div class="sh"><h2>Quick-send makes repeating automatic, but browsers repeat too</h2></div>
  <p>The entry point of the repeat purchase (<code>top_up_started_from</code>, from {a(DCS_4011, "DCS-4011")}) shows how much of the loyalty is the interface and how much is choice. One-tap repeats pre-fill the last order, so they are close to 100% by design. The browse flows are the cleaner test of preference: the buyer sees the offer list and most still pick the offer they bought last time.</p>
  {fig4}
</section>

<section>
  <div class="sh"><h2>Where buyers switch more</h2></div>
  <p>Data packs and a few markets switch more than average. These are the places where the offer list, promotions and featured offers have the most room to change what people buy.</p>
  {fig5}
</section>

<section>
  <div class="sh"><h2>Over a whole quarter, the same pattern</h2></div>
  <p>Across {num(TOTAL_Q_USERS)} buyers and {num(TOTAL_Q_PURCH)} purchases from 1 July to 27 September, the average buyer uses fewer distinct offers than they have recipients, whatever their frequency. Among buyers with exactly two purchases, {pct(2 - Q_OFFERS[1], 0)} bought the same offer twice, even though {pct(Q_RECIPS[1] - 1, 0)} of them topped up two different people.</p>
  {fig6}
  <details><summary>Show the table</summary>{q_table}</details>
</section>

<section>
  <div class="sh"><h2>What this means for the product</h2></div>
  <div class="recs">
    <div class="rec"><h3>Put the last offer first in the browse flows</h3><p>In the recents list, people page and search, {pct(BR[1] / BR[0], 0)} of same-recipient repeats end on the same offer after scrolling the full list. Showing "last sent to this person" at the top of the offer list would shorten the path for most of them. Check what the list pre-selects today before building.</p></div>
    <div class="rec"><h3>Subscriptions automate a habit that already exists</h3><p>{num(RO)} buyers in this cohort repeated the exact same offer to the same person within 30 days. They are the natural audience for a subscription offer on that recipient, and the offer to propose is the one they just bought.</p></div>
    <div class="rec"><h3>Upselling needs a nudge</h3><p>Denomination changes split {pct(AMT_TOT[3] / (AMT_TOT[1] + AMT_TOT[3]), 0)} up and {pct(AMT_TOT[1] / (AMT_TOT[1] + AMT_TOT[3]), 0)} down, so amounts do not rise on their own. The {pct(1 - same_offer_share_recip, 0)} of same-recipient repeats that already change offer, and the data-pack and Haiti, Jamaica and Nigeria buyers, are the most open to featured offers and promotions.</p></div>
    <div class="rec"><h3>Senders have a go-to offer</h3><p>{pct(OTHER_SAME_OFFER / ANY, 0)} of all next purchases send the same offer to a different person on the same carrier. Promotions set at offer level therefore reach more than one recipient per sender.</p></div>
    <div class="rec"><h3>Close the measurement gaps</h3><p>Offer-list position and a "pre-selected" flag on the order would separate accepted defaults from active choices; neither is tracked today (see the {a(AUDIT_URL, "IMTU Amplitude events audit")}). Subscription renewals are server-side and never reach Amplitude, so the true repeat rate of the same offer is higher than shown here.</p></div>
  </div>
</section>

<section>
  <div class="sh"><h2>Method and caveats</h2></div>
  <dl class="method">
    <dt>Pairing each purchase with the next one</dt>
    <dd>Amplitude funnels with the Nth-time filter on {a(EVENT_URL, "MTUOrderStatusSuccessScr")}: step 1 is a buyer's 1st purchase counted from 30 June (1-day lookback), step 2 their 2nd, within 30 days. The anchoring was validated: the "2nd purchase" step returned 148,089 users against 145,580 users with 2+ purchases in the same window. Each buyer contributes one pair, so heavy buyers are not over-weighted.</dd>
    <dt>What "same" means</dt>
    <dd>Each chart holds one or more properties constant across the two steps: <code>recipient_phone_number</code>, <code>offer_id</code>, <code>recipient_carrier</code>, <code>offer_amount</code>, <code>offer_type</code>. All are populated on 100% of successful orders in the last 30 days. Recipient numbers are consistently E.164 (99.96% carry a "+" prefix), so one person is not split across formats. Offer IDs are carrier SKUs such as <code>TIGO_GT-US-PAQUETIGO-10</code> or <code>CLARO_DO_6</code>; amounts are in the sender's currency (98% USD).</dd>
    <dt>Segments</dt>
    <dd>Established = 3+ purchases from 1 April to 29 June 2026 ({num(N["est"])} buyers), light = 1-2 ({num(N["light"])}), new or lapsed = none ({num(N["new"])}).</dd>
    <dt>Not covered</dt>
    <dd>The Money app (project 420385), subscription renewals (server-side, not in Amplitude) and anything before July 2026. Subscription creations are 25% of successful orders in the last 30 days; excluding them raises same-recipient loyalty from {pct(same_offer_share_recip)} to {pct(REG["recip_offer"] / REG["recip"])}. The Tableau connector failed to connect in this session, so this analysis uses Amplitude only. The <code>"empty"</code> entry point is a known tracking defect listed in the {a(AUDIT_URL, "events audit")}.</dd>
  </dl>
</section>
</div>
<div id="tip" hidden></div>
<script>{JS}</script>
'''

if __name__ == "__main__":
    assert "—" not in html, "em dash found"
    with open("IMTU_Offer_Loyalty_Analysis.html", "w") as f:
        f.write(html)
    print("wrote IMTU_Offer_Loyalty_Analysis.html", len(html), "chars")
