import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Download 10 years of IDT daily data
ticker = "IDT"
data = yf.download(ticker, period="10y", interval="1d", auto_adjust=True)

if data.empty:
    raise RuntimeError("No data returned for ticker IDT. Check your internet connection.")

close = data["Close"].squeeze()

# Find min/max points
min_idx = close.idxmin()
max_idx = close.idxmax()
min_price = close[min_idx]
max_price = close[max_idx]

# Plot
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(close.index, close.values, linewidth=1.5, color="#1f77b4", label="Closing Price")

# Highlight min/max
ax.scatter([min_idx], [min_price], color="red", zorder=5, s=60)
ax.annotate(
    f"  Low: ${min_price:.2f}\n  {min_idx.strftime('%b %Y')}",
    xy=(min_idx, min_price),
    fontsize=8,
    color="red",
    va="top",
)

ax.scatter([max_idx], [max_price], color="green", zorder=5, s=60)
ax.annotate(
    f"  High: ${max_price:.2f}\n  {max_idx.strftime('%b %Y')}",
    xy=(max_idx, max_price),
    fontsize=8,
    color="green",
    va="bottom",
)

ax.set_title("IDT Corporation (IDT) — Stock Price (Last 10 Years)", fontsize=14, fontweight="bold")
ax.set_xlabel("Date", fontsize=11)
ax.set_ylabel("Price (USD)", fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(fontsize=10)

plt.tight_layout()

# Save chart
output_path = Path(__file__).parent / "idt_stock_chart.png"
fig.savefig(output_path, dpi=150)
print(f"Chart saved to: {output_path}")

plt.show()
