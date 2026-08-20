"""Simple command-line entry point for testing the AI-first game runtime."""

from backend.ai.game_master import GameMaster


def _print_combat_results(results) -> None:
    if not isinstance(results, list):
        return
    for event in results:
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        if event_type == "combat_start":
            print("\n⚔️ COMBAT BEGINS")
            print("Initiative:", " → ".join(event.get("order", [])))
        elif event_type in {"player_attack", "enemy_attack"}:
            attacker = event.get("attacker", "Attacker")
            target = event.get("target", "Target")
            d20 = event.get("d20")
            bonus = int(event.get("attack_bonus", 0))
            total = event.get("attack_total")
            ac = event.get("armor_class")
            sign = "+" if bonus >= 0 else "-"
            hit_text = "HIT" if event.get("hit") else "MISS"
            print(f"\n⚔️ {attacker} attacks {target}")
            print(f"d20: {d20} {sign} {abs(bonus)} = {total} vs AC {ac} — {hit_text}")
            if event.get("hit"):
                crit = " CRITICAL!" if event.get("critical") else ""
                print(
                    f"Damage: {event.get('damage')} | {target} HP: "
                    f"{event.get('target_hp')}/{event.get('target_max_hp')}{crit}"
                )
                if event.get("target_defeated"):
                    print(f"{target} is defeated.")
        elif event_type == "enemy_pass":
            print(f"\n⚔️ {event.get('actor', 'Enemy')} takes no attack action.")
        elif event_type == "invalid":
            print(f"\n⚠️ COMBAT ACTION INVALID: {event.get('reason', 'Unknown reason')}")


def main() -> None:
    print("=" * 48)
    print("THE SHATTERED REALMS — AI GAME MASTER")
    print("=" * 48)
    print("Type anything your character attempts. Type 'quit' to stop.\n")

    game_master = GameMaster()

    while True:
        action = input("What do you do? ").strip()
        if action.lower() in {"quit", "exit"}:
            print("Campaign paused.")
            break

        result = game_master.handle_action(action)
        check = result.get("roll")
        if isinstance(check, dict) and check.get("rolls"):
            rolled = check["rolls"][0]
            modifier = int(check.get("modifier", 0))
            total = check.get("total")
            dc = check.get("dc")
            outcome = str(check.get("outcome", "")).replace("_", " ").upper()
            sign = "+" if modifier >= 0 else "-"
            print(
                f"\n🎲 CHECK — {check.get('reason', 'Action')}\n"
                f"d20: {rolled} {sign} {abs(modifier)} = {total} vs DC {dc}\n"
                f"RESULT: {outcome}"
            )

        _print_combat_results(result.get("combat_results"))
        print("\n" + result.get("narration", "The world waits...") + "\n")


if __name__ == "__main__":
    main()
