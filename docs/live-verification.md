# OpenAI live check results

Verified November 19, 2026, using the official OpenAI SDK 2.48.0 and the actual served model `gpt-6.2-sol`. Three end-to-end cases completed in six real Responses API requests. Tool arguments, returned match statuses, product IDs, source links, and answer content were reviewed against the bundled catalog.

| Case | Observed behavior | Result |
| --- | --- | --- |
| Vegan dinner using lentils, onions, and tomatoes | The model requested `vegan: true`; the tool returned `dahl-masala`. The answer linked the exact official product and recipe pages and used the source's red-lentil timing, yield, and ingredient quantities. | Pass |
| Replacing one teaspoon of cumin with a packet | The model requested `single_spice: true`; the tool returned `no_match` with no products. The answer refused a measured substitution and explained that a mixed packet belongs with its own recipe. | Pass |
| Tandoori chicken from scratch in 30 minutes, including marinating | The model requested `max_minutes: 30`; the tool returned `no_match` with no products. The answer refused to claim a recipe met the unsupported complete-time limit. | Pass |

The vegan dal answer linked [Dahl Masala](https://www.mojimasala.com/products/dahl-masala) and the [official Dahl recipe](https://www.mojimasala.com/blogs/recipes/dahl-masala-recipe). It specified the red-lentil version, 45 minutes, 4–5 servings, and the source's full-packet method. It directed shoppers to the product page for current price and stock rather than inventing an offer.

The six responses reported 6,486 input tokens and 470 output tokens in total. These are recorded token counts, not a calculated cash charge. API pricing, cached-token treatment, and credits affect billing.

The credential was supplied through hidden process input and was not written to the repository or included in results. The local structured trace is excluded from Git; this summary includes no account identifiers or credentials.

An earlier attempt on November 18 stopped at HTTP 429, `credit_balance_exhausted`. This November 19 run succeeded after credits were added. Claude still requires its own successful live verification.

These checks establish the three recorded OpenAI behaviors only. They do not establish broad model accuracy, live inventory accuracy, official cookbook acceptance, consumer ChatGPT visibility, or sales lift.
