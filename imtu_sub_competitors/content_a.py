"""Doc content, part A: title, summary, method, market at a glance, IDT today."""
import data as D

FIG = "figures/"
SCR = "screens/"


def J(key):
    return f"[{key}](https://idtjira.atlassian.net/browse/{key})"


def L(text, url):
    return f"[{text}]({url})"


# Frequently cited sources
U = dict(
    idt_fy26="https://www.sec.gov/Archives/edgar/data/0001005731/000143774926031364/ex_950508.htm",
    journey="https://docs.google.com/document/d/13GzrL7TMQ8otuMFluVaoTghE4d90jZ9m9S4-OXlpAhQ/edit",
    toggle="https://docs.google.com/document/d/1yZD43J2sEr9RWEnE7OmrPZepLrk70TiHlz456bnakyw/edit",
    logic="https://docs.google.com/document/d/1TyKsndU--XZVdvUSNCXRsOnS6bwtBFUdOo0YcUvaRlA/edit",
    dups="https://docs.google.com/document/d/1nALdqejtdIGxyuB8xsh0emvMr4NbO_WMkfX0x5yXMSU/edit",
    applepay="https://docs.google.com/document/d/1Mmc-eDPteg4xVTYv6vm6cAf59viWlOSliBlL_lNebsU/edit",
    fy27sugg="https://docs.google.com/document/d/1D1LV0BN_L0X4aAIqVFOW-kaV1hRJX98OlJGkk75M-j4/edit",
    monthly="https://docs.google.com/document/d/1Yj-0_1xfJB8Yf-EvA_dGNJsRj_suvphswS1QBfngWtk/edit",
    bespike="https://docs.google.com/document/d/1757DxnqbEzERY9jncPQTydaINlunJ0NjHHDZ_MYyNzE/edit",
    amp_journey="https://app.amplitude.com/analytics/BOSS/dashboard/o1jhxth9",
    amp_toggle="https://app.amplitude.com/analytics/BOSS/dashboard/1c3815cw",
    amp_home="https://app.amplitude.com/analytics/BOSS/dashboard/bwtn629z",
    figma_bar="https://www.figma.com/design/7HfHbf5Q4t7eXhDzPtfTX1/BR-IMTU---HANDOFF-2027?node-id=976-17639",
    figma_cancel="https://www.figma.com/design/7HfHbf5Q4t7eXhDzPtfTX1/BR-IMTU---HANDOFF-2027?node-id=169-13081",
    figma_edit="https://www.figma.com/design/7HfHbf5Q4t7eXhDzPtfTX1/BR-IMTU---HANDOFF-2027?node-id=58-14706",
    figma_date="https://www.figma.com/design/7HfHbf5Q4t7eXhDzPtfTX1/BR-IMTU---HANDOFF-2027?node-id=1123-23943",
    br_web="https://www.bossrevolution.com/en-us/services/international-mobile-topup",
    br_as="https://apps.apple.com/us/app/id586745548",
    bm_as="https://apps.apple.com/us/app/id1169518032",
    bm_faq="https://www.bossrevolution.com/en-us/boss-money-app-faq",
    ding_as="https://apps.apple.com/us/app/ding-top-up-mobile-recharge/id425228767",
    ding_play="https://play.google.com/store/apps/details?id=com.ezetop.world",
    ding_terms="https://web.archive.org/web/20260519194044/https://www.ding.com/terms-conditions",
    ding_activate="https://support.ding.com/hc/en-us/articles/360004427557-How-do-I-activate-an-auto-top-up",
    ding_cancel="https://support.ding.com/hc/en-us/articles/360004422418-How-do-I-cancel-an-auto-top-up",
    ding_nothanks="https://support.ding.com/hc/en-us/articles/4403191385233-I-don-t-want-to-set-up-an-auto-top-up",
    ding_app_activate="https://appsupport.ding.com/hc/en-us/articles/360014365898-How-to-activate-an-auto-top-up",
    ding_app_cancel="https://appsupport.ding.com/hc/en-us/articles/360014384358-How-do-I-cancel-an-auto-top-up",
    ding_vip="https://support.ding.com/hc/en-us/articles/50704507699601-What-is-dingVIP",
    ding_vip_sub="https://support.ding.com/hc/en-us/articles/50879419929873-How-to-subscribe-to-dingVIP",
    ding_vip_credits="https://support.ding.com/hc/en-us/articles/50879728399889-How-to-use-your-dingVIP-credits",
    ding_vip_manage="https://support.ding.com/hc/en-us/articles/50879964648977-Manage-your-dingVIP-subscription",
    ding_rewards="https://support.ding.com/hc/en-us/articles/29797644551569-Ding-Rewards-Club",
    ding_money="https://support.ding.com/hc/en-us/articles/39129629327377-What-is-DingMoney",
    ding_fees="https://support.ding.com/hc/en-us/articles/203036322-Processing-fees",
    ding_request="https://support.ding.com/hc/en-us/articles/4411762291217-How-to-request-a-top-up",
    ding_hub="https://support.ding.com/hc/en-us/articles/33876544673169-Ding-Hub-Using-Ding-as-a-receiver",
    ding_presale="https://support.ding.com/hc/en-us/articles/360013644358-Cubacel-Why-is-my-transaction-status-Reserved",
    ding_2020="https://web.archive.org/web/20250120190704/https://www.ding.com/community/introducing-auto-top-up-worldwide",
    ding_pollen="https://www.pollenstreetgroup.com/pollen-street-capital-acquires-majority-stake-in-worlds-largest-mobile-top-up-service-ding/",
    reb_tos="https://www.rebtel.com/en/legal-information/terms-of-service/",
    reb_generic="https://www.rebtel.com/en/campaign/cms/mtu-generic/",
    reb_mx="https://www.rebtel.com/en/campaign/cms/mexico-recharge/",
    reb_buy="https://www.rebtel.com/en/help/article/15948694220946-how-do-i-buy-mobile-top-up-subscription/",
    reb_diff="https://www.rebtel.com/en/help/article/15955182817682-what-are-the-differences-between-mobile-top-up-bundles-and-plans/",
    reb_deact="https://www.rebtel.com/en/help/article/22035601041682-how-do-i-deactivate-and-reactivate-my-subscriptions/",
    reb_qa="https://www.rebtel.com/en/help/article/28331366817682-mtu-related-questions-and-answers/",
    reb_fail="https://www.rebtel.com/en/help/article/38142300593554-why-did-my-rebtel-payment-fail/",
    reb_cuba="https://www.rebtel.com/en/cuba/recharge/",
    reb_wallet="https://www.rebtel.com/en/help/article/38750887866770-how-do-i-check-my-balance-in-the-rebtel-app/",
    reb_as="https://apps.apple.com/us/app/rebtel-top-ups-and-calls/id310755560",
    reb_play="https://play.google.com/store/apps/details?id=com.rebtel.android",
    reb_wiki="https://en.wikipedia.org/wiki/Rebtel",
    reb_trust="https://www.trustpilot.com/review/www.rebtel.com",
    rc_telcel="https://www.recharge.com/en/mx/telcel",
    rc_as="https://apps.apple.com/us/app/id1547603137",
    rc_coda="https://www.coda.co/press/coda-completes-recharge-acquisition-expanding-global-reach/",
    mr_web="https://mobilerecharge.com/",
    mr_as="https://apps.apple.com/us/app/id946046304",
    topup_as="https://apps.apple.com/us/app/id1367920546",
    kc_as="https://apps.apple.com/us/app/id518708790",
    digicel_as="https://apps.apple.com/us/app/id930383772",
    digicel_faq="https://topup.digicelgroup.com/en/faq/",
    telcel_portal="https://mitelcel1.recarga.telcel.com/NewTelcelMXExternalWebMiTelcel/enter.do",
    etopup_blog="https://www.etopuponline.com/blog/how-to-auto-top-up-set-up-automatic-mobile-recharges",
    natcom_play="https://play.google.com/store/apps/details?id=com.etopuponline.natcom",
    natcom_blog="https://natcomtopup.com/blog/keep-your-mobile-phone-working-abroad-with-natcom-auto-top-up",
    elemt="https://www.elemt.com/",
    claro_rd="https://www.claro.com.do/personas/servicios/servicios-moviles/prepago/recargas/recarga-desde-el-exterior/",
    claro_gt="https://www.claro.com.gt/personas/servicios/servicios-moviles/prepago/superpacks-usa/",
    tigo_int="https://internacional.tigo.com/",
    cuballama="https://www.cuballama.com/recargas-a-cuba",
    fonoma="https://www.fonoma.com/cms/en/landing/recarga-cubacel",
    acuba="https://apps.apple.com/us/app/id1532066975",
    cubatel_as="https://apps.apple.com/us/app/id1300396049",
    ensip="https://ensip.com/experiencia-ensip-cuba",
    felix="https://www.felixpago.com/recargas-internacionales",
    felix_guide="https://www.felixpago.com/guias/recargas-internacionales",
    felix_raise="https://refreshmiami.com/news/felix-raises-200-million-to-bring-loans-and-savings-to-whatsapp/",
    felix_growth="https://www.elespanol.com/invertia/disruptores-americas/20260924/felix-pago-consigue-millones-dolares-ir-alla-remesas-eeuu-america-latina/1003744390623_0.amp.html",
    remitly_one="https://www.remitly.com/blog/money-transfer/what-is-remitly-one/",
    remitly_wa="https://www.globenewswire.com/news-release/2026/04/23/3279982/0/en/Remitly-Expands-WhatsApp-Send-to-New-Markets-Launches-Request-Money-to-Capture-Growing-Customer-Demand.html",
    wu_reload="https://www.westernunion.com/us/en/international-mobile-reload.html",
    mg_topup="https://www.moneygram.com/us/en/services/mobile-top-ups",
    mg_recurring="https://www.moneygram.com/us/en/help-center/faq/send-receive/general-questions/can-i-schedule-a-recurring-send-to-send-money-transfers-on-a-weekly-or",
    xoom="https://www.xoom.com/mobile-reloads",
    wr="https://www.worldremit.com/en-us/send-airtime",
    taptap="https://help.taptapsend.com/en/sending-money/how-does-pay-bills-work",
    taptap_wa="https://help.taptapsend.com/en/getting-started/what-does-taptap-send-do",
    banxico="https://www.banxico.org.mx/publicaciones-y-prensa/remesas/%7B626A49AF-D316-BBF0-D62D-8A7783EDA277%7D.pdf",
    dialogue="https://thedialogue.org/blogs/2026/09/a-mixed-bag-in-mexican-remittance-growth",
    amx="https://s22.q4cdn.com/604986553/files/doc_financials/2026/q2/2Q26.pdf",
    millicom="https://ml-eu.globenewswire.com/Resource/Download/601d4371-7795-45fa-8810-20d5fe4f47cd",
    curp="https://www.infobae.com/mexico/2026/09/05/el-registro-obligatorio-de-celular-con-curp-entra-en-su-segunda-ronda-quienes-perderan-su-linea-este-mes-si-no-lo-realizan/",
    curp_susp="https://www.xataka.com.mx/telecomunicaciones/te-suspendieron-tu-linea-te-quedaste-saldo-esto-debes-hacer-para-recuperar-tu-servicio",
    cubacel_x6="https://www.periodicocubano.com/etecsa-promociona-recarga-internacional-que-multiplica-x6-el-saldo-principal/",
    recurly="https://recurly.com/research/churn-rate-benchmarks/",
    recurly26="https://recurly.com/resources/report/2026-state-of-subscriptions/",
    stripe="https://stripe.com/billing",
    chargebee="https://www.chargebee.com/blog/navigating-retention-chargebee-subscription-insights-2024/",
    visa_tokens="https://corporate.visa.com/en/solutions/tokenization.html",
    visa_rules="https://usa.visa.com/content/dam/VCOM/global/support-legal/documents/visa-new-subscription-rules-flier.pdf",
    rosca="https://www.law.cornell.edu/uscode/text/15/8403",
    ca_arl="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=BPC&sectionNum=17602",
    mn_arl="https://www.revisor.mn.gov/statutes/cite/325G.57",
    ma_arl="https://www.law.cornell.edu/regulations/massachusetts/940-CMR-38-05",
    ftc_anprm="https://www.ftc.gov/news-events/news/press-releases/2026/03/ftc-seeks-public-comment-response-advance-notice-proposed-rulemaking-regarding-negative-option",
    ftc_amazon="https://www.ftc.gov/news-events/news/press-releases/2026/09/ftc-announces-additional-payments-consumers-stemming-ftcs-amazon-prime-settlement",
    vacatur="https://www.lw.com/en/insights/eighth-circuit-vacates-ftc-click-to-cancel-rule-days-before-compliance-deadline",
    nyc_la="https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/summer-2026-autorenewal-roundup-nyc-and-louisiana-enact-new-regulatory-requirements",
    zwillgen="https://www.zwillgen.com/auto-renewal/auto-renewal-update-legal-landscape-imposes-complex-obligations-subscription-businesses/",
    rege="https://www.ecfr.gov/current/title-12/chapter-X/part-1005/subpart-A/section-1005.10",
    tax4475="https://www.federalregister.gov/documents/2026/04/13/2026-07085/excise-tax-on-remittance-transfers",
    ofac="https://www.ecfr.gov/current/title-31/subtitle-B/chapter-V/part-515/section-515.542",
    coda="https://www.coda.co/press/coda-acquires-recharge-global-expansion/",
    wu_q2="https://www.sec.gov/Archives/edgar/data/0001365135/000119312526326110/wu-ex99_1.htm",
    wu_intermex="https://www.sec.gov/Archives/edgar/data/0001365135/000119312526350419/d126356dex991.htm",
    wa_india="https://techcrunch.com/2026/04/23/whatsapp-adds-prepaid-phone-recharges-in-india-as-its-payments-usage-still-lags/",
    visa_agent="https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21961.html",
    ap2="https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol",
    esim="https://www.gsmaintelligence.com/research/consumer-esim-device-and-mno-service-trackers-and-2030-adoption-forecast-q1-2026",
    dtone="https://www.dtone.com/company/news-events",
)


def src(*keys_or_pairs):
    """Render a 'Sources:' small line from U keys or (label, url) pairs."""
    parts = []
    for k in keys_or_pairs:
        if isinstance(k, tuple):
            parts.append(L(k[0], k[1]))
        else:
            parts.append(L(k.replace("_", " "), U[k]))
    return ("small", "Sources: " + ", ".join(parts) + ".")


BLOCKS_A = [
    ("title", "IMTU Subscriptions: Competitor Investigation and 12-Month Plan"),
    ("meta", "DCS / IMTU product. 29 September 2026. Recurring international mobile top-up (IMTU) products sold to "
             "US senders, compared with IDT's Boss Revolution (BR) and BOSS Money apps. Method in section 1, sources in "
             "the appendix. Evidence tags: Verified (official page or filing read), Reported (third party), Inferred (our reading)."),

    ("h1", "Summary"),
    ("callout", "idt",
     "**The short version.** IDT already runs the largest IMTU subscription business in the market: about 45,000 new "
     "subscriptions a week across BR and BOSS Money, 1.35 million since March 2026. But that base is built on a "
     "pre-ticked default and has no payment-recovery layer. Competitors are much smaller, but they are ahead on "
     "consent, control and value. Ding asks explicitly and now sells a paid membership. Rebtel prices subscribing "
     "below one-time. Carriers such as Digicel run free auto top-up with renewal nudges. No one has solved failed "
     "payments, pause and skip, or promo-aware scheduling. That is where IDT can lead over the next 12 months."),
    ("h3", "Six findings"),
    ("numbered", [
        "**Recurring top-up is now table stakes, not a differentiator.** Ding (since 2019, relaunched in 2025), "
        "MobileRecharge and TopUp.com, Rebtel, Digicel, Natcom's official app and even Telcel's own portal all sell "
        "it, mostly on 7, 14, 28 or 30-day cadences. The remittance apps (Remitly, Western Union, MoneyGram, Xoom, "
        "WorldRemit, Taptap Send, Félix Pago) do not.",
        "**IDT wins on scale, not on consent.** Attach is 62.9% when the toggle defaults ON and 5.5% when it defaults "
        "OFF. 46.6% of users shown ON switch it off, in a median of 7 seconds. 30.6% of new subscriptions are "
        "cancelled within 30 days (49.4% on weekly cadences). BR's App Store reviews about subscriptions and "
        "auto-charges rose from 0.4% of reviews (Apr to Jun) to 5.0% (Jul to Sep 2026).",
        "**Value is the new battleground.** Rebtel Plans are 3 to 17% cheaper than one-time (up to 47% in Nigeria), "
        "with $3.99 first-month teasers. Ding launched dingVIP in September 2026: a paid membership with a 7-day "
        "trial, a PLUS tier at $5 a month, monthly credits and extra points. IDT's subscription promo is built but "
        "not launched.",
        "**Failed payments are everyone's weak spot.** Ding cancels the auto top-up on the first decline, Rebtel "
        "deactivates it, MobileRecharge retries for 12 hours and then switches off, and IDT stays silent and tries "
        "again next cycle. About a third of consumer subscription churn is failed payments; nobody runs a real "
        "recovery ladder.",
        "**Corridors are rewriting the rules.** Mexico's mandatory CURP registration suspends unregistered prepaid "
        "lines through 31 Dec 2026, and about 42% of lines were unregistered in mid-September. In Cuba the value sits "
        "in short Cubacel promo windows, so specialists sell 'reserve now, deliver on promo', and Rebtel excludes "
        "Cuba from subscriptions entirely.",
        "**Regulation tightens state by state.** California, Minnesota, Massachusetts, New York, Virginia, "
        "Connecticut and Maryland rules are in force, NYC's starts on 1 Oct 2026 and Louisiana's on 1 Jan 2027, and "
        "the FTC keeps enforcing ROSCA ($2.5B Amazon Prime settlement). A pre-ticked default and missing per-charge "
        "receipts are IDT's main exposure.",
    ]),
    ("h3", "Where IDT is strong, where competitors are strong"),
    ("table", [
        ["IDT is strong at", "Competitors are strong at"],
        ["**Scale and distribution.** Largest rating base of any top-up app (BR 277,506 US ratings), two apps, "
         "6M+ customers, retail network, five sender markets.",
         "**Consent that holds up.** Ding's opt-in modal with 'No thanks' and an editable order-summary row; "
         "Rebtel's cadence pick before payment. Ding draws almost no subscription complaints (4 in 696 reviews)."],
        ["**Attach at checkout.** The subscription is the top-up being bought, with zero extra steps; subscription "
         "checkout converts within 1 point of one-time (93.3% vs 94.2%).",
         "**A reason to subscribe.** Rebtel Plans priced below one-time, teaser first months; dingVIP credits and "
         "points; Digicel's free auto top-up with 'Renew before it's too late' nudges."],
        ["**Carrier-change resilience.** Retired offers are swapped automatically to a replacement product; "
         "cadence defaults to offer validity.",
         "**Scheduling flexibility.** Ding lets senders pick a start date with no payment upfront; 28-day "
         "option that matches carrier plan cycles."],
        ["**Payment fallbacks.** Charges a second card in flight, blocks deleting the last card (missing-card "
         "errors down 62% in the A/B), push reminder 2 days before every charge.",
         "**Wallet breadth on renewals.** Apple Pay, Google Pay and PayPal on recurring (Ding, Rebtel); "
         "Rebtel Credits pay the first month."],
        ["**Own engine and promo system.** Subly and IDT Pay avoid about 1% billing fees; a subscription-specific "
         "loyalty promo group is built.",
         "**Ecosystem loops.** Ding Rewards Club, Request top-up links, Ding Hub for receivers, dingMoney wallet; "
         "Félix inside WhatsApp."],
    ], {"widths": [50, 50], "font_pt": 8.5}),
    ("callout", "good",
     "**The plan in one line.** First fix trust and payment health (Oct 2026 to Jan 2027), then give senders "
     "control (Nov to Mar), then add value and corridor fit (Jan to Sep 2027), with three decision gates. "
     "Section 11 has the detail, KPIs and dependencies."),

    ("pagebreak",),
    ("h1", "1. Scope, method and evidence"),
    ("p", "**What counts as a subscription here.** Any product that charges a sender again without a new purchase "
          "decision to send airtime, data or a bundle to someone else's prepaid phone abroad: calendar auto top-ups, "
          "subscription-only plans, promo-triggered presales and paid memberships attached to top-up. "
          "Recurring money transfers and calling-balance auto-recharge are covered only as analogs."),
    ("p", "**Players.** Ding; Rebtel; Recharge.com (Coda); MobileRecharge, TopUp.com and KeepCalling (Miron "
          "Enterprises); carriers selling direct (Digicel, Telcel, Natcom and Viva through Elemt / Prepay Nation, "
          "Claro, Tigo); Cuba specialists (Cuballama, Fonoma, aCuba, Cubatel, DimeCuba, Ensip); remittance and chat "
          "apps (Remitly, Western Union, MoneyGram, Xoom, WorldRemit, Sendwave, Taptap Send, Félix Pago, Intermex, "
          "Ria, Viamericas). IDT's own BR and BOSS Money apps are the baseline."),
    ("p", "**How the evidence was gathered (29 Sep 2026).**"),
    ("bullets", [
        "**Public web flows**, captured in headless Chrome at iPhone size, with non-essential cookies rejected or "
        "the banner hidden without consent. No account was created, no sign-in was used and nothing was bought.",
        "**Competitors' own help centres, terms and store listings.** Ding's and Rebtel's help articles include "
        "their own screenshots of the logged-in flows, which is how this doc shows screens behind a login. "
        "Rebtel's public product catalog and web-app code were read for prices, cadences and checkout logic.",
        "**App Store reviews.** 7,367 US written reviews across 10 apps, pulled from the public RSS feed and "
        "hand-coded (894 keyword candidates read in full).",
        "**Filings, regulators and trade press** for market size, remittances, carriers and rules.",
        "**IDT internal data.** Amplitude (BR app 650506, BOSS Money 420385), live Jira statuses, the Figma "
        "handoff file, and the internal subscription analyses listed in the appendix.",
    ]),
    ("p", "**Limits.**"),
    ("bullets", [
        "Account creation and sign-in on competitor apps were out of scope by policy, and public screens only was "
        "the chosen approach. Logged-in and in-app steps are therefore shown from each company's own published "
        "screenshots, not from a live session. Checkout steps that need a recipient phone number were not captured.",
        "Captures ran from a Brazilian IP, with US sender paths forced by URL where possible. Prices shown in "
        "screenshots can differ by sender country.",
        "Competitor figures (users, operators, ratings) are as published. Adoption and churn of competitor "
        "subscriptions are not public anywhere.",
        "Written App Store reviews skew negative and cover the US store only; counts are lower bounds.",
    ]),

    ("pagebreak",),
    ("h1", "2. The market at a glance"),
    ("h2", "2.1 Five ways the market sells recurring top-ups"),
    ("figure", FIG + "fig_models.png", 624, ""),
    ("p", "Most of the market has converged on the **calendar auto top-up**: the same product at the same price, "
          "sent again every 7, 14, 28 or 30 days. The differences are in the edges. Rebtel adds **subscription-only "
          "Plans** that are cheaper than one-time. Ding and Remitly sell a **paid membership** on top. Cuba specialists "
          "sell **promo-triggered presales** instead of calendars. Recharge.com offers only a **reminder**."),
    ("h2", "2.2 Capabilities side by side"),
    ("figure", FIG + "fig_capabilities.png", 624, ""),
    ("p", "Three patterns stand out. First, no one runs a real recovery ladder on failed renewals (MobileRecharge "
          "retries for 12 hours at most), and no one lets the sender skip or pause a cycle. Second, IDT is the only large player whose subscription is pre-ticked. Third, IDT is ahead on "
          "reminders (a push before every charge) and is one of the few that lets senders edit after activation. The full comparison of the main "
          "products is below; the same matrix as a table is in appendix B."),
    ("table", [
        ["Product", "Model", "Cadence", "Default", "Price for subscribing", "Before each charge", "Failed payment",
         "Manage and cancel"],
        ["**IDT BR / BOSS Money**", "Calendar, created inside a normal top-up", "7, 14, 30, 90 days; default from offer validity",
         "**ON** for most users since 20 Jun 2026", "Same price; subscription promo built, not launched", "Push 2 days before",
         "Stays active, silent, retried next cycle", "Edit offer, cadence, card; cancel in app (yes/no)"],
        ["**Ding**", "Calendar auto top-up; dingVIP membership on top", "7, 14, 28, 30 days; pick a start date",
         "Opt-in modal, 30 days pre-highlighted", "Same price; promos pass through; dingVIP credits", "Not in terms; a review mentions a text",
         "Auto top-up cancelled", "Cancel only (no edit, skip, pause)"],
        ["**Rebtel Auto Top-Up**", "Calendar on credits and bundles", "Credits 7, 14, 28, 30 (30 preselected); bundles at validity",
         "Opt-in (legacy modal); new checkout default not visible", "Same price; $0.99 one-time fee waived on 3 operators",
         "None found", "Deactivated", "Deactivate, reactivate, change card"],
        ["**Rebtel Plans**", "Subscription-only SKUs, 36 in 6 countries", "Validity: 7 to 84 days",
         "Recurring by definition", "3 to 17% cheaper; teasers from $3.99", "None found", "Deactivated", "As above"],
        ["**MobileRecharge / TopUp.com**", "Calendar, 'Activate Auto Top-up at checkout' (since 2022)", "7, 14, 28, 30 days",
         "Opt-in toggle at checkout", "Same as one-time (fee from $1)", "Optional notice 48 hours before",
         "Retries for 12 hours, then off", "Cancel from dashboard, immediate; edit only inside a new order"],
        ["**Digicel**", "Carrier-run calendar plus auto-pay plans", "7, 14, 28, 30 days", "Auto-pay checkbox shown ticked in store screenshot",
         "Free service", "'Renew before it's too late' home card", "Not public", "Delete link in account"],
        ["**eTopUpOnline / Natcom (Elemt)**", "Calendar", "Weekly, half-monthly, monthly; start date and day",
         "Not public", "Loyalty points instead", "Not public", "Not public", "Natcom: edit or cancel any time"],
        ["**Recharge.com**", "Reminder only; no recurring payments", "Chosen date and time", "n/a", "10% off first app order (max 5 EUR)", "It is the reminder", "n/a", "n/a"],
        ["**Cuba specialists**", "Presale: reserve, delivered when the promo starts", "Event-based", "Explicit reservation",
         "Cashback and credit (Fonoma 3%)", "Promo alerts", "n/a", "n/a"],
    ], {"widths": [12, 14, 14, 12, 14, 11, 11, 12], "font_pt": 7.4}),
    src(("Ding terms section 8", U["ding_terms"]), ("Ding help", U["ding_activate"]), ("Rebtel terms 2.16", U["reb_tos"]),
        ("Rebtel help", U["reb_diff"]), ("MobileRecharge", U["mr_web"]), ("Digicel app", U["digicel_as"]),
        ("eTopUpOnline", U["etopup_blog"]), ("Recharge.com app", U["rc_as"]), ("Cuballama", U["cuballama"]),
        ("IDT logic reference", U["logic"])),

    ("h2", "2.3 Scale"),
    ("figure", FIG + "fig_scale.png", 600, ""),
    ("p", "BR has the largest rating base of any top-up app in the US store, more than twice Rebtel's and more than "
          "three times Ding's. Cuballama is second, but it is a Cuba super-app (recharges, shipping, travel). "
          "Ratings are all between 4.6 and 4.9, so they do not separate the players; review volume and complaint "
          "mix do (section 6)."),
    ("h2", "2.4 Demand behind the market"),
    ("bullets", [
        "**No credible public size exists for international top-up**, and nobody sizes the US-outbound segment; "
        "vendor estimates span $5B to $600B depending on definition. The best public anchor is IDT Digital "
        "Payments: $429.2M revenue in FY26, +3% (" + L("IDT FY26 results, 28 Sep 2026", U["idt_fy26"]) + "). "
        "A mature, low-growth category.",
        "**Fewer senders sending more.** Remittances to Mexico fell 3.9% in 2025 and are up 3.1% in Jan to Jul "
        "2026, but transaction counts are still down 1.6% (" + L("Banxico", U["banxico"]) + "). Top-ups follow "
        "sender and recipient counts, not ticket size, so unit volume into Mexico is flat to slightly down.",
        "**Airtime is giving way to data.** BR international calling revenue fell 20% in FY25 and 15% in FY26 "
        "(" + L("IDT FY26", U["idt_fy26"]) + "); carriers sell data bundles with 7 and 30-day validity, and "
        "operators are converting their best prepaid users to postpaid (Millicom Guatemala postpaid +19%, "
        + L("Millicom Q2 2026", U["millicom"]) + ").",
        "**Cash to digital.** The 1% US remittance tax (from 1 Jan 2026) hits cash-funded transfers only; BOSS "
        "Money is 88% digital and Western Union 43% (" + L("WU Q2 2026", U["wu_q2"]) + "). Card-funded top-up "
        "subscriptions are most likely outside the tax (counsel to confirm, " + L("proposed rules", U["tax4475"]) + ").",
    ]),

    ("pagebreak",),
    ("h1", "3. IDT today"),
    ("h2", "3.1 How the IDT subscription works"),
    ("p", "An IMTU subscription is a recurring top-up to one recipient number, for one offer, at a fixed cadence. "
          "It is created inside a normal top-up when the subscription toggle is on: that purchase is the first "
          "charge, and the next falls one cycle later. There is no trial, grace or pause state; a subscription is "
          "active or cancelled, and one that cannot be charged stays active (" + L("Logic Reference", U["logic"]) + ")."),
    ("bullets", [
        "**Where it is offered.** On the order screen; from 26.9.3 in the payment bar with a bottom sheet "
        "(" + J("DCS-5299") + ", release candidate, not in 26.9.1). Also from the BR7 home Subscriptions widget.",
        "**Default.** ON for most users since 20 Jun 2026. The toggle hides after 3 off-toggles (" + J("DCS-4854") + "). "
        "The recipient-based default-off rules (" + J("DCS-5374") + ", " + J("DCS-5361") + ", " + J("DCS-5373") +
        ") were closed as Won't fix on 25 Sep 2026 while the rules move to the backend (spike " + J("DCS-5424") +
        " done; cleanup " + J("DCS-5546") + " to do).",
        "**Cadence.** 7, 14, 30 or 90 days, defaulted from the offer's validity and editable in the dropdown.",
        "**Renewals.** Push 2 days before every charge (" + J("DCS-4983") + "). The card on file is charged (wallet-first "
        "logic exists, but the wallet is disabled for compliance); a second card on file is charged in flight if the first fails. If all fail, nothing is sent to the customer "
        "(CRMC-3299 in backlog since 2024) and the next attempt is the next cycle.",
        "**Manage and cancel.** Edit offer, frequency and payment method (payment change partly built). Cancel is "
        "Edit, Cancel, a yes/no dialog, then success; no reason is captured today. An enhanced flow with an exit "
        "survey and save screens is in QA (" + J("DCS-4708") + ", " + J("DCS-5257") + ", " + J("DCS-5418") + ").",
    ]),
    ("row", [(SCR + "idt_order_payment_bar_off.png", 180, "Payment bar, toggle off: 'Pay $30.00'"),
             (SCR + "idt_order_payment_bar_sub.png", 180, "Payment bar, subscription on: 'Subscribe & Pay $27.50' with savings copy")]),
    ("small", "IDT screens are from the " + L("BR IMTU handoff file in Figma", U["figma_bar"]) + " (payment bar, "
              + J("DCS-5299") + " and " + J("DCS-5486") + "). Recipient details blurred. The savings line depends on the "
              "subscription promo, which is built but not launched."),

    ("h2", "3.2 Scale and attach"),
    ("figure", FIG + "idt_weekly_subs.png", 600, ""),
    ("table", [
        ["Metric", "Value", "Definition and window"],
        ["New subscriptions per week", "~44,800 (BR 37,584; BOSS Money 7,172)", "Week of 21 Sep 2026; Amplitude, subscription created at purchase"],
        ["New subscriptions since March", "1.35M (BR 1.03M, BOSS Money 0.33M)", "2 Mar to 27 Sep 2026"],
        ["Share of in-app purchases that subscribe", "BR 23.5%, BOSS Money 15.3%", "Week of 21 Sep 2026 (peak 45%, week of 22 Jun)"],
        ["Distinct subscription purchasers", "272,026", "BR app, 1 Mar to 1 Aug 2026"],
        ["Attach when the toggle defaults ON / OFF", "62.9% / 5.5%", "Order-screen users, 1 to 29 Aug 2026 (observational)"],
        ["Shown ON, switched it OFF", "46.6% (median 7 seconds)", "Users, 20 Jun to 31 Aug 2026"],
        ["Shown OFF, switched it ON", "18.5% (14.0% in August)", "Users, 20 Jun to 31 Aug 2026"],
        ["Payment-step conversion, subscription vs one-time", "93.3% vs 94.2%", "1 to 29 Aug 2026"],
    ], {"widths": [34, 26, 40], "font_pt": 8.2}),
    src(("Amplitude query, 29 Sep 2026", U["amp_journey"]), ("Subscription Journey v2", U["journey"]),
        ("Toggle analysis, 3 Sep 2026", U["toggle"])),

    ("h2", "3.3 Where the base leaks"),
    ("figure", FIG + "fig_idt_cancel.png", 600, ""),
    ("bullets", [
        "**The base is built by the default more than by demand.** 51.3% of default-ON users never touch the toggle, "
        "and weekly attach fell 11 weeks in a row after the rollout (45.5% to 26.0%).",
        "**Early cancellation.** 30.6% cancel within 30 days; 44.8% of the default-ON cohort within 60 days, with a "
        "jump at the first monthly charge (21.3% of 60-day cancellers act on days 29 to 32).",
        "**Cancelling is not leaving.** 65.4% of cancellers buy a one-time top-up within 60 days, and 80.7% come back "
        "in some form. The demand is there; the mechanic was rejected.",
        "**Failures are invisible.** No renewal event exists, 100% of payment-failure events lack a subscription "
        "flag, and 28.4% of subscriptions were failing in an April database check. Each failed attempt costs "
        "about 7 cents.",
        "**Duplicates.** 1,094 customers are paying for 3,469 surplus subscriptions (at least $150k a year), and "
        "995 customers removed their only card to stop charges (" + L("duplicates analysis", U["dups"]) + ").",
    ]),
    ("h2", "3.4 What is in flight (live Jira, 29 Sep 2026)"),
    ("table", [
        ["Item", "Ticket", "Status"],
        ["Subscription section in the payment bar", J("DCS-5299"), "Done; in the 26.9.3 release candidate"],
        ["Savings subtext and subscription promotion label", J("DCS-5429"), "Ready in feature branch"],
        ["Enhanced cancellation flow: survey and save screens", J("DCS-5257") + ", " + J("DCS-5418") + ", QA " + J("DCS-5436"), "Ready in feature; QA blocked"],
        ["Retention offer in the cancellation flow", J("DCS-5375") + ", BE spike " + J("DCS-5538"), "Spec in progress; spike to do"],
        ["Auto-cancel after N consecutive failed charges", J("DCS-5420"), "To do"],
        ["Cancel the remaining K2 duplicate", J("DCS-5580"), "To do"],
        ["Edit the next charge date without changing cadence", J("DCS-5501"), "In progress"],
        ["My Subscriptions: past and scheduled transactions", J("DCS-5505"), "Design in progress"],
        ["Total subscription savings flag", J("DCS-5597"), "In progress"],
        ["Subscription SMS moved to the Notification Service", J("DCS-5575"), "To do"],
        ["Separate subscription availability from card rules", J("DCS-5509"), "To do"],
        ["Informational toast after three toggle-offs", J("DCS-5487"), "To do"],
        ["Subscriptions V2 A/B test in production", J("DCS-5345") + ", " + J("DCS-5590"), "In progress / to do"],
        ["Apple Pay and Google Pay (FY27 B4)", L("design doc", U["applepay"]), "Backend supports; phase 1 for users 90+ days on file"],
    ], {"widths": [52, 28, 20], "font_pt": 8.2}),
    ("row", [(SCR + "idt_cancel_survey.png", 118, "Exit survey"),
             (SCR + "idt_cancel_save_emotional.png", 118, "Save: emotional"),
             (SCR + "idt_cancel_save_benefit.png", 118, "Save: benefit"),
             (SCR + "idt_cancel_save_incentive.png", 118, "Save: incentive"),
             (SCR + "idt_cancel_done.png", 118, "Cancelled, 'restart anytime'")]),
    ("small", "Enhanced cancellation flow, four save variants for A/B (" + L("Figma", U["figma_cancel"]) + ", "
              + J("DCS-4708") + "). Designed and built; not yet live."),
    ("h2", "3.5 How IDT presents it publicly"),
    ("row", [(SCR + "br_web_imtu.png", 150, "bossrevolution.com: 'Automate Top-Ups'"),
             (SCR + "br_as_topup.png", 130, "BR App Store: top-up screen"),
             (SCR + "br_as_promos.png", 130, "BR App Store: carrier promos")]),
    ("bullets", [
        "The BR website sells scheduling ('Schedule your Top-Ups', weekly, monthly or quarterly), but none of the "
        "646 pages in its sitemap explains how to view, pause or cancel a scheduled top-up, and no subscriber "
        "benefit is stated (" + L("BR IMTU page", U["br_web"]) + ").",
        "The BR App Store listing never shows the subscription; it leads with calls, top-up discounts and carrier "
        "promos (" + L("App Store", U["br_as"]) + "). Ding's listing shows an 'Every 30 days' top-up with 'Manage' "
        "in History.",
        "The BOSS Money FAQ documents recurring transfers in full (setup, notice the day before, cancel by swipe), "
        "the best public recurring-payment help page among the remittance apps (" + L("BOSS Money FAQ", U["bm_faq"]) +
        "). It is a ready template for an IMTU subscription help page.",
        "Small fixes: carrier counts differ across pages (280+ / 270+ / 300+), referral values differ ($5, $10, "
        "$30), and the English scheduling tagline contains a Cyrillic letter in 'peace'.",
    ]),
]
