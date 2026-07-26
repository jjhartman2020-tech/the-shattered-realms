# StatusEffects.md

**Location:** `/docs/systems/StatusEffects.md`

Version: 1.0
Status: In Development

---

# Table of Contents

1. Status Effect Philosophy
2. Types of Status Effects
3. Buffs
4. Debuffs
5. Crowd Control
6. Damage Over Time
7. Healing Effects
8. Resistances
9. Immunities
10. Stacking Rules
11. Cleansing
12. Status Effect Interface
13. Balance Philosophy
14. Future Systems
15. Official Status Effect Index

---

# 1. Status Effect Philosophy

Status Effects are temporary conditions that influence combat.

They should:

- Encourage strategic gameplay.
- Reward preparation.
- Create interesting decisions.
- Promote teamwork.
- Make enemies feel unique.
- Give abilities additional depth.

Status Effects should rarely feel unfair.

Players should almost always have a way to respond.

---

# 2. Types of Status Effects

Status Effects fall into several categories:

- Buffs
- Debuffs
- Crowd Control
- Damage Over Time
- Healing Effects
- Utility Effects

Each effect belongs to one or more categories.

---

# 3. Buffs

Buffs temporarily strengthen a character.

Examples include:

- Increased Damage
- Increased Armor
- Increased Speed
- Increased Dodge Chance
- Increased Critical Chance
- Increased Mana Regeneration
- Increased Health Regeneration
- Damage Reflection
- Lifesteal
- Stealth
- Invisibility
- Magic Resistance

Buff durations vary depending on the source.

---

# 4. Debuffs

Debuffs temporarily weaken a target.

Examples include:

- Reduced Damage
- Reduced Armor
- Reduced Speed
- Reduced Accuracy
- Reduced Healing
- Reduced Mana Regeneration
- Reduced Vision
- Exhaustion
- Vulnerable
- Marked
- Silence

---

# 5. Crowd Control

Crowd Control (CC) temporarily limits a character's actions.

## Stun

- Cannot move.
- Cannot attack.
- Cannot cast abilities.

---

## Root

- Cannot move.
- May still attack.
- May still cast abilities.

---

## Fear

- Runs away from the source of fear.
- Player movement becomes temporarily uncontrolled.

---

## Sleep

- Cannot act.
- Ends immediately upon taking damage.

---

## Freeze

- Cannot move.
- Cannot attack.
- Cannot cast abilities.
- May still receive damage.

---

## Knockdown

- Falls to the ground.
- Requires time to recover.

---

## Taunt

- Forces the target to prioritize attacking the caster whenever possible.

---

## Charm

- Temporarily fights for the opposing side or refuses to attack them, depending on the ability.

---

# 6. Damage Over Time

Damage Over Time (DoT) effects deal damage continuously.

## Bleed

Physical damage over time.

---

## Poison

Nature damage over time.

Usually lasts longer than Bleed.

---

## Burn

Fire damage over time.

May spread through environmental hazards.

---

## Corruption

Dark magic damage over time.

May reduce healing received.

---

## Frostbite

Deals damage while also slowing movement.

---

# 7. Healing Effects

Healing effects restore health over time.

Examples include:

- Regeneration
- Healing Aura
- Life Bloom
- Holy Blessing

Healing may occur instantly or gradually.

---

# 8. Resistances

Characters may gain resistance to Status Effects.

Examples include:

- Fire Resistance
- Poison Resistance
- Bleed Resistance
- Fear Resistance
- Freeze Resistance
- Stun Resistance

Resistance reduces the effectiveness or duration of an effect but does not necessarily prevent it entirely.

---

# 9. Immunities

Some creatures, equipment, or abilities grant complete immunity.

Examples:

- Fire Elementals are immune to Burn.
- Skeletons cannot Bleed.
- Golems cannot be Poisoned.
- Ghosts cannot be Rooted by physical effects.

Immunities should always make logical sense based on the creature or effect.

---

# 10. Stacking Rules

Status Effects follow consistent stacking rules.

General Rules:

- Different effects always stack.
- The same Buff usually refreshes its duration.
- The same Debuff usually refreshes its duration.
- Damage Over Time effects may stack if they originate from different sources.
- Stronger versions replace weaker versions.

Individual abilities may override these rules.

---

# 11. Cleansing

Some abilities remove Status Effects.

Examples include:

- Remove Poison
- Cleanse
- Purify
- Dispel Magic

Certain powerful effects cannot be cleansed.

Some boss mechanics may require unique cleansing methods.

---

# 12. Status Effect Interface

Every active Status Effect should clearly display its information.

Example:

**Poison**

Duration:
3 Turns

Source:
Venom Arrow

Effect:
Lose 12 Health each turn.

Can Be Cleansed:
Yes

---

Another example:

**Stunned**

Duration:
1 Turn

Source:
Shield Bash

Effect:
Cannot perform any actions.

Can Be Cleansed:
No

Players should never have to guess:

- What an effect does.
- How long it lasts.
- Where it came from.
- Whether it can be removed.

Clear information creates better strategic decisions.

---

# 13. Balance Philosophy

Design Goals

- Status Effects should create decisions rather than frustration.
- Every effect should have meaningful counterplay.
- Powerful effects should have reasonable durations.
- Bosses should not be permanently disabled.
- Players should understand exactly why an effect occurred.

Status Effects should reward strategy instead of luck.

---

# 14. Future Systems

Possible future additions:

- Disease
- Madness
- Curse System
- Blessings
- Environmental Status Effects
- Weather-Based Effects
- Corruption Meter
- Infection System

---

# 15. Official Status Effect Index

This document serves as the official reference for every Status Effect in **The Shattered Realms**.

As development continues, every permanent Status Effect introduced into the game should be added to this document.

Each entry should include:

- Name
- Category
- Description
- Gameplay Effect
- Duration
- Stack Rules
- Sources
- Counters
- Resistances
- Immunities
- Whether it can be Cleansed

This index ensures every ability, item, enemy, boss, environment, and AI behavior uses consistent mechanics across the game.

Status Effects should never be defined in multiple locations. This document is the single source of truth for all Status Effect mechanics.
