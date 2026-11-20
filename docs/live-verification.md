# Live provider check results

Verified November 19, 2026, with the official provider SDKs. Tool arguments, returned match statuses, product and recipe IDs, source links, and answer content were reviewed against the bundled catalog. These are small end-to-end smoke checks, separate from the 33 deterministic catalog cases.

| Provider | Actual served model | Core cases | Successful requests | Result |
| --- | --- | --- | --- | --- |
| OpenAI SDK 2.48.0 | `gpt-6.2-sol` | 3 | 6 | Pass |
| Anthropic SDK 0.125.0 | `claude-sonnet-5-5` | 3, plus one focused wording follow-up | 8 | Pass |

## Behaviors checked on both providers

| Case | Observed behavior | Result |
| --- | --- | --- |
| Vegan dinner using lentils, onions, and tomatoes | Both models requested `vegan: true`; the tool returned `dahl-masala`. Answers linked the exact official product and recipe pages and used the source's red-lentil timing, yield, and ingredient quantities. | Pass |
| Replacing one teaspoon of cumin with a packet | Both models requested `single_spice: true`; the tool returned `no_match` with no products. Answers refused a measured substitution and explained that the blend is used with its own recipe. | Pass |
| Tandoori chicken from scratch in 30 minutes, including marinating | Both models requested `max_minutes: 30`; the tool returned `no_match` with no products. Answers refused to claim a recipe met that unsupported complete-time limit. | Pass |

The vegan dal answers linked [Dahl Masala](https://www.mojimasala.com/products/dahl-masala) and the [official Dahl recipe](https://www.mojimasala.com/blogs/recipes/dahl-masala-recipe). They specified the red-lentil version, 45 minutes, 4–5 servings, and the source's full-packet method. Price and stock were directed to the current product page rather than invented.

## Review finding and focused follow-up

Claude's first tandoori answer correctly refused the 30-minute request, but promised it could show the complete total time if the user removed the limit. The source's complete elapsed time remains unknown. The shared prompt was refined to prohibit promising that missing facts will become available when a constraint is relaxed.

A focused Claude rerun preserved `max_minutes: 30` and `no_match`, and explicitly said it could not promise a listed total even after removing the cap. This follow-up used two additional successful requests. No new recipe, timing, or substitution was invented to make the request pass.

## Recorded usage and scope

- OpenAI's six successful responses reported 6,486 input tokens and 470 output tokens.
- Claude's first six successful responses reported 12,090 input tokens and 1,849 output tokens; its focused follow-up reported 3,540 input tokens and 425 output tokens.

These are recorded token counts, not calculated cash charges. API pricing, caching, and promotional credits affect billing. Preliminary setup failures returned no model answer and are not included in the successful-request counts.

Credentials were supplied through hidden process input or ignored local configuration. They were not committed to Git or included in results. Local structured traces are excluded from Git; this summary contains no credentials or account identifiers.

These checks establish the recorded behaviors only. They do not establish broad model accuracy, live inventory accuracy, official cookbook acceptance, consumer ChatGPT or Claude visibility, or sales lift.
