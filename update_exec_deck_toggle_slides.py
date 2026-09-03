"""Build slides 8 and 9 of the MTU Exec Demo 2026_09 deck.

Slide 8: what customers actually do with the subscription toggle (opt-out and
         opt-in rates, user-level, clean post-rollout window).
Slide 9: 60-day cancellation for default-ON subscribers, and why the default-ON
         versus default-OFF comparison cannot be made from current data.

Both drawn with native Slides shapes so they match slides 5, 6 and 7: light grey
KPI cards, teal figures, Roboto, charts assembled from rectangles.

Every figure was rebuilt and adversarially re-verified on Amplitude project
650506. Source charts live in dashboard 1c3815cw.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
PRESENTATION_ID = "1X6HKcEBgNJepqlG-Kj8p-JBZCOGmzxWGn2O_loQzadQ"
SLIDE_BEHAVIOUR = "g3f8ba9a44e2_47_42"    # slide 8
SLIDE_CANCEL = "g3f8ba9a44e2_47_107"      # slide 9
PREFIX = "tg"

EMU = 914400.0
BOX = 3000000

TEAL = {"red": 0.011764706, "green": 0.42352942, "blue": 0.5647059}
INK = {"red": 0.2627451, "green": 0.2627451, "blue": 0.2627451}
MUTED = {"red": 0.5411765, "green": 0.56078434, "blue": 0.5764706}
CARD = {"red": 0.9490196, "green": 0.95686275, "blue": 0.9607843}
GRID = {"red": 0.87058824, "green": 0.88627452, "blue": 0.89411765}
AMBER = {"red": 0.65, "green": 0.35, "blue": 0.04}
SLATE = {"red": 0.62, "green": 0.65, "blue": 0.67}

DASHBOARD = "https://app.amplitude.com/analytics/BOSS/dashboard/1c3815cw"
CHART = "https://app.amplitude.com/analytics/BOSS/chart/%s"

MARGIN_L, CONTENT_W = 0.233, 9.534


class Deck:
    """Accumulates Slides requests for one slide."""

    def __init__(self, slide_id, tag):
        self.slide_id = slide_id
        self.tag = tag
        self.requests = []
        self.n = 0

    def _id(self, kind):
        self.n += 1
        return "%s%s%s%04d" % (PREFIX, self.tag, kind, self.n)

    def _props(self, x, y, w, h):
        return {
            "pageObjectId": self.slide_id,
            "size": {"width": {"magnitude": BOX, "unit": "EMU"},
                     "height": {"magnitude": BOX, "unit": "EMU"}},
            "transform": {"scaleX": w * EMU / BOX, "scaleY": h * EMU / BOX,
                          "translateX": x * EMU, "translateY": y * EMU, "unit": "EMU"},
        }

    def rect(self, x, y, w, h, fill):
        oid = self._id("r")
        self.requests.append({"createShape": {
            "objectId": oid, "shapeType": "RECTANGLE",
            "elementProperties": self._props(x, y, w, h)}})
        self.requests.append({"updateShapeProperties": {
            "objectId": oid,
            "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
            "shapeProperties": {
                "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": fill}}},
                "outline": {"propertyState": "NOT_RENDERED"}}}})
        return oid

    def text(self, x, y, w, h, content, size, color, bold=False, italic=False,
             align="START", valign="TOP"):
        oid = self._id("t")
        self.requests.append({"createShape": {
            "objectId": oid, "shapeType": "TEXT_BOX",
            "elementProperties": self._props(x, y, w, h)}})
        self.requests.append({"insertText": {
            "objectId": oid, "insertionIndex": 0, "text": content}})
        self.requests.append({"updateTextStyle": {
            "objectId": oid, "textRange": {"type": "ALL"},
            "fields": ("foregroundColor,bold,italic,fontFamily,fontSize,"
                       "weightedFontFamily"),
            "style": {"foregroundColor": {"opaqueColor": {"rgbColor": color}},
                      "bold": bold, "italic": italic, "fontFamily": "Roboto",
                      "fontSize": {"magnitude": size, "unit": "PT"},
                      "weightedFontFamily": {"fontFamily": "Roboto",
                                             "weight": 700 if bold else 400}}}})
        self.requests.append({"updateParagraphStyle": {
            "objectId": oid, "textRange": {"type": "ALL"},
            "fields": "lineSpacing,alignment,spaceAbove,spaceBelow",
            "style": {"lineSpacing": 100, "alignment": align,
                      "spaceAbove": {"magnitude": 0, "unit": "PT"},
                      "spaceBelow": {"magnitude": 0, "unit": "PT"}}}})
        self.requests.append({"updateShapeProperties": {
            "objectId": oid, "fields": "contentAlignment,autofit.autofitType",
            "shapeProperties": {"contentAlignment": valign,
                                "autofit": {"autofitType": "NONE"}}}})
        return oid

    def link(self, oid, content, needle, url):
        """Every reference on a slide has to be clickable."""
        start = content.find(needle)
        while start != -1:
            self.requests.append({"updateTextStyle": {
                "objectId": oid,
                "textRange": {"type": "FIXED_RANGE", "startIndex": start,
                              "endIndex": start + len(needle)},
                "fields": "link,underline,foregroundColor",
                "style": {"link": {"url": url}, "underline": True,
                          "foregroundColor": {"opaqueColor": {"rgbColor": TEAL}}}}})
            start = content.find(needle, start + len(needle))

    def cards(self, items, y=1.42, h=0.66):
        """Card texts are vertically centred in their own band; a top-aligned
        19pt value overflows its box and collides with the note beneath it."""
        gap = 0.14
        cw = (CONTENT_W - gap * (len(items) - 1)) / len(items)
        for k, (label, value, note, color) in enumerate(items):
            cx = MARGIN_L + k * (cw + gap)
            self.rect(cx, y, cw, h, CARD)
            self.text(cx + 0.11, y + 0.045, cw - 0.22, 0.15, label, 7, MUTED,
                      valign="MIDDLE")
            self.text(cx + 0.11, y + 0.185, cw - 0.22, 0.30, value, 18, color,
                      bold=True, valign="MIDDLE")
            self.text(cx + 0.11, y + 0.495, cw - 0.22, 0.14, note, 7, INK,
                      valign="MIDDLE")

    def source(self, text, links):
        oid = self.text(0.853, 4.965, 8.914, 0.14, text, 6, MUTED)
        for needle, url in links:
            self.link(oid, text, needle, url)


def slide_behaviour():
    d = Deck(SLIDE_BEHAVIOUR, "a")

    d.text(MARGIN_L, 0.719, CONTENT_W, 0.284,
           "Nearly half the customers shown an ON default turn it off, and the "
           "share is still rising", 14, INK, bold=True)
    d.text(MARGIN_L, 1.01, CONTENT_W, 0.30,
           "User-level rates on the clean post-rollout window, 20 June to 31 August 2026. "
           "One in seven customers shown an OFF default switches it on, so the subscription "
           "base is being built by the default rather than by demand.",
           9, INK)

    d.cards([
        ("Shown ON, turned it OFF", "46.6%", "197,721 of 423,888 users", TEAL),
        ("Shown OFF, turned it ON", "18.5%", "32,933 of 177,656 users", TEAL),
        ("Median time to the opt-out tap", "7 sec", "A reflex, not a considered choice", TEAL),
        ("Opt-out cost to conversion", "2.1 pts", "89.7% still order vs 91.8%", TEAL),
    ])

    # ---- chart: monthly opt-out vs opt-in -------------------------------
    PLOT_L, PLOT_R, PLOT_T, PLOT_B = 0.75, 5.20, 2.52, 4.12
    PLOT_W, PLOT_H = PLOT_R - PLOT_L, PLOT_B - PLOT_T
    YMAX = 50
    d.text(MARGIN_L, 2.24, 4.40, 0.21,
           "Opt-out is climbing while opt-in is flat", 9, INK, bold=True)

    for tick in (10, 20, 30, 40, 50):
        gy = PLOT_B - tick / float(YMAX) * PLOT_H
        d.rect(PLOT_L, gy, PLOT_W, 0.007, GRID)
        d.text(MARGIN_L, gy - 0.07, PLOT_L - MARGIN_L - 0.06, 0.14,
               "%d%%" % tick, 6, MUTED, align="END")

    months = [("July", 43.2, 13.9), ("August", 48.9, 14.0)]
    gw = PLOT_W / len(months)
    bw = 0.52
    for k, (name, out_v, in_v) in enumerate(months):
        cx = PLOT_L + k * gw + gw / 2
        for j, (val, col) in enumerate(((out_v, TEAL), (in_v, SLATE))):
            bx = cx - bw - 0.03 + j * (bw + 0.06)
            hh = val / float(YMAX) * PLOT_H
            d.rect(bx, PLOT_B - hh, bw, hh, col)
            d.text(bx - 0.10, PLOT_B - hh - 0.20, bw + 0.20, 0.15,
                   "%.1f%%" % val, 8, col, bold=True, align="CENTER")
        d.text(cx - 0.60, 4.16, 1.20, 0.15, name, 7, INK, align="CENTER")

    d.rect(PLOT_L, PLOT_B, PLOT_W, 0.008, MUTED)
    d.rect(PLOT_L, 4.42, 0.10, 0.10, TEAL)
    d.text(PLOT_L + 0.15, 4.39, 1.60, 0.15, "Shown ON, turned OFF", 7, INK)
    d.rect(PLOT_L + 1.85, 4.42, 0.10, 0.10, SLATE)
    d.text(PLOT_L + 2.00, 4.39, 1.60, 0.15, "Shown OFF, turned ON", 7, INK)

    # ---- right column ---------------------------------------------------
    RL, RW = 5.60, 4.167
    d.text(RL, 2.24, RW, 0.21, "What this tells us", 9, INK, bold=True)
    bullets = [
        "The default is doing the work. Attach is 76% in the ON arm against 5% "
        "in the OFF arm, but half the ON arm removes it by hand.",
        "Resistance is growing, not settling. Opt-out rose 5.7 points between "
        "July and August. If the default were teaching customers to accept "
        "subscriptions, this line would fall.",
        "Turning it off does not cost the sale. Opt-outs complete their order "
        "at 89.7% against 91.8% for everyone else, and only 0.58% switch it "
        "back on.",
        "Genuine demand is about one in seven. That is the share who switch a "
        "default-OFF toggle on unprompted.",
    ]
    by = 2.50
    for b in bullets:
        d.text(RL, by, RW, 0.44, "•  " + b, 7.5, INK)
        by += 0.47

    src = ("User-level funnels, one explicitly filtered chart per arm, unique users, "
           "Amplitude project 650506. Charts and denominators in dashboard 1c3815cw. "
           "Read 3 Sep 2026.")
    d.source(src, [("1c3815cw", DASHBOARD)])
    return d.requests


def slide_cancel():
    d = Deck(SLIDE_CANCEL, "b")

    d.text(MARGIN_L, 0.719, CONTENT_W, 0.284,
           "Default-ON subscribers cancel at 44.8% within 60 days, and the renewal "
           "charge is the trigger", 14, INK, bold=True)
    d.text(MARGIN_L, 1.01, CONTENT_W, 0.30,
           "Fully observed cohort: customers who bought with a subscription between "
           "1 June and 4 July 2026, every one of whom has had a complete 60 days. "
           "The comparison against a default-OFF group cannot be made, for the reasons on the right.",
           9, INK)

    d.cards([
        ("Cancel within 60 days", "44.8%", "2,845 of 6,356 subscribers", TEAL),
        ("Median time to cancel", "25.0 days", "Just before the first renewal", TEAL),
        ("Cancel on days 29 to 32", "21.3%", "of all cancellers, at the first charge", TEAL),
        ("Cancel within 24 hours", "6.7%", "426 buyers, immediate regret", TEAL),
    ])

    # ---- chart: cumulative cancellation ---------------------------------
    PLOT_L, PLOT_R, PLOT_T, PLOT_B = 0.75, 4.75, 2.52, 4.12
    PLOT_W, PLOT_H = PLOT_R - PLOT_L, PLOT_B - PLOT_T
    YMAX = 50
    d.text(MARGIN_L, 2.24, 4.20, 0.21,
           "Cumulative cancellation after purchase", 9, INK, bold=True)

    for tick in (10, 20, 30, 40, 50):
        gy = PLOT_B - tick / float(YMAX) * PLOT_H
        d.rect(PLOT_L, gy, PLOT_W, 0.007, GRID)
        d.text(MARGIN_L, gy - 0.07, PLOT_L - MARGIN_L - 0.06, 0.14,
               "%d%%" % tick, 6, MUTED, align="END")

    points = [("24 h", 6.7), ("28 d", 26.0), ("32 d", 35.5), ("60 d", 44.8)]
    gw = PLOT_W / len(points)
    bw = 0.46
    for k, (name, val) in enumerate(points):
        cx = PLOT_L + k * gw + gw / 2
        hh = val / float(YMAX) * PLOT_H
        col = AMBER if name == "32 d" else TEAL
        d.rect(cx - bw / 2, PLOT_B - hh, bw, hh, col)
        d.text(cx - 0.40, PLOT_B - hh - 0.20, 0.80, 0.15,
               "%.1f%%" % val, 8, col, bold=True, align="CENTER")
        d.text(cx - 0.40, 4.16, 0.80, 0.15, name, 7, INK, align="CENTER")

    d.rect(PLOT_L, PLOT_B, PLOT_W, 0.008, MUTED)
    d.text(PLOT_L, 4.36, PLOT_W, 0.28,
           "The 9.5 point jump between day 28 and day 32 is the first monthly "
           "renewal charge landing.", 6.5, MUTED)

    # ---- right column: why the comparison fails -------------------------
    RL, RW = 5.15, 4.617
    d.text(RL, 2.24, RW, 0.21,
           "Why we cannot compare this against a default-OFF group", 9, AMBER, bold=True)
    blockers = [
        "The A/B tag covers 3.6% of purchasers, and 47% of the users tagged B "
        "also carry an A tag, so it never was a stable assignment.",
        "Arm B stops on 18 June, two days before the default-ON rollout "
        "completed, and holds 143 subscription buyers in total.",
        "Attach is about 67% in arm A against 1.4% in arm B. Arm B's "
        "subscribers deliberately switched a default-OFF toggle on, so they are "
        "a self-selected, high-intent group.",
        "A lower cancellation rate among deliberate opt-ins is exactly what "
        "selection predicts on its own. Showing the pair would assert a cause "
        "the data cannot support.",
    ]
    by = 2.50
    for b in blockers:
        d.text(RL, by, RW, 0.42, "•  " + b, 7.5, INK)
        by += 0.45

    d.text(RL, 4.34, RW, 0.30,
           "To answer it: run a concurrent randomised default-OFF holdback after "
           "20 June, and instrument the toggle state at submission.",
           7.5, AMBER, bold=True)

    src = ("Unique users, ordered funnels, 60-day conversion window, Amplitude project "
           "650506. Cohort ends 4 Jul 2026 so every buyer has a full 60 days. "
           "Charts in dashboard 1c3815cw. Read 3 Sep 2026.")
    d.source(src, [("1c3815cw", DASHBOARD)])
    return d.requests


def main():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as fh:
            fh.write(creds.to_json())

    slides = build("slides", "v1", credentials=creds)
    deck = slides.presentations().get(presentationId=PRESENTATION_ID).execute()
    by_id = {s["objectId"]: s for s in deck["slides"]}

    plan = [(SLIDE_BEHAVIOUR, "a", slide_behaviour, "Slide 8"),
            (SLIDE_CANCEL, "b", slide_cancel, "Slide 9")]

    requests = []
    for slide_id, tag, builder, name in plan:
        existing = [e["objectId"] for e in by_id[slide_id].get("pageElements", [])
                    if e["objectId"].startswith(PREFIX + tag)]
        if existing:
            print("clearing %d shapes from %s" % (len(existing), name))
        requests += [{"deleteObject": {"objectId": oid}} for oid in existing]
        requests += builder()

    print("%d requests" % len(requests))
    for i in range(0, len(requests), 50):
        chunk = requests[i:i + 50]
        slides.presentations().batchUpdate(
            presentationId=PRESENTATION_ID, body={"requests": chunk}).execute()
        print("  applied %d-%d" % (i + 1, i + len(chunk)))

    for slide_id, _, _, name in plan:
        print("%s: https://docs.google.com/presentation/d/%s/edit#slide=id.%s"
              % (name, PRESENTATION_ID, slide_id))


if __name__ == "__main__":
    main()
