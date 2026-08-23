"""Interactive character creation for The Shattered Realms prototype."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Dict, List

from .attributes import (
    ATTRIBUTE_NAMES,
    STARTING_SKILL_POINTS,
    character_sheet_channels,
    normalize_attributes,
    validate_allocation,
)
from .dice import normalize_damage_expression
from .economy import currency_profile, format_money
from .progression import ABILITY_TIER_COSTS, xp_required_for_next_level
from .resources import resource_key


def _starter_ability(ability: Dict) -> Dict:
    result = deepcopy(ability)
    result["tier"] = "beginner"
    result["ability_point_cost"] = ABILITY_TIER_COSTS["beginner"]
    return result


def _fallback_generation(name: str, appearance: str, stats: Dict[str, int]) -> Dict:
    strongest = sorted(stats.items(), key=lambda item: item[1], reverse=True)[:3]
    focus = ", ".join(label.title() for label, _ in strongest)
    return {
        "class_name": "Wanderborn Adept",
        "resource_name": "Resolve",
        "backstory": f"{name} grew up far from the great courts and learned to survive through {focus}. A recent unexplained event forced them onto the road.",
        "abilities": [
            _starter_ability({"name": "Committed Strike", "description": "A forceful single-target attack.", "resource_cost": 10, "target": "enemy", "range": 1, "attack_attribute": "strength", "damage": "1d6"}),
            _starter_ability({"name": "Quickstep", "description": "A short burst of controlled movement.", "resource_cost": 5, "target": "self", "range": 0, "movement_squares": 2}),
            _starter_ability({"name": "Focused Shot", "description": "A precise ranged attack.", "resource_cost": 10, "target": "enemy", "range": 5, "attack_attribute": "dexterity", "damage": "1d6"}),
            _starter_ability({"name": "Arc Spark", "description": "A small magical projectile.", "resource_cost": 10, "target": "enemy", "range": 4, "attack_attribute": "magic", "damage": "1d6"}),
            _starter_ability({"name": "Brace", "description": "Reinforce yourself against an incoming threat.", "resource_cost": 5, "target": "self", "range": 0, "shield": 4}),
            _starter_ability({"name": "Second Wind", "description": "A small restorative surge.", "resource_cost": 15, "target": "self", "range": 0, "healing": "1d6"}),
        ],
        "starter_kits": [
            {"name": "Vanguard Kit", "starting_currency": 15, "items": [
                {"name": "Worn Iron Sword", "type": "weapon", "description": "A plain starter sword.", "damage": "1d6", "range": 1, "attack_attribute": "strength"},
                {"name": "Leather Coat", "type": "armor", "description": "Simple light protection.", "armor_bonus": 1},
                {"name": "Healing Draught", "type": "consumable", "description": "Restores a small amount of health.", "healing": "1d6"},
            ]},
            {"name": "Scout Kit", "starting_currency": 25, "items": [
                {"name": "Simple Shortbow", "type": "weapon", "description": "A modest starter bow.", "damage": "1d4", "range": 5, "attack_attribute": "dexterity"},
                {"name": "Travel Cloak", "type": "armor", "description": "Light protection for the road.", "armor_bonus": 1},
                {"name": "Rope", "type": "utility", "description": "Useful for climbing and traversal."},
            ]},
            {"name": "Mystic Kit", "starting_currency": 20, "items": [
                {"name": "Cracked Focus Rod", "type": "weapon", "description": "A weak magical focus.", "damage": "1d4", "range": 4, "attack_attribute": "magic"},
                {"name": "Padded Robes", "type": "armor", "description": "Basic protective robes.", "armor_bonus": 1},
                {"name": "Restorative Tonic", "type": "consumable", "description": "Restores a small amount of health.", "healing": "1d6"},
            ]},
        ],
        "special_equipment": [
            {"name": "Balanced Knife", "type": "weapon", "description": "A quick but weak backup blade.", "damage": "1d4", "range": 1, "attack_attribute": "dexterity"},
            {"name": "Hunter's Sling", "type": "weapon", "description": "A simple ranged backup weapon.", "damage": "1d4", "range": 4, "attack_attribute": "dexterity"},
            {"name": "Faded Runestone", "type": "focus", "description": "A minor magical focus.", "effect": "+1 to one Magic-based check when specifically invoked by a valid effect."},
            {"name": "Reinforced Buckler", "type": "shield", "description": "A compact defensive tool.", "shield": 4},
            {"name": "Traveler's Charm", "type": "accessory", "description": "A small class-themed keepsake.", "effect": "Story utility only."},
            {"name": "Utility Satchel", "type": "utility", "description": "Tools for exploration and improvisation.", "effect": "Contains basic rope, chalk, flint, and simple hand tools."},
        ],
    }


def _normalize_starter_abilities(abilities: List[Dict]) -> List[Dict]:
    normalized = []
    for raw in abilities:
        ability = deepcopy(raw) if isinstance(raw, dict) else {}
        cost = max(5, int(ability.get("resource_cost", 5) or 5))
        if 1 <= cost <= 3:
            cost *= 5
        cost = max(5, int(round(cost / 5.0)) * 5)
        ability["resource_cost"] = cost
        ability["tier"] = "beginner"
        ability["ability_point_cost"] = 1
        if ability.get("damage") not in {None, "", "0", 0}:
            ability["damage"] = normalize_damage_expression(ability.get("damage"), "1d4")
        if ability.get("healing") not in {None, "", "0", 0}:
            ability["healing"] = normalize_damage_expression(ability.get("healing"), "1d4")
        normalized.append(ability)
    return normalized


def _normalize_items(items: List[Dict]) -> List[Dict]:
    """Normalize generated item mechanics before display/storage."""
    normalized: List[Dict] = []
    for raw in items:
        item = deepcopy(raw) if isinstance(raw, dict) else {}
        if item.get("damage") not in {None, "", "0", 0}:
            item["damage"] = normalize_damage_expression(item.get("damage"), "1d4")
        if item.get("healing") not in {None, "", "0", 0}:
            item["healing"] = normalize_damage_expression(item.get("healing"), "1d4")
        item_type = str(item.get("type") or "").strip().lower()
        if item_type == "weapon":
            item.pop("resource_cost", None)
        if item_type == "shield":
            try:
                shield_hp = int(item.get("shield", 4) or 4)
            except (TypeError, ValueError):
                shield_hp = 4
            item["shield"] = max(3, min(5, shield_hp))
            item.pop("resource_cost", None)
            item.pop("armor_bonus", None)
        normalized.append(item)
    return normalized


def _normalize_generated_equipment(package: Dict) -> Dict:
    result = deepcopy(package)
    kits = []
    fallback_money = (15, 25, 20)
    for index, raw_kit in enumerate(result.get("starter_kits", [])):
        kit = deepcopy(raw_kit) if isinstance(raw_kit, dict) else {}
        kit["items"] = _normalize_items(kit.get("items", []))
        try:
            starting_currency = int(kit.get("starting_currency", fallback_money[index] if index < len(fallback_money) else 20) or 20)
        except (TypeError, ValueError):
            starting_currency = fallback_money[index] if index < len(fallback_money) else 20
        # Starter money should matter, but it should not overwhelm the early economy.
        kit["starting_currency"] = max(10, min(30, starting_currency))
        kits.append(kit)
    result["starter_kits"] = kits
    result["special_equipment"] = _normalize_items(result.get("special_equipment", []))
    return result


def _effect_text(entry: Dict, resource_name: str | None = None) -> str:
    parts: List[str] = []
    if entry.get("damage") not in {None, "", "0", 0}: parts.append(f"Damage {normalize_damage_expression(entry['damage'], '1d4')}")
    if entry.get("healing") not in {None, "", "0", 0}: parts.append(f"Healing {normalize_damage_expression(entry['healing'], '1d4')}")
    if entry.get("shield") not in {None, "", "0", 0}: parts.append(f"Shield HP {entry['shield']}")
    if entry.get("movement_squares") not in {None, "", "0", 0}: parts.append(f"Move {entry['movement_squares']} squares")
    if entry.get("armor_bonus") not in {None, "", "0", 0}: parts.append(f"Armor +{entry['armor_bonus']}")
    if entry.get("range") is not None and entry.get("type") in {"weapon", "active", None}: parts.append(f"Range {entry['range']}")
    if entry.get("resource_cost") is not None and str(entry.get("type") or "").strip().lower() != "weapon":
        parts.append(f"Cost {int(entry.get('resource_cost', 0) or 0)} {resource_name or 'Resource'}")
    if entry.get("tier"):
        tier = str(entry["tier"]).title()
        parts.append(f"{tier} ({int(entry.get('ability_point_cost', ABILITY_TIER_COSTS.get(str(entry['tier']).lower(), 1)))} AP)")
    if entry.get("effect"): parts.append(str(entry["effect"]))
    return " | ".join(parts) if parts else "No numeric combat effect"


def generate_character_package(provider, *, name: str, appearance: str, stats: Dict[str, int]) -> Dict:
    client = getattr(provider, "client", None)
    model = getattr(provider, "model", None)
    sheet = character_sheet_channels(stats, level=1)
    max_resource = int(sheet["max_resource_base"])
    if client is None or not model:
        generated = _fallback_generation(name, appearance, stats)
        generated["abilities"] = _normalize_starter_abilities(generated["abilities"])
        return _normalize_generated_equipment(generated)

    instructions = """You generate starting characters for The Shattered Realms. Return ONLY valid JSON.
Use the player's exact name and appearance as fixed canon. Use the confirmed 13-stat build to inspire but never alter the build.
Generate a unique beginner-friendly class, thematic resource name, and backstory.
Generate exactly 6 BEGINNER abilities. Every starter ability has tier='beginner' and ability_point_cost=1. Character-creation ability choices are granted as part of the starting package, so the player does not spend AP for the two chosen starters.
Every ability must have exact mechanics: name, description, resource_cost, target, range and exact applicable fields such as damage, healing, movement_squares, shield, duration, target_count, or effect. Damage and healing MUST use dice notation such as 1d4, 1d6, 1d8, or 2d6, never fixed totals such as 4 or 6. Resource costs are real points in multiples of 5. Do NOT reduce costs to 0 just because the character has 0 or low maximum Resource. A player may choose an ability they cannot currently afford; it remains unusable until Resource is raised.
Starter abilities must be weak compared with later Novice/Expert/Master/Legendary abilities.
Generate exactly 3 starter kits with 3-4 structured item objects. EACH starter kit must also include integer starting_currency between 10 and 30. Around 20 is the normal baseline. Balance it against the kit: a gear-heavy/combat-heavy kit can start with less money, while a lighter/trader/scout/resourceful kit can start with more. The number represents units of the confirmed world's currency, whatever that currency is; never hardcode the word gold, dollars, or credits into the number.
Starter weapons are weak and must include type='weapon', description, dice-based damage, range, and attack_attribute. Weapon damage MUST be a dice expression, never a fixed total. WEAPONS DO NOT USE CLASS RESOURCE AND MUST NOT HAVE resource_cost. Basic weapon attacks never consume Mana, Stamina, Rage, Focus, or any other class Resource. Resource costs belong to abilities only.
Generate exactly 6 special starter equipment options as structured objects with exact mechanics when applicable. Any item with type='weapon' must also have dice-based damage and no resource_cost. Any item with type='shield' MUST include integer shield between 3 and 5. This is its Beginner Shield HP. Shields do not use class Resource and must not have resource_cost or armor_bonus. Shield HP is a separate defensive pool, not AC and not Armor HP. Do not grant permanent stat increases.
Top-level keys: class_name, resource_name, backstory, abilities, starter_kits, special_equipment. Each starter_kits entry must contain name, starting_currency, and items."""
    payload = {"name": name, "appearance": appearance, "confirmed_stats": stats,
               "derived": {"max_hp": sheet["max_health_base"], "max_resource": max_resource,
                           "resource_regen": sheet["resource_regeneration_per_round"], "movement": sheet["movement"]}}
    response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, indent=2))
    try:
        generated = json.loads(response.output_text.strip())
    except json.JSONDecodeError:
        generated = _fallback_generation(name, appearance, stats)
    if not isinstance(generated, dict) or len(generated.get("abilities", [])) != 6 or len(generated.get("starter_kits", [])) != 3 or len(generated.get("special_equipment", [])) != 6:
        generated = _fallback_generation(name, appearance, stats)
    generated["abilities"] = _normalize_starter_abilities(generated.get("abilities", []))
    return _normalize_generated_equipment(generated)


def _choose_many(options: List[Dict], count: int, prompt: str) -> List[Dict]:
    while True:
        try: indexes = [int(part.strip()) - 1 for part in input(prompt).strip().split(",")]
        except ValueError: indexes = []
        if len(indexes) == count and len(set(indexes)) == count and all(0 <= i < len(options) for i in indexes):
            return [deepcopy(options[i]) for i in indexes]
        print(f"Choose exactly {count} different numbers from 1-{len(options)}.")


def _choose_one(options: List[Dict], prompt: str) -> Dict:
    while True:
        try: index = int(input(prompt).strip()) - 1
        except ValueError: index = -1
        if 0 <= index < len(options): return deepcopy(options[index])
        print(f"Choose a number from 1-{len(options)}.")


def _allocate_stats() -> Dict[str, int]:
    remaining = STARTING_SKILL_POINTS
    allocation: Dict[str, int] = {}
    print(f"\nYou have {STARTING_SKILL_POINTS} SP to spend across {len(ATTRIBUTE_NAMES)} stats.")
    print("SP = Skill Points. AP = Ability Points. Each stat has a natural cap of 100.\n")
    for stat in ATTRIBUTE_NAMES:
        while True:
            raw = input(f"{stat.title()} (remaining SP: {remaining}): ").strip()
            try: value = int(raw)
            except ValueError: value = -1
            if 0 <= value <= min(100, remaining):
                allocation[stat] = value; remaining -= value; break
            print(f"Enter a whole number from 0 to {min(100, remaining)}.")
    while remaining > 0:
        print(f"\nYou still have {remaining} SP. Spend all starting SP before confirming.")
        stat = input("Stat to increase: ").strip().lower()
        if stat not in allocation:
            print("Unknown stat."); continue
        try: amount = int(input(f"How many SP? (remaining {remaining}): ").strip())
        except ValueError: amount = 0
        if 1 <= amount <= remaining and allocation[stat] + amount <= 100:
            allocation[stat] += amount; remaining -= amount
        else: print("Invalid amount.")
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
    if not isinstance(item, dict): return str(item)
    description = str(item.get("description") or "").strip()
    suffix = f" — {description}" if description else ""
    return f"{item.get('name', 'Item')}{suffix} [{_effect_text(item, resource_name)}]"


def run_character_creation(game_master) -> Dict:
    print("\n" + "=" * 48)
    print("START NEW ADVENTURE — CHARACTER CREATION")
    print("=" * 48)
    name = input("Character name: ").strip() or "Traveler"
    appearance = input("Describe your appearance: ").strip()

    while True:
        stats = _allocate_stats()
        validation = validate_allocation(stats, level=1)
        print("\nCHARACTER BUILD")
        for stat in ATTRIBUTE_NAMES: print(f"  {stat.title():<14} {stats[stat]}")
        sheet = character_sheet_channels(stats, level=1)
        _print_derived_sheet(sheet)
        if input("\nConfirm this build? (yes/no): ").strip().lower() in {"yes", "y"} and validation["valid"] and validation["skill_points_unspent"] == 0:
            break
        print("Rebuilding your stats.\n")

    print("\nGenerating your class, backstory, abilities, and starting gear...")
    package = generate_character_package(game_master.provider, name=name, appearance=appearance, stats=stats)
    resource_name = str(package.get("resource_name") or "Resource").strip() or "Resource"
    world = game_master.state.data.get("world_profile", {})
    money_profile = currency_profile(world)
    print(f"\nCLASS: {package['class_name']}")
    print(f"RESOURCE: {resource_name}")
    print(f"BACKSTORY: {package['backstory']}")
    _print_derived_sheet(sheet, resource_name)

    abilities = package["abilities"]
    print(f"\nBEGINNER ABILITIES — choose 2 (Max {resource_name}: {int(sheet['max_resource_base'])})")
    print("Your two starting Beginner abilities are free character-creation grants; their normal unlock tier is shown for future progression.")
    for i, ability in enumerate(abilities, 1):
        warning = ""
        if int(ability.get("resource_cost", 0) or 0) > int(sheet["max_resource_base"]):
            warning = " [UNUSABLE NOW — raise Resource to afford this]"
        print(f"{i}. {ability.get('name')} — {ability.get('description')} [{_effect_text(ability, resource_name)}]{warning}")
    chosen_abilities = _choose_many(abilities, 2, "Choose 2 ability numbers (example 1,4): ")

    kits = package["starter_kits"]
    print("\nSTARTER KITS — choose 1")
    for i, kit in enumerate(kits, 1):
        starting_money = format_money(int(kit.get("starting_currency", 20) or 20), money_profile)
        items_text = "; ".join(_print_item(item, resource_name) for item in kit.get("items", []))
        print(f"{i}. {kit.get('name')} — Starting Money: {starting_money}; {items_text}")
    chosen_kit = _choose_one(kits, "Choose a kit: ")
    starting_money = max(10, min(30, int(chosen_kit.get("starting_currency", 20) or 20)))

    equipment = package["special_equipment"]
    print("\nSPECIAL STARTER EQUIPMENT — choose 2")
    for i, item in enumerate(equipment, 1): print(f"{i}. {_print_item(item, resource_name)}")
    chosen_equipment = _choose_many(equipment, 2, "Choose 2 equipment numbers: ")

    kit_items = deepcopy(chosen_kit.get("items", []))
    all_items = kit_items + deepcopy(chosen_equipment)
    starter_weapon = next((item for item in all_items if isinstance(item, dict) and item.get("type") == "weapon"), None)
    starter_shield = next((item for item in all_items if isinstance(item, dict) and str(item.get("type") or "").lower() == "shield"), None)
    starter_shield_hp = int(starter_shield.get("shield", 0) or 0) if starter_shield else 0
    player = game_master.state.data.setdefault("player", {})
    player.update({
        "name": name, "appearance": appearance, "level": 1, "xp_orbs": 0,
        "xp_to_next_level": xp_required_for_next_level(1), "class": str(package.get("class_name") or "Unassigned"),
        "background": str(package.get("backstory") or ""), "stats": stats,
        "skill_points_unspent": 0, "attribute_points_unspent": 0, "ability_points": 0,
        "hp": sheet["max_health_base"], "max_hp": sheet["max_health_base"],
        "resource_name": resource_name, "resource_type": resource_key(resource_name),
        "resource": sheet["max_resource_base"], "max_resource": sheet["max_resource_base"],
        "resource_regeneration_per_round": sheet["resource_regeneration_per_round"],
        "mana": sheet["max_resource_base"], "max_mana": sheet["max_resource_base"],
        "initiative_bonus": sheet["initiative_bonus"], "movement": sheet["movement"],
        "critical_chance_percent": sheet["critical_chance_percent"],
        "physical_resistance_percent": sheet["physical_resistance_percent"],
        "status_resistance_percent": sheet["status_resistance_percent"], "defend_action_ac_bonus": sheet["defend_action_ac_bonus"],
        "unlocked_abilities": deepcopy(chosen_abilities), "equipped_abilities": deepcopy(chosen_abilities),
        "starter_kit": deepcopy(chosen_kit), "inventory": all_items,
        "special_starting_equipment": deepcopy(chosen_equipment), "equipped_weapon": deepcopy(starter_weapon),
        "equipped_shield": deepcopy(starter_shield), "shield_hp": starter_shield_hp, "max_shield_hp": starter_shield_hp,
        "damage": normalize_damage_expression(starter_weapon.get("damage", "1d4"), "1d4") if starter_weapon else "1d4",
        "wallet": {"amount": starting_money, **money_profile},
        "character_creation_complete": True,
    })
    game_master.state.data.update({"combat": {"active": False}, "encounter_template": {},
                                   "pending_encounter_enemies": [], "encounter_reset_pending": False,
                                   "campaign_status": "active"})
    game_master.state.save()

    print("\nFINAL CHARACTER SUMMARY")
    print(f"  {name} — {player['class']} | Level 1 | SP 0 | AP 0 | XP 0/{player['xp_to_next_level']}")
    _print_derived_sheet(sheet, resource_name)
    print(f"  Starting Money:          {format_money(starting_money, money_profile)}")
    print("  Chosen Abilities:")
    for ability in chosen_abilities: print(f"    - {ability.get('name')}: {_effect_text(ability, resource_name)}")
    print("  Starter Kit:             " + str(chosen_kit.get("name")))
    if starter_weapon: print("  Starting Weapon:         " + _print_item(starter_weapon, resource_name))
    if starter_shield: print("  Starting Shield:         " + _print_item(starter_shield, resource_name))

    opening = game_master.provider.respond({"player_action": "Begin the adventure with an opening scene for this newly completed character.",
                                            "game_state": game_master.state.snapshot(), "relevant_memories": [], "relevant_rules": []})
    return {"player": deepcopy(player), "narration": str(opening.get("narration") or "Your adventure begins."), "package": package}