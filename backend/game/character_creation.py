"""Interactive character creation for The Shattered Realms prototype.

Flow:
name + appearance -> allocate 42 AP -> AI generates class/backstory/resource
-> choose 2 of 6 abilities -> choose 1 of 3 starter kits -> choose 2 of 6
special starter items -> save character -> begin adventure.
"""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Dict, List

from .attributes import (
    ATTRIBUTE_NAMES,
    STARTING_ATTRIBUTE_POINTS,
    character_sheet_channels,
    normalize_attributes,
    validate_allocation,
)
from .resources import resource_key


def _fallback_generation(name: str, appearance: str, stats: Dict[str, int]) -> Dict:
    """Playable offline fallback when the live AI provider is unavailable."""
    strongest = sorted(stats.items(), key=lambda item: item[1], reverse=True)[:3]
    focus = ", ".join(label.title() for label, _ in strongest)
    return {
        "class_name": "Wanderborn Adept",
        "resource_name": "Resolve",
        "backstory": (
            f"{name} grew up far from the great courts and learned to survive by relying on "
            f"{focus}. A recent unexplained event forced them onto the road, where the first "
            "threads of a much larger conflict are beginning to gather."
        ),
        "abilities": [
            {"name": "Committed Strike", "description": "A forceful single-target attack.", "resource_cost": 10, "target": "enemy", "range": 1, "attack_attribute": "strength", "damage": "1d6"},
            {"name": "Quickstep", "description": "A short burst of controlled movement.", "resource_cost": 5, "target": "self", "range": 0, "movement_squares": 2},
            {"name": "Focused Shot", "description": "A precise ranged attack.", "resource_cost": 10, "target": "enemy", "range": 5, "attack_attribute": "dexterity", "damage": "1d6"},
            {"name": "Arc Spark", "description": "A small magical projectile.", "resource_cost": 10, "target": "enemy", "range": 4, "attack_attribute": "magic", "damage": "1d6"},
            {"name": "Brace", "description": "Reinforce yourself against an incoming threat.", "resource_cost": 5, "target": "self", "range": 0, "shield": 4},
            {"name": "Second Wind", "description": "A small restorative surge.", "resource_cost": 15, "target": "self", "range": 0, "healing": "1d6"},
        ],
        "starter_kits": [
            {"name": "Vanguard Kit", "items": [
                {"name": "Worn Iron Sword", "type": "weapon", "description": "A plain starter sword.", "damage": "1d6", "resource_cost": 0, "range": 1, "attack_attribute": "strength"},
                {"name": "Leather Coat", "type": "armor", "description": "Simple light protection.", "armor_bonus": 1},
                {"name": "Healing Draught", "type": "consumable", "description": "Restores a small amount of health.", "healing": "1d6"},
            ]},
            {"name": "Scout Kit", "items": [
                {"name": "Simple Shortbow", "type": "weapon", "description": "A modest starter bow.", "damage": "1d4", "resource_cost": 0, "range": 5, "attack_attribute": "dexterity"},
                {"name": "Travel Cloak", "type": "armor", "description": "Light protection for the road.", "armor_bonus": 1},
                {"name": "Rope", "type": "utility", "description": "Useful for climbing and traversal."},
            ]},
            {"name": "Mystic Kit", "items": [
                {"name": "Cracked Focus Rod", "type": "weapon", "description": "A weak magical focus.", "damage": "1d4", "resource_cost": 5, "range": 4, "attack_attribute": "magic"},
                {"name": "Padded Robes", "type": "armor", "description": "Basic protective robes.", "armor_bonus": 1},
                {"name": "Restorative Tonic", "type": "consumable", "description": "Restores a small amount of health.", "healing": "1d6"},
            ]},
        ],
        "special_equipment": [
            {"name": "Balanced Knife", "type": "weapon", "description": "A quick but weak backup blade.", "damage": "1d4", "resource_cost": 0, "range": 1, "attack_attribute": "dexterity"},
            {"name": "Hunter's Sling", "type": "weapon", "description": "A simple ranged backup weapon.", "damage": "1d4", "resource_cost": 0, "range": 4, "attack_attribute": "dexterity"},
            {"name": "Faded Runestone", "type": "focus", "description": "A minor magical focus.", "effect": "+1 to one Magic-based check when specifically invoked by a valid effect."},
            {"name": "Reinforced Buckler", "type": "shield", "description": "A compact defensive tool.", "armor_bonus": 1},
            {"name": "Traveler's Charm", "type": "accessory", "description": "A small class-themed keepsake.", "effect": "No combat bonus; story utility only."},
            {"name": "Utility Satchel", "type": "utility", "description": "Tools for exploration and improvisation.", "effect": "Contains basic rope, chalk, flint, and simple hand tools."},
        ],
    }


def _normalize_starter_ability_costs(abilities: List[Dict], max_resource: int) -> List[Dict]:
    """Normalize starter ability costs to the real resource-point scale.

    Starter abilities are intentionally low-tier and should normally be usable by
    the new character. The wider game may still contain abilities whose resource
    costs exceed the player's current or maximum resource; those may be unlocked
    and equipped but cannot be activated until the requirement can actually be paid.
    """
    normalized: List[Dict] = []
    for raw in abilities:
        ability = deepcopy(raw) if isinstance(raw, dict) else {}
        raw_cost = max(0, int(ability.get("resource_cost", 0) or 0))
        if max_resource <= 0:
            cost = 0
        else:
            if 1 <= raw_cost <= 3:
                raw_cost *= 5
            if raw_cost <= 0:
                raw_cost = 5
            cost = max(5, int(round(raw_cost / 5.0)) * 5)
            # Character-creation abilities are beginner-tier, so keep them usable.
            cost = min(cost, max_resource)
        ability["resource_cost"] = cost
        normalized.append(ability)
    return normalized


def _effect_text(entry: Dict, resource_name: str | None = None) -> str:
    """Return exact mechanical information for an ability or item."""
    parts: List[str] = []
    damage = entry.get("damage")
    healing = entry.get("healing")
    shield = entry.get("shield")
    movement = entry.get("movement_squares")
    armor = entry.get("armor_bonus")
    range_value = entry.get("range")
    resource_cost = entry.get("resource_cost")
    effect = entry.get("effect")

    if damage not in {None, "", "0", 0}:
        parts.append(f"Damage {damage}")
    if healing not in {None, "", "0", 0}:
        parts.append(f"Healing {healing}")
    if shield not in {None, "", "0", 0}:
        parts.append(f"Shield {shield}")
    if movement not in {None, "", "0", 0}:
        parts.append(f"Move {movement} squares")
    if armor not in {None, "", "0", 0}:
        parts.append(f"Armor +{armor}")
    if range_value is not None and entry.get("type") in {"weapon", "active", None}:
        parts.append(f"Range {range_value}")
    if resource_cost is not None:
        label = resource_name or "Resource"
        parts.append(f"Cost {int(resource_cost or 0)} {label}")
    if effect:
        parts.append(str(effect))
    return " | ".join(parts) if parts else "No numeric combat effect"


def generate_character_package(provider, *, name: str, appearance: str, stats: Dict[str, int]) -> Dict:
    """Ask the live model for a strictly structured character package."""
    client = getattr(provider, "client", None)
    model = getattr(provider, "model", None)
    sheet = character_sheet_channels(stats, level=1)
    max_resource = int(sheet["max_resource_base"])
    if client is None or not model:
        generated = _fallback_generation(name, appearance, stats)
        generated["abilities"] = _normalize_starter_ability_costs(generated["abilities"], max_resource)
        return generated

    instructions = """You generate starting characters for The Shattered Realms.
Return ONLY valid JSON. Do not include markdown.
Use the player's exact name and appearance as fixed canon. Do not rewrite or contradict them.
Use the confirmed 13-stat build to inspire, but not mechanically alter, the character.
Generate a unique beginner-friendly class, a thematic class-resource name, and a backstory.

Generate exactly 6 BEGINNER abilities. Starter abilities must be intentionally weaker than mid/late-game abilities. Stronger abilities later in progression should have stronger effects and usually higher resource costs.
Every ability must state exact mechanics, not vague prose. Include name, description, resource_cost, target, range, and the exact effect fields that apply. Offensive abilities need damage such as 1d4, 1d6, or another explicit expression. Movement abilities need movement_squares. Healing abilities need healing. Shield abilities need shield. Buff/debuff/utility abilities need an explicit effect string with exact values/duration when relevant.
RESOURCE COSTS ARE REAL RESOURCE POINTS. Costs use multiples of 5. Beginner abilities normally cost 5, 10, or 15 resource and should be affordable by this starting character. Do not output 1/2/3 slot-style costs.
attack_attribute may be strength, dexterity, or magic when an attack roll is appropriate.

Generate exactly 3 starter kits, each with a name and 3-4 structured item objects. Starter weapons must be deliberately weak early-game weapons. Every weapon item MUST contain type='weapon', description, damage, resource_cost, range, and attack_attribute. Weapon attacks may cost 0 or a small amount of class resource at the beginning. Stronger weapons acquired later should generally deal more damage or have stronger effects and may cost more resource per attack.
Non-weapon items must also state their exact mechanical effect when they have one, such as armor_bonus, healing, movement_squares, or effect.

Generate exactly 6 special starter equipment choices as structured item objects with name, type, description, and exact mechanical fields whenever applicable.
Do not give permanent stat increases in starter equipment.
Top-level JSON keys: class_name, resource_name, backstory, abilities, starter_kits, special_equipment."""
    payload = {
        "name": name,
        "appearance": appearance,
        "confirmed_stats": stats,
        "derived_character_values": {
            "max_hp": int(sheet["max_health_base"]),
            "max_resource": max_resource,
            "resource_regeneration_per_round": int(sheet["resource_regeneration_per_round"]),
            "movement": int(sheet["movement"]),
            "initiative_bonus": int(sheet["initiative_bonus"]),
            "critical_chance_percent": int(sheet["critical_chance_percent"]),
        },
    }
    response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, indent=2))
    raw = response.output_text.strip()
    try:
        generated = json.loads(raw)
    except json.JSONDecodeError:
        generated = _fallback_generation(name, appearance, stats)

    if not isinstance(generated, dict):
        generated = _fallback_generation(name, appearance, stats)
    if len(generated.get("abilities", [])) != 6 or len(generated.get("starter_kits", [])) != 3 or len(generated.get("special_equipment", [])) != 6:
        generated = _fallback_generation(name, appearance, stats)
    generated["abilities"] = _normalize_starter_ability_costs(generated.get("abilities", []), max_resource)
    return generated


def _choose_many(options: List[Dict], count: int, prompt: str) -> List[Dict]:
    while True:
        raw = input(prompt).strip()
        try:
            indexes = [int(part.strip()) - 1 for part in raw.split(",")]
        except ValueError:
            indexes = []
        if len(indexes) == count and len(set(indexes)) == count and all(0 <= i < len(options) for i in indexes):
            return [deepcopy(options[i]) for i in indexes]
        print(f"Choose exactly {count} different numbers from 1-{len(options)}.")


def _choose_one(options: List[Dict], prompt: str) -> Dict:
    while True:
        raw = input(prompt).strip()
        try:
            index = int(raw) - 1
        except ValueError:
            index = -1
        if 0 <= index < len(options):
            return deepcopy(options[index])
        print(f"Choose a number from 1-{len(options)}.")


def _allocate_attributes() -> Dict[str, int]:
    """Collect an exact 42-point allocation one stat at a time."""
    remaining = STARTING_ATTRIBUTE_POINTS
    allocation: Dict[str, int] = {}
    print(f"\nYou have {STARTING_ATTRIBUTE_POINTS} AP to spend across {len(ATTRIBUTE_NAMES)} stats.")
    print("Each stat has a natural cap of 100. You must spend all starting AP before confirming.\n")
    for stat in ATTRIBUTE_NAMES:
        while True:
            raw = input(f"{stat.title()} (remaining AP: {remaining}): ").strip()
            try:
                value = int(raw)
            except ValueError:
                value = -1
            if 0 <= value <= min(100, remaining):
                allocation[stat] = value
                remaining -= value
                break
            print(f"Enter a whole number from 0 to {min(100, remaining)}.")
    if remaining:
        print(f"\nYou still have {remaining} AP. Add the remainder to any stats before confirming.")
        while remaining > 0:
            stat = input("Stat to increase: ").strip().lower()
            if stat not in allocation:
                print("Unknown stat.")
                continue
            raw = input(f"How many points? (remaining {remaining}): ").strip()
            try:
                amount = int(raw)
            except ValueError:
                amount = 0
            if 1 <= amount <= remaining and allocation[stat] + amount <= 100:
                allocation[stat] += amount
                remaining -= amount
            else:
                print("Invalid amount.")
    return normalize_attributes(allocation)


def _print_derived_sheet(sheet: Dict, resource_name: str = "Resource") -> None:
    print("\nDERIVED CHARACTER STATS")
    print(f"  Max HP:                  {int(sheet['max_health_base'])}")
    print(f"  Max {resource_name}:".ljust(28) + f"{int(sheet['max_resource_base'])}")
    print(f"  {resource_name} Regen/Round:".ljust(28) + f"{int(sheet['resource_regeneration_per_round'])}")
    print(f"  Movement:                {int(sheet['movement'])} squares")
    print(f"  Initiative Bonus:        +{int(sheet['initiative_bonus'])}")
    print(f"  Critical Chance:         {int(sheet['critical_chance_percent'])}%")
    print(f"  Physical Resistance:     {int(sheet['physical_resistance_percent'])}%")
    print(f"  Status Resistance:       {int(sheet['status_resistance_percent'])}%")
    print(f"  Defend Action AC Bonus:  +{int(sheet['defend_action_ac_bonus'])}")


def _print_item(item: Dict, resource_name: str) -> str:
    if not isinstance(item, dict):
        return str(item)
    name = str(item.get("name") or "Item")
    description = str(item.get("description") or "").strip()
    mechanics = _effect_text(item, resource_name)
    suffix = f" — {description}" if description else ""
    return f"{name}{suffix} [{mechanics}]"


def run_character_creation(game_master) -> Dict:
    print("\n" + "=" * 48)
    print("START NEW ADVENTURE — CHARACTER CREATION")
    print("=" * 48)
    name = input("Character name: ").strip() or "Traveler"
    appearance = input("Describe your appearance: ").strip()

    while True:
        stats = _allocate_attributes()
        validation = validate_allocation(stats, level=1)
        print("\nCHARACTER BUILD")
        for stat in ATTRIBUTE_NAMES:
            print(f"  {stat.title():<14} {stats[stat]}")
        sheet = character_sheet_channels(stats, level=1)
        _print_derived_sheet(sheet)
        confirm = input("\nConfirm this build? (yes/no): ").strip().lower()
        if confirm in {"yes", "y"} and validation["valid"] and validation["points_unspent"] == 0:
            break
        print("Rebuilding your attributes.\n")

    print("\nGenerating your class, backstory, abilities, and starting gear...")
    package = generate_character_package(game_master.provider, name=name, appearance=appearance, stats=stats)
    resource_name = str(package.get("resource_name") or "Resource").strip() or "Resource"
    print(f"\nCLASS: {package['class_name']}")
    print(f"RESOURCE: {resource_name}")
    print(f"BACKSTORY: {package['backstory']}")
    _print_derived_sheet(sheet, resource_name)

    abilities = package["abilities"]
    print(f"\nBEGINNER ABILITIES — choose 2 (Max {resource_name}: {int(sheet['max_resource_base'])})")
    for i, ability in enumerate(abilities, 1):
        print(f"{i}. {ability.get('name')} — {ability.get('description')} [{_effect_text(ability, resource_name)}]")
    chosen_abilities = _choose_many(abilities, 2, "Choose 2 ability numbers (example 1,4): ")

    kits = package["starter_kits"]
    print("\nSTARTER KITS — choose 1")
    for i, kit in enumerate(kits, 1):
        item_text = "; ".join(_print_item(item, resource_name) for item in kit.get("items", []))
        print(f"{i}. {kit.get('name')} — {item_text}")
    chosen_kit = _choose_one(kits, "Choose a kit: ")

    equipment = package["special_equipment"]
    print("\nSPECIAL STARTER EQUIPMENT — choose 2")
    for i, item in enumerate(equipment, 1):
        print(f"{i}. {_print_item(item, resource_name)}")
    chosen_equipment = _choose_many(equipment, 2, "Choose 2 equipment numbers: ")

    sheet = character_sheet_channels(stats, level=1)
    player = game_master.state.data.setdefault("player", {})
    kit_items = deepcopy(chosen_kit.get("items", []))
    all_items = kit_items + deepcopy(chosen_equipment)
    starter_weapon = next((item for item in all_items if isinstance(item, dict) and item.get("type") == "weapon"), None)

    player.update({
        "name": name,
        "appearance": appearance,
        "level": 1,
        "xp_orbs": 0,
        "class": str(package.get("class_name") or "Unassigned"),
        "background": str(package.get("backstory") or ""),
        "stats": stats,
        "attribute_points_unspent": 0,
        "hp": sheet["max_health_base"],
        "max_hp": sheet["max_health_base"],
        "resource_name": resource_name,
        "resource_type": resource_key(resource_name),
        "resource": sheet["max_resource_base"],
        "max_resource": sheet["max_resource_base"],
        "resource_regeneration_per_round": sheet["resource_regeneration_per_round"],
        "mana": sheet["max_resource_base"],
        "max_mana": sheet["max_resource_base"],
        "initiative_bonus": sheet["initiative_bonus"],
        "movement": sheet["movement"],
        "critical_chance_percent": sheet["critical_chance_percent"],
        "physical_resistance_percent": sheet["physical_resistance_percent"],
        "status_resistance_percent": sheet["status_resistance_percent"],
        "defend_action_ac_bonus": sheet["defend_action_ac_bonus"],
        "unlocked_abilities": deepcopy(chosen_abilities),
        "equipped_abilities": deepcopy(chosen_abilities),
        "starter_kit": deepcopy(chosen_kit),
        "inventory": all_items,
        "special_starting_equipment": deepcopy(chosen_equipment),
        "equipped_weapon": deepcopy(starter_weapon),
        "damage": str(starter_weapon.get("damage", "1d4")) if starter_weapon else "1d4",
        "character_creation_complete": True,
    })
    game_master.state.data["combat"] = {"active": False}
    game_master.state.data["encounter_template"] = {}
    game_master.state.data["pending_encounter_enemies"] = []
    game_master.state.data["encounter_reset_pending"] = False
    game_master.state.data["campaign_status"] = "active"
    game_master.state.save()

    print("\nFINAL CHARACTER SUMMARY")
    print(f"  {name} — {player['class']}")
    _print_derived_sheet(sheet, resource_name)
    print("  Chosen Abilities:")
    for ability in chosen_abilities:
        print(f"    - {ability.get('name')}: {_effect_text(ability, resource_name)}")
    print("  Starter Kit:             " + str(chosen_kit.get("name")))
    if starter_weapon:
        print("  Starting Weapon:         " + _print_item(starter_weapon, resource_name))
    print("  Special Equipment:")
    for item in chosen_equipment:
        print("    - " + _print_item(item, resource_name))

    opening_context = {
        "player_action": "Begin the adventure with an opening scene for this newly completed character.",
        "game_state": game_master.state.snapshot(),
        "relevant_memories": [],
        "relevant_rules": [],
    }
    opening = game_master.provider.respond(opening_context)
    narration = str(opening.get("narration") or "Your adventure begins.")
    return {"player": deepcopy(player), "narration": narration, "package": package}
