"""AI-first Game Master runtime for The Shattered Realms."""

from typing import Dict

from .context import ContextBuilder
from .memory import CampaignMemory
from .provider import provider_from_environment
from .rules import RuleLibrary
from backend.game.attributes import SKILL_ATTRIBUTE, attribute_check_bonus, normalize_attributes
from backend.game.checks import resolve_check
from backend.game.state import GameState
from backend.game.world import WorldSimulator


SKILL_ALIASES = {
    "acrobatics": "acrobatics", "animal handling": "animal_handling",
    "arcana": "arcana", "athletics": "athletics", "strength": "athletics",
    "stealth": "stealth", "sneak": "stealth",
    "sleight of hand": "sleight_of_hand", "sleight_of_hand": "sleight_of_hand",
    "pickpocket": "sleight_of_hand", "perception": "perception",
    "investigation": "investigation", "survival": "survival",
    "persuasion": "persuasion", "persuade": "persuasion",
    "deception": "deception", "deceive": "deception",
    "intimidation": "intimidation", "intimidate": "intimidation",
    "insight": "insight", "medicine": "medicine", "nature": "nature",
    "performance": "performance", "religion": "religion", "history": "history",
}

ATTRIBUTE_ALIASES = {
    "health": "health", "mana": "mana", "strength": "strength",
    "dexterity": "dexterity", "agility": "dexterity",
    "constitution": "constitution", "durability": "constitution",
    "intelligence": "intelligence", "wisdom": "wisdom",
    "charisma": "charisma", "speed": "speed",
}

ATTRIBUTE_REASON_HINTS = {
    "strength": ("force", "lift", "break", "shove", "grapple", "overpower", "push", "pull"),
    "dexterity": ("dodge", "balance", "jump", "reflex", "aim", "precise", "finesse"),
    "constitution": ("endure", "resist poison", "hold breath", "tough", "fatigue", "pain"),
    "intelligence": ("recall", "decode", "analyze", "research", "arcane", "solve"),
    "wisdom": ("notice", "sense", "track", "intuition", "heal", "survive"),
    "charisma": ("convince", "persuade", "deceive", "intimidate", "perform", "negotiate"),
    "speed": ("sprint", "race", "outrun", "react quickly", "catch up"),
}


def _skill_for_check(request: Dict, reason: str) -> str | None:
    requested = str(request.get("skill") or "").strip().lower().replace("-", " ")
    if requested in SKILL_ALIASES:
        return SKILL_ALIASES[requested]
    text = reason.lower()
    for phrase, skill in SKILL_ALIASES.items():
        if phrase.replace("_", " ") in text:
            return skill
    return None


def _attribute_for_check(request: Dict, reason: str, skill: str | None) -> str | None:
    requested = str(request.get("attribute") or "").strip().lower().replace("-", " ")
    if requested in ATTRIBUTE_ALIASES:
        return ATTRIBUTE_ALIASES[requested]
    if skill and skill in SKILL_ATTRIBUTE:
        return SKILL_ATTRIBUTE[skill]
    text = reason.lower()
    for attribute, hints in ATTRIBUTE_REASON_HINTS.items():
        if any(hint in text for hint in hints):
            return attribute
    return None


class GameMaster:
    def __init__(self, provider=None, state: GameState | None = None,
                 memory: CampaignMemory | None = None, rules: RuleLibrary | None = None) -> None:
        self.provider = provider or provider_from_environment()
        self.state = state or GameState()
        self.memory = memory or CampaignMemory()
        self.rules = rules or RuleLibrary()
        self.context_builder = ContextBuilder()
        self.world = WorldSimulator()
        self.ready = True

    def handle_action(self, player_action: str) -> Dict:
        action = player_action.strip()
        if not action:
            return {"narration": "Tell the Game Master what you want to do.", "state": self.state.snapshot()}

        relevant_memories = self.memory.context_for(action)
        relevant_rules = self.rules.retrieve(action)
        context = self.context_builder.build(player_action=action, game_state=self.state.snapshot(),
                                             memories=relevant_memories, rules=relevant_rules)
        result = self.provider.respond(context)
        mechanical_result = None

        if result.get("requires_roll"):
            request = result.get("roll") or {}
            if not isinstance(request, dict):
                request = {}
            reason = str(request.get("reason") or action).strip()
            difficulty = str(request.get("difficulty") or "standard").strip().lower()
            if difficulty not in {"trivial", "easy", "standard", "hard", "very_hard", "extreme"}:
                difficulty = "standard"

            skill = _skill_for_check(request, reason)
            player = self.state.snapshot().get("player", {})
            skills = player.get("skills", {}) if isinstance(player, dict) else {}
            raw_stats = player.get("stats") or player.get("attributes") or {} if isinstance(player, dict) else {}
            attributes = normalize_attributes(raw_stats)
            skill_bonus = float(skills.get(skill, 0)) if skill else 0.0
            attribute = _attribute_for_check(request, reason, skill)
            attribute_value = int(attributes.get(attribute, 0)) if attribute else 0
            attribute_bonus = attribute_check_bonus(attribute_value) if attribute else 0.0
            modifier = skill_bonus + attribute_bonus

            mechanical_result = resolve_check(reason=reason, difficulty=difficulty, modifier=modifier)
            mechanical_result["skill"] = skill
            mechanical_result["attribute"] = attribute
            mechanical_result["attribute_value"] = attribute_value
            mechanical_result["skill_bonus"] = skill_bonus
            mechanical_result["attribute_bonus"] = attribute_bonus

            resolved_context = dict(context)
            resolved_context["mechanical_result"] = mechanical_result
            resolved_context["mechanical_instruction"] = (
                "The rules engine has resolved the requested check using the character's stored skill "
                "bonus and canonical 0-60 attribute scaling. Obey this result exactly, do not reroll, "
                "and narrate its consequence."
            )
            result = self.provider.respond(resolved_context)
            result["requires_roll"] = False
            result["roll"] = mechanical_result

        changes = result.get("state_changes", [])
        self.state.apply_changes(changes)
        for memory in result.get("memories", []):
            self._store_memory(memory, default_category="event")
        for note in result.get("world_notes", []):
            self._store_memory(note, default_category="world")

        narration = str(result.get("narration", "")).strip()
        if narration:
            turn_record = f"Player action: {action}\nGame Master result: {narration}"
            if mechanical_result:
                turn_record += (f"\nMechanical check: {mechanical_result['reason']} | skill "
                                f"{mechanical_result.get('skill') or 'none'} | attribute "
                                f"{mechanical_result.get('attribute') or 'none'} "
                                f"({mechanical_result.get('attribute_value', 0)}) | d20 "
                                f"{mechanical_result['rolls'][0]} + {mechanical_result['modifier']} = "
                                f"{mechanical_result['total']} vs DC {mechanical_result['dc']} | "
                                f"{mechanical_result['outcome']}")
            self.memory.remember(turn_record, category="turn", importance=1, confirmed=True)

        result["state"] = self.state.snapshot()
        result["memory_count"] = len(self.memory.all())
        return result

    def _store_memory(self, memory, default_category: str) -> None:
        if isinstance(memory, str):
            self.memory.remember(memory, category=default_category, importance=2)
        elif isinstance(memory, dict):
            self.memory.remember(memory.get("text", ""), category=memory.get("category", default_category),
                                 importance=memory.get("importance", 2), confirmed=memory.get("confirmed", True))

    def advance_world(self, elapsed_days: int) -> Dict:
        events = self.world.advance(self.state.snapshot(), elapsed_days)
        changes = [event["state_change"] for event in events if "state_change" in event]
        self.state.apply_changes(changes)
        for event in events:
            summary = event.get("summary")
            if summary:
                self.memory.remember(summary, category="world", importance=2)
        return {"events": events, "state": self.state.snapshot()}
