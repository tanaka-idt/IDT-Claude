"""
Creates a Google Doc: "BOSS Revolution IMTU — Crypto Payments via Triple-A"
Architecture + workflows for adding Triple-A crypto checkout to the IMTU
payment flow (alongside credit card, debit card, and BOSS Money wallet).
Uses the same OAuth credentials as create_google_doc.py / create_imtu_doc.py.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

DOC_TITLE = "BOSS Revolution IMTU — Crypto Payments via Triple-A (Architecture & Workflows)"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                raise FileNotFoundError("credentials.json missing")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def ins(text):
    return {"insertText": {"location": {"index": 1}, "text": text + "\n"}}


def para_style(text, style):
    return {"updateParagraphStyle": {
        "range": {"startIndex": 1, "endIndex": 1 + len(text) + 1},
        "paragraphStyle": {"namedStyleType": style},
        "fields": "namedStyleType",
    }}


# BLOCKS are written in natural top-to-bottom document order.
# main() iterates over reversed(BLOCKS) because every insert happens at index 1.
BLOCKS = [
    ("h1", DOC_TITLE),

    ("body",
     "Prepared by: João Tanaka — Digital Channel Services (DCS)\n"
     "Date: July 7, 2026\n"
     "Status: Draft for discussion\n"
     "Scope: Add Triple-A as a fourth payment option (crypto / stablecoins) in the BOSS Revolution "
     "IMTU purchase flow for DTC customers, alongside credit card, debit card, and BOSS Money wallet."
    ),

    # ── 1. Executive Summary ──────────────────────────────────────────────
    ("h2", "1. Executive Summary"),
    ("body",
     "This document proposes integrating Triple-A (triple-a.io), a licensed crypto payment gateway, "
     "into the IDTPay ecosystem so BOSS Revolution DTC customers can pay for International Mobile "
     "Top-Up (IMTU) with cryptocurrencies and stablecoins (USDC, USDT, BTC, ETH, and others).\n\n"
     "The core design principle: IDT never touches, holds, or converts crypto. The customer pays "
     "crypto to Triple-A; Triple-A locks the exchange rate at checkout, absorbs all volatility, and "
     "settles to IDT in fiat (USD) via next-business-day bank transfer. Inside IDTPay, Triple-A is "
     "just one more payment-method adapter — architecturally equivalent to a card PSP — so the IMTU "
     "order, fulfillment, ledger, and receipt flows remain unchanged.\n\n"
     "Why it is attractive for IMTU:\n"
     "• Zero chargebacks — crypto payments are push-based and irreversible, eliminating the "
     "friendly-fraud losses that plague card-funded IMTU.\n"
     "• Diaspora fit — many BOSS Revolution corridors (LATAM, Africa, Caribbean, Southeast Asia) "
     "have high stablecoin adoption among senders.\n"
     "• Lower cost of acceptance — Triple-A's publicly referenced pricing is a flat fee in the "
     "~0.8%–1% range (to be confirmed commercially), vs. typical card interchange + scheme fees, "
     "with no chargeback/dispute overhead.\n"
     "• Licensed rails — Triple-A is FinCEN-registered (MSB) and holds US money transmitter "
     "licensing (NMLS ID 2514255), is a MAS-licensed Major Payment Institution in Singapore, and is "
     "licensed in the EU (Payment Institution via ACPR; crypto-asset services via AMF) and "
     "registered in Canada (FINTRAC, Bank of Canada PSP)."
    ),

    # ── 2. About Triple-A ────────────────────────────────────────────────
    ("h2", "2. What Triple-A Provides"),
    ("body",
     "Triple-A is a white-label digital-currency payment gateway. Key properties relevant to this "
     "integration:\n\n"
     "• Hosted, white-label checkout — customer is handed to a Triple-A-hosted payment form "
     "(redirect or in-app webview) or an embedded form; the form shows the crypto amount, a QR "
     "code / wallet address, and a countdown while the exchange rate is locked.\n"
     "• Locked-in exchange rate — the fiat price is converted to a fixed crypto amount for the "
     "duration of the payment window; merchants carry zero volatility risk.\n"
     "• Guaranteed funds — Triple-A monitors the blockchain and confirms valid payments within "
     "seconds (stablecoins); once confirmed, funds are guaranteed to the merchant even before deep "
     "on-chain confirmation.\n"
     "• Fiat settlement — merchant balance is credited in local currency (USD for IDT) at the "
     "guaranteed rate; bank settlement next business day. IDT never holds crypto.\n"
     "• No chargebacks — transactions are irreversible; refunds are explicit outbound payouts.\n"
     "• API + webhooks — REST API to create payment requests (with order reference, notify_url "
     "webhook, and notify_secret for verification), webhook notifications on status change, and "
     "status polling as a fallback. Sandbox environment and Postman collection available.\n"
     "• Compliance layer — Triple-A performs payer-side wallet screening, sanctions/blockchain "
     "analytics, and applicable KYC/travel-rule obligations as the licensed money services provider."
    ),

    # ── 3. Target Architecture ───────────────────────────────────────────
    ("h2", "3. Target Payment Architecture — IDTPay Ecosystem ↔ IDTPay ↔ Triple-A"),
    ("h3", "3.1 Components and responsibilities"),
    ("body",
     "BOSS Revolution DTC channels (app / web) — IDTPay ecosystem edge\n"
     "Owns the IMTU shopping experience: product selection, recipient, checkout UI, payment-method "
     "selection. Renders the new \"Pay with Crypto\" option and hosts the Triple-A checkout webview.\n\n"
     "IMTU Order Service — IDTPay ecosystem\n"
     "Owns the order: catalog, pricing, order state, and top-up fulfillment through IDT's carrier "
     "hub once payment is confirmed. Unchanged by this project except for new payment states.\n\n"
     "IDTPay (payment orchestration) — the integration point\n"
     "Owns payment intents, tender routing, and the ledger. Today it routes to the card PSP adapter "
     "(credit/debit) and the BOSS Money wallet adapter. We add a third adapter: the Triple-A Crypto "
     "Adapter, which encapsulates all Triple-A API calls, webhook handling, status mapping, and "
     "reconciliation ingestion. To the rest of IDTPay, crypto is just another tender with the same "
     "intent lifecycle.\n\n"
     "Triple-A (licensed crypto PSP) — external\n"
     "Owns everything crypto: hosted checkout, rate lock, blockchain monitoring, payment guarantee, "
     "compliance screening, fiat conversion, and USD bank settlement to IDT.\n\n"
     "Finance / Reconciliation — IDTPay ecosystem\n"
     "Ingests Triple-A settlement reports, matches them to IDTPay ledger entries and the bank "
     "credit, posts GL entries, and routes breaks to an ops queue."
    ),
    ("h3", "3.2 Architecture principles"),
    ("body",
     "1. No crypto custody at IDT — all crypto exposure (wallets, keys, volatility, conversion) "
     "stays with Triple-A. IDT's books see only USD.\n"
     "2. Adapter pattern inside IDTPay — Triple-A sits behind the same payment-intent interface as "
     "the card PSP; IMTU and channel teams integrate once against IDTPay, not against Triple-A.\n"
     "3. Fulfill only on confirmed payment — the IMTU top-up fires only after IDTPay receives and "
     "cryptographically verifies Triple-A's \"paid\" webhook (or confirms via status poll). Never on "
     "client-side redirect alone.\n"
     "4. Idempotency everywhere — webhook delivery can repeat; order fulfillment and ledger posting "
     "must be idempotent on the Triple-A payment reference.\n"
     "5. Fiat-denominated — the customer owes a USD amount; the crypto amount is Triple-A's "
     "problem. Receipts show USD (plus crypto paid, for transparency).\n"
     "6. Feature-flagged rollout — enable by platform, corridor, and amount band; instant kill "
     "switch that removes the tender from the payment-method list."
    ),
    ("h3", "3.3 High-level flow (one line per hop)"),
    ("body",
     "Customer → BR app: chooses IMTU product, taps Pay with Crypto\n"
     "BR app → IDTPay: create payment intent (orderId, USD amount, tender=CRYPTO_TRIPLEA)\n"
     "IDTPay → Triple-A: OAuth2 client-credentials token, then create payment request "
     "(order_ref, amount, currency, notify_url, success/cancel URLs)\n"
     "Triple-A → IDTPay: hosted checkout URL + payment reference + rate-lock expiry\n"
     "IDTPay → BR app: hosted checkout URL\n"
     "BR app → Customer: opens Triple-A checkout (webview); QR code + locked crypto amount + timer\n"
     "Customer wallet → blockchain → Triple-A: customer sends crypto from their own wallet\n"
     "Triple-A → IDTPay: signed webhook \"paid\" (verified with notify_secret; poll as fallback)\n"
     "IDTPay → IMTU Order Service: payment confirmed event → top-up fulfillment via carrier hub\n"
     "BR app → Customer: success screen, receipt, delivery notification\n"
     "Triple-A → IDT bank: next-business-day USD settlement, net of fees, with settlement report\n"
     "Finance: three-way reconciliation (report ↔ IDTPay ledger ↔ bank credit)"
    ),

    # ── 4. Workflow 1: happy path ────────────────────────────────────────
    ("h2", "4. Workflow 1 — End-to-End Purchase (Happy Path)"),
    ("body",
     "Step 1 — [Customer / BR app] Customer selects an IMTU product and recipient and proceeds to "
     "checkout (existing flow, unchanged).\n\n"
     "Step 2 — [BR app → IDTPay] Checkout requests eligible payment methods. IDTPay applies "
     "eligibility rules (feature flag on, platform enabled, corridor enabled, USD amount within "
     "min/max band) and returns: Credit Card, Debit Card, BOSS Money Wallet, and Crypto (Triple-A).\n\n"
     "Step 3 — [Customer] Selects \"Pay with Crypto\" (first-time users see a short education "
     "sheet: what it is, that price is locked, that they need their own wallet).\n\n"
     "Step 4 — [BR app → IDTPay] App requests a payment intent: {orderId, amount: USD, tender: "
     "CRYPTO_TRIPLEA}. IDTPay creates the intent in state CREATED.\n\n"
     "Step 5 — [IDTPay → Triple-A] The Triple-A Crypto Adapter authenticates (OAuth2 "
     "client-credentials) and creates a payment request carrying: our order reference, USD amount "
     "and currency, webhook notify_url + notify_secret, and success/cancel return URLs.\n\n"
     "Step 6 — [Triple-A → IDTPay] Triple-A responds with the hosted payment URL, its payment "
     "reference, and the rate-lock expiry. IDTPay persists the mapping (orderId ↔ payment "
     "reference), moves the intent to PENDING_CUSTOMER, and returns the URL to the app.\n\n"
     "Step 7 — [Customer on Triple-A hosted checkout] In a secure in-app webview, the customer "
     "picks coin and network (e.g., USDC on a low-fee network), and sees the exact crypto amount at "
     "the locked rate, a QR code / address, and a countdown timer.\n\n"
     "Step 8 — [Customer wallet → blockchain] Customer pays from their own wallet: scan QR on "
     "another device, copy address/amount, or tap a wallet deep link on mobile.\n\n"
     "Step 9 — [Triple-A] Detects the transaction on-chain, validates amount/asset/network, and "
     "guarantees the funds — for stablecoins this is typically seconds. Checkout shows "
     "\"Payment received.\"\n\n"
     "Step 10 — [Triple-A → IDTPay] Sends the signed \"paid\" webhook to notify_url. IDTPay "
     "verifies the signature with notify_secret, idempotently transitions the intent to PAID, "
     "writes the ledger entry, and emits a payment-confirmed event. (A scheduled status poll "
     "covers missed webhooks.)\n\n"
     "Step 11 — [IMTU Order Service] Consumes the event and fires the top-up through IDT's carrier "
     "hub; on carrier confirmation the order is COMPLETED.\n\n"
     "Step 12 — [BR app] The webview success redirect returns the customer to the app; the app "
     "confirms against IDTPay (never trusts the redirect alone) and shows success + receipt (USD "
     "amount, crypto amount paid, coin/network, Triple-A reference). Push/SMS delivery "
     "notification follows.\n\n"
     "Step 13 — [Async, Triple-A → IDT bank] Funds convert to USD at the locked rate and settle to "
     "IDT's bank account next business day (see Workflow 3)."
    ),

    # ── 5. Workflow 2: lifecycle & exceptions ────────────────────────────
    ("h2", "5. Workflow 2 — Payment Lifecycle & Exception Handling"),
    ("body",
     "IDTPay intent states for the crypto tender:\n"
     "CREATED → PENDING_CUSTOMER → PAID → (fulfillment) COMPLETED\n"
     "plus exception states: EXPIRED, SHORT_PAID, OVERPAID, LATE_PAYMENT, REFUND_PENDING, "
     "REFUNDED, CANCELLED.\n\n"
     "A) Abandonment / expiry\n"
     "Customer never pays before the rate-lock countdown ends. Triple-A marks the request expired; "
     "IDTPay (webhook or poll) moves the intent to EXPIRED and releases the order. App UX: "
     "\"Payment window expired — get a new quote\" with one tap to re-create the intent (Step 4). "
     "No funds moved, nothing to refund.\n\n"
     "B) Underpayment (short payment)\n"
     "Customer sends less than the quoted crypto amount (wrong amount, wallet fee deducted). "
     "Triple-A flags a short payment. IDTPay holds the intent in SHORT_PAID and never fulfills. "
     "Resolution options (policy to finalize with Triple-A): customer tops up the difference within "
     "the window on the same hosted form, or the partial amount is refunded per Triple-A's process. "
     "Order auto-cancels if unresolved by timeout.\n\n"
     "C) Overpayment\n"
     "Customer sends more than quoted. The order is fulfilled normally (intent OVERPAID → PAID "
     "path), and the excess follows the refund policy — refund of the excess via Triple-A, or "
     "(recommended) offer credit to the customer's BOSS Money wallet.\n\n"
     "D) Late on-chain payment (after expiry)\n"
     "Funds arrive after the rate lock ended. Triple-A treats it as a late/held payment, not a "
     "valid purchase. IDTPay marks LATE_PAYMENT; the order is not fulfilled; funds are returned via "
     "the refund path. CS tooling must be able to look these up by Triple-A reference.\n\n"
     "E) Fulfillment failure after successful payment\n"
     "Payment is PAID but the carrier top-up terminally fails after retries. Options presented to "
     "the customer, in order: (1) instant credit to BOSS Money wallet (preferred — keeps funds in "
     "ecosystem, instant, no crypto payout needed); (2) fiat-value crypto refund via Triple-A "
     "payout to the customer's wallet address. Intent moves REFUND_PENDING → REFUNDED.\n\n"
     "F) Webhook outage\n"
     "If the webhook is missed (network, deploy), the reconciliation poller queries Triple-A "
     "payment status for all PENDING_CUSTOMER intents older than N minutes, so no paid order is "
     "ever stranded."
    ),

    # ── 6. Workflow 3: settlement & recon ────────────────────────────────
    ("h2", "6. Workflow 3 — Settlement & Reconciliation (T+1)"),
    ("body",
     "Step 1 — [Day D, Triple-A] Every confirmed payment is credited to IDT's Triple-A merchant "
     "balance in USD at the rate locked at checkout (a \"local currency account\" — IDT's balance "
     "is never held in crypto).\n\n"
     "Step 2 — [Day D+1, Triple-A → IDT bank] Triple-A initiates a bank payout of the accumulated "
     "USD balance, net of processing fees, to IDT's designated settlement account (cadence and "
     "minimums per commercial agreement).\n\n"
     "Step 3 — [Triple-A → Finance] A settlement report accompanies the payout (dashboard / API / "
     "file): one line per transaction with Triple-A payment reference, our order reference, gross "
     "USD, fee, net USD, coin/network, and timestamps.\n\n"
     "Step 4 — [IDTPay Recon] Automated three-way match: settlement report line ↔ IDTPay ledger "
     "entry (by order reference) ↔ aggregate bank credit. Refunds and short/over payments appear "
     "as adjustment lines and are matched to their intents.\n\n"
     "Step 5 — [Ops] Unmatched lines route to the existing recon exceptions queue with the "
     "Triple-A reference attached.\n\n"
     "Step 6 — [Finance] GL posting: crypto-tender sales, Triple-A fees, settlement clearing "
     "account. Month-end: Triple-A statement vs. GL tie-out."
    ),

    # ── 7. Workflow 4: refunds ───────────────────────────────────────────
    ("h2", "7. Workflow 4 — Refunds"),
    ("body",
     "Crypto payments are push-based and irreversible — there is no chargeback rail. Every refund "
     "is therefore an explicit, IDT-initiated outbound payout, always denominated in the original "
     "USD amount (never the crypto amount — FX movement since purchase is not the customer's risk "
     "or windfall).\n\n"
     "Step 1 — [CS / automated flow] Refund is approved for order X (customer request, failed "
     "fulfillment, over/short resolution).\n\n"
     "Step 2 — [Customer choice] (a) BOSS Money wallet credit — instant, free, keeps funds in the "
     "IDT ecosystem; the default and recommended path; or (b) crypto refund — customer provides a "
     "receiving wallet address in the app.\n\n"
     "Step 3 — [If crypto refund: IDTPay → Triple-A] The adapter calls Triple-A's payout API for "
     "the USD value; Triple-A performs its compliance checks (wallet screening, travel rule where "
     "applicable), converts, and sends crypto to the customer's address.\n\n"
     "Step 4 — [IDTPay] Intent REFUND_PENDING → REFUNDED on Triple-A's payout confirmation "
     "webhook; ledger contra-entry posted; refund appears in the next settlement report as an "
     "adjustment.\n\n"
     "Policy notes: set a refund SLA (e.g., 1–2 business days); require the refund address to be "
     "customer-confirmed in-app (mistyped addresses are unrecoverable); wallet-credit path should "
     "be incentivized in UX copy."
    ),

    # ── 8. DTC customer flow ─────────────────────────────────────────────
    ("h2", "8. DTC Customer Step-by-Step Flow (Screen by Screen)"),
    ("body",
     "Screen 1 — IMTU checkout (existing). Product, recipient number and carrier, USD amount. "
     "CTA: Continue to payment.\n\n"
     "Screen 2 — Payment method. Four tiles: Credit Card, Debit Card, BOSS Money Wallet, and new "
     "\"Crypto — USDC, USDT, BTC, ETH & more\". Subcopy: \"Price locked in USD. No card needed.\"\n\n"
     "Screen 3 — First-time education sheet (once per user). Three bullets: pay from your own "
     "crypto wallet; exchange rate locked for the payment window; top-up delivered as soon as "
     "payment confirms. CTA: Continue.\n\n"
     "Screen 4 — Triple-A hosted checkout (secure in-app webview, white-labeled to BOSS "
     "Revolution). Customer picks coin and network; sees exact crypto amount, QR code, address, "
     "and countdown timer (rate-lock window).\n\n"
     "Screen 5 — Pay. Mobile: tap wallet deep link (opens their wallet app pre-filled) or copy "
     "address + amount. Desktop web: scan QR with phone wallet.\n\n"
     "Screen 6 — Confirming. \"Waiting for your payment…\" flips to \"Payment received\" within "
     "seconds for stablecoins. Webview redirects back to the app.\n\n"
     "Screen 7 — Success (BR app, rendered only after IDTPay confirms PAID). \"Your top-up is on "
     "its way\" → delivery confirmation push. Receipt shows USD amount, crypto paid "
     "(amount + coin + network), rate, and reference ID.\n\n"
     "Unhappy paths: timer expires → \"Get a new quote\" (one tap); payment short → clear "
     "instruction to send the remainder or get refunded; any hard failure → \"Try another payment "
     "method\" returns to Screen 2 with card/wallet preselected."
    ),

    # ── 9. Integration requirements ──────────────────────────────────────
    ("h2", "9. Integration Requirements & Workstreams"),
    ("body",
     "Commercial / setup\n"
     "• Merchant agreement with Triple-A: pricing (flat fee ~0.8–1% publicly referenced — "
     "confirm), settlement cadence and account, enabled coins/networks, refund/short-payment "
     "policy, sandbox access.\n"
     "• Legal/compliance review: IDT-side state coverage analysis for offering the tender, T&C and "
     "receipt disclosure updates, marketing claims review.\n\n"
     "IDTPay (BE)\n"
     "• New Triple-A Crypto Adapter: OAuth2 client-credentials auth, create-payment call, status "
     "poll, payout (refund) call.\n"
     "• Public webhook endpoint with notify_secret signature verification, idempotent processing, "
     "and replay protection.\n"
     "• Intent state machine extension (states in Section 5) + ledger entries for the new tender.\n"
     "• Reconciliation ingestion of Triple-A settlement reports; poller for stranded intents.\n"
     "• Eligibility rules + feature flags (platform, corridor, amount band) + kill switch.\n\n"
     "BOSS Revolution app / web (APP)\n"
     "• Payment-method tile + education sheet + webview integration with return-URL handling.\n"
     "• Success/failure/expiry states wired to IDTPay intent status (never the redirect alone).\n"
     "• Receipt additions (crypto amount, coin, network, reference).\n"
     "• Refund address capture UX for crypto refunds; wallet-credit default.\n\n"
     "Data / QA / Ops\n"
     "• Amplitude funnel events: crypto_offered, crypto_selected, checkout_opened, qr_shown, "
     "paid, expired, short_paid, refunded — to measure conversion vs. card.\n"
     "• QA against Triple-A sandbox (Postman collection available) incl. webhook signature and "
     "idempotency tests.\n"
     "• CS tooling: look up by Triple-A reference; refund runbooks.\n\n"
     "Note: exact Triple-A endpoint names, field names, and rate-lock window durations must be "
     "confirmed against their current API documentation (developers.triple-a.io) during technical "
     "onboarding — the developer portal requires an account for full detail."
    ),

    # ── 10. Compliance & risk ────────────────────────────────────────────
    ("h2", "10. Compliance, Risk & Open Questions"),
    ("body",
     "Compliance posture\n"
     "• Triple-A is the licensed layer: FinCEN MSB + US MTLs (NMLS 2514255), MAS Major Payment "
     "Institution (Singapore), EU PI (ACPR) + CASP (AMF), FINTRAC/Bank of Canada. Payer wallet "
     "screening, sanctions, and blockchain analytics are theirs.\n"
     "• IDT never custodies crypto, which keeps IDT largely outside crypto-licensing scope — but "
     "IDT legal must confirm state-by-state availability and any disclosure requirements before "
     "launch.\n\n"
     "Risk considerations\n"
     "• Fraud: no chargebacks removes card-style friendly fraud on this tender; conversely, "
     "stolen-crypto risk sits with the payer side and Triple-A's screening. Keep IMTU velocity "
     "limits; consider conservative per-user/day caps at launch.\n"
     "• UX risk: small IMTU denominations ($5–$50) make network fees material for BTC/ETH L1 — "
     "default and promote stablecoins on low-fee networks.\n"
     "• Operational: irreversible mistaken payments (wrong amount/asset) create CS load — hosted "
     "checkout minimizes this, but runbooks are required.\n\n"
     "Open questions for Triple-A / internal decision\n"
     "1. Final pricing, settlement cadence, and minimum payout threshold.\n"
     "2. Which coins/networks to enable at launch (recommend USDC + USDT on low-fee networks, "
     "BTC/ETH optional).\n"
     "3. Exact rate-lock window and short-payment top-up rules.\n"
     "4. Hosted redirect vs. embedded form — recommend hosted webview for PCI-like scope "
     "minimization and fastest launch.\n"
     "5. Refund mechanics and fees for crypto payouts; confirm BOSS Money wallet credit is "
     "compliant as the default refund path.\n"
     "6. US state coverage map vs. BOSS Revolution DTC footprint.\n\n"
     "Suggested rollout\n"
     "Phase 1: single platform (app), US senders, USDC/USDT only, conservative caps, feature "
     "flag. Phase 2: expand coins/corridors, add web. Phase 3: evaluate crypto for other BOSS "
     "products (eGift, eSIM, Money) on the same IDTPay adapter."
    ),

    # ── Sources ──────────────────────────────────────────────────────────
    ("h2", "Sources"),
    ("body",
     "• Triple-A — Digital currency payments: https://www.triple-a.io/digital-currency-payments\n"
     "• Triple-A — Developer/API documentation portal: https://developers.triple-a.io\n"
     "• Triple-A — Company/licensing information: https://www.triple-a.io\n"
     "All Triple-A product claims (rate lock, settlement, licensing, no-chargeback) sourced from "
     "Triple-A public materials as of July 2026; API specifics to be validated in technical "
     "onboarding."
    ),
]


def main():
    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)

    print("Creating Google Doc...")
    doc = docs_svc.documents().create(body={"title": DOC_TITLE}).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"  Doc ID: {doc_id}")

    requests = []
    # Reverse order: every block inserts at index 1, so the last-processed
    # block ends up at the top of the document.
    for block_type, content in reversed(BLOCKS):
        if block_type == "h1":
            requests += [ins(content), para_style(content, "HEADING_1")]
        elif block_type == "h2":
            requests += [ins(content), para_style(content, "HEADING_2")]
        elif block_type == "h3":
            requests += [ins(content), para_style(content, "HEADING_3")]
        elif block_type == "body":
            requests += [ins(content), para_style(content, "NORMAL_TEXT")]

    print(f"Sending {len(requests)} requests to Google Docs...")
    for i in range(0, len(requests), 50):
        chunk = requests[i:i + 50]
        for attempt in range(3):
            try:
                docs_svc.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": chunk},
                ).execute()
                print(f"  Processed {i + 1}–{i + len(chunk)}")
                break
            except Exception as e:
                if attempt < 2:
                    print(f"  Retry {attempt + 1}/2: {str(e)[:80]}")
                    time.sleep(1.0)
                else:
                    raise
        time.sleep(0.2)

    print("\n✅  Done!")
    print(f"   Google Doc: {doc_url}\n")

    import webbrowser
    webbrowser.open(doc_url)


if __name__ == "__main__":
    main()
