#!/usr/bin/env python3
"""
Creates ONE Google Doc: "Duplicate IMTU Subscriptions: Analysis and Cleanup Rules".

Text twin of IMTU_Duplicate_Subscriptions_Analysis.html. Both are built from the
same verified figures, computed from the five tabs of the source sheet
"Copy of Duplicates Sep 18" (1yPf33IWtMHgBSnuZG-o_FZTLWVdfi5CsSxTq7JDTTuM).

Every headline number was derived twice: once by an independent analysis pass
over the extract, then re-derived from the raw CSVs. Where the two disagreed the
re-derived figure is the one used (day-one cancels at N=3 are 18,486 not 18,566;
surplus charges in the last 30 days are 1,835 not 1,746).
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

TITLE = "Duplicate IMTU Subscriptions: Analysis and Cleanup Rules"
SHEET = ("https://docs.google.com/spreadsheets/d/"
         "1yPf33IWtMHgBSnuZG-o_FZTLWVdfi5CsSxTq7JDTTuM/edit")
DOC_LINKS = dict(LINK_MAP)
DOC_LINKS.update({"Copy of Duplicates Sep 18": SHEET, "source sheet": SHEET})

# ---------------------------------------------------------------- tables ----

POPS = [
    ["Population", "Subscriptions", "Groups", "Customers", "What it is", "What fixes it"],
    ["A. Behavioural duplicates (backlog)", "27,256", "5,807", "3,644",
     "Three or more subscriptions from the same customer to the same number, same offer, same frequency. Built up since January 2024.",
     "Auto-cancel rules plus a purchase-flow fix"],
    ["B. K2 double fulfilment (live bug)", "14,011", "7,005", "5,955",
     "Two subscriptions created from a single checkout, a median 202 seconds apart. 98% created since April 2026, still running.",
     "Idempotency on the transaction id"],
]

CASES = [
    ["Classification", "Groups", "Subscriptions", "Customers", "Reading"],
    ["Case 2. Re-subscribed on later top-ups, then removed the card", "2,159", "11,562", "1,064",
     "The dominant story. Subscriptions added days or weeks apart, then the card pulled."],
    ["Card on file but failing (no funds, declined, expired)", "1,957", "7,932", "1,435",
     "Not in the three cases. The card is still there, it simply does not pay."],
    ["Case 3. Paying duplicates", "1,387", "6,175", "1,094",
     "Charging successfully today. Revenue, and the group we do not cancel."],
    ["Case 1. Same-session accidental, then removed the card", "229", "1,330", "202",
     "Much smaller than expected. Genuine double taps are rare."],
    ["New, not yet launched", "75", "257", "71",
     "Created recently, first charge still pending."],
]

FREQ = [
    ["Frequency", "Subscriptions", "Share", "Groups", "Time to reach 3 consecutive failures"],
    ["3 month", "11,426", "41.9%", "2,327", "9 months"],
    ["1 month", "8,143", "29.9%", "1,905", "3 months"],
    ["1 week", "5,082", "18.6%", "1,013", "3 weeks"],
    ["2 week", "2,605", "9.6%", "562", "6 weeks"],
    ["Total", "27,256", "100%", "5,807", ""],
]

CAUSE = [
    ["Dominant failure cause", "Subscriptions", "Customers"],
    ["Card removed, no card on file", "9,823", "971"],
    ["No funds on the card", "4,353", "1,080"],
    ["Card removed, after payment failures", "3,267", "643"],
    ["Card declined or restricted", "1,654", "498"],
    ["Card expired", "919", "212"],
    ["Other or generic failure", "978", "302"],
    ["Unclassified", "296", "113"],
    ["Top-up limit reached", "53", "16"],
]

AGE = [
    ["How long it has been failing", "Subscriptions", "Share"],
    ["365 days or more", "9,861", "46.2%"],
    ["180 to 364 days", "7,067", "33.1%"],
    ["90 to 179 days", "2,626", "12.3%"],
    ["30 to 89 days", "985", "4.6%"],
    ["Under 30 days", "804", "3.8%"],
]

THRESH = [
    ["Threshold", "Day one", "Share", "Customers", "90% cleared", "Effectively done", "At risk of a wrong cancel"],
    ["N = 3 (recommended)", "18,486", "86.6%", "2,588", "13 weeks", "39 weeks", "452"],
    ["N = 4", "17,028", "79.8%", "2,427", "26 weeks", "52 weeks", "384"],
    ["N = 5", "16,050", "75.2%", "2,303", "39 weeks", "65 weeks", "319"],
]

CLEAR = [
    ["Rule", "Day one", "3 months", "6 months", "9 months", "12 months"],
    ["N = 3 consecutive failures", "86.6%", "90.0%", "96.3%", "99.9%", "100%"],
    ["N = 4 consecutive failures", "79.8%", "83.5%", "89.9%", "96.3%", "99.9%"],
    ["N = 5 consecutive failures", "75.2%", "79.0%", "84.6%", "89.9%", "96.3%"],
    ["N = 3 or 90 days without a charge", "95.1%", "about 100%", "100%", "100%", "100%"],
]

FLOOR = [
    ["Component", "N=3", "N=4", "N=5", "Why it is permanent"],
    ["Structural residue, subscriptions the rule can never reach", "4,314", "4,314", "4,314",
     "3,336 intermittent payers that fail then succeed inside two cycles, 580 too new to have launched, 398 failing with no future launch scheduled"],
    ["In-flight stock, failing but not yet at the threshold", "1,149", "1,531", "1,914",
     "New duplicates keep arriving; each waits out its N cycles before the rule fires"],
    ["Permanent floor, 2026 inflow", "about 5,460", "about 5,850", "about 6,230", ""],
    ["Permanent floor, if inflow returns to the 2025 rate", "about 7,870", "about 9,050", "about 10,240",
     "Upper bound, using the trailing twelve-month transition rate of 957 per month"],
]

TOPOWN = [
    ["Customer", "Surplus subscriptions", "Groups", "Charges taken"],
    ["7aqie3a1b4a7", "156", "16", "636"],
    ["d1xxxy94h8tw", "88", "20", "280"],
    ["agx09v54i89y", "52", "7", "103"],
    ["cd7957kemv6n", "51", "13", "213"],
    ["deyt87bofare", "40", "3", "58"],
    ["dv53myzfq0vr", "35", "7", "121"],
    ["aqn6vdw6oxxn", "34", "5", "106"],
    ["egmx35pcnk96", "27", "6", "251"],
]

GEO = [
    ["Destination", "Surplus subscriptions", "Frequency", "Surplus subscriptions"],
    ["Haiti", "722", "3 month", "1,944"],
    ["Guatemala", "455", "1 month", "1,049"],
    ["Honduras", "389", "1 week", "256"],
    ["Dominican Republic", "368", "2 week", "220"],
    ["Ethiopia", "306", "", ""],
]

K2STATE = [
    ["State of the pair", "Pairs", "What it means"],
    ["Both actively purchasing", "2,642", "Double charging right now"],
    ["Both awaiting first charge", "2,511",
     "Will start double charging on their first cycle. 2,295 customers, $21,934 of position-2 value per cycle."],
    ["Both failing", "1,018", "Neither collecting"],
    ["One active, one failing", "824", "Self-resolved, effectively"],
    ["Never launched", "10", ""],
]

TABLES = [("POPS", POPS), ("CASES", CASES), ("FREQ", FREQ), ("CAUSE", CAUSE),
          ("AGE", AGE), ("THRESH", THRESH), ("CLEAR", CLEAR), ("FLOOR", FLOOR),
          ("TOPOWN", TOPOWN), ("GEO", GEO), ("K2STATE", K2STATE)]

# ---------------------------------------------------------------- blocks ----

B = [
    ("h1", "Duplicate IMTU subscriptions: what is in the file, and what the cleanup rules will actually do"),
    ("cap", f"Source: Copy of Duplicates Sep 18. Extract date 2026-09-04. Prepared 2026-09-18. Five tabs, 41,267 rows. Sheet: {SHEET}"),

    ("h2", "The short version"),
    ("p", "The extract holds two unrelated problems that need opposite treatments. A behavioural backlog of 27,256 duplicate subscriptions, mostly dead and costing us launch attempts, and a live server bug that is still minting new double subscriptions at about 570 pairs a week. An auto-cancel rule fixes the first and does almost nothing for the second."),
    ("p", "Headline figures: 27,256 behavioural duplicates across 5,807 groups and 3,644 customers. 21,343 already failing, 78.3% of the file. 18,486 cancelled on day one at a threshold of three failures, 86.6% of the failing backlog. 1,094 customers paying for 3,469 surplus subscriptions. A permanent floor of roughly 5,400 to 7,900 failing subscriptions once the rules reach steady state. And 570 new duplicate pairs per week from the K2 bug, which is still live."),
    ("p", "Five things drive every recommendation in this document."),
    ("n", "The auto-cancel rule works, and it works fast. At three consecutive failures it clears 86.6% of the failing backlog the moment it runs, 90% within three months and effectively all of it within nine months. N=4 and N=5 buy very little extra safety and add three and six months respectively."),
    ("n", "The card-removal story is confirmed, and it is the single largest cause. 13,090 failing subscriptions carry a missing-card failure. 995 of the 1,285 customers involved have no working card left anywhere in the file. They did exactly what you described: they pulled the payment method to stop the charges."),
    ("n", "Most duplicates are not accidental double taps. Only 12.8% of the gaps between one subscription and the next in the same group are under ten minutes. The median gap is 12.2 days. This is Case 2, a customer re-adding the subscription on every top-up, not Case 1."),
    ("n", "Case 3 is real and it is 1,094 customers. They hold 3,469 surplus active subscriptions that have taken 20,459 charges, 1,835 of them in the last 30 days alone. No failure rule will ever touch these, by design."),
    ("n", "The K2 double-fulfilment bug is a separate, urgent, and much cheaper fix. One checkout creates two subscriptions roughly 202 seconds apart. It is not user behaviour and no cancellation rule prevents it. An idempotency key on the transaction id stops it outright."),

    ("h2", "What is actually in the file"),
    ("p", "The spreadsheet contains two populations that barely overlap: they share only 221 subscriptions and 61 customers. Treating them as one problem is the main analytical trap here, because the fix for one is a cancellation rule and the fix for the other is a code change."),
    ("table", "POPS"),
    ("p", "A few facts worth knowing before reading any number below. The canceled_at and canceled_reason columns exist and are blank on all 27,256 rows, which means a soft cancel is already supported by the schema and nothing has ever used it. Creation dates start on 2024-01-16, so nothing here predates 2024. And 8,722 creation timestamps, 32% of the file, are estimated rather than recorded, all of them older rows, so month-level history before 2025 is approximate."),
    ("p", "Exclude from behavioural analysis: a system event on 2025-12-19 created 1,122 subscriptions in two one-hour windows, up to 83 per minute, across 343 customers. That is a migration, not customer behaviour, and it is why December 2025 is the tallest month in the timeline. Removing it drops 349 groups below the three-subscription threshold entirely."),

    ("h2", "The three cases, measured"),
    ("p", "Your three hypotheses map onto the data cleanly, but not in the proportions you might expect. I classified every one of the 5,807 groups: a group is Case 3 if it currently has two or more subscriptions actively purchasing; otherwise if the majority of its failing subscriptions show a missing card, it is Case 1 or Case 2 depending on whether the subscriptions were created within a day of each other or spread out over time."),
    ("table", "CASES"),
    ("p", "The one correction to the brief. Case 1 as described, the accidental double purchase, is only 229 groups. The mechanism behind almost all of the backlog is Case 2: the customer tops up again, the subscription toggle is on again, and a second subscription is created. The median gap between one subscription and the next in a group is 12.2 days, and only 12.8% of gaps are under ten minutes. That matters for the fix, because a double-tap guard would catch almost nothing, while a check at checkout saying \"you already have a subscription to this number\" would catch most of it."),
    ("p", "There is corroborating evidence for the Case 2 mechanism. 91.1% of later subscriptions with a recorded creation date had their first charge attempt 0.8 to 1.2 cycles after creation, which is the signature of a subscription created at a top-up checkout. And 51.2% of later subscriptions were created after an earlier sibling had already charged at least once, with 22.4% created while a sibling was still successfully purchasing."),

    ("h2", "Profile: frequency, age, and failure count"),
    ("h3", "Frequency"),
    ("p", "The backlog skews long-cycle, which is the single most important fact for how long the rules take to work. A three-month subscription needs three months to accumulate one failure, so it needs nine months to reach three."),
    ("table", "FREQ"),
    ("h3", "When they were generated"),
    ("p", "Creation runs from 2024-01-16 to the extract date, peaking at 2,976 in December 2025 (inflated by the migration event) and running at 483 to 709 a month through mid-2026. Duplicate creation has slowed materially. Daily creation ran at 36.9 per day from January to mid-March 2026, dropped to 19.9 per day after the 26.3.1 release on 17 to 19 March, and sits at 17.3 per day since the 26.4.3 release on 30 April. That is a 53% reduction."),
    ("p", "One caveat carried over from the earlier analysis: the same March release also changed the default recurrence from three months to one month, which mechanically slows group formation, so the two effects cannot be separated from this file alone. Amplitude can separate them."),
    ("h3", "How many times they have been failing"),
    ("p", "The distribution is extreme at the top end. The median failing subscription has already failed 11 consecutive times, the mean is 26.5, and 7,483 subscriptions have failed more than 21 times in a row. The worst has launched 188 times. Collectively the failing set has burned 710,225 failed attempts and, left alone, will generate another 7,819 attempts every week, about 408,000 a year, none of which can ever succeed for the 9,823 with no card on file."),
    ("p", "Counts by bucket: 14 subscriptions at zero consecutive failures, 1,061 at one, 1,782 at two, 1,458 at three, 978 at four, 1,255 at five, 3,795 at six to ten, 3,517 at eleven to twenty, and 7,483 at twenty-one or more."),
    ("table", "AGE"),
    ("p", "Median 328 days. This backlog is old, and 79.4% of it is still armed with a future launch date, so it is not dormant: 7,099 of these subscriptions were scheduled to fire within seven days of the extract."),
    ("h3", "Why they fail"),
    ("table", "CAUSE"),
    ("p", "Card removal, the escape hatch you described, is the dominant cause at 13,090 subscriptions across the two card-removed rows. The detail confirms the behaviour precisely: of the 1,285 customers with a missing-card failure, 995 have every single subscription in the file failing for a missing card, meaning they removed their only payment method. 923 of them had completed at least one purchase first, and 704 paid and now have nothing active at all, having completed 12,058 purchases over a median of 139 days before pulling the card."),
    ("p", "And the crucial corroboration for your hypothesis: among those customers, 860 of their 1,531 groups had two or more subscriptions completing purchases before the card was pulled. 556 customers were genuinely double-billed for the same recipient and offer, and then stopped it themselves. That is the behaviour loop you suspected, measured."),

    ("h2", "The auto-cancel rule: what it clears and how fast"),
    ("p", "I simulated the rule you proposed, cancelling after N consecutive failed attempts, against every failing subscription. Consecutive failures are counted directly from the launch count for subscriptions that never charged, and estimated as the number of cycles between the last successful charge and the last attempt for the rest."),
    ("table", "THRESH"),
    ("p", "Recommendation: N = 3. The extra caution in N=4 and N=5 protects only 68 and 133 additional subscriptions respectively from a wrong cancel, while costing three and six extra months of dead launch traffic. \"At risk of a wrong cancel\" counts subscriptions that would be cancelled despite having completed a charge in the last 90 days, that is, intermittent payers. At N=3 that is 452 subscriptions, 2.4% of the cancel set, and a 30-day grace check removes almost all of them."),
    ("p", "The much better version of the same rule. Adding a calendar arm cuts the clearance time from nine months to three. Cancel after 3 consecutive failures OR after 90 days of launching without a single successful charge, whichever comes first. That is eligible for 20,287 subscriptions on day one, 95.1%, instead of 18,486, and finishes the entire backlog within about three months rather than nine. The reason is the 8,348 three-month subscriptions, which need nine months to hit three failures under the count-only rule but trip the calendar arm immediately."),

    ("h2", "How long, and what will always remain"),
    ("h3", "How long to clear the backlog"),
    ("table", "CLEAR"),
    ("p", "Read that as: with N=3 alone, the visible backlog is gone in a single batch run, and the long tail of quarterly subscriptions takes until roughly June 2027 to finish. With the hybrid rule, everything is done by December 2026."),
    ("h3", "The minimum that will always be there"),
    ("p", "This is the question with the least clean answer, so here is the arithmetic rather than a single number. The permanent floor has two parts."),
    ("table", "FLOOR"),
    ("p", "The honest answer is a range of roughly 5,400 to 7,900 failing or failure-prone subscriptions permanently in the database at N=3, and the position within that range is decided by product, not by the rule. The in-flight component is driven entirely by how many new duplicates get created: at the current 2026 rate of 309 new failing subscriptions per month it is about 1,149, and if creation returns to the 2025 rate it triples. The structural residue of about 4,300 does not move with N at all, and about 3,336 of it is arguably not a problem: those are subscriptions that fail sometimes and succeed sometimes, which is normal for a card that occasionally lacks funds."),
    ("p", "The lever that actually moves the floor: changing N from 3 to 5 moves it by about 770. Stopping duplicate creation at checkout moves it by up to 2,400, and it is the only thing that does. The rules clean up history; the purchase-flow fix is what stops the floor from being rebuilt."),

    ("h2", "Rules to build, beyond the failure counter"),
    ("p", "Ordered by value per unit of engineering effort. R1 is the rule you already proposed, tuned; R2 and R3 are the ones I would add first."),
    ("b", "R1. Soft cancel after 3 consecutive failures, or 90 days launching without a charge. The rule you proposed with a calendar arm added. Never delete: write canceled_at and canceled_reason, which already exist and are unused. Deleting destroys the audit trail and breaks the 18,758 purchase records that hang off these subscriptions. Clears 20,287 on day one and all of it in about three months."),
    ("b", "R1a. Grace exemption: never cancel a subscription that charged successfully in the last 30 days. A one-line guard that removes essentially all of the false-positive risk in R1, protecting the 452 intermittent payers whose card occasionally lacks funds."),
    ("b", "R2. Duplicate guard at checkout: block a second subscription to the same number, offer and frequency. The highest-value rule in this list because it is the only one that stops the backlog being rebuilt. If an active subscription already exists for that recipient and offer, do not create a second one. Offer \"you already have this subscription, change it instead\". This is the direct fix for Case 2, which is 2,159 groups and 11,562 subscriptions, and it prevents up to 2,400 of the permanent floor."),
    ("b", "R3. Idempotency key on the checkout transaction id. Stops the K2 double-fulfilment bug outright. Two subscriptions are being created from one transaction id a median 202 seconds apart, which is a retry after a timeout, not a user action. The SQL in the source tab already groups by txid, so the key is identified. This is a code fix, not a rule, and it is the most urgent item in this document. Stops about 570 new duplicate pairs per week and protects 2,511 pairs about to start double charging."),
    ("b", "R4. Card-removal cascade: when the last card is removed, pause every subscription immediately. Today a customer removes their card and their subscriptions keep firing for a median of 328 days. 995 customers are in exactly this state. Pause on card removal, tell the customer what will happen, and offer to cancel. This would have prevented 9,823 of today's failures and saves about 4,950 launch attempts per week."),
    ("b", "R5. Cancel any subscription whose offer has been retired. These can never succeed regardless of the card. A deterministic, zero-judgement cleanup that should run before the failure-count rule so those subscriptions are cancelled with an accurate reason rather than a generic payment failure."),
    ("b", "R6. Warn the customer before cancelling, not after. Send a notification on the second consecutive failure: \"we could not charge your card for your top-up to +509...; it will be cancelled after the next failed attempt\". This recovers the customers who simply need to update a card, and it turns a silent cancellation into a service message. It also gives the 4,353 no-funds cases a chance to act."),
    ("b", "R7. Cap concurrent active subscriptions per recipient and offer at one. The structural version of R2, enforced at the subscription service rather than the UI, so no client and no retry path can create the second one. This is what prevents Case 3 from growing while you decide what to do about the existing paying duplicates."),
    ("b", "R8. Stop launching subscriptions that have no payment method at all. 9,823 subscriptions have no card on file and still fire on schedule. Suspend rather than attempt. This is pure waste: roughly 4,950 pointless attempts per week against the payment stack, and it will continue for the quarterly subscriptions for months even after R1 goes live."),
    ("h3", "Suggested sequence"),
    ("n", "R3 now. It is a live bug creating 570 new duplicate pairs a week. Every week of delay adds roughly 570 pairs to the backlog."),
    ("n", "R8 and R5 next. Deterministic, no customer impact, immediate load relief."),
    ("n", "R2 and R7 with the next app release. These stop the backlog being rebuilt and therefore set the permanent floor."),
    ("n", "R6, then R1 with R1a. Warn first, then cancel. Run R1 as a batch over the backlog once, then as a daily job."),
    ("n", "R4 with the card management work."),

    ("h2", "Case 3: the customers paying for duplicates"),
    ("p", "These are the customers being charged more than once for the same top-up to the same number, and paying. No failure rule reaches them, because nothing about them is failing. As instructed, none of these are cancelled."),
    ("p", "The cohort: 1,094 customers, 30.0% of all customers in the file. 1,387 duplicate groups. 4,856 active subscriptions in those groups, of which 3,469 are surplus beyond one keeper per group. Those surplus subscriptions have taken 20,459 charges, a median of 3 each, and 1,835 of them took a charge in the 30 days before the extract."),
    ("p", "How solid the money number is. Population A has no price column. The estimate takes the face value from the offer code, keeps only subscriptions billed in USD with a plausible face value between $1 and $60, and multiplies by the charges per month. That covers 1,568 of the 3,469 surplus subscriptions, 45%, and gives $12,499 per month, about $150,000 a year. The remaining 55% are in local currencies, have blank currency, or carry offer codes with no parseable price, so the true figure is higher. Treat $150k as a floor, not a point estimate, and get a real figure from the billing system before taking this to finance."),
    ("h3", "What these customers look like"),
    ("p", "Concurrent active subscriptions per group: 333 groups have 2, 673 have 3, 190 have 4, 160 have 5 to 9, and 31 have 10 or more. By concentration: 231 customers hold exactly one surplus subscription, 131 hold five or more, and 42 hold ten or more. The top 15 customers hold 641 surplus subscriptions, 18.5% of the total."),
    ("p", "The distribution has a long tail that matters for how you communicate. 231 customers hold exactly one surplus subscription and will barely notice. At the other end, customer 7aqie3a1b4a7 holds 156 surplus active subscriptions across 16 groups to 13 Honduran numbers, which have taken 636 charges between April 2024 and the extract date. One group of theirs has 43 concurrently active subscriptions on a single number. That is not a customer who has noticed and accepted the arrangement."),
    ("table", "TOPOWN"),
    ("h3", "Where they are"),
    ("table", "GEO"),
    ("p", "Quarterly subscriptions are 56% of the surplus by count but a much smaller share of the money, because they bill four times a year. The monthly and weekly surplus subscriptions are a minority of the count and the majority of the revenue."),
    ("p", "A decision you will need to make separately. I have followed the instruction not to cancel these. It is worth being explicit about what that means: 1,835 surplus charges went out in the last 30 days to customers who, on the evidence of the other 995 customers who pulled their cards, would stop them if they noticed. The 556 customers who were double-billed and then removed their card are the control group, and they tell you what happens when a customer does notice. This is a chargeback and trust exposure, not only a revenue line. A middle path worth considering: notify the 42 customers with ten or more surplus subscriptions, leave the 231 single-surplus customers alone, and stop the cohort growing with R7."),

    ("h2", "The K2 double-fulfilment bug"),
    ("p", "This is a different problem with a different fix, and it is the most urgent thing in the file. One checkout creates two subscriptions. The median gap between them is 202 seconds, with 99.2% falling between two and five minutes, which is a server-side retry after a timeout, not a customer double tap."),
    ("p", "Scale: 7,005 pairs, 14,011 subscriptions, 5,955 customers. About 570 new pairs per week in the four weeks to 2026-09-07, and still rising. 2,773 pairs have already double charged. 2,511 pairs are about to."),
    ("table", "K2STATE"),
    ("p", "Revenue already collected on the second subscription of a pair, where both collected: $25,230 USD plus 806 GBP, 838 CAD, 256 EUR and 23 AUD. Concentrated in Nigeria with 9,676 subscriptions and Venezuela with 3,622, and 97.9% on a monthly cycle."),
    ("p", "A problem with the \"remove least revenue\" plan in the tab. In 2,108 of the 2,773 paying pairs, 76%, the two subscriptions have collected exactly the same amount, so \"least revenue\" has no tie-break in three quarters of cases and the choice falls through to an arbitrary rule. More importantly, applying it as written cancels 2,655 subscriptions that are currently active and paying, and in 13 cases it would cancel the active subscription and keep the failing one. If you go ahead, the tie-break should be \"keep position 1, the original\", not \"keep the one with more revenue\", and the 13 inversions should be held out and handled manually."),

    ("h2", "Method and limits"),
    ("b", "What was computed. Every number here came from the five tabs of the source sheet, read through the Sheets API and analysed in pandas. Seven independent analyses were run over the extract, and every headline number in this document was then re-derived a second time from the raw CSVs. Where the two passes disagreed, the re-derived number is the one shown: the day-one cancel count at N=3 is 18,486 and not 18,566, and the surplus charges in the last 30 days are 1,835 and not 1,746."),
    ("b", "Consecutive failures are partly estimated. For the 13,702 failing subscriptions that never charged, the count is the launch count, which is exact. For the 7,641 that charged and then went stale, it is the number of cycles between the last successful charge and the last attempt, which is an estimate. It can be wrong if a subscription was paused."),
    ("b", "Money is an estimate with stated coverage. Population A has no price column. See the note in the Case 3 section."),
    ("b", "Creation dates before 2025 are approximate. 8,722 of 27,256 creation timestamps, 32%, are reconstructed as the first launch minus one cycle."),
    ("b", "Clearance timing assumes every future attempt fails and that the rule runs daily from go-live on the extract date. Real clearance will be slightly slower, because some subscriptions will charge successfully once more and reset their counter."),
    ("b", "The December 2025 bulk event is included in totals but should be excluded from behavioural conclusions. 1,122 subscriptions created in two hours are a migration artefact."),
    ("b", "Not answerable from this file: whether the March 2026 release reduced duplicates through the UI change or through the recurrence default change, actual amounts charged, and whether any of these customers have raised a support ticket or a chargeback. The first needs Amplitude, the second the billing system, the third Zendesk."),
    ("cap", "Prepared for the IMTU product review, 18 September 2026. An HTML version with charts is in the repository as IMTU_Duplicate_Subscriptions_Analysis.html."),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}


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
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(line)},
            "paragraphStyle": para, "fields": fields}})
        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind == "n":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"}})
        if kind == "cap":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(text)},
                "textStyle": {"italic": True,
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}})
        if kind in ("b", "n") and ". " in text:
            lead = len(text.split(". ")[0]) + 1
            if lead < 120:
                reqs.append({"updateTextStyle": {
                    "range": {"startIndex": cur, "endIndex": cur + lead},
                    "textStyle": {"bold": True}, "fields": "bold"}})
        cur += len(line)
    return reqs


def batched(docs, doc_id, reqs, size=40):
    for i in range(0, len(reqs), size):
        for attempt in range(5):
            try:
                docs.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": reqs[i:i + size]}).execute()
                break
            except Exception as exc:
                if "Quota" not in str(exc) and "429" not in str(exc):
                    raise
                time.sleep(2 ** attempt)
        time.sleep(0.4)


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in el["paragraph"]["elements"])


def insert_table(docs, doc_id, marker, data):
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = plen = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[{marker}]]":
            idx, plen = el["startIndex"], len(para_text(el))
            break
    if idx is None:
        print(f"  ! placeholder {marker} not found")
        return False
    rows, cols = len(data), len(data[0])
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
        {"deleteContentRange": {"range": {"startIndex": idx,
                                          "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx}, "rows": rows,
                         "columns": cols}},
    ]}).execute()
    time.sleep(1.2)
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
        if r == 0 or c == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
    batched(docs, doc_id, reqs, size=40)
    return True


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    doc = docs.documents().create(body={"title": TITLE}).execute()
    doc_id = doc["documentId"]
    print(f"Created doc: {doc_id}")

    batched(docs, doc_id, build_requests(B))
    print("Text inserted")

    for marker, data in TABLES:
        ok = insert_table(docs, doc_id, marker, data)
        print(f"  table {marker}: {'ok' if ok else 'FAILED'} ({len(data) - 1} rows)")

    linkify(docs, doc_id, DOC_LINKS)

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
