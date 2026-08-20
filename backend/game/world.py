"""Persistent-world simulation helpers."""

from typing import Dict, List


class WorldSimulator:
    """Advances important world processes without micromanaging every actor."""

    def advance(self, state: Dict, elapsed_days: int = 0) -> List[Dict]:
        events: List[Dict] = []
        if elapsed_days <= 0:
            return events

        campaign = state.get("campaign", {})
        old_day = int(campaign.get("day", 1))
        new_day = old_day + elapsed_days
        events.append({
            "type": "time_advanced",
            "from_day": old_day,
            "to_day": new_day,
            "state_change": {"path": "campaign.day", "value": new_day},
        })

        for faction_id, faction in state.get("factions", {}).items():
            goal = faction.get("active_goal") if isinstance(faction, dict) else None
            if goal:
                events.append({
                    "type": "faction_progress",
                    "faction": faction_id,
                    "summary": f"{faction_id} continues pursuing: {goal}",
                })

        return events
