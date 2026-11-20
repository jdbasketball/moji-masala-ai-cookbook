**Is your feature request related to a problem? Please describe.**

A plausible product lookup can still give an unsuitable cooking recommendation. A vegan spice blend does not make its chicken recipe vegan; a matching dish name does not establish a documented total time; and a packet of blended spices is not a measured replacement for one teaspoon of cumin. Developers need an example that separates retrieving a candidate from verifying that its recipe satisfies the request.

**Describe the solution you'd like**

We propose a focused, self-contained Python notebook using the OpenAI Responses API and official SDK to demonstrate structured function calls, deterministic recipe constraints, and evidence-based refusal or clarification. The model extracts requirements and explains the result; a client-side tool validates the catalog and decides which records satisfy supported constraints.

Learning objectives and outline:

1. Load a small catalog with explicit ingredient quantities, recipe variants, source URLs, and unknown fields.
2. Run an alias-only product lookup and inspect its false matches.
3. Define a recipe-matching function schema and complete the Responses API function-call/function-output loop.
4. Apply vegan, added-salt, individual-spice, and documented-time checks; return `no_match` or `needs_clarification` when evidence is insufficient.
5. Construct an answer from the returned recipe and product source URLs, without inventing substitutions, measurements, or elapsed times.
6. Evaluate status and product selection separately from final model wording, and explain snapshot freshness and licensing.

The emphasis beyond the existing [MCP tool guide](https://github.com/openai/openai-cookbook/blob/main/examples/mcp/mcp_tool_guide.ipynb) and [outfit matching example](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb) is failure analysis after retrieval: when the assistant should reject a tempting candidate and how to test that decision. This uses the SDK directly, without an external orchestration framework.

**Additional context**

An implemented [reference demo](https://github.com/jdbasketball/moji-masala-ai-cookbook) includes an [introductory notebook](https://github.com/jdbasketball/moji-masala-ai-cookbook/blob/codex%2Finitial-demo/notebooks/recipe_to_spice.ipynb), both providers' SDK examples, 61 passing local tests, and a dated catalog of 14 products and 15 recipe variants.

In the [reproducible deterministic comparison](https://github.com/jdbasketball/moji-masala-ai-cookbook/blob/codex%2Finitial-demo/docs/baseline-comparison.md), guarded matching satisfies 33/33 existing fixtures versus 11/33 for alias-only lookup. Both retain all nine expected product matches; the difference is refusal/clarification on selected unsuitable requests. The baseline intentionally ignores constraint flags and recipe completeness. These hand-authored development regression fixtures are **not held-out data, model accuracy, or a statistical benchmark**. Three [live OpenAI smoke cases](https://github.com/jdbasketball/moji-masala-ai-cookbook/blob/codex%2Finitial-demo/docs/live-verification.md) also passed; their small scope is documented separately.

Disclosure: this proposal is submitted on behalf of Moji Masala, which supplies the branded reference dataset. The demo's code is MIT-licensed; its recipe/catalog content retains separate rights and source attribution. For an official notebook, we can implement original synthetic or appropriately licensed fixtures under the Cookbook's licensing requirements, with the branded demo only as an optional reference. This is an educational contribution proposal, not a request for product ranking or endorsement.

Following `CONTRIBUTING.md`, could a maintainer assess whether this topic fits and route it to the internal proposal review? We will wait for that review before opening a full tutorial PR and adapt the implementation to the repository's current conventions.
