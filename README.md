# Spicy Sweet Payroll

Weekly chatter payroll, paystubs, model invoices, insights and reports for the Spicy Sweet agency.
One React file, built into one HTML page, hosted on GitHub Pages, with Supabase for accounts and sync.

**Live app:** https://dalton007.github.io/spicysweet-payroll/ (same link on iPhone — Share → Add to Home Screen)
**Desktop app:** `desktop/` — an Electron shell that opens the live link (see desktop/README.txt).

## Layout

| Path | What it is |
|---|---|
| `src/app.jsx` | The whole app (React 18, JSX). Everything lives here. |
| `tools/build.py` | Turns `src/app.jsx` into one HTML page (JSX compiled with `tsc`, Tailwind CDN, pptxgenjs inlined). |
| `index.html`, `manifest.webmanifest`, `icon-*.png`, `version.json` | The built site that GitHub Pages serves. Regenerate with the build command — don't hand-edit. |
| `desktop/` | Electron `main.js` + `package.json` for the Windows/Mac wrapper. |
| `tests/` | Headless-Chromium checks (Playwright) with a mock Supabase (`sbmock.js`) and a mini-Tailwind generator (`twgen.py`) so the page renders offline. |
| `docs/` | Research report on payroll efficiency / Discord / payouts / invoices, the coaching guide, deploy notes. |
| `.github/workflows/pages.yml` | Deploys `index.html` to GitHub Pages on every push to `main`. |

## Build & deploy

```bash
# hosted build (this is what gets committed and served)
python3 tools/build.py src/app.jsx index.html --hosted --version 5.3.8 \
  --supabase https://ctsbigebqkyggntjevqq.supabase.co sb_publishable_2jC3tz_LgP3P-439fIjUMA_P36MN8Q0
git add -A && git commit -m "5.3.9: …" && git push
```

The publishable Supabase key is safe in the page (row-level security does the protecting). Bump `--version` each release — the app shows it in the sidebar and offers an "Update ready" bar to anyone on an older copy.

A plain standalone file (no accounts, local storage only): `python3 tools/build.py src/app.jsx SpicySweet-Payroll.html`.

## Tests

```bash
python3 tools/build.py src/app.jsx tests/build.html --supabase <url> <key>
python3 tests/test51.py tests/build.html   # accounts, invoices, send-out deck
python3 tests/test52.py                     # chatter + creator report imports
python3 tests/testmp.py                     # Messages Pro metrics + 70% flag
python3 tests/shots.py                      # screenshots of every view, desktop + phone
```
`smoke40.py` swaps the CDN scripts for local React + generated CSS so Chromium can run the page with no network. `tests/vendor/xlsx.full.min.js` is SheetJS for the import tests.

## Backend (Supabase project `ctsbigebqkyggntjevqq`)

Tables `config`, `profiles`, `app_state`, `weeks`; roles owner / coowner / manager / head / chatter; RLS so chatters only read their own slice via `my_slice()`. `guard_manager_settings` lists the settings keys managers may change (goals, roster, invoices, creator reports, reviewed checks — never pay rules or features). Owner email is set in `config.owner_email`. Supabase Auth → URL Configuration needs the Pages URL as Site URL and `…/**` as a redirect.

## Pay rules (as configured in the app; all adjustable in Settings)

Base $3/hr + 3% · T1 $750 → $3.50 + 4% · T2 $900 → $4 + 5% · T3 $1150 → $4.50 + 6% (per-shift revenue targets) · streaming +$1.50/hr · head chatter $40/wk · weekly goal $15 × 4, monthly $25 · podium $15/$10/$5, most improved $10, golden ratio $5 · strikes 2/4/6 · commission on net after the 20% platform cut, targets on gross · manager 3% of profit.

## Version history (highlights)

- 5.3 — themes (light/dim/night/midnight + custom background/accent/glow), glass cursor, sound library with per-event assignment, version stamp + update bar, phone shift cards, payroll checks you can tick off
- 5.2 — Infloww creator (biweekly) report import: model trends, team assignment, invoice drafting, goal recommendations; 0-hour sales merge into the previous shift; Messages Pro hours + 70% flag
- 5.1 — model invoice creator (INV-### layout), Send-out decks for paystubs and invoices, glass redesign
- 5.0 — Supabase accounts and roles, GitHub Pages hosting, desktop 5.0
- 4.x — app shell layout, cloud sync, Electron desktop, iPhone home-screen app
- 3.x — visual overhaul, goal recommendations, adjustments, week browser, attendance, history, P&L, roster, Discord template
