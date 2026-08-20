# Prototype Combat Actions

Status: In Development

This file defines the first playable implementation of the action-economy framework described in `CoreMechanics.md` and `CombatFlow.md`.

## Primary Action

- Each combatant receives **1 primary action per turn** by default.
- A basic Attack consumes the primary action.
- Defend consumes the primary action.
- An Active Ability consumes the primary action unless a future ability explicitly says otherwise.
- Movement uses its own Movement budget and does **not** consume the primary action.
- Movement may occur before or after the primary action as long as movement remains.
- When the combatant's next turn begins, the primary action becomes available again.
- An invalid action does not consume the primary action or spend resources.
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
- Attack, move-attack, and targeted ability actions target one specific living combatant unless an ability explicitly supports multiple targets.
- The chosen target's own HP, Armor Class, position, Defense state, resistances, and defeat state are resolved independently.
- Defeating one enemy does not end combat while another opposing combatant remains alive.
- Initiative continues through all living combatants, skipping defeated combatants.
- Enemy target selection should follow `EnemyAI.md`: distance, threat, accessibility, health, positioning, objectives, and information the enemy could reasonably know may influence the choice.

## Encounter Reset and Reconfiguration

- A normal combat reset restores the existing encounter to its pristine pre-fight state.
- The original enemy roster, max HP, stats, positions, equipment-derived combat values, and other combat data are preserved on a normal reset.
- If the player explicitly changes the encounter while resetting it, such as adding an archer, removing a guard, or replacing enemies, the revised **complete enemy roster** becomes the template for the next start.
- A roster change must be stored mechanically; narration alone does not create or remove combatants.
- After the reconfigured encounter begins, that new roster becomes the pristine template used by future normal resets.

## Active Abilities

The first active-ability framework is data-driven and follows `Abilities.md`.

- Only abilities equipped on the combatant may be used.
- The engine validates the exact ability name before resolving it.
- Active abilities may define a resource, resource cost, cooldown, target type, range, attack attribute, damage expression, and optional damage-scaling attribute.
- Mana is the first supported ability resource. Other resources such as Stamina, Rage, Focus, Energy, Ki, Divine Power, and Shadow Energy remain planned.
- An ability cannot be used without enough of its required resource.
- Invalid ability attempts do not consume mana or the primary action.
- Targeted abilities respect battlefield positions and range.
- Attack-roll abilities obey natural 1 automatic misses and natural 20 critical hits.
- Ability damage and resource spending are resolved by Python and are authoritative.
- Cooldowns are tracked per combatant and prevent reuse until the ability becomes ready.

### Prototype Test Ability

`Power Strike` exists temporarily so the active-ability engine can be tested before final class ability libraries are wired into character creation.

- Type: Active
- Category: Offensive
- Resource: Mana
- Cost: 1 Mana
- Target: Enemy
- Range: 1 square
- Attack Attribute: Strength
- Damage: 1d8 + Strength scaling
- Cooldown: 1 turn

`Power Strike` is a prototype test ability, not a statement that every finished class will automatically receive it.

## Turn Ending

Using a primary action does not automatically end the player's turn. The player may still spend remaining Movement, then explicitly end/pass the turn. Enemy AI completes its chosen action(s) and then advances the turn automatically.

## Next Systems

The same primary-action framework will be expanded for:

- Full class ability libraries
- Additional ability resources
- Healing, buffs, debuffs, mobility, and crowd control abilities
- Item use
- Environmental interactions
- Helping allies
- Prepared actions
- Retreat attempts
- Other campaign-specific combat actions

Each system must validate costs, legal targets, ranges, resources, and other requirements before consuming the primary action.
