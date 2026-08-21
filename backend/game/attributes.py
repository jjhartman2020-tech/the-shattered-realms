"""Canonical Shattered Realms core attribute framework."""

from copy import deepcopy
from typing import Dict

from .progression import MAX_LEVEL, SKILL_POINTS_PER_LEVEL, total_skill_points_earned
from .resources import max_resource_from_attribute, resource_regeneration_per_round

ATTRIBUTE_NAMES = (
    "health", "resource", "strength", "dexterity", "agility",
    "constitution", "intelligence", "wisdom", "charisma", "speed",
    "defense", "luck", "magic",
)

STARTING_SKILL_POINTS = 42
# Backward-compatible aliases while old saves/callers are migrated.
STARTING_ATTRIBUTE_POINTS = STARTING_SKILL_POINTS
ATTRIBUTE_POINTS_PER_LEVEL = SKILL_POINTS_PER_LEVEL
NATURAL_ATTRIBUTE_CAP = 100
BASE_ARMOR_CLASS = 10
BASE_MOVEMENT = 6
BASE_CRITICAL_CHANCE = 5

DEFAULT_ATTRIBUTES = {name: 0 for name in ATTRIBUTE_NAMES}

SKILL_ATTRIBUTE = {
    "athletics": "strength", "grappling": "strength", "might": "strength",
    "sleight_of_hand": "dexterity", "lockpicking": "dexterity", "pickpocketing": "dexterity", "precision": "dexterity",
    "acrobatics": "agility", "stealth": "agility", "evasion": "agility",
    "endurance": "constitution", "fortitude": "constitution",
    "investigation": "intelligence", "arcana": "intelligence", "history": "intelligence", "nature": "intelligence", "engineering": "intelligence",
    "perception": "wisdom", "insight": "wisdom", "survival": "wisdom", "medicine": "wisdom", "animal_handling": "wisdom",
    "persuasion": "charisma", "deception": "charisma", "intimidation": "charisma", "performance": "charisma", "leadership": "charisma",
    "spellcasting": "magic", "channeling": "magic",
}


def _clamp_attribute(value: int) -> int:
    return max(0, min(NATURAL_ATTRIBUTE_CAP, int(value)))


def normalize_attributes(attributes: Dict | None = None) -> Dict[str, int]:
    result = deepcopy(DEFAULT_ATTRIBUTES)
    if not isinstance(attributes, dict):
        return result
    aliases = {"mana": "resource", "durability": "constitution", "defence": "defense"}
    for raw_name, raw_value in attributes.items():
        name = aliases.get(str(raw_name).strip().lower())
        if name in result:
            result[name] = _clamp_attribute(raw_value)
    for raw_name, raw_value in attributes.items():
        name = str(raw_name).strip().lower()
        if name in result:
            result[name] = _clamp_attribute(raw_value)
    return result


def earned_skill_points(level: int) -> int:
    return total_skill_points_earned(level, STARTING_SKILL_POINTS)


def earned_attribute_points(level: int) -> int:
    """Legacy alias. New UI and docs call these Skill Points (SP)."""
    return earned_skill_points(level)


def points_spent(attributes: Dict | None = None) -> int:
    return sum(normalize_attributes(attributes).values())


def validate_allocation(attributes: Dict | None = None, level: int = 1) -> Dict:
    normalized = normalize_attributes(attributes)
    available = earned_skill_points(level)
    spent = sum(normalized.values())
    return {
        "valid": spent <= available,
        "attributes": normalized,
        "points_spent": spent,
        "skill_points_available": available,
        "skill_points_unspent": available - spent,
        # Legacy keys for older callers.
        "points_available": available,
        "points_unspent": available - spent,
        "natural_cap": NATURAL_ATTRIBUTE_CAP,
    }


def attribute_check_bonus(score: int) -> int:
    score = _clamp_attribute(score)
    if score <= 30:
        return score // 3
    return 10 + (score - 30) // 10


def attack_accuracy_bonus(score: int) -> int:
    return attribute_check_bonus(score)


def strength_damage_bonus(strength: int) -> int:
    """Temporary compatibility curve until final damage scaling is redesigned."""
    return _clamp_attribute(strength) // 6


def critical_chance(luck: int) -> int:
    return BASE_CRITICAL_CHANCE + attribute_check_bonus(luck)


def physical_resistance(constitution: int) -> int:
    return _clamp_attribute(constitution) // 5


def status_resistance(constitution: int) -> int:
    return _clamp_attribute(constitution) // 4


def defense_bonus(agility: int, constitution: int, speed: int) -> int:
    """Temporary passive-AC compatibility curve pending final AC rules."""
    return _clamp_attribute(agility) // 9 + _clamp_attribute(constitution) // 15 + _clamp_attribute(speed) // 15


def defend_action_ac_bonus(defense: int) -> int:
    return attribute_check_bonus(defense)


def initiative_bonus(speed: int, dexterity: int | None = None) -> int:
    return attribute_check_bonus(speed)


def movement_spaces(speed: int) -> int:
    speed = _clamp_attribute(speed)
    early = min(speed, 30)
    late = max(0, speed - 30)
    return (BASE_MOVEMENT * 10 + early * 5 + late) // 10


def trading_influence(charisma: int) -> int:
    return attribute_check_bonus(charisma)


def character_sheet_channels(attributes: Dict | None = None, level: int = 1) -> Dict:
    a = normalize_attributes(attributes)
    level = max(1, min(MAX_LEVEL, int(level)))
    max_resource = max_resource_from_attribute(a["resource"])
    resource_regen = resource_regeneration_per_round(a["resource"])
    # Health comes from the Health stat only. Leveling does not grant automatic HP.
    max_health = max(1, a["health"] * 5)
    return {
        "attributes": a,
        "max_health_base": max_health,
        "max_resource_base": max_resource,
        "resource_regeneration_per_round": resource_regen,
        "max_mana_base": max_resource,
        "health_rating": a["health"], "resource_rating": a["resource"],
        "strength_rating": a["strength"], "dexterity_rating": a["dexterity"], "agility_rating": a["agility"],
        "constitution_rating": a["constitution"], "intelligence_rating": a["intelligence"], "wisdom_rating": a["wisdom"],
        "charisma_rating": a["charisma"], "speed_rating": a["speed"], "defense_rating": a["defense"],
        "luck_rating": a["luck"], "magic_rating": a["magic"],
        "strength_check_bonus": attribute_check_bonus(a["strength"]),
        "dexterity_check_bonus": attribute_check_bonus(a["dexterity"]),
        "agility_check_bonus": attribute_check_bonus(a["agility"]),
        "constitution_check_bonus": attribute_check_bonus(a["constitution"]),
        "intelligence_check_bonus": attribute_check_bonus(a["intelligence"]),
        "wisdom_check_bonus": attribute_check_bonus(a["wisdom"]),
        "charisma_check_bonus": attribute_check_bonus(a["charisma"]),
        "speed_check_bonus": attribute_check_bonus(a["speed"]),
        "defense_check_bonus": attribute_check_bonus(a["defense"]),
        "luck_check_bonus": attribute_check_bonus(a["luck"]),
        "magic_check_bonus": attribute_check_bonus(a["magic"]),
        "strength_attack_accuracy": attack_accuracy_bonus(a["strength"]),
        "dexterity_attack_accuracy": attack_accuracy_bonus(a["dexterity"]),
        "magic_attack_accuracy": attack_accuracy_bonus(a["magic"]),
        "strength_damage_bonus": strength_damage_bonus(a["strength"]),
        "critical_chance_percent": critical_chance(a["luck"]),
        "physical_resistance_percent": physical_resistance(a["constitution"]),
        "status_resistance_percent": status_resistance(a["constitution"]),
        "defense_bonus": defense_bonus(a["agility"], a["constitution"], a["speed"]),
        "defend_action_ac_bonus": defend_action_ac_bonus(a["defense"]),
        "initiative_bonus": initiative_bonus(a["speed"]),
        "movement": movement_spaces(a["speed"]),
        "trading_influence_percent": trading_influence(a["charisma"]),
    }


def build_combatant(name: str, team: str, attributes: Dict | None = None, *, level: int = 1,
                    hp: int | None = None, overrides: Dict | None = None) -> Dict:
    a = normalize_attributes(attributes)
    level = max(1, min(MAX_LEVEL, int(level)))
    sheet = character_sheet_channels(a, level)
    actor = {
        "name": name, "team": team, "level": level,
        "attributes": a, "attribute_channels": sheet,
        "hp": sheet["max_health_base"] if hp is None else int(hp),
        "max_hp": sheet["max_health_base"],
        "resource": sheet["max_resource_base"], "max_resource": sheet["max_resource_base"],
        "resource_regeneration_per_round": sheet["resource_regeneration_per_round"],
        "mana": sheet["max_resource_base"], "max_mana": sheet["max_resource_base"],
        "attack_bonus": 0, "damage_bonus": sheet["strength_damage_bonus"],
        "armor_class": BASE_ARMOR_CLASS + sheet["defense_bonus"],
        "initiative_bonus": sheet["initiative_bonus"], "movement": sheet["movement"],
        "defend_action_ac_bonus": sheet["defend_action_ac_bonus"],
        "critical_chance_percent": sheet["critical_chance_percent"],
        "physical_resistance_percent": sheet["physical_resistance_percent"],
        "status_resistance_percent": sheet["status_resistance_percent"],
    }
    if isinstance(overrides, dict):
        actor.update(overrides)
    if "resource" in actor:
        actor["mana"] = int(actor.get("resource", 0) or 0)
    if "max_resource" in actor:
        actor["max_mana"] = int(actor.get("max_resource", 0) or 0)
    return actor
