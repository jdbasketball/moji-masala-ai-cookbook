"""Refresh behavior with simulated public source responses; no network required."""
import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("moji_catalog_refresh", ROOT / "scripts/refresh_catalog.py")
refresh_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh_script)


class CatalogRefreshTests(unittest.TestCase):
    def setUp(self):
        source = json.loads((ROOT / "data/catalog.json").read_text())
        self.recipe = copy.deepcopy(source["recipes"][0])
        product = next(p for p in source["products"] if p["id"] == self.recipe["product_id"])
        self.product = copy.deepcopy(product)
        self.schema = {
            "@type": "Recipe", "name": self.recipe["title"],
            "totalTime": "PT45M", "recipeYield": self.recipe["servings"],
            "recipeIngredient": self.recipe["ingredients"],
            "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in self.recipe["instructions"]],
        }
        self.recipe["source_schema_sha256"] = refresh_script.recipe_digest(self.schema)
        self.catalog = dict(source, products=[self.product], recipes=[self.recipe])
        self.responses = {
            "https://www.mojimasala.com/pages/about-moji-masala-indian-spice-blends":
                "<p>13 of 14 blends are vegan; all 14 blends gluten-free. Sweet Masala contains honey powder.</p>",
            self.product["product_url"]:
                "<p>Ingredients: " + ", ".join(self.product["ingredients"]) + "</p><h2>Quick facts</h2>",
            self.product["product_url"] + ".js": json.dumps({"handle": self.product["id"], "available": False}),
            self.recipe["url"]: self.recipe_html(self.schema),
        }

    @staticmethod
    def recipe_html(schema):
        return '<script type="application/ld+json">' + json.dumps(schema) + '</script>'

    def test_availability_updates_only_when_cooking_sources_match(self):
        original = copy.deepcopy(self.catalog)
        candidate = refresh_script.refresh(self.catalog, fetch=self.responses.__getitem__)
        self.assertEqual(candidate["products"][0]["availability"], "out_of_stock")
        self.assertEqual(candidate["recipes"], self.catalog["recipes"])
        self.assertEqual(self.catalog, original, "Input must never be mutated")

    def test_changed_cooking_hash_refuses_candidate(self):
        changed = copy.deepcopy(self.schema)
        changed["recipeIngredient"][0] = "A changed source quantity"
        self.responses[self.recipe["url"]] = self.recipe_html(changed)
        original = copy.deepcopy(self.catalog)
        with self.assertRaisesRegex(ValueError, "cooking source changed"):
            refresh_script.refresh(self.catalog, fetch=self.responses.__getitem__)
        self.assertEqual(self.catalog, original)

    def test_fetch_failure_leaves_original_and_candidate_files_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "catalog.json"
            candidate_path = Path(directory) / "candidate.json"
            source_text = json.dumps(self.catalog)
            source_path.write_text(source_text)
            candidate_path.write_text("previous reviewed candidate")
            argv = ["refresh_catalog.py", "--catalog", str(source_path), "--output", str(candidate_path)]
            with patch.object(sys, "argv", argv), patch.object(
                refresh_script, "fetch_text", side_effect=OSError("simulated fetch failure")
            ), redirect_stderr(io.StringIO()):
                result = refresh_script.main()
            self.assertEqual(result, 1)
            self.assertEqual(source_path.read_text(), source_text)
            self.assertEqual(candidate_path.read_text(), "previous reviewed candidate")

    def test_changed_ingredients_require_dietary_review(self):
        self.responses[self.product["product_url"]] = "<p>Ingredients: honey, salt</p><h2>Quick facts</h2>"
        with self.assertRaisesRegex(ValueError, "ingredient label changed"):
            refresh_script.refresh(self.catalog, fetch=self.responses.__getitem__)

    def test_redirect_to_external_host_is_rejected_before_request(self):
        handler = refresh_script.PublicOnlyRedirectHandler()
        with self.assertRaisesRegex(ValueError, "Only HTTPS public"):
            handler.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1/private")


if __name__ == "__main__":
    unittest.main()
