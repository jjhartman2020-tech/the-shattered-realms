"""Simple command-line entry point for testing the AI-first game runtime."""

from backend.ai.game_master import GameMaster


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
        print("\n" + result.get("narration", "The world waits...") + "\n")


if __name__ == "__main__":
    main()
