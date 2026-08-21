"""Optional AI-assisted starting-stat allocation for character creation."""
from __future__ import annotations

import json
from typing import Dict

from .attributes import ATTRIBUTE_NAMES, STARTING_SKILL_POINTS, normalize_attributes


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
        # Neutral fallback. The remainder is distributed from the first stat onward.
        values = {stat: STARTING_SKILL_POINTS // len(ATTRIBUTE_NAMES) for stat in ATTRIBUTE_NAMES}
        total = sum(values.values())

    # Scale toward the exact starting budget while preserving the AI's priorities.
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
    """Simple offline fallback that still produces a legal 42-SP build."""
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
A stat may be 0. The natural cap is 100, though a Level 1 build will obviously be far below that because only 42 SP exist.
Respect the setting. For example, a realistic modern investigator does not need Magic unless the world actually includes supernatural powers; a cyberpunk engineer may favor Intelligence; a fast stealth fighter may favor Agility, Dexterity and Speed; a power-user may need Resource so their abilities are usable.
Return only the 13 numeric key/value pairs."""
    payload = {
        "build_description": description,
        "world_profile": world_profile or {},
        "sp_budget": STARTING_SKILL_POINTS,
        "stats": list(ATTRIBUTE_NAMES),
    }
    try:
        response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, indent=2))
        parsed = json.loads(response.output_text.strip())
    except Exception:
        parsed = {}
    return _repair_allocation(parsed if isinstance(parsed, dict) else {})


def install_ai_stat_allocator(game_master) -> None:
    """Wrap character creation's normal allocator with manual-or-AI choice.

    Safe to call repeatedly; only one wrapper is installed per process.
    """
    from . import character_creation

    current = character_creation._allocate_stats
    if getattr(current, "_ai_builder_wrapper", False):
        return
    manual_allocator = current

    def choose_allocation() -> Dict[str, int]:
        print("\nHow do you want to build your starting stats?")
        print("  1. Spend the 42 SP yourself")
        print("  2. Describe your build and let the AI spend the 42 SP for you")
        while True:
            choice = input("Choose 1 or 2: ").strip().lower()
            if choice in {"1", "manual", "myself"}:
                return manual_allocator()
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
