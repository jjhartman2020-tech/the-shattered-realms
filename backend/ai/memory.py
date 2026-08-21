"""Persistent campaign memory primitives for the AI Game Master."""

import json
from pathlib import Path
from typing import Dict, List


DEFAULT_MEMORY_PATH = Path(".shattered_realms/default_campaign_memory.json")


class CampaignMemory:
    """Stores confirmed campaign facts and persists them between game sessions."""

    def __init__(self, path: str | Path = DEFAULT_MEMORY_PATH) -> None:
        self.path = Path(path)
        self._events: List[Dict] = []
        self.load()

    def remember(self, text: str, category: str = "event", importance: int = 1, confirmed: bool = True) -> Dict:
        memory = {"text": text.strip(), "category": category, "importance": max(1, min(5, importance)), "confirmed": confirmed}
        if memory["text"] and not self._is_duplicate(memory):
            self._events.append(memory); self.save()
        return memory

    def _is_duplicate(self, memory: Dict) -> bool:
        text = memory.get("text", "").strip().lower(); category = memory.get("category", "event")
        return any(event.get("text", "").strip().lower() == text and event.get("category", "event") == category for event in self._events)

    def recent(self, limit: int = 12, confirmed_only: bool = True) -> List[Dict]:
        events = self._events
        if confirmed_only: events = [event for event in events if event.get("confirmed")]
        return events[-limit:]

    def search(self, query: str, limit: int = 8) -> List[Dict]:
        terms = {term.lower() for term in query.split() if len(term) > 2}; scored = []
        for event in self._events:
            if not event.get("confirmed"): continue
            text = event.get("text", "").lower(); score = sum(1 for term in terms if term in text) + int(event.get("importance", 1))
            if score: scored.append((score, event))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [event for _, event in scored[:limit]]

    def context_for(self, query: str, limit: int = 12) -> List[Dict]:
        selected: List[Dict] = []; seen = set()
        for event in self.search(query, limit=limit):
            key = (event.get("category"), event.get("text"))
            if key not in seen: selected.append(event); seen.add(key)
        for event in reversed(self.recent(limit=limit)):
            key = (event.get("category"), event.get("text"))
            if key not in seen: selected.append(event); seen.add(key)
            if len(selected) >= limit: break
        return selected[:limit]

    def clear(self) -> None:
        """Erase all remembered canon when starting a completely new campaign."""
        self._events = []
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._events, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.path.exists(): return
        try: data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError): return
        if isinstance(data, list): self._events = [item for item in data if isinstance(item, dict)]

    def all(self) -> List[Dict]:
        return list(self._events)
