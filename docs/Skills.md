# Skills.md

Version: 2.0
Status: In Development

This file extends the skill mappings defined in `Stats.md`. If a skill-to-attribute mapping conflicts with `Stats.md`, the core attribute rules in `Stats.md` remain authoritative until reconciled.

---

# 1. Skill Philosophy

Skills exist to describe **what kind of action the character is attempting** and to help the AI Game Master select the correct governing attribute.

Skills do **not** have separate points, proficiency ranks, expertise ranks, training points, or level-based skill bonuses.

The character's core attributes remain the mechanical source of skill strength.

---

# 2. Skill Check Formula

A normal skill check is:

`d20 + Governing Attribute Modifier + Other Explicit Modifiers`

There is no automatic Proficiency or Expertise bonus.

Example:

A character with Agility 18 has a +6 Agility modifier. Their normal Stealth check is:

`d20 + 6`

Equipment, abilities, conditions, environmental effects, or other explicit mechanics may add separate modifiers when documented.

---

# 3. Default Skill Mapping

## Strength

- Athletics
- Grappling
- Might

## Dexterity

- Sleight of Hand
- Lockpicking
- Pickpocketing
- Precision

## Agility

- Acrobatics
- Stealth
- Evasion

## Constitution

- Endurance
- Fortitude

## Intelligence

- Investigation
- Arcana
- History
- Nature
- Engineering

## Wisdom

- Perception
- Insight
- Survival
- Medicine
- Animal Handling

## Charisma

- Persuasion
- Deception
- Intimidation
- Performance
- Leadership

## Magic

- Spellcasting
- Channeling

Health, Resource, Speed, Defense, and Luck may be rolled directly when the action specifically tests those attributes. They do not need artificial permanent skills.

---

# 4. Contextual Attribute Checks

The mappings above are defaults rather than absolute restrictions.

When the player's described method clearly uses another attribute, the AI Game Master may pair the skill with that attribute as long as the choice follows the fiction and is not being changed simply to give a higher bonus.

Examples:

- Intimidation normally uses Charisma, but bending an iron bar to frighten someone may use **Intimidation (Strength)**.
- Escaping a grapple through body movement may use Agility, while overpowering the opponent may use Strength.
- Identifying a spell uses **Arcana (Intelligence)**, while overpowering unstable magic may use **Channeling (Magic)**.

The Python rules engine remains authoritative for the actual attribute value, modifier, roll, DC, and result.

---

# 5. Character Growth

Characters improve skill checks primarily by improving their governing core attributes.

The game does not track separate skill-training progression. Story events, teachers, backgrounds, or special features may still matter narratively or grant an explicit documented bonus, but they do not create a universal Proficiency/Expertise subsystem.

---

# 6. Design Summary

- Attribute Points are spent only on core attributes.
- Skills do not receive separate points.
- Skills do not use Proficiency or Expertise.
- Skill checks normally equal `d20 + governing attribute modifier`.
- Context may change the governing attribute when justified.
- Explicit equipment, ability, status, or story mechanics may add separately documented modifiers.
