"""Build the case-detail slide (slide 9) of the MTU Exec Demo 2026_09 deck.

Backs slide 8 with all ten IMTU subscription complaints found in the app
reviews between 1 March and 2 September 2026: the reviewer's own words, and
what the investigation in the review thread concluded.

Scope matches slide 8. Only IMTU subscription cases appear here. No other
complaint theme and no other cause is shown.

Laid out as two columns of five cards so all ten fit at a readable size, using
the same palette and Roboto sizing as slides 5, 6 and 8.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
PRESENTATION_ID = "1X6HKcEBgNJepqlG-Kj8p-JBZCOGmzxWGn2O_loQzadQ"
SLIDE_ID = "g3f8ba9a44e2_0_394"
PREFIX = "tc"

EMU = 914400.0
BOX = 3000000

TEAL = {"red": 0.011764706, "green": 0.42352942, "blue": 0.5647059}
INK = {"red": 0.2627451, "green": 0.2627451, "blue": 0.2627451}
MUTED = {"red": 0.5411765, "green": 0.56078434, "blue": 0.5764706}
CARD = {"red": 0.9490196, "green": 0.95686275, "blue": 0.9607843}

JIRA = "https://idtjira.atlassian.net/browse/%s"
CHANNEL = "https://idt.slack.com/archives/C011AQKV0CV"

# (date, platform, mechanism, traced, review quote, what the thread concluded)
CASES = [
    ("21 Apr", "Android", "Not traced", False,
     "“If you’re not careful, it will keep taking your money for top-ups "
     "until your bank account is empty!”",
     "Customer could not be identified. Support asked them to email and never "
     "heard back."),
    ("20 May", "Android", "Upsell sheet", True,
     "“They’ve put me on automatic top-up for Cuba without my authorization "
     "and just charged me 20.49 without my consent. I’ve already called my bank "
     "to file a complaint.”",
     "Traced: the user accepted the subscription upsell on 20 and 26 April, not "
     "the toggle. They later used the toggle correctly and deleted both "
     "subscriptions."),
    ("22 May", "Android", "Not traced", False,
     "“Bad experience and on top of that they send a recharge that you didn’t "
     "schedule.”",
     "No investigation in the thread. The wording names an unscheduled top-up."),
    ("19 Jun", "Android", "Upsell sheet", True,
     "“When you send a top-up, they automatically add a subscription, and if "
     "you’re not careful, they’ll just keep taking your money.”",
     "The upsell asks again after the user declines. DCS-4872 was opened to "
     "remove the upsell suggestion."),
    ("05 Jul", "iOS", "Not traced", False,
     "“The app is on every step defaulting to monthly subscriptions. You are "
     "automatically opted in. I have had to cancel subscriptions I was tricked "
     "into multiple times.”",
     "The user ID was requested but never found. The wording matches default-on "
     "behaviour."),
    ("08 Aug", "Android", "Default-on toggle", True,
     "“They add subscriptions you didn’t authorize, charge you extra or double "
     "when you send phone top-ups, and when you call, they don’t refund your "
     "money.”",
     "Traced: two top-ups on 1 July where the user did not realise the new "
     "default subscription toggle was on. Duplicate recurring charges followed "
     "on 1 August. Refund requested."),
    ("10 Aug", "Android", "IMTU subscription", True,
     "“Yesterday I sent a $23 top-up. And today, without even using the app, "
     "they charged me another $23 for a top-up I didn’t even send.”",
     "Traced: subscription created 10 July, and its recurring charge on 10 August "
     "collided with a manual top-up the user made on 9 August. Confirmed as the "
     "MTU subscription, not PINless auto recharge."),
    ("13 Aug", "Android", "Upsell sheet", True,
     "“It was good until they started to make unapproved mobile top up. I was "
     "told to turn off the auto recharge, did that, and within a week there was "
     "another unauthorized top up.”",
     "Traced: the user switched the toggle off twice, then accepted Save and "
     "Subscribe on the upsell sheet both times. Support pointed them at PINless "
     "auto recharge, a different feature."),
    ("21 Aug", "Android", "Default-on toggle", True,
     "“It’s outrageous that mobile top-ups automatically remain active. I’ve "
     "had to cancel several times and they still keep automatically debiting my "
     "card.”",
     "Traced: default subscription on. A different offer each time, so the "
     "existing two-subscription guard never fired. The user deleted three "
     "subscriptions before posting."),
    ("29 Aug", "iOS", "Not traced", False,
     "“They enroll you in auto pay or some subscription nonsense without even "
     "you being aware. I deleted my card in their system now.”",
     "Answered in channel with DCS-5289 and DCS-5299 as the fixes in flight."),
]

# ---------------------------------------------------------------- layout (in)
MARGIN_L, CONTENT_W = 0.233, 9.534
COL_GAP = 0.20
COL_W = (CONTENT_W - COL_GAP) / 2
ROW_H, ROW_GAP = 0.714, 0.050
GRID_T = 1.09
PAD = 0.10


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

    def text(self, x, y, w, h, content, size, color, bold=False, italic=False,
             align="START", valign="TOP"):
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
                "fields": ("foregroundColor,bold,italic,fontFamily,fontSize,"
                           "weightedFontFamily"),
                "style": {
                    "foregroundColor": {"opaqueColor": {"rgbColor": color}},
                    "bold": bold,
                    "italic": italic,
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
                "fields": "contentAlignment,autofit.autofitType",
                "shapeProperties": {"contentAlignment": valign,
                                    "autofit": {"autofitType": "NONE"}},
            }}
        )
        return oid

    def link(self, oid, content, needle, url):
        """Every reference produced here has to be clickable."""
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

    for oid in existing_ids:
        d.requests.append({"deleteObject": {"objectId": oid}})

    # ---- headline ----------------------------------------------------------
    d.text(MARGIN_L, 0.719, CONTENT_W, 0.284,
           "The ten, and what each investigation found",
           14, INK, bold=True)

    # ---- the ten cards -----------------------------------------------------
    for i, (date, plat, mech, traced, quote, verdict) in enumerate(CASES):
        col, row = i // 5, i % 5
        cx = MARGIN_L + col * (COL_W + COL_GAP)
        cy = GRID_T + row * (ROW_H + ROW_GAP)

        d.rect(cx, cy, COL_W, ROW_H, CARD)

        tw = COL_W - 2 * PAD
        # header: date and platform on the left, mechanism tag on the right
        d.text(cx + PAD, cy + 0.040, tw * 0.45, 0.130,
               "%s 2026  ·  %s  ·  1 star" % (date, plat),
               6.5, INK, bold=True)
        d.text(cx + PAD + tw * 0.45, cy + 0.040, tw * 0.55, 0.130,
               mech, 6.5, TEAL if traced else MUTED, bold=True, align="END")

        d.text(cx + PAD, cy + 0.180, tw, 0.28, quote, 6, INK, italic=True)

        oid = d.text(cx + PAD, cy + 0.470, tw, 0.225, verdict, 5.5, MUTED)
        for key in ("DCS-4872", "DCS-5289", "DCS-5299"):
            d.link(oid, verdict, key, JIRA % key)

    # ---- source ------------------------------------------------------------
    src = ("Every IMTU subscription complaint in the 1 and 2 star reviews posted to "
           "#appreviews-revolution between 1 Mar and 2 Sep 2026. Quotes are the "
           "reviewer's own words, translated where the review was not in English. "
           "Findings are from the reply thread on each review.")
    # indented to clear the red template block in the bottom left corner,
    # matching where slide 7 puts its own source line
    oid = d.text(0.853, 4.965, 8.914, 0.14, src, 6, MUTED)
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
    print("Slide 9 updated: "
          "https://docs.google.com/presentation/d/%s/edit#slide=id.%s"
          % (PRESENTATION_ID, SLIDE_ID))


if __name__ == "__main__":
    main()
