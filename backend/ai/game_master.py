"""AI-first Game Master runtime for The Shattered Realms."""

from typing import Dict

from .context import ContextBuilder
from .memory import CampaignMemory
from .provider import provider_from_environment
from .rules import RuleLibrary
from backend.game.state import GameState
from backend.game.world import WorldSimulator


class GameMaster:
    """Coordinates player freedom, rules, memory, AI reasoning, and world state."""

    def __init__(
        self,
        provider=None,
        state: GameState | None = None,
        memory: CampaignMemory | None = None,
        rules: RuleLibrary | None = None,
    ) -> None:
        self.provider = provider or provider_from_environment()
        self.state = state or GameState()
        self.memory = memory or CampaignMemory()
        self.rules = rules or RuleLibrary()
        self.context_builder = ContextBuilder()
        self.world = WorldSimulator()
        self.ready = True

    def handle_action(self, player_action: str) -> Dict:
        """Resolve one unrestricted player action through the AI core."""
        action = player_action.strip()
        if not action:
            return {
                "narration": "Tell the Game Master what you want to do.",
                "state": self.state.snapshot(),
            }

        relevant_memories = self.memory.search(action)
        relevant_rules = self.rules.retrieve(action)
        context = self.context_builder.build(
            player_action=action,
            game_state=self.state.snapshot(),
            memories=relevant_memories,
            rules=relevant_rules,
        )

        result = self.provider.respond(context)
        changes = result.get("state_changes", [])
        self.state.apply_changes(changes)

        for memory in result.get("memories", []):
            if isinstance(memory, str):
                self.memory.remember(memory)
            elif isinstance(memory, dict):
                self.memory.remember(
                    memory.get("text", ""),
                    category=memory.get("category", "event"),
                    importance=memory.get("importance", 1),
                    confirmed=memory.get("confirmed", True),
                )

        result["state"] = self.state.snapshot()
        return result

    def advance_world(self, elapsed_days: int) -> Dict:
        """Advance independent world activity and apply resulting state changes."""
        events = self.world.advance(self.state.snapshot(), elapsed_days)
        changes = [event["state_change"] for event in events if "state_change" in event]
        self.state.apply_changes(changes)
        for event in events:
            summary = event.get("summary")
            if summary:
                self.memory.remember(summary, category="world", importance=2)
        return {"events": events, "state": self.state.snapshot()}
