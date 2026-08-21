"""Interactive Skill Point spending for level progression."""

from __future__ import annotations

from copy import deepcopy
import re

from .attributes import ATTRIBUTE_NAMES, NATURAL_ATTRIBUTE_CAP, character_sheet_channels


def _derived_summary(stats: dict, level: int, resource_name: str) -> dict:
    sheet = character_sheet_channels(stats, level)
    return {
        "Max HP": int(sheet["max_health_base"]),
        f"Max {resource_name}": int(sheet["max_resource_base"]),
        f"{resource_name} Regen/Round": int(sheet["resource_regeneration_per_round"]),
        "Movement": int(sheet["movement"]),
        "Initiative Bonus": int(sheet["initiative_bonus"]),
        "Critical Chance": int(sheet["critical_chance_percent"]),
        "Physical Resistance": int(sheet["physical_resistance_percent"]),
        "Status Resistance": int(sheet["status_resistance_percent"]),
        "Defend AC Bonus": int(sheet["defend_action_ac_bonus"]),
    }


def _print_full_build(stats: dict, remaining: int) -> None:
    print("\n" + "=" * 48)
    print("CURRENT 13-STAT BUILD")
    print(f"Unspent SP: {remaining}")
    print("=" * 48)
    for name in ATTRIBUTE_NAMES:
        print(f"  {name.title():<14} {int(stats.get(name, 0))}")


def _print_changes(before: dict, after: dict) -> None:
    changed = False
    print("\nDERIVED CHANGES")
    for key, old_value in before.items():
        new_value = after[key]
        if new_value != old_value:
            changed = True
            suffix = "%" if "Chance" in key or "Resistance" in key else ""
            sign = "+" if new_value - old_value >= 0 else ""
            print(f"  {key}: {old_value}{suffix} -> {new_value}{suffix} ({sign}{new_value-old_value}{suffix})")
    if not changed:
        print("  No derived breakpoint changed yet. The raw stat increase still counts toward future scaling.")


def _parse_sp_command(raw: str) -> tuple[str | None, int | None]:
    """Parse commands like 'speed,3 sp', 'speed 3', or 'magic, 2'."""
    cleaned = raw.strip().lower().replace("skill points", "sp").replace("skill point", "sp")
    match = re.fullmatch(r"\s*([a-z_ ]+)\s*[, ]+\s*(\d+)\s*(?:sp)?\s*", cleaned)
    if not match:
        return None, None
    stat = match.group(1).strip().replace(" ", "_")
    amount = int(match.group(2))
    return stat, amount


def run_spending_screen(game_master) -> dict:
    """Spend any amount of banked SP outside combat and persist the resulting build."""
    state = game_master.state
    player = state.data.setdefault("player", {})
    combat = state.data.get("combat")
    if isinstance(combat, dict) and combat.get("active"):
        print("\nYou cannot spend SP during active combat. Finish the battle first.")
        return deepcopy(player)

    available = max(0, int(player.get("skill_points_unspent", 0) or 0))
    if available <= 0:
        print("\nYou do not have any unspent SP.")
        return deepcopy(player)

    level = max(1, int(player.get("level", 1) or 1))
    resource_name = str(player.get("resource_name") or "Resource")
    original_stats = deepcopy(player.get("stats") or {})
    working = deepcopy(original_stats)
    remaining = available
    before_sheet = _derived_summary(original_stats, level, resource_name)

    print("\nSPEND SKILL POINTS")
    print("Enter upgrades in one line, for example: speed,3 sp")
    print("You may spend some SP and save the rest. Type 'done' to review or 'cancel' to leave without spending.")

    while True:
        _print_full_build(working, remaining)
        raw = input("\nWhat do you spend SP on? (example: speed,3 sp): ").strip().lower()
        if raw in {"cancel", "quit", "exit"}:
            print("No SP spent.")
            return deepcopy(player)
        if raw in {"done", "confirm"}:
            spent = available - remaining
            if spent <= 0:
                print("You have not allocated any SP yet.")
                continue
            after_sheet = _derived_summary(working, level, resource_name)
            _print_changes(before_sheet, after_sheet)
            print(f"\nSP to spend now: {spent} | SP saved for later: {remaining}")
            if input("Confirm these upgrades? (yes/no): ").strip().lower() in {"yes", "y"}:
                break
            print("Keep editing your allocation.")
            continue

        stat, amount = _parse_sp_command(raw)
        if stat not in ATTRIBUTE_NAMES or amount is None:
            print("Use the format 'stat,amount sp' — for example: speed,3 sp")
            continue
        current = int(working.get(stat, 0) or 0)
        room = NATURAL_ATTRIBUTE_CAP - current
        maximum = min(remaining, room)
        if maximum <= 0:
            print(f"{stat.title()} cannot be increased right now.")
            continue
        if amount < 1 or amount > maximum:
            print(f"You can add 1-{maximum} SP to {stat.title()} right now.")
            continue
        working[stat] = current + amount
        remaining -= amount
        print(f"Queued: {stat.title()} {current} -> {working[stat]} ({amount} SP)")

    old_hp = int(player.get("hp", 0) or 0)
    old_max_hp = int(player.get("max_hp", old_hp) or old_hp)
    old_resource = int(player.get("resource", player.get("mana", 0)) or 0)
    old_max_resource = int(player.get("max_resource", player.get("max_mana", old_resource)) or old_resource)
    hp_missing = max(0, old_max_hp - old_hp)
    resource_missing = max(0, old_max_resource - old_resource)

    player["stats"] = deepcopy(working)
    player["skill_points_unspent"] = remaining
    player["attribute_points_unspent"] = remaining
    state._migrate_player()

    player = state.data.setdefault("player", {})
    player["hp"] = max(0, int(player.get("max_hp", 0)) - hp_missing)
    player["resource"] = max(0, int(player.get("max_resource", 0)) - resource_missing)
    player["mana"] = player["resource"]
    state.save()

    print("\nUPGRADES SAVED")
    _print_full_build(working, remaining)
    _print_changes(before_sheet, _derived_summary(working, level, resource_name))
    return deepcopy(player)
