#!/usr/bin/env python3
"""
Creates ONE Google Doc: "Felix Pago WhatsApp Top-Up — Journey Analysis & BOSS Revolution Recommendation".

Competitive teardown of Felix Pago's WhatsApp international mobile top-up
(recarga) service, and a recommended end-to-end WhatsApp IMTU flow for
BOSS Revolution.

IMPORTANT SCOPE NOTE, carried prominently in the document itself:
no live transaction was performed. Every Felix finding is sourced from public
material — Felix's own help centre, its recargas landing page, the three step
images it publishes on its CDN, its Terms/Privacy, app-store and Trustpilot/BBB
review corpora, and press. Findings are tagged Verified / Inferred / Unverified.

Method: 8 parallel research passes reconciled against 4 adversarial
verification passes, then synthesised. Claims that failed verification are
listed explicitly so the team does not act on them.

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

TITLE = "Felix Pago WhatsApp Top-Up — Journey Analysis & BOSS Revolution Recommendation"

# ------------------------------------------------------------------ content ----

BLOCKS = [
    ("h1", TITLE),
    ("cap", "Competitive teardown and channel recommendation · Prepared 29 August 2026 · "
            "DCS / IMTU · Sources public-only, no live transaction performed"),

    # ---------------------------------------------------------------- 1 ----
    ("h2", "1. Executive summary"),

    ("p", "Felix Pago sells international mobile top-ups entirely inside a WhatsApp thread. "
          "This document reconstructs that journey step by step from public evidence, assesses it, "
          "and recommends an end-to-end WhatsApp IMTU flow for BOSS Revolution."),

    ("p", "The headline is not that Felix built a good top-up product. It is that Felix built a good "
          "distribution position and then hung a thin top-up product off it. BOSS Revolution has the "
          "opposite problem: a deep top-up product with no conversational channel. That asymmetry, "
          "not any single UX pattern, is what should drive the decision."),

    ("h3", "What Felix does well"),
    ("b", "One thread, one number, one identity  —  the same WhatsApp number (+1 669 333-3549) serves "
          "onboarding, remittances, top-ups and 24/7 support. Top-up is a menu branch off an installed "
          "remittance relationship, not a separate acquisition. This is the real advantage."),
    ("b", "Detect-then-confirm carrier resolution  —  the user sends a number; Felix resolves country and "
          "carrier from the MSISDN, states what it found, and offers an explicit override. Two picker "
          "steps disappear without losing the correction path. This is the single most portable pattern."),
    ("b", "Structured choice inside a conversational wrapper  —  quick-reply buttons and a list picker "
          "drive the transaction. Free text is used only to declare intent. Every verified competitor "
          "converges on this design."),
    ("b", "A legible zero-fee claim  —  the checkout prints “Comisión Félix: $0.00 USD” as a line item, "
          "making the claim feel audited rather than asserted."),

    ("h3", "Where Felix is weak — and where BR wins on assets it already owns"),
    ("b", "No receipt, no reference number, no refund path  —  Felix's Terms never mention top-ups at all. "
          "A wrong number is unrecoverable by Felix's own statement. BR's existing receipt (itemised price, "
          "reference number, delivery status, savings line) is a decisive advantage."),
    ("b", "No promo mechanic on top-ups whatsoever  —  no bonus airtime, no first-recarga discount; the "
          "referral credit is denominated for transfers and is structurally unspendable on a recarga. "
          "Against BR, where BLS bonus airtime is the dominant conversion lever, this is Felix's clearest "
          "commercial gap."),
    ("b", "Card-only, US-issued, no Amex  —  no cash-in for top-ups, against BR's retail and NRS footprint."),
    ("b", "Documentation contradicts itself constantly  —  country count stated four different ways, "
          "recharge types three ways, accepted IDs three ways, refund windows differing between the "
          "Spanish and English help centres. In a channel where documentation is the product surface, "
          "that is a product defect, not a cosmetic one."),
    ("b", "Top-ups appear to have almost no traction  —  across 166 app-store reviews retrieved and searched "
          "programmatically, not one mentions a top-up as a purchased product."),

    ("h3", "The three things that most affect the BR decision"),
    ("n", "A US business cannot collect payment natively inside WhatsApp. Meta's Payments API exists only "
          "for India, Brazil and (unconfirmed) Singapore. The payment step must hand off to an external "
          "hosted checkout via a CTA URL button — and Meta's documentation states that URL opens in the "
          "device's default browser, not an in-app webview. That browser exit is the unavoidable funnel "
          "break and the largest unmeasured risk in the business case. Felix and Remitly both live with it."),
    ("n", "Whether Meta's Commerce Policy permits selling prepaid airtime over WhatsApp Business at all — "
          "including via external checkout — is not resolved by the policy text. This needs a ruling from "
          "Meta or a BSP compliance team before any build. It is the single largest policy risk to the concept."),
    ("n", "BR's own documents disagree about whether a WhatsApp channel already exists. The FY roadmaps "
          "describe a shipped DTC Universal API covering “CSA IVR, Braze, WhatsApp”; the August 2026 revenue "
          "analysis states flatly that “WhatsApp-first is also not a channel BR has — it is unbuilt candidate A8”. "
          "That is the difference between a one-quarter orchestration project and a Meta Business API "
          "onboarding programme, and it must be settled first."),

    ("h3", "Recommendation in one line"),
    ("p", "Do not open with full in-thread commerce. Lead with Request Top-Up plus WhatsApp nudges — a "
          "primitive BR has already shipped and under-leveraged, which needs no in-thread payment, carries "
          "the least platform risk, and is the same recipient-initiated pattern Remitly shipped in 2026 and "
          "Ding shipped in 2021. Build the full purchase flow behind it, once the payment and policy "
          "questions above are answered."),

    ("p", "One correction to carry back into internal material: BR's existing one-liner on Felix — "
          "“400K+ users, NPS >90, ~99% success / <2-min delivery via WhatsApp + USDC” — is partly wrong. "
          "400K+ users is right (Feb 2026). NPS >90 traces to coverage that could not be retrieved and is "
          "company-supplied. The ~99% success / <2-min figure is a remittance-payout testing metric, not a "
          "top-up metric. It should not go into a deck as written."),

    # ---------------------------------------------------------------- 2 ----
    ("h2", "2. Research approach and test conditions"),

    ("h3", "2.1 What was and was not done"),
    ("p", "No live transaction was performed and no purchase was initiated. No message was sent to Felix, "
          "no account was created, and no payment details were entered anywhere. The entire analysis is "
          "built from publicly published material."),
    ("p", "This is a real limitation and it is flagged wherever it bites. The parts of the journey that only "
          "a live session can establish — verbatim confirmation copy, whether a reference number is issued, "
          "the full error taxonomy, denominations per corridor, and whether KYC fires mid-flow — are "
          "collected in Section 9 rather than guessed at."),

    ("h3", "2.2 Sources used"),
    ("b", "Felix's own help centre  —  the recarga how-to article, the recargas landing page and FAQ, the "
          "international top-ups guide, and roughly 27 further help articles covering limits, verification, "
          "fraud, official channels, cards and support."),
    ("b", "Felix's own published step images  —  three annotated screenshots of a real top-up thread, served "
          "from Felix's CDN. These were invisible to text extraction because the img tags carry empty alt "
          "attributes, and they resolve four questions the documentation leaves ambiguous."),
    ("b", "Felix's legal surface  —  Terms of Use, Privacy Policy, and the site footer's licensing disclosure."),
    ("b", "Review corpora  —  82 App Store reviews and 84 Google Play reviews retrieved and searched "
          "programmatically, plus Trustpilot (512 reviews) and the BBB complaint file."),
    ("b", "Press and vendor material  —  TechCrunch, QED Investors, Stripe and Circle case studies, the "
          "Intermex partnership release. Vendor case studies are company-supplied marketing and are treated as such."),
    ("b", "Meta's own developer and business documentation  —  for every WhatsApp Business Platform constraint."),
    ("b", "BOSS Revolution internal material  —  the IMTU FY27 plan, IMTU and cross-cutting FY roadmaps, the "
          "competitor landscape file, and the August 2026 IMTU revenue analysis."),

    ("h3", "2.3 Method and confidence tagging"),
    ("p", "Eight parallel research passes were run, then reconciled against four adversarial verification "
          "passes whose instruction was to assume every claim false until independently re-fetched. Where a "
          "verification verdict contradicted a research finding, the verdict won. Thirty-eight claims that "
          "were believed on the first pass did not survive; the material ones are listed in Section 9.3 so "
          "they are not repeated downstream."),
    ("p", "Every finding in this document carries one of three confidence levels. Verified means it was read "
          "on a fetched page and can be quoted with a URL. Inferred means it is reasoned from adjacent "
          "evidence, with the reasoning stated. Unverified means it could not be established from public "
          "sources and is listed in Section 9."),

    ("h3", "2.4 Handling of sensitive data"),
    ("p", "All six occurrences of the recipient phone number in Felix's published screenshots have been "
          "redacted in the images reproduced here. The screenshots are Felix's own marketing material, "
          "reproduced for competitive analysis with attribution."),

    ("h3", "2.5 A caution about Felix's own copy"),
    ("p", "Felix's marketing and help copy is not a reliable description of its shipped product. It "
          "contradicts itself on country count (four ways), accepted IDs (three ways), recharge types "
          "(three ways), step count (two ways), refund windows (Spanish versus English), support channels, "
          "and even on whether the user picks the carrier or the system detects it. Where prose and "
          "screenshots disagree, this analysis follows the screenshots."),

    # ---------------------------------------------------------------- 3 ----
    ("h2", "3. The Felix journey, step by step"),

    ("p", "Seventeen steps, reconstructed from the sources in Section 2. Verbatim Spanish copy is quoted "
          "where Felix publishes it. Confidence is marked per step."),

    ("h3", "3.1 Discovery and entry"),
    ("p", "Step 1 — Entry (Verified). Felix's site CTAs deep-link into WhatsApp via "
          "api.whatsapp.com/send?phone=16693333549 with a prefilled message. Notably, the prefill on the "
          "recargas page reads “¡Hola Félix! Quiero realizar un envío de dinero” — a money-transfer message "
          "on a top-up page. A user arriving with top-up intent is handed transfer language. This is a "
          "free conversion leak and the first thing BR should not copy."),
    ("p", "Step 2 — Keyword (Verified). The user types “recarga”. Felix's help article is explicit: "
          "“Para enviar una recarga telefónica internacional con Félix, escribe 'recarga' en tu chat de "
          "WhatsApp”. There is no separate number, no menu button and no app for top-ups."),

    ("h3", "3.2 Recipient capture and carrier resolution"),
    ("p", "Step 3 — Number prompt (Verified). Felix asks: “¿A qué número quieres mandar la recarga? "
          "Incluye el código de país.” with an inline worked example, “Ejemplo: +52 1234567890”. Giving the "
          "format example in the prompt rather than in an error message is a small, cheap, effective choice."),
    ("p", "Step 4 — Number entry (Verified). The user sends the number. Free text, one turn."),
    ("p", "Step 5 — Validation (Unverified). The flow evidently parses the MSISDN server-side, but Felix "
          "publishes no error copy for a malformed number. What the user sees on a bad entry is unknown."),
    ("p", "Step 6 — Auto-detection (Verified). Felix resolves both country and carrier from the number and "
          "states the result: “Detecté que [número] (Colombia) es un número de Claro Colombia.” There is no "
          "country picker and no carrier picker before this point."),
    ("p", "Step 7 — Confirm or override (Verified). Felix asks “¿Continuamos?” and offers two quick-reply "
          "buttons: “Sí, continuar” and “Cambiar compañía”. This is the detect-then-confirm pattern, and it "
          "is the strongest single thing in the flow. It removes two steps while preserving a correction "
          "path — which matters because number portability makes carrier detection genuinely unreliable."),

    ("cap", "Steps 1–7 as Felix publishes them. Recipient number redacted. Source: felixpago.com/recargas-internacionales"),
    ("table", "IMG_STEP1"),

    ("h3", "3.3 Product and amount selection"),
    ("p", "Step 8 — Recharge type (Verified, with a caveat). Felix asks “Perfecto. ¿Qué tipo de recarga "
          "quieres hacer a tu numero Claro Colombia?”. The published taxonomy is datos, paquete, saldo libre "
          "— but Felix publishes three mutually inconsistent versions of this list across its own pages. "
          "There is no canonical set."),
    ("p", "Step 9 — Amount (Verified). Here the flow makes a consequential choice: the amount is denominated "
          "in the recipient's currency, not the sender's. Felix offers three quick-reply buttons "
          "(COP 4,000 / 5,000 / 6,000 in the published example) plus a separate list message, “Elegir un "
          "monto diferente: Opciones”, for the rest. Three buttons is not a design preference — it is "
          "WhatsApp's hard maximum, and the overflow list is the correct way to handle it."),
    ("p", "The FX rate is disclosed here, but only as an estimate: “Tipo de cambio estimado: ~3225.81 "
          "COP/USD. El total final en USD se confirma al pagar.” The sender is choosing a foreign-currency "
          "amount without yet knowing what they will be charged."),

    ("cap", "Steps 8–9: recharge type, amount in recipient currency, estimated FX. Source: felixpago.com"),
    ("table", "IMG_STEP2"),

    ("h3", "3.4 Summary, confirmation and payment"),
    ("p", "Step 10 — Summary (Verified). An in-chat “RESUMEN DE RECARGA” block lists número, país, compañía, "
          "producto, total a pagar in USD, and tipo de cambio. This is where the USD figure first appears."),
    ("p", "Step 11 — Confirmation gate (Verified). “¿Confirmas esta recarga?” with buttons “Confirmar recarga” "
          "and “Cambiar algo”. A genuine escape hatch immediately before the irreversible step."),
    ("p", "Step 12 — Payment hand-off (Verified). On confirmation Felix sends “Listo. Completa tu pago en "
          "este sitio seguro para enviar la recarga.” with a CTA URL button, “Pagar recarga”."),
    ("p", "Step 13 — Hosted checkout (Verified). The button opens Felix's own checkout at "
          "payments-ui.prod.fpago.com, branded “Félix recargas”, with a “Regresar a WhatsApp” return "
          "affordance. It repeats the summary and adds the explicit line “Comisión Félix: $0.00 USD”, then "
          "collects card number and expiry. Card details are never typed into the chat — the correct and "
          "only defensible design."),
    ("p", "Payment is restricted to US-issued debit or credit cards, excluding American Express. There is no "
          "cash-in option for top-ups, and Apple Pay / Google Pay are not present (Stripe's case study says "
          "Felix is “preparing” them, so treat their absence as current state rather than permanent)."),
    ("p", "Step 14 — Authorisation (Unverified). No decline copy or recovery path for a failed top-up "
          "payment is published anywhere."),

    ("cap", "Steps 10–13: summary, confirmation buttons, and the hand-off to Felix's hosted checkout. "
            "Recipient number redacted. Source: felixpago.com"),
    ("table", "IMG_STEP3"),

    ("h3", "3.5 Fulfilment and post-purchase"),
    ("p", "Step 15 — Confirmation (Verified as existing, Unverified as to content). Felix states it sends a "
          "WhatsApp confirmation once the recharge is processed. What that message actually says, and "
          "whether it carries a reference number, is not published. Felix's Terms define a transaction "
          "reference number only for Transfers — and the Terms never mention top-ups at all."),
    ("p", "Step 16 — Delivery (Verified). Balance is credited “en cuestión de minutos”, and the carrier "
          "sends the recipient its own message. Note that Felix leans on the carrier's notification as "
          "delivery evidence rather than issuing a delivery-confirmed message of its own."),
    ("p", "Step 17 — The irreversibility rule (Verified). This is the sharpest edge in the product. Felix "
          "states plainly that a wrong number “suele acreditar el saldo a otra línea sin posibilidad de "
          "reembolso”, and that “una vez procesada la recarga, no hay forma de corregir un error en estos "
          "datos”. Whether Felix refunds its own or a carrier's failure is undocumented."),

    ("h3", "3.6 Support"),
    ("p", "Human escalation is one keyword away — “hablar con agente” — 24/7 in Spanish, with no case number "
          "required. The best user reviews cite exactly this. The worst describe the opposite failure mode: "
          "being bounced back to the bot by the agents themselves."),

    # ---------------------------------------------------------------- 4 ----
    ("h2", "4. Detailed flowchart"),
    ("p", "Every step, decision point, alternate path and terminal state in the observed Felix journey. "
          "Dashed edges are documented but unobserved."),
    ("table", "IMG_FLOW_FELIX"),
    ("cap", "Diagram 1 — Felix Pago observed WhatsApp top-up journey"),

    # ---------------------------------------------------------------- 5 ----
    ("h2", "5. Strengths and weaknesses"),
    ("h3", "5.1 Strengths worth adopting"),
    ("table", "STRENGTHS"),
    ("h3", "5.2 Weaknesses, friction and abandonment risk"),
    ("table", "WEAKNESSES"),

    ("h3", "5.3 The pattern behind the weaknesses"),
    ("p", "Felix's failures cluster in one place: everything after the money leaves the sender's account. "
          "Acquisition, capture and checkout are well built. Receipts, delivery proof, error recovery, "
          "refunds and dispute handling are thin or absent, and the review corpus reflects exactly that "
          "distribution of complaints. For BR — which already has receipts, reference numbers, delivery "
          "states and a refund path — this is the most exploitable gap in the competitor."),

    # ---------------------------------------------------------------- 6 ----
    ("h2", "6. Competitive insights"),

    ("h3", "6.1 Felix is targeting BOSS Revolution by name"),
    ("p", "Felix publishes a comparison guide naming Boss Revolution and Ding as the two best-known "
          "international top-up players, and then coaches the reader on how to evaluate them — steering the "
          "comparison away from headline price and onto delivered balance, and warning readers to watch for "
          "“un descuento menor al valor nominal del saldo”. It does not disclose its own discount. This is "
          "SEO used as a competitive weapon, aimed directly at IDT, and it is the single most actionable "
          "passage found in the entire corpus."),

    ("h3", "6.2 The hosted-checkout hand-off is the industry norm, not a Felix compromise"),
    ("p", "Remitly is the closest strategic analogue. Its WhatsApp assistant (launched April 2025, expanded "
          "April 2026 to four send countries and 14 receive countries) quotes rate and fees in-thread and "
          "then completes payment “through Remitly's trusted, secure website”. Felix does the same thing "
          "with its own checkout. No US-market player has native in-thread payment, because none is available."),

    ("h3", "6.3 Recipient-initiated request is a shipped pattern — twice — and BR already owns the primitive"),
    ("p", "Remitly added Request Money in April 2026. Ding did the same thing five years earlier via KaiOS, "
          "letting a recipient request airtime that friends and family then purchase. BR's Request Top-Up is "
          "the same primitive, already shipped and described internally as under-leveraged. It needs no "
          "in-thread payment and carries the least platform risk of any entry point."),

    ("h3", "6.4 Nobody publishes conversion numbers for these channels"),
    ("p", "Remitly did not mention WhatsApp on its Q2 2026 earnings call at all, having discussed it "
          "earlier. That silence is worth noting. The only credible published benchmark is Meta-commissioned, "
          "from Indian insurance rather than US top-up, and reports a 43% higher conversion rate than "
          "business-as-usual Meta web campaigns for click-to-WhatsApp. Several widely circulated figures — "
          "including a “20% conversational vs under 1% ecommerce” comparison and various “45–60% WhatsApp "
          "conversion” claims — could not be traced to any primary document and should not be cited."),

    ("h3", "6.5 The bank-grade analogues are more instructive than the fintechs"),
    ("p", "FNB's eWallet in South Africa is the closest full analogue to “BOSS Revolution on WhatsApp”: no "
          "bank account required, in-channel KYC, a 5-digit PIN, and a product set spanning transfers, "
          "airtime, data, electricity and vouchers. Absa's ChatWallet sells airtime and data over WhatsApp "
          "to non-customers behind a menu and a PIN. Both prove that a full transactional product can live "
          "in the channel where payment rails permit it."),

    ("h3", "6.6 Meta is a competitor on this surface, not only a platform"),
    ("p", "Meta launched first-party prepaid recharge inside WhatsApp in India in April 2026, on its own "
          "payments rail, reachable from a dedicated icon on the home screen. It is domestic Indian "
          "recharge, so it does not compete with BR's US-outbound product today. But it establishes both "
          "the precedent and the UX template for any market where Meta controls payments, and Meta's stated "
          "motive — fixing weak UPI payments share — means it has reason to keep going. Whether Meta intends "
          "to extend this beyond India, or to cross-border top-up, is the existential question for the IMTU "
          "business and deserves a standing watch item rather than a one-off check."),

    ("h3", "6.7 The design consensus"),
    ("p", "Every verified transactional player — Felix, Remitly, FNB, Absa, ChatPay, RecargaPay — gates the "
          "transaction behind structured menus, buttons or a PIN, and completes payment either on a native "
          "rail where one exists or on a hosted page where it does not. Free text is used for intent "
          "capture only. Nobody is running open AI chat over a payment."),

    # ---------------------------------------------------------------- 7 ----
    ("h2", "7. Recommended BOSS Revolution WhatsApp IMTU flow"),

    ("p", "The recommended flow keeps Felix's proven spine — deep-link entry, keyword intent, number-first "
          "capture, detect-then-confirm carrier resolution, structured selection, in-chat summary, hosted "
          "checkout — and closes its transparency, recovery and identity gaps using capabilities BR already "
          "owns."),

    ("table", "IMG_FLOW_BR"),
    ("cap", "Diagram 2 — Recommended BOSS Revolution WhatsApp IMTU flow"),

    ("h3", "7.1 What to adopt, adapt, avoid, and add"),
    ("table", "ADOPT"),

    ("h3", "7.2 The three BR-only moves"),
    ("p", "Identity. Felix treats the WhatsApp number as the entire identity and starts every top-up from a "
          "blank number field. BR can match the WhatsApp number to an existing account and open with saved "
          "recipients and a one-tap reorder. This is the largest single conversion difference available, and "
          "it depends on the cross-app unified identity work already named internally as the most important "
          "enabling dependency."),
    ("p", "Promotions. Felix has no top-up promo mechanic at all. BR's BLS bonus airtime is described "
          "internally as the dominant conversion lever. Carrying it into the thread is a direct, "
          "unmatched advantage — and Felix's detect-then-confirm pattern is precisely the mechanism that "
          "makes BR's fragile carrier-scoped promo eligibility safe to show in a conversational context."),
    ("p", "Post-purchase. Felix's weakest area is BR's strongest. An itemised receipt with a reference "
          "number, a delivery-confirmed message distinct from payment confirmation, and an in-thread support "
          "handoff would beat the incumbent on exactly the dimension its users complain about most."),

    ("h3", "7.3 What the flow deliberately does not do"),
    ("p", "It does not carry the subscription toggle in its default-ON form. Attach lifted from ~0.9% to "
          "~45.5% with default-ON, but 95.5% of taps on the toggle switch it off, 12.7% cancel within 30 days "
          "at a 5.9-day median, and two consent defects are open — DCS-5277 (Critical) and DCS-5001, with "
          "DCS-5110 (Automatic Renewal Law notices) still To Do. Reproducing a default-ON mechanic inside a "
          "chat thread is a materially higher consent risk than in a visible checkout screen. The "
          "recommendation is default-OFF in chat regardless of how the in-app A/B resolves."),
    ("p", "It also does not put commerce and support on the same number without a decision. Felix does, and "
          "it is convenient. RecargaPay deliberately runs no WhatsApp support line at all and states that "
          "any such number claiming to be them is a scam. Given BR would be putting a payment flow and a "
          "support channel on one identity, the impersonation risk deserves quantifying before launch."),

    # ---------------------------------------------------------------- 8 ----
    ("h2", "8. Prioritised recommendations"),
    ("table", "PRIORITY"),

    ("h3", "8.1 Suggested sequencing"),
    ("p", "Phase 0, before any build: resolve the three blocking questions — does the DTC Universal API "
          "actually have a WhatsApp leg, does Meta's Commerce Policy permit airtime sales, and is there a "
          "WABA and BSP relationship at IDT today. None of these is a product question and all three can "
          "invalidate the plan."),
    ("p", "Phase 1, lowest risk: Request Top-Up with WhatsApp nudges. No in-thread payment, no catalogue, "
          "reuses a shipped primitive, and directly addresses a two-sided acquisition loop the FY27 plan "
          "already wants. This is where to prove channel economics."),
    ("p", "Phase 2: transactional utility templates — failed-renewal dunning first. 28.4% of active "
          "subscriptions sit in a failing payment state and a failed renewal currently produces no message "
          "on any channel (CRMC-3299, in backlog since 2024). This is the clearest unserved need, it is "
          "Utility-category and therefore free inside an open window, and it is measurable."),
    ("p", "Phase 3: full in-thread purchase, gated on the payment and policy answers from Phase 0 and on the "
          "measured browser-exit drop-off from a hosted-checkout pilot."),

    # ---------------------------------------------------------------- 9 ----
    ("h2", "9. Open questions, assumptions, and what remains unverified"),

    ("h3", "9.1 Unverified because no live session was run"),
    ("p", "The single highest-value next action is one live top-up from a US number with a US card. It "
          "would resolve most of this list in under an hour, and it needs prior approval before any purchase "
          "is completed."),
    ("b", "Denominations, minimums and maximums per country and carrier. One Colombia/Claro example exists; "
          "nothing else. This is the biggest gap for any price comparison against BR."),
    ("b", "The effective FX spread, benchmarked against mid-market on two or three corridors — the exact "
          "method Felix's own guide recommends readers use."),
    ("b", "Whether top-ups are sold at face value or at a discount to face value. This determines whether "
          "“no commission” is a real price advantage or a repositioned one."),
    ("b", "Whether a first-time user typing “recarga” is routed through full KYC, or whether small top-ups "
          "clear the tiered threshold without document verification."),
    ("b", "The verbatim confirmation message, and whether it carries a reference number, carrier name, "
          "destination number and delivered denomination."),
    ("b", "The complete error taxonomy and its copy: malformed number, unsupported carrier or country, "
          "denomination unavailable, declined card, and carrier fulfilment failure after successful payment."),
    ("b", "Whether any refund path exists for a Felix-side or carrier-side failure, as opposed to the "
          "documented no-refund rule for a wrong number."),
    ("b", "Whether a saved-number or one-tap repeat affordance exists for top-ups."),
    ("b", "Whether top-ups count against the AML send limits, which are documented only for transfers."),
    ("b", "Whether any scheduled or recurring top-up exists — directly relevant given subscriptions are 30%+ "
          "of BR IMTU revenue."),

    ("h3", "9.2 Structural unknowns a walkthrough will not answer"),
    ("b", "Who supplies Felix's top-up inventory — aggregator or direct carrier integrations. This "
          "determines its margin structure and how fast it can widen coverage, and it is an IDT-adjacent "
          "supplier question."),
    ("b", "Top-up transaction volume, attach rate to remittance users, and revenue contribution. No data exists."),
    ("b", "Whether Felix's Terms will ever be extended to cover top-ups, and what refund regime would apply."),
    ("b", "Whether prepaid airtime falls under Meta's prohibition on digital-goods commerce, and whether "
          "that policy reaches sales completed on an external checkout."),
    ("b", "The CFPB Consumer Complaint Database was never checked. For a US-licensed money transmitter this "
          "is the authoritative complaint venue and the largest single missing source in the corpus."),
    ("b", "Whether Felix runs Meta click-to-WhatsApp paid campaigns. A Meta Ad Library search would settle it."),

    ("h3", "9.3 Claims that failed verification — do not repeat these"),
    ("table", "REFUTED"),

    ("h3", "9.4 Open questions for the BR team"),
    ("table", "QUESTIONS"),

    ("h3", "9.5 Assumptions this analysis rests on"),
    ("b", "That Felix's published step images depict its current shipped flow. They are undated marketing "
          "assets; the flow may have changed since publication."),
    ("b", "That the absence of US WhatsApp payments documentation means the capability does not exist. No "
          "Meta page states this prohibition explicitly — it is inferred from three market-scoped editions "
          "and corroborated by integrator sources. Worth one confirming question to a Meta partner rep."),
    ("b", "That Felix's top-up corridors materially overlap BR's. Felix's own country statements conflict "
          "four ways, so the overlap is directional rather than precise."),
    ("b", "That review-corpus sentiment is representative. The app is roughly eight months old with a young "
          "review base, while Trustpilot spans a longer pre-app window; the two cohorts are not directly "
          "comparable."),

    ("h2", "10. Source note"),
    ("p", "Primary Felix sources: felixpago.com/recargas-internacionales, "
          "felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional, "
          "felixpago.com/ayuda/puedo-enviar-recargas-a-celulares, felixpago.com/guias/recargas-internacionales, "
          "and the Felix help centre index at felixpago.com/ayuda. Platform constraints are from Meta's "
          "developer documentation. Internal BR context is from IMTU_FY27_Plan.md, IMTU_FY_Roadmap.md, "
          "CrossCutting_FY_Roadmap.md and the August 2026 IMTU revenue analysis in this repository."),
]

# ------------------------------------------------------------------- tables ----

STRENGTHS = [
    ["Strength", "What Felix actually does", "Why it matters for BR"],
    ["One thread, one number, one identity",
     "+1 669 333-3549 serves onboarding, remittances, top-ups and 24/7 support. Top-up is a branch off an installed relationship.",
     "This, not any top-up feature, is Felix's real advantage. BR's equivalent is its installed app base plus cross-app identity."],
    ["Detect-then-confirm carrier resolution",
     "Resolves country and carrier from the MSISDN, states the result, offers “Cambiar compañía” as an override.",
     "The strongest directly portable pattern. Maps onto BR's fragile carrier-scoped BLS promo eligibility and the delivered country-vs-carrier error-sheet spec."],
    ["Structured choice, conversational wrapper",
     "Quick-reply buttons and a list picker drive the transaction; free text only declares intent.",
     "Caps the error surface without losing conversational entry. Matches every verified competitor."],
    ["Format example in the prompt",
     "“Ejemplo: +52 1234567890” is given when asking, not after a failure.",
     "Near-zero cost, reduces malformed entries before they happen."],
    ["Legible zero-fee claim",
     "Checkout prints “Comisión Félix: $0.00 USD” as an explicit line item.",
     "Makes a pricing claim feel audited. Rhetorically strong against a competitor whose fee is a visible line."],
    ["Escape hatch before the irreversible step",
     "“Cambiar algo” alongside “Confirmar recarga” on the final summary.",
     "Cheap correction at the one moment where error cost is highest."],
    ["Card data never enters the chat",
     "Payment collected on a hosted page, with a “Regresar a WhatsApp” return path.",
     "The only defensible design, and the one BR must replicate regardless."],
    ["Human escalation one keyword away",
     "“hablar con agente”, 24/7 in Spanish, no case number required.",
     "The strongest positive reviews cite exactly this."],
    ["Prominent irreversibility warnings",
     "Repeated four times, plus a comparison table rating reversibility “Muy baja”.",
     "Honest UX that pre-empts disputes, whatever one thinks of the liability posture."],
    ["Comparison SEO as a weapon",
     "Publishes a guide naming Boss Revolution and Ding, then coaches readers on how to compare them.",
     "Aimed directly at IDT. Worth a response in BR's own content."],
]

WEAKNESSES = [
    ["Weakness", "Evidence", "Risk / opportunity for BR"],
    ["No receipt, reference number or refund path for top-ups",
     "The Terms never mention top-ups at all. A wrong number is unrecoverable by Felix's own statement.",
     "BR's itemised receipt with reference number and delivery status is a decisive, already-built advantage."],
    ["Entry prefill contradicts entry intent",
     "The recargas page deep-links into WhatsApp with “Quiero realizar un envío de dinero” prefilled.",
     "A free conversion leak. BR should match prefill to the creative that was tapped."],
    ["Amount chosen in recipient currency, USD total deferred",
     "“El total final en USD se confirma al pagar.” The published FX estimate drifts across the three screens.",
     "The sender commits before knowing the charge. BR should price in both currencies with a locked rate."],
    ["No promo mechanic on top-ups whatsoever",
     "No bonus airtime, no first-recarga discount. The referral credit is denominated for transfers and is unspendable on a recarga.",
     "Felix's clearest commercial gap, against BR's dominant conversion lever."],
    ["Card-only, US-issued, no Amex, no cash-in",
     "Stated on the recargas FAQ. Cash is a money-transfer method only.",
     "A real distribution gap against BR's retail and NRS footprint."],
    ["Verification burden sits entirely on the sender",
     "Felix's own guide: “recargar a la operadora equivocada es el error más común y el más difícil de corregir.”",
     "Detection reduces typing, not risk. BR can add an echo-back and a cheap edit path."],
    ["Bot loops on support escalation",
     "Four reviewers across three platforms describe agents returning them to the bot, including after asking for a supervisor.",
     "The gap between a good escalation keyword and a good escalation experience."],
    ["Unexplained declines with no diagnostic reason",
     "Multiple reviews report cancelled sends with no stated cause; the Terms reserve a silent-hold authority.",
     "BR's own failure taxonomy has the same defect — 47.3% of failed orders carry no usable reason code."],
    ["Mid-transaction KYC as an abandonment point",
     "Reviewers report accounts blocked after ID and selfie, with only an AI available to appeal to.",
     "Argues for tiering KYC so small top-ups clear without document capture."],
    ["Documentation contradicts itself constantly",
     "Country count four ways, recharge types three ways, IDs three ways, step count two ways, refund windows ES vs EN.",
     "In a channel where documentation is the product surface, this is a product defect."],
    ["Anti-phishing guidance contradicts its own channels",
     "The Spanish help centre tells users to distrust any Felix contact outside WhatsApp; the English one designates email and SMS as official.",
     "A Spanish-speaking user would be told to ignore genuine Felix messages."],
    ["Pre-checked, tooltip-hidden marketing consent",
     "The SMS consent control ships pre-checked site-wide, with the consent text concealed in a tooltip.",
     "A hazard to avoid, not a pattern to copy — particularly given BR's own open consent defects."],
    ["Refund latency against instant debiting",
     "Reviews cite 10-day refunds against instant debits; a BBB case shows a promised refund unreceived two months later.",
     "A trust wedge BR can attack directly."],
    ["Localisation is a shell",
     "English and Portuguese pages are Spanish underneath; the English CTA button is still Spanish.",
     "Caps Felix's non-Spanish acquisition. BR already runs a multilingual Braze creative pipeline."],
    ["Top-ups have almost no traction",
     "Zero of 166 app-store reviews retrieved and searched mention a top-up as a purchased product.",
     "The incumbent's position in this specific product is far weaker than its brand suggests."],
]

ADOPT = [
    ["Verdict", "Pattern", "How BR should treat it"],
    ["Adopt", "Detect-then-confirm carrier resolution",
     "Resolve country and carrier from the MSISDN, state the result, require an explicit confirm, offer an override. Directly de-risks BR's carrier-scoped promo eligibility."],
    ["Adopt", "Structured selection via buttons and lists",
     "Never free-text-parse the transaction. Free text captures intent only."],
    ["Adopt", "Format example inside the prompt",
     "Give the number format when asking, not after a failure."],
    ["Adopt", "In-chat summary with an explicit confirmation gate",
     "Summary block plus confirm / change-anything buttons immediately before the irreversible step."],
    ["Adopt", "Hosted checkout, card data never in-thread",
     "Architecturally forced for a US business, and correct regardless."],
    ["Adopt", "Explicit zero-or-stated fee line on checkout",
     "Print the fee as a line item even when it is zero."],
    ["Adopt", "Keyword escalation to a human",
     "One keyword, no case number. Resource it so it does not loop back to the bot."],
    ["Adapt", "Amount selection",
     "Felix prices in recipient currency with a deferred USD total. BR should show both currencies on every option with a locked rate and a validity window."],
    ["Adapt", "Irreversibility warning",
     "Keep the honesty, but pair it with an echo-back of the number in readable groups and a cheap edit path — warn and prevent, not warn and disclaim."],
    ["Adapt", "Entry deep link",
     "Keep click-to-WhatsApp, but match the prefill to the creative. Felix's own prefill contradicts its top-up page."],
    ["Adapt", "Carrier's message as delivery proof",
     "Send BR's own delivery-confirmed message, distinct from payment confirmation, rather than relying on the carrier's."],
    ["Avoid", "Shipping without a receipt or reference number",
     "BR already has both. Carry them into the thread."],
    ["Avoid", "Leaving refund and failure policy undefined",
     "Define the top-up refund regime before launch, including carrier-side failure."],
    ["Avoid", "Pre-checked or bundled marketing consent",
     "Capture opt-in explicitly and separately from the purchase."],
    ["Avoid", "Default-ON subscription mechanics in chat",
     "Higher consent risk than a visible checkout screen, with DCS-5277 and DCS-5110 open. Default-OFF in chat."],
    ["Avoid", "Contradictory published documentation",
     "In this channel the documentation is the product surface."],
    ["Avoid", "Declines with no stated reason",
     "Return a typed decline reason and an in-thread retry with an alternate method."],
    ["New", "Identity-aware opening",
     "Match the WhatsApp number to the BR account, greet by name, surface saved recipients and one-tap reorder. Felix starts every top-up from a blank field."],
    ["New", "BLS promos and bundles in-thread",
     "Bonus airtime and data bundles ranked by Engager/NBO. Felix has no top-up promo mechanic at all."],
    ["New", "Request Top-Up as the channel wedge",
     "Recipient-initiated requests need no in-thread payment. Remitly and Ding both shipped this; BR already has the primitive."],
    ["New", "Failed-renewal dunning over WhatsApp",
     "28.4% of active subscriptions are in a failing payment state with no message on any channel today (CRMC-3299)."],
    ["New", "Cash-in via retail and NRS",
     "A funding option Felix structurally cannot match on top-ups."],
]

PRIORITY = [
    ["#", "Recommendation", "Why now", "Effort"],
    ["P0", "Settle whether the DTC Universal API has a live WhatsApp leg",
     "The FY roadmaps and the Aug 2026 revenue analysis directly contradict each other. Determines whether this is a one-quarter project or a Meta onboarding programme.",
     "Days"],
    ["P0", "Get a ruling on Meta's Commerce Policy for prepaid airtime",
     "Whether airtime counts as prohibited digital content, and whether the policy reaches external checkout, is unresolved. Largest single policy risk to the concept.",
     "Days–weeks"],
    ["P0", "Confirm no US-available native WhatsApp payment path",
     "If confirmed, the CTA-URL browser exit is architecturally unavoidable and must be modelled in the business case.",
     "Days"],
    ["P1", "Run one live Felix top-up, with prior approval",
     "Resolves roughly two-thirds of the unverified list in under an hour: denominations, confirmation copy, error taxonomy, whether KYC fires.",
     "Hours"],
    ["P1", "Benchmark Felix's effective rate against BR and Ding",
     "Use the published Colombia/Claro example ($1.87 USD for COP 6,000) as the starting comparison — the exact method Felix's own guide recommends.",
     "Days"],
    ["P1", "Correct the internal Felix one-liner before it reaches a deck",
     "NPS >90 is unverified; ~99% / <2-min is a remittance-payout metric, not a top-up metric.",
     "Hours"],
    ["P2", "Scope Request Top-Up + WhatsApp nudges as the channel wedge",
     "No in-thread payment, lowest platform risk, reuses a shipped primitive, and proves channel economics before any commerce build.",
     "1 quarter"],
    ["P2", "Design failed-renewal dunning as a Utility template",
     "28.4% of subscriptions are failing with no message on any channel. Free inside an open window, and measurable.",
     "1 quarter"],
    ["P2", "Make the Promo Eligibility & Error-Sheet Service the hard dependency",
     "Its KPI already names cross-channel eligibility consistency across app, WhatsApp and IVR.",
     "Aligns with FY27 #5"],
    ["P3", "Model the Utility vs Marketing template split for every BR promo mechanic",
     "A validity reminder is free-in-window Utility; adding a promo nudge re-prices it as Marketing.",
     "Days"],
    ["P3", "Verify existing app/web opt-in language carries over to Meta's requirements",
     "Opt-in need not be collected on WhatsApp if worded correctly — this avoids a fresh consent collection.",
     "Days"],
    ["P3", "Decide the CTA hand-off target: app deep link or web",
     "Deep-link rails are done, but IMTU web is about a year behind the app and lacks wallet payment, tokenised cards and instrumentation.",
     "Days"],
    ["P3", "Quantify the impersonation and ATO risk of commerce-plus-support on one number",
     "RecargaPay refuses to run any WhatsApp support line and calls any such number a scam. Felix does the opposite.",
     "Weeks"],
    ["P4", "Establish a standing watch on Meta's recharge expansion",
     "Whether Meta extends in-app recharge beyond India or to cross-border is the existential question for IMTU.",
     "Ongoing"],
]

REFUTED = [
    ["Claim believed on first pass", "What is actually true"],
    ["Felix purely auto-detects the carrier with no selection step.",
     "Auto-detect then explicit confirm-or-override, with “Sí, continuar” / “Cambiar compañía” buttons."],
    ["No screenshot or transcript of the top-up flow exists publicly.",
     "Felix publishes three annotated screenshots of a real thread. They were invisible to text extraction because the img alt attributes are empty."],
    ["Denominations, amounts and FX rates are published nowhere.",
     "A complete worked example is published: COP 4,000/5,000/6,000, $0.00 commission, $1.87 USD total, ~3,211 COP/USD. No per-country grid exists, but “nothing published” is false."],
    ["Felix claims 40+ top-up carriers.",
     "Unsubstantiated marketing. Felix's own table yields 16 distinct carrier brands across 31 country-carrier entries, and the accompanying logo strip recycles remittance payout logos."],
    ["The practical top-up country list is 10.",
     "Unknown. Felix states its footprint four different ways across its own properties — 9, 10, “more than 10”, and 11."],
    ["Top-ups are a pilot with human-in-the-loop fulfilment.",
     "Refuted. The screenshots show a fully automated, button-driven bot handling detection, selection, summary, confirmation and payment hand-off."],
    ["The product launched around 24 August 2026.",
     "That is a CMS publish date for a help article. The dedicated domain was registered in December 2025; the effort is roughly eight months old."],
    ["Stripe processes top-up payments.",
     "Unestablished. The Stripe case study covers money transfers only and never mentions recargas. The top-up checkout is Felix-owned."],
    ["Felix has processed $3 billion in payment volume.",
     "That is a projection, not an achievement. The verified achieved figure is over $1B in the year to approximately April 2025."],
    ["Felix's valuation approaches $1B.",
     "Never officially disclosed. It traces to speculation the CEO publicly dismissed. Do not put a valuation in a deck."],
    ["Felix is a Y Combinator company.",
     "It is not. The YC company page returns 404. Founding year is also unresolved between 2020 and 2021."],
    ["The iOS listing claims 130+ countries and 300+ carriers for Felix.",
     "That copy belongs to the “similar apps” module. The 300+ carriers line is BOSS Money — IDT's own app."],
    ["First-time users must complete KYC before any transaction.",
     "Tiered. Registration is required; document and selfie verification is a gated step, and small amounts can start without full verification."],
    ["WhatsApp payments are coming to the US, EU and Canada.",
     "Based on a third-party iOS beta teardown, not a Meta announcement. The article itself says presence in a beta menu does not guarantee launch. Do not plan against it."],
    ["Conversational channels convert at 20%+ versus under 1% for ecommerce; WhatsApp converts at 45–60%.",
     "Neither figure could be traced to any primary document. Both trace to vendor marketing with no defined denominator. Do not cite."],
    ["BR's internal note: Felix has NPS >90 and ~99% success / sub-2-minute delivery.",
     "400K+ users is correct (Feb 2026). NPS >90 is company-supplied and unretrievable. The ~99% / <2-min figure is a remittance-payout test metric, not a top-up metric."],
]

QUESTIONS = [
    ["Tier", "Question", "Why it matters"],
    ["Blocking", "Does the DTC Universal API have a live WhatsApp leg, or not?",
     "The roadmaps say shipped; the Aug 2026 revenue analysis says unbuilt. No spec, endpoint list, vendor, WABA ID or template inventory exists anywhere in the repository."],
    ["Blocking", "Is there a Meta WhatsApp Business Account, verified business profile or BSP relationship at IDT today?",
     "No vendor or conversation-pricing model appears in any internal document."],
    ["Blocking", "Does Meta's Commerce Policy permit a US business to sell international airtime over WhatsApp?",
     "Unresolved by the policy text, including whether it reaches external checkout. Needs a ruling before build."],
    ["Blocking", "Is there genuinely no US-available native payment path?",
     "If confirmed, the browser exit is unavoidable and must be modelled as the primary funnel risk."],
    ["Blocking", "What does Confluence page 5926354995 (“IMTU in WA”) actually cover — WhatsApp or Web App?",
     "If WhatsApp, it is the most important internal document for this project and is summarised nowhere."],
    ["Competitive", "What are Felix's denominations, minimums and maximums per corridor?",
     "The biggest gap for any price comparison. One live session answers it."],
    ["Competitive", "Is Felix selling at face value or at a discount to face value?",
     "Determines whether “no commission” is a real price advantage or a repositioned one."],
    ["Competitive", "Who supplies Felix's top-up inventory?",
     "Determines its margin structure and how fast it can widen coverage. An IDT-adjacent supplier question."],
    ["Product", "Would a WhatsApp channel carry the subscription toggle, and in what default state?",
     "Default-ON in a chat thread is a materially higher consent risk than in a visible checkout, with DCS-5277 and DCS-5110 open."],
    ["Product", "Which BR promo mechanics survive Meta's Utility versus Marketing split?",
     "A validity reminder is free-in-window Utility; adding a promo nudge re-prices the whole template as Marketing."],
    ["Product", "Which surface does the CTA URL hand off to — app deep link or web?",
     "Deep-link rails are done, but IMTU web lacks wallet payment, tokenised cards, Braze delivery and Amplitude instrumentation."],
    ["Product", "What does WhatsApp add over push and SMS, quantitatively?",
     "BR's own revenue analysis recommends push/SMS for win-back. The failed-renewal gap could be closed on existing channels first, at far lower cost."],
    ["Product", "How would channel performance be measured?",
     "Renewal charges emit no app event and notification-service messages are untracked in Amplitude (DCS-5260). Any measurement plan inherits that blind spot."],
    ["Strategic", "Has Meta signalled intent to extend in-app recharge beyond India, or to cross-border?",
     "The existential question for the IMTU business. Should be a standing watch item."],
]

TABLES = [
    ("STRENGTHS", STRENGTHS),
    ("WEAKNESSES", WEAKNESSES),
    ("ADOPT", ADOPT),
    ("PRIORITY", PRIORITY),
    ("REFUTED", REFUTED),
    ("QUESTIONS", QUESTIONS),
]

# marker -> (filename, width_pt, native_w, native_h)
IMAGES = [
    ("IMG_STEP1", "felix_redacted_step1.png", 200.0, 718, 1000),
    ("IMG_STEP2", "felix_redacted_step2.png", 200.0, 718, 1000),
    ("IMG_STEP3", "felix_redacted_step3.png", 200.0, 718, 998),
    ("IMG_FLOW_FELIX", "felix_whatsapp_topup_flow.png", 468.0, 2405, 2508),
    ("IMG_FLOW_BR", "br_whatsapp_imtu_recommended_flow.png", 468.0, 2405, 2508),
]

# Named sources cited in prose that linkify's bare-URL rule cannot catch,
# because they appear without an https:// prefix. Longest-first matching in
# spans_for() means the short /ayuda entry cannot clobber the longer paths.
FELIX_LINKS = {
    "felixpago.com/recargas-internacionales":
        "https://www.felixpago.com/recargas-internacionales",
    "felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional":
        "https://www.felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional",
    "felixpago.com/ayuda/puedo-enviar-recargas-a-celulares":
        "https://www.felixpago.com/ayuda/puedo-enviar-recargas-a-celulares",
    "felixpago.com/guias/recargas-internacionales":
        "https://www.felixpago.com/guias/recargas-internacionales",
    "felixpago.com/ayuda": "https://www.felixpago.com/ayuda",
    "payments-ui.prod.fpago.com": "https://payments-ui.prod.fpago.com",
    "api.whatsapp.com/send?phone=16693333549":
        "https://api.whatsapp.com/send/?phone=16693333549",
}

STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT",
             "cap": "NORMAL_TEXT"}

VERDICT_COLOR = {
    "Adopt": (0.05, 0.48, 0.42),
    "Adapt": (0.65, 0.35, 0.04),
    "Avoid": (0.70, 0.15, 0.12),
    "New":   (0.25, 0.32, 0.62),
    "Blocking": (0.70, 0.15, 0.12),
    "Competitive": (0.65, 0.35, 0.04),
    "Product": (0.05, 0.48, 0.42),
    "Strategic": (0.25, 0.32, 0.62),
    "P0": (0.70, 0.15, 0.12),
    "P1": (0.65, 0.35, 0.04),
    "P2": (0.05, 0.48, 0.42),
    "P3": (0.25, 0.32, 0.62),
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
            return el["startIndex"], len(para_text(el)), doc
    return None, None, doc


def insert_table(docs, doc_id, marker, data):
    idx, plen, _ = find_marker(docs, doc_id, marker)
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
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        if r == 0:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True}, "fields": "bold"}})
        elif txt in VERDICT_COLOR and c == 0:
            red, green, blue = VERDICT_COLOR[txt]
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": start + len(txt)},
                "textStyle": {"bold": True, "foregroundColor": {"color": {
                    "rgbColor": {"red": red, "green": green, "blue": blue}}}},
                "fields": "bold,foregroundColor"}})
    batched(docs, doc_id, reqs, size=40)
    return True


def insert_image(docs, doc_id, marker, fname, width, nw, nh):
    idx, plen, _ = find_marker(docs, doc_id, marker)
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

    linkify(docs, doc_id, {**LINK_MAP, **FELIX_LINKS})

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
