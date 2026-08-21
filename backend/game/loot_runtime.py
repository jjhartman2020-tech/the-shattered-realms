"""Persistent loot/pickup support for The Shattered Realms.

This module patches GameState.apply_changes so AI-emitted add_inventory_item
changes become real saved inventory entries. It also adds concise loot-generation
context to the AI provider so found loot fits the confirmed world and player level.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from .inventory import default_sell_value
from .state import GameState

_STACKABLE_TYPES = {"material", "ingredient", "flower", "herb", "food", "ammo", "consumable", "misc"}
_INSTALLED = False


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _normalize_item(raw: Dict, level: int) -> Dict:
    item = deepcopy(raw) if isinstance(raw, dict) else {}
    item["name"] = str(item.get("name") or "Unknown Item").strip() or "Unknown Item"
    item["type"] = str(item.get("type") or "misc").strip().lower().replace(" ", "_")
    item["description"] = str(item.get("description") or "").strip()
    item["quantity"] = max(1, _safe_int(item.get("quantity"), 1))

    # Keep mechanics explicit and safe for the rest of the engine.
    if item["type"] == "shield":
        shield = max(1, _safe_int(item.get("shield", item.get("max_shield_hp", 1)), 1))
        item["shield"] = shield
        item["max_shield_hp"] = shield
    elif item["type"] == "armor":
        item["armor_hp"] = max(0, _safe_int(item.get("armor_hp"), 0))
        item["max_armor_hp"] = max(item["armor_hp"], _safe_int(item.get("max_armor_hp", item["armor_hp"]), item["armor_hp"]))
        item["weight"] = max(0, _safe_int(item.get("weight"), 0))
    elif item["type"] == "weapon":
        item["damage"] = str(item.get("damage") or "1d4")
        item["range"] = max(0, _safe_int(item.get("range"), 1))
        attr = str(item.get("attack_attribute") or "dexterity").strip().lower()
        item["attack_attribute"] = attr if attr in {"strength", "dexterity"} else "dexterity"

    # Record the level the item entered the campaign so future balancing can use it.
    item.setdefault("item_level", max(1, int(level or 1)))
    if "sell_value" not in item:
        item["sell_value"] = default_sell_value(item)
    else:
        item["sell_value"] = max(0, _safe_int(item.get("sell_value"), 0))
    return item


def _stack_key(item: Dict) -> tuple[str, str]:
    return (str(item.get("name") or "").strip().lower(), str(item.get("type") or "misc").strip().lower())


def _add_inventory_item(player: Dict, raw_item: Dict) -> Dict:
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    player["inventory"] = inventory
    item = _normalize_item(raw_item, int(player.get("level", 1) or 1))

    if item.get("type") in _STACKABLE_TYPES:
        key = _stack_key(item)
        for existing in inventory:
            if not isinstance(existing, dict) or _stack_key(existing) != key:
                continue
            existing["quantity"] = max(1, _safe_int(existing.get("quantity"), 1)) + item["quantity"]
            # Preserve the more complete description/mechanics when stacking.
            if not existing.get("description") and item.get("description"):
                existing["description"] = item["description"]
            if "sell_value" not in existing:
                existing["sell_value"] = item["sell_value"]
            return existing

    inventory.append(item)
    return item


def _remove_inventory_item(player: Dict, name: str, quantity: int = 1) -> int:
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    wanted = str(name or "").strip().lower()
    remaining = max(1, int(quantity or 1))
    removed = 0
    for index in range(len(inventory) - 1, -1, -1):
        item = inventory[index]
        if not isinstance(item, dict) or str(item.get("name") or "").strip().lower() != wanted:
            continue
        have = max(1, _safe_int(item.get("quantity"), 1))
        take = min(have, remaining)
        removed += take
        remaining -= take
        if take >= have:
            inventory.pop(index)
        else:
            item["quantity"] = have - take
        if remaining <= 0:
            break
    return removed


def install_loot_runtime() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    original_apply_changes = GameState.apply_changes

    def apply_changes_with_inventory(self: GameState, changes: List[Dict]) -> None:
        changes = changes if isinstance(changes, list) else []
        passthrough: List[Dict] = []
        touched_inventory = False
        player = self.data.setdefault("player", {})

        for change in changes:
            if not isinstance(change, dict):
                continue
            kind = str(change.get("type") or "").strip().lower()
            if kind in {"add_inventory_item", "add_item", "give_item", "loot_item"}:
                item = change.get("item")
                if isinstance(item, dict):
                    _add_inventory_item(player, item)
                    touched_inventory = True
                continue
            if kind in {"remove_inventory_item", "remove_item"}:
                name = str(change.get("name") or (change.get("item") or {}).get("name") or "")
                _remove_inventory_item(player, name, _safe_int(change.get("quantity"), 1))
                touched_inventory = True
                continue
            passthrough.append(change)

        original_apply_changes(self, passthrough)
        if touched_inventory:
            self.save()

    GameState.apply_changes = apply_changes_with_inventory

    # Add loot-generation guidance without rewriting the provider's main system prompt.
    try:
        from backend.ai.provider import OpenAIProvider
        original_respond = OpenAIProvider.respond

        def respond_with_loot_rules(self, context: Dict) -> Dict:
            enriched = dict(context) if isinstance(context, dict) else {}
            enriched["loot_generation_rules"] = {
                "world_fit": "All loot must match the confirmed world_profile, era, technology, supernatural rules, and culture.",
                "progression": "Early-game loot is usually modest. Stronger gear should become more common as player level and encounter importance rise; occasional exciting upgrades are allowed without making every drop better than current gear.",
                "pickup": "When the player actually takes/receives/harvests an item, emit state_changes type add_inventory_item with a complete item object. Seeing or finding an item alone does not auto-add it.",
                "combat_loot": "When a combat or major challenge is clearly finished, you may reveal 0-3 sensible loot items or materials in narration. Do not force loot every fight. If the player then takes them, add them to inventory through add_inventory_item.",
                "item_fields": "Items should include name, type, description, quantity, sell_value, plus exact mechanics when relevant (damage/range/attack_attribute, shield HP, armor slot/Armor HP/weight/stat_bonus, healing/effect).",
                "economy": "sell_value is numeric only; the terminal displays it using the campaign world's currency.",
            }
            return original_respond(self, enriched)

        OpenAIProvider.respond = respond_with_loot_rules
    except Exception:
        pass
