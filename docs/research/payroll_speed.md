# Speeding up the weekly chatter-payroll run (Spicy Sweet): data sources, bulk entry, validation, distribution

## 1. Where do agencies get hours and sales data (Infloww, Supercreator, Fanshub, CreatorHero, OnlyMonster)? Can the app import a CSV or pasted table?

### Takeaway
The OFM tools expose per-chatter revenue and activity time inside their dashboards, and most advertise CSV/Excel export, but none of the vendor docs I could reach publish CSV column names or a public API. The realistic route is a column-mapped CSV/paste import that tolerates whatever headers each tool emits.

### Cited Findings
- OnlyMonster has a Data Export feature. Exportable types for OnlyFans are Trial Links, Tracking Links, Fan Notes, Message Templates, Transactions, Message Tracker and Chargebacks. For Fansly they are Fan Notes and Transactions. Output is CSV or XLSX, and files stay downloadable for 31 days. The page does not list file columns, mention chatter sales/hours reports, or describe an API. — [OnlyMonster docs](https://docs.onlymonster.ai/management-system/data-export)
- CreatorHero's "Chatter Tracking" page: the All Chatters table shows Active Time (time engaging fans), Inactive Time (logged in, no activity) and Total Revenue per chatter. Table data can be exported as CSV or Excel. Payroll and API are not mentioned. — [CreatorHero help](https://help.creatorhero.com/en/articles/10426384-chatter-tracking)
- Supercreator's chatter management page says it monitors each chatter's sales every shift and tracks hours worked/online, sign-ins, sign-outs and disconnects. It says it can "simplify commission calculations and payouts" and offers per-chatter exports for commissions, with daily per-chatter numbers per page. API is not mentioned. — [Supercreator](https://www.supercreator.app/onlyfans-crm/chatter-management)
- A third-party roundup says Infloww has shift-level reporting (response-time averages, QA scoring), priced from $30/creator/month. The same source says platforms lacking chatter-level revenue attribution leave pay decisions as guesswork. It does not cover exports or API for any tool. This is a marketing-style blog, so treat it as weak. — [ofm-course tech stack](https://ofm-course.pages.dev/blog/chatting-sales-tools-tech-stack-2026/)
- A second roundup says nothing about exports, API, payroll or shift tracking for Infloww, Supercreator or OnlyMonster, and does not mention CreatorHero or Fanshub. — [forgeflow](https://forgeflow.pages.dev/blog/best-onlyfans-agency-tools-2026)
- Papa Parse parses a CSV/TSV string client-side with `Papa.parse(str, config)`. With `header: true`, each row becomes an object keyed by header name and `meta.fields` lists the headers. Leaving `delimiter` blank auto-detects from comma, tab, pipe, semicolon and two ASCII separators. `skipEmptyLines: true` or `'greedy'` drops blank rows. `dynamicTyping: true` converts numbers. — [Papa Parse docs](https://www.papaparse.com/docs)

### Inferences
- Since the same Papa Parse call handles a CSV file and text pasted from Excel/Sheets (tab-delimited), one "Import" dialog can accept both drag-drop and paste.
- Because column names are undocumented and likely differ per vendor, the import needs a mapping step. Fuzzy-match headers (e.g. contains "chatter"/"employee"/"name", "revenue"/"sales"/"gross"/"net", "hours"/"active time"), then ask the owner to confirm. Save the mapping in Supabase or localStorage keyed by source tool so it is one click from week 2 on.
- Match chatter names to roster records via a stored alias table (vendor display name, Discord handle, legal name). Show unmatched rows for a one-time alias assignment.
- Key risk: the exports may show gross vs net revenue and per-creator-page rows. Importing must therefore aggregate rows by chatter and let the owner pick the revenue column (gross vs net), since the tier thresholds ($750/$900/$1150) depend on the app's definition.
- CreatorHero "Active Time" is activity time, which may not equal paid shift hours. Hours should likely come from the roster/schedule, with tool activity time used only as a cross-check.

### Gaps
- No CSV column names found for Infloww, Supercreator, CreatorHero, OnlyMonster or Fanshub; the vendor help pages that would list them were not reachable or did not include them.
- No evidence found of public APIs for any of these tools. Fanshub documentation was not surfaced at all. Verify directly in each vendor's dashboard by downloading one sample export.
- Infloww's own help center was not retrieved; Infloww claims rest on a third-party blog.

## 2. Fastest UX for bulk entry in a single-file React web app, and suitable small libraries

### Takeaway
Pasting a table copied from a spreadsheet or tool, with a header-mapping and preview step, is the single biggest win. A keyboard-navigable grid plus "copy last week" prefill covers the remainder. react-datasheet-grid supports Excel/Sheets paste and full keyboard navigation out of the box.

### Cited Findings
- react-datasheet-grid (v4.11.4, TypeScript, maintainer nick-keller) is an Airtable/Excel-like grid. It supports copy and paste to and from Excel and Google Sheets, fully supported keyboard navigation and shortcuts, drag-to-expand selection and a custom context menu. Unpacked size is 311 kB. The fetched page did not state the license. — [npm: react-datasheet-grid](https://www.npmjs.com/package/react-datasheet-grid)
- Papa Parse offers auto-detected delimiters, header-keyed rows, and per-row error reporting for rows whose field count mismatches the header. — [Papa Parse docs](https://www.papaparse.com/docs)
- A 2026 comparison page of grid options exists (TanStack Table vs AG Grid vs React Data Grid) but I did not fetch it, so no claims from it are made. — [pkgpulse](https://www.pkgpulse.com/guides/tanstack-table-vs-ag-grid-vs-react-data-grid-2026)

### Inferences
- Ranked by expected time saved for a 14-chatter roster:
  1. Paste-table importer: `textarea` onPaste -> `Papa.parse(text, {header:true, skipEmptyLines:'greedy'})` -> mapping UI -> preview table with matched/unmatched chatters -> "Apply". No library beyond Papa Parse is needed.
  2. CSV drag-drop on the same dialog: `Papa.parse(file, {...})`; files never leave the browser.
  3. Copy-last-week prefill: copy last week's hours per chatter (and shift slot assignments) into this week's draft, so the owner edits only deviations.
  4. Roster-based auto hours: if each chatter has a default weekly shift pattern (3 daily 8-hour slots), compute hours automatically and let the owner mark only absences/swaps. A subtraction workflow (mark exceptions) is much faster than 14 manual typings.
  5. A lightweight editable grid for residual edits: either react-datasheet-grid (about 311 kB unpacked, so check the minified bundle) or a hand-rolled table of `<input>`s with Enter/Tab/arrow handlers. For ~14 rows x ~4 columns (hours, sales, adjustments, strikes), a hand-rolled grid is likely lighter than adding a dependency in a single-file app. Handle `onPaste` per cell by splitting on `\n` and `\t` to fill down/right.
- For a single-file React app loaded via CDN/ESM, Papa Parse (small, dependency-free) is the easiest addition. The grid library choice depends on whether the file is bundled; verify licenses (react-datasheet-grid license not confirmed here; handsontable is commercial for non-personal use and glide-data-grid is canvas-based, both from memory and unverified, so likely overkill).
- Persist import drafts in Supabase (a `payroll_drafts` row per week) so an interrupted run resumes.

### Gaps
- Licenses and minified/gzip sizes not verified for react-datasheet-grid, react-data-grid, glide-data-grid, or Handsontable.
- No evidence gathered on whether any of these work well when loaded via a script tag/ESM CDN in a single HTML file.

## 3. How agencies track chatter hours (Hubstaff, Clockify, Discord clock-in bots, Infloww shift tracking) and browser reachability

### Takeaway
Clockify exposes a REST API with key-based auth and a Detailed Report endpoint, which could feed hours automatically. A browser call is at risk from CORS and from exposing the API key, so a Supabase Edge Function proxy is the safer route. I found no sourced evidence on Discord clock-in bot exports or Hubstaff API details.

### Cited Findings
- Clockify API auth is via an `X-Api-Key` (or `X-Addon-Token`) header; workspaces on a subdomain need a workspace-specific key from Profile Settings. — [Clockify docs](https://docs.clockify.me/)
- Clockify's Detailed Report is a POST at `https://reports.api.clockify.me/v1/workspaces/{workspaceId}/reports/detailed`; regional/subdomain variants use `/report/v1/...`. — [Clockify docs](https://docs.clockify.me/)
- Clockify rate limits per workspace for X-Api-Key: FREE 30 requests per hour; TRIAL/BASIC/STANDARD/PRO 20 per second; ENTERPRISE 50 per second. — [Clockify docs](https://docs.clockify.me/)
- A Clockify marketplace developer forum thread titled "Detailed Reports API throws CORS error in PROD" exists, indicating browser calls to the reports API can hit CORS errors (I only saw the title, not the resolution). — [Cake/Clockify dev forum](https://dev-forum.marketplace.cake.com/t/detailed-reports-api-throws-cors-error-in-prod/93)
- Supercreator and CreatorHero track sign-in/sign-out and active/inactive time themselves (see section 1), so tool-native activity time could replace a separate time tracker. — [Supercreator](https://www.supercreator.app/onlyfans-crm/chatter-management), [CreatorHero](https://help.creatorhero.com/en/articles/10426384-chatter-tracking)

### Inferences
- A Supabase Edge Function (Deno) could hold the Clockify key as a secret, call the Detailed Report API for the week's date range, aggregate hours per user, and return JSON to the static app. This avoids CORS and key exposure. Authenticate the function with the Supabase user's JWT so only the owner can call it.
- A Discord clock-in alternative with no extra tool: a slash-command bot (or a button in a clock-in channel) writes rows to a Supabase `shifts` table (chatter_id, start, end, slot) via an Edge Function; the app then sums hours per week with a single SQL query/view. This removes hour typing entirely, at the cost of building and maintaining the bot.
- A cheaper step before any integration: ask chatters to post hours in a fixed format in a Discord channel, and let the app paste-parse that export. Lower fidelity, no infra.
- Clockify's free-tier limit (30 requests/hour) is fine for one weekly pull.

### Gaps
- Hubstaff API details (auth, CORS, plan requirements) not retrieved.
- Nothing sourced about Discord clock-in bots' export formats; the Discord-bot design above is my own inference.
- The Clockify CORS thread's resolution was not read; whether the Reports API allows browser origins is unconfirmed.
- Infloww shift tracking export/API unconfirmed.

## 4. Validation and review steps that catch errors fast

### Takeaway
No sourced material on payroll anomaly rules for chatter agencies was found; the rules below are design proposals derived from the pay structure in the brief and are cheap to implement as pure functions over the draft.

### Cited Findings
- Papa Parse surfaces row-level problems itself: rows whose field count differs from the header produce errors, duplicate headers are renamed and recorded in `meta.renamedHeaders`, and extra cells land in `__parsed_extra`. These can feed an import-error list directly. — [Papa Parse docs](https://www.papaparse.com/docs)
- A third-party blog says platforms without chatter-level revenue attribution leave pay decisions guesswork, supporting cross-checking per-chatter sales against the tool's own totals. — [ofm-course tech stack](https://ofm-course.pages.dev/blog/chatting-sales-tools-tech-stack-2026/)

### Inferences
- Flag rules (all computed client-side, shown as a sortable "review" column with severity, blocking only on errors):
  - Hours > 56 (7 x 8h) or more than the roster allows (3 slots x 8h x scheduled days); hours = 0 with sales > 0; sales > 0 but no scheduled shifts.
  - Sales outliers: week-over-week change beyond a threshold (e.g. > +/-60%) or z-score vs the chatter's last 8 weeks; sales per hour far above/below team median.
  - Missing data: roster chatter with no row, or an imported row with no matching chatter (alias needed); duplicates.
  - Tier-boundary proximity: sales within a few dollars below $750/$900/$1150 of a tier, so the owner double-checks the number that changes pay.
  - Reconciliation: sum of imported per-chatter sales vs the OFM tool's total for the creator pages; show the difference.
  - Pay sanity: total payout as a percent of team revenue vs the usual range; negative net pay after strikes/adjustments.
  - Diff view vs previous week: one table with last week's pay, this week's pay, delta.
- Add a "reviewed" checkbox per row and a summary count ("11 ok, 2 warnings, 1 error"). The owner reviews only flagged rows.

### Gaps
- No external evidence or benchmarks for thresholds; all numbers are suggestions to be tuned on Spicy Sweet's history.

## 5. Distribution shortcuts: one-click send, batch PDF, scheduled Monday run, reminders

### Takeaway
Everything can run browser-side except unattended scheduling and Discord posting with a secret webhook, which need a Supabase Edge Function (plus pg_cron). I did not fetch docs for these in this pass, so the technical specifics below are inferences and flagged for verification.

### Cited Findings
- Supercreator markets per-chatter exports for commissions and downloadable insights, indicating per-chatter statements are a normal artifact in the tooling category. — [Supercreator](https://www.supercreator.app/onlyfans-crm/chatter-management)

### Inferences
- Batch export: loop over chatters and render each paystub to PDF/PNG, then bundle into one ZIP (JSZip) for a single download. The app already produces PDF/PNG/XLSX/PPTX individually, so adding a "Download all (ZIP)" button and a combined single PDF is a small change. Render sequentially to avoid memory spikes.
- Discord distribution: a Discord channel webhook (HTTP POST with multipart file attachments) can post the announcement plus paystub files in one request (up to 10 files per message), but calling the webhook from the browser exposes its URL; put it behind a Supabase Edge Function. Per-chatter DMs would need a bot token (also server-side). These Discord specifics are from memory and not verified here.
- Scheduling: Supabase pg_cron can invoke an Edge Function on a schedule (e.g. Monday morning) to (a) pull hours from Clockify/the shifts table, (b) create a draft payroll week, and (c) post a Discord reminder to the owner "draft ready, N flags". Full unattended payout is not recommended; keep a human approval click. Verify pg_cron/Edge Function scheduling in the Supabase docs.
- A "Publish week" button should lock the week (immutable snapshot row), generate all stubs, and post the announcement, so the whole distribution step is one click plus a confirmation.
- Chatter-facing reminder: before the run, an automated Discord message asking chatters to submit/confirm hours by a cutoff reduces back-and-forth.

### Gaps
- No Discord webhook, Supabase pg_cron or JSZip docs were fetched; limits (file sizes, rate limits) are unverified.

## 6. Evidence on how long a weekly payroll run takes for small agencies and the biggest time sinks

### Takeaway
I found no credible, sourced measurement of weekly payroll time for small OFM agencies. The only adjacent figure is a vendor-blog claim about chatter admin time, which is not about payroll.

### Cited Findings
- One vendor-style blog says chatters can lose 30-40% of a shift to admin work that software should handle. This is about chatter shifts, not owner payroll, and is an unsupported marketing claim. — [ofm-course tech stack](https://ofm-course.pages.dev/blog/chatting-sales-tools-tech-stack-2026/)
- The same blog mentions manual exports of OnlyFans data as part of the status quo for some tools, consistent with export/re-entry being a manual step. — [ofm-course tech stack](https://ofm-course.pages.dev/blog/chatting-sales-tools-tech-stack-2026/)

### Inferences
- Likely time sinks for this app, by reasoning from the brief (not measured): (1) retyping ~14 chatters' hours and sales, (2) chasing missing/disputed hours, (3) re-checking tier maths and bonuses, (4) generating and posting each paystub in several formats, (5) writing the Discord announcement. Items 1, 4 and 5 are automatable; item 2 is addressed by roster/clock-in data; item 3 by validation.
- The owner should time one run by section for a baseline (a simple stopwatch log in the app: start/stop per stage) to see where to invest first.

### Gaps
- Searches for Reddit/YouTube owner accounts of payroll time returned only generic agency guides; none gave payroll-time figures. Reddit and YouTube content was not directly reachable.
- No benchmark found for typical weekly payroll duration at agencies with ~14 chatters.
