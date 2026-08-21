# Skills.md

Version: 1.0
Status: In Development

This file extends the skill mappings defined in `Stats.md`. If an attribute formula or skill-to-attribute mapping conflicts with `Stats.md`, the core attribute rules in `Stats.md` remain authoritative until the files are reconciled.

---

# 1. Skill Check Formula

Skills represent trained applications of attributes. Attribute Points are never spent directly on skills.

A normal skill check is:

`d20 + Governing Attribute Modifier + Training Bonus + Other Valid Modifiers`

The governing attribute normally comes from the default mapping in `Stats.md`, but the AI Game Master may use a contextual attribute when the player's described method clearly justifies it.

Training stays attached to the **skill**, not the attribute. For example, a character proficient in Intimidation keeps their Intimidation training bonus even when a valid contextual Intimidation (Strength) check replaces Charisma with Strength.

---

# 2. Training Ranks

Every skill has one of three training ranks:

1. **Untrained** — no training bonus.
2. **Proficient** — trained in the skill and receives the normal Proficiency Bonus.
3. **Expertise** — exceptional training in the skill and receives double the normal Proficiency Bonus.

A character cannot gain Expertise in a skill without first being Proficient in that skill, unless a specific character-creation rule explicitly grants Expertise as part of the starting package.

---

# 3. Proficiency Bonus by Character Level

The training bonus grows slowly with character level so trained skills remain meaningful without overwhelming the d20 system.

| Character Level | Proficient | Expertise |
| --- | ---: | ---: |
| 1-20 | +2 | +4 |
| 21-40 | +3 | +6 |
| 41-60 | +4 | +8 |
| 61-80 | +5 | +10 |
| 81-100 | +6 | +12 |

`Expertise Bonus = 2 x Proficiency Bonus`

Untrained skills always receive +0 from training.

Example: A Level 10 character with Agility 18 has a +6 Agility modifier. If they are Proficient in Stealth, their normal Stealth check is `d20 + 6 + 2`, or `d20 + 8`. If they have Expertise in Stealth, it becomes `d20 + 6 + 4`, or `d20 + 10`.

---

# 4. Starting Training

Starting skill training is generated **after the player confirms their attributes** and the AI generates the character's class and backstory.

Every starting character receives the same training budget:

- **3 Proficient skills total.**
- **Up to 1 of those 3 skills may begin with Expertise** when the generated class and/or backstory strongly supports exceptional specialization in that skill.

The AI chooses the starting trained skills from the established skill list based on the generated class and backstory. It may not grant extra starting Proficiencies or Expertise simply because a generated backstory is unusually elaborate.

Examples:

- A former royal assassin may begin trained in Stealth, Sleight of Hand, and another fitting skill, with Expertise potentially in Stealth.
- An artificer may begin trained in Engineering, Investigation, and another fitting skill, with Expertise potentially in Engineering.
- A wilderness tracker may begin trained in Survival, Perception, and another fitting skill, with Expertise potentially in Survival.

The purpose of the AI choice is to make training fit the character's history while keeping every new character on the same mechanical budget.

---

# 5. Gaining Training During Play

Skill training is earned through the character's actual experiences in the world rather than purchased with Attribute Points.

Valid paths toward Proficiency or Expertise include:

- Training with a qualified NPC teacher or mentor.
- Meaningful practice over time.
- Repeated relevant experience as part of genuine gameplay.
- Completing a major story achievement directly related to the skill.
- A class feature, ability, background effect, artifact, blessing, or other explicit rule that grants training.

Training should become part of the campaign world. A character who wants to learn Lockpicking might seek out a thief or locksmith. A character who wants to improve Engineering might study under an inventor, work on machines, or complete a substantial engineering project.

---

# 6. Anti-Spam Rule

Repeatedly attempting the same easy action does **not** automatically create training progress.

The AI Game Master must not award Proficiency or Expertise simply because the player repeatedly rolls the same skill.

Progress must represent meaningful learning, instruction, practice, challenge, accomplishment, or another explicit training source.

The rules engine/campaign state should store awarded training ranks so the AI cannot repeatedly grant or remove them inconsistently.

---

# 7. Proficiency to Expertise

Expertise represents exceptional mastery and should be substantially harder to earn than Proficiency.

A character normally must:

1. Already be Proficient in the skill.
2. Complete significant additional training, repeated high-level practical experience, or a major skill-related accomplishment.
3. Have the promotion to Expertise explicitly awarded and saved to character state.

Ordinary successful checks alone are not enough to turn Proficiency into Expertise.

---

# 8. AI Game Master Responsibilities

The AI Game Master may recognize when a character has completed meaningful training and propose or award skill progression when justified by the campaign state.

The AI must:

- Use the established skill list and training ranks.
- Respect the starting training budget.
- Never fabricate training the character has not earned.
- Never remove earned training without an explicit game mechanic that says it can be lost.
- Avoid awarding progression for spam or trivial repetition.
- Consider teachers, downtime, story accomplishments, and genuine practical experience.
- Save confirmed training changes to persistent character state.

The AI interprets whether the story justifies training. The deterministic game state remains authoritative for which skills are currently Untrained, Proficient, or Expertise and for the numeric bonus attached to each rank.

---

# 9. Contextual Attribute Checks

Training belongs to the skill even when the governing attribute changes because of context.

Example: A character with Intimidation Proficiency normally makes Intimidation (Charisma). If the character bends an iron bar to frighten someone and the Game Master rules that Strength is appropriate, the roll becomes:

`d20 + Strength Modifier + Intimidation Proficiency Bonus`

The character does not need a separate Strength-based Intimidation proficiency.

---

# 10. Design Summary

The skill system has three independent layers:

- **Attribute** = natural capability and build investment.
- **Proficiency** = meaningful training.
- **Expertise** = exceptional mastery.

Attribute Points improve attributes. Training is earned through character creation, gameplay, teachers, accomplishments, or explicit game effects. Character level determines the size of the Proficiency/Expertise bonus but does not automatically decide which skills the character knows.
