#!/usr/bin/env python3
"""
Two figures for the IMTU promotion-interaction reference (design team).

  1. promo_interaction_states.png    - the gate, then three states and every
                                       transition on the far side of it
  2. promo_interaction_journeys.png  - five worked journeys

The mental model both figures encode: a transaction has exactly two promotion
SLOTS - Fee and Top-up amount - and each slot holds at most one promotion.
Automatic and manual promotions compete for slots. A subscription is read in
two halves: one that carries its own promotion is not a slot-filler at all, it
takes over the whole transaction and remembers what it displaced; one with no
promotion attached is only a delivery setting and leaves both slots alone.

Everything about the subscription sits behind a gate. An instant automatic
promotion anywhere on the transaction hides the subscription section outright,
because the two cannot stack and the automatic wins. The gate is evaluated
once, when the transaction loads, so the section does not come back even when
a manual code later displaces the automatic. Journeys 1 and 2 therefore live
on the hidden side of the gate and never show a subscription at all.

Product decisions of 31 Aug 2026 folded in:
  - one manual code per transaction (never two)
  - turning a subscription promotion off restores the previous state IN FULL,
    manual code included
  - the promo-code field stays live while subscribed
  - manual always outranks automatic, the customer decides, no warning

Product decisions of 1 Sep 2026 (DCS-5299 comment thread) folded in:
  - a manual code never hides the subscription section, only the toggle moves
  - with a subscription promotion, applying a manual code toggles the
    subscription OFF; removing the code returns the toggle to its previous
    state; toggling back ON asks for confirmation because the code must go
  - the manual code is cached, so restoring it never means retyping
  - with no subscription promotion, a manual code changes nothing at all
  - an instant automatic hides the section entirely, decided once on load

Colour language is fixed and must match the doc:
  Automatic = blue      Manual = amber      Subscription = violet

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


# ----------------------------------------------------- fig 1: state model ---

def chip(ax, cx, cy, w, text, style, fs=7.6):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - 0.26), w, 0.52,
        boxstyle="round,pad=0,rounding_size=0.09", linewidth=1.1,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
            fontweight="bold", color=style["text"], zorder=5)


def statecard(ax, cx, cy, w, h, title, slots, foot, style):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.16", linewidth=1.6,
        facecolor="#FFFFFF", edgecolor=style["edge"], zorder=3))
    ax.text(cx, cy + h / 2 - 0.42, title, ha="center", va="center",
            fontsize=10.0, fontweight="bold", color=style["text"], zorder=5)

    if len(slots) == 1:                       # a subscription promo takes both
        label, st = slots[0]
        chip(ax, cx, cy - 0.05, w * 0.52, label, st, fs=8.2)
    else:
        for dx, (name, label, st) in zip((-w * 0.24, w * 0.24), slots):
            ax.text(cx + dx, cy + 0.36, name, ha="center", va="center",
                    fontsize=6.6, color="#9A9A9A", zorder=5)
            if label is None:
                ax.text(cx + dx, cy - 0.10, "no promo", ha="center", va="center",
                        fontsize=7.2, color="#B4B0AA", zorder=5)
            else:
                chip(ax, cx + dx, cy - 0.10, w * 0.40, label, st)

    ax.text(cx, cy - h / 2 + 0.36, foot, ha="center", va="center",
            fontsize=7.2, color="#8A8A8A", zorder=5)


def gatebox(ax, cx, cy, w, h, verdict, body, style):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.14", linewidth=1.5,
        facecolor=style["fill"], edgecolor=style["edge"], zorder=3))
    ax.text(cx, cy + h / 2 - 0.40, verdict, ha="center", va="center",
            fontsize=9.2, fontweight="bold", color=style["text"], zorder=5)
    ax.text(cx, cy - 0.30, body, ha="center", va="center",
            fontsize=7.6, color=style["text"], alpha=0.92, zorder=5,
            linespacing=1.55)


def fig_flow():
    H = 12.6
    fig, ax = canvas(H)

    # The gate decides whether any of this is on screen at all.
    ax.text(XMAX / 2, 12.1,
            "First, the gate: does an instant automatic promotion apply to this "
            "transaction?",
            ha="center", va="center", fontsize=10.2, fontweight="bold",
            color="#232320", zorder=5)

    gw, gy, gh = 9.9, 10.85, 2.15
    gatebox(ax, 5.8, gy, gw, gh, "YES · no subscription section",
            "The two cannot stack and the automatic wins, so the section\n"
            "is not rendered. Decided once on load: nothing the customer\n"
            "types afterwards brings it back. Manual codes still work on\n"
            "the slots, and ✕ still restores the automatic.", RED)
    gatebox(ax, 16.2, gy, gw, gh, "NO · the section is rendered",
            "Everything below applies: the three states, the toggle,\n"
            "and the promo-code interactions. No automatic is on the\n"
            "transaction, so both slots start empty and the customer\n"
            "can subscribe.", VIOLET)

    yt = 8.0                      # the two "normal" states sit on this line
    ax_, bx = 5.6, 16.4
    cw, ch = 6.8, 2.5
    a_bot = b_bot = yt - ch / 2

    # The NO branch lands on A: no automatic means both slots start empty.
    ax.plot([11.25, 11.25], [gy - gh / 2, 9.55], color=ARROW, linewidth=1.2,
            zorder=2)
    ax.plot([11.25, ax_], [9.55, 9.55], color=ARROW, linewidth=1.2, zorder=2)
    ax.add_patch(FancyArrowPatch(
        (ax_, 9.55), (ax_, yt + ch / 2), arrowstyle="-|>", mutation_scale=11,
        linewidth=1.2, color=ARROW, zorder=2))

    statecard(ax, ax_, yt, cw, ch, "A · No promotion",
              [("FEE", None, GRAY), ("AMOUNT", None, GRAY)],
              "the default here · the subscription section is shown", GRAY)

    statecard(ax, bx, yt, cw, ch, "B · Manual code applied",
              [("FEE", "Manual", AMBER), ("AMOUNT", None, GRAY)],
              "the code takes one slot · the other stays empty", AMBER)

    # A <-> B
    arrow(ax, (ax_ + cw / 2, yt + 0.50), (bx - cw / 2, yt + 0.50),
          label="enter a promo code", ldy=0.36)
    arrow(ax, (bx - cw / 2, yt - 0.50), (ax_ + cw / 2, yt - 0.50),
          label="tap ✕ to remove it", ldy=-0.40)

    # C, spanning underneath both
    cx_c, cy_c, cwc, chc = 10.4, 3.0, 12.6, 2.5
    statecard(ax, cx_c, cy_c, cwc, chc, "C · Subscription promotion",
              [("SUBSCRIPTION PROMO", VIOLET)],
              "both slots cleared · the previous state is remembered", VIOLET)
    c_top = cy_c + chc / 2

    # A -> C and B -> C. Leaving B has to ask first, because the code must go.
    arrow(ax, (ax_, a_bot), (ax_, c_top), label="subscription ON", lpos=0.46)
    arrow(ax, (bx, b_bot), (bx, c_top),
          label="subscription ON\nask first: the code goes", lpos=0.46)

    # C -> whichever state was active, restored in full
    ax.plot([cx_c, cx_c], [c_top, 5.55], color=ARROW, linewidth=1.2,
            linestyle=(0, (4, 3)), zorder=2)
    ax.plot([7.2, 14.8], [5.55, 5.55], color=ARROW, linewidth=1.2,
            linestyle=(0, (4, 3)), zorder=2)
    for x in (7.2, 14.8):
        ax.add_patch(FancyArrowPatch(
            (x, 5.55), (x, a_bot), arrowstyle="-|>", mutation_scale=11,
            linewidth=1.2, color=ARROW, zorder=2, linestyle=(0, (4, 3))))
    ax.text(11.0, 6.12,
            "subscription OFF, the remembered state returns in full,\n"
            "the cached manual code re-applied without retyping",
            ha="center", va="center", fontsize=7.8, color="#6A6A6A", zorder=5,
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="none", alpha=0.95))

    # the special exit: a code typed while a subscription promotion is on
    nx, ny, nw, nh = 19.4, 3.0, 4.6, 2.5
    ax.add_patch(FancyBboxPatch(
        (nx - nw / 2, ny - nh / 2), nw, nh,
        boxstyle="round,pad=0,rounding_size=0.14", linewidth=1.4,
        facecolor=AMBER["fill"], edgecolor=AMBER["edge"], zorder=3))
    ax.text(nx, ny + 0.76, "Code entered while\nthe promo is on",
            ha="center", va="center",
            fontsize=8.2, fontweight="bold", color=AMBER["text"], zorder=5)
    ax.text(nx, ny - 0.56,
            "the toggle switches OFF\non its own, the code\napplies, and is cached",
            ha="center", va="center", fontsize=7.2, color=AMBER["text"],
            alpha=0.9, zorder=5)
    arrow(ax, (cx_c + cwc / 2, ny), (nx - nw / 2, ny))
    arrow(ax, (nx, ny + nh / 2), (nx, b_bot))

    legend_chips(ax, 0.95,
                 "A manual code never hides the section, it only moves the toggle · "
                 "only an instant automatic hides it, and only at load time.")
    return fig


# -------------------------------------------------- fig 2: worked journeys ---

CARD_W, CARD_H = 3.1, 1.9
INNER = 1.42
VAL = {"auto": ("Automatic", BLUE), "manual": ("Manual", AMBER)}


def slotcard(ax, cx, cy, fee=None, amount=None, sub=False, tag=None, tagcol=None,
             sub_tag=None):
    ax.add_patch(FancyBboxPatch(
        (cx - CARD_W / 2, cy - CARD_H / 2), CARD_W, CARD_H,
        boxstyle="round,pad=0,rounding_size=0.12", linewidth=1.3,
        facecolor="#FFFFFF", edgecolor="#C9C6C0", zorder=2))

    if tag:
        ax.text(cx, cy + CARD_H / 2 + 0.26, tag, ha="center", va="center",
                fontsize=7.0, fontweight="bold",
                color=(tagcol or BLUE)["text"], zorder=5)

    if sub_tag:
        # A subscription riding alongside the slots rather than taking them.
        ax.add_patch(FancyBboxPatch(
            (cx - CARD_W / 2, cy - CARD_H / 2 - 0.62), CARD_W, 0.44,
            boxstyle="round,pad=0,rounding_size=0.10", linewidth=1.1,
            facecolor=VIOLET["fill"], edgecolor=VIOLET["edge"], zorder=3))
        ax.text(cx, cy - CARD_H / 2 - 0.40, sub_tag, ha="center", va="center",
                fontsize=6.6, fontweight="bold", color=VIOLET["text"], zorder=4)

    if sub:
        ax.add_patch(FancyBboxPatch(
            (cx - INNER, cy - 0.14), INNER * 2, 0.72,
            boxstyle="round,pad=0,rounding_size=0.10", linewidth=1.2,
            facecolor=VIOLET["fill"], edgecolor=VIOLET["edge"], zorder=3))
        ax.text(cx, cy + 0.22, "SUBSCRIPTION PROMO", ha="center", va="center",
                fontsize=7.2, fontweight="bold", color=VIOLET["text"], zorder=4)
        ax.text(cx, cy - 0.50, "occupies both slots", ha="center", va="center",
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


def modalcard(ax, cx, cy, title, body):
    """The yes/no sheet owed on DCS-5299, drawn where it interrupts the flow."""
    ax.add_patch(FancyBboxPatch(
        (cx - CARD_W / 2, cy - CARD_H / 2), CARD_W, CARD_H,
        boxstyle="round,pad=0,rounding_size=0.12", linewidth=1.4,
        facecolor=AMBER["fill"], edgecolor=AMBER["edge"], zorder=2))
    ax.text(cx, cy + 0.52, title, ha="center", va="center",
            fontsize=8.0, fontweight="bold", color=AMBER["text"], zorder=4)
    ax.text(cx, cy - 0.22, body, ha="center", va="center",
            fontsize=6.9, color=AMBER["text"], alpha=0.92, zorder=4,
            linespacing=1.4)


def rowlabel(ax, cy, title, hint):
    """Title grows upward, hint downward, so multi-line titles never collide."""
    ax.text(0.15, cy + 0.14, title, ha="left", va="bottom",
            fontsize=9.6, fontweight="bold", color="#232320", linespacing=1.35)
    ax.text(0.15, cy - 0.16, hint, ha="left", va="top",
            fontsize=7.8, color="#8A8A8A", linespacing=1.35)


def note(ax, cy, text):
    ax.text(17.85, cy, text, ha="left", va="center", fontsize=7.6,
            color="#7A7A7A", linespacing=1.45)


def fig_examples():
    H = 14.4
    fig, ax = canvas(H)

    x1, x2, x3 = 6.3, 11.2, 16.1
    gap = CARD_W / 2 + 0.14
    ra, rb, rc, rd, re = 13.2, 10.5, 7.8, 5.1, 2.4

    def step(cy, xa, xb, label):
        arrow(ax, (xa + gap, cy), (xb - gap, cy), label=label, ldy=0.50, lsize=7.0)

    # --- 1 and 2 sit on the hidden side of the gate: an automatic applies ---
    rowlabel(ax, ra, "1 · Replacement",
             "an automatic applies, so\nthere is no subscription section")
    slotcard(ax, x1, ra, fee="auto")
    step(ra, x1, x2, "apply a manual\nFEE code")
    slotcard(ax, x2, ra, fee="manual")
    step(ra, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, ra, fee="auto", tag="the automatic comes back", tagcol=BLUE)
    note(ax, ra, "The code always wins the\nslot: the customer decides.\nThe automatic is displaced,\nnot deleted, and ✕ restores it.")

    rowlabel(ax, rb, "2 · Stacking",
             "still an automatic, so\nstill no subscription section")
    slotcard(ax, x1, rb, fee="auto")
    step(rb, x1, x2, "apply a manual\nAMOUNT code")
    slotcard(ax, x2, rb, fee="auto", amount="manual")
    note(ax, rb, "Different targets, so both\nsurvive. An automatic is on\nthe transaction either way, so\nthe section never appears.")

    # --- 3 to 5 sit on the visible side: no automatic on the transaction -----
    rowlabel(ax, rc, "3 · Restoration",
             "no automatic, so the\nsection is on screen")
    slotcard(ax, x1, rc, sub=True)
    step(rc, x1, x2, "subscription\npromo OFF")
    slotcard(ax, x2, rc, fee="manual", tag="cached code re-applied", tagcol=AMBER)
    step(rc, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, rc)
    note(ax, rc, "Everything comes back\nexactly as it was, the code\nincluded and never retyped.")

    rowlabel(ax, rd, "4 · Code while\nsubscribed · WITH promo",
             "the subscription carries\na promotion of its own")
    slotcard(ax, x1, rd, sub=True)
    step(rd, x1, x2, "enter a manual\nFEE code")
    slotcard(ax, x2, rd, fee="manual",
             tag="toggle OFF · code cached", tagcol=VIOLET)
    step(rd, x2, x3, "toggle it\nback ON")
    modalcard(ax, x3, rd, "Confirm first",
              "Turning the subscription\non removes your promo\ncode. Continue?")
    note(ax, rd, "The toggle flips on its own,\nso say so on screen. Going\nback the other way has to\nask, because the code must go.")

    rowlabel(ax, re, "5 · Code while\nsubscribed · NO promo",
             "the subscription is only\na delivery setting")
    slotcard(ax, x1, re, sub_tag="subscription ON")
    step(re, x1, x2, "enter a manual\nFEE code")
    slotcard(ax, x2, re, fee="manual", sub_tag="subscription ON")
    step(re, x2, x3, "tap ✕ on\nthe code")
    slotcard(ax, x3, re, sub_tag="subscription ON")
    note(ax, re, "Nothing about the subscription\nmoves. The section stays\nvisible and the toggle stays\nwhere the customer left it.")

    legend_chips(ax, 0.25)
    return fig


if __name__ == "__main__":
    print("Generating promotion-interaction figures...")
    save(fig_flow(), "promo_interaction_states.png")
    save(fig_examples(), "promo_interaction_journeys.png")
    print("Done.")
