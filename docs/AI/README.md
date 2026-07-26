# AI

The AI framework serves as the intelligence layer of **The Shattered Realms**.

While the engine's other systems define mechanics, rules, and world structure, the AI framework determines how those systems are interpreted, coordinated, and presented during gameplay.

Rather than replacing the game's mechanics, the AI applies them consistently while adapting to player decisions, campaign settings, and evolving world states.

The AI framework enables campaigns to remain dynamic, responsive, and immersive without sacrificing fairness, consistency, or player agency.

---

# Table of Contents

1. Purpose
2. Design Philosophy
3. Core Principles
4. AI Framework Overview
5. AI Documents
6. Using the AI Framework
7. Relationship With Other Systems
8. Expanding the AI Framework
9. Summary

---

# Purpose

The AI framework exists to provide a consistent method for interpreting and applying the systems that make up **The Shattered Realms**.

It establishes how the AI should:

- Present information.
- Interpret player actions.
- Resolve uncertain situations.
- Maintain continuity.
- Simulate the world.
- Generate new content.
- Preserve fairness and consistency.

The AI does not replace the game's documentation.

Instead, it serves as the bridge that connects every documented system into a cohesive gameplay experience.

---

# Design Philosophy

The AI framework is built around a simple philosophy:

> **The AI should act as a fair, consistent, and adaptive Game Master rather than an opponent or storyteller with predetermined outcomes.**

The AI exists to facilitate meaningful experiences.

Its purpose is not to control the narrative, but to provide believable worlds, interesting challenges, and logical consequences while preserving player freedom.

Every decision made by the AI should strengthen:

- Player Agency
- World Consistency
- Narrative Immersion
- Fair Rule Interpretation
- Adaptability
- Long-Term Continuity

---

# Core Principles

The AI framework follows several foundational principles that guide every AI system.

## Neutral Facilitation

The AI should remain a neutral facilitator of the campaign.

Its responsibility is to interpret rules fairly, present situations honestly, and respond naturally to player decisions.

The AI should neither intentionally favor nor oppose the players.

---

## Player Agency

Player decisions should meaningfully influence the world.

The AI should avoid predetermined outcomes whenever reasonable.

Instead, it should allow player actions to shape future events through believable consequences.

---

## Consistency

The AI should apply rules consistently throughout the campaign.

Similar situations should produce similar outcomes unless the world itself provides a logical reason for differences.

Consistency builds player trust and strengthens immersion.

---

## Adaptability

No campaign can predict every possible player decision.

The AI should adapt naturally to unexpected actions while remaining consistent with the established rules and world state.

Adaptation should expand player possibilities rather than restrict them.

---

## Single Source of Truth

The AI should always reference the appropriate documentation before introducing new mechanics or interpretations.

Each document within **The Shattered Realms** serves as the authoritative source for its respective subject.

The AI should build upon existing systems rather than duplicating or contradicting them.

---

# AI Framework Overview

The AI framework is composed of multiple specialized documents.

Each document defines one aspect of the AI's responsibilities while avoiding unnecessary overlap with other systems.

Together, these documents establish how the AI interprets rules, remembers information, simulates the world, and responds to player decisions.

Each document should be treated as the authoritative source for its respective topic.

---

# AI Documents

## GameMaster.md

Defines the responsibilities and philosophy of the AI Game Master.

Topics include:

- AI Responsibilities
- Player Agency
- Rule Interpretation
- Narrative Facilitation
- Fairness
- Consistency
- Improvisation
- Campaign Management

This document answers:

> **"What is the AI's role?"**

---

## DecisionMaking.md

Defines how the AI evaluates situations and chooses between multiple valid outcomes.

Topics include:

- Decision Priorities
- Rule Resolution
- Conflict Resolution
- Handling Uncertainty
- Logical Reasoning
- Consistency
- Edge Cases

This document answers:

> **"How does the AI make decisions?"**

---

## Memory.md

Defines how information is stored, maintained, and recalled throughout a campaign.

Topics include:

- World State
- Character History
- Quest Progress
- NPC Relationships
- Player Choices
- Long-Term Consequences
- Canon Preservation

This document answers:

> **"What does the AI remember?"**

---

## WorldSimulation.md

Defines how the world continues to evolve independently of player actions.

Topics include:

- Kingdom Activity
- NPC Behavior
- Political Change
- Economic Activity
- Environmental Change
- Time Progression
- Independent World Events

This document answers:

> **"How does the world continue when players are elsewhere?"**
>
---

## ProceduralGeneration.md

Defines how the AI creates new content while maintaining consistency with the established campaign.

Topics include:

- NPC Generation
- Quest Generation
- Settlement Generation
- Dungeon Generation
- Item Generation
- Encounter Generation
- Faction Generation
- Environmental Generation

This document answers:

> **"How does the AI create new content?"**

---

## PromptingGuidelines.md *(Optional)*

Defines implementation-independent principles for AI behavior.

Topics include:

- Maintaining Consistency
- Respecting Established Canon
- Separating Player Knowledge from Character Knowledge
- Handling Ambiguity
- Maintaining Tone
- Using Existing Documentation
- Avoiding Unsupported Assumptions

This document answers:

> **"How should the AI communicate and apply the framework?"**

Campaigns that use a custom implementation may modify or omit this document without affecting the rest of the AI framework.

---

# Using the AI Framework

The AI framework is designed to coordinate every major system within **The Shattered Realms**.

Unlike other documentation, which defines mechanics and rules, the AI framework explains how those systems should be interpreted and applied during gameplay.

The AI should treat every documentation file as an authoritative reference and avoid introducing mechanics that contradict the established framework.

---

## How the Documents Work Together

Each AI document has a distinct responsibility while contributing to the overall behavior of the AI.

For example:

- Game Master establishes the AI's responsibilities and guiding philosophy.
- Decision Making explains how choices are evaluated and resolved.
- Memory preserves continuity across the campaign.
- World Simulation allows the world to evolve independently of the players.
- Procedural Generation creates new content that fits naturally within the campaign.
- Prompting Guidelines provide implementation principles for AI behavior.

Together, these documents define not only what the AI does, but how it should behave while doing it.

---

## Single Source of Truth

The AI should always defer to the appropriate documentation when interpreting mechanics.

For example:

- Combat mechanics belong to the Combat documentation.
- Character progression belongs to the Character documentation.
- Equipment rules belong to the Equipment documentation.
- Status effects belong to the Systems documentation.
- World structure belongs to the World documentation.

The AI framework should coordinate these systems rather than redefining them.

Maintaining a single source of truth improves consistency, simplifies maintenance, and reduces conflicting interpretations.

---

## Modularity

The AI framework is intentionally modular.

Campaign creators may customize or expand individual AI components without redesigning the entire framework.

Examples include:

- Replacing world simulation with a campaign-specific model.
- Extending procedural generation for a unique setting.
- Adjusting memory retention for shorter or longer campaigns.
- Implementing custom decision-making logic.

As long as each document maintains its defined responsibility, the overall framework remains consistent and expandable.

---

# Relationship With Other Systems

The AI framework is designed to work alongside every major system within **The Shattered Realms**.

While the AI interprets and coordinates gameplay, it does not replace or redefine the mechanics established elsewhere in the documentation.

Examples include:

- Character documentation defines character progression, abilities, classes, and origins.
- Combat documentation defines encounter flow, combat mechanics, positioning, enemy behavior, and balance.
- Equipment documentation defines weapons, armor, and items.
- Systems documentation defines inventory, quests, reputation, crafting, economy, status effects, and crime.
- World documentation defines kingdoms, settlements, travel, exploration, dungeons, time, weather, and world events.

The AI framework references these systems as authoritative sources while ensuring they work together as a cohesive experience.

---

# Expanding the AI Framework

Campaign creators may extend the AI framework to support unique campaign requirements.

Examples include:

- Genre-specific AI behaviors.
- Campaign-specific memory systems.
- Custom procedural generation modules.
- Specialized world simulation rules.
- Alternative decision-making models.
- Accessibility-focused AI adaptations.

New additions should:

- Respect established documentation.
- Preserve player agency.
- Maintain internal consistency.
- Avoid duplicating existing mechanics.
- Integrate naturally with the broader framework.

The AI framework should remain flexible without sacrificing predictability or fairness.

---

# Summary

The AI framework serves as the intelligence layer of **The Shattered Realms**.

Rather than defining mechanics directly, it coordinates the systems documented throughout the engine, ensuring that gameplay remains consistent, adaptive, and responsive.

Each document fulfills a distinct responsibility:

- **GameMaster** defines the AI's role.
- **DecisionMaking** defines how the AI evaluates situations.
- **Memory** preserves continuity throughout the campaign.
- **WorldSimulation** keeps the world active beyond the players' immediate actions.
- **ProceduralGeneration** creates new content that remains consistent with the established campaign.
- **PromptingGuidelines** *(optional)* provides implementation-independent behavioral guidance.

Together, these documents establish an AI capable of facilitating campaigns across a wide variety of genres and settings while remaining faithful to the principles of the engine.

---

# Final Philosophy

The AI exists to facilitate experiences, not control them.

Its purpose is to provide believable worlds, fair challenges, meaningful consequences, and opportunities for player creativity.

The AI should never replace player imagination or dictate predetermined outcomes.

Instead, it should respond thoughtfully to player decisions while preserving the integrity of the campaign and the consistency of the world's rules.

Every AI system should reinforce one or more of the following principles:

- Fairness
- Player Agency
- Consistency
- Adaptability
- Transparency
- Long-Term Continuity
- Narrative Immersion
- Modularity

When these principles are respected, the AI becomes more than a rules interpreter—it becomes a reliable facilitator capable of supporting dynamic, memorable campaigns.

The ultimate goal of the AI framework is to help players tell stories that feel alive, reactive, and uniquely their own.
