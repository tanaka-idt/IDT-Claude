#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU Subscription Journey — Investigation & Recommendations".

Data-driven investigation of the BOSS Revolution IMTU subscription journey:
toggle exposure, checkout, renewals, cancellation, reactivation. Reconciles Jira
(DCS / DTCBE / CRMC) against Amplitude project 650506 "BR app Prod".

Method: 8 parallel research passes reconciled against 4 adversarial verification
passes. Where a verification verdict contradicted a research finding, the verdict
governs. That pass changed the headline — three claims in circulation failed:

  * 30-day cancellation is 29.10%, not 12.7% (the prior figure was right-censored)
  * attach peaked in the week of 22 Jun at 45.49%, not in July
  * neither variant believed to limit toggle exposure has actually shipped

Companion HTML report carries the same content with charts and funnels.

Images are served from the public GitHub repo (Docs API needs public URLs;
IDT Drive sharing is org-restricted) — commit + push the PNGs before running.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from linkify_refs import LINK_MAP, linkify

SCOPES = ["https://www.googleapis.com/auth/documents",
          "https://www.googleapis.com/auth/drive"]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"
RAW_BASE = "https://raw.githubusercontent.com/tanaka-idt/IDT-Claude/main/"

TITLE = "IMTU Subscription Journey — Investigation & Recommendations"

AMP = "https://app.amplitude.com/analytics/BOSS/chart/"
EXTRA_LINKS = {
    "project 650506": "https://app.amplitude.com/analytics/BOSS/home/project/650506",
    "chart gb7jgqqz": AMP + "gb7jgqqz",
    "dashboard bx3h416b": "https://app.amplitude.com/analytics/BOSS/dashboard/bx3h416b",
    "dashboard dsyei9ee": "https://app.amplitude.com/analytics/BOSS/dashboard/dsyei9ee",
}

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Data-driven investigation · 30 August 2026 · DCS / IMTU · "
            "Amplitude project 650506 reconciled against Jira · Adversarially verified"),

    # ----------------------------------------------------------------- 1 ----
    ("h2", "1. Executive summary"),
    ("p", "Defaulting the IMTU subscription toggle to ON raised attach from near zero to a peak of "
          "45.49%. It also produced a subscription base that customers cancel at close to three times "
          "the rate currently believed, concentrated precisely on the days they are charged."),

    ("h3", "Three numbers in circulation are wrong"),
    ("b", "30-day cancellation is 29.10%, not 12.7%  —  the figure in circulation was right-censored: "
          "it counted cohorts that had not yet had 30 days in which to cancel. Re-run on a fully "
          "observed base of 342,130 unique subscription purchasers (1 Mar – 31 Jul 2026), 99,550 "
          "cancelled within 30 days. Chart gb7jgqqz's own definition, re-run today on an unchanged "
          "denominator, returns 27.83%."),
    ("b", "Attach peaked in June, not July, and has fallen for eleven consecutive weeks  —  45.49% in "
          "the week of 22 June down to 25.98% in the week of 24 August. The monthly series manufactured "
          "a false July peak by averaging across June's ramp."),
    ("b", "Neither limiting variant has shipped  —  DCS-5289 is QA Available; the entire V2 epic "
          "DCS-5297 is To Do. The brief assumed both were live. Anyone briefing that is wrong."),

    ("h3", "What the data shows"),
    ("b", "The toggle default is the largest lever in the product  —  users shown a default-ON toggle "
          "attach at 62.60% (208,950 users) against 5.45% for default-OFF (69,475), August 2026. But "
          "this is association, not causation: the default-OFF population is defined by already owning "
          "subscriptions, so it is selected on the outcome."),
    ("b", "Where the toggle is engaged, it is rejected  —  opt-out from default-ON runs at 49.13% per "
          "exposure (265,123 of 539,638) against opt-in from default-OFF at 6.51% (25,661 of 394,128). "
          "Among users who engage at all, 89.63% of default-ON engagements end with it off."),
    ("b", "Most subscriptions are created by inaction  —  57.20% of default-ON order screens produce no "
          "toggle interaction whatsoever (142,161 of 332,157 users interacted, Jun–Jul)."),
    ("b", "The charge date is the trigger  —  weekly cadence cancels at 48.60% within 30 days against "
          "monthly at 24.79% (n = 78,211 / 203,212, Jun–Jul). Both spike exactly at the renewal "
          "boundary: a 7-day comb for weekly, a single day-30 explosion for monthly."),
    ("b", "Cadence is derived, not chosen  —  a 1–7 day offer validity silently becomes a weekly "
          "charge. When customers pick a frequency explicitly they prefer 90-day by a wide margin."),
    ("b", "A confirmed consent defect has no QA record  —  DCS-5277 creates subscriptions for users "
          "never shown the toggle, 100% reproducible. Its QA task DCS-5310 was opened and closed "
          "“Won't fix” 33 seconds later."),

    ("h3", "The judgement this report asks for"),
    ("p", "Half the subscription base is behaving like people undoing something they did not choose. "
          "57.20% never touch the toggle; 49.13% of those who do switch it off; the median 24-hour "
          "canceller acts in under three minutes. Before adding retention, the programme needs to "
          "establish how much of its attach is consented — because a save flow applied to unintended "
          "subscriptions converts a consent problem into a revenue problem."),

    # ----------------------------------------------------------------- 2 ----
    ("h2", "2. Methodology and test conditions"),
    ("p", "Eight parallel research passes across Amplitude project 650506, Jira (DCS, DTCBE, CRMC) and "
          "the team's own internal analysis, reconciled against four adversarial verification passes "
          "whose standing instruction was to reproduce every number independently before accepting it. "
          "Where a verification verdict contradicted a finding, the verdict governs."),
    ("p", "That pass changed the headline. The 12.7% cancellation figure, the July attach peak and the "
          "belief that the limiting variants were live all failed verification."),

    ("h3", "2.1 Reading conventions"),
    ("b", "EVIDENCE  —  a measurement or directly quoted artefact, carrying its denominator, date range "
          "and source."),
    ("b", "HYPOTHESIS  —  an inference or proposed mechanism. Not measured."),
    ("b", "CANNOT ANSWER  —  not answerable with current instrumentation. These are collected in "
          "Section 7."),

    ("h3", "2.2 Two caveats that apply to every figure"),
    ("p", "Counts are events unless “unique users” is stated. Several events over-fire relative to "
          "users — MTUOrderScr at roughly 1.36–1.62× per order, and MTUEditSubscriptionCancelSuccess at "
          "about 1.38× per cancelling user-day. Never read an event count as a customer count."),
    ("p", "No production release date is obtainable from Jira. Every fixVersion on every subscription "
          "ticket carries released=false — the flag is unmaintained project-wide. All dates in Section 3 "
          "are Jira resolution or build dates, which precede store release by an estimated three weeks."),

    # ----------------------------------------------------------------- 3 ----
    ("h2", "3. Release and targeting timeline"),
    ("p", "Eight months, two policy reversals, and no rollout record anywhere. Only one post-launch "
          "targeting change has actually completed: smart-hide."),
    ("table", "TIMELINE"),

    ("h3", "3.1 What is actually live"),
    ("p", "Live: the V1 default-ON toggle at effectively 100% of traffic; smart-hide (DCS-4854); the "
          "re-added duplicate warning (DCS-5224); and the renewal reminder at charge date minus two "
          "days (DCS-4983)."),
    ("p", "Merged to a feature branch only — which Jira files under Done but which means not in "
          "production, with QA recorded “on DEV”: DCS-5172, DCS-5182, DCS-5205 and the consent fix "
          "DCS-5277."),
    ("p", "Specified but not shipped: DCS-5289, the entire V2 epic DCS-5297 including its Amplitude "
          "events (DCS-5300, DCS-5301) and A/B harness (DCS-5303), the enhanced cancellation flow "
          "(DCS-5257, DCS-5258), and payment-method change (DCS-4461, DCS-4463). Three cancellation "
          "children were explicitly abandoned Won't fix: DCS-4900, DCS-5066 and DCS-5100 — dropped "
          "scope, not merely delayed."),

    ("h3", "3.2 Intended versus implemented"),
    ("p", "The V1 targeting predicate has two incompatible readings, and this is the most consequential "
          "open discrepancy in the pack because it determines what DCS-5289 actually replaces."),
    ("p", "Reading A, from the internal core-logic reference: two independent gates evaluated in "
          "order — if a duplicate subscription exists, OFF; else if the customer has 3 or more active "
          "subscriptions, OFF; else if in the experiment control group, OFF; otherwise ON."),
    ("p", "Reading B, from DCS-5289's own description of the outgoing rule: “Toggle defaults to OFF "
          "only if the user has 3 or more active subscriptions AND the purchase is for the same offer "
          "to the same recipient.” Under this reading nothing defaults OFF unless offer and recipient "
          "also match — which contradicts a separate max_subscriptions reason existing at all."),
    ("p", "Either V1 shipped differently from its specification, or DCS-5289 is scoped against a false "
          "premise. Resolve this before it leaves QA."),
    ("p", "Separately, three suppression rules were added at implementation time (DCS-4854) and never "
          "written back into the definition ticket (DCS-4781) — including “the toggle OFF is only "
          "counted if the user completes a purchase”. They were, however, tested: QA enumerated all "
          "eight rules with individual verdicts, and the rule that failed was the one that diverged."),

    ("h3", "3.3 Two reversals in five months"),
    ("p", "The duplicate-subscription warning was removed on 21 April 2026 (DCS-4428) on the reasoning "
          "that it “gives the impression that the user needs to take some action”, then re-added on "
          "13 August (DCS-5224). The resubscribe toggle went from “must always show toggle on” "
          "(DCS-4205, March) to “hide subscription toggle” (DCS-5182, August)."),

    ("cap", "Diagram 2 — Every variant and targeting change, grouped by actual shipping status"),
    ("table", "IMG_VARIANTS"),

    # ----------------------------------------------------------------- 4 ----
    ("h2", "4. Behavioural analysis"),

    ("h3", "4.1 Offer exposure and toggle interaction"),
    ("p", "The exposure surface is MTUOrderScr, which carries default_subscription_toggle recording the "
          "default state actually shown — the correct denominator, and one the prior internal analysis "
          "did not use. 1,152,462 events in August, of which 18.98% carry no toggle state at all."),
    ("p", "On a clean partition of August traffic, grouped rather than filtered: default-ON 208,950 "
          "users converting at 62.60%; default-OFF 69,475 at 5.45%; untagged 59,366 at 7.00%. That is "
          "a factor of 11.5, not the 12.8 previously reported — the earlier figure came from three "
          "overlapping filtered funnels whose step-one counts summed to more users than actually exist."),
    ("table", "TOGGLE"),

    ("h3", "4.2 Checkout and confirmation"),
    ("p", "The real funnel is MTUOfferListScr → MTUOrderCompleteBtn → MTUOrderStatusSuccessScr / "
          "FailedScr / QueuedScr. August: 849,390 completion taps producing 686,314 successes, 133,778 "
          "failures and 12,308 queued. Roughly 2.0% of attempts reach no recorded outcome screen at all."),
    ("p", "Subscription and one-time orders convert within 0.53 percentage points of each other, and "
          "iOS and Android within 0.11 points (iOS 76.42%, Android 76.14%). The subscription mechanic "
          "does not measurably harm checkout. Subscription orders confirm faster — median 8 seconds "
          "from tap to success against 13 for one-time, consistent with a stored card."),
    ("p", "Order failure sits at roughly 14.4%, up about 1.4 points July to August, and "
          "offerTemporaryUnavailable more than accounts for the whole rise."),

    ("h3", "4.3 Renewals and payments"),
    ("p", "This is the largest blind spot in the product. A regex sweep of all 1,500 event names returns "
          "zero for both /renew/ and /recurr/ — there is no renewal event of any kind. A successful "
          "recurring charge became partially observable only on 10 August 2026, when MarketingTxnCompleted "
          "with product_category='MTU' began carrying subscription=true; it had been zero on all 100 "
          "prior days."),
    ("p", "Renewal FAILURE remains entirely unobservable: MarketingTxnFailed never carries the "
          "subscription flag for MTU, 100% unset across 121 days. And a failed renewal cannot produce a "
          "cancellation by design — DTCBE-623 removed auto-cancellation for all payment scenarios in "
          "May 2024, after DTCBE-444's introduction of it lost roughly 30,000 subscriptions."),
    ("p", "There is no dunning ladder. A customer whose renewal fails receives nothing, on any channel "
          "(CRMC-3299, in backlog since 2024)."),

    ("h3", "4.4 Reactivation and post-cancellation"),
    ("p", "45.3% of cancelled subscribers return to one-time top-ups. Demand persists after "
          "cancellation — what was rejected is the recurring mechanic, not the product. That is the "
          "single most encouraging number in this report, and it reframes cancellation as substitution "
          "rather than churn for a large share of the base."),

    ("cap", "Diagram 1 — The current journey as measured. Dashed steps exist but emit no event"),
    ("table", "IMG_CURRENT"),

    # ----------------------------------------------------------------- 5 ----
    ("h2", "5. Variant comparison"),
    ("p", "The comparison the brief asks for is not currently available, for a specific and fixable "
          "reason."),
    ("table", "VARIANTS"),
    ("p", "A taxonomy defect will mislead the next analyst: two A/B properties coexist undeleted, and "
          "the broken one — which recorded feature-flag state rather than arm assignment and tagged "
          "unenrolled users (DCS-4369) — is still being written, and is now the only populated A/B "
          "property. Anyone segmenting by it will get a confident, wrong answer."),
    ("p", "The one genuine opportunity: A_B_subscription_toggle_test_id is balanced and populated for "
          "May and June 2026, at roughly 35,000 and 58,000 events per arm. This is the only causal "
          "readout the programme has, and it has never been analysed."),

    # ----------------------------------------------------------------- 6 ----
    ("h2", "6. Cancellation findings"),
    ("p", "Time-to-cancel is bimodal: an immediate-regret spike inside the first hour, a quiet trough "
          "across days one to four, then a much larger mass locked to the renewal charge."),
    ("table", "BRACKETS"),

    ("h3", "6.1 The immediate cluster is undo, not churn"),
    ("p", "16.9% of all 30-day cancellers act within the first hour, at a median of 175 seconds. Two "
          "and a half minutes is not deliberation — it is someone discovering a subscription on the "
          "confirmation screen or the receipt and reversing it. No reason is captured, so nothing is "
          "learned from any of it."),
    ("p", "Whether this is genuine regret or promotional capture-then-cancel is not currently knowable. "
          "DCS-5293 raises exactly this question and asks the team to confirm whether a promo-created "
          "subscription can even be identified — so today, it cannot."),

    ("h3", "6.2 The delayed cluster is locked to the charge date"),
    ("p", "Weekly subscriptions produce a 7-day comb: the day-7 peak runs 19.3× the non-boundary daily "
          "baseline, and eight boundary days hold 47.9% of all 60-day cancellers — on 13% of the "
          "elapsed days. Monthly subscriptions are flat for 28 days with no day-7 spike at all, then "
          "35.9% of cancellers arrive in the day 29–32 window at 12.2× baseline. The median monthly "
          "subscriber cancels at 29.96 days: the moment of the first renewal charge."),
    ("p", "The renewal reminder reshapes when people cancel but not whether they cancel. After DCS-4983 "
          "moved it to charge date minus two days, the day-5 share of weekly cancellations more than "
          "doubled from 5.64% to 12.66% and the median moved about a day earlier — but the total rate "
          "moved just 0.46 points, from 33.04% to 33.50%. It warns people in time to cancel; it does "
          "not persuade them to stay. Caveat: these are different calendar cohorts, not randomised groups."),

    ("h3", "6.3 Ranked drivers"),
    ("table", "DRIVERS"),

    ("cap", "Diagram 3 — Immediate cancellation, within 24 hours"),
    ("table", "IMG_IMMEDIATE"),
    ("cap", "Diagram 4 — Delayed cancellation, by cadence"),
    ("table", "IMG_DELAYED"),

    # ----------------------------------------------------------------- 7 ----
    ("h2", "7. Tracking gaps"),
    ("p", "Each row is a missing event or property, and each blocks a specific question the programme "
          "is actively asking."),
    ("table", "GAPS"),
    ("p", "Two live taxonomy defects will silently distort analysis: both A/B properties coexist with "
          "the broken one still writing; and gp:imtu_cls_label carries both “none” and “(none)” as "
          "distinct values, covering 45,684 subscription creators — 17.7% of the base — with a 7.4-point "
          "cancellation difference between them."),

    # ----------------------------------------------------------------- 8 ----
    ("h2", "8. Recommended future-state journey"),
    ("p", "The recommended journey changes three things. It refuses to create a subscription without a "
          "rendered toggle. It stops deriving weekly cadence from short offer validity. And it offers a "
          "single genuine alternative at cancellation — without obstructing the cancel path."),
    ("p", "The sharpest risk in this pack sits on that third change. A large share of the cancellation "
          "pool is people undoing a subscription they never chose. Deflecting them into a skip or a "
          "discount re-banks revenue they never authorised. Any retention readout must be split by "
          "whether the subscription was toggle-created — and that split needs the cancellation-reason "
          "property that does not yet exist."),
    ("cap", "Diagram 5 — Recommended future state"),
    ("table", "IMG_FUTURE"),

    # ----------------------------------------------------------------- 9 ----
    ("h2", "9. Prioritised recommendations"),
    ("table", "RECS"),
    ("h3", "9.1 Explicitly not recommended"),
    ("p", "Opening a regression ticket on app version 26.8.1: its 2.19-point conversion deficit sits "
          "inside a 4.60-point spread across versions, and it is not the worst build. And attributing "
          "the Stripe request-rate spikes (DCS-5252) to the default-ON toggle: eleven same-second "
          "timers cannot mechanically produce the observed rate."),

    # ---------------------------------------------------------------- 10 ----
    ("h2", "10. Limitations and additional data required"),
    ("b", "Right-censoring caused the largest error corrected here  —  12.7% to 29.10%. Every funnel in "
          "this report ends 31 July so all cohorts have a full 30 days. The 60-day reactivation figures "
          "are still censored and should be read as floors."),
    ("b", "Funnel arms are not clean partitions  —  a user who viewed order screens in more than one "
          "default state appears in more than one arm, so the arm counts sum to more than the distinct base."),
    ("b", "No confidence intervals anywhere  —  the 0.53-point checkout gap and the 0.11-point platform "
          "gap are reported at equal weight. At these sample sizes the first is likely significant and "
          "the second almost certainly noise."),
    ("b", "No production release dates exist in Jira  —  the timeline is built on resolution and build "
          "dates, with an estimated three-week lag to store release."),
    ("b", "The 28.4% failing-subscription pool is not observable in Amplitude  —  it came from an April "
          "2026 database analysis and cannot be refreshed or trended without warehouse access."),

    ("h3", "10.1 Data required to close the remaining questions"),
    ("b", "Subly or IDTPay billing records  —  to test any link between failed renewals and cancellation. "
          "Not answerable in Amplitude at all."),
    ("b", "Warehouse access  —  to compute repeat-versus-new recipient status. The phone number is on "
          "both the order and cancel events but cannot be joined in Amplitude."),
    ("b", "A decision record for the V1 experiment  —  none exists anywhere in Jira. No ticket records "
          "a decision to conclude the test and go to 100%."),

    ("h2", "11. Source note"),
    ("p", "Amplitude org BOSS (127967), project 650506 “BR app Prod”, queried 30 August 2026. Jira "
          "projects DCS, DTCBE and CRMC at idtjira.atlassian.net. Internal analysis generators in the "
          "IDT-Claude repository. Prior charts referenced and re-derived: gb7jgqqz, dsyei9ee, bx3h416b. "
          "A companion HTML report carries the same content with charts, funnels and the same five "
          "flowcharts."),
]

# ---------------------------------------------------------------- tables ----

TIMELINE = [
    ["Date", "Ticket", "Change", "Status"],
    ["2025-12-29", "DCS-3789", "A/B config for the toggle. Two arms, “50k users (TDB)”. No allocation, metric, MDE or stop rule. Closed with no QA by explicit waiver.", "Done"],
    ["2026-01-09", "DCS-3818", "V1 epic “Subscription Toggle and Frequency”. 52 children. Never closed.", "In Progress"],
    ["2026-04-01", "DCS-4369", "Bug: the A/B property reported feature-flag state rather than arm assignment, and tagged unenrolled users.", "Fixed"],
    ["2026-04-21", "DCS-4428", "Duplicate-subscription warning removed — “gives the impression that the user needs to take some action”.", "Reversed Aug"],
    ["2026-07-08", "DCS-4854", "Smart-hide: the toggle stops being shown after 3 off-toggles. The only completed post-launch targeting change.", "LIVE"],
    ["2026-07-16", "DCS-4983", "Renewal reminder moved to charge date minus 2 days.", "LIVE"],
    ["2026-08-12", "DCS-5182", "Resubscribe flow — hide the toggle. Reverses DCS-4205.", "Feature branch"],
    ["2026-08-13", "DCS-5224", "Duplicate warning re-added, reversing DCS-4428 four months later.", "LIVE"],
    ["2026-08-25", "DCS-5172", "Insurance cross-sell flag; in insurance_priority mode the subscription toggle is hidden.", "Feature branch"],
    ["2026-08-26", "DCS-5289", "Default OFF when the user has ≥1 active subscription.", "NOT LIVE"],
    ["2026-08-28", "DCS-5277", "Consent-defect fix (insurance path).", "Feature branch"],
]

TOGGLE = [
    ["Metric", "Value", "Denominator", "Window"],
    ["Attach, default-ON", "62.60%", "208,950 unique users", "1–28 Aug 2026"],
    ["Attach, default-OFF", "5.45%", "69,475 unique users", "1–28 Aug 2026"],
    ["Attach, untagged", "7.00%", "59,366 unique users", "1–28 Aug 2026"],
    ["Opt-out per exposure (default-ON)", "49.13%", "265,123 / 539,638 events", "1–28 Aug 2026"],
    ["Opt-in per exposure (default-OFF)", "6.51%", "25,661 / 394,128 events", "1–28 Aug 2026"],
    ["Engagements ending OFF", "89.63%", "198,455 / 221,408 taps", "1 Jun – 30 Aug 2026"],
    ["Default-ON screens with NO interaction", "57.20%", "142,161 of 332,157 users interacted", "Jun–Jul 2026"],
    ["Order screens carrying no toggle state", "18.98%", "218,696 / 1,152,462 events", "Aug 2026"],
    ["Attach, week of 22 Jun (peak)", "45.49%", "instrumented order-complete events", "week of 22 Jun"],
    ["Attach, week of 24 Aug", "25.98%", "instrumented order-complete events", "week of 24 Aug"],
]

VARIANTS = [
    ["Comparison", "Status", "Why"],
    ["DCS-5289 variant vs control", "IMPOSSIBLE", "The variant is not in production. There is nothing to measure."],
    ["Randomised A/B arms, post-GA", "IMPOSSIBLE", "Variant tagging effectively stopped in July. Arm B carries 143 users — no power."],
    ["Randomised A/B arms, May–Jun", "AVAILABLE, NOT RUN", "A_B_subscription_toggle_test_id is balanced and populated — ~35k (May) and ~58k (Jun) events per arm. The only causal readout the programme has."],
    ["Default ON vs OFF, observational", "CONFOUNDED", "62.60% vs 5.45% attach; 30.74% vs 24.86% cancellation. Selected on the outcome — the OFF arm is defined by prior subscription ownership."],
    ["Platform / app version / country / cadence / tenure", "AVAILABLE", "All segmentable today. Cadence is the one that matters."],
]

BRACKETS = [
    ["Bracket", "Cancellers", "Rate", "Median time-to-cancel", "Chart"],
    ["Within 24 hours", "32,925", "9.62%", "175 s (2.9 min)", "psuznfi6"],
    ["Within 3 days", "38,210", "11.17%", "500 s (8.3 min)", "a1bw4wf9"],
    ["Within 7 days", "52,000", "15.20%", "13.9 hours", "py2ht641"],
    ["Within 14 days", "71,086", "20.78%", "5.12 days", "jzu4k15o"],
    ["Within 30 days", "99,550", "29.10%", "11.87 days (mean 12.72)", "msvoc2b7"],
    ["By cadence — weekly", "38,008 / 78,211", "48.60%", "—", "Jun–Jul cohort"],
    ["By cadence — monthly", "50,375 / 203,212", "24.79%", "29.96 days", "Jun–Jul cohort"],
]

DRIVERS = [
    ["Driver", "Verdict", "Evidence"],
    ["Renewal cadence / charge dates", "SUPPORTS — strongest",
     "Weekly 48.60% vs monthly 24.79% at 30 days (n = 78,211 / 203,212, Jun–Jul). Day-7 peak 19.3× baseline; 8 boundary days hold 47.9% of 60-day cancellers. Holds within corridors: Guatemala weekly 53.82% vs monthly 27.71%."],
    ["Customer tenure", "SUPPORTS — confounded",
     "VIP 43.33% (21,288/49,129) down to one-transaction 23.50% (10,610/45,145). Two readings fit equally: redundant stacked subscriptions, or simply being able to find the cancel control."],
    ["Top-up amount", "SUPPORTS within cadence",
     "$10 moves from 36.20% overall to 51.30% within weekly — the overall series was a cadence mix artefact. Non-monotonic at the low end, which a simple bill-shock story does not fit."],
    ["Recipient country", "SUPPORTS",
     "June cohort: Nicaragua 40.80%, Honduras 39.50%, El Salvador 38.94%, Guatemala 36.72%, Jamaica 28.01%, Mexico 26.38%, Dominican Rep. 24.29%, Haiti 22.04%, Ethiopia 17.22%. A previously unreported low tier sits below: Nigeria 14.76%, Cuba 15.34%."],
    ["Recipient stacking", "SUPPORTS",
     "Holding recipient_phone_number constant retains 24.35 of the 29.10 points (n = 567,345 user×recipient, Mar–Jul). New-vs-repeat recipient is NOT answerable in Amplitude."],
    ["Operator / carrier", "SUPPORTS weakly",
     "Largely collinear with country. The one clean within-corridor contrast is Haiti: Digicel 28.09% vs Natcom 23.69%."],
    ["Toggle default state", "ASSOCIATION ONLY",
     "default-ON 30.74% vs default-OFF 24.86% (Jun–Jul). Not causal — the OFF arm is defined by prior ownership."],
    ["Renewal reminders", "TIMING, NOT RATE",
     "Day-5 share rose 5.64% → 12.66% and the median moved ~1 day earlier; total rate moved +0.46 pp. Reminder RECEIPT is unobservable — no first-party event exists."],
    ["Failed payments", "CANNOT ANSWER",
     "No renewal-decline event exists; MarketingTxnFailed never carries the subscription flag for MTU. And by design a failed renewal cannot cause cancellation (DTCBE-623)."],
    ["Promotions / discount abuse", "CANNOT ANSWER",
     "DCS-5293 asks the team to confirm whether a promo-created subscription can even be identified — so today it cannot."],
    ["Payment method", "CANNOT ANSWER",
     "No payment property exists on MTUOrderCompleteBtn (32 props), MTUOrderStatusSuccessScr (31), MTUOrderScr (30) or MTUEditSubscriptionCancelSuccess (13)."],
    ["Platform", "SUPPORTS — small",
     "Android 33.82% vs iOS 29.24% (n = 83,604 / 174,544, Jun–Jul). Must be queried user-scoped; event scope returns 100% unset."],
]

GAPS = [
    ["Missing", "Question it blocks", "Status"],
    ["Cancellation reason on the cancel events",
     "Why do people cancel, and how many because the subscription was unintended? The premise of the entire V2 epic.", "Not ticketed"],
    ["subscription flag on MarketingTxnFailed",
     "Involuntary churn — how many, when, why. The pipeline already sets this flag on successes as of 10 Aug. One property; the highest-leverage fix available.", "Not ticketed"],
    ["Any renewal event",
     "Renewal volume, success rate, cycles survived, cohort decay. A regex sweep of all 1,500 event names returns zero for /renew/ and /recurr/.", "Not ticketed"],
    ["Per-subscription identifier",
     "Subscription lifetime, and whether a cancellation maps to the subscription just created. All analysis is forced to user level today.", "Not ticketed"],
    ["Toggle-shown signal",
     "Whether an unset toggle state means “correctly not rendered” or “not instrumented” — exactly the ambiguity DCS-5277 turns on.", "Not ticketed"],
    ["Toggle default reason",
     "How often the duplicate rule or the subscription cap actually fires. Four outcomes documented; none emitted.", "Not ticketed"],
    ["Toggle state at payment (MTUSubscriptionPayTap)",
     "The true final toggle state at purchase. Currently funnel-inferred.", "Defined, not built"],
    ["Notification analytics",
     "Whether a reminded user cancels, tops up or updates their card.", "DCS-5260 To Do"],
    ["V2 presentation events",
     "Any V2-versus-V1 comparison at all.", "DCS-5300 / 5301 To Do"],
    ["Offer selection",
     "Any offer-selection to checkout conversion rate. 250,026 recorded selections against 849,390 completion taps — at least 70.6% unrecorded.", "Not ticketed"],
    ["Offer validity as a property",
     "A direct test of “validity drives cadence drives churn” — the mechanism behind the strongest driver found.", "Not ticketed"],
    ["Subscription state model",
     "Reproducing or trending the 28.4% failing-subscription pool. Database only.", "Not ticketed"],
]

RECS = [
    ["#", "Recommendation", "Evidence", "Impact / risk", "Effort", "Success metric", "Experiment"],
    ["P0 · R1", "Size and remediate the consent population, and re-open QA",
     "DCS-5277 100% reproducible; fix on a feature branch with empty fixVersions; QA task DCS-5310 closed “Won't fix” in 33 s",
     "Bounds a live regulatory exposure. Risk: remediation contact may surface subscriptions customers had not noticed — sequence with Legal",
     "S for QA; M for the cohort query", "A dated count of affected subscriptions and a QA pass on a production build", "None — verification, not experimentation"],
    ["P0 · R2", "Test whether the consent failure mode recurs on the smart-hide path",
     "DCS-5277's mechanism is toggle ON in state, toggle not rendered, subscription created. DCS-4854 hides the toggle by design while the default may still be ON. Never tested.",
     "Potentially a second, much larger consent population — smart-hide is live to everyone; the insurance path is not",
     "S", "Completed orders with a subscription and no preceding toggle tap in session", "Not applicable — a test case"],
    ["P0 · R3", "Run the May–June randomised readout and freeze a V1 baseline before DCS-5289 ships",
     "A_B_subscription_toggle_test_id balanced and populated, ~35k (May) / ~58k (Jun) events per arm",
     "Converts the programme's central claim from observational to causal. Risk: two concurrent tests may overlap",
     "S — queries only", "Arm-level attach AND 30-day cancellation on unique users, plus a frozen pre-DCS-5289 baseline", "Ship DCS-5289 randomised, not globally, so its effect on cancellation is readable"],
    ["P0 · R4", "Instrument the four things that make the core questions answerable",
     "Section 7. In order: subscription flag on MarketingTxnFailed; cancellation reason with an explicit “I didn't mean to subscribe”; a per-subscription id; a toggle-shown event carrying the default reason",
     "Makes involuntary churn measurable for the first time",
     "S · S–M · M · M", "Each blocked question becomes answerable with a named query", "Attach to DCS-5260 and DCS-5300 — raise DCS-5300 above the behaviour changes it is meant to measure"],
    ["P1 · R5", "Stop defaulting weekly cadence from 7-day offer validity",
     "Weekly 48.60% vs monthly 24.79% at 30 days; the 7-day comb holds 47.9% of cancellers on 13% of elapsed days; explicit choosers prefer 90-day",
     "The largest available reduction in early cancellation. Risk: fewer charges per subscription — do not assume the churn saving nets positive",
     "M — the backend lever exists as DCS-5290", "Fee revenue per purchaser per 90 days, not attach rate", "Three arms on 7-day-validity offers: default weekly, default monthly, no default. Randomise."],
    ["P1 · R6", "Build a skip or defer path instead of only cancel",
     "Only active/cancelled states exist; ~94% of cancel-flow entrants complete; the dialog deflects ~1%; 45.3% substitute to one-time top-ups",
     "Converts timing-driven cancellations into deferrals. Risk: deflecting unintended subscriptions re-banks unauthorised revenue",
     "M — a launch_at bump on the existing timer row, no new state", "90-day revenue per cancel-flow entrant, not deflection alone", "Ship as a fifth variant inside the DCS-5257/5258 retention A/B, not as a separate release"],
    ["P1 · R7", "Ship the unblocked half of payment-method change",
     "DCS-4461 marks Scenario 1 feasible with current capabilities; only the future-dated case is blocked on fraud. Both High, both unassigned, under an epic marked Low",
     "Removes an involuntary-churn path — an expiring card currently forces cancellation",
     "M", "In-app payment-method changes completed; reduction in cancel-and-recreate", "None required — instrument before and after"],
    ["P2 · R8", "Scope the stacking guardrail per recipient, not per account",
     "A sender supporting three recipients has three legitimate subscriptions; a ≥1-per-account rule defaults the second and third OFF",
     "Raise on DCS-5289 before it leaves QA. Risk: leaves same-recipient stacking under-addressed if mis-specified",
     "S — a spec change", "Attach retained on distinct-recipient purchases", "Fold into the DCS-5289 randomisation"],
    ["P2 · R9", "Localise offerTemporaryUnavailable",
     "It more than accounts for the entire +1.4 pp rise in order failure July → August",
     "One query — split by recipient_carrier and recipient_country, plotted daily — distinguishes an incident from a structural ramp",
     "S to diagnose", "Order failure returned to ≤14.4%", "None — diagnosis"],
    ["P2 · R10", "Clean the two taxonomy defects",
     "Both A/B properties coexist with the broken one still writing; gp:imtu_cls_label carries both “none” and “(none)” across 45,684 creators, 7.4 pp apart",
     "Prevents the next analyst reaching a confident wrong conclusion",
     "S", "Single-valued buckets; the broken property deleted or blocked", "None"],
]

TABLES = [("TIMELINE", TIMELINE), ("TOGGLE", TOGGLE), ("VARIANTS", VARIANTS),
          ("BRACKETS", BRACKETS), ("DRIVERS", DRIVERS), ("GAPS", GAPS), ("RECS", RECS)]

IMAGES = [
    ("IMG_VARIANTS", "imtu_journey_2_variants.png", 468.0, 2405, 2272),
    ("IMG_CURRENT", "imtu_journey_1_current.png", 468.0, 2405, 2508),
    ("IMG_IMMEDIATE", "imtu_journey_3_immediate.png", 468.0, 2142, 1918),
    ("IMG_DELAYED", "imtu_journey_4_delayed.png", 468.0, 2273, 2036),
    ("IMG_FUTURE", "imtu_journey_5_future.png", 468.0, 2405, 2508),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}

CELL_COLOR = {
    "LIVE": (0.05, 0.48, 0.42), "NOT LIVE": (0.70, 0.15, 0.12),
    "Feature branch": (0.65, 0.35, 0.04), "Reversed Aug": (0.65, 0.35, 0.04),
    "IMPOSSIBLE": (0.70, 0.15, 0.12), "CONFOUNDED": (0.65, 0.35, 0.04),
    "AVAILABLE": (0.05, 0.48, 0.42), "AVAILABLE, NOT RUN": (0.25, 0.32, 0.62),
    "CANNOT ANSWER": (0.45, 0.42, 0.50),
}


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
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in el["paragraph"]["elements"])


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
    time.sleep(1.0)

    doc = docs.documents().get(documentId=doc_id).execute()
    table_el = None
    for el in doc["body"]["content"]:
        if "table" in el and el["startIndex"] >= idx - 2:
            table_el = el
            break
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
        elif txt in CELL_COLOR:
            red, green, blue = CELL_COLOR[txt]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": red, "green": green, "blue": blue}}}},
                "fields": "bold,foregroundColor"}})
        elif c == 0 and (txt.startswith("P0") or txt.startswith("P1") or txt.startswith("P2")):
            tone = {"P0": (0.70, 0.15, 0.12), "P1": (0.65, 0.35, 0.04),
                    "P2": (0.05, 0.48, 0.42)}[txt[:2]]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": tone[0], "green": tone[1], "blue": tone[2]}}}},
                "fields": "bold,foregroundColor"}})
    batched(docs, doc_id, reqs, size=40)
    return True


def insert_image(docs, doc_id, marker, fname, width, nw, nh):
    idx, plen = find_marker(docs, doc_id, marker)
    if idx is None:
        print(f"  ! placeholder {marker} not found")
        return False
    height = round(width * nh / nw, 1)
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx, "endIndex": idx + plen - 1}}},
        {"insertInlineImage": {
            "location": {"index": idx}, "uri": RAW_BASE + fname,
            "objectSize": {"width": {"magnitude": width, "unit": "PT"},
                           "height": {"magnitude": height, "unit": "PT"}}}},
        {"updateParagraphStyle": {
            "range": {"startIndex": idx, "endIndex": idx + 1},
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT", "alignment": "CENTER"},
            "fields": "namedStyleType,alignment"}},
    ]}).execute()
    time.sleep(0.4)
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

    for marker, fname, w, nw, nh in IMAGES:
        ok = insert_image(docs, doc_id, marker, fname, w, nw, nh)
        print(f"  image {marker}: {'ok' if ok else 'FAILED'} ({fname})")

    linkify(docs, doc_id, {**LINK_MAP, **EXTRA_LINKS})

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
