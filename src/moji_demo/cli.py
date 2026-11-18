"""Run key-free matching, provider examples, and evidence checks."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import load_catalog, validate_catalog
from .evaluation import evaluate
from .matching import match_recipes, parse_offline_prompt


def render_offline(result: dict) -> str:
    lines = ["Offline catalog demo (no AI model called)",
             "Catalog snapshot: " + result["catalog_verified_at"],
             result["scope"], "", result["message"]]
    for match in result["matches"]:
        product, recipe = match["product"], match["recipe"]
        lines += ["", product["name"] + " → " + recipe["title"],
                  "Product: " + product["product_url"], "Recipe: " + recipe["url"]]
        if recipe.get("servings"):
            lines.append("Recipe yield: " + str(recipe["servings"]))
        if recipe.get("total_minutes"):
            lines.append("Source total time: " + str(recipe["total_minutes"]) + " minutes")
        else:
            lines.append("Total elapsed time: not verified; check recipe and marinating notes.")
        lines += ["Ingredients:"] + ["- " + s for s in recipe["ingredients"]]
        lines += ["Method:"] + [str(i) + ". " + s for i, s in enumerate(recipe["instructions"], 1)]
        notes = product.get("notes", []) + recipe.get("notes", [])
        if notes:
            lines += ["Source notes:"] + ["- " + n for n in notes]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Source-backed Moji recipe and spice-kit demo")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("offline", "openai", "claude"):
        command = sub.add_parser(name)
        command.add_argument("--prompt", required=True, help="A cooking question")
        if name == "offline":
            command.add_argument("--json", action="store_true", help="Print structured tool result")
        else:
            command.add_argument("--model", help="Override the provider model")
    validation = sub.add_parser("validate", help="Check catalog integrity and public provenance")
    validation.add_argument("--catalog", type=Path, help="Validate a staged catalog instead of the bundled snapshot")
    sub.add_parser("evaluate", help="Run deterministic catalog regression cases")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            print(json.dumps(validate_catalog(load_catalog(args.catalog)), indent=2))
        elif args.command == "evaluate":
            report = evaluate()
            print(json.dumps(report, indent=2))
            return 0 if report["passed"] == report["cases"] else 1
        elif args.command == "offline":
            if not args.prompt.strip():
                parser.error("--prompt cannot be empty")
            result = match_recipes(**parse_offline_prompt(args.prompt))
            print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else render_offline(result))
        else:
            from .providers import run_claude, run_openai
            run = run_openai if args.command == "openai" else run_claude
            print(run(args.prompt, model=args.model))
    except (ValueError, OSError, RuntimeError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 2
    return 0
