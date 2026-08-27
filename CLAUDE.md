# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IDT product-management workspace. Holds roadmaps, competitor analyses, and product specs (Markdown) alongside Python scripts that generate formatted Google Docs — with embedded charts, diagrams, and screen designs — for IMTU, Boss Money, eGift, eSIM, and crypto-payment initiatives.

## Build & Run

Install dependencies:
```bash
pip install matplotlib google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

The `create_*.py` scripts each build a specific Google Doc (e.g. `create_imtu_doc.py`, `create_crypto_payment_doc.py`, `create_boss_money_prd.py`). Run the one you need:
```bash
python create_imtu_doc.py
```

**Google Docs Integration Setup (one-time):**
1. Go to https://console.cloud.google.com
2. Create a project or select existing one
3. Enable: Google Docs API + Google Drive API
4. Credentials → Create → OAuth 2.0 Client ID → Desktop app
5. Download JSON credentials → save as `credentials.json` in project root
6. Run a `create_*.py` script — browser tab opens for authorization

## Git & GitHub Workflow

**IMPORTANT: Always commit and push to GitHub regularly.** This ensures no work is ever lost and provides a complete history of the project.

- Make commits after completing meaningful work (new features, bug fixes, documentation updates)
- Use clear, descriptive commit messages in imperative form (e.g., "Add IMTU FY27 roadmap" not "added stuff")
- Push to GitHub immediately after committing: `git push origin main`
- Before starting new work, verify the repository is up to date with `git status`
- If reverting changes is needed, use `git log --oneline` to find commits and `git revert <commit-hash>` or `git reset`

**Repository:** https://github.com/tanaka-idt/IDT-Claude

## Jira Ticket Creation

Always follow the DCS team's Jira template guidelines when creating tickets:
**Template reference:** https://idtjira.atlassian.net/wiki/spaces/DCS/pages/5868127031/Jira+Template+Suggestions

Key rules:
- Summary prefix must match role: `[BE]`, `[APP]`, `[DESIGN]`, `[TPM]`, `[QA]`
- Description structure: TL;DR → Spec link → What needs to be done → (optional sections)
- Acceptance Criteria goes in `customfield_18938` only, never in the description — **always populate this field on every ticket**
- On creation, pass `customfield_18938` in `additional_fields`; if the API rejects it (field not on screen), immediately follow up with an `editJiraIssue` call to set it
- If both attempts fail due to screen configuration, include the AC items in the response so the user can paste them manually
- Required fields on every story: Epic link, Assignee, Priority, Story Points, Team Type (`customfield_18836`)
- Default project: DCS

## Document Conventions

**IMPORTANT: Every reference in every document must be a clickable link.** This applies to
all deliverables — Google Docs, Claude artifacts, Confluence pages, and chat replies.
Never leave a bare identifier or name a source in plain text.

| Reference type | Must link to |
| --- | --- |
| Jira key (`DCS-1234`, `OMTU-7551`, `BAT-7936`) | `https://idtjira.atlassian.net/browse/<KEY>` |
| Confluence page named in text | its page URL |
| Figma file or frame | the node URL (including `?node-id=…`) |
| Amplitude chart or dashboard | its chart/dashboard URL |
| Google Doc or Sheet named in text | its document URL |
| A URL written as plain text | itself, as a real anchor |

**Why:** documents are reviewed by jumping straight from a reference into the source.
A bare key forces a manual copy-paste-search for every one, which makes a document with
dozens of references unusable.

**How to apply:**

- **Google Docs** — use `linkify_refs.py`. It auto-links Jira keys by pattern, links bare
  URLs, and links named sources from a phrase→URL map. It walks body paragraphs *and*
  table cells, skips runs that already carry a link (so it is idempotent), and applies
  everything in one pass since text-style requests do not shift indices.
  ```bash
  python linkify_refs.py <doc_id> [<doc_id> ...] [--map refs.json]
  ```
  New `create_*.py` generators should `from linkify_refs import linkify` and call it
  before sharing. `create_imtu_web_parity_doc.py` is the reference implementation.
  Add newly-cited Confluence pages to `LINK_MAP` so they link automatically next time.

- **Artifacts / HTML** — `<a href="…" target="_blank" rel="noopener">`. Split the source
  on tags before regex-replacing so attributes are never rewritten.

- **Chat replies** — markdown links.

## Key Conventions

- Google Doc requests sent in batches of 50 to avoid API rate limits
- Ensure internet connectivity for Google API calls
- Google credentials (`token.json`) auto-saved after first authorization; `credentials.json` required
