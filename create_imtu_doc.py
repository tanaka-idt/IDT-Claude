"""
Creates a Google Doc: "IMTU Recipient App — Needs & Opportunities"
Uses the same OAuth credentials as create_google_doc.py.
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


def ins(text):
    return {"insertText": {"location": {"index": 1}, "text": text + "\n"}}

def para_style(text, style):
    return {"updateParagraphStyle": {
        "range": {"startIndex": 1, "endIndex": 1 + len(text) + 1},
        "paragraphStyle": {"namedStyleType": style},
        "fields": "namedStyleType",
    }}

def bold_range(start, end):
    return {"updateTextStyle": {
        "range": {"startIndex": start, "endIndex": end},
        "textStyle": {"bold": True},
        "fields": "bold",
    }}


# Content built in REVERSE order (each block is prepended at index 1)
BLOCKS = [

    # ── 4. Recommendations ───────────────────────────────────────────────────
    ("h2", "4. Recommendations"),
    ("body",
     "1.  Build a Recipient Profile Card first\n"
     "A QR-code-based shareable profile (phone number + carrier) is the foundation of the two-sided network. "
     "It immediately reduces sender errors and is the primary onboarding hook for recipients who don't "
     "already know the Boss Revolution brand.\n\n"
     "2.  Position the app as an 'airtime tracker', not a Boss Revolution companion\n"
     "Don't lead with Boss Revolution in the recipient onboarding — position the app as a personal "
     "airtime/data management tool. Lower friction for recipients. The IMTU connection becomes a feature, "
     "not the pitch.\n\n"
     "3.  Launch the pull/request model early\n"
     "A structured top-up request flow — recipient picks a specific package, sends to a named sender, "
     "sender approves and pays — is the highest-value differentiator vs. competitors. It shifts the dynamic "
     "from 'sender guesses' to 'recipient expresses need.'\n\n"
     "4.  Make carrier promos a shared asset\n"
     "Surface active promotions in both the sender and recipient apps simultaneously. The recipient sees "
     "'there's a 3x data promo this week' and can nudge the sender — this drives engagement from both sides "
     "without extra effort from either.\n\n"
     "5.  Design permission-based balance sharing carefully\n"
     "Sharing balance with a sender is privacy-sensitive. Build it with clear per-sender opt-in consent and "
     "easy revocation. The trust payoff is high, but the risk of getting it wrong (user churn, negative "
     "press in communities) is real.\n\n"
     "6.  Plan for multi-sender from day one\n"
     "In many LATAM, African, and Caribbean families, multiple diaspora members top up a single recipient. "
     "The data model and UX must support multiple linked senders per recipient from the start — "
     "retrofitting this later is expensive and risks breaking the sender experience."
    ),

    # ── 3. How the Recipient App Helps the Sender ────────────────────────────
    ("h2", "3. How the Recipient App Helps the Sender"),
    ("body",
     "Having a recipient on the platform creates compounding value for the sender side:\n\n"
     "Eliminates number and carrier errors\n"
     "The recipient owns and maintains their own verified profile. The sender always has the correct phone "
     "number and carrier — reducing failed top-ups to wrong numbers or stale carriers.\n\n"
     "Pull-based model reduces friction\n"
     "Instead of the sender guessing when to send, the recipient initiates the request. The sender approves "
     "and pays — no back-and-forth over WhatsApp to confirm number and amount.\n\n"
     "Preference-driven purchasing\n"
     "The sender knows exactly what to buy (data vs. airtime, which bundle size) because the recipient has "
     "expressed their preferences. No wasted spend on the wrong product.\n\n"
     "Promo optimization\n"
     "The recipient app surfaces active carrier promotions specific to their carrier. The sender gets more "
     "value per dollar without researching the promotions themselves.\n\n"
     "True delivery confirmation\n"
     "The sender receives confirmed receipt from the recipient's device — not just a 'transaction sent' "
     "status from the carrier API, which may not reflect actual delivery.\n\n"
     "Opt-in balance visibility\n"
     "The recipient can share their current balance with trusted senders. The sender knows when to act "
     "without waiting to be asked, enabling proactive support for the family.\n\n"
     "Automatic carrier change sync\n"
     "If the recipient switches carriers or phone numbers, their profile updates automatically. The sender's "
     "next top-up goes to the right place without any manual correction.\n\n"
     "Family coordination\n"
     "Multiple senders can see shared activity (with recipient permission) — preventing duplicate top-ups "
     "and allowing family members to divide responsibility efficiently.\n\n"
     "Reduced support burden\n"
     "Fewer wrong-number errors, failed transactions, and 'did you receive it?' messages reduce friction "
     "for the sender and lower customer support costs for IDT.\n\n"
     "Platform stickiness\n"
     "A recipient embedded in the Boss Revolution ecosystem gives the sender a strong reason to stay loyal "
     "vs. switching to a competing service like Remitly, MobileRecharge, or carrier-direct apps."
    ),

    # ── 2. Recipient Needs ───────────────────────────────────────────────────
    ("h2", "2. Recipient Needs"),
    ("body",
     "What the recipient's own app should address:\n\n"
     "•  Top-up arrival notifications — Push notification when airtime or data arrives: who sent it, "
     "how much, and the local-currency value equivalent.\n\n"
     "•  Top-up request flow (pull model) — Proactively request a top-up from a specific sender. Choose "
     "a specific package or amount rather than sending a generic 'please send me credit' message.\n\n"
     "•  Verified phone number & carrier profile — Maintain a profile that senders can trust, "
     "eliminating the #1 cause of failed top-ups: wrong number or stale carrier information.\n\n"
     "•  Carrier promo discovery — See active promotions and data bundle options for their specific "
     "carrier, so they can inform senders of the best time to top up.\n\n"
     "•  Preference expression — Declare preferences (e.g., 'I prefer 1 GB data over airtime', "
     "'I always use WhatsApp, not calls') so senders know exactly what to buy.\n\n"
     "•  Low-balance alerts — Receive a notification when balance drops below a threshold, with an "
     "option to trigger an automatic top-up request to a preferred sender.\n\n"
     "•  Balance expiry alerts — Notification before airtime or a bundle expires, which is critical in "
     "prepaid markets where unused credit is forfeited.\n\n"
     "•  Top-up history — View all received top-ups sorted by sender and date, providing a clear record "
     "of family support over time.\n\n"
     "•  Multi-sender management — Manage relationships with multiple senders (e.g., mom in Miami, "
     "brother in London), each with separate permissions and preferences.\n\n"
     "•  Local currency transparency — See the local-currency equivalent of each top-up so the "
     "recipient understands the value being sent.\n\n"
     "•  Sender acknowledgment — Send a quick thank-you or confirmation to the sender within the app, "
     "reinforcing the relationship and closing the communication loop.\n\n"
     "•  Carrier/number change notification — Automatically alert all linked senders when they switch "
     "carriers or phone numbers, preventing the next top-up from failing.\n\n"
     "•  Package wishlist — Create a short list of preferred packages (e.g., 'the $10 5 GB bundle') "
     "that senders can fulfill in a single tap without research.\n\n"
     "•  Usage pattern insights — See how quickly they typically consume airtime or data, helping them "
     "time requests more accurately and plan ahead.\n\n"
     "•  One-tap emergency request — A dedicated shortcut for urgent situations: one tap sends a "
     "priority top-up request to a designated sender."
    ),

    # ── 1. Sender Needs ──────────────────────────────────────────────────────
    ("h2", "1. Sender Needs"),
    ("body",
     "What the sender requires from the IMTU ecosystem (existing needs, expanded):\n\n"
     "•  Trigger a top-up in response to a recipient request — Act on an incoming request from the "
     "recipient rather than initiating unprompted.\n\n"
     "•  Track delivery status — Know whether a top-up is in transit, delivered, or failed, with "
     "real-time status rather than a one-shot 'sent' confirmation.\n\n"
     "•  View transaction history — See past top-ups by recipient, amount, date, and carrier promotion "
     "used, to understand spending patterns and family support habits.\n\n"
     "•  Discover active carrier promotions — Know which promotional bundles are available for a "
     "specific recipient's carrier before deciding how much to send.\n\n"
     "•  Set up recurring or scheduled top-ups — Automate a monthly or weekly top-up to a recipient "
     "so they never run out of airtime between active requests.\n\n"
     "•  Receive low-balance alerts for recipients — Get notified when a recipient's balance is low "
     "(with recipient permission), enabling proactive support without waiting to be asked.\n\n"
     "•  Get true delivery confirmation — Confirm the recipient actually received and can use the "
     "top-up, not just that the transaction was submitted to the carrier.\n\n"
     "•  Avoid number and carrier errors — Always have the correct current phone number and carrier "
     "for each recipient, eliminating the most common cause of failed or misdirected top-ups."
    ),

    # ── Overview ─────────────────────────────────────────────────────────────
    ("h2", "Overview"),
    ("body",
     "International Mobile Top-Up (IMTU) connects senders — typically diaspora living abroad — with "
     "recipients in their home countries who depend on prepaid mobile airtime and data. Today, Boss "
     "Revolution's IMTU experience is entirely sender-centric: the sender initiates, pays, and tracks "
     "everything. The recipient is a passive endpoint.\n\n"
     "A companion app for the recipient changes this dynamic by creating a two-sided ecosystem. The "
     "recipient gains agency over their own airtime needs; the sender gains accuracy, transparency, and "
     "reduced friction. Together, this unlocks new engagement and differentiates Boss Revolution from "
     "commodity top-up services that offer no recipient-side experience."
    ),

    # ── Title ────────────────────────────────────────────────────────────────
    ("h1", "IMTU Recipient App — Needs & Opportunities"),
]


def main():
    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)

    print("Creating Google Doc...")
    doc = docs_svc.documents().create(
        body={"title": "IMTU Recipient App — Needs & Opportunities"}
    ).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"  Doc ID: {doc_id}")

    requests = []
    for block_type, content in BLOCKS:
        if block_type == "h1":
            requests += [ins(content), para_style(content, "HEADING_1")]
        elif block_type == "h2":
            requests += [ins(content), para_style(content, "HEADING_2")]
        elif block_type == "body":
            requests += [ins(content)]

    print(f"Sending {len(requests)} requests to Google Docs...")
    for i in range(0, len(requests), 50):
        chunk = requests[i:i+50]
        for attempt in range(3):
            try:
                docs_svc.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": chunk},
                ).execute()
                print(f"  Processed {i+1}–{i+len(chunk)}")
                break
            except Exception as e:
                if attempt < 2:
                    print(f"  Retry {attempt+1}/2: {str(e)[:80]}")
                    time.sleep(1.0)
                else:
                    raise
        time.sleep(0.2)

    print(f"\n✅  Done!")
    print(f"   Google Doc: {doc_url}\n")

    import webbrowser
    webbrowser.open(doc_url)


if __name__ == "__main__":
    main()
