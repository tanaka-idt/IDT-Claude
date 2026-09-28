#!/usr/bin/env python3
"""
Single source of truth for the Felix Pago WhatsApp top-up teardown (September 2026).

Consumed by:
  create_felix_recarga_evidence_doc.py   (Google Doc)
  build_felix_recarga_evidence_html.py   (self-contained HTML report / Claude artifact)

Block kinds: h1 h2 h3 h4 p b (bullet) n (numbered) cap (caption) quote (verbatim
copy, prefix "Bot:" / "User:" / "Web:") table (marker) image (marker) meta (Google
Doc only: the byline under the title; the HTML carries META_LINE in its hero).
Paragraphs and bullets may use "Lead  ::  rest" to bold the lead; both builders
render it as "Lead: rest".
Consecutive image blocks render side by side (HTML grid row, one Doc paragraph).
"""

from pathlib import Path
from PIL import Image

BASE = Path(__file__).parent
IMG_DIR = BASE / "felix_evidence"

DOC_URL = "https://docs.google.com/document/d/1MiP_fI-gY0ZIfxcdfYEnrTTVTUVkWtl3Ysth8T-MHAY/edit"
ARTIFACT_URL = "https://claude.ai/code/artifact/3bea064b-49c8-4170-b0de-96a0ae7da1c8"
PREV_DOC = "https://docs.google.com/document/d/18ajLNYrY49XjDsz4DwEVrElQknsdr5wWuGfl9QN3kLk/edit"
FY27_DOC = "https://docs.google.com/document/d/1oxHLqsnsfQ4qObTfFYzwPgrxDrT5i25erhlFL2GOn-I/edit"
ASANA_TASK = "https://app.asana.com/1/8556634603607/project/1215564565348002/task/1215922468293591"
GUIDE = "https://www.felixpago.com/guias/recargas-internacionales"

TITLE = "Felix Pago WhatsApp Top-Up: The Real End-to-End Flow"
SUBTITLE = ("Félix's recarga journey rebuilt from Félix's own production screenshots, 36 public videos and its "
            "launch carousels, with every step graded by the evidence behind it and mapped to the FY27 "
            "BOSS Revolution WhatsApp MTU chatbot.")
META_LINE = ("Updated 28 September 2026, first issued 10 September 2026  ·  Author João Tanaka  ·  "
             "Google Doc version  ·  Supersedes the August 2026 analysis  ·  No live transaction was run")
DOC_META = ("Updated 28 September 2026, first issued 10 September 2026  ·  João Tanaka  ·  "
            "Same content with larger screenshots: HTML artifact  ·  Supersedes the August 2026 analysis  ·  "
            "No live transaction was run")

EXTRA_LINKS = {
    "felixpago.com/recargas-internacionales": "https://www.felixpago.com/recargas-internacionales",
    "felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional":
        "https://www.felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional",
    "felixpago.com/ayuda/puedo-enviar-recargas-a-celulares":
        "https://www.felixpago.com/ayuda/puedo-enviar-recargas-a-celulares",
    "felixpago.com/guias/recargas-internacionales": GUIDE,
    "Félix's recargas guide": GUIDE,
    "payments-ui.prod.fpago.com": "https://payments-ui.prod.fpago.com",
    "pay.felixpago.com": "https://pay.felixpago.com",
    "Félix's recarga launch video": "https://www.youtube.com/watch?v=hCliPe4-71w",
    "Félix's May 2026 tutorial": "https://www.youtube.com/watch?v=V7EJA0MV8fQ",
    "Independent creator's first transfer": "https://www.youtube.com/watch?v=n6QF6oaAISI",
    "the X launch carousel": "https://x.com/Felixpago/status/2090884151939301454",
    "the Instagram carrier carousel": "https://www.instagram.com/p/DbbxTDwE7hJ/",
    "Despierta América segment": "https://www.youtube.com/watch?v=q7B_XdXNnnQ",
    "the 2022 brand spot": "https://www.youtube.com/watch?v=cokVPx6A394",
    "App Store listing": "https://apps.apple.com/us/app/f%C3%A9lix-pago-env%C3%ADos-de-dinero/id6756128226",
    "Google Play listing": "https://play.google.com/store/apps/details?id=com.felixpago.felix&hl=es",
    "the August 2026 analysis": PREV_DOC,
    "DCS FY27 Initiative Plan": FY27_DOC,
    "Asana task": ASANA_TASK,
    "Google Doc version": DOC_URL,
    "HTML artifact": ARTIFACT_URL,
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
    _img("IMG_REAL01", "real_01_entry_prefilled_token.jpg", 150),
    _img("IMG_STEP2", "felix_step2_redacted.jpg", 235),
    _img("IMG_STEP3", "felix_step3_redacted.jpg", 300),
    _img("IMG_REAL02", "real_02_payment_method_inapp_browser.jpg", 150),
    _img("IMG_REAL03", "real_03_kyc_step1_of_3.jpg", 150),
    _img("IMG_TUT10", "tut_10_success_referral.jpg", 150),
    _img("IMG_REAL04", "real_04_whatsapp_receipt_reference.jpg", 150),
    _img("IMG_DIAGRAM", "felix_recarga_flow_evidence.png", 468),
    _img("IMG_TUT01", "tut_01_web_calculator.jpg", 190),
    _img("IMG_TUT03", "tut_03_menu.jpg", 150),
    _img("IMG_TUT04", "tut_04_beneficiary_list.jpg", 150),
    _img("IMG_TUT06", "tut_06_resumen_confirm.jpg", 150),
    _img("IMG_IG_CARRIERS", "ig_carriers_grid.jpg", 330),
]

IMAGE_CAPTIONS = {
    "IMG_STEP1": "Steps 1 to 5 as Félix published them: a real WhatsApp iOS capture of the production bot. "
                 "Recipient number redacted. Source: felixpago.com/recargas-internacionales",
    "IMG_REAL01": "A real user's entry (March 2026): the deep link prefills an eight-character session token before the "
                  "greeting, and WhatsApp adds Meta's secure-service notice.",
    "IMG_STEP2": "Step 6, the amount picker in COP, and the top of the RESUMEN card. Source: felixpago.com/recargas-internacionales",
    "IMG_STEP3": "Steps 7 to 9: summary, Confirmar recarga, the Pagar recarga button and the checkout opening inside "
                 "WhatsApp's in-app browser. Source: felixpago.com/recargas-internacionales",
    "IMG_REAL02": "Payment method page in WhatsApp's in-app browser (title WhatsApp, Done control). Card only; debit is "
                  "flagged Sin comisión extra. Recipient name pixelated.",
    "IMG_REAL03": "Sender identity collected inside the checkout as step 1 de 3 (name, date of birth, email), with an "
                  "optional Verifica tu identidad tier above the form.",
    "IMG_TUT10": "Web success page from Félix's May 2026 tutorial: availability in about 30 minutes, then a referral "
                 "offer. No reference number.",
    "IMG_REAL04": "The WhatsApp receipt image after a real payment, with the pickup reference as its hero. Reference and "
                  "personal lines pixelated.",
    "IMG_DIAGRAM": "The recarga journey, each step coloured by the strongest evidence found for it.",
    "IMG_TUT01": "Web calculator on felixpago.com: promotional rate, first-send fee waived, one button into WhatsApp.",
    "IMG_TUT03": "First bot message: today's FX rate, then three quick replies. Recarga is not one of them.",
    "IMG_TUT04": "Saved beneficiaries as a WhatsApp list with Nuevo beneficiario on top. Recarga has no equivalent.",
    "IMG_TUT06": "RESUMEN in monospace headers with itemised fees. The recarga summary reuses the same component.",
    "IMG_IG_CARRIERS": "Carrier logos from the 30 Jul 2026 Instagram carousel: nine countries, no El Salvador. "
                       "Félix's recargas guide now lists ten.",
}

# ------------------------------------------------------------------ TABLES ----
TABLES = [
    ("EVIDENCE", [
        ["Source", "Type", "Date", "What it shows", "Grade"],
        ["felixpago.com/recargas-internacionales, three step images",
         "WhatsApp iOS production captures framed by marketing (prod host payments-ui.prod.fpago.com, Meta verified badge)",
         "Captured 9 Sep 2026, unchanged on 28 Sep", "Steps 1 to 9 of the recarga flow, across two sessions", "Real"],
        ["Independent creator's first transfer (Inteligencia Económica)",
         "Unscripted screen recording of a real $150 transfer", "24 Mar 2026",
         "The only real end-to-end transaction on record: deep-link token, in-app browser checkout, identity in three web "
         "steps, WhatsApp receipt", "Video"],
        ["Félix's May 2026 tutorial (1080p)", "Screen recording of the remittance flow on the same bot", "7 May 2026",
         "Web calculator, menu, list pickers, RESUMEN, hand-off, hosted checkout, CVV, success page", "Video"],
        ["Félix's recarga launch video (CEO Manuel Godoy)", "Talking head with step overlays; the phone insert is illegible",
         "27 Jul 2026", "Launch date and the three-step marketing framing", "Video"],
        ["the Instagram carrier carousel and the X launch carousel", "Designed composites; the X one uses Stripe test data",
         "30 Jul and 21 Aug 2026", "Carrier logos for nine countries; mocks of the entry and the checkout whose copy matches production",
         "Mock"],
        ["Help centre and guide pages (three recarga pages)", "Text", "Captured 10 Sep, rechecked 28 Sep 2026",
         "Step list, payment rules, coverage by country, no-refund rule, cost built into the FX rate, Boss Revolution named",
         "Documented"],
        ["Despierta América segment and 30 further public videos",
         "TV insert, screen recordings, ads, interviews, a Finovate 2025 stage demo", "2022 to 2026",
         "How the bot evolved, fee history, limits, cancellation, support, partner models", "Video"],
        ["App Store listing and Google Play listing", "Store screenshots", "Captured 9 Sep 2026",
         "The native app is a rates-and-alerts companion with no recarga", "Mock"],
    ]),
    ("CHASSIS", [
        ["Pattern seen in the remittance recordings", "Evidence", "Carried into recarga?", "So what for BR"],
        ["Entry from the website with a prefilled WhatsApp message and a full-screen redirect interstitial",
         "Tutorial 12 to 15 s; production recarga step 1 shows the same bold prefilled message",
         "Yes: the recarga entry is a prefilled deep-link message, not a typed keyword",
         "Design the web-to-WhatsApp hand-off, not only the in-thread keyword"],
        ["Welcome message leads with today's FX rate, then exactly three quick replies",
         "Tutorial 16 s; Despierta América 4:06; the 2022 brand spot shows the same shape",
         "No: recarga is reached by keyword, not from the three buttons",
         "The three-button cap forces a hierarchy; recarga is not on Félix's front door"],
        ["Free text only where a number is needed (amount, phone number); everything else is a button or a list",
         "Tutorial 20 to 33 s; production steps 4 to 8",
         "Yes: the phone number is the only free-text step in recarga",
         "Match this: free text for capture, structured replies for choices"],
        ["Saved beneficiaries as a list picker with Nuevo beneficiario on top",
         "Tutorial 19 s",
         "No: recarga starts from a blank number prompt every time",
         "Saved recipients are BR's largest available advantage in the thread"],
        ["RESUMEN block in monospace section headers with itemised fees and a Sí, correcto / Cambiar algo pair",
         "Tutorial 33 s; production RESUMEN DE RECARGA step 7",
         "Yes, same component, with Comisión Félix shown as $0.00 in the recarga checkout",
         "Reuse one summary component across products; show the fee even when it is zero"],
        ["Payment hand-off through a CTA URL button to a Félix-hosted page",
         "Tutorial 35 s (Completar pago); production step 8 (Pagar recarga)",
         "Yes: it opens inside WhatsApp's in-app browser (Done control, WhatsApp title bar)",
         "Plan for the in-app browser, not for a full browser exit"],
        ["Hosted checkout re-states the summary, reuses a saved card and asks for the CVV",
         "Tutorial 36 to 39 s (pay.felixpago.com)",
         "Partly: the recarga checkout asks for the full card (Número de tarjeta, MM / AA); a saved card appears only in the X mock",
         "Card on file plus CVV is Félix's repeat-purchase pattern; recarga may still be first-card entry only"],
        ["Web success page with an availability estimate, then Volver a WhatsApp and a referral offer",
         "Tutorial 40 to 41 s",
         "Not observed for recarga",
         "The receipt moment is where Félix is thinnest; BR can win it"],
    ]),
    ("MARKETING_VS_PRODUCT", [
        ["Marketing says", "Where", "The shipped bot does", "Evidence"],
        ["Escribe recarga en tu chat de Félix", "Help centre, landing page, X, Instagram, launch video",
         "Félix's own capture starts with a bold prefilled message, which is what a wa.me deep link produces. Typing the "
         "keyword is plausible but not shown.", "Real"],
        ["Choose the country and the operator, then enter the number", "Help-centre step list",
         "Number first; country and carrier are detected from it and confirmed with Sí, continuar / Cambiar compañía", "Real"],
        ["Amount in dollars ($20 USD, $20 por favor)", "Help-centre hero images",
         "Amount in the recipient's currency (COP); the USD total appears only at the summary", "Real"],
        ["Sin comisiones", "Landing-page headline",
         "No fee line on any screen, but Félix's guide says the cost is built into the exchange rate", "Documented"],
        ["Recarga enviada con éxito inside the chat", "Help-centre hero image",
         "No in-chat success message has ever been shown for a recarga", "Documented"],
        ["Three steps: escribir, compartir el teléfono, confirmar", "Launch video overlays",
         "Twelve screen states, including a browser hand-off and card entry", "Real"],
        ["A saved card at checkout", "the X launch carousel",
         "The production checkout asks for the card number and expiry; the saved card (ending 4242, Stripe's public test "
         "card) exists only in the mock", "Mock"],
        ["A free-text chat answered like a human", "Help-centre and third-party explainers",
         "Buttons and lists; free text only for numbers and, in remittances, names and amounts", "Video"],
    ]),
    ("FX", [
        ["Screen", "Rate shown", "What it implies"],
        ["Amount prompt (step 6)", "Tipo de cambio estimado: ~3225.81 COP/USD",
         "Quoted before the amount is chosen; the USD total is confirmed at payment"],
        ["RESUMEN DE RECARGA (step 7)", "~3208.56 COP/USD", "Exactly 6000 / 1.87, so it is back-computed from the rounded USD price"],
        ["Hosted checkout (step 9)", "TC: 3211.78 COP/USD", "6000 / 3211.78 = 1.868, displayed as $1.87"],
        ["X carousel mock", "TC: 3211.78 COP/USD", "Same figure as the production checkout, so the mock was built from a real session"],
        ["Comisión Félix", "$0.00 USD on every screen",
         "Félix's guide: el costo está incorporado en el tipo de cambio que ves al momento de pagar"],
    ]),
    ("BENCHMARK", [
        ["Dimension", "Félix recarga (observed)", "BOSS Revolution IMTU (today)", "Read"],
        ["Channel", "WhatsApp thread plus a checkout in WhatsApp's in-app browser; the native app is a companion only",
         "BR7 app and web; the WhatsApp MTU chatbot is an FY27 Q1 goal, not yet built",
         "Félix owns the channel BR lacks; BR owns the product depth Félix lacks"],
        ["Entry", "Prefilled deep link from the website with a session token, or the keyword recarga in the thread",
         "App tile, MTU home", "The plan's MARCOM deep link covers the first path; the bot should also accept the keyword"],
        ["Returning customers", "The WhatsApp number is the whole identity; every recarga starts from a blank number prompt",
         "Logged-in account with saved recipients and history", "The largest conversion gap available to BR in the thread"],
        ["Recipient capture", "Free-text number with country code and an example line",
         "Contact picker or typed number", "Adopt the example line and the country-code rule"],
        ["Carrier resolution", "Detect from the number, then confirm, with an explicit Cambiar compañía override",
         "Carrier detection with known portability failures; drives BLS promo eligibility",
         "Adopt detect-then-confirm; it de-risks carrier-scoped promos"],
        ["Product selection", "Type first (datos, paquete, saldo libre, varying by country), then three popular amounts plus a list",
         "Denomination grid; data bundles limited", "Félix demos a data bundle; BR's data gap would show in the thread"],
        ["Currency", "Recipient currency first, FX estimated, USD total only at the summary",
         "USD price with the delivered local amount", "BR's convention is clearer; keep it in the thread"],
        ["Fees and promotions", "Comisión Félix $0.00; the margin sits in the FX rate; no promotion of any kind",
         "Fee plus BLS bonus airtime", "The BLS promo is the one thing Félix cannot answer quickly"],
        ["Payment", "US-issued debit or credit card on a hosted page, no American Express; no Apple Pay or Google Pay seen",
         "Saved cards, wallets, in-app", "The in-app browser, not a browser exit, is the funnel break to measure"],
        ["Receipt", "Remittances: receipt image in the thread with the reference as its hero, plus an email. Recarga: promised, never shown",
         "Itemised receipt with reference number and delivery state",
         "Félix has the receipt primitive; whether recarga uses it is unknown"],
        ["Delivery proof", "The carrier's SMS to the recipient, en cuestión de minutos", "Delivery-confirmed state",
         "A delivered message in the thread, separate from the payment, is a visible BR advantage"],
        ["Refunds and errors", "Wrong number: sin posibilidad de reembolso; no refund path or error copy published",
         "Refund path exists", "Félix's own guide tells buyers to read refund policies first; BR should state its rule in the flow"],
        ["Support", "hablar con agente typed in the same thread, 24/7", "In-app help, CSA",
         "One thread for commerce and support is convenient and an impersonation risk"],
    ]),
    ("DECISIONS", [
        ["Decision", "What Félix does", "FY27 plan today", "Call", "BR move"],
        ["Where payment happens", "Pagar recarga opens payments-ui.prod.fpago.com in WhatsApp's in-app browser, with Regresar a WhatsApp on the page",
         "Covered: reuse the web checkout in the in-app browser", "Adopt",
         "Put a return-to-chat link on the checkout and on the result page"],
        ["Entry", "Prefilled deep link from the website with a session token; keyword in the thread",
         "Covered: MARCOM owns the entry deep link", "Adapt",
         "Carry corridor, amount and promo in the link and use them; Félix's welcome ignores its token and defaults to Mexico"],
        ["Carrier handling", "Detecté que … es un número de Claro Colombia. ¿Continuamos? with Cambiar compañía",
         "Covered: one lookup returns carrier, offers and promos", "Adopt",
         "Ask the sender to confirm the detected carrier and log every override"],
        ["Amount step", "Three quick replies for popular amounts plus an Opciones list (WhatsApp caps quick replies at three)",
         "Not in the plan yet", "Adopt", "Top three offers for the carrier as buttons, the rest in a list"],
        ["Currency", "Amounts in COP with an estimated rate; USD appears only at the summary",
         "Not in the plan yet", "Adapt", "Show the USD price and the delivered local amount together from the first amount prompt"],
        ["Returning customers", "No saved recipients for recarga; remittances have a beneficiary list",
         "Not in the plan yet", "Add",
         "Match the WhatsApp number to a BR account and open with saved recipients and a one-tap repeat"],
        ["Promotion", "None anywhere in the flow", "Covered: BLS first-purchase promo at launch", "Add",
         "Show the promo line inside the summary, after the carrier is confirmed"],
        ["Identity and KYC", "Collected inside the checkout as 1 de 3, 2 de 3, 3 de 3; nothing is asked in the thread",
         "Not in the plan yet", "Adopt", "Keep identity capture in the web checkout, never in the chat"],
        ["Receipt and delivery", "Promised, never shown for recarga; the delivery proof is the carrier's SMS",
         "Covered: order confirmation and status queries", "Add",
         "A receipt with a reference number in the thread, then a separate delivered message"],
        ["Errors, refunds, expired links", "No declined-card, unsupported-carrier, failed-delivery or expired-link copy published",
         "Not in the plan yet", "Add", "Write the error set and a refund rule before launch"],
        ["Product names", "Producto: $6000 COP - Unlimited GB 2 Hours in a Spanish flow",
         "Not in the plan yet", "Avoid", "Localise every SKU name the bot shows"],
    ]),
    ("CORRECTIONS", [
        ["Claim in the August 2026 analysis", "What the real screens show", "Verdict"],
        ["The hosted checkout opens in the default browser",
         "It opens inside WhatsApp's in-app browser (title bar WhatsApp, Done control, payments-ui.prod.fpago.com). "
         "The sender leaves the thread but not the app.", "Corrected"],
        ["The entry is the typed keyword recarga",
         "Félix's own capture opens with a bold prefilled message, which only a deep link produces, and a real user's link "
         "also carries a session token. The keyword path is documented, not shown.", "Corrected"],
        ["No receipt or reference number",
         "Wrong for remittances: a real March 2026 transfer ends with a WhatsApp receipt image whose hero is the pickup "
         "reference, plus an email receipt, and the Terms promise a Número de referencia on every confirmation. Still "
         "unobserved for recarga.", "Corrected"],
        ["Whether KYC fires mid-flow was unknown",
         "For a first-time remittance the bot asks nothing; identity and billing address are collected in three steps "
         "inside the hosted checkout. Recarga not yet observed.", "New"],
        ["Recharge types are datos, paquete, saldo libre",
         "The prompt is confirmed but the buttons are unseen, and Félix now says the types vary by country. The demo "
         "purchase is Datos, a bundle named Unlimited GB 2 Hours.", "Still open"],
        ["Recarga launch date unknown",
         "Dated to 27 Jul 2026 (launch video), with carousels on 30 Jul (Instagram) and 21 Aug (X). Félix still invites "
         "senders to probar it.", "New"],
    ]),
]

# ------------------------------------------------------------------ BLOCKS ----
BLOCKS = [
    ("h1", TITLE),
    ("meta", DOC_META),

    # ------------------------------------------------------------ 1 --------
    ("h2", "1. Summary"),
    ("p", "Bottom line  ::  Félix's WhatsApp recarga is a thin layer on its remittance bot. A deep link opens the chat, the "
          "bot detects the carrier from the recipient's number, the sender picks an amount from three buttons, and payment "
          "happens on a Félix web page inside WhatsApp's in-app browser. The FY27 WhatsApp MTU chatbot already copies the "
          "three parts that matter: deep-link entry, carrier from the number, web checkout in the in-app browser. BR can "
          "beat Félix on everything Félix has not built: returning customers, promotions, the receipt and the error paths."),
    ("b", "What is proven  ::  real production screens exist for nine of the twelve steps, from the prefilled entry message "
          "to the hosted checkout, all published by Félix on its own recargas page. Nothing after the Pagar button has "
          "been seen for a recarga."),
    ("b", "Two findings change the BR design  ::  the checkout opens inside WhatsApp's in-app browser (title bar WhatsApp, "
          "Done control), so the sender never leaves the WhatsApp app; and Félix's own entry is a prefilled deep-link "
          "message carrying a session token, not a typed keyword."),
    ("b", "The margin is in the exchange rate, and Félix now says so  ::  COP 6,000 of Claro Colombia data costs $1.87 with "
          "Comisión Félix $0.00, and three different COP/USD rates appear on three screens. Félix's recargas guide, "
          "rechecked on 28 Sep 2026, states that the cost está incorporado en el tipo de cambio."),
    ("b", "Identity waits for the checkout  ::  in the only real first-time transfer on record, the bot asked nothing "
          "about the sender; name, date of birth, email and billing address were collected in three web steps inside the "
          "payment page. Cards must be US-issued, and American Express is refused."),
    ("b", "Félix's gaps are BR's openings  ::  no saved recipients for recarga, no promotion anywhere in the flow, no "
          "published refund rule or error copy, and delivery proof left to the carrier's SMS. Recarga is still framed as "
          "something to probar, reached by keyword only, and absent from the welcome menu and the native app."),
    ("b", "What BR should do next  ::  add the four things the FY27 plan does not yet specify (account match with saved "
          "recipients and a one-tap repeat, the BLS promo line in the summary, an in-thread receipt with a reference "
          "number, error and refund copy), and run Félix's own comparison test, the same Claro Colombia purchase on BR, "
          "before Félix's delivered-value framing reaches customers. Section 9 has the full list."),

    # ------------------------------------------------------------ 2 --------
    ("h2", "2. Evidence base and method"),
    ("p", "Everything here comes from public sources gathered on 9 and 10 September 2026, with Félix's landing, help and "
          "guide pages rechecked on 28 September 2026. No Félix account was created and no transaction was run, so every "
          "claim carries the grade of the evidence behind it."),
    ("b", "Real  ::  a production WhatsApp capture published by Félix. Tells: Meta verified badge, native quick-reply and "
          "list rendering, the prod hostname payments-ui.prod.fpago.com."),
    ("b", "Video  ::  a frame from a public screen recording of the live bot. All are remittance flows; none is a recarga."),
    ("b", "Mock  ::  a designed composite from Félix's marketing. Tells: placeholder numbers, Stripe's 4242 test card, "
          "timestamps that run backwards."),
    ("b", "Documented  ::  stated in Félix's help centre or guide but never seen on a screen."),
    ("table", "EVIDENCE"),
    ("p", "Video frames were read one per second and every distinct screen was transcribed verbatim. Recipient numbers and "
          "private names are pixelated in the images and masked in the text; the marketing mocks use placeholder data."),

    # ------------------------------------------------------------ 3 --------
    ("h2", "3. The recarga journey, screen by screen"),
    ("p", "Twelve screen states, in the order the sender meets them. Spanish copy is quoted verbatim, typos included. "
          "Steps 1 to 9 are production captures; steps 10 to 12 are inferred from the remittance flow and Félix's documentation."),

    ("h3", "3.1 Entry and number capture (steps 1 to 3)"),
    ("image", "IMG_STEP1"),
    ("image", "IMG_REAL01"),
    ("quote", "User: Quiero hacer una “recarga telefónica”                                   3:57 PM ✓✓"),
    ("quote", "Bot: ¿A qué número quieres mandar la recarga? Incluye el código de país.\n| Ejemplo: +52 1234567890                                        3:57 PM"),
    ("quote", "User: +57 ••• ••• ••••                                                         4:00 PM ✓✓"),
    ("p", "Entry  ::  the opening message is bold and wrapped in curly quotes. WhatsApp renders that only when the sent text "
          "carries asterisks, which a person does not type: this is a wa.me deep link with prefilled text, the same "
          "mechanism behind the website's Empezar envío sin comisión button. In a real user's recording the link also "
          "prefills an eight-character session token ahead of the greeting, so the bot can tie the chat to the web session "
          "(corridor, amount, promo). Félix's welcome then ignores it and defaults to Mexico, which costs the sender an "
          "extra Enviar a otro país step and a country list."),
    ("p", "Keyword path  ::  the help centre, the landing page and every marketing asset say escribe recarga. The X "
          "carousel shows the word inside a full sentence, Quiero hacer una “recarga”, so the bot likely matches the "
          "keyword within free text rather than requiring a bare command. Both paths exist; only the deep link is on a real screen."),
    ("p", "Number prompt  ::  one free-text question with an inline example and an explicit country-code requirement. There "
          "is no country picker and no carrier picker before the number. The example is Mexican (+52) although every real "
          "capture is Colombian: Mexico is the corridor Félix designs for, Colombia is where the team happened to test."),

    ("h3", "3.2 Carrier detection and recharge type (steps 4 to 5)"),
    ("quote", "Bot: 📶 Detecté que ••• ••• •••• (Colombia) es un número de Claro Colombia.\n\n¿Continuamos?                                                        4:00 PM\n[ Sí, continuar ]   [ Cambiar compañía ]"),
    ("quote", "User: Sí, continuar                                                             4:00 PM ✓✓"),
    ("quote", "Bot: 📱 Perfecto. ¿Qué tipo de recarga quieres hacer a tu numero Claro Colombia?"),
    ("p", "Detect, then confirm  ::  country and carrier are inferred from the number's prefix and put back to the sender as "
          "a yes-or-change question. This is the most portable pattern in the flow. Félix does not pretend detection is "
          "certain; it lets the customer override. For BR, whose carrier-scoped BLS promos break on ported numbers, this is "
          "the mechanism that makes showing a promo in a conversational surface safe."),
    ("p", "Recharge type  ::  the prompt is confirmed on a real screen (with the accent missing from numero), but the option "
          "buttons are cut off in every published capture. The help centre lists datos, paquete o saldo libre, and the "
          "landing page now adds that la disponibilidad de operadoras y tipos de recarga varía según el país, so the "
          "buttons likely change with the carrier. The published purchase is Datos."),

    ("h3", "3.3 Amount, denominated in the recipient's currency (step 6)"),
    ("image", "IMG_STEP2"),
    ("quote", "Bot: 📱 De acuerdo, vamos a mandar Datos a tu Claro Colombia. ¿Cuánto quieres mandar?\nTipo de cambio estimado: ~3225.81 COP/USD. El total final en USD se confirma al pagar.\n\nOpciones populares 👇                                              5:40 PM\n[ $4000 COP ]   [ $5000 COP ]   [ $6000 COP ]"),
    ("quote", "Bot: Elegir un monto diferente:                                        5:40 PM\n[ ≡ Opciones ]"),
    ("quote", "User: $6000 COP                                                                 5:40 PM ✓✓"),
    ("p", "Three buttons plus a list  ::  WhatsApp caps quick replies at three per message, so Félix splits the step into a "
          "message of three popular amounts and a separate list message for the rest. The list contents were never captured."),
    ("p", "Recipient currency first  ::  the sender picks a COP amount before seeing a USD price. The rate is labelled an "
          "estimate and the USD total is deferred to the summary, so the sender commits to a foreign-currency amount "
          "without knowing what the card will be charged. BR's app shows the USD price next to the delivered amount."),

    ("h3", "3.4 Summary, confirmation, hand-off and checkout (steps 7 to 9)"),
    ("image", "IMG_STEP3"),
    ("quote", "Bot: 🧾 RESUMEN DE RECARGA\nNúmero: ••• ••• ••••\nPaís: Colombia\nCompañía: Claro Colombia\nProducto: $6000 COP - Unlimited GB 2 Hours\nTotal a pagar: $1.87 USD\nTipo de cambio: ~3208.56 COP/USD\n\n¿Confirmas esta recarga?                                             5:40 PM\n[ Confirmar recarga ]   [ Cambiar algo ]"),
    ("quote", "User: Confirmar recarga                                                         5:40 PM ✓✓"),
    ("quote", "Bot: Listo. Completa tu pago en este sitio seguro para enviar la recarga.\n[ ↗ Pagar recarga ]"),
    ("quote", "Web: Done                    WhatsApp · payments-ui.prod.fpago.com\nFélix recargas                              [ Regresar a WhatsApp ]\nResumen de tu recarga\nNúmero            ••• ••• ••••\nCompañía          Claro Colombia\nPaquete           Unlimited GB 2 Hours\nRecibes           COP 6,000.00 COP\nComisión Félix    $0.00 USD\nTotal a pagar     $1.87 USD\n                  TC: 3211.78 COP/USD\nMétodo de pago\nNúmero de tarjeta                 MM / AA\n[ Pagar ]"),
    ("p", "The summary  ::  the first place the USD figure appears. It is the same RESUMEN component the remittance bot uses "
          "(monospace section header, bold values), which is a good sign for BR: one summary primitive can serve every "
          "product in the thread."),
    ("p", "The gate  ::  Confirmar recarga / Cambiar algo is a genuine escape hatch before the irreversible step. What "
          "Cambiar algo does was never captured."),
    ("p", "The hand-off  ::  a CTA URL button that opens inside WhatsApp's in-app browser: the title bar reads WhatsApp "
          "with a Done control and the address payments-ui.prod.fpago.com, and the page itself offers Regresar a WhatsApp. "
          "The sender leaves the thread but never leaves the WhatsApp app."),
    ("p", "The checkout  ::  re-states the summary, adds the explicit Comisión Félix $0.00 USD line and a third rate "
          "(TC: 3211.78), then asks for the card number and expiry. Card details are never typed into the chat. Copy "
          "defects on this screen: Recibes COP 6,000.00 COP repeats the currency code, the SKU name is untranslated "
          "English, and the recipient number is shown with the country code doubled (+57 57…). The X mock of this screen "
          "shows a saved card ending 4242 (Stripe's test card), a hint that repeat buyers see a card-on-file state."),

    ("h3", "3.5 After Pagar: payment result, confirmation and delivery (steps 10 to 12)"),
    ("p", "No recarga screen exists for anything after Pagar. The closest evidence is an independent creator's unscripted "
          "first transfer ($150 cash pickup to El Salvador, March 2026), the only real end-to-end transaction on record, "
          "plus the success page from Félix's May 2026 tutorial. Both run on the same bot and checkout family. Read them "
          "as the likely recarga shape, not as recarga fact."),
    ("image", "IMG_REAL02"),
    ("image", "IMG_REAL03"),
    ("image", "IMG_TUT10"),
    ("image", "IMG_REAL04"),
    ("quote", "Web: Done · WhatsApp · pay.felixpago.com\n¡Estás a punto de completar tu envío a [recipient]!\n¿Cómo deseas pagar?\nTarjeta de crédito/débito →  Las tarjetas de crédito pueden incurrir en tarifas adicionales según el emisor.\n[ Sin comisión extra para débito ]\nPago seguro y encriptado · Este es un pago seguro encriptado con SSL de 256 bits."),
    ("quote", "Web: 1 de 3 · ★ Desbloquea más beneficios · Verifica tu identidad de forma fácil y segura >\nCuéntanos más sobre ti\nNombre * · Segundo nombre · Apellido Paterno * · Apellido Materno · Fecha de nacimiento * · Correo electrónico *\n2 de 3 · Ingresa la dirección vinculada a tu tarjeta · 3 de 3 · card, then CVV"),
    ("quote", "Web: ¡Listo! Tu pago se completó con éxito.\nTu envío de $20 USD, convertidos en $401 MXN, estará disponible para [beneficiary] en aproximadamente 30 minutos.\nGana hasta $500 USD · Obtén $20 dólares por cada amigo que recomiendes\n[ Recomendar por WhatsApp ]        (earlier frame: [ Volver a WhatsApp ])"),
    ("quote", "Bot: ¡Tu envío está siendo procesado! En un momento te enviamos tu recibo por email 📧            12:31 PM\n[ receipt image: reference number as hero · amount, 30 minutos, pickup store, recipient · ¡Ahorraste $… USD ]"),
    ("p", "Consent and payment method  ::  on the first CTA tap WhatsApp shows a one-time Securely browse this business "
          "website sheet, then the page opens in the in-app browser. Card is the only method; credit cards carry an "
          "issuer-fee warning and debit is flagged Sin comisión extra. Félix's help centre adds that the card must be "
          "issued in the US and cannot be American Express, and tells senders Félix will never ask them to pay outside "
          "the official chat."),
    ("p", "Identity  ::  no KYC question is asked in the thread. Name (with paternal and maternal surnames), date of birth "
          "and email, then the billing address, then the card are collected as 1 de 3, 2 de 3, 3 de 3 inside "
          "pay.felixpago.com after the transfer is fully specified, with an optional Verifica tu identidad tier above the form."),
    ("p", "Payment result  ::  a web page, not a WhatsApp message. It confirms the charge, gives an availability estimate "
          "and pivots straight to referral. No reference number appears on the page."),
    ("p", "WhatsApp confirmation  ::  seconds after the charge, three artefacts arrive: the web success page, an email "
          "titled Recibo de transacción, and in the thread a bot line followed by a receipt image whose hero is the "
          "cash-pickup reference number, with a savings chip (¡Ahorraste …). Félix's Terms promise a unique Número de "
          "referencia de la transacción on every confirmation, and its guide promises una confirmación por WhatsApp una "
          "vez que la recarga se procesó. For recarga, where there is no pickup code to show, whether this receipt image "
          "exists at all is the open question that matters most."),
    ("p", "Delivery  ::  El saldo se acredita en la línea de tu familiar, generalmente en minutos. La operadora le envía a "
          "tu familiar un mensaje confirmando la recarga. Félix leans on the carrier's SMS as delivery proof rather than "
          "sending its own delivered message."),
    ("p", "The irreversibility rule  ::  un número equivocado suele acreditar el saldo a otra línea sin posibilidad de "
          "reembolso, and una vez procesada la recarga, no hay forma de corregir un error en estos datos. No refund path "
          "for a Félix-side or carrier-side failure is published anywhere."),

    ("h3", "3.6 The journey on one page"),
    ("image", "IMG_DIAGRAM"),

    # ------------------------------------------------------------ 4 --------
    ("h2", "4. The chassis underneath: what the remittance recordings prove"),
    ("p", "Félix built recarga on the bot it already had. The May 2026 tutorial is the only 1080p screen recording of that "
          "bot, so it is the clearest view of the mechanics recarga inherits and the ones it does not have yet."),
    ("image", "IMG_TUT01"),
    ("image", "IMG_TUT03"),
    ("image", "IMG_TUT04"),
    ("image", "IMG_TUT06"),
    ("quote", "Bot: El tipo de cambio de hoy es $20.05 pesos por dólar.\n\nPor favor selecciona una de las opciones para continuar 👇          8:37 a.m.\n[ Enviar dinero ]   [ Refiere y gana ]   [ Otras opciones ]"),
    ("quote", "Bot: Tu beneficiario recibirá $401.00 MXN.\n¿A quién le quieres enviar dinero? 🎁 Selecciona el nombre en las opciones 👇\n[ ≡ Opciones ]  →  Nuevo beneficiario · then four saved beneficiaries"),
    ("quote", "Bot: 🧾 RESUMEN\nMonto: $401.00 MXN ($20.00 USD)\nTasa: $20.05 MXN/USD\n🏦 DESTINO\nA: [beneficiary]\nEn: Ciudad de México, MX-MEX\nTienda: Oxxo\n🪙 TARIFAS\nComisión: $2.99\nComisión por tienda: $1.99\n💵 TOTAL A PAGAR\n$20.00 + $4.98 = $24.98                                              8:38 a.m.\n[ Sí, correcto 👍 ]   [ Cambiar algo ]"),
    ("table", "CHASSIS"),
    ("p", "One inconsistency worth noting  ::  the tutorial's web calculator advertises Comisión Gratis and Te ahorras hoy "
          "-$2.99 USD for the first send, but the chat RESUMEN in the same video charges $2.99 plus $1.99 for cash pickup, "
          "a 24.9% all-in cost on a $20 send. Félix's zero fee is a first-send promotion on the remittance side and a "
          "standing claim on the recarga side."),

    ("h3", "4.1 What the wider video corpus adds"),
    ("p", "Most of the other videos are talking-head ads with no screens. The ones that show the product add the following."),
    ("b", "Recarga has not earned a menu button  ::  the welcome has been a three-button message since 2022. By 2026 the "
          "buttons are Enviar dinero, Refiere y gana and Otras opciones (or Enviar a otro país for deep-link arrivals), "
          "with the FX rate leading the body."),
    ("b", "Fee history  ::  a flat $2.99 to Mexico in December 2022; $2.99 plus a $1.99 store fee for cash pickup in 2026; "
          "first-send incentives that vary by placement ($15 extra, $20 free, $0 commission). Recarga is the first Félix "
          "product marketed with no fee at all."),
    ("b", "Limits  ::  Félix's 2024 infographic states $1,000 per transaction, $3,000 per week and $12,000 per month. "
          "Whether recargas count against these is undocumented."),
    ("b", "Cancellation lives in the Terms, not the bot  ::  a personal transfer can be cancelled for a full refund, fees "
          "included, within 30 minutes of payment by WhatsApp, email or phone, quoting the reference number. The Terms "
          "never mention recargas."),
    ("b", "Every payment link expires  ::  a 2025 brand video lists CADA LINK DE PAGO TIENE TIEMPO DE EXPIRACIÓN as a "
          "security feature, so the Pagar recarga button is time-boxed. The expiry copy and the recovery path were never captured."),
    ("b", "Support is a keyword  ::  hablar con agente or Necesito ayuda typed in the thread reaches 24/7 human support in "
          "Spanish; no phone number or web help path is shown in any 2025 or 2026 asset."),
    ("b", "Two other Félix models matter for BR  ::  the Finovate 2025 demo shows a partner bank app deep-linking into "
          "WhatsApp with a token, the bot debiting the bank account on Confirmar Pago and posting ¡Tu pago fue exitoso! in "
          "the chat, with no hosted checkout at all. The June 2026 Nexa video shows a recipient-initiated request link "
          "(holafelix.com/request/…) created in the recipient's Guatemalan wallet and shared over WhatsApp. The first "
          "proves Félix can close payment in the thread when the funding rail allows it; the second is Félix's version "
          "of BR's Request Top-Up."),
    ("b", "Competitors bid on Félix's name  ::  in the March 2026 recording Remitly ran App Store search ads on felix pago "
          "and Google ads headlined Enviar Dinero por WhatsApp, and Ria bid on the brand too. Google autocomplete for felix "
          "pago offered es seguro, reviews and reddit, so trust is the dominant pre-purchase question."),

    # ------------------------------------------------------------ 5 --------
    ("h2", "5. Marketing versus the shipped product"),
    ("p", "Félix's help-centre heroes, carousels and launch video describe a simpler product than the one on the screens. "
          "The gaps matter because BR will be benchmarked against the marketing version in executive conversations."),
    ("table", "MARKETING_VS_PRODUCT"),

    # ------------------------------------------------------------ 6 --------
    ("h2", "6. Pricing, FX and the zero-commission claim"),
    ("p", "The one transaction Félix chose to publish is COP 6,000 of Claro Colombia data for $1.87. The landing page "
          "promises no commission, solo pagas el monto de la recarga, al tipo de cambio que ves antes de confirmar, and a "
          "summary price that does not change at payment."),
    ("table", "FX"),
    ("p", "What this means  ::  the sender sees three rates in one purchase and none is presented as the price. With the "
          "fee at zero, the spread between Félix's rate and mid-market is the whole margin, and Félix's recargas guide now "
          "says so in writing: Félix no cobra una comisión explícita por recarga: el costo está incorporado en el tipo de "
          "cambio. The same guide tells readers to run the same simulation (mismo país, misma operadora, mismo monto) on "
          "each provider and compare the saldo real que recibirá tu familiar, naming Boss Revolution and Ding as the two "
          "best-known incumbents. It also lists promociones de saldo extra and paying con efectivo en tienda as selection "
          "criteria; Félix offers neither."),
    ("p", "What BR should do  ::  run that exact test first, internally: the same Claro Colombia data SKU (or COP 6,000 of "
          "saldo) on BR, with and without the BLS promo, and record the delivered value against Félix's $1.87. If BR wins, "
          "it is a ready-made message for the WhatsApp launch; if it loses, the launch promo has to close the gap."),
    ("p", "Still unknown  ::  whether Félix sells at face value, and its effective spread against mid-market. One live "
          "purchase on two or three corridors settles it; it needs approval before any card is charged."),

    # ------------------------------------------------------------ 7 --------
    ("h2", "7. Coverage: countries and carriers"),
    ("p", "Félix says recarga is available in every country where it sends money and claims Más de 40 empresas para "
          "recargar. Félix's recargas guide, rechecked on 28 September 2026, is the fullest list: ten countries."),
    ("b", "Mexico  ::  Telcel, AT&T, Bait, Unefon, Movistar, OuiMovil, Virgin Mobile."),
    ("b", "Central America  ::  Guatemala, Honduras and Nicaragua: Tigo, Claro. El Salvador: Claro, Tigo, Digicel, "
          "Movistar, Red. Costa Rica: Claro only."),
    ("b", "South America and the Caribbean  ::  Colombia: Claro, Tigo, Movistar. Ecuador: Claro, Movistar, Tuenti. Peru: "
          "Movistar, Bitel, Entel. Dominican Republic: Claro, Altice, Viva."),
    ("b", "Gaps  ::  Brazil, a 2026 remittance corridor, is missing from the recarga list despite the claim of full "
          "corridor parity. The 30 Jul Instagram carousel left out El Salvador, but the guide now includes it (the 10 Sep "
          "version of this report called it absent). Carriers to verify in the live bot: WOM in Colombia, CNT in Ecuador, "
          "Kölbi and Liberty in Costa Rica."),
    ("image", "IMG_IG_CARRIERS"),

    # ------------------------------------------------------------ 8 --------
    ("h2", "8. Benchmark: Félix recarga versus BOSS Revolution IMTU"),
    ("table", "BENCHMARK"),

    # ------------------------------------------------------------ 9 --------
    ("h2", "9. What this means for the FY27 WhatsApp MTU chatbot"),
    ("p", "The DCS FY27 Initiative Plan schedules the WhatsApp MTU chatbot as a Q1 business goal. The WhatsApp Business team "
          "builds the conversational layer on the DTC Universal API shipped in FY26; DCS owns the recipient-number lookup, "
          "promo eligibility, the checkout hand-off, order confirmation and status queries. Scope is MTU only, launched in "
          "one corridor (Mexico or Guatemala) with a BLS first-purchase promo, with a target above 25% conversion from offer "
          "picked to paid. The Asana task has no owner or dates yet (checked 28 Sep 2026)."),
    ("p", "The plan already takes the three Félix patterns that matter. The table lists every design decision the Félix "
          "screens inform and whether the plan covers it yet."),
    ("table", "DECISIONS"),
    ("h3", "9.1 Where BR can beat Félix"),
    ("p", "Returning customers  ::  Félix starts every recarga from a blank number prompt because the WhatsApp number is its "
          "whole identity model. BR can match the WhatsApp number to an account and open with saved recipients and a "
          "one-tap repeat, the same list pattern Félix already uses for remittance beneficiaries. This depends on the "
          "cross-app identity work and is the largest conversion difference on the table."),
    ("p", "Promotions  ::  there is no promo mechanic on any Félix recarga screen. BR's BLS bonus airtime, shown inside the "
          "summary after the carrier is confirmed, is an advantage Félix cannot answer without building a pricing engine."),
    ("p", "Post-purchase  ::  Félix's flow ends on a web page with a referral offer and no reference number. An itemised "
          "receipt in the thread, a delivered message distinct from the payment confirmation, and an in-thread support "
          "hand-off beat Félix where its own help centre is weakest."),
    ("h3", "9.2 What to instrument in the pilot"),
    ("p", "The plan already names the funnel events (link open, number confirmed, offer picked, checkout opened, paid). "
          "The Félix screens point to five more places where senders will drop or where BR carries risk."),
    ("b", "Consent sheet and in-app browser load  ::  CTA taps versus checkout page loads. The first tap shows WhatsApp's "
          "one-time Securely browse this business website sheet, a drop point every Félix sender also passes."),
    ("b", "Return to chat  ::  return-link taps versus checkout completions. Félix offers Regresar a WhatsApp on the "
          "checkout header and Volver a WhatsApp on the success page."),
    ("b", "Number parse failures  ::  the only free-text step; the example line and the country-code rule are the "
          "mitigation, and BR should log how often the number fails to parse."),
    ("b", "Carrier override rate  ::  taps on the change-carrier option measure detection accuracy and, for BR, "
          "promo-eligibility risk."),
    ("b", "Expired links  ::  opens of an expired checkout link and how many of those senders recover. Félix time-boxes "
          "every payment link and has never shown what happens when one lapses."),

    # ------------------------------------------------------------ 10 -------
    ("h2", "10. What changed since earlier versions"),
    ("p", "Against the August 2026 analysis, which was built without real screens:"),
    ("table", "CORRECTIONS"),
    ("p", "Everything else in the August document held on the real screens: the three-button amount step with an Opciones "
          "list, the RESUMEN DE RECARGA fields, card-only payment, Colombia as the demonstrated corridor, and Félix naming "
          "Boss Revolution in its guide."),
    ("p", "In this update (28 Sep 2026), from a recheck of Félix's live pages and the FY27 plan:"),
    ("b", "Félix's guide now states that the recarga cost is built into the exchange rate, confirming the inference in section 6."),
    ("b", "Payment is a US-issued debit or credit card, American Express excluded, and Félix warns it will never ask for "
          "payment outside the official chat."),
    ("b", "Coverage is ten countries in the guide, El Salvador included; the earlier statement that El Salvador was "
          "absent is withdrawn."),
    ("b", "Félix frames recarga as something to probar and says carrier and recharge-type availability varies by country."),
    ("b", "Section 9 is now mapped to the FY27 WhatsApp MTU chatbot goal; forensic detail with no bearing on the "
          "decision (session timestamps, battery levels, launch-video frames, duplicate marketing mocks) was cut."),

    # ------------------------------------------------------------ 11 -------
    ("h2", "11. Still open, and how to close it"),
    ("p", "Nine of twelve steps are on real screens. The remaining gaps cluster after payment and around the error paths. "
          "One live top-up from a US number with a US card would close most of them in under an hour; it needs approval "
          "before any purchase is completed."),
    ("b", "The recharge-type buttons (step 5) and the Opciones list of denominations (step 6), per carrier."),
    ("b", "The recarga payment result and WhatsApp confirmation, including whether a reference number exists and what the "
          "receipt image shows when there is no pickup code."),
    ("b", "Whether a first-time recarga sender is taken through identity capture in the checkout, as for remittances, or "
          "earlier in the thread."),
    ("b", "The expiry window of the Pagar recarga link and the copy shown when it lapses."),
    ("b", "The error set: malformed number, unsupported carrier or country, denomination unavailable, declined card, "
          "carrier failure after a successful charge."),
    ("b", "Whether a saved-number or repeat option appears for a second recarga."),
    ("b", "Whether top-ups are sold at face value, and the effective FX spread against mid-market on two or three corridors."),
    ("b", "Whether recargas count against the published send limits, and whether a recurring recarga exists."),
    ("b", "BR's own delivered value on the same Claro Colombia purchase. This one is internal and needs no approval."),
    ("p", "Suggested protocol  ::  one Claro Colombia data recarga at the smallest denomination and one Telcel Mexico saldo "
          "recarga, recorded from the deep link to the carrier SMS, with the card statement checked for the exact USD charge."),

    # ------------------------------------------------------------ 12 -------
    ("h2", "12. Sources"),
    ("b", "Félix recargas landing page (three production step images, FAQ): https://www.felixpago.com/recargas-internacionales"),
    ("b", "Help centre, ¿Cómo enviar una recarga telefónica internacional con Félix?: https://www.felixpago.com/ayuda/como-enviar-una-recarga-telefonica-internacional"),
    ("b", "Help centre, ¿Puedo enviar recargas a celulares con Félix?: https://www.felixpago.com/ayuda/puedo-enviar-recargas-a-celulares"),
    ("b", "Guide, Recargas internacionales (coverage by country, cost in the FX rate, names Boss Revolution and Ding): " + GUIDE),
    ("b", "Launch video, Félix lanza Recargas Telefónicas, 27 Jul 2026: https://www.youtube.com/watch?v=hCliPe4-71w"),
    ("b", "Tutorial, Cómo enviar dinero por WhatsApp con Félix, 7 May 2026: https://www.youtube.com/watch?v=V7EJA0MV8fQ"),
    ("b", "Independent first transfer, Probando Felix Pago | ¿Funciona de verdad?, Inteligencia Económica, 24 Mar 2026: https://www.youtube.com/watch?v=n6QF6oaAISI"),
    ("b", "Despierta América segment, 3 May 2026: https://www.youtube.com/watch?v=q7B_XdXNnnQ"),
    ("b", "Brand spot, ¡Envía dinero a México por WhatsApp!, 5 Dec 2022: https://www.youtube.com/watch?v=cokVPx6A394"),
    ("b", "Cancellation terms walkthrough, Dinero Digital, 12 Jul 2025: https://www.youtube.com/watch?v=FlCvpicOwTQ"),
    ("b", "FinovateSpring 2025 demo (embedded Félix Send): https://www.youtube.com/watch?v=CIc0e46UGrI"),
    ("b", "Nexa request-link video, 10 Jun 2026: https://www.youtube.com/watch?v=LXk_aAZ5xqU"),
    ("b", "Security brand video with support keywords and link expiry, 21 Nov 2025: https://www.youtube.com/watch?v=nwxXznMqksw"),
    ("b", "X carousel, 21 Aug 2026: https://x.com/Felixpago/status/2090884151939301454"),
    ("b", "Instagram carousel, 30 Jul 2026: https://www.instagram.com/p/DbbxTDwE7hJ/"),
    ("b", "iOS App Store listing: https://apps.apple.com/us/app/f%C3%A9lix-pago-env%C3%ADos-de-dinero/id6756128226"),
    ("b", "Google Play listing: https://play.google.com/store/apps/details?id=com.felixpago.felix&hl=es"),
    ("b", "DCS FY27 Initiative Plan, WhatsApp MTU chatbot goal: " + FY27_DOC),
    ("b", "Asana, New Channel - Rollout WhatsApp MTU chatbot: " + ASANA_TASK),
    ("b", "Previous analysis, 29 Aug 2026: " + PREV_DOC),
    ("b", "Repository with the evidence images and generators: https://github.com/tanaka-idt/IDT-Claude"),
]
