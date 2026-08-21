"""Command-line entry point for testing The Shattered Realms runtime."""

from backend.ai.game_master import GameMaster
from backend.game.world_creation import run_world_creation
from backend.game.character_creation import run_character_creation
from backend.game.level_up import run_spending_screen
from backend.game.ability_learning import run_ap_spending_screen


def _position_xy(actor) -> tuple[int, int]:
    position = actor.get("position") or {"x": 0, "y": 0}
    if isinstance(position, (list, tuple)) and len(position) >= 2: return int(position[0]), int(position[1])
    if isinstance(position, dict): return int(position.get("x", 0)), int(position.get("y", 0))
    return 0, 0


def _print_progress(player) -> None:
    print("\n📈 PROGRESSION")
    print(f"Level: {int(player.get('level', 1))}/100 | XP Orbs: {int(player.get('xp_orbs', 0))}/{int(player.get('xp_to_next_level', 0))}")
    print(f"Unspent SP: {int(player.get('skill_points_unspent', player.get('attribute_points_unspent', 0)) or 0)} | Stored AP: {int(player.get('ability_points', 0) or 0)}")


def _print_suggested_actions(result) -> None:
    if not isinstance(result, dict):
        return
    suggestions = result.get("suggested_actions")
    if not isinstance(suggestions, list):
        return
    suggestions = [str(item).strip() for item in suggestions if str(item).strip()][:3]
    if not suggestions:
        return
    print("Possible actions:")
    for index, suggestion in enumerate(suggestions, 1):
        print(f"  {index}. {suggestion}")
    print("  Or type any other action you want.")


def _print_combat_hud(combat) -> None:
    if not isinstance(combat, dict) or not combat.get("active"): return
    combatants = combat.get("combatants") or []
    player = next((a for a in combatants if isinstance(a, dict) and a.get("team") == "player"), None)
    if player:
        movement = int(player.get("movement", 0) or 0); used = int(player.get("movement_used", 0) or 0)
        x, y = _position_xy(player)
        resource_name = str(player.get("resource_name") or "Resource")
        resource = int(player.get("resource", player.get("mana", 0)) or 0)
        max_resource = int(player.get("max_resource", player.get("max_mana", resource)) or resource)
        action = "USED" if player.get("primary_action_used") else "READY"
        order = combat.get("order") or []; index = int(combat.get("turn_index", 0) or 0)
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
        print("🎯 TARGETS"); print(" | ".join(entries))


def _print_combat_results(results, combat=None) -> None:
    if not isinstance(results, list): return
    for event in results:
        if not isinstance(event, dict): continue
        kind = event.get("type")
        if kind == "combat_start":
            print("\n⚔️ COMBAT BEGINS"); print("Initiative:", " → ".join(event.get("order", [])))
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
        elif kind == "player_end_turn": print(f"\n⏭️ {event.get('actor', 'Player')} ends the turn.")
        elif kind == "invalid": print(f"\n⚠️ COMBAT ACTION INVALID: {event.get('reason', 'Unknown reason')}")
    _print_combat_hud(combat)


def main() -> None:
    print("=" * 48); print("THE SHATTERED REALMS — AI GAME MASTER"); print("=" * 48)
    print("Type 'start game' to create a world, build a character, and begin a new adventure.")
    print("Type 'progress' to view Level, XP Orbs, SP, and stored AP.")
    print("Type 'spend sp' to upgrade stats. Type 'spend ap' to learn abilities. Type 'quit' to stop.\n")
    game_master = GameMaster()

    while True:
        action = input("What do you do? ").strip(); lowered = action.lower()
        if lowered in {"quit", "exit"}:
            print("Campaign paused."); break
        if lowered == "progress":
            _print_progress(game_master.state.snapshot().get("player", {})); continue
        if lowered in {"spend sp", "spend skill points", "upgrade stats", "level stats"}:
            player = run_spending_screen(game_master); _print_progress(player); continue
        if lowered in {"spend ap", "spend ability points", "learn ability", "learn abilities", "ability shop"}:
            player = run_ap_spending_screen(game_master); _print_progress(player); continue
        if lowered in {"start game", "start new adventure", "new game", "new adventure"}:
            game_master.state.reset_for_new_campaign()
            game_master.memory.clear()
            print("\nStarting a completely fresh campaign. Previous campaign state and memory were cleared.")

            world = run_world_creation(game_master)
            print(f"\nWorld confirmed: {world.get('name', 'Your World')}")
            print("Now create the character who will live in it.\n")
            created = run_character_creation(game_master); player = created["player"]
            print("\n" + "=" * 48); print(f"{player.get('name')} — {player.get('class')}")
            print(f"World: {world.get('name', 'Custom World')}")
            print(f"HP: {player.get('hp')}/{player.get('max_hp')} | {player.get('resource_name')}: {player.get('resource')}/{player.get('max_resource')}")
            _print_progress(player)
            print("Abilities:", ", ".join(str(a.get("name")) for a in player.get("equipped_abilities", []) if isinstance(a, dict)))
            print("=" * 48); print("\n" + created.get("narration", "Your adventure begins.") + "\n")
            _print_suggested_actions(created)
            continue

        before_player = game_master.state.snapshot().get("player", {})
        before_level = int(before_player.get("level", 1) or 1)
        result = game_master.handle_action(action)
        check = result.get("roll")
        if isinstance(check, dict) and check.get("rolls"):
            rolled = check["rolls"][0]; modifier = int(check.get("modifier", 0)); sign = "+" if modifier >= 0 else "-"
            outcome = str(check.get("outcome", "")).replace("_", " ").upper()
            print(f"\n🎲 CHECK — {check.get('reason', 'Action')}\nd20: {rolled} {sign} {abs(modifier)} = {check.get('total')} vs DC {check.get('dc')}\nRESULT: {outcome}")
        _print_combat_results(result.get("combat_results"), result.get("combat"))
        after_player = game_master.state.snapshot().get("player", {})
        if int(after_player.get("level", 1) or 1) > before_level:
            print("\n⬆️ LEVEL UP!"); _print_progress(after_player)
            print("Your SP and AP are stored. Spend them now or save them for later with 'spend sp' / 'spend ap'.")
        print("\n" + result.get("narration", "The world waits...") + "\n")
        _print_suggested_actions(result)
        print()


if __name__ == "__main__":
    main()
