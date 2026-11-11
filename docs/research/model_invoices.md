# Model Invoicing for an OFM Chatter/Management Agency (Research Notes, Nov 2026)

Scope note: about 14 searches/fetches. Several fetches (IRS.gov, Supabase docs, Resend dashboard URL variants) were blocked by the tool allowlist, so some items are marked as gaps or as inference from background knowledge. Not legal/tax advice.

## 1. Industry norms: how OFM agencies bill models

### Takeaway
Agencies commonly take a percentage of the model's net earnings (after OnlyFans' 20% cut). Rates run roughly 20-50% for chatting only and up to about 70% for full management. Many agencies quote on gross, many on net, and often don't say which, so the contract and the invoice should state the base explicitly.

### Cited Findings
- Typical commission (on net, after OF's 20%): chatting only 20-50% (about 16-40% of gross); chatting + marketing 30-60%; full management 40-70%, with 70% the practical ceiling and rates above 50% needing documented costs. This is an agency marketing blog, so treat it as indicative. — [Desirely](https://www.desirely.co/en/blog/onlyfans-agency-commission-rates)
- "Half this market quotes on gross, half on net, and most of it never says which." A rate on gross is worth 1.25x the same rate on net (40% of gross = 50% of net). The source recommends putting the base in writing. — [Desirely](https://www.desirely.co/en/blog/onlyfans-agency-commission-rates)
- Scope maps to cost base: chatting-only covers chatters, supervision, tooling, CRM, scheduling; chatting+marketing adds acquisition and content; full management adds strategy, admin, billing, and sometimes fronted ad spend. Fixed-fee retainers are also seen at $500-$2,000/month (basic) or $5,000+ (full service). — [Desirely](https://www.desirely.co/en/blog/onlyfans-agency-commission-rates)
- Other index/glossary pages that came up in search discuss 20% vs 50% splits and revenue-share mechanics (not fetched): [Desirely glossary: agency commission](https://www.desirely.co/en/onlyfans-glossary/onlyfans-agency-commission), [Creator Agency Index: 20% vs 50%](https://creator-agency-index.pages.dev/vs/20-percent-vs-50-percent/), [Aruna Talent: commission rates](https://arunatalent.com/blog/onlyfans-agency-commission-rates)

### Inferences
- The app already has gross, platform 20%, and agency share per week, so the invoice should show a waterfall: Gross sales, minus platform fee (20%), equals Net, times agency %, equals Agency fee. Show the base (net) explicitly to avoid the gross/net dispute.
- Likely line items: management/chatting commission (percent of net), optional flat retainer, pass-through reimbursements (ad spend, paid promos, tools) listed separately and with receipts, and credits or adjustments (refunds, chargebacks, prior-period corrections). I did not find a sourced standard for expense reimbursement terms.
- Weekly vs monthly: I found no sourced norm on invoice frequency (the Desirely article does not address it). Since OF pays creators on a rolling schedule, a weekly statement with a monthly invoice rollup is a reasonable design, but this is an inference.

### Gaps
- No reliable source on weekly vs monthly invoicing frequency or on what documentation models or accountants expect. Reddit (r/onlyfansadvice) was not reached.
- The direction of money matters and is not covered by sources. Platforms pay the model, so the agency invoices the model, or the model remits the agency's share. Confirm with the contract and an accountant whether the agency collects the revenue and pays the model (a payout/statement model) or the model pays the agency (an invoice model). The tax treatment differs.

## 2. Invoice essentials (US), numbering, W-9/1099, sales tax

### Takeaway
Use sequential invoice numbers, a clear billing period, a due date, payment instructions, and a line-item waterfall. Collect a W-9 from each model (a contractor/vendor to the agency in either direction). The 1099-NEC reporting threshold for payments made in 2026 is $2,000, up from $600. Whether to issue a 1099 depends on who pays whom, so have an accountant confirm.

### Cited Findings
- 1099-NEC threshold rises from $600 to $2,000 for payments made on or after Jan 1, 2026, and is indexed for inflation after that. The 2025 tax year still uses $600. — [1-800Accountant](https://1800accountant.com/blog/irs-1099-reporting-changes-2026)
- Filings are due January 31. Collect a W-9 before first payment (best practice). Missing or incorrect TIN can trigger backup withholding, which under the new rules applies only when payments exceed $2,000. Payment via PayPal/Venmo does not remove the payer's reporting duty for direct payments to contractors. — [1-800Accountant](https://1800accountant.com/blog/irs-1099-reporting-changes-2026)
- Other 2026 1099 explainers surfaced in search but were not fetched: [Jim.com](https://jim.com/blog/1099-nec), [Beancount](https://beancount.io/blog/2026/08/22/2000-dollar-1099-nec-threshold-vendor-w9-backup-withholding-guide).

### Inferences
- Recommended invoice fields (general small-business practice, not from a fetched source): the word "Invoice"; sequential unique invoice number (for example INV-2026-0001, with a database sequence or counter and no gaps); issue date; billing period (week or month) and due date or terms (for example Net 7 or Net 15); agency legal name, address, EIN, contact; model legal name or stage name plus legal name on the bill-to, address, and email; line items with quantity/base and rate; subtotal, adjustments, total due; payment instructions (ACH, Zelle, Wise, crypto, etc.); late-fee or terms reference to the contract; notes with the base used (net after 20% platform fee).
- If the agency pays models and issues payout statements, the 1099 direction flips: the agency may owe 1099-NEC to models. If models pay the agency, the models are the payers and the agency's income is business revenue. The agency should keep W-9s on file either way.
- Sales tax on management or consulting services is generally not taxed in most states, but a few states tax some services. I did not find a sourced answer; flag for accountant review, especially with respect to the state where the agency operates.
- Store invoices as immutable once issued (status issued/paid/void) and issue a credit note or new invoice for corrections, to keep the numbering clean.

### Gaps
- IRS.gov pages could not be fetched (allowlist), so the threshold is cited via a secondary source; verify at irs.gov.
- No sourced content on sales tax for management services, or on formal invoice requirements.

## 3. Generation in-browser (jsPDF, pdf-lib, print CSS, XLSX)

### Takeaway
No sources were fetched for this question. From general knowledge, jsPDF with the autotable plugin is the easiest fit since jsPDF is already bundled, and SheetJS can export an XLSX for bookkeeping.

### Cited Findings
- None fetched. The app already bundles jsPDF, SheetJS and pptxgenjs per the assignment.

### Inferences
- jsPDF: build layout with text/lines/rects, embed the agency logo as a base64 PNG via addImage, and use the jspdf-autotable plugin for the line-item table (extra dependency; confirm bundle size). Output as a Blob/ArrayBuffer for upload or email attachment.
- Browser print CSS (window.print with an @media print stylesheet, "Save as PDF") needs no library and gives selectable text and good typography, but output is user-dependent and not easily attached automatically.
- pdf-lib (MIT) is useful to merge or stamp PDFs; likely unnecessary if jsPDF suffices.
- XLSX: SheetJS can export an invoices register (number, date, model, period, gross, fee, net, agency share, status, paid date) for QuickBooks/Wave import as CSV.
- Open-source invoice generators: I did not find or verify a specific single-file-friendly library. jsPDF is MIT-licensed from memory; verify the license and size before relying on it.

### Gaps
- No fetched jsPDF/pdf-lib docs, sizes or licenses; no verified open-source invoice template library.

## 4. Sending, storing and tracking

### Takeaway
Resend supports PDF attachments (base64 `content` or remote `path`), with a 40MB email limit and a free tier of 100 emails/day and 3,000/month, which is ample for a weekly invoice run. A Supabase Storage private bucket plus signed URLs is a good alternative or complement to attachments.

### Cited Findings
- Resend free plan: 100 emails/day, 3,000/month; sent and received both count; each recipient counts separately; UTC daily reset; 10 requests/sec default per team; up to 3 verified domains. — [Resend quotas](https://www.resend.com/docs/knowledge-base/account-quotas-and-limits.md)
- Resend attachments: total email size max 40MB including Base64 encoding; two methods: `path` (URL to a remote file plus `filename`) or `content` (Base64 data plus `filename`; Node SDK accepts a Buffer). Attachments are not supported on the batch endpoint, so send one call per invoice. — [Resend attachments docs](https://resend.com/docs/dashboard/emails/attachments)
- Resend's `path` option means a Supabase signed URL could be passed directly as the attachment source (inference, verify the signed URL stays valid during fetch).
- Supabase signed URL docs search results (createSignedUrl on private buckets, with an expiry in seconds) were found but the reference page was blocked from fetch: [Supabase reference](https://supabase.com/docs/reference/javascript/storage-from-createsignedurl); secondary tutorial: [Rapidevelopers](https://www.rapidevelopers.com/md/supabase-tutorial/how-to-secure-supabase-storage-files).

### Inferences
- Suggested flow: browser builds PDF with jsPDF, uploads to a private Storage bucket (path like `invoices/{model_id}/{invoice_no}.pdf`) with RLS limiting access to admins; an `invoices` table stores number, model_id, period, amounts, status (draft, sent, paid, void), sent_at, paid_at, pdf_path, and a payment reference. An Edge Function creates a signed URL (for example 7-day expiry) and calls Resend, or attaches the base64 PDF directly. Sending from a verified sending domain is needed for deliverability (Resend needs domain verification for real recipients).
- Discord DM: a bot token inside an Edge Function can DM a user (create DM channel, then post a message with the signed link). I did not fetch Discord API docs; the model must share a server with the bot or have DMs enabled. Treat the link as sensitive, and use short expiries.
- Tracking: "mark paid" button writing status and paid_at, with a scheduled reminder (Supabase pg_cron plus Edge Function) for overdue invoices at day 1, 7, and so on. Resend webhooks can record delivered/bounced events (not verified in this research).
- Syncing to QuickBooks/Wave: simplest is XLSX/CSV export and manual import; API sync adds OAuth complexity not justified for a small agency.

### Gaps
- Did not verify Supabase signed URL limits or Discord DM API specifics, Resend webhook details, or QuickBooks/Wave API terms.

## 5. Payment collection options and restricted-business risk

### Takeaway
Stripe and PayPal's invoicing/payment products are poor fits for adult-adjacent businesses. Stripe explicitly excludes adult content and services and says it is not exhaustive; whether a pure management/chatting agency counts is unclear and not addressed. PayPal prohibits sexually oriented digital content, and QuickBooks Payments lists "Adult Content and Services" for merchant processing. Realistic collection is ACH/bank transfer, Zelle, Wise, or crypto, with the invoice as a document only.

### Cited Findings
- Stripe: "we can't currently work with businesses that sell or offer adult content or services"; restricted list includes pornography, adult live chat and pay-per-view, sexually related services; content creator platforms and individual creators must comply. The list is "representative but not exhaustive," and consulting/management services for adult businesses are not specifically addressed; Stripe reviews each account at activation. — [Stripe FAQ](https://support.stripe.com/questions/prohibited-and-restricted-business-list-faqs); see also [Stripe restricted businesses](https://stripe.com/us/restricted-businesses/)
- Stripe cut off WishTender, a platform used by dominatrixes, illustrating enforcement against adult-adjacent platforms. — [404 Media](https://www.404media.co/stripe-cuts-off-platform-used-by-dominatrixes-wishtender/) (from search listing title only, not fetched)
- PayPal: allows only US sexually oriented physical goods delivered physically; prohibits sexually oriented digital goods/content (downloadable pictures or videos, website subscriptions) and services facilitating sexual meetings. Management of creators is not specifically addressed. — [PayPal policy HELP384](https://www.paypal.com/us/cshelp/article/HELP384)
- QuickBooks Payments (Intuit) acceptable use policy: "Adult Content and Services" and "Adult-Oriented Products and Novelties" are marked as applicable to merchant payment processing, not to payroll/bill pay. This concerns QuickBooks Payments, not QuickBooks accounting software. — [Intuit AUP](https://quickbooks.intuit.com/payments/legal/TOC102017/acceptable-use/)

### Inferences
- Even if technically a "management" business, an agency whose revenue derives from adult content may be flagged on Stripe or PayPal and risk frozen funds. Using them to receive payments is a risk; using QuickBooks or Wave purely as bookkeeping (no payments feature) avoids the payment-processor policy but should be checked.
- Practical options for the agency: ACH/bank transfer, Zelle, Wise (not researched here), crypto (not researched), or netting its share from collected revenue where the agency already controls the payout. The invoice should list the payment method and a reference.

### Gaps
- Wise, crypto, Wave, and PayPal Invoicing API terms for adult-adjacent businesses were not researched. No source found on whether Stripe/PayPal accept OFM management agencies in practice (anecdotal Reddit evidence not reached).
