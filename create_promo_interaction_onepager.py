#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU — How Promotions Interact in a Transaction".

A two-page visual reference for the design team covering the three promotion
types (instant automatic, manual, subscription), the two targets they can apply
to (fee, top-up amount), and what the customer should see at every transition.

Page 1 is the model, the rules, and the state diagram. Page 2 is the full
combination matrix, four worked journeys, the screen implications, and the
product decisions of 31 Aug 2026 that closed every open question.

Figures come from generate_promo_interaction_diagrams.py and are served from
the public GitHub repo - the Docs API fetches image URIs server-side and IDT
Drive sharing is org-restricted, so the PNGs must be committed and pushed
before this runs.
"""

import time
from pathlib import Path

from PIL import Image
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

RAW_BASE = "https://raw.githubusercontent.com/tanaka-idt/IDT-Claude/main/"

TITLE = "IMTU — How Promotions Interact in a Transaction"

MARGIN_PT = 40
PAGE_W = 612 - 2 * MARGIN_PT          # 532pt of usable width
IMG_W = 495.0                          # figures sit just inside the text block

# --------------------------------------------------------------- figures ----

IMAGES = {
    "flow": ("promo_interaction_flow.png", IMG_W),
    "examples": ("promo_interaction_examples.png", IMG_W),
}

# ---------------------------------------------------------------- matrix ----
# Read a cell as: this Fee-slot promotion together with this Amount-slot one.

MATRIX = [
    ["Fee ↓  /  Amount →", "Automatic", "Manual", "Subscription", "None"],
    ["Automatic", "✓  both apply", "✓  both apply", "✗  exclusive", "✓  fee only"],
    ["Manual", "✓  both apply", "✗  one code only", "✗  exclusive", "✓  fee only"],
    ["Subscription", "✗  exclusive", "✗  exclusive",
     "✓  replaces both slots", "✗  exclusive"],
    ["None", "✓  amount only", "✓  amount only", "✗  exclusive", "—  no promotion"],
]

TABLES = [("MATRIX", MATRIX)]

# Colour language, identical to the figures.
C_AUTO = "#E6EEF7"
C_MANUAL = "#FAEBD9"
C_SUB = "#EFEAF7"
C_NONE = "#EEEBE5"
C_NO = "#FBE9E9"      # not possible
C_ASK = "#FDF3D0"     # needs a product decision

LABEL_FILL = [C_NONE, C_AUTO, C_MANUAL, C_SUB, C_NONE]   # by row / column index

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Design reference  ·  IMTU · DCS  ·  31 August 2026  ·  "
            "Joao Tanaka  ·  Context: DCS-2846"),

    ("h2", "The model"),
    ("p", "Every IMTU transaction has exactly two places a promotion can land: the "
          "fee and the top-up amount. Think of them as two slots. Each slot holds at "
          "most one promotion, which is what keeps the rules below short — there is "
          "never a question of two discounts competing over the same line. Three kinds "
          "of promotion compete for those slots, and they are colour-coded the same "
          "way everywhere on this page."),
    ("b", "Instant automatic  —  applied by the system the moment the customer "
          "qualifies, with no action from them. Blue."),
    ("b", "Manual  —  a promo code the customer types in. Amber. At most one per "
          "transaction."),
    ("b", "Subscription  —  attached to turning a one-off top-up into a recurring "
          "one. Violet. It is not a slot-filler: it takes the whole transaction."),

    ("h2", "The rules"),
    ("p", "Five rules cover every case. The first two describe how the slots work; "
          "the last three are the product decisions taken on 31 August."),
    ("b", "One promotion per target  —  the fee slot and the amount slot each hold a "
          "single promotion."),
    ("b", "Two promotions, but only on different targets  —  an automatic fee discount "
          "and a manual amount discount ride together. So can two automatics, one on "
          "each slot."),
    ("b", "One manual code per transaction  —  a fee code and an amount code cannot "
          "both be active. Whichever the customer applies is the only code on the "
          "transaction."),
    ("b", "Manual outranks automatic  —  a code always takes the slot, even when the "
          "automatic it displaces was worth more. The customer decides, and we do not "
          "warn them off it."),
    ("b", "Subscription is exclusive, and fully reversible  —  turning it on clears "
          "both slots and remembers what was there. Turning it off puts all of it "
          "back, the manual code included."),

    ("h2", "The three states, and every way to move between them"),
    ("p", "There are only three states a transaction can be in, and six transitions "
          "between them. Every one of the six is a moment the customer sees something "
          "change, so each needs a designed state. Note the two that are not "
          "symmetrical: removing a code with ✕ brings back the automatic underneath "
          "it, and typing a code while subscribed switches the subscription off on "
          "the customer's behalf."),
    ("img", "flow"),

    ("pagebreak", ""),

    ("h2", "Every combination"),
    ("table", "MATRIX"),
    ("p", "Read a cell as one transaction holding both promotions: the row is what "
          "sits on the fee, the column what sits on the top-up amount. Every "
          "combination is now decided — nothing in this grid is open. The red band is "
          "the subscription's exclusivity, plus the one cell where two manual codes "
          "would have met."),

    ("h2", "Four journeys to design for"),
    ("p", "The same two slots, tracked through each sequence of actions. This is the "
          "state the screen has to show at every step. Journeys 3 and 4 are the ones "
          "worth reading closely: they are where the transaction changes without the "
          "customer directly asking it to."),
    ("img", "examples"),

    ("h2", "What this changes on screen"),
    ("b", "The applied code needs an ✕  —  it is the only route back to the automatic "
          "promotion it displaced, and the only way to undo a restore the customer "
          "did not want."),
    ("b", "The promo-code field stays live while a subscription is on  —  not "
          "disabled, not hidden."),
    ("b", "Applying a code while subscribed flips the subscription off  —  the "
          "customer did not ask for that, so the screen has to say it happened rather "
          "than let the toggle change quietly."),
    ("b", "Restoration is automatic but must be legible  —  when the subscription goes "
          "off, the previous promotions reappear in place. Nothing to confirm, but the "
          "change should be visible in the price breakdown."),

    ("h2", "Decisions taken 31 August 2026"),
    ("b", "Two manual codes  —  not allowed. One manual code per transaction."),
    ("b", "Restoration  —  the manual code comes back with the automatics. Making the "
          "customer re-enter it was judged worse than letting them remove it in one "
          "tap."),
    ("b", "Code while subscribed  —  the field stays available; applying a code "
          "switches the subscription off automatically."),
    ("b", "A weaker manual promo  —  no warning. Manual always has priority, so the "
          "customer keeps the choice."),
    ("b", "Automatic expired mid-session  —  out of scope. Edge case, not designed "
          "for."),

    ("cap", "Two mechanics follow from the rules but were not stated outright — worth "
            "confirming before build: removing a code with ✕ brings back the automatic "
            "it displaced (automatics apply by default), and applying a second manual "
            "code replaces the first rather than being rejected."),
]

SIZE_MAP = {"h1": 15, "h2": 10.5, "p": 9, "b": 9, "cap": 7.5}
STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "pagebreak": "NORMAL_TEXT",
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
        if kind in ("table", "img", "pagebreak"):
            line = f"[[{kind.upper()}:{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += len(line)
            continue

        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        # Named styles ship generous space-above/below; a one-pager cannot afford it.
        above, below = (8, 3) if kind == "h2" else (0, 2)
        para = {"namedStyleType": STYLE_MAP[kind],
                "spaceAbove": {"magnitude": above, "unit": "PT"},
                "spaceBelow": {"magnitude": below, "unit": "PT"},
                "lineSpacing": 100}
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(line)},
            "paragraphStyle": para,
            "fields": "namedStyleType,spaceAbove,spaceBelow,lineSpacing"}})

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


def find_placeholder(docs, doc_id, marker):
    doc = docs.documents().get(documentId=doc_id).execute()
    for el in doc["body"]["content"]:
        if para_text(el).strip() == marker:
            return el["startIndex"], len(para_text(el))
    return None, None


def insert_pagebreak(docs, doc_id):
    """Swap the [[PAGEBREAK:]] placeholder for a real page break."""
    idx, plen = find_placeholder(docs, doc_id, "[[PAGEBREAK:]]")
    if idx is None:
        print("  ! placeholder PAGEBREAK not found")
        return False
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx,
                                          "endIndex": idx + plen - 1}}},
        {"insertPageBreak": {"location": {"index": idx}}},
    ]}).execute()
    time.sleep(0.5)
    print("  page break: ok")
    return True


def insert_image(docs, doc_id, key):
    fname, width = IMAGES[key]
    idx, plen = find_placeholder(docs, doc_id, f"[[IMG:{key}]]")
    if idx is None:
        print(f"  ! placeholder IMG:{key} not found")
        return False

    with Image.open(BASE / fname) as im:
        height = round(width * im.height / im.width, 1)

    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx,
                                          "endIndex": idx + plen - 1}}},
        {"insertInlineImage": {
            "location": {"index": idx}, "uri": RAW_BASE + fname,
            "objectSize": {"width": {"magnitude": width, "unit": "PT"},
                           "height": {"magnitude": height, "unit": "PT"}}}},
        {"updateParagraphStyle": {
            "range": {"startIndex": idx, "endIndex": idx + 1},
            "paragraphStyle": {"alignment": "CENTER",
                               "spaceAbove": {"magnitude": 2, "unit": "PT"},
                               "spaceBelow": {"magnitude": 2, "unit": "PT"}},
            "fields": "alignment,spaceAbove,spaceBelow"}},
    ]}).execute()
    time.sleep(0.6)
    print(f"  image {key}: ok ({width} x {height} pt)")
    return True


def insert_table(docs, doc_id, marker, data):
    """Replace the [[TABLE:marker]] placeholder with a shaded Docs table."""
    idx, plen = find_placeholder(docs, doc_id, f"[[TABLE:{marker}]]")
    if idx is None:
        print(f"  ! placeholder TABLE:{marker} not found")
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
    for start, r, c in sorted(cells, reverse=True):   # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        style = {"fontSize": {"magnitude": 8, "unit": "PT"}}
        fields = "fontSize"
        if r == 0 or c == 0:
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

    # Shading and column widths carry the colour language into the table.
    style_reqs = []
    for r in range(rows):
        for c in range(cols):
            if r == 0:
                fill = LABEL_FILL[c]
            elif c == 0:
                fill = LABEL_FILL[r]
            elif data[r][c].startswith("✗"):
                fill = C_NO
            elif data[r][c].startswith("?"):
                fill = C_ASK
            else:
                continue
            style_reqs.append({"updateTableCellStyle": {
                "tableRange": {
                    "tableCellLocation": {
                        "tableStartLocation": {"index": t_start},
                        "rowIndex": r, "columnIndex": c},
                    "rowSpan": 1, "columnSpan": 1},
                "tableCellStyle": {
                    "backgroundColor": hexrgb(fill),
                    "paddingTop": {"magnitude": 1, "unit": "PT"},
                    "paddingBottom": {"magnitude": 1, "unit": "PT"},
                    "paddingLeft": {"magnitude": 4, "unit": "PT"},
                    "paddingRight": {"magnitude": 4, "unit": "PT"}},
                "fields": ("backgroundColor,paddingTop,paddingBottom,"
                           "paddingLeft,paddingRight")}})

    widths = [100] + [108] * (cols - 1)
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

    batched(docs, doc_id, build_requests(BLOCKS))
    print("Inserted text blocks")

    for marker, data in TABLES:
        ok = insert_table(docs, doc_id, marker, data)
        print(f"  table {marker}: {'ok' if ok else 'FAILED'}")

    for key in IMAGES:
        insert_image(docs, doc_id, key)

    insert_pagebreak(docs, doc_id)

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
