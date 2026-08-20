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

The prototype Defend action is a simple universal defensive option.

- Defend costs the combatant's primary action.
- Defend grants **+2 Armor Class**.
- The bonus lasts until the start of that combatant's next turn.
- The bonus affects the Armor Class used when resolving incoming attacks.
- Defend does not consume movement, so the combatant may still use any remaining Movement before ending the turn.

This is a prototype balance value and may be tuned later, but the engine and documentation must be updated together if it changes.

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
