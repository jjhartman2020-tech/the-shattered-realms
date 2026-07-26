# Player Interface

## Purpose

The Player Interface serves as the primary location for viewing and interacting with the player's character.

It provides a centralized, organized presentation of character information while allowing quick access to progression, equipment, appearance, relationships, achievements, and other personal information.

The interface focuses on presentation and navigation rather than gameplay mechanics.

---

# Scope

This document defines:

- Interface layout
- Navigation
- Character presentation
- Information grouping
- Interface interactions
- Customization
- Accessibility

This document does not define:

- Character progression
- Statistics
- Equipment mechanics
- Ability functionality
- Combat calculations

Those systems remain documented within their respective folders.

---

# Player Interface Philosophy

The Player Interface should feel like opening a personal journal rather than navigating a spreadsheet.

Players should immediately recognize that this screen belongs to their character.

The interface should encourage exploration while remaining easy to understand.

---

# Opening the Interface

The Player Interface is primarily opened through the Character Portrait located on the HUD.

Example navigation:

Character Portrait

↓

Player Interface

Additional access methods may include:

- Pause Menu
- Keyboard shortcut
- Controller shortcut
- Accessibility shortcut

Regardless of how the interface is opened, navigation should remain consistent.

---

# Primary Responsibilities

The Player Interface is responsible for presenting:

- Character identity
- Equipment overview
- Character statistics
- Progression summary
- Appearance
- Reputation
- Relationships
- Achievements
- Personal records
- Biography

The interface summarizes information while linking to systems that own the underlying mechanics.

---

# Interface Layout

The Player Interface is divided into multiple regions.

Typical layout:

Header

Character Overview

Navigation Tabs

Main Content

Context Panel

Footer

Each region serves a specific purpose while maintaining visual consistency.

---

# Header

The header immediately establishes character identity.

Typical information includes:

- Character portrait
- Character name
- Current title
- Level
- Class
- Origin
- Current location (optional)

The header should remain visible while navigating the interface.

---

# Character Portrait

The Player Interface expands the HUD portrait into a larger presentation.

The portrait should display the player's current appearance.

Possible updates include:

- Armor
- Clothing
- Hairstyles
- Facial features
- Permanent scars
- Cosmetic choices
- Helmet visibility

The portrait reflects the player's current in-game appearance.

---

# Character Identity

The interface presents concise identity information.

Examples include:

Name

Title

Race (if applicable)

Class

Origin

Alignment (if applicable)

Current Level

Current Campaign

Identity information should remain grouped together.

---

# Navigation Tabs

Rather than displaying every category simultaneously, the Player Interface organizes information into dedicated tabs.

Example tabs include:

Overview

Equipment

Progression

Appearance

Relationships

Achievements

Statistics

Biography

Additional tabs may be introduced as future systems are added.

---

# Overview Tab

The Overview tab serves as the player's home page.

Rather than displaying every possible statistic, it summarizes the most important information.

Examples include:

Character Portrait

Current Level

Current Health

Primary Resource

Current Objective

Current Reputation

Current Companion Count

Current Gold

Recent Achievements

The Overview should provide an immediate snapshot of the character's current state.

---

# Overview Cards

Important information should be grouped into visually distinct cards.

Examples include:

Character

Progression

Equipment

Reputation

Campaign

Relationships

Statistics

Cards should summarize information while encouraging deeper exploration through other tabs.

---

# Character Summary

The Character Summary presents a concise description of the player's current status.

Examples include:

Current Title

Current Class

Current Campaign Chapter

Current Region

Current Objective

Play Time

Players should understand their current situation within seconds.

---

# Equipment Preview

The Overview provides a summarized equipment display.

Examples include:

Weapon

Armor

Accessory

Off-Hand

Quick Slots

The Overview displays only currently equipped items.

Detailed equipment management remains available within the Equipment tab.

---

# Progress Preview

Rather than presenting complete progression trees, the Overview summarizes progression.

Examples include:

Current Level

Experience Progress

Available Skill Points

Recent Unlocks

Next Milestone

Detailed progression remains documented elsewhere.

---

# Reputation Preview

The interface summarizes the player's current reputation.

Examples include:

Overall Reputation

Recent Reputation Changes

Most Influential Faction

Recent Titles

Only summary information remains visible.

Detailed reputation history belongs elsewhere.

---

# Relationship Preview

The Overview presents the player's most important relationships.

Examples include:

Closest Companion

Recent Relationship Changes

Newest Companion

Romance Status (if applicable)

Important Story Relationships

Selecting a relationship opens additional details where appropriate.

---

# Achievement Preview

Recent accomplishments should remain visible.

Examples include:

Latest Achievement

Recent Milestone

Collection Progress

Exploration Progress

Story Progress

The Overview celebrates player accomplishments without overwhelming the interface.

---

# Biography Preview

The player's biography summarizes their personal story.

Examples include:

Origin

Current Chapter

Recent Story Event

Personal Description

Character Background

The Biography provides narrative context while encouraging players to revisit their journey.

---

# Life At A Glance

The Player Interface provides an AI-generated summary describing the player's current journey.

Rather than presenting isolated statistics, this section explains the character's current place within the world using natural language.

Examples include:

Current role

Recent accomplishments

Important allies

Current objective

Major threats

Recent discoveries

Campaign chapter

The summary should update dynamically as the story evolves.

---

# Dynamic Character Summary

The summary should reflect meaningful changes throughout the campaign.

Examples include:

A new title earned

A companion joins

A kingdom falls

A major villain is defeated

An important relationship changes

A new region is discovered

A world-changing event occurs

Minor events should not constantly rewrite the summary.

---

# Character Milestones

Major milestones should be highlighted within the interface.

Examples include:

First Companion Recruited

First Boss Defeated

Kingdom Saved

Legendary Weapon Obtained

Highest Reputation Earned

Campaign Completed

Milestones create a visual timeline of the player's journey.

---

# Appearance Tab

The Appearance tab presents the player's current visual appearance.

Examples include:

Portrait

Full Character Preview

Armor

Clothing

Hair

Facial Hair

Eye Color

Accessories

Scars

Cosmetics

The Appearance tab reflects the player's current in-game appearance.

---

# Character Preview

The interface should display a large character model or artwork when available.

Players should be able to:

Rotate

Zoom

Inspect Equipment

Hide Helmet

Preview Cosmetics

The preview remains presentation only.

Equipment mechanics remain documented elsewhere.

---

# Cosmetic Collection

Unlocked cosmetic options should be organized into categories.

Examples include:

Hairstyles

Armor Skins

Portrait Frames

Titles

Companion Cosmetics

Special Event Rewards

Unavailable cosmetics should remain clearly distinguished from unlocked items.

---

# Biography Tab

The Biography tab tells the story of the player's character.

Unlike statistics, this tab emphasizes narrative.

Examples include:

Origin Story

Current Chapter

Recent Events

Personal Notes

Important Decisions

Legacy

Biography information should evolve naturally throughout the campaign.

---

# Story Timeline

The interface maintains a timeline of significant events.

Examples include:

Campaign Started

Joined the Ravens

Defeated the Storm Warden

Entered the Ashlands

Forged Nightwhisper

Met the Queen

Each event should include:

Date

Location

Short Description

Optional Illustration

The timeline allows players to revisit their journey.

---

# Personal Journal

Players may optionally create their own journal entries.

Examples include:

Travel Notes

Battle Strategies

Favorite NPCs

Roleplaying Notes

Future Goals

Journal entries belong to the player and are never modified automatically.

---

# Titles

The interface presents earned titles.

Examples include:

The Ashborn

Slayer of Kings

Guardian of Ironhold

Raven Commander

Titles should display:

Description

How Earned

Date Earned

Current Status

Players may select which earned title is displayed publicly.

---

# Statistics Tab

The Statistics tab focuses on lifetime accomplishments rather than combat mechanics.

Examples include:

Hours Played

Enemies Defeated

Bosses Defeated

Distance Traveled

Locations Discovered

Gold Earned

Items Crafted

Quests Completed

Dialogue Choices Made

Companions Recruited

Statistics celebrate the player's overall journey.

---

# Exploration Statistics

Examples include:

Regions Visited

Cities Visited

Dungeons Cleared

Secrets Found

Fast Travel Locations

Books Read

Lore Entries Collected

These values encourage exploration without affecting gameplay.

---

# Combat Statistics

Examples include:

Victories

Defeats

Critical Hits

Damage Dealt

Damage Taken

Healing Received

Abilities Used

Favorite Weapon

Statistics remain informational only.

---

# AI Insights

The Player Interface may generate optional observations about the player's playstyle.

Examples include:

"You often solve problems through diplomacy."

"You prefer stealth over direct combat."

"You frequently protect companions before yourself."

"You enjoy exploring optional locations."

These insights should remain descriptive rather than judgmental.

---

# Favorite Moments

Players may bookmark important memories.

Examples include:

Favorite Battle

Favorite Companion Moment

Favorite Landscape

Favorite Dialogue

Favorite Image

Favorite Cutscene

Bookmarked moments remain accessible through both the Player Interface and the Media Gallery.

---

# Personal Collections

The Player Interface summarizes collectible progress.

Examples include:

Achievements

Books

Artifacts

Weapons

Armor Sets

Portrait Frames

Music Tracks

Detailed collections remain documented by their owning systems.

---

# Search

The Player Interface includes search functionality for large collections.

Examples include:

Achievements

Titles

Statistics

Biography Entries

Journal Notes

Search results should update immediately while typing.

---

# Filters

Players should be able to filter information.

Examples include:

Newest

Oldest

Story

Combat

Exploration

Completed

Favorites

Filtering improves navigation without changing stored information.

---

# Favorites

Players may mark information as favorites.

Examples include:

Equipment

Titles

Achievements

Journal Entries

Biography Events

Favorite items should remain easily accessible throughout the interface.

---

# Relationships Tab

The Relationships tab provides a centralized overview of the player's connections throughout the world.

Rather than defining relationship mechanics, this tab presents relationship information in an organized and meaningful way.

---

# Relationship Overview

The interface summarizes important relationships.

Examples include:

- Closest Companion
- Most Trusted Ally
- Greatest Rival
- Current Mentor
- Romance Partner (if applicable)
- Most Influential NPC

This section provides an immediate understanding of the player's social standing.

---

# Relationship Categories

Relationships should be organized into clear categories.

Examples include:

- Companions
- Allies
- Neutral Characters
- Rivals
- Enemies
- Important Story Characters
- Factions

Categories improve navigation as the campaign grows.

---

# Character Profiles

Selecting a relationship opens a profile page.

Examples of displayed information include:

- Portrait
- Name
- Role
- Current Status
- Relationship Summary
- Recent Interactions
- Current Location (when appropriate)
- Story Importance

This profile serves as a quick reference rather than a complete encyclopedia.

---

# Relationship Timeline

Important interactions should appear in chronological order.

Examples include:

- First Meeting
- Joined the Party
- Betrayed the Player
- Relationship Improved
- Story Event
- Final Encounter

Players should be able to revisit important moments throughout the campaign.

---

# AI Relationship Summary

The interface may generate a concise summary describing each important relationship.

Examples:

"Nyra has become your most trusted companion after countless battles."

"Garrick respects your leadership but often questions unnecessary risks."

"The Ash King views you as his greatest threat."

Summaries should evolve naturally as relationships change.

---

# Records Tab

The Records tab celebrates long-term accomplishments throughout the campaign.

Unlike achievements, records focus on personal bests and lifetime milestones.

Examples include:

- Highest Level Reached
- Largest Gold Total
- Most Damage Dealt
- Longest Survival Streak
- Most Companions Recruited
- Largest Inventory
- Fastest Dungeon Clear

Records provide long-term goals without affecting gameplay balance.

---

# Campaign Statistics

Campaign-specific information may include:

- Current Campaign Length
- Story Completion
- Chapters Finished
- Main Quests Completed
- Side Quests Completed
- Decisions Made
- Alternate Endings Unlocked

Campaign statistics help players understand their overall progress.

---

# Collection Progress

Collection summaries provide an overview of collectible completion.

Examples include:

- Weapons
- Armor Sets
- Books
- Artifacts
- Music
- Portrait Frames
- Lore Entries

Each category displays completion progress without overwhelming the interface.

---

# Search and Navigation

Large collections should remain easy to navigate.

Navigation tools may include:

- Search
- Sort
- Filters
- Categories
- Favorites
- Recently Viewed

Navigation tools should remain consistent across every tab.

---

# Comparison Mode

Certain information may be compared directly.

Examples include:

- Current Equipment vs Previous Equipment
- Reputation Changes
- Character Appearance Before and After
- Statistics Across Campaign Chapters

Comparison mode should emphasize meaningful changes rather than raw numbers.

---

# Session Summary

The Player Interface presents a summary of the current play session.

Examples include:

- Time Played
- Quests Completed
- New Discoveries
- Battles Won
- New Relationships
- Items Collected

Session summaries help players quickly remember recent accomplishments.

---

# Recent Activity

The interface maintains a chronological list of recent character activity.

Examples include:

- Equipped New Weapon
- Learned New Ability
- Completed Quest
- Entered New Region
- Reputation Increased
- Companion Joined

This section acts as a quick history of the player's recent actions.

---

# Character Notes

Players may create personal notes attached specifically to their character.

Examples include:

- Build Ideas
- Future Goals
- Roleplaying Details
- Character Personality
- Important Reminders

These notes remain entirely player-controlled.

---

# Interface Shortcuts

The Player Interface provides direct navigation to related interfaces.

Examples include:

Equipment

↓

Inventory Interface

Current Quest

↓

Quest Journal

Favorite Companion

↓

Party Interface

Recent Image

↓

Media Gallery

Campaign Summary

↓

Campaign Hub

Navigation should minimize unnecessary menu transitions.

---

# Portrait Interaction

The enlarged character portrait supports additional interaction.

Possible actions include:

- Rotate Character
- Zoom
- Toggle Helmet
- Change Pose
- Preview Cosmetic Rewards
- Capture Screenshot

These interactions remain optional and do not affect gameplay.

---

# Recent Unlocks

The interface highlights newly unlocked content.

Examples include:

- Titles
- Cosmetics
- Achievements
- Portrait Frames
- Journal Entries

Recently unlocked items should remain easy to identify until viewed.

---

# Story Progress

The interface summarizes overall narrative progression.

Examples include:

Current Chapter

Current Objective

Major Story Arc

Last Story Event

Next Recommended Goal

Detailed quest information remains within the Quest Journal.

---

# Interface Feedback

Every interaction should provide clear visual feedback.

Examples include:

- Hover Highlights
- Selection Borders
- Button Animations
- Smooth Tab Transitions
- Loading Indicators
- Confirmation Messages

Feedback improves usability while maintaining immersion.

---

# Empty States

When a section contains no information, the interface should present a meaningful placeholder.

Examples include:

"No companions recruited yet."

"No journal entries created."

"No titles earned."

"No favorite memories saved."

Empty states should encourage exploration without feeling unfinished.

---

# Responsive Layout

The Player Interface should adapt to different display sizes.

Large displays may present multiple panels simultaneously.

Smaller displays should reorganize content into stacked layouts while preserving navigation consistency.

Platform adaptation should prioritize readability above layout symmetry.

# Customization

Players should be able to customize the presentation of the Player Interface without affecting gameplay.

Customization options may include:

- Default tab
- Portrait size
- Interface scale
- Card layout
- Compact mode
- Expanded mode
- Animation intensity
- Background theme
- Sidebar position

Customization should improve comfort while preserving interface consistency.

---

# Theme Support

The Player Interface should support multiple visual themes.

Examples include:

- Default
- Dark
- High Contrast
- Minimal
- Accessibility Themes
- Seasonal Themes (optional)

Themes should only affect presentation.

---

# Layout Preferences

Players may choose how information is organized.

Examples include:

Single Column

Dual Column

Card View

List View

Compact Summary

Expanded Detail

The underlying information should remain identical regardless of layout.

---

# Accessibility Integration

The Player Interface should fully support the Accessibility system.

Examples include:

- Adjustable text size
- Screen reader compatibility
- Colorblind support
- High contrast mode
- Reduced motion
- Keyboard-only navigation
- Controller-only navigation
- Touch optimization
- Custom UI scaling

Accessibility should be considered during initial design rather than added later.

---

# Input Consistency

Navigation should remain predictable across every supported input method.

Supported inputs include:

Keyboard and Mouse

Controller

Touch

Regardless of platform, players should always know how to:

- Move between tabs
- Select information
- Return to previous pages
- Open related interfaces
- Search
- Filter
- Favorite content

Consistency reduces the learning curve for every player.

---

# Animation Principles

Animations should communicate state changes rather than serve as decoration.

Examples include:

- Opening the interface
- Switching tabs
- Updating portraits
- Expanding cards
- Unlocking achievements
- New relationship events

Animations should remain smooth, responsive, and optional when accessibility settings require reduced motion.

---

# Performance

The Player Interface should remain responsive regardless of campaign size.

Implementation should prioritize:

- Efficient loading
- Lazy loading of large collections
- Cached portraits
- Cached summaries
- Incremental updates
- Efficient search indexing

Large campaigns should never noticeably reduce interface responsiveness.

---

# Offline Availability

Information stored within the save file should remain fully accessible while offline.

AI-generated summaries should be cached whenever possible to prevent unnecessary regeneration.

Unavailable online services should never prevent players from viewing existing character information.

---

# Save Integration

The Player Interface should accurately reflect the current campaign state.

Information displayed should always remain synchronized with:

- Save files
- Campaign progression
- Character appearance
- Equipment
- Reputation
- Relationships
- Statistics

The interface should never become the authoritative source of this information.

---

# Error Handling

When information cannot be displayed, the interface should provide graceful fallback behavior.

Examples include:

- Missing portrait artwork
- Unavailable cosmetic preview
- Corrupted journal entry
- Missing achievement icon
- Delayed AI summary

Fallback behavior should prioritize usability over visual completeness.

---

# Privacy

Player-created content should remain under the player's control.

Examples include:

- Personal journal entries
- Notes
- Favorites
- Custom organization
- Cosmetic preferences

The interface should clearly distinguish between player-created information and system-generated information.

---

# Interface Ownership

The Player Interface presents information owned by many engine systems.

Examples include:

Character

- Identity
- Appearance
- Statistics

Equipment

- Equipped items
- Appearance preview

Progression

- Level
- Experience
- Unlock summaries

Reputation

- Reputation summaries

Companions

- Relationship previews

World

- Current location
- Story chapter

Campaign

- Session summaries
- Timeline

Media Gallery

- Favorite images
- Story illustrations

The Player Interface owns presentation—not the mechanics behind the information.

---

# Interaction With Other Interfaces

The Player Interface serves as a navigation hub connecting multiple interfaces.

Examples include:

Equipment Preview

↓

Inventory Interface

Relationship

↓

Party Interface

Story Progress

↓

Quest Journal

Campaign Summary

↓

Campaign Hub

Favorite Image

↓

Media Gallery

Current Region

↓

Map Interface

Navigation should remain intuitive and require as few interactions as possible.

---

# Future Extensibility

Future systems should integrate naturally into the Player Interface.

Potential additions include:

- Mounts
- Pets
- Guild Membership
- Housing
- Family Trees
- Seasonal Progress
- Player Collections
- Legendary Deeds
- Community Features

New features should integrate through existing navigation patterns whenever possible.

---

# Design Philosophy

The Player Interface is more than a character sheet.

It is the player's personal history, identity, and legacy within The Shattered Realms.

Rather than overwhelming players with isolated numbers, the interface presents information in meaningful groups that tell the story of who the character has become.

Every section should answer one of three questions:

"Who am I?"

"What have I accomplished?"

"Where do I go next?"

If a piece of information does not help answer one of those questions, it should be reconsidered before becoming part of the interface.

The Player Interface should feel less like opening a spreadsheet and more like opening a living chronicle that grows alongside every adventure.

---

# Summary

The Player Interface is the primary destination for understanding the player's character.

It presents identity, appearance, progression, relationships, achievements, statistics, biography, and campaign history through an organized, immersive, and accessible interface.

By separating presentation from gameplay mechanics, emphasizing AI-assisted storytelling, and maintaining consistent navigation throughout the user experience, the Player Interface becomes more than a menu—it becomes the evolving record of the player's journey through The Shattered Realms.
