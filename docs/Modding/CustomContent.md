# Custom Content

## Table of Contents

1. Purpose
2. Content Philosophy
3. Supported Content Types
4. Content Registration
5. Content Validation
6. Dependencies
7. Packaging and Distribution
8. Best Practices
9. Interaction With Other Systems
10. Summary

---

# Purpose

The Custom Content framework defines how creators add new content to The Shattered Realms without modifying the core engine.

Custom content extends the game through data, assets, and configuration while relying on the engine's existing systems for behavior.

This approach allows campaigns, expansions, and community-created projects to remain modular, maintainable, and compatible with future engine updates.

---

# Content Philosophy

Custom content should build upon documented engine systems rather than replacing them.

Creators should be able to introduce entirely new experiences while preserving consistency with the core framework.

The engine should support extension through configuration whenever possible and reserve scripting for behavior that cannot be expressed through existing systems.

---

# Supported Content Types

Creators may define custom versions of any supported content category.

Examples include:

- Items
- Equipment
- Weapons
- Armor
- Consumables
- Characters
- NPCs
- Companions
- Enemies
- Bosses
- Classes
- Origins
- Abilities
- Status Effects
- Quests
- Dialogue
- Factions
- Kingdoms
- Settlements
- Dungeons
- World Events
- Crafting Recipes
- Merchants
- Loot Tables
- Music
- Sound Effects
- Visual Assets
- User Interface Assets

Future engine versions may expand this list without breaking existing content.

---

# Content Registration

Every custom asset should be registered with the engine using standardized identifiers.

Each registered object should provide enough information for the engine to:

- Identify it.
- Load it.
- Validate it.
- Reference it.
- Save it.
- Share it with other systems.

Identifiers should remain unique within the scope of the loaded project.

---

# Content Validation

Before loading custom content, the engine should verify that it is valid.

Validation may include:

- Required fields.
- Data types.
- Missing references.
- Duplicate identifiers.
- Circular dependencies.
- Unsupported engine versions.
- Asset availability.

Invalid content should produce clear error messages that help creators locate and resolve issues.

Whenever possible, invalid content should not prevent unrelated content from loading.

---

# Dependencies

Some content may depend on other content packs or campaigns.

Dependencies should declare:

- Required packages.
- Optional packages.
- Supported engine versions.
- Minimum versions.
- Incompatible packages.

The engine should verify dependencies before enabling custom content.

---

# Packaging and Distribution

Custom content should be distributed as self-contained packages.

A package may contain:

- Configuration files.
- Assets.
- Localization.
- Documentation.
- Scripts.
- Metadata.

Packages should be portable, easy to install, and removable without affecting the core engine.

---

# Best Practices

Creators are encouraged to:

- Reuse existing engine systems.
- Keep identifiers descriptive and consistent.
- Document custom assets.
- Organize content into logical folders.
- Minimize unnecessary dependencies.
- Test compatibility with supported engine versions.
- Avoid duplicating existing content unless intentionally replacing it.

Well-organized content is easier to maintain, share, and expand.

---

# Interaction With Other Systems

The Custom Content framework extends existing engine systems without redefining their behavior.

Examples include:

- **Campaign Creation** organizes custom content into playable campaigns.
- **Scripting** adds custom logic when configuration alone is insufficient.
- **AI** interprets custom lore, dialogue, and world data.
- **Combat**, **Characters**, **World**, and **Systems** consume custom content through their documented interfaces.

Custom Content provides new data while existing systems determine how that data behaves.

---

# Summary

The Custom Content framework enables creators to expand The Shattered Realms through modular, reusable content packages.

By separating data from engine logic, creators can build new adventures, settings, mechanics, and experiences while preserving compatibility, stability, and long-term maintainability.
