#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU Subscriptions - Core Logic Reference".

Single end-to-end reference for how IMTU subscriptions actually work:
lifecycle, notification triggers, branch decision logic, and the toggle.

Logic layer only - no UI/UX, no screens, no notification copy.
Every substantive claim carries a Jira key or Confluence page id. Where IDT has
no documented rule, the doc says so rather than inventing one.

Figure slots are marked in-line; PNGs are inserted by hand because Workspace
policy blocks the public link-sharing the Docs API needs to fetch an image.
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

TITLE = "IMTU Subscriptions — Core Logic Reference"

FIGURES = {
    "F1": ("imtu_sub_flow_1_lifecycle.png", "Figure 1 — Full subscription lifecycle"),
    "F2": ("imtu_sub_flow_2_toggle.png", "Figure 2 — Subscription toggle decision logic"),
    "F3": ("imtu_sub_flow_3_renewal.png", "Figure 3 — Renewal charge and payment failure"),
    "F4": ("imtu_sub_flow_4_cancel_modify.png", "Figure 4 — Cancellation and modification"),
    "F5": ("imtu_sub_flow_5_offer.png", "Figure 5 — Offer withdrawal"),
}

NOTIF_TABLE = [
    ["Trigger condition", "Timing", "Channel", "Status"],
    ["Subscription purchased successfully",
     "Immediately on purchase", "Push", "Shipped"],
    ["Renewal is approaching",
     "2 days before every charge date, all cadences", "Push", "Shipped · DCS-4983"],
    ["Customer edits the subscription",
     "Immediately on save", "Push", "Shipped"],
    ["Subscribed offer withdrawn, no substitute exists",
     "On the Kafka event; cancels at iteration date", "Push", "Shipped"],
    ["Subscribed offer withdrawn, substitute found",
     "On the Kafka event", "Push", "Shipped"],
    ["Subscription cancelled by the system",
     "On involuntary cancellation; reason embedded", "Push", "Shipped · DCS-2333"],
    ["Primary payment fails and a second method succeeds",
     "Within the same charge attempt", "SMS (EMMS)", "Shipped · DCS-2413"],
    ["Renewal charge fails and no method succeeds",
     "—", "NONE", "NOT BUILT · CRMC-3299 Backlog"],
]


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "cap": "NORMAL_TEXT"}


def build_requests(blocks):
    reqs, cur = [], 1
    for kind, text in blocks:
        if kind == "fig":
            fname, _ = FIGURES[text]
            line = f"◼  FIGURE SLOT — insert  {fname}\n"
            reqs += [
                {"insertText": {"location": {"index": cur}, "text": line}},
                {"updateParagraphStyle": {
                    "range": {"startIndex": cur, "endIndex": cur + len(line)},
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT",
                                       "alignment": "CENTER"},
                    "fields": "namedStyleType,alignment"}},
                {"updateTextStyle": {
                    "range": {"startIndex": cur, "endIndex": cur + len(line) - 1},
                    "textStyle": {"bold": True, "foregroundColor": {"color": {
                        "rgbColor": {"red": 0.72, "green": 0.45, "blue": 0.10}}}},
                    "fields": "bold,foregroundColor"}},
            ]
            cur += len(line)
            continue

        if kind == "table":
            line = "[[TABLE]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += len(line)
            continue

        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        para = {"namedStyleType": STYLE_MAP[kind]}
        fields = "namedStyleType"
        if kind == "cap":
            para["alignment"] = "CENTER"
            fields += ",alignment"
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(line)},
            "paragraphStyle": para, "fields": fields}})
        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind == "cap":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(text)},
                "textStyle": {"italic": True,
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}})
        if kind in ("b", "p") and "  —  " in text:
            lead = text.split("  —  ")[0]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(lead)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        cur += len(line)
    return reqs


def batched(docs, doc_id, reqs, size=40):
    for i in range(0, len(reqs), size):
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": reqs[i:i + size]}).execute()
        time.sleep(0.25)


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in el["paragraph"]["elements"])


def insert_table(docs, doc_id, data):
    """Replace the [[TABLE]] placeholder with a real Docs table."""
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == "[[TABLE]]":
            idx = el["startIndex"]
            plen = len(para_text(el))
            break
    if idx is None:
        print("  ! table placeholder not found")
        return False

    rows, cols = len(data), len(data[0])
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx,
                                          "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx}, "rows": rows,
                         "columns": cols}},
    ]}).execute()
    time.sleep(1.0)

    # Locate the table and collect every cell's insert position.
    doc = docs.documents().get(documentId=doc_id).execute()
    table_el = None
    for el in doc["body"]["content"]:
        if "table" in el and el["startIndex"] >= idx - 2:
            table_el = el
            break
    if table_el is None:
        print("  ! table not found after insert")
        return False

    cells = []
    for r, row in enumerate(table_el["table"]["tableRows"]):
        for c, cell in enumerate(row["tableCells"]):
            cells.append((cell["content"][0]["startIndex"], r, c))

    reqs = []
    for start, r, c in sorted(cells, reverse=True):        # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        elif c == 3 and ("NOT BUILT" in txt):
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": 0.70, "green": 0.15, "blue": 0.15}}}},
                "fields": "bold,foregroundColor"}})
    batched(docs, doc_id, reqs, size=30)
    return True


# ==================================================================== TEXT ====
def blocks():
    b = [
        ("h1", TITLE),
        ("p", "This document describes the logic layer only — the conditions and "
              "branches that govern IMTU subscriptions. It deliberately excludes "
              "UI/UX, screen designs and notification copy, so that it stays "
              "accurate when the interface changes."),
        ("p", "Scope is IMTU (International Mobile Top-Up) subscriptions. Calling "
              "Plans, BOSS Complete and SingIt run on a different platform with "
              "different rules — see section 2.1, which is the single most common "
              "source of confusion on this topic."),
        ("p", "Compiled 11 August 2026 from Jira and Confluence. Every rule is "
              "cited. Where IDT has no documented rule, this document says so "
              "explicitly rather than describing generic industry behaviour."),

        # ------------------------------------------------------------------ 1
        ("h2", "1. The model in brief"),
        ("p", "An IMTU subscription is a recurring top-up of one offer to one "
              "recipient. It is created inside an ordinary purchase — the customer "
              "buys a top-up with the subscription toggle on. The first charge is "
              "taken immediately on the purchase date. A timer is then scheduled, "
              "and the same top-up is re-purchased every cycle until someone stops "
              "it."),
        ("b", "No trial  —  IMTU has no trial, no grace period and no "
              "pending-activation state. The subscription is live from the moment "
              "the first charge succeeds."),
        ("b", "Cadences  —  7, 14, 30 or 90 days, defaulted from the offer's "
              "validity period."),
        ("b", "Payment  —  BOSS Cash wallet is attempted first, then a card on the "
              "customer's profile."),
        ("b", "States  —  active or cancelled. There is no past-due, suspended or "
              "paused state."),
        ("b", "Failure  —  a failed renewal does not cancel the subscription, does "
              "not notify the customer, and is not retried on a schedule. It is "
              "simply attempted again at the next cycle."),
        ("p", "That last point is the most frequently misunderstood behaviour in "
              "the product, and it is covered in full in section 5."),

        # ------------------------------------------------------------------ 2
        ("h2", "2. System landscape"),
        ("p", "IMTU subscriptions are scheduled by the Timers API — rows in a "
              "Postgres timers table (type mtu-v2) in the poppers database, with a "
              "companion reminder-mtu-v2 row for the renewal reminder. Each "
              "subscription carries repeat_info: timer_id, reminder_timer_id, "
              "timer_status, launch_at, recurrent_unit, recurrent_interval, "
              "reminder_unit and reminder_interval, where launch_at is epoch "
              "milliseconds. Offers and fulfilment live in K2; payment "
              "authorisation goes through IDT Pay. (DCS-2145, DCS-2018, DCS-3541)"),
        ("h3", "2.1 Subly is not IMTU — read this before citing it"),
        ("p", "Searching Jira for subscription retry logic surfaces Subly, which "
              "has a clean state machine — pending, active, past-due, ended — plus "
              "an EndReason enum and a configurable payment_retry_schedule. It is "
              "tempting to treat that as the answer. It is not IMTU."),
        ("b", "Subly is the DTC platform for BOSS Complete and SingIt.  —  "
              "DTCBE-2686, which defines that state machine, is still To Do, and "
              "its out-of-scope list explicitly names \"MTU subscription payment "
              "ownership\"."),
        ("b", "A migration is under way, but a narrow one.  —  Subscription "
              "storage and event triggering are moving from the Timers API to "
              "Subly, one subscription at a time as each reaches its charge date. "
              "DCS retains payment processing, purchase execution, fulfilment "
              "through K2, and notification delivery. Payment retries are named "
              "explicitly as not migrating. (Confluence 5850923041)"),
        ("p", "So: Subly will schedule IMTU subscriptions, but it will not govern "
              "what happens when an IMTU payment fails. Anything quoted from "
              "DTCBE-2686 about past-due states or retry ladders describes BOSS "
              "Complete and SingIt, not this product."),

        # ------------------------------------------------------------------ 3
        ("h2", "3. Lifecycle"),
        ("fig", "F1"),
        ("cap", FIGURES["F1"][1]),
        ("b", "Creation  —  a subscription is created inside a normal top-up "
              "purchase with the toggle on. A separate direct-subscription entry "
              "point also exists for marketing flows. (Confluence 4525031473)"),
        ("b", "Initial charge  —  taken immediately on the purchase date. Worked "
              "example from the December 2025 incident record: a customer "
              "subscribing monthly on 10 November is charged that day, with the "
              "second iteration on 10 December."),
        ("b", "Activation  —  there is no separate activation step. A successful "
              "first charge is what makes the subscription live."),
        ("b", "Scheduling  —  launch_at is jittered by up to 1440 minutes. "
              "DCS-3541 introduced this after rounded timers fired simultaneously "
              "and triggered payment-processor rate limits; 15,580 rows were "
              "adjusted. No fixed renewal hour or timezone is documented anywhere "
              "— it would have to be read from the code or database."),
        ("b", "Duplicate definition  —  same user, same recipient, same offer. "
              "This definition drives both the toggle default and the duplicate "
              "warning. (Confluence 5552079089, DCS-3815)"),

        # ------------------------------------------------------------------ 4
        ("h2", "4. The subscription toggle"),
        ("p", "The toggle determines whether a purchase becomes a subscription. "
              "Its default state is computed by the backend when the Offer "
              "Confirmation page opens, in strict priority order."),
        ("fig", "F2"),
        ("cap", FIGURES["F2"][1]),
        ("h3", "4.1 Default-state priority"),
        ("b", "If a duplicate subscription exists  —  OFF, reason duplicate"),
        ("b", "Else if the customer has 3 or more active subscriptions  —  OFF, "
              "reason max_subscriptions"),
        ("b", "Else if the customer is in the experiment control group  —  OFF, "
              "reason experiment"),
        ("b", "Otherwise  —  ON, reason default"),
        ("p", "This is a soft restriction throughout. A default of OFF never "
              "prevents the customer from switching the toggle on, and the "
              "duplicate warning never blocks a purchase. (Confluence 5552079089)"),
        ("h3", "4.2 Default frequency"),
        ("p", "Frequency is defaulted from the offer's validity period. The "
              "options presented are 7, 14, 30 and 90 days."),
        ("b", "Validity 1–7 days  —  7 days"),
        ("b", "Validity 8–14 days  —  14 days"),
        ("b", "Validity 15–30 days  —  30 days"),
        ("b", "Validity 31+ days  —  90 days"),
        ("b", "Top-up products with no validity period  —  30 days"),
        ("b", "Validity NULL, 0 or missing  —  30 days fallback"),
        ("p", "Selecting a frequency automatically switches the toggle on. If the "
              "customer then switches the toggle off, the chosen frequency is "
              "preserved and restored if they switch it back on."),
        ("h3", "4.3 Upsell popup"),
        ("p", "Shown when the customer taps Buy with the toggle OFF and every "
              "eligibility check passes — fewer than 3 active subscriptions and no "
              "duplicate. It is deliberately not shown when the toggle is off "
              "because of an eligibility rule, since the system has already "
              "determined this customer should not subscribe by default. It is "
              "also suppressed if the customer already saw the Featured Upsell "
              "Card."),
        ("h3", "4.4 A/B experiment on the default"),
        ("p", "Live from the March 2026 release across both the Money App and the "
              "Calling App, targeting 25,000 users per app. Treatment group A "
              "defaults the toggle ON; control group B defaults it OFF. Assignment "
              "is persistent per customer, and the eligibility rules in 4.1 "
              "override the experiment at all times."),
        ("b", "Toggle ON group  —  50.1% complete a purchase with a subscription"),
        ("b", "Toggle OFF group  —  15.1% interact with the toggle at all"),
        ("p", "Open question, recorded in the spec and still unresolved: when the "
              "test concludes, which group becomes the permanent default. Related "
              "configuration flags are "
              "mtu_subscription_toggle_interactions_to_disable (default 3) and "
              "mtu_subscription_toggle_reset_days (default 30). "
              "(Confluence 6091505685)"),

        # ------------------------------------------------------------------ 5
        ("h2", "5. Renewal, payment and retries"),
        ("fig", "F3"),
        ("cap", FIGURES["F3"][1]),
        ("h3", "5.1 Charge sequence"),
        ("b", "Wallet first  —  the BOSS Cash balance is attempted before any "
              "card. If it cannot cover the full amount, or errors, the charge "
              "falls through to a card. (DCS-2905)"),
        ("b", "Card on profile  —  the card is not pinned to the subscription. "
              "DTCBE-582 changed this in May 2024 so the card present on the user "
              "profile is used. (Confluence 3881173002)"),
        ("b", "In-flight fallback  —  if the primary method fails and another is "
              "on file, it is charged immediately, within the same attempt. "
              "Subsequent cycles revert to the original card. If the second "
              "attempt also fails, DCS-2413 states the behaviour plainly: \"we do "
              "nothing\". DCS-5153 fixed the case where the backup was not being "
              "selected at all."),
        ("h3", "5.2 The CVV and fraud gate"),
        ("p", "Subscriptions carry a cvv_verified flag in timer metadata "
              "(DCS-3295). Where it is true and fraud bypass applies, the recurring "
              "charge proceeds without a fraud check; where false, the charge is "
              "fraud-checked and can fail authorisation. Fraud Check for "
              "Subscriptions went live on 24 November 2025 with an important "
              "consequence: the same card used at setup must be used for recurring "
              "charges, because if the card changes the subscription fails — no new "
              "CVV flow exists. (Confluence 5021925393)"),
        ("h3", "5.3 Retries — what actually happens"),
        ("p", "IMTU has no dunning ladder. There is no retry schedule, no attempt "
              "counter, no exhaustion condition and no cooldown period. After a "
              "failed cycle the subscription remains active and is attempted again "
              "at the next scheduled cycle, indefinitely."),
        ("p", "Because this is the question that prompted the document, here is "
              "the evidence for the absence, rather than an assertion:"),
        ("b", "DCS-1667  —  would have introduced second-card fallback plus \"3 "
              "times total before informing users that the subscription will be "
              "cancelled\". Closed Won't Fix, noted as belonging to a future "
              "subscription service."),
        ("b", "DCS-1200  —  the only written retry ladder anywhere (retry at 5, 10 "
              "and 20 days, cancel on the 4th failure) is scoped to Subscriber "
              "Manager on the Calling side. It is not IMTU. DCS-1574 adds that "
              "these rules still required review, with the live numbers held in a "
              "Google Sheet outside Jira."),
        ("b", "DCS-3407  —  the one interval that did ship, and it is throttling "
              "rather than dunning: when IDT Pay returns Retry because of a "
              "processor rate limit, callers must wait at least 5 to 10 minutes "
              "before re-attempting."),
        ("b", "DCS-4944  —  Subly may invoke a renewal up to 10 times, so an "
              "idempotency guard prevents double charging. Again a safety "
              "mechanism, not a retry ladder."),
        ("h3", "5.4 Why a failure never cancels"),
        ("p", "This is deliberate, and the history matters. DTCBE-444 introduced "
              "auto-cancellation on missing card and missing offer, and roughly "
              "30,000 subscriptions were lost — 13,377 missing card, 10,923 offer "
              "not found, 2,012 account locked, 984 CVV. After hot fix DTCBE-552, "
              "DTCBE-623 removed cancellation for all payment scenarios and was "
              "deployed on 22 May 2024. (Confluence 3881173002)"),
        ("p", "The trade-off is that subscriptions now fail silently and "
              "indefinitely instead of ending. Section 6 quantifies that."),

        # ------------------------------------------------------------------ 6
        ("h2", "6. Failure taxonomy"),
        ("h3", "6.1 Production distribution"),
        ("p", "From the April 2026 analysis of 273,258 active subscriptions, of "
              "which 77,650 — 28.4% — were in a failing state "
              "(Confluence 5854003362):"),
        ("b", "Missing or removed payment instrument  —  24,794 (31.9%). Requires "
              "customer action. 43% of these had a working card that was later "
              "removed, median 154 days."),
        ("b", "Generic IDTPay - failed  —  21,383 (27.5%). No reason code at all; "
              "an explicit observability gap."),
        ("b", "Insufficient funds  —  14,645 (18.9%). Transient in principle, but "
              "28% of previously-working cases have been failing for over 90 days."),
        ("p", "Of the 36,980 subscriptions classed transient, 9,562 have been "
              "failing for more than 90 days. Roughly half of all failing "
              "subscriptions never completed a single successful charge, and 26,005 "
              "customers — 17% of the subscriber base — have no working "
              "subscription at all."),
        ("h3", "6.2 IDT Pay result codes"),
        ("p", "success, limit_exceeded, failed_already_refunded, "
              "failed_card_declined, failed, failed_card_expired, failed_no_credit, "
              "failed_server_error, failed_fraud, unknown_fraud_status, "
              "failed_lost_or_stolen_cc, failed_card_restricted, "
              "failed_invalid_card_info, failed_invalid_card_number, "
              "duplicate_request, cvv_required, 3ds_pending, 3ds_required, "
              "3ds_failed."),
        ("p", "DCS-3539 proposed splitting these into retryable and terminal but "
              "closed without ratifying it, deferring to IDTPAY-3912. Its opening "
              "line still describes today's behaviour: \"Currently we retry an IDT "
              "Pay authorization for any error response, even when the card has "
              "insufficient funds.\" There is therefore no agreed definition of a "
              "hard decline for IMTU."),
        ("h3", "6.3 Queued is not a failure"),
        ("p", "Queued means accepted but not yet fulfilled. It is a frontend "
              "pseudo-status shown when the backend does not respond within roughly "
              "15 seconds, and queued transactions require all_transactions=true to "
              "be returned. (Confluence 5926354995, DCS-478, DCS-2070)"),

        # ------------------------------------------------------------------ 7
        ("h2", "7. Cancellation and modification"),
        ("fig", "F4"),
        ("cap", FIGURES["F4"][1]),
        ("h3", "7.1 Customer-initiated cancellation"),
        ("p", "Two entry points: IMTU Home, then My Top-Up Activity, Edit, Cancel, "
              "Confirm; or Calling Home, Funding page, Subscriptions, Edit, Cancel. "
              "Cancellation takes effect immediately. There is no retention offer, "
              "no exit survey, no cancellation-reason capture and no cooldown "
              "before the customer can resubscribe."),
        ("h3", "7.2 Modification"),
        ("p", "Offer, frequency and payment method can be changed. Editing was "
              "historically implemented as cancel-and-recreate; DCS-3521 migrated "
              "it to a dedicated PUT /store/v1/subscriptions/{timerId} endpoint, "
              "and DCS-5184 tracks removing the legacy path. There is no proration "
              "— IMTU charges per cycle, not per term, so a change simply applies "
              "from the next cycle."),
        ("p", "One gap worth knowing: changing the payment method on an existing "
              "subscription is not built. DCS-4461 and DCS-4463 are open and "
              "blocked on the fraud team, because no immediate transaction occurs "
              "at the moment of the change and CVV cannot be stored for later use "
              "under PCI."),
        ("h3", "7.3 System-initiated cancellation"),
        ("p", "Payment failure is not on this list. The documented involuntary "
              "cancellation reasons are (DCS-2018, DCS-2145, Confluence 4659314778):"),
        ("b", "User phone number disconnected  —  invalid_msisdn; hard delete, no "
              "recovery"),
        ("b", "Recipient not prepaid  —  msisdn_not_prepaid"),
        ("b", "User profile locked  —  account_locked; under 3 months no action, "
              "over 3 months cancel"),
        ("b", "User profile deleted  —  account_deleted"),
        ("b", "Offer no longer available  —  missing_offer, where no substitute "
              "exists"),

        # ------------------------------------------------------------------ 8
        ("h2", "8. Offer withdrawal and substitution"),
        ("fig", "F5"),
        ("cap", FIGURES["F5"][1]),
        ("p", "An automatic flow identifies subscriptions whose offer has been "
              "discontinued in K2. Each discontinued offer either has a substitute, "
              "in which case active subscriptions switch to it automatically at the "
              "Kafka event, or has none, in which case they are cancelled — on the "
              "iteration date, not at the Kafka event. Whether the original "
              "frequency survives a substitution is still under PM research "
              "(DCS-4204), currently leaning toward preserving it. "
              "(Confluence 5327421441)"),
        ("h3", "8.1 The December 2025 incident"),
        ("p", "The cancellation flow did not take country into account, so "
              "withdrawing an offer in one country cancelled that offer's "
              "subscriptions in every country. On 8 December 2025, 29,474 "
              "subscriptions across 17,464 customers were cancelled and the feature "
              "was disabled. 15,723 subscriptions were reinstated with their "
              "original dates and 11,662 were recreated with a new start date. "
              "6,117 belonged to customers with no card on file and could only "
              "resume once a card was added. 6,603 customers received an SMS. It "
              "remains the clearest worked example of how this branch can go "
              "wrong, and why country scoping matters here."),

        # ------------------------------------------------------------------ 9
        ("h2", "9. Customer-facing notification triggers"),
        ("p", "Conditions only — copy is out of scope by design. This is the table "
              "to open when someone asks when exactly we message a customer about "
              "something. Source: Confluence 6129057864, with the backend strings "
              "in 5145493539."),
        ("table", ""),
        ("p", "All push notifications carry the title \"BOSS Revolution\" and deep "
              "link to the IMTU home page."),
        ("p", "Two channels exist beyond push: SMS via EMMS, used for the "
              "alternate-payment message, and SMS via Fireball, used for incident "
              "communications such as the December 2025 reinstatement."),
        ("p", "Braze (Appboy) carries campaign and promotional messaging rather "
              "than these lifecycle triggers. Campaign-level conditions are "
              "configured inside Braze and are not documented in Jira or "
              "Confluence, so a complete picture including marketing sends has to "
              "come from the CRM team."),
        ("p", "The last row is the important one. A customer whose renewal fails — "
              "the 28.4% described in section 6 — receives nothing at all. "
              "CRMC-3299 was raised for exactly this and has been in Backlog since "
              "2024."),

        # ----------------------------------------------------------------- 10
        ("h2", "10. Known gaps and open questions"),
        ("p", "These are gaps in the documented logic, not in this document. Each "
              "is a decision someone still owns."),
        ("b", "No payment-failure notification  —  the largest gap in the "
              "notification set, and the one most directly linked to recoverable "
              "revenue. CRMC-3299, Backlog since 2024."),
        ("b", "No retry policy for IMTU  —  DCS-1667 closed Won't Fix; DCS-1200's "
              "ladder belongs to Calling. Nothing defines how many attempts IMTU "
              "should make, or what exhausted would mean."),
        ("b", "Retryable versus terminal errors never ratified  —  DCS-3539 closed "
              "deferring to IDTPAY-3912. Today an authorisation is retried on any "
              "error response, including insufficient funds."),
        ("b", "Fallback method selection order unspecified  —  DCS-5121 records "
              "the open question: \"can we for sure say that the first card in the "
              "list will be next to be charged?\" The fallback is selected "
              "silently."),
        ("b", "Renewal hour and timezone undocumented  —  launch_at is epoch "
              "milliseconds with up to 1440 minutes of jitter. No cron hour or "
              "timezone is written down."),
        ("b", "Payment-method editing not built  —  DCS-4461 and DCS-4463 blocked "
              "on fraud-team guidance."),
        ("b", "Observability gap on failures  —  27.5% of failing subscriptions "
              "carry a generic error with no reason code, which limits any "
              "remediation effort."),
        ("b", "A/B conclusion pending  —  the permanent toggle default has not "
              "been decided."),

        # ----------------------------------------------------------------- 11
        ("h2", "11. Sources"),
        ("p", "Confluence: 5552079089 Subscription Toggle and Frequency Changes · "
              "6129057864 MTU subscriptions - Push notifications · 5854003362 "
              "Subscriptions Last Transaction Status Analysis · 5327421441 MTU "
              "Subscription Cancellation (Incident) · 3881173002 Subscriptions "
              "issue · 5850923041 What is being migrated to Subly · 5740200101 "
              "Migration to Subly · 5021925393 Fraud Check for Subscriptions · "
              "4659314778 Subscription cancellation and substitution · 6091505685 "
              "Feature Flags · 5926354995 IMTU in WA · 4525031473 Direct "
              "subscription · 5145493539 Push Notification BE info."),
        ("p", "Jira: DCS-2413 · DCS-2905 · DCS-5153 · DCS-1133 · DCS-5121 · "
              "DCS-1667 · DCS-1200 · DCS-1574 · DCS-3407 · DCS-3539 · DCS-3541 · "
              "DCS-4944 · DCS-3295 · DCS-4461 · DCS-4463 · DCS-4983 · DCS-2333 · "
              "DCS-2018 · DCS-2145 · DCS-3521 · DCS-5184 · DCS-4204 · DCS-4317 · "
              "DCS-3815 · DCS-4514 · DCS-478 · DCS-2070 · DTCBE-2686 · DTCBE-2696 · "
              "DTCBE-623 · DTCBE-582 · CRMC-3299 · IDTPAY-3912."),
        ("p", "Figures reflect the April 2026 subscription analysis. The A/B "
              "results are early data from late March 2026 and should be refreshed "
              "before being quoted externally."),
    ]
    return b


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)

    print("Creating document...")
    doc_id = docs.documents().create(body={"title": TITLE}).execute()["documentId"]
    batched(docs, doc_id, build_requests(blocks()))

    print("Inserting notification table...")
    ok = insert_table(docs, doc_id, NOTIF_TABLE)
    print(f"  table inserted: {ok}")

    print("\nDONE")
    print(f"https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
