#!/usr/bin/env python3
"""
Builds the Google Doc "Felix Pago WhatsApp Top-Up: The Real End-to-End Flow".

Competitive teardown of Felix Pago's WhatsApp recarga (mobile top-up) journey, rebuilt
from real captured screens: Felix's own production screenshots, public videos, the X
and Instagram launch carousels and the app store listings, mapped to the FY27
WhatsApp MTU chatbot.

Images are served from the public GitHub repo (the Docs API needs public URLs and IDT
Drive sharing is org-restricted). Commit and push the felix_evidence/ folder before
running this script.

Content comes from felix_recarga_evidence_content.py, the same source of truth as the
HTML artifact (build_felix_recarga_evidence_html.py).

Usage:
    python create_felix_recarga_evidence_doc.py                 # new doc
    python create_felix_recarga_evidence_doc.py --doc-id <id>   # rebuild in place, same URL
"""

import argparse
import re
import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from linkify_refs import LINK_MAP, linkify
from felix_recarga_evidence_content import (
    TITLE, BLOCKS, TABLES, IMAGES, IMAGE_CAPTIONS, EXTRA_LINKS, VERDICT_COLOR,
)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"
RAW_BASE = "https://raw.githubusercontent.com/tanaka-idt/IDT-Claude/main/felix_evidence/"

PAGE_WIDTH_PT = 468          # Letter with 1-inch margins
IMAGE_MARGIN_PT = 18         # Docs gives every inline image 9 pt of margin on each side
QUOTE_MAX_CHARS = 80         # 9 pt Roboto Mono in a 24 pt indent fits about 82 characters
SPACE_BELOW = {"p": 6, "b": 3, "n": 3, "quote": 2, "cap": 8, "meta": 10}
POSITION = {2: ["Left", "Right"], 3: ["Left", "Centre", "Right"],
            4: ["First", "Second", "Third", "Fourth"]}

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3", "h4": "HEADING_4",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT", "quote": "NORMAL_TEXT", "meta": "NORMAL_TEXT"}
GREY = {"red": 0.42, "green": 0.45, "blue": 0.44}


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


def u16(s):
    """Docs API indices count UTF-16 code units, so emoji count as two."""
    return len(s.encode("utf-16-le")) // 2


_last_write = [0.0]


def write(docs, doc_id, reqs):
    """One batchUpdate, spaced to stay under the 60 writes/minute quota, retried on 429."""
    for attempt in range(6):
        wait = 1.05 - (time.time() - _last_write[0])
        if wait > 0:
            time.sleep(wait)
        try:
            _last_write[0] = time.time()
            return docs.documents().batchUpdate(documentId=doc_id, body={"requests": reqs}).execute()
        except HttpError as e:
            if e.resp.status != 429 or attempt == 5:
                raise
            time.sleep(15 * (attempt + 1))


def batched(docs, doc_id, reqs, size=40):
    for i in range(0, len(reqs), size):
        write(docs, doc_id, reqs[i:i + size])


def group_blocks(blocks):
    """Merge consecutive image blocks into one ("images", [markers]) block."""
    out = []
    for kind, text in blocks:
        if kind == "image":
            if out and out[-1][0] == "images":
                out[-1][1].append(text)
            else:
                out.append(("images", [text]))
        else:
            out.append((kind, text))
    return out


def caption_lines(markers):
    caps = [IMAGE_CAPTIONS.get(m, "") for m in markers]
    if len(markers) == 1:
        return [c for c in caps if c]
    names = POSITION.get(len(markers), [str(i + 1) for i in range(len(markers))])
    return [f"{n}: {c}" for n, c in zip(names, caps) if c]


def fit_quote(text):
    """Chat quotes pad timestamps with spaces for the wide HTML bubble; shrink the padding
    on lines that would wrap in the Doc so a timestamp never lands on a line of its own."""
    return "\n".join(re.sub(r" {3,}", "   ", ln) if len(ln) > QUOTE_MAX_CHARS else ln
                     for ln in text.split("\n"))


def build_requests(blocks):
    """Text blocks -> batchUpdate requests. Tables and images are placeholders
    ([[MARKER]]) that are replaced afterwards, because insertTable/insertInlineImage
    shift indices unpredictably. Side-by-side images share one placeholder paragraph."""
    reqs, cur = [], 1

    def para(line, kind):
        nonlocal cur
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        style = {"namedStyleType": STYLE_MAP.get(kind, "NORMAL_TEXT")}
        fields = "namedStyleType"
        if kind in ("cap", "images"):
            style["alignment"] = "CENTER"
            fields += ",alignment"
        if kind == "quote":
            style["indentStart"] = {"magnitude": 24, "unit": "PT"}
            fields += ",indentStart"
        if kind in SPACE_BELOW:
            style["spaceBelow"] = {"magnitude": SPACE_BELOW[kind], "unit": "PT"}
            fields += ",spaceBelow"
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + u16(line)},
            "paragraphStyle": style, "fields": fields}})
        start = cur
        cur += u16(line)
        return start

    for kind, text in group_blocks(blocks):
        if kind == "table":
            para(f"[[{text}]]\n", "p")
            continue
        if kind == "images":
            para("".join(f"[[{m}]]" for m in text) + "\n", "images")
            for cap in caption_lines(text):
                start = para(cap + "\n", "cap")
                reqs.append({"updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": start + u16(cap)},
                    "textStyle": {"italic": True, "fontSize": {"magnitude": 9, "unit": "PT"},
                                  "foregroundColor": {"color": {"rgbColor": GREY}}},
                    "fields": "italic,fontSize,foregroundColor"}})
            continue

        lead = None
        if kind == "quote":
            text = fit_quote(text)
        if kind in ("b", "p", "n") and "  ::  " in text:
            lead, rest = text.split("  ::  ", 1)
            text = f"{lead}: {rest}"
        line = text + "\n"
        start = para(line, kind)

        if kind in ("b", "n"):
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": start, "endIndex": start + u16(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE" if kind == "b" else "NUMBERED_DECIMAL_ALPHA_ROMAN"}})
        if kind == "meta":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + u16(text)},
                "textStyle": {"fontSize": {"magnitude": 9.5, "unit": "PT"},
                              "foregroundColor": {"color": {"rgbColor": GREY}}},
                "fields": "fontSize,foregroundColor"}})
        if kind == "quote":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + u16(text)},
                "textStyle": {"weightedFontFamily": {"fontFamily": "Roboto Mono"},
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "weightedFontFamily,fontSize"}})
        if lead is not None:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + u16(lead) + 1},
                "textStyle": {"bold": True}, "fields": "bold"}})
    return reqs


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in el["paragraph"]["elements"])


def find_marker(docs, doc_id, marker):
    """Return (start, end) of the [[marker]] token, wherever it sits in a paragraph."""
    token = f"[[{marker}]]"
    doc = docs.documents().get(documentId=doc_id).execute()
    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        for e in el["paragraph"]["elements"]:
            content = e.get("textRun", {}).get("content", "")
            pos = content.find(token)
            if pos >= 0:
                start = e["startIndex"] + u16(content[:pos])
                return start, start + u16(token)
    return None, None


def insert_table(docs, doc_id, marker, data):
    start, end = find_marker(docs, doc_id, marker)
    if start is None:
        print(f"  ! placeholder {marker} not found")
        return False

    rows, cols = len(data), len(data[0])
    write(docs, doc_id, [
        {"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}},
        {"insertTable": {"location": {"index": start}, "rows": rows, "columns": cols}},
    ])

    doc = docs.documents().get(documentId=doc_id).execute()
    table_el = next((el for el in doc["body"]["content"]
                     if "table" in el and el["startIndex"] >= start - 2), None)
    if table_el is None:
        print(f"  ! table {marker} not found after insert")
        return False

    cells = []
    for r, row in enumerate(table_el["table"]["tableRows"]):
        for c, cell in enumerate(row["tableCells"]):
            cells.append((cell["content"][0]["startIndex"], r, c))

    reqs = []
    for cstart, r, c in sorted(cells, reverse=True):
        txt = data[r][c]
        if not txt:
            continue
        reqs.append({"insertText": {"location": {"index": cstart}, "text": txt}})
        style = {"fontSize": {"magnitude": 9, "unit": "PT"}}
        fields = "fontSize"
        if r == 0:
            style["bold"] = True
            fields += ",bold"
        elif txt in VERDICT_COLOR:
            red, green, blue = VERDICT_COLOR[txt]
            style["bold"] = True
            style["foregroundColor"] = {"color": {"rgbColor": {"red": red, "green": green, "blue": blue}}}
            fields += ",bold,foregroundColor"
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": cstart, "endIndex": cstart + u16(txt)},
            "textStyle": style, "fields": fields}})
    batched(docs, doc_id, reqs, size=40)
    return True


def group_widths(markers, images):
    """Each image keeps its own width alone; a side-by-side row is scaled to fit the page."""
    widths = [images[m][1] for m in markers]
    if len(markers) == 1:
        return widths
    room = PAGE_WIDTH_PT - IMAGE_MARGIN_PT * len(markers) - 2
    scale = min(1.0, room / sum(widths))
    return [w * scale for w in widths]


def insert_image(docs, doc_id, marker, fname, width, nw, nh):
    start, end = find_marker(docs, doc_id, marker)
    if start is None:
        print(f"  ! placeholder {marker} not found")
        return False
    height = round(width * nh / nw, 1)
    write(docs, doc_id, [
        {"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}},
        {"insertInlineImage": {
            "location": {"index": start}, "uri": RAW_BASE + fname,
            "objectSize": {"width": {"magnitude": round(width, 1), "unit": "PT"},
                           "height": {"magnitude": height, "unit": "PT"}}}},
    ])
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc-id", default="", help="rebuild this existing document in place instead of creating a new one")
    args = ap.parse_args()

    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    if args.doc_id:
        doc_id = args.doc_id
        doc = docs.documents().get(documentId=doc_id).execute()
        end = doc["body"]["content"][-1]["endIndex"]
        if end > 2:
            write(docs, doc_id, [{"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1}}}])
        print(f"Cleared doc: {doc_id}")
    else:
        doc = docs.documents().create(body={"title": TITLE}).execute()
        doc_id = doc["documentId"]
        print(f"Created doc: {doc_id}")

    reqs = build_requests(BLOCKS)
    batched(docs, doc_id, reqs)
    print(f"Inserted {len(reqs)} text requests")

    for marker, data in TABLES:
        ok = insert_table(docs, doc_id, marker, data)
        print(f"  table {marker}: {'ok' if ok else 'FAILED'} ({len(data) - 1} rows)")

    images = {m: (f, w, nw, nh) for m, f, w, nw, nh in IMAGES}
    for kind, markers in group_blocks(BLOCKS):
        if kind != "images":
            continue
        for marker, width in zip(markers, group_widths(markers, images)):
            fname, _, nw, nh = images[marker]
            ok = insert_image(docs, doc_id, marker, fname, width, nw, nh)
            print(f"  image {marker}: {'ok' if ok else 'FAILED'} ({fname}, {width:.0f} pt)")

    linkify(docs, doc_id, {**LINK_MAP, **EXTRA_LINKS})

    if not args.doc_id:
        drive.permissions().create(
            fileId=doc_id,
            body={"role": "writer", "type": "domain", "domain": "idt.net"},
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
