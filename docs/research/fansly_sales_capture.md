# Getting per-chatter Fansly PPV sales into a Supabase payroll app (Nov 2026)

## 1. Fansly data sources: official API, CSV export, per-chatter attribution, agency tools, unofficial API risk

### Takeaway
I found no evidence of an official public Fansly creator API or a native per-chatter attribution report. The usable paths are (a) Fansly's own Wallet/earnings views, exported via a third-party browser extension (FBuddy) as CSV, and (b) agency tools. Of the agency tools, OnlyMonster has Fansly account metrics with export, but its per-chatter attribution rules were documented as OnlyFans-only (the docs contradict themselves). Unofficial API/scraping is feasible but carries unquantified ToS/ban risk.

### Cited Findings
- FBuddy (browser extension) can download Fansly Wallet History as CSV with columns Date, Status (Pending/Approved/Canceled/Refunded), Order Number, Description (tips, subscription, media, bundle, stream ticket, referral), Total. There is no chatter column, and fan names can show "Unknown". It runs in the creator's logged-in browser on Earnings > Wallet > History. — [FBuddy docs](https://docs.fbuddy.net/features/download-wallet-history-csv)
- OnlyMonster Accounts Overview supports Fansly accounts: revenue, transactions, spenders, APV per account, and Fansly tracking-link revenue (FYP, Search, Suggestions). Export as CSV/XLSX. New accounts sync within 6 hours, then hourly. The page does not break down by chatter. — [OnlyMonster Fansly accounts overview](https://docs.onlymonster.ai/management-system/accounts-overview-fansly)
- OnlyMonster chatter metrics: attribution rules per transaction type (message sender, last active member within a 1 min–12 h window, "cents fingerprint", or unassigned); mass messages cannot be auto-attributed; changes are not retroactive; Team Metrics and My Metrics export to CSV/XLSX (member/account columns show IDs). The page is inconsistent on Fansly: intro says OnlyFans and Fansly, but Sales Settings says "OnlyFans is the only platform available at the moment." — [OnlyMonster Chatter Metrics](https://docs.onlymonster.ai/management-system/chatter-metrics)
- Usly (Fansly analytics tool): Fansly supported, per-creator breakdown, "Export CSV" of tables, subscriber figures labelled "Estimated" from Fansly aggregated data, a few hours lag; no per-chatter breakdown described. — [Usly help](https://intercom.help/usly-1422d0f4f655/en/articles/14470513-creator-analytics)
- A secondary blog lists Infloww and CreatorXOne as CRM options for Fansly agencies, mentions per-chatter performance tracking only generically, and describes no data export or Fansly API. It says Fansly has native employee access controls. This is a low-quality secondary source. — [Sozee](https://sozee.ai/resources/best-fansly-agency-management-tools)
- Unofficial Fansly scrapers exist (Apify actors such as Fansly Profile Scraper), which suggests an undocumented web API is reachable, but those are public-profile scrapers, not earnings access. — [Apify Fansly scraper](https://apify.com/dev00/fansly-scraper.md)
- A reviewer of the Fansly ToS (terms.law) did not address automation, bots or third-party access; it only notes the general suspend/terminate clause. I did not read the primary ToS. — [terms.law Fansly review](https://terms.law/ToS-Watchdog/creator-platforms/fansly/)
- Fanvue (a different platform) does publish an agency API with an earnings summary endpoint, which is a contrast and not applicable to Fansly. — [Fanvue API](https://api.fanvue.com/docs/api-reference/reference/agencies/get-creator-earnings-summary)

### Inferences
- Even where tools export Fansly data, Fansly's own earnings are per model account, not per chatter. Per-chatter attribution has to come from the chatters (self-report/Discord) or heuristics (OnlyMonster-style last-active-chatter or cents fingerprint, which appear OnlyFans-only). Cents-fingerprint (assigning each chatter a unique cents value on PPV prices) is a cheap trick you could copy manually on Fansly if prices are set by the chatter, but that is my idea, not a documented Fansly feature.
- The realistic reconciliation source is the FBuddy Wallet CSV (or Fansly's own earnings screen) per model, compared with the sum of chatter-reported sales. Fansly Wallet "Description" is per transaction type, so PPV (media) can be filtered from tips and subscriptions.
- Using an unofficial API with a creator's session token means sharing credentials and acting as automation. Risk is unquantified, so I would rank it last.

### Gaps
- No primary Fansly source found confirming or denying an official creator/agency API. Fansly help center and ToS text were not fetched (search surfaced no direct help-center page).
- Could not confirm Infloww, Supercreator, Fanshub, or CreatorHero Fansly per-chatter attribution/export; search results were marketing/aggregator pages. Verify in each vendor's docs or with a trial.
- No primary-source ToS clause on automation or third-party access.
- FBuddy CSV has no fan or chatter field, and whether it includes PPV message sales (vs. only "media") was not verified.

## 2. Discord-side capture: slash command/modal via Edge Function, and message reading

### Takeaway
A Supabase Edge Function can serve as the Discord Interactions endpoint (Ed25519 verification, deployed with JWT verification off), so `/sale` or a modal needs no always-on server. Reading free-text channel messages requires the privileged Message Content intent (or an on-demand REST fetch, which has the same content restriction), so structured slash commands and modals are the better fit, since they work without that intent.

### Cited Findings
- Official Supabase example: Edge Function using TweetNaCl to verify `X-Signature-Ed25519` and `X-Signature-Timestamp` over timestamp+raw body with the `DISCORD_PUBLIC_KEY` secret; returns 401 on failure; type 1 (PING) -> type 1 (PONG); type 2 (application command) -> type 4 response; deployed with `supabase functions deploy discord-bot --no-verify-jwt`; the secret set via `supabase secrets set`; the command is registered via a POST to `/applications/{CLIENT_ID}/commands` with the bot token. — [Supabase Discord bot guide](https://supabase.com/docs/guides/functions/examples/discord-bot.md)
- Message Content intent is required to read `content`, `embeds`, `attachments`, `components`, `poll` of messages the app receives, except messages the app sends, DMs to the app, messages that @mention the app, and replies to the app's messages. Without it you still get slash commands (string/integer/user/channel/role/attachment options), message context-menu commands (which receive the full message object when invoked), buttons/select menus, and modals with text inputs. Apps under 10,000 servers-installed-users can toggle privileged intents in the Developer Portal. — [Discord: you might not need a privileged intent](https://docs.discord.com/developers/gateway/you-might-not-need-a-privileged-intent.md)
- Slash commands support an attachment option type, so `/sale amount model screenshot` can carry a screenshot without the intent. — same Discord page
- Message context-menu commands: a head chatter or owner could right-click an existing screenshot message and run "Log sale" to capture that message's content/attachments without the intent. — same Discord page
- Make's Discord module: with Make's verified bot, Watch Channel Messages/List Channel Messages return empty content/embeds/attachments for member messages; a custom bot with the Privileged Intent enabled is needed. — [Make Discord app docs](https://apps.make.com/discord.md)

### Inferences
- Design: `/sale amount:120 model:<choice> [screenshot:<attachment>]`, with `model` as a registered choices/autocomplete list and the chatter identified by `interaction.member.user.id` mapped to the app's chatter row (a one-time Discord ID link field in the profile). That removes parsing and the "who posted this" problem.
- From my general knowledge of Discord (not verified by a fetched page this session, verify): interactions must be acknowledged within 3 seconds (use deferred response type 5 plus a follow-up webhook if the DB write may be slow); the Interactions Endpoint URL is checked by Discord with signed PING and invalid-signature probes; Edge Function cold starts are usually fine but test. The channel-history REST `GET /channels/{id}/messages` needs the bot in the channel with View Channel + Read Message History, and returns empty content fields without the intent. With a small private server (the bot's owner toggling the intent in the portal) the intent is simply a switch, no review needed, per the under-10,000 note above. Gateway reading would need an always-on process (conflicts with the constraint), so on-demand history fetch from an Edge Function, e.g. a "Import from Discord" button, is the no-server alternative.
- The regex-parse approach ("name — $amount") is fragile to typos and screenshots-only posts; slash command/modal is better. A hybrid is possible: keep the current channel and have the bot reply on each post.

### Gaps
- Discord's Interactions docs page was not fetchable (allowlist), so the 3-second limit, modal payload shape, and endpoint-verification behavior are unverified here.
- Supabase Edge Function free-tier limits/invocation costs not checked.

## 3. In-app self-reporting with approval and anti-fraud

### Takeaway
No external source was needed for the core design; this is an app-side build on Supabase (table + RLS + Storage). Nothing found contradicts it. The Fansly-side check against the actual earnings report is the main fraud control.

### Cited Findings
- OnlyMonster's own model shows the precedent: transactions can be left "Unassigned" and assigned/reassigned manually later, and attribution changes are non-retroactive. This resembles a pending/approved workflow. — [OnlyMonster Chatter Metrics](https://docs.onlymonster.ai/management-system/chatter-metrics)

### Inferences (design suggestions from general knowledge, not from sources)
- Table `sales(id, chatter_id, model, amount_cents, sold_at, source 'app'|'discord'|'ocr', screenshot_path, status 'pending'|'approved'|'rejected', approved_by, approved_at, period_id)`. RLS: chatters insert/select own rows, and can update only while pending; only owner/head chatter role can set status. Payroll sums approved rows; once a pay period is closed, rows get `locked` and a trigger blocks edits.
- Storage private bucket with per-chatter path prefix policies, signed URLs for review. Require a screenshot on submit; store a hash (e.g. SHA-256 of the image) to detect duplicate screenshot reuse; add a unique constraint on (model, sold_at, amount) plus a soft-warning for duplicates.
- Both entry points (Discord command and app form) can write to the same table, so Discord becomes just another input.

### Gaps
- No source on Supabase RLS/Storage specifics was fetched this session (docs not fetched due to the tool budget).

## 4. Screenshot OCR fallback (Tesseract.js)

### Takeaway
Feasible in-browser but not reliable enough to be unattended; use it only to pre-fill the amount for human confirmation. I found no accuracy data specific to Fansly screenshots.

### Cited Findings
- General sources report OCR commonly drops or misreads decimal points and currency symbols, and character whitelisting (digits, `.`, `$`) is a standard mitigation in Tesseract. — [ImageToTable on decimals/currency errors](https://imagetotable.ai/blog/ocr-accuracy-by-field-type), [PyImageSearch whitelisting](https://pyimagesearch.com/2021/09/06/whitelisting-and-blacklisting-characters-with-tesseract-and-python/), [Tesseract mailing list on decimal recognition](https://groups.google.com/g/tesseract-ocr/c/xaRnYoSqSw8)
- Vendor-ish claim of "95% overall, 60% on fields that matter" accuracy in one OCR blog; a marketing source, treat with caution. — [ImageToTable](https://imagetotable.ai/blog/ocr-accuracy-by-field-type)

### Inferences
- Dark-mode UI, small fonts and screenshots of a phone screen would hurt accuracy; a misread like $120.00 vs $12000 is costly, so OCR should only suggest a value that the chatter confirms, with the screenshot kept as evidence. An alternative, which I did not research, is sending the image to a vision LLM from an Edge Function (cost/privacy trade-off, and sensitive-content considerations).

### Gaps
- No tests on Fansly screenshots; no Tesseract.js-specific benchmark found. Needs a quick 10-sample trial.

## 5. Reconciliation against Fansly's actual earnings

### Takeaway
Reconcile per model per pay period: sum of approved chatter-reported PPV sales vs. Fansly's Wallet History/earnings total for that model, and flag variance above a threshold.

### Cited Findings
- Fansly Wallet History CSV (via FBuddy) provides date, status, order number, description and total per transaction, so you can filter media/PPV rows and exclude Canceled/Refunded. — [FBuddy docs](https://docs.fbuddy.net/features/download-wallet-history-csv)
- OnlyMonster and Usly export per-account Fansly revenue as CSV/XLSX, hourly or a few hours lag. — [OnlyMonster](https://docs.onlymonster.ai/management-system/accounts-overview-fansly), [Usly](https://intercom.help/usly-1422d0f4f655/en/articles/14470513-creator-analytics)

### Inferences
- Add an owner-only "Reconcile" screen: upload the model's CSV (parsed client-side), compare totals (and ideally per-transaction matching on timestamp+amount, ±few minutes) against approved chatter sales; show matched, unmatched-chatter-claims (possible fraud/typos), and unclaimed Fansly sales (nobody reported; unattributed revenue). Pending/Refunded status handling matters since Fansly shows Pending/Canceled/Refunded.
- Per-transaction match is what also catches inflated individual claims; totals alone only catch aggregate mismatch.

### Gaps
- Whether the Wallet CSV includes net or gross amounts (after Fansly's fee) and the timezone is not confirmed ("device local date/time" per FBuddy), so normalize before comparing.

## 6. No-code bridges (Zapier/Make) and cost

### Takeaway
They work only with a custom bot with the Message Content intent enabled; they poll rather than push, and add recurring cost, with little advantage over the Edge Function approach.

### Cited Findings
- Make has Discord "Watch Channel Messages" (with a Limit per cycle); with Make's verified bot, member message content/attachments return empty, so you need your own bot token with the privileged intent. The polling interval is not specified in the doc. — [Make Discord docs](https://apps.make.com/discord.md)
- Community threads report Make's Discord channel-watch trigger sometimes not firing. — [Make community](https://community.make.com/t/discord-watch-channel-messages-is-not-triggering/12071.md)
- Zapier and Pipedream have Discord-to-Supabase templates/integrations (existence only). — [Zapier template](https://zapier.com/templates/details/0f13da655a01196217f39dbaaae10c316350d110c49b2c05d94fd3c05ddd9926), [Pipedream](https://pipedream.com/integrations/select-row-with-supabase-api-on-new-message-in-channel-from-discord-bot-api-int_Vyseg4P)

### Inferences
- A regex/LLM parser step in Make would still be needed for free text; slash-command via Edge Function is cheaper and more reliable.

### Gaps
- Current Make/Zapier pricing was not retrieved (search returned no pricing pages); check before relying on them.

## Ranked options by effort (synthesis)
1. Lowest effort: Discord `/sale` slash command (+ optional attachment) -> Edge Function -> `sales` table as pending; owner approves in app. No privileged intent needed.
2. Add in-app "Log sale" form with required screenshot (same table), approval/lock workflow.
3. Reconciliation screen with Fansly Wallet CSV upload per model (FBuddy or OnlyMonster/Usly export).
4. Optional: Tesseract.js amount pre-fill; on-demand channel-history import (needs privileged intent).
5. Agency tool with per-chatter Fansly attribution — unverified; OnlyMonster's documented attribution is OnlyFans-only.
6. Last/avoid: unofficial Fansly API with creator session tokens — ToS/account-risk unquantified.
