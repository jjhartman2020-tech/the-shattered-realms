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

        # Give every turn both relevant memories and enough recent canon to keep
        # the scene coherent even when the player's wording changes.
        relevant_memories = self.memory.context_for(action)
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
            self._store_memory(memory, default_category="event")

        # The provider can separately return freshly invented world facts such
        # as a tavern layout, NPC identity, local rumor, landmark, or discovery.
        for note in result.get("world_notes", []):
            self._store_memory(note, default_category="world")

        result["state"] = self.state.snapshot()
        result["memory_count"] = len(self.memory.all())
        return result

    def _store_memory(self, memory, default_category: str) -> None:
        if isinstance(memory, str):
            self.memory.remember(memory, category=default_category, importance=2)
        elif isinstance(memory, dict):
            self.memory.remember(
                memory.get("text", ""),
                category=memory.get("category", default_category),
                importance=memory.get("importance", 2),
                confirmed=memory.get("confirmed", True),
            )

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
