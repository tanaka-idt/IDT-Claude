#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU — Round-Total Pricing ($11.50 → $11.99)".

A one-page decision summary condensed from the full deep dive, "The $11.99
Question" (27 Aug 2026), which itself is a deep dive on item 03 of the IMTU
Revenue Shortlist.

The proposal: hold face value at $10.00 and move the service fee from $1.50 to
$1.99, so the customer pays a charm price ($11.99) instead of an odd one
($11.50). Every cent of the difference is service-fee revenue; the recipient
receives the same top-up.

All figures re-measured against Amplitude BR app Prod 650506 on 27 Aug 2026 and
traceable to the "Round-Total Pricing — Evidence Base" dashboard (7di5o1ad).
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

TITLE = "IMTU — Round-Total Pricing ($11.50 → $11.99)"

AMP_DASHBOARD = "https://app.amplitude.com/analytics/BOSS/dashboard/7di5o1ad"
DEEP_DIVE = "https://claude.ai/code/artifact/1f04120b-e6dc-411f-ae12-8aa870b1b835"

# Named sources that must resolve to real links in the finished doc.
EXTRA_LINKS = {
    "Round-Total Pricing — Evidence Base": AMP_DASHBOARD,
    "The $11.99 Question": DEEP_DIVE,
}

# ----------------------------------------------------------------- table ----
# Columns: Rung | Orders/mo | Clean share | Eligible | Fee now → target |
#          Δ on total | Break-even | Annual @ 2%

VALUE = [
    ["Rung → new total", "Eligible orders / mo", "Fee now → target", "Δ on total",
     "Break-even volume loss", "Added revenue / yr (at 2% volume loss)"],
    ["$10 → $11.99", "112,143", "$1.50 → $1.99", "+4.26%", "24.6%", "$605,846"],
    ["$15 → $17.99", "31,304", "$2.25 → $2.99", "+4.29%", "24.7%", "$255,516"],
    ["$25 → $28.99", "23,303", "$3.22 → $3.99", "+2.73%", "19.3%", "$193,008"],
    ["$5 → $5.99", "52,571", "$0.75 → $0.99", "+4.17%", "24.2%", "$138,913"],
    ["$12 → $13.99", "26,814", "$1.80 → $1.99", "+1.38%", "9.5%", "$48,324"],
    ["$6 → $6.99", "41,099", "$0.90 → $0.99", "+1.30%", "9.1%", "$34,620"],
    ["In scope, total", "287,234", "—", "—", "—", "$1,276,227"],
    ["$20", "—", "already totals $23.00", "—", "—", "excluded"],
    ["$8 → $9.99", "—", "$1.20 → $1.99", "+8.59%", "—", "excluded"],
    ["$4 → $4.99", "—", "$0.60 → $0.99", "+8.48%", "—", "excluded"],
    ["$7 → $8.99", "—", "$1.05 → $1.99", "+11.68%", "—", "excluded"],
]

TABLES = [("VALUE", VALUE)]

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("cap", "One-page decision summary  ·  IMTU · BOSS Revolution app · DCS  ·  "
            "28 August 2026  ·  Condensed from the full deep dive, "
            "The $11.99 Question"),

    ("h2", "Recommendation"),
    ("p", "Adopt target-total pricing: set what the customer pays to a charm price by "
          "adjusting the service fee, holding face value constant. Because the fee is a "
          "percentage of face value, the total is a number we choose rather than one we "
          "inherit — and today it mostly lands on untidy figures like $11.50 and $17.25. "
          "Moving those to $11.99 and $17.99 changes only what we keep: the recipient "
          "still receives the full top-up, and the fee stays itemised on its own line."),
    ("b", "Charm, not whole-dollar  —  “Round total” admits both readings and they carry "
          "opposite revenue signs: on the $10 rung $11.99 is a rise, while $11.00 would "
          "be a 33% fee cut."),
    ("p", "Six rungs qualify under a discipline of no more than a 5% rise in what the "
          "customer pays, together worth about $1.28M a year at an assumed 2% volume "
          "loss. Sequence them rather than shipping together: put the highest-value rung "
          "behind a flag, read completion against control for 4–6 weeks, and let that "
          "result decide whether the rest follow. The timing makes the first step cheap "
          "— DCS-5297 is rebuilding the Total and price-breakdown sections now and "
          "DCS-5303 already provisions the flag and A/B harness, so this is one extra "
          "variant on a component being written anyway."),

    ("h2", "What it is worth"),
    ("table", "VALUE"),
    ("cap", "Ordered by annual value. Eligible = the share of each rung landing on a "
            "predictable total today — the only population a target-total rule can "
            "address. That share is measured for $10 (79.6%), $5 (69.8%) and $20 "
            "(79.5%); the $15, $25, $12 and $6 rows assume 75%, which is inside the "
            "observed band but not measured. Break-even volume loss = the share of "
            "orders we could lose before the rise stops adding anything, since a lost "
            "order forfeits the original fee as well as the increase; it is a safety "
            "margin, not a forecast. Added revenue is money gained, not lost, and "
            "assumes we shed 2% of orders — the only figure here that is assumed rather "
            "than measured, and the one the experiment exists to settle. Figures are "
            "gross of processing; the two lead rungs are ~$723k net of the 2.9% card "
            "cost on the increment."),

    ("h2", "Scope guardrail"),
    ("p", "$20 is excluded — 79.5% of those orders already total exactly $23.00, so "
          "there is no untidy total to fix. $4, $7 and $8 need an 8–12% rise to reach "
          "their charm price, which is a price increase wearing a charm price as cover. "
          "A six-rung rollout computes to ~$1.28M a year, but four of those rungs rest "
          "on an assumed 75% clean-total share — a ceiling, not a plan."),

    ("cap", "Caveat: every figure is service-fee only. Carrier commission scales with "
            "face value and is unmeasured — and this idea holds face value constant, so "
            "it earns none; the comparison against face-value ideas is biased in its "
            "favour. Evidence: Round-Total Pricing — Evidence Base, Amplitude BR app "
            "Prod 650506, queried 27 Aug 2026."),
]

# One-pager discipline: tight margins and a compact type scale.
SIZE_MAP = {"h1": 15, "h2": 10.5, "p": 9.5, "b": 9.5, "n": 9.5, "cap": 8}
MARGIN_PT = 43   # ~0.6in

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
        # Named styles ship generous space-above/below; a one-pager cannot afford it.
        above, below = (8, 2) if kind == "h2" else (0, 2)
        para = {"namedStyleType": STYLE_MAP[kind],
                "spaceAbove": {"magnitude": above, "unit": "PT"},
                "spaceBelow": {"magnitude": below, "unit": "PT"},
                "lineSpacing": 100}
        fields = "namedStyleType,spaceAbove,spaceBelow,lineSpacing"
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(line)},
            "paragraphStyle": para, "fields": fields}})

        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        style = {"fontSize": {"magnitude": SIZE_MAP[kind], "unit": "PT"}}
        style_fields = "fontSize"
        if kind == "cap":
            style["italic"] = True
            style_fields += ",italic"
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(text)},
            "textStyle": style, "fields": style_fields}})

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

    # Bold the header and any subtotal row, wherever it sits.
    bold_rows = {0} | {r for r, row in enumerate(data)
                       if row[0].lower().startswith("in scope")}
    reqs = []
    for start, r, c in sorted(cells, reverse=True):   # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        style, fields = {"fontSize": {"magnitude": 9, "unit": "PT"}}, "fontSize"
        if r in bold_rows:
            style["bold"] = True
            fields += ",bold"
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": start, "endIndex": start + len(txt)},
            "textStyle": style, "fields": fields}})
    batched(docs, doc_id, reqs, size=40)
    return True


def clear_body(docs, doc_id):
    """Empty an existing doc so it can be rebuilt in place, keeping its URL."""
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

    reqs = build_requests(BLOCKS)
    batched(docs, doc_id, reqs)
    print(f"Inserted {len(reqs)} text requests")

    for marker, data in TABLES:
        ok = insert_table(docs, doc_id, marker, data)
        print(f"  table {marker}: {'ok' if ok else 'FAILED'} ({len(data) - 1} rows)")

    # Jira keys link by pattern; named sources come from LINK_MAP + EXTRA_LINKS.
    link_map = dict(LINK_MAP)
    link_map.update(EXTRA_LINKS)
    linkify(docs, doc_id, link_map)
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
