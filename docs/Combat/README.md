# Combat

The combat framework provides a modular, campaign-agnostic foundation for resolving conflict within **The Shattered Realms**.

Rather than prescribing a specific ruleset, the framework defines the structure, responsibilities, and design principles required to create fair, engaging, and expandable combat systems across a wide variety of campaign settings.

Every combat document focuses on a single responsibility while working together as part of a unified system.

This approach allows campaign creators to customize combat extensively without sacrificing consistency, maintainability, or player understanding.

---

# Table of Contents

1. Purpose
2. Design Philosophy
3. Core Principles
4. Combat Framework Overview
5. Combat Documents
6. Using the Combat Framework
7. Relationship With Other Systems
8. Expanding Combat
9. Summary

---

# Purpose

The combat framework exists to provide a consistent structure for resolving conflict while preserving player agency, strategic depth, and narrative immersion.

Combat should support the story rather than interrupt it.

Every encounter should encourage meaningful decision-making through mechanics that are understandable, predictable, and adaptable.

The framework intentionally avoids assumptions about campaign genre, setting, scale, or ruleset.

Instead, it provides the architectural foundation upon which individual campaigns may build their own combat mechanics.

---

# Design Philosophy

Combat within **The Shattered Realms** is designed around a simple philosophy:

> **Combat should create meaningful decisions that naturally become memorable stories.**

Victory should come from intelligent choices, teamwork, adaptation, and creativity rather than overwhelming statistics or repetitive strategies.

Likewise, defeat should feel understandable and fair, providing opportunities for players to learn, adapt, and continue their journey.

The combat framework prioritizes:

- Fairness
- Consistency
- Player Agency
- Strategic Depth
- Narrative Integration
- Expandability

Every combat system should reinforce one or more of these principles.

---

# Core Principles

The combat framework follows several foundational principles that guide every combat document.

## Modular Design

Combat is divided into focused documents.

Each document has a clearly defined responsibility and serves as the authoritative source for its subject.

This separation improves readability, simplifies maintenance, and allows campaigns to expand the system without creating conflicting documentation.

---

## Single Source of Truth

Every mechanic should be defined only once.

For example:

- Combat Flow defines encounter structure.
- Core Mechanics defines combat actions.
- Positioning defines battlefield interaction.
- Enemy AI defines opponent behavior.
- Equipment defines equipment.
- Status Effects defines status effects.

Combat documentation should reference external systems rather than redefining them.

This principle helps maintain consistency across the engine as it grows.

---

## Campaign Agnostic

The combat framework intentionally avoids assumptions regarding:

- Dice systems
- Numerical formulas
- Action economies
- Character statistics
- Genres
- Settings
- Technology levels

Campaign creators remain free to implement mechanics appropriate for their own worlds while following the framework established by these documents.

---

## Narrative First

Combat is both a mechanical system and a storytelling tool.

Every encounter should contribute to:

- Character Development
- World Building
- Story Progression
- Player Expression
- Meaningful Consequences

Mechanics and narrative should complement one another rather than compete for the player's attention.

---

# Combat Framework Overview

The combat framework is composed of multiple specialized documents.

Rather than concentrating every mechanic into a single file, the framework separates combat into focused components with clearly defined responsibilities.

Together, these documents create a complete combat system while remaining easy to understand, maintain, and expand.

Each document should be treated as the authoritative source for its respective topic.

---

# Combat Documents

## CombatFlow.md

Defines the overall structure of combat encounters.

Topics include:

- Entering Combat
- Encounter Progression
- Turn Structure
- Objectives
- Ending Combat

This document answers:

> **"When does everything happen?"**

---

## CoreMechanics.md

Defines the core actions and interactions available during combat.

Topics include:

- Combat Actions
- Reactions
- Resources
- Targeting
- Combat Resolution

This document answers:

> **"What can participants do?"**

---

## Positioning.md

Defines spatial interaction throughout combat.

Topics include:

- Battlefield Positioning
- Movement
- Terrain
- Environmental Interaction
- Tactical Space

This document answers:

> **"Where does combat take place?"**

---

## EnemyAI.md

Defines how opponents evaluate situations and make decisions.

Topics include:

- Tactical Decision Making
- Target Selection
- Cooperation
- Adaptation
- Retreat
- Personality

This document answers:

> **"How do enemies think?"**

---

## BossCombat.md

Defines systems unique to major encounters.

Topics include:

- Boss Design
- Encounter Phases
- Unique Mechanics
- Objectives
- Escalation

This document answers:

> **"How are major encounters different?"**

---

## DeathAndRecovery.md

Defines defeat and its consequences.

Topics include:

- Defeat
- Recovery
- Consequences
- Permanent Outcomes
- Returning to Play

This document answers:

> **"What happens after participants fall?"**
>
---

## CombatLog.md

Defines how combat information is communicated to players.

Topics include:

- Combat Narration
- Action Resolution
- Combat History
- Information Management
- Visibility
- Combat Summaries

This document answers:

> **"How is combat communicated?"**

---

## Balance.md

Defines the guiding principles behind combat design.

Topics include:

- Fairness
- Strategic Depth
- Encounter Design
- Difficulty
- Player Agency
- Combat Philosophy

This document answers:

> **"Why is combat designed this way?"**

---

# Using the Combat Framework

The combat framework is designed to be modular.

Each document defines a specific aspect of combat while avoiding unnecessary overlap with other systems.

Campaign creators should reference the appropriate document when implementing or modifying combat mechanics.

The AI Game Master should treat each document as the authoritative source for its respective topic.

---

## How the Documents Work Together

Although each document focuses on a single responsibility, they are designed to operate as a unified framework.

For example:

- Combat Flow determines when events occur.
- Core Mechanics determines what participants can do.
- Positioning determines where interactions take place.
- Enemy AI determines how opponents respond.
- Boss Combat expands encounters with unique mechanics.
- Death and Recovery defines the consequences of defeat.
- Combat Log communicates events to the players.
- Balance ensures every mechanic supports the framework's design philosophy.

Each document contributes to combat without redefining the responsibilities of another.

---

## Single Source of Truth

Every combat mechanic should have one authoritative location within the documentation.

For example:

- Equipment is defined within the Equipment documentation.
- Status Effects are defined within the Systems documentation.
- Character Abilities are defined within the Character documentation.

Combat documentation should reference these systems rather than duplicate their mechanics.

This approach improves consistency, simplifies maintenance, and reduces the likelihood of conflicting rules.

---

## Modularity

Campaign creators are encouraged to extend the combat framework by building upon existing systems instead of replacing them.

Whenever possible, new mechanics should integrate with established documentation.

Examples include:

- Introducing new abilities through the Abilities documentation.
- Adding new equipment through the Equipment documentation.
- Creating new status effects through the Status Effects documentation.
- Expanding combat objectives through the Quest system.

Maintaining modularity allows campaigns to grow while preserving compatibility with the broader engine.

---

# Relationship With Other Systems

Combat is one component of a larger game engine and is designed to integrate seamlessly with the rest of **The Shattered Realms**.

While combat frequently interacts with other systems, each system remains responsible for its own mechanics.

Examples include:

- Character documentation defines statistics, abilities, classes, and origins.
- Equipment documentation defines weapons, armor, and items.
- Systems documentation defines inventory, status effects, quests, reputation, crafting, economy, and crime.
- World documentation defines locations, travel, exploration, settlements, and environmental systems.
- AI documentation defines how the AI Game Master manages encounters, remembers information, simulates the world, and makes decisions.

Combat references these systems rather than redefining them.

This separation keeps the engine organized, modular, and easier to expand.

---

# Expanding the Combat Framework

Campaign creators may introduce additional combat mechanics whenever appropriate.

Examples include:

- New combat actions.
- Specialized boss mechanics.
- Campaign-specific resources.
- Environmental hazards.
- Unique encounter objectives.
- Custom AI behaviors.
- Genre-specific combat rules.

New mechanics should:

- Respect the framework's existing responsibilities.
- Integrate with established systems.
- Avoid duplicating existing documentation.
- Preserve fairness and consistency.
- Encourage meaningful player decisions.

Expanding the framework should strengthen the overall system rather than increase unnecessary complexity.

---

# Summary

The combat framework provides a structured foundation for resolving conflict across a wide variety of campaign settings.

By separating combat into specialized documents with clearly defined responsibilities, the framework remains flexible, maintainable, and adaptable without sacrificing consistency.

Each document contributes a unique piece of the overall system:

- Combat Flow organizes encounters.
- Core Mechanics defines participant actions.
- Positioning governs spatial interaction.
- Enemy AI controls opponent behavior.
- Boss Combat expands major encounters.
- Death and Recovery defines the consequences of defeat.
- Combat Log communicates encounters clearly.
- Balance establishes the principles that guide combat design.

Together, these documents create a complete combat framework capable of supporting everything from small skirmishes to large-scale battles across any genre or setting.

---

# Final Philosophy

Combat is more than a method of resolving conflict.

It is an opportunity for players to make meaningful decisions, express their creativity, overcome challenges, and shape the stories that emerge from the campaign.

The framework is intentionally designed to support these experiences without restricting the imagination of campaign creators or players.

Every combat mechanic should reinforce one or more of the following principles:

- Fairness
- Player Agency
- Strategic Depth
- Adaptability
- Consistency
- Narrative Integration
- Modularity

When these principles are respected, combat becomes more than a collection of mechanics—it becomes an engaging part of the world's ongoing story.

The goal of the combat framework is not simply to determine victory or defeat, but to create encounters that players will remember long after the battle has 
