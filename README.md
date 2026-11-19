# Moji Masala AI Cookbook Demo

A recipe-to-spice matching example for OpenAI and Claude, built from [moji masala®](https://www.mojimasala.com/) product and recipe information. The dataset copies existing website recipes and records links to their source pages. Running this demo does not add or change recipes on the Moji website.

Ask for a dish and cooking constraints. The assistant calls a shared catalog tool, receives suitable products and source recipes, and explains the match with links. The same matching logic runs without an API key in offline mode.

This is a Moji-owned demonstration. It has not been accepted into either company's official cookbook, and it does not change the recommendations made in other ChatGPT or Claude conversations.

## Quick start

Use Python 3.9 or later from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

python -m moji_demo validate
python -m moji_demo offline --prompt "I want to make vegan lentil dal"
python -m moji_demo evaluate
```

Offline mode uses a small, deterministic prompt parser to demonstrate the catalog. It is not a general language model or a substitute for the provider examples.

## OpenAI example

New to API keys? See [API setup](docs/api-setup.md) for account links and a hidden-input local setup helper.

Install the optional provider SDKs and set your key locally:

```bash
python -m pip install -e '.[providers]'
export OPENAI_API_KEY="your-api-key"
python -m moji_demo openai --prompt "I have lentils, onions and tomatoes. Which Moji blend and recipe fit a vegan dinner?"
```

The default model is `gpt-6.2-sol`; set `OPENAI_MODEL` to override it. API usage is billed by the provider. Keep keys in your local environment or a secret manager; do not commit them.

## Claude example

```bash
export ANTHROPIC_API_KEY="your-api-key"
python -m moji_demo claude --prompt "I want to cook tandoori chicken. Which spice blend fits, and where is the source recipe?"
```

The default model is `claude-sonnet-5-5`; set `ANTHROPIC_MODEL` to override it. Model references and provider-specific details are in [examples/README.md](examples/README.md). The examples use the same catalog and filtering tool, so differences in wording do not change which records satisfy the structured constraints.

## What this teaches

1. Extract dish and cooking requirements through a model tool call.
2. Match aliases such as dal/dahl to a dish-specific product.
3. Apply deterministic filters for vegan recipes, added salt, and documented total time.
4. Return source ingredients, quantities, instructions, and links to the model.
5. Handle unsuitable requests instead of forcing a brand recommendation.

For example, a blend is not a measured replacement for a single spice in an unrelated recipe. Missing timing or dietary data cannot satisfy a strict constraint. Gluten-free information does not establish that a product is safe for every allergy; check the current package and source page.

## How it works

```text
Cooking request
    -> OpenAI Responses API / Claude Messages API
    -> match_recipes(dish, vegan, no_added_salt, max_minutes, single_spice)
    -> validated catalog filters
    -> matched product + recipe + source URLs, or a no-match explanation
    -> assistant answer
```

The initial snapshot contains 14 products and 15 curated recipe variants across 13 products. Variants separate alternatives already present in the source recipes. Fish Masala is included as a product, but its cooking recipe is omitted pending review of source timing and temperature information.

The catalog is a dated snapshot, not a live inventory or pricing service. The assistant should not invent substitutions, serving conversions, current prices, availability, or recipe measurements. An independently connected application must keep its catalog current and verify the offer on the merchant site.

Walk through the [recipe-to-spice notebook](notebooks/recipe_to_spice.ipynb) for a GitHub-previewable introduction with key-free examples and optional provider calls. It uses your installed Python environment; Jupyter is only needed to run the notebook interactively.

See [data provenance](data/README.md), the [verification record](docs/verification.md), [rollout plan](docs/rollout-plan.md), [measurement worksheet](docs/measurement.md), and [cookbook proposal drafts](docs/cookbook-proposals.md).

## Validation

```bash
python -m unittest discover -s tests -v
python -m moji_demo validate
python -m moji_demo evaluate
```

The [GitHub Actions template](docs/github-actions/checks.yml) installs the optional SDKs and runs checks on Python 3.9 and 3.12 without provider secrets. It is supplied as a template because the publishing login lacks GitHub's `workflow` scope. An authorized owner can enable it by placing it at `.github/workflows/checks.yml`. Provider transport tests exercise the tool-call conversation without making paid API requests. The real-SDK transport tests are skipped if the SDK extras are absent in a local environment. These tests do not prove that a real provider account accepts the selected model or that a model's final wording is always accurate.

On November 19, 2026, all three OpenAI live smoke cases passed using `gpt-6.2-sol`: a sourced vegan dal match, refusal of a measured single-spice substitution, and refusal of an unsupported 30-minute tandoori total. These six real API requests verify those three behaviors, not general model accuracy or consumer recommendations. Claude live verification is pending its API key. See the [live check results](docs/live-verification.md) and [verification record](docs/verification.md).

## Distribution and outcomes

The demo creates a reusable dataset, two integration examples, and a repeatable correctness check. It can support adoption by cooking apps, meal planners, and developers. Official cookbook inclusion requires separate maintainer review. A public repository or a connected catalog does not guarantee consumer recommendations, traffic, or sales.

OpenAI says Shopify catalog data is already integrated into ChatGPT product discovery. Business Hub separately offers eligible businesses tools for managing their information and available insights. Verify Moji's current account and catalog state before adding another feed. [Product discovery announcement](https://openai.com/index/powering-product-discovery-in-chatgpt/), [Business Hub instructions](https://help.openai.com/en/articles/20001635-setting-up-your-business-on-chatgpt).

## Licensing

The original software code and project documentation are provided under the [MIT License](LICENSE). Catalog facts, source recipe text, brand assets, and third-party materials are excluded from that grant and retain their existing rights. Source attribution is recorded with the data. The project does not grant rights to the Moji Masala, OpenAI, Anthropic, or Claude names or trademarks.
