#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU Duplicate Subscriptions: Analysis and Cleanup Plan".

Analysis of the "Copy 2 of Duplicates" spreadsheet
(1Y9Hz8-uZfiSWv1q56E8f_trMhyXJWvMQ9j3IKW3FK2k), which holds 27,256 duplicate
IMTU subscription timers across 5,807 recipient+offer groups and 3,644 owners.

The headline finding inverts the proposed plan. The plan deletes 16,501 failing
timers that charge nobody and explicitly preserves every active one, but 3,469
of those active timers are surplus duplicates that are billing 1,094 customers
right now, roughly $339k a year on a face-value estimate.

Every number was computed directly from the extract. Where an adversarial review
disagreed with a first-pass number, the corrected number is what appears here,
and where the review itself was wrong (the February-break claim) that is stated.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from linkify_refs import LINK_MAP, linkify

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

TITLE = "IMTU Duplicate Subscriptions: Analysis and Cleanup Plan"

SHEET = ("https://docs.google.com/spreadsheets/d/"
         "1Y9Hz8-uZfiSWv1q56E8f_trMhyXJWvMQ9j3IKW3FK2k/edit")

DOC_LINKS = dict(LINK_MAP)
DOC_LINKS.update({
    "Copy 2 of Duplicates": SHEET,
    "source spreadsheet": SHEET,
})

# ---------------------------------------------------------------- tables ----

STATE = [
    ["Timer state", "Timers", "Share", "Completed purchases", "What it means"],
    ["failing (launches, no purchase for 2+ periods)", "21,343", "78.3%", "33,369",
     "Still firing on schedule, not collecting. 79% have a future launch date."],
    ["active (purchasing)", "5,333", "19.6%", "34,557",
     "Collecting normally. 3,469 of these are surplus duplicates."],
    ["no launches found", "580", "2.1%", "0",
     "Brand new. All created since 4 June 2026, 579 with a future launch date. Not dead."],
    ["Total", "27,256", "100%", "67,926", ""],
]

BILLING = [
    ["", "Count", "Detail"],
    ["Groups with 2 or more active timers", "1,387", "same owner, recipient, offer and recurrence"],
    ["Surplus active timers (all but the oldest)", "3,469", "these are the duplicate charges"],
    ["Customers affected", "1,094", "worst single account has 43 on one recipient"],
    ["Purchases already taken by surplus timers", "21,142", "61% of all active-timer purchases"],
    ["Surplus timers that charged in the last 30 days", "1,894", "this is live, not historical"],
    ["Surplus timers firing again within 30 days", "1,958", "will charge again unless stopped"],
    ["Estimated annual duplicate billing", "about $339,000", "face value parsed from offer_id, estimate only"],
    ["Estimated already charged", "about $152,000", "same method, same caveat"],
]

WAVES = [
    ["Wave", "What", "Timers", "Revenue argument", "Risk"],
    ["0", "Fix the k2 double-fulfilment pairs first (separate sheet, 6,217 owners, deterministic: drop the 2nd id)",
     "7,256 pairs", "None, it is a system bug", "Lowest. Hold out the 70 ids that collide with this plan."],
    ["1", "Stop the live double billing: cancel the 3,469 surplus active timers, keep the oldest per group",
     "3,469", "Negative, this is money we should not be taking", "Needs a billing decision on refund or proration"],
    ["2", "Cancel duplicates in the 1,678 groups where no timer ever purchased, plus timers on the 256 retired offers",
     "7,645", "None, zero purchase history", "Near zero. No keeper judgement needed."],
    ["3", "The remaining failing duplicates that do carry purchase history",
     "8,856", "Historical only, median 348 days since last charge", "Needs the keeper rule and a support script"],
]

PREMISES = [
    ["Your premise", "Verdict", "What the data says"],
    ["Most of these started before 2023", "Wrong",
     "Zero timers predate 2024. Earliest is 16 Jan 2024. By year: 2024 8,607, 2025 12,728, 2026 5,921."],
    ["Most of them are failing", "Right",
     "78.3% failing, 19.6% active, 2.1% too new to have launched."],
    ["Users deleted the card so they would not be charged", "Half right",
     "65.5% of failing timers show a card-absent cause. But 3,804 of them collected for a median 168 days first, so these are mostly broken paying subscriptions, not never-wanted ones."],
    ["Keep all active ones, they generate revenue", "Backwards for 3,469 of them",
     "Those are surplus duplicates double-billing 1,094 customers. The rest, 1,864 timers, are the genuine revenue base."],
    ["The March 2026 UI changed behaviour", "Timing fits, cause is confounded",
     "Duplicate creation fell 52% from March to April. But the same release also changed the recurrence default from 3 months to 1 month, and the two cannot be separated here."],
    ["Users do not trust the app", "Untestable here",
     "Nothing in the extract distinguishes deliberate card removal from expiry, reissue or a failed token migration. canceled_reason is blank on all 27,256 rows."],
]

TABLES = [("STATE", STATE), ("BILLING", BILLING), ("WAVES", WAVES), ("PREMISES", PREMISES)]

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("p", "Analysis of the source spreadsheet: 27,256 duplicate IMTU subscription "
          "timers across 5,807 groups (same owner, recipient, offer and recurrence) "
          "and 3,644 customers. Every group in the extract has at least 3 timers. "
          "All figures below were computed directly from the extract, dated 4 "
          "September 2026."),

    ("h2", "The finding that changes the plan"),
    ("b", "The plan protects the only timers that are costing customers money. It "
          "deletes 16,501 failing timers, which charge nobody, and explicitly leaves "
          "every active timer alone. But 3,469 of those active timers are surplus "
          "duplicates: 1,387 groups have two or more timers actively collecting on "
          "the same recipient and the same offer. They belong to 1,094 customers, "
          "1,894 of them charged in the last 30 days, and 1,958 are scheduled to "
          "charge again within 30 days."),
    ("b", "The worst account is not a long tail case. Owner 7aqie3a1b4a7 has 43 "
          "simultaneously active timers on one phone number (+50488693565) for one "
          "offer (CLARO_HN_7-SUPERPACK) on a 3 month cycle. 172 of that account's "
          "182 timers are active, which is why the proposed rule only takes them from "
          "182 subscriptions to 174."),
    ("b", "Order of magnitude: roughly $339,000 a year of duplicate billing, with "
          "about $152,000 already charged. That is an estimate built by parsing the "
          "dollar figure out of the offer_id string (CLARO_HN_7 reads as $7), because "
          "the extract has no price column. Treat it as a scale indicator that "
          "justifies pulling a real number, not as a finance figure."),
    ("b", "So the sequence should invert. Stop the 3,469 live duplicate charges "
          "first, then tidy the failing rows. Shipping the deletion on its own leaves "
          "every double charge running and removes the evidence trail on the other side."),

    ("h2", "What the population actually looks like"),
    ("table", "STATE"),
    ("b", "\"Failing\" does not mean \"never worked\". 7,641 of the 21,343 failing "
          "timers (35.8%) completed at least one purchase, and failing timers account "
          "for 33,369 completed purchases between them. The label means \"has not "
          "collected for 2 or more periods\", which is a stopped subscription, not a "
          "fake one."),
    ("b", "They are also not dormant records. 79.4% of failing timers have a launch "
          "date in the future and 53.5% fired in the last 14 days. Of the 16,501 "
          "marked for deletion, 714 are due to fire within 24 hours. Deleting them is "
          "not housekeeping, it is silently cancelling 13,040 armed schedules."),
    ("b", "But they are genuinely dead as revenue. Among failing timers that ever "
          "collected, the median time since the last successful charge is 348 days and "
          "47.5% last charged over a year ago. Only 122 charged within the last 30 "
          "days. Those 122 should simply be excluded by rule."),
    ("b", "The 580 \"no launches found\" timers must not be touched. Every one was "
          "created on or after 4 June 2026 and 579 have a future launch date. They "
          "are new subscriptions that have not reached their first cycle. Any rule "
          "keyed on \"never launched\" would delete the newest and most likely "
          "intentional subscriptions in the file."),

    ("h2", "Live double billing, in detail"),
    ("table", "BILLING"),
    ("b", "It has been going on for a long time. In 2,581 of 5,807 groups (44.4%) "
          "two or more timers were charging over overlapping date windows, 12,621 of "
          "those overlaps lasting 30 days or more, across 1,964 customers. Concurrent "
          "charging is the norm in this dataset, not an edge case."),
    ("b", "Purchase history is spread, not concentrated. Only 721 groups have exactly "
          "one timer that ever collected; 1,642 have three and 1,050 have four or "
          "more. In 3,404 groups the question \"which of these is the real "
          "subscription\" has no answer in the data, so any keeper rule is arbitrary "
          "there and should be presented to support as a convention, not a truth."),

    ("h2", "Your hypothesis, tested"),
    ("table", "PREMISES"),
    ("h3", "Where the card story holds"),
    ("b", "The card signature is real and it is account-level, which is the strongest "
          "evidence for your reading. 13,972 failing timers (65.5%) show a card-absent "
          "cause, missing_card or card_expired. Of the 1,285 owners with such a timer, "
          "only 45 (3.5%) have another timer that collected after that one broke. When "
          "the card goes, it goes for the whole account, which fits removal or expiry "
          "and rules out a per-timer tokenisation bug."),
    ("b", "The handle_id column supports it independently. 2,029 groups (34.9%) span "
          "more than one payment handle, and timers on a superseded handle fail at "
          "86.5% against 74.9% on the current one, carrying missing_card at 64.4% "
          "against 44.8%. People really are re-subscribing on new instruments and "
          "leaving the old subscription attached to a dead one."),
    ("h3", "Where it does not hold"),
    ("b", "The card was usually removed after the subscription worked, not to dodge "
          "it. 3,804 failing timers carry both a missing_card cause and real "
          "purchases: 13,385 completed charges, a median 168 days from creation to the "
          "last successful charge, then a median 334 further days of failed launches. "
          "That is a subscription somebody used for five months and then broke, and "
          "which kept knocking for eleven months afterwards."),
    ("b", "A third of the failing population is not a card story at all. 5,410 of the "
          "deletion candidates (32.8%) failed with no_credit, which is a working card "
          "with no funds. 2,574 (15.6%) have no card-related reason in either column, "
          "and 172 are labelled failing with no recorded cause whatsoever. Those 2,574 "
          "are the rows you will least be able to explain to a caller."),
    ("b", "\"Users do not trust the app\" cannot be tested with this extract, and the "
          "data arguably points the other way: most of these subscriptions collected "
          "money for months before breaking. If you want the motive, it needs a survey "
          "or a session replay, not this file."),

    ("h2", "Did the March 2026 UI fix it?"),
    ("b", "The timing fits precisely. Counting new timers added to already-existing "
          "groups per month, with the December bulk event removed: Jan 995, Feb 897, "
          "Mar 882, then Apr 421, May 389, Jun 412, Jul 578, Aug 437. Month on month "
          "that is -9.8%, -1.7%, then -52.3% between March and April. February and "
          "March are flat; the break is exactly where the release landed."),
    ("b", "But the same release changed the recurrence default, and that is a "
          "competing explanation. The share of new timers on \"3 month\" runs 42%, "
          "42%, 42% in January, February and March, then 31%, 23%, 20%, 13%. \"1 "
          "month\" moves the opposite way, 26%, 29%, 29% then 43%, 48%, 52%, 67%. "
          "Customer taste does not shift 25 points in one month across every country. "
          "That is a default value changing."),
    ("b", "Why it matters: a 1 month default fires three times as often as a 3 month "
          "one, so it changes how fast a group reaches the 3-timer threshold that gets "
          "it into this extract at all. Part of the 52% drop may be that mechanical "
          "effect rather than users understanding the screen better."),
    ("b", "There is also a real relationship between period length and duplication, "
          "which supports the underlying story. Mean group size is 4.91 on 3 month "
          "subscriptions against 4.27 on 1 month, and the share of groups with two or "
          "more concurrently active timers is 28.4% on 3 month, 26.6% on 1 month, "
          "18.5% on 2 week and 11.4% on 1 week. The longer a subscription stays "
          "invisible between charges, the more often somebody re-subscribes on top of "
          "a live one. So moving the default from 3 months to 1 month plausibly helped "
          "on its own merits."),
    ("b", "Honest conclusion: duplicate creation halved and it halved when the "
          "release shipped, but this data cannot separate the new UI from the new "
          "default. Both are plausible and both point the same way. Do not claim the "
          "UI alone caused it. Amplitude can settle it, since the two changes affect "
          "different events."),

    ("h2", "Two things in the data nobody was looking for"),
    ("b", "A bulk system event on 19 December 2025 created 1,266 timers, against a "
          "median of 25 a day. 730 landed in a single hour and 467 of 941 arrived "
          "within a minute of the previous duplicate in their group. It spans 403 "
          "owners and 322 of the timers opened brand-new groups. With 20 and 21 "
          "December it totals 1,802 timers, 6.6% of the whole dataset. That reads as a "
          "migration or backfill, not customer behaviour, and it should be tagged and "
          "excluded from any behavioural analysis of this population."),
    ("b", "256 offers have no active timer anywhere in the file, covering 2,492 "
          "timers (9.1%). These subscriptions cannot succeed no matter what the "
          "customer does with their card, because the offer is retired. The clearest "
          "cases are ORANGECELLCOM_LR_6-I-DATA_B (124 timers), SAFARICOM_KE_5-I (85) "
          "and four offers with no successful purchase on record at all. This also "
          "explains the outliers in failure rate: ORANGECELLCOM_LR_5_FEE is 97.1% "
          "failing against a 76 to 82% band for every other large offer. Worth asking "
          "whether offer retirement has a subscriber migration step at all."),

    ("h2", "The recommended plan"),
    ("table", "WAVES"),
    ("b", "Use a soft cancel, not a delete. The timers table already has canceled_at "
          "and canceled_reason and both are blank on all 27,256 rows, so the "
          "capability exists and has never been used. Setting state to cancelled with "
          "a stamped reason preserves the 18,758 purchases and their foreign keys, "
          "makes the whole operation reversible with one filtered query, gives support "
          "a per-row explanation to read to a caller, and still delivers the entire "
          "operational benefit, since a cancelled timer stops being scheduled."),
    ("b", "Answer one schema question before running anything. The delete set carries "
          "18,758 completed purchases and 592,542 launches. A hard delete either "
          "cascades and destroys the receipts for real charges, or fails on a "
          "constraint and leaves a half-processed dataset, or orphans the purchase rows "
          "so every report that joins purchases to timers silently loses them. Nothing "
          "in the extract tells you which. Read the foreign key definition first."),
    ("b", "Your keeper rule is already the best of the options tested. Keeping the "
          "failing timer with the most purchases destroys 18,758 purchases; keeping "
          "the newest destroys 25,905, which is 38% worse. Keep the rule you have. Note "
          "that it picks a different timer from \"newest\" in 44% of groups, and that "
          "933 of the 4,842 keepers will never fire again."),
    ("n", "Read the foreign key on the purchases table. Everything else waits on this."),
    ("n", "Ship the k2 double-fulfilment fix, holding out the 70 timer ids that "
          "collide with this plan. It is a bigger population (6,217 owners), a "
          "genuine system bug, and the action is deterministic."),
    ("n", "Stop the 3,469 surplus active timers. Get a billing decision on refund or "
          "proration for the 1,094 customers first, and an offer_id to price map, "
          "because the first support question will be how much was taken."),
    ("n", "Soft cancel Wave 2, the 7,645 timers with no purchase history and the "
          "retired-offer timers. No keeper judgement, no revenue argument, and it "
          "recovers a large share of the 512,523 failed launches."),
    ("n", "Only then take Wave 3, with an explicit exclusion for the 122 failing "
          "timers that charged in the last 30 days and manual review of the 2,574 with "
          "no card-related cause."),
    ("n", "Decide the mixed groups deliberately. In 951 groups the rule leaves one "
          "broken timer next to a working one for the same recipient, and 818 of those "
          "keepers still fire. The customer's complaint is \"why do I see two "
          "subscriptions to my mother\" and this answers \"now you see two instead of "
          "five\". Deleting the failing ones outright in groups that already have an "
          "active timer costs 951 more cancellations and gives those users a single "
          "clean row."),
    ("n", "Fix the cause, not just the rows. Per-group dedupe cannot reach the "
          "heaviest accounts, and an interstitial saying \"you already have a "
          "subscription for this number\" plus a per-account cap would. The recurrence "
          "default move from 3 months to 1 month appears to have helped already."),

    ("h2", "Operational traps found while checking the plan"),
    ("b", "The two cleanup plans collide on 70 timers. 26 of the k2 \"remove\" ids are "
          "timers this plan keeps as a group's sole survivor, and 44 k2 \"keep\" ids "
          "fall in this plan's delete set. Run both without a shared exclusion list and "
          "70 customers lose the subscription entirely instead of having it deduped."),
    ("b", "The delete breaks its own audit key. 3,171 of the 16,501 candidates are "
          "their group's first timer, which is the column the source spreadsheet uses "
          "to identify a group. Afterwards 54.6% of groups cannot be joined back to the "
          "authorising sheet, so a run that dies half way is neither resumable nor "
          "auditable. Snapshot the full rows first and batch on the group key."),
    ("b", "handle_id is not per-timer and is a likely cascade surface. There are only "
          "5,805 handles for 27,256 timers, 1,347 span more than one group and 28 span "
          "more than one owner. Under the plan 1,181 handles lose every one of their "
          "timers. If a handle carries a stored payment instrument, orphaning it is not "
          "cosmetic."),
    ("b", "Do not trust list order in the source sheet. The later_timers column is "
          "lexically sorted but chronological in only about 82% of groups, so a script "
          "that treats position as age picks the wrong keeper in roughly one group in "
          "five. Sort by created_at."),
    ("b", "The dedupe key is narrower than the customer's view. 197 groups exist only "
          "because recurrence differs, and 378 owner and recipient pairs carry more "
          "than one offer. Somebody with a 1 month and a 3 month timer to the same "
          "number keeps both under this key and will still ask why they see two. "
          "Whatever key you choose, put it in the support script."),

    ("h2", "What to distrust in this document"),
    ("b", "The dollar figures are estimates from a string parse. Face value comes "
          "from the offer_id text and there is no price, amount or fx column anywhere "
          "in the extract, with currency blank on 39.4% of rows. The counts are exact; "
          "the money is an order of magnitude."),
    ("b", "The extract only contains live timers. canceled_at is blank on all 27,256 "
          "rows and every launching timer last fired between 11 May and 4 September "
          "2026, so cancelled duplicates are filtered out by construction. Nothing here "
          "can say whether customers clean up after themselves, and the true duplicate "
          "population is larger than 27,256."),
    ("b", "It only contains groups of 3 or more. Pairs are excluded, so this "
          "understates how many customers have any duplicate at all."),
    ("b", "Failure reason columns are often empty. 31.9% of failing timers have no "
          "launch reason and 47.8% have no payment reason, so every cause percentage "
          "over the full failing base is a lower bound."),
    ("b", "One reviewer finding was itself wrong and is worth recording. An "
          "adversarial pass concluded the decline began in February, before the "
          "release, using a 60-day follow-up window per group. That window straddles "
          "the ship date and smears the effect backwards. On monthly counts the break "
          "is unambiguously between March and April."),

    ("cap", "Computed from the Copy 2 of Duplicates extract on 4 September 2026. "
            "27,256 timers, 5,807 groups, 3,644 owners. Counts are exact; dollar "
            "figures are parsed estimates."),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}


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
        if kind == "n":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"}})
        if kind == "cap":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(text)},
                "textStyle": {"italic": True,
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}})
        if kind == "b" and ". " in text:
            lead = len(text.split(". ")[0]) + 1
            if lead < 120:
                reqs.append({"updateTextStyle": {
                    "range": {"startIndex": cur, "endIndex": cur + lead},
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


def insert_table(docs, doc_id, marker, data):
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = plen = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[{marker}]]":
            idx, plen = el["startIndex"], len(para_text(el))
            break
    if idx is None:
        print(f"  ! placeholder {marker} not found")
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
        print(f"  ! table {marker} not found after insert")
        return False
    cells = []
    for r, row in enumerate(table_el["table"]["tableRows"]):
        for c, cell in enumerate(row["tableCells"]):
            cells.append((cell["content"][0]["startIndex"], r, c))
    reqs = []
    for start, r, c in sorted(cells, reverse=True):
        txt = data[r][c]
        if not txt:
            continue
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0 or c == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
    batched(docs, doc_id, reqs, size=40)
    return True


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    doc = docs.documents().create(body={"title": TITLE}).execute()
    doc_id = doc["documentId"]
    print(f"Created doc: {doc_id}")

    reqs = build_requests(BLOCKS)
    batched(docs, doc_id, reqs)
    print(f"Inserted {len(reqs)} text requests")

    for marker, data in TABLES:
        ok = insert_table(docs, doc_id, marker, data)
        print(f"  table {marker}: {'ok' if ok else 'FAILED'} ({len(data) - 1} rows)")

    linkify(docs, doc_id, DOC_LINKS)

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
