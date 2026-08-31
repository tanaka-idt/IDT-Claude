#!/usr/bin/env python3
"""Build the v2 IMTU report HTML from the canonical metric registry."""
import base64, pathlib, sys, html as H

sys.path.insert(0, "/Users/joaotanaka/IDT Claude")
from imtu_metrics import (DASHBOARD, CHART, ALL_GROUPS, GAPS, all_metrics,
                          EXPOSURE, CHECKOUT, BRACKETS, CANCEL_FLOW,
                          COUNTRY, TENURE, PLATFORM, VERSION, RENEWALS)

S = pathlib.Path("/private/tmp/claude-501/-Users-joaotanaka-IDT-Claude/3daff475-c0ac-441c-8376-9b831c0e9f16/scratchpad")
WEB = S / "web"
OUT = S / "imtu_subscription_report.html"
CSS = (S / "_css.txt").read_text()

def img(name):
    return "data:image/jpeg;base64," + base64.b64encode((WEB / name).read_bytes()).decode()

D1, D2, D3, D4, D5 = (img(f"imtu_journey_{i}_{s}.jpg") for i, s in
                      [(1, "current"), (2, "variants"), (3, "immediate"), (4, "delayed"), (5, "future")])

BY = {m["key"]: m for m in all_metrics()}
def e(s): return H.escape(str(s))
def clink(cid, label=None):
    return f'<a class="mono ck" href="{CHART}{cid}" target="_blank" rel="noopener">{e(label or cid)}</a>'

PILL = {"confirmed": "p-ev", "superseded": "p-crit", "new": "p-no", "gap": "p-na"}

def mtable(metrics, cols=("Finding", "Value", "Denominator", "Window", "Configuration", "Chart")):
    rows = []
    for m in metrics:
        rows.append(
            "<tr>"
            f'<td><strong>{e(m["label"])}</strong>'
            f'<div class="fs2">{e(m["note"])}</div>' if m["note"] else
            f'<tr><td><strong>{e(m["label"])}</strong>')
    out = ['<div class="tw"><table><thead><tr>']
    out.append("".join(f"<th>{e(c)}</th>" for c in cols))
    out.append('<th>Status</th></tr></thead><tbody>')
    for m in metrics:
        note = f'<div class="note2">{e(m["note"])}</div>' if m["note"] else ""
        out.append(
            "<tr>"
            f'<td><strong>{e(m["label"])}</strong>{note}</td>'
            f'<td class="num">{e(m["value"])}</td>'
            f'<td class="num">{e(m["denom"])}</td>'
            f'<td class="num">{e(m["window"])}</td>'
            f'<td class="cfg">{e(m["cfg"])}</td>'
            f'<td>{clink(m["chart"])}</td>'
            f'<td><span class="pill {PILL[m["status"]]}">{e(m["status"])}</span></td>'
            "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)

def trace_table():
    out = ['<div class="tw"><table><thead><tr><th>Group</th><th>Finding</th><th>Value</th>'
           '<th>Denominator</th><th>Window</th><th>Chart</th><th>Status</th></tr></thead><tbody>']
    for gname, group in ALL_GROUPS:
        for m in group:
            out.append(
                f'<tr><td class="fs">{e(gname)}</td><td>{e(m["label"])}</td>'
                f'<td class="num">{e(m["value"])}</td><td class="num">{e(m["denom"])}</td>'
                f'<td class="num">{e(m["window"])}</td><td>{clink(m["chart"])}</td>'
                f'<td><span class="pill {PILL[m["status"]]}">{e(m["status"])}</span></td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)

def gaps_table():
    out = ['<div class="tw"><table><thead><tr><th>Missing</th><th>What is absent</th>'
           '<th>Question it blocks</th><th>Status</th></tr></thead><tbody>']
    for a, b, c, d in GAPS:
        out.append(f'<tr><td><strong>{e(a)}</strong></td><td class="cfg">{e(b)}</td>'
                   f'<td>{e(c)}</td><td><span class="pill p-no">{e(d)}</span></td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)

DRIVERS = [
    ("Renewal cadence", "SUPPORTS — strongest", "Weekly 49.36% (34,975/70,861) vs monthly 23.96% (48,161/201,009) at 30 days. Cadence is auto-derived from offer validity, not chosen.", "a75n2jgf"),
    ("Customer tenure", "SUPPORTS — confounded", "vip 43.08% down to one_trx 23.29%. Two readings fit equally; nothing separates them.", "6haohove"),
    ("Recipient country", "SUPPORTS", "El Salvador 39.57% down to Nigeria 17.88% across the top 8 corridors.", "2j37y76s"),
    ("Platform", "SUPPORTS — small", "Android 33.61% vs iOS 29.11%. The only dimension that cleanly partitions the base.", "9ibdyo1j"),
    ("App version", "ASSOCIATION ONLY", "23.03% to 37.20% — a 14.2pp spread, confounded with adopter mix and rollout timing.", "iw7zip5m"),
    ("Toggle default state", "ASSOCIATION ONLY", "Not causal — the default-OFF arm is defined by prior subscription ownership.", "qf6uouru"),
    ("Renewal reminders", "TIMING, NOT RATE", "Reminder receipt is unobservable — no first-party event exists.", ""),
    ("Failed payments", "CANNOT ANSWER", "100.0% of MTU payment failures carry no subscription flag; and by design a failed renewal cannot cause cancellation.", "owzed305"),
    ("Promotions", "CANNOT ANSWER", "Whether a subscription was promo-created is not persisted (DCS-5293).", ""),
    ("Payment method", "CANNOT ANSWER", "No payment property exists on any MTU order or cancel event.", ""),
    ("Recipient new vs repeat", "CANNOT ANSWER", "Phone number is on both events but cannot be joined in Amplitude. Warehouse only.", ""),
]
VP = {"SUPPORTS — strongest": "p-crit", "SUPPORTS — confounded": "p-hy", "SUPPORTS": "p-ev",
      "SUPPORTS — small": "p-ev", "ASSOCIATION ONLY": "p-hy", "TIMING, NOT RATE": "p-hy",
      "CANNOT ANSWER": "p-na"}

def drivers_table():
    out = ['<div class="tw"><table><thead><tr><th>Driver</th><th>Verdict</th>'
           '<th>Evidence</th><th>Chart</th></tr></thead><tbody>']
    for d, v, ev, c in DRIVERS:
        out.append(f'<tr><td><strong>{e(d)}</strong></td>'
                   f'<td><span class="pill {VP[v]}">{e(v)}</span></td>'
                   f'<td class="num">{e(ev)}</td><td>{clink(c) if c else "—"}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)

RECS = [
    ("P0", "R1", "Size and remediate the consent population, and re-open QA",
     "DCS-5277 100% reproducible; fix on a feature branch; QA task DCS-5310 closed “Won't fix” in 33 seconds",
     "Bounds a live regulatory exposure. Risk: remediation contact may surface subscriptions customers had not noticed — sequence with Legal",
     "S for QA; M for the cohort query", "A dated count of affected subscriptions and a QA pass on a production build",
     "None — verification, not experimentation", ""),
    ("P0", "R2", "Test whether the consent failure mode recurs on the smart-hide path",
     "DCS-5277's mechanism is toggle ON in state, toggle not rendered, subscription created. DCS-4854 hides the toggle by design and was never tested for this",
     "Potentially a second, much larger consent population — smart-hide is live to everyone", "S",
     "Completed orders with a subscription and no preceding toggle tap in session", "Not applicable — a test case", ""),
    ("P0", "R3", "Instrument the subscription flag on MarketingTxnFailed",
     "100.0% unset across 381,167 MTU failure events. The pipeline already sets it on successes",
     "Makes involuntary churn measurable for the first time. One property", "S",
     "Failed renewals attributable, and a dunning baseline that can be trended", "None — instrumentation", "owzed305"),
    ("P0", "R4", "Run the May–June randomised readout before DCS-5289 ships",
     "A_B_subscription_toggle_test_id balanced and populated, ~35k / ~58k events per arm",
     "Converts the central claim from observational to causal. Risk: two concurrent tests may overlap",
     "S — queries only", "Arm-level attach AND 30-day cancellation on unique users",
     "Ship DCS-5289 randomised, not globally", ""),
    ("P1", "R5", "Stop defaulting weekly cadence from 7-day offer validity",
     "Weekly 49.36% vs monthly 23.96% at 30 days; explicit choosers prefer 90-day",
     "The largest available reduction in early cancellation. Risk: fewer charges per subscription — do not assume the churn saving nets positive",
     "M — backend lever exists as DCS-5290", "Fee revenue per purchaser per 90 days, not attach rate",
     "Three arms on 7-day-validity offers: default weekly, default monthly, no default", "a75n2jgf"),
    ("P1", "R6", "Add cancellation-reason capture with an explicit “I didn't mean to subscribe”",
     "No cancel_reason property exists on any cancel event; 99.14% of Cancel-tappers complete",
     "The only way to split the pool into unintended versus considered — which every retention decision depends on",
     "S–M", "Reason distribution with skip rate reported alongside",
     "None — instrumentation, but gate the retention A/B on it", "0k93sx6m"),
    ("P1", "R7", "Build a skip or defer path instead of only cancel",
     "Only active/cancelled states exist; the dialog deflects 2.63% of taps; 63.87% substitute back to one-time top-ups",
     "Converts timing-driven cancellations into deferrals. Risk: deflecting unintended subscriptions re-banks unauthorised revenue",
     "M — a launch_at bump on the existing timer row", "90-day revenue per cancel-flow entrant, not deflection alone",
     "Ship as a fifth variant inside the DCS-5257/5258 retention A/B", "fndtbvdu"),
    ("P2", "R8", "Ship the unblocked half of payment-method change",
     "DCS-4461 marks Scenario 1 feasible; both stories High and unassigned under a Low-priority epic",
     "Removes an involuntary-churn path — an expiring card currently forces cancellation", "M",
     "In-app payment-method changes completed; reduction in cancel-and-recreate", "None — instrument before and after", ""),
    ("P2", "R9", "Fix the two taxonomy defects and the diagnostic gap",
     "gp:imtu_cls_label carries both 'none' and '(none)' 7.8pp apart; the broken A/B property is still writing; 37.27% of failures carry the bare value 'failed'",
     "Prevents the next analyst reaching a confident wrong conclusion", "S",
     "Single-valued buckets; failure reasons diagnostic", "None", "5d718501"),
    ("P2", "R10", "Scope the stacking guardrail per recipient, not per account",
     "A sender supporting three recipients has three legitimate subscriptions; a ≥1-per-account rule defaults the second and third OFF",
     "Raise on DCS-5289 before it leaves QA", "S — a spec change",
     "Attach retained on distinct-recipient purchases", "Fold into the DCS-5289 randomisation", ""),
]

def recs_html():
    out = []
    for pri, rid, title, ev, imp, eff, met, exp, chart in RECS:
        cls = {"P0": "p0", "P1": "p1", "P2": "p2"}[pri]
        pill = {"P0": "p-crit", "P1": "p-hy", "P2": "p-ev"}[pri]
        link = f' {clink(chart)}' if chart else ""
        out.append(f"""<div class="rec {cls}">
<div class="rec-h"><span class="id">{rid}</span><span class="pill {pill}">{pri}</span><h3>{e(title)}</h3></div>
<dl><dt>Evidence</dt><dd>{e(ev)}{link}</dd>
<dt>Impact / risk</dt><dd>{e(imp)}</dd>
<dt>Effort</dt><dd>{e(eff)}</dd>
<dt>Success metric</dt><dd>{e(met)}</dd>
<dt>Experiment</dt><dd>{e(exp)}</dd></dl></div>""")
    return "".join(out)

EXTRA_CSS = """
<style>
.ck{font-size:.78em;padding:1px 5px;border-radius:3px;background:var(--accent-soft);
  color:var(--accent);text-decoration:none;white-space:nowrap}
.ck:hover{text-decoration:underline}
.note2{font-family:var(--sans);font-size:.72rem;color:var(--muted);margin-top:4px;line-height:1.45}
.cfg{font-family:var(--mono);font-size:.68rem;color:var(--muted);line-height:1.5}
.fs{font-family:var(--sans);font-size:.72rem;color:var(--muted)}
td.num{font-size:.78rem}
.dashbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;background:var(--surface);
  border:1px solid var(--rule);border-left:3px solid var(--accent);border-radius:8px;
  padding:16px 20px;margin:26px 0}
.dashbar a{font-family:var(--sans);font-weight:600;font-size:.9rem}
</style>"""

HTML = f"""<title>IMTU Subscription Journey</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=JetBrains+Mono:wght@400;500;700&display=swap">
{CSS}{EXTRA_CSS}
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">BOSS Revolution · IMTU · Investigation v2</p>
  <h1>The subscription nobody chose</h1>
  <p class="sub">Every figure rebuilt as a saved Amplitude chart with a stated denominator.
  48 metrics, 46 charts, one dashboard — and 15 figures that did not survive the rebuild.</p>
  <div class="meta"><span>31 August 2026</span><span>Amplitude project 650506</span>
  <span>Jira DCS / DTCBE / CRMC</span><span>v2 — supersedes the first version</span></div>
</header>

<nav class="toc" aria-label="Sections"><ol>
  <li><a href="#summary">Summary</a></li><li><a href="#method">Method</a></li>
  <li><a href="#timeline">Timeline</a></li><li><a href="#behaviour">Behaviour</a></li>
  <li><a href="#variants">Variants</a></li><li><a href="#cancel">Cancellation</a></li>
  <li><a href="#segments">Segments</a></li><li><a href="#renewals">Renewals</a></li>
  <li><a href="#gaps">Gaps</a></li><li><a href="#future">Future flow</a></li>
  <li><a href="#next">Next steps</a></li><li><a href="#trace">Traceability</a></li>
</ol></nav>

<section id="summary"><div class="col">
  <p class="eyebrow">01 — Executive summary</p>
  <h2>The default is doing the work, not customer intent</h2>
  <p class="lede">Defaulting the subscription toggle to ON attaches 11.4× better than defaulting it
  OFF. It also produces a base that cancels at roughly a third within thirty days, concentrated on
  the days customers are charged.</p>
</div>

<div class="dashbar"><span class="eyebrow">All 46 charts</span>
<a href="{DASHBOARD}" target="_blank" rel="noopener">IMTU Subscription Journey — Full Evidence Pack →</a></div>

<div class="readout">
  <div class="ro crit"><span class="n">30.57%</span><span class="k">Cancel within 30 days</span>
    <span class="d">83,148 / 272,026 · Mar–Jul</span></div>
  <div class="ro crit"><span class="n">7.91%</span><span class="k">Cancel within 24 hours</span>
    <span class="d">median 178 seconds</span></div>
  <div class="ro warn"><span class="n">49.23%</span><span class="k">Opt out when defaulted ON</span>
    <span class="d">259,895 / 527,930 · Aug</span></div>
  <div class="ro acc"><span class="n">25.96%</span><span class="k">Attach, week of 24 Aug</span>
    <span class="d">down from 45.49% peak</span></div>
  <div class="ro good"><span class="n">44.80%</span><span class="k">Resubscribe within 60 days</span>
    <span class="d">60,891 / 135,903 cancellers</span></div>
</div>

<div class="col">
  <h3>Corrections this version makes</h3>
  <p>Fifteen of 48 figures did not survive rebuilding. The direction of the analysis is unchanged;
  several magnitudes are not.</p>
  <ul class="clean">
    <li><strong>30-day cancellation is 30.57%, not 29.10%.</strong> The earlier denominator of
    342,130 was close to the <em>sum</em> of monthly unique purchasers rather than distinct users
    over the window. The correct base is 272,026. {clink("7200e6l9")}</li>
    <li><strong>Checkout converts at 87.82%, not ~76%.</strong> The earlier figure was
    arithmetically impossible against its own platform split. {clink("movsvyvz")}</li>
    <li><strong>Android converts better than iOS, not worse</strong> — 88.34% against 87.52%.
    The direction was reversed. {clink("vqml240x")}</li>
    <li><strong>Post-cancellation substitution is 63.87%, not 45.3%</strong>, and a further 44.80%
    resubscribe. Cancelling is mostly not rejection of the product.
    {clink("fndtbvdu")} {clink("i7673xwm")}</li>
    <li><strong>The 57.20% non-interaction figure is not reproducible</strong> — it was screen-level
    and no single chart can produce it. The user-level equivalent is 51.29%. {clink("fqiwoqr8")}</li>
    <li><strong>Two property names do not exist.</strong> The toggle event carries
    <span class="mono">default_state</span> / <span class="mono">new_state</span>, not
    <span class="mono">default_subscription_toggle</span>; and app version is
    <span class="mono">version</span>, not <span class="mono">version_name</span>.</li>
  </ul>

  <div class="callout crit">
    <h4>The judgement this asks for</h4>
    <p>Roughly half the subscription base behaves like people undoing something they did not choose:
    51.29% never touch the toggle, 49.23% of those exposed to an ON default turn it off, and the
    median 24-hour canceller acts in 178 seconds. Before adding retention, establish how much attach
    is consented — a save flow applied to unintended subscriptions converts a consent problem into a
    revenue problem. The 44.80% who resubscribe voluntarily suggest the product is wanted; the
    mechanic is what is being rejected.</p>
  </div>
</div></section>

<section id="method"><div class="col">
  <p class="eyebrow">02 — Methodology and traceability standard</p>
  <h2>Every figure carries four things</h2>
  <p>Value, denominator, date range, and a link to the saved chart that reproduces it. Both this
  report and the Google Doc are generated from one canonical registry, so they cannot drift apart.
  Each chart's own description repeats its configuration, so a reviewer opening a chart cold can see
  what it measures.</p>
  <h3>Two standard windows</h3>
  <ul class="clean">
    <li><strong>Cancellation cohort — 1 March to 1 August 2026.</strong> Unique users, shared step-1
    denominator of 272,026 distinct subscription purchasers. Every cancellation and segment chart
    uses this identical shape so rates are directly comparable.</li>
    <li><strong>Exposure and checkout — 1 to 29 August 2026.</strong> 29 days, not a calendar month.
    Figures described as “August” elsewhere may differ by 2–3% for that reason alone.</li>
  </ul>
  <h3>Four traps this report avoids</h3>
  <ul class="clean">
    <li><strong>Events are not customers.</strong> Order-success events fire ~2.21× per converting
    user, and 39,628 toggle taps end where they began.</li>
    <li><strong>Grouped funnels return unlabelled series</strong>, so every segment figure is backed
    by an explicitly filtered chart. Rank-order inference was tested and found invalid.</li>
    <li><strong>Some segments do not partition the base.</strong> Tenure cohorts sum to 114% and
    version cohorts to 119%. Do not sum their denominators. Platform is the only clean partition.</li>
    <li><strong>Right-censoring.</strong> Bracket and 60-day rates are floors. Right-censoring is what
    produced the 12.7% figure that circulated before this work.</li>
  </ul>
</div></section>

<section id="behaviour"><div class="col">
  <p class="eyebrow">03 — Behavioural analysis</p>
  <h2>Exposure and the toggle</h2>
  <p>Nearly one order screen in five records no toggle state at all, and that untagged arm converts
  at 7.01% — between the ON and OFF arms, so it cannot be assumed to be either.</p>
</div>
{mtable(EXPOSURE)}
<div class="col">
  <div class="callout"><h4>Association, not causation <span class="pill p-hy">Hypothesis</span></h4>
  <p>The 11.4× attach gap is observational. The default-OFF population is defined by already owning
  subscriptions, so it is selected on the outcome. The randomised A/B property is unusable post-GA —
  arm B carries 143 users.</p></div>
  <h2>Checkout and confirmation</h2>
  <p>Checkout is healthy and the subscription mechanic does not measurably harm it — platforms sit
  within 0.82 points and subscription versus one-time within 0.89 at the payment step.</p>
</div>
{mtable(CHECKOUT)}
<figure class="fig"><img src="{D1}" alt="Diagram 1: the current IMTU subscription journey as measured.">
<figcaption>Diagram 1 — The current journey as measured. Dashed steps exist but emit no event.</figcaption></figure>
</section>

<section id="timeline"><div class="col">
  <p class="eyebrow">04 — Release timeline</p>
  <h2>One completed targeting change, two reversals, no rollout record</h2>
  <p>Neither variant the brief assumes is limiting exposure has shipped. <span class="mono">DCS-5289</span>
  is QA Available; the entire V2 epic <span class="mono">DCS-5297</span> is To Do, including its
  Amplitude events and its A/B harness. The only completed post-launch targeting change is smart-hide
  (<span class="mono">DCS-4854</span>).</p>
  <p>Two standing caveats: every <span class="mono">fixVersion</span> carries
  <span class="mono">released=false</span>, so all dates are Jira resolution or build dates; and
  READY-IN-FEAT means merged to a feature branch, not shipped, even though Jira files it under Done.</p>
  <div class="callout crit"><h4>Intended versus implemented</h4>
  <p>The V1 targeting predicate has two incompatible readings. The internal core-logic reference
  describes two independent gates — duplicate, then a 3-or-more cap. <span class="mono">DCS-5289</span>
  describes the outgoing rule as a single conjunction: OFF <em>only if</em> 3+ active subscriptions
  <em>and</em> the same offer to the same recipient. Either V1 shipped differently from its spec, or
  DCS-5289 is scoped against a false premise. Resolve before it leaves QA.</p></div>
</div>
<figure class="fig"><img src="{D2}" alt="Diagram 2: variants and targeting changes by shipping status.">
<figcaption>Diagram 2 — Every variant and targeting change, by actual shipping status.</figcaption></figure>
</section>

<section id="variants"><div class="col">
  <p class="eyebrow">05 — Variant comparison</p>
  <h2>Why the comparison cannot be made today</h2>
  <div class="tw"><table><thead><tr><th>Comparison</th><th>Status</th><th>Why</th></tr></thead><tbody>
  <tr><td><strong>DCS-5289 vs control</strong></td><td><span class="pill p-na">Impossible</span></td>
  <td>The variant is not in production. There is nothing to measure.</td></tr>
  <tr><td><strong>Randomised arms, post-GA</strong></td><td><span class="pill p-na">Impossible</span></td>
  <td>Tagging effectively stopped in July. Arm B carries 143 users — no power.</td></tr>
  <tr><td><strong>Randomised arms, May–Jun</strong></td><td><span class="pill p-no">Available, not run</span></td>
  <td>Balanced at ~35k and ~58k events per arm. The only causal readout the programme has.</td></tr>
  <tr><td><strong>Default ON vs OFF</strong></td><td><span class="pill p-hy">Confounded</span></td>
  <td>62.90% vs 5.53% attach, but selected on the outcome. {clink("qf6uouru")}</td></tr>
  <tr><td><strong>Platform / version / country / cadence / tenure</strong></td>
  <td><span class="pill p-ev">Available</span></td>
  <td>All segmentable, each with its own saved chart.</td></tr>
  </tbody></table></div>
  <div class="col"><div class="callout warn"><h4>A taxonomy defect that will mislead the next analyst</h4>
  <p>Two A/B properties coexist undeleted, and <strong>the broken one is still being written</strong> —
  it recorded feature-flag state rather than arm assignment (<span class="mono">DCS-4369</span>) and is
  now the only populated one. Anyone segmenting by it gets a confident, wrong answer.</p></div></div>
</div></section>

<section id="cancel"><div class="col">
  <p class="eyebrow">06 — Cancellation findings</p>
  <h2>Two cancellations with two different causes</h2>
  <p>Time-to-cancel is bimodal: an immediate-regret spike inside the first hour, a quiet trough across
  days one to four, then a larger mass locked to the renewal charge.</p>
</div>
{mtable(BRACKETS)}
<div class="col">
  <p>The immediate cluster is undo, not churn. A 178-second median is not deliberation — it is someone
  discovering a subscription on the confirmation screen or receipt and reversing it. No reason is
  captured, so nothing is learned.</p>
  <div class="callout"><h4>Regret or promo capture? <span class="pill p-hy">Hypothesis</span></h4>
  <p>Not currently distinguishable. <span class="mono">DCS-5293</span> raises exactly this and asks
  whether a promo-created subscription can even be identified — so today it cannot.</p></div>
  <h3>The flow itself, and what follows it</h3>
</div>
{mtable(CANCEL_FLOW)}
<div class="col"><p>The two post-cancellation figures overlap and must not be summed — a customer who
both buys a one-time top-up and resubscribes appears in both. Both are right-censored floors.</p>
<h3>Ranked drivers</h3></div>
{drivers_table()}
<figure class="fig"><img src="{D3}" alt="Diagram 3: immediate cancellation path.">
<figcaption>Diagram 3 — Immediate cancellation, within 24 hours.</figcaption></figure>
<figure class="fig"><img src="{D4}" alt="Diagram 4: delayed cancellation by cadence.">
<figcaption>Diagram 4 — Delayed cancellation, by cadence.</figcaption></figure>
</section>

<section id="segments"><div class="col">
  <p class="eyebrow">07 — Segment analysis</p>
  <h2>Where cancellation concentrates</h2>
  <p>Nicaragua and Ethiopia, both quoted in the earlier version, are not among the top 8 corridors by
  volume on this window. El Salvador and Honduras are tied at 0.09 points apart; neither should be
  called the worst market.</p>
</div>
{mtable(COUNTRY)}
<div class="col"><div class="callout"><h4>The tenure gradient has two readings <span class="pill p-hy">Hypothesis</span></h4>
<p>Either VIPs accumulate redundant default-ON subscriptions and cancel them, or VIPs are simply more
able to find the cancel control — in which case low-tenure customers' lower rate reflects
non-detection rather than satisfaction. Nothing in current tracking separates them.</p></div></div>
{mtable(TENURE)}
{mtable(PLATFORM)}
<div class="col"><p>The version spread is 14.2 points — wider than the entire Android/iOS gap. That is
why no single-version comparison should be used to claim a build regression.</p></div>
{mtable(VERSION)}
</section>

<section id="renewals"><div class="col">
  <p class="eyebrow">08 — Renewals and payments</p>
  <h2>The largest blind spot in the product</h2>
  <p>A taxonomy search across six renewal, billing, retry and dunning concepts returns no renewal
  event of any kind. A partial view opened on 10 August 2026, and it is both recent and impure.</p>
</div>
{mtable(RENEWALS)}
<div class="col">
  <div class="callout crit"><h4>Involuntary churn cannot be measured at all</h4>
  <p>100.0% of MTU payment failures carry no subscription flag, so a failed renewal is
  indistinguishable from a failed one-off top-up. Voluntary churn is measurable; involuntary churn is
  not. And a failed renewal cannot itself produce a cancellation — DTCBE-623 removed auto-cancellation
  in May 2024 after DTCBE-444 lost roughly 30,000 subscriptions. Failing subscriptions simply persist,
  and the customer is told nothing on any channel (<span class="mono">CRMC-3299</span>, backlog since
  2024). {clink("owzed305")}</p></div>
</div></section>

<section id="gaps"><div class="col">
  <p class="eyebrow">09 — Tracking gaps</p>
  <h2>What the instrumentation cannot answer</h2>
</div>
{gaps_table()}
</section>

<section id="future"><div class="col">
  <p class="eyebrow">10 — Recommended flow</p>
  <h2>Consent first, cadence chosen, one real alternative</h2>
  <p>Three changes: refuse to create a subscription without a rendered toggle; stop deriving weekly
  cadence from short offer validity; and offer one genuine alternative at cancellation without
  obstructing the cancel path.</p>
</div>
<figure class="fig"><img src="{D5}" alt="Diagram 5: recommended future-state journey.">
<figcaption>Diagram 5 — Recommended future state.</figcaption></figure>
<div class="col"><div class="callout crit"><h4>The sharpest risk</h4>
<p>A large share of the cancellation pool is people undoing a subscription they never chose.
Deflecting them into a skip or a discount re-banks revenue they never authorised. Any retention
readout must be split by whether the subscription was toggle-created — which needs the
cancellation-reason property that does not yet exist.</p></div></div>
</section>

<section id="next"><div class="col">
  <p class="eyebrow">11 — Prioritised next steps</p>
  <h2>Ten recommendations</h2>
</div>
{recs_html()}
<div class="col"><div class="callout"><h4>Explicitly not recommended</h4>
<p>Opening a regression ticket on any single app version — the spread is 14.2 points and a comparator
can be chosen to prove almost anything. And attributing the Stripe request-rate spikes to the
default-ON toggle: eleven same-second timers cannot mechanically produce the observed rate.</p></div></div>
</section>

<section id="trace"><div class="col">
  <p class="eyebrow">12 — Full traceability index</p>
  <h2>Every figure in this report</h2>
  <p>48 metrics, 46 saved charts, one dashboard. Each row links to the chart that reproduces it.</p>
</div>
<div class="dashbar"><span class="eyebrow">Dashboard</span>
<a href="{DASHBOARD}" target="_blank" rel="noopener">IMTU Subscription Journey — Full Evidence Pack →</a></div>
{trace_table()}
<div class="col">
  <h3>Limitations</h3>
  <ul class="clean">
    <li><strong>No confidence intervals.</strong> The 0.82-point platform gap and the 19.8-point
    tenure gap are reported at equal weight; the second is clearly meaningful and the first probably
    is not, but nothing here distinguishes them formally.</li>
    <li><strong>Two figures are derived across charts</strong> — the opt-out and opt-in rates take
    numerators from the toggle-tap chart and denominators from the exposure chart.</li>
    <li><strong>Funnel group labels are inferred, not read</strong>, for the attach-by-default-state
    chart. Every other segment figure avoids this using explicitly filtered charts.</li>
    <li><strong>The 28.4% failing-subscription pool is not observable in Amplitude</strong> — it came
    from an April 2026 database analysis and cannot be refreshed without warehouse access.</li>
    <li><strong>Still required:</strong> Subly or IDTPay billing records to link failed renewals to
    cancellation; warehouse access for repeat-versus-new recipient; and a written decision record for
    the V1 experiment, which exists nowhere in Jira.</li>
  </ul>
</div></section>

<footer>
  <p>Sources — Amplitude org BOSS (127967), project 650506 “BR app Prod”, queried 30–31 August 2026.
  All 46 charts saved and collected on one dashboard. Jira DCS, DTCBE, CRMC at idtjira.atlassian.net.</p>
  <p>Method — figures rebuilt as saved charts from a canonical registry shared with the companion
  Google Doc. 15 of 48 figures superseded the previous version; each is marked in the index above.</p>
</footer>
</div>
"""

OUT.write_text(HTML, encoding="utf-8")
print("wrote", OUT, OUT.stat().st_size // 1024, "KB")
