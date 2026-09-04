#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU Home Redesign: Is It Working?".

An effectiveness review of the redesigned IMTU home page (BR7) in the BOSS
Revolution app, built from Amplitude (org BOSS, BR app Prod appId 650506) and
DCS Jira. Answers three questions: is the new home helping people buy, is it
helping them find things, and what should change next.

Every figure links to a saved Amplitude chart on dashboard bwtn629z. Numbers
marked "verified" were run directly while writing this; the rest came from a
parallel agent sweep that was then adversarially reviewed, and the review's
corrections are what appear here.

Key methodological point: the rollout was an eight-week ramp (27 Apr to 22 Jun
2026), not a switch, so naive before/after windows are wrong. The cleanest test
is the variant flag is_br7_mtu_home on MTUHomeScr, which lets old and new home
be compared in the same weeks.
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

TITLE = "IMTU Home Redesign: Is It Working?"

AMP = "https://app.amplitude.com/analytics/BOSS"
DASH = f"{AMP}/dashboard/bwtn629z"
FIGMA = ("https://www.figma.com/design/CtqMj3TydM2jz7jpUlKChc/IMTU-Homepage"
         "?node-id=419-29757")

# Saved chart id -> (short alias used in prose, full saved name)
CHARTS = {
    "gk8rshea": ("same-weeks funnel chart", "IMTU purchase funnel: old vs new home, same weeks (11 May to 21 Jun 2026)"),
    "oh9jxe42": ("variant flag chart", "IMTU home views by variant flag, weekly users (6mo)"),
    "qrmv0064": ("rollout chart", "IMTU home: legacy vs new widgets, weekly users (6mo)"),
    "cvu57zvd": ("before chart", "IMTU home to purchase, 2-step, BEFORE redesign (16 Feb to 12 Apr 2026)"),
    "kpg3tbpl": ("after chart", "IMTU home to purchase, 2-step, AFTER full rollout (6 Jul to 3 Sep 2026)"),
    "iihxt670": ("spring 2025 chart", "IMTU home to purchase, 2-step, spring 2025 baseline (16 Feb to 12 Apr 2025)"),
    "ksgr8de4": ("summer 2025 chart", "IMTU home to purchase, 2-step, summer 2025 baseline (6 Jul to 30 Aug 2025)"),
    "ijq8e456": ("weekly purchasers chart", "IMTU weekly purchasers, total and by recurrent_unit (6mo)"),
    "qg43xv3s": ("platform funnel chart", "IMTU home to purchase funnel by platform, Last 90 Days"),
    "41hol0mm": ("app version chart", "IMTU new home reach by app version, Last 90 Days"),
    "k5o6sv13": ("Send Again chart", "Activity: Send Again to order to success (1h, Last 90 Days)"),
    "i1v3hlpw": ("card tap chart", "Activity: past transaction card tap to order to success (1h, Last 90 Days)"),
    "hmxzktta": ("legacy activity chart", "Legacy activity transaction view to order to success (1h, 16 Feb to 12 Apr 2026)"),
    "fvznvi6r": ("card overlap chart", "Activity: card tap then Send Again then order (1h, Last 90 Days)"),
    "wolxkf69": ("promo tap chart", "Promos: card tap to order to success (1h, Last 90 Days)"),
    "l5r4pemt": ("legacy promo chart", "Legacy carrier promo select to order to success (1h, 16 Feb to 12 Apr 2026)"),
    "611svswl": ("promo type chart", "Promos: card tap to purchase by promo type (1h, Last 90 Days)"),
    "ui7efuzg": ("promo placement chart", "Promos: card taps by screen_name, daily (Last 90 Days)"),
    "nmb7gplw": ("cancellation chart", "Subscriptions: home card tap to completed cancellation (1h, Last 90 Days)"),
    "ums1liyh": ("cancel button chart", "Subscriptions: home card tap to cancel button (1h, Last 90 Days)"),
    "ox6r88si": ("subscriptions weekly chart", "Subscriptions: weekly subscription purchasers vs cancel-button users (6mo)"),
    "w3sl7xul": ("tutorial chart", "Home tutorial: navigation by current step to next step (Last 90 Days)"),
    "z7p46sf0": ("search share chart", "Home: weekly search bar users vs home users (6mo)"),
    "gnilo00a": ("empty state chart", "Activity empty state: Send Top Up to order to success (1-day, Last 90 Days)"),
    "pgzji0fk": ("Start Top Up chart", "Home: Start Top Up to search bar (1h, Last 90 Days)"),
}

DOC_LINKS = dict(LINK_MAP)
DOC_LINKS.update({
    "IMTU Home Redesign evidence dashboard": DASH,
    "evidence dashboard": DASH,
    "IMTU Homepage Figma file": FIGMA,
})
for cid, (alias, name) in CHARTS.items():
    DOC_LINKS[alias] = f"{AMP}/chart/{cid}"
    DOC_LINKS[name] = f"{AMP}/chart/{cid}"

# ---------------------------------------------------------------- tables ----

SAMEWEEKS = [
    ["Step", "Old home", "New home", "Read"],
    ["Home screen users", "346,253", "176,829", "same six weeks, 11 May to 21 Jun"],
    ["Tap Top Up", "82.9%", "84.0%", "+1.1 points"],
    ["Reach order screen", "77.9%", "78.3%", "+0.4"],
    ["Tap Complete Order", "95.8%", "96.1%", "+0.3"],
    ["Order succeeds", "94.5%", "95.1%", "+0.6"],
    ["Home to purchase", "58.5%", "60.1%", "+1.6 points, +2.7% relative"],
]

BEFOREAFTER = [
    ["Window", "Home to purchase", "Users", "Chart"],
    ["Spring 2026, before (16 Feb to 12 Apr)", "63.3%", "598,312", "before chart"],
    ["Summer 2026, after full rollout (6 Jul to 3 Sep)", "59.1%", "603,482", "after chart"],
    ["Spring 2025, same weeks a year earlier", "58.2%", "596,692", "spring 2025 chart"],
    ["Summer 2025, same weeks a year earlier", "59.4%", "574,477", "summer 2025 chart"],
]

CONTROLS = [
    ["Home control", "Users (90d)", "Reach order screen", "Purchase", "Chart"],
    ["Send Again on an activity card", "90,870", "97.6%, median 1s", "84.8%", "Send Again chart"],
    ["Activity card tap", "176,304", "71.2%, median 27s", "57.4%", "card tap chart"],
    ["Legacy transaction view (spring)", "221,449", "81.9%, median 18s", "72.3%", "legacy activity chart"],
    ["Carrier promo card", "46,870", "59.3%", "44.8%", "promo type chart"],
    ["Loyalty promo card", "48,999", "43.1%", "28.3%", "promo type chart"],
    ["Legacy carrier promo list (spring)", "66,593", "40.6%", "31.7%", "legacy promo chart"],
    ["Activity empty state CTA", "44,489", "44.9%", "31.7% (1 day)", "empty state chart"],
    ["Subscription card", "118,421", "", "55.4% cancel a subscription", "cancellation chart"],
]

EVIDENCE = [["Chart", "What it evidences"]] + [
    [name, alias.replace(" chart", "")] for cid, (alias, name) in CHARTS.items()
]

TABLES = [("SAMEWEEKS", SAMEWEEKS), ("BEFOREAFTER", BEFOREAFTER),
          ("CONTROLS", CONTROLS), ("EVIDENCE", EVIDENCE)]

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("p", "An effectiveness review of the redesigned IMTU home page (epic DCS-3599, "
          "design in the IMTU Homepage Figma file, spec on the MTU Home Page Redesign "
          "BR7 Confluence page). Source is Amplitude, BR app Prod (650506), org BOSS. "
          "Unless a line says otherwise, figures are unique users and Last 90 Days "
          "means the 90 days to 4 September 2026. Every number links to its chart; all "
          "25 charts sit on one evidence dashboard."),

    ("h2", "The short version"),
    ("n", "The new home did not change how many home visitors buy. In the same six "
          "weeks, users on the new home converted at 60.1% and users on the old home at "
          "58.5%, a difference too small to call a win and partly explained by app "
          "version. It did not hurt either."),
    ("n", "The redesign's clearest behavioural win is the Start Top Up button: weekly "
          "users tapping it went from about 6,700 to about 27,000 once the new CTA "
          "shipped (DCS-4261). People found the door."),
    ("n", "The Activity widget is the only new element that produces purchases at "
          "scale, and it is doing a worse job than the list it replaced: fewer buyers "
          "start from a past transaction (31.8 to 34.6% now, 35.8 to 45.8% before) and "
          "28.8% of card tappers never reach the order screen, against 18.1% before."),
    ("n", "Send Again is the best control on the page (84.8% to purchase, one second "
          "to a prefilled order) and only 7% of weekly home visitors use it. That is a "
          "placement problem, not a conversion problem."),
    ("n", "The Subscriptions widget is a cancellation surface. 55.4% of people who tap "
          "a subscription card complete a cancellation within the hour. That is users "
          "cleaning up the subscriptions the default-on toggle created, and the widget "
          "should be judged as a management tool, not an acquisition one."),
    ("n", "The Promos carousel converts each tap better than the old carrier list "
          "(37.1% vs 31.7%) but reaches no more people, and half its taps are loyalty "
          "punch cards that were never purchase CTAs. Users tap See All more than they "
          "tap a card."),

    ("h2", "What actually shipped, and when"),
    ("b", "A ramp, not a launch: the new widgets first fired on 20 April, reached a "
          "quarter of home users in the week of 18 May, two thirds in the week of 25 "
          "May, and full volume in the week of 22 June, when the legacy controls "
          "stopped (rollout chart, variant flag chart). iOS and Android ramped "
          "together."),
    ("b", "It is a build gate: reach is 99.8% on app versions 26.6.x and later, about "
          "half on 26.5.x, and about 1% below 26.5 (app version chart). Today 90.0% of "
          "home users are on the new home; the other 10% are old installs, not a flag "
          "problem."),
    ("b", "Why this matters for every comparison in this document: any before/after "
          "that treats May or June as 'after' is comparing a mixed population. The "
          "clean after-window starts 6 July. The cleanest test of all is the variant "
          "flag is_br7_mtu_home on MTUHomeScr, which allows old and new home to be "
          "compared in the same weeks."),

    ("h2", "Is it helping people buy?"),
    ("h3", "Same weeks, old home against new home"),
    ("p", "Users who saw the old home and users who saw the new one, 11 May to 21 "
          "June 2026, 1-day ordered funnel. Source: same-weeks funnel chart."),
    ("table", "SAMEWEEKS"),
    ("b", "What it says: the new home converts 1.6 points better on a controlled "
          "same-period comparison across 523,000 users, with the gain spread thinly "
          "across every step. That is a real but small effect."),
    ("b", "What to distrust: assignment was by app build, not by random user split "
          "(DCS-4423 created the groups but no readout was ever posted). Users on the "
          "newest builds skew more engaged. Users on builds too old to carry the flag "
          "converted at 56.6% in the same weeks, below both groups, which is the "
          "signature of a version effect. Treat +1.6 as an upper bound."),

    ("h3", "Before and after, with the 2025 control"),
    ("p", "Two-step funnel, home screen to purchase success, 1-day window."),
    ("table", "BEFOREAFTER"),
    ("b", "The raw drop is 4.2 points (63.3% to 59.1%). Seasonality does not explain "
          "it: in 2025 the same two windows moved the other way, up 1.2 points."),
    ("b", "But spring 2026 was the anomaly, not summer: it sat 5.1 points above spring "
          "2025, while summer 2026 is within 0.3 points of summer 2025. The subscription "
          "toggle launched on 9 March 2026 and lifted subscription purchases from about "
          "1,000 to about 18,000 a week through the spring; the June toggle rule change "
          "(DCS-5289) then coincided with the fall."),
    ("b", "Honest reading: conversion after full rollout is about 4 points lower than "
          "before, this is not seasonal, and the data cannot separate 'the redesign cost "
          "4 points' from 'a spring lift driven by the toggle faded while the redesign "
          "landed'. The same-weeks comparison above leans toward the second reading. "
          "Do not report this as flat, and do not report it as a redesign loss."),
    ("b", "Weekly purchasers have slid 13% since late April (about 132,000 to about "
          "116,000 a week) while weekly home users stayed at 152,000 to 164,000 (weekly "
          "purchasers chart). The slide is gradual and started before the new home had "
          "material reach, so it is not attributable to the home, but it is the number "
          "the business will ask about."),
    ("b", "Platform: iOS converts 57.6% and Android 54.3% in the last 90 days, with the "
          "whole gap at the first two steps (platform funnel chart). The gap predates "
          "the redesign (3.4 points before, 2.5 after), so the new home did not open it."),

    ("h3", "Where purchases start on the new home"),
    ("p", "One-hour ordered funnels from each control to a successful order, last 90 "
          "days. The legacy rows are the spring window the control existed in. Rates "
          "at different funnel depths are not comparable with each other: Send Again is "
          "one tap from a prefilled order, so its rate is a checkout completion rate."),
    ("table", "CONTROLS"),
    ("b", "Start Top Up and the search bar are one path, not two: 67.7% of Start Top "
          "Up users tap the search bar within a median 5 seconds (Start Top Up chart). "
          "Do not add them together, and do not read the search bar's share as a legacy "
          "path beating the widgets."),

    ("h2", "Is it helping people find things?"),
    ("b", "The manual route did not shrink: the share of weekly home visitors who go "
          "to the search bar was 29% before and 30% after (search share chart). If the "
          "widgets were surfacing the recipients people wanted, this would have fallen. "
          "It measures new-recipient intent as much as widget failure, so read it as "
          "'no visible improvement', not as failure."),
    ("b", "Fewer people find their past recipients through the home: activity card "
          "tappers are 22.1% of home users now against 37.2% for the legacy transaction "
          "list in spring, and the share of all buyers who start from a past "
          "transaction fell from 35.8 to 45.8% to 31.8 to 34.6% (card tap chart, legacy "
          "activity chart, card overlap chart). Only 8.6% of card tappers go on to Send "
          "Again, so the two controls are near disjoint."),
    ("b", "The tutorial is a branching flow and the biggest loss is on its second "
          "stop: 86,214 users arrive at the quick top-ups tooltip and 47,783 (55%) tap "
          "forward, against 75 to 77% forward taps on the promotions and activity stops "
          "(tutorial chart). About 46,000 of roughly 106,000 starters navigate into a "
          "terminal tooltip. There is no dismiss event, so completion cannot be measured "
          "cleanly."),
    ("b", "The empty state converts new users: 44,489 people with no history tapped "
          "its Send Top Up and 14,088 (31.7%) bought within a day (empty state chart). "
          "The loss is before the order screen, where 55% drop."),
    ("b", "See All is the most-tapped thing in the promo section: 89,810 users tapped "
          "it against 73,448 who tapped a promo card on the home itself (promo placement "
          "chart). People are looking for a promo the carousel is not showing them."),

    ("h2", "The three widgets, one by one"),
    ("h3", "Activity"),
    ("b", "Engagement is modest against exposure: of about 891,000 widget viewers, "
          "24.8% swipe the cards, 19.8% tap one, 10.2% press Send Again."),
    ("b", "Send Again is the win: 90,870 users, 97.6% reach the order screen in a "
          "median 1 second, 84.8% buy, against 74.4% for the legacy Quick Send button "
          "(Send Again chart). Its weekly reach is about 7% of home visitors, roughly "
          "parity with Quick Send, so the redesign made the shortcut better without "
          "putting it in front of more people."),
    ("b", "The card tap is the loss: 176,304 tappers, 71.2% reach the order screen in "
          "a median 27 seconds, 57.4% buy, against 81.9% and 72.3% for the legacy "
          "transaction view (card tap chart, legacy activity chart). The path is "
          "heterogeneous: about a third of tappers fall back into the regular send flow "
          "via the Top Up button a median 97 seconds later, so the card is not reliably "
          "delivering a prefilled order. The intermediate screen is not instrumented."),
    ("h3", "Promos"),
    ("b", "Reach did not grow: weekly unique promo tappers run 7,700 to 10,400 on the "
          "carousel against 8,100 to 10,200 on the legacy list, with flat home traffic, "
          "and promo-led buyers sit at roughly 2,500 a week either way (promo tap chart, "
          "legacy promo chart)."),
    ("b", "Per tap it converts better, but only for the right card type: carrier promo "
          "taps go to purchase at 44.8%, loyalty punch-card taps at 28.3% on near-equal "
          "volumes (promo type chart). A loyalty card opens progress, not an order, so "
          "half of the '48% of tappers never reach the order screen' is the widget doing "
          "what it was designed to do. Judge the promo carousel on carrier taps alone."),
    ("b", "The details sheet is a dead path: 87,843 taps, 4,662 open details, 847 tap "
          "the details CTA, 375 reach an order screen. Under 1% of promo-led orders."),
    ("b", "A placement went dark: the congratulations-screen promo cards recorded zero "
          "taps from 20 July to 3 August (promo placement chart). Two weeks of a "
          "post-purchase surface switched off inside the analysis window, cause "
          "unknown."),
    ("h3", "Subscriptions"),
    ("b", "It is a management surface: 579,068 viewers, 118,421 card tappers (20.4%), "
          "45,419 See All, and 3,560 empty-state Start Subscription tappers of whom "
          "1,386 (38.9%) bought within a day."),
    ("b", "Verified: 65,624 of 118,421 card tappers (55.4%) completed a subscription "
          "cancellation within the hour, median 15 seconds to the cancel button and 99% "
          "pass-through from the button to confirmed success (cancellation chart). This "
          "is not a dismiss button being misread."),
    ("b", "Read it in context: subscription purchases doubled in the week of 15 June "
          "(about 17,500 to about 35,600 weekly users, now 30.8% of all purchasers) when "
          "the toggle default changed, and cancel volume stepped up with it (weekly "
          "purchasers chart, subscriptions weekly chart). The widget accounts for about "
          "39% of all cancel-button users; the other 61% arrive from other routes. The "
          "home card is how people find and undo a subscription they did not mean to "
          "start, which is the problem DCS-5297 exists to fix upstream."),

    ("h2", "What to do next, in order"),
    ("n", "Make the activity card behave like Send Again. The card leaks 28.8% before "
          "the order screen and the button leaks 2.4%. Either the card tap lands on the "
          "same prefilled order Send Again does, or Send Again becomes the card's "
          "primary tap target. Instrument whatever screen currently sits between card "
          "tap and order screen so the leak can be seen."),
    ("n", "Put Send Again in front of more people. It converts 84.8% and reaches 7% of "
          "home visitors. Surfacing it on the first card without a swipe, or on the "
          "home header for the most recent recipient, is the highest-return change on "
          "this list."),
    ("n", "Split the promo carousel: carrier promos as purchase CTAs, loyalty progress "
          "somewhere that does not compete for the same taps. Then read the carrier "
          "conversion on its own, and find out why See All out-taps the cards; the "
          "personalised ordering from DCS-3940 is the first thing to check."),
    ("n", "Treat the subscriptions widget as a management tool and pair its cancel "
          "path with the retention offer in DCS-5375. Do not spend on acquisition here: "
          "3,560 Start Subscription tappers in 90 days says the audience is not on this "
          "surface."),
    ("n", "Cut the tutorial to the stops people complete and rewrite the second one: "
          "55% forward on quick top-ups against 75 to 77% elsewhere. Add a dismiss event "
          "so completion can be measured (DCS-4012, DCS-4399)."),
    ("n", "Prefill the empty state. 55% of new users who tap its Send Top Up never reach "
          "the order screen; landing them on the recipient search with the keyboard open "
          "is the cheapest fix."),
    ("n", "Look outside the home for the big leak: Top Up tap to order screen loses 24 "
          "to 27% of users and its median time grew 9 seconds since spring. It is the "
          "largest single drop in the whole flow and none of it is on the home page."),
    ("n", "Produce the A/B readout that was never written. DCS-4423 built the groups; "
          "the is_br7_mtu_home flag makes a proper same-period comparison possible for "
          "11 May to 21 June, controlled for app version. One afternoon of work, and it "
          "settles the 'did it help' question this document can only bound."),

    ("h2", "How this was built, and what to distrust"),
    ("b", "Verified directly: the same-weeks funnel, the variant ramp, the widget "
          "rollout series, the subscription cancellation funnel and the promo-type split "
          "were run while writing this and are linked above."),
    ("b", "Reviewed, not re-run: the before/after windows, the 2025 baselines, the "
          "platform split, the widget funnels, the tutorial and search figures came from "
          "a parallel agent sweep. Two adversarial reviewers then re-ran the load-bearing "
          "ones; where they corrected a number, the corrected number is what appears "
          "here. Six claims from the sweep were killed outright and do not appear."),
    ("b", "Windows are not all the same: Last 90 Days includes 12 days before the new "
          "home reached full volume, and the 90-day unique-user denominators differ "
          "slightly between charts because they were run minutes apart. No share in "
          "this document divides a figure from one chart by a denominator from another."),
    ("b", "No randomised test exists: the variant groups were build-gated, so every "
          "old-versus-new comparison carries an app-version confound in the new home's "
          "favour."),
    ("b", "Event semantics were checked where they mattered: the cancel button was "
          "traced through to confirmed cancellation, the promo types were read from the "
          "chart, and Start Top Up was shown to feed the search bar. The activity card's "
          "intermediate screen and the tutorial's dismiss action remain uninstrumented."),

    ("h2", "Sources"),
    ("b", "Amplitude: every chart in this document is on the IMTU Home Redesign "
          "evidence dashboard, org BOSS, project BR app Prod (650506)."),
    ("b", "Jira: epic DCS-3599 (MTU Home Page Redesign, resolved 28 May 2026); DCS-4423 "
          "(A/B groups); DCS-4261 (Start Top Up CTA); DCS-3940 (promo personalisation); "
          "DCS-4012 and DCS-4399 (tutorial and its events); DCS-3675, DCS-3689, DCS-3895 "
          "(widget Amplitude events); DCS-5289 (toggle rule); DCS-5297 (unintentional "
          "subscriptions); DCS-5375 (retention offer)."),
    ("b", "Design and spec: the IMTU Homepage Figma file and the MTU Home Page "
          "Redesign BR7 Confluence page."),
    ("table", "EVIDENCE"),

    ("cap", "Compiled from Amplitude and Jira on 4 September 2026. Charts use relative "
            "windows where stated, so re-opening them later will show a later window "
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
