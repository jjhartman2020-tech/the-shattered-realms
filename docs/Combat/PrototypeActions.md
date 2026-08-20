# Prototype Combat Actions

Status: In Development

This file defines the first playable implementation of the action-economy framework described in `CoreMechanics.md` and `CombatFlow.md`.

## Primary Action

- Each combatant receives **1 primary action per turn** by default.
- A basic Attack consumes the primary action.
- Defend consumes the primary action.
- Movement uses its own Movement budget and does **not** consume the primary action.
- Movement may occur before or after the primary action as long as movement remains.
- When the combatant's next turn begins, the primary action becomes available again.
- An invalid action does not consume the primary action.
- Additional actions may later be granted by abilities, equipment, statuses, or special rules.

## Defend

The prototype Defend action is a universal defensive option tied to the Defense attribute.

- Defend costs the combatant's primary action.
- Defense is a 0-30 attribute.
- `Defend AC Bonus = floor(Defense / 3)`.
- Every full 3 Defense grants +1 temporary Armor Class while defending.
- The bonus lasts until the start of that combatant's next turn.
- The bonus affects the Armor Class used when resolving incoming attacks.
- Defend does not consume movement, so the combatant may still use any remaining Movement before ending the turn.

Examples:

- Defense 0-2 = +0 AC while defending.
- Defense 3-5 = +1 AC.
- Defense 9-11 = +3 AC.
- Defense 17 = +5 AC.
- Defense 30 = +10 AC.

## Multiple Combatants and Targeting

The combat engine may contain multiple living combatants on either side.

- Every combatant in one encounter must have a unique combat name so initiative and targeting remain unambiguous.
- When multiple enemies of the same kind appear, they must be distinguishable, such as `Goblin Guard 1` and `Goblin Guard 2`, or by different roles such as `Goblin Guard` and `Goblin Archer`.
- Attack and move-attack actions target one specific living combatant unless an ability explicitly supports multiple targets.
- The chosen target's own HP, Armor Class, position, Defense state, resistances, and defeat state are resolved independently.
- Defeating one enemy does not end combat while another opposing combatant remains alive.
- Initiative continues through all living combatants, skipping defeated combatants.
- Enemy target selection should follow `EnemyAI.md`: distance, threat, accessibility, health, positioning, objectives, and information the enemy could reasonably know may influence the choice.

## Turn Ending

Using a primary action does not automatically end the player's turn. The player may still spend remaining Movement, then explicitly end/pass the turn. Enemy AI completes its chosen action(s) and then advances the turn automatically.

## Next Systems

The same primary-action framework will be used for:

- Active Abilities
- Item use
- Environmental interactions
- Helping allies
- Prepared actions
- Retreat attempts
- Other campaign-specific combat actions

Each system must validate costs, legal targets, ranges, resources, and other requirements before consuming the primary action.
