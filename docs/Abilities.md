# Abilities.md

Version: 1.1
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

# 1. Ability Philosophy

## Design Goals

- Every ability should feel unique.
- Every ability should have a purpose.
- Players should be free to create their own playstyle.
- Every class should support multiple viable builds.
- Abilities should reward long-term planning.
- Powerful abilities should feel like major accomplishments to unlock.

---

# 2. Ability Types

## Active Abilities

Abilities activated by the player during combat.

---

## Passive Abilities

Always active abilities that provide permanent bonuses or effects.

---

## Ultimate Abilities

Extremely powerful abilities with significant resource costs and/or explicit special restrictions.

---

## Utility Abilities

Abilities focused on exploration, movement, stealth, survival, crafting, dialogue, and other non-combat gameplay.

---

# 3. Ability Points

## Earning Ability Points

Players gain:

- +1 Ability Point every level.

Unused Ability Points may be saved and spent later.

---

## Spending Ability Points

Ability Points are used to permanently unlock new abilities.

Every ability has its own Ability Point cost based on its power.

---

# 4. Ability Requirements

Abilities may require:

- Class
- Attribute Requirements
- Ability Point Cost

All attribute requirements use the game's current 0-30 attribute scale.

---

# 5. Ability Library

Every class has a complete Ability Library.

All abilities are visible from Level 1.

Locked abilities display:

- Description
- Effects
- Damage
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
- Unlimited Passive Abilities (unless otherwise specified)
- 1 Ultimate Ability Slot

Players may freely change equipped abilities outside of combat.

---

# 7. Active Abilities

Examples include:

- Melee Attacks
- Magic
- Healing
- Buffs
- Debuffs
- Mobility
- Crowd Control
- Summoning
- Defensive Skills

Using an active ability normally consumes the character's primary action unless the ability explicitly says otherwise.

Normal active abilities do **not** use a universal cooldown system. If the character has enough of the required class resource and an available action, the ability may be used again on a later turn.

---

# 8. Passive Abilities

Examples include:

- Increased Damage
- Faster Movement
- Increased Critical Chance
- Reduced Resource Cost
- Better Stealth
- Improved Defense
- Better Crafting
- Improved Persuasion

Passive abilities remain active at all times unless disabled by another effect.

---

# 9. Ultimate Abilities

Ultimate abilities are among the strongest abilities available.

Characteristics may include:

- High Ability Point Cost
- High Attribute Requirements
- Powerful Effects
- Significant Resource Costs
- Explicit Special Restrictions

Every class has multiple Ultimate abilities to choose from.

---

# 10. Resource Costs

Abilities consume the user's class resource.

Default examples include:

- Mana
- Stamina
- Rage
- Focus
- Energy
- Ki
- Divine Power
- Shadow Energy

Each class has one primary resource defined in `Classes.md`.

Unless an ability explicitly states otherwise, its Resource Cost is paid from the user's primary class-resource pool.

The **Mana attribute** in `Stats.md` determines the maximum size of that pool regardless of the pool's displayed name:

`Maximum Class Resource = floor(Mana / 2) x 10`

For example, a Warrior with Mana 10 has 50 Stamina, while a Mage with Mana 10 has 50 Mana.

Players cannot use an ability without sufficient resources. An invalid ability attempt does not spend the resource or primary action.

---

# 11. Ability Categories

Abilities may belong to one or more categories.

Examples include:

- Offensive
- Defensive
- Healing
- Mobility
- Summoning
- Stealth
- Support
- Crowd Control
- Utility

Categories help players organize and search their abilities.

---

# 12. AI Generated Abilities

Custom classes automatically generate balanced abilities.

Every generated ability follows the same balancing rules as developer-created abilities.

The AI determines:

- Ability Name
- Description
- Effects
- Resource Cost
- Ability Point Cost
- Attribute Requirements
- Special Restrictions when genuinely needed

The AI may not invent a different class-resource pool during play. It must use the character's established class resource unless the ability itself explicitly introduces a special resource mechanic.

---

# 13. Balance Philosophy

Design Goals

- No mandatory abilities.
- Every class should support multiple playstyles.
- Powerful abilities require meaningful investment.
- Every build should have strengths and weaknesses.
- Player creativity should always be rewarded.
- Resource cost, action economy, positioning, targeting, and requirements are preferred balancing tools over cooldowns.

---

# 14. Future Systems

Possible additions:

- Ability Loadout Presets
- Multiplayer Ability Sharing
- Seasonal Abilities
- Event Exclusive Abilities
- Cosmetic Ability Effects

---

# 15. Ability Scaling

Abilities should remain useful throughout an entire campaign without requiring players to repeatedly replace their favorite abilities.

Abilities do **not** gain levels independently.

Instead, an ability's effectiveness may scale automatically based on the character using it.

Possible scaling factors include:

- Character Level
- Attributes
- Equipment
- Passive Abilities
- Active Status Effects
- Environmental Conditions

Each ability determines which attributes contribute to its effectiveness.

Example scaling statistics include:

- Damage
- Healing
- Shield Strength
- Duration
- Range
- Number of Targets
- Area of Effect
- Resource Cost when appropriate

Scaling should preserve an ability's identity while ensuring it remains relevant throughout progression.

---

# 16. Usage Restrictions

There is **no universal cooldown system** for normal abilities.

Exceptionally powerful or unusual abilities may define explicit restrictions such as:

- Once Per Encounter
- Once Per Rest
- Once Per Day
- Limited Charges
- Requires a specific condition or setup

These restrictions belong to the individual ability and must be visible to the player. They are separate from normal resource costs.

---

# 17. Targeting Rules

Every ability defines how it selects valid targets.

Common targeting methods include:

- Self
- Ally
- Enemy
- Object
- Ground Location
- Single Target
- Multiple Targets
- Radius
- Cone
- Line
- Chain
- Random Target
- Nearest Target
- Lowest Health Target

Each ability should clearly define:

- Valid Targets
- Maximum Range
- Area of Effect
- Target Limit

Targeting should remain consistent so both players and the AI Game Master can reliably understand how every ability functions.

---

# 18. Ability Interactions

Abilities may interact with other abilities, status effects, environmental hazards, equipment, or world objects.

Examples include:

- Fire igniting Oil
- Ice freezing Water
- Lightning spreading through Wet targets
- Wind increasing Fire spread
- Earth creating defensive barriers

Interactions should reward creative thinking without requiring players to memorize overly complex combinations.

The AI Game Master may create additional logical interactions provided they remain consistent with established world rules.

---

# 19. Ability Templates

Every ability should follow a standardized structure.

## General Information

- Name
- Description
- Category
- Type

---

## Requirements

- Ability Point Cost
- Attribute Requirements
- Class Restrictions (if any)
- Origin Restrictions (if any)

---

## Usage

- Resource Cost
- Valid Targets
- Range
- Area of Effect
- Special Restrictions (if any)

---

## Effects

- Primary Effect
- Secondary Effects
- Status Effects Applied
- Scaling Attributes
- Special Interactions

---

Using a standardized template ensures consistency for both handcrafted and AI-generated abilities while making future balancing significantly easier.
