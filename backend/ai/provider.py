"""Model-provider boundary for the AI Game Master.

The repository never stores API keys. Live providers read secrets from environment variables at runtime.
"""

import json
import os
from typing import Dict, Protocol


class AIProvider(Protocol):
    def respond(self, context: Dict) -> Dict:
        """Return a structured Game Master turn."""


class DevelopmentProvider:
    def respond(self, context: Dict) -> Dict:
        action = context.get("player_action", "").strip()
        return {"narration": "The Game Master core received your action and assembled the campaign context. Set OPENAI_API_KEY to enable the live AI.", "player_action": action, "requires_roll": False, "roll": None, "combat_request": None, "state_changes": [], "memories": [], "world_notes": [], "debug": {"provider": "development"}}


class OpenAIProvider:
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
Be neutral, fair, imaginative, adaptive, and consistent with established canon. Keep the game moving while preserving established facts.

MECHANICAL CHECK RULES
- Ordinary movement, conversation, looking around, and uncontested actions do not need rolls.
- Risky, contested, uncertain non-combat actions whose success matters require a mechanical check.
- On the first pass, if a check is needed, set requires_roll=true. Do not invent a die result, modifier, total, or success/failure.
- Choose the most appropriate skill and difficulty from trivial, easy, standard, hard, very_hard, extreme.
- When context contains mechanical_result, Python has resolved the roll. Obey it exactly.

COMBAT RULES
- Python is authoritative for initiative, positions, movement, range, attack rolls, HP, damage, critical hits, defeat, and turn progression.
- Never invent or silently change those values.
- To begin combat return combat_request.type=\"start\" with every newly-created enemy.
- Enemy entries include name, team=\"enemy\", level, attributes, hp, armor_class, damage, attack_attribute, and role. Position and attack_range may be included when established.
- Attributes use the game's 0-30 stats: health, mana, strength, dexterity, constitution, intelligence, wisdom, charisma, speed.
- During active combat use attack, move, move_attack, end_turn, or pass.
- If the player says they end their turn, wait, pass, hold position, or otherwise deliberately finish without another action, return {\"type\":\"end_turn\"}. Do NOT merely narrate that their turn ended.
- For move return integer x and y. For move_attack return x, y, target, and attack_attribute.
- active_combat positions are authoritative. Compute destinations from the current positions in active_combat, never from an earlier narration or memory.
- Never choose a destination occupied by a living combatant. A melee move_attack must stop on an unoccupied square adjacent to the target.
- Respect exact requested square counts/directions when legal. For \"toward\" or \"next to\", choose a shortest legal destination within remaining movement.
- Movement alone does not end the player's turn or spend their attack.
- A combined move_attack is one atomic intended action. Python may reject the whole action; if combat_result says invalid, narrate that no part of the attempted combined action occurred.
- If context contains enemy_turn, choose attack, move, move_attack, or pass using only information the enemy could know.
- If context contains combat_result, narrate it exactly. Do not issue another combat request, reroll, move anyone again, or alter mechanics.

Return ONLY valid JSON with this top-level shape:
{\"narration\":\"player-facing description\",\"player_action\":\"interpreted action\",\"requires_roll\":false,\"roll\":null,\"combat_request\":null,\"state_changes\":[],\"memories\":[],\"world_notes\":[]}

When requires_roll=true, roll must contain reason, difficulty, and skill.
Combat examples:
{\"type\":\"attack\",\"target\":\"Goblin Scout\",\"attack_attribute\":\"strength\"}
{\"type\":\"move\",\"x\":4,\"y\":0}
{\"type\":\"move_attack\",\"x\":4,\"y\":0,\"target\":\"Goblin Scout\",\"attack_attribute\":\"strength\"}
{\"type\":\"end_turn\"}

Do not apply success/failure state changes before a required roll or combat action is resolved. Never include private chain-of-thought or hidden reasoning.
"""
        response = self.client.responses.create(model=self.model, instructions=system_instructions, input=serialize_context(context))
        raw = response.output_text.strip()
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"narration": raw or "The world hesitates for a moment.", "player_action": context.get("player_action", ""), "requires_roll": False, "roll": None, "combat_request": None, "state_changes": [], "memories": [], "world_notes": []}
        result.setdefault("narration", "The world waits...")
        result.setdefault("player_action", context.get("player_action", ""))
        result.setdefault("requires_roll", False)
        result.setdefault("roll", None)
        result.setdefault("combat_request", None)
        result.setdefault("state_changes", [])
        result.setdefault("memories", [])
        result.setdefault("world_notes", [])
        result["debug"] = {"provider": "openai", "model": self.model, "rules_found": len(context.get("relevant_rules", [])), "memories_found": len(context.get("relevant_memories", []))}
        return result


def provider_from_environment() -> AIProvider:
    if os.getenv("OPENAI_API_KEY", "").strip():
        return OpenAIProvider()
    return DevelopmentProvider()


def serialize_context(context: Dict) -> str:
    return json.dumps(context, ensure_ascii=False, indent=2, default=str)
