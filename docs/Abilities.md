# Abilities.md

Version: 1.3
Status: In Development

---

# 1. Ability Philosophy

Abilities should feel distinct, useful, and worth planning around. The player must always be able to see what an ability mechanically does before choosing, unlocking, equipping, purchasing, or using it.

Power is balanced through Ability Point cost, Resource cost, action economy, positioning, targeting, requirements, and explicit restrictions rather than a universal cooldown system.

---

# 2. Ability Points (AP)

**Ability Points (AP)** are used only to permanently unlock abilities.

AP is separate from **Skill Points (SP)**, which improve core stats.

AP earned from leveling scales upward at higher character levels as defined in `docs/progression/Leveling.md`.

Unused AP may be saved indefinitely.

---

# 3. Ability Tiers

Every unlockable ability belongs to one progression tier.

| Tier | Ability Point Cost |
|---|---:|
| Beginner | 1 AP |
| Novice | 3 AP |
| Expert | 6 AP |
| Master | 10 AP |
| Legendary | 15 AP |

The AP cost is fixed by tier. The AI may not randomly change the cost of an ability after its tier is established.

Tier represents overall mechanical strength, not only damage. Healing, movement, shielding, crowd control, number of targets, area size, range, duration, summoning, utility, and combinations of effects all contribute to tier.

---

# 4. Ability Types

Abilities may be:

- Active
- Passive
- Ultimate
- Utility

Using an active ability normally consumes the primary action unless the ability explicitly says otherwise.

Normal active abilities do **not** use universal cooldowns.

---

# 5. Ability Slots

Default slots:

- 4 Active Ability Slots
- Unlimited Passive Abilities unless another rule limits them
- 1 Ultimate Ability Slot

Players may freely change equipped abilities outside combat.

A character may unlock and equip an ability even if they cannot currently afford its Resource Cost. The ability remains in the slot but cannot be activated until the full cost can be paid.

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

Beginner abilities are intentionally modest. As the campaign progresses, stronger tiers become available.

Higher-tier abilities may:

- Deal more damage
- Heal more
- Move farther
- Shield more damage
- Affect more targets
- Cover larger areas
- Have longer range or duration
- Apply stronger conditions
- Combine multiple useful effects

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

Abilities may also require:

- Class or generated-class compatibility
- Minimum attributes
- Specific equipment
- Story unlocks
- Other explicit conditions

Attribute requirements use the current 0-100 stat system.

Resource capacity is **not** an equip requirement unless an individual ability explicitly says so.

---

# 10. AI-Generated Abilities

AI-generated abilities follow the same tier, AP, Resource, and display rules as handcrafted abilities.

The AI must determine and store:

- Name
- Description
- Tier
- Ability Point Cost derived from tier
- Resource Cost
- Type/category
- Targeting
- Range
- Exact mechanical effects
- Scaling attribute(s)
- Attribute or story requirements if applicable
- Explicit special restrictions if genuinely needed

The AI may not use vague wording in place of mechanical values.

---

# 11. Scaling

Abilities do not independently level up.

An ability may scale from character attributes, equipment, status effects, environment, or other explicitly defined systems, but progression also introduces genuinely stronger ability tiers rather than automatically turning every Beginner ability into a Legendary one.

---

# 12. Usage Restrictions

There is no universal cooldown system.

Rare abilities may define special restrictions such as:

- Once per encounter
- Once per rest
- Once per day
- Limited charges
- Required setup condition

Any such restriction must be visible to the player.

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
