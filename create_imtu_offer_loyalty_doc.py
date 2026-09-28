#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU Offer Loyalty: Same Offer or Switch?".

Google Doc version of IMTU_Offer_Loyalty_Analysis.html. Every number is imported
from build_imtu_offer_loyalty_html.py, which holds the Amplitude chart outputs
(dashboard fcw7gsdb), so the page and the doc cannot drift apart.

Two steps, because Docs embeds images by public URL:
    python create_imtu_offer_loyalty_doc.py --figures   # draw the PNGs
    git add offer_loyalty_*.png && git commit && git push
    python create_imtu_offer_loyalty_doc.py [<doc_id>]  # build (or rebuild) the doc

Text blocks accept two inline marks: **bold** and [label](url).
"""

import re
import sys
import time
from pathlib import Path

import build_imtu_offer_loyalty_html as D
from build_imtu_offer_loyalty_html import chart, num, pct

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"
RAW_BASE = "https://raw.githubusercontent.com/tanaka-idt/IDT-Claude/main/"
ARTIFACT_URL = "https://claude.ai/artifact/B7waand91ZJ6qepi7r6ZNM"

TITLE = "IMTU Offer Loyalty: Same Offer or Switch?"
MARGIN_PT = 54
IMG_W = 500.0

# Validated categorical and diverging steps (dataviz validator, light mode).
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
NEUTRAL, DOWN = "#cdd5df", "#e34948"
INK, INK2, INK3, GRID = "#0F141C", "#39424F", "#6B7484", "#E1E6EE"

FIGS = {
    "next": "offer_loyalty_1_next_purchase.png",
    "loyal": "offer_loyalty_2_same_offer_share.png",
    "amount": "offer_loyalty_3_amount_direction.png",
    "entry": "offer_loyalty_4_entry_point.png",
    "where": "offer_loyalty_5_type_country.png",
    "quarter": "offer_loyalty_6_quarter_view.png",
}

# ---------------------------------------------------------------- figures ----


def draw_figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    plt.rcParams.update({
        "font.family": ["Arial", "Helvetica", "DejaVu Sans"], "font.size": 9,
        "axes.edgecolor": GRID, "axes.labelcolor": INK3, "xtick.color": INK3,
        "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
        "axes.spines.left": False, "savefig.dpi": 220, "savefig.bbox": "tight",
        "savefig.pad_inches": 0.12,
    })

    def label_color(fill):
        return "#FFFFFF" if fill == S1 else INK

    def stacked_rows(ax, rows, colors, min_label=0.12):
        """rows: list of (label, [values]); draws 100% bars top to bottom."""
        for i, (lab, vals) in enumerate(rows):
            tot = sum(vals)
            left = 0.0
            for v, c in zip(vals, colors):
                w = v / tot
                ax.barh(i, w, left=left, height=0.56, color=c, edgecolor="white", linewidth=2)
                if w >= min_label:
                    ax.text(left + w / 2, i, pct(w), ha="center", va="center",
                            fontsize=8.5, fontweight="bold", color=label_color(c))
                left += w
        ax.set_yticks(range(len(rows)), [r[0] for r in rows])
        ax.invert_yaxis()
        ax.set_xlim(0, 1)
        ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

    def hbars(ax, rows, colors, xmax=1.0, note_col=True, note_x=1.14):
        """rows: list of (label, value, note)."""
        for i, (lab, v, note) in enumerate(rows):
            ax.barh(i, v, height=0.56, color=colors[i])
            ax.text(v + xmax * 0.012, i, pct(v), va="center", fontsize=8.5, fontweight="bold", color=INK)
            if note_col:
                ax.text(xmax * note_x, i, note, va="center", ha="right", fontsize=7.5, color=INK3)
        ax.set_yticks(range(len(rows)), [r[0] for r in rows])
        ax.invert_yaxis()
        ax.set_xlim(0, xmax)
        ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

    def legend(fig, items, ax=None):
        y = ax.get_position().y1 + 0.02 if ax is not None else 1.0
        fig.legend(handles=[Patch(color=c, label=t) for t, c in items], loc="lower left",
                   bbox_to_anchor=(0.0, y), ncol=len(items), frameon=False, fontsize=8.5,
                   handlelength=1.1, handleheight=1.1, columnspacing=1.4)

    # 1. Where the next top-up went
    fig, ax = plt.subplots(figsize=(7.0, 1.9))
    stacked_rows(ax, [
        (f"Same recipient\n{num(D.RECIP)} ({pct(D.RECIP / D.ANY)})", [D.RO, D.RC - D.RO, D.RECIP - D.RC]),
        (f"Different recipient\n{num(D.OTHER)} ({pct(D.OTHER / D.ANY)})", [D.OTHER_SAME_OFFER, D.OTHER_DIFF_OFFER, D.OTHER_DIFF_CARRIER]),
    ], [S1, S2, S3])
    legend(fig, [("Same offer as last time", S1), ("Different offer, same carrier", S2), ("Different carrier", S3)], ax)
    fig.savefig(BASE / FIGS["next"]); plt.close(fig)

    # 2. Same-offer share for the same recipient
    rows = []
    for s in ["new", "light", "est", "all"]:
        r, ro = D.F["recip"][s], D.F["recip_offer"][s]
        rows.append((D.seg_names[s], ro / r, f"{num(ro)} of {num(r)}"))
    rows += [
        ("Regular purchases only", D.REG["recip_offer"] / D.REG["recip"], f"{num(D.REG['recip_offer'])} of {num(D.REG['recip'])}"),
        ("60-day window", D.W60["recip_offer"] / D.W60["recip"], f"{num(D.W60['recip_offer'])} of {num(D.W60['recip'])}"),
        ("Other recipients in between", D.F["per_recip_offer"]["all"] / D.F["per_recip"]["all"], f"{num(D.F['per_recip_offer']['all'])} of {num(D.F['per_recip']['all'])}"),
    ]
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    hbars(ax, rows, [S1] * len(rows))
    ax.axhline(3.5, color=INK3, linewidth=0.8, linestyle=(0, (1, 2)))
    ax.get_yticklabels()[3].set_fontweight("bold")
    fig.savefig(BASE / FIGS["loyal"]); plt.close(fig)

    # 3. Amount direction
    arows = [(f"After ${s}  ({num(c)})", [d, sm, u]) for s, (c, d, sm, u, av) in D.AMT_ROWS.items()]
    fig, ax = plt.subplots(figsize=(7.0, 2.5))
    stacked_rows(ax, arows, [DOWN, NEUTRAL, S1], min_label=0.08)
    for i, (s, (c, d, sm, u, av)) in enumerate(D.AMT_ROWS.items()):
        ax.text(1.015, i, f"avg next ${av:.2f}", va="center", fontsize=7.5, color=INK3)
    legend(fig, [("Lower amount", DOWN), ("Same amount", NEUTRAL), ("Higher amount", S1)], ax)
    fig.savefig(BASE / FIGS["amount"]); plt.close(fig)

    # 4. Entry point of the repeat
    groups = [
        ("quick-send", ["quick-send"], S1), ("calling-home-quick-send", ["calling-home-quick-send"], S1),
        ("Send-again buttons", ["people-page-quick-send", "chat-send-again", "hub-send-again"], S1),
        ("people-page", ["people-page"], S2), ("recents-people-list", ["recents-people-list"], S2),
        ("People page offers, post-call", ["people-page-offers", "post-call"], S2), ("search", ["search"], S2),
        ('Not tracked ("empty")', ["empty"], "#AFBAC8"),
    ]
    rows, cols = [], []
    for lab, keys, c in groups:
        r, s = D.grp(keys)
        rows.append((lab, s / r, f"{num(s)} of {num(r)}")); cols.append(c)
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    hbars(ax, rows, cols, note_x=1.34)
    legend(fig, [("One-tap repeat", S1), ("Browse the offer list", S2), ("Not tracked", "#AFBAC8")], ax)
    fig.savefig(BASE / FIGS["entry"]); plt.close(fig)

    # 5. Product type and country
    trows = [(k, ro / r, f"{num(ro)} of {num(r)}") for k, (n, r, ro) in D.PTYPE.items()]
    crows = [(k, ro / r, f"{num(ro)} of {num(r)}") for k, (n, r, ro) in sorted(D.CTRY.items(), key=lambda x: -x[1][2] / x[1][1])]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.6), gridspec_kw={"height_ratios": [3, 12], "hspace": 0.35})
    hbars(a1, trows, [S1] * 3)
    a1.set_title("By product type of the previous top-up", loc="left", fontsize=9, color=INK, fontweight="bold")
    hbars(a2, crows, [S1] * len(crows))
    a2.set_title("By destination country (top 12 by buyers)", loc="left", fontsize=9, color=INK, fontweight="bold")
    fig.savefig(BASE / FIGS["where"]); plt.close(fig)

    # 6. Quarter view dumbbell
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    for i, b in enumerate(D.BUCKETS):
        vals = [D.Q_CARR[i], D.Q_OFFERS[i], D.Q_RECIPS[i]]
        ax.plot([min(vals), max(vals)], [i, i], color="#D9E0EA", linewidth=3, solid_capstyle="round", zorder=1)
        for v, c in zip(vals, [S3, S1, S2]):
            ax.scatter(v, i, s=70, color=c, edgecolor="white", linewidth=1.5, zorder=3)
        ax.text(1.02, i, f"{num(D.Q_USERS[i])} buyers", va="center", ha="left", fontsize=7.5, color=INK3,
                transform=ax.get_yaxis_transform())
    ax.set_yticks(range(len(D.BUCKETS)), [f"{b} purchase{'s' if b != '1' else ''}" for b in D.BUCKETS])
    ax.invert_yaxis()
    ax.set_xlim(0, 9)
    ax.set_xlabel("distinct values per buyer, 1 Jul to 27 Sep 2026", fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    legend(fig, [("Distinct carriers", S3), ("Distinct offers", S1), ("Distinct recipients", S2)], ax)
    fig.savefig(BASE / FIGS["quarter"]); plt.close(fig)
    print("figures:", ", ".join(FIGS.values()))


# ---------------------------------------------------------------- content ----

def L(label, url):
    return f"[{label}]({url})"


A = D.AMT_TOT
UP_SHARE = A[3] / (A[1] + A[3])
OT, BR = D.OT, D.BR

KEY_TABLE = [
    ["Finding", "Value", "What it means"],
    ["Same person, same offer", pct(D.RO / D.RECIP),
     f"of repeat top-ups to the same recipient use the exact same offer ID ({num(D.RO)} of {num(D.RECIP)})"],
    ["Same person, same product type", pct(D.RT / D.RECIP),
     "stay on bundle, airtime or data; most of the rest is a different denomination"],
    ["Next top-up, same person", pct(D.RECIP / D.ANY),
     f"of next purchases go to the same recipient; {pct(D.OTHER / D.ANY)} go to someone else"],
    ["Next top-up, same offer", pct(D.OFFER / D.ANY),
     "of next purchases reuse the previous offer, whoever the recipient is"],
]

NEXT_TABLE = [["Next purchase", "Buyers", "Share"]] + [
    [l, num(v), pct(v / D.ANY)] for l, v in D.decomp_rows
] + [["All next purchases within 30 days", num(D.ANY), "100.0%"]]

SWITCH_TABLE = [["Same-recipient repeat", "Buyers", "Share"]] + [
    [l, num(v), pct(v / D.RECIP)] for l, v in D.SAME_RECIP_SPLIT
] + [["All repeat top-ups to the same recipient", num(D.RECIP), "100.0%"]]

AMOUNT_TABLE = [["Previous top-up", "Repeats", "Lower", "Same", "Higher", "Avg next"]] + [
    [L(f"${s}", chart(D.AMOUNT_CID[s])), num(c), pct(d / c), pct(sm / c), pct(u / c), f"${av:.2f}"]
    for s, (c, d, sm, u, av) in D.AMT_ROWS.items()
] + [["Pooled", num(A[0]), pct(A[1] / A[0]), pct(A[2] / A[0]), pct(A[3] / A[0]), ""]]

QUARTER_TABLE = [["Purchases", "Buyers", "Per buyer", "Recipients", "Offers", "Amounts", "Carriers"]] + [
    [b, num(D.Q_USERS[i]), f"{D.Q_PURCH[i] / D.Q_USERS[i]:.2f}", f"{D.Q_RECIPS[i]:.2f}",
     f"{D.Q_OFFERS[i]:.2f}", f"{D.Q_AMT[i]:.2f}", f"{D.Q_CARR[i]:.2f}"]
    for i, b in enumerate(D.BUCKETS)
]

TABLES = {
    "KEY": (KEY_TABLE, [150, 60, 294]),
    "NEXT": (NEXT_TABLE, [334, 90, 80]),
    "SWITCH": (SWITCH_TABLE, [334, 90, 80]),
    "AMOUNT": (AMOUNT_TABLE, [104, 80, 80, 80, 80, 80]),
    "QUARTER": (QUARTER_TABLE, [72, 72, 72, 72, 72, 72, 72]),
}

seg = D.F
BLOCKS = [
    ("title", TITLE),
    ("subtitle", "Buyers keep their offer. What changes is who they top up."),
    ("meta", f"IMTU · Amplitude analysis · 28 Sep 2026 · Source: BR app Prod (650506), "
             f"{L('MTUOrderStatusSuccessScr', D.EVENT_URL)} · Cohort: {num(D.N['all'])} buyers, 1 Jul to 28 Aug 2026 · "
             f"Evidence: {L('Amplitude dashboard fcw7gsdb', D.DASH)} · {L('Web version', ARTIFACT_URL)}"),
    ("p", f"When a BOSS Revolution user tops up the same person again, {pct(D.RO / D.RECIP, 0)} of the time it is the "
          f"exact same offer and {pct(D.RT / D.RECIP, 0)} of the time the same product type. Most offer changes between one "
          "purchase and the next happen because the next top-up is for someone else, often on another carrier."),
    ("table", "KEY"),

    ("h1", "The answer: repeat for the same person, change for a different one"),
    ("p", f"For each buyer, we took their first successful top-up after 30 June and looked at the very next one. "
          f"{pct(D.ANY / D.N['all'], 0)} bought again within 30 days. The next purchase went to the same recipient only "
          f"{pct(D.RECIP / D.ANY, 0)} of the time, and those repeats are highly loyal. Next purchases for a different recipient "
          f"still reuse the same offer {pct(D.OTHER_SAME_OFFER / D.OTHER, 0)} of the time, and "
          f"{pct(D.OTHER_SAME_OFFER / D.OTHER_SAME_CARRIER, 0)} of the time when the new recipient is on the same carrier."),
    ("img", "next"),
    ("cap", f"Figure 1. Where the next top-up went, for {num(D.ANY)} buyers who bought again within 30 days. A third of the "
            f"next top-ups for someone else land on another carrier, where no offer can carry over. Charts: "
            f"{L('any repeat', chart('dmmwysk6'))}, {L('same recipient', chart('as44pz1v'))}, "
            f"{L('same recipient + offer', chart('h5r3f3a0'))}, {L('same offer', chart('g6r3txzr'))}, "
            f"{L('same carrier', chart(D.CARRIER_CID))}, {L('same recipient + carrier', chart('ghgqoyi8'))}."),
    ("table", "NEXT"),

    ("h1", "For the same person, the offer rarely changes"),
    ("p", f"The share of same-recipient repeats that keep the offer ID stays between "
          f"{pct(min(seg['recip_offer'][s] / seg['recip'][s] for s in D.SEGS), 0)} and "
          f"{pct(D.REG['recip_offer'] / D.REG['recip'], 0)} across tenure segments and every robustness check. It is lowest for "
          "new buyers, who are still finding their offer, and highest for established buyers and for regular "
          "(non-subscription) purchases."),
    ("img", "loyal"),
    ("cap", f"Figure 2. Share of repeat top-ups to the same person that used the exact same offer. The three rows below the dotted line are robustness checks on all buyers. Segments by purchases from "
            f"1 April to 29 June 2026: established 3+, light 1-2, new or lapsed 0. Charts: "
            f"{L('regular only, same recipient', chart(D.REG_CID['recip']))}, {L('regular only, same offer', chart(D.REG_CID['recip_offer']))}, "
            f"{L('60 days, same recipient', chart(D.W60_CID['recip']))}, {L('60 days, same offer', chart(D.W60_CID['recip_offer']))}, "
            f"{L('in between allowed, same recipient', chart('p7xgzbsm'))}, {L('in between allowed, same offer', chart('tk7wnx2b'))}."),
    ("p", f"When the offer does change for the same person, it is mostly a different denomination within the same product "
          f"type. Catalog churn and carrier changes are negligible: only {num(D.SAME_AMOUNT_NEW_ID)} switches kept the same "
          f"carrier and amount under a new offer ID, and {num(D.CARRIER_CHANGED)} followed a change of the recipient's carrier "
          f"({L('same recipient, carrier and amount', chart('5mo4xk68'))}, {L('same recipient and carrier', chart('ghgqoyi8'))}, "
          f"{L('same recipient and type', chart('s2n5xug7'))})."),
    ("table", "SWITCH"),

    ("h1", "When the amount changes, it moves both ways"),
    ("p", "We checked the next same-recipient top-up after the five most common USD amounts. Denomination loyalty matches "
          "offer loyalty, and changes show no upward trend."),
    ("img", "amount"),
    ("cap", f"Figure 3. Amount of the next top-up to the same recipient, by the amount of the previous one. "
            f"{pct(A[2] / A[0])} keep the denomination; of the changes, {pct(UP_SHARE)} go up and {pct(1 - UP_SHARE)} go down. "
            "Small amounts tend to move up and large ones down, toward the $10 to $20 band. Each row links to its chart in the table below."),
    ("table", "AMOUNT"),

    ("h1", "Quick-send makes repeating automatic, but browsers repeat too"),
    ("p", "The entry point of the repeat purchase (top_up_started_from, from DCS-4011) shows how much of the loyalty is the "
          "interface and how much is choice. One-tap repeats pre-fill the last order, so they are close to 100% by design. "
          "The browse flows are the cleaner test of preference: the buyer sees the offer list and most still pick the offer "
          "they bought last time."),
    ("img", "entry"),
    ("cap", f"Figure 4. Same recipient, same offer, by where the repeat started. One-tap repeats are "
            f"{pct(OT[0] / D.SRC_TOTAL)} of same-recipient repeats and land on the same offer {pct(OT[1] / OT[0])} of the time. "
            f"Browse flows are {pct(BR[0] / D.SRC_TOTAL)} of repeats and {pct(BR[1] / BR[0])} still pick last time's offer. Charts: "
            f"{L('same recipient by entry point', chart(D.SRC_CID[0]))}, {L('same offer by entry point', chart(D.SRC_CID[1]))}."),

    ("h1", "Where buyers switch more"),
    ("p", "Data packs and a few markets switch more than average. These are the places where the offer list, promotions and "
          "featured offers have the most room to change what people buy."),
    ("img", "where"),
    ("cap", f"Figure 5. Same recipient, same offer, by product type and destination country of the previous top-up. Bundles "
            "are the stickiest and data packs the most switched; Central America repeats most, while Haiti, Jamaica, Nigeria and "
            f"Ethiopia switch most. Charts: {L('type, same recipient', chart(D.PTYPE_CID[0]))}, "
            f"{L('type, same offer', chart(D.PTYPE_CID[1]))}, {L('country, same recipient', chart(D.CTRY_CID[0]))}, "
            f"{L('country, same offer', chart(D.CTRY_CID[1]))}."),

    ("h1", "Over a whole quarter, the same pattern"),
    ("p", f"Across {num(D.TOTAL_Q_USERS)} buyers and {num(D.TOTAL_Q_PURCH)} purchases from 1 July to 27 September, the "
          "average buyer uses fewer distinct offers than they have recipients, whatever their frequency. Among buyers with "
          f"exactly two purchases, {pct(2 - D.Q_OFFERS[1], 0)} bought the same offer twice, even though "
          f"{pct(D.Q_RECIPS[1] - 1, 0)} of them topped up two different people."),
    ("img", "quarter"),
    ("cap", f"Figure 6. Distinct carriers, offers and recipients per buyer, by how many times they bought. A buyer with 13 or "
            f"more purchases tops up 8.4 people but uses only 5.0 offers. Charts: {L('buyers', chart(D.Q_CID['users']))}, "
            f"{L('recipients', chart(D.Q_CID['recips']))}, {L('offers', chart(D.Q_CID['offers']))}, "
            f"{L('carriers', chart(D.Q_CID['carriers']))}, {L('amounts', chart(D.Q_CID['amounts']))}."),
    ("table", "QUARTER"),

    ("h1", "What this means for the product"),
    ("b", ("Put the last offer first in the browse flows",
           f"in the recents list, people page and search, {pct(BR[1] / BR[0], 0)} of same-recipient repeats end on the same "
           "offer after scrolling the full list. Showing \"last sent to this person\" at the top of the offer list would "
           "shorten the path for most of them. Check what the list pre-selects today before building.")),
    ("b", ("Subscriptions automate a habit that already exists",
           f"{num(D.RO)} buyers in this cohort repeated the exact same offer to the same person within 30 days. They are the "
           "natural audience for a subscription offer on that recipient, and the offer to propose is the one they just bought.")),
    ("b", ("Upselling needs a nudge",
           f"denomination changes split {pct(UP_SHARE, 0)} up and {pct(1 - UP_SHARE, 0)} down, so amounts do not rise on their "
           f"own. The {pct(1 - D.RO / D.RECIP, 0)} of same-recipient repeats that already change offer, and the data-pack and "
           "Haiti, Jamaica and Nigeria buyers, are the most open to featured offers and promotions.")),
    ("b", ("Senders have a go-to offer",
           f"{pct(D.OTHER_SAME_OFFER / D.ANY, 0)} of all next purchases send the same offer to a different person on the same "
           "carrier. Promotions set at offer level therefore reach more than one recipient per sender.")),
    ("b", ("Close the measurement gaps",
           "offer-list position and a \"pre-selected\" flag on the order would separate accepted defaults from active choices; "
           f"neither is tracked today (see the {L('IMTU Amplitude events audit', D.AUDIT_URL)}). Subscription renewals are "
           "server-side and never reach Amplitude, so the true repeat rate of the same offer is higher than shown here.")),

    ("h1", "Method and caveats"),
    ("b", ("Pairing each purchase with the next one",
           f"Amplitude funnels with the Nth-time filter on {L('MTUOrderStatusSuccessScr', D.EVENT_URL)}: step 1 is a buyer's "
           "1st purchase counted from 30 June (1-day lookback), step 2 their 2nd, within 30 days. The anchoring was validated: "
           "the \"2nd purchase\" step returned 148,089 users against 145,580 users with 2+ purchases in the same window. Each "
           "buyer contributes one pair, so heavy buyers are not over-weighted.")),
    ("b", ("What \"same\" means",
           "each chart holds one or more properties constant across the two steps: recipient_phone_number, offer_id, "
           "recipient_carrier, offer_amount, offer_type. All are populated on 100% of successful orders in the last 30 days. "
           "Recipient numbers are consistently E.164 (99.96% carry a \"+\" prefix). Offer IDs are carrier SKUs such as "
           "TIGO_GT-US-PAQUETIGO-10 or CLARO_DO_6; amounts are in the sender's currency (98% USD).")),
    ("b", ("Segments",
           f"established = 3+ purchases from 1 April to 29 June 2026 ({num(D.N['est'])} buyers), light = 1-2 "
           f"({num(D.N['light'])}), new or lapsed = none ({num(D.N['new'])}).")),
    ("b", ("Not covered",
           "the Money app (project 420385), subscription renewals (server-side, not in Amplitude) and anything before July "
           "2026. Subscription creations are 25% of successful orders in the last 30 days; excluding them raises same-recipient "
           f"loyalty from {pct(D.RO / D.RECIP)} to {pct(D.REG['recip_offer'] / D.REG['recip'])}. The Tableau connector failed to "
           "connect when this was built, so the analysis uses Amplitude only. The \"empty\" entry point is a known tracking "
           f"defect listed in the {L('events audit', D.AUDIT_URL)}.")),
]

STYLE = {"title": "TITLE", "subtitle": "SUBTITLE", "meta": "NORMAL_TEXT", "h1": "HEADING_1",
         "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "cap": "NORMAL_TEXT"}
SIZE = {"title": 22, "subtitle": 14, "meta": 8.5, "h1": 15, "p": 10.5, "b": 10.5, "cap": 8.5}
SPACE = {"title": (0, 2), "subtitle": (0, 6), "meta": (0, 10), "h1": (16, 6), "p": (0, 8), "b": (0, 5), "cap": (2, 10)}

MARK = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)")


def parse_marks(s):
    """Return (plain_text, links[(start,end,url)], bolds[(start,end)]) with offsets into plain_text."""
    out, links, bolds, pos = [], [], [], 0
    for m in MARK.finditer(s):
        out.append(s[pos:m.start()])
        start = sum(len(x) for x in out)
        if m.group(1) is not None:
            out.append(m.group(1)); bolds.append((start, start + len(m.group(1))))
        else:
            out.append(m.group(2)); links.append((start, start + len(m.group(2)), m.group(3)))
        pos = m.end()
    out.append(s[pos:])
    return "".join(out), links, bolds


def utf16(s):
    return len(s.encode("utf-16-le")) // 2


# --------------------------------------------------------------- Docs API ----

def get_credentials():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def hexrgb(h):
    return {"color": {"rgbColor": {"red": int(h[1:3], 16) / 255, "green": int(h[3:5], 16) / 255,
                                   "blue": int(h[5:7], 16) / 255}}}


def link_style(start, end, url):
    return {"updateTextStyle": {"range": {"startIndex": start, "endIndex": end},
                                "textStyle": {"link": {"url": url}}, "fields": "link"}}


def build_requests(blocks):
    reqs, cur = [], 1
    for kind, text in blocks:
        if kind in ("table", "img"):
            line = f"[[{kind.upper()}:{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += utf16(line)
            continue
        lead = None
        if isinstance(text, tuple):
            lead, body = text
            text = f"**{lead}:** {body}"
        plain, links, bolds = parse_marks(text)
        line = plain + "\n"
        n = utf16(line)
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        above, below = SPACE[kind]
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + n},
            "paragraphStyle": {"namedStyleType": STYLE[kind],
                               "spaceAbove": {"magnitude": above, "unit": "PT"},
                               "spaceBelow": {"magnitude": below, "unit": "PT"},
                               "lineSpacing": 115 if kind in ("p", "b") else 100},
            "fields": "namedStyleType,spaceAbove,spaceBelow,lineSpacing"}})
        if kind == "b":
            reqs.append({"createParagraphBullets": {"range": {"startIndex": cur, "endIndex": cur + n},
                                                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        style = {"fontSize": {"magnitude": SIZE[kind], "unit": "PT"}}
        fields = "fontSize"
        if kind in ("meta", "cap"):
            style["foregroundColor"] = hexrgb(INK3 if kind == "meta" else INK2)
            fields += ",foregroundColor"
        if kind == "subtitle":
            style["foregroundColor"] = hexrgb(INK2)
            fields += ",foregroundColor"
        reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + n - 1},
                                         "textStyle": style, "fields": fields}})
        for s, e in bolds:
            a, b = cur + utf16(plain[:s]), cur + utf16(plain[:e])
            reqs.append({"updateTextStyle": {"range": {"startIndex": a, "endIndex": b},
                                             "textStyle": {"bold": True}, "fields": "bold"}})
        for s, e, url in links:
            reqs.append(link_style(cur + utf16(plain[:s]), cur + utf16(plain[:e]), url))
        cur += n
    return reqs


def batched(docs, doc_id, reqs, size=40):
    for i in range(0, len(reqs), size):
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": reqs[i:i + size]}).execute()
        time.sleep(0.25)


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "") for e in el["paragraph"]["elements"])


def find_placeholder(docs, doc_id, marker):
    doc = docs.documents().get(documentId=doc_id).execute()
    for el in doc["body"]["content"]:
        if para_text(el).strip() == marker:
            return el["startIndex"], utf16(para_text(el))
    return None, None


def insert_image(docs, doc_id, key):
    from PIL import Image
    fname = FIGS[key]
    idx, plen = find_placeholder(docs, doc_id, f"[[IMG:{key}]]")
    if idx is None:
        print(f"  ! placeholder IMG:{key} not found")
        return
    with Image.open(BASE / fname) as im:
        height = round(IMG_W * im.height / im.width, 1)
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx, "endIndex": idx + plen - 1}}},
        {"insertInlineImage": {"location": {"index": idx}, "uri": RAW_BASE + fname,
                               "objectSize": {"width": {"magnitude": IMG_W, "unit": "PT"},
                                              "height": {"magnitude": height, "unit": "PT"}}}},
        {"updateParagraphStyle": {"range": {"startIndex": idx, "endIndex": idx + 1},
                                  "paragraphStyle": {"alignment": "CENTER",
                                                     "spaceAbove": {"magnitude": 6, "unit": "PT"},
                                                     "spaceBelow": {"magnitude": 2, "unit": "PT"}},
                                  "fields": "alignment,spaceAbove,spaceBelow"}},
    ]}).execute()
    time.sleep(0.6)
    print(f"  image {key}: ok")


def insert_table(docs, doc_id, key):
    data, widths = TABLES[key]
    idx, plen = find_placeholder(docs, doc_id, f"[[TABLE:{key}]]")
    if idx is None:
        print(f"  ! placeholder TABLE:{key} not found")
        return
    rows, cols = len(data), len(data[0])
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx, "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx}, "rows": rows, "columns": cols}},
    ]}).execute()
    time.sleep(1.0)
    doc = docs.documents().get(documentId=doc_id).execute()
    table_el = next(el for el in doc["body"]["content"] if "table" in el and el["startIndex"] >= idx - 2)
    t_start = table_el["startIndex"]
    cells = [(cell["content"][0]["startIndex"], r, c)
             for r, row in enumerate(table_el["table"]["tableRows"])
             for c, cell in enumerate(row["tableCells"])]
    total_row = data[-1][0].startswith(("All ", "Pooled"))
    numeric_from = 1 if key != "KEY" else 99
    reqs = []
    for start, r, c in sorted(cells, reverse=True):      # reverse keeps indices valid
        plain, links, _ = parse_marks(data[r][c])
        if not plain:
            continue
        n = utf16(plain)
        reqs.append({"insertText": {"location": {"index": start}, "text": plain}})
        style = {"fontSize": {"magnitude": 9, "unit": "PT"}}
        fields = "fontSize"
        if r == 0 or (total_row and r == rows - 1) or (key == "KEY" and c == 1):
            style["bold"] = True
            fields += ",bold"
        reqs.append({"updateTextStyle": {"range": {"startIndex": start, "endIndex": start + n},
                                         "textStyle": style, "fields": fields}})
        for s, e, url in links:
            reqs.append(link_style(start + utf16(plain[:s]), start + utf16(plain[:e]), url))
        para = {"spaceAbove": {"magnitude": 0, "unit": "PT"}, "spaceBelow": {"magnitude": 0, "unit": "PT"},
                "lineSpacing": 100}
        pfields = "spaceAbove,spaceBelow,lineSpacing"
        if c >= numeric_from:
            para["alignment"] = "END"
            pfields += ",alignment"
        reqs.append({"updateParagraphStyle": {"range": {"startIndex": start, "endIndex": start + n},
                                              "paragraphStyle": para, "fields": pfields}})
    batched(docs, doc_id, reqs)

    style_reqs = []
    for r in range(rows):
        fill = "#EDF1F6" if r == 0 or (total_row and r == rows - 1) else None
        for c in range(cols):
            cs = {"paddingTop": {"magnitude": 3, "unit": "PT"}, "paddingBottom": {"magnitude": 3, "unit": "PT"},
                  "paddingLeft": {"magnitude": 5, "unit": "PT"}, "paddingRight": {"magnitude": 5, "unit": "PT"}}
            f = "paddingTop,paddingBottom,paddingLeft,paddingRight"
            if fill:
                cs["backgroundColor"] = hexrgb(fill)
                f += ",backgroundColor"
            style_reqs.append({"updateTableCellStyle": {
                "tableRange": {"tableCellLocation": {"tableStartLocation": {"index": t_start},
                                                     "rowIndex": r, "columnIndex": c},
                               "rowSpan": 1, "columnSpan": 1},
                "tableCellStyle": cs, "fields": f}})
    for c, w in enumerate(widths):
        style_reqs.append({"updateTableColumnProperties": {
            "tableStartLocation": {"index": t_start}, "columnIndices": [c],
            "tableColumnProperties": {"widthType": "FIXED_WIDTH", "width": {"magnitude": w, "unit": "PT"}},
            "fields": "widthType,width"}})
    batched(docs, doc_id, style_reqs)
    print(f"  table {key}: ok")


def clear_body(docs, doc_id):
    doc = docs.documents().get(documentId=doc_id).execute()
    end = doc["body"]["content"][-1]["endIndex"]
    if end > 2:
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
            {"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1}}}]}).execute()
        time.sleep(0.5)


def main(doc_id=None):
    from googleapiclient.discovery import build
    from linkify_refs import LINK_MAP, linkify

    for f in FIGS.values():
        assert (BASE / f).exists(), f"missing {f}: run with --figures, then commit and push"
    for kind, text in BLOCKS:
        assert "—" not in str(text), f"em dash in {kind}"

    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    if doc_id:
        clear_body(docs, doc_id)
        print(f"Rebuilding doc in place: {doc_id}")
    else:
        doc_id = docs.documents().create(body={"title": TITLE}).execute()["documentId"]
        print(f"Created doc: {doc_id}")

    m = {"magnitude": MARGIN_PT, "unit": "PT"}
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [{"updateDocumentStyle": {
        "documentStyle": {"marginTop": m, "marginBottom": m, "marginLeft": m, "marginRight": m},
        "fields": "marginTop,marginBottom,marginLeft,marginRight"}}]}).execute()

    batched(docs, doc_id, build_requests(BLOCKS))
    print("Inserted text blocks")
    for key in TABLES:
        insert_table(docs, doc_id, key)
    for key in FIGS:
        insert_image(docs, doc_id, key)

    linkify(docs, doc_id, dict(LINK_MAP))
    print("Linkified references")

    existing = drive.permissions().list(fileId=doc_id, fields="permissions(type,domain)").execute()
    if not any(p.get("type") == "domain" and p.get("domain") == "idt.net" for p in existing.get("permissions", [])):
        drive.permissions().create(fileId=doc_id, body={"role": "writer", "type": "domain", "domain": "idt.net"}).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    if "--figures" in sys.argv:
        draw_figures()
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else None)
