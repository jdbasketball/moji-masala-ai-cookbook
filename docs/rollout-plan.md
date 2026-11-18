# Five-step rollout plan

Prepared November 18, 2026. Dates below are proposed work windows, not promises of platform approval or commercial results.

The demo is the implementation asset for steps 2 and 3. Its dataset copies existing Moji website recipes and retains links to their source pages; running the demo does not add or edit website recipes. The other steps require account verification, distribution, and measurement. Completing the code does not complete those business activities.

| Step | Owner | Next actions | Evidence of completion |
| --- | --- | --- | --- |
| 1. Verify commerce distribution | Moji account owner with developer support | Inspect current Shopify/ChatGPT channel state, catalog coverage, product URLs, variants, and prices. Check whether the eligible Moji business is already claimed in Business Hub; follow its verification flow if needed. Fix demonstrated catalog errors before adding another feed. | Dated catalog report; correct product links and offer details; account claim state recorded separately from recommendation results. |
| 2. Maintain the recipe dataset | Moji recipe/content owner | Review each product and linked recipe in `data/catalog.json`. Confirm quantities, instructions, yield, total time, dietary facts, and source URLs. Review changed records after refresh. Keep unknown values explicit. | Catalog validation passes; each recipe has a product and public source; Moji signs off on the content. |
| 3. Verify the two API examples | Developer | Run offline checks; install provider SDKs; run both examples with authorized API keys; review actual tool calls and answers. Check successful matches and rejected substitutions. Record the provider, model, date, costs, and reviewed result. | Passing local checks plus separately recorded real OpenAI and Claude smoke results. Offline mocks alone are insufficient evidence of live integration. |
| 4. Distribute the project | Moji owner and developer | Publish under the selected Moji-controlled GitHub account after repository review. Use the demo to approach relevant recipe/meal-planning developers. Prepare a focused tutorial proposal for each official cookbook following its current process. | Working repository URL, reproducible installation, developer feedback, and any submitted proposal URL. An actual connected application is stronger adoption evidence than a repository star. |
| 5. Measure and improve | Moji marketing/analytics owner | Establish unbranded consumer-question baselines; repeat the same protocol; track correct mentions, citations, product visits, and attributed purchases. Keep API demo scores separate from consumer assistant visibility. | Dated worksheet with denominators, source links, traffic evidence, attribution limits, and changes since baseline. |

Moji's earlier local audit recorded an active ChatGPT Shopify channel on November 5, 2026. That is historical evidence to recheck, not proof of today's coverage or ranking. OpenAI documents Shopify catalog integration and Business Hub management; neither channel provides control over every recommendation. [Shopify discovery announcement](https://openai.com/index/powering-product-discovery-in-chatgpt/), [Business Hub instructions](https://help.openai.com/en/articles/20001635-setting-up-your-business-on-chatgpt).

## First 30 days

| Window | Work | Decision at the end |
| --- | --- | --- |
| Days 1–7 | Approve the public dataset, run both live API checks, verify the current commerce catalog, and record consumer visibility baselines. | Is the product/recipe information accurate enough to distribute? Resolve errors before promotion. |
| Days 8–14 | Publish the reviewed repository and a short demonstration. Identify a small group of relevant cooking-app developers. Prepare cookbook proposals using the drafts in this project. | Can a developer reproduce the example without direct help? |
| Days 15–21 | Collect implementation feedback and test an actual integration where a developer agrees to connect the catalog. Submit educational proposals only through the documented routes. | Are users finding suitable recipes and reaching the correct product pages? |
| Days 22–30 | Repeat the consumer-question protocol, review source and catalog freshness, and compare visits and purchases with the baseline. | Continue channels producing useful adoption or qualified visits; repair inaccurate answers before expanding. |

Platform reviews and search indexing may take longer than this schedule. No external proposal or outreach is submitted by this repository itself.

## Expected advantages and possible outcomes

| Outcome level | What may be observed | What it does and does not establish |
| --- | --- | --- |
| Immediate implementation benefit | One maintainable product/recipe dataset, consistent matching logic, examples for both providers, and a regression check. | Confirms a useful technical asset exists. It does not establish consumer reach. |
| Developer adoption | A cooking or meal-planning application connects to the catalog and uses it for suitable requests. | Creates a measurable distribution path within that application; it does not make the tool universal across Claude or ChatGPT. |
| Discovery improvement | More accurate citations or relevant mentions in repeated consumer tests. | Suggests visibility changed under the recorded conditions; it does not prove the repository caused the change. |
| Commercial gain | Qualified recipe visits, product clicks, add-to-carts, and purchases. | Evaluate using actual analytics and attribution evidence. A brand mention alone is not revenue. |
| Limited initial impact | The code works, but no developers adopt it and consumer answers change little. | A plausible early result. Improve distribution, data usefulness, and content based on evidence rather than assuming publication should produce sales. |

Do not forecast a percentage sales lift before establishing traffic, conversion, and adoption baselines. Separate targets Moji chooses from measured results.
