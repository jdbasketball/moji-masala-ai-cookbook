# Catalog sources and curation

`catalog.json` contains 14 moji masala® spice blends and 15 curated recipe variants. Public storefront product HTML, public Shopify `.js` product data, and the brand's published Recipe JSON-LD were retrieved on **November 18, 2026**. The checked-in data is a dated demonstration snapshot, not a live inventory or nutrition service. Prices, private Shopify inventory counts, customer data, and account exports are not included.

## Public sources

- [Brand facts and dietary distinctions](https://www.mojimasala.com/pages/about-moji-masala-indian-spice-blends)
- [Dish-to-blend shopping guide](https://www.mojimasala.com/pages/ai-shopping-guide)
- [Salt and sodium guide](https://www.mojimasala.com/pages/salt-and-sodium-guide)
- Each record's `source_urls` links to the precise product and recipe pages. Recipe quantities, steps, yields, and reported times come from those pages; whitespace is normalized.

Product `vegan`, `vegetarian`, and `gluten_free` fields describe the **blend**. Recipe dietary fields describe the selected **prepared variant**. A vegan blend used with chicken does not produce a vegan recipe. A gluten-free blend does not establish a finished dish's allergen freedom. The brand states that products are manufactured in a shared facility; check current labels for allergy decisions.

`contains_added_salt` is a **blend** attribute. Several recipes made with no-added-salt blends separately call for salt. Filtering for a no-added-salt blend must not be represented as a sodium-free or no-added-salt prepared meal.

## Deliberate curation

- Dahl, Aloo, and Palak have vegan serving variants that omit the yogurt accompaniment. Aloo's source explicitly labels yogurt optional; Dahl and Palak's measured main-dish ingredient lists have no dairy. The curation is recorded in each recipe's `notes`.
- Kitchari selects the source's vegetable-oil alternative rather than ghee. No other dairy replacement or protein substitution is invented.
- Baingan's page contains two recipes. Baingan Bharta and Tzok Vangun have separate ingredient/step ranges; their quantities are never combined.
- Wings have two alternative marinades. Each is a separate record with the shared source cooking steps. The hot-sauce version's finished-dish gluten-free status is unknown because the sauce brand determines it.
- Tandoori's bone-in method is kept separate from its tenderloin variation. Dahl's separate fried-onion variation is not appended to the basic method as another consecutive step.
- Sweet Masala contains honey powder, so its chai remains non-vegan with oat milk.
- Garam masala and Sweet Masala are multi-use blends. Their recipes use measured spoonfuls, not whole packets.
- The Fish Masala **product** is included, but no executable fish recipe is bundled. The published source's timing and cooking-temperature guidance require review before this demo should repeat them. A fish request therefore has no verified complete bundled recipe.

## Timing limits and source conflicts

The dataset preserves a published total only when it represents a usable complete recipe estimate. `total_minutes: null` means the demo must not claim a strict time match.

- Rogan Josh now states 15 minutes prep + 75 minutes cooking, plus 4–48 hours marinating: **at least 5 hours 30 minutes elapsed**. Its Recipe JSON-LD reflects that minimum. A minimum is not a guaranteed maximum, so the demo keeps `total_minutes: null` and records `minimum_total_minutes: 330`.
- Tandoori now identifies 50 minutes as oven cooking time, with preparation and refrigerating/marinating for up to 48 hours additional. Its Recipe JSON-LD omits unknown `totalTime`, and the demo keeps the total unknown.
- Baingan now separates about one hour roasting for Bharta from 40 minutes baking for Tzok Vangun, followed by pan cooking. Its previous conflicting 20-minute metadata was removed. The combined page omits unknown preparation/cooking/total durations from Recipe JSON-LD; both demo totals remain unknown.
- Dahl now consistently states 15 minutes prep + 30 minutes cooking (45 minutes total) for the standard red-lentil recipe. Split chickpeas may need about one hour soaking; yellow split peas may need 50–60 minutes cooking. A time-limited recommendation must specify red lentils and explain that times are estimates.
- Availability is a dated public-storefront snapshot. `in_stock` means that a public product was offered for sale when retrieved; it is not an inventory reservation or a promise of current availability.

The four recipe pages above were corrected and their live HTML and Recipe JSON-LD rechecked on November 18, 2026. Their ingredient and direction arrays were verified unchanged. The demo source hashes match the corrected live cooking metadata.

## Refreshing

From the repository root:

```bash
python scripts/refresh_catalog.py
```

This reads only bounded HTTPS URLs on `mojimasala.com`, checks brand dietary claims, product ingredient labels, availability, and hashes of the original recipe cooking facts. It stages `data/catalog.candidate.json` atomically **only if every source succeeds and curated cooking facts remain unchanged**. The checked-in catalog is untouched on any fetch, parsing, or source-change error. Review the candidate, run `python -m moji_demo validate --catalog data/catalog.candidate.json`, and replace the source catalog deliberately. The refresh script also validates both the input and candidate catalog before staging.

If a recipe or ingredient list changes, inspect the source, update the curated variants/dietary flags/notes and `source_schema_sha256`, and rerun validation. The script intentionally refuses to reuse old ingredient/step ranges against changed recipe source data. It does not automatically reinterpret changed cooking instructions.

## Rights and attribution

Original demo code is covered by the repository's code license. Product descriptions, recipes, brand names, and source material remain the property of moji masala® and their respective rightsholders. They are supplied here for this Moji demonstration and are **not relicensed under MIT**. Obtain permission from the rightsholder for other reuse. Linking to or retrieving these public sources does not imply endorsement by OpenAI or Anthropic.
