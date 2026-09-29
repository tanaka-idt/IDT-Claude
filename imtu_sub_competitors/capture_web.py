"""Minimal Chrome DevTools Protocol driver for capturing public web flows.

Usage: python3 cdp.py steps.json
steps.json = {"device": "mobile"|"desktop", "steps": [...]} where each step is one of
  {"goto": url, "wait": secs}
  {"wait": secs}
  {"click_text": "Text", "tag": "button|a|*", "nth": 0}
  {"click": "css selector"}
  {"type": ["css selector", "text"]}
  {"eval": "js expression"}                 (result printed)
  {"cookies": "reject"}                     (tries to reject non-essential cookies)
  {"shot": "file.png", "full": false}       (viewport or full-page PNG)
  {"scroll": pixels}
  {"text": "file.txt"}                      (dump visible text)
One Chrome process per run; state persists across steps of a run.
"""
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import websockets

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHOTS = os.environ.get("CAPTURE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures"))
os.makedirs(SHOTS, exist_ok=True)
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1")
DESKTOP_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

REJECT_JS = r"""
(() => {
  const ids = ['#onetrust-reject-all-handler', '#CybotCookiebotDialogBodyButtonDecline',
               '#didomi-notice-disagree-button', '[data-testid="uc-deny-all-button"]',
               'button[aria-label*="Reject"]', 'button[aria-label*="Decline"]'];
  for (const s of ids) { const el = document.querySelector(s); if (el) { el.click(); return 'clicked ' + s; } }
  const words = ['reject all', 'reject', 'decline all', 'decline', 'only necessary', 'necessary only',
                 'use necessary', 'essential only', 'deny', 'rechazar', 'recusar', 'rejeitar'];
  const els = [...document.querySelectorAll('button, a, [role=button]')];
  for (const w of words) {
    const el = els.find(e => (e.innerText || '').trim().toLowerCase() === w ||
                             (e.innerText || '').trim().toLowerCase().startsWith(w));
    if (el) { el.click(); return 'clicked text ' + w; }
  }
  // usercentrics shadow root
  const uc = document.querySelector('#usercentrics-root');
  if (uc && uc.shadowRoot) {
    const b = uc.shadowRoot.querySelector('[data-testid="uc-deny-all-button"]');
    if (b) { b.click(); return 'clicked usercentrics deny'; }
  }
  const pc = document.querySelector('#onetrust-pc-btn-handler');
  if (pc) { pc.click(); return 'opened onetrust settings'; }
  const settings = els.find(e => /cookie(s)? settings|manage (cookies|preferences)|customi[sz]e/i.test((e.innerText||'').trim()));
  if (settings) { settings.click(); return 'opened settings: ' + (settings.innerText||'').trim().slice(0,40); }
  return 'no banner button found';
})()
"""


class CDP:
    def __init__(self, ws):
        self.ws = ws
        self.n = 0
        self.events = []

    async def call(self, method, params=None, timeout=60):
        self.n += 1
        mid = self.n
        await self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        end = time.time() + timeout
        while time.time() < end:
            msg = json.loads(await asyncio.wait_for(self.ws.recv(), timeout=timeout))
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
            self.events.append(msg)
        raise TimeoutError(method)

    async def eval(self, expr):
        r = await self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True,
                                                 "awaitPromise": True})
        return r.get("result", {}).get("value")


async def run(spec):
    port = 9333
    profile = tempfile.mkdtemp(prefix="cdp-profile-")
    mobile = spec.get("device", "mobile") == "mobile"
    w, h = (390, 844) if mobile else (1280, 900)
    proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={port}",
                             f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
                             "--hide-scrollbars", f"--window-size={w},{h}",
                             f"--lang={spec.get('lang', 'en-US')}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                page = next(t for t in tabs if t.get("type") == "page")
                break
            except Exception:
                time.sleep(0.2)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=200_000_000) as ws:
            c = CDP(ws)
            await c.call("Page.enable")
            await c.call("Runtime.enable")
            await c.call("Network.enable")
            await c.call("Network.setUserAgentOverride", {
                "userAgent": IPHONE_UA if mobile else DESKTOP_UA,
                "acceptLanguage": spec.get("accept_language", "en-US,en;q=0.9")})
            await c.call("Emulation.setDeviceMetricsOverride", {
                "width": w, "height": h, "deviceScaleFactor": 3 if mobile else 2, "mobile": mobile})
            if mobile:
                await c.call("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
            await c.call("Emulation.setEmulatedMedia", {"features": [
                {"name": "prefers-color-scheme", "value": spec.get("scheme", "light")}]})
            if spec.get("width"):
                w, h = spec["width"], spec.get("height", h)
                await c.call("Emulation.setDeviceMetricsOverride", {
                    "width": w, "height": h, "deviceScaleFactor": spec.get("dpr", 2), "mobile": mobile})
            if spec.get("timezone"):
                await c.call("Emulation.setTimezoneOverride", {"timezoneId": spec["timezone"]})
            for st in spec["steps"]:
                if "goto" in st:
                    await c.call("Page.navigate", {"url": st["goto"]})
                    await asyncio.sleep(st.get("wait", 6))
                    print("goto", st["goto"], "->", await c.eval("location.href"))
                elif "cookies" in st:
                    for _ in range(3):
                        r = await c.eval(REJECT_JS)
                        print("cookies:", r)
                        await asyncio.sleep(1.5)
                        if not r or r.startswith("clicked") or r.startswith("no banner"):
                            break
                    # OneTrust preference centre: reject all / confirm with defaults off
                    r2 = await c.eval("""(() => { const b = document.querySelector('.ot-pc-refuse-all-handler, #onetrust-pc-sdk .ot-pc-refuse-all-handler');
                        if (b) { b.click(); return 'pc reject all'; }
                        const s = document.querySelector('.save-preference-btn-handler');
                        if (s) { s.click(); return 'pc save (defaults off)'; } return 'no pc'; })()""")
                    print("cookies pc:", r2)
                    await asyncio.sleep(1.5)
                elif "click_text" in st:
                    tag = st.get("tag", "*")
                    js = f"""(() => {{
                      const want = {json.dumps(st['click_text'].lower())};
                      const els = [...document.querySelectorAll({json.dumps(tag)})].filter(e =>
                        e.offsetParent !== null && (e.innerText || '').trim().toLowerCase().includes(want));
                      els.sort((a, b) => (a.innerText || '').length - (b.innerText || '').length);
                      const el = els[{st.get('nth', 0)}];
                      if (!el) return 'NOT FOUND';
                      el.scrollIntoView({{block: 'center'}}); el.click();
                      return 'clicked: ' + (el.innerText || '').trim().slice(0, 60);
                    }})()"""
                    print("click_text", st["click_text"], "->", await c.eval(js))
                    await asyncio.sleep(st.get("wait", 3))
                elif "click" in st:
                    js = f"""(() => {{ const el = document.querySelector({json.dumps(st['click'])});
                      if (!el) return 'NOT FOUND'; el.scrollIntoView({{block:'center'}}); el.click();
                      return 'clicked'; }})()"""
                    print("click", st["click"], "->", await c.eval(js))
                    await asyncio.sleep(st.get("wait", 3))
                elif "type" in st:
                    sel, text = st["type"]
                    js = f"""(() => {{ const el = document.querySelector({json.dumps(sel)});
                      if (!el) return 'NOT FOUND'; el.focus(); return 'focused'; }})()"""
                    print("type focus", sel, "->", await c.eval(js))
                    await c.call("Input.insertText", {"text": text})
                    await asyncio.sleep(st.get("wait", 2))
                elif "eval" in st:
                    print("eval ->", str(await c.eval(st["eval"]))[:3000])
                    await asyncio.sleep(st.get("wait", 0.5))
                elif "hide" in st:
                    js = "(() => { let n=0; for (const sel of %s) { document.querySelectorAll(sel).forEach(e => { e.style.setProperty('display','none','important'); n++; }); } document.documentElement.style.overflow='auto'; document.body.style.overflow='auto'; return n; })()" % json.dumps(st["hide"])
                    print("hide ->", await c.eval(js))
                    await asyncio.sleep(0.5)
                elif "blur" in st:
                    js = "(() => { let n=0; for (const sel of %s) { document.querySelectorAll(sel).forEach(e => { e.style.setProperty('filter','blur(7px)','important'); n++; }); } return n; })()" % json.dumps(st["blur"])
                    print("blur ->", await c.eval(js))
                elif "links" in st:
                    js = "JSON.stringify([...document.querySelectorAll('a[href]')].map(a => [(a.innerText||'').trim().slice(0,60), a.href]).filter(x => new RegExp(%s,'i').test(x[0]+' '+x[1])))" % json.dumps(st["links"])
                    for t, h in json.loads(await c.eval(js) or "[]"):
                        print("  link:", t.replace("\n"," "), "|", h)
                elif "scroll" in st:
                    await c.eval(f"window.scrollBy(0, {int(st['scroll'])})")
                    await asyncio.sleep(st.get("wait", 1.5))
                elif "shot" in st:
                    params = {"format": "png"}
                    if st.get("clip"):
                        x, y, cw, ch = st["clip"]
                        params.update({"captureBeyondViewport": True,
                                       "clip": {"x": x, "y": y, "width": cw, "height": ch, "scale": 1}})
                    if st.get("full"):
                        dims = await c.eval("JSON.stringify([document.documentElement.scrollWidth, "
                                            "Math.min(document.documentElement.scrollHeight, 12000)])")
                        fw, fh = json.loads(dims)
                        params.update({"captureBeyondViewport": True,
                                       "clip": {"x": 0, "y": 0, "width": w, "height": fh, "scale": 1}})
                    r = await c.call("Page.captureScreenshot", params)
                    out = os.path.join(SHOTS, st["shot"])
                    with open(out, "wb") as f:
                        f.write(base64.b64decode(r["data"]))
                    print("shot", out)
                elif "shots_of" in st:
                    js = ("JSON.stringify([...document.querySelectorAll(%s)].map(e=>{const r=e.getBoundingClientRect();"
                          "return [r.x+scrollX, r.y+scrollY, r.width, r.height]}).filter(a=>a[3]>=%d && a[2]>=%d))"
                          % (json.dumps(st["shots_of"]), st.get("min_h", 400), st.get("min_w", 150)))
                    rects = json.loads(await c.eval(js) or "[]")
                    seen = []
                    for (x, y, cw, ch) in rects:
                        if any(abs(x - a) < 3 and abs(y - b) < 3 for a, b in seen):
                            continue
                        seen.append((x, y))
                    for i, (x, y) in enumerate(seen[:st.get("max", 12)]):
                        cw, ch = next((r[2], r[3]) for r in rects if abs(r[0] - x) < 3 and abs(r[1] - y) < 3)
                        r = await c.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True,
                                         "clip": {"x": x, "y": y, "width": cw, "height": ch, "scale": 1}})
                        out = os.path.join(SHOTS, f"{st['prefix']}_{i + 1}.png")
                        with open(out, "wb") as f:
                            f.write(base64.b64decode(r["data"]))
                    print("shots_of", st["prefix"], len(seen), "images")
                elif "hide_text" in st:
                    js = """(() => { const q = %s.toLowerCase(); const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n, hid = 0;
                      while ((n = w.nextNode())) { if (!n.textContent.toLowerCase().includes(q)) continue;
                        let el = n.parentElement; let target = null;
                        while (el && el !== document.body) { const cs = getComputedStyle(el);
                          if (cs.position === 'fixed' || cs.position === 'sticky') target = el; el = el.parentElement; }
                        if (target) { target.style.setProperty('display','none','important'); hid++; } }
                      document.querySelectorAll('*').forEach(e => { const cs = getComputedStyle(e);
                        if (cs.position === 'fixed' && parseFloat(cs.opacity) > 0 && e.getBoundingClientRect().height > innerHeight*0.8
                            && e.getBoundingClientRect().width > innerWidth*0.8 && (e.innerText||'').trim().length < 5) { e.style.setProperty('display','none','important'); hid++; } });
                      document.documentElement.style.overflow='auto'; document.body.style.overflow='auto';
                      return 'hid ' + hid; })()""" % json.dumps(st["hide_text"])
                    print("hide_text", st["hide_text"], "->", await c.eval(js))
                    await asyncio.sleep(0.6)
                elif "scroll_to_text" in st:
                    js = """(() => { const q = %s.toLowerCase(); const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
                      while ((n = w.nextNode())) { if (n.textContent.toLowerCase().includes(q)) { const el = n.parentElement;
                        if (el.getBoundingClientRect().height === 0) continue;
                        el.scrollIntoView({block: 'start'}); return 'ok'; } } return 'NOT FOUND'; })()""" % json.dumps(st["scroll_to_text"])
                    r = await c.eval(js)
                    await asyncio.sleep(0.8)
                    if st.get("offset"):
                        await c.eval("""(() => { window.scrollBy(0, %d); const els=[...document.querySelectorAll('*')].filter(e=>{const s=getComputedStyle(e); return (s.overflowY==='auto'||s.overflowY==='scroll') && e.scrollHeight>e.clientHeight+50;}); els.forEach(e=>e.scrollBy(0, %d)); })()""" % (int(st["offset"]), int(st["offset"])))
                    print("scroll_to_text", st["scroll_to_text"], "->", r)
                    await asyncio.sleep(st.get("wait", 1.5))
                elif "locate" in st:
                    js = """(() => { const want = %s; const out = {};
                      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
                      while ((n = w.nextNode())) { const t = n.textContent;
                        for (const q of want) { if (!(q in out) && t.toLowerCase().includes(q.toLowerCase())) {
                          const r = n.parentElement.getBoundingClientRect();
                          if (r.height > 0) out[q] = [Math.round(r.y + scrollY), Math.round(r.height)]; } } }
                      return JSON.stringify(out); })()""" % json.dumps(st["locate"])
                    print("locate ->", await c.eval(js))
                elif "text" in st:
                    txt = await c.eval("document.body.innerText")
                    out = os.path.join(SHOTS, st["text"])
                    with open(out, "w") as f:
                        f.write(txt or "")
                    print("text", out, len(txt or ""))
                elif "wait" in st:
                    await asyncio.sleep(st["wait"])
    finally:
        proc.terminate()
        try:
            proc.wait(5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])) if not sys.argv[1].startswith("{") else json.loads(sys.argv[1])
    asyncio.run(run(spec))
