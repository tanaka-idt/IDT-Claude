# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IDT product-management workspace. Holds roadmaps, competitor analyses, and product specs (Markdown) alongside Python scripts that generate formatted Google Docs (with embedded charts, diagrams, and screen designs) for IMTU, Boss Money, eGift, eSIM, and crypto-payment initiatives.

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
6. Run a `create_*.py` script, and a browser tab opens for authorization

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
- **No placeholders anywhere in a ticket.** Never write `TBD`, `TBC`, `N/A`, `[link]` or an
  empty bracket, and never on a Spec, Confluence or Figma line. If the link or value does
  not exist yet, leave the field empty and omit the line entirely.
  **Why:** a `TBD` reads as a filled-in reference at a glance, so a missing spec or design
  link stops being visible in review. A blank field is honest and easy to spot.
- Acceptance Criteria goes in its dedicated field (ADF format), never in the description. **Always populate it on every ticket.**
- Required fields on every story: Epic link, Assignee, Priority, Story Points, Team Type
  (Story Points per the defaults table below, which overrides this for some roles)
- Default project: DCS
- **Whenever you create tickets that are related to each other, link them.** A shared
  epic parent is not a link, and neither is naming the sibling key in the description.

**Defaults by role.** Apply these without asking, unless the request names someone else:

| Role | Assignee | Story Points |
| --- | --- | --- |
| `[DESIGN]` | Viktoryia Shmidt (`712020:f413ae5c-bfd0-4674-a838-7fc82aaeb484`) | always `0` |
| `[TPM]` / PM | (per request) | always `0` |
| `[BE]` | (per request) | **leave empty**, never estimate |
| `[APP]` | (per request) | **leave empty**, never estimate |
| any other role | (per request) | estimate as usual |

For Design and PM/TPM, set Story Points explicitly to `0` rather than leaving it empty.
For BE and App, omit `customfield_11666` entirely: the team estimates those in grooming,
so a guessed number is worse than a blank field.

**Field IDs differ by issue type. Using the wrong one fails with "not on the appropriate
screen".** Verified against DCS create metadata 2026-08-26:

| Field | Story (`12257`) | Task (`12258`) |
| --- | --- | --- |
| Acceptance Criteria | `customfield_18937` | `customfield_18938` |
| Team Type | `customfield_18836` | `customfield_18936` |
| Team Type option IDs | App `22229`, BE `22230`, Design `22231`, PM/TPM `22232`, QA `22233` | App `22301`, BE `22302`, Design `22303`, PM/TPM `22304`, QA `22305` |

Both fields are **required** on both issue types. Pass Team Type as `{"id": "<id>"}`.
Matching by value works only when the label is exact, so `{"value": "TPM"}` fails
(the label is "PM/TPM"). When unsure, read `getJiraIssueTypeMetaWithFields` for the
issue type and grep for the field name rather than guessing.

- **Bugs** (`12259`) have **no** Acceptance Criteria field, and both custom fields are
  rejected. Use the description's "Expected result" section as the pass/fail criteria.
  Bug creation also requires Severity (`customfield_11403`), Testing Stage
  (`customfield_18035`), and Components (`customfield_13266`, a string array, not the
  built-in `components`).
- AC is often not on the *create* screen. If creation rejects it, create first and then
  set it with `editJiraIssue`, which succeeds where the create failed.
- Editing an issue's `description` via `editJiraIssue` can silently clear the `assignee`.
  Re-set the assignee after any description edit; AC-only edits are safe.
- Sprint is `customfield_10571` (DCS board `2057`), set by numeric sprint id. Find it with
  `project = DCS AND Sprint = "DCS Sprint <N>"`. Sprint ids are **not** sequential with
  sprint numbers, so always look the id up rather than inferring it.
- Story Points is `customfield_11666` ("Story point estimate"), a plain number. Epic link on
  DCS is the `parent` field (DCS is a team-managed project), not `customfield_*`.
- If every attempt fails due to screen configuration, include the AC items in the response
  so they can be pasted manually.
- **An `[APP]` ticket created from a `[DESIGN]` ticket copies the design fields across.**
  Read **Design Needed?** (`customfield_19305`, select: Yes `23022`, No `23023`, N/A `23024`)
  and **Figma Link** (`customfield_19270`, plain URL string) off the design ticket and set the
  same values on the app ticket. Neither is on the create screen, so set them with
  `editJiraIssue` after creation.
  **Why:** the app ticket is the one developers open. Left blank, the Figma frame lives only
  on a sibling ticket and the dev has to hunt for it, and board filters on Design Needed? miss
  the app work.
- **Issue links** are created with `createIssueLink` after the tickets exist. Pick the type
  that states the real relationship, and link out to existing tickets the new work depends
  on or supersedes, not only the ones created in the same batch. Run `getIssueLinkTypes`
  when unsure; DCS also has Supersede, Duplicated, Similar, and Due to ("is caused by").

  | Relationship | Type | Direction |
  | --- | --- | --- |
  | One must ship first, e.g. a BE flag before the APP story reading it | `Blocks` | `inwardIssue` blocks, `outwardIssue` is blocked |
  | Siblings with no ordering | `Relates` | either way |
  | New ticket replaces an old one | `Supersede` | `outwardIssue` supersedes `inwardIssue` |

  **Why:** the linked-issues panel is how the team sees dependencies on the board and in
  sprint planning. A key buried in a description does not appear there, so an unlinked
  dependency gets picked up in the wrong order.

## Sprint Goals

When asked for sprint goals, pull the sprint's real contents from Jira first. Never draft from
memory, from the epic names, or from the previous sprint's list.

**Gathering the data.** Query `project = DCS AND Sprint = "DCS Sprint <N>"` for `summary`,
`status`, `issuetype`, `parent` and `customfield_18836` (Team Type), then group by epic. Look the
sprint id up rather than inferring it. The response is large (Sprint 77 held 122 tickets) and
will overflow the tool result, so extract a compact table with `jq` instead of reading raw JSON.
Pull the previous sprint's ticket list too: comparing it against the goals actually written for
that sprint is the best calibration available.

**Format.** Numbered, one line each, role tag in parentheses at the end. Sub-items use `N.1)`,
and only where a goal has separable parts.

```
1) Insurance modular component: finalize early-eligibility check for release (APP)
2) IMTU Subscriptions V2: ship the payment bar (APP):
2.1) Move toggle into payment bar
5) Apple Pay / Google Pay: implement one-time and subscription flows (BE)
10) Spike - Configurable Exclusion of Offers from Subscription Eligibility (Country / IMTU Type) (BE)
```

Role tags: `APP`, `BE`, `APP + BE`, `App+QA`, `BE + App + Design`, `DESIGN`, `QA`, `PM/TPM`,
`Strategy`, `Config`. Outcome verbs: Ship, Deliver, Finalize, Implement, Advance, Define, Launch,
Investigate, Turn ON. Terse PM English, short lines.

**What earns a goal**

| Rule | Detail |
| --- | --- |
| Initiative level | A goal maps to an epic or a coherent slice of one, never to a single ticket |
| Spikes get their own line | Format `Spike - <ticket title> (BE)`. A To Do spike still counts: its deliverable is a decision, so it closes inside the sprint whatever happens downstream |
| No cap on the count | 6 to 11 is normal. Never reject a candidate because the list is "full" |
| Verb must match status | Ship / Finalize / Launch needs backing tickets at In Progress or beyond. A To Do stack gets Deliver / Implement / Define |

**What never earns a goal:** `QA - DCS-xxxx` mirror tickets (they shadow a dev ticket, they are
not independent work), colour swap work, eSIM TPM taxonomy chores, RAF event-doc chores, small
bugs, and any initiative with no committed build behind it this sprint (a spec sign-off plus a
contract spike is not enough).

**Sub-items name separable new behaviour, not backing tickets.** Defects against the feature and
enabling chores sit under the goal unnamed, even when they gate the release. A goal with a single
sub-item is fine.
**Why:** the sub-list says what the goal means. An inventory of the epic buries the actual
commitment and makes the list unreadable.

**Always hand over a short "deliberately not a goal" list** with the goals, naming the significant
work left off and the exact line to use if it should go in after all. That is what makes the
scoping calls visible instead of silent, and it is where missing goals get caught.

## Document Conventions

**IMPORTANT: Do not use em dashes (—).** This applies to everything produced here: Google
Docs, Jira tickets, Confluence pages, HTML and artifacts, Python docstrings and comments,
commit messages, and chat replies. Use a comma, a colon, parentheses, or a full stop
instead, or split the sentence in two. Only reach for an em dash when nothing else will do,
which is rare. En dashes in numeric ranges (26-31 Aug) are fine as hyphens.

**IMPORTANT: Every reference in every document must be a clickable link.** This applies to
all deliverables: Google Docs, Claude artifacts, Confluence pages, and chat replies.
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

- **Google Docs**: use `linkify_refs.py`. It auto-links Jira keys by pattern, links bare
  URLs, and links named sources from a phrase→URL map. It walks body paragraphs *and*
  table cells, skips runs that already carry a link (so it is idempotent), and applies
  everything in one pass since text-style requests do not shift indices.
  ```bash
  python linkify_refs.py <doc_id> [<doc_id> ...] [--map refs.json]
  ```
  New `create_*.py` generators should `from linkify_refs import linkify` and call it
  before sharing. `create_imtu_web_parity_doc.py` is the reference implementation.
  Add newly-cited Confluence pages to `LINK_MAP` so they link automatically next time.

- **Artifacts / HTML**: `<a href="…" target="_blank" rel="noopener">`. Split the source
  on tags before regex-replacing so attributes are never rewritten.

- **Chat replies**: markdown links.

## Key Conventions

- Google Doc requests sent in batches of 50 to avoid API rate limits
- Ensure internet connectivity for Google API calls
- Google credentials (`token.json`) auto-saved after first authorization; `credentials.json` required
