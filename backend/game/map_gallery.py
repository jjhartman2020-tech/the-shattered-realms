"""Persistent, searchable campaign maps with cached AI-generated artwork."""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
from typing import Any, Dict, Iterable, List
import zlib


MAP_TYPES = {"universe", "world", "town"}
MAP_RENDER_VERSION = 2


def _slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return clean[:72] or "map"


def _world_is_spacefaring(world: Dict) -> bool:
    text = json.dumps(world, ensure_ascii=False, default=str).lower()
    return any(
        phrase in text
        for phrase in (
            "outer space", "space opera", "space travel", "starship", "interstellar",
            "galaxy", "galactic", "solar system", "multiple planets", "planetary",
        )
    )


def _gallery(state: Dict) -> Dict:
    gallery = state.setdefault("map_gallery", {"maps": [], "selected_map_id": None})
    if not isinstance(gallery, dict):
        gallery = {"maps": [], "selected_map_id": None}
        state["map_gallery"] = gallery
    if not isinstance(gallery.get("maps"), list):
        gallery["maps"] = []
    return gallery


def _record_id(map_type: str, title: str, location: str) -> str:
    source = f"{map_type}|{title}|{location}".encode("utf-8")
    return f"{map_type}-{_slug(title)}-{hashlib.sha256(source).hexdigest()[:10]}"


def normalize_map_record(raw: Dict, *, discovered_turn: int = 0) -> Dict:
    map_type = str(raw.get("map_type") or raw.get("type") or "town").strip().lower()
    if map_type not in MAP_TYPES:
        map_type = "town"
    location = str(raw.get("location") or raw.get("name") or "Unknown place").strip()[:100]
    title = str(raw.get("title") or f"{location} Map").strip()[:110]
    if not title.lower().endswith("map"):
        title += " Map"
    map_id = str(raw.get("id") or _record_id(map_type, title, location)).strip()
    return {
        "id": map_id,
        "title": title,
        "map_type": map_type,
        "location": location,
        "description": str(raw.get("description") or "A map revealed through exploration.").strip()[:420],
        "discovered_turn": max(0, int(raw.get("discovered_turn", discovered_turn) or 0)),
        "image_file": str(raw.get("image_file") or f"{_slug(map_id)}.png"),
        "image_status": str(raw.get("image_status") or "pending"),
        "image_source": str(raw.get("image_source") or ""),
        "image_model": str(raw.get("image_model") or ""),
        "image_error": str(raw.get("image_error") or ""),
        "image_render_version": max(0, int(raw.get("image_render_version", 0) or 0)),
        "source": str(raw.get("source") or "story"),
    }


def register_map(state: Dict, raw: Dict) -> Dict:
    """Add a map once. Repeated discoveries of the same place reuse the first image."""
    gallery = _gallery(state)
    record = normalize_map_record(raw, discovered_turn=int(state.get("turn", 0) or 0))
    for existing in gallery["maps"]:
        if not isinstance(existing, dict):
            continue
        same_id = str(existing.get("id") or "") == record["id"]
        same_place = (
            str(existing.get("map_type") or "") == record["map_type"]
            and str(existing.get("location") or "").strip().lower() == record["location"].lower()
        )
        if same_id or same_place:
            return existing
    gallery["maps"].append(record)
    if not gallery.get("selected_map_id"):
        gallery["selected_map_id"] = record["id"]
    return record


def initial_map_records(world: Dict) -> List[Dict]:
    """Create the starting world map and, for space games, a universe map."""
    world_name = str(world.get("name") or "Untitled World").strip()
    result = [normalize_map_record({
        "title": f"{world_name} World Map",
        "map_type": "world",
        "location": world_name,
        "description": "The known geography of the campaign world. Undiscovered places remain unmarked.",
        "source": "world_creation",
    })]
    if _world_is_spacefaring(world):
        result.insert(0, normalize_map_record({
            "title": f"{world_name} Universe Map",
            "map_type": "universe",
            "location": world_name,
            "description": "Known planets and travel routes in this spacefaring setting. Unknown systems remain hidden.",
            "source": "world_creation",
        }))
    return result


def _map_prompt(world: Dict, record: Dict) -> str:
    map_type = str(record.get("map_type") or "town")
    type_direction = {
        "universe": "an orthographic star-chart with distinct planets, moons, sectors, and clearly traced public travel routes",
        "world": "a true overhead atlas with coastlines, borders, terrain regions, roads, rivers, and known settlements",
        "town": "a true overhead street plan with blocks, roads, districts, gates, paths, and known public landmarks",
    }[map_type]
    label_candidates: List[str] = []
    raw_candidates: List[Any] = [record.get("location")]
    important_locations = world.get("important_locations")
    if isinstance(important_locations, list):
        raw_candidates.extend(important_locations)
    for raw in raw_candidates:
        label = str(raw or "").strip()
        for separator in (" — ", " - ", ":", "("):
            label = label.split(separator, 1)[0].strip()
        if not label or len(label) > 28 or label.lower() in {item.lower() for item in label_candidates}:
            continue
        label_candidates.append(label)
        if len(label_candidates) >= 7:
            break
    exact_labels = ", ".join(f'"{label.upper()}"' for label in label_candidates) or '"KNOWN REGION"'
    return f"""GOAL
Create a functional, readable cartographic map for a teen-rated AI text RPG. This must look like an actual map used for navigation—not a landscape painting, cinematic scene, concept-art picture, poster, or angled view.

MAP CONTENT
Map type and purpose: {type_direction}.
World name: {world.get('name', 'Untitled World')}
Player's world request: {world.get('player_request', '')}
World premise: {world.get('premise', '')}
Genre / era / technology: {world.get('genre', '')} / {world.get('era', '')} / {world.get('technology_level', '')}
Map location: {record.get('location', '')}
Location description: {record.get('description', '')}

VISUAL RULES
- Strict 90-degree top-down / orthographic cartography with flat, clean map symbols.
- Clear geographic shapes and navigation routes are more important than decorative artwork.
- Use a restrained setting-appropriate color palette, a subtle paper or tactical-display texture, a small compass rose, and a simple border.
- No people, dramatic foreground objects, horizon, sky, camera perspective, scenery, fake game UI, logos, watermark, copyrighted characters, gore, or sexual content.

LABEL RULES
- Use no more than 7 labels total. Only use these exact public names where geographically relevant: {exact_labels}.
- Render every label once, verbatim, in LARGE BOLD UPPERCASE block lettering.
- Use a clean sans-serif or highly readable atlas typeface, generous spacing, and strong contrast.
- Put each name on a pale solid label plate with dark lettering, never directly over busy terrain.
- No cursive, runes, decorative lettering, tiny writing, warped words, invented extra names, legends full of text, or map title inside the image. The game UI displays the title separately.

KNOWLEDGE LIMITS
Show only geography and public places the player could reasonably know. Do not reveal secret locations, hidden enemies, future events, puzzle answers, undiscovered treasure, or private Game Master information. Use a landscape aspect ratio."""


def _fallback_png(record: Dict, world: Dict, width: int = 960, height: int = 640) -> bytes:
    """Produce a valid, fast placeholder PNG when image generation is unavailable."""
    text = json.dumps(world, ensure_ascii=False, default=str).lower()
    if str(record.get("map_type")) == "universe":
        bg, land, route = (8, 14, 34), (91, 74, 153), (109, 211, 255)
    elif any(word in text for word in ("desert", "western", "sand")):
        bg, land, route = (225, 194, 126), (181, 121, 71), (86, 68, 51)
    elif any(word in text for word in ("cyber", "neon", "future")):
        bg, land, route = (17, 27, 43), (38, 117, 126), (178, 106, 255)
    else:
        bg, land, route = (80, 137, 157), (107, 157, 83), (238, 221, 153)
    rows: List[bytearray] = [bytearray(bg * width) for _ in range(height)]

    def fill_rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                offset = x * 3
                rows[y][offset:offset + 3] = bytes(color)

    if str(record.get("map_type")) == "universe":
        for index, (x, y, size) in enumerate(((150, 160, 34), (385, 430, 55), (610, 195, 42), (810, 410, 62))):
            fill_rect(x - size, y - size, x + size, y + size, land if index % 2 == 0 else route)
        for x in range(150, 810):
            y = 160 + int((x - 150) * 0.38)
            fill_rect(x, y, x + 3, y + 3, route)
    else:
        fill_rect(70, 70, 460, 290, land)
        fill_rect(335, 210, 885, 560, land)
        fill_rect(420, 0, 475, 640, route)
        fill_rect(0, 365, 960, 405, route)
        for x, y in ((150, 150), (300, 470), (600, 330), (790, 485)):
            fill_rect(x - 13, y - 13, x + 13, y + 13, (245, 235, 176))

    raw = b"".join(b"\x00" + bytes(row) for row in rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 6))
        + chunk(b"IEND", b"")
    )


def _is_valid_png(image_bytes: bytes) -> bool:
    """Validate the whole PNG container so corrupt cached files are never reused."""
    if not isinstance(image_bytes, bytes) or not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    position = 8
    saw_header = False
    saw_image_data = False
    saw_end = False
    try:
        while position + 12 <= len(image_bytes):
            length = struct.unpack(">I", image_bytes[position:position + 4])[0]
            kind = image_bytes[position + 4:position + 8]
            data_start = position + 8
            data_end = data_start + length
            crc_end = data_end + 4
            if crc_end > len(image_bytes):
                return False
            payload = image_bytes[data_start:data_end]
            expected_crc = struct.unpack(">I", image_bytes[data_end:crc_end])[0]
            if (zlib.crc32(kind + payload) & 0xFFFFFFFF) != expected_crc:
                return False
            if kind == b"IHDR":
                if saw_header or length != 13:
                    return False
                width, height = struct.unpack(">II", payload[:8])
                if width < 1 or height < 1:
                    return False
                saw_header = True
            elif kind == b"IDAT":
                saw_image_data = saw_image_data or length > 0
            elif kind == b"IEND":
                if length != 0:
                    return False
                saw_end = True
                position = crc_end
                break
            position = crc_end
    except (struct.error, TypeError, ValueError):
        return False
    return saw_header and saw_image_data and saw_end and position == len(image_bytes)


def _read_valid_png(image_path: Path) -> bytes:
    try:
        image_bytes = image_path.read_bytes() if image_path.is_file() else b""
    except OSError:
        return b""
    return image_bytes if _is_valid_png(image_bytes) else b""


def generate_map_image(provider, world: Dict, record: Dict, output_dir: Path) -> Dict:
    """Generate and cache exactly one map image, falling back without breaking play."""
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / Path(str(record.get("image_file") or "map.png")).name
    cached_bytes = _read_valid_png(image_path)
    render_is_current = int(record.get("image_render_version", 0) or 0) == MAP_RENDER_VERSION
    if cached_bytes and render_is_current:
        record["image_status"] = "ready"
        return record
    if image_path.is_file():
        try:
            image_path.unlink()
        except OSError:
            pass

    image_bytes = b""
    generation_error = ""
    client = getattr(provider, "client", None)
    try:
        if client is not None and hasattr(client, "images"):
            model = os.getenv("OPENAI_MAP_IMAGE_MODEL", os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1.5")).strip() or "gpt-image-1.5"
            quality = os.getenv("OPENAI_MAP_IMAGE_QUALITY", "medium").strip().lower()
            if quality not in {"low", "medium", "high", "auto"}:
                quality = "medium"
            result = client.images.generate(
                model=model,
                prompt=_map_prompt(world, record),
                size="1536x1024",
                quality=quality,
                output_format="png",
            )
            encoded = getattr(result.data[0], "b64_json", "") if getattr(result, "data", None) else ""
            if not encoded:
                raise ValueError("The image service returned no map image.")
            image_bytes = base64.b64decode(encoded, validate=True)
            if not _is_valid_png(image_bytes):
                raise ValueError("The image service returned a corrupt or unsupported map image.")
            record["image_source"] = "ai"
            record["image_model"] = model
    except Exception as exc:
        generation_error = str(exc).strip() or exc.__class__.__name__
        print(f"[Map Gallery] AI map generation failed; using a backup map: {generation_error}")
        image_bytes = b""

    if not image_bytes:
        image_bytes = _fallback_png(record, world)
        record["image_source"] = "fallback"
    if not _is_valid_png(image_bytes):
        record["image_status"] = "error"
        record["image_error"] = generation_error or "Map image validation failed."
        return record
    temporary = image_path.with_suffix(image_path.suffix + ".tmp")
    temporary.write_bytes(image_bytes)
    temporary.replace(image_path)
    record["image_file"] = image_path.name
    record["image_status"] = "ready"
    record["image_render_version"] = MAP_RENDER_VERSION
    record["image_error"] = generation_error[:320]
    return record


def prepare_initial_maps(provider, world: Dict, output_dir: Path) -> tuple[List[Dict], str]:
    """Generate the world-map preview; leave any universe map ready for lazy loading."""
    records = initial_map_records(world)
    preview = ""
    for record in records:
        if record["map_type"] != "world":
            continue
        generate_map_image(provider, world, record, output_dir)
        preview = load_map_base64(record, output_dir)
        break
    return records, preview


def install_initial_maps(state: Dict, records: Iterable[Dict]) -> None:
    gallery = _gallery(state)
    gallery["maps"] = []
    gallery["selected_map_id"] = None
    for record in records:
        if isinstance(record, dict):
            register_map(state, deepcopy(record))


def generate_pending_maps(
    game_master,
    output_dir: Path,
    limit: int = 1,
    only_ids: Iterable[str] | None = None,
) -> List[Dict]:
    gallery = _gallery(game_master.state.data)
    world = game_master.state.data.get("world_profile")
    if not isinstance(world, dict):
        world = {}
    generated: List[Dict] = []
    allowed_ids = {str(value) for value in only_ids} if only_ids is not None else None
    for record in gallery["maps"]:
        if not isinstance(record, dict) or str(record.get("image_status")) == "ready":
            continue
        if allowed_ids is not None and str(record.get("id") or "") not in allowed_ids:
            continue
        generate_map_image(game_master.provider, world, record, output_dir)
        generated.append(deepcopy(record))
        if len(generated) >= max(1, int(limit)):
            break
    if generated:
        game_master.state.save()
    return generated


def list_maps(state: Dict) -> List[Dict]:
    result = []
    for record in _gallery(state)["maps"]:
        if not isinstance(record, dict):
            continue
        clean = deepcopy(record)
        clean.pop("image_base64", None)
        result.append(clean)
    result.sort(key=lambda item: (int(item.get("discovered_turn", 0) or 0), str(item.get("title") or "").lower()))
    return result


def find_map(state: Dict, map_id: str) -> Dict | None:
    for record in _gallery(state)["maps"]:
        if isinstance(record, dict) and str(record.get("id") or "") == str(map_id or ""):
            return record
    return None


def load_map_base64(record: Dict, output_dir: Path) -> str:
    if int(record.get("image_render_version", 0) or 0) != MAP_RENDER_VERSION:
        record["image_status"] = "pending"
        return ""
    image_path = output_dir / Path(str(record.get("image_file") or "")).name
    image_bytes = _read_valid_png(image_path)
    if not image_bytes:
        if image_path.is_file():
            record["image_status"] = "pending"
        return ""
    return base64.b64encode(image_bytes).decode("ascii")


def clear_map_cache(output_dir: Path) -> None:
    try:
        if output_dir.is_dir():
            shutil.rmtree(output_dir)
    except OSError:
        pass
