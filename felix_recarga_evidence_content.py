#!/usr/bin/env python3
"""
Single source of truth for the Felix Pago WhatsApp top-up teardown (September 2026).

Consumed by:
  create_felix_recarga_evidence_doc.py   (Google Doc)
  build_felix_recarga_evidence_html.py   (self-contained HTML report / Claude artifact)

Block kinds: h1 h2 h3 h4 p b (bullet) n (numbered) cap (caption) quote (verbatim
copy, prefix "Bot:" / "User:" / "Web:") table (marker) image (marker).
Paragraphs and bullets may use "Lead  ::  rest" to bold the lead.
"""

from pathlib import Path
from PIL import Image

BASE = Path(__file__).parent
IMG_DIR = BASE / "felix_evidence"

TITLE = "Felix Pago WhatsApp Top-Up: The Real End-to-End Flow"
SUBTITLE = ("Second-pass teardown of Félix's recarga journey, rebuilt from Félix's own production "
            "screenshots, 36 public videos and its launch carousels, with every step graded by the "
            "evidence behind it and the implications for the BOSS Revolution WhatsApp IMTU channel (A8).")
META_LINE = ("10 September 2026  ·  Author João Tanaka  ·  Supersedes the 29 August 2026 analysis: "
             "https://docs.google.com/document/d/18ajLNYrY49XjDsz4DwEVrElQknsdr5wWuGfl9QN3kLk/edit"
             "  ·  Google Doc version: https://docs.google.com/document/d/1MiP_fI-gY0ZIfxcdfYEnrTTVTUVkWtl3Ysth8T-MHAY/edit"
             "  ·  No live transaction was run")

PREV_DOC = "https://docs.google.com/document/d/18ajLNYrY49XjDsz4DwEVrElQknsdr5wWuGfl9QN3kLk/edit"

EXTRA_LINKS = {
    "felixpago.com/recargas-internacionales": "https://www.felixpago.com/recargas-internacionales",
    "felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional":
        "https://www.felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional",
    "felixpago.com/ayuda/puedo-enviar-recargas-a-celulares":
        "https://www.felixpago.com/ayuda/puedo-enviar-recargas-a-celulares",
    "felixpago.com/guias/recargas-internacionales": "https://www.felixpago.com/guias/recargas-internacionales",
    "payments-ui.prod.fpago.com": "https://payments-ui.prod.fpago.com",
    "pay.felixpago.com": "https://pay.felixpago.com",
    "Félix's recarga launch video": "https://www.youtube.com/watch?v=hCliPe4-71w",
    "Félix's May 2026 tutorial": "https://www.youtube.com/watch?v=V7EJA0MV8fQ",
    "the X launch carousel": "https://x.com/Felixpago/status/2090884151939301454",
    "the Instagram carrier carousel": "https://www.instagram.com/p/DbbxTDwE7hJ/",
    "Despierta América segment": "https://www.youtube.com/watch?v=q7B_XdXNnnQ",
    "the 2022 brand spot": "https://www.youtube.com/watch?v=cokVPx6A394",
    "App Store listing": "https://apps.apple.com/us/app/f%C3%A9lix-pago-env%C3%ADos-de-dinero/id6756128226",
    "Google Play listing": "https://play.google.com/store/apps/details?id=com.felixpago.felix&hl=es",
    "the August 2026 analysis": PREV_DOC,
    "IMTU FY27 Plan": "https://github.com/tanaka-idt/IDT-Claude/blob/main/IMTU_FY27_Plan.md",
}

# Words that render as coloured chips (HTML) or coloured bold text (Google Doc)
GRADE_WORDS = {
    "Real": "real", "Video": "video", "Mock": "mock", "Documented": "doc", "Risk": "risk",
    "Confirmed": "real", "Corrected": "risk", "Still open": "mock", "New": "video",
    "Adopt": "real", "Adapt": "video", "Avoid": "risk", "Add": "mock",
}
VERDICT_COLOR = {
    "Real": (0.12, 0.54, 0.36), "Video": (0.17, 0.42, 0.69), "Mock": (0.65, 0.45, 0.04),
    "Documented": (0.43, 0.45, 0.43), "Risk": (0.69, 0.23, 0.23),
    "Confirmed": (0.12, 0.54, 0.36), "Corrected": (0.69, 0.23, 0.23), "Still open": (0.65, 0.45, 0.04),
    "New": (0.17, 0.42, 0.69),
    "Adopt": (0.12, 0.54, 0.36), "Adapt": (0.17, 0.42, 0.69), "Avoid": (0.69, 0.23, 0.23), "Add": (0.65, 0.45, 0.04),
}


def _img(marker, fname, width_pt):
    with Image.open(IMG_DIR / fname) as im:
        w, h = im.size
    return (marker, fname, float(width_pt), w, h)


IMAGES = [
    _img("IMG_STEP1", "felix_step1_redacted.jpg", 235),
    _img("IMG_STEP2", "felix_step2_redacted.jpg", 235),
    _img("IMG_STEP3", "felix_step3_redacted.jpg", 300),
    _img("IMG_IG_MOCK", "ig_mock_chat.jpg", 200),
    _img("IMG_X_MOCK_CHAT", "x_mock_chat.jpg", 200),
    _img("IMG_X_MOCK_CHECKOUT", "x_mock_checkout.jpg", 200),
    _img("IMG_LAUNCH1", "launch_video_step1_overlay.jpg", 300),
    _img("IMG_LAUNCH2", "launch_video_step2_overlay.jpg", 300),
    _img("IMG_LAUNCH3", "launch_video_step3_overlay.jpg", 300),
    _img("IMG_TUT01", "tut_01_web_calculator.jpg", 190),
    _img("IMG_TUT02", "tut_02_redirect_whatsapp.jpg", 150),
    _img("IMG_TUT03", "tut_03_menu.jpg", 150),
    _img("IMG_TUT04", "tut_04_beneficiary_list.jpg", 150),
    _img("IMG_TUT05", "tut_05_amount_and_beneficiary.jpg", 150),
    _img("IMG_TUT06", "tut_06_resumen_confirm.jpg", 150),
    _img("IMG_TUT07", "tut_07_payment_handoff.jpg", 150),
    _img("IMG_TUT08", "tut_08_checkout_review.jpg", 150),
    _img("IMG_TUT09", "tut_09_cvv.jpg", 150),
    _img("IMG_TUT10", "tut_10_success_referral.jpg", 150),
    _img("IMG_REAL01", "real_01_entry_prefilled_token.jpg", 150),
    _img("IMG_REAL02", "real_02_payment_method_inapp_browser.jpg", 150),
    _img("IMG_REAL03", "real_03_kyc_step1_of_3.jpg", 150),
    _img("IMG_REAL04", "real_04_whatsapp_receipt_reference.jpg", 150),
    _img("IMG_IG_CARRIERS", "ig_carriers_grid.jpg", 330),
    _img("IMG_DIAGRAM", "felix_recarga_flow_evidence.png", 468),
    _img("IMG_IOS", "ios_companion_app.jpg", 130),
]

IMAGE_CAPTIONS = {
    "IMG_STEP1": "Steps 1 to 5 as Félix published them (real WhatsApp iOS capture, 3:57 to 4:01 PM, 32 unread chats, "
                 "battery 94%). Recipient number redacted. Source: felixpago.com/recargas-internacionales",
    "IMG_STEP2": "Step 6, the amount picker, and the top of the RESUMEN card (5:40 PM session). Source: felixpago.com/recargas-internacionales",
    "IMG_STEP3": "Steps 7 to 9: summary, Confirmar recarga, the Pagar recarga CTA and the hosted checkout opening inside "
                 "WhatsApp's in-app browser at 5:44 PM. Source: felixpago.com/recargas-internacionales",
    "IMG_IG_MOCK": "Instagram, 30 Jul 2026: designed mock (timestamps run backwards, +52 example detected as Colombia). "
                   "Bot copy matches the production capture word for word.",
    "IMG_X_MOCK_CHAT": "X, 21 Aug 2026: mock of the entry and number prompt. The sender types a full sentence containing the keyword.",
    "IMG_X_MOCK_CHECKOUT": "X, 21 Aug 2026: mock of the checkout with a saved card ending 4242 (Stripe's public test card) and the "
                           "English SKU name Unlimited GB 2 Hours.",
    "IMG_LAUNCH1": "Launch video, 27 Jul 2026 (Manuel Godoy, CEO): overlay step 1, Escribir la palabra Recarga. The phone insert is too small to read.",
    "IMG_LAUNCH2": "Launch video: overlay step 2, Compartir el teléfono del que quieres enviarle saldo.",
    "IMG_LAUNCH3": "Launch video: overlay step 3, Confirmar la operación. Three steps in marketing, twelve on the real screens.",
    "IMG_TUT01": "Web calculator on felixpago.com: destination, USD amount, MXN received, promotional rate, first-send fee waived, SMS consent.",
    "IMG_TUT02": "The website hands the sender to WhatsApp with a full-screen Redirigiéndote a WhatsApp interstitial.",
    "IMG_TUT03": "First bot message: today's FX rate, then three quick replies (Enviar dinero, Refiere y gana, Otras opciones). "
                 "The composer is prefilled by the deep link.",
    "IMG_TUT04": "Saved beneficiaries come back as a WhatsApp list message (Opciones), with Nuevo beneficiario at the top.",
    "IMG_TUT05": "Free-text amount in either currency, immediate conversion, then the beneficiary and delivery-method list pickers.",
    "IMG_TUT06": "RESUMEN block in monospace headers: amount, rate, destination, itemised fees, total. Buttons Sí, correcto / Cambiar algo.",
    "IMG_TUT07": "Payment hand-off message with a CTA URL button, Completar pago.",
    "IMG_TUT08": "Hosted checkout at pay.felixpago.com: review, saved card ending 1084 with Cambiar, total, Enviar ahora. "
                 "Branded An authorized agent of UniTeller.",
    "IMG_TUT09": "CVV re-entry for the saved card before the charge.",
    "IMG_TUT10": "Success page: ¡Listo! Tu pago se completó con éxito, an availability estimate of about 30 minutes, then a referral offer. "
                 "An earlier frame shows Volver a WhatsApp in the same slot.",
    "IMG_REAL01": "Independent creator's real first transfer, March 2026: the deep link prefills an 8-character session token plus the greeting, "
                  "WhatsApp shows the Meta secure-service notice, and the welcome still defaults to Mexico.",
    "IMG_REAL02": "The Completar pago link opens inside WhatsApp's in-app browser (title WhatsApp, Done control). Card is the only method; "
                  "credit cards carry an issuer-fee warning and debit is flagged Sin comisión extra. Recipient name pixelated.",
    "IMG_REAL03": "Sender identity is collected inside the checkout as step 1 de 3 (name, date of birth, email), after the transfer is fully specified. "
                  "An optional Verifica tu identidad tier is offered above the form.",
    "IMG_REAL04": "After payment the bot posts ¡Tu envío está siendo procesado! En un momento te enviamos tu recibo por email, then a receipt image whose "
                  "hero is the pickup reference number. Reference and personal lines pixelated; the creator had already covered part of the number.",
    "IMG_IG_CARRIERS": "Carriers per country from the 30 Jul 2026 Instagram carousel: Mexico (7 brands), Guatemala, Honduras, Nicaragua, "
                       "Costa Rica, Colombia, Dominican Republic, Ecuador, Peru. El Salvador is absent.",
    "IMG_DIAGRAM": "The recarga journey with every step coloured by the strongest evidence found for it.",
    "IMG_IOS": "The native iOS app is a rates-and-alerts companion; it contains no recarga and sends transactions back to WhatsApp.",
}

# ------------------------------------------------------------------ TABLES ----
TABLES = [
    ("EVIDENCE", [
        ["Source", "Type", "Date", "What it shows", "Grade"],
        ["felixpago.com/recargas-internacionales, three step images",
         "WhatsApp iOS production captures framed by marketing (payments-ui.prod.fpago.com hostname, Meta verified badge, real unread counts)",
         "Live page, captured 9 Sep 2026", "Steps 1 to 9 of the recarga flow, two separate sessions (3:57 to 4:01 PM and 5:40 to 5:44 PM)", "Real"],
        ["Félix's May 2026 tutorial (Cómo enviar dinero por WhatsApp con Félix, 1080p)",
         "Screen recording of the remittance flow, same bot", "7 May 2026",
         "Web calculator, redirect, menu, amount, list pickers, RESUMEN, hand-off, hosted checkout, CVV, success page", "Video"],
        ["Despierta América segment (Univision)", "TV segment with a 10-second product insert", "3 May 2026",
         "Same remittance chassis: three-button welcome, list picker, RESUMEN with itemised fees, Completar pago", "Video"],
        ["Félix's recarga launch video (CEO Manuel Godoy)", "Talking head with an illegible phone insert and step overlays", "27 Jul 2026",
         "Three-step marketing framing: escribir Recarga, compartir el teléfono, confirmar la operación", "Video"],
        ["the Instagram carrier carousel (6 slides)", "Designed composites", "30 Jul 2026",
         "Carrier logos for 9 countries; a mock of steps 1 to 4 whose copy matches production", "Mock"],
        ["the X launch carousel (4 slides)", "Designed composites with Stripe test data", "21 Aug 2026",
         "Entry and number prompt; checkout mock with saved card and the Unlimited GB 2 Hours SKU", "Mock"],
        ["Help centre and guide pages (3 recarga pages)", "Text", "Live, captured 10 Sep 2026",
         "Step list, product types, no-refund rule, confirmation promise, Boss Revolution named as a comparator", "Documented"],
        ["31 further public videos (official channel, TikTok, third-party walkthroughs, Finovate 2025 demo)",
         "Screen recordings, ads, interviews", "2022 to 2026",
         "Bot evolution since 2022, fee history, limits, onboarding, cancel and receive-side flows", "Video"],
        ["App Store listing and Google Play listing", "Store screenshots", "Captured 9 Sep 2026",
         "Native app is a companion (rates, alerts, referral); no recarga surface", "Mock"],
    ]),
    ("CHASSIS", [
        ["Pattern seen in the remittance recordings", "Evidence", "Carried into recarga?", "So what for BR"],
        ["Entry from the website with a prefilled WhatsApp message and a full-screen redirect interstitial",
         "Tutorial 12 to 15 s; production recarga step 1 shows the same bold prefilled message",
         "Yes: the recarga entry is a prefilled deep-link message, not a typed keyword",
         "Design the web-to-WhatsApp hand-off, not only the in-thread keyword"],
        ["Welcome message leads with today's FX rate, then exactly three quick replies",
         "Tutorial 16 s; Despierta América 4:06; the 2022 brand spot shows the same shape with Ver tipo de cambio as a button",
         "Recarga is reached by keyword, not from the three buttons",
         "Three-button cap forces a hierarchy; recarga is not yet on Félix's front door"],
        ["Free text only where a number is needed (amount, phone number); everything else is a button or a list",
         "Tutorial 20 to 33 s; production steps 4 to 8",
         "Yes: the phone number is the only free-text step in recarga",
         "Match this: free text for capture, structured replies for choices"],
        ["Saved beneficiaries as a list picker with Nuevo beneficiario on top",
         "Tutorial 19 s",
         "Not observed: recarga starts from a blank number prompt every time",
         "Saved recipients are BR's largest available advantage in the thread"],
        ["RESUMEN block in monospace section headers with itemised fees and a Sí, correcto / Cambiar algo pair",
         "Tutorial 33 s; production RESUMEN DE RECARGA step 7",
         "Yes, same component, with Comisión Félix shown as $0.00 in the recarga checkout",
         "Reuse one summary component across products; show fee even when zero"],
        ["Payment hand-off through a CTA URL button to a Félix-hosted page",
         "Tutorial 35 s (Completar pago); production step 8 (Pagar recarga)",
         "Yes: opens inside WhatsApp's in-app browser (Done / WhatsApp title bar visible)",
         "Plan for the in-app browser, not for a full browser exit"],
        ["Hosted checkout re-states the summary, re-uses a saved card, asks for CVV",
         "Tutorial 36 to 39 s (pay.felixpago.com, card ending 1084)",
         "Recarga checkout collects the full card (Número de tarjeta, MM / AA); saved-card reuse only in the X mock",
         "Card-on-file plus CVV is Félix's repeat-purchase pattern; recarga may still be on first-card entry"],
        ["Success page on the web with an availability estimate, then Volver a WhatsApp and a referral offer",
         "Tutorial 40 to 41 s",
         "Not observed for recarga",
         "The receipt moment is where Félix is thinnest; BR can win it"],
    ]),
    ("MARKETING_VS_PRODUCT", [
        ["Marketing says", "Where", "The shipped bot does", "Evidence"],
        ["Escribe recarga en tu chat de Félix (type one word)", "Help centre, X, Instagram, launch video",
         "Félix's own capture starts with a bold prefilled message, Quiero hacer una “recarga telefónica”, which is what a wa.me deep link produces. Typing the keyword is plausible but not what is shown.", "Real"],
        ["Choose the country and the operator, then enter the number", "Help centre step list and guide",
         "Number first; country and carrier are detected from it and confirmed with Sí, continuar / Cambiar compañía", "Real"],
        ["Amount in dollars ($20 USD, $20 por favor)", "Help-centre hero images",
         "Amount in the recipient's currency (COP) with an estimated FX rate; the USD total appears only in the summary", "Real"],
        ["Recarga enviada con éxito inside the chat", "Help-centre hero image",
         "No in-chat success message has ever been shown; the only success screen on record is the remittance web page", "Documented"],
        ["Three steps: escribir, compartir el teléfono, confirmar", "Launch video overlays",
         "Twelve distinct screen states, including a browser hand-off and card entry", "Real"],
        ["Comparte el número y elige el monto with a saved card", "the X launch carousel",
         "The production checkout asks for the card number and expiry; the saved-card state exists only in the mock (card 4242)", "Mock"],
        ["Félix chat drawn from Félix's side, human avatar, free-text conversation", "Help-centre and third-party explainers",
         "Button and list driven; free text only for the number and, in remittances, the amount", "Video"],
    ]),
    ("FX", [
        ["Screen", "Rate shown", "What it implies"],
        ["Amount prompt (step 6)", "Tipo de cambio estimado: ~3225.81 COP/USD", "Quoted before the amount is chosen; labelled an estimate, total confirmed at payment"],
        ["RESUMEN DE RECARGA (step 7)", "~3208.56 COP/USD", "Exactly 6000 / 1.87, so it is back-computed from the rounded USD price"],
        ["Hosted checkout (step 9)", "TC: 3211.78 COP/USD", "6000 / 3211.78 = 1.868, still displayed as $1.87"],
        ["X carousel mock", "TC: 3211.78 COP/USD", "Same figure as the production checkout, so the mock was built from a real session"],
        ["Comisión Félix", "$0.00 USD on every screen", "With no fee, the margin can only sit in the FX rate and the rounding"],
    ]),
    ("BENCHMARK", [
        ["Dimension", "Félix recarga (observed)", "BOSS Revolution IMTU (today)", "Read"],
        ["Channel", "WhatsApp thread plus in-app browser checkout; native app is a companion only",
         "BR7 app and web; WhatsApp is unbuilt candidate A8", "Félix owns the channel BR lacks; BR owns the product depth Félix lacks"],
        ["Entry", "Deep link with prefilled message from the website, or keyword recarga in an existing chat",
         "App tile, MTU home", "BR needs both a web-to-WhatsApp hand-off and an in-thread keyword"],
        ["Identity", "WhatsApp number is the identity; recarga starts from a blank number prompt",
         "Logged-in account with saved recipients and history", "Largest conversion gap available to BR in the thread"],
        ["Recipient capture", "Free-text E.164 number with country code, example shown",
         "Contact picker or typed number", "Adopt the example line and the country-code requirement"],
        ["Carrier resolution", "Detect from the number, then confirm, with an explicit Cambiar compañía override",
         "Carrier detection with known portability failures; drives BLS promo eligibility", "Adopt detect-then-confirm; it de-risks carrier-scoped promos"],
        ["Product selection", "Type first (datos, paquete, saldo libre), then three popular amounts plus a list for the rest",
         "Denomination grid; data bundles limited", "Félix sells a data bundle in its own demo; BR's data gap is visible"],
        ["Currency", "Recipient currency, FX estimated, USD total confirmed at payment",
         "USD price with delivered local amount", "Both are defensible; Félix's approach hides the USD price until step 7"],
        ["Fee display", "Comisión Félix $0.00 on the summary and checkout", "Fee plus promotional bonus airtime", "Félix has no promo mechanic at all; BR's BLS bonus is unmatched"],
        ["Payment", "Card entry on a hosted page inside WhatsApp's in-app browser; no Apple Pay or Google Pay seen",
         "Saved cards, wallets, in-app", "In-app browser, not a browser exit, is the realistic funnel break to measure"],
        ["Receipt", "Remittances: receipt image in the thread with the pickup reference as hero, plus an email receipt. Recarga: promised, never shown",
         "Itemised receipt with reference number and delivery state", "Félix has the receipt primitive; whether recarga uses it is unknown"],
        ["Delivery proof", "Carrier SMS to the recipient; en cuestión de minutos", "Delivery-confirmed state", "Same as above"],
        ["Refund", "Wrong number: sin posibilidad de reembolso; no top-up refund path published", "Refund path exists", "Same as above"],
        ["Support", "Hablar con agente keyword in the same thread, 24/7", "In-app help, CSA", "One thread for commerce and support is convenient and an impersonation risk"],
    ]),
    ("DECISIONS", [
        ["Decision for the BR WhatsApp IMTU flow", "Evidence from Félix", "Recommendation"],
        ["Where payment happens", "CTA URL button opens payments-ui.prod.fpago.com inside WhatsApp's in-app browser with Regresar a WhatsApp",
         "Adopt"],
        ["Carrier handling", "Detecté que … es un número de Claro Colombia. ¿Continuamos? with Cambiar compañía", "Adopt"],
        ["Amount picker shape", "Three quick replies for popular amounts plus an Opciones list; the three-button cap is a platform limit",
         "Adopt"],
        ["Currency denomination", "Amounts in COP with an estimated FX; USD total appears only in the summary", "Adapt"],
        ["Entry", "Prefilled deep-link message from the website; keyword in an existing thread", "Adapt"],
        ["Starting from a blank number every time", "No saved-recipient list for recarga; remittances do have one", "Avoid"],
        ["Untranslated SKU names", "Producto: $6000 COP - Unlimited GB 2 Hours in a Spanish flow", "Avoid"],
        ["Receipt and delivery confirmation in the thread", "Promised in the help centre, never shown, no reference number", "Add"],
        ["Promotional airtime in the summary", "No promo mechanic anywhere in the recarga flow", "Add"],
        ["Refund and error copy", "No declined-card, unsupported-carrier or failed-delivery copy published", "Add"],
    ]),
    ("CORRECTIONS", [
        ["Claim in the August 2026 analysis", "What the real screens show", "Verdict"],
        ["Hosted checkout opens in the default browser, which Meta documents for CTA URL buttons",
         "Step 9 opens inside WhatsApp's in-app browser: the title bar reads WhatsApp with a Done control and the URL payments-ui.prod.fpago.com. "
         "The remittance tutorial also shows pay.felixpago.com in a Safari view. Treat the exit as an in-app browser, not a browser switch.", "Corrected"],
        ["Entry is the typed keyword recarga", "Félix's own capture opens with a bold prefilled message, Quiero hacer una “recarga telefónica”, "
         "which only a deep link produces. The keyword path is documented but not shown.", "Corrected"],
        ["Recharge types are datos, paquete, saldo libre", "The bot prompt is confirmed (¿Qué tipo de recarga quieres hacer…?) but the option "
         "buttons are still unseen. The demo transaction is Datos, a bundle named Unlimited GB 2 Hours.", "Still open"],
        ["Three quick replies plus an Opciones list at the amount step", "Confirmed verbatim: $4000 COP / $5000 COP / $6000 COP and "
         "Elegir un monto diferente: Opciones.", "Confirmed"],
        ["RESUMEN DE RECARGA lists número, país, compañía, producto, total, tipo de cambio", "Confirmed, with the added finding that the "
         "rate on the summary is back-computed from the rounded USD price.", "Confirmed"],
        ["No receipt or reference number", "Corrected for remittances: a real March 2026 transfer ends with a WhatsApp receipt image whose hero is "
         "the pickup reference number, plus an email receipt, and the Terms guarantee a Número de referencia de la transacción on every confirmation. "
         "Still unobserved for recarga.", "Corrected"],
        ["Whether KYC fires mid-flow", "New: for a first-time remittance the bot asks nothing; identity (name, date of birth, email) and billing "
         "address are collected as a three-step form inside the hosted checkout. Recarga not yet observed.", "New"],
        ["Card only, no Apple Pay or Google Pay", "No wallet button on any checkout screen in 2026 footage.", "Confirmed"],
        ["Félix names Boss Revolution in its guide", "Confirmed on the live guide page on 10 Sep 2026.", "Confirmed"],
        ["The corridor demonstrated is Colombia despite Mexico being the marketed corridor", "Confirmed: every real capture is a Claro Colombia "
         "number; the bot example is +52 and the marketed carriers are Telcel, Movistar, AT&T.", "Confirmed"],
        ["Recarga is a launched product", "New: dated to 27 Jul 2026 (launch video), 30 Jul 2026 (Instagram) and 21 Aug 2026 (X); "
         "the help-centre pages call it available hoy mismo.", "New"],
    ]),
]

# ------------------------------------------------------------------ BLOCKS ----
BLOCKS = [
    ("h1", TITLE),

    # ------------------------------------------------------------ 1 --------
    ("h2", "1. Summary"),
    ("p", "The August analysis reconstructed Félix's WhatsApp top-up from documentation. This rebuild starts from the screens. "
          "Félix's own recargas landing page carries three real WhatsApp iOS captures of the production bot, its May 2026 tutorial "
          "is a 1080p screen recording of the remittance flow that the recarga rides on, and its launch carousels on X and Instagram "
          "show how Félix wants the flow to be seen. Together they put real screens behind nine of the twelve steps in the journey."),
    ("b", "The spine held up  ::  entry, number prompt, detect-then-confirm carrier resolution, structured amount picker, RESUMEN card, "
          "confirmation gate, CTA hand-off and hosted checkout all appear on Félix's production screens with the copy the August doc predicted."),
    ("b", "Two corrections matter for BR  ::  the checkout opens inside WhatsApp's in-app browser (title bar WhatsApp, Done control), not in "
          "the default browser; and Félix's own entry is a prefilled deep-link message, not a typed keyword. Both change how the BR "
          "hand-offs should be designed and measured."),
    ("b", "Post-payment is dark for recarga, lit for remittances  ::  no recarga payment result, confirmation, receipt or delivery message exists on "
          "any screen. For remittances a real user's recording shows the shape Félix already has: a web success page, an email receipt, and a "
          "WhatsApp receipt image whose hero is the pickup reference number. Whether recarga inherited that receipt is the biggest open question."),
    ("b", "Identity is collected at checkout, not in the chat  ::  in the only real first-time transfer on record, the bot asked no identity "
          "questions; name, date of birth, email and billing address were collected as a three-step form inside the payment page. The WhatsApp "
          "in-app browser also shows a one-time Securely browse this business website consent sheet on first use."),
    ("b", "The economics are visible  ::  COP 6,000 of Claro Colombia data (Unlimited GB 2 Hours) costs $1.87 with Comisión Félix $0.00. "
          "Three different COP/USD rates appear across three screens (3225.81, 3208.56, 3211.78), so the margin sits in FX and rounding."),
    ("b", "Recarga is new and still marketed as a side door  ::  launched 27 Jul 2026, reached only by keyword, absent from the three-button "
          "welcome menu and from the native app. Félix has no saved-recipient list for it and no promotional mechanic anywhere in the flow."),
    ("b", "For BR  ::  adopt the detect-then-confirm carrier step, the three-plus-list amount picker and the in-app-browser hand-off; "
          "beat Félix on identity (saved recipients), promotions (BLS bonus in the summary) and the post-purchase receipt. "
          "Detailed decisions are in section 9."),

    # ------------------------------------------------------------ 2 --------
    ("h2", "2. Evidence base and method"),
    ("p", "Everything below was gathered from public sources between 9 and 10 September 2026. No Félix account was created and no "
          "transaction was run, so every claim is graded by the kind of evidence behind it."),
    ("b", "Real  ::  a production WhatsApp capture published by Félix. Tells: Meta verified badge, real unread counts and battery levels, "
          "native quick-reply and list rendering, the prod hostname payments-ui.prod.fpago.com."),
    ("b", "Video  ::  a frame from a public screen recording of the live bot. All are remittance flows; none is a recarga."),
    ("b", "Mock  ::  a designed composite from Félix's marketing. Tells: placeholder numbers, Stripe's 4242 test card, timestamps that run backwards."),
    ("b", "Documented  ::  stated in Félix's help centre or guide but never seen on a screen."),
    ("table", "EVIDENCE"),
    ("p", "Videos were downloaded, cut into one-frame-per-second contact sheets and read frame by frame; every distinct screen state was "
          "extracted at full resolution and transcribed verbatim. Static images were catalogued and then re-read by a second, adversarial "
          "pass that challenged the transcription, the authenticity call and the privacy flags. The recipient number that appears in Félix's "
          "production captures is a plausible live Claro Colombia line and is redacted throughout; the marketing mocks use placeholders "
          "and needed no redaction."),

    # ------------------------------------------------------------ 3 --------
    ("h2", "3. The recarga journey, screen by screen"),
    ("p", "Twelve distinct states, in the order the sender meets them. Spanish copy is quoted verbatim from the screens, including Félix's "
          "own typos. Steps 1 to 9 come from production captures; 10 to 12 are inferred from the remittance chassis and Félix's documentation."),

    ("h3", "3.1 Entry and number capture (steps 1 to 3)"),
    ("image", "IMG_STEP1"),
    ("quote", "User: Quiero hacer una “recarga telefónica”                                   3:57 PM ✓✓"),
    ("quote", "Bot: ¿A qué número quieres mandar la recarga? Incluye el código de país.\n| Ejemplo: +52 1234567890                                        3:57 PM"),
    ("quote", "User: +57 ••• ••• ••••                                                         4:00 PM ✓✓"),
    ("p", "Entry  ::  the opening message is bold and wrapped in curly quotes. WhatsApp renders that only when the sent text carries asterisks, "
          "which a person does not type: this is a wa.me deep link with prefilled text, the same mechanism the remittance tutorial shows behind "
          "the website's Empezar envío sin comisión button. Félix's caption, Escribe recarga en tu chat de Félix, describes the second entry path, "
          "typing the keyword into an existing thread. Both exist; only the deep link is on a real screen."),
    ("p", "Number prompt  ::  one free-text question with an inline example and an explicit country-code requirement. There is no country picker "
          "and no carrier picker before the number. The example is Mexican (+52) even though every real capture is Colombian, which says "
          "Mexico is the corridor Félix designs for and Colombia is where the team happened to test."),
    ("p", "What the marketing adds  ::  the Instagram and X carousels restage this exact exchange as designed mocks. Their bot copy is "
          "identical to the production capture, so they are useful for reading the copy in clean type, but their timestamps run backwards "
          "and the X version has the sender typing a full sentence, Quiero hacer una “recarga”, which suggests the bot matches the keyword "
          "inside free text rather than requiring a bare command."),
    ("image", "IMG_IG_MOCK"),
    ("image", "IMG_X_MOCK_CHAT"),
    ("p", "The launch video  ::  Manuel Godoy's 27 July 2026 announcement compresses the flow into three overlays, Escribir la palabra Recarga, "
          "Compartir el teléfono del que quieres enviarle saldo, Confirmar la operación, and states that recarga is available in every country "
          "where Félix already operates. The phone in the insert is too small to read; it adds a date and a framing, not a screen."),
    ("image", "IMG_LAUNCH1"),
    ("image", "IMG_LAUNCH2"),
    ("image", "IMG_LAUNCH3"),

    ("h3", "3.2 Carrier detection and recharge type (steps 4 to 5)"),
    ("quote", "Bot: 📶 Detecté que ••• ••• •••• (Colombia) es un número de Claro Colombia.\n\n¿Continuamos?                                                        4:00 PM\n[ Sí, continuar ]   [ Cambiar compañía ]"),
    ("quote", "User: Sí, continuar                                                             4:00 PM ✓✓"),
    ("quote", "Bot: 📱 Perfecto. ¿Qué tipo de recarga quieres hacer a tu numero Claro Colombia?"),
    ("p", "Detect, then confirm  ::  country and carrier are inferred from the number (the 313 prefix is a Claro Colombia range) and put "
          "back to the sender as a yes-or-change question. This is the single most portable pattern in the flow. Félix does not run an HLR "
          "lookup and does not pretend detection is certain; it lets the customer override. For BR, whose carrier-scoped BLS promos break on "
          "ported numbers, this is the mechanism that makes showing a promo in a conversational surface safe."),
    ("p", "Recharge type  ::  the prompt is confirmed on a real screen, with the accent missing from numero. The option buttons themselves "
          "are cut off in every published capture. The help centre lists datos, paquete o saldo libre; the second capture shows the sender "
          "chose Datos. Whether the list is three fixed buttons or varies by carrier is still unknown."),
    ("p", "Two sessions  ::  the first capture runs 3:57 to 4:01 PM on a phone at 94% battery with 32 unread chats; the second runs 5:40 to "
          "5:44 PM at 34% with 26 unread. Félix's tutorial was stitched from at least two sessions, and the type-selection screen fell between them."),

    ("h3", "3.3 Amount, denominated in the recipient's currency (step 6)"),
    ("image", "IMG_STEP2"),
    ("quote", "Bot: 📱 De acuerdo, vamos a mandar Datos a tu Claro Colombia. ¿Cuánto quieres mandar?\nTipo de cambio estimado: ~3225.81 COP/USD. El total final en USD se confirma al pagar.\n\nOpciones populares 👇                                              5:40 PM\n[ $4000 COP ]   [ $5000 COP ]   [ $6000 COP ]"),
    ("quote", "Bot: Elegir un monto diferente:                                        5:40 PM\n[ ≡ Opciones ]"),
    ("quote", "User: $6000 COP                                                                 5:40 PM ✓✓"),
    ("p", "Three buttons plus a list  ::  WhatsApp caps quick replies at three per message, so Félix splits the step into a three-button "
          "message of popular amounts and a separate list message for everything else. The list contents were never captured."),
    ("p", "Recipient currency first  ::  the sender picks a COP amount before seeing a USD price. The FX is labelled an estimate and the "
          "USD total is deferred to payment. This is the opposite of BR's USD-first denomination grid, and it means the sender commits to a "
          "foreign-currency amount without knowing what the card will be charged until step 7."),

    ("h3", "3.4 Summary, confirmation, hand-off and checkout (steps 7 to 9)"),
    ("image", "IMG_STEP3"),
    ("quote", "Bot: 🧾 RESUMEN DE RECARGA\nNúmero: ••• ••• ••••\nPaís: Colombia\nCompañía: Claro Colombia\nProducto: $6000 COP - Unlimited GB 2 Hours\nTotal a pagar: $1.87 USD\nTipo de cambio: ~3208.56 COP/USD\n\n¿Confirmas esta recarga?                                             5:40 PM\n[ Confirmar recarga ]   [ Cambiar algo ]"),
    ("quote", "User: Confirmar recarga                                                         5:40 PM ✓✓"),
    ("quote", "Bot: Listo. Completa tu pago en este sitio seguro para enviar la recarga.\n[ ↗ Pagar recarga ]"),
    ("quote", "Web: Done                    WhatsApp · payments-ui.prod.fpago.com\nFélix recargas                              [ Regresar a WhatsApp ]\nResumen de tu recarga\nNúmero            ••• ••• ••••\nCompañía          Claro Colombia\nPaquete           Unlimited GB 2 Hours\nRecibes           COP 6,000.00 COP\nComisión Félix    $0.00 USD\nTotal a pagar     $1.87 USD\n                  TC: 3211.78 COP/USD\nMétodo de pago\nNúmero de tarjeta                 MM / AA\n[ Pagar ]"),
    ("p", "The summary  ::  the first place the USD figure appears. It is the same RESUMEN component the remittance bot uses (monospace section "
          "header, bold values), which is a good sign for BR: one summary primitive can serve every product in the thread."),
    ("p", "The gate  ::  Confirmar recarga / Cambiar algo is a genuine escape hatch before the irreversible step. What Cambiar algo does was never captured."),
    ("p", "The hand-off  ::  a CTA URL button. On the real screen it opens inside WhatsApp's in-app browser: the title bar reads WhatsApp with a "
          "Done control and the address payments-ui.prod.fpago.com, and the page itself offers Regresar a WhatsApp. This corrects the August "
          "doc's assumption of a default-browser exit. The sender never leaves the WhatsApp app, but does leave the thread."),
    ("p", "The checkout  ::  re-states the summary, adds the explicit Comisión Félix $0.00 USD line and a slightly different rate (TC: 3211.78), "
          "then asks for the card number and expiry. Card details are never typed into the chat. Félix's own capture blurs an element between "
          "the card fields and the Pagar button (likely a CVV or cardholder field). Copy defects on this screen: Recibes COP 6,000.00 COP repeats "
          "the currency code, the SKU is untranslated English, and the number is shown as +57 573134299124 with the country code doubled."),
    ("p", "The X mock of this screen  ::  shows a saved card ending 4242 (Stripe's public test card) with no CVV field and a 10:06 status bar. "
          "It confirms the layout and the SKU, and it hints that repeat buyers see a card-on-file state, but it is not a production capture."),
    ("image", "IMG_X_MOCK_CHECKOUT"),

    ("h3", "3.5 Payment result, confirmation and delivery (steps 10 to 12)"),
    ("p", "No recarga screen exists for anything after Pagar. The best available evidence is the remittance flow in Félix's May 2026 tutorial, "
          "which runs on the same bot and the same checkout family. Treat the four screens below as the likely shape, not as recarga fact."),
    ("image", "IMG_TUT07"),
    ("image", "IMG_TUT08"),
    ("image", "IMG_TUT09"),
    ("image", "IMG_TUT10"),
    ("quote", "Bot: Para continuar con tu envío, completa tu pago en el siguiente enlace. 🔒\nPícale al botón abajo                                              8:38 a.m.\n[ ↗ Completar pago ]"),
    ("quote", "Web: pay.felixpago.com · An authorized agent of UniTeller\nRevisa los detalles de tu envío para Daniel Rangel\nTú envías USD $20.00 · Tu beneficiario recibe MXN $401.00\nEstás pagando con  •••• 1084   Cambiar\nMonto a enviar + Comisiones   USD $24.98\n[ Enviar ahora ]"),
    ("quote", "Web: Código de seguridad\nPara continuar con tu envío, introduce el código de seguridad (CVV) que está en el reverso de tu tarjeta CARD .... 1084\n[ CVV ]   [ Confirmar ]"),
    ("quote", "Web: ¡Listo! Tu pago se completó con éxito.\nTu envío de $20 USD, convertidos en $401 MXN, estará disponible para Daniel Rangel en aproximadamente 30 minutos.\nGana hasta $500 USD · Obtén $20 dólares por cada amigo que recomiendes\n[ Recomendar por WhatsApp ]        (earlier frame: [ Volver a WhatsApp ])"),
    ("p", "Payment result  ::  a web page, not a WhatsApp message. It confirms the charge, gives an availability estimate, and immediately pivots "
          "to referral. No reference number appears on the page itself."),
    ("p", "What a real first-time sender actually saw  ::  the only unscripted, end-to-end recording in the corpus is an independent creator's "
          "$150 cash-pickup transfer to El Salvador in March 2026. It fills in the post-payment shape for remittances and shows where identity is collected."),
    ("image", "IMG_REAL01"),
    ("image", "IMG_REAL02"),
    ("image", "IMG_REAL03"),
    ("image", "IMG_REAL04"),
    ("quote", "User: 039925H7 ¡Hola Félix! Quiero hacer un envío de dinero a El Salvador                                  12:25 PM ✓✓"),
    ("quote", "Bot: Bienvenido a Félix, la forma más fácil y rápida de enviar dinero a México 🇲🇽 desde WhatsApp.\nHaz click en el botón para iniciar tu envío, nuestro chat te guiará paso a paso.\nTu promoción se verá reflejada al momento de confirmar los datos de la transacción.        12:25 PM\n[ Enviar dinero 💸 ]   [ Más información ]   [ Enviar a otro país ]"),
    ("quote", "Bot: 🧾 RESUMEN\nMonto: $150 dólares\nPromoción: Comisión gratis\n🏦 DESTINO\nA: [recipient name]\nEn: [town], SV-US\nTienda: Super Selectos\n🪙 TARIFAS\nComisión: $0 dólares\n💵 TOTAL A PAGAR\n$150 + $0 = $150 dólares                                              12:27 PM\n[ Sí, correcto 👍 ]   [ Cambiar algo ]   [ Nuestra comisión ]"),
    ("quote", "Bot: Para continuar con tu envío, completa tu pago entrando a la siguiente liga segura y confidencial para ingresar tus datos. 🔒\n| Toca al botón abajo                                                12:27 PM\n[ ↗ Completar pago ]"),
    ("quote", "Web: Done · WhatsApp · pay.felixpago.com\n¡Estás a punto de completar tu envío a [recipient]!\n¿Cómo deseas pagar?\nTarjeta de crédito/débito →  Las tarjetas de crédito pueden incurrir en tarifas adicionales según el emisor.\n[ Sin comisión extra para débito ]\nPago seguro y encriptado · Este es un pago seguro encriptado con SSL de 256 bits."),
    ("quote", "Web: 1 de 3 · ★ Desbloquea más beneficios · Verifica tu identidad de forma fácil y segura >\nCuéntanos más sobre ti\nNombre * · Segundo nombre · Apellido Paterno * · Apellido Materno · Fecha de nacimiento * · Correo electrónico *\nPor favor completa con tu información personal tal y como aparece en tu ID.\n2 de 3 · Ingresa la dirección vinculada a tu tarjeta · 3 de 3 · card, then CVV modal"),
    ("quote", "Bot: ¡Tu envío está siendo procesado! En un momento te enviamos tu recibo por email 📧            12:31 PM\n[ receipt image: reference number as hero · one line on presenting the reference at the store · amount, 30 minutos, Super Selectos, recipient · ¡Ahorraste $… USD ]"),
    ("p", "Entry  ::  the deep link carries an eight-character session token ahead of the greeting, so the bot can tie the chat to the web session "
          "(corridor, amount, promo eligibility). The welcome still defaults to Mexico even though the token said El Salvador, which costs the sender "
          "an extra Enviar a otro país step and a seven-country list picker. WhatsApp itself inserts the notice This business uses a secure service "
          "from Meta to manage this chat, and on the first CTA tap shows a Securely browse this business website sheet before the in-app browser opens."),
    ("p", "Identity  ::  no KYC question is asked in the thread. Name (split into paternal and maternal surnames), date of birth and email, then the "
          "billing address, then the card are collected as 1 de 3, 2 de 3, 3 de 3 inside pay.felixpago.com after the transfer is fully specified, "
          "with an optional Verifica tu identidad tier offered above the form. Payment is card only; credit cards carry an issuer-fee warning and "
          "debit is flagged Sin comisión extra."),
    ("p", "WhatsApp confirmation  ::  seconds after the charge, three artefacts arrive: the web success page, an email titled Recibo de transacción, "
          "and in the thread a bot line, ¡Tu envío está siendo procesado! En un momento te enviamos tu recibo por email, followed by a receipt image "
          "whose hero is the cash-pickup reference number, with a savings chip (¡Ahorraste …) and small-print rows. Félix's Terms of Use state that "
          "every order receives a unique Número de referencia de la transacción shown on the confirmation. For recarga, where there is no pickup "
          "code to display, whether this receipt image exists at all is the open question that matters most."),
    ("p", "After the transaction  ::  later B-roll shows the bot pushing a $20 referral credit and then asking ¿Qué tan probable es que recomiendes "
          "Félix? on a 1 to 10 list picker; the creator started typing a free-text answer instead, a hint that list prompts get typed replies in practice."),
    ("p", "Delivery  ::  El saldo se acredita en la línea de tu familiar, generalmente en minutos. La operadora le envía a tu familiar un mensaje "
          "confirmando la recarga. Félix leans on the carrier's SMS as delivery proof rather than issuing its own delivered-state message."),
    ("p", "The irreversibility rule  ::  un número equivocado suele acreditar el saldo a otra línea sin posibilidad de reembolso, and una vez procesada "
          "la recarga, no hay forma de corregir un error en estos datos. No refund path for a Félix-side or carrier-side failure is published anywhere."),

    ("h3", "3.6 The journey on one page"),
    ("image", "IMG_DIAGRAM"),

    # ------------------------------------------------------------ 4 --------
    ("h2", "4. The chassis underneath: what the remittance recordings prove"),
    ("p", "Félix built recarga on the bot it already had. The May 2026 tutorial is the only 1080p screen recording of that bot, so it is the "
          "clearest view of the mechanics the recarga inherits and the ones it does not yet have."),
    ("image", "IMG_TUT01"),
    ("image", "IMG_TUT02"),
    ("image", "IMG_TUT03"),
    ("image", "IMG_TUT04"),
    ("image", "IMG_TUT05"),
    ("image", "IMG_TUT06"),
    ("quote", "Web: Destino  Enviar a México\n¿Cuánto quieres enviar?  200 USD\n¿Cuánto quieres que reciban?  3,494.00 MXN\nTasa de cambio promocional  1 USD = 17.47 MXN\nComisión  Gratis · Te ahorras hoy  -$2.99 USD\n☑ Me gustaría recibir información de Félix a traves de mensajes de texto. (SMS)\n[ Empezar envío sin comisión ]"),
    ("quote", "Bot: El tipo de cambio de hoy es $20.05 pesos por dólar.\n\nPor favor selecciona una de las opciones para continuar 👇          8:37 a.m.\n[ Enviar dinero ]   [ Refiere y gana ]   [ Otras opciones ]"),
    ("quote", "Bot: ¿Cuánto quieres enviar? 💰\nEl tipo de cambio es $20.05.\n| Ejemplo: 100 dólares ó 2005 pesos"),
    ("quote", "User: 20"),
    ("quote", "Bot: Tu beneficiario recibirá $401.00 MXN.\n¿A quién le quieres enviar dinero? 🎁 Selecciona el nombre en las opciones 👇\n[ ≡ Opciones ]  →  Nuevo beneficiario · Alejandra Ramírez · Daniel Rangel ✓ · María Quintero · Rosalba Quintero"),
    ("quote", "Bot: ¿Cómo quieres que Daniel Rodrigo Rangel Quintero reciba su dinero? 💰\n[ ≡ Opciones ]  →  Walmart · Elektra · Oxxo · Soriana · Nuevo método"),
    ("quote", "Bot: 🧾 RESUMEN\nMonto: $401.00 MXN ($20.00 USD)\nTasa: $20.05 MXN/USD\n🏦 DESTINO\nA: Daniel Rodrigo Rangel Quintero\nEn: Ciudad de México, MX-MEX\nTienda: Oxxo\n🪙 TARIFAS\nComisión: $2.99\nComisión por tienda: $1.99\n💵 TOTAL A PAGAR\n$20.00 + $4.98 = $24.98                                              8:38 a.m.\n[ Sí, correcto 👍 ]   [ Cambiar algo ]"),
    ("table", "CHASSIS"),
    ("p", "One inconsistency worth noting  ::  the tutorial's web calculator advertises Comisión Gratis and Te ahorras hoy -$2.99 USD for the first "
          "send, but the chat RESUMEN in the same video charges $2.99 plus $1.99 for cash pickup, a 24.9% all-in cost on a $20 send. Félix's "
          "zero-fee promise is a first-send promotion on the remittance side and a standing claim on the recarga side."),

    ("h3", "4.1 What the wider video corpus adds"),
    ("p", "Thirty-one further videos were downloaded and read, from Félix's first 2022 explainer to third-party walkthroughs and a Finovate 2025 "
          "stage demo; fourteen were catalogued screen by screen before the cataloguing budget ran out, and the rest were scanned on contact sheets. "
          "Most are talking-head ads with no screens. The screen-bearing ones establish how the bot has evolved and what Félix says about limits, "
          "fees, cancellation and support."),
    ("b", "The welcome message has been a three-button interactive message since 2022  ::  the 2022 brand spot shows Enviar dinero, Más información "
          "and Ver tipo de cambio under a $2.99 fee claim; the 2023 bot had two buttons and a Mexico-only flow; by 2026 the buttons are Enviar dinero, "
          "Refiere y gana, Otras opciones (or Enviar a otro país for deep-link arrivals) and the FX rate leads the body. Recarga has not earned a button."),
    ("b", "Fee history  ::  a flat $2.99 to Mexico in December 2022, no importa cuánto envíes; $2.99 plus a $1.99 store fee for cash pickup in 2026; "
          "first-send incentives that vary by placement ($15 extra, $20 free, $0 commission). The recarga is the first Félix product marketed with "
          "no fee at all rather than a waived first fee."),
    ("b", "Limits stated in Félix's own 2024 infographic  ::  $1,000 per transaction, $3,000 per week, $12,000 per month; the Nexa partner page "
          "quotes a $10,000 monthly receive limit. Whether recargas count against these is undocumented."),
    ("b", "Cancellation rights are in the Terms, not the bot  ::  a personal transfer can be cancelled for a full refund including fees within 30 "
          "minutes of payment, via WhatsApp or by email or phone, quoting the reference number; the refund is issued within three business days unless "
          "the recipient has already collected. The Terms never mention recargas, and Félix's help centre says a processed recarga cannot be corrected."),
    ("b", "Every payment link expires  ::  a 2025 brand video lists CADA LINK DE PAGO TIENE TIEMPO DE EXPIRACIÓN as a security feature, so the "
          "Pagar recarga button is time-boxed; the expiry copy and the recovery path were never captured."),
    ("b", "Support is a keyword  ::  Necesito ayuda or Hablar con un agente typed in the thread reaches 24/7 human support; no phone number or web "
          "help path is shown in any 2025 or 2026 asset."),
    ("b", "Two other Félix models exist beside the consumer bot  ::  the Finovate 2025 demo shows an embedded flow where a partner bank app deep-links "
          "into WhatsApp with a token, the bot debits the bank account on Confirmar Pago and posts ¡Tu pago fue exitoso! inside the chat, with no hosted "
          "checkout at all. The June 2026 Nexa video shows a recipient-initiated request link (holafelix.com/request/…) generated in the recipient's "
          "Guatemalan wallet and shared over WhatsApp. Both matter for BR: the first proves Félix can close payment in-thread when the funding rail "
          "allows it, the second is Félix's version of BR's Request Top-Up."),
    ("b", "Brand-keyword conquesting is live  ::  in the March 2026 recording, Remitly ran App Store search ads on felix pago and Google ads headlined "
          "Enviar Dinero por WhatsApp, and Ria bid on the brand too. Google autocomplete for felix pago offered es seguro, reviews and reddit, so trust "
          "is the dominant pre-purchase question."),
    ("b", "Marketing consistently overstates the conversational feel  ::  third-party explainers and Félix's own hero images draw free-text chats "
          "answered like a human; every real recording is buttons and lists, with free text only for numbers, names and cities."),

    # ------------------------------------------------------------ 5 --------
    ("h2", "5. Marketing versus the shipped product"),
    ("p", "Félix's help-centre heroes, its carousels and its launch video describe a product that is simpler than the one on the screens. "
          "The gaps matter because BR will be benchmarked against the marketing version in any executive conversation."),
    ("table", "MARKETING_VS_PRODUCT"),

    # ------------------------------------------------------------ 6 --------
    ("h2", "6. Pricing, FX and the zero-commission claim"),
    ("p", "The single transaction Félix chose to publish is COP 6,000 of Claro Colombia data for $1.87. The landing page says Félix no cobra "
          "comisión por enviar una recarga internacional: solo pagas el monto de la recarga, al tipo de cambio que ves antes de confirmar, and "
          "promises el precio que revisas en el resumen es el mismo que terminas pagando."),
    ("table", "FX"),
    ("p", "What this means  ::  the sender sees three rates in one purchase, none of which is presented as the price. With the fee pinned at zero, "
          "the spread between Félix's rate and the mid-market COP/USD rate on the day is the entire margin. Félix's own guide coaches readers to "
          "compare providers on the saldo real que recibirá tu familiar rather than the headline price, and names Boss Revolution and Ding as the "
          "two best-known incumbents while doing so. BR should publish delivered-value comparisons before Félix's framing hardens."),
    ("p", "Face value or discount  ::  whether COP 6,000 of data is sold at face value is still unknown. A single live purchase on two or three "
          "corridors would settle it, and it needs prior approval before any card is charged."),

    # ------------------------------------------------------------ 7 --------
    ("h2", "7. Coverage: countries and carriers"),
    ("image", "IMG_IG_CARRIERS"),
    ("p", "The landing page claims Más de 40 empresas para recargar and availability in every country where Félix sends money. The Instagram "
          "carousel is the only place the carriers are listed."),
    ("b", "Mexico  ::  Telcel, AT&T, Bait, Unefon, Movistar, Oui, Virgin Mobile (seven brands, the only country with a full slide)."),
    ("b", "Guatemala, Honduras, Nicaragua  ::  Tigo, Claro. Costa Rica: Claro."),
    ("b", "Colombia  ::  Tigo, Claro, Movistar. Dominican Republic: Claro, Altice, Viva."),
    ("b", "Ecuador and Peru  ::  shown on the fifth slide (Claro and Movistar in Ecuador; Movistar, Entel and Bitel in Peru per the carousel)."),
    ("b", "Absent  ::  El Salvador does not appear on any carrier slide although it is a core Félix remittance corridor and a top US-Hispanic "
          "destination; Brazil, added to remittances in 2026, is also absent. Gaps to verify in the live bot: WOM and Virgin Mobile in Colombia, "
          "CNT in Ecuador, Kölbi and Liberty in Costa Rica."),

    # ------------------------------------------------------------ 8 --------
    ("h2", "8. Benchmark: Félix recarga versus BOSS Revolution IMTU"),
    ("table", "BENCHMARK"),
    ("image", "IMG_IOS"),

    # ------------------------------------------------------------ 9 --------
    ("h2", "9. Implications for the BOSS Revolution WhatsApp IMTU flow"),
    ("p", "Initiative A8 in the IMTU FY27 Plan proposes WhatsApp as a transaction surface. The real Félix screens narrow the design space "
          "considerably: the platform's three-button cap, the in-app browser hand-off and the free-text-only-for-numbers rule are constraints, "
          "not Félix choices, and any BR flow will face them too."),
    ("table", "DECISIONS"),
    ("h3", "9.1 The three moves Félix cannot copy quickly"),
    ("p", "Identity  ::  Félix starts every recarga from a blank number prompt because the WhatsApp number is its whole identity model. BR can "
          "match the WhatsApp number to an account and open with saved recipients and a one-tap repeat, the same list-picker pattern Félix "
          "already uses for remittance beneficiaries. This depends on the cross-app identity work and is the largest conversion difference on the table."),
    ("p", "Promotions  ::  there is no promo mechanic on any Félix recarga screen. BR's BLS bonus airtime, shown inside the RESUMEN after a "
          "detect-then-confirm carrier step, is a visible advantage Félix cannot answer without building a pricing engine it does not have."),
    ("p", "Post-purchase  ::  Félix's flow ends on a web page with a referral offer and no reference number. An itemised receipt in the thread, a "
          "delivered-state message distinct from the payment confirmation, and an in-thread support hand-off would beat Félix on the dimension "
          "its own help centre is weakest on."),
    ("h3", "9.2 What to measure in a BR pilot, given the real hand-off"),
    ("b", "In-app browser open rate  ::  taps on the CTA URL button versus checkout page loads. Félix's hand-off stays inside WhatsApp, so the "
          "drop should be smaller than a browser switch, but it is still a context change."),
    ("b", "Return rate  ::  Regresar a WhatsApp and Volver a WhatsApp taps versus checkout completions. Félix offers the return link on both "
          "the checkout header and the success page."),
    ("b", "Free-text failure rate at the number prompt  ::  the only free-text step; Félix's example line and country-code requirement are the "
          "mitigation, and BR should log how often the number fails to parse."),
    ("b", "Override rate on Cambiar compañía  ::  a direct measure of carrier-detection accuracy and, for BR, of promo-eligibility risk."),

    # ------------------------------------------------------------ 10 -------
    ("h2", "10. Corrections to the August 2026 analysis"),
    ("p", "The earlier document, the August 2026 analysis, was built without real screens. Each of its material claims is checked below."),
    ("table", "CORRECTIONS"),

    # ------------------------------------------------------------ 11 -------
    ("h2", "11. Still unverified, and how to close it"),
    ("p", "Nine of twelve steps are now on real screens. The remaining gaps cluster after payment and around the error paths. One live "
          "top-up from a US number with a US card would close most of them in under an hour; it needs approval before any purchase is completed."),
    ("b", "The recharge-type buttons (step 5) and the Opciones list of denominations (step 6), per corridor and carrier."),
    ("b", "The payment result and the WhatsApp confirmation message for a recarga, including whether a reference number exists."),
    ("b", "Whether a first-time sender typing recarga is routed through onboarding or KYC before the number prompt, or whether identity is collected "
          "inside the checkout as it is for remittances (1 de 3, 2 de 3, 3 de 3)."),
    ("b", "Whether the recarga receives the same in-thread receipt image as a remittance, and what its hero is when there is no pickup code."),
    ("b", "The expiry window of the Pagar recarga link and the copy shown when it lapses."),
    ("b", "The full error taxonomy: malformed number, unsupported carrier or country, denomination unavailable, declined card, carrier failure after a successful charge."),
    ("b", "Whether a saved-number or repeat affordance appears for a second recarga."),
    ("b", "Whether top-ups are sold at face value, and the effective FX spread against mid-market on two or three corridors."),
    ("b", "Whether recargas count against the published send limits, and whether a recurring or scheduled recarga exists."),
    ("p", "Suggested protocol  ::  one Claro Colombia data recarga at the smallest denomination and one Telcel Mexico saldo recarga, captured "
          "as screen recordings from the deep link to the carrier SMS, with the card statement checked for the exact USD charge."),

    # ------------------------------------------------------------ 12 -------
    ("h2", "12. Sources"),
    ("b", "Félix recargas landing page (three production step images): https://www.felixpago.com/recargas-internacionales"),
    ("b", "Help centre, ¿Cómo enviar una recarga telefónica internacional con Félix?: https://www.felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional"),
    ("b", "Help centre, ¿Puedo enviar recargas a celulares con Félix?: https://www.felixpago.com/ayuda/puedo-enviar-recargas-a-celulares"),
    ("b", "Guide, Recargas internacionales (names Boss Revolution and Ding): https://www.felixpago.com/guias/recargas-internacionales"),
    ("b", "Launch video, Félix lanza Recargas Telefónicas, 27 Jul 2026: https://www.youtube.com/watch?v=hCliPe4-71w"),
    ("b", "Tutorial, Cómo enviar dinero por WhatsApp con Félix, 7 May 2026: https://www.youtube.com/watch?v=V7EJA0MV8fQ"),
    ("b", "Despierta América segment, 3 May 2026: https://www.youtube.com/watch?v=q7B_XdXNnnQ"),
    ("b", "Brand spot, ¡Envía dinero a México por WhatsApp!, 5 Dec 2022: https://www.youtube.com/watch?v=cokVPx6A394"),
    ("b", "Independent first transfer, Probando Felix Pago | ¿Funciona de verdad?, Inteligencia Económica, 24 Mar 2026: https://www.youtube.com/watch?v=n6QF6oaAISI"),
    ("b", "Cancellation terms walkthrough, Dinero Digital, 12 Jul 2025: https://www.youtube.com/watch?v=FlCvpicOwTQ"),
    ("b", "FinovateSpring 2025 demo (embedded Félix Send): https://www.youtube.com/watch?v=CIc0e46UGrI"),
    ("b", "Nexa request-link video, 10 Jun 2026: https://www.youtube.com/watch?v=LXk_aAZ5xqU"),
    ("b", "Security brand video with support keywords and link expiry, 21 Nov 2025: https://www.youtube.com/watch?v=nwxXznMqksw"),
    ("b", "Early tutorial (2023 UI generation), 2 Feb 2023: https://www.youtube.com/watch?v=RagAifMeRFQ"),
    ("b", "X carousel, 21 Aug 2026: https://x.com/Felixpago/status/2090884151939301454"),
    ("b", "Instagram carousel, 30 Jul 2026: https://www.instagram.com/p/DbbxTDwE7hJ/"),
    ("b", "iOS App Store listing: https://apps.apple.com/us/app/f%C3%A9lix-pago-env%C3%ADos-de-dinero/id6756128226"),
    ("b", "Google Play listing: https://play.google.com/store/apps/details?id=com.felixpago.felix&hl=es"),
    ("b", "Previous analysis, 29 Aug 2026: " + PREV_DOC),
    ("b", "Repository with the evidence images, catalogs and generators: https://github.com/tanaka-idt/IDT-Claude"),
]
