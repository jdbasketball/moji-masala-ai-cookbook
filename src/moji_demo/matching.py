"""Deterministic matching. Products and finished recipes are checked separately."""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .catalog import load_catalog


# These source-specific aliases distinguish existing alternatives; they do not
# create adaptations or assert that a generic recipe makes a different dish.
RECIPE_VARIANTS = {
    "baingan-masala": {
        "baingan-bharta": ("baingan bharta", "bharta"),
        "tzok-vangun": ("tzok vangun", "tamarind eggplant", "tamarind"),
    },
    "chicken-wings-masala": {
        "masala-wings-tomato": ("tomato marinade", "tomato", "tomatoes"),
        "masala-wings-hot-sauce": ("hot sauce",),
    },
}

INDIVIDUAL_SPICES = (
    r"(?:cumin|turmeric|coriander|cinnamon|cardamom|cloves?|mustard|"
    r"pepper|paprika|ginger|fenugreek|saffron|nutmeg|chili|chilli)"
)


def _has_phrase(text: str, phrase: str) -> bool:
    return " " + normalize(phrase) + " " in " " + text + " "


def _individual_spice_request(text: str) -> bool:
    modifiers = r"(?:(?:some|more|a|an|ground|whole|powdered|of|pure|black|green|red|yellow|white|crushed|fresh)\s+)*"
    patterns = (
        r"\b(?:teaspoons?|tsp|tablespoons?|tbsp|individual|single|pure)\s+" + modifiers + INDIVIDUAL_SPICES + r"\b",
        r"\b(?:need|buy|find|get|looking for|ran out of|out of|missing)\s+" + modifiers + INDIVIDUAL_SPICES + r"\b",
        r"\b(?:replace|substitute|swap|instead of|replacement for)\b[^.;!?]*\b" + INDIVIDUAL_SPICES + r"\b",
        r"\b" + INDIVIDUAL_SPICES + r"\s+(?:replacement|substitute)\b",
    )
    return any(re.search(pattern, text) for pattern in patterns) or bool(
        re.fullmatch(modifiers + INDIVIDUAL_SPICES, text)
    )


def _unsupported_constraint(text: str) -> Optional[str]:
    if re.search(r"\b(?:allerg\w*|anaphyla\w*|celiac|coeliac)\b", text):
        return "allergy or medical dietary safety"
    if re.search(r"\b(?:nut|peanut|tree nut|gluten|wheat|dairy|milk|lactose|soy|egg|sesame) free\b", text):
        return "the requested allergen or ingredient-free requirement"
    if re.search(r"\b(?:without|no|avoid) (?:nuts?|peanuts?|almonds?|cashews?|walnuts?|gluten|wheat|dairy|milk|soy|eggs?|sesame)\b", text):
        return "the requested ingredient exclusion"
    if re.search(r"\b(?:no (?:chili |chilli )?heat|not spicy|non spicy|no chilli|no chili|without chili|without chilli|mild only)\b", text):
        return "the requested heat restriction for the finished recipe"
    if re.search(r"\b(?:vegetarian|keto|ketogenic|paleo|low carb|low sodium|low salt|sodium free)\b", text):
        return "the requested diet or nutrition restriction"
    return None


def _unsupported_named_dish(text: str) -> bool:
    spinach_variant = re.search(r"\b(?:palak|saag|spinach)\b", text) and re.search(r"\b(?:paneer|tofu)\b", text)
    return bool(spinach_variant or re.search(
        r"\b(?:(?:dal|dahl|daal) makhani|gobi manchurian|manchurian gobi)\b", text))


def _time_request(raw: str) -> tuple:
    """Only simple whole-number maximum minutes/hours are supported offline."""
    text = normalize(raw)
    units = r"(?:minutes?|mins?|hours?|hrs?)"
    found = list(re.finditer(
        r"\b(?:(under|less than|within|in|at most|no more than|up to)\s+)?(\d+)\s*(" + units + r")\b", text
    ))
    fractional = re.search(r"\d+[.,]\d+\s*" + units + r"\b", raw.lower())
    if fractional or len(found) > 1 or re.search(r"\bat least\b.*\b" + units + r"\b", text):
        return None, True
    if found:
        match = found[0]
        minutes = int(match.group(2)) * (60 if match.group(3).startswith(("h", "hr")) else 1)
        if match.group(1) in {"under", "less than"}:
            minutes -= 1
        return minutes, False
    return None, bool(re.search(r"\b" + units + r"\b", text))


def _independent_products(text: str, products: list) -> set:
    spans = []
    for product in products:
        phrases = product["aliases"] + product["dish_types"] + [product["name"]]
        for phrase in phrases:
            phrase = normalize(phrase)
            for found in re.finditer(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text):
                spans.append((found.start(), found.end(), product["id"]))
    # "rice and lentils" names kitchari. Its nested "lentils" alias must
    # not be counted as a second requested dal recipe.
    return {
        product_id for start, end, product_id in spans
        if not any(other_id != product_id and other_start <= start and other_end >= end
                   and other_end - other_start > end - start
                   for other_start, other_end, other_id in spans)
    }


def _narrow_variants(text: str, product_id: str, recipes: list) -> list:
    variants = RECIPE_VARIANTS.get(product_id, {})
    named = {rid for rid, aliases in variants.items() if any(_has_phrase(text, alias) for alias in aliases)}
    if not named:
        return recipes
    # A negated variant is an exclusion, not a request for that recipe.
    excluded = {
        rid for rid, aliases in variants.items()
        if any(re.search(r"\b(?:no|without|avoid|not) " + re.escape(normalize(alias)) + r"\b", text)
               for alias in aliases)
    }
    included = named - excluded
    permitted = included if included else set(variants) - excluded
    return [recipe for recipe in recipes if recipe["id"] in permitted]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _score(text: str, product: dict) -> int:
    phrases = product["aliases"] + product["dish_types"] + [product["name"]]
    scores = []
    for phrase in phrases:
        phrase = normalize(phrase)
        if phrase and " " + phrase + " " in " " + text + " ":
            scores.append(len(phrase.split()) * 100 + len(phrase))
    return max(scores, default=0)


def match_recipes(dish: str, vegan: bool = False, no_added_salt: bool = False,
                  max_minutes: Optional[int] = None, single_spice: bool = False,
                  catalog: Optional[dict] = None) -> dict:
    catalog = catalog if catalog is not None else load_catalog()
    base = {"catalog_verified_at": catalog["verified_at"], "matches": [],
            "scope": "Moji Masala catalog only; this is not a comparison of all brands."}
    text = normalize(dish) if isinstance(dish, str) else ""
    if single_spice or _individual_spice_request(text):
        return dict(base, status="no_match", message=(
            "This catalog contains spice blends. A blend is not a measured substitute "
            "for one individual spice in an existing recipe."))
    if not isinstance(dish, str) or not dish.strip():
        return dict(base, status="needs_clarification", message="Which dish would you like to cook?")
    unsupported = _unsupported_constraint(text)
    if unsupported:
        return dict(base, status="needs_clarification", message=(
            "This tool cannot verify " + unsupported + ". It currently filters vegan "
            "recipes, added salt in the blend, and documented total time. Check the "
            "current package and recipe; no suitable or safe match is being asserted."))
    if _unsupported_named_dish(text):
        return dict(base, status="no_match", message=(
            "That specific dish or variant is not bundled as a verified recipe. "
            "A related blend or base dish does not establish a matching recipe."))
    prose_minutes, unsupported_time = _time_request(dish)
    if unsupported_time:
        return dict(base, status="needs_clarification", message=(
            "The time request is outside this demo's supported syntax. State one "
            "maximum as whole-number minutes or hours, such as 'within 30 minutes' "
            "or 'under 1 hour'. Compound, fractional, and spelled-out times are not parsed."))
    if prose_minutes is not None:
        max_minutes = prose_minutes if max_minutes is None else min(max_minutes, prose_minutes)
    if (re.search(r"\b(?:and|or|plus|alongside|together|as well as)\b", text) or
        re.search(r"[&+;,\n]", dish)) and len(
        _independent_products(text, catalog["products"])
    ) > 1:
        return dict(base, status="needs_clarification", message=(
            "Your request names more than one dish or recipe option. Which one should "
            "I match first? This tool does not plan multiple dishes in one lookup."))
    ranked = [(p, _score(text, p)) for p in catalog["products"]]
    ranked = [(p, score) for p, score in ranked if score > 0]
    if not ranked:
        return dict(base, status="needs_clarification", message=(
            "No verified dish match. Name a dish or main ingredient, such as dal, "
            "cauliflower, or tandoori chicken. Do not infer a substitute."))
    best = max(score for _, score in ranked)
    selected = [p for p, score in ranked if score == best]
    if any(p["blend_type"] == "multi_use" for p in selected) and len(
        _independent_products(text, catalog["products"])
    ) > 1:
        return dict(base, status="needs_clarification", message=(
            "A multi-use blend and a separate dish were named. This snapshot does not "
            "verify that combination as a recipe. Choose a bundled recipe or check "
            "the source before adapting the blend."))
    matches = []
    reasons = set()
    for product in selected:
        if product["availability"] == "out_of_stock":
            reasons.add("The matching product was out of stock in the snapshot.")
            continue
        if vegan and product["vegan"] is not True:
            reasons.add("The matching blend is not verified vegan.")
            continue
        if no_added_salt and product["contains_added_salt"] is not False:
            reasons.add("The matching blend is not verified to have no added salt.")
            continue
        source_recipes = [
            r for r in catalog["recipes"] if r["product_id"] == product["id"]
        ]
        recipes = _narrow_variants(text, product["id"], source_recipes)
        for recipe in recipes:
            if vegan and recipe.get("vegan") is not True:
                reasons.add("The finished recipe is not verified vegan, even if its blend is vegan.")
                continue
            minutes = recipe.get("total_minutes")
            if max_minutes is not None and (minutes is None or minutes > max_minutes):
                reasons.add("The source recipe does not verify the requested time limit.")
                continue
            matches.append({"product": product, "recipe": recipe,
                            "source_urls": sorted(set(product["source_urls"] + recipe["source_urls"]))})
        if not recipes:
            reasons.add("No verified source recipe matches the requested variant." if source_recipes else
                        "No verified complete recipe is bundled for that blend.")
    if not matches:
        return dict(base, status="no_match", message=" ".join(sorted(reasons)) or
                    "No verified recipe satisfies all requested constraints.")
    salt_note = (
        " The no-added-salt filter applies to the blend only. The published recipe "
        "may still call for salt; this is not a salt-free or low-sodium meal claim."
    ) if no_added_salt else ""
    return dict(base, status="matched", matches=matches, message=(
        "Follow the linked recipe and its measured packet quantity. Stock is a dated "
        "snapshot, not a live promise; check the product page before purchasing. "
        "No prices or delivery promises are supplied by this tool." + salt_note))


def parse_offline_prompt(prompt: str) -> dict:
    """Small visible heuristic for key-free demos; live models use the tool schema."""
    text = normalize(prompt)
    minutes, _ = _time_request(prompt)
    single_spice = _individual_spice_request(text)
    return {"dish": prompt, "vegan": bool(re.search(r"\bvegan\b", text)) and
            not bool(re.search(r"\b(?:not|non) vegan\b", text)),
            "no_added_salt": any(x in text for x in ("no added salt", "salt free", "without salt", "no salt")),
            "max_minutes": minutes,
            "single_spice": single_spice}
