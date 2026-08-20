"""One-shot smoke test for the live Shattered Realms AI provider."""

import os

from backend.ai.provider import OpenAIProvider


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not available in this Codespace.")

    provider = OpenAIProvider()
    result = provider.respond(
        {
            "player_action": "I open the old tavern door and look inside.",
            "game_state": {
                "location": "Abandoned Tavern",
                "player": {"hp": 10, "inventory": []},
            },
            "relevant_memories": [],
            "relevant_rules": [
                "Preserve player agency.",
                "Do not invent unsupported facts.",
                "Use logical cause and effect.",
            ],
        }
    )

    print("\n=== LIVE AI TEST ===\n")
    print(result.get("narration", "No narration returned."))
    print("\nProvider:", result.get("debug", {}).get("provider"))
    print("Model:", result.get("debug", {}).get("model"))


if __name__ == "__main__":
    main()
