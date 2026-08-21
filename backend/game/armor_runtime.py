"""Runtime integration for the five-slot Armor HP system."""
from __future__ import annotations

from copy import deepcopy
from typing import Dict

from .armor import (
    apply_damage_to_armor,
    effective_movement,
    print_armor,
    run_starting_armor_creation,
    sync_armor_summary,
)


def _player_actor(combat: Dict, player_name: str) -> Dict | None:
    for actor in combat.get("combatants", []):
        if isinstance(actor, dict) and actor.get("name") == player_name:
            return actor
    return None


def _living_teams(combat: Dict) -> set:
    return {a.get("team") for a in combat.get("combatants", []) if not a.get("defeated")}


def _repair_combat_end_state(combat: Dict) -> None:
    """Recompute winner after Armor HP may have prevented an apparent defeat."""
    teams = _living_teams(combat)
    if len(teams) <= 1:
        combat["active"] = False
        combat["winner"] = next(iter(teams), None)
    else:
        combat["active"] = True
        combat.pop("winner", None)


def _inject_player_armor(game_master, combat: Dict) -> None:
    player = game_master.state.data.get("player", {})
    name = str(player.get("name") or "Traveler")
    actor = _player_actor(combat, name)
    if not actor:
        return
    actor["equipped_armor"] = deepcopy(player.get("equipped_armor", {}))
    actor["armor_set_name"] = player.get("armor_set_name")
    base_move = int(player.get("base_movement_without_armor", actor.get("movement", 1)) or 1)
    actor["base_movement_without_armor"] = base_move
    sync_armor_summary(actor)
    actor["movement"] = effective_movement(base_move, actor.get("equipped_armor", {}))


def _sync_player_from_combat(game_master, combat: Dict) -> None:
    player = game_master.state.data.get("player", {})
    name = str(player.get("name") or "Traveler")
    actor = _player_actor(combat, name)
    if not actor:
        return
    player["hp"] = int(actor.get("hp", player.get("hp", 0)) or 0)
    player["resource"] = int(actor.get("resource", player.get("resource", 0)) or 0)
    player["mana"] = player["resource"]
    if isinstance(actor.get("equipped_armor"), dict):
        player["equipped_armor"] = deepcopy(actor["equipped_armor"])
        player["armor_set_name"] = actor.get("armor_set_name")
        player["base_movement_without_armor"] = int(actor.get("base_movement_without_armor", player.get("base_movement_without_armor", 1)) or 1)
        sync_armor_summary(player)
    player["movement"] = int(actor.get("movement", player.get("movement", 1)) or 1)
    game_master.state.save()


def _retrofit_armor_after_damage(combat: Dict, outcome: Dict, target_name: str, *, damage_type: str | None = None) -> Dict:
    """Route already-calculated final damage through Armor HP before real HP."""
    if not isinstance(outcome, dict) or not outcome.get("hit"):
        return outcome
    damage = max(0, int(outcome.get("damage", 0) or 0))
    if damage <= 0:
        return outcome
    target = next((a for a in combat.get("combatants", []) if isinstance(a, dict) and a.get("name") == target_name), None)
    if not target or not isinstance(target.get("equipped_armor"), dict):
        return outcome

    sync_armor_summary(target)
    if int(target.get("max_armor", 0) or 0) <= 0:
        return outcome

    # Legacy resolver already deducted damage from HP. Restore that exact final damage,
    # then apply the SAME damage through Armor -> HP. No dice or attack rolls are rerolled.
    old_hp_after = int(target.get("hp", 0) or 0)
    max_hp = int(target.get("max_hp", old_hp_after) or old_hp_after)
    target["hp"] = min(max_hp, old_hp_after + damage)
    target["defeated"] = False
    split = apply_damage_to_armor(target, damage, damage_type=damage_type)

    base_move = int(target.get("base_movement_without_armor", target.get("movement", 1)) or 1)
    target["movement"] = effective_movement(base_move, target.get("equipped_armor", {}))

    outcome["armor_absorbed"] = split["armor_absorbed"]
    outcome["hp_damage"] = split["hp_damage"]
    outcome["armor_before"] = split["armor_before"]
    outcome["armor_after"] = split["armor_after"]
    outcome["target_armor"] = split["armor_after"]
    outcome["target_max_armor"] = split["max_armor"]
    outcome["target_hp"] = split["hp_after"]
    outcome["target_max_hp"] = int(target.get("max_hp", split["hp_after"]))
    outcome["target_defeated"] = bool(target.get("defeated"))
    outcome["broken_armor_pieces"] = split["broken_pieces"]
    outcome["resisted_by_armor"] = split["resisted_damage"]
    _repair_combat_end_state(combat)
    return outcome


def install_armor_runtime(game_master) -> None:
    """Patch the existing GM runtime once without duplicating the combat engine."""
    if getattr(game_master, "_armor_runtime_installed", False):
        return
    game_master._armor_runtime_installed = True

    original_start = game_master._start_combat
    def start_with_armor(request):
        combat = original_start(request)
        _inject_player_armor(game_master, combat)
        return combat
    game_master._start_combat = start_with_armor

    original_persist = game_master._persist_combat
    def persist_with_armor(combat):
        original_persist(combat)
        _sync_player_from_combat(game_master, combat)
    game_master._persist_combat = persist_with_armor

    # GameMaster imported these functions directly, so replace its module globals.
    import backend.ai.game_master as gm_module
    original_attack = gm_module.resolve_attack
    original_ability = gm_module.resolve_ability

    def attack_with_armor(combat, attacker_name, target_name, **kwargs):
        outcome = original_attack(combat, attacker_name, target_name, **kwargs)
        return _retrofit_armor_after_damage(combat, outcome, target_name)

    def ability_with_armor(combat, actor_name, ability_name, target_name=None, **kwargs):
        outcome = original_ability(combat, actor_name, ability_name, target_name, **kwargs)
        damage_type = None
        try:
            actor = next(a for a in combat.get("combatants", []) if a.get("name") == actor_name)
            ability = next(a for a in actor.get("abilities", []) if isinstance(a, dict) and str(a.get("name", "")).lower() == str(ability_name).lower())
            damage_type = ability.get("damage_type")
        except (StopIteration, TypeError):
            pass
        actual_target = str(outcome.get("target") or target_name or actor_name)
        return _retrofit_armor_after_damage(combat, outcome, actual_target, damage_type=damage_type)

    gm_module.resolve_attack = attack_with_armor
    gm_module.resolve_ability = ability_with_armor


def finish_character_creation_with_armor(game_master, created: Dict) -> Dict:
    """Run the final armor step, replacing obsolete starter-kit armor."""
    player = game_master.state.data.setdefault("player", {})
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    player["inventory"] = [
        item for item in inventory
        if not (isinstance(item, dict) and str(item.get("type") or "").strip().lower() == "armor")
    ]
    for item in player["inventory"]:
        if isinstance(item, dict):
            item.pop("armor_bonus", None)

    run_starting_armor_creation(game_master)
    created["player"] = deepcopy(game_master.state.data.get("player", {}))
    return created


def show_player_armor(game_master) -> None:
    player = game_master.state.data.get("player", {})
    if not isinstance(player.get("equipped_armor"), dict):
        print("\nYou do not have an equipped five-piece armor loadout yet.")
        return
    print_armor(player)
