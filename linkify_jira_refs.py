#!/usr/bin/env python3
"""
Turns every Jira issue key in a Google Doc into a clickable link to idtjira.

Walks the whole document - body paragraphs and table cells - finds keys like
DCS-1234 / OMTU-7551 / BAT-7936, and applies a hyperlink to each occurrence.
Text styling requests do not shift indices, so all edits are applied in one
pass without re-fetching.

Runs are skipped if they already carry a link, so this is safe to re-run.

Usage:
    python linkify_jira_refs.py <doc_id> [<doc_id> ...]
"""

import re
import sys
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
KEY = re.compile(r"\b([A-Z]{2,8}-\d+)\b")

# Link colour: a muted blue that reads on the default Docs white page.
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
                # Leave already-linked runs alone so re-runs are idempotent.
                if run.get("textStyle", {}).get("link"):
                    continue
                yield e["startIndex"], run.get("content", "")
        elif "table" in el:
            for row in el["table"]["tableRows"]:
                for cell in row["tableCells"]:
                    yield from iter_text_runs(cell["content"])
        elif "tableOfContents" in el:
            yield from iter_text_runs(el["tableOfContents"].get("content", []))


def build_link_requests(doc):
    reqs, seen = [], []
    for start, text in iter_text_runs(doc["body"]["content"]):
        for m in KEY.finditer(text):
            s, e = start + m.start(), start + m.end()
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": s, "endIndex": e},
                "textStyle": {
                    "link": {"url": JIRA_BASE + m.group(1)},
                    "foregroundColor": {"color": {"rgbColor": LINK_RGB}},
                    "underline": True,
                },
                "fields": "link,foregroundColor,underline",
            }})
            seen.append(m.group(1))
    return reqs, seen


def linkify(docs, doc_id):
    doc = docs.documents().get(documentId=doc_id).execute()
    title = doc.get("title", doc_id)
    reqs, seen = build_link_requests(doc)
    if not reqs:
        print(f"  {title}: nothing to link (already done?)")
        return 0
    for i in range(0, len(reqs), 40):
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": reqs[i:i + 40]}).execute()
        time.sleep(0.25)
    uniq = sorted(set(seen))
    print(f"  {title}: linked {len(reqs)} references ({len(uniq)} unique)")
    print(f"    {', '.join(uniq[:12])}{' …' if len(uniq) > 12 else ''}")
    return len(reqs)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    docs = build("docs", "v1", credentials=get_credentials())
    for doc_id in sys.argv[1:]:
        linkify(docs, doc_id)


if __name__ == "__main__":
    main()
