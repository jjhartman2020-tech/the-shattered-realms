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
        confirmed_recent = [
            memory for memory in memories
            if isinstance(memory, dict) and memory.get("confirmed", True)
        ][-8:]
        return {
            "role": "AI Game Master for The Shattered Realms",
            "principles": self.core_principles,
            "decision_order": [
                "Identify the situation",
                "Check recent confirmed continuity before inventing or repeating anything",
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
            "continuity_guard": {
                "instruction": (
                    "These recent confirmed events are authoritative continuity. Before narrating or suggesting actions, "
                    "check them explicitly. Never say an object, body, room, container, NPC, clue, or location has not "
                    "been searched/examined/visited/used if a recent confirmed event says it already was. A failed search "
                    "still counts as having searched that target; do not offer the exact same search again unless the player "
                    "clearly chooses to retry, new information changes what could be found, or the scene materially changes. "
                    "Do not undo completed actions just because the current player command is about something else such as "
                    "inventory, leveling, progress, or equipment. Preserve consequences across turns."
                ),
                "recent_confirmed_events": confirmed_recent,
            },
            "relevant_rules": rules,
        }
