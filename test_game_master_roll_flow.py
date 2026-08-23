from tempfile import TemporaryDirectory
import json

import backend.game.combat as combat_module
from backend.ai.game_master import GameMaster, _fallback_check_request
from backend.ai.provider import _parse_json_object
from backend.game.state import GameState


class Memory:
    def __init__(self):
        self.items = []

    def context_for(self, _query):
        return []

    def remember(self, text, **_kwargs):
        self.items.append({"text": text, "confirmed": True, "category": "turn", "importance": 1})

    def recent(self, limit=12, confirmed_only=True):
        items = [item for item in self.items if item.get("confirmed", True)] if confirmed_only else self.items
        return items[-limit:]

    def all(self):
        return list(self.items)

    def clear(self):
        self.items.clear()


class Rules:
    def retrieve(self, _query):
        return []


class Provider:
    def respond(self, context):
        action = str(context.get("player_action") or "")
        if context.get("mechanical_result"):
            return {"narration": "The check is resolved.", "state_changes": [], "memories": [], "world_notes": [], "suggested_actions": []}
        if context.get("combat_result"):
            return {"narration": "The attack is resolved.", "state_changes": [], "memories": [], "world_notes": [], "suggested_actions": []}
        if action == "Sneak past the sensor":
            return {
                "narration": "You approach the sensor.", "requires_roll": True,
                "roll": {"reason": "Sneak past the sensor", "difficulty": "hard", "skill": "stealth"},
                "state_changes": [], "memories": [], "world_notes": [], "suggested_actions": [],
            }
        if action in {"Search the dead body", "Haggle with the merchant for a lower price"}:
            # Deliberately omit the roll. The Python rules fallback must add it.
            return {
                "narration": "The AI incorrectly tries to resolve this immediately.",
                "requires_roll": False, "roll": None, "combat_request": None,
                "state_changes": [], "memories": [], "world_notes": [], "suggested_actions": [],
            }
        return {
            "narration": "You line up the attack.",
            "combat_request": {"type": "attack", "target": "Guard", "attack_attribute": "dexterity"},
            "state_changes": [], "memories": [], "world_notes": [], "suggested_actions": [],
        }


def combatant(name, team, hp, position):
    return {
        "name": name, "team": team, "hp": hp, "max_hp": hp, "position": position,
        "attributes": {"health": 4, "strength": 6, "dexterity": 9, "speed": 3},
        "level": 1, "armor_class": 10, "attack_bonus": 0, "damage": "1d8",
        "movement": 6, "movement_used": 0, "primary_action_used": False,
        "attack_committed": False, "defending": False, "active_defense_ac_bonus": 0,
        "critical_chance_percent": 5, "physical_resistance_percent": 0,
        "defeated": False, "resource": 0, "max_resource": 0,
    }


def main():
    with TemporaryDirectory() as folder:
        hero = combatant("Hero", "player", 20, {"x": 0, "y": 0})
        guard = combatant("Guard", "enemy", 1, {"x": 1, "y": 0})
        initial = {
            "player": {
                "name": "Hero", "character_creation_complete": True,
                "stats": {"health": 4, "dexterity": 9, "agility": 2, "intelligence": 9, "charisma": 6, "speed": 3},
                "skills": {"stealth": 1, "investigation": 2, "persuasion": 1}, "hp": 20, "max_hp": 20,
                "equipped_armor": {
                    "boots": {"name": "Quiet Boots", "slot": "boots", "armor_hp": 2, "weight": 1, "stat_bonus": {"stat": "agility", "amount": 1}}
                },
            },
            "combat": {
                "active": True, "round": 1, "turn_index": 0,
                "order": ["Hero", "Guard"], "combatants": [hero, guard],
                "grid": {"width": 12, "height": 8}, "log": [],
            },
        }
        state = GameState(initial=initial, path=f"{folder}/state.json")
        gm = GameMaster(provider=Provider(), state=state, memory=Memory(), rules=Rules())

        waiting = gm.handle_action("Attack Guard")
        assert waiting["pending_roll"]["kind"] == "attack"
        assert waiting["pending_roll"]["dc"] == 10
        assert state.data["combat"]["combatants"][0]["attack_committed"] is True

        rolls = iter([
            {"expression": "1d20", "rolls": [12], "total": 12},
            {"expression": "1d100", "rolls": [50], "total": 50},
            {"expression": "1d8", "rolls": [4], "total": 4},
        ])
        original_roll = combat_module.roll
        combat_module.roll = lambda _expression: next(rolls)
        try:
            hit = gm.resolve_pending_roll()
            assert hit["pending_roll"]["kind"] == "damage"
            finished = gm.resolve_pending_roll()
            assert finished["pending_roll"] == {}
            assert state.data["combat"]["active"] is False
        finally:
            combat_module.roll = original_roll

        state.data["combat"] = {"active": False}
        check_waiting = gm.handle_action("Sneak past the sensor")
        assert check_waiting["pending_roll"]["kind"] == "check"
        assert check_waiting["pending_roll"]["dc"] == 16
        assert check_waiting["pending_roll"]["modifier"] == 2
        assert "Armor grants +1 Agility" in check_waiting["pending_roll"]["armor_bonus_note"]
        resolved = gm.resolve_pending_roll()
        assert resolved["pending_roll"] == {}
        assert resolved["roll"]["dc"] == 16

        search_waiting = gm.handle_action("Search the dead body")
        assert search_waiting["pending_roll"]["skill"] == "investigation"
        assert search_waiting["pending_roll"]["attribute"] == "intelligence"
        assert search_waiting["pending_roll"]["dc"] == 8
        assert search_waiting["pending_roll"]["modifier"] == 5
        gm.resolve_pending_roll()

        haggle_waiting = gm.handle_action("Haggle with the merchant for a lower price")
        assert haggle_waiting["pending_roll"]["skill"] == "persuasion"
        assert haggle_waiting["pending_roll"]["attribute"] == "charisma"
        assert haggle_waiting["pending_roll"]["dc"] == 12
        assert haggle_waiting["pending_roll"]["modifier"] == 3

        expected_skills = {
            "Investigate the strange clue": "investigation",
            "Convince the guard to let me pass": "persuasion",
            "Bluff my way through the checkpoint": "deception",
            "Intimidate the smuggler": "intimidation",
            "Pick the lock": "lockpicking",
            "Pickpocket the key": "sleight_of_hand",
            "Follow the tracks": "survival",
            "Listen for movement": "perception",
            "Balance across the narrow beam": "acrobatics",
            "Climb the damaged wall": "athletics",
            "Hack the security terminal": "engineering",
            "Treat the injury": "medicine",
        }
        for sample_action, expected_skill in expected_skills.items():
            inferred = _fallback_check_request(sample_action)
            assert inferred is not None and inferred["skill"] == expected_skill, (sample_action, inferred)

        malformed_wrapper = "```json\n" + json.dumps({
            "narration": "The passage divides around a stone pillar.",
            "player_action": "Enter the gate",
            "requires_roll": False,
            "state_changes": [{"type": "set_location", "location": "Bottomless Dungeon - First Landing"}],
            "memories": [], "world_notes": [],
            "suggested_actions": [
                {"text": "Study the stone pillar.", "requires_roll": True, "skill": "intelligence"},
                {"text": "Take the red-marked route.", "requires_roll": False, "skill": None},
                {"text": "Take the blue-marked route.", "requires_roll": False, "skill": None},
            ],
        }) + "\n```"
        parsed = _parse_json_object(malformed_wrapper)
        assert parsed is not None and parsed["state_changes"][0]["type"] == "set_location"

        recovery_memory = Memory()
        recovery_memory.remember("Player action: Enter the gate\nGame Master result: " + malformed_wrapper)
        recovery_state = GameState(initial={
            "player": {
                "name": "Hero", "character_creation_complete": True, "location": "unknown",
                "stats": {"health": 4, "resource": 4}, "hp": 20, "max_hp": 20,
            },
            "combat": {"active": False},
        }, path=f"{folder}/recovery_state.json")
        recovery_gm = GameMaster(provider=Provider(), state=recovery_state, memory=recovery_memory, rules=Rules())
        resumed = recovery_gm.resume_scene()
        assert recovery_state.data["player"]["location"] == "Bottomless Dungeon - First Landing"
        assert len(resumed["suggested_actions"]) == 3
        assert "You are currently at Bottomless Dungeon - First Landing" in resumed["narration"]
        assert '"state_changes"' not in resumed["narration"]

    print("GameMaster combat and non-combat roll pause flow: PASS")


if __name__ == "__main__":
    main()
