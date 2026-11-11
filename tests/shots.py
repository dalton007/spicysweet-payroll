import re, sys
from playwright.sync_api import sync_playwright
OUT='tests/t51'
p=sync_playwright().start(); b=p.chromium.launch(); errs=[]
pg=b.new_page(viewport={"width":1440,"height":1000}); pg.on("pageerror", lambda e: errs.append(str(e)))
html=open(f"{OUT}/t.html").read()
html=html.replace("<script>\n", "<script src=\"file://tests/vendor/xlsx.full.min.js\"></script>\n<script>\n", 1); open(f"{OUT}/t-x.html","w").write(html)
pg.goto(f"file://{OUT}/t-x.html"); pg.wait_for_timeout(1200)
pg.get_by_role("button", name=re.compile("Create an account")).click(); pg.wait_for_timeout(200)
pg.locator('input[placeholder^="Your name"]').fill("Dalton"); pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123")
pg.get_by_role("button", name=re.compile("^Create account$")).click(); pg.wait_for_timeout(400)
pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123"); pg.get_by_role("button", name=re.compile("^Sign in$")).click(); pg.wait_for_timeout(900)
pg.get_by_role("button", name=re.compile("Enter payroll")).click(); pg.wait_for_timeout(600)
pg.get_by_role("button", name=re.compile("^Import$")).click(); pg.locator(".ss-menu button").first.click(); pg.wait_for_timeout(200)
pg.locator('header input[type="file"]').set_input_files('tests/mp-test2.csv'); pg.wait_for_timeout(1000)
pg.get_by_role("button", name=re.compile("^Confirm$")).click(); pg.wait_for_timeout(600)
pg.get_by_role("button", name=re.compile("^Import$")).click(); pg.locator(".ss-menu button").nth(1).click(); pg.wait_for_timeout(200)
pg.locator('header input[type="file"]').set_input_files('tests/creators.xlsx'); pg.wait_for_timeout(1500)
pg.get_by_role("button", name=re.compile("^Import report$")).click(); pg.wait_for_timeout(800)
pg.locator('input[placeholder^="e.g. Oct"]').fill("Nov 2 – Nov 8, 2026"); pg.wait_for_timeout(300)
views=["Payroll","Send out","Insights","Leaderboard","History","Agency P&L","Invoices","Settings"]
for w,tag in [(1440,"d"),(390,"m")]:
    pg.set_viewport_size({"width":w,"height":1000 if w>400 else 844}); pg.wait_for_timeout(300)
    for v in views:
        pg.locator(f"aside.ss-side button[title='{v}']").click(); pg.wait_for_timeout(500)
        if v=="Send out": pg.get_by_role("button", name=re.compile("^Start$")).first.click(); pg.wait_for_timeout(300)
        pg.screenshot(path=f"{OUT}/s-{tag}-{v.replace(' ','').replace('&','')}.png", full_page=True)
print("errors:", errs[:3]); b.close(); p.stop()
