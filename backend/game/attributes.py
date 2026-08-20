"""Canonical Shattered Realms 0-60 attribute framework.

Sources of truth:
- docs/Stats.md
- docs/progression/Leveling.md

This module owns conversion from raw attributes into deterministic mechanical
channels. The AI may choose context, but it may not invent these values.
"""

from copy import deepcopy
from math import floor
from typing import Dict

ATTRIBUTE_NAMES = (
    "health", "mana", "strength", "dexterity", "constitution",
    "intelligence", "wisdom", "charisma", "speed",
)

STARTING_ATTRIBUTE_POINTS = 60
ATTRIBUTE_POINTS_PER_LEVEL = 5
ABILITY_POINTS_PER_LEVEL = 1
MAX_HEALTH_GAIN_PER_LEVEL = 5
NATURAL_ATTRIBUTE_CAP = 60
MAX_LEVEL = 97
BASE_ARMOR_CLASS = 10
BASE_MOVEMENT = 6
BASE_CRITICAL_CHANCE = 0.05

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
    return {"valid": spent <= available, "attributes": normalized,
            "points_spent": spent, "points_available": available,
            "points_unspent": available - spent, "natural_cap": NATURAL_ATTRIBUTE_CAP}


def attribute_check_bonus(score: int) -> float:
    return max(0, int(score)) / 6.0


def attack_accuracy_bonus(score: int) -> float:
    return max(0, int(score)) / 12.0


def physical_damage_multiplier(strength: int) -> float:
    return 1.0 + max(0, int(strength)) / 100.0


def magic_power_multiplier(intelligence: int) -> float:
    return 1.0 + max(0, int(intelligence)) / 100.0


def healing_multiplier(wisdom: int) -> float:
    return 1.0 + max(0, int(wisdom)) / 100.0


def critical_chance(dexterity: int) -> float:
    return BASE_CRITICAL_CHANCE + max(0, int(dexterity)) * 0.001


def physical_resistance(constitution: int) -> float:
    return min(1.0, max(0, int(constitution)) * 0.0025)


def status_resistance(constitution: int) -> float:
    return min(1.0, max(0, int(constitution)) * 0.005)


def defense_bonus(dexterity: int, constitution: int, speed: int) -> float:
    return max(0, int(dexterity)) / 15.0 + max(0, int(constitution)) / 20.0 + max(0, int(speed)) / 30.0


def initiative_bonus(speed: int, dexterity: int) -> float:
    return max(0, int(speed)) / 6.0 + max(0, int(dexterity)) / 12.0


def movement_spaces(speed: int) -> int:
    return BASE_MOVEMENT + floor(max(0, int(speed)) / 10)


def character_sheet_channels(attributes: Dict | None = None, level: int = 1) -> Dict:
    a = normalize_attributes(attributes)
    level = max(1, min(MAX_LEVEL, int(level)))
    return {
        "attributes": a,
        "level_health_bonus": level_health_bonus(level),
        "max_health_base": max(1, a["health"] + level_health_bonus(level)),
        "max_mana_base": a["mana"],
        "strength_rating": a["strength"], "dexterity_rating": a["dexterity"],
        "constitution_rating": a["constitution"], "intelligence_rating": a["intelligence"],
        "wisdom_rating": a["wisdom"], "charisma_rating": a["charisma"],
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
        "physical_damage_multiplier": physical_damage_multiplier(a["strength"]),
        "magic_power_multiplier": magic_power_multiplier(a["intelligence"]),
        "healing_multiplier": healing_multiplier(a["wisdom"]),
        "critical_chance": critical_chance(a["dexterity"]),
        "physical_resistance": physical_resistance(a["constitution"]),
        "status_resistance": status_resistance(a["constitution"]),
        "defense_bonus": defense_bonus(a["dexterity"], a["constitution"], a["speed"]),
        "initiative_bonus": initiative_bonus(a["speed"], a["dexterity"]),
        "movement": movement_spaces(a["speed"]),
        "trading_influence": a["charisma"] * 0.0025,
    }


def build_combatant(name: str, team: str, attributes: Dict | None = None, *,
                    level: int = 1, hp: int | None = None,
                    overrides: Dict | None = None) -> Dict:
    a = normalize_attributes(attributes)
    level = max(1, min(MAX_LEVEL, int(level)))
    sheet = character_sheet_channels(a, level)
    actor = {
        "name": name, "team": team, "level": level, "attributes": a,
        "attribute_channels": sheet,
        "hp": sheet["max_health_base"] if hp is None else int(hp),
        "max_hp": sheet["max_health_base"],
        "mana": sheet["max_mana_base"], "max_mana": sheet["max_mana_base"],
        "attack_bonus": 0, "damage_bonus": 0,
        "armor_class": BASE_ARMOR_CLASS + sheet["defense_bonus"],
        "initiative_bonus": sheet["initiative_bonus"],
        "movement": sheet["movement"],
        "critical_chance": sheet["critical_chance"],
        "physical_resistance": sheet["physical_resistance"],
        "status_resistance": sheet["status_resistance"],
    }
    if isinstance(overrides, dict):
        actor.update(overrides)
    return actor
