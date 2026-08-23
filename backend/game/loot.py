"""Authoritative loot rarity rolls and rarity-based item scaling."""
from __future__ import annotations

import random
import re
from typing import Dict

RARITIES = ("common", "uncommon", "rare", "epic", "legendary")

# Hard Python-controlled rarity odds by source tier.
# Legendary is intentionally extremely rare from routine loot.
RARITY_TABLES = {
    "routine": {"common": 78.0, "uncommon": 17.0, "rare": 4.3, "epic": 0.65, "legendary": 0.05},
    "dangerous": {"common": 65.0, "uncommon": 24.0, "rare": 8.5, "epic": 2.3, "legendary": 0.2},
    "elite": {"common": 45.0, "uncommon": 30.0, "rare": 18.0, "epic": 6.0, "legendary": 1.0},
    "boss": {"common": 20.0, "uncommon": 30.0, "rare": 30.0, "epic": 15.0, "legendary": 5.0},
    "mythic": {"common": 5.0, "uncommon": 15.0, "rare": 30.0, "epic": 30.0, "legendary": 20.0},
}

RARITY_SELL_MULTIPLIER = {
    "common": 1.0,
    "uncommon": 1.3,
    "rare": 1.8,
    "epic": 2.8,
    "legendary": 5.0,
}

RARITY_POWER_MULTIPLIER = {
    "common": 1.0,
    "uncommon": 1.2,
    "rare": 1.5,
    "epic": 2.0,
    "legendary": 3.0,
}

DICE_LADDER = [
    "1d3", "1d4", "1d6", "1d8", "1d10", "1d12",
    "2d6", "2d8", "2d10", "3d8", "3d10", "4d8",
]
RARITY_DICE_STEPS = {"common": 0, "uncommon": 1, "rare": 2, "epic": 3, "legendary": 4}


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _normalized_tier(value) -> str:
    tier = str(value or "routine").strip().lower().replace(" ", "_")
    aliases = {
        "normal": "routine", "ordinary": "routine", "common": "routine",
        "hard": "dangerous", "danger": "dangerous",
        "champion": "elite", "mini_boss": "elite", "miniboss": "elite",
        "major_boss": "boss", "final_boss": "mythic", "endgame": "mythic",
        "legendary": "mythic",
    }
    tier = aliases.get(tier, tier)
    return tier if tier in RARITY_TABLES else "routine"


def roll_rarity(loot_tier: str = "routine", player_level: int = 1) -> str:
    """Roll rarity from a hard probability table.

    Player level gives only a very small quality nudge so normal loot never turns
    into a Legendary farm at high level. Source tier remains the main driver.
    """
    tier = _normalized_tier(loot_tier)
    table = RARITY_TABLES[tier]
    level = max(1, min(100, _safe_int(player_level, 1)))
    # At level 100 this is only +0.5 percentile points toward better loot.
    quality_bonus = min(0.5, max(0.0, (level - 1) / 198.0))
    roll = min(99.999999, random.random() * 100.0 + quality_bonus)

    cumulative = 0.0
    for rarity in RARITIES:
        cumulative += table[rarity]
        if roll < cumulative:
            return rarity
    return "legendary"


def _upgrade_damage_dice(expression: str, rarity: str) -> str:
    cleaned = str(expression or "1d4").replace(" ", "").lower()
    if cleaned not in DICE_LADDER:
        match = re.fullmatch(r"(\d+)d(\d+)", cleaned)
        if not match:
            return cleaned
        count, sides = int(match.group(1)), int(match.group(2))
        # Pick nearest expected-damage rung if the AI generated an unusual die.
        expected = count * (sides + 1) / 2.0
        nearest = min(
            range(len(DICE_LADDER)),
            key=lambda i: abs(_expected_damage(DICE_LADDER[i]) - expected),
        )
    else:
        nearest = DICE_LADDER.index(cleaned)
    target = min(len(DICE_LADDER) - 1, nearest + RARITY_DICE_STEPS[rarity])
    return DICE_LADDER[target]


def _expected_damage(expression: str) -> float:
    match = re.fullmatch(r"(\d+)d(\d+)", expression)
    if not match:
        return 0.0
    count, sides = int(match.group(1)), int(match.group(2))
    return count * (sides + 1) / 2.0


def scale_item_for_rarity(raw_item: Dict, rarity: str) -> Dict:
    """Apply real mechanical differences between rarity tiers."""
    item = raw_item
    rarity = rarity if rarity in RARITIES else "common"
    kind = str(item.get("type") or "misc").strip().lower()
    multiplier = RARITY_POWER_MULTIPLIER[rarity]

    item["rarity"] = rarity

    if kind == "weapon" and item.get("damage"):
        item["damage"] = _upgrade_damage_dice(str(item.get("damage")), rarity)

    elif kind == "shield":
        base = max(1, _safe_int(item.get("shield", item.get("max_shield_hp", 1)), 1))
        scaled = max(1, round(base * multiplier))
        item["shield"] = scaled
        item["max_shield_hp"] = scaled

    elif kind == "armor":
        base = max(1, _safe_int(item.get("max_armor_hp", item.get("armor_hp", 1)), 1))
        scaled = max(1, round(base * multiplier))
        current = max(0, _safe_int(item.get("armor_hp", base), base))
        ratio = min(1.0, current / base) if base else 1.0
        item["max_armor_hp"] = scaled
        item["armor_hp"] = max(0, round(scaled * ratio))
        bonus = item.get("stat_bonus") if isinstance(item.get("stat_bonus"), dict) else None
        if bonus:
            caps = {"common": 1, "uncommon": 1, "rare": 2, "epic": 2, "legendary": 3}
            bonus["amount"] = max(1, min(caps[rarity], _safe_int(bonus.get("amount"), 1)))

    elif kind == "consumable" and item.get("healing"):
        item["healing"] = _upgrade_damage_dice(str(item.get("healing")), rarity)

    base_value = max(0, _safe_int(item.get("sell_value", 0), 0))
    if base_value > 0:
        item["sell_value"] = max(1, round(base_value * RARITY_SELL_MULTIPLIER[rarity]))

    return item


def finalize_loot_result(result: Dict, context: Dict) -> Dict:
    """Override AI-chosen rarity with Python-owned rarity and power scaling."""
    if not isinstance(result, dict):
        return result
    state_changes = result.get("state_changes")
    if not isinstance(state_changes, list):
        return result

    game_state = context.get("game_state") if isinstance(context, dict) else {}
    player = game_state.get("player", {}) if isinstance(game_state, dict) else {}
    player_level = _safe_int(player.get("level", 1), 1) if isinstance(player, dict) else 1

    rolled_items = []
    for change in state_changes:
        if not isinstance(change, dict) or str(change.get("type") or "").lower() != "add_inventory_item":
            continue
        item = change.get("item")
        if not isinstance(item, dict):
            continue
        loot_tier = item.pop("loot_tier", item.pop("source_tier", "routine"))
        rarity = roll_rarity(str(loot_tier), player_level)
        scale_item_for_rarity(item, rarity)
        rolled_items.append({"name": str(item.get("name") or "Item"), "rarity": rarity})

    if rolled_items:
        result["loot_rolls"] = rolled_items
        narration = str(result.get("narration") or "")
        # Keep player-facing rarity labels consistent when the AI wrote `Name [Rarity]`.
        for entry in rolled_items:
            name = re.escape(entry["name"])
            rarity_title = entry["rarity"].title()
            narration = re.sub(
                rf"({name}\s*)\[(?:Common|Uncommon|Rare|Epic|Legendary)\]",
                rf"\1[{rarity_title}]",
                narration,
                flags=re.IGNORECASE,
            )
        result["narration"] = narration
    return result
