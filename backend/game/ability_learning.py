"""Ability learning, tier gates, and four-slot loadout rules."""
from copy import deepcopy
from typing import Dict, List

from .progression import ABILITY_TIER_COSTS

MAX_ABILITY_SLOTS = 4
ABILITY_TIER_LEVELS = {
    "beginner": 1,
    "novice": 3,
    "expert": 10,
    "master": 25,
    "legendary": 50,
}
TIER_ORDER = ("beginner", "novice", "expert", "master", "legendary")


def normalize_tier(tier: str | None) -> str:
    value = str(tier or "beginner").strip().lower()
    return value if value in ABILITY_TIER_COSTS else "beginner"


def highest_unlocked_tier(level: int) -> str:
    level = max(1, int(level or 1))
    unlocked = "beginner"
    for tier in TIER_ORDER:
        if level >= ABILITY_TIER_LEVELS[tier]: unlocked = tier
    return unlocked


def tier_is_unlocked(level: int, tier: str) -> bool:
    tier = normalize_tier(tier)
    return int(level or 1) >= ABILITY_TIER_LEVELS[tier]


def ability_ap_cost(ability: Dict) -> int:
    return ABILITY_TIER_COSTS[normalize_tier(ability.get("tier"))]


def available_to_learn(player: Dict, abilities: List[Dict]) -> List[Dict]:
    known = {str(a.get("name", "")).strip().lower() for a in player.get("equipped_abilities", []) if isinstance(a, dict)}
    level = int(player.get("level", 1) or 1)
    result = []
    for raw in abilities:
        if not isinstance(raw, dict): continue
        ability = deepcopy(raw); tier = normalize_tier(ability.get("tier")); ability["tier"] = tier
        if str(ability.get("name", "")).strip().lower() in known: continue
        if not tier_is_unlocked(level, tier): continue
        ability["ability_point_cost"] = ability_ap_cost(ability)
        result.append(ability)
    return result


def learn_ability(player: Dict, ability: Dict, forget_index: int | None = None) -> Dict:
    """Buy and equip an ability. A full four-slot loadout requires forgetting one ability."""
    if not isinstance(ability, dict) or not str(ability.get("name", "")).strip():
        raise ValueError("Invalid ability")
    level = int(player.get("level", 1) or 1)
    tier = normalize_tier(ability.get("tier"))
    if not tier_is_unlocked(level, tier):
        raise ValueError(f"{tier.title()} abilities unlock at Level {ABILITY_TIER_LEVELS[tier]}")
    cost = ability_ap_cost(ability)
    ap = int(player.get("ability_points", 0) or 0)
    if ap < cost: raise ValueError(f"You need {cost} AP but only have {ap}")
    equipped = player.get("equipped_abilities")
    if not isinstance(equipped, list): equipped = []
    if any(isinstance(a, dict) and str(a.get("name", "")).strip().lower() == str(ability.get("name", "")).strip().lower() for a in equipped):
        raise ValueError("You already know that ability")
    forgotten = None
    if len(equipped) >= MAX_ABILITY_SLOTS:
        if forget_index is None or not 0 <= int(forget_index) < len(equipped):
            raise ValueError("All 4 ability slots are full; choose one current ability to forget")
        forgotten = equipped.pop(int(forget_index))
    learned = deepcopy(ability); learned["tier"] = tier; learned["ability_point_cost"] = cost
    equipped.append(learned)
    player["equipped_abilities"] = equipped
    # In this design forgotten means forgotten, not stored in a reserve list.
    player["unlocked_abilities"] = deepcopy(equipped)
    player["ability_points"] = ap - cost
    return {"learned": deepcopy(learned), "forgotten": deepcopy(forgotten), "ability_points_remaining": player["ability_points"]}
