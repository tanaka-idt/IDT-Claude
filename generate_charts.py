"""
Generate multiple IDT stock analysis charts for the investment strategy Google Doc.
"""
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent
TICKER = "IDT"

print("Downloading IDT data...")
raw = yf.download(TICKER, period="10y", interval="1d", auto_adjust=True)
data = raw.copy()
data.columns = data.columns.get_level_values(0)  # flatten multi-index if present

close = data["Close"].squeeze()
volume = data["Volume"].squeeze()

# ── helpers ──────────────────────────────────────────────────────────────────
def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved {name}")
    plt.close(fig)

# ── Chart 1: Closing price + 50/200-day MAs ──────────────────────────────────
ma50  = close.rolling(50).mean()
ma200 = close.rolling(200).mean()

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(close.index, close.values, lw=1.2, color="#1f77b4", label="Close", alpha=0.9)
ax.plot(ma50.index, ma50.values, lw=1.5, color="orange", label="50-day MA")
ax.plot(ma200.index, ma200.values, lw=1.5, color="red", label="200-day MA")

min_idx, max_idx = close.idxmin(), close.idxmax()
ax.scatter([min_idx], [close[min_idx]], color="red", zorder=5, s=70)
ax.annotate(f"  Low\n  ${close[min_idx]:.2f}\n  {min_idx.strftime('%b %Y')}",
            xy=(min_idx, close[min_idx]), fontsize=8, color="red", va="top")
ax.scatter([max_idx], [close[max_idx]], color="green", zorder=5, s=70)
ax.annotate(f"  High\n  ${close[max_idx]:.2f}\n  {max_idx.strftime('%b %Y')}",
            xy=(max_idx, close[max_idx]), fontsize=8, color="green", va="bottom")

ax.set_title("IDT Corporation — Closing Price with Moving Averages (10 Years)", fontsize=13, fontweight="bold")
ax.set_xlabel("Date"); ax.set_ylabel("Price (USD)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(fontsize=10)
save(fig, "chart1_price_ma.png")

# ── Chart 2: Annual returns bar chart ────────────────────────────────────────
annual = close.resample("YE").last().pct_change().dropna() * 100
years  = annual.index.year

colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in annual.values]
fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(years, annual.values, color=colors, edgecolor="white", linewidth=0.5)
for bar, val in zip(bars, annual.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + (1 if val >= 0 else -2),
            f"{val:+.1f}%", ha="center", va="bottom" if val >= 0 else "top", fontsize=8)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("IDT Corporation — Annual Returns (%)", fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Return (%)")
ax.set_xticks(years)
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
save(fig, "chart2_annual_returns.png")

# ── Chart 3: Volume (monthly average) ────────────────────────────────────────
monthly_vol = volume.resample("ME").mean() / 1e6  # in millions

fig, ax = plt.subplots(figsize=(14, 4))
ax.fill_between(monthly_vol.index, monthly_vol.values, alpha=0.4, color="#9b59b6")
ax.plot(monthly_vol.index, monthly_vol.values, lw=1.2, color="#9b59b6")
ax.set_title("IDT Corporation — Average Monthly Trading Volume", fontsize=13, fontweight="bold")
ax.set_xlabel("Date"); ax.set_ylabel("Volume (millions of shares)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.grid(True, linestyle="--", alpha=0.4)
save(fig, "chart3_volume.png")

# ── Chart 4: Drawdown from all-time high ─────────────────────────────────────
rolling_max = close.cummax()
drawdown    = (close - rolling_max) / rolling_max * 100

fig, ax = plt.subplots(figsize=(14, 5))
ax.fill_between(drawdown.index, drawdown.values, color="#e74c3c", alpha=0.5, label="Drawdown")
ax.plot(drawdown.index, drawdown.values, lw=0.8, color="#e74c3c")
max_dd_idx = drawdown.idxmin()
ax.annotate(f"Max DD: {drawdown[max_dd_idx]:.1f}%\n{max_dd_idx.strftime('%b %Y')}",
            xy=(max_dd_idx, drawdown[max_dd_idx]), fontsize=9, color="darkred",
            arrowprops=dict(arrowstyle="->", color="darkred"),
            xytext=(max_dd_idx, drawdown[max_dd_idx] - 10))
ax.set_title("IDT Corporation — Drawdown from Peak (%)", fontsize=13, fontweight="bold")
ax.set_xlabel("Date"); ax.set_ylabel("Drawdown (%)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(fontsize=10)
save(fig, "chart4_drawdown.png")

# ── Chart 5: Cumulative return vs S&P 500 ────────────────────────────────────
print("Downloading S&P 500 data...")
sp_raw = yf.download("^GSPC", period="10y", interval="1d", auto_adjust=True)
sp500 = sp_raw["Close"].squeeze()

# Align on common dates
common = close.index.intersection(sp500.index)
idt_ret = (close[common] / close[common].iloc[0] - 1) * 100
sp_ret  = (sp500[common] / sp500[common].iloc[0] - 1) * 100

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(idt_ret.index, idt_ret.values, lw=1.8, color="#1f77b4", label="IDT")
ax.plot(sp_ret.index,  sp_ret.values,  lw=1.8, color="#ff7f0e", label="S&P 500")
ax.set_title("IDT vs S&P 500 — Cumulative Return (10 Years, base = 0%)", fontsize=13, fontweight="bold")
ax.set_xlabel("Date"); ax.set_ylabel("Cumulative Return (%)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(fontsize=11)
save(fig, "chart5_idt_vs_sp500.png")

# ── Print key stats ───────────────────────────────────────────────────────────
start_price = close.iloc[0]
end_price   = close.iloc[-1]
total_return = (end_price / start_price - 1) * 100
cagr = ((end_price / start_price) ** (1/10) - 1) * 100
daily_returns = close.pct_change().dropna()
volatility = daily_returns.std() * np.sqrt(252) * 100
sharpe = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
max_dd = drawdown.min()

print("\n── IDT Key Statistics (10-Year) ──────────────────────")
print(f"  Start price   : ${start_price:.2f}  ({close.index[0].strftime('%Y-%m-%d')})")
print(f"  End price     : ${end_price:.2f}  ({close.index[-1].strftime('%Y-%m-%d')})")
print(f"  Total return  : {total_return:+.1f}%")
print(f"  CAGR          : {cagr:.2f}% / year")
print(f"  Annualized vol: {volatility:.1f}%")
print(f"  Sharpe ratio  : {sharpe:.2f}")
print(f"  Max drawdown  : {max_dd:.1f}%")
print(f"  All-time high : ${close[max_idx]:.2f} ({max_idx.strftime('%Y-%m-%d')})")
print(f"  All-time low  : ${close[min_idx]:.2f} ({min_idx.strftime('%Y-%m-%d')})")
sp_total = (sp500[common].iloc[-1] / sp500[common].iloc[0] - 1) * 100
print(f"  S&P 500 return: {sp_total:+.1f}% (same period)")
print("──────────────────────────────────────────────────────")
