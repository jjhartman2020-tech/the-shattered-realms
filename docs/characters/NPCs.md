# NPCs.md

**Location:** `/docs/characters/NPCs.md`

Version: 1.0  
Status: In Development

---

# Table of Contents

1. NPC Philosophy
2. NPC Identity
3. NPC Profiles
4. Biography and Player Connection
5. Levels and Stats
6. Classes and Abilities
7. Equipment and Inventory
8. Personality
9. Goals and Decision Making
10. Daily Life and Schedules
11. Memory
12. Relationships
13. Player Relationship
14. Knowledge and Information
15. Dialogue Behavior
16. Growth and Progression
17. Current Status
18. NPC Death
19. AI-Generated NPCs
20. NPC Journal
21. Standard NPC Template
22. Balance Philosophy
23. Future Systems

---

# 1. NPC Philosophy

NPCs should feel like people who exist within the world rather than characters who exist only to serve the player.

The world does not exist for the player.

The player exists within the world.

NPCs should have:

- Personal histories
- Relationships
- Responsibilities
- Goals
- Fears
- Beliefs
- Daily routines
- Memories
- Strengths
- Weaknesses

NPCs should continue living and making decisions even when the player is not nearby.

They may:

- Work
- Travel
- Form relationships
- Join factions
- Complete goals
- Gain levels
- Change occupations
- Move homes
- Become injured
- Be imprisoned
- Retire
- Disappear
- Die

Important events should not wait forever for the player.

---

# 2. NPC Identity

Every NPC must have a clear identity.

Core identity information includes:

- Name
- Title or nickname
- Age
- Race or species
- Gender
- Occupation
- Class
- Level
- Home
- Current location
- Faction
- Current status

NPCs may also have:

- Religious beliefs
- Political beliefs
- Cultural background
- Social class
- Family name
- Reputation
- Criminal history
- Military rank
- Guild rank

Not all information should immediately be known to the player.

Unknown information may become visible through conversation, investigation, observation, quests, or other characters.

---

# 3. NPC Profiles

Every important NPC should have a permanent profile.

The profile acts as the official record of:

- Who the NPC is
- What they look like
- How the player knows them
- Their history
- Their level
- Their stats
- Their abilities
- Their equipment
- Their relationships
- Their memories
- Their current status

Minor NPCs may begin with simplified profiles.

If a minor NPC becomes important, the AI should expand their profile while preserving all previously established information.

NPC information must remain consistent across the campaign.

---

# 4. Biography and Player Connection

Every known NPC should have two separate descriptions.

## Who They Are

A short biography explaining:

- Their background
- Their role in the world
- Their occupation
- Their important history
- Their current situation

Example:

> Elara Voss is a former royal scout who now protects travelers moving through the Ashwood region. She left the royal army after refusing an order to attack civilians.

## How You Know Them

A short explanation of how the player first encountered the NPC and what has happened between them.

Example:

> You first met Elara after helping her defend a merchant caravan from bandits near Ashwood. She later guided you through the northern forest.

This description should update as the relationship develops.

Important shared experiences should be added without removing established history.

---

# 5. Levels and Stats

Every NPC has a level.

NPC levels use the same maximum level of **97** established in `Leveling.md`.

An NPC's level represents:

- Experience
- Combat ability
- Training
- Knowledge
- Survival skill
- Magical strength
- Professional mastery

A high level does not always mean the NPC is a warrior.

Examples:

- A high-level blacksmith may be extremely skilled at crafting but only moderately capable in combat.
- A high-level scholar may possess powerful knowledge and magical abilities.
- A low-level noble may have great political influence without being physically strong.

NPCs use the same nine core attributes as the player:

- Health
- Mana
- Strength
- Dexterity
- Constitution
- Intelligence
- Wisdom
- Charisma
- Speed

Each NPC profile should show:

- Level
- Maximum Health
- Current Health
- Maximum Mana
- Current Mana
- Attribute values
- Resistances
- Immunities
- Active Status Effects

Base attributes follow the natural cap of **60**.

Equipment, abilities, buffs, transformations, and special conditions may raise effective attributes beyond 60.

---

# 6. Classes and Abilities

NPCs may use:

- Standard classes
- AI-generated classes
- Profession-based classes
- Unique classes
- Creature-specific classes
- Boss classes

Their class should match their:

- History
- Training
- occupation
- culture
- personality
- role in the world

NPC abilities follow the established ability system.

Abilities may have:

- Class requirements
- Attribute requirements
- Resource costs
- Ability Point costs

NPCs should not possess random abilities that conflict with their identity.

Important NPC profiles should display:

- Class
- Passive abilities
- Active abilities
- Ultimate ability
- Equipped active abilities
- Resource type

The player should only see abilities they have discovered through observation, combat, dialogue, investigation, or shared history.

---

# 7. Equipment and Inventory

NPCs possess real equipment and inventories.

Possible items include:

- Weapons
- Armor
- Shields
- Accessories
- Consumables
- Tools
- Keys
- Currency
- Quest items
- Personal belongings
- Crafting materials

NPC equipment should reflect:

- Occupation
- Wealth
- Faction
- Location
- Level
- Personality
- Current activity

An NPC should not automatically generate replacement equipment after losing it.

If equipment is:

- Stolen
- Destroyed
- Sold
- Given away
- Dropped upon death

The NPC loses access to it unless they obtain another item naturally.

NPCs may upgrade, replace, repair, sell, hide, or lend equipment.

---

# 8. Personality

Every important NPC should have a consistent personality.

Personality information may include:

- Core traits
- Temperament
- Values
- Beliefs
- Humor
- Confidence
- Patience
- Honesty
- Loyalty
- Aggression
- Compassion
- Curiosity
- Greed
- Courage

NPCs should not react identically to the same situation.

For example:

- A cautious NPC may avoid an uncertain battle.
- A loyal NPC may remain despite terrible odds.
- A greedy NPC may betray someone for enough money.
- A proud NPC may reject help.
- A compassionate NPC may protect a stranger.

Personality can slowly change through major life experiences.

Changes should be recorded and should not happen without a believable reason.

---

# 9. Goals and Decision Making

Every important NPC should have goals.

Goals may be:

- Immediate
- Short-term
- Long-term
- Secret
- Personal
- Professional
- Political
- Faction-related

Examples include:

- Protecting their family
- Becoming a knight
- Gaining wealth
- Escaping a criminal past
- Taking revenge
- Discovering forbidden knowledge
- Becoming ruler
- Rebuilding a destroyed home
- Surviving a war

NPC decisions should consider:

- Personality
- Goals
- Fears
- Relationships
- Memories
- Available information
- Current resources
- Health
- Location
- Faction orders
- World events
- Risk

NPCs should not know information they have never learned.

They may make mistakes based on incomplete or false information.

---

# 10. Daily Life and Schedules

NPCs should have believable daily routines.

Activities may include:

- Sleeping
- Eating
- Working
- Training
- Shopping
- Traveling
- Socializing
- Worshipping
- Patrolling
- Studying
- Resting
- Caring for family

Schedules may change because of:

- Weather
- War
- Illness
- Injury
- Holidays
- Crime
- Faction orders
- Personal emergencies
- Player actions
- World events

NPCs should not remain permanently frozen in one location.

The player may fail to find an NPC because that person is:

- At work
- Sleeping
- Traveling
- Hiding
- Imprisoned
- Completing another task
- Visiting someone
- Dead

---

# 11. Memory

NPCs remember important events.

Possible memories include:

- Meeting the player
- Being helped
- Being threatened
- Being injured
- Being robbed
- Being deceived
- Receiving a gift
- Losing a family member
- Completing a quest
- Witnessing a crime
- Fighting beside the player
- Being abandoned
- Being rescued
- Being betrayed

Memories should include:

- What happened
- Who was involved
- Where it happened
- When it happened
- How the NPC interpreted it
- Emotional importance
- Whether the memory is public or private

Minor memories may fade or become less important.

Major memories may remain permanently.

NPCs can remember events incorrectly, misunderstand motives, or believe false information.

NPC memory must distinguish between:

- What actually happened
- What the NPC witnessed
- What the NPC was told
- What the NPC believes

---

# 12. Relationships

NPCs may have relationships with:

- Family
- Friends
- Partners
- Rivals
- Enemies
- Mentors
- Students
- Employers
- Employees
- Faction members
- Political allies
- The player

Each relationship may track:

- Trust
- Respect
- Loyalty
- Fear
- Affection
- Anger
- Suspicion
- Debt
- Rivalry

Relationships may change through direct interaction or world events.

NPCs should discuss, defend, betray, assist, mourn, or oppose others based on these relationships.

Relationships between NPCs continue changing without player involvement.

---

# 13. Player Relationship

Every known NPC should have a specific relationship record for the player.

This record should include:

- How you know them
- First meeting
- Current opinion
- Trust
- Respect
- Loyalty
- Fear
- Suspicion
- Important shared events
- Promises
- Debts
- Betrayals
- Current attitude
- Relationship status

Possible attitudes include:

- Loving
- Loyal
- Friendly
- Respectful
- Neutral
- Suspicious
- Afraid
- Hostile
- Vengeful

An NPC may feel several emotions toward the player at the same time.

For example, an NPC may respect the player's strength while fearing their cruelty.

NPC reactions should be based on personal knowledge, not global player reputation alone.

---

# 14. Knowledge and Information

Each NPC has limited knowledge.

NPC knowledge may come from:

- Personal experience
- Education
- Profession
- Observation
- Rumors
- Friends
- Faction reports
- Letters
- Books
- Spies
- The player

NPCs must not possess unlimited knowledge of the world.

Information can be:

- True
- False
- Incomplete
- Outdated
- Misunderstood
- Secret

NPCs may:

- Share information
- Hide information
- Sell information
- Forget information
- Lie
- Spread rumors
- Investigate
- Verify claims

Secret information should only be revealed when the NPC has a believable reason.

---

# 15. Dialogue Behavior

NPC dialogue should reflect:

- Personality
- Education
- Culture
- Occupation
- Mood
- Relationship with the player
- Current goals
- Memories
- Knowledge
- Location
- Situation

Each important NPC should have a speaking style.

This may include:

- Formal or casual speech
- Vocabulary
- Accent description
- Sentence length
- Humor
- Repeated phrases
- Emotional openness
- Honesty
- Confidence

NPCs should not repeat identical dialogue unless it makes sense.

Dialogue must remain consistent with what the NPC knows and believes.

Detailed conversation rules will be defined in `Dialogue.md`.

---

# 16. Growth and Progression

NPCs can grow over time.

They may:

- Gain XP Orbs
- Gain levels
- Increase attributes
- Unlock abilities
- Find equipment
- Learn professions
- Change classes
- Improve relationships
- Gain ranks
- Become weaker from age, injury, curses, or disease

NPC growth should be connected to actual experiences.

Examples:

- A soldier who survives a war may level up.
- An apprentice may become a master blacksmith.
- A companion who travels with the player may unlock new abilities.
- A defeated rival may train and return stronger.

NPCs should not automatically scale to the player.

Some NPCs will remain weaker.

Others may become far stronger.

---

# 17. Current Status

Every NPC profile must show a current status.

Possible statuses include:

- Alive
- Dead
- Missing
- Imprisoned
- Traveling
- Injured
- Ill
- Retired
- Recruited
- In Hiding
- Corrupted
- Captured
- Exiled
- Unknown

The status may include additional details.

Example:

```text
Current Status:
Alive — Traveling toward Ironhaven with a merchant caravan.
```

Status changes should include:

- Date or world time
- Cause
- Location
- Known witnesses
- Whether the player knows

The player's journal should not reveal a status the player has no way of knowing.

---

# 18. NPC Death

Almost every NPC may die.

NPC death should have consequences.

Possible consequences include:

- Shops closing
- Leadership changing
- Family members reacting
- Quests changing
- Factions seeking revenge
- Prices rising
- Services disappearing
- Apprentices taking over
- Rivals gaining power
- Communities weakening

Quests should adapt rather than automatically break.

Dead NPCs remain dead unless a specific established resurrection system applies.

NPCs drop the equipment and inventory they were carrying, following the game's death and inventory rules.

The world should remember their death.

---

# 19. AI-Generated NPCs

The AI may generate NPCs when the world requires them.

Generated NPCs should be based on:

- Location
- Culture
- Population
- Occupation needs
- Factions
- Current events
- Local economy
- World history
- Existing relationships

The AI should avoid generating unnecessary duplicate characters.

Generated NPCs must receive persistent identities.

Once established, their important information becomes canon and must remain consistent.

The AI must not rewrite an NPC's:

- Name
- Appearance
- Personality
- History
- Relationships
- Level
- Class
- Major memories

Unless a real in-world event causes the change.

---

# 20. NPC Journal

The player may access a journal containing known NPCs.

Each journal entry should display only discovered information.

The journal may include:

- Name
- Portrait
- Title
- Who they are
- How you know them
- Current known status
- Level
- Known class
- Known faction
- Known location
- Relationship
- Important memories
- Quest history
- Known abilities
- Known equipment

Unknown details should display as:

- Unknown
- Undiscovered
- Unconfirmed
- Rumored

The journal should clearly separate confirmed facts from rumors.

---

# 21. Standard NPC Template

Every important NPC should use the following structure:

```markdown
# NPC Name

## Basic Information

**Full Name:**  
**Title or Nickname:**  
**Age:**  
**Race or Species:**  
**Gender:**  
**Occupation:**  
**Class:**  
**Level:**  
**Faction:**  
**Home:**  
**Current Location:**  
**Current Status:**  

## Who They Are

Short biography explaining the NPC's identity, history, occupation, and role in the world.

## How You Know Them

Explanation of the first meeting and important shared history between the NPC and the player.

## Appearance

Physical appearance, clothing, equipment, distinguishing features, and general presentation.

## Personality

**Core Traits:**  
**Values:**  
**Beliefs:**  
**Fears:**  
**Likes:**  
**Dislikes:**  
**Speaking Style:**  

## Goals

**Immediate Goal:**  
**Long-Term Goal:**  
**Secret Goal:**  

## Player Relationship

**Current Opinion:**  
**Trust:**  
**Respect:**  
**Loyalty:**  
**Fear:**  
**Suspicion:**  
**Relationship Status:**  

## Stats

**Maximum Health:**  
**Current Health:**  
**Maximum Mana:**  
**Current Mana:**  

**Health:**  
**Mana:**  
**Strength:**  
**Dexterity:**  
**Constitution:**  
**Intelligence:**  
**Wisdom:**  
**Charisma:**  
**Speed:**  

## Resistances and Immunities

**Resistances:**  
**Immunities:**  
**Current Status Effects:**  

## Abilities

**Passive Abilities:**  
**Active Abilities:**  
**Ultimate Ability:**  
**Resource Type:**  

## Equipment

**Weapon:**  
**Armor:**  
**Shield:**  
**Accessories:**  
**Other Carried Items:**  
**Currency:**  

## Relationships

**Family:**  
**Friends:**  
**Allies:**  
**Rivals:**  
**Enemies:**  
**Faction Relationships:**  

## Memory

Important memories involving the player, other NPCs, factions, and world events.

## Knowledge

Information the NPC knows, believes, suspects, or has heard as a rumor.

## Daily Schedule

The NPC's normal routine and how it changes under unusual conditions.

## Quest History

Quests given, completed, failed, changed, or connected to this NPC.

## Important Events

Major events that permanently changed the NPC.

## AI Notes

Private instructions used to preserve consistency in behavior, knowledge, personality, and decision making.
```

---

# 22. Balance Philosophy

## Design Goals

- NPCs should feel consistent.
- NPCs should have believable strengths and weaknesses.
- Important NPCs should remain memorable.
- Player actions should have lasting consequences.
- NPC knowledge should remain limited and realistic.
- NPCs should not automatically trust or hate the player.
- NPCs should continue developing without the player.
- Levels and stats should reflect the NPC's actual life and training.

The AI should prioritize consistency over convenience.

---

# 23. Future Systems

Possible future additions include:

- Aging
- Marriage
- Children
- Inheritance
- Generational NPCs
- Advanced occupations
- NPC-controlled businesses
- Political careers
- Elections
- Dynamic migration
- Disease and recovery
- Psychological development
- Personal journals
- Letters and messaging
- NPC-created quests
- NPC-controlled parties
