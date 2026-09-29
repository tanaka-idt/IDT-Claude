"""Build a Google Doc from simple content blocks by rendering one HTML file with
embedded images and letting Drive convert it.

Why HTML import: the IDT Workspace blocks "anyone with the link" sharing, so the
Docs API cannot fetch images from Drive, and pushing figures to the public GitHub
repo would publish internal data. Drive's HTML import embeds base64 images
directly, keeps tables, links and headings, and updates an existing Doc in place
(same file id, same URL).

Blocks (tuples):
  ("title", text)                ("meta", text)
  ("h1"|"h2"|"h3", text)         ("p", text)          ("small", text)
  ("bullets", [text, ...])       ("numbered", [text, ...])
  ("callout", tone, text)        tone: info | good | warn | risk | idt
  ("table", rows, opts)          rows[0] is the header; opts: widths, cell_bg, font_pt
  ("figure", path, width_px, caption)
  ("row", [(path, width_px, caption), ...])      side-by-side images
  ("pagebreak",)                 ("spacer",)
Inline markup in text: **bold**, *italic*, [label](https://url)
"""
import base64
import html
import io
import re

from PIL import Image

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#c3c2b7"
HEAD_BG = "#f0efec"
TONES = {
    "info": ("#eef4fc", "#9ec5f4"),
    "good": ("#eaf6ea", "#8fce8f"),
    "warn": ("#fdf4e1", "#f2c86b"),
    "risk": ("#fbeaea", "#e59a9a"),
    "idt": ("#eef4fc", "#2a78d6"),
}

_INLINE = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|\[([^\]]+)\]\((https?://[^)\s]+)\)")


def inline(text):
    out, pos = [], 0
    for m in _INLINE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f"<b>{inline(m.group(1))}</b>")
        elif m.group(2) is not None:
            out.append(f"<i>{inline(m.group(2))}</i>")
        else:
            out.append(f'<a href="{html.escape(m.group(4), quote=True)}">{html.escape(m.group(3))}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def img_data(path, width_px, scale=2.0):
    """Downscale to scale x display width and embed. Screens go JPEG, figures PNG."""
    im = Image.open(path)
    target = int(width_px * scale)
    if im.width > target:
        im = im.resize((target, round(im.height * target / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if path.lower().endswith((".jpg", ".jpeg")) or "/screens/" in path:
        im.convert("RGB").save(buf, "JPEG", quality=84, optimize=True)
        mime = "image/jpeg"
    else:
        im.save(buf, "PNG", optimize=True)
        mime = "image/png"
    h_px = round(width_px * im.height / im.width)
    return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}", h_px


def cap_html(caption):
    return (f'<p style="text-align:center;font-size:8.5pt;color:{INK2};margin:2pt 0 10pt 0">'
            f"<i>{inline(caption)}</i></p>") if caption else ""


def render(blocks, title):
    body = []
    for b in blocks:
        kind = b[0]
        if kind == "title":
            body.append(f'<p style="font-size:24pt;font-weight:bold;color:{INK};margin:0 0 6pt 0">{inline(b[1])}</p>')
        elif kind == "meta":
            body.append(f'<p style="font-size:9pt;color:{INK2};margin:0 0 10pt 0">{inline(b[1])}</p>')
        elif kind in ("h1", "h2", "h3"):
            body.append(f"<{kind}>{inline(b[1])}</{kind}>")
        elif kind == "p":
            body.append(f'<p style="margin:0 0 7pt 0">{inline(b[1])}</p>')
        elif kind == "small":
            body.append(f'<p style="font-size:8.5pt;color:{INK2};margin:0 0 7pt 0">{inline(b[1])}</p>')
        elif kind in ("bullets", "numbered"):
            tag = "ul" if kind == "bullets" else "ol"
            items = "".join(f'<li style="margin:0 0 3pt 0">{inline(t)}</li>' for t in b[1])
            body.append(f"<{tag}>{items}</{tag}>")
        elif kind == "callout":
            bg, line = TONES[b[1]]
            body.append(f'<table style="border-collapse:collapse;width:100%;margin:4pt 0 10pt 0"><tr>'
                        f'<td style="background:{bg};border:1px solid {line};border-left:4px solid {line};'
                        f'padding:8pt 10pt">{inline(b[2])}</td></tr></table><p></p>')
        elif kind == "table":
            rows = b[1]
            opts = b[2] if len(b) > 2 else {}
            fpt = opts.get("font_pt", 8.5)
            widths = opts.get("widths")
            cell_bg = opts.get("cell_bg", {})     # (r, c) -> (bg, fg)
            has_header = opts.get("header", True)
            trs = []
            for r, row in enumerate(rows):
                tds = []
                for c, val in enumerate(row):
                    is_head = has_header and r == 0
                    tag = "th" if is_head else "td"
                    st = [f"border:1px solid {GRID}", "padding:3pt 5pt", f"font-size:{fpt}pt", "vertical-align:top",
                          "text-align:left"]
                    if widths:
                        st.append(f"width:{widths[c]}%")
                    if is_head:
                        st.append(f"background:{HEAD_BG}")
                    elif not has_header and c == 0:
                        st.append(f"background:#f7f6f2")
                    if (r, c) in cell_bg:
                        bg, fg = cell_bg[(r, c)]
                        st += [f"background:{bg}", f"color:{fg}", "text-align:center"]
                    txt = inline(str(val)).replace("\n", "<br>")
                    if is_head or (not has_header and c == 0):
                        txt = f"<b>{txt}</b>"
                    tds.append(f'<{tag} style="{";".join(st)}">{txt}</{tag}>')
                trs.append("<tr>" + "".join(tds) + "</tr>")
            body.append(f'<table style="border-collapse:collapse;width:100%">{"".join(trs)}</table>'
                        f'<p style="margin:0 0 4pt 0"></p>')
        elif kind == "figure":
            _, path, w, caption = b
            src, h = img_data(path, w)
            body.append(f'<p style="text-align:center;margin:6pt 0 0 0"><img src="{src}" width="{w}" height="{h}"></p>'
                        + cap_html(caption))
        elif kind == "row":
            cells = []
            n = len(b[1])
            for path, w, caption in b[1]:
                src, h = img_data(path, w)
                cap = (f'<br><span style="font-size:8pt;color:{INK2}"><i>{inline(caption)}</i></span>'
                       if caption else "")
                cells.append(f'<td style="border:none;text-align:center;vertical-align:top;width:{100 // n}%;'
                             f'padding:2pt">'
                             f'<img src="{src}" width="{w}" height="{h}">{cap}</td>')
            body.append('<table style="border-collapse:collapse;border:none;width:100%;margin:6pt 0 8pt 0"><tr>'
                        + "".join(cells) + "</tr></table><p></p>")
        elif kind == "pagebreak":
            body.append('<p style="page-break-before:always"></p>')
        elif kind == "spacer":
            body.append("<p></p>")
        else:
            raise ValueError(kind)
    return (f'<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
            f"<style>body{{font-family:Arial;font-size:10pt;color:{INK}}}"
            f"h1{{font-size:17pt;margin:18pt 0 6pt 0}} h2{{font-size:13.5pt;margin:14pt 0 5pt 0}}"
            f"h3{{font-size:11pt;margin:10pt 0 4pt 0}}</style></head><body>"
            + "\n".join(body) + "</body></html>")


def publish(html_text, title, doc_id=None):
    """Create or replace a Google Doc from HTML. Returns the doc id."""
    from pathlib import Path
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload

    token = Path(__file__).resolve().parent.parent / "token.json"
    creds = Credentials.from_authorized_user_file(str(token))
    if not creds.valid:
        creds.refresh(Request())
        token.write_text(creds.to_json())
    drive = build("drive", "v3", credentials=creds)
    media = MediaIoBaseUpload(io.BytesIO(html_text.encode("utf-8")), mimetype="text/html", resumable=True)
    if doc_id:
        drive.files().update(fileId=doc_id, body={"name": title}, media_body=media, fields="id").execute()
    else:
        doc_id = drive.files().create(body={"name": title, "mimeType": "application/vnd.google-apps.document"},
                                      media_body=media, fields="id").execute()["id"]
    return doc_id, creds


def polish(docs, doc_id):
    """Page break before each Heading 1 (except the first) and keep headings with the next paragraph.
    Drive's HTML import ignores CSS page breaks, so this is set on the paragraphs afterwards."""
    doc = docs.documents().get(documentId=doc_id).execute()
    reqs, seen_h1 = [], False
    for el in doc["body"]["content"]:
        p = el.get("paragraph")
        if not p:
            continue
        style = p.get("paragraphStyle", {}).get("namedStyleType", "")
        rng = {"startIndex": el["startIndex"], "endIndex": el["endIndex"]}
        if style == "HEADING_1":
            ps = {"keepWithNext": True}
            fields = "keepWithNext"
            if seen_h1:
                ps["pageBreakBefore"] = True
                fields += ",pageBreakBefore"
            seen_h1 = True
            reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": ps, "fields": fields}})
        elif style in ("HEADING_2", "HEADING_3"):
            reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": {"keepWithNext": True},
                                                  "fields": "keepWithNext"}})
    for i in range(0, len(reqs), 50):
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": reqs[i:i + 50]}).execute()
    return len(reqs)
