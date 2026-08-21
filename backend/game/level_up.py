"""Interactive Skill Point spending for level progression."""

from __future__ import annotations

from copy import deepcopy

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


def _print_stats(stats: dict, remaining: int) -> None:
    print("\nSKILL POINTS")
    print(f"Unspent SP: {remaining}")
    for index, name in enumerate(ATTRIBUTE_NAMES, 1):
        print(f"{index:>2}. {name.title():<14} {int(stats.get(name, 0))}")


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

    print("\n" + "=" * 48)
    print("SPEND SKILL POINTS")
    print("=" * 48)
    print("Enter a stat number or name, then choose how many SP to add.")
    print("Type 'done' to review/confirm, or 'cancel' to leave without spending anything.")

    while True:
        _print_stats(working, remaining)
        raw = input("\nStat to increase (or done/cancel): ").strip().lower()
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
            print(f"\nSP to spend now: {spent} | SP remaining afterward: {remaining}")
            if input("Confirm these upgrades? (yes/no): ").strip().lower() in {"yes", "y"}:
                break
            print("Keep editing your allocation.")
            continue

        if raw.isdigit():
            index = int(raw) - 1
            stat = ATTRIBUTE_NAMES[index] if 0 <= index < len(ATTRIBUTE_NAMES) else ""
        else:
            stat = raw.replace(" ", "_")
        if stat not in ATTRIBUTE_NAMES:
            print("Unknown stat.")
            continue
        current = int(working.get(stat, 0) or 0)
        room = NATURAL_ATTRIBUTE_CAP - current
        maximum = min(remaining, room)
        if maximum <= 0:
            print("That stat cannot be increased right now.")
            continue
        try:
            amount = int(input(f"Add how many SP to {stat.title()}? (1-{maximum}): ").strip())
        except ValueError:
            amount = 0
        if not 1 <= amount <= maximum:
            print("Invalid amount.")
            continue
        working[stat] = current + amount
        remaining -= amount

    old_hp = int(player.get("hp", 0) or 0)
    old_max_hp = int(player.get("max_hp", old_hp) or old_hp)
    old_resource = int(player.get("resource", player.get("mana", 0)) or 0)
    old_max_resource = int(player.get("max_resource", player.get("max_mana", old_resource)) or old_resource)
    hp_missing = max(0, old_max_hp - old_hp)
    resource_missing = max(0, old_max_resource - old_resource)

    player["stats"] = deepcopy(working)
    player["skill_points_unspent"] = remaining
    player["attribute_points_unspent"] = remaining  # legacy save compatibility
    state._migrate_player()

    # Increasing capacity does not magically erase existing damage/resource spent.
    player = state.data.setdefault("player", {})
    player["hp"] = max(0, int(player.get("max_hp", 0)) - hp_missing)
    player["resource"] = max(0, int(player.get("max_resource", 0)) - resource_missing)
    player["mana"] = player["resource"]
    state.save()

    print("\nUPGRADES SAVED")
    print(f"SP remaining: {remaining}")
    for name in ATTRIBUTE_NAMES:
        old = int(original_stats.get(name, 0) or 0)
        new = int(working.get(name, 0) or 0)
        if new != old:
            print(f"  {name.title()}: {old} -> {new}")
    _print_changes(before_sheet, _derived_summary(working, level, resource_name))
    return deepcopy(player)
