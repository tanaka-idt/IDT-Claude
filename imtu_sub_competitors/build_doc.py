"""Build the 'IMTU Subscriptions: Competitor Investigation and 12-Month Plan' Google Doc.

Usage:
  python3 build_doc.py                 # rebuild the existing doc in place
  python3 build_doc.py --html-only     # write build/imtu_sub_competitors.html only
  python3 build_doc.py --doc-id <id>   # rebuild another doc

Renders content_a/b/c into one HTML file with embedded images (docbuilder.py), uploads it
to Drive with conversion to Google Docs (same file id, same URL), then runs linkify_refs so
any Jira key or bare URL left unlinked becomes a link.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import docbuilder  # noqa: E402
from content_a import BLOCKS_A  # noqa: E402
from content_b import BLOCKS_B  # noqa: E402
from content_c import BLOCKS_C  # noqa: E402

TITLE = "IMTU Subscriptions: Competitor Investigation and 12-Month Plan (Sep 2026)"
DOC_ID = "1kgzZwKzGDbx0BywM7E_JUhUr1-FQyB4DtwnzgkuKoMo"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc-id", default=DOC_ID)
    ap.add_argument("--html-only", action="store_true")
    args = ap.parse_args()

    import os
    os.chdir(HERE)
    blocks = BLOCKS_A + BLOCKS_B + BLOCKS_C
    html = docbuilder.render(blocks, TITLE)
    out = HERE / "build" / "imtu_sub_competitors.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"HTML: {out} ({len(html) / 1e6:.1f} MB, {sum(1 for b in blocks if b[0] in ('figure', 'row'))} image blocks)")
    if args.html_only:
        return

    doc_id, creds = docbuilder.publish(html, TITLE, args.doc_id)
    print(f"Uploaded: https://docs.google.com/document/d/{doc_id}/edit")

    from googleapiclient.discovery import build
    from linkify_refs import LINK_MAP, linkify
    docs = build("docs", "v1", credentials=creds)
    print(f"Paragraph polish: {docbuilder.polish(docs, doc_id)} headings")
    linkify(docs, doc_id, LINK_MAP)
    print(f"Done: https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
