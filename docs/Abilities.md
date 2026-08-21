# Abilities.md

Version: 1.2
Status: In Development

---

# Table of Contents

1. Ability Philosophy
2. Ability Types
3. Ability Points
4. Ability Requirements
5. Ability Library
6. Ability Slots
7. Active Abilities
8. Passive Abilities
9. Ultimate Abilities
10. Resource Costs
11. Ability Categories
12. AI Generated Abilities
13. Balance Philosophy
14. Future Systems
15. Ability Scaling
16. Usage Restrictions
17. Targeting Rules
18. Ability Interactions
19. Ability Templates
20. Exact Mechanical Display Rules
21. Power and Resource-Cost Progression

# 1. Ability Philosophy

## Design Goals

- Every ability should feel unique.
- Every ability should have a purpose.
- Players should be free to create their own playstyle.
- Every class should support multiple viable builds.
- Abilities should reward long-term planning.
- Powerful abilities should feel like major accomplishments to unlock.
- The player should always be able to see exactly what an ability mechanically does before choosing or equipping it.

---

# 2. Ability Types

## Active Abilities

Abilities activated by the player during combat.

## Passive Abilities

Always active abilities that provide permanent bonuses or effects.

## Ultimate Abilities

Extremely powerful abilities with significant resource costs and/or explicit special restrictions.

## Utility Abilities

Abilities focused on exploration, movement, stealth, survival, crafting, dialogue, and other non-combat gameplay.

---

# 3. Ability Points

Players gain +1 Ability Point every level unless the progression system is later revised.

Unused Ability Points may be saved and spent later. Ability Points permanently unlock abilities; they do not pay the combat Resource Cost of using an ability.

---

# 4. Ability Requirements

Abilities may require:

- Class
- Attribute Requirements
- Ability Point Cost

Attribute requirements use the current 0-100 attribute system in `Stats.md`.

A character may unlock and equip an ability even when their current maximum class resource is lower than that ability's Resource Cost, unless the ability has another explicit equip restriction. However, that ability cannot be activated until the character can actually pay the full Resource Cost.

---

# 5. Ability Library

Every class has a complete Ability Library.

All abilities are visible from Level 1.

Locked abilities display:

- Description
- Exact Effects
- Damage, healing, movement, shielding, duration, range, targets, or other numeric values
- Resource Cost
- Special Restrictions, if any
- Attribute Requirements
- Ability Point Cost

Players are encouraged to plan long-term builds by viewing every available ability from the beginning of the game.

---

# 6. Ability Slots

Players cannot equip every unlocked ability at once.

Default slots:

- 4 Active Ability Slots
- Unlimited Passive Abilities unless otherwise specified
- 1 Ultimate Ability Slot

Players may freely change equipped abilities outside of combat.

**Equipping an ability does not require the player to currently have enough maximum resource to use it.** An under-resourced ability may remain equipped but is unavailable for activation until its full cost can be paid.

---

# 7. Active Abilities

Examples include melee attacks, magic, healing, buffs, debuffs, mobility, crowd control, summoning, and defensive skills.

Using an active ability normally consumes the character's primary action unless the ability explicitly says otherwise.

Normal active abilities do not use a universal cooldown system. If the character has enough required class resource and an available action, the ability may be used again on a later turn.

---

# 8. Passive Abilities

Examples include increased damage, faster movement, increased critical chance, reduced Resource Cost, better stealth, improved defense, better crafting, and improved persuasion.

Passive abilities remain active at all times unless disabled by another effect.

---

# 9. Ultimate Abilities

Ultimate abilities are among the strongest abilities available.

Characteristics may include high Ability Point Cost, high attribute requirements, powerful effects, significant Resource Costs, and explicit special restrictions.

---

# 10. Resource Costs

Abilities consume the user's class resource.

The core capacity stat is **Resource** in `Stats.md`. The actual displayed pool name is class-specific or AI-generated, such as Mana, Stamina, Rage, Focus, Energy, Ki, Divine Power, Shadow Energy, Trailmarks, or another established class resource.

`Maximum Class Resource = floor(Resource / 2) x 10`

The player cannot activate an ability without enough current resource to pay its complete Resource Cost. The ability may still remain unlocked and equipped. An invalid attempt caused by insufficient resource spends no resource and no primary action.

Resource Cost is one of the game's main balancing tools. A stronger ability should generally cost more than a weaker ability that fills the same role.

---

# 11. Ability Categories

Abilities may belong to Offensive, Defensive, Healing, Mobility, Summoning, Stealth, Support, Crowd Control, Utility, or other clear categories.

---

# 12. AI Generated Abilities

Custom classes automatically generate balanced abilities.

Every generated ability follows the same rules as developer-created abilities. The AI determines the name, description, exact effects, Resource Cost, Ability Point Cost, attribute requirements, and any genuine special restrictions.

AI-generated abilities **must never rely on vague mechanical wording**. If the ability damages, heals, shields, moves, buffs, debuffs, creates an area, affects multiple targets, or lasts for a duration, those values must be explicit.

Examples:

- `Damage: 1d6`
- `Move: 3 squares`
- `Heal: 1d8`
- `Shield: 6 damage`
- `Range: 5 squares`
- `Duration: 2 rounds`
- `Targets: up to 2 enemies`

---

# 13. Balance Philosophy

- No mandatory abilities.
- Every class should support multiple playstyles.
- Powerful abilities require meaningful investment.
- Every build should have strengths and weaknesses.
- Player creativity should be rewarded.
- Resource cost, action economy, positioning, targeting, and requirements are preferred balancing tools over cooldowns.
- When two abilities fill a similar role, the one with the lower Resource Cost should normally have a weaker effect, while the more expensive one may deal more damage, move farther, heal more, affect more targets, last longer, or provide a stronger special effect.

---

# 14. Future Systems

Possible additions include Ability Loadout Presets, Multiplayer Ability Sharing, Seasonal Abilities, Event Exclusive Abilities, and Cosmetic Ability Effects.

---

# 15. Ability Scaling

Abilities do not gain independent levels. Their effectiveness may scale with character level, attributes, equipment, passive abilities, status effects, and environmental conditions.

An ability's identity should stay recognizable as the character grows. However, progression should also introduce genuinely stronger abilities rather than making every beginner ability equal to late-game powers.

---

# 16. Usage Restrictions

There is no universal cooldown system for normal abilities.

Exceptionally powerful abilities may define explicit restrictions such as Once Per Encounter, Once Per Rest, Once Per Day, Limited Charges, or a required setup condition. These restrictions must always be visible to the player.

---

# 17. Targeting Rules

Every ability defines valid targets, maximum range, area of effect when applicable, and target limit.

Common targeting methods include Self, Ally, Enemy, Object, Ground Location, Single Target, Multiple Targets, Radius, Cone, Line, Chain, Random Target, Nearest Target, and Lowest Health Target.

---

# 18. Ability Interactions

Abilities may interact with other abilities, status effects, environmental hazards, equipment, or world objects. Logical interactions may include fire igniting oil, ice freezing water, lightning spreading through wet targets, wind affecting fire, and earth creating barriers.

---

# 19. Ability Templates

Every ability should use a standardized structure.

## General Information

- Name
- Description
- Category
- Type

## Requirements

- Ability Point Cost
- Attribute Requirements
- Class Restrictions if any
- Origin Restrictions if any

## Usage

- Resource Cost
- Valid Targets
- Range
- Area of Effect
- Special Restrictions if any

## Effects

Every applicable effect must be explicit:

- Damage expression
- Healing expression
- Movement squares
- Shield amount
- Buff/debuff value
- Duration
- Number of targets
- Area size
- Status effects applied
- Scaling attributes
- Special interactions

---

# 20. Exact Mechanical Display Rules

Whenever the player is choosing, viewing, equipping, purchasing, looting, or inspecting an ability, the UI must show the actual mechanical effect rather than only flavor text.

Examples:

`Roadside Feint — Damage 1d6 | Move 1 square | Range 1 | Cost 10 Trailmarks`

`Blink Step — Move 4 squares | Cost 15 Focus`

`Mending Light — Heal 1d8+2 | Range 4 | Cost 20 Divine Power`

Flavor descriptions may appear alongside these values but may never replace them.

---

# 21. Power and Resource-Cost Progression

Beginner abilities should be intentionally modest. Early characters should normally receive low-damage, short-range, small-healing, short-movement, or narrow utility powers with low Resource Costs.

As the campaign progresses, stronger abilities become available. Higher-tier abilities may deal more damage, heal more, move farther, affect larger areas, hit more targets, apply stronger conditions, or combine multiple effects. Those stronger abilities should generally have correspondingly higher Resource Costs.

There is no rule that an ability's cost must be affordable when it is acquired or equipped. A character may own and slot a powerful ability whose Resource Cost exceeds their current maximum pool. In that case the ability is visibly unavailable until progression raises their Resource capacity enough to pay the cost.
