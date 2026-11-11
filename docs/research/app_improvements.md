# Improvement opportunities for a custom OnlyFans/Fansly chatter payroll app (as of Nov 2026)

Method note: about 14 searches and fetches. Evidence for competitor feature depth is thin. Infloww's site was not fetchable (not allowlisted). Product pages for Supercreator, Fanshub and OnlyMonster were not retrieved. G2 and Reddit content was not retrievable. Anything not cited below is marked as an inference or a gap.

## 1. What agency-management tools (Infloww, Supercreator, Fanshub, CreatorHero, OnlyMonster, Scrile) offer for chatters

### Takeaway
CreatorHero documents shift scheduling with a chatter-visible shifts page and a shift history page for revenue and performance review. Industry guidance centres on revenue-per-chatter, ARPC, response time and sampled conversation quality reviews. Most of those are conversation-level metrics sourced from the platform (OnlyFans or Fansly) and sit outside a payroll app's data. The payroll-relevant overlap is shifts, per-model views, leaderboards, notifications and chatter self-service.

### Cited Findings
- CreatorHero's Shift Management docs describe a Shifts page that lets agencies plan chatter shifts, with chatters seeing their assigned shifts there. A Shifts History page reviews past shifts and lets you follow chatter activity, gauge revenue and assess performance indicators. The page does not mention clock in/out, payroll or notifications. — [CreatorHero Help](https://help.creatorhero.com/en/collections/11993045-shift-management)
- A CreatorHero blog page fetch returned only a capability list: payroll, commissions, shifts, performance tracking, per-model views, leaderboards, notifications and chatter self-service. No detail or mechanics were given, so treat it as a marketing-level claim. — [CreatorHero blog](https://www.creatorhero.com/blog/agency-for-onlyfans-creatorhero)
- Recommended chatter KPIs: Revenue Per Chatter, conversion rate on targeted offers, Average Revenue Per Conversation (called "the most telling KPI" because it rewards efficiency over volume), Average Response Time, and retention/churn impact. — [remove.tech](https://www.remove.tech/creator-blog/the-ultimate-guide-to-agency-scaling-how-do-i-measure-chatter-performance-across-my-agency-effectively)
- Quality scoring method: managers review a random sample of 10 to 20 conversations per chatter each week. They score brand alignment/tone, script adaptability, emotional intelligence and boundary enforcement, then hold weekly 1-on-1 reviews. The article says "activity does not equal achievement" and warns that rewarding raw volume or short-term revenue can hurt retention. It gives no bonus or penalty structure. — [remove.tech](https://www.remove.tech/creator-blog/the-ultimate-guide-to-agency-scaling-how-do-i-measure-chatter-performance-across-my-agency-effectively)
- Scrile's roundup says Infloww and Fansmetric let you manage hired chatters without giving full account access, so chatters can only handle messages. Chatterly offers message tracking, analytics, permission settings and shared multi-account access. The roundup says nothing on payroll or shifts. — [Scrile](https://scrile.com/blog/best-onlyfans-tools)
- An OFM community wiki reports that one agency tracked open-chat rate, first/second-PPV buy rates, selling-chat conversion, script completion, aftercare and renewal rate after adopting OFMOS. Before that it tracked only daily revenue. The wiki also advises assigning one named owner per KPI. — [OFM Bank wiki](https://ofmbank-wiki.pages.dev/agency-business)

### Inferences
- A payroll app cannot replicate conversation-level analytics without platform integration, and scraping is risky. The feasible overlap is manual or semi-manual fields that feed pay:
  - a weekly QA score (1–5) per chatter, entered by a manager from the 10–20 sampled chats, which can modify or gate bonuses;
  - per-model attribution of sales;
  - shift schedule and attendance, which the app already partly has.
- Gating bonuses on a quality score addresses the cited warning that volume-based rewards hurt retention. The app's podium and golden-ratio prizes are currently sales-driven.

### Gaps
- No primary documentation was retrieved for Infloww, Supercreator, Fanshub or OnlyMonster. Their shift/clock-in, automated bonus and penalty features are unverified.
- No G2 or Capterra review text was retrievable.

## 2. Contractor and payroll tools: approvals, pay-run checklists, audit log, locking, corrections, payment status, tax docs, notifications

### Takeaway
The retrieved sources confirm only 1099-NEC filing (Gusto and others) and contractor self-service/onboarding. Approvals, audit logs, locked periods, corrections and payment-status tracking were not confirmed from sources. Their inclusion below is based on general payroll-product practice (inference).

### Cited Findings
- Gusto lists "1099-NEC filing included" among its contractor features. OnPay offers contractor self-service setup, Gusto offers contractor self-onboarding, and ADP includes self-service portals. — [Gusto: best contractor payroll software](https://gusto.com/resources/best-contractor-payroll-software)
- That Gusto comparison page did not mention approvals, payment status tracking, audit or corrections. — [Gusto](https://gusto.com/resources/best-contractor-payroll-software)
- Gusto's embedded-payroll docs have a contractor payments process page. I did not retrieve its details. — [Gusto docs](https://docs.gusto.com/embedded-payroll/docs/process-contractor-payments)

### Inferences
- Standard payroll-product patterns that fit this app (from general knowledge, not retrieved):
  - a pay-run lifecycle of draft, review, approved, paid;
  - a paid/unpaid flag with paid date and method per chatter per week;
  - a retro-adjustment line item that carries into the next period, instead of editing a closed week;
  - an annual earnings summary per chatter, which replaces the tax-form feature for contractors the app does not file for.
- Many chatters are offshore contractors. Cited sources do not cover tax-doc requirements for them. An annual earnings statement export is cheap and low-risk.

### Gaps
- No evidence was retrieved on Deel, Homebase, When I Work or 7shifts specifics (approvals, audit log, locked periods).
- No source confirmed how any tool handles corrections or retro pay.

## 3. Reliability and ops: audit trail, finalize/lock, undo, backup/restore, offline, conflicts

### Takeaway
No competitor evidence was retrieved. These are engineering recommendations from general practice and fit Supabase well (inference).

### Cited Findings
- Supabase Edge Functions can be invoked from the app with `supabase.functions.invoke` using the signed-in user's JWT, or from a database function. — [Supabase docs](https://supabase.com/docs/guides/functions/examples/send-emails)

### Inferences
- Audit log: a Postgres `audit_log` table (who, when, table, row, old and new JSON) filled by a trigger on pay-affecting tables. Effort: S–M. It is the top reliability item for a money app with several editors.
- Finalize/lock week: add `locked_at` and `locked_by` to a week, enforce it with RLS or a trigger, and allow edits only via a logged "reopen" or an adjustment line. Effort: S.
- Undo: snapshot a week's JSON before each bulk action and offer "revert to snapshot". The audit log can drive this. Effort: M.
- Backup: scheduled JSON export (a Supabase cron job or the manual Export button), plus a restore-from-JSON import. Effort: S.
- Conflicts: add an `updated_at` or version column and use optimistic checks ("this week changed since you opened it"). This matters because owners, managers and head chatters can all edit. Effort: S–M.
- Offline-first: low priority for a manager-driven app. A localStorage draft queue for hours entry is enough. Effort: M.

### Gaps
- No competitor sources on audit, lock or undo behaviour were retrieved.

## 4. Communication: paystub delivery, push, acknowledgment, disputes

### Takeaway
All three channels are technically feasible. Web Push works on iOS only for Home Screen web apps, which already matches the app's deployment. Email via Resend from a Supabase Edge Function is documented and simple.

### Cited Findings
- WebKit: Web Push for Home Screen web apps shipped in iOS/iPadOS 16.4. The site must be a Home Screen web app with a manifest `display` of `standalone` or `fullscreen`. Permission can be requested only in response to direct user interaction such as a tap. Web Push uses the Push, Notifications and Service Worker APIs and Apple's push service, with no Apple Developer membership needed. Notifications appear on the Lock Screen and Notification Center and respect Focus modes. This was fetched via a WebKit mirror link of the original blog post (https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/ was not allowlisted; the article was written against the 16.4 beta). — [WebKit](https://webkit.org/?p=13878)
- Resend from Supabase: create a Resend API key and verify the sending domain, then write an Edge Function that POSTs to Resend's email endpoint with a bearer token. Store `RESEND_API_KEY` in Edge Function secrets and deploy. The function can be called from the client or from a database function. — [Supabase docs](https://supabase.com/docs/guides/functions/examples/send-emails); see also [Resend docs](https://resend.com/docs/send-with-supabase-edge-functions)
- The Supabase page gives no code for a database trigger or webhook invoking the function. — [Supabase docs](https://supabase.com/docs/guides/functions/examples/send-emails)

### Inferences
- "Publish and notify" flow: when the manager marks a week approved or paid, an Edge Function sends each chatter a Resend email with a link to their paystub, or a Web Push, or a Discord DM or channel post. Effort: M. Email is the most reliable and the best first step.
- The app already has a Discord announcement template, so posting a webhook message from the same Edge Function is a small increment. Effort: S. Discord DMs to individual chatters need a bot and are more work (M–L).
- Web Push needs a service worker, VAPID keys, a subscriptions table and an Edge Function sender. The user must tap to enable it, and the app must be installed to the Home Screen. Effort: M–L. Do it after email.
- Acknowledge and dispute: a per-paystub "Acknowledge" button, plus a per-line "Question this" comment that notifies the manager and logs to the audit trail. Effort: M. It reduces payout disputes and gives a paper trail.

### Gaps
- No evidence on Declarative Web Push or on iOS push reliability in 2026. The WebKit post did not mention it.
- No source on how competitors handle acknowledgment or disputes.

## 5. Analytics: per-model profitability, per-slot performance, retention, cost per $ sales, forecasting

### Takeaway
Cited sources support tracking revenue per chatter, ARPC and churn. The cost-side metrics are straightforward to derive from data the app already holds if sales are tagged by model and shift.

### Cited Findings
- Weekly tracking of response rate, revenue per active fan, PPV conversion, rebill rate and LTV per fan is recommended. A cited figure puts average OnlyFans management churn at 50–60% and attributes 35% of fan churn to chatting, though this is a single agency blog's claim. — [Desirely](https://www.desirely.co/en/blog/10-mistakes-onlyfans-agencies-fail)
- Desirely gives a worked example of margin pressure: at a 5% commission on a €5,000 monthly model, the agency keeps €250, leaving about €100 for chatting. It also puts a chatter's cost at €800–€2,000 per month and estimates 2–4 weeks of training and lost revenue on a bad hire. — [Desirely](https://www.desirely.co/en/blog/10-mistakes-onlyfans-agencies-fail)

### Inferences
- Feasible derived metrics from existing data:
  - cost per $1 of sales per chatter (total chatter pay divided by sales);
  - per-model profit, if sales entries carry a model field;
  - sales per hour by shift slot, if shifts are recorded;
  - chatter tenure and retention from the roster start date and status;
  - a simple payroll forecast from a trailing average plus goal-bonus exposure.
- Per-model attribution is the biggest data-model change, since the current entry is per chatter. If entry is per chatter only, an optional "model" split row is the least invasive route. Effort: M.

### Gaps
- No pricing or feature evidence on how tools present per-slot or per-model profitability.

## 6. Gamification

### Takeaway
No retrieved source documents agency gamification in detail beyond leaderboards (CreatorHero claim) and the cautions about volume-only incentives. The following are ideas only.

### Cited Findings
- CreatorHero lists leaderboards as a feature. — [CreatorHero blog](https://www.creatorhero.com/blog/agency-for-onlyfans-creatorhero)
- Rewarding raw volume or aggressive short-term revenue can hurt quality and retention, so incentives should weigh those outcomes. — [remove.tech](https://www.remove.tech/creator-blog/the-ultimate-guide-to-agency-scaling-how-do-i-measure-chatter-performance-across-my-agency-effectively)

### Inferences
- Cheap additions given existing podium, most-improved and golden-ratio prizes:
  - attendance streaks (consecutive weeks with no strike or no-show) with a small bonus;
  - badges computed from history (first $X week, 4-week improvement streak, perfect attendance month);
  - a quality-score multiplier on prizes;
  - auto-generating prize lines from the leaderboard when a week is finalized. Effort: S–M.
- Team versus team needs a team field on the roster. Effort: S–M.

### Gaps
- No evidence of what agencies actually use or what works.

## 7. Evidence of agency-owner complaints

### Takeaway
Direct owner complaints about payroll tools were not found. Indirect evidence points to untracked KPIs, unclear accountability, thin margins, high churn and abusive or vague contracts.

### Cited Findings
- Agencies scaling without systems lost about 50% of top-performer revenue in one anecdote, and "everyone responsible for everything" leaves no one accountable. — [OFM Bank wiki](https://ofmbank-wiki.pages.dev/agency-business)
- Abusive contract clauses are described as the main cause of disputes between creators and agencies. That concerns the creator side, not chatter pay. — [Desirely](https://www.desirely.co/en/blog/10-mistakes-onlyfans-agencies-fail)
- Press coverage describes low-paid chatters, reportedly around $2 per hour for some workers, and a lawsuit over fans not knowing who they were chatting with. This is context rather than payroll-tool evidence. — [Vice](https://vice.com/en/article/onlyfans-management-agency-chatters); [404 Media](https://404media.co/onlyfans-sued-after-two-guys-realized-they-might-not-actually-be-talking-to-models)

### Inferences
- Pay transparency (the line-by-line paystub, which the app already has) plus acknowledgment and dispute notes serve the trust and retention angle.

### Gaps
- Reddit, forum and G2/Capterra complaint evidence was not retrievable in this session. Nothing here should be quoted as owner sentiment about payroll tools.

## Prioritized improvement list (rationale and effort for a single-file React + Supabase app)

Evidence strength: "sourced" means a retrieved source supports the technical or product claim; "inference" means general practice.

| # | Improvement | Why | Effort | Basis |
|---|---|---|---|---|
| 1 | Finalize/lock week with a logged reopen | Prevents silent edits to paid weeks; the base for everything below | S | inference |
| 2 | Audit log table via Postgres triggers, with a viewer for owners | Shows who changed what; essential with several editors | S–M | inference |
| 3 | Payment status per chatter per week (paid, date, method) plus a pay-run checklist | Core payroll workflow gap; stops double or missed payments | S | inference |
| 4 | Corrections as adjustment lines in the next period instead of editing closed weeks | Retro pay without rewriting history | S | inference |
| 5 | Email paystub or "your pay is ready" via Resend Edge Function on approve/paid | Automatic delivery; documented pattern | M | [Supabase](https://supabase.com/docs/guides/functions/examples/send-emails) |
| 6 | Chatter acknowledgment and per-line dispute comment | Builds a paper trail and reduces payout arguments | M | inference |
| 7 | Backup/restore (scheduled JSON export and import) and optimistic concurrency checks | Safety net and conflict handling for a multi-role app | S–M | inference |
| 8 | Weekly QA score (manager-entered) feeding bonus eligibility | Matches sourced KPI/QA practice; counters volume-only incentives | S–M | [remove.tech](https://www.remove.tech/creator-blog/the-ultimate-guide-to-agency-scaling-how-do-i-measure-chatter-performance-across-my-agency-effectively) |
| 9 | Cost per $ of sales, retention and tenure, payroll forecast | Derivable from existing data; helps margin control | S–M | [Desirely](https://www.desirely.co/en/blog/10-mistakes-onlyfans-agencies-fail) |
| 10 | Per-model sales attribution and per-model profit | High value for agency P&L; biggest schema change | M | inference |
| 11 | Discord webhook auto-post on approve (reuses the existing template) | Small increment on existing feature | S | inference |
| 12 | Web Push for iOS Home Screen web app | Direct lock-screen alerts; needs service worker, VAPID, subscriptions table | M–L | [WebKit](https://webkit.org/?p=13878) |
| 13 | Streaks, badges, team vs team, auto-prize lines | Engagement; builds on existing prizes | S–M | inference |
| 14 | Shift schedule with chatter-visible shifts and shift history (sales per slot) | CreatorHero offers this; attendance already exists | M | [CreatorHero Help](https://help.creatorhero.com/en/collections/11993045-shift-management) |
| 15 | Annual earnings statement export per chatter | Stand-in for tax docs; low risk | S | inference ([Gusto](https://gusto.com/resources/best-contractor-payroll-software) shows 1099 filing is standard in payroll tools) |
