"""Canonical Shattered Realms core attribute framework.

Sources of truth:
- docs/Stats.md
- docs/Skills.md
- docs/progression/Leveling.md for progression rules not yet redesigned

The AI may choose context, but the engine owns mechanical values.
"""

from copy import deepcopy
from typing import Dict

from .resources import max_resource_from_attribute, resource_regeneration_per_round

ATTRIBUTE_NAMES = (
    "health", "resource", "strength", "dexterity", "agility",
    "constitution", "intelligence", "wisdom", "charisma", "speed",
    "defense", "luck", "magic",
)

STARTING_ATTRIBUTE_POINTS = 42
ATTRIBUTE_POINTS_PER_LEVEL = 3
ABILITY_POINTS_PER_LEVEL = 1
# Leveling.md still defines this until the leveling redesign is finalized.
MAX_HEALTH_GAIN_PER_LEVEL = 5
NATURAL_ATTRIBUTE_CAP = 100
# Leveling.md still defines the current level cap. Do not derive it from stat caps.
MAX_LEVEL = 71
BASE_ARMOR_CLASS = 10
BASE_MOVEMENT = 6
BASE_CRITICAL_CHANCE = 5  # percentage points

DEFAULT_ATTRIBUTES = {name: 0 for name in ATTRIBUTE_NAMES}

SKILL_ATTRIBUTE = {
    "athletics": "strength",
    "grappling": "strength",
    "might": "strength",
    "sleight_of_hand": "dexterity",
    "lockpicking": "dexterity",
    "pickpocketing": "dexterity",
    "precision": "dexterity",
    "acrobatics": "agility",
    "stealth": "agility",
    "evasion": "agility",
    "endurance": "constitution",
    "fortitude": "constitution",
    "investigation": "intelligence",
    "arcana": "intelligence",
    "history": "intelligence",
    "nature": "intelligence",
    "engineering": "intelligence",
    "perception": "wisdom",
    "insight": "wisdom",
    "survival": "wisdom",
    "medicine": "wisdom",
    "animal_handling": "wisdom",
    "persuasion": "charisma",
    "deception": "charisma",
    "intimidation": "charisma",
    "performance": "charisma",
    "leadership": "charisma",
    "spellcasting": "magic",
    "channeling": "magic",
}


def _clamp_attribute(value: int) -> int:
    return max(0, min(NATURAL_ATTRIBUTE_CAP, int(value)))


def normalize_attributes(attributes: Dict | None = None) -> Dict[str, int]:
    """Return a complete 13-stat mapping and migrate common legacy names.

    Old saves used ``mana`` for the universal capacity stat and had no separate
    Agility, Luck, or Magic attributes. Missing new attributes safely begin at 0.
    An explicit new ``resource`` value always wins over a legacy ``mana`` value.
    """
    result = deepcopy(DEFAULT_ATTRIBUTES)
    if not isinstance(attributes, dict):
        return result

    aliases = {
        "mana": "resource",
        "durability": "constitution",
        "defence": "defense",
    }

    # Legacy aliases first, then canonical names so explicit new fields win.
    for raw_name, raw_value in attributes.items():
        name = aliases.get(str(raw_name).strip().lower())
        if name in result:
            result[name] = _clamp_attribute(raw_value)
    for raw_name, raw_value in attributes.items():
        name = str(raw_name).strip().lower()
        if name in result:
            result[name] = _clamp_attribute(raw_value)
    return result


def earned_attribute_points(level: int) -> int:
    level = max(1, min(MAX_LEVEL, int(level)))
    return STARTING_ATTRIBUTE_POINTS + (level - 1) * ATTRIBUTE_POINTS_PER_LEVEL


def earned_ability_points(level: int) -> int:
    level = max(1, min(MAX_LEVEL, int(level)))
    return (level - 1) * ABILITY_POINTS_PER_LEVEL


def level_health_bonus(level: int) -> int:
    """Current progression bonus retained until Leveling.md is redesigned."""
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
    """Standard 0-100 modifier: 3:1 through 30, then 10:1."""
    score = _clamp_attribute(score)
    if score <= 30:
        return score // 3
    return 10 + (score - 30) // 10


def attack_accuracy_bonus(score: int) -> int:
    return attribute_check_bonus(score)


def strength_damage_bonus(strength: int) -> int:
    """Temporary legacy damage curve until damage scaling is formally redesigned."""
    return _clamp_attribute(strength) // 6


def critical_chance(luck: int) -> int:
    """Return whole percentage points. Luck, not Dexterity, controls crit chance."""
    return BASE_CRITICAL_CHANCE + attribute_check_bonus(luck)


def physical_resistance(constitution: int) -> int:
    """Return whole percentage points: +1% per full 5 Constitution."""
    return _clamp_attribute(constitution) // 5


def status_resistance(constitution: int) -> int:
    """Return whole percentage points: +1% per full 4 Constitution."""
    return _clamp_attribute(constitution) // 4


def defense_bonus(agility: int, constitution: int, speed: int) -> int:
    """Temporary passive-AC compatibility curve pending the final AC redesign.

    Agility takes the evasive role formerly overloaded onto Dexterity. The exact
    passive Armor Class formula is still marked unfinished in Stats.md.
    """
    return _clamp_attribute(agility) // 9 + _clamp_attribute(constitution) // 15 + _clamp_attribute(speed) // 15


def defend_action_ac_bonus(defense: int) -> int:
    return attribute_check_bonus(defense)


def initiative_bonus(speed: int, dexterity: int | None = None) -> int:
    """Speed alone drives initiative. Dexterity arg is accepted for old callers."""
    return attribute_check_bonus(speed)


def movement_spaces(speed: int) -> int:
    """Base 6; +0.5 square/Speed through 30, then +0.1/Speed, floored."""
    speed = _clamp_attribute(speed)
    early = min(speed, 30)
    late = max(0, speed - 30)
    # Work in tenths to avoid float rounding: base 6=60, 0.5=5, 0.1=1.
    return (BASE_MOVEMENT * 10 + early * 5 + late) // 10


def trading_influence(charisma: int) -> int:
    """Legacy helper retained for callers; social rules may redefine trading later."""
    return attribute_check_bonus(charisma)


def character_sheet_channels(attributes: Dict | None = None, level: int = 1) -> Dict:
    a = normalize_attributes(attributes)
    level = max(1, min(MAX_LEVEL, int(level)))
    max_resource = max_resource_from_attribute(a["resource"])
    resource_regen = resource_regeneration_per_round(a["resource"])
    max_health = max(1, a["health"] * 5 + level_health_bonus(level))
    return {
        "attributes": a,
        "level_health_bonus": level_health_bonus(level),
        "max_health_base": max_health,
        "max_resource_base": max_resource,
        "resource_regeneration_per_round": resource_regen,
        # Backward-compatible aliases for older save/runtime code.
        "max_mana_base": max_resource,
        "health_rating": a["health"],
        "resource_rating": a["resource"],
        "strength_rating": a["strength"],
        "dexterity_rating": a["dexterity"],
        "agility_rating": a["agility"],
        "constitution_rating": a["constitution"],
        "intelligence_rating": a["intelligence"],
        "wisdom_rating": a["wisdom"],
        "charisma_rating": a["charisma"],
        "speed_rating": a["speed"],
        "defense_rating": a["defense"],
        "luck_rating": a["luck"],
        "magic_rating": a["magic"],
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
        "resource": sheet["max_resource_base"],
        "max_resource": sheet["max_resource_base"],
        "resource_regeneration_per_round": sheet["resource_regeneration_per_round"],
        # Backward-compatible aliases used by older save/runtime code.
        "mana": sheet["max_resource_base"],
        "max_mana": sheet["max_resource_base"],
        "attack_bonus": 0,
        "damage_bonus": sheet["strength_damage_bonus"],
        "armor_class": BASE_ARMOR_CLASS + sheet["defense_bonus"],
        "initiative_bonus": sheet["initiative_bonus"],
        "movement": sheet["movement"],
        "defend_action_ac_bonus": sheet["defend_action_ac_bonus"],
        "critical_chance_percent": sheet["critical_chance_percent"],
        "physical_resistance_percent": sheet["physical_resistance_percent"],
        "status_resistance_percent": sheet["status_resistance_percent"],
    }
    if isinstance(overrides, dict):
        actor.update(overrides)
    # Keep legacy mana aliases synchronized with the universal resource pool.
    if "resource" in actor:
        actor["mana"] = int(actor.get("resource", 0) or 0)
    if "max_resource" in actor:
        actor["max_mana"] = int(actor.get("max_resource", 0) or 0)
    return actor
