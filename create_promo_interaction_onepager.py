#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU — How Promotions Interact in a Transaction".

A two-page visual reference for the design team covering the three promotion
types (instant automatic, manual, subscription), the two targets they can apply
to (fee, top-up amount), and what the customer should see at every transition.

Page 1 is the model, the rules, and the gate. Page 2 is the full combination
matrix, five worked journeys, and the screen implications.

The governing rule, from the DCS-5299 thread: a subscription promotion cannot
be applied alongside an instant automatic or a manual promo code. What happens
next depends on which of the two is on the transaction, because the customer
can remove one of them and not the other.

  Instant automatic + subscription promo: the SECTION IS HIDDEN for the whole
  transaction. A manual code outranks the automatic and can replace it, but
  the automatic is only displaced, never gone, so the section does not return.

  Manual code + subscription promo, no automatic: the SECTION STAYS and only
  the TOGGLE switches off. Switching it back on shows a yes/no modal warning
  the code will be deleted, and the code is cached so switching the
  subscription off again re-applies it.

  Subscription offer with no promotion: nothing clashes and nothing moves.

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
    "states": ("promo_interaction_states.png", 505.0),
    "journeys": ("promo_interaction_journeys.png", 505.0),
}

# ---------------------------------------------------------------- matrix ----
# Read a cell as: this Fee-slot promotion together with this Amount-slot one.

MATRIX = [
    ["Fee ↓  /  Amount →", "Automatic", "Manual", "Subscription", "None"],
    ["Automatic", "✓  both apply", "✓  both apply", "✗  section hidden",
     "✓  fee only"],
    ["Manual", "✓  both apply", "✗  one code only", "✗  toggle off, ask first",
     "✓  fee only"],
    ["Subscription", "✗  section hidden", "✗  toggle off, ask first", "N/A",
     "✓  subscription only"],
    ["None", "✓  amount only", "✓  amount only", "✓  subscription only",
     "·  no promotion"],
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

# A block's text is either a plain string or a (lead, body) pair, which renders
# as "Lead: body" with the lead in bold. No em dashes anywhere, per house style.

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Design reference  ·  IMTU · DCS  ·  2 September 2026  ·  "
            "Joao Tanaka  ·  Context: DCS-2846, DCS-5299"),

    ("h2", "The model"),
    ("p", "Every IMTU transaction has two places a promotion can land: the fee and "
          "the top-up amount. Two slots, each holding at most one promotion. The "
          "first two kinds below compete for those slots; the third cannot be "
          "applied alongside either."),
    ("b", ("Instant automatic",
           "applied by the system the moment the customer qualifies, with no action "
           "from them. Blue.")),
    ("b", ("Manual",
           "a promo code the customer types in. Amber. At most one per "
           "transaction.")),
    ("b", ("Subscription",
           "attached to turning a one-off top-up into a recurring one. Violet. An "
           "offer carrying a promotion of its own cannot be applied alongside an "
           "instant automatic or a manual code, and what happens next depends on "
           "which of the two it meets. An offer with no promotion clashes with "
           "nothing and never moves.")),

    ("h2", "The rules"),
    ("p", "Ten rules cover every case. The first four are the slot mechanics. Rules "
          "5 and 6 are the clash with an instant automatic, which hides the section. "
          "Rules 7 to 9 are the clash with a manual code, which moves the toggle "
          "instead. Rule 10 is the case where nothing clashes at all."),
    ("b", ("One promotion per target",
           "the fee slot and the amount slot each hold a single promotion.")),
    ("b", ("Two promotions, but only on different targets",
           "an automatic fee discount and a manual amount discount ride together. "
           "So can two automatics, one on each slot.")),
    ("b", ("One manual code per transaction",
           "a fee code and an amount code cannot both be active. Whichever the "
           "customer applies is the only code on the transaction.")),
    ("b", ("Manual outranks automatic",
           "a code always takes the slot, even when the automatic it displaces was "
           "worth more. The customer decides, and we do not warn them off it.")),
    ("b", ("An instant automatic and a subscription promotion cannot both apply, "
           "and the automatic wins",
           "when the transaction is eligible for an instant automatic and the "
           "subscription offer carries a promotion, the subscription section is "
           "hidden. We show the automatic, because it is the one the customer never "
           "chose and cannot remove.")),
    ("b", ("That hiding lasts the whole transaction",
           "a manual code outranks the automatic and can replace it in its slot, but "
           "the section stays hidden. Remove the code and the automatic returns, "
           "still hidden. The automatic was only ever displaced, so the clash never "
           "clears.")),
    ("b", ("A manual code and a subscription promotion cannot both apply either, but "
           "here the section stays",
           "with no instant automatic on the transaction, the clash is live only "
           "while the code is. The section remains on screen and only the toggle "
           "moves: applying a code switches the subscription off, removing it "
           "switches the toggle back to exactly where the customer had it.")),
    ("b", ("Switching the toggle back on asks first",
           "the section is still there, so the customer can insist. Because the code "
           "and the subscription promotion cannot both stand, a yes/no modal warns "
           "that the manual promo code will be deleted. Yes subscribes and deletes "
           "the code. No changes nothing at all.")),
    ("b", ("The promo code is cached, not discarded",
           "once entered it is held for the rest of the transaction. If the customer "
           "switches the subscription off again, the code is re-applied "
           "automatically, so it never has to be typed twice.")),
    ("b", ("A subscription with no promotion clashes with nothing",
           "it stays on offer whatever else the transaction carries, and the toggle "
           "never moves. A discount on its own is never a reason to hide or switch "
           "anything.")),

    ("pagebreak", ""),

    ("h2", "What happens on each clash"),
    ("p", "Two questions decide it: what the transaction carries, and whether the "
          "subscription offer has a promotion of its own. Six combinations, and only "
          "two of them move anything. The asymmetry between those two is the point, "
          "and the panel underneath explains why it is there."),
    ("img", "states"),

    ("h2", "Every combination"),
    ("table", "MATRIX"),
    ("p", "Read a cell as one transaction holding both promotions: the row is what "
          "sits on the fee, the column what sits on the top-up amount. Subscription "
          "here means a subscription promotion, and it reaches the customer only "
          "from the last row and the last column, where nothing else is on the "
          "transaction. A subscription with no promotion attached is not a "
          "promotion at all: it does not appear in this grid, and it stays on offer "
          "in every cell. The two blocked pairings do not behave the same way: "
          "against an automatic the section is hidden outright, while against a "
          "manual code it stays on screen with the toggle off, and the customer can "
          "switch it back on through the modal in rule 8."),

    ("pagebreak", ""),

    ("h2", "Five journeys to design for"),
    ("p", "The same two slots, tracked through each sequence of actions. Journey 1 "
          "is the slot mechanics, which run the same way whatever the subscription "
          "is doing. Journeys 2 and 3 are the pair to read together: the customer "
          "does the same thing in both, and the outcome differs only because of what "
          "was already on the transaction. Journey 4 is the one that needs new "
          "screens."),
    ("img", "journeys"),

    ("h2", "What this changes on screen"),
    ("b", ("Two different outcomes to design, not one",
           "against an instant automatic the section is gone and stays gone. "
           "Against a manual code it is present with the toggle off. Do not "
           "collapse them into a single empty state.")),
    ("b", ("The hidden case needs no controls at all",
           "there is nothing for the customer to act on and nothing that brings the "
           "section back, so it should not hint that something is available "
           "elsewhere.")),
    ("b", ("Switching the subscription off is a change they did not ask for",
           "so it needs saying on screen rather than letting the toggle move "
           "quietly. Same when removing the last code switches it back.")),
    ("b", ("The modal is the one genuinely new screen",
           "a yes/no confirmation, shown when the customer switches the toggle back "
           "on while a code is applied. It has to name the code being deleted, and "
           "No must leave the transaction untouched.")),
    ("b", ("The cache should be visible when it fires",
           "a re-applied code was not retyped by the customer, so show it returning "
           "rather than let it appear silently in the price breakdown.")),
    ("b", ("The applied code still needs an ✕",
           "it is the only route back to the automatic promotion it displaced, and "
           "the only way to clear a cached code the customer no longer wants.")),
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
        lead = None
        if isinstance(text, tuple):
            lead, body = text
            text = f"{lead}: {body}"

        if kind in ("table", "img", "pagebreak"):
            line = f"[[{kind.upper()}:{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += len(line)
            continue

        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        # Named styles ship generous space-above/below; a one-pager cannot afford it.
        above, below = (4, 2) if kind == "h2" else (0, 2)
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

        if lead:                       # bold the lead-in, colon included
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(lead) + 1},
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
    """Swap every [[PAGEBREAK:]] placeholder for a real page break."""
    n = 0
    while _one_pagebreak(docs, doc_id):
        n += 1
    print(f"  page breaks: {n}")
    return n > 0


def _one_pagebreak(docs, doc_id):
    idx, plen = find_placeholder(docs, doc_id, "[[PAGEBREAK:]]")
    if idx is None:
        return False
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx,
                                          "endIndex": idx + plen - 1}}},
        {"insertPageBreak": {"location": {"index": idx}}},
    ]}).execute()
    time.sleep(0.5)
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
            "paragraphStyle": {"spaceAbove": {"magnitude": 0, "unit": "PT"},
                               "spaceBelow": {"magnitude": 0, "unit": "PT"},
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


def tighten_blanks(docs, doc_id):
    """Shrink the empty paragraphs the table and image inserts leave behind."""
    doc = docs.documents().get(documentId=doc_id).execute()
    reqs = []
    for el in doc["body"]["content"]:
        p = el.get("paragraph")
        if not p or para_text(el).strip():
            continue
        if any("pageBreak" in e for e in p.get("elements", [])):
            continue
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": el["startIndex"],
                      "endIndex": el["startIndex"] + 1},
            "textStyle": {"fontSize": {"magnitude": 4, "unit": "PT"}},
            "fields": "fontSize"}})
    if reqs:
        batched(docs, doc_id, reqs)
    print(f"  blank paragraphs tightened: {len(reqs)}")


def trim_trailing_blanks(docs, doc_id):
    """Drop empty paragraphs at the very end, which spill onto a blank page."""
    doc = docs.documents().get(documentId=doc_id).execute()
    body = doc["body"]["content"]
    cut = None
    for el in reversed(body):
        if "paragraph" not in el:
            break
        if para_text(el).strip():
            break
        cut = el["startIndex"]
    if cut is None or cut <= 1:
        return 0
    end = body[-1]["endIndex"] - 1
    if end <= cut:
        return 0
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": cut, "endIndex": end}}}]}
    ).execute()
    time.sleep(0.3)
    return end - cut


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
    tighten_blanks(docs, doc_id)

    n = trim_trailing_blanks(docs, doc_id)
    if n:
        print(f"Trimmed {n} trailing blank characters")

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
