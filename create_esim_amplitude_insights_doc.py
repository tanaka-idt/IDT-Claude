#!/usr/bin/env python3
"""
Creates ONE Google Doc: "eSIM: What Amplitude Says About the Journey".

A product investigation of eSIM in the BOSS Revolution app, built from Amplitude
(org BOSS 127967, BR app Prod appId 650506). Window is the 90 days ending
2026-09-03 unless a line says otherwise.

Every figure in the document links to the saved Amplitude chart it came from.
The charts live on dashboard 024gnsog, created alongside this doc.

Two things to know about how the numbers were produced:

  1. The funnel is anchored on ESIMOrderConfirmationScr, not ESIMBuyBtn. The
     BuyBtn event is an entry tile on the eSIM home screen (median 3 seconds to
     the offers list), so a funnel that treats it as checkout reports 0.30%
     conversion instead of the real 2.27%. That trap is documented in the doc.

  2. Numbers under "verified" were run directly against Amplitude while writing
     this. Numbers under "secondary" came from a parallel agent sweep and are
     labelled as needing a re-run before they carry a decision.
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

TITLE = "eSIM: What Amplitude Says About the Journey"

AMP = "https://app.amplitude.com/analytics/BOSS"
DASH = f"{AMP}/dashboard/024gnsog"
CHART = {
    "funnel":      f"{AMP}/chart/eqs34s89",
    "checkbox":    f"{AMP}/chart/xf6jrrv2",
    "destination": f"{AMP}/chart/yjnkx3bo",
    "outcomes":    f"{AMP}/chart/pe606wrv",
    "activation":  f"{AMP}/chart/ruedcncc",
    "entry":       f"{AMP}/chart/f6nb23tu",
    "promo":       f"{AMP}/chart/uljscp8e",
    "baseline":    f"{AMP}/chart/rf2qatoe",
    "platform":    f"{AMP}/chart/bgcg3q18",
}

# Phrase -> URL. Longest phrases match first, so the full chart names win over
# the short aliases used in prose.
DOC_LINKS = dict(LINK_MAP)
DOC_LINKS.update({
    "eSIM Product Deep Dive dashboard": DASH,
    "evidence dashboard": DASH,

    "eSIM purchase funnel, anchored on order review": CHART["funnel"],
    "purchase funnel chart": CHART["funnel"],
    "the corrected funnel": CHART["funnel"],

    "eSIM order review: compatibility checkbox then submit": CHART["checkbox"],
    "checkbox chart": CHART["checkbox"],

    "eSIM funnel by destination type: country vs regional": CHART["destination"],
    "destination type chart": CHART["destination"],

    "eSIM order outcomes: success vs failure, weekly users": CHART["outcomes"],
    "order outcomes chart": CHART["outcomes"],

    "eSIM post-purchase activation": CHART["activation"],
    "activation chart": CHART["activation"],

    "eSIM entry surfaces, weekly unique users": CHART["entry"],
    "entry surfaces chart": CHART["entry"],

    "eSIM promo code: tapped vs applied": CHART["promo"],
    "promo code chart": CHART["promo"],

    "eSIM checkout and activation events, unique users": CHART["baseline"],
    "event baseline chart": CHART["baseline"],

    "eSIM funnel by platform: iOS vs Android": CHART["platform"],
    "platform funnel chart": CHART["platform"],
})

# ---------------------------------------------------------------- tables ----

FUNNEL = [
    ["Step", "Event", "Users", "Advance", "Median to next"],
    ["eSIM home", "ESIMHomeScr", "88,600", "27.9%", "13s"],
    ["Offers list", "ESIMOffersListScr", "24,748", "31.8%", "34s"],
    ["Offer selected", "ESIMOfferSelectBtn", "7,874", "85.7%", "0s"],
    ["Order review", "ESIMOrderConfirmationScr", "6,749", "37.1%", "30s"],
    ["Order submitted", "ESIMOrderProcessingScr", "2,507", "80.3%", "17s"],
    ["Purchase complete", "ESIMOrderStatusSuccessScr", "2,014", "end: 2.27%", ""],
]

PLATFORM = [
    ["", "iOS", "Android", "Gap"],
    ["Users on eSIM home", "57,310", "31,418", "Android is 35% of traffic"],
    ["Reach the offers list", "30.1%", "24.0%", "6.1 points"],
    ["Select an offer", "32.6%", "30.2%", "2.4 points"],
    ["Reach order review", "87.2%", "82.1%", "5.1 points"],
    ["Submit the order", "39.0%", "32.9%", "6.1 points"],
    ["Order succeeds", "81.1%", "77.9%", "3.2 points"],
    ["End to end", "2.71%", "1.52%", "iOS converts 1.8x better"],
    ["Purchases in 90 days", "1,552", "479", "Android is 24% of purchases"],
]

DESTINATION = [
    ["", "Country plans", "Regional plans", "Read"],
    ["Offers-list users", "22,813", "4,296", "Regional is 15.8% of interest"],
    ["Select an offer", "32.7%", "23.2%", "Regional loses 9.5 points here"],
    ["Reach order review", "86.5%", "78.3%", "And 8.2 more points here"],
    ["Purchases", "1,946", "228", "Regional is 10.5% of purchases"],
    ["End to end", "8.53%", "5.31%", "Regional converts 38% worse"],
]

EVIDENCE = [
    ["Chart", "What it evidences", "Window"],
    ["eSIM purchase funnel, anchored on order review",
     "The six-step funnel and every step conversion in this document.",
     "90 days, 1-day window"],
    ["eSIM order review: compatibility checkbox then submit",
     "The checkbox gate: 3,294 of 6,787 tick it, 71.3% of those submit.",
     "90 days, 1-hour window"],
    ["eSIM funnel by platform: iOS vs Android",
     "The iOS/Android conversion gap, step by step.",
     "90 days, 1-day window"],
    ["eSIM funnel by destination type: country vs regional",
     "Country versus regional plan conversion, split on destination_type.",
     "90 days, 1-day window"],
    ["eSIM order outcomes: success vs failure, weekly users",
     "Payment failure volume and its stability over half a year.",
     "26 weeks, unique users"],
    ["eSIM post-purchase activation",
     "Install Now tap rate and eSIM info views after purchase.",
     "90 days, 7-day window"],
    ["eSIM entry surfaces, weekly unique users",
     "Home, country picker, offers list and search box, plus the 27 June break.",
     "26 weeks, unique users"],
    ["eSIM promo code: tapped vs applied",
     "511 users tap the promo control, 15 reach an applied event.",
     "90 days, 1-hour window"],
    ["eSIM checkout and activation events, unique users",
     "Unique-user baseline for every checkout, install and picker event cited.",
     "90 days"],
]

TABLES = [("FUNNEL", FUNNEL), ("PLATFORM", PLATFORM),
          ("DESTINATION", DESTINATION), ("EVIDENCE", EVIDENCE)]

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("p", "An investigation of the eSIM product in Amplitude, looking for ways to "
          "improve the user journey and the purchase funnel. Source is BR app Prod "
          "(appId 650506) in org BOSS. All figures are unique users over the 90 days "
          "ending 3 September 2026 unless a line says otherwise. Every number links "
          "to the chart behind it, and all nine charts sit on one evidence dashboard."),

    ("h2", "The short version"),
    ("n", "The eSIM funnel converts 2.27% end to end, not the 0.30% a naive funnel "
          "reports. The difference is one misread event, and it matters because the "
          "wrong number points the roadmap at the wrong screen."),
    ("n", "The single biggest recoverable loss is the order review screen: 4,242 of "
          "6,749 users (62.9%) look at the final price and never submit. That is "
          "more than twice the loss at every other late-funnel step combined."),
    ("n", "The prime suspect for that loss is a compatibility checkbox. Only 3,294 "
          "of 6,787 review-screen users tick it, and ticking is associated with "
          "submitting at 71.3% against 37.1% overall."),
    ("n", "Android is 35% of eSIM traffic and 24% of eSIM purchases. Closing that "
          "gap is worth about 371 purchases a quarter with no new traffic."),
    ("n", "Once a user submits, the product works: 80.3% succeed in a median of 17 "
          "seconds. Payment and provisioning are not the eSIM problem. Everything "
          "upstream of the submit tap is."),

    ("h2", "The funnel, corrected"),
    ("p", "Anchored on ESIMOrderConfirmationScr, the actual order review screen, over "
          "a 1-day conversion window. Source: purchase funnel chart."),
    ("table", "FUNNEL"),
    ("b", "Read the last two steps together: the product converts 2,014 of the 2,507 "
          "users who actually submit an order (80.3%), and loses 4,242 of the 6,749 "
          "who reach the screen where they would submit. The checkout works. Getting "
          "people to press the button does not."),
    ("b", "Buying an eSIM is a single-session act: median time from the eSIM home "
          "screen to a completed purchase is under three minutes, and widening the "
          "window from one hour to seven days adds about 2% more conversions. There "
          "is no abandoned-cart audience to retarget here, so a Braze winback plan "
          "aimed at eSIM browsers would be chasing a population that does not exist."),

    ("h3", "A trap worth documenting"),
    ("p", "ESIMBuyBtn looks like a checkout button and is not one. It is an entry "
          "tile on the eSIM home screen: users tap it and land on the offers list a "
          "median of 3 seconds later, and only 32% of successful purchasers ever "
          "fire it. A funnel that places it before the success screen reports 0.30% "
          "conversion, understating the truth by roughly 7x, and points at an "
          "offer-detail screen that is not losing anyone. ESIMOrderConfirmationScr "
          "is on 100% of purchases and carries offer_id, offer_amount, validity, "
          "destination, destination_type and is_esim_reload. Any existing eSIM chart "
          "or alert built on ESIMBuyBtn should be re-pointed at it. That is a "
          "dashboard change, not an app ticket."),

    ("h2", "Where the money is going"),

    ("h3", "1. The order review screen loses two thirds of the people who reach it"),
    ("b", "The size of it: 6,749 users reach order review and 2,507 submit. The 4,242 "
          "lost there is the largest single recoverable number in the product, and it "
          "is a group that has already chosen a plan and seen the price."),
    ("b", "The prime suspect: a compatibility checkbox sits on that screen. It is "
          "shown to 100% of review-screen users, and only 3,294 of 6,787 tick it. On "
          "the checkbox chart, users who tick go on to submit at 71.3%, against an "
          "overall review-to-submit rate of 37.1%. Almost every submitter ticks first."),
    ("b", "What this does and does not prove: ticking a box is downstream of "
          "intending to buy, so this is correlation, not a measured cause. What is "
          "not in doubt is that a mandatory device-compatibility confirmation stands "
          "between a chosen plan and a payment, and that half the people who get "
          "there do not clear it."),
    ("b", "Worth trying: move the compatibility check upstream so it is resolved "
          "before the price screen, replace the blocking checkbox with an inline "
          "device check result, or test a pre-confirmed state for devices already "
          "known to support eSIM. Any of the three is an A/B test, not a rebuild."),
    ("b", "Rough sizing: if non-tickers submitted at even half the tickers' rate, "
          "that is roughly 1,240 more submissions per quarter and, at the observed "
          "80% success rate, close to 985 additional purchases against a base of "
          "2,014. Treat that as an upper bound on a correlational reading, not a "
          "forecast."),

    ("h3", "2. Android converts at 56% of the iOS rate"),
    ("p", "Same six-step funnel, split by platform. Source: platform funnel chart."),
    ("table", "PLATFORM"),
    ("b", "Where Android actually loses ground: the two weakest steps are the eSIM "
          "home to offers list (24.0% against 30.1%) and order review to submit "
          "(32.9% against 39.0%). Both are screens, not payment plumbing, and the "
          "order-status success rate once submitted is nearly identical, so this is "
          "not an Android payment problem."),
    ("b", "What parity is worth: at the iOS end-to-end rate, Android's 31,418 home "
          "users would produce about 851 purchases instead of 479, so roughly 371 "
          "more purchases a quarter from traffic the app already has. That makes an "
          "Android-only review of those two screens the highest-return piece of "
          "platform work available."),

    ("h3", "3. Regional plans are found but not chosen"),
    ("p", "Split on destination_type, the property that separates a single-country "
          "plan from a multi-country one. Source: destination type chart."),
    ("table", "DESTINATION"),
    ("b", "The pattern: regional plans draw a respectable 15.8% of offers-list "
          "interest and end up as 10.5% of purchases. They lose most of that ground "
          "at the offer card, converting list view to offer selection at 23.2% "
          "against 32.7% for country plans."),
    ("b", "Why this is worth reading now: the June and July 2026 region-matching "
          "release (DCS-4543, DCS-4544) set out to make regional plans findable from "
          "a country search, and on this evidence findability is not the constraint. "
          "People reach regional plans and then decline them. The next move is on the "
          "offer card itself, most likely showing which countries a regional plan "
          "covers and what it costs per country against the single-country "
          "alternative."),
    ("b", "One caveat: this compares two different product sets, not the same plan "
          "priced two ways. Regional plans are pricier and broader by nature, so some "
          "of the gap is the catalogue rather than the presentation."),

    ("h3", "4. Payment failure is real, stable, and smaller than it looks"),
    ("b", "The honest denominator: over 26 weeks, 1,435 unique users reached a "
          "failure screen against 4,009 who reached a success screen, so about 26% "
          "of users who get an order outcome see a failure. Counting events instead "
          "of users gives 35%, but that number double-counts retries, since failing "
          "users fire the failure screen about 2.3 times each. Use the user figure."),
    ("b", "It is not getting worse: weekly failure users have run in a flat band for "
          "half a year on the order outcomes chart, with no visible trend and no step "
          "change at any release. This is a standing cost, not an incident."),
    ("b", "Where it ranks: 493 users are lost between submitting and succeeding, "
          "against 4,242 lost before submitting. Payment failure deserves a fix, but "
          "it is roughly a tenth of the review-screen problem and should be "
          "prioritised accordingly."),
    ("b", "Secondary, worth a re-run: the agent sweep found that about half of all "
          "failure events carry the literal reason string 'failed', at nearly "
          "identical rates on iOS (51.0%) and Android (49.1%). If that holds, the "
          "fix is on the service that maps the payment response, not in either app."),

    ("h3", "5. One in five buyers never starts installation"),
    ("p", "Source: activation chart."),
    ("b", "The numbers: of 2,042 users who complete a purchase, 1,607 (78.7%) tap "
          "Install Now on the success screen, a median of 9 seconds later. The "
          "remaining 435 have paid for a data plan and not begun installing it."),
    ("b", "Why the success screen is the moment: it is the one point where every "
          "buyer is present and attentive, and the install CTA already converts most "
          "of them. The work is on the 21% who leave, which is a retention and "
          "support-cost question rather than a funnel one."),
    ("b", "Secondary, worth a re-run: the sweep put post-purchase support contact at "
          "roughly 395 of 2,042 buyers within seven days. If that holds, support "
          "contact is an activation-stage cost, and better install guidance pays for "
          "itself twice."),

    ("h3", "6. The search box is not where destinations get picked"),
    ("p", "Source: entry surfaces chart."),
    ("b", "The surface that matters: over 26 weeks the Hey Traveler country picker "
          "on the eSIM home reached 50,563 users against 12,796 for the search box, "
          "so the picker is four times the size of search. Only about 6% of eSIM "
          "home users ever open search at all."),
    ("b", "What follows: merchandising effort belongs on the home-screen picker, not "
          "in the search box. This does not argue against the search improvements "
          "already shipped, it argues about where the next hour of design time goes."),
    ("b", "A gap that blocks the obvious analysis: the picker records no destination. "
          "Its only properties are component_name, a GeoIP country of the user, "
          "event_name, hosting_app, phone_number and user_id. So the app cannot "
          "currently answer which destinations people pick on the biggest "
          "destination-picking surface it has. That is the highest-value tagging fix "
          "on this list."),
    ("b", "An unexplained traffic break: weekly eSIM home users dropped from 9,907 "
          "in the week of 22 June to 6,900 in the week of 29 June and have stayed "
          "there. The eSIM entry button did not move and overall app activity did "
          "not fall, so a distinct population stopped arriving on 27 June. The sweep "
          "found the same break on both platforms in the same week, which rules out a "
          "staged app rollout and points at a server-side or campaign change. Worth "
          "one hour with whoever owns the CRM calendar, because it is roughly 3,000 "
          "eSIM home users a week."),

    ("h2", "Smaller things that are cheap to fix"),
    ("b", "The promo code path is effectively broken: 511 users tap the promo code "
          "control and 15 reach an applied event, on the promo code chart. Either "
          "code entry is failing for almost everyone who tries, or the applied event "
          "only fires on valid codes and half the funnel is untracked. Both are worth "
          "an hour, and 511 users a quarter are reaching for a discount mechanism "
          "that appears not to work."),
    ("b", "Two thirds of the tutorial is unshipped: 59,788 users see step 1 of the "
          "eSIM tutorial and 8,942 (15.0%) reach step 3. Whatever is on screens two "
          "and three is not being read. Note the sweep also tested and rejected the "
          "obvious worry: tutorial-exposed users reach the offers list slightly more "
          "often than unexposed ones, so the interstitial is not blocking the funnel "
          "and should not be pulled on funnel grounds. Secondary, worth a re-run."),
    ("b", "Repeat purchase is better than a travel product implies: the sweep put "
          "90-day repeat purchase at 816 of 4,027 buyers (20.3%) and rising. If that "
          "holds it changes how eSIM should be valued against acquisition cost, so it "
          "is the single most useful number to re-run properly. Secondary."),
    ("b", "The offer-list filter is not what its name suggests: the filter property "
          "records Unlimited against Standard, not country against region. Anyone "
          "reaching for it to measure the region work will measure the wrong thing. "
          "Use destination_type instead."),

    ("h2", "What to do, in order"),
    ("n", "Re-point every eSIM funnel, dashboard and alert from ESIMBuyBtn to "
          "ESIMOrderConfirmationScr. No engineering, and it stops the team optimising "
          "a screen that is not losing anyone."),
    ("n", "A/B test the compatibility checkbox on the order review screen. Largest "
          "single loss in the product, cheapest credible hypothesis for it."),
    ("n", "Run an Android-only review of the eSIM home and the order review screen. "
          "Worth roughly 371 purchases a quarter at iOS parity, on existing traffic."),
    ("n", "Add the picked destination to the Hey Traveler country picker event. One "
          "property, and it unblocks the demand analysis for the surface that carries "
          "four times the traffic of search."),
    ("n", "Fix or instrument the promo code path, and find out what happened on 27 "
          "June. Both are hour-scale investigations with real numbers behind them."),
    ("n", "Rework the regional plan offer card to show coverage and per-country "
          "value. The region-matching release made these plans findable; this is the "
          "half that turns finding them into buying them."),

    ("h2", "How this was built, and what to distrust"),
    ("b", "Verified directly: the funnel, the platform split, the destination-type "
          "split, the checkbox behaviour, order outcomes, activation, entry surfaces "
          "and the promo code path were each run against Amplitude while writing this "
          "and are linked to their charts above."),
    ("b", "Secondary and labelled as such: repeat purchase, support contact rate, "
          "tutorial step drop-off, failure reason codes and the IMTU cross-sell "
          "comparison came from a parallel agent sweep. They are directionally "
          "reported here and each should be re-run before it carries a decision."),
    ("b", "Screen events are not intent: several of these events fire on render "
          "rather than on tap, so a drop between two of them can be navigation rather "
          "than abandonment. The compatibility check is the worked example: its two "
          "events look like consecutive funnel steps and are actually separate "
          "surfaces, with 68% of confirm-sheet viewers never tapping the check button "
          "at all. Adjacent event counts are not a funnel."),
    ("b", "No experiment has been run: every recommendation here is a hypothesis "
          "drawn from observational data. The checkbox finding in particular is "
          "correlational, and the sizing attached to it is an upper bound rather than "
          "a forecast."),
    ("b", "One window, one app: this is BR app Prod only, over 90 days. eSIM in the "
          "Money app was not examined, and the traffic break on 27 June sits inside "
          "the window, so any before-and-after comparison across it is confounded."),

    ("h2", "Evidence index"),
    ("p", "All nine charts are on the eSIM Product Deep Dive dashboard in Amplitude, "
          "under org BOSS, project BR app Prod (650506)."),
    ("table", "EVIDENCE"),

    ("cap", "Compiled from Amplitude on 3 September 2026. Charts are saved with "
            "relative date ranges, so re-opening them later will show a later window "
            "than the figures quoted here."),
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

        # Bullets read "Lead: explanation", so bold through the colon.
        if kind == "b" and ": " in text:
            lead = len(text.split(": ")[0]) + 1
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
        if not txt:
            continue
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0 or c == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        # Event-name column on the funnel table reads better monospaced.
        if marker == "FUNNEL" and c == 1 and r > 0:
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

    # Chart names, the dashboard and every Jira key become clickable.
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
