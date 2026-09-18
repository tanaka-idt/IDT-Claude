"""
Creates a Google Doc: "IMTU Subscription Toggle (ON/OFF) — Analysis & Conclusions"
Uses the same OAuth credentials (token.json / credentials.json) as create_imtu_doc.py.

Content is authored in normal reading order in SECTIONS and inserted in reverse
(each block is prepended at index 1), mirroring create_imtu_doc.py.
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
TITLE = "IMTU Subscription Toggle (ON/OFF) — Analysis & Conclusions"


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

# ── Content in NORMAL reading order ──────────────────────────────────────────
SECTIONS = [
    ("h1", TITLE),
    ("body",
     "Boss Revolution · IMTU · Amplitude project: BR app Prod (650506) · Prepared 2026-06-25\n"
     "Scope: analysis of the subscription ON/OFF toggle on the IMTU offer/order confirmation screen."),

    ("h2", "1. What the feature is"),
    ("body",
     "On the IMTU offer/order confirmation screen, a subscription toggle controls whether the top-up "
     "becomes recurring. When the toggle is left ON, completing the top-up also creates a recurring "
     "subscription; when it is OFF, the top-up is one-time. Users can flip the toggle on the confirmation "
     "screen before paying.\n\n"
     "The feature launched as an A/B experiment on the toggle's DEFAULT state. Per the events tracking plan: "
     "variant A = default ON (subscription_on), variant B = default OFF (subscription_off). Default-ON "
     "exposure only ramped up in June 2026."),

    ("h2", "2. Dashboards (Amplitude)"),
    ("body",
     "Overview — Behavior, Funnel & Cancellation:\n"
     "https://app.amplitude.com/analytics/BOSS/dashboard/4slmct3m\n\n"
     "Deep-dive — Transition Cancellation & Deeper Behavior:\n"
     "https://app.amplitude.com/analytics/BOSS/dashboard/4qi0ak6h\n\n"
     "Note: the underlying charts are currently saved unpublished in a personal space and should be "
     "reviewed before publishing/sharing."),

    ("h2", "3. Key conclusions"),

    ("h3", "3.1 Defaulting the toggle ON is a powerful subscription driver"),
    ("body",
     "When the toggle defaults ON, ~91% of order-screen viewers end up with a subscription, versus ~6% when "
     "it defaults OFF. Because only ~22% of users interact with the toggle at all, the default state largely "
     "decides whether a subscription is created."),

    ("h3", "3.2 …at a small cost to order completion"),
    ("body",
     "Defaulting the toggle ON slightly lowers overall order completion — roughly 88% (default ON) versus "
     "90.5% (default OFF), about a 2 percentage-point difference. The subscription lift far outweighs this "
     "modest completion cost."),

    ("h3", "3.3 Users mostly opt OUT, rarely opt IN"),
    ("body",
     "Among users who do interact with the toggle, far more turn a default-ON toggle OFF (~114k taps over "
     "90 days) than turn a default-OFF toggle ON (~57k). This confirms the default is doing the heavy "
     "lifting, and that a meaningful share of default-ON users actively decline the subscription."),

    ("h3", "3.4 The cancellation flow has almost no 'save' step"),
    ("body",
     "Of users who tap 'cancel' and reach the confirmation, ~96%+ go through with it; very few choose "
     "'keep'. The cancel flow currently has effectively no deflection (no pause, discount, or reason "
     "capture). This is the clearest near-term retention opportunity."),

    ("h3", "3.5 Cancellation by toggle transition (the four cohorts)"),
    ("body",
     "Cohorts from the toggle tap (default_state → new_state), funnel into cancellation success "
     "(90-day window). Cancellation rate = share of the cohort that reaches a cancellation:\n\n"
     "•  off → on (opt-in):  ~36,500 users  —  ~28.0% cancellation rate\n"
     "•  off → off (kept off):  ~95,300 users  —  ~22.6%\n"
     "•  on → off (opt-out):  ~44,400 users  —  ~8.1%\n"
     "•  on → on (kept on):  ~4,200 users  —  negligible / insufficient data\n\n"
     "Read these with care — two effects distort them:\n"
     "1.  Maturity skew (dominant): default-OFF has existed for months, while default-ON only ramped in "
     "June 2026. The ON-default cohorts (on→off, on→on) have had little time to accumulate cancellations, "
     "so their low rates mostly reflect insufficient elapsed time, not better retention.\n"
     "2.  Attribution conflation: the funnel counts a cancellation of any subscription within 90 days, not "
     "strictly the one created in that exact flow. This is why off→off shows ~22.6% despite those users not "
     "subscribing via that toggle — they are cancelling other subscriptions. Treat off→off as a "
     "noise/baseline indicator.\n\n"
     "Defensible takeaway today: among mature (default-OFF) cohorts, active opt-in (off→on) users show the "
     "highest cancellation activity (~28%) — deliberate subscribers are also active managers/cancellers. "
     "The ON-default cohorts need several more weeks before their cancellation behavior is trustworthy."),

    ("h3", "3.6 Subscription frequency choices"),
    ("body",
     "Among users who explicitly choose a frequency, the longest cadence is the most popular:\n\n"
     "•  Every 90 days — ~12,800\n"
     "•  Every 30 days — ~10,900\n"
     "•  Every 7 days — ~10,200\n"
     "•  Every 14 days — ~4,200"),

    ("h3", "3.7 Other behavioral signals"),
    ("body",
     "•  Duplicate-subscription warnings are rising to ~1,400–1,600 users/week — a meaningful number of "
     "users nearly re-subscribe to something they may already have (relevant to the 'accidentally "
     "subscribed' cancellation reason).\n"
     "•  ~11,000–13,000 users/week enter the manage/edit subscription screen — the top of the "
     "cancellation-intent funnel.\n"
     "•  A time-from-subscribe-to-cancellation distribution is available on the deep-dive dashboard, showing "
     "how long subscriptions survive before cancellation."),

    ("h2", "4. Caveats"),
    ("body",
     "•  Maturity: default-ON ramped only in June 2026 — long-run churn comparisons involving ON-default "
     "cohorts are preliminary.\n"
     "•  Attribution: toggle-transition → cancellation funnels can capture cancellations of unrelated "
     "subscriptions within the window.\n"
     "•  Instrumentation gap: MTUSubscriptionPayTap (toggle state and is_subscription at the moment of Pay) "
     "is defined but not yet implemented, so the true final toggle-state-at-purchase is currently inferred.\n"
     "•  Charts are unpublished in a personal space pending review."),

    ("h2", "5. Recommendations"),
    ("body",
     "1.  Instrument MTUSubscriptionPayTap (toggle_enabled + is_subscription at Pay) to capture the true "
     "final toggle state at purchase and remove funnel-inferred state.\n\n"
     "2.  Re-measure transition cancellation in ~4–6 weeks once the default-ON cohort matures, ideally "
     "holding recipient_phone_number constant across subscribe → cancel so the cancellation is tied to the "
     "same subscription.\n\n"
     "3.  Add a save/deflection step to the cancel flow (pause, reason capture, or a targeted offer) — the "
     "flow currently lets ~96%+ cancel with no intervention.\n\n"
     "4.  Reduce accidental subscriptions: monitor the rising duplicate-subscription warnings and consider "
     "clearer subscribe consent / confirmation on the toggle.\n\n"
     "5.  On rolling out default-ON: the subscription lift (~91% vs ~6%) is large and the order-completion "
     "cost is small (~2pp), but continue to monitor cancellation as the ON cohort matures before committing "
     "to a full default-ON rollout."),
]


def main():
    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)

    print("Creating Google Doc...")
    doc = docs_svc.documents().create(body={"title": TITLE}).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"  Doc ID: {doc_id}")

    # Insert in REVERSE so the first section ends up at the top.
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
