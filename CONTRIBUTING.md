# Contributing to The Shattered Realms

Welcome to The Shattered Realms.

This repository contains the complete design, architecture, and implementation of an AI-first role-playing game.

Whether you are fixing a typo, improving documentation, designing new systems, or writing engine code, thank you for contributing.

This document explains the standards that keep the project consistent.

---

# Vision

The Shattered Realms is designed around one guiding principle:

> Build an RPG where AI enhances immersion without replacing player agency.

Every contribution should support this vision.

---

# Core Principles

These principles apply to every contribution.

## One Document Owns One System

Every mechanic has a single source of truth.

Do not duplicate mechanics across documents.

If information belongs somewhere else, reference that document instead.

---

## UI Presents

UI documents explain:

- Layout
- Navigation
- Interaction
- Presentation

UI documents never own mechanics.

---

## Systems Own Mechanics

System documents define:

- Rules
- Logic
- Behaviors
- Calculations

Mechanics should never be defined inside UI documentation.

---

## AI Reasons

AI documentation defines:

- Reasoning
- Decision making
- Memory
- Adaptation
- Dialogue generation

AI should never become the authoritative game state.

---

## Engine Owns State

The application is always the source of truth.

Examples include:

Inventory

Quest State

Combat

Progression

Relationships

World State

The AI reads this information.

It never owns it.

---

# Documentation Standards

Documentation should explain:

Why

Before

How

Readers should understand the purpose of a system before implementation details.

---

# File Organization

Contributors should place documentation inside the correct folder.

Examples include:

docs/

character/

combat/

systems/

world/

ui/

ai/

modding/

app/

Avoid creating new folders unless absolutely necessary.

---

# Avoid Duplication

Never copy mechanics into multiple files.

Instead:

Reference the owning document.

Keeping one source of truth prevents inconsistencies.

---

# Writing Style

Documentation should be:

Clear

Direct

Consistent

Professional

Avoid unnecessary jargon.

Prefer concise explanations.

---

# Naming Conventions

Use descriptive names.

Examples:

QuestJournal.md

PlayerInterface.md

CombatFlow.md

Avoid abbreviations unless widely understood.

---

# Formatting

Use Markdown.

Maintain consistent heading structure.

Separate major sections with horizontal rules.

Prefer lists over dense paragraphs when appropriate.

---

# Philosophy Sections

Every major document should begin by answering:

What problem does this document solve?

Every major document should end with:

Design Philosophy

Summary

These sections ensure consistent documentation quality.

---

# Repository Structure

Repository organization exists for clarity.

Do not move files between folders without strong justification.

If a system expands significantly, discuss structural changes before implementing them.

---

# Cross References

When another document owns information:

Reference it.

Do not redefine it.

---

# Design Consistency

Every new feature should ask:

Does this already exist?

Who owns it?

Am I duplicating logic?

Can this integrate with existing systems?

---

# Backwards Compatibility

When changing documentation:

Prefer extending existing systems over replacing them.

Avoid unnecessary rewrites.

Maintain consistency whenever possible.

---

# AI Contributions

AI should enhance:

Immersion

Storytelling

Accessibility

Replayability

Player understanding

AI should never remove meaningful player decisions.

---

# Accessibility

Every contribution should consider accessibility.

Questions to ask include:

Can this be understood?

Can it be navigated?

Can it be customized?

Can it be explained?

Accessibility is part of every feature.

---

# Performance Awareness

When designing new systems:

Consider scalability.

Avoid unnecessary complexity.

Design for long campaigns.

Large worlds should remain performant.

---

# Modularity

Systems should remain loosely coupled.

Each system should have clearly defined responsibilities.

Dependencies should remain intentional.

---

# Pull Request Guidelines

Before submitting changes:

Verify ownership.

Avoid duplicated mechanics.

Maintain formatting.

Update cross references.

Review consistency.

Explain why the change exists.

---

# Issue Reporting

When reporting issues include:

Affected Document

Problem Description

Expected Behavior

Suggested Improvement (optional)

Supporting Context

Clear reports improve development.

---

# Feature Proposals

Before proposing a feature ask:

Does it solve a real problem?

Does another system already solve this?

Does it respect repository philosophy?

Can it integrate cleanly?

Features should improve the project rather than increase complexity.

---

# Code Standards

Implementation should reflect documentation.

Avoid hidden mechanics.

Favor readable code.

Document unusual decisions.

Keep systems modular.

Architecture should remain consistent with repository design.

---

# Testing Philosophy

Every implementation should be tested.

Examples include:

Gameplay

Save/Load

UI

AI

Performance

Accessibility

Regression testing becomes increasingly important as the project grows.

---

# Long-Term Maintenance

This repository is expected to evolve over many years.

Design changes should prioritize:

Clarity

Consistency

Maintainability

Scalability

Future contributors should understand why systems exist.

---

# Project Philosophy

The Shattered Realms is built around thoughtful design rather than feature count.

Every system should have:

A clear purpose.

A defined owner.

Minimal overlap.

Meaningful interaction with the rest of the game.

Complexity should emerge from systems working together—not from individual systems becoming unnecessarily complicated.

If a contribution makes the project easier to understand, easier to maintain, or more enjoyable to play, it is moving the project in the right direction.

---

# Thank You

Thank you for helping build The Shattered Realms.

Whether your contribution is a typo fix, a new mechanic, a performance optimization, or a major gameplay feature, every improvement helps shape the world.

Build thoughtfully.

Document clearly.

Respect player agency.

Create memorable adventures.

Welcome to The Shattered Realms.
