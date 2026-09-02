"""Build the cancellations slide (slide 6) of the MTU Exec Demo 2026_09 deck.

Draws everything with native Slides shapes so the slide matches the visual
language already used on slide 5: light grey KPI cards, teal figures, Roboto,
and a chart assembled from rectangles rather than an embedded image.

Data source: Cancellations.csv, 244 daily rows, 1 Jan to 1 Sep 2026.
"""

import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
PRESENTATION_ID = "1X6HKcEBgNJepqlG-Kj8p-JBZCOGmzxWGn2O_loQzadQ"
SLIDE_ID = "g3f8ba9a44e2_0_145"
PREFIX = "cx"

EMU = 914400.0  # EMU per inch
BOX = 3000000   # nominal shape size, scaled via the transform (deck convention)

# Palette lifted from slide 5 of the same deck.
TEAL = {"red": 0.011764706, "green": 0.42352942, "blue": 0.5647059}
INK = {"red": 0.2627451, "green": 0.2627451, "blue": 0.2627451}
MUTED = {"red": 0.5411765, "green": 0.56078434, "blue": 0.5764706}
CARD = {"red": 0.9490196, "green": 0.95686275, "blue": 0.9607843}
GRID = {"red": 0.87058824, "green": 0.88627452, "blue": 0.89411765}

VALUES = [
    540, 575, 566, 467, 480, 518, 477, 524, 482, 575, 533, 474, 499, 479, 532,
    603, 525, 538, 511, 494, 490, 493, 535, 581, 538, 552, 502, 478, 452, 437,
    477, 480, 505, 469, 452, 491, 538, 470, 513, 477, 428, 418, 487, 532, 526,
    451, 454, 374, 419, 534, 558, 564, 514, 525, 492, 491, 542, 542, 697, 614,
    412, 427, 467, 466, 543, 479, 507, 514, 433, 430, 461, 466, 520, 529, 516,
    448, 443, 550, 683, 704, 646, 683, 632, 657, 714, 1035, 1135, 912, 1026,
    1187, 1317, 1330, 1625, 1655, 1648, 1750, 1752, 1824, 1941, 2213, 2401,
    2200, 2221, 2190, 2031, 2276, 2572, 2643, 2476, 2566, 2533, 2661, 2703,
    3050, 3360, 3419, 3680, 3581, 3454, 3980, 3977, 3728, 3490, 3701, 3507,
    3373, 3420, 3643, 3794, 3615, 3370, 3340, 3085, 3293, 3291, 3547, 3227,
    3125, 3137, 3249, 3239, 3488, 3638, 3460, 3439, 3319, 3626, 3972, 4007,
    4014, 3434, 4047, 4009, 3834, 3603, 4055, 3831, 3631, 3732, 3899, 4194,
    3986, 4053, 4127, 3776, 3876, 3775, 3766, 4110, 4261, 4461, 4360, 4285,
    4443, 4407, 4886, 5451, 5634, 5276, 5191, 5860, 5562, 5960, 6307, 6256,
    6024, 5979, 5774, 5783, 5890, 6439, 6253, 5917, 6108, 5702, 5631, 5678,
    6598, 7311, 7719, 7969, 8240, 8185, 7743, 8093, 7724, 7524, 7471, 7070,
    7001, 6611, 5762, 6763, 6798, 6922, 6860, 6546, 6542, 6676, 6333, 6144,
    6799, 7136, 7399, 7491, 7326, 6413, 6043, 6172, 6757, 6842, 6927, 6953,
    6817, 6582, 6099, 6229, 5938, 5872, 6098, 5713, 5530, 5186, 5623,
]
START = datetime.date(2026, 1, 1)
N = len(VALUES)
PEAK_I = max(range(N), key=lambda i: VALUES[i])   # 21 July 2026
BREAK_I = 78                                      # 20 March 2026

# ---------------------------------------------------------------- layout (in)
MARGIN_L, CONTENT_W = 0.233, 9.534
PLOT_L, PLOT_R = 0.75, 6.55
PLOT_T, PLOT_B = 2.42, 4.10
PLOT_W, PLOT_H = PLOT_R - PLOT_L, PLOT_B - PLOT_T
YMAX = 8500
RIGHT_L, RIGHT_W = 6.90, 2.867
BUCKET = 3


def x_of(i):
    return PLOT_L + (i / (N - 1)) * PLOT_W


def y_of(v):
    return PLOT_B - (v / YMAX) * PLOT_H


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

    def dot(self, cx, cy, d, fill):
        oid = self._id("e")
        self.requests.append(
            {"createShape": {"objectId": oid, "shapeType": "ELLIPSE",
                             "elementProperties": self._props(cx - d / 2, cy - d / 2, d, d)}}
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

    def vline(self, x, y1, y2, color, weight_pt=1.0, dash="DASH"):
        oid = self._id("l")
        self.requests.append(
            {"createLine": {"objectId": oid, "lineCategory": "STRAIGHT",
                            "elementProperties": self._props(x, y1, 0.001, y2 - y1)}}
        )
        self.requests.append(
            {"updateLineProperties": {
                "objectId": oid,
                "fields": "lineFill.solidFill.color,weight,dashStyle",
                "lineProperties": {
                    "lineFill": {"solidFill": {"color": {"rgbColor": color}}},
                    "weight": {"magnitude": weight_pt, "unit": "PT"},
                    "dashStyle": dash,
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


def build_requests():
    d = Deck()

    # ---- headline copy -----------------------------------------------------
    d.text(MARGIN_L, 0.767, CONTENT_W, 0.30,
           "Cancellations broke upward on 20 March and are still 11 times the "
           "January baseline",
           14, INK, bold=True)
    d.text(MARGIN_L, 1.06, CONTENT_W, 0.32,
           "Daily cancellations, 1 January to 1 September 2026. The count held flat "
           "near 500 a day for the first eleven weeks, stepped up on 20 March, and "
           "climbed for four straight months to a peak of 8,240 on 21 July. It has "
           "eased since, but it has not reverted.",
           9, INK)

    # ---- KPI cards ---------------------------------------------------------
    cards = [
        ("Baseline per day", "501", "Flat for 78 days, 1 Jan to 19 Mar"),
        ("Peak day", "8,240", "21 July 2026, 16x the baseline"),
        ("Latest 7 days per day", "5,709", "11.4x baseline, 31% off the peak"),
        ("Total cancellations", "773,341", "Across 244 days"),
    ]
    gap, cw = 0.14, (CONTENT_W - 3 * 0.14) / 4
    for k, (label, value, note) in enumerate(cards):
        cx = MARGIN_L + k * (cw + gap)
        d.rect(cx, 1.44, cw, 0.615, CARD)
        d.text(cx + 0.11, 1.487, cw - 0.22, 0.14, label, 7, MUTED)
        d.text(cx + 0.11, 1.615, cw - 0.22, 0.26, value, 19, TEAL, bold=True)
        d.text(cx + 0.11, 1.885, cw - 0.22, 0.13, note, 7, INK)

    # ---- chart -------------------------------------------------------------
    d.text(MARGIN_L, 2.16, 4.20, 0.21,
           "Cancellations per day (3-day mean)", 9, INK, bold=True)

    # baseline band, behind the marks
    d.rect(PLOT_L, PLOT_T, x_of(BREAK_I) - PLOT_L, PLOT_H, CARD)

    # gridlines and value labels
    for tick in (2000, 4000, 6000, 8000):
        gy = y_of(tick)
        d.rect(PLOT_L, gy, PLOT_W, 0.007, GRID)
        d.text(MARGIN_L, gy - 0.07, PLOT_L - MARGIN_L - 0.06, 0.14,
               "{:,}".format(tick), 6, MUTED, align="END")

    # the series, as adjacent columns of the 3-day mean
    starts = list(range(0, N, BUCKET))
    bw = PLOT_W / len(starts)
    for k, s in enumerate(starts):
        chunk = VALUES[s:s + BUCKET]
        mean = sum(chunk) / float(len(chunk))
        h = (mean / YMAX) * PLOT_H
        d.rect(PLOT_L + k * bw, PLOT_B - h, bw * 1.04, h, TEAL)

    # zero axis
    d.rect(PLOT_L, PLOT_B, PLOT_W, 0.008, MUTED)

    # Month ticks. The box has to be comfortably wider than the label: Slides
    # adds its own inset and wraps "Jan" to two lines in anything narrower.
    for m in range(9):
        idx = (datetime.date(2026, m + 1, 1) - START).days
        tx = x_of(idx)
        w = 0.78
        label = datetime.date(2026, m + 1, 1).strftime("%b")
        d.text(min(max(tx - w / 2, 0.10), 9.90 - w), 4.13, w, 0.15,
               label, 6, MUTED, align="CENTER")

    # break marker
    d.vline(x_of(BREAK_I), PLOT_T, PLOT_B, MUTED, weight_pt=1.0, dash="DASH")
    d.text(PLOT_L + 0.06, PLOT_T + 0.04, 1.20, 0.14,
           "Flat near 500 a day", 6, MUTED)
    d.text(x_of(BREAK_I) + 0.06, PLOT_T + 0.04, 1.20, 0.14,
           "20 Mar, break upward", 6, INK, bold=True)

    # peak marker
    d.dot(x_of(PEAK_I), y_of(VALUES[PEAK_I]), 0.075, TEAL)
    d.text(x_of(PEAK_I) - 1.80, y_of(VALUES[PEAK_I]) - 0.10, 1.72, 0.15,
           "8,240 on 21 Jul", 7, TEAL, bold=True, align="END")

    # ---- right column ------------------------------------------------------
    d.text(RIGHT_L, 2.16, RIGHT_W, 0.21, "What the shape says", 9, INK, bold=True)
    bullets = [
        "78 days flat at about 500 a day, then a step change on 20 March that "
        "has not reverted.",
        "Four months of climb: 2,435 a day in April, 6,654 a day in July.",
        "Off the peak but plateauing: 6,513 a day in August, 5,709 in the last week.",
    ]
    by = 2.40
    for b in bullets:
        d.text(RIGHT_L, by, RIGHT_W, 0.34, "•  " + b, 7.5, INK)
        by += 0.36

    d.text(RIGHT_L, 3.54, RIGHT_W, 0.21, "What we cannot tell yet", 9, INK, bold=True)
    d.text(RIGHT_L, 3.78, RIGHT_W, 0.52,
           "The export carries only date and count. Nothing in it separates real "
           "churn from a billing or reporting change. Next step: the same series "
           "split by product, country and cancellation reason.",
           7.5, INK)

    # ---- source ------------------------------------------------------------
    d.text(MARGIN_L, 4.60, CONTENT_W, 0.14,
           "1 Jan to 1 Sep 2026, 244 daily rows. Baseline is the mean of 1 Jan to "
           "19 Mar. Latest 7 days is 26 Aug to 1 Sep. Source: Cancellations.csv "
           "export, 2 Sep 2026.",
           6, MUTED)

    return d.requests


def main():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as fh:
            fh.write(creds.to_json())

    slides = build("slides", "v1", credentials=creds)
    requests = build_requests()
    print("%d requests" % len(requests))
    for i in range(0, len(requests), 50):
        chunk = requests[i:i + 50]
        slides.presentations().batchUpdate(
            presentationId=PRESENTATION_ID, body={"requests": chunk}
        ).execute()
        print("  applied %d-%d" % (i + 1, i + len(chunk)))
    print("Slide 6 updated: "
          "https://docs.google.com/presentation/d/%s/edit#slide=id.%s"
          % (PRESENTATION_ID, SLIDE_ID))


if __name__ == "__main__":
    main()
