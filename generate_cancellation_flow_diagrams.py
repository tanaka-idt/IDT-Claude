#!/usr/bin/env python3
"""
Generate the Digicel top-up cancellation flowchart and the recommended
BOSS Revolution IMTU subscription cancellation flow.

Diagram 1 combines two sources. The navigation is quoted from Digicel's FAQ
(topup.digicelgroup.com/en/faq/, "How do I cancel AutoPay/Auto Top Up?"). The
confirmation dialog, its A/B branch and its verbatim copy were read out of the
shipped production bundle for /profile/autopays — Digicel documents none of it.
The finding is that exactly 2 of 16 retention mechanisms are present, and that
the one that matters emits no exposure event and no save event, so Digicel
cannot measure the experiment it is running.

Diagram 2 is the recommended BR flow, built to Minnesota Stat. 325G.58 — the
strictest US state ARL — so a single flow ships nationally. Note the FTC
click-to-cancel rule was vacated by the Eighth Circuit on 8 July 2025; ROSCA,
FTC Act s5 and the state ARLs are what actually bind.

Visual language mirrors generate_felix_whatsapp_flow_diagrams.py.
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
ARROW = "#7A7A7A"


def box(ax, cx, cy, w, h, title, sub=None, style=GRAY, title_size=10.5, sub_size=8.2):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.14",
        linewidth=1.4, facecolor=style["fill"], edgecolor=style["edge"], zorder=2))
    if sub:
        ax.text(cx, cy + h * 0.19, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=style["text"], zorder=3)
        ax.text(cx, cy - h * 0.24, sub, ha="center", va="center",
                fontsize=sub_size, color=style["text"], alpha=0.88, zorder=3)
    else:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=style["text"], zorder=3)


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
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.92))


def canvas(fig_w, h, title, subtitle, legend, xmax=20):
    fig, ax = plt.subplots(figsize=(fig_w, fig_w * h / xmax))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.text(xmax / 2, h - 0.5, title, ha="center", va="center",
            fontsize=17, fontweight="bold", color="#232320")
    ax.text(xmax / 2, h - 1.15, subtitle, ha="center", va="center",
            fontsize=9.5, color="#6A6A6A")
    ax.text(xmax / 2, 0.35, legend, ha="center", va="center",
            fontsize=8.5, color="#8A8A8A")
    return fig, ax


def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


# ==================================================== 1. DIGICEL OBSERVED ====
def digicel_flow():
    H = 20
    fig, ax = canvas(
        18, H,
        "Diagram 1 \u2014 Digicel International Top-Up: Observed Cancellation Flow",
        "Navigation quoted from Digicel's FAQ; the dialog copy and the A/B branch read directly from shipped production JavaScript. "
        "Digicel's own documentation never mentions this dialog.",
        "Gray = navigation / system     Teal = retained     Amber = alternate arm     "
        "Red = destructive / terminal     Blue = instrumentation finding")

    X = 6.4
    XL, XR = 2.9, 10.2
    XP = 16.4
    W = 5.2

    box(ax, X, 17.6, W + 0.6, 1.5, "1 \u00b7 Reach the recurring-payment list",
        "Web: Profile \u2192 Recurring Payments (4 steps)\nApp: More \u2192 Frequent Payments (5 steps)", style=TEAL)

    box(ax, X, 16.0, W + 0.6, 1.3, "2 \u00b7 Tap the trash icon / \u201cRemove\u201d",
        "Icon-only destructive control on mobile", style=RED)
    arrow(ax, (X, 17.6 - 0.75), (X, 16.0 + 0.65))

    diamond(ax, X, 13.6, 5.6, 2.0, "3 \u00b7 Feature flag\n\u201cfrequent-payments\u201d\nresolves to?", size=9)
    arrow(ax, (X, 16.0 - 0.65), (X, 13.6 + 1.0))

    # --- control arm ---
    box(ax, XL, 10.6, 4.6, 2.5, "CONTROL ARM",
        "\u201cRemove Frequent Payment\u201d\n\u201cAre you sure you want to remove\nthis frequent payment?\u201d\n\u201cThis action cannot be undone!\u201d\n[ Back ]   [ Remove ]", style=GRAY, sub_size=7.8)
    arrow(ax, (X - 2.8, 13.6), (XL, 10.6 + 1.25), label="control", rad=0.1)

    # --- test arm ---
    box(ax, XR, 10.6, 5.0, 2.5, "TEST ARM \u2014 the intervention",
        "\u201cIf you cancel, you will miss out on:\u201d\n\u2713 Exclusive benefits, like discounts\n\u2713 Worry-free connection to your loved ones\n\u2713 the comfort of sitting back\n[ Keep my Advantages ]  [ Remove Recurring Top Up ]", style=AMBER, sub_size=7.4)
    arrow(ax, (X + 2.8, 13.6), (XR, 10.6 + 1.25), label="test", rad=-0.1)

    ax.text(XR, 8.85, "Localised EN \u00b7 ES \u00b7 FR \u00b7 NL \u2014 genuinely deployed",
            ha="center", fontsize=8, style="italic", color="#8F5E0E")

    # --- outcomes ---
    box(ax, XL, 7.4, 4.2, 1.35, "\u201cBack\u201d \u2192 retained", "No event fires", style=TEAL)
    arrow(ax, (XL, 10.6 - 1.25), (XL, 7.4 + 0.68))

    box(ax, XR, 7.4, 4.6, 1.5, "\u201cKeep my Advantages\u201d \u2192 retained",
        "onClick = onClose \u00b7 NO EVENT FIRES", style=TEAL)
    arrow(ax, (XR, 10.6 - 1.25), (XR, 7.4 + 0.75))

    box(ax, X, 4.9, W + 0.6, 1.5, "4 \u00b7 Recurring payment deleted",
        "Success snackbar in-product\n\u201cremove_frequent_payment\u201d event fires", style=RED)
    arrow(ax, (XL, 7.4 - 0.68), (X - 2.0, 4.9 + 0.75), label="Remove", rad=-0.15)
    arrow(ax, (XR, 7.4 - 0.75), (X + 2.0, 4.9 + 0.75), label="Remove Recurring Top Up", rad=0.15, ldy=-0.35)

    box(ax, X, 2.4, W + 0.6, 1.5, "5 \u00b7 Post-cancellation",
        "No win-back evidence in any source, any market\nEmail/SMS confirmation unverified", style=AMBER)
    arrow(ax, (X, 4.9 - 0.75), (X, 2.4 + 0.75))

    # --- panel ---
    ax.add_patch(FancyBboxPatch(
        (XP - 3.1, 1.5), 6.2, 16.4,
        boxstyle="round,pad=0,rounding_size=0.2",
        linewidth=1.6, facecolor="#FCFAF7", edgecolor="#3F6FA8",
        linestyle="--", zorder=1))
    ax.text(XP, 17.3, "RETENTION MECHANISM", ha="center",
            fontsize=11, fontweight="bold", color="#2C5384")
    ax.text(XP, 16.75, "INVENTORY \u2014 16 checked", ha="center",
            fontsize=11, fontweight="bold", color="#2C5384")

    rows = [
        ("\u2713", "Benefit-loss reminder", "#1E7A5E"),
        ("\u2713", "Confirmation dialog", "#1E7A5E"),
        ("\u2715", "Reason capture / survey", "#C05050"),
        ("\u2715", "Personalised messaging", "#C05050"),
        ("\u2715", "Discount / credit / bonus", "#C05050"),
        ("\u2715", "Pause / postpone / skip", "#C05050"),
        ("\u2715", "Downgrade or modify", "#C05050"),
        ("\u2715", "Alternative amount", "#C05050"),
        ("\u2715", "Alternative frequency", "#C05050"),
        ("\u2715", "Alternative payment method", "#C05050"),
        ("\u2715", "Alternative recipient", "#C05050"),
        ("\u2715", "Urgency / scarcity", "#C05050"),
        ("\u2715", "Social proof", "#C05050"),
        ("\u2715", "Support handoff", "#C05050"),
        ("\u2715", "Post-cancel win-back", "#C05050"),
    ]
    y = 15.9
    for mark, label, colour in rows:
        ax.text(XP - 2.75, y, mark, ha="left", va="center",
                fontsize=10, fontweight="bold", color=colour)
        ax.text(XP - 2.3, y, label, ha="left", va="center",
                fontsize=8.8, color="#5A5A5A")
        y -= 0.78

    ax.text(XP, 3.55, "2 of 16 present", ha="center", fontsize=11.5,
            fontweight="bold", color="#2C5384")
    ax.text(XP, 2.75, "And the one that matters\ncannot be measured:\nno exposure event, no save event.",
            ha="center", fontsize=8.6, style="italic", color="#9E3232")
    ax.text(XP, 1.95, "Absences are architectural \u2014\nthe API has no PUT or PATCH.",
            ha="center", fontsize=8.6, style="italic", color="#5A5A5A")

    save(fig, "digicel_cancellation_flow.png")


# ============================================= 2. BR RECOMMENDED CANCEL ====
def br_flow():
    H = 21
    fig, ax = canvas(
        18, H,
        "Diagram 2 \u2014 Recommended BOSS Revolution IMTU Cancellation Flow",
        "Built to Minnesota \u00a7325G.58 \u2014 the strictest US state ARL \u2014 so one flow ships nationally. "
        "The FTC click-to-cancel rule was vacated in July 2025; ROSCA and state ARLs are what bind.",
        "Gray = system step     Teal = retention opportunity     Amber = alternative to cancelling     "
        "Red = cancellation proceeds     Blue = compliance guardrail")

    XA, XAB = 4.5, 9.2
    XB, XBB = 13.9, 18.1
    W, BW = 5.0, 3.2
    h1 = 1.15

    yA = [18.4, 16.2, 14.0, 11.7, 9.4, 7.0, 4.5]

    box(ax, XA, yA[0], W, h1 + 0.35, "1 \u00b7 Cancel entry point",
        "On the subscription card itself, \u22642 taps\nSame medium it was sold in \u2014 never support-only", style=BLUE)

    box(ax, XA, yA[1], W, h1 + 0.35, "2 \u00b7 State what is being cancelled",
        "Recipient, amount, frequency, next charge date\nRemoves the \u201cwhich one?\u201d error class")
    arrow(ax, (XA, yA[0] - 0.75), (XA, yA[1] + 0.75))

    box(ax, XA, yA[2], W, h1 + 0.5, "3 \u00b7 Skippable reason + consequences",
        "Lawful without permission (Minn. subd. 5(1)\u2013(2))\nNever a gate \u2014 answering is optional", style=BLUE)
    arrow(ax, (XA, yA[1] - 0.75), (XA, yA[2] + 0.83))

    diamond(ax, XA, yA[3], 5.0, 1.9, "4 \u00b7 \u201cCan we show you\none option?\u201d", size=9, style=BLUE)
    arrow(ax, (XA, yA[2] - 0.83), (XA, yA[3] + 0.95))
    box(ax, XAB, yA[3], BW, 1.5, "\u201cNo, cancel now\u201d", "Straight to step 8.\nAsked ONCE per attempt.", style=BLUE)
    arrow(ax, (XA + 2.5, yA[3]), (XAB - 1.6, yA[3]), label="decline")

    box(ax, XA, yA[4], W, h1 + 0.7, "5 \u00b7 ONE intervention \u2014 pause first",
        "Pause / skip / downgrade is the safe harbour\n(Minn. subd. 5(4)) \u2014 lawful, and the strongest lever\nDiscount only where permission was granted", style=TEAL)
    arrow(ax, (XA, yA[3] - 0.95), (XA, yA[4] + 0.93), label="permission given")

    diamond(ax, XA, yA[5], 4.6, 1.8, "6 \u00b7 Accept an\nalternative?")
    arrow(ax, (XA, yA[4] - 0.93), (XA, yA[5] + 0.9))
    box(ax, XAB, yA[5], BW, 1.5, "Retained", "Pause / downgrade applied,\nconfirmed, and logged", style=TEAL)
    arrow(ax, (XA + 2.3, yA[5]), (XAB - 1.6, yA[5]), label="yes")

    box(ax, XA, yA[6], W, h1 + 0.5, "7 \u00b7 Cancel control visible THROUGHOUT",
        "Displayed simultaneously with the offer\n(Cal. \u00a717602(e)(2)) \u00b7 equal weight, no confirmshaming", style=BLUE)
    arrow(ax, (XA, yA[5] - 0.9), (XA, yA[6] + 0.83), label="no")

    ax.text(XA, 2.6, "\u25b6  continues in the right-hand column", ha="center", va="center",
            fontsize=9.5, style="italic", color="#1E7A5E")

    # ---- column B ----
    yB = [17.6, 15.4, 13.2, 11.0, 8.8, 6.5, 4.2, 2.2]
    ax.text(XB, 18.85, "(continued)", ha="center", va="center",
            fontsize=9.5, style="italic", color="#8A8A8A")

    diamond(ax, XB, yB[0], 4.4, 1.7, "8 \u00b7 Confirm\ncancellation?")
    box(ax, XBB, yB[0], BW, 1.35, "Abandon", "Returns to subscription,\nunchanged", style=AMBER)
    arrow(ax, (XB + 2.2, yB[0]), (XBB - 1.6, yB[0]), label="no")

    box(ax, XB, yB[1], W, h1 + 0.5, "9 \u00b7 Cancelled, no further charge",
        "Stated explicitly \u00b7 no \u201ceffective at period end\u201d\nambiguity \u00b7 no exit fee", style=RED)
    arrow(ax, (XB, yB[0] - 0.85), (XB, yB[1] + 0.83), label="yes")

    box(ax, XB, yB[2], W, h1 + 0.5, "10 \u00b7 Confirmation + reference number",
        "In-app AND on the channel it was sold on\nMinn. \u00a7325G.59: miss this and your controls\nstop being authoritative", style=BLUE, sub_size=7.8)
    arrow(ax, (XB, yB[1] - 0.83), (XB, yB[2] + 0.83))

    box(ax, XB, yB[3], W, h1 + 0.5, "11 \u00b7 Instrument EVERY branch",
        "Exposure \u00b7 offer shown \u00b7 accepted \u00b7 declined \u00b7 cancelled\nvariant-tagged \u2014 the exact failure Digicel shipped", style=TEAL)
    arrow(ax, (XB, yB[2] - 0.83), (XB, yB[3] + 0.83))

    box(ax, XB, yB[4], W, h1 + 0.5, "12 \u00b7 One-tap resubscribe kept visible",
        "The cheapest retention surface there is,\nand it costs the user nothing to ignore", style=TEAL)
    arrow(ax, (XB, yB[3] - 0.83), (XB, yB[4] + 0.83))

    box(ax, XB, yB[5], W, h1 + 0.5, "13 \u00b7 Reason feeds the promo engine",
        "Price reasons \u2192 BLS eligibility\nProduct reasons \u2192 NBO / bundle ranking", style=TEAL)
    arrow(ax, (XB, yB[4] - 0.83), (XB, yB[5] + 0.83))

    box(ax, XB, yB[6], W, h1 + 0.5, "14 \u00b7 Win-back after a cooling-off gap",
        "Reason-targeted, frequency-capped, opt-out honoured\nImmediacy reads as punishment", style=AMBER)
    arrow(ax, (XB, yB[5] - 0.83), (XB, yB[6] + 0.83))

    box(ax, XB, yB[7], W, h1 + 0.35, "Fixes the dunning gap too",
        "A failed renewal currently sends nothing (CRMC-3299)", style=AMBER)
    arrow(ax, (XB, yB[6] - 0.83), (XB, yB[7] + 0.75), dashed=True)

    save(fig, "br_imtu_cancellation_recommended_flow.png")


if __name__ == "__main__":
    print("Generating cancellation flow diagrams\u2026")
    digicel_flow()
    br_flow()
    print("Done.")
