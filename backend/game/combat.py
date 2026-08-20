"""Authoritative combat engine for The Shattered Realms."""

from copy import deepcopy
from typing import Dict, List

from .dice import roll
from .attributes import character_sheet_channels, normalize_attributes


def roll_initiative(name: str, attributes: Dict | None = None, bonus: int = 0) -> Dict:
    base = roll("1d20")
    channels = character_sheet_channels(attributes)
    modifier = int(channels["initiative_bonus"]) + int(bonus)
    return {"name": name, "roll": int(base["total"]), "modifier": modifier,
            "total": int(base["total"]) + modifier}


def start_combat(combatants: List[Dict]) -> Dict:
    if not combatants:
        raise ValueError("Combat requires at least one combatant")
    prepared, initiative = [], []
    for raw in combatants:
        actor = deepcopy(raw)
        actor.setdefault("name", "Unknown combatant")
        actor.setdefault("team", "enemy")
        attrs = normalize_attributes(actor.get("attributes"))
        channels = character_sheet_channels(attrs, actor.get("level", 1))
        actor["attributes"] = attrs
        actor.setdefault("hp", channels["max_health_base"])
        actor.setdefault("max_hp", actor["hp"])
        actor.setdefault("armor_class", 10 + channels["defense_bonus"])
        actor.setdefault("attack_bonus", 0)
        actor.setdefault("damage_bonus", channels["strength_damage_bonus"])
        actor.setdefault("damage", "1d4")
        actor.setdefault("movement", channels["movement"])
        actor.setdefault("critical_chance_percent", channels["critical_chance_percent"])
        actor.setdefault("physical_resistance_percent", channels["physical_resistance_percent"])
        actor["defeated"] = int(actor["hp"]) <= 0
        prepared.append(actor)
        initiative.append(roll_initiative(actor["name"], attrs, actor.get("initiative_bonus", 0)))
    initiative.sort(key=lambda item: (item["total"], item["modifier"]), reverse=True)
    return {"active": True, "round": 1, "turn_index": 0,
            "order": [i["name"] for i in initiative], "initiative": initiative,
            "combatants": prepared, "log": ["Combat begins."]}


def _find_actor(combat: Dict, name: str) -> Dict:
    for actor in combat.get("combatants", []):
        if actor.get("name") == name:
            return actor
    raise ValueError(f"Unknown combatant: {name}")


def current_actor(combat: Dict) -> Dict | None:
    if not combat.get("active") or not combat.get("order"):
        return None
    return _find_actor(combat, combat["order"][combat["turn_index"]])


def resolve_attack(combat: Dict, attacker_name: str, target_name: str, *,
                   attack_bonus: int | None = None, damage_expression: str | None = None,
                   damage_bonus: int | None = None, attack_attribute: str = "strength",
                   enforce_turn: bool = False) -> Dict:
    attacker, target = _find_actor(combat, attacker_name), _find_actor(combat, target_name)
    if attacker.get("defeated"):
        raise ValueError(f"{attacker_name} is defeated and cannot attack")
    if target.get("defeated"):
        raise ValueError(f"{target_name} is already defeated")
    if enforce_turn:
        active = current_actor(combat)
        if not active or active.get("name") != attacker_name:
            raise ValueError(f"It is not {attacker_name}'s turn")

    attrs = normalize_attributes(attacker.get("attributes"))
    channels = character_sheet_channels(attrs, attacker.get("level", 1))
    stat_accuracy = channels["dexterity_attack_accuracy"] if attack_attribute == "dexterity" else channels["strength_attack_accuracy"]
    bonus = int(attacker.get("attack_bonus", 0) if attack_bonus is None else attack_bonus) + int(stat_accuracy)

    attack = roll("1d20")
    natural = int(attack["rolls"][0])
    total = int(attack["total"]) + bonus
    armor_class = int(target.get("armor_class", 10))
    automatic_miss = natural == 1
    crit_chance = int(attacker.get("critical_chance_percent", channels["critical_chance_percent"]))
    critical = natural == 20
    hit = False if automatic_miss else (True if critical else total >= armor_class)
    damage, damage_rolls = 0, []

    default_damage_bonus = channels["strength_damage_bonus"] if attack_attribute == "strength" else 0
    applied_damage_bonus = int(attacker.get("damage_bonus", default_damage_bonus) if damage_bonus is None else damage_bonus)
    if hit:
        expression = damage_expression or str(attacker.get("damage", "1d4"))
        first = roll(expression)
        damage_rolls.append(first)
        raw_damage = int(first["total"]) + applied_damage_bonus
        if critical:
            second = roll(expression)
            damage_rolls.append(second)
            raw_damage += int(second["total"])
        resistance_percent = int(target.get("physical_resistance_percent", 0)) if attack_attribute in {"strength", "dexterity"} else 0
        damage = max(0, round(raw_damage * (100 - resistance_percent) / 100))
        target["hp"] = max(0, int(target.get("hp", 0)) - damage)
        target["defeated"] = target["hp"] <= 0

    outcome = {"attacker": attacker_name, "target": target_name, "d20": natural,
               "attack_attribute": attack_attribute, "attack_bonus": bonus,
               "attack_total": total, "armor_class": armor_class,
               "hit": hit, "critical": critical, "critical_chance_percent": crit_chance,
               "damage": damage, "damage_bonus": applied_damage_bonus,
               "damage_rolls": damage_rolls, "target_hp": int(target.get("hp", 0)),
               "target_max_hp": int(target.get("max_hp", target.get("hp", 0))),
               "target_defeated": bool(target.get("defeated"))}
    combat.setdefault("log", []).append(outcome)
    _check_combat_end(combat)
    return outcome


def end_turn(combat: Dict) -> Dict:
    if not combat.get("active"):
        return combat
    order = combat.get("order", [])
    if not order:
        combat["active"] = False
        return combat
    starting_index = int(combat.get("turn_index", 0))
    index = starting_index
    while True:
        index = (index + 1) % len(order)
        if index == 0:
            combat["round"] = int(combat.get("round", 1)) + 1
        actor = _find_actor(combat, order[index])
        if not actor.get("defeated"):
            combat["turn_index"] = index
            break
        if index == starting_index:
            combat["active"] = False
            break
    _check_combat_end(combat)
    return combat


def _check_combat_end(combat: Dict) -> None:
    living_teams = {a.get("team") for a in combat.get("combatants", []) if not a.get("defeated")}
    if len(living_teams) <= 1:
        combat["active"] = False
        combat["winner"] = next(iter(living_teams), None)
