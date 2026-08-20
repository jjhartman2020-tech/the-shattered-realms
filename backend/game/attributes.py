"""Canonical Shattered Realms 0-30 attribute framework.

Sources of truth:
- docs/Stats.md
- docs/progression/Leveling.md

The AI may choose context, but the engine owns mechanical values.
"""

from copy import deepcopy
from math import floor
from typing import Dict

ATTRIBUTE_NAMES = (
    "health", "mana", "strength", "dexterity", "constitution",
    "intelligence", "wisdom", "charisma", "speed",
)

STARTING_ATTRIBUTE_POINTS = 60
ATTRIBUTE_POINTS_PER_LEVEL = 3
ABILITY_POINTS_PER_LEVEL = 1
MAX_HEALTH_GAIN_PER_LEVEL = 5
NATURAL_ATTRIBUTE_CAP = 30
MAX_LEVEL = 71
BASE_ARMOR_CLASS = 10
BASE_MOVEMENT = 6
BASE_CRITICAL_CHANCE = 5  # percentage points

DEFAULT_ATTRIBUTES = {name: 0 for name in ATTRIBUTE_NAMES}

SKILL_ATTRIBUTE = {
    "acrobatics": "dexterity", "animal_handling": "wisdom",
    "arcana": "intelligence", "athletics": "strength",
    "deception": "charisma", "history": "intelligence",
    "insight": "wisdom", "intimidation": "charisma",
    "investigation": "intelligence", "medicine": "wisdom",
    "nature": "intelligence", "perception": "wisdom",
    "performance": "charisma", "persuasion": "charisma",
    "religion": "intelligence", "sleight_of_hand": "dexterity",
    "stealth": "dexterity", "survival": "wisdom",
}


def normalize_attributes(attributes: Dict | None = None) -> Dict[str, int]:
    result = deepcopy(DEFAULT_ATTRIBUTES)
    if not isinstance(attributes, dict):
        return result
    aliases = {"agility": "dexterity", "durability": "constitution"}
    for raw_name, raw_value in attributes.items():
        name = aliases.get(raw_name, raw_name)
        if name in result:
            result[name] = max(0, min(NATURAL_ATTRIBUTE_CAP, int(raw_value)))
    return result


def earned_attribute_points(level: int) -> int:
    level = max(1, min(MAX_LEVEL, int(level)))
    return STARTING_ATTRIBUTE_POINTS + (level - 1) * ATTRIBUTE_POINTS_PER_LEVEL


def earned_ability_points(level: int) -> int:
    level = max(1, min(MAX_LEVEL, int(level)))
    return (level - 1) * ABILITY_POINTS_PER_LEVEL


def level_health_bonus(level: int) -> int:
    level = max(1, min(MAX_LEVEL, int(level)))
    return (level - 1) * MAX_HEALTH_GAIN_PER_LEVEL


def points_spent(attributes: Dict | None = None) -> int:
    return sum(normalize_attributes(attributes).values())


def validate_allocation(attributes: Dict | None = None, level: int = 1) -> Dict:
    normalized = normalize_attributes(attributes)
    available = earned_attribute_points(level)
    spent = sum(normalized.values())
    return {
        "valid": spent <= available,
        "attributes": normalized,
        "points_spent": spent,
        "points_available": available,
        "points_unspent": available - spent,
        "natural_cap": NATURAL_ATTRIBUTE_CAP,
    }


def attribute_check_bonus(score: int) -> int:
    """Every complete 3 attribute points grant +1. No decimals."""
    return max(0, int(score)) // 3


def attack_accuracy_bonus(score: int) -> int:
    return attribute_check_bonus(score)


def strength_damage_bonus(strength: int) -> int:
    return max(0, int(strength)) // 6


def critical_chance(dexterity: int) -> int:
    """Return whole percentage points."""
    return BASE_CRITICAL_CHANCE + attribute_check_bonus(dexterity)


def physical_resistance(constitution: int) -> int:
    """Return whole percentage points."""
    return attribute_check_bonus(constitution)


def status_resistance(constitution: int) -> int:
    """Return whole percentage points."""
    return attribute_check_bonus(constitution) * 2


def defense_bonus(dexterity: int, constitution: int, speed: int) -> int:
    return max(0, int(dexterity)) // 9 + max(0, int(constitution)) // 15 + max(0, int(speed)) // 15


def initiative_bonus(speed: int, dexterity: int) -> int:
    return max(0, int(speed)) // 3 + max(0, int(dexterity)) // 6


def movement_spaces(speed: int) -> int:
    return BASE_MOVEMENT + max(0, int(speed)) // 6


def trading_influence(charisma: int) -> int:
    """Return whole percentage points."""
    return attribute_check_bonus(charisma)


def character_sheet_channels(attributes: Dict | None = None, level: int = 1) -> Dict:
    a = normalize_attributes(attributes)
    level = max(1, min(MAX_LEVEL, int(level)))
    return {
        "attributes": a,
        "level_health_bonus": level_health_bonus(level),
        "max_health_base": max(1, a["health"] + level_health_bonus(level)),
        "max_mana_base": a["mana"],
        "strength_rating": a["strength"],
        "dexterity_rating": a["dexterity"],
        "constitution_rating": a["constitution"],
        "intelligence_rating": a["intelligence"],
        "wisdom_rating": a["wisdom"],
        "charisma_rating": a["charisma"],
        "speed_rating": a["speed"],
        "strength_check_bonus": attribute_check_bonus(a["strength"]),
        "dexterity_check_bonus": attribute_check_bonus(a["dexterity"]),
        "constitution_check_bonus": attribute_check_bonus(a["constitution"]),
        "intelligence_check_bonus": attribute_check_bonus(a["intelligence"]),
        "wisdom_check_bonus": attribute_check_bonus(a["wisdom"]),
        "charisma_check_bonus": attribute_check_bonus(a["charisma"]),
        "speed_check_bonus": attribute_check_bonus(a["speed"]),
        "strength_attack_accuracy": attack_accuracy_bonus(a["strength"]),
        "dexterity_attack_accuracy": attack_accuracy_bonus(a["dexterity"]),
        "strength_damage_bonus": strength_damage_bonus(a["strength"]),
        "critical_chance_percent": critical_chance(a["dexterity"]),
        "physical_resistance_percent": physical_resistance(a["constitution"]),
        "status_resistance_percent": status_resistance(a["constitution"]),
        "defense_bonus": defense_bonus(a["dexterity"], a["constitution"], a["speed"]),
        "initiative_bonus": initiative_bonus(a["speed"], a["dexterity"]),
        "movement": movement_spaces(a["speed"]),
        "trading_influence_percent": trading_influence(a["charisma"]),
    }


def build_combatant(name: str, team: str, attributes: Dict | None = None, *,
                    level: int = 1, hp: int | None = None,
                    overrides: Dict | None = None) -> Dict:
    a = normalize_attributes(attributes)
    level = max(1, min(MAX_LEVEL, int(level)))
    sheet = character_sheet_channels(a, level)
    actor = {
        "name": name,
        "team": team,
        "level": level,
        "attributes": a,
        "attribute_channels": sheet,
        "hp": sheet["max_health_base"] if hp is None else int(hp),
        "max_hp": sheet["max_health_base"],
        "mana": sheet["max_mana_base"],
        "max_mana": sheet["max_mana_base"],
        "attack_bonus": 0,
        "damage_bonus": sheet["strength_damage_bonus"],
        "armor_class": BASE_ARMOR_CLASS + sheet["defense_bonus"],
        "initiative_bonus": sheet["initiative_bonus"],
        "movement": sheet["movement"],
        "critical_chance_percent": sheet["critical_chance_percent"],
        "physical_resistance_percent": sheet["physical_resistance_percent"],
        "status_resistance_percent": sheet["status_resistance_percent"],
    }
    if isinstance(overrides, dict):
        actor.update(overrides)
    return actor
