# Official cookbook proposals

Proposal bodies are prepared in [submissions/openai-proposal.md](submissions/openai-proposal.md) and [submissions/claude-proposal.md](submissions/claude-proposal.md). Submission receipts will be recorded here after posting. The Moji-owned demonstration works independently of any maintainer decision.

## Shared educational proposal

**Title:** From dinner request to shopping list: matching recipes to spice kits with verified constraints.

**Problem:** A language model can associate a dish with a product while overlooking recipe quantities, added salt, dietary distinctions, or unsupported substitutions. A useful assistant must retrieve evidence and decline matches that fail the requested constraints.

**Learning objectives:** Extract structured requirements through tool use; resolve dish aliases; separate semantic matching from deterministic checks; preserve recipe/product sources; compare provider tool-call lifecycles; evaluate unsuitable as well as successful requests.

**Example data:** A small, transparently attributed catalog of Moji Masala blends and source recipes. Moji is the disclosed brand supplying the example data. The code can be adapted to another catalog with the same schema. Data rights and recipe attribution must remain explicit.

**Differentiation:** Demonstrate the errors made by simple keyword matching, then show how explicit constraints and source provenance change the result. A basic product-search demonstration alone would overlap existing examples. Both provider integrations passed three real smoke cases. The [evaluated comparison](baseline-comparison.md) records 33/33 guarded matches versus 11/33 alias-only matches on the existing hand-authored regression fixtures. Both preserve nine expected product matches. These are developed-on examples, not held-out accuracy or consumer visibility measurements.

**Proposed notebook outline:**

1. Load and validate the dated catalog.
2. Show a simple alias/keyword baseline and its limitations.
3. Define the recipe-matching tool schema.
4. Run a complete provider tool-call conversation.
5. Apply vegan, added-salt, and documented-time constraints.
6. Demonstrate a no-match result for an individual-spice request.
7. Review source-grounded answers and evaluate results.
8. Explain refresh, data rights, and deployment limitations.

## OpenAI route

Use the [current contribution instructions](https://github.com/openai/openai-cookbook/blob/main/CONTRIBUTING.md). New proposals require maintainer review before a new-cookbook PR. An outside contributor should open or reuse a feature request and wait for confirmation that a maintainer shared the proposal. Finished publication requires Developer Experience approval; review and merging are not guaranteed.

The OpenAI version should focus on the Responses API function-call lifecycle and reproducible evaluations. Explain the additional learning value beyond the [MCP product-catalog guide](https://github.com/openai/openai-cookbook/blob/main/examples/mcp/mcp_tool_guide.ipynb) and [product matching tutorial](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb).

**Draft summary:**

> We propose a focused tutorial showing how to turn cooking requirements into a source-backed recipe/product match. It uses a disclosed Moji Masala dataset to demonstrate structured tool arguments, deterministic constraint checking, and evaluations that penalize unsupported substitutions. The example teaches a reusable catalog workflow and records cases where no product fits.

## Claude route

Use the [proposal guidelines](https://github.com/anthropics/claude-cookbooks/blob/main/.github/ISSUE_GUIDELINES.md), [proposal template](https://github.com/anthropics/claude-cookbooks/blob/main/.github/ISSUE_TEMPLATE/cookbook_proposal.yml), and [contribution guide](https://github.com/anthropics/claude-cookbooks/blob/main/CONTRIBUTING.md). Anthropic seeks runnable examples with practical educational value and generally excludes primarily promotional notebooks or duplicated documentation.

The Claude version should teach the Messages API tool-use/tool-result lifecycle and evidence-based answer construction. Explain the additional learning value beyond the [retrieval guide](https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/retrieval_augmented_generation/guide.ipynb) and [citations example](https://github.com/anthropics/claude-cookbooks/blob/main/misc/using_citations.ipynb). The current demonstration returns source URLs; do not describe that as native API citation support unless the submitted notebook implements it.

**Draft summary:**

> This tutorial demonstrates a Claude recipe assistant that retrieves a product/recipe record through a client tool, checks explicit cooking constraints, and explains a supported match using source information. A transparent brand dataset makes the problem reproducible. Evaluations include spelling variants, missing facts, conflicting constraints, and requests for an individual spice that a blend cannot replace.

## Submission preparation

- The repositories' contribution rules and proposal templates were reviewed, and issue searches found no direct Moji or spice-matching duplicate.
- Moji approved public release of the current 15 recipe variants with recipe rights reserved and source links retained. Original code is MIT; the recipe/catalog material is excluded from that grant.
- Both live provider examples and the offline baseline comparison completed; see [verification](verification.md).
- The proposals offer original synthetic or openly licensed fixtures for an official MIT tutorial, preserving the rights of the external Moji dataset.
- If maintainers invite an implementation, adapt it to that repository's notebook, dependency, testing, and author requirements.
- Keep the official proposal focused on developer learning; link the branded implementation as transparently attributed supporting material.

Cookbook inclusion offers potential developer distribution. It does not train future models on demand or force Moji into consumer recommendations.
