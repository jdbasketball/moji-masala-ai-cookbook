"""One validated tool shared by both provider examples."""
from __future__ import annotations

from .matching import match_recipes

TOOL_NAME = "match_recipes"
TOOL_DESCRIPTION = (
    "Look up official Moji Masala recipes and compatible spice blends. Extract the dish "
    "and constraints without weakening the user's request. Set vegan for a vegan finished "
    "meal, no_added_salt only for a no-added-salt blend request, max_minutes for a stated "
    "total-time limit, and single_spice when an individual spice is required. Unknown "
    "facts cannot satisfy strict filters. Returns exact source ingredients and steps; "
    "never treat mixed blends as measured one-spice substitutes. This is a dated, "
    "single-brand catalog, not live stock or a market-wide comparison."
)
TOOL_PARAMETERS = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "dish": {"type": "string", "minLength": 1, "maxLength": 500,
                 "description": "The requested dish, main ingredient, or spice; retain relevant user wording."},
        "vegan": {"type": "boolean", "description": "Require a vegan finished recipe."},
        "no_added_salt": {"type": "boolean", "description": "Require verified no added salt in the blend; not a low-sodium claim."},
        "max_minutes": {"type": ["integer", "null"], "minimum": 1, "maximum": 10080,
                        "description": "Maximum total recipe minutes, or null if unrestricted."},
        "single_spice": {"type": "boolean", "description": "True if the request needs an individual spice, not a blend."}
    },
    "required": ["dish", "vegan", "no_added_salt", "max_minutes", "single_spice"]
}


def dispatch_tool(name: str, arguments: dict) -> dict:
    if name != TOOL_NAME:
        return {"error": "Unknown tool: " + str(name)}
    if not isinstance(arguments, dict):
        return {"error": "Tool arguments must be a JSON object."}
    unknown = set(arguments) - set(TOOL_PARAMETERS["properties"])
    if unknown:
        return {"error": "Unsupported arguments: " + ", ".join(sorted(unknown))}
    dish = arguments.get("dish")
    if not isinstance(dish, str) or not 1 <= len(dish.strip()) <= 500:
        return {"error": "dish must be a nonempty string of at most 500 characters."}
    for field in ("vegan", "no_added_salt", "single_spice"):
        if type(arguments.get(field, False)) is not bool:
            return {"error": field + " must be a boolean."}
    minutes = arguments.get("max_minutes")
    if minutes is not None and (type(minutes) is not int or not 1 <= minutes <= 10080):
        return {"error": "max_minutes must be null or an integer from 1 to 10080."}
    return match_recipes(**arguments)
