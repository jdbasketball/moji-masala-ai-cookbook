# Deterministic product-lookup baseline comparison

On November 19, 2026, the guarded matcher satisfied **33 of 33 existing regression fixtures**, while a product-only alias lookup satisfied **11 of 33**. A fixture passes only when both its expected status and its complete set of unique product IDs match. These are local deterministic results. No provider API calls are part of this comparison.

The 33 fixtures are hand-authored examples used during development, including cases that motivated specific guard rules. They are not held-out data or a statistical benchmark. The counts do not establish model accuracy, performance on arbitrary cooking requests, consumer recommendation visibility, or commercial outcomes.

## Baseline definition

Both methods receive the same catalog snapshot and the same dish text. The guarded method also receives the fixture's structured constraint flags.

The baseline deliberately performs only product lookup:

1. Normalize the text, product aliases, dish types, and product names using the same lowercase, accent-stripping, word-token normalization as the matcher.
2. Find full-word phrases present in the dish text. Score each phrase as `100 × word count + character count`.
3. Return every product tied at the highest positive score, with status `matched`.
4. Return no products and status `needs_clarification` if no phrase matches.

It ignores constraint flags, recipe existence and completeness, stock, specific recipe variants, unsupported requirements, and ambiguous intent. It does not generate language or choose a recipe. This intentionally limited baseline demonstrates what the additional validation features cover; it is not a comparison against a complete alternative recipe assistant.

## Observed results

| Existing fixture subset | Fixtures | Baseline exact matches | Guarded exact matches |
| --- | ---: | ---: | ---: |
| Expected a product match | 9 | 9 | 9 |
| Expected no products (`no_match` or `needs_clarification`) | 24 | 2 | 24 |
| All fixtures | **33** | **11** | **33** |

Both methods retained the nine expected product matches. The baseline also handled the unrelated-dish and generic-curry clarification cases correctly. Its remaining 22 failures returned product candidates where the fixture required a refusal or clarification. The difference therefore demonstrates validation on these selected cases, rather than finding more products.

Each baseline failure is assigned one editorial category. These categories describe the existing fixtures; they are not inferred from model answers.

| Baseline failure category | Count | Fixture IDs |
| --- | ---: | --- |
| Added salt in the blend | 1 | `dal-added-salt` |
| Ambiguous or unverified combination | 2 | `multiple-dishes-clarify`, `multi-use-blend-dish-combination` |
| Individual spice substitution | 3 | `whole-spice-substitution`, `individual-cumin-request`, `turmeric-substitution-request` |
| Missing verified recipe | 1 | `fish-source-review` |
| Time limit or unknown complete total | 3 | `dal-short-time`, `tandoori-elapsed-unknown`, `eggplant-time-conflict` |
| Unbundled named variant | 4 | `palak-paneer-not-bundled`, `palak-tofu-not-bundled`, `dal-makhani-not-bundled`, `gobi-manchurian-not-bundled` |
| Unsupported requirement | 3 | `allergy-cannot-be-verified`, `gluten-free-filter-not-supported`, `no-heat-filter-not-supported` |
| Unsupported time syntax | 2 | `spelled-hour-limit-clarify`, `fractional-hour-limit-clarify` |
| Vegan finished recipe | 3 | `vegan-chicken`, `vegan-chai-honey`, `vegan-burger-no-adaptation` |
| **Total** | **22** | |

For example, the `vegan-chicken` fixture asks for `chicken curry` with `vegan=true`. The baseline returns Chicken Curry Masala because its name matches. The guarded matcher returns `no_match`: a vegan spice blend does not make the bundled chicken recipe vegan. Similarly, a Fish Masala keyword hit does not establish a complete verified fish recipe in this snapshot.

## Reproduce

From the repository root, after installing the project:

```bash
python -m moji_demo evaluate
python -m unittest discover -s tests -p test_evaluation.py -v
```

The existing `cases`, `passed`, and `results` fields continue to describe guarded matching. The additive `baseline` object contains its definition, exact-match counts, subset counts, and failure categories. Each existing result now also includes its baseline prediction and whether that prediction passed the same fixture labels. The original fixtures and labels were not changed for this comparison.

The evaluator checks status and product IDs. Recipe-variant selection has separate regression tests; final model wording, quantities, citations, and live API behavior require their own review. A future generalization claim would require independently labeled, held-out requests and stronger comparison methods.
