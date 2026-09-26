#!/usr/bin/env python3
"""
Creates a one-page Google Doc summarising the Delete Card Warning A/B test report
(BAT-8959, data pulled 11 Sep 2026). Same content as the published HTML summary.

Usage:
    python create_delete_card_warning_summary_doc.py                 # new doc
    python create_delete_card_warning_summary_doc.py --doc-id <id>   # rebuild in place
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
TITLE = "Delete Card Warning (BAT-8959): One-Page Summary"
REPORT = "https://claude.ai/code/artifact/8aef8c43-7df0-425c-a530-9bcb4dbdaa9d?sk=UcO5Qbo9XTAb8KTNQQ0pLw"

LINKS = {
    "the full report": REPORT,
    "Amplitude dashboard": "https://app.amplitude.com/analytics/BOSS/dashboard/98i0g1c0",
    "shared by Jouni Salonen in Slack": "https://idt.slack.com/archives/C0C1083E285/p1789113818108399",
    "HTML version": "https://claude.ai/artifact/QeBr5o9hri1kUeUDvWzSgo",
}

# kinds: h1, h2, p, meta, lead (bold lead-in paragraph), bl (bullet with bold lead), n (numbered), note, table
BLOCKS = [
    ("h1", "Delete Card Warning, BAT-8959"),
    ("meta", "One-page summary · BOSS Revolution · Funding. Source: the full report and its Amplitude dashboard. "
             "Data pulled 11 September 2026. Analysis by Dzmitry Hankevich, shared by Jouni Salonen in Slack. "
             "Also available as an HTML version."),
    ("lead", "Bottom line.", "The warning works where it appears, but it barely appears. In a randomised test it cut "
             "last-card deletions by a third and first-time missing-card failures by almost two thirds. It reaches "
             "only about 2% of eligible users because the test froze on an old app build. The report recommends "
             "turning it on for everyone."),
    ("h2", "What was tested"),
    ("p", "Someone might try to delete their only card while a renewable subscription is charging it. The calling "
          "app then blocks the deletion with a dialog offering “Keep my card” or “Go to subscriptions”, and there "
          "is no way to delete anyway. About 100,000 existing US users on app version 26.8.1 were split at random "
          "between 14 and 21 August. Half saw the warning, and results run to 10 September."),
    ("h2", "Randomised result"),
    ("table", "RESULTS"),
    ("h2", "What the numbers mean"),
    ("bl", "More cancellations are the goal, not churn.", "A subscription whose card is gone keeps failing every "
           "cycle. The warning makes people cancel it first. Without the warning, 61% of these subscriptions failed "
           "within 18 days, against about 5% with it."),
    ("bl", "Deletion is delayed, not prevented.", "The largest group cancelled a subscription and then deleted the "
           "card, typically within four minutes. A third kept the card and changed nothing."),
    ("bl", "Keeping the card did not keep spending.", "Both groups spent less on top-ups afterwards. The warning "
           "changes how subscriptions end more than whether they end."),
    ("bl", "Calling plans get cancelled too.", "The dialog says “your current subscriptions”, and people take it "
           "literally."),
    ("bl", "Purchases were unaffected.", "Completed top-ups grew by the same amount in both groups."),
    ("h2", "Reach and the wider problem"),
    ("p", "The test stopped enrolling once full, so nobody on the current build 26.8.2 gets the warning. Meanwhile "
          "broken subscriptions grow faster than the business."),
    ("table", "REACH"),
    ("h2", "Recommendations, in the report’s order"),
    ("n", "Turn the warning on for everyone by dropping the 26.8.1 and US restrictions."),
    ("n", "Expect reported cancellations to rise, and read them as failures avoided rather than new churn."),
    ("n", "Add a server-side check on card deletion, DTCBE-2903, so Boss Money and every screen are covered. "
          "Re-attach a subscription when a card is added back."),
    ("n", "Log deletions from the new card-details screen, and either switch on or remove the Boss Money version, "
          "which has never fired."),
    ("n", "Track weekly missing-card failures as the main measure. They should start falling within two to four "
          "weeks of full rollout."),
    ("h2", "Caveats"),
    ("bl", "Eligibility is undercounted.", "Calling-plan, Boss Complete and Singit subscribers were not in readable "
           "tables."),
    ("bl", "App deletion counts are a floor.", "The deletion event fires only from the old edit-card screen."),
    ("bl", "Some groups are small.", "Card data is also missing for 11% of users in both groups."),
    ("lead", "Since the report, and not in it.", "The Boss Money flag was switched on in production on 24 September, "
             "under DCS-5336. The Money app build that uses it, 26.9.3, was still a release candidate that day."),
]

TABLES = {
    "RESULTS": [
        ["Measure, people counted once each", "No warning", "Warning", "Change"],
        ["Deleted their last card", "3.20%", "2.16%", "-32%"],
        ["Cancelled a subscription", "6.13%", "7.47%", "+22%"],
        ["Cancelled a calling plan", "0.63%", "1.10%", "+75%"],
        ["First-ever missing-card failure", "0.52%", "0.19%", "-64%"],
    ],
    "REACH": [
        ["Measure", "Value"],
        ["People shown the warning, 15 Aug to 10 Sep", "1,347, about 45 a day"],
        ["People deleting a card each day", "about 2,600"],
        ["Weekly top-up charges failing on a missing card", "35,626, up 51% in ten weeks"],
        ["Newly broken subscriptions that follow an in-app card deletion", "4 in 5"],
    ],
}

STYLE = {"h1": "HEADING_1", "h2": "HEADING_2"}


def creds():
    c = Credentials.from_authorized_user_file(str(BASE / "token.json"), SCOPES)
    if not c.valid and c.refresh_token:
        c.refresh(Request())
        (BASE / "token.json").write_text(c.to_json())
    return c


def text_of(b):
    return b[1] + " " + b[2] if b[0] in ("lead", "bl") else b[1]


def build_requests():
    reqs, cur = [], 1
    for b in BLOCKS:
        kind = b[0]
        line = (f"[[{b[1]}]]" if kind == "table" else text_of(b)) + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        rng = {"startIndex": cur, "endIndex": cur + len(line)}
        reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": {
            "namedStyleType": STYLE.get(kind, "NORMAL_TEXT"),
            "spaceBelow": {"magnitude": 4, "unit": "PT"}}, "fields": "namedStyleType,spaceBelow"}})
        if kind == "bl":
            reqs.append({"createParagraphBullets": {"range": rng, "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind == "n":
            reqs.append({"createParagraphBullets": {"range": rng, "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"}})
        if kind in ("lead", "bl"):
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + len(b[1])},
                                             "textStyle": {"bold": True}, "fields": "bold"}})
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
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {"range": {"startIndex": start, "endIndex": start + len(txt)},
                                             "textStyle": {"bold": True}, "fields": "bold"}})
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
    if not args.doc_id:
        drive.permissions().create(fileId=doc_id, body={"role": "writer", "type": "domain", "domain": "idt.net"}).execute()
    print(f"https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
