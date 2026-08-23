"""Inventory display and equipment swapping for The Shattered Realms."""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Dict, List

from .armor import ARMOR_SLOTS, effective_movement, normalize_armor_piece, sync_armor_summary
from .dice import normalize_damage_expression
from .economy import ensure_wallet, format_money

RARITY_ORDER = {"common": 0, "uncommon": 1, "rare": 2, "epic": 3, "legendary": 4}
RARITY_VALUE_MULTIPLIER = {"common": 1.0, "uncommon": 1.25, "rare": 1.6, "epic": 2.2, "legendary": 3.0}


def _item_type(item: Dict) -> str:
    return str(item.get("type") or "misc").strip().lower()


def _item_rarity(item: Dict) -> str:
    rarity = str(item.get("rarity") or "common").strip().lower()
    return rarity if rarity in RARITY_ORDER else "common"


def _safe_int(value, default: int = 0) -> int:
    try: return int(value)
    except (TypeError, ValueError): return int(default)


def _dice_sides(value) -> int:
    match = re.search(r"\d+d(\d+)", str(value or "").lower())
    return int(match.group(1)) if match else 0


def default_sell_value(item: Dict) -> int:
    """Give legacy/generated items a modest resale value when none was stored."""
    if not isinstance(item, dict): return 0
    if "sell_value" in item: return max(0, _safe_int(item.get("sell_value"), 0))
    kind = _item_type(item)
    if kind in {"quest", "quest_item", "key_item"}: return 0
    bases = {"weapon": 6, "shield": 5, "armor": 3, "consumable": 3, "utility": 2, "material": 1, "ingredient": 1, "flower": 1, "herb": 1, "food": 1, "ammo": 1, "focus": 5, "accessory": 5, "arcane_relic": 8, "relic": 8, "misc": 1}
    value = bases.get(kind, 2)
    if kind == "weapon":
        value += max(1, _dice_sides(item.get("damage")) // 2); value += max(0, min(6, _safe_int(item.get("range"), 0)))
    elif kind == "shield": value += max(0, _safe_int(item.get("shield", item.get("max_shield_hp", 0)), 0) * 2)
    elif kind == "armor":
        value += max(0, _safe_int(item.get("max_armor_hp", item.get("armor_hp", 0)), 0) * 2)
        bonus = item.get("stat_bonus") if isinstance(item.get("stat_bonus"), dict) else {}; value += max(0, _safe_int(bonus.get("amount"), 0) * 3)
    elif kind == "consumable" and item.get("healing"): value += max(1, _dice_sides(item.get("healing")) // 2)
    value = round(value * RARITY_VALUE_MULTIPLIER[_item_rarity(item)])
    return max(0, value)


def ensure_inventory_sell_values(player: Dict) -> bool:
    changed = False; inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    for item in inventory:
        if not isinstance(item, dict): continue
        rarity = _item_rarity(item)
        if item.get("rarity") != rarity: item["rarity"] = rarity; changed = True
        if "sell_value" not in item: item["sell_value"] = default_sell_value(item); changed = True
        if "quantity" not in item: item["quantity"] = 1; changed = True
    return changed


def _currency_label(game_master, amount: int) -> str:
    return format_money(amount, game_master.state.data.get("world_profile", {}))


def _same_item(a: Dict | None, b: Dict | None) -> bool:
    if not isinstance(a, dict) or not isinstance(b, dict): return False
    return str(a.get("name") or "").strip().lower() == str(b.get("name") or "").strip().lower() and _item_type(a) == _item_type(b)


def _equipped_label(player: Dict, item: Dict) -> str:
    kind = _item_type(item)
    if kind == "weapon" and _same_item(player.get("equipped_weapon"), item): return " [EQUIPPED WEAPON]"
    if kind == "shield" and _same_item(player.get("equipped_shield"), item): return " [EQUIPPED SHIELD]"
    if kind == "armor":
        slot = str(item.get("slot") or "").strip().lower(); current = (player.get("equipped_armor") or {}).get(slot) if isinstance(player.get("equipped_armor"), dict) else None
        if _same_item(current, item): return f" [EQUIPPED {slot.upper()}]"
    return ""


def _item_mechanics(item: Dict) -> str:
    parts: List[str] = []; kind = _item_type(item)
    if kind == "weapon":
        parts.append(f"Damage {normalize_damage_expression(item.get('damage', '1d4'), '1d4')}")
        if item.get("range") is not None: parts.append(f"Range {item.get('range')}")
        if item.get("attack_attribute"): parts.append(str(item.get("attack_attribute")).title())
    elif kind == "shield": parts.append(f"Shield HP {max(0, _safe_int(item.get('shield', item.get('max_shield_hp', 0)), 0))}")
    elif kind == "armor":
        parts.append(f"Armor {_safe_int(item.get('armor_hp'),0)}/{_safe_int(item.get('max_armor_hp', item.get('armor_hp',0)),0)}"); parts.append(f"Slot {str(item.get('slot') or 'unknown').title()}"); parts.append(f"Weight {_safe_int(item.get('weight'),0)}")
        bonus = item.get("stat_bonus") if isinstance(item.get("stat_bonus"), dict) else None
        if bonus: parts.append(f"+{_safe_int(bonus.get('amount'),0)} {str(bonus.get('stat') or '').title()}")
    elif item.get("healing"): parts.append(f"Healing {normalize_damage_expression(item.get('healing'), '1d4')}")
    if item.get("effect"): parts.append(str(item.get("effect")))
    return " | ".join(parts) if parts else "Utility / story item"


CATEGORY_ORDER = {
    "WEAPONS": 0,
    "SHIELDS": 1,
    "ARMOR": 2,
    "POTIONS & HEALING": 3,
    "CONSUMABLES": 4,
    "AMMO": 5,
    "MATERIALS & INGREDIENTS": 6,
    "TOOLS & UTILITY": 7,
    "RELICS & ACCESSORIES": 8,
    "QUEST & KEY ITEMS": 9,
    "OTHER": 10,
}


def _inventory_category(item: Dict) -> str:
    kind = _item_type(item)
    name = str(item.get("name") or "").lower()
    description = str(item.get("description") or "").lower()
    combined = f"{name} {description}"
    if kind == "weapon": return "WEAPONS"
    if kind == "shield": return "SHIELDS"
    if kind == "armor": return "ARMOR"
    if kind in {"quest", "quest_item", "key_item"}: return "QUEST & KEY ITEMS"
    if kind == "ammo": return "AMMO"
    if kind in {"material", "ingredient", "flower", "herb", "resource"}: return "MATERIALS & INGREDIENTS"
    if kind in {"relic", "arcane_relic", "accessory", "focus", "headwear"}: return "RELICS & ACCESSORIES"
    if kind == "consumable":
        healing_words = ("potion", "elixir", "tonic", "draught", "medicine", "medkit", "bandage", "stim", "healing", "heal", "restore health", "restore hp")
        if item.get("healing") or any(word in combined for word in healing_words): return "POTIONS & HEALING"
        return "CONSUMABLES"
    if kind == "food": return "CONSUMABLES"
    if kind in {"utility", "tool"}: return "TOOLS & UTILITY"
    return "OTHER"


def _organize_inventory(player: Dict) -> bool:
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    before = [id(item) for item in inventory]
    inventory.sort(key=lambda item: (
        CATEGORY_ORDER.get(_inventory_category(item), 99) if isinstance(item, dict) else 99,
        RARITY_ORDER.get(_item_rarity(item), 0) if isinstance(item, dict) else 0,
        str(item.get("name") or "").lower() if isinstance(item, dict) else str(item).lower(),
    ))
    return before != [id(item) for item in inventory]


def show_equipment(player: Dict) -> None:
    print("\nEQUIPPED GEAR"); weapon = player.get("equipped_weapon") if isinstance(player.get("equipped_weapon"), dict) else None; shield = player.get("equipped_shield") if isinstance(player.get("equipped_shield"), dict) else None
    print("  Weapon: " + ((weapon.get("name") + " — " + _item_mechanics(weapon)) if weapon else "None"))
    if shield: print(f"  Shield: {shield.get('name')} — {_safe_int(player.get('shield_hp'),0)}/{_safe_int(player.get('max_shield_hp'),0)} Shield HP")
    else: print("  Shield: None")
    armor = player.get("equipped_armor") if isinstance(player.get("equipped_armor"), dict) else {}; print("  Armor:")
    for slot in ARMOR_SLOTS:
        piece = armor.get(slot)
        if isinstance(piece, dict): print(f"    {slot.title():<12} {piece.get('name')} — {_item_mechanics(piece)}")
        else: print(f"    {slot.title():<12} None")


def show_inventory(game_master) -> None:
    player = game_master.state.data.get("player", {})
    changed = ensure_inventory_sell_values(player)
    changed = _organize_inventory(player) or changed
    wallet = ensure_wallet(game_master, grant_starting_funds=True)
    if changed: game_master.state.save()
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    print("\n" + "=" * 52); print("INVENTORY"); print("=" * 52)
    print(f"💰 Balance: {format_money(wallet.get('amount', 0), wallet)}")
    show_equipment(player)
    if not inventory: print("\nYour inventory is empty."); return

    current_category = None
    for index, item in enumerate(inventory, 1):
        if not isinstance(item, dict):
            category = "OTHER"
            if category != current_category:
                print(f"\n{category}"); print("-" * len(category)); current_category = category
            print(f"  {index}. {item}")
            continue
        category = _inventory_category(item)
        if category != current_category:
            print(f"\n{category}")
            print("-" * len(category))
            current_category = category
        desc = str(item.get("description") or "").strip(); desc_text = f" — {desc}" if desc else ""; quantity = max(1, _safe_int(item.get("quantity"), 1)); quantity_text = f" x{quantity}" if quantity > 1 else ""; sell_value = default_sell_value(item)
        sell_text = "Unsellable" if sell_value <= 0 else f"Sell Value {_currency_label(game_master, sell_value)}" + (" each" if quantity > 1 else "")
        rarity = _item_rarity(item).title()
        print(f"  {index}. {item.get('name','Item')}{quantity_text} [{rarity}] ({_item_type(item).title()}){_equipped_label(player, item)}{desc_text}")
        print(f"     {_item_mechanics(item)} | {sell_text}")
    print("\nType 'equip' to change your equipped weapon, shield, or armor piece. Type 'shop' when visiting a merchant.")


def _combat_active(game_master) -> bool:
    combat = game_master.state.data.get("combat"); return isinstance(combat, dict) and bool(combat.get("active"))


def _equip_weapon(player: Dict, item: Dict) -> str:
    player["equipped_weapon"] = deepcopy(item); player["damage"] = normalize_damage_expression(item.get("damage", "1d4"), "1d4"); return f"Equipped weapon: {item.get('name')} ({player['damage']})."


def _equip_shield(player: Dict, item: Dict) -> str:
    shield_hp = max(1, _safe_int(item.get("shield", item.get("max_shield_hp", 1)), 1)); item = deepcopy(item); item["shield"] = shield_hp; player["equipped_shield"] = item; player["max_shield_hp"] = shield_hp; player["shield_hp"] = shield_hp; return f"Equipped shield: {item.get('name')} ({shield_hp} Shield HP)."


def _equip_armor(player: Dict, item: Dict) -> str:
    piece = normalize_armor_piece(item); slot = piece["slot"]; equipped = player.get("equipped_armor") if isinstance(player.get("equipped_armor"), dict) else {}; equipped = deepcopy(equipped); equipped[slot] = piece; player["equipped_armor"] = equipped; player["armor_set_name"] = "Mixed Set"; sync_armor_summary(player); base_move = _safe_int(player.get("base_movement_without_armor", player.get("movement", 1)), 1); player["base_movement_without_armor"] = base_move; player["movement"] = effective_movement(base_move, equipped); return f"Equipped {piece.get('name')} in the {slot.title()} slot. Armor is now {player.get('armor',0)}/{player.get('max_armor',0)}."


def equip_inventory_item(game_master, index: int) -> str:
    if _combat_active(game_master): return "You cannot swap equipment during active combat. Finish or leave the encounter first."
    player = game_master.state.data.get("player", {}); inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    if index < 1 or index > len(inventory): return f"Choose an inventory number from 1-{len(inventory)}."
    item = inventory[index - 1]
    if not isinstance(item, dict): return "That inventory entry cannot be equipped."
    kind = _item_type(item)
    if kind == "weapon": message = _equip_weapon(player, item)
    elif kind == "shield": message = _equip_shield(player, item)
    elif kind == "armor": message = _equip_armor(player, item)
    else: return f"{item.get('name','That item')} is not equippable."
    game_master.state.save(); return message


def run_equipment_screen(game_master) -> None:
    if _combat_active(game_master): print("\nYou cannot swap equipment during active combat."); return
    show_inventory(game_master); inventory = game_master.state.data.get("player", {}).get("inventory")
    if not isinstance(inventory, list) or not inventory: return
    while True:
        raw = input("\nEnter the inventory number to equip, or 'back': ").strip().lower()
        if raw in {"back", "b", "exit", "cancel"}: return
        try: index = int(raw)
        except ValueError: print("Enter an inventory number or 'back'."); continue
        print(equip_inventory_item(game_master, index)); show_equipment(game_master.state.data.get("player", {})); return
