#!/usr/bin/env python3
"""
Creates the Google Doc "DCS FY27 Initiative Plan" from the shared plan data:
summary, method, sequence table, one section per initiative (description,
implementation strategy, phases and sizing, dependencies, success measures),
carry-over work, FY28 spill, sources. Every reference is linked through
linkify_refs (bare URLs plus a phrase map).

Usage:
    python build_fy27_doc.py [--sheet-url URL] [--html-url URL]
"""

import argparse
import time
from datetime import timedelta

from googleapiclient.discovery import build

from fy27_plan_data import (INITIATIVES, CARRY_OVERS, TEAM, PHASES, PHASE_LONG, QUARTERS,
                            QUARTER_LABELS, WEEKS, SPRINT_WEEKS, TECH_RESERVE, ASANA_PROJECT,
                            ASANA_FY26, FY26_SHEET, CONFLUENCE_MODULAR, asana_url, be_fte,
                            app_fte, week_start, fmt)
from fy27_schedule import schedule, summary_rows
from linkify_refs import get_credentials, linkify, LINK_MAP

TITLE = "DCS FY27 Initiative Plan"
FOLDER_ID = "1PM0j7sUc2cG5tVYUC5yojA7E95x-vBDi"
STYLE_MAP = {"h1": "HEADING_1", "h2": "HEADING_2", "h3": "HEADING_3",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "n": "NORMAL_TEXT", "cap": "NORMAL_TEXT"}


def date_of(w):
    return fmt(week_start(w))


def end_date_of(w):
    return fmt(week_start(w) - timedelta(days=1))


def utf16(s):
    return len(s.encode("utf-16-le")) // 2


# --------------------------------------------------------------- content ---

def content(sheet_url, html_url):
    sched = schedule()
    rows = summary_rows(sched)
    board = [r for r in rows if r["i"]["goal"] == "Board Goal"]
    biz = [r for r in rows if r["i"]["goal"] == "Business Goal"]
    spill = [r for r in rows if r["spill"]]
    sprints = WEEKS // SPRINT_WEEKS
    be_demand = sum(be_fte(i) for i in INITIATIVES)
    app_demand = sum(app_fte(i) for i in INITIATIVES)
    cap = round(3 * sprints * (1 - TECH_RESERVE))
    fy_end = end_date_of(WEEKS)

    B, T = [], []
    B.append(("h1", TITLE))
    B.append(("cap", f"Prepared by João Tanaka, 16 September 2026, descriptions revised 17 September 2026. Fiscal year {fmt(week_start(0))} to {fy_end}. "
                     f"Source: DCS FY27 Asana board."))
    B.append(("p", f"Description, implementation strategy and phased schedule for the {len(rows)} Board and Business goals on the "
                   f"DCS FY27 Asana board ({ASANA_PROJECT})."))
    if sheet_url:
        B.append(("p", f"Companion spreadsheet with estimates, weekly timeline and phase dates: DCS FY27 Initiatives spreadsheet ({sheet_url})."))
    if html_url:
        B.append(("p", f"Interactive version of this document: {html_url}"))

    B.append(("h2", "Summary"))
    B.append(("p", f"The FY27 board lists {len(rows)} goals once duplicates are merged: {len(board)} Board goals and {len(biz)} Business goals. "
                   f"Backend is the constraint. The goals ask for about {be_demand} backend FTE sprints while three developers minus the 35% tech reserve "
                   f"provide {cap} across {sprints} sprints, so roughly {be_demand - cap} sprints of backend work do not fit inside the year. "
                   f"App demand ({app_demand} FTE sprints) fits with a little slack, which is why backend-light initiatives run in parallel with the heavy ones."))
    B.append(("p", "The order follows three rules. First, finish what is in flight (Terminus, the WhatsApp chatbot) and build the pieces other goals reuse "
                   "(the IMTU module, Engager cards). Second, put the High-priority revenue and payments work in Q2 so it lands before the second half. "
                   "Third, give the two largest builds (Bundling, ROW expansion) a full quarter of backend in Q3 with their discovery done in Q2. "
                   "The Q4 slate (Engager personalisation, Wallet promo balances, IVA migration, Gamification, Crypto) is where the capacity gap shows: "
                   "at the 35% reserve those initiatives start their build in the last sprints and finish in FY28."))
    B.append(("p", "Every estimate is a PM first pass on the FY26 scale (S 1, M 2, L 4, XL 9 FTE sprints). Engineering should validate them in the "
                   "Comments column of the spreadsheet before the plan is committed, as Marc and Ilya did for FY26."))

    B.append(("h2", "How the plan was built"))
    B.append(("p", "Every initiative goes through the same six phases in strict order: the PM defines requirements and strategy, Design produces the screens, "
                   "the TPM runs the spike and breaks the work into tickets, Backend builds the services, App builds the UI, QA tests and releases. "
                   "A role that finishes one initiative starts the next the following week, so the roles form a pipeline and several initiatives are in flight at once."))
    B.append(("p", "Capacity is modelled as parallel lanes per role. Backend and App have three people each, but 35% of their time is reserved for tech debt "
                   "and company tech goals, as in FY26, which leaves two lanes for initiatives. Large backend builds take both lanes; the rest take one. "
                   "The PM may start discovery up to eight weeks before the target quarter so specifications do not go stale."))
    team = [["Role", "People", "Parallel lanes", "Note"]]
    for role in PHASES:
        team.append([role, TEAM[role]["label"], str(TEAM[role]["lanes"]), TEAM[role]["note"] or PHASE_LONG[role]])
    T.append(("TEAM", team)); B.append(("table", "TEAM"))

    B.append(("h2", "Sequence and dates"))
    B.append(("p", "The proposed execution order. Start is the first PM week and End is the last QA week. BE and App show size and FTE sprints."))
    seq = [["#", "Initiative", "Goal", "Priority", "Q", "BE", "App", "Start", "End", "Status"]]
    for r in rows:
        i = r["i"]
        status = "Lands in FY28" if r["spill"] else ("Carry over" if i["fy27"] == "Carry Over" else "Fits FY27")
        seq.append([str(i["order"]), i["name"], i["goal"].replace(" Goal", ""), i["priority"], i["quarter"],
                    f"{i['be']} ({be_fte(i)})", f"{i['app']} ({app_fte(i)})", date_of(r["start"]), r["end_date"], status])
    T.append(("SEQ", seq)); B.append(("table", "SEQ"))

    B.append(("h2", "Capacity check"))
    capt = [["Role", "Demand (FTE sprints)", "Available at 35% reserve", "Gap"],
            ["Backend", str(be_demand), str(cap), str(cap - be_demand)],
            ["App", str(app_demand), str(cap), str(cap - app_demand)]]
    T.append(("CAP", capt)); B.append(("table", "CAP"))
    B.append(("p", f"Available = 3 developers x {sprints} sprints x (1 - 35%). A negative gap means the work does not fit inside FY27 at this reserve."))

    B.append(("h2", "Initiatives"))
    B.append(("p", "Grouped by the quarter in which the build is meant to land, in execution order."))
    for q in QUARTERS:
        B.append(("h2", QUARTER_LABELS[q]))
        for r in [x for x in rows if x["i"]["quarter"] == q]:
            i = r["i"]
            B.append(("h3", f"{i['order']}. {i['name']}"))
            tags = f"{i['goal']} · {i['product']} · Priority {i['priority']} · {i['quarter']} · {i['fy27']}"
            if r["spill"]:
                tags += " · Lands in FY28 at the 35% reserve"
            B.append(("cap", tags))
            B.append(("p", i["summary"]))
            for par in i["long"].split("\n\n"):
                B.append(("p", par))
            B.append(("p", "Implementation strategy"))
            for s in i["strategy"]:
                B.append(("n", s))
            B.append(("p", f"Phases and sizing. BE {i['be']} ({be_fte(i)} FTE sprints, {i['be_devs']} dev{'s' if i['be_devs'] > 1 else ''}), "
                           f"App {i['app']} ({app_fte(i)} FTE sprints), Design {i['design']}."))
            ph = [["Phase", "Weeks", "Who", "Start", "End"]]
            for p in PHASES:
                if p in r["phases"]:
                    s, e, lanes = r["phases"][p]
                    who = f"{lanes} dev{'s' if lanes > 1 else ''}" if p in ("BE", "App") else TEAM[p]["label"].split(" ", 1)[1]
                    ph.append([PHASE_LONG[p], str(e - s), who, date_of(s), end_date_of(e)])
                else:
                    ph.append([PHASE_LONG[p], "0", "not needed", "", ""])
            key = f"PH_{i['id']}"
            T.append((key, ph)); B.append(("table", key))
            B.append(("p", f"Dependencies: {i['deps']}"))
            B.append(("p", "Success measures"))
            for m in i["metrics"]:
                B.append(("b", m))
            links = " and ".join(asana_url(g) for g in i["asana"])
            src = f"Source: Asana {links}"
            if i["id"] == "G1":
                src += f". Confluence: Modular IMTU Component ({CONFLUENCE_MODULAR})"
            B.append(("cap", src))

    B.append(("h2", "Carry-over work"))
    B.append(("p", f"Four FY26 items were still In Progress when FY27 opened (DCS FY26 Asana board, {ASANA_FY26}). They occupy backend, app and QA lanes "
                   "in the first sprints, which is why the first FY27 builds start in October rather than September. Terminus and the WhatsApp chatbot are "
                   "FY26 items too, but they are FY27 Business goals, so they appear as initiatives 1 and 2."))
    ct = [["FY26 item", "Product", "Occupies from", "Until"]]
    for c in CARRY_OVERS:
        ph = sched[c["id"]]
        ct.append([c["name"], c["product"], date_of(min(v[0] for v in ph.values())), end_date_of(max(v[1] for v in ph.values()))])
    T.append(("CARRY", ct)); B.append(("table", "CARRY"))

    B.append(("h2", "What lands in FY28"))
    B.append(("p", f"At the 35% tech reserve the backend lanes are fully booked from October 2026 to the end of the year, and the initiatives below start "
                   f"their backend build too late to finish by {fy_end}. Three levers close the gap, in order of preference: engineering validates the "
                   f"estimates down (the Bundling service alone is nine FTE sprints); the reserve drops to 20% for the second half, which adds about "
                   f"{round(3 * sprints * 0.15)} backend sprints; or the lowest-priority items (Crypto checkout, Gamification) are formally moved to FY28."))
    st = [["#", "Initiative", "Priority", "Backend starts", "Ends"]]
    for r in spill:
        st.append([str(r["i"]["order"]), r["i"]["name"], r["i"]["priority"], date_of(r["phases"]["BE"][0]), r["end_date"]])
    T.append(("SPILL", st)); B.append(("table", "SPILL"))

    B.append(("h2", "Sources and conventions"))
    B.append(("b", f"DCS FY27 Asana board ({ASANA_PROJECT}): the 44 items in Ideas. Board and Business goals are scheduled here, Backlog items were left out by decision, and the six duplicate pairs were merged; each merged initiative cites both tasks."))
    B.append(("b", f"DCS FY26 Asana board ({ASANA_FY26}): status of the carry-over work."))
    B.append(("b", f"DCS FY26 Initiatives spreadsheet ({FY26_SHEET}): the sizing scale, the 35% tech reserve, the phase colours and the tab layout the FY27 spreadsheet copies."))
    if sheet_url:
        B.append(("b", f"DCS FY27 Initiatives spreadsheet ({sheet_url}): Tech and Business estimates, the weekly Timelines Gantt, the Sequence tab with every phase date, and the Capacity tab with the assumptions."))
    B.append(("cap", "Neither the Asana boards nor the FY26 spreadsheet were modified. Generated from fy27_plan_data.py and fy27_schedule.py in the IDT-Claude repository."))
    return B, T


# ------------------------------------------------------------ docs API ---

def build_requests(blocks):
    reqs, cur = [], 1
    for kind, text in blocks:
        if kind == "table":
            line = f"[[{text}]]\n"
            reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
            cur += utf16(line)
            continue
        line = text + "\n"
        n = utf16(line)
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        para = {"namedStyleType": STYLE_MAP[kind]}
        fields = "namedStyleType"
        reqs.append({"updateParagraphStyle": {"range": {"startIndex": cur, "endIndex": cur + n},
                                              "paragraphStyle": para, "fields": fields}})
        if kind == "b":
            reqs.append({"createParagraphBullets": {"range": {"startIndex": cur, "endIndex": cur + n},
                                                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind == "n":
            reqs.append({"createParagraphBullets": {"range": {"startIndex": cur, "endIndex": cur + n},
                                                    "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"}})
        if kind == "cap":
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + utf16(text)},
                                             "textStyle": {"italic": True, "fontSize": {"magnitude": 9, "unit": "PT"}},
                                             "fields": "italic,fontSize"}})
        if kind == "p" and (text in ("Implementation strategy", "Success measures") or text.startswith("Phases and sizing.") or text.startswith("Dependencies:")):
            lead = text.split(".")[0] if text.startswith("Phases") else (text.split(":")[0] if text.startswith("Dependencies") else text)
            reqs.append({"updateTextStyle": {"range": {"startIndex": cur, "endIndex": cur + utf16(lead)},
                                             "textStyle": {"bold": True}, "fields": "bold"}})
        cur += n
    return reqs


WRITE_GAP = 1.3          # seconds between write calls: the Docs API allows 60 writes per minute per user


def write(docs, doc_id, requests):
    """One batchUpdate, throttled, with a wait-and-retry when the per-minute quota is hit."""
    from googleapiclient.errors import HttpError
    for attempt in range(4):
        try:
            res = docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
            time.sleep(WRITE_GAP)
            return res
        except HttpError as e:
            if e.resp.status == 429 and attempt < 3:
                print("  quota hit, waiting 65 s")
                time.sleep(65)
                continue
            raise


def batched(docs, doc_id, reqs, size=40):
    for i in range(0, len(reqs), size):
        write(docs, doc_id, reqs[i:i + size])


def para_text(el):
    if "paragraph" not in el:
        return ""
    return "".join(e.get("textRun", {}).get("content", "") for e in el["paragraph"]["elements"])


def insert_table(docs, doc_id, marker, data):
    doc = docs.documents().get(documentId=doc_id).execute()
    idx = plen = None
    for el in doc["body"]["content"]:
        if para_text(el).strip() == f"[[{marker}]]":
            idx, plen = el["startIndex"], utf16(para_text(el))
            break
    if idx is None:
        print(f"  ! placeholder {marker} not found")
        return False
    rows, cols = len(data), len(data[0])
    write(docs, doc_id, [
        {"deleteContentRange": {"range": {"startIndex": idx, "endIndex": idx + plen - 1}}},
        {"insertTable": {"location": {"index": idx}, "rows": rows, "columns": cols}},
    ])
    doc = docs.documents().get(documentId=doc_id).execute()
    table_el = next((el for el in doc["body"]["content"] if "table" in el and el["startIndex"] >= idx - 2), None)
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
        if not txt:
            continue
        reqs.append({"insertText": {"location": {"index": start}, "text": txt}})
        style = {"fontSize": {"magnitude": 9, "unit": "PT"}}
        fields = "fontSize"
        if r == 0:
            style["bold"] = True
            fields += ",bold"
        reqs.append({"updateTextStyle": {"range": {"startIndex": start, "endIndex": start + utf16(txt)},
                                         "textStyle": style, "fields": fields}})
    batched(docs, doc_id, reqs, size=40)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet-url", default="")
    ap.add_argument("--html-url", default="")
    ap.add_argument("--doc-id", default="", help="rebuild this existing document in place instead of creating a new one")
    args = ap.parse_args()

    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    blocks, tables = content(args.sheet_url, args.html_url)
    if args.doc_id:
        doc_id = args.doc_id
        doc = docs.documents().get(documentId=doc_id).execute()
        end = doc["body"]["content"][-1]["endIndex"]
        if end > 2:
            write(docs, doc_id, [{"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1}}}])
        print(f"Cleared doc: {doc_id}")
    else:
        doc = docs.documents().create(body={"title": TITLE}).execute()
        doc_id = doc["documentId"]
        print(f"Created doc: {doc_id}")
    reqs = build_requests(blocks)
    batched(docs, doc_id, reqs)
    print(f"Inserted {len(reqs)} text requests")
    for marker, data in tables:
        ok = insert_table(docs, doc_id, marker, data)
        print(f"  table {marker}: {'ok' if ok else 'FAILED'} ({len(data) - 1} rows)")

    link_map = dict(LINK_MAP)
    link_map.update({
        "DCS FY27 Asana board": ASANA_PROJECT,
        "DCS FY26 Asana board": ASANA_FY26,
        "DCS FY26 Initiatives spreadsheet": FY26_SHEET,
        "Modular IMTU Component": CONFLUENCE_MODULAR,
    })
    if args.sheet_url:
        link_map["DCS FY27 Initiatives spreadsheet"] = args.sheet_url
    linkify(docs, doc_id, link_map)

    f = drive.files().get(fileId=doc_id, fields="parents").execute()
    if FOLDER_ID not in f.get("parents", []):
        drive.files().update(fileId=doc_id, addParents=FOLDER_ID,
                             removeParents=",".join(f.get("parents", [])), fields="id,parents").execute()
    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"Google Doc: {url}")
    return url


if __name__ == "__main__":
    main()
