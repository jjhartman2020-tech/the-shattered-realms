"""Class-resource rules for The Shattered Realms.

Source of truth:
- docs/Classes.md
- docs/Stats.md
- docs/Abilities.md

The 0-30 Mana attribute is the universal resource-capacity attribute.
The class determines the resource's displayed name.
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


def resource_name_for_class(class_name: str | None) -> str:
    key = str(class_name or "").strip().lower()
    return CLASS_RESOURCE_NAMES.get(key, DEFAULT_RESOURCE_NAME)


def resource_key(resource_name: str | None) -> str:
    return str(resource_name or DEFAULT_RESOURCE_NAME).strip().lower().replace(" ", "_")


def max_resource_from_mana(mana_attribute: int) -> int:
    """Every complete 2 Mana attribute points grant 10 class-resource points."""
    score = max(0, min(30, int(mana_attribute)))
    return (score // 2) * 10
