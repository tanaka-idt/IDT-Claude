#!/usr/bin/env python3
"""
Two figures for the IMTU promotion-interaction reference (design team).

  1. promo_interaction_states.png    - when the subscription section is on
                                       screen and when it is not
  2. promo_interaction_journeys.png  - four worked journeys

Two ideas, and the second one governs:

SLOTS. A transaction has exactly two promotion slots, Fee and Top-up amount,
each holding at most one promotion. Automatic and manual promotions compete
for them: a manual code always wins the slot it lands on, and ✕ restores the
automatic it displaced.

THE GATE. The subscription section is rendered only on a transaction that
carries no discount at all. An instant automatic the customer qualifies for
hides it, and so does a promo code they type, whether or not the subscription
would have carried a promotion of its own. The reason is the recurring charge:
a discount sitting beside a subscription offer reads as a discount on every
future charge, and it is not. The gate follows the discount rather than the
page load, so removing the last discount brings the section back with the
toggle exactly as the customer left it.

Because of the gate, a subscription never competes for a slot: it is only ever
offered when both slots are empty. Earlier drafts of this figure drew that
competition, and it cannot happen.

Colour language is fixed and must match the doc:
  Automatic = blue      Manual = amber      Subscription = violet
  Section hidden = red

Visual language matches generate_subscription_flow_diagrams.py.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

GRAY = dict(fill="#EEEBE5", edge="#A8A29A", text="#454340")
BLUE = dict(fill="#E6EEF7", edge="#3F6FA8", text="#2C5384")    # AUTOMATIC
AMBER = dict(fill="#FAEBD9", edge="#C4841F", text="#8F5E0E")   # MANUAL
VIOLET = dict(fill="#EFEAF7", edge="#6B4FA8", text="#4E3684")  # SUBSCRIPTION
RED = dict(fill="#FBE9E9", edge="#C05050", text="#9E3232")
WHITE = dict(fill="#FFFFFF", edge="#C9C6C0", text="#454340")
ARROW = "#7A7A7A"

XMAX = 22.0


def arrow(ax, p0, p1, label=None, lpos=0.5, ldx=0.0, ldy=0.16, dashed=False,
          lsize=7.6, rad=0.0, color=None):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=11,
        linewidth=1.2, color=color or ARROW, zorder=3,
        linestyle=(0, (4, 3)) if dashed else "solid",
        connectionstyle=f"arc3,rad={rad}"))
    if label:
        mx = p0[0] + (p1[0] - p0[0]) * lpos + ldx
        my = p0[1] + (p1[1] - p0[1]) * lpos + ldy
        ax.text(mx, my, label, ha="center", va="center", fontsize=lsize,
                color="#6A6A6A", zorder=5,
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="none", alpha=0.95))


def legend_chips(ax, y, extra=None):
    """The colour key, drawn identically on both figures."""
    items = [("Automatic", BLUE), ("Manual", AMBER), ("Subscription", VIOLET)]
    x = 6.4
    for name, st in items:
        ax.add_patch(FancyBboxPatch(
            (x, y - 0.17), 0.42, 0.34,
            boxstyle="round,pad=0,rounding_size=0.08",
            linewidth=1.1, facecolor=st["fill"], edgecolor=st["edge"], zorder=3))
        ax.text(x + 0.58, y, name, ha="left", va="center",
                fontsize=8.0, color="#6A6A6A", zorder=3)
        x += 0.58 + len(name) * 0.175 + 0.95
    if extra:
        ax.text(XMAX / 2, y - 0.62, extra, ha="center", va="center",
                fontsize=7.8, color="#9A9A9A", zorder=3)


def canvas(h):
    """No in-figure title - the document heading above each figure carries it."""
    fig_w = 13.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_w * h / XMAX))
    ax.set_xlim(0, XMAX)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


# ------------------------------------------------------- fig 1: the gate ---

def panel(ax, cx, cy, w, h, style):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.18", linewidth=1.7,
        facecolor="#FFFFFF", edgecolor=style["edge"], zorder=3))


def slotline(ax, cx, cy, label, value, style=None):
    ax.text(cx - 3.5, cy, label, ha="left", va="center",
            fontsize=6.8, color="#9A9A9A", zorder=5)
    if style is None:
        ax.text(cx + 0.6, cy, value, ha="center", va="center",
                fontsize=7.6, color="#B4B0AA", zorder=5)
        return
    ax.add_patch(FancyBboxPatch(
        (cx - 0.75, cy - 0.27), 2.7, 0.54,
        boxstyle="round,pad=0,rounding_size=0.09", linewidth=1.1,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=4))
    ax.text(cx + 0.6, cy, value, ha="center", va="center", fontsize=7.8,
            fontweight="bold", color=style["text"], zorder=5)


def fig_flow():
    H = 11.35
    fig, ax = canvas(H)

    ax.text(XMAX / 2, 10.75,
            "The subscription section is shown if, and only if, nothing "
            "discounts this purchase.",
            ha="center", va="center", fontsize=10.4, fontweight="bold",
            color="#232320", zorder=5)

    lx, rx, pw = 5.0, 17.0, 8.6
    pcy, ph = 6.9, 4.2

    ax.text(lx, 9.55, "SECTION SHOWN", ha="center", va="center",
            fontsize=9.0, fontweight="bold", color=VIOLET["text"], zorder=5)
    ax.text(rx, 9.55, "SECTION HIDDEN", ha="center", va="center",
            fontsize=9.0, fontweight="bold", color=RED["text"], zorder=5)

    # ---- left: the one state where the offer is made ----------------------
    panel(ax, lx, pcy, pw, ph, VIOLET)
    ax.text(lx, pcy + ph / 2 - 0.46, "Nothing discounts the purchase",
            ha="center", va="center", fontsize=9.4, fontweight="bold",
            color=VIOLET["text"], zorder=5)
    slotline(ax, lx, pcy + 0.72, "FEE", "no promo")
    slotline(ax, lx, pcy + 0.10, "AMOUNT", "no promo")
    ax.add_patch(FancyBboxPatch(
        (lx - 3.6, pcy - 1.18), 7.2, 0.66,
        boxstyle="round,pad=0,rounding_size=0.10", linewidth=1.2,
        facecolor=VIOLET["fill"], edgecolor=VIOLET["edge"], zorder=4))
    ax.text(lx, pcy - 0.85, "SUBSCRIPTION TOGGLE · the customer's to set",
            ha="center", va="center", fontsize=7.8, fontweight="bold",
            color=VIOLET["text"], zorder=5)
    ax.text(lx, pcy - ph / 2 + 0.38,
            "the only state the offer is ever made from",
            ha="center", va="center", fontsize=7.2, color="#8A8A8A", zorder=5)

    # ---- right: every other transaction -----------------------------------
    panel(ax, rx, pcy, pw, ph, RED)
    ax.text(rx, pcy + ph / 2 - 0.46, "A discount applies",
            ha="center", va="center", fontsize=9.4, fontweight="bold",
            color=RED["text"], zorder=5)
    for dx, (name, st) in zip((-2.0, 2.0),
                              (("Instant automatic", BLUE),
                               ("Manual promo code", AMBER))):
        ax.add_patch(FancyBboxPatch(
            (rx + dx - 1.75, pcy + 0.18), 3.5, 0.62,
            boxstyle="round,pad=0,rounding_size=0.10", linewidth=1.2,
            facecolor=st["fill"], edgecolor=st["edge"], zorder=4))
        ax.text(rx + dx, pcy + 0.49, name, ha="center", va="center",
                fontsize=7.6, fontweight="bold", color=st["text"], zorder=5)
    ax.text(rx, pcy + 0.49, "or", ha="center", va="center", fontsize=7.4,
            color="#8A8A8A", zorder=5,
            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none"))
    ax.text(rx, pcy - 0.62,
            "no toggle, no section, nothing to design.\nAny subscription the "
            "customer had set is off.",
            ha="center", va="center", fontsize=7.6, color=RED["text"],
            alpha=0.92, zorder=5, linespacing=1.5)
    ax.text(rx, pcy - ph / 2 + 0.38,
            "whether or not the subscription had a promotion of its own",
            ha="center", va="center", fontsize=7.2, color="#8A8A8A", zorder=5)

    # ---- the crossing, which is the whole interaction ----------------------
    le, re_ = lx + pw / 2, rx - pw / 2
    arrow(ax, (le, 7.9), (re_, 7.9))
    ax.text((le + re_) / 2, 8.62,
            "a discount lands:\nan automatic at load, or a\ncode the customer types",
            ha="center", va="center", fontsize=7.2, color="#6A6A6A",
            zorder=5, linespacing=1.5)
    arrow(ax, (re_, 5.9), (le, 5.9))
    ax.text((le + re_) / 2, 5.18,
            "the last discount goes:\nthe section returns, toggle\nexactly as they left it",
            ha="center", va="center", fontsize=7.2, color="#6A6A6A",
            zorder=5, linespacing=1.5)

    # ---- why ---------------------------------------------------------------
    wy, wh = 2.55, 2.0
    ax.add_patch(FancyBboxPatch(
        (0.6, wy - wh / 2), XMAX - 1.2, wh,
        boxstyle="round,pad=0,rounding_size=0.16", linewidth=1.5,
        facecolor=VIOLET["fill"], edgecolor=VIOLET["edge"], zorder=3))
    ax.text(XMAX / 2, wy + 0.58, "Why we hide it rather than explain it",
            ha="center", va="center", fontsize=9.6, fontweight="bold",
            color=VIOLET["text"], zorder=5)
    ax.text(XMAX / 2, wy - 0.28,
            "A discount sitting beside a subscription offer reads as a discount "
            "on every future charge. It is not: the promotion applies\n"
            "to this purchase only. Rather than explain that on the payment "
            "screen, we do not make the offer while a discount is on\n"
            "the transaction. The subscription therefore never competes for a "
            "slot, because it is only ever offered when both are empty.",
            ha="center", va="center", fontsize=7.6, color=VIOLET["text"],
            alpha=0.92, zorder=5, linespacing=1.6)

    legend_chips(ax, 0.72,
                 "The gate follows the discount, not the page load · "
                 "there is no partly-available state to design.")
    return fig


# -------------------------------------------------- fig 2: worked journeys ---

CARD_W, CARD_H = 3.1, 1.9
INNER = 1.42
VAL = {"auto": ("Automatic", BLUE), "manual": ("Manual", AMBER)}


def statuspill(ax, cx, cy, text, style):
    """Whether the subscription section is on screen for this step."""
    ax.add_patch(FancyBboxPatch(
        (cx - CARD_W / 2, cy - CARD_H / 2 - 0.55), CARD_W, 0.44,
        boxstyle="round,pad=0,rounding_size=0.10", linewidth=1.1,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=3))
    ax.text(cx, cy - CARD_H / 2 - 0.33, text, ha="center", va="center",
            fontsize=6.6, fontweight="bold", color=style["text"], zorder=4)


def slotcard(ax, cx, cy, fee=None, amount=None, sub=False, tag=None, tagcol=None,
             status=None):
    ax.add_patch(FancyBboxPatch(
        (cx - CARD_W / 2, cy - CARD_H / 2), CARD_W, CARD_H,
        boxstyle="round,pad=0,rounding_size=0.12", linewidth=1.3,
        facecolor="#FFFFFF", edgecolor="#C9C6C0", zorder=2))

    if tag:
        ax.text(cx, cy + CARD_H / 2 + 0.26, tag, ha="center", va="center",
                fontsize=7.0, fontweight="bold",
                color=(tagcol or BLUE)["text"], zorder=5)

    if status:
        statuspill(ax, cx, cy, *status)

    if sub:
        ax.add_patch(FancyBboxPatch(
            (cx - INNER, cy - 0.14), INNER * 2, 0.72,
            boxstyle="round,pad=0,rounding_size=0.10", linewidth=1.2,
            facecolor=VIOLET["fill"], edgecolor=VIOLET["edge"], zorder=3))
        ax.text(cx, cy + 0.22, "SUBSCRIPTION", ha="center", va="center",
                fontsize=7.8, fontweight="bold", color=VIOLET["text"], zorder=4)
        ax.text(cx, cy - 0.50, "a recurring top-up", ha="center", va="center",
                fontsize=7.0, color="#8A8A8A", zorder=4)
        return

    ax.plot([cx - INNER, cx + INNER], [cy, cy], color="#E4E1DC",
            linewidth=0.9, zorder=3)
    for dy, label, val in ((0.44, "FEE", fee), (-0.44, "AMOUNT", amount)):
        ax.text(cx - INNER, cy + dy, label, ha="left", va="center",
                fontsize=6.4, color="#9A9A9A", zorder=4)
        if val is None:
            ax.text(cx + 0.50, cy + dy, "no promo", ha="center", va="center",
                    fontsize=7.0, color="#B4B0AA", zorder=4)
            continue
        name, st = VAL[val]
        ax.add_patch(FancyBboxPatch(
            (cx - 0.42, cy + dy - 0.25), 1.84, 0.50,
            boxstyle="round,pad=0,rounding_size=0.09", linewidth=1.1,
            facecolor=st["fill"], edgecolor=st["edge"], zorder=3))
        ax.text(cx + 0.50, cy + dy, name, ha="center", va="center",
                fontsize=7.4, fontweight="bold", color=st["text"], zorder=4)


def rowlabel(ax, cy, title, hint):
    """Title grows upward, hint downward, so multi-line titles never collide."""
    ax.text(0.15, cy + 0.14, title, ha="left", va="bottom",
            fontsize=9.6, fontweight="bold", color="#232320", linespacing=1.35)
    ax.text(0.15, cy - 0.16, hint, ha="left", va="top",
            fontsize=7.8, color="#8A8A8A", linespacing=1.35)


def note(ax, cy, text):
    ax.text(17.85, cy, text, ha="left", va="center", fontsize=7.6,
            color="#7A7A7A", linespacing=1.45)


HIDDEN = ("section hidden", RED)
SHOWN = ("section shown", VIOLET)
SUBBED = ("shown · subscribed", VIOLET)


def fig_examples():
    H = 12.9
    fig, ax = canvas(H)

    x1, x2, x3 = 6.3, 11.2, 16.1
    gap = CARD_W / 2 + 0.14
    ra, rb, rc, rd = 11.6, 8.5, 5.4, 2.3

    def step(cy, xa, xb, label):
        arrow(ax, (xa + gap, cy), (xb - gap, cy), label=label, ldy=0.50, lsize=7.0)

    # --- 1 and 2: the slot mechanics, all on the hidden side of the gate ----
    rowlabel(ax, ra, "1 · Replacement",
             "a discount applies, so\nthere is no section")
    slotcard(ax, x1, ra, fee="auto", status=HIDDEN)
    step(ra, x1, x2, "apply a manual\nFEE code")
    slotcard(ax, x2, ra, fee="manual", status=HIDDEN)
    step(ra, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, ra, fee="auto", status=HIDDEN,
             tag="the automatic comes back", tagcol=BLUE)
    note(ax, ra, "The code always wins the\nslot: the customer decides.\nThe automatic is displaced,\nnot deleted, and ✕ restores it.")

    rowlabel(ax, rb, "2 · Stacking",
             "still a discount, so\nstill no section")
    slotcard(ax, x1, rb, fee="auto", status=HIDDEN)
    step(rb, x1, x2, "apply a manual\nAMOUNT code")
    slotcard(ax, x2, rb, fee="auto", amount="manual", status=HIDDEN)
    note(ax, rb, "Different targets, so both\nsurvive. A discount is on the\ntransaction either way, so the\noffer is never made.")

    # --- 3: the only route in ----------------------------------------------
    rowlabel(ax, rc, "3 · Subscribing",
             "the only route to\na subscription")
    slotcard(ax, x1, rc, status=SHOWN)
    step(rc, x1, x2, "toggle the\nsubscription ON")
    slotcard(ax, x2, rc, sub=True, status=SUBBED)
    note(ax, rc, "Nothing discounts the purchase,\nso the offer is on screen. Both\nslots are empty, which is the\nonly way it is ever offered.")

    # --- 4: the crossing, both directions ----------------------------------
    rowlabel(ax, rd, "4 · Code while\nsubscribed, and back",
             "the crossing, in both\ndirections")
    slotcard(ax, x1, rd, sub=True, status=SUBBED)
    step(rd, x1, x2, "enter a manual\nFEE code")
    slotcard(ax, x2, rd, fee="manual", status=HIDDEN,
             tag="subscription switched off", tagcol=RED)
    step(rd, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, rd, sub=True, status=SUBBED,
             tag="toggle as they left it", tagcol=VIOLET)
    note(ax, rd, "The subscription goes off with\nthe section and comes back\nwith it. Neither change was\nasked for, so say both.")

    legend_chips(ax, 0.35)
    return fig


if __name__ == "__main__":
    print("Generating promotion-interaction figures...")
    save(fig_flow(), "promo_interaction_states.png")
    save(fig_examples(), "promo_interaction_journeys.png")
    print("Done.")
