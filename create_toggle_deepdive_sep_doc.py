"""Build the September 2026 IMTU subscription toggle deep-dive Google Doc.

Answers three questions put to the team on 3 September 2026:
  1. Reactivation and post-cancellation, and the provenance of the "45.3%" claim.
  2. Of users shown the toggle defaulted ON, how many turn it OFF before buying?
     Of users shown it defaulted OFF, how many turn it ON?
  3. Of default-ON buyers who purchase WITH a subscription, how many cancel
     within 60 days, compared with default-OFF buyers who purchase with it on?

Every figure is user-level, built as one explicitly filtered funnel per arm over
one window. Charts live in the evidence dashboard 1c3815cw and each is linked
inline. Question 3 is answered with a negative result: the comparison cannot be
made from the current instrumentation, and the document says why in numbers.
"""

import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from linkify_refs import LINK_MAP, linkify

SCOPES = ["https://www.googleapis.com/auth/documents",
          "https://www.googleapis.com/auth/drive"]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

TITLE = ("IMTU Subscription Toggle — Opt-out, Opt-in and 60-Day Cancellation "
         "(September 2026)")

CHART = "https://app.amplitude.com/analytics/BOSS/chart/"
DASHBOARD = "https://app.amplitude.com/analytics/BOSS/dashboard/1c3815cw"
DOC_V2 = ("https://docs.google.com/document/d/"
          "13GzrL7TMQ8otuMFluVaoTghE4d90jZ9m9S4-OXlpAhQ/edit")
DOC_V1 = ("https://docs.google.com/document/d/"
          "10nWxXEyzhn-uP2YvZa23qyLPpK-JjW2yfaOqKwASGgM/edit")

# Saved charts built and verified for this document (dashboard 1c3815cw).
C = {
    "optout": "hsjw005p",
    "optin": "fjusknm6",
    "subst": "ummjv325",
    "resub": "yst4cqjc",
    "cancelA": "ec37ye5t",
    "tags": "4cpirjcb",
    "armB": "l22v9asp",
}
CHART_IDS = set(C.values())

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "cap": "NORMAL_TEXT"}

STATUS_COLOR = {
    "ANSWERED": (0.05, 0.48, 0.42),
    "WITHDRAWN": (0.70, 0.15, 0.12),
    "NOT ANSWERABLE": (0.70, 0.15, 0.12),
    "SUPERSEDED": (0.70, 0.15, 0.12),
    "NEW": (0.25, 0.32, 0.62),
    "CONFOUNDED": (0.65, 0.35, 0.04),
    "GAP": (0.45, 0.42, 0.50),
}

# ---------------------------------------------------------------- tables

ANSWERS = [
    ["Question", "Answer", "Status"],
    ["Where does 45.3% come from, and is it right?",
     "It is not reproducible as a substitution rate and should be withdrawn. "
     "The matching figure is the RESUBSCRIBE rate, 45.42%. The two rates were "
     "almost certainly transposed. Substitution on a clean, matured cohort is 65.4%.",
     "WITHDRAWN"],
    ["Shown the toggle ON, how many turn it OFF before buying?",
     "46.6% of users shown a default-ON toggle turn it off (197,721 of 423,888). "
     "Median time to the tap is 7 seconds. Rising: 43.2% in July, 48.9% in August.",
     "ANSWERED"],
    ["Shown the toggle OFF, how many turn it ON before buying?",
     "18.5% turn it on at least once over the quarter (32,933 of 177,656); "
     "13.9% in July and 14.0% in August as single-month rates.",
     "ANSWERED"],
    ["Default-ON buyers with a subscription: 60-day cancellation?",
     "44.8% cancel within 60 days (2,845 of 6,356). Median 25.0 days, which lands "
     "on the first monthly renewal charge.",
     "ANSWERED"],
    ["Compared with default-OFF buyers who bought with it on?",
     "The comparison cannot be made. The A/B tag covers 3.6% of purchasers, 47% of "
     "B-tagged users also carry an A tag, arm B tagging stops on 18 June (before "
     "the rollout completed), and arm B holds 143 subscription buyers whose attach "
     "rate is ~48x lower. Selection bias runs in the direction of the result.",
     "NOT ANSWERABLE"],
]

Q1_TABLE = [
    ["Measure", "Cohort of cancellers", "Value", "Numerator / denominator", "Chart"],
    ["Bought a one-time top-up within 60 days  (PUBLISH THIS)",
     "20 Jun - 4 Jul 2026", "65.4%", "18,830 / 28,787", C["subst"]],
    ["Started a NEW subscription within 60 days",
     "1 Mar - 1 Aug 2026", "45.4%", "61,724 / 135,911", C["resub"]],
    ["Bought a one-time top-up within 60 days",
     "1 Mar - 4 Jul 2026", "71.1%", "59,244 / 83,287", ""],
    ["Bought a one-time top-up within 60 days",
     "1 Mar - 1 Aug 2026 (censored)", "64.5%", "87,647 / 135,911", ""],
    ["Started a NEW subscription within 60 days",
     "1 Jun - 4 Jul 2026", "55.2%", "25,970 / 47,020", ""],
    ["Returned at all, either type, within 60 days",
     "1 Jun - 4 Jul 2026", "80.7%", "37,954 / 47,020", ""],
]

Q2_TABLE = [
    ["Measure", "Value", "Numerator / denominator", "Window", "Chart"],
    ["Shown default ON, turned it OFF", "46.6%", "197,721 / 423,888",
     "20 Jun - 31 Aug 2026", C["optout"]],
    ["   the same, July only", "43.2%", "110,325 / 255,430", "1 - 31 Jul 2026", ""],
    ["   the same, August only", "48.9%", "115,100 / 235,610", "1 - 31 Aug 2026", ""],
    ["Shown default OFF, turned it ON", "18.5%", "32,933 / 177,656",
     "20 Jun - 31 Aug 2026", C["optin"]],
    ["   the same, July only", "13.9%", "14,405 / 103,884", "1 - 31 Jul 2026", ""],
    ["   the same, August only", "14.0%", "17,661 / 126,043", "1 - 31 Aug 2026", ""],
    ["Opted out and still completed the order", "89.7%", "177,399 / 197,721",
     "20 Jun - 31 Aug 2026", ""],
    ["Stayed subscribed and completed the order", "91.8%", "207,684 / 226,167",
     "20 Jun - 31 Aug 2026", ""],
    ["Opted out then toggled back ON inside the hour", "0.58%", "1,155 / 197,721",
     "20 Jun - 31 Aug 2026", ""],
]

Q3_TABLE = [
    ["Measure", "Value", "Numerator / denominator", "Chart"],
    ["Arm A (default ON) subscription buyers cancelling within 60 days",
     "44.8%", "2,845 / 6,356", C["cancelA"]],
    ["   the same on the fully post-rollout window 20 Jun - 4 Jul",
     "45.5%", "2,305 / 5,069", ""],
    ["   cancelled within 24 hours of buying", "6.7%", "426 / 6,356", ""],
    ["   cancelled on days 29-32, the first renewal charge",
     "9.5% of buyers, 21.3% of cancellers", "606 / 6,356", ""],
    ["   median days to cancel", "25.0 days", "across 2,845 cancellers", ""],
    ["Arm B (default OFF) buyers cancelling within 60 days",
     "34.3%  CONFOUNDED, do not quote", "49 / 143", ""],
]

BLOCKERS = [
    ["Why the ON vs OFF comparison fails", "Measured", "Chart"],
    ["The A/B tag covers almost nobody",
     "19,719 distinct tagged purchasers of 551,656 = 3.6%. Untagged 540,195, "
     "A 14,435, B 9,939.", C["tags"]],
    ["The tag does not partition users",
     "4,655 users carry BOTH an A and a B label, 46.8% of everyone tagged B. "
     "Assignment is not stable per user, so it is not a randomised arm.", ""],
    ["Arm B expires before the clean window opens",
     "The last arm B subscription purchase is 18 June 2026, two days BEFORE the "
     "default-ON rollout completed on 20 June. Arm B holds 143 buyers in total.",
     C["armB"]],
    ["The two arms are not comparable populations",
     "Subscription attach is about 67% in arm A against about 1.4% in arm B, a "
     "gap of roughly 48x. Arm B's subscribers are people who deliberately switched "
     "a default-OFF toggle ON: a self-selected, high-intent group.", ""],
    ["Even the shown-state arms overlap heavily",
     "50.9% of the users in the default-ON arm also saw a default-OFF screen in "
     "the same window, and 79.0% of the OFF arm also saw an ON screen.", ""],
    ["Nothing records the toggle's final state",
     "Only transition taps are instrumented. No event carries the toggle state at "
     "submission, so 'bought with the toggle on' has to be inferred.", ""],
]

METHOD = [
    ["Trap", "What it does", "How this document avoids it"],
    ["Events are not customers",
     "Order-success events fire about 2.2 times per converting user and toggle "
     "taps include no-change taps, so event counts overstate people.",
     "Every figure is unique users from a funnel, never event totals."],
    ["Summed monthly uniques",
     "Adding monthly unique users double-counts anyone active in more than one "
     "month and inflates the denominator.",
     "One funnel over the whole window, every time."],
    ["Grouped funnels return unlabelled series",
     "Reading a segment off a grouped funnel by rank order silently mislabels arms.",
     "One explicitly filtered chart per arm."],
    ["Right censoring",
     "A 60-day rate on a cohort that has not had 60 days is a floor, not a rate.",
     "Cancellation cohorts stop at 4 July 2026, the last date with a full 60 days."],
    ["Pre-rollout contamination",
     "Default-ON only reached full volume on 20 June 2026. A window starting "
     "1 June mixes a mature OFF arm with an immature ON arm.",
     "Toggle-behaviour windows start 20 June 2026."],
    ["Silent empty charts",
     "These properties are event-scoped, but the taxonomy tool reports them as "
     "user-scoped with a single '(none)' value. A user-scoped filter returns an "
     "empty chart with no error at all.",
     "Filters are event-scoped and is_subscription is matched as True / False, "
     "capitalised. Every chart was checked for a non-empty result."],
]

# ---------------------------------------------------------------- prose

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Investigation · 3 September 2026 · DCS / IMTU · Amplitude project "
            "650506 (BR app Prod) · evidence dashboard 1c3815cw"),

    ("h2", "1. Answers"),
    ("p", "Three questions were asked. Two are answered. The third cannot be "
          "answered with the instrumentation that exists today, and the most "
          "useful thing this document does is say so precisely, in numbers, "
          "rather than publish a comparison that would not survive review."),
    ("table", "ANSWERS"),

    ("h2", "2. Post-cancellation behaviour, and the 45.3% claim"),
    ("h3", "2.1 The claim should be withdrawn"),
    ("p", "The figure comes from section 4.4 of the first version of the "
          "Subscription Journey investigation, which stated that 45.3% of "
          "cancelled subscribers return to one-time top-ups. It carried no chart. "
          "The second version already corrected it to 63.87% and marked it "
          "superseded, but did not explain where 45.3% had come from."),
    ("p", "It is now reasonably clear. 45.3% is not a plausible substitution "
          "rate under any defensible specification, and three candidate "
          "mis-specifications were tested and ruled out: using the wrong "
          "cancellation event moves the rate by 0.01pp, widening the date range "
          "moves it by 1.5pp, and reaching 45.3% by shortening the conversion "
          "window would require about 17 days, which nobody would choose "
          "deliberately."),
    ("p", "What does match, almost exactly, is the RESUBSCRIBE rate on the very "
          "window the original report used: 45.42% of cancellers start a new "
          "subscription within 60 days (61,724 of 135,911, 1 March to 1 August "
          "2026). The likeliest explanation is that the substitution and "
          "resubscribe figures were transposed. This is consistent with the "
          "evidence rather than proven, because the original chart was never saved."),

    ("h3", "2.2 What to publish instead"),
    ("p", "Substitution is real and it is larger than either published figure, "
          "but it is sensitive to the cohort. Two effects pull in opposite "
          "directions: censoring drags the rate down, because cancellers late in "
          "a window have not had 60 days, and pre-rollout contamination drags it "
          "up, because cancellers before 20 June behave differently. Only one "
          "cohort is clean on both counts."),
    ("b", "Publish 65.4%  —  cancellers between 20 June and 4 July 2026, the only "
          "window that is both fully post-rollout and fully matured at 60 days. "
          "18,830 of 28,787 bought a one-time top-up, median 12.2 days."),
    ("table", "Q1_TABLE"),
    ("p", "The wider readings are given so the sensitivity is visible rather than "
          "hidden. Do not sum substitution and resubscribe: they overlap, and the "
          "correct union is 80.7% returning in some form."),
    ("b", "One caveat that limits the resubscribe number  —  under default-ON, "
          "is_subscription fires True for an ordinary top-up where the customer "
          "simply left the toggle alone. The resubscribe rate therefore mixes "
          "deliberate recommitment with passive re-enrolment, and should not be "
          "read as evidence that cancellers actively want the product back."),

    ("h2", "3. What customers do with the toggle"),
    ("p", "This is the question the data answers best. Both directions are "
          "user-level, measured on the clean post-rollout window, with one "
          "explicitly filtered funnel per arm."),
    ("table", "Q2_TABLE"),
    ("h3", "3.1 What the numbers say"),
    ("b", "Nearly half of the customers shown an ON default turn it off  —  46.6%, "
          "and the median time to the tap is 7 seconds. That is a reflex on seeing "
          "the order screen, not a considered decision late in checkout."),
    ("b", "Resistance is growing, not settling  —  opt-out rose from 43.2% in July "
          "to 48.9% in August. If the default were teaching customers to accept "
          "subscriptions, this line would fall."),
    ("b", "Turning it off does not cost the sale  —  89.7% of opt-outs still "
          "completed the order against 91.8% of customers who left it on, a gap "
          "of 2.1 points. And opting out is decisive: only 0.58% toggled back on "
          "within the hour."),
    ("b", "The reverse pull is much weaker  —  18.5% of customers shown an OFF "
          "default turn it on across the quarter, and 13.9% to 14.0% within a "
          "single month. Roughly one in seven customers wants a subscription "
          "enough to switch it on unprompted."),
    ("p", "Read together, these say the subscription base is being built by the "
          "default rather than by demand, and that the gap between the two is "
          "widening. That is a commercial choice, not a defect, but it should be "
          "made knowingly."),
    ("b", "An open thread worth closing  —  of the 32,933 customers who opted in, "
          "only 10,576 submitted a purchase within the hour, and only 3,841 of "
          "those completions carried is_subscription = True. Either opt-ins are "
          "being reversed at the payment step or the opt-in does not always create "
          "a subscription. Those have opposite product implications and Amplitude "
          "cannot currently tell them apart."),

    ("h2", "4. Cancellation within 60 days"),
    ("h3", "4.1 What can be said"),
    ("p", "For customers in the tagged default-ON arm who bought with a "
          "subscription, on the fully observed cohort of 1 June to 4 July 2026:"),
    ("table", "Q3_TABLE"),
    ("b", "The renewal charge is the moment of truth  —  the median cancellation "
          "lands at 25.0 days and 21.3% of all cancellers act on days 29 to 32, "
          "when the first monthly charge appears. A further 6.7% of buyers cancel "
          "within 24 hours, which reads as immediate regret at the point of sale."),
    ("p", "This figure is sound on its own terms and can be presented on its own. "
          "It is a statement about default-ON subscribers, not a comparison."),

    ("h3", "4.2 Why the comparison you asked for cannot be made"),
    ("p", "The request was to compare that 44.8% against customers who were shown "
          "the toggle OFF and switched it on. That comparison is not available, "
          "and the reasons are structural rather than a matter of sample size "
          "alone."),
    ("table", "BLOCKERS"),
    ("b", "The decisive problem is selection, and it runs the same way as the "
          "answer  —  arm B's subscribers deliberately switched a default-OFF "
          "toggle on. Arm A's mostly left a pre-ticked box alone. A lower "
          "cancellation rate among deliberate opt-ins is exactly what selection "
          "predicts on its own, with no default effect at all. The arm B number "
          "is 34.3%, which is lower, and it would be read as proof that the "
          "default causes cancellation. Nothing in this data separates the two "
          "explanations, so presenting the pair would assert a causal claim the "
          "evidence does not carry."),

    ("h3", "4.3 What would answer it"),
    ("b", "A concurrent randomised default-OFF holdback after 20 June 2026  —  a "
          "small live holdback running at the same time as the ON population, "
          "with assignment fixed per user. Every arm available today is "
          "contaminated by overlap, sparse tagging, or self-selection, and no "
          "re-cut of existing data fixes that."),
    ("b", "Toggle state at submission on MTUOrderCompleteBtn  —  the single "
          "highest-value instrumentation fix. Today only transition taps exist, so "
          "the final state has to be inferred, and that is what leaves the opt-in "
          "gap in section 3.1 unresolved."),
    ("b", "Cancellation linked to the subscription purchased  —  every 60-day "
          "figure here uses an unfiltered cancellation event, so it measures "
          "'cancelled something', not 'cancelled this one'."),
    ("b", "Close the tagging gap  —  about 150,000 users per quarter see an order "
          "screen with no default_subscription_toggle value at all, roughly a "
          "quarter of the base. Their attach rate sits between the two arms, so "
          "they cannot be assumed to belong to either."),

    ("h2", "5. Method and the traps this avoids"),
    ("p", "An earlier version of this analysis was wrong on several of these, "
          "which is why they are listed explicitly."),
    ("table", "METHOD"),
    ("p", "Every number in this document was rebuilt and then adversarially "
          "re-tested by independent reviewers who were asked to refute it. Figures "
          "that did not survive were removed rather than softened. Funnel step "
          "counts in Amplitude use approximate counting, so raw counts can move by "
          "a fraction of a percent between identical runs; the rates are stable."),

    ("h2", "6. Sources"),
    ("b", "Evidence dashboard  —  every chart cited above, each stating its own "
          "denominator and window: 1c3815cw."),
    ("b", "Superseded  —  the first Subscription Journey document is the origin of "
          "the 45.3% claim, and the second version corrected it to 63.87% without "
          "identifying the cause. Both are superseded on this point by section 2."),
]

TABLES = [("ANSWERS", ANSWERS), ("Q1_TABLE", Q1_TABLE), ("Q2_TABLE", Q2_TABLE),
          ("Q3_TABLE", Q3_TABLE), ("BLOCKERS", BLOCKERS), ("METHOD", METHOD)]


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
        if kind == "cap":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(text)},
                "textStyle": {"italic": True, "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}})
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
    return "".join(r.get("textRun", {}).get("content", "")
                   for r in el["paragraph"].get("elements", []))


def find_marker(docs, doc_id, marker):
    doc = docs.documents().get(documentId=doc_id).execute()
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[{marker}]]":
            return el["startIndex"], len(para_text(el))
    return None, None


def insert_table(docs, doc_id, marker, data):
    idx, plen = find_marker(docs, doc_id, marker)
    if idx is None:
        print(f"  ! placeholder {marker} not found")
        return False
    rows, cols = len(data), len(data[0])
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx, "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx}, "rows": rows, "columns": cols}},
    ]}).execute()
    time.sleep(1.2)

    doc = docs.documents().get(documentId=doc_id).execute()
    table_el = next((el for el in doc["body"]["content"]
                     if "table" in el and el["startIndex"] >= idx - 2), None)
    if table_el is None:
        print(f"  ! table {marker} not found after insert")
        return False

    cells = []
    for r, row in enumerate(table_el["table"]["tableRows"]):
        for c, cell in enumerate(row["tableCells"]):
            cells.append((cell["content"][0]["startIndex"], r, c))

    reqs = []
    for start, r, c in sorted(cells, reverse=True):
        txt = data[r][c]
        if not txt:
            continue
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
            continue
        if txt in CHART_IDS:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"link": {"url": CHART + txt},
                              "weightedFontFamily": {"fontFamily": "Roboto Mono"},
                              "fontSize": {"magnitude": 8, "unit": "PT"}},
                "fields": "link,weightedFontFamily,fontSize"}})
        elif txt in STATUS_COLOR:
            red, green, blue = STATUS_COLOR[txt]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": red, "green": green, "blue": blue}}}},
                "fields": "bold,foregroundColor"}})
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

    extra = {cid: CHART + cid for cid in CHART_IDS}
    extra["1c3815cw"] = DASHBOARD
    extra["first version of the Subscription Journey investigation"] = DOC_V1
    extra["second version"] = DOC_V2
    extra["first Subscription Journey document"] = DOC_V1
    linkify(docs, doc_id, {**LINK_MAP, **extra})

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
