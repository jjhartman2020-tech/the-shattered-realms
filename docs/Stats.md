# Stats.md

Version: 1.3
Status: In Development

---

# Table of Contents

1. Stat Philosophy
2. Starting Attribute Points
3. Leveling
4. Attribute Caps
5. Universal Scaling Rules
6. Health
7. Mana
8. Strength
9. Dexterity
10. Constitution
11. Intelligence
12. Wisdom
13. Charisma
14. Speed
15. Attribute Milestones
16. Attribute Requirements
17. Balancing
18. Future Attributes

---

# 1. Stat Philosophy

## Design Goals

- Stats should be easy to read at a glance.
- Mechanical roll bonuses use whole numbers only.
- Attribute investment should create clear thresholds and meaningful build choices.
- Stats should affect combat, exploration, dialogue, equipment, and world interactions.
- Players should be free to build nearly any type of character.
- The game uses its own 0-30 attribute system rather than traditional D&D ability-score modifier math.

---

# 2. Starting Attribute Points

## Character Creation

- Every new character begins with **60 Attribute Points**.
- Players may distribute these points however they choose.
- AI-generated classes provide a recommended starting allocation, but players can freely modify it before beginning the game.
- The nine attributes are Health, Mana, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma, and Speed.

---

# 3. Leveling

## Attribute Points

- Every level grants **3 Attribute Points**.
- Players may allocate them however they choose.
- Stats can be increased at every level.
- Each level after Level 1 also grants **+5 Maximum Health** and **+1 Ability Point** as defined in the progression rules.

---

# 4. Attribute Caps

## Natural Cap

- Every attribute has a natural maximum of **30**.
- Base attributes cannot permanently exceed 30.
- Equipment, buffs, blessings, artifacts, abilities, and world effects may temporarily or specially exceed the natural cap.

---

# 5. Universal Scaling Rules

These formulas define the first playable balance pass for the 0-30 system.

## Universal Attribute Modifier

For d20 rolls, every full 3 points in the relevant attribute grants +1.

`Attribute Modifier = floor(Attribute / 3)`

There are no fractional roll modifiers.

Examples:

- 0-2 Strength = +0
- 3-5 Strength = +1
- 6-8 Strength = +2
- 9-11 Strength = +3
- 12-14 Strength = +4
- 15-17 Strength = +5
- 18-20 Strength = +6
- 21-23 Strength = +7
- 24-26 Strength = +8
- 27-29 Strength = +9
- 30 Strength = +10

Example: **17 Strength gives +5 to Strength rolls.**

The same modifier rule applies to Dexterity, Constitution, Intelligence, Wisdom, Charisma, and Speed rolls.

The AI Game Master chooses which attribute is relevant, but the engine calculates the modifier.

## Attack Accuracy

Attack rolls use the same whole-number attribute modifier:

- Strength-based melee attacks: `floor(Strength / 3)`
- Dexterity-based finesse attacks: `floor(Dexterity / 3)`
- Ranged attacks: `floor(Dexterity / 3)`

Weapons, abilities, conditions, positioning, and proficiency systems may add separate modifiers.

## Defense

Base Armor Class is 10 before equipment and temporary effects.

Natural defensive contribution uses whole numbers:

`Defense Bonus = floor(Dexterity / 9) + floor(Constitution / 15) + floor(Speed / 15)`

This keeps defensive stats relevant while preventing raw attributes alone from making characters nearly unhittable.

## Initiative

`Initiative Bonus = floor(Speed / 3) + floor(Dexterity / 6)`

Speed is the primary initiative attribute; Dexterity provides a smaller secondary contribution.

## Movement

Base tactical movement is 6 grid spaces.

`Movement = 6 + floor(Speed / 6)`

At 30 Speed, natural movement is 11 spaces before other effects.

## Damage Scaling

Strength-based physical attacks gain a whole-number damage bonus:

`Strength Damage Bonus = floor(Strength / 6)`

At 30 Strength, the natural Strength damage bonus is +5 before weapon, ability, and other modifiers.

### Accuracy Margin Damage

A successful attack that beats the target's Armor Class by a large amount deals extra precision/quality damage. This makes a very accurate hit meaningfully better than a hit that barely connects.

`Accuracy Margin = max(0, Attack Total - Armor Class)`

`Accuracy Margin Damage Bonus = floor(Accuracy Margin / 3)`

Examples:

- Attack Total 10 vs AC 10 = +0 damage
- Attack Total 12 vs AC 10 = +0 damage
- Attack Total 13 vs AC 10 = +1 damage
- Attack Total 16 vs AC 10 = +2 damage
- Attack Total 19 vs AC 10 = +3 damage

This bonus is flat damage and is added once. Critical hits still roll the weapon damage dice one additional time; they do not double the Accuracy Margin Damage Bonus.

A natural 1 is still an automatic miss and deals no damage regardless of bonuses. A natural 20 is still an automatic critical hit.

## Critical Chance

Base critical chance is 5% unless a weapon, ability, or campaign rule states otherwise.

`Critical Chance = 5% + floor(Dexterity / 3)%`

At 30 Dexterity, natural critical chance is 15% before other effects.

A **natural 20 on an attack roll is always a critical hit** regardless of the normal critical-chance roll. A critical hit rolls the attack's weapon damage dice one additional time, while flat damage bonuses are added only once. Non-natural-20 hits may still become critical hits through the normal Critical Chance formula.

## Physical Resistance

`Physical Resistance = floor(Constitution / 3)%`

At 30 Constitution, natural physical damage resistance is 10% before armor, abilities, or special effects.

## Status Resistance

`Status Resistance = floor(Constitution / 3) x 2%`

At 30 Constitution, natural status resistance is 20% before other modifiers.

These formulas are balance constants and may be tuned later, but changes must remain documented here before the engine is changed.

---

# 6. Health

## Description

Health directly increases the character's Maximum Health pool.

## Combat Effects

`Maximum Health = max(1, Health + 5 x (Level - 1))`

The +5 per level comes from the progression system and is separate from Attribute Point spending.

## World Effects

Health may be referenced by survival challenges, endurance events, environmental hazards, and campaign-specific mechanics.

---

# 7. Mana

## Description

Mana directly determines the character's base Maximum Mana.

## Spellcasting

`Maximum Mana = Mana`

Abilities may consume Mana according to their own documented costs.

## Mana Regeneration

Regeneration rules are defined separately and are not created by the Mana stat unless an ability or effect says otherwise.

---

# 8. Strength

## Description

Strength represents raw physical power.

## Rolls

Strength rolls use `floor(Strength / 3)`.

## Damage

Strength-based physical damage gains `floor(Strength / 6)` bonus damage.

## Accuracy

Strength-based melee attacks use the Strength modifier for attack accuracy.

## Weapon Requirements

Weapons may require a minimum raw Strength value.

## Environmental Interaction

Strength governs forcing doors, lifting, breaking, grappling, shoving, and similar physical actions.

---

# 9. Dexterity

## Description

Dexterity represents precision, coordination, finesse, and reflex control.

## Rolls

Dexterity rolls use `floor(Dexterity / 3)`.

## Accuracy

Finesse and ranged attacks use the Dexterity modifier for accuracy.

## Critical Chance

Dexterity increases critical chance using the universal Critical Chance formula.

## Dodge

Dexterity contributes to natural Defense.

---

# 10. Constitution

## Description

Constitution represents physical toughness and resistance.

## Rolls

Constitution rolls use `floor(Constitution / 3)`.

## Defense

Constitution contributes to natural Defense.

## Physical Resistance

Constitution provides 1% physical resistance for every full 3 points.

## Status Resistance

Constitution provides 2% status resistance for every full 3 points.

---

# 11. Intelligence

## Description

Intelligence represents reasoning, technical knowledge, arcane understanding, and learned expertise.

## Rolls

Intelligence rolls use `floor(Intelligence / 3)`.

## Spell Power

Intelligence-based spell systems may use the Intelligence modifier and raw Intelligence for requirements. Exact spell damage rules remain part of the magic system.

---

# 12. Wisdom

## Description

Wisdom represents awareness, judgment, intuition, and spiritual understanding.

## Rolls

Wisdom rolls use `floor(Wisdom / 3)`.

## Healing and Divine Magic

Wisdom-based healing and divine systems may use the Wisdom modifier and raw Wisdom for requirements.

---

# 13. Charisma

## Description

Charisma represents presence, influence, leadership, and social force.

## Rolls

Persuasion, Deception, Intimidation, Performance, leadership, and similar Charisma rolls use `floor(Charisma / 3)` unless context makes another attribute more appropriate.

## Trading

Baseline trading influence improves by 1% for every full 3 Charisma, up to 10% at 30 Charisma.

Exact merchant pricing remains part of the economy system.

---

# 14. Speed

## Description

Speed represents movement quickness, reaction speed, and combat tempo.

## Rolls

Speed rolls use `floor(Speed / 3)`.

## Movement

Movement follows the universal movement formula.

## Initiative

Speed is the primary initiative attribute.

## Dodge

Speed contributes to natural Defense.

---

# 15. Attribute Milestones

Specific abilities, equipment, dialogue options, and world interactions may require raw attribute thresholds.

Milestones must be defined by the relevant system rather than automatically granted by every attribute.

---

# 16. Attribute Requirements

Raw attribute values may be used as requirements for weapons, armor, shields, magic, companions, dialogue, abilities, and environmental interactions.

Requirements must always be visible or logically discoverable to the player when relevant.

---

# 17. Balancing

## AI Validation

The AI Game Master may choose the relevant attribute, target difficulty, or contextual modifiers, but may not invent the player's attribute values or mechanical roll result.

## Preventing Overpowered Builds

- Raw base attributes cap at 30.
- Core attribute roll modifiers cap naturally at +10.
- Defense pulls from several attributes at slower rates.
- Combat difficulty should rely on tactics, positioning, resources, and enemy behavior rather than stat inflation alone.

## Respec Rules

Respec rules remain to be finalized.

---

# 18. Future Attributes

Possible future stats include Luck, Faith, Corruption, and Reputation.

These are not part of the nine-attribute base progression unless formally added to the progression documentation.
