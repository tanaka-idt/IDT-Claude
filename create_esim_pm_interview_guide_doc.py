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
from google.auth.transport.requests import Request
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
}

# kinds: h1, h2, h3, p, meta, lead (bold lead-in), bl (bullet, bold lead), b (plain bullet),
#        q (question, bold), lf / rf (indented "Listen for" / "Red flag"), note, table
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
    ("bl", "Distributed teams.", "Core hours are CET with a 9am to 1pm New York overlap, so decisions have to "
           "live in writing."),
    ("h3", "Where the eSIM app funnel stands today"),
    ("p", "From eSIM: What Amplitude Says About the Journey and the eSIM Amplitude dashboard, 90 days to "
          "3 September 2026, BR app. Questions 13 to 15 use these. Give the candidate rounded figures only."),
    ("table", "FUNNEL"),

    ("h2", "4. The 30 minutes"),
    ("table", "PLAN"),

    ("h2", "5. Questions"),
    ("h3", "A. Agile and working with DCS (my filter)"),
    ("q", "1. Walk me through one feature you owned from idea to production. What did you hand the team at each "
          "step, and what came back to you?"),
    ("lf", "Listen for.", "Problem and metric first, then PRD, design review, refinement, stories with acceptance "
           "criteria, sprint planning, QA, release, and a look at the numbers after launch. Knows who does what."),
    ("rf", "Red flag.", "The story ends at \"I gave engineering the requirements\", or never mentions QA or "
           "post-launch data."),
    ("q", "2. You will be a stakeholder for two scrum teams, DPC and DCS, and neither reports to you. DCS is "
          "already over capacity on backend this year. How do you get an eSIM feature into the next sprint?"),
    ("lf", "Listen for.", "Works with the DCS PM and the other product owners, brings a business case and names "
           "what moves out, arrives with groomed stories, sequences backend and provider work first."),
    ("rf", "Red flag.", "Escalation as the first move, or assumes the team takes priorities straight from them."),
    ("q", "3. Our team estimates stories in grooming, and PMs never set the points. Tell me about a time an "
          "estimate came back much bigger than you expected."),
    ("lf", "Listen for.", "Asks why, slices the scope, finds a smaller first release, keeps the team's number."),
    ("rf", "Red flag.", "Negotiates the estimate down, or treats it as padding."),
    ("q", "4. Write acceptance criteria out loud for: \"Check that the customer's phone supports eSIM before "
          "checkout.\""),
    ("lf", "Listen for.", "Criteria QA can pass or fail. Covers supported, unsupported and unknown devices, "
           "carrier-locked phones, iOS and Android, what the customer sees on failure, and the event to track."),
    ("rf", "Red flag.", "\"It should work well and be clear to the user.\""),
    ("q", "5. Halfway through a sprint, a partner changes a plan price or an API, and sales wants it live this "
          "week. What happens to the sprint?"),
    ("lf", "Listen for.", "Separates real urgency from noise, agrees it with the team, swaps out equal scope "
           "instead of adding, protects the sprint goal."),
    ("rf", "Red flag.", "Adds it on top and expects the same delivery."),
    ("q", "6. Tell me about a release that went wrong in production. How did you find out, and what did you "
          "change afterwards?"),
    ("lf", "Listen for.", "Dashboards or alerts, feature flags or a staged rollout, a retro with a concrete "
           "action. Owns their part."),
    ("rf", "Red flag.", "Blames engineering or QA, or heard about it from customers weeks later."),
    ("q", "7. The traveler enters where and when they are going, and gets a recommended plan plus an install "
          "reminder before departure. How would you split that into pieces that each deliver something in a "
          "sprint?"),
    ("lf", "Listen for.", "Vertical slices, backend and catalog first, a flag to hide unfinished work, the "
           "smallest release that proves demand."),
    ("rf", "Red flag.", "One big release after months, or slices by layer that deliver nothing alone."),
    ("q", "8. Core hours are CET with a 9am to 1pm New York overlap, and the teams sit in several time zones. "
          "What do you keep async, and what needs a live meeting?"),
    ("lf", "Listen for.", "Written PRDs and decisions, recorded demos, live time kept for planning, refinement "
           "and hard trade-offs."),
    ("rf", "Red flag.", "Everything is a meeting, or nothing gets written down."),

    ("h3", "B. Roadmap ownership (Emilio's criterion 2)"),
    ("q", "9. Show me a roadmap you personally owned. What was on it, what did you cut, and who disagreed?"),
    ("lf", "Listen for.", "They made the calls, can name what they killed and why, tie it to a metric, and "
           "handled a senior stakeholder who disagreed."),
    ("rf", "Red flag.", "Only \"we\", a roadmap handed down from above, or cannot name a single cut."),
    ("q", "10. Sales, marketing and a wholesale partner each want something in the same quarter. How do you "
          "decide?"),
    ("lf", "Listen for.", "A stated method tied to revenue, margin or conversion, the trade-off made visible, "
           "and a no given with a reason."),
    ("rf", "Red flag.", "Tries to fit everything in, or the loudest voice wins."),

    ("h3", "C. P&L and pricing (Emilio's criterion 3)"),
    ("q", "11. Have you owned a P&L or a margin number? Which lines were yours, and how much did you move them?"),
    ("lf", "Listen for.", "Specific lines (revenue, cost of goods, marketing spend, gross margin), real numbers, "
           "and a decision that moved one of them."),
    ("rf", "Red flag.", "\"I influenced revenue\", no numbers, or finance owned it."),
    ("q", "12. How would you price a Europe 10 GB, 30-day plan? What inputs do you need?"),
    ("lf", "Listen for.", "Wholesale cost, competitor prices, what a local SIM costs on arrival, the margin "
           "target, price tests, and differences by corridor."),
    ("rf", "Red flag.", "Cost plus a markup only, or just \"cheaper than the market leader\"."),

    ("h3", "D. Travel eSIM, the app side (Emilio's criterion 1; David goes deeper)"),
    ("q", "13. About 6 in 10 people who reach our order review screen leave without buying. That screen has a "
          "device compatibility checkbox. What do you look at first, and what would you test?"),
    ("lf", "Listen for.", "Splits by platform, device, and new versus returning buyers; watches session "
           "replays; forms a hypothesis about the checkbox; weighs conversion against refunds from incompatible "
           "phones; proposes an A/B test with a guardrail metric."),
    ("rf", "Red flag.", "Removes the checkbox straight away, or redesigns the screen with no data."),
    ("q", "14. Android buyers convert at a little over half the iOS rate. Why might that happen with eSIM in "
          "particular?"),
    ("lf", "Listen for.", "Different install flows on iOS and Android, a fragmented Android device base, "
           "carrier-locked phones, weaker automatic compatibility detection, QR versus one-tap install."),
    ("rf", "Red flag.", "A generic answer about Android users with no eSIM-specific reason."),
    ("q", "15. About 1 in 5 buyers never taps Install. What is going on, and what would you do?"),
    ("lf", "Listen for.", "People buy days before the trip; activation, not purchase, is the success metric; "
           "install reminders timed to the trip; clearer install guidance; the support cost of failed installs."),
    ("rf", "Red flag.", "Treats the sale as the finish line."),

    ("h3", "E. Ready from day one"),
    ("q", "16. What would your first 30 days here look like?"),
    ("lf", "Listen for.", "Reads the funnel data, uses our app and the competitors', meets DPC, DCS, support and "
           "sales, and ships one small improvement early."),
    ("rf", "Red flag.", "A three-month research phase before any output."),
    ("q", "17. What would you like to ask me?"),
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
         "travelers get stuck; knows the major players", "David Phelps in depth; me on the app funnel (13 to 15)"],
        ["2. PM owning a roadmap", "Built the roadmap, made the cuts, pushed it into sprints", "Me (9, 10) and "
         "Emilio"],
        ["3. Ideally a product P&L", "Accountable for margin by corridor, catalog and pricing", "Emilio; me "
         "briefly (11, 12)"],
        ["DCS filter", "Knows agile and how to get work through DCS", "Me (1 to 8)"],
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
        ["2 to 8 min", "Roadmap and P&L", "9, 11", "10, 12"],
        ["8 to 20 min", "Agile and working with DCS", "1, 2, 4, 5", "3, 6, 7, 8"],
        ["20 to 26 min", "eSIM case from our app", "13", "14, 15"],
        ["26 to 30 min", "Day one and their questions", "16, 17", ""],
    ],
    "SCORE": [
        ["Area", "Strong", "Red flag", "Score", "Notes"],
        ["Agile and DCS fit", "Describes a sprint from the team's side, writes testable criteria, trades scope "
         "instead of pushing the team", "Hands over requirements and waits, or escalates first", "", ""],
        ["eSIM and travel eSIM", "Knows where travelers get stuck; gives eSIM-specific reasons for funnel gaps",
         "Generic e-commerce answers, or telecom detail with no customer view", "", ""],
        ["Roadmap ownership", "Made and defended the cuts personally", "Executed someone else's roadmap", "", ""],
        ["P&L ownership", "Names the lines and the numbers they moved", "\"Influenced revenue\"", "", ""],
        ["Ready from day one", "A concrete 30-day plan that ships something", "A long research phase", "", ""],
        ["Communication", "Short, structured, turns a constraint into a business case", "Rambles, hides in "
         "jargon", "", ""],
    ],
}

STYLE = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3"}
LEADS = ("lead", "bl", "lf", "rf")


def creds():
    c = Credentials.from_authorized_user_file(str(BASE / "token.json"), SCOPES)
    if not c.valid and c.refresh_token:
        c.refresh(Request())
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
                  "spaceBelow": {"magnitude": 2 if kind in ("q", "lf") else 4, "unit": "PT"}}
        fields = "namedStyleType,spaceBelow"
        if kind == "q":
            pstyle["spaceAbove"] = {"magnitude": 8, "unit": "PT"}
            fields += ",spaceAbove"
        if kind in ("lf", "rf"):
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
