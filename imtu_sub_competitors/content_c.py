"""Doc content, part C: head-to-head, reviews, regulation, strengths, trends, recommendations, plan, appendix."""
import data as D
from content_a import FIG, SCR, J, L, U, src

LEAD, PAR, GAP, BEH = ("#e6f4ea", "#1d5e33"), ("#f0efec", "#3d3b36"), ("#fdf2dc", "#7a5410"), ("#fbe8e8", "#8b2222")
VERDICT = {"Lead": LEAD, "Parity": PAR, "Gap": GAP, "Behind": BEH}


def verdict_table(rows, col=3, widths=None, font_pt=8.0):
    cell_bg = {}
    for r, row in enumerate(rows):
        if r and row[col] in VERDICT:
            cell_bg[(r, col)] = VERDICT[row[col]]
    return ("table", rows, {"widths": widths, "font_pt": font_pt, "cell_bg": cell_bg})


LIFECYCLE = [
    ["Stage", "IDT today", "Best in market", "IDT verdict"],
    ["1. Discover", "Toggle on the order screen and a home widget; not in the App Store listing or public help",
     "Ding: 'Every 30 days' badge and Manage in History, next to Send again; Digicel: renewal cards on home", "Behind"],
    ["2. Consent", "Pre-ticked for most users since 20 Jun 2026; explicit prompt only when the default is off",
     "Ding: modal with 'No thanks' plus an editable order-summary row; Rebtel: cadence pick before payment", "Gap"],
    ["3. Configure", "7, 14, 30, 90 days, defaulted from offer validity; no start date; first charge now",
     "Ding: start date with nothing paid upfront, 28-day option; eTopUpOnline: start date and processing day", "Parity"],
    ["4. Price and value", "Same price as one-time; subscription promo built, not launched",
     "Rebtel Plans 3 to 17% cheaper, teasers; dingVIP credits and points", "Gap"],
    ["5. Payment methods", "Cards with an in-flight fallback card; wallet disabled; Apple Pay and Google Pay in progress",
     "Ding and Rebtel: Apple Pay, Google Pay and PayPal on renewals; Rebtel Credits", "Gap"],
    ["6. Before each charge", "Push 2 days before every charge",
     "IDT; TopUp.com optional 48-hour notice; Digicel renewal card", "Lead"],
    ["7. Failed payment", "Stays active and silent; retried next cycle; 28% failing (Apr 2026)",
     "MobileRecharge retries for 12 hours, then switches off; Ding cancels; Rebtel deactivates. All at least stop charging", "Behind"],
    ["8. Manage", "Edit offer, cadence and card (partly built); next-date edit in progress; no pause or skip",
     "Natcom (Elemt): edit any time; nobody offers pause or skip", "Parity"],
    ["9. Cancel", "Self-serve, 5 taps, yes/no dialog; enhanced survey and save flow in QA",
     "Ding: immediate self-serve; dingVIP: save offer and one-tap reactivate", "Parity"],
    ["10. Win back and loyalty", "65% of cancellers buy one-time within 60 days; no win-back; loyalty punch cards",
     "Ding Rewards Club and dingVIP reactivate; Fonoma 3% credit; Cuballama cashback", "Gap"],
    ["11. Corridor fit", "Calendar only; no line-status check",
     "Cuba presale that delivers on promo day (Cuballama, Ensip, Ding)", "Gap"],
    ["12. Scale and reach", "Largest base; two apps; retail network; five sender markets",
     "IDT", "Lead"],
]

REG = [
    ["Requirement", "Rule", "IDT today", "Action"],
    ["Clear terms next to the consent: what, how much, how often, until cancelled, how to cancel",
     L("ROSCA", U["rosca"]) + "; " + L("California 17602", U["ca_arl"]) + "; " + L("Minnesota", U["mn_arl"]) + "; " +
     L("Massachusetts", U["ma_arl"]) + "; NYC; " + L("Visa", U["visa_rules"]),
     "Savings copy and 'Manage or cancel anytime'; no 'continues until you cancel' or next charge date", "Add one disclosure line under the section, Spanish-first"],
    ["Express, separate consent to the recurring terms", "ROSCA; California; NYC; Visa",
     "Pre-ticked for most users", "Explicit choice (see recommendation 1)"],
    ["Keep proof of consent for 3 years", "California", "Toggle state at submission is not logged", "Store a consent record with copy version and timestamp"],
    ["Enrollment confirmation with cancel instructions", "California; Minnesota; Visa; Mastercard",
     "Push on purchase", "Add a retainable email or in-app receipt with terms, next date and cancel link"],
    ["Receipt for every charge with amount and how to cancel", "Massachusetts (monthly plans); Visa; Mastercard",
     "Renewal receipt not observable", "Renewal receipt by push and email with a cancel link"],
    ["Click-to-cancel in the same channel, effective immediately", "California; Minnesota; Massachusetts; Colorado; Virginia; NYC",
     "In-app cancel exists; no web page", "Keep it within two steps; add a web page (also needed for Apple Pay)"],
    ["Save offers only with cancel always visible; ask permission first in Minnesota", "California; Minnesota; Colorado",
     "Enhanced flow keeps 'Cancel subscription' on every save screen", "Legal review before launch; one ask per attempt"],
    ["Notice or consent before a price change", "California 7 to 30 days; New York consent; Visa 7 days; " + L("Reg E", U["rege"]) + " 10 days for debit",
     "Renewal price rule not defined (dynamic pricing, FY27 B1)", "Lock the USD price per plan, or take consent to a narrow range"],
    ["Annual reminder for continuous service", "California; Minnesota; Connecticut (any term, from 1 Jul 2026)", "None", "Yearly summary message"],
    ["Reminder before a teaser ends", "Visa (7 days); California; Maryland", "Subscription promo not launched", "Required if the promo discounts the first charge"],
    ["Stored-credential consent and recurring flags", "Visa and Mastercard MIT framework", "Stripe via IDT Pay; Apple Pay MPAN design", "Confirm MIT flags; add network tokens"],
    ["Cuba: OFAC notice and semiannual reports", L("31 CFR 515.542", U["ofac"]), "To confirm for recurring top-ups", "Confirm with compliance"],
]

TRENDS = [
    ["#", "Trend", "Evidence", "What it means for IMTU subscriptions"],
    ["1", "Low growth, fewer senders", "Mexico remittances -3.9% in 2025, +3.1% YTD with transactions -1.6% (" + L("Banxico", U["banxico"]) +
     "); Central America +7.1% YTD; IDT Digital Payments +3% (" + L("FY26", U["idt_fy26"]) + ")",
     "Subscriptions are a retention and share-of-wallet engine for a shrinking but deepening base, not an acquisition engine"],
    ["2", "Enforcement climate", "320,000 ICE removals in FY25; precautionary sending; Hispanic spending pullback",
     "Expect abrupt sender exits (involuntary churn); offer pause, skip, change recipient"],
    ["3", "Cash to digital", "BOSS Money 88% digital; WU 43% (" + L("WU Q2", U["wu_q2"]) + "); 1% tax on cash transfers",
     "Use the subscription as the digital hook for retail cash customers, with online cancel"],
    ["4", "Mexico CURP suspensions", "Deadlines 15 Oct to 31 Dec 2026; ~42% unregistered mid-Sep (" + L("Infobae", U["curp"]) +
     "); suspended lines still accept top-ups (" + L("Xataka", U["curp_susp"]) + ")",
     "Check line status before each charge; auto-pause and warn the sender. Top Q4 risk"],
    ["5", "Best prepaid users move to postpaid", "Telcel 81% prepaid, flat (" + L("America Movil", U["amx"]) + "); Millicom Guatemala postpaid +19%",
     "Protect high-value recipients with bigger bundles; postpaid bill pay as the next subscription"],
    ["6", "Airtime becomes data", "BR calling revenue -15% in FY26; carrier bundles at 7 and 30-day validity",
     "Bundle-first catalog with cadence matched to validity; show GB and WhatsApp, not currency"],
    ["7", "Promo calendars and Cuba policy", "Cubacel x5/x6 windows roughly monthly; WU Cuba channel closed since Feb 2025",
     "'Deliver on the next promo' scheduling is a real differentiator in Cuba"],
    ["8", "Chat, wallets and stablecoins", "Félix $200M and recargas in WhatsApp; " + L("WhatsApp recharges in India", U["wa_india"]) +
     "; dingMoney and BOSS Money wallets; GENIUS Act by Jan 2027",
     "Manage subscriptions by message; fund renewals from a wallet balance to cut card declines"],
    ["9", "Feature parity and consolidation", "Coda bought Recharge (" + L("Coda", U["coda"]) + "); DT One bought DENT (" +
     L("DT One", U["dtone"]) + "); WU and Intermex pending (" + L("SEC", U["wu_intermex"]) + ")",
     "Recurring alone no longer differentiates; win on reliability, promo capture, price lock and FX transparency"],
    ["10", "Auto-renewal rules tighten", "State laws in force; NYC 1 Oct 2026; Louisiana 1 Jan 2027 (" + L("Kelley Drye", U["nyc_la"]) +
     "); " + L("FTC ANPRM", U["ftc_anprm"]) + "; " + L("Amazon $2.5B", U["ftc_amazon"]),
     "Build to the strictest common standard: explicit consent, receipts, click-to-cancel, price-change notice"],
]

RECS = [
    ["#", "Improvement", "Why (evidence)", "Precedent", "Size", "Impact", "Existing work"],
    ["1", "**Replace the pre-ticked default with an explicit, well-framed choice**, tested against default ON on net active subscriptions and revenue, not attach",
     "46.6% switch off in 7 s; 30.6% cancel in 30 days; review spike; ROSCA and state consent rules", "Ding modal and summary row; Rebtel cadence pick", "M", "High",
     J("DCS-5345") + ", " + J("DCS-5590") + ", " + J("DCS-5546")],
    ["2", "**Compliance pack**: disclosure line, enrollment receipt, per-charge receipt with cancel link, annual reminder, consent record",
     "MA per-charge notice; Visa and Mastercard receipts; NYC from 1 Oct 2026", "Ding confirmations", "S-M", "High", J("DCS-5575") + ", " + J("DCS-5260")],
    ["3", "**Failed-payment recovery**: tell the sender, 2 to 3 timed retries within 7 days, card updater and network tokens, then the tiered soft auto-cancel",
     "28% failing; silent failures; a third of subscription churn is payments (" + L("Recurly", U["recurly"]) + "); Stripe recovers 55% (" +
     L("Stripe", U["stripe"]) + ")", "Only MobileRecharge retries (12 hours): a chance to lead", "M", "High", J("DCS-5420") + ", CRMC-3299"],
    ["4", "**Duplicate guard**: one active subscription per recipient and offer, an in-session guard, clean up surplus actives",
     "1,094 customers paying 3,469 surplus subscriptions; 995 removed their only card", "Rebtel one-per-number rule", "S-M", "High",
     J("DCS-5580") + ", " + L("cleanup rules", U["dups"])],
    ["5", "**Pause or skip a cycle; change date, amount and recipient**", "Nobody offers it; pause usage up 337% at top Recurly merchants (" +
     L("Recurly 2026", U["recurly26"]) + ")", "None in IMTU", "M", "High", J("DCS-5501") + ", FY27 B2"],
    ["6", "**Ship the enhanced cancel flow**: exit survey first, then test pause before discount as the save offer",
     "No reason captured today; save acceptance 15 to 21% for pause and discount (" + L("Chargebee", U["chargebee"]) + ")",
     "dingVIP save offer and reactivate", "S", "High", J("DCS-5257") + ", " + J("DCS-5418") + ", " + J("DCS-5375")],
    ["7", "**Give subscribing a price reason**: price lock per plan and a small bonus or fee waiver; Plans-style data bundles below one-time",
     "Rebtel Plans 8 to 15% cheaper; IDT promo built but unused", "Rebtel Plans; Rebtel $0.99 fee waiver", "M-L", "High",
     J("DCS-5429") + ", " + J("DCS-4504")],
    ["8", "**Start date and 'schedule without paying now'**; add a 28-day cadence", "Carrier plans run 28 days; Ding and Digicel offer it",
     "Ding 2025 flow; Digicel", "M", "Med", ""],
    ["9", "**Wallets on renewals**: Apple Pay and Google Pay, then PayPal and the BOSS Money wallet when compliance allows",
     "Cards only today; FY27 B4 targets 30% wallet share", "Ding; Rebtel", "Under way", "Med", L("Apple Pay flow", U["applepay"])],
    ["10", "**Corridor intelligence**: Mexico CURP line check and auto-pause now; Cuba promo-aware delivery next",
     "6 of 10 CURP deadline groups fall 15 Oct to 31 Dec; Cubacel value sits in promo windows", "Cuballama, Ensip, Ding presale", "M", "High", ""],
    ["11", "**Make it visible**: History badge with Manage, My Subscriptions hub, store screenshots, public help page",
     "Subscriptions absent from the store listing and help; widget works as a cancel surface", "Ding History badge; BOSS Money FAQ",
     "S", "Med", J("DCS-5505")],
    ["12", "**Loyalty and membership pilot**: points per renewal, or a paid tier with credits and perks", "dingVIP ($5 a month); Remitly One ($9.99)",
     "Ding; Remitly", "L", "Med", ""],
    ["13", "**Family and recipient-led**: several recipients on one subscription; recipient requests; keep-your-own-number use case",
     "50 to 60% send to one recipient, 20% to two, 15% to three", "Ding Request top-up; Natcom", "M", "Med", ""],
    ["14", "**WhatsApp management**: reminders, pause, skip and cancel by message", "Félix growth; WhatsApp live for US senders",
     "Félix, Remitly, Taptap", "M-L", "Med", "FY27 WhatsApp MTU chatbot"],
    ["15", "**Measure it**: renewal event, subscription_id, cancel reason, failure flag, payment method, toggle state at submission",
     "Renewals, failures and involuntary churn cannot be measured today", "", "S-M", "Enabling", J("DCS-5260") + ", " + J("DCS-5511")],
]

KPIS = [
    ["KPI", "Baseline", "Target by Sep 2027", "Source of baseline"],
    ["New subscriptions cancelled within 30 days", "30.6% (Mar to Aug 2026)", "Below 18%", L("Journey v2", U["journey"])],
    ["Monthly voluntary cancellations", "~5,700 a day (late Aug)", "-20% vs FY27 Q1 (FY27 B2)", "Exec deck, Sep 2026"],
    ["Cancel-flow openers who pause or keep", "1 to 4% (yes/no dialog)", "30% or more (FY27 B2)", L("Journey v2", U["journey"])],
    ["Failed renewals recovered within 7 days", "0% (no retry)", "40% or more", "Stripe benchmark 55%"],
    ["Share of active subscriptions failing", "28.4% (Apr 2026)", "Below 8%", L("Journey v2", U["journey"])],
    ["Surplus duplicate active subscriptions", "3,469", "0; new duplicates under 10 a week", L("Duplicates analysis", U["dups"])],
    ["Active subscriptions 90 days after purchase, per 100 purchasers", "Not measured", "Baseline in Q4, +20% by Q3", "New metric"],
    ["Wallet share of new payment methods", "0%", "Above 30% within two months of launch (FY27 B4)", "FY27 plan"],
    ["App Store reviews mentioning subscriptions", "5.0% (Jul to Sep 2026)", "Below 1%", "Review coding, this doc"],
]

PHASES = [
    ["Window", "Focus", "Deliverables", "Exit criteria"],
    ["Oct to Dec 2026", "Stop the leaks, measure",
     "Renewal and failure events; ship payment bar and enhanced cancel flow; failure notice and tiered auto-cancel; duplicate guard and cleanup; "
     "compliance pack; Mexico CURP line check; explicit-choice A/B live",
     "Gate 1 (31 Dec): renewal success measurable, surplus duplicates at zero, A/B powered"],
    ["Jan to Mar 2027", "Give control",
     "Pause and skip; change date, amount and recipient; My Subscriptions hub; retries and card updater; save-offer test (pause first); A/B readout and default decision",
     "Gate 2 (31 Mar): 30-day cancel below 22%, save rate above 15%, default policy decided"],
    ["Apr to Jun 2027", "Make it worth it",
     "Subscriber price lock and bonus test; Plans-style data bundles in Mexico, Guatemala, Honduras and Dominican Republic; Apple Pay and Google Pay on renewals; web and WhatsApp management; Cuba promo-aware build",
     "Gate 3 (30 Jun): value test read out on revenue per subscriber"],
    ["Jul to Sep 2027", "Scale what works",
     "Membership pilot; multi-recipient; retail enrollment with online cancel; BOSS Money parity; new sender markets",
     "Targets in the KPI table"],
]

RISKS = [
    ["Risk", "Mitigation"],
    ["Explicit choice lowers attach", "Judge on net active subscriptions and revenue at 90 days, not attach; pair the choice with a clear benefit"],
    ["Retries raise processor cost and fraud", "Cap attempts, time them to paydays, use Radar and network tokens; each failed attempt costs about 7 cents today"],
    ["Promo margin", "Save offer first (pause), price test second; no stacking with instant promos (13 Aug decision)"],
    ["Carrier offers change under subscribers", "Keep the replacement-product mapping; notify before a price or content change"],
    ["Backend capacity", "FY27 plan already shows a backend bottleneck; sequence measurement and payment health first, keep app-only items parallel"],
    ["Regulatory change", "Build to the strictest state rules now; watch the FTC NPRM and card-network updates"],
]

DECISIONS = [
    "**Default policy test.** Approve an A/B of explicit choice vs default ON, judged on net active subscriptions and revenue at 90 days.",
    "**Promo timing.** Save offer first (pause, then a discount), then a price-lock and bonus test for new subscribers.",
    "**Failed-payment rule.** Soft cancel with notice (the tiered 3/2 rule) rather than hard delete, which would break 18,758 purchase records.",
    "**Mexico CURP.** Approve a line-status check and auto-pause before the October to December deadline waves.",
    "**Cuba.** Approve a spike on promo-aware delivery sized to Cubacel bands.",
    "**Legal review.** Compliance pack and save-offer flow, ahead of NYC (1 Oct 2026) and Louisiana (1 Jan 2027).",
]


def appendix_matrix():
    head = ["Capability"] + [p[2] for p in D.PLAYERS]
    rows = [head]
    lab = {"Y": "Yes", "P": "Part", "N": "No", "-": "n/a", "?": "?"}
    for ck, clabel in D.CAPABILITIES:
        rows.append([clabel] + [lab[D.MATRIX[pk][ck]] for pk, _, _ in D.PLAYERS])
    return ("table", rows, {"font_pt": 6.8, "widths": [23] + [7.7] * len(D.PLAYERS)})


def app_table():
    rows = [["App", "US App Store ratings", "Average stars", "Google Play installs"]]
    for name, n, stars, play, _ in D.APP_SCALE:
        rows.append([name, f"{n:,}", f"{stars:.2f}", play])
    return ("table", rows, {"widths": [34, 24, 18, 24], "font_pt": 8.2})


BLOCKS_C = [
    ("pagebreak",),
    ("h1", "5. Head-to-head across the subscription lifecycle"),
    ("figure", FIG + "fig_optin_flows.png", 624, ""),
    verdict_table(LIFECYCLE, widths=[14, 32, 40, 14]),
    ("small", "Verdict: Lead = IDT is best in market; Parity = comparable; Gap = a competitor does it better; Behind = IDT is "
              "clearly worse or exposed."),
    ("figure", FIG + "fig_failed_payment.png", 600, ""),

    ("pagebreak",),
    ("h1", "6. What customers say"),
    ("figure", FIG + "fig_reviews.png", 600, ""),
    ("p", "Across 7,367 US written reviews, only 11 discuss a recurring mobile top-up; the subscription talk is mostly "
          "calling plans and calling-balance auto-recharge (120 mentions). When subscriptions come up, it is mostly bad "
          "news: the 162 mentions average 2.27 stars against 3.79 overall."),
    ("table", [["Theme (all 10 apps)", "Mentions"]] + [[t, str(n)] for t, n in D.REVIEW_THEMES],
     {"widths": [70, 30], "font_pt": 8.4}),
    ("bullets", [
        "**BR's spike is about consent and control.** All 14 BR mentions in 2026 are 1 to 3 stars: enrolled without "
        "noticing (6), charged unexpectedly (8), could not cancel (4). None names the top-up subscription explicitly "
        "(four are calling auto-recharge or plans), so this should be checked against billing data.",
        "**What users love:** set and forget, a low flat price, flexible cadence, an easy exit. Twelve reviews describe "
        "manual monthly habits, and several ask for automatic top-ups on a chosen date: latent demand.",
        "**What users hate:** enrollment they did not notice, charges after cancelling, no in-app cancel, unused "
        "credit that does not roll over.",
        "**Spanish speakers barely write reviews** (19% of top-up app reviews, 3 of 159 mentions), so reviews under-"
        "represent IDT's core users; in-app surveys are the better channel.",
    ]),

    ("pagebreak",),
    ("h1", "7. Regulation and compliance"),
    ("p", "The FTC's click-to-cancel rule was vacated in July 2025 (" + L("Latham", U["vacatur"]) + "), and the FTC "
          "restarted rulemaking in March 2026 (" + L("ANPRM", U["ftc_anprm"]) + "). Enforcement under ROSCA continues "
          "($2.5B " + L("Amazon Prime settlement", U["ftc_amazon"]) + "), and state and city rules keep adding "
          "requirements (" + L("ZwillGen tracker", U["zwillgen"]) + "). The checklist below builds to the strictest "
          "common standard; items are design interpretations for counsel to confirm."),
    ("table", REG, {"widths": [26, 24, 25, 25], "font_pt": 7.6}),

    ("h1", "8. What IDT is strong at, and what competitors are strong at"),
    verdict_table([
        ["Dimension", "IDT", "Strongest competitor", "Verdict"],
        ["Scale and reach", "277,506 US ratings on BR; ~45k new subscriptions a week; two apps; retail; 5 sender markets",
         "Rebtel 125k ratings; Ding 84k", "Lead"],
        ["Checkout attach", "Subscription is the top-up being bought; payment conversion within 1 point of one-time",
         "Ding and Rebtel add a step", "Lead"],
        ["Renewal notice", "Push 2 days before every charge", "TopUp.com optional 48-hour notice", "Lead"],
        ["Carrier-change handling", "Automatic replacement product when an offer retires", "Not documented elsewhere", "Lead"],
        ["Consent quality", "Pre-ticked default; 46.6% switch off", "Ding explicit modal and summary row", "Behind"],
        ["Value for subscribing", "None live", "Rebtel Plans; dingVIP", "Gap"],
        ["Payment recovery", "Silent failures", "Nobody good; MobileRecharge retries 12 hours; Ding and Rebtel stop", "Behind"],
        ["Control after purchase", "Edit, no pause", "Natcom edit; nobody pauses", "Parity"],
        ["Payment methods on renewal", "Cards", "Ding, Rebtel: Apple Pay, Google Pay, PayPal", "Gap"],
        ["Loyalty and ecosystem", "Loyalty punch cards, referral", "Ding Rewards Club, dingVIP, dingMoney, Request top-up", "Gap"],
        ["Corridor fit (Cuba, Mexico)", "Calendar only", "Cuba presale specialists", "Gap"],
        ["Chat channel", "Not public", "Félix inside WhatsApp", "Gap"],
    ], widths=[20, 34, 32, 14]),

    ("pagebreak",),
    ("h1", "9. Trends for the next 12 months"),
    ("figure", FIG + "fig_timeline.png", 624, ""),
    ("table", TRENDS, {"widths": [4, 18, 40, 38], "font_pt": 7.6}),
    ("p", "**Watch list** (lower 12-month impact): agentic commerce (" + L("Visa", U["visa_agent"]) + ", " +
          L("Google AP2", U["ap2"]) + ") makes trigger-based 'keep it topped up up to $30 a month' mandates plausible, "
          "so the Zendit API should be mandate-ready; eSIM penetration doubles in 2026 and 2027 (" + L("GSMA", U["esim"]) +
          "), mostly on the sender side, a cross-sell for trips home; 5G raises bundle sizes over time."),

    ("pagebreak",),
    ("h1", "10. Improvements for IDT's IMTU subscription"),
    ("p", "Fifteen improvements, ordered by what they protect first. Size: S under a sprint, M one to three sprints, "
          "L more than a quarter across teams."),
    ("table", RECS, {"widths": [3, 27, 23, 13, 7, 8, 19], "font_pt": 7.2}),
    ("h3", "The five that matter most"),
    ("numbered", [
        "**Earn the opt-in (1, 2).** The default is doing the selling, and customers notice: switch-offs in seconds, "
        "one in three cancelled within a month, and a review spike. Test an explicit, benefit-led choice (Ding's modal "
        "and summary row are the model) against default ON, and judge on net active subscriptions and revenue at 90 "
        "days. Ship the compliance pack whatever the outcome.",
        "**Recover failed payments (3, 4).** No competitor runs a recovery ladder (MobileRecharge retries for 12 hours at most), so this is the fastest way to lead. Tell the sender, "
        "retry on a schedule, refresh cards, and only then soft-cancel with notice. Fix duplicates at the same time.",
        "**Pause beats cancel (5, 6).** Give a pause or skip before the cancel button, capture the reason, and test "
        "save offers in the enhanced flow already built.",
        "**A reason to stay (7, 9).** Price lock plus a small bonus, or Plans-style bundles below one-time, and wallets "
        "on renewals.",
        "**Corridor intelligence (10).** Mexico CURP handling is urgent this quarter; Cuba promo-aware delivery is the "
        "differentiator no generalist offers.",
    ]),

    ("pagebreak",),
    ("h1", "11. Plan for IMTU subscriptions, Oct 2026 to Sep 2027"),
    ("figure", FIG + "fig_plan.png", 624, ""),
    ("table", PHASES, {"widths": [13, 14, 48, 25], "font_pt": 7.8}),
    ("h3", "KPIs and targets"),
    ("table", KPIS, {"widths": [36, 20, 24, 20], "font_pt": 7.8}),
    ("h3", "Experiments"),
    ("bullets", [
        "**A/B 1, consent:** explicit benefit-led choice vs default ON (users randomised, arm stored server side). "
        "Primary metric: active subscriptions per 100 purchasers at 90 days; guardrails: checkout conversion, complaints.",
        "**A/B 2, save offer:** pause first vs discount first vs no offer, inside the enhanced cancel flow.",
        "**A/B 3, value:** price lock with bonus vs price lock only vs control, on new subscribers in two corridors.",
        "**Pilot, Cuba:** promo-aware delivery vs calendar for Cubacel subscribers.",
    ]),
    ("h3", "Dependencies and risks"),
    ("table", RISKS, {"widths": [34, 66], "font_pt": 8.0}),
    ("h3", "Decisions needed now"),
    ("numbered", DECISIONS),

    ("pagebreak",),
    ("h1", "Appendix"),
    ("h2", "A. App fact sheet"),
    app_table(),
    ("small", "US App Store via the iTunes lookup API; Google Play bands from listing pages; 29 Sep 2026."),
    ("h2", "B. Capability matrix as a table"),
    appendix_matrix(),
    ("h2", "C. Sources"),
    ("p", "**IDT internal.** " + ", ".join([
        L("Subscription Journey v2 (31 Aug 2026)", U["journey"]), L("Toggle opt-out and 60-day cancellation (3 Sep 2026)", U["toggle"]),
        L("Logic Reference (20 Aug 2026)", U["logic"]), L("Duplicate subscriptions (23 Sep 2026)", U["dups"]),
        L("Apple Pay subscription flow", U["applepay"]), L("Monthly review notes (25 Aug 2026)", U["monthly"]),
        L("Toggle rules backend spike (18 Sep 2026)", U["bespike"]), L("FY27 suggestions (Jun 2026)", U["fy27sugg"]),
        L("Journey evidence dashboard", U["amp_journey"]), L("Toggle dashboard", U["amp_toggle"]), L("Home dashboard", U["amp_home"]),
        L("Figma: payment bar", U["figma_bar"]), L("Figma: cancellation flow", U["figma_cancel"]),
        L("Figma: edit subscription", U["figma_edit"]), L("Figma: next charge date", U["figma_date"])]) + "."),
    ("p", "**Ding.** " + ", ".join([L("App Store", U["ding_as"]), L("Google Play", U["ding_play"]), L("Terms (archived May 2026)", U["ding_terms"]),
        L("activate", U["ding_activate"]), L("cancel", U["ding_cancel"]), L("no thanks", U["ding_nothanks"]),
        L("app activate", U["ding_app_activate"]), L("app cancel", U["ding_app_cancel"]), L("dingVIP", U["ding_vip"]),
        L("subscribe", U["ding_vip_sub"]), L("credits", U["ding_vip_credits"]), L("manage", U["ding_vip_manage"]),
        L("Rewards Club", U["ding_rewards"]), L("dingMoney", U["ding_money"]), L("processing fees", U["ding_fees"]),
        L("Request top-up", U["ding_request"]), L("Ding Hub", U["ding_hub"]), L("Cubacel presale", U["ding_presale"]),
        L("2020 launch", U["ding_2020"]), L("Pollen Street", U["ding_pollen"])]) + "."),
    ("p", "**Rebtel.** " + ", ".join([L("Terms", U["reb_tos"]), L("three-tier page", U["reb_generic"]), L("Mexico page", U["reb_mx"]),
        L("buy a subscription", U["reb_buy"]), L("plans vs bundles", U["reb_diff"]), L("deactivate and reactivate", U["reb_deact"]),
        L("MTU Q&A", U["reb_qa"]), L("payment failed", U["reb_fail"]), L("Cuba", U["reb_cuba"]), L("Wallet", U["reb_wallet"]),
        L("App Store", U["reb_as"]), L("Google Play", U["reb_play"]), L("Wikipedia", U["reb_wiki"]), L("Trustpilot", U["reb_trust"])]) + "."),
    ("p", "**Recharge.com, Miron, carriers, Cuba.** " + ", ".join([L("Recharge.com Telcel", U["rc_telcel"]), L("Recharge.com app", U["rc_as"]),
        L("Coda", U["rc_coda"]), L("MobileRecharge", U["mr_web"]), L("MobileRecharge app", U["mr_as"]), L("TopUp.com app", U["topup_as"]),
        L("KeepCalling app", U["kc_as"]), L("Digicel app", U["digicel_as"]), L("Digicel FAQ", U["digicel_faq"]),
        L("Telcel portal", U["telcel_portal"]), L("eTopUpOnline", U["etopup_blog"]), L("Natcom app", U["natcom_play"]),
        L("Natcom blog", U["natcom_blog"]), L("Elemt", U["elemt"]), L("Claro RD", U["claro_rd"]), L("Claro GT", U["claro_gt"]),
        L("Tigo Internacional", U["tigo_int"]), L("Cuballama", U["cuballama"]), L("Fonoma", U["fonoma"]), L("aCuba", U["acuba"]),
        L("Cubatel", U["cubatel_as"]), L("Ensip", U["ensip"]), L("Cubacel x6 promo", U["cubacel_x6"])]) + "."),
    ("p", "**Remittance and chat.** " + ", ".join([L("Félix recargas", U["felix"]), L("Félix guide", U["felix_guide"]),
        L("Félix raise", U["felix_raise"]), L("Félix growth", U["felix_growth"]), L("Remitly One", U["remitly_one"]),
        L("Remitly WhatsApp", U["remitly_wa"]), L("Western Union reload", U["wu_reload"]), L("MoneyGram top-ups", U["mg_topup"]),
        L("MoneyGram recurring FAQ", U["mg_recurring"]), L("Xoom", U["xoom"]), L("WorldRemit", U["wr"]),
        L("Taptap Send bills", U["taptap"]), L("Taptap Send WhatsApp", U["taptap_wa"]), L("BOSS Money FAQ", U["bm_faq"]),
        L("BR IMTU page", U["br_web"]), L("BR App Store", U["br_as"]), L("BOSS Money App Store", U["bm_as"])]) + "."),
    ("p", "**Market and regulation.** " + ", ".join([L("IDT FY26 results", U["idt_fy26"]), L("Banxico", U["banxico"]),
        L("Inter-American Dialogue", U["dialogue"]), L("America Movil 2Q26", U["amx"]), L("Millicom Q2 2026", U["millicom"]),
        L("CURP registration", U["curp"]), L("suspended lines", U["curp_susp"]), L("Recurly benchmarks", U["recurly"]),
        L("Recurly 2026", U["recurly26"]), L("Stripe Billing", U["stripe"]), L("Chargebee", U["chargebee"]),
        L("Visa tokens", U["visa_tokens"]), L("Visa subscription rules", U["visa_rules"]), L("ROSCA", U["rosca"]),
        L("California", U["ca_arl"]), L("Minnesota", U["mn_arl"]), L("Massachusetts", U["ma_arl"]), L("FTC ANPRM", U["ftc_anprm"]),
        L("FTC Amazon", U["ftc_amazon"]), L("8th Circuit vacatur", U["vacatur"]), L("NYC and Louisiana", U["nyc_la"]),
        L("ZwillGen", U["zwillgen"]), L("Reg E", U["rege"]), L("remittance tax proposed rules", U["tax4475"]),
        L("OFAC 515.542", U["ofac"]), L("Coda and Recharge", U["coda"]), L("WU Q2 2026", U["wu_q2"]),
        L("WU and Intermex", U["wu_intermex"]), L("WhatsApp India", U["wa_india"]), L("Visa agentic", U["visa_agent"]),
        L("Google AP2", U["ap2"]), L("GSMA eSIM", U["esim"]), L("DT One", U["dtone"])]) + "."),
    ("h2", "D. Method notes"),
    ("bullets", [
        "Web captures: headless Chrome at 390 x 844, device scale 3, iPhone user agent, English. Cookie banners were "
        "rejected through the site's own controls where possible, or hidden without consent.",
        "Store galleries: rendered from the public App Store pages; each screenshot cropped at its own size.",
        "Reviews: App Store RSS (up to 500 most recent and 500 most helpful per app), deduplicated, 894 keyword "
        "candidates read and coded by hand; a random recall check put the residual miss rate at about 0.7%.",
        "Rebtel prices come from its public product catalog queried by country and operator, never by phone number.",
        "IDT weekly subscriptions: Amplitude event MTUOrderStatusSuccessScr split by recurrent_unit, weeks starting Monday.",
    ]),
    ("h2", "E. Open questions"),
    ("bullets", [
        "Ding's live start-date flow, whether plans and bundles can recur today, and whether its pre-charge text is standard.",
        "Rebtel's default in the new checkout, and whether renewals retry before deactivation.",
        "Digicel's failed-payment handling, and whether MobileRecharge's 12-hour retries notify the sender.",
        "Whether BR's 2026 review complaints trace to the top-up subscription or to calling auto-recharge (billing data).",
        "Renewal success rate and involuntary churn at IDT (needs the measurement workstream).",
        "Whether a US sender without a Telcel line can use Telcel's programmed recharges.",
    ]),
    ("h2", "F. Glossary"),
    ("table", [
        ["Term", "Meaning"],
        ["IMTU", "International mobile top-up: airtime, data or bundles sent to a prepaid phone abroad"],
        ["Attach", "Share of top-up purchases that create a subscription"],
        ["Dunning", "Retrying and messaging after a failed recurring payment"],
        ["Presale (preventa)", "A top-up reserved now and delivered when a carrier promo starts"],
        ["CURP", "Mexico's population registry key, now required to keep a prepaid line active"],
        ["ROSCA / ARL", "Restore Online Shoppers' Confidence Act / state automatic renewal laws"],
        ["MIT", "Merchant-initiated transaction, the card-network flag for recurring charges"],
    ], {"widths": [22, 78], "font_pt": 8.2}),
]
