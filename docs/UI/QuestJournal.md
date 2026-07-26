# Quest Journal

## Purpose

The Quest Journal provides a centralized interface for viewing, organizing, and understanding the player's adventures.

Rather than defining quest mechanics, progression rules, or objective logic, the journal presents quest information in a structured, narrative-focused format.

The Quest Journal serves as both a gameplay tool and a historical record of the player's journey.

---

# Scope

This document defines:

- Quest presentation
- Journal organization
- Objective visualization
- Quest navigation
- Story summaries
- Search
- Filters
- Accessibility
- Customization

This document does not define:

- Quest mechanics
- Objective logic
- Rewards
- Reputation changes
- Dialogue systems
- Branching story implementation

Those systems remain documented within their respective folders.

---

# Journal Philosophy

The Quest Journal should feel like reading the chronicle of an adventure rather than checking tasks off a list.

Players should understand not only what they are doing, but why they are doing it.

Every completed quest should become part of the player's permanent story.

---

# Opening the Interface

The Quest Journal is primarily opened through:

- Objective Tracker (HUD)
- Map Interface
- Player Interface
- Pause Menu
- Keyboard Shortcut
- Controller Shortcut

Navigation should remain consistent regardless of entry point.

---

# Primary Responsibilities

The Quest Journal presents:

- Active quests
- Completed quests
- Failed quests
- Objectives
- Story summaries
- Companion quests
- Decision history
- Quest relationships
- Campaign journal
- Search
- Filters

The journal presents information without owning quest mechanics.

---

# Interface Layout

The Quest Journal is divided into several persistent regions.

Typical layout:

Header

Quest Categories

Quest List

Quest Details

Objective Panel

Footer

Each region serves a distinct purpose.

---

# Header

The header summarizes the player's current progress.

Examples include:

- Active Quests
- Completed Quests
- Current Chapter
- Campaign Name
- Recent Quest
- Total Objectives Completed

The header remains visible while navigating the journal.

---

# Quest Categories

Quests should be organized into clear categories.

Examples include:

- Main Story
- Side Quests
- Companion Quests
- Guild Quests
- Faction Quests
- World Events
- Exploration
- Contracts
- Completed
- Failed

Categories improve navigation while keeping the journal organized.

---

# Quest List

The Quest List presents quests within the selected category.

Each quest should appear as a summary card.

Cards remain visually consistent throughout the interface.

---

# Quest Card

Each quest card summarizes essential information.

Examples include:

Quest Name

Current Chapter

Quest Type

Current Status

Recommended Region

Companion Involvement

Last Updated

Cards should communicate progression without requiring players to open every quest.

---

# Quest Status

Every quest should clearly communicate its current state.

Examples include:

Active

Tracked

Paused

Completed

Failed

Unavailable

Hidden

Status presentation should remain concise and immediately recognizable.

---

# Quest Selection

Selecting a quest expands additional information.

Expanded information may include:

Story Summary

Current Objectives

Important Characters

Recent Events

Related Locations

Companion Involvement

Decision History

The quest list should remain visible while viewing quest details.

---

# Quest Overview

The overview provides a concise summary of the selected quest.

Examples include:

Quest Title

Current Chapter

Quest Giver

Current Region

Recommended Destination

Story Importance

Estimated Progress

The overview helps players immediately understand the quest's role within the campaign.

---

# AI Story Summary

Each quest includes an AI-generated narrative summary.

Rather than repeating objective text, the summary explains the current story.

Examples include:

"Captain Rowan believes the ancient watchtower may contain evidence linking the Ash Cult to Project Ashfall. Nyra recommends investigating before the cult returns."

"The Queen has asked you to negotiate peace between two rival houses. Your earlier decision to spare Lord Harren may influence the outcome."

Summaries should evolve naturally as quests progress.

---

# Objective Panel

The Objective Panel presents the player's current objectives.

Objectives should remain concise while preserving context.

Examples include:

Speak with Captain Rowan.

Investigate the Southern Watchtower.

Search the Library Archives.

Return to Ironhold.

Objectives explain immediate goals.

The story remains within the quest summary.

# Objective Timeline

The Objective Timeline presents the progression of a quest in chronological order.

Rather than displaying only the current objective, the timeline shows how the quest has evolved.

Examples include:

Quest Accepted

First Lead Discovered

Important Decision

Objective Updated

Companion Joined

Quest Completed

Timeline entries should reinforce narrative continuity.

---

# Current Objectives

Current objectives should remain visually distinct from completed objectives.

Each objective should display:

- Current Status
- Objective Summary
- Last Updated
- Related Region (when applicable)

Objectives should communicate immediate goals without overwhelming the player.

---

# Completed Objectives

Completed objectives remain visible throughout the quest.

Completed entries should be visually distinguished while remaining readable.

Players should always understand what has already been accomplished.

---

# Failed Objectives

Failed objectives should remain part of the permanent quest history.

Examples include:

Failed Negotiation

Unable to Save Villagers

Lost Important Evidence

Companion Declined Request

Failed objectives preserve narrative continuity rather than punishing the player.

---

# Decision History

The journal summarizes important decisions made throughout the quest.

Examples include:

Spared the Prisoner

Executed the Cult Leader

Accepted the Bribe

Refused the King's Request

Destroyed the Artifact

Decision history should remain chronological.

---

# Consequence Summary

The journal may summarize known consequences resulting from player decisions.

Examples include:

Village Trust Increased

Guild Reputation Decreased

Companion Approved

Faction Became Hostile

Trade Route Reopened

Only known consequences should be displayed.

Unknown future consequences should remain hidden.

---

# Companion Involvement

The journal summarizes companion participation within each quest.

Examples include:

Present During Quest

Personal Dialogue

Relationship Event

Personal Quest Connection

Special Recommendation

Companion involvement reinforces party participation throughout the story.

---

# Important Characters

Each quest should summarize key characters involved.

Examples include:

Quest Giver

Primary Ally

Primary Antagonist

Important Witness

Merchant

Faction Leader

Selecting a character opens the appropriate interface.

---

# Related Locations

The journal summarizes significant locations connected to the quest.

Examples include:

Current Destination

Important Settlement

Dungeon

Landmark

Region

Selecting a location opens the Map Interface.

---

# Quest Connections

Related quests should remain clearly identified.

Examples include:

Prerequisite Quest

Follow-Up Quest

Companion Quest

Faction Quest

Shared Story Arc

Quest connections help players understand larger narrative structures.

---

# Story Arc

Each quest belongs to a broader story arc whenever applicable.

Examples include:

Ashfall Investigation

Civil War

The Seven Seals

The Raven Company

Kingdom Restoration

Viewing the story arc should summarize connected quests without revealing undiscovered content.

---

# Journal Recap

Every quest includes an AI-generated recap.

Unlike the story summary, the recap focuses on recent developments.

Examples include:

"After speaking with the Queen, you discovered that the southern fortress has already fallen. Nyra recommends investigating before the trail grows cold."

"The negotiation ended peacefully, but Garrick remains suspicious of the treaty."

Recaps should help players immediately resume long campaigns.

---

# Last Session Reminder

When returning after an extended absence, the journal may provide a brief reminder.

Examples include:

Last Quest Worked On

Last Objective Completed

Last Region Visited

Last Companion Conversation

Recommended Next Step

The reminder should reduce the friction of returning to the game.

---

# AI Recommended Next Step

The journal may generate a suggested next action.

Examples include:

Speak with Captain Rowan.

Return to Ironhold.

Investigate the Northern Ruins.

Meet Nyra at the Watchtower.

Recommendations remain optional and never force player behavior.

---

# Related Lore

The journal summarizes discovered lore connected to the quest.

Examples include:

Historical Event

Ancient Kingdom

Legend

Artifact

Faction History

Selecting an entry opens the appropriate lore interface when available.

---

# Rewards Preview

The interface may summarize known quest rewards.

Examples include:

Equipment

Titles

Companion

Settlement Access

Faction Trust

Unknown Reward

Reward mechanics remain documented elsewhere.

---

# Attachments

Quest entries may contain associated content.

Examples include:

Letters

Maps

Books

Drawings

Evidence

Photographs

Selecting an attachment opens the appropriate viewer.

---

# Quest Notes

Players may create personal notes for each quest.

Examples include:

Puzzle Ideas

Suspect List

Roleplaying Notes

Future Plans

Reminder

Player-created notes remain separate from system-generated content.

---

# Bookmarks

Players may bookmark important quests.

Bookmarked quests should appear:

- First in lists
- First in search results
- First within quick navigation

Bookmarks affect organization only.

---

# Search

The Quest Journal includes comprehensive search functionality.

Players may search by:

Quest Name

Character

Location

Faction

Story Arc

Companion

Objective

Decision

Results should update dynamically while typing.

---

# Filters

Players may filter quests using multiple criteria.

Examples include:

Active

Completed

Failed

Main Story

Side Quest

Companion

Faction

Recently Updated

Bookmarked

Filters affect presentation only.

---

# Favorites

Players may mark quests as favorites.

Favorite quests should remain easily accessible throughout the interface.

Favorites should not affect gameplay progression.

# Campaign Journal

Beyond individual quests, the Quest Journal maintains a continuous record of the player's overall adventure.

The Campaign Journal connects major events into a single chronological history.

Unlike individual quest logs, the Campaign Journal focuses on the broader story.

---

# Campaign Timeline

Major campaign events should appear chronologically.

Examples include:

Campaign Began

First Companion Recruited

First Kingdom Visited

Major Boss Defeated

Chapter Completed

Legendary Artifact Found

Campaign Finale

Timeline entries should celebrate the player's journey rather than overwhelm them with detail.

---

# Chapter Summaries

Each completed story chapter should receive its own summary.

Examples include:

Chapter Title

Primary Conflict

Major Decisions

Important Characters

Regions Visited

Key Outcomes

These summaries help players remember long campaigns.

---

# Story Recaps

The journal may generate AI-written summaries of completed chapters.

Examples include:

"The defense of Ironhold marked a turning point in the campaign. Although the city survived, your decision to spare Lord Harren created growing political tension that continues to influence neighboring kingdoms."

Story recaps should emphasize narrative rather than objective completion.

---

# Decision Timeline

Important campaign decisions should remain visible throughout the journal.

Examples include:

Joined the Ravens

Refused the King's Offer

Destroyed the Ash Relic

Forged an Alliance

Executed the Traitor

Decision entries should include:

Date

Campaign Chapter

Immediate Outcome

Known Consequences

Future consequences should remain hidden until discovered.

---

# Companion Chronicle

The journal summarizes important moments shared with companions.

Examples include:

First Meeting

Joined the Party

Relationship Improved

Personal Quest Completed

Important Sacrifice

Farewell

The chronicle celebrates companion stories throughout the campaign.

---

# Kingdom Chronicle

Major events affecting kingdoms should appear separately.

Examples include:

Capital Liberated

Civil War Began

Trade Restored

New Ruler Crowned

City Destroyed

These entries help players understand how the world has changed.

---

# World Event Chronicle

The journal records major world events witnessed by the player.

Examples include:

Solar Eclipse

Ash Storm

Dragon Migration

Ancient Gate Opened

Festival

The chronicle should only include events the player has experienced or learned about.

---

# Quest Completion Gallery

Completed quests may display commemorative artwork when available.

Examples include:

Victory Illustration

Generated Landscape

Important Character Portrait

Quest Finale Scene

Selecting artwork opens the Media Gallery.

---

# Personal Journey

The Quest Journal gradually becomes a personalized record of the player's adventure.

The journey combines:

Completed Quests

Major Decisions

Relationships

Discoveries

World Events

Campaign Chapters

Story Summaries

Every campaign should produce a unique history.

---

# AI Campaign Summary

The interface generates an evolving overview of the player's adventure.

Examples include:

"You have become one of the kingdom's most influential leaders, forging fragile alliances while confronting the growing threat of the Ash Cult."

"Your decisions have strengthened your companions' loyalty, though tensions continue to rise among the northern kingdoms."

The summary should update naturally throughout the campaign.

---

# Character Involvement

Each quest should summarize important participating characters.

Examples include:

Primary Companion

Supporting Companion

Quest Giver

Primary Antagonist

Neutral Participants

Selecting a character opens the appropriate interface.

---

# Faction Involvement

The journal summarizes participating factions.

Examples include:

Kingdom Army

Merchant Guild

Ash Cult

Northern Alliance

The Ravens

Faction summaries help players understand broader political context.

---

# Quest Dependencies

The journal visually displays relationships between connected quests.

Examples include:

Required Quest

Optional Follow-Up

Alternative Outcome

Companion Branch

Faction Branch

Dependency visualization should improve understanding without revealing hidden content.

---

# Missed Opportunities

The journal may summarize permanently unavailable content.

Examples include:

Failed Recruitment

Missed Dialogue

Destroyed Settlement

Lost Reward

Unavailable Questline

These entries should explain that an opportunity has passed without encouraging replay.

---

# Replay Notes

Completed quests may include optional replay information.

Examples include:

Alternative Outcomes Exist

Different Companion Dialogue Available

Faction-Specific Variations

Additional Secrets Discovered

Replay information should avoid major spoilers.

---

# Journal Collections

The Quest Journal organizes quest-related collectibles.

Examples include:

Letters

Evidence

Maps

Books

Artifacts

Contracts

Collections remain searchable.

---

# Journal Attachments

Quest entries may reference additional supporting material.

Examples include:

Signed Contracts

Ancient Scrolls

Evidence Files

Drawings

Photographs

Voice Recordings

Selecting an attachment opens the appropriate viewer.

---

# Recent Updates

Recently updated quests should receive temporary emphasis.

Examples include:

Objective Changed

Companion Joined

Quest Advanced

Decision Recorded

Story Updated

The emphasis should disappear once viewed.

---

# Navigation History

The journal maintains recently viewed entries.

Examples include:

Recent Quest

Recent Chapter

Recent Character

Recent Story Arc

Recent Search

History improves navigation during long campaigns.

---

# Split View

Players may compare two quest entries simultaneously.

Possible comparisons include:

Main Story vs Companion Quest

Completed vs Active Quest

Alternative Story Arcs

Two Campaign Chapters

Split View improves organization while remaining optional.

---

# Context Actions

Different quest types may provide different contextual actions.

Examples include:

Quest

- Track
- Favorite
- Add Note
- View Map

Companion Quest

- View Companion
- Open Relationship

Location

- Open Map
- View Settlement

Context actions reduce unnecessary navigation.

---

# Progress Overview

The journal summarizes campaign-wide quest progress.

Examples include:

Main Story Progress

Side Quest Completion

Companion Quest Completion

Faction Progress

Exploration Objectives

Contract Completion

Progress summaries remain informational only.

---

# Empty States

When no information exists within a section, the interface should display meaningful guidance.

Examples include:

"No completed companion quests yet."

"No campaign chapters completed."

"No bookmarked quests."

"No recent journal updates."

Empty states should encourage continued exploration rather than appear unfinished.

# Customization

Players should be able to customize the presentation of the Quest Journal without affecting gameplay.

Customization options may include:

- Default category
- Card size
- Timeline visibility
- Story summary length
- Objective density
- Chapter grouping
- Animation intensity
- Compact mode
- Expanded mode

Customization should improve readability while preserving consistency.

---

# Theme Support

The Quest Journal should support all application-wide themes.

Examples include:

- Default
- Dark
- High Contrast
- Minimal
- Accessibility Themes
- Seasonal Themes (optional)

Themes affect presentation only.

---

# Layout Preferences

Players may organize journal information using multiple layouts.

Examples include:

List View

Card View

Timeline View

Chronicle View

Compact View

Expanded View

Changing layouts should never alter stored information.

---

# Accessibility Integration

The Quest Journal should fully integrate with the Accessibility system.

Examples include:

- Adjustable text size
- High contrast mode
- Colorblind support
- Screen reader compatibility
- Keyboard-only navigation
- Controller navigation
- Touch optimization
- Reduced motion
- Adjustable interface scaling

Accessibility should be incorporated from the beginning of interface design.

---

# Input Consistency

Navigation should remain intuitive across every supported platform.

Supported inputs include:

Keyboard and Mouse

Controller

Touch

Players should always understand how to:

- Open quests
- Change categories
- Track objectives
- Search
- Filter
- Bookmark quests
- Add notes
- Return

Consistency improves usability throughout the application.

---

# Animation Principles

Animations should reinforce storytelling without interrupting navigation.

Examples include:

- Opening quests
- Timeline updates
- Objective completion
- Chapter transitions
- Story recap generation
- New journal entries

Animations should remain smooth, responsive, and optional.

---

# Performance

The Quest Journal should remain responsive regardless of campaign length.

Implementation should prioritize:

- Lazy loading completed quests
- Cached AI summaries
- Incremental timeline loading
- Efficient search indexing
- Optimized filtering
- Responsive scrolling

Very long campaigns should not reduce interface performance.

---

# Save Integration

The Quest Journal should accurately reflect the current campaign.

Displayed information should remain synchronized with:

- Quest progression
- Objectives
- Decisions
- Story chapters
- Companion involvement
- World events
- Campaign timeline

The journal should never become the authoritative source for this information.

---

# Offline Availability

Previously generated journal information should remain accessible while offline.

Examples include:

- Quest summaries
- Story recaps
- Decision history
- Chapter summaries
- Player notes
- Attachments

Unavailable online services should never prevent players from reviewing their completed adventures.

---

# Error Handling

When information cannot be displayed, the journal should fail gracefully.

Examples include:

- Missing artwork
- Delayed AI summary
- Corrupted attachment
- Missing companion portrait
- Unavailable media preview

Fallback behavior should prioritize readability and usability.

---

# Privacy

Player-created journal information should remain separate from system-generated content.

Examples include:

- Personal notes
- Bookmarks
- Favorites
- Custom organization
- Search history

The interface should clearly distinguish between player-created and AI-generated entries.

---

# Interface Ownership

The Quest Journal presents information owned by multiple engine systems.

Examples include:

Systems

- Quest summaries
- Objective summaries

Characters

- Companion involvement
- Important NPCs

Dialogue

- Conversation references
- Story events

World

- Locations
- Regions
- World events

Campaign

- Chapters
- Timeline
- Major decisions

Media Gallery

- Quest artwork
- Story illustrations
- Cinematic references

AI

- Story summaries
- Session recaps
- Campaign overviews
- Recommended next steps

The Quest Journal owns presentation only.

---

# Interaction With Other Interfaces

The Quest Journal serves as a navigation hub for story-related information.

Examples include:

Quest Location

↓

Map Interface

Companion

↓

Party Interface

Player

↓

Player Interface

Story Artwork

↓

Media Gallery

Campaign Chapter

↓

Campaign Hub

Related Character

↓

Character Profile

Navigation should minimize unnecessary transitions while maintaining context.

---

# Future Extensibility

Future systems should integrate naturally into the Quest Journal.

Potential additions include:

- Seasonal Storylines
- Community Campaigns
- Cooperative Quest Logs
- Guild Storylines
- Dynamic World Chronicles
- Legacy Campaigns
- New Game Plus Journals
- Procedural Adventure Logs
- Cross-Campaign History

Future additions should follow the organizational principles established within this document.

---

# Design Philosophy

The Quest Journal is more than an objective tracker.

It is the written history of the player's adventure.

Every completed quest, every difficult decision, every companion who joined, every kingdom that changed, and every chapter that ended should become part of a permanent chronicle unique to that campaign.

Rather than asking players to remember dozens of disconnected objectives, the journal should help them understand the larger story they are creating.

Every section should answer one of three questions:

"What am I trying to accomplish?"

"Why does it matter?"

"How has this adventure changed because of my actions?"

If a feature cannot help answer one of those questions, it should be reconsidered before becoming part of the journal.

The Quest Journal should allow players to return months or even years later and immediately reconnect with the adventure they once lived.

---

# Summary

The Quest Journal provides a comprehensive, narrative-focused interface for understanding every stage of the player's adventure.

It presents quests, objectives, story summaries, decision histories, companion involvement, campaign chapters, AI-generated recaps, and personal notes through a unified, accessible interface while leaving gameplay mechanics to their respective systems.

By emphasizing storytelling, historical continuity, and AI-assisted recollection, the Quest Journal transforms traditional quest tracking into a living chronicle that preserves each player's unique journey through The Shattered Realms.

