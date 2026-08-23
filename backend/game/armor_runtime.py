"""Runtime integration for Armor HP, shield HP, and armor stat bonuses."""
from __future__ import annotations

from copy import deepcopy
from typing import Dict

from .armor import apply_armor_stat_bonuses, apply_damage_to_armor, effective_movement, print_armor, run_starting_armor_creation, sync_armor_summary


def _player_actor(combat: Dict, player_name: str) -> Dict | None:
    return next((a for a in combat.get("combatants", []) if isinstance(a, dict) and a.get("name") == player_name), None)


def _living_teams(combat: Dict) -> set:
    return {a.get("team") for a in combat.get("combatants", []) if not a.get("defeated")}


def _repair_combat_end_state(combat: Dict) -> None:
    teams = _living_teams(combat)
    if len(teams) <= 1:
        combat["active"] = False; combat["winner"] = next(iter(teams), None)
    else:
        combat["active"] = True; combat.pop("winner", None)


def _resource_snapshot(combat: Dict) -> Dict[str, tuple[int, int]]:
    return {str(a.get("name")): (int(a.get("resource", a.get("mana", 0)) or 0), int(a.get("max_resource", a.get("max_mana", 0)) or 0)) for a in combat.get("combatants", []) if isinstance(a, dict)}


def _restore_resources(combat: Dict, snapshot: Dict[str, tuple[int, int]], *, ability_actor: str | None = None, ability_after: int | None = None) -> None:
    for actor in combat.get("combatants", []):
        name = str(actor.get("name"))
        if name not in snapshot: continue
        current, maximum = snapshot[name]
        if ability_actor == name and ability_after is not None: current = int(ability_after)
        actor["resource"] = current; actor["max_resource"] = maximum; actor["mana"] = current; actor["max_mana"] = maximum


def _sanitize_old_package_armor(package: Dict) -> Dict:
    result = deepcopy(package)
    kits = []
    for raw_kit in result.get("starter_kits", []):
        kit = deepcopy(raw_kit) if isinstance(raw_kit, dict) else {}; items = []
        for raw in kit.get("items", []):
            if not isinstance(raw, dict): continue
            item = deepcopy(raw)
            if str(item.get("type") or "").strip().lower() == "armor": continue
            item.pop("armor_bonus", None); items.append(item)
        kit["items"] = items; kits.append(kit)
    result["starter_kits"] = kits
    special = []
    for raw in result.get("special_equipment", []):
        if not isinstance(raw, dict): continue
        item = deepcopy(raw)
        if str(item.get("type") or "").strip().lower() == "armor": continue
        item.pop("armor_bonus", None); special.append(item)
    result["special_equipment"] = special
    return result


def _install_character_creation_hook() -> None:
    import backend.game.character_creation as cc
    current = cc.generate_character_package
    if getattr(current, "_five_slot_armor_hook", False): return
    def wrapped(*args, **kwargs): return _sanitize_old_package_armor(current(*args, **kwargs))
    wrapped._five_slot_armor_hook = True; cc.generate_character_package = wrapped


def _refresh_actor_armor_stats(actor: Dict) -> None:
    base_attrs = actor.get("base_attributes_without_armor")
    if not isinstance(base_attrs, dict):
        base_attrs = deepcopy(actor.get("attributes", {})); actor["base_attributes_without_armor"] = deepcopy(base_attrs)
    actor["attributes"] = apply_armor_stat_bonuses(base_attrs, actor.get("equipped_armor", {}))
    sync_armor_summary(actor)


def _inject_player_armor(game_master, combat: Dict) -> None:
    player = game_master.state.data.get("player", {}); actor = _player_actor(combat, str(player.get("name") or "Traveler"))
    if not actor: return
    actor["equipped_armor"] = deepcopy(player.get("equipped_armor", {})); actor["armor_set_name"] = player.get("armor_set_name")
    actor["equipped_shield"] = deepcopy(player.get("equipped_shield")) if isinstance(player.get("equipped_shield"), dict) else None
    actor["shield_hp"] = max(0, int(player.get("shield_hp", 0) or 0))
    actor["max_shield_hp"] = max(actor["shield_hp"], int(player.get("max_shield_hp", actor["shield_hp"]) or actor["shield_hp"]))
    actor["base_attributes_without_armor"] = deepcopy(actor.get("attributes", {})); _refresh_actor_armor_stats(actor)
    base = int(player.get("base_movement_without_armor", actor.get("movement", 1)) or 1); actor["base_movement_without_armor"] = base
    actor["movement"] = effective_movement(base, actor.get("equipped_armor", {}))


def _sync_player_from_combat(game_master, combat: Dict) -> None:
    player = game_master.state.data.get("player", {}); actor = _player_actor(combat, str(player.get("name") or "Traveler"))
    if not actor: return
    player["hp"] = int(actor.get("hp", player.get("hp", 0)) or 0); player["resource"] = int(actor.get("resource", player.get("resource", 0)) or 0); player["mana"] = player["resource"]
    player["shield_hp"] = max(0, int(actor.get("shield_hp", player.get("shield_hp", 0)) or 0))
    player["max_shield_hp"] = max(player["shield_hp"], int(actor.get("max_shield_hp", player.get("max_shield_hp", player["shield_hp"])) or player["shield_hp"]))
    if isinstance(actor.get("equipped_shield"), dict): player["equipped_shield"] = deepcopy(actor["equipped_shield"])
    if isinstance(actor.get("equipped_armor"), dict):
        player["equipped_armor"] = deepcopy(actor["equipped_armor"]); player["armor_set_name"] = actor.get("armor_set_name"); player["base_movement_without_armor"] = int(actor.get("base_movement_without_armor", player.get("base_movement_without_armor", 1)) or 1); sync_armor_summary(player)
    player["movement"] = int(actor.get("movement", player.get("movement", 1)) or 1); game_master.state.save()


def _apply_shield_then_armor(target: Dict, damage: int, *, damage_type: str | None = None) -> Dict:
    """Apply damage in the authoritative order: Shield HP -> Armor HP -> HP."""
    incoming = max(0, int(damage or 0))
    hp_before = int(target.get("hp", 0) or 0)
    shield_before = max(0, int(target.get("shield_hp", 0) or 0))
    max_shield = max(shield_before, int(target.get("max_shield_hp", shield_before) or shield_before))
    shield_absorbed = min(shield_before, incoming)
    target["shield_hp"] = shield_before - shield_absorbed
    remaining = incoming - shield_absorbed

    sync_armor_summary(target)
    armor_before = int(target.get("armor", 0) or 0)
    max_armor = int(target.get("max_armor", 0) or 0)
    armor_absorbed = 0; broken = []

    if remaining > 0 and max_armor > 0 and isinstance(target.get("equipped_armor"), dict):
        split = apply_damage_to_armor(target, remaining, damage_type=damage_type)
        armor_absorbed = int(split.get("armor_absorbed", 0) or 0)
        hp_damage = int(split.get("hp_damage", 0) or 0)
        broken = split.get("broken_pieces", []) or []
    else:
        hp_damage = remaining
        target["hp"] = max(0, hp_before - hp_damage)
        target["defeated"] = target["hp"] <= 0
        sync_armor_summary(target)

    return {
        "incoming_damage": incoming,
        "shield_absorbed": shield_absorbed,
        "shield_before": shield_before,
        "shield_after": int(target.get("shield_hp", 0) or 0),
        "max_shield": max_shield,
        "armor_absorbed": armor_absorbed,
        "armor_before": armor_before,
        "armor_after": int(target.get("armor", 0) or 0),
        "max_armor": int(target.get("max_armor", max_armor) or max_armor),
        "hp_damage": hp_damage,
        "hp_before": hp_before,
        "hp_after": int(target.get("hp", 0) or 0),
        "broken_pieces": broken,
    }


def _retrofit_armor_after_damage(combat: Dict, outcome: Dict, target_name: str, *, damage_type: str | None = None) -> Dict:
    if not isinstance(outcome, dict) or not outcome.get("hit"): return outcome
    damage = max(0, int(outcome.get("damage", 0) or 0))
    if damage <= 0: return outcome
    target = _player_actor(combat, target_name)
    if not target: return outcome
    has_shield = int(target.get("max_shield_hp", 0) or 0) > 0
    has_armor = isinstance(target.get("equipped_armor"), dict) and bool(target.get("equipped_armor"))
    if not has_shield and not has_armor: return outcome

    # The core resolver already removed the full damage from HP. Restore that damage,
    # then re-apply it through Shield -> Armor -> HP.
    after_engine = int(target.get("hp", 0) or 0); max_hp = int(target.get("max_hp", after_engine) or after_engine)
    target["hp"] = min(max_hp, after_engine + damage); target["defeated"] = False
    split = _apply_shield_then_armor(target, damage, damage_type=damage_type)
    _refresh_actor_armor_stats(target)
    base = int(target.get("base_movement_without_armor", target.get("movement", 1)) or 1); target["movement"] = effective_movement(base, target.get("equipped_armor", {}))
    outcome.update({
        "shield_absorbed": split["shield_absorbed"], "shield_before": split["shield_before"], "shield_after": split["shield_after"], "target_shield": split["shield_after"], "target_max_shield": split["max_shield"],
        "armor_absorbed": split["armor_absorbed"], "hp_damage": split["hp_damage"], "armor_before": split["armor_before"], "armor_after": split["armor_after"], "target_armor": split["armor_after"], "target_max_armor": split["max_armor"],
        "target_hp": split["hp_after"], "target_max_hp": int(target.get("max_hp", split["hp_after"])), "target_defeated": bool(target.get("defeated")), "broken_armor_pieces": split["broken_pieces"], "resisted_by_armor": 0,
    })
    _repair_combat_end_state(combat); return outcome


def install_armor_runtime(game_master) -> None:
    if getattr(game_master, "_armor_runtime_installed", False): return
    game_master._armor_runtime_installed = True; _install_character_creation_hook()
    original_start = game_master._start_combat
    def start_with_armor(request):
        combat = original_start(request); _inject_player_armor(game_master, combat); return combat
    game_master._start_combat = start_with_armor
    original_persist = game_master._persist_combat
    def persist_with_armor(combat): original_persist(combat); _sync_player_from_combat(game_master, combat)
    game_master._persist_combat = persist_with_armor

    import backend.ai.game_master as gm_module
    original_attack = gm_module.resolve_attack; original_ability = gm_module.resolve_ability
    original_prepared_damage = gm_module.resolve_prepared_damage_roll
    def attack_with_armor(combat, attacker_name, target_name, **kwargs):
        resources = _resource_snapshot(combat); was_active = bool(combat.get("active")); outcome = original_attack(combat, attacker_name, target_name, **kwargs); engine_ended = was_active and not combat.get("active"); outcome = _retrofit_armor_after_damage(combat, outcome, target_name)
        if engine_ended and combat.get("active"): _restore_resources(combat, resources)
        return outcome
    def ability_with_armor(combat, actor_name, ability_name, target_name=None, **kwargs):
        resources = _resource_snapshot(combat); was_active = bool(combat.get("active")); outcome = original_ability(combat, actor_name, ability_name, target_name, **kwargs); engine_ended = was_active and not combat.get("active"); outcome = _retrofit_armor_after_damage(combat, outcome, str(outcome.get("target") or target_name or actor_name))
        if engine_ended and combat.get("active"): _restore_resources(combat, resources, ability_actor=actor_name, ability_after=int(outcome.get("resource_after", resources.get(actor_name, (0,0))[0]) or 0))
        return outcome
    def prepared_damage_with_armor(combat, pending):
        target_name = str(pending.get("target") or "")
        resources = _resource_snapshot(combat); was_active = bool(combat.get("active"))
        outcome = original_prepared_damage(combat, pending)
        engine_ended = was_active and not combat.get("active")
        outcome = _retrofit_armor_after_damage(combat, outcome, target_name)
        if engine_ended and combat.get("active"): _restore_resources(combat, resources)
        return outcome
    gm_module.resolve_attack = attack_with_armor; gm_module.resolve_ability = ability_with_armor
    gm_module.resolve_prepared_damage_roll = prepared_damage_with_armor


def finish_character_creation_with_armor(game_master, created: Dict) -> Dict:
    player = game_master.state.data.setdefault("player", {}); inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    player["inventory"] = [item for item in inventory if not (isinstance(item, dict) and str(item.get("type") or "").strip().lower() == "armor")]
    for item in player["inventory"]:
        if isinstance(item, dict): item.pop("armor_bonus", None)
    run_starting_armor_creation(game_master)
    player["inventory"] = [item for item in player.get("inventory", []) if not (isinstance(item, dict) and str(item.get("type") or "").strip().lower() == "armor")]
    game_master.state.save(); created["player"] = deepcopy(game_master.state.data.get("player", {})); return created


def show_player_armor(game_master) -> None:
    player = game_master.state.data.get("player", {})
    if not isinstance(player.get("equipped_armor"), dict): print("\nYou do not have an equipped five-piece armor loadout yet."); return
    print_armor(player)
