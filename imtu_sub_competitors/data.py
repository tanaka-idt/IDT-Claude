"""Single source of truth for the IMTU subscription competitor study (Sep 2026).

Every value here is taken from the research notes of 29 Sep 2026 (public competitor pages,
help centres, app stores, filings) and IDT's own Amplitude, Jira and internal analyses.
Figures and the Doc tables both read from this module so they cannot drift apart.

Capability codes: Y = yes / full, P = partial or limited, N = no, - = not applicable, ? = not verified.
"""

PLAYERS = [
    # key, label, short label
    ("idt", "IDT (Boss Revolution)", "IDT BR"),
    ("ding", "Ding", "Ding"),
    ("rebtel", "Rebtel", "Rebtel"),
    ("miron", "MobileRecharge / TopUp.com", "MobileRecharge"),
    ("recharge", "Recharge.com (Coda)", "Recharge.com"),
    ("digicel", "Digicel (carrier)", "Digicel"),
    ("elemt", "eTopUpOnline / Natcom (Elemt)", "eTopUp / Natcom"),
    ("cuballama", "Cuballama (Cuba)", "Cuballama"),
    ("felix", "Félix Pago (WhatsApp)", "Félix Pago"),
    ("remitly", "Remitly (One)", "Remitly"),
]

CAPABILITIES = [
    ("recurring", "Recurring top-up to a recipient"),
    ("cadence", "Sender chooses the cadence"),
    ("startdate", "Pick a start date, pay later"),
    ("optin", "Explicit opt-in (not pre-ticked)"),
    ("price", "Price advantage for subscribing"),
    ("membership", "Paid membership"),
    ("promo", "Promo-aware delivery (presale)"),
    ("reminder", "Reminder before each charge"),
    ("dunning", "Retries after a failed payment"),
    ("pause", "Skip or pause a cycle"),
    ("edit", "Edit after activation"),
    ("cancel", "Self-serve cancel, immediate"),
    ("save", "Exit survey or save offer"),
    ("wallets", "Apple Pay, Google Pay or PayPal on renewals"),
    ("loyalty", "Loyalty points or cashback"),
    ("whatsapp", "WhatsApp channel"),
]

MATRIX = {
    "idt":      dict(recurring="Y", cadence="Y", startdate="N", optin="N", price="P", membership="N", promo="N",
                     reminder="Y", dunning="N", pause="N", edit="P", cancel="Y", save="P", wallets="P", loyalty="P", whatsapp="N"),
    "ding":     dict(recurring="Y", cadence="Y", startdate="Y", optin="Y", price="N", membership="Y", promo="P",
                     reminder="P", dunning="N", pause="N", edit="N", cancel="Y", save="P", wallets="Y", loyalty="Y", whatsapp="N"),
    "rebtel":   dict(recurring="Y", cadence="Y", startdate="N", optin="P", price="Y", membership="N", promo="N",
                     reminder="N", dunning="N", pause="N", edit="P", cancel="Y", save="P", wallets="Y", loyalty="P", whatsapp="N"),
    "miron":    dict(recurring="Y", cadence="Y", startdate="N", optin="Y", price="N", membership="N", promo="N",
                     reminder="P", dunning="P", pause="N", edit="P", cancel="Y", save="?", wallets="?", loyalty="P", whatsapp="N"),
    "recharge": dict(recurring="N", cadence="-", startdate="-", optin="-", price="-", membership="N", promo="N",
                     reminder="P", dunning="-", pause="-", edit="-", cancel="-", save="-", wallets="P", loyalty="N", whatsapp="N"),
    "digicel":  dict(recurring="Y", cadence="Y", startdate="Y", optin="P", price="N", membership="N", promo="N",
                     reminder="P", dunning="?", pause="?", edit="?", cancel="Y", save="?", wallets="P", loyalty="P", whatsapp="N"),
    "elemt":    dict(recurring="Y", cadence="Y", startdate="Y", optin="?", price="N", membership="N", promo="N",
                     reminder="?", dunning="?", pause="?", edit="Y", cancel="P", save="?", wallets="P", loyalty="Y", whatsapp="N"),
    "cuballama": dict(recurring="P", cadence="N", startdate="N", optin="Y", price="P", membership="N", promo="Y",
                      reminder="P", dunning="-", pause="-", edit="-", cancel="-", save="-", wallets="?", loyalty="Y", whatsapp="N"),
    "felix":    dict(recurring="N", cadence="-", startdate="-", optin="-", price="-", membership="N", promo="N",
                     reminder="N", dunning="-", pause="-", edit="-", cancel="-", save="-", wallets="N", loyalty="P", whatsapp="Y"),
    "remitly":  dict(recurring="N", cadence="-", startdate="-", optin="-", price="-", membership="Y", promo="-",
                     reminder="-", dunning="-", pause="-", edit="-", cancel="-", save="-", wallets="P", loyalty="P", whatsapp="Y"),
}

# App Store (US) rating counts, iTunes lookup API, 29 Sep 2026; Google Play installs band where known.
APP_SCALE = [
    # label, iOS ratings, iOS stars, Play installs, is_idt
    ("Boss Revolution", 277506, 4.68, "10M+", True),
    ("Cuballama", 221809, 4.88, "n/a", False),
    ("Rebtel", 125428, 4.82, "10M+", False),
    ("Ding", 83831, 4.82, "5M+", False),
    ("BOSS Money", 83043, 4.86, "1M+", True),
    ("Cubatel", 74376, 4.88, "n/a", False),
    ("aCuba", 36347, 4.88, "n/a", False),
    ("Talk360", 20943, 4.68, "n/a", False),
    ("KeepCalling", 18972, 4.62, "1M+", False),
    ("Digicel International", 17725, 4.75, "n/a", False),
    ("MobileRecharge", 9578, 4.73, "1M+", False),
    ("Recharge.com", 2233, 4.72, "1M+", False),
]

# IDT cancellation curve (BR app, 272,026 subscription purchasers 1 Mar to 1 Aug 2026), right-censored floors.
IDT_CANCEL = [(1, 7.91), (3, 9.25), (7, 13.16), (14, 19.17), (30, 30.57)]
IDT_CANCEL_60D_DEFAULT_ON = 44.8     # default-ON A/B cohort 1 Jun to 4 Jul, fully observed
IDT_CANCEL_30D_BY_CADENCE = {"Weekly (7 and 14 days)": 49.36, "Monthly (30 and 90 days)": 23.96}

# Rebtel Plans vs closest same-operator one-time bundle (USD, public catalog 29 Sep 2026). Negative = Plan cheaper.
REBTEL_PLAN_DELTAS = [
    ("MX Telcel Amigo 200", -9.6), ("MX Telcel Amigo 500", -9.1), ("MX AT&T Combo Mediano", -8.0),
    ("MX Movistar Combo Mega", -9.8), ("MX Unefon", -3.4), ("MX Flash Mobile", -15.1),
    ("NG MTN 16.5GB", -47.4), ("NG MTN 36GB", -38.0), ("NG MTN Mini", 22.3), ("NG Airtel 35GB", -31.1), ("NG Glo 28GB", -21.8),
    ("IN Airtel Large", 6.8), ("IN Jio Medium", -8.2), ("IN Jio Large", 7.8), ("IN BSNL", -8.9),
    ("GT Tigo Superplan (weekly)", -9.1), ("GT Tigo Plan", -7.3), ("GT Claro Superplan (weekly)", 5.3), ("GT Claro Plan", -9.4),
    ("ET Ethio Mini", -15.4), ("ET Ethio Unlimited", -13.3),
    ("DO Viva small", -16.7), ("DO Viva medium", -14.9), ("DO Viva 60 days", -13.9),
]

# Share of 2026 US App Store reviews that mention subscriptions or auto-charges (hand-coded).
REVIEW_SHARE_2026 = [
    ("Rebtel", 7.4, 121), ("KeepCalling", 3.5, 57), ("Boss Revolution", 2.7, 513), ("Western Union", 0.4, 511),
    ("BOSS Money", 0.2, 511), ("Remitly", 0.0, 554), ("Taptap Send", 0.0, 616),
]
BR_REVIEW_MONTHS = [("Apr", 0, 95), ("May", 1, 97), ("Jun", 0, 86), ("Jul", 3, 82), ("Aug", 6, 84), ("Sep*", 2, 56)]
REVIEW_THEMES = [("Unexpected charge", 40), ("Enrolled by default or pushed in", 29), ("Positive: convenience, price", 29),
                 ("Cannot cancel", 25), ("Double charge", 5), ("Recurring top-up failed", 4)]
