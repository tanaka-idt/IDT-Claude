#!/usr/bin/env python3
"""
Creates the Google Doc interview guide for the Travel eSIM Product Manager
candidates (req 3260), from the DCS interviewer's seat: the profile the role
calls for, what the position needs, what working with DCS takes, a 30-minute
plan, questions tied to Emilio del Rio's three criteria, and a scorecard.

Sources: the job req Google Doc and Emilio's Slack thread of 28 Sep 2026.
eSIM funnel numbers come from "eSIM: What Amplitude Says About the Journey"
(90 days to 3 Sep 2026, BR app Prod 650506).

Usage:
    python create_esim_pm_interview_guide_doc.py                 # new doc
    python create_esim_pm_interview_guide_doc.py --doc-id <id>   # rebuild in place
"""

import argparse
import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from linkify_refs import LINK_MAP, linkify

BASE = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]
TITLE = "Travel eSIM PM Interview Guide (DCS)"

JOB_REQ = "https://docs.google.com/document/d/1eyBl3q4v2qbQQKkxYOedP5rD9B6Tu2foIzcP99G9Rcs/edit"
LINKS = {
    "job req": JOB_REQ,
    "Slack thread": "https://idt.slack.com/archives/C09FHTV2TN2/p1790624158749589",
    "eSIM: What Amplitude Says About the Journey":
        "https://docs.google.com/document/d/1sbSOmxSlla-gX8d8MPnZLM9YiwMcytzHMFOCWfLdBCI/edit",
    "DCS FY27 Initiative Plan":
        "https://docs.google.com/document/d/1oxHLqsnsfQ4qObTfFYzwPgrxDrT5i25erhlFL2GOn-I/edit",
    "eSIM Amplitude dashboard": "https://app.amplitude.com/analytics/BOSS/dashboard/024gnsog",
    "IMTU gamification test": "https://app.amplitude.com/analytics/BOSS/dashboard/1dp0yzo6",
    "IMTU events audit": "https://app.amplitude.com/analytics/BOSS/dashboard/bm14j7e2",
}

# kinds: h1, h2, h3, p, meta, lead (bold lead-in), bl (bullet, bold lead), b (plain bullet),
#        h4, q (question, bold), pr / lf / rf (indented "Probe" / "Listen for" / "Red flag"),
#        cx (indented "Why we ask" context, grey italic), table
BLOCKS = [
    ("h1", "Travel eSIM PM Interview Guide (DCS)"),
    ("meta", "Prepared by João Tanaka, 28 September 2026. Senior Product Manager, Travel eSIM, req 3260. "
             "Interview step 4 of 6, 30 minutes, after David Phelps and before Emilio del Rio. "
             "Sources: the job req and Emilio del Rio's Slack thread."),
    ("lead", "Bottom line.", "Emilio wants three things: eSIM ecosystem knowledge (ideally travel eSIM), "
             "experience owning a roadmap, and ideally a product P&L. Emilio added me as the DCS filter: does this "
             "person know agile and what it takes to get work through DCS. David Phelps quizzes eSIM fluency "
             "for DPC. So most of my 30 minutes goes on agile and DCS fit, with shorter probes on roadmap, P&L "
             "and the app side of eSIM."),

    ("h2", "1. The candidate profile we are looking for"),
    ("p", "A commercial consumer PM, not a telecom engineer. The req is explicit that this is a travel-commerce "
          "product role: the eSIM has to work the moment a traveler lands, and it has to earn the next trip's "
          "purchase too."),
    ("bl", "Consumer product owner.", "4+ years owning a consumer product end to end, from pricing and catalog "
           "through purchase, activation and retention."),
    ("bl", "Roadmap owner.", "Has personally built and owned a roadmap, not contributed to someone else's."),
    ("bl", "P&L owner, ideally.", "Has been accountable for revenue and margin, in this role by corridor."),
    ("bl", "Working eSIM knowledge.", "Understands how eSIM works well enough to lead technical discussions, "
           "not at expert level. Best case: has run, or competed against, a major travel eSIM product."),
    ("bl", "Agile delivery.", "Has shipped complex technical products with designers, engineers and QA in "
           "scrum teams, and gives useful feedback on technical designs."),
    ("bl", "Data fluent.", "Runs funnel analysis and A/B tests alone in Amplitude, GA or Looker/Power BI."),
    ("bl", "Sharp communicator.", "Turns a technical or pricing constraint into a one-slide business case."),
    ("bl", "Nice to have.", "Travel industry background: OTAs, airlines, hospitality or travel-commerce."),
    ("table", "ROLE"),

    ("h2", "2. What the position needs"),
    ("h3", "What they will own"),
    ("b", "The travel eSIM roadmap and product lifecycle, end to end."),
    ("b", "Purchase to activation: browse, purchase, QR or eSIM install, first connection."),
    ("b", "The data-plan catalog and pricing per corridor, against local SIM cost, margin targets and "
          "competitors."),
    ("b", "The metrics: conversion, activation, ARPU, repeat purchase and margin by corridor."),
    ("b", "Roaming and wholesale partners for coverage, capacity and cost."),
    ("b", "PRDs, and pushing priorities into sprint planning for several scrum teams."),
    ("b", "Launches with engineering, marketing, sales and support, plus sales materials and B2B onboarding."),
    ("h3", "Emilio's three criteria, and who tests them"),
    ("table", "EMILIO"),
    ("p", "Emilio's overall bar: someone ready to hit the ground running, who adds travel eSIM product "
          "knowledge to the team and helps execute the eSIM vision."),

    ("h2", "3. What working with DCS takes (my filter)"),
    ("p", "DCS is one of the two scrum teams this PM leans on, alongside DPC. They will not manage either team, "
          "so everything they want built reaches us through the backlog. What that means in practice:"),
    ("bl", "Ready work, not ideas.", "A PRD and a design, then stories with acceptance criteria that QA can "
           "pass or fail. The team estimates backend and app stories in grooming; the PM never sets the points."),
    ("bl", "Work runs in order.", "PM, then Design, TPM, BE, App and QA. Backend and provider dependencies (DPC, "
           "Zendit) have to be ready before app stories enter a sprint."),
    ("bl", "Capacity is already spoken for.", "The DCS FY27 Initiative Plan needs 57 backend FTE sprints against "
           "51 available, so eSIM work gets in by trading against other goals with a business case, not by "
           "escalation."),
    ("bl", "Measurement is part of the story.", "Every feature ships with its Amplitude events defined up front. "
           "The eSIM events in the app already have traps: the Buy button is an entry tile, not checkout."),
    ("bl", "Releases are app versions.", "Features ship in versioned app builds with a phased store rollout, "
           "and users move to a new version over weeks. A launch or campaign needs a flag and a version filter."),
    ("bl", "Distributed teams.", "Core hours are CET with a 9am to 1pm New York overlap, so decisions have to "
           "live in writing."),
    ("h3", "Where the eSIM app funnel stands today"),
    ("p", "From eSIM: What Amplitude Says About the Journey and the eSIM Amplitude dashboard, 90 days to "
          "3 September 2026, BR app. Questions 17 to 19 use these. Give the candidate rounded figures only."),
    ("table", "FUNNEL"),

    ("h2", "4. The 30 minutes"),
    ("table", "PLAN"),

    ("h2", "5. Questions"),
    ("h3", "A. Agile and working with DCS (my filter)"),
    ("p", "Ask for a real example first, then use the probe. Strong answers name the artifact (PRD, story, flag, "
          "dashboard) and who owned each step. Answers that stay hypothetical are a weak signal. Must ask: 1, 3, "
          "5, 7 and 9."),

    ("h4", "How they deliver"),
    ("q", "1. Pick one feature you shipped in a mobile app in the last year. Walk me through it from the first "
          "PRD to the week after release. What did you hand the team at each step?"),
    ("pr", "Probe.", "What was in the PRD that was not in the stories? Who wrote the stories? When did QA first "
           "see it?"),
    ("lf", "Listen for.", "Problem and success metric first. The PRD and the stories are different documents. "
           "Design finished and the API agreed before app work started. QA involved in refinement, not only at "
           "the end. Checked the numbers after release."),
    ("rf", "Red flag.", "Ends at \"I gave engineering the requirements\", cannot say who wrote the stories, or "
           "never looked at the data after launch."),
    ("q", "2. At DCS an app story cannot start until its design is final and the backend API is documented. What "
          "does \"ready for sprint planning\" mean to you, and what do you do when a story you need is not ready?"),
    ("pr", "Probe.", "Tell me about a story you pulled out of a sprint because it was not ready."),
    ("lf", "Listen for.", "A checklist in their own words: acceptance criteria, design link, API contract, "
           "dependencies, feature flag, analytics. Refines one or two sprints ahead of the team. Would rather slip "
           "a sprint than start half-ready."),
    ("rf", "Red flag.", "\"The developers work out the details during the sprint.\""),
    ("q", "3. Write acceptance criteria out loud, three to five items, for: \"Check that the customer's phone "
          "supports eSIM before checkout.\""),
    ("pr", "Probe.", "What happens on an iPad? On a phone locked to a carrier? When the check cannot tell?"),
    ("lf", "Listen for.", "Criteria QA can pass or fail. Covers supported, unsupported and unknown devices, "
           "carrier-locked phones, iOS and Android, what the customer sees and can do on failure, and the event "
           "to track. Says what is out of scope."),
    ("rf", "Red flag.", "\"It should work well and be clear to the user\", or describes the screen instead of "
           "testable behavior."),
    ("q", "4. Which scrum meetings do you attend, what do you bring to each, and what do you keep in writing "
          "when the team spans CET to New York?"),
    ("pr", "Probe.", "Have you ever rejected a story in sprint review? Why?"),
    ("lf", "Listen for.", "Arrives at refinement and planning with prepared stories. Accepts or rejects work in "
           "review against the acceptance criteria. Joins the retro when invited. Decisions and PRDs live in "
           "writing; live time is kept for planning and hard trade-offs."),
    ("rf", "Red flag.", "Skips refinement, treats the review as a demo only, or decisions live in calls."),

    ("h4", "Working inside our constraints"),
    ("q", "5. You will bring eSIM work to two scrum teams, DPC and DCS, and neither reports to you. DCS already "
          "has more backend work planned this year than it can deliver. You need an eSIM feature in the next "
          "sprint. Walk me through the week before sprint planning."),
    ("pr", "Probe.", "What would you offer to take out? Who do you talk to first?"),
    ("lf", "Listen for.", "Talks to the DCS PM before planning, not during it. Brings a business case in numbers "
           "and names what moves out. Arrives with groomed stories. Accepts a later sprint if the case loses."),
    ("rf", "Red flag.", "Escalation as the first move, \"everything is P1\", or assumes the team takes "
           "priorities straight from them."),
    ("q", "6. The team estimates in grooming, and PMs never set the points. You bring \"recommend a plan from "
          "the traveler's destination and dates, then remind them to install before departure\", and it comes "
          "back at three sprints. What do you do?"),
    ("pr", "Probe.", "What is the smallest version you would ship first, and how would you know it worked?"),
    ("lf", "Listen for.", "Asks what drives the size. Splits into vertical slices that each ship, for example "
           "destination-only recommendations first and the reminder later. Keeps the team's number. Sets the "
           "metric for the first slice."),
    ("rf", "Red flag.", "Negotiates the estimate down, treats it as padding, or slices by layer (all backend "
           "first, screens in sprint three) so nothing ships on its own."),
    ("q", "7. DPC owns the eSIM backend. DCS sprint planning is tomorrow, and the DPC endpoint your app story "
          "needs is late. What do you do?"),
    ("pr", "Probe.", "Would you let the app team build against a mocked API?"),
    ("lf", "Listen for.", "Saw the risk before planning because the dependency was tracked and linked. Options "
           "ready: an agreed contract plus a mock, a flag, or swapping in another ready story. Tells both teams "
           "and the stakeholders early. Does not leave DCS idle."),
    ("rf", "Red flag.", "Finds out in planning, pushes the app team to start without a contract, or blames the "
           "other team."),
    ("q", "8. Halfway through a sprint, a wholesale partner changes a plan price or an API, and sales wants it "
          "live this week. What happens to the sprint?"),
    ("pr", "Probe.", "Who decides whether it goes in?"),
    ("lf", "Listen for.", "Separates real urgency from noise and asks whether a price change is configuration "
           "rather than code. Agrees it with the team, swaps out equal scope, protects the sprint goal."),
    ("rf", "Red flag.", "Adds it on top and expects the same delivery, or goes straight to a developer."),

    ("h4", "Mobile releases and measurement"),
    ("q", "9. Your eSIM feature shipped in the latest app release. Marketing wants to launch a campaign pointing "
          "to it on Monday. What do you check first?"),
    ("pr", "Probe.", "What share of users do you expect on the new version a week after release?"),
    ("lf", "Listen for.", "Phased store rollout and slow version adoption. The feature flag state and who "
           "switches it on. A campaign audience filtered to app versions that have the feature. Proof in "
           "production analytics by app version."),
    ("rf", "Red flag.", "Assumes \"released\" means every user has it, with no idea of version adoption or "
           "flags."),
    ("cx", "Why we ask.", "In September the IMTU gamification test reached 2 of 5,000 entrants, because its "
           "trigger only shipped in 26.9.1 and almost nobody had that version yet."),
    ("q", "10. How do you specify analytics for a new feature? Who decides the event names, and how do you check "
          "them after release?"),
    ("pr", "Probe.", "Our eSIM Buy button is an entry tile, but a funnel built on it reads like checkout and "
           "reports conversion about 7 times too low. How would you catch that before it misleads anyone?"),
    ("lf", "Listen for.", "Events and properties written into the story before build, against a tracking plan. "
           "QA checks the events. The first days of production data compared with expected volumes. Knows a "
           "button name is not a funnel step."),
    ("rf", "Red flag.", "\"The developers add the tracking\", or analytics only after launch."),
    ("cx", "Why we ask.", "The IMTU events audit found 179 events, none documented and 71% never queried."),
    ("q", "11. The same eSIM catalog can be sold in our app, on the web and through partners. A pricing rule "
          "changes, or the compatibility check has a bug. How do you decide whether to fix it in the app, on the "
          "web, or in the backend?"),
    ("pr", "Probe.", "What does fixing it only in the app cost you?"),
    ("lf", "Listen for.", "A backend fix covers every surface and does not wait for a store release. An app fix "
           "waits for rollout and adoption. Keeps app and web in step. One owner per rule."),
    ("rf", "Red flag.", "No view on the difference, or fixes it wherever the bug was reported."),
    ("cx", "Why we ask.", "The delete-card warning shipped in one app and still needed a server-side fix, "
           "DTCBE-2903, to cover the other screens and apps."),
    ("q", "12. Tell me about a release that went wrong in production. How did you find out, and what changed "
          "afterwards?"),
    ("pr", "Probe.", "What would you watch in the first 48 hours after an eSIM release?"),
    ("lf", "Listen for.", "Dashboards or alerts, a staged rollout or a flag to switch it off, a retro with a "
           "concrete action. Owns their part. For eSIM: purchase success, install success, failed orders, "
           "support contacts."),
    ("rf", "Red flag.", "Blames engineering or QA, or heard about it from customers weeks later."),

    ("h3", "B. Roadmap ownership (Emilio's criterion 2)"),
    ("q", "13. Show me a roadmap you personally owned. What was on it, what did you cut, and who disagreed?"),
    ("lf", "Listen for.", "They made the calls, can name what they killed and why, tie it to a metric, and "
           "handled a senior stakeholder who disagreed."),
    ("rf", "Red flag.", "Only \"we\", a roadmap handed down from above, or cannot name a single cut."),
    ("q", "14. Sales, marketing and a wholesale partner each want something in the same quarter. How do you "
          "decide?"),
    ("lf", "Listen for.", "A stated method tied to revenue, margin or conversion, the trade-off made visible, "
           "and a no given with a reason."),
    ("rf", "Red flag.", "Tries to fit everything in, or the loudest voice wins."),

    ("h3", "C. P&L and pricing (Emilio's criterion 3)"),
    ("q", "15. Have you owned a P&L or a margin number? Which lines were yours, and how much did you move them?"),
    ("lf", "Listen for.", "Specific lines (revenue, cost of goods, marketing spend, gross margin), real numbers, "
           "and a decision that moved one of them."),
    ("rf", "Red flag.", "\"I influenced revenue\", no numbers, or finance owned it."),
    ("q", "16. How would you price a Europe 10 GB, 30-day plan? What inputs do you need?"),
    ("lf", "Listen for.", "Wholesale cost, competitor prices, what a local SIM costs on arrival, the margin "
           "target, price tests, and differences by corridor."),
    ("rf", "Red flag.", "Cost plus a markup only, or just \"cheaper than the market leader\"."),

    ("h3", "D. Travel eSIM, the app side (Emilio's criterion 1; David goes deeper)"),
    ("q", "17. About 6 in 10 people who reach our order review screen leave without buying. That screen has a "
          "device compatibility checkbox. What do you look at first, and what would you test?"),
    ("lf", "Listen for.", "Splits by platform, device, and new versus returning buyers; watches session "
           "replays; forms a hypothesis about the checkbox; weighs conversion against refunds from incompatible "
           "phones; proposes an A/B test with a guardrail metric."),
    ("rf", "Red flag.", "Removes the checkbox straight away, or redesigns the screen with no data."),
    ("q", "18. Android buyers convert at a little over half the iOS rate. Why might that happen with eSIM in "
          "particular?"),
    ("lf", "Listen for.", "Different install flows on iOS and Android, a fragmented Android device base, "
           "carrier-locked phones, weaker automatic compatibility detection, QR versus one-tap install."),
    ("rf", "Red flag.", "A generic answer about Android users with no eSIM-specific reason."),
    ("q", "19. About 1 in 5 buyers never taps Install. What is going on, and what would you do?"),
    ("lf", "Listen for.", "People buy days before the trip; activation, not purchase, is the success metric; "
           "install reminders timed to the trip; clearer install guidance; the support cost of failed installs."),
    ("rf", "Red flag.", "Treats the sale as the finish line."),

    ("h3", "E. Ready from day one"),
    ("q", "20. What would your first 30 days here look like?"),
    ("lf", "Listen for.", "Reads the funnel data, uses our app and the competitors', meets DPC, DCS, support and "
           "sales, and ships one small improvement early."),
    ("rf", "Red flag.", "A three-month research phase before any output."),
    ("q", "21. What would you like to ask me?"),
    ("lf", "Listen for.", "Questions about how the teams plan, their capacity, the data, and the eSIM supply "
           "side."),
    ("rf", "Red flag.", "Nothing about the work itself."),

    ("h2", "6. Scorecard"),
    ("p", "Score 1 to 4: 1 no evidence, 2 some evidence, 3 clear evidence, 4 strong evidence with numbers. "
          "The first row is the DCS filter Emilio asked me for."),
    ("table", "SCORE"),

    ("h2", "7. Hand-off to Emilio"),
    ("b", "Read David Phelps's notes from step 3 first and skip what David already covered."),
    ("b", "Send Emilio a DCS verdict (pass, pass with concerns, or fail) with the reason in one sentence."),
    ("b", "Add one line on each of Emilio's three criteria: eSIM, roadmap and P&L."),
    ("b", "Flag the pattern the req warns about: strong on scope and trade-offs but vague on data or numbers "
          "usually means the person looks right on paper but is not a commerce PM."),
]

TABLES = {
    "ROLE": [
        ["Role facts", "From the job req"],
        ["Title", "Senior Product Manager, Travel eSIM (req 3260), 1 headcount"],
        ["Division and manager", "IDT Digital Payments; hiring manager Emilio del Rio"],
        ["Team", "No direct reports. Works with DPC (12+ people, the provider team) and DCS (10 people, app "
                 "and web). Sales and marketing are internal customers"],
        ["Location and hours", "Europe (including Belarus, Georgia, Moldova); Latam and US considered. CET, "
                               "with a 9am to 1pm New York overlap"],
        ["Compensation band", "USD 100,000 a year"],
    ],
    "EMILIO": [
        ["Criterion", "What it means for this role", "Who tests it"],
        ["1. eSIM ecosystem, ideally travel eSIM", "Knows the path from purchase to first connection and where "
         "travelers get stuck; knows the major players", "David Phelps in depth; me on the app funnel (17 to 19)"],
        ["2. PM owning a roadmap", "Built the roadmap, made the cuts, pushed it into sprints", "Me (13, 14) and "
         "Emilio"],
        ["3. Ideally a product P&L", "Accountable for margin by corridor, catalog and pricing", "Emilio; me "
         "briefly (15, 16)"],
        ["DCS filter", "Knows agile and how to get work through DCS", "Me (1 to 12)"],
    ],
    "FUNNEL": [
        ["Measure", "Value", "Say to the candidate"],
        ["End-to-end conversion, eSIM home to purchase", "2.27% (2,014 of 88,600 users)", "About 2%"],
        ["Lost between order review and submit", "62.9% (4,242 of 6,749)", "About 6 in 10"],
        ["Conversion by platform", "iOS 2.71%, Android 1.52%", "Android a little over half of iOS"],
        ["Submitted orders that succeed", "80.3%, median 17 seconds", "Most, within seconds"],
        ["Buyers who never tap Install Now", "435 of 2,042 (21%)", "About 1 in 5"],
    ],
    "PLAN": [
        ["Time", "Block", "Must ask", "If time"],
        ["0 to 2 min", "Intro: who I am and how DCS works with this role", "", ""],
        ["2 to 7 min", "Roadmap and P&L", "13, 15", "14, 16"],
        ["7 to 22 min", "Agile and working with DCS", "1, 3, 5, 7, 9", "2, 4, 6, 8, 10 to 12"],
        ["22 to 27 min", "eSIM case from our app", "17", "18, 19"],
        ["27 to 30 min", "Day one and their questions", "20, 21", ""],
    ],
    "SCORE": [
        ["Area", "Strong", "Red flag", "Score", "Notes"],
        ["Agile and DCS fit", "Describes a sprint from the team's side, writes testable criteria, trades scope "
         "instead of pushing the team, knows a shipped release is not an adopted one", "Hands over requirements and waits, or escalates first", "", ""],
        ["eSIM and travel eSIM", "Knows where travelers get stuck; gives eSIM-specific reasons for funnel gaps",
         "Generic e-commerce answers, or telecom detail with no customer view", "", ""],
        ["Roadmap ownership", "Made and defended the cuts personally", "Executed someone else's roadmap", "", ""],
        ["P&L ownership", "Names the lines and the numbers they moved", "\"Influenced revenue\"", "", ""],
        ["Ready from day one", "A concrete 30-day plan that ships something", "A long research phase", "", ""],
        ["Communication", "Short, structured, turns a constraint into a business case", "Rambles, hides in "
         "jargon", "", ""],
    ],
}

STYLE = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3", "h4": "HEADING_4"}
LEADS = ("lead", "bl", "pr", "lf", "rf", "cx")
INDENTED = ("pr", "lf", "rf", "cx")


def creds():
    c = Credentials.from_authorized_user_file(str(BASE / "token.json"), SCOPES)
    if not c.valid:
        try:
            c.refresh(Request())
        except RefreshError:
            # Revoked or expired refresh token: re-authorize in the browser.
            flow = InstalledAppFlow.from_client_secrets_file(str(BASE / "credentials.json"), SCOPES)
            c = flow.run_local_server(port=0)
        (BASE / "token.json").write_text(c.to_json())
    return c


def text_of(b):
    return b[1] + " " + b[2] if b[0] in LEADS else b[1]


def build_requests():
    reqs, cur = [], 1
    for b in BLOCKS:
        kind = b[0]
        line = (f"[[{b[1]}]]" if kind == "table" else text_of(b)) + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        rng = {"startIndex": cur, "endIndex": cur + len(line)}
        pstyle = {"namedStyleType": STYLE.get(kind, "NORMAL_TEXT"),
                  "spaceBelow": {"magnitude": 2 if kind in ("q", "pr", "lf") else 4, "unit": "PT"}}
        fields = "namedStyleType,spaceBelow"
        if kind == "q":
            pstyle["spaceAbove"] = {"magnitude": 8, "unit": "PT"}
            fields += ",spaceAbove"
        if kind in INDENTED:
            pstyle["indentStart"] = {"magnitude": 18, "unit": "PT"}
            pstyle["indentFirstLine"] = {"magnitude": 18, "unit": "PT"}
            fields += ",indentStart,indentFirstLine"
        reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": pstyle, "fields": fields}})
        if kind in ("bl", "b"):
            reqs.append({"createParagraphBullets": {"range": rng, "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind in LEADS:
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + len(b[1])},
                                             "textStyle": {"bold": True}, "fields": "bold"}})
        if kind == "q":
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + len(line) - 1},
                                             "textStyle": {"bold": True}, "fields": "bold"}})
        if kind == "rf":
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + len(b[1])},
                                             "textStyle": {"foregroundColor": {"color": {"rgbColor": {
                                                 "red": 0.72, "green": 0.11, "blue": 0.11}}}},
                                             "fields": "foregroundColor"}})
        if kind == "cx":
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + len(line) - 1},
                                             "textStyle": {"italic": True, "fontSize": {"magnitude": 9.5, "unit": "PT"},
                                                           "foregroundColor": {"color": {"rgbColor": {
                                                               "red": 0.4, "green": 0.4, "blue": 0.4}}}},
                                             "fields": "italic,fontSize,foregroundColor"}})
        if kind == "meta":
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + len(line) - 1},
                                             "textStyle": {"italic": True, "fontSize": {"magnitude": 9.5, "unit": "PT"}},
                                             "fields": "italic,fontSize"}})
        cur += len(line)
    return reqs


def insert_table(docs, doc_id, marker, data):
    doc = docs.documents().get(documentId=doc_id).execute()
    for el in doc["body"]["content"]:
        t = "".join(r.get("textRun", {}).get("content", "") for r in el.get("paragraph", {}).get("elements", []))
        if t.strip() == f"[[{marker}]]":
            idx, plen = el["startIndex"], len(t)
            break
    else:
        raise SystemExit(f"marker {marker} not found")
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx, "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx}, "rows": len(data), "columns": len(data[0])}}]}).execute()
    doc = docs.documents().get(documentId=doc_id).execute()
    table = next(el for el in doc["body"]["content"] if "table" in el and el["startIndex"] >= idx - 2)
    cells = [(cell["content"][0]["startIndex"], r, c)
             for r, row in enumerate(table["table"]["tableRows"]) for c, cell in enumerate(row["tableCells"])]
    reqs = []
    for start, r, c in sorted(cells, reverse=True):
        txt = data[r][c]
        if not txt:
            continue
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        reqs.append({"updateTextStyle": {"range": {"startIndex": start, "endIndex": start + len(txt)},
                                         "textStyle": {"bold": r == 0,
                                                       "fontSize": {"magnitude": 9.5, "unit": "PT"}},
                                         "fields": "bold,fontSize"}})
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": reqs}).execute()
    time.sleep(0.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc-id")
    args = ap.parse_args()
    c = creds()
    docs, drive = build("docs", "v1", credentials=c), build("drive", "v3", credentials=c)
    if args.doc_id:
        doc_id = args.doc_id
        end = docs.documents().get(documentId=doc_id).execute()["body"]["content"][-1]["endIndex"]
        if end > 2:
            docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
                {"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1}}}]}).execute()
    else:
        doc_id = docs.documents().create(body={"title": TITLE}).execute()["documentId"]
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": build_requests()}).execute()
    for marker, data in TABLES.items():
        insert_table(docs, doc_id, marker, data)
    linkify(docs, doc_id, {**LINK_MAP, **LINKS})
    print(f"https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
