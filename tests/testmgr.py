import re, json, sys
from playwright.sync_api import sync_playwright
S=sys.argv[1]
CH='/mnt/user-data/uploads/4e9f3427-c9b8-49c7-9fc0-0b5abdeebc1c.xlsx'
CR='/mnt/user-data/attachments/004f865a-57f9-5c51-b943-5c520cd84915/ee647029-Creator_Reports_Overview_All_Data_Net_Earnings_Display_total_numbers_and_by_day_20261112_2647953186160672.xlsx'
p=sync_playwright().start(); b=p.chromium.launch(); errs=[]
pg=b.new_page(viewport={"width":1440,"height":1000}); pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
pg.goto("file:///home/claude/preview/t51/mgr.html"); pg.wait_for_timeout(300); pg.evaluate("localStorage.clear()"); pg.goto("file:///home/claude/preview/t51/mgr.html"); pg.wait_for_timeout(1200)
pg.get_by_role("button", name=re.compile("Create an account")).click(); pg.wait_for_timeout(200)
pg.locator('input[placeholder^="Your name"]').fill("Dalton"); pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123")
pg.get_by_role("button", name=re.compile("^Create account$")).click(); pg.wait_for_timeout(400)
pg.locator('input[type="email"]').fill("owner@test.com"); pg.locator('input[type="password"]').fill("password123"); pg.get_by_role("button", name=re.compile("^Sign in$")).click(); pg.wait_for_timeout(900)
pg.get_by_role("button", name=re.compile("Enter payroll")).click(); pg.wait_for_timeout(600)
def imp(k,f):
    pg.get_by_role("button", name=re.compile("^Import$")).click(); pg.wait_for_timeout(200)
    pg.locator(".ss-menu button").nth(k).click(); pg.wait_for_timeout(200)
    pg.locator('header input[type="file"]').set_input_files(f); pg.wait_for_timeout(1500)
imp(0,CH); pg.get_by_role("button", name=re.compile("^Confirm$")).click(); pg.wait_for_timeout(900)
pg.get_by_role("button", name=re.compile("Save this week")).click(); pg.wait_for_timeout(600)
imp(1,CR); pg.get_by_role("button", name=re.compile("^Import report$")).click(); pg.wait_for_timeout(1200)
pg.locator("aside.ss-side button[title='Manager pay']").click(); pg.wait_for_timeout(600)
pg.screenshot(path=f"{S}/mgr-empty.png")
pg.get_by_role("button", name=re.compile("Start the first period")).click(); pg.wait_for_timeout(700)
st=lambda: (pg.wait_for_timeout(2500), pg.evaluate("(()=>{const s=window.__sb.db.app_state.main.data.settings;return s.managerPeriods})()"))[1]
print("1 period:", json.dumps(st())[:300])
print("  commission shown:", pg.locator(".font-display.text-3xl").inner_text(), "| invoices ticked:", pg.locator("main input[type=checkbox]:checked").count())
pg.screenshot(path=f"{S}/mgr-period.png", full_page=True)
# move start back to cover the saved payroll week
pg.locator('main input[type=date]').first.fill("2026-06-30"); pg.wait_for_timeout(400)
print("2 after start Jun 30:", pg.locator(".font-display.text-3xl").inner_text())
pg.get_by_role("button", name=re.compile("^2 weeks$")).click(); pg.wait_for_timeout(400)
print("   end now:", st()[0]['end'], "| commission:", pg.locator(".font-display.text-3xl").inner_text())
pg.locator('main input[type=date]').first.fill("2026-10-28"); pg.get_by_role("button", name=re.compile("^2 weeks$")).click(); pg.wait_for_timeout(300)
# include the payroll week manually
lbl=pg.locator("main label", has_text="2026-06-30")
if lbl.count(): lbl.first.locator("input").check(); pg.wait_for_timeout(300)
print("   SUMMARY3:", pg.locator("main .max-w-md").inner_text().replace(chr(10)," | ")); print("   WEEKS3:", pg.locator("main ul").nth(1).inner_text().replace(chr(10)," | "));print("3 with payroll week ticked:", pg.locator(".font-display.text-3xl").inner_text(), "| wk override:", st()[0]['wk'])
pg.get_by_role("button", name=re.compile("Add expense")).click(); pg.wait_for_timeout(200)
pg.locator('main input[placeholder="e.g. software, ads"]').fill("Infloww seats"); pg.locator('main input[placeholder="0.00"]').last.fill("250"); pg.wait_for_timeout(300)
print("   SUMMARY4:", pg.locator("main .max-w-md").inner_text().replace(chr(10)," | ")); print("   WEEKS4:", pg.locator("main ul").nth(1).inner_text().replace(chr(10)," | "));print("4 with expense:", pg.locator(".font-display.text-3xl").inner_text(), [(x["label"],x["amount"]) for x in st()[0]["expenses"]], "income", st()[0]["income"])
pg.locator("main select").last.select_option("Zelle"); pg.get_by_role("button", name=re.compile("Mark paid")).click(); pg.wait_for_timeout(500)
print("5 paid:", {k:st()[0][k] for k in ('status','paidMethod','paidDate')}, "| date inputs disabled:", pg.locator('main input[type=date]').first.is_disabled())
pg.get_by_role("button", name=re.compile("^New$")).click(); pg.wait_for_timeout(500)
print("6 next period:", [(x['start'],x['end'],x['status']) for x in st()])
pg.screenshot(path=f"{S}/mgr-midnight.png", full_page=True)
pg.locator(".ss-mgr-period").nth(1).click(); pg.wait_for_timeout(300)
pg.get_by_role("button", name=re.compile("Copy statement")).click(); pg.wait_for_timeout(300)
pg.set_viewport_size({"width":390,"height":844}); pg.wait_for_timeout(500)
print("7 phone width:", pg.evaluate("document.documentElement.scrollWidth"))
pg.screenshot(path=f"{S}/mgr-phone.png", full_page=True)
print("errors", errs[:5]); b.close(); p.stop()
