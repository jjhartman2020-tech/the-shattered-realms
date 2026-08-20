"""Character-sheet statistics for The Shattered Realms.

The engine owns mechanical truth. AI narration can describe outcomes, but these
functions calculate attributes, modifiers, skills, saves and derived values.
"""
from copy import deepcopy
from typing import Dict

# Shattered Realms keeps the six classic tabletop abilities and adds Speed as a
# separate tactical attribute because grid movement is a core game mechanic.
CORE_ATTRIBUTES = (
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma", "speed"
)
DEFAULT_ATTRIBUTES = {name: 10 for name in CORE_ATTRIBUTES}

SKILL_ABILITY = {
    "acrobatics": "dexterity",
    "animal_handling": "wisdom",
    "arcana": "intelligence",
    "athletics": "strength",
    "deception": "charisma",
    "history": "intelligence",
    "insight": "wisdom",
    "intimidation": "charisma",
    "investigation": "intelligence",
    "medicine": "wisdom",
    "nature": "intelligence",
    "perception": "wisdom",
    "performance": "charisma",
    "persuasion": "charisma",
    "religion": "intelligence",
    "sleight_of_hand": "dexterity",
    "stealth": "dexterity",
    "survival": "wisdom",
}


def modifier(score: int) -> int:
    return (int(score) - 10) // 2


def proficiency_bonus(level: int) -> int:
    level = max(1, int(level))
    return 2 + (level - 1) // 4


def normalize_attributes(attributes: Dict | None = None) -> Dict[str, int]:
    result = deepcopy(DEFAULT_ATTRIBUTES)
    if isinstance(attributes, dict):
        aliases = {"agility": "dexterity", "durability": "constitution"}
        for raw_name, value in attributes.items():
            name = aliases.get(raw_name, raw_name)
            if name in result:
                result[name] = max(1, int(value))
    return result


def ability_modifiers(attributes: Dict | None = None) -> Dict[str, int]:
    a = normalize_attributes(attributes)
    return {name: modifier(score) for name, score in a.items()}


def saving_throws(attributes: Dict | None = None, level: int = 1,
                  proficient: list[str] | None = None) -> Dict[str, int]:
    mods = ability_modifiers(attributes)
    prof = proficiency_bonus(level)
    proficient = set(proficient or [])
    return {name: mods[name] + (prof if name in proficient else 0)
            for name in CORE_ATTRIBUTES if name != "speed"}


def skill_bonuses(attributes: Dict | None = None, level: int = 1,
                  proficient: list[str] | None = None,
                  expertise: list[str] | None = None) -> Dict[str, int]:
    mods = ability_modifiers(attributes)
    prof = proficiency_bonus(level)
    proficient, expertise = set(proficient or []), set(expertise or [])
    result = {}
    for skill, ability in SKILL_ABILITY.items():
        bonus = mods[ability]
        if skill in expertise:
            bonus += prof * 2
        elif skill in proficient:
            bonus += prof
        result[skill] = bonus
    return result


def derived_stats(attributes: Dict | None = None, level: int = 1,
                  skill_proficiencies: list[str] | None = None,
                  expertise: list[str] | None = None,
                  save_proficiencies: list[str] | None = None) -> Dict:
    a = normalize_attributes(attributes)
    m = ability_modifiers(a)
    level = max(1, int(level))
    prof = proficiency_bonus(level)
    skills = skill_bonuses(a, level, skill_proficiencies, expertise)
    saves = saving_throws(a, level, save_proficiencies)
    max_hp = max(1, 10 + (level - 1) * 4 + m["constitution"] * 2)

    return {
        "proficiency_bonus": prof,
        "ability_modifiers": m,
        "saving_throws": saves,
        "skills": skills,
        "armor_class": max(1, 10 + m["dexterity"]),
        "initiative_bonus": m["dexterity"] + m["speed"],
        "movement": max(1, 6 + m["speed"]),
        "max_hp": max_hp,
        "hit_dice": f"{level}d8",
        "max_mana": max(0, m["intelligence"] + m["wisdom"] + (level - 1) * 2),
        "passive_perception": 10 + skills["perception"],
        "passive_insight": 10 + skills["insight"],
        "passive_investigation": 10 + skills["investigation"],
        "melee_attack_bonus": m["strength"] + prof,
        "finesse_attack_bonus": m["dexterity"] + prof,
        "ranged_attack_bonus": m["dexterity"] + prof,
        "melee_damage_bonus": m["strength"],
        "finesse_damage_bonus": m["dexterity"],
        "physical_resistance": m["constitution"],
        "mental_resistance": m["wisdom"],
        "magic_power": m["intelligence"],
        "spell_attack_bonus": prof + max(m["intelligence"], m["wisdom"], m["charisma"]),
        "spell_save_dc": 8 + prof + max(m["intelligence"], m["wisdom"], m["charisma"]),
    }


def build_combatant(name: str, team: str, attributes: Dict | None = None, *, level: int = 1,
                    hp: int | None = None, damage: str = "1d6", attack_type: str = "melee",
                    overrides: Dict | None = None) -> Dict:
    a = normalize_attributes(attributes)
    d = derived_stats(a, level)
    attack_key = {"melee": "melee_attack_bonus", "finesse": "finesse_attack_bonus",
                  "ranged": "ranged_attack_bonus"}.get(attack_type, "melee_attack_bonus")
    damage_key = "finesse_damage_bonus" if attack_type == "finesse" else (
        "melee_damage_bonus" if attack_type == "melee" else None)
    actor = {
        "name": name, "team": team, "level": int(level), "attributes": a, "derived": d,
        "hp": d["max_hp"] if hp is None else int(hp), "max_hp": d["max_hp"],
        "armor_class": d["armor_class"], "dexterity": a["dexterity"],
        "initiative_bonus": d["initiative_bonus"], "movement": d["movement"],
        "attack_bonus": d[attack_key], "damage_bonus": d[damage_key] if damage_key else 0,
        "damage": damage, "attack_type": attack_type,
    }
    if isinstance(overrides, dict):
        actor.update(overrides)
    return actor
