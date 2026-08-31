#!/usr/bin/env python3
"""
Canonical metric registry for the IMTU Subscription Journey report.

Every figure that appears in either deliverable is defined here exactly once,
with its value, denominator, window, query configuration and the saved Amplitude
chart that reproduces it. Both the Google Doc and the HTML report are generated
from this file, so the two cannot drift apart.

status:
  confirmed  - reproduced within rounding of the previous version of the report
  superseded - the previous figure did not survive rebuilding; this is the correct one
  new        - not present in the previous version
  gap        - an instrumentation finding: the metric cannot be measured

Windows used throughout:
  COHORT  1 Mar - 1 Aug 2026, unique users, shared denominator 272,026
  AUG     1-29 Aug 2026 (29 days, not a calendar month)
  RENEW   1 Jun - 30 Aug 2026
"""

DASHBOARD = "https://app.amplitude.com/analytics/BOSS/dashboard/o1jhxth9"
CHART = "https://app.amplitude.com/analytics/BOSS/chart/"

COHORT = "1 Mar – 1 Aug 2026"
AUG = "1–29 Aug 2026"
RENEW = "1 Jun – 30 Aug 2026"

BASE = "272,026 distinct subscription purchasers"

FUNNEL_CFG = ("Ordered funnel MTUOrderCompleteBtn (is_subscription = true) → "
              "MTUEditSubscriptionCancelSuccess · 30-day conversion window · unique users")


def M(key, label, value, denom, window, cfg, chart, status, note=""):
    return dict(key=key, label=label, value=value, denom=denom, window=window,
                cfg=cfg, chart=chart, status=status, note=note)


# ---------------------------------------------------------------- exposure ----
EXPOSURE = [
    M("exp_screens", "Order screens by toggle default state",
      "ON 46.93% · OFF 34.12% · untagged 18.96%",
      "1,125,007 order-screen EVENTS (527,930 / 383,834 / 213,243)", AUG,
      "MTUOrderScr · event_totals · group by default_subscription_toggle", "59nqhb2i",
      "superseded",
      "Previous version said 1,152,462 events. The untagged share is robust either way; "
      "the count differs because this window is 29 days."),

    M("exp_attach_default", "Subscription attach by toggle default state",
      "default-ON 62.90% · default-OFF 5.53% · untagged 7.01%",
      "per-arm step-1 unique users: 214,006 / 70,032 / 60,613", AUG,
      "Ordered funnel MTUOrderScr → MTUOrderCompleteBtn (is_subscription = true) · 1h window · "
      "unique users · grouped on default_subscription_toggle", "qf6uouru", "confirmed",
      "ASSUMPTION: the API returns funnel group rows unlabelled, so arm assignment is inferred "
      "from descending step-1 volume. Directionally identical to the previous version."),

    M("exp_taps", "Toggle taps by starting and resulting state",
      "opt-out 259,895 · opt-in 25,007 · no-change 39,628",
      "324,530 toggle-tap EVENTS", AUG,
      "MTUSubscriptionToggleTap · event_totals · group by default_state AND new_state", "vpe29q4t",
      "new",
      "TAXONOMY CORRECTION: this event does not carry default_subscription_toggle; it carries "
      "default_state and new_state. 39,628 taps end where they began."),

    M("exp_optout", "Opt-out rate per default-ON exposure",
      "49.23%", "259,895 opt-out taps ÷ 527,930 default-ON order screens", AUG,
      "DERIVED across two charts: numerator from vpe29q4t, denominator from 59nqhb2i", "vpe29q4t",
      "confirmed", "CALCULATED FROM TWO SOURCES — not self-contained in one chart."),

    M("exp_optin", "Opt-in rate per default-OFF exposure",
      "6.51%", "25,007 opt-in taps ÷ 383,834 default-OFF order screens", AUG,
      "DERIVED across two charts: numerator from vpe29q4t, denominator from 59nqhb2i", "vpe29q4t",
      "confirmed", "CALCULATED FROM TWO SOURCES — not self-contained in one chart."),

    M("exp_nointeract", "Default-ON users who never touch the toggle",
      "51.29%", "115,760 of 225,685 default-ON exposed unique users", AUG,
      "Ordered funnel MTUOrderScr (default = on) → MTUSubscriptionToggleTap (default_state = on) · "
      "1h window · unique users", "fqiwoqr8", "superseded",
      "The previous 57.20% was a SCREEN-level claim and is not reproducible from any single chart. "
      "This is the user-level equivalent."),

    M("exp_attach_weekly", "Subscription attach rate by week",
      "peak 45.49% (week of 22 Jun) → 25.96% (week of 24 Aug)",
      "tagged MTUOrderCompleteBtn events per week", "18 May – 30 Aug 2026",
      "Two events, formula TOTALS(A)/TOTALS(B): A = is_subscription true, B = is_subscription set",
      "tyvyvyge", "confirmed", "Eleven consecutive weekly declines. Reproduced to the decimal."),

    M("exp_purchasers", "Subscription purchasers per month",
      "Mar 2,252 · Apr 5,435 · May 15,484 · Jun 127,755 · Jul 181,283 · Aug 147,093",
      "unique users per month", "Mar – Aug 2026",
      "MTUOrderCompleteBtn (is_subscription = true) · unique_users · monthly", "gfkcqj5t", "new",
      "DO NOT SUM these months. The distinct total across Mar–Jul is 272,026, not the 332,209 the "
      "months add to. Summing period uniques is what produced the error corrected below."),
]

# ---------------------------------------------------------------- checkout ----
CHECKOUT = [
    M("chk_funnel", "IMTU checkout funnel, end to end",
      "87.82%", "302,686 of 344,651 distinct users reaching the order screen", AUG,
      "Ordered funnel MTUOrderScr → MTUOrderCompleteBtn → MTUOrderStatusSuccessScr · 1h · unique users",
      "movsvyvz", "superseded",
      "The previous version reported ~76%, which was arithmetically impossible against its own "
      "platform split — a grouped funnel's whole must lie between its parts."),

    M("chk_platform", "Checkout funnel by platform",
      "Android 88.34% · iOS 87.52%",
      "Android 100,395 / 113,641 · iOS 202,832 / 231,758", AUG,
      "Same 3-step funnel · group by platform at USER scope (event scope returns 100% unset)",
      "vqml240x", "superseded",
      "DIRECTION REVERSED. The previous version had iOS ahead; Android in fact leads by 0.82pp. "
      "Platform groups over-count the base by 0.22%."),

    M("chk_subvsone", "Payment step: subscription vs one-time",
      "one-time 94.16% · subscription 93.26%",
      "one-time 208,461 / 221,394 · subscription 133,168 / 142,785", AUG,
      "2-step funnel MTUOrderCompleteBtn → MTUOrderStatusSuccessScr · unique users · split on is_subscription",
      "wb1cnq01", "superseded",
      "A 0.89pp gap, not the 0.53pp previously reported. LIMITATION: the full 3-step funnel cannot "
      "be split this way because is_subscription is not carried on MTUOrderScr, so read this as a "
      "payment-step comparison only."),

    M("chk_outcomes", "Order outcomes",
      "success 82.40% · failed 16.11% · queued 1.50%",
      "812,567 terminal-state EVENTS (669,527 / 130,882 / 12,158)", AUG,
      "event_totals of MTUOrderStatusSuccessScr, FailedScr and QueuedScr", "bw0lhbha", "superseded",
      "Previous version reported 686,314 / 133,778 / 12,308 from a slightly wider window. Success "
      "fires roughly 2.21× per converting user, so these are not customer counts."),

    M("chk_failreasons", "Order failure reasons",
      "the bare value 'failed' is the largest bucket at 37.27%",
      "48,780 of 130,882 failure events", AUG,
      "MTUOrderStatusFailedScr · event_totals · group by failed_reason", "5d718501", "new",
      "Over a third of failures carry no diagnostic information at all. The 12 returned values leave "
      "1,435 events (1.10%) ungrouped."),
]

# ------------------------------------------------------------ cancellation ----
BRACKETS = [
    M("br_24h", "Cancellation within 24 hours", "7.91%", "21,510 of " + BASE, COHORT,
      FUNNEL_CFG + " · 24-hour window", "42u1rqz8", "superseded", "Median 178 seconds."),
    M("br_3d", "Cancellation within 3 days", "9.25%", "25,164 of " + BASE, COHORT,
      FUNNEL_CFG + " · 3-day window", "m65f9ue3", "superseded", "Median 488 seconds."),
    M("br_7d", "Cancellation within 7 days", "13.16%", "35,800 of " + BASE, COHORT,
      FUNNEL_CFG + " · 7-day window", "syiky5x9", "superseded", "Median 19.9 hours."),
    M("br_14d", "Cancellation within 14 days", "19.17%", "52,136 of " + BASE, COHORT,
      FUNNEL_CFG + " · 14-day window", "2kxvu6t6", "superseded", "Median 6.0 days."),
    M("br_30d", "Cancellation within 30 days", "30.57%", "83,148 of " + BASE, COHORT,
      FUNNEL_CFG + " · 30-day window", "7200e6l9", "superseded",
      "Median 13.9 days. Supersedes both the 12.7% long in circulation (right-censored) and the "
      "29.10% in the previous version (inflated denominator)."),
]

CANCEL_FLOW = [
    M("cf_funnel", "Cancel-flow funnel",
      "99.14% of Cancel-tappers go on to tap Yes; 80.65% end to end",
      "135,848 of 137,031 tap Yes · 135,688 of 168,233 complete", COHORT,
      "Ordered funnel MTUEditSubscriptionScr → CancelBtn → CancelYesBtn → CancelSuccess · unique users",
      "0k93sx6m", "new",
      "Only 1,183 users are deflected by the confirmation dialog. It is a mis-tap guard, not retention."),

    M("cf_dialog", "Confirmation dialog: No vs Yes",
      "2.63% of dialog responses are No",
      "7,837 No of 298,064 total dialog response EVENTS", COHORT,
      "event_totals of MTUEditSubscriptionCancelNoBtn vs CancelYesBtn", "vrsoq9zk", "confirmed",
      "Per-tap, not per-customer: 290,227 Yes events against 135,848 unique Yes users."),

    M("cf_cadence", "30-day cancellation by renewal cadence",
      "weekly 49.36% · monthly 23.96%",
      "weekly 34,975 / 70,861 · monthly 48,161 / 201,009", COHORT,
      FUNNEL_CFG + " · group by recurrent_unit on step 1", "a75n2jgf", "confirmed",
      "The strongest measured driver. recurrent_unit is only reliable here because step 1 is already "
      "filtered to subscriptions."),

    M("cf_substitute", "Return to one-time top-ups after cancelling",
      "63.87%", "86,805 of 135,903 successful cancellers", COHORT,
      "Ordered funnel MTUEditSubscriptionCancelSuccess → MTUOrderCompleteBtn (is_subscription = false) · "
      "60-day window · unique users", "fndtbvdu", "superseded",
      "Median 10.1 days. Supersedes 45.3%. Right-censored, so a floor. Overlaps with resubscribe — do not sum."),

    M("cf_resubscribe", "Resubscribe after cancelling",
      "44.80%", "60,891 of 135,903 successful cancellers", COHORT,
      "Ordered funnel MTUEditSubscriptionCancelSuccess → MTUOrderCompleteBtn (is_subscription = true) · "
      "60-day window · unique users", "i7673xwm", "new",
      "Median 19.3 days. Absent from the previous version entirely. Right-censored, so a floor."),
]

# ---------------------------------------------------------------- segments ----
def seg(label, value, num, den, chart, status="new", note=""):
    return M("seg_" + chart, label, value, f"{num} of {den}", COHORT, FUNNEL_CFG + " · filtered",
             chart, status, note)

COUNTRY = [
    seg("El Salvador", "39.57%", "6,678", "16,875", "2j37y76s", "new",
        "Effectively tied with Honduras — 0.09pp apart. Neither should be called the worst market."),
    seg("Honduras", "39.48%", "12,969", "32,847", "1dj79fxz", "confirmed"),
    seg("Guatemala", "37.03%", "21,252", "57,389", "ey0kpugm", "confirmed", "Largest corridor in the base."),
    seg("Jamaica", "32.17%", "5,500", "17,097", "82fap7h4", "superseded",
        "Runs 4.2pp above the previous version — the largest per-country revision."),
    seg("Mexico", "27.11%", "4,468", "16,480", "arrf2w4r", "confirmed"),
    seg("Dominican Republic", "26.78%", "9,145", "34,148", "8lp44hg2", "confirmed"),
    seg("Haiti", "25.81%", "13,233", "51,269", "rpe7s0my", "superseded",
        "Runs 3.8pp above the previous version. Second-largest corridor."),
    seg("Nigeria", "17.88%", "1,770", "9,897", "4qfcm8hj", "new", "Best of the top 8."),
]

TENURE = [
    seg("vip", "43.08%", "22,016", "51,105", "6haohove", "confirmed"),
    seg("low", "33.27%", "13,452", "40,436", "i4htn6sr", "confirmed"),
    seg("high_freq", "31.11%", "13,593", "43,698", "u0fvy1kj", "confirmed"),
    seg("high_denom", "30.84%", "12,648", "41,017", "yo5u180g", "confirmed"),
    seg("literal 'none'", "26.96%", "5,059", "18,764", "9jbzyp7h", "new",
        "TAXONOMY DEFECT: distinct from unset '(none)', and the two behave 7.8pp apart."),
    seg("two_trx", "24.65%", "8,855", "35,927", "p5t2rupa", "confirmed"),
    seg("one_trx", "23.29%", "11,295", "48,506", "zh4bpjtv", "confirmed"),
    seg("unset '(none)'", "19.19%", "5,956", "31,044", "9b84pe34", "new",
        "Lowest rate in the tenure set — an unlabelled cohort behaving distinctly suggests the label "
        "tracks engagement, not only value."),
]

PLATFORM = [
    seg("Android", "33.61%", "29,522", "87,842", "9ibdyo1j", "confirmed"),
    seg("iOS", "29.11%", "53,757", "184,693", "31wy7mq4", "confirmed",
        "iOS is 68% of the base, so the blended 30.57% is dominated by iOS."),
]

VERSION = [
    seg("app version 26.7.1 (worst)", "37.20%", "11,245", "30,231", "iw7zip5m", "new",
        "TAXONOMY NOTE: the property is 'version'; 'version_name' does not exist in this project."),
    seg("app version 26.6.3 (largest cohort)", "32.81%", "36,216", "110,369", "kl63v1ok", "new"),
    seg("app version 26.4.3 (best)", "23.03%", "4,220", "18,320", "lomcxda4", "new",
        "A 14.2pp spread across versions — wider than the entire Android/iOS gap. No single-version "
        "comparison should be used to claim a regression."),
]

# ---------------------------------------------------------------- renewals ----
RENEWALS = [
    M("rn_charges", "Subscription-flagged MTU charges",
      "307,301 events, all on or after 10 Aug 2026",
      "3,438,517 MTU MarketingTxnCompleted events in the window (8.94%)", RENEW,
      "MarketingTxnCompleted · product_category = MTU AND subscription = true · event_totals · daily",
      "y9dwp54t", "new",
      "Zero across the preceding 70 days. Nothing before 10 Aug is observable, so the report cannot "
      "speak to renewal behaviour for the Mar–Aug cancellation cohort."),

    M("rn_control", "MTU completed transactions by subscription flag",
      "unset 62.20% · False 28.86% · True 8.94%",
      "3,438,517 MTU completed EVENTS", RENEW,
      "MarketingTxnCompleted · product_category = MTU · group by subscription · event_totals",
      "otwzggm5", "superseded",
      "CORRECTS the previous claim that the property 'began carrying the flag' on 10 Aug. It already "
      "carried False on 781,120 events beforehand; only the True value is new, and it arrives "
      "additively. Even post-10-Aug, 47.0% remain unset, so this property is unsafe as a denominator."),

    M("rn_failgap", "Renewal-failure attribution",
      "100.0% of MTU payment failures carry no subscription flag",
      "381,167 of 381,167 MarketingTxnFailed events", RENEW,
      "MarketingTxnFailed · product_category = MTU · group by subscription · event_totals",
      "owzed305", "confirmed",
      "A single '(none)' group; zero True and zero False. A failed renewal is indistinguishable from "
      "a failed one-off top-up, so involuntary churn cannot be measured at any volume. The window is "
      "90 days, not the 121 previously stated."),

    M("rn_mixture", "Share of flagged charges not attributable to an in-window creation",
      "71.2%", "114,893 of 161,267 distinct users", "10–29 Aug 2026",
      "MarketingTxnCompleted (product_category = MTU, subscription = true) · unique users · "
      "segmented to users with zero subscription checkouts in the window", "6rdjnsi9", "new",
      "The flagged stream is a MIXTURE of renewals and initial charges — 28.8% did complete a "
      "checkout in-window. 307,301 must not be reported as a pure renewal count."),
]

GAPS = [
    ("Cancellation reason", "No cancel_reason property on any MTUEditSubscriptionCancel* event.",
     "Why customers cancel, and what share were unintended — the premise of the V2 epic.", "Not ticketed"),
    ("Renewal-failure attribution", "subscription flag is 100% unset on MarketingTxnFailed for MTU.",
     "Involuntary churn: how many, when, why. One property on a pipeline that already sets it on successes.",
     "Not ticketed · highest leverage"),
    ("Any renewal event", "Taxonomy search across six renewal/billing/dunning concepts returns nothing.",
     "Renewal volume, success rate, cycles survived, cohort decay.", "Not ticketed"),
    ("Per-subscription identifier", "No subscription_id on IMTU order or cancel events.",
     "Subscription lifetime, and whether a cancellation maps to the subscription just created.", "Not ticketed"),
    ("Toggle-shown signal", "18.96% of order screens carry no default_subscription_toggle value.",
     "Whether unset means 'correctly not rendered' or 'not instrumented' — the ambiguity DCS-5277 turns on.",
     "Not ticketed"),
    ("Toggle default reason", "Four documented outcomes (duplicate / max_subscriptions / experiment / default); none emitted.",
     "How often the duplicate rule or the subscription cap actually fires.", "Not ticketed"),
    ("Diagnostic failure reasons", "37.27% of order failures carry the bare value 'failed'.",
     "What is actually breaking in a third of failed orders.", "Not ticketed"),
    ("Funnel group labels", "Grouped funnels return series without labels in this API.",
     "Any grouped segment read — every segment figure here needed an explicitly filtered chart instead.",
     "Tooling limitation"),
    ("Notification analytics", "No transactional event for the renewal reminder or failure SMS.",
     "Whether a reminded customer cancels, tops up, or updates their card.", "DCS-5260 To Do"),
    ("V2 presentation events", "Payment-bar toggle events not yet defined.",
     "Any V2-versus-V1 comparison at all.", "DCS-5300 / 5301 To Do"),
]

ALL_GROUPS = [
    ("Exposure and toggle interaction", EXPOSURE),
    ("Checkout and confirmation", CHECKOUT),
    ("Cancellation brackets", BRACKETS),
    ("Cancellation flow and what follows", CANCEL_FLOW),
    ("Cancellation by recipient country", COUNTRY),
    ("Cancellation by customer tenure", TENURE),
    ("Cancellation by platform", PLATFORM),
    ("Cancellation by app version", VERSION),
    ("Renewals and payments", RENEWALS),
]


def all_metrics():
    for _, g in ALL_GROUPS:
        for m in g:
            yield m


if __name__ == "__main__":
    n = list(all_metrics())
    from collections import Counter
    print(f"{len(n)} metrics")
    print(Counter(m["status"] for m in n))
    print(f"{len(set(m['chart'] for m in n))} distinct charts")
