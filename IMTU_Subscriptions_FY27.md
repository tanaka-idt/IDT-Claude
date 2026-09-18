# BOSS Revolution — IMTU Subscriptions
### FY27 Initiative Suggestions + Market Investigation
**Product line:** International Mobile Top-Up (IMTU) — Subscriptions / Recurring
**Prepared for:** DCS stakeholders & leadership

---

## 1. Executive Summary

IMTU subscriptions are the highest-quality revenue in the product line — recurring, predictable, higher-retention, and harder to churn — and the market has moved decisively here. Competitors have standardized **pay-per-cycle recurring top-up** (Ding, Rebtel), wrapped the whole relationship in a **membership** (Remitly One, $9.99/mo), and built the **billing-health/dunning** machinery that recurring revenue depends on (Holafly, telco auto-renew).

BR has shipped the subscription *plumbing* (Subly, auto-toggle, Edit-subscription, BLS promos) and selected **Annual Plans (prepay)** for FY27 — but is missing four things the market treats as standard: the **pay-per-cycle recurring model**, a **membership wrapper**, a **dunning/retention layer**, and **data/family/gift subscription variants**.

This document captures the market investigation and **10 suggested FY27 subscription initiatives**, each scored on revenue, complexity, time-to-value, and connection to existing/selected work. **Top 3 to commit:** Flexible Recurring Top-Up, Smart Dunning & Churn Recovery, and Recurring Data-Plan Subscription.

---

## 2. What the IMTU Subscription Market Is Doing

- **Recurring top-up is a shipped competitor feature.** Ding launched **recurring top-ups (July 2025)** — no upfront payment, choose start date + cadence (every **7 / 14 / 28 / 30 days**). Rebtel **Plans auto-renew every 30 days at a fixed price.** This is pay-per-cycle, distinct from prepay.
- **The membership bundle is the defining monetization wrapper.** **Remitly One ($9.99/mo)** bundles send-now-pay-later (Flex), a 4%-yield Wallet, a debit Card, identity/credit monitoring, and a credit line (Spring 2026) — proof diaspora users will pay a recurring fee for a bundled relationship.
- **Telcos run auto-renew + auto-top-up as standard.** Lyca auto-tops-up every 30 days; 1-year plans auto-renew every 365 days; **bundle subscriptions** (connectivity + extras) and direct-carrier billing are expanding reach to the unbanked.
- **eSIM has a clean recurring model to copy.** **Holafly Plans auto-renew every 30 days**, month-to-month, cancel anytime, with an explicit **dunning ladder** (retry 3×, suspend after 5 days, cancel after 30).
- **Involuntary churn is the silent killer.** It is **20–50% of subscription losses**; well-run dunning recovers **70–80% of failed payments** via smart retries timed to payroll cycles, card-updater services, and pre-dunning nudges.
- **Recurring + membership + loyalty are converging** — recurring revenue depends on loyalty, sustained through membership value.

---

## 3. Where BR Stands Today

| | |
|---|---|
| **Shipped (FY26)** | Subly subscription integration · Auto-toggle for subscribing to IMTU · Edit-subscription feature · BLS promos for subscriptions · "Improve Experience & Penetration" · Annual plans (billing) |
| **Selected (FY27)** | **Subscription — Annual Plans** (prepay 12 months upfront for 12 monthly top-ups at a discount) |
| **The gaps** | Pay-per-cycle recurring · Membership wrapper · Dunning / churn recovery · Data / family / gift subscription variants |

---

## 4. Suggested FY27 Subscription Initiatives

### Theme 1 — Core recurring mechanics (catch up to Ding/Rebtel)

#### 1. Flexible Recurring Top-Up (pay-per-cycle)  ·  *Revenue: Med · Complexity: Low · TTV: <1 qtr · Priority: Now/Q1*
Schedule a recurring top-up to a recipient with **no upfront payment**, choosing start date and cadence (weekly / 14-day / 28-day / monthly), charged each cycle with skip/edit before each run.
- **Market signal:** the exact Ding (Jul 2025) feature; Rebtel Plans auto-renew at 30 days.
- **Connects to:** complements your prepay **Annual Plans** — together they cover "prepay a year" and "pay-as-you-go monthly." Builds on Subly + auto-toggle + Validity-Based Reminders.
- **Key risk:** recurring-payment retries/dunning (addressed by #6).

#### 2. Low-Balance-Triggered Auto-Recharge  ·  *Revenue: Med · Complexity: Low–Med · TTV: <1–2 qtrs · Priority: Now/Q1*
Auto-send airtime/data when the **recipient's balance runs low**, rather than on a fixed calendar.
- **Market signal:** telco "auto top-up" standard (Lyca); auto-top-up adoption is an industry white-space.
- **Connects to:** the "triggered" complement to Annual Plans / Recurring Top-Up; reuses Subly rails.
- **Key risk:** needs near-real-time recipient balance data (uneven by carrier) → ship balance-trigger corridor-by-corridor, calendar cadence as the universal base.

#### 3. Recurring Data-Plan Subscription  ·  *Revenue: High · Complexity: Med · TTV: 1–2 qtrs · Priority: Next/Q2*
Subscribe a recipient to a **monthly data allowance** (not just voice airtime).
- **Market signal:** Holafly Plans + telco data subscriptions + Rebtel Plans; the prepaid→data shift is the #1 trend.
- **Connects to:** depends on / pairs with the **Data-Bundle Builder**; higher ticket than voice subscriptions.
- **Key risk:** data-pack catalog fragmentation (expiry/validity metadata).

### Theme 2 — The membership wrapper (Remitly One analog)

#### 4. BOSS Diaspora Membership  ·  *Revenue: High · Complexity: High · TTV: 2–4 qtrs · Priority: Next/Q3*
A flat monthly fee bundling discounted/bonus recurring top-ups + a data allowance + fee/FX discounts + exclusive promos, with **auto-enrollment of high-frequency senders** to beat the ~50% enrollment gap.
- **Market signal:** Remitly One proves willingness to pay; the clearest recurring-revenue, high-LTV wrapper in the category.
- **Connects to:** Subly, Annual plans, BLS; stronger once a wallet exists.
- **Key risk:** bundle economics must clear the per-benefit COGS.

#### 5. Subscriber-Only Pricing & Perks Tier  ·  *Revenue: Med · Complexity: Med · TTV: 1–2 qtrs · Priority: Next/Q2*
Subscribers get better fees/FX/bonus airtime than one-off senders — the loyalty/membership convergence.
- **Market signal:** recurring + loyalty + membership converging.
- **Connects to:** BLS promos, Variable Fees (dynamic pricing), Gamification.
- **Key risk:** margin discipline; avoid training one-off users to wait for subscriber pricing.

### Theme 3 — Billing health & retention (the critical, unglamorous layer)

#### 6. Smart Dunning & Involuntary-Churn Recovery  ·  *Revenue: Med (protective) · Complexity: Med · TTV: 1–2 qtrs · Priority: Now/Q1*
Retry logic timed to payroll cycles, card-updater integration, pre-expiry reminders, pre-dunning nudges, and helpful-tone failed-payment messaging.
- **Market signal:** involuntary churn is 20–50% of losses; good dunning recovers 70–80% of failed payments.
- **Connects to:** essential for **Annual Plans** and every recurring product; delivered via Subly + DTC Universal API (WhatsApp/Braze).
- **Key risk:** none material — this is pure retention protection; sequence early.

#### 7. Subscription Lifecycle: Pause / Skip / Cancel-Flow + Win-Back  ·  *Revenue: Med · Complexity: Low · TTV: <1 qtr · Priority: Now/Q1*
Let subscribers **pause or skip a cycle** instead of cancelling, add a save-offer cancel-flow, and run reactivation campaigns.
- **Market signal:** cancel-flows + dunning form a holistic retention system; Holafly cancel-anytime norm.
- **Connects to:** Edit-subscription feature + Validity-Based Reminders + NBO.
- **Key risk:** low; mostly flow/UX + offer governance.

### Theme 4 — Family, gifting & intelligence

#### 8. Multi-Recipient / Family Subscription  ·  *Revenue: Med · Complexity: Med · TTV: 1–2 qtrs · Priority: Next/Q2*
One subscription funding recurring top-ups to **several recipients** (parents + siblings) on a single bill.
- **Market signal:** family-plan / data-sharing analog (EE data gifting, family accounts).
- **Connects to:** the recipient model behind Request Top-Up; raises switching costs.
- **Key risk:** billing/allocation logic across multiple recipients.

#### 9. Gift a Subscription  ·  *Revenue: Med · Complexity: Med · TTV: 1–2 qtrs · Priority: Next/Q2*
Buy someone a recurring top-up/data subscription as a gift (gift an Annual Plan or monthly plan).
- **Market signal:** gifting + recurring convergence; gift occasions drive enrollment.
- **Connects to:** ties **Gifting Top-Up** to recurring revenue; uses claimable-value rails.
- **Key risk:** escrow/redemption + recurring-consent handling.

#### 10. AI-Recommended Subscription  ·  *Revenue: Med · Complexity: High · TTV: 2–4 qtrs · Priority: Later/Q3*
Suggest the optimal cadence/amount/bundle per recipient from past-send behavior, and surface "turn this into a subscription" after a few manual sends.
- **Market signal:** personalization lifts conversion; AI-led upsell.
- **Connects to:** shares the engine with Variable Fees + AI Next-Best-Bundle/NBO.
- **Key risk:** ML build + data readiness.

---

## 5. Prioritized View & Sequencing

| Priority | Initiatives |
|---|---|
| **Now / Q1** | 1 Flexible Recurring Top-Up · 2 Low-Balance Auto-Recharge · 6 Smart Dunning · 7 Lifecycle Pause/Skip/Win-Back |
| **Next / Q2** | 3 Recurring Data-Plan Subscription · 5 Subscriber-Only Pricing · 8 Family Subscription · 9 Gift a Subscription |
| **Next–Later / Q3** | 4 BOSS Diaspora Membership · 10 AI-Recommended Subscription |

### Top 3 to commit
1. **Flexible Recurring Top-Up (#1)** — table-stakes; Ding already ships it; low build on existing rails.
2. **Smart Dunning & Churn Recovery (#6)** — protects the revenue of Annual Plans *and* every recurring product; without it, subscriptions leak 20–50%.
3. **Recurring Data-Plan Subscription (#3)** — puts subscriptions on the right side of the prepaid→data shift.

**Sequencing logic:** ship the recurring mechanic + the dunning/retention layer **first** (they are the foundation that protects all recurring revenue, including the already-selected Annual Plans), then layer the membership, data, family, and gift variants on top.

---

## 6. Sources

- [Ding — recurring top-ups](https://www.ding.com/topup) · [Ding (company)](https://en.wikipedia.org/wiki/Ding_(company))
- [Remitly One announcement](https://ir.remitly.com/news-releases/news-release-details/remitly-announces-remitly-one-new-all-one-financial-membership) · [Payments Dive — Remitly One](https://www.paymentsdive.com/news/remitly-one-launch-subscription-tier-flex-wallet-debit-card-currency-passbook/760499/)
- [Holafly Plans — international data subscriptions (auto-renew + dunning)](https://esim.holafly.com/faq/holafly-plans/international-data-subscriptions/) · [Holafly — manage subscriptions](https://esim.holafly.com/plans/manage-subscriptions/)
- [1Global — the rise of bundle subscriptions](https://www.1global.com/blog/mobile-operators/rise-of-bundle-subscriptions) · [Lyca Mobile prepaid plans 2026](https://www.lycamobile.us/blog/en/usa-best-prepaid-phone-plans-a-2026-guide/)
- [Churn Buster — reduce customer churn 2026](https://churnbuster.io/articles/how-to-reduce-customer-churn) · [Failed-payment recovery: 2026 dunning playbook](https://www.digitalapplied.com/blog/failed-payment-recovery-dunning-playbook-2026)
- [SubscriptionX 2026 — recurring/membership/loyalty convergence](https://internetretailing.net/subscriptionx-2026-why-recurring-revenue-membership-and-loyalty-are-converging/)

---

*Compiled from live web research (June 2026) plus the Boss Revolution FY-roadmap research base. Revenue/complexity reflect the FY-roadmap scoring framework. Excludes Annual Plans (already selected for FY27) and shipped subscription plumbing.*
