"""Authoritative combat engine for The Shattered Realms.

Combat follows the documented combat framework and canonical 0-30 attributes.
The rules engine owns mechanical values; AI narration must not invent results.
"""

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


def _normalize_position(position) -> Dict[str, int]:
    if isinstance(position, dict):
        return {"x": int(position.get("x", 0)), "y": int(position.get("y", 0))}
    if isinstance(position, (list, tuple)) and len(position) >= 2:
        return {"x": int(position[0]), "y": int(position[1])}
    return {"x": 0, "y": 0}


def grid_distance(a: Dict, b: Dict) -> int:
    """Return square-grid distance using orthogonal square steps."""
    pa = _normalize_position(a.get("position"))
    pb = _normalize_position(b.get("position"))
    return abs(pa["x"] - pb["x"]) + abs(pa["y"] - pb["y"])


def start_combat(combatants: List[Dict]) -> Dict:
    if not combatants:
        raise ValueError("Combat requires at least one combatant")
    prepared, initiative = [], []
    enemy_slot = 0
    player_slot = 0
    for raw in combatants:
        actor = deepcopy(raw)
        actor.setdefault("name", "Unknown combatant")
        actor.setdefault("team", "enemy")
        attrs = normalize_attributes(actor.get("attributes"))
        channels = character_sheet_channels(attrs, actor.get("level", 1))
        actor["attributes"] = attrs
        actor["attribute_channels"] = channels
        actor.setdefault("hp", channels["max_health_base"])
        actor.setdefault("max_hp", channels["max_health_base"])
        # Encounter enemy HP supplied by the Game Master is the enemy's full
        # encounter health, not an already-wounded value. Keep the denominator
        # locked to that starting HP so 17 HP stays 17/17 instead of becoming
        # 17/20 because of the generic attribute-derived health calculation.
        if actor.get("team") == "enemy" and "hp" in raw:
            actor["max_hp"] = int(actor["hp"])
        actor.setdefault("mana", channels["max_mana_base"])
        actor.setdefault("max_mana", channels["max_mana_base"])
        actor.setdefault("armor_class", 10 + channels["defense_bonus"])
        actor.setdefault("attack_bonus", 0)
        actor.setdefault("damage", "1d4")
        actor.setdefault("movement", channels["movement"])
        actor["movement_used"] = 0
        actor.setdefault("attack_range", 1)
        actor.setdefault("critical_chance_percent", channels["critical_chance_percent"])
        actor.setdefault("physical_resistance_percent", channels["physical_resistance_percent"])
        actor.setdefault("status_resistance_percent", channels["status_resistance_percent"])

        if "position" not in actor:
            if actor.get("team") == "player":
                actor["position"] = {"x": 0, "y": player_slot}
                player_slot += 1
            else:
                actor["position"] = {"x": 1, "y": enemy_slot}
                enemy_slot += 1
        else:
            actor["position"] = _normalize_position(actor.get("position"))

        actor["defeated"] = int(actor["hp"]) <= 0
        prepared.append(actor)
        initiative.append(roll_initiative(actor["name"], attrs, actor.get("initiative_bonus", 0)))
    initiative.sort(key=lambda item: (item["total"], item["modifier"]), reverse=True)
    return {"active": True, "round": 1, "turn_index": 0,
            "order": [i["name"] for i in initiative], "initiative": initiative,
            "combatants": prepared, "log": ["Combat begins."],
            "grid": {"type": "square", "distance": "orthogonal_steps"}}


def _find_actor(combat: Dict, name: str) -> Dict:
    for actor in combat.get("combatants", []):
        if actor.get("name") == name:
            return actor
    raise ValueError(f"Unknown combatant: {name}")


def current_actor(combat: Dict) -> Dict | None:
    if not combat.get("active") or not combat.get("order"):
        return None
    return _find_actor(combat, combat["order"][combat["turn_index"]])


def move_actor(combat: Dict, actor_name: str, x: int, y: int, *,
               enforce_turn: bool = False) -> Dict:
    actor = _find_actor(combat, actor_name)
    if actor.get("defeated"):
        raise ValueError(f"{actor_name} is defeated and cannot move")
    if enforce_turn:
        active = current_actor(combat)
        if not active or active.get("name") != actor_name:
            raise ValueError(f"It is not {actor_name}'s turn")

    destination = {"x": int(x), "y": int(y)}
    origin = _normalize_position(actor.get("position"))
    distance = abs(origin["x"] - destination["x"]) + abs(origin["y"] - destination["y"])
    movement_limit = int(actor.get("movement", 0))
    movement_used = int(actor.get("movement_used", 0))
    movement_remaining = max(0, movement_limit - movement_used)
    if distance > movement_remaining:
        raise ValueError(
            f"{actor_name} has only {movement_remaining} movement squares remaining this turn"
        )

    for other in combat.get("combatants", []):
        if other is actor or other.get("defeated"):
            continue
        if _normalize_position(other.get("position")) == destination:
            raise ValueError(f"Square ({destination['x']}, {destination['y']}) is occupied by {other.get('name')}")

    actor["position"] = destination
    actor["movement_used"] = movement_used + distance
    result = {
        "actor": actor_name,
        "from": origin,
        "to": destination,
        "distance": distance,
        "movement_limit": movement_limit,
        "movement_used": actor["movement_used"],
        "movement_remaining": max(0, movement_limit - actor["movement_used"]),
    }
    combat.setdefault("log", []).append({"type": "move", **result})
    return result


def resolve_attack(combat: Dict, attacker_name: str, target_name: str, *,
                   attack_bonus: int | None = None, damage_expression: str | None = None,
                   damage_bonus: int | None = None, attack_attribute: str = "strength",
                   attack_range: int | None = None, enforce_turn: bool = False) -> Dict:
    attacker, target = _find_actor(combat, attacker_name), _find_actor(combat, target_name)
    if attacker.get("defeated"):
        raise ValueError(f"{attacker_name} is defeated and cannot attack")
    if target.get("defeated"):
        raise ValueError(f"{target_name} is already defeated")
    if enforce_turn:
        active = current_actor(combat)
        if not active or active.get("name") != attacker_name:
            raise ValueError(f"It is not {attacker_name}'s turn")

    distance = grid_distance(attacker, target)
    maximum_range = int(attacker.get("attack_range", 1) if attack_range is None else attack_range)
    if distance > maximum_range:
        raise ValueError(
            f"{target_name} is {distance} squares away; {attacker_name}'s attack range is {maximum_range}"
        )

    attrs = normalize_attributes(attacker.get("attributes"))
    channels = character_sheet_channels(attrs, attacker.get("level", 1))
    if attack_attribute == "dexterity":
        stat_accuracy = int(channels["dexterity_attack_accuracy"])
        default_damage_bonus = 0
    else:
        attack_attribute = "strength"
        stat_accuracy = int(channels["strength_attack_accuracy"])
        default_damage_bonus = int(channels["strength_damage_bonus"])

    other_bonus = int(attacker.get("attack_bonus", 0) if attack_bonus is None else attack_bonus)
    total_attack_bonus = stat_accuracy + other_bonus
    attack = roll("1d20")
    natural = int(attack["rolls"][0])
    total = int(attack["total"]) + total_attack_bonus
    armor_class = int(target.get("armor_class", 10))
    automatic_miss = natural == 1
    automatic_hit = natural == 20
    hit = False if automatic_miss else (True if automatic_hit else total >= armor_class)

    # Criticals have two routes by design: a natural 20 is always critical,
    # while other successful hits can crit through the attacker's Dexterity-
    # based critical chance.
    crit_chance = int(attacker.get("critical_chance_percent", channels["critical_chance_percent"]))
    crit_roll = int(roll("1d100")["total"]) if hit and not automatic_hit else None
    critical = bool(automatic_hit or (hit and crit_roll is not None and crit_roll <= crit_chance))

    # A hit that beats Armor Class by a wide margin lands more cleanly.
    # Every complete 3 points above AC adds +1 flat damage. This bonus is
    # applied once even on a critical hit.
    accuracy_margin = max(0, total - armor_class) if hit else 0
    accuracy_margin_damage_bonus = accuracy_margin // 3

    applied_damage_bonus = int(default_damage_bonus if damage_bonus is None else damage_bonus)
    damage, damage_rolls, raw_damage, resistance_percent = 0, [], 0, 0
    if hit:
        expression = damage_expression or str(attacker.get("damage", "1d4"))
        first = roll(expression)
        damage_rolls.append(first)
        raw_damage = int(first["total"]) + applied_damage_bonus + accuracy_margin_damage_bonus
        if critical:
            extra = roll(expression)
            damage_rolls.append(extra)
            raw_damage += int(extra["total"])
        resistance_percent = int(target.get("physical_resistance_percent", 0))
        damage = max(0, round(raw_damage * (100 - resistance_percent) / 100))
        target["hp"] = max(0, int(target.get("hp", 0)) - damage)
        target["defeated"] = target["hp"] <= 0

    outcome = {"attacker": attacker_name, "target": target_name,
               "attack_attribute": attack_attribute, "distance": distance,
               "attack_range": maximum_range, "d20": natural,
               "stat_accuracy_bonus": stat_accuracy, "other_attack_bonus": other_bonus,
               "attack_bonus": total_attack_bonus, "attack_total": total,
               "armor_class": armor_class, "hit": hit, "critical": critical,
               "critical_roll": crit_roll, "critical_chance_percent": crit_chance,
               "accuracy_margin": accuracy_margin,
               "accuracy_margin_damage_bonus": accuracy_margin_damage_bonus,
               "damage_bonus": applied_damage_bonus, "raw_damage": raw_damage,
               "physical_resistance_percent": resistance_percent,
               "damage": damage, "damage_rolls": damage_rolls,
               "target_hp": int(target.get("hp", 0)),
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
            actor["movement_used"] = 0
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
