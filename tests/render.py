"""
Server-render every view of the app with realistic seeded data, wrap each in
the design CSS + generated utility CSS, and screenshot at desktop width.
Usage: python3 render.py <app.jsx> <outdir>
"""
import sys, os, subprocess, re, json

SRC = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))

# utility css for whatever classes this version uses
subprocess.run(['python3', f'{HERE}/twgen.py', SRC, f'{OUT}/tw.css'], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

src = open(SRC).read()
m = '<style>{`'
i = src.index(m) + len(m); j = src.index('`}</style>', i)
design_css = src[i:j]
# preview-only font stand-ins (the shipped file loads Outfit + Plus Jakarta Sans)
design_css = design_css.replace("'Plus Jakarta Sans', ui-sans-serif", "Inter, ui-sans-serif")
design_css = design_css.replace("'Outfit', 'Plus Jakarta Sans', sans-serif", "'Inter Display', Inter, sans-serif")
open(f'{OUT}/design.css', 'w').write(design_css)

logo = re.search(r'const LOGO =\s*"([^"]+)"', src).group(1)

SEED = r'''
  const [employees, setEmployees] = useState(SEED_EMPLOYEES);
'''
seed_js = r'''
const SEED_EMPLOYEES = (() => {
  const mk = (name, team, n, shifts, extra) => {
    const e = newEmployee(n); e.name = name; e.team = team;
    e.shifts = shifts.map((s, i) => ({ id: name + "-" + i, date: "2026-11-0" + (i + 1), hours: s[0], revenue: s[1],
      fansly: s[2] || "", streaming: !!s[3], streamHours: s[3] ? String(s[3]) : "", creators: s[4] || "Smeepsx",
      ppvSent: s[5] || 40, msgsSent: s[6] || 600, schedHours: 8, respMin: s[7] || 3.4 }));
    return Object.assign(e, extra || {});
  };
  return [
    mk("Flor", "Team Smeeps", 1, [["8","2400","",0,"Smeepsx",90,900,2.1],["8","2210","150",0,"Smeepsx",85,880,2.4],["8","1980","",0,"Smeepsx",70,800,2.0],["8","2300","",0,"Smeepsx",88,850,2.2]], { headChatter: true, paid: true, adjustments: [{ id: "a1", amount: 25, label: "October contest prize" }, { id: "a2", amount: -40, label: "Advance repayment 2/4" }] }),
    mk("Jah", "Team Mennah", 2, [["7","1900","",0,"Mennah",80,700,2.8],["8","2100","200",0,"Mennah",92,760,3.0],["8","1750","",0,"Mennah",60,720,3.1]], { headChatter: true }),
    mk("Katelyn", "Team Mennah", 3, [["8","1500","",0,"Mennah",70,650,3.6],["8","1620","",0,"Mennah",74,640,3.2],["6","1100","",0,"Mennah",48,500,3.9]]),
    mk("Khaizelle", "Team Smeeps", 4, [["8","1400","",0,"Smeepsx",58,800,4.1],["8","1250","",0,"Smeepsx",52,780,4.4]]),
    mk("Kristoffer", "Team Smeeps", 5, [["8","1200","",0,"Smeepsx",64,610,1.9],["7","980","",0,"Smeepsx",55,590,2.2]]),
    mk("Keycee", "Team Spicy", 6, [["8","820","",3,"Elara",40,520,4.8],["8","760","120",0,"Elara",36,500,5.1]]),
    mk("Zuna", "Team Spicy", 7, [["8","700","",0,"Elara",30,620,5.6],["8","640","",0,"Elara",28,600,6.0]], { strikeLog: [{ id: "s1", date: "2026-10-20", reason: "Late clock-in" }, { id: "s2", date: "2026-10-27", reason: "No handoff notes" }] }),
    mk("Gesel", "Team Kenna", 8, [["8","610","",0,"Kenna",22,480,6.2],["8","590","",0,"Kenna",20,470,6.5]]),
    mk("Crimes", "Team Sweet", 9, [["8","520","",0,"Keawave",18,610,7.1],["8","480","",0,"Keawave",15,590,7.4]]),
    mk("Vanny", "Team Spicy", 10, [["8","410","",0,"Elara",16,520,8.2],["8","380","",0,"Elara",14,500,8.0]]),
    mk("Topic", "Team Sweet", 11, [["8","220","",0,"Gen",9,420,9.5],["8","180","",0,"Gen",7,400,10.2]]),
  ];
})();
const SEED_HISTORY = [
  { payPeriod: "Oct 12 – 18", savedDate: "2026-10-18", chatters: {
      flor: { name:"Flor", rev: 7800, gross: 420, hits: 3, shifts: 4, gr: 9.1, rph: 240, avgRev: 1950, avgResp: 2.3, focus: [] },
      jah: { name:"Jah", rev: 5200, gross: 300, hits: 2, shifts: 3, gr: 10.1, rph: 226, avgRev: 1733, avgResp: 2.9, focus: ["Push to Target 3"] },
      keycee: { name:"Keycee", rev: 1300, gross: 110, hits: 1, shifts: 2, gr: 6.2, rph: 81, avgRev: 650, avgResp: 5.4, focus: ["Golden ratio", "Response speed"] },
      topic: { name:"Topic", rev: 300, gross: 50, hits: 0, shifts: 2, gr: 1.8, rph: 19, avgRev: 150, avgResp: 10.9, focus: ["Close the gap to Target 1", "Golden ratio"] },
    }, teams: { "Team Smeeps": { rev: 11200, shiftRevs: [2100,1900,1800,2000,1300,1100,1000,900] }, "Team Mennah": { rev: 8900, shiftRevs: [1800,2000,1700,1500,1400,500] }, "Team Spicy": { rev: 3600, shiftRevs: [800,700,650,600,450,400] }, "Team Kenna": { rev: 1100, shiftRevs: [600,500] }, "Team Sweet": { rev: 1300, shiftRevs: [500,450,200,150] } },
       models: { Smeepsx: { rev: 11200 }, Mennah: { rev: 8900 }, Elara: { rev: 3600 }, Kenna: { rev: 1100 }, Keawave: { rev: 900 }, Gen: { rev: 400 } } },
  { payPeriod: "Oct 19 – 25", savedDate: "2026-10-25", chatters: {
      flor: { name:"Flor", rev: 8400, gross: 450, hits: 4, shifts: 4, gr: 9.6, rph: 262, avgRev: 2100, avgResp: 2.2, focus: [] },
      jah: { name:"Jah", rev: 5600, gross: 320, hits: 3, shifts: 3, gr: 11.0, rph: 233, avgRev: 1866, avgResp: 2.8, focus: [] },
      keycee: { name:"Keycee", rev: 1450, gross: 118, hits: 1, shifts: 2, gr: 6.9, rph: 90, avgRev: 725, avgResp: 5.0, focus: ["Golden ratio"] },
      topic: { name:"Topic", rev: 350, gross: 52, hits: 0, shifts: 2, gr: 1.9, rph: 22, avgRev: 175, avgResp: 10.1, focus: ["Close the gap to Target 1", "Golden ratio"] },
    }, teams: { "Team Smeeps": { rev: 12600, shiftRevs: [2300,2100,1900,2200,1350,1200,1100,950] }, "Team Mennah": { rev: 9400, shiftRevs: [1900,2100,1750,1600,1450,600] }, "Team Spicy": { rev: 3400, shiftRevs: [780,720,640,580,420,360] }, "Team Kenna": { rev: 1150, shiftRevs: [620,530] }, "Team Sweet": { rev: 1250, shiftRevs: [480,470,180,120] } },
       models: { Smeepsx: { rev: 12600 }, Mennah: { rev: 9400 }, Elara: { rev: 3400 }, Kenna: { rev: 1150 }, Keawave: { rev: 850 }, Gen: { rev: 400 } } },
];
SEED_HISTORY[0].weekStart = "2026-10-12"; SEED_HISTORY[0].weekEnd = "2026-10-18"; SEED_HISTORY[0].savedAt = "2026-10-18T20:00:00Z";
SEED_HISTORY[1].weekStart = "2026-10-19"; SEED_HISTORY[1].weekEnd = "2026-10-25"; SEED_HISTORY[1].savedAt = "2026-10-25T20:00:00Z";
SEED_HISTORY[1].full = { employees: SEED_EMPLOYEES.map((e) => ({ ...e, shifts: e.shifts.map((s) => ({ ...s, date: s.date.replace("2026-11-0", "2026-10-2") })) })), settings: { ...DEFAULT_SETTINGS, payPeriod: "Oct 19 – 25" }, roster: DEFAULT_ROSTER, prizes: {} };
Object.values(SEED_HISTORY[1].chatters).forEach((c) => { c.team = { flor: "Team Smeeps", jah: "Team Mennah", keycee: "Team Spicy", topic: "Team Sweet" }[c.name.toLowerCase()]; c.bonus = 15; c.prize = c.name === "Flor" ? 15 : 0; c.net = c.rev * 0.8; });
Object.values(SEED_HISTORY[0].chatters).forEach((c) => { c.team = { flor: "Team Smeeps", jah: "Team Mennah", keycee: "Team Spicy", topic: "Team Sweet" }[c.name.toLowerCase()]; c.net = c.rev * 0.8; });
Object.values(SEED_HISTORY[0].teams).forEach((t) => { t.payroll = Math.round(t.rev * 0.09); t.members = 2; });
Object.values(SEED_HISTORY[1].teams).forEach((t) => { t.payroll = Math.round(t.rev * 0.09); t.members = 2; });
'''

src = src.replace('import * as XLSX from "xlsx";', 'const XLSX = {};')
src = src.replace('const DEFAULT_FEATURES = {', 'let LANDING = false;\nlet VIEW0 = "payroll";\nlet ITAB0 = "insights";\nconst DEFAULT_FEATURES = {')
src = src.replace('const [showLanding, setShowLanding] = useState(true);', 'const [showLanding, setShowLanding] = useState(LANDING);')
src = src.replace('const [view, setView] = useState("payroll");', 'const [view, setView] = useState(VIEW0);')
src = src.replace('const [historyTab, setHistoryTab] = useState("weeks");', 'const [historyTab, setHistoryTab] = useState(HTAB0);')
src = src.replace('let ITAB0 = "insights";', 'let ITAB0 = "insights";\nlet HTAB0 = "weeks";')
src = src.replace('["Zuna", "Team Spicy", "12AM–8AM"],', '["Zuna", "Team Spicy", "12AM–8AM", "2026-03-02", "active", 6],')
src = src.replace('["Chad", "Team Sweet", "12AM–8AM"],', '["Chad", "Team Sweet", "12AM–8AM", "2026-09-28", "probation", 6],')
src = src.replace('["Precious", "Team Sweet", "4PM–12AM"],', '["Precious", "Team Sweet", "4PM–12AM", "2025-08-01", "left", 6],')
src = src.replace('const [insightsTab, setInsightsTab] = useState("insights");', 'const [insightsTab, setInsightsTab] = useState(ITAB0);')
old_emp = '''  const [employees, setEmployees] = useState(
    (saved && saved.employees && saved.employees.length
      ? saved.employees
      : [newEmployee(1)])
  );'''
assert src.count(old_emp) == 1, "employees state anchor"
src = src.replace(old_emp, SEED)
old_hist = '  const [history, setHistory] = useState((saved && saved.history) || []);'
assert src.count(old_hist) == 1
src = src.replace(old_hist, '  const [history, setHistory] = useState(SEED_HISTORY);')
old_set = '''  const [settings, setSettings] = useState(
    (saved && saved.settings) || DEFAULT_SETTINGS
  );'''
assert src.count(old_set) == 1
src = src.replace(old_set, '''  const [settings, setSettings] = useState({ ...DEFAULT_SETTINGS, payPeriod: "Oct 26 – Nov 1, 2026", timeZone: "America/Chicago",
    managerName: "Leagin", invoices: [{ id: "i1", model: "Smeepsx", amount: "14894.41", tbd: false }, { id: "i2", model: "Mennah", amount: "14613.02", tbd: false }, { id: "i3", model: "Kitki", amount: "9727.42", tbd: false }, { id: "i4", model: "Cindy", amount: "", tbd: true }],
    teamGoalAmounts: { "Team Smeeps": { weekly: 20000, monthly: 80000 }, "Team Spicy": { weekly: 6000, monthly: 24000 } },
    modelGoalAmounts: { Smeepsx: { weekly: 12000, monthly: 48000 } } });''')
# prevWeek from seeded history
src = src.replace('''  const [prevWeek, setPrevWeek] = useState(
    saved && saved.history && saved.history.length
      ? saved.history[saved.history.length - 1]
      : null
  );''', '  const [prevWeek, setPrevWeek] = useState(SEED_HISTORY[SEED_HISTORY.length - 1]);')
# place seed before the component
src = src.replace('export default function PaystubApp()', seed_js + '\nexport default function PaystubApp()')

harness = r'''
const mem = {}; global.window = global.window || {};
window.localStorage = { getItem:(k)=>(k in mem?mem[k]:null), setItem:(k,v)=>{mem[k]=String(v);}, removeItem:(k)=>{delete mem[k];} };
window.matchMedia = window.matchMedia || (() => ({ matches:false, addListener(){}, removeListener(){} }));
import { renderToStaticMarkup } from "react-dom/server";
import * as fs from "fs";
const OUT = process.argv[2];
const pages = [
  ["landing", true, "payroll", "insights"],
  ["payroll", false, "payroll", "insights"],
  ["insights", false, "insights", "insights"],
  ["insights-team", false, "insights", "team"],
  ["insights-models", false, "insights", "models"],
  ["board", false, "board", "insights"],
  ["insights-attendance", false, "insights", "attendance"],
  ["history-weeks", false, "history", "insights", "weeks"],
  ["history-months", false, "history", "insights", "months"],
  ["trends", false, "history", "insights", "trends"],
  ["pnl", false, "pnl", "insights"],
  ["settings", false, "settings", "insights"],
];
for (const [name, landing, view, itab, htab] of pages) {
  LANDING = landing; VIEW0 = view; ITAB0 = itab; HTAB0 = htab || "weeks";
  const body = renderToStaticMarkup(React.createElement(PaystubApp));
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="tw.css"><link rel="stylesheet" href="design.css">
<style>body{font-family:Inter,sans-serif}</style></head><body>${body}</body></html>`;
  fs.writeFileSync(`${OUT}/${name}.html`, html);
  console.log("wrote", name, body.length);
}
'''
open(f'{OUT}/App.tsx', 'w').write(src + harness)
open(f'{OUT}/tsconfig.json', 'w').write(json.dumps({"compilerOptions": {"jsx": "react", "target": "es2020", "module": "commonjs",
  "esModuleInterop": True, "allowJs": True, "skipLibCheck": True, "noEmitOnError": False, "outDir": "out"}}))
env = dict(os.environ, NODE_PATH='/usr/local/lib/node_modules_global', TZ='America/Chicago')
subprocess.run(['tsc', '-p', 'tsconfig.json'], cwd=OUT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
r = subprocess.run(['node', 'out/App.js', OUT], cwd=OUT, env=env, capture_output=True, text=True)
print(r.stdout[-1500:]);
if r.returncode: print("NODE ERROR:", r.stderr[-1500:]); sys.exit(1)

# screenshots
shot = f'''
from playwright.sync_api import sync_playwright
import os
p = sync_playwright().start(); b = p.chromium.launch()
pg = b.new_page(viewport={{"width": 1380, "height": 900}}, device_scale_factor=1.5)
for name in {json.dumps(["landing","payroll","insights","insights-team","insights-models","insights-attendance","board","history-weeks","history-months","trends","pnl","settings"])}:
    pg.goto("file://{OUT}/" + name + ".html"); pg.wait_for_timeout(900)
    pg.screenshot(path="{OUT}/" + name + ".png", full_page=True)
    print("shot", name)
b.close(); p.stop()
'''
open(f'{OUT}/shot.py', 'w').write(shot)
subprocess.run(['python3', f'{OUT}/shot.py'], check=True)
