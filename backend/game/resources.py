"""Class-resource rules for The Shattered Realms.

Sources of truth:
- docs/Classes.md
- docs/Stats.md
- docs/Abilities.md

The core Resource attribute determines pool capacity and combat regeneration.
The character's generated/default class determines the resource's displayed name.
"""

CLASS_RESOURCE_NAMES = {
    "warrior": "Stamina",
    "rogue": "Energy",
    "paladin": "Divine Power",
    "ranger": "Focus",
    "mage": "Mana",
    "cleric": "Divine Power",
    "druid": "Mana",
    "monk": "Ki",
    "bard": "Focus",
    "barbarian": "Rage",
    "sorcerer": "Mana",
    "warlock": "Shadow Energy",
}

DEFAULT_RESOURCE_NAME = "Mana"
NATURAL_RESOURCE_ATTRIBUTE_CAP = 100


def resource_name_for_class(class_name: str | None) -> str:
    key = str(class_name or "").strip().lower()
    return CLASS_RESOURCE_NAMES.get(key, DEFAULT_RESOURCE_NAME)


def resource_key(resource_name: str | None) -> str:
    return str(resource_name or DEFAULT_RESOURCE_NAME).strip().lower().replace(" ", "_")


def max_resource_from_attribute(resource_attribute: int) -> int:
    """Every complete 2 Resource attribute points grant 10 class-resource points."""
    score = max(0, min(NATURAL_RESOURCE_ATTRIBUTE_CAP, int(resource_attribute)))
    return (score // 2) * 10


def resource_regeneration_per_round(resource_attribute: int) -> int:
    """Every complete 3 Resource points regenerate 1 class-resource point per round."""
    score = max(0, min(NATURAL_RESOURCE_ATTRIBUTE_CAP, int(resource_attribute)))
    return score // 3


def max_resource_from_mana(mana_attribute: int) -> int:
    """Backward-compatible alias for old runtime/save code.

    Old saves stored the universal resource-capacity attribute under ``mana``.
    New code should call :func:`max_resource_from_attribute` with Resource.
    """
    return max_resource_from_attribute(mana_attribute)
