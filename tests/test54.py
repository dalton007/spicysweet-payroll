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
pg.locator("aside.ss-side button[title='Settings']").click(); pg.wait_for_timeout(500)
print("sounds section:", pg.locator("#set-sounds").count(), "| play buttons:", pg.locator("#set-sounds button").count())
pg.locator("#set-sounds button").first.click(); pg.wait_for_timeout(300)
pg.locator("#set-sounds input[type=checkbox]").first.uncheck(); pg.wait_for_timeout(200)
print("pref saved:", pg.evaluate("localStorage.getItem('spicysweet.payroll.v2.sounds')"), "| errors:", errs[:2])
b.close(); p.stop()
