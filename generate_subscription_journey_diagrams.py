#!/usr/bin/env python3
"""
Five flowcharts for the IMTU subscription journey investigation.

  1. imtu_journey_1_current.png      — the current end-to-end journey
  2. imtu_journey_2_variants.png     — every variant, and what is actually live
  3. imtu_journey_3_immediate.png    — immediate cancellation (<=24h)
  4. imtu_journey_4_delayed.png      — delayed cancellation, by cadence
  5. imtu_journey_5_future.png       — recommended future state

Every figure on these charts is traceable to Amplitude project 650506 or to a
Jira key, and is carried in the accompanying report. Numbers reflect the
adversarially-verified evidence base of 2026-08-30 — notably 30-day cancellation
at 29.10% (not the 12.7% previously in circulation, which was right-censored).

Visual language matches generate_subscription_flow_diagrams.py.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

GRAY = dict(fill="#EEEBE5", edge="#A8A29A", text="#454340")
TEAL = dict(fill="#E3F1EA", edge="#1E7A5E", text="#186B51")
AMBER = dict(fill="#FAEBD9", edge="#C4841F", text="#8F5E0E")
RED = dict(fill="#FBE9E9", edge="#C05050", text="#9E3232")
BLUE = dict(fill="#E6EEF7", edge="#3F6FA8", text="#2C5384")
VIOLET = dict(fill="#EFEAF7", edge="#6B4FA8", text="#4E3684")
ARROW = "#7A7A7A"


def box(ax, cx, cy, w, h, title, sub=None, style=GRAY, ts=10.5, ss=8.2):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.14",
        linewidth=1.4, facecolor=style["fill"], edgecolor=style["edge"], zorder=2))
    if sub:
        ax.text(cx, cy + h * 0.20, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=style["text"], zorder=3)
        ax.text(cx, cy - h * 0.23, sub, ha="center", va="center",
                fontsize=ss, color=style["text"], alpha=0.88, zorder=3)
    else:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=style["text"], zorder=3)


def diamond(ax, cx, cy, w, h, label, size=9.5, style=GRAY):
    ax.add_patch(Polygon(
        [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
        closed=True, linewidth=1.4,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=2))
    ax.text(cx, cy, label, ha="center", va="center",
            fontsize=size, color=style["text"], zorder=3)


def arrow(ax, p0, p1, label=None, lpos=0.5, ldx=0.0, ldy=0.14, dashed=False,
          lsize=8.2, rad=0.0, color=None):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=12,
        linewidth=1.2, color=color or ARROW, zorder=1,
        linestyle="--" if dashed else "-",
        connectionstyle=f"arc3,rad={rad}"))
    if label:
        mx = p0[0] + (p1[0] - p0[0]) * lpos + ldx
        my = p0[1] + (p1[1] - p0[1]) * lpos + ldy
        ax.text(mx, my, label, ha="center", va="center", fontsize=lsize,
                color="#6A6A6A", zorder=4,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.93))


def canvas(fig_w, h, title, subtitle, legend, xmax=20):
    fig, ax = plt.subplots(figsize=(fig_w, fig_w * h / xmax))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.text(xmax / 2, h - 0.5, title, ha="center", va="center",
            fontsize=17, fontweight="bold", color="#232320")
    ax.text(xmax / 2, h - 1.15, subtitle, ha="center", va="center",
            fontsize=9.5, color="#6A6A6A")
    ax.text(xmax / 2, 0.32, legend, ha="center", va="center",
            fontsize=8.3, color="#8A8A8A")
    return fig, ax


def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


LEG_STD = ("Gray = system / screen     Teal = positive outcome     Amber = friction / alternate     "
           "Red = churn / defect     Blue = measurement     Violet = not shipped")


# ============================================================ 1. CURRENT ====
def current():
    H = 21
    fig, ax = canvas(18, H, "Diagram 1 — Current IMTU Subscription Journey (as measured)",
                     "Amplitude project 650506, Aug 2026 unless stated. Percentages carry their denominators. "
                     "Dashed = the step exists but emits no event.", LEG_STD)
    XA, XAB = 4.6, 9.4
    XB, XBB = 14.0, 18.2
    W, BW = 5.2, 3.2

    yA = [18.4, 16.2, 13.9, 11.5, 9.2, 6.9, 4.3]

    box(ax, XA, yA[0], W, 1.5, "1 · Offer list", "MTUOfferListScr\n≥70.6% of selections unrecorded", style=BLUE)

    box(ax, XA, yA[1], W, 1.6, "2 · Order screen — toggle shown",
        "MTUOrderScr · 1,152,462 events (Aug)\n18.98% carry no toggle state", style=GRAY)
    arrow(ax, (XA, yA[0] - 0.75), (XA, yA[1] + 0.8))

    diamond(ax, XA, yA[2], 5.2, 1.9, "3 · Default state?\n(not randomised)", size=9)
    arrow(ax, (XA, yA[1] - 0.8), (XA, yA[2] + 0.95))

    box(ax, XAB, yA[2], BW + 0.4, 1.7, "Default OFF",
        "69,475 users → 5.45% attach\nopt-in 6.51% per exposure", style=AMBER, ss=7.8)
    arrow(ax, (XA + 2.6, yA[2]), (XAB - 1.8, yA[2]), label="OFF")

    box(ax, XA, yA[3], W, 1.7, "Default ON",
        "208,950 users → 62.60% attach\nopt-out 49.13% per exposure", style=RED, ss=7.8)
    arrow(ax, (XA, yA[2] - 0.95), (XA, yA[3] + 0.85), label="ON")

    box(ax, XA, yA[4], W, 1.7, "4 · Toggle interaction",
        "57.20% never touch it at all\n89.63% of engagements end OFF", style=AMBER, ss=7.8)
    arrow(ax, (XA, yA[3] - 0.85), (XA, yA[4] + 0.85))

    box(ax, XAB, yA[4], BW + 0.4, 1.7, "Smart-hide (LIVE)",
        "DCS-4854 · after 3 off-toggles\nthe toggle stops being shown", style=AMBER, ss=7.8)
    arrow(ax, (XA + W / 2, yA[4]), (XAB - 1.8, yA[4]), dashed=True)

    box(ax, XA, yA[5], W, 1.7, "5 · Complete order",
        "MTUOrderCompleteBtn · 849,390 (Aug)\nattach 25.98% (wk 24 Aug), peak 45.49%", style=GRAY, ss=7.8)
    arrow(ax, (XA, yA[4] - 0.85), (XA, yA[5] + 0.85))

    box(ax, XA, yA[6], W, 1.7, "6 · Cadence auto-derived",
        "From offer validity, NOT chosen\n1–7d validity → 7-day billing", style=RED, ss=7.8)
    arrow(ax, (XA, yA[5] - 0.85), (XA, yA[6] + 0.85))

    ax.text(XA, 2.4, "▶  continues in the right-hand column", ha="center",
            fontsize=9.5, style="italic", color="#1E7A5E")

    # column B
    yB = [17.6, 15.2, 12.8, 10.4, 7.9, 5.4, 2.9]
    ax.text(XB, 18.9, "(continued)", ha="center", fontsize=9.5, style="italic", color="#8A8A8A")

    box(ax, XB, yB[0], W, 1.7, "7 · Order outcome",
        "Success 686,314 · Failed 133,778 · Queued 12,308\n~2.0% reach no outcome screen at all", style=GRAY, ss=7.8)

    box(ax, XB, yB[1], W, 1.6, "8 · Renewal charge",
        "NO EVENT EXISTS — /renew/ and /recurr/\nreturn zero across 1,500 event names", style=BLUE, ss=7.8)
    arrow(ax, (XB, yB[0] - 0.85), (XB, yB[1] + 0.8), dashed=True)

    box(ax, XB, yB[2], W, 1.6, "9 · Renewal reminder",
        "DCS-4983 · charge date − 2 days\nReceipt unobservable — no event", style=BLUE, ss=7.8)
    arrow(ax, (XB, yB[1] - 0.8), (XB, yB[2] + 0.8), dashed=True)

    diamond(ax, XB, yB[3], 5.0, 1.9, "10 · Payment\nsucceeds?", size=9)
    arrow(ax, (XB, yB[2] - 0.8), (XB, yB[3] + 0.95))

    box(ax, XBB, yB[3], BW - 0.2, 1.8, "Fails silently",
        "No dunning ladder.\nNever auto-cancels\n(DTCBE-623). No message\non any channel (CRMC-3299)", style=RED, ss=7.4)
    arrow(ax, (XB + 2.5, yB[3]), (XBB - 1.5, yB[3]), label="no")

    box(ax, XB, yB[4], W, 1.7, "11 · Cancellation",
        "5 taps · Yes/No dialog only\nNo reason captured · ~1–4% tap No", style=RED, ss=7.8)
    arrow(ax, (XB, yB[3] - 0.95), (XB, yB[4] + 0.85), label="yes")

    box(ax, XB, yB[5], W, 1.8, "12 · Cancelled",
        "29.10% within 30 days (n=342,130)\n9.62% within 24h · median 11.87 d", style=RED, ss=7.8)
    arrow(ax, (XB, yB[4] - 0.85), (XB, yB[5] + 0.9))

    box(ax, XB, yB[6], W, 1.8, "13 · After cancelling",
        "45.3% return to one-time top-ups\nDemand persists — the mechanic was rejected", style=TEAL, ss=7.8)
    arrow(ax, (XB, yB[5] - 0.9), (XB, yB[6] + 0.9))

    save(fig, "imtu_journey_1_current.png")


# =========================================================== 2. VARIANTS ====
def variants():
    H = 19
    fig, ax = canvas(18, H, "Diagram 2 — Variants and Targeting Changes: what is actually live",
                     "Jira status as of 2026-08-30. The brief assumed the limiting variants had launched; "
                     "the two central ones have not.",
                     "Teal = LIVE in production     Amber = merged to feature branch only     "
                     "Violet = specified, not shipped     Red = contested or defective")

    ax.text(4.6, 17.4, "LIVE", ha="center", fontsize=12, fontweight="bold", color="#186B51")
    ax.text(11.6, 17.4, "FEATURE BRANCH ONLY", ha="center", fontsize=12, fontweight="bold", color="#8F5E0E")
    ax.text(17.4, 17.4, "NOT SHIPPED", ha="center", fontsize=12, fontweight="bold", color="#4E3684")

    live = [
        ("V1 toggle — default ON", "Effectively 100% of traffic\nAttach peaked 45.49% wk 22 Jun,\nnow 25.98% — 11 weeks of decline", 15.9, 2.3),
        ("Targeting predicate", "CONTESTED — two incompatible\nreadings (§3.1). Resolve before\nDCS-5289 leaves QA", 13.2, 2.3),
        ("Smart-hide · DCS-4854", "Hides toggle after 3 off-toggles.\nResolved 2026-07-08. The ONLY\ncompleted post-launch change", 10.5, 2.3),
        ("Duplicate warning · DCS-5224", "Re-added 2026-08-13, reversing\nDCS-4428 which removed it\n2026-04-21. Same element, 4 months", 7.8, 2.3),
        ("Renewal reminder · DCS-4983", "Moved to charge date − 2 days,\n2026-07-16. Shifts WHEN people\ncancel, not WHETHER", 5.1, 2.3),
    ]
    for i, (t, s, y, h) in enumerate(live):
        # the predicate is live but its definition is contested — colour it as such
        st = RED if t == "Targeting predicate" else TEAL
        box(ax, 4.6, y, 5.4, h, t, s, style=st, ts=10, ss=7.6)

    box(ax, 4.6, 2.5, 5.4, 1.7, "No rollout record exists",
        "No ticket among 90 children of\nDCS-3818 / 4707 / 5297 records a\nrollout %, cohort size or wave date", style=RED, ts=10, ss=7.6)

    feat = [
        ("DCS-5277 · consent fix", "Subscription created with NO\nconsent. Critical, 100% repro.\nQA task closed “Won't fix” in 33s", 15.9, 2.3, RED),
        ("DCS-5172 · insurance flag", "In insurance_priority mode the\nsubscription toggle is HIDDEN\nwhile default may still be ON", 13.2, 2.3, AMBER),
        ("DCS-5182 · resubscribe", "Hide toggle on resubscribe —\nreverses DCS-4205 (Mar 2026)", 10.7, 1.9, AMBER),
        ("DCS-5205 · resubscribe btn", "Hide resubscribe when offer\nnot subscription-eligible", 8.4, 1.9, AMBER),
    ]
    for t, s, y, h, st in feat:
        box(ax, 11.6, y, 5.0, h, t, s, style=st, ts=10, ss=7.6)

    box(ax, 11.6, 5.6, 5.0, 2.0, "“READY-IN-FEAT” is not shipped",
        "Jira files it under Done, but it\nmeans merged to a feature branch.\nQA is recorded “on DEV”.", style=RED, ts=10, ss=7.6)

    notship = [
        ("DCS-5289", "Default OFF at ≥1 active\nsubscription.\nQA Available — NOT LIVE", 15.9, 2.1),
        ("DCS-5297 · V2 epic", "Payment-bar toggle,\nV2 events, V2 A/B harness.\nAll To Do", 13.2, 2.1),
        ("DCS-5257 / 5258", "Enhanced cancellation flow\n(4 retention variants).\nTo Do, unassigned", 10.6, 2.1),
        ("DCS-5300 / 5301", "V2 Amplitude events —\nstill to be DEFINED.\nTo Do", 8.0, 2.1),
        ("DCS-4461 / 4463", "Change payment method on\nan existing subscription.\nHigh, both unassigned", 5.4, 2.1),
    ]
    for t, s, y, h in notship:
        box(ax, 17.4, y, 4.4, h, t, s, style=VIOLET, ts=10, ss=7.4)

    ax.text(17.4, 2.7, "3 cancellation children\nabandoned Won't fix\n(DCS-4900 · 5066 · 5100)",
            ha="center", fontsize=8.4, style="italic", color="#9E3232")

    save(fig, "imtu_journey_2_variants.png")


# ========================================================== 3. IMMEDIATE ====
def immediate():
    H = 18
    fig, ax = canvas(16, H, "Diagram 3 — Immediate Cancellation (within 24 hours)",
                     "9.62% of subscription purchasers cancel inside 24h — 32,925 of 342,130 users, "
                     "purchases Mar–Jul 2026. Median 175 seconds.", LEG_STD)
    X = 5.6
    XR = 13.2
    W = 6.0

    y = [15.9, 13.6, 11.3, 9.0, 6.7, 4.3, 2.1]

    box(ax, X, y[0], W, 1.7, "Order completes with subscription attached",
        "Often without the customer registering it:\n57.20% never touched the toggle", style=GRAY, ss=8)

    box(ax, X, y[1], W, 1.7, "Discovery moment",
        "Order-confirmation screen, receipt,\nemail or SMS — the subscription becomes visible", style=AMBER, ss=8)
    arrow(ax, (X, y[0] - 0.85), (X, y[1] + 0.85))

    box(ax, X, y[2], W, 1.7, "Immediate hunt for the cancel control",
        "IMTU Home → My Top-Up Activity → Edit →\nCancel → Confirm. Five taps.", style=GRAY, ss=8)
    arrow(ax, (X, y[1] - 0.85), (X, y[2] + 0.85))

    diamond(ax, X, y[3], 5.4, 1.8, "Yes / No dialog", size=10)
    arrow(ax, (X, y[2] - 0.85), (X, y[3] + 0.9))
    box(ax, XR, y[3], 4.4, 1.5, "Taps “No”", "~1–4% only.\nA mis-tap guard,\nnot retention", style=TEAL, ss=7.8)
    arrow(ax, (X + 2.7, y[3]), (XR - 2.2, y[3]))

    box(ax, X, y[4], W, 1.7, "Cancelled — median 175 seconds",
        "16.9% of ALL 30-day cancellers act inside the first hour\nNo reason is captured. Nothing is learned.", style=RED, ss=8)
    arrow(ax, (X, y[3] - 0.9), (X, y[4] + 0.85), label="Yes")

    box(ax, X, y[5], W, 1.6, "Interpretation",
        "A 2.9-minute median is not deliberation.\nThis is undo, not churn.", style=RED, ss=8)
    arrow(ax, (X, y[4] - 0.85), (X, y[5] + 0.8))

    box(ax, XR, y[5], 4.4, 1.9, "The open question",
        "Genuine regret, or promo\ncapture-then-cancel?\nDCS-5293 asks exactly this\nand is To Do — not known", style=VIOLET, ss=7.6)
    arrow(ax, (X + W / 2, y[5]), (XR - 2.2, y[5]), dashed=True)

    box(ax, X, y[6], W, 1.5, "What would settle it",
        "A cancellation-reason property with an explicit\n“I didn't mean to subscribe” option", style=BLUE, ss=8)
    arrow(ax, (X, y[5] - 0.8), (X, y[6] + 0.75))

    save(fig, "imtu_journey_3_immediate.png")


# ============================================================ 4. DELAYED ====
def delayed():
    H = 18
    fig, ax = canvas(17, H, "Diagram 4 — Delayed Cancellation: the charge date drives it",
                     "Cadence is the strongest measured driver. Weekly cancels at roughly twice the monthly rate, "
                     "and both spike precisely at the renewal boundary.", LEG_STD)

    XW, XM = 5.0, 13.4
    W = 6.4

    ax.text(XW, 15.9, "WEEKLY CADENCE", ha="center", fontsize=12, fontweight="bold", color="#9E3232")
    ax.text(XM, 15.9, "MONTHLY CADENCE", ha="center", fontsize=12, fontweight="bold", color="#2C5384")

    box(ax, XW, 14.4, W, 1.4, "Auto-derived from 1–7 day offer validity",
        "~27% of subscription-bearing orders", style=RED, ss=7.8)
    box(ax, XM, 14.4, W, 1.4, "Auto-derived from longer validity",
        "The larger share of the base", style=BLUE, ss=7.8)

    box(ax, XW, 12.3, W, 1.7, "Quiet days 1–4",
        "Below-baseline cancellation.\nThe customer has not been charged again yet.", style=GRAY, ss=7.8)
    arrow(ax, (XW, 14.4 - 0.7), (XW, 12.3 + 0.85))
    box(ax, XM, 12.3, W, 1.7, "Flat for 28 days",
        "No day-7 spike at all\n(day-7 bin 977 vs ~800 baseline)", style=GRAY, ss=7.8)
    arrow(ax, (XM, 14.4 - 0.7), (XM, 12.3 + 0.85))

    box(ax, XW, 10.1, W, 1.6, "Reminder at charge − 2 days",
        "DCS-4983 · day-5 share rose 5.64% → 12.66%", style=AMBER, ss=7.8)
    arrow(ax, (XW, 12.3 - 0.85), (XW, 10.1 + 0.8))
    box(ax, XM, 10.1, W, 1.6, "Reminder at charge − 2 days",
        "Same mechanism, 28 days later", style=AMBER, ss=7.8)
    arrow(ax, (XM, 12.3 - 0.85), (XM, 10.1 + 0.8))

    box(ax, XW, 7.9, W, 1.7, "DAY 7 — the charge lands",
        "Peak is 19.3× the non-boundary baseline.\n8 boundary days hold 47.9% of 60-day cancellers", style=RED, ss=7.8)
    arrow(ax, (XW, 10.1 - 0.8), (XW, 7.9 + 0.85))
    box(ax, XM, 7.9, W, 1.7, "DAYS 29–32 — the charge lands",
        "35.9% of monthly cancellers, at 12.2× baseline.\nMedian cancel at 29.96 days", style=RED, ss=7.8)
    arrow(ax, (XM, 10.1 - 0.8), (XM, 7.9 + 0.85))

    box(ax, XW, 5.8, W, 1.5, "Repeats every 7 days",
        "A comb, not a decay curve", style=RED, ss=7.8)
    arrow(ax, (XW, 7.9 - 0.85), (XW, 5.8 + 0.75))
    arrow(ax, (XW - W / 2, 5.8), (XW - W / 2 - 0.9, 8.7), rad=0.45, dashed=True)

    box(ax, XM, 5.8, W, 1.5, "30-day cancellation 24.79%",
        "vs weekly 48.60% (Jun–Jul)", style=BLUE, ss=7.8)
    arrow(ax, (XM, 7.9 - 0.85), (XM, 5.8 + 0.75))

    box(ax, 9.2, 3.5, 12.0, 1.8, "The charge is the trigger — but the charge itself is invisible",
        "No renewal event exists anywhere in the 1,500-event tracking plan. The spike is inferred from cancellation timing\n"
        "against the known cadence, not observed directly. Reminder RECEIPT is equally unobservable.", style=BLUE, ss=8)
    arrow(ax, (XW, 5.8 - 0.75), (7.0, 3.5 + 0.9), rad=-0.1)
    arrow(ax, (XM, 5.8 - 0.75), (11.4, 3.5 + 0.9), rad=0.1)

    box(ax, 9.2, 1.5, 12.0, 1.3, "The reminder moves timing, not outcome",
        "Rate moved +0.46 pp; median shifted ~1 day earlier. It warns people in time to cancel — it does not persuade them to stay.",
        style=AMBER, ss=8)
    arrow(ax, (9.2, 3.5 - 0.9), (9.2, 1.5 + 0.65))

    save(fig, "imtu_journey_4_delayed.png")


# ============================================================= 5. FUTURE ====
def future():
    H = 21
    fig, ax = canvas(18, H, "Diagram 5 — Recommended Future-State Journey",
                     "Consent-first creation, cadence chosen not derived, and a cancellation flow that offers a real "
                     "alternative — without obstructing cancellation.",
                     "Teal = new capability     Blue = instrumentation     Amber = alternative to cancelling     "
                     "Red = cancellation proceeds     Gray = unchanged")

    XA, XAB = 4.6, 9.4
    XB, XBB = 14.0, 18.2
    W, BW = 5.2, 3.3

    yA = [18.4, 16.1, 13.8, 11.4, 9.0, 6.6, 4.2]

    box(ax, XA, yA[0], W, 1.6, "1 · Offer list — instrumented",
        "Close the ≥70.6% selection gap\nso funnel entry is measurable", style=BLUE, ss=7.8)

    box(ax, XA, yA[1], W, 1.7, "2 · Toggle shown — and logged as shown",
        "Emit MTUSubscriptionToggleShown with the\ndefault REASON (duplicate/cap/experiment/default)", style=BLUE, ss=7.8)
    arrow(ax, (XA, yA[0] - 0.8), (XA, yA[1] + 0.85))

    box(ax, XA, yA[2], W, 1.7, "3 · Never create without a shown toggle",
        "Hard guard. Closes DCS-5277 and the\nuntested smart-hide path (DCS-4854)", style=RED, ss=7.8)
    arrow(ax, (XA, yA[1] - 0.85), (XA, yA[2] + 0.85))

    box(ax, XA, yA[3], W, 1.8, "4 · Cadence CHOSEN, not derived",
        "Stop defaulting weekly from 7-day validity.\nExplicit choosers prefer 90-day by ~41×\nWeekly cancels 48.60% vs monthly 24.79%", style=TEAL, ss=7.6)
    arrow(ax, (XA, yA[2] - 0.85), (XA, yA[3] + 0.9))

    box(ax, XAB, yA[3], BW, 1.6, "Guardrail per RECIPIENT",
        "not per account —\n3 recipients is 3 legitimate\nsubscriptions", style=TEAL, ss=7.6)
    arrow(ax, (XA + W / 2, yA[3]), (XAB - 1.65, yA[3]), dashed=True)

    box(ax, XA, yA[4], W, 1.7, "5 · Confirmation states the commitment",
        "Amount, cadence, next charge date, and how\nto cancel — in the same medium it was sold", style=TEAL, ss=7.8)
    arrow(ax, (XA, yA[3] - 0.9), (XA, yA[4] + 0.85))

    box(ax, XA, yA[5], W, 1.7, "6 · Renewal + reminder — both emit events",
        "Server-side renewal event, and\nsubscription=true on MarketingTxnFailed", style=BLUE, ss=7.8)
    arrow(ax, (XA, yA[4] - 0.85), (XA, yA[5] + 0.85))

    box(ax, XA, yA[6], W, 1.7, "7 · Failed payment → dunning",
        "Retry ladder + a message on a real channel.\nToday: nothing, on any channel (CRMC-3299)", style=TEAL, ss=7.8)
    arrow(ax, (XA, yA[5] - 0.85), (XA, yA[6] + 0.85))

    ax.text(XA, 2.3, "▶  continues in the right-hand column", ha="center",
            fontsize=9.5, style="italic", color="#1E7A5E")

    yB = [17.6, 15.3, 12.9, 10.5, 8.1, 5.7, 3.2]
    ax.text(XB, 18.9, "(continued)", ha="center", fontsize=9.5, style="italic", color="#8A8A8A")

    box(ax, XB, yB[0], W, 1.6, "8 · Cancel entry — unchanged depth",
        "Keep it easy to find. Do not add steps.", style=GRAY, ss=7.8)

    box(ax, XB, yB[1], W, 1.7, "9 · Skippable reason capture",
        "With an explicit “I didn't mean to subscribe”.\nThe single most valuable missing property", style=BLUE, ss=7.8)
    arrow(ax, (XB, yB[0] - 0.8), (XB, yB[1] + 0.85))

    diamond(ax, XB, yB[2], 5.2, 1.9, "10 · Offer ONE\nalternative?", size=9.5)
    arrow(ax, (XB, yB[1] - 0.85), (XB, yB[2] + 0.95))
    box(ax, XBB, yB[2], BW, 1.9, "Skip / defer one cycle",
        "A launch_at bump on the\nexisting timer row — no new\nstate, no Subly change", style=AMBER, ss=7.6)
    arrow(ax, (XB + 2.6, yB[2]), (XBB - 1.65, yB[2]))

    box(ax, XB, yB[3], W, 1.8, "11 · Or change cadence / amount",
        "The modify endpoint already exists.\n“Every 30 days instead of weekly”", style=AMBER, ss=7.8)
    arrow(ax, (XB, yB[2] - 0.95), (XB, yB[3] + 0.9), label="yes")

    box(ax, XB, yB[4], W, 1.8, "12 · Cancel stays primary throughout",
        "Equal weight, one tap, always visible.\nNo confirmshaming, no re-prompting", style=RED, ss=7.8)
    arrow(ax, (XB, yB[3] - 0.9), (XB, yB[4] + 0.9), label="no / declined")

    box(ax, XB, yB[5], W, 1.8, "13 · Confirmation + no further charge",
        "Stated explicitly, on the channel it was sold on", style=RED, ss=7.8)
    arrow(ax, (XB, yB[4] - 0.9), (XB, yB[5] + 0.9))

    box(ax, XB, yB[6], W, 1.9, "14 · Measure what matters",
        "Not attach rate — fee revenue per purchaser\nper 90 days. Attach does not survive DCS-5289;\nrevenue per purchaser does.", style=TEAL, ss=7.6)
    arrow(ax, (XB, yB[5] - 0.9), (XB, yB[6] + 0.95))

    save(fig, "imtu_journey_5_future.png")


if __name__ == "__main__":
    print("Generating IMTU subscription journey diagrams…")
    current()
    variants()
    immediate()
    delayed()
    future()
    print("Done.")
