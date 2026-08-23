"""Authoritative mutations used by the Godot Character Hub."""

from __future__ import annotations

import base64
from copy import deepcopy
import os
from pathlib import Path
from typing import Dict

from .armor import ARMOR_SLOTS, effective_movement, normalize_armor_piece, sync_armor_summary
from .attributes import ATTRIBUTE_NAMES, NATURAL_ATTRIBUTE_CAP


def _player(game_master) -> Dict:
    player = game_master.state.data.get("player")
    if not isinstance(player, dict) or not player.get("character_creation_complete"):
        raise ValueError("Finish character creation before opening the Character Hub.")
    return player


def _require_outside_combat(game_master) -> None:
    combat = game_master.state.data.get("combat")
    if isinstance(combat, dict) and combat.get("active"):
        raise ValueError("Character upgrades and equipment changes are locked during combat.")


def spend_stat_point(game_master, stat: str, amount: int = 1) -> Dict:
    """Spend banked SP on one core stat without healing through the upgrade."""
    _require_outside_combat(game_master)
    player = _player(game_master)
    stat_name = str(stat or "").strip().lower()
    if stat_name not in ATTRIBUTE_NAMES:
        raise ValueError("Choose one of the 13 core stats.")
    points = max(1, int(amount or 1))
    available = max(0, int(player.get("skill_points_unspent", 0) or 0))
    if points > available:
        raise ValueError(f"You need {points} SP but only have {available}.")

    stats = deepcopy(player.get("stats")) if isinstance(player.get("stats"), dict) else {}
    current = max(0, int(stats.get(stat_name, 0) or 0))
    if current + points > NATURAL_ATTRIBUTE_CAP:
        raise ValueError(f"{stat_name.title()} cannot exceed {NATURAL_ATTRIBUTE_CAP}.")

    old_hp = int(player.get("hp", 0) or 0)
    old_max_hp = int(player.get("max_hp", old_hp) or old_hp)
    old_resource = int(player.get("resource", player.get("mana", 0)) or 0)
    old_max_resource = int(player.get("max_resource", player.get("max_mana", old_resource)) or old_resource)
    hp_missing = max(0, old_max_hp - old_hp)
    resource_missing = max(0, old_max_resource - old_resource)

    stats[stat_name] = current + points
    remaining = available - points
    player["stats"] = stats
    player["skill_points_unspent"] = remaining
    player["attribute_points_unspent"] = remaining
    game_master.state._migrate_player()

    player = game_master.state.data["player"]
    player["hp"] = max(0, int(player.get("max_hp", 0) or 0) - hp_missing)
    player["resource"] = max(0, int(player.get("max_resource", 0) or 0) - resource_missing)
    player["mana"] = player["resource"]
    game_master.state.save()
    return {
        "stat": stat_name,
        "before": current,
        "after": int(player.get("stats", {}).get(stat_name, current + points)),
        "spent": points,
        "skill_points_remaining": int(player.get("skill_points_unspent", 0) or 0),
    }


def equip_armor_from_inventory(game_master, inventory_index: int) -> Dict:
    """Equip one owned armor item by its zero-based inventory index."""
    _require_outside_combat(game_master)
    player = _player(game_master)
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    index = int(inventory_index)
    if index < 0 or index >= len(inventory):
        raise ValueError("That inventory item is no longer available.")
    raw_item = inventory[index]
    if not isinstance(raw_item, dict) or str(raw_item.get("type") or "").strip().lower() != "armor":
        raise ValueError("Choose an armor piece from your inventory.")

    piece = normalize_armor_piece(raw_item)
    equipped = deepcopy(player.get("equipped_armor")) if isinstance(player.get("equipped_armor"), dict) else {}
    replaced = deepcopy(equipped.get(piece["slot"])) if isinstance(equipped.get(piece["slot"]), dict) else None
    if replaced and str(replaced.get("name") or "").strip().lower() == str(piece.get("name") or "").strip().lower():
        raise ValueError(f"{piece.get('name', 'That armor')} is already equipped.")
    if replaced:
        _sync_owned_armor(inventory, replaced)
    equipped[piece["slot"]] = piece
    player["equipped_armor"] = equipped
    player["armor_set_name"] = "Mixed Set"
    totals = sync_armor_summary(player)
    base_movement = int(player.get("base_movement_without_armor", player.get("movement", 1)) or 1)
    player["base_movement_without_armor"] = base_movement
    player["movement"] = effective_movement(base_movement, equipped)
    game_master.state.save()
    return {
        "equipped": deepcopy(piece), "replaced": replaced,
        "armor": totals["armor"], "max_armor": totals["max_armor"],
        "weight": totals["weight"], "movement": int(player.get("movement", 1) or 1),
    }


def unequip_armor_slot(game_master, slot: str) -> Dict:
    """Clear one armor slot; owned items remain visible in inventory."""
    _require_outside_combat(game_master)
    player = _player(game_master)
    slot_name = str(slot or "").strip().lower()
    if slot_name not in ARMOR_SLOTS:
        raise ValueError("Choose a valid armor slot.")
    equipped = deepcopy(player.get("equipped_armor")) if isinstance(player.get("equipped_armor"), dict) else {}
    removed = equipped.pop(slot_name, None)
    if not isinstance(removed, dict):
        raise ValueError(f"The {slot_name.title()} slot is already empty.")
    inventory = player.get("inventory") if isinstance(player.get("inventory"), list) else []
    _sync_owned_armor(inventory, removed)
    player["equipped_armor"] = equipped
    player["armor_set_name"] = "Mixed Set" if equipped else None
    totals = sync_armor_summary(player)
    base_movement = int(player.get("base_movement_without_armor", player.get("movement", 1)) or 1)
    player["movement"] = effective_movement(base_movement, equipped)
    game_master.state.save()
    return {
        "unequipped": deepcopy(removed), "slot": slot_name,
        "armor": totals["armor"], "max_armor": totals["max_armor"],
        "weight": totals["weight"], "movement": int(player.get("movement", 1) or 1),
    }


def _sync_owned_armor(inventory: list, piece: Dict) -> None:
    """Keep a worn piece's current durability when it returns to inventory."""
    target_name = str(piece.get("name") or "").strip().lower()
    target_slot = str(piece.get("slot") or "").strip().lower()
    for index, item in enumerate(inventory):
        if not isinstance(item, dict) or str(item.get("type") or "").strip().lower() != "armor":
            continue
        if str(item.get("name") or "").strip().lower() != target_name:
            continue
        if str(item.get("slot") or "").strip().lower() != target_slot:
            continue
        inventory[index] = deepcopy(piece)
        return


def cached_character_portrait(output_path: Path) -> str:
    """Return the cached PNG as base64, or an empty string if none exists."""
    try:
        if output_path.is_file():
            return base64.b64encode(output_path.read_bytes()).decode("ascii")
    except OSError:
        pass
    return ""


def generate_character_portrait(
    game_master,
    output_path: Path,
    *,
    changed_slot: str = "",
    change_type: str = "",
) -> str:
    """Generate or edit cached full-body art from authoritative equipped armor."""
    player = _player(game_master)
    client = getattr(game_master.provider, "client", None)
    if client is None or not hasattr(client, "images"):
        raise ValueError("Character art needs OPENAI_API_KEY. Set it, then restart python -m backend.api.")

    world = game_master.state.data.get("world_profile")
    if not isinstance(world, dict):
        world = game_master.state.data.get("world") if isinstance(game_master.state.data.get("world"), dict) else {}
    equipped = player.get("equipped_armor") if isinstance(player.get("equipped_armor"), dict) else {}
    armor_details = []
    for slot in ARMOR_SLOTS:
        piece = equipped.get(slot)
        if isinstance(piece, dict):
            armor_details.append(
                f"{slot.upper()}: EQUIPPED — unique item '{piece.get('name', 'armor')}'. "
                f"Visual design: {piece.get('description', 'invent a distinct design matching its exact name and setting')}"
            )
        else:
            armor_details.append(
                f"{slot.upper()}: EMPTY — show normal clothing/body at this slot and remove any armor piece previously shown there"
            )

    change_instruction = ""
    normalized_slot = str(changed_slot or "").strip().lower()
    normalized_change = str(change_type or "").strip().lower()
    if normalized_slot in ARMOR_SLOTS:
        if normalized_change == "unequip":
            change_instruction = (
                f"IMPORTANT CURRENT EDIT: the {normalized_slot} was just UNEQUIPPED. Completely remove the old "
                f"{normalized_slot} armor while leaving the character's identity and unrelated slots unchanged."
            )
        elif normalized_change == "equip":
            current_piece = equipped.get(normalized_slot, {})
            change_instruction = (
                f"IMPORTANT CURRENT EDIT: the {normalized_slot} was just changed to "
                f"'{current_piece.get('name', 'the newly equipped item')}'. Completely replace the previous "
                f"{normalized_slot} design with this new item's visibly different silhouette, materials, colors, and details."
            )

    prompt = f"""Create original full-body character concept art for a text RPG character screen.
Show one fully clothed character, head to toe, in a neutral readable pose on a simple atmospheric background. No text, labels, UI, logos, gore, or sexualized presentation. Keep the design suitable for a teen-rated adventure game. If the description names an existing copyrighted character, reinterpret the idea into a clearly original design rather than copying that character.

Character name: {player.get('name', 'Traveler')}
Species: {player.get('species', 'unspecified')}
Class/build: {player.get('class', 'unassigned')}
Saved appearance: {player.get('appearance', 'Use a distinctive original adventurer design.')}
World name/genre: {world.get('name', world.get('title', 'The Shattered Realms'))} / {world.get('genre', world.get('setting', 'adaptive fantasy and science fiction'))}
World visual direction: {world.get('description', world.get('summary', world.get('tone', 'Match the established game world.')))}
AUTHORITATIVE ARMOR SLOTS (follow every slot exactly):
{chr(10).join(armor_details)}
{change_instruction}

Use polished, detailed, colorful digital illustration with a strong readable silhouette. Preserve the same face, hair, body design, pose, framing, art style, and background when an earlier portrait is supplied. Only change armor that differs from the authoritative slots. Every named armor item is a unique visual design: swapping between two helmets must produce two clearly different helmets, not a recolor of the same helmet."""

    model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1.5").strip() or "gpt-image-1.5"
    quality = os.getenv("OPENAI_IMAGE_QUALITY", "medium").strip().lower()
    if quality not in {"low", "medium", "high", "auto"}:
        quality = "medium"
    if output_path.is_file():
        with output_path.open("rb") as source_image:
            result = client.images.edit(
                model=model,
                image=source_image,
                prompt=prompt,
                n=1,
                size="1024x1536",
                quality=quality,
                output_format="png",
                input_fidelity="high",
            )
    else:
        result = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size="1024x1536",
            quality=quality,
            output_format="png",
        )
    entries = getattr(result, "data", None)
    encoded = getattr(entries[0], "b64_json", "") if entries else ""
    if not encoded:
        raise ValueError("The image service returned no character art. Try again.")
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("The image service returned invalid character art.") from exc
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("The image service returned an unsupported image format.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_bytes(image_bytes)
    temporary.replace(output_path)
    return encoded
