"""
Creates a Google Doc:
"BOSS Money Recipient App - Product Requirements Document"

Includes:
- Feature list for the Recipient app (with details)
- Improvements needed on the Sender app (with details)
- How the Recipient app helps the Sender
- Prioritization matrix (Google Docs table)
- Recommended build order with paired implementations
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE  = BASE / "token.json"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                raise FileNotFoundError("credentials.json missing")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


# ── Table data: [Feature, App, UX Impact, Revenue Impact, Priority] ───────────
TABLE_DATA = [
    ["Feature", "App", "UX Impact", "Revenue Impact", "Priority"],
    # Recipient — P0
    ["Start the purchase flow", "Recipient", "High", "High", "P0"],
    ["Subscription request", "Recipient", "High", "High", "P0"],
    ["Subscription editing request", "Recipient", "Medium", "High", "P0"],
    ["Emergency / one-tap request", "Recipient", "High", "Medium", "P0"],
    ["Notifications when top-up arrives", "Recipient", "High", "Medium", "P0"],
    ["Failed transactions notification", "Recipient", "High", "Medium", "P0"],
    ["See available carrier promos", "Recipient", "Medium", "High", "P0"],
    ["Loyalty promos visualization", "Recipient", "Medium", "High", "P0"],
    ["History of received top-ups (filter by sender)", "Recipient", "Medium", "Low", "P0"],
    # Sender — P0
    ["Trigger IMTU based on recipient request", "Sender", "High", "High", "P0"],
    ["Set top-ups subscription requested by recipient", "Sender", "High", "High", "P0"],
    # Recipient — P1
    ["Low-balance & validity expiration alerts", "Recipient", "High", "High", "P1"],
    ["Thank you messaging to sender", "Recipient", "Medium", "Low", "P1"],
    ["Multi-sender management", "Recipient", "Medium", "Medium", "P1"],
    # Sender — P1
    ["Get low-balance alerts (carrier API)", "Sender", "High", "High", "P1"],
    ["Confirm delivery (carrier API)", "Sender", "High", "Medium", "P1"],
    ["Thank you messaging from recipient", "Sender", "Medium", "Low", "P1"],
    ["View transaction request history", "Sender", "Medium", "Low", "P1"],
    ["Blocking numbers", "Sender", "Low", "Low", "P1"],
]

NUM_ROWS = len(TABLE_DATA)
NUM_COLS = 5


# ── Helpers ───────────────────────────────────────────────────────────────────
def ins(text):
    return {"insertText": {"location": {"index": 1}, "text": text + "\n"}}

def para_style(text, style):
    return {"updateParagraphStyle": {
        "range": {"startIndex": 1, "endIndex": 1 + len(text) + 1},
        "paragraphStyle": {"namedStyleType": style},
        "fields": "namedStyleType",
    }}

def insert_table():
    return {"insertTable": {"location": {"index": 1}, "rows": NUM_ROWS, "columns": NUM_COLS}}


# ── Content blocks in REVERSE order (each block prepended at index 1) ─────────
BLOCKS = [
    # ── Recommended Build Order ──────────────────────────────────────────────
    ("h2", "Recommended Build Order"),
    ("body",
     "Tier 1 — MVP (P0). Deliver the end-to-end recipient-to-sender request flow. Without this, "
     "neither app produces value. Required pairs that must be built together:\n"
     "  • Start the purchase flow (Recipient) + Trigger IMTU based on recipient request (Sender)\n"
     "  • Subscription request (Recipient) + Set top-ups subscription (Sender)\n"
     "  • Subscription editing request (Recipient) + Approve subscription edits (Sender)\n\n"
     "Other P0 features that can be built in parallel within Tier 1:\n"
     "  • Notifications when top-up arrives, failed transaction notifications, emergency one-tap, "
     "carrier promos, loyalty promos, history with sender filter\n\n"
     "Tier 2 — High-value post-MVP (P1). Drives revenue and reduces support load:\n"
     "  • Low-balance & validity alerts on the Recipient side\n"
     "  • Get low-balance alerts via carrier API on the Sender side (paired)\n"
     "  • Confirm delivery via carrier API on the Sender side\n\n"
     "Tier 3 — Engagement & polish (P1):\n"
     "  • Thank you messaging on both apps (paired)\n"
     "  • Multi-sender management on the Recipient side\n"
     "  • View transaction request history on the Sender side\n\n"
     "Tier 4 — Defer (P1, low impact):\n"
     "  • Blocking numbers (Sender side, anti-abuse)"
    ),

    # ── Table placeholder ────────────────────────────────────────────────────
    ("table", None),
    ("body",
     "Each feature is scored on UX Impact (does it materially improve the user's daily experience?) "
     "and Revenue Impact (does it drive transactions, AOV, or retention?). P0 = required for MVP "
     "launch; P1 = post-MVP enhancement."
    ),
    ("h2", "Prioritization Matrix"),

    # ── How the Recipient App Helps the Sender ───────────────────────────────
    ("body",
     "•  Pull-based model reduces friction for both sides — the recipient knows exactly what they "
     "need; the sender approves in one tap instead of guessing amount, offer, or timing.\n\n"
     "•  Preference-driven purchases — the sender sends the right product (data vs. airtime, "
     "correct bundle size, best promo) because the recipient has specified it in their request.\n\n"
     "•  Reduces support load and failed transactions — fewer wrong-number errors, fewer disputes, "
     "fewer 'did you receive it?' chats over WhatsApp."
    ),
    ("h2", "3. How the Recipient App Helps the Sender"),

    # ── Sender Improvements ──────────────────────────────────────────────────
    ("body",
     "P0 — Required for MVP\n\n"
     "Purchase flow: Trigger IMTU based on a recipient request\n"
     "Sender receives a push notification for each incoming request and approves with one tap. "
     "This is the bridge that links the two apps; nothing else functions without it.\n\n"
     "Purchase flow: Set top-ups subscription requested by recipient\n"
     "Sender reviews and approves a recurring top-up that the recipient configured. Converts "
     "one-off transactions into predictable monthly revenue.\n\n"
     "P1 — Post-MVP\n\n"
     "Management: Blocking numbers\n"
     "Lets the sender block specific recipient numbers from submitting requests. Prevents abuse "
     "from estranged contacts without forcing app removal.\n\n"
     "Informative: Thank you messaging from recipient\n"
     "Displays the recipient's thank-you note inside the sender app after each top-up. Closes the "
     "emotional loop and reinforces the human relationship behind every transaction.\n\n"
     "Informative: View transaction request history\n"
     "Full log of incoming requests (approved, declined, pending) with filters by recipient, date, "
     "and amount. Supports trust and post-hoc analysis.\n\n"
     "Informative: Get low-balance alerts (carrier API)\n"
     "Push notification when a linked recipient's balance drops below threshold (recipient opt-in). "
     "Drives proactive top-ups without waiting for a request.\n\n"
     "Informative: Confirm delivery (carrier API)\n"
     "Confirms the top-up landed on the recipient's line via carrier API — replaces the ambiguous "
     "'transaction sent' state. Cuts support tickets and increases trust."
    ),
    ("h2", "2. Improvements for the Sender App"),

    # ── Recipient Features ───────────────────────────────────────────────────
    ("body",
     "P0 — Required for MVP\n\n"
     "Purchase flow: Start the purchase flow (choose available offers, sender)\n"
     "Recipient browses available offers (airtime, data bundles, carrier promos) and selects a "
     "linked sender to submit the request to. The foundational flow that produces every transaction.\n\n"
     "Purchase flow: Subscription request\n"
     "Recipient sets up a recurring top-up (offer, frequency, day of month) and submits it to a "
     "sender for approval. Drives recurring revenue and predictable monthly cash flow.\n\n"
     "Purchase flow: Subscription editing request (change offer, frequency, date)\n"
     "Lets the recipient request changes to an active subscription (different offer, new schedule, "
     "or pause). Reduces churn vs. forcing cancel-and-restart.\n\n"
     "Purchase flow: Emergency / one-tap request (quick Send)\n"
     "Single shortcut on the home screen to request an immediate small top-up from a default "
     "sender. For urgent moments (out of data, need a call now).\n\n"
     "Informative: Notifications when top-up arrives (who sent it, offer details)\n"
     "Real-time push notification with sender name, offer details, and local-currency value. "
     "The signature moment of the recipient experience.\n\n"
     "Informative: Failed transactions notification\n"
     "Push notification when a top-up fails, with failure reason and next steps. Critical for "
     "trust — the recipient must know immediately if something went wrong.\n\n"
     "Promos: See available carrier promos\n"
     "Surfaces current carrier promotions (2x data weekends, bonus airtime, limited-time bundles) "
     "so the recipient requests the best-value offer at the right time. Lifts AOV per transaction.\n\n"
     "Promos: Loyalty promos visualization\n"
     "Shows BOSS Money loyalty rewards, referral credits, and promotional offers tied to the "
     "transaction history. Drives retention and increased purchase frequency.\n\n"
     "Informative: History of received top-ups (filter by sender)\n"
     "Chronological log of all received top-ups, filterable by sender, date, and offer. Supports "
     "trust and creates a clear family-support record over time.\n\n"
     "P1 — Post-MVP\n\n"
     "Informative: Low-balance and validity expiration alerts\n"
     "Notification when balance is low or about to expire, with a one-tap shortcut to send a "
     "top-up request. Especially critical in prepaid markets where unused credit is forfeited.\n\n"
     "Informative: Thank you messaging to sender\n"
     "Quick thank-you note or emoji sent to the sender after each top-up. Closes the emotional "
     "loop and reinforces the long-term relationship behind the transactions.\n\n"
     "Management: Multi-sender management (coordinate across family)\n"
     "Manage multiple linked senders (mom in Miami, brother in London) with separate permissions, "
     "preferences, and default offers. Standard in extended family structures across LATAM, "
     "Caribbean, and African corridors."
    ),
    ("h2", "1. Recipient App Features"),

    # ── Overview ─────────────────────────────────────────────────────────────
    ("body",
     "BOSS Money has historically been a sender-only experience: the diaspora user initiates and "
     "manages every transaction. The recipient is a passive endpoint with no app of their own.\n\n"
     "This PRD defines a companion app for BOSS Money recipients, plus the parallel improvements "
     "required on the existing BOSS Money sender app for the two to function together. Some "
     "features must be implemented on both apps in parallel — these are explicitly called out in "
     "the Recommended Build Order section.\n\n"
     "Together, the two apps shift the experience from a one-sided send to a two-sided "
     "request-and-approve model — unlocking recurring revenue, reducing failed transactions, "
     "and creating a network effect that makes BOSS Money harder for users to abandon."
    ),
    ("h2", "Overview"),

    # ── Title ────────────────────────────────────────────────────────────────
    ("h1", "BOSS Money Recipient App — Product Requirements Document"),
]


def main():
    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)

    print("Creating Google Doc...")
    doc = docs_svc.documents().create(
        body={"title": "BOSS Money Recipient App — PRD"}
    ).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"  Doc ID: {doc_id}")

    # Phase 1: Insert narrative content + empty table
    requests = []
    for block_type, content in BLOCKS:
        if block_type == "h1":
            requests += [ins(content), para_style(content, "HEADING_1")]
        elif block_type == "h2":
            requests += [ins(content), para_style(content, "HEADING_2")]
        elif block_type == "body":
            requests += [ins(content)]
        elif block_type == "table":
            requests += [insert_table()]

    print(f"Phase 1: Sending {len(requests)} narrative requests...")
    for i in range(0, len(requests), 50):
        chunk = requests[i:i+50]
        for attempt in range(3):
            try:
                docs_svc.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": chunk},
                ).execute()
                print(f"  Processed {i+1}-{i+len(chunk)}")
                break
            except Exception as e:
                if attempt < 2:
                    print(f"  Retry {attempt+1}/2: {str(e)[:100]}")
                    time.sleep(1.0)
                else:
                    raise
        time.sleep(0.3)

    # Phase 2: Locate the table and collect cell positions
    print("Phase 2: Locating table cells...")
    doc_data = docs_svc.documents().get(documentId=doc_id).execute()
    table_elem = None
    for element in doc_data["body"]["content"]:
        if "table" in element:
            table_elem = element["table"]
            break

    if not table_elem:
        print("⚠️  Table not found in document!")
        return

    cells_to_fill = []
    for row_idx, row in enumerate(table_elem["tableRows"]):
        for col_idx, cell in enumerate(row["tableCells"]):
            # Cell content starts at content[0].startIndex
            cell_text_idx = cell["content"][0]["startIndex"]
            text = TABLE_DATA[row_idx][col_idx]
            cells_to_fill.append((cell_text_idx, text))

    # Sort by index DESCENDING so inserts don't shift earlier cell indices
    cells_to_fill.sort(key=lambda x: x[0], reverse=True)

    print(f"Phase 3: Filling {len(cells_to_fill)} table cells...")
    fill_requests = [
        {"insertText": {"location": {"index": idx}, "text": text}}
        for idx, text in cells_to_fill
    ]

    for i in range(0, len(fill_requests), 50):
        chunk = fill_requests[i:i+50]
        docs_svc.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": chunk},
        ).execute()
        time.sleep(0.3)

    # Phase 4: Bold the header row + style the table cells
    print("Phase 4: Formatting header row...")
    doc_data = docs_svc.documents().get(documentId=doc_id).execute()
    table_elem = None
    for element in doc_data["body"]["content"]:
        if "table" in element:
            table_elem = element["table"]
            break

    format_requests = []
    header_row = table_elem["tableRows"][0]
    for cell in header_row["tableCells"]:
        cell_para = cell["content"][0].get("paragraph", {})
        for elem in cell_para.get("elements", []):
            if "textRun" in elem:
                start = elem["startIndex"]
                end = elem["endIndex"]
                format_requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": start, "endIndex": end},
                        "textStyle": {"bold": True},
                        "fields": "bold",
                    }
                })

    # Shade the header row background
    if header_row["tableCells"]:
        first_cell = header_row["tableCells"][0]
        # Find the parent table's start index
        for element in doc_data["body"]["content"]:
            if "table" in element:
                table_start_idx = element["startIndex"]
                break
        format_requests.append({
            "updateTableCellStyle": {
                "tableCellStyle": {
                    "backgroundColor": {
                        "color": {"rgbColor": {"red": 0.93, "green": 0.93, "blue": 0.93}}
                    }
                },
                "fields": "backgroundColor",
                "tableRange": {
                    "tableCellLocation": {
                        "tableStartLocation": {"index": table_start_idx},
                        "rowIndex": 0,
                        "columnIndex": 0,
                    },
                    "rowSpan": 1,
                    "columnSpan": NUM_COLS,
                }
            }
        })

    if format_requests:
        docs_svc.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": format_requests},
        ).execute()

    print(f"\n✅  Done!")
    print(f"   Google Doc: {doc_url}\n")

    import webbrowser
    webbrowser.open(doc_url)


if __name__ == "__main__":
    main()
