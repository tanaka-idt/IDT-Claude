#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU Revenue Shortlist - BOSS Revolution App".

Eleven ranked revenue ideas for IMTU in the BOSS Revolution app, produced by a
multi-agent analysis: four grounding passes (FY27 roadmaps + competitor
landscape, the DCS backlog including Won't-fix items, Confluence specs across
DCS/MTUOAM/DPC/TEAM, and Amplitude on BR app Prod 650506), five ideation lenses
(pricing, conversion, retention, cross-sell, growth) producing 38 candidates,
four independent judge panels (revenue upside, feasibility, risk, skeptic), and
a final completeness critic.

Every figure is labelled SOURCED or ASSUMPTION. Amplitude chart ids are quoted
so each number can be re-run. The one figure the analysis could not obtain is
carrier commission per corridor, so every number here is a fee-revenue number
and understates true contribution by an unknown amount.
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

TITLE = "IMTU Revenue Shortlist — BOSS Revolution App"

# ------------------------------------------------------------------ TABLES ----
UNKNOWNS_TABLE = [
    ["Unknown", "Why it matters", "What settles it"],
    ["Who funds discount_amount — IDT, BLS or the carrier",
     "Idea 4 is worth ~$500k/yr or exactly $0",
     "One answer from Finance / BLS commercial"],
    ["The failing-subscription pool AFTER the toggle rollout",
     "273,258 / 77,650 is an April, pre-toggle number and therefore a floor; it "
     "scales idea 1 directly",
     "Re-run the Confluence 5854003362 analysis on current data"],
    ["Whether card-updater and alternate-instrument retries are permitted at all",
     "The Nov-2025 fraud rule fixes the card at setup with no CVV flow — it may "
     "cap idea 1's mechanism",
     "Fraud team, against Confluence 5021925393"],
    ["Carrier commission per corridor",
     "The other IMTU revenue line; makes every gross-profit claim unverifiable "
     "and under-prices the face-value ideas",
     "Read-only export from MTUOAM catalog owners — there is no MTUOAM Jira "
     "project, so this is a request, not a ticket"],
    ["Non-USD share of DTC face value",
     "Scales idea 8's entire figure",
     "Same MTUOAM request"],
    ["IDT's real Stripe / IDT Pay per-transaction cost",
     "Nobody can judge a payment-rail idea without it; list pricing is certainly "
     "wrong at ~700k txns/month",
     "Finance rate card"],
    ["Data-SKU share of orders and their face value vs voice",
     "Idea 6 is unsized despite being the roadmap's top-ranked addition",
     "One Amplitude query"],
    ["Top-decile fee spend per purchaser",
     "2.081 is a mean over a heavy-tailed distribution and is load-bearing in "
     "the membership kill",
     "Decile breakdown of chart 8jhc3wbs"],
    ["Subscription cohort revenue and LTV over 90 days",
     "Required to judge ideas 1 and 5 and any cadence change; renewals emit no "
     "app event at all",
     "Finance or Subly data — build the baseline BEFORE DCS-5289 lands"],
    ["Whether the Aug offerTemporaryUnavailable spike is a corridor/catalog incident",
     "Swings idea 9 six-fold",
     "One-day Amplitude query split by corridor, carrier, offer"],
    ["Per-query number-portability price",
     "Break-even is ~$0.01/query; idea 11's lookup phase lives or dies on it",
     "K2 / vendor quote"],
    ["Whether a ladder shift is trade-up or frequency substitution",
     "Decides the SIGN of idea 7",
     "Fee revenue per purchaser per 90 days in the A/B readout"],
]

TOTAL_TABLE = [
    ["Item", "Defensible range", "Status of the number"],
    ["Idea 1 — dunning ladder", "~$284k – 1.06M / yr",
     "Pool measured and pre-toggle, so a floor. Recovery rate assumed. Additive "
     "to every other idea here."],
    ["Idea 3 — round-total pricing", "~$850k / yr",
     "Pools sourced, one assumed conversion loss, 24.6% break-even. A commercial "
     "decision, not a product A/B."],
    ["Idea 4 — promo as % of fee", "$457–543k / yr or $0",
     "Entirely conditional on the funding answer, and the arithmetic needs a "
     "distribution rather than a mean."],
    ["Idea 8 — DTC FX spread", "up to ~$878k / yr",
     "Biggest single number, weakest disclosure case. Non-USD share "
     "unquantified."],
    ["Ideas 2, 5, 7, 9, 10, 11 combined", "~$400–500k / yr",
     "After removing overlap on the shared payment-failure pool."],
    ["Idea 6 — data-bundle merchandising", "unsized",
     "No lens generated it, so it carries no revenue math here. Roadmap scores "
     "it Revenue High, TTV <1 qtr."],
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
        if kind == "table":
            line = f"[[{text}]]\n"
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


def insert_table(docs, doc_id, placeholder, data):
    """Replace a [[NAME]] placeholder paragraph with a real Docs table."""
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[{placeholder}]]":
            idx = el["startIndex"]
            plen = len(para_text(el))
            break
    if idx is None:
        print(f"  ! placeholder [[{placeholder}]] not found")
        return False

    rows, cols = len(data), len(data[0])
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx,
                                          "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx}, "rows": rows,
                         "columns": cols}},
    ]}).execute()
    time.sleep(1.0)

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
    for start, r, c in sorted(cells, reverse=True):    # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
    batched(docs, doc_id, reqs, size=30)
    return True


# ==================================================================== TEXT ====
def blocks():
    b = [
        ("h1", TITLE),
        ("p", "Eleven ranked ideas with large positive revenue impact for IMTU "
              "(International Mobile Top-Up) in the BOSS Revolution app. Compiled "
              "26 August 2026."),
        ("p", "How this was produced: four grounding passes (the FY27 roadmaps and "
              "competitor landscape in the PM workspace; the DCS backlog including "
              "Won't-fix items; Confluence specs across DCS, MTUOAM, DPC and TEAM; "
              "and Amplitude on BR app Prod, appId 650506) fed five ideation "
              "lenses — pricing, conversion, retention, cross-sell and growth — "
              "producing 38 candidate ideas. Four independent judge panels then "
              "scored every idea on revenue upside, feasibility against the actual "
              "stack, risk (including FTC negative-option and app-store exposure), "
              "and a skeptic panel whose only job was to kill ideas already in "
              "flight or resting on invented numbers. A final completeness critic "
              "audited the survivors."),
        ("p", "How to read the figures  —  every number is labelled SOURCED (with "
              "the Amplitude chart id, file path, Jira key or Confluence page id "
              "that produced it) or ASSUMPTION. Where a number could not be "
              "obtained, the document says so rather than estimating. The figure "
              "the analysis could not obtain at all is carrier commission per "
              "corridor, so every figure below is a fee-revenue figure and "
              "understates true contribution by an unknown amount."),
        ("p", "Amplitude context: org BOSS (127967), BR app Prod appId 650506. "
              "Chart ids are quoted throughout so each number can be re-run."),

        # ================================================================== 1
        ("h2", "1. Correction first: the revenue unit was wrong"),
        ("p", "Ten of the nineteen candidate ideas that reached the judging stage "
              "priced a recovered IMTU order at $5.63. That figure comes from "
              "IMTU_FY_Roadmap.md line 82 and is portfolio-level Digital Payments "
              "revenue per transaction against a ~$104M/qtr line. Against the "
              "Amplitude-measured $10.48 average face value it would imply a 54% "
              "take rate, which is impossible for airtime."),
        ("p", "IMTU's measured revenue per order is the service fee: $1.5218  —  "
              "SOURCED, Amplitude chart yf63oi1y, Last 30 Days, run 2026-08-26 — "
              "plus carrier commission, which is quantified nowhere. That is a "
              "3.7x haircut on the whole decline-recovery family of ideas, and it "
              "reorders the shortlist."),
        ("p", "The fee schedule itself was recovered from Amplitude, not from any "
              "document in the repo or Jira: a flat 15% of face value — $4 to "
              "$0.60, $10 to $1.50, $20 to $3.00 — paid by 85.4% of $10 orders "
              "(charts qjl4da1e, 7ze3ftsy; corroborated by the real-screen mockup "
              "crypto_screens/s7.html, where $25.00 + $3.75 is exactly 15.0%). At "
              "698,251 successful purchases per month that is roughly $1.06M per "
              "month, ~$12.75M per year, of BR-app IMTU fee revenue (SOURCED "
              "volume and rate; ASSUMPTION that the last-30-day rate annualises "
              "flat)."),
        ("p", "The planning consequence  —  because the fee is ad-valorem, every "
              "$1 of average face value is worth about $0.15 of fee revenue, and "
              "take-rate expansion on existing volume beats decline recovery by "
              "roughly 5:1 per unit of engineering effort."),
        ("p", "Two caveats that stop this being the whole story  —  first, because "
              "carrier commission scales with face value and is unmeasured, every "
              "fee-only figure below under-prices the face-value ideas (6, 7, 8) "
              "relative to the fee ideas. Second, the flat-15% reading is inferred "
              "from one denomination rung, while the same catalog documents "
              "describe fee dispersion of 0–25% set per offer. Both cannot be "
              "true, and the '+$1 face = +$0.15 fee' conversion rests on the "
              "reading that is contradicted."),

        ("h3", "1.1 Baseline metrics"),
        ("b", "~$12.75M / yr  —  BR-app IMTU fee revenue. 698,251 purchases/month "
              "at 15%; rate assumed to annualise flat."),
        ("b", "28.4%  —  of active subscriptions are in a failing payment state: "
              "77,650 of 273,258 (April 2026, pre-toggle)."),
        ("b", "14.35%  —  of order-completion attempts fail: 128,991/month, of "
              "which 47.3% carry no usable reason code."),
        ("b", "58.4%  —  of orders are at $10 face value or below (chart "
              "vbm1x184). Weighted average face value is $10.480."),
        ("b", "2.081 purchases and $3.17 of fee per purchaser per month  —  across "
              "~335,500 unique monthly purchasers (chart 8jhc3wbs; purchaser count "
              "derived). Treat as a mean over a heavy-tailed distribution."),

        # ================================================================== 2
        ("h2", "2. Do not build a plan on the 45.5% attach rate"),
        ("p", "This needs to be on the record before anyone builds a plan on top "
              "of the subscription attach rate. The toggle win is real but "
              "fragile, and the team is deliberately reducing it this quarter."),
        ("b", "Attach went ~0.9% to ~45.5% (established, prior Amplitude "
              "analysis). But 95.5% of taps on a default-ON toggle switch it OFF, "
              "and 12.7% of subscription purchases cancel within 30 days at a "
              "median of 5.9 days — right at the first weekly renewal."),
        ("b", "The cancel funnel is worse than previously cited  —  37,408 "
              "initiations to 35,160 confirmations per week, 94.0% completion "
              "(SOURCED, chart 9wxtpq92, week of 2026-08-17). That is materially "
              "above the ~18k/week figure in circulation. The save step in the "
              "cancel flow catches 0.98%. Caveat: single week, not reconciled "
              "against the established ~97% confirm-yes rate, and whether the "
              "chart counts events or unique users is unstated."),
        ("b", "DCS-5289 is at QA Available  —  it changes the default-OFF trigger "
              "from '3 or more active subscriptions AND same offer AND same "
              "recipient' to '1 or more active subscriptions'. This will "
              "mechanically cut the attach rate. Any FY plan quoting 45.5% is "
              "quoting a number the team is reducing on purpose."),
        ("b", "Two open consent defects, not optics  —  DCS-5277 (Critical, QA "
              "Testing): subscription created without user consent when the toggle "
              "is ON but not shown on Order Confirmation. DCS-5001: a live "
              "customer dispute over automatic recharges."),
        ("b", "The 5.9-day cancel has a findable mechanical cause  —  renewal "
              "frequency is auto-derived from offer validity (core-logic "
              "reference, section 4.2: validity of 1–7 days yields a 7-day "
              "renewal). 28.0% of new subscriptions are on weekly cadence and "
              "96.6% sit at interval=1 (SOURCED, charts exfxfy3d, 6gu681ly). Every "
              "7-day data or bundle SKU silently becomes a weekly charge nobody "
              "chose."),
        ("p", "Planning implication  —  report and forecast on fee revenue per "
              "purchaser per 90 days, not attach rate. That metric survives "
              "DCS-5289; attach rate does not."),
        ("p", "One number needs reconciling before it leaves the building  —  "
              "measured on MTUOrderCompleteBtn with is_subscription=True, July "
              "order-level attach is 32.1%, not 45.5%, and 4.9% of July events "
              "(43,767 of 899,163) carry no is_subscription value at all. "
              "Separately, renewal charges emit no app event (they happen "
              "backend-side in Subly/Stripe), so the subscription programme's "
              "actual LTV case cannot be validated in Amplitude at all. It needs "
              "finance or Subly data."),
        ("p", "The obvious cadence fix is not a revenue idea  —  switching the "
              "default from offer-validity to the sender's own inter-purchase gap "
              "is the right structural repair, but moving a surviving weekly "
              "subscription to monthly cuts its renewals roughly 4x. For the ~87% "
              "who do not cancel within 30 days that is a large in-period revenue "
              "loss against ~494 subscriptions per week retained. Do it as a trust "
              "and durability fix with a 90-day cohort-revenue readout, pre-sell "
              "the attach-rate and renewal-count drop as a deliberate trade, and "
              "do not book it as upside."),

        # ================================================================== 3
        ("h2", "3. What the completeness critic changed"),
        ("p", "The first synthesis produced nine ideas. A final critic pass, "
              "checking specifically for levers no lens had covered, found one "
              "omission large enough to top the list — independently corroborated "
              "by two of the four grounding agents."),
        ("b", "Promoted to #1  —  dunning / involuntary-churn recovery was absent "
              "from the shortlist, from the excluded list and from the unknowns "
              "table, despite being the largest measured pool in the entire "
              "grounding set and the only idea additive to every other one here."),
        ("b", "Added  —  data-bundle merchandising (the roadmap's own top-ranked "
              "addition, TTV under one quarter) and a sell-side FX spread on the "
              "DTC channel, which had been killed by association with a different, "
              "correctly killed cost-side FX idea."),
        ("b", "Re-ranked  —  round-total pricing dropped from #1 to #3: it is a "
              "33% fee increase on a liquidity-constrained base and overlaps the "
              "committed Variable Fees initiative. The cheap, unblocked "
              "failure-taxonomy work moved up to #2."),
        ("b", "Kill reversed  —  BOSS Sender membership was killed partly on an "
              "Apple 3.1.1 claim that is wrong: airtime is a real-world service "
              "delivered by a carrier, not in-app digital content, and BR already "
              "bills IMTU subscriptions outside IAP today."),

        # ================================================================== 4
        ("h2", "4. Ranked shortlist"),
        ("p", "Ranked by revenue upside x feasibility / risk. Ideas 2, 9, 10 and "
              "11 all draw on the same 128,991/month payment-failure pool — do not "
              "sum them. Idea 1 draws on a different population and is additive to "
              "all of them. Pools are sourced; conversion rates are assumptions "
              "until the first A/B reports."),

        # ---- 1
        ("h3", "Idea 1 — Build the dunning ladder IMTU has never had"),
        ("p", "~$284k–1.06M/yr · Effort M, largely a port not a build · BE, APP, "
              "TPM, Fraud, IDT Pay · ADDED AFTER REVIEW · pool measured · additive "
              "to every other idea"),
        ("p", "Mechanism  —  verified verbatim in the core-logic reference, "
              "section 5.3: 'IMTU has no dunning ladder. There is no retry "
              "schedule, no attempt counter, no exhaustion condition and no "
              "cooldown period. After a failed cycle the subscription remains "
              "active and is attempted again at the next scheduled cycle, "
              "indefinitely.' The renewal path tries the registered card, then at "
              "most one alternate, and then nothing happens — and the user is "
              "never told. Ship a retry ladder timed to payroll cycles, a "
              "card-updater integration, pre-expiry reminders, pre-dunning nudges, "
              "and a failed-payment message that links to the repair screen."),
        ("p", "Sizing  —  SOURCED: the April 2026 analysis of 273,258 active "
              "subscriptions found 77,650 (28.4%) in a failing state (Confluence "
              "5854003362). Missing or removed payment instrument: 24,794 (31.9%), "
              "and 43% of those had a working card that was later removed, median "
              "154 days. Generic 'IDTPay - failed': 21,383 (27.5%) with no reason "
              "code at all, an explicit observability gap. Insufficient funds: "
              "14,645 (18.9%). Of the 36,980 classed transient, 9,562 have been "
              "failing for more than 90 days; roughly half of all failing "
              "subscriptions never completed a single successful charge; and "
              "26,005 customers — 17% of the subscriber base — have no working "
              "subscription at all."),
        ("p", "ASSUMPTION 20% recovery on monthly cadence: 15,530 x 12 x $1.5218 "
              "is approximately $284k/yr. At the 70–80% recovery benchmark for "
              "well-run dunning cited in IMTU_Subscriptions_FY27.md line 24 it "
              "reaches ~$1.06M/yr, which straddles or beats every other idea in "
              "this document."),
        ("p", "Why this is the strongest item here  —  it is largely a port: the "
              "calling platform already shipped the instrument cascade (ADMI-9099: "
              "PRIORITY_HANDLE, off-session 3DS, off-session wallet handle reuse). "
              "DCS-4992 is Done, so the repair UI for a missing card already "
              "exists and nothing tells the user to use it. And 273,258 is a "
              "pre-toggle April number — attach went 0.9% to 45.5% after that, so "
              "the failing pool has almost certainly grown proportionally. The "
              "toggle win multiplied this leak."),
        ("p", "The gate  —  Fraud Check for Subscriptions went live on 24 November "
              "2025 with the consequence that the same card used at setup must be "
              "used for recurring charges: if the card changes the subscription "
              "fails, and no new-CVV flow exists (Confluence 5021925393). That "
              "directly constrains the card-updater and alternate-instrument "
              "halves of this idea. Settle it with the fraud team before scoping, "
              "or the ladder can only ever retry the same failing card."),
        ("p", "Why it kept getting dropped  —  DCS-1667, which would have "
              "introduced second-card fallback plus '3 attempts before informing "
              "users', was closed Won't Fix. DCS-3539 deferred to IDTPAY-3912. "
              "CRMC-3299 has sat in Backlog since 2024. Confluence states "
              "explicitly that payment retries are NOT migrating to Subly. This "
              "needs a named owner and an epic or it dies a fourth time — and "
              "IMTU_Subscriptions_FY27.md line 124 already recommends shipping the "
              "dunning layer first."),
        ("p", "First ticket  —  [TPM] IMTU — Re-measure the failing-subscription "
              "pool post-toggle and confirm with Fraud whether card-updater / "
              "alternate-instrument retries are permitted under the Nov-2025 "
              "card-immutability rule"),

        # ---- 2
        ("h3", "Idea 2 — Reason-branch the failure screen"),
        ("p", "~$180k/yr · Effort S–M · BE, APP, Design, QA, TPM · safe bet · no "
              "external dependency · unblocks ideas 9, 10 and 11"),
        ("p", "Mechanism  —  14.35% of order-completion attempts fail and 47.3% of "
              "those arrive with the uninformative reason 'failed', so every "
              "recovery mechanism downstream fires blind. Meanwhile IDT Pay returns "
              "a 19-value result enum (core-logic reference 6.2) including "
              "cvv_required, 3ds_pending, 3ds_required, 3ds_failed and "
              "failed_server_error — none of which appear anywhere in the Amplitude "
              "breakdown. Several of those are not declines at all; they are orders "
              "the user could complete right now."),
        ("b", "Pass the full IDT Pay status through to failed_reason and ratify a "
              "retryable-versus-terminal split."),
        ("b", "Branch the screen: retryable or server error to a one-tap retry on "
              "the same order; challenge-required to the 3DS/CVV step (carve this "
              "out as its own ticket — a post-authorisation SCA challenge is a real "
              "payment build, not a screen branch); card error to a one-tap 'use "
              "your other card' with the next instrument pre-selected and confirmed "
              "by the user."),
        ("b", "Funds down-sell: failedNoCredit is 35,849/month and is the most "
              "recoverable class, because the blocker is the amount, not the "
              "intent. DTC is fixed-offer-only (Confluence 5108269167), so a lower "
              "rung provably exists on every ladder — offer the next-lower "
              "denomination for the same recipient and carrier, pre-filled, one "
              "tap."),
        ("b", "Absorbs the standalone out-of-session SMS idea that ranked "
              "separately at ~$57k/yr — below this list's noise floor, unmeasurable "
              "while DCS-5260 is open, TCPA-gated, and overlapping DCS-5291 which "
              "is In Progress. Fold it in as the notification branch."),
        ("p", "Sizing  —  SOURCED pools, ASSUMPTION conversion rates, all at "
              "$1.5218. 3DS/CVV/server-error: 61,059 unattributed x 25% completable "
              "x 40% convert = 6,105/month, ~$112k/yr. Funds down-sell: 35,849 x "
              "12% accept at 50–60% of fee yield (a real down-sell is usually two "
              "or more rungs, $10 to $5, not one), ~$39–47k/yr. One-tap second "
              "instrument on failedCardDeclined (3,874) and failedCardRestricted "
              "(4,510) x 20% success, ~$31k/yr. Total ~$180k/yr."),
        ("p", "Do not build the silent cascade  —  the original proposal was to "
              "retry a second instrument automatically before showing any failure. "
              "That is a 'transaction not authorized' dispute mapped to a "
              "card-network reason code, it repeats the act-without-consent "
              "instinct that produced DCS-5277, and layering it on a path that "
              "already retries for any error response — even insufficient funds — "
              "will raise decline ratios with issuers and worsen DCS-5252. One "
              "tap, user-confirmed, saved instruments only."),
        ("p", "IDTPAY-3912 does not block this  —  that ticket is 'Implement Global "
              "Card Blocking based on Recurring Hard Decline Codes', in Triage "
              "since 2026-01-22, unrelated scope. Remove it from the dependency "
              "list. failedNoCredit is already emitted as its own distinct value, "
              "so the down-sell can ship in parallel with the taxonomy work."),
        ("p", "The A/B must measure net revenue per failed attempt, not down-sell "
              "acceptance rate, or full-price-retry cannibalisation will read as a "
              "win. The retryable/terminal table is the business decision DCS-3539 "
              "closed by deferring; it needs a named owner or this dies the same "
              "way."),
        ("p", "First ticket  —  [BE] IMTU — Pass the full IDT Pay result code "
              "through to failed_reason on MTUOrderStatusFailedScr"),

        # ---- 3
        ("h3", "Idea 3 — Round-total pricing on the payment bar being rebuilt now"),
        ("p", "~$850k/yr · Effort S–M · APP, BE, Design, QA, TPM, Legal · was "
              "ranked #1 · a commercial decision, not a product A/B"),
        ("p", "Mechanism  —  a $10 top-up totals exactly $11.50 for 85.4% of "
              "buyers; $5 totals $5.75. The fee is ad-valorem and therefore fully "
              "parameterisable: hold face value constant and set the fee so the "
              "total lands on a charm price — $11.99 on the $10 rung, $5.99 on $5. "
              "Test against the current itemised control."),
        ("p", "Sizing  —  SOURCED: the $10 rung is 141,152 orders/month, of which "
              "120,583 (85.4%) pay a $1.50 fee (charts vbm1x184, 7ze3ftsy); the $5 "
              "rung is 74,996 at $0.75. DERIVED at an ASSUMED 2% conversion loss: "
              "the $10 rung yields +$54.3k/month, ~$652k/yr; the $5 rung "
              "+$16.5k/month, ~$198k/yr. Combined ~$850k/yr. The robustness "
              "argument is stronger than the point estimate: incremental fee is "
              "$0.49 against a $1.50 base, so break-even volume loss is 24.6%. Even "
              "a 10% conversion loss clears comfortably."),
        ("p", "Why this dropped from #1 to #3  —  it is a 33% fee increase "
              "($1.50 to $1.99) on a base this same analysis calls "
              "liquidity-constrained: 58.4% of orders are $10 or under and there "
              "are 35,849 insufficient-funds declines a month. It ships while two "
              "consent defects are open and while the team is remediating 'users "
              "subscribe without realising'. Itemising a higher fee does not make "
              "it not a higher fee. It is also the same scope as Variable Fees "
              "(S5), already committed for FY27 — and fee-tiering was excluded "
              "from this list partly because S5 owns it. Treat this as a Finance "
              "and commercial pricing decision that a product A/B can inform, not "
              "as a product A/B that sets price."),
        ("p", "Ship variant B only  —  round total with the fee still itemised "
              "underneath. Do NOT ship the 'all-in, nothing else to pay' framing: "
              "using a transparency label as cover for a price rise inverts its "
              "purpose, collides head-on with the A9 fee-transparency commitment, "
              "and is exactly what Xoom competes on "
              "(MTU_Competitor_Landscape.md section 3B)."),
        ("p", "Why it is cheap  —  DCS-5299, DCS-5318 (Critical), DCS-5319, "
              "DCS-5320 and DCS-5321 are all live children of DCS-5297 rebuilding "
              "the Total-amount and price-breakdown sections into the persistent "
              "payment bar, and DCS-5303 already provisions the feature flag and "
              "A/B harness. DCS-5081 is at PENDING DEV DEPLOYMENT. This is one "
              "extra variant on a component being written anyway — but it needs its "
              "own A/B window so it does not confound the DCS-5303 V2 toggle test."),
        ("p", "Arithmetic notes  —  excluding the $20 rung as 'past break-even at "
              "+4.3%' is incoherent, because the included $10 rung's $11.50 to "
              "$11.99 is +4.26%. Either both are past break-even or neither is. "
              "The 120,583 figure reads as the product of two separately-cited "
              "charts, so verify that 7ze3ftsy is the fee distribution WITHIN the "
              "$10 rung before quoting it as measured. And nothing here is priced "
              "net of payment-processing cost, which is unknown and itself "
              "ad-valorem, so the true increment is under $0.49."),
        ("p", "Load-bearing unknown to resolve before estimating  —  is the service "
              "fee applied in store-api at order assembly (overridable in-team) or "
              "resolved per offer from the MTUOAM catalog (not overridable "
              "in-team, and there is no MTUOAM Jira project to file into)?"),
        ("p", "First ticket  —  [BE] IMTU — Spike: where is the 15% service fee "
              "resolved (store-api order assembly vs MTUOAM offer catalog), and "
              "can it accept a target-total input?"),

        # ---- 4
        ("h3", "Idea 4 — The promo is eating the fee: cap it as a percentage of fee"),
        ("p", "~$457–543k/yr, or exactly $0 · Effort M · BE, TPM, QA, BLS, Finance "
              "· binary on one Finance answer"),
        ("p", "Mechanism  —  on the 8.5% of orders that carry a promo, "
              "discount_amount is a cash reduction off the order total, so it lands "
              "directly on the 15% service fee, which is IDT's own revenue line. "
              "The discount consumes 83–95% of the entire fee, leaving about nine "
              "cents retained on a discounted order. Express every BLS/loyalty "
              "promo as a percentage of fee_amount with a hard cap (for example "
              "50%) so a promo can never exceed the revenue it discounts. Where "
              "deeper incentive is commercially needed, fund it as bonus face value "
              "from carrier commission (the 'discount' term in the MTUOAM cost "
              "formula, Confluence 4484628828) rather than as a rebate off IDT's "
              "fee — same perceived generosity, different P&L line."),
        ("p", "Sizing  —  SOURCED: 59,333 of 698,251 orders carry a discount, an "
              "8.5% attach rate (chart 9tojtd0c); average discount $1.6171 in "
              "August and $1.6045 in July (chart oarm1oig); average fee on that "
              "same subset $1.7105 August and $1.9240 July (chart rufqfadk). "
              "Discount over fee is therefore 94.5% on the August window and 83.4% "
              "on July — a large enough swing that both should be quoted, and note "
              "the count is a 30-day total while the averages are monthly buckets. "
              "Capping at 50% of fee saves $0.64–0.76 per order across 59,333 "
              "orders, $38–45k/month, ~$457–543k/yr, at an ASSUMED zero conversion "
              "loss."),
        ("p", "The gate, not a risk  —  the IDT-versus-BLS-versus-carrier funding "
              "split for discount_amount is documented nowhere. If BLS or the "
              "carrier funds it, the prize is exactly $0 and the cap only destroys "
              "conversion. Rank the question, not the lever."),
        ("p", "The arithmetic is wrong in method, not just in inputs  —  it applies "
              "a per-order cap to a mean discount. If the discount distribution is "
              "bimodal (many small punch-card discounts plus a few 100%-off-fee "
              "promos, and DCS-3997 confirms those exist), a 50%-of-fee cap saves "
              "far less than mean arithmetic implies. Get the distribution, not the "
              "average. And zero conversion loss on an instrument whose entire "
              "purpose is conversion is not conservative — it is the assumption "
              "that decides the answer, so this ships behind a flag with a "
              "permanent holdout or not at all."),
        ("p", "Encouraging precedent  —  DCS-3997 shows the BLS /api/participations "
              "call already carries a customer_fee parameter and loyalty correctly "
              "returned a '100% off fee' promo; the failure was client-side "
              "application. Percentage-of-fee is an existing, exercised capability, "
              "not new plumbing. DCS-5217 (BE logic centralised) and DCS-5045 "
              "(promo_groups instant/subscription) are Done."),
        ("p", "Apply to new subscriptions only  —  shrinking a discount an existing "
              "subscriber was shown at signup raises their effective renewal price "
              "and triggers state Automatic Renewal Law notice obligations. "
              "DCS-5110 (To Do) is the gating legal work."),
        ("p", "Fold in, do not run separately  —  the tenure-escalating variant for "
              "subscription promos (small at cycle 1, full at cycle 4+) is already "
              "option 3 of four inside the open spike DCS-5293. Its standalone case "
              "was overstated 4–6x: the $2.50 figure comes from DCS-5148, a "
              "Won't-fix bug whose summary is that the message was never shown, and "
              "the measured average discount is $1.62 on no more than 26% of "
              "subscription orders, so subsidy-at-risk is ~$146k/yr, not $870k. "
              "Rule out claw-back — clawing a discount from a cancelling user is a "
              "chargeback generator against an already-open consent defect."),
        ("p", "First ticket  —  [TPM] IMTU — Establish who funds discount_amount "
              "(IDT / BLS / carrier) and pull the discount distribution, not the "
              "mean"),

        # ---- 5
        ("h3", "Idea 5 — Skip-a-cycle, via the timer table not Subly"),
        ("p", "~$139–223k/yr · Effort S for skip, L for full pause · BE, APP, "
              "Design, QA, TPM · largest voluntary-cancel pool · no BR benchmark"),
        ("p", "Mechanism  —  IMTU subscriptions have exactly two states, active or "
              "cancelled: 'there is no past-due, suspended or paused state' "
              "(core-logic reference section 1). So a sender whose only problem is "
              "timing has one available action, and 94.0% of them take it. Surface "
              "'Skip this one' in the renewal reminder that already fires two days "
              "before the iteration date (DCS-4983, Done), and as the FIRST branch "
              "of the cancel flow, before any argument or discount."),
        ("p", "The non-obvious part is the implementation  —  do not build a paused "
              "state in Subly. DTCBE-2686, which defines Subly's state machine, is "
              "still To Do and explicitly lists 'MTU subscription payment "
              "ownership' as out of scope, so that is not deliverable in one or two "
              "quarters. But IMTU scheduling is rows in a Postgres timers table "
              "(type mtu-v2) in poppers, with launch_at in epoch milliseconds, plus "
              "a companion reminder-mtu-v2 row. A skip is a launch_at bump of one "
              "interval on both rows — fully DCS-controlled, no new state, no "
              "external platform. Ship that this quarter and treat indefinite pause "
              "as the separate L-sized state-machine change it actually is."),
        ("p", "Sizing  —  SOURCED: 35,160 cancel confirmations per week, 1.83M/yr, "
              "from 37,408 initiations at 94.0% completion (chart 9wxtpq92). A skip "
              "forgoes the current cycle by definition, so a deflected subscription "
              "nets +1 renewal, not +2. ASSUMPTION 5% choose skip: 1,758/week x 1 "
              "renewal x $1.5218 is ~$139k/yr; at 8%, ~$223k/yr; scaling linearly "
              "if deflected subscriptions survive more than one further cycle. "
              "Deflection rate is the single load-bearing assumption and has no BR "
              "benchmark, because no save step has ever shipped."),
        ("p", "The sharpest gap in the whole backlog  —  DCS-5257's four retention "
              "variants (emotional, benefit-based, incentive-based, no-discount) all "
              "ARGUE with the sender, and DCS-5050 (savings-to-date endpoint) is "
              "already Done and unused. None of the four creates the backend state "
              "that deferral requires. Ship skip as a fifth variant inside the "
              "DCS-5257/5258 A/B, not as a separate release. DCS-5258 is To Do and "
              "unassigned."),
        ("p", "One caveat to instrument, not ignore  —  a large share of this "
              "cancel pool is people undoing a subscription they never chose. "
              "Deflecting them into a skip re-banks revenue they never authorised. "
              "Split the readout by whether the subscription was toggle-created "
              "(default_state is already captured on MTUSubscriptionToggleTap) and "
              "judge the intentional and unintentional cohorts separately. And cap "
              "any pause at two cycles with auto-resume plus advance notification, "
              "or you build a zombie-subscription population that inflates the "
              "active base and bills nothing."),
        ("p", "First ticket  —  [BE] IMTU — Skip next renewal: bump launch_at by "
              "one interval on the mtu-v2 and reminder-mtu-v2 timer rows"),

        # ---- 6
        ("h3", "Idea 6 — Data-first merchandising (the roadmap's own top pick)"),
        ("p", "Unsized here · Effort M, TTV under one quarter · APP, BE, Design, "
              "TPM, K2 · ADDED AFTER REVIEW · demand-side"),
        ("p", "Mechanism  —  IMTU_FY27_Plan.md line 13 states it plainly: all seven "
              "selected FY27 initiatives are voice-airtime-centric, 'yet the "
              "defining category trend is prepaid to data, and every competitor has "
              "moved (Ding sells data plans across 850+ operators; Rebtel Bundles; "
              "Reloadly's Data Bundle API; DT One). A Data-Bundle Builder is the "
              "single most important addition.' It is scored Revenue High, "
              "Complexity Med, TTV under one quarter (line 45) and placed in Now/Q1 "
              "(line 122), yet it is not one of the seven committed items."),
        ("p", "Data SKUs are already live in the app, so the near-term move is "
              "merchandising rather than a platform build: surface data bundles as "
              "a first-class category with data-first defaults per corridor, compose "
              "GB plus voice plus social, and lead with them where the recipient's "
              "usage suggests it."),
        ("p", "Why it belongs above the ladder-anchoring idea  —  both are "
              "face-value levers and face value is revenue at 15%, but this one "
              "gives the sender a demand-side reason to trade up (a better thing "
              "for the recipient) rather than relying on an anchoring effect. Same "
              "economics, none of the dark-pattern exposure, and carrier commission "
              "scales with face value too."),
        ("p", "Honest status: unsized  —  no lens generated this idea, so it "
              "carries no revenue math in this document. Sizing needs the data-SKU "
              "share of current orders and their average face value versus voice, "
              "which is one Amplitude query. Do that before it enters a plan; the "
              "roadmap's 'Revenue: High' is an assessment, not a measurement."),
        ("p", "It also unlocks two committed items  —  Annual Plans (S1) gains "
              "'data annual plan' and 'gift an annual plan' variants once the "
              "builder exists (line 113), and every new corridor inherits it (line "
              "90). It also interacts with the cadence bug in section 2: 7-day data "
              "SKUs are exactly what generates unwanted weekly subscriptions."),
        ("p", "First ticket  —  [TPM] IMTU — Size the data-bundle opportunity: "
              "current data-SKU share of orders, average face value vs voice, by "
              "corridor"),

        # ---- 7
        ("h3", "Idea 7 — Mid-denomination anchor on the offer ladder"),
        ("p", "~$251k/yr on an assumed shift · Effort M · APP, BE, Design, QA, TPM "
              "· ranked here for the sequencing, not the number"),
        ("p", "Mechanism  —  because the fee is a fixed 15% of face, average face "
              "value and fee revenue move one-for-one: the ladder is a pricing "
              "surface, not just a merchandising one. Two moves worth testing: lead "
              "with a mid-ladder anchor rather than the lowest denomination, so the "
              "$10 rung reads as the economy option; and insert the missing rungs — "
              "there is no $11 or $13 between $10 and $12/$15, while the low end is "
              "unusually dense ($4, $4.50, $5, $6, $7, $8, $9, $10 all live), which "
              "is backwards for trading up."),
        ("p", "Sizing  —  SOURCED: the top-12 denominations are 571,739 of 698,251 "
              "orders (81.9%), weighted average face $10.480, and 58.4% of all "
              "orders are at $10 face or below (chart vbm1x184). SOURCED conversion "
              "factor: +$1.00 of average face is +$0.15 fee per order, +$105k/month "
              "if it applied to every order. ASSUMPTION 5 percentage points of "
              "orders shift up one rung (+$4.00 face): 34,913 x $4.00 x 15% is "
              "+$20.9k/month, ~$251k/yr in fee, plus ~$1.68M/yr of additional face "
              "value carrying unquantified carrier commission."),
        ("p", "The offset nobody modelled  —  this base's binding constraint is "
              "budget, not preference: 58.4% of orders are $10 or under and there "
              "are 35,849 insufficient-funds declines a month. A sender with a "
              "fixed monthly support budget anchored from $10 to $15 may simply "
              "send LESS OFTEN, making the face-value lift pure frequency "
              "cannibalisation at zero revenue gain. The A/B must report fee "
              "revenue per purchaser per 90 days, not average face value or ARPT, "
              "or a fixed-budget substitution reads as a win."),
        ("p", "Why it ranks despite being all-assumption  —  Open Ranges (S4) is a "
              "committed FY27 initiative, and open amount entry destroys the "
              "anchoring lever: senders type round numbers and anchor low. Run and "
              "measure the ladder test BEFORE S4 ships, or the effect is "
              "permanently unmeasurable. S4 is both a threat to this idea's "
              "measurability and an unsized revenue lever of its own."),
        ("p", "Explicitly excluded from this idea  —  ranking the offer list by IDT "
              "gross profit per order. That optimises the displayed ordering "
              "against the customer's interest with no disclosure, on a "
              "liquidity-constrained base, and it is the same institutional "
              "instinct as the default-ON toggle. It also depends on carrier "
              "commission being surfaced to the offer-list service, and that data "
              "lives in a catalog with no Jira path for DCS. Do not build on "
              "DCS-5074 — it is BLOCKED. New rungs are a K2/carrier catalog ask "
              "where denominations are carrier-defined; scope that separately."),
        ("p", "First ticket  —  [APP] IMTU — A/B the offer-list ordering: "
              "mid-denomination anchor vs ascending price"),

        # ---- 8
        ("h3", "Idea 8 — The DTC channel is the only one with no FX spread"),
        ("p", "Up to ~$878k/yr · Effort M, the configuration already exists · "
              "MTUOAM catalog, Finance, TPM · ADDED AFTER REVIEW · transparency "
              "collision"),
        ("p", "Mechanism  —  per the MTUOAM offer-setup documents (Confluence "
              "5108269167 and 5000626416), the BR app's DTC channel is uniquely "
              "constrained: fixed offers only, no PriceFX/Spread, market-rate "
              "reprice, round up to the next $0.25 — while Retail, Wholesale and "
              "B2B/Zendit get range offers and a fully built FX Spread "
              "configuration (spread %, periodic versus float, auto-adjust "
              "threshold, round-up, effective date). Most large corridors — HT, DO, "
              "GT, SV, HN, CU, MX, VE — are non-USD-denominated, so this is a live "
              "price lever on face value that the app simply does not use."),
        ("p", "Sizing  —  SOURCED: total face value is 698,251 x $10.48, "
              "approximately $7.32M per month. ASSUMPTION of a 1% spread on the "
              "non-USD share gives up to ~$878k/yr, with the non-USD share "
              "unquantified — which is the first thing to measure, because it "
              "scales the whole figure."),
        ("p", "Read this before liking the number  —  an FX spread is an "
              "UNDISCLOSED price increase. It collides with the A9 "
              "fee-transparency commitment considerably harder than the 'all-in' "
              "framing this analysis already refused in idea 3, and harder than an "
              "itemised fee change. The earlier analysis applied a transparency "
              "standard to the fee and never applied it to FX. If you would not "
              "ship variant C of idea 3, you need a very explicit reason to ship "
              "this. It is a Finance and Legal call, not a product one."),
        ("p", "And it is not yours to file  —  the configuration lives in the "
              "MTUOAM catalog, for which there is no Jira project DCS can file "
              "into. The deliverable is a request to the catalog owners, not a "
              "ticket. Note this is a different idea from the cost-side FX hygiene "
              "item that was correctly killed in section 8."),
        ("p", "First ticket  —  [TPM] IMTU — Request from MTUOAM: non-USD share of "
              "DTC face value by corridor, and whether a DTC PriceFX/Spread is "
              "permissible under the A9 transparency commitment"),

        # ---- 9
        ("h3", "Idea 9 — Revalidate offer availability before payment"),
        ("p", "~$25–156k/yr, and the range is the point · Effort S diagnostic then "
              "M · BE, APP, Design, QA, TPM, K2"),
        ("p", "Mechanism  —  the order confirmation screen can be reached with an "
              "offer K2 no longer sells, and the user only finds out after tapping "
              "complete. Two moves: revalidate availability server-side on "
              "order-screen render and on submit, so an unavailable offer never "
              "reaches a payment attempt (this half is pure risk reduction and "
              "would rank far higher on its own); and when it does happen, return "
              "the nearest equivalent offer for the same recipient and carrier for "
              "one-tap user confirmation — never a silent swap."),
        ("p", "Sizing  —  SOURCED: offerTemporaryUnavailable was 2,302 events in "
              "July 2026 and 12,340 in 1–26 August, a 5.36x step change, "
              "approximately 14,238/month normalised. ASSUMPTION 60% convert on a "
              "confirmed substitute: 8,543 x $1.5218 is ~$156k/yr at the August "
              "rate, ~$25k/yr at the July rate."),
        ("p", "That range is a prerequisite, not a sensitivity case  —  a 5.4x jump "
              "in one failure reason is far more likely a specific corridor, "
              "carrier or catalog event that gets fixed as a defect regardless. The "
              "one-day query that settles it should run before any build is funded. "
              "Note carrierProblemContactCarrier moved 5,320 to 7,697 over the same "
              "window and currently tells the user to contact the carrier "
              "themselves, with no recovery path at all."),
        ("p", "Hard constraint on the substitution half  —  the offer-withdrawal "
              "and substitution flow was built and then disabled after the 8 "
              "December 2025 incident: 29,474 subscriptions cancelled across 17,464 "
              "customers, 6,117 with no card on file (core-logic reference 8.1, "
              "Confluence 5327421441, DCS-4204). The lesson was that substitution "
              "must respect country scope, not that substitution is wrong — but "
              "purchase-time substitution must be firewalled from subscription "
              "logic entirely. Also DCS-5178 (subscription promo not applied when "
              "the offer is unavailable) is Won't fix, so promo behaviour on a "
              "substituted offer is genuinely undefined and needs a decision in the "
              "spec, or you ship an order that silently drops a discount the user "
              "was shown."),
        ("p", "Scope it as the first ticket of DCS-4442 rather than a new epic — "
              "though note that epic is Low priority and unassigned and will not "
              "pull this along on its own."),
        ("p", "First ticket  —  [TPM] IMTU — Root-cause the 5.4x "
              "offerTemporaryUnavailable increase (Jul to Aug 2026) by corridor, "
              "carrier and offer"),

        # ---- 10
        ("h3", "Idea 10 — Resolve the ambiguous-outcome orders, and add an "
               "idempotency key"),
        ("p", "Revenue explicitly UNQUANTIFIED · Effort S then M–L · BE, APP, "
              "Design, QA, TPM, K2 · gates ideas 2 and 5 · do it anyway"),
        ("p", "Mechanism  —  'queued' is not a backend state; it is a frontend "
              "pseudo-status shown when the backend does not respond within roughly "
              "15 seconds (core-logic reference 6.3), and K2 fulfils "
              "asynchronously, so a slow fulfilment and a failed one look identical "
              "to the sender. SOURCED July arithmetic: 899,168 completion taps minus "
              "730,070 success minus 128,991 failed minus 18,297 queued leaves "
              "21,810 attempts that reached no status screen at all; with the "
              "queued, 40,107 per month whose outcome the user was never clearly "
              "told. Against 23,920 MTUHomeActivityRetryBtn taps per month, that is "
              "a double-charge waiting to happen."),
        ("p", "Two phases  —  phase 1 (S, no dependencies) is a BE pull resolving "
              "one month of queued and no-status orders to their real terminal "
              "state. Phase 2 is a persistent pending state the app can poll or "
              "subscribe to, an idempotency key on order submission, a K2 delivery "
              "retry ladder, and a resolution push."),
        ("p", "Be honest about the number  —  the $226k/month figure circulating "
              "for this is built on the wrong $5.63 unit (at $1.5218 it is about "
              "$61k/month of IDT fee revenue in an unconfirmed state) and it is "
              "revenue ALREADY RECOGNISED, not incremental. The 21,810 residual is "
              "also an instrumentation inference: it subtracts across four event "
              "counts with different denominators (taps versus screen views), and "
              "MTUOrderCompleteBtn can fire more than once per order, so it sits "
              "within event-loss noise. No refund rate, chargeback rate or "
              "support-cost baseline for IMTU exists in any file, ticket or "
              "Confluence page, which is why this is protective rather than a "
              "revenue line."),
        ("p", "Why it still ranks here  —  phase 1 validates or invalidates the "
              "failure counts that ideas 2, 9 and 11 are all built on, which makes "
              "it the highest-leverage cheap thing in this document. And "
              "idempotency must land before any of those ideas make retry "
              "affordances more prominent, or they actively increase double-charge "
              "and chargeback exposure on a base already disputing recurring "
              "charges (DCS-5001). DCS-4944 shows the idempotency pattern already "
              "exists in-house for Subly renewals."),
        ("p", "External dependency worth naming  —  carrier-side delivery "
              "idempotency, since double-delivering a top-up is direct COGS with no "
              "revenue against it. Polling needs a load estimate against DCS-5252 "
              "(Stripe RPS spikes, In Progress, High). No epic sponsors this today; "
              "a TPM has to create one."),
        ("p", "First ticket  —  [BE] IMTU — Resolve one month of queued and "
              "no-status orders to their terminal state (data pull)"),

        # ---- 11
        ("h3", "Idea 11 — Pre-payment number and carrier validation"),
        ("p", "~$82k/yr gross, minus an unknown per-query cost · Effort S for the "
              "free slice · APP, BE, Design, QA, TPM"),
        ("p", "Mechanism  —  invalidMsisdnOrWrongCarrier (5,722/month) and "
              "invalidMsisdn (721/month) fail AFTER the charge attempt, for a "
              "condition knowable before it. Move validation upstream to recipient "
              "entry, and when a mismatch is found do not error: auto-select the "
              "correct carrier and show its offers, turning a dead end into a "
              "normal purchase. This is genuinely additive to ideas 2, 9 and 10 "
              "because it draws on a different failure class."),
        ("p", "Sizing  —  SOURCED: 6,443 failures per month against only 472 "
              "change-number retry taps (7.3%), so the existing recovery path is "
              "essentially unused. ASSUMPTION 70% preventable with a "
              "carrier/portability lookup: 4,510 x $1.5218 is ~$82k/yr gross."),
        ("p", "The number that decides it  —  $82k/yr against lookups fired on all "
              "~8.4M annual recipient entries puts break-even at roughly $0.01 per "
              "query. Get that price from K2 or a portability vendor before "
              "committing anything. Portability data quality in HT, DO and Cuba "
              "also makes 70% optimistic, and stale data converts a rare "
              "post-payment failure into a frequent pre-payment block — so soft "
              "warning with override, never a hard block."),
        ("p", "Start with the free slice  —  MSISDN format and prefix validation is "
              "pure in-team APP and BE work: zero marginal cost, zero vendor, zero "
              "third-party data-protection surface. A portability lookup queries a "
              "third party about a phone number belonging to someone who is NOT "
              "IDT's customer, which needs a vendor DPA at minimum. Measure how "
              "much of the 6,443 that alone removes; how large the malformed-number "
              "subset is inside that 6,443 is currently unquantified, so the $82k "
              "cannot be attributed to phase one."),
        ("p", "No epic owns this today; the closest is DCS-4429 (To Do, Low)."),
        ("p", "First ticket  —  [APP] IMTU — MSISDN format and prefix validation at "
              "recipient entry (soft warning, no vendor lookup)"),

        # ================================================================== 5
        ("h2", "5. A free fix, and a kill worth reversing"),
        ("h3", "5.1 Make the new subscription guardrail per-recipient"),
        ("p", "DCS-5289 changes the default-OFF trigger to '1 or more active "
              "subscriptions' — per ACCOUNT. A sender supporting three different "
              "recipients has three legitimate subscriptions, and the new rule "
              "defaults the second and third OFF."),
        ("p", "Scoping the guardrail per RECIPIENT instead protects consent exactly "
              "as well while not suppressing genuine intent. It is free, it is a "
              "one-line change to a condition already being written, and nobody has "
              "quantified how many customers hit the cap (core-logic reference "
              "4.1). Raise it on DCS-5289 before it leaves QA."),
        ("h3", "5.2 BOSS Sender membership was killed on a wrong premise"),
        ("p", "The kill rested on two faults. It compared a self-selecting "
              "subscriber population against the MEAN of all purchasers (2.081 "
              "orders/month) and then treated that selection as fatal — but adverse "
              "selection on a fee-free tier is solved by pricing (price above the "
              "heavy user's expected fee, cap included orders, price by corridor), "
              "not by abandonment. The relevant figure, top-decile fee spend, was "
              "never queried."),
        ("p", "And the Apple 3.1.1 objection is simply wrong: airtime is a "
              "real-world service delivered by a carrier, not in-app digital "
              "content, and BR already bills IMTU subscriptions outside IAP today. "
              "A 15–30% platform cut does not apply. Reopen as a pricing analysis, "
              "not a build."),

        # ================================================================== 6
        ("h2", "6. Method corrections — read before quoting any figure"),
        ("p", "Seven places where this analysis presents something firmer than it "
              "is. They change how the numbers should be used; they do not sink the "
              "ideas."),
        ("b", "$1.5218 is the measured FEE, not IMTU's revenue per order. Carrier "
              "commission is admitted unquantified and then forgotten in the "
              "ranking, which systematically under-prices every face-value idea (6, "
              "7, 8) against the fee ideas, because commission scales with face."),
        ("b", "'Flat 15% of face' is inferred from one rung and is contradicted by "
              "the catalog's own 0–25% per-offer dispersion. The '+$1 face = +$0.15 "
              "fee' conversion rests on the contested reading."),
        ("b", "Idea 4's cap arithmetic applies a per-order cap to a mean discount. "
              "If the distribution is bimodal the saving is much smaller than the "
              "mean implies. Get the distribution."),
        ("b", "Idea 10's 21,810 residual is within event-loss noise — a "
              "subtraction across taps and screen views with different "
              "denominators. Inference, not measurement."),
        ("b", "The 94.0% cancel completion is a single week and is not reconciled "
              "against the established ~97% confirm-yes; events versus unique users "
              "is unstated."),
        ("b", "Nothing here is priced net of payment-processing cost, which is "
              "unknown and itself ad-valorem — so idea 3's true increment is under "
              "$0.49."),
        ("b", "No corridor, segment or platform splits anywhere. Eight corridors, "
              "all priced at one blended rate, when fee percentage, face value, "
              "decline rate, cancel rate, promo attach and non-USD exposure all "
              "vary by corridor. One query would re-rank this list. There is also "
              "no new-versus-returning, frequency-decile or tenure segmentation, "
              "and no iOS/Android split — which matters because DCS-5289 and V2 "
              "ship app-side on a staged rollout, so any A/B readout without a "
              "platform split is confounded."),
        ("p", "The structural gap: nothing here grows demand  —  ten of eleven "
              "ideas convert or retain existing traffic. Request Top-Up (committed "
              "FY27; DCS-4719 is Critical in the open sprint with placeholder spec "
              "links), MTU+ insurance attach (DCS-5079, in flight, appearing in "
              "this analysis only as the source of a consent bug), eGift and eSIM "
              "attach on the already-shipped cross-sell success page, and the "
              "committed Recipient App all received no attention from any lens. "
              "First-purchase activation — where face-value lift is largest — has "
              "no idea attached to it at all."),

        # ================================================================== 7
        ("h2", "7. What could not be quantified, and the data that would settle it"),
        ("p", "The first three are gates rather than risks: one decides whether "
              "idea 4 is worth half a million or zero, and two of them scale or cap "
              "idea 1."),
        ("table", "UNKNOWNS"),

        # ================================================================== 8
        ("h2", "8. Deliberately excluded"),
        ("p", "Ideas that survived ideation and did not survive the judges, listed "
              "with their reasons because the reasons are reusable."),

        ("h3", "8.1 Tier the 15% fee off 'the natural price experiment already in "
               "production'"),
        ("p", "The 0–25% fee dispersion is a per-offer catalog setting, "
              "deterministically correlated with corridor, carrier and offer type, "
              "so there is no within-cell variation and no elasticity is "
              "identifiable however many covariates you add. The leakage half also "
              "fails its own arithmetic: the $10 rung shows 332 zero-fee orders "
              "while the monthly total is 23,294, so zero-fee orders are "
              "concentrated in OTHER rungs and the ~$143k extrapolation is "
              "unreliable in an unknown direction. The 0% and 10% cohorts are far "
              "more likely carrier caps or partner deals than leakage. And the "
              "pricing half IS Variable Fees (S5), already committed."),

        ("h3", "8.2 Fee rebate for wallet-funded top-ups"),
        ("p", "A price cut on the $12.75M/yr fee line to buy a processing saving "
              "nobody has priced. The ACH/pay-by-bank load leg the whole "
              "amortisation rests on does not exist and is a new payment "
              "integration; the amortised wallet cost was understated 6–12x by its "
              "own inputs ($0.06–0.13 per order, not $0.01); DCS-2842 is still an "
              "open epic with only its children Done and BOSS Cash flag-gated; and "
              "it needs money-transmitter and escheatment review plus the same "
              "fraud sign-off that has left DCS-4461 and DCS-4463 unassigned for "
              "months."),

        ("h3", "8.3 Cost-side FX on non-USD offers"),
        ("p", "Real hygiene, but every input to the $220k is assumed and the "
              "direction is probably backwards: for chronically depreciating "
              "corridor currencies a stale periodic rate makes USD cost "
              "OVERSTATED, so 'recovery' means cutting prices. All of the work also "
              "lives inside a catalog with no Jira path for DCS. Not to be confused "
              "with idea 8, the sell-side spread, which is a different and live "
              "lever. Worth asking the catalog owners for a read-only export of "
              "offer FX settings plus 90-day realised drift by corridor — that "
              "request is the whole deliverable."),

        ("h3", "8.4 Silent decline cascade to a second instrument"),
        ("p", "Consent risk mapped directly to a card-network dispute reason code, "
              "layered on a path that already over-retries, behind a fraud gate. "
              "Kept only as the user-confirmed one-tap variant inside idea 2."),

        ("h3", "8.5 Apple Pay / Google Pay as a revenue idea"),
        ("p", "About $61k/yr of card-entry declines for an M–L build with four "
              "external dependencies and a predecessor already closed Won't fix "
              "(DCS-3877); DCS-5238 is Low priority and unassigned; and it is "
              "competitive parity with Ding, not differentiation. Keep the "
              "sequencing recommendation, which is free and correct: ship DCS-5249 "
              "(one-time flow) as its own release ahead of DCS-5250 (subscription "
              "token storage), because DCS-5250 inherits the Confluence 5021925393 "
              "fraud/CVV constraint that has already stalled DCS-4461 and DCS-4463. "
              "The unsized lever worth a look is network-tokenised credentials "
              "lifting authorisation across the whole 14.35% failure rate, not the "
              "6,672-order card-entry subset — and note that off-session wallet "
              "handle reuse is part of what idea 1 would port from the calling "
              "platform."),

        ("h3", "8.6 Behaviour-derived subscription cadence, as a revenue idea"),
        ("p", "Correct diagnosis, wrong ledger: weekly to monthly cuts renewals "
              "roughly 4x for the 87% who do not cancel — an ~18,800-renewal loss "
              "per weekly cohort against ~494 subscriptions retained. Reframed in "
              "section 2 as the structural trust fix under the toggle-fragility "
              "note."),

        ("h3", "8.7 Cancelled-subscriber win-back campaign"),
        ("p", "Arrived unsized, with no revenue math at all, and the audience is "
              "the worst available: with 95.5% of toggle taps switching it off and "
              "94.0% of cancel intents completing, this pool is dominated by people "
              "undoing something they never chose. Re-soliciting them while "
              "DCS-5277 is open is a complaint generator, and it is unambiguously "
              "marketing, so TCPA prior express written consent applies rather than "
              "transactional footing. WhatsApp-first is also not a channel BR has — "
              "it is unbuilt candidate A8, so that framing turns a one-quarter "
              "campaign into a Meta Business API onboarding programme. Note the "
              "distinction from idea 1: dunning messages to CURRENTLY FAILING "
              "subscribers are transactional and are a different, legitimate "
              "population. If a win-back ever runs: push/SMS, with a hard "
              "suppression rule excluding anyone whose subscription was "
              "toggle-created and cancelled inside 30 days."),

        ("h3", "8.8 Out-of-session decline recovery, as a standalone initiative"),
        ("p", "About $57k/yr is below this list's noise floor for an idea that is "
              "unmeasurable while DCS-5260 is open (notification-service messages "
              "are not tracked in Amplitude at all), carries a TCPA "
              "re-characterisation risk, and overlaps DCS-5291 which is already In "
              "Progress. The rails are Done — DCS-5035 (personalised "
              "recipient/offer details), DCS-4966 and DCS-5034 (deep link to Offer "
              "Confirmation from SMS and push), DCS-2421 (abandoned-cart Braze for "
              "BR) — so folding it into idea 2 as the notification branch is cheap. "
              "Two gates if it runs: TCPA/CTIA re-characterisation as marketing, "
              "and DCS-4949, which exempts subscribers from validity notifications "
              "and may silently swallow the trigger."),

        # ================================================================== 9
        ("h2", "9. The total — do not sum the list"),
        ("table", "TOTAL"),
        ("p", "Ideas 2, 9, 10 and 11 draw on the same 128,991/month failure pool, "
              "and idea 3 competes with any fee-rate increase for the same "
              "headroom. Outside ideas 3 and 4 the POOLS are sourced and the "
              "CONVERSION RATES are all assumptions until the first A/B reports."),
        ("p", "If you take one thing from this document  —  idea 1 is the only item "
              "whose pool is measured, whose population does not overlap anything "
              "else, and whose fix is mostly a port of code that already runs on "
              "the calling platform."),

        # ================================================================= 10
        ("h2", "10. Sources"),
        ("p", "Amplitude (org BOSS 127967, BR app Prod 650506): yf63oi1y fee per "
              "order · qjl4da1e and 7ze3ftsy fee schedule and distribution · "
              "vbm1x184 denomination mix · 9tojtd0c discount attach · oarm1oig "
              "average discount · rufqfadk average fee on discounted orders · "
              "9wxtpq92 cancel funnel · exfxfy3d cadence mix · 6gu681ly renewal "
              "interval · 8jhc3wbs purchases and fee per purchaser."),
        ("p", "Confluence: 5854003362 Subscriptions Last Transaction Status "
              "Analysis · 5108269167 Offer Setups and Costs · 5000626416 offer/FX "
              "configuration · 4484628828 Handling Offer Costs · 5021925393 Fraud "
              "Check for Subscriptions · 5327421441 MTU Subscription Cancellation "
              "(Incident) · 6129057864 MTU subscriptions - Push notifications · "
              "5850923041 What is being migrated to Subly."),
        ("p", "Jira: DCS-5289 · DCS-5297 · DCS-5277 · DCS-5001 · DCS-5299 · "
              "DCS-5318 · DCS-5319 · DCS-5320 · DCS-5321 · DCS-5303 · DCS-5081 · "
              "DCS-5293 · DCS-5148 · DCS-3997 · DCS-5217 · DCS-5045 · DCS-5110 · "
              "DCS-5257 · DCS-5258 · DCS-5050 · DCS-4983 · DCS-4992 · DCS-1667 · "
              "DCS-3539 · DCS-4944 · DCS-5252 · DCS-5178 · DCS-4204 · DCS-4442 · "
              "DCS-5074 · DCS-3914 · DCS-3466 · DCS-4429 · DCS-5260 · DCS-5291 · "
              "DCS-5035 · DCS-4966 · DCS-5034 · DCS-2421 · DCS-4949 · DCS-3921 · "
              "DCS-2842 · DCS-4461 · DCS-4463 · DCS-3877 · DCS-5238 · DCS-5249 · "
              "DCS-5250 · DCS-4719 · DCS-5079 · DTCBE-2686 · CRMC-3299 · "
              "IDTPAY-3912 · ADMI-9099."),
        ("p", "Workspace files: IMTU_FY27_Plan.md · IMTU_FY_Roadmap.md · "
              "IMTU_Subscriptions_FY27.md · MTU_Competitor_Landscape.md · "
              "CrossCutting_FY_Roadmap.md · create_core_logic_doc.py (the IMTU "
              "Subscriptions Core Logic Reference) · crypto_screens/s7.html."),
        ("p", "Provenance note  —  the ranked list is the output of a multi-agent "
              "pass, not of a single reading. Where the judges or the completeness "
              "critic corrected the ideation stage, the correction is stated in "
              "place rather than silently applied, so a reader can see which claims "
              "were revised and why."),
    ]
    return b


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)

    print("Creating document...")
    doc_id = docs.documents().create(body={"title": TITLE}).execute()["documentId"]

    body = blocks()
    print(f"  {len(body)} blocks")
    batched(docs, doc_id, build_requests(body))

    print("Inserting unknowns table...")
    print(f"  inserted: {insert_table(docs, doc_id, 'UNKNOWNS', UNKNOWNS_TABLE)}")

    print("Inserting totals table...")
    print(f"  inserted: {insert_table(docs, doc_id, 'TOTAL', TOTAL_TABLE)}")

    print("\nDONE")
    print(f"https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
