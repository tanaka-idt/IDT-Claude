#!/usr/bin/env python3
"""
Render the Digicel cancellation flow, step by step, as UI RECONSTRUCTIONS.

WHY THESE ARE RECONSTRUCTIONS AND NOT SCREENSHOTS
-------------------------------------------------
No screenshot of Digicel's cancellation flow exists anywhere. Digicel's own
help-centre images of the opt-out path (optout1.PNG, active-plans1.JPG and
siblings) now resolve to soft-404 pages, a sweep of 509 archived records shows
no web archive ever captured them, and the account area behind the login has
never been archived. All five published store screenshots for the Digicel
International app were independently re-checked: they show the home screen,
Send Money, a promo modal, checkout and a payment confirmation — none shows
Frequent Payments, the account area, or any cancellation control.

What DOES exist is the shipped production JavaScript for the Recurring Payments
route (/profile/autopays), which carries the dialog's branch logic, its click
handlers, and its message catalogue in four languages. Every string rendered
below is quoted verbatim from that bundle or from Digicel's own FAQ. Layout,
spacing and iconography are inferred and are NOT authoritative — only the copy,
the control labels and the branch structure are.

Each figure is stamped RECONSTRUCTED so it can never be mistaken for evidence
of pixel-level appearance.

  digicel_step_1_list.png     — Recurring Payments list, the delete control
  digicel_step_2_control.png  — control arm confirmation dialog
  digicel_step_3_test.png     — test arm, the benefit-loss retention dialog
  digicel_step_4_deleted.png  — completion state
  digicel_step_5_absent.png   — the states that do not exist in the flow
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

RED = "#DA202A"
INK = "#1C2024"
MUTED = "#6E767D"
LINE = "#E3E5E8"
PAPER = "#FFFFFF"
CANVAS = "#F4F5F7"
AMBER = "#B26A00"
AMBER_BG = "#FDF3E3"


def phone(ax, x, y, w, h):
    """Device frame. Returns the inner content rect (x, y, w, h)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.5",
                                facecolor="#0E1113", edgecolor="#0E1113", zorder=1))
    pad = 0.16
    ax.add_patch(FancyBboxPatch((x + pad, y + pad), w - 2 * pad, h - 2 * pad,
                                boxstyle="round,pad=0,rounding_size=0.42",
                                facecolor=PAPER, edgecolor="none", zorder=2))
    return x + pad, y + pad, w - 2 * pad, h - 2 * pad


def header(ax, ix, iy, iw, ih, title):
    hh = 1.15
    ax.add_patch(Rectangle((ix, iy + ih - hh), iw, hh, facecolor=RED, edgecolor="none", zorder=3))
    ax.text(ix + iw / 2, iy + ih - hh / 2 - 0.04, title, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="white", zorder=4)
    ax.text(ix + 0.45, iy + ih - hh / 2 - 0.04, "‹", ha="center", va="center",
            fontsize=15, color="white", zorder=4)
    return iy + ih - hh


def stamp(ax, x, y, w):
    ax.add_patch(FancyBboxPatch((x, y), w, 0.62, boxstyle="round,pad=0,rounding_size=0.14",
                                facecolor=AMBER_BG, edgecolor=AMBER, linewidth=1.1, zorder=6))
    ax.text(x + w / 2, y + 0.31, "RECONSTRUCTED FROM SHIPPED CODE — NOT A SCREENSHOT",
            ha="center", va="center", fontsize=8.0, fontweight="bold", color=AMBER, zorder=7)


def canvas(w=7.4, h=9.6, title="", sub=""):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 10); ax.set_ylim(0, 14.4); ax.axis("off")
    fig.patch.set_facecolor(CANVAS)
    ax.text(5, 13.95, title, ha="center", va="center", fontsize=12.5,
            fontweight="bold", color=INK)
    if sub:
        ax.text(5, 13.45, sub, ha="center", va="center", fontsize=8.4, color=MUTED)
    return fig, ax


def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor=CANVAS)
    plt.close(fig)
    print(f"  wrote {path}")


def row(ax, ix, iw, y, label, sub):
    ax.add_patch(Rectangle((ix + 0.3, y - 0.95), iw - 0.6, 1.5,
                           facecolor=PAPER, edgecolor=LINE, linewidth=1, zorder=3))
    ax.text(ix + 0.6, y + 0.16, label, ha="left", va="center",
            fontsize=8.6, fontweight="bold", color=INK, zorder=4)
    ax.text(ix + 0.6, y - 0.36, sub, ha="left", va="center",
            fontsize=7.4, color=MUTED, zorder=4)
    # trash affordance — icon-only, which is the accessibility point
    tx = ix + iw - 0.95
    ax.add_patch(Rectangle((tx - 0.17, y - 0.30), 0.34, 0.42,
                           facecolor="none", edgecolor=RED, linewidth=1.3, zorder=4))
    ax.add_patch(Rectangle((tx - 0.24, y + 0.12), 0.48, 0.09,
                           facecolor=RED, edgecolor="none", zorder=4))
    return tx


# --------------------------------------------------------------- step 1 ----
def step1():
    fig, ax = canvas(title="Step 1–4 · Reaching the delete control",
                     sub="App: More → Frequent Payments → Auto Top Up and AutoPay → trash icon (5 steps)")
    ix, iy, iw, ih = phone(ax, 1.7, 2.55, 6.6, 10.4)
    top = header(ax, ix, iy, iw, ih, "Frequent Payments")
    ax.add_patch(Rectangle((ix, iy), iw, top - iy, facecolor=CANVAS, edgecolor="none", zorder=2))

    ax.text(ix + 0.55, top - 0.75, "AUTO TOP UP", ha="left", va="center",
            fontsize=7.4, fontweight="bold", color=MUTED, zorder=4)
    tx = row(ax, ix, iw, top - 1.9, "+509 •••• ••••  ·  Haiti", "Every week  ·  $12.00 USD")
    row(ax, ix, iw, top - 3.7, "+509 •••• ••••  ·  Haiti", "Every month  ·  $25.00 USD")

    ax.annotate("", xy=(tx + 0.30, top - 1.78), xytext=(tx + 1.5, top - 1.05),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6), zorder=8)
    ax.text(tx + 1.55, top - 0.95, "the only\ncontrol", ha="left", va="center",
            fontsize=7.8, fontweight="bold", color=RED, zorder=8)

    ax.text(ix + iw / 2, iy + 1.2,
            "No edit. No pause. No change of amount,\nfrequency, recipient or payment method.",
            ha="center", va="center", fontsize=8, color=MUTED, style="italic", zorder=4)

    stamp(ax, 1.15, 0.35, 7.7)
    save(fig, "digicel_step_1_list.png")


# --------------------------------------------------------------- step 2 ----
def step2():
    fig, ax = canvas(title="Step 5a · Control arm — plain confirmation",
                     sub="Shown when the “frequent-payments” flag resolves to control, and whenever flag evaluation fails")
    ix, iy, iw, ih = phone(ax, 1.7, 2.55, 6.6, 10.4)
    top = header(ax, ix, iy, iw, ih, "Frequent Payments")
    ax.add_patch(Rectangle((ix, iy), iw, top - iy, facecolor="#00000018", edgecolor="none", zorder=3))

    dy, dh = iy + 3.2, 4.6
    ax.add_patch(FancyBboxPatch((ix + 0.45, dy), iw - 0.9, dh,
                                boxstyle="round,pad=0,rounding_size=0.22",
                                facecolor=PAPER, edgecolor=LINE, zorder=4))
    ax.text(ix + iw / 2, dy + dh - 0.68, "Remove Frequent Payment", ha="center", va="center",
            fontsize=10, fontweight="bold", color=INK, zorder=5)
    ax.text(ix + iw / 2, dy + dh - 1.72, "Are you sure you want to remove\nthis frequent payment?",
            ha="center", va="center", fontsize=8.4, color=INK, zorder=5, linespacing=1.4)
    ax.text(ix + iw / 2, dy + dh - 2.72, "This action cannot be undone!", ha="center", va="center",
            fontsize=8.4, fontweight="bold", color=RED, zorder=5)

    bw = (iw - 1.5) / 2
    ax.add_patch(FancyBboxPatch((ix + 0.7, dy + 0.55), bw, 0.85,
                                boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor=PAPER, edgecolor=MUTED, zorder=5))
    ax.text(ix + 0.7 + bw / 2, dy + 0.97, "Back", ha="center", va="center",
            fontsize=9, fontweight="bold", color=INK, zorder=6)
    ax.add_patch(FancyBboxPatch((ix + 0.8 + bw, dy + 0.55), bw, 0.85,
                                boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor=RED, edgecolor=RED, zorder=5))
    ax.text(ix + 0.8 + bw * 1.5, dy + 0.97, "Remove", ha="center", va="center",
            fontsize=9, fontweight="bold", color="white", zorder=6)

    ax.text(5, 1.62, "No reason is asked. No alternative is offered. Neither button emits an event.",
            ha="center", va="center", fontsize=8, color=MUTED, style="italic")
    stamp(ax, 1.15, 0.35, 7.7)
    save(fig, "digicel_step_2_control.png")


# --------------------------------------------------------------- step 3 ----
def step3():
    fig, ax = canvas(title="Step 5b · Test arm — the retention intervention",
                     sub="The only save attempt Digicel makes. Localised EN · ES · FR · NL")
    ix, iy, iw, ih = phone(ax, 1.7, 2.55, 6.6, 10.4)
    top = header(ax, ix, iy, iw, ih, "Frequent Payments")
    ax.add_patch(Rectangle((ix, iy), iw, top - iy, facecolor="#00000018", edgecolor="none", zorder=3))

    dy, dh = iy + 1.9, 6.9
    ax.add_patch(FancyBboxPatch((ix + 0.32, dy), iw - 0.64, dh,
                                boxstyle="round,pad=0,rounding_size=0.22",
                                facecolor=PAPER, edgecolor=LINE, zorder=4))
    ax.text(ix + iw / 2, dy + dh - 0.62, "If you cancel, you will miss out on:",
            ha="center", va="center", fontsize=9.4, fontweight="bold", color=INK, zorder=5)

    bullets = ["Exclusive benefits,\nlike discounts",
               "Worry-free connection\nto your loved ones",
               "the comfort of sitting back\nwhile we do the work"]
    by = dy + dh - 1.62
    for b in bullets:
        ax.add_patch(Circle((ix + 0.78, by), 0.15, facecolor="#E9F5EE",
                            edgecolor="#2F7A57", linewidth=1, zorder=5))
        ax.text(ix + 0.78, by - 0.02, "\u2713", ha="center", va="center",
                fontsize=7, fontweight="bold", color="#2F7A57", zorder=6)
        ax.text(ix + 1.06, by, b, ha="left", va="center", fontsize=7.8,
                color=INK, zorder=5, linespacing=1.35)
        by -= 1.12

    ax.add_patch(FancyBboxPatch((ix + 0.6, dy + 1.42), iw - 1.2, 0.86,
                                boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor=RED, edgecolor=RED, zorder=5))
    ax.text(ix + iw / 2, dy + 1.85, "Keep my Advantages", ha="center", va="center",
            fontsize=9, fontweight="bold", color="white", zorder=6)
    ax.add_patch(FancyBboxPatch((ix + 0.6, dy + 0.42), iw - 1.2, 0.86,
                                boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor=PAPER, edgecolor=MUTED, zorder=5))
    ax.text(ix + iw / 2, dy + 0.85, "Remove Recurring Top Up", ha="center", va="center",
            fontsize=9, fontweight="bold", color=INK, zorder=6)

    ax.text(5, 1.62,
            "It names benefits; it grants nothing. “Keep my Advantages” is wired to close the dialog —\n"
            "no discount is applied, and no event fires, so the save cannot be counted.",
            ha="center", va="center", fontsize=8, color=MUTED, style="italic")
    stamp(ax, 1.15, 0.35, 7.7)
    save(fig, "digicel_step_3_test.png")


# --------------------------------------------------------------- step 4 ----
def step4():
    fig, ax = canvas(title="Step 6 · Completion",
                     sub="The only branch in the whole flow that emits an analytics event")
    ix, iy, iw, ih = phone(ax, 1.7, 2.55, 6.6, 10.4)
    top = header(ax, ix, iy, iw, ih, "Frequent Payments")
    ax.add_patch(Rectangle((ix, iy), iw, top - iy, facecolor=CANVAS, edgecolor="none", zorder=2))

    ax.text(ix + 0.55, top - 0.75, "AUTO TOP UP", ha="left", va="center",
            fontsize=7.4, fontweight="bold", color=MUTED, zorder=4)
    row(ax, ix, iw, top - 1.9, "+509 •••• ••••  ·  Haiti", "Every month  ·  $25.00 USD")
    ax.text(ix + iw / 2, top - 3.4, "the weekly schedule is gone",
            ha="center", va="center", fontsize=8, color=MUTED, style="italic", zorder=4)

    ax.add_patch(FancyBboxPatch((ix + 0.5, iy + 0.75), iw - 1.0, 0.95,
                                boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor="#1F2A2E", edgecolor="none", zorder=5))
    ax.text(ix + iw / 2, iy + 1.22, "Frequent payment removed", ha="center", va="center",
            fontsize=9, fontweight="bold", color="white", zorder=6)

    ax.text(5, 1.62,
            "A success snackbar, and “remove_frequent_payment” fires. No receipt, no reference number,\n"
            "and no confirmation by email or SMS is documented anywhere.",
            ha="center", va="center", fontsize=8, color=MUTED, style="italic")
    stamp(ax, 1.15, 0.35, 7.7)
    save(fig, "digicel_step_4_deleted.png")


# --------------------------------------------------------------- step 5 ----
def step5():
    fig, ax = canvas(w=8.6, h=6.4, title="The screens that do not exist",
                     sub="Sought at every step of the flow and absent from the shipped bundle, the FAQ and every published image")
    ax.set_ylim(0, 9.0)

    items = [
        ("Reason capture", "No reason key among 54 recurring-payment\nkeys across four locales"),
        ("Retention offer with value", "The dialog names discounts; the bundle\ngrants none"),
        ("Pause / skip a cycle", "No pause key — and no PUT or PATCH\nendpoint exists to build one"),
        ("Change amount, frequency,\nrecipient or payment method", "Management screen offers removal only.\nRecurring is card-only, one schedule per number"),
        ("Support handoff", "No support affordance in either dialog.\nSupport is a separate page, Mon–Sat"),
        ("Error states", "No copy published for a failed delete,\nnetwork error or expired session"),
        ("Post-cancellation win-back", "No evidence in any source, any market"),
        ("Confirmation by email or SMS", "Undocumented — the FAQ's receipt entry\ncovers purchases only"),
    ]
    x0, y0, cw, chh = 0.4, 7.7, 4.55, 0.95
    for i, (t, s) in enumerate(items):
        cx = x0 + (i % 2) * (cw + 0.35)
        cy = y0 - (i // 2) * (chh + 0.42)
        ax.add_patch(FancyBboxPatch((cx, cy - chh), cw, chh,
                                    boxstyle="round,pad=0,rounding_size=0.12",
                                    facecolor=PAPER, edgecolor="#E0C7C7", linewidth=1.1, zorder=3))
        ax.text(cx + 0.3, cy - 0.30, "✕", ha="center", va="center",
                fontsize=10, fontweight="bold", color="#C05050", zorder=4)
        ax.text(cx + 0.58, cy - 0.28, t, ha="left", va="center",
                fontsize=8.4, fontweight="bold", color=INK, zorder=4)
        ax.text(cx + 0.58, cy - 0.68, s, ha="left", va="center",
                fontsize=7.2, color=MUTED, zorder=4)

    ax.set_xlim(0, 9.9)
    ax.text(4.95, 1.15, "2 of 16 retention mechanisms are present. The absences are architectural, not stylistic.",
            ha="center", va="center", fontsize=8.6, fontweight="bold", color="#9E3232")
    stamp(ax, 1.1, 0.35, 7.7)
    save(fig, "digicel_step_5_absent.png")


if __name__ == "__main__":
    print("Rendering Digicel cancellation-flow reconstructions…")
    step1(); step2(); step3(); step4(); step5()
    print("Done.")
