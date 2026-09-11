#!/usr/bin/env python3
"""
Builds the self-contained HTML report for the Felix Pago WhatsApp top-up teardown.

Reads the same content blocks as create_felix_recarga_evidence_doc.py
(felix_recarga_evidence_content.py) so the HTML artifact and the Google Doc never
drift. Images are embedded as data URIs so the file works as a local page and as a
Claude artifact (the artifact CSP blocks external images).

Output: Felix_WhatsApp_TopUp_Real_Flow.html
"""

import base64
import html
import io
import re
from pathlib import Path

from PIL import Image

from felix_recarga_evidence_content import (
    TITLE, SUBTITLE, META_LINE, BLOCKS, TABLES, IMAGES, IMAGE_CAPTIONS, EXTRA_LINKS,
    GRADE_WORDS,
)

BASE = Path(__file__).parent
OUT = BASE / "Felix_WhatsApp_TopUp_Real_Flow.html"
IMG_DIR = BASE / "felix_evidence"

JIRA = re.compile(r"\b([A-Z]{2,8}-\d+)\b")
URL = re.compile(r"(https?://[^\s<>\"')\]]+)")


def data_uri(fname, max_w=900, quality=82):
    p = IMG_DIR / fname
    im = Image.open(p).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii"), im.size


def linkify(text):
    """Escape, then link bare URLs, Jira keys and named sources. Splits on existing
    tags so attributes are never rewritten."""
    esc = html.escape(text, quote=False)
    # named sources first (longest first) so a phrase inside a URL is not double-linked
    for phrase in sorted(EXTRA_LINKS, key=len, reverse=True):
        url = EXTRA_LINKS[phrase]
        ph = html.escape(phrase, quote=False)
        if ph in esc and url not in esc:
            esc = esc.replace(ph, f'<a href="{url}" target="_blank" rel="noopener">{ph}</a>', 1)
    parts = re.split(r"(<a [^>]*>.*?</a>)", esc)
    out = []
    for part in parts:
        if part.startswith("<a "):
            out.append(part)
            continue
        part = URL.sub(lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>', part)
        part = JIRA.sub(lambda m: f'<a href="https://idtjira.atlassian.net/browse/{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>', part)
        out.append(part)
    return "".join(out)


def lead_bold(text):
    """'Lead  ::  rest' -> <strong>Lead</strong> rest (same convention as the doc generator)."""
    if "  ::  " in text:
        lead, rest = text.split("  ::  ", 1)
        return f"<strong>{linkify(lead)}</strong> {linkify(rest)}"
    return linkify(text)


def grade_chip(text):
    """Wrap known evidence-grade words in a chip."""
    for word, cls in GRADE_WORDS.items():
        if text.strip() == word:
            return f'<span class="chip chip-{cls}">{html.escape(word)}</span>'
    return None


def render_table(rows):
    head, body = rows[0], rows[1:]
    h = "".join(f"<th>{linkify(c)}</th>" for c in head)
    b = []
    for r in body:
        cells = []
        for i, c in enumerate(r):
            chip = grade_chip(c)
            cells.append(f"<td>{chip if chip else linkify(c)}</td>")
        b.append("<tr>" + "".join(cells) + "</tr>")
    return f'<div class="tablewrap"><table><thead><tr>{h}</tr></thead><tbody>{"".join(b)}</tbody></table></div>'


def render():
    tables = dict(TABLES)
    images = {m: (f, w, nw, nh) for m, f, w, nw, nh in IMAGES}
    body = []
    toc = []
    list_open = None
    fig_row = []
    sec_id = 0

    def close_list():
        nonlocal list_open
        if list_open:
            body.append(f"</{list_open}>")
            list_open = None

    def flush_figs():
        nonlocal fig_row
        if fig_row:
            n = len(fig_row)
            body.append(f'<div class="figrow figrow-{min(n,4)}">' + "".join(fig_row) + "</div>")
            fig_row = []

    for kind, text in BLOCKS:
        if kind != "image":
            flush_figs()
        if kind not in ("b", "n"):
            close_list()
        if kind == "h1":
            continue  # rendered in the hero
        if kind == "h2":
            sec_id += 1
            sid = f"s{sec_id}"
            toc.append((sid, text))
            body.append(f'<h2 id="{sid}">{linkify(text)}</h2>')
        elif kind == "h3":
            body.append(f"<h3>{linkify(text)}</h3>")
        elif kind == "h4":
            body.append(f"<h4>{linkify(text)}</h4>")
        elif kind == "p":
            body.append(f"<p>{lead_bold(text)}</p>")
        elif kind == "b":
            if list_open != "ul":
                close_list(); body.append("<ul>"); list_open = "ul"
            body.append(f"<li>{lead_bold(text)}</li>")
        elif kind == "n":
            if list_open != "ol":
                close_list(); body.append("<ol>"); list_open = "ol"
            body.append(f"<li>{lead_bold(text)}</li>")
        elif kind == "quote":
            # verbatim bot / user copy. "Bot: ..." and "User: ..." prefixes pick the bubble side.
            side = "bot"
            t = text
            if t.startswith("User:"):
                side = "user"; t = t[5:].strip()
            elif t.startswith("Bot:"):
                t = t[4:].strip()
            elif t.startswith("Web:"):
                side = "web"; t = t[4:].strip()
            body.append(f'<div class="bubble bubble-{side}">{html.escape(t)}</div>')
        elif kind == "cap":
            body.append(f'<p class="cap">{linkify(text)}</p>')
        elif kind == "table":
            body.append(render_table(tables[text]))
        elif kind == "image":
            fname, w, nw, nh = images[text]
            uri, size = data_uri(fname)
            cap = IMAGE_CAPTIONS.get(text, "")
            fig_row.append(
                f'<figure><img src="{uri}" alt="{html.escape(cap or fname)}" width="{size[0]}" height="{size[1]}" loading="lazy">'
                + (f"<figcaption>{linkify(cap)}</figcaption>" if cap else "") + "</figure>")
    flush_figs(); close_list()

    toc_html = "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t in toc)
    return f"""<title>{html.escape(TITLE)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#f5f7f4; --ink:#10211d; --ink-2:#3d4a45; --ink-3:#6b7771; --rule:#d8dfda; --surface:#ffffff; --surface-2:#eef2ee;
  --accent:#1f8a5b; --accent-ink:#0f4d33; --accent-soft:#e3f2ea; --marker:#22d3c5;
  --real:#1f8a5b; --real-bg:#e3f2ea; --video:#2b6cb0; --video-bg:#e6eef9; --mock:#a5730a; --mock-bg:#fbf0d9; --doc:#6f746f; --doc-bg:#eeefec; --risk:#b03a3a; --risk-bg:#fbe6e6;
  --bubble-bot:#ffffff; --bubble-user:#dcf8c6; --bubble-web:#f1f3f5; --bubble-ink:#111b17; --link:#175f9e;
  --shadow:0 1px 2px rgba(16,33,29,.08), 0 8px 24px rgba(16,33,29,.06);
}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{
  --paper:#0e1a17; --ink:#e6ece8; --ink-2:#b6c2bb; --ink-3:#8b978f; --rule:#243530; --surface:#15241f; --surface-2:#1b2c26;
  --accent:#3fbf86; --accent-ink:#9fe3c2; --accent-soft:#16342a; --marker:#22d3c5;
  --real:#3fbf86; --real-bg:#16342a; --video:#6ea3e0; --video-bg:#1a2a3d; --mock:#d9a441; --mock-bg:#3a2d12; --doc:#9aa39d; --doc-bg:#232e29; --risk:#e07373; --risk-bg:#3d1c1c;
  --bubble-bot:#1f2c27; --bubble-user:#1f3a2a; --bubble-web:#1c2622; --bubble-ink:#e6ece8; --link:#8fb8ea;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
}} }}
:root[data-theme="dark"]{{
  --paper:#0e1a17; --ink:#e6ece8; --ink-2:#b6c2bb; --ink-3:#8b978f; --rule:#243530; --surface:#15241f; --surface-2:#1b2c26;
  --accent:#3fbf86; --accent-ink:#9fe3c2; --accent-soft:#16342a; --marker:#22d3c5;
  --real:#3fbf86; --real-bg:#16342a; --video:#6ea3e0; --video-bg:#1a2a3d; --mock:#d9a441; --mock-bg:#3a2d12; --doc:#9aa39d; --doc-bg:#232e29; --risk:#e07373; --risk-bg:#3d1c1c;
  --bubble-bot:#1f2c27; --bubble-user:#1f3a2a; --bubble-web:#1c2622; --bubble-ink:#e6ece8; --link:#8fb8ea;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Source Sans 3",-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}}
a{{color:var(--link);text-decoration-thickness:1px;text-underline-offset:2px}}
.hero{{background:var(--ink);color:#e6ece8;padding:56px 24px 40px}}
:root[data-theme="dark"] .hero,.hero{{background:#10211d}}
.hero .in{{max-width:1080px;margin:0 auto}}
.eyebrow{{font:600 12px/1 "Source Sans 3",sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#22d3c5;margin:0 0 18px}}
.hero h1{{font-family:"Bricolage Grotesque","Source Sans 3",sans-serif;font-weight:800;font-size:clamp(30px,4.6vw,52px);line-height:1.02;letter-spacing:-.02em;margin:0 0 16px;max-width:900px;text-wrap:balance;color:#f4f8f5}}
.hero p.sub{{font-size:19px;line-height:1.45;max-width:760px;color:#c9d6cf;margin:0 0 22px}}
.hero .meta{{font-size:14px;color:#9fb0a7;display:flex;flex-wrap:wrap;gap:8px 22px}}
.hero .meta a{{color:#22d3c5}}
nav.toc{{position:sticky;top:0;z-index:5;background:var(--surface);border-bottom:1px solid var(--rule);overflow-x:auto}}
nav.toc .in{{max-width:1080px;margin:0 auto;display:flex;gap:4px;padding:6px 16px;white-space:nowrap}}
nav.toc a{{font:600 13px/1 "Source Sans 3",sans-serif;color:var(--ink-2);text-decoration:none;padding:9px 10px;border-radius:6px}}
nav.toc a:hover,nav.toc a:focus-visible{{background:var(--surface-2);color:var(--ink);outline:none}}
main{{max-width:1080px;margin:0 auto;padding:16px 24px 80px}}
main > *{{max-width:760px}}
main > .figrow, main > .tablewrap{{max-width:none}}
h2{{font-family:"Bricolage Grotesque","Source Sans 3",sans-serif;font-weight:800;font-size:30px;line-height:1.12;letter-spacing:-.015em;margin:64px 0 14px;text-wrap:balance;color:var(--ink)}}
h2::before{{content:"";display:block;width:44px;height:3px;background:var(--marker);margin-bottom:18px;border-radius:2px}}
h3{{font-family:"Bricolage Grotesque","Source Sans 3",sans-serif;font-weight:700;font-size:21px;line-height:1.25;margin:34px 0 8px;text-wrap:balance}}
h4{{font-weight:700;font-size:17px;margin:22px 0 6px}}
p{{margin:0 0 14px}}
ul,ol{{margin:0 0 16px;padding-left:22px}}
li{{margin:0 0 8px}}
strong{{font-weight:700;color:var(--ink)}}
p.cap{{font-size:14px;color:var(--ink-3);margin:-4px 0 22px;line-height:1.45}}
.bubble{{font:14px/1.5 "JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;color:var(--bubble-ink);background:var(--bubble-bot);border:1px solid var(--rule);border-radius:12px 12px 12px 4px;padding:10px 14px;margin:0 60px 8px 0;box-shadow:var(--shadow)}}
.bubble-user{{background:var(--bubble-user);border-radius:12px 12px 4px 12px;margin:0 0 8px 60px}}
.bubble-web{{background:var(--bubble-web);border-radius:8px;margin:0 0 8px 0;border-style:dashed}}
.bubble + p, .bubble + h3{{margin-top:16px}}
.figrow{{display:grid;gap:18px;margin:18px 0 26px;align-items:start}}
.figrow-1{{grid-template-columns:minmax(0,1fr)}}
.figrow-2{{grid-template-columns:repeat(2,minmax(0,1fr))}}
.figrow-3{{grid-template-columns:repeat(3,minmax(0,1fr))}}
.figrow-4{{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:860px){{.figrow-3,.figrow-4{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media (max-width:520px){{.figrow-2,.figrow-3,.figrow-4{{grid-template-columns:minmax(0,1fr)}}}}
figure{{margin:0;background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:10px;box-shadow:var(--shadow)}}
figure img{{display:block;width:100%;height:auto;border-radius:6px;background:#10211d}}
figcaption{{font-size:13.5px;line-height:1.45;color:var(--ink-2);padding:10px 4px 2px}}
.tablewrap{{overflow-x:auto;margin:16px 0 26px;border:1px solid var(--rule);border-radius:10px;background:var(--surface)}}
table{{border-collapse:collapse;width:100%;font-size:14.5px;line-height:1.45}}
th,td{{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--rule)}}
th{{font-weight:700;background:var(--surface-2);position:sticky;top:0}}
tbody tr:last-child td{{border-bottom:0}}
td:first-child{{font-weight:600}}
.chip{{display:inline-block;font:600 12px/1 "Source Sans 3",sans-serif;letter-spacing:.02em;padding:5px 9px;border-radius:999px;border:1px solid;white-space:nowrap}}
.chip-real{{color:var(--real);background:var(--real-bg);border-color:var(--real)}}
.chip-video{{color:var(--video);background:var(--video-bg);border-color:var(--video)}}
.chip-mock{{color:var(--mock);background:var(--mock-bg);border-color:var(--mock)}}
.chip-doc{{color:var(--doc);background:var(--doc-bg);border-color:var(--doc)}}
.chip-risk{{color:var(--risk);background:var(--risk-bg);border-color:var(--risk)}}
footer{{max-width:1080px;margin:0 auto;padding:24px;border-top:1px solid var(--rule);font-size:13px;color:var(--ink-3)}}
:focus-visible{{outline:2px solid var(--marker);outline-offset:2px}}
@media (prefers-reduced-motion: reduce){{*{{scroll-behavior:auto}}}}
html{{scroll-behavior:smooth}}
</style>
<header class="hero"><div class="in">
<p class="eyebrow">Competitive teardown · IMTU · WhatsApp channel (A8)</p>
<h1>{html.escape(TITLE)}</h1>
<p class="sub">{linkify(SUBTITLE)}</p>
<div class="meta">{linkify(META_LINE)}</div>
</div></header>
<nav class="toc"><div class="in">{toc_html}</div></nav>
<main>
{chr(10).join(body)}
</main>
<footer>Prepared by João Tanaka (IDT, DCS product) with Claude. Every screenshot is Felix's own published material or a frame from a public video; recipient numbers are redacted. Felix, WhatsApp and carrier marks belong to their owners and appear here for internal benchmarking only.</footer>
"""


def main():
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
