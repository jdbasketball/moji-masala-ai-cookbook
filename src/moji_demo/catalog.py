"""Load the public catalog snapshot and validate its grounding fields."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse


def data_path(filename: str) -> Path:
    source = Path(__file__).resolve().parents[2] / "data" / filename
    installed = Path(sys.prefix) / "share" / "moji-masala-ai-cookbook" / filename
    for candidate in (source, installed):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Cannot find bundled data: " + filename)


def _public_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return (parsed.scheme == "https" and parsed.hostname in
            {"www.mojimasala.com", "mojimasala.com"} and not parsed.username)


def validate_catalog(catalog: dict) -> dict:
    errors = []
    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    try:
        date.fromisoformat(catalog.get("verified_at", ""))
    except (TypeError, ValueError):
        errors.append("verified_at must be an ISO date")
    products = catalog.get("products", [])
    recipes = catalog.get("recipes", [])
    if not isinstance(products, list) or not isinstance(recipes, list):
        raise ValueError("products and recipes must be arrays")
    if not products or not recipes:
        errors.append("at least one product and verified recipe are required")
    product_ids = set()
    for p in products:
        pid = p.get("id")
        if not isinstance(pid, str) or not pid or pid in product_ids:
            errors.append("missing or duplicate product ID: " + str(pid))
        product_ids.add(pid)
        if not p.get("name") or not _public_url(p.get("product_url")):
            errors.append(str(pid) + ": name and official product URL required")
        for field in ("aliases", "dish_types", "ingredients"):
            if not isinstance(p.get(field), list) or not p[field] or not all(
                isinstance(s, str) and s.strip() for s in p[field]
            ):
                errors.append(str(pid) + ": nonempty " + field + " required")
        for flag in ("vegan", "vegetarian", "gluten_free", "contains_added_salt"):
            if flag not in p or (p[flag] is not None and type(p[flag]) is not bool):
                errors.append(str(pid) + ": " + flag + " must be boolean or null")
        if p.get("heat") not in {"none", "mild", "medium", "unknown"}:
            errors.append(str(pid) + ": invalid heat")
        if p.get("blend_type") not in {"dish_specific", "multi_use"}:
            errors.append(str(pid) + ": invalid blend_type")
        if p.get("availability") not in {"unknown", "in_stock", "out_of_stock"}:
            errors.append(str(pid) + ": invalid availability")
        if not p.get("source_urls") or not all(_public_url(s) for s in p["source_urls"]):
            errors.append(str(pid) + ": official source_urls required")
    recipe_ids = set()
    for r in recipes:
        rid = r.get("id")
        if not isinstance(rid, str) or not rid or rid in recipe_ids:
            errors.append("missing or duplicate recipe ID: " + str(rid))
        recipe_ids.add(rid)
        if r.get("product_id") not in product_ids:
            errors.append(str(rid) + ": unknown product_id")
        if not r.get("title") or not _public_url(r.get("url")):
            errors.append(str(rid) + ": title and official recipe URL required")
        for field in ("ingredients", "instructions", "source_urls"):
            if not isinstance(r.get(field), list) or not r[field] or not all(
                isinstance(s, str) and s.strip() for s in r[field]
            ):
                errors.append(str(rid) + ": nonempty " + field + " required")
        if not all(_public_url(s) for s in r.get("source_urls", [])):
            errors.append(str(rid) + ": sources must be official URLs")
        for flag in ("vegan", "vegetarian", "gluten_free"):
            if flag not in r or (r[flag] is not None and type(r[flag]) is not bool):
                errors.append(str(rid) + ": " + flag + " must be boolean or null")
        minutes = r.get("total_minutes")
        if minutes is not None and (type(minutes) is not int or minutes <= 0):
            errors.append(str(rid) + ": total_minutes must be positive integer or null")
    if errors:
        raise ValueError("Invalid catalog:\n- " + "\n- ".join(errors))
    return {"status": "valid", "products": len(products), "recipes": len(recipes),
            "verified_at": catalog["verified_at"]}


def load_catalog(path: Optional[Path] = None) -> dict:
    with (path or data_path("catalog.json")).open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    validate_catalog(catalog)
    return catalog
