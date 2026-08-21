# Stats.md

Version: 2.3
Status: In Development

---

# 1. Core Attributes

The Shattered Realms uses thirteen core stats:

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
13. Magic

Players improve these stats with **Skill Points (SP)**.

**SP replaces the old term Attribute Points.** Ability Points (AP) are a different currency used only for unlocking abilities.

Character creation begins with **42 SP**. Every core stat has a natural base cap of **100**.

---

# 2. Standard Modifier

Strength, Dexterity, Agility, Constitution, Intelligence, Wisdom, Charisma, Speed, Defense, Luck, and Magic use this modifier when a d20 check or another rule calls for the stat modifier.

For scores 0-30:

`Modifier = floor(Stat / 3)`

After 30:

`Modifier = 10 + floor((Stat - 30) / 10)`

Examples: 3 = +1, 9 = +3, 30 = +10, 40 = +11, 60 = +13, 100 = +17.

---

# 3. Health

Every 1 Health grants **5 Maximum HP**.

`Maximum HP = Health x 5`

Leveling does not automatically grant HP. Players who want more HP invest SP into Health or gain explicit bonuses from other systems.

---

# 4. Resource

Resource controls the size and regeneration of the character's class-resource pool. The displayed resource name is generated or class-specific, such as Mana, Rage, Focus, Trailmarks, Burial Sparks, etc.

Every 1 Resource grants **5 Maximum Resource**.

`Maximum Resource = Resource x 5`

Examples:

- Resource 0 = 0
- Resource 1 = 5
- Resource 5 = 25
- Resource 10 = 50
- Resource 30 = 150
- Resource 60 = 300
- Resource 100 = 500

Combat regeneration:

`Resource Regeneration per Round = floor(Resource / 3)`

At the end of a completed battle, the character's Resource pool resets to full.

Abilities may be unlocked and equipped even when their Resource Cost exceeds the character's current maximum, but they cannot be activated until the full cost can be paid.

---

# 5. Strength

Strength represents raw physical power.

Uses the Standard Modifier. It governs Strength-based melee accuracy, forcing, lifting, breaking, grappling, shoving, physical requirements, and Strength-based abilities.

---

# 6. Dexterity

Dexterity represents precision, fine motor control, finesse, and hand coordination.

Uses the Standard Modifier. It governs ranged/finesse accuracy, Sleight of Hand, Lockpicking, Pickpocketing, Precision, and Dexterity-based abilities.

Dexterity does not control critical chance.

---

# 7. Agility

Agility represents body control, evasiveness, balance, stealth, and coordinated movement.

Uses the Standard Modifier. It governs Acrobatics, Stealth, Evasion, balance, and similar body-control checks.

---

# 8. Constitution

Constitution represents toughness and resistance.

Uses the Standard Modifier for Constitution checks.

`Physical Resistance = floor(Constitution / 5)%`

`Status Resistance = floor(Constitution / 4)%`

---

# 9. Intelligence

Intelligence represents reasoning, technical knowledge, learned expertise, investigation, engineering, and magical theory.

Uses the Standard Modifier.

Common Intelligence skills include Investigation, Arcana, History, Nature, and **Engineering**.

Intelligence represents understanding magic; Magic represents raw magical power.

---

# 10. Wisdom

Wisdom represents awareness, judgment, intuition, perception, and spiritual understanding.

Uses the Standard Modifier.

Common Wisdom skills include Perception, Insight, Survival, Medicine, and Animal Handling.

---

# 11. Charisma

Charisma represents presence, influence, leadership, social force, and performance.

Uses the Standard Modifier.

Common Charisma skills include Persuasion, Deception, Intimidation, Performance, and Leadership.

---

# 12. Speed

Speed represents movement quickness, reaction speed, and combat tempo.

Initiative uses the Standard Speed Modifier:

`Initiative Bonus = Standard Speed Modifier`

Base tactical movement is 6 squares.

Through Speed 30:

`+0.5 square per Speed`

After Speed 30:

`+0.1 square per additional Speed`

Final usable movement is floored to whole squares.

---

# 13. Defense

Defense represents guarding, blocking, bracing, stance control, and focused defensive technique.

Uses the Standard Modifier.

When the combatant spends their primary action to Defend:

`Defend AC Bonus = Standard Defense Modifier`

The bonus normally lasts until the start of that combatant's next turn.

---

# 14. Luck

Luck represents chance and critical-hit potential.

Luck checks use the Standard Modifier.

Base critical chance is 5%.

`Critical Chance = 5% + Standard Luck Modifier%`

A natural 20 remains an automatic critical hit.

Luck does not automatically increase loot rarity.

---

# 15. Magic

Magic represents raw magical power and magical control.

Uses the Standard Modifier.

Magic may govern magical attack accuracy, magical damage/healing scaling, controlling unstable magic, overpowering magical forces, and magical equipment/ability requirements.

Magic, Intelligence, and Resource remain distinct:

- Intelligence = understanding.
- Magic = raw supernatural power/control.
- Resource = capacity and regeneration used to pay ability costs.

---

# 16. Skill Mapping

Skills use the governing stat's modifier. There is no proficiency/expertise/training-point system.

Default mappings:

- Strength: Athletics, Grappling, Might
- Dexterity: Sleight of Hand, Lockpicking, Pickpocketing, Precision
- Agility: Acrobatics, Stealth, Evasion
- Constitution: Endurance, Fortitude
- Intelligence: Investigation, Arcana, History, Nature, Engineering
- Wisdom: Perception, Insight, Survival, Medicine, Animal Handling
- Charisma: Persuasion, Deception, Intimidation, Performance, Leadership
- Magic: Spellcasting, Channeling

Health, Resource, Speed, Defense, and Luck may be rolled directly when context calls for them.

The Game Master may use a contextual governing stat when the player's method clearly justifies it, such as Intimidation (Strength).

---

# 17. Progression Currency Terminology

To prevent confusion:

- **SP = Skill Points = spent on the 13 core stats.**
- **AP = Ability Points = spent on unlocking abilities.**
- **XP Orbs = used to gain character levels.**
- **Resource = combat pool spent to activate abilities/equipment.**

The complete leveling and AP reward rules are defined in `docs/progression/Leveling.md`.
