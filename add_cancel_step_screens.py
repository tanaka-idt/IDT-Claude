#!/usr/bin/env python3
"""
Add the step-by-step cancellation figures to Section 3 of the Digicel doc.

Each figure is placed directly after the paragraph that describes its step, with
a caption naming the screen, the user's action and the resulting outcome.

The figures are RECONSTRUCTIONS built from the verbatim strings in Digicel's
shipped /profile/autopays bundle — not screenshots. No screenshot of Digicel's
cancellation flow exists: its own help-centre opt-out images are dead links, no
web archive ever captured them, and all five published store screenshots were
re-checked and show no account or cancellation surface. The captions and the
figures themselves say so.

Insertions run bottom-to-top so earlier indices stay valid.
"""

import time

from googleapiclient.discovery import build

from create_digicel_cancellation_doc import get_credentials, RAW_BASE

DOC_ID = "1u7B865KXvZIaGcxSdAbOJtp7MGLovfOU0bmv5UTCl3U"

# (paragraph text prefix to anchor after, image file, native size, caption)
STEPS = [
    ("Steps 1–4 — Navigation", "digicel_step_1_list.png", (1008, 1290),
     "Steps 1–4 — Recurring Payments list. The customer has navigated More → Frequent "
     "Payments → Auto Top Up and AutoPay. Action: tap the trash icon on the schedule they "
     "want to end. Outcome: the confirmation dialog opens. Note the row offers no edit, "
     "pause or change control — deletion is the only thing that can be done here."),

    ("Control arm (Verified)", "digicel_step_2_control.png", (1008, 1290),
     "Step 5a — Control arm dialog, shown when the “frequent-payments” flag resolves to "
     "control and whenever flag evaluation fails. Action: the customer taps “Back” to abandon "
     "or “Remove” to proceed. Outcome: “Back” closes the dialog and the subscription survives; "
     "“Remove” deletes it. Neither button emits an analytics event."),

    ("Test arm (Verified)", "digicel_step_3_test.png", (1008, 1290),
     "Step 5b — Test arm dialog: the only retention intervention Digicel operates, localised "
     "into English, Spanish, French and Dutch. Action: the customer taps “Keep my Advantages” "
     "to stay or “Remove Recurring Top Up” to proceed. Outcome: the save path simply closes the "
     "dialog — no discount is applied and no event fires, so the save cannot be counted."),

    ("Completing cancellation (Verified)", "digicel_step_4_deleted.png", (1008, 1290),
     "Step 6 — Completion. Action: the customer confirmed removal. Outcome: the schedule "
     "disappears from the list, a success snackbar appears, and “remove_frequent_payment” "
     "fires — the only branch in the entire flow that emits an event. No receipt, reference "
     "number, or email/SMS confirmation is documented."),

    ("Not one published image anywhere depicts", "digicel_step_5_absent.png", (1167, 1267),
     "The states that do not exist. Each was sought in the shipped bundle, the FAQ and every "
     "published image, and none is present. The absences are architectural rather than "
     "stylistic: with only GET and DELETE on the recurring-payments API, a pause or a "
     "modify option could not be added as a front-end change."),
]

INTRO = ("A note on the figures below. No screenshot of Digicel's cancellation flow exists "
         "anywhere — Digicel's own help-centre images of the opt-out path now resolve to "
         "soft-404 pages, no web archive ever captured them, and all five published store "
         "screenshots for the Digicel International app show the home screen, Send Money, a "
         "promo modal, checkout and a payment confirmation, with no account or cancellation "
         "surface among them. The step figures that follow are therefore RECONSTRUCTIONS, "
         "rendered from the verbatim strings recovered from the shipped Recurring Payments "
         "bundle. Every word of copy and every control label is quoted exactly; layout, "
         "spacing and iconography are inferred and are not authoritative. Each figure is "
         "stamped accordingly. The two genuine screenshots in this document are the Digicel "
         "store assets in Section 3.4.")


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in el["paragraph"]["elements"])


def anchor_end(docs, prefix):
    """End index of the paragraph starting with `prefix`."""
    doc = docs.documents().get(documentId=DOC_ID).execute()
    for el in doc["body"]["content"]:
        if para_text(el).strip().startswith(prefix):
            return el["endIndex"]
    return None


def insert_figure(docs, at, fname, native, caption, width=330.0):
    """Insert an image paragraph then a caption paragraph at index `at`."""
    nw, nh = native
    height = round(width * nh / nw, 1)
    cap = caption + "\n"
    reqs = [
        {"insertText": {"location": {"index": at}, "text": "\n"}},
        {"insertInlineImage": {
            "location": {"index": at}, "uri": RAW_BASE + fname,
            "objectSize": {"width": {"magnitude": width, "unit": "PT"},
                           "height": {"magnitude": height, "unit": "PT"}}}},
        {"updateParagraphStyle": {
            "range": {"startIndex": at, "endIndex": at + 1},
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT", "alignment": "CENTER"},
            "fields": "namedStyleType,alignment"}},
        {"insertText": {"location": {"index": at + 2}, "text": cap}},
        {"updateParagraphStyle": {
            "range": {"startIndex": at + 2, "endIndex": at + 2 + len(cap)},
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT", "alignment": "CENTER"},
            "fields": "namedStyleType,alignment"}},
        {"updateTextStyle": {
            "range": {"startIndex": at + 2, "endIndex": at + 2 + len(caption)},
            "textStyle": {"italic": True, "fontSize": {"magnitude": 9, "unit": "PT"}},
            "fields": "italic,fontSize"}},
    ]
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": reqs}).execute()
    time.sleep(0.6)


def main():
    docs = build("docs", "v1", credentials=get_credentials())

    # Resolve every anchor first, then apply bottom-to-top so indices stay valid.
    points = []
    for prefix, fname, native, caption in STEPS:
        end = anchor_end(docs, prefix)
        if end is None:
            print(f"  ! anchor not found: {prefix!r}")
            continue
        points.append((end, prefix, fname, native, caption))

    for end, prefix, fname, native, caption in sorted(points, reverse=True):
        insert_figure(docs, end, fname, native, caption)
        print(f"  inserted {fname} after “{prefix[:38]}…”")

    # Framing note, added last so it does not shift the anchors above.
    intro_at = anchor_end(docs, "Confidence is marked per step")
    if intro_at:
        txt = INTRO + "\n"
        docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": [
            {"insertText": {"location": {"index": intro_at}, "text": txt}},
            {"updateParagraphStyle": {
                "range": {"startIndex": intro_at, "endIndex": intro_at + len(txt)},
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType"}},
        ]}).execute()
        print("  inserted framing note")

    print(f"\nDone: https://docs.google.com/document/d/{DOC_ID}/edit")


if __name__ == "__main__":
    main()
