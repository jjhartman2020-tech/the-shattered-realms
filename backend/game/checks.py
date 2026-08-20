"""Core d20 check resolution for The Shattered Realms.

The AI may decide that an action needs a check, but this module owns the actual
roll and success/failure result. The model never gets to invent the number.
"""

from typing import Dict

from .dice import roll

DIFFICULTY_DCS = {"trivial": 5, "easy": 8, "standard": 12, "hard": 16,
                  "very_hard": 20, "extreme": 25}


def resolve_check(*, modifier: float = 0, dc: int | None = None,
                  difficulty: str = "standard", expression: str = "1d20",
                  reason: str = "") -> Dict:
    """Roll and resolve one mechanical check using deterministic modifiers."""
    if dc is None:
        key = difficulty.strip().lower().replace(" ", "_")
        if key not in DIFFICULTY_DCS:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        dc = DIFFICULTY_DCS[key]
    if dc < 1 or dc > 100:
        raise ValueError("DC must be between 1 and 100")

    base = roll(expression)
    applied_modifier = float(modifier)
    total = float(base["total"]) + applied_modifier
    natural_1 = bool(base.get("natural_1"))
    natural_20 = bool(base.get("natural_20"))
    if natural_1:
        outcome, success = "critical_failure", False
    elif natural_20:
        outcome, success = "critical_success", True
    elif total >= dc:
        outcome, success = "success", True
    else:
        outcome, success = "failure", False

    return {"reason": reason.strip(), "expression": base["expression"],
            "rolls": base["rolls"], "base_total": base["total"],
            "modifier": applied_modifier, "total": total, "dc": int(dc),
            "difficulty": difficulty, "success": success, "outcome": outcome,
            "margin": total - dc, "natural_1": natural_1, "natural_20": natural_20}
