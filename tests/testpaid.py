import re
from playwright.sync_api import sync_playwright
OUT='/home/claude/preview/t51'
p=sync_playwright().start(); b=p.chromium.launch(); errs=[]
pg=b.new_page(viewport={"width":1440,"height":1000}); pg.on("pageerror", lambda e: errs.append(str(e)))
pg.goto(f"file://{OUT}/t-x.html"); pg.wait_for_timeout(1200)
pg.get_by_role("button", name=re.compile("Create an account")).click(); pg.wait_for_timeout(200)
pg.locator('input[placeholder^="Your name"]').fill("Dalton"); pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123")
pg.get_by_role("button", name=re.compile("^Create account$")).click(); pg.wait_for_timeout(400)
pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123"); pg.get_by_role("button", name=re.compile("^Sign in$")).click(); pg.wait_for_timeout(900)
pg.get_by_role("button", name=re.compile("Enter payroll")).click(); pg.wait_for_timeout(600)
def imp(f):
    pg.get_by_role("button", name=re.compile("^Import$")).click(); pg.wait_for_timeout(200)
    pg.locator(".ss-menu button").first.click(); pg.wait_for_timeout(200)
    pg.locator('header input[type="file"]').set_input_files(f); pg.wait_for_timeout(1000)
    pg.get_by_role("button", name=re.compile("^Confirm$")).click(); pg.wait_for_timeout(900)
state=lambda: pg.evaluate("(() => { const d=window.__sb.db.app_state.main.data; return [d.settings.payPeriod, d.employees.map(e=>[e.name,e.paid,e.paidPeriod||'',e.paidMethod||''])]; })()")
imp('/tmp/claude-0/-home-claude/004f865a-57f9-5c51-b943-5c520cd84915/scratchpad/week1.csv'); print("1 week1:", state())
# mark everyone paid through the Send out deck
pg.locator("aside.ss-side button[title='Send out']").click(); pg.wait_for_timeout(500)
pg.locator(".ss-deck-card").first.click(); pg.wait_for_timeout(300)
for i in range(8):
    btn=pg.get_by_role("button", name=re.compile("Mark paid & next"))
    if btn.count()==0: break
    btn.first.click(); pg.wait_for_timeout(500)
print("2 after paying:", state())
# legacy: strip paidPeriod to mimic chatters marked paid before this update
print("2b same-week re-import keeps paid:"); imp('/tmp/claude-0/-home-claude/004f865a-57f9-5c51-b943-5c520cd84915/scratchpad/week1.csv'); print("  ", state())
imp('/tmp/claude-0/-home-claude/004f865a-57f9-5c51-b943-5c520cd84915/scratchpad/week2.csv'); s=state(); print("3 new week:", s)
print("   notice:", [l for l in pg.locator("body").inner_text().split("\n") if "reset to unpaid" in l][:1])
print("RESULT new-week all unpaid:", all(not x[1] for x in s[1]))
print("errors:", errs[:4]); b.close(); p.stop()
