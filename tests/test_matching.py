import copy
import unittest

from moji_demo.catalog import load_catalog, validate_catalog
from moji_demo.evaluation import evaluate
from moji_demo.matching import match_recipes, parse_offline_prompt
from moji_demo.tools import dispatch_tool


class MatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def test_public_snapshot_is_complete(self):
        report = validate_catalog(self.catalog)
        self.assertEqual(report["products"], 14)
        self.assertGreaterEqual(report["recipes"], 12)

    def test_reference_evaluation(self):
        report = evaluate()
        self.assertEqual(report["passed"], report["cases"], report)

    def test_unavailable_product_does_not_match(self):
        catalog = copy.deepcopy(self.catalog)
        next(p for p in catalog["products"] if p["id"] == "dahl-masala")["availability"] = "out_of_stock"
        self.assertEqual(match_recipes("dal", catalog=catalog)["status"], "no_match")

    def test_unknown_recipe_diet_does_not_pass(self):
        catalog = copy.deepcopy(self.catalog)
        for recipe in catalog["recipes"]:
            if recipe["product_id"] == "dahl-masala":
                recipe["vegan"] = None
        self.assertEqual(match_recipes("dal", vegan=True, catalog=catalog)["status"], "no_match")

    def test_unknown_salt_does_not_pass(self):
        catalog = copy.deepcopy(self.catalog)
        next(p for p in catalog["products"] if p["id"] == "gobi-masala")["contains_added_salt"] = None
        self.assertEqual(match_recipes("gobi", no_added_salt=True, catalog=catalog)["status"], "no_match")

    def test_aliases_have_word_boundaries(self):
        self.assertEqual(match_recipes("dahlia flowers", catalog=self.catalog)["status"], "needs_clarification")

    def test_schema_rejects_orphan_recipe(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["recipes"][0]["product_id"] = "does-not-exist"
        with self.assertRaisesRegex(ValueError, "unknown product_id"):
            validate_catalog(catalog)

    def test_schema_rejects_external_source(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["products"][0]["source_urls"] = ["https://example.org/fake"]
        with self.assertRaisesRegex(ValueError, "official source_urls"):
            validate_catalog(catalog)

    def test_tool_rejects_invalid_model_arguments(self):
        for args in ({"dish":"dal", "vegan":"true"}, {"dish":"dal", "max_minutes":True},
                     {"dish":"dal", "max_minutes":-1}, {"dish":"dal", "command":"shell"},
                     {"dish":""}, {"dish":"x" * 501}):
            self.assertIn("error", dispatch_tool("match_recipes", args))

    def test_tool_rejects_unknown_function(self):
        self.assertIn("error", dispatch_tool("buy_product", {"dish":"dal"}))

    def test_offline_parser_does_not_offer_spice_substitution(self):
        args = parse_offline_prompt("I need one teaspoon of cumin for dal")
        self.assertTrue(args["single_spice"])
        self.assertEqual(match_recipes(catalog=self.catalog, **args)["status"], "no_match")

    def test_offline_parser_preserves_constraints(self):
        args = parse_offline_prompt("Vegan dal with no added salt in 20 minutes")
        self.assertTrue(args["vegan"])
        self.assertTrue(args["no_added_salt"])
        self.assertEqual(args["max_minutes"], 20)

    def test_unbundled_specific_dishes_do_not_match_related_base_recipes(self):
        for dish in ("palak paneer", "palak with tofu", "spinach curry with paneer",
                     "dal makhani", "gobi manchurian"):
            with self.subTest(dish=dish):
                result = match_recipes(dish, catalog=self.catalog)
                self.assertEqual(result["status"], "no_match")
                self.assertFalse(result["matches"])

    def test_multiple_dishes_do_not_silently_choose_the_longest_alias(self):
        for dish in ("dal and chicken curry", "dal & chicken curry", "potato curry or cauliflower curry"):
            with self.subTest(dish=dish):
                self.assertEqual(match_recipes(dish, catalog=self.catalog)["status"], "needs_clarification")

    def test_compound_kitchari_alias_is_one_dish(self):
        result = match_recipes("rice and lentils", vegan=True, catalog=self.catalog)
        self.assertEqual(result["status"], "matched")
        self.assertEqual({m["product"]["id"] for m in result["matches"]}, {"kitchari-masala"})

    def test_unsupported_allergy_diet_and_heat_constraints_are_explicit(self):
        for prompt in ("vegan cauliflower with a nut allergy", "gluten-free dal",
                       "cauliflower without almonds", "dal with no chili heat",
                       "vegetarian chicken curry"):
            with self.subTest(prompt=prompt):
                result = match_recipes(catalog=self.catalog, **parse_offline_prompt(prompt))
                self.assertEqual(result["status"], "needs_clarification")
                self.assertFalse(result["matches"])

    def test_common_individual_spice_requests_do_not_return_a_mixed_packet(self):
        for prompt in ("I need cumin for dal", "Can I replace turmeric in dal?",
                       "Where can I buy whole black cardamom for dal?", "cumin"):
            with self.subTest(prompt=prompt):
                args = parse_offline_prompt(prompt)
                self.assertTrue(args["single_spice"])
                self.assertEqual(match_recipes(catalog=self.catalog, **args)["status"], "no_match")

    def test_pantry_spice_mention_alone_is_not_a_substitution_request(self):
        result = match_recipes(catalog=self.catalog, **parse_offline_prompt("I have cumin, lentils, onions and tomatoes"))
        self.assertEqual(result["status"], "matched")

    def test_baingan_variant_is_not_replaced_by_the_other_eggplant_recipe(self):
        for dish, expected in (("baingan bharta", "baingan-bharta"), ("tamarind eggplant", "tzok-vangun")):
            with self.subTest(dish=dish):
                result = match_recipes(dish, catalog=self.catalog)
                self.assertEqual({m["recipe"]["id"] for m in result["matches"]}, {expected})

    def test_wings_variant_does_not_combine_alternative_marinades(self):
        for dish, expected in (("chicken wings with tomato marinade", "masala-wings-tomato"),
                               ("chicken wings with hot sauce", "masala-wings-hot-sauce"),
                               ("chicken wings without hot sauce", "masala-wings-tomato")):
            with self.subTest(dish=dish):
                result = match_recipes(dish, catalog=self.catalog)
                self.assertEqual({m["recipe"]["id"] for m in result["matches"]}, {expected})
        generic = match_recipes("chicken wings", catalog=self.catalog)
        self.assertEqual(len(generic["matches"]), 2)

    def test_numeric_hour_limit_is_applied_and_strict_under_is_respected(self):
        args = parse_offline_prompt("dal under 1 hour")
        self.assertEqual(args["max_minutes"], 59)
        self.assertEqual(match_recipes(catalog=self.catalog, **args)["status"], "matched")
        args = parse_offline_prompt("potato curry under 30 minutes")
        self.assertEqual(args["max_minutes"], 29)
        self.assertEqual(match_recipes(catalog=self.catalog, **args)["status"], "no_match")

    def test_unsupported_time_forms_are_not_treated_as_unlimited(self):
        for prompt in ("dal under one hour", "dal within half an hour", "dal in 1.5 hours", "dal in 1 hour 30 minutes"):
            with self.subTest(prompt=prompt):
                result = match_recipes(catalog=self.catalog, **parse_offline_prompt(prompt))
                self.assertEqual(result["status"], "needs_clarification")

    def test_multi_use_blend_does_not_return_an_unrelated_burger_for_dal(self):
        result = match_recipes("garam masala for dal", catalog=self.catalog)
        self.assertEqual(result["status"], "needs_clarification")

    def test_blend_salt_filter_is_not_a_finished_meal_claim(self):
        result = match_recipes("potato curry", no_added_salt=True, catalog=self.catalog)
        self.assertEqual(result["status"], "matched")
        self.assertIn("blend only", result["message"])
        self.assertIn("recipe may still call for salt", result["message"])


if __name__ == "__main__":
    unittest.main()
