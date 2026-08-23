"""World-aware AI generation for connected top-down exploration areas."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Dict, List


AREA_WIDTH = 48
AREA_HEIGHT = 34
ALLOWED_PALETTES = {"lush", "bright", "desert", "ice", "urban", "neon", "cosmic", "ocean", "volcanic"}
ALLOWED_GROUNDS = {"grass", "forest", "sand", "snow", "stone", "pavement", "metal", "alien", "coast"}
ALLOWED_FEATURES = {
    "trees", "flowers", "rocks", "water", "river", "pond", "street_lights", "crystals",
    "cactus", "snow_pines", "metal_crates", "holograms", "stars", "coral", "lava", "farmland",
}
ALLOWED_LANDMARK_TYPES = {
    "house", "shop", "station", "starport", "shrine", "ruins", "tower", "dock", "cave",
    "lab", "hangar", "inn", "farm", "fort", "temple", "office", "clinic", "market",
}


def _seed_for(world: Dict, x: int, y: int) -> int:
    source = f"{world.get('name', '')}|{world.get('player_request', '')}|{x}|{y}".encode("utf-8")
    return int(hashlib.sha256(source).hexdigest()[:8], 16)


def _world_kind(world: Dict) -> str:
    text = json.dumps(world, ensure_ascii=False, default=str).lower()
    if any(word in text for word in ("outer space", "space opera", "starship", "interstellar", "planet", "galaxy")):
        return "space"
    if any(word in text for word in ("cyberpunk", "neon", "megacorporation", "high-tech")):
        return "cyber"
    if any(word in text for word in ("modern", "present day", "earth", "crime", "realistic")):
        return "modern"
    if any(word in text for word in ("western", "frontier", "cowboy")):
        return "western"
    if any(word in text for word in ("post-apocalyptic", "wasteland", "apocalypse")):
        return "wasteland"
    if any(word in text for word in ("snow", "frozen", "ice age", "arctic")):
        return "ice"
    if any(word in text for word in ("desert", "dune", "sand")):
        return "desert"
    return "fantasy"


def _fallback_area(world: Dict, x: int, y: int, direction: str) -> Dict:
    kind = _world_kind(world)
    name = str(world.get("name") or "The Shattered Realms")
    templates = {
        "space": {
            "area_name": f"{name} Orbital Sector {x:+d}-{y:+d}", "biome": "orbital settlement",
            "palette": "cosmic", "ground_style": "metal",
            "features": ["metal_crates", "holograms", "street_lights", "stars"],
            "landmarks": [("Transit Hangar", "hangar"), ("Docking Concourse", "starport")],
            "npcs": [("Dock Guide", "station guide"), ("Wayfarer", "traveler")],
            "travel": [{"mode": "starship", "destination": "another planet", "available": False}],
        },
        "cyber": {
            "area_name": f"Neon District {x:+d}-{y:+d}", "biome": "high-tech city block",
            "palette": "neon", "ground_style": "pavement",
            "features": ["street_lights", "holograms", "metal_crates", "flowers"],
            "landmarks": [("Waystation", "station"), ("Street Clinic", "clinic")],
            "npcs": [("Local Guide", "district guide"), ("Courier", "courier")],
            "travel": [{"mode": "mag-rail", "destination": "another district", "available": False}],
        },
        "modern": {
            "area_name": f"{name} — District {x:+d}-{y:+d}", "biome": "modern neighborhood",
            "palette": "bright", "ground_style": "grass",
            "features": ["trees", "flowers", "street_lights", "water"],
            "landmarks": [("Regional Airport", "station"), ("Harbor Terminal", "dock")],
            "npcs": [("Local Resident", "resident"), ("Traveler", "traveler")],
            "travel": [
                {"mode": "airplane", "destination": "another region", "available": False},
                {"mode": "ship", "destination": "another coast", "available": False},
            ],
        },
        "western": {
            "area_name": f"Frontier Range {x:+d}-{y:+d}", "biome": "sunlit frontier town",
            "palette": "desert", "ground_style": "sand", "features": ["cactus", "rocks", "flowers"],
            "landmarks": [("Trail Inn", "inn"), ("Supply Post", "shop")],
            "npcs": [("Trail Guide", "scout"), ("Ranch Hand", "worker")],
            "travel": [{"mode": "stagecoach", "destination": "another settlement", "available": False}],
        },
        "wasteland": {
            "area_name": f"Wasteland Zone {x:+d}-{y:+d}", "biome": "reclaimed ruins",
            "palette": "desert", "ground_style": "stone", "features": ["rocks", "metal_crates", "cactus"],
            "landmarks": [("Salvage Shelter", "fort"), ("Broken Relay", "ruins")],
            "npcs": [("Scout", "scout"), ("Salvager", "salvager")],
            "travel": [{"mode": "ground vehicle", "destination": "a distant zone", "available": False}],
        },
        "ice": {
            "area_name": f"Frozen Reach {x:+d}-{y:+d}", "biome": "snowbound settlement",
            "palette": "ice", "ground_style": "snow", "features": ["snow_pines", "rocks", "crystals"],
            "landmarks": [("Warm Lodge", "inn"), ("Icewatch Post", "tower")],
            "npcs": [("Trail Keeper", "guide"), ("Researcher", "researcher")],
            "travel": [{"mode": "ice crawler", "destination": "another reach", "available": False}],
        },
        "desert": {
            "area_name": f"Sunscar Expanse {x:+d}-{y:+d}", "biome": "desert settlement",
            "palette": "desert", "ground_style": "sand", "features": ["cactus", "rocks", "crystals"],
            "landmarks": [("Caravan Rest", "inn"), ("Sun Market", "market")],
            "npcs": [("Caravan Guide", "guide"), ("Merchant", "merchant")],
            "travel": [{"mode": "caravan", "destination": "another oasis", "available": False}],
        },
        "fantasy": {
            "area_name": f"{name} Wilds {x:+d}-{y:+d}", "biome": "colorful woodland village",
            "palette": "lush", "ground_style": "grass", "features": ["trees", "flowers", "rocks", "water"],
            "landmarks": [("Wayfarer's Inn", "inn"), ("Village Shrine", "shrine")],
            "npcs": [("Village Guide", "guide"), ("Wanderer", "traveler")],
            "travel": [{"mode": "sailing ship", "destination": "another shore", "available": False}],
        },
    }
    chosen = templates[kind]
    landmarks = [
        {"name": chosen["landmarks"][0][0], "type": chosen["landmarks"][0][1], "x": 31, "y": 11, "width": 9, "height": 7,
         "interaction_prompt": f"I inspect and enter {chosen['landmarks'][0][0]}."},
        {"name": chosen["landmarks"][1][0], "type": chosen["landmarks"][1][1], "x": 15, "y": 6, "width": 7, "height": 5,
         "interaction_prompt": f"I inspect and enter {chosen['landmarks'][1][0]}."},
    ]
    npcs = [
        {"name": chosen["npcs"][0][0], "role": chosen["npcs"][0][1], "x": 28, "y": 21, "look": "friendly and setting-appropriate"},
        {"name": chosen["npcs"][1][0], "role": chosen["npcs"][1][1], "x": 20, "y": 19, "look": "distinctive local clothing"},
    ]
    return {
        "id": f"{x},{y}", "x": x, "y": y, "seed": _seed_for(world, x, y),
        "name": chosen["area_name"], "biome": chosen["biome"], "palette": chosen["palette"],
        "ground_style": chosen["ground_style"], "visual_features": chosen["features"],
        "landmarks": landmarks, "npcs": npcs, "travel_links": chosen["travel"],
        "arrival_text": f"You enter {chosen['area_name']}. The surroundings match the established {name} setting.",
        "suggested_actions": ["Speak to someone nearby", "Inspect the closest landmark", "Explore the main path"],
        "entered_from": direction,
    }


def _clean_json(text: str) -> Dict:
    clean = str(text or "").strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[-1]
        clean = clean.rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _clamp_int(value, minimum: int, maximum: int, fallback: int) -> int:
    try:
        return max(minimum, min(maximum, int(value)))
    except (TypeError, ValueError):
        return fallback


def _sanitize_area(raw: Dict, fallback: Dict, world: Dict, x: int, y: int, direction: str) -> Dict:
    area = deepcopy(fallback)
    area["id"], area["x"], area["y"], area["seed"] = f"{x},{y}", x, y, _seed_for(world, x, y)
    for key, maximum in (("name", 70), ("biome", 80), ("arrival_text", 280)):
        value = str(raw.get(key) or "").strip()
        if value:
            area[key] = value[:maximum]
    palette = str(raw.get("palette") or "").lower().strip()
    if palette in ALLOWED_PALETTES:
        area["palette"] = palette
    ground = str(raw.get("ground_style") or "").lower().strip()
    if ground in ALLOWED_GROUNDS:
        area["ground_style"] = ground
    features = raw.get("visual_features") if isinstance(raw.get("visual_features"), list) else []
    cleaned_features = [str(item).lower().strip() for item in features if str(item).lower().strip() in ALLOWED_FEATURES]
    if cleaned_features:
        area["visual_features"] = cleaned_features[:7]

    landmarks: List[Dict] = []
    for index, value in enumerate(raw.get("landmarks", []) if isinstance(raw.get("landmarks"), list) else []):
        if not isinstance(value, dict):
            continue
        fallback_x = 31 if index == 0 else 15
        fallback_y = 11 if index == 0 else 6
        width = _clamp_int(value.get("width"), 5, 10, 8)
        height = _clamp_int(value.get("height"), 4, 8, 6)
        landmark_type = str(value.get("type") or "house").lower().strip()
        if landmark_type not in ALLOWED_LANDMARK_TYPES:
            landmark_type = "house"
        landmark = {
            "name": str(value.get("name") or f"Landmark {index + 1}").strip()[:48],
            "type": landmark_type,
            "x": _clamp_int(value.get("x"), 5, AREA_WIDTH - width - 4, fallback_x),
            "y": _clamp_int(value.get("y"), 4, AREA_HEIGHT - height - 3, fallback_y),
            "width": width,
            "height": height,
            "interaction_prompt": str(value.get("interaction_prompt") or "I inspect this place and enter if possible.").strip()[:180],
        }
        landmarks.append(landmark)
    if landmarks:
        area["landmarks"] = landmarks[:3]

    npcs: List[Dict] = []
    for index, value in enumerate(raw.get("npcs", []) if isinstance(raw.get("npcs"), list) else []):
        if not isinstance(value, dict):
            continue
        npcs.append({
            "name": str(value.get("name") or f"Local {index + 1}").strip()[:40],
            "role": str(value.get("role") or "local").strip()[:50],
            "x": _clamp_int(value.get("x"), 3, 44, 28 - index * 5),
            "y": _clamp_int(value.get("y"), 3, 30, 21 - index * 2),
            "look": str(value.get("look") or "setting-appropriate clothing").strip()[:100],
        })
    if npcs:
        area["npcs"] = npcs[:4]

    links: List[Dict] = []
    for value in raw.get("travel_links", []) if isinstance(raw.get("travel_links"), list) else []:
        if not isinstance(value, dict):
            continue
        links.append({
            "mode": str(value.get("mode") or "transport").strip()[:40],
            "destination": str(value.get("destination") or "another region").strip()[:70],
            "available": False,
        })
    if links:
        area["travel_links"] = links[:3]

    actions = raw.get("suggested_actions") if isinstance(raw.get("suggested_actions"), list) else []
    cleaned_actions = [str(item).strip()[:90] for item in actions if str(item).strip()]
    if len(cleaned_actions) >= 3:
        area["suggested_actions"] = cleaned_actions[:3]
    area["entered_from"] = direction
    return area


def generate_world_area(provider, world: Dict, x: int, y: int, direction: str, previous_area: Dict | None = None) -> Dict:
    """Generate one visible, connected overworld area that obeys the confirmed world profile."""
    fallback = _fallback_area(world, x, y, direction)
    client = getattr(provider, "client", None)
    model = getattr(provider, "model", None)
    if client is None or not model:
        return fallback
    instructions = f"""You design one colorful top-down cartoon RPG exploration area. Return ONLY valid JSON.

The CONFIRMED WORLD PROFILE is authoritative. Every visible object, building, NPC, vehicle, material, plant, road, technology, and travel hint must naturally belong in that world. Never fall back to generic fantasy scenery when the profile is modern, science-fiction, cyberpunk, historical, western, superhero, post-apocalyptic, or another genre.

This area sits at world-grid coordinates ({x}, {y}) and the player entered from {direction}. It must connect logically to the previous area while introducing only what is immediately visible. Do not reveal secret factions, distant locations, future events, hidden villains, or major mysteries.

For an outer-space setting, areas can be planet surfaces, stations, colonies, hangars, or ships. Include a visible starport/dock/hangar and a future starship travel_link when appropriate. For an Earth-like modern setting, use roads, ports, train stations, airports, boats, aircraft, or vehicles when appropriate. Transportation is not playable yet, so set travel_link available=false.

Return exactly these keys:
- name: short area name
- biome: short visual description
- palette: one of {sorted(ALLOWED_PALETTES)}
- ground_style: one of {sorted(ALLOWED_GROUNDS)}
- visual_features: 3-7 values chosen only from {sorted(ALLOWED_FEATURES)}
- landmarks: 2-3 objects with name, type, x, y, width, height, interaction_prompt. type must be one of {sorted(ALLOWED_LANDMARK_TYPES)}. Coordinates fit width {AREA_WIDTH}, height {AREA_HEIGHT}.
- npcs: 2-4 objects with name, role, x, y, look
- travel_links: 0-3 objects with mode, destination, available=false
- arrival_text: 1-2 short sentences describing only what is immediately visible
- suggested_actions: exactly 3 concise actions

Keep a broad cross-shaped walking route near the center and avoid placing landmarks or NPCs directly on the four map-edge exits."""
    request = {
        "confirmed_world_profile": world,
        "area_coordinates": {"x": x, "y": y},
        "entered_from": direction,
        "previous_visible_area": previous_area or {},
    }
    try:
        response = client.responses.create(model=model, instructions=instructions, input=json.dumps(request, ensure_ascii=False, default=str))
        raw = _clean_json(getattr(response, "output_text", ""))
    except Exception:
        return fallback
    return _sanitize_area(raw, fallback, world, x, y, direction)
