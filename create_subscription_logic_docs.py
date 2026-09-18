#!/usr/bin/env python3
"""
Creates two Google Docs describing IMTU subscription logic:

  1. "IMTU Subscriptions - Logic Summary"      (concise, shareable)
  2. "IMTU Subscription Logic - Reference"     (full detail)

Flowchart PNGs are uploaded to Drive, made link-readable only long enough for
the Docs API to fetch them, then locked back down (Docs stores its own copy).

Every substantive claim carries a Jira key or Confluence page id. Where IDT has
no documented rule, the docs say so explicitly rather than inventing one.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

IMAGES = {
    "F1": "imtu_sub_flow_1_lifecycle.png",
    "F2": "imtu_sub_flow_2_toggle.png",
    "F3": "imtu_sub_flow_3_renewal.png",
    "F4": "imtu_sub_flow_4_cancel_modify.png",
    "F5": "imtu_sub_flow_5_offer.png",
}
IMG_WIDTH_PT = 460.0


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
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


# ------------------------------------------------------------ doc builder ----
STYLE_MAP = {
    "h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
    "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "cap": "NORMAL_TEXT",
    "img": None,
}


def build_requests(blocks):
    """Forward-order construction; cursor tracks the running insert index."""
    reqs, cur = [], 1
    for kind, text in blocks:
        if kind == "img":
            # Workspace policy blocks public link-sharing, and the Docs API can
            # only fetch images from a public URI - so the figure slot is marked
            # here and the PNG is dropped in by hand.
            line = f"◼  FIGURE SLOT — insert  {IMAGES[text]}\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            reqs.append({"updateParagraphStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT",
                                   "alignment": "CENTER"},
                "fields": "namedStyleType,alignment"}})
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(line) - 1},
                "textStyle": {"bold": True,
                              "foregroundColor": {"color": {"rgbColor": {
                                  "red": 0.72, "green": 0.45, "blue": 0.10}}}},
                "fields": "bold,foregroundColor"}})
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

        # bold the "Label —" lead-in on bullet/labelled lines
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


def place_images(docs, doc_id, uri_map):
    """Replace [[F1]] placeholders with inline images, last-to-first."""
    doc = docs.documents().get(documentId=doc_id).execute()
    hits = []
    for el in doc["body"]["content"]:
        t = para_text(el).strip()
        if t.startswith("[[") and t.endswith("]]"):
            key = t[2:-2]
            if key in uri_map:
                hits.append((el["startIndex"], len(para_text(el)) - 1, key))
    ok = 0
    for start, length, key in sorted(hits, reverse=True):
        try:
            docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
                {"deleteContentRange": {"range": {"startIndex": start,
                                                  "endIndex": start + length}}},
                {"insertInlineImage": {
                    "location": {"index": start}, "uri": uri_map[key],
                    "objectSize": {"width": {"magnitude": IMG_WIDTH_PT,
                                             "unit": "PT"}}}},
            ]}).execute()
            ok += 1
            time.sleep(0.4)
        except Exception as exc:                                # noqa: BLE001
            print(f"  ! image {key} failed: {str(exc)[:140]}")
    return ok, len(hits)


def upload_images(drive):
    """Upload PNGs, grant temporary link-read, return {key: uri, key: file_id}."""
    uris, ids = {}, {}
    for key, fname in IMAGES.items():
        path = BASE / fname
        if not path.exists():
            print(f"  ! missing {fname}")
            continue
        meta = {"name": f"[temp-embed] {fname}"}
        media = MediaFileUpload(str(path), mimetype="image/png", resumable=False)
        f = drive.files().create(body=meta, media_body=media, fields="id").execute()
        fid = f["id"]
        drive.permissions().create(
            fileId=fid, body={"type": "anyone", "role": "reader"}).execute()
        ids[key] = fid
        uris[key] = f"https://drive.google.com/uc?export=download&id={fid}"
        print(f"  uploaded {fname}")
    time.sleep(2)  # let Drive propagate the ACL before Docs fetches
    return uris, ids


def lock_down(drive, ids, delete=True):
    for key, fid in ids.items():
        try:
            if delete:
                drive.files().delete(fileId=fid).execute()
            else:
                for p in drive.permissions().list(
                        fileId=fid, fields="permissions(id,type)"
                ).execute().get("permissions", []):
                    if p["type"] == "anyone":
                        drive.permissions().delete(fileId=fid,
                                                   permissionId=p["id"]).execute()
        except Exception as exc:                                # noqa: BLE001
            print(f"  ! cleanup {key}: {str(exc)[:100]}")


def create_doc(docs, drive, title, blocks, uri_map):
    doc_id = docs.documents().create(body={"title": title}).execute()["documentId"]
    batched(docs, doc_id, build_requests(blocks))
    ok, total = place_images(docs, doc_id, uri_map)
    print(f"  images placed: {ok}/{total}")
    return doc_id


# ==================================================================== TEXT ====
SUB = "IMTU Subscriptions"
DISCLAIMER = ("Logic layer only. This document deliberately excludes UI/UX, screen "
              "designs and notification copy — it describes conditions and branches, "
              "so it stays accurate when the interface changes.")

# ---- shared content fragments -------------------------------------------------
NOTIF_ROWS = [
    "Subscription purchased  —  fires immediately on a successful subscription "
    "purchase. Push. Shipped. (imtu_notification_delivered_success_text)",
    "Renewal reminder  —  fires 2 days before every charge date, at all cadences. "
    "Push. Shipped, DCS-4983. (imtu_notification_alert_text)",
    "Subscription updated by user  —  fires when the customer edits the "
    "subscription. Push. Shipped. (imtu_notification_scheduled_delivery_text)",
    "Offer withdrawn, no substitute  —  fires when the subscribed offer is "
    "discontinued in K2 and no replacement exists. Push. Shipped. "
    "(offer_cancelation_text)",
    "Offer substituted  —  fires when the offer is discontinued but K2 supplies a "
    "replacement. Push. Shipped. (offer_substitution_text)",
    "Subscription cancelled by system  —  fires on involuntary cancellation; the "
    "reason is embedded in the message. Push. Shipped, DCS-2333. "
    "(imtu_notification_scheduled_cancellation_text)",
    "Alternate payment method used  —  fires when the primary card fails and a "
    "second method succeeds. SMS via EMMS. Shipped, DCS-2413.",
]

GAPS = [
    "No payment-failure notification  —  when a renewal charge fails, the customer "
    "is not told. CRMC-3299 was raised for exactly this and has sat in Backlog "
    "since 2024. This is the single largest gap in the notification set.",
    "No retry ladder for IMTU  —  DCS-1667, which would have introduced "
    "3-attempts-then-cancel, is closed Won't Fix. The retry schedule in DCS-1200 "
    "(5/10/20 days) belongs to Subscriber Manager on the Calling side, not IMTU.",
    "Retryable vs terminal errors never ratified  —  DCS-3539 proposed a "
    "classification but closed deferring to IDTPAY-3912. Today an authorisation is "
    "retried on any error response, including insufficient funds.",
    "Fallback card order unspecified  —  DCS-5121 records the open question: "
    "\"can we for sure say that the first card in the list will be next to be "
    "charged?\" The fallback method is selected silently.",
    "Renewal hour and timezone undocumented  —  launch_at is epoch milliseconds "
    "with up to 1440 minutes of jitter (DCS-3541). No cron hour or timezone is "
    "written down anywhere; it would have to come from the code or database.",
    "Editing a payment method on an existing subscription is not built  —  "
    "DCS-4461 and DCS-4463 are open and blocked on the fraud team, because CVV "
    "cannot be stored for future use under PCI.",
    "Observability gap on failures  —  21,383 failing subscriptions (27.5%) carry "
    "a generic IDTPay - failed with no reason code.",
]


def concise_blocks():
    b = [
        ("h1", f"{SUB} — Logic Summary"),
        ("p", DISCLAIMER),
        ("p", "Scope: IMTU (International Mobile Top-Up) subscriptions only. "
              "Calling Plans, BOSS Complete and SingIt run on a different platform "
              "and different rules — see the note at the end."),

        ("h2", "The model in one paragraph"),
        ("p", "An IMTU subscription is a recurring top-up to one recipient for one "
              "offer. It is created inside a normal purchase: the customer buys a "
              "top-up with the subscription toggle on. The first charge is taken "
              "immediately on the purchase date — there is no trial and no "
              "activation delay. A timer is then scheduled, and the same top-up is "
              "re-purchased every cycle until someone stops it."),
        ("b", "Cadences  —  7, 14, 30 or 90 days. Default is derived from the "
              "offer's validity period; 30 days when there is no validity."),
        ("b", "Payment  —  wallet balance (BOSS Cash) is tried first, then a card "
              "on the customer's profile."),
        ("b", "States  —  active or cancelled. There is no past-due, suspended or "
              "paused state on IMTU."),

        ("h2", "Full lifecycle"),
        ("img", "F1"),
        ("cap", "Figure 1 — IMTU subscription lifecycle, from purchase through "
                "renewal to payment failure."),

        ("h2", "The subscription toggle"),
        ("p", "The toggle decides whether a purchase becomes a subscription. Its "
              "default state is computed by the backend on the Offer Confirmation "
              "page, in strict priority order. It is a soft restriction: a default "
              "of OFF never blocks the customer from switching it on."),
        ("img", "F2"),
        ("cap", "Figure 2 — Toggle default-state decision logic."),
        ("p", "Priority order: duplicate subscription wins over the 3-subscription "
              "cap, which wins over A/B assignment, which falls through to ON."),

        ("h2", "When we message the customer"),
        ("p", "Seven customer-facing messages exist. Each row is the condition that "
              "fires it, not the copy."),
    ]
    b += [("b", r) for r in NOTIF_ROWS]
    b += [
        ("h2", "The three things people get wrong"),
        ("b", "A failed renewal does not cancel the subscription.  —  It stays "
              "active and is simply attempted again at the next cycle, indefinitely. "
              "There is no dunning ladder and no cooldown."),
        ("b", "A failed renewal does not notify the customer.  —  There is no "
              "message for a declined charge. The customer discovers it in the app, "
              "or not at all."),
        ("b", "Payment fallback happens within a single attempt, not across days.  "
              "—  If the primary method fails, a second method on file is tried "
              "immediately. If that also fails, nothing further happens until the "
              "next cycle."),

        ("h2", "Why this matters right now"),
        ("p", "As of the April 2026 analysis, 77,650 of 273,258 active subscriptions "
              "— 28.4% — were in a failing state, and 17% of the subscriber base had "
              "no working subscription at all. Roughly half of all failing "
              "subscriptions never completed a single successful charge. The largest "
              "single cause, 31.9%, is a missing or removed payment instrument: a "
              "customer-fixable problem that we currently do not tell the customer "
              "about."),

        ("h2", "One clarification that trips everyone up"),
        ("p", "Searching Jira for subscription retry logic surfaces Subly — a clean "
              "state machine with pending / active / past-due / ended and a "
              "configurable retry policy. That is the DTC platform for BOSS Complete "
              "and SingIt. It does not govern IMTU: DTCBE-2686 lists \"MTU "
              "subscription payment ownership\" as out of scope and is itself still "
              "To Do. IMTU subscription storage is currently migrating to Subly, but "
              "payment processing, retries, fulfilment and notifications stay with "
              "DCS."),
        ("p", "Full detail, citations and open questions: see the companion "
              "reference document."),
    ]
    return b


def detailed_blocks():
    b = [
        ("h1", f"{SUB} — Logic Reference"),
        ("p", DISCLAIMER),
        ("p", "Scope: IMTU only. Every rule below is sourced from Jira or "
              "Confluence, cited inline. Where IDT has no documented rule, this "
              "document says so rather than describing generic industry behaviour."),

        # ---------------------------------------------------------------- 1
        ("h2", "1. System landscape"),
        ("p", "IMTU subscriptions are scheduled by the Timers API — rows in a "
              "Postgres timers table (type mtu-v2) in the poppers database, with a "
              "companion reminder-mtu-v2 row. Each subscription carries repeat_info: "
              "timer_id, reminder_timer_id, timer_status, launch_at, recurrent_unit, "
              "recurrent_interval, reminder_unit, reminder_interval. launch_at is "
              "epoch milliseconds. (DCS-2145, DCS-2018, DCS-3541)"),
        ("p", "Offers, transactions and fulfilment live in K2. Payment "
              "authorisation goes through IDT Pay."),
        ("h3", "1.1 Migration to Subly — read this before citing Subly"),
        ("p", "Subscription storage and event triggering are migrating from the "
              "Timers API to Subly, one subscription at a time as each reaches its "
              "charge date (Confluence 5850923041). DCS retains payment processing, "
              "purchase execution, fulfilment through K2, and notification delivery. "
              "Payment retries are explicitly named as not migrating."),
        ("p", "Consequence: DTCBE-2686 (\"Subly: past-due state, configurable retry "
              "policy, and EndReason\") describes pending / active / past-due / "
              "ended, an EndReason enum and a payment_retry_schedule. That model "
              "governs BOSS Complete and SingIt. It is still To Do, and its "
              "out-of-scope list names \"MTU subscription payment ownership\". It "
              "must not be presented as IMTU behaviour."),
        ("p", "Subly plan codes for DCS recurring transactions are "
              "dcs-recurring-transactions-{hourly, weekly, bi-weekly, monthly, "
              "three-montly}, auto_renew true, cancellation_policy immediate. Note "
              "that in Subly a subscription is not edited — it is cancelled and "
              "recreated."),

        # ---------------------------------------------------------------- 2
        ("h2", "2. Creation, first charge and activation"),
        ("img", "F1"),
        ("cap", "Figure 1 — IMTU subscription lifecycle."),
        ("b", "Creation path  —  a subscription is created inside a normal top-up "
              "purchase with the toggle on. A separate direct-subscription entry "
              "point also exists (Confluence 4525031473)."),
        ("b", "First charge  —  taken immediately on the purchase date. Worked "
              "example from the December 2025 incident record: a customer "
              "subscribing monthly on Nov 10 is charged that day, with the second "
              "iteration on Dec 10."),
        ("b", "No trial  —  IMTU has no trial, grace or pending-activation concept. "
              "Nothing in Jira or Confluence describes one."),
        ("b", "States  —  active or cancelled. There is no past-due, suspended or "
              "paused state; a subscription that cannot be charged remains active."),
        ("b", "Scheduling  —  launch_at is jittered by up to 1440 minutes. DCS-3541 "
              "applied this after rounded timers fired simultaneously and triggered "
              "Stripe rate limits; 15,580 rows were adjusted. No fixed cron hour or "
              "timezone is documented."),
        ("b", "Duplicate definition  —  same user + same recipient + same offer "
              "(Confluence 5552079089, DCS-3815)."),

        # ---------------------------------------------------------------- 3
        ("h2", "3. The subscription toggle and frequency"),
        ("img", "F2"),
        ("cap", "Figure 2 — Toggle default-state decision logic."),
        ("h3", "3.1 Default-state priority"),
        ("p", "Evaluated by the backend when the Offer Confirmation page opens "
              "(Confluence 5552079089):"),
        ("b", "If a duplicate subscription exists → OFF, reason duplicate"),
        ("b", "Else if the customer has 3 or more active subscriptions → OFF, "
              "reason max_subscriptions"),
        ("b", "Else if the customer is in the experiment control group → OFF, "
              "reason experiment"),
        ("b", "Else → ON, reason default"),
        ("p", "This is a soft restriction. A default of OFF never blocks the "
              "customer from enabling the toggle manually, and the duplicate warning "
              "never blocks a purchase."),
        ("h3", "3.2 Default frequency"),
        ("p", "Derived from the offer's validity period. Options presented: 7, 14, "
              "30, 90 days."),
        ("b", "Validity 1–7 days → 7 days"),
        ("b", "Validity 8–14 days → 14 days"),
        ("b", "Validity 15–30 days → 30 days"),
        ("b", "Validity 31+ days → 90 days"),
        ("b", "Top-up products with no validity → 30 days"),
        ("b", "Validity NULL, 0 or missing → 30 days fallback"),
        ("p", "If the customer selects a frequency while the toggle is off, the "
              "selection is preserved and restored if the toggle is later switched "
              "on. Selecting a frequency automatically switches the toggle on."),
        ("h3", "3.3 Upsell popup"),
        ("p", "Shown when the customer taps Buy with the toggle OFF and all "
              "eligibility checks pass — fewer than 3 active subscriptions and no "
              "duplicate. It is deliberately not shown when the toggle is off "
              "because of an eligibility rule, since the system has already "
              "determined the customer should not subscribe by default. It is also "
              "suppressed if the customer already saw the Featured Upsell Card."),
        ("h3", "3.4 A/B experiment"),
        ("p", "Live from the March 2026 release across both the Money App and the "
              "Calling App, targeting 25,000 users per app. Treatment group A "
              "defaults the toggle ON; control group B defaults it OFF. Assignment "
              "is persistent per user, and eligibility rules override it at all "
              "times."),
        ("b", "Toggle ON group  —  50.1% complete a purchase with a subscription"),
        ("b", "Toggle OFF group  —  15.1% interact with the toggle at all"),
        ("p", "Open: the spec records \"When will the A/B test conclude and which "
              "group will become the permanent default?\" as still TBD. Related "
              "config flags: mtu_subscription_toggle_interactions_to_disable "
              "(default 3) and mtu_subscription_toggle_reset_days (default 30), "
              "per Confluence 6091505685."),

        # ---------------------------------------------------------------- 4
        ("h2", "4. Renewal and payment"),
        ("img", "F3"),
        ("cap", "Figure 3 — Renewal charge decision logic."),
        ("h3", "4.1 Charge sequence"),
        ("b", "Wallet first  —  the subscription attempts the BOSS Cash balance "
              "before any card. If the balance cannot cover the full amount, or the "
              "wallet errors, it falls through to a card. (DCS-2905)"),
        ("b", "Card on profile  —  the card is not pinned to the subscription. "
              "DTCBE-582 changed this in May 2024 so that the card present on the "
              "user profile is used. (Confluence 3881173002)"),
        ("b", "In-flight fallback  —  if the primary method fails and another "
              "method is on file, it is charged immediately. Subsequent cycles "
              "revert to the original card. If the second attempt also fails, "
              "DCS-2413 states plainly: \"we do nothing\". DCS-5153 fixed the case "
              "where the backup method was not being selected."),
        ("b", "Fallback notification  —  an SMS is sent via EMMS when a second "
              "method is used successfully, localised EN/ES/FR/DE. (DCS-2413)"),
        ("h3", "4.2 The CVV and fraud gate"),
        ("p", "Subscriptions carry a cvv_verified flag in timer metadata "
              "(DCS-3295). When true and fraud bypass applies, the recurring charge "
              "proceeds without a fraud check. When false, the charge goes through "
              "fraud checking and can fail authorisation. Fraud Check for "
              "Subscriptions went live 24 Nov 2025 with an important consequence: "
              "\"Ensure the same card used at subscription setup is used for "
              "recurring charges. If the card changes, the subscription will fail "
              "(no new CVV flow exists).\" (Confluence 5021925393)"),
        ("h3", "4.3 Retry behaviour — the critical section"),
        ("p", "IMTU has no dunning ladder. There is no retry schedule, no attempt "
              "counter, no exhaustion state and no cooldown. After a failed cycle "
              "the subscription remains active and is simply attempted again at the "
              "next scheduled cycle."),
        ("b", "DCS-1667  —  would have added second-card fallback plus "
              "\"3 times total before informing users that the subscription will be "
              "cancelled\". Closed Won't Fix; noted as belonging to a future "
              "subscription service."),
        ("b", "DCS-1200  —  the only written retry ladder (retry at 5, 10 and 20 "
              "days, cancel on the 4th failure) is scoped to Subscriber Manager on "
              "the Calling side. It is not IMTU. DCS-1574 further notes these rules "
              "still needed review, with the live numbers held in a Google Sheet "
              "outside Jira."),
        ("b", "DCS-3407  —  the one interval that did ship: when IDT Pay returns "
              "Retry because of a processor rate limit, callers must wait at least "
              "5–10 minutes before re-attempting. This is throttling, not dunning."),
        ("b", "DCS-4944  —  Subly may invoke renewal up to 10 times, so an "
              "idempotency guard prevents double charging. Again not a dunning "
              "ladder."),
        ("h3", "4.4 Why failures never cancel"),
        ("p", "This is deliberate. DTCBE-444 introduced auto-cancellation on "
              "missing card and missing offer, and approximately 30,000 "
              "subscriptions were lost — 13,377 missing card, 10,923 offer not "
              "found, 2,012 account locked, 984 CVV. After hot fix DTCBE-552, "
              "DTCBE-623 removed cancellation for all payment scenarios, deployed "
              "22 May 2024. (Confluence 3881173002)"),

        # ---------------------------------------------------------------- 5
        ("h2", "5. Failure taxonomy"),
        ("h3", "5.1 Production distribution"),
        ("p", "From the April 2026 analysis of 273,258 active subscriptions, of "
              "which 77,650 (28.4%) were failing (Confluence 5854003362):"),
        ("b", "Missing or removed payment instrument  —  24,794 (31.9%). Requires "
              "user action. 43% of these had a working card that was later removed, "
              "median 154 days."),
        ("b", "Generic IDTPay - failed  —  21,383 (27.5%). No reason code; an "
              "explicit observability gap."),
        ("b", "Insufficient funds  —  14,645 (18.9%). Transient in principle, but "
              "28% of previously-working cases have been failing for over 90 days."),
        ("p", "Of the 36,980 subscriptions classed transient, 9,562 have been "
              "failing more than 90 days. Around half of all failing subscriptions "
              "never completed a single successful charge, and 26,005 customers — "
              "17% of the base — have no working subscription."),
        ("h3", "5.2 IDT Pay result codes"),
        ("p", "success, limit_exceeded, failed_already_refunded, "
              "failed_card_declined, failed, failed_card_expired, failed_no_credit, "
              "failed_server_error, failed_fraud, unknown_fraud_status, "
              "failed_lost_or_stolen_cc, failed_card_restricted, "
              "failed_invalid_card_info, failed_invalid_card_number, "
              "duplicate_request, cvv_required, 3ds_pending, 3ds_required, "
              "3ds_failed. (DCS-3539)"),
        ("p", "DCS-3539 proposed splitting these into retryable and terminal but "
              "closed without ratifying it, deferring to IDTPAY-3912. Its opening "
              "line still describes current behaviour: \"Currently we retry an IDT "
              "Pay authorization for any error response, even when the card has "
              "insufficient funds.\""),
        ("h3", "5.3 Queued is not a failure"),
        ("p", "Queued means accepted but not yet fulfilled. It is a frontend "
              "pseudo-status shown when the backend does not respond within roughly "
              "15 seconds (Confluence 5926354995). Queued transactions require "
              "all_transactions=true to be returned (DCS-478, DCS-2070)."),

        # ---------------------------------------------------------------- 6
        ("h2", "6. Cancellation and modification"),
        ("img", "F4"),
        ("cap", "Figure 4 — Cancellation and modification branches."),
        ("h3", "6.1 Customer-initiated cancellation"),
        ("p", "Two entry points, unchanged by the toggle work: IMTU Home → My "
              "Top-Up Activity → Edit → Cancel → Confirm; and Calling Home → Funding "
              "page → Subscriptions → Edit → Cancel. Cancellation is immediate. "
              "There is no retention offer, no exit survey and no cooldown before "
              "resubscribing."),
        ("h3", "6.2 Modification"),
        ("p", "Offer, frequency and payment method can be changed. Editing was "
              "historically implemented as cancel-and-recreate; DCS-3521 migrated it "
              "to a dedicated PUT /store/v1/subscriptions/{timerId} endpoint, and "
              "DCS-5184 tracks removing the legacy path. There is no proration — "
              "IMTU charges per cycle, not per term."),
        ("p", "Changing the payment method on an existing subscription is not "
              "built. DCS-4461 and DCS-4463 are open and blocked on the fraud team, "
              "because no immediate transaction occurs at the time of the change and "
              "CVV cannot be stored for future use under PCI."),
        ("h3", "6.3 System-initiated cancellation"),
        ("p", "Payment failure is not among these. The documented involuntary "
              "cancellation reasons are (DCS-2018, DCS-2145, Confluence 4659314778):"),
        ("b", "User phone number disconnected  —  invalid_msisdn; hard delete, no "
              "recovery"),
        ("b", "Recipient not prepaid  —  msisdn_not_prepaid"),
        ("b", "User profile locked  —  account_locked; under 3 months no action, "
              "over 3 months cancel"),
        ("b", "User profile deleted  —  account_deleted"),
        ("b", "Offer is no longer available  —  missing_offer, when no substitute "
              "exists"),

        # ---------------------------------------------------------------- 7
        ("h2", "7. Offer withdrawal and substitution"),
        ("img", "F5"),
        ("cap", "Figure 5 — Offer withdrawal branches."),
        ("p", "An automatic flow identifies subscriptions whose offer has been "
              "discontinued in K2. Each discontinued offer either has a substitute, "
              "in which case active subscriptions switch to it automatically at the "
              "Kafka event, or has none, in which case they are cancelled — on the "
              "iteration date, not at the Kafka event (Confluence 5327421441)."),
        ("p", "Whether the original frequency survives a substitution is still "
              "under PM research (DCS-4204), currently leaning toward preserving it."),
        ("h3", "7.1 The December 2025 incident"),
        ("p", "The cancellation flow did not take country into account, so "
              "withdrawing an offer in one country cancelled that offer's "
              "subscriptions everywhere. On 8 December 2025, 29,474 subscriptions "
              "across 17,464 customers were cancelled and the feature was disabled. "
              "15,723 subscriptions were reinstated with original dates; 11,662 were "
              "recreated with a new start date. 6,117 belonged to customers with no "
              "card on file and could only resume once a card was added. 6,603 "
              "customers received an SMS via Fireball. This remains the clearest "
              "worked example of how the withdrawal branch can go wrong."),

        # ---------------------------------------------------------------- 8
        ("h2", "8. Notification trigger catalogue"),
        ("p", "Conditions only — copy is deliberately out of scope. Source: "
              "Confluence 6129057864, with backend strings in 5145493539."),
    ]
    b += [("b", r) for r in NOTIF_ROWS]
    b += [
        ("p", "All push notifications use the title \"BOSS Revolution\" and deep "
              "link to the IMTU home page. Two channels exist beyond push: SMS via "
              "EMMS for the alternate-payment message, and SMS via Fireball, used "
              "for incident communications."),
        ("p", "Braze (Appboy) carries campaign and promotional messaging rather "
              "than these lifecycle triggers. Campaign-level conditions live in "
              "Braze itself and are not documented in Jira or Confluence — if a "
              "complete picture including marketing sends is needed, that has to "
              "come from the CRM team."),

        # ---------------------------------------------------------------- 9
        ("h2", "9. Known gaps and open questions"),
        ("p", "These are gaps in the documented logic, not in this document. Each "
              "one is a decision someone still owns."),
    ]
    b += [("b", g) for g in GAPS]
    b += [
        ("h2", "10. Sources"),
        ("p", "Confluence: 5552079089 Subscription Toggle and Frequency Changes · "
              "6129057864 MTU subscriptions - Push notifications · 5854003362 "
              "Subscriptions Last Transaction Status Analysis · 5327421441 MTU "
              "Subscription Cancellation (Incident) · 3881173002 Subscriptions issue "
              "· 5850923041 What is being migrated to Subly · 5740200101 Migration "
              "to Subly · 5021925393 Fraud Check for Subscriptions · 4659314778 "
              "Subscription cancellation / substitution · 6091505685 Feature Flags · "
              "5926354995 IMTU in WA · 4525031473 Direct subscription · 5536318125 "
              "BR7 MTU Subscription Promos."),
        ("p", "Jira: DCS-2413 · DCS-2905 · DCS-5153 · DCS-1133 · DCS-5121 · "
              "DCS-1667 · DCS-1200 · DCS-1574 · DCS-3407 · DCS-3539 · DCS-3541 · "
              "DCS-4944 · DCS-3295 · DCS-4461 · DCS-4463 · DCS-4983 · DCS-2333 · "
              "DCS-2018 · DCS-2145 · DCS-3521 · DCS-5184 · DCS-4204 · DCS-4317 · "
              "DCS-3815 · DCS-4514 · DTCBE-2686 · DTCBE-2696 · DTCBE-623 · "
              "CRMC-3299 · IDTPAY-3912."),
        ("p", "Compiled 11 August 2026. Figures reflect the April 2026 subscription "
              "analysis; the A/B result is early data from late March 2026."),
    ]
    return b


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)

    # Note: IDT Workspace policy returns publishOutNotPermitted on any
    # "anyone with link" grant, and the Docs API can only embed images from a
    # public URI. Rather than publish internal figures externally, the docs are
    # written with marked figure slots and the PNGs are inserted manually.
    print("Creating concise doc...")
    d1 = docs.documents().create(
        body={"title": f"{SUB} — Logic Summary"}).execute()["documentId"]
    batched(docs, d1, build_requests(concise_blocks()))

    print("Creating detailed doc...")
    d2 = docs.documents().create(
        body={"title": f"{SUB} — Logic Reference"}).execute()["documentId"]
    batched(docs, d2, build_requests(detailed_blocks()))

    print("\nDONE")
    print(f"Summary  : https://docs.google.com/document/d/{d1}/edit")
    print(f"Reference: https://docs.google.com/document/d/{d2}/edit")


if __name__ == "__main__":
    main()
