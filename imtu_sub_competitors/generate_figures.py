"""Figures for the IMTU subscription competitor study (Sep 2026).

Run: python3 generate_figures.py [name ...]   (no args = all)
Writes PNGs to figures/. Data comes from data.py and data/idt_weekly_subs.json.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

import data as D
from figkit import (BASE, BOX, Flow, GRID, INK, INK2, MUTED, NEUTRAL, OTHER, SEQ, SERIES, STATUS, SURFACE,
                    finish, hairline, wrap)

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
FIGS = {}


def fig(fn):
    FIGS[fn.__name__] = fn
    return fn


# ---------------------------------------------------------------- capability heatmap
@fig
def capabilities():
    caps = D.CAPABILITIES
    players = D.PLAYERS
    fig = plt.figure(figsize=(9.4, 8.6))
    ax = fig.add_axes([0.33, 0.07, 0.66, 0.74])
    ncol, nrow = len(players), len(caps)
    style = {"Y": (SEQ["full"], "#ffffff", "Yes"), "P": (SEQ["partial"], INK, "Part"),
             "N": (NEUTRAL, INK2, "No"), "-": ("#ffffff", MUTED, "n/a"), "?": ("#ffffff", MUTED, "?")}
    for r, (ck, clabel) in enumerate(caps):
        for c, (pk, _, _) in enumerate(players):
            v = D.MATRIX[pk][ck]
            face, ink, txt = style[v]
            ax.add_patch(Rectangle((c + 0.04, r + 0.06), 0.92, 0.88, facecolor=face,
                                   edgecolor=BASE if v in "-?" else face, lw=0.7))
            ax.text(c + 0.5, r + 0.52, txt, ha="center", va="center", fontsize=7.6, color=ink,
                    fontweight="bold" if v == "Y" else "normal")
        ax.text(-0.15, r + 0.52, clabel, ha="right", va="center", fontsize=8.6, color=INK)
    for c, (pk, _, short) in enumerate(players):
        ax.text(c + 0.5, -0.25, short, ha="left", va="bottom", rotation=38, fontsize=8.6,
                color=INK, fontweight="bold" if pk == "idt" else "normal")
    ax.add_patch(Rectangle((0, 0), 1, nrow, fill=False, edgecolor=SERIES[0], lw=2.2))
    ax.set_xlim(0, ncol)
    ax.set_ylim(nrow, -0.05)
    ax.axis("off")
    # legend
    lx = 0.33
    for i, (k, lab) in enumerate([("Y", "Yes"), ("P", "Partial or limited"), ("N", "No"), ("?", "Not verified publicly"),
                                  ("-", "Not applicable")]):
        face, ink, _ = style[k]
        fig.patches.append(Rectangle((lx, 0.018), 0.014, 0.016, transform=fig.transFigure, facecolor=face,
                                     edgecolor=BASE, lw=0.6))
        fig.text(lx + 0.019, 0.026, lab, fontsize=7.8, color=INK2, va="center")
        lx += 0.036 + len(lab) * 0.0072
    finish(fig, OUT / "fig_capabilities.png",
           title="Recurring top-up capabilities across the market",
           subtitle="Public evidence as of 29 Sep 2026. IDT is outlined. Detail and sources in the comparison tables.")


# ---------------------------------------------------------------- app scale
@fig
def scale():
    rows = sorted(D.APP_SCALE, key=lambda r: r[1])
    fig = plt.figure(figsize=(8.6, 5.2))
    ax = fig.add_axes([0.25, 0.10, 0.70, 0.74])
    y = range(len(rows))
    cols = [SERIES[0] if r[4] else OTHER for r in rows]
    ax.barh(list(y), [r[1] for r in rows], color=cols, height=0.62, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    for i, r in enumerate(rows):
        ax.text(r[1] + 3000, i, f"{r[1]/1000:,.1f}k  ({r[2]:.2f}★)", va="center", fontsize=8.2, color=INK2)
    hairline(ax, "x")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax.set_xlim(0, 340000)
    ax.set_xlabel("US App Store ratings (count)", fontsize=8.5)
    finish(fig, OUT / "fig_scale.png", title="Boss Revolution has the largest rating base of any top-up app",
           subtitle="US App Store rating count and average stars, 29 Sep 2026. IDT apps in blue.",
           source="Source: iTunes lookup API (US storefront). Cuba specialists sell almost only to Cuba; Remitly (2.75M) and WU (1.33M) do not sell top-up subscriptions.")


# ---------------------------------------------------------------- IDT cancellation curve
@fig
def idt_cancel():
    fig = plt.figure(figsize=(8.6, 4.4))
    ax = fig.add_axes([0.08, 0.16, 0.52, 0.62])
    xs = list(range(len(D.IDT_CANCEL)))
    vals = [v for _, v in D.IDT_CANCEL]
    ax.plot(xs, vals, color=SERIES[0], lw=2, marker="o", ms=6, zorder=3)
    for x, v in zip(xs, vals):
        ax.text(x, v + 1.8, f"{v:.1f}%", ha="center", fontsize=8.2, color=INK)
    x60 = len(xs)
    ax.plot([xs[-1], x60], [vals[-1], D.IDT_CANCEL_60D_DEFAULT_ON], color=SERIES[0], lw=1.4, ls=(0, (3, 2)))
    ax.plot([x60], [D.IDT_CANCEL_60D_DEFAULT_ON], marker="o", ms=6, color=SURFACE, markeredgecolor=SERIES[0], mew=1.6)
    ax.text(x60, D.IDT_CANCEL_60D_DEFAULT_ON + 2.2, f"{D.IDT_CANCEL_60D_DEFAULT_ON:.1f}%\n(default-ON cohort)", ha="center",
            fontsize=7.8, color=INK2)
    ax.set_xticks(xs + [x60])
    ax.set_xticklabels(["1 day", "3 days", "7 days", "14 days", "30 days", "60 days"], fontsize=8)
    ax.set_xlim(-0.4, x60 + 0.6)
    ax.set_ylim(0, 56)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    hairline(ax, "y")
    ax.set_title("Share of new subscriptions cancelled within N days", loc="left", fontsize=9.5, color=INK)
    ax.axvline(xs[-1], color=GRID, lw=0.8, zorder=0)
    ax.text(xs[-1] + 0.08, 3, "first monthly\ncharge", fontsize=7.4, color=MUTED)
    ax2 = fig.add_axes([0.70, 0.16, 0.27, 0.62])
    labs = list(D.IDT_CANCEL_30D_BY_CADENCE.keys())
    vs = list(D.IDT_CANCEL_30D_BY_CADENCE.values())
    ax2.bar([0, 1], vs, color=[SERIES[0], SERIES[0]], width=0.55, zorder=3)
    for i, v in enumerate(vs):
        ax2.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=8.6, color=INK, fontweight="bold")
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels([wrap(l, 12) for l in labs], fontsize=8)
    ax2.set_ylim(0, 56)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    hairline(ax2, "y")
    ax2.set_title("Cancelled within 30 days, by cadence", loc="left", fontsize=9.5, color=INK)
    finish(fig, OUT / "fig_idt_cancel.png", title="One in three new IDT subscriptions is cancelled within a month",
           subtitle="BR app, 272,026 subscription purchasers, 1 Mar to 1 Aug 2026. Rates are floors (right-censored).",
           source="Sources: IMTU Subscription Journey v2 (31 Aug 2026); 60-day default-ON cohort from the 3 Sep 2026 toggle analysis.")


# ---------------------------------------------------------------- Rebtel plan deltas
@fig
def rebtel_plans():
    rows = sorted(D.REBTEL_PLAN_DELTAS, key=lambda r: r[1])
    fig = plt.figure(figsize=(8.6, 7.2))
    ax = fig.add_axes([0.33, 0.10, 0.62, 0.76])
    y = range(len(rows))
    cols = [SERIES[0] if v < 0 else "#e34948" for _, v in rows]
    ax.barh(list(y), [v for _, v in rows], color=cols, height=0.64, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.2)
    for i, (_, v) in enumerate(rows):
        ax.text(v + (-1 if v < 0 else 1), i, f"{v:+.1f}%", va="center", ha="right" if v < 0 else "left", fontsize=7.6,
                color=INK2)
    ax.axvline(0, color=BASE, lw=1)
    hairline(ax, "x")
    ax.set_xlim(-55, 30)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:+.0f}%"))
    ax.set_xlabel("Plan price vs closest one-time bundle with the same content", fontsize=8.5)
    finish(fig, OUT / "fig_rebtel_plans.png", title="Rebtel Plans: subscribing is usually 8 to 15% cheaper",
           subtitle="24 subscription-only Plans vs matching one-time bundles, US prices, 29 Sep 2026. Blue = Plan cheaper, red = dearer.",
           source="Source: Rebtel public product catalog. Matching by content and validity. 11 Plans also carry a first-period teaser (e.g. Telcel $3.99, then $14).")


# ---------------------------------------------------------------- reviews
@fig
def reviews():
    fig = plt.figure(figsize=(8.6, 4.4))
    ax = fig.add_axes([0.20, 0.14, 0.36, 0.64])
    rows = list(reversed(D.REVIEW_SHARE_2026))
    y = range(len(rows))
    ax.barh(list(y), [r[1] for r in rows], color=[SERIES[0] if r[0].startswith(("Boss", "BOSS")) else OTHER for r in rows],
            height=0.6, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{r[0]} (n={r[2]})" for r in rows], fontsize=8.2)
    for i, r in enumerate(rows):
        ax.text(r[1] + 0.15, i, f"{r[1]:.1f}%", va="center", fontsize=8.2, color=INK2)
    hairline(ax, "x")
    ax.set_xlim(0, 9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_title("2026 reviews that mention subscriptions", loc="left", fontsize=9.5, color=INK)
    ax2 = fig.add_axes([0.66, 0.14, 0.31, 0.64])
    m = D.BR_REVIEW_MONTHS
    share = [a / b * 100 for _, a, b in m]
    ax2.bar(range(len(m)), share, color=SERIES[0], width=0.6, zorder=3)
    for i, (lab, a, b) in enumerate(m):
        ax2.text(i, share[i] + 0.25, f"{a}/{b}", ha="center", fontsize=7.6, color=INK2)
    ax2.set_xticks(range(len(m)))
    ax2.set_xticklabels([x[0] for x in m], fontsize=8.2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax2.set_ylim(0, 9)
    hairline(ax2, "y")
    ax2.set_title("Boss Revolution by month, 2026", loc="left", fontsize=9.5, color=INK)
    finish(fig, OUT / "fig_reviews.png", title="Subscription complaints spiked in BR reviews from July 2026",
           subtitle="US App Store written reviews, hand-coded (7,367 reviews, 10 apps). BR: 0.4% Apr to Jun vs 5.0% Jul to Sep (p = 0.0008).",
           source="Source: App Store RSS feed, pulled 29 Sep 2026. *September to the 26th. None of the BR reviews names the top-up subscription explicitly.")


# ---------------------------------------------------------------- subscription model spectrum
@fig
def models():
    f = Flow(10.4, 5.3, height=100)
    cols = [
        ("Reminder only", "The app reminds; the sender still pays each time", "step",
         ["Recharge.com (recharge reminder)", "Western Union US (transfer reminders)"]),
        ("Promo-triggered delivery", "Reserve now, delivered when the carrier promo starts", "step",
         ["Cuballama, Ensip (Cuba preventa)", "Ding 'Reserva tu Recarga' (Cubacel)"]),
        ("Calendar auto top-up", "Same price as one-time, repeats on a cadence", "offer",
         ["Ding (7/14/28/30 days)", "MobileRecharge, TopUp.com", "Digicel, Natcom, Telcel portal",
          "Rebtel Auto Top-Up", "IDT (7/14/30/90 days, default ON)"]),
        ("Subscription-only plans", "Cheaper SKUs that only exist as a subscription", "good",
         ["Rebtel Plans (36 SKUs, 6 countries)", "Rebtel teasers: $3.99 first month"]),
        ("Paid membership", "A monthly fee for credits, points and perks", "warn",
         ["dingVIP PLUS ($5/mo, 7-day trial)", "Remitly One ($9.99/mo, no top-up)"]),
    ]
    xs = [10.5, 30.25, 50, 69.75, 89.5]
    for x, (title, sub, style, who) in zip(xs, cols):
        f.box(title, x, 31, 18.2, 16, title, sub, style=style, title_size=9.6, sub_size=7.6, wrap_at=22)
        for i, w in enumerate(who):
            f.box(title + str(i), x, 50 + i * 9.4, 18.2, 7.6, w, style="offer" if w.startswith("IDT") else "ghost",
                  title_size=7.4, wrap_at=30)
    f.ax.annotate("", xy=(98.5, 18), xytext=(1.5, 18),
                  arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2, mutation_scale=12))
    f.ax.text(1.5, 16.2, "Less commitment and value for the sender", fontsize=8, color=MUTED, ha="left", va="bottom")
    f.ax.text(98.5, 16.2, "More commitment and value", fontsize=8, color=MUTED, ha="right", va="bottom")
    f.save(OUT / "fig_models.png", title="Five ways the market sells recurring top-ups",
           subtitle="Where each player sits, Sep 2026. IDT runs a calendar auto top-up that is switched on by default.")



# ---------------------------------------------------------------- opt-in flows side by side
@fig
def optin_flows():
    f = Flow(10.6, 8.0, height=112)
    lanes = [
        ("IDT (BR app 26.9.3)", [
            ("Pick offer", "offer list, recipient", "step"),
            ("Order screen", "subscription section in the payment bar, cadence 7/14/30/90", "step"),
            ("Toggle ON by default", "copy: 'You will save $X every month'", "risk"),
            ("'Subscribe & Pay'", "first charge now, then every cycle", "step"),
            ("Renewals", "push 2 days before; a failed charge is silent, no retry", "warn"),
        ]),
        ("Ding (app and web)", [
            ("Pick amount", "Top-up or Plans tab", "step"),
            ("'Set auto top-up' modal", "7/14/28/30 chips, 30 highlighted, 'No thanks'", "good"),
            ("Order summary", "'Auto top-up every 30 days', edit or remove", "good"),
            ("Pay now or pick a start date", "no upfront payment in the 2025 flow", "good"),
            ("Renewals", "declined card cancels the auto top-up", "warn"),
        ]),
        ("Rebtel (web and app)", [
            ("Pick product", "Plans ('Subscribe', teaser price) or credits", "step"),
            ("Checkout choice", "'Pay once' vs 'Auto Top Up'; legacy modal forces a cadence pick", "good"),
            ("First order is normal", "schedule created after it succeeds", "good"),
            ("Post-purchase upsell", "'Top up automatically every X?' Yes / No", "offer"),
            ("Renewals", "declined card deactivates; no reminder found", "warn"),
        ]),
        ("MobileRecharge / Digicel", [
            ("Pick amount", "carrier product or plan", "step"),
            ("Checkout checkbox", "'Activate Auto Top-up' / 'Auto pay enabled'", "offer"),
            ("Every 7/14/28/30 days", "free service, saved card only", "step"),
            ("Digicel home nudge", "'Renew before it's too late'", "good"),
            ("Cancel", "delete link in the account (Digicel)", "step"),
        ]),
    ]
    top = 12
    lane_h = 24
    for li, (name, steps) in enumerate(lanes):
        y0 = top + li * lane_h
        f.lane(y0, y0 + lane_h - 2.4, name, fc="#eef4fc" if li == 0 else "#f7f6f2")
        xs = [11.5, 30.5, 49.5, 68.5, 87.5]
        for si, (t, s, st) in enumerate(steps):
            f.box(f"{li}_{si}", xs[si], y0 + 12.5, 16.6, 13.2, t, s, style=st, title_size=8.2, sub_size=6.9, wrap_at=22)
            if si:
                f.arrow(f"{li}_{si-1}", f"{li}_{si}", "right", "left")
    f.save(OUT / "fig_optin_flows.png", title="How each player turns a top-up into a subscription",
           subtitle="Reconstructed from public help centres, store screenshots, client code and IDT's Figma handoff. Red = default ON, green = explicit choice.",
           legend="Grey = step    Blue = offer moment    Green = consent or control the sender sees    Amber = weak point    Red = pre-ticked default")


# ---------------------------------------------------------------- failed payment handling
@fig
def failed_payment():
    f = Flow(10.6, 5.8, height=84)
    rows = [
        ("IDT today", "Stays active and silent", "No retry, no message; tried again next cycle. 28% of subscriptions were failing (Apr 2026); card removal is the de facto cancel.", "risk"),
        ("Ding", "Cancelled on first decline", "Terms section 8: a declined payment cancels the auto top-up; user must set a new one.", "warn"),
        ("Rebtel", "Deactivated on decline", "ToS 2.16: declined method deactivates the Auto Top-Up; no documented retry or grace.", "warn"),
        ("MobileRecharge", "12-hour retries, then off", "Retries for 12 hours, then switches the Auto Top-up off; also switches off on an operator change or a price rise above 6%.", "warn"),
        ("Best practice", "Retry ladder + notice + updater", "Card account updater and network tokens, 2-3 smart retries over ~7 days, SMS/push 'update your card', grace before the recipient is affected, auto-cancel after N (IDT's tiered 3/2 rule).", "good"),
    ]
    for i, (who, what, detail, st) in enumerate(rows):
        y = 16 + i * 15
        f.box(f"w{i}", 10, y, 16, 11, who, style="step", title_size=9)
        f.box(f"s{i}", 31, y, 22, 11, what, style=st, title_size=8.8, wrap_at=24)
        f.note(44, y, detail, size=7.8, width=78, style="normal", color=INK2)
        f.arrow(f"w{i}", f"s{i}", "right", "left")
    f.save(OUT / "fig_failed_payment.png", title="What happens when a renewal payment fails",
           subtitle="Only MobileRecharge documents a retry window, and only for 12 hours. About a third of consumer subscription churn is failed payments (Recurly, Jul 2026).")



# ---------------------------------------------------------------- 12-month timeline
DAYS_PER_CHAR = 2.35


def _bar(ax, d0, d1, y, text, color, h=0.2, alpha=1.0, text_color="#ffffff"):
    import matplotlib.dates as mdates
    x0, x1 = mdates.date2num(d0), mdates.date2num(d1)
    ax.add_patch(Rectangle((x0, y - h / 2), x1 - x0, h, facecolor=color, alpha=alpha, edgecolor="none", zorder=3))
    if len(text) * DAYS_PER_CHAR + 6 < (x1 - x0):
        ax.text(x0 + 3, y, text, fontsize=7.4, color=text_color, va="center", zorder=4)
    else:
        ax.text(x1 + 3, y, text, fontsize=7.4, color=INK2, va="center", zorder=4)


@fig
def timeline():
    import datetime as dt
    import matplotlib.dates as mdates
    fig = plt.figure(figsize=(10.6, 6.0))
    ax = fig.add_axes([0.16, 0.10, 0.81, 0.74])
    start, end = dt.date(2026, 10, 1), dt.date(2027, 9, 30)
    lanes = ["Regulation", "Corridors and carriers", "Competitors", "IDT (in flight)"]
    for i, lane in enumerate(lanes):
        ax.add_patch(Rectangle((mdates.date2num(start), i - 0.46), mdates.date2num(end) - mdates.date2num(start), 0.92,
                               facecolor="#f5f4ef" if i % 2 else "#fbfaf7", edgecolor="none", zorder=0))
        ax.text(mdates.date2num(start) - 6, i, lane, ha="right", va="center", fontsize=9, color=INK, fontweight="bold")

    def point(d, y, text, color=SERIES[0]):
        x = mdates.date2num(d)
        ax.plot([x], [y], marker="o", ms=6.5, color=color, zorder=3)
        ax.text(x + 3, y, text, fontsize=7.4, color=INK2, va="center", zorder=4)

    point(dt.date(2026, 10, 1), -0.27, "NYC auto-renewal rule in force (1 Oct)")
    point(dt.date(2027, 1, 1), -0.27, "Louisiana auto-renewal law (1 Jan)")
    point(dt.date(2027, 1, 18), 0.03, "GENIUS Act (stablecoins) effective by 18 Jan at the latest")
    _bar(ax, dt.date(2026, 10, 1), dt.date(2027, 9, 30), 0.31, "FTC negative-option rulemaking restarted (ANPRM Mar 2026); a proposed rule can land any time",
         OTHER, h=0.16, text_color=INK)
    for m in range(12):
        d = dt.date(2026 + (9 + m) // 12, (9 + m) % 12 + 1, 20)
        ax.plot([mdates.date2num(d)], [1 - 0.27], marker="|", ms=9, mew=2, color="#eda100", zorder=3)
    ax.text(mdates.date2num(dt.date(2026, 10, 2)), 1 - 0.37, "Cubacel x5 / x6 promo windows: roughly monthly, 3 to 7 days, no fixed calendar",
            fontsize=7.4, color=INK2, va="bottom")
    point(dt.date(2026, 12, 15), 1.02, "Holiday peak", color=MUTED)
    point(dt.date(2027, 5, 10), 1.02, "Mother's Day, Mexico (10 May)", color=MUTED)
    _bar(ax, dt.date(2026, 10, 15), dt.date(2026, 12, 31), 1.3, "Mexico CURP suspensions of unregistered prepaid lines (digits 4 to 9)",
         "#e34948", h=0.16)
    point(dt.date(2026, 10, 1), 2 - 0.27, "dingVIP paid membership live (Sep 2026) and rolling out", color=SERIES[1])
    point(dt.date(2027, 3, 1), 2.02, "Western Union and Intermex: closing pending (California DFPI)", color=MUTED)
    _bar(ax, dt.date(2026, 10, 1), dt.date(2027, 6, 30), 2.3, "Félix Pago: WhatsApp recargas, $200M raise; Brazil, Venezuela, savings and loans next",
         SERIES[1], h=0.16)
    _bar(ax, dt.date(2026, 10, 1), dt.date(2026, 11, 15), 3 - 0.27, "Payment-bar subscription and enhanced cancel flow (26.9.3 RC, QA)", SERIES[0], h=0.16)
    _bar(ax, dt.date(2026, 10, 1), dt.date(2027, 2, 14), 3.02, "Reduce cancellations (FY27 B2): pause, remorse window, exit survey", SERIES[0], h=0.16)
    _bar(ax, dt.date(2026, 10, 5), dt.date(2027, 4, 18), 3.3, "Apple Pay and Google Pay (FY27 B4)", SERIES[0], h=0.16)
    ax.set_ylim(len(lanes) - 0.5, -0.55)
    ax.set_xlim(mdates.date2num(start), mdates.date2num(end))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="x", labelsize=7.8, length=0)
    ax.set_yticks([])
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(BASE)
    ax.grid(axis="x", color=GRID, lw=0.7, zorder=1)
    finish(fig, OUT / "fig_timeline.png", title="What lands in the next 12 months",
           subtitle="Dated events that shape IMTU subscriptions, Oct 2026 to Sep 2027.",
           source="Sources: state and city rules (law-firm trackers), CRT and America Movil (CURP), ETECSA promo history, company releases, IDT Jira and FY27 plan.")


# ---------------------------------------------------------------- plan gantt
@fig
def plan():
    import datetime as dt
    import matplotlib.dates as mdates
    rows = [
        ("0  Measure it", [("Renewal, failure and cancel-reason events; subscription_id", dt.date(2026, 10, 1), dt.date(2026, 12, 15))]),
        ("1  Earn the opt-in", [("Explicit-choice A/B vs default ON; disclosures, receipts, click-to-cancel", dt.date(2026, 10, 1), dt.date(2027, 1, 31))]),
        ("2  Fix payment health", [("Failure notice, retries, tiered auto-cancel, duplicate guard", dt.date(2026, 10, 15), dt.date(2027, 2, 28)),
                                   ("Apple Pay / Google Pay on renewals, card updater", dt.date(2027, 1, 1), dt.date(2027, 4, 30))]),
        ("3  Give control", [("Pause / skip, change date, amount, recipient; My Subscriptions hub", dt.date(2026, 11, 15), dt.date(2027, 3, 31)),
                             ("Web and WhatsApp management", dt.date(2027, 3, 1), dt.date(2027, 6, 30))]),
        ("4  Make it worth it", [("Save offer first, then subscriber price lock and bonus", dt.date(2027, 1, 1), dt.date(2027, 5, 31)),
                                 ("Data-bundle Plans; membership pilot", dt.date(2027, 4, 1), dt.date(2027, 9, 30))]),
        ("5  Fit the corridors", [("Mexico CURP line check + auto-pause", dt.date(2026, 10, 15), dt.date(2026, 12, 31)),
                                  ("Cuba promo-aware delivery; multi-recipient; retail enrollment", dt.date(2027, 2, 1), dt.date(2027, 8, 31))]),
    ]
    fig = plt.figure(figsize=(10.6, 5.8))
    ax = fig.add_axes([0.19, 0.10, 0.79, 0.72])
    start, end = dt.date(2026, 10, 1), dt.date(2027, 9, 30)
    y, ticks = 0, []
    for label, bars in rows:
        ticks.append((y + (len(bars) - 1) * 0.5, label))
        for (text, d0, d1) in bars:
            _bar(ax, d0, d1, y, text, SERIES[0], h=0.62)
            y += 1
        y += 0.35
    for d, lab in [(dt.date(2026, 12, 31), "Gate 1: attach quality\nand payment health"),
                   (dt.date(2027, 3, 31), "Gate 2: control shipped,\nsave-rate readout"),
                   (dt.date(2027, 6, 30), "Gate 3: value tests\nread out")]:
        x = mdates.date2num(d)
        ax.axvline(x, color="#eda100", lw=1.4, zorder=2)
        ax.text(x + 2, -0.95, lab, fontsize=7.2, color=INK2, va="bottom")
    ax.set_yticks([t for t, _ in ticks])
    ax.set_yticklabels([l for _, l in ticks], fontsize=8.8)
    ax.set_ylim(y - 0.2, -1.25)
    ax.set_xlim(mdates.date2num(start), mdates.date2num(end))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="both", length=0, labelsize=7.8)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(BASE)
    ax.grid(axis="x", color=GRID, lw=0.7, zorder=1)
    finish(fig, OUT / "fig_plan.png", title="IMTU subscriptions plan, Oct 2026 to Sep 2027",
           subtitle="Six workstreams and three decision gates. Detail, KPIs and dependencies in section 11.")



@fig
def idt_weekly():
    import datetime as dt
    import matplotlib.dates as mdates
    d = json.load(open(Path(__file__).resolve().parent / "data" / "idt_weekly_subs.json"))
    w = [dt.date.fromisoformat(x) for x in d["weeks"]]
    br, mo = d["br_subs"], d["money_subs"]
    brs = [a / (a + b) * 100 for a, b in zip(d["br_subs"], d["br_onetime"])]
    mos = [a / (a + b) * 100 for a, b in zip(d["money_subs"], d["money_onetime"])]
    light = "#86b6ef"
    fig = plt.figure(figsize=(9.2, 6.2))
    ax1 = fig.add_axes([0.07, 0.50, 0.9, 0.34])
    ax2 = fig.add_axes([0.07, 0.09, 0.9, 0.30])
    ax1.bar(w, br, width=5.2, color=SERIES[0], label="Boss Revolution app", zorder=3)
    ax1.bar(w, mo, width=5.2, bottom=br, color=light, label="BOSS Money app", zorder=3, edgecolor=SURFACE, linewidth=0.8)
    hairline(ax1, "y")
    ax1.set_ylabel("New subscriptions / week", fontsize=8.5)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax1.tick_params(axis="x", labelsize=8)
    tot = [a + b for a, b in zip(br, mo)]
    i = w.index(dt.date(2026, 6, 22))
    ax1.annotate(f"Peak {tot[i]/1000:.0f}k\n(default ON at 100%, 20 Jun)", xy=(w[i], tot[i]),
                 xytext=(w[i] - dt.timedelta(days=62), tot[i] * 0.93), fontsize=8, color=INK2,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax1.annotate(f"{tot[-1]/1000:.1f}k", xy=(w[-1], tot[-1]), xytext=(w[-1], tot[-1] + 3500), ha="center", fontsize=8.5,
                 color=INK, fontweight="bold")
    ax1.annotate("Auto-ON rollout\nbegins 19 Mar", xy=(w[3], tot[3]), xytext=(w[3] - dt.timedelta(days=16), 62000),
                 fontsize=8, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax1.legend(loc="upper left", frameon=False, fontsize=8.5, bbox_to_anchor=(0.0, 1.2), ncol=2)
    ax2.plot(w, brs, color=SERIES[0], lw=2)
    ax2.plot(w, mos, color=light, lw=2)
    hairline(ax2, "y")
    ax2.set_ylabel("Share of in-app top-up\npurchases that subscribe", fontsize=8.5)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax2.tick_params(axis="x", labelsize=8)
    ax2.text(w[-1] + dt.timedelta(days=2), brs[-1], f"BR {brs[-1]:.0f}%", fontsize=8.5, va="center", color=INK)
    ax2.text(w[-1] + dt.timedelta(days=2), mos[-1], f"Money {mos[-1]:.0f}%", fontsize=8.5, va="center", color=INK)
    ax2.set_xlim(w[0] - dt.timedelta(days=4), w[-1] + dt.timedelta(days=24))
    ax1.set_xlim(ax2.get_xlim())
    ax2.set_title("Subscription attach at purchase", loc="left", fontsize=9.5, color=INK, pad=4)
    finish(fig, OUT / "idt_weekly_subs.png", title="IDT creates ~45k new top-up subscriptions a week",
           subtitle="New subscriptions created in-app per week, Mar to Sep 2026 (weeks start Monday). Renewals are server-side and not counted here.",
           source="Source: Amplitude (BOSS org), BR app 650506 and Money app 420385, event MTUOrderStatusSuccessScr split by recurrent_unit. Pulled 29 Sep 2026.")


def run(names):
    for n in names or FIGS:
        FIGS[n]()
        print("wrote", n)


if __name__ == "__main__":
    run(sys.argv[1:])
