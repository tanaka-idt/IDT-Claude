"""
Creates a Google Doc: "IMTU Validity Reminder — Initial Campaign Brief (Backend)"
Uses the same OAuth credentials (token.json / credentials.json) as create_imtu_doc.py.
Content authored in normal reading order; inserted in reverse (each block prepended at index 1).
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
TOKEN_FILE = BASE / "token.json"
TITLE = "IMTU Validity Reminder — Initial Campaign Brief (Backend)"


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


STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3"}

SECTIONS = [
    ("h1", TITLE),
    ("body",
     "Boss Revolution · IMTU · Draft 2026-06-27 · Owner: João Tanaka · Audience: Backend team\n"
     "Status: initial campaign definition — parameters marked “TBD” need confirmation before build."),

    ("h2", "1. Objective"),
    ("body",
     "We built a notification service that reminds users their purchased top-up offer is approaching its "
     "validity (expiry) date — i.e., it's time to top up again. The reminder is sent a few days before the "
     "original offer expires so the user can buy another one before it expires, or right when the old one "
     "expires. Goal: increase repurchase / retention by prompting timely re-purchase."),

    ("h2", "2. How the reminder works"),
    ("body",
     "•  Trigger: based on the purchased offer's validity period and purchase date.\n"
     "•  Timing: sent N days before the offer's expiry (N = TBD — e.g., 1–2 days before).\n"
     "•  Channel: SMS or push notification (channel priority / fallback = TBD).\n"
     "•  Outcome we want: the user purchases a new top-up before or at the moment the current offer expires."),

    ("h2", "3. Initial campaign scope"),
    ("body",
     "•  Target audience: users who purchased Tigo top-up offers with a 7-day validity.\n"
     "•  Enrollment window: users who buy a qualifying Tigo offer during a one-week period.\n"
     "•  Start: first days of July 2026.\n"
     "•  Reminder send: a few days before each enrolled user's 7-day offer expires (N = TBD).\n"
     "•  Measurement: evaluate results over the following weeks (repurchase behavior after the reminder).\n"
     "•  Control group: a randomly held-out portion of eligible users receives NO reminder, so we can "
     "measure the lift from the notification."),

    ("h2", "4. Backend requirements"),
    ("body",
     "•  Eligibility detection: identify transactions where carrier = Tigo and offer validity = 7 days, "
     "within the one-week enrollment window. (Confirm exact carrier identifier and how validity is stored.)\n"
     "•  Reminder scheduling: compute send time per enrolled transaction = purchase date + (7 − N) days. "
     "Define N (lead days before expiry).\n"
     "•  Group assignment: randomly assign each eligible user to control (no reminder) or treatment "
     "(reminder). Assignment must be stable per user and recorded.\n"
     "•  Channel handling: choose SMS vs push per user (e.g., push if available/opted-in, else SMS) and "
     "define fallback. Respect notification opt-out / consent.\n"
     "•  Deduplication & suppression: at most one reminder per qualifying offer; avoid double-sends and "
     "avoid reminding users who already repurchased.\n"
     "•  Tracking/events (for measurement): emit events for reminder scheduled, sent, delivered, "
     "opened/clicked, and link to any subsequent repurchase — each tagged with the group (control / "
     "treatment), channel, carrier, and offer/validity. This is required to measure effectiveness in "
     "Amplitude."),

    ("h2", "5. Measurement & control group"),
    ("body",
     "•  Primary metric: repurchase rate within the attribution window after the reminder send / expiry "
     "(window = TBD, e.g., reminder date through a few days after expiry).\n"
     "•  Comparison: treatment vs control repurchase rate = the campaign lift.\n"
     "•  Secondary: time-to-repurchase, channel performance (SMS vs push), and notification "
     "delivered/open/click rates.\n"
     "•  The control group must be drawn from the same eligible population (Tigo, 7-day validity, same "
     "enrollment week) and sized to detect a meaningful difference (split % = TBD, e.g., 80/20 or 50/50)."),

    ("h2", "6. Parameters to confirm (TBD)"),
    ("body",
     "•  N — how many days before expiry the reminder is sent.\n"
     "•  Control/treatment split (e.g., 80/20 vs 50/50) and minimum sample size.\n"
     "•  Channel priority and fallback (SMS vs push) and consent handling.\n"
     "•  Tigo market scope — all Tigo countries or a specific country?\n"
     "•  Exact start date and the one-week enrollment window.\n"
     "•  Repurchase attribution window for measuring success."),
]


def main():
    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)

    print("Creating Google Doc...")
    doc = docs_svc.documents().create(body={"title": TITLE}).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"  Doc ID: {doc_id}")

    requests = []
    for block_type, content in reversed(SECTIONS):
        if block_type in STYLE_MAP:
            requests += [ins(content), para_style(content, STYLE_MAP[block_type])]
        else:
            requests += [ins(content)]

    print(f"Sending {len(requests)} requests to Google Docs...")
    for i in range(0, len(requests), 50):
        chunk = requests[i:i + 50]
        for attempt in range(3):
            try:
                docs_svc.documents().batchUpdate(
                    documentId=doc_id, body={"requests": chunk}
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

    print("\n✅  Done!")
    print(f"   Google Doc: {doc_url}\n")


if __name__ == "__main__":
    main()
