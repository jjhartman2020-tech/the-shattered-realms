# UI

## Purpose

The UI layer defines how players interact with The Shattered Realms.

While gameplay systems define mechanics and application systems define engine behavior, the UI presents those systems to the player through clear, intuitive, and immersive interfaces.

This documentation establishes the principles, responsibilities, and organization of every player-facing interface throughout the engine.

---

# Scope

The UI layer defines:

- Screen layouts
- HUD organization
- Interface navigation
- Information presentation
- User interactions
- Accessibility features
- Visual hierarchy
- Player workflows

The UI layer does **not** define gameplay mechanics, AI behavior, progression systems, combat calculations, inventory rules, dialogue logic, or world simulation.

Those systems remain documented within their respective folders.

---

# UI Philosophy

The interface exists to support the player's experience without becoming the focus of it.

Players should spend their attention exploring the world rather than learning complicated menus.

Every interface should feel like a natural extension of the adventure.

---

# Core Principles

## Information Before Decoration

Every visual element should communicate useful information.

Decorative elements should enhance readability and immersion without reducing clarity.

---

## Immersion Without Obstruction

The interface should never unnecessarily block the player's view of the world.

Only information relevant to the current situation should remain visible.

Additional information should always remain easily accessible.

---

## Consistency

Similar interactions should behave consistently throughout the engine.

Examples include:

- Buttons
- Menus
- Navigation
- Tooltips
- Search
- Filtering
- Sorting
- Confirmation dialogs

Consistency reduces learning time and improves usability.

---

## Context Awareness

Interfaces should adapt to the player's current activity.

Examples include:

- Combat HUD
- Exploration HUD
- Dialogue overlays
- Merchant interfaces
- Crafting windows
- Map overlays

Players should only see information relevant to their current context whenever practical.

---

## Player Choice

Players should be able to customize many aspects of the interface.

Examples include:

- HUD visibility
- HUD scale
- Interface opacity
- Notification behavior
- Key bindings
- Color themes
- Accessibility settings

Customization should improve comfort without affecting gameplay balance.

---

## Accessibility First

Accessibility is a fundamental design goal rather than an optional feature.

Every player should be able to comfortably interact with the game regardless of individual needs.

---

## System Separation

The UI presents information owned by other systems.

The UI never becomes responsible for:

- Combat mechanics
- Character progression
- Dialogue generation
- Inventory management
- AI reasoning
- World simulation

Instead, it displays the authoritative information produced elsewhere.

---

# Navigation Philosophy

The HUD serves as the primary navigation system.

Rather than relying on deep menu structures, players should naturally move between interfaces by interacting with visible HUD elements.

Examples include:

- Character portrait → Player Interface
- Companion portraits → Party Interface
- Mini-map → World Map
- Active quest → Quest Journal
- Notifications → Related information
- Campaign summary → Campaign Hub

Navigation should feel intuitive and require minimal memorization.

---

# Visual Hierarchy

Information should be presented according to importance.

Highest priority:

- Health
- Critical status effects
- Immediate objectives

Medium priority:

- Resources
- Party information
- Navigation
- Current location

Lower priority:

- Statistics
- Historical information
- Completed objectives
- Collection galleries

The player's attention should naturally focus on the most important information first.

---

# Persistent Interfaces

Certain interface elements remain available throughout most gameplay.

Examples include:

- HUD
- Character portrait
- Party overview
- Mini-map
- Notifications

Persistent elements should remain lightweight and unobtrusive.

---

# Contextual Interfaces

Some interfaces appear only when appropriate.

Examples include:

- Merchant interface
- Crafting interface
- Dialogue choices
- Loot windows
- Skill checks
- Confirmation dialogs

Contextual interfaces should disappear once their purpose has been fulfilled.

---

# Interface Ownership

Each UI document owns only its presentation layer.

For example:

The Player Interface defines:

- Layout
- Tabs
- Navigation
- Visual organization

Character systems continue to define:

- Attributes
- Skills
- Equipment rules
- Progression

This separation prevents duplicated documentation and establishes a single source of truth.

---

# Interface Organization

The UI documentation is divided into specialized components.

Each document focuses on one interface rather than attempting to describe every screen.

This modular approach simplifies future expansion and maintenance.

---

# Player Experience Goals

The interface should help players:

- Understand the world
- Make informed decisions
- Manage their characters
- Track progression
- Navigate efficiently
- Access information quickly
- Stay immersed throughout gameplay

Good interface design should feel almost invisible during normal play.

---

# Future Growth

As new gameplay systems are introduced, new interfaces may be added without restructuring the existing UI architecture.

Future interfaces should continue following the principles defined within this document.

---

# Interaction With Other Systems

The UI presents information originating from every major engine subsystem.

Examples include:

- Combat
- Characters
- Progression
- Equipment
- Systems
- AI
- World
- Modding
- Application

The UI owns presentation while each referenced system continues to own its mechanics.

---

# Summary

The UI layer defines how players see, navigate, and interact with The Shattered Realms.

By separating presentation from gameplay logic, emphasizing clarity, consistency, accessibility, and immersion, the UI provides a cohesive experience that allows players to focus on the adventure rather than the interface itself.

Every UI document builds upon the principles established within this README, ensuring a unified and maintainable player experience across the entire engine.
