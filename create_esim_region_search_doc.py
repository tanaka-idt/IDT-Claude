#!/usr/bin/env python3
"""
Creates ONE Google Doc: "eSIM Search: Region Plan Matching".

A short account of what changed in eSIM search and why it matters, covering the
three shipped pieces (new search screen, region plan matching, personalized
country suggestions) plus the catalog work underneath them.

Every claim is sourced from Jira. Where the tickets disagree with each other, or
where nothing measures a result, the document says so rather than smoothing it
over: see the "Status and open points" section.

Source: DCS Jira (DCS-4415, DCS-4513, DCS-4543, DCS-4544, DCS-4642, DCS-4728,
DCS-4937, epic DCS-2791) and OMTU Jira (OMTU-8262, OMTU-8272).
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

TITLE = "eSIM Search: Region Plan Matching"

FIGMA = ("https://www.figma.com/design/jZAEcWnvH6bSXgYJtLAbDJ/eSIM---Handoff"
         "?node-id=8716-10189")
REGIONS_SHEET = ("https://docs.google.com/spreadsheets/d/"
                 "1DkawwD5AkUVNynfk1FsJsHtJqi0JzosNpvZRnE1vy-g/edit?gid=0#gid=0")

# Named sources cited in this doc, on top of the shared map. Jira keys and bare
# URLs are linked by pattern, so only phrases need an entry here.
DOC_LINKS = dict(LINK_MAP)
DOC_LINKS.update({
    "eSIM Handoff Figma frame": FIGMA,
    "standard regions reference list": REGIONS_SHEET,
})

# ---------------------------------------------------------------- tables ----

CHANGED = [
    ["What changed", "Before", "After", "Jira"],
    ["Search screen",
     "The destination picker opened on a list of regions, which implied you had "
     "to choose a region before you could choose a country.",
     "One search screen with All, Country plans and Regional plans filters. "
     "Region matching was deliberately excluded from this first step and "
     "deferred to a second one.",
     "DCS-4415, DCS-4513"],
    ["Region plan matching",
     "Searching a country returned that country's own plans only. Regional plans "
     "existed behind the Regional plans filter, but no country query ever "
     "matched them.",
     "Searching a country also returns regional plans whose coverage includes "
     "that country. The region-to-country map is read from the catalog rather "
     "than hardcoded in the client or the service.",
     "DCS-4544 (BE), DCS-4543 (APP)"],
    ["Personalized country suggestions",
     "The search widget opened on a fixed country list for every user.",
     "All and Country plans open on up to 4 countries the user has bought an "
     "eSIM for, most recent first, taken from their last 20 transactions. With "
     "no eSIM history it falls back to the same 4 countries as the home page. "
     "The section hides as soon as the user types.",
     "DCS-4642"],
]

SUPPORTING = [
    ["Supporting change", "What it does", "Jira"],
    ["Dead destinations dropped from the catalog response",
     "A destination country is returned by /catalog/offers/combinations only "
     "when at least one enabled offer sits behind it. Kosovo (XK) was the "
     "reported symptom: it appeared in search with nothing purchasable.",
     "OMTU-8262"],
    ["Regions and their countries exposed by the catalog",
     "An endpoint returning the available regions and the countries in each, as "
     "ISO 2-letter codes, limited to what enabled offers actually cover. "
     "Filterable by region and product type.",
     "OMTU-8272"],
    ["Region coverage re-derived from the offers themselves",
     "The region-to-country map in GET /v1/config now comes from the union of "
     "each offer's roaming countries per region, replacing the K2 catalog region "
     "list, which had drifted away from what the offers really cover. A failed "
     "region keeps its previously cached countries instead of shrinking.",
     "DCS-4937"],
    ["Suggestions stopped reacting to regional purchases",
     "Buying any regional plan used to push USA to the top of the suggested "
     "countries, at 100% reproducibility. Fixed so a regional purchase leaves "
     "the suggestions untouched.",
     "DCS-4728"],
]

TABLES = [("CHANGED", CHANGED), ("SUPPORTING", SUPPORTING)]

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("p", "What shipped in eSIM search across the region plan matching work, "
          "what it is worth, and what is still open. Compiled from DCS and OMTU "
          "Jira. All of it sits under epic DCS-2791, eSIM Version 2."),

    ("h2", "What changed"),
    ("table", "CHANGED"),

    ("h2", "How a country search resolves now"),
    ("n", "The catalog publishes which regions exist and which countries each "
          "one covers, limited to destinations that have at least one enabled "
          "offer behind them."),
    ("n", "That map is cached on the IDT side and refreshed by a scheduled job, "
          "rather than fetched on every keystroke."),
    ("n", "A country query is resolved against the map, and any regional plan "
          "whose coverage includes that country comes back alongside the "
          "country's own plans."),

    ("h2", "Supporting work"),
    ("table", "SUPPORTING"),

    ("h2", "Why it matters"),
    ("b", "Regional plans become findable by the only thing a traveller "
          "actually types: the destination. Someone going to Japan no longer "
          "has to know that an Asia plan exists, or that Japan sits inside it, "
          "to be offered one."),
    ("b", "Country and region stop being a forced first choice: the problem "
          "DCS-4415 opened with was that search led on regions and read as a "
          "two-step selection. Both are now answers to the same query."),
    ("b", "What search shows is what can be bought: region membership is "
          "derived from the offers themselves and destinations with no enabled "
          "offer are dropped, so a match cannot point at something "
          "unpurchasable (OMTU-8262, DCS-4937)."),
    ("b", "New regions need no release: both Phase 2 stories forbid hardcoded "
          "region lists, so a region added in the catalog shows up in search "
          "without an app or backend change. LATAM, EU and EuroZone are the "
          "examples named in the tickets."),
    ("b", "Repeat buyers start closer to the purchase: search opens on the "
          "countries they have bought before instead of a generic list "
          "(DCS-4642)."),
    ("b", "Country search was protected, not traded away: both Phase 2 stories "
          "carry an explicit acceptance criterion that existing "
          "country-specific results are unaffected."),

    ("h2", "Status and open points"),
    ("b", "Nothing here is measured: no ticket in this set carries a baseline, "
          "a target, or an Amplitude event. Everything under “Why it "
          "matters” is the stated intent of the work, not an observed "
          "result. Worth instrumenting before the next change to eSIM search."),
    ("b", "Two QA questions on DCS-4543 have no recorded answer: the K2 regions "
          "response returned countries the offer list page does not show as "
          "supported, and Global does not come back from K2 as a region at all. "
          "Both were raised on 18 June 2026; the ticket passed on 9 July 2026 "
          "with no resolution written on either."),
    ("b", "The mapping source is described three different ways: the Phase 2 "
          "acceptance criteria say the K2 combinations endpoint, the "
          "pre-planning note on DCS-4543 says a DCS-side cache scanning K2 "
          "offers, and DCS-4937 says GET /v1/config derived from each offer's "
          "roaming countries. The criteria were never updated after the "
          "approach changed, so the tickets no longer describe what runs. Read "
          "the code, not the ACs."),
    ("b", "Both Phase 2 stories claim the resolution step: DCS-4544 puts "
          "country-to-region resolution in the search endpoint, DCS-4543 puts "
          "it in app search logic. Both are Done, so where it actually happens "
          "is a code question."),
    ("b", "DCS-4937 is a correction, not a foundation: it was created on 26 "
          "June 2026, after Phase 2 passed QA on 16 and 18 June 2026, and "
          "shipped in a later release. The Jira link that shows it blocking "
          "DCS-4543 was added after the fact."),
    ("b", "A region can go quietly stale: when a region's refresh fails, "
          "DCS-4937 keeps its previously cached countries by design. Failures "
          "are logged, but the metric was written as optional and nothing "
          "confirms one was built, so there is no alert behind it."),
    ("b", "Two threads are still open: automated regression coverage for the "
          "new search (DCS-4756) is To Do, and DCS-4249, the new Country "
          "Selector from the original design proposal, is closed as Won't fix, "
          "so not all of DCS-4415 was built."),

    ("h2", "References"),
    ("b", "Design: the eSIM Handoff Figma frame, from the proposal in DCS-4415. "
          "It is confirmed as the design link on DCS-4642; DCS-4513 still "
          "carries [TBD]."),
    ("b", "Regions: the standard regions reference list cited by both Phase 2 "
          "stories as the alignment source."),
    ("b", "Epics: DCS-2791 (eSIM Version 2, In Progress) for the app work, "
          "OMTU-7509 (Catalog enhancements FY26, To Do) for the catalog work."),

    ("cap", "Compiled from Jira on 3 September 2026. No production release date "
            "is recorded on any of these tickets, only DEV and FEAT builds."),
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

        # Bullets are written as "Lead: explanation" - bold through the colon so
        # the list scans without a separator character in the text.
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

    last = len(data[0]) - 1
    reqs = []
    for start, r, c in sorted(cells, reverse=True):   # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0 or c == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        if r > 0 and c == last:                       # the Jira key column
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

    # Jira keys, bare URLs and the named sources above all become clickable.
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
