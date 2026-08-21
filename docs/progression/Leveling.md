# Leveling.md

**Location:** `/docs/progression/Leveling.md`

Version: 2.0  
Status: In Development

---

# 1. Leveling Philosophy

Progression rewards exploration, quests, difficult enemies, discoveries, puzzles, story progress, faction goals, companion stories, world events, and other meaningful accomplishments rather than repetitive farming.

The maximum player level is **100**.

---

# 2. XP Orbs

The game uses **XP Orbs** instead of traditional experience points.

XP Orbs earned toward the next level carry over if a reward causes multiple level-ups. XP Orbs are not lost on death.

The XP requirement has a real increasing curve. Early levels arrive quickly, while high levels require increasingly larger accomplishments.

The authoritative runtime formula for advancing from Level `L` to `L + 1` is:

`XP Required = round(5 x 1.06^(L - 1) + 1.2 x (L - 1))`

The minimum requirement is 5 XP Orbs. Level 100 is the cap and has no next-level requirement.

Example checkpoints:

| Current Level | XP Orbs to Next Level |
|---:|---:|
| 1 | 5 |
| 5 | 11 |
| 10 | 19 |
| 20 | 38 |
| 30 | 62 |
| 40 | 95 |
| 50 | 146 |
| 75 | 462 |
| 99 | 1627 |

The formula, not the example table, is authoritative.

---

# 3. Skill Points (SP)

**Skill Points (SP)** are the currency used to increase the 13 core stats in `Stats.md`.

This replaces the old term **Attribute Points** so it cannot be confused with Ability Points.

Character creation grants **42 starting SP**.

Every level after Level 1 grants:

**+3 SP**

SP may be saved and spent later. The 13 core stats retain their natural cap of 100.

Leveling does **not** automatically grant Maximum Health. Health increases by investing SP into the Health stat, where 1 Health = 5 Maximum HP.

---

# 4. Ability Points (AP)

**Ability Points (AP)** are used only to unlock abilities.

AP income increases as the player reaches higher levels:

| Level Reached | AP Gained on That Level-Up |
|---:|---:|
| 2-10 | +1 AP |
| 11-20 | +2 AP |
| 21-30 | +3 AP |
| 31-40 | +4 AP |
| 41-50 | +5 AP |
| 51-100 | +6 AP |

Unused AP may be saved indefinitely.

---

# 5. Ability Tiers and Unlock Costs

Abilities are grouped into five progression tiers. Their AP unlock cost scales sharply with power:

| Ability Tier | AP Cost |
|---|---:|
| Beginner | 1 AP |
| Novice | 3 AP |
| Expert | 6 AP |
| Master | 10 AP |
| Legendary | 15 AP |

Tier represents the overall mechanical strength of the ability, not only damage. Movement, healing, defense, summoning, crowd control, targeting, area size, duration, utility, and other effects all contribute to tier.

A character may save AP for a higher-tier ability instead of spending immediately.

---

# 6. AP Cost vs Resource Cost

Ability Point Cost and combat Resource Cost are separate gates.

- **AP Cost** decides whether the ability can be permanently unlocked.
- **Resource Cost** decides whether the unlocked/equipped ability can actually be activated during play.

A player may unlock and equip an ability even if its Resource Cost is greater than their current maximum Resource. In that case the ability remains unusable until the character raises Resource enough to pay the full cost.

---

# 7. Equipment Progression

Weapons and equipment do not automatically improve when the player levels up.

Stronger equipment is earned through the world: quests, bosses, exploration, shops, crafting, factions, hidden rewards, story events, and other gameplay sources.

Early-game equipment should be intentionally modest. More dangerous or advanced content may provide stronger weapons, stronger effects, and higher Resource-cost equipment.

---

# 8. Experience Sources

XP Orb rewards may come from:

- Main and side quests
- Bosses and meaningful combat encounters
- Exploration and hidden locations
- Puzzles and discoveries
- Story milestones
- Companion and faction quests
- World events
- Exceptional achievements

Combat is only one path to progression.

---

# 9. Reward Guidance

XP Orb rewards should be judged against the player's current next-level requirement rather than using one fixed reward table for the entire game.

General goal:

- Small accomplishments contribute noticeable progress.
- Major quests may provide a large portion of a level.
- Bosses and major story milestones may grant one or more levels when appropriate.
- Repetitive low-risk farming should not be the fastest progression path.

---

# 10. Level-Up Summary

Whenever a player levels up, the game should clearly display:

- New Level
- XP Orbs remaining toward the next level
- XP Orbs required for the next level
- SP gained
- Current unspent SP
- AP gained
- Current unspent AP

If one XP reward causes multiple level-ups, each level's AP reward is calculated using the level reached.

---

# 11. Terminology

To prevent confusion:

- **SP = Skill Points = improve core stats.**
- **AP = Ability Points = unlock abilities.**
- **Resource = combat energy used to activate abilities and certain equipment.**
- **XP Orbs = progression currency used to gain character levels.**

These terms must remain distinct in the UI, AI narration, save data, and documentation.
