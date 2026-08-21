# Abilities.md

Version: 1.4
Status: In Development

---

# 1. Ability Philosophy

Abilities should feel distinct, useful, and worth planning around. The player must always be able to see what an ability mechanically does before choosing, learning, or using it.

Power is balanced through Ability Point cost, Resource cost, action economy, positioning, targeting, requirements, and explicit restrictions rather than a universal cooldown system.

---

# 2. Ability Points (AP)

**Ability Points (AP)** are used only to learn abilities.

AP is separate from **Skill Points (SP)**, which improve core stats.

AP earned from leveling scales upward at higher character levels as defined in `docs/progression/Leveling.md`.

**Unused AP may be saved indefinitely. Leveling never forces the player to spend AP.**

---

# 3. Ability Tiers and Level Gates

Every learnable ability belongs to one progression tier.

| Tier | AP Cost | First Available Level |
|---|---:|---:|
| Beginner | 1 AP | 1 |
| Novice | 3 AP | 3 |
| Expert | 6 AP | 10 |
| Master | 10 AP | 25 |
| Legendary | 15 AP | 50 |

The AP cost is fixed by tier. The AI may not randomly change it.

A player cannot learn a tier before its level gate even if they have enough saved AP. Once a tier is unlocked, the player may continue learning abilities from that tier or any lower unlocked tier.

Tier represents overall mechanical strength, not only damage. Healing, movement, shielding, crowd control, number of targets, area size, range, duration, summoning, utility, and combinations of effects all contribute to tier.

---

# 4. Ability Types

Abilities may be Active, Passive, Ultimate, or Utility. The current four-slot learning system applies to the character's normal active ability loadout.

Using an active ability normally consumes the primary action unless the ability explicitly says otherwise.

Normal active abilities do **not** use universal cooldowns.

---

# 5. Four Ability Slots and Forgetting

A character may know at most **4 normal active abilities at one time**.

If the character has fewer than four abilities, learning a new ability fills an empty slot.

If all four slots are full, learning a new ability requires the player to choose one current ability to **permanently forget**, similar to learning a new move in Pokémon.

The forgotten ability is removed from the active known-ability list. It is not automatically stored in a reserve collection for free swapping later.

The game must show the four current abilities and require explicit confirmation before permanently replacing one.

Ability replacement cannot be performed during combat.

A character may learn and keep an ability whose Resource Cost is higher than their current maximum Resource. It occupies one of the four slots but cannot be activated until the full cost can actually be paid.

---

# 6. Resource Costs

Abilities consume the character's established class resource.

The core **Resource** stat controls the size and regeneration of that pool. The displayed pool name may be Mana, Rage, Focus, Trailmarks, Burial Sparks, or another generated class-specific name.

`Maximum Class Resource = Resource x 5`

`Resource Regeneration per Round = floor(Resource / 3)`

The player cannot activate an ability without enough current Resource to pay its full cost. An invalid attempt caused by insufficient Resource spends no Resource and no primary action.

Stronger abilities generally have higher Resource Costs than weaker abilities filling the same role.

---

# 7. Ability Progression

Beginner abilities are intentionally modest. As the campaign progresses, higher tiers become available through the fixed level gates in Section 3.

Higher-tier abilities may deal more damage, heal more, move farther, shield more damage, affect more targets, cover larger areas, have longer range or duration, apply stronger conditions, or combine multiple useful effects.

AP Cost and Resource Cost are separate progression gates. Unlocking a 15 AP Legendary ability does not guarantee the player has enough Resource to activate it.

---

# 8. Exact Mechanical Display Rules

Every ability must show exact mechanics rather than only flavor text.

Examples:

`Roadside Feint — Damage 1d6 | Move 1 square | Range 1 | Cost 10 Trailmarks | Beginner | 1 AP`

`Blink Step — Move 6 squares | Cost 25 Focus | Expert | 6 AP`

`Mending Light — Heal 2d8+4 | Range 5 | Cost 30 Divine Power | Expert | 6 AP`

If an ability damages, heals, shields, moves, buffs, debuffs, creates an area, affects multiple targets, or lasts for a duration, those values must be explicit.

---

# 9. Ability Requirements

Abilities may also require class/generated-class compatibility, minimum attributes, specific equipment, story unlocks, or other explicit conditions.

Attribute requirements use the current 0-100 stat system.

Resource capacity is **not** a learning requirement unless an individual ability explicitly says so.

---

# 10. AI-Generated Abilities

When the player opens the ability-learning screen, the AI may generate class-specific ability choices using the character's class, backstory, stats, current level, Resource name, and current four abilities.

The AI may generate only tiers currently unlocked by character level and must not repeat abilities the character already knows.

AI-generated abilities follow the same tier, AP, Resource, and display rules as handcrafted abilities.

The AI must determine and store the name, description, tier, Resource Cost, type/category, targeting, range, exact mechanical effects, scaling attributes, requirements, and any explicit special restrictions. AP Cost is derived from tier by Python.

The AI may not use vague wording in place of mechanical values.

---

# 11. Scaling

Abilities do not independently level up.

An ability may scale from character attributes, equipment, status effects, environment, or other explicitly defined systems, but progression also introduces genuinely stronger ability tiers rather than automatically turning every Beginner ability into a Legendary one.

---

# 12. Usage Restrictions

There is no universal cooldown system.

Rare abilities may define explicit special restrictions such as once per encounter, once per rest, once per day, limited charges, or a required setup condition. Any such restriction must be visible to the player.

---

# 13. Standard Ability Data

Every ability should store enough structured data for deterministic resolution:

- `name`
- `description`
- `tier`
- `ability_point_cost`
- `resource_cost`
- `type`
- `category`
- `target`
- `range`
- exact effect fields such as `damage`, `healing`, `movement_squares`, `shield`, duration, area, target count, statuses, or other relevant numeric effects
- attack/scaling attribute when applicable
- requirements
- special restrictions when applicable

Python owns the actual mechanical resolution. AI narration must obey the stored values.
