#!/usr/bin/env python3
"""
Creates ONE Google Doc: "ClearSale Demo: Prep Notes (DCS seat)".

Prep for the ClearSale (Experian) demo, Tuesday 29 September 2026, 11:30 EST.
Attendees on the IDT side: Diana Scolari (commercial), Joao Tanaka and
Ana Jishkariani (introduced to ClearSale as "the development team").

Written for Joao's seat specifically. Diana owns price and contract. Joao owns
the question of whether this thing can be wired into the DTC eGift flow at all,
and what it would cost DCS to do it.

Carries forward the verified findings from the nSure.ai / Riskified evaluation
(eGift_Fraud_Vendor_DCS_Plan.html, 15 Sep 2026), because they apply to any
vendor and they change what a good answer sounds like:

  - IDT Pay's decisioning is Accertify, a third party. At least five gates
    decline an eGift purchase independently.
  - 89.9% decline Mar-Jul 2026, but 41.2% is issuer declines no vendor converts
    and only 1.9% is velocity. 55.3% is an opaque bucket nobody has split.
  - EGIFT-858 disabled Visa on DTC on 2026-08-28 and was never reverted.
  - DCS cannot hold a transaction: there is no async review state to put a
    "pending analyst review" verdict into.

Two facts checked on the morning of 29 Sep 2026: ClearSale and Experian appear
nowhere in IDT Jira or Confluence, and EGIFT-858 is still Closed with no revert
ticket, so Visa has been off DTC for 32 days.

Companion: eGift_Fraud_Vendor_DCS_Plan.html and its Google Doc.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from linkify_refs import linkify, LINK_MAP

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

TITLE = "ClearSale Demo: Prep Notes (DCS seat)"

WIKI = "https://idtjira.atlassian.net/wiki/spaces"

EXTRA_LINKS = {
    "IMTU Wallet: Accertify Fraud Integration":
        f"{WIKI}/DCS/pages/5671944225/IMTU+Wallet+Accertify+Fraud+Integration+-DRAFT",
    "eGIFT in DTC: Anti Fraud Rules":
        f"{WIKI}/DCS/pages/3574890503/eGIFT+in+DTC+Anti+Fraud+Rules",
    "ShieldWall 2.0":
        f"{WIKI}/DPC/pages/5720932375/ShieldWall+2.0",
    "Preliminary Design Review":
        f"{WIKI}/TEAM/pages/371037206/Preliminary+Design+Reviews+Architecture+Review",
    "Amplitude project 650506":
        "https://analytics.amplitude.com/boss/project/650506",
}
LINK_MAP.update(EXTRA_LINKS)

# ---------------------------------------------------------------- tables ----

# T1: what to put on the table early, so their pitch is aimed at the real problem
FRAME = [
    ["State this early", "Why you say it"],
    ["Our baseline is 89.9% decline over 1 March to 31 July 2026, not the number you may have been given.",
     "Any September figure is inflated by about 7 points because we disabled Visa on DTC ourselves on 28 August and have not reverted it. If they price off a contaminated number, both sides waste the evaluation."],
    ["41.2% of our eGift failures are issuer card declines. Only 1.9% carry a velocity or limit code.",
     "This is the single most important thing they need to hear. No fraud vendor converts an issuer decline, so the addressable pool is far smaller than the headline. It also forces an honest answer on what they actually expect to recover."],
    ["55.3% of failures are an opaque \"failed\" bucket we have not yet split by response code.",
     "Says plainly that the addressable pool is bounded above by that bucket and is currently unknown inside it. Anyone quoting a guaranteed uplift before we split it is guessing."],
    ["Decisioning today is not an internal rules table. It is Accertify, called from inside IDT Pay.",
     "They will pitch against \"your internal rules\". The real incumbent is a competitor product already contracted and PCI-integrated at IDT. Expect a sharper answer on what they replace."],
    ["An eGift purchase can be declined at up to five independent gates, and a vendor replaces one or two of them.",
     "Fraudzilla velocity, Jube, IDT Pay and Accertify, K2's own velocity and location screens, and ShieldWall, which fails closed on timeout. Their approval does not produce an approved transaction on its own."],
    ["Our app is a single Flutter codebase, not native iOS and Android.",
     "They said they have a Mobile SDK. Establish on the call whether that means a Flutter plugin or a wrapper we would have to build and pay for."],
    ["We cannot hold a transaction today. There is no async review state in the eGift flow.",
     "This is the constraint that matters most against their model, and it is the one thing in this document only you and Ana can say."],
]

# T2: the eight questions ClearSale did not answer in the 15 Sep email
UNANSWERED = [
    ["#", "Question they skipped", "What a good answer sounds like"],
    ["5", "Review-team hours and coverage. 24/7, or does turnaround vary by time of day and region?",
     "A specific coverage window with a named SLA per window. Our buyers transact at any hour from a phone. \"We tailor to your business requirements\" is not an answer to this."],
    ["9", "Exactly which transaction types are excluded from the guarantee: card types, countries, denominations, first-time buyers, promo or bonus balances, non-card rails.",
     "A written exclusion list. Push hard here: our documented fraud vector is account takeover on the customer's own saved card, which frequently sits outside standard fraud-liability cover."],
    ["10", "Approval and chargeback rate specifically on gift cards and digital goods, not a blended average.",
     "Two numbers with the merchant category and time window attached. A blended figure across 100,000 merchants tells us nothing about an irrecoverable cash-equivalent product."],
    ["11", "Minimum volume and evaluation window before they will commit to a contractual approval-rate guarantee for eGift.",
     "A volume threshold and a number of weeks. If the window is short, ask how they account for chargeback lag, which runs far longer than the window."],
    ["12", "Can they run a POC or shadow-mode pilot against our historical transactions before we sign?",
     "Yes, with a described method. This is the highest-value question on the list. If pre-contract is impossible, get the closest equivalent during onboarding, in writing."],
    ["14", "Typical end-to-end integration timeline from signature to live production decisioning at full liability.",
     "Two separate numbers: time to first decision, and time to full liability coverage. Vendors habitually quote the first and let you assume it is the second."],
    ["15", "Compliance certifications, whether they receive full card data, and their PCI scope.",
     "SOC 2 report available under NDA, and a precise statement of which card data elements they require. BIN, last four and expiry are cardholder data even though they are not a full PAN."],
    ["16", "Process and timeline for submitting and resolving a guarantee or chargeback claim.",
     "A described workflow with a decision SLA and an appeal path. This is the clause that decides whether the guarantee is real in practice."],
]

# T3: questions that only arise because this vendor is ClearSale
CLEARSALE = [
    ["Question", "Why it matters here specifically"],
    ["Your differentiator is the analyst team. If we take the automatic real-time path you offered for digital goods, what changes: the approval rate, the guarantee, or the price?",
     "The most important question in the meeting. Their value is partly human review. Strip it out for a mobile checkout and you may be buying a materially different product at the same price. Get all three answers, not one."],
    ["On the auto-decision path, what is the p50 and p99 decision latency, and what is the timeout behaviour?",
     "Our checkout is a consumer mobile flow. Also ask what their API returns on their own outage, because fail-open and fail-closed are both expensive here and the choice is a contract term, not a default."],
    ["Does your verdict set include anything other than approve and decline? A review, a hold, a step-up?",
     "If yes, we cannot consume it today. Say so in the meeting. Building a hold-and-resume state is unbudgeted DCS work and it would land on the critical path."],
    ["If a transaction goes to analyst review, what does the buyer see in the app while they wait?",
     "There is no good answer for a gift-card checkout. Asking it out loud is how you find out whether they have ever done a real-time consumer mobile flow, or only ecommerce with a shipping delay."],
    ["As part of Experian, where does our customer data go? Does any of it enter Experian's wider data estate or any bureau product?",
     "A materially bigger privacy question than with a standalone vendor, and one our Legal team will ask before it signs. Get the answer on the record now rather than in week five."],
    ["Is anything you do with our data a consumer report or an FCRA-regulated product?",
     "Ask it plainly and let them answer. If any part of the decision touches bureau data, the compliance path is different and longer. Better to know today."],
    ["Does IDT already have an Experian master agreement we could contract under?",
     "If yes, this could shorten contracting by weeks. Nothing in Jira or Confluence records an Experian relationship, so the answer has to come from them or from Legal."],
    ["You asked Diana for our mutual NDA. Who signs on our side, and how quickly can you turn it round?",
     "The NDA gates every useful technical conversation, including any historical-data POC. It is the first real date in the schedule."],
    ["What do you need from us to quote, and can you quote without customer PII leaving IDT?",
     "IDT has no outbound DPA template where IDT is the controller and the vendor the processor. If they can quote on aggregates, that removes the least predictable gate in the whole timeline."],
]

# T4: the integration questions that are genuinely yours, not Diana's
INTEGRATION = [
    ["Question", "What you are really testing"],
    ["Is the decision available server-side only, with no SDK required?",
     "If yes, the app release train comes off the critical path entirely and a pilot can run without shipping a binary. This single answer is worth more to the schedule than anything else in the demo."],
    ["Is your Mobile SDK a Flutter plugin, or native iOS and Android that we wrap ourselves?",
     "We are a single Flutter monorepo shared with three other app teams. A wrapper is unbudgeted work on a bench of three developers, and a native SDK touches pubspec, Podfile, build.gradle and Info.plist across four app targets."],
    ["What data classes does the SDK collect, and have your merchants had to add a Google Play prominent-disclosure screen for it?",
     "A new data class means a disclosure screen shown before the SDK initialises, plus store re-review. This gate is the one that slips, and we already have it failing on another live vendor migration."],
    ["Can we disable your decisioning instantly from our side, without an app release?",
     "Our kill switch has to be ours. A native SDK starts before Dart on Android and at plugin registration on iOS, so a remote flag cannot stop it in the launch where we need it."],
    ["Can your decision be scoped to one product, so eGift changes while IMTU and eSIM stay on the incumbent path?",
     "eGift, IMTU and eSIM share one payment path and one admin surface. Blast-radius containment is a hard requirement, not a preference."],
    ["How do you want chargeback outcomes fed back, and at what latency?",
     "This is a recurring server-side integration with our acquirer and billing, not a one-off. It is also the feed their guarantee depends on, so ask what happens to the guarantee if the feed breaks."],
    ["How do you define an approved transaction for billing purposes?",
     "Our fulfilment layer can decline after you approve. If \"approved\" means their verdict rather than our fulfilment, we pay on transactions that never completed."],
    ["What do you give us for monitoring: approval rate, decline reasons, latency, availability?",
     "We have no fraud dashboard today, so anything they supply is a genuine saving. If they supply nothing, that is net-new DCS build we have to schedule."],
    ["Who do we call at 2am when decisioning is down, and what is the support model?",
     "Establishes whether there is a named technical counterpart or only an account manager."],
]

# T5: traps
TRAPS = [
    ["Trap", "How to handle it"],
    ["They quote an approval-rate uplift against our 89.9% decline.",
     "Any uplift claim has to be against the addressable pool, not the headline. Ask them to restate it excluding issuer declines. If they cannot, that tells you what the number was worth."],
    ["\"We are flexible on contract terms and minimums.\"",
     "Diana's ground. Your job is to make sure flexibility on price does not quietly buy a scope we cannot build against, for example a model that needs a review state."],
    ["A percentage of approved GMV sounds cheap.",
     "It is charged on the whole approved base, including transactions we already approve. On a 3 to 8% gift-card commission, 1% takes an eighth to a third of gross margin on every sale. Flag it, then leave the number to Diana and Finance."],
    ["They offer a pilot that reads out in four weeks.",
     "Fraud labels arrive about two weeks late and scheme chargebacks far later, so a four-week read-out cannot yet have seen the fraud it let through. Ask for the read-out date to be set separately from the traffic-stop date."],
    ["\"We will review that in the demo\" turns into a slide, not an answer.",
     "Eight questions from 15 September are still unanswered. If a slide does not answer one, say so in the room and ask for it in writing. Ricky already committed in email to covering several of them today."],
    ["The demo becomes a product tour.",
     "You have two things to get: whether they can decision server-side, and what their verdict set is. If the clock runs down, ask those two and let the rest go to email."],
]

TABLES = [
    ("T1", FRAME), ("T2", UNANSWERED), ("T3", CLEARSALE),
    ("T4", INTEGRATION), ("T5", TRAPS),
]

# ---------------------------------------------------------------- content ---

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Tuesday 29 September 2026, 11:30 EST  ·  ClearSale (Experian): Ricky Sunzeri, Faye McEachern, Rafaela Fernandes  ·  IDT: Diana Scolari, Joao Tanaka, Ana Jishkariani"),

    ("h2", "Your job in this meeting"),
    ("p", "Diana owns price, contract and the vendor relationship. You and Ana were brought in as the development team, so the useful thing you can do is answer one question the commercial track cannot: can this be wired into the DTC eGift flow at all, and what would it cost DCS to do it."),
    ("p", "If the clock runs out and you only get two answers, get these. First, can ClearSale decision server-side with no mobile SDK required. That single answer decides whether the app release train sits on the critical path, and it is worth more to the schedule than anything else in the demo. Second, what is in their verdict set. If it is anything other than approve and decline, we cannot consume it today."),

    ("h2", "Put these on the table early"),
    ("p", "They are pitching against a picture of our problem that is wrong in three specific ways. Correcting it in the first ten minutes gets you a better demo, because their solutions engineer can aim at the real thing."),
    ("table", "T1"),

    ("h2", "Eight questions they never answered"),
    ("p", "Diana sent sixteen questions on 15 September. Ricky answered eight, in part, and deferred the rest to this demo. These are the eight with no answer at all, and they are the ones that decide whether this vendor is viable. Ricky committed in writing to covering several of them today, so it is fair to hold him to it."),
    ("table", "T2"),

    ("h2", "Questions this vendor raises that the others did not"),
    ("p", "ClearSale is a different shape from the two vendors we looked at in September. It is human-review-led rather than pure model, and it is owned by Experian. Both facts create questions that were not on Diana's original list."),
    ("table", "T3"),

    ("h2", "The integration questions that are yours"),
    ("table", "T4"),

    ("h2", "Traps"),
    ("table", "T5"),

    ("h2", "What a good meeting looks like"),
    ("n", "You know whether they can decision server-side without an SDK, and whether their SDK is Flutter or native."),
    ("n", "You know their full verdict set, and you have told them plainly that we cannot consume a review or hold state today."),
    ("n", "You have a written commitment on a pre-contract POC against historical data, or a clear no with the nearest alternative."),
    ("n", "You have the gift-card-specific approval and chargeback rates, or a date by which they will send them."),
    ("n", "You have the guarantee exclusion list, and an explicit answer on whether account takeover on a customer's own saved card is covered."),
    ("n", "Diana has what she needs to move the NDA, which gates everything technical that follows."),

    ("h2", "Two things to raise internally, separately from this call"),
    ("b", "Visa is still disabled on DTC eGift.  ·  EGIFT-858 was closed on 28 August and there is still no revert ticket, so it has been off for 32 days. It costs nothing to re-enable, it is worth about seven points of approval rate, and it is the honest control arm against any vendor's claim. It also contaminates any data pack we hand a vendor for pricing."),
    ("b", "There are now three vendors and still no decision paper.  ·  nSure.ai, Riskified and ClearSale, and none of them appears anywhere in Jira or Confluence. The only tracking artefact is EGIFT-861. A decision of this shape, assigning chargeback liability to a third party and removing decisioning from IDT Pay, triggers the Preliminary Design Review process on three independent grounds, and the PDR is what compels IDT Pay and CAF into the room."),

    ("h2", "Numbers to have in front of you"),
    ("b", "89.9% decline  ·  1 March to 31 July 2026, the clean window. 300 successes against 2,667 failures. Use this, never a September figure."),
    ("b", "41.2% issuer declines  ·  1,100 of those 2,667. Declined, no credit, invalid, restricted, expired. No fraud vendor converts these."),
    ("b", "1.9% velocity or limit  ·  50 of 2,667, and they fire as a seven-day incident response rather than a standing constraint."),
    ("b", "55.3% opaque  ·  1,475 of 2,667, reason recorded only as \"failed\". The addressable pool is bounded above by this bucket and is currently unknown inside it."),
    ("b", "About 7 points  ·  The contamination from the Visa disable. 89.1% decline in the fortnight before 28 August, 96.1% in the fortnight after."),

    ("cap", "Figures from Amplitude project 650506, re-run 15 September 2026. Jira state checked the morning of 29 September 2026."),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}

LEAD_SEP = "  ·  "


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


def ulen(text):
    """Docs indices count UTF-16 code units, not Python characters."""
    return len(text.encode("utf-16-le")) // 2


def build_requests(blocks):
    reqs, cur = [], 1
    for kind, text in blocks:
        if kind == "table":
            line = f"[[{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += ulen(line)
            continue

        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        para = {"namedStyleType": STYLE_MAP[kind]}
        fields = "namedStyleType"
        if kind == "cap":
            para["alignment"] = "CENTER"
            fields += ",alignment"
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + ulen(line)},
            "paragraphStyle": para, "fields": fields}})

        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind == "n":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(line)},
                "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"}})
        if kind == "cap":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(text)},
                "textStyle": {"italic": True,
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}})
        if kind in ("b", "p") and LEAD_SEP in text:
            lead = text.split(LEAD_SEP)[0]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(lead)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        cur += ulen(line)
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
    """Replace the [[marker]] placeholder with a real Docs table."""
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = plen = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[{marker}]]":
            idx, plen = el["startIndex"], ulen(para_text(el))
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
    for start, r, c in sorted(cells, reverse=True):   # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + ulen(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        elif marker == "T2" and c == 0:
            # The original question numbers from Diana's 15 Sep email.
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + ulen(txt)},
                "textStyle": {"bold": True, "weightedFontFamily": {
                    "fontFamily": "Roboto Mono"}},
                "fields": "bold,weightedFontFamily"}})
        elif c == 0:
            # First column is the question or the claim: keep it prominent.
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + ulen(txt)},
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

    linkify(docs, doc_id)

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
