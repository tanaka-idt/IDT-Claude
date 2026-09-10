#!/usr/bin/env python3
"""
Creates ONE Google Doc: "IMTU Amplitude Events Audit".

A review of how the Boss Revolution app (Amplitude project BR app Prod, 650506)
and the Boss Money app (Money app Prod, 420385) instrument International Mobile
Top-Up in Amplitude: what the event structure gets right, where the data is
wrong or silent, what is missing, and what to change so both apps can be
measured with one structure.

Sources: the live Amplitude taxonomy of both projects (pulled 9 Sep 2026), 19
ad hoc queries on the last 30 days saved to dashboard bm14j7e2, the BR6 MTU
Amplitude Events spreadsheet (all 17 tabs), and the 39 dashboards and 111
charts that reference IMTU. Every event name links to its Amplitude Data
catalog entry and every figure links to its saved chart.

A twin HTML version of this report is IMTU_Amplitude_Events_Audit.html.
"""

import re
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

TITLE = "IMTU Amplitude Events Audit"

AMP = "https://app.amplitude.com/analytics/BOSS"
DATA_BR = "https://app.amplitude.com/data/BOSS/650506/events/main/latest"
DATA_MONEY = "https://app.amplitude.com/data/BOSS/420385/events/main/latest"
DASH = f"{AMP}/dashboard/bm14j7e2"
SHEET = ("https://docs.google.com/spreadsheets/d/"
         "1zpnqglr0dC4tw_AC4FdxFM3UlAFSwJGZ-mGPhojaLrs/edit?gid=1401783006#gid=1401783006")

# Saved chart id -> (alias used in prose, saved name)
CHARTS = {
    "23zsjmnw": ("BR funnel chart", "[Audit] BR purchase funnel: home to success"),
    "79sjkgkk": ("Money funnel chart", "[Audit] Money app purchase funnel: contact list to success"),
    "8q2t6rrf": ("reconciliation chart", "[Audit] Order outcome reconciliation"),
    "nkveexl1": ("property fill chart", "[Audit] Success screen: (none) count per key property"),
    "bw7b6e3i": ("flag fill chart", "[Audit] Fill of is_subscription, default_subscription_toggle, is_br7_mtu_home"),
    "iur77opl": ("hosting app chart", "[Audit] hosting_app, platform and dead A/B properties"),
    "stkq29c4": ("recurrent_unit chart", "[Audit] Success screen by recurrent_unit (literal 'empty' string)"),
    "qe1xnoc3": ("top_up_started_from chart", "[Audit] Success screen by top_up_started_from"),
    "3icyttvz": ("offer_type chart", "[Audit] Success screen by offer_type"),
    "rmi5zkxe": ("failed_reason chart", "[Audit] Failed screen by failed_reason"),
    "fdvwj5mr": ("duplicate pairs chart", "[Audit] Duplicate and misspelled event pairs"),
    "6y6o7jei": ("renamed pairs chart", "[Audit] Renamed and legacy event pairs"),
    "hlh7j7tj": ("toggle chart", "[Audit] Toggle tap by default_state x new_state"),
    "csevgfiv": ("marketing transaction chart", "[Audit] MarketingTxnCompleted by product_category and payment_method"),
    "ts90xu02": ("Money legacy chart", "[Audit] Money app: MTU vs legacy IMTU events"),
    "od6wv5h1": ("Money fill chart", "[Audit] Money app: success screen property fill"),
}

DASHBOARDS = [
    ["Dashboard", "Owner", "Project", "Charts", "Views"],
    ["MTU User Behaviour", "Yuliana Turchyn", "650506", "13", "154"],
    ["[BR] Lifecycle: Cart Abandonment - IMTU", "Aron Souza", "650506", "22", "52"],
    ["MTU Subscription Toggle Dashboard", "Joao Tanaka", "650506", "30", "36"],
    ["MTU KPIs", "Yuliana Turchyn", "650506", "11", "30"],
    ["MA. MTU User Behavior", "Yuliana Turchyn", "420385", "13", "29"],
    ["MTU Dashboard", "Joao Tanaka, Yuliana Turchyn", "650506", "34", "21"],
    ["IMTU in MoneyApp", "Siarhei Samuseu, Vitaly Shidlovskiy", "420385", "66", "10"],
    ["IMTU Home Redesign: Effectiveness Review (Sep 2026)", "Joao Tanaka", "650506", "25", "0"],
    ["IMTU Subscription Journey - Full Evidence Pack (v2)", "Joao Tanaka", "650506", "46", "0"],
    ["[BOSS Money] Lifecycle: Cart Abandonment - IMTU", "Aron Souza", "420385", "17", "0"],
    ["IMTU Featured Offers - Performance and Bottlenecks", "Joao Tanaka", "650506", "2", "0"],
]
DASH_IDS = {
    "MTU User Behaviour": "k5w7eh02",
    "[BR] Lifecycle: Cart Abandonment - IMTU": "udapxwg7",
    "MTU Subscription Toggle Dashboard": "uwycvtev",
    "MTU KPIs": "z9dkzeuz",
    "MA. MTU User Behavior": "8m38qhfp",
    "MTU Dashboard": "al1l6dd0",
    "IMTU in MoneyApp": "ld594eo5",
    "IMTU Home Redesign: Effectiveness Review (Sep 2026)": "bwtn629z",
    "IMTU Subscription Journey - Full Evidence Pack (v2)": "o1jhxth9",
    "[BOSS Money] Lifecycle: Cart Abandonment - IMTU": "pkdkmadp",
    "IMTU Featured Offers - Performance and Bottlenecks": "z8wyviql",
}

# Proposed names that do not exist yet must not be linked to the catalog.
PROPOSED = {
    "MTUEntryTap", "MTUOrderStatusChanged", "MTUPurchase",
    "MTUSubscriptionRenewalAttempted", "MTUSubscriptionRenewalSucceeded",
    "MTUSubscriptionRenewalFailed", "MTUSubscriptionPaused",
    "MTUSubscriptionExpired", "MTUOfferFeaturedCardImpression", "MTUNoOffersScr",
    "MTUSearchResultsView", "MTUCarrierLookupFailed", "MTUSubscriptionPayTap",
    "MTUOrderStatusRefundedScr", "MTUOrderStatusScheduledScr", "MTUTermsScr",
    "MTUContactCustomerServiceTap", "MTUCarrierPromosScroll",
    "MTUCarrierPromoCountryFilterSwipeDown", "MTUCarrierPromoCountryFilterXBtn",
    "MTUHomeActivityEditSubscriptionTap", "MTUHomeActivityPastTransactionsCardTap",
    "MTUHomeActivitySeePastTransactionsTap", "MTUHomeActivitySendAgainTap",
    "MTUHomePromoCardTap", "MTUHomePromoCardView", "MTUHomePromoCardsSwipe",
    "MTUHomePromoCardsView", "MTUHomePromoSeeAllTap", "MTUHomePromoUsePromoTap",
    "MTUHomeRecipientAvatarTap", "MTUHomeXsellCardTap", "MTUHomeXsellCardsView",
    "MTUHomeXsellEgiftCardTap", "MTUHomeXsellEsimCardTap",
    "MTUOrderOfferDetailsCollapse", "MTUOrderOfferDetailsExpand",
    "MTUOrderSubscriptionUpsellDismissBtn", "MTUPromoListAvailabilityFilterSelect",
    "MTUPromoListCountryFilterSelect", "MTUPromoListPromoCardTap",
    "MTUPromoListScroll", "MTUPromoListView", "MTUSubscriptionDuplicateWarningCloseBtn",
    "MTUSubscriptionsStartTopUpBtn", "MTUTransactionsAllFilterTap",
    "MTUTransactionsContactAvatarTap", "MTUTransactionsListScroll",
    "MTUTransactionsListView", "MTUTransactionsPastTransactionTap",
    "MTUTransactionsQuickSendTap", "MTUTransactionsSubscriptionFilterTap",
    "MTUViewHomePromoCardDetailsTap", "MTUViewHomePromoSeeOffersTap", "MTUHome",
}
# Events that exist only in the Money project.
MONEY_ONLY = {"MTUOrderScrCloseBtn", "MTUEditSubscrScrCloseBtn", "SendIMTUBtn",
              "RequestIMTUBtn", "PostCallMtuBtn"}

# ---------------------------------------------------------------- tables ----

QUALITY = [
    ["#", "Defect", "Where", "Impact, last 30 days", "Chart"],
    ["Q1", "Literal string \"empty\" sent instead of null; the Money app also sends \"null\"",
     "recurrent_unit and top_up_started_from on all order events",
     "529,817 success events (74.9%) carry recurrent_unit = \"empty\"; 37,021 (5.2%) carry top_up_started_from = \"empty\"",
     "recurrent_unit chart; Money fill chart"],
    ["Q2", "Default toggle state missing on the order screen", "default_subscription_toggle on MTUOrderScr",
     "221,370 of 1,188,524 (18.6%) are none", "flag fill chart"],
    ["Q3", "Subscription flag missing on the complete tap", "is_subscription on MTUOrderCompleteBtn",
     "33,205 of 875,951 (3.8%) are none", "flag fill chart"],
    ["Q4", "Home variant flag missing", "is_br7_mtu_home on MTUHomeScr",
     "75,815 of 1,556,039 (4.9%) are none", "flag fill chart"],
    ["Q5", "Generic failure reason", "failed_reason on MTUOrderStatusFailedScr",
     "50,693 of 138,786 failures (36.5%) are just \"failed\"", "failed_reason chart"],
    ["Q6", "Orders with no terminal status event", "MTUOrderProcessingScr vs Success + Failed + Queued",
     "871,032 processing vs 857,330 terminal: 13,702 (1.6%) unaccounted; Scheduled and Refunded screens never instrumented",
     "reconciliation chart"],
    ["Q7", "Dead experiment properties still on events",
     "A_B_subscription_toggle_test_group, A_B_subscription_toggle_test_id, A_B_br7_homepage_test_id, featured_card_variant",
     "98.6% and 100% none; featured_card_variant none on 97% (removal in DCS-5331)", "hosting app chart"],
    ["Q8", "Typo event still firing beside its fix", "MTUOrderTotalPriceCollpase vs MTUOrderTotalPriceCollapse",
     "371 vs 21,548 events; the typo is still referenced in the DCS-5300 spec", "duplicate pairs chart"],
    ["Q9", "Two events for one action",
     "MTUHomePromotionsSeeAllTap / MTUHomePromoSeeAllPromotionsTap; MTUHomeActivitySeeAllTap / MTUHomeActivitySeeAllTransactionsTap",
     "46,516 + 5,237; 48,480 + 22,278", "duplicate pairs chart"],
    ["Q10", "Renames left dead events, and a new rename is splitting a series now",
     "MTUReceiptScr (0) vs MTUOrderStatusViewFullReceiptScr (49,792); MTUHomeSearchBtn (0) vs MTUHomeSearchBarBtn (272,549); MTUSubscriptionDuplicateWarningView (21,943) vs MTUSubscriptionDuplicateWarningModalView (3, first seen 8 Sep)",
     "Dead events stay in dropdowns; the duplicate-warning series will split as the new build ships", "renamed pairs chart"],
    ["Q11", "Legacy Money-app flow events leak into both projects",
     "IMTUOrderScr, IMTUReceiptScr, IMTUbuy_btn, IMTUProcessingResult, IMTUContactsScr",
     "BR: 185 and 118 events; Money: 8,966 IMTUOrderScr vs 323,595 MTUOrderScr (2.8%)", "Money legacy chart"],
    ["Q12", "Toggle taps cannot be netted per order", "default_state and new_state on MTUSubscriptionToggleTap",
     "on to off 248,257; off to off 30,651; off to on 27,374; on to on 10,829. Same-state pairs exist because default_state is the screen default, not the state before the tap; there is no previous_state",
     "toggle chart"],
    ["Q13", "Revenue chart built on a button tap", "MTU revenue daily sums total_amount on MTUOrderCompleteBtn",
     "Complete taps exceed successes by 168,374 (23.8%) in 30 days, so the chart overstates revenue by failed and retried orders",
     "reconciliation chart"],
    ["Q14", "Payment method values mix two taxonomies", "payment_method on MarketingTxnCompleted (the only MTU event that has it)",
     "debit 619,491; Customer Credit Card Purchase 458,328; Customer Transfer from Retailer 303,548; credit 60,350; prepaid 25,964; Hard Card Topup 5,605",
     "marketing transaction chart"],
]

APPS = [
    ["Dimension", "Boss Revolution (650506)", "Boss Money (420385)", "Read"],
    ["Purchases (success screen, 30 days)", "707,640", "205,939", "BR is 77% of app purchases, consistent with the 12-month split"],
    ["Subscription share of purchases", "25.1% (monthly 18.1%, weekly 7.0%)", "26.8% (monthly 17.5%, weekly 9.3%)", "Same behaviour; Money leans slightly weekly"],
    ["Product mix (offer_type)", "Top Up 49.4%, Bundle 44.9%, Data 5.7%", "Bundle 57.0%, Top Up 36.5%, Data 6.0%", "Money buyers skew to bundles"],
    ["Entry event", "MTUHomeScr (1.56M) then MTUTopupBtn", "No MTU home; MTUSendTopUpContactListScr (212,789) or MTUCarrierListScr (392,419); MTUHomeScr is blocked", "No common first step, so the funnels are not comparable"],
    ["Funnel to success (1 day, unique users)", "52.6% from home", "68.2% from contact list", "Money starts one step deeper; from the offer list both convert about 79 to 80%"],
    ["Where top-ups start", "search 29.0%, recents 27.6%, people page 17.5%, quick send 12.3%, calling home 4.2%", "recents 44.1%, search 38.1%, quick send 11.9%; no people page or calling surfaces", "Attribution works in both with the same vocabulary"],
    ["Promo surfaces as purchase source", "0.34% (promo cards 1,506, all promotions 408)", "0.28% (321 + 172 + 79)", "Millions of promo views, a few thousand purchases"],
    ["Legacy IMTU* events", "Trace (185 IMTUOrderScr)", "2.8% of orders still on the legacy flow (8,966)", "Old app versions or an unmigrated path in Money"],
    ["Literal null strings", "\"empty\"", "\"empty\" and \"null\"", "Two client implementations of the same bug"],
    ["Events only in this app", "MTUSubscriptionDuplicateWarningModalView, MTUSubscriptionDuplicateWarningContinueBtn, MTUBtn, MTUHistoryBtn, MTUPromosBtn, MTUReceiptEGiftBannerBtn", "MTUOrderScrCloseBtn, MTUEditSubscrScrCloseBtn", "Release drift between the two hosts"],
    ["Purchase property set", "31 properties on the success screen", "30 properties, same names", "Parity is good; both lack payment_method, subscription_id, is_subscription"],
    ["Analyst assets", "MTU Dashboard, MTU KPIs, MTU User Behaviour, cart abandonment, toggle and home reviews", "IMTU in MoneyApp (66 charts), MA. MTU User Behavior, Money cart abandonment", "Two parallel dashboard families; no cross-app view"],
]

PLAN = [
    ["Priority", "Change", "Role", "Why now", "Fixes"],
    ["P0", "Send null, not the string \"empty\" or \"null\", for absent recurrent_unit and top_up_started_from; both apps", "[APP]", "Every subscription-vs-regular split filters on a magic string", "Q1"],
    ["P0", "Populate default_subscription_toggle, is_subscription and is_br7_mtu_home on every fire; add previous_state to MTUSubscriptionToggleTap", "[APP]", "18.6% of order screens are unclassifiable in the toggle analysis", "Q2, Q3, Q4, Q12"],
    ["P0", "Add payment_method (closed list), card_on_file and is_first_card_use to MTUOrderCompleteBtn, MTUOrderProcessingScr and all MTUOrderStatus* events; extend DCS-5327 beyond wallets", "[APP] [BE]", "Payment method is the most requested cut that does not exist", "M1, Q14"],
    ["P0", "Pass the backend decline code as failed_reason_code and failed_stage on failed and retry events", "[BE] [APP]", "36.5% of failures are undiagnosable", "Q5, M7"],
    ["P0", "Server event MTUOrderStatusChanged with order_status and mtu_confirmation_number", "[BE]", "13,700 orders a month have no outcome in Amplitude", "Q6, M6"],
    ["P0", "Rebuild MTU revenue daily and any chart summing amounts on MTUOrderCompleteBtn onto MTUOrderStatusSuccessScr; long term, send a MTUPurchase revenue event", "[TPM] [BE]", "Reported revenue is inflated by 24% of taps that did not succeed", "Q13, M11"],
    ["P0", "Register all IMTU events and properties in the Amplitude tracking plan with description, category (IMTU), owner and value lists; block the typo and dead events; make the sheet a mirror, not the source", "[TPM]", "Zero documentation in the tool; 71% of events unused", "S1, S2, S5"],
    ["P1", "Subscription lifecycle server events (renewal attempted, succeeded, failed, paused, expired) with subscription_id, cycle_number, failure_reason; add subscription_id to every client subscription event", "[BE] [APP]", "Renewals, recurring revenue and the double-billing risk are invisible", "M2"],
    ["P1", "cancel_reason, cancel_source, subscription_age_days, cycles_completed on MTUEditSubscriptionCancelSuccess; build MTUSubscriptionPayTap as specified", "[APP] [DESIGN]", "Cancellation is the largest subscription behaviour and has no stated cause", "M3, M4"],
    ["P1", "Retire duplicates: stop MTUOrderTotalPriceCollpase, merge the two See-All pairs, block MTUReceiptScr, MTUHomeSearchBtn, MTUOfferSelect, MTUOfferFeaturedSelect; decide one name for the duplicate-warning modal before the 8 Sep build reaches volume", "[APP] [TPM]", "Parallel events split series and mislead dropdowns", "Q8, Q9, Q10"],
    ["P1", "Remove A_B_subscription_toggle_test_group, A_B_subscription_toggle_test_id, A_B_br7_homepage_test_id, featured_card_variant (DCS-5331), offer_Id, event_name, component_name", "[APP]", "Dead and duplicate properties cost ingestion and confuse group-bys", "Q7, S3"],
    ["P1", "Hash recipient_phone_number (salted) and drop phone_number, user_id, msisdn, raw_number, recipient_name from event properties", "[APP] [BE]", "Personal data on 180 event types", "S6"],
    ["P1", "One entry event MTUEntryTap with top_up_started_from in both apps; add MTUHomeScr or its equivalent to the Money app; ship module events to both hosts in the same release", "[APP]", "No cross-app funnel is possible today", "S4"],
    ["P2", "Offer list context: offer_count, position, has_promo_offers, featured card impression, MTUNoOffersScr", "[APP]", "Offer selection cannot be explained by what was shown", "M5"],
    ["P2", "Search and lookup events; transaction status on activity and details taps; screen exit events with time on screen", "[APP]", "Largest entry surface and largest home widget are half-instrumented", "M8, M9, M12"],
    ["P2", "Daily IMTU user properties (active subscriptions, last purchase, lifetime purchases, primary destination, card on file)", "[BE]", "Every cohort is rebuilt from raw events", "M10"],
    ["P2", "Naming standard: MTU prefix only, PascalCase events, Scr/Tap/View/Swipe/Result suffixes, snake_case properties, closed value lists in kebab-case; rename MtuProductLeftToCart; distinct prefix for Money Transfer identity screens", "[TPM]", "Three prefixes and a collision with Money Transfer", "S3"],
]

ADDITIONS = [
    ["Event", "Fires when", "Properties", "Source"],
    ["MTUEntryTap", "Any control that starts a top-up", "top_up_started_from, has_promo_badge, recipient_prefilled", "App, both hosts"],
    ["MTUOrderStatusChanged", "Backend order state changes after submission", "mtu_confirmation_number, order_status, status_reason_code, offer_id, total_amount, payment_method, is_subscription, subscription_id", "Server"],
    ["MTUPurchase (revenue event)", "Order confirmed successful", "$price, $quantity, $productId, $revenueType, recipient_country, recipient_carrier, offer_type, payment_method", "Server"],
    ["MTUSubscriptionRenewalAttempted / Succeeded / Failed", "Recurring timer fires", "subscription_id, cycle_number, attempt_number, failure_reason, recurrent_unit, recurrent_interval, offer_id, total_amount, payment_method", "Server"],
    ["MTUSubscriptionPaused / Expired", "Timer paused after failures or offer retired", "subscription_id, reason, cycles_completed", "Server"],
    ["MTUSubscriptionPayTap", "Pay tapped with the toggle visible", "toggle_enabled, is_subscription, duplicate_subscription_warning_shown, frequency", "App (spec exists)"],
    ["MTUOfferFeaturedCardImpression", "Featured card enters the viewport", "featured_offer_id, position, offer_count", "App"],
    ["MTUNoOffersScr", "Carrier or offer lookup returns nothing", "recipient_country, recipient_carrier, error_code", "App"],
    ["MTUSearchResultsView", "Search results rendered", "result_count, query_type", "App"],
    ["MTUCarrierLookupFailed", "Number could not be resolved to a carrier", "recipient_country, error_code", "App"],
    ["Back and Close buttons on offer list, carrier list, order and edit-subscription screens", "User leaves the screen", "time_on_screen_ms, screen context", "App, both hosts"],
]

EVIDENCE = [["Chart", "What it shows", "Project"]] + [
    [name, alias.replace(" chart", ""), "420385" if "Money" in name else "650506"]
    for cid, (alias, name) in CHARTS.items()
]

TOPQ = [
    ["Event", "All-time volume", "Queries"],
    ["MTUTopupBtn", "7,599,715", "3,154"],
    ["MTUOrderCompleteBtn", "5,477,856", "1,698"],
    ["MTUOrderScr", "7,192,025", "1,595"],
    ["MTUSubscriptionToggleTap", "1,284,652", "1,061"],
    ["MTUEditSubscriptionCancelSuccess", "437,164", "449"],
    ["MTUOrderSubscriptionUpsellSaveCompleteOrderBtn", "623,887", "343"],
    ["MTUHomeScr", "9,242,026", "217"],
    ["MTUEditSubscriptionCancelBtn", "470,693", "194"],
    ["MTUSubscriptionDuplicateWarningView", "67,954", "179"],
    ["MTUOrderSubscriptionUpsellScr", "1,044,364", "165"],
]

NEVERQ = [
    ["Event", "All-time volume", "Queries"],
    ["MTUHomeActivityModuleView", "7,377,676", "0"],
    ["MTUPromoCardsView", "6,088,195", "0"],
    ["MTUHomeSubscriptionsSectionView", "5,303,525", "0"],
    ["MTUTxnDetailsScr", "4,293,708", "0"],
    ["MTUSendTopUpContactListScr", "3,028,414", "0"],
    ["MTUOfferListScrScroll", "2,057,172", "0"],
    ["MTUOfferUpsellNoBtn", "1,294,146", "0"],
    ["MTUHomeActivityTransactionCardsSwipe", "1,121,058", "0"],
    ["MTUHomeTooltipStepView", "1,013,798", "0"],
    ["MTUTxnDetailsSendAgainBtn", "1,008,066", "0"],
]

TABLES = [("QUALITY", QUALITY), ("APPS", APPS), ("PLAN", PLAN),
          ("ADDITIONS", ADDITIONS), ("EVIDENCE", EVIDENCE), ("TOPQ", TOPQ),
          ("NEVERQ", NEVERQ), ("DASHBOARDS", DASHBOARDS)]

SPEC_MISSING = [
    "MTUCarrierPromoCountryFilterSwipeDown [DCS-1426] dropped",
    "MTUCarrierPromoCountryFilterXBtn [DCS-1426] dropped",
    "MTUCarrierPromosScroll [DCS-1767, Events]",
    "MTUContactCustomerServiceTap [Events]",
    "MTUEditSubscrScrCloseBtn [BR7] Money only",
    "MTUHomeActivityEditSubscriptionTap [Events]",
    "MTUHomeActivityPastTransactionsCardTap [Events] shipped as MTUHomeActivityPastTransactionCardTap",
    "MTUHomeActivitySeePastTransactionsTap [Events]",
    "MTUHomeActivitySendAgainTap [Events] shipped as MTUHomeActivitySendAgainBtn",
    "MTUHomePromoCardTap [BR7] shipped as MTUPromoCardTap",
    "MTUHomePromoCardView [Events]",
    "MTUHomePromoCardsSwipe [BR7, Events] shipped as MTUPromoCardsSwipe",
    "MTUHomePromoCardsView [BR7] shipped as MTUPromoCardsView",
    "MTUHomePromoSeeAllTap [Events]",
    "MTUHomePromoUsePromoTap [Events]",
    "MTUHomeRecipientAvatarTap [BR7]",
    "MTUHomeXsellCardTap [BR7]",
    "MTUHomeXsellCardsView [BR7, Events]",
    "MTUHomeXsellEgiftCardTap [Events]",
    "MTUHomeXsellEsimCardTap [Events]",
    "MTUOrderOfferDetailsCollapse [Events] shipped as MTUOfferDetailsCollapseBtn",
    "MTUOrderOfferDetailsExpand [Events] shipped as MTUOfferDetailsExpandBtn",
    "MTUOrderScrCloseBtn [BR7] Money only",
    "MTUOrderStatusRefundedScr [DCS-1265, Events, Update to existing events]",
    "MTUOrderStatusScheduledScr [Events]",
    "MTUOrderSubscriptionUpsellDismissBtn [DCS-1265, Events, Update to existing events] replaced by MTUOrderSubscriptionUpsellCloseBtn and MTUOrderSubscriptionUpsellSwipeDown",
    "MTUPromoListAvailabilityFilterSelect [Events]",
    "MTUPromoListCountryFilterSelect [Events]",
    "MTUPromoListPromoCardTap [Events]",
    "MTUPromoListScroll [Events]",
    "MTUPromoListView [Events]",
    "MTUSubscriptionDuplicateWarningCloseBtn [BR7]",
    "MTUSubscriptionPayTap [Events]",
    "MTUSubscriptionsStartTopUpBtn [Events]",
    "MTUTermsScr [Events]",
    "MTUTransactionsAllFilterTap [Events]",
    "MTUTransactionsContactAvatarTap [Events]",
    "MTUTransactionsListScroll [Events]",
    "MTUTransactionsListView [Events]",
    "MTUTransactionsPastTransactionTap [Events]",
    "MTUTransactionsQuickSendTap [Events]",
    "MTUTransactionsSubscriptionFilterTap [Events]",
    "MTUViewHomePromoCardDetailsTap [BR7, Events] shipped as MTUViewPromoCardDetailsTap",
    "MTUViewHomePromoSeeOffersTap [Events]",
    "MTUHome [BR7] section label, not an event",
]

LIVE_UNSPEC = [
    "IMTU/HistoryList", "IMTUCarriersListShown", "IMTUCarriersProductsFetchingFailure",
    "IMTUContactsScr", "IMTUGetProductsSuccess", "IMTUNoCarriers", "IMTUOrderScr",
    "IMTUProcessingResult", "IMTUProcessingShown", "IMTUProductsListShown",
    "IMTUProductsScr", "IMTUReceiptScr", "IMTUadd_card_popup_shown", "IMTUbuy_btn",
    "IMTUcarrier_selected", "IMTUcontact_selected", "IMTUcvv_popup_shown",
    "IMTUproduct_selected", "MTUBtn", "MTUDeeplinkOpened", "MTUFilterBundle",
    "MTUFilterData", "MTUFilterTopup", "MTUHistoryBtn",
    "MTUHomeActivityChangeOfferRetryBtn", "MTUHomeActivityChangePaymentMethodRetryBtn",
    "MTUHomeActivityChangePhoneNumberRetryBtn", "MTUOrderStatusViewFullReceiptScr",
    "MTUOrderTotalPriceCollapse", "MTUPromoCardTap", "MTUPromoCardsSwipe",
    "MTUPromoCardsView", "MTUPromosBtn", "MTUTopupBtn",
    "MTUTxnDetailsChangeOfferRetryBtn", "MTUTxnDetailsChangePhoneNumberRetryBtn",
    "MTUTxnDetailsRetryLaterBtn", "MTUTxnDetailsRetryNowBtn",
    "MTUViewPromoCardDetailsTap",
    "MTUserDOBExitBtn (Money Transfer, prefix collision)",
    "MTUserDOBScr (Money Transfer, prefix collision)", "MtuProductLeftToCart",
]

# ---------------------------------------------------------------- blocks ----

BLOCKS = [
    ("h1", TITLE),
    ("p", "How the Boss Revolution and Boss Money apps instrument International Mobile "
          "Top-Up (IMTU) in Amplitude today, where the data is wrong or silent, and "
          "what to change so both apps can be measured with one structure. Reviewed "
          "9 September 2026. Amplitude org BOSS: BR app Prod (650506) and Money app "
          "Prod (420385). Figures are event totals over the last 30 days (10 August to "
          "9 September 2026) unless the text says users. Every figure links to a saved "
          "chart on the audit dashboard; every event name links to its entry in the "
          "Amplitude Data catalog. The spec of record is the BR6 MTU Amplitude Events "
          "sheet. A twin HTML version of this report exists with the same content."),

    ("h2", "1. Summary"),
    ("p", "The IMTU instrumentation is broad and, at the purchase step, unusually "
          "complete: the success screen carries offer, recipient, price, promotion and "
          "source-of-entry context on 100% of events. What it lacks is governance and a "
          "few load-bearing fields. Nothing is documented in Amplitude, 71% of events "
          "have never been queried, the spec sheet and the live taxonomy have drifted "
          "apart in both directions, and the questions the business asks most often "
          "(payment method, why subscriptions are cancelled, whether a renewal "
          "succeeded, revenue) cannot be answered from the current events."),
    ("b", "Headline numbers: 179 IMTU events live in the BR app, none with a description, "
          "category or owner in Amplitude; 114 of 160 events with usage statistics (71%) "
          "have never been queried; 45 events in the sheet never fired and 42 live events "
          "are not in the sheet; the purchase funnel is 52.6% in Boss Revolution and 68.2% "
          "in Boss Money, but the two apps have no common entry event so the figures are "
          "not comparable."),
    ("b", "Six P0 fixes: they corrupt numbers people already report. A literal \"empty\" "
          "string instead of null on recurrent_unit and top_up_started_from; "
          "default_subscription_toggle missing on 18.6% of order screens; the generic "
          "\"failed\" reason on 36.5% of failures; 13,700 orders a month (1.6%) that reach "
          "the processing screen and never reach a terminal status event; the daily "
          "revenue chart summing a button tap instead of the success screen; and no "
          "payment_method on any MTU event."),
    ("b", "Subscriptions are the biggest blind spot: cancellation has no reason and no "
          "tenure, renewals (the backend charge) do not exist in Amplitude at all, there "
          "is no subscription_id, and the pay-time toggle event MTUSubscriptionPayTap "
          "specified in March was never built. The double-billing case from the September "
          "duplicate-subscription analysis could not have been seen in Amplitude."),
    ("b", "Both apps share one event set (same names, same properties, hosting_app tells "
          "them apart), which is the right design. But the Money app has no MTU home "
          "event, still emits legacy IMTU events on about 3% of orders, and each app has "
          "entry-point events the other lacks, so a cross-app funnel has no first step."),
    ("b", "Naming has decayed: a typo event (MTUOrderTotalPriceCollpase) still fires beside "
          "its fix, five renamed pairs run in parallel or left dead events behind, offer_Id "
          "duplicates offer_id, one event is camelCase (MtuProductLeftToCart) with "
          "camelCase properties, and the MTU prefix collides with Money Transfer's "
          "MTUser screens."),
    ("b", "Privacy: recipient phone numbers, the sender's phone number and user id ride on "
          "every IMTU event as plain event properties, and MtuProductLeftToCart adds "
          "recipient name and four phone formats."),
    ("b", "Recommended path: register the IMTU set in the Amplitude tracking plan with "
          "owners and descriptions, fix the data-quality defects in one app release, add "
          "the subscription lifecycle events server-side, then retire duplicates. Detail "
          "and ticket-ready scope in section 8."),

    ("h2", "2. Scope and method"),
    ("p", "Only IMTU (event prefix MTU) was reviewed, across both apps that host the "
          "shared IMTU module."),
    ("b", "Amplitude taxonomy: every event and event property in BR app Prod (1,519 event "
          "types) and Money app Prod (1,439 event types), pulled on 9 September 2026 with "
          "status, first and last seen, description and category."),
    ("b", "Live data: 19 ad hoc queries on the last 30 days, saved as permanent charts on "
          "the audit dashboard. Every figure below links to its chart."),
    ("b", "The spec: all 17 tabs of the BR6 MTU Amplitude Events sheet (Events, BR7 IMTU "
          "HomePage, Carrier promotion flow, Update to existing events, Order processing, "
          "Punch cards, Apple/Google Pay and the DCS ticket tabs), parsed for event names "
          "and property definitions and diffed against the live taxonomy."),
    ("b", "Existing analytics: the 39 dashboards and 111 saved charts that reference IMTU, "
          "to see which events analysts rely on and how key charts are defined."),
    ("p", "\"None\" means the property is absent from the event. \"empty\" in quotes means "
          "the app sent that literal string."),

    ("h2", "3. What the current structure gets right"),
    ("h3", "The purchase record is rich and fully populated"),
    ("p", "On MTUOrderStatusSuccessScr (707,640 events in 30 days) the properties offer_id, "
          "recipient_country, recipient_carrier, mtu_confirmation_number, offer_amount, "
          "fee_amount, total_amount, featured_offer and offer_type are present on 100% of "
          "events (property fill chart, offer_type chart). That is enough to segment "
          "revenue proxies by destination, carrier, product type and promotion without a "
          "backend join."),
    ("h3", "Source attribution exists and is 95% populated"),
    ("p", "top_up_started_from is an event property carried from the entry point through to "
          "the success screen. It resolves 94.8% of purchases to one of 20 entry surfaces: "
          "search 29.0%, recent people list 27.6%, people page 17.5%, quick send 12.3% "
          "(top_up_started_from chart). The earlier belief that it only existed as an "
          "always-empty user property is wrong; the event property works and should be "
          "the standard attribution field."),
    ("h3", "One event set serves both apps"),
    ("p", "The IMTU module emits the same MTU events with the same property set in both "
          "projects, and hosting_app is 100% calling-app in the BR project and 99.99% "
          "money-app in the Money project (hosting app chart). Any chart built in one "
          "project can be rebuilt in the other by changing the project."),
    ("h3", "Failure and marketing events reconcile"),
    ("p", "MTUOrderStatusFailedScr (138,786) and MarketingTxnFailed filtered to MTU "
          "(138,485) agree within 0.2% (marketing transaction chart), so the two "
          "pipelines see the same failures."),

    ("h2", "4. Structure and governance findings"),
    ("h3", "S1. Nothing is registered in the tracking plan"),
    ("p", "All 179 IMTU events in the BR project have status \"unexpected\" (182 including "
          "two blocked), meaning none was ever added to the Amplitude tracking plan. Zero "
          "events and zero of the 2,090 event properties carry a description, category, "
          "owner or expected value list. In the Money project 169 of 191 are unexpected and "
          "only 6 are marked live. The spreadsheet is the only documentation, and it lives "
          "outside the tool analysts use."),
    ("h3", "S2. The spec sheet and the live taxonomy have drifted apart"),
    ("p", "Of 182 event names in the sheet, 45 have never fired in the BR project (Appendix "
          "B). Some were consciously dropped (the DCS-1426 filter dismiss events), but most "
          "are gaps: the whole List of Promos page and List of Transactions page blocks, "
          "the customer-service tap, MTUSubscriptionPayTap, MTUOrderStatusRefundedScr, "
          "MTUOrderStatusScheduledScr, MTUTermsScr. In the other direction, 42 live events "
          "are not in the sheet (Appendix C), including the busiest entry event in the "
          "product, MTUTopupBtn (7.6 million all-time events, the most-queried IMTU event), "
          "the July 2026 retry events, the promo card events and the MTUFilter events."),
    ("p", "Property values also diverge from the sheet: the sheet writes \"recents people "
          "list\" and \"mobile top up\", the app sends \"recents-people-list\" and \"Mobile "
          "Top Up\". Anyone building a filter from the sheet gets an empty chart."),
    ("h3", "S3. Naming has three prefixes, two suffix conventions and one collision"),
    ("b", "Prefixes: MTU (current), IMTU (legacy Money app flow, still firing in both "
          "projects), Mtu (MtuProductLeftToCart, a Braze cart-abandonment event whose "
          "properties are camelCase: carrierCode, productCode, txId)."),
    ("b", "Collision: the MTU prefix matches Money Transfer's MTUser and MTUpi screens "
          "(MTUserDOBScr, MTUserHomeAddressScr, MTUpiEnterKeyScr). Any \"starts with MTU\" "
          "filter, cohort or search picks up Money Transfer identity screens as top-up "
          "events. Five such events exist in BR, eight in Money."),
    ("b", "Suffixes: BR6 events end in Btn, Scr or Select; BR7 home events end in Tap, View "
          "or Swipe. The same See All action is MTUHomePromotionsSeeAllTap in one place and "
          "MTUHomePromoSeeAllPromotionsTap in another. MTUFilterBundle, MTUFilterData, "
          "MTUFilterTopup and MTUDeeplinkOpened have no action suffix at all."),
    ("b", "Property case: offer_Id exists beside offer_id on the order, success and failed "
          "events. Money app entry buttons exist as both PostCallMTUBtn and PostCallMtuBtn."),
    ("b", "Redundant meta: every IMTU event carries event_name and component_name, which "
          "repeat the event type."),
    ("h3", "S4. Entry points are not standardised"),
    ("p", "Eleven different events start a top-up depending on where the user is: "
          "MTUTopupBtn, MTUBtn, TopUpBtn, MTUHomeStartTopUpBtn, FundsServicesMTUBtn, "
          "HomeOnboardingActivityMTUBtn, PostCallMTUBtn, ContactMTUOfferBtn, "
          "ContactMTUCarrierBtn, RAFMtuCrossSellGiveNowBtn in BR, plus SendIMTUBtn and "
          "RequestIMTUBtn in Money. The top_up_started_from property already names the "
          "surface, so the entry event should be one event with that property, not eleven."),
    ("h3", "S5. Analysts use 29% of the events"),
    ("p", "Of 160 IMTU events with usage statistics, 114 have never appeared in a saved "
          "chart or query. Screens that fire millions of times (MTUHomeActivityModuleView "
          "7.4M, MTUPromoCardsView 6.1M, MTUHomeSubscriptionsSectionView 5.3M, "
          "MTUTxnDetailsScr 4.3M, MTUSendTopUpContactListScr 3.0M) have zero usage. Either "
          "they answer no question, in which case they cost ingestion for nothing, or "
          "nobody knows they exist, which points back to S1. Appendix D lists the most and "
          "least used events."),
    ("h3", "S6. Personal data rides on every event"),
    ("p", "recipient_phone_number (a full E.164 number), phone_number (the sender) and "
          "user_id are event properties on every IMTU event in both projects. "
          "MtuProductLeftToCart adds msisdn, raw_number, national_formatted, "
          "international_formatted and recipient_name. A recipient identifier is "
          "legitimately needed for duplicate-subscription and velocity analysis, but it "
          "should be a salted hash, and the sender fields belong in the user profile, not "
          "on 180 event types."),

    ("h2", "5. Data quality findings"),
    ("p", "Each row states the defect, the measured impact over the last 30 days in the BR "
          "project, and the chart that shows it."),
    ("table", "QUALITY"),
    ("cap", "Table 1. Data quality defects, BR app Prod, 10 August to 9 September 2026."),
    ("p", "The failure reasons deserve a closer look. Of 138,786 failures, 50,693 (36.5%) "
          "are the generic \"failed\", 36,166 (26.1%) failedNoCredit, 16,191 (11.7%) "
          "offerTemporaryUnavailable, 9,021 carrierProblemContactCarrier, 5,901 "
          "invalidMsisdnOrWrongCarrier, and the six card-related values together 17,517 "
          "(12.6%). The backend knows the K2 decline code; passing it through as "
          "failed_reason_code would make a third of failures diagnosable (failed_reason "
          "chart)."),

    ("h2", "6. Missing events and properties"),
    ("p", "These are questions the product team asks that the current events cannot "
          "answer, ordered by how often the question comes up."),
    ("h3", "M1. Payment method on the order"),
    ("p", "No MTU event carries payment_method. It exists only on MarketingTxnCompleted, a "
          "cross-channel marketing event whose values mix card type with transaction type "
          "(Q14). DCS-5327 adds the property for Apple Pay and Google Pay only. It should "
          "be added for every method with one closed value list: credit_card, debit_card, "
          "prepaid_card, apple_pay, google_pay, boss_share, promo_balance, plus "
          "card_on_file (true/false) and is_first_card_use."),
    ("h3", "M2. The subscription lifecycle after the first purchase"),
    ("p", "Amplitude sees the subscription being created (recurrent_unit on the success "
          "screen), edited and cancelled, and nothing else. There is no subscription_id on "
          "any event, so a cancellation cannot be joined to the purchase that created it. "
          "There are no renewal events: the recurring charge is a backend timer, and its "
          "success, failure and retry never reach Amplitude. The September "
          "duplicate-subscription analysis found 3,469 concurrently active timers "
          "double-billing 1,094 customers; none of that is visible here. Needed, sent "
          "server-side with the user id: MTUSubscriptionRenewalAttempted, "
          "MTUSubscriptionRenewalSucceeded, MTUSubscriptionRenewalFailed (with "
          "failure_reason and attempt_number), MTUSubscriptionPaused, "
          "MTUSubscriptionExpired, each carrying subscription_id, cycle_number, "
          "recurrent_unit, recurrent_interval, offer_id and total_amount."),
    ("h3", "M3. Why people cancel"),
    ("p", "MTUEditSubscriptionCancelSuccess carries offer, recipient and recurrence but no "
          "cancel_reason, no subscription_age_days, no cycles_completed and no "
          "cancel_source (home widget, transaction details, activity tab). The home "
          "redesign review found that 55% of users who tap the subscription card cancel "
          "within the hour; the review had to infer intent from sequence because no "
          "property states it."),
    ("h3", "M4. Final toggle state at payment"),
    ("p", "MTUSubscriptionPayTap with toggle_enabled, is_subscription and "
          "duplicate_subscription_warning_shown was specified in March 2026 and never "
          "built. The team uses is_subscription on the complete tap instead, which is "
          "missing 3.8% of the time (Q3). The toggle-tap event also needs previous_state "
          "(Q12) so opt-out can be netted per order without sequencing."),
    ("h3", "M5. Offer list context"),
    ("p", "MTUOfferListScr records that the list opened and whether a featured card was "
          "rendered, but not how many offers were shown, whether the list was empty, which "
          "offer position the user tapped, or whether the featured card entered the "
          "viewport. Add offer_count, featured_offer_id, has_promo_offers, price_min and "
          "price_max to the screen, position to MTUOfferSelectBtn, and a "
          "MTUOfferFeaturedCardImpression event. An empty-result state (MTUNoOffersScr) "
          "does not exist; the legacy IMTUNoCarriers and IMTUNoProducts covered this in "
          "the old flow and were never carried over."),
    ("h3", "M6. Backend outcomes beyond success and failure"),
    ("p", "Orders that are scheduled, refunded, reversed or time out have no screen event "
          "(Q6). Rather than four more screens, add one MTUOrderStatusChanged server event "
          "with order_status (success, failed, queued, scheduled, refunded, reversed, "
          "timeout), status_reason_code and mtu_confirmation_number so it joins to the "
          "client screens."),
    ("h3", "M7. Failure diagnostics"),
    ("p", "failed_reason is a UI copy key, not the backend code (Q5). Add failed_reason_code "
          "(the K2 or payment gateway code) and failed_stage (payment, carrier, validation, "
          "fraud) to MTUOrderStatusFailedScr and MarketingTxnFailed. The retry events added "
          "in July 2026 (MTUTxnDetailsRetryNowBtn, "
          "MTUHomeActivityChangePaymentMethodRetryBtn and siblings) should carry the same "
          "code so retry success can be measured by cause."),
    ("h3", "M8. Search and lookup"),
    ("p", "Search is the largest entry surface (29% of purchases) and the only events are "
          "the bar tap and the start-top-up taps. Nothing records a query with no result, "
          "a number the carrier lookup could not resolve, or a lookup error. Add "
          "MTUSearchResultsView (result_count, query_type) and MTUCarrierLookupFailed "
          "(error_code, recipient_country)."),
    ("h3", "M9. Activity and transaction context"),
    ("p", "MTUHomeActivityPastTransactionCardTap carries only transaction_id. Without "
          "transaction_status, recipient_country, recipient_carrier and is_subscription on "
          "the tap, the leak between the card and the order screen (28.8% in the home "
          "review) cannot be explained. The same applies to MTUTxnDetailsScr, which has no "
          "status property although failed transactions are exactly where retry actions "
          "live."),
    ("h3", "M10. User-level IMTU state"),
    ("p", "The only IMTU user properties are Is IMTU sender (Yes/No from the customer data "
          "platform), imtu_cls_label and imtu_retention_prob. Cohorts such as has an "
          "active subscription, last top-up more than 60 days ago or sends to two or more "
          "countries have to be rebuilt from raw events every time. Add "
          "imtu_active_subscriptions, imtu_last_purchase_date, imtu_lifetime_purchases, "
          "imtu_primary_destination and imtu_card_on_file, refreshed daily."),
    ("h3", "M11. Revenue as a revenue event"),
    ("p", "Amplitude's revenue features (LTV, the built-in paying property, revenue by "
          "cohort) need a revenue event with $revenue or $price. IMTU has none; revenue is "
          "approximated by summing total_amount on a screen or, worse, a button (Q13). "
          "Send a MTUPurchase revenue event from the success path with $price = "
          "total_amount, $quantity = 1, $productId = offer_id and $revenueType = one_time, "
          "subscription_first or subscription_renewal."),
    ("h3", "M12. Screen exits and abandonment"),
    ("p", "Until September 2026 no IMTU screen had an exit event; MTUOrderScrBackBtn "
          "appeared on 2 September (19 events) and MTUOrderScrCloseBtn exists only in the "
          "Money project. Abandonment is currently measured by absence in a funnel, which "
          "cannot separate left from lost the session. Add back and close events to the "
          "offer list, carrier list and edit-subscription screens with time_on_screen_ms, "
          "in both apps."),

    ("h2", "7. Boss Revolution vs Boss Money"),
    ("p", "The two apps embed the same IMTU module and emit the same events, so the "
          "comparison is mostly about what surrounds the module (BR funnel chart, Money "
          "funnel chart, Money legacy chart, Money fill chart)."),
    ("table", "APPS"),
    ("cap", "Table 2. IMTU in the two host apps, last 30 days."),
    ("p", "To measure both apps as one product: (1) give the Money app the same MTUHomeScr "
          "or, better, a single MTUEntryTap in both apps with top_up_started_from; (2) "
          "build IMTU dashboards once in either project with a hosting_app breakdown, or "
          "create a cross-project portfolio view; (3) retire the legacy IMTU flow in Money "
          "and the lower-case Imtu variants that appeared in 2024; (4) ship module "
          "analytics changes to both hosts in the same release so the only-in-this-app "
          "row stays empty."),

    ("h2", "8. Recommendations"),
    ("p", "Ordered by the damage done to numbers people already use. Roles follow the DCS "
          "Jira convention. Each P0 item is small enough for one story."),
    ("table", "PLAN"),
    ("cap", "Table 3. Prioritised changes. Q = data quality finding, M = missing item, S = structure finding."),
    ("h3", "Proposed additions, ready for a spec tab"),
    ("table", "ADDITIONS"),
    ("cap", "Table 4. New events and their properties."),
    ("p", "Sequencing: the P0 client changes are one story per host app and should ship "
          "together so the Boss Revolution and Boss Money series change on the same day. "
          "The tracking-plan registration can start now with no code. The server events "
          "depend on the k2 timer and order services and are the only items that need a "
          "backend epic."),

    ("h2", "Appendix A. Evidence charts"),
    ("p", "All on the audit dashboard, last 30 days, run on 9 September 2026."),
    ("table", "EVIDENCE"),

    ("h2", "Appendix B. Specified in the sheet, never fired in the BR project (45)"),
    ("p", "Tab in brackets. Items marked dropped were explicitly deferred in the sheet."),
] + [("b", s) for s in SPEC_MISSING] + [

    ("h2", "Appendix C. Live in the BR project, not in the sheet (42)"),
] + [("b", s) for s in LIVE_UNSPEC] + [

    ("h2", "Appendix D. Event inventory and usage"),
    ("p", "BR app Prod has 1,519 event types, 184 matching the MTU or IMTU prefix (179 IMTU "
          "after removing the five Money Transfer collisions), 182 with status unexpected, "
          "2 blocked, 10 not seen in 30 days. Money app Prod has 1,439 event types, 191 "
          "matching the prefix (183 IMTU), 169 unexpected, 16 blocked, 6 live, 32 not seen "
          "in 30 days. 160 events have usage statistics; 114 have zero queries."),
    ("h3", "Most queried IMTU events (all-time query count, BR project)"),
    ("table", "TOPQ"),
    ("h3", "Highest-volume IMTU events never queried"),
    ("table", "NEVERQ"),

    ("h2", "Appendix E. Existing IMTU dashboards"),
    ("p", "39 dashboards and 111 charts reference IMTU. The ones below are the actively "
          "used or recently built families; the audit dashboard should be merged into one "
          "of them once the fixes ship."),
    ("table", "DASHBOARDS"),
    ("p", "Related Jira: DCS-5327 (Apple/Google Pay property), DCS-5331 "
          "(featured_card_variant removal), DCS-5300 (toggle V2 properties), DCS-1647 "
          "(marketing transaction events), DCS-1265 and DCS-1182 (order properties and "
          "source attribution)."),
]

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}

# ---------------------------------------------------------------- links -----

EVENT_RE = re.compile(r"\b(I?MTU[A-Za-z0-9_/]{3,}|MtuProductLeftToCart|"
                      r"MarketingTxnCompleted|MarketingTxnFailed|TopUpBtn|"
                      r"FundsServicesMTUBtn|HomeOnboardingActivityMTUBtn|"
                      r"PostCallMTUBtn|ContactMTUOfferBtn|ContactMTUCarrierBtn|"
                      r"RAFMtuCrossSellGiveNowBtn|SendIMTUBtn|RequestIMTUBtn|"
                      r"PostCallMtuBtn)\b")


def build_doc_links():
    links = dict(LINK_MAP)
    links.update({
        "audit dashboard": DASH,
        "IMTU Amplitude Events Audit (Sep 2026)": DASH,
        "BR6 MTU Amplitude Events sheet": SHEET,
        "BR6 MTU Amplitude Events spreadsheet": SHEET,
        "BR app Prod (650506)": DATA_BR,
        "Money app Prod (420385)": DATA_MONEY,
        "MTU revenue daily": f"{AMP}/chart/tmn7ym6m",
    })
    for cid, (alias, name) in CHARTS.items():
        links[alias] = f"{AMP}/chart/{cid}"
        links[name] = f"{AMP}/chart/{cid}"
    for name, did in DASH_IDS.items():
        links[name] = f"{AMP}/dashboard/{did}"

    corpus = []
    for kind, text in BLOCKS:
        corpus.append(text)
    for _, table in TABLES:
        for row in table:
            corpus.extend(row)
    for m in EVENT_RE.finditer("\n".join(corpus)):
        ev = m.group(1)
        if ev in PROPOSED or ev in links:
            continue
        base = DATA_MONEY if ev in MONEY_ONLY else DATA_BR
        links[ev] = f"{base}/{ev}"
    return links


# ---------------------------------------------------------------- docs api --

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
        if kind == "b" and ": " in text and len(text.split(": ")[0]) < 60:
            lead = len(text.split(": ")[0]) + 1
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + lead},
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
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": start, "endIndex": start + len(txt)},
            "textStyle": {"fontSize": {"magnitude": 9, "unit": "PT"},
                          "bold": r == 0 or c == 0},
            "fields": "fontSize,bold"}})
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

    links = build_doc_links()
    print(f"Link map has {len(links)} phrases")
    linkify(docs, doc_id, links)

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
