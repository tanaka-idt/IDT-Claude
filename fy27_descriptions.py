#!/usr/bin/env python3
"""
Rewritten, fuller descriptions for the 22 FY27 initiatives (16 Sep 2026).

Each entry is plain text with paragraphs separated by a blank line so the
same text can be dropped into a spreadsheet cell, a Google Doc and the HTML
page. The original one-paragraph descriptions stay in fy27_plan_data.py so
the spreadsheet can show both side by side.

Facts come from the Asana boards, Slack (#ibp-dev, #ibp-product-hub,
#tf-expand-mtu-esim-row-apps, #dba-support, #k2_qa), the Digital Payments
Program Management log, the FY26 estimation sheet and the DCS analyses done
in August and September 2026.
"""

LONG = {}

LONG["G6"] = """\
Send every IMTU purchase to Terminus, IDT's internal fraud decisioning system, and act on its answer before the carrier is charged. Terminus receives the transaction, the payer and the recipient attributes, returns approve, reject or review, and the order flow honours the outcome. Today IMTU relies on IDT Pay checks, card BIN rules and the br-web block list, and none of them fired during the Egypt and Pakistan burner-account cash-out of late August 2026, when cards that authorised cleanly funded hundreds of prepaid top-ups into a handful of recipient numbers.

The backend work started in FY26 and is In Progress, so FY27 closes it rather than opening it. The integration ships behind a per-country flag and runs in shadow mode first: Terminus decisions are logged and compared with IDT Pay and manual fraud outcomes for two sprints before enforcement is switched on. The payload adds the recipient-velocity signals the August fraud would have tripped: top-ups per recipient number per day and distinct payer accounts per recipient.

DCS scope: the Terminus call inside the order flow, the payload mapping, the review outcome (a held order shows a pending state and a clear message instead of a generic failure, agreed with Customer Service), and the shadow-versus-enforce reporting. Dependencies: the Terminus team for rules and thresholds, Fraud for the enforcement decision per corridor."""

LONG["G4"] = """\
Let a customer buy a top-up inside WhatsApp: open a chat from a prefilled deep link, confirm the recipient number, pick from the offers the bot resolves for that carrier, pay, and receive the confirmation and later the order status in the same conversation. The DTC Universal API shipped in FY26 already exposes customer, product and order data to external channels, and the WhatsApp Business team builds the conversational layer on top of it.

DCS owns the product side of the channel: a recipient-number lookup that returns carrier, eligible offers and promos in one call so the bot never chains requests; the checkout hand-off, which reuses the web checkout inside the WhatsApp in-app browser so PCI scope and fraud controls stay where they are; order confirmation and status queries; and the same Amplitude event taxonomy as the app so the channel can be compared with app and web. The Felix Pago teardown done in August 2026 showed this exact pattern converting well for a competitor.

The FY27 scope is MTU only, launched in one corridor (Mexico or Guatemala) with a BLS first-purchase promo, then widened by country. eGift and the status of past eGift orders wait until conversion is measured. Dependencies: the WhatsApp Business team for the bot, MARCOM for the entry link and campaigns, the promo engine for the launch offer."""

LONG["B11"] = """\
Let a BR customer pay a family member's postpaid mobile bill from the top-up flow, starting with Tigo Guatemala. Instead of choosing a fixed amount, the flow looks up the bill for the recipient's number, shows the amount due, takes payment and confirms once the carrier posts it, which is not always instant. Postpaid customers are a growing share of the base in Central America, carry higher monthly amounts, and are a natural fit for subscriptions later.

The mechanics already exist on the K2 side. International Bill Pay (IBP) is the K2 platform built by the Core team through FY25 and FY26: catalogue fields, a bill simulator, brand endpoints, refunds, cutoff times, and connectors for Finch (Mexico billers), Banco Industrial (Guatemala utilities) and Tigo GT postpaid mobile and home internet bills. The Tigo GT connector has been waiting for deployment since March 2026; the production connection was tested, the daily reconciliation files to Tigo's SFTP still arrive empty (OMTU-8315), and a joint production test with Tigo has not happened. Zendit B2B is the first channel to use IBP; no DTC channel is wired yet. In Asana this goal is blocked by the DPC task Support Post Paid Top Ups (Core).

DCS scope is therefore the DTC flow rather than a carrier integration: a number lookup that tells postpaid from prepaid (Twilio only says mobile or landline; David Phelps proposed a K2 lookup returning postpaid with a bill, postpaid without a bill, or prepaid), the bill-details screen replacing the denomination list, pending and failure states, receipts, and reconciliation reporting for Finance. Open items: the Core team deploying and jointly testing Tigo GT in production, commercial terms with Tigo (still open in March 2026), bill amount and compliance limits, and which carriers follow Tigo."""

LONG["G1"] = """\
Build one reusable IMTU cross-sell component and embed it first in the Boss Money Transfer flow. The module takes a recipient (phone number or contact) plus the host context, resolves the carrier and a single best offer, renders one offer card, and hands off to the existing IMTU checkout. The purchase stays a separate transaction in this version, so no unified cart is needed; combining purchases is the Bundling initiative's job. Pinless, insurance, calling plans, eGift and eSIM reuse the same module later, which is why it is one of the first builds of the year. The starting spec is the Modular IMTU Component page on Confluence.

The module contract (input: recipient and host context; output: one offer card and a checkout hand-off) is designed and frozen before UI work so every later host integrates the same way. The offer is chosen by a backend ranking service seeded with simple rules (last offer sent to this recipient, most popular offer for the carrier) and carries a hook for Engager and ML ranking in Q4. The first embed goes on the Money Transfer success screen, where the sender has just confirmed a recipient and a payment method, and moves to the review screen once conversion is known.

DCS scope: module contract, ranking service, module UI, the Money Transfer embed, and impression, tap, checkout-open and purchase events per host surface so attach rates can be compared across hosts. Dependencies: the Boss Money app team for the host screens, Engager for later offer selection."""

LONG["B2"] = """\
Cut voluntary and accidental subscription cancellations at the three moments of a subscription: in, during and out. Subscriptions are the highest-quality IMTU revenue and the default-on toggle grew them quickly, but the September 2026 executive review showed the cancel rate is the open problem. The home-page subscriptions widget is used mostly as a cancel surface, a share of cancels are buyer's remorse within days of an unintended opt-in, and the duplicate-timer analysis found users double-billed by surplus active subscriptions.

In: a seven-day remorse window after a toggle-on subscription with a one-tap cancel and immediate confirmation, which removes support contacts and chargebacks. During: pause for one or two cycles as the primary action on the cancel screen, with cancel as the secondary path, keeping recipient and payment method attached, plus a savings message showing what the subscription has earned. Out: an exit survey with five fixed reasons and free text, routing "too expensive" to a subscription promo and "recipient no longer needs it" to an edit-recipient flow. Underneath, the cancel funnel gets clean events (entry surface, reason, pause versus cancel, resubscribe) before any UX ships, so the baseline is trustworthy.

DCS scope: the measurement fix, the three flows above, and a Braze attribute with savings to date per subscriber for CRM lifecycle messages. Dependencies: Subly (subscription engine) for pause and remorse handling, CRM for the Braze journeys, the Amplitude taxonomy clean-up."""

LONG["G3"] = """\
Replace the static Boss Recommends rail on the redesigned MTU home page with cards served and targeted by Engager. Today the rail content is BMK configuration that everyone sees. Engager already decides which offer or message a user sees in other parts of the BR app (Boss Club dialogs, panels), so the MTU home becomes one more Engager placement: the backend requests cards for the user, the app renders whatever comes back (eGift, eSIM, calling plans, RAF, a subscription nudge), and impressions and taps are reported back with the campaign id so Engager can learn and marketing can measure each card.

The app renders a small card schema (title, body, image, deep link, campaign id) and rejects anything outside it so the rail never breaks on unexpected content. When Engager returns nothing or times out, the current static rail is shown, so the home page never has an empty slot. The first release carries the same four card types that exist today; after that CRM adds campaigns without an app release. The event tagging is defined up front so the featured_card_variant gap seen in the FY26 featured-offers test (untagged on most taps) does not repeat.

This is the cheapest path to personalised cross-sell and the prerequisite for the Personalised experiences via Engager goal in Q4. Dependencies: the Engager team for card content and targeting, the BR7 MTU home redesign shipped in FY26."""

LONG["B4"] = """\
Offer Apple Pay and Google Pay as payment methods for IMTU, eGift and eSIM in the BR Calling App. Card entry is the biggest friction in a first purchase, and mobile wallets carry a fraud rate near zero (Apple Pay dropped to 0.01% in the fraud team's data). The DCS epic exists with a single unstarted ticket and the calling-app wallet spec deferred DCS products, so this goal funds the DCS side properly. Arun Gatta's Apple and Google Pay working group is already defining the backend path for the calling app (wallet token exchanged for a payment handle that is passed to PSF), and DCS builds on the same IDT Pay path.

The IDT Pay work is done once for all three products: a wallet token is one more payment instrument in the order API, so IMTU, eGift and eSIM get it in the same release. Apple Pay ships first (merchant validation, single processor path) and Google Pay two weeks later on the same backend. Wallets become the default for new users with no saved card, saved cards stay default for existing users, and the reverse is tested. Recurring charges use the wallet token where IDT Pay allows it, so a subscription created with Apple Pay never forces a card later. Payment method is added to the Terminus payload so fraud rules can treat wallets differently from cards.

DCS scope: the app payment sheets and stored-method handling on iOS and Android, the order API and IDT Pay integration for wallet tokens, subscription support, analytics. Dependencies: IDT Pay for tokenisation and processor support, Fraud, Apple and Google merchant onboarding, the calling app team for the shared wallet components."""

LONG["B1"] = """\
Let the price and the fee of an IMTU offer be set per user and per moment by a pricing model, in both the BR and Boss Money apps. Today every customer sees one price and one fee per offer. The pricing team is building a model that sets the offer price and a variable fee from corridor, carrier, user history and time; the FY26 spike sized the DCS side as Small to Medium because the apps already render whatever price the backend returns.

DCS owns the integration and the guardrails, not the model. One pricing call at offer-list time returns price, fee and a quote id; checkout validates the quote id so the customer never pays a different amount than shown. The confirmation screen shows the exact fee and the exact amount delivered so dynamic pricing does not read as hidden pricing. The subscription rule is fixed up front (renewals charge the price at subscription time or the current price, stated in the subscription details). Rollout is by corridor behind a flag with a holdout group so revenue lift is measured, not assumed, and the backend falls back to list price when the pricing service is unavailable.

DCS scope: the pricing contract, caching and fallback, quote validation at checkout, the transparency changes on confirmation, the subscription renewal rule, holdout instrumentation. Dependencies: the pricing team and OMTU for the model and service, K2 for price and fee fields, Legal for price display rules."""

LONG["G9"] = """\
Move eGift onto an IDT voucher that the recipient redeems for a branded gift card, instead of issuing the branded card at purchase. With KVouchers, the customer buys an IDT voucher; the recipient redeems it for a specific brand or any brand in the catalogue, and only then is the branded card bought from the supplier. This delays supplier spend, creates breakage on unredeemed vouchers, gives a consistent branded experience, and adds a fraud checkpoint between purchase and redemption, since a risky purchase can be held before any value is issued. The platform becomes the foundation of eGift, so the existing purchase flow migrates onto it and the redemption experience is new.

The migration is phased. First, vouchers are issued behind the existing purchase flow with automatic redemption to the chosen brand, with no customer-visible change. Then the choose-at-redemption flow opens. The redemption landing page is designed with MARCOM, because it is the brand surface the recipient sees and the place to offer a BR app download. The API is shaped so Zendit B2B and NRS retail can issue the same vouchers later.

DCS scope: the app purchase flow on the new platform, the redemption experience, the fraud hold between purchase and redemption, the daily breakage and liability report for Finance. Backend owns the full voucher lifecycle: create, redeem, cancel, expire, monitor. Dependencies: the KVouchers platform team, Finance for breakage accounting, eGift supplier contracts."""

LONG["G2"] = """\
Embed the IMTU module in the Pinless calling flow of the BR Calling App, so a caller is offered a top-up for the number they just called. Pinless knows the called number, the caller cares about that person, and the carrier is known from the lookup, which makes it the best possible IMTU lead. The module built for the Money Transfer flow is placed on the post-call screen and in the recent-calls list, offering one relevant top-up for the called number.

Because the module already exists, the work is the host integration, the trigger rules and the analytics. The offer triggers on call end for international calls to IMTU-supported carriers only, at most once per recipient per week, so it stays relevant. The module contract is reused unchanged; any host-specific need becomes a module feature rather than a fork. Attach is measured separately from Money Transfer so the two hosts can be compared and the trigger frequency tuned.

Dependencies: the MTU modular component (initiative 4) and the Calling (Pinless) product team for the host screens. Delivering it in one App sprint is itself a success measure, because it proves the module is reusable."""

LONG["G10"] = """\
Put a specialised fraud vendor in front of every eGift purchase so more good orders are approved and fewer bad ones are paid for. eGift is the most fraud-exposed DCS product because the goods are instant and resellable. FY26 controls decline a very high share of attempts, but the September 2026 vendor handover showed that much of it is issuer declines that no vendor can convert, and that Visa being switched off since 28 August adds several points on top. Decisioning runs through Accertify via IDT Pay, and the realistic go-live is March 2027, which is why the build sits in Q2.

DCS's work is the integration around the vendor. The device fingerprint and behavioural signals are collected in the app SDK first, a small App change, because the vendor's accuracy depends on them being present from day one. The vendor runs in shadow for one month against IDT Pay decisions to measure lift on approvals before enforcing. The KVouchers redemption hold becomes the review action, so a risky order is neither declined nor fulfilled until reviewed. Chargeback and confirmed-fraud outcomes go back to the vendor weekly; without that feedback the model stays static.

DCS scope: SDK signal collection, consuming the decision in the order flow, review handling, the feedback file, approval and loss reporting. Dependencies: the fraud vendor and IDT Pay, the Fraud and Finance teams, KVouchers for the hold."""

LONG["B7"] = """\
Let a US customer buy a calling plan for a family member abroad from the IMTU flow. After a top-up, and on the recipient page, if the recipient number belongs to a BR account in a RoW or RoRoW market, the sender is offered to sponsor a calling plan for that number; the sender pays with the card on file and the plan is assigned to the recipient's account so the relative can call back. The top-up sender has already told us who they care about, so the moment of generosity is the right time to make the offer.

The sponsorship mechanics are being built by the ADMI team as "USA-Sponsored RoW Calling": a sponsorship record linking the sponsor's account to the sponsored account (kept in the Oracle Debit database, decided July 2026), plan assignment through the existing plan store and PSF, renewal and cancellation. DCS builds the cross-sell on top: an eligibility lookup by recipient number (does a BR account abroad exist, which plans apply), the offer placement on the IMTU success screen and the recipient page through the Engager card schema so marketing controls it, the purchase hand-off with the sponsor's payment method, confirmation and analytics.

Open items for the PRD: which plans and destination countries are in the first release and their US dollar prices; what happens when the recipient has no BR account (invite by SMS, or offer only to numbers that already have one); the renewal model and who can cancel; whether the sponsor sees the plan in their own subscriptions list; and attribution between DCS and Calling. Dependencies: ADMI for the sponsorship feature, the Calling product for the plan catalogue, and the ROW expansion, which grows the sponsorable base."""

LONG["B10"] = """\
Build a bundling service so a customer can buy and receive several products in one transaction with bundle pricing: a top-up plus an eGift, a top-up plus an eSIM, a top-up plus a sponsored calling plan. Every cross-sell initiative so far ends in two transactions: the module offers, the customer pays twice. Bundling removes that with one cart, one charge and several fulfilments, with the option of a bundle price or discount. It is the largest build of the year and mostly backend.

Version one is deliberately narrow: two-item bundles defined by IDT (not user-built carts), IMTU as the anchor item, one payment. Open carts and user-built bundles come after V1 proves attach. Fulfilment is an orchestration with compensating actions: if the second item fails after the first succeeded, the second is refunded automatically and the customer is told exactly what was delivered. The IMTU module is the surface that proposes a bundle, so the customer path is "add to my top-up" rather than a new shop. PM and Design run through Q2 so the backend can start on the first day of Q3 with two developers for the full quarter.

DCS scope: bundle definition and price composition, single payment through IDT Pay with partial refunds, fulfilment orchestration and partial-failure handling, refund and reporting rules, the cart and combined review screen in the app. The revenue split and discount accounting are agreed with Finance before build, because bundle pricing changes how each product line reports revenue. Dependencies: K2 catalogue and order services, IDT Pay, Finance, the product teams that define the bundles."""

LONG["B8"] = """\
Enable IMTU and eSIM in every country where the BR Calling App is already available, so the full product set (Pinless, IMTU, eSIM) is on sale in each app market. As of July 2026 the app is live in more than twenty markets, Pinless in all of them, MTU in five and eSIM in one. Emilio del Rio opened a task force for this in July; in the app it is a feature flag per market, and the real work is configuration and money movement. The exact per-country status is on the App supported countries page on Confluence.

The markets fall into two groups. RoW (Rest of World) are the full non-US markets, Canada, UK, Spain, Germany and Australia, with local currency, local pricing and their own debit classes. RoRoW (Rest of Rest of World) is the long tail where the app runs in a light mode, Pinless only, billed in USD or EUR, configured through per-country debit classes (Guatemala, Mexico, Brazil, Bolivia, Ecuador, South Africa, Senegal, Finland, the Netherlands and others). The rollout follows the same split: first switch IMTU and eSIM on in the RoW markets that lack them, then roll both into RoRoW using USD or EUR pricing.

Per market this means: IMTU corridors and eSIM plans enabled in K2 for that sender country with currency, pricing, FX and taxes; local payment methods and fraud rules through IDT Pay; promo scoping in BLS; localisation, store listings and legal texts; revenue reporting by sender market. Two questions the task force raised are still open: how collections are settled (one USD account or per-market accounts) and whether to run a USD base catalogue converted daily or local-currency catalogues for the larger markets, which K2 can do either way. Dependencies: K2 catalogue team, IDT Pay, Legal and Tax per market, MARCOM, the Calling app team."""

LONG["B5"] = """\
Make the Refer-a-Friend journey fully trackable from invite to first transaction to reward payout, so every step is measurable and the programme's cost per acquired customer is known. The new RAF platform launched in FY26 with a $5 IMTU reward, and a new programme paying $24 into the wallet instead of a gift card was being localised in July 2026. Attribution is still partial: invites, installs, first purchase and payout live in different systems, and the RAF event documentation has been a recurring chore. Today the RAF bonus applies in the USA and UK only.

The initiative defines one RAF event contract (invite sent, link opened, installed, registered, first purchase, reward issued, reward redeemed) with referrer and referee ids on every event, and makes it the acceptance criteria for every surface. The backend attaches the referral to the account at registration and evaluates the reward on the first qualifying purchase across all DCS products, not only IMTU. The app shows the referrer a live status of each invite (installed, purchased, reward paid), so the feature explains itself and support contacts fall. A weekly report covers invites, conversion per step, reward cost per acquired customer, and the share of referees who transact again within 30 days.

DCS scope: the event contract and instrumentation in IMTU, eGift and eSIM, the referral attach and reward evaluation, the invite status screen, the report. Dependencies: DTC Core (RAF platform), CRM for reward messaging, the Data team for attribution reporting, the Wallet for the $24 reward payout. Request Top-Up and gifting ideas both need this loop to work."""

LONG["G7"] = """\
Let a recipient abroad ask a sender for a top-up by SMS, landing the sender in a prefilled purchase flow. The recipient sends a request from a lightweight web page or by replying to an SMS; the sender receives an SMS with a link that opens the app (or web) with the number, carrier and suggested amount already filled. Senders who are not BR customers land in onboarding with a Refer-a-Friend credit, so every request that converts also acquires a sender. The FY26 board carried it as a business spike; FY27 builds it once the RAF loop and the WhatsApp channel exist to amplify it.

The request is a deep link with a signed payload (recipient, carrier, amount, requester id) so the same link works for app, web and, later, WhatsApp. Requests are capped per recipient per week and senders can opt out, so the channel does not become spam. MARCOM owns the landing page and SMS templates, which is why the Asana card flags that dependency.

DCS scope: request creation, SMS dispatch, request status and expiry in the backend; a "request received" entry in the app that opens a prefilled checkout, and a request history for the sender. Dependencies: MARCOM, the SMS gateway, the RAF platform for the referral hook."""

LONG["G11"] = """\
Use the traveller's location and trip context to recommend, activate and top up the right eSIM plan at the right moment. The eSIM funnel converts about 2.3% end to end and loses most users at order review, partly because the customer has to know which regional plan they need; Android converts at roughly half the iOS rate. Location awareness fixes the recommendation: detect the destination from device locale, trip dates or arrival, propose the matching plan, remind the traveller to install before departure, and offer a data top-up when usage runs high in-country. It also prepares eSIM for the ROW expansion, where the customer is the traveller rather than the sender.

Location permission is requested only at the moment it helps (plan search and arrival), never at app start, and degrades to a country picker. One plan per detected destination is recommended and prefilled on the eSIM home and the order review, which is where the funnel loses most users today. "You have arrived, activate now" and "running low, add data" notifications go through the validity-reminder service shipped in FY26. A usage widget with location context on the calling app home follows once the recommendation converts.

DCS scope: destination detection, plan recommendation and prefill, the notification triggers, and the funnel instrumentation to prove the lift. Dependencies: the eSIM supplier for coverage and usage data, OS location permissions."""

LONG["B6"] = """\
Turn Engager from a campaign tool into the personalisation layer of the BR Calling App, so what each user sees for IMTU, eGift and eSIM is chosen per user by ML models rather than by one static configuration for everyone. Today Engager serves cards and dialogs from segments that marketing defines by hand. This initiative connects it to Data Science models trained on transaction history (recipients, cadence, offers taken, promo response) and gives it control of three surfaces: the order of sections on the MTU home page, the featured offer, and the single offer proposed by the IMTU modular component inside other flows. The same decisions feed Braze lifecycle campaigns, so in-app and messaging tell one story per user.

Prerequisites are the Engager cards on the MTU home page (Cross-sell 2.0) and the offer-ranking hook in the IMTU modular component. The data ships first: a clean event and feature contract exported to the model team by the end of Q3 so models train while DCS builds the placements. Every personalised decision carries a model version and a decision id in analytics so lift can be attributed and a model rolled back, each surface has a control group, and a static fallback covers latency or outages.

DCS scope: the feature contract, the three Engager-controlled placements with holdouts, decision tagging in analytics, latency guardrails. Data Science owns the models, Engager owns the decisioning service, CRM owns the Braze journeys. The first use case is next-best-offer for IMTU repeat senders, the largest and best-understood population, before widening to eGift and eSIM."""

LONG["B9"] = """\
Make promotional balances earned through Boss products spendable from the BR Wallet in both apps, across all products including Pinless. Promotions today pay out as product-specific credits: an IMTU discount, an eGift bonus, a RAF airtime reward. The Wallet integration shipped in FY26 made the stored balance (BOSS Cash) a payment method for DCS products, live for US users since April 2026, and the new RAF programme already pays $24 into the wallet. This initiative adds a promo balance type so any campaign pays a reward once and the customer spends it on any product in either app. Pinless is excluded as a source of promos but included as a place to spend them, turning scattered incentives into one loyalty currency that the gamification programme then draws on.

The balance model is agreed with the Wallet team first: promo balance as a separate bucket with expiry, spend order (promo before cash), and per-product spend rules. The backend maps BLS promo payouts to Wallet promo credits and applies them at checkout for IMTU, eGift, eSIM and Pinless; the app shows the promo balance, its expiry and what it can be spent on. The RAF reward is the pilot campaign before all campaigns are opened. Promo liability and breakage are reported to Finance from the Wallet ledger rather than from each product.

DCS scope: the promo-to-wallet mapping, checkout application across the four products, the balance display, the Finance report. Dependencies: the BR Wallet team for balance types and ledger, the BLS promo engine, the Boss Money app team, Finance."""

LONG["B3"] = """\
Move the MTU credit card purchase and self-service flows from the legacy IVR to the AI virtual agent (IVA) without losing context. The IVR still sells top-ups by phone and answers balance and order questions; the company-wide IVA programme replaces it with a conversational agent, and MTU is one of the flows to migrate. The BR Self-Serve IVA facade is already being tested with ADMI and CSA (hard-card redemption and plan assignment in August 2026), and the DTC Universal API CSA connector shipped in FY26 is the base for the MTU calls.

DCS exposes the MTU flow as a small set of stateless API calls plus a context token: recipient lookup, offer list, promo eligibility, payment with a stored card or wallet, order status, subscription cancellation. The token lets the agent resume a purchase after a hand-off to a human agent or a dropped call, so the customer is never asked for the recipient number twice. New card capture stays in the app or with a human agent, keeping PCI scope unchanged. Promo and pricing rules mirror the app exactly so a phone customer sees the same offer and price. Self-service (order status, cancel a subscription) migrates first, purchase second, so the agent handles volume before it handles money.

DCS scope: the API set and context token, the parity of promo and pricing rules, analytics on phone orders. There is no app work. Dependencies: the IVA programme team, CSA and IVR teams, the DTC Universal API."""

LONG["G8"] = """\
Run a cross-product programme of missions, streaks and surprise rewards that drives repeat purchase and product exploration across IMTU, eGift and eSIM. FY26 shipped the first mechanics as Braze in-app messages: punch cards and first-purchase promos, documented on the MTU Gamification page on Confluence. FY27 turns them into a programme: missions with visible progress, time-limited offers ("top up in the next hour for a bonus"), occasional surprise games, a monthly mission calendar and sharing of prizes, each targeted to a customer segment. Mechanics and rewards are decided per product.

The backend gets a mission engine (definition, progress tracking from order events, reward issuance) while presentation stays in Braze and the app, so marketing launches missions without releases. The FY26 punch card is the first mission type; streaks (top up three months in a row) and cross-product missions (top-up plus eGift) are the second and third. Rewards are paid as Wallet promo balance where that exists, BLS promos where it does not. Each mission runs with a holdout so incrementality is measured, and mechanics that do not lift repeat rate within two cycles are retired.

It sits late in the year deliberately so it can pay rewards into the Wallet promo balance and be targeted by Engager rather than static segments. Dependencies: the BLS promo engine, Braze, the Wallet promo balance initiative, the Loyalty team."""

LONG["G5"] = """\
Let customers pay for a top-up with cryptocurrency (for example USDT or Bitcoin) from their own wallet, while IDT is paid in US dollars and never holds or converts crypto. Triple-A acts as the payment processor: the customer picks "Pay with crypto" at checkout, is shown a hosted payment page with the amount and a wallet address or QR code, pays from their wallet, and Triple-A confirms the payment and settles the dollar amount to IDT. To the order flow it is one more payment method delivered through an IDT Pay adapter, so pricing, receipts, refunds, fraud and reporting stay as they are today. The architecture and workflows were written up in July 2026.

Scope: the IDT Pay adapter to Triple-A; the payment lifecycle in the backend (created, awaiting payment, underpaid, confirmed, expired, refunded) with a clear customer message and a Customer Service procedure for each state; a "Pay with crypto" tile and confirmation handling in the app; Amplitude events per state. Launch is IMTU only, one-time purchases only, in two corridors with crypto-native diaspora demand (proposal: Nigeria and Venezuela), behind a feature flag. eGift is excluded until fraud results are clean, since it is the higher-risk product for a payment the payer cannot reverse.

It is a Low priority business goal aimed at a specific segment, which is why it lands after the payments work with broader impact. Dependencies: the Triple-A commercial agreement and onboarding, IDT Pay, Legal and Compliance review of crypto acceptance, Finance for settlement and reconciliation. The first step is the education call with Triple-A already listed as a subtask on the Asana card."""

assert len(LONG) == 22, len(LONG)
for k, v in LONG.items():
    assert "—" not in v, k
