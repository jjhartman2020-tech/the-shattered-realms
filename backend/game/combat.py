"""Deterministic combat foundation for The Shattered Realms.

The AI describes combat and chooses NPC intentions. This module owns initiative,
attack rolls, damage, HP, defeat, and turn order so the model cannot invent
mechanical outcomes.
"""

from copy import deepcopy
from typing import Dict, List

from .dice import roll


def ability_modifier(score: int) -> int:
    """Convert a D&D-style ability score into its modifier."""
    return (int(score) - 10) // 2


def roll_initiative(name: str, dexterity: int = 10, bonus: int = 0) -> Dict:
    base = roll("1d20")
    modifier = ability_modifier(dexterity) + int(bonus)
    return {
        "name": name,
        "roll": int(base["total"]),
        "modifier": modifier,
        "total": int(base["total"]) + modifier,
    }


def start_combat(combatants: List[Dict]) -> Dict:
    """Create initiative order from combatant dictionaries."""
    if not combatants:
        raise ValueError("Combat requires at least one combatant")

    prepared = []
    initiative = []
    for raw in combatants:
        actor = deepcopy(raw)
        actor.setdefault("name", "Unknown combatant")
        actor.setdefault("team", "enemy")
        actor.setdefault("hp", 10)
        actor.setdefault("max_hp", actor["hp"])
        actor.setdefault("armor_class", 10)
        actor.setdefault("dexterity", 10)
        actor.setdefault("attack_bonus", 0)
        actor.setdefault("damage", "1d4")
        actor["defeated"] = int(actor["hp"]) <= 0
        prepared.append(actor)
        initiative.append(
            roll_initiative(
                actor["name"],
                actor.get("dexterity", 10),
                actor.get("initiative_bonus", 0),
            )
        )

    initiative.sort(key=lambda item: (item["total"], item["modifier"]), reverse=True)
    order = [item["name"] for item in initiative]
    return {
        "active": True,
        "round": 1,
        "turn_index": 0,
        "order": order,
        "initiative": initiative,
        "combatants": prepared,
        "log": ["Combat begins."],
    }


def _find_actor(combat: Dict, name: str) -> Dict:
    for actor in combat.get("combatants", []):
        if actor.get("name") == name:
            return actor
    raise ValueError(f"Unknown combatant: {name}")


def current_actor(combat: Dict) -> Dict | None:
    if not combat.get("active") or not combat.get("order"):
        return None
    name = combat["order"][combat["turn_index"]]
    return _find_actor(combat, name)


def resolve_attack(
    combat: Dict,
    attacker_name: str,
    target_name: str,
    *,
    attack_bonus: int | None = None,
    damage_expression: str | None = None,
    damage_bonus: int = 0,
) -> Dict:
    """Resolve an attack and mutate the supplied combat state."""
    attacker = _find_actor(combat, attacker_name)
    target = _find_actor(combat, target_name)
    if attacker.get("defeated"):
        raise ValueError(f"{attacker_name} is defeated and cannot attack")
    if target.get("defeated"):
        raise ValueError(f"{target_name} is already defeated")

    bonus = int(attacker.get("attack_bonus", 0) if attack_bonus is None else attack_bonus)
    attack = roll("1d20")
    natural = int(attack["rolls"][0])
    total = int(attack["total"]) + bonus
    armor_class = int(target.get("armor_class", 10))

    critical = natural == 20
    automatic_miss = natural == 1
    hit = False if automatic_miss else (True if critical else total >= armor_class)
    damage = 0
    damage_rolls = []

    if hit:
        expression = damage_expression or str(attacker.get("damage", "1d4"))
        first = roll(expression)
        damage_rolls.append(first)
        damage = int(first["total"]) + int(damage_bonus)
        if critical:
            second = roll(expression)
            damage_rolls.append(second)
            damage += int(second["total"])
        damage = max(0, damage)
        target["hp"] = max(0, int(target.get("hp", 0)) - damage)
        target["defeated"] = target["hp"] <= 0

    outcome = {
        "attacker": attacker_name,
        "target": target_name,
        "d20": natural,
        "attack_bonus": bonus,
        "attack_total": total,
        "armor_class": armor_class,
        "hit": hit,
        "critical": critical,
        "damage": damage,
        "damage_rolls": damage_rolls,
        "target_hp": int(target.get("hp", 0)),
        "target_max_hp": int(target.get("max_hp", target.get("hp", 0))),
        "target_defeated": bool(target.get("defeated")),
    }
    combat.setdefault("log", []).append(outcome)
    _check_combat_end(combat)
    return outcome


def end_turn(combat: Dict) -> Dict:
    """Advance to the next living combatant, increasing the round on wrap."""
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
    living_teams = {
        actor.get("team")
        for actor in combat.get("combatants", [])
        if not actor.get("defeated")
    }
    if len(living_teams) <= 1:
        combat["active"] = False
        combat["winner"] = next(iter(living_teams), None)
