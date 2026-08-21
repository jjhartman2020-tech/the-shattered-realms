# Stats.md

Version: 2.0
Status: In Development

---

# 1. Stat Philosophy

The Shattered Realms uses twelve core attributes. Players spend Attribute Points (AP) directly on these attributes.

Design goals:

- Starting builds should require meaningful specialization.
- Early attribute investment should have strong, readable effects.
- Long campaigns need room for continued progression.
- d20 modifiers must not become unbounded at high attributes.
- Derived values such as movement, resource capacity, resistance, and critical chance use their own documented formulas.
- Skills are derived from attributes and will be documented separately.

---

# 2. Core Attributes

The twelve core attributes are:

1. Health
2. Resource
3. Strength
4. Dexterity
5. Agility
6. Constitution
7. Intelligence
8. Wisdom
9. Charisma
10. Speed
11. Defense
12. Luck

## Character Creation

Every new character begins with **30 Attribute Points** to distribute among the twelve core attributes.

The player chooses their own name, appearance, and starting attribute allocation. After the player confirms the build, the AI may use the confirmed build and appearance to generate the character's unique class, class-resource name, backstory, beginner ability choices, and starter equipment choices as defined by the character-creation system.

---

# 3. Attribute Caps

Every core attribute has a natural base maximum of **100**.

Equipment, buffs, blessings, artifacts, abilities, and special world effects may temporarily or specially exceed the natural cap when their own rules explicitly permit it.

---

# 4. Standard Attribute Modifier

Strength, Dexterity, Agility, Constitution, Intelligence, Wisdom, Charisma, Speed, Defense, and Luck use the standard modifier when a d20 check or another mechanic calls for that attribute's modifier.

## 0-30 Scaling

From 0 through 30, every full 3 attribute points grant +1.

`Modifier = floor(Attribute / 3)` for Attribute <= 30

Examples:

- 0-2 = +0
- 3-5 = +1
- 6-8 = +2
- 9-11 = +3
- 15-17 = +5
- 27-29 = +9
- 30 = +10

## 31-100 Scaling

After 30, diminishing returns apply. Every full 10 additional points grant another +1.

`Modifier = 10 + floor((Attribute - 30) / 10)` for Attribute > 30

Examples:

- 30-39 = +10
- 40-49 = +11
- 50-59 = +12
- 60-69 = +13
- 70-79 = +14
- 80-89 = +15
- 90-99 = +16
- 100 = +17

Health and Resource have their own primary scaling formulas below rather than using this modifier for their pool sizes.

---

# 5. Health

Health determines Maximum Health.

**Every 1 Health point grants 5 Maximum Health.**

`Maximum Health from Health = Health x 5`

Examples:

- Health 1 = 5 HP
- Health 3 = 15 HP
- Health 6 = 30 HP
- Health 10 = 50 HP
- Health 30 = 150 HP
- Health 100 = 500 HP

Any additional level-based or special-source Maximum Health bonuses must be documented separately and are not part of this formula.

---

# 6. Resource

Resource is the universal attribute that determines the size and regeneration of a character's class-resource pool.

The attribute itself is called **Resource**. The actual pool is displayed using the character's class-specific or AI-generated resource name, such as Mana, Stamina, Rage, Ki, Focus, Energy, Divine Power, Shadow Energy, or another generated name.

## Maximum Resource

Every full 2 Resource points grant 10 maximum class resource.

`Maximum Class Resource = floor(Resource / 2) x 10`

Examples:

- Resource 0-1 = 0
- Resource 2-3 = 10
- Resource 4-5 = 20
- Resource 10-11 = 50
- Resource 30 = 150
- Resource 60 = 300
- Resource 100 = 500

## Combat Resource Regeneration

During combat, every full 3 Resource points regenerate 1 class resource per round.

`Resource Regeneration per Round = floor(Resource / 3)`

Examples:

- Resource 0-2 = 0 per round
- Resource 3-5 = 1 per round
- Resource 9-11 = 3 per round
- Resource 30 = 10 per round
- Resource 60 = 20 per round
- Resource 100 = 33 per round

Resource regeneration cannot raise the pool above its maximum.

## Post-Battle Recovery

After a battle is fully completed, the character's class-resource pool resets to its maximum value.

---

# 7. Strength

Strength represents raw physical power.

Strength uses the standard attribute modifier:

- +1 per full 3 Strength through 30.
- After 30, +1 per full 10 additional Strength.

Strength governs Strength-based melee accuracy, forcing, lifting, breaking, grappling, shoving, physical requirements, and Strength-based abilities.

Strength-based physical damage may use separate slower damage scaling defined by the combat/equipment rules so the d20 modifier is not automatically copied directly into damage.

---

# 8. Dexterity

Dexterity represents precision, fine motor control, finesse, and hand coordination.

Dexterity uses the standard attribute modifier:

- +1 per full 3 Dexterity through 30.
- After 30, +1 per full 10 additional Dexterity.

Dexterity is intended for mechanics such as:

- Ranged weapon accuracy
- Finesse weapon accuracy
- Sleight of hand
- Lockpicking
- Pickpocketing
- Fine precision tasks
- Dexterity-based ability scaling and requirements

**Dexterity does not determine critical chance. Critical chance is governed by Luck.**

---

# 9. Agility

Agility represents body control, evasiveness, balance, and coordinated physical movement.

Agility uses the standard attribute modifier:

- +1 per full 3 Agility through 30.
- After 30, +1 per full 10 additional Agility.

Agility is intended for mechanics such as:

- Stealth
- Acrobatics
- Dodging and evasive checks
- Balance
- Escaping restraints or grapples when body control is relevant
- Agility-based abilities and requirements

Agility and Dexterity are separate: Dexterity represents precision and hand control, while Agility represents whole-body control and evasiveness.

---

# 10. Constitution

Constitution represents physical toughness, durability, and resistance.

Constitution checks use the standard attribute modifier:

- +1 per full 3 Constitution through 30.
- After 30, +1 per full 10 additional Constitution.

## Physical Resistance

`Physical Resistance = floor(Constitution / 5)%`

Examples:

- Constitution 10 = 2%
- Constitution 30 = 6%
- Constitution 60 = 12%
- Constitution 100 = 20%

## Status Resistance

`Status Resistance = floor(Constitution / 4)%`

Examples:

- Constitution 10 = 2%
- Constitution 30 = 7%
- Constitution 60 = 15%
- Constitution 100 = 25%

Equipment, abilities, conditions, and special effects may modify these values separately.

---

# 11. Intelligence

Intelligence represents reasoning, technical knowledge, learned expertise, investigation, and arcane understanding.

Intelligence uses the standard attribute modifier:

- +1 per full 3 Intelligence through 30.
- After 30, +1 per full 10 additional Intelligence.

Intelligence-based skills, abilities, requirements, and checks use this modifier when appropriate.

---

# 12. Wisdom

Wisdom represents awareness, judgment, intuition, perception, and spiritual understanding.

Wisdom uses the standard attribute modifier:

- +1 per full 3 Wisdom through 30.
- After 30, +1 per full 10 additional Wisdom.

Wisdom-based skills, abilities, healing systems, requirements, and checks use this modifier when appropriate.

---

# 13. Charisma

Charisma represents presence, influence, leadership, social force, and performance.

Charisma uses the standard attribute modifier:

- +1 per full 3 Charisma through 30.
- After 30, +1 per full 10 additional Charisma.

Charisma-based social checks, abilities, and requirements use this modifier when appropriate.

The exact skill mapping for Persuasion, Deception, Intimidation, Performance, and other social skills will be defined in the skill system.

---

# 14. Speed

Speed represents raw movement quickness, reaction speed, and combat tempo.

Speed checks and initiative use the standard attribute modifier:

- +1 per full 3 Speed through 30.
- After 30, +1 per full 10 additional Speed.

## Initiative

`Initiative Bonus = Standard Speed Modifier`

Speed is the primary initiative attribute. Dexterity does not automatically add a second initiative bonus.

## Movement

Base tactical movement is **6 grid squares** before Speed.

From Speed 0 through 30:

**Every 1 Speed adds 0.5 movement squares.**

After Speed 30:

**Every 1 additional Speed adds 0.1 movement squares.**

`Movement = 6 + (min(Speed, 30) x 0.5) + (max(0, Speed - 30) x 0.1)`

The combat engine floors the final result to whole usable grid squares.

Examples:

- Speed 0 = 6 squares
- Speed 2 = 7 squares
- Speed 10 = 11 squares
- Speed 20 = 16 squares
- Speed 30 = 21 squares
- Speed 40 = 22 squares
- Speed 60 = 24 squares
- Speed 100 = 28 squares

---

# 15. Defense

Defense represents deliberate guarding, blocking, bracing, stance control, and focused defensive technique.

Defense uses the standard attribute modifier:

- +1 per full 3 Defense through 30.
- After 30, +1 per full 10 additional Defense.

## Active Defend Action

When a combatant spends their primary action to Defend:

`Defend AC Bonus = Standard Defense Modifier`

The bonus lasts until the start of that combatant's next turn unless another documented rule changes the duration.

Defense is primarily an active defensive stat rather than a permanent one-for-one passive AC bonus.

---

# 16. Luck

Luck represents chance, fortunate outcomes, and critical-hit potential.

Luck checks use the standard attribute modifier:

- +1 per full 3 Luck through 30.
- After 30, +1 per full 10 additional Luck.

## Critical Chance

Base critical chance is **5%**.

From Luck 0 through 30, every full 3 Luck adds +1% critical chance.

After Luck 30, every full 10 additional Luck adds another +1% critical chance.

`Critical Chance = 5% + Standard Luck Modifier%`

Examples:

- Luck 0 = 5%
- Luck 3 = 6%
- Luck 9 = 8%
- Luck 15 = 10%
- Luck 30 = 15%
- Luck 40 = 16%
- Luck 60 = 18%
- Luck 80 = 20%
- Luck 100 = 22%

A natural 20 on an attack roll remains an automatic critical hit regardless of Luck.

Luck does **not** automatically increase loot rarity. Explicit Luck checks or abilities may use Luck when appropriate.

---

# 17. Attribute Requirements

Raw attribute values may be used as requirements for weapons, armor, shields, abilities, equipment, dialogue options, environmental interactions, and other systems.

Requirements should be visible or logically discoverable to the player when relevant.

---

# 18. Derived Systems Still To Finalize

The following systems will be finalized in their own documentation and then cross-checked against this file:

- Skill list and attribute-to-skill mapping
- Passive Armor Class formula
- Strength physical-damage scaling beyond the d20 modifier
- Equipment requirements and scaling
- Ability scaling and resource costs
- Level progression and maximum level
- Any automatic level-based Maximum Health bonuses
- Respec rules

These systems must not silently contradict the formulas defined in this file.
