# Payout rails for a small US chatter agency (Supabase Edge Functions + static React app) — research as of Nov 2026

Not legal or tax advice. Research budget was ~16 fetches/searches; several providers (Deel, Tremendous, Dots, Cosmo, Bitwage, Circle/Coinbase, Venmo/Cash App links, Stripe Connect fees) were NOT directly verified — see Gaps in each section.

## 1. Adult-industry policy risk per rail (will an adult-adjacent chatter agency get closed?)

### Takeaway
Nearly every mainstream rail lists adult content/services as prohibited or restricted, but the wording targets what is *sold* (content, webcam/live chat, escorts), not a back-office agency paying its own contractors. That leaves the agency in a gray zone: enforcement is by compliance reviewers' judgment, and the agency's own business description at onboarding (e.g. "OnlyFans management") is what usually triggers declines. Paxum is the only rail found that is positioned for the adult industry. Describing the business accurately and keeping income documentation is safer than concealing it.

### Cited Findings
- PayPal AUP: lists "certain sexually oriented materials or services" among restricted transactions; Section 10 "Mature Audience Content" covers "Any adult content delivered digitally including video on demand (VOD) and web-cam activities" and requires PayPal approval (not an outright ban); transacting in any approval-required activity without approval is prohibited; approval inquiries go to PayPal Sales. The approval list is "not intended to be an exhaustive list." The terms "pornography"/"sexually explicit" were not found in the page (as summarized by the fetch tool). — [PayPal AUP (UK mirror)](https://www.paypal.com/gb/webapps/mpp/ua/acceptableuse-full)
- Stripe: "Adult content and services" is under Prohibited: adult services incl. "pay-per-view," pornography and "other mature audience content," adult video stores, strip clubs, and AI-generated content meeting the criteria. The adult-content ban is stated to apply to all content creators; content-creation platforms hosting third-party content are "restricted" (extra due diligence). The page does not say whether paying contractors is affected; "Payment facilitation and aggregation" is restricted and "Peer-to-peer money transmission" is prohibited. — [Stripe Restricted Businesses](https://stripe.com/legal/restricted-businesses)
- Stripe has cut off adult-adjacent platforms in the past (e.g., WishTender, used by dominatrixes). — [404 Media](https://www.404media.co/stripe-cuts-off-platform-used-by-dominatrixes-wishtender/) (search-result title only; article body not fetched)
- Wise AUP §1.2.1: "Adult content" is a restricted category covering "Pornography and other visual content depicting explicitly sexual acts," "Services of sexual nature (webcam shows, live chats, prostitution, escorts, etc)," and sexually oriented establishments; Wise "does not support these businesses or transactions, and they may be declined." Restrictions "do not apply to lawful transactions using the Wise Multi-Currency Card." — [Wise AUP](https://wise.com/acceptable-use-policy)
- SpankChain (advocacy, one-sided) reports a "recent Wise deplatforming" of adult-industry creators, with notices like "We do not support transfers related to Adult Content"; no dates or counts given. Advises preserving evidence, minimal retries, appeal via Wise. — [SpankChain](https://www.spankchain.com/spankbyte-collection/wises-antics-and-what-to-do-if-youre-debanked)
- Payoneer prohibited list: "Adult services including prostitution, escorts, pay-per view, sexual massages, and adult live chat features" and "Adult pictures, videos, games that include pornographic or mature audience content." — [Payoneer prohibited transaction list](https://www.payoneer.com/legal/prohibited-transaction-list/)
- Paxum markets to webcam studios/models (case-study pages: "Get Paid From Top Webcam Platforms To Your Paxum Account"), but its mass-payout page does not state an adult policy. — [Paxum mass payouts](https://paxum.com/services/mass-payouts); [Paxum webcam case study](https://paxum.com/case-studies/webcam-studios)
- OFM operator-community summary (unverified chatter, secondary site): Wise is "hit-or-miss for agency use" and works for OnlyFans payouts only in the model's own name; Paxum offers auto-split of withdrawals between manager and model; Skrill is most-used fallback but with weeks-long support delays and sudden restrictions; Cosmo needs a $10K minimum before withdrawal; crypto chains cost ~2–4%. PayPal, Payoneer, Deel were not mentioned. — [OFM Insider](https://ofm-insider.pages.dev/agency-payments-2026)
- Wise itself lists a "can my business use Wise" help page and Nium, Moov, Wix publish similar prohibited lists (not read). — search results only

### Inferences
- A chatter agency is not literally "selling adult content," so a strict reading of the PayPal/Wise/Stripe/Payoneer lists may not capture pure payroll — but all lists are broad ("services of sexual nature… live chats" at Wise; "adult live chat features" at Payoneer), and chatting as a service on creator accounts could be read as in-scope. Treat as genuinely ambiguous, not safe.
- PayPal is the only mainstream rail with an explicit approval path rather than flat prohibition; Stripe is the most hostile on paper.
- Lowest-risk pattern: keep the money-moving account in a business whose registration/description is accurate (e.g., "marketing / customer-engagement services"), avoid evasive statements, and keep a backup rail. Whether that is advisable to disclose is a compliance question for counsel (not decided here).

### Gaps
- No primary-source evidence found of an agency-specific closure on PayPal Payouts, Payoneer, Trolley, Tipalti, Dots, Deel. No searchable Reddit threads fetched (r/onlyfansadvice not reached within budget).
- Policies for Trolley, Tipalti, Deel, Tremendous, Dots, Coinbase/Circle, Bitwage, Cosmo not read.
- All policy texts are summaries from a fetch tool, not verbatim page reads; re-verify wording before relying on it.

## 2. Rail-by-rail: API, fees, countries, speed, recipient requirements

### Takeaway
For a Supabase Edge Function, the viable API-first options are PayPal Payouts, Wise (API/batch), Trolley, Tipalti, Payoneer (limited), Paxum (REST). Fee, country, and speed figures verified here are thin; only PayPal fee structure, Wise batch limits, and country/batch-size counts for Trolley/Tipalti/Payoneer were sourced.

### Cited Findings
- **PayPal Payouts**: sender pays a percentage per payout item with a cap (rate/cap vary by sending country and domestic vs international); "typically… variable fee of 2%"; recipients pay no fee; funding account must cover total plus fees; per-item limits e.g. USD 60,000 registered / 20,000 unregistered; currency conversion adds fees; Venmo payouts (US) same fees. The fees page mentions no approval requirement (but see AUP above). — [PayPal Payouts fees](https://developer.paypal.com/payouts/fees.md); API docs entry: [docs.paypal.ai/payouts](https://docs.paypal.ai/payouts)
- **Wise Business batch/API**: up to 1,000 transfers per CSV file; one source currency per file, multiple target currencies; same pricing as regular transfers; open API with no extra charge; unpaid transfers cancel after a few days; real-time tracking. Page dated Feb 2022 — stale. — [Wise batch payments guide](https://wise.com/us/blog/everything-about-batch-payments); API landing: [wise.com/payouts](https://wise.com/payouts/)
- **Trolley** (vendor marketing, own comparison page): 210 countries/135 currencies; API-first with SDKs; up to 20,000 payments per batch; payouts triggerable by platform events; collects W-8/W-9, e-files 1099 and 1042-S. **Tipalti**: 200 countries/120 currencies; up to 5,000 instructions/batch; tax-form collection, some reporting needs third-party tools. **Payoneer**: 190 countries/70 currencies; "limited API," up to 1,000 transactions/batch; no native tax compliance. Fees and minimums not quantified for any of the three. — [Trolley vs Tipalti vs Payoneer](https://trolley.com/blog/trolley-vs-tipalti-vs-payoneer-which-is-best-for-paying-gig-workers)
- **Paxum**: REST API for automated mass payouts ([api.paxum.com](https://api.paxum.com)); EFT to 50+ countries in 20+ currencies (recipient bank must be in local currency), wires in 200+ currencies, card funding, and P2P to a recipient's Paxum email; fees "low" but unquantified (see paxum.com/fees/business); minimums not stated. — [Paxum mass payouts](https://paxum.com/services/mass-payouts)
- **Discord**: see Question 4.

### Inferences
- PayPal Payouts is the most straightforward Edge Function integration (REST, OAuth, webhooks documented) and recipients need only a PayPal account/email; ~2% sender fee likely matters little at $100–$600 payouts (~14 people ≈ $2k–$8k/week). Account-closure risk is the dominant concern, not cost.
- Trolley/Tipalti are built for exactly this use case (contractor payouts + tax forms) but pricing is typically sales-led/subscription-based; for 14 people it may be disproportionate — not verified.
- Wise is cheapest for PH/LatAm/EU local-bank delivery in practice, but its AUP and reported adult deplatforming make it the riskiest as a primary account for this business.

### Gaps
- Not verified: Deel/Remote contractor pricing and APIs; Stripe Connect transfer fees/country coverage (and Connect cross-border payout limits); Tremendous (gift-card/PayPal/ACH payouts, fees); Dots (dots.dev) pricing and policy; Cosmo; Coinbase/Circle USDC payouts; Bitwage; Payoneer fees; Trolley/Tipalti pricing; Wise per-corridor fees (e.g., PH, Colombia, Ukraine); speed claims for any rail; webhook availability per provider (PayPal and Trolley believed to offer webhooks but not confirmed in this research).
- Whether Wise's API permits fully server-side transfers without per-transfer SCA/approval for US business accounts — not confirmed.

## 3. Lighter alternatives: batch files and payment links (no money movement by the app)

### Takeaway
The app can generate a Wise-style batch CSV or PayPal Payouts/mass-pay file server-side and let the owner upload it manually, keeping the app out of money transmission and keeping credentials out of Edge Functions. Venmo/Cash App/PayPal.me links are not verified here.

### Cited Findings
- Wise batch tool accepts a CSV with up to 1,000 transfers, one source currency per file, and a human reviews/pays in Wise's UI. — [Wise batch payments guide](https://wise.com/us/blog/everything-about-batch-payments)
- PayPal also offers a Mass Payments (file upload) product alongside the Payouts API. — [PayPal Mass payments](https://www.paypal.com/us/business/operations/mass-payments) (page not read; existence only from search result)
- Chatterly's blog suggests payroll software (Pilot, Gusto) so international contractors can complete W-8BEN and sign company documents before onboarding. — [Chatterly](https://usechatterly.com/blog-full/how-to-get-paid-by-creators-and-pay-local-and-international-contractors-employees)

### Inferences
- A "payout CSV export" rung is nearly free to build: one Edge Function/React export that emits per-rail CSV columns (name, email/account id, currency, amount, reference = week id). Marking "paid" can be manual or by re-importing the provider's result CSV.
- Per-chatter payment links (PayPal.me with amount, Venmo/Cash App deep links) could appear on the paystub for manual payment, but Venmo/Cash App are US-only consumer apps and unsuitable for Philippines/LatAm/Eastern Europe contractors; PayPal.me works internationally in principle. Unverified.

### Gaps
- PayPal.me/Venmo/Cash App link formats, business-use ToS, and country availability not fetched.
- Exact PayPal mass-pay CSV format and Wise CSV template columns not captured.

## 4. Discord: native payments and tipping bots

### Takeaway
Discord has no native way to pay people; its monetization is for bots/apps selling SKUs (subscriptions, one-time purchases) to users. Discord can still be used as a notification/control surface (bot or webhook posts "payout batch ready/paid"), but not as a payment rail.

### Cited Findings
- Discord app monetization supports recurring subscriptions and one-time purchases via SKU/Entitlement APIs, with Discord handling billing; the page does not mention peer-to-peer payments or paying people. — [Discord app monetization](https://docs.discord.com/developers/platform/app-monetization.md)
- Third-party "payment bots" exist (Launchpass, etc.) but are for selling server access/subscriptions. — [Launchpass on Medium](https://medium.com/launchpass/discord-payment-bots-the-key-to-monetizing-your-discord-server-93ea898e764e) (search result only; not fetched)

### Inferences
- Tipping/economy bots use virtual currency and are not suitable payroll; none verified.
- A Supabase DB webhook / Edge Function posting to a Discord channel webhook URL (and slash-command approval buttons for "Pay all") is feasible with Discord's standard bot/webhook APIs, but this was not researched here. Putting approval of real-money payouts behind a Discord interaction is a security tradeoff (bot token and interaction signature verification needed).

### Gaps
- Discord webhook/interaction docs not fetched; no evaluated tipping bot; Discord's own policy on adult-industry servers not researched.

## 5. Tax records: 1099-NEC vs W-8BEN

### Takeaway
Only partially researched: Trolley markets built-in W-8/W-9 collection and 1099/1042-S e-filing; Tipalti collects forms with some reporting outsourced; Payoneer has no native tax compliance. PayPal/Wise/Paxum tax-form handling was not checked.

### Cited Findings
- Trolley: W-9, W-8BEN, W-8BEN-E collection; 1099 and 1042-S e-filing. Tipalti: tax-form collection, some reporting via third-party tools. Payoneer: no native tax compliance. — [Trolley comparison](https://trolley.com/blog/trolley-vs-tipalti-vs-payoneer-which-is-best-for-paying-gig-workers) (vendor-biased)
- Chatterly advises collecting W-8BEN from international contractors and considering home-country tax obligations. — [Chatterly](https://usechatterly.com/blog-full/how-to-get-paid-by-creators-and-pay-local-and-international-contractors-employees)

### Inferences
- From general knowledge (not sourced here): US-person contractors get W-9 and 1099-NEC when paid ≥ the IRS threshold; non-US contractors performing services outside the US generally provide W-8BEN and are typically not issued 1099-NEC. The app should store a W-9/W-8BEN on file, tax-year payout totals, and country per chatter regardless of rail. Confirm thresholds and 1042-S edge cases with a CPA.
- Payment-processor 1099-K reporting for PayPal-funded payouts is a separate question not researched.

### Gaps
- Current-year 1099-NEC threshold and e-file rules, W-8BEN validity, and which rail (PayPal, Wise, Deel) handles forms — not verified with sources.

## 6. Recommendation ladder

### Takeaway
Suggested path (judgment, based on above): (1) build payout CSV export plus a `payouts` table with status; (2) if money movement from the app is wanted, pick one API rail — PayPal Payouts is simplest technically and has an approval path, with Trolley as the paperwork-heavy alternative, and keep Paxum/crypto as a backup given adult-industry risk; (3) only then add webhooks writing "paid/failed" into Supabase.

### Cited Findings
- PayPal Payouts: percentage fee (~2% typical) with cap, recipients pay nothing, API available. — [PayPal Payouts fees](https://developer.paypal.com/payouts/fees.md)
- Trolley supports event-triggered payouts, W-8/W-9 and 1099 filing, and batches up to 20,000. — [Trolley comparison](https://trolley.com/blog/trolley-vs-tipalti-vs-payoneer-which-is-best-for-paying-gig-workers)
- Paxum offers REST API mass payouts and is marketed to webcam/adult segments. — [Paxum mass payouts](https://paxum.com/services/mass-payouts)

### Inferences
- Rung 1 (CSV export): zero provider risk, ~1 day of work, works with Wise, PayPal mass pay, Paxum. Add idempotent `payout_batch_id`, per-row reference, and manual "mark paid."
- Rung 2 (one API rail, "Pay all" button): Edge Function with provider secrets in Supabase secrets, admin-only auth check, idempotency key per (chatter, week) (PayPal `sender_batch_id`), dry-run preview, two-step confirm. Static GitHub Pages front end must never hold provider keys.
- Rung 3: provider webhook → Edge Function (verify signature) → update `payout_items.status`; reconcile with a scheduled poll since webhooks can drop; optional Discord channel notification.
- Design for rail-portability (adapter per provider) because closure risk is real for this business type; keep 1–2 weeks of buffer funds outside any single rail.
- Compliance caution: moving money on behalf of others from your own app could implicate money-transmitter rules if funds are not the agency's own; paying from the agency's own funded account to its own contractors is the lower-risk framing. Confirm with counsel.

### Gaps
- No verified cost model per rail for 14 payees/week; no verified speed data (hours vs days) for any rail; Reddit/operator evidence is thin and unverified.
