#!/usr/bin/env python3
"""
Creates ONE Google Doc: "eGift Fraud Decisioning: DCS Project Plan".

The DCS-side plan for moving eGift fraud decisioning off IDT Pay and onto an
external vendor (nSure.ai or Riskified), following the eGift Fraud Vendor Review
meeting of 15 September 2026.

Three findings reframe the brief that came out of that meeting:

  1. IDT Pay's decisioning IS Accertify, a third-party vendor already contracted.
     There is no internal rules table to switch off, and at least four further
     gates decline an eGift purchase independently.
  2. 41.2% of eGift failures are issuer card declines that no fraud vendor can
     convert, and only 1.9% are velocity. Both vendors bill on total approved GMV.
  3. IDT disabled Visa on DTC eGift on 2026-08-28 (EGIFT-858) and never reverted
     it, inflating the current decline rate by about 7 points.

Figures re-run against Amplitude project 650506 (BR app Prod) on 2026-09-15.
Sources: Jira (DCS, ATF, AL, EGIFT, IDTPAY, BGW, BRS, RCS, BLNG) and Confluence
(DCS, DPC, TEAM, BOSS, BAC, TRCS, Fuji, AL spaces).

Companion HTML: eGift_Fraud_Vendor_DCS_Plan.html
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from linkify_refs import linkify, LINK_MAP

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

TITLE = "eGift Fraud Decisioning: DCS Project Plan"

WIKI = "https://idtjira.atlassian.net/wiki/spaces"

# Named sources cited below, so linkify turns the phrase into a real anchor.
EXTRA_LINKS = {
    "eGIFT in DTC: Anti Fraud Rules":
        f"{WIKI}/DCS/pages/3574890503/eGIFT+in+DTC+Anti+Fraud+Rules",
    "IMTU Wallet: Accertify Fraud Integration":
        f"{WIKI}/DCS/pages/5671944225/IMTU+Wallet+Accertify+Fraud+Integration+-DRAFT",
    "DTC Fraudzilla":
        f"{WIKI}/BAC/pages/3359408227/DTC+Fraudzilla",
    "ShieldWall 2.0":
        f"{WIKI}/DPC/pages/5720932375/ShieldWall+2.0",
    "Preliminary Design Review":
        f"{WIKI}/TEAM/pages/371037206/Preliminary+Design+Reviews+Architecture+Review",
    "PDR: MTU Fraud Detection with Terminus":
        f"{WIKI}/TEAM/pages/5673320464/PDR+MTU+Fraud+Detection+with+Terminus",
    "Kochava to AppsFlyer Migration":
        f"{WIKI}/TEAM/pages/6250987559/Kochava+AppsFlyer+Migration+Project+Hub",
    "Engineering Teams":
        f"{WIKI}/TEAM/pages/77546602/Engineering+Teams",
    "DCS Feature Flags":
        f"{WIKI}/DCS/pages/6091505685/Feature+Flags",
    "Inventory of Applications supported by CAF Team":
        f"{WIKI}/TEAM/pages/2853994971/Inventory+of+Applications+supported+by+CAF+Team",
    "Amplitude project 650506":
        "https://analytics.amplitude.com/boss/project/650506",
}
LINK_MAP.update(EXTRA_LINKS)

# ---------------------------------------------------------------- tables ----

# T1: the decline decomposition, Mar-Jul 2026
DECOMP = [
    ["Decline reason", "Count", "Share", "Can a fraud vendor convert it?"],
    ["Opaque \"failed\"", "1,475", "55.3%",
     "Unknown. This bucket is the upper bound of the addressable pool and nobody has split it."],
    ["Issuer card declines", "1,100", "41.2%",
     "No. Declined, no credit, invalid card, restricted, expired. These decline identically under any vendor."],
    ["Velocity or limit", "50", "1.9%",
     "Yes, but it is tiny. It fires as a seven-day incident response, not a standing constraint."],
    ["Other", "42", "1.6%",
     "No. Carrier, product and payment-verification failures."],
    ["Total", "2,667", "100%",
     "Measured 1 Mar to 31 Jul 2026, Visa enabled, no fraud episode."],
]

# T2: decline rate by window
WINDOWS = [
    ["Window", "Decline rate", "What contaminates it"],
    ["1 Mar to 31 Jul 2026", "89.9%",
     "Nothing. Use this as the baseline in the vendor business case."],
    ["1 to 24 Aug 2026", "89.1%",
     "Nothing. Visa still enabled, before the fraud episode."],
    ["25 to 31 Aug 2026", "72.9%",
     "The account farm being approved. 200 of August's 235 successes fall in these seven days. Exclude from any data pack."],
    ["1 to 15 Sep 2026", "96.1%",
     "Visa disabled on DTC since 28 August (EGIFT-858) and never reverted. About 7 points of this is IDT's own kill switch."],
]

# T3: the six gates on the critical path
GATES = [
    ["#", "Gate", "Target", "Compressible?"],
    ["G1", "Decline decomposition owned and published. Split the 55.3% opaque bucket to IDT Pay response codes and attribute every failure to a gate.",
     "30 Sep 2026", "Yes, it is a query"],
    ["G2", "PDR held, buy-versus-build resolved, vendor selected. The PDR process compels IDT Pay and CAF to attend as downstream dependencies.",
     "9 Oct 2026", "Yes"],
    ["G3", "nSure NDA executed, if nSure is selected. Riskified's is already executed and runs through 2028.",
     "+2 to 4 weeks", "No, and unpriced"],
    ["G4", "Pre-contract PII export approval and the outbound DPA. No process, template, register, owner or SLA exists anywhere at IDT.",
     "no known SLA", "Unestimated"],
    ["G5", "Contract plus DPA signed. This, not the vendor decision, unblocks production data flow.",
     "23 Oct (Riskified) / 20 Nov (nSure)", "No"],
    ["G6", "Advisory run plus chargeback label maturation. Internal fraud labels arrive about two weeks late; scheme chargebacks are slower.",
     "16 Nov to 25 Jan", "No, cannot compress"],
]

# T4: phases
PHASES = [
    ["Phase", "Window", "Goal", "Owner"],
    ["0. Baseline and the free lift", "15 Sep to 2 Oct 2026",
     "Replace the meeting-note figure with an owned, gate-attributed baseline, and recover the approval rate that costs nothing.",
     "DCS Backend, eGift Product"],
    ["1. Make the decision defensible", "15 Sep to 9 Oct 2026",
     "Convert an end-September preference into a PDR decision that survives architecture review, with IDT Pay and CAF in the room.",
     "DCS TPM drafts, VP Boss Revolution convenes"],
    ["2. Contracting, privacy and PCI", "9 Oct to 13 Nov 2026",
     "Reach signed contract plus DPA. Nothing downstream can be pulled forward by engineering effort.",
     "VP Boss Revolution signs, Compliance, BI"],
    ["3. Track A build, dev-only", "12 Oct to 27 Nov 2026",
     "Code-complete on a server-side vendor decision call with no dependency on an app store release.",
     "DCS Backend under the DCS Engineering Manager"],
    ["4. Production advisory run", "16 Nov 2026 to 25 Jan 2027",
     "Gather enough matured outcome data to make an enforcement decision that could actually be wrong. Minimum 8 weeks.",
     "DCS Backend and DCS TPM, Finance with Billing"],
    ["5. Enforcement ramp", "26 Jan to 9 Mar 2027",
     "Hand the vendor the decision, stand IDT Pay down for eGift, and reach full chargeback liability at 10 / 50 / 100 percent.",
     "DCS Backend with IDT Pay and CAF"],
    ["Track B (parallel, conditional)", "12 Oct 2026 to 5 Feb 2027",
     "Client SDK and the decline surface. Off the critical path unless the vendor cannot decision without device telemetry.",
     "DCS App bench of three, DCS Design"],
]

# T5: cross-team dependencies
TEAMS = [
    ["Team", "Jira", "What DCS needs from them", "By when"],
    ["IDT Pay (Core Services)", "IDTPAY",
     "Agreement to stand decisioning down for eGift, plus the PCI determination from the vendor field list. Without this, a vendor approval does not produce an approved transaction.",
     "9 Oct, at the PDR"],
    ["CAF (Compliance and Anti-Fraud)", "ATF",
     "The live eGift rule readout, the buy-versus-build position, the routing conditions owed on ATF-2527 since May, and the chargeback-rate definition.",
     "9 Oct, at the PDR"],
    ["AI Lab", "AL",
     "An honest answer on what has been delivered against AL-100. Do not take a dependency on its promote and rollback tooling: AL-474 and AL-475 are still in Triage.",
     "9 Oct, at the PDR"],
    ["Digital Payments Core", "DPC",
     "The K2 and ShieldWall decline contribution, and confirmation that K2 will not decline after a vendor approves.",
     "30 Sep, gate G1"],
    ["Billing", "BLNG",
     "Who files representments under a liability-shift model, and how vendor reimbursement reconciles. They have never been in this conversation.",
     "13 Nov"],
    ["Legal and Compliance", "CPL",
     "An outbound DPA where IDT is controller. No template, register, owner or SLA exists, and CPL will not originate this.",
     "2 Oct"],
    ["eGift Product", "EGIFT",
     "The Visa revert decision, the commercial eGift view, and the vendor thread itself.",
     "19 Sep"],
]

# T6: decision register
DECISIONS = [
    ["Decision", "Who decides", "By when", "Status"],
    ["Is the DTC Visa disable reverted, and when? Off for 18 days with no owner and no revert ticket. Worth about 7 points, and it costs nothing.",
     "Diana Scolari with Emilio DelRio", "19 Sep 2026", "Unowned"],
    ["Who owns the decline decomposition, and by what date? Write the deliverable into the ticket's Acceptance Criteria field, not into a meeting.",
     "Ana Jishkariani assigns", "18 Sep 2026", "Unowned"],
    ["Does the vendor decision go through a PDR, and who are the approvers? It triggers the process on three independent grounds.",
     "Emilio DelRio convenes", "23 Sep 2026", "Not raised"],
    ["Does the vendor require mobile SDK telemetry, or can it decision server-side? A wrong answer re-dates everything by 10 to 14 weeks.",
     "Vendors in writing; Yuri Rykovsky arbitrates", "2 Oct 2026", "Not asked"],
    ["Does either vendor ship a Flutter plugin? Both quote native or React Native. The BR app is neither.",
     "DCS App lead with Yuri Rykovsky", "2 Oct 2026", "Not asked"],
    ["Who approves the pre-contract PII export, and what is the turnaround? It gates Riskified's rate, which gates the contract.",
     "Compliance with Legal", "2 Oct 2026", "No process"],
    ["Buy versus finish building. Does a vendor supersede, bridge or coexist with ATF-2265, AL-100 and FY2026 board goal 9?",
     "Emilio DelRio with CAF and AI Lab", "9 Oct 2026", "Never framed"],
    ["nSure or Riskified, judged against the decomposed baseline rather than the meeting-note figure.",
     "Emilio DelRio with Yuri Rykovsky and CAF", "9 Oct 2026", "In progress"],
    ["Is the scope DTC eGift only, or retail too? This changes the GMV base the 1 percent is charged against.",
     "Emilio DelRio with eGift Product and RCS", "9 Oct 2026", "Unstated"],
    ["Binary decision only, or build hold-and-resume for a review verdict? eGift has no async review or transaction hold today.",
     "Yuri Rykovsky with CAF", "9 Oct 2026", "Unstated"],
    ["Fail-open or fail-closed on vendor timeout? On a percentage-of-approved-GMV model this is a contract term, not a default.",
     "Yuri Rykovsky with CAF and Legal", "27 Nov 2026", "Open since June"],
    ["Who books eGift chargebacks and owns representments?",
     "Finance with BLNG", "13 Nov 2026", "Unowned"],
    ["Pilot duration, thresholds, approvers and rollback SLA, agreed before any production traffic.",
     "Emilio DelRio names approvers", "6 Nov 2026", "Not started"],
    ["Does re-enabling Visa plus relaxing the limits recover enough that the vendor is not needed? The honest control arm.",
     "Emilio DelRio, on the Phase 0 evidence", "9 Oct 2026", "Phase 0 answers it"],
]

# T7: risks
RISKS = [
    ["Risk", "Mitigation", "Owner"],
    ["The vendor is bought to fix declines it cannot move. 41.2 percent of failures are issuer declines and velocity is 1.9 percent, yet both vendors bill on total approved GMV. At a 3 percent take rate a 1 percent fee eats a third of gross margin on every approved transaction.",
     "Do not sign a percentage-of-approved-GMV contract until the opaque bucket is split by IDT Pay response code. State the addressable pool as a bounded range. Price the fee against the whole approved base.",
     "DCS TPM, VP Boss Revolution"],
    ["Vendor approval does not produce an approved transaction. eGift declines at up to five independent gates and a vendor replaces at most two. BGW-9535 is live proof: a transaction accepted by Sardine still failed at antifraud.",
     "Make the IDT Pay stand-down a functional exit criterion of Phase 3, verified before the pilot. Inventory K2-sourced declines first. Define \"approved\" contractually and build an independent count.",
     "DCS Backend with IDT Pay"],
    ["The pilot reads out on a metric that structurally cannot have gone wrong yet. A four-week pilot declares victory on approval rate having seen none of the fraud it let through. ATF-2801 documents the realised downside at roughly $70K.",
     "Minimum eight weeks of live advisory traffic. A pending-label state on every record from day one. Read-out date separated from traffic-stop date. Thresholds and approvers agreed before the pilot starts.",
     "DCS TPM, approvers named at the PDR"],
    ["The liability transfer does not cover the fraud that caused the clampdown. The documented eGift vector is account takeover on the genuine cardholder's own saved card, which commonly falls outside standard fraud-liability cover.",
     "Put the exact DCS-3472 scenario to both vendors in writing before signature. It may be the difference between the 1 and 1.5 percent tiers, and it may be excluded by both.",
     "VP Boss Revolution with Legal"],
    ["Buy-versus-build is never resolved and the decision is reopened at architecture review, cutting across a live FY2026 board commitment.",
     "Route the decision as a PDR. Put the single outstanding ask to Mark Moorman in writing with a date. Note that the Terminus PDR carries no accepted status and eGift has zero delivery tickets in ATF.",
     "VP Boss Revolution, DCS TPM"],
    ["The kill switch cannot ship when it is needed. eGift has no feature flags at all, and a native SDK starts before Dart on Android and at plugin registration on iOS, so a remote flag cannot stop it in the current launch.",
     "Keep the decision server-side, where the call site is ours and disables instantly. If the vendor requires SDK telemetry, say so at the PDR and re-date there rather than in December.",
     "Yuri Rykovsky, DCS App lead"],
    ["A scoping mistake degrades IMTU or eSIM. All three share one payment path and one admin surface, so the eGift rule change is made on the screen that governs IMTU velocity rules.",
     "Per-product config already shipped, so the carve-out is config not code. Four-eyes review, a change window, a captured pre and post diff of IMTU rule state, and IMTU regression as a Phase 3 exit criterion.",
     "DCS Backend with CAF"],
    ["Approval-rate gains do not convert into completed purchases. The customer sees generic decline text with no reason and no retry path.",
     "Put decline copy and a retry path in Track B with a named design owner. Measure completed purchases in the charter, not approval rate alone.",
     "DCS Design and DCS App"],
    ["The client workstream lands unbudgeted on a bench of three Flutter developers already carrying IMTU subscriptions. ATF-2666 has run 67 days and is still not enforcing.",
     "Get the Flutter answer in writing before the decision and keep Track B off the critical path. Require a measured bundle and cold-start delta from a real build before signature.",
     "DCS App lead with Yuri Rykovsky"],
]

# T8: Jira scaffold
JIRA = [
    ["Epic", "Tickets"],
    ["1. eGift decline baseline and decision instrumentation (Phase 0)",
     "[BE] Resolve the opaque eGift failed_reason bucket to IDT Pay response codes / "
     "[BE] Obtain the eGift TransServiceId and Owner value and isolate eGift in the idtpay statusChange stream / "
     "[BE] Read and publish the live Fraudzilla eGift velocity and limit rule set / "
     "[BE] Baseline the ShieldWall and K2 decline contribution separately from IDT Pay / "
     "[TPM] Publish the eGift decline decomposition for 1 Mar to 31 Jul 2026, split by gate / "
     "[TPM] Revert or confirm the DTC Visa disable from EGIFT-858 and measure over two weeks / "
     "[TPM] Confirm the retention window for eGift decline events before promising a win-back audience / "
     "[QA] Verify decline-reason instrumentation end to end on the eGift purchase path"],
    ["2. eGift fraud decisioning: the decision pack (Phase 1)",
     "[TPM] Publish the eGift fraud decisioning PDR in the TEAM space and convene the architecture review / "
     "[TPM] Record the cross-org decision owner and approver set for removing eGift decisioning from IDT Pay / "
     "[TPM] Obtain written CAF and AI Lab positions on whether a vendor supersedes, bridges or duplicates ATF-2265 and AL-100 / "
     "[TPM] Put the account-takeover pattern from DCS-3472 to both vendors and obtain the liability category in writing / "
     "[TPM] Obtain each vendor's Flutter position, decision enum and required field list in writing / "
     "[TPM] Confirm whether a DTC web eGift purchase flow exists before weighting web against native / "
     "[BE Spike] Confirm the fraud decision call site for the DTC eGift purchase path / "
     "[BE Spike] Confirm eGift can be scoped out of the IDT Pay Accertify call by product type"],
    ["3. Server-side integration, Track A (Phase 3)",
     "[BE] Add the vendor decision call to hdm-go-payment-int-api behind a product-scoped server switch / "
     "[BE] Map the vendor verdict enum onto the existing anti_fraud status contract / "
     "[BE] Implement the agreed fail-open or fail-closed behaviour for vendor timeout and outage / "
     "[BE] Scope IDT Pay Accertify decisioning off eGift by product type, with a rollback runbook and an IMTU rule-state diff / "
     "[BE] Implement the vendor outcome and chargeback feed with a per-chargeback reconciliation assertion / "
     "[BE] Replay historical eGift declines against the vendor score and join to realised outcomes / "
     "[BE] Produce an IDT-side independent count of approved eGift transactions and approved GMV / "
     "[BE] Build the eGift fraud Grafana board: approval rate, decline reason, latency, vendor availability / "
     "[QA] Regression: prove IMTU and eSIM decisioning is unchanged with the eGift switch on and off / "
     "[QA] Verify no shadow verdict reaches the decline path, including on retry and queued messages"],
    ["4. Client signals, kill switch and decline UX, Track B",
     "[APP] Decide and document whether the vendor SDK replaces, wraps or duplicates the risk_signals package / "
     "[APP] Add the eGift fraud vendor remote config switch with legacy IDT Pay decisioning as the compiled default / "
     "[APP] Propagate the vendor session or device token on the eGift purchase request / "
     "[APP] Measure the all-ABI Android bundle delta and cold-start delta on a real build / "
     "[APP] Surface actionable eGift decline messaging and a retry path / "
     "[DESIGN] eGift decline and retry copy for a purchase refused on risk / "
     "[DESIGN] Google Play pre-SDK disclosure screen for any new data classes / "
     "[QA] Verify the kill switch defaults to legacy decisioning when remote config fails to load / "
     "[QA] Physical-device pass on both apps for the vendor SDK"],
    ["5. Advisory pilot, ramp and rollback (Phases 4 and 5)",
     "[TPM] Agree and publish the pilot duration, thresholds and named approvers before any traffic / "
     "[BE] Run the vendor as a non-decisive scored input recorded alongside the live decision / "
     "[TPM] Publish the agreement matrix of vendor verdict against IDT verdict against realised outcome / "
     "[BE] Rollback runbook and a deliberate production rollback exercise / "
     "[BE] Execute the enforcement ramp at 10, 50 and 100 percent with a per-step approval hold / "
     "[QA] Regression per enforcement ramp step across eGift, IMTU and eSIM"],
    ["6. Liability, reconciliation and compliance (Phases 2, 4 and 5)",
     "[TPM] Obtain written approval and an SLA for exporting eGift transaction data to a pre-contract vendor / "
     "[TPM] Execute the outbound data processing agreement with IDT as controller / "
     "[TPM] Obtain the vendor field list and a written PCI scope determination from the IDT Pay PCI owner / "
     "[TPM] Assign a named iOS App Privacy owner and a named Play Data Safety owner per app / "
     "[TPM] Define representment ownership and chargeback reconciliation with the Billing team / "
     "[TPM] Obtain contractual auditor access to per-transaction vendor decision records and their retention / "
     "[TPM] Confirm whether outsourcing card-fraud decisioning creates any obligation for IDT Payment Services / "
     "[BE] Confirm the automatic chargeback blacklisting process fires for eGift transactions"],
]

TABLES = [
    ("T1", DECOMP), ("T2", WINDOWS), ("T3", GATES), ("T4", PHASES),
    ("T5", TEAMS), ("T6", DECISIONS), ("T7", RISKS), ("T8", JIRA),
]

# ---------------------------------------------------------------- content ---

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Prepared for Emilio del Rio  ·  15 September 2026  ·  Scope: DTC eGift, Boss Revolution app  ·  Sources: Jira, Confluence and Amplitude project 650506"),

    ("p", "What DCS has to do to hand eGift fraud decisioning to an external vendor, what it must settle before signing anything, and why the six-week integration estimate is not the number that sets the date."),

    ("h2", "Three corrections before the plan"),
    ("p", "The vendor review is real and the channel is genuinely blocked. But the brief that came out of the meeting contains three factual errors, and each one changes what DCS should build, what it should pay, and when it can be live."),

    ("h3", "1. There is no IDT Pay rules table to switch off, and IDT Pay is only one of at least five gates"),
    ("p", "IDT Pay's fraud decisioning is Accertify, a third-party vendor already contracted, adapter-built and PCI-integrated, called from inside IDTPay. The documented chain is mtu-int-api to payment-int-api to IDTPay to Accertify, per IMTU Wallet: Accertify Fraud Integration."),
    ("p", "Four further gates decline an eGift purchase independently: Fraudzilla velocity rules, which DCS and DTC own and IDT Pay does not (see DTC Fraudzilla); Jube, which surfaces as \"Error 59\"; K2's own velocity and location screens; and ShieldWall on the Zendit rails, which fails closed on timeout (see ShieldWall 2.0)."),
    ("p", "This is not academic. BGW-9535 is a live production defect titled \"Transaction which was accepted by Sardine, still failed at antifraud\". A vendor approval does not produce an approved transaction while a second gate still runs. Standing IDT Pay down for eGift is a functional requirement of this project, not a courtesy."),

    ("h3", "2. 41 percent of eGift failures are issuer declines no fraud vendor can convert"),
    ("p", "Over the clean window 1 March to 31 July 2026, 41.2% of eGift failures carry an issuer-side card decline. Those decline identically under nSure or Riskified. Only 1.9% carry a velocity or limit code. The remaining 55.3% is the opaque literal \"failed\", which is where the addressable pool lives and which nobody has split."),
    ("p", "Both vendors bill on total approved GMV, not on incremental approvals. Gift cards run a roughly 3 to 8 percent merchant commission, so a 1 percent fee consumes between one eighth and one third of gross margin on every approved transaction, including the ones IDT was already approving. At the low end of that band the choice between the 1 percent and 1.5 percent tiers is material, not a rounding difference. Finance needs a sensitivity table over take rate and approval lift, not a point estimate."),

    ("h3", "3. IDT switched Visa off on DTC eGift 18 days ago and never reverted it"),
    ("p", "EGIFT-858, description \"Disable Visa in DTC\", was created and closed within 61 seconds on 28 August 2026. There is no revert ticket, no review date and no owner. It inflates the current decline rate by about 7 percentage points: 89.1% in the fortnight before, 96.1% in the fortnight after."),
    ("p", "Separately, 85 percent of August's successes fall inside 25 to 31 August, the documented account-farm window (BRS-56097), where the decline rate fell to its yearly low because fraud was being approved. If that month goes into Riskified's six-month pricing pack unflagged, IDT hands over a window whose approvals are disproportionately fraudulent and gets a worse rate quoted back."),

    ("h2", "The verified numbers"),
    ("p", "All figures below were re-run against Amplitude project 650506 on 15 September 2026, not taken from the meeting notes. The premise survives: the channel really is blocked, at 89.9% decline in a clean window. What does not survive is the assumption that a fraud vendor addresses most of it."),
    ("table", "T1"),
    ("p", "Fraud never appears as a decline reason by design: DCS-5412 records that no decline code is mapped to Fraud. So gate attribution cannot come from failed_reason alone. It has to come from the IDT Pay response code, which is exactly what Phase 0 commissions."),
    ("table", "T2"),
    ("p", "Quote 89.9% as the baseline. Never quote a September number."),

    ("h2", "What actually sets the date"),
    ("p", "\"Decision end of September, pilot promptly, up to six weeks of integration\" is counted from the wrong event and against the wrong long pole. The gates below run in series. Three of them cannot be compressed by adding engineers, and the integration is not one of them."),
    ("table", "T3"),
    ("p", "First honest date on which \"eGift approval rate improved in production because of the vendor\" can be claimed: 9 March 2027 on the enforcement ramp, assuming Riskified and no slip at G4. The mobile app release train is deliberately not on this list, which is the point of the two-track split."),

    ("h2", "Two tracks"),
    ("p", "Put the decision server-side and the app store never sits on the critical path. Put it in an SDK and the schedule is hostage to a release train that already closed for September."),
    ("b", "Track A, the pilot path  ·  Call the vendor from hdm-go-payment-int-api, scoped to eGift by product type. This has a shipped reference implementation: DCS-3949 put Accertify behind wallet transactions from exactly this service. No app release, no store review, no train dependency, and the kill switch is our own config so it reverts instantly. The per-product carve-out already shipped and was verified in DCS-3472, so IMTU and eSIM need not be touched."),
    ("b", "Track B, parallel and conditional  ·  The vendor mobile SDK and the decline surface. This only becomes the critical path if the vendor cannot decision acceptably without device telemetry, and if it does the whole plan re-dates by roughly 10 to 14 weeks. Get that answer in writing before the decision. Note that the BR app is a single Flutter monorepo and neither vendor was stated to ship a Flutter plugin, that eGift has no feature flags at all today, and that ATF-2666 records that a native fraud SDK starts before Dart on Android and at plugin registration on iOS, so a remote flag cannot stop it in the launch where you need it."),

    ("h2", "The plan"),
    ("p", "Sprint 77 (id 38431) runs 9 to 22 September and Sprint 78 (id 38502) runs 23 September to 6 October. Both are real. Sprint 79 onward do not exist in Jira yet and their ids are not derivable, so every date after 6 October is a projection on the verified 14-day cadence and the ids must be looked up when the board is extended."),
    ("table", "T4"),

    ("h3", "Phase 0 exit criteria, the phase most likely to be skipped"),
    ("n", "A named owner and a dated Jira ticket exist, with the deliverable written into the Acceptance Criteria field rather than promised in a meeting. The December 2025 incident review closed with Root Cause blank and this same measurement owed and undelivered."),
    ("n", "All 2,667 failures in the clean window are attributed across Fraudzilla, Jube, IDT Pay and Accertify, K2 and ShieldWall."),
    ("n", "Visa is re-enabled, or a written decision not to re-enable exists with a named owner and a review date."),
    ("n", "A baseline data pack exists with 25 to 31 August flagged as an excluded incident window and the EGIFT-858 Visa disable labelled on the timeline."),
    ("n", "The addressable pool is stated as a bounded range, never a point estimate, with the issuer-decline share explicitly excluded as unconvertible."),

    ("h3", "Eight questions both vendors must answer in writing"),
    ("p", "None of these are in either vendor deck."),
    ("n", "Flutter. The BR app is a Flutter monorepo, not native and not React Native. Is there a plugin, or is a wrapper unbudgeted DCS work?"),
    ("n", "Account takeover. The documented eGift vector is SMS-code phishing against the genuine cardholder's own saved card (DCS-3472). ATO commonly falls outside standard fraud-liability cover, so get the category confirmed. This may be the whole difference between the 1 percent and 1.5 percent tiers, and it may be excluded by both."),
    ("n", "Decision enum. Binary only. eGift has no async review or transaction hold, and CHALLENGE is documented as unsupported for exactly that reason."),
    ("n", "Which layer does the vendor replace: Fraudzilla velocity, the IDT Pay and Accertify card decision, or both? If only the card decision, the channel stays blocked after go-live."),
    ("n", "Fail-open or fail-closed on vendor timeout, and are fail-open approvals indemnified? On a percentage-of-approved-GMV liability model this is a contract term, not an engineering default."),
    ("n", "The exact field list, so PCI scope can be determined. BIN, last four and expiry are cardholder data even though they are not a full PAN."),
    ("n", "The definition of \"approved\" for billing, given K2 can decline after the vendor approves."),
    ("n", "Auditor access and retention of per-transaction decision records. BDO is sampling fraud decision evidence right now, and this term is very hard to add after signature."),

    ("h2", "Who has to be in the room"),
    ("p", "DCS owns detection, never decisioning. That boundary is why this cannot sit inside DCS alone, and it is also the strongest internal evidence for the business case: IDT's own fraud alerting ticket, DCS-5350, documents that no control fired on a live attack."),
    ("table", "T5"),

    ("h2", "Decision register"),
    ("p", "Nothing in this table has an owner today."),
    ("table", "T6"),

    ("h2", "Risks worth the room's attention"),
    ("table", "T7"),

    ("h2", "Jira scaffold"),
    ("p", "There is no epic, no spike, no spec page and no sprint slot for any of this. A site-wide search returns zero Jira issues and zero Confluence pages for either vendor, and the only tracking artefact is EGIFT-861, an empty Open task sitting beside gift-card supplier sourcing tickets. Nothing is on the DCS board, so nothing will be groomed for the October train unless it is created now."),
    ("p", "Create these in DCS, not EGIFT: the EGIFT project has no epic structure and no engineering team behind it. Link every epic to DCS-5238, DCS-5350, EGIFT-861, ATF-2265 and AL-100, so the dependencies appear in the linked-issues panel rather than in a description."),
    ("table", "T8"),
    ("p", "Per the DCS ticket conventions: Acceptance Criteria goes in its dedicated field on every story, Design tickets get Story Points 0 and go to Viktoryia Shmidt, TPM tickets get Story Points 0, and BE and App tickets leave Story Points empty for grooming. No placeholders anywhere: where a spec or Figma link does not exist yet, omit the line rather than writing TBD."),

    ("h2", "What could not be verified"),
    ("b", "\"Anna\" and \"Edvard\"  ·  Neither name in the meeting notes could be matched. Three Annas exist at IDT and none works in payments fraud; the most likely reading, and it is an inference not a finding, is Ana Jishkariani, the DCS TPM. \"Edvard\" matches no Jira user at all. Diana Scolari holds the only vendor-evaluation ticket. Confirm both with the meeting owner before assigning action items."),
    ("b", "The Riskified NDA  ·  Described as executed with IDT Payment Services and active through 2028, but the date is inconsistent between the brief and the deck, and the executed copy is not discoverable in any system of record. An NDA nobody can produce is not a cleared gate."),
    ("b", "The DTC web surface  ·  It is unconfirmed whether a DTC web eGift purchase flow exists at all today. If there is no web surface, nSure's JavaScript-snippet advantage is worth nothing for eGift and the comparison changes materially. Ask Katsiaryna Bialevich."),
    ("b", "Accertify's scope  ·  The DCS integration page implies the card-fraud chain covers eGift; the Inventory of Applications supported by CAF Team lists Accertify's line of business as Money Transfer only. Both cannot be true, and the answer determines what a vendor actually replaces. This is a question for the IDT Pay team, not for either vendor."),
    ("b", "Sprint ids  ·  Sprints 79 and beyond do not exist in Jira and their ids are not derivable, because ids are non-sequential (74 is 34336 but 76 is 37582). Every date after 6 October is a projection."),
    ("b", "eGift GMV  ·  The eGift DTC approved GMV figure does not exist anywhere in Confluence, so the break-even model cannot be built from it. Three numbers must be sourced before any contract: trailing twelve-month approved GMV and transaction count, the same for declined attempts split by decline source, and the current realised chargeback and fraud-loss rate on approved eGift."),
    ("b", "A security note  ·  Unrelated to this decision: the Confluence page IMTU Wallet: Accertify Fraud Integration contains what appear to be plaintext service credentials in its example XML payload, on an instance-readable page. Worth reporting to security and the page owner for rotation and redaction."),

    ("h2", "If only one thing happens this week"),
    ("p", "Assign the decline decomposition to a named DCS backend engineer with a date, and put the deliverable in the ticket's Acceptance Criteria field. That measurement has been owed since the December 2025 incident review, which closed with Root Cause blank and the affected transaction count recorded as still to be determined. An unowned, undated spike will repeat that exactly."),
    ("p", "Then decide whether Visa goes back on. It has been off for 18 days with no owner and no review date, it is worth about seven points of approval rate, it costs nothing, and it beats any vendor to production by roughly five months. It is also the control arm the room needs in order to judge the vendor case honestly."),
    ("p", "The most likely way this plan fails is not a missed date. It is that the end-September deadline is taken at face value, a vendor is selected against the meeting-note figure, and IDT discovers in February 2027 that 41 percent of the declines were issuers saying no, and much of the rest was a kill switch nobody reverted plus a hand-maintained limit set that drifted conservative and was never tuned back. Phase 0 is the cheapest phase in this document and the easiest one to skip."),

    ("cap", "Figures re-run 15 September 2026. Sprint and status data will drift, so re-check before committing scope."),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}

# Status words in the decision register, coloured so the unowned rows stand out.
TAG_COLOR = {
    "Unowned":            (0.70, 0.23, 0.12),
    "No process":         (0.70, 0.23, 0.12),
    "Never framed":       (0.70, 0.23, 0.12),
    "Not raised":         (0.70, 0.23, 0.12),
    "Not asked":          (0.60, 0.43, 0.08),
    "Unstated":           (0.60, 0.43, 0.08),
    "Not started":        (0.60, 0.43, 0.08),
    "Open since June":    (0.60, 0.43, 0.08),
    "In progress":        (0.29, 0.25, 0.72),
    "Phase 0 answers it": (0.05, 0.48, 0.42),
}

LEAD_SEP = "  ·  "


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


def ulen(text):
    """Docs indices count UTF-16 code units, not Python characters."""
    return len(text.encode("utf-16-le")) // 2


def build_requests(blocks):
    reqs, cur = [], 1
    for kind, text in blocks:
        if kind == "table":
            line = f"[[{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += ulen(line)
            continue

        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        para = {"namedStyleType": STYLE_MAP[kind]}
        fields = "namedStyleType"
        if kind == "cap":
            para["alignment"] = "CENTER"
            fields += ",alignment"
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + ulen(line)},
            "paragraphStyle": para, "fields": fields}})

        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind == "n":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(line)},
                "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"}})
        if kind == "cap":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(text)},
                "textStyle": {"italic": True,
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}})
        if kind in ("b", "p") and LEAD_SEP in text:
            lead = text.split(LEAD_SEP)[0]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + ulen(lead)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        cur += ulen(line)
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


def insert_table(docs, doc_id, marker, data):
    """Replace the [[marker]] placeholder with a real Docs table."""
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = plen = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[{marker}]]":
            idx, plen = el["startIndex"], ulen(para_text(el))
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
    for start, r, c in sorted(cells, reverse=True):   # reverse keeps indices valid
        txt = data[r][c]
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + ulen(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        elif txt in TAG_COLOR:
            red, green, blue = TAG_COLOR[txt]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + ulen(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": red, "green": green, "blue": blue}}}},
                "fields": "bold,foregroundColor"}})
        elif marker == "T8" and c == 1:
            # The ticket lists are long; set them smaller and monospaced so the
            # epic name column stays readable next to them.
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + ulen(txt)},
                "textStyle": {"fontSize": {"magnitude": 8, "unit": "PT"},
                              "weightedFontFamily": {"fontFamily": "Roboto Mono"}},
                "fields": "fontSize,weightedFontFamily"}})
        elif marker in ("T1", "T2", "T3") and c in (1, 2):
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + ulen(txt)},
                "textStyle": {"weightedFontFamily": {"fontFamily": "Roboto Mono"},
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "fontSize,weightedFontFamily"}})
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

    # Every Jira key and named source becomes a clickable link.
    linkify(docs, doc_id)

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
