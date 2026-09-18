#!/usr/bin/env python3
"""
Updates the existing "IMTU Subscriptions - Core Logic Reference" Google Doc with
Amplitude findings, in place (so the shared URL stays valid).

Changes:
  1. §4.4 - replace the "A/B outcome TBD" sentence with the measured conclusion.
  2. §10 - replace the "A/B conclusion pending" gap bullet.
  3. Insert "Appendix A - Instrumentation and measurement" before §11 Sources.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents",
          "https://www.googleapis.com/auth/drive"]
BASE = Path(__file__).parent
DOC_ID = "1tWVkbGX3-oXGXCsRwC76TCWCK-DBWj-xzAIhmaYkgI4"

STYLE_MAP = {"h2": "HEADING_2", "h3": "HEADING_3", "p": "NORMAL_TEXT",
             "b": "NORMAL_TEXT"}

REPLACEMENTS = [
    # ---- §4.4 : the A/B question is now answered by the data
    ("Open question, recorded in the spec and still unresolved: when the test "
     "concludes, which group becomes the permanent default.",
     "The spec recorded the permanent default as an open question. Amplitude "
     "now answers it in practice: control-group (B) assignment fell to 4 events "
     "in July 2026 and 0 in August, so the control arm is no longer being "
     "served, and default-ON has been rolled out broadly. See Appendix A."),
    # ---- §10 : gap bullet superseded
    ("A/B conclusion pending  —  the permanent toggle default has not been "
     "decided.",
     "A/B formally unclosed  —  the control arm has stopped being served and "
     "default-ON is live, but no written decision record closes the experiment "
     "or states the permanent default. Worth recording somewhere durable."),
]

APPENDIX = [
    ("h2", "Appendix A — Instrumentation and measurement"),
    ("p", "Added 12 August 2026 from Amplitude (org BOSS, project 650506 — BR "
          "app Prod). This appendix records what the product analytics can and "
          "cannot tell us about the logic described above. It matters because "
          "several rules in this document can only be verified, or monitored for "
          "drift, if the corresponding event data exists."),

    ("h3", "A.1 The toggle is measurable; the reason behind it is not"),
    ("p", "MTUOrderScr carries default_subscription_toggle, with values on and "
          "off. This closes the instrumentation gap the toggle spec raised as "
          "AC-12 — though under a different property name than the spec "
          "proposed, so anyone searching for toggleDefaultState will not find "
          "it."),
    ("p", "What is still missing is the reason. Section 4.1 defines four "
          "outcomes — duplicate, max_subscriptions, experiment and default — but "
          "no reason property is emitted. We can therefore see what state the "
          "toggle was presented in, but not which rule produced it. In practical "
          "terms, we cannot currently measure how often the duplicate rule or "
          "the 3-subscription cap fires, which makes it hard to judge whether "
          "either threshold is set correctly."),

    ("h3", "A.2 The A/B experiment has effectively ended"),
    ("p", "Control-group assignment on MTUOrderScr (A = default ON, B = default "
          "OFF):"),
    ("b", "May 2026  —  A 6,930 · B 317,801"),
    ("b", "June 2026  —  A 21,080 · B 25,206"),
    ("b", "July 2026  —  A 27,604 · B 4"),
    ("b", "August 2026 (to the 11th)  —  A 7,394 · B 0"),
    ("p", "The control arm stopped being served during July. The share of order "
          "screens presenting the toggle already ON, excluding events without "
          "the property, moved accordingly: 4% in May, 39% in June, 66% in July, "
          "61% in August to date."),
    ("p", "Two readings follow. First, default-ON is now the live behaviour for "
          "roughly two thirds of order screens, which is consistent with the "
          "subscription volume step-change from March 2026 onward. Second, the "
          "residual third defaulting to OFF is no longer explained by the "
          "experiment — with the control arm retired, those are the eligibility "
          "rules in section 4.1 firing. That is a useful proxy for how often the "
          "duplicate and 3-subscription conditions are hit, and the closest we "
          "can get to it until a reason property exists."),

    ("h3", "A.3 Cancellation captures no reason — confirmed"),
    ("p", "MTUEditSubscriptionCancelSuccess carries offer, recipient, frequency "
          "and A/B identifiers, but no cancellation-reason property. Section 7.1's "
          "statement that no reason is captured is confirmed directly against the "
          "event taxonomy rather than inferred from ticket history. Voluntary "
          "churn therefore cannot be attributed to a cause from product analytics "
          "alone."),

    ("h3", "A.4 Renewals and payment failures are invisible in product analytics"),
    ("p", "No client-side event represents a recurring charge attempt, a "
          "decline, a fallback to a second payment method, or a subscription "
          "entering the failing state described in section 5.3. This is expected "
          "— renewals are executed server-side by the Timers API, with no app "
          "session involved — but it has a consequence worth stating plainly: "
          "the 28.4% failing population in section 6.1 is not observable in "
          "Amplitude. It surfaced through a database analysis, and monitoring it "
          "requires that route rather than a dashboard."),

    ("h3", "A.5 Braze delivery is instrumented, but the conditions are not"),
    ("p", "Braze (Appboy) delivery events are flowing into Amplitude: Push "
          "Notification Send, Open, Abort and Bounce; Email Send, Delivery, "
          "Open, Click, Bounce, Unsubscribe and Abort; Canvas Entry, Canvas Step "
          "Progression and Canvas Conversion; Campaign Conversion; In-App "
          "Message Impression; and Content Card Send and Impression."),
    ("p", "This refines what section 9 says about Braze. Campaign sends and "
          "engagement are measurable in Amplitude, so the live campaign set can "
          "be enumerated from the data. What still lives only in Braze is the "
          "firing condition for each campaign. Note also that Braze email is an "
          "active channel here, whereas the lifecycle triggers in section 9 are "
          "push and SMS only."),
    ("p", "One caution: the presence of these event types does not by itself "
          "establish that any given campaign relates to IMTU subscriptions. They "
          "are Braze's standard set and cover the whole app. Confirming which "
          "campaigns touch subscription customers requires either a "
          "campaign-name breakdown in Amplitude or the CRM team."),

    ("h3", "A.6 What this changes"),
    ("b", "Nothing in the core logic is contradicted.  —  Every rule in "
          "sections 1 to 8 stands as written."),
    ("b", "One open question is now answered.  —  The permanent toggle default "
          "is default-ON in practice, even if it was never formally recorded."),
    ("b", "One claim moves from inferred to verified.  —  No cancellation "
          "reason is captured."),
    ("b", "One measurement gap is now explicit.  —  We cannot attribute a "
          "toggle-OFF default to its cause, which limits any tuning of the "
          "duplicate rule or the 3-subscription cap."),
]


def build_reqs(blocks, start):
    reqs, cur = [], start
    for kind, text in blocks:
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
        if kind in ("b", "p") and "  —  " in text:
            lead = text.split("  —  ")[0]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(lead)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        cur += len(line)
    return reqs


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in el["paragraph"]["elements"])


def main():
    creds = Credentials.from_authorized_user_file(str(BASE / "token.json"), SCOPES)
    docs = build("docs", "v1", credentials=creds)

    # 1 + 2 : targeted text replacements
    reqs = [{"replaceAllText": {
        "containsText": {"text": old, "matchCase": True},
        "replaceText": new}} for old, new in REPLACEMENTS]
    res = docs.documents().batchUpdate(
        documentId=DOC_ID, body={"requests": reqs}).execute()
    for i, r in enumerate(res.get("replies", [])):
        n = r.get("replaceAllText", {}).get("occurrencesChanged", 0)
        print(f"  replacement {i + 1}: {n} occurrence(s)")
    time.sleep(0.5)

    # 3 : insert appendix immediately before the Sources heading
    doc = docs.documents().get(documentId=DOC_ID).execute()
    idx = None
    for el in doc["body"]["content"]:
        if para_text(el).strip().startswith("11. Sources"):
            idx = el["startIndex"]
            break
    if idx is None:
        raise RuntimeError("Sources heading not found")
    print(f"  inserting appendix at index {idx}")

    reqs = build_reqs(APPENDIX, idx)
    for i in range(0, len(reqs), 40):
        docs.documents().batchUpdate(
            documentId=DOC_ID, body={"requests": reqs[i:i + 40]}).execute()
        time.sleep(0.25)

    print("\nDONE")
    print(f"https://docs.google.com/document/d/{DOC_ID}/edit")


if __name__ == "__main__":
    main()
