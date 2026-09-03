"""Build the app-review slide (slide 8) of the MTU Exec Demo 2026_09 deck.

Scope is deliberately narrow: IMTU subscription complaints only. The underlying
audit classified all 298 low ratings into fourteen themes, but this slide shows
none of the other themes and none of their causes. The only comparative fact it
carries is the rank, tenth of fourteen, which the deck owner approved.

Drawn with native Slides shapes so the slide matches slides 5 and 6: light grey
KPI cards, teal figures, Roboto, and a chart assembled from rectangles.

Data source: #appreviews-revolution Appbot feed, 1 Mar to 2 Sep 2026, 1,935
unique reviews de-duplicated by Appbot review ID. Product attribution comes from
the reply threads on each review.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
PRESENTATION_ID = "1X6HKcEBgNJepqlG-Kj8p-JBZCOGmzxWGn2O_loQzadQ"
SLIDE_ID = "g3f8ba9a44e2_0_388"
PREFIX = "rv"

EMU = 914400.0
BOX = 3000000

# Palette lifted from slides 5 and 6 of the same deck.
TEAL = {"red": 0.011764706, "green": 0.42352942, "blue": 0.5647059}
INK = {"red": 0.2627451, "green": 0.2627451, "blue": 0.2627451}
MUTED = {"red": 0.5411765, "green": 0.56078434, "blue": 0.5764706}
CARD = {"red": 0.9490196, "green": 0.95686275, "blue": 0.9607843}
GRID = {"red": 0.87058824, "green": 0.88627452, "blue": 0.89411765}

JIRA = "https://idtjira.atlassian.net/browse/%s"
CHANNEL = "https://idt.slack.com/archives/C011AQKV0CV"

# IMTU subscription complaints per month, and that month's low-rating total.
# Only the IMTU series is plotted; the low totals supply the percentage.
MONTHS = [
    ("Mar", 0, 109),
    ("Apr", 1, 43),
    ("May", 2, 38),
    ("Jun", 1, 30),
    ("Jul", 1, 48),
    ("Aug", 5, 30),
]
YMAX = 5

# ---------------------------------------------------------------- layout (in)
MARGIN_L, CONTENT_W = 0.233, 9.534
PLOT_L, PLOT_R = 0.75, 5.60
PLOT_T, PLOT_B = 2.52, 4.12
PLOT_W, PLOT_H = PLOT_R - PLOT_L, PLOT_B - PLOT_T
RIGHT_L, RIGHT_W = 5.95, 3.817


def y_of(v):
    return PLOT_B - (v / float(YMAX)) * PLOT_H


class Deck:
    """Accumulates Slides requests and hands out unique object IDs."""

    def __init__(self):
        self.requests = []
        self.n = 0

    def _id(self, tag):
        self.n += 1
        return "%s%s%04d" % (PREFIX, tag, self.n)

    def _props(self, x, y, w, h):
        return {
            "pageObjectId": SLIDE_ID,
            "size": {
                "width": {"magnitude": BOX, "unit": "EMU"},
                "height": {"magnitude": BOX, "unit": "EMU"},
            },
            "transform": {
                "scaleX": w * EMU / BOX,
                "scaleY": h * EMU / BOX,
                "translateX": x * EMU,
                "translateY": y * EMU,
                "unit": "EMU",
            },
        }

    def rect(self, x, y, w, h, fill):
        oid = self._id("r")
        self.requests.append(
            {"createShape": {"objectId": oid, "shapeType": "RECTANGLE",
                             "elementProperties": self._props(x, y, w, h)}}
        )
        self.requests.append(
            {"updateShapeProperties": {
                "objectId": oid,
                "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
                "shapeProperties": {
                    "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": fill}}},
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
            }}
        )
        return oid

    def text(self, x, y, w, h, content, size, color, bold=False, align="START"):
        oid = self._id("t")
        self.requests.append(
            {"createShape": {"objectId": oid, "shapeType": "TEXT_BOX",
                             "elementProperties": self._props(x, y, w, h)}}
        )
        self.requests.append({"insertText": {"objectId": oid, "insertionIndex": 0,
                                             "text": content}})
        self.requests.append(
            {"updateTextStyle": {
                "objectId": oid,
                "textRange": {"type": "ALL"},
                "fields": "foregroundColor,bold,fontFamily,fontSize,weightedFontFamily",
                "style": {
                    "foregroundColor": {"opaqueColor": {"rgbColor": color}},
                    "bold": bold,
                    "fontFamily": "Roboto",
                    "fontSize": {"magnitude": size, "unit": "PT"},
                    "weightedFontFamily": {"fontFamily": "Roboto",
                                           "weight": 700 if bold else 400},
                },
            }}
        )
        self.requests.append(
            {"updateParagraphStyle": {
                "objectId": oid,
                "textRange": {"type": "ALL"},
                "fields": "lineSpacing,alignment,spaceAbove,spaceBelow",
                "style": {
                    "lineSpacing": 100,
                    "alignment": align,
                    "spaceAbove": {"magnitude": 0, "unit": "PT"},
                    "spaceBelow": {"magnitude": 0, "unit": "PT"},
                },
            }}
        )
        self.requests.append(
            {"updateShapeProperties": {
                "objectId": oid,
                "fields": "contentAlignment",
                "shapeProperties": {"contentAlignment": "MIDDLE"},
            }}
        )
        return oid

    def link(self, oid, content, needle, url):
        """Turn every occurrence of `needle` inside `content` into a link.

        Every reference in anything produced here has to be clickable, and
        Slides only takes links as a style applied to an index range.
        """
        start = content.find(needle)
        while start != -1:
            self.requests.append(
                {"updateTextStyle": {
                    "objectId": oid,
                    "textRange": {"type": "FIXED_RANGE", "startIndex": start,
                                  "endIndex": start + len(needle)},
                    "fields": "link,underline,foregroundColor",
                    "style": {
                        "link": {"url": url},
                        "underline": True,
                        "foregroundColor": {"opaqueColor": {"rgbColor": TEAL}},
                    },
                }}
            )
            start = content.find(needle, start + len(needle))


def build_requests(existing_ids):
    d = Deck()

    # Re-running must not stack a second copy on top of the first.
    for oid in existing_ids:
        d.requests.append({"deleteObject": {"objectId": oid}})

    # ---- headline copy -----------------------------------------------------
    d.text(MARGIN_L, 0.719, CONTENT_W, 0.284,
           "Subscription complaints are 3.4% of low app ratings, and half of them "
           "landed in August",
           14, INK, bold=True)

    sub = ("Every 1 and 2 star review of the BOSS Revolution apps from 1 March to "
           "2 September 2026 was read and attributed to a product. Ten are about "
           "IMTU subscriptions. That makes it the tenth largest of fourteen "
           "complaint themes, but it is the one that is growing.")
    oid = d.text(MARGIN_L, 1.01, CONTENT_W, 0.30, sub, 9, INK)

    # ---- KPI cards ---------------------------------------------------------
    cards = [
        ("IMTU subscription complaints", "10", "1 Mar to 2 Sep 2026"),
        ("Share of low ratings", "3.4%", "10 of 298 reviews at 1 or 2 stars"),
        ("Share of all reviews", "0.5%", "Of 1,935 reviews in the period"),
        ("August share of low ratings", "16.7%", "5 of 30, up from none in March"),
    ]
    gap = 0.14
    cw = (CONTENT_W - 3 * gap) / 4
    for k, (label, value, note) in enumerate(cards):
        cx = MARGIN_L + k * (cw + gap)
        d.rect(cx, 1.44, cw, 0.615, CARD)
        d.text(cx + 0.11, 1.487, cw - 0.22, 0.14, label, 7, MUTED)
        d.text(cx + 0.11, 1.615, cw - 0.22, 0.26, value, 19, TEAL, bold=True)
        d.text(cx + 0.11, 1.885, cw - 0.22, 0.13, note, 7, INK)

    # ---- chart -------------------------------------------------------------
    d.text(MARGIN_L, 2.24, 4.20, 0.21,
           "IMTU subscription complaints per month", 9, INK, bold=True)

    for tick in range(1, YMAX + 1):
        gy = y_of(tick)
        d.rect(PLOT_L, gy, PLOT_W, 0.007, GRID)
        d.text(MARGIN_L, gy - 0.07, PLOT_L - MARGIN_L - 0.06, 0.14,
               str(tick), 6, MUTED, align="END")

    gw = PLOT_W / len(MONTHS)
    bw = 0.42
    for k, (name, count, low) in enumerate(MONTHS):
        cx = PLOT_L + k * gw + gw / 2
        h = (count / float(YMAX)) * PLOT_H
        if count:
            d.rect(cx - bw / 2, PLOT_B - h, bw, h, TEAL)
        # count above the bar, or just above the axis for a month with none
        d.text(cx - 0.40, (PLOT_B - h if count else PLOT_B) - 0.20, 0.80, 0.15,
               str(count), 8, TEAL if count else MUTED, bold=True, align="CENTER")
        # month label, with that month's share of low ratings underneath
        d.text(cx - 0.40, 4.16, 0.80, 0.15, name, 7, INK, align="CENTER")
        share = "0%" if not count else "%.1f%%" % (100.0 * count / low)
        d.text(cx - 0.40, 4.31, 0.80, 0.14, share, 6, MUTED, align="CENTER")

    d.rect(PLOT_L, PLOT_B, PLOT_W, 0.008, MUTED)
    d.text(MARGIN_L, 4.47, PLOT_R - MARGIN_L, 0.14,
           "Percentages are that month's share of all low ratings.", 6, MUTED)

    # ---- right column ------------------------------------------------------
    d.text(RIGHT_L, 2.24, RIGHT_W, 0.21, "What the ten cases were", 9, INK, bold=True)

    b1 = ("Five were traced to a customer account. Three of those came from the "
          "subscription upsell sheet and two from the default-on toggle.")
    b2 = ("The upsell was due to be removed on 23 June under DCS-4872, but the "
          "flag was still on in August and produced one of the August cases.")
    b3 = ("The other five could not be tied to an account and rest on the wording "
          "of the review alone.")
    by = 2.50
    for body in (b1, b2, b3):
        oid = d.text(RIGHT_L, by, RIGHT_W, 0.40, "•  " + body, 7.5, INK)
        d.link(oid, "•  " + body, "DCS-4872", JIRA % "DCS-4872")
        by += 0.44

    d.text(RIGHT_L, 3.88, RIGHT_W, 0.21,
           "Where it sits", 9, INK, bold=True)
    tail = ("Tenth of fourteen complaint themes over the same six months, and the "
            "only one trending up. DCS-5289 and DCS-5299 are the fixes in flight, "
            "so August is the baseline to judge them against.")
    oid = d.text(RIGHT_L, 4.12, RIGHT_W, 0.52, tail, 7.5, INK)
    d.link(oid, tail, "DCS-5289", JIRA % "DCS-5289")
    d.link(oid, tail, "DCS-5299", JIRA % "DCS-5299")

    # ---- source ------------------------------------------------------------
    src = ("1,935 reviews from the Appbot feed in #appreviews-revolution, 1 Mar to "
           "2 Sep 2026, de-duplicated by review ID. Product attribution taken from "
           "the reply threads. Read 2 Sep 2026.")
    oid = d.text(MARGIN_L, 4.90, CONTENT_W, 0.14, src, 6, MUTED)
    d.link(oid, src, "#appreviews-revolution", CHANNEL)

    return d.requests


def main():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as fh:
            fh.write(creds.to_json())

    slides = build("slides", "v1", credentials=creds)

    deck = slides.presentations().get(presentationId=PRESENTATION_ID).execute()
    slide = next(s for s in deck["slides"] if s["objectId"] == SLIDE_ID)
    existing = [e["objectId"] for e in slide.get("pageElements", [])
                if e["objectId"].startswith(PREFIX)]
    if existing:
        print("clearing %d shapes from a previous run" % len(existing))

    requests = build_requests(existing)
    print("%d requests" % len(requests))
    for i in range(0, len(requests), 50):
        chunk = requests[i:i + 50]
        slides.presentations().batchUpdate(
            presentationId=PRESENTATION_ID, body={"requests": chunk}
        ).execute()
        print("  applied %d-%d" % (i + 1, i + len(chunk)))
    print("Slide 8 updated: "
          "https://docs.google.com/presentation/d/%s/edit#slide=id.%s"
          % (PRESENTATION_ID, SLIDE_ID))


if __name__ == "__main__":
    main()
