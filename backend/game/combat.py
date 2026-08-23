"""Authoritative combat engine for The Shattered Realms.

Combat follows the documented combat framework and canonical 0-100 attributes.
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


def _sync_resource_aliases(actor: Dict) -> None:
    actor["mana"] = int(actor.get("resource", 0) or 0)
    actor["max_mana"] = int(actor.get("max_resource", 0) or 0)


def _regenerate_resource_for_turn(actor: Dict) -> int:
    """Regenerate the actor's documented per-round class resource at turn start."""
    current = int(actor.get("resource", actor.get("mana", 0)) or 0)
    maximum = int(actor.get("max_resource", actor.get("max_mana", 0)) or 0)
    regen = int(actor.get("resource_regeneration_per_round", 0) or 0)
    new_value = min(maximum, current + max(0, regen))
    actor["resource"] = new_value
    actor["max_resource"] = maximum
    _sync_resource_aliases(actor)
    return new_value - current


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
        if actor.get("team") == "enemy" and "hp" in raw:
            actor["max_hp"] = int(actor["hp"])
        actor.setdefault("resource", channels["max_resource_base"])
        actor.setdefault("max_resource", channels["max_resource_base"])
        actor.setdefault("resource_regeneration_per_round", channels["resource_regeneration_per_round"])
        _sync_resource_aliases(actor)
        actor.setdefault("armor_class", 10 + channels["defense_bonus"])
        actor.setdefault("attack_bonus", 0)
        actor.setdefault("damage", "1d4")
        actor.setdefault("movement", channels["movement"])
        actor.setdefault("defend_action_ac_bonus", channels["defend_action_ac_bonus"])
        actor["movement_used"] = 0
        actor["primary_action_used"] = False
        actor["defending"] = False
        actor["active_defense_ac_bonus"] = 0
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
            "grid": {"type": "square", "distance": "orthogonal_steps", "width": 12, "height": 8}}


def _find_actor(combat: Dict, name: str) -> Dict:
    for actor in combat.get("combatants", []):
        if actor.get("name") == name:
            return actor
    raise ValueError(f"Unknown combatant: {name}")


def current_actor(combat: Dict) -> Dict | None:
    if not combat.get("active") or not combat.get("order"):
        return None
    return _find_actor(combat, combat["order"][combat["turn_index"]])


def _require_turn(combat: Dict, actor: Dict, actor_name: str) -> None:
    active = current_actor(combat)
    if not active or active.get("name") != actor_name:
        raise ValueError(f"It is not {actor_name}'s turn")
    if actor.get("defeated"):
        raise ValueError(f"{actor_name} is defeated and cannot act")


def _require_primary_action(actor: Dict, actor_name: str) -> None:
    if actor.get("primary_action_used"):
        raise ValueError(f"{actor_name} has already used the primary action this turn")


def move_actor(combat: Dict, actor_name: str, x: int, y: int, *,
               enforce_turn: bool = False) -> Dict:
    actor = _find_actor(combat, actor_name)
    if actor.get("defeated"):
        raise ValueError(f"{actor_name} is defeated and cannot move")
    if enforce_turn:
        _require_turn(combat, actor, actor_name)
    if actor.get("attack_committed"):
        raise ValueError(f"{actor_name} has already attacked; attacking ends movement for this turn")

    destination = {"x": int(x), "y": int(y)}
    grid = combat.get("grid") if isinstance(combat.get("grid"), dict) else {}
    grid_width = max(1, int(grid.get("width", 12) or 12))
    grid_height = max(1, int(grid.get("height", 8) or 8))
    if destination["x"] < 0 or destination["x"] >= grid_width or destination["y"] < 0 or destination["y"] >= grid_height:
        raise ValueError(f"Square ({destination['x']}, {destination['y']}) is outside the {grid_width}x{grid_height} battle grid")
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


def prepare_attack(combat: Dict, attacker_name: str, target_name: str, *,
                   attack_bonus: int | None = None, damage_expression: str | None = None,
                   damage_bonus: int | None = None, attack_attribute: str = "strength",
                   attack_range: int | None = None, enforce_turn: bool = False) -> Dict:
    """Validate and lock in an attack without rolling any player-facing dice."""
    attacker, target = _find_actor(combat, attacker_name), _find_actor(combat, target_name)
    if attacker.get("defeated"):
        raise ValueError(f"{attacker_name} is defeated and cannot attack")
    if target.get("defeated"):
        raise ValueError(f"{target_name} is already defeated")
    if enforce_turn:
        _require_turn(combat, attacker, attacker_name)
        _require_primary_action(attacker, attacker_name)

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
    elif attack_attribute == "magic":
        stat_accuracy = int(channels["magic_attack_accuracy"])
        default_damage_bonus = 0
    else:
        attack_attribute = "strength"
        stat_accuracy = int(channels["strength_attack_accuracy"])
        default_damage_bonus = int(channels["strength_damage_bonus"])

    other_bonus = int(attacker.get("attack_bonus", 0) if attack_bonus is None else attack_bonus)
    base_armor_class = int(target.get("armor_class", 10))
    defense_ac_bonus = int(target.get("active_defense_ac_bonus", 0)) if target.get("defending") else 0
    armor_class = base_armor_class + defense_ac_bonus
    applied_damage_bonus = int(default_damage_bonus if damage_bonus is None else damage_bonus)
    armor_stat_bonuses = attacker.get("armor_stat_bonuses") if isinstance(attacker.get("armor_stat_bonuses"), dict) else {}
    armor_stat_amount = int(armor_stat_bonuses.get(attack_attribute, 0) or 0)

    attacker["primary_action_used"] = True
    attacker["attack_committed"] = True
    pending = {
        "kind": "attack",
        "stage": "attack",
        "purpose": f"Aim at {target_name}",
        "expression": "1d20",
        "dc": armor_class,
        "modifier": stat_accuracy + other_bonus,
        "modifier_breakdown": [
            {"source": f"{attack_attribute.title()} {int(attrs.get(attack_attribute, 0))}", "value": stat_accuracy},
            {"source": "Weapon / gear accuracy", "value": other_bonus},
        ],
        "dc_breakdown": [
            {"source": "Target defense", "value": base_armor_class},
            {"source": "Defending bonus", "value": defense_ac_bonus},
        ],
        "armor_bonus_note": (
            f"Armor grants +{armor_stat_amount} {attack_attribute.title()}, already included in the stat above."
            if armor_stat_amount else ""
        ),
        "attacker": attacker_name,
        "target": target_name,
        "attack_attribute": attack_attribute,
        "distance": distance,
        "attack_range": maximum_range,
        "stat_accuracy_bonus": stat_accuracy,
        "other_attack_bonus": other_bonus,
        "base_armor_class": base_armor_class,
        "defense_ac_bonus": defense_ac_bonus,
        "damage_expression": damage_expression or str(attacker.get("damage", "1d4")),
        "damage_bonus": applied_damage_bonus,
        "critical_chance_percent": int(attacker.get("critical_chance_percent", channels["critical_chance_percent"])),
    }
    combat.setdefault("log", []).append({"type": "attack_declared", "attacker": attacker_name, "target": target_name})
    return pending


def resolve_prepared_attack_roll(combat: Dict, pending: Dict) -> Dict:
    """Roll only the d20 portion of an attack and return its hit result."""
    if pending.get("kind") not in {"attack", "ability_attack"} or pending.get("stage") != "attack":
        raise ValueError("No attack roll is waiting.")
    attacker = _find_actor(combat, str(pending.get("attacker") or ""))
    target = _find_actor(combat, str(pending.get("target") or ""))
    if target.get("defeated"):
        raise ValueError(f"{target.get('name')} is already defeated")

    attack = roll("1d20")
    natural = int(attack["rolls"][0])
    attack_bonus = int(pending.get("modifier", 0) or 0)
    total = int(attack["total"]) + attack_bonus
    armor_class = int(pending.get("dc", target.get("armor_class", 10)) or 10)
    automatic_miss = natural == 1
    automatic_hit = natural == 20
    hit = False if automatic_miss else (True if automatic_hit else total >= armor_class)
    crit_chance = int(pending.get("critical_chance_percent", 5) or 5)
    crit_roll = int(roll("1d100")["total"]) if hit and not automatic_hit else None
    critical = bool(automatic_hit or (hit and crit_roll is not None and crit_roll <= crit_chance))
    accuracy_margin = max(0, total - armor_class) if hit else 0
    accuracy_margin_damage_bonus = accuracy_margin // 3

    result = {
        "attacker": str(pending.get("attacker")),
        "target": str(pending.get("target")),
        "attack_attribute": str(pending.get("attack_attribute") or "strength"),
        "distance": int(pending.get("distance", 0) or 0),
        "attack_range": int(pending.get("attack_range", 1) or 1),
        "d20": natural,
        "stat_accuracy_bonus": int(pending.get("stat_accuracy_bonus", 0) or 0),
        "other_attack_bonus": int(pending.get("other_attack_bonus", 0) or 0),
        "attack_bonus": attack_bonus,
        "attack_total": total,
        "base_armor_class": int(pending.get("base_armor_class", armor_class) or armor_class),
        "defense_ac_bonus": int(pending.get("defense_ac_bonus", 0) or 0),
        "armor_class": armor_class,
        "hit": hit,
        "critical": critical,
        "critical_roll": crit_roll,
        "critical_chance_percent": crit_chance,
        "accuracy_margin": accuracy_margin,
        "accuracy_margin_damage_bonus": accuracy_margin_damage_bonus,
        "primary_action_used": True,
    }
    if pending.get("source_kind") == "ability":
        result.update({
            "source_kind": "ability",
            "actor": str(pending.get("actor") or pending.get("attacker") or ""),
            "ability": str(pending.get("ability") or "Ability"),
            "target_type": str(pending.get("target_type") or "enemy"),
            "resource": pending.get("resource"),
            "resource_name": pending.get("resource_name"),
            "resource_cost": int(pending.get("resource_cost", 0) or 0),
            "resource_before": int(pending.get("resource_before", 0) or 0),
            "resource_after": int(pending.get("resource_after", 0) or 0),
            "requires_attack_roll": True,
            "damage_expression": str(pending.get("damage_expression") or "0"),
            "damage_bonus_attribute": pending.get("damage_bonus_attribute"),
            "damage_bonus": int(pending.get("damage_bonus", 0) or 0),
        })
    combat.setdefault("log", []).append({"type": "attack_roll", **result})
    return result


def prepare_damage_roll(combat: Dict, pending: Dict, attack_result: Dict) -> Dict:
    """Create the visible damage-roll card after a successful attack roll."""
    target = _find_actor(combat, str(pending.get("target") or ""))
    base_bonus = int(pending.get("damage_bonus", 0) or 0)
    accuracy_bonus = int(attack_result.get("accuracy_margin_damage_bonus", 0) or 0)
    resistance = int(target.get("physical_resistance_percent", 0) or 0)
    armor_hp = int(target.get("armor", 0) or 0)
    shield_hp = int(target.get("shield_hp", 0) or 0)
    expression = str(pending.get("damage_expression") or "1d4")
    protection_notes = []
    if shield_hp:
        protection_notes.append(f"Target has {shield_hp} Shield HP, which absorbs damage first")
    if armor_hp:
        protection_notes.append(f"Target has {armor_hp} Armor HP, which absorbs damage before HP")
    if resistance:
        protection_notes.append(f"Target resistance reduces remaining damage by {resistance}%")
    return {
        "kind": "damage",
        "stage": "damage",
        "purpose": f"Damage against {target.get('name')}",
        "expression": expression,
        "dc": None,
        "modifier": base_bonus + accuracy_bonus,
        "modifier_breakdown": [
            {"source": "Stat damage bonus", "value": base_bonus},
            {"source": "Accurate-hit bonus", "value": accuracy_bonus},
        ],
        "armor_bonus_note": ". ".join(protection_notes) + ("." if protection_notes else ""),
        "attacker": str(pending.get("attacker")),
        "target": str(pending.get("target")),
        "source_kind": pending.get("source_kind"),
        "ability": pending.get("ability"),
        "damage_expression": expression,
        "damage_bonus": base_bonus,
        "accuracy_margin_damage_bonus": accuracy_bonus,
        "physical_resistance_percent": resistance,
        "target_armor_hp": armor_hp,
        "target_shield_hp": shield_hp,
        "critical": bool(attack_result.get("critical")),
        "attack_result": deepcopy(attack_result),
    }


def resolve_prepared_damage_roll(combat: Dict, pending: Dict) -> Dict:
    """Roll damage, apply it, and finish the stored attack result."""
    if pending.get("kind") != "damage" or pending.get("stage") != "damage":
        raise ValueError("No damage roll is waiting.")
    target = _find_actor(combat, str(pending.get("target") or ""))
    expression = str(pending.get("damage_expression") or pending.get("expression") or "1d4")
    damage_rolls = [roll(expression)]
    if bool(pending.get("critical")):
        damage_rolls.append(roll(expression))
    raw_damage = sum(int(item["total"]) for item in damage_rolls) + int(pending.get("modifier", 0) or 0)
    resistance = int(pending.get("physical_resistance_percent", 0) or 0)
    damage = max(0, round(raw_damage * (100 - resistance) / 100))
    target["hp"] = max(0, int(target.get("hp", 0)) - damage)
    target["defeated"] = target["hp"] <= 0

    outcome = deepcopy(pending.get("attack_result")) if isinstance(pending.get("attack_result"), dict) else {}
    outcome.update({
        "damage_bonus": int(pending.get("damage_bonus", 0) or 0),
        "accuracy_margin_damage_bonus": int(pending.get("accuracy_margin_damage_bonus", 0) or 0),
        "raw_damage": raw_damage,
        "physical_resistance_percent": resistance,
        "damage": damage,
        "damage_rolls": damage_rolls,
        "target_hp": int(target.get("hp", 0)),
        "target_max_hp": int(target.get("max_hp", target.get("hp", 0))),
        "target_defeated": bool(target.get("defeated")),
    })
    combat.setdefault("log", []).append({"type": "damage_roll", **outcome})
    _check_combat_end(combat)
    return outcome


def defend_actor(combat: Dict, actor_name: str, *, enforce_turn: bool = False) -> Dict:
    """Spend the primary action to gain Defense-scaled AC until next turn."""
    actor = _find_actor(combat, actor_name)
    if enforce_turn:
        _require_turn(combat, actor, actor_name)
    _require_primary_action(actor, actor_name)
    attrs = normalize_attributes(actor.get("attributes"))
    channels = character_sheet_channels(attrs, actor.get("level", 1))
    defense_score = int(attrs.get("defense", 0))
    defense_ac_bonus = int(channels.get("defend_action_ac_bonus", 0))
    actor["primary_action_used"] = True
    actor["defending"] = True
    actor["active_defense_ac_bonus"] = defense_ac_bonus
    result = {
        "actor": actor_name,
        "defending": True,
        "defense_score": defense_score,
        "defense_ac_bonus": defense_ac_bonus,
        "primary_action_used": True,
    }
    combat.setdefault("log", []).append({"type": "defend", **result})
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
        _require_turn(combat, attacker, attacker_name)
        _require_primary_action(attacker, attacker_name)

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
    elif attack_attribute == "magic":
        stat_accuracy = int(channels["magic_attack_accuracy"])
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
    base_armor_class = int(target.get("armor_class", 10))
    defense_ac_bonus = int(target.get("active_defense_ac_bonus", 0)) if target.get("defending") else 0
    armor_class = base_armor_class + defense_ac_bonus
    automatic_miss = natural == 1
    automatic_hit = natural == 20
    hit = False if automatic_miss else (True if automatic_hit else total >= armor_class)

    crit_chance = int(attacker.get("critical_chance_percent", channels["critical_chance_percent"]))
    crit_roll = int(roll("1d100")["total"]) if hit and not automatic_hit else None
    critical = bool(automatic_hit or (hit and crit_roll is not None and crit_roll <= crit_chance))

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

    attacker["primary_action_used"] = True
    outcome = {"attacker": attacker_name, "target": target_name,
               "attack_attribute": attack_attribute, "distance": distance,
               "attack_range": maximum_range, "d20": natural,
               "stat_accuracy_bonus": stat_accuracy, "other_attack_bonus": other_bonus,
               "attack_bonus": total_attack_bonus, "attack_total": total,
               "base_armor_class": base_armor_class,
               "defense_ac_bonus": defense_ac_bonus,
               "armor_class": armor_class, "hit": hit, "critical": critical,
               "critical_roll": crit_roll, "critical_chance_percent": crit_chance,
               "accuracy_margin": accuracy_margin,
               "accuracy_margin_damage_bonus": accuracy_margin_damage_bonus,
               "damage_bonus": applied_damage_bonus, "raw_damage": raw_damage,
               "physical_resistance_percent": resistance_percent,
               "damage": damage, "damage_rolls": damage_rolls,
               "primary_action_used": True,
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
            actor["primary_action_used"] = False
            actor["attack_committed"] = False
            actor["defending"] = False
            actor["active_defense_ac_bonus"] = 0
            regenerated = _regenerate_resource_for_turn(actor)
            if regenerated > 0:
                combat.setdefault("log", []).append({
                    "type": "resource_regeneration",
                    "actor": actor.get("name"),
                    "amount": regenerated,
                    "resource": actor.get("resource"),
                    "max_resource": actor.get("max_resource"),
                })
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
        # Stats.md: class resources refill completely after a finished battle.
        for actor in combat.get("combatants", []):
            maximum = int(actor.get("max_resource", actor.get("max_mana", 0)) or 0)
            actor["resource"] = maximum
            actor["max_resource"] = maximum
            _sync_resource_aliases(actor)
