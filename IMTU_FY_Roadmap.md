# Boss Revolution — IMTU Product Roadmap
### Next Fiscal Year Strategy & Prioritized Initiative Plan
**Product line:** International Mobile Top-Up (IMTU)
**Prepared for:** DCS stakeholders & leadership
**Status:** Part 1 of 3 — IMTU (e-Gift and e-SIM roadmaps to follow)

---

## 1. Executive Summary

International Mobile Top-Up is the most strategically important product in the DCS portfolio right now — not because it is the largest revenue line, but because of *where it sits*. IMTU is the one Traditional-Communications-adjacent product still **growing** (it lives inside IDT Digital Payments, ~$104.4M in Q2 FY2026, +3% YoY, on the Zendit platform that more than doubled YoY), while the legacy BOSS Revolution Calling business is in deliberate decline (~-14% YoY). IMTU is therefore the **bridge product**: the high-frequency, low-stakes habit that migrates declining-calling diaspora users into the high-growth Fintech funnel (BOSS Money digital remittance grew +29.1% to $139.8M in FY2025; IDT Fintech swung to $15.4M operating income).

This roadmap proposes **10 IMTU initiatives** for the coming fiscal year. The unifying thesis is built on two structural truths from the market:

1. **The category is shifting from voice airtime to data bundles.** Global data use hit 23 GB/smartphone/month in 2025; in Africa, data is now ~39% of operator revenue and is lifting ARPU sharply (MTN $2.17 → $3.60). Plain $5 voice top-ups are being replaced by data/social bundles. IMTU must follow the value.
2. **Top-up is a frequency, retention and acquisition wedge — not a standalone profit center.** Every serious competitor treats it that way. Our advantage is unique: IMTU lives in **both** the Calling app and the Money app, making it the natural cross-sell engine no pure-play rival has.

Crucially, **9 of the 10 initiatives build directly on capabilities DCS already shipped this year** (the modular MTU component, redesigned MTU home, BLS automatic promos, Subly subscriptions, Validity-Based Reminders, Request Top-Up, the new RAF platform, and the DTC Universal API). This roadmap is mostly *composition and monetization of existing assets*, not greenfield build — which is why time-to-value is fast and capital efficiency is high.

**The headline recommendation:** lead Q1 with five "Now" initiatives that re-monetize and retain the existing base at low build cost, anchored by the **IMTU Data-Bundle Builder** as the keystone bet.

---

## 2. Strategic Context — What We Shipped, and Why It Matters Here

This year DCS built the foundations this roadmap stands on:

| Shipped capability | Why it matters for IMTU FY+1 |
|---|---|
| **DTC Universal API** (CSA IVR, Braze, WhatsApp) | The channel layer for conversational top-up, win-back, and gifting |
| **Subscription stack** (Subly, auto-toggle, Edit, Annual plans) | The rails for recurring/auto-recharge top-ups |
| **Validity-Based Reminder (BE + EMMS)** | The trigger engine for expiry-driven win-back |
| **Modular MTU component** | A reusable purchase engine for new payout types (data, bill pay) |
| **MTU — Request Top-Up** | The primitive for social/gifting acquisition loops |
| **Redesigned MTU Home (cross-sell)** + **Cross-Sell success page** | The surfaces for AI recommendations and attach |
| **BLS automatic promos** (1st-purchase, punch-card, World Cup) | The dominant acquisition lever, now needing reliability hardening |
| **New RAF platform** | The referral/acquisition-credit engine for viral loops |

The roadmap below turns these discrete primitives into a coherent IMTU growth system.

---

## 3. How We Prioritized

Each initiative was scored independently on four dimensions:

- **Revenue impact** (High / Medium / Low) — value *mechanism* and rough magnitude: volume × take-rate, attach, frequency, retention/LTV.
- **Complexity to build** (High / Medium / Low) — real engineering, integration, supply, and compliance effort.
- **Strategic fit** — alignment with the "IMTU as bridge into the fintech funnel" thesis and continuity with shipped work.
- **Connection to existing features** — how much it reuses what we already built (higher reuse = faster, cheaper, lower risk).

Initiatives were then assigned a **priority tier** (Now / Next / Later) and a **recommended quarter**, balancing impact against effort and dependencies. The logic: **favor high-strategic-fit, low-complexity, high-reuse moves first** to bank fast wins and fund the harder bets (bill pay, credit) later.

---

## 4. IMTU Initiative Summary

| # | Initiative | Priority | Quarter | Revenue Impact | Complexity | Time-to-Value |
|---|---|---|---|---|---|---|
| 1 | **IMTU Data-Bundle Builder** | 🟢 Now | Q1 | **High** | Medium | <1 qtr |
| 2 | **Auto-Recharge & Scheduled Recurring Top-Ups** | 🟢 Now | Q1 | Medium | **Low** | <1 qtr |
| 3 | **Request-Top-Up Social Loop + Referral Hook** | 🟢 Now | Q1 | Medium | **Low** | <1 qtr |
| 4 | **Validity-Based Save-Offer Reminders** | 🟢 Now | Q1 | Medium | **Low** | <1 qtr |
| 5 | **Promo Eligibility & Error-Sheet Resolution Service** | 🟢 Now | Q1 | Medium | Medium | 1–2 qtrs |
| 6 | **AI Next-Best-Bundle Recommendations** | 🟡 Next | Q2 | **High** | High | 1–2 qtrs |
| 7 | **Corridor Coverage Expansion (Carriers + Countries)** | 🟡 Next | Q2 | Medium | Medium | 1–2 qtrs |
| 8 | **Gift-a-Top-Up (Instant Claimable Code)** | 🟡 Next | Q2 | Medium | Medium | 1–2 qtrs |
| 9 | **Postpaid Bill Pay Abroad** | 🟡 Next | Q3 | Medium | High | 2–4 qtrs |
| 10 | **Airtime-on-Credit / Top-Up Now, Pay Later** | 🔵 Later | Q3 | Medium | High | 2–4 qtrs |

---

## 5. The Initiatives — Detail

### 🟢 NOW (Q1) — Fast, high-reuse wins on the existing base

#### 1. IMTU Data-Bundle Builder  ·  *Revenue: High · Complexity: Medium · TTV: <1 quarter*
**Reframe IMTU from flat $5 voice airtime into a per-recipient, data-first bundle builder that lifts ticket size and take-rate while defending against the prepaid-to-data shift.**

Restructures the purchase flow so the sender composes a per-recipient, per-corridor mix of data GBs, voice minutes, and social/streaming day-passes — with carrier-specific and non-expiring data packs (sourced via Zendit's direct carrier connections) surfaced as the default first screen, and plain airtime demoted to secondary. This moves IMTU *up the value curve* exactly as voice airtime is structurally replaced by data.

- **Revenue mechanism:** ARPT and take-rate uplift across the existing, growing transaction base. Data bundles carry a materially higher ticket than ~$5 voice top-ups (revenue/transaction fell 4% to $5.63 — this directly reverses that). Even a modest mix-shift compounds on a ~$104M/qtr line.
- **Builds on:** Modular MTU component (purchase engine), redesigned MTU home (surface), BLS promos (layer onto data packs), Zendit (carrier-direct data inventory).
- **Top KPIs:** ARPT & data-pack attach rate; data vs. voice GMV mix by corridor; repeat frequency / 90-day retention of data buyers.
- **Key risk:** Data-pack catalog fragmentation (inconsistent expiry/validity metadata) → ties into the promo error-sheet work (#5).

#### 2. Auto-Recharge & Scheduled Recurring Top-Ups  ·  *Revenue: Medium · Complexity: Low · TTV: <1 quarter*
**Turn one-off senders into recurring subscribers with low-balance-triggered and calendar-scheduled auto-recharge — assembled almost entirely from subscription primitives we already shipped.**

A sender can have airtime/data auto-sent when a recipient's balance runs low or on a fixed weekly/monthly/28-day cadence, with optional annual prepay. Converting a one-off sender into 12+ guaranteed annual cycles is the single highest-leverage retention move in the category — and **auto top-up adoption is documented as LOW industry-wide**, a clear white-space.

- **Revenue mechanism:** Frequency + retention/LTV. Recurring revenue is high-quality (predictable, raises switching costs) and feeds the growing Digital Payments line.
- **Builds on:** Subly, IMTU auto-toggle, Edit-subscription, Annual plans, Validity-Based Reminders (pre-cycle skip/edit), BLS punch-card stamp per run.
- **Top KPIs:** Auto-recharge attach rate; 3-/6-month plan retention; incremental frequency vs. one-off baseline.
- **Key risk:** Low-balance trigger needs near-real-time recipient balance data (uneven across carriers) → ship calendar-scheduled as the universal MVP, low-balance corridor-by-corridor.

#### 3. Request-Top-Up Social Loop with Referral Hook  ·  *Revenue: Medium · Complexity: Low · TTV: <1 quarter*
**Turn the existing Request Top-Up feature into a two-sided viral loop where inbound asks convert non-users via RAF-credited onboarding and WhatsApp reminders drive recurring fulfillment.**

Pure composition of four shipped primitives (Request Top-Up + RAF + DTC Universal API/WhatsApp + BLS). A recipient requests a top-up; a non-user payer is routed through RAF-credited onboarding so both sides earn a reward; "people who requested you" WhatsApp nudges drive repeat fulfillment.

- **Revenue mechanism:** Near-zero-CAC viral acquisition (inbound requests are warm intent) + frequency lift from WhatsApp re-engagement + funnel feeding into BOSS Money/eSIM.
- **Builds on:** Request Top-Up (currently under-leveraged), RAF, DTC Universal API (WhatsApp), BLS (funds/caps the reward).
- **Top KPIs:** Viral coefficient (K-factor); request→fulfillment & non-user→activation conversion; loop CAC vs. paid channels.
- **Key risk:** Two-sided reward abuse (self-referral/collusion) — needs velocity limits, identity de-dupe, payout caps before scale.

#### 4. Validity-Based Save-Offer Reminders (Expiry-Triggered Win-Back)  ·  *Revenue: Medium · Complexity: Low · TTV: <1 quarter*
**Upgrade the shipped expiry reminder from a passive nudge into an active churn-prevention engine that fires NBO-selected airtime save-offers via a WhatsApp-first multi-channel cascade.**

When a prior top-up/bundle or an expiring cross-sell deal nears expiry, the system fires a personalized save-offer (bonus airtime / discounted reorder) chosen by Engager/NBO and delivered on the user's best channel. Operationalizes the research's clearest retention levers: expiry triggers, AI-churn save offers, and airtime rewards that are **~3× more redeemed** than generic perks (WhatsApp delivers ~3× engagement vs. push).

- **Revenue mechanism:** Reorder-rate and retention uplift on the installed base; only marginal cost is the bonus/discount.
- **Builds on:** Validity-Based Reminder, Engager/NBO, Cross-Sell success page, DTC Universal API, BLS.
- **Top KPIs:** Reorder rate (reminded vs. holdout); save-offer redemption & net retained GP; 30/60/90-day churn vs. control.
- **Key risk:** Promo subsidy eroding recovered GP / cannibalizing users who'd repurchase anyway — govern with NBO targeting + holdout groups.

#### 5. Promo Eligibility & Error-Sheet Resolution Service  ·  *Revenue: Medium · Complexity: Medium · TTV: 1–2 quarters*
**A centralized promo-eligibility service that resolves country- vs. carrier-scoped BLS promos correctly *before* they're shown — protecting IMTU's single biggest acquisition lever across app, WhatsApp, and IVR.**

Bonus airtime is the dominant conversion lever, but BLS promos are fragile: country-scoped (resolved by dialing code) and carrier-scoped (resolved by unreliable carrier detection due to number portability) offers are easily mis-shown. This centralizes eligibility into one service, powers accurate error/eligibility bottom sheets, and exposes the same logic to WhatsApp/IVR. It productizes the country-vs-carrier error-sheet spec already delivered (2026-06-10).

- **Revenue mechanism:** Protective/enabling — recovers promo-driven sessions that abandon when a shown promo fails at checkout (a textbook broken-promise drop-off) and lifts promo-attach because offers become trustworthy.
- **Builds on:** BLS promos, DTC Universal API, the delivered IMTU promo error-sheet UX spec, redesigned MTU homepage.
- **Top KPIs:** Promo mis-show rate (→ near-zero); promo-attached conversion rate; cross-channel eligibility consistency (app/WhatsApp/IVR).
- **Key risk:** Number-portability ambiguity makes carrier scope probabilistic; must hedge to avoid suppressing valid promos.

---

### 🟡 NEXT (Q2–Q3) — Higher-leverage growth, more build

#### 6. AI Next-Best-Bundle Recommendations on MTU Home  ·  *Revenue: High · Complexity: High · TTV: 1–2 quarters*
**An AI layer that pre-fills the optimal recipient/corridor bundle for one-tap repeat sends and drives high-margin eSIM/eGift/remittance cross-sell from the redesigned MTU Home.**

ML predicts the optimal data/voice/social bundle and amount per recipient — learned from send history, recipient operator, and live promos — so a repeat send becomes one tap, churn signals trigger save offers, and the same surface attaches eSIM/eGift/BOSS Money. **Competitive whitespace:** no diaspora top-up rival has shipped AI bundle recommendations at scale.

- **Revenue mechanism:** Frequency lift (one-tap reorder) + cross-sell attach into higher-margin Fintech (NBO lifts cross-sell conversion 25–40% per McKinsey) + churn-save retention.
- **Builds on:** Engager/NBO (decisioning), redesigned MTU Home, BLS (offer inventory), Cross-Sell success page.
- **Top KPIs:** Repeat-send frequency / one-tap reorder rate; cross-sell attach & incremental GP/session; recommendation acceptance rate.
- **Key risk:** Genuine ML build (feature pipeline, ranking + churn models, real-time serving, A/B infra) — multi-quarter; cold-start & cross-app identity risk.

#### 7. Corridor Coverage Expansion (Carriers + Countries)  ·  *Revenue: Medium · Complexity: Medium · TTV: 1–2 quarters*
**Close the operator/country coverage gap toward Ding-level breadth via aggregator long-tail plus direct carrier deals, and add data top-up so IMTU stays the growing bridge into the fintech funnel.**

Expands IMTU from ~280 carriers / ~95–100 countries toward parity with Ding's 850+ operators / 150+ countries — DT One & Reloadly for the long tail, direct carrier deals in core corridors for better rates and exclusive promos — and adds instant data-bundle top-up for new operators.

- **Revenue mechanism:** Incremental GMV from newly addressable corridors + higher frequency from data bundles. (Share-defense/funnel-feeding; not a step-change — long tail is low-volume per corridor.)
- **Builds on:** Zendit/aggregator rails, Modular MTU component, BLS promos (extend bonus airtime to new corridors).
- **Top KPIs:** Operators/countries live (toward 850+/150+); incremental GMV from new corridors (net-new vs. cannibalized); delivery success rate per operator.
- **Key risk:** Aggregator supply is thinner-margin with less promo control; direct carrier deals are slow and relationship-dependent.

#### 8. Gift-a-Top-Up / Send as an Instant Claimable Code  ·  *Revenue: Medium · Complexity: Medium · TTV: 1–2 quarters*
**Turn IMTU into a gift: buy airtime/data as a branded, claimable code sent via WhatsApp/SMS/email that doubles as a low-CAC acquisition loop through RAF.**

Buy a top-up (or eGift) and deliver it as a redeemable code/link rather than charging a known number, with branded presentation for birthdays/holidays. A direct, on-brand answer to Ding's gifting top-up and Western Union's "gift value to family" — neither fused with WhatsApp delivery at scale.

- **Revenue mechanism:** New gifting occasions lift frequency/basket + each code exposes a non-user to the brand → near-zero-CAC acquisition via RAF.
- **Builds on:** DTC Universal API (delivery), RAF (referral credit), Request Top-Up (claim/fulfillment), BLS (gift-occasion offers).
- **Top KPIs:** Gifted top-ups/month (% of IMTU); claim/redemption rate; recipient→new-user conversion & CAC vs. paid.
- **Key risk:** Fraud/abuse on claimable codes (gift-card-draining/resale category) + escrow/refund accounting — needs light-KYC at claim and abuse controls.

#### 9. Postpaid Bill Pay Abroad  ·  *Revenue: Medium · Complexity: High · TTV: 2–4 quarters*
**Let diaspora senders pay a relative's postpaid mobile or utility bill abroad against the same saved recipient — turning IMTU from prepaid top-up into a multi-payout household-support engine.**

Adds a new payout type (postpaid mobile / utility / biller) entered against the existing saved-recipient profile, leaning on aggregator bill-pay coverage plus direct biller deals. Moves the relationship from "send airtime" to "keep their phone/lights on" — a proven diaspora wedge (Ding utility e-cards; Xoom bill pay; Remitly offers no top-up at all).

- **Revenue mechanism:** Higher tickets ($20–60 vs. $5–15) + recurring monthly bills → larger basket, higher frequency, stickier retention.
- **Builds on:** Request Top-Up (recipient capture), Modular MTU component, Zendit/aggregator rails, BLS.
- **Top KPIs:** Bill-pay attach rate among active senders; incremental GP per relationship; recurring bill-pay (household stickiness); on-time posting rate.
- **Key risk:** Materially harder than prepaid (biller validation, exact-amount entry, non-instant settlement/reconciliation, higher fraud/AML); biller coverage thin outside mobile → BD-heavy.

---

### 🔵 LATER (Q3+) — Strategic optionality, sequence behind platform bets

#### 10. Airtime-on-Credit / Top-Up Now, Pay Later  ·  *Revenue: Medium · Complexity: High · TTV: 2–4 quarters*
**Let cash-constrained senders advance an IMTU top-up (and eventually remittance) now and repay on their next funding cycle — opening a credit-based revenue line on the segment BR already serves.**

BR fronts the cost and collects on the next card/bank funding event, using operator-funded nano-credit where available. Targets the thin-file, payday-constrained base for whom liquidity is the >50% top deterrent — mirroring proven Remitly Flex and LemFi "Send Now, Pay Later" mechanics, and a credible first step toward the wallet/credit stack every diaspora super-app is building.

- **Revenue mechanism:** Conversion/frequency uplift on liquidity-deterred carts + a new credit fee/interest take. (Near-term prize is conversion/funnel-feeding into higher-margin BOSS Money, *not* standalone lending profit — per-loan economics on $5–25 tickets are thin.)
- **Builds on:** Subly (repayment scheduling), BLS, Request Top-Up, DTC Universal API — but underwriting, licensing and loss-capital are net-new.
- **Top KPIs:** SNPL attach rate; conversion uplift vs. control; net credit margin (fees minus default losses); downstream BOSS Money conversion.
- **Key risk:** Heavy US consumer-lending compliance (licensing, TILA/Reg Z, UDAAP, fair-lending); credit losses on thin-file base; float/capital requirement. **Sequence behind higher-leverage platform bets.**

---

## 6. Quarterly Roadmap

| Quarter | Initiatives | Theme |
|---|---|---|
| **Q1** | Data-Bundle Builder · Auto-Recharge · Request-Top-Up Loop · Save-Offer Reminders · Promo Eligibility Service | **Re-monetize & retain the base** with high-reuse, low-complexity wins |
| **Q2** | AI Next-Best-Bundle · Corridor Coverage Expansion · Gift-a-Top-Up | **Grow frequency, reach & acquisition** |
| **Q3** | Postpaid Bill Pay Abroad · Airtime-on-Credit (begin) | **Deepen the household relationship & test credit** |

---

## 7. Competitive Context for IMTU

The roadmap is built against a clear read of where rivals are heading:

- **Ding** (category leader, 850+ operators / 150+ countries) — the coverage and gifting benchmark. Drives initiatives #7 (coverage parity) and #8 (gifting).
- **Xoom (PayPal)** & **WorldRemit/Sendwave (Zepz, raised $165M led by HSBC, Apr 2025)** — use top-up as a remittance retention wedge and are pressing **fee/FX transparency** as a differentiator.
- **Remitly** (175+ countries) — notably offers **no airtime top-up**, leaving a gap; but is building **Remitly Flex** and a 2026 credit-builder → validates initiative #10.
- **LemFi** — "Send Now, Pay Later" + credit (Pillar) aimed at exactly BR's thin-file base → reinforces #10.
- **Recharge.com → acquired by Coda (Jul 2025)** — a well-capitalized digital-prepaid platform (16,000+ products, 180+ countries) that can underprice standalone players → raises the urgency of the data-bundle and coverage moves.
- **Meta/WhatsApp** launched prepaid recharge in India (Apr 2026, via PayU) — validates top-up as a habit-forming wedge *and* signals a platform-scale threat if extended cross-border. Our WhatsApp initiatives (#3, #4, #8) get ahead of this on our own terms.

**The structural opportunity:** the market is migrating from voice airtime to **data bundles** and from one-off sends to **recurring/subscription** mechanics. Initiatives #1, #2, and #7 put BR on the right side of both shifts, while #3, #4, #6, and #8 exploit our singular advantage — IMTU living in both apps with WhatsApp reach — that pure-play and remittance rivals lack.

---

## 8. Key Cross-Initiative Risks & Dependencies

- **BLS promo reliability is foundational.** Initiatives #1, #2, #4, #6, and #7 all assume promos resolve correctly. **#5 (Promo Eligibility Service) de-risks all of them** — which is why it is a Q1 "Now" item despite being infrastructure.
- **Recipient-side data quality** (carrier detection, balance, portability) gates the data-first defaults (#1), low-balance auto-recharge (#2), and AI recommendations (#6).
- **Cross-app identity** (IMTU in both Calling and Money apps) is the unlock for personalization (#6) and cross-sell measurement; without it, signal fragments.
- **Compliance escalates with ambition:** bill pay (#9) and credit (#10) add fraud/AML and US lending-regulatory surface — deliberately sequenced later.

---

## 9. Recommendation

**Commit Q1 to the five "Now" initiatives.** They are low-complexity, high-reuse, fast-payback moves that re-monetize and retain the existing base — anchored by the **Data-Bundle Builder** (the keystone revenue bet) and de-risked by the **Promo Eligibility Service**. Use the Q1 wins to fund the higher-build Q2–Q3 growth bets (AI recommendations, coverage, gifting, bill pay) and to validate the conditions for the Q3+ credit option.

---

*Sources: IDT Corporation FY2025 / Q2 FY2026 segment reporting; GSMA State of the Industry (Mobile Money) 2025; operator disclosures (MTN, Airtel); Ding, Xoom, WorldRemit/Zepz, Remitly, LemFi, Recharge.com/Coda, Reloadly, DT One public materials; Meta/WhatsApp–PayU announcement (Apr 2026). Full research dataset and per-initiative scoring available on request.*
