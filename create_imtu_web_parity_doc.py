#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU — App vs Web Feature Gap".

Inventory of IMTU features shipped in the BOSS app that the IMTU web experience
does not yet have. Built to structure the DCS <-> web team parity conversation
kicked off by Emilio del Rio (25 Aug 2026).

Every feature row is tagged by how it would actually reach web:
  Component  - arrives with the flow-component swap, no extra web work
  Web work   - needs separate web-side platform work regardless of the component
  Moving     - still in flight in the app; do not build against it yet

Source: DCS Jira (epics DCS-3599, DCS-3818, DCS-2842, DCS-4387, DCS-2846) and
Confluence (MTU Home Page Redesign BR7, Modular IMTU Component, MTU Gamification).
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

TITLE = "IMTU — App vs Web Feature Gap"

# ---------------------------------------------------------------- tables ----
# Columns: Feature | What it does | Delivered by | Jira / source

HOME = [
    ["Feature", "What it does", "Delivered by", "Jira / source"],
    ["Unified promo home page",
     "Carrier promos and loyalty punch cards merged into one coherent page instead of two separate mechanics.",
     "Component", "DCS-3599"],
    ["“Your Activity” with rich transaction cards",
     "Redesigned history supporting successful, failed, queued and refunded states, with per-state action buttons and skeleton loading.",
     "Component", "DCS-3662, DCS-4166"],
    ["Carrier-promo highlight on activity cards",
     "Yellow background on a transaction card when a carrier promo is live for that specific offer — a repeat-purchase nudge.",
     "Component", "DCS-3893"],
    ["Activity “See All” page with filters",
     "Full history (~50 transactions) with All / Subscriptions filters that stay visible while scrolling; Subscriptions pre-selects when entered from that section.",
     "Component", "DCS-3665, DCS-4183"],
    ["Subscriptions section on home",
     "Surfaces active recurring top-ups on the home page. With subscriptions now 30%+ of revenue this is the highest-value single item on the list.",
     "Component", "DCS-3841, DCS-3828"],
    ["“Your Promos” carousel",
     "Up to 4 promo cards with dot indicators, fully tappable cards, and an animation when only one promo exists.",
     "Component", "DCS-3663, DCS-3926"],
    ["Promo count badge",
     "“7 promos available” badge on the home page, showing “9+” above nine. Direct discoverability lever for campaigns.",
     "Component", "DCS-3925"],
    ["Promo list page with country filter",
     "Dedicated promo list filterable by country, with non-matching promos still shown beneath rather than hidden.",
     "Component", "DCS-3664, DCS-3952"],
    ["Activity-based promo personalisation",
     "Promos ordered by relevance to the user's own send history and countries, falling back to non-relevant promos when nothing matches.",
     "Component", "DCS-3940, DCS-3791"],
    ["Promos on the order-complete screen",
     "Post-purchase page surfaces relevant promos using the same priority logic — captures the moment of highest intent.",
     "Component", "DCS-4284, DCS-4393"],
    ["First-time user tutorial",
     "Guided walkthrough for new IMTU users on first install or upgrade. App uses a Flutter tutorial library, so web needs its own implementation.",
     "Web work", "DCS-4012, DCS-3960"],
    ["Empty states",
     "Designed “No Activity” and “No past transactions” placeholders with illustration, localised across all supported languages.",
     "Component", "DCS-4229, DCS-4004"],
    ["New IMTU colour design system",
     "Token-based colour scheme with dark-mode image variants — the foundation the newer screens are built on.",
     "Component", "DCS-3598, DCS-5220"],
    ["Offer details redesign",
     "Reworked offer detail screen from the MTU 4.0 workstream.",
     "Component", "DCS-2423"],
]

SUBS = [
    ["Feature", "What it does", "Delivered by", "Jira / source"],
    ["Subscription toggle at checkout",
     "Converts a one-time top-up into a recurring one. This mechanic drove subscription volume from ~1k to ~18k per week after rollout. If only one thing ships to web, it is this.",
     "Component", "DCS-3818"],
    ["Frequency selection",
     "Recurring cadence of every 7, 14, 30 or 90 days, chosen at purchase.",
     "Component", "DCS-3818"],
    ["Edit subscription",
     "Change amount, schedule or payment method on an existing subscription via the current endpoint, without the legacy cancel-and-recreate path.",
     "Component", "DCS-3521, DCS-5184"],
    ["Cancel subscription flow",
     "Full cancellation journey with a revised confirmation dialog.",
     "Component", "DCS-4993, DCS-4974"],
    ["Active-subscription warning on one-time top-ups",
     "Warns a user buying a single top-up that they already have a subscription to that recipient — prevents accidental double-charging and the support contact that follows.",
     "Component", "DCS-4317, DCS-5224"],
    ["Resubscribe flow",
     "Re-enrol into a previously cancelled subscription, fetching subscription promos only and suppressing instant promos.",
     "Moving", "DCS-5042, DCS-5182"],
    ["Recover a subscription with a missing card",
     "“Add Payment” CTA on scheduled transaction details when the saved card is gone — recovers revenue that would otherwise churn involuntarily.",
     "Web work", "DCS-4992, DCS-4780"],
    ["Card-deletion protection",
     "Blocks removing the last payment card while an active subscription exists. Depends on the web's own card-management surface.",
     "Web work", "DCS-4514, DCS-5212"],
]

PROMOS = [
    ["Feature", "What it does", "Delivered by", "Jira / source"],
    ["BLS promo tool integration (v2)",
     "Current-generation promo-code engine. Worth confirming which version web is on — this is the substrate for marketing's campaigns.",
     "Web work", "DCS-937, DCS-14"],
    ["Loyalty punch cards",
     "Progress-based loyalty offers with “days left” badges on time-limited promos.",
     "Component", "DCS-2710, DCS-3843"],
    ["Combined promos endpoint",
     "Single endpoint serving both carrier and loyalty promos, replacing separate calls. A backend prerequisite web will need too.",
     "Web work", "DCS-4605"],
    ["Subscription-specific promos",
     "Promos that apply only to recurring purchases, separated from instant promos via promo_groups. Actively being built — app behaviour still changing.",
     "Moving", "DCS-4387, DCS-5045"],
]

PAY = [
    ["Feature", "What it does", "Delivered by", "Jira / source"],
    ["BOSS Cash (wallet) payment",
     "Stored-balance wallet as a selectable payment method in the top-up flow, with per-product visibility flags. Live for all US users since April 2026.",
     "Web work", "DCS-2842, DCS-2949"],
    ["CVV tokenization",
     "Tokenized CVV handling across MTU, eGift and eSIM purchases.",
     "Web work", "DCS-3519, DCS-4712"],
    ["Google Pay / Apple Pay",
     "NOT A GAP — neither surface has it. The DCS epic is open with a single unstarted ticket and the calling-app spec explicitly defers DCS products. Listed so it is not raised as a web-only shortfall.",
     "Neither", "DCS-3877, DCS-5238"],
]

XSELL = [
    ["Feature", "What it does", "Delivered by", "Jira / source"],
    ["“Boss Recommends” cross-sell",
     "eGift and eSIM cards surfaced on the MTU home page, driven by BMK content.",
     "Moving", "DCS-3666, DCS-3678"],
    ["Calling Plan cross-sell card",
     "Calling plans added to the Boss Recommends rail.",
     "Moving", "DCS-5150"],
    ["Refer-a-Friend $5 MTU cross-sell",
     "RAF offer placed into the top-up flow.",
     "Moving", "DCS-4178"],
    ["Insurance cross-sell on the subscription toggle",
     "Modular insurance component offered alongside subscriptions, gated by feature flag.",
     "Moving", "DCS-5172, DCS-5149"],
    ["App promo badge",
     "Katsiaryna's own example. Note this one runs the other way — it is a web-side placement promoting the app, so it is net-new web work rather than a component inheritance.",
     "Web work", "—"],
]

CRM = [
    ["Feature", "What it does", "Delivered by", "Jira / source"],
    ["Braze in-app messaging",
     "The app runs gamified promo pop-ups as Braze custom-HTML in-app messages, A/B/C tested and localised into five languages. Web has no equivalent delivery channel today — the direct blocker for running the same campaigns against web users.",
     "Web work", "Confluence: MTU Gamification"],
    ["Amplitude event instrumentation",
     "The app emits a full IMTU event taxonomy — order screens, toggle interactions, subscription edits and cancellations, activity entry points. Campaign targeting and measurement depend on web emitting a comparable set.",
     "Web work", "DCS-4775, DCS-3895"],
    ["Deep links into the top-up flow",
     "Campaigns land users directly in the flow or on a subscription. Web needs its own URL entry points to be targetable the same way.",
     "Web work", "brum://fundairtime"],
]

ERRORS = [
    ["Feature", "What it does", "Delivered by", "Jira / source"],
    ["Improved error descriptions",
     "Reworked error copy throughout the IMTU flow, replacing generic failure messages.",
     "Component", "DCS-4308"],
    ["Provider-error messaging on Top Up Failed",
     "Distinguishes carrier-side failures from our own, so users retry appropriately instead of abandoning.",
     "Component", "DCS-4300"],
    ["Promo error bottom sheets",
     "Distinct handling for country-scoped BLS promos versus carrier promos when a promo cannot be applied.",
     "Component", "—"],
]

TABLES = [
    ("T1", HOME), ("T2", SUBS), ("T3", PROMOS),
    ("T4", PAY), ("T5", XSELL), ("T6", CRM), ("T7", ERRORS),
]

# ---------------------------------------------------------------- content ---

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Prepared for Emilio del Rio and Katsiaryna Bialevich  ·  26 August 2026  ·  Source: DCS Jira + Confluence"),

    ("p", "A working inventory of IMTU features shipped in the app since the web experience was last updated, prepared to structure the parity conversation between DCS and the web team."),

    ("h2", "On “it's the same component”"),
    ("p", "Emilio's point is that the web would use the same component the app uses, so functionality should be identical. That holds for the flow and UI — most of the list below arrives with the component swap and costs the web team nothing beyond the integration itself."),
    ("p", "It does not hold for everything. A number of these features depend on capabilities the app has and the web does not: wallet payment, tokenized card handling, Braze messaging, deep links, and app-side analytics instrumentation. Those need separate web-side work regardless of which component renders the screens — and the CRM-facing ones are exactly what the marketing timeline depends on."),
    ("p", "So the useful question for the meeting is not “which features are missing” but “which of these come free with the swap, and which are their own line item.” Every row below is tagged accordingly."),

    ("h2", "How to read the tags"),
    ("b", "Component  —  Arrives with the flow-component swap; no extra web work beyond integration."),
    ("b", "Web work  —  Needs separate web-side platform work regardless of the component."),
    ("b", "Moving  —  Still in flight in the app. Do not build against it yet."),

    ("h2", "Home page and core flow"),
    ("p", "BR7 redesign, behind feature flag use_mtu_BR7_homepage."),
    ("table", "T1"),

    ("h2", "Subscriptions"),
    ("p", "30%+ of revenue — the commercial core of the gap."),
    ("table", "T2"),

    ("h2", "Promotions and loyalty"),
    ("p", "The engine most campaign work depends on."),
    ("table", "T3"),

    ("h2", "Payments"),
    ("p", "All require web-side platform work."),
    ("table", "T4"),

    ("h2", "Cross-sell and growth"),
    ("table", "T5"),

    ("h2", "CRM and tracking"),
    ("p", "The section that gates the marketing timeline."),
    ("table", "T6"),

    ("h2", "Errors and reliability"),
    ("p", "Quiet items, but they move completion rates."),
    ("table", "T7"),

    ("h2", "What to ask the web team"),
    ("n", "Which of these does web already have? This list is built from what the app shipped, not from an audit of web. Treat it as a checklist to mark up, not a backlog."),
    ("n", "What version of the flow component is web on today, and what does the swap actually deliver? That single answer collapses or confirms most of the Component rows above."),
    ("n", "Which backend endpoints does web currently call? Several features assume the combined promos endpoint, the current edit-subscription endpoint, and the store config endpoint. If web is on older ones, that is the real work item."),
    ("n", "What is web's path to Braze and Amplitude? This gates marketing's campaign timeline independently of the component, so it should be scoped in parallel rather than after."),
    ("n", "Can we agree a cut line? Suggested phase one: subscription toggle, subscriptions section, and CRM instrumentation. That captures the revenue driver and unblocks marketing without waiting for the full home-page redesign."),
    ("n", "How do we stay in sync afterwards? Four items on this list are still changing. Without a shared release convention, web will be re-closing this same gap in six months."),

    ("h2", "Caveats"),
    ("b", "This is the app's shipped inventory, not a verified diff.  —  Built from DCS Jira and Confluence, which document the app. No inventory of the web build was available, so “not available on web” rests on Katsiaryna's note that web was last updated about a year ago."),
    ("b", "Four items are still in flight.  —  Resubscribe, subscription promos, the cross-sell rail, and insurance. App behaviour is still changing there."),
    ("b", "Scope is IMTU only.  —  eGift and eSIM share several of these systems (wallet payment, tokenization, colour tokens) but were not surveyed."),
    ("b", "Google Pay / Apple Pay is not a web gap.  —  Neither surface supports it. Included above so it is not miscounted as web falling behind."),

    ("cap", "Feature status reflects Jira as of 26 August 2026 and will drift — re-check the moving items before committing scope."),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}

TAG_COLOR = {
    "Component": (0.05, 0.48, 0.42),
    "Web work":  (0.65, 0.35, 0.04),
    "Moving":    (0.70, 0.15, 0.12),
    "Neither":   (0.45, 0.42, 0.50),
}


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


def insert_table(docs, doc_id, marker, data):
    """Replace the [[marker]] placeholder with a real Docs table."""
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
    for start, r, c in sorted(cells, reverse=True):   # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        elif c == 2 and txt in TAG_COLOR:
            red, green, blue = TAG_COLOR[txt]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": red, "green": green, "blue": blue}}}},
                "fields": "bold,foregroundColor"}})
        elif c == 3:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"fontSize": {"magnitude": 8, "unit": "PT"},
                              "weightedFontFamily": {"fontFamily": "Roboto Mono"}},
                "fields": "fontSize,weightedFontFamily"}})
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

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
