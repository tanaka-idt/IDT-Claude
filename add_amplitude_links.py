#!/usr/bin/env python3
"""
Add Amplitude chart links to the IMTU Subscription Journey doc, and correct the
cancellation-bracket figures that did not survive rebuilding.

WHY FIGURES CHANGED
-------------------
Rebuilding the bracket table as a single funnel over one cohort window exposed a
denominator error in the first version. The original table used n = 342,130,
which is close to the SUM of monthly unique purchasers (2,252 + 5,435 + 15,484 +
127,755 + 181,283 = 332,209) rather than the count of DISTINCT users over the
window, which is 272,026. Summing period-level uniques double-counts anyone
active in more than one month, and the numerators were inflated the same way.

Every bracket now sits on one denominator (272,026 distinct users, cohort
1 Mar - 31 Jul 2026) and each has a saved, linked Amplitude chart.

The attach-rate trend and the cadence split were also rebuilt and both reproduce
almost exactly, so those figures are unchanged.
"""

import time

from googleapiclient.discovery import build

from create_subscription_journey_doc import get_credentials
from linkify_refs import LINK_MAP, linkify

DOC_ID = "10nWxXEyzhn-uP2YvZa23qyLPpK-JjW2yfaOqKwASGgM"
AMP = "https://app.amplitude.com/analytics/BOSS/chart/"
DASH = "https://app.amplitude.com/analytics/BOSS/dashboard/mlfhkse6"

CHARTS = {
    "tyvyvyge": ("Attach rate by week",
                 "Share of tagged order completions carrying a subscription. Peak 45.49% "
                 "(week of 22 Jun) falling to 25.96% (week of 24 Aug) — eleven consecutive "
                 "weekly declines. Reproduced exactly."),
    "gfkcqj5t": ("Subscription purchasers per month",
                 "Unique subscription purchasers by month. Establishes the base size and shows "
                 "why monthly figures must not be summed — the distinct total for 1 Mar – 31 Jul "
                 "is 272,026, not the 332,209 the months add to."),
    "42u1rqz8": ("Cancellation within 24 hours",
                 "7.91% (21,510 of 272,026), median 178 seconds."),
    "m65f9ue3": ("Cancellation within 3 days",
                 "9.25% (25,164 of 272,026), median 488 seconds."),
    "syiky5x9": ("Cancellation within 7 days",
                 "13.16% (35,800 of 272,026), median 19.9 hours."),
    "2kxvu6t6": ("Cancellation within 14 days",
                 "19.17% (52,136 of 272,026), median 6.0 days."),
    "w9hl0x4l": ("Cancellation within 30 days",
                 "30.57% (83,148 of 272,026), median 13.9 days. The headline measure."),
    "a75n2jgf": ("30-day cancellation by renewal cadence",
                 "Weekly 49.36% (34,975 of 70,861) against monthly 23.96% (48,161 of 201,009). "
                 "The strongest measured driver; reproduced almost exactly."),
}

# Figures that did not survive the rebuild. Old -> new.
FIXES = [
    ("342,130", "272,026"),
    ("29.10%", "30.57%"),
    ("99,550", "83,148"),
    ("9.62%", "7.91%"), ("32,925", "21,510"), ("175 s (2.9 min)", "178 s (3.0 min)"),
    ("11.17%", "9.25%"), ("38,210", "25,164"), ("500 s (8.3 min)", "488 s (8.1 min)"),
    ("15.20%", "13.16%"), ("52,000", "35,800"), ("13.9 hours", "19.9 hours"),
    ("20.78%", "19.17%"), ("71,086", "52,136"), ("5.12 days", "6.0 days"),
    ("11.87 days (mean 12.72)", "13.9 days"),
    ("median 11.87 days", "median 13.9 days"),
    # point the bracket table's Chart column at the saved charts
    ("psuznfi6", "42u1rqz8"), ("a1bw4wf9", "m65f9ue3"),
    ("py2ht641", "syiky5x9"), ("jzu4k15o", "2kxvu6t6"), ("msvoc2b7", "w9hl0x4l"),
]

NEW_SECTION = [
    ("h2", "12. Amplitude source charts"),
    ("p", "Every headline number in this document now has a saved Amplitude chart behind it, "
          "each carrying its own title and a description stating the denominator, the date range "
          "and the caveats. All eight are collected in one dashboard: " + DASH),
    ("p", "Rebuilding the charts changed part of the analysis, and the changes are reflected "
          "above. The cancellation-bracket table originally used a denominator of 342,130, which "
          "is close to the sum of monthly unique purchasers rather than the count of distinct "
          "users across the window. Summing period-level uniques double-counts anyone who "
          "purchased in more than one month, and the numerators were inflated the same way. "
          "Rebuilt as a single funnel over one cohort window, the denominator is 272,026 distinct "
          "users and 30-day cancellation is 30.57%, not 29.10%. The direction of the finding is "
          "unchanged and slightly stronger — the earlier correction from the 12.7% figure in "
          "circulation still stands, and stands larger."),
    ("p", "The attach-rate trend and the cadence split were rebuilt on the same basis and both "
          "reproduce almost exactly, so those figures are unchanged."),
    ("table", "CHARTS"),
    ("h3", "12.1 How to read these charts"),
    ("b", "One denominator  —  every cancellation funnel uses unique users on the cohort window "
          "1 March to 31 July 2026, and all share the same 272,026 step-one population. Rates "
          "across brackets are therefore directly comparable."),
    ("b", "Right-censoring  —  purchasers late in the cohort window have not had a full 30 days "
          "in which to cancel, so every bracket rate is a floor rather than a point estimate."),
    ("b", "Events versus users  —  the attach-rate chart is measured on event totals because its "
          "question is about orders; every cancellation chart is measured on unique users because "
          "its question is about people. Do not compare the two directly."),
    ("b", "The 3-day chart carries a title but no description  —  it was added to the dashboard "
          "after creation, and the tool used cannot set a description on that path. Its figures "
          "are in the table above and one line can be pasted in manually."),
]

STYLE_MAP = {"h2": "HEADING_2", "h3": "HEADING_3", "p": "NORMAL_TEXT", "b": "NORMAL_TEXT"}


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in el["paragraph"]["elements"])


def main():
    docs = build("docs", "v1", credentials=get_credentials())

    # 1. corrections -------------------------------------------------------
    reqs = [{"replaceAllText": {"containsText": {"text": o, "matchCase": True},
                                "replaceText": n}} for o, n in FIXES]
    res = docs.documents().batchUpdate(
        documentId=DOC_ID, body={"requests": reqs}).execute()
    changed = sum(r.get("replaceAllText", {}).get("occurrencesChanged", 0)
                  for r in res.get("replies", []))
    print(f"corrections applied: {changed} occurrences")

    # 2. append the new section -------------------------------------------
    doc = docs.documents().get(documentId=DOC_ID).execute()
    end = doc["body"]["content"][-1]["endIndex"] - 1

    reqs, cur = [], end
    for kind, text in NEW_SECTION:
        if kind == "table":
            line = f"[[{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += len(line)
            continue
        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(line)},
            "paragraphStyle": {"namedStyleType": STYLE_MAP[kind]},
            "fields": "namedStyleType"}})
        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
            if "  —  " in text:
                lead = text.split("  —  ")[0]
                reqs.append({"updateTextStyle": {
                    "range": {"startIndex": cur, "endIndex": cur + len(lead)},
                    "textStyle": {"bold": True}, "fields": "bold"}})
        cur += len(line)

    for i in range(0, len(reqs), 40):
        docs.documents().batchUpdate(
            documentId=DOC_ID, body={"requests": reqs[i:i + 40]}).execute()
        time.sleep(0.25)
    print(f"appended section 12 ({len(reqs)} requests)")

    # 3. the chart table ---------------------------------------------------
    data = [["Chart", "Chart ID", "What it establishes"]]
    for cid, (name, desc) in CHARTS.items():
        data.append([name, cid, desc])

    doc = docs.documents().get(documentId=DOC_ID).execute()
    idx = plen = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == "[[CHARTS]]":
            idx, plen = el["startIndex"], len(para_text(el))
            break
    if idx is None:
        print("  ! CHARTS placeholder missing")
        return

    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx, "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx},
                         "rows": len(data), "columns": 3}},
    ]}).execute()
    time.sleep(1.0)

    doc = docs.documents().get(documentId=DOC_ID).execute()
    table_el = next((el for el in doc["body"]["content"]
                     if "table" in el and el["startIndex"] >= idx - 2), None)
    cells = []
    for r, row in enumerate(table_el["table"]["tableRows"]):
        for c, cell in enumerate(row["tableCells"]):
            cells.append((cell["content"][0]["startIndex"], r, c))

    reqs = []
    for start, r, c in sorted(cells, reverse=True):
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        elif c == 1:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"link": {"url": AMP + txt},
                              "weightedFontFamily": {"fontFamily": "Roboto Mono"},
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "link,weightedFontFamily,fontSize"}})
    for i in range(0, len(reqs), 40):
        docs.documents().batchUpdate(
            documentId=DOC_ID, body={"requests": reqs[i:i + 40]}).execute()
        time.sleep(0.25)
    print(f"chart table inserted ({len(data) - 1} charts)")

    # 4. make every chart id elsewhere in the doc a live link --------------
    chart_links = {cid: AMP + cid for cid in CHARTS}
    chart_links["mlfhkse6"] = DASH
    linkify(docs, DOC_ID, {**LINK_MAP, **chart_links})

    print(f"\nDone: https://docs.google.com/document/d/{DOC_ID}/edit")


if __name__ == "__main__":
    main()
