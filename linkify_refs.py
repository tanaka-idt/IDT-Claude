#!/usr/bin/env python3
"""
Makes every reference in a Google Doc clickable.

Two kinds of reference are handled:

1. Jira issue keys - DCS-1234, OMTU-7551, BAT-7936 - linked automatically to
   idtjira by pattern, no configuration needed.
2. Named sources - Confluence page titles, Figma files, Amplitude dashboards,
   anything else - linked from a phrase -> URL map. Pass a JSON file with
   --map, or import LINK_MAP and extend it.

Bare URLs already written as text are linked too, so a doc that pastes
"https://..." inline becomes clickable without extra config.

Walks body paragraphs and table cells alike. Text-style requests do not shift
indices, so everything is applied in one pass without re-fetching. Runs that
already carry a link are skipped, so this is safe to re-run on any document.

Usage:
    python linkify_refs.py <doc_id> [<doc_id> ...] [--map refs.json]
"""

import argparse
import json
import re
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

JIRA_BASE = "https://idtjira.atlassian.net/browse/"
WIKI = "https://idtjira.atlassian.net/wiki/spaces"

KEY = re.compile(r"\b([A-Z]{2,8}-\d+)\b")
URL = re.compile(r"https?://[^\s,)\]]+")

# Named sources referenced often enough to be worth keeping here.
# Phrase -> URL. Longest phrases are matched first.
LINK_MAP = {
    "MTU Home Page Redesign BR7":
        f"{WIKI}/DCS/pages/5824217133/MTU+Home+Page+Redesign+BR7",
    "MTU Home Page Redesign (BR7)":
        f"{WIKI}/DCS/pages/5824217133/MTU+Home+Page+Redesign+BR7",
    "Modular IMTU Component":
        f"{WIKI}/DCS/pages/6002180195/Modular+IMTU+Component",
    "MTU Gamification":
        f"{WIKI}/DCS/pages/6135676962/MTU+Gamification+Braze+In-App+Messages",
    "MTU Activity widget":
        f"{WIKI}/BOSS/pages/5592809513/MTU+Activity+widget",
    "Jira Template Suggestions":
        f"{WIKI}/DCS/pages/5868127031/Jira+Template+Suggestions",
}

LINK_RGB = {"red": 0.10, "green": 0.32, "blue": 0.75}


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def iter_text_runs(elements):
    """Yield (start_index, text) for every text run, descending into tables."""
    for el in elements:
        if "paragraph" in el:
            for e in el["paragraph"]["elements"]:
                run = e.get("textRun")
                if not run:
                    continue
                if run.get("textStyle", {}).get("link"):
                    continue          # already linked - keeps re-runs idempotent
                yield e["startIndex"], run.get("content", "")
        elif "table" in el:
            for row in el["table"]["tableRows"]:
                for cell in row["tableCells"]:
                    yield from iter_text_runs(cell["content"])
        elif "tableOfContents" in el:
            yield from iter_text_runs(el["tableOfContents"].get("content", []))


def link_request(start, end, url):
    return {"updateTextStyle": {
        "range": {"startIndex": start, "endIndex": end},
        "textStyle": {
            "link": {"url": url},
            "foregroundColor": {"color": {"rgbColor": LINK_RGB}},
            "underline": True,
        },
        "fields": "link,foregroundColor,underline",
    }}


def spans_for(text, start, link_map):
    """Return (start, end, url, label) for each reference found in one run."""
    hits, taken = [], []

    def free(s, e):
        return all(e <= ts or s >= te for ts, te in taken)

    # Bare URLs first - they must not be re-matched by the phrase pass.
    for m in URL.finditer(text):
        hits.append((start + m.start(), start + m.end(), m.group(0), m.group(0)))
        taken.append((m.start(), m.end()))

    # Named phrases, longest first so a longer title wins over a substring.
    for phrase in sorted(link_map, key=len, reverse=True):
        for m in re.finditer(re.escape(phrase), text):
            if free(m.start(), m.end()):
                hits.append((start + m.start(), start + m.end(),
                             link_map[phrase], phrase))
                taken.append((m.start(), m.end()))

    # Jira keys.
    for m in KEY.finditer(text):
        if free(m.start(), m.end()):
            hits.append((start + m.start(), start + m.end(),
                         JIRA_BASE + m.group(1), m.group(1)))
            taken.append((m.start(), m.end()))

    return hits


def linkify(docs, doc_id, link_map=None):
    link_map = LINK_MAP if link_map is None else link_map
    doc = docs.documents().get(documentId=doc_id).execute()
    title = doc.get("title", doc_id)

    reqs, labels = [], []
    for start, text in iter_text_runs(doc["body"]["content"]):
        for s, e, url, label in spans_for(text, start, link_map):
            reqs.append(link_request(s, e, url))
            labels.append(label)

    if not reqs:
        print(f"  {title}: nothing to link (already done?)")
        return 0

    for i in range(0, len(reqs), 40):
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": reqs[i:i + 40]}).execute()
        time.sleep(0.25)

    uniq = sorted(set(labels))
    print(f"  {title}: linked {len(reqs)} references ({len(uniq)} unique)")
    return len(reqs)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("doc_ids", nargs="+")
    ap.add_argument("--map", dest="map_file",
                    help="JSON file of extra phrase -> URL entries")
    args = ap.parse_args()

    link_map = dict(LINK_MAP)
    if args.map_file:
        link_map.update(json.loads(Path(args.map_file).read_text()))

    docs = build("docs", "v1", credentials=get_credentials())
    for doc_id in args.doc_ids:
        linkify(docs, doc_id, link_map)


if __name__ == "__main__":
    main()
