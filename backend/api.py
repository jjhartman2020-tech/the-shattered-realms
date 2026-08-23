"""Local JSON API used by the Godot client.

Run with:
    python -m backend.api

The Python backend stays authoritative. Godot only sends player choices/actions
and renders the returned state/result.
"""
from __future__ import annotations

from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
from typing import Any, Dict, List

import backend.game.character_creation as character_creation
from backend.ai.game_master import GameMaster
from backend.game.armor import effective_movement, generate_starting_armor, sync_armor_summary
from backend.game.armor_runtime import install_armor_runtime
from backend.game.ai_stat_builder import generate_ai_allocation
from backend.game.attributes import (
    ATTRIBUTE_NAMES,
    BASE_ARMOR_CLASS,
    STARTING_SKILL_POINTS,
    character_sheet_channels,
    normalize_attributes,
    validate_allocation,
)
from backend.game.abilities import resolve_ability
from backend.game.combat import current_actor, defend_actor, end_turn, move_actor, resolve_attack
from backend.game.dice import normalize_damage_expression
from backend.game.economy import currency_profile, ensure_wallet, format_money
from backend.game.progression import xp_required_for_next_level
from backend.game.resources import resource_key
from backend.game.world_character_generation import install_world_aware_character_generation
from backend.game.world_creation import generate_world
from backend.game.world_exploration import generate_world_area

HOST = os.getenv("SHATTERED_REALMS_API_HOST", "127.0.0.1")
PORT = int(os.getenv("SHATTERED_REALMS_API_PORT", "8765"))

GAME_MASTER = GameMaster()
install_armor_runtime(GAME_MASTER)
LOCK = threading.RLock()

# The creator is a short-lived local wizard. Confirmed world/player state is still
# stored in GameState; only generated previews/selections live here temporarily.
CREATION_SESSION: Dict[str, Any] = {
    "world": None,
    "identity": None,
    "package": None,
    "armor_options": [],
}


def _clear_creation_session() -> None:
    CREATION_SESSION.update({"world": None, "identity": None, "package": None, "armor_options": []})


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return json.loads(json.dumps(value, default=str))


def _resume_text(state: Dict) -> str:
    player = state.get("player", {}) if isinstance(state.get("player"), dict) else {}
    if not player.get("character_creation_complete"):
        return "No completed character is saved yet. Start a new game to open the creator."

    name = str(player.get("name") or "Traveler")
    location = str(player.get("location") or "Unknown location")
    combat = state.get("combat") if isinstance(state.get("combat"), dict) else {}
    if combat.get("active"):
        actor = current_actor(combat)
        turn_text = str(actor.get("name")) if isinstance(actor, dict) else "unknown"
        return f"{name} resumes an active fight at {location}. Current turn: {turn_text}."

    objective = "Continue your current lead."
    quests = state.get("quests") if isinstance(state.get("quests"), dict) else {}
    for quest in quests.values():
        if not isinstance(quest, dict):
            continue
        status = str(quest.get("status") or "active").lower()
        if status in {"complete", "completed", "failed", "inactive"}:
            continue
        objective = str(quest.get("objective") or quest.get("name") or objective)
        break
    return f"{name} resumes at {location}. Current objective: {objective}"


def _session_payload() -> Dict:
    state = GAME_MASTER.state.snapshot()
    player = state.get("player", {}) if isinstance(state.get("player"), dict) else {}
    if player.get("character_creation_complete"):
        wallet = ensure_wallet(GAME_MASTER, grant_starting_funds=True)
        state = GAME_MASTER.state.snapshot()
        money = format_money(wallet.get("amount", 0), wallet)
    else:
        money = "0"
    return {
        "ok": True,
        "narration": _resume_text(state),
        "suggested_actions": [],
        "state": state,
        "money_text": money,
        "creation_required": not bool(player.get("character_creation_complete")),
    }


def _new_game_payload() -> Dict:
    """Reset all campaign state/memory from a deliberate UI new-game action."""
    GAME_MASTER.state.reset_for_new_campaign()
    GAME_MASTER.memory.clear()
    _clear_creation_session()
    state = GAME_MASTER.state.snapshot()
    return {
        "ok": True,
        "narration": "New campaign created. Build your world and character to begin.",
        "suggested_actions": [],
        "state": state,
        "money_text": "0",
        "new_game": True,
        "creation_required": True,
        "creation_step": "world",
    }


def _generate_world_payload(payload: Dict) -> Dict:
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt:
        return {"ok": False, "error": "Describe the world and adventure you want first."}
    world = generate_world(GAME_MASTER.provider, prompt)
    CREATION_SESSION["world"] = deepcopy(world)
    return {"ok": True, "world": world}


def _confirm_world_payload() -> Dict:
    world = CREATION_SESSION.get("world")
    if not isinstance(world, dict) or not world:
        return {"ok": False, "error": "Generate a world before confirming it."}

    GAME_MASTER.state.data["world_profile"] = deepcopy(world)
    GAME_MASTER.state.data["world_creation_complete"] = True
    campaign = GAME_MASTER.state.data.setdefault("campaign", {})
    campaign["name"] = str(world.get("name") or "Untitled Campaign")
    campaign["genre"] = str(world.get("genre") or "custom")
    GAME_MASTER.state.save()
    install_world_aware_character_generation(GAME_MASTER, world)
    return {"ok": True, "state": GAME_MASTER.state.snapshot(), "world": deepcopy(world)}


def _generate_stats_payload(payload: Dict) -> Dict:
    if not GAME_MASTER.state.data.get("world_creation_complete"):
        return {"ok": False, "error": "Confirm the world before building character stats."}

    description = str(payload.get("description") or "").strip()
    if not description:
        return {"ok": False, "error": "Describe the character build you want first."}

    world = GAME_MASTER.state.data.get("world_profile", {})
    allocation = generate_ai_allocation(GAME_MASTER.provider, description, world)
    validation = validate_allocation(allocation, level=1)
    if not validation.get("valid") or int(validation.get("skill_points_unspent", 0)) != 0:
        return {"ok": False, "error": f"The AI build must spend exactly {STARTING_SKILL_POINTS} SP."}
    return {"ok": True, "stats": allocation, "points_spent": STARTING_SKILL_POINTS}


def _generate_character_payload(payload: Dict) -> Dict:
    if not GAME_MASTER.state.data.get("world_creation_complete"):
        return {"ok": False, "error": "Confirm the world before creating the character."}

    name = str(payload.get("name") or "").strip() or "Traveler"
    appearance = str(payload.get("appearance") or "").strip()
    raw_stats = payload.get("stats") if isinstance(payload.get("stats"), dict) else {}
    stats = normalize_attributes(raw_stats)
    validation = validate_allocation(stats, level=1)
    if not validation.get("valid") or int(validation.get("skill_points_unspent", 0)) != 0:
        spent = int(validation.get("points_spent", 0))
        return {
            "ok": False,
            "error": f"Spend exactly {STARTING_SKILL_POINTS} SP before continuing. You currently spent {spent}.",
        }

    package = character_creation.generate_character_package(
        GAME_MASTER.provider, name=name, appearance=appearance, stats=stats
    )
    sheet = character_sheet_channels(stats, level=1)
    CREATION_SESSION["identity"] = {"name": name, "appearance": appearance, "stats": deepcopy(stats)}
    CREATION_SESSION["package"] = deepcopy(package)
    CREATION_SESSION["armor_options"] = []
    return {
        "ok": True,
        "package": package,
        "derived": {
            "max_hp": int(sheet["max_health_base"]),
            "max_resource": int(sheet["max_resource_base"]),
            "resource_regen": int(sheet["resource_regeneration_per_round"]),
            "movement": int(sheet["movement"]),
            "initiative_bonus": int(sheet["initiative_bonus"]),
            "critical_chance_percent": int(sheet["critical_chance_percent"]),
        },
        "currency": currency_profile(GAME_MASTER.state.data.get("world_profile", {})),
    }


def _generate_armor_payload(payload: Dict) -> Dict:
    identity = CREATION_SESSION.get("identity")
    package = CREATION_SESSION.get("package")
    if not isinstance(identity, dict) or not isinstance(package, dict):
        return {"ok": False, "error": "Generate the character package before choosing armor."}

    world = GAME_MASTER.state.data.get("world_profile", {})
    preview_player = {
        "name": identity.get("name"),
        "appearance": identity.get("appearance"),
        "stats": identity.get("stats"),
        "class": package.get("class_name"),
    }
    custom_request = str(payload.get("custom_request") or "").strip()
    custom = bool(custom_request)
    options = generate_starting_armor(
        GAME_MASTER.provider,
        world,
        preview_player,
        request=custom_request,
        custom=custom,
    )
    CREATION_SESSION["armor_options"] = deepcopy(options)
    return {"ok": True, "armor_options": options, "custom": custom}


def _indexes(raw: Any) -> List[int]:
    if not isinstance(raw, list):
        return []
    result: List[int] = []
    for value in raw:
        try:
            result.append(int(value))
        except (TypeError, ValueError):
            return []
    return result


def _finalize_character_payload(payload: Dict) -> Dict:
    identity = CREATION_SESSION.get("identity")
    package = CREATION_SESSION.get("package")
    armor_options = CREATION_SESSION.get("armor_options")
    if not isinstance(identity, dict) or not isinstance(package, dict):
        return {"ok": False, "error": "Character generation has not been completed."}
    if not isinstance(armor_options, list) or not armor_options:
        return {"ok": False, "error": "Choose starting armor before finishing the character."}

    ability_indexes = _indexes(payload.get("ability_indexes"))
    equipment_indexes = _indexes(payload.get("equipment_indexes"))
    try:
        kit_index = int(payload.get("kit_index", -1))
        armor_index = int(payload.get("armor_index", -1))
    except (TypeError, ValueError):
        return {"ok": False, "error": "Invalid character-creation selection."}

    abilities = package.get("abilities", []) if isinstance(package.get("abilities"), list) else []
    kits = package.get("starter_kits", []) if isinstance(package.get("starter_kits"), list) else []
    equipment = package.get("special_equipment", []) if isinstance(package.get("special_equipment"), list) else []
    if len(ability_indexes) != 2 or len(set(ability_indexes)) != 2 or not all(0 <= i < len(abilities) for i in ability_indexes):
        return {"ok": False, "error": "Choose exactly 2 different Beginner abilities."}
    if not 0 <= kit_index < len(kits):
        return {"ok": False, "error": "Choose 1 starter kit."}
    if len(equipment_indexes) != 2 or len(set(equipment_indexes)) != 2 or not all(0 <= i < len(equipment) for i in equipment_indexes):
        return {"ok": False, "error": "Choose exactly 2 different special equipment items."}
    if not 0 <= armor_index < len(armor_options):
        return {"ok": False, "error": "Choose 1 starting armor set."}

    name = str(identity.get("name") or "Traveler")
    appearance = str(identity.get("appearance") or "")
    stats = normalize_attributes(identity.get("stats", {}))
    sheet = character_sheet_channels(stats, level=1)
    resource_name = str(package.get("resource_name") or "Resource").strip() or "Resource"
    chosen_abilities = [deepcopy(abilities[i]) for i in ability_indexes]
    chosen_kit = deepcopy(kits[kit_index])
    chosen_equipment = [deepcopy(equipment[i]) for i in equipment_indexes]
    kit_items = deepcopy(chosen_kit.get("items", [])) if isinstance(chosen_kit.get("items"), list) else []
    all_items = kit_items + deepcopy(chosen_equipment)

    starter_weapon = next(
        (item for item in all_items if isinstance(item, dict) and str(item.get("type") or "").lower() == "weapon"),
        None,
    )
    starter_shield = next(
        (item for item in all_items if isinstance(item, dict) and str(item.get("type") or "").lower() == "shield"),
        None,
    )
    starter_shield_hp = int(starter_shield.get("shield", 0) or 0) if starter_shield else 0
    starting_money = max(10, min(30, int(chosen_kit.get("starting_currency", 20) or 20)))
    money_profile = currency_profile(GAME_MASTER.state.data.get("world_profile", {}))

    player = GAME_MASTER.state.data.setdefault("player", {})
    player.update({
        "name": name,
        "appearance": appearance,
        "level": 1,
        "xp_orbs": 0,
        "xp_to_next_level": xp_required_for_next_level(1),
        "class": str(package.get("class_name") or "Unassigned"),
        "background": str(package.get("backstory") or ""),
        "stats": stats,
        "skill_points_unspent": 0,
        "attribute_points_unspent": 0,
        "ability_points": 0,
        "hp": int(sheet["max_health_base"]),
        "max_hp": int(sheet["max_health_base"]),
        "resource_name": resource_name,
        "resource_type": resource_key(resource_name),
        "resource": int(sheet["max_resource_base"]),
        "max_resource": int(sheet["max_resource_base"]),
        "resource_regeneration_per_round": int(sheet["resource_regeneration_per_round"]),
        "mana": int(sheet["max_resource_base"]),
        "max_mana": int(sheet["max_resource_base"]),
        "armor_class": BASE_ARMOR_CLASS + int(sheet["defense_bonus"]),
        "initiative_bonus": int(sheet["initiative_bonus"]),
        "movement": int(sheet["movement"]),
        "critical_chance_percent": int(sheet["critical_chance_percent"]),
        "physical_resistance_percent": int(sheet["physical_resistance_percent"]),
        "status_resistance_percent": int(sheet["status_resistance_percent"]),
        "defend_action_ac_bonus": int(sheet["defend_action_ac_bonus"]),
        "unlocked_abilities": deepcopy(chosen_abilities),
        "equipped_abilities": deepcopy(chosen_abilities),
        "starter_kit": deepcopy(chosen_kit),
        "inventory": all_items,
        "special_starting_equipment": deepcopy(chosen_equipment),
        "equipped_weapon": deepcopy(starter_weapon),
        "equipped_shield": deepcopy(starter_shield),
        "shield_hp": starter_shield_hp,
        "max_shield_hp": starter_shield_hp,
        "damage": normalize_damage_expression(starter_weapon.get("damage", "1d4"), "1d4") if starter_weapon else "1d4",
        "wallet": {"amount": starting_money, **money_profile},
        "character_creation_complete": True,
    })

    chosen_armor = deepcopy(armor_options[armor_index])
    pieces = chosen_armor.get("pieces", []) if isinstance(chosen_armor.get("pieces"), list) else []
    equipped_armor = {
        str(piece.get("slot")): deepcopy(piece)
        for piece in pieces
        if isinstance(piece, dict) and str(piece.get("slot") or "")
    }
    player["equipped_armor"] = equipped_armor
    player["armor_set_name"] = chosen_armor.get("name")
    sync_armor_summary(player)
    player["base_movement_without_armor"] = int(sheet["movement"])
    player["movement"] = effective_movement(int(sheet["movement"]), equipped_armor)
    player.setdefault("inventory", []).extend(deepcopy(pieces))

    GAME_MASTER.state.data.update({
        "combat": {"active": False},
        "encounter_template": {},
        "pending_encounter_enemies": [],
        "encounter_reset_pending": False,
        "campaign_status": "active",
    })
    GAME_MASTER.state.save()

    opening = GAME_MASTER.provider.respond({
        "player_action": "Begin the adventure with an opening scene for this newly completed character.",
        "game_state": GAME_MASTER.state.snapshot(),
        "relevant_memories": [],
        "relevant_rules": [],
    })
    narration = str(opening.get("narration") or "Your adventure begins.")
    suggested = opening.get("suggested_actions", []) if isinstance(opening, dict) else []
    state = GAME_MASTER.state.snapshot()
    _clear_creation_session()
    return {
        "ok": True,
        "narration": narration,
        "suggested_actions": suggested,
        "state": state,
        "player": deepcopy(player),
        "starting_money": format_money(starting_money, money_profile),
        "character_creation_complete": True,
    }


def _direct_end_turn() -> Dict | None:
    combat = GAME_MASTER.state.data.get("combat")
    if not isinstance(combat, dict) or not combat.get("active"):
        return None
    player = GAME_MASTER.state.data.get("player", {})
    player_name = str(player.get("name") or "Traveler")
    actor = current_actor(combat)
    if not actor or actor.get("name") != player_name:
        return {
            "narration": "It is not your turn right now.",
            "suggested_actions": [],
            "combat": combat,
            "combat_results": [],
            "state": GAME_MASTER.state.snapshot(),
        }
    events = [{"type": "player_end_turn", "actor": player_name}]
    end_turn(combat)
    events.extend(GAME_MASTER._run_enemy_turns(combat))
    GAME_MASTER._persist_combat(combat)
    return {
        "narration": "You end your turn. The battle advances.",
        "suggested_actions": [],
        "combat": combat,
        "combat_results": events,
        "state": GAME_MASTER.state.snapshot(),
    }


def _combat_response(narration: str, events: List[Dict], combat: Dict) -> Dict:
    GAME_MASTER._persist_combat(combat)
    return {
        "ok": True,
        "narration": narration,
        "suggested_actions": [],
        "combat": deepcopy(combat),
        "combat_results": events,
        "state": GAME_MASTER.state.snapshot(),
    }


def _player_combat_context() -> tuple[Dict, Dict, str]:
    combat = GAME_MASTER.state.data.get("combat")
    if not isinstance(combat, dict) or not combat.get("active"):
        raise ValueError("No tactical battle is active.")
    player = GAME_MASTER.state.data.get("player")
    if not isinstance(player, dict):
        raise ValueError("No player character is available.")
    player_name = str(player.get("name") or "Traveler")
    actor = current_actor(combat)
    if not actor or str(actor.get("name")) != player_name:
        raise ValueError("Wait for the enemy turn to finish.")
    return combat, player, player_name


def _prototype_start_battle() -> Dict:
    player = GAME_MASTER.state.data.get("player")
    if not isinstance(player, dict) or not player.get("character_creation_complete"):
        return {"ok": False, "error": "Finish character creation before entering the tactical arena."}
    existing = GAME_MASTER.state.data.get("combat")
    if isinstance(existing, dict) and existing.get("active"):
        return _combat_response("The current battle continues.", [], existing)

    GAME_MASTER.state.set_path("player.combat_position", {"x": 2, "y": 4}, save=False)
    combat = GAME_MASTER._start_combat({
        "enemies": [{
            "name": "Practice Sentinel",
            "role": "training opponent",
            "level": 1,
            "hp": 12,
            "armor_class": 10,
            "damage": "1d4",
            "attack_range": 1,
            "position": {"x": 8, "y": 4},
            "attributes": {"health": 2, "strength": 3, "agility": 2, "speed": 2, "defense": 1},
        }]
    })
    events = [{"type": "combat_start", "order": combat.get("order", []), "initiative": combat.get("initiative", [])}]
    events.extend(GAME_MASTER._run_enemy_turns(combat))
    return _combat_response("The world expands into a tactical arena. Move by squares, choose a target, and use your abilities.", events, combat)


def _direct_combat_action(payload: Dict, action_type: str) -> Dict:
    try:
        combat, player, player_name = _player_combat_context()
        events: List[Dict] = []

        if action_type == "move":
            event = move_actor(combat, player_name, int(payload.get("x")), int(payload.get("y")), enforce_turn=True)
            events.append({"type": "player_move", **event})
            narration = f"{player_name} moves {event.get('distance', 0)} squares."

        elif action_type == "attack":
            target = str(payload.get("target") or "").strip()
            if not target:
                raise ValueError("Choose an enemy target.")
            weapon = player.get("equipped_weapon") if isinstance(player.get("equipped_weapon"), dict) else {}
            attack_attribute = str(weapon.get("attack_attribute") or "strength").lower()
            if attack_attribute not in {"strength", "dexterity", "magic"}:
                attack_attribute = "strength"
            event = resolve_attack(
                combat,
                player_name,
                target,
                attack_attribute=attack_attribute,
                attack_range=int(weapon.get("range", 1) or 1),
                damage_expression=str(weapon.get("damage") or player.get("damage") or "1d4"),
                enforce_turn=True,
            )
            events.append({"type": "player_attack", **event})
            narration = f"{player_name} attacks {target}."
            if combat.get("active"):
                events.append({"type": "player_end_turn", "actor": player_name, "automatic": True})
                end_turn(combat)
                events.extend(GAME_MASTER._run_enemy_turns(combat))

        elif action_type == "ability":
            ability_name = str(payload.get("ability") or "").strip()
            if not ability_name:
                raise ValueError("Choose an ability.")
            target = str(payload.get("target") or "").strip() or None
            event = resolve_ability(combat, player_name, ability_name, target, enforce_turn=True)
            events.append({"type": "player_ability", **event})
            narration = f"{player_name} uses {ability_name}."

        elif action_type == "defend":
            event = defend_actor(combat, player_name, enforce_turn=True)
            events.append({"type": "player_defend", **event})
            narration = f"{player_name} takes a defensive stance."

        elif action_type == "end_turn":
            direct = _direct_end_turn()
            if direct is None:
                raise ValueError("No tactical battle is active.")
            direct["ok"] = True
            return direct

        else:
            raise ValueError("Unknown tactical action.")

        if not combat.get("active"):
            winner = str(combat.get("winner") or "")
            narration += " The battle is over." if winner else ""
        return _combat_response(narration, events, combat)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}



def _world_area_payload(payload: Dict) -> Dict:
    world = GAME_MASTER.state.data.get("world_profile")
    if not isinstance(world, dict) or not world:
        return {"ok": False, "error": "Create and confirm a world before exploring it."}
    player = GAME_MASTER.state.data.get("player")
    if not isinstance(player, dict) or not player.get("character_creation_complete"):
        return {"ok": False, "error": "Finish character creation before exploring the world."}

    direction = str(payload.get("direction") or "current").lower().strip()
    deltas = {
        "current": (0, 0),
        "north": (0, -1),
        "south": (0, 1),
        "west": (-1, 0),
        "east": (1, 0),
    }
    if direction not in deltas:
        return {"ok": False, "error": "Unknown exploration direction."}

    exploration = GAME_MASTER.state.data.setdefault("exploration", {})
    if not isinstance(exploration, dict):
        exploration = {}
        GAME_MASTER.state.data["exploration"] = exploration
    areas = exploration.setdefault("areas", {})
    if not isinstance(areas, dict):
        areas = {}
        exploration["areas"] = areas

    current_x = int(exploration.get("current_x", 0) or 0)
    current_y = int(exploration.get("current_y", 0) or 0)
    delta_x, delta_y = deltas[direction]
    target_x = current_x + delta_x
    target_y = current_y + delta_y
    target_key = f"{target_x},{target_y}"
    current_key = f"{current_x},{current_y}"
    previous_area = areas.get(current_key) if isinstance(areas.get(current_key), dict) else {}

    area = areas.get(target_key)
    generated = False
    if not isinstance(area, dict):
        area = generate_world_area(
            GAME_MASTER.provider,
            deepcopy(world),
            target_x,
            target_y,
            direction,
            deepcopy(previous_area),
        )
        areas[target_key] = deepcopy(area)
        generated = True

    exploration["current_x"] = target_x
    exploration["current_y"] = target_y
    exploration["current_area"] = deepcopy(area)
    exploration["last_entry_direction"] = direction
    GAME_MASTER.state.data["current_location"] = str(area.get("name") or "Unknown Area")
    GAME_MASTER.state.save()

    actions = area.get("suggested_actions") if isinstance(area.get("suggested_actions"), list) else []
    suggested = [{"text": str(text), "requires_roll": False, "skill": None} for text in actions[:3]]
    return {
        "ok": True,
        "area": deepcopy(area),
        "generated": generated,
        "entry_direction": direction,
        "narration": str(area.get("arrival_text") or f"You enter {area.get('name', 'a new area')}."),
        "suggested_actions": suggested,
        "state": GAME_MASTER.state.snapshot(),
    }

def _handle_action(action: str) -> Dict:
    clean = str(action or "").strip()
    if not clean:
        return {"ok": False, "error": "Action cannot be empty."}
    lowered = clean.lower()
    if lowered in {"end turn", "end my turn", "pass turn", "pass my turn"}:
        direct = _direct_end_turn()
        if direct is not None:
            direct["ok"] = True
            return direct
    result = GAME_MASTER.handle_action(clean)
    result["ok"] = True
    return _json_safe(result)


class Handler(BaseHTTPRequestHandler):
    server_version = "ShatteredRealmsAPI/0.3"

    def _send(self, status: int, payload: Dict) -> None:
        body = json.dumps(_json_safe(payload), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length > 0 else b"{}"
        parsed = json.loads(raw.decode("utf-8") or "{}")
        return parsed if isinstance(parsed, dict) else {}

    def do_GET(self) -> None:  # noqa: N802
        try:
            with LOCK:
                if self.path == "/health":
                    self._send(200, {"ok": True, "service": "the-shattered-realms"})
                    return
                if self.path in {"/", "/session", "/state"}:
                    self._send(200, _session_payload())
                    return
            self._send(404, {"ok": False, "error": "Not found."})
        except Exception as exc:  # pragma: no cover - user-facing dev server guard
            self._send(500, {"ok": False, "error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._read_json()
            with LOCK:
                if self.path == "/action":
                    result = _handle_action(str(payload.get("action") or ""))
                elif self.path == "/world/area/generate":
                    result = _world_area_payload(payload)
                elif self.path == "/prototype/battle/start":
                    result = _prototype_start_battle()
                elif self.path == "/combat/move":
                    result = _direct_combat_action(payload, "move")
                elif self.path == "/combat/attack":
                    result = _direct_combat_action(payload, "attack")
                elif self.path == "/combat/ability":
                    result = _direct_combat_action(payload, "ability")
                elif self.path == "/combat/defend":
                    result = _direct_combat_action(payload, "defend")
                elif self.path == "/combat/end_turn":
                    result = _direct_combat_action(payload, "end_turn")
                elif self.path == "/new_game":
                    result = _new_game_payload()
                elif self.path == "/creation/world/generate":
                    result = _generate_world_payload(payload)
                elif self.path == "/creation/world/confirm":
                    result = _confirm_world_payload()
                elif self.path == "/creation/stats/generate":
                    result = _generate_stats_payload(payload)
                elif self.path == "/creation/character/generate":
                    result = _generate_character_payload(payload)
                elif self.path == "/creation/armor/generate":
                    result = _generate_armor_payload(payload)
                elif self.path == "/creation/finalize":
                    result = _finalize_character_payload(payload)
                else:
                    self._send(404, {"ok": False, "error": "Not found."})
                    return
            self._send(200 if result.get("ok") else 400, result)
        except json.JSONDecodeError:
            self._send(400, {"ok": False, "error": "Invalid JSON body."})
        except Exception as exc:  # pragma: no cover - user-facing dev server guard
            self._send(500, {"ok": False, "error": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[Godot API] {self.address_string()} - {fmt % args}")


def main() -> None:
    print("=" * 52)
    print("THE SHATTERED REALMS — GODOT BACKEND API")
    print("=" * 52)
    print(f"Listening on http://{HOST}:{PORT}")
    print("Leave this running while the Godot client is open.\n")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

