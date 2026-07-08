"""
Inserts the 7 BOSS Revolution crypto-flow screen designs (crypto_screen_1..7.png)
into the Triple-A architecture Google Doc as subsection "8.1 Screen designs",
placed at the end of Section 8 (right before the Section 9 heading).

Images are served from the public GitHub repo (Docs API needs public URLs;
IDT Drive sharing is org-restricted) — commit + push the PNGs before running.
"""

from googleapiclient.discovery import build

from generate_crypto_flow_diagrams import DOC_ID, RAW_BASE, get_credentials, paragraph_text

HEADING = "8.1 Screen designs — Designs 1–7 (BOSS Revolution design language)"
INTRO = ("High-fidelity screen designs for the DTC crypto purchase journey, following the "
         "current BOSS Revolution app design system (light canvas, white rounded cards, purple "
         "accents, teal CTAs) and reusing the real Send Top Up flow — recipient IDT Guatemala "
         "Tigo, Soccer Paquetigo bundle, USD $26.25 total.")

DESIGNS = [
    ("crypto_screen_1.png", "Design 1 — Send top up: IMTU product selection (existing screen, unchanged)"),
    ("crypto_screen_2.png", "Design 2 — Select payment: new “Pay with crypto” option alongside BOSS Cash and cards"),
    ("crypto_screen_3.png", "Design 3 — First-time education sheet: what paying with crypto means"),
    ("crypto_screen_4.png", "Design 4 — Triple-A hosted checkout (white-label): locked rate, coin selection, QR"),
    ("crypto_screen_5.png", "Design 5 — Pay from your own wallet: deep links or copy address"),
    ("crypto_screen_6.png", "Design 6 — Payment received: on-chain confirmation progress"),
    ("crypto_screen_7.png", "Design 7 — Receipt: top up delivered, paid with crypto"),
]

IMG_W = 230.0
IMG_H = round(IMG_W * 844 / 390, 1)


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    doc = docs.documents().get(documentId=DOC_ID).execute()

    idx = None
    for el in doc["body"]["content"]:
        if paragraph_text(el).strip().startswith("9. Integration Requirements"):
            idx = el["startIndex"]
            break
    if idx is None:
        raise RuntimeError("Section 9 heading not found")
    print(f"Insertion index: {idx}")

    requests = []

    def norm_para(start, end, center=False):
        style = {"namedStyleType": "NORMAL_TEXT"}
        fields = "namedStyleType"
        if center:
            style["alignment"] = "CENTER"
            fields += ",alignment"
        return {"updateParagraphStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "paragraphStyle": style, "fields": fields}}

    # Blocks are emitted in REVERSE display order: every block inserts at `idx`,
    # so the last-emitted block ends up first in the document.
    for fname, cap in reversed(DESIGNS):
        cap_line = cap + "\n"
        requests += [
            {"insertInlineImage": {
                "location": {"index": idx}, "uri": RAW_BASE + fname,
                "objectSize": {"width": {"magnitude": IMG_W, "unit": "PT"},
                               "height": {"magnitude": IMG_H, "unit": "PT"}}}},
            {"insertText": {"location": {"index": idx + 1}, "text": "\n"}},
            norm_para(idx, idx + 2, center=True),
            {"insertText": {"location": {"index": idx + 2}, "text": cap_line}},
            norm_para(idx + 2, idx + 2 + len(cap_line), center=True),
            {"updateTextStyle": {
                "range": {"startIndex": idx + 2, "endIndex": idx + 2 + len(cap)},
                "textStyle": {"italic": True, "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}},
        ]

    intro_line = INTRO + "\n"
    requests += [
        {"insertText": {"location": {"index": idx}, "text": intro_line}},
        norm_para(idx, idx + len(intro_line)),
    ]

    heading_line = HEADING + "\n"
    requests += [
        {"insertText": {"location": {"index": idx}, "text": heading_line}},
        {"updateParagraphStyle": {
            "range": {"startIndex": idx, "endIndex": idx + len(heading_line)},
            "paragraphStyle": {"namedStyleType": "HEADING_3"},
            "fields": "namedStyleType"}},
    ]

    print(f"Sending {len(requests)} requests...")
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": requests}).execute()
    print("✅  Designs 1–7 inserted.")
    print(f"   https://docs.google.com/document/d/{DOC_ID}/edit")


if __name__ == "__main__":
    main()
