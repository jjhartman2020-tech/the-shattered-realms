"""Command-line entry point for testing The Shattered Realms runtime."""

from backend.ai.game_master import GameMaster
from backend.game.world_creation import run_world_creation
from backend.game.character_creation import run_character_creation
from backend.game.level_up import run_spending_screen
from backend.game.ability_learning import run_ap_spending_screen
from backend.game.armor_runtime import finish_character_creation_with_armor, install_armor_runtime
from backend.game.inventory import show_inventory, show_equipment, run_equipment_screen
from backend.game.economy import ensure_wallet, format_money, run_shop_screen, wallet_text
from backend.game.attributes import SKILL_ATTRIBUTE
from backend.game.combat import current_actor, end_turn


def _position_xy(actor) -> tuple[int, int]:
    position = actor.get("position") or {"x": 0, "y": 0}
    if isinstance(position, (list, tuple)) and len(position) >= 2:
        return int(position[0]), int(position[1])
    if isinstance(position, dict):
        return int(position.get("x", 0)), int(position.get("y", 0))
    return 0, 0


def _print_progress(player) -> None:
    print("\n📈 PROGRESSION")
    print(f"Level: {int(player.get('level', 1))}/100 | XP Orbs: {int(player.get('xp_orbs', 0))}/{int(player.get('xp_to_next_level', 0))}")
    print(f"Unspent SP: {int(player.get('skill_points_unspent', player.get('attribute_points_unspent', 0)) or 0)} | Stored AP: {int(player.get('ability_points', 0) or 0)}")


def _preview_stat(item: dict) -> str:
    raw = str(item.get("stat") or item.get("attribute") or item.get("skill") or "").strip().lower().replace(" ", "_")
    if raw in SKILL_ATTRIBUTE:
        raw = SKILL_ATTRIBUTE[raw]
    allowed = {"health", "resource", "strength", "dexterity", "agility", "constitution", "intelligence", "wisdom", "charisma", "speed", "defense", "luck", "magic"}
    return raw.title() if raw in allowed else "Core Stat"


def _ability_from_text(text: str, player: dict | None):
    if not isinstance(player, dict):
        return None
    lowered = text.lower()
    for ability in player.get("equipped_abilities", []) if isinstance(player.get("equipped_abilities"), list) else []:
        if not isinstance(ability, dict):
            continue
        name = str(ability.get("name") or "").strip()
        if name and name.lower() in lowered:
            return ability
    return None


def _combat_action_preview(text: str, player: dict | None) -> str | None:
    lowered = text.lower()
    ability = _ability_from_text(text, player)
    if ability is not None:
        if bool(ability.get("requires_attack_roll", False)):
            stat = str(ability.get("attack_attribute") or ability.get("damage_bonus_attribute") or "magic").replace("_", " ").title()
            return f" [ATTACK ROLL: {stat}]"
        return " [NO ATTACK ROLL]"
    attack_words = ("attack", "strike", "shoot", "slash", "stab", "swing", "hit ", "fire at", "blast", "punch", "kick")
    weapon = player.get("equipped_weapon") if isinstance(player, dict) and isinstance(player.get("equipped_weapon"), dict) else {}
    weapon_name = str(weapon.get("name") or "").strip().lower()
    if any(word in lowered for word in attack_words) or (weapon_name and weapon_name in lowered):
        stat = str(weapon.get("attack_attribute") or player.get("attack_attribute") or "strength").replace("_", " ").title() if isinstance(player, dict) else "Strength"
        return f" [ATTACK ROLL: {stat}]"
    return None


def _print_suggested_actions(result, player_state: dict | None = None) -> None:
    if not isinstance(result, dict):
        return
    suggestions = result.get("suggested_actions")
    if not isinstance(suggestions, list) or not suggestions:
        return
    combat = result.get("combat")
    combat_active = isinstance(combat, dict) and bool(combat.get("active"))
    print("Possible actions:")
    shown = 0
    for item in suggestions:
        if shown >= 3:
            break
        if isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            combat_preview = _combat_action_preview(text, player_state) if combat_active else None
            if combat_preview is not None:
                preview = combat_preview
            elif combat_active:
                preview = " [NO ATTACK ROLL]"
            else:
                preview = f" [ROLL: {_preview_stat(item)}]" if bool(item.get("requires_roll", False)) else " [NO ROLL EXPECTED]"
        else:
            text = str(item).strip()
            if not text:
                continue
            preview = _combat_action_preview(text, player_state) if combat_active else ""
            if combat_active and preview is None:
                preview = " [NO ATTACK ROLL]"
        shown += 1
        print(f"  {shown}. {text}{preview}")
    if shown:
        print("  Or type any other action you want.")


def _ability_summary(ability: dict, resource_name: str) -> str:
    parts = []
    if ability.get("damage"):
        parts.append(f"Damage {ability.get('damage')}")
    if ability.get("healing"):
        parts.append(f"Healing {ability.get('healing')}")
    if ability.get("shield"):
        parts.append(f"Shield {ability.get('shield')}")
    if ability.get("movement") is not None:
        parts.append(f"Move {ability.get('movement')} squares")
    if ability.get("range") is not None:
        parts.append(f"Range {ability.get('range')}")
    cost = ability.get("resource_cost", ability.get("cost"))
    if cost is not None:
        parts.append(f"Cost {cost} {resource_name}")
    description = str(ability.get("description") or ability.get("effect") or "").strip()
    mechanics = " | ".join(parts)
    if description:
        return f"{mechanics} — {description}" if mechanics else description
    return mechanics or "No description"


def _print_combat_hud(combat, player_state: dict | None = None) -> None:
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
        shield = int(player.get("shield_hp", 0) or 0)
        max_shield = int(player.get("max_shield_hp", 0) or 0)
        armor = int(player.get("armor", 0) or 0)
        max_armor = int(player.get("max_armor", 0) or 0)
        hp = int(player.get("hp", 0) or 0)
        max_hp = int(player.get("max_hp", hp) or hp)
        action = "USED" if player.get("primary_action_used") else "READY"
        order = combat.get("order") or []
        index = int(combat.get("turn_index", 0) or 0)
        turn = order[index] if order and 0 <= index < len(order) else "Unknown"
        defending = f" | Defending +{int(player.get('active_defense_ac_bonus', 0) or 0)} AC" if player.get("defending") else ""
        shield_text = f" | Shield: {shield}/{max_shield}" if max_shield > 0 else ""
        print("\n🏃 COMBAT HUD")
        print(f"Round {combat.get('round', 1)} | Position: ({x}, {y}) | Movement: {max(0, movement-used)}/{movement} | HP: {hp}/{max_hp}{shield_text} | Armor: {armor}/{max_armor} | {resource_name}: {resource}/{max_resource} | Action: {action} | Turn: {turn}{defending}")

        persistent = player_state if isinstance(player_state, dict) else {}
        weapon = persistent.get("equipped_weapon") if isinstance(persistent.get("equipped_weapon"), dict) else None
        if weapon:
            weapon_name = str(weapon.get("name") or "Weapon")
            damage = str(weapon.get("damage") or player.get("damage") or "?")
            attack_stat = str(weapon.get("attack_attribute") or player.get("attack_attribute") or "strength").title()
            range_value = weapon.get("range")
            range_text = f" | Range {range_value}" if range_value is not None else ""
            print(f"🗡️ WEAPON: {weapon_name} | Damage {damage}{range_text} | Attack stat: {attack_stat}")
        else:
            print(f"🗡️ WEAPON: Basic attack | Damage {player.get('damage', '?')}")

        abilities = persistent.get("equipped_abilities") if isinstance(persistent.get("equipped_abilities"), list) else player.get("abilities", [])
        print("✨ ABILITIES:")
        if isinstance(abilities, list) and abilities:
            for ability in abilities:
                if isinstance(ability, dict):
                    print(f"  - {ability.get('name', 'Ability')}: {_ability_summary(ability, resource_name)}")
        else:
            print("  - None equipped")

    enemies = [a for a in combatants if isinstance(a, dict) and a.get("team") == "enemy"]
    if enemies:
        entries = []
        for enemy in enemies:
            x, y = _position_xy(enemy)
            status = "DEFEATED" if enemy.get("defeated") else f"{int(enemy.get('hp', 0))}/{int(enemy.get('max_hp', enemy.get('hp', 0)))} HP"
            if int(enemy.get("max_shield_hp", 0) or 0) > 0:
                status += f", {int(enemy.get('shield_hp', 0) or 0)}/{int(enemy.get('max_shield_hp', 0) or 0)} Shield"
            if int(enemy.get("max_armor", 0) or 0) > 0:
                status += f", {int(enemy.get('armor', 0) or 0)}/{int(enemy.get('max_armor', 0) or 0)} Armor"
            entries.append(f"{enemy.get('name', 'Enemy')}: {status} @ ({x}, {y})")
        print("🎯 TARGETS")
        print(" | ".join(entries))


def _damage_dice_text(event: dict) -> str:
    rolls = event.get("damage_rolls")
    if not isinstance(rolls, list) or not rolls:
        return ""
    parts = []
    for entry in rolls:
        if not isinstance(entry, dict):
            continue
        expression = str(entry.get("expression") or "").strip()
        values = entry.get("rolls") if isinstance(entry.get("rolls"), list) else []
        if expression:
            rolled = "+".join(str(v) for v in values) if values else str(entry.get("total", "?"))
            parts.append(f"{expression}: {rolled}")
    return ", ".join(parts)


def _print_damage_result(event: dict) -> None:
    crit = " CRITICAL!" if event.get("critical") else ""
    damage = int(event.get("damage", 0) or 0)
    shield_absorbed = int(event.get("shield_absorbed", 0) or 0)
    armor_absorbed = int(event.get("armor_absorbed", 0) or 0)
    hp_damage = int(event.get("hp_damage", damage) or 0)
    dice_text = _damage_dice_text(event)
    dice_suffix = f" | Damage roll: {dice_text}" if dice_text else ""
    if "shield_after" in event or "armor_after" in event:
        print(f"Damage: {damage}{dice_suffix} | Shield absorbed: {shield_absorbed} | Armor absorbed: {armor_absorbed} | HP damage: {hp_damage}{crit}")
        status_parts = []
        if "shield_after" in event:
            status_parts.append(f"Shield: {int(event.get('shield_after', 0) or 0)}/{int(event.get('target_max_shield', 0) or 0)}")
        if "armor_after" in event:
            status_parts.append(f"Armor: {int(event.get('armor_after', 0) or 0)}/{int(event.get('target_max_armor', 0) or 0)}")
        status_parts.append(f"HP: {event.get('target_hp')}/{event.get('target_max_hp')}")
        print(" | ".join(status_parts))
        broken = event.get("broken_armor_pieces") or []
        if broken:
            print("BROKEN ARMOR: " + ", ".join(str(x) for x in broken))
    else:
        print(f"Damage: {damage}{dice_suffix} | Target HP: {event.get('target_hp')}/{event.get('target_max_hp')}{crit}")


def _print_combat_results(results, combat=None, player_state: dict | None = None) -> None:
    if isinstance(results, list):
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
                    _print_damage_result(event)
            elif kind in {"player_ability", "enemy_ability"}:
                print(f"\n✨ {event.get('actor')} uses {event.get('ability')} on {event.get('target')}")
                print(f"{event.get('resource_name', 'Resource')}: {event.get('resource_before')} → {event.get('resource_after')} (cost {event.get('resource_cost', 0)})")
                if event.get("requires_attack_roll"):
                    hit = "HIT" if event.get("hit") else "MISS"
                    print(f"d20: {event.get('d20')} + {event.get('attack_bonus', 0)} = {event.get('attack_total')} vs AC {event.get('armor_class')} — {hit}")
                if event.get("hit") and event.get("damage_rolls"):
                    _print_damage_result(event)
            elif kind in {"player_defend", "enemy_defend"}:
                print(f"\n🛡️ {event.get('actor')} DEFENDS — +{event.get('defense_ac_bonus', 0)} AC")
            elif kind == "player_end_turn":
                print(f"\n⏭️ {event.get('actor', 'Player')} ends the turn.")
            elif kind == "invalid":
                print(f"\n⚠️ COMBAT ACTION INVALID: {event.get('reason', 'Unknown reason')}")
    _print_combat_hud(combat, player_state)


def _format_check_sources(check) -> str:
    if not isinstance(check, dict):
        return ""
    parts = []
    attribute = str(check.get("attribute") or "").strip().replace("_", " ").title()
    skill = str(check.get("skill") or "").strip().replace("_", " ").title()
    attribute_bonus = int(check.get("attribute_bonus", 0) or 0)
    skill_bonus = int(check.get("skill_bonus", 0) or 0)
    if attribute:
        parts.append(f"{attribute} {attribute_bonus:+d}")
    if skill:
        parts.append(f"{skill} {skill_bonus:+d}")
    return ", ".join(parts)


def _direct_end_turn(game_master: GameMaster) -> bool:
    """End the player's combat turn without relying on the AI to interpret the command."""
    combat = game_master.state.data.get("combat")
    if not isinstance(combat, dict) or not combat.get("active"):
        return False
    actor = current_actor(combat)
    player = game_master.state.data.get("player", {})
    player_name = str(player.get("name") or "Traveler")
    if not actor or actor.get("name") != player_name:
        print("\nIt is not your turn right now.")
        _print_combat_hud(combat, player)
        return True
    results = [{"type": "player_end_turn", "actor": player_name}]
    end_turn(combat)
    results.extend(game_master._run_enemy_turns(combat))
    game_master._persist_combat(combat)
    _print_combat_results(results, combat, game_master.state.data.get("player", {}))
    return True


def _print_resume_recap(game_master: GameMaster) -> None:
    """Give a concise DM recap for an existing campaign resumed outside combat."""
    snapshot = game_master.state.snapshot()
    player = snapshot.get("player", {}) if isinstance(snapshot.get("player"), dict) else {}
    if not player.get("character_creation_complete"):
        return

    context = game_master.context_builder.build(
        player_action=(
            "Resume this existing campaign. Give me a QUICK recap only: where I am, what just happened, "
            "my current mission/objective, and the immediate situation. Do not advance time, resolve an action, "
            "invent a new event, or change any state. Use established campaign state and recent confirmed memories only."
        ),
        game_state=snapshot,
        memories=game_master.memory.recent(limit=18),
        rules=game_master.rules.retrieve("campaign recap current objective mission location continuity"),
    )
    context["resume_recap"] = True
    result = game_master.provider.respond(context)
    recap = str(result.get("narration") or "").strip() if isinstance(result, dict) else ""

    print("\n" + "=" * 52)
    print("🎬 CAMPAIGN RECAP")
    print("=" * 52)
    if recap:
        print(recap)
    else:
        location = str(player.get("location") or "your last known location")
        print(f"You resume your adventure at {location}.")

    hp = int(player.get("hp", 0) or 0)
    max_hp = int(player.get("max_hp", hp) or hp)
    shield = int(player.get("shield_hp", 0) or 0)
    max_shield = int(player.get("max_shield_hp", 0) or 0)
    armor = int(player.get("armor", 0) or 0)
    max_armor = int(player.get("max_armor", 0) or 0)
    resource_name = str(player.get("resource_name") or "Resource")
    resource = int(player.get("resource", player.get("mana", 0)) or 0)
    max_resource = int(player.get("max_resource", player.get("max_mana", resource)) or resource)
    level = int(player.get("level", 1) or 1)
    xp = int(player.get("xp_orbs", 0) or 0)
    xp_needed = int(player.get("xp_to_next_level", 0) or 0)
    sp = int(player.get("skill_points_unspent", player.get("attribute_points_unspent", 0)) or 0)
    ap = int(player.get("ability_points", 0) or 0)
    location = str(player.get("location") or "Unknown")
    weapon = player.get("equipped_weapon") if isinstance(player.get("equipped_weapon"), dict) else None
    wallet = ensure_wallet(game_master, grant_starting_funds=True)

    print("\n📍 CURRENT STATUS")
    print(f"Location: {location}")
    shield_text = f" | Shield: {shield}/{max_shield}" if max_shield > 0 else ""
    print(f"HP: {hp}/{max_hp}{shield_text} | Armor: {armor}/{max_armor} | {resource_name}: {resource}/{max_resource}")
    print(f"Money: {format_money(wallet.get('amount', 0), wallet)}")
    print(f"Level: {level}/100 | XP Orbs: {xp}/{xp_needed} | Stored SP: {sp} | Stored AP: {ap}")
    if weapon:
        print(f"Weapon: {weapon.get('name', 'Weapon')} | Damage {weapon.get('damage', '?')} | Range {weapon.get('range', '?')}")
    abilities = [str(a.get("name")) for a in player.get("equipped_abilities", []) if isinstance(a, dict) and a.get("name")]
    if abilities:
        print("Abilities: " + ", ".join(abilities))
    print("=" * 52 + "\n")


def main() -> None:
    print("=" * 48)
    print("THE SHATTERED REALMS — AI GAME MASTER")
    print("=" * 48)
    game_master = GameMaster()
    install_armor_runtime(game_master)

    saved_combat = game_master.state.data.get("combat")
    player_state = game_master.state.data.get("player", {})
    if isinstance(player_state, dict) and player_state.get("character_creation_complete"):
        ensure_wallet(game_master, grant_starting_funds=True)
    if isinstance(saved_combat, dict) and saved_combat.get("active"):
        print("\n⚔️ RESUMING ACTIVE COMBAT")
        _print_combat_hud(saved_combat, player_state)
        print()
    elif isinstance(player_state, dict) and player_state.get("character_creation_complete"):
        _print_resume_recap(game_master)
    else:
        print("Type 'start game' to create a world, build a character, and begin a new adventure.")
        print("Type 'progress' to view Level, XP Orbs, SP, and stored AP.")
        print("Type 'inventory' to view your items and equipped armor/gear. Type 'equipment' to view equipped gear only. Type 'equip' to swap gear.")
        print("Type 'wallet' to view your money. Type 'shop' when visiting a merchant.")
        print("Type 'spend sp' to upgrade stats. Type 'spend ap' to learn abilities. Type 'quit' to stop.\n")

    while True:
        action = input("What do you do? ").strip()
        lowered = action.lower()
        if lowered in {"quit", "exit"}:
            print("Campaign paused.")
            break
        if lowered == "progress":
            _print_progress(game_master.state.snapshot().get("player", {}))
            continue
        if lowered in {"inventory", "inv", "bag", "items"}:
            show_inventory(game_master)
            continue
        if lowered in {"equipment", "gear", "loadout", "show equipment"}:
            show_equipment(game_master.state.data.get("player", {}))
            continue
        if lowered in {"equip", "change equipment", "swap gear", "swap equipment"}:
            run_equipment_screen(game_master)
            continue
        if lowered in {"wallet", "money", "balance", "currency"}:
            print(f"\n💰 Balance: {wallet_text(game_master)}")
            continue
        if lowered in {"shop", "merchant", "store", "trade"}:
            run_shop_screen(game_master)
            continue
        if lowered in {"spend sp", "spend skill points", "upgrade stats", "level stats"}:
            player = run_spending_screen(game_master)
            _print_progress(player)
            continue
        if lowered in {"spend ap", "spend ability points", "learn ability", "learn abilities", "ability shop"}:
            player = run_ap_spending_screen(game_master)
            _print_progress(player)
            continue
        if lowered in {"end turn", "end my turn", "pass turn", "pass my turn"}:
            if _direct_end_turn(game_master):
                continue
        if lowered in {"start game", "start new adventure", "new game", "new adventure"}:
            game_master.state.reset_for_new_campaign()
            game_master.memory.clear()
            print("\nStarting a completely fresh campaign. Previous campaign state and memory were cleared.")
            world = run_world_creation(game_master)
            print(f"\nWorld confirmed: {world.get('name', 'Your World')}")
            print("Now create the character who will live in it.\n")
            created = run_character_creation(game_master)
            created = finish_character_creation_with_armor(game_master, created)
            player = created["player"]
            wallet = ensure_wallet(game_master, grant_starting_funds=True)
            print("\n" + "=" * 48)
            print(f"{player.get('name')} — {player.get('class')}")
            print(f"World: {world.get('name', 'Custom World')}")
            shield_text = f" | Shield: {player.get('shield_hp',0)}/{player.get('max_shield_hp',0)}" if int(player.get('max_shield_hp',0) or 0) > 0 else ""
            print(f"HP: {player.get('hp')}/{player.get('max_hp')}{shield_text} | Armor: {player.get('armor',0)}/{player.get('max_armor',0)} | {player.get('resource_name')}: {player.get('resource')}/{player.get('max_resource')}")
            print(f"Money: {format_money(wallet.get('amount', 0), wallet)}")
            _print_progress(player)
            print("Abilities:", ", ".join(str(a.get("name")) for a in player.get("equipped_abilities", []) if isinstance(a, dict)))
            print("=" * 48)
            print("\n" + created.get("narration", "Your adventure begins.") + "\n")
            _print_suggested_actions(created, player)
            continue

        before_player = game_master.state.snapshot().get("player", {})
        before_level = int(before_player.get("level", 1) or 1)
        result = game_master.handle_action(action)
        check = result.get("roll")
        if isinstance(check, dict) and check.get("rolls"):
            rolled = check["rolls"][0]
            modifier = int(check.get("modifier", 0) or 0)
            sign = "+" if modifier >= 0 else "-"
            outcome = str(check.get("outcome", "")).replace("_", " ").upper()
            sources = _format_check_sources(check)
            source_text = f" ({sources})" if sources else ""
            skill = str(check.get("skill") or "").strip().replace("_", " ").title()
            attribute = str(check.get("attribute") or "").strip().replace("_", " ").title()
            check_label = skill or attribute or "General check"
            print(f"\n🎲 CHECK — {check.get('reason', 'Action')}")
            print(f"Using: {check_label}" + (f" ({attribute})" if skill and attribute else ""))
            print(f"d20: {rolled} {sign} {abs(modifier)}{source_text} = {check.get('total')} vs DC {check.get('dc')}")
            print(f"RESULT: {outcome}")

        after_player = game_master.state.snapshot().get("player", {})
        combat_for_hud = result.get("combat")
        if not isinstance(combat_for_hud, dict):
            combat_for_hud = game_master.state.data.get("combat")
        _print_combat_results(result.get("combat_results"), combat_for_hud, after_player)

        if int(after_player.get("level", 1) or 1) > before_level:
            print("\n⬆️ LEVEL UP!")
            _print_progress(after_player)
            print("Your SP and AP are stored. Spend them now or save them for later with 'spend sp' / 'spend ap'.")
        print("\n" + result.get("narration", "The world waits...") + "\n")
        _print_suggested_actions(result, after_player)
        print()


if __name__ == "__main__":
    main()
