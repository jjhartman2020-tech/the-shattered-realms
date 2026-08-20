"""Model-provider boundary for the AI Game Master.

The repository never stores API keys. Live providers read secrets from
environment variables at runtime.
"""

import json
import os
from typing import Dict, Protocol


class AIProvider(Protocol):
    def respond(self, context: Dict) -> Dict:
        """Return a structured Game Master turn."""


class DevelopmentProvider:
    """Offline provider used when no live model is configured."""

    def respond(self, context: Dict) -> Dict:
        action = context.get("player_action", "").strip()
        return {
            "narration": "The Game Master core received your action and assembled the campaign context. Set OPENAI_API_KEY to enable the live AI.",
            "player_action": action,
            "requires_roll": False,
            "roll": None,
            "combat_request": None,
            "state_changes": [],
            "memories": [],
            "world_notes": [],
            "debug": {"provider": "development"},
        }


class OpenAIProvider:
    """Live OpenAI Responses API provider for the AI Game Master."""

    def __init__(self, model: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("The OpenAI Python package is not installed. Run: pip install openai") from exc
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

    def respond(self, context: Dict) -> Dict:
        system_instructions = """You are the AI Game Master for The Shattered Realms.
Be neutral, fair, imaginative, adaptive, and consistent with established canon.
Keep the game moving. Invent reasonable undefined creative details rather than
blocking exploration, while preserving established facts.

MECHANICAL CHECK RULES
- Ordinary movement, conversation, looking around, and uncontested actions do not need rolls.
- Risky, contested, uncertain non-combat actions whose success matters require a mechanical check.
- On the first pass, if a check is needed, set requires_roll=true. Do not invent a die result, modifier, total, or success/failure.
- Choose the most appropriate skill from: athletics, stealth, sleight_of_hand, perception, investigation, survival, persuasion, deception, intimidation.
- Choose difficulty from: trivial, easy, standard, hard, very_hard, extreme.
- Difficulty must reflect the actual situation, opposition, environment, and established facts.
- When context contains mechanical_result, Python has already resolved the roll. Obey it exactly.

COMBAT RULES
- Combat begins when hostile opposition can no longer reasonably be handled as normal roleplay.
- Never invent attack rolls, initiative, HP loss, damage, critical hits, or defeat. Python owns those mechanics.
- If a player's action should BEGIN combat, return combat_request.type="start" and list every newly-created enemy participant.
- Enemy entries must include: name, team="enemy", level, attributes, hp, armor_class, damage, attack_attribute, role.
- attributes use the game's 0-30 stats: health, mana, strength, dexterity, constitution, intelligence, wisdom, charisma, speed.
- Keep generated enemies appropriate to established fiction and encounter difficulty. Do not inflate stats just to force difficulty.
- If combat is already active and the player attacks, return combat_request.type="attack" with target and attack_attribute (strength or dexterity).
- If context contains enemy_turn, choose a legal tactical action for that enemy based only on information available to it. For the current prototype, return an attack action when attacking is reasonable; otherwise return type="pass". Do not invent the outcome.
- If context contains combat_result, Python already resolved the combat action. Narrate it exactly and do not change the mechanical outcome.

Return ONLY valid JSON with this top-level shape:
{
  "narration": "player-facing description",
  "player_action": "interpreted action",
  "requires_roll": false,
  "roll": null,
  "combat_request": null,
  "state_changes": [],
  "memories": [],
  "world_notes": []
}

When requires_roll=true, roll MUST look like:
{
  "reason": "Sneak past an alert guard",
  "difficulty": "hard",
  "skill": "stealth"
}

Combat start example:
{
  "type": "start",
  "enemies": [
    {
      "name": "Goblin Scout",
      "team": "enemy",
      "level": 1,
      "attributes": {"health": 10, "mana": 0, "strength": 6, "dexterity": 9, "constitution": 6, "intelligence": 3, "wisdom": 6, "charisma": 2, "speed": 9},
      "hp": 10,
      "armor_class": 11,
      "damage": "1d4",
      "attack_attribute": "dexterity",
      "role": "ranged"
    }
  ]
}

Combat attack example:
{"type":"attack","target":"Goblin Scout","attack_attribute":"strength"}

Do not apply success/failure state changes before a required roll or combat action is resolved.
Never include private chain-of-thought or hidden reasoning.
"""
        response = self.client.responses.create(
            model=self.model,
            instructions=system_instructions,
            input=serialize_context(context),
        )
        raw = response.output_text.strip()
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {
                "narration": raw or "The world hesitates for a moment.",
                "player_action": context.get("player_action", ""),
                "requires_roll": False,
                "roll": None,
                "combat_request": None,
                "state_changes": [],
                "memories": [],
                "world_notes": [],
            }
        result.setdefault("narration", "The world waits...")
        result.setdefault("player_action", context.get("player_action", ""))
        result.setdefault("requires_roll", False)
        result.setdefault("roll", None)
        result.setdefault("combat_request", None)
        result.setdefault("state_changes", [])
        result.setdefault("memories", [])
        result.setdefault("world_notes", [])
        result["debug"] = {
            "provider": "openai",
            "model": self.model,
            "rules_found": len(context.get("relevant_rules", [])),
            "memories_found": len(context.get("relevant_memories", [])),
        }
        return result


def provider_from_environment() -> AIProvider:
    if os.getenv("OPENAI_API_KEY", "").strip():
        return OpenAIProvider()
    return DevelopmentProvider()


def serialize_context(context: Dict) -> str:
    return json.dumps(context, ensure_ascii=False, indent=2, default=str)
