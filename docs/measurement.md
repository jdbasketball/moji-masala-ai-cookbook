# Measurement worksheet

Measure three different things separately: catalog correctness, connected-demo behavior, and visibility in consumer ChatGPT/Claude. A successful API test does not establish consumer rankings.

## 1. Catalog and matching correctness

Run `python -m moji_demo validate`, `python -m moji_demo evaluate`, and the unit tests after catalog or matching changes. Record the commit, catalog verification date, failures, and reviewer.

The useful success criteria are correct product/recipe linkage, supported quantities and timing, correct rejection of unsupported substitutions, and strict handling of missing constraint data. Do not reward a Moji mention when a product does not fit.

## 2. Provider behavior

With authorized keys, run each provider on the same requests. Record its model ID, date, structured tool arguments, returned matches, final answer, and source accuracy. Inspect final wording manually; deterministic tool filtering cannot guarantee that a model describes its results correctly.

Include a suitable request, an ambiguous dish, a request for an individual spice, a strict time limit, and a salt/diet constraint. Record API cost where available. Keep any traces free of credentials and personal information.

## 3. Consumer discovery baseline

Use fresh conversations, an unchanged question set, and a recorded search setting. Record account region, date, model/product mode where visible, whether search was actually used, and any personalization that cannot be controlled. Repeat each question several times and report the number of runs; answers can vary.

Suggested unbranded questions:

1. Which Indian cooking kits suit a beginner without a spice collection?
2. Where can I buy a pre-measured spice blend for lentil dal in the United States?
3. What should I buy to make tandoori chicken at home?
4. Which spice blend fits a vegan spinach curry?
5. What spices do I need for Kashmiri rogan josh?
6. I need one teaspoon of cumin for a recipe. What should I buy?

The sixth question is a relevance check: a forced blend recommendation would be a failure, even if it mentions Moji.

Use a worksheet with these columns:

```text
run_id, date, platform, mode_or_model, search_used, prompt_id,
moji_named, moji_url_cited, product_match_correct, source_urls,
claim_errors, transcript_reference, notes
```

Report brand-name mention rate and official-domain citation rate separately. Neither is the same as a Business Hub "mention" metric. OpenAI's current documentation defines its online-business mentions using website references, and available insights may be incomplete. [Business Hub metric definitions](https://help.openai.com/en/articles/20001635-setting-up-your-business-on-chatgpt).

## 4. Website and sales outcomes

Use tagged links for the demonstration and each partner integration so those visits can be distinguished. Keep canonical source URLs in the catalog; add attribution parameters at the distribution layer. Measure visits, recipe-to-product clicks, add-to-carts, purchases, and conversion rate by channel when available.

For native assistant referrals, preserve the actual referrer/source evidence. Missing referral information does not prove no AI influence, and a rise in direct traffic does not prove AI caused it. Compare with the baseline and record simultaneous advertising, discounts, press coverage, and website changes.

## Review cadence

Review correctness before each release, API behavior when the SDK/model changes, consumer questions weekly during the first month, and commercial outcomes once there is enough traffic to interpret. These are suggested work practices; this repository does not create scheduled automations.
