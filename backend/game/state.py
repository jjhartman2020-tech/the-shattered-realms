"""Authoritative persistent state for a Shattered Realms campaign."""

from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Dict, List


DEFAULT_STATE = {
    "campaign": {"name": "Untitled Campaign", "genre": "fantasy", "day": 1, "time": "morning"},
    "player": {
        "name": "Traveler", "level": 1, "hp": 10, "max_hp": 10, "mana": 0, "max_mana": 0,
        "stats": {
            "strength": 10,
            "agility": 10,
            "speed": 10,
            "durability": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        },
        "skills": {
            "athletics": 0, "acrobatics": 0, "stealth": 0, "sleight_of_hand": 0,
            "perception": 0, "investigation": 0, "survival": 0,
            "persuasion": 0, "deception": 0, "intimidation": 0,
        },
        "inventory": [], "conditions": [], "location": "unknown",
    },
    "party": [], "npcs": {}, "factions": {}, "locations": {}, "quests": {}, "world_flags": {}, "turn": 0,
}


class GameState:
    """Owns campaign truth. The AI proposes changes; this class persists them."""

    def __init__(self, initial: Dict | None = None, path: str | None = None) -> None:
        default_path = os.getenv("SHATTERED_REALMS_STATE_FILE", "data/campaign_state.json")
        self.path = Path(path or default_path)
        self.data = deepcopy(DEFAULT_STATE)
        saved = self._load()
        if saved:
            self._deep_merge(self.data, saved)
        if initial:
            self._deep_merge(self.data, deepcopy(initial))

    def _load(self) -> Dict:
        if not self.path.exists():
            return {}
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            return loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)

    def snapshot(self) -> Dict:
        return deepcopy(self.data)

    def apply_changes(self, changes: List[Dict]) -> None:
        if not isinstance(changes, list):
            changes = []
        for change in changes:
            if not isinstance(change, dict):
                continue
            path = change.get("path")
            if not isinstance(path, str) or not path.strip() or "value" not in change:
                continue
            self.set_path(path, change["value"], save=False)
        self.data["turn"] = int(self.data.get("turn", 0)) + 1
        self.save()

    def set_path(self, path: str, value, save: bool = True) -> None:
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
        if save:
            self.save()

    @classmethod
    def _deep_merge(cls, target: Dict, source: Dict) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                cls._deep_merge(target[key], value)
            else:
                target[key] = deepcopy(value)
