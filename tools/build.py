"""
Package the payroll app as one HTML file.
  python3 build.py <app.jsx> <out.html> [--babel]
Default: JSX is precompiled here with tsc, so the page loads React and runs — no
in-browser Babel. --babel keeps the old text/babel route (slower to open).
"""
import sys, os, re, subprocess, json, base64

SRC, OUT = sys.argv[1], sys.argv[2]
USE_BABEL = "--babel" in sys.argv
HOSTED = "--hosted" in sys.argv  # icons + manifest as sibling files instead of data: URLs
SUPABASE = None  # --supabase URL KEY → accounts + cloud sync through the user's Supabase project
if "--supabase" in sys.argv:
    i = sys.argv.index("--supabase"); SUPABASE = (sys.argv[i + 1], sys.argv[i + 2])
TMP = os.environ.get("SS_BUILD_TMP", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".build"))
os.makedirs(TMP, exist_ok=True)

src = open(SRC).read()
src = re.sub(r'^import .*$', '', src, flags=re.M)
src = src.replace('export default function PaystubApp', 'function PaystubApp')
body = 'const { useState, useMemo, useRef, useEffect, useLayoutEffect } = React;\n// XLSX loaded globally from CDN\n' + src
body += '\n\nReactDOM.createRoot(document.getElementById("root")).render(React.createElement(typeof AppRoot === "function" ? AppRoot : PaystubApp));\n'

if USE_BABEL:
    app_script = '<script type="text/babel" data-presets="react">\n' + body.replace('React.createElement(PaystubApp)', '<PaystubApp />') + '\n</script>'
    babel_tag = '<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>'
else:
    open(f'{TMP}/app.tsx', 'w').write(body)
    open(f'{TMP}/tsconfig.json', 'w').write(json.dumps({"compilerOptions": {
        "jsx": "react", "target": "es2020", "module": "none", "allowJs": True, "skipLibCheck": True,
        "noEmitOnError": False, "outDir": "out", "lib": ["es2020", "dom"], "removeComments": False}, "files": ["app.tsx"]}))
    subprocess.run(['tsc', '-p', 'tsconfig.json'], cwd=TMP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    js = open(f'{TMP}/out/app.js').read()
    js = js.replace('</script', '<\\/script')
    app_script = '<script>\n' + js + '\n</script>'
    babel_tag = ''

logo = re.search(r'const LOGO =\s*"([^"]+)"', src).group(1)
pptx_path = '/usr/local/lib/node_modules_global/pptxgenjs/dist/pptxgen.bundle.js'
if os.path.exists(pptx_path):
    pptx = '<script>\n' + open(pptx_path).read().replace('</script', '<\\/script') + '\n</script>'
else:
    pptx = '<script src="https://cdn.jsdelivr.net/npm/pptxgenjs@4.0.1/dist/pptxgen.bundle.js"></script>'

manifest = json.dumps({
    "name": "Spicy Sweet Payroll", "short_name": "Payroll", "start_url": ".", "display": "standalone",
    "background_color": "#FFF7FB", "theme_color": "#1C1126",
    "icons": [{"src": logo, "sizes": "any", "type": "image/png", "purpose": "any"}],
})
manifest_href = "data:application/manifest+json;base64," + base64.b64encode(manifest.encode()).decode()
icon_href = logo
if HOSTED:
    manifest_href = "manifest.webmanifest"
    icon_href = "icon-180.png"
    open(os.path.join(os.path.dirname(os.path.abspath(OUT)), "manifest.webmanifest"), "w").write(json.dumps({
        "name": "Spicy Sweet Payroll", "short_name": "Payroll", "start_url": ".", "display": "standalone",
        "background_color": "#FFF7FB", "theme_color": "#1C1126",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }))

TW_CONFIG = r"""
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Outfit', '"Plus Jakarta Sans"', 'sans-serif'],
      },
      borderRadius: { md: '9px', lg: '13px', xl: '18px', '2xl': '24px' },
      colors: {
        pink: { 50:'#FFF7FB', 100:'#FFEAF4', 200:'#FFD0E6', 300:'#FFA8CF', 400:'#F96FB0',
                500:'#F04393', 600:'#EC2A86', 700:'#C2156B', 800:'#951050', 900:'#6B0B3A' },
        rose: { 50:'#FFF5F6', 100:'#FFE4E7', 200:'#FFC6CC', 300:'#FF99A4', 400:'#F65E70',
                500:'#E73A4E', 600:'#DE2A3C', 700:'#B21A2A', 800:'#8A1420', 900:'#5E0D16' },
        red:  { 50:'#FFF5F6', 100:'#FFE3E6', 200:'#FFC4CA', 300:'#FF949F', 400:'#F75C6E',
                500:'#E53348', 600:'#DE2A3C', 700:'#A8101F', 800:'#850C18', 900:'#5C0810' },
        slate:{ 50:'#FAF7FB', 100:'#F4EEF6', 200:'#E7DEEB', 300:'#D1C4D8', 400:'#7F7089',
                500:'#7D6D86', 600:'#5F5069', 700:'#473A50', 800:'#2F2438', 900:'#1C1126' },
        yellow:{50:'#FFFCEC', 100:'#FDF3D2', 200:'#F9E6A3', 300:'#F4D86F', 400:'#EFC838',
                500:'#DDB220', 600:'#B98E16', 700:'#8E6B12', 800:'#6B5010', 900:'#4A370B' },
        amber: {50:'#FFFBEB', 100:'#FDF3D2', 200:'#F9E6A3', 300:'#F4D86F', 400:'#EFC838',
                500:'#DDB220', 600:'#B98E16', 700:'#8E6B12', 800:'#6B5010', 900:'#4A370B' },
        sky:  { 50:'#F2FBFE', 100:'#E0F5FC', 200:'#C2EBF8', 300:'#9FDCF2', 400:'#6AC6E6',
                500:'#38A9D1', 600:'#2287AE', 700:'#1A6A8A', 800:'#15516A', 900:'#0F3A4C' },
        emerald:{50:'#F0FBF6', 100:'#D7F4E7', 200:'#AAE7CD', 300:'#6FD3AB', 400:'#38B88A',
                500:'#1E9E73', 600:'#16815E', 700:'#13674C', 800:'#10503C', 900:'#0B382A' },
      },
    },
  },
};
"""

import datetime
APP_VERSION = "5.3.2+" + datetime.datetime.utcnow().strftime("%m%d%H%M")
if "--version" in sys.argv:
    APP_VERSION = sys.argv[sys.argv.index("--version") + 1]
if HOSTED:
    open(os.path.join(os.path.dirname(os.path.abspath(OUT)), "version.json"), "w").write(json.dumps({"version": APP_VERSION}))
supabase_tags = '<script>window.SPICY_VERSION = ' + json.dumps(APP_VERSION) + ';</script>\n'
if SUPABASE:
    supabase_tags += ('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.49.1/dist/umd/supabase.js"></script>\n'
                     '<script>window.SPICY_BACKEND = ' + json.dumps({"url": SUPABASE[0], "key": SUPABASE[1]}) + ';</script>')
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Spicy Sweet Payroll</title>
<meta name="description" content="Weekly chatter payroll, paystubs, insights and reports for the Spicy Sweet agency." />
<meta name="theme-color" content="#1C1126" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-title" content="Payroll" />
<link rel="icon" href="{logo}" />
<link rel="apple-touch-icon" href="{icon_href}" />
<link rel="manifest" href="{manifest_href}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
{babel_tag}
{supabase_tags}
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
<script>{TW_CONFIG}</script>
{pptx}
<style>
  html, body {{ margin: 0; background: #FFF7FB; }}
  #boot {{ position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; background: #FFF7FB; font-family: Outfit, sans-serif; color: #C2156B; font-weight: 800; letter-spacing: -.01em; }}
</style>
</head>
<body>
<div id="root"><div id="boot">Opening Spicy Sweet Payroll…</div></div>
{app_script}
</body>
</html>
"""
open(OUT, 'w').write(html)
print("packaged", os.path.basename(OUT), round(len(html) / 1024), "KB", "(babel)" if USE_BABEL else "(precompiled)")
