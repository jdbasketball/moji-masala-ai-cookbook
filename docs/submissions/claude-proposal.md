### Preflight Checklist

- [x] I have searched existing cookbooks and this topic isn't already covered
- [x] This proposal focuses on Claude API/SDK capabilities (not external frameworks)
- [x] I am prepared to implement this cookbook (or have a clear implementation plan)

### Problem Statement

Recipe/product assistants can retrieve a plausible item while overlooking a constraint that makes its recipe unsuitable. A vegan blend does not make a bundled chicken recipe vegan, and a dish-name match does not prove that the recipe meets a strict total-time limit. Developers need a runnable example that distinguishes candidate lookup from evidence-based eligibility and handles missing facts without forcing a recommendation.

### Claude Capabilities Demonstrated

The proposed self-contained Python notebook uses the official Anthropic SDK and Claude Messages API directly:

- Define a client tool with an `input_schema` for dish, vegan, added-salt, time, and individual-spice requirements.
- Complete the `tool_use` / `tool_result` conversation, preserving the assistant tool-use content and matching tool IDs.
- Return validated recipe records or explicit `no_match` / `needs_clarification` results, then have Claude explain that evidence.
- Keep source URLs with the tool result and include them in the final answer. This is source-link provenance, **not native API citations**.

Learning objectives are to design tool arguments, separate model interpretation from deterministic checks, preserve unknown values, and evaluate refusal/clarification as well as successful matches.

Proposed outline:

1. Load and validate a small recipe/product catalog with source attribution.
2. Demonstrate why an alias-only lookup returns unsuitable candidates.
3. Implement the schema and complete Messages API tool loop.
4. Compare a suitable vegan lentil recipe, an unsupported measured-spice substitution, and a time limit the source cannot establish.
5. Evaluate statuses and product selection; inspect final wording separately.
6. Explain refresh, missing-data behavior, fixture licensing, and deployment limits.

### Differentiation

The [retrieval guide](https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/retrieval_augmented_generation/guide.ipynb) teaches retrieval, and the [citations example](https://github.com/anthropics/claude-cookbooks/blob/main/misc/using_citations.ipynb) teaches native citations. This proposal concentrates on what happens after a candidate is retrieved: explicit recipe eligibility, refusal when a fact is unknown, and a reproducible comparison showing which selected mistakes the checks prevent. It requires no external framework or commercial service beyond the Claude API.

### Additional Context

The [implemented reference demo](https://github.com/jdbasketball/moji-masala-ai-cookbook) has an [introductory notebook](https://github.com/jdbasketball/moji-masala-ai-cookbook/blob/codex%2Finitial-demo/notebooks/recipe_to_spice.ipynb), a direct Claude SDK loop, 61 passing local tests, and 14 products with 15 recipe variants.

The [deterministic comparison](https://github.com/jdbasketball/moji-masala-ai-cookbook/blob/codex%2Finitial-demo/docs/baseline-comparison.md) records 33/33 fixture matches for guarded lookup versus 11/33 for alias-only lookup; both retain all nine expected product matches. The baseline intentionally ignores constraint flags and recipe completeness. The hand-authored development fixtures are **not held-out data, a model accuracy score, or a statistical benchmark**. Three [live Claude smoke cases](https://github.com/jdbasketball/moji-masala-ai-cookbook/blob/codex%2Finitial-demo/docs/live-verification.md) passed, with one focused follow-up verifying that the answer does not promise an unknown total time.

Disclosure: submitted on behalf of Moji Masala, the reference dataset's brand. Demo code is MIT-licensed; recipe/catalog text retains separate rights and source attribution. We can implement original synthetic or appropriately licensed fixtures for the official MIT-licensed notebook, making the branded project an optional reference. The contribution would teach the API pattern rather than promote a product. We will adapt it to the repository's Python, notebook, formatting, and validation conventions after maintainer feedback.
