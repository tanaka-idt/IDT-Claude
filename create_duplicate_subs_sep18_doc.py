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
    ["B. K2 double fulfilment (resolved)", "14,011", "7,005", "5,955",
     "Two subscriptions from a single checkout, a median 202 seconds apart. Fixed by backend in the week of 15 September 2026; these records have been deleted.",
     "Done. No further action"],
]

GLOSS = [
    ["Term", "Also called", "What it means", "Example"],
    ["Subscription", "timer, one row",
     "A single recurring top-up instruction. It has its own schedule, its own card, its own state and its own charge history, and it is one row in the extract. The database calls these timers.",
     "\"$7 to +504 8869 3565, every 3 months\""],
    ["Group", "the unit of duplication",
     "Every subscription from one customer to the same recipient number, for the same offer, at the same frequency. A group holding more than one subscription is by definition a duplicate, which makes the group the thing we are counting when we say \"duplicate\".",
     "5 identical \"$7 to +504..., every 3 months\" subscriptions = one group of 5"],
    ["Customer", "owner_id, the account",
     "The BOSS account holder. One customer can hold several groups, to different numbers or different offers, and several subscriptions inside each group. The median customer here holds 1 group and 4 subscriptions; the largest holds 33 groups and 182 subscriptions.",
     "983 of the 3,644 customers have more than one group"],
]

CASEDEF = [
    ["Case", "As described", "What the data says"],
    ["Case 1. Subscribed on every top-up, then removed the card",
     "The customer does not understand the subscription purchase flow and leaves the subscription option on for every transaction, so each top-up creates another subscription. They end up with several subscriptions to the same number, and the way out they find is to delete the payment method so they stop being charged several times.",
     "Confirmed, and it is the dominant story. 2,388 groups, 12,892 subscriptions, 1,184 customers. This is the only mechanism by which a duplicate gets created, and it covers both the slow version, where the subscriptions arrive weeks apart, and the fast version, where the customer buys two top-ups minutes apart in one sitting."],
    ["Case 2. Subscribed more than once, but the card is still on file and does not pay",
     "The same purchase behaviour as Case 1, but the customer never removed anything. The payment method is still on the account and simply fails: no funds, declined, restricted, or expired. The duplicates go on failing and the customer has taken no action, and may not know there is anything to act on.",
     "Confirmed, and it is the largest case by customer count. 1,957 groups, 7,932 subscriptions, 1,435 customers. Worth separating from Case 1 because the remedy is different: a Case 1 customer has made a decision and acted on it, whereas a Case 2 customer may simply need a working card, which makes them the group most likely to be recovered by a notification rather than a cancellation."],
    ["Case 3. Subscribed on every top-up, and is paying for all of them",
     "The same misunderstanding as Case 1, adding a subscription to every transaction, but the customer does not check their card statements. IDT charges several subscriptions to the same recipient and the customer pays for all of them.",
     "Confirmed. 1,387 groups, 6,175 subscriptions, 1,094 customers, with 3,469 surplus subscriptions that have taken 20,459 charges. Not cancelled, as instructed."],
]

GAPS = [
    ["Time between one subscription and the next in the same group", "Occurrences", "Share"],
    ["Under 1 minute", "1,158", "5.4%"],
    ["1 to 10 minutes", "1,578", "7.4%"],
    ["10 to 60 minutes", "561", "2.6%"],
    ["1 to 24 hours", "1,554", "7.2%"],
    ["1 to 7 days", "3,409", "15.9%"],
    ["7 to 30 days", "6,790", "31.7%"],
    ["More than 30 days", "6,399", "29.8%"],
    ["Total, median gap 12.2 days", "21,449", "100%"],
]

CASES = [
    ["Classification", "Groups", "Subscriptions", "Customers", "Reading"],
    ["Case 1. Subscribed on every top-up, then removed the card", "2,388", "12,892", "1,184",
     "The dominant story, and the only duplicate-creation story. Each subscription is its own purchase, then the card was pulled."],
    ["Case 2. Card on file but failing (no funds, declined, expired)", "1,957", "7,932", "1,435",
     "The card is still there, it simply does not pay. Largest case by customer count."],
    ["Case 3. Paying duplicates", "1,387", "6,175", "1,094",
     "Charging successfully today. Revenue, and the group we do not cancel."],
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
    ["Threshold", "First run", "Share", "Customers", "90% cleared", "Effectively done", "At risk of a wrong cancel"],
    ["Tiered: 3, or 2 for quarterly (chosen)", "19,846", "93.0%", "2,695", "first run", "26 weeks", "452"],
    ["Flat N = 3", "18,486", "86.6%", "2,588", "13 weeks", "39 weeks", "452"],
    ["Flat N = 4", "17,028", "79.8%", "2,427", "26 weeks", "52 weeks", "384"],
    ["Flat N = 5", "16,050", "75.2%", "2,303", "39 weeks", "65 weeks", "319"],
]

CLEAR = [
    ["Rule", "First run", "3 months", "6 months", "9 months", "12 months"],
    ["Tiered: 3, or 2 for quarterly", "93.0%", "96.3%", "99.9%", "100%", "100%"],
    ["Flat N = 3", "86.6%", "90.0%", "96.3%", "99.9%", "100%"],
    ["Flat N = 4", "79.8%", "83.5%", "89.9%", "96.3%", "99.9%"],
    ["Flat N = 5", "75.2%", "79.0%", "84.6%", "89.9%", "96.3%"],
    ["Tiered plus a 90-day calendar arm", "95.5%", "about 100%", "100%", "100%", "100%"],
]

FLOOR = [
    ["Component", "Tiered 3 / 2", "Flat N=3", "Flat N=5", "Why it is permanent"],
    ["Structural residue, subscriptions the rule can never reach", "4,314", "4,314", "4,314",
     "3,336 intermittent payers that fail then succeed inside two cycles, 580 too new to have launched, 398 failing with no future launch scheduled"],
    ["In-flight stock, failing but not yet at the threshold", "927", "1,149", "1,914",
     "New duplicates keep arriving; each waits out its cycles before the rule fires"],
    ["Permanent floor, 2026 inflow", "about 5,240", "about 5,460", "about 6,230", ""],
    ["Permanent floor, if inflow returns to the 2025 rate", "about 7,180", "about 7,870", "about 10,240",
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
    ["Both actively purchasing", "2,642", "Were double charging at the extract date"],
    ["Both awaiting first charge", "2,511",
     "Would have started double charging on their first cycle. 2,295 customers, $21,934 of position-2 value per cycle, now prevented."],
    ["Both failing", "1,018", "Neither collecting"],
    ["One active, one failing", "824", "Self-resolved, effectively"],
    ["Never launched", "10", ""],
]

K2CHARGED = [
    ["What happened to the pair", "Pairs"],
    ["Both subscriptions had collected at least once (the customer paid twice)", "2,773"],
    ["Both still charging successfully on 4 Sep", "2,642"],
    ["Neither had charged yet (would have charged twice on their first renewal; the fix stopped this)", "2,511"],
    ["Both failing, so no money taken", "1,018"],
    ["One charging, one failing (effectively a single charge)", "824"],
]

TABLES = [("POPS", POPS), ("GLOSS", GLOSS), ("CASEDEF", CASEDEF), ("CASES", CASES), ("GAPS", GAPS), ("FREQ", FREQ), ("CAUSE", CAUSE),
          ("AGE", AGE), ("THRESH", THRESH), ("CLEAR", CLEAR), ("FLOOR", FLOOR),
          ("TOPOWN", TOPOWN), ("GEO", GEO), ("K2STATE", K2STATE), ("K2CHARGED", K2CHARGED)]

# ---------------------------------------------------------------- blocks ----

B = [
    ("h1", "Duplicate IMTU subscriptions: what is in the file, and what the cleanup rules will actually do"),
    ("cap", f"Source: Copy of Duplicates Sep 18. Extract date 2026-09-04. Prepared 2026-09-18. Five tabs, 41,267 rows. Sheet: {SHEET}"),

    ("h2", "The short version"),
    ("p", "One of the two problems in this extract is already solved: the K2 double-fulfilment bug was fixed by backend in the week of 15 September 2026 and its records have been deleted. What remains is the behavioural backlog of 27,256 duplicate subscriptions, mostly dead and burning launch attempts, plus 1,094 customers quietly paying for duplicates. A tiered auto-cancel rule clears 93% of the dead backlog on its first run."),
    ("p", "Headline figures: 27,256 behavioural duplicates across 5,807 groups and 3,644 customers. 21,343 already failing, 78.3% of the file. 19,846 cancelled on the first run of the tiered rule, 93.0% of the failing backlog. 1,094 customers paying for 3,469 surplus subscriptions. A permanent floor of roughly 5,200 to 7,200 failing subscriptions once the rules reach steady state. The K2 double-fulfilment bug, previously running at 570 new pairs per week, is fixed and its 14,011 records deleted."),
    ("p", "The backlog divides into three customer cases, defined in full in the next section but worth naming here: Case 1, subscribed repeatedly then removed the card, 1,184 customers. Case 2, subscribed repeatedly and the card is still there but does not pay, 1,435 customers. Case 3, subscribed repeatedly and paying for all of them, 1,094 customers."),
    ("p", "Five things drive every recommendation in this document."),
    ("n", "The tiered rule works, and it is strictly better than a flat threshold. Three failures for weekly, biweekly and monthly subscriptions, two for quarterly, clears 93.0% of the failing backlog on the first run and finishes in six months instead of nine. Critically, it does this with no additional false-positive risk at all: the at-risk count is 452 either way."),
    ("n", "Case 1 is confirmed and is the single largest cause. 13,090 failing subscriptions carry a missing-card failure. 995 of the 1,285 customers involved have no working card left anywhere in the file. They did exactly what you described: they pulled the payment method to stop the charges."),
    ("n", "There is no accidental double subscription, so every duplicate is a deliberate repeat purchase. The purchase flow cannot subscribe twice within one top-up, so each subscription in a group is a separate top-up with the subscription option turned on. 12.8% of them were bought within ten minutes of the previous one and the median gap is 12.2 days, but the mechanism is identical at both ends of that range, which is why they sit in one case rather than two."),
    ("n", "Case 3 is real and it is 1,094 customers. They hold 3,469 surplus active subscriptions that have taken 20,459 charges, 1,835 of them in the last 30 days alone. No failure rule will ever touch these, by design."),
    ("n", "The K2 double-fulfilment bug is resolved and out of scope. Backend fixed it in the week of 15 September 2026 and the 14,011 affected records have been deleted. It was never a behavioural problem: those pairs shared a single transaction id, which the purchase flow cannot produce. The analysis below is now entirely about the behavioural backlog."),

    ("h2", "What is actually in the file"),
    ("p", "The spreadsheet contains two populations that barely overlap: they share only 221 subscriptions and 61 customers. Population B has since been fixed at source and deleted, so everything after this section concerns Population A alone. It is recorded here because the two were mixed together in the source file, and because the 221 shared rows mean Population A totals still include a small number of now-deleted records."),
    ("table", "POPS"),
    ("h3", "How the counting works"),
    ("p", "Three units appear in every table below and they are not interchangeable. One customer can hold many groups, and one group holds many subscriptions."),
    ("table", "GLOSS"),
    ("p", "So 27,256 subscriptions sit in 5,807 groups held by 3,644 customers, and those three numbers describe the same population at three levels of aggregation. When a table says 1,387 groups and 1,094 customers, it means some customers appear in more than one group."),
    ("p", "These figures are a lower bound. The source extract only includes groups of three or more subscriptions. A customer with exactly two identical subscriptions to the same number is a duplicate too, and is not in this file. The real duplicate population is therefore larger than 27,256, and the Case 3 cohort is larger than 1,094 customers. Every number in this document should be read as \"at least\"."),
    ("p", "A few more facts worth knowing before reading any number below. The canceled_at and canceled_reason columns exist and are blank on all 27,256 rows, which means a soft cancel is already supported by the schema and nothing has ever used it. Creation dates start on 2024-01-16, so nothing here predates 2024. And 8,722 creation timestamps, 32% of the file, are estimated rather than recorded, all of them older rows, so month-level history before 2025 is approximate."),
    ("p", "Exclude from behavioural analysis: a system event on 2025-12-19 created 1,122 subscriptions in two one-hour windows, up to 83 per minute, across 343 customers. That is a migration, not customer behaviour, and it is why December 2025 is the tallest month in the timeline. Removing it drops 349 groups below the three-subscription threshold entirely."),

    ("h2", "The three cases, measured"),
    ("p", "These are the three customer stories as you described them, each stated in full, with what the data says about it."),
    ("table", "CASEDEF"),
    ("p", "What happened to the original Case 1. Your original brief had a separate first case: the customer who bought several subscriptions without realising, then removed the card. That is not a mechanism that can exist, because the IMTU purchase flow has no way to subscribe twice inside a single top-up. Every subscription in a group is a separate, deliberate purchase with the subscription option turned on. Those groups were therefore folded into Case 1 above, and the case that was previously unnumbered, the card that is present but does not pay, has taken the free slot as Case 2."),
    ("h3", "How each group was classified"),
    ("p", "Every one of the 5,807 groups falls into exactly one row below. A group is Case 3 if it currently holds two or more subscriptions that are actively purchasing. Otherwise, if the majority of its failing subscriptions show a missing card it is Case 1; if the card is still present it is Case 2; and if nothing has launched yet it is counted as new, which is a residual bucket rather than a case."),
    ("table", "CASES"),
    ("p", "What the fast duplicates actually are. 2,736 subscriptions, 12.8%, were created less than ten minutes after the previous one in their group, and 1,158 of those less than a minute after. Because the flow cannot subscribe twice in one purchase, each of these is two separate top-up purchases minutes apart, both with the subscription option on, and 2,580 of the 2,736 were paid with the same card as the subscription before them. It is the same behaviour as the 30-day gaps, simply compressed: a customer buying two top-ups in one sitting, perhaps two different amounts or a retry after they thought the first had failed."),
    ("p", "That changes what the checkout guard has to do. It is not enough to check across days; R2 has to fire inside a single session, seconds after the previous purchase, because that is where an eighth of the backlog is created. It is also why the fast and slow versions sit together in Case 1: the behaviour is the same, only the spacing differs."),
    ("table", "GAPS"),
    ("p", "There is corroborating evidence for the Case 1 mechanism. 91.1% of later subscriptions with a recorded creation date had their first charge attempt 0.8 to 1.2 cycles after creation, which is the signature of a subscription created at a top-up checkout. And 51.2% of later subscriptions were created after an earlier sibling had already charged at least once, with 22.4% created while a sibling was still successfully purchasing."),

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
    ("p", "I simulated the tiered rule you specified against every failing subscription: cancel after three consecutive failures for weekly, biweekly and monthly subscriptions, and after two for quarterly ones. Consecutive failures are counted directly from the launch count for subscriptions that never charged, and estimated as the number of cycles between the last successful charge and the last attempt for the rest."),
    ("table", "THRESH"),
    ("p", "The tiering earns its keep on the quarterly subscriptions, which are 8,348 of the 21,343 failing backlog. At a flat three failures only 74.3% of them are eligible on the first run and the tail runs 276 days. At two, 90.6% are eligible immediately and the tail is 185 days."),
    ("p", "The tiering is free. Dropping quarterly subscriptions from three failures to two adds 1,360 cancellations on the first run and zero additional false-positive risk. The at-risk count is 452 under both rules. The reason is arithmetic: two missed quarterly cycles is already about six months without a successful charge, so no subscription that reaches the lower threshold has charged anyone recently. The usual trade-off between speed and safety simply does not apply here."),
    ("p", "\"At risk of a wrong cancel\" counts subscriptions that would be cancelled despite having completed a charge in the last 90 days, that is, intermittent payers. At 452 subscriptions that is 2.3% of the cancel set, and the 30-day grace check in R1a removes almost all of them."),
    ("p", "Optional refinement, if you want the last 7%. Adding a calendar arm on top of the tiered rule, cancel at the tiered threshold OR after 90 days launching without a single successful charge, whichever comes first, lifts the first run from 19,846 to 20,389, 95.5%. That is a smaller gain than it would have been against a flat rule, because the tiering has already captured most of what the calendar arm would catch. It is worth adding only if you want the residual quarterly tail gone in one pass rather than over six months."),

    ("h2", "How long, and what will always remain"),
    ("h3", "How long to clear the backlog"),
    ("table", "CLEAR"),
    ("p", "Read that as: the tiered rule removes 19,846 subscriptions in its first batch run, is at 99.9% by March 2027 and complete shortly after. The equivalent flat rule at three failures would still have been working through the quarterly tail in June 2027."),
    ("h3", "The minimum that will always be there"),
    ("p", "This is the question with the least clean answer, so here is the arithmetic rather than a single number. The permanent floor has two parts."),
    ("table", "FLOOR"),
    ("p", "The honest answer is a range of roughly 5,200 to 7,200 failing or failure-prone subscriptions permanently in the database under the tiered rule, and the position within that range is decided by product, not by the rule. The in-flight component is driven entirely by how many new duplicates get created: at the current 2026 rate of 309 new failing subscriptions per month it is about 927, and if creation returns to the 2025 rate it triples. The structural residue of about 4,300 does not move with the threshold at all, and about 3,336 of it is arguably not a problem: those are subscriptions that fail sometimes and succeed sometimes, which is normal for a card that occasionally lacks funds."),
    ("p", "The lever that actually moves the floor: the tiering moves it by about 220 against a flat three. Stopping duplicate creation at checkout moves it by up to 2,400, and it is the only thing that does. The rules clean up history; the purchase-flow fix is what stops the floor from being rebuilt."),

    ("h2", "Rules to build, beyond the failure counter"),
    ("p", "Ordered by value per unit of engineering effort. R1 is the rule you already proposed, tuned; R2 and R3 are the ones I would add first."),
    ("b", "R1. Soft cancel after 3 consecutive failures, or 2 for quarterly subscriptions. The tiered rule. Never delete: write canceled_at and canceled_reason, which already exist and are unused. Deleting destroys the audit trail and breaks the 18,758 purchase records that hang off these subscriptions. Clears 19,846 on the first run and all of it in about six months."),
    ("b", "R1a. Grace exemption: never cancel a subscription that charged successfully in the last 30 days. A one-line guard that removes essentially all of the false-positive risk in R1, protecting the 452 intermittent payers whose card occasionally lacks funds."),
    ("b", "R2. Duplicate guard at checkout: block a second subscription to the same number, offer and frequency. Now the highest-value item in this list, because with R3 shipped it is the only remaining rule that stops the backlog being rebuilt. If an active subscription already exists for that recipient and offer, do not create a second one. Offer \"you already have this subscription, change it instead\". This is the direct fix for Case 1, which is 2,388 groups and 12,892 subscriptions, and it prevents up to 2,400 of the permanent floor. It must apply within a single session as well as across days: 2,736 duplicates were created less than ten minutes after the previous one, so a guard that only checks yesterday's subscriptions misses an eighth of the problem."),
    ("b", "R3. Idempotency key on the checkout transaction id. SHIPPED. This was the fix for the K2 double-fulfilment bug and backend shipped it in the week of 15 September 2026. Listed here only so the rule set is complete and so the reasoning survives: two subscriptions were being created from a single transaction id a median 202 seconds apart, which is a retry after a timeout. Keep the idempotency check in place for any future change to the purchase path. It removed 14,011 records from the database."),
    ("b", "R4. Card-removal cascade: when the last card is removed, pause every subscription immediately. Today a customer removes their card and their subscriptions keep firing for a median of 328 days. 995 customers are in exactly this state. Pause on card removal, tell the customer what will happen, and offer to cancel. This would have prevented 9,823 of today's failures and saves about 4,950 launch attempts per week."),
    ("b", "R5. Cancel any subscription whose offer has been retired. These can never succeed regardless of the card. A deterministic, zero-judgement cleanup that should run before the failure-count rule so those subscriptions are cancelled with an accurate reason rather than a generic payment failure."),
    ("b", "R6. Warn the customer before cancelling, not after. Send a notification on the second consecutive failure: \"we could not charge your card for your top-up to +509...; it will be cancelled after the next failed attempt\". This recovers the customers who simply need to update a card, and it turns a silent cancellation into a service message. This is the rule that matters most for Case 2, the 1,435 customers whose card is still on file: they have not decided to leave, they just have a card that does not work. Recovery opportunity on 7,932 subscriptions across 1,435 customers."),
    ("b", "R7. Cap concurrent active subscriptions per recipient and offer at one. The structural version of R2, enforced at the subscription service rather than the UI, so no client and no retry path can create the second one. This is what prevents Case 3 from growing while you decide what to do about the existing paying duplicates."),
    ("b", "R8. Stop launching subscriptions that have no payment method at all. 9,823 subscriptions have no card on file and still fire on schedule. Suspend rather than attempt. This is pure waste: roughly 4,950 pointless attempts per week against the payment stack, and it will continue for the quarterly subscriptions for months even after R1 goes live."),
    ("h3", "Suggested sequence"),
    ("n", "R8 and R5 first. Deterministic, no customer impact, immediate load relief. Neither needs a release."),
    ("n", "R2 and R7 with the next app release. With R3 shipped, these are the only things that stop the backlog being rebuilt, and they set the permanent floor."),
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

    ("h2", "The K2 double-fulfilment bug, for the record"),
    ("p", "Closed. Backend fixed this in the week of 15 September 2026 and the affected records have been deleted from the database. No action is required and no cancellation rule applies. This section is kept only as a record of what the bug was and what it cost, because the source spreadsheet still contains these rows and anyone re-reading that file will find them."),
    ("p", "Two subscriptions shared a single transaction id, and since the purchase flow cannot subscribe twice within one purchase, these could only ever have been a system fault. The median gap between the two was 202 seconds, with 99.2% falling between two and five minutes, consistent with a server-side retry after a timeout. It was the one place in the file where a duplicate was not created by the customer."),
    ("p", "Scale before the fix: 7,005 pairs, 14,011 subscriptions, 5,955 customers, running at about 570 new pairs per week in the four weeks to 2026-09-07. 2,773 pairs had already double charged and 2,511 were about to, which the fix prevented."),
    ("table", "K2STATE"),
    ("p", "Revenue collected on the second subscription of a pair before the fix, where both collected: $25,230 USD plus 806 GBP, 838 CAD, 256 EUR and 23 AUD. Concentrated in Nigeria with 9,676 subscriptions and Venezuela with 3,622, and 97.9% on a monthly cycle. That is the scale of what was refundable or disputable, and it is worth a conversation with finance even though the subscriptions themselves are gone."),
    ("h3", "Were these customers charged twice?"),
    ("p", "Yes, some of them were. The customer's first purchase was only charged once. The double charges came at renewal, when both subscriptions in a pair tried to charge."),
    ("p", "These numbers come from the data extract of 4 September, before the fix went in:"),
    ("table", "K2CHARGED"),
    ("p", "That's 7,005 pairs across 5,955 customers in total."),
    ("p", "How much was overcharged: about $25,230, plus small amounts in other currencies (\u00a3806, C$838, \u20ac256, A$23). This is what the second subscription in each pair collected before the fix. Most of it was monthly subscriptions, mainly to Nigeria and Venezuela."),
    ("p", "One thing worth confirming with backend. The \"remove least revenue\" tab in the source file would have had no tie-break in 2,108 of the 2,773 paying pairs, 76%, where both subscriptions collected exactly the same amount, and in 13 cases it would have cancelled the active subscription and keep the failing one. If the deletion that has now run used that logic rather than \"keep the original\", it is worth checking that those 13 customers were not left with the failing side. That is a short query, not a project."),

    ("h2", "Method and limits"),
    ("b", "What was computed. The cases were renumbered on 18 September 2026. Product confirmed that the IMTU purchase flow cannot create two subscriptions from one purchase, so the original Case 1 (accidental double subscription) was merged into the original Case 2 and the pair became Case 1; the card-present failures, previously unnumbered, became Case 2; and the paying duplicates remain Case 3. That merge is why Case 1 counts 2,388 groups rather than the 2,159 of the earlier split. Every number came from the five tabs of the source sheet, read through the Sheets API and analysed in pandas. Seven independent analyses were run over the extract, and every headline number in this document was then re-derived a second time from the raw CSVs. Where the two passes disagreed, the re-derived number is the one shown: the day-one cancel count at N=3 is 18,486 and not 18,566, and the surplus charges in the last 30 days are 1,835 and not 1,746."),
    ("b", "Consecutive failures are partly estimated. For the 13,702 failing subscriptions that never charged, the count is the launch count, which is exact. For the 7,641 that charged and then went stale, it is the number of cycles between the last successful charge and the last attempt, which is an estimate. It can be wrong if a subscription was paused."),
    ("b", "Money is an estimate with stated coverage. Population A has no price column. See the note in the Case 3 section."),
    ("b", "Creation dates before 2025 are approximate. 8,722 of 27,256 creation timestamps, 32%, are reconstructed as the first launch minus one cycle."),
    ("b", "Clearance timing assumes every future attempt fails and that the rule runs daily from go-live on the extract date. Real clearance will be slightly slower, because some subscriptions will charge successfully once more and reset their counter."),
    ("b", "The December 2025 bulk event is included in totals but should be excluded from behavioural conclusions. 1,122 subscriptions created in two hours are a migration artefact."),
    ("b", "Population B is no longer in the database. The K2 records were deleted after the backend fix in the week of 15 September 2026. Its figures here describe the state at the 4 September extract and are kept for the record only. Population A totals include 221 subscriptions that overlapped with Population B and are therefore also gone."),
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
