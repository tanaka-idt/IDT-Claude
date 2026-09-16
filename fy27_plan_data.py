#!/usr/bin/env python3
"""
Single source of truth for the DCS FY27 plan.

Holds the 22 Board and Business goals taken from the DCS FY27 Asana board
(duplicates merged), the FY26 carry-over work that occupies the first sprints,
the sizing scale, the team capacity, and the fiscal calendar. Every generator
(Google Sheet, Google Doc, HTML) imports from here so the three deliverables
never drift apart.

Sizing scale follows the FY26 spreadsheet: S = 1, M = 2, L = 4, XL = 9 FTE
sprints, where one sprint is two weeks. Estimates are a PM first pass and are
meant to be validated by engineering in the same way Marc and Ilya annotated
the FY26 sheet.
"""

from datetime import date, timedelta

# ----------------------------------------------------------------- calendar ---

FY_START = date(2026, 8, 31)          # Monday of the week that contains 1 Sep 2026
WEEKS = 52                            # 31 Aug 2026 .. 29 Aug 2027
FIRST_SPRINT = 76                     # sprint that is running when the FY opens
SPRINT_WEEKS = 2

QUARTERS = {                          # week index of first week in each quarter
    "Q1": 0,    # Sep - Nov 2026
    "Q2": 13,   # Dec 2026 - Feb 2027
    "Q3": 26,   # Mar - May 2027
    "Q4": 39,   # Jun - Aug 2027
}
QUARTER_LABELS = {
    "Q1": "Q1 FY27 (Sep-Nov 2026)",
    "Q2": "Q2 FY27 (Dec 2026-Feb 2027)",
    "Q3": "Q3 FY27 (Mar-May 2027)",
    "Q4": "Q4 FY27 (Jun-Aug 2027)",
}


def week_start(idx):
    return FY_START + timedelta(weeks=idx)


def week_label(idx):
    return week_start(idx).isocalendar()[1]


def sprint_of_week(idx):
    return FIRST_SPRINT + idx // SPRINT_WEEKS


def fmt(d):
    return d.strftime("%-d %b %Y")


# ----------------------------------------------------------------- capacity ---

TEAM = {
    "PM":     {"people": 1, "lanes": 2, "label": "1 PM",
               "note": "one PM runs two discovery tracks at a time"},
    "Design": {"people": 1, "lanes": 2, "label": "1 Designer",
               "note": "one designer runs two initiatives at a time, as in FY26"},
    "TPM":    {"people": 1, "lanes": 2, "label": "1 TPM",
               "note": "spikes and ticket breakdown for two initiatives at a time"},
    "BE":     {"people": 3, "lanes": 2, "label": "3 BE devs",
               "note": "35% reserved for tech debt and company tech goals, "
                       "leaving 2 lanes for initiatives"},
    "App":    {"people": 3, "lanes": 2, "label": "3 App devs",
               "note": "35% reserved for tech debt and company tech goals, "
                       "leaving 2 lanes for initiatives"},
    "QA":     {"people": 2, "lanes": 2, "label": "2 QAs", "note": ""},
}
TECH_RESERVE = 0.35
PHASES = ["PM", "Design", "TPM", "BE", "App", "QA"]
PHASE_LONG = {
    "PM": "Discovery, PRD and strategy (PM)",
    "Design": "Design (Figma)",
    "TPM": "Dev spike, specs and tickets (TPM)",
    "BE": "Backend development",
    "App": "App development",
    "QA": "QA and release",
}
# Colours copied from the FY26 spreadsheet legend so both sheets read the same.
PHASE_COLOR = {
    "PM": "93C47D", "Design": "FEEC68", "TPM": "FFBE7B",
    "BE": "FF8000", "App": "DA4848", "QA": "B45F06",
    "CarryOver": "CCCCCC", "Blocked": "A4C2F4",
}

SIZE_FTE = {"S": 1, "M": 2, "L": 4, "XL": 9, "XXL": 15, "-": 0}
SIZE_WORDS = {"S": "Small", "M": "Medium", "L": "Large", "XL": "Extra large",
              "-": "None"}

ASANA_PROJECT = "https://app.asana.com/1/8556634603607/project/1215564565348002/list/1215603355542208"
ASANA_FY26 = "https://app.asana.com/1/8556634603607/project/1210535324395006/list/1210535557338992"
FY26_SHEET = "https://docs.google.com/spreadsheets/d/1hK1f50qNr4Sv69JirlDSqw68bV_CzV_kJt7HgJJszDE/edit"
CONFLUENCE_MODULAR = "https://idtjira.atlassian.net/wiki/x/DIDHXAE"


def asana_url(gid):
    return f"https://app.asana.com/1/8556634603607/project/1215564565348002/task/{gid}"


# -------------------------------------------------------------- initiatives ---
# Phase effort:
#   pm, design, tpm, qa  -> calendar weeks for the single owner of that phase
#   be, app              -> FTE sprints on the FY26 scale, plus how many devs
#                           work it in parallel (1 or 2)
# Order is the proposed execution order. Quarter is the quarter in which the
# build (BE/App) is meant to land; PM may start up to 8 weeks earlier.

INITIATIVES = [
    # ------------------------------------------------------------- Q1 -------
    dict(
        id="G6", order=1, quarter="Q1", goal="Business Goal", product="MTU",
        priority="High", fy27="Carry Over", asana=["1215923982536887"],
        name="Integrate MTU transaction flow to Terminus",
        short="Terminus fraud integration",
        be="M", be_devs=1, be_left=1, app="-", app_devs=1, design="-",
        pm_w=0, design_w=0, tpm_w=0, qa_w=1,
        deps="Terminus team (fraud platform). Carry-over from FY26, backend In Progress.",
        summary="Send every IMTU purchase to Terminus for a fraud decision before the top-up is fulfilled.",
        description=(
            "Terminus is IDT's internal fraud decisioning system. Today IMTU relies on a "
            "patchwork of controls (IDT Pay checks, card BIN rules, the br-web block list) "
            "and none of them fired during the Egypt and Pakistan burner-account cash-out in "
            "August 2026. This initiative wires the IMTU purchase flow into Terminus: the "
            "backend maps the transaction, sender and recipient attributes Terminus needs, "
            "calls it synchronously inside the order flow, and honours approve, reject and "
            "review outcomes before the carrier is charged. The work is backend only and was "
            "started in FY26, so FY27 closes it rather than opening it."),
        strategy=[
            "Finish the remaining backend work in Sprint 76-77 and keep the integration behind a per-country flag so it can be enabled corridor by corridor.",
            "Start in shadow mode: log the Terminus decision without acting on it for two sprints, compare against IDT Pay and manual fraud outcomes, then switch to enforce.",
            "Add recipient-velocity attributes (top-ups per recipient number per day, distinct payer accounts per recipient) to the payload, since that is the signal the August fraud would have tripped.",
            "Define the review outcome UX with CS: an order held for review shows a pending state and a clear message instead of a generic failure.",
        ],
        metrics=["100% of IMTU orders scored by Terminus in the enforced corridors",
                 "Chargeback and refund rate on IMTU below the FY26 baseline",
                 "No increase in false declines for repeat senders (monitor decline rate of users with 3+ prior successful top-ups)"],
    ),
    dict(
        id="G4", order=2, quarter="Q1", goal="Business Goal", product="MTU",
        priority="High", fy27="Carry Over", asana=["1215922468293591"],
        name="New Channel: roll out the WhatsApp MTU chatbot",
        short="WhatsApp MTU chatbot",
        be="M", be_devs=1, app="-", app_devs=1, design="-",
        pm_w=1, design_w=0, tpm_w=1, qa_w=2,
        deps="WhatsApp Business team (chatbot and conversation design), DTC Universal API (shipped FY26), MARCOM for the entry deep link.",
        summary="Let a customer buy a top-up, pay, and check order status inside WhatsApp, on top of the DTC Universal API built in FY26.",
        description=(
            "The DTC Universal API shipped in FY26 exposes customer, product and order data to "
            "external channels, and the WhatsApp team is building the conversational layer. "
            "DCS owns the product side: offer lookup by recipient number, promo eligibility, "
            "checkout hand-off, order confirmation and status queries. The Felix Pago teardown "
            "done in August showed the winning pattern: a prefilled deep link into the chat, "
            "the carrier and offer resolved from the recipient number, and checkout in the "
            "WhatsApp in-app browser. eGift follows in a later phase once the MTU flow proves "
            "the channel."),
        strategy=[
            "Ship MTU only in FY27 Q1; eGift and status of past eGift orders are out of scope until conversion is measured.",
            "Reuse the web checkout for payment inside the WhatsApp in-app browser rather than building a chat-native payment, which keeps PCI scope and fraud controls where they already are.",
            "Expose a recipient-number lookup endpoint that returns carrier, eligible offers and promos in one call so the bot never has to chain requests.",
            "Instrument the funnel end to end (link open, number confirmed, offer picked, checkout opened, paid) with the same Amplitude taxonomy as the app so the channel can be compared with app and web.",
            "Launch to one corridor (Mexico or Guatemala) with a BLS first-purchase promo, then widen by country.",
        ],
        metrics=["Chatbot funnel conversion from offer picked to paid above 25%",
                 "At least 5% of WhatsApp buyers are new to IMTU (no prior order)",
                 "Order-status queries resolved in chat without a CS contact"],
    ),
    dict(
        id="G1", order=4, quarter="Q1", goal="Business Goal", product="MTU",
        priority="High", fy27="New", asana=["1216072967479615", "1216262799162703"],
        name="MTU modular component and cross-selling MTU on Money Transfer",
        short="MTU module + cross-sell on MT",
        be="M", be_devs=1, app="L", app_devs=2, design="M",
        pm_w=2, design_w=3, tpm_w=2, qa_w=2,
        deps="Boss Money app team (host surface), Engager for offer selection. Spec started in Confluence (Modular IMTU Component).",
        summary="Build the reusable IMTU cross-sell module once and embed it first in the Money Transfer flow.",
        description=(
            "A reusable component that presents one personalised IMTU offer inside another "
            "product's purchase flow, starting with Money Transfer in the Boss Money app. "
            "The first version keeps the IMTU purchase as a separate transaction, so no "
            "unified cart is needed. The module takes a recipient (phone number or contact), "
            "resolves the carrier and the single best offer through backend rules and remote "
            "config, and hands off to the existing IMTU checkout. Pinless, insurance, "
            "calling plans, eGift and eSIM reuse the same module later, which is why it is "
            "the first build of the year."),
        strategy=[
            "Design the module contract first (input: recipient and host context; output: one offer card plus a checkout hand-off) and freeze it before UI work so every later host integrates the same way.",
            "Present exactly one offer, chosen by a backend ranking service seeded with simple rules (last offer sent to this recipient, most popular offer for the carrier), with a hook for Engager and ML ranking in FY27 Q4.",
            "Ship the Money Transfer embed on the MT success screen first, where the sender has just confirmed a recipient and payment method, then move to the MT review screen once conversion is known.",
            "Track impression, tap, checkout open and purchase per host surface so the module's attach rate can be compared across MT, Pinless and later hosts.",
            "Keep the transaction separate in V1; a combined cart is the Bundling initiative's job.",
        ],
        metrics=["Attach rate (IMTU purchase within 24h of an MT with the module shown) above 3%",
                 "Second host (Pinless) integrated in under one sprint of App work",
                 "No regression in MT completion rate on the screens that host the module"],
    ),
    dict(
        id="B2", order=5, quarter="Q1", goal="Board Goal", product="MTU",
        priority="High", fy27="New", asana=["1218156225083577", "1215564565348037"],
        name="Reduce subscription cancellations",
        short="Subscription cancellation reduction",
        be="M", be_devs=1, app="L", app_devs=2, design="M",
        pm_w=3, design_w=3, tpm_w=2, qa_w=2,
        deps="Subly (subscription engine), CRM for the Braze savings attribute, Amplitude taxonomy fixes (DCS-5331 style) for the cancel funnel.",
        summary="Cut voluntary and accidental cancellations across the in, during and out moments of a subscription.",
        description=(
            "Subscriptions are the highest-quality IMTU revenue and the default-on toggle "
            "grew them fast, but the September exec review showed the cancel rate is the "
            "open problem: the home subscriptions widget is used mostly as a cancel surface "
            "and a share of cancels are buyer's remorse within days of an unintended "
            "opt-in. The Asana subtasks frame the work as in, during and out. In: a short "
            "remorse window with a one-tap undo. During: pause instead of cancel, and a "
            "savings message that shows what the subscription has earned. Out: an exit "
            "survey that captures the reason and offers a targeted save. Underneath, the "
            "cancel funnel needs clean events so each change can be measured."),
        strategy=[
            "Fix the measurement first: define the cancel funnel events (entry surface, reason, pause vs cancel, resubscribe) and fill the untagged properties before any UX ships, so the baseline is trustworthy.",
            "Ship 'pause for one or two cycles' as the primary action on the cancel screen, with cancel as the secondary path; pausing keeps the payment method and recipient attached.",
            "Add a 7-day remorse window after a toggle-on subscription: one tap cancels with an immediate confirmation and no future charge, which removes the support contacts and chargebacks.",
            "Exit survey with five fixed reasons plus free text; route 'too expensive' to a subscription promo (BLS) and 'recipient no longer needs it' to an edit-recipient flow.",
            "Give CRM a Braze attribute with savings to date per subscriber so lifecycle messages can quote it.",
        ],
        metrics=["Monthly voluntary cancellation rate down 20% against the Q1 baseline",
                 "At least 30% of users who open the cancel flow choose pause or keep",
                 "Cancel funnel events documented and 100% tagged with reason and surface"],
    ),
    dict(
        id="G3", order=6, quarter="Q1", goal="Business Goal", product="MTU",
        priority="Medium", fy27="New", asana=["1215922468293595"],
        name="Cross-sell 2.0: Engager cards on the MTU home page",
        short="Engager cards on MTU home",
        be="S", be_devs=1, app="M", app_devs=1, design="S",
        pm_w=2, design_w=2, tpm_w=1, qa_w=1,
        deps="Engager team (card content and targeting), BR7 MTU home redesign (shipped FY26).",
        summary="Replace the static Boss Recommends rail on the MTU home with cards served and targeted by Engager.",
        description=(
            "The redesigned MTU home ships a cross-sell rail whose content is static BMK "
            "configuration. Engager already decides which offer or message a user should "
            "see in other parts of the BR app. This initiative makes the MTU home rail an "
            "Engager placement: the backend requests cards for the user and the app renders "
            "whatever comes back (eGift, eSIM, calling plan, RAF, a subscription nudge), "
            "with impressions and taps reported back so Engager can learn. It is the "
            "cheapest path to personalised cross-sell and the prerequisite for the "
            "Personalised experiences via Engager board goal in Q4."),
        strategy=[
            "Define a small card schema (title, body, image, deep link, campaign id) that Engager fills and the app renders; anything not in the schema is rejected so the rail never breaks on unexpected content.",
            "Fall back to the current static rail when Engager returns nothing or times out, so the home page never shows an empty slot.",
            "Report impression and tap events with the Engager campaign id so marketing can measure each card and the featured_card_variant gap seen in the FY26 featured-offers test does not repeat.",
            "Start with the same four card types that exist today, then let CRM add campaigns without an app release.",
        ],
        metrics=["Rail tap-through rate at least equal to the static rail, with per-campaign reporting",
                 "New cross-sell campaign live without an app release",
                 "Zero empty-rail sessions after fallback"],
    ),
    dict(
        id="B11", order=3, quarter="Q1", goal="Board Goal", product="MTU",
        priority="High", fy27="New", asana=["1218156429240249", "1215922468293626"],
        name="Introduce postpaid top-ups (direct billers)",
        short="Postpaid top-ups",
        be="L", be_devs=2, app="S", app_devs=1, design="S",
        pm_w=2, design_w=2, tpm_w=2, qa_w=2,
        deps="K2 connectors team (biller integration), Tigo and other carriers for postpaid APIs, Finance for non-instant settlement.",
        summary="Let a sender pay a relative's postpaid mobile bill through the IMTU flow, starting with Tigo.",
        description=(
            "IMTU today only recharges prepaid numbers. Postpaid customers in Latin America "
            "are a growing share of the base, carry higher bills, and pay monthly, which "
            "makes them a natural fit for subscriptions. The FY26 Tigo postpaid work sized "
            "the connector side as Large; FY27 completes it and exposes it in the app. The "
            "flow changes: the number lookup must recognise a postpaid line, the amount is "
            "the open bill (or an open range) instead of a fixed denomination, and "
            "confirmation may not be instant."),
        strategy=[
            "Start with Tigo (Guatemala, Honduras, El Salvador) where the carrier relationship and the FY26 spike already exist; add carriers only after the first is stable.",
            "Backend owns the postpaid detection in the number lookup, bill inquiry, payment posting and asynchronous confirmation; the app changes are limited to an amount screen that shows the bill and a pending state on the success screen.",
            "Treat settlement and reconciliation as part of the scope: Finance needs a daily file per biller, and refunds for a posted bill payment follow a different path than a failed prepaid recharge.",
            "Enable subscriptions for postpaid lines in a second step once the monthly bill amount can be fetched reliably.",
        ],
        metrics=["Postpaid payments live for Tigo in three countries by end of Q1",
                 "Postpaid success rate above 97% with confirmation within 15 minutes",
                 "Postpaid share of IMTU revenue in those corridors above 5% by Q3"],
    ),
    # ------------------------------------------------------------- Q2 -------
    dict(
        id="B4", order=7, quarter="Q2", goal="Board Goal", product="All Products",
        priority="High", fy27="New", asana=["1218156429240276", "1215922468194943"],
        name="Add mobile payments (Apple Pay and Google Pay)",
        short="Apple Pay / Google Pay",
        be="L", be_devs=2, app="L", app_devs=2, design="S",
        pm_w=2, design_w=2, tpm_w=2, qa_w=3,
        deps="IDT Pay (tokenisation and processor support), Fraud team (Apple Pay fraud at 0.01%), Apple and Google merchant onboarding.",
        summary="Offer Apple Pay and Google Pay as payment methods for IMTU, eGift and eSIM in the BR calling app.",
        description=(
            "Card entry is the biggest friction in first purchase, and mobile wallets carry "
            "a fraud rate near zero (Apple Pay dropped to 0.01% in the fraud team's data). "
            "The DCS epic exists but has a single unstarted ticket, and the calling-app "
            "wallet spec deferred DCS products. This initiative adds both wallets as payment "
            "methods across the three DCS products through IDT Pay: the app collects the "
            "wallet token, the backend passes it to the processor, and the payment method is "
            "stored for subscriptions where the wallet allows it."),
        strategy=[
            "Do the IDT Pay work once for all three products: a wallet token is just another payment instrument in the order API, so IMTU, eGift and eSIM get it in the same release.",
            "Sequence Apple Pay first (single processor path, merchant validation) and Google Pay two weeks later on the same backend.",
            "Make wallets the default payment method for new users with no saved card, and keep saved cards default for existing users, then test the reverse.",
            "Support recurring charges through the wallet token where IDT Pay allows it, so a subscription created with Apple Pay does not force a card later.",
            "Extend the Terminus payload with payment method so fraud rules can treat wallet payments differently from cards.",
        ],
        metrics=["First-purchase conversion for new users up 10% where a wallet is available",
                 "Wallet share of new payment methods added above 30% within two months",
                 "Wallet fraud rate below 0.05%"],
    ),
    dict(
        id="B1", order=8, quarter="Q2", goal="Board Goal", product="MTU",
        priority="High", fy27="New", asana=["1218156225083580", "1215684148744082"],
        name="Deploy AI-powered dynamic pricing (offer price and variable fees)",
        short="AI-powered pricing",
        be="M", be_devs=1, app="S", app_devs=1, design="S",
        pm_w=3, design_w=2, tpm_w=2, qa_w=2,
        deps="Pricing team and OMTU (pricing model and service), K2 (price and fee fields), Legal for price display rules.",
        summary="Let the price and the fee of an IMTU offer be set per user and per moment by a pricing model, in both the BR and Boss Money apps.",
        description=(
            "Pricing today is one price and one fee per offer for everyone. The pricing team "
            "is building a model that sets the offer price and a variable fee from corridor, "
            "carrier, user history and time, and the FY26 spike estimated the DCS side as "
            "Small to Medium: the apps already render whatever price the backend returns. "
            "DCS's job is the integration and the guardrails: call the pricing service when "
            "offers are listed, lock the quoted price for the session, show fee and total "
            "transparently at confirmation, and make sure promos and subscriptions renew at "
            "the rules the customer agreed to."),
        strategy=[
            "Integrate through one pricing call at offer-list time that returns price, fee and a quote id; checkout validates the quote id so the customer never pays a different amount than shown.",
            "Show the exact fee and exact amount delivered on the confirmation screen (the Xoom pattern) so dynamic pricing does not read as hidden pricing.",
            "Fix the subscription rule up front: renewals charge the price at subscription time or the current price, and the choice is shown in the subscription details.",
            "Roll out by corridor behind a flag with a holdout group so revenue lift is measured, not assumed.",
            "Keep the pricing model outside DCS; DCS owns the contract, the caching and the fallback to list price when the service is unavailable.",
        ],
        metrics=["Gross margin per IMTU transaction up in the dynamically priced corridors versus holdout",
                 "No increase in checkout abandonment at the confirmation step",
                 "Pricing service fallback rate below 1%"],
    ),
    dict(
        id="G9", order=9, quarter="Q2", goal="Business Goal", product="eGIFT",
        priority="High", fy27="New", asana=["1215840097748060"],
        name="Integrate with the KVouchers platform (IDT vouchers and new flows)",
        short="KVouchers integration",
        be="L", be_devs=2, app="M", app_devs=1, design="M",
        pm_w=3, design_w=3, tpm_w=2, qa_w=2,
        deps="KVouchers platform team, Finance (breakage accounting), eGift supplier contracts.",
        summary="Move eGift onto an IDT voucher that the recipient redeems for a branded card, capturing breakage and improving cash flow and fraud control.",
        description=(
            "Today an eGift purchase issues the branded gift card immediately, so IDT pays the "
            "supplier at once and any fraud loss is realised at once. KVouchers issues an IDT "
            "voucher first; the recipient redeems it for a specific brand or any brand in the "
            "catalogue, and only then is the branded card bought. This delays supplier spend, "
            "creates breakage on unredeemed vouchers, gives a consistent branded experience, "
            "and adds a fraud checkpoint between purchase and redemption. The platform "
            "becomes the foundation of eGift, so the existing purchase flow migrates onto it "
            "and the redemption experience is new."),
        strategy=[
            "Phase the migration: first issue vouchers behind the existing purchase flow with automatic redemption to the chosen brand (no customer-visible change), then open the 'choose at redemption' flow.",
            "Design the redemption landing page with MARCOM as the piece the recipient sees; it is the brand surface of the product and the place where a BR app download can be offered.",
            "Backend owns the full voucher lifecycle: create, redeem, cancel, expire, monitor, and the daily breakage and liability report Finance needs.",
            "Put the fraud hold between purchase and redemption: high-risk purchases issue a voucher that redeems only after review, so the loss is never realised on a bad card.",
            "Keep the B2B and retail channels in mind in the API so Zendit and NRS can issue the same vouchers later.",
        ],
        metrics=["100% of DTC eGift purchases issued as KVouchers by end of Q3",
                 "Fraud loss per eGift transaction down 50% against FY26 with the redemption hold",
                 "Redemption rate and breakage reported daily; breakage revenue recognised per Finance policy"],
    ),
    dict(
        id="G2", order=10, quarter="Q2", goal="Business Goal", product="MTU",
        priority="High", fy27="New", asana=["1216072967479611"],
        name="Cross-selling MTU on Pinless (module)",
        short="MTU module on Pinless",
        be="S", be_devs=1, app="S", app_devs=1, design="S",
        pm_w=1, design_w=2, tpm_w=1, qa_w=1,
        deps="MTU modular component (G1). Calling (Pinless) product team for the host screens.",
        summary="Embed the IMTU module in the Pinless calling flow so callers to a number are offered a top-up for that number.",
        description=(
            "Pinless calling knows the number the customer just called. That number is the "
            "best possible IMTU lead: the caller cares about the person and the carrier is "
            "known from the lookup. This initiative places the module built in Q1 on the "
            "post-call screen and the recent-calls list of the BR calling app, offering a "
            "single relevant top-up for the called number. Because the module already "
            "exists, the work is the host integration, the trigger rules and the analytics."),
        strategy=[
            "Trigger on call end for international calls to IMTU-supported carriers only, at most once per recipient per week, so the offer is relevant and not a nag.",
            "Reuse the module contract from G1 unchanged; any host-specific need becomes a module feature, not a fork.",
            "Measure attach separately from MT so the two hosts can be compared and the trigger frequency tuned.",
        ],
        metrics=["Attach rate (IMTU purchase within 24h of a call with the module shown) above 2%",
                 "Integration delivered in one App sprint, proving the module is reusable",
                 "No measurable drop in Pinless redial or call volume"],
    ),
    dict(
        id="G10", order=11, quarter="Q2", goal="Business Goal", product="eGIFT",
        priority="Medium", fy27="New", asana=["1215781833204001"],
        name="Fraud: integrate the outsourced eGift security layer",
        short="eGift fraud vendor",
        be="M", be_devs=1, app="S", app_devs=1, design="-",
        pm_w=2, design_w=0, tpm_w=1, qa_w=2,
        deps="Fraud vendor (Accertify, decisioning through IDT Pay), Fraud and Finance teams; vendor go-live planned for March 2027.",
        summary="Put a specialised fraud vendor in front of every eGift purchase so more good orders are approved and fewer bad ones are paid for.",
        description=(
            "eGift is the most fraud-exposed DCS product because the goods are instant and "
            "resellable, and FY26 controls decline a very high share of attempts, much of "
            "it issuer declines that no vendor can convert. The vendor handover done in "
            "September set the real go-live for March 2027. DCS's work is the integration: "
            "device and behavioural signals collected in the app, the vendor decision "
            "consumed in the order flow, review outcomes handled, and the results fed back "
            "so the model learns. Together with KVouchers, this moves eGift from 'decline "
            "everything risky' to 'approve more, hold the risky ones'."),
        strategy=[
            "Collect the device fingerprint and behavioural signals in the app SDK first (small App change), since the vendor's accuracy depends on them being present from day one.",
            "Run the vendor in shadow for one month against IDT Pay decisions to measure lift on approvals before enforcing.",
            "Use the KVouchers redemption hold as the 'review' action so a risky order is neither declined nor fulfilled until reviewed.",
            "Send chargeback and confirmed-fraud outcomes back to the vendor weekly; without feedback the model stays static.",
        ],
        metrics=["eGift approval rate up 15 points with fraud loss flat or lower",
                 "Manual review queue under 2% of orders with 24h resolution",
                 "Vendor live for 100% of eGift orders by end of Q3"],
    ),
    dict(
        id="B7", order=12, quarter="Q2", goal="Board Goal", product="MTU",
        priority="High", fy27="New", asana=["1218156429240267", "1216112201710177"],
        name="Support sponsor calling plans and cross-sell them in the IMTU flow",
        short="Sponsor calling plans",
        be="M", be_devs=1, app="M", app_devs=1, design="S",
        pm_w=2, design_w=2, tpm_w=1, qa_w=2,
        deps="Calling plans product team (sponsor plan catalogue and provisioning), Engager for offer placement.",
        summary="Let a US sender buy a calling plan for the recipient abroad, offered at the moment they top up that recipient.",
        description=(
            "A sponsor calling plan is paid by the US customer and used by the person "
            "abroad to call back. The IMTU flow already holds the recipient and the moment "
            "of generosity, so the cross-sell is natural: after a top-up, offer a sponsored "
            "plan for the same number. DCS provides the catalogue call, the offer placement "
            "in the IMTU success screen and recipient page, and the purchase hand-off; the "
            "calling product owns provisioning."),
        strategy=[
            "Place the sponsor plan offer on the IMTU success screen and the recipient details page through the Engager card schema from G3, so it is one more campaign rather than a new surface.",
            "Backend adds a sponsor-plan eligibility call keyed by recipient number and country; the app renders the plan card and hands off to the calling plan checkout.",
            "Bundle it with a top-up in a later phase through the Bundling service, once both purchases exist separately.",
        ],
        metrics=["Sponsor plan attach rate on IMTU success above 1.5% in eligible corridors",
                 "Sponsor plan purchases from the IMTU flow above 20% of all sponsor plan sales by Q4"],
    ),
    # ------------------------------------------------------------- Q3 -------
    dict(
        id="B10", order=13, quarter="Q3", goal="Board Goal", product="All Products",
        priority="High", fy27="New", asana=["1218156429240253"],
        name="Introduce bundling capabilities for DTC",
        short="Bundling service",
        be="XL", be_devs=2, app="L", app_devs=2, design="L",
        pm_w=4, design_w=4, tpm_w=3, qa_w=3,
        deps="K2 catalogue and order services, IDT Pay (single charge, partial refunds), Finance for revenue split, product teams for bundle definitions.",
        summary="A bundling service that lets a customer buy and receive several products in one transaction, with bundle pricing.",
        description=(
            "Every cross-sell initiative so far ends in two transactions: the module offers, "
            "the customer pays twice. Bundling is the platform piece that removes that: one "
            "cart, one charge, multiple fulfilments (top-up plus eGift, top-up plus eSIM, "
            "top-up plus sponsor plan), with the option of a bundle price or discount. It is "
            "the largest build of the year, mostly backend: bundle definition, price "
            "composition, one payment, orchestration of fulfilments with partial-failure "
            "handling, and the refund and reporting rules that follow. The app side is a "
            "cart and a combined review screen."),
        strategy=[
            "Run PM and Design through Q2 so the backend can start on day one of Q3; this is the only initiative that needs a full quarter of two backend developers.",
            "Scope V1 to two-item bundles defined by IDT (not user-built carts), IMTU as the anchor item, and one payment; open-ended carts and user-built bundles come after V1 proves attach.",
            "Design fulfilment as an orchestration with compensating actions: if the second item fails after the first succeeded, refund the second automatically and tell the customer exactly what was delivered.",
            "Reuse the module (G1) as the surface that proposes a bundle, so the customer path is 'add to my top-up' rather than a new shop.",
            "Agree the revenue split and discount accounting with Finance before build, since bundle pricing changes how each product line reports revenue.",
        ],
        metrics=["First IDT-defined bundle (top-up + eGift) live by end of Q3",
                 "Average order value of bundled orders at least 40% above a single top-up",
                 "Partial fulfilment incidents resolved automatically with no manual refunds"],
    ),
    dict(
        id="B8", order=14, quarter="Q3", goal="Board Goal", product="All Products",
        priority="High", fy27="New", asana=["1218156429240264", "1215922468194936", "1215922468194932"],
        name="Expand the BR app in ROW markets (Pinless, IMTU and eSIM)",
        short="ROW market expansion",
        be="L", be_devs=2, app="L", app_devs=2, design="M",
        pm_w=4, design_w=3, tpm_w=2, qa_w=3,
        deps="Country launch programme (legal, tax, payments per market), IDT Pay local payment methods, Calling (Pinless) team, K2 offer catalogue per market.",
        summary="Take the BR calling app international with IMTU and eSIM enabled per market, not just US-origin sales.",
        description=(
            "The BR app sells IMTU and eSIM to US customers. The FY27 board goal is to "
            "launch and operate the app in rest-of-world markets (Europe and Canada first) "
            "with Pinless, IMTU and eSIM. For DCS this means market-aware catalogues, "
            "currencies and taxes, local payment methods through IDT Pay, sender-country "
            "rules for fraud and promos, localisation, and store listings. The FY26 Portuguese "
            "translation and the market flags in the offer catalogue are the starting point."),
        strategy=[
            "Pick two launch markets with the country programme (proposal: Spain and Canada) and build every capability as market configuration rather than code paths, so market three costs configuration and content.",
            "Backend: sender-market dimension across catalogue, pricing, promos, fraud rules and reporting; App: currency and tax display, market selector at onboarding, localisation for the launch languages.",
            "Land eSIM as a first-class product in the new markets from day one, since travel eSIM is the product with the clearest ROW demand.",
            "Launch soft (no marketing) for one sprint per market to shake out payments and support before MARCOM spends.",
        ],
        metrics=["BR app live in two ROW markets with IMTU and eSIM by end of Q4",
                 "Payment success rate in new markets above 90% within two months",
                 "Third market enabled with configuration only, no app release"],
    ),
    dict(
        id="B5", order=15, quarter="Q3", goal="Board Goal", product="All Products",
        priority="Medium", fy27="New", asana=["1218156429240273"],
        name="Support the RAF program with a fully trackable journey",
        short="Refer-a-Friend journey",
        be="M", be_devs=1, app="M", app_devs=1, design="S",
        pm_w=2, design_w=2, tpm_w=2, qa_w=2,
        deps="DTC Core (RAF platform, shipped FY26), CRM for reward messaging, Data team for attribution reporting.",
        summary="Instrument and complete the Refer-a-Friend journey from invite to first transaction to reward payout so every step is measurable.",
        description=(
            "The new RAF platform launched in FY26 with a $5 IMTU reward, but attribution "
            "is still partial: invites, installs, first purchase and payout live in different "
            "systems and the RAF event documentation was a recurring chore. This initiative "
            "closes the loop in the DCS products: a referral code or link carried through "
            "install and first IMTU, eGift or eSIM purchase, reward issuance visible to both "
            "parties, and a single funnel in Amplitude and the data warehouse. The IMTU "
            "Request Top-Up and Gifting ideas both need this loop to work."),
        strategy=[
            "Define the RAF event contract once (invite sent, link opened, installed, registered, first purchase, reward issued, reward redeemed) with referrer and referee ids on every event, and make it the acceptance criteria for every surface.",
            "Backend attaches the referral to the account at registration and evaluates the reward on first qualifying purchase across all DCS products, not only IMTU.",
            "App shows the referrer a live status of each invite (installed, purchased, reward paid) so the feature explains itself and support contacts fall.",
            "Report weekly: invites, conversion per step, reward cost per acquired customer, and share of referees who transact again within 30 days.",
        ],
        metrics=["100% of RAF rewards attributable to an invite event",
                 "Referee 30-day repeat rate reported and above 40%",
                 "RAF cost per acquired transacting customer known and below paid CAC"],
    ),
    dict(
        id="G7", order=16, quarter="Q3", goal="Business Goal", product="MTU",
        priority="Medium", fy27="Carry Over", asana=["1215836632250426"],
        name="Request Top-Up (SMS based)",
        short="Request Top-Up",
        be="M", be_devs=1, app="M", app_devs=1, design="M",
        pm_w=2, design_w=3, tpm_w=2, qa_w=2,
        deps="MARCOM (landing page and SMS templates), SMS gateway, RAF platform for the referral hook.",
        summary="Let a recipient abroad ask a sender for a top-up by SMS, landing the sender in a prefilled purchase flow.",
        description=(
            "Request Top-Up turns the recipient into an acquisition channel. The recipient "
            "sends a request from a lightweight web page or by replying to an SMS; the sender "
            "receives an SMS with a link that opens the app (or web) with the number, carrier "
            "and suggested amount prefilled. Senders who are not BR customers land in "
            "onboarding with a RAF credit. The FY26 board carried it as a business spike; "
            "FY27 builds it once the RAF loop and the WhatsApp channel exist to amplify it."),
        strategy=[
            "Build the request as a deep link with a signed payload (recipient, carrier, amount, requester id) so the same link works for app, web and, later, WhatsApp.",
            "Backend: request creation, SMS dispatch, request status, and expiry; App: a 'request received' entry that opens a prefilled checkout, and a request history for the sender.",
            "Route non-customer senders through onboarding with the RAF reward so every request that converts also acquires a sender.",
            "Cap requests per recipient per week and require sender opt-out handling so the channel does not become spam.",
        ],
        metrics=["Request to paid top-up conversion above 15%",
                 "At least 10% of converted requests come from senders new to BR",
                 "SMS complaint rate below 0.1%"],
    ),
    dict(
        id="G11", order=17, quarter="Q3", goal="Business Goal", product="eSIM",
        priority="Medium", fy27="New", asana=["1215728501648860"],
        name="eSIM location-based improvements",
        short="eSIM location features",
        be="S", be_devs=1, app="M", app_devs=1, design="S",
        pm_w=2, design_w=2, tpm_w=1, qa_w=2,
        deps="eSIM supplier (coverage and usage data), OS location permissions.",
        summary="Use the traveller's location and trip context to recommend, activate and top up the right eSIM plan at the right moment.",
        description=(
            "The eSIM funnel converts 2.3% end to end and loses most users at order review, "
            "partly because the customer has to know which region plan they need. Location "
            "awareness fixes the recommendation: detect the destination from the device "
            "locale, trip dates or arrival, propose the matching regional plan, remind the "
            "traveller to install before departure, and offer a data top-up when usage is "
            "high in-country. It also positions the eSIM product for the ROW expansion, "
            "where the customer is the traveller rather than the sender."),
        strategy=[
            "Ask for location permission only at the moment it helps (plan search and arrival), never at app start, and degrade gracefully to a country picker.",
            "Recommend one plan per detected destination on the eSIM home and the order review, and prefill it, which is where the funnel loses 63% today.",
            "Trigger 'you have arrived, activate now' and 'running low, add data' notifications through the validity-reminder service shipped in FY26.",
            "Put a usage widget with location context on the calling app home in a later step, once the recommendation converts.",
        ],
        metrics=["eSIM order review to purchase conversion up 10 points",
                 "Activation within 24h of arrival above 80% for plans bought before travel",
                 "In-trip data top-up rate above 15%"],
    ),
    # ------------------------------------------------------------- Q4 -------
    dict(
        id="B6", order=18, quarter="Q4", goal="Board Goal", product="All Products",
        priority="Medium", fy27="New", asana=["1218156429240270"],
        name="Personalised experiences via Engager (ML-driven)",
        short="Engager personalisation",
        be="M", be_devs=1, app="M", app_devs=1, design="M",
        pm_w=3, design_w=3, tpm_w=2, qa_w=2,
        deps="Engager and Data Science teams (ML models and next-best-offer), CRM (Braze), G3 Engager cards as the delivery surface.",
        summary="Expand Engager from cards on one rail to personalised home layouts, offers and lifecycle campaigns driven by ML models.",
        description=(
            "With Engager cards live on the MTU home (G3) and the module ranking hook in "
            "place (G1), FY27 Q4 turns them into a personalisation layer: the home order of "
            "sections, the featured offer, the module's single offer and the Braze lifecycle "
            "messages are all chosen per user by models trained on transaction history. DCS "
            "provides the placements, the feature events the models need, and the "
            "experimentation hooks; Data Science owns the models."),
        strategy=[
            "Ship the data first: a clean event and feature contract (recipient history, cadence, offer taken, promo response) exported to the model team by end of Q3 so models train while DCS builds placements.",
            "Make three surfaces Engager-controlled: MTU home section order, the featured offer, and the module's offer choice; each with a control group.",
            "Every personalised decision carries a model version and decision id in analytics so lift can be attributed and rolled back.",
            "Start with next-best-offer for IMTU repeat senders, the largest and best-understood population, before widening to eGift and eSIM.",
        ],
        metrics=["IMTU repeat-purchase rate up 5% in the personalised group versus control",
                 "Three Engager-controlled surfaces live with holdouts",
                 "Model-to-app latency under 200 ms at the 95th percentile"],
    ),
    dict(
        id="B9", order=19, quarter="Q4", goal="Board Goal", product="All Products",
        priority="Medium", fy27="New", asana=["1218156429240261"],
        name="Promo balances support for the BR Wallet",
        short="Promo balances in Wallet",
        be="L", be_devs=2, app="M", app_devs=1, design="S",
        pm_w=2, design_w=2, tpm_w=2, qa_w=2,
        deps="BR Wallet team (balance types and ledger), BLS promo engine, Boss Money app team, Finance for promo liability.",
        summary="Make promotional balances earned through Boss products spendable from the Wallet in both apps, across all products including Pinless.",
        description=(
            "Promotions today pay out as product-specific credits: an IMTU discount, an eGift "
            "bonus, a RAF airtime reward. The Wallet integration shipped in FY26 made the "
            "stored balance a payment method for DCS products. This initiative adds a promo "
            "balance type to the Wallet so any campaign can pay a reward once and the customer "
            "spends it on any product in either app. Pinless is excluded as a source of "
            "promos but included as a place to spend them. It turns scattered incentives into "
            "one loyalty currency, which the gamification work then draws on."),
        strategy=[
            "Agree the balance model with the Wallet team first: promo balance as a separate bucket with expiry, spend order (promo before cash), and per-product spend rules.",
            "Backend maps BLS promo payouts to Wallet promo credits and applies them at checkout for IMTU, eGift, eSIM and Pinless; App shows the promo balance, its expiry and what it can be spent on.",
            "Migrate one existing campaign (RAF $5 reward) to the Wallet promo balance as the pilot before opening it to all campaigns.",
            "Report promo liability and breakage to Finance from the Wallet ledger rather than from each product.",
        ],
        metrics=["Promo balance redeemable in both apps across all four products",
                 "Share of promo credits spent within 30 days above 60%",
                 "RAF reward migrated with no increase in support contacts"],
    ),
    dict(
        id="B3", order=20, quarter="Q4", goal="Board Goal", product="MTU",
        priority="Medium", fy27="New", asana=["1218156225083574"],
        name="Support the IVA migration for MTU",
        short="IVA migration",
        be="M", be_devs=1, app="-", app_devs=1, design="-",
        pm_w=2, design_w=0, tpm_w=2, qa_w=2,
        deps="IVA (Intelligent Virtual Agent) programme team, CSA and IVR teams, DTC Universal API (CSA connector shipped FY26).",
        summary="Move the MTU credit card purchase and self-service flows from the legacy IVR to the AI virtual agent without losing context.",
        description=(
            "The legacy IVR still sells top-ups by phone and handles balance and order "
            "questions. The company-wide IVA programme replaces the IVR with a conversational "
            "agent, and MTU is one of the flows to migrate. DCS provides the APIs the agent "
            "calls: recipient lookup, offer list, promo eligibility, payment with a stored "
            "card, order status, and the ability to carry context (caller identity, recipient, "
            "partially completed order) between the agent and the app or an agent hand-off. "
            "The DTC Universal API CSA connector is the base."),
        strategy=[
            "Expose the MTU flow as a small set of stateless API calls plus a context token, so the IVA can resume a purchase after a hand-off or a dropped call.",
            "Support only stored-card and Wallet payment in the agent; new card capture stays in the app or with a human agent, keeping PCI scope unchanged.",
            "Mirror the app's promo and pricing rules exactly so a phone customer sees the same offer and price as an app customer.",
            "Migrate self-service (order status, cancel a subscription) first, purchase second, so the agent handles volume before it handles money.",
        ],
        metrics=["MTU IVR call volume down 80% after migration",
                 "Phone purchase completion rate at least equal to the IVR baseline",
                 "Context preserved on 100% of hand-offs (no re-asking the recipient number)"],
    ),
    dict(
        id="G8", order=21, quarter="Q4", goal="Business Goal", product="All Products",
        priority="Medium", fy27="Carry Over", asana=["1215836632250433"],
        name="MTU gamification",
        short="Gamification",
        be="M", be_devs=1, app="L", app_devs=2, design="L",
        pm_w=3, design_w=4, tpm_w=2, qa_w=2,
        deps="BLS promo engine, Braze in-app messages (FY26 punch cards), Wallet promo balance (B9) for rewards, Loyalty team.",
        summary="A cross-product programme of missions, streaks and surprise rewards that drives repeat purchase and product exploration.",
        description=(
            "FY26 shipped the first mechanics as Braze in-app messages: punch cards and "
            "first-purchase promos. FY27 turns them into a programme: missions with visible "
            "progress, time-limited offers, occasional surprise games, a monthly calendar and "
            "sharing of prizes, each targeted to a customer segment. Mechanics and rewards are "
            "decided per product. It sits late in the year deliberately so it can pay rewards "
            "into the Wallet promo balance and be targeted by Engager rather than by static "
            "segments."),
        strategy=[
            "Build a mission engine in the backend (definition, progress tracking from order events, reward issuance) and keep the presentation in Braze and the app so marketing can launch missions without releases.",
            "Reuse the FY26 punch card as the first mission type; add streaks (top up three months in a row) and cross-product missions (top-up plus eGift) as the second and third.",
            "Pay rewards as Wallet promo balance where B9 is live, BLS promos where it is not.",
            "Measure incrementality with holdouts per mission; retire mechanics that do not lift repeat rate within two cycles.",
        ],
        metrics=["Repeat purchase rate of mission participants 10% above matched holdout",
                 "At least 20% of active IMTU users enrolled in a mission in the first quarter after launch",
                 "New mission launched by marketing without an app release"],
    ),
    dict(
        id="G5", order=22, quarter="Q4", goal="Business Goal", product="MTU",
        priority="Low", fy27="New", asana=["1215922468293585"],
        name="Introduce crypto payment checkout",
        short="Crypto checkout",
        be="M", be_devs=1, app="S", app_devs=1, design="S",
        pm_w=2, design_w=2, tpm_w=1, qa_w=2,
        deps="Triple-A (crypto payment processor), IDT Pay adapter, Legal and Compliance, Finance for fiat settlement.",
        summary="Accept crypto payments for IMTU through Triple-A, settled in fiat, with no crypto custody at IDT.",
        description=(
            "The architecture was defined in July 2026: Triple-A acts as the processor, the "
            "customer pays from their own wallet, IDT receives fiat, and IDT Pay gains an "
            "adapter so crypto is one more payment method in the order flow. It is a Low "
            "priority business goal aimed at a specific segment (crypto-native diaspora in "
            "corridors like Nigeria and Venezuela), so it lands in Q4 after the payments work "
            "that has broader impact. The Asana subtask to run an education call with "
            "Triple-A is the PM entry point."),
        strategy=[
            "Implement through the IDT Pay adapter model so the app change is a payment-method tile and a hosted payment page, with no wallet logic in the app.",
            "Handle the lifecycle states defined in the architecture document (created, awaiting payment, underpaid, confirmed, expired, refunded) in the backend with a clear customer message for each.",
            "Launch for IMTU only, in two corridors, behind a flag; extend to eGift only if fraud results are clean, since eGift is the higher-risk product for irreversible payments.",
        ],
        metrics=["Crypto payment success rate above 90% of initiated payments",
                 "Refund and underpayment cases resolved automatically in over 95% of cases",
                 "Share of IMTU volume in the pilot corridors paid in crypto measured and reported"],
    ),
]

# FY26 work that is still in flight when FY27 opens. These rows occupy App and
# QA lanes in the first sprints so the FY27 start dates are realistic.
CARRY_OVERS = [
    dict(id="C1", name="Subscription: BLS promos specific for subscriptions",
         product="MTU", be_w=2, app_w=2, app_devs=1, qa_w=2),
    dict(id="C2", name="Redesign MTU Home Page (cross-sell) rollout",
         product="MTU", be_w=0, app_w=2, app_devs=1, qa_w=2),
    dict(id="C3", name="Cross Sell: success page expiring x-sell deal",
         product="All Products", be_w=0, app_w=1, app_devs=1, qa_w=1),
    dict(id="C4", name="Improve BE and APP errors presented to users",
         product="MTU", be_w=2, app_w=2, app_devs=1, qa_w=1),
]

TECH_DEBT_ROWS = [
    ("Company tech goals and tech debt (35% of DCS capacity)",
     "Unit test coverage, service consolidation, transaction-history storage, platform "
     "upgrades and the standing company tech goals. Reserved capacity, not scheduled per item.",
     "XL", "XL"),
]


def by_id(iid):
    return next(i for i in INITIATIVES if i["id"] == iid)


def be_fte(i):
    return i.get("be_left", SIZE_FTE[i["be"]])


def app_fte(i):
    return SIZE_FTE[i["app"]]


def phase_weeks(i):
    """Calendar weeks each phase takes, given the devs assigned."""
    be_w = 0 if be_fte(i) == 0 else max(1, round(be_fte(i) * SPRINT_WEEKS / i["be_devs"]))
    app_w = 0 if app_fte(i) == 0 else max(1, round(app_fte(i) * SPRINT_WEEKS / i["app_devs"]))
    return {"PM": i["pm_w"], "Design": i["design_w"], "TPM": i["tpm_w"],
            "BE": be_w, "App": app_w, "QA": i["qa_w"]}


if __name__ == "__main__":
    tot_be = sum(be_fte(i) for i in INITIATIVES)
    tot_app = sum(app_fte(i) for i in INITIATIVES)
    cap = WEEKS // SPRINT_WEEKS
    print(f"{len(INITIATIVES)} initiatives")
    print(f"BE demand {tot_be} FTE sprints vs {TEAM['BE']['lanes'] * cap} available lanes-sprints")
    print(f"App demand {tot_app} FTE sprints vs {TEAM['App']['lanes'] * cap} available lanes-sprints")
    for i in INITIATIVES:
        print(i["order"], i["id"], i["quarter"], i["short"], phase_weeks(i))
