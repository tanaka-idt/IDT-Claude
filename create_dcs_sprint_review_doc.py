#!/usr/bin/env python3
"""
Creates ONE Google Doc: "DCS: What We Shipped, Sprints 71 to 76".

A delivery review of the DCS board covering sprints 71 to 76 (17 June to
8 September 2026, sprint 76 still running). 543 issues, 638 story points,
50 epics, pulled from Jira and grouped by epic, then ranked by business
importance rather than by effort.

The epic table is generated from scratchpad/epic_table.json, which is built
from the Jira export. Epics below 5 points and 6 issues are folded into a
remainder line.
"""

import json
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
EPIC_JSON = Path("/private/tmp/claude-501/-Users-joaotanaka-IDT-Claude/"
                 "e07b5cbe-00b9-4b1c-a043-48993f66790a/scratchpad/epic_table.json")

TITLE = "DCS: What We Shipped, Sprints 71 to 76"

MARGIN_PT = 42

# ----------------------------------------------------------------- tables ----

GLANCE = [
    ["", "Issues", "Points", "Share of points", "Done"],
    ["Subscriptions (7 epics)", "134", "134", "21%", "52%"],
    ["Platform, tech debt and API (13 epics)", "138", "213", "33%", "67%"],
    ["Adjacent products: eGift, eSIM, RAF (8 epics)", "100", "100", "16%", "75%"],
    ["Cross-sell and insurance (4 epics)", "57", "63", "10%", "49%"],
    ["Notifications (2 epics)", "33", "47", "7%", "76%"],
    ["Everything else", "81", "81", "13%", "58%"],
]

EPICS = [["Epic", "Name", "Theme", "Issues", "Points", "Done", "Sprints"]]
EPICS += json.loads(EPIC_JSON.read_text())
EPICS += [["", "36 epics above cover 517 of 543 issues and 614 of 638 points. "
               "The remaining 14 epics are 1 to 3 issues each.",
           "", "26", "24", "", ""]]

TABLES = [("GLANCE", GLANCE), ("EPICS", EPICS)]

C_HEAD = "#EEEBE5"
C_WARN = "#FBE9E9"
C_GOOD = "#E3F1EA"

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Delivery review  ·  DCS board 2057  ·  sprints 71 to 76 "
            "(17 June to 8 September 2026)  ·  Joao Tanaka  ·  1 September 2026"),

    ("h2", "At a glance"),
    ("p", "543 issues, 638 story points, 50 epics. Throughput held steady "
          "throughout: 96 to 140 issues and 89 to 146 points per sprint, with "
          "sprint 76 the busiest. Note that 36% of all issues are QA tickets "
          "paired to a development ticket, so raw issue counts run roughly 1.5 "
          "times the underlying work."),
    ("table", "GLANCE"),

    ("h2", "Ranked by importance"),
    ("p", "Ordered by business weight, not by effort. Where the two diverge is "
          "itself worth noting, and it does diverge sharply at the top."),

    ("b", "1. IMTU Subscriptions.  134 issues, 134 points, 21% of all effort, "
          "spread across seven epics: Subscription Promos (DCS-4387), "
          "Subscription FY26 (DCS-2846), Subly (DCS-3879), Subscriptions V2 "
          "(DCS-5297), Cancellation (DCS-4707), Toggle and Frequency, and "
          "Subscription CVV. This is the strategic centre of the period and the "
          "clearest retention lever we have. The engine room is finished: the "
          "Subly migration is 84% done, and renewal reminders, the savings-to-date "
          "endpoint and the recurring Stripe RPS spikes are all resolved. The "
          "customer-facing layer is not: Promos sits at 41%, V2 at 25%, "
          "Cancellation at 44%."),

    ("b", "2. Platform, tech debt and API.  138 issues, 213 points, 33% of all "
          "effort, 67% done. Tech Debt FY26 (DCS-3173) alone is the single "
          "largest epic of the period at 85 points across 66 issues. Add the "
          "MTU TechAudit (DCS-4675), the on-prem k8s migration (DCS-4772), "
          "Pulsar to Kafka, and DTC API (DCS-3231) at 93% done. A third of "
          "capacity went here, more than any single product initiative."),

    ("b", "3. Notification service for validity-based products.  DCS-3398, 30 "
          "issues, 44 points, 80% done. The quiet success of the period and the "
          "most complete large initiative on the board. Expiry reminders carrying "
          "personalised recipient and offer details, deep links into SMS and push, "
          "Grafana analytics on what was sent, and a rework of firing-time "
          "configuration. It drives repeat purchase directly and is nearly "
          "finished."),

    ("b", "4. Cross-sell and insurance.  57 issues, 63 points, 49% done. X-sell "
          "Deals (DCS-4386) is the problem child: 38% done and touched in every "
          "sprint from 65 through 76, with the Calling Plans cross-sell currently "
          "BLOCKED. The Insurance modular component (DCS-5079) is the newer and "
          "healthier strand, started in sprint 74 and already shipping the "
          "subscription-to-insurance cross-sell behind a feature flag."),

    ("b", "5. Adjacent products: eGift, eSIM and RAF.  100 issues, 100 points, "
          "75% done, the best completion rate of any theme. eGift My Activity "
          "(DCS-5002) shipped end to end at 100%. The RAF Share Sheet (DCS-4696) "
          "replaced the native share sheet at 93%. eSIM V2 delivered the new "
          "search, package speed information and deleted-eSIM handling."),

    ("b", "6. New payment rails and channels.  Small but forward-looking. The "
          "Google Pay and Apple Pay spike (DCS-5238) opened in sprint 76, "
          "alongside the IVA IMTU integration and the WhatsApp application ids "
          "landing inside DTC API."),

    ("h2", "Three things worth attention"),

    ("b", "Effort and importance diverge at the top.  Platform work outweighs the "
          "largest product initiative by 60% in points. That may well be the right "
          "call in the year of the TechAudit and the on-prem migration, but it is "
          "the sort of ratio a stakeholder will ask about, so it is better to "
          "have the answer ready than to be asked for it."),

    ("b", "16% of tickets were abandoned.  89 of 543 issues ended in \"Won't fix\". "
          "Much of that is QA twins closed when their parent was dropped, but the "
          "rate still points to scope churn worth a look, particularly inside "
          "Subscription Promos where nine items were dropped."),

    ("b", "Two initiatives are stuck rather than slow.  X-sell has been open across "
          "12 sprints at 38% complete with blocked items. Color Swap (DCS-4209) "
          "has 14 issues and 14% completion across sprints 66 to 76. Both are "
          "candidates for either a deliberate push or a deliberate close."),

    ("h2", "Every epic"),
    ("p", "Sorted by points. \"Sprints\" counts how many of the six this epic was "
          "touched in, so a 6 means continuous work throughout the window."),
    ("table", "EPICS"),
]

SIZE_MAP = {"h1": 16, "h2": 11, "p": 9.5, "b": 9.5, "cap": 8}
STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "cap": "NORMAL_TEXT"}


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


def hexrgb(h):
    return {"color": {"rgbColor": {
        "red": int(h[1:3], 16) / 255,
        "green": int(h[3:5], 16) / 255,
        "blue": int(h[5:7], 16) / 255}}}


def build_requests(blocks):
    reqs, cur = [], 1
    for kind, text in blocks:
        if kind == "table":
            line = f"[[TABLE:{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += len(line)
            continue

        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        above, below = (9, 3) if kind == "h2" else (0, 3)
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(line)},
            "paragraphStyle": {"namedStyleType": STYLE_MAP[kind],
                               "spaceAbove": {"magnitude": above, "unit": "PT"},
                               "spaceBelow": {"magnitude": below, "unit": "PT"},
                               "lineSpacing": 108},
            "fields": "namedStyleType,spaceAbove,spaceBelow,lineSpacing"}})

        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})

        style = {"fontSize": {"magnitude": SIZE_MAP[kind], "unit": "PT"}}
        fields = "fontSize"
        if kind == "cap":
            style["italic"] = True
            fields += ",italic"
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(text)},
            "textStyle": style, "fields": fields}})

        # Bold the lead-in of each ranked bullet, up to the double space.
        if kind == "b" and "  " in text:
            lead = text.split("  ")[0]
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


def insert_table(docs, doc_id, marker, data, widths, font=8.5):
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = plen = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[TABLE:{marker}]]":
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
    time.sleep(1.2)

    doc = docs.documents().get(documentId=doc_id).execute()
    table_el = next((el for el in doc["body"]["content"]
                     if "table" in el and el["startIndex"] >= idx - 2), None)
    if table_el is None:
        print(f"  ! table {marker} not found after insert")
        return False
    t_start = table_el["startIndex"]

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
        style = {"fontSize": {"magnitude": font, "unit": "PT"}}
        fields = "fontSize"
        if r == 0 or (c == 0 and marker == "GLANCE"):
            style["bold"] = True
            fields += ",bold"
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": start, "endIndex": start + len(txt)},
            "textStyle": style, "fields": fields}})
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": start, "endIndex": start + len(txt)},
            "paragraphStyle": {"spaceAbove": {"magnitude": 1, "unit": "PT"},
                               "spaceBelow": {"magnitude": 1, "unit": "PT"},
                               "lineSpacing": 100},
            "fields": "spaceAbove,spaceBelow,lineSpacing"}})
    batched(docs, doc_id, reqs, size=40)

    style_reqs = []
    for r in range(len(data)):
        fill = None
        if r == 0:
            fill = C_HEAD
        elif marker == "EPICS":
            pct = data[r][5].rstrip("%")
            if pct.isdigit():
                if int(pct) <= 45:
                    fill = C_WARN
                elif int(pct) >= 90:
                    fill = C_GOOD
        if not fill:
            continue
        for c in range(len(data[0])):
            style_reqs.append({"updateTableCellStyle": {
                "tableRange": {"tableCellLocation": {
                    "tableStartLocation": {"index": t_start},
                    "rowIndex": r, "columnIndex": c}, "rowSpan": 1, "columnSpan": 1},
                "tableCellStyle": {
                    "backgroundColor": hexrgb(fill),
                    "paddingTop": {"magnitude": 1.5, "unit": "PT"},
                    "paddingBottom": {"magnitude": 1.5, "unit": "PT"},
                    "paddingLeft": {"magnitude": 4, "unit": "PT"},
                    "paddingRight": {"magnitude": 4, "unit": "PT"}},
                "fields": ("backgroundColor,paddingTop,paddingBottom,"
                           "paddingLeft,paddingRight")}})
    for c, w in enumerate(widths):
        style_reqs.append({"updateTableColumnProperties": {
            "tableStartLocation": {"index": t_start},
            "columnIndices": [c],
            "tableColumnProperties": {"widthType": "FIXED_WIDTH",
                                      "width": {"magnitude": w, "unit": "PT"}},
            "fields": "widthType,width"}})
    batched(docs, doc_id, style_reqs, size=40)
    return True


def clear_body(docs, doc_id):
    doc = docs.documents().get(documentId=doc_id).execute()
    end = doc["body"]["content"][-1]["endIndex"]
    if end > 2:
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
            {"deleteContentRange": {"range": {"startIndex": 1,
                                              "endIndex": end - 1}}}]}).execute()
        time.sleep(0.5)


def main(doc_id=None):
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    if doc_id:
        clear_body(docs, doc_id)
        print(f"Rebuilding doc in place: {doc_id}")
    else:
        doc = docs.documents().create(body={"title": TITLE}).execute()
        doc_id = doc["documentId"]
        print(f"Created doc: {doc_id}")

    m = {"magnitude": MARGIN_PT, "unit": "PT"}
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"updateDocumentStyle": {
            "documentStyle": {"marginTop": m, "marginBottom": m,
                              "marginLeft": m, "marginRight": m},
            "fields": "marginTop,marginBottom,marginLeft,marginRight"}}]}).execute()

    batched(docs, doc_id, build_requests(BLOCKS))
    print("Inserted text blocks")

    insert_table(docs, doc_id, "GLANCE", GLANCE, [196, 60, 60, 90, 62], font=9)
    print("  table GLANCE: ok")
    insert_table(docs, doc_id, "EPICS", EPICS, [62, 200, 68, 48, 48, 44, 58], font=8)
    print(f"  table EPICS: ok ({len(EPICS) - 1} rows)")

    linkify(docs, doc_id, dict(LINK_MAP))
    print("Linkified references")

    existing = drive.permissions().list(
        fileId=doc_id, fields="permissions(type,domain)").execute()
    if not any(p.get("type") == "domain" and p.get("domain") == "idt.net"
               for p in existing.get("permissions", [])):
        drive.permissions().create(
            fileId=doc_id,
            body={"role": "writer", "type": "domain", "domain": "idt.net"},
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
