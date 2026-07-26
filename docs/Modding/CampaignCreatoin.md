# Campaign Creation

## Table of Contents

1. Purpose
2. Campaign Structure
3. Campaign Metadata
4. World Configuration
5. Starting Conditions
6. AI Responsibilities
7. Compatibility
8. Best Practices
9. Interaction With Other Systems
10. Summary

---

# Purpose

The Campaign Creation framework defines how creators build new campaigns using The Shattered Realms engine.

A campaign is a collection of content, configuration, and world data that uses the engine's existing systems without modifying their behavior.

Campaigns should be easy to create, expand, maintain, and share while remaining compatible with future versions of the engine whenever possible.

---

# Campaign Structure

Every campaign should consist of organized content rather than engine modifications.

Typical campaign components may include:

- World Data
- Kingdoms
- Settlements
- Factions
- NPCs
- Quests
- Dungeons
- Items
- Dialogue
- Events
- Custom Assets
- Configuration Files

Campaigns should separate content from engine logic to improve maintainability and compatibility.

---

# Campaign Metadata

Each campaign should define basic metadata describing the project.

Metadata may include:

- Campaign Name
- Author
- Version
- Supported Engine Version
- Description
- Tags
- Recommended Player Count
- Recommended Difficulty
- Required Dependencies

Metadata helps the engine identify, organize, and validate campaigns.

---

# World Configuration

Campaign creators should configure the world without changing core engine systems.

Examples include:

- World Map
- Regions
- Starting Kingdoms
- Climate
- Cultures
- Languages
- Historical Background
- Religious Beliefs
- Technology Level
- Magic Availability

These settings establish the identity of the campaign while relying on existing engine mechanics.

---

# Starting Conditions

Campaigns should define how players enter the world.

Starting conditions may include:

- Starting Location
- Initial Equipment
- Starting Reputation
- Companion Availability
- Opening Quest
- Time of Year
- World State
- Difficulty Modifiers

Campaign creators should have flexibility while preserving consistency with engine rules.

---

# AI Responsibilities

When running a campaign, the AI should:

- Interpret campaign data consistently.
- Respect creator-defined lore.
- Preserve continuity.
- Generate new content that matches the campaign's tone.
- Avoid contradicting established world information.
- Use procedural generation only where permitted by campaign configuration.

The AI should treat creator-defined content as authoritative unless explicitly overridden by engine rules.

---

# Compatibility

Campaigns should remain compatible across engine updates whenever practical.

To support compatibility, creators should:

- Avoid modifying core engine systems.
- Use documented extension points.
- Follow standardized data structures.
- Declare required engine versions.
- Minimize unnecessary dependencies.

Future engine updates should strive to preserve compatibility with existing campaigns whenever possible.

---

# Best Practices

Campaign creators are encouraged to:

- Keep lore internally consistent.
- Define clear goals and themes.
- Reuse existing engine systems whenever possible.
- Avoid duplicating mechanics.
- Organize content into logical categories.
- Test campaign progression from beginning to end.
- Document custom content for future maintenance.

Well-structured campaigns are easier to expand and more enjoyable to play.

---

# Interaction With Other Systems

Campaign Creation builds upon nearly every documented system within the engine.

Examples include:

- **World** defines locations and environments.
- **Characters** define NPCs and companions.
- **Combat** governs encounters.
- **Quests** provide progression.
- **AI** interprets campaign content.
- **Procedural Generation** expands creator-authored content where appropriate.
- **Custom Content** extends the campaign with additional assets and data.

Campaign Creation defines how these systems are assembled into a complete playable experience.

---

# Summary

The Campaign Creation framework provides a structured approach for building complete adventures within The Shattered Realms.

By separating campaign content from engine functionality, creators can build rich, expandable worlds while benefiting from a stable and reusable AI-driven RPG engine.
