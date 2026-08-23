from tempfile import TemporaryDirectory
from pathlib import Path
import base64
from types import SimpleNamespace

import backend.api as api
from backend.ai.game_master import GameMaster
from backend.game.state import GameState


class Provider:
    def respond(self, _context):
        return {"narration": "", "state_changes": [], "memories": [], "world_notes": [], "suggested_actions": []}


class Images:
    def __init__(self):
        self.generate_calls = 0
        self.edit_calls = 0

    def generate(self, **_kwargs):
        self.generate_calls += 1
        tiny_png = base64.b64encode(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        ).decode("ascii")
        return SimpleNamespace(data=[SimpleNamespace(b64_json=tiny_png)])

    def edit(self, **_kwargs):
        self.edit_calls += 1
        tiny_png = base64.b64encode(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        ).decode("ascii")
        return SimpleNamespace(data=[SimpleNamespace(b64_json=tiny_png)])


class Memory:
    def context_for(self, _query): return []
    def remember(self, *_args, **_kwargs): pass
    def all(self): return []


class Rules:
    def retrieve(self, _query): return []


def main():
    with TemporaryDirectory() as folder:
        state = GameState(path=f"{folder}/state.json")
        player = state.data["player"]
        player.update({
            "name": "Hub Tester", "character_creation_complete": True, "level": 2,
            "stats": {
                "health": 10, "resource": 10, "strength": 10, "dexterity": 12,
                "agility": 0, "constitution": 0, "intelligence": 0, "wisdom": 0,
                "charisma": 0, "speed": 0, "defense": 0, "luck": 0, "magic": 0,
            },
            "skill_points_unspent": 3, "attribute_points_unspent": 3,
            "ability_points": 2, "equipped_abilities": [], "unlocked_abilities": [],
            "inventory": [{
                "name": "Test Breastplate", "type": "armor", "slot": "breastplate",
                "armor_hp": 9, "max_armor_hp": 9, "weight": 14,
                "stat_bonus": {"stat": "defense", "amount": 1},
            }],
            "equipped_armor": {}, "base_movement_without_armor": 6, "movement": 6,
        })
        state.data["combat"] = {"active": False}
        state._migrate_player()
        player = state.data["player"]
        player["hp"] = player["max_hp"] - 10
        old_max_hp = player["max_hp"]
        state.save()

        gm = GameMaster(provider=Provider(), state=state, memory=Memory(), rules=Rules())
        original_gm = api.GAME_MASTER
        original_portrait_path = api.PORTRAIT_PATH
        try:
            api.GAME_MASTER = gm
            api.PORTRAIT_PATH = Path(folder) / "portrait.png"
            api._clear_character_hub_session()

            stat_result = api._character_hub_action({"stat": "health", "amount": 1}, "spend_sp")
            assert stat_result["ok"] is True
            assert stat_result["state"]["player"]["stats"]["health"] == 11
            assert stat_result["state"]["player"]["skill_points_unspent"] == 2
            assert stat_result["state"]["player"]["max_hp"] == old_max_hp + 5
            assert stat_result["state"]["player"]["hp"] == old_max_hp - 5

            equip_result = api._character_hub_action({"inventory_index": 0}, "equip_armor")
            assert equip_result["ok"] is True
            assert equip_result["state"]["player"]["armor"] == 9
            assert equip_result["state"]["player"]["armor_weight"] == 14
            assert equip_result["state"]["player"]["movement"] == 5

            gm.state.data["player"]["equipped_armor"]["breastplate"]["armor_hp"] = 4
            unequip_result = api._character_hub_action({"slot": "breastplate"}, "unequip_armor")
            assert unequip_result["ok"] is True
            assert unequip_result["state"]["player"]["armor"] == 0
            assert unequip_result["state"]["player"]["movement"] == 6
            assert unequip_result["state"]["player"]["inventory"][0]["armor_hp"] == 4

            choices_result = api._character_hub_action({}, "generate_abilities")
            assert choices_result["ok"] is True
            assert len(choices_result["ability_choices"]) >= 1
            learn_result = api._character_hub_action({"choice_index": 0}, "learn_ability")
            assert learn_result["ok"] is True
            assert len(learn_result["state"]["player"]["equipped_abilities"]) == 1
            assert learn_result["state"]["player"]["ability_points"] == 1

            empty_portrait = api._character_hub_action({}, "load_portrait")
            assert empty_portrait["ok"] is True
            assert empty_portrait["portrait_available"] is False

            gm.state.data["player"]["character_creation_complete"] = False
            old_save_portrait = api._character_hub_action({}, "load_portrait")
            assert old_save_portrait["ok"] is True
            gm.state.data["player"]["character_creation_complete"] = True

            images = Images()
            gm.provider.client = SimpleNamespace(images=images)
            generated_portrait = api._character_hub_action({}, "generate_portrait")
            assert generated_portrait["ok"] is True
            assert generated_portrait["portrait_available"] is True
            assert generated_portrait["portrait_stale"] is False
            assert api.PORTRAIT_PATH.is_file()
            assert images.generate_calls == 1

            exact_empty = api._character_hub_action({}, "load_portrait")
            assert exact_empty["portrait_cached"] is True
            assert exact_empty["portrait_stale"] is False

            second_equip = api._character_hub_action({"inventory_index": 0}, "equip_armor")
            assert second_equip["ok"] is True
            stale_armor = api._character_hub_action({}, "load_portrait")
            assert stale_armor["portrait_available"] is True
            assert stale_armor["portrait_stale"] is True
            assert images.edit_calls == 0

            edited_portrait = api._character_hub_action({}, "generate_portrait")
            assert edited_portrait["ok"] is True
            assert edited_portrait["portrait_available"] is True
            assert images.edit_calls == 1

            second_unequip = api._character_hub_action({"slot": "breastplate"}, "unequip_armor")
            assert second_unequip["ok"] is True
            restored_empty = api._character_hub_action({}, "load_portrait")
            assert restored_empty["portrait_cached"] is True
            assert restored_empty["portrait_stale"] is False
            assert images.generate_calls == 1
            assert images.edit_calls == 1
        finally:
            api.GAME_MASTER = original_gm
            api.PORTRAIT_PATH = original_portrait_path

    print("Character Hub AP/SP/armor backend flow: PASS")


if __name__ == "__main__":
    main()
