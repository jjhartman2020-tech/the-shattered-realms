"""Active ability resolution for The Shattered Realms combat prototype.

Abilities are data-driven. The rules engine validates ownership, action cost,
resources, range, target, attack rolls, damage, and cooldowns. AI narration
never decides the mechanical result.
"""

from typing import Dict

from .attributes import attribute_check_bonus, normalize_attributes
from .combat import current_actor, grid_distance
from .dice import roll


def _find_actor(combat: Dict, name: str) -> Dict:
    for actor in combat.get("combatants", []):
        if actor.get("name") == name:
            return actor
    raise ValueError(f"Unknown combatant: {name}")


def _find_ability(actor: Dict, ability_name: str) -> Dict:
    requested = str(ability_name or "").strip().lower()
    for ability in actor.get("abilities", []):
        if isinstance(ability, dict) and str(ability.get("name") or "").strip().lower() == requested:
            return ability
    raise ValueError(f"{actor.get('name', 'Combatant')} does not have an equipped ability named {ability_name}")


def resolve_ability(
    combat: Dict,
    actor_name: str,
    ability_name: str,
    target_name: str | None = None,
    *,
    enforce_turn: bool = False,
) -> Dict:
    """Resolve one equipped active ability and mutate authoritative combat state."""
    actor = _find_actor(combat, actor_name)
    if actor.get("defeated"):
        raise ValueError(f"{actor_name} is defeated and cannot use abilities")
    if enforce_turn:
        active = current_actor(combat)
        if not active or active.get("name") != actor_name:
            raise ValueError(f"It is not {actor_name}'s turn")
    if actor.get("primary_action_used"):
        raise ValueError(f"{actor_name} has already used the primary action this turn")

    ability = _find_ability(actor, ability_name)
    if str(ability.get("type") or "active").lower() != "active":
        raise ValueError(f"{ability.get('name')} is not an active ability")

    name = str(ability.get("name") or ability_name)
    resource = str(ability.get("resource") or "mana").lower()
    resource_cost = max(0, int(ability.get("resource_cost", 0) or 0))
    if resource != "mana":
        raise ValueError(f"Prototype ability engine does not support {resource} yet")
    current_resource = int(actor.get("mana", 0) or 0)
    if current_resource < resource_cost:
        raise ValueError(f"{actor_name} needs {resource_cost} mana for {name} but only has {current_resource}")

    current_round = int(combat.get("round", 1) or 1)
    cooldowns = actor.setdefault("ability_cooldowns", {})
    ready_round = int(cooldowns.get(name, 0) or 0)
    if current_round < ready_round:
        turns_remaining = ready_round - current_round
        raise ValueError(f"{name} is on cooldown for {turns_remaining} more turn(s)")

    target_type = str(ability.get("target") or "enemy").lower()
    target = None
    if target_type == "self":
        target = actor
    else:
        if not target_name:
            raise ValueError(f"{name} requires a target")
        target = _find_actor(combat, str(target_name))
        if target.get("defeated"):
            raise ValueError(f"{target.get('name')} is already defeated")
        if target_type == "enemy" and target.get("team") == actor.get("team"):
            raise ValueError(f"{name} must target an enemy")
        if target_type == "ally" and target.get("team") != actor.get("team"):
            raise ValueError(f"{name} must target an ally")

    maximum_range = max(0, int(ability.get("range", 1) or 0))
    distance = 0 if target is actor else grid_distance(actor, target)
    if distance > maximum_range:
        raise ValueError(f"{target.get('name')} is {distance} squares away; {name}'s range is {maximum_range}")

    attack_attribute = str(ability.get("attack_attribute") or "strength").lower()
    attrs = normalize_attributes(actor.get("attributes"))
    if attack_attribute not in attrs:
        attack_attribute = "strength"
    stat_bonus = int(attribute_check_bonus(int(attrs.get(attack_attribute, 0))))
    other_bonus = int(ability.get("attack_bonus", 0) or 0)
    attack_bonus = stat_bonus + other_bonus

    requires_attack_roll = bool(ability.get("requires_attack_roll", True))
    natural = None
    attack_total = None
    armor_class = None
    hit = True
    critical = False
    if requires_attack_roll:
        attack = roll("1d20")
        natural = int(attack["rolls"][0])
        attack_total = int(attack["total"]) + attack_bonus
        base_ac = int(target.get("armor_class", 10))
        defense_bonus = int(target.get("active_defense_ac_bonus", 0)) if target.get("defending") else 0
        armor_class = base_ac + defense_bonus
        hit = False if natural == 1 else (True if natural == 20 else attack_total >= armor_class)
        critical = natural == 20

    damage_expression = str(ability.get("damage") or "0")
    damage_bonus_attribute = str(ability.get("damage_bonus_attribute") or "").lower()
    damage_stat_bonus = 0
    if damage_bonus_attribute in attrs:
        damage_stat_bonus = int(attribute_check_bonus(int(attrs.get(damage_bonus_attribute, 0))))

    raw_damage = 0
    damage = 0
    damage_rolls = []
    resistance_percent = 0
    if hit and damage_expression not in {"", "0", "none"}:
        first = roll(damage_expression)
        damage_rolls.append(first)
        raw_damage = int(first["total"]) + damage_stat_bonus
        if critical:
            extra = roll(damage_expression)
            damage_rolls.append(extra)
            raw_damage += int(extra["total"])
        resistance_percent = int(target.get("physical_resistance_percent", 0) or 0)
        damage = max(0, round(raw_damage * (100 - resistance_percent) / 100))
        target["hp"] = max(0, int(target.get("hp", 0)) - damage)
        target["defeated"] = target["hp"] <= 0

    actor["mana"] = current_resource - resource_cost
    actor["primary_action_used"] = True
    cooldown_turns = max(0, int(ability.get("cooldown", 0) or 0))
    if cooldown_turns:
        cooldowns[name] = current_round + cooldown_turns + 1

    outcome = {
        "actor": actor_name,
        "ability": name,
        "target": target.get("name"),
        "target_type": target_type,
        "distance": distance,
        "range": maximum_range,
        "resource": resource,
        "resource_cost": resource_cost,
        "resource_before": current_resource,
        "resource_after": int(actor.get("mana", 0)),
        "attack_attribute": attack_attribute,
        "stat_accuracy_bonus": stat_bonus,
        "other_attack_bonus": other_bonus,
        "attack_bonus": attack_bonus,
        "requires_attack_roll": requires_attack_roll,
        "d20": natural,
        "attack_total": attack_total,
        "armor_class": armor_class,
        "hit": hit,
        "critical": critical,
        "damage_expression": damage_expression,
        "damage_bonus_attribute": damage_bonus_attribute or None,
        "damage_bonus": damage_stat_bonus,
        "raw_damage": raw_damage,
        "physical_resistance_percent": resistance_percent,
        "damage": damage,
        "damage_rolls": damage_rolls,
        "cooldown_turns": cooldown_turns,
        "ready_round": cooldowns.get(name, current_round),
        "primary_action_used": True,
        "target_hp": int(target.get("hp", 0)),
        "target_max_hp": int(target.get("max_hp", target.get("hp", 0))),
        "target_defeated": bool(target.get("defeated")),
    }
    combat.setdefault("log", []).append({"type": "ability", **outcome})

    living_teams = {a.get("team") for a in combat.get("combatants", []) if not a.get("defeated")}
    if len(living_teams) <= 1:
        combat["active"] = False
        combat["winner"] = next(iter(living_teams), None)
    return outcome
