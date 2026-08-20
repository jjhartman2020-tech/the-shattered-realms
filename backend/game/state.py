"""Authoritative runtime state for a Shattered Realms campaign."""

from copy import deepcopy
from typing import Dict, List


DEFAULT_STATE = {
    "campaign": {
        "name": "Untitled Campaign",
        "genre": "fantasy",
        "day": 1,
        "time": "morning",
    },
    "player": {
        "name": "Traveler",
        "level": 1,
        "hp": 10,
        "max_hp": 10,
        "mana": 0,
        "max_mana": 0,
        "inventory": [],
        "conditions": [],
        "location": "unknown",
    },
    "party": [],
    "npcs": {},
    "factions": {},
    "locations": {},
    "quests": {},
    "world_flags": {},
    "turn": 0,
}


class GameState:
    """Owns current campaign facts. The AI proposes changes; this class applies them."""

    def __init__(self, initial: Dict | None = None) -> None:
        self.data = deepcopy(DEFAULT_STATE)
        if initial:
            self.data.update(deepcopy(initial))

    def snapshot(self) -> Dict:
        return deepcopy(self.data)

    def apply_changes(self, changes: List[Dict]) -> None:
        for change in changes:
            path = change.get("path")
            if not path or "value" not in change:
                continue
            self.set_path(path, change["value"])
        self.data["turn"] = int(self.data.get("turn", 0)) + 1

    def set_path(self, path: str, value) -> None:
        keys = [key for key in path.split(".") if key]
        if not keys:
            return
        node = self.data
        for key in keys[:-1]:
            child = node.get(key)
            if not isinstance(child, dict):
                child = {}
                node[key] = child
            node = child
        node[keys[-1]] = value
