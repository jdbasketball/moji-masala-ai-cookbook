#!/usr/bin/env python3
"""Recheck approved public sources and stage an atomic catalog candidate.

Recipe curation and dietary claims require human review if source data changes.
Only public mojimasala.com URLs are fetched. This script never reads Shopify
Admin exports, API tokens, customer records, or local .env files.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 5 * 1024 * 1024
sys.path.insert(0, str(ROOT / "src"))
from moji_demo.catalog import validate_catalog


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, text):
        if not self.skip and text.strip():
            self.parts.append(" ".join(text.split()))


def visible_text(document):
    parser = VisibleText()
    parser.feed(document)
    return "\n".join(parser.parts)


def approved_url(url):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in
            ("www.mojimasala.com", "mojimasala.com") or parsed.username or
            parsed.password or parsed.port not in (None, 443)):
        raise ValueError("Only HTTPS public mojimasala.com sources are allowed")
    return url


class PublicOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        approved_url(new_url)
        return super().redirect_request(request, fp, code, message, headers, new_url)


def fetch_text(url):
    approved_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 MojiCatalogDemo/1.0"})
    opener = urllib.request.build_opener(PublicOnlyRedirectHandler())
    with opener.open(request, timeout=30) as response:
        approved_url(response.geturl())
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Source exceeded size limit")
    return raw.decode("utf-8")


def normalized(value):
    return " ".join(html.unescape(str(value)).split())


def extract_product_ingredients(document):
    text = visible_text(document)
    match = re.search(r"Ingredients:\s*(.*?)\s*Quick facts", text, re.S | re.I)
    if not match:
        match = re.search(r"\nIngredients\n(.*?)\nHow to Make", text, re.S | re.I)
    if not match:
        raise ValueError("Cannot find published product ingredient list")
    return [normalized(x).rstrip(".") for x in match.group(1).split(",") if normalized(x)]


def walk_objects(value):
    if isinstance(value, dict):
        yield value
        if "@graph" in value:
            yield from walk_objects(value["@graph"])
    elif isinstance(value, list):
        for item in value:
            yield from walk_objects(item)


def extract_recipe_schema(document):
    pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    recipes = []
    for block in re.findall(pattern, document, re.S | re.I):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        for item in walk_objects(data):
            kinds = item.get("@type", [])
            if kinds == "Recipe" or isinstance(kinds, list) and "Recipe" in kinds:
                recipes.append(item)
    if len(recipes) != 1:
        raise ValueError("Expected exactly one Recipe JSON-LD object")
    recipe = recipes[0]
    if not recipe.get("recipeIngredient") or not recipe.get("recipeInstructions"):
        raise ValueError("Recipe has no measured ingredients or cooking instructions")
    return recipe


def recipe_digest(schema):
    # Ignore ratings/images/marketing copy; changes to cooking facts require review.
    fields = ("name", "prepTime", "cookTime", "totalTime", "recipeYield", "recipeIngredient", "recipeInstructions")
    facts = {field: schema.get(field) for field in fields}
    payload = json.dumps(facts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def refresh(catalog, fetch=None):
    validate_catalog(catalog)
    if fetch is None:
        fetch = fetch_text
    candidate = copy.deepcopy(catalog)
    changes = []
    brand_url = "https://www.mojimasala.com/pages/about-moji-masala-indian-spice-blends"
    brand_text = visible_text(fetch(brand_url)).lower()
    expected_claims = ("13 of 14 blends are vegan", "all 14 blends gluten-free", "sweet masala contains honey powder")
    if any(claim not in brand_text for claim in expected_claims):
        raise ValueError("Published brand dietary claims changed; review all product dietary flags")
    for product in candidate["products"]:
        url = product["product_url"]
        ingredients = extract_product_ingredients(fetch(url))
        if ingredients != product["ingredients"]:
            changes.append(product["id"] + ": ingredient label changed; review dietary flags and curation")
        public_product = json.loads(fetch(url + ".js"))
        expected_salt = any("salt" in ingredient.lower() for ingredient in ingredients)
        if expected_salt != product["contains_added_salt"]:
            changes.append(product["id"] + ": salt label changed; review blend salt flag")
        if public_product.get("handle") != product["id"]:
            raise ValueError("Product handle does not match approved source")
        availability = public_product.get("available")
        product["availability"] = ("in_stock" if availability is True else
                                   "out_of_stock" if availability is False else "unknown")
    schemas = {}
    for recipe in candidate["recipes"]:
        url = recipe["url"]
        if url not in schemas:
            schemas[url] = extract_recipe_schema(fetch(url))
        if recipe_digest(schemas[url]) != recipe.get("source_schema_sha256"):
            changes.append(recipe["id"] + ": cooking source changed; review source ranges and constraints")
    if changes:
        raise ValueError("Catalog unchanged. Source review required:\n" + "\n".join(changes))
    candidate["verified_at"] = datetime.now(timezone.utc).date().isoformat()
    validate_catalog(candidate)
    return candidate


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as out:
            name = out.name
            json.dump(value, out, indent=2, ensure_ascii=False)
            out.write("\n")
        Path(name).replace(path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/catalog.candidate.json")
    args = parser.parse_args()
    try:
        source = json.loads(args.catalog.read_text(encoding="utf-8"))
        candidate = refresh(source)
        atomic_json(args.output, candidate)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("Refresh failed: " + str(exc), file=sys.stderr)
        return 1
    print("Staged reviewed-source candidate: " + str(args.output))
    print("Compare with the checked-in catalog and run moji-demo validate before replacing it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
