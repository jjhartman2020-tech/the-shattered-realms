"""Core attributes and derived combat statistics for The Shattered Realms.

Raw attributes are the permanent character numbers. Derived values are calculated
by the engine so AI narration cannot invent mechanical bonuses.
"""

from copy import deepcopy
from typing import Dict

CORE_ATTRIBUTES = (
    "strength",       # melee power, lifting, physical force
    "agility",        # accuracy, dodge, finesse, stealth
    "speed",          # initiative and grid movement
    "durability",     # health and physical toughness
    "intelligence",   # knowledge, investigation, technical/arcane reasoning
    "wisdom",         # perception, survival, awareness and mental resistance
    "charisma",       # persuasion, deception, intimidation and presence
)

DEFAULT_ATTRIBUTES = {name: 10 for name in CORE_ATTRIBUTES}


def modifier(score: int) -> int:
    """Convert an attribute score to a familiar tabletop modifier."""
    return (int(score) - 10) // 2


def normalize_attributes(attributes: Dict | None = None) -> Dict[str, int]:
    result = deepcopy(DEFAULT_ATTRIBUTES)
    if isinstance(attributes, dict):
        # Backward compatibility with early saves that used DEX/CON terminology.
        aliases = {"dexterity": "agility", "constitution": "durability"}
        for raw_name, value in attributes.items():
            name = aliases.get(raw_name, raw_name)
            if name in result:
                result[name] = max(1, int(value))
    return result


def derived_stats(attributes: Dict | None = None, level: int = 1) -> Dict[str, int]:
    """Calculate baseline combat values from attributes.

    Equipment, classes, abilities, conditions, and temporary effects can modify
    these values later without changing the underlying attributes.
    """
    a = normalize_attributes(attributes)
    level = max(1, int(level))

    strength = modifier(a["strength"])
    agility = modifier(a["agility"])
    speed = modifier(a["speed"])
    durability = modifier(a["durability"])
    intelligence = modifier(a["intelligence"])
    wisdom = modifier(a["wisdom"])
    charisma = modifier(a["charisma"])

    return {
        "max_hp": max(1, 10 + (level - 1) * 4 + durability * 2),
        "max_mana": max(0, intelligence + wisdom + (level - 1) * 2),
        "armor_class": max(1, 10 + agility + durability // 2),
        "initiative_bonus": agility + speed,
        "movement": max(1, 6 + speed),
        "melee_attack_bonus": strength + max(0, (level - 1) // 4),
        "finesse_attack_bonus": agility + max(0, (level - 1) // 4),
        "ranged_attack_bonus": agility + max(0, (level - 1) // 4),
        "melee_damage_bonus": strength,
        "finesse_damage_bonus": agility,
        "physical_resistance": durability,
        "mental_resistance": wisdom,
        "magic_power": intelligence,
        "perception_bonus": wisdom,
        "social_bonus": charisma,
    }


def build_combatant(name: str, team: str, attributes: Dict | None = None, *, level: int = 1,
                    hp: int | None = None, damage: str = "1d6", attack_type: str = "melee",
                    overrides: Dict | None = None) -> Dict:
    """Build a combat-engine actor from permanent character attributes."""
    a = normalize_attributes(attributes)
    d = derived_stats(a, level)
    attack_key = {
        "melee": "melee_attack_bonus",
        "finesse": "finesse_attack_bonus",
        "ranged": "ranged_attack_bonus",
    }.get(attack_type, "melee_attack_bonus")
    damage_key = "finesse_damage_bonus" if attack_type == "finesse" else (
        "melee_damage_bonus" if attack_type == "melee" else None
    )

    actor = {
        "name": name,
        "team": team,
        "level": int(level),
        "attributes": a,
        "derived": d,
        "hp": d["max_hp"] if hp is None else int(hp),
        "max_hp": d["max_hp"],
        "armor_class": d["armor_class"],
        "dexterity": a["agility"],  # compatibility with existing combat engine
        "initiative_bonus": d["initiative_bonus"],
        "movement": d["movement"],
        "attack_bonus": d[attack_key],
        "damage_bonus": d[damage_key] if damage_key else 0,
        "damage": damage,
        "attack_type": attack_type,
    }
    if isinstance(overrides, dict):
        actor.update(overrides)
    return actor
