#!/usr/bin/env python3
"""
Creates ONE Google Doc: "Digicel Top-Up Cancellation — Retention Teardown & BOSS Revolution Recommendation".

Competitive teardown of the cancellation and retention experience for Digicel's
recurring top-up products, and a recommended end-to-end IMTU subscription
cancellation flow for BOSS Revolution.

SCOPE NOTE carried prominently in the document: no cancellation was performed
and no account was created. Digicel's cancellation UI sits behind a login. The
retention dialog documented here was recovered by reading Digicel's shipped
production JavaScript, not by walking the flow.

Method: 8 parallel research passes reconciled against 4 adversarial verification
passes. The brief's central premise (that Digicel runs a sophisticated retention
flow worth copying) did not survive, but not in the direction first expected —
see Section 1.

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

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"
RAW_BASE = "https://raw.githubusercontent.com/tanaka-idt/IDT-Claude/main/"

TITLE = "Digicel Top-Up Cancellation — Retention Teardown & BOSS Revolution Recommendation"

DIGICEL_LINKS = {
    "topup.digicelgroup.com/en/faq/": "https://topup.digicelgroup.com/en/faq/",
    "topup.digicelgroup.com": "https://topup.digicelgroup.com",
    "Minn. Stat. §325G.58": "https://www.revisor.mn.gov/statutes/cite/325G.58",
    "Cal. Bus. & Prof. Code §17602": "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240AB2863",
    "FTC v. Vonage": "https://www.ftc.gov/news-events/news/press-releases/2022/11/ftc-action-against-vonage-results-100-million-customers-trapped-illegal-dark-patterns-junk-fees-when-trying-cancel-service",
    "FTC v. Amazon": "https://www.ftc.gov/news-events/news/press-releases/2025/09/ftc-secures-historic-25-billion-settlement-against-amazon",
    "chart dsyei9ee": "https://app.amplitude.com/analytics/BOSS/dashboard/dsyei9ee",
    "chart gb7jgqqz": "https://app.amplitude.com/analytics/BOSS/chart/gb7jgqqz",
    "dashboard bx3h416b": "https://app.amplitude.com/analytics/BOSS/dashboard/bx3h416b",
}

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Competitive teardown and flow recommendation · Prepared 30 August 2026 · DCS / IMTU · "
            "Public sources plus production code inspection · No cancellation performed"),

    # ------------------------------------------------------------ 1 ----
    ("h2", "1. Executive summary"),

    ("p", "This document examines how Digicel treats a customer who tries to cancel a recurring top-up, "
          "and recommends an IMTU subscription cancellation flow for BOSS Revolution."),

    ("h3", "The brief's premise did not survive, but not in the way expected"),
    ("p", "The brief assumed Digicel runs a sophisticated retention flow worth learning from. It does not. "
          "But nor is the flow the bare delete its own documentation describes."),
    ("p", "Digicel's published help centre says cancellation ends at a trash icon. That is incomplete. Reading "
          "the shipped production JavaScript for the Recurring Payments screen shows the trash icon opens a "
          "dialog, and that dialog has two variants behind a live feature flag. The control arm is an ordinary "
          "confirmation. The test arm is a loss-framed benefit reminder — the only retention intervention "
          "Digicel operates at the cancellation moment."),
    ("p", "Of sixteen retention mechanisms checked, two are present. Fourteen are absent. And the mechanisms "
          "that are missing are missing architecturally rather than by choice: the API exposes only GET and "
          "DELETE for recurring payments, with no PUT or PATCH anywhere in the bundle. Digicel could not ship "
          "a pause or a downgrade offer without building new endpoints first."),

    ("h3", "The finding BOSS Revolution should actually take away"),
    ("p", "Digicel cannot measure the experiment it is running. The retention dialog fires no event when it is "
          "shown, and the “Keep my Advantages” button is wired to close the dialog and nothing else. The only "
          "two events in the flow are one when the dialog opens and one when deletion succeeds. There is no "
          "exposure count and no save count, so the outcome the test exists to measure emits nothing at all. "
          "Session recording is disabled globally across the site and switched on for this one flow — which "
          "reads like a team watching replays because their analytics cannot answer the question."),
    ("p", "This matters because BOSS Revolution would be shipping into a worse measurement position. Renewal "
          "charges emit no app event, notification-service messages are untracked, post-GA A/B events carry no "
          "variant tag, and the cancellation event has no reason property. Building a save flow before fixing "
          "that would reproduce Digicel's mistake with less instrumentation to start from."),

    ("h3", "Where Digicel does spend retention effort — and it is not at cancellation"),
    ("p", "Digicel's genuine retention investment sits upstream of the cancel intent. Its app home screen "
          "carries a “Renew before it's too late” card with a “3 DAYS REMAINING” urgency badge and a “Renew "
          "Now” button, inside a rotating carousel. It also enrols customers into auto-pay through a "
          "pre-checked “Auto pay enabled” box at checkout, with the consent microcopy set beneath it in small "
          "type. Digicel works hard to start and sustain the subscription, and barely at all to save it once "
          "the customer has decided to leave."),
    ("p", "That is a defensible strategy, and arguably the correct one. By the time a sender reaches the "
          "cancel screen, the decision is usually already made — a pattern BR's own data confirms emphatically."),

    ("h3", "BOSS Revolution's starting position is worse than Digicel's"),
    ("b", "BR has zero of the sixteen mechanisms  —  three separate internal files state it flatly: no "
          "retention offer, no exit survey, no cancellation-reason capture, no cooldown. The only friction is "
          "a Yes/No dialog, and roughly 1–4% tap “No”."),
    ("b", "Cancellation is fast and decided  —  77.8% of Edit Subscription viewers hit Cancel, 98.9% of those "
          "confirm, and 76.9% complete end-to-end within the hour. Median transitions are 7 seconds to Cancel "
          "and 3 seconds to confirm. The Edit screen is functionally a cancellation screen."),
    ("b", "Pause does not exist  —  the subscription has two states, active and cancelled. A sender whose only "
          "problem is timing has exactly one available action, and 94% of them take it."),

    ("h3", "The highest-value fix is not a save flow at all"),
    ("p", "12.7% of subscriptions are cancelled within 30 days at a 5.9-day median, and around 70% of those "
          "30-day cancellations happen in week one. That median sitting just under seven days points at a "
          "mechanical cause rather than a persuasion problem: renewal frequency is auto-derived from offer "
          "validity, 28% of new subscriptions land on a weekly cadence, and 96.6% sit at an interval of one. "
          "Every 7-day bundle silently becomes a weekly charge nobody chose. When senders pick a frequency "
          "explicitly, the most popular choice is every 90 days — not weekly."),
    ("p", "Fixing the default cadence, and making the subscription visible at the moment it is created, "
          "addresses the cause of the largest churn cluster. A save flow only argues with the symptom. Both are "
          "worth doing; the order matters."),

    ("h3", "The compliance position has changed and internal material may be stale"),
    ("p", "The FTC's click-to-cancel Negative Option Rule is not in force. The Eighth Circuit vacated it in its "
          "entirety on 8 July 2025, six days before the compliance date, on procedural grounds. What binds "
          "instead is ROSCA and FTC Act §5 — under which enforcement has accelerated, not slowed — plus state "
          "Automatic Renewal Laws, which apply by customer residence."),
    ("p", "Minnesota is the strictest and therefore the design constraint: a seller may not present offers, "
          "modifications or gifts to a customer who has given notice of cancellation until it has asked "
          "permission, and it may ask only once per attempt. Critically, Minnesota carves out four safe "
          "harbours that need no permission — asking a skippable reason, stating consequences, verifying "
          "identity, and describing options such as downgrading, pausing or suspending. Pause is therefore both "
          "the strongest retention lever available and the lowest-risk one."),

    ("h3", "Recommendation in one line"),
    ("p", "Do not lead with a save offer. Fix the cadence default and the enrolment visibility first, build "
          "pause and instrument every branch second, and add the reason-targeted offer third — gated behind a "
          "single skippable permission prompt so one flow ships nationally."),

    # ------------------------------------------------------------ 2 ----
    ("h2", "2. Research approach and test conditions"),

    ("h3", "2.1 What was and was not done"),
    ("p", "No cancellation was performed, no account was created, no account changes were made, and no payment "
          "details were entered. Digicel's cancellation UI sits behind authentication, so the flow could not be "
          "walked."),
    ("p", "The retention dialog documented in Section 3 was not observed in a browser. It was recovered by "
          "fetching and parsing the JavaScript bundle that Digicel serves to every visitor of the Recurring "
          "Payments route, which contains the dialog's branch logic, its message catalogue in four languages, "
          "and the click handlers behind both buttons. That is strong evidence about what the code does, and "
          "weaker evidence about what a given customer sees, because the feature flag resolves server-side."),

    ("h3", "2.2 Two products, three surfaces — and why the distinction matters"),
    ("b", "Digicel International  —  topup.digicelgroup.com plus its companion app. The diaspora-facing product "
          "that actually competes with BOSS Revolution IMTU. This is the primary subject."),
    ("b", "MyDigicel  —  the domestic self-care app for Digicel's own subscribers in Caribbean markets. Adjacent, "
          "not the competitor."),
    ("b", "Digicel Pacific  —  sold to Telstra on 14 July 2022. Six help centres covering PNG, Fiji, Samoa, "
          "Nauru, Tonga and Vanuatu describe a product Digicel no longer owns. Early research leant on these "
          "and the verification pass removed them."),

    ("h3", "2.3 Method"),
    ("p", "Eight parallel research passes were reconciled against four adversarial verification passes whose "
          "standing instruction was to assume every claim false until independently re-fetched. Where a verdict "
          "contradicted a finding, the verdict won. The verification pass materially changed the conclusion of "
          "this document: the first pass concluded Digicel had no retention intervention at all, and that was "
          "wrong."),
    ("p", "Findings are tagged Verified (read on a fetched page or in shipped code, quotable with a source), "
          "Inferred (reasoned from adjacent evidence, with the reasoning stated), or Unverified (could not be "
          "established, and listed in Section 11)."),

    ("h3", "2.4 Handling of sensitive data"),
    ("p", "The two Digicel screenshots reproduced here are the company's own Play Store marketing assets. "
          "Recipient names and contact photographs have been redacted; the phone numbers were already blurred "
          "by Digicel at source. No customer data was accessed at any point."),

    ("h3", "2.5 A caution about Digicel's own documentation"),
    ("p", "Digicel's help centre is not a reliable description of its shipped product. It documents the "
          "navigation to the trash icon and stops there, describing none of the dialog that follows — neither "
          "variant, in any language, in any market. Where documentation and code disagree, this analysis "
          "follows the code."),

    # ------------------------------------------------------------ 3 ----
    ("h2", "3. The cancellation journey, step by step"),

    ("p", "Confidence is marked per step. Verbatim strings are quoted exactly as they appear in Digicel's "
          "message catalogue."),

    ("h3", "3.1 Reaching the cancellation control"),
    ("p", "Steps 1–4 — Navigation (Verified, from Digicel's FAQ). Two paths, quoted verbatim. In the app: log "
          "in, tap “More” at the bottom right, select “Frequent Payments”, select Auto Top Up and AutoPay, then "
          "tap the trash icon — five steps. On web: log in, click the “Profile” icon at the top right, select "
          "“Recurring Payments”, then click the trash icon — four steps."),
    ("p", "This is genuinely low-friction and self-serve, with no phone call, no chat and no email required. "
          "Against the standard set by the Vonage and Amazon enforcement actions, that is the right shape. The "
          "criticism worth making is narrower: the terminal control is an icon-only trash button on mobile, "
          "which is both an accessibility problem and an ambiguity problem."),

    ("h3", "3.2 The dialog Digicel does not document"),
    ("p", "Step 5 — Feature-flag branch (Verified, from shipped code). The delete opens a dialog whose content "
          "depends on a flag named “frequent-payments”. Both variants exist in production and both are "
          "localised into English, Spanish, French and Dutch — the translation investment being the strongest "
          "available evidence that this is genuinely deployed rather than dead code."),
    ("p", "Control arm (Verified). Titled “Remove Frequent Payment”, body “Are you sure you want to remove this "
          "frequent payment?”, followed by “This action cannot be undone!”, with buttons “Back” and “Remove”. "
          "An ordinary destructive-action confirmation."),
    ("p", "Test arm (Verified). Titled “If you cancel, you will miss out on:” followed by three fixed bullets — "
          "“Exclusive benefits, like discounts”, “Worry-free connection to your loved ones”, and “the comfort "
          "of sitting back while we do the work” — with buttons “Keep my Advantages” and “Remove Recurring Top "
          "Up”. The bullets render in a hard-coded order with no segmentation, no interpolation and no runtime "
          "data, so the message is identical for every customer."),
    ("p", "Note what the test arm is not. It names benefits; it grants nothing. No discount is applied, no "
          "credit is issued, and no alternative is offered, because none exists to offer. The confirm button is "
          "labelled “Remove Recurring Top Up” — explicit and not confirm-shamed, which is to Digicel's credit."),

    ("h3", "3.3 Outcomes"),
    ("p", "Abandoning (Verified). In the control arm, “Back” closes the dialog. In the test arm, “Keep my "
          "Advantages” is wired directly to the close handler. In both cases the subscription survives and no "
          "analytics event is emitted."),
    ("p", "Accepting an alternative (Verified as absent). There is no alternative to accept. A sweep of the "
          "four-locale message catalogue found 54 keys relating to recurring payments, covering listing, setup, "
          "interval display, errors and removal — and no key for edit, pause, skip, snooze, change, downgrade, "
          "reason, survey or support."),
    ("p", "Completing cancellation (Verified). The delete call fires and a success snackbar appears in-product. "
          "This is the only branch that emits an event."),
    ("p", "Contacting support (Verified as absent from the flow). No support affordance appears in either "
          "dialog. Support is a separate page, staffed Monday to Saturday, 09:00–18:00 EST."),
    ("p", "Post-cancellation (Unverified). No win-back or recovery message is documented in any source or any "
          "market, and whether an email or SMS confirmation is sent could not be established."),

    ("h3", "3.4 Where Digicel actually intervenes"),
    ("p", "The screenshot below is Digicel's own store asset for the international app. The “Renew before it's "
          "too late” card, its “3 DAYS REMAINING” badge and its “Renew Now” button are a genuine retention "
          "mechanism using urgency — placed before expiry, not at cancellation. Note also the bottom navigation: "
          "the “More” tab is the same one the FAQ says leads to Frequent Payments."),
    ("cap", "Digicel International app home — pre-expiry renewal nudge with urgency badge. "
            "Contacts redacted; phone number blurred at source. Source: Google Play listing"),
    ("table", "IMG_NUDGE"),

    ("p", "The second screenshot is the enrolment counterpart. “Auto pay enabled” is pre-checked at checkout, "
          "with the consent microcopy — “By checking this you agree that this plan will be auto renewed until "
          "cancelled” — set in small type beneath it. The marketing headline above reads “Never miss a moment. "
          "Keep their service on”."),
    ("p", "This is a direct parallel to BR's own default-ON subscription toggle, and it carries the same "
          "exposure. A pre-checked recurring-billing consent is precisely the pattern state ARLs scrutinise, "
          "and BR already has an open Critical defect in this area."),
    ("cap", "Digicel International checkout — auto-pay pre-checked, consent microcopy beneath. "
            "Recipient name redacted; phone number blurred at source. Source: Google Play listing"),
    ("table", "IMG_OPTIN"),

    ("h3", "3.5 What no screenshot shows"),
    ("p", "Not one published image anywhere depicts a Digicel cancellation confirmation, retention offer or "
          "save screen, for either product. Digicel's own help-centre screenshots of the opt-out flow — "
          "filenames such as optout1.PNG and active-plans1.JPG — now resolve to soft-404 pages, and a sweep of "
          "509 archived records shows no web archive ever captured them. The account area has never been "
          "archived; only login redirects exist. The retention dialog documented above is known solely from its "
          "source code."),

    # ------------------------------------------------------------ 4 ----
    ("h2", "4. Retention mechanisms and behavioural techniques"),
    ("p", "The brief's checklist, worked through item by item against the Digicel International product. An "
          "inventory of absences is the result."),
    ("table", "MECHANISMS"),

    ("h3", "4.1 Three observations"),
    ("p", "First, the absences are architectural rather than stylistic. With no PUT or PATCH endpoint, pause "
          "and modify are not design decisions Digicel declined to make — they are capabilities it does not "
          "have. Any competitor reading this should note that BR is in the same position on pause, and a "
          "better one on modify."),
    ("p", "Second, the one mechanism Digicel did ship, it cannot evaluate. That is the single most transferable "
          "lesson in this document."),
    ("p", "Third, there is a structural lock-in mechanic worth noting even though it is not a save flow: "
          "recurring purchases carry a discount that applies “from the second renewal”, which rewards persistence "
          "rather than rescuing a departing customer. Its value is not published."),

    # ------------------------------------------------------------ 5 ----
    ("h2", "5. Detailed flowchart"),
    ("p", "Every step, decision point, branch, alternate arm and terminal state in the observed flow. "
          "Navigation is from Digicel's FAQ; the dialog branch and its copy are from the shipped bundle."),
    ("table", "IMG_FLOW_DIGICEL"),
    ("cap", "Diagram 1 — Digicel International top-up: observed cancellation flow, with the retention-mechanism inventory"),

    # ------------------------------------------------------------ 6 ----
    ("h2", "6. Strengths and weaknesses"),
    ("h3", "6.1 Strengths worth adopting"),
    ("table", "STRENGTHS"),
    ("h3", "6.2 Weaknesses, friction and manipulative patterns"),
    ("table", "WEAKNESSES"),

    ("h3", "6.3 The honest verdict on manipulation"),
    ("p", "Digicel's cancellation flow is not manipulative. It is short, self-serve, available in the same "
          "medium the product was bought in, and its confirm button says plainly what it does. The dark-pattern "
          "risk in this product sits at the other end of the lifecycle — in the pre-checked auto-pay box at "
          "checkout, not in the exit."),
    ("p", "The test arm's loss framing (“you will miss out on”) is mild persuasion of a kind every regulator "
          "reviewed here expressly permits, provided the statements are true and the cancel path stays "
          "available. The weaker point is that its claims are generic and unverifiable — “Exclusive benefits, "
          "like discounts” is asserted to a customer who may never have received one."),

    # ------------------------------------------------------------ 7 ----
    ("h2", "7. Customer experience, accessibility and compliance"),

    ("h3", "7.1 The federal position has changed — check any internal deck that predates this"),
    ("p", "The FTC's amended Negative Option Rule, published November 2024 and known as click-to-cancel, was "
          "vacated in its entirety by the Eighth Circuit on 8 July 2025 in Custom Communications v. FTC, six "
          "days before its compliance date. The grounds were procedural — the Commission failed to perform a "
          "required preliminary regulatory analysis — and the court did not hold that the FTC lacked authority "
          "to impose the requirements. The vacatur reinstated the 1973 rule, which does not reach app "
          "subscriptions. The FTC restarted rulemaking with an advance notice published 13 March 2026."),
    ("p", "The substance survives by statute. ROSCA independently requires simple mechanisms to stop recurring "
          "charges, and FTC Act §5 reaches deceptive cancellation practices. Enforcement has accelerated since "
          "the vacatur, not slowed. Two precedents matter here: the Amazon settlement of September 2025, which "
          "required cancellation by the same method used to sign up and a clear conspicuous decline button, and "
          "FTC v. Vonage in 2022 — the telecom analogue, and the most on-point precedent BR has — which turned "
          "on forcing customers through a live retention agent to cancel."),

    ("h3", "7.2 Minnesota is the binding constraint, and its safe harbours are the design"),
    ("p", "State ARLs apply by customer residence, so a single US flow must be built to the strictest. That is "
          "Minnesota, in force since 1 January 2025, which prohibits presenting additional benefits, contract "
          "modifications or gifts to a customer who has given notice of cancellation until permission has been "
          "obtained — and permits asking for that permission only once per attempt."),
    ("p", "Minnesota's four express safe harbours are the most useful design finding in this document. Without "
          "prior permission a seller may still ask the reason for cancelling, provided answering is not a "
          "condition of cancelling; state the consequences of cancelling; verify identity; and describe options "
          "to maintain the relationship, expressly including downgrading, pausing or suspending."),
    ("p", "One genuine textual tension deserves counsel input: the statute bars contract modifications without "
          "permission while expressly permitting the describing of a pause. Whether offering a pause, as "
          "opposed to describing one, needs prior permission is open on the text. Design conservatively."),
    ("p", "California supplies the shape of a lawful online save offer: a retention offer is permitted provided "
          "the business simultaneously displays a prominently located, continuously and proximately displayed "
          "“click to cancel” link or button, and processes the cancellation promptly if it is used. New York, "
          "Colorado and Virginia follow the same model on comparable timelines."),

    ("h3", "7.3 What a retention flow may and may not do"),
    ("table", "COMPLIANCE"),

    ("h3", "7.4 Accessibility"),
    ("p", "A cancellation flow is a high-stakes destructive action and attracts the strictest reading of "
          "WCAG 2.2. The specific failure modes that retention patterns tend to introduce are: icon-only "
          "destructive controls with no accessible name — Digicel's trash icon is the textbook case; modal "
          "dialogs that trap or lose focus; and decline options styled as low-contrast secondary text, which "
          "is simultaneously a dark pattern and a contrast failure."),
    ("p", "Practical acceptance criteria for any BR cancellation ticket: every control has a programmatic "
          "accessible name, not an icon alone; the decline and confirm paths meet the same contrast ratio and "
          "the same minimum target size; focus moves into the dialog on open and returns to the invoking "
          "control on close; the destructive action is announced as such; no countdown or time limit gates any "
          "step; and the flow is available in every language the purchase flow supports."),

    ("h3", "7.5 The customer-experience read"),
    ("p", "From the customer's side, Digicel's flow is fine. It is quick, honest about irreversibility, and "
          "does not trap. From the business's side it is close to worthless — it captures no reason, offers no "
          "alternative, and cannot report whether its one intervention works. BR's flow today is the same "
          "trade with the retention half removed entirely."),

    # ------------------------------------------------------------ 8 ----
    ("h2", "8. Recommended BOSS Revolution IMTU cancellation flow"),
    ("p", "The flow below is built to Minnesota so that one version ships nationally, keeps the cancel control "
          "continuously visible to satisfy California, and instruments every branch so the experiment is "
          "answerable — the failure Digicel shipped."),
    ("table", "IMG_FLOW_BR"),
    ("cap", "Diagram 2 — Recommended BOSS Revolution IMTU cancellation flow"),

    ("h3", "8.1 Adopt, adapt, avoid, and add"),
    ("table", "ADOPT"),

    ("h3", "8.2 Why pause is the primary intervention rather than a discount"),
    ("p", "Three reasons converge. Legally, pause sits inside Minnesota's express safe harbour while a discount "
          "requires prior permission. Commercially, BR's churn is dominated by senders who did not intend a "
          "weekly commitment, and a timing problem is answered by deferral rather than by price. Practically, "
          "BR already has the modify endpoint that a frequency change needs, so a deferral is closer to shippable "
          "than a new discount mechanic tied to the promo engine."),
    ("p", "Pause does not exist today — the subscription has only active and cancelled states — so this is real "
          "backend work. It is the single highest-value capability in this document."),

    ("h3", "8.3 What the flow deliberately does not do"),
    ("p", "It does not re-prompt. The permission ask happens once per attempt, and a declined offer is not "
          "shown again. It does not gate cancellation behind the reason question. It does not style the decline "
          "path as secondary. And it does not carry an incentive-based variant to Minnesota residents without "
          "the permission gate — of the four variants currently planned internally, three are likely "
          "safe-harboured and the incentive-based one is not."),

    # ------------------------------------------------------------ 9 ----
    ("h2", "9. Prioritised recommendations"),
    ("table", "PRIORITY"),

    ("h3", "9.1 Sequencing"),
    ("p", "Phase 0 fixes causes rather than symptoms: change how renewal cadence is derived, and make the "
          "subscription unmistakable at the moment it is created. This addresses the largest churn cluster and "
          "reduces the population a save flow would ever need to argue with."),
    ("p", "Phase 1 fixes measurement: a cancellation-reason property, renewal events, variant tags that survive "
          "GA, and notification tracking. Without these, no retention experiment can be read."),
    ("p", "Phase 2 builds pause and the reason-targeted intervention behind the permission gate."),
    ("p", "Phase 3 adds win-back, which should not run at all while the consent defect remains open."),

    # ------------------------------------------------------------ 10 ----
    ("h2", "10. Success metrics and experimentation"),

    ("h3", "10.1 The metric set"),
    ("table", "METRICS"),

    ("h3", "10.2 Guardrails that must be watched, not just outcome metrics"),
    ("p", "A save flow can improve its own numbers while damaging the business. Watch support contacts per "
          "thousand cancellations, app-store and Trustpilot sentiment mentioning cancellation, chargeback and "
          "dispute rate, and the rate of subsequent hard churn among saved customers. A customer retained into "
          "a subscription they did not want is a future dispute, not a win."),

    ("h3", "10.3 Experiment design notes"),
    ("p", "Randomise at the customer level and tag every event with the variant, including post-GA — the "
          "current instrumentation loses variant tags after general availability, which would make the result "
          "unreadable exactly when it matters. Fire an exposure event when the intervention renders, not when "
          "the screen that precedes it loads. Power the test on save rate, but pre-register the guardrails "
          "above as stopping conditions."),
    ("p", "Sequence the experiments rather than running them together: cadence default first, because it "
          "changes the composition of the cancelling population and would otherwise confound everything "
          "downstream; then the permission gate and reason capture; then intervention content."),
    ("p", "One caution on the baseline. Attach rate and cancellation figures are being deliberately moved by "
          "work already in flight, so any pre/post comparison needs its baseline captured before that lands."),

    # ------------------------------------------------------------ 11 ----
    ("h2", "11. Open questions, assumptions and what remains unverified"),

    ("h3", "11.1 Unverified about Digicel"),
    ("b", "Whether the retention flag is currently enabled, and for what share of traffic. Flag state resolves "
          "server-side behind login, and the client falls back to the control arm when flag evaluation is "
          "unavailable — so real exposure may be far narrower than “an A/B test is running” suggests."),
    ("b", "Whether the native app shows the same dialog. The web app runs inside a native webview, which makes "
          "it likely, but the app binary was not analysed. An APK teardown would settle this and several "
          "questions below without needing an account."),
    ("b", "Whether an email or SMS confirmation follows cancellation."),
    ("b", "Whether any win-back campaign runs after cancellation. Outbound CRM is rarely public, so absence of "
          "evidence is weak evidence here."),
    ("b", "The value of the recurring discount that applies from the second renewal."),
    ("b", "Whether MyDigicel's domestic self-care app has any retention step. This is genuinely unresolved: the "
          "documentation is stale, much of what was found describes Telstra-owned markets, and help articles "
          "stop at the tap rather than describing what renders after it."),

    ("h3", "11.2 Open questions for the BR team"),
    ("table", "QUESTIONS"),

    ("h3", "11.3 Assumptions this analysis rests on"),
    ("b", "That the shipped bundle reflects what customers see. Code presence proves capability, not exposure; "
          "the flag could be off for everyone."),
    ("b", "That Digicel's store screenshots depict current UI. They are dated February 2026 and are marketing "
          "assets, so they may be idealised."),
    ("b", "That BR's internal figures are sound. Two are contested inside BR's own documents — the attach rate "
          "appears as both 45.5% and 32.1% depending on the measure, and one file says the cancel flow's save "
          "step catches 0.98% while another says no save step has ever shipped. Neither should be quoted "
          "externally until reconciled."),
    ("b", "That state ARL coverage is complete enough to design against. Minnesota, California, New York, "
          "Colorado and Virginia were examined; a full fifty-state survey was not done and remains outstanding "
          "before launch."),

    ("h2", "12. Source note"),
    ("p", "Digicel primary sources: topup.digicelgroup.com/en/faq/, the Recurring Payments route bundle served "
          "from topup.digicelgroup.com, and the Google Play listings for the Digicel International and "
          "MyDigicel apps. Regulatory sources: Minn. Stat. §325G.58, Cal. Bus. & Prof. Code §17602, the FTC's "
          "2024 final rule and its 2026 advance notice, FTC v. Vonage and FTC v. Amazon. Internal BR context is "
          "drawn from the IMTU core-logic, subscription-logic, toggle-analysis and revenue documents in this "
          "repository, and from the Amplitude charts cited inline."),
]

# ---------------------------------------------------------------- tables ----

MECHANISMS = [
    ["Mechanism", "Digicel International", "Evidence"],
    ["Placement / visibility of cancel option", "PRESENT — low friction",
     "4 steps on web, 5 in app, self-serve, same medium as purchase. Confirm button explicitly labelled."],
    ["Benefit-loss reminder", "PRESENT — the entire intervention",
     "Test arm: “If you cancel, you will miss out on:” plus three fixed bullets. Control arm: “This action cannot be undone!”"],
    ["Confirmation dialog", "PRESENT",
     "Both arms confirm before deleting. Undocumented in the help centre."],
    ["Reason capture / exit survey", "ABSENT",
     "No reason key among 54 recurring-payment keys across four locales; no reason string anywhere in the bundle."],
    ["Personalised messaging", "ABSENT",
     "Three static bullets in hard-coded order, no segmentation, no interpolation, no runtime data."],
    ["Discount / credit / bonus at cancel", "ABSENT",
     "The dialog mentions “discounts” but grants nothing. A separate recurrence discount applies from the second renewal — lock-in, not a save."],
    ["Pause / postpone / skip", "ABSENT — and unbuildable today",
     "No pause key; no PUT or PATCH endpoint anywhere in the bundle."],
    ["Downgrade or modify", "ABSENT at cancel",
     "Setup copy promises “Easily change this setting in your profile”; the management screen offers only removal."],
    ["Alternative amount", "ABSENT", "No amount-change capability."],
    ["Alternative frequency", "ABSENT", "Interval is server-supplied and read-only in the client."],
    ["Alternative payment method", "ABSENT",
     "Recurring is Visa/Mastercard only, so no fallback instrument exists to offer."],
    ["Alternative recipient", "ABSENT", "Recipient is not editable; one schedule per number."],
    ["Urgency / scarcity", "ABSENT at cancel",
     "No timer or scarcity language in either arm. Urgency is used pre-expiry instead (“3 DAYS REMAINING”)."],
    ["Social proof", "ABSENT", "No testimonial, count or peer-behaviour language anywhere."],
    ["Support intervention / handoff", "ABSENT from the flow",
     "No support affordance in either dialog. Support is a separate page, Mon–Sat 09:00–18:00 EST."],
    ["Post-cancellation win-back", "NO EVIDENCE",
     "Nothing found in any source or market. Outbound CRM is rarely public, so this is weak evidence."],
    ["Measurement of the intervention", "BROKEN — the key finding",
     "No exposure event on render; “Keep my Advantages” is wired to close only. Session recording disabled globally, enabled solely here."],
]

STRENGTHS = [
    ["Strength", "What Digicel does", "Relevance to BR"],
    ["Self-serve cancellation in the purchase medium",
     "Four to five steps, no phone call, no chat, no email. Available on both web and app.",
     "This is the compliance floor under ROSCA and every state ARL reviewed. BR already meets it."],
    ["An explicit confirm label",
     "“Remove Recurring Top Up” rather than a vague “Continue” or a shaming “No thanks”.",
     "Cheap, and directly responsive to what the Amazon order required."],
    ["Honest irreversibility warning",
     "“This action cannot be undone!” in the control arm.",
     "Pre-empts disputes. Keep the honesty, but pair it with prevention rather than disclaimer."],
    ["Loss framing that stays factual and permitted",
     "“If you cancel, you will miss out on:” with three benefit bullets, no countdown, no fake scarcity.",
     "Sits inside Minnesota's “consequences of cancelling” safe harbour. The framing is adoptable; the content is too generic to copy."],
    ["Localisation of the intervention",
     "The dialog ships in English, Spanish, French and Dutch.",
     "BR's multilingual Braze pipeline already supports five languages — parity is achievable."],
    ["Retention effort placed pre-expiry",
     "“Renew before it's too late” card with a 3-days-remaining badge and a Renew Now button, in a home-screen carousel.",
     "The strategically interesting choice. Intervening before the cancel intent forms is cheaper than arguing at the exit."],
]

WEAKNESSES = [
    ["Weakness", "Evidence", "Consequence"],
    ["The one intervention cannot be measured",
     "No exposure event on dialog render; “Keep my Advantages” wired to onClose only. Just two events exist in the flow.",
     "Digicel cannot compute a save rate or a denominator. The experiment cannot conclude."],
    ["Session recording used as a substitute for analytics",
     "Recording disabled globally across the site, enabled only for this flow.",
     "Reads as a team compensating for missing events with manual replay review."],
    ["No alternative to accept",
     "54 recurring-payment keys across four locales contain no pause, skip, edit, downgrade or change key.",
     "The dialog asks the customer to reconsider while offering nothing to reconsider in favour of."],
    ["The absences are architectural",
     "The API client exposes only getAutoPays and removeAutoPay; no PUT or PATCH appears in the entire bundle.",
     "Digicel cannot add pause or modify as a UI change. Neither can BR — this is backend work for both."],
    ["Generic, unverifiable benefit claims",
     "“Exclusive benefits, like discounts” is shown to every customer regardless of whether they ever received one.",
     "Weak persuasion, and a truthfulness risk if the customer has had no such benefit."],
    ["No reason capture anywhere",
     "Confirmed absent from the bundle.",
     "Digicel learns nothing from its own churn. BR has the identical gap today."],
    ["Icon-only destructive control on mobile",
     "The terminal action is a trash icon.",
     "Accessibility failure if unlabelled, and ambiguous next to a list of scheduled payments."],
    ["Cancellation undocumented beyond the tap",
     "The help centre describes navigation and stops; neither dialog variant appears in any language or market.",
     "Customers cannot know what to expect, and the documentation actively understates the product."],
    ["Pre-checked auto-pay at enrolment",
     "Store screenshot shows “Auto pay enabled” checked by default with consent microcopy in small type beneath.",
     "The real dark-pattern exposure in this product, and the closest parallel to BR's own open consent defect."],
    ["No support route from the flow",
     "No support key in either dialog; support hours are Mon–Sat only.",
     "A customer with a fixable problem has no path to someone who could fix it."],
]

ADOPT = [
    ["Verdict", "Pattern", "How BR should treat it"],
    ["Adopt", "Self-serve cancellation in the same medium as purchase",
     "Already true for BR. Protect it — this is the compliance floor, not a feature."],
    ["Adopt", "Explicit, non-shaming labels on both buttons",
     "“Cancel subscription” and “Keep subscription”, equal weight, equal contrast, equal target size."],
    ["Adopt", "Factual statement of consequences",
     "Name the real losses: the recipient's top-up stops on a stated date, a promotional rate ends. Safe-harboured in Minnesota, and it must be true."],
    ["Adopt", "Retention effort before the cancel intent forms",
     "Digicel's most defensible choice. For BR this means the renewal reminder and the failed-payment message, not the exit screen."],
    ["Adapt", "Loss-framed reminder",
     "Keep the frame, replace the content. BR can name the customer's actual bonus airtime and actual saved rate rather than generic “exclusive benefits”."],
    ["Adapt", "Confirmation dialog",
     "BR already has one and it saves 1–4%. Do not expect more from it; it is a mis-tap guard, not a retention tool."],
    ["Adapt", "Urgency badge",
     "Legitimate before expiry, where the deadline is real. Never at cancellation, where a countdown would be manufactured pressure."],
    ["Avoid", "Shipping an intervention you cannot measure",
     "The central lesson. Instrument exposure, offer-shown, accepted, declined and cancelled, variant-tagged, before launch."],
    ["Avoid", "Generic benefit claims",
     "Do not assert benefits a given customer has never received. Truthfulness is an independent legal requirement, not just good practice."],
    ["Avoid", "Icon-only destructive controls",
     "Label the action in text. This is both an accessibility requirement and a clarity one."],
    ["Avoid", "Pre-checked recurring-billing consent",
     "Digicel's clearest bad pattern, and BR's most direct shared exposure. Resolve the open consent defect before adding retention on top."],
    ["Avoid", "Support-only or delayed cancellation",
     "The Vonage action turned on exactly this. Never route cancellation through a retention agent."],
    ["New", "Pause / skip a cycle",
     "Does not exist in either product. Minnesota's safe harbour expressly permits describing it, and BR's churn is dominated by timing, not price."],
    ["New", "Skippable reason capture feeding the promo engine",
     "Safe-harboured, and it closes BR's inability to attribute voluntary churn to a cause."],
    ["New", "Reason-targeted intervention behind a permission gate",
     "One ask, once per attempt, cancel control visible throughout. Satisfies Minnesota and California in a single flow."],
    ["New", "Frequency change offered as a save",
     "BR already has the modify endpoint. Offering “every 30 days instead of weekly” is close to shippable and answers the dominant churn cause."],
    ["New", "Failed-renewal dunning",
     "28.4% of active subscriptions are failing and the customer is told nothing on any channel. This is retention before it becomes cancellation."],
]

COMPLIANCE = [
    ["", "Requirement", "Source"],
    ["MAY NOT", "Require a phone call, chat or any offline step to cancel something bought in-app or online.",
     "Cal. §17602(d)(1); NY GBL §527-a; FTC v. Vonage; Amazon order"],
    ["MAY NOT", "Sequence the customer through offer screens before any cancel control becomes reachable.",
     "Cal. §17602(e)(2) “simultaneously”; FTC Amazon complaint"],
    ["MAY NOT", "Show a discount, credit, bonus or plan modification to a Minnesota customer without first asking permission — once only, per attempt.",
     "Minn. §325G.58 subd. 4"],
    ["MAY NOT", "Make a cancellation-reason survey mandatory or gate the cancel button behind answering it.",
     "Minn. §325G.58 subd. 5(1)"],
    ["MAY NOT", "Use asymmetric button design or confirmshaming copy on the decline path.",
     "Amazon order names this pattern; EU dark-pattern work targets it"],
    ["MAY NOT", "Take one more scheduled charge after a cancellation request, or apply a surprise exit fee.",
     "FTC v. Vonage"],
    ["MAY NOT", "Write a price-match or right-of-first-refusal term into the subscription agreement.",
     "Minn. §325G.58 subd. 3 — void and unenforceable"],
    ["MAY", "Offer or describe pause, skip, downgrade or suspend — the highest-value, lowest-risk lever.",
     "Minn. §325G.58 subd. 5(4)"],
    ["MAY", "Present one save offer on the same screen as a persistent, prominent cancel control.",
     "Cal. §17602(e)(2)"],
    ["MAY", "State the genuine consequences of cancelling — and they must be true.",
     "Minn. subd. 5(2); FTC Act §5 for truthfulness"],
    ["MAY", "Ask a skippable “why are you leaving?” and verify identity.",
     "Minn. subd. 5(1) and 5(3)"],
    ["WATCH", "The March 2026 FTC advance notice asks directly whether save attempts should be restricted. A future rule could reinstate an opt-in gate.",
     "91 FR 12318"],
]

PRIORITY = [
    ["#", "Recommendation", "Why now", "Effort"],
    ["P0", "Change how renewal cadence is derived from offer validity",
     "28% of new subscriptions land on weekly and 96.6% at interval 1, while explicit choosers prefer every 90 days. This is the mechanical cause of the 5.9-day cancel cluster.",
     "Weeks"],
    ["P0", "Make the subscription unmistakable at the moment it is created",
     "Roughly 70% of 30-day cancellations happen in week one, and the same-day cluster cancels ~3.3h after purchase — the signature of discovery, not regret.",
     "Weeks"],
    ["P0", "Close the open consent defect before adding any retention layer",
     "A subscription created without consent, plus ARL notice obligations still To Do. Retention built on contested consent multiplies the exposure.",
     "Weeks"],
    ["P1", "Add a cancellation-reason property to the cancel event",
     "Voluntary churn cannot currently be attributed to a cause from product analytics at all.",
     "Days"],
    ["P1", "Emit events for renewal attempts, declines and failing state",
     "28.4% of subscriptions are failing and the population is invisible in Amplitude — it surfaced only via a database analysis.",
     "Weeks"],
    ["P1", "Preserve A/B variant tags post-GA",
     "Post-GA events carry no variant, so a retention experiment would become unreadable exactly when it ships.",
     "Days"],
    ["P2", "Build pause / skip a cycle",
     "The strongest lever available, expressly safe-harboured in Minnesota, and the direct answer to a timing-driven churn profile. Does not exist today.",
     "1–2 quarters"],
    ["P2", "Build failed-renewal dunning",
     "A failed renewal sends nothing on any channel today, and the ticket has sat in backlog since 2024. This is retention before cancellation.",
     "1 quarter"],
    ["P2", "Add a skippable reason step and a single permission-gated intervention",
     "Safe-harboured, and it makes the reason data actionable through the existing promo engine.",
     "1 quarter"],
    ["P3", "Offer a frequency change as a save action",
     "The modify endpoint already exists, so this is largely front-end work over a shipped capability.",
     "Weeks"],
    ["P3", "Complete a fifty-state ARL survey before launch",
     "Five states were examined. Coverage applies by customer residence, so gaps are live exposure.",
     "Weeks"],
    ["P4", "Reconsider win-back only after consent is clean",
     "An internal review already rejected it: the audience is dominated by people undoing something they never chose, and marketing consent rules apply.",
     "Deferred"],
]

METRICS = [
    ["Metric", "Definition", "Why this one"],
    ["Save rate", "Customers who reach the intervention and do not cancel in that session, over all customers who reach it.",
     "The headline. Requires an exposure event — the thing Digicel omitted."],
    ["Intervention exposure rate", "Customers shown the intervention over all cancel initiations.",
     "Detects flag or routing failures. Digicel cannot compute this at all."],
    ["Cancel completion rate", "Confirmations over initiations.",
     "Today roughly 94–99% depending on the measure. The guardrail against building obstruction rather than persuasion."],
    ["Pause uptake", "Pauses accepted over interventions shown.",
     "Tests whether timing, not price, is the real driver — as BR's cancel timing suggests."],
    ["Reason distribution", "Share of cancellations by captured reason, with skip rate reported alongside.",
     "Currently unobtainable. Skip rate must be reported or the distribution is biased."],
    ["30-day survival after save", "Saved customers still active 30 days later.",
     "Distinguishes genuine retention from deferred churn. A save that fails at day 20 is not a save."],
    ["Week-one cancellation rate", "Cancellations within 7 days of creation.",
     "The direct measure of whether the cadence and disclosure fixes worked. Around 70% of 30-day churn sits here."],
    ["Weekly-cadence share of new subscriptions", "Share created at a 7-day interval.",
     "The leading indicator for the P0 cadence fix. Currently about 28%."],
    ["Failing-subscription share", "Active subscriptions with no working payment instrument.",
     "Currently 28.4% and invisible in analytics. Fixing dunning should move it."],
    ["Support contacts per 1,000 cancellations", "Cancellation-related contacts normalised to volume.",
     "The friction guardrail. A rising number means the flow is obstructing, not persuading."],
    ["Dispute / chargeback rate on subscriptions", "Disputes over renewal charges.",
     "The consent guardrail, and the one most likely to attract regulatory attention."],
]

QUESTIONS = [
    ["Tier", "Question", "Why it matters"],
    ["Blocking", "What does epic DCS-4707 “Subscription Cancellation” actually contain?",
     "It is absent from the entire repository and from git history. It may already scope some of this work."],
    ["Blocking", "Reconcile the contested attach and save figures before any of this is quoted.",
     "Attach appears as both 45.5% and 32.1%; one file says the save step catches 0.98% while another says no save step ever shipped."],
    ["Blocking", "Is a pause state acceptable to Finance and to the billing stack?",
     "The whole recommendation leans on pause, and the subscription today has only active and cancelled states."],
    ["Blocking", "Does Legal accept the Minnesota-strictest single-flow approach?",
     "The alternative is geo-varied flows, which multiply build and QA cost. Includes the open offer-versus-describe tension on pause."],
    ["Shaping", "Why is renewal cadence derived from offer validity rather than chosen?",
     "Determines whether the P0 cadence fix is a config change or a redesign of subscription creation."],
    ["Shaping", "Can the recipient be changed on an existing subscription?",
     "Not documented as editable, and its absence is not stated as deliberate either. Affects the alternatives available at cancel."],
    ["Shaping", "What is the true subscription share of revenue and 90-day cohort LTV?",
     "Not available today because renewals emit no app event. Without it, no save flow can be sized."],
    ["Shaping", "Which of the four planned retention variants survive Minnesota?",
     "Three describe consequences or benefits and are likely safe-harboured; the incentive-based variant requires prior permission."],
    ["Worth knowing", "Is Digicel's retention flag actually on, and for whom?",
     "Determines whether this is a live experiment or dormant code. An APK teardown would help settle it."],
    ["Worth knowing", "Does MyDigicel's domestic app have any retention step?",
     "Genuinely unresolved. Adjacent to BR's competitive question rather than central to it."],
]

TABLES = [
    ("MECHANISMS", MECHANISMS),
    ("STRENGTHS", STRENGTHS),
    ("WEAKNESSES", WEAKNESSES),
    ("ADOPT", ADOPT),
    ("COMPLIANCE", COMPLIANCE),
    ("PRIORITY", PRIORITY),
    ("METRICS", METRICS),
    ("QUESTIONS", QUESTIONS),
]

IMAGES = [
    ("IMG_NUDGE", "digicel_nudge_redacted.png", 210.0, 884, 1920),
    ("IMG_OPTIN", "digicel_optin_redacted.png", 210.0, 884, 1920),
    ("IMG_FLOW_DIGICEL", "digicel_cancellation_flow.png", 468.0, 2405, 2390),
    ("IMG_FLOW_BR", "br_imtu_cancellation_recommended_flow.png", 468.0, 2405, 2508),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}

VERDICT_COLOR = {
    "Adopt": (0.05, 0.48, 0.42), "Adapt": (0.65, 0.35, 0.04),
    "Avoid": (0.70, 0.15, 0.12), "New": (0.25, 0.32, 0.62),
    "MAY": (0.05, 0.48, 0.42), "MAY NOT": (0.70, 0.15, 0.12),
    "WATCH": (0.65, 0.35, 0.04),
    "Blocking": (0.70, 0.15, 0.12), "Shaping": (0.65, 0.35, 0.04),
    "Worth knowing": (0.45, 0.42, 0.50),
    "P0": (0.70, 0.15, 0.12), "P1": (0.65, 0.35, 0.04),
    "P2": (0.05, 0.48, 0.42), "P3": (0.25, 0.32, 0.62),
    "P4": (0.45, 0.42, 0.50),
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
    for start, r, c in sorted(cells, reverse=True):
        txt = data[r][c]
        if not txt:
            continue
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        elif c == 0 and txt in VERDICT_COLOR:
            red, green, blue = VERDICT_COLOR[txt]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": red, "green": green, "blue": blue}}}},
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
        {"deleteContentRange": {"range": {"startIndex": idx,
                                          "endIndex": idx + plen - 1}}},
        {"insertInlineImage": {
            "location": {"index": idx}, "uri": RAW_BASE + fname,
            "objectSize": {"width": {"magnitude": width, "unit": "PT"},
                           "height": {"magnitude": height, "unit": "PT"}}}},
        {"updateParagraphStyle": {
            "range": {"startIndex": idx, "endIndex": idx + 1},
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT",
                               "alignment": "CENTER"},
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

    linkify(docs, doc_id, {**LINK_MAP, **DIGICEL_LINKS})

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
