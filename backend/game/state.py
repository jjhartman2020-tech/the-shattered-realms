"""Authoritative persistent state for a Shattered Realms campaign."""
from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Dict, List

from .attributes import BASE_ARMOR_CLASS, character_sheet_channels, earned_skill_points, normalize_attributes
from .progression import apply_xp_orbs, total_ability_points_earned, xp_required_for_next_level
from .resources import resource_key, resource_name_for_class

PROTOTYPE_POWER_STRIKE = {
    "name": "Power Strike", "description": "A committed melee strike used to test active ability rules.",
    "type": "active", "category": "offensive", "resource": "class", "resource_cost": 10,
    "target": "enemy", "range": 1, "requires_attack_roll": True, "attack_attribute": "strength",
    "damage": "1d8", "damage_bonus_attribute": "strength", "prototype": True,
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
    "campaign": {"name": "Untitled Campaign", "genre": "custom", "day": 1, "time": "morning"},
    "campaign_status": "no_character",
    "world_creation_complete": False,
    "world_profile": {},
    "player": {
        "name": "Traveler", "level": 1, "xp_orbs": 0, "xp_to_next_level": 5,
        "class": "unassigned", "subclass": None, "background": None, "appearance": None,
        "species": None, "inspiration": 0, "character_creation_complete": False,
        "skill_points_unspent": 42, "attribute_points_unspent": 42, "ability_points": 0,
        "stats": {"health": 0, "resource": 0, "strength": 0, "dexterity": 0, "agility": 0,
                  "constitution": 0, "intelligence": 0, "wisdom": 0, "charisma": 0,
                  "speed": 0, "defense": 0, "luck": 0, "magic": 0},
        "hp": 1, "max_hp": 1, "temporary_hp": 0,
        "resource_name": "Resource", "resource_type": "resource", "resource": 0, "max_resource": 0,
        "mana": 0, "max_mana": 0, "armor_class": 10, "initiative_bonus": 0, "movement": 6,
        "skills": deepcopy(DEFAULT_SKILLS), "unlocked_abilities": [deepcopy(PROTOTYPE_POWER_STRIKE)],
        "equipped_abilities": [deepcopy(PROTOTYPE_POWER_STRIKE)], "inventory": [], "equipment": {},
        "currency": {"copper": 0, "silver": 0, "gold": 0}, "features": [], "traits": [],
        "conditions": [], "location": "unknown",
    },
    "party": [], "npcs": {}, "factions": {}, "locations": {}, "quests": {}, "world_flags": {},
    "combat": {"active": False}, "encounter_template": {}, "encounter_reset_pending": False,
    "pending_encounter_enemies": [], "turn": 0,
}


class GameState:
    def __init__(self, initial: Dict | None = None, path: str | None = None) -> None:
        default_path = os.getenv("SHATTERED_REALMS_STATE_FILE", "data/campaign_state.json")
        self.path = Path(path or default_path)
        self.data = deepcopy(DEFAULT_STATE)
        saved = self._load()
        if saved: self._deep_merge(self.data, saved)
        if initial: self._deep_merge(self.data, deepcopy(initial))
        self._migrate_player()

    def reset_for_new_campaign(self) -> None:
        self.data = deepcopy(DEFAULT_STATE)
        self.save()

    @staticmethod
    def _scaled_current(old_current: int, old_max: int, new_max: int) -> int:
        if new_max <= 0: return 0
        if old_max <= 0: return new_max
        ratio = max(0.0, min(1.0, float(old_current) / float(old_max)))
        return max(0, min(new_max, round(ratio * new_max)))

    def _migrate_player(self) -> None:
        player = self.data.setdefault("player", {})
        raw_stats = player.setdefault("stats", {})
        legacy_mana_stat = int(raw_stats.get("mana", 0) or 0)
        if int(raw_stats.get("resource", 0) or 0) <= 0 and legacy_mana_stat > 0: raw_stats["resource"] = legacy_mana_stat
        stats = normalize_attributes(raw_stats); player["stats"] = stats
        level = max(1, min(100, int(player.get("level", 1) or 1))); player["level"] = level
        sheet = character_sheet_channels(stats, level)
        old_hp = int(player.get("hp", 0) or 0); old_max_hp = int(player.get("max_hp", 0) or 0); new_max_hp = int(sheet["max_health_base"])
        player["max_hp"] = new_max_hp; player["hp"] = self._scaled_current(old_hp, old_max_hp, new_max_hp)
        completed = bool(player.get("character_creation_complete"))
        if completed and str(player.get("resource_name") or "").strip(): resource_name = str(player.get("resource_name")).strip()
        else: resource_name = resource_name_for_class(player.get("class"))
        resource_type = resource_key(resource_name); new_max = int(sheet["max_resource_base"])
        old_current = int(player.get("resource", player.get("mana", 0)) or 0); old_max = int(player.get("max_resource", player.get("max_mana", 0)) or 0)
        new_current = self._scaled_current(old_current, old_max, new_max)
        player.update({"resource_name": resource_name, "resource_type": resource_type, "resource": new_current, "max_resource": new_max,
                       "resource_regeneration_per_round": int(sheet["resource_regeneration_per_round"]), "mana": new_current, "max_mana": new_max,
                       "armor_class": BASE_ARMOR_CLASS + int(sheet["defense_bonus"]), "initiative_bonus": int(sheet["initiative_bonus"]), "movement": int(sheet["movement"]),
                       "critical_chance_percent": int(sheet["critical_chance_percent"]), "physical_resistance_percent": int(sheet["physical_resistance_percent"]),
                       "status_resistance_percent": int(sheet["status_resistance_percent"]), "defend_action_ac_bonus": int(sheet["defend_action_ac_bonus"])})
        earned_sp = earned_skill_points(level); spent_sp = sum(stats.values()); stored_sp = player.get("attribute_points_unspent", player.get("skill_points_unspent", 0)); calculated_sp = max(0, earned_sp - spent_sp)
        player["skill_points_unspent"] = max(0, int(stored_sp or 0), calculated_sp); player["attribute_points_unspent"] = player["skill_points_unspent"]
        player["ability_points"] = max(0, int(player.get("ability_points", 0) or 0)); player["xp_orbs"] = max(0, int(player.get("xp_orbs", 0) or 0)); player["xp_to_next_level"] = xp_required_for_next_level(level)
        player["total_ability_points_earned_at_level"] = total_ability_points_earned(level)
        skills = player.get("skills") if isinstance(player.get("skills"), dict) else {}; migrated = deepcopy(DEFAULT_SKILLS)
        for name in migrated:
            if name in skills: migrated[name] = int(skills.get(name, 0) or 0)
        player["skills"] = migrated
        inventory = player.get("inventory")
        if not isinstance(inventory, list): player["inventory"] = []
        if not completed:
            for key in ("unlocked_abilities", "equipped_abilities"):
                items = player.get(key)
                if not isinstance(items, list): items = []; player[key] = items
                if not any(isinstance(i, dict) and str(i.get("name", "")).lower() == "power strike" for i in items): items.append(deepcopy(PROTOTYPE_POWER_STRIKE))
        combat = self.data.get("combat")
        if isinstance(combat, dict) and combat.get("active"):
            player_name = str(player.get("name") or "Traveler")
            for actor in combat.get("combatants", []):
                if not isinstance(actor, dict) or actor.get("name") != player_name: continue
                actor.update({"attributes": deepcopy(stats), "attribute_channels": deepcopy(sheet), "max_hp": new_max_hp, "hp": min(int(actor.get("hp", new_max_hp) or 0), new_max_hp),
                              "abilities": deepcopy(player.get("equipped_abilities", [])), "resource_name": resource_name, "resource_type": resource_type,
                              "max_resource": new_max, "resource": min(int(actor.get("resource", new_current) or 0), new_max), "max_mana": new_max,
                              "resource_regeneration_per_round": int(sheet["resource_regeneration_per_round"]), "armor_class": player["armor_class"],
                              "initiative_bonus": player["initiative_bonus"], "movement": player["movement"], "critical_chance_percent": player["critical_chance_percent"],
                              "physical_resistance_percent": player["physical_resistance_percent"], "status_resistance_percent": player["status_resistance_percent"],
                              "defend_action_ac_bonus": player["defend_action_ac_bonus"]})
                actor["mana"] = actor["resource"]; actor.pop("ability_cooldowns", None); break
        self.save()

    def award_xp_orbs(self, amount: int) -> Dict:
        player = self.data.setdefault("player", {}); summary = apply_xp_orbs(player, amount); player["xp_to_next_level"] = summary["xp_to_next_level"]; self.save(); return summary

    def _load(self) -> Dict:
        if not self.path.exists(): return {}
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8")); return loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError): return {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True); temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"); temporary.replace(self.path)

    def snapshot(self) -> Dict: return deepcopy(self.data)

    def _template_from_combat(self, combat: Dict) -> Dict:
        actors = []
        for raw in combat.get("combatants", []) if isinstance(combat, dict) else []:
            if not isinstance(raw, dict): continue
            actor = deepcopy(raw); max_hp = max(0, int(actor.get("max_hp", actor.get("hp", 0)) or 0)); max_resource = max(0, int(actor.get("max_resource", actor.get("max_mana", 0)) or 0))
            actor.update({"hp": max_hp, "max_hp": max_hp, "resource": max_resource, "max_resource": max_resource, "mana": max_resource, "max_mana": max_resource,
                          "movement_used": 0, "primary_action_used": False, "defending": False, "active_defense_ac_bonus": 0, "defeated": False})
            actor.pop("ability_cooldowns", None); actors.append(actor)
        return {"combatants": actors, "grid": deepcopy(combat.get("grid", {})) if isinstance(combat, dict) else {}}

    @staticmethod
    def _add_inventory_item(player: Dict, raw_item: Dict) -> None:
        if not isinstance(raw_item, dict): return
        item = deepcopy(raw_item)
        name = str(item.get("name") or "Item").strip() or "Item"
        item_type = str(item.get("type") or "misc").strip().lower() or "misc"
        item["name"] = name; item["type"] = item_type
        try: quantity = max(1, int(item.get("quantity", 1) or 1))
        except (TypeError, ValueError): quantity = 1
        try: sell_value = max(0, int(item.get("sell_value", 0) or 0))
        except (TypeError, ValueError): sell_value = 0
        item["quantity"] = quantity; item["sell_value"] = sell_value
        inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
        player["inventory"] = inventory
        stackable = item_type in {"misc", "material", "ingredient", "food", "consumable", "ammo", "resource", "flower", "herb"}
        if stackable:
            for existing in inventory:
                if not isinstance(existing, dict): continue
                if str(existing.get("name") or "").strip().lower() == name.lower() and str(existing.get("type") or "misc").strip().lower() == item_type:
                    try: existing_qty = max(1, int(existing.get("quantity", 1) or 1))
                    except (TypeError, ValueError): existing_qty = 1
                    existing["quantity"] = existing_qty + quantity
                    if "sell_value" not in existing: existing["sell_value"] = sell_value
                    return
        inventory.append(item)

    def apply_changes(self, changes: List[Dict]) -> None:
        if not isinstance(changes, list): changes = []
        for change in changes:
            if not isinstance(change, dict): continue
            kind = str(change.get("type") or "").strip().lower()
            if kind == "award_xp_orbs": self.award_xp_orbs(int(change.get("amount", 0) or 0)); continue
            if kind == "add_inventory_item":
                self._add_inventory_item(self.data.setdefault("player", {}), change.get("item") if isinstance(change.get("item"), dict) else {})
                continue
            if kind == "set_encounter_enemies":
                enemies = change.get("enemies")
                if isinstance(enemies, list): self.data["pending_encounter_enemies"] = [deepcopy(e) for e in enemies if isinstance(e, dict)]
                continue
            if kind == "reset_combat_state":
                current = self.data.get("combat")
                if isinstance(current, dict) and current.get("combatants"):
                    template = self.data.get("encounter_template")
                    if not isinstance(template, dict) or not template.get("combatants"): self.data["encounter_template"] = self._template_from_combat(current)
                self.data["encounter_reset_pending"] = True; self.data["combat"] = {"active": False}
                player = self.data.setdefault("player", {}); player["combat_position"] = {"x": 0, "y": 0}; player["hp"] = int(player.get("max_hp", player.get("hp", 0)) or 0)
                player["resource"] = int(player.get("max_resource", 0) or 0); player["mana"] = player["resource"]; player["temporary_hp"] = 0; player["conditions"] = []; continue
            if kind == "restore_hp":
                player = self.data.setdefault("player", {}); requested = change.get("hp", player.get("max_hp", player.get("hp", 0))); player["hp"] = max(0, int(requested or 0)); continue
            if kind in {"restore_mana", "restore_resource"}:
                player = self.data.setdefault("player", {}); requested = change.get("resource", change.get("mana", player.get("max_resource", 0))); value = max(0, int(requested or 0)); player["resource"] = value; player["mana"] = value; continue
            path = change.get("path")
            if isinstance(path, str) and path.strip() and "value" in change: self.set_path(path, change["value"], save=False)
        self.data["turn"] = int(self.data.get("turn", 0)) + 1; self.save()

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
