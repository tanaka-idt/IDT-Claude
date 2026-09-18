#!/usr/bin/env python3
"""
Generate IMTU subscription-logic flowcharts.

Visual language mirrors the reference charts supplied by the requester:
  rounded box = state/step, diamond = decision,
  bold title + subtitle (subtitle carries the notification trigger),
  Gray = system step | Teal = positive | Amber = warning | Red = terminal.

Every fact rendered here is sourced from Jira/Confluence - see the accompanying
Google Docs for citations. Where IDT has no documented rule, the diagram says so
explicitly rather than inventing one.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

# ---------------------------------------------------------------- palette ----
GRAY  = dict(fill="#EEEBE5", edge="#A8A29A", text="#454340")
TEAL  = dict(fill="#E981EA".replace("981", "3F1"), edge="#1E7A5E", text="#186B51")
AMBER = dict(fill="#FAEBD9", edge="#C4841F", text="#8F5E0E")
RED   = dict(fill="#FBE9E9", edge="#C05050", text="#9E3232")
ARROW = "#7A7A7A"
ANNOT = "#8A8A8A"

LEGEND = "Gray = system step    Teal = positive    Amber = warning    Red = terminal"


def box(ax, cx, cy, w, h, title, sub=None, style=GRAY, title_size=12, sub_size=9.5):
    """Rounded rectangle with bold title and optional subtitle."""
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.16",
        linewidth=1.5, facecolor=style["fill"], edgecolor=style["edge"], zorder=2))
    if sub:
        ax.text(cx, cy + h * 0.17, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=style["text"], zorder=3)
        ax.text(cx, cy - h * 0.22, sub, ha="center", va="center",
                fontsize=sub_size, color=style["text"], alpha=0.85, zorder=3)
    else:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=style["text"], zorder=3)


def diamond(ax, cx, cy, w, h, label, size=11):
    """Decision diamond."""
    ax.add_patch(Polygon(
        [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
        closed=True, linewidth=1.5,
        facecolor=GRAY["fill"], edgecolor=GRAY["edge"], zorder=2))
    ax.text(cx, cy, label, ha="center", va="center",
            fontsize=size, color=GRAY["text"], zorder=3)


def arrow(ax, p0, p1, label=None, lpos=0.5, ldx=0.0, ldy=0.12, dashed=False,
          lsize=9.5, connector=None):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=13,
        linewidth=1.4, color=ARROW, zorder=1,
        linestyle="--" if dashed else "-",
        connectionstyle=connector or "arc3,rad=0",
        shrinkA=0, shrinkB=0))
    if label:
        lx = p0[0] + (p1[0] - p0[0]) * lpos + ldx
        ly = p0[1] + (p1[1] - p0[1]) * lpos + ldy
        ax.text(lx, ly, label, ha="center", va="center",
                fontsize=lsize, color=ANNOT, zorder=4,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))


def elbow(ax, p0, p1, label=None, ldx=0.0, ldy=0.15, lsize=9.5, first="v"):
    """Right-angle connector. first='v' goes vertical then horizontal."""
    mid = (p0[0], p1[1]) if first == "v" else (p1[0], p0[1])
    ax.plot([p0[0], mid[0]], [p0[1], mid[1]], color=ARROW, lw=1.4, zorder=1)
    ax.add_patch(FancyArrowPatch(
        mid, p1, arrowstyle="-|>", mutation_scale=13,
        linewidth=1.4, color=ARROW, zorder=1, shrinkA=0, shrinkB=0))
    if label:
        ax.text((p0[0] + p1[0]) / 2 + ldx, (p0[1] + p1[1]) / 2 + ldy, label,
                ha="center", va="center", fontsize=lsize, color=ANNOT, zorder=4,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))


def note(ax, cx, cy, text, size=9.5):
    ax.text(cx, cy, text, ha="center", va="center",
            fontsize=size, color=ANNOT, style="italic", zorder=3)


def canvas(w, h, xlim, ylim, title=None):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.axis("off"); ax.set_aspect("equal")
    if title:
        ax.text((xlim[0] + xlim[1]) / 2, ylim[1] - 0.35, title,
                ha="center", va="top", fontsize=15, fontweight="bold", color="#333")
    return fig, ax


def finish(fig, ax, xlim, ylim, path, legend=True):
    if legend:
        ax.text((xlim[0] + xlim[1]) / 2, ylim[0] + 0.28, LEGEND,
                ha="center", va="center", fontsize=9.5, color=ANNOT)
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


# ============================================================ 1. LIFECYCLE ====
def chart_lifecycle(path):
    XL, YL = (0, 20), (0, 27)
    fig, ax = canvas(13, 17.5, XL, YL,
                     "IMTU Subscription — Full Lifecycle")
    C, BW, BH = 10, 5.4, 1.5

    box(ax, C, 25.0, BW, BH, "Offer Confirmation Page",
        "subscription toggle evaluated", GRAY)
    arrow(ax, (C, 24.25), (C, 23.35))

    box(ax, C, 22.6, BW, BH, "Purchase with subscription",
        "toggle ON at checkout", GRAY)
    arrow(ax, (C, 21.85), (C, 20.95))

    box(ax, C, 20.2, BW + 0.5, BH, "Subscription created",
        "purchase confirmation push sent", TEAL)
    note(ax, C + 5.4, 20.2, "first charge is taken on the\npurchase date — there is no trial")
    arrow(ax, (C, 19.45), (C, 18.55))

    box(ax, C, 17.8, BW, BH, "Subscription active",
        "timer scheduled (launch_at)", GRAY)
    note(ax, C + 5.5, 17.8, "cadence: 7 / 14 / 30 / 90 days")
    arrow(ax, (C, 17.05), (C, 16.15))

    box(ax, C, 15.4, BW + 0.6, BH, "Renewal reminder",
        "push sent 2 days before charge", TEAL)
    arrow(ax, (C, 14.65), (C, 13.75))

    box(ax, C, 13.0, BW + 0.4, BH, "Renewal charge attempted",
        "wallet first, then card on profile", GRAY)
    arrow(ax, (C, 12.25), (C, 11.5))

    diamond(ax, C, 10.4, 5.2, 1.9, "Charge successful?")

    # success branch
    elbow(ax, (C - 2.6, 10.4), (4.6, 8.6), "yes", ldx=-0.5, ldy=0.65, first="h")
    box(ax, 4.6, 7.85, BW - 0.2, BH, "Top-up delivered",
        "delivery confirmation push", TEAL)
    note(ax, 4.6, 6.75, "next cycle scheduled — stays active")

    # failure branch
    elbow(ax, (C + 2.6, 10.4), (15.4, 8.6), "no", ldx=0.5, ldy=0.65, first="h")
    box(ax, 15.4, 7.85, BW + 0.3, BH, "Payment failed",
        "no customer notification", AMBER)
    arrow(ax, (15.4, 7.1), (15.4, 6.3))

    diamond(ax, 15.4, 5.2, 5.4, 1.9, "Alternate payment\non file?", size=10)

    elbow(ax, (15.4 - 2.7, 5.2), (7.6, 3.3), "yes", ldx=-0.45, ldy=0.6, first="h")
    box(ax, 7.6, 2.55, BW + 0.3, BH, "Charged to alternate",
        "SMS sent (EMMS)", TEAL)
    note(ax, 7.6, 1.4, "next charge reverts\nto the original card")

    arrow(ax, (15.4, 4.25), (15.4, 3.3), "no", ldx=0.45, ldy=0.15)
    box(ax, 15.4, 2.55, BW + 0.3, BH, "Stays ACTIVE, failing",
        "no retry · no cancel · silent", RED)
    note(ax, 15.4, 1.4, "no dunning ladder — it simply\nretries next cycle, indefinitely")

    finish(fig, ax, XL, YL, path)


# =============================================================== 2. TOGGLE ====
def chart_toggle(path):
    # Geometry note: each gate's "yes" branch runs horizontally at the diamond's
    # own y, then drops into its box. Rows are spaced so that horizontal run
    # always passes well clear of the box belonging to the gate above it.
    XL, YL = (0, 22), (2.0, 19.4)
    fig, ax = canvas(13.5, 10.9, XL, YL,
                     "Subscription Toggle — Default-State Decision Logic")
    C, L, BW, BH = 11.0, 3.9, 5.2, 1.45
    HALF = BH / 2

    box(ax, C, 17.4, BW + 1.0, BH, "Offer Confirmation Page opens",
        "backend evaluates eligibility", GRAY)
    arrow(ax, (C, 17.4 - HALF), (C, 16.05))

    # --- gate 1: duplicate
    diamond(ax, C, 15.0, 7.6, 2.1,
            "Active subscription for same\nuser + recipient + offer?", size=10)
    elbow(ax, (C - 3.8, 15.0), (L, 12.9 + HALF), "yes", ldy=1.04, first="h")
    box(ax, L, 12.9, BW, BH, "Toggle OFF", "reason: duplicate", AMBER)
    note(ax, L, 12.9 - HALF - 0.42, "duplicate warning shown")

    # --- gate 2: max subscriptions
    arrow(ax, (C, 13.95), (C, 12.0), "no", ldx=0.45, ldy=0.0)
    diamond(ax, C, 11.0, 5.8, 2.0, "Active subscriptions ≥ 3?", size=10)
    elbow(ax, (C - 2.9, 11.0), (L, 8.6 + HALF), "yes", ldy=1.19, first="h")
    box(ax, L, 8.6, BW, BH, "Toggle OFF", "reason: max_subscriptions", AMBER)

    # --- fall-through: no gate fired
    arrow(ax, (C, 10.0), (C, 8.6 + HALF), "no", ldx=0.45, ldy=0.0)
    box(ax, C, 8.6, BW, BH, "Toggle ON", "reason: default", TEAL)

    note(ax, 18.6, 12.5,
         "Soft restriction:\nOFF never blocks the user.\nThey may always enable\n"
         "the toggle manually.")

    # --- convergence: parallel drops into one wide box, no elbows needed
    arrow(ax, (L, 8.6 - HALF), (L, 6.4 + HALF))
    arrow(ax, (C, 8.6 - HALF), (C, 6.4 + HALF))
    box(ax, 7.45, 6.4, 8.8, BH, "User taps Buy",
        "toggle state as presented, or overridden", GRAY)
    arrow(ax, (7.45, 6.4 - HALF), (7.45, 4.2 + HALF))

    box(ax, 7.45, 4.2, BW + 1.0, BH, "Purchase completes",
        "single or subscription", TEAL)

    finish(fig, ax, XL, YL, path)


# ============================================== 3. RENEWAL PAYMENT HANDLING ====
def chart_renewal(path):
    XL, YL = (0, 21), (0, 24)
    fig, ax = canvas(13.5, 15.5, XL, YL,
                     "Renewal Charge — Payment Decision Logic")
    C, BW, BH = 10.5, 5.6, 1.45

    box(ax, C, 22.2, BW + 1.2, BH, "Timer fires (launch_at)",
        "jittered up to 1440 min to avoid rate limits", GRAY)
    arrow(ax, (C, 21.48), (C, 20.6))

    diamond(ax, C, 19.5, 5.8, 1.9, "Wallet balance\ncovers total?", size=10)
    elbow(ax, (C - 2.9, 19.5), (3.6, 17.6), "yes", ldx=-0.5, ldy=0.6, first="h")
    box(ax, 3.6, 16.85, BW - 0.4, BH, "Charged to wallet", "BOSS Cash used", TEAL)

    arrow(ax, (C, 18.55), (C, 17.6), "no", ldx=0.4, ldy=0.15)
    box(ax, C, 16.85, BW + 0.6, BH, "Charge card on profile",
        "cvv_verified gate applies", GRAY)
    arrow(ax, (C, 16.12), (C, 15.2))

    diamond(ax, C, 14.1, 5.4, 1.9, "Authorisation OK?", size=10)
    elbow(ax, (C - 2.7, 14.1), (3.6, 12.2), "yes", ldx=-0.5, ldy=0.6, first="h")
    box(ax, 3.6, 11.45, BW - 0.4, BH, "Top-up delivered",
        "success push sent", TEAL)
    note(ax, 3.6, 10.35, "subscription remains active")

    arrow(ax, (C, 13.15), (C, 12.2), "no", ldx=0.4, ldy=0.15)
    box(ax, C, 11.45, BW + 0.8, BH, "Payment failed",
        "error_reason recorded", AMBER)
    arrow(ax, (C, 10.72), (C, 9.8))

    diamond(ax, C, 8.7, 6.2, 1.95, "Another payment method\non file?", size=10)

    elbow(ax, (C - 3.1, 8.7), (3.6, 6.7), "yes", ldx=-0.5, ldy=0.6, first="h")
    box(ax, 3.6, 5.95, BW + 0.2, BH, "Charged to 2nd method",
        "SMS sent (EMMS)", TEAL)
    note(ax, 3.6, 4.7, "next cycle reverts to\nthe original card")

    arrow(ax, (C, 7.72), (C, 6.7), "no", ldx=0.4, ldy=0.15)
    box(ax, C, 5.95, BW + 0.8, BH, "No charge taken",
        "no customer notification", AMBER)
    arrow(ax, (C, 5.22), (C, 4.35))

    box(ax, C, 3.6, BW + 1.6, BH + 0.15, "Subscription stays ACTIVE",
        "no retry schedule · no cancellation · no cooldown", RED)
    note(ax, C, 2.25,
         "The charge is simply re-attempted at the next scheduled cycle.\n"
         "28.4% of active subscriptions are in this failing state.")

    note(ax, 17.6, 8.7, "IMTU has no\ndunning ladder.\nFallback happens\nwithin one attempt,\nnot across days.")

    finish(fig, ax, XL, YL, path)


# =================================================== 4. CANCEL / MODIFY ========
def chart_cancel(path):
    XL, YL = (0, 20), (0, 17)
    fig, ax = canvas(13, 11.5, XL, YL,
                     "Cancellation and Modification")
    BW, BH = 5.2, 1.45

    box(ax, 10, 15.2, BW + 1.0, BH, "Change requested",
        "Edit Subscription opened", GRAY)
    arrow(ax, (10, 14.48), (10, 13.6))

    diamond(ax, 10, 12.5, 5.4, 1.9, "Cancel or modify?", size=11)

    # modify
    elbow(ax, (10 - 2.7, 12.5), (4.0, 10.6), "modify", ldx=-0.6, ldy=0.6, first="h")
    box(ax, 4.0, 9.85, BW + 0.2, BH, "Subscription updated",
        "update push sent", TEAL)
    note(ax, 4.0, 8.75, "returns to active subscription")
    arrow(ax, (4.0, 8.35), (4.0, 7.5))
    box(ax, 4.0, 6.75, BW + 0.4, BH, "Schedule recalculated",
        "frequency / offer / payment method", GRAY)
    note(ax, 4.0, 5.5, "no proration — IMTU charges\nper cycle, not per term")

    # cancel
    elbow(ax, (10 + 2.7, 12.5), (15.6, 10.6), "cancel", ldx=0.6, ldy=0.6, first="h")
    box(ax, 15.6, 9.85, BW + 0.4, BH, "Cancellation confirmed",
        "immediate — no retention offer", AMBER)
    arrow(ax, (15.6, 9.12), (15.6, 8.25))
    box(ax, 15.6, 7.5, BW + 0.4, BH, "Subscription ended",
        "no further charges", RED)
    note(ax, 15.6, 6.3, "user may resubscribe at any time —\nno cooldown period")

    # system-initiated
    box(ax, 10, 3.4, BW + 4.4, BH + 0.2, "System-initiated cancellation",
        "phone disconnected · profile locked >3 months · profile deleted · offer withdrawn",
        AMBER, sub_size=9)
    note(ax, 10, 1.9,
         "Cancellation push carries the reason. Note: payment failure is NOT a cancellation trigger.")

    finish(fig, ax, XL, YL, path)


# ===================================================== 5. OFFER LIFECYCLE ======
def chart_offer(path):
    XL, YL = (0, 20), (0, 16)
    fig, ax = canvas(13, 11, XL, YL,
                     "Offer Withdrawn — Substitution or Cancellation")
    BW, BH = 5.4, 1.45

    box(ax, 10, 14.2, BW + 1.4, BH, "Offer discontinued in K2",
        "Kafka event emitted", GRAY)
    arrow(ax, (10, 13.48), (10, 12.6))

    diamond(ax, 10, 11.5, 6.0, 1.95, "Substitute offer\navailable?", size=10.5)

    # substitute
    elbow(ax, (10 - 3.0, 11.5), (4.0, 9.4), "yes", ldx=-0.5, ldy=0.6, first="h")
    box(ax, 4.0, 8.65, BW + 0.6, BH, "Migrated to substitute",
        "push: subscription adjusted", TEAL)
    note(ax, 4.0, 7.5, "applied at the Kafka event")
    arrow(ax, (4.0, 7.1), (4.0, 6.3))
    box(ax, 4.0, 5.55, BW + 0.4, BH, "Subscription continues",
        "My Activity: updated with new offer", GRAY)
    note(ax, 4.0, 4.3, "frequency retained —\nunder PM review")

    # no substitute
    elbow(ax, (10 + 3.0, 11.5), (15.8, 9.4), "no", ldx=0.5, ldy=0.6, first="h")
    box(ax, 15.8, 8.65, BW + 0.6, BH, "Cancellation scheduled",
        "push: update to another offer", AMBER)
    note(ax, 15.8, 7.5, "user may switch offer to keep it")
    arrow(ax, (15.8, 7.1), (15.8, 6.3))
    box(ax, 15.8, 5.55, BW + 0.6, BH, "Cancelled on iteration date",
        "not at the Kafka event", RED)
    note(ax, 15.8, 4.3, "My Activity: offer no\nlonger available")

    note(ax, 10, 2.2,
         "Country scoping is essential here: a December 2025 defect ignored country and\n"
         "cancelled 29,474 subscriptions across 17,464 users. The flow was disabled and reinstated.")

    finish(fig, ax, XL, YL, path)


if __name__ == "__main__":
    chart_lifecycle("imtu_sub_flow_1_lifecycle.png")
    chart_toggle("imtu_sub_flow_2_toggle.png")
    chart_renewal("imtu_sub_flow_3_renewal.png")
    chart_cancel("imtu_sub_flow_4_cancel_modify.png")
    chart_offer("imtu_sub_flow_5_offer.png")
    print("all diagrams generated")
