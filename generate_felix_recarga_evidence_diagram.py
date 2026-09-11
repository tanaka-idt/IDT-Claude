#!/usr/bin/env python3
"""
Draws the evidence-graded Felix Pago WhatsApp recarga journey.

Every node is coloured by the strongest evidence that exists for it:
  green  = real production screenshot published by Felix (WhatsApp iOS capture)
  blue   = real screen recording from a Felix video, remittance flow, same bot chassis
  amber  = marketing mock only (designed composite, placeholder data)
  grey   = documented in Felix's help centre but never observed on a screen
  red    = terminal risk stated by Felix

Output: felix_evidence/felix_recarga_flow_evidence.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / "felix_evidence" / "felix_recarga_flow_evidence.png"

GRADE = {
    "real":  dict(face="#e6f4ec", edge="#1f8a5b", text="#0f4d33", label="Real production screenshot"),
    "video": dict(face="#e8eff9", edge="#2b6cb0", text="#173f6b", label="Real screen recording (remittance flow, same bot)"),
    "mock":  dict(face="#fbf1dc", edge="#b8860b", text="#6b4d00", label="Marketing mock only"),
    "doc":   dict(face="#f1f1ef", edge="#8a8a84", text="#3d3d3a", label="Documented, never observed on a screen"),
    "risk":  dict(face="#fbe6e6", edge="#b03a3a", text="#6e1c1c", label="Terminal risk stated by Felix"),
}

# (column, row, grade, title, body)
NODES = [
    (0, 0, "real", "1  Entry", "Prefilled deep-link message\n“Quiero hacer una “recarga telefónica””\nor the typed keyword “recarga”"),
    (0, 1, "real", "2  Number prompt", "“¿A qué número quieres mandar la recarga?\nIncluye el código de país.”\nEjemplo: +52 1234567890"),
    (0, 2, "real", "3  Sender types the number", "Free text, E.164 with country code\nOnly free-text step in the whole flow"),
    (0, 3, "real", "4  Auto-detect country + carrier", "“Detecté que … (Colombia) es un número\nde Claro Colombia. ¿Continuamos?”\nSí, continuar / Cambiar compañía"),
    (0, 4, "real", "5  Recharge type", "“Perfecto. ¿Qué tipo de recarga quieres hacer\na tu numero Claro Colombia?”\nOptions documented: datos, paquete, saldo libre"),
    (0, 5, "real", "6  Amount in recipient currency", "3 quick replies ($4000 / $5000 / $6000 COP)\n+ list “Elegir un monto diferente”\nFX shown as estimate (~3225.81 COP/USD)"),
    (1, 0, "real", "7  RESUMEN DE RECARGA", "Número · País · Compañía · Producto\nTotal a pagar $1.87 USD · Tipo de cambio\nButtons: Confirmar recarga / Cambiar algo"),
    (1, 1, "real", "8  Payment hand-off", "“Listo. Completa tu pago en este sitio\nseguro para enviar la recarga.”\nCTA URL button: Pagar recarga"),
    (1, 2, "real", "9  Hosted checkout", "WhatsApp in-app browser\npayments-ui.prod.fpago.com\nCard + MM/AA · Comisión Félix $0.00 · Pagar"),
    (1, 3, "video", "10  Payment result", "Not captured for recarga. Remittance analogue:\n“¡Listo! Tu pago se completó con éxito.”\n+ Volver a WhatsApp + referral offer"),
    (1, 4, "video", "11  WhatsApp confirmation", "Not captured for recarga. Remittance analogue:\n“¡Tu envío está siendo procesado!” + receipt image\nwith the reference number as its hero"),
    (1, 5, "doc", "12  Delivery", "Credited “en cuestión de minutos”\nCarrier sends its own SMS to the recipient\nNo Felix delivery-confirmed message seen"),
]

SIDE = [
    (0, 3, "doc", "Cambiar compañía", "Manual carrier pick.\nList never observed."),
    (0, 5, "doc", "Opciones list", "Other denominations.\nContents never observed."),
    (1, 0, "doc", "Cambiar algo", "Edit path.\nNever observed."),
    (1, 2, "doc", "Card declined", "No recovery copy\npublished anywhere."),
    (1, 5, "risk", "Wrong number", "“sin posibilidad de reembolso”\nNo refund path for top-ups."),
]

COL_X = {0: 0.55, 1: 6.05}
SIDE_X = {0: 3.45, 1: 8.95}
ROW_Y = lambda r: 8.75 - r * 1.58
W, H = 2.75, 1.28
SW, SH = 1.55, 0.78


def box(ax, x, y, w, h, grade, title, body, tfs=8.6, bfs=6.9):
    g = GRADE[grade]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                linewidth=1.6, edgecolor=g["edge"], facecolor=g["face"]))
    ax.text(x + 0.12, y + h - 0.16, title, fontsize=tfs, fontweight="bold", color=g["text"], va="top", ha="left")
    ax.text(x + 0.12, y + h - 0.44, body, fontsize=bfs, color="#2b2b28", va="top", ha="left", linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, style="-", color="#6b6b66"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11,
                                 linewidth=1.1, linestyle=style, color=color,
                                 connectionstyle="arc3,rad=0.0"))


def main():
    fig, ax = plt.subplots(figsize=(11.4, 12.4), dpi=200)
    ax.set_xlim(0, 11.4); ax.set_ylim(-0.75, 11.55); ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.55, 11.28, "Felix Pago WhatsApp top-up (recarga): what the real screens prove",
            fontsize=15, fontweight="bold", color="#10211d", ha="left", va="top")
    ax.text(0.55, 10.86, "Each step is coloured by the strongest evidence found for it. Spanish copy is quoted verbatim from Felix's own\n"
            "production screenshots (felixpago.com/recargas-internacionales) and its May 2026 tutorial video.",
            fontsize=8.2, color="#4a4a46", ha="left", va="top", linespacing=1.4)

    # main nodes
    pos = {}
    for c, r, grade, title, body in NODES:
        x, y = COL_X[c], ROW_Y(r)
        box(ax, x, y, W, H, grade, title, body)
        pos[(c, r)] = (x, y)
    # side nodes
    for c, r, grade, title, body in SIDE:
        x, y = SIDE_X[c], ROW_Y(r) + 0.25
        box(ax, x, y, SW, SH, grade, title, body, tfs=7.6, bfs=6.3)
        # dashed link from the main node
        mx, my = pos[(c, r)]
        arrow(ax, mx + W, my + H / 2, x, y + SH / 2, style="--", color="#9a9a94")

    # vertical flow arrows
    for c in (0, 1):
        for r in range(5):
            x, y = pos[(c, r)]
            arrow(ax, x + W / 2, y, x + W / 2, ROW_Y(r + 1) + H)
    # column jump 6 -> 7: leave node 6 above its side box, run up the gutter, enter node 7 from the left
    x6, y6 = pos[(0, 5)]; x7, y7 = pos[(1, 0)]
    gx = 5.55
    yl = y6 + H - 0.15
    ax.plot([x6 + W, gx, gx], [yl, yl, y7 + H / 2], color="#6b6b66", linewidth=1.1)
    arrow(ax, gx, y7 + H / 2, x7, y7 + H / 2)
    ax.text(gx - 0.08, (yl + y7 + H / 2) / 2, "continues in column 2", fontsize=6.6, color="#6b6b66",
            ha="right", va="center", rotation=90)

    # surface bands
    ax.text(0.55, 10.2, "WHATSAPP THREAD", fontsize=7.2, color="#1f8a5b", fontweight="bold", ha="left", va="bottom")
    ax.text(6.05, 10.2, "THREAD  >  IN-APP BROWSER  >  THREAD", fontsize=7.2, color="#1f8a5b", fontweight="bold", ha="left", va="bottom")

    # legend
    lx, ly = 0.55, 0.2
    ax.text(lx, ly + 0.36, "Evidence grade", fontsize=8, fontweight="bold", color="#10211d", ha="left", va="bottom")
    for i, key in enumerate(["real", "video", "mock", "doc", "risk"]):
        g = GRADE[key]
        xx = lx + (i % 2) * 5.5
        yy = ly - (i // 2) * 0.4
        ax.add_patch(FancyBboxPatch((xx, yy), 0.42, 0.22, boxstyle="round,pad=0.01,rounding_size=0.05",
                                    linewidth=1.4, edgecolor=g["edge"], facecolor=g["face"]))
        ax.text(xx + 0.52, yy + 0.11, g["label"], fontsize=7.2, color="#2b2b28", va="center", ha="left")

    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", facecolor="white")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
