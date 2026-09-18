# BOSS Revolution — IMTU FY27 Plan
### Selected Initiatives + Candidate Additions
**Product line:** International Mobile Top-Up (IMTU)
**Prepared for:** DCS stakeholders & leadership
**Purpose:** Capture the FY27 IMTU initiatives selected so far, plus recommended additions and enhancements, with revenue / complexity / dependency context for prioritization.

---

## 1. Executive Summary

Seven IMTU initiatives have been selected for FY27. They are strong on **monetization mechanics** (Annual Plans, Variable Fees, Gamification) and **acquisition loops** (Request Top-Up, Gifting, Recipient App). Reviewing them against the market and competitor landscape surfaces three gaps worth closing:

1. **No data product.** All seven are voice-airtime-centric, yet the defining category trend is prepaid → data, and every competitor has moved (Ding sells data plans across 850+ operators; Rebtel "Bundles"; Reloadly's Data Bundle API; DT One). **A Data-Bundle Builder is the single most important addition.**
2. **No intelligence / reliability layer.** Variable Fees, Gamification, and Gifting all quietly depend on accurate promo eligibility and personalization that don't exist yet.
3. **No channel play.** WhatsApp is where the diaspora transacts, and Meta launched in-app recharge in India (Apr 2026) — a latent cross-border threat.

This plan keeps the 7 selected initiatives, adds **9 candidate initiatives** (grouped into four themes), and lists **enhancements** that strengthen the selected set. **Top 3 to add:** Data-Bundle Builder, AI Next-Best-Bundle/Reorder, and the Promo Eligibility & Error-Sheet Service.

---

## 2. Selected FY27 Initiatives (the 7)

| # | Initiative | Revenue | Complexity | Builds on / connects to |
|---|---|---|---|---|
| S1 | **Subscription — Annual Plans** | High | Med | Subly subscription rails, annual billing, Validity-Based Reminders |
| S2 | **MTU — Request Top-Up** | Med | Low–Med | Shipped Request Top-Up, new RAF platform, DTC Universal API (WhatsApp) |
| S3 | **Gamification** | Med | High | BLS promos, RAF, Engager/NBO + Lifecycle Workflow |
| S4 | **MTU Open Ranges** | Med | Med | Modular MTU component, carrier open-range support |
| S5 | **Variable Fees (dynamic pricing)** | High | High | Transaction-history data, BLS, pricing guardrails |
| S6 | **Gifting Top-Up** | Med | Med | DTC Universal API, RAF, Request Top-Up, BLS |
| S7 | **Recipient App (request + history)** | Med | High | BR7 app, DTC Universal API, Request Top-Up |

**Notes on the selected set:**
- **S1 Annual Plans** is calendar-based prepay (12 months upfront). It pairs naturally with the *low-balance* auto-recharge variant (A2 below) to cover both "scheduled" and "triggered" recurring sends.
- **S3 Gamification** and **S5 Variable Fees** both need a personalization/decisioning engine — see A3 (AI Next-Best-Bundle), which shares that engine.
- **S5 Variable Fees** and **S6 Gifting** both rely on promos resolving correctly — see A4 (Promo Eligibility Service).
- **S6 Gifting** and **S2 Request Top-Up** both want WhatsApp as a delivery channel — see A8 (WhatsApp Commerce).

---

## 3. Candidate Additions (9)

### Theme 1 — Go data-first (the biggest gap)

#### A1. IMTU Data-Bundle Builder  ·  *Revenue: High · Complexity: Med · TTV: <1 qtr*
Let the sender compose a per-recipient, per-corridor mix of **data GBs, voice, and social/streaming packs**, with data-first defaults and non-expiring packs where available (sourced via Zendit's carrier-direct supply). Demote flat airtime to secondary.
- **Why / signal:** Prepaid→data is the #1 trend; Ding (850+ operators' data plans), Rebtel Bundles, Reloadly Data Bundle API are all there. Data carries a higher ticket and take-rate than $5 voice top-ups.
- **Connects to your 7:** powers **Open Ranges** (data amounts), **Variable Fees** (price data packs dynamically), **Annual Plans** (a "data annual plan"), and **Gifting** (gift a data bundle).
- **Key risk:** data-pack catalog fragmentation (expiry/validity metadata) → ties to the Promo Eligibility Service (A4).

### Theme 2 — Smarter automation & retention

#### A2. Low-Balance Auto-Recharge  ·  *Revenue: Med · Complexity: Low · TTV: <1 qtr*
Auto-send airtime/data when the **recipient's balance runs low** (vs. your calendar-based Annual Plans). Set-and-forget recharge with skip/edit before each run.
- **Why / signal:** Auto top-up adoption is documented as LOW industry-wide — a clear white-space. Converts one-off senders into recurring.
- **Connects to your 7:** the "triggered" complement to **Annual Plans (S1)**; reuses the same Subly rails.
- **Key risk:** needs near-real-time recipient balance data (uneven by carrier) → ship balance-trigger corridor-by-corridor, calendar cadence as the universal base.

#### A5. Validity-Based Expiry Win-Back  ·  *Revenue: Med · Complexity: Low · TTV: <1 qtr*
When a prior top-up/bundle or an expiring offer nears expiry, fire a personalized **save-offer** (bonus airtime/discount) via WhatsApp-first cascade.
- **Why / signal:** airtime/bill-credit rewards are ~3× more redeemed than generic perks; coordinated multi-channel lifecycle lifts retention up to ~24%.
- **Connects to your 7:** feeds **Gamification (S3)** missions; uses the same NBO brain as A3.
- **Key risk:** promo-subsidy discipline + holdout measurement to prove incrementality.

### Theme 3 — Intelligence & reliability layer (powers several of your picks)

#### A3. AI Next-Best-Bundle & 1-Tap Reorder  ·  *Revenue: High · Complexity: High · TTV: 1–2 qtrs*
ML pre-fills the optimal bundle/amount per recipient for **one-tap reorder**, and surfaces the best cross-sell at the moment of intent; churn signals trigger save offers.
- **Why / signal:** NBO lifts cross-sell conversion 25–40% (McKinsey); no diaspora top-up rival has shipped AI bundle recommendations at scale (whitespace).
- **Connects to your 7:** **shares the data/feature store with Variable Fees (S5)** and **personalizes Gamification (S3)** missions; makes Gifting/Request smarter.
- **Key risk:** genuine ML build (feature pipeline, ranking + churn models, A/B infra); cross-app identity.

#### A4. Promo Eligibility & Error-Sheet Resolution Service  ·  *Revenue: Med · Complexity: Med · TTV: 1–2 qtrs*
A central service that resolves **country- vs carrier-scoped promos correctly before they're shown**, powers accurate eligibility/error sheets, and exposes the same logic to WhatsApp/IVR.
- **Why / signal:** bonus airtime is the category's dominant acquisition lever, but mis-shown promos cause broken-promise abandonment at checkout.
- **Connects to your 7:** **foundational for Gamification (S3), Variable Fees (S5), and Gifting (S6)** — they all assume promos fire correctly.
- **Key risk:** number-portability makes carrier scope probabilistic; must hedge to avoid suppressing valid promos.

### Theme 4 — Expand the product & win the channel

#### A6. Postpaid Bill Pay Abroad  ·  *Revenue: Med · Complexity: High · TTV: 2–4 qtrs*
Add a new payout type: pay a relative's **postpaid mobile / utility bill** against the same saved recipient — "send help, not just airtime."
- **Why / signal:** Taptap Send already lets senders pay utility/water/gas/school-fee bills directly; higher tickets, recurring, stickier.
- **Connects to your 7:** extends **Open Ranges (S4)** (exact-amount entry) and the recipient model behind **Request Top-Up (S2)**.
- **Key risk:** biller validation, non-instant settlement/reconciliation, higher fraud/AML; biller coverage is BD-heavy.

#### A7. Corridor & Carrier Coverage Expansion (+ data)  ·  *Revenue: Med · Complexity: Med · TTV: 1–2 qtrs*
Close the breadth gap toward Ding (850+ operators) / DT One (600+) via aggregator long-tail + direct carrier deals, and add **data SKUs** to newly onboarded operators.
- **Why / signal:** coverage + instant delivery are table stakes; BR trails the category leaders on the headline metrics.
- **Connects to your 7:** every new corridor inherits **Variable Fees (S5)**, **Gifting (S6)**, and the Data-Bundle Builder (A1).
- **Key risk:** thin-margin aggregator supply; slow direct-carrier negotiations.

#### A8. WhatsApp Conversational Commerce  ·  *Revenue: Med · Complexity: Med · TTV: 1–2 qtrs*
Make WhatsApp a transaction surface: in-thread recharge, **one-tap reorder**, data bundles, and gift send/redeem, with verified-business branding.
- **Why / signal:** WhatsApp ~95% engagement; Meta launched in-app recharge in India (Apr 2026). Pre-empt the threat on rails BR already built (DTC Universal API).
- **Connects to your 7:** becomes the **delivery channel for Gifting (S6)** and the nudge channel for **Request Top-Up (S2)**.
- **Key risk:** Meta platform/pricing dependence; in-thread payment compliance.

#### A9. Fee/FX Transparency at Confirmation  ·  *Revenue: Med · Complexity: Low · TTV: <1 qtr*
Show the **exact fee and exact amount delivered** before the sender confirms, and make displayed bonus-airtime match what's actually delivered.
- **Why / signal:** Xoom's "exact amount before you send" is becoming the category trust differentiator; reduces refunds/support.
- **Connects to your 7:** **pairs directly with Variable Fees (S5)** so dynamic pricing stays trusted and transparent.
- **Key risk:** low — primarily display + accuracy logic.

---

## 4. Enhancements to the Selected 7

These upgrade what you've already chosen rather than adding standalone scope:

- **Request Top-Up (S2) → add a RAF referral hook + WhatsApp nudges.** Route non-user payers through RAF-credited onboarding (both sides rewarded) and send "who requested you" reminders — turning a convenience feature into a **two-sided acquisition loop**.
- **Gifting Top-Up (S6) → add scheduled/recurring gifting + a redemption-driven RAF loop.** Birthday/holiday auto-gifts and "monthly data gift," and convert each redeemed gift into a new-user signup.
- **Annual Plans (S1) → add "data annual plan" + "gift an annual plan" variants** (once the Data-Bundle Builder exists).
- **Recipient App (S7) → make it the redemption surface for Gifting + the anchor for a future recipient-side wallet/loyalty.**

---

## 5. Combined Prioritized View

| Priority | Initiatives |
|---|---|
| **Now / Q1** | A1 Data-Bundle Builder · A2 Low-Balance Auto-Recharge · A4 Promo Eligibility Service · A5 Expiry Win-Back · A9 Fee/FX Transparency · (selected: S2 Request Top-Up, S4 Open Ranges) |
| **Next / Q2–Q3** | A3 AI Next-Best-Bundle · A7 Corridor Coverage · A8 WhatsApp Commerce · A6 Postpaid Bill Pay · (selected: S1 Annual Plans, S5 Variable Fees, S6 Gifting, S3 Gamification) |
| **Later** | (selected: S7 Recipient App — high build; sequence after the loops it amplifies are live) |

### Top 3 additions to make the FY27 cut
1. **A1 — Data-Bundle Builder.** Without it, the other six selected items optimize a shrinking voice-airtime base.
2. **A3 — AI Next-Best-Bundle / Reorder.** It's the shared brain behind your **Variable Fees** and **Gamification**, so it compounds.
3. **A4 — Promo Eligibility & Error-Sheet Service.** The reliability layer your **Gamification, Variable Fees, and Gifting** silently depend on.

**Sequencing logic:** lead with the data product + the reliability/intelligence layer (A1, A4, A3) because the selected monetization and engagement bets (S3, S5, S6) deliver more on top of them. Bank the low-complexity wins (A2, A5, A9, S4) in parallel.

---

*Competitive signals referenced: Ding (data plans 850+ operators, recurring top-ups, gifting), Rebtel (Bundles/Plans), Reloadly (Data Bundle API), DT One/Tunz (eSIM/data), Taptap Send (direct bill pay), Xoom (fee/FX transparency), Meta/WhatsApp (in-app recharge, India Apr 2026). Revenue/complexity reflect the FY-roadmap scoring framework. Full per-initiative detail available in the IMTU FY Roadmap.*
