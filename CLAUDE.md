# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IDT Corporation stock analysis toolkit. Fetches 10-year historical data via yfinance, generates technical analysis charts (price, moving averages, volume, drawdown, returns), and exports a formatted Google Docs investment analysis with embedded charts. Primarily used to analyze and visualize IDT's performance relative to the S&P 500.

## Build & Run

Install dependencies:
```bash
pip install yfinance matplotlib pandas numpy google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Run individual analysis scripts:
```bash
python idt_stock_chart.py        # Generate basic 10-year price chart with min/max
python generate_charts.py        # Generate 5 comprehensive charts + key statistics
python create_google_doc.py      # Create formatted Google Docs analysis with embedded charts
```

**Google Docs Integration Setup (one-time):**
1. Go to https://console.cloud.google.com
2. Create a project or select existing one
3. Enable: Google Docs API + Google Drive API
4. Credentials → Create → OAuth 2.0 Client ID → Desktop app
5. Download JSON credentials → save as `credentials.json` in project root
6. Run `create_google_doc.py` — browser tab opens for authorization

## Architecture

**Data Flow:**
1. `yfinance` fetches 10-year historical data (OHLCV) for IDT and S&P 500 index (^GSPC)
2. `pandas` processes data: rolling averages, annual returns, drawdowns, cumulative returns
3. `matplotlib` generates PNG visualizations at 150 DPI
4. `create_google_doc.py` uploads PNGs to Google Drive, builds formatted Google Doc with content blocks inserted at index 1

**Key Modules:**
- `idt_stock_chart.py`: Simple entry point; generates single chart with price extrema
- `generate_charts.py`: Core analysis engine producing 5 charts + statistics; uses helper `save()` to output and print metrics
- `create_google_doc.py`: Google Docs/Drive API integration; handles OAuth flow, image upload, batch document formatting

**Output:**
- PNG charts (14×6 inches, 150 DPI) saved to repo root
- Google Drive folder created: "IDT Stock Analysis"
- Google Doc URL printed and opened in browser

## Git & GitHub Workflow

**IMPORTANT: Always commit and push to GitHub regularly.** This ensures no work is ever lost and provides a complete history of the project.

- Make commits after completing meaningful work (new features, bug fixes, documentation updates)
- Use clear, descriptive commit messages in imperative form (e.g., "Add IDT vs S&P 500 comparison chart" not "added stuff")
- Push to GitHub immediately after committing: `git push origin main`
- Before starting new work, verify the repository is up to date with `git status`
- If reverting changes is needed, use `git log --oneline` to find commits and `git revert <commit-hash>` or `git reset`

**Repository:** https://github.com/tanaka-idt/IDT-Claude

## Key Conventions

- All data processing is 10-year rolling window (present day - 10 years)
- yfinance `auto_adjust=True` ensures splits/dividends handled correctly
- Charts use consistent coloring: blue (IDT/Close), orange (50-day MA), red (200-day MA/negative), green (highs), purple (volume)
- Google Doc requests sent in batches of 50 to avoid API rate limits
- Ensure internet connectivity for yfinance and Google API calls
- Google credentials (`token.json`) auto-saved after first authorization; `credentials.json` required (git-ignored)
