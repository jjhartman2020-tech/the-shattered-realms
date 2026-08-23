"""Local JSON API used by the Godot client.

Run with:
    python -m backend.api

The Python backend stays authoritative. Godot only sends player actions and
renders the returned state/result.
"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
from typing import Any, Dict

from backend.ai.game_master import GameMaster
from backend.game.armor_runtime import install_armor_runtime
from backend.game.combat import current_actor, end_turn
from backend.game.economy import ensure_wallet, format_money

HOST = os.getenv("SHATTERED_REALMS_API_HOST", "127.0.0.1")
PORT = int(os.getenv("SHATTERED_REALMS_API_PORT", "8765"))

GAME_MASTER = GameMaster()
install_armor_runtime(GAME_MASTER)
LOCK = threading.RLock()


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return json.loads(json.dumps(value, default=str))


def _resume_text(state: Dict) -> str:
    player = state.get("player", {}) if isinstance(state.get("player"), dict) else {}
    if not player.get("character_creation_complete"):
        return "No completed character is saved yet. Character creation UI is coming next."

    name = str(player.get("name") or "Traveler")
    location = str(player.get("location") or "Unknown location")
    combat = state.get("combat") if isinstance(state.get("combat"), dict) else {}
    if combat.get("active"):
        actor = current_actor(combat)
        turn_text = str(actor.get("name")) if isinstance(actor, dict) else "unknown"
        return f"{name} resumes an active fight at {location}. Current turn: {turn_text}."

    objective = "Continue your current lead."
    quests = state.get("quests") if isinstance(state.get("quests"), dict) else {}
    for quest in quests.values():
        if not isinstance(quest, dict):
            continue
        status = str(quest.get("status") or "active").lower()
        if status in {"complete", "completed", "failed", "inactive"}:
            continue
        objective = str(quest.get("objective") or quest.get("name") or objective)
        break
    return f"{name} resumes at {location}. Current objective: {objective}"


def _session_payload() -> Dict:
    state = GAME_MASTER.state.snapshot()
    player = state.get("player", {}) if isinstance(state.get("player"), dict) else {}
    if player.get("character_creation_complete"):
        wallet = ensure_wallet(GAME_MASTER, grant_starting_funds=True)
        state = GAME_MASTER.state.snapshot()
        money = format_money(wallet.get("amount", 0), wallet)
    else:
        money = "0"
    return {
        "ok": True,
        "narration": _resume_text(state),
        "suggested_actions": [],
        "state": state,
        "money_text": money,
    }


def _direct_end_turn() -> Dict | None:
    combat = GAME_MASTER.state.data.get("combat")
    if not isinstance(combat, dict) or not combat.get("active"):
        return None
    player = GAME_MASTER.state.data.get("player", {})
    player_name = str(player.get("name") or "Traveler")
    actor = current_actor(combat)
    if not actor or actor.get("name") != player_name:
        return {
            "narration": "It is not your turn right now.",
            "suggested_actions": [],
            "combat": combat,
            "combat_results": [],
            "state": GAME_MASTER.state.snapshot(),
        }
    events = [{"type": "player_end_turn", "actor": player_name}]
    end_turn(combat)
    events.extend(GAME_MASTER._run_enemy_turns(combat))
    GAME_MASTER._persist_combat(combat)
    return {
        "narration": "You end your turn. The battle advances.",
        "suggested_actions": [],
        "combat": combat,
        "combat_results": events,
        "state": GAME_MASTER.state.snapshot(),
    }


def _handle_action(action: str) -> Dict:
    clean = str(action or "").strip()
    if not clean:
        return {"ok": False, "error": "Action cannot be empty."}
    lowered = clean.lower()
    if lowered in {"end turn", "end my turn", "pass turn", "pass my turn"}:
        direct = _direct_end_turn()
        if direct is not None:
            direct["ok"] = True
            return direct
    result = GAME_MASTER.handle_action(clean)
    result["ok"] = True
    return _json_safe(result)


class Handler(BaseHTTPRequestHandler):
    server_version = "ShatteredRealmsAPI/0.1"

    def _send(self, status: int, payload: Dict) -> None:
        body = json.dumps(_json_safe(payload), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length > 0 else b"{}"
        parsed = json.loads(raw.decode("utf-8") or "{}")
        return parsed if isinstance(parsed, dict) else {}

    def do_GET(self) -> None:  # noqa: N802
        try:
            with LOCK:
                if self.path == "/health":
                    self._send(200, {"ok": True, "service": "the-shattered-realms"})
                    return
                if self.path in {"/", "/session", "/state"}:
                    self._send(200, _session_payload())
                    return
            self._send(404, {"ok": False, "error": "Not found."})
        except Exception as exc:  # pragma: no cover - user-facing dev server guard
            self._send(500, {"ok": False, "error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path != "/action":
                self._send(404, {"ok": False, "error": "Not found."})
                return
            payload = self._read_json()
            with LOCK:
                result = _handle_action(str(payload.get("action") or ""))
            self._send(200 if result.get("ok") else 400, result)
        except json.JSONDecodeError:
            self._send(400, {"ok": False, "error": "Invalid JSON body."})
        except Exception as exc:  # pragma: no cover - user-facing dev server guard
            self._send(500, {"ok": False, "error": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[Godot API] {self.address_string()} - {fmt % args}")


def main() -> None:
    print("=" * 52)
    print("THE SHATTERED REALMS — GODOT BACKEND API")
    print("=" * 52)
    print(f"Listening on http://{HOST}:{PORT}")
    print("Leave this running while the Godot client is open.\n")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
