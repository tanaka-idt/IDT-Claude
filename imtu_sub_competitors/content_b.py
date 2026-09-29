"""Doc content, part B: competitor deep dives."""
from content_a import FIG, SCR, J, L, U, src

BLOCKS_B = [
    ("pagebreak",),
    ("h1", "4. Competitor deep dives"),

    # ------------------------------------------------------------------ Ding
    ("h2", "4.1 Ding: the mature benchmark, now adding a paid membership"),
    ("table", [
        ["Company", "Ezetop Unlimited Company t/a Ding, Dublin; Pollen Street Capital majority since Sep 2021 (no PayU link found). Powers the top-up checkouts of Western Union and MoneyGram."],
        ["Scale", "500M+ top-ups to date, 150+ countries, 700+ operators (600 to 850 depending on the page). iOS 4.82 from 83,831 US ratings; Google Play 4.7, 63.5K reviews, 5M+ installs."],
        ["Recurring product", "'Auto top-up' since Dec 2019 (web only at first). Relaunched mid-2025 as 'Recurring Top-ups 2.0' (Android) and 'Smarter Recurring Top-Ups' (iOS 5.26, 23 Jul 2025): pick a start date, no payment upfront, every 7, 14, 28 or 30 days."],
        ["Price", "No extra cost and no subscriber discount; operator and Ding promos apply automatically. Processing fee is added at the order summary: about 15 to 23% of subtotal on small orders in Ding's own screenshots."],
        ["Payment on renewals", "Apple Pay, Google Pay, PayPal (iOS app only), Visa and Mastercard. Not Amex, Discover, Venmo, Cash App or the dingMoney balance."],
        ["New in Sep 2026", "dingVIP: a paid monthly membership with a 7-day free trial, sold at checkout as 'Subscribe & save'."],
    ], {"widths": [18, 82], "font_pt": 8.4, "header": False}),
    src(("Ding activate help", U["ding_activate"]), ("2020 launch post", U["ding_2020"]), ("App Store", U["ding_as"]),
        ("Google Play", U["ding_play"]), ("Terms", U["ding_terms"]), ("processing fees", U["ding_fees"]),
        ("Pollen Street", U["ding_pollen"])),
    ("h3", "How the auto top-up flow works"),
    ("numbered", [
        "Choose country and number, then the amount (Top-up or Plans tab).",
        "**A modal appears before the order summary**: 'Set auto top-up' on web, 'Schedule a top-up' in the app. "
        "Frequency chips 7, 14, 28 and 30 days, with 30 highlighted; microcopy 'Renews automatically. No extra "
        "costs. Cancel anytime.'; an equal-weight 'No thanks' button.",
        "**The order summary repeats the choice** ('Auto top-up every 30 days') with Edit and Remove before paying.",
        "Pay. SMS or email confirms activation and frequency. Each run is charged no more than 24 hours before it "
        "is sent; amount and fee are locked at setup, but the USD charge moves with FX.",
        "**Manage.** Web: My Account, Auto top-up, next billing date, Cancel. App: Account, Scheduled top-ups, Edit, "
        "which only offers Cancel. No documented skip, pause or edit after activation.",
    ]),
    ("row", [(SCR + "ding_web_autotopup_card.png", 150, "Account entry point"),
             (SCR + "ding_web_set_autotopup_modal.png", 150, "'Set auto top-up' modal (web)"),
             (SCR + "ding_app_schedule_modal.png", 120, "'Schedule a top-up' (app)")]),
    ("row", [(SCR + "ding_web_order_summary_edit.png", 150, "Order summary: edit auto top-up, fee line"),
             (SCR + "ding_as_history_every30.png", 120, "History: 'Every 30 days', Manage (App Store)"),
             (SCR + "ding_app_autotopup_details.png", 120, "Details: FX disclaimer, Cancel")]),
    ("small", "Screens from Ding's own help centre (" + L("web", U["ding_activate"]) + ", " + L("cancel", U["ding_cancel"]) +
              ", " + L("no thanks", U["ding_nothanks"]) + ", " + L("app", U["ding_app_activate"]) + ", " +
              L("app cancel", U["ding_app_cancel"]) + ") and its " + L("App Store listing", U["ding_as"]) +
              ". Phone numbers are masked by Ding."),
    ("h3", "dingVIP: Ding's first paid subscription layer"),
    ("bullets", [
        "Offered at checkout as two radio cards with no default: **'FREE 7 day trial, Subscribe & save, dingVIP PLUS' "
        "at 8.99 USD vs 'One time top-up' at 11.28 USD** (Jamaica example). 'Continue to payment' stays disabled "
        "until a choice is made.",
        "PLUS tier at **5 USD a month** with 10 monthly credits of 1 USD each (one per order, not combinable with "
        "promo codes), extra Ding points, member offers and priority support.",
        "Cancel shows the benefits you lose and **may offer an alternative that keeps some rewards** (a save offer); "
        "benefits run to the end of the paid period, with one-tap 'Reactivate'.",
        "Eligibility is gated ('we'll tell you when it's available'); help articles published 9 to 14 Sep 2026.",
    ]),
    ("row", [(SCR + "ding_vip_subscribe_save.png", 140, "'Subscribe & save' vs one-time"),
             (SCR + "ding_vip_tier_plus.png", 140, "PLUS tier, 5 USD a month, credits"),
             (SCR + "ding_vip_use_credit.png", 140, "Using a 1 USD credit"),
             (SCR + "ding_vip_reactivate.png", 150, "After cancel: reactivate")]),
    src(("What is dingVIP", U["ding_vip"]), ("subscribe", U["ding_vip_sub"]), ("credits", U["ding_vip_credits"]),
        ("manage", U["ding_vip_manage"])),
    ("h3", "The rest of Ding's retention stack"),
    ("bullets", [
        "**Ding Rewards Club**: points on every top-up (about 2 per USD, so roughly 1% back), medals, 18-month "
        "expiry (" + L("help", U["ding_rewards"]) + ").",
        "**Request top-up** links for receivers, and **Ding Hub** with a monthly lucky draw for receivers who sign up "
        "(" + L("request", U["ding_request"]) + ", " + L("hub", U["ding_hub"]) + ").",
        "**dingMoney**: a free US-sender wallet on a Bridge-issued stablecoin; receivers in 22 countries spend it on "
        "top-ups and gift cards (" + L("help", U["ding_money"]) + ").",
        "**Cubacel presale** ('Reserva tu Recarga'), delivered on promo day (" + L("help", U["ding_presale"]) + ").",
    ]),
    ("row", [(SCR + "ding_as_home_points.png", 120, "Home with points balance"),
             (SCR + "ding_as_amount_plans_tab.png", 120, "Amount screen: Top-up / Plans"),
             (SCR + "ding_as_points_earned.png", 120, "'You earned +37 points'")]),
    ("table", [
        ["What Ding does better than IDT", "Where Ding is weak", "What IDT should take"],
        ["Explicit, repeated consent (modal plus order-summary row); start date with no upfront payment; 28-day "
         "option; recurring visible in History next to 'Send again'; wallets on renewals; a points and "
         "membership layer.",
         "Cancels on the first declined payment (no retry); no skip, pause or edit; terms still say the first "
         "top-up is paid at setup, which contradicts the 2025 flow; sender price floats with FX; fees revealed late.",
         "The consent pattern, the History badge and the start-date option. Leave out the hard cancel on decline "
         "and the floating price."],
    ], {"widths": [34, 33, 33], "font_pt": 8.2}),

    # ------------------------------------------------------------------ Rebtel
    ("pagebreak",),
    ("h2", "4.2 Rebtel: two products, and the only one that prices subscribing lower"),
    ("table", [
        ["Company", "Rebtel Networks AB, Stockholm; US customers contract with Rebtel Canada Inc. Privately held (Balderton, Index Ventures, reported); 2024 revenue about SEK 1.35bn (reported). New CEO April 2025; money transfer shut in 2025."],
        ["Scale", "iOS 4.82 from 125,428 US ratings; Google Play 4.64 from 188,029, 10M+ installs; 3,219 top-up products in 146 destination countries."],
        ["Recurring products", "**Auto Top-Up** schedules any credit or bundle at the one-time price. **Plans** are 36 subscription-only products in Mexico, Dominican Republic, Nigeria, India, Guatemala and Ethiopia."],
        ["Coverage", "3,207 of 3,219 products can recur. The 12 exceptions are all Cuba (Cubacel and Nauta)."],
        ["Launch", "December 2023 (help articles created 22 Dec 2023); terms section 2.16 last updated 16 Oct 2024; Wallet tab with 'My subscriptions' from app 6.83 (Sep 2026)."],
    ], {"widths": [18, 82], "font_pt": 8.4, "header": False}),
    src(("Rebtel terms", U["reb_tos"]), ("help: plans vs bundles", U["reb_diff"]), ("App Store", U["reb_as"]),
        ("Google Play", U["reb_play"]), ("Wikipedia", U["reb_wiki"]), ("Wallet tab", U["reb_wallet"])),
    ("figure", FIG + "fig_rebtel_plans.png", 560, ""),
    ("bullets", [
        "**Teasers.** 11 of 36 Plans carry a first-period price, for example Telcel $3.99 then $14 every 30 days "
        "(3.5x at the second charge), and weekly Guatemala Superplans with a first-week discount.",
        "**Fee asymmetry.** A $0.99 service fee on one-time purchases for three operators does not apply to "
        "subscriptions or renewals (help, Oct 2025; the catalog shows $0 fees today).",
        "**Cadence.** Credits renew every 7, 14, 28 or 30 days (30 preselected); bundles and Plans at their validity "
        "(7 to 84 days). Marketing says 'every 30 days' even where Plans are weekly.",
    ]),
    ("row", [(SCR + "rebtel_mx_hero.png", 150, "Mexico: '3.5 GB, unlimited calls and SMS for $3.99'"),
             (SCR + "rebtel_mx_plans.png", 160, "'Renew automatically every 30 days... first month $3.99'"),
             (SCR + "rebtel_mx_fixed_cancel.png", 160, "'Fixed prices', 'Cancel anytime'")]),
    ("small", "Rebtel's " + L("Mexico recharge page", U["reb_mx"]) + " and " + L("three-tier page", U["reb_generic"]) +
              ", mobile, 29 Sep 2026."),
    ("h3", "Flow and rules"),
    ("bullets", [
        "**Opt-in.** The legacy web checkout opens a pre-payment modal where the sender must pick a cadence or dismiss "
        "it ('Not this time'); the new checkout shows a 'Pay once' / 'Auto Top Up' choice (default not visible "
        "without login); a post-purchase modal offers auto top-up again. The terms allow default-on for some products.",
        "**The first order is always a normal order**; the schedule is created only after it succeeds, so a "
        "subscription failure never blocks the top-up.",
        "**One active Auto Top-Up per number and product**, a built-in duplicate guard.",
        "**Lifecycle is thin.** Deactivate, reactivate, remove or change card; no skip, pause, cadence, amount or date "
        "change. **A declined renewal deactivates the Auto Top-Up**; no retry or grace is documented, and no "
        "pre-renewal reminder was found.",
    ]),
    ("row", [(SCR + "rebtel_as_welcome_offer.png", 120, "App: welcome offers on credits"),
             (SCR + "rebtel_app_your_subs.png", 130, "App: 'Your Subscriptions'"),
             (SCR + "rebtel_web_my_subs.png", 200, "Web: 'My Subscriptions', Every 7 days, Reactivate")]),
    ("small", "Management screens from Rebtel's " + L("deactivate and reactivate help article", U["reb_deact"]) +
              " (numbers and email blurred) and its " + L("App Store listing", U["reb_as"]) + "."),
    ("row", [(SCR + "rebtel_cuba_page.png", 150, "Cuba: carrier bonus and welcome offer, no subscription")]),
    ("table", [
        ["What Rebtel does better than IDT", "Where Rebtel is weak", "What IDT should take"],
        ["A real price reason to subscribe (Plans); near-universal eligibility; consent-based entry points; the "
         "first order stays a normal order; one-per-number duplicate guard; wallets and credits on renewals.",
         "Teaser-to-full-price jumps with no reminder; 'fixed price' marketing but no contractual price lock; "
         "deactivates on decline; no pause or edit; stale help (six articles link to a deleted cancel page); the "
         "heaviest subscription complaint rate in reviews (7.4% of 2026 reviews, mostly calling plans).",
         "Plan-style subscriber pricing on data bundles, the first-order-then-schedule mechanic and the duplicate "
         "guard. Avoid teasers without a reminder."],
    ], {"widths": [34, 33, 33], "font_pt": 8.2}),
    src(("Rebtel terms 2.16", U["reb_tos"]), ("buy a subscription", U["reb_buy"]), ("MTU Q&A", U["reb_qa"]),
        ("payment failed", U["reb_fail"]), ("Cuba page", U["reb_cuba"]), ("Trustpilot", U["reb_trust"])),

    # ------------------------------------------------------------------ Recharge.com
    ("h2", "4.3 Recharge.com (Coda): reminders, not subscriptions"),
    ("bullets", [
        "Amsterdam-based digital prepaid marketplace (16,000+ products across gaming, gift cards and mobile), acquired "
        "by Coda (signed 17 Jul, closed 19 Aug 2025); the combined group processed $1.75B+ in 2024 across 180+ markets "
        "(" + L("Coda", U["rc_coda"]) + ").",
        "**No recurring top-up of any kind.** Its 34-article help centre has no article on recurring payments, "
        "subscriptions, loyalty or referral, its terms have no auto-renewal clause, and its own Trustpilot replies tell "
        "customers it offers no recurring payments.",
        "**What it has instead:** 'Set a recharge reminder' on the post-purchase screen, Reorder, saved and labelled "
        "numbers, 10% off the first app order (up to 5 EUR) and app-only deals (" + L("App Store", U["rc_as"]) + ").",
        "For US senders the flow is a product page per operator (for example " + L("Telcel", U["rc_telcel"]) +
        ") that shows face value only; fees and the USD price appear in the cart. Cuba is not sold. iOS 4.72 from only "
        "2,233 US ratings: a small US presence.",
    ]),
    ("row", [(SCR + "rc_telcel_page.png", 130, "Telcel page and '10% off in the app'"),
             (SCR + "rc_as_reminder.png", 120, "'Set a recharge reminder' (App Store)"),
             (SCR + "rc_as_payment_methods.png", 120, "56+ payment methods")]),

    # ------------------------------------------------------------------ Miron
    ("h2", "4.4 MobileRecharge, TopUp.com and KeepCalling (Miron Enterprises)"),
    ("bullets", [
        "Atlanta-based US diaspora apps from one seller (founded 2002, rebranding to Tello since June 2025). "
        "MobileRecharge advertises **'Activate Auto Top-up at Checkout and we'll automatically send credit on your "
        "behalf every 7, 14, 28, or 30 days'** on its home page (" + L("site", U["mr_web"]) + "). The feature has run "
        "on the web since 2022 and is shared by KeepCalling, TopUp.com and HablaMexico.",
        "**Mechanics.** An opt-in toggle in the logged-in checkout; priced like a one-time order (processing fee from "
        "$1, no subscriber discount); charged up to 24 hours before sending; an optional 'notify me 48 hours in advance' "
        "tick; cancel from the dashboard, effective immediately; no pause or skip.",
        "**Friction.** It can only be switched on or edited inside a new paid order. It switches itself off after a "
        "declined payment and 12 hours of retries, an operator change, or a price rise above 6%; smaller rises apply "
        "silently.",
        "Scale is modest: MobileRecharge iOS 4.73 from 9,578 ratings; KeepCalling 4.62 from 18,972 (" +
        L("MobileRecharge", U["mr_as"]) + ", " + L("KeepCalling", U["kc_as"]) + ", " + L("TopUp.com", U["topup_as"]) +
        "). No App Store review discusses the auto top-up; two older reviews asked for it.",
    ]),
    ("row", [(SCR + "mr_web_autotopup.png", 200, "MobileRecharge home: Auto Top-up at checkout"),
             (SCR + "mr_as_history.png", 120, "Order history with 'Resend' (App Store)")]),

    # ------------------------------------------------------------------ Carriers
    ("pagebreak",),
    ("h2", "4.5 Carriers selling direct"),
    ("bullets", [
        "**Digicel** (Haiti, Jamaica and the Caribbean) runs a free **Auto Top Up every 7, 14, 28 or 30 days** in the "
        "Digicel International app and web, cancelled from a delete link. Its checkout shows an 'Auto pay enabled' "
        "checkbox ('this plan will be auto renewed until cancelled'), and the home screen shows **'Renew before it's "
        "too late'** cards. Diaspora plans can also auto-renew on the recipient's own credit (" +
        L("App Store", U["digicel_as"]) + ", " + L("FAQ", U["digicel_faq"]) + ").",
        "**Telcel** runs 'recargas programadas' on international cards through its own recharge portal (monthly on a "
        "chosen day, or biweekly), with Telcel promos applied; whether a US sender without a Telcel line can register "
        "is unverified (" + L("portal", U["telcel_portal"]) + ").",
        "**Natcom (Haiti) and Viva (Dominican Republic)** have 'official' apps built and run by Elemt / Prepay Nation "
        "with Autotop (weekly, every two weeks, monthly; several schedules, edit or cancel any time). Natcom pitches "
        "auto top-up to Haitians abroad as a way to **keep their own home number alive** (" +
        L("Natcom app", U["natcom_play"]) + ", " + L("blog", U["natcom_blog"]) + ").",
        "**Claro and Tigo** do not schedule for senders abroad. Claro Dominican Republic and Guatemala link senders to "
        "partners, **Boss Revolution among them** (" + L("Claro RD", U["claro_rd"]) + ", " + L("Claro GT", U["claro_gt"]) + ").",
    ]),
    ("row", [(SCR + "digicel_as_renew_nudge.png", 120, "Digicel: 'Renew before it's too late'"),
             (SCR + "digicel_as_autopay_checkbox.png", 120, "Digicel: 'Auto pay enabled' checkbox"),
             (SCR + "etopup_autotopup.png", 130, "eTopUpOnline: weekly, half-monthly, monthly")]),
    ("small", "Digicel screens from its " + L("App Store listing", U["digicel_as"]) + "; eTopUpOnline from its "
              + L("auto top-up guide", U["etopup_blog"]) + "."),
    ("callout", "warn",
     "**Why carriers matter for IDT.** Every operator that signs with a white-label storefront (Elemt runs nine) moves "
     "recurring top-ups toward the carrier's own 'official' channel, and Digicel already sets the default expectation "
     "for Haiti and Jamaica senders: free, cancellable, with a renewal nudge."),

    # ------------------------------------------------------------------ Cuba
    ("h2", "4.6 Cuba: promo-triggered delivery beats the calendar"),
    ("bullets", [
        "Cubacel's big bonuses (x5, x6 main balance) run in short windows, roughly monthly, for 3 to 7 days, and only "
        "for international recharges inside CUP amount bands such as 600 to 1,250 CUP (" + L("example", U["cubacel_x6"]) + ").",
        "A fixed-date, fixed-amount subscription will often miss those windows. Specialists sell **presale** instead: "
        "reserve now, delivered when the promo starts (" + L("Cuballama", U["cuballama"]) + ", " + L("Ensip", U["ensip"]) +
        ", Ding's " + L("Reserva tu Recarga", U["ding_presale"]) + "). aCuba lets users schedule a recharge (" +
        L("App Store", U["acuba"]) + ").",
        "Fonoma says outright that it does not schedule, and uses promo alerts plus 3% credit on every recharge "
        "(" + L("FAQ", U["fonoma"]) + "). Rebtel excludes Cuba from subscriptions entirely.",
        "BR's own Cubacel blog advises splitting recharges to multiply bonuses, which a calendar subscription works "
        "against. With Western Union's Cuba channel closed since February 2025, top-ups are one of the few formal "
        "US-to-Cuba value channels (OFAC 515.542 authorizes them, with notification and semiannual reports, " +
        L("eCFR", U["ofac"]) + ").",
    ]),
    ("row", [(SCR + "cuballama_preventa.png", 170, "Cuballama: plans only in presale periods"),
             (SCR + "cubatel_as.png", 120, "Cubatel: zero-fee recharges")]),

    # ------------------------------------------------------------------ Remittance and chat
    ("h2", "4.7 Remittance and chat apps: no recurring top-ups, but they set expectations"),
    ("bullets", [
        "**No remittance app schedules top-ups.** Remitly and Sendwave do not sell airtime to US senders; Western "
        "Union and MoneyGram resell Ding's checkout without scheduling; Xoom, WorldRemit, Taptap Send, Intermex and Ria "
        "sell one-off reloads only (" + L("WU", U["wu_reload"]) + ", " + L("MoneyGram", U["mg_topup"]) + ", " +
        L("Xoom", U["xoom"]) + ", " + L("WorldRemit", U["wr"]) + ", " + L("Taptap Send", U["taptap"]) + ").",
        "**Remitly One** proves US senders will pay a membership: $9.99 a month for send-now-pay-later, wallet rewards "
        "and up to $5 a month cashback, open to select US customers (" + L("Remitly One", U["remitly_one"]) + ").",
        "**Félix Pago** sells recargas natively inside WhatsApp, with the cost built into the FX rate; its public guide "
        "names Boss Revolution and Ding as the incumbents; it raised $200M in September 2026 and its CEO says recargas "
        "grow more than 100% a month (" + L("Félix", U["felix"]) + ", " + L("guide", U["felix_guide"]) + ", " +
        L("raise", U["felix_raise"]) + ", " + L("growth", U["felix_growth"]) + "). No recurring recarga yet, but a chat "
        "thread is the easiest place to add 'same recarga every month'.",
        "**WhatsApp Send** at Remitly (US since April 2025) and US WhatsApp sending at Taptap Send show the channel is "
        "live for US senders (" + L("Remitly", U["remitly_wa"]) + ", " + L("Taptap", U["taptap_wa"]) + ").",
        "**IDT's own benchmark:** BOSS Money already runs recurring transfers (weekly, biweekly, monthly; notice the day "
        "before; cancel by swipe), better documented than any peer's (" + L("BOSS Money FAQ", U["bm_faq"]) + "). "
        "MoneyGram says it cannot schedule transfers at all (" + L("FAQ", U["mg_recurring"]) + ").",
    ]),
    ("row", [(SCR + "felix_recargas.png", 140, "Félix Pago: recargas by WhatsApp"),
             (SCR + "remitly_one.png", 170, "Remitly One: $9.99 a month")]),
]
