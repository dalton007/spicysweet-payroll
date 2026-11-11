import re
from playwright.sync_api import sync_playwright
OUT='tests/t51'
p=sync_playwright().start(); b=p.chromium.launch(); errs=[]
pg=b.new_page(viewport={"width":1440,"height":1000}); pg.on("pageerror", lambda e: errs.append(str(e)))
pg.goto(f"file://{OUT}/t.html"); pg.wait_for_timeout(1200)
pg.get_by_role("button", name=re.compile("Create an account")).click(); pg.wait_for_timeout(200)
pg.locator('input[placeholder^="Your name"]').fill("Dalton"); pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123")
pg.get_by_role("button", name=re.compile("^Create account$")).click(); pg.wait_for_timeout(400)
pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123"); pg.get_by_role("button", name=re.compile("^Sign in$")).click(); pg.wait_for_timeout(900)
pg.get_by_role("button", name=re.compile("Enter payroll")).click(); pg.wait_for_timeout(600)
pg.locator('section input').first.fill("Zuna"); pg.wait_for_timeout(300)
print("1 slot for Zuna:", pg.locator("table.ss-table tr.row").first.inner_text().replace("\n"," | ")[:80])
pg.locator('section input').first.fill("Zuna Rose"); pg.wait_for_timeout(300)
print("2 slot after rename:", pg.locator("table.ss-table tr.row").first.inner_text().replace("\n"," | ")[:80])
print("3 roster row:", pg.evaluate("window.__sb && null") , pg.evaluate("(() => { try { return JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.includes('paystub')||k.includes('spicy')))).roster.filter(r=>r[0].startsWith('Zuna')) } catch(e) { return String(e) } })()"))
pg.get_by_role("button", name=re.compile(r"\+ Add shift")).click(); pg.wait_for_timeout(200)
pg.locator('input[placeholder="8"]').first.fill("16"); pg.locator('input[placeholder="0.00"]').first.fill("900"); pg.wait_for_timeout(500)
print("4 checks:", [l for l in pg.locator("main").inner_text().split("\n") if "16h" in l or "typo" in l][:2])
print("errors:", errs[:3]); b.close(); p.stop()
