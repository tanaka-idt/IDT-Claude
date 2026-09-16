#!/usr/bin/env python3
"""
Renders the FY27 plan as a single HTML page (DCS_FY27_Plan.html): summary,
sequence table, weekly Gantt, one section per initiative with description and
implementation strategy, assumptions and sources. Every reference is a link.

Usage:
    python build_fy27_html.py [--sheet-url URL] [--doc-url URL]
"""

import argparse
import html
from datetime import timedelta
from pathlib import Path

from fy27_plan_data import (INITIATIVES, CARRY_OVERS, TEAM, PHASES, PHASE_LONG, QUARTERS,
                            QUARTER_LABELS, WEEKS, SPRINT_WEEKS, TECH_RESERVE, ASANA_PROJECT,
                            ASANA_FY26, FY26_SHEET, CONFLUENCE_MODULAR, asana_url, be_fte,
                            app_fte, phase_weeks, week_start, fmt, sprint_of_week)
from fy27_schedule import schedule, summary_rows

OUT = Path(__file__).parent / "DCS_FY27_Plan.html"

# Validated for colour-vision separation with the dataviz palette checker;
# every bar also carries its phase label, so identity never rests on colour.
HTML_PHASE = {"PM": "#3F8F5A", "Design": "#6F45A0", "TPM": "#A88A00",
              "BE": "#2F6FBF", "App": "#C9463F", "QA": "#0E8FA3"}
SHORT = {"PM": "PM", "Design": "Design", "TPM": "TPM", "BE": "BE", "App": "App", "QA": "QA"}


def esc(s):
    return html.escape(str(s), quote=True)


def a(url, text):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'


def date_of(w):
    return fmt(week_start(w))


def end_date_of(w):
    return fmt(week_start(w) - timedelta(days=1))


def build(sheet_url, doc_url):
    sched = schedule()
    rows = summary_rows(sched)
    n_weeks = max(WEEKS, max(r["end"] for r in rows))
    board = [r for r in rows if r["i"]["goal"] == "Board Goal"]
    biz = [r for r in rows if r["i"]["goal"] == "Business Goal"]
    spill = [r for r in rows if r["spill"]]
    sprints = WEEKS // SPRINT_WEEKS
    be_demand = sum(be_fte(i) for i in INITIATIVES)
    app_demand = sum(app_fte(i) for i in INITIATIVES)
    cap = round(3 * sprints * (1 - TECH_RESERVE))
    fy_end = end_date_of(WEEKS)

    css = f"""
<title>DCS FY27 Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --ground:#F5F6F3; --surface:#FFFFFF; --surface-2:#EDF0EA; --line:#D5DAD1;
  --ink:#1B2430; --ink-2:#3C4858; --muted:#6B7686; --accent:#1F5F8B; --accent-ink:#FFFFFF;
  --risk-bg:#FBE9E7; --risk-ink:#8C2F24; --carry-bg:#E4E7E1; --carry-ink:#4B5563;
  --pm:{HTML_PHASE['PM']}; --design:{HTML_PHASE['Design']}; --tpm:{HTML_PHASE['TPM']};
  --be:{HTML_PHASE['BE']}; --app:{HTML_PHASE['App']}; --qa:{HTML_PHASE['QA']};
  --display:"Archivo",system-ui,sans-serif; --body:"Source Sans 3",system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{
  --ground:#171B21; --surface:#1F242C; --surface-2:#262C35; --line:#343B46;
  --ink:#E8ECF1; --ink-2:#C4CCD6; --muted:#8B96A5; --accent:#7FB3DA; --accent-ink:#0F1A24;
  --risk-bg:#3A2320; --risk-ink:#F2B8B0; --carry-bg:#2C323B; --carry-ink:#B8C0CC;
  --pm:#5FAE7A; --design:#A07FD0; --tpm:#D4B32C; --be:#6C9BE0; --app:#E07670; --qa:#3FB2C6;
}} }}
:root[data-theme="dark"]{{
  --ground:#171B21; --surface:#1F242C; --surface-2:#262C35; --line:#343B46;
  --ink:#E8ECF1; --ink-2:#C4CCD6; --muted:#8B96A5; --accent:#7FB3DA; --accent-ink:#0F1A24;
  --risk-bg:#3A2320; --risk-ink:#F2B8B0; --carry-bg:#2C323B; --carry-ink:#B8C0CC;
  --pm:#5FAE7A; --design:#A07FD0; --tpm:#D4B32C; --be:#6C9BE0; --app:#E07670; --qa:#3FB2C6;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font:16px/1.5 var(--body);}}
.wrap{{max-width:1180px;margin:0 auto;padding-block:32px 64px;padding-inline:20px;}}
h1,h2,h3{{font-family:var(--display);text-wrap:balance;margin:0;color:var(--ink)}}
h1{{font-size:clamp(28px,4vw,40px);font-weight:700;letter-spacing:-0.01em}}
h2{{font-size:24px;font-weight:600;margin-top:56px;padding-top:16px;border-top:2px solid var(--ink)}}
h3{{font-size:19px;font-weight:600}}
p{{max-width:72ch;margin:10px 0}}
a{{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:2px}}
a:focus-visible,button:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.byline{{color:var(--muted);margin-top:8px;font-size:15px}}
.eyebrow{{font-family:var(--mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:24px}}
.stat{{background:var(--surface);border:1px solid var(--line);padding:14px 16px}}
.stat b{{display:block;font-family:var(--display);font-size:28px;font-weight:600;font-variant-numeric:tabular-nums}}
.stat span{{color:var(--muted);font-size:14px}}
nav.toc{{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:20px;font-size:15px}}
table{{border-collapse:collapse;width:100%;font-size:14.5px;background:var(--surface)}}
th,td{{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line)}}
th{{font-family:var(--mono);font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:500;background:var(--surface-2)}}
td.num,th.num{{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--mono);font-size:13px}}
.scroll{{overflow-x:auto;border:1px solid var(--line);background:var(--surface)}}
.pill{{display:inline-block;font-family:var(--mono);font-size:11.5px;padding:2px 8px;border-radius:999px;border:1px solid var(--line);color:var(--ink-2);white-space:nowrap}}
.pill.risk{{background:var(--risk-bg);color:var(--risk-ink);border-color:transparent}}
.pill.carry{{background:var(--carry-bg);color:var(--carry-ink);border-color:transparent}}
.pill.high{{border-color:var(--ink-2)}}
.legend{{display:flex;flex-wrap:wrap;gap:10px 18px;margin:14px 0;font-size:14px}}
.legend i{{display:inline-block;width:14px;height:14px;vertical-align:-2px;margin-right:6px;border-radius:2px}}
/* gantt */
.gantt{{font-size:12px;min-width:{260 + n_weeks * 14}px}}
.grow{{display:grid;grid-template-columns:260px repeat({n_weeks},14px);align-items:center;min-height:26px;
  background-image:repeating-linear-gradient(to right,var(--line) 0 1px,transparent 1px {SPRINT_WEEKS * 14}px);
  background-position:260px 0;background-size:calc(100% - 260px) 100%;background-repeat:no-repeat}}
.grow.head{{background:none;min-height:22px;color:var(--muted);font-family:var(--mono);font-size:11px}}
.glabel{{position:sticky;left:0;background:var(--surface);padding:3px 10px 3px 8px;z-index:2;border-right:1px solid var(--line);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px}}
.glabel small{{color:var(--muted);font-family:var(--mono);font-size:11px;margin-right:6px}}
.bar{{grid-row:1;height:18px;line-height:18px;color:#fff;padding:0 4px;font-family:var(--mono);font-size:10.5px;
  overflow:hidden;white-space:nowrap;border-right:2px solid var(--surface);border-radius:2px}}
.bar.PM{{background:var(--pm)}} .bar.Design{{background:var(--design)}} .bar.TPM{{background:var(--tpm)}}
.bar.BE{{background:var(--be)}} .bar.App{{background:var(--app)}} .bar.QA{{background:var(--qa)}}
.q{{grid-row:1;padding:2px 6px;border-left:2px solid var(--ink-2);font-weight:500;color:var(--ink)}}
.q.fy28{{background:var(--risk-bg);color:var(--risk-ink)}}
.m{{grid-row:1;padding:0 4px;border-left:1px solid var(--line)}}
.grow.carry .glabel{{color:var(--carry-ink);font-style:italic}}
.grow.sep{{border-top:2px solid var(--ink-2)}}
/* initiative cards */
.init{{background:var(--surface);border:1px solid var(--line);padding:22px 24px;margin-top:20px}}
.init header{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:6px}}
.init h3{{margin-top:4px}}
.init .lead{{font-size:17px;color:var(--ink-2);font-style:italic}}
.init h4{{font-family:var(--display);font-size:14px;letter-spacing:.02em;text-transform:uppercase;color:var(--muted);margin:22px 0 6px;font-weight:600}}
.init ol,.init ul{{max-width:76ch;padding-left:22px;margin:6px 0}}
.init li{{margin:6px 0}}
.phases{{max-width:720px;font-size:14px}}
.phases td:first-child{{font-weight:600}}
.two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}}
.note{{background:var(--surface-2);border-left:3px solid var(--accent);padding:12px 16px;max-width:76ch}}
@media (max-width:640px){{ .init{{padding:16px}} h2{{font-size:21px}} .glabel{{font-size:12px}} .grow{{grid-template-columns:200px repeat({n_weeks},14px)}} .gantt{{min-width:{200 + n_weeks * 14}px}} .grow{{background-position:200px 0;background-size:calc(100% - 200px) 100%}} }}
@media (prefers-reduced-motion: reduce){{ *{{scroll-behavior:auto}} }}
</style>
"""

    parts = [css, '<div class="wrap">']
    parts.append(f"""
<div class="eyebrow">DCS product management · fiscal year 2027 · {fmt(week_start(0))} to {fy_end}</div>
<h1>DCS FY27 Initiative Plan</h1>
<p class="byline">Description, implementation strategy and phased schedule for the {len(rows)} Board and Business goals on the
{a(ASANA_PROJECT, "DCS FY27 Asana board")}. Prepared by João Tanaka, 16 September 2026. Companion spreadsheet:
{a(sheet_url, "DCS FY27 Initiatives") if sheet_url else "DCS FY27 Initiatives (Google Sheet)"}{(" · Google Doc version: " + a(doc_url, "DCS FY27 Initiative Plan")) if doc_url else ""}.</p>
<div class="stats">
  <div class="stat"><b>{len(rows)}</b><span>initiatives scheduled ({len(board)} Board, {len(biz)} Business)</span></div>
  <div class="stat"><b>{be_demand} / {cap}</b><span>backend FTE sprints demanded vs available at a 35% tech reserve</span></div>
  <div class="stat"><b>{app_demand} / {cap}</b><span>app FTE sprints demanded vs available</span></div>
  <div class="stat"><b>{len(rows) - len(spill)}</b><span>initiatives that finish inside FY27; {len(spill)} land in FY28</span></div>
</div>
<nav class="toc"><a href="#summary">Summary</a><a href="#method">How the plan was built</a><a href="#sequence">Sequence</a>
<a href="#timeline">Timeline</a><a href="#initiatives">Initiatives</a><a href="#carry">Carry-over work</a><a href="#fy28">What lands in FY28</a><a href="#sources">Sources</a></nav>
""")

    # ---------------------------------------------------------- summary ---
    parts.append(f"""
<h2 id="summary">Summary</h2>
<p>The FY27 board lists {len(rows)} goals once duplicates are merged: {len(board)} Board goals and {len(biz)} Business goals. Backend is the constraint. The goals ask for about {be_demand} backend FTE sprints while three developers minus the 35% tech reserve provide {cap} across {sprints} sprints, so roughly {be_demand - cap} sprints of backend work do not fit inside the year. App demand ({app_demand} FTE sprints) fits with a little slack, which is why backend-light initiatives run in parallel with the heavy ones.</p>
<p>The order follows three rules. First, finish what is in flight (Terminus, the WhatsApp chatbot) and build the pieces other goals reuse (the IMTU module, Engager cards). Second, put the High-priority revenue and payments work in Q2 so it lands before the second half. Third, give the two largest builds (Bundling, ROW expansion) a full quarter of backend in Q3 with their discovery done in Q2. The Q4 slate (Engager personalisation, Wallet promo balances, IVA migration, Gamification, Crypto) is where the capacity gap shows: at the 35% reserve those initiatives start their build in the last sprints and finish in FY28.</p>
<div class="note">Every estimate here is a PM first pass on the FY26 scale (S 1, M 2, L 4, XL 9 FTE sprints). Engineering should validate them in the Comments column of the spreadsheet before the plan is committed, as Marc and Ilya did for FY26.</div>
""")

    # ----------------------------------------------------------- method ---
    team_rows = "".join(
        f"<tr><td>{esc(role)}</td><td>{esc(TEAM[role]['label'])}</td><td class='num'>{TEAM[role]['lanes']}</td><td>{esc(TEAM[role]['note'] or PHASE_LONG[role])}</td></tr>"
        for role in PHASES)
    parts.append(f"""
<h2 id="method">How the plan was built</h2>
<div class="two">
<div>
<p>Every initiative goes through the same six phases in strict order: the PM defines requirements and strategy, Design produces the screens, the TPM runs the spike and breaks the work into tickets, Backend builds the services, App builds the UI, QA tests and releases. A role that finishes one initiative starts the next the following week, so the roles form a pipeline and several initiatives are in flight at once.</p>
<p>Capacity is modelled as parallel lanes per role. Backend and App have three people each, but 35% of their time is reserved for tech debt and company tech goals, as in FY26, which leaves two lanes for initiatives. Large backend builds take both lanes; the rest take one. The PM may start discovery up to eight weeks before the target quarter so specifications do not go stale.</p>
</div>
<div class="scroll"><table><thead><tr><th>Role</th><th>People</th><th class="num">Lanes</th><th>Note</th></tr></thead><tbody>{team_rows}</tbody></table></div>
</div>
""")

    # --------------------------------------------------------- sequence ---
    seq = []
    for r in rows:
        i = r["i"]
        status = ('<span class="pill risk">lands in FY28</span>' if r["spill"] else
                  ('<span class="pill carry">carry over</span>' if i["fy27"] == "Carry Over" else '<span class="pill">fits FY27</span>'))
        seq.append(
            f"<tr><td class='num'>{i['order']}</td><td><a href='#{i['id']}'>{esc(i['name'])}</a></td>"
            f"<td>{esc(i['goal'])}</td><td>{esc(i['product'])}</td><td>{esc(i['priority'])}</td><td>{i['quarter']}</td>"
            f"<td class='num'>{esc(i['be'])} · {be_fte(i)}</td><td class='num'>{esc(i['app'])} · {app_fte(i)}</td>"
            f"<td>{esc(date_of(r['start']))}</td><td>{esc(r['end_date'])}</td><td>{status}</td></tr>")
    parts.append(f"""
<h2 id="sequence">Sequence</h2>
<p>The proposed execution order. Start is the first PM week, End is the last QA week. BE and App show size and FTE sprints.</p>
<div class="scroll"><table><thead><tr><th class="num">#</th><th>Initiative</th><th>Goal</th><th>Product</th><th>Priority</th><th>Quarter</th><th class="num">BE</th><th class="num">App</th><th>Start</th><th>End</th><th>Status</th></tr></thead>
<tbody>{''.join(seq)}</tbody></table></div>
""")

    # --------------------------------------------------------- timeline ---
    legend = "".join(f'<span><i style="background:var(--{k.lower()})"></i>{esc(PHASE_LONG[k])}</span>' for k in PHASES)
    qhead = ['<div class="grow head"><div class="glabel">Quarter</div>']
    qs = list(QUARTERS.items()) + [("FY28", WEEKS)]
    for (q, s), (_, e) in zip(qs, qs[1:] + [(None, n_weeks)]):
        if s >= n_weeks:
            continue
        label = QUARTER_LABELS.get(q, "FY28 (unfunded at 35% reserve)")
        qhead.append(f'<div class="q{" fy28" if q == "FY28" else ""}" style="grid-column:{2 + s}/{2 + min(e, n_weeks)}">{esc(label)}</div>')
    qhead.append("</div>")
    mhead = ['<div class="grow head"><div class="glabel">Month · sprint</div>']
    w = 0
    mid = lambda k: week_start(k) + timedelta(days=3)      # mid-week date names the month
    while w < n_weeks:
        d = mid(w)
        nxt = w + 1
        while nxt < n_weeks and mid(nxt).month == d.month:
            nxt += 1
        mhead.append(f'<div class="m" style="grid-column:{2 + w}/{2 + nxt}">{d.strftime("%b %y")}</div>')
        w = nxt
    mhead.append("</div>")
    shead = ['<div class="grow head"><div class="glabel">Sprint</div>']
    for w in range(0, n_weeks, SPRINT_WEEKS):
        shead.append(f'<div class="m" style="grid-column:{2 + w}/{2 + min(w + SPRINT_WEEKS, n_weeks)}">S{sprint_of_week(w)}</div>')
    shead.append("</div>")

    grows = []
    for c in CARRY_OVERS:
        ph = sched[c["id"]]
        bars = "".join(f'<div class="bar {k}" style="grid-column:{2 + v[0]}/{2 + v[1]}" title="{k}: {esc(date_of(v[0]))} to {esc(end_date_of(v[1]))}">{SHORT[k]}</div>'
                       for k, v in ph.items())
        grows.append(f'<div class="grow carry"><div class="glabel"><small>FY26</small>{esc(c["name"])}</div>{bars}</div>')
    for r in rows:
        i = r["i"]
        bars = "".join(f'<div class="bar {k}" style="grid-column:{2 + v[0]}/{2 + v[1]}" title="{PHASE_LONG[k]}: {esc(date_of(v[0]))} to {esc(end_date_of(v[1]))}">{SHORT[k]}</div>'
                       for k, v in r["phases"].items())
        grows.append(f'<div class="grow{" sep" if i["order"] == 1 else ""}"><div class="glabel"><small>#{i["order"]}</small><a href="#{i["id"]}">{esc(i["short"])}</a></div>{bars}</div>')
    parts.append(f"""
<h2 id="timeline">Timeline</h2>
<p>One row per initiative, one column per week from {fmt(week_start(0))}. Thin lines mark sprint boundaries. Hover a bar for its dates. The shaded zone after {fy_end} is FY28: work drawn there does not fit at the 35% reserve.</p>
<div class="legend">{legend}<span><i style="background:var(--carry-bg);border:1px solid var(--line)"></i>FY26 carry-over</span></div>
<div class="scroll"><div class="gantt">{''.join(qhead)}{''.join(mhead)}{''.join(shead)}{''.join(grows)}</div></div>
""")

    # ------------------------------------------------------ initiatives ---
    parts.append('<h2 id="initiatives">Initiatives</h2><p>Grouped by the quarter in which the build is meant to land, in execution order.</p>')
    for q in QUARTERS:
        parts.append(f'<h3 style="margin-top:36px">{esc(QUARTER_LABELS[q])}</h3>')
        for r in [x for x in rows if x["i"]["quarter"] == q]:
            i = r["i"]
            pw = phase_weeks(i)
            prow = []
            for p in PHASES:
                if p in r["phases"]:
                    s, e, lanes = r["phases"][p]
                    who = f"{lanes} dev{'s' if lanes > 1 else ''}" if p in ("BE", "App") else TEAM[p]["label"].split(" ", 1)[1]
                    prow.append(f"<tr><td>{esc(PHASE_LONG[p])}</td><td class='num'>{e - s}</td><td>{esc(who)}</td><td>{esc(date_of(s))}</td><td>{esc(end_date_of(e))}</td></tr>")
                else:
                    prow.append(f"<tr><td>{esc(PHASE_LONG[p])}</td><td class='num'>0</td><td colspan='3' style='color:var(--muted)'>not needed</td></tr>")
            asana_links = " · ".join(a(asana_url(g), f"Asana task {k + 1}" if len(i["asana"]) > 1 else "Asana task") for k, g in enumerate(i["asana"]))
            extra = f" · {a(CONFLUENCE_MODULAR, 'Confluence: Modular IMTU Component')}" if i["id"] == "G1" else ""
            pills = (f'<span class="pill">{esc(i["goal"])}</span><span class="pill">{esc(i["product"])}</span>'
                     f'<span class="pill{" high" if i["priority"] == "High" else ""}">Priority {esc(i["priority"])}</span>'
                     f'<span class="pill">{i["quarter"]}</span>'
                     + (f'<span class="pill carry">FY26 carry-over</span>' if i["fy27"] == "Carry Over" else "")
                     + (f'<span class="pill risk">lands in FY28 at 35% reserve</span>' if r["spill"] else ""))
            parts.append(f"""
<section class="init" id="{i['id']}">
<header><span class="eyebrow">#{i['order']} · {i['id']}</span>{pills}</header>
<h3>{esc(i['name'])}</h3>
<p class="lead">{esc(i['summary'])}</p>
<h4>Description</h4>
<p>{esc(i['description'])}</p>
<h4>Implementation strategy</h4>
<ol>{''.join(f'<li>{esc(s)}</li>' for s in i['strategy'])}</ol>
<div class="two">
<div>
<h4>Phases and sizing</h4>
<p style="margin-top:0;font-size:14px;color:var(--muted)">BE {esc(i['be'])} ({be_fte(i)} FTE sprints, {i['be_devs']} dev{'s' if i['be_devs'] > 1 else ''}) · App {esc(i['app'])} ({app_fte(i)} FTE sprints) · Design {esc(i['design'])}</p>
<div class="scroll"><table class="phases"><thead><tr><th>Phase</th><th class="num">Weeks</th><th>Who</th><th>Start</th><th>End</th></tr></thead><tbody>{''.join(prow)}</tbody></table></div>
</div>
<div>
<h4>Dependencies</h4>
<p style="margin-top:0">{esc(i['deps'])}</p>
<h4>Success measures</h4>
<ul>{''.join(f'<li>{esc(m)}</li>' for m in i['metrics'])}</ul>
<h4>Source</h4>
<p style="margin-top:0">{asana_links}{extra}</p>
</div>
</div>
</section>""")

    # ------------------------------------------------------- carry-over ---
    crows = "".join(
        f"<tr><td>{esc(c['name'])}</td><td>{esc(c['product'])}</td>"
        f"<td>{esc(date_of(min(v[0] for v in sched[c['id']].values())))}</td>"
        f"<td>{esc(end_date_of(max(v[1] for v in sched[c['id']].values())))}</td></tr>" for c in CARRY_OVERS)
    parts.append(f"""
<h2 id="carry">Carry-over work</h2>
<p>Four FY26 items were still In Progress when FY27 opened (see the {a(ASANA_FY26, "DCS FY26 Asana board")}). They occupy backend, app and QA lanes in the first sprints, which is why the first FY27 builds start in October rather than September. Terminus and the WhatsApp chatbot are FY26 items too, but they are FY27 Business goals, so they appear as initiatives 1 and 2.</p>
<div class="scroll"><table><thead><tr><th>FY26 item</th><th>Product</th><th>Occupies from</th><th>Until</th></tr></thead><tbody>{crows}</tbody></table></div>
""")

    # ------------------------------------------------------------ FY28 ---
    srows = "".join(
        f"<tr><td class='num'>{r['i']['order']}</td><td><a href='#{r['i']['id']}'>{esc(r['i']['name'])}</a></td><td>{esc(r['i']['priority'])}</td>"
        f"<td>{esc(date_of(r['phases']['BE'][0]))}</td><td>{esc(r['end_date'])}</td></tr>" for r in spill)
    parts.append(f"""
<h2 id="fy28">What lands in FY28</h2>
<p>At the 35% tech reserve the backend lanes are fully booked from October 2026 to the end of the year, and the initiatives below start their backend build too late to finish by {fy_end}. Three levers close the gap, in order of preference: engineering validates the estimates down (the Bundling service alone is nine FTE sprints); the reserve drops to 20% for the second half, which adds about {round(3 * sprints * 0.15)} backend sprints; or the lowest-priority items (Crypto checkout, Gamification) are formally moved to FY28.</p>
<div class="scroll"><table><thead><tr><th class="num">#</th><th>Initiative</th><th>Priority</th><th>Backend starts</th><th>Ends</th></tr></thead><tbody>{srows}</tbody></table></div>
""")

    # --------------------------------------------------------- sources ---
    parts.append(f"""
<h2 id="sources">Sources and conventions</h2>
<ul>
<li>{a(ASANA_PROJECT, "DCS FY27 Asana board")}: the 44 items in Ideas; Board and Business goals scheduled here, Backlog items left out by decision, duplicate pairs merged (each merged initiative links both tasks).</li>
<li>{a(ASANA_FY26, "DCS FY26 Asana board")}: status of the carry-over work.</li>
<li>{a(FY26_SHEET, "DCS FY26 Initiatives spreadsheet")}: the sizing scale, the 35% tech reserve, the phase colours and the tab layout this plan's spreadsheet copies.</li>
<li>{a(CONFLUENCE_MODULAR, "Modular IMTU Component")} on Confluence: the starting spec for initiative 4.</li>
{("<li>" + a(sheet_url, "DCS FY27 Initiatives spreadsheet") + ": Tech and Business estimates, the weekly Timelines Gantt, the Sequence tab with every phase date, and the Capacity tab with the assumptions.</li>") if sheet_url else ""}
</ul>
<p class="byline">Neither the Asana boards nor the FY26 spreadsheet were modified. Generated from fy27_plan_data.py and fy27_schedule.py in the IDT-Claude repository.</p>
</div>
""")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet-url", default="")
    ap.add_argument("--doc-url", default="")
    args = ap.parse_args()
    build(args.sheet_url, args.doc_url)
