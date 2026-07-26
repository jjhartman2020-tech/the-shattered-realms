# Map Interface

## Purpose

The Map Interface provides players with a centralized view of the explored world.

Rather than defining exploration mechanics, travel systems, or world generation, the interface presents geographic information in a clear, interactive, and organized manner.

The Map Interface serves as the primary navigation tool for understanding the player's position within the world.

---

# Scope

This document defines:

- Map presentation
- Navigation
- Region visualization
- Marker organization
- Route previews
- Search
- Filters
- Accessibility
- Customization

This document does not define:

- Exploration mechanics
- Travel mechanics
- Fast travel rules
- Settlement generation
- World simulation
- Discovery systems

Those systems remain documented within the World folder.

---

# Map Philosophy

The map should answer one simple question:

"Where am I, and where can I go?"

Rather than overwhelming players with information, the interface should progressively reveal the world as it becomes known.

Exploration should remain rewarding.

Unknown places should remain mysterious.

The interface should encourage curiosity rather than eliminate it.

---

# Opening the Interface

The Map Interface is primarily opened by selecting the Mini-Map from the HUD.

Example navigation:

Mini-Map

↓

Map Interface

Additional access methods may include:

- Pause Menu
- Keyboard Shortcut
- Controller Shortcut
- Quest Journal
- Player Interface

Navigation should remain consistent regardless of entry point.

---

# Primary Responsibilities

The Map Interface presents:

- World map
- Regional maps
- Settlement locations
- Player position
- Party position
- Objectives
- Custom markers
- Route previews
- Search
- Filters
- Exploration progress

The interface presents information while leaving exploration mechanics to their owning systems.

---

# Interface Layout

The Map Interface is divided into several persistent regions.

Typical layout:

Header

World Map

Information Panel

Navigation Toolbar

Filter Panel

Footer

Each region serves a specific purpose.

---

# Header

The header summarizes the current map view.

Examples include:

Current Region

Current Settlement

Current World

Current Coordinates (optional)

Current Chapter

Weather

Time

The header remains visible throughout navigation.

---

# World Map

The World Map occupies the majority of the interface.

The map should prioritize readability over visual decoration.

Important information should remain easy to identify regardless of zoom level.

---

# Player Marker

The player's current position should always remain clearly visible.

The marker should communicate:

Current Position

Facing Direction

Movement (when appropriate)

Current Activity (optional)

The player marker should remain distinguishable from every other map icon.

---

# Party Marker

When companions are traveling with the player, their location should be represented alongside the player marker.

When companions are separated, the map may display their independent locations when known.

The presentation should clearly distinguish:

- Active Party
- Independent Companion
- Unknown Location

Unknown locations should never be guessed.

---

# Region Boundaries

Discovered regions should be visually separated.

Examples include:

Kingdom Borders

Mountain Ranges

Forests

Deserts

Swamps

Oceans

Political borders should remain visually distinct from natural geography.

---

# Region Information

Selecting a region opens a summary panel.

Examples include:

Region Name

Description

Ruling Faction

Discovery Progress

Settlements

Known Dungeons

Current Weather

Current Threat Level

The panel summarizes information while linking to owning systems where appropriate.

---

# Discovery Progress

The interface summarizes regional exploration.

Examples include:

Map Revealed

Landmarks Found

Settlements Visited

Secrets Discovered

Dungeons Cleared

Discovery summaries should encourage continued exploration rather than reveal undiscovered content.

---

# Zoom Levels

The Map Interface supports multiple zoom levels.

Examples include:

World

Continent

Kingdom

Region

Settlement

Local Area

Each zoom level should prioritize information appropriate to its scale.

---

# Smooth Navigation

Players should be able to:

Pan

Zoom

Rotate (optional)

Center on Player

Center on Objective

Jump to Region

Navigation should remain fluid across every supported platform.

---

# Dynamic Labels

Labels should adapt intelligently to zoom level.

Examples include:

World Names

Kingdom Names

Region Names

Settlement Names

Landmarks

Roads

Small points of interest should appear only when sufficient zoom is available.

---

# Information Panel

Selecting a map element opens a contextual information panel.

Depending on selection, the panel may summarize:

- Settlement
- Dungeon
- Landmark
- Quest Objective
- Companion
- Custom Marker
- Region

The panel provides concise information without replacing dedicated interfaces.

---

# Markers

Markers identify important locations throughout the world.

Markers should remain recognizable regardless of zoom level while avoiding unnecessary visual clutter.

Each marker should clearly communicate its purpose through consistent iconography.

---

# Marker Categories

Markers should be grouped into logical categories.

Examples include:

- Settlements
- Capitals
- Villages
- Dungeons
- Landmarks
- Quest Objectives
- Fast Travel Points
- Merchants
- Inns
- Blacksmiths
- Guilds
- Shrines
- Camps
- Player Markers
- Companion Markers
- Custom Markers

Categories improve readability and support filtering.

---

# Marker Visibility

Marker visibility should adapt based on zoom level.

Examples include:

World View

- Capitals
- Kingdoms
- Major Landmarks

Regional View

- Towns
- Roads
- Dungeons
- Quest Markers

Local View

- Shops
- Inns
- NPC Services
- Points of Interest

The interface should avoid overwhelming the player with excessive information.

---

# Marker Interaction

Selecting a marker opens a contextual summary.

Examples include:

Location Name

Description

Discovery Status

Current Services

Known NPCs

Related Quests

Recent Events

Additional actions may also become available depending on the selected location.

---

# Custom Markers

Players may place custom markers anywhere on discovered portions of the map.

Examples include:

Treasure Location

Interesting Cave

Future Objective

Boss Reminder

Roleplaying Location

Meeting Point

Custom markers remain entirely player-controlled.

---

# Custom Marker Editing

Players should be able to modify custom markers.

Supported actions include:

Rename

Change Icon

Change Color

Add Notes

Move Marker

Delete Marker

Customization should remain simple and immediate.

---

# Notes

Map markers may contain player-created notes.

Examples include:

"Locked door."

"Come back after Level 20."

"Merchant sells rare arrows."

"Hidden entrance nearby."

Notes should remain searchable.

---

# Favorites

Players may favorite important locations.

Examples include:

Home Settlement

Favorite Merchant

Training Area

Guild Hall

Safe Camp

Favorited locations should appear first in search results and navigation lists.

---

# Quest Markers

Quest objectives should remain visually distinct from other markers.

Examples include:

Primary Objective

Secondary Objective

Completed Objective

Optional Objective

Failed Objective

Quest markers summarize information while detailed objectives remain within the Quest Journal.

---

# Active Route

The interface may display the player's currently selected navigation route.

Route previews may include:

Destination

Estimated Distance

Estimated Travel Time

Known Hazards

Terrain Changes

The route should remain informational rather than prescriptive.

---

# Route Preview

Selecting a destination may preview the planned journey.

Examples include:

Roads

Mountain Passes

River Crossings

Dangerous Areas

Rest Stops

Settlements Along Route

Preview information helps players plan their adventures.

---

# Terrain Visualization

Terrain should remain visually distinct throughout the interface.

Examples include:

Mountains

Forests

Grasslands

Swamps

Deserts

Snowfields

Volcanic Regions

Oceans

Terrain should remain recognizable at multiple zoom levels.

---

# Roads

Known roads should become visible after discovery.

Examples include:

Trade Routes

Military Roads

Forest Trails

Mountain Paths

Hidden Paths (when discovered)

Roads improve navigation without revealing unexplored regions.

---

# Rivers and Waterways

Waterways should remain clearly identifiable.

Examples include:

Major Rivers

Streams

Lakes

Oceans

Canals

Ferries

Water features improve geographic understanding while enhancing immersion.

---

# Landmarks

Major landmarks should remain visually prominent.

Examples include:

Ancient Ruins

Great Trees

Volcanoes

Castles

Statues

Monuments

Watchtowers

Landmarks help players orient themselves naturally.

---

# Settlement View

Selecting a settlement opens a concise overview.

Examples include:

Settlement Name

Population

Ruling Faction

Known Services

Discovered NPCs

Recent Events

Available Fast Travel

The overview provides quick reference without replacing dedicated settlement systems.

---

# Dungeon View

Dungeon summaries may include:

Dungeon Name

Discovery Status

Completion Status

Difficulty

Known Boss

Collected Secrets

Current Quest Connections

Dungeon mechanics remain documented elsewhere.

---

# Companion Locations

When known, companion positions may appear on the map.

Examples include:

Traveling

Training

Resting

Guarding Settlement

Scouting

Unknown

Unknown locations should never display estimated positions.

---

# Dynamic World Events

Temporary world events may appear on the map.

Examples include:

Festival

Tournament

Siege

Merchant Caravan

Storm

Bandit Activity

Refugee Camp

These events should disappear when no longer active.

---

# AI Region Summary

Selecting a discovered region may generate a concise AI summary.

Examples include:

"The Ashlands remain scarred by centuries of war. Travelers report growing cult activity near the southern ruins."

"The Emerald Vale has prospered since the reopening of its trade routes."

Summaries should evolve as the world changes.

---

# Exploration Heatmap

Players may optionally view areas they have explored most frequently.

Examples include:

Frequently Traveled

Recently Visited

Rarely Visited

Never Visited

The heatmap provides an interesting retrospective without affecting gameplay.

---

# Search

The Map Interface includes a comprehensive search function.

Players may search for:

Region

Settlement

Dungeon

Landmark

Companion

Quest

Merchant

Custom Marker

Results should update immediately while typing.

---

# Filters

Players should be able to enable or disable categories independently.

Examples include:

Quest Markers

Settlements

Roads

Landmarks

Fast Travel

Companions

Shops

Guilds

Custom Markers

Active Events

Filtering affects presentation only.

# World State Overlay

The Map Interface may optionally display high-level information describing the current state of the world.

These overlays summarize ongoing world conditions without revealing hidden information.

Examples include:

- Political Influence
- War Zones
- Safe Regions
- Dangerous Regions
- Environmental Changes
- Seasonal Effects

World state overlays should remain optional.

---

# Political Influence

Players may visualize the territories controlled by major factions.

Examples include:

Kingdom Borders

Guild Influence

Military Occupation

Contested Territory

Independent Regions

Influence overlays should update naturally as the campaign evolves.

---

# Conflict Overlay

Active conflicts may be displayed.

Examples include:

Battles

Sieges

Civil Wars

Monster Incursions

Border Conflicts

Only conflicts known to the player should appear.

---

# Environmental Overlay

Environmental overlays summarize changing world conditions.

Examples include:

Wildfires

Flooding

Blizzards

Volcanic Activity

Magical Corruption

Ash Storms

These overlays help communicate a living world.

---

# Seasonal Overlay

The map may optionally display seasonal changes.

Examples include:

Snow Coverage

Autumn Forests

Frozen Lakes

Blooming Fields

Harvest Regions

Seasonal overlays affect presentation only.

---

# Weather Overlay

Current weather conditions may be visualized across explored regions.

Examples include:

Rain

Snow

Fog

Thunderstorms

Heat Waves

Strong Winds

Weather visualization should remain readable without obscuring navigation.

---

# Day and Night Visualization

The world map may reflect the current time of day.

Examples include:

Sunlight

Night Regions

Sunrise

Sunset

Moonlight

This visualization reinforces immersion while remaining optional.

---

# Discovery Timeline

Players may review when regions were discovered.

Examples include:

Discovery Date

Campaign Chapter

Current Progress

Major Events

Related Quests

This timeline celebrates exploration throughout long campaigns.

---

# Travel History

The interface may summarize previously traveled routes.

Examples include:

Frequently Used Roads

First Expedition

Longest Journey

Recent Route

Most Dangerous Expedition

Travel history encourages reflection without affecting navigation.

---

# Visited Locations

Previously visited locations should remain visually distinguishable.

Examples include:

Never Visited

Visited Once

Frequently Visited

Current Location

Home Settlement

Visited indicators should remain subtle.

---

# Region History

Each region may include a historical summary.

Examples include:

Major Battles

Political Changes

Important Decisions

Natural Disasters

Player Influence

The summary should evolve as the campaign progresses.

---

# Bookmarked Routes

Players may save frequently traveled routes.

Examples include:

Capital Route

Trade Route

Dungeon Run

Favorite Hunting Path

Guild Circuit

Bookmarked routes improve navigation efficiency.

---

# Route Management

Players should be able to:

Rename Routes

Delete Routes

Favorite Routes

Duplicate Routes

Add Notes

Routes remain entirely player-controlled.

---

# Recently Visited

The interface should summarize recently explored locations.

Examples include:

Last Settlement

Last Dungeon

Recent Landmark

Previous Region

Recent Fast Travel

This section helps players quickly resume exploration after returning to the game.

---

# Personal Atlas

The Map Interface gradually becomes the player's personal atlas.

The atlas combines:

Discovered Regions

Player Notes

Bookmarked Locations

Travel History

Favorite Routes

Discovery Timeline

World Events

The atlas reflects the player's individual journey rather than a universal map.

---

# Region Gallery

Important regions may include associated media.

Examples include:

Landscape Artwork

Settlement Illustration

Companion Screenshot

Story Cinematic

Generated Artwork

Selecting media opens the Media Gallery.

---

# World Statistics

The interface summarizes exploration progress.

Examples include:

Regions Discovered

Settlements Visited

Landmarks Found

Secrets Found

Maps Completed

Exploration Percentage

Statistics remain informational.

---

# Navigation History

Players may quickly return to recently viewed map locations.

Examples include:

Recent Region

Recent Settlement

Recent Dungeon

Recent Marker

Recent Search

History improves navigation efficiency.

---

# Multiple Map Views

The interface may support multiple visual styles.

Examples include:

Illustrated Map

Satellite Style

Political Map

Terrain Map

Minimal Navigation

Classic Fantasy Atlas

Changing map style affects presentation only.

---

# Legend

The interface includes a dynamic legend explaining visible symbols.

Examples include:

Marker Icons

Road Types

Faction Colors

Quest Indicators

Danger Icons

Weather Symbols

The legend updates automatically based on enabled filters.

---

# Context Actions

Different map elements provide different available actions.

Examples include:

Settlement

- Open Summary
- Set Destination
- Add Favorite
- Add Note

Dungeon

- View Summary
- Track Quest
- Add Marker

Companion

- Open Party Interface
- View Summary

Context actions reduce unnecessary menu navigation.

---

# Split View

Players may optionally compare two map regions simultaneously.

Possible uses include:

Comparing Kingdoms

Planning Routes

Tracking Multiple Objectives

Reviewing Political Changes

Split View remains optional.

---

# Route Comparison

Players may compare multiple possible routes.

Examples include:

Shortest Distance

Safest Route

Fastest Route

Scenic Route

Known Route

Unknown Route

Route comparison summarizes available information without guaranteeing outcomes.

---

# Collaborative Markers

When supported, campaigns may include shared markers.

Examples include:

Party Notes

Shared Objectives

Group Waypoints

Guild Locations

Shared markers should remain visually distinct from personal markers.

---

# Marker Collections

Players may organize custom markers into collections.

Examples include:

Treasure

Bosses

Crafting

Lore

Roleplaying

Exploration

Collections improve organization within large campaigns.

---

# Smart Recommendations

The interface may optionally recommend locations based on campaign context.

Examples include:

Nearby Unfinished Quest

Undiscovered Landmark

Companion Personal Quest

Recently Unlocked Region

Recommended Merchant

Recommendations remain optional and should never replace player choice.

---

# Recently Updated

Locations with recent changes should receive temporary emphasis.

Examples include:

New World Event

Political Change

Quest Update

Companion Activity

Settlement Expansion

Once viewed, recent indicators should disappear.

# Customization

Players should be able to customize the presentation of the Map Interface without affecting gameplay.

Customization options may include:

- Default zoom level
- Default map style
- Marker scale
- Icon density
- Label density
- Overlay transparency
- Route visibility
- Grid visibility
- Compass visibility

Customization should improve readability while maintaining interface consistency.

---

# Theme Support

The Map Interface should support all application-wide visual themes.

Examples include:

- Default
- Dark
- High Contrast
- Minimal
- Accessibility Themes
- Seasonal Themes (optional)

Themes modify presentation only.

---

# Accessibility Integration

The Map Interface should fully integrate with the Accessibility system.

Examples include:

- Adjustable text size
- High contrast mode
- Colorblind support
- Screen reader compatibility
- Keyboard-only navigation
- Controller navigation
- Touch optimization
- Reduced motion
- Adjustable icon scaling
- Increased marker spacing

Accessibility should be considered during initial interface design.

---

# Input Consistency

Navigation should remain intuitive regardless of platform.

Supported inputs include:

Keyboard and Mouse

Controller

Touch

Players should always understand how to:

- Pan
- Zoom
- Select markers
- Open summaries
- Search
- Filter
- Return
- Place custom markers

Input methods may differ, but available functionality should remain consistent.

---

# Animation Principles

Animations should reinforce navigation without delaying interaction.

Examples include:

- Smooth zoom transitions
- Marker selection
- Route previews
- Overlay transitions
- Discovery animations
- Region highlighting

Animations should remain responsive and optional.

---

# Performance

The Map Interface should remain responsive regardless of world size.

Implementation should prioritize:

- Lazy loading regions
- Cached map tiles
- Incremental marker loading
- Efficient filtering
- Optimized search indexing
- Dynamic label rendering
- Viewport-based updates

Performance should remain stable even during extremely large campaigns.

---

# Save Integration

The Map Interface should accurately reflect the player's current campaign.

Displayed information should remain synchronized with:

- World discovery
- Exploration progress
- Quest progression
- Companion locations
- Custom markers
- Player notes
- Bookmarked routes
- World events

The interface should never become the authoritative source of this information.

---

# Offline Availability

Previously discovered information should remain available while offline.

Examples include:

- Explored regions
- Player notes
- Saved routes
- Favorites
- Discovery timeline
- Region summaries

Unavailable online services should never prevent players from viewing previously acquired information.

---

# Error Handling

When information cannot be displayed, the interface should fail gracefully.

Examples include:

- Missing artwork
- Missing region preview
- Delayed AI summary
- Corrupted custom marker
- Missing event icon

Fallback behavior should prioritize usability over visual completeness.

---

# Privacy

Player-created map information should remain under player control.

Examples include:

- Notes
- Custom markers
- Bookmarked routes
- Favorites
- Collections
- Personal atlas organization

Player-created information should remain clearly distinguished from system-generated content.

---

# Interface Ownership

The Map Interface presents information owned by multiple engine systems.

Examples include:

World

- Geography
- Regions
- Settlements
- Exploration

Quests

- Objectives
- Quest markers

Characters

- Companion locations
- Party position

Campaign

- World events
- Timeline

Media Gallery

- Region artwork
- Landscape illustrations

AI

- Region summaries
- Smart recommendations

The Map Interface owns presentation only.

---

# Interaction With Other Interfaces

The Map Interface naturally connects to multiple interfaces.

Examples include:

Quest Marker

↓

Quest Journal

Companion Marker

↓

Party Interface

Player Marker

↓

Player Interface

Region Artwork

↓

Media Gallery

Campaign Event

↓

Campaign Hub

Settlement Summary

↓

Settlement Systems

Navigation between interfaces should remain direct and intuitive.

---

# Future Extensibility

Future systems should integrate naturally into the Map Interface.

Potential additions include:

- Naval Charts
- Underground Maps
- Sky Islands
- Dynamic Kingdom Borders
- Community Maps
- Player Housing
- Guild Territories
- Seasonal Festivals
- Expedition Planning

Future additions should follow the navigation philosophy established within this document.

---

# Design Philosophy

The Map Interface is more than a navigation screen.

It is the player's evolving understanding of the world.

Rather than revealing every secret from the beginning, the map grows alongside the adventure.

Every discovered settlement, every handwritten note, every bookmarked journey, every changing political border, and every AI-generated regional summary becomes part of the player's personal atlas.

Every feature should answer one of three questions:

"Where have I been?"

"Where can I go?"

"How has the world changed?"

If a feature cannot help answer one of those questions, it should be reconsidered before becoming part of the interface.

The Map Interface should encourage exploration rather than replace it, allowing curiosity—not icons—to guide the player's adventure.

---

# Summary

The Map Interface provides an interactive, accessible, and immersive representation of the player's discovered world.

It presents regions, settlements, routes, markers, exploration progress, world events, AI-generated summaries, and player-created notes through a unified interface while leaving gameplay mechanics to their respective systems.

By emphasizing progressive discovery, intuitive navigation, extensive customization, and the concept of a living personal atlas, the Map Interface transforms exploration from a means of travel into a permanent record of the player's unique journey through The Shattered Realms.

