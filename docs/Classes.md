# Classes.md

Version: 1.1
Status: In Development

---

# Table of Contents

1. Class Philosophy
2. Default Classes
3. AI Generated Classes
4. Class Creation
5. Class Identity
6. Starting Abilities
7. Passive Abilities
8. Active Abilities
9. Ultimate Abilities
10. Ability Progression
11. Class Resources
12. Equipment Proficiencies
13. Class Balance
14. Future Classes

---

# 1. Class Philosophy

## Design Goals

- Every class should have a unique identity.
- Every class should be fun from the beginning of the game.
- No class should feel mandatory.
- Every class should have strengths and weaknesses.
- Players should be able to customize any class into their own unique build.
- AI should expand creativity rather than limit it.

---

# 2. Default Classes

## Warrior
Primary Resource: **Stamina**

## Rogue
Primary Resource: **Energy**

## Paladin
Primary Resource: **Divine Power**

## Ranger
Primary Resource: **Focus**

## Mage
Primary Resource: **Mana**

## Cleric
Primary Resource: **Divine Power**

## Druid
Primary Resource: **Mana**

## Monk
Primary Resource: **Ki**

## Bard
Primary Resource: **Focus**

## Barbarian
Primary Resource: **Rage**

## Sorcerer
Primary Resource: **Mana**

## Warlock
Primary Resource: **Shadow Energy**

---

# 3. AI Generated Classes

## Philosophy

Players may create completely original classes using natural language.

Examples:

- Shadow Knight
- Blood Mage
- Dragon Tamer
- Storm Monk
- Beast Tamer
- Crystal Assassin
- Time Weaver

The AI generates a balanced class while following all game rules.

---

## AI Generation

The AI creates:

- Class Name
- Class Description
- Lore
- Starting Equipment
- Passive Ability
- Active Abilities
- Ultimate Ability
- Recommended Stats
- Recommended Weapons
- Recommended Armor
- Primary Class Resource

The primary resource should fit the class identity. Existing resource names may be reused, or the AI may create a custom resource name when appropriate, as long as it follows the same resource-capacity rules.

---

## Player Customization

After the AI creates a class, the player may freely modify:

- Attribute Point Allocation
- Equipment
- Appearance
- Name
- Background Story

The AI updates the class while maintaining game balance.

---

# 4. Class Creation

## Choose a Default Class

or

## Generate a Custom Class

---

# 5. Class Identity

## Combat Role

## Strengths

## Weaknesses

## Playstyle

## Primary Resource

Every class has one primary ability resource. The resource's name depends on the class, but its maximum pool is determined by the universal **Mana attribute** described in `Stats.md`.

The Mana attribute therefore represents a character's general supernatural/combat resource capacity, even when the class displays that pool under another name such as Stamina, Rage, Focus, Energy, Divine Power, Ki, or Shadow Energy.

---

# 6. Starting Abilities

## Basic Attack

## Starting Passive

## Starting Active Ability

---

# 7. Passive Abilities

## Description

## Progression

---

# 8. Active Abilities

## Ability Slots

## Resource Costs

## Upgrades

Active abilities are primarily limited by their resource costs and the combat action economy. There is **no universal cooldown system** for normal active abilities.

If a character has enough of their class resource and a primary action available, they may use the same normal active ability again on a later turn.

---

# 9. Ultimate Abilities

## Unlock Requirements

## Resource Costs

## Restrictions

Ultimate abilities may use unusually high resource costs or explicit special restrictions such as once per encounter, once per rest, or another ability-specific rule. These are not universal cooldowns.

---

# 10. Ability Progression

## Ability Experience

## Ability Upgrades

## Ability Evolution

---

# 11. Class Resources

Class resources power active abilities and other class-specific mechanics.

Default resource mapping:

| Class | Primary Resource |
| --- | --- |
| Warrior | Stamina |
| Rogue | Energy |
| Paladin | Divine Power |
| Ranger | Focus |
| Mage | Mana |
| Cleric | Divine Power |
| Druid | Mana |
| Monk | Ki |
| Bard | Focus |
| Barbarian | Rage |
| Sorcerer | Mana |
| Warlock | Shadow Energy |

## Resource Capacity

All primary class resources use the character's **Mana attribute** to determine their maximum pool:

`Maximum Class Resource = floor(Mana / 2) x 10`

Examples:

- Mana 0-1 = 0 resource
- Mana 2-3 = 10 resource
- Mana 4-5 = 20 resource
- Mana 10-11 = 50 resource
- Mana 20-21 = 100 resource
- Mana 30 = 150 resource

The pool is displayed using the class resource's name. A Warrior with Mana 10 therefore has **50 Stamina**, while a Mage with Mana 10 has **50 Mana**.

Ability costs are paid from this pool. A character cannot use an ability if they do not have enough of the required resource.

Resource regeneration and recovery rules are defined separately and must not be invented by the AI Game Master.

---

# 12. Equipment Proficiencies

## Weapons

## Armor

## Shields

## Magic Focuses

---

# 13. Class Balance

## AI Validation

## Player Freedom

## No Overpowered Classes

## Every Build Has Trade-Offs

Resource capacity, ability costs, action economy, positioning, attribute requirements, and special restrictions should be used to balance abilities rather than universal cooldowns.

---

# 14. Future Classes

## Necromancer

## Gunslinger

## Alchemist

## Vampire

## Shapeshifter

## Psion

## Engineer

---

# Signature Abilities

## Philosophy

Every class begins with a small number of signature abilities that define its identity.

These abilities are unique to the class and cannot normally be learned by other classes.

Beyond these signature abilities, players are free to discover, learn, upgrade, or earn additional abilities throughout their adventure.

No two characters of the same class are expected to develop identically.

Player choices, quests, legendary teachers, artifacts, and AI-generated events all influence how a character evolves.
