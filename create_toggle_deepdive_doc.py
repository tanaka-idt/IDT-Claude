"""
Creates a Google Doc: "IMTU Subscription Cancellation & Toggle — Deep Dive Findings"
Uses the same OAuth credentials as create_google_doc.py / create_imtu_doc.py.
"""

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


# Content built in REVERSE order (each block is prepended at index 1)
BLOCKS = [

    # ── 6. Appendix ──────────────────────────────────────────────────────────
    ("h2", "6. Appendix — Links & Reference Numbers"),
    ("body",
     "Dashboards (Amplitude, BOSS org, personal space/unpublished):\n"
     "• Deep Dive (this analysis): https://app.amplitude.com/analytics/BOSS/dashboard/dsyei9ee\n"
     "• Rollout Behavior Analysis (companion): https://app.amplitude.com/analytics/BOSS/dashboard/bx3h416b\n"
     "• Conclusions summary doc (Jul 2): "
     "https://docs.google.com/document/d/1dtmdBCbr4Fq4Rkft5i7SkUDDsJsyeSzQdLH645EdYAI/edit\n\n"
     "Reference numbers (BR app Prod 650506, Mar 1 – Jul 2, 2026):\n"
     "• Cancel flow funnel (1h): 103,860 edit-screen viewers → 80,831 Cancel (77.8%) → 79,969 Yes "
     "(98.9%) → 79,838 success. Total 76.9%. Median 7s → 3s → 0s.\n"
     "• Purchase→cancel: 8.8% ≤7d (median ~3.3h) · 12.7% ≤30d (median 5.9d, avg 6.7d) · ~70% of "
     "30-day cancels happen in week 1.\n"
     "• Attach rate (orders with subscription ON): ~0.9% (Apr) → 45.5% (wk Jun 22).\n"
     "• Interval-1 share of created subscriptions: ~97%. Explicit schedule picks: every_90_days "
     "1,692 · every_30_days 1,182 · every_7_days 1,131 · every_14_days 329 (wk Jun 22).\n"
     "• June cancel/creation ratio by country: SV 43% · GT 42% · HN 41% · NI 39% · JM 37% · MX 31% "
     "· DO 27% · HT 26% · ET 25%.\n"
     "• Duplicate-subscription warnings: ~2.8k/wk and rising.\n"
     "• Weekly uniques (wk Jun 22): 67,526 subscribing users vs 13,229 cancelling users.\n"
     "• Daily toggle inflection: Jun 18–19 (off-taps ~5k → ~10–12k/day; on-taps ~1k/day)."),

    # ── 5. Recommendations ───────────────────────────────────────────────────
    ("h2", "5. Recommendations"),
    ("body",
     "1. Fix the same-day surprise: make subscription creation unmistakable at purchase "
     "(explicit copy + next-charge date on the confirmation screen). ~9% of subscribers cancel "
     "within 7 days, half of those within ~3 hours — these users never intended to subscribe.\n\n"
     "2. Reconsider the default frequency: 97% of auto-created subscriptions use interval 1, but "
     "when users choose explicitly they prefer every 90 / every 30 days. Testing a longer default "
     "(or a frequency picker at purchase) should cut first-renewal cancellations.\n\n"
     "3. Add a pre-renewal notification before the first charge (ties into DCS-4949 / DCS-4966): "
     "the 30-day cancel median of 5.9 days shows renewal is the discovery moment.\n\n"
     "4. Redesign the Edit Subscription screen: 77% of viewers cancel within the hour, in seconds. "
     "There is no meaningful save moment — add pause/skip/change-frequency options ahead of the "
     "cancel CTA, and a lightweight reason survey (~18k cancels/week gives instant signal).\n\n"
     "5. Target retention by corridor: Guatemala, El Salvador and Honduras churn at ~41–43% of "
     "creation volume vs Haiti/DR at ~26–27%. Corridor-specific offers or defaults could preserve "
     "the base where churn concentrates.\n\n"
     "6. Close the analytics gaps: GA-rollout events carry no A/B group tag (shows as \"(none)\"), "
     "and the default_state/new_state combination is internally inconsistent (large off→off "
     "volume). Add a server-side subscription_created event and re-verify toggle instrumentation.\n\n"
     "7. Watch duplicate subscriptions: warnings are rising (~2.8k/week) — with auto-ON on every "
     "purchase, users can stack subscriptions for the same recipient unintentionally."),

    # ── 4. Timing & net flow ─────────────────────────────────────────────────
    ("h2", "4. Timing of Cancellations & Net Flow"),
    ("body",
     "Two distinct canceller clusters emerge:\n\n"
     "• Same-day discoverers — 8.8% of subscription purchasers cancel within 7 days, and inside "
     "that window the median time-to-cancel is ~3.3 hours. These users discover the subscription "
     "almost immediately (confirmation screen, email/SMS receipt) and undo it.\n\n"
     "• First-renewal cancellers — over 30 days, 12.7% cancel with a median of 5.9 days, i.e. "
     "clustered just before/at the first interval-1 renewal. The renewal (or its reminder) is the "
     "second discovery moment.\n\n"
     "Roughly 70% of all 30-day cancellations happen in the first week. After the first renewal "
     "survives, cancellation risk drops sharply.\n\n"
     "Net flow: during the small-cohort phase (April), unique cancellers outnumbered unique "
     "subscribers up to ~6:1 (legacy + accumulated auto-subscriptions burning off). At full "
     "rollout the balance flipped decisively: wk Jun 22 saw 67.5k unique subscribing users vs "
     "13.2k cancelling users — strong net growth, with retention quality still to be proven over "
     "the next renewal cycles."),

    # ── 3. Cancellation behavior ─────────────────────────────────────────────
    ("h2", "3. Cancellation Behavior"),
    ("body",
     "The cancellation flow is frictionless to a fault. Of 103,860 users who opened the Edit "
     "Subscription screen (Mar–Jul), 77.8% tapped Cancel, 98.9% of those confirmed \"Yes\", and "
     "99.8% completed — an end-to-end 76.9% within one hour. Median transition times are 7 seconds "
     "from screen to Cancel and 3 seconds from Cancel to confirmation: users arrive decided; the "
     "confirmation dialog saves almost nobody (~1–4% tap \"No\").\n\n"
     "The Edit Subscription screen is functionally a cancellation screen — cancellation is its "
     "dominant outcome, not schedule edits or offer changes.\n\n"
     "Cancellations concentrate on interval-1 subscriptions (~95%, matching the creation mix). "
     "Interval-2/3 cancellations (~400–600/wk) form a stable base that pre-dates the rollout — "
     "the legacy, deliberately-created subscriptions churn at a much lower, steadier rate.\n\n"
     "By corridor, Guatemala leads cancellations (14.7k in June) despite Haiti leading creations "
     "(42.7k). June cancel-to-creation ratios: El Salvador 43%, Guatemala 42%, Honduras 41%, "
     "Nicaragua 39%, Jamaica 37%, Mexico 31%, Dominican Republic 27%, Haiti 26%, Ethiopia 25%. "
     "Platform split is stable: iOS ~63%, Android ~37% of cancellations — proportional to usage."),

    # ── 2. Subscription creation ─────────────────────────────────────────────
    ("h2", "2. Subscription Creation Under the Auto-ON Toggle"),
    ("body",
     "Subscription attach on completed orders exploded with the rollout: ~0.9% of instrumented "
     "orders in April → 5.9% (wk May 25) → 29.4% (wk Jun 15) → 45.5% (wk Jun 22). Weekly "
     "subscription-flagged orders peaked at ~90.5k.\n\n"
     "~97% of created subscriptions carry recurrent_interval = 1 — the toggle's default. Almost "
     "nobody adjusts the frequency at purchase. In contrast, when users engage the explicit "
     "schedule selector elsewhere in the flow, the most-chosen options are every 90 days and every "
     "30 days, ahead of every 7 days. The default frequency does not match expressed user "
     "preference — a likely driver of first-renewal cancellations.\n\n"
     "Destination mix follows the corridor base: Haiti (42.7k June subscription orders), Guatemala "
     "(35.3k), Dominican Republic (23.3k), Honduras (20.9k), Jamaica (12.4k), Mexico (10.3k), "
     "El Salvador (10.1k), Nigeria (8.5k).\n\n"
     "Duplicate-subscription warnings are climbing (~2.8k/week at full rollout) — auto-ON on every "
     "purchase makes accidental stacking for the same recipient increasingly common."),

    # ── 1. Toggle behavior ───────────────────────────────────────────────────
    ("h2", "1. Toggle On/Off Behavior"),
    ("body",
     "Daily data places the final wave on Jun 18–19: off-taps jumped from ~5k/day to ~10–12k/day "
     "and stabilized, while on-taps only rose from ~800 to ~1k/day. At full rollout, taps that end "
     "OFF outnumber taps that end ON by ~11:1, and 95.5% of interactions with a default-ON toggle "
     "switch it off. Users who interact are overwhelmingly opting out; the subscription growth "
     "comes from the silent majority who never touch the toggle.\n\n"
     "All interactions originate from a single component (component_name = \"mtu\") — the purchase "
     "flow toggle; there is no secondary surface.\n\n"
     "Experiment context: group B (default OFF) generated most interactions during the Mar–Apr A/B "
     "phase and faded to zero by late June; group A (default ON) stayed small. Since early May the "
     "GA rollout sends no test-group tag (values appear as \"(none)\"), so variant-level "
     "segmentation is impossible post-GA — an instrumentation gap worth closing.\n\n"
     "Data-quality flag (carried over from the rollout analysis): a large default_state=off & "
     "new_state=off volume (~109k in May) cannot arise from simple on/off alternation — likely "
     "double-firing or inconsistent state semantics across versions. Precise per-user opt-out "
     "rates need instrumentation review first."),

    # ── 0. Executive summary ─────────────────────────────────────────────────
    ("h2", "Executive Summary"),
    ("body",
     "• The auto-ON toggle multiplied subscription creation ~50x (attach rate ~1% → ~45% of "
     "orders), driven by user inaction: 95.5% of users who actually touch a default-ON toggle "
     "turn it off (~11:1 off:on at full rollout).\n"
     "• Cancellation behavior confirms low awareness: 8.8% of subscribers cancel within 7 days "
     "(median ~3.3 hours — same-day discovery), 12.7% within 30 days (median 5.9 days — the first "
     "interval-1 renewal). ~70% of 30-day cancels happen in week 1.\n"
     "• The cancel flow itself offers no resistance: 77% of Edit-Subscription-screen viewers "
     "cancel within the hour, deciding in seconds; the Yes/No confirmation saves ~1–4%.\n"
     "• The default frequency (interval 1) fits few users — explicit choosers prefer every 90/30 "
     "days — and duplicate-subscription warnings are rising.\n"
     "• Churn is corridor-skewed: GT/SV/HN cancel at ~41–43% of creation volume; HT/DO at ~26–27%.\n"
     "• Net flow is strongly positive at full rollout (67.5k subscribing vs 13.2k cancelling "
     "uniques, wk Jun 22), but first-renewal retention will decide the true LTV impact."),

    # ── Header ───────────────────────────────────────────────────────────────
    ("body",
     "Prepared: July 2, 2026 · Source: Amplitude, BR app Prod (project 650506) · Period: "
     "Mar 1 – Jul 2, 2026\n"
     "Deep-dive dashboard: https://app.amplitude.com/analytics/BOSS/dashboard/dsyei9ee · "
     "Companion rollout dashboard: https://app.amplitude.com/analytics/BOSS/dashboard/bx3h416b"),
    ("h1", "IMTU Subscription Cancellation & Toggle — Deep Dive Findings"),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3", "body": "NORMAL_TEXT"}


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)

    doc = docs.documents().create(
        body={"title": "IMTU Subscription Cancellation & Toggle — Deep Dive Findings"}
    ).execute()
    doc_id = doc["documentId"]

    requests = []
    for kind, text in BLOCKS:
        requests.append({"insertText": {"location": {"index": 1}, "text": text + "\n"}})
        requests.append({"updateParagraphStyle": {
            "range": {"startIndex": 1, "endIndex": 1 + len(text) + 1},
            "paragraphStyle": {"namedStyleType": STYLE_MAP[kind]},
            "fields": "namedStyleType",
        }})

    # Send in batches of 50 per project convention
    for i in range(0, len(requests), 50):
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests[i:i + 50]}
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print("DOC_URL=" + url)


if __name__ == "__main__":
    main()
