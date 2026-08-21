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
            {"name": "Committed Strike", "description": "A forceful single-target attack.", "resource_cost": 10, "target": "enemy", "range": 1, "attack_attribute": "strength", "damage": "1d8"},
            {"name": "Quickstep", "description": "A burst of controlled movement.", "resource_cost": 5, "target": "self", "range": 0},
            {"name": "Focused Shot", "description": "A precise ranged attack.", "resource_cost": 10, "target": "enemy", "range": 6, "attack_attribute": "dexterity", "damage": "1d6"},
            {"name": "Arc Spark", "description": "A basic magical attack.", "resource_cost": 10, "target": "enemy", "range": 5, "attack_attribute": "magic", "damage": "1d6"},
            {"name": "Brace", "description": "Reinforce yourself against an incoming threat.", "resource_cost": 5, "target": "self", "range": 0},
            {"name": "Second Wind", "description": "A small restorative surge.", "resource_cost": 15, "target": "self", "range": 0},
        ],
        "starter_kits": [
            {"name": "Vanguard Kit", "items": ["Iron Sword", "Leather Coat", "Healing Draught"]},
            {"name": "Scout Kit", "items": ["Shortbow", "Travel Cloak", "Rope"]},
            {"name": "Mystic Kit", "items": ["Focus Rod", "Padded Robes", "Restorative Tonic"]},
        ],
        "special_equipment": [
            {"name": "Balanced Blade", "description": "A reliable starter weapon."},
            {"name": "Hunter's Bow", "description": "A light ranged weapon."},
            {"name": "Runed Focus", "description": "A simple focus for magical effects."},
            {"name": "Reinforced Buckler", "description": "A compact defensive tool."},
            {"name": "Traveler's Charm", "description": "A small class-themed keepsake."},
            {"name": "Utility Satchel", "description": "Tools for exploration and improvisation."},
        ],
    }


def _normalize_starter_ability_costs(abilities: List[Dict], max_resource: int) -> List[Dict]:
    """Force generated starter costs into the game's real resource-point scale.

    The model sometimes returns tabletop-style costs such as 1 or 2. Shattered
    Realms resources use actual point pools (10, 20, 50, etc.), so beginner
    abilities use multiples of 5 and must be affordable by the confirmed build.
    """
    normalized: List[Dict] = []
    for raw in abilities:
        ability = deepcopy(raw) if isinstance(raw, dict) else {}
        raw_cost = max(0, int(ability.get("resource_cost", 0) or 0))
        if max_resource <= 0:
            cost = 0
        else:
            # Treat accidental 1/2/3 style costs as 5/10/15 resource points.
            if 1 <= raw_cost <= 3:
                raw_cost *= 5
            if raw_cost <= 0:
                raw_cost = 5
            # Starter costs live on 5-point increments and cannot exceed the pool.
            cost = max(5, int(round(raw_cost / 5.0)) * 5)
            cost = min(cost, max_resource)
        ability["resource_cost"] = cost
        normalized.append(ability)
    return normalized


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
Generate exactly 6 beginner abilities. They must be meaningfully different and suitable for the generated class.
Each ability needs name, description, resource_cost, target, range, and may include attack_attribute and damage.
RESOURCE COSTS ARE REAL RESOURCE POINTS, NOT 1/2/3 tabletop slots. Costs must be multiples of 5. Beginner abilities should normally cost 5, 10, or 15 resource points and should be affordable with the character's confirmed maximum resource. Do not output costs of 1, 2, or 3.
attack_attribute may be strength, dexterity, or magic when an attack roll is appropriate.
Generate exactly 3 starter kits, each with a name and 3-4 ordinary starter items.
Generate exactly 6 special starter equipment choices, each with name and description.
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
    for index, stat in enumerate(ATTRIBUTE_NAMES):
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
    """Show the important values produced by the confirmed attributes."""
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


def run_character_creation(game_master) -> Dict:
    """Run the current CLI character creator and persist the finished character."""
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
        print(f"{i}. {ability.get('name')} — {ability.get('description')} (Cost {ability.get('resource_cost', 0)} {resource_name})")
    chosen_abilities = _choose_many(abilities, 2, "Choose 2 ability numbers (example 1,4): ")

    kits = package["starter_kits"]
    print("\nSTARTER KITS — choose 1")
    for i, kit in enumerate(kits, 1):
        print(f"{i}. {kit.get('name')} — {', '.join(str(x) for x in kit.get('items', []))}")
    chosen_kit = _choose_one(kits, "Choose a kit: ")

    equipment = package["special_equipment"]
    print("\nSPECIAL STARTER EQUIPMENT — choose 2")
    for i, item in enumerate(equipment, 1):
        print(f"{i}. {item.get('name')} — {item.get('description')}")
    chosen_equipment = _choose_many(equipment, 2, "Choose 2 equipment numbers: ")

    sheet = character_sheet_channels(stats, level=1)
    player = game_master.state.data.setdefault("player", {})
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
        "inventory": deepcopy(chosen_kit.get("items", [])) + deepcopy(chosen_equipment),
        "special_starting_equipment": deepcopy(chosen_equipment),
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
    print("  Chosen Abilities:        " + ", ".join(str(a.get("name")) for a in chosen_abilities))
    print("  Starter Kit:             " + str(chosen_kit.get("name")))
    print("  Special Equipment:       " + ", ".join(str(i.get("name")) for i in chosen_equipment))

    opening_context = {
        "player_action": "Begin the adventure with an opening scene for this newly completed character.",
        "game_state": game_master.state.snapshot(),
        "relevant_memories": [],
        "relevant_rules": [],
    }
    opening = game_master.provider.respond(opening_context)
    narration = str(opening.get("narration") or "Your adventure begins.")
    return {"player": deepcopy(player), "narration": narration, "package": package}
