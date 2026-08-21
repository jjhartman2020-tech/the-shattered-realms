"""AI-guided world creation for a new Shattered Realms campaign."""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Dict


def _fallback_world(prompt: str) -> Dict:
    return {
        "name": "Untitled World",
        "premise": prompt,
        "genre": "custom",
        "era": "as described by the player",
        "tone": "adventure",
        "technology_level": "defined by the player's premise",
        "supernatural_rules": "Only what the player requested exists.",
        "government_and_society": "To be discovered during play.",
        "factions": [],
        "important_locations": [],
        "cultures_and_species": [],
        "common_weapons_and_gear": [],
        "economy": "Setting-appropriate currency and trade.",
        "major_conflicts": [],
        "special_world_rules": [],
        "character_guidance": "Generate classes, resources, abilities, equipment, NPCs, enemies, and quests that strictly fit this world.",
        "player_request": prompt,
    }


def generate_world(provider, prompt: str) -> Dict:
    client = getattr(provider, "client", None)
    model = getattr(provider, "model", None)
    if client is None or not model:
        return _fallback_world(prompt)
    instructions = """You are the World Architect for a universal AI tabletop RPG. Return ONLY valid JSON.
The game can support fantasy, modern realistic crime/investigation, science fiction, cyberpunk, elemental martial arts, space opera, historical settings, horror, superhero-like worlds, or any other player-described setting. Do NOT assume medieval fantasy, magic, swords, or any particular technology unless the player requested them.
Preserve the player's requested premise and tone. Expand it into a playable original world profile without changing the core fantasy of what they asked for.
If the player references an existing franchise, capture the requested style, themes, gameplay concepts, and kinds of technology/powers without requiring exact copyrighted characters or plotlines.
The world profile is authoritative context for all later generation: character class, resource name, abilities, weapons, equipment, NPCs, enemies, factions, quests, locations, economy, narration, and encounters must fit it.
Return these keys: name, premise, genre, era, tone, technology_level, supernatural_rules, government_and_society, factions, important_locations, cultures_and_species, common_weapons_and_gear, economy, major_conflicts, special_world_rules, character_guidance, player_request.
Use arrays of short strings for factions, important_locations, cultures_and_species, common_weapons_and_gear, major_conflicts, and special_world_rules."""
    response = client.responses.create(model=model, instructions=instructions, input=json.dumps({"player_world_request": prompt}, ensure_ascii=False))
    try:
        world = json.loads(response.output_text.strip())
    except (json.JSONDecodeError, AttributeError):
        world = _fallback_world(prompt)
    if not isinstance(world, dict):
        world = _fallback_world(prompt)
    world["player_request"] = prompt
    return world


def _print_world(world: Dict) -> None:
    print("\n" + "=" * 52)
    print("WORLD SUMMARY")
    print("=" * 52)
    labels = [
        ("WORLD", "name"), ("PREMISE", "premise"), ("GENRE", "genre"), ("ERA", "era"),
        ("TONE", "tone"), ("TECHNOLOGY", "technology_level"), ("POWERS / SUPERNATURAL", "supernatural_rules"),
        ("SOCIETY", "government_and_society"), ("ECONOMY", "economy"),
    ]
    for label, key in labels:
        value = world.get(key)
        if value: print(f"{label}: {value}")
    for label, key in [("FACTIONS", "factions"), ("IMPORTANT LOCATIONS", "important_locations"),
                       ("CULTURES / SPECIES", "cultures_and_species"), ("COMMON GEAR", "common_weapons_and_gear"),
                       ("MAJOR CONFLICTS", "major_conflicts"), ("SPECIAL RULES", "special_world_rules")]:
        values = world.get(key)
        if isinstance(values, list) and values:
            print(f"{label}:")
            for value in values: print(f"  - {value}")
    print("=" * 52)


def run_world_creation(game_master) -> Dict:
    print("\n" + "=" * 52)
    print("WORLD CREATION")
    print("=" * 52)
    print("This game can take place in any kind of setting — fantasy, modern day, space opera, cyberpunk, historical, or something completely original.")
    request = input("Where do you want your story to take place? Describe the world and kind of adventure you want:\n> ").strip()
    if not request:
        request = "Create an original adventure world with a balanced mix of exploration, conflict, and mystery."

    while True:
        print("\nGenerating your world...")
        world = generate_world(game_master.provider, request)
        _print_world(world)
        answer = input("\nDoes this match what you had in mind? (yes / describe changes): ").strip()
        if answer.lower() in {"yes", "y", "confirm", "looks good", "good"}:
            break
        if answer:
            request = f"ORIGINAL REQUEST:\n{request}\n\nPLAYER CHANGES:\n{answer}\nRegenerate the world incorporating the changes while preserving everything the player did not ask to change."

    game_master.state.data["world_profile"] = deepcopy(world)
    game_master.state.data["world_creation_complete"] = True
    game_master.state.save()

    # Character creation now offers either manual 42-SP allocation or an AI-built
    # allocation based on the player's build description and this world profile.
    from .ai_stat_builder import install_ai_stat_allocator
    install_ai_stat_allocator(game_master)

    return deepcopy(world)
