"""Shared figure helpers for the IMTU subscription competitor study.

Palette: the validated reference palette (dataviz skill). Entities keep one colour
across every chart: IDT blue, Ding orange, Rebtel aqua; everyone else is grey,
because only the first three categorical slots validate all-pairs.
"""
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASE = "#c3c2b7"
NEUTRAL = "#f0efec"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
ENTITY = {"IDT": SERIES[0], "Boss Revolution": SERIES[0], "BOSS Money": SERIES[0],
          "Ding": SERIES[1], "Rebtel": SERIES[2]}
OTHER = "#b9b7ae"
SEQ = {"none": "#f0efec", "partial": "#86b6ef", "full": "#256abf", "na": "#ffffff"}
STATUS = {"good": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}

# Flow-box styles: (face, edge, title ink)
BOX = {
    "step": ("#f3f2ee", "#a8a59b", "#3d3b36"),
    "offer": ("#e8f1fc", "#2a78d6", "#1c4f91"),
    "good": ("#e6f4ea", "#2f8f4e", "#1d5e33"),
    "warn": ("#fdf2dc", "#c9922a", "#7a5410"),
    "risk": ("#fbe8e8", "#c24545", "#8b2222"),
    "ghost": ("#ffffff", "#c3c2b7", "#6b6962"),
}

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.edgecolor": BASE,
    "axes.labelcolor": INK2,
    "xtick.color": MUTED,
    "ytick.color": INK2,
    "axes.titlecolor": INK,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def colour(name):
    return ENTITY.get(name, OTHER)


def finish(fig, path, title=None, subtitle=None, source=None):
    h = fig.get_size_inches()[1]
    ty = 1 - 0.10 / h
    if title:
        fig.text(0.012, ty, title, ha="left", va="top", fontsize=13, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.012, ty - (0.30 / h if title else 0), subtitle, ha="left", va="top", fontsize=9.5, color=INK2)
    if source:
        fig.text(0.012, 0.06 / h, source.replace("$", r"\$"), ha="left", va="bottom", fontsize=7.5, color=MUTED)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def hairline(ax, axis="x"):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASE)
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def wrap(s, width):
    return "\n".join(textwrap.wrap(s, width)) if s else ""


class Flow:
    """Tiny box-and-arrow diagram on a 0..100 x 0..H canvas (y grows downward)."""

    def __init__(self, w_in, h_in, height=100):
        self.fig = plt.figure(figsize=(w_in, h_in))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(height, 0)
        self.ax.axis("off")
        self.nodes = {}

    def box(self, key, x, y, w, h, title, sub="", style="step", title_size=9.5, sub_size=7.8, wrap_at=None):
        face, edge, ink = BOX[style]
        ls = (0, (3, 2)) if style == "ghost" else "-"
        self.ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                         boxstyle="round,pad=0,rounding_size=1.2",
                                         fc=face, ec=edge, lw=1.3, ls=ls))
        n = wrap_at or max(12, int(w * 1.55))
        if sub:
            self.ax.text(x, y - h * 0.16, wrap(title, n), ha="center", va="center", fontsize=title_size,
                         fontweight="bold", color=ink)
            self.ax.text(x, y + h * 0.22, wrap(sub, int(n * 1.2)), ha="center", va="center", fontsize=sub_size,
                         color=INK2, linespacing=1.15)
        else:
            self.ax.text(x, y, wrap(title, n), ha="center", va="center", fontsize=title_size,
                         fontweight="bold", color=ink)
        self.nodes[key] = (x, y, w, h)

    def diamond(self, key, x, y, w, h, text, size=8.5):
        pts = [(x, y - h / 2), (x + w / 2, y), (x, y + h / 2), (x - w / 2, y)]
        self.ax.add_patch(Polygon(pts, closed=True, fc="#f3f2ee", ec="#a8a59b", lw=1.3))
        self.ax.text(x, y, wrap(text, int(w * 1.1)), ha="center", va="center", fontsize=size, color="#3d3b36")
        self.nodes[key] = (x, y, w, h)

    def _anchor(self, key, side):
        x, y, w, h = self.nodes[key]
        return {"top": (x, y - h / 2), "bottom": (x, y + h / 2), "left": (x - w / 2, y),
                "right": (x + w / 2, y)}[side]

    def arrow(self, a, b, sa="bottom", sb="top", label="", dashed=False, via=None, lpos=0.5, lsize=7.5,
              color="#7d7a72"):
        p0, p1 = self._anchor(a, sa), self._anchor(b, sb)
        pts = [p0] + (via or []) + [p1]
        for i in range(len(pts) - 1):
            last = i == len(pts) - 2
            self.ax.annotate("", xy=pts[i + 1], xytext=pts[i],
                             arrowprops=dict(arrowstyle="-|>" if last else "-", color=color, lw=1.2,
                                             ls=(0, (3, 2)) if dashed else "-", shrinkA=0, shrinkB=0,
                                             mutation_scale=11))
        if label:
            i = min(len(pts) - 2, int(lpos * (len(pts) - 1)))
            (xa, ya), (xb, yb) = pts[i], pts[i + 1]
            self.ax.text((xa + xb) / 2 + 0.8, (ya + yb) / 2, label, fontsize=lsize, color=INK2,
                         ha="left", va="center",
                         bbox=dict(fc=SURFACE, ec="none", pad=0.6))

    def note(self, x, y, text, size=7.6, ha="left", color=None, width=34, style="italic"):
        self.ax.text(x, y, wrap(text, width), fontsize=size, color=color or MUTED, ha=ha, va="center",
                     style=style, linespacing=1.2)

    def lane(self, y0, y1, label, fc="#f7f6f2"):
        self.ax.add_patch(FancyBboxPatch((0.6, y0), 98.8, y1 - y0, boxstyle="round,pad=0,rounding_size=1",
                                         fc=fc, ec="none"))
        self.ax.text(1.6, y0 + 1.6, label, fontsize=8.5, fontweight="bold", color=INK2, ha="left", va="top")

    def save(self, path, title=None, subtitle=None, legend=None, source=None):
        if title:
            self.ax.text(1, 2.2, title, fontsize=13, fontweight="bold", color=INK, ha="left", va="top")
        if subtitle:
            self.ax.text(1, 5.6, subtitle, fontsize=9, color=INK2, ha="left", va="top")
        ylim = self.ax.get_ylim()[0]
        if legend:
            self.ax.text(50, ylim - 1.6, legend, fontsize=7.8, color=MUTED, ha="center", va="bottom")
        if source:
            self.ax.text(1, ylim - 1.6, source, fontsize=7.2, color=MUTED, ha="left", va="bottom")
        self.fig.savefig(path, dpi=200)
        plt.close(self.fig)
        return path
