"""Leveling and progression rules for The Shattered Realms."""

from __future__ import annotations

from typing import Dict

MAX_LEVEL = 100
SKILL_POINTS_PER_LEVEL = 3

ABILITY_TIER_COSTS = {
    "beginner": 1,
    "novice": 3,
    "expert": 6,
    "master": 10,
    "legendary": 15,
}


def ability_points_for_reaching_level(level: int) -> int:
    """AP awarded when the player reaches ``level``."""
    level = max(1, min(MAX_LEVEL, int(level)))
    if level <= 1:
        return 0
    if level <= 10:
        return 1
    if level <= 20:
        return 2
    if level <= 30:
        return 3
    if level <= 40:
        return 4
    if level <= 50:
        return 5
    return 6


def xp_required_for_next_level(level: int) -> int:
    """XP Orbs required to advance from ``level`` to ``level + 1``.

    The curve starts very quickly and gradually steepens through Level 100.
    Level 1 -> 2 costs 5 XP Orbs. The formula is deterministic so the UI,
    saves, and AI all use one source of truth instead of a hand-maintained table.
    """
    level = max(1, min(MAX_LEVEL, int(level)))
    if level >= MAX_LEVEL:
        return 0
    return max(5, round(5 * (1.06 ** (level - 1)) + 1.2 * (level - 1)))


def total_skill_points_earned(level: int, starting_skill_points: int = 42) -> int:
    level = max(1, min(MAX_LEVEL, int(level)))
    return int(starting_skill_points) + (level - 1) * SKILL_POINTS_PER_LEVEL


def total_ability_points_earned(level: int) -> int:
    level = max(1, min(MAX_LEVEL, int(level)))
    return sum(ability_points_for_reaching_level(reached) for reached in range(2, level + 1))


def apply_xp_orbs(player: Dict, amount: int) -> Dict:
    """Award XP Orbs, apply all earned level-ups, and return a summary.

    ``xp_orbs`` stores progress toward the next level, not lifetime XP. Extra XP
    carries over through multiple level-ups. Level-ups grant +3 SP and a tiered
    amount of AP based on the level reached. No automatic HP is granted.
    """
    amount = max(0, int(amount))
    old_level = max(1, min(MAX_LEVEL, int(player.get("level", 1) or 1)))
    level = old_level
    xp = max(0, int(player.get("xp_orbs", 0) or 0)) + amount
    sp_gained = 0
    ap_gained = 0
    levels_gained = []

    while level < MAX_LEVEL:
        requirement = xp_required_for_next_level(level)
        if xp < requirement:
            break
        xp -= requirement
        level += 1
        sp_gained += SKILL_POINTS_PER_LEVEL
        gained_ap = ability_points_for_reaching_level(level)
        ap_gained += gained_ap
        levels_gained.append({
            "level": level,
            "skill_points": SKILL_POINTS_PER_LEVEL,
            "ability_points": gained_ap,
        })

    if level >= MAX_LEVEL:
        xp = 0

    player["level"] = level
    player["xp_orbs"] = xp
    player["skill_points_unspent"] = max(0, int(player.get("skill_points_unspent", player.get("attribute_points_unspent", 0)) or 0)) + sp_gained
    player["attribute_points_unspent"] = player["skill_points_unspent"]  # legacy save alias
    player["ability_points"] = max(0, int(player.get("ability_points", 0) or 0)) + ap_gained

    return {
        "xp_awarded": amount,
        "old_level": old_level,
        "new_level": level,
        "levels_gained": levels_gained,
        "skill_points_gained": sp_gained,
        "ability_points_gained": ap_gained,
        "xp_orbs_remaining": xp,
        "xp_to_next_level": xp_required_for_next_level(level),
        "max_level": MAX_LEVEL,
    }
