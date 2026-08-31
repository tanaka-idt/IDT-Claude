#!/usr/bin/env python3
"""
Two figures for the IMTU promotion-interaction one-pager (design team).

  1. promo_interaction_flow.png      - step-by-step interaction logic
  2. promo_interaction_examples.png  - replacement, stacking, restoration

The mental model both figures encode: a transaction has exactly two promotion
SLOTS - Fee and Top-up amount - and each slot holds at most one promotion.
Automatic and manual promotions compete for slots; a subscription promotion is
not a slot-filler at all, it takes over the whole transaction.

Colour language is fixed and must match the doc:
  Automatic   = blue      Manual = amber      Subscription = violet

Visual language matches generate_subscription_flow_diagrams.py.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

GRAY = dict(fill="#EEEBE5", edge="#A8A29A", text="#454340")
BLUE = dict(fill="#E6EEF7", edge="#3F6FA8", text="#2C5384")    # AUTOMATIC
AMBER = dict(fill="#FAEBD9", edge="#C4841F", text="#8F5E0E")   # MANUAL
VIOLET = dict(fill="#EFEAF7", edge="#6B4FA8", text="#4E3684")  # SUBSCRIPTION
RED = dict(fill="#FBE9E9", edge="#C05050", text="#9E3232")
WHITE = dict(fill="#FFFFFF", edge="#C9C6C0", text="#454340")
ARROW = "#7A7A7A"

XMAX = 22.0


def box(ax, cx, cy, w, h, title, sub=None, style=GRAY, ts=9.6, ss=7.6):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.14",
        linewidth=1.4, facecolor=style["fill"], edgecolor=style["edge"], zorder=2))
    if sub:
        ax.text(cx, cy + h * 0.20, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=style["text"], zorder=3)
        ax.text(cx, cy - h * 0.24, sub, ha="center", va="center",
                fontsize=ss, color=style["text"], alpha=0.88, zorder=3)
    else:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=style["text"], zorder=3)


def diamond(ax, cx, cy, w, h, label, size=9.0, style=WHITE):
    ax.add_patch(Polygon(
        [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
        closed=True, linewidth=1.4,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=2))
    ax.text(cx, cy, label, ha="center", va="center",
            fontsize=size, color=style["text"], zorder=3)


def arrow(ax, p0, p1, label=None, lpos=0.5, ldx=0.0, ldy=0.16, dashed=False,
          lsize=7.6, rad=0.0, color=None):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=11,
        linewidth=1.2, color=color or ARROW, zorder=1,
        linestyle="--" if dashed else "-",
        connectionstyle=f"arc3,rad={rad}"))
    if label:
        mx = p0[0] + (p1[0] - p0[0]) * lpos + ldx
        my = p0[1] + (p1[1] - p0[1]) * lpos + ldy
        ax.text(mx, my, label, ha="center", va="center", fontsize=lsize,
                color="#6A6A6A", zorder=4,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.94))


def elbow_return(ax, start, corridor, end, label, lsize=8.0):
    """Dashed return path routed down, across a clear corridor, then up."""
    x0, y0 = start
    x1, y1 = end
    ax.plot([x0, x0], [y0, corridor], color=ARROW, linewidth=1.2,
            linestyle=(0, (4, 3)), zorder=1)
    ax.plot([x0, x1], [corridor, corridor], color=ARROW, linewidth=1.2,
            linestyle=(0, (4, 3)), zorder=1)
    ax.add_patch(FancyArrowPatch(
        (x1, corridor), (x1, y1), arrowstyle="-|>", mutation_scale=11,
        linewidth=1.2, color=ARROW, zorder=1, linestyle=(0, (4, 3))))
    ax.text((x0 + x1) / 2, corridor + 0.30, label, ha="center", va="center",
            fontsize=lsize, color="#6A6A6A", zorder=4,
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


def canvas(h, title, subtitle):
    fig_w = 13.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_w * h / XMAX))
    ax.set_xlim(0, XMAX)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.text(XMAX / 2, h - 0.42, title, ha="center", va="center",
            fontsize=15, fontweight="bold", color="#232320")
    ax.text(XMAX / 2, h - 1.02, subtitle, ha="center", va="center",
            fontsize=9.0, color="#6A6A6A")
    return fig, ax


def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


# ------------------------------------------------------------------ fig 1 ---

def fig_flow():
    H = 10.4
    fig, ax = canvas(
        H,
        "How the three promotion types interact",
        "A transaction has two promotion slots - Fee and Top-up amount. "
        "Each slot holds one promotion. A subscription takes the whole transaction.")

    y = 5.5

    box(ax, 2.35, y, 3.9, 1.35, "Transaction opens",
        "two slots: Fee · Amount", GRAY)
    arrow(ax, (4.30, y), (5.05, y))

    box(ax, 7.15, y, 4.2, 1.35, "Automatic promos apply",
        "by default · one per slot", BLUE)
    arrow(ax, (9.25, y), (10.00, y))

    diamond(ax, 11.95, y, 3.9, 2.15, "Customer applies\na manual promo?")

    # yes, same slot -> replacement (above the spine)
    arrow(ax, (11.95, y + 1.08), (11.95, y + 1.85), label="yes — same slot", ldy=0)
    box(ax, 11.95, y + 2.65, 6.6, 1.40, "Manual replaces the automatic",
        "same slot · the automatic is remembered", AMBER, ss=7.4)

    # yes, other slot -> stacking (below the spine)
    arrow(ax, (11.95, y - 1.08), (11.95, y - 1.85), label="yes — other slot", ldy=0)
    box(ax, 11.95, y - 2.65, 6.6, 1.40, "Both promos apply",
        "one on Fee, one on Amount", AMBER)

    arrow(ax, (13.90, y), (14.80, y), label="no", ldy=0.24)

    diamond(ax, 16.75, y, 3.9, 2.15, "Subscription\nenabled?", style=VIOLET)
    arrow(ax, (15.25, y + 2.65), (16.75, y + 1.15), rad=-0.20)
    arrow(ax, (15.25, y - 2.65), (16.75, y - 1.15), rad=0.20)

    arrow(ax, (18.30, y + 0.60), (19.15, y + 1.55), label="no", lpos=0.32, ldx=0.30, ldy=0.20)
    box(ax, 20.35, y + 2.35, 3.2, 1.40, "Nothing changes",
        "slots stay as set above", GRAY, ss=7.4)

    arrow(ax, (18.30, y - 0.60), (19.15, y - 1.55), label="yes", lpos=0.32, ldx=0.34, ldy=-0.22)
    box(ax, 20.35, y - 2.35, 3.2, 1.50, "Subscription only",
        "every other promo\nis removed", VIOLET, ss=7.4)

    # restoration - the return path, routed under the whole diagram
    elbow_return(ax, (20.35, y - 3.10), 1.45, (7.15, y - 0.68),
                 "toggle OFF  →  the original AUTOMATIC promos are restored")

    legend_chips(ax, 0.62,
                 "Only one promotion per target. Two automatic promos may coexist "
                 "when one is on Fee and the other on Amount.")
    return fig


# ------------------------------------------------------------------ fig 2 ---

CARD_W, CARD_H = 3.1, 1.9
INNER = 1.42          # half-width of the content area inside a card
VAL = {"auto": ("Automatic", BLUE), "manual": ("Manual", AMBER)}


def slotcard(ax, cx, cy, fee=None, amount=None, sub=False, ghost=False):
    a = 0.40 if ghost else 1.0
    ax.add_patch(FancyBboxPatch(
        (cx - CARD_W / 2, cy - CARD_H / 2), CARD_W, CARD_H,
        boxstyle="round,pad=0,rounding_size=0.12", linewidth=1.3,
        facecolor="#FFFFFF", edgecolor=RED["edge"] if ghost else "#C9C6C0",
        zorder=2, alpha=1.0 if ghost else 1.0,
        linestyle=(0, (3, 2)) if ghost else "solid"))

    if sub:
        ax.add_patch(FancyBboxPatch(
            (cx - INNER, cy - 0.14), INNER * 2, 0.72,
            boxstyle="round,pad=0,rounding_size=0.10", linewidth=1.2,
            facecolor=VIOLET["fill"], edgecolor=VIOLET["edge"], zorder=3))
        ax.text(cx, cy + 0.22, "SUBSCRIPTION", ha="center", va="center",
                fontsize=8.0, fontweight="bold", color=VIOLET["text"], zorder=4)
        ax.text(cx, cy - 0.50, "occupies both slots", ha="center", va="center",
                fontsize=7.0, color="#8A8A8A", zorder=4)
        return

    ax.plot([cx - INNER, cx + INNER], [cy, cy], color="#E4E1DC",
            linewidth=0.9, zorder=3, alpha=a)
    for dy, label, val in ((0.44, "FEE", fee), (-0.44, "AMOUNT", amount)):
        ax.text(cx - INNER, cy + dy, label, ha="left", va="center",
                fontsize=6.4, color="#9A9A9A", zorder=4, alpha=a)
        if val is None:
            ax.text(cx + 0.50, cy + dy, "no promo", ha="center", va="center",
                    fontsize=7.0, color="#B4B0AA", zorder=4, alpha=a)
            continue
        name, st = VAL[val]
        ax.add_patch(FancyBboxPatch(
            (cx - 0.42, cy + dy - 0.25), 1.84, 0.50,
            boxstyle="round,pad=0,rounding_size=0.09", linewidth=1.1,
            facecolor=st["fill"], edgecolor=st["edge"], zorder=3, alpha=a))
        ax.text(cx + 0.50, cy + dy, name, ha="center", va="center",
                fontsize=7.4, fontweight="bold", color=st["text"], zorder=4, alpha=a)


def rowlabel(ax, cy, title, hint):
    ax.text(0.15, cy + 0.30, title, ha="left", va="center",
            fontsize=9.6, fontweight="bold", color="#232320")
    ax.text(0.15, cy - 0.32, hint, ha="left", va="center",
            fontsize=7.8, color="#8A8A8A")


def note(ax, cy, text, warn=False):
    ax.text(17.45, cy, text, ha="left", va="center", fontsize=7.6,
            color=RED["text"] if warn else "#7A7A7A",
            fontweight="bold" if warn else "normal")


def fig_examples():
    H = 9.9
    fig, ax = canvas(
        H,
        "What the customer ends up with",
        "The same two slots, tracked through each action. "
        "This is the state the screen has to show at every step.")

    x1, x2, x3 = 5.2, 10.3, 15.4
    gap = CARD_W / 2 + 0.14
    ra, rb, rc = 7.25, 4.65, 2.05

    def step(cy, xa, xb, label):
        arrow(ax, (xa + gap, cy), (xb - gap, cy), label=label, ldy=0.50, lsize=7.0)

    # --- 1. replacement -----------------------------------------------------
    rowlabel(ax, ra, "1 · Replacement", "manual hits an occupied slot")
    slotcard(ax, x1, ra, fee="auto")
    step(ra, x1, x2, "apply manual\nFEE code")
    slotcard(ax, x2, ra, fee="manual")
    step(ra, x2, x3, "subscription\nON")
    slotcard(ax, x3, ra, sub=True)
    note(ax, ra, "One promotion per slot, so the\nmanual code pushes the automatic\nout — but it is remembered.")

    # --- 2. stacking --------------------------------------------------------
    rowlabel(ax, rb, "2 · Stacking", "manual hits a free slot")
    slotcard(ax, x1, rb, fee="auto")
    step(rb, x1, x2, "apply manual\nAMOUNT code")
    slotcard(ax, x2, rb, fee="auto", amount="manual")
    step(rb, x2, x3, "subscription\nON")
    slotcard(ax, x3, rb, sub=True)
    note(ax, rb, "Different targets, so both survive —\nuntil the subscription takes over\nand clears the pair.")

    # --- 3. restoration -----------------------------------------------------
    rowlabel(ax, rc, "3 · Restoration", "subscription switched back off")
    slotcard(ax, x1, rc, sub=True)
    step(rc, x1, x2, "subscription\nOFF")
    slotcard(ax, x2, rc, fee="auto")
    ax.text(x3, rc + CARD_H / 2 + 0.30, "the manual code does NOT come back",
            ha="center", va="center", fontsize=7.2, fontweight="bold",
            color=RED["text"])
    slotcard(ax, x3, rc, fee="manual", ghost=True)
    note(ax, rc, "Only the ORIGINAL automatic\npromos are restored. Confirm this\nis intended — see open questions.",
         warn=True)

    legend_chips(ax, 0.42)
    return fig


if __name__ == "__main__":
    print("Generating promotion-interaction figures...")
    save(fig_flow(), "promo_interaction_flow.png")
    save(fig_examples(), "promo_interaction_examples.png")
    print("Done.")
