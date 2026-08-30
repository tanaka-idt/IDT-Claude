#!/usr/bin/env python3
"""
Apply a run-level translation to an existing Google Doc, in place.

Why this is fiddly: a Docs paragraph is made of several text runs, each with its
own formatting (a bold lead, a linked Jira key, an italic caption). Replacing a
whole paragraph would flatten all of that. So we replace ONE RUN AT A TIME, and
we do it by inserting the new text INSIDE the run before deleting the old text —
inserted text inherits the formatting of the character it is inserted after, so
bold, italics and hyperlinks all survive.

Two further rules keep the document structure intact:

  * The paragraph's trailing newline is never touched. Deleting it would merge
    paragraphs. We only ever replace the stripped core of a run and re-attach the
    original leading/trailing whitespace positions.
  * Runs are applied in DESCENDING index order. Edits at high indices do not
    shift low indices, so every precomputed index stays valid — including within
    a single batchUpdate, which applies its requests sequentially.

Usage:
    python3 apply_translation.py <doc_id> <runs.json> <translations.json>
"""

import json
import sys
import time

from googleapiclient.discovery import build

from create_felix_whatsapp_analysis_doc import get_credentials


def build_requests(runs, translations):
    """One (insert, delete, delete) triple per changed run, descending by index."""
    reqs = []
    changed = skipped = 0

    for idx in sorted(range(len(runs)), key=lambda i: -runs[i]["start"]):
        pt = translations.get(str(idx), translations.get(idx))
        if pt is None:
            continue

        raw = runs[idx]["text"]
        core = raw.strip()
        if not core or pt == core:
            skipped += 1
            continue

        # Offsets of the stripped core inside the run.
        lead = len(raw) - len(raw.lstrip())
        cs = runs[idx]["start"] + lead
        n_old = len(core)
        n_new = len(pt)

        # 1. Insert the translation one character in, so it inherits this run's
        #    formatting rather than the previous run's.
        reqs.append({"insertText": {"location": {"index": cs + 1}, "text": pt}})
        # 2. Remove the tail of the original (everything after its first char).
        if n_old > 1:
            reqs.append({"deleteContentRange": {"range": {
                "startIndex": cs + 1 + n_new,
                "endIndex": cs + 1 + n_new + n_old - 1}}})
        # 3. Remove the original's first character.
        reqs.append({"deleteContentRange": {"range": {
            "startIndex": cs, "endIndex": cs + 1}}})
        changed += 1

    return reqs, changed, skipped


def main():
    doc_id, runs_file, trans_file = sys.argv[1], sys.argv[2], sys.argv[3]

    runs = json.load(open(runs_file))["runs"]
    translations = json.load(open(trans_file))

    reqs, changed, skipped = build_requests(runs, translations)
    print(f"runs: {len(runs)} | changed: {changed} | unchanged/skipped: {skipped}")
    print(f"requests: {len(reqs)}")

    docs = build("docs", "v1", credentials=get_credentials())
    for i in range(0, len(reqs), 50):
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": reqs[i:i + 50]}).execute()
        time.sleep(0.3)
        print(f"  applied {min(i + 50, len(reqs))}/{len(reqs)}")

    print(f"\nDone: https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
