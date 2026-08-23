"""Active ability resolution for The Shattered Realms combat prototype.

Abilities are data-driven. The rules engine validates ownership, action cost,
class resources, range, target, attack rolls, and damage. AI narration never
decides the mechanical result.
"""

from typing import Dict

from .attributes import attribute_check_bonus, normalize_attributes
from .combat import current_actor, grid_distance
from .dice import roll


TECH_RANGED_HINTS = (
    "aim", "shoot", "shot", "blaster", "repulsor", "firearm", "rifle",
    "pistol", "gun", "bow", "crossbow", "laser", "projectile", "cannon",
    "launcher", "ranged", "sniper", "throw", "thrown",
)
MAGIC_HINTS = (
    "spell", "magic", "arcane", "sorcery", "psychic", "psionic", "hex",
    "curse", "ritual", "mana",
)


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


def _ability_text(ability: Dict) -> str:
    return " ".join(
        str(ability.get(key) or "")
        for key in ("name", "description", "effect", "category")
    ).lower()


def attack_attribute_for_ability(ability: Dict) -> str:
    """Choose the gameplay stat from what the ability actually does.

    AI-created data occasionally labels a technological ranged attack as
    Intelligence. Aimed weapons are Dexterity attacks; actual supernatural
    powers may use Magic.
    """
    requested = str(ability.get("attack_attribute") or "").strip().lower()
    text = _ability_text(ability)
    if any(hint in text for hint in TECH_RANGED_HINTS):
        return "dexterity"
    if requested in {"strength", "dexterity", "magic"}:
        return requested
    if requested in {"intelligence", "wisdom"} or any(hint in text for hint in MAGIC_HINTS):
        return "magic"
    return "strength"


def _damage_attribute_for_ability(ability: Dict, attack_attribute: str) -> str:
    requested = str(ability.get("damage_bonus_attribute") or "").strip().lower()
    if attack_attribute == "dexterity" and requested in {"", "intelligence", "wisdom"}:
        return "dexterity"
    if requested in {"strength", "dexterity", "magic"}:
        return requested
    if requested in {"intelligence", "wisdom"}:
        return "magic"
    return ""


def prepare_ability_roll(
    combat: Dict,
    actor_name: str,
    ability_name: str,
    target_name: str | None = None,
    *,
    enforce_turn: bool = False,
) -> Dict | None:
    """Validate an attack ability and pause before its player-facing d20 roll.

    Returns ``None`` for abilities that do not require an attack roll so the
    existing instant-effect resolver can handle them.
    """
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
    if not bool(ability.get("requires_attack_roll", True)):
        return None

    name = str(ability.get("name") or ability_name)
    class_resource_name = str(actor.get("resource_name") or "Mana")
    class_resource_key = str(actor.get("resource_type") or class_resource_name.lower().replace(" ", "_"))
    requested_resource = str(ability.get("resource") or "class").strip().lower().replace(" ", "_")
    if requested_resource not in {"class", class_resource_key}:
        raise ValueError(f"{name} requires {ability.get('resource')} but {actor_name} uses {class_resource_name}")

    resource_cost = max(0, int(ability.get("resource_cost", 0) or 0))
    current_resource = int(actor.get("resource", actor.get("mana", 0)) or 0)
    if current_resource < resource_cost:
        raise ValueError(
            f"{actor_name} needs {resource_cost} {class_resource_name} for {name} "
            f"but only has {current_resource}"
        )

    target_type = str(ability.get("target") or "enemy").lower()
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

    attributes = normalize_attributes(actor.get("attributes"))
    attack_attribute = attack_attribute_for_ability(ability)
    stat_bonus = int(attribute_check_bonus(int(attributes.get(attack_attribute, 0))))
    other_bonus = int(ability.get("attack_bonus", 0) or 0)
    damage_attribute = _damage_attribute_for_ability(ability, attack_attribute)
    damage_bonus = int(attribute_check_bonus(int(attributes.get(damage_attribute, 0)))) if damage_attribute else 0
    base_armor_class = int(target.get("armor_class", 10) or 10)
    defense_bonus = int(target.get("active_defense_ac_bonus", 0) or 0) if target.get("defending") else 0
    armor_class = base_armor_class + defense_bonus
    armor_stats = actor.get("armor_stat_bonuses") if isinstance(actor.get("armor_stat_bonuses"), dict) else {}
    armor_stat_amount = int(armor_stats.get(attack_attribute, 0) or 0)

    actor["resource"] = current_resource - resource_cost
    actor["mana"] = actor["resource"]
    actor["primary_action_used"] = True
    actor["attack_committed"] = True

    pending = {
        "kind": "ability_attack",
        "source_kind": "ability",
        "stage": "attack",
        "purpose": f"Use {name} on {target.get('name')}",
        "expression": "1d20",
        "dc": armor_class,
        "modifier": stat_bonus + other_bonus,
        "modifier_breakdown": [
            {"source": f"{attack_attribute.title()} {int(attributes.get(attack_attribute, 0))}", "value": stat_bonus},
            {"source": f"{name} accuracy", "value": other_bonus},
        ],
        "dc_breakdown": [
            {"source": "Target defense", "value": base_armor_class},
            {"source": "Defending bonus", "value": defense_bonus},
        ],
        "armor_bonus_note": (
            f"Armor grants +{armor_stat_amount} {attack_attribute.title()}, already included in the stat above."
            if armor_stat_amount else ""
        ),
        "attacker": actor_name,
        "actor": actor_name,
        "ability": name,
        "target": str(target.get("name")),
        "target_type": target_type,
        "distance": distance,
        "attack_range": maximum_range,
        "attack_attribute": attack_attribute,
        "stat_accuracy_bonus": stat_bonus,
        "other_attack_bonus": other_bonus,
        "base_armor_class": base_armor_class,
        "defense_ac_bonus": defense_bonus,
        "damage_expression": str(ability.get("damage") or "0"),
        "damage_bonus_attribute": damage_attribute or None,
        "damage_bonus": damage_bonus,
        "resource": class_resource_key,
        "resource_name": class_resource_name,
        "resource_cost": resource_cost,
        "resource_before": current_resource,
        "resource_after": int(actor.get("resource", 0)),
        "requires_attack_roll": True,
        "critical_chance_percent": int(actor.get("critical_chance_percent", 5) or 5),
    }
    combat.setdefault("log", []).append({
        "type": "ability_declared", "actor": actor_name, "ability": name,
        "target": target.get("name"), "resource_cost": resource_cost,
    })
    return pending


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
    class_resource_name = str(actor.get("resource_name") or "Mana")
    class_resource_key = str(actor.get("resource_type") or class_resource_name.lower().replace(" ", "_"))
    requested_resource = str(ability.get("resource") or "class").strip().lower().replace(" ", "_")
    if requested_resource not in {"class", class_resource_key}:
        raise ValueError(f"{name} requires {ability.get('resource')} but {actor_name} uses {class_resource_name}")

    resource_cost = max(0, int(ability.get("resource_cost", 0) or 0))
    current_resource = int(actor.get("resource", actor.get("mana", 0)) or 0)
    if current_resource < resource_cost:
        raise ValueError(
            f"{actor_name} needs {resource_cost} {class_resource_name} for {name} "
            f"but only has {current_resource}"
        )

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

    attack_attribute = attack_attribute_for_ability(ability)
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
    damage_bonus_attribute = _damage_attribute_for_ability(ability, attack_attribute)
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

    # A legal ability attempt spends the resource and primary action even if its attack roll misses.
    actor["resource"] = current_resource - resource_cost
    actor["mana"] = actor["resource"]  # backward-compatible alias
    actor["primary_action_used"] = True

    outcome = {
        "actor": actor_name,
        "ability": name,
        "target": target.get("name"),
        "target_type": target_type,
        "distance": distance,
        "range": maximum_range,
        "resource": class_resource_key,
        "resource_name": class_resource_name,
        "resource_cost": resource_cost,
        "resource_before": current_resource,
        "resource_after": int(actor.get("resource", 0)),
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
