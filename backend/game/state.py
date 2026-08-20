"""Authoritative persistent state for a Shattered Realms campaign."""
from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Dict, List

PROTOTYPE_POWER_STRIKE = {
    "name": "Power Strike",
    "description": "A committed melee strike used to test active ability rules.",
    "type": "active",
    "category": "offensive",
    "resource": "mana",
    "resource_cost": 1,
    "cooldown": 1,
    "target": "enemy",
    "range": 1,
    "requires_attack_roll": True,
    "attack_attribute": "strength",
    "damage": "1d8",
    "damage_bonus_attribute": "strength",
    "prototype": True,
}

DEFAULT_STATE = {
    "campaign": {"name": "Untitled Campaign", "genre": "fantasy", "day": 1, "time": "morning"},
    "player": {
        "name": "Traveler", "level": 1, "xp_orbs": 0, "class": "unassigned", "subclass": None,
        "background": None, "species": None, "inspiration": 0,
        "attribute_points_unspent": 60, "ability_points": 0,
        "stats": {
            "health": 0, "mana": 0, "strength": 0, "dexterity": 0, "constitution": 0,
            "intelligence": 0, "wisdom": 0, "charisma": 0, "speed": 0, "defense": 0,
        },
        "hp": 0, "max_hp": 0, "temporary_hp": 0, "mana": 0, "max_mana": 0,
        "armor_class": 10, "initiative_bonus": 0, "movement": 6,
        "saving_throw_proficiencies": [], "skill_proficiencies": [], "expertise": [],
        "skills": {"acrobatics": 0, "animal_handling": 0, "arcana": 0, "athletics": 0,
                   "deception": 0, "history": 0, "insight": 0, "intimidation": 0,
                   "investigation": 0, "medicine": 0, "nature": 0, "perception": 0,
                   "performance": 0, "persuasion": 0, "religion": 0,
                   "sleight_of_hand": 0, "stealth": 0, "survival": 0},
        "proficiencies": {"armor": [], "weapons": [], "tools": [], "languages": []},
        "death_saves": {"successes": 0, "failures": 0},
        "spellcasting": {"ability": None, "spell_save_dc": 0, "spell_attack_bonus": 0,
                         "cantrips": [], "spells_known": []},
        "unlocked_abilities": [deepcopy(PROTOTYPE_POWER_STRIKE)],
        "equipped_abilities": [deepcopy(PROTOTYPE_POWER_STRIKE)],
        "inventory": [], "equipment": {}, "currency": {"copper": 0, "silver": 0, "gold": 0},
        "features": [], "traits": [], "conditions": [], "location": "unknown",
    },
    "party": [], "npcs": {}, "factions": {}, "locations": {}, "quests": {}, "world_flags": {},
    "combat": {"active": False}, "encounter_template": {}, "encounter_reset_pending": False,
    "pending_encounter_enemies": [],
    "turn": 0,
}

class GameState:
    """Owns campaign truth. The AI proposes changes; this class persists them."""
    def __init__(self, initial: Dict | None = None, path: str | None = None) -> None:
        default_path = os.getenv("SHATTERED_REALMS_STATE_FILE", "data/campaign_state.json")
        self.path = Path(path or default_path)
        self.data = deepcopy(DEFAULT_STATE)
        saved = self._load()
        if saved: self._deep_merge(self.data, saved)
        if initial: self._deep_merge(self.data, deepcopy(initial))

    def _load(self) -> Dict:
        if not self.path.exists(): return {}
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            return loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError): return {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)

    def snapshot(self) -> Dict: return deepcopy(self.data)

    def _template_from_combat(self, combat: Dict) -> Dict:
        if not isinstance(combat, dict):
            return {}
        actors = []
        for raw_actor in combat.get("combatants", []):
            if not isinstance(raw_actor, dict):
                continue
            actor = deepcopy(raw_actor)
            max_hp = max(0, int(actor.get("max_hp", actor.get("hp", 0)) or 0))
            max_mana = max(0, int(actor.get("max_mana", actor.get("mana", 0)) or 0))
            actor["hp"] = max_hp
            actor["max_hp"] = max_hp
            actor["mana"] = max_mana
            actor["max_mana"] = max_mana
            actor["movement_used"] = 0
            actor["primary_action_used"] = False
            actor["defending"] = False
            actor["active_defense_ac_bonus"] = 0
            actor["ability_cooldowns"] = {}
            actor["defeated"] = False
            actors.append(actor)
        return {"combatants": actors, "grid": deepcopy(combat.get("grid", {}))}

    def apply_changes(self, changes: List[Dict]) -> None:
        if not isinstance(changes, list): changes = []
        for change in changes:
            if not isinstance(change, dict):
                continue

            change_type = str(change.get("type") or "").strip().lower()
            if change_type == "set_encounter_enemies":
                enemies = change.get("enemies")
                if isinstance(enemies, list):
                    self.data["pending_encounter_enemies"] = [
                        deepcopy(enemy) for enemy in enemies if isinstance(enemy, dict)
                    ]
                continue

            if change_type == "reset_combat_state":
                current_combat = self.data.get("combat")
                if isinstance(current_combat, dict) and current_combat.get("combatants"):
                    existing_template = self.data.get("encounter_template")
                    if not isinstance(existing_template, dict) or not existing_template.get("combatants"):
                        self.data["encounter_template"] = self._template_from_combat(current_combat)
                self.data["encounter_reset_pending"] = True
                self.data["combat"] = {"active": False}
                player = self.data.setdefault("player", {})
                player["combat_position"] = {"x": 0, "y": 0}
                max_hp = int(player.get("max_hp", 0) or 0)
                if max_hp > 0:
                    player["hp"] = max_hp
                max_mana = int(player.get("max_mana", 0) or 0)
                if max_mana > 0:
                    player["mana"] = max_mana
                player["temporary_hp"] = 0
                player["conditions"] = []
                continue

            if change_type == "restore_hp":
                target = str(change.get("target") or "").strip()
                player = self.data.setdefault("player", {})
                player_name = str(player.get("name") or "Traveler")
                if not target or target == player_name:
                    requested = change.get("hp")
                    if requested is None:
                        requested = player.get("max_hp", player.get("hp", 0))
                    player["hp"] = max(0, int(requested or 0))
                continue

            if change_type == "restore_mana":
                target = str(change.get("target") or "").strip()
                player = self.data.setdefault("player", {})
                player_name = str(player.get("name") or "Traveler")
                if not target or target == player_name:
                    requested = change.get("mana")
                    if requested is None:
                        requested = player.get("max_mana", player.get("mana", 0))
                    player["mana"] = max(0, int(requested or 0))
                continue

            path = change.get("path")
            if not isinstance(path, str) or not path.strip() or "value" not in change:
                continue
            self.set_path(path, change["value"], save=False)

        self.data["turn"] = int(self.data.get("turn", 0)) + 1
        self.save()

    def set_path(self, path: str, value, save: bool = True) -> None:
        keys = [key for key in path.split(".") if key]
        if not keys: return
        node = self.data
        for key in keys[:-1]:
            child = node.get(key)
            if not isinstance(child, dict): child = {}; node[key] = child
            node = child
        node[keys[-1]] = value
        if save: self.save()

    @classmethod
    def _deep_merge(cls, target: Dict, source: Dict) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict): cls._deep_merge(target[key], value)
            else: target[key] = deepcopy(value)
