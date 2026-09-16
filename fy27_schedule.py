#!/usr/bin/env python3
"""
Greedy resource-constrained scheduler for the FY27 plan.

Each initiative runs its phases in strict sequence (PM, Design, TPM, BE, App,
QA). Each role has a fixed number of lanes (see TEAM in fy27_plan_data). An
initiative is scheduled in priority order: every phase starts at the later of
"previous phase finished" and "enough lanes are free", and a lane that finishes
one initiative picks up the next one immediately. A phase with zero weeks is
skipped. PM may start at most PM_LEAD weeks before the initiative's quarter so
specs do not go stale.

Output: for each initiative, a dict phase -> (start_week, end_week_exclusive,
lanes_used). Week 0 is 31 Aug 2026.
"""

from fy27_plan_data import (INITIATIVES, CARRY_OVERS, TEAM, PHASES, QUARTERS,
                            WEEKS, phase_weeks, week_start, fmt, sprint_of_week)

PM_LEAD = 8


class Lanes:
    def __init__(self, n):
        self.free = [0] * n

    def book(self, ready, weeks, k):
        """Earliest start >= ready at which k lanes are free; books them."""
        k = min(k, len(self.free))
        order = sorted(range(len(self.free)), key=lambda i: self.free[i])
        start = max(ready, self.free[order[k - 1]])
        for i in order[:k]:
            self.free[i] = start + weeks
        return start


def schedule():
    lanes = {role: Lanes(TEAM[role]["lanes"]) for role in PHASES}
    out = {}

    # FY26 carry-overs occupy App and QA from week 0.
    for c in CARRY_OVERS:
        ph = {}
        ready = 0
        if c["be_w"]:
            s = lanes["BE"].book(0, c["be_w"], 1)
            ph["BE"] = (s, s + c["be_w"], 1)
            ready = ph["BE"][1]
        s = lanes["App"].book(ready, c["app_w"], c["app_devs"])
        ph["App"] = (s, s + c["app_w"], c["app_devs"])
        s = lanes["QA"].book(ph["App"][1], c["qa_w"], 1)
        ph["QA"] = (s, s + c["qa_w"], 1)
        out[c["id"]] = ph

    for i in sorted(INITIATIVES, key=lambda x: x["order"]):
        w = phase_weeks(i)
        ready = max(0, QUARTERS[i["quarter"]] - PM_LEAD)
        ph = {}
        for role in PHASES:
            if w[role] == 0:
                continue
            k = i["be_devs"] if role == "BE" else i["app_devs"] if role == "App" else 1
            s = lanes[role].book(ready, w[role], k)
            ph[role] = (s, s + w[role], k)
            ready = s + w[role]
        out[i["id"]] = ph
    return out


def start_end(ph):
    s = min(v[0] for v in ph.values())
    e = max(v[1] for v in ph.values())
    return s, e


def summary_rows(sched):
    rows = []
    for i in sorted(INITIATIVES, key=lambda x: x["order"]):
        ph = sched[i["id"]]
        s, e = start_end(ph)
        rows.append(dict(
            i=i, start=s, end=e,
            start_date=fmt(week_start(s)), end_date=fmt(week_start(e) - __import__("datetime").timedelta(days=1)),
            spill=e > WEEKS,
            phases={r: ph[r] for r in PHASES if r in ph},
        ))
    return rows


if __name__ == "__main__":
    sched = schedule()
    for r in summary_rows(sched):
        i = r["i"]
        ph = " ".join(f"{k}:{v[0]}-{v[1] - 1}" for k, v in r["phases"].items())
        flag = "  << past FY end" if r["spill"] else ""
        print(f"{i['order']:2} {i['id']:3} {i['quarter']} {i['short'][:32]:32} "
              f"{r['start_date']:>12} -> {r['end_date']:>12}  {ph}{flag}")
    for role in PHASES:
        busy = sum(v[1] - v[0] for ph in sched.values() for k, v in ph.items() if k == role) 
    print()
    for role in PHASES:
        used = sum((v[1] - v[0]) * v[2] for ph in sched.values() for k, v in ph.items() if k == role)
        print(f"{role:6} lane-weeks used {used:3} of {TEAM[role]['lanes'] * WEEKS}")
