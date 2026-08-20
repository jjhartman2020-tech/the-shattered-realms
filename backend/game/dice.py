"""Dice engine for checks, combat, and generated encounters."""

import random
import re
from typing import Dict, List


DICE_PATTERN = re.compile(r"^(?P<count>\d*)d(?P<sides>\d+)(?P<modifier>[+-]\d+)?$", re.I)


def roll(expression: str = "1d20") -> Dict:
    cleaned = expression.replace(" ", "").lower()
    match = DICE_PATTERN.match(cleaned)
    if not match:
        raise ValueError(f"Invalid dice expression: {expression}")

    count = int(match.group("count") or 1)
    sides = int(match.group("sides"))
    modifier = int(match.group("modifier") or 0)

    if count < 1 or count > 100 or sides < 2 or sides > 1000:
        raise ValueError("Dice expression is outside supported limits")

    rolls: List[int] = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + modifier

    return {
        "expression": cleaned,
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
        "natural_1": count == 1 and sides == 20 and rolls[0] == 1,
        "natural_20": count == 1 and sides == 20 and rolls[0] == 20,
    }
