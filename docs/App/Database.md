# Database

## Table of Contents

1. Purpose
2. Database Principles
3. Data Ownership
4. Data Categories
5. Entity Identity
6. Relationships and References
7. Data Validation
8. Versioning and Migration
9. Caching and Temporary Data
10. Security and Privacy
11. Interaction With Other Systems
12. Summary

---

# Purpose

The Database framework defines how persistent engine and campaign data is organized, identified, validated, and accessed.

The database stores the information required to reconstruct the state of a campaign while supporting content creation, world simulation, saving, modding, and future expansion.

This document defines the responsibilities and structure of stored data without requiring a specific database technology.

The engine may use relational databases, document databases, local files, cloud storage, or a combination of these approaches as long as the documented responsibilities remain consistent.

---

# Database Principles

The database should follow several core principles.

## Single Source of Truth

Every piece of authoritative data should have one clearly defined owner.

For example:

- Character data should be owned by the Character system.
- Inventory data should be owned by the Inventory system.
- Quest state should be owned by the Quest system.
- World state should be owned by World Simulation.
- Account information should be owned by Authentication.

Other systems may read or reference this data, but they should not maintain competing versions of it.

---

## Separation of Definitions and State

The database should distinguish between content definitions and runtime state.

### Definitions

Definitions describe what something is.

Examples include:

- An item template.
- A class definition.
- A quest structure.
- A settlement description.
- An ability definition.
- A campaign configuration.

### State

State describes the current condition of a specific campaign or entity.

Examples include:

- A character's current health.
- An item instance in a player's inventory.
- A quest's current stage.
- A settlement's present ruler.
- A faction's current reputation.
- The current time and weather.

Definitions should remain reusable, while state should change as the campaign progresses.

---

## Data Independence

Stored data should not depend unnecessarily on application code structure.

Changing the internal implementation of a module should not require rewriting unrelated campaign data.

Persistent data should rely on stable schemas, identifiers, and documented relationships.

---

## Data Integrity

The database should prevent invalid or contradictory state whenever practical.

Examples include:

- An inventory referencing an item that does not exist.
- A character assigned to an invalid location.
- A completed quest retaining an active objective.
- A companion belonging to two incompatible parties.
- A world event referencing a deleted settlement.

Validation should occur before invalid data becomes authoritative.

---

## Recoverability

The database should support recovery from failures.

The engine should protect against:

- Interrupted writes.
- Corrupted saves.
- Failed migrations.
- Invalid mod data.
- Partial updates.
- Unexpected application shutdowns.

Whenever possible, the engine should preserve the most recent valid state.

---

# Data Ownership

Each data category should be owned by the module responsible for its behavior.

Ownership determines:

- Which module may create the data.
- Which module may modify it.
- Which module validates it.
- Which systems may receive change notifications.
- How the data is serialized and restored.

Ownership should not prevent other systems from reading necessary information through documented interfaces.

For example, Combat may read character attributes, equipment, and status effects, but it should not independently rewrite their permanent records without going through the responsible modules.

---

# Data Categories

The database should organize information into clear categories.

## Engine Data

Engine data describes the application's supported formats and internal configuration.

Examples include:

- Engine version.
- Schema versions.
- Supported content types.
- System configuration.
- Feature flags.
- Migration records.

Engine data should remain separate from individual campaign content and player saves.

---

## Campaign Definitions

Campaign definitions describe creator-authored content.

Examples include:

- Campaign metadata.
- World lore.
- Kingdoms.
- Settlements.
- Factions.
- NPC templates.
- Quests.
- Dialogue.
- Items.
- Abilities.
- Dungeons.
- World events.
- Custom rules permitted by the engine.

These definitions may come from official content, community content, or locally created campaigns.

Campaign definitions should be treated as authoritative within the campaign that loads them.

---

## Runtime Campaign State

Runtime campaign state records how the campaign has changed during play.

Examples include:

- Current date and time.
- Current weather.
- Political borders.
- Active conflicts.
- Settlement conditions.
- Quest progression.
- World event progression.
- Discovered locations.
- Destroyed or altered locations.
- Faction relationships.
- Economic conditions.

This state should be sufficient to restore the living world accurately.

---

## Character Data

Character data may include:

- Identity.
- Appearance.
- Stats.
- Class.
- Origin.
- Abilities.
- Progression.
- Current conditions.
- Equipment.
- Inventory references.
- Relationships.
- Reputation.
- Party membership.
- Location.
- Personal history.

Character definitions and character instances should remain distinguishable.

A reusable NPC template is different from the specific NPC instance encountered in a campaign.

---

## Player Data

Player data may include:

- Account reference.
- Preferences.
- Accessibility settings.
- Input settings.
- Interface configuration.
- Campaign permissions.
- Connected characters.
- Multiplayer status.

Gameplay state should remain associated with the campaign rather than being stored only in the player's account.

---

## Save Metadata

Every save should contain enough metadata for the engine to identify and validate it.

Examples include:

- Save identifier.
- Campaign identifier.
- Engine version.
- Campaign version.
- Creation time.
- Last modified time.
- Playtime.
- Active character.
- Current location.
- Required mods.
- Schema version.
- Save status.
- Compatibility information.

Save metadata allows the application to inspect a save before fully loading it.

---

## Generated Content

Procedurally generated content should be stored when it becomes relevant to campaign continuity.

Examples include:

- Generated NPCs.
- Generated quests.
- Generated settlements.
- Generated dungeon layouts.
- Generated dialogue facts.
- Generated world events.
- Generated items with persistent identity.

Generated content should not be regenerated differently after it becomes established canon.

Temporary suggestions or unused generation candidates do not need to become persistent data.

---

## Historical Data

The engine may maintain records of important past changes.

Examples include:

- Completed quests.
- Major character deaths.
- Former rulers.
- Previous faction alliances.
- Resolved world events.
- Significant player decisions.
- Settlement ownership changes.
- Discovered lore.
- Campaign milestones.

Historical records support AI memory, dialogue, recaps, continuity, and world simulation.

Not every minor action requires permanent historical storage.

---

## Logs and Diagnostics

Operational information should remain separate from authoritative gameplay state.

Examples include:

- Error logs.
- AI request logs.
- Performance measurements.
- Mod validation reports.
- Migration reports.
- Debug events.
- Network diagnostics.

Deleting diagnostic logs should not alter the campaign itself.

---

# Entity Identity

Every persistent entity should have a stable identifier.

Examples include:

- Characters.
- Items.
- Quests.
- Locations.
- Settlements.
- Kingdoms.
- Factions.
- Events.
- Saves.
- Campaigns.
- Content packages.

Identifiers allow entities to be referenced safely across systems.

---

## Definition Identifiers

Definition identifiers refer to reusable content.

Examples include:

- `core.weapon.iron_sword`
- `campaign.blackspire.kingdom.ravenhold`
- `mod.frostlands.status.frozen`

Definition identifiers should be:

- Unique.
- Stable.
- Descriptive.
- Namespaced.
- Independent of display names.

Changing the displayed name of an item should not break references to it.

---

## Instance Identifiers

Instance identifiers refer to specific runtime objects.

For example, two characters may each possess an item created from the same sword definition.

Each sword instance should have its own identifier so the engine can track:

- Ownership.
- Durability.
- Enchantments.
- Custom names.
- History.
- Location.

Definition identifiers explain what an object is.

Instance identifiers explain which specific object it is.

---

## Identifier Stability

Persistent identifiers should not be reused after deletion.

Reusing identifiers may cause historical references, saves, logs, or scripts to point to the wrong entity.

Human-readable names may change, but stable identifiers should remain unchanged whenever possible.

---

# Relationships and References

Entities should reference one another through stable identifiers rather than duplicated embedded data whenever practical.

Examples include:

- A character references their current location.
- An inventory references item instances.
- A quest references relevant NPCs and settlements.
- A faction references allied and hostile factions.
- A world event references affected regions.
- A save references its campaign and required content packages.

References reduce duplication and help preserve consistency.

---

## Strong References

A strong reference represents a relationship required for the entity to function.

For example:

- An item instance requires an item definition.
- A save requires its campaign.
- A quest stage may require its parent quest.

Missing strong references should prevent affected content from loading normally.

---

## Optional References

An optional reference enriches content but is not required for basic functionality.

For example:

- An NPC may reference an optional portrait.
- A settlement may reference background music.
- A quest may reference optional flavor dialogue.

Missing optional references should produce warnings or graceful fallbacks rather than total failure.

---

## Historical References

Historical records may reference entities that are no longer active.

The engine should preserve enough identifying information to interpret the record even if the original entity has been removed from current gameplay.

For example, the campaign history may still record that a destroyed kingdom once controlled a region.

---

# Data Validation

All data should be validated before becoming authoritative.

Validation should occur at appropriate stages, including:

- Content import.
- Mod loading.
- Campaign creation.
- Save creation.
- Save loading.
- Data migration.
- Network synchronization.
- Script execution.

---

## Structural Validation

Structural validation confirms that data follows the required schema.

Examples include:

- Required fields are present.
- Values use valid data types.
- Identifiers follow supported formats.
- Collections contain valid entries.
- Enumerated values are recognized.

---

## Referential Validation

Referential validation confirms that relationships are valid.

Examples include:

- Referenced entities exist.
- Required dependencies are installed.
- Parent-child relationships are consistent.
- Circular references are not present where prohibited.
- Cross-package references are permitted.

---

## Logical Validation

Logical validation confirms that the stored state makes sense within engine rules.

Examples include:

- Current health does not exceed permitted limits.
- A character cannot occupy an inaccessible deleted location.
- A completed quest cannot also be marked unstarted.
- An unequipped item cannot occupy an equipment slot.
- A deceased character cannot remain an active party member unless supported by the campaign.

The responsible gameplay system should define these rules.

The database should enforce or request validation without redefining them.

---

## Validation Results

Validation errors should clearly report:

- The affected entity.
- The invalid field or reference.
- The source package or save.
- The severity of the problem.
- Whether the engine can recover.
- A useful explanation when possible.

Validation messages should help developers and creators fix problems rather than simply declaring the data invalid

---

# Versioning and Migration

The database should support long-term evolution without unnecessarily breaking existing campaigns or saves.

As the engine grows, schemas, content formats, and internal structures may change.

Migration systems should allow older data to be updated safely while preserving player progress whenever possible.

---

## Schema Versioning

Every persistent dataset should declare its schema version.

Examples include:

- Engine database schema.
- Save schema.
- Campaign schema.
- Mod schema.
- Configuration schema.

Version information allows the engine to determine whether migration or compatibility checks are required before loading.

---

## Data Migration

When incompatible changes occur, migration procedures should transform older data into the current supported format.

Migration should:

- Preserve existing information whenever possible.
- Report any data that cannot be converted.
- Validate migrated data before use.
- Prevent partial or inconsistent migrations.

Failed migrations should never overwrite the original data.

---

## Backward Compatibility

Engine updates should strive to maintain compatibility with previous content.

When compatibility cannot be preserved, the engine should clearly identify:

- Unsupported engine versions.
- Missing migrations.
- Deprecated content.
- Required creator updates.

Compatibility decisions should prioritize data integrity over automatic loading.

---

# Transactions and Atomic Operations

Persistent changes should be treated as complete operations rather than unrelated writes.

If multiple pieces of data must change together, the engine should commit them as a single transaction whenever practical.

Examples include:

- Completing a quest while granting rewards.
- Purchasing an item while reducing currency.
- Recruiting a companion while updating party membership.
- Saving a campaign after multiple world changes.

If part of the operation fails, the engine should restore the previous valid state whenever possible.

This prevents partially completed actions from corrupting campaign data.

---

# Caching and Temporary Data

Not all information needs permanent storage.

The engine may maintain temporary data to improve performance.

Examples include:

- AI reasoning context.
- Navigation caches.
- Pathfinding results.
- Render data.
- Temporary calculations.
- Session-only user interface state.

Temporary data should always be rebuildable from authoritative persistent data.

Deleting cached information should never permanently alter a campaign.

---

## Session State

Some information exists only while the application is running.

Examples include:

- Currently selected menu.
- Open dialogue window.
- Active editor tools.
- Camera position.
- Debug overlays.

Unless explicitly requested by the user, session state should not become part of campaign saves.

---

# Backup and Recovery

The engine should support recovering from unexpected failures.

Recovery features may include:

- Automatic backups.
- Manual backups.
- Recovery checkpoints.
- Save verification.
- Corruption detection.
- Rollback to previous valid versions.

Whenever possible, users should be informed before any potentially destructive recovery action occurs.

---

## Save Integrity

The engine should verify save integrity before loading.

Verification may include:

- File completeness.
- Schema validation.
- Reference validation.
- Required content availability.
- Data consistency.
- Checksum or integrity verification.

Corrupted saves should provide useful diagnostic information while preserving any recoverable data.

---

# Security and Privacy

Persistent data should be protected against unauthorized modification and accidental loss.

Security considerations include:

- Authentication.
- Authorization.
- Data encryption when appropriate.
- Secure cloud synchronization.
- Safe handling of user credentials.
- Protection against malicious content packages.

Campaign content should never gain unrestricted access to player or system information.

---

## Privacy

Player information should remain separate from gameplay data whenever practical.

Examples include:

- Account credentials.
- Personal profile information.
- Analytics preferences.
- Cloud account details.

Campaign authors and mods should only access player information explicitly exposed through documented engine interfaces.

---

# Performance Considerations

The database should remain efficient as campaigns grow in complexity.

Performance strategies may include:

- Indexed lookups.
- Lazy loading.
- Incremental updates.
- Background maintenance.
- Efficient serialization.
- Selective loading of nearby or relevant world data.

Performance optimizations should never compromise correctness or data integrity.

---

# Multiplayer Considerations

If multiplayer is supported, the database should distinguish between:

- Shared world state.
- Individual player state.
- Session-specific information.
- Server-managed data.
- Client-managed data.

Conflict resolution and synchronization should preserve a consistent authoritative world while minimizing unnecessary data transfer.

The database framework defines these responsibilities without prescribing a specific networking architecture.

---

# Interaction With Other Systems

The Database framework provides persistent storage for every major engine system.

Examples include:

- **Save System** manages when data is written and restored.
- **Architecture** defines ownership and communication between modules.
- **AI** reads and updates campaign knowledge through documented interfaces.
- **World Simulation** maintains the evolving state of the world.
- **Campaign Creation** supplies creator-authored definitions.
- **Custom Content** registers additional persistent data.
- **Scripting** interacts with stored data through the engine's supported APIs.

The database stores authoritative information while individual systems remain responsible for the behavior associated with that information.

---

# Data Lifecycle

Every piece of persistent data should follow a predictable lifecycle.

Understanding this lifecycle ensures that information remains consistent, recoverable, and maintainable throughout the life of a campaign.

The lifecycle generally consists of:

1. Creation
2. Validation
3. Active Use
4. Modification
5. Persistence
6. Archival
7. Removal

---

## Creation

Persistent data may originate from several sources.

Examples include:

- Official engine content.
- Campaign definitions.
- Community-created content.
- Procedural generation.
- Player actions.
- AI-generated content.

Newly created data should receive:

- A stable identifier.
- Initial validation.
- Appropriate ownership.
- Default values where required.

No data should become authoritative before passing validation.

---

## Validation

After creation, data should be verified before entering active use.

Validation should ensure:

- Structural correctness.
- Valid relationships.
- Logical consistency.
- Engine compatibility.
- Content compatibility.

Invalid data should never become part of the authoritative database.

---

## Active Use

Once validated, data becomes part of the active campaign.

During gameplay, systems may:

- Read data.
- Reference data.
- Request modifications.
- Generate new relationships.
- Produce events based on the current state.

Ownership rules remain in effect throughout active use.

Only the responsible module should authorize permanent modifications.

---

## Modification

Persistent data changes as the campaign evolves.

Examples include:

- Character progression.
- Inventory changes.
- Quest advancement.
- Settlement development.
- Political changes.
- AI-generated memories.
- World event progression.

Every modification should preserve consistency with existing relationships and validation rules.

Whenever practical, changes should occur through documented engine interfaces rather than direct database manipulation.

---

## Persistence

Authoritative state should periodically be written to persistent storage.

Persistence may occur:

- During manual saves.
- During automatic saves.
- At important milestones.
- Before application shutdown.
- During cloud synchronization.

The Save System determines *when* persistence occurs.

The Database framework defines *what* is stored.

---

## Archival

Some information is no longer active but remains valuable.

Archived information may include:

- Completed quests.
- Historical rulers.
- Retired companions.
- Previous alliances.
- Former settlement ownership.
- Significant player achievements.
- Past world events.

Archived data supports:

- Campaign continuity.
- Historical records.
- AI memory.
- Dialogue.
- Recaps.
- Analytics.
- Future procedural generation.

Archival preserves history without cluttering active gameplay systems.

---

## Removal

Some information may eventually be removed.

Examples include:

- Temporary caches.
- Expired session data.
- Obsolete backups.
- Unused generated content.
- Deleted campaigns.

Before removal, the engine should verify that no required references remain.

Removing active authoritative data should only occur through documented engine procedures.

---

# Data Lifecycle Responsibilities

Different systems participate in different stages of the lifecycle.

Examples include:

| System | Primary Responsibility |
|---------|------------------------|
| Database | Store authoritative data |
| Save System | Persist and restore state |
| AI | Generate and consume persistent knowledge |
| World Simulation | Update world state |
| Character | Manage character records |
| Inventory | Manage item ownership |
| Quest | Manage progression state |
| Mod Loader | Register external content |
| Validation Systems | Verify correctness |

Each system contributes to the lifecycle while maintaining its own documented responsibilities.

---

# Future Scalability

The Database framework should continue supporting future engine growth without requiring fundamental redesign.

Future capabilities may include:

- Distributed storage.
- Dedicated multiplayer servers.
- Cloud-native persistence.
- Large-scale procedural worlds.
- Multiple simultaneous campaigns.
- Cross-platform synchronization.
- Advanced analytics.
- Creator collaboration tools.

The framework should accommodate these features through extension rather than replacement.

---

# Summary

The Database framework provides the authoritative foundation for all persistent information within The Shattered Realms engine.

By defining clear ownership, stable identifiers, validation procedures, relationships, versioning, lifecycle management, and long-term scalability, the framework ensures that every campaign remains consistent, recoverable, and extensible throughout its lifetime.

The Database is not responsible for gameplay mechanics or business logic. Instead, it serves as the trusted source of persistent information that every engine system relies upon to create a living, evolving world.
