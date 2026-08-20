"""Model-provider boundary for the AI Game Master.

No API key is stored in this repository. A real provider can be connected later
through environment variables or a server-side secret manager.
"""

import json
from typing import Dict, Protocol


class AIProvider(Protocol):
    def respond(self, context: Dict) -> Dict:
        """Return a structured Game Master turn."""


class DevelopmentProvider:
    """Offline provider used while the live model connection is not configured."""

    def respond(self, context: Dict) -> Dict:
        action = context.get("player_action", "").strip()
        return {
            "narration": (
                "The Game Master core received your action and assembled the "
                "campaign context. A live AI model still needs to be connected "
                "before the world can resolve this action dynamically."
            ),
            "player_action": action,
            "requires_roll": False,
            "state_changes": [],
            "memories": [],
            "debug": {
                "rules_found": len(context.get("relevant_rules", [])),
                "memories_found": len(context.get("relevant_memories", [])),
            },
        }


def serialize_context(context: Dict) -> str:
    """Serialize context for an external model API without leaking Python objects."""
    return json.dumps(context, ensure_ascii=False, indent=2, default=str)
