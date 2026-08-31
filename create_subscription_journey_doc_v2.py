#!/usr/bin/env python3
"""
Creates the v2 IMTU Subscription Journey Google Doc.

Every quantitative statement is generated from imtu_metrics.py, so the doc and
the HTML report cannot drift. Each figure carries its denominator, window,
query configuration and a link to the saved Amplitude chart that reproduces it.

v2 supersedes the first version: 15 of 48 figures did not survive rebuilding.
The corrections are listed in the executive summary and flagged inline.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from linkify_refs import LINK_MAP, linkify
from imtu_metrics import (DASHBOARD, CHART, ALL_GROUPS, GAPS, all_metrics,
                          EXPOSURE, CHECKOUT, BRACKETS, CANCEL_FLOW,
                          COUNTRY, TENURE, PLATFORM, VERSION, RENEWALS)

SCOPES = ["https://www.googleapis.com/auth/documents",
          "https://www.googleapis.com/auth/drive"]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"
RAW_BASE = "https://raw.githubusercontent.com/tanaka-idt/IDT-Claude/main/"

TITLE = "IMTU Subscription Journey — Investigation & Recommendations (v2, fully sourced)"

BY_KEY = {m["key"]: m for m in all_metrics()}


def v(key):
    """Value of a metric, for inline prose."""
    return BY_KEY[key]["value"]


BLOCKS = [
    ("h1", TITLE),
    ("cap", "Data-driven investigation · 31 August 2026 · DCS / IMTU · "
            "Amplitude project 650506 · 48 metrics, 46 saved charts, one dashboard"),

    # ------------------------------------------------------------------ 1 ----
    ("h2", "1. Executive summary"),
    ("p", "Defaulting the IMTU subscription toggle to ON is the largest behavioural lever in the "
          "product. It is also producing a subscription base that cancels at roughly a third within "
          "thirty days, concentrated on the days customers are charged."),
    ("p", "This version replaces the first. Every figure has been rebuilt as a saved Amplitude chart "
          "with a stated denominator, and 15 of 48 figures did not survive that rebuild. The direction "
          "of the analysis is unchanged; several magnitudes are not."),

    ("h3", "1.1 Corrections that matter"),
    ("b", "30-day cancellation is 30.57%, not 29.10%  —  the earlier denominator of 342,130 was close "
          "to the SUM of monthly unique purchasers rather than the count of distinct users over the "
          "window. Summing period uniques double-counts anyone active in more than one month. The "
          "correct base is 272,026 distinct purchasers."),
    ("b", "Checkout converts at 87.82%, not ~76%  —  the earlier figure was arithmetically impossible "
          "against its own platform split, since a grouped funnel's whole must lie between its parts."),
    ("b", "Android converts better than iOS, not worse  —  88.34% against 87.52%. The earlier version "
          "had the direction reversed."),
    ("b", "Post-cancellation substitution is 63.87%, not 45.3%  —  nearly two-thirds of cancellers buy "
          "a one-time top-up within 60 days, and a further 44.80% start a new subscription. Cancelling "
          "is mostly not rejection of the product."),
    ("b", "The 57.20% non-interaction figure is not reproducible  —  it was a screen-level claim that "
          "no single chart can produce. The user-level equivalent is 51.29%."),
    ("b", "Two property names in the earlier version do not exist  —  the toggle event carries "
          "default_state and new_state, not default_subscription_toggle; and app version is 'version', "
          "not 'version_name'."),

    ("h3", "1.2 What the evidence supports"),
    ("b", "The default is doing the work, not customer intent  —  default-ON attaches at " + v("exp_attach_default").split("·")[0].strip() +
          " against default-OFF at 5.53%, an 11.4× gap. Half of customers shown an ON default turn it "
          "off (49.23% per exposure), and 51.29% never engage with it at all."),
    ("b", "Attach has fallen for eleven consecutive weeks  —  from a peak of 45.49% in the week of "
          "22 June to 25.96% in the week of 24 August."),
    ("b", "The charge date is the strongest measured driver  —  weekly cadence cancels at 49.36% "
          "against monthly at 23.96%, and cadence is auto-derived from offer validity rather than chosen."),
    ("b", "The confirmation dialog is a mis-tap guard, not retention  —  99.14% of customers who tap "
          "Cancel go on to tap Yes; only 1,183 users in five months were deflected."),
    ("b", "Involuntary churn cannot be measured at all  —  100.0% of MTU payment failures carry no "
          "subscription flag, so a failed renewal is indistinguishable from a failed one-off top-up."),

    ("h3", "1.3 The judgement this asks for"),
    ("p", "Roughly half the subscription base behaves like people undoing something they did not "
          "choose. Before adding retention, the programme needs to know how much of its attach is "
          "consented — because a save flow applied to unintended subscriptions converts a consent "
          "problem into a revenue problem. The 44.80% who resubscribe voluntarily suggest the product "
          "is wanted; the mechanic is what is being rejected."),

    # ------------------------------------------------------------------ 2 ----
    ("h2", "2. Methodology and traceability standard"),
    ("p", "Dashboard containing every chart in this report: " + DASHBOARD),
    ("p", "Each of the 48 figures below is generated from a single canonical registry and carries four "
          "things: the value, the denominator, the date range, and a link to the saved Amplitude chart "
          "that reproduces it. Each chart's own description repeats its configuration, so a reviewer "
          "opening a chart cold can see what it measures without returning to this document."),

    ("h3", "2.1 Two standard windows"),
    ("b", "Cancellation cohort — 1 March to 1 August 2026  —  unique users, shared step-1 denominator "
          "of 272,026 distinct subscription purchasers. Every cancellation and segment chart uses this "
          "identical shape so rates are directly comparable."),
    ("b", "Exposure and checkout — 1 to 29 August 2026  —  note this is 29 days, not a calendar month. "
          "Figures described as “August” elsewhere may differ by 2–3% for that reason alone."),

    ("h3", "2.2 Reading conventions"),
    ("b", "Confirmed  —  reproduced within rounding of the earlier version."),
    ("b", "Superseded  —  the earlier figure did not survive rebuilding; the figure here is the correct one."),
    ("b", "New  —  not present in the earlier version."),
    ("b", "Derived  —  calculated across more than one chart. Two figures are marked this way: the "
          "opt-out and opt-in rates, whose numerators and denominators come from different charts."),

    ("h3", "2.3 Four measurement traps this report avoids, and reviewers should too"),
    ("b", "Events are not customers  —  order-success events fire about 2.21 times per converting user, "
          "and toggle taps include 39,628 that end where they began. Never read an event count as a "
          "customer count."),
    ("b", "Grouped funnels return unlabelled series  —  so every segment figure here is backed by an "
          "explicitly filtered chart. Rank-order inference was tested against filtered cohorts and "
          "found invalid for user-scoped properties."),
    ("b", "Some segments do not partition the base  —  tenure cohorts sum to 114% of the base and "
          "version cohorts to 119%, because customers change label and upgrade mid-window. Do not sum "
          "their denominators. Platform is the only clean partition tested, at +0.2%."),
    ("b", "Right-censoring  —  customers late in a cohort window have not had the full conversion "
          "window in which to act, so bracket and 60-day rates are floors rather than point estimates. "
          "Right-censoring is what produced the 12.7% figure that circulated before this work."),

    # ------------------------------------------------------------------ 3 ----
    ("h2", "3. Release and targeting timeline"),
    ("p", "From Jira (DCS, DTCBE, CRMC). Two standing caveats apply. Every fixVersion on every "
          "subscription ticket carries released=false — the flag is unmaintained project-wide — so all "
          "dates are Jira resolution or build dates, which precede store release by an estimated three "
          "weeks. And READY-IN-FEAT means merged to a feature branch, not shipped, even though Jira "
          "files it under Done."),
    ("table", "TIMELINE"),
    ("p", "Only one post-launch targeting change has actually completed: smart-hide (DCS-4854). "
          "Neither variant the brief assumes is limiting exposure has shipped — DCS-5289 is QA "
          "Available and the entire V2 epic DCS-5297 is To Do, including its Amplitude events "
          "(DCS-5300, DCS-5301) and its A/B harness (DCS-5303)."),

    ("h3", "3.1 Intended versus implemented"),
    ("p", "The V1 targeting predicate has two incompatible readings, and this is the most consequential "
          "open discrepancy because it determines what DCS-5289 actually replaces. The internal "
          "core-logic reference describes two independent gates — duplicate, then a 3-or-more cap. "
          "DCS-5289 describes the outgoing rule as a single conjunction: OFF only if the user has 3 or "
          "more active subscriptions AND the purchase is for the same offer to the same recipient. "
          "Either V1 shipped differently from its specification, or DCS-5289 is scoped against a false "
          "premise. Resolve before it leaves QA."),
    ("p", "Three suppression rules were added at implementation time (DCS-4854) and never written back "
          "into the definition ticket (DCS-4781). They were, however, tested — QA enumerated all eight "
          "rules with individual verdicts, and the rule that failed was the one that had diverged."),

    ("cap", "Diagram 2 — Every variant and targeting change, by actual shipping status"),
    ("table", "IMG_VARIANTS"),

    # ------------------------------------------------------------------ 4 ----
    ("h2", "4. Behavioural analysis"),
    ("h3", "4.1 Offer exposure and toggle interaction"),
    ("p", "The exposure surface is MTUOrderScr, which carries default_subscription_toggle recording the "
          "state actually shown. Nearly one screen in five records no toggle state at all, and that "
          "untagged arm converts at 7.01% — between the ON arm and the OFF arm, so it cannot be "
          "assumed to be either."),
    ("table", "M_EXPOSURE"),
    ("p", "HYPOTHESIS, not measured: the 11.4× attach gap between default-ON and default-OFF is "
          "observational, not causal. The default-OFF population is defined by already owning "
          "subscriptions, so it is selected on the outcome. The randomised A/B property is unusable "
          "after general availability — arm B carries 143 users."),

    ("h3", "4.2 Checkout and confirmation"),
    ("p", "Checkout is healthy and the subscription mechanic does not measurably harm it. The two "
          "platforms sit within 0.82 percentage points and subscription and one-time orders within "
          "0.89 at the payment step."),
    ("table", "M_CHECKOUT"),

    ("cap", "Diagram 1 — The current journey as measured. Dashed steps exist but emit no event"),
    ("table", "IMG_CURRENT"),

    # ------------------------------------------------------------------ 5 ----
    ("h2", "5. Variant comparison"),
    ("p", "The comparison the brief asks for is not currently available, for a specific and fixable "
          "reason: neither limiting variant is in production, and the randomised tagging that would "
          "support a causal read stopped in July."),
    ("table", "VARIANTS"),
    ("p", "One genuine opportunity remains. A_B_subscription_toggle_test_id is balanced and populated "
          "for May and June 2026 at roughly 35,000 and 58,000 events per arm. That is the only causal "
          "readout the programme has, and it has never been analysed. A taxonomy defect will mislead "
          "anyone who tries: two A/B properties coexist undeleted and the broken one — which recorded "
          "feature-flag state rather than arm assignment (DCS-4369) — is still being written and is now "
          "the only populated one."),

    # ------------------------------------------------------------------ 6 ----
    ("h2", "6. Cancellation findings"),
    ("p", "Time-to-cancel is bimodal: an immediate-regret spike inside the first hour, a quiet trough "
          "across days one to four, then a larger mass locked to the renewal charge."),
    ("table", "M_BRACKETS"),
    ("p", "The immediate cluster is undo, not churn. The median 24-hour canceller acts in 178 seconds — "
          "under three minutes is not deliberation, it is someone discovering a subscription on the "
          "confirmation screen or receipt and reversing it. No reason is captured, so nothing is learned."),
    ("p", "HYPOTHESIS, not measured: whether that cluster is genuine regret or promotional "
          "capture-then-cancel cannot currently be distinguished. DCS-5293 raises exactly this and asks "
          "the team to confirm whether a promo-created subscription can even be identified — so today "
          "it cannot."),

    ("h3", "6.1 The cancellation flow itself, and what follows it"),
    ("table", "M_CANCELFLOW"),
    ("p", "The two post-cancellation figures overlap and must not be summed — a customer who both buys "
          "a one-time top-up and resubscribes appears in both. Both are right-censored and therefore floors."),

    ("cap", "Diagram 3 — Immediate cancellation, within 24 hours"),
    ("table", "IMG_IMMEDIATE"),
    ("cap", "Diagram 4 — Delayed cancellation, by cadence"),
    ("table", "IMG_DELAYED"),

    ("h3", "6.2 Ranked drivers"),
    ("table", "DRIVERS"),

    ("h3", "6.3 By recipient country"),
    ("p", "Nicaragua and Ethiopia, both quoted in the earlier version, are not among the top 8 corridors "
          "by subscription-purchaser volume on this window. El Salvador and Honduras are effectively "
          "tied at 0.09 percentage points apart; neither should be described as the worst market."),
    ("table", "M_COUNTRY"),

    ("h3", "6.4 By customer tenure"),
    ("p", "HYPOTHESIS, not measured: two explanations fit the tenure gradient equally. Either VIPs "
          "accumulate redundant default-ON subscriptions and cancel them, or VIPs are simply more able "
          "to find the cancel control, in which case low-tenure customers' lower rate reflects "
          "non-detection rather than satisfaction. Nothing in current tracking separates them."),
    ("table", "M_TENURE"),

    ("h3", "6.5 By platform and app version"),
    ("table", "M_PLATFORM"),
    ("p", "The version spread is 14.2 percentage points — wider than the entire Android/iOS gap. That "
          "is why no single-version comparison should be used to claim a build regression: a comparator "
          "can be chosen to support almost any conclusion."),
    ("table", "M_VERSION"),

    # ------------------------------------------------------------------ 7 ----
    ("h2", "7. Renewals, payments, and the limits of what is observable"),
    ("p", "This is the largest blind spot in the product. A taxonomy search across six renewal, "
          "billing, retry and dunning concepts returns no renewal event of any kind. A partial view "
          "opened on 10 August 2026, and it is both recent and impure."),
    ("table", "M_RENEWALS"),
    ("p", "Two consequences follow. Renewal survival cannot be computed — only twenty days of "
          "renewal-side data exist, less than one monthly billing cycle. And involuntary churn is "
          "invisible: because the subscription flag is never set on failures, a failed renewal cannot "
          "be told apart from a failed one-off top-up. Voluntary churn is measurable; involuntary "
          "churn is not measurable at all."),
    ("p", "Note also that a failed renewal cannot itself produce a cancellation: DTCBE-623 removed "
          "auto-cancellation for all payment scenarios in May 2024, after DTCBE-444's introduction of "
          "it lost roughly 30,000 subscriptions. Failing subscriptions simply persist, and the customer "
          "is told nothing on any channel (CRMC-3299, in backlog since 2024)."),

    # ------------------------------------------------------------------ 8 ----
    ("h2", "8. Tracking gaps"),
    ("p", "Each row is a missing event or property and the specific question it blocks."),
    ("table", "GAPS"),

    # ------------------------------------------------------------------ 9 ----
    ("h2", "9. Recommended future-state journey"),
    ("p", "Three changes: refuse to create a subscription without a rendered toggle; stop deriving "
          "weekly cadence from short offer validity; and offer one genuine alternative at cancellation "
          "without obstructing the cancel path."),
    ("cap", "Diagram 5 — Recommended future state"),
    ("table", "IMG_FUTURE"),
    ("p", "The sharpest risk sits on the third change. A large share of the cancellation pool is people "
          "undoing a subscription they never chose; deflecting them into a skip or a discount re-banks "
          "revenue they never authorised. Any retention readout must be split by whether the "
          "subscription was toggle-created — which needs the cancellation-reason property that does "
          "not yet exist."),

    # ----------------------------------------------------------------- 10 ----
    ("h2", "10. Prioritised recommendations"),
    ("table", "RECS"),
    ("h3", "10.1 Explicitly not recommended"),
    ("p", "Opening a regression ticket on any single app version: the spread across versions is 14.2 "
          "percentage points and a comparator can be chosen to prove almost anything. And attributing "
          "the Stripe request-rate spikes (DCS-5252) to the default-ON toggle: eleven same-second "
          "timers cannot mechanically produce the observed rate."),

    # ----------------------------------------------------------------- 11 ----
    ("h2", "11. Success metrics and experimentation"),
    ("table", "METRICS"),
    ("p", "Guardrails matter more than the outcome metric here. A save flow can improve its own numbers "
          "while damaging the business, so watch support contacts per thousand cancellations, "
          "dispute and chargeback rate on subscriptions, and 30-day survival among saved customers. A "
          "customer retained into a subscription they did not want is a future dispute, not a win."),
    ("p", "Sequence the experiments rather than running them together. The cadence default changes the "
          "composition of the cancelling population and would otherwise confound everything downstream; "
          "run it first, then the permission gate and reason capture, then intervention content. "
          "Randomise at customer level and tag every event with the variant including post-GA, because "
          "the current instrumentation loses variant tags exactly when a result would matter."),

    # ----------------------------------------------------------------- 12 ----
    ("h2", "12. Full traceability index"),
    ("p", "Every figure in this document, with its denominator, window, query configuration and saved "
          "chart. Dashboard: " + DASHBOARD),
    ("table", "TRACE"),

    # ----------------------------------------------------------------- 13 ----
    ("h2", "13. Limitations and additional data required"),
    ("b", "No confidence intervals anywhere  —  the 0.82-point platform gap and the 19.8-point tenure "
          "gap are reported at equal weight. At these sample sizes the second is clearly meaningful and "
          "the first probably is not, but nothing here distinguishes them formally."),
    ("b", "Right-censoring  —  bracket rates and the two 60-day post-cancellation rates are floors. "
          "Customers late in each cohort window have not had the full window in which to act."),
    ("b", "Funnel arms are not clean partitions  —  a customer who saw order screens in more than one "
          "default state appears in more than one arm, so arm counts sum to more than the distinct base."),
    ("b", "Two figures are derived across charts  —  the opt-out and opt-in rates take their numerators "
          "from the toggle-tap chart and their denominators from the exposure chart. They are not "
          "reproducible from a single chart and are labelled accordingly."),
    ("b", "Funnel group labels are inferred, not read  —  for the attach-by-default-state chart the API "
          "returns unlabelled series, so arm assignment rests on descending volume. Every other segment "
          "figure avoids this by using explicitly filtered charts."),
    ("b", "No production release dates exist in Jira  —  the timeline is built on resolution and build "
          "dates with an estimated three-week lag to store release."),
    ("b", "The 28.4% failing-subscription pool is not observable in Amplitude  —  it came from an April "
          "2026 database analysis and cannot be refreshed or trended without warehouse access."),

    ("h3", "13.1 Data required to close the remaining questions"),
    ("b", "Subly or IDTPay billing records  —  to test any link between failed renewals and "
          "cancellation. Not answerable in Amplitude at all."),
    ("b", "Warehouse access  —  to compute repeat-versus-new recipient status. The phone number is on "
          "both the order and cancel events but cannot be joined in Amplitude."),
    ("b", "A decision record for the V1 experiment  —  none exists anywhere in Jira. No ticket records "
          "a decision to conclude the test and go to 100%."),

    ("h2", "14. Source note"),
    ("p", "Amplitude org BOSS (127967), project 650506 “BR app Prod”, queried 30–31 August 2026. All "
          "46 charts are saved and collected on one dashboard: " + DASHBOARD + " . Jira projects DCS, "
          "DTCBE and CRMC at idtjira.atlassian.net. A companion HTML report carries identical content "
          "generated from the same metric registry."),
]

# ---------------------------------------------------------------- tables ----

TIMELINE = [
    ["Date", "Ticket", "Change", "Status"],
    ["2025-12-29", "DCS-3789", "A/B config for the toggle. Two arms, “50k users (TDB)”. No allocation, metric, MDE or stop rule. Closed with no QA by explicit waiver.", "Done"],
    ["2026-01-09", "DCS-3818", "V1 epic “Subscription Toggle and Frequency”. 52 children. Never closed.", "In Progress"],
    ["2026-04-01", "DCS-4369", "Bug: the A/B property reported feature-flag state rather than arm assignment, and tagged unenrolled users. Still writing today.", "Fixed"],
    ["2026-04-21", "DCS-4428", "Duplicate-subscription warning removed.", "Reversed Aug"],
    ["2026-07-08", "DCS-4854", "Smart-hide: the toggle stops being shown after 3 off-toggles. The only completed post-launch targeting change.", "LIVE"],
    ["2026-07-16", "DCS-4983", "Renewal reminder moved to charge date minus 2 days.", "LIVE"],
    ["2026-08-13", "DCS-5224", "Duplicate warning re-added, reversing DCS-4428 four months later.", "LIVE"],
    ["2026-08-26", "DCS-5289", "Default OFF when the user has ≥1 active subscription.", "NOT LIVE"],
    ["2026-08-28", "DCS-5277", "Consent-defect fix (insurance path). QA task DCS-5310 closed “Won't fix” 33 seconds after creation.", "Feature branch"],
]

VARIANTS = [
    ["Comparison", "Status", "Why"],
    ["DCS-5289 variant vs control", "IMPOSSIBLE", "The variant is not in production. There is nothing to measure."],
    ["Randomised A/B arms, post-GA", "IMPOSSIBLE", "Variant tagging effectively stopped in July. Arm B carries 143 users — no power."],
    ["Randomised A/B arms, May–Jun", "AVAILABLE, NOT RUN", "Balanced and populated at ~35k (May) and ~58k (Jun) events per arm. The only causal readout the programme has."],
    ["Default ON vs OFF, observational", "CONFOUNDED", "62.90% vs 5.53% attach. Selected on the outcome — the OFF arm is defined by prior subscription ownership."],
    ["Platform / version / country / cadence / tenure", "AVAILABLE", "All segmentable today, each with its own saved chart. Cadence is the one that matters."],
]

DRIVERS = [
    ["Driver", "Verdict", "Evidence", "Chart"],
    ["Renewal cadence", "SUPPORTS — strongest", "Weekly 49.36% (34,975/70,861) vs monthly 23.96% (48,161/201,009) at 30 days. Cadence is auto-derived from offer validity, not chosen.", "a75n2jgf"],
    ["Customer tenure", "SUPPORTS — confounded", "vip 43.08% down to one_trx 23.29%. Two readings fit equally; nothing separates them.", "6haohove"],
    ["Recipient country", "SUPPORTS", "El Salvador 39.57% down to Nigeria 17.88% across the top 8 corridors.", "2j37y76s"],
    ["Platform", "SUPPORTS — small", "Android 33.61% vs iOS 29.11%. The only dimension that cleanly partitions the base.", "9ibdyo1j"],
    ["App version", "ASSOCIATION ONLY", "23.03% to 37.20% across versions — a 14.2pp spread. Confounded with adopter mix and rollout timing.", "iw7zip5m"],
    ["Toggle default state", "ASSOCIATION ONLY", "Not causal — the default-OFF arm is defined by prior subscription ownership.", "qf6uouru"],
    ["Renewal reminders", "TIMING, NOT RATE", "Reminder receipt is unobservable — no first-party event exists for the DCS-4983 reminder.", ""],
    ["Failed payments", "CANNOT ANSWER", "100.0% of MTU payment failures carry no subscription flag. And by design a failed renewal cannot cause cancellation (DTCBE-623).", "owzed305"],
    ["Promotions", "CANNOT ANSWER", "Whether a subscription was promo-created is not persisted (DCS-5293).", ""],
    ["Payment method", "CANNOT ANSWER", "No payment property exists on any MTU order or cancel event.", ""],
    ["Recipient (new vs repeat)", "CANNOT ANSWER", "The phone number is on both events but cannot be joined in Amplitude. Warehouse only.", ""],
]

RECS = [
    ["#", "Recommendation", "Evidence", "Impact / risk", "Effort", "Success metric", "Experiment"],
    ["P0 · R1", "Size and remediate the consent population, and re-open QA",
     "DCS-5277 100% reproducible; fix on a feature branch with empty fixVersions; QA task DCS-5310 closed “Won't fix” in 33 s",
     "Bounds a live regulatory exposure. Risk: remediation contact may surface subscriptions customers had not noticed — sequence with Legal",
     "S for QA; M for the cohort query", "A dated count of affected subscriptions and a QA pass on a production build", "None — verification, not experimentation"],
    ["P0 · R2", "Test whether the consent failure mode recurs on the smart-hide path",
     "DCS-5277's mechanism is toggle ON in state, toggle not rendered, subscription created. DCS-4854 hides the toggle by design. Never tested.",
     "Potentially a second, much larger consent population — smart-hide is live to everyone",
     "S", "Completed orders with a subscription and no preceding toggle tap in session", "Not applicable — a test case"],
    ["P0 · R3", "Instrument the subscription flag on MarketingTxnFailed",
     "100.0% unset across 381,167 MTU failure events (chart owzed305). The pipeline already sets it on successes.",
     "Makes involuntary churn measurable for the first time. One property.",
     "S", "Failed renewals attributable, and a dunning baseline that can be trended", "None — instrumentation"],
    ["P0 · R4", "Run the May–June randomised readout before DCS-5289 ships",
     "A_B_subscription_toggle_test_id balanced and populated, ~35k / ~58k events per arm",
     "Converts the central claim from observational to causal. Risk: two concurrent tests may overlap",
     "S — queries only", "Arm-level attach AND 30-day cancellation on unique users", "Ship DCS-5289 randomised, not globally"],
    ["P1 · R5", "Stop defaulting weekly cadence from 7-day offer validity",
     "Weekly 49.36% vs monthly 23.96% at 30 days (chart a75n2jgf); explicit choosers prefer 90-day",
     "The largest available reduction in early cancellation. Risk: fewer charges per subscription — do not assume the churn saving nets positive",
     "M — the backend lever exists as DCS-5290", "Fee revenue per purchaser per 90 days, not attach rate", "Three arms on 7-day-validity offers: default weekly, default monthly, no default"],
    ["P1 · R6", "Add cancellation-reason capture with an explicit “I didn't mean to subscribe”",
     "No cancel_reason property exists on any cancel event; 99.14% of Cancel-tappers complete (chart 0k93sx6m)",
     "The only way to split the cancellation pool into unintended versus considered — which every retention decision depends on",
     "S–M", "Reason distribution with skip rate reported alongside", "None — instrumentation, but gate the retention A/B on it"],
    ["P1 · R7", "Build a skip or defer path instead of only cancel",
     "Only active/cancelled states exist; the dialog deflects 2.63% of taps; 63.87% substitute back to one-time top-ups",
     "Converts timing-driven cancellations into deferrals. Risk: deflecting unintended subscriptions re-banks unauthorised revenue",
     "M — a launch_at bump on the existing timer row", "90-day revenue per cancel-flow entrant, not deflection alone", "Ship as a fifth variant inside the DCS-5257/5258 retention A/B"],
    ["P2 · R8", "Ship the unblocked half of payment-method change",
     "DCS-4461 marks Scenario 1 feasible with current capabilities; both stories High and unassigned under a Low-priority epic",
     "Removes an involuntary-churn path — an expiring card currently forces cancellation",
     "M", "In-app payment-method changes completed; reduction in cancel-and-recreate", "None — instrument before and after"],
    ["P2 · R9", "Fix the two taxonomy defects and the diagnostic gap",
     "gp:imtu_cls_label carries both 'none' and '(none)' 7.8pp apart; the broken A/B property is still writing; 37.27% of failures carry the bare value 'failed'",
     "Prevents the next analyst reaching a confident wrong conclusion",
     "S", "Single-valued buckets; failure reasons diagnostic", "None"],
    ["P2 · R10", "Scope the stacking guardrail per recipient, not per account",
     "A sender supporting three recipients has three legitimate subscriptions; a ≥1-per-account rule defaults the second and third OFF",
     "Raise on DCS-5289 before it leaves QA",
     "S — a spec change", "Attach retained on distinct-recipient purchases", "Fold into the DCS-5289 randomisation"],
]

METRICS_TBL = [
    ["Metric", "Definition", "Baseline today", "Why this one"],
    ["Save rate", "Customers reaching the intervention who do not cancel in that session.", "No intervention exists", "The headline. Requires an exposure event."],
    ["Cancel completion rate", "Cancel-flow entrants who complete.", "80.65% end-to-end; 99.14% Cancel→Yes", "Guardrail against building obstruction rather than persuasion."],
    ["Reason distribution", "Share of cancellations by captured reason, with skip rate alongside.", "Unobtainable — no property", "Splits unintended from considered churn."],
    ["Week-one cancellation", "Cancellations within 7 days of creation.", "13.16%", "Direct measure of whether cadence and disclosure fixes worked."],
    ["30-day cancellation", "Cancellations within 30 days.", "30.57%", "The programme's headline health metric."],
    ["Weekly-cadence share", "Share of new subscriptions created at a 7-day interval.", "~26% of the subscription base", "Leading indicator for the cadence fix."],
    ["Attach rate", "Subscription share of tagged order completions.", "25.96% (week of 24 Aug)", "Falling for 11 weeks. Do NOT use as the success metric for retention work."],
    ["Revenue per purchaser per 90 days", "Fee revenue divided by distinct purchasers.", "Not yet computed", "The metric that survives DCS-5289; attach rate does not."],
    ["Involuntary churn rate", "Subscriptions lost to failed payment.", "Unmeasurable", "Blocked on R3. Currently invisible."],
    ["Support contacts per 1,000 cancellations", "Cancellation-related contacts, normalised.", "No baseline", "Friction guardrail."],
    ["Dispute rate on subscriptions", "Disputes over renewal charges.", "No baseline", "Consent guardrail, and the one most likely to attract regulatory attention."],
]

GAPS_TBL = [["Missing", "What is absent", "Question it blocks", "Status"]] + [list(g) for g in GAPS]


def metric_table(metrics, show_status=True):
    head = ["Finding", "Value", "Denominator", "Window", "Configuration", "Chart"]
    if show_status:
        head.insert(2, "Status")
    rows = [head]
    for m in metrics:
        r = [m["label"], m["value"], m["denom"], m["window"], m["cfg"], m["chart"]]
        if show_status:
            r.insert(2, m["status"].upper())
        rows.append(r)
    return rows


def trace_table():
    rows = [["Group", "Finding", "Value", "Denominator", "Window", "Chart", "Notes"]]
    for gname, group in ALL_GROUPS:
        for m in group:
            rows.append([gname, m["label"], m["value"], m["denom"], m["window"],
                         m["chart"], m["note"] or "—"])
    return rows


TABLES = [
    ("TIMELINE", TIMELINE),
    ("VARIANTS", VARIANTS),
    ("M_EXPOSURE", metric_table(EXPOSURE)),
    ("M_CHECKOUT", metric_table(CHECKOUT)),
    ("M_BRACKETS", metric_table(BRACKETS)),
    ("M_CANCELFLOW", metric_table(CANCEL_FLOW)),
    ("M_COUNTRY", metric_table(COUNTRY)),
    ("M_TENURE", metric_table(TENURE)),
    ("M_PLATFORM", metric_table(PLATFORM)),
    ("M_VERSION", metric_table(VERSION)),
    ("M_RENEWALS", metric_table(RENEWALS)),
    ("DRIVERS", DRIVERS),
    ("GAPS", GAPS_TBL),
    ("RECS", RECS),
    ("METRICS", METRICS_TBL),
    ("TRACE", trace_table()),
]

IMAGES = [
    ("IMG_VARIANTS", "imtu_journey_2_variants.png", 468.0, 2405, 2272),
    ("IMG_CURRENT", "imtu_journey_1_current.png", 468.0, 2405, 2508),
    ("IMG_IMMEDIATE", "imtu_journey_3_immediate.png", 468.0, 2142, 1918),
    ("IMG_DELAYED", "imtu_journey_4_delayed.png", 468.0, 2273, 2036),
    ("IMG_FUTURE", "imtu_journey_5_future.png", 468.0, 2405, 2508),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "cap": "NORMAL_TEXT"}

STATUS_COLOR = {
    "CONFIRMED": (0.05, 0.48, 0.42), "SUPERSEDED": (0.70, 0.15, 0.12),
    "NEW": (0.25, 0.32, 0.62), "GAP": (0.45, 0.42, 0.50),
    "IMPOSSIBLE": (0.70, 0.15, 0.12), "CONFOUNDED": (0.65, 0.35, 0.04),
    "AVAILABLE": (0.05, 0.48, 0.42), "AVAILABLE, NOT RUN": (0.25, 0.32, 0.62),
    "LIVE": (0.05, 0.48, 0.42), "NOT LIVE": (0.70, 0.15, 0.12),
    "Feature branch": (0.65, 0.35, 0.04), "Reversed Aug": (0.65, 0.35, 0.04),
}
CHART_IDS = {m["chart"] for m in all_metrics()} | {r[3] for r in DRIVERS[1:] if r[3]}


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
        elif c == 0 and txt[:2] in ("P0", "P1", "P2"):
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
        print(f"  image {marker}: {'ok' if ok else 'FAILED'}")

    extra = {cid: CHART + cid for cid in CHART_IDS}
    extra["o1jhxth9"] = DASHBOARD
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
