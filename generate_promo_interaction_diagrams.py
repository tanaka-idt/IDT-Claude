#!/usr/bin/env python3
"""
Two figures for the IMTU promotion-interaction reference (design team).

  1. promo_interaction_states.png    - the 2x2 that decides whether the
                                       subscription section is on screen
  2. promo_interaction_journeys.png  - four worked journeys

Two ideas, and the second one governs:

SLOTS. A transaction has exactly two promotion slots, Fee and Top-up amount,
each holding at most one promotion. Automatic and manual promotions compete
for them: a manual code always wins the slot it lands on, and ✕ restores the
automatic it displaced.

THE CLASH. A subscription promotion cannot be applied alongside an instant
automatic or a manual promo code. The section stays on screen either way: what
changes is the toggle. It switches OFF exactly when that clash would arise, a
discount on the transaction AND a subscription offer carrying a promotion of
its own. Both halves are required. A discount on its own moves nothing.

Because the section stays, the customer can switch the toggle back on, and
that is where the confirmation belongs: a yes/no modal warning that the manual
promo code will be removed. The code is cached, so switching the subscription
off again re-applies it without retyping.

Colour language is fixed and must match the doc:
  Automatic = blue      Manual = amber      Subscription = violet
  Toggle switched off = red

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


# ---------------------------------------------------------- fig 1: the 2x2 ---

def cell(ax, cx, cy, w, h, verdict, body, style):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.15", linewidth=1.7,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=3))
    ax.text(cx, cy + h / 2 - 0.48, verdict, ha="center", va="center",
            fontsize=9.8, fontweight="bold", color=style["text"], zorder=5)
    ax.text(cx, cy - 0.32, body, ha="center", va="center",
            fontsize=7.6, color=style["text"], alpha=0.92, zorder=5,
            linespacing=1.55)


def minichip(ax, cx, cy, text, style, w=3.3):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - 0.24), w, 0.48,
        boxstyle="round,pad=0,rounding_size=0.09", linewidth=1.1,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=7.0,
            fontweight="bold", color=style["text"], zorder=5)


def fig_flow():
    H = 12.2
    fig, ax = canvas(H)

    ax.text(XMAX / 2, 11.6,
            "The toggle switches off on one combination only: a subscription "
            "promotion that would have to sit beside another one.",
            ha="center", va="center", fontsize=10.4, fontweight="bold",
            color="#232320", zorder=5)

    c1, c2, cw = 9.5, 18.1, 7.0
    r1, r2, ch = 8.3, 4.9, 2.5

    # column headers
    ax.text(c1, 10.5, "No discount on the transaction", ha="center",
            va="center", fontsize=9.2, fontweight="bold", color="#454340",
            zorder=5)
    ax.text(c2, 10.72, "A discount on the transaction", ha="center",
            va="center", fontsize=9.2, fontweight="bold", color="#454340",
            zorder=5)
    minichip(ax, c2 - 1.85, 10.15, "Instant automatic", BLUE)
    ax.text(c2, 10.15, "or", ha="center", va="center", fontsize=6.8,
            color="#8A8A8A", zorder=5)
    minichip(ax, c2 + 1.85, 10.15, "Manual code", AMBER)

    # row headers
    ax.text(3.0, r1, "The subscription offer\ncarries a promotion",
            ha="center", va="center", fontsize=9.2, fontweight="bold",
            color=VIOLET["text"], zorder=5, linespacing=1.45)
    ax.text(3.0, r2, "The subscription offer\ncarries no promotion",
            ha="center", va="center", fontsize=9.2, fontweight="bold",
            color="#454340", zorder=5, linespacing=1.45)

    # the four cells
    cell(ax, c1, r1, cw, ch, "SECTION SHOWN",
         "with its savings copy: the\nsubscription promotion applies",
         VIOLET)
    cell(ax, c2, r1, cw, ch, "TOGGLE SWITCHED OFF",
         "the clash. The section stays on screen,\nbut the two promotions cannot both\n"
         "apply, so the subscription steps aside",
         RED)
    cell(ax, c1, r2, cw, ch, "SECTION SHOWN",
         "a plain recurring top-up,\nwith no savings copy",
         VIOLET)
    cell(ax, c2, r2, cw, ch, "SECTION SHOWN",
         "nothing to clash with. The discount\nis on this purchase only, and the\n"
         "subscription is offered as normal",
         VIOLET)

    # only the top row moves
    arrow(ax, (c1 + cw / 2, r1 + 0.55), (c2 - cw / 2, r1 + 0.55))
    arrow(ax, (c2 - cw / 2, r1 - 0.55), (c1 + cw / 2, r1 - 0.55))
    ax.text(XMAX / 2, 6.62,
            "Only the top row moves. A code typed, or an automatic applying at "
            "load, crosses left to right and takes the toggle off with it.\n"
            "Removing the last discount crosses back, with the toggle exactly as "
            "the customer left it. Nothing on the bottom row moves at all.",
            ha="center", va="center", fontsize=7.6, color="#6A6A6A", zorder=5,
            linespacing=1.55)

    # ---- why ---------------------------------------------------------------
    wy, wh = 1.95, 2.0
    ax.add_patch(FancyBboxPatch(
        (0.6, wy - wh / 2), XMAX - 1.2, wh,
        boxstyle="round,pad=0,rounding_size=0.16", linewidth=1.5,
        facecolor=VIOLET["fill"], edgecolor=VIOLET["edge"], zorder=3))
    ax.text(XMAX / 2, wy + 0.56, "Why the toggle steps aside, and what the customer can do about it",
            ha="center", va="center", fontsize=9.6, fontweight="bold",
            color=VIOLET["text"], zorder=5)
    ax.text(XMAX / 2, wy - 0.28,
            "A subscription promotion cannot be applied together with an instant "
            "automatic or a manual promo code, so on that one combination the "
            "toggle switches off.\nThe section itself stays on screen, which means "
            "the customer can switch it back on. Doing so needs the promo code "
            "removed, so we ask first with a\nyes/no modal. The code is cached "
            "either way: switch the subscription off again and it is re-applied "
            "without retyping.",
            ha="center", va="center", fontsize=7.6, color=VIOLET["text"],
            alpha=0.92, zorder=5, linespacing=1.6)
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


def modalcard(ax, cx, cy, tag=None):
    """The yes/no confirmation shown when the customer switches the toggle on."""
    ax.add_patch(FancyBboxPatch(
        (cx - CARD_W / 2, cy - CARD_H / 2), CARD_W, CARD_H,
        boxstyle="round,pad=0,rounding_size=0.12", linewidth=1.6,
        facecolor=AMBER["fill"], edgecolor=AMBER["edge"], zorder=3))
    if tag:
        ax.text(cx, cy + CARD_H / 2 + 0.26, tag, ha="center", va="center",
                fontsize=7.0, fontweight="bold", color=AMBER["text"], zorder=5)
    ax.text(cx, cy + 0.52, "REMOVE YOUR\nPROMO CODE?", ha="center", va="center",
            fontsize=7.2, fontweight="bold", color=AMBER["text"], zorder=4,
            linespacing=1.3)
    ax.text(cx, cy - 0.14, "subscribing means giving\nup the code you applied",
            ha="center", va="center", fontsize=6.4, color=AMBER["text"],
            alpha=0.9, zorder=4, linespacing=1.35)
    for dx, lab in ((-0.62, "No"), (0.62, "Yes")):
        ax.add_patch(FancyBboxPatch(
            (cx + dx - 0.46, cy - 0.82), 0.92, 0.36,
            boxstyle="round,pad=0,rounding_size=0.08", linewidth=1.1,
            facecolor="#FFFFFF", edgecolor=AMBER["edge"], zorder=4))
        ax.text(cx + dx, cy - 0.64, lab, ha="center", va="center", fontsize=6.8,
                fontweight="bold", color=AMBER["text"], zorder=5)


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
        ax.text(cx, cy + 0.22, "SUBSCRIPTION PROMO", ha="center", va="center",
                fontsize=7.2, fontweight="bold", color=VIOLET["text"], zorder=4)
        ax.text(cx, cy - 0.50, "on offer with the top-up", ha="center",
                va="center", fontsize=7.0, color="#8A8A8A", zorder=4)
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


TOGGLE_OFF = ("toggle switched OFF", RED)
SHOWN = ("section shown", VIOLET)
SUBBED = ("shown · subscribed", VIOLET)


def fig_examples():
    H = 16.1
    fig, ax = canvas(H)

    x1, x2, x3 = 6.3, 11.2, 16.1
    gap = CARD_W / 2 + 0.14
    ra, rb, rc, rd, re_ = 14.7, 11.6, 8.5, 5.4, 2.3

    def step(cy, xa, xb, label):
        arrow(ax, (xa + gap, cy), (xb - gap, cy), label=label, ldy=0.50, lsize=7.0)

    # --- 1 and 2: slot mechanics, independent of what the subscription does -
    rowlabel(ax, ra, "1 · Replacement",
             "the slot mechanics, whatever\nthe subscription is doing")
    slotcard(ax, x1, ra, fee="auto")
    step(ra, x1, x2, "apply a manual\nFEE code")
    slotcard(ax, x2, ra, fee="manual")
    step(ra, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, ra, fee="auto", tag="the automatic comes back", tagcol=BLUE)
    note(ax, ra, "The code always wins the\nslot: the customer decides.\nThe automatic is displaced,\nnot deleted, and ✕ restores it.")

    rowlabel(ax, rb, "2 · Stacking",
             "two promotions, as long as\nthey are on two targets")
    slotcard(ax, x1, rb, fee="auto")
    step(rb, x1, x2, "apply a manual\nAMOUNT code")
    slotcard(ax, x2, rb, fee="auto", amount="manual")
    note(ax, rb, "Different targets, so both\nsurvive. Neither of them is a\nsubscription promotion, so\nneither is in any conflict.")

    # --- 3: no subscription promotion, so nothing to clash with -------------
    rowlabel(ax, rc, "3 · Code applied ·\nNO subscription promo",
             "a plain recurring offer,\nnothing to clash with")
    slotcard(ax, x1, rc, status=SHOWN)
    step(rc, x1, x2, "enter a manual\nFEE code")
    slotcard(ax, x2, rc, fee="manual", status=SHOWN)
    step(rc, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, rc, status=SHOWN)
    note(ax, rc, "Nothing clashes, so nothing\nmoves. The section stays on\nscreen and the toggle stays\nwhere the customer left it.")

    # --- 4: the clash. The section stays, the toggle steps aside ------------
    rowlabel(ax, rd, "4 · Code applied ·\nWITH subscription promo",
             "the toggle steps aside,\nthe section does not")
    slotcard(ax, x1, rd, sub=True, status=SHOWN)
    step(rd, x1, x2, "enter a manual\nFEE code")
    slotcard(ax, x2, rd, fee="manual", status=TOGGLE_OFF,
             tag="subscription switched off", tagcol=RED)
    step(rd, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, rd, sub=True, status=SHOWN,
             tag="toggle back as they left it", tagcol=VIOLET)
    note(ax, rd, "Both cannot apply, so the\nsubscription gives way. The\nsection never leaves the\nscreen, only the toggle moves.")

    # --- 5: the customer insists. Modal, then the cache ---------------------
    rowlabel(ax, re_, "5 · Toggling back on ·\nthe modal and the cache",
             "the customer chooses the\nsubscription over the code")
    slotcard(ax, x1, re_, fee="manual", status=TOGGLE_OFF)
    step(re_, x1, x2, "tap the toggle\nON")
    modalcard(ax, x2, re_, tag="ask before taking anything")
    step(re_, x2, x3, "Yes")
    slotcard(ax, x3, re_, sub=True, status=SHOWN,
             tag="code removed, held in cache", tagcol=AMBER)
    note(ax, re_, "No leaves everything alone.\nYes drops the code, but we\ncache it: switch the\nsubscription off and it is\nre-applied without retyping.")

    legend_chips(ax, 0.35)
    return fig


if __name__ == "__main__":
    print("Generating promotion-interaction figures...")
    save(fig_flow(), "promo_interaction_states.png")
    save(fig_examples(), "promo_interaction_journeys.png")
    print("Done.")
