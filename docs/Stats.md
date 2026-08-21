# Stats.md

Version: 1.5
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
15. Defense
16. Attribute Milestones
17. Attribute Requirements
18. Balancing
19. Future Attributes

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
- The ten attributes are **Health, Mana, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma, Speed, and Defense**.

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

For d20 rolls and other systems that use the universal modifier, every full 3 points in the relevant attribute grants +1.

`Attribute Modifier = floor(Attribute / 3)`

There are no fractional modifiers.

Examples:

- 0-2 = +0
- 3-5 = +1
- 6-8 = +2
- 9-11 = +3
- 12-14 = +4
- 15-17 = +5
- 18-20 = +6
- 21-23 = +7
- 24-26 = +8
- 27-29 = +9
- 30 = +10

Example: **17 Strength gives +5 to Strength rolls.**

The same threshold rule applies whenever an attribute is explicitly using the universal modifier.

## Attack Accuracy

Attack rolls use the same whole-number attribute modifier:

- Strength-based melee attacks: `floor(Strength / 3)`
- Dexterity-based finesse attacks: `floor(Dexterity / 3)`
- Ranged attacks: `floor(Dexterity / 3)`

Weapons, abilities, conditions, positioning, and proficiency systems may add separate modifiers.

## Passive Defense / Base Armor Class

Base Armor Class is 10 before equipment and temporary effects.

Natural passive defensive contribution remains:

`Defense Bonus = floor(Dexterity / 9) + floor(Constitution / 15) + floor(Speed / 15)`

This represents reflexes, toughness, and movement while fighting normally. The separate **Defense attribute does not permanently add its full modifier to AC**; it powers the active Defend action instead.

## Active Defend Action

Defense is a dedicated 0-30 attribute for characters who invest in guarding, blocking, bracing, and defensive combat technique.

When a combatant spends their primary action to **Defend**:

`Defend AC Bonus = floor(Defense / 3)`

The bonus lasts until the start of that combatant's next turn.

Examples:

- Defense 0-2 = +0 AC while Defending
- Defense 3-5 = +1 AC
- Defense 6-8 = +2 AC
- Defense 9-11 = +3 AC
- Defense 12-14 = +4 AC
- Defense 15-17 = +5 AC
- Defense 18-20 = +6 AC
- Defense 21-23 = +7 AC
- Defense 24-26 = +8 AC
- Defense 27-29 = +9 AC
- Defense 30 = +10 AC

This bonus is temporary and applies only while the Defend action is active.

## Initiative

`Initiative Bonus = floor(Speed / 3) + floor(Dexterity / 6)`

Speed is the primary initiative attribute; Dexterity provides a smaller secondary contribution.

## Movement

Base tactical movement is 6 grid spaces.

`Movement = 6 + floor(Speed / 6)`

At 30 Speed, natural movement is 11 spaces before other effects.

## Resource Capacity

The **Mana attribute** is the universal resource-capacity attribute, even when a class gives its resource a different name.

`Maximum Class Resource = floor(Mana / 2) x 10`

Examples:

- Mana 0-1 = 0 resource
- Mana 2-3 = 10 resource
- Mana 4-5 = 20 resource
- Mana 6-7 = 30 resource
- Mana 10-11 = 50 resource
- Mana 20-21 = 100 resource
- Mana 30 = 150 resource

The resource is displayed using the character's class resource name. For example, Mana 10 means 50 Stamina for a Warrior, 50 Rage for a Barbarian, 50 Ki for a Monk, or 50 Mana for a Mage.

No fractional resource capacity is granted for an incomplete 2-point threshold.

## Damage Scaling

Strength-based physical attacks gain a whole-number damage bonus:

`Strength Damage Bonus = floor(Strength / 6)`

At 30 Strength, the natural Strength damage bonus is +5 before weapon, ability, and other modifiers.

### Accuracy Margin Damage

A successful attack that beats the target's Armor Class by a large amount deals extra precision/quality damage.

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

A **natural 20 on an attack roll is always a critical hit**. A critical hit rolls the attack's weapon damage dice one additional time, while flat damage bonuses are added only once. Non-natural-20 hits may still become critical hits through the normal Critical Chance formula.

## Physical Resistance

`Physical Resistance = floor(Constitution / 3)%`

At 30 Constitution, natural physical damage resistance is 10% before armor, abilities, or special effects.

## Status Resistance

`Status Resistance = floor(Constitution / 3) x 2%`

At 30 Constitution, natural status resistance is 20% before other modifiers.

These formulas are balance constants and may be tuned later, but changes must remain documented here before the engine is changed.

---

# 6. Health

Health directly increases the character's Maximum Health pool.

`Maximum Health = max(1, Health + 5 x (Level - 1))`

The +5 per level comes from the progression system and is separate from Attribute Point spending.

Health may also be referenced by survival challenges, endurance events, environmental hazards, and campaign-specific mechanics.

---

# 7. Mana

Mana is the universal **class-resource capacity attribute**.

It does not mean every class literally uses a resource called Mana. The class determines the pool's displayed name, while the Mana attribute determines the pool's maximum size.

`Maximum Class Resource = floor(Mana / 2) x 10`

Examples:

- Mana 2 = 10 resource
- Mana 4 = 20 resource
- Mana 10 = 50 resource
- Mana 20 = 100 resource
- Mana 30 = 150 resource

For a Mage this pool is called Mana. For other classes it may be Stamina, Energy, Divine Power, Focus, Ki, Rage, Shadow Energy, or another established custom-class resource.

Abilities consume the character's class resource according to their documented costs. Regeneration and recovery rules are defined separately.

---

# 8. Strength

Strength represents raw physical power.

- Strength rolls use `floor(Strength / 3)`.
- Strength-based physical damage gains `floor(Strength / 6)` bonus damage.
- Strength-based melee attacks use the Strength modifier for attack accuracy.
- Weapons may require a minimum raw Strength value.
- Strength governs forcing doors, lifting, breaking, grappling, shoving, and similar actions.

---

# 9. Dexterity

Dexterity represents precision, coordination, finesse, and reflex control.

- Dexterity rolls use `floor(Dexterity / 3)`.
- Finesse and ranged attacks use the Dexterity modifier for accuracy.
- Dexterity increases critical chance.
- Dexterity contributes to passive natural Defense.

---

# 10. Constitution

Constitution represents physical toughness and resistance.

- Constitution rolls use `floor(Constitution / 3)`.
- Constitution contributes to passive natural Defense.
- Constitution provides 1% physical resistance for every full 3 points.
- Constitution provides 2% status resistance for every full 3 points.

---

# 11. Intelligence

Intelligence represents reasoning, technical knowledge, arcane understanding, and learned expertise.

- Intelligence rolls use `floor(Intelligence / 3)`.
- Intelligence-based spell systems may use the Intelligence modifier and raw Intelligence for requirements.

---

# 12. Wisdom

Wisdom represents awareness, judgment, intuition, and spiritual understanding.

- Wisdom rolls use `floor(Wisdom / 3)`.
- Wisdom-based healing and divine systems may use the Wisdom modifier and raw Wisdom for requirements.

---

# 13. Charisma

Charisma represents presence, influence, leadership, and social force.

- Persuasion, Deception, Intimidation, Performance, leadership, and similar Charisma rolls use `floor(Charisma / 3)` unless context makes another attribute more appropriate.
- Baseline trading influence improves by 1% for every full 3 Charisma, up to 10% at 30 Charisma.

---

# 14. Speed

Speed represents movement quickness, reaction speed, and combat tempo.

- Speed rolls use `floor(Speed / 3)`.
- Movement follows the universal movement formula.
- Speed is the primary initiative attribute.
- Speed contributes to passive natural Defense.

---

# 15. Defense

Defense represents deliberate guarding skill, blocking technique, bracing, stance control, and the ability to protect yourself when focusing on defense.

## Active Defense

Defense is primarily used by the **Defend** combat action.

`Defend AC Bonus = floor(Defense / 3)`

Every full 3 points of Defense therefore adds +1 AC while actively Defending.

Defense does not automatically replace Dexterity, Constitution, or Speed in passive AC. Passive defense and active Defense investment are separate so a character must choose whether to spend a primary action to gain the larger temporary protection.

Equipment, shields, abilities, statuses, and special mechanics may add additional defensive bonuses separately.

---

# 16. Attribute Milestones

Specific abilities, equipment, dialogue options, and world interactions may require raw attribute thresholds.

Milestones must be defined by the relevant system rather than automatically granted by every attribute.

---

# 17. Attribute Requirements

Raw attribute values may be used as requirements for weapons, armor, shields, magic, companions, dialogue, abilities, and environmental interactions.

Requirements must always be visible or logically discoverable to the player when relevant.

---

# 18. Balancing

## AI Validation

The AI Game Master may choose the relevant attribute, target difficulty, or contextual modifiers, but may not invent the player's attribute values or mechanical roll result.

## Preventing Overpowered Builds

- Raw base attributes cap at 30.
- Core attribute modifiers cap naturally at +10.
- Class-resource capacity caps naturally at 150 from a base Mana attribute of 30 before special effects.
- Passive Defense pulls from several attributes at slower rates.
- The Defense attribute's large AC scaling requires spending the character's primary action to activate it.
- Combat difficulty should rely on tactics, positioning, resources, and enemy behavior rather than stat inflation alone.

## Respec Rules

Respec rules remain to be finalized.

---

# 19. Future Attributes

Possible future stats include Luck, Faith, Corruption, and Reputation.

These are not part of the ten-attribute base progression unless formally added to the progression documentation.
