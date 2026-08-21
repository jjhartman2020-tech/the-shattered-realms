"""Authoritative persistent state for a Shattered Realms campaign."""
from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Dict, List

from .attributes import (
    BASE_ARMOR_CLASS,
    character_sheet_channels,
    earned_attribute_points,
    normalize_attributes,
)
from .resources import max_resource_from_attribute, resource_key, resource_name_for_class

PROTOTYPE_POWER_STRIKE = {
    "name": "Power Strike",
    "description": "A committed melee strike used to test active ability rules.",
    "type": "active",
    "category": "offensive",
    "resource": "class",
    "resource_cost": 10,
    "target": "enemy",
    "range": 1,
    "requires_attack_roll": True,
    "attack_attribute": "strength",
    "damage": "1d8",
    "damage_bonus_attribute": "strength",
    "prototype": True,
}

DEFAULT_SKILLS = {
    "athletics": 0, "grappling": 0, "might": 0,
    "sleight_of_hand": 0, "lockpicking": 0, "pickpocketing": 0, "precision": 0,
    "acrobatics": 0, "stealth": 0, "evasion": 0,
    "endurance": 0, "fortitude": 0,
    "investigation": 0, "arcana": 0, "history": 0, "nature": 0, "engineering": 0,
    "perception": 0, "insight": 0, "survival": 0, "medicine": 0, "animal_handling": 0,
    "persuasion": 0, "deception": 0, "intimidation": 0, "performance": 0, "leadership": 0,
    "spellcasting": 0, "channeling": 0,
}

DEFAULT_STATE = {
    "campaign": {"name": "Untitled Campaign", "genre": "fantasy", "day": 1, "time": "morning"},
    "player": {
        "name": "Traveler", "level": 1, "xp_orbs": 0, "class": "unassigned", "subclass": None,
        "background": None, "species": None, "inspiration": 0,
        "attribute_points_unspent": 42, "ability_points": 0,
        "stats": {
            "health": 0, "resource": 0, "strength": 0, "dexterity": 0, "agility": 0,
            "constitution": 0, "intelligence": 0, "wisdom": 0, "charisma": 0,
            "speed": 0, "defense": 0, "luck": 0, "magic": 0,
        },
        "hp": 1, "max_hp": 1, "temporary_hp": 0,
        "resource_name": "Mana", "resource_type": "mana", "resource": 0, "max_resource": 0,
        "mana": 0, "max_mana": 0,
        "armor_class": 10, "initiative_bonus": 0, "movement": 6,
        "saving_throw_proficiencies": [], "skill_proficiencies": [], "expertise": [],
        "skills": deepcopy(DEFAULT_SKILLS),
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
        self._migrate_prototype_player()

    @staticmethod
    def _scaled_current(old_current: int, old_max: int, new_max: int) -> int:
        if new_max <= 0:
            return 0
        if old_max <= 0:
            return new_max
        ratio = max(0.0, min(1.0, float(old_current) / float(old_max)))
        return max(0, min(new_max, round(ratio * new_max)))

    def _migrate_prototype_player(self) -> None:
        """Bring legacy saves forward to the current stat/resource schema."""
        player = self.data.setdefault("player", {})
        raw_stats = player.setdefault("stats", {})

        # Old saves called the universal capacity stat ``mana``. Because DEFAULT_STATE
        # now contains Resource=0 before deep-merge, explicitly carry a meaningful
        # legacy Mana value forward when Resource has not yet been populated.
        legacy_mana_stat = int(raw_stats.get("mana", 0) or 0)
        if int(raw_stats.get("resource", 0) or 0) <= 0 and legacy_mana_stat > 0:
            raw_stats["resource"] = legacy_mana_stat
        stats = normalize_attributes(raw_stats)
        player["stats"] = stats

        level = max(1, int(player.get("level", 1) or 1))
        sheet = character_sheet_channels(stats, level)

        old_hp = int(player.get("hp", 0) or 0)
        old_max_hp = int(player.get("max_hp", 0) or 0)
        new_max_hp = int(sheet["max_health_base"])
        player["max_hp"] = new_max_hp
        player["hp"] = self._scaled_current(old_hp, old_max_hp, new_max_hp)

        resource_name = resource_name_for_class(player.get("class"))
        resource_type = resource_key(resource_name)
        new_max = max_resource_from_attribute(stats["resource"])
        old_current = int(player.get("resource", player.get("mana", 0)) or 0)
        old_max = int(player.get("max_resource", player.get("max_mana", 0)) or 0)
        new_current = self._scaled_current(old_current, old_max, new_max)

        player["resource_name"] = resource_name
        player["resource_type"] = resource_type
        player["resource"] = new_current
        player["max_resource"] = new_max
        player["resource_regeneration_per_round"] = int(sheet["resource_regeneration_per_round"])
        # Backward-compatible aliases while older systems are migrated.
        player["mana"] = new_current
        player["max_mana"] = new_max

        player["armor_class"] = BASE_ARMOR_CLASS + int(sheet["defense_bonus"])
        player["initiative_bonus"] = int(sheet["initiative_bonus"])
        player["movement"] = int(sheet["movement"])
        player["critical_chance_percent"] = int(sheet["critical_chance_percent"])
        player["physical_resistance_percent"] = int(sheet["physical_resistance_percent"])
        player["status_resistance_percent"] = int(sheet["status_resistance_percent"])
        player["defend_action_ac_bonus"] = int(sheet["defend_action_ac_bonus"])

        available = earned_attribute_points(level)
        spent = sum(stats.values())
        player["attribute_points_unspent"] = max(0, available - spent)

        skills = player.get("skills")
        if not isinstance(skills, dict):
            skills = {}
        migrated_skills = deepcopy(DEFAULT_SKILLS)
        for name in migrated_skills:
            if name in skills:
                migrated_skills[name] = int(skills.get(name, 0) or 0)
        # Useful legacy skill migrations where the meaning stayed equivalent.
        if "pickpocketing" not in skills and "sleight_of_hand" in skills:
            migrated_skills["pickpocketing"] = int(skills.get("sleight_of_hand", 0) or 0)
        player["skills"] = migrated_skills

        unlocked = player.get("unlocked_abilities")
        if not isinstance(unlocked, list):
            unlocked = []
            player["unlocked_abilities"] = unlocked
        equipped = player.get("equipped_abilities")
        if not isinstance(equipped, list):
            equipped = []
            player["equipped_abilities"] = equipped

        def normalize_power_strike(items: List[Dict]) -> None:
            found = False
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                if str(item.get("name") or "").strip().lower() == "power strike":
                    items[index] = deepcopy(PROTOTYPE_POWER_STRIKE)
                    found = True
            if not found:
                items.append(deepcopy(PROTOTYPE_POWER_STRIKE))

        normalize_power_strike(unlocked)
        normalize_power_strike(equipped)

        # Hot-sync an encounter already in progress so old combats do not keep stale
        # movement, initiative, crit, resistance, resource, or attribute data.
        combat = self.data.get("combat")
        if isinstance(combat, dict) and combat.get("active"):
            player_name = str(player.get("name") or "Traveler")
            for actor in combat.get("combatants", []):
                if not isinstance(actor, dict) or actor.get("name") != player_name:
                    continue
                actor_old_hp = int(actor.get("hp", old_hp) or 0)
                actor_old_max_hp = int(actor.get("max_hp", old_max_hp) or 0)
                actor_old_current = int(actor.get("resource", actor.get("mana", old_current)) or 0)
                actor_old_max = int(actor.get("max_resource", actor.get("max_mana", old_max)) or 0)
                actor_current = self._scaled_current(actor_old_current, actor_old_max, new_max)
                actor["attributes"] = deepcopy(stats)
                actor["attribute_channels"] = deepcopy(sheet)
                actor["hp"] = self._scaled_current(actor_old_hp, actor_old_max_hp, new_max_hp)
                actor["max_hp"] = new_max_hp
                actor["abilities"] = deepcopy(equipped)
                actor["resource_name"] = resource_name
                actor["resource_type"] = resource_type
                actor["resource"] = actor_current
                actor["max_resource"] = new_max
                actor["resource_regeneration_per_round"] = int(sheet["resource_regeneration_per_round"])
                actor["mana"] = actor_current
                actor["max_mana"] = new_max
                actor["armor_class"] = player["armor_class"]
                actor["initiative_bonus"] = player["initiative_bonus"]
                actor["movement"] = player["movement"]
                actor["critical_chance_percent"] = player["critical_chance_percent"]
                actor["physical_resistance_percent"] = player["physical_resistance_percent"]
                actor["status_resistance_percent"] = player["status_resistance_percent"]
                actor["defend_action_ac_bonus"] = player["defend_action_ac_bonus"]
                actor.pop("ability_cooldowns", None)
                break

        self.save()

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
            max_resource = max(0, int(actor.get("max_resource", actor.get("max_mana", 0)) or 0))
            actor["hp"] = max_hp
            actor["max_hp"] = max_hp
            actor["resource"] = max_resource
            actor["max_resource"] = max_resource
            actor["mana"] = max_resource
            actor["max_mana"] = max_resource
            actor["movement_used"] = 0
            actor["primary_action_used"] = False
            actor["defending"] = False
            actor["active_defense_ac_bonus"] = 0
            actor.pop("ability_cooldowns", None)
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
                max_resource = int(player.get("max_resource", player.get("max_mana", 0)) or 0)
                if max_resource > 0:
                    player["resource"] = max_resource
                    player["mana"] = max_resource
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

            if change_type in {"restore_mana", "restore_resource"}:
                target = str(change.get("target") or "").strip()
                player = self.data.setdefault("player", {})
                player_name = str(player.get("name") or "Traveler")
                if not target or target == player_name:
                    requested = change.get("resource", change.get("mana"))
                    if requested is None:
                        requested = player.get("max_resource", player.get("max_mana", 0))
                    value = max(0, int(requested or 0))
                    player["resource"] = value
                    player["mana"] = value
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
