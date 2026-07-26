# HUD

## Purpose

The HUD (Heads-Up Display) serves as the player's primary interface throughout gameplay.

Rather than functioning solely as an information display, the HUD acts as the central navigation layer connecting the player to every major interface within The Shattered Realms.

The HUD should remain informative, responsive, and unobtrusive while supporting immersion during exploration, combat, dialogue, and other gameplay activities.

---

# Scope

This document defines:

- HUD layout
- Persistent interface elements
- Navigation behavior
- Context-sensitive elements
- Information hierarchy
- Player interaction
- HUD customization
- HUD visibility rules

This document does not define gameplay mechanics or system behavior.

---

# HUD Philosophy

The HUD should feel like a natural extension of the game world rather than an overlay sitting on top of it.

Players should instinctively know where important information is located without searching through menus.

Every persistent HUD element should serve a clear purpose.

---

# Primary Responsibilities

The HUD is responsible for:

- Presenting critical gameplay information
- Providing quick navigation
- Displaying player status
- Displaying party status
- Displaying current objectives
- Presenting notifications
- Providing immediate access to frequently used interfaces

The HUD should never replace full interfaces.

Instead, it should provide concise summaries that allow players to quickly access deeper information when desired.

---

# HUD Design Principles

## Minimal Obstruction

The HUD should occupy as little screen space as possible while remaining readable.

The game world should remain the visual focus.

---

## Immediate Readability

Important information should be understandable within a single glance.

Players should never need to interpret complicated layouts during combat or exploration.

---

## Consistent Placement

Persistent HUD elements should remain in predictable locations.

Players should build muscle memory over time.

Examples include:

- Character portrait
- Party portraits
- Mini-map
- Objective tracker
- Resource bars

---

## Expand Rather Than Replace

HUD elements should expand into larger interfaces instead of opening entirely unrelated menus.

Examples include:

Character Portrait

↓

Player Interface

Mini Map

↓

World Map

Quest Tracker

↓

Quest Journal

Party Portrait

↓

Party Interface

This creates a natural navigation experience.

---

# HUD States

The HUD adapts according to gameplay context.

Major states include:

- Exploration
- Combat
- Dialogue
- Cinematics
- Menus

Each state determines which HUD components remain visible.

---

# Exploration HUD

During exploration the HUD presents general gameplay information while minimizing distractions.

Typical visible elements include:

- Character portrait
- Health
- Resource bars
- Party portraits
- Mini-map
- Active objective
- Time
- Weather
- Notifications

---

# Combat HUD

Combat increases information density.

Additional information may include:

- Turn order
- Ability shortcuts
- Status effects
- Enemy information
- Target indicators
- Cooldowns
- Combat log summary

Combat-specific information disappears once combat concludes.

---

# Dialogue HUD

During dialogue, unnecessary HUD elements fade away.

Visible components typically include:

- Character portrait
- Dialogue window
- Speaker information
- Dialogue choices
- Relationship indicators (when appropriate)
- Skip and history controls

The world should remain partially visible whenever practical.

---

# Cinematic HUD

During cinematics, nearly all HUD elements disappear automatically.

Optional elements may include:

- Subtitle controls
- Skip prompts
- Accessibility indicators

Cinematics should prioritize immersion.

---

# Core Layout

The HUD consists of several persistent regions.

Example layout:

Top

- Time
- Weather
- Region
- Compass

Upper Right

- Mini-map

Lower Left

- Player HUD

Lower Center

- Party HUD

Lower Right

- Active objective
- Notifications

The exact artistic presentation may evolve while maintaining functional consistency.

---

# Character Portrait

The character portrait serves as the primary anchor of the HUD.

It should always remain visible except during cinematics or when intentionally hidden by the player.

The portrait represents the player's character using a circular profile image.

Portraits should update dynamically throughout the campaign.

Examples include:

- Current armor
- Equipped helmet
- Facial appearance
- Hair style
- Permanent scars
- Cosmetic customization

The portrait creates a personal connection between the player and their character.

---

# Character Portrait Interaction

Selecting the character portrait opens the Player Interface.

The portrait does not display every available statistic.

Instead, it provides quick access to the complete character interface.

Example navigation:

Character Portrait

↓

Player Interface

The Player Interface remains documented separately.

---

# Player Status

Adjacent to the character portrait, the HUD displays concise player information.

Examples include:

- Health
- Primary resource
- Active buffs
- Active debuffs
- Experience progress (optional)
- Level

Only essential information should remain permanently visible.

---

# Party HUD

The Party HUD provides a quick overview of active companions.

Rather than opening a full management screen, the HUD displays concise companion summaries.

Each active companion is represented by a circular portrait matching the visual style of the player portrait.

Portrait consistency helps players quickly recognize companions during gameplay.

---

# Companion Portraits

Each companion portrait may display:

- Portrait
- Current health
- Status effects
- Downed indicator
- Selection indicator

Portraits should remain visually compact.

Detailed statistics belong within the Party Interface.

---

# Companion Interaction

Selecting a companion portrait opens that companion's Party Interface page.

From there players may review:

- Equipment
- Skills
- Biography
- Relationship
- Current task
- Statistics
- Appearance

The HUD remains focused on quick access rather than detailed management.

---

# Party Summary

When the party contains additional companions beyond the visible limit, the HUD should summarize remaining members.

Example:

+3

Selecting the summary expands the complete Party Interface.

This prevents HUD overcrowding while preserving accessibility.

---

# Mini-Map

The Mini-Map provides immediate spatial awareness without requiring the player to open the full World Map.

It should remain compact while presenting only the information necessary for navigation.

The Mini-Map supplements exploration rather than replacing environmental observation.

---

# Mini-Map Information

Depending on player progression and current context, the Mini-Map may display:

- Player location
- Party location
- Current heading
- Quest markers
- Custom pins
- Nearby merchants
- Inns
- Blacksmiths
- Fast travel points
- Major landmarks
- Dungeon entrances
- Region borders (optional)
- Fog of war
- Search radius indicators

Information should respect exploration progress.

Undiscovered locations should never appear automatically.

---

# Mini-Map Interaction

Selecting the Mini-Map opens the full Map Interface.

Example:

Mini-Map

↓

Map Interface

The HUD never replaces the complete navigation tools available within the Map Interface.

---

# Compass

A compass remains positioned near the Mini-Map.

The compass provides orientation without requiring players to rotate the map.

The compass may also display:

- Objective direction
- Party member direction
- Custom waypoint direction

Compass indicators should remain subtle.

---

# Objective Tracker

The Objective Tracker provides a concise summary of the player's current focus.

Only one primary objective should remain pinned by default.

Examples:

Investigate Project Ashfall

Return to Ironhold

Speak with Captain Rowan

Escape the Ruins

The tracker summarizes progress rather than replacing the Quest Journal.

---

# Objective Interaction

Selecting the Objective Tracker opens the Quest Journal.

Players should immediately access:

- Active objectives
- Quest descriptions
- Optional objectives
- Progress
- Rewards
- Related notes

---

# Summary HUD

The Summary HUD provides important world information at a glance.

Examples include:

Current Region

Current Settlement

Current Time

Weather

Season

Difficulty

Gold

Encumbrance (optional)

These values should update automatically as gameplay changes.

---

# Time Display

Time should remain visible during exploration.

Examples include:

8:42 PM

Day 47

Late Evening

Moon Phase

Season

Exact formatting may vary depending on player settings.

---

# Weather Display

Weather should display through concise icons accompanied by optional text.

Examples:

Sunny

Rain

Heavy Snow

Thunderstorm

Fog

Weather information should remain informative without occupying excessive space.

---

# Notification Area

A dedicated notification region presents important events.

Notifications should never interrupt gameplay unnecessarily.

Examples include:

Quest Updated

Level Up

Companion Joined

Relationship Increased

Item Acquired

Achievement Unlocked

Save Complete

World Event

Notifications should appear briefly before fading automatically.

---

# Notification Priority

Notifications should follow consistent priority levels.

Critical

Examples:

Player Death

Quest Failure

Important Story Event

Major Companion Event

High

Examples:

Quest Update

Level Up

Relationship Change

Medium

Examples:

Items Found

Crafting Complete

Location Discovered

Low

Examples:

Autosave

Journal Updated

Lore Added

Lower-priority notifications should never obscure critical information.

---

# Resource Indicators

Primary resources remain visible beside the character portrait.

Typical examples include:

Health

Mana

Energy

Stamina

Rage

Focus

Only resources relevant to the player's class or current gameplay should appear.

Unused resources should remain hidden.

---

# Status Effects

The HUD presents only active status effects.

Each effect should display through a recognizable icon.

Selecting a status icon may display:

Effect Name

Description

Duration

Source

Stack Count

Detailed mechanics remain documented within Status Effects.

---

# Quick Access Shortcuts

Frequently used interfaces should remain accessible without opening large menus.

Examples include:

Inventory

Quest Journal

Map

Campaign Hub

Media Gallery

Character

Party

Quick access should reduce unnecessary navigation while maintaining immersion.

---

# HUD Navigation

The HUD serves as the central navigation layer connecting major interfaces.

Example flow:

Character Portrait

↓

Player Interface

Party Portrait

↓

Party Interface

Mini-Map

↓

Map Interface

Objective Tracker

↓

Quest Journal

Campaign Summary

↓

Campaign Hub

Recent Image

↓

Media Gallery

This navigation philosophy minimizes menu depth throughout the game.

---

# Campaign Summary

A compact campaign summary may remain available during exploration.

Examples include:

Current Campaign

Current Chapter

Current Objective

Last Save

Session Duration

Selecting the summary opens the Campaign Hub.

---

# Media Shortcut

When recent AI-generated media exists, the HUD may present a small preview.

Examples include:

Newest Character Portrait

Recent Story Illustration

Generated Landscape

Recent Cinematic

Selecting the preview opens the Media Gallery.

This allows players to revisit generated content without searching through menus.

---

# DM Message Indicator

When new narration or important story information becomes available, the HUD should indicate unread messages.

Examples include:

Story Updates

Companion Messages

Narrative Recaps

System Announcements

Selecting the indicator expands the conversation history.

Dialogue mechanics remain defined within Characters/Dialogue.

---

# Interaction Feedback

Every selectable HUD element should clearly communicate interaction.

Examples include:

Hover highlight

Selection animation

Controller focus

Touch feedback

Audio confirmation

Visual feedback improves usability while reinforcing interface consistency.

---

# Auto-Hide Behavior

Players may optionally enable automatic HUD hiding.

When enabled:

The HUD fades during exploration.

Movement, combat, interaction, or notifications restore visibility immediately.

Automatic hiding improves immersion while preserving accessibility.

---

# HUD Customization

Players should control the appearance of the HUD.

Examples include:

Scale

Opacity

Element visibility

Portrait size

Mini-Map size

Notification duration

Objective visibility

Party display

Customization should never affect gameplay balance.

---

# Platform Adaptation

The HUD should adapt naturally to the player's platform while maintaining consistent functionality.

Supported layouts include:

- PC
- Console
- Mobile (where applicable)
- Steam Deck and handheld devices
- Future supported platforms

Layout changes should improve usability without changing navigation principles.

---

# Screen Scaling

HUD elements should automatically adjust to different display sizes and resolutions.

Scaling should preserve:

- Readability
- Touch accessibility
- Controller navigation
- Mouse precision

Players should also be able to manually adjust interface scale.

---

# Safe Areas

HUD components should respect platform safe areas.

No critical information should appear underneath:

- Device notches
- Rounded display corners
- System overlays
- Platform navigation bars

---

# Input Support

Every HUD interaction should support all available input methods.

Examples include:

Keyboard and Mouse

- Clicking
- Hover tooltips
- Drag interactions
- Scroll wheel

Controller

- Focus navigation
- Shoulder button shortcuts
- Radial selection
- Button prompts

Touch

- Tap
- Double tap
- Hold
- Pinch
- Swipe

Interaction methods may differ, but available functionality should remain consistent.

---

# Animation

HUD animations should enhance clarity without becoming distracting.

Examples include:

- Health changes
- Notification appearance
- Objective updates
- Portrait selection
- Interface transitions

Animations should prioritize responsiveness over visual complexity.

---

# Performance

HUD rendering should remain lightweight.

The interface should avoid unnecessary updates.

Examples include:

- Only refresh changing values.
- Cache static elements.
- Reduce animation workload when appropriate.
- Minimize redraw frequency.

HUD responsiveness should never negatively impact gameplay performance.

---

# Error Handling

When HUD information becomes temporarily unavailable, the interface should fail gracefully.

Examples include:

- Missing portrait
- Missing icon
- Delayed AI response
- Network interruption (multiplayer support)
- Corrupted media preview

Players should receive understandable fallback behavior rather than broken interface elements.

---

# Accessibility Integration

The HUD should integrate seamlessly with the Accessibility system.

Examples include:

- Adjustable text size
- High contrast mode
- Colorblind support
- Subtitle compatibility
- Screen reader labels
- Reduced motion
- Custom notification timing
- HUD scaling

Accessibility options should remain available without redesigning the interface.

---

# HUD Visibility Rules

The player should decide how much information remains visible.

Examples include:

Always Visible

Auto Hide

Combat Only

Minimal Mode

Fully Custom

These options allow players to tailor the experience to their preferences.

---

# Minimal Mode

Minimal Mode provides only the most essential gameplay information.

Typical elements include:

- Character portrait
- Health
- Primary resource
- Objective
- Critical notifications

All other HUD elements remain accessible through interaction.

This mode prioritizes immersion while preserving usability.

---

# Expanded Mode

Expanded Mode displays additional gameplay summaries simultaneously.

Examples include:

- Complete party overview
- Resource details
- Current weather
- Time
- Quest summary
- Mini-map overlays
- Recent notifications

Expanded Mode benefits players who prefer maximum information visibility.

---

# HUD Persistence

HUD customization should persist across play sessions.

Player preferences should be stored as part of user settings rather than campaign data whenever appropriate.

Examples include:

- Scale
- Opacity
- Element positions (if supported)
- Visibility preferences
- Accessibility settings

---

# Developer Responsibilities

Developers implementing HUD features should ensure that:

- Navigation remains consistent.
- Information remains accurate.
- Layouts remain responsive.
- Performance remains efficient.
- Accessibility standards are maintained.
- Presentation remains separate from gameplay logic.
- New HUD elements integrate with existing navigation patterns.

HUD additions should enhance clarity rather than increase complexity.

---

# Interaction With Other Systems

The HUD summarizes information owned by nearly every major engine system.

Examples include:

Application

- User settings
- Save information

Characters

- Portraits
- Player status
- Companion summaries

Combat

- Health
- Resources
- Status effects
- Combat indicators

World

- Time
- Weather
- Region
- Exploration

Systems

- Inventory summaries
- Reputation updates
- Quest tracking

AI

- Story updates
- Generated narration
- Dynamic events

Media Gallery

- Recent generated content
- Story illustrations
- Cinematic previews

Campaign Hub

- Session summaries
- Chapter progress
- Current campaign state

The HUD presents information without owning the systems that produce it.

---

# Future Extensibility

Future HUD components should integrate without requiring redesign of existing navigation.

Possible additions include:

- Guild management
- Mount status
- Pet companions
- Multiplayer overlays
- Territory control
- Seasonal events
- Community features

Future interfaces should continue following the navigation principles established within this document.

---

# Design Philosophy

The HUD is more than a collection of bars and icons.

It is the player's constant companion throughout every adventure.

Rather than functioning as a traditional game overlay, the HUD serves as the primary gateway into every major interface while remaining respectful of the player's immersion.

Every persistent element should answer one simple question:

"What useful information does this provide right now?"

If an element cannot answer that question, it should not permanently occupy screen space.

The HUD should guide players naturally through the world without requiring them to think about the interface itself.

---

# Summary

The HUD serves as the central navigation and information layer of The Shattered Realms.

It presents essential gameplay information, provides intuitive access to major interfaces, adapts to changing gameplay contexts, and supports extensive customization while maintaining clarity and immersion.

By separating presentation from gameplay logic, emphasizing contextual information, and using persistent interface anchors such as the character portrait, companion portraits, mini-map, and objective tracker, the HUD creates a cohesive player experience that allows navigation to feel immediate, natural, and unobtrusive throughout every campaign.

