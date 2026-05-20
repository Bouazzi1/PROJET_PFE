from __future__ import annotations

from datetime import date
from math import exp
from typing import Any

import numpy as np
import pandas as pd

BUDGET_LEVELS = {"budget": 0, "standard": 1, "luxury": 2}
PROFILE_TYPES = {"student": 0, "young": 1, "family": 2, "couple": 3, "business": 4, "senior": 5}
CATEGORIES = {"budget": 0, "standard": 1, "luxury": 2, "adventure": 3, "religious": 4}
AUDIENCES = {"student": 0, "young": 1, "family": 2, "couple": 3, "business": 4, "senior": 5, "all": 6}
LANGUAGES = {"fr": 0, "ar": 1}
CLIMATES = {"Méditerranéen": 0, "Mediterraneen": 0, "Désertique": 1, "Desertique": 1, "Océanique": 2, "Oceanique": 2, "Semi-aride": 3}

FEATURE_COLUMNS = [
    "budget_level",
    "profile_type_encoded",
    "preferred_language",
    "budget_numeric",
    "price_normalized",
    "duration_days",
    "category_encoded",
    "target_audience_encoded",
    "visa_required",
    "has_spa",
    "has_pool",
    "has_beach",
    "has_flight",
    "is_all_inclusive",
    "hotel_stars",
    "climate_encoded",
    "is_religious",
    "budget_match_score",
    "audience_match",
    "price_ratio",
    "season_match",
    "visa_obstacle",
]

BASE_BUDGETS = {
    "student": {"budget": 2200, "standard": 3000, "luxury": 4800},
    "young": {"budget": 2600, "standard": 3800, "luxury": 6500},
    "family": {"budget": 3200, "standard": 5200, "luxury": 9000},
    "couple": {"budget": 3000, "standard": 5200, "luxury": 10500},
    "business": {"budget": 3600, "standard": 6500, "luxury": 12000},
    "senior": {"budget": 3000, "standard": 5000, "luxury": 8000},
}


def encode(mapping: dict[str, int], value: Any, default: int = 0) -> int:
    return mapping.get(str(value or "").strip(), default)


def estimated_budget(client: dict[str, Any]) -> float:
    profile = client.get("profile_type", "young")
    preference = client.get("budget_preference", "standard")
    return float(BASE_BUDGETS.get(profile, BASE_BUDGETS["young"]).get(preference, 3800))


def current_season(today: date | None = None) -> str:
    month = (today or date.today()).month
    if month in (3, 4, 5):
        return "Printemps"
    if month in (6, 7, 8):
        return "Été"
    if month in (9, 10, 11):
        return "Automne"
    return "Hiver"


def contains_any(values: list[str] | tuple[str, ...] | str | None, needles: tuple[str, ...]) -> int:
    if values is None:
        text = ""
    elif isinstance(values, str):
        text = values
    else:
        text = " ".join(map(str, values))
    normalized = text.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a")
    return int(any(needle in normalized for needle in needles))


def budget_match_score(price: float, budget: float) -> float:
    if budget <= 0:
        return 0.0
    ratio = price / budget
    if ratio <= 1.0:
        return max(0.55, 1.0 - abs(1.0 - ratio) * 0.55)
    return max(0.0, exp(-2.2 * (ratio - 1.0)))


def audience_match(client: dict[str, Any], program: dict[str, Any]) -> int:
    target = program.get("target_audience", "all")
    return int(target == "all" or target == client.get("profile_type"))


def interest_match_score(client: dict[str, Any], program: dict[str, Any]) -> float:
    profile = client.get("profile_type")
    category = program.get("category")
    amenities = program.get("amenities") or []
    includes = program.get("includes") or []
    text = " ".join(map(str, amenities + includes)).lower()

    score = 0.45
    if category == client.get("budget_preference"):
        score += 0.25
    if profile == "student" and category == "budget":
        score += 0.25
    if profile == "business" and (category == "luxury" or "business" in text):
        score += 0.25
    if profile == "family" and (program.get("target_audience") == "family" or "tout" in text or "piscine" in text):
        score += 0.25
    if profile == "young" and category in {"adventure", "budget"}:
        score += 0.25
    if profile == "couple" and (category == "luxury" or "spa" in text):
        score += 0.25
    if profile == "senior" and category in {"standard", "religious"}:
        score += 0.20
    return min(score, 1.0)


def season_match(program: dict[str, Any], today: date | None = None) -> int:
    best = str(program.get("best_season") or "Toute l'année")
    season = current_season(today)
    return int("Toute" in best or season in best)


def build_features(client: dict[str, Any], program: dict[str, Any], price_scale: float = 12000.0) -> dict[str, float]:
    budget = estimated_budget(client)
    price = float(program.get("price", 0) or 0)
    amenities = program.get("amenities") or []
    includes = program.get("includes") or []
    all_text_values = list(amenities) + list(includes)

    features = {
        "budget_level": encode(BUDGET_LEVELS, client.get("budget_preference"), 1),
        "profile_type_encoded": encode(PROFILE_TYPES, client.get("profile_type"), 1),
        "preferred_language": encode(LANGUAGES, client.get("preferred_language"), 0),
        "budget_numeric": budget,
        "price_normalized": price / price_scale,
        "duration_days": float(program.get("duration_days", 7) or 7),
        "category_encoded": encode(CATEGORIES, program.get("category"), 1),
        "target_audience_encoded": encode(AUDIENCES, program.get("target_audience"), 6),
        "visa_required": int(bool(program.get("visa_required", False))),
        "has_spa": contains_any(all_text_values, ("spa", "hammam", "bien-etre")),
        "has_pool": contains_any(all_text_values, ("piscine", "pool")),
        "has_beach": contains_any(all_text_values, ("plage", "beach", "mer")),
        "has_flight": contains_any(all_text_values, ("vol", "flight", "billet")),
        "is_all_inclusive": contains_any(all_text_values, ("all inclusive", "all-inclusive", "tout inclus", "tout-inclus")),
        "hotel_stars": float(program.get("hotel_stars", 3) or 3),
        "climate_encoded": encode(CLIMATES, program.get("climate"), 0),
        "is_religious": int(program.get("category") == "religious"),
        "budget_match_score": budget_match_score(price, budget),
        "audience_match": audience_match(client, program),
        "price_ratio": price / max(budget, 1.0),
        "season_match": season_match(program),
        "visa_obstacle": int(bool(program.get("visa_required", False))),
    }
    return {key: float(features[key]) for key in FEATURE_COLUMNS}


def score_label(client: dict[str, Any], program: dict[str, Any]) -> float:
    no_visa = 1.0 - float(bool(program.get("visa_required", False)))
    score = (
        0.30 * budget_match_score(float(program.get("price", 0) or 0), estimated_budget(client))
        + 0.25 * audience_match(client, program)
        + 0.20 * interest_match_score(client, program)
        + 0.15 * season_match(program)
        + 0.10 * no_visa
    )
    return float(np.clip(score, 0.0, 1.0))


def make_training_frame(clients: list[dict[str, Any]], programs: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for client in clients:
        for program in programs:
            row = {
                "client_id": client["id"],
                "program_id": program["id"],
                "label": score_label(client, program),
            }
            row.update(build_features(client, program))
            rows.append(row)
    return pd.DataFrame(rows)
