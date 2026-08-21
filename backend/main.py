"""Command-line entry point for testing The Shattered Realms runtime."""

from backend.ai.game_master import GameMaster
from backend.game.character_creation import run_character_creation


def _position_xy(actor) -> tuple[int, int]:
    position = actor.get("position") or {"x": 0, "y": 0}
    if isinstance(position, (list, tuple)) and len(position) >= 2:
        return int(position[0]), int(position[1])
    if isinstance(position, dict):
        return int(position.get("x", 0)), int(position.get("y", 0))
    return 0, 0


def _print_combat_hud(combat) -> None:
    if not isinstance(combat, dict) or not combat.get("active"):
        return
    combatants = combat.get("combatants") or []
    player = next((a for a in combatants if isinstance(a, dict) and a.get("team") == "player"), None)
    if player:
        movement = int(player.get("movement", 0) or 0)
        used = int(player.get("movement_used", 0) or 0)
        x, y = _position_xy(player)
        resource_name = str(player.get("resource_name") or "Resource")
        resource = int(player.get("resource", player.get("mana", 0)) or 0)
        max_resource = int(player.get("max_resource", player.get("max_mana", resource)) or resource)
        action = "USED" if player.get("primary_action_used") else "READY"
        order = combat.get("order") or []
        index = int(combat.get("turn_index", 0) or 0)
        turn = order[index] if order and 0 <= index < len(order) else "Unknown"
        defending = f" | Defending +{int(player.get('active_defense_ac_bonus', 0) or 0)} AC" if player.get("defending") else ""
        print("\n🏃 MOVEMENT HUD")
        print(f"Round {combat.get('round', 1)} | Position: ({x}, {y}) | Movement: {max(0, movement-used)}/{movement} | {resource_name}: {resource}/{max_resource} | Action: {action} | Turn: {turn}{defending}")

    enemies = [a for a in combatants if isinstance(a, dict) and a.get("team") == "enemy"]
    if enemies:
        entries = []
        for enemy in enemies:
            x, y = _position_xy(enemy)
            status = "DEFEATED" if enemy.get("defeated") else f"{int(enemy.get('hp', 0))}/{int(enemy.get('max_hp', enemy.get('hp', 0)))} HP"
            entries.append(f"{enemy.get('name', 'Enemy')}: {status} @ ({x}, {y})")
        print("🎯 TARGETS")
        print(" | ".join(entries))


def _print_combat_results(results, combat=None) -> None:
    if not isinstance(results, list):
        return
    for event in results:
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind == "combat_start":
            print("\n⚔️ COMBAT BEGINS")
            print("Initiative:", " → ".join(event.get("order", [])))
        elif kind in {"player_attack", "enemy_attack"}:
            hit = "HIT" if event.get("hit") else "MISS"
            print(f"\n⚔️ {event.get('attacker')} attacks {event.get('target')}")
            print(f"d20: {event.get('d20')} + {event.get('attack_bonus', 0)} = {event.get('attack_total')} vs AC {event.get('armor_class')} — {hit}")
            if event.get("hit"):
                crit = " CRITICAL!" if event.get("critical") else ""
                print(f"Damage: {event.get('damage')} | {event.get('target')} HP: {event.get('target_hp')}/{event.get('target_max_hp')}{crit}")
        elif kind in {"player_ability", "enemy_ability"}:
            print(f"\n✨ {event.get('actor')} uses {event.get('ability')} on {event.get('target')}")
            print(f"{event.get('resource_name', 'Resource')}: {event.get('resource_before')} → {event.get('resource_after')} (cost {event.get('resource_cost', 0)})")
            if event.get("requires_attack_roll"):
                hit = "HIT" if event.get("hit") else "MISS"
                print(f"d20: {event.get('d20')} + {event.get('attack_bonus', 0)} = {event.get('attack_total')} vs AC {event.get('armor_class')} — {hit}")
            if event.get("hit") and event.get("damage_rolls"):
                crit = " CRITICAL!" if event.get("critical") else ""
                print(f"Damage: {event.get('damage')} | {event.get('target')} HP: {event.get('target_hp')}/{event.get('target_max_hp')}{crit}")
        elif kind in {"player_defend", "enemy_defend"}:
            print(f"\n🛡️ {event.get('actor')} DEFENDS — +{event.get('defense_ac_bonus', 0)} AC")
        elif kind == "player_end_turn":
            print(f"\n⏭️ {event.get('actor', 'Player')} ends the turn.")
        elif kind == "invalid":
            print(f"\n⚠️ COMBAT ACTION INVALID: {event.get('reason', 'Unknown reason')}")
    _print_combat_hud(combat)


def main() -> None:
    print("=" * 48)
    print("THE SHATTERED REALMS — AI GAME MASTER")
    print("=" * 48)
    print("Type 'start game' to build a new character and begin a new adventure.")
    print("Type anything else to continue the current campaign. Type 'quit' to stop.\n")

    game_master = GameMaster()

    while True:
        action = input("What do you do? ").strip()
        lowered = action.lower()
        if lowered in {"quit", "exit"}:
            print("Campaign paused.")
            break
        if lowered in {"start game", "start new adventure", "new game", "new adventure"}:
            created = run_character_creation(game_master)
            player = created["player"]
            print("\n" + "=" * 48)
            print(f"{player.get('name')} — {player.get('class')}")
            print(f"HP: {player.get('hp')}/{player.get('max_hp')} | {player.get('resource_name')}: {player.get('resource')}/{player.get('max_resource')}")
            print("Abilities:", ", ".join(str(a.get("name")) for a in player.get("equipped_abilities", []) if isinstance(a, dict)))
            print("=" * 48)
            print("\n" + created.get("narration", "Your adventure begins.") + "\n")
            continue

        result = game_master.handle_action(action)
        check = result.get("roll")
        if isinstance(check, dict) and check.get("rolls"):
            rolled = check["rolls"][0]
            modifier = int(check.get("modifier", 0))
            sign = "+" if modifier >= 0 else "-"
            outcome = str(check.get("outcome", "")).replace("_", " ").upper()
            print(f"\n🎲 CHECK — {check.get('reason', 'Action')}\nd20: {rolled} {sign} {abs(modifier)} = {check.get('total')} vs DC {check.get('dc')}\nRESULT: {outcome}")

        _print_combat_results(result.get("combat_results"), result.get("combat"))
        print("\n" + result.get("narration", "The world waits...") + "\n")


if __name__ == "__main__":
    main()
