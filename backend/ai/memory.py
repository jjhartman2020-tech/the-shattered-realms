"""Persistent campaign memory primitives for the AI Game Master."""

from typing import Dict, List, Optional


class CampaignMemory:
    """Stores confirmed campaign events and retrieves useful recent context."""

    def __init__(self) -> None:
        self._events: List[Dict] = []

    def remember(
        self,
        text: str,
        category: str = "event",
        importance: int = 1,
        confirmed: bool = True,
    ) -> Dict:
        memory = {
            "text": text.strip(),
            "category": category,
            "importance": max(1, min(5, importance)),
            "confirmed": confirmed,
        }
        if memory["text"]:
            self._events.append(memory)
        return memory

    def recent(self, limit: int = 12, confirmed_only: bool = True) -> List[Dict]:
        events = self._events
        if confirmed_only:
            events = [event for event in events if event.get("confirmed")]
        return events[-limit:]

    def search(self, query: str, limit: int = 8) -> List[Dict]:
        terms = {term.lower() for term in query.split() if len(term) > 2}
        scored = []
        for event in self._events:
            if not event.get("confirmed"):
                continue
            text = event.get("text", "").lower()
            score = sum(1 for term in terms if term in text)
            score += int(event.get("importance", 1))
            if score:
                scored.append((score, event))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [event for _, event in scored[:limit]]

    def all(self) -> List[Dict]:
        return list(self._events)
