"""
Creates a Google Doc: "IDT Corporation — 10-Year Investment Strategy Analysis"
Uploads charts to Google Drive and embeds them in the document.

SETUP (one time):
  1. Go to https://console.cloud.google.com
  2. Create a project (or select one)
  3. Enable: Google Docs API  +  Google Drive API
  4. Credentials → Create → OAuth 2.0 Client ID → Desktop app
  5. Download JSON → save as  credentials.json  in this folder
  6. Run this script; a browser tab will open for you to authorise
"""

import json
import os
import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Config ────────────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE  = BASE / "credentials.json"
TOKEN_FILE  = BASE / "token.json"

CHARTS = [
    ("chart1_price_ma.png",      "Figure 1 — Closing Price with 50 & 200-Day Moving Averages"),
    ("chart2_annual_returns.png","Figure 2 — Annual Returns (%)"),
    ("chart5_idt_vs_sp500.png",  "Figure 3 — IDT vs S&P 500 Cumulative Return"),
    ("chart3_volume.png",        "Figure 4 — Average Monthly Trading Volume"),
    ("chart4_drawdown.png",      "Figure 5 — Drawdown from Peak"),
]

# ── Auth ──────────────────────────────────────────────────────────────────────
def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                print(f"\n❌  credentials.json not found at {CREDS_FILE}")
                print("   Follow the SETUP steps at the top of this file.\n")
                raise FileNotFoundError("credentials.json missing")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds

# ── Drive: upload image → return file id ─────────────────────────────────────
def upload_image(drive_svc, path: Path, folder_id: str) -> str:
    meta = {"name": path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(path), mimetype="image/png", resumable=False)
    file = drive_svc.files().create(body=meta, media_body=media, fields="id").execute()
    fid = file["id"]
    # Make readable by anyone with the link (needed for Docs API insertInlineImage)
    drive_svc.permissions().create(
        fileId=fid,
        body={"type": "anyone", "role": "reader"},
    ).execute()
    return fid

# ── Docs helpers ──────────────────────────────────────────────────────────────
PT = 1          # 1 pt in Docs magnitude units (1 pt = 1)
def pt(n): return {"magnitude": n, "unit": "PT"}

def heading(text, level=1):
    style = f"HEADING_{level}"
    return [
        {"insertText": {"location": {"index": 1}, "text": text + "\n"}},
        {"updateParagraphStyle": {
            "range": {"startIndex": 1, "endIndex": 1 + len(text) + 1},
            "paragraphStyle": {"namedStyleType": style},
            "fields": "namedStyleType",
        }},
    ]

def body_text(text):
    return [{"insertText": {"location": {"index": 1}, "text": text + "\n"}}]

def inline_image(uri, width_pt=480):
    return [{
        "insertInlineImage": {
            "location": {"index": 1},
            "uri": uri,
            "objectSize": {
                "width":  pt(width_pt),
                "height": pt(width_pt * 6 / 14),   # preserve 14:6 aspect ratio
            },
        }
    }]

def caption(text):
    return [
        {"insertText": {"location": {"index": 1}, "text": text + "\n"}},
        {"updateParagraphStyle": {
            "range": {"startIndex": 1, "endIndex": 1 + len(text) + 1},
            "paragraphStyle": {
                "alignment": "CENTER",
                "spaceAbove": pt(2),
                "spaceBelow": pt(10),
            },
            "fields": "alignment,spaceAbove,spaceBelow",
        }},
        {"updateTextStyle": {
            "range": {"startIndex": 1, "endIndex": 1 + len(text)},
            "textStyle": {"italic": True, "foregroundColor": {
                "color": {"rgbColor": {"red": 0.4, "green": 0.4, "blue": 0.4}}
            }},
            "fields": "italic,foregroundColor",
        }},
    ]

# ── Document content (built in reverse — each block prepended at index 1) ────
CONTENT_BLOCKS = [
    # ── Conclusion ─────────────────────────────────────────────────────────
    ("h2", "6. Conclusion"),
    ("body",
     "IDT Corporation delivered exceptional long-term returns (+531% over 10 years, CAGR ~20%) "
     "while significantly outperforming the S&P 500 (+258%). The stock's high volatility and "
     "deep drawdowns make it unsuitable for risk-averse or short-horizon investors, but for "
     "those with patience and conviction in its telecom/fintech transition, a disciplined "
     "buy-and-hold strategy with periodic DCA during drawdowns offered outstanding risk-adjusted "
     "performance.\n\n"
     "Key takeaway: IDT rewarded long-term holders who ignored short-term noise. The combination "
     "of a value-driven management team (Howard Jonas), consistent buybacks, and growing fintech "
     "segment (BOSS Money, net2phone) provides a durable thesis for continued outperformance."
    ),

    # ── Risk management ────────────────────────────────────────────────────
    ("h2", "5. Risk Management"),
    ("body",
     "• Position sizing: Given 55% annualised volatility, IDT should represent no more than "
     "5–10% of a diversified portfolio.\n"
     "• Stop-loss discipline: A trailing 30% stop-loss from a recent high would have exited "
     "during the 2018 and 2020 crashes, but also re-entered at higher prices. Buy-and-hold "
     "outperformed active stop strategies over the full period.\n"
     "• Catalysts to monitor: NRS (National Retail Solutions) spin-off valuation, net2phone "
     "revenue growth, BOSS Money market share, and Howard Jonas capital allocation decisions.\n"
     "• Risks: Small-cap illiquidity, telecom regulatory changes, FX exposure (international "
     "remittances), and reliance on legacy calling-card revenue declining ~10% per year."
    ),

    # ── Strategy ───────────────────────────────────────────────────────────
    ("h2", "4. Recommended Investment Strategy"),
    ("body",
     "Core strategy: Long-term buy-and-hold with Dollar-Cost Averaging (DCA) into drawdowns.\n\n"
     "Entry rules:\n"
     "  • Initiate a position when price pulls back ≥20% from a 52-week high.\n"
     "  • Add 50% more on drawdowns ≥40% from the peak (demonstrated in 2018 and 2020).\n"
     "  • Use the 200-day MA as a long-term trend filter — only hold full position when "
     "price > 200-day MA.\n\n"
     "Exit rules:\n"
     "  • Take partial profits (25–33%) when the stock is up >100% from entry.\n"
     "  • Full exit only on fundamental deterioration (revenue collapse, management change, "
     "or loss of fintech thesis).\n\n"
     "Historical back-test summary:\n"
     "  • Investor who bought at the 2018 low ($4.79) and held to the 2025 high ($69.73) "
     "achieved +1,356% return.\n"
     "  • Investor who DCA'd $1,000/month from 2016 would have ~$180,000 invested and "
     "~$850,000 in market value at peak (2025 high).\n"
     "  • Buy-and-hold from day one (Feb 2016, $8.00) to today ($50.52): +531% vs S&P 500 +258%."
    ),

    # ── Drawdown chart ──────────────────────────────────────────────────────
    ("chart", "chart4_drawdown.png"),

    # ── Volume chart ────────────────────────────────────────────────────────
    ("chart", "chart3_volume.png"),

    # ── Risk section ───────────────────────────────────────────────────────
    ("h2", "3. Volatility & Risk Profile"),
    ("body",
     "IDT is a high-volatility small-cap stock:\n\n"
     "  • Annualised volatility: ~55% (vs ~15% for S&P 500)\n"
     "  • Maximum drawdown: -72.9% (Jul 2016 – May 2018)\n"
     "  • COVID crash drawdown (Feb–Mar 2020): ~-55% in 5 weeks\n"
     "  • Recovery from COVID low to 2021 peak: +800% in 18 months\n\n"
     "The Sharpe Ratio of 0.60 indicates moderate risk-adjusted return — below what you'd "
     "expect given raw returns, due to the extreme volatility. However, patient long-term "
     "holders were well-compensated. Figures 4 and 5 illustrate trading volume patterns "
     "and the depth of historical drawdowns."
    ),

    # ── Benchmark comparison ────────────────────────────────────────────────
    ("chart", "chart5_idt_vs_sp500.png"),
    ("h2", "2. Performance vs S&P 500"),
    ("body",
     "Over the 10-year period, IDT dramatically outperformed the S&P 500:\n\n"
     "  • IDT total return:    +531%\n"
     "  • S&P 500 total return: +258%\n"
     "  • IDT CAGR: 20.2% vs S&P 500 ~13.7%\n\n"
     "IDT underperformed the S&P 500 in 2016–2018 as its legacy telecom business declined, "
     "but massively outperformed from 2019 onward as its fintech transformation (net2phone, "
     "BOSS Money, NRS) became apparent. The key insight: IDT's alpha was concentrated in "
     "the 2020–2021 and 2023–2025 periods — investors who held through the volatile 2016–2019 "
     "trough were richly rewarded."
    ),

    # ── Annual returns ──────────────────────────────────────────────────────
    ("chart", "chart2_annual_returns.png"),

    # ── Price & MAs ─────────────────────────────────────────────────────────
    ("chart", "chart1_price_ma.png"),
    ("h2", "1. Price History & Key Milestones"),
    ("body",
     "IDT's closing price ranged from a 10-year low of $4.79 (May 2018) to a high of $69.73 "
     "(July 2025). The stock went through three distinct phases:\n\n"
     "  • 2016–2018 (Decline):    Legacy telecom revenue erosion, price fell from ~$12 to $4.79. "
     "The 50-day MA crossed below the 200-day MA (death cross), signalling a downtrend.\n\n"
     "  • 2019–2021 (Expansion):  Fintech pivot with net2phone and BOSS Money gained traction. "
     "The stock surged from ~$6 to over $40, driven by a strong golden cross (50-day MA "
     "crossing above 200-day MA) in mid-2020.\n\n"
     "  • 2022–2026 (Consolidation & New Highs):  After a correction in 2022, IDT resumed its "
     "uptrend to all-time highs above $69 in 2025, supported by NRS growth and buyback "
     "discipline under Howard Jonas."
    ),

    # ── Summary stats table ─────────────────────────────────────────────────
    ("h2", "Key Statistics (10-Year Period)"),
    ("body",
     "Metric                        Value\n"
     "─────────────────────────────────────\n"
     "Start Price (Feb 2016)        $8.00\n"
     "End Price   (Feb 2026)        $50.52\n"
     "All-Time High                 $69.73  (Jul 2025)\n"
     "All-Time Low                  $4.79   (May 2018)\n"
     "Total Return                  +531%\n"
     "CAGR                          20.2% / year\n"
     "S&P 500 Total Return          +258%\n"
     "Annualised Volatility         54.8%\n"
     "Sharpe Ratio                  0.60\n"
     "Maximum Drawdown              -72.9%\n"
    ),

    # ── Executive summary ───────────────────────────────────────────────────
    ("h2", "Executive Summary"),
    ("body",
     "IDT Corporation (NYSE: IDT) is a Newark-based telecom and fintech company controlled "
     "by Howard Jonas. Over the past 10 years (2016–2026), IDT delivered a total return of "
     "+531%, a CAGR of ~20%, and significantly outperformed the S&P 500 (+258%). However, "
     "this exceptional performance came with extreme volatility — a maximum drawdown of "
     "-72.9% and annualised volatility near 55%.\n\n"
     "This analysis covers price history, annual returns, benchmark comparison, volume "
     "trends, drawdown profiles, and provides a recommended investment strategy based on "
     "the historical data."
    ),

    # ── Title ────────────────────────────────────────────────────────────────
    ("h1", "IDT Corporation (IDT) — 10-Year Investment Strategy Analysis"),
]

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    creds = get_credentials()
    docs_svc  = build("docs",  "v1", credentials=creds)
    drive_svc = build("drive", "v3", credentials=creds)

    # 1. Create a Drive folder for this project
    print("Creating Drive folder...")
    folder = drive_svc.files().create(
        body={"name": "IDT Stock Analysis", "mimeType": "application/vnd.google-apps.folder"},
        fields="id",
    ).execute()
    folder_id = folder["id"]
    print(f"  Folder ID: {folder_id}")

    # 2. Upload all chart images
    print("Uploading charts to Drive...")
    chart_file_ids = {}
    for fname, _ in CHARTS:
        path = BASE / fname
        if not path.exists():
            print(f"  ⚠️  {fname} not found — skipping")
            continue
        fid = upload_image(drive_svc, path, folder_id)
        chart_file_ids[fname] = fid
        print(f"  Uploaded {fname} → {fid}")

    # 3. Create a blank Google Doc
    print("Creating Google Doc...")
    doc = docs_svc.documents().create(
        body={"title": "IDT Corporation — 10-Year Investment Strategy Analysis"}
    ).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"  Doc ID: {doc_id}")

    # 4. Build requests list (content is prepended at index 1 in reverse order)
    print("Building document content...")
    requests = []
    for block_type, content in CONTENT_BLOCKS:
        if block_type == "h1":
            requests += [
                {"insertText": {"location": {"index": 1}, "text": content + "\n"}},
                {"updateParagraphStyle": {
                    "range": {"startIndex": 1, "endIndex": 1 + len(content) + 1},
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }},
            ]
        elif block_type == "h2":
            requests += [
                {"insertText": {"location": {"index": 1}, "text": content + "\n"}},
                {"updateParagraphStyle": {
                    "range": {"startIndex": 1, "endIndex": 1 + len(content) + 1},
                    "paragraphStyle": {"namedStyleType": "HEADING_2"},
                    "fields": "namedStyleType",
                }},
            ]
        elif block_type == "body":
            requests += [
                {"insertText": {"location": {"index": 1}, "text": content + "\n"}},
            ]
        elif block_type == "chart":
            fname = content
            # Find matching caption
            cap_text = next((c for f, c in CHARTS if f == fname), fname)
            if fname in chart_file_ids:
                uri = f"https://drive.google.com/uc?id={chart_file_ids[fname]}"
                requests += inline_image(uri, width_pt=500)
                requests += [{"insertText": {"location": {"index": 1}, "text": cap_text + "\n"}}]
                requests += [{
                    "updateParagraphStyle": {
                        "range": {"startIndex": 1, "endIndex": 1 + len(cap_text) + 1},
                        "paragraphStyle": {"alignment": "CENTER"},
                        "fields": "alignment",
                    }
                }]
                requests += [{
                    "updateTextStyle": {
                        "range": {"startIndex": 1, "endIndex": 1 + len(cap_text)},
                        "textStyle": {"italic": True, "bold": False},
                        "fields": "italic,bold",
                    }
                }]

    # 5. Send all requests
    print(f"Sending {len(requests)} formatting requests to Google Docs...")
    # Batch in chunks of 50 to avoid API limits
    for i in range(0, len(requests), 50):
        chunk = requests[i:i+50]
        docs_svc.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": chunk},
        ).execute()
        print(f"  Processed requests {i+1}–{i+len(chunk)}")
        time.sleep(0.3)

    print(f"\n✅  Done!")
    print(f"   Google Doc: {doc_url}\n")

    # Open in browser
    import webbrowser
    webbrowser.open(doc_url)

if __name__ == "__main__":
    main()
