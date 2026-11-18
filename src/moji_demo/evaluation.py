"""Repeatable catalog checks; these are not consumer AI visibility measurements."""
from __future__ import annotations

import json

from .catalog import data_path, load_catalog
from .matching import match_recipes


def evaluate() -> dict:
    catalog = load_catalog()
    with data_path("evaluation.json").open(encoding="utf-8") as handle:
        cases = json.load(handle)
    results = []
    for case in cases:
        response = match_recipes(catalog=catalog, **case["arguments"])
        found = sorted(set(m["product"]["id"] for m in response["matches"]))
        passed = response["status"] == case["expected_status"] and found == sorted(case["expected_products"])
        results.append({"id": case["id"], "passed": passed, "status": response["status"],
                        "products": found, "expected_status": case["expected_status"],
                        "expected_products": case["expected_products"]})
    return {"scope": "Offline deterministic catalog regression, not model quality or consumer visibility.",
            "cases": len(results), "passed": sum(r["passed"] for r in results), "results": results}
