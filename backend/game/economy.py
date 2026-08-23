"""World-aware currency, merchants, buying, and selling for The Shattered Realms."""
from __future__ import annotations

from copy import deepcopy
import json
import math
import random
import re
from typing import Dict, List

from .loot import scale_item_for_rarity

SHOP_RARITY_TABLES = {
    # Ordinary stores never carry Epic/Legendary gear.
    "ordinary": {"common": 82.0, "uncommon": 16.0, "rare": 2.0, "epic": 0.0, "legendary": 0.0},
    "quality": {"common": 65.0, "uncommon": 27.0, "rare": 7.0, "epic": 1.0, "legendary": 0.0},
    "elite": {"common": 40.0, "uncommon": 35.0, "rare": 20.0, "epic": 5.0, "legendary": 0.0},
    # Legendary stock exists only at genuinely exceptional/special merchants.
    "special": {"common": 20.0, "uncommon": 30.0, "rare": 30.0, "epic": 18.0, "legendary": 2.0},
}
SHOP_RARITIES = ("common", "uncommon", "rare", "epic", "legendary")


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def currency_profile(world: Dict | None) -> Dict:
    """Return the world's persistent single-currency profile."""
    world = world if isinstance(world, dict) else {}
    explicit_name = str(world.get("currency_name") or "").strip()
    explicit_symbol = str(world.get("currency_symbol") or "").strip()
    if explicit_name:
        return {"name": explicit_name, "symbol": explicit_symbol, "prefix": bool(explicit_symbol)}

    economy = str(world.get("economy") or "").strip()
    genre = str(world.get("genre") or "").lower()
    era = str(world.get("era") or "").lower()
    tech = str(world.get("technology_level") or "").lower()
    text = f"{economy} {genre} {era} {tech}".lower()

    if "$" in economy or any(word in text for word in ("dollar", "dollars", "usd", "modern", "contemporary")):
        return {"name": "dollars", "symbol": "$", "prefix": True}
    if any(word in text for word in ("credit", "credits", "cyberpunk", "space opera", "futuristic", "sci-fi", "science fiction")):
        return {"name": "credits", "symbol": "", "prefix": False}
    if any(word in text for word in ("gold", "medieval", "fantasy")):
        return {"name": "gold", "symbol": "", "prefix": False}

    match = re.search(r"(?:currency|money|paid in|uses?)\s*(?:is|:|=)?\s*([A-Za-z][A-Za-z -]{1,24})", economy, re.IGNORECASE)
    if match:
        name = match.group(1).strip().rstrip(".,;")
        return {"name": name, "symbol": "", "prefix": False}
    return {"name": "currency", "symbol": "", "prefix": False}


def format_money(amount: int, world_or_profile: Dict | None) -> str:
    amount = max(0, _safe_int(amount, 0))
    profile = world_or_profile if isinstance(world_or_profile, dict) and "prefix" in world_or_profile else currency_profile(world_or_profile)
    symbol = str(profile.get("symbol") or "")
    name = str(profile.get("name") or "currency")
    if symbol and profile.get("prefix"):
        return f"{symbol}{amount:,}"
    if amount == 1 and name.endswith("s"):
        unit = name[:-1]
    else:
        unit = name
    return f"{amount:,} {unit}"


def ensure_wallet(game_master, *, grant_starting_funds: bool = False) -> Dict:
    """Create/migrate the player's wallet and keep its currency synced to the world."""
    player = game_master.state.data.setdefault("player", {})
    world = game_master.state.data.get("world_profile", {})
    profile = currency_profile(world)
    wallet = player.get("wallet") if isinstance(player.get("wallet"), dict) else None

    if wallet is None:
        legacy = player.get("currency") if isinstance(player.get("currency"), dict) else {}
        legacy_total = sum(max(0, _safe_int(value, 0)) for value in legacy.values()) if legacy else 0
        amount = legacy_total
        if amount <= 0 and grant_starting_funds and player.get("character_creation_complete"):
            # A modest universal starter purse so the economy can function immediately.
            amount = 50
        wallet = {"amount": amount, **profile}
        player["wallet"] = wallet
    else:
        wallet["amount"] = max(0, _safe_int(wallet.get("amount", 0), 0))
        wallet.update(profile)

    game_master.state.save()
    return wallet


def wallet_text(game_master) -> str:
    wallet = ensure_wallet(game_master)
    return format_money(wallet.get("amount", 0), wallet)


def _normalize_shop_quality(raw: str, player_level: int, hint: str = "") -> str:
    quality = str(raw or "ordinary").strip().lower().replace(" ", "_")
    aliases = {"normal": "ordinary", "common": "ordinary", "good": "quality", "premium": "elite", "legendary": "special", "mythic": "special"}
    quality = aliases.get(quality, quality)
    if quality not in SHOP_RARITY_TABLES:
        quality = "ordinary"

    level = max(1, min(100, _safe_int(player_level, 1)))
    hint_text = str(hint or "").lower()
    exceptional = any(word in hint_text for word in ("legendary", "special", "master", "auction", "black market", "secret", "elite", "royal", "military prototype"))
    if quality == "special" and level < 70 and not exceptional:
        quality = "elite" if level >= 30 else "quality"
    if quality == "elite" and level < 20 and not exceptional:
        quality = "quality"
    return quality


def roll_shop_rarity(shop_quality: str, player_level: int = 1) -> str:
    quality = _normalize_shop_quality(shop_quality, player_level)
    table = SHOP_RARITY_TABLES[quality]
    roll = random.random() * 100.0
    cumulative = 0.0
    for rarity in SHOP_RARITIES:
        cumulative += table[rarity]
        if roll < cumulative:
            return rarity
    return "common"


def _base_price_from_item(item: Dict) -> int:
    value = max(0, _safe_int(item.get("sell_value", 0), 0))
    if value <= 0:
        kind = str(item.get("type") or "misc").lower()
        value = {"weapon": 10, "shield": 8, "armor": 8, "consumable": 4, "ammo": 2, "material": 2, "utility": 4, "tool": 5, "accessory": 8, "relic": 12}.get(kind, 3)
    return max(1, value)


def _normalize_stock_item(raw: Dict, quality: str, player_level: int) -> Dict:
    item = deepcopy(raw) if isinstance(raw, dict) else {}
    item["name"] = str(item.get("name") or "Unnamed Item").strip() or "Unnamed Item"
    item["type"] = str(item.get("type") or "misc").strip().lower() or "misc"
    item["description"] = str(item.get("description") or "").strip()
    item["quantity"] = max(1, min(99, _safe_int(item.get("quantity", 1), 1)))
    item["sell_value"] = _base_price_from_item(item)
    rarity = roll_shop_rarity(quality, player_level)
    scale_item_for_rarity(item, rarity)
    # Buying costs twice the resale amount. Haggling will modify this later.
    item["buy_price"] = max(1, int(math.ceil(max(1, _safe_int(item.get("sell_value"), 1)) * 2.0)))
    return item


def _fallback_stock(world: Dict, store_hint: str) -> List[Dict]:
    common_gear = world.get("common_weapons_and_gear") if isinstance(world.get("common_weapons_and_gear"), list) else []
    stock: List[Dict] = []
    for name in common_gear[:6]:
        stock.append({"name": str(name), "type": "utility", "description": "Common setting-appropriate gear.", "quantity": 1, "sell_value": 5})
    if not stock:
        stock = [
            {"name": "Basic Supply Kit", "type": "utility", "description": "Ordinary supplies appropriate to this world.", "quantity": 1, "sell_value": 5},
            {"name": "Basic Healing Supply", "type": "consumable", "description": "A modest healing item appropriate to this world.", "quantity": 2, "sell_value": 4, "healing": "1d4"},
        ]
    return stock


def generate_merchant(game_master, store_hint: str) -> Dict:
    """Generate and persist one world/location-appropriate merchant with Python-owned rarity."""
    snapshot = game_master.state.snapshot()
    world = snapshot.get("world_profile", {}) if isinstance(snapshot.get("world_profile"), dict) else {}
    player = snapshot.get("player", {}) if isinstance(snapshot.get("player"), dict) else {}
    level = max(1, _safe_int(player.get("level", 1), 1))
    location = str(player.get("location") or "unknown")
    hint = str(store_hint or "local general merchant").strip()
    client = getattr(game_master.provider, "client", None)
    model = getattr(game_master.provider, "model", None)

    data: Dict = {}
    if client is not None and model:
        instructions = """You generate a merchant for a universal RPG. Return ONLY valid JSON.
The merchant and every item MUST fit the confirmed world, current location, technology, powers, culture, and the requested store type. Never default to medieval fantasy.
Return: merchant_name, store_type, quality, description, stock.
quality must be one of ordinary, quality, elite, special. Use special only for genuinely exceptional merchants such as secret master dealers, auctions, legendary craftsmen, black markets, royal vault sellers, or similarly rare cases.
stock must contain 6-10 BASE items appropriate to the store and player level. Do NOT assign rarity; Python does that.
Each stock item must include name, type, description, quantity, sell_value and exact mechanics when relevant: weapon damage/range/attack_attribute; shield shield; armor slot/armor_hp/max_armor_hp/weight/stat_bonus; consumable healing/effect; ammo/material/tool exact purpose.
Base items should be progression-appropriate before rarity scaling. Keep ordinary early-game stock modest. Legendary-quality mechanics are NOT generated here.
Do not include quest/key items for sale unless the world context specifically makes that legitimate."""
        payload = {
            "world": world,
            "location": location,
            "player_level": level,
            "store_request": hint,
        }
        try:
            response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, default=str))
            parsed = json.loads(response.output_text.strip())
            if isinstance(parsed, dict):
                data = parsed
        except Exception:
            data = {}

    merchant_name = str(data.get("merchant_name") or "Local Merchant").strip()
    store_type = str(data.get("store_type") or hint or "General Store").strip()
    quality = _normalize_shop_quality(str(data.get("quality") or "ordinary"), level, hint)
    raw_stock = data.get("stock") if isinstance(data.get("stock"), list) else _fallback_stock(world, hint)
    stock = [_normalize_stock_item(item, quality, level) for item in raw_stock[:10] if isinstance(item, dict)]
    if not stock:
        stock = [_normalize_stock_item(item, quality, level) for item in _fallback_stock(world, hint)]

    merchant = {
        "merchant_name": merchant_name,
        "store_type": store_type,
        "quality": quality,
        "description": str(data.get("description") or "").strip(),
        "location": location,
        "stock": stock,
    }
    game_master.state.data.setdefault("world_flags", {})["active_merchant"] = merchant
    game_master.state.save()
    return merchant


def active_merchant(game_master) -> Dict | None:
    flags = game_master.state.data.get("world_flags") if isinstance(game_master.state.data.get("world_flags"), dict) else {}
    merchant = flags.get("active_merchant")
    return merchant if isinstance(merchant, dict) and isinstance(merchant.get("stock"), list) else None


def clear_active_merchant(game_master) -> None:
    flags = game_master.state.data.setdefault("world_flags", {})
    flags.pop("active_merchant", None)
    game_master.state.save()


def _item_mechanics(item: Dict) -> str:
    kind = str(item.get("type") or "misc").lower()
    parts: List[str] = []
    if kind == "weapon":
        if item.get("damage"): parts.append(f"Damage {item.get('damage')}")
        if item.get("range") is not None: parts.append(f"Range {item.get('range')}")
        if item.get("attack_attribute"): parts.append(str(item.get("attack_attribute")).title())
    elif kind == "shield":
        parts.append(f"Shield HP {_safe_int(item.get('shield', item.get('max_shield_hp', 0)), 0)}")
    elif kind == "armor":
        parts.append(f"Armor HP {_safe_int(item.get('max_armor_hp', item.get('armor_hp', 0)), 0)}")
        if item.get("slot"): parts.append(f"{str(item.get('slot')).title()}")
        if item.get("weight") is not None: parts.append(f"Weight {_safe_int(item.get('weight'), 0)}")
        bonus = item.get("stat_bonus") if isinstance(item.get("stat_bonus"), dict) else None
        if bonus: parts.append(f"+{_safe_int(bonus.get('amount'), 0)} {str(bonus.get('stat') or '').title()}")
    elif item.get("healing"):
        parts.append(f"Healing {item.get('healing')}")
    if item.get("effect"): parts.append(str(item.get("effect")))
    return " | ".join(parts) if parts else "Utility / story item"


def _same_item(a: Dict | None, b: Dict | None) -> bool:
    if not isinstance(a, dict) or not isinstance(b, dict): return False
    return str(a.get("name") or "").lower() == str(b.get("name") or "").lower() and str(a.get("type") or "").lower() == str(b.get("type") or "").lower()


def _equipped(player: Dict, item: Dict) -> bool:
    if _same_item(player.get("equipped_weapon"), item) or _same_item(player.get("equipped_shield"), item):
        return True
    armor = player.get("equipped_armor") if isinstance(player.get("equipped_armor"), dict) else {}
    return any(_same_item(piece, item) for piece in armor.values() if isinstance(piece, dict))


def _comparison_line(player: Dict, item: Dict) -> str:
    kind = str(item.get("type") or "").lower()
    current = None
    if kind == "weapon": current = player.get("equipped_weapon")
    elif kind == "shield": current = player.get("equipped_shield")
    elif kind == "armor":
        slot = str(item.get("slot") or "").lower()
        armor = player.get("equipped_armor") if isinstance(player.get("equipped_armor"), dict) else {}
        current = armor.get(slot)
    if not isinstance(current, dict):
        return "Currently equipped: nothing comparable."
    return f"Currently equipped: {current.get('name', 'Item')} [{str(current.get('rarity') or 'common').title()}] — {_item_mechanics(current)}"


def show_shop(game_master, merchant: Dict | None = None) -> None:
    merchant = merchant or active_merchant(game_master)
    if not merchant:
        print("\nNo merchant is currently open.")
        return
    wallet = ensure_wallet(game_master)
    world = game_master.state.data.get("world_profile", {})
    print("\n" + "=" * 56)
    print(f"🏪 {merchant.get('merchant_name', 'MERCHANT')} — {merchant.get('store_type', 'Shop')}")
    print("=" * 56)
    if merchant.get("description"): print(str(merchant.get("description")))
    print(f"Shop quality: {str(merchant.get('quality') or 'ordinary').title()} | Your balance: {format_money(wallet.get('amount', 0), wallet)}")
    stock = merchant.get("stock") if isinstance(merchant.get("stock"), list) else []
    if not stock:
        print("This merchant is out of stock.")
        return
    print("\nFOR SALE")
    for index, item in enumerate(stock, 1):
        if not isinstance(item, dict): continue
        rarity = str(item.get("rarity") or "common").title()
        qty = max(1, _safe_int(item.get("quantity", 1), 1))
        qty_text = f" x{qty}" if qty > 1 else ""
        price = max(1, _safe_int(item.get("buy_price", 1), 1))
        print(f"  {index}. {item.get('name', 'Item')}{qty_text} [{rarity}] — {_item_mechanics(item)}")
        print(f"     Buy Price: {format_money(price, world)} | Sell Value: {format_money(_safe_int(item.get('sell_value'), 0), world)}")
    print("\nCommands: buy <number> | compare <number> | sell | refresh | leave")


def buy_item(game_master, index: int) -> str:
    merchant = active_merchant(game_master)
    if not merchant: return "No merchant is currently open."
    stock = merchant.get("stock") if isinstance(merchant.get("stock"), list) else []
    if index < 1 or index > len(stock): return f"Choose a shop item from 1-{len(stock)}."
    item = stock[index - 1]
    if not isinstance(item, dict): return "That shop entry cannot be purchased."
    wallet = ensure_wallet(game_master)
    price = max(1, _safe_int(item.get("buy_price", 1), 1))
    balance = max(0, _safe_int(wallet.get("amount", 0), 0))
    if balance < price:
        return f"You need {format_money(price, wallet)}, but you only have {format_money(balance, wallet)}."

    purchased = deepcopy(item)
    purchased.pop("buy_price", None)
    purchased["quantity"] = 1
    wallet["amount"] = balance - price
    game_master.state._add_inventory_item(game_master.state.data.setdefault("player", {}), purchased)

    quantity = max(1, _safe_int(item.get("quantity", 1), 1))
    if quantity <= 1:
        del stock[index - 1]
    else:
        item["quantity"] = quantity - 1
    game_master.state.save()
    return f"Bought {purchased.get('name')} for {format_money(price, wallet)}. Balance: {format_money(wallet.get('amount', 0), wallet)}."


def _remove_inventory_quantity(inventory: List, index: int, quantity: int = 1) -> Dict | None:
    item = inventory[index]
    if not isinstance(item, dict): return None
    current = max(1, _safe_int(item.get("quantity", 1), 1))
    sold = deepcopy(item); sold["quantity"] = min(quantity, current)
    if quantity >= current:
        del inventory[index]
    else:
        item["quantity"] = current - quantity
    return sold


def sell_item(game_master, index: int) -> str:
    player = game_master.state.data.setdefault("player", {})
    from .inventory import ensure_inventory_sell_values
    ensure_inventory_sell_values(player)
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    if index < 1 or index > len(inventory): return f"Choose an inventory item from 1-{len(inventory)}."
    item = inventory[index - 1]
    if not isinstance(item, dict): return "That inventory entry cannot be sold."
    if _equipped(player, item): return "Unequip that item before selling it."
    value = max(0, _safe_int(item.get("sell_value", 0), 0))
    if value <= 0: return f"{item.get('name', 'That item')} is unsellable."

    sold = _remove_inventory_quantity(inventory, index - 1, 1)
    wallet = ensure_wallet(game_master)
    wallet["amount"] = max(0, _safe_int(wallet.get("amount", 0), 0)) + value

    merchant = active_merchant(game_master)
    if merchant and sold:
        resale = deepcopy(sold)
        resale["quantity"] = 1
        resale["buy_price"] = max(1, int(math.ceil(value * 2.0)))
        merchant.setdefault("stock", []).append(resale)
    game_master.state.save()
    return f"Sold {item.get('name')} for {format_money(value, wallet)}. Balance: {format_money(wallet.get('amount', 0), wallet)}."


def _show_sell_inventory(game_master) -> None:
    player = game_master.state.data.get("player", {})
    from .inventory import ensure_inventory_sell_values
    ensure_inventory_sell_values(player)
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    world = game_master.state.data.get("world_profile", {})
    print("\nSELL ITEMS")
    if not inventory:
        print("Your inventory is empty.")
        return
    for index, item in enumerate(inventory, 1):
        if not isinstance(item, dict): continue
        value = max(0, _safe_int(item.get("sell_value", 0), 0))
        equipped = " [EQUIPPED — CANNOT SELL]" if _equipped(player, item) else ""
        sell_text = "Unsellable" if value <= 0 else format_money(value, world)
        print(f"  {index}. {item.get('name', 'Item')} [{str(item.get('rarity') or 'common').title()}] — {sell_text}{equipped}")


def run_shop_screen(game_master) -> None:
    combat = game_master.state.data.get("combat")
    if isinstance(combat, dict) and combat.get("active"):
        print("\nYou cannot shop during active combat.")
        return

    ensure_wallet(game_master, grant_starting_funds=True)
    merchant = active_merchant(game_master)
    if not merchant:
        hint = input("\nWhat kind of merchant/store are you visiting? (or 'back'): ").strip()
        if hint.lower() in {"back", "b", "cancel", "exit"}:
            return
        merchant = generate_merchant(game_master, hint or "local general merchant")

    while True:
        show_shop(game_master, merchant)
        raw = input("\nShop> ").strip()
        lowered = raw.lower()
        if lowered in {"leave", "back", "b", "exit", "close"}:
            clear_active_merchant(game_master)
            print("You leave the shop.")
            return
        if lowered in {"refresh", "show", "shop", "stock"}:
            merchant = active_merchant(game_master) or merchant
            continue
        if lowered == "sell":
            _show_sell_inventory(game_master)
            choice = input("Sell which inventory number? (or 'back'): ").strip().lower()
            if choice in {"back", "b", "cancel"}: continue
            try: print(sell_item(game_master, int(choice)))
            except ValueError: print("Enter an inventory number.")
            merchant = active_merchant(game_master) or merchant
            continue
        if lowered.startswith("buy "):
            try: print(buy_item(game_master, int(lowered.split(maxsplit=1)[1])))
            except ValueError: print("Use: buy <number>")
            merchant = active_merchant(game_master) or merchant
            continue
        if lowered.startswith("compare "):
            try: index = int(lowered.split(maxsplit=1)[1])
            except ValueError:
                print("Use: compare <number>"); continue
            stock = merchant.get("stock") if isinstance(merchant.get("stock"), list) else []
            if not 1 <= index <= len(stock):
                print(f"Choose a shop item from 1-{len(stock)}."); continue
            item = stock[index - 1]
            print(f"\n{item.get('name')} [{str(item.get('rarity') or 'common').title()}] — {_item_mechanics(item)}")
            print(_comparison_line(game_master.state.data.get("player", {}), item))
            continue
        print("Use: buy <number>, compare <number>, sell, refresh, or leave.")
