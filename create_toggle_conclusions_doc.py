"""
Creates a Google Doc: "IMTU Subscription Toggle — Rollout Behavior Analysis & Conclusions"
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

    # ── 5. Appendix ──────────────────────────────────────────────────────────
    ("h2", "5. Appendix — Weekly Data Highlights & Links"),
    ("body",
     "Toggle taps ending OFF (weekly): Mar 23: 11.2k · Apr 27: 23.2k · May 25: 33.9k · "
     "Jun 15: 59.6k · Jun 22: 73.1k\n"
     "Toggle taps ending ON (weekly): Mar 23: 1.8k · Apr 27: 4.9k · May 25: 5.5k · Jun 22: 6.5k\n"
     "Orders with subscription ON (weekly): Apr avg ~1.8k · May 25: 11.7k · Jun 15: 59.7k · Jun 22: 90.5k\n"
     "Successful cancellations (weekly): Mar 2: 1.1k · Apr 27: 11.9k · Jun 8: 11.4k · Jun 22: 18.0k\n"
     "Cancel confirmation rate: ~97% Yes · Cancel completion: ~93–96% of cancel-button taps\n"
     "Purchase→cancel funnel (Mar–Jul): 153.4k subscription purchases → 19.4k cancelled within 30 days "
     "(12.7%), median 5.9 days, average 6.7 days\n\n"
     "Amplitude dashboard: https://app.amplitude.com/analytics/BOSS/dashboard/bx3h416b\n"
     "Charts (personal space, unpublished):\n"
     "• Toggle Taps by New State — https://app.amplitude.com/analytics/BOSS/chart/c4oknene\n"
     "• Toggle Taps by Default State — https://app.amplitude.com/analytics/BOSS/chart/5pxe8mfn\n"
     "• Toggle Unique Users by Platform — https://app.amplitude.com/analytics/BOSS/chart/0r12epg1\n"
     "• Orders by is_subscription — https://app.amplitude.com/analytics/BOSS/chart/vkxkhnve\n"
     "• Cancellation Flow — https://app.amplitude.com/analytics/BOSS/chart/kswuhn5y\n"
     "• Cancellations by Platform — https://app.amplitude.com/analytics/BOSS/chart/l7gtteha\n"
     "• Purchase → Cancellation Funnel — https://app.amplitude.com/analytics/BOSS/chart/gb7jgqqz"),

    # ── 4. Recommendations ───────────────────────────────────────────────────
    ("h2", "4. Recommendations"),
    ("body",
     "1. Make the subscription creation explicit at purchase — clear copy near the CTA showing "
     "frequency and next charge date — to convert \"silent\" subscribers into aware ones and reduce "
     "first-renewal shock.\n\n"
     "2. Send a pre-renewal notification before the first charge. Users who would cancel anyway will "
     "do so before the charge, reducing refunds and complaints. (Pairs with the notification-service "
     "work in DCS-4949 / DCS-4966.)\n\n"
     "3. Add a cancellation-reason survey in the cancel flow — with ~18k cancels/week, even a short "
     "survey would quickly explain motivations.\n\n"
     "4. Fix the toggle instrumentation (see 2.6) so opt-out rates can be measured precisely, and "
     "consider a dedicated server-side \"subscription created\" event.\n\n"
     "5. Track net retained subscriptions per rollout cohort (created – cancelled, by week of "
     "creation) to quantify true incremental subscription growth and revenue."),

    # ── 3. Conclusions ───────────────────────────────────────────────────────
    ("h2", "3. Conclusions"),
    ("body",
     "1. The auto-ON toggle is highly effective at creating subscriptions — attach rate went from "
     "~1% to ~45% of orders — but a large share of that lift comes from user inaction, not intent.\n\n"
     "2. Users who notice the toggle mostly reject it: 95.5% of interactions with a default-ON "
     "toggle turn it off.\n\n"
     "3. A meaningful minority of \"silent\" subscribers cancel soon after: 12.7% within 30 days, "
     "typically ~6 days in (right around the first weekly renewal). Cancel-at-first-renewal plus "
     "firm confirmation behavior (~97% confirm) indicates surprise subscriptions rather than "
     "changed minds.\n\n"
     "4. Net-net the feature grows the subscription base substantially (~18k cancellations/week vs "
     "~90k subscription-flagged orders/week at full rollout), but the opt-out and early-cancel "
     "signals carry churn, support-contact, and trust/CSAT risk, plus potential app-store/compliance "
     "exposure around negative-option billing.\n\n"
     "5. The true measure of the feature is renewal-cohort retention: how many auto-created "
     "subscriptions survive the first 2–3 renewal cycles and generate incremental LTV."),

    # ── 2.6 Data quality ─────────────────────────────────────────────────────
    ("h3", "2.6 Data-quality observation (needs BE/QA follow-up)"),
    ("body",
     "A large volume of toggle events report default_state=off AND new_state=off (~109k in May) — "
     "more than can be explained by users flipping on→off in sequence. This suggests either (a) the "
     "event double-fires, (b) new_state/default_state semantics differ between platforms or app "
     "versions, or (c) the toggle is pre-set ON by the app while default_state still reports \"off\". "
     "Recommend an instrumentation review before using these properties for precise opt-out-rate "
     "calculations."),

    # ── 2.5 Platform ─────────────────────────────────────────────────────────
    ("h3", "2.5 Platform split: iOS leads, proportionally"),
    ("body",
     "iOS accounts for ~63–64% of both toggle interactions and cancellations; Android ~36–37%. "
     "Behavior is consistent across platforms — no platform-specific anomaly."),

    # ── 2.4 Time to cancel ───────────────────────────────────────────────────
    ("h3", "2.4 Time to cancel: users cancel right around the first weekly renewal"),
    ("body",
     "Of users who complete a subscription purchase, 12.7% cancel within 30 days. Median time to "
     "cancel is ~5.9 days; average ~6.7 days. The median sitting just under 7 days strongly suggests "
     "users cancel when the first weekly renewal (or its reminder/charge) makes the subscription "
     "visible — many users likely did not realize a subscription was created at purchase."),

    # ── 2.3 Cancellations ────────────────────────────────────────────────────
    ("h3", "2.3 Cancellations scaled with the rollout (~16x)"),
    ("body",
     "Weekly successful cancellations grew from ~1.1k (early March baseline) to ~18.0k in the week "
     "of Jun 22 (~16x). Volume began climbing from late March — as soon as the first 50k-user wave "
     "started accumulating auto-created subscriptions — and stepped up with every wave.\n\n"
     "Once users open the cancellation dialog they follow through: ~97% tap \"Yes\" and only ~1–4% "
     "tap \"No\". The confirmation step does not save subscriptions — cancellation intent is firm.\n\n"
     "Unique cancelling users in the week of Jun 22: ~13.2k (iOS ~63%, Android ~37%)."),

    # ── 2.2 Attach rate ──────────────────────────────────────────────────────
    ("h3", "2.2 Despite opt-outs, subscription attach on orders increased dramatically"),
    ("body",
     "Share of completed top-up orders with is_subscription = true:\n"
     "• Pre-rollout baseline (April): ~0.9% of instrumented orders\n"
     "• Week of May 25 (1M users): ~5.9%\n"
     "• Week of Jun 15: ~29.4%\n"
     "• Week of Jun 22 (full rollout): ~45.5%\n\n"
     "This is roughly a 50x increase in subscription-flagged orders vs the manual-toggle baseline. "
     "The auto-ON default is extremely effective at converting purchases into subscriptions — mostly "
     "via user inaction rather than explicit choice."),

    # ── 2.1 Toggle interaction ───────────────────────────────────────────────
    ("h3", "2.1 Toggle interaction: users overwhelmingly opt OUT of the default-ON toggle"),
    ("body",
     "After the full rollout (June), taps on default-ON toggles reached ~152k in the month, and "
     "95.5% of them switched the toggle OFF (151.8k off vs 7.1k re-enabled on). In the week of "
     "Jun 22 alone there were ~73.1k off-taps vs ~6.5k on-taps (≈11:1).\n\n"
     "Interpretation: when users notice the pre-selected subscription, the dominant deliberate action "
     "is to opt out at purchase time. The toggle's net effect therefore comes from users who do NOT "
     "interact with it."),

    ("h2", "2. Key Findings"),

    # ── 1. Context ───────────────────────────────────────────────────────────
    ("h2", "1. Context"),
    ("body",
     "The BOSS Revolution app introduced an automatic subscription toggle (default ON) in the IMTU "
     "purchase flow. The feature was rolled out progressively (approximate dates, per platform):\n"
     "• Mar 19 — 25k iOS + 25k Android\n"
     "• May 11 — 100k iOS + 100k Android (right after Mother's Day)\n"
     "• May 18 — 200k + 200k\n"
     "• May 25 — 500k + 500k\n"
     "• Jun 1 — 1M + 1M\n"
     "• Jun 20 — 100% of users\n\n"
     "Analysis based on: toggle interactions (MTUSubscriptionToggleTap, properties default_state / "
     "new_state), subscription attach on orders (MTUOrderCompleteBtn, property is_subscription), and "
     "the cancellation flow (MTUEditSubscriptionCancelBtn → Yes/No → CancelSuccess)."),

    # ── Header ───────────────────────────────────────────────────────────────
    ("body",
     "Prepared: July 2, 2026 · Data source: Amplitude, BR app Prod (project 650506) · "
     "Period analyzed: Mar 1 – Jul 2, 2026\n"
     "Amplitude dashboard: https://app.amplitude.com/analytics/BOSS/dashboard/bx3h416b"),
    ("h1", "IMTU Subscription Toggle — Rollout Behavior Analysis & Conclusions"),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3", "body": "NORMAL_TEXT"}


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)

    doc = docs.documents().create(
        body={"title": "IMTU Subscription Toggle — Rollout Behavior Analysis & Conclusions"}
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
