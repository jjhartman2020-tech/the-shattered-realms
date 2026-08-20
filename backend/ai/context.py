"""Context assembly for the Shattered Realms AI Game Master."""

from typing import Dict, List


CORE_PRINCIPLES = [
    "Preserve player agency.",
    "Respect established campaign canon.",
    "Follow documented systems before improvising.",
    "Maintain internal consistency and logical cause and effect.",
    "Acknowledge uncertainty instead of inventing unsupported facts.",
    "Apply consequences fairly and proportionally.",
    "Keep the world active beyond the player's immediate location.",
]


class ContextBuilder:
    """Builds the information packet sent to the AI for each turn."""

    def __init__(self) -> None:
        self.core_principles = list(CORE_PRINCIPLES)

    def build(
        self,
        player_action: str,
        game_state: Dict,
        memories: List[Dict],
        rules: List[str],
    ) -> Dict:
        return {
            "role": "AI Game Master for The Shattered Realms",
            "principles": self.core_principles,
            "decision_order": [
                "Identify the situation",
                "Determine which documented systems apply",
                "Gather currently available information",
                "Evaluate reasonable outcomes",
                "Choose the outcome most consistent with the framework",
                "Apply consequences",
                "Update world state",
            ],
            "player_action": player_action,
            "game_state": game_state,
            "relevant_memories": memories,
            "relevant_rules": rules,
        }
