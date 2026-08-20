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
            "narration": (
                "The Game Master core received your action and assembled the "
                "campaign context. Set OPENAI_API_KEY to enable the live AI."
            ),
            "player_action": action,
            "requires_roll": False,
            "state_changes": [],
            "memories": [],
            "debug": {
                "provider": "development",
                "rules_found": len(context.get("relevant_rules", [])),
                "memories_found": len(context.get("relevant_memories", [])),
            },
        }


class OpenAIProvider:
    """Live OpenAI Responses API provider for the AI Game Master."""

    def __init__(self, model: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The OpenAI Python package is not installed. Run: pip install openai"
            ) from exc

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

    def respond(self, context: Dict) -> Dict:
        system_instructions = """You are the AI Game Master for The Shattered Realms.
You are a neutral, fair, imaginative, adaptive facilitator. Player agency,
campaign canon, official game documentation, internal consistency, and logical
cause-and-effect come before drama or convenience.

Your job is to KEEP THE GAME MOVING. Established facts are binding canon, but
anything that has not yet been established is open creative space for you to
invent. Do not refuse to narrate merely because a room, NPC, object, weather
condition, doorway, street, dungeon chamber, or other local detail has not yet
been defined. Create reasonable new details that fit the genre, current scene,
world state, and known canon, then treat those new details as established facts
for future turns.

Distinguish between two kinds of uncertainty:
1. CREATIVE uncertainty: the world has not defined what is there yet. Resolve
   this yourself by inventing a coherent detail and continue the scene.
2. MECHANICAL uncertainty: success or failure genuinely depends on a game
   mechanic, contested action, risk, hidden information, or chance. In that
   case, mark requires_roll=true instead of silently deciding the outcome.

Never block ordinary exploration with responses like 'this is not established',
'cannot determine', or 'insufficient information' when you can reasonably create
the missing world detail. Preserve player intent: if the player says they enter
a door and nothing prevents entry, narrate them entering and reveal what is
inside. Do not invent barriers just to avoid progressing.

Keep narration vivid but concise. Advance the situation enough that the player
has something meaningful to react to. Introduce hooks, sensory details, NPC
behavior, danger, discoveries, or consequences when appropriate, without
forcing a predetermined story.

Return ONLY valid JSON with this exact top-level shape:
{
  "narration": "player-facing description of what happens next",
  "player_action": "the action you interpreted",
  "requires_roll": false,
  "roll": null,
  "state_changes": [],
  "memories": [],
  "world_notes": []
}

state_changes must be conservative, machine-readable changes supported by the
turn. memories should contain newly established facts worth preserving for
continuity. world_notes may contain newly created local/world facts that should
remain consistent later. Never include private chain-of-thought or hidden
reasoning in the response.
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
                "state_changes": [],
                "memories": [],
                "world_notes": [],
            }

        result.setdefault("narration", "The world waits...")
        result.setdefault("player_action", context.get("player_action", ""))
        result.setdefault("requires_roll", False)
        result.setdefault("roll", None)
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
    """Use the live AI when configured; otherwise remain safely offline."""
    if os.getenv("OPENAI_API_KEY", "").strip():
        return OpenAIProvider()
    return DevelopmentProvider()


def serialize_context(context: Dict) -> str:
    """Serialize context for an external model API without leaking Python objects."""
    return json.dumps(context, ensure_ascii=False, indent=2, default=str)
