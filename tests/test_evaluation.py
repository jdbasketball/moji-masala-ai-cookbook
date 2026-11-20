"""Check the deliberately weak lookup baseline against meaningful counterexamples."""

import unittest

from moji_demo.catalog import load_catalog
from moji_demo.evaluation import alias_product_baseline, evaluate
from moji_demo.matching import match_recipes


class BaselineComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def test_keyword_hit_cannot_establish_a_vegan_chicken_recipe(self):
        baseline = alias_product_baseline("chicken curry", self.catalog)
        guarded = match_recipes("chicken curry", vegan=True, catalog=self.catalog)
        self.assertEqual(baseline, {"status": "matched", "products": ["chicken-curry-masala"]})
        self.assertEqual(guarded["status"], "no_match")
        self.assertEqual(guarded["matches"], [])

    def test_product_lookup_ignores_missing_recipe_evidence(self):
        baseline = alias_product_baseline("fish curry", self.catalog)
        guarded = match_recipes("fish curry", catalog=self.catalog)
        self.assertEqual(baseline["products"], ["fish-masala"])
        self.assertEqual(baseline["status"], "matched")
        self.assertEqual(guarded["status"], "no_match")

    def test_baseline_still_handles_basic_aliases_and_word_boundaries(self):
        for alias in ("dal", "dahl"):
            self.assertEqual(alias_product_baseline(alias, self.catalog)["products"], ["dahl-masala"])
        self.assertEqual(alias_product_baseline("dahlia flowers", self.catalog),
                         {"status": "needs_clarification", "products": []})

    def test_long_compound_alias_does_not_become_a_second_lentil_product(self):
        self.assertEqual(alias_product_baseline("rice and lentils", self.catalog)["products"],
                         ["kitchari-masala"])

    def test_existing_evaluation_fields_and_fixture_labels_are_preserved(self):
        report = evaluate()
        self.assertEqual(report["passed"], report["cases"])
        self.assertEqual(report["cases"], len(report["results"]))
        for result in report["results"]:
            self.assertIn("expected_status", result)
            self.assertIn("expected_products", result)
            baseline = result["baseline"]
            exact = (baseline["status"] == result["expected_status"] and
                     baseline["products"] == sorted(result["expected_products"]))
            self.assertEqual(baseline["passed"], exact)

    def test_category_counts_partition_actual_baseline_failures(self):
        report = evaluate()
        baseline = report["baseline"]
        failed_ids = {row["id"] for row in report["results"] if not row["baseline"]["passed"]}
        categorized = [case_id for group in baseline["failure_categories"] for case_id in group["case_ids"]]
        self.assertEqual(set(categorized), failed_ids)
        self.assertEqual(len(categorized), len(failed_ids))
        self.assertEqual(sum(group["count"] for group in baseline["failure_categories"]),
                         baseline["cases"] - baseline["passed"])
        positive = baseline["subsets"]["expected_product_matches"]
        self.assertEqual(positive["baseline_passed"], positive["cases"])
        self.assertEqual(positive["guarded_passed"], positive["cases"])


if __name__ == "__main__":
    unittest.main()
