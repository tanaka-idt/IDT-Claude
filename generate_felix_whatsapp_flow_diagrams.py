#!/usr/bin/env python3
"""
Generate the Felix Pago WhatsApp top-up (recarga) flowcharts and the
recommended BOSS Revolution WhatsApp IMTU flow.

Visual language mirrors generate_subscription_flow_diagrams.py:
  rounded box = state/step, diamond = decision,
  bold title + subtitle, Gray = system step | Teal = positive |
  Amber = warning/alternate path | Red = terminal/failure.

Every step in Diagram 1 is sourced from Felix's own public material
(help centre, recargas landing page, and the three step images published on
their CDN). Steps that are INFERRED rather than observed are labelled as such
in the subtitle. Nothing here is invented.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

# ---------------------------------------------------------------- palette ----
GRAY = dict(fill="#EEEBE5", edge="#A8A29A", text="#454340")
TEAL = dict(fill="#E3F1EA", edge="#1E7A5E", text="#186B51")
AMBER = dict(fill="#FAEBD9", edge="#C4841F", text="#8F5E0E")
RED = dict(fill="#FBE9E9", edge="#C05050", text="#9E3232")
BLUE = dict(fill="#E6EEF7", edge="#3F6FA8", text="#2C5384")
ARROW = "#7A7A7A"

LEGEND = ("Gray = system / bot step     Teal = user action or success     "
          "Amber = alternate path     Red = failure / terminal     Blue = external surface")


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


def canvas(fig_w, h, title, subtitle, xmax=20):
    fig, ax = plt.subplots(figsize=(fig_w, fig_w * h / xmax))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.text(xmax / 2, h - 0.5, title, ha="center", va="center",
            fontsize=17, fontweight="bold", color="#232320")
    ax.text(xmax / 2, h - 1.15, subtitle, ha="center", va="center",
            fontsize=9.5, color="#6A6A6A")
    ax.text(xmax / 2, 0.35, LEGEND, ha="center", va="center", fontsize=8.5, color="#8A8A8A")
    return fig, ax


def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


# ======================================================= 1. FELIX OBSERVED ====
XA, XAB = 4.5, 9.0      # column A spine / its branch lane
XB, XBB = 13.8, 18.0    # column B spine / its branch lane
W, BW = 5.0, 2.9


def felix_flow():
    H = 21
    fig, ax = canvas(18, H, "Diagram 1 — Felix Pago: Observed WhatsApp Top-Up (Recarga) Journey",
                     "Reconstructed from Felix's own public help centre, recargas landing page and the three step images on their CDN. "
                     "Spanish copy quoted verbatim. Dashed = documented but unobserved.")

    yA = [18.4, 16.35, 14.3, 12.25, 10.1, 7.9, 5.7, 3.5]
    h1 = 1.15

    box(ax, XA, yA[0], W, h1 + 0.2, "1 · Entry: click-to-WhatsApp",
        "api.whatsapp.com/send?phone=1669\u2022\u2022\u2022\u2022\u2022\u2022\u2022", style=TEAL)

    box(ax, XA, yA[1], W, h1 + 0.2, '2 \u00b7 User types "recarga"',
        'But site prefill says "env\u00edo de dinero"', style=TEAL)
    arrow(ax, (XA, yA[0] - 0.68), (XA, yA[1] + 0.68))

    box(ax, XA, yA[2], W, h1 + 0.2, "3 \u00b7 Bot asks for the number",
        '"\u00bfA qu\u00e9 n\u00famero\u2026? Incluye el c\u00f3digo de pa\u00eds"')
    arrow(ax, (XA, yA[1] - 0.68), (XA, yA[2] + 0.68))

    box(ax, XA, yA[3], W, h1 + 0.2, "4 \u00b7 User sends the number",
        'Inline example: "+52 1234567890"', style=TEAL)
    arrow(ax, (XA, yA[2] - 0.68), (XA, yA[3] + 0.68))

    diamond(ax, XA, yA[4], 3.8, 1.55, "5 \u00b7 Number parses?")
    arrow(ax, (XA, yA[3] - 0.68), (XA, yA[4] + 0.78))
    box(ax, XAB, yA[4], BW, 1.15, "Re-prompt", "Error copy not published", style=AMBER)
    arrow(ax, (XA + 1.9, yA[4]), (XAB - 1.45, yA[4]), label="no")
    arrow(ax, (XAB, yA[4] + 0.58), (XAB, yA[2]), rad=0.3, dashed=True)

    box(ax, XA, yA[5], W, h1 + 0.35, "6 \u00b7 Auto-detect country + carrier",
        '"Detect\u00e9 que \u2026 es un n\u00famero de Claro\nColombia" \u2014 no manual country picker', style=BLUE)
    arrow(ax, (XA, yA[4] - 0.78), (XA, yA[5] + 0.75), label="yes")

    diamond(ax, XA, yA[6], 4.0, 1.6, "7 \u00b7 \u00bfContinuamos?")
    arrow(ax, (XA, yA[5] - 0.75), (XA, yA[6] + 0.8))
    box(ax, XAB, yA[6], BW, 1.25, "Cambiar compa\u00f1\u00eda", "Manual carrier override", style=AMBER)
    arrow(ax, (XA + 2.0, yA[6]), (XAB - 1.45, yA[6]), label="tap")
    arrow(ax, (XAB, yA[6] - 0.63), (XAB, yA[7]), rad=0.0)
    arrow(ax, (XAB, yA[7]), (XA + W / 2, yA[7]))

    box(ax, XA, yA[7], W, h1 + 0.2, "8 \u00b7 Choose recharge type",
        "Datos \u00b7 Paquete \u00b7 Saldo libre")
    arrow(ax, (XA, yA[6] - 0.8), (XA, yA[7] + 0.68), label='"S\u00ed, continuar"')

    ax.text(XA, 1.75, "\u25b6  continues in the right-hand column", ha="center", va="center",
            fontsize=9.5, style="italic", color="#1E7A5E")

    # ---- column B ----
    yB = [17.6, 15.6, 13.6, 11.6, 9.6, 7.6, 5.7, 3.9, 2.2]
    ax.text(XB, 18.85, "(continued)", ha="center", va="center",
            fontsize=9.5, style="italic", color="#8A8A8A")

    box(ax, XB, yB[0], W, h1 + 0.5, "9 \u00b7 Choose amount \u2014 in RECIPIENT currency",
        "3 quick-reply buttons (the platform maximum)\n+ an \u201cOpciones\u201d list for the rest\nFX shown only as an estimate")

    box(ax, XB, yB[1], W, h1 + 0.5, "10 \u00b7 RESUMEN DE RECARGA",
        "N\u00famero \u00b7 Pa\u00eds \u00b7 Compa\u00f1\u00eda \u00b7 Producto\nTotal a pagar USD \u00b7 Tipo de cambio")
    arrow(ax, (XB, yB[0] - 0.83), (XB, yB[1] + 0.83))

    diamond(ax, XB, yB[2], 4.2, 1.6, "11 \u00b7 \u00bfConfirmas\nesta recarga?")
    arrow(ax, (XB, yB[1] - 0.83), (XB, yB[2] + 0.8))
    box(ax, XBB, yB[2], BW, 1.25, "Cambiar algo", "Returns to edit", style=AMBER)
    arrow(ax, (XB + 2.1, yB[2]), (XBB - 1.45, yB[2]), label="tap")
    arrow(ax, (XBB, yB[2] + 0.63), (XBB, yB[0]), rad=-0.3, dashed=True)

    box(ax, XB, yB[3], W, h1 + 0.2, "12 \u00b7 CTA button: \u201cPagar recarga\u201d",
        "Hands off out of the thread", style=BLUE)
    arrow(ax, (XB, yB[2] - 0.8), (XB, yB[3] + 0.68), label='"Confirmar recarga"')

    box(ax, XB, yB[4], W, h1 + 0.5, "13 \u00b7 Hosted checkout (webview)",
        "payments-ui.prod.fpago.com\nCard + MM/AA \u00b7 \u201cComisi\u00f3n F\u00e9lix: $0.00\u201d\nNever card-in-chat", style=BLUE)
    arrow(ax, (XB, yB[3] - 0.68), (XB, yB[4] + 0.83))

    diamond(ax, XB, yB[5], 3.9, 1.6, "14 \u00b7 Payment\nauthorised?")
    arrow(ax, (XB, yB[4] - 0.83), (XB, yB[5] + 0.8))
    box(ax, XBB, yB[5], BW, 1.25, "Declined", "Recovery path\nnot published", style=RED)
    arrow(ax, (XB + 2.0, yB[5]), (XBB - 1.45, yB[5]), label="no")

    box(ax, XB, yB[6], W, h1 + 0.2, "15 \u00b7 Confirmation in-thread",
        "Same WhatsApp conversation", style=TEAL)
    arrow(ax, (XB, yB[5] - 0.8), (XB, yB[6] + 0.68), label="yes")

    box(ax, XB, yB[7], W, h1 + 0.35, "16 \u00b7 Credited \u201cen minutos\u201d",
        "Carrier sends its own SMS to the recipient", style=TEAL)
    arrow(ax, (XB, yB[6] - 0.68), (XB, yB[7] + 0.75))

    box(ax, XB, yB[8], W, h1 + 0.35, "\u26a0  Wrong number = no refund",
        "\u201csin posibilidad de reembolso\u201d \u2014 irreversible\nRisk carried by the whole flow, not one step", style=RED)
    arrow(ax, (XB, yB[7] - 0.75), (XB, yB[8] + 0.75), dashed=True)

    save(fig, "felix_whatsapp_topup_flow.png")


# ================================================ 2. BR RECOMMENDED FLOW ======
def br_flow():
    H = 21
    fig, ax = canvas(18, H, "Diagram 2 \u2014 Recommended BOSS Revolution WhatsApp IMTU Flow",
                     "Adopts Felix's proven spine; closes its transparency, recovery and identity gaps. "
                     "Teal = BR differentiator with no Felix equivalent.")

    yA = [18.4, 16.35, 14.3, 12.25, 10.1, 7.9, 5.7, 3.5]
    h1 = 1.15

    box(ax, XA, yA[0], W, h1 + 0.35, "1 \u00b7 Intent-matched entry",
        "Click-to-WhatsApp ad \u00b7 QR \u00b7 in-app share\nPrefill matches the creative that was tapped", style=TEAL)

    box(ax, XA, yA[1], W, h1 + 0.35, "2 \u00b7 Identify by WhatsApp number",
        "Match to the existing BR account, greet by name\nSurface saved recipients straight away", style=TEAL)
    arrow(ax, (XA, yA[0] - 0.75), (XA, yA[1] + 0.75))

    diamond(ax, XA, yA[2], 4.2, 1.6, "3 \u00b7 Known recipient?")
    arrow(ax, (XA, yA[1] - 0.75), (XA, yA[2] + 0.8))
    box(ax, XAB, yA[2], BW, 1.45, "One-tap reorder", '"Same as last time \u2014\n$10 to Claro Colombia?"', style=TEAL)
    arrow(ax, (XA + 2.1, yA[2]), (XAB - 1.45, yA[2]), label="yes")

    box(ax, XA, yA[3], W, h1 + 0.2, "4 \u00b7 Ask for the number",
        "Inline example \u00b7 accept a pasted contact")
    arrow(ax, (XA, yA[2] - 0.8), (XA, yA[3] + 0.68), label="no")

    box(ax, XA, yA[4], W, h1 + 0.5, "5 \u00b7 Auto-detect + echo back",
        "Show the number in readable groups\nConfirm, with an explicit carrier override\nADOPTED FROM FELIX", style=BLUE)
    arrow(ax, (XA, yA[3] - 0.68), (XA, yA[4] + 0.83))

    diamond(ax, XA, yA[5], 4.2, 1.6, "6 \u00b7 Number\nconfirmed?")
    arrow(ax, (XA, yA[4] - 0.83), (XA, yA[5] + 0.8))
    box(ax, XAB, yA[5], BW, 1.45, "Edit number", "Cheap correction BEFORE\nan irreversible send", style=AMBER)
    arrow(ax, (XA + 2.1, yA[5]), (XAB - 1.45, yA[5]), label="no")
    arrow(ax, (XAB, yA[5] + 0.73), (XAB, yA[3]), rad=-0.3, dashed=True)

    box(ax, XA, yA[6], W, h1 + 0.5, "7 \u00b7 Offers with BLS promo applied",
        "Reuse the existing promo engine + Engager/NBO\nBundles and data plans, not airtime alone\nBR CAPABILITY FELIX LACKS", style=TEAL)
    arrow(ax, (XA, yA[5] - 0.8), (XA, yA[6] + 0.83), label="yes")

    box(ax, XA, yA[7], W, h1 + 0.5, "8 \u00b7 Price in BOTH currencies",
        '"$10.00 USD \u2192 40,000 COP" on every option\nLocked rate + validity window, not an estimate\nFIXES A FELIX WEAKNESS', style=TEAL)
    arrow(ax, (XA, yA[6] - 0.83), (XA, yA[7] + 0.83))

    ax.text(XA, 1.75, "\u25b6  continues in the right-hand column", ha="center", va="center",
            fontsize=9.5, style="italic", color="#1E7A5E")

    # ---- column B ----
    yB = [17.6, 15.6, 13.6, 11.6, 9.6, 7.6, 5.7, 3.9, 2.2]
    ax.text(XB, 18.85, "(continued)", ha="center", va="center",
            fontsize=9.5, style="italic", color="#8A8A8A")

    box(ax, XB, yB[0], W, h1 + 0.5, "9 \u00b7 Summary + full price breakdown",
        "Recipient gets \u00b7 fee \u00b7 FX \u00b7 total charged\nThe all-in total stated before any handoff")

    diamond(ax, XB, yB[1], 4.0, 1.6, "10 \u00b7 Confirm?")
    arrow(ax, (XB, yB[0] - 0.83), (XB, yB[1] + 0.8))
    box(ax, XBB, yB[1], BW, 1.25, "Change anything", "Return to the exact step", style=AMBER)
    arrow(ax, (XB + 2.0, yB[1]), (XBB - 1.45, yB[1]))
    arrow(ax, (XBB, yB[1] + 0.63), (XBB, yB[0]), rad=-0.3, dashed=True)

    box(ax, XB, yB[2], W, h1 + 0.5, "11 \u00b7 Pay \u2014 saved card or hosted link",
        "Returning: tokenised card, no re-entry\nNew: hosted checkout, never card-in-chat", style=BLUE)
    arrow(ax, (XB, yB[1] - 0.8), (XB, yB[2] + 0.83), label="yes")

    diamond(ax, XB, yB[3], 3.9, 1.6, "12 \u00b7 Authorised?")
    arrow(ax, (XB, yB[2] - 0.83), (XB, yB[3] + 0.8))
    box(ax, XBB, yB[3], BW, 1.45, "Typed decline reason", "Retry in-thread with\nan alternate method", style=AMBER)
    arrow(ax, (XB + 2.0, yB[3]), (XBB - 1.45, yB[3]), label="no")
    arrow(ax, (XBB, yB[3] + 0.73), (XBB, yB[2]), rad=-0.3, dashed=True)

    box(ax, XB, yB[4], W, h1 + 0.5, "13 \u00b7 Confirmation + receipt",
        "Reference number \u00b7 carrier \u00b7 both currencies\nSupport handoff offered in-thread", style=TEAL)
    arrow(ax, (XB, yB[3] - 0.8), (XB, yB[4] + 0.83), label="yes")

    box(ax, XB, yB[5], W, h1 + 0.5, "14 \u00b7 Delivery-confirmed message",
        "Distinct from \u201cpayment taken\u201d \u2014 closes the loop\nFIXES A FELIX AMBIGUITY", style=TEAL)
    arrow(ax, (XB, yB[4] - 0.83), (XB, yB[5] + 0.83))

    box(ax, XB, yB[6], W, h1 + 0.35, "15 \u00b7 Opt-in captured explicitly",
        "Separate marketing consent from the purchase", style=BLUE)
    arrow(ax, (XB, yB[5] - 0.83), (XB, yB[6] + 0.75))

    box(ax, XB, yB[7], W, h1 + 0.5, "16 \u00b7 Re-engagement",
        "Balance-low nudge \u00b7 subscription offer\nRAF referral hook \u00b7 utility templates", style=TEAL)
    arrow(ax, (XB, yB[6] - 0.75), (XB, yB[7] + 0.83))

    box(ax, XB, yB[8], W, h1 + 0.35, "17 \u00b7 One-tap reorder next time",
        "Feeds back into step 3", style=TEAL)
    arrow(ax, (XB, yB[7] - 0.83), (XB, yB[8] + 0.75))

    save(fig, "br_whatsapp_imtu_recommended_flow.png")


if __name__ == "__main__":
    print("Generating WhatsApp IMTU flow diagrams\u2026")
    felix_flow()
    br_flow()
    print("Done.")
