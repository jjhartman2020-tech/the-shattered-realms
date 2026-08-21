"""Optional AI-assisted starting-stat allocation for character creation."""
from __future__ import annotations

import json
import re
from typing import Dict

from .attributes import ATTRIBUTE_NAMES, STARTING_SKILL_POINTS, normalize_attributes


STAT_HELP = {
    "health": "How much punishment you can take. 1 SP = +5 Max HP.",
    "resource": "Fuel for class abilities. 1 SP = +5 Max Resource; every 3 total Resource SP = +1 Resource regenerated per round.",
    "strength": "Raw physical power, heavy melee actions, Athletics/Grappling/Might. Every 3 SP = +1 Strength check/attack accuracy; current engine also grants +1 melee damage per 6 SP.",
    "dexterity": "Aim, precision, lockpicking, pickpocketing and fine hand control. Every 3 SP = +1 Dexterity check/attack accuracy.",
    "agility": "Dodging, stealth, acrobatics and evasive movement. Every 3 SP = +1 Agility checks; every 9 SP currently adds +1 passive AC.",
    "constitution": "Toughness, endurance and resisting harmful effects. Every 3 SP = +1 Constitution checks; every 5 SP = +1% physical resistance; every 4 SP = +1% status resistance.",
    "intelligence": "Investigation, knowledge, hacking/engineering and problem solving. Every 3 SP = +1 Intelligence checks.",
    "wisdom": "Perception, insight, survival, medicine and awareness. Every 3 SP = +1 Wisdom checks.",
    "charisma": "Persuasion, deception, intimidation, performance and leadership. Every 3 SP = +1 Charisma checks/trading influence.",
    "speed": "Movement and initiative. Up to 30 Speed, 1 SP = +0.5 movement squares; after 30, 1 SP = +0.1 square. Every 3 SP = +1 initiative/check bonus.",
    "defense": "How effective your Defend action is. Every 3 SP = +1 AC while defending.",
    "luck": "Critical-hit potential and luck-based checks. Every 3 SP = +1 Luck check bonus and +1% critical chance (base crit is 5%).",
    "magic": "Spellcasting, channeling and magical/power accuracy when the world supports it. Every 3 SP = +1 Magic check/attack accuracy.",
}


def _repair_allocation(raw: Dict) -> Dict[str, int]:
    """Force an AI allocation into the legal 13-stat, exact-SP format."""
    values = {}
    for stat in ATTRIBUTE_NAMES:
        try:
            values[stat] = max(0, min(100, int(raw.get(stat, 0) or 0)))
        except (TypeError, ValueError):
            values[stat] = 0

    total = sum(values.values())
    if total == 0:
        values = {stat: STARTING_SKILL_POINTS // len(ATTRIBUTE_NAMES) for stat in ATTRIBUTE_NAMES}
        total = sum(values.values())

    if total != STARTING_SKILL_POINTS:
        scaled = {stat: int(values[stat] * STARTING_SKILL_POINTS / total) for stat in ATTRIBUTE_NAMES}
        remaining = STARTING_SKILL_POINTS - sum(scaled.values())
        priority = sorted(ATTRIBUTE_NAMES, key=lambda stat: values[stat], reverse=True)
        index = 0
        while remaining > 0:
            stat = priority[index % len(priority)]
            if scaled[stat] < 100:
                scaled[stat] += 1
                remaining -= 1
            index += 1
        while remaining < 0:
            stat = priority[index % len(priority)]
            if scaled[stat] > 0:
                scaled[stat] -= 1
                remaining += 1
            index += 1
        values = scaled
    return normalize_attributes(values)


def _fallback_from_description(description: str) -> Dict[str, int]:
    text = description.lower()
    scores = {stat: 1 for stat in ATTRIBUTE_NAMES}
    keyword_map = {
        "strength": ("strong", "power", "melee", "brute", "heavy"),
        "dexterity": ("accurate", "aim", "shoot", "gun", "archer", "precise", "lockpick"),
        "agility": ("agile", "dodge", "acrobat", "stealth", "sneak", "nimble"),
        "constitution": ("tough", "durable", "tank", "endurance", "stamina"),
        "intelligence": ("smart", "engineer", "engineering", "hacker", "tech", "scientist", "detective"),
        "wisdom": ("wise", "perceptive", "aware", "investigator", "survival"),
        "charisma": ("charismatic", "persuasive", "leader", "social", "talker"),
        "speed": ("fast", "speed", "quick", "runner"),
        "defense": ("defensive", "armor", "tank", "guard"),
        "luck": ("lucky", "luck", "gambler"),
        "magic": ("magic", "mage", "spell", "psychic", "power", "bender", "force"),
        "health": ("healthy", "survivor", "tough", "tank"),
        "resource": ("resource", "mana", "energy", "rage", "focus", "ability", "powers"),
    }
    for stat, words in keyword_map.items():
        scores[stat] += 3 * sum(1 for word in words if word in text)
    return _repair_allocation(scores)


def generate_ai_allocation(provider, description: str, world_profile: Dict | None = None) -> Dict[str, int]:
    client = getattr(provider, "client", None)
    model = getattr(provider, "model", None)
    if client is None or not model:
        return _fallback_from_description(description)

    instructions = """You allocate starting Skill Points for The Shattered Realms. Return ONLY a valid JSON object.
The player has exactly 42 SP total across exactly these 13 stats: strength, dexterity, agility, constitution, intelligence, wisdom, charisma, speed, defense, luck, magic, health, resource.
Read the player's build description and the confirmed world profile. Allocate the 42 SP to best represent that concept. Do not change the stat names, invent stats, omit stats, use negative values, or spend more/less than 42 total.
A stat may be 0. The natural cap is 100.
Respect the setting. For example, a realistic modern investigator does not need Magic unless the world actually includes supernatural powers; a cyberpunk engineer may favor Intelligence; a fast stealth fighter may favor Agility, Dexterity and Speed; a power-user may need Resource so their abilities are usable.
Return only the 13 numeric key/value pairs."""
    payload = {"build_description": description, "world_profile": world_profile or {}, "sp_budget": STARTING_SKILL_POINTS, "stats": list(ATTRIBUTE_NAMES)}
    try:
        response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, indent=2))
        parsed = json.loads(response.output_text.strip())
    except Exception:
        parsed = {}
    return _repair_allocation(parsed if isinstance(parsed, dict) else {})


def _print_manual_stat_reference(allocation: Dict[str, int], remaining: int) -> None:
    print("\n" + "=" * 76)
    print(f"MANUAL STAT BUILD — {remaining} SP REMAINING")
    print("=" * 76)
    for stat in ATTRIBUTE_NAMES:
        print(f"{stat.title():<14} Current: {allocation.get(stat, 0):>2}  | {STAT_HELP[stat]}")
    print("\nSpend SP by typing: stat,amount sp")
    print("Example: speed,3sp")
    print("You may also type 'reset' to clear the build or 'help' to show this list again.")


def _manual_allocation() -> Dict[str, int]:
    allocation = {stat: 0 for stat in ATTRIBUTE_NAMES}
    remaining = STARTING_SKILL_POINTS
    _print_manual_stat_reference(allocation, remaining)
    pattern = re.compile(r"^\s*([a-zA-Z_ ]+)\s*,\s*(\d+)\s*(?:sp)?\s*$", re.I)

    while remaining > 0:
        raw = input(f"\nSpend SP ({remaining} remaining): ").strip()
        lowered = raw.lower()
        if lowered in {"help", "stats", "show", "show stats", "build"}:
            _print_manual_stat_reference(allocation, remaining)
            continue
        if lowered in {"reset", "restart", "clear"}:
            allocation = {stat: 0 for stat in ATTRIBUTE_NAMES}
            remaining = STARTING_SKILL_POINTS
            _print_manual_stat_reference(allocation, remaining)
            continue

        match = pattern.match(raw)
        if not match:
            print("Use the format stat,amount sp — for example: speed,3sp")
            continue
        stat = match.group(1).strip().lower().replace(" ", "_")
        aliases = {"defence": "defense", "mana": "resource", "int": "intelligence", "char": "charisma", "con": "constitution", "dex": "dexterity", "agi": "agility", "str": "strength"}
        stat = aliases.get(stat, stat)
        amount = int(match.group(2))
        if stat not in allocation:
            print(f"Unknown stat '{stat}'. Type 'help' to see all 13 stats.")
            continue
        if amount <= 0:
            print("Spend at least 1 SP.")
            continue
        if amount > remaining:
            print(f"You only have {remaining} SP remaining.")
            continue
        if allocation[stat] + amount > 100:
            print(f"{stat.title()} cannot exceed the natural cap of 100.")
            continue

        allocation[stat] += amount
        remaining -= amount
        print(f"Added {amount} SP to {stat.title()} → {allocation[stat]} total. {remaining} SP remaining.")

    print("\nAll 42 starting SP have been allocated.")
    _print_manual_stat_reference(allocation, 0)
    return normalize_attributes(allocation)


def install_ai_stat_allocator(game_master) -> None:
    """Install manual-or-AI starting-stat selection for character creation."""
    from . import character_creation

    current = character_creation._allocate_stats
    if getattr(current, "_ai_builder_wrapper", False):
        return

    def choose_allocation() -> Dict[str, int]:
        print("\nHow do you want to build your starting stats?")
        print("  1. Spend the 42 SP yourself")
        print("  2. Describe your build and let the AI spend the 42 SP for you")
        while True:
            choice = input("Choose 1 or 2: ").strip().lower()
            if choice in {"1", "manual", "myself"}:
                return _manual_allocation()
            if choice in {"2", "ai", "auto", "automatic"}:
                description = input("Describe the build you want (playstyle, strengths, weaknesses, role, etc.):\n> ").strip()
                if not description:
                    print("Give the AI a short build description first.")
                    continue
                print("\nAI is allocating your 42 SP...")
                world_profile = game_master.state.data.get("world_profile", {})
                allocation = generate_ai_allocation(game_master.provider, description, world_profile)
                print("\nAI-GENERATED BUILD")
                for stat in ATTRIBUTE_NAMES:
                    print(f"  {stat.title():<14} {allocation[stat]}")
                print(f"  {'TOTAL SP':<14} {sum(allocation.values())}/{STARTING_SKILL_POINTS}")
                print("You will still get the normal full build/derived-stat preview and confirmation next.")
                return allocation
            print("Choose 1 for manual allocation or 2 for AI allocation.")

    choose_allocation._ai_builder_wrapper = True
    character_creation._allocate_stats = choose_allocation
