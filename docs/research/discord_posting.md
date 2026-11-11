# Posting to Discord from a static React app on GitHub Pages with Supabase as the only backend (research as of Nov 2026)

Method note: about 17 tool calls. Several discord.com URLs were blocked by the fetch allowlist, so docs.discord.com mirrors were used. Items that could not be confirmed from a fetched source are listed under Gaps rather than stated as fact.

## 1. Discord webhooks: capabilities, CORS, rate limits, editing, DMs

### Takeaway
A webhook can post content, up to 10 embeds, multipart files, mentions, and thread posts (thread_id). It can also edit its own earlier message via PATCH, so a leaderboard can update in place. Webhooks are channel-scoped, and the docs describe no DM use. Direct browser calls appear to work in practice, but Discord's docs say nothing about CORS and community reports conflict, so a browser-only design is fragile and also leaks the secret URL.

### Cited Findings
- Execute Webhook is `POST /webhooks/{id}/{token}`. Query params: `wait` (return the created message; needed to get the message id for later edits), `thread_id` (post into a thread in the webhook's channel; the thread is auto-unarchived), `with_components`. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Body fields: `content` (max 2000 chars), `username`, `avatar_url`, `embeds` (max 10), `allowed_mentions`, `components`, `files[n]` (multipart/form-data), `payload_json` (required only for multipart), `attachments`, `flags`, `thread_name` and `applied_tags` (forum/media channels only), `poll`. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- At least one of content, embeds, components, file, or poll is required. For forum/media channels you must supply `thread_id` or `thread_name`. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Only `SUPPRESS_EMBEDS`, `SUPPRESS_NOTIFICATIONS`, and `IS_COMPONENTS_V2` flags can be set by webhooks. `SUPPRESS_NOTIFICATIONS` is useful for a silent leaderboard refresh. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Edit: `PATCH /webhooks/{id}/{token}/messages/{message_id}` with optional `thread_id` and `with_components` query params. Body accepts content, embeds, flags, allowed_mentions, components, files, payload_json, attachments. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Edit file behavior: new files are appended. In API v10, `attachments` must list every attachment to keep, including old and new ones. Editing `content` recomputes the mention arrays. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Non-application-owned webhooks (plain channel webhooks) can use only non-interactive components, and only when `with_components=true`. Application-owned webhooks can use all components. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- The webhook doc page contains no statements about DMs. Webhooks are described as tied to `channel_id`/`guild_id`. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Rate limits: global limit is 50 requests per second per bot (per IP when there is no Authorization header). Per-route limits are calculated per top-level resource, and webhooks are a top-level resource keyed by webhook id (+ token). Docs say not to hard-code limits and to read `X-RateLimit-*` headers. — [Discord rate limits](https://docs.discord.com/developers/topics/rate-limits.md)
- 429 body contains `message`, `retry_after` (float seconds), `global` (bool). Use `Retry-After` / `retry_after`. — [Discord rate limits](https://docs.discord.com/developers/topics/rate-limits.md)
- If a webhook returns 404 the app should stop using it; repeated attempts lead to a temporary restriction. IPs exceeding 10,000 invalid (401/403/429) requests per 10 minutes are temporarily blocked. — [Discord rate limits](https://docs.discord.com/developers/topics/rate-limits.md)
- CORS: Discord's rate-limit docs do not mention CORS. A dev.to article calls webhooks from browser `fetch` with no backend, but also reports that Discord "seems to selectively not return the needed CORS headers for TLDs that it does not like", and the author's comment suggests `mode: 'no-cors'` (opaque response, so you cannot read the message id). — [dev.to contact-form article](https://dev.to/mistval/discord-webhook-powered-contact-form-3lk6). Several forum threads report CORS errors too (not opened): [Glitch forum](https://support.glitch.com/t/discord-webhook-cors-error/56403).
- Exposure risk: the same article warns that a webhook URL in frontend code lets a malicious actor spam the channel, though the URL can only send messages, not read or administer. It recommends a backend middleman for higher-risk situations. — [dev.to contact-form article](https://dev.to/mistval/discord-webhook-powered-contact-form-3lk6)

### Inferences
- Because `wait=true` is needed to receive the message id, and `no-cors` gives an opaque response, an in-place leaderboard edit needs a readable response. Either the browser gets CORS headers (not guaranteed by docs) or an Edge Function proxy makes the call. The proxy is the robust path.
- Store the leaderboard `message_id` (and `thread_id` if used) in a Postgres row. The first post creates the message, and later posts PATCH it, falling back to a new POST if Discord returns 404 (message deleted).
- Since the webhook docs describe only channel/thread targets, webhooks cannot DM. The paystub DM must come from a bot (section 2), or a private thread via bot.
- Sketch (browser, discouraged for prod):
```js
const fd = new FormData();
fd.append('payload_json', JSON.stringify({embeds:[{title:'Week 45 leaderboard', description:'...'}], allowed_mentions:{parse:[]}, attachments:[{id:0, filename:'board.png'}]}));
fd.append('files[0]', pngBlob, 'board.png');
const r = await fetch(`${WEBHOOK}?wait=true&thread_id=${tid}`, {method:'POST', body:fd});
const msg = await r.json();            // msg.id for later PATCH
// update: fetch(`${WEBHOOK}/messages/${msg.id}`, {method:'PATCH', ...})
```

### Gaps
- Exact per-webhook rate (commonly cited as about 5 requests per 2 seconds) was not confirmed on a fetched page; rely on headers.
- No authoritative Discord statement on CORS headers for webhook endpoints; evidence is anecdotal and conflicting. Not tested live.
- No explicit Discord sentence that "webhooks cannot DM" was fetched; conclusion is from the docs' channel-only model.

## 2. Bot via Supabase Edge Function: DMs, permissions, user-ID mapping, limits

### Takeaway
A bot token held in an Edge Function secret can open a DM (`POST /users/@me/channels` with `recipient_id`) and then post a message with embed and file. Discord warns against bulk-DM use and says DMs should start from a user action, so send paystubs only to opted-in chatters at a measured pace. A bot needs no privileged intent for outbound DMs (inference), but DMs only succeed if the user permits them.

### Cited Findings
- Create DM: `POST /users/@me/channels`, body `{recipient_id}`; returns the existing DM channel if one exists. — [Discord User resource](https://docs.discord.com/developers/resources/user.md)
- Discord warns: do not use this endpoint to DM everyone in a server; DMs should generally start from a user action; opening many DMs quickly may get the bot rate limited or blocked from opening new ones. — [Discord User resource](https://docs.discord.com/developers/resources/user.md)
- The User resource page does not mention a shared-server requirement. Community threads on error 50007 ("Cannot send messages to this user") attribute failures to users with DMs closed or no mutual server (secondary, not verified): [Latenode thread](https://community.latenode.com/t/why-cant-my-discord-bot-send-direct-messages-to-users/14023), [Muse issue](https://lightrun.com/answers/codetheweb-muse-error-50007-cannot-send-messages-to-this-user).
- Message send to the DM channel then uses the normal create-message route with `embeds`, `content`, and multipart `files[n]` + `payload_json`. Embed images use `attachment://filename.png`, and only .jpg/.jpeg/.png/.webp/.gif are supported for that. Default file limit is 20 MiB per file (Nitro/boost can raise it in some contexts). — [Discord Reference: Uploading Files](https://docs.discord.com/developers/reference.md)
- A PDF cannot be shown in an embed via attachment:// but can be attached as a file (inference from the image-only list above).
- Attachment CDN URLs are signed and expire, though Discord refreshes them when passed back in fields such as embed image url. Standard CDN endpoints are unsigned. — [Discord Reference: Uploading Files](https://docs.discord.com/developers/reference.md)
- Edge Function limits: 2 s CPU per request (async I/O not counted), 256 MB memory, 150 s idle request timeout, wall clock 150 s free / 400 s paid. — [Supabase Edge Function limits](https://supabase.com/docs/guides/functions/limits.md)
- Secrets: set via Dashboard or `supabase secrets set`, read with `Deno.env.get`; only Owner/Admin can create/delete production secrets; names cannot start with `SUPABASE_`; new secrets are picked up without redeploy. — [Supabase secrets](https://supabase.com/docs/guides/functions/secrets)
- Injected env: `SUPABASE_URL`, `SUPABASE_SECRET_KEYS`, `SUPABASE_PUBLISHABLE_KEYS`, `SUPABASE_JWKS`. — [Supabase secrets](https://supabase.com/docs/guides/functions/secrets)

### Inferences
- Setup: create an application in the Developer Portal, add a Bot, copy the token into `supabase secrets set DISCORD_BOT_TOKEN=...`, and invite the bot to the guild with OAuth2 `bot` scope (guild membership gives the shared server). Permissions needed in the guild: View Channel, Send Messages, Embed Links, Attach Files for channel posting, plus Create Private Threads / Send Messages in Threads if using private threads. No Message Content or Members intent is needed to send messages; listing guild members for a picker does need the Server Members privileged intent (GUILD_MEMBERS). These permission and intent statements come from general Discord knowledge and were not verified on a fetched page.
- Pacing: 50 paystub DMs fit within global limits, but add 1-2 s spacing and honor 429 `retry_after` because open-DM calls are the guarded action. With 2 s CPU per request and 150 s timeout, send in batches (for example one chatter per invocation, or a queue table processed by cron) and record per-chatter status.
- A private thread in a staff-only channel is an alternative to DMs that avoids closed-DM failures, but any member who can see the thread or has Manage Threads can read it, so it is weaker for pay privacy.
- Edge Function outline:
```ts
Deno.serve(async (req) => {
  const user = await verifyJwt(req);                 // supabase.auth.getUser(jwt)
  await assertOwner(user.id);                        // select role from profiles
  const { chatterId, payload_png_base64 } = await req.json();
  const { discord_id } = await getChatter(chatterId);
  const H = { Authorization: `Bot ${Deno.env.get('DISCORD_BOT_TOKEN')}` };
  const ch = await (await fetch('https://discord.com/api/v10/users/@me/channels',
     {method:'POST', headers:{...H,'Content-Type':'application/json'}, body: JSON.stringify({recipient_id: discord_id})})).json();
  const fd = new FormData();
  fd.append('payload_json', JSON.stringify({embeds:[{title:'Paystub', image:{url:'attachment://stub.png'}}], attachments:[{id:0,filename:'stub.png'}]}));
  fd.append('files[0]', new Blob([bytes],{type:'image/png'}), 'stub.png');
  const r = await fetch(`https://discord.com/api/v10/channels/${ch.id}/messages`, {method:'POST', headers:H, body:fd});
  if (r.status===429) { /* read retry_after, requeue */ }
  return Response.json({ok:r.ok, status:r.status});   // include CORS headers for GitHub Pages origin
});
```
- The browser renders the stub to PNG (canvas/html-to-image) or PDF and sends base64 or a Storage signed URL to the function, because the function has no DOM.

### Gaps
- The "bot can only DM users sharing a server" rule is supported only by community threads, not by a fetched official page.
- No fetched source for DM-specific rate-limit numbers; Discord only says bulk opening may be limited.
- Required bot permissions/intents were not confirmed on a fetched page.

## 3. Mapping chatters to Discord IDs (Supabase Auth Discord provider)

### Takeaway
Supabase supports Discord as an OAuth provider, and an identity's `provider_id` is the provider account ID, which for Discord is the user snowflake needed for DMs and mentions. Sign-in with Discord can therefore capture IDs automatically, with manual entry or a guild-member picker as fallbacks.

### Cited Findings
- Setup: create Discord application, add the Supabase callback `https://<project-ref>.supabase.co/auth/v1/callback` under OAuth2 redirects, enter Client ID/Secret in Dashboard > Authentication > Providers > Discord, then call `supabase.auth.signInWithOAuth({ provider: 'discord' })`. PKCE flows need `redirectTo` on the allow list and `exchangeCodeForSession`. — [Supabase: Login with Discord](https://supabase.com/docs/guides/auth/social-login/auth-discord)
- An identity's `provider_id` is the ID returned by the provider (for OAuth, the user's account at that provider); `identity_data` holds provider profile info for OAuth. A user can have multiple identities. — [Supabase Identities](https://supabase.com/docs/guides/auth/identities)
- Discord's `identify` scope returns the user object without email; the `email` scope adds email. — [Discord User resource](https://docs.discord.com/developers/resources/user.md)
- Identity linking exists for adding Discord to an existing (e.g. email) account: [Supabase Identity Linking](https://supabase.com/docs/guides/auth/auth-identity-linking.md) (listed in search; not opened).

### Inferences
- Flow: chatters sign in or link Discord, the app reads `user.identities.find(i => i.provider==='discord').provider_id` (or `identity_data`), and a database trigger or the app copies it into `chatters.discord_id`. Since `provider_id` is the snowflake, mentions are `<@${discord_id}>`.
- If chatters do not have app logins, the owner can paste IDs (Developer Mode > Copy User ID) or use a bot-backed picker (`GET /guilds/{id}/members/search?query=`, which needs the Server Members intent). Validate pasted IDs by attempting a test DM.
- Client-supplied IDs must not be trusted for authorization. Take the ID from the server-verified identity, not from a writable user_metadata field.

### Gaps
- The exact keys inside Discord `identity_data` / `user_metadata` (for example full_name, avatar_url, custom_claims) were not confirmed on a fetched page; check a test sign-in. Whether `provider_id` equals the Discord snowflake is stated generically by Supabase, not Discord-specifically.
- Default scopes Supabase requests for Discord (identify/email) were not confirmed.

## 4. Secret handling: webhook URL and bot token

### Takeaway
Never ship a webhook URL or bot token in the GitHub Pages bundle. Put them in Edge Function secrets and expose a function that verifies the caller's Supabase JWT and checks an owner role before posting.

### Cited Findings
- A webhook URL in frontend code can be reused by anyone to spam the channel. — [dev.to](https://dev.to/mistval/discord-webhook-powered-contact-form-3lk6)
- Edge Function secrets (Dashboard or CLI) are read with `Deno.env.get`; only Owner/Admin may change production secrets, and Developers can view them. — [Supabase secrets](https://supabase.com/docs/guides/functions/secrets)
- For cron callers, store project URL and secret key in Supabase Vault via `vault.create_secret(...)` and read from `vault.decrypted_secrets`. Caveat from Supabase: any login-capable DB role may read the secret key while the request is pending because pg_net writes the decrypted key to `net.http_request_queue`. — [Supabase: Schedule Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions)
- Discord: if a webhook returns 404, stop using it. Rotating or deleting a leaked webhook ends abuse. — [Discord rate limits](https://docs.discord.com/developers/topics/rate-limits.md)

### Inferences
- Pattern: the browser calls `supabase.functions.invoke('discord-post', {body})`, which sends the user JWT automatically. The function validates it (default `verify_jwt`), looks up `profiles.role = 'owner'`, then calls Discord. Rate-limit per user, sanitize `allowed_mentions` (set `parse: []` and explicitly list users) to prevent @everyone injection, and never accept a raw webhook URL from the client.
- Keep the webhook URL in secrets, or in a Vault/Postgres table readable only by the service role, if the owner needs to configure it in-app.
- Set CORS headers in the function for the GitHub Pages origin (handle OPTIONS). This is standard Edge Function practice (not fetched).

### Gaps
- No fetched source for Vault versus Edge Secrets recommendations beyond the above; Vault read via SQL needs the service role.

## 5. Embed and Components v2 limits; images

### Takeaway
Classic messages allow 2000-char content and 10 embeds. Components V2 is available for new messages but disables content/embeds/polls and is irreversible for that message. Use embeds for leaderboards unless a richer layout is needed.

### Cited Findings
- Content up to 2000 chars; up to 10 embeds per message. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Components V2: flag `1<<15` (32768), cannot be removed once set; up to 40 total components; `content` and `embeds` stop working and `poll` and `stickers` are disabled. Types: Container (17, accent_color), Section (9, 1-3 text displays plus Button/Thumbnail accessory), Text Display (10, markdown, mentions ping per allowed_mentions), Media Gallery (12, 1-10 items), File (13, `attachment://` only), Separator (14). — [Discord Components reference](https://docs.discord.com/developers/components/reference)
- Webhook rule: with IS_COMPONENTS_V2, only `components` allowed; adding content/embeds/files/poll gives 400. Switching an existing message to V2 requires nulling content/embeds/files/poll first. Plain webhooks need `with_components=true` and are limited to non-interactive components. — [Discord Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Discord says legacy message component behavior will not be deprecated; new components are recommended for new projects. — [Discord Components overview](https://docs.discord.com/developers/components/overview)
- Embed images: hosted URL, or `attachment://name.png` for an uploaded file (image formats only). — [Discord Reference: Uploading Files](https://docs.discord.com/developers/reference.md)

### Inferences
- Files attached in a V2 message must be shown through a File or Media Gallery component using `attachment://`, because the `files[n]` field is rejected on webhook V2 sends per the webhook rules above (webhook doc says files[n] cannot accompany the flag; verify for bot sends).
- Embed field limits from memory (title 256, description 4096, 25 fields, field name 256 / value 1024, footer 2048, author 256, 6000 total across an embed set) were not confirmed on a fetched page because the message resource fetch was blocked. Treat as widely documented but unverified here.
- Leaderboard in one embed: a code-block table in the description (4096 chars) is more reliable than fields, and stays under the 6000 cap.
- UX: "Post leaderboard" and "Update this week's post" buttons; show last-posted time and a link to the message; preview of the embed in-app; a per-chatter send status (Sent / DMs closed / Failed) with a retry button; a confirmation modal before sending pay data.

### Gaps
- Text Display character limit and total V2 payload size not stated in fetched content.
- Embed numeric limits unverified (see above).

## 6. Scheduling auto-posts (Monday)

### Takeaway
Supabase pg_cron plus pg_net can invoke an Edge Function on a schedule, using Vault for the project URL and a secret key.

### Cited Findings
- Hosted Supabase supports pg_cron, and pg_net can call Edge Functions on schedule. The example job `invoke-function-every-minute` uses `net.http_post` against `/functions/v1/function-name` with JSON headers, an `apikey` header, and a body. — [Supabase: Schedule Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions)
- Use the secret key, not the publishable key. The function should disable `verify_jwt` and set `auth: 'secret'` to accept it. — [Supabase: Schedule Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions)
- Edge Function limits (2 s CPU, 150 s request timeout) apply to scheduled invocations too. — [Supabase Edge Function limits](https://supabase.com/docs/guides/functions/limits.md)

### Inferences
- SQL shape (cron is UTC, so choose the hour for the community's timezone):
```sql
select cron.schedule('weekly-leaderboard', '0 14 * * 1',
 $$ select net.http_post(
      url := (select decrypted_secret from vault.decrypted_secrets where name='project_url') || '/functions/v1/discord-post',
      headers := jsonb_build_object('Content-Type','application/json','apikey',(select decrypted_secret from vault.decrypted_secrets where name='secret_key')),
      body := jsonb_build_object('kind','leaderboard')) $$);
```
- The function computes the leaderboard from Postgres server-side, then POSTs the first message of the week or PATCHes the stored message id. Browser-rendered PNGs are not possible on a schedule, so scheduled posts should use text/embed content (or server-side image generation).
- Paystub DMs probably should stay manual (owner clicks "Send"), consistent with Discord's guidance that DMs start from a user action.

### Gaps
- Timezone/DST handling for pg_cron was not researched. pg_net response retention and failure alerting not researched.

## 7. No-code bridges (Zapier / Make / n8n)

### Takeaway
They can post to Discord channels without code, but the app would need a way to trigger them (webhook or database event) and they add recurring cost and another secret location. For a Supabase-based app, an Edge Function is cheaper and simpler.

### Cited Findings
- Zapier: free $0 with 100 tasks/month and 2-step Zaps; Professional from $19.99/mo (annual) with 750 tasks; each action step counts as a task, triggers are free. Make: Core $9/mo with 10K operations; Pro $59/mo 100K. n8n Cloud: Starter EUR 20/mo, Pro EUR 50/mo for 10K executions; self-hosted about $15-30/mo VPS. — [Toolradar pricing roundup](https://toolradar.com/blog/zapier-pricing-2026) (secondary; the article's n8n Starter execution figure is internally inconsistent: 2.5K vs 1,000)

### Inferences
- A Supabase Database Webhook or Edge Function could call a Zapier/Make/n8n catch-hook URL, but that URL has the same leak problem unless held server-side. Bridges help mainly if non-developers must edit the message format.
- Whether their Discord actions can send DMs or file attachments was not researched.

### Gaps
- Official vendor pricing pages were not checked, and the bridges' Discord DM/file support was not verified.

## Recommended shape (synthesis, inference)
1. Channel posts and the editable leaderboard: Edge Function `discord-post` using a webhook URL or bot token from secrets, with `wait=true`, storing `message_id` in a table and PATCHing on update.
2. Paystub DMs: the same function using the bot, opening the DM per chatter and sending an embed plus PNG/PDF, with a per-chatter status table and throttling.
3. IDs: Discord sign-in or link (`provider_id`), with manual entry fallback.
4. Weekly auto-post: pg_cron plus pg_net plus Vault, text/embed only.
