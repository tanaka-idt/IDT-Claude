"""
Generates visual diagrams for the Triple-A crypto payment workflows and
inserts them into the existing Google Doc
"BOSS Revolution IMTU — Crypto Payments via Triple-A (Architecture & Workflows)".

1. Renders 6 PNG diagrams with matplotlib (150 DPI).
2. Uploads them to Google Drive (anyone-with-link reader, required by Docs API).
3. Inserts each image + caption directly under its matching section heading.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

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

DOC_ID = "1W_KwGlC1ebxmakFTvaNwlHmOmVJxd5jnRqv0IGyRlIQ"

# ── palette ───────────────────────────────────────────────────────────────────
CUST = dict(fc="#E3F2FD", ec="#1565C0")   # customer
APP  = dict(fc="#E8EAF6", ec="#3949AB")   # BOSS Revolution app
PAY  = dict(fc="#EDE7F6", ec="#5E35B1")   # IDTPay
TRI  = dict(fc="#FFF3E0", ec="#EF6C00")   # Triple-A
CHN  = dict(fc="#E0F2F1", ec="#00897B")   # blockchain / wallet
FUL  = dict(fc="#E8F5E9", ec="#2E7D32")   # IMTU fulfillment / success
BNK  = dict(fc="#EFEBE9", ec="#6D4C41")   # bank / finance
ERR  = dict(fc="#FFEBEE", ec="#C62828")   # error / exception
WRN  = dict(fc="#FFF8E1", ec="#F9A825")   # warning / pending
GRY  = dict(fc="#ECEFF1", ec="#607D8B")   # neutral


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


# ── drawing helpers ───────────────────────────────────────────────────────────
def new_fig(w_in, h_in, xmax, ymax, title):
    fig, ax = plt.subplots(figsize=(w_in, h_in))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
    ax.text(xmax / 2, ymax - 2.2, title, ha="center", va="top",
            fontsize=14, fontweight="bold", color="#212121")
    return fig, ax


def box(ax, x, y, w, h, text, c, fs=9.5, bold=False, lw=1.4, z=2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.0",
        linewidth=lw, edgecolor=c["ec"], facecolor=c["fc"], zorder=z))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#212121",
            zorder=z + 1, linespacing=1.3)


def arrow(ax, x1, y1, x2, y2, label="", color="#455A64", fs=8.5,
          dashed=False, dy=1.1, lw=1.7, ha="center"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                linestyle=(0, (4, 3)) if dashed else "-",
                                shrinkA=3, shrinkB=3, mutation_scale=15),
                zorder=4)
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, label, ha=ha, va="bottom",
                fontsize=fs, color="#263238", zorder=6,
                bbox=dict(boxstyle="round,pad=0.18", fc="white",
                          ec="#B0BEC5", lw=0.5, alpha=0.95))


def save(fig, name):
    out = BASE / name
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  saved {name}")
    return out


# ── D1: architecture overview ────────────────────────────────────────────────
def d1_architecture():
    fig, ax = new_fig(12, 8, 120, 80,
                      "Payment Architecture — BOSS Revolution ↔ IDTPay ↔ Triple-A")

    box(ax, 2, 56, 20, 12, "DTC Customer", CUST, fs=11, bold=True)
    box(ax, 28, 56, 24, 12,
        "BOSS Revolution App / Web\nIMTU checkout\n(hosts Triple-A webview)", APP, bold=True)
    box(ax, 2, 30, 20, 10, "Customer's own\ncrypto wallet", CHN)
    box(ax, 28, 30, 24, 10, "Blockchain networks\nUSDC · USDT · BTC · ETH", CHN)

    # IDTPay container + adapters
    box(ax, 58, 36, 30, 34, "", PAY, lw=1.8)
    ax.text(73, 66.5, "IDTPay — payment orchestration\n(intents · routing · ledger)",
            ha="center", va="center", fontsize=10, fontweight="bold", zorder=3)
    box(ax, 60.5, 54.5, 25, 5.5, "Card PSP adapter (credit / debit)", GRY, fs=8.5, z=3)
    box(ax, 60.5, 47, 25, 5.5, "BOSS Money wallet adapter", GRY, fs=8.5, z=3)
    box(ax, 60.5, 39.5, 25, 5.5, "Triple-A crypto adapter — NEW", TRI, fs=8.5, bold=True, z=3)

    # Triple-A container
    box(ax, 94, 36, 24, 34, "", TRI, lw=1.8)
    ax.text(106, 66.5, "Triple-A\nlicensed crypto PSP",
            ha="center", va="center", fontsize=10, fontweight="bold", zorder=3)
    box(ax, 96, 56.5, 20, 5.5, "Hosted checkout (QR)", GRY, fs=8.5, z=3)
    box(ax, 96, 49.5, 20, 5.5, "Rate lock & FX to USD", GRY, fs=8.5, z=3)
    box(ax, 96, 42.5, 20, 5.5, "AML / wallet screening", GRY, fs=8.5, z=3)

    box(ax, 58, 12, 30, 10, "IMTU Order Service + Carrier Hub\n(top-up fulfillment)", FUL, bold=True)
    box(ax, 94, 12, 24, 10, "IDT bank account\nFinance & Reconciliation", BNK, bold=True)

    arrow(ax, 22, 62, 28, 62, "buys IMTU")
    arrow(ax, 52, 62, 58, 62, "payment intent")
    arrow(ax, 85.5, 41, 94, 41, "create payment (REST)", dy=-3.2)
    arrow(ax, 94, 44.5, 85.5, 44.5, "hosted URL · webhook: paid", dashed=True, ha="right")
    arrow(ax, 12, 56, 12, 40, "pays from\nown wallet", ha="left", dy=0)
    arrow(ax, 22, 35, 28, 35, "send tx")
    arrow(ax, 52, 34, 94, 37.5, "on-chain payment detected", color=CHN["ec"])
    arrow(ax, 73, 36, 73, 22, "payment confirmed → fulfill", color=FUL["ec"])
    arrow(ax, 106, 36, 106, 22, "T+1 USD settlement + report", color=BNK["ec"])
    arrow(ax, 97, 22, 87, 36, "3-way recon\nvs ledger", dashed=True, color=BNK["ec"], fs=8, dy=-5.5)

    return save(fig, "crypto_flow_1_architecture.png")


# ── D2: workflow 1 happy path (sequence) ─────────────────────────────────────
def d2_happy_path():
    fig, ax = new_fig(12, 10, 134, 100,
                      "Workflow 1 — End-to-End Purchase (Happy Path)")

    lanes = [
        ("Customer", 10, CUST), ("BR App", 32, APP), ("IDTPay", 56, PAY),
        ("Triple-A", 82, TRI), ("Blockchain", 104, CHN), ("IMTU / Carrier", 122, FUL),
    ]
    X = {name: x for name, x, _ in lanes}
    for name, x, c in lanes:
        box(ax, x - 9, 87.5, 18, 6, name, c, fs=10, bold=True)
        ax.plot([x, x], [6, 87.5], ls=(0, (3, 3)), color="#B0BEC5", lw=1.1, zorder=1)

    steps = [
        ("Customer", "BR App", "1. Select IMTU product · choose Pay with Crypto"),
        ("BR App", "IDTPay", "2. Create payment intent (orderId, USD amount)"),
        ("IDTPay", "Triple-A", "3. OAuth2 + create payment request (order_ref, notify_url)"),
        ("Triple-A", "IDTPay", "4. Payment ref + hosted checkout URL + rate-lock expiry"),
        ("IDTPay", "BR App", "5. Hosted URL — intent: PENDING_CUSTOMER"),
        ("BR App", "Customer", "6. Open hosted checkout: QR · locked amount · timer"),
        ("Customer", "Blockchain", "7. Pay from own wallet (scan QR / deep link / copy address)"),
        ("Blockchain", "Triple-A", "8. Tx detected & validated (seconds for stablecoins)"),
        ("Triple-A", "IDTPay", "9. Signed 'paid' webhook (notify_secret) — intent: PAID"),
        ("IDTPay", "IMTU / Carrier", "10. Payment-confirmed event"),
        (None, None, "11. Top-up fulfilled via carrier hub → delivered"),
        ("BR App", "Customer", "12. Success + receipt (USD + crypto paid)"),
        (None, None, None),  # step 13 drawn manually (settlement)
    ]
    y = 83
    for frm, to, label in steps:
        if label is None:
            pass
        elif frm is None:  # self-step on IMTU lane
            box(ax, X["IMTU / Carrier"] - 21, y - 2.4, 30, 4.8, label, FUL, fs=8)
        else:
            ha = "left" if "6." in label else "center"
            arrow(ax, X[frm], y, X[to], y, label, dy=0.9, fs=8.3, ha=ha)
        y -= 6.2

    box(ax, 96, 3, 34, 5.5, "IDT bank — T+1 USD settlement (net of fees)", BNK, fs=8.5)
    arrow(ax, X["Triple-A"], 12, 100, 8, "13. convert at locked rate → settle",
          dashed=True, color=BNK["ec"], fs=8, dy=0.6)

    return save(fig, "crypto_flow_2_happy_path.png")


# ── D3: workflow 2 lifecycle states ──────────────────────────────────────────
def d3_lifecycle():
    fig, ax = new_fig(12, 8, 120, 80,
                      "Workflow 2 — Payment Intent Lifecycle & Exception States")

    box(ax, 4, 46, 16, 9, "CREATED", APP, bold=True)
    box(ax, 28, 46, 24, 9, "PENDING_\nCUSTOMER", WRN, bold=True)
    box(ax, 60, 46, 14, 9, "PAID", FUL, bold=True)
    box(ax, 100, 46, 17, 9, "COMPLETED", FUL, bold=True)
    arrow(ax, 20, 50.5, 28, 50.5, "hosted URL\nreturned", fs=8, dy=0.8)
    arrow(ax, 52, 50.5, 60, 50.5, "webhook 'paid'\nverified", fs=8, dy=0.8)
    arrow(ax, 74, 50.5, 100, 50.5, "top-up fulfilled", fs=8)

    box(ax, 28, 64, 18, 8, "EXPIRED", ERR, bold=True)
    box(ax, 4, 64, 16, 8, "CANCELLED", GRY, bold=True)
    arrow(ax, 39, 55, 38, 64, "timer ends,\nno payment", fs=8, dy=0.2, ha="left")
    arrow(ax, 28, 68, 20, 68, "order released", fs=8, dy=0.5)
    ax.text(48, 67, "(retry = new intent, new quote)",
            ha="left", fontsize=8, style="italic", color="#616161")

    box(ax, 18, 28, 18, 8, "SHORT_PAID\nnever fulfill", WRN, bold=True, fs=8.5)
    box(ax, 46, 28, 20, 9, "OVERPAID\nfulfill · refund excess", WRN, bold=True, fs=8.5)
    box(ax, 2, 12, 22, 8, "LATE_PAYMENT", ERR, bold=True)
    box(ax, 68, 20, 22, 8, "REFUND_\nPENDING", WRN, bold=True)
    box(ax, 100, 20, 17, 8, "REFUNDED", GRY, bold=True)

    arrow(ax, 33, 46, 27, 36, "underpaid", fs=8, dy=0.3, ha="right")
    arrow(ax, 27, 36, 60, 47, "tops up in window", dashed=True, fs=8, dy=0.5)
    arrow(ax, 46, 46, 54, 37, "overpaid", fs=8, dy=0.1, ha="left")
    arrow(ax, 58, 37, 64, 46)
    arrow(ax, 28, 66, 10, 20, "funds arrive\nafter expiry", fs=8, dy=0, ha="right")
    arrow(ax, 24, 16, 68, 22, "auto-refund (no fulfillment)", fs=8, dy=0.8)
    arrow(ax, 36, 30, 68, 24, "unresolved by timeout", fs=8, dy=-2.8)
    arrow(ax, 67, 46, 76, 28, "carrier fulfillment fails\n(terminal, after retries)", fs=8, dy=0.4, ha="left")
    arrow(ax, 90, 24, 100, 24, "payout\nconfirmed", fs=8, dy=0.4)

    ax.text(60, 4, "Refund destination: BOSS Money wallet credit (default, instant) "
                   "or crypto payout via Triple-A — always the original USD amount.",
            ha="center", fontsize=8.5, style="italic", color="#455A64")

    return save(fig, "crypto_flow_3_lifecycle_states.png")


# ── D4: workflow 3 settlement & recon ────────────────────────────────────────
def d4_settlement():
    fig, ax = new_fig(12, 7, 120, 70,
                      "Workflow 3 — T+1 Settlement & Three-Way Reconciliation")

    ax.plot([58, 58], [4, 60], ls=(0, (5, 4)), color="#90A4AE", lw=1.4)
    ax.text(29, 60, "Day D", ha="center", fontsize=11, fontweight="bold", color="#546E7A")
    ax.text(89, 60, "Day D+1 (next business day)", ha="center", fontsize=11,
            fontweight="bold", color="#546E7A")

    box(ax, 3, 38, 24, 13, "Confirmed crypto\npayments\n(each at locked FX rate)", TRI)
    box(ax, 31, 38, 24, 13, "IDT merchant balance\ncredited in USD\n(never held in crypto)", TRI)
    box(ax, 62, 38, 24, 13, "Bank payout initiated\n(net of Triple-A fees)", BNK)
    box(ax, 92, 38, 25, 13, "IDT settlement\naccount credited\n(aggregate USD)", BNK)
    box(ax, 62, 14, 24, 13, "Settlement report\nper txn: refs, gross,\nfee, net, FX", APP)
    box(ax, 92, 14, 25, 13, "IDTPay 3-way match\nreport ↔ ledger ↔\nbank credit", PAY, bold=True)
    box(ax, 62, 1, 24, 9, "Matched →\nGL posting (Finance)", FUL, fs=8.5)
    box(ax, 92, 1, 25, 9, "Breaks →\nOps exceptions queue", ERR, fs=8.5)

    arrow(ax, 27, 44.5, 31, 44.5)
    arrow(ax, 55, 44.5, 62, 44.5, "T+1")
    arrow(ax, 86, 44.5, 92, 44.5)
    arrow(ax, 74, 38, 74, 27, "accompanies\npayout", fs=8, dy=0, ha="left")
    arrow(ax, 104.5, 38, 104.5, 27, "bank credit", fs=8, dy=0, ha="left")
    arrow(ax, 86, 20.5, 92, 20.5)
    arrow(ax, 92, 16, 86, 8, "", color=FUL["ec"])
    arrow(ax, 104.5, 14, 104.5, 10, "", color=ERR["ec"])

    return save(fig, "crypto_flow_4_settlement_recon.png")


# ── D5: workflow 4 refunds ───────────────────────────────────────────────────
def d5_refunds():
    fig, ax = new_fig(12, 8, 120, 80, "Workflow 4 — Refund Decision Flow")

    box(ax, 35, 64, 50, 9,
        "Refund approved\nCS request · failed fulfillment · over-/short-payment resolution",
        WRN, bold=True)

    ax.add_patch(Polygon([(60, 58), (79, 50), (60, 42), (41, 50)],
                         closed=True, facecolor=PAY["fc"], edgecolor=PAY["ec"],
                         lw=1.5, zorder=2))
    ax.text(60, 50, "Customer chooses\nrefund method", ha="center", va="center",
            fontsize=9.5, fontweight="bold", zorder=3)
    arrow(ax, 60, 64, 60, 58)

    ax.text(17, 60, "Crypto has no chargebacks —\nevery refund is an explicit\noutbound payout, always for\nthe original USD amount.",
            ha="center", va="center", fontsize=8.5, style="italic", color="#455A64",
            bbox=dict(boxstyle="round,pad=0.5", fc="#FAFAFA", ec="#B0BEC5", lw=0.8))

    box(ax, 6, 30, 34, 12,
        "BOSS Money wallet credit\n(DEFAULT)\ninstant · free · stays in ecosystem", FUL, bold=True)
    arrow(ax, 41, 50, 23, 42, "wallet credit", fs=8.5, dy=0.8)

    box(ax, 76, 32, 38, 9,
        "Customer confirms receiving wallet\naddress in-app (unrecoverable if wrong)", CHN)
    arrow(ax, 79, 50, 95, 41, "crypto refund", fs=8.5, dy=0.8)
    box(ax, 76, 18, 38, 9,
        "IDTPay → Triple-A payout API (USD value)\ncompliance checks → crypto sent", TRI)
    arrow(ax, 95, 32, 95, 27)

    box(ax, 35, 3, 50, 9,
        "Intent: REFUND_PENDING → REFUNDED\nledger contra-entry · shows in next settlement report",
        PAY, bold=True)
    arrow(ax, 23, 30, 45, 12)
    arrow(ax, 95, 18, 75, 12)

    return save(fig, "crypto_flow_5_refunds.png")


# ── D6: DTC customer journey ─────────────────────────────────────────────────
def d6_customer_journey():
    fig, ax = new_fig(12, 7.5, 120, 75, "DTC Customer Journey — Screen by Screen")

    cards = [
        (2, 50, "1. IMTU checkout\nproduct · recipient ·\nUSD amount", APP),
        (32, 50, "2. Payment method\nnew Crypto tile +\ncard / debit / wallet", APP),
        (62, 50, "3. Education sheet\n(first time only)", APP),
        (92, 50, "4. Triple-A hosted checkout\ncoin + network · QR ·\nlocked amount · timer", TRI),
        (92, 27, "5. Pay from own wallet\ndeep link / scan QR /\ncopy address", TRI),
        (62, 27, "6. Confirming…\n'Payment received'\nin seconds", TRI),
        (32, 27, "7. Success + receipt\nUSD + crypto paid ·\ndelivery push", FUL),
    ]
    for x, y, t, c in cards:
        box(ax, x, y, 26, 13, t, c, fs=8.8, bold=True)

    arrow(ax, 28, 56.5, 32, 56.5)
    arrow(ax, 58, 56.5, 62, 56.5)
    arrow(ax, 88, 56.5, 92, 56.5)
    arrow(ax, 105, 50, 105, 40)
    arrow(ax, 92, 33.5, 88, 33.5)
    arrow(ax, 62, 33.5, 58, 33.5)

    ax.text(3, 19, "Unhappy paths", fontsize=9.5, fontweight="bold", color=ERR["ec"])
    box(ax, 2, 4, 36, 12, "Timer expires →\none tap 'Get a new quote'\n(back to screen 4)", ERR, fs=8.3)
    box(ax, 42, 4, 36, 12, "Short payment →\nsend remainder in window\nor get refunded", ERR, fs=8.3)
    box(ax, 82, 4, 36, 12, "Hard failure →\n'Try another payment method'\n(back to screen 2)", ERR, fs=8.3)

    return save(fig, "crypto_flow_6_customer_journey.png")


# ── Google Doc insertion ─────────────────────────────────────────────────────
# heading prefix → (png path, fig w_in, fig h_in, caption)
def build_targets(paths):
    return [
        ("3. Target Payment Architecture", paths[0], 12, 8,
         "Figure 1 — Component architecture: BOSS Revolution ↔ IDTPay ↔ Triple-A"),
        ("4. Workflow 1", paths[1], 12, 10,
         "Figure 2 — Workflow 1: end-to-end purchase (happy path)"),
        ("5. Workflow 2", paths[2], 12, 8,
         "Figure 3 — Workflow 2: payment intent lifecycle & exception states"),
        ("6. Workflow 3", paths[3], 12, 7,
         "Figure 4 — Workflow 3: T+1 settlement & three-way reconciliation"),
        ("7. Workflow 4", paths[4], 12, 8,
         "Figure 5 — Workflow 4: refund decision flow"),
        ("8. DTC Customer Step-by-Step", paths[5], 12, 7.5,
         "Figure 6 — DTC customer journey, screen by screen"),
    ]


# The Docs API only accepts publicly fetchable image URIs. IDT's Workspace
# policy blocks public Drive sharing (publishOutNotPermitted), and Drive
# thumbnailLinks are refused by the Docs image fetcher — so we serve the PNGs
# from this (public) GitHub repo instead. Commit + push the PNGs before running.
RAW_BASE = "https://raw.githubusercontent.com/tanaka-idt/IDT-Claude/main/"


def paragraph_text(element):
    if "paragraph" not in element:
        return ""
    parts = []
    for el in element["paragraph"].get("elements", []):
        parts.append(el.get("textRun", {}).get("content", ""))
    return "".join(parts)


def insert_into_doc(docs_svc, targets):
    doc = docs_svc.documents().get(documentId=DOC_ID).execute()
    content = doc["body"]["content"]

    inserts = []  # (index, uri, w_pt, h_pt, caption)
    for prefix, path, w_in, h_in, cap in targets:
        idx = None
        for element in content:
            if paragraph_text(element).strip().startswith(prefix):
                idx = element["endIndex"]
                break
        if idx is None:
            print(f"⚠️  heading not found: {prefix!r} — skipping")
            continue
        uri = RAW_BASE + path.name
        w_pt = 460
        h_pt = round(w_pt * h_in / w_in, 1)
        inserts.append((idx, uri, w_pt, h_pt, cap))

    # Insert bottom-up so earlier indices stay valid; one batch per image so
    # a single bad image doesn't fail the whole run.
    inserts.sort(key=lambda t: t[0], reverse=True)
    ok = 0
    for idx, uri, w_pt, h_pt, cap in inserts:
        cap_line = cap + "\n"
        requests = [
            {"insertInlineImage": {
                "location": {"index": idx}, "uri": uri,
                "objectSize": {"width": {"magnitude": w_pt, "unit": "PT"},
                               "height": {"magnitude": h_pt, "unit": "PT"}}}},
            {"insertText": {"location": {"index": idx + 1}, "text": "\n"}},
            {"updateParagraphStyle": {
                "range": {"startIndex": idx, "endIndex": idx + 2},
                "paragraphStyle": {"alignment": "CENTER", "namedStyleType": "NORMAL_TEXT"},
                "fields": "alignment,namedStyleType"}},
            {"insertText": {"location": {"index": idx + 2}, "text": cap_line}},
            {"updateParagraphStyle": {
                "range": {"startIndex": idx + 2, "endIndex": idx + 2 + len(cap_line)},
                "paragraphStyle": {"alignment": "CENTER", "namedStyleType": "NORMAL_TEXT"},
                "fields": "alignment,namedStyleType"}},
            {"updateTextStyle": {
                "range": {"startIndex": idx + 2, "endIndex": idx + 2 + len(cap)},
                "textStyle": {"italic": True,
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}},
        ]
        try:
            docs_svc.documents().batchUpdate(
                documentId=DOC_ID, body={"requests": requests}).execute()
            ok += 1
            print(f"  inserted: {cap[:60]}")
        except Exception as e:
            print(f"  ❌ insert failed for {cap[:40]}: {str(e)[:200]}")

    print(f"Inserted {ok}/{len(inserts)} images.")


def main():
    print("Rendering diagrams...")
    paths = [
        d1_architecture(),
        d2_happy_path(),
        d3_lifecycle(),
        d4_settlement(),
        d5_refunds(),
        d6_customer_journey(),
    ]

    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)

    insert_into_doc(docs_svc, build_targets(paths))

    print(f"\n✅  Done!")
    print(f"   https://docs.google.com/document/d/{DOC_ID}/edit\n")


if __name__ == "__main__":
    main()
