"""Repeatable catalog checks; these are not consumer AI visibility measurements."""
from __future__ import annotations

import json

from .catalog import data_path, load_catalog
from .matching import match_recipes, normalize


BASELINE_NAME = "longest_alias_product_lookup"
BASELINE_DEFINITION = (
    "Normalize dish text and catalog aliases, dish types, and product names. "
    "Score each full-word phrase present in the text as 100 times its word count "
    "plus its character count. Return all products tied at the highest positive "
    "score with status matched, or needs_clarification when no phrase matches. "
    "Ignore every constraint flag, recipe availability/completeness, stock, "
    "specific recipe variants, and unsupported intent."
)

# These are editorial labels for the existing regression fixtures, not labels
# inferred from a provider answer. Unknown future failures stay uncategorized.
FAILURE_CATEGORIES = {
    "time_limit_or_unknown_total": {
        "dal-short-time", "tandoori-elapsed-unknown", "eggplant-time-conflict",
    },
    "vegan_finished_recipe": {
        "vegan-chicken", "vegan-chai-honey", "vegan-burger-no-adaptation",
    },
    "added_salt_in_blend": {"dal-added-salt"},
    "individual_spice_substitution": {
        "whole-spice-substitution", "individual-cumin-request", "turmeric-substitution-request",
    },
    "missing_verified_recipe": {"fish-source-review"},
    "unbundled_named_variant": {
        "palak-paneer-not-bundled", "palak-tofu-not-bundled", "dal-makhani-not-bundled",
        "gobi-manchurian-not-bundled",
    },
    "unsupported_requirement": {
        "allergy-cannot-be-verified", "gluten-free-filter-not-supported", "no-heat-filter-not-supported",
    },
    "unsupported_time_syntax": {"spelled-hour-limit-clarify", "fractional-hour-limit-clarify"},
    "ambiguous_or_unverified_combination": {
        "multiple-dishes-clarify", "multi-use-blend-dish-combination",
    },
}


def alias_product_baseline(dish: str, catalog: dict) -> dict:
    """A deliberately limited product lookup, not a recipe validator."""
    text = normalize(dish) if isinstance(dish, str) else ""
    ranked = []
    for product in catalog["products"]:
        scores = []
        for alias in product["aliases"] + product["dish_types"] + [product["name"]]:
            phrase = normalize(alias)
            if phrase and " " + phrase + " " in " " + text + " ":
                scores.append(100 * len(phrase.split()) + len(phrase))
        ranked.append((product["id"], max(scores, default=0)))
    best = max((score for _, score in ranked), default=0)
    products = sorted(pid for pid, score in ranked if score == best and score > 0)
    return {"status": "matched" if products else "needs_clarification", "products": products}


def _category(case_id: str) -> str:
    return next((name for name, ids in FAILURE_CATEGORIES.items() if case_id in ids), "uncategorized")


def evaluate() -> dict:
    catalog = load_catalog()
    with data_path("evaluation.json").open(encoding="utf-8") as handle:
        cases = json.load(handle)
    results = []
    baseline_failures = {}
    for case in cases:
        response = match_recipes(catalog=catalog, **case["arguments"])
        found = sorted(set(m["product"]["id"] for m in response["matches"]))
        passed = response["status"] == case["expected_status"] and found == sorted(case["expected_products"])
        baseline = alias_product_baseline(case["arguments"]["dish"], catalog)
        baseline["passed"] = (baseline["status"] == case["expected_status"] and
                              baseline["products"] == sorted(case["expected_products"]))
        if not baseline["passed"]:
            category = _category(case["id"])
            baseline["failure_category"] = category
            baseline_failures.setdefault(category, []).append(case["id"])
        results.append({"id": case["id"], "passed": passed, "status": response["status"],
                        "products": found, "expected_status": case["expected_status"],
                        "expected_products": case["expected_products"], "baseline": baseline})
    positive = [result for result in results if result["expected_status"] == "matched"]
    no_product = [result for result in results if not result["expected_products"]]
    baseline = {
        "name": BASELINE_NAME,
        "definition": BASELINE_DEFINITION,
        "metric": "Exact expected status and unique product-ID set, both required.",
        "cases": len(results),
        "passed": sum(result["baseline"]["passed"] for result in results),
        "failure_categories": [
            {"category": category, "count": len(ids), "case_ids": ids}
            for category, ids in sorted(baseline_failures.items())
        ],
        "subsets": {
            "expected_product_matches": {
                "cases": len(positive),
                "baseline_passed": sum(result["baseline"]["passed"] for result in positive),
                "guarded_passed": sum(result["passed"] for result in positive),
            },
            "expected_no_products": {
                "cases": len(no_product),
                "baseline_passed": sum(result["baseline"]["passed"] for result in no_product),
                "guarded_passed": sum(result["passed"] for result in no_product),
            },
        },
        "limitations": (
            "These are hand-authored regression fixtures used while developing the guards, "
            "not held-out data, model accuracy, consumer visibility, or a statistical benchmark. "
            "The product-only baseline intentionally lacks the recipe tool's validation features. "
            "This comparison does not measure recipe selection, factual wording, or citations."
        ),
    }
    return {"scope": "Offline deterministic catalog regression, not model quality or consumer visibility.",
            "cases": len(results), "passed": sum(r["passed"] for r in results),
            "results": results, "baseline": baseline}
