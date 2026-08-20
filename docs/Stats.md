# Stats.md

Version: 1.1
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

- Every stat should feel meaningful.
- Every point invested should matter.
- Stats should affect combat, exploration, dialogue, equipment, and world interactions.
- Players should be free to build nearly any type of character.
- The game uses its own 0-60 attribute system rather than traditional D&D ability-score modifier math.

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

- Every level grants **5 Attribute Points**.
- Players may allocate them however they choose.
- Stats can be increased at every level.
- Each level after Level 1 also grants **+5 Maximum Health** and **+1 Ability Point** as defined in the progression rules.

---

# 4. Attribute Caps

## Natural Cap

- Every attribute has a natural maximum of **60**.
- Base attributes cannot permanently exceed 60.
- Equipment, buffs, blessings, artifacts, abilities, and world effects may temporarily or specially exceed the natural cap.

---

# 5. Universal Scaling Rules

These formulas define the first playable balance pass for the 0-60 system.

## Check Bonus

For d20 checks, the relevant raw attribute contributes:

`Attribute Check Bonus = Attribute / 6`

The result may be fractional. This allows every single Attribute Point to matter.

Examples:

- 6 Strength = +1.0
- 15 Strength = +2.5
- 30 Strength = +5.0
- 60 Strength = +10.0

The AI Game Master chooses which attribute is relevant, but the engine calculates the bonus.

## Attack Accuracy

- Strength-based melee attacks: `Strength / 12`
- Dexterity-based finesse attacks: `Dexterity / 12`
- Ranged attacks: `Dexterity / 12`

Maximum natural attribute contribution to attack accuracy is +5.0.

## Defense

Base Armor Class is 10 before equipment and temporary effects.

Natural defensive contribution:

`Defense Bonus = Dexterity / 15 + Constitution / 20 + Speed / 30`

This keeps defense valuable without allowing raw stats alone to make a character unhittable.

## Initiative

`Initiative Bonus = Speed / 6 + Dexterity / 12`

Speed is the primary initiative attribute; Dexterity provides a smaller secondary contribution.

## Movement

Base tactical movement is 6 grid spaces.

`Movement = 6 + floor(Speed / 10)`

Speed still affects every-point initiative and dodge scaling even when movement increases at milestones.

## Damage Scaling

Strength-based physical attacks use:

`Damage Multiplier = 1 + Strength / 100`

Examples:

- 10 Strength = x1.10 physical damage
- 30 Strength = x1.30 physical damage
- 60 Strength = x1.60 physical damage

Final damage is rounded only after all modifiers are resolved.

## Critical Chance

Base critical chance is 5% unless a weapon, ability, or campaign rule states otherwise.

`Critical Chance = 5% + Dexterity x 0.10%`

At 60 Dexterity, the natural critical chance is 11% before other effects.

## Physical Resistance

`Physical Resistance = Constitution x 0.25%`

At 60 Constitution, natural physical damage resistance is 15% before armor, abilities, or special effects.

## Status Resistance

`Status Resistance = Constitution x 0.50%`

At 60 Constitution, natural status resistance is 30% before other modifiers.

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

## Damage Scaling

Strength increases Strength-based physical damage using the universal Damage Multiplier.

## Accuracy

Strength-based melee attacks gain `Strength / 12` attack accuracy.

## Weapon Requirements

Weapons may require a minimum raw Strength value.

## Carry Weight

Carry-weight formulas may use raw Strength when the inventory system is finalized.

## Environmental Interaction

Strength governs forcing doors, lifting, breaking, grappling, shoving, and similar physical actions.

---

# 9. Dexterity

## Description

Dexterity represents precision, coordination, finesse, and reflex control.

## Accuracy

Finesse and ranged attacks gain `Dexterity / 12` accuracy.

## Critical Chance

Dexterity increases critical chance using the universal Critical Chance formula.

## Dodge

Dexterity contributes to natural Defense.

## Bow Usage

Ranged weapon accuracy uses Dexterity unless a weapon explicitly states otherwise.

## Dual Wielding

Dual-wielding requirements and penalties may reference raw Dexterity.

---

# 10. Constitution

## Description

Constitution represents physical toughness and resistance.

## Defense

Constitution contributes to natural Defense.

## Physical Resistance

Constitution provides `0.25%` physical resistance per point.

## Status Resistance

Constitution provides `0.50%` status resistance per point.

## Heavy Armor

Heavy armor may require a minimum raw Constitution value.

---

# 11. Intelligence

## Description

Intelligence represents reasoning, technical knowledge, arcane understanding, and learned expertise.

## Spell Power

For Intelligence-based magic:

`Magic Power Multiplier = 1 + Intelligence / 100`

## Magical Knowledge

Arcana, magical investigation, research, and technical reasoning may use Intelligence checks.

## Enchanting

Enchanting requirements and effectiveness may reference raw Intelligence when that system is implemented.

---

# 12. Wisdom

## Description

Wisdom represents awareness, judgment, intuition, and spiritual understanding.

## Healing

For Wisdom-based healing:

`Healing Multiplier = 1 + Wisdom / 100`

## Divine Magic

Wisdom-based divine or spirit abilities may use raw Wisdom for checks and scaling.

## Perception

Perception and many awareness checks use the universal `Wisdom / 6` check bonus.

---

# 13. Charisma

## Description

Charisma represents presence, influence, leadership, and social force.

## Persuasion

Persuasion, Deception, Intimidation, and Performance checks normally use `Charisma / 6` unless context makes another attribute more appropriate.

## Trading

Baseline trading influence may improve by up to 15% through:

`Trading Influence = Charisma x 0.25%`

Exact merchant pricing remains part of the economy system.

## Leadership

Leadership and command checks use raw Charisma scaling.

## Companion Loyalty

Charisma may influence loyalty checks but cannot override established NPC personality, reputation, or player actions.

---

# 14. Speed

## Description

Speed represents movement quickness, reaction speed, and combat tempo.

## Movement

Movement follows the universal movement formula.

## Initiative

Speed is the primary initiative attribute.

## Attack Speed

Attack-speed mechanics may reference raw Speed, but extra actions must obey Combat/CoreMechanics.md and cannot become unlimited or remove meaningful turn decisions.

## Dodge

Speed contributes to natural Defense.

---

# 15. Attribute Milestones

## Unlocks

Specific abilities, equipment, dialogue options, and world interactions may require raw attribute thresholds.

Milestones must be defined by the relevant system rather than automatically granted by every attribute.

---

# 16. Attribute Requirements

Raw attribute values may be used as requirements for:

- Weapons
- Armor
- Shields
- Magic
- Companions
- Dialogue
- Abilities
- Environmental interactions

Requirements must always be visible or logically discoverable to the player when relevant.

---

# 17. Balancing

## AI Validation

The AI Game Master may choose the relevant attribute, target difficulty, or contextual modifiers, but may not invent the player's attribute values or mechanical roll result.

## Preventing Overpowered Builds

- Raw base attributes cap at 60.
- Attack accuracy scales more slowly than general checks.
- Defense pulls from several stats at reduced rates.
- Combat difficulty should rely on tactics, positioning, resources, and enemy behavior rather than stat inflation alone.

## Respec Rules

Respec rules remain to be finalized.

---

# 18. Future Attributes

## Possible New Stats

- Luck
- Faith
- Corruption
- Reputation

These are not part of the nine-attribute base progression unless formally added to the progression documentation.
