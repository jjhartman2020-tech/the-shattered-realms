"""Make character abilities and starter equipment obey the confirmed world profile."""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Dict


class _ResponsesProxy:
    def __init__(self, responses, world: Dict):
        self._responses = responses
        self._world = deepcopy(world)

    def create(self, *args, **kwargs):
        world_json = json.dumps(self._world, ensure_ascii=False, indent=2, default=str)
        extra = f"""

CONFIRMED WORLD PROFILE — AUTHORITATIVE:
{world_json}

WORLD-FIT REQUIREMENTS:
- The confirmed world profile is authoritative for EVERY generated class, ability, starter kit, weapon, consumable, utility item, and special equipment option.
- Do not fall back to generic medieval-fantasy vocabulary or equipment unless that world actually contains it.
- Match the world's technology, era, supernatural rules, culture, and common gear literally. A cyberpunk/high-tech world should naturally use things such as firearms/blasters, smart weapons, drones, cyberware, scanners, med-tech, hacking tools, energy equipment, and setting-appropriate utilities when those concepts fit the profile — not bows, runestones, healing draughts, or fantasy travel gear by default.
- Likewise, a modern, historical, sci-fi, western, superhero, post-apocalyptic, or other setting must receive gear and abilities native to THAT setting.
- Ability flavor must fit the character AND world. Do not call a mechanical projectile 'Arc Spark' or magical unless supernatural powers actually exist in the confirmed world.
- CHARACTER BUILD HAS PRIORITY OVER SETTING CLICHES. The world controls technology, materials, names, and flavor; the chosen stats and intended archetype control the combat role and item function.
- Starter kits must be cohesive variations built for THIS character's strongest stats, class concept, and playstyle—not generic examples of gear that merely exists in the setting.
- Translate the archetype into the setting. Example: a ninja/stealth build in a high-tech space world should receive advanced stealth blades, smart throwing weapons, infiltration tools, grapnels, compact cloaking gear, or other ninja-like equipment. Do NOT replace that identity with a generic blaster user unless the build actually favors or requests firearms.
- Weapons and tools should use attack attributes and functions that match the character's strongest stats. Do not give a low-Dexterity melee specialist a gun-focused kit, or a stealth specialist a loud heavy-weapons kit.
- Special equipment must be both setting-native AND build-native.
- Mechanics remain constrained by the original character-generation rules; only theme/flavor and appropriate mechanical fields should adapt to the world.
"""
        kwargs["instructions"] = str(kwargs.get("instructions") or "") + extra
        original_input = kwargs.get("input", "")
        kwargs["input"] = f"{original_input}\n\nCONFIRMED_WORLD_PROFILE:\n{world_json}"
        return self._responses.create(*args, **kwargs)


class _ClientProxy:
    def __init__(self, client, world: Dict):
        self._client = client
        self.responses = _ResponsesProxy(client.responses, world)

    def __getattr__(self, name):
        return getattr(self._client, name)


class _ProviderProxy:
    def __init__(self, provider, world: Dict):
        self._provider = provider
        self.client = _ClientProxy(provider.client, world)
        self.model = provider.model

    def __getattr__(self, name):
        return getattr(self._provider, name)


def install_world_aware_character_generation(game_master, world: Dict) -> None:
    """Wrap character package generation so its AI always sees the confirmed world."""
    import backend.game.character_creation as cc

    current = cc.generate_character_package
    # Reinstall for a newly confirmed world, but never stack our own wrappers.
    base = getattr(current, "_world_aware_base", current)
    confirmed_world = deepcopy(world)

    def world_aware(provider, *, name: str, appearance: str, stats: Dict[str, int]):
        client = getattr(provider, "client", None)
        model = getattr(provider, "model", None)
        if client is None or not model:
            return base(provider, name=name, appearance=appearance, stats=stats)
        proxy = _ProviderProxy(provider, confirmed_world)
        return base(proxy, name=name, appearance=appearance, stats=stats)

    world_aware._world_aware_base = base
    cc.generate_character_package = world_aware
