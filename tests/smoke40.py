"""Smoke-test the BUILT html in a real browser: swap CDN scripts for local React, click through."""
import os, re, sys, json
HTML = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
NM = '/usr/local/lib/node_modules_global'
html = open(HTML).read()
def cjs(path): return open(path).read()
shim = '''
var process = { env: { NODE_ENV: "development" } };
var __mods = {};
function __def(name, fn){ __mods[name] = {fn:fn, exp:null}; }
function require(name){ var m = __mods[name]; if(!m) throw new Error("no module "+name); if(!m.exp){ var module={exports:{}}; m.fn(module, module.exports, require); m.exp = module.exports; } return m.exp; }
__def("react", function(module, exports, require){ %s });
__def("scheduler", function(module, exports, require){ %s });
__def("react-dom", function(module, exports, require){ %s });
__def("react-dom/client", function(module, exports, require){ %s });
window.React = require("react"); window.ReactDOM = Object.assign({}, require("react-dom"), require("react-dom/client"));
''' % (cjs(f'{NM}/react/cjs/react.development.js'), cjs('/opt/npm-tools/node_modules/scheduler/cjs/scheduler.development.js'),
       cjs(f'{NM}/react-dom/cjs/react-dom.development.js'), cjs(f'{NM}/react-dom/cjs/react-dom-client.development.js'))
html = re.sub(r'<script src="https://cdnjs[^"]*react-dom[^"]*"></script>', '', html)
html = re.sub(r'<script src="https://cdnjs[^"]*/react/[^"]*"></script>', lambda m: '<script>' + shim.replace('</script', '<\\/script') + '</script>', html)
html = re.sub(r'<script src="https://cdn.tailwindcss.com"></script>', '<link rel="stylesheet" href="tw.css"><script>window.tailwind={}</script>', html)
html = re.sub(r'<script src="https://cdnjs[^"]*"></script>', '', html)
html = re.sub(r'<link[^>]*fonts[^>]*>', '', html)
open(f'{OUT}/smoke.html', 'w').write(html)
import shutil; shutil.copy('tests/v40/tw.css', f'{OUT}/tw.css')

from playwright.sync_api import sync_playwright
p = sync_playwright().start(); b = p.chromium.launch()
pg = b.new_page(viewport={"width": 1380, "height": 900})
errs = []
pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
pg.goto(f"file://{OUT}/smoke.html"); pg.wait_for_timeout(1200)
print("landing:", pg.locator("text=Enter payroll").count())
pg.get_by_role("button", name=re.compile("Enter payroll")).click(); pg.wait_for_timeout(700)
pg.screenshot(path=f"{OUT}/s_payroll.png")
print("sidebar items:", pg.locator("aside.ss-side nav button.ss-side-item").count())
# add shift + values
pg.get_by_role("button", name=re.compile(r"\+ Add shift")).click(); pg.wait_for_timeout(200)
pg.locator('input[placeholder="8"]').first.fill("8")
pg.locator('input[placeholder="0.00"]').first.fill("1200"); pg.wait_for_timeout(400)
print("gross pay:", pg.locator("text=Gross pay").count())
# table row present, sort click
pg.locator("table.ss-table th", has_text="Pay").click(); pg.wait_for_timeout(200)
print("table rows:", pg.locator("table.ss-table tbody tr").count())
for v in ["Insights", "Leaderboard", "History", "Agency P&L", "Settings", "Payroll"]:
    pg.locator(f'aside.ss-side button[title="{v}"]').first.click(); pg.wait_for_timeout(450)
    pg.screenshot(path=f"{OUT}/s_{v.lower().replace(' ','_').replace('&','')}.png")
# insights sub-items via sidebar
pg.locator('aside.ss-side button[title="Insights"]').first.click(); pg.wait_for_timeout(300)
for t in ["Team", "Models", "Attendance", "Chatter"]:
    btn = pg.locator("aside.ss-side .ss-side-sub button", has_text=re.compile("^"+t+"$"))
    if btn.count(): btn.first.click(); pg.wait_for_timeout(350)
# collapse sidebar
pg.locator("button.ss-side-toggle").click(); pg.wait_for_timeout(400)
print("mini:", pg.locator("aside.ss-side.is-mini").count())
pg.screenshot(path=f"{OUT}/s_mini.png")
pg.locator("button.ss-side-toggle").click(); pg.wait_for_timeout(300)
# save week → history
pg.locator('aside.ss-side button[title="Payroll"]').first.click(); pg.wait_for_timeout(300)
sv = pg.get_by_role("button", name=re.compile("Save this week"))
if sv.count(): sv.first.click(); pg.wait_for_timeout(500)
pg.locator('aside.ss-side button[title="History"]').first.click(); pg.wait_for_timeout(400)
print("saved weeks:", pg.locator("text=Open in editor").count())
# reload persistence (mini state + data)
pg.reload(); pg.wait_for_timeout(1000)
pg.get_by_role("button", name=re.compile("Enter payroll")).click(); pg.wait_for_timeout(500)
print("after reload rows:", pg.locator("table.ss-table tbody tr").count())
b.close(); p.stop()
print("console errors:", len(errs))
for e in errs[:8]: print("  ", e[:300])
