"""Authoritative mutations used by the Godot Character Hub."""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict

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


def _portrait_metadata_path(output_path: Path) -> Path:
    return output_path.with_suffix(".json")


def _portrait_cache_dir(output_path: Path) -> Path:
    return output_path.parent / f"{output_path.stem}_outfits"


def _portrait_manifest(game_master) -> Dict[str, Any]:
    """Describe the identity and visible loadout without volatile durability values."""
    player = _player(game_master)
    world = game_master.state.data.get("world_profile")
    if not isinstance(world, dict):
        world = game_master.state.data.get("world") if isinstance(game_master.state.data.get("world"), dict) else {}
    equipped = player.get("equipped_armor") if isinstance(player.get("equipped_armor"), dict) else {}
    armor: Dict[str, Any] = {}
    for slot in ARMOR_SLOTS:
        piece = equipped.get(slot)
        if not isinstance(piece, dict):
            armor[slot] = None
            continue
        armor[slot] = {
            "name": str(piece.get("name") or "Armor"),
            "description": str(piece.get("description") or ""),
            "rarity": str(piece.get("rarity") or "common"),
        }
    return {
        "character": {
            "name": str(player.get("name") or "Traveler"),
            "species": str(player.get("species") or "unspecified"),
            "class": str(player.get("class") or "unassigned"),
            "appearance": str(player.get("appearance") or ""),
        },
        "world": {
            "name": str(world.get("name") or world.get("title") or "The Shattered Realms"),
            "genre": str(world.get("genre") or world.get("setting") or "adaptive fantasy and science fiction"),
            "description": str(world.get("description") or world.get("summary") or world.get("tone") or ""),
        },
        "armor": armor,
    }


def _portrait_signature(manifest: Dict[str, Any]) -> str:
    canonical = json.dumps(manifest, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _read_portrait_metadata(output_path: Path) -> Dict[str, Any]:
    try:
        parsed = json.loads(_portrait_metadata_path(output_path).read_text(encoding="utf-8"))
        return parsed if isinstance(parsed, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def _write_portrait_files(output_path: Path, image_bytes: bytes, manifest: Dict[str, Any], signature: str) -> None:
    """Atomically activate the image and save an exact reusable copy for this outfit."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path = _portrait_cache_dir(output_path) / f"{signature}.png"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"signature": signature, "manifest": manifest}

    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_bytes(image_bytes)
    temporary.replace(output_path)
    cache_temporary = cache_path.with_suffix(cache_path.suffix + ".tmp")
    cache_temporary.write_bytes(image_bytes)
    cache_temporary.replace(cache_path)
    metadata_path = _portrait_metadata_path(output_path)
    metadata_temporary = metadata_path.with_suffix(metadata_path.suffix + ".tmp")
    metadata_temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata_temporary.replace(metadata_path)


def load_character_portrait(game_master, output_path: Path) -> Dict[str, Any]:
    """Restore an exact cached outfit, or return the current picture marked stale."""
    manifest = _portrait_manifest(game_master)
    signature = _portrait_signature(manifest)
    cache_path = _portrait_cache_dir(output_path) / f"{signature}.png"
    active_metadata = _read_portrait_metadata(output_path)

    try:
        if cache_path.is_file():
            image_bytes = cache_path.read_bytes()
            _write_portrait_files(output_path, image_bytes, manifest, signature)
            return {
                "portrait_base64": base64.b64encode(image_bytes).decode("ascii"),
                "portrait_available": True,
                "portrait_stale": False,
                "portrait_cached": True,
            }
        encoded = cached_character_portrait(output_path)
        exact_active = bool(encoded) and str(active_metadata.get("signature") or "") == signature
        if exact_active:
            image_bytes = base64.b64decode(encoded)
            _write_portrait_files(output_path, image_bytes, manifest, signature)
        return {
            "portrait_base64": encoded,
            "portrait_available": bool(encoded),
            "portrait_stale": not exact_active,
            "portrait_cached": False,
        }
    except (OSError, ValueError, TypeError):
        encoded = cached_character_portrait(output_path)
        return {
            "portrait_base64": encoded,
            "portrait_available": bool(encoded),
            "portrait_stale": True,
            "portrait_cached": False,
        }


def clear_character_portrait_cache(output_path: Path) -> None:
    """Remove portraits belonging to a deliberately reset campaign."""
    for path in (output_path, _portrait_metadata_path(output_path)):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
    cache_dir = _portrait_cache_dir(output_path)
    try:
        for cached_file in cache_dir.glob("*"):
            if cached_file.is_file():
                cached_file.unlink(missing_ok=True)
        cache_dir.rmdir()
    except OSError:
        pass


def generate_character_portrait(
    game_master,
    output_path: Path,
    *,
    force_refresh: bool = False,
) -> str:
    """Generate one outfit preview, reusing exact cached loadouts when possible."""
    player = _player(game_master)
    client = getattr(game_master.provider, "client", None)
    if client is None or not hasattr(client, "images"):
        raise ValueError("Character art needs OPENAI_API_KEY. Set it, then restart python -m backend.api.")

    manifest = _portrait_manifest(game_master)
    signature = _portrait_signature(manifest)
    cache_path = _portrait_cache_dir(output_path) / f"{signature}.png"
    if cache_path.is_file() and not force_refresh:
        image_bytes = cache_path.read_bytes()
        _write_portrait_files(output_path, image_bytes, manifest, signature)
        return base64.b64encode(image_bytes).decode("ascii")

    world = manifest["world"]
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

    previous_metadata = _read_portrait_metadata(output_path)
    previous_manifest = previous_metadata.get("manifest") if isinstance(previous_metadata.get("manifest"), dict) else {}
    previous_armor = previous_manifest.get("armor") if isinstance(previous_manifest.get("armor"), dict) else {}
    changed_slots = [slot for slot in ARMOR_SLOTS if previous_armor.get(slot) != manifest["armor"].get(slot)]
    if previous_manifest:
        changed_text = ", ".join(slot.upper() for slot in changed_slots) if changed_slots else "none"
        change_instruction = (
            f"CURRENT EDIT: Only these slots changed: {changed_text}. Preserve every unchanged armor piece exactly as "
            "it appears in the supplied portrait—same silhouette, colors, materials, and small details. Completely "
            "remove armor from changed slots marked EMPTY and replace changed equipped slots with their exact named design."
        )
    else:
        change_instruction = "Apply the complete authoritative loadout while preserving the character's identity."

    prompt = f"""Create original full-body character concept art for a text RPG character screen.
Show one fully clothed character, head to toe, in a neutral readable pose on a simple atmospheric background. No text, labels, UI, logos, gore, or sexualized presentation. Keep the design suitable for a teen-rated adventure game. If the description names an existing copyrighted character, reinterpret the idea into a clearly original design rather than copying that character.

Character name: {player.get('name', 'Traveler')}
Species: {player.get('species', 'unspecified')}
Class/build: {player.get('class', 'unassigned')}
Saved appearance: {player.get('appearance', 'Use a distinctive original adventurer design.')}
World name/genre: {world.get('name', 'The Shattered Realms')} / {world.get('genre', 'adaptive fantasy and science fiction')}
World visual direction: {world.get('description', 'Match the established game world.')}
AUTHORITATIVE ARMOR SLOTS (follow every slot exactly):
{chr(10).join(armor_details)}
{change_instruction}

Use polished, detailed, colorful digital illustration with a strong readable silhouette. Preserve the same face, hair, body design, pose, framing, art style, and background when an earlier portrait is supplied. Only change armor that differs from the authoritative slots. Every named armor item is a unique visual design: swapping between two helmets must produce two clearly different helmets, not a recolor of the same helmet."""

    model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1.5").strip() or "gpt-image-1.5"
    quality = os.getenv("OPENAI_IMAGE_QUALITY", "medium").strip().lower()
    if quality not in {"low", "medium", "high", "auto"}:
        quality = "medium"
    same_identity = previous_manifest and previous_manifest.get("character") == manifest.get("character") and previous_manifest.get("world") == manifest.get("world")
    if output_path.is_file() and (same_identity or not previous_manifest):
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

    _write_portrait_files(output_path, image_bytes, manifest, signature)
    return encoded
