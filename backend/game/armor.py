"""Five-slot armor system and starting armor creation."""
from __future__ import annotations
from copy import deepcopy
import json
import re
from typing import Dict, List

ARMOR_SLOTS = ("helmet", "breastplate", "pants", "gloves", "boots")
STARTING_ARMOR_MIN = 10
STARTING_ARMOR_MAX = 20


def _safe_int(value, default: int = 0) -> int:
    """Parse AI-generated numeric fields without crashing on labels like 'Light'."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value or "").strip().lower()
    if not text:
        return int(default)
    weight_words = {
        "very light": 1,
        "ultralight": 1,
        "light": 2,
        "lightweight": 2,
        "medium": 3,
        "moderate": 3,
        "balanced": 3,
        "heavy": 5,
        "very heavy": 7,
        "super heavy": 8,
    }
    if text in weight_words:
        return weight_words[text]
    match = re.search(r"-?\d+", text)
    if match:
        return int(match.group(0))
    return int(default)


def normalize_armor_piece(raw: Dict) -> Dict:
    piece = deepcopy(raw) if isinstance(raw, dict) else {}
    slot = str(piece.get("slot") or "").strip().lower()
    if slot not in ARMOR_SLOTS:
        slot = "breastplate"
    piece["slot"] = slot
    piece["type"] = "armor"
    piece["armor_hp"] = max(0, _safe_int(piece.get("armor_hp", 0), 0))
    piece["max_armor_hp"] = max(piece["armor_hp"], _safe_int(piece.get("max_armor_hp", piece["armor_hp"]), piece["armor_hp"]))
    piece["weight"] = max(0, _safe_int(piece.get("weight", 0), 0))
    effects = piece.get("effects", [])
    piece["effects"] = effects if isinstance(effects, list) else ([str(effects)] if effects else [])
    piece.pop("armor_bonus", None)
    return piece


def armor_totals(equipped: Dict) -> Dict:
    pieces = [p for p in (equipped or {}).values() if isinstance(p, dict)]
    return {
        "armor": sum(max(0, _safe_int(p.get("armor_hp", 0), 0)) for p in pieces),
        "max_armor": sum(max(0, _safe_int(p.get("max_armor_hp", p.get("armor_hp", 0)), 0)) for p in pieces),
        "weight": sum(max(0, _safe_int(p.get("weight", 0), 0)) for p in pieces),
    }


def armor_effects(equipped: Dict) -> Dict:
    """Convert armor text effects into a few engine-readable beginner bonuses."""
    movement = 0
    resistances: Dict[str, int] = {}
    for piece in (equipped or {}).values():
        if not isinstance(piece, dict) or _safe_int(piece.get("armor_hp", 0), 0) <= 0:
            continue
        for raw in piece.get("effects", []):
            text = str(raw).strip().lower()
            move = re.search(r"([+-]\d+)\s*(?:movement|move)(?:\s+square)?", text)
            if move:
                movement += int(move.group(1))
            resist = re.search(r"(\d+)\s*%\s*([a-z -]+?)\s*resistance", text)
            if resist:
                kind = resist.group(2).strip().replace(" ", "_")
                resistances[kind] = min(50, resistances.get(kind, 0) + int(resist.group(1)))
    return {"movement_bonus": movement, "resistances": resistances}


def armor_weight_movement_penalty(weight: int) -> int:
    """Heavy equipment slows movement without making beginner armor oppressive."""
    weight = max(0, _safe_int(weight, 0))
    if weight >= 30: return 3
    if weight >= 22: return 2
    if weight >= 14: return 1
    return 0


def effective_movement(base_movement: int, equipped: Dict) -> int:
    totals = armor_totals(equipped)
    effects = armor_effects(equipped)
    return max(1, int(base_movement) + int(effects["movement_bonus"]) - armor_weight_movement_penalty(totals["weight"]))


def sync_armor_summary(actor: Dict) -> Dict:
    equipped = actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"), dict) else {}
    totals = armor_totals(equipped)
    actor["armor"] = totals["armor"]
    actor["max_armor"] = totals["max_armor"]
    actor["armor_weight"] = totals["weight"]
    actor["armor_effects"] = armor_effects(equipped)
    return totals


def apply_damage_to_armor(actor: Dict, damage: int, *, damage_type: str | None = None) -> Dict:
    """Absorb damage with Armor HP first, then overflow into real HP."""
    incoming = max(0, int(damage or 0))
    equipped = actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"), dict) else {}
    sync_armor_summary(actor)
    armor_before = int(actor.get("armor", 0) or 0)
    hp_before = int(actor.get("hp", 0) or 0)

    resisted = 0
    if damage_type:
        kind = str(damage_type).strip().lower().replace(" ", "_")
        pct = int((actor.get("armor_effects") or {}).get("resistances", {}).get(kind, 0) or 0)
        resisted = round(incoming * min(50, max(0, pct)) / 100)
        incoming = max(0, incoming - resisted)

    absorbed = min(armor_before, incoming)
    overflow = incoming - absorbed
    remaining = absorbed
    pieces = sorted(
        [p for p in equipped.values() if isinstance(p, dict)],
        key=lambda p: (str(p.get("slot")) != "breastplate", -_safe_int(p.get("armor_hp", 0), 0)),
    )
    broken = []
    for piece in pieces:
        if remaining <= 0: break
        current = max(0, _safe_int(piece.get("armor_hp", 0), 0))
        take = min(current, remaining)
        piece["armor_hp"] = current - take
        remaining -= take
        if current > 0 and piece["armor_hp"] == 0:
            broken.append(str(piece.get("name") or piece.get("slot") or "Armor piece"))

    actor["hp"] = max(0, hp_before - overflow)
    actor["defeated"] = actor["hp"] <= 0
    sync_armor_summary(actor)
    return {
        "incoming_damage": int(damage or 0),
        "resisted_damage": resisted,
        "armor_absorbed": absorbed,
        "hp_damage": overflow,
        "armor_before": armor_before,
        "armor_after": int(actor.get("armor", 0)),
        "max_armor": int(actor.get("max_armor", 0)),
        "hp_before": hp_before,
        "hp_after": int(actor.get("hp", 0)),
        "broken_pieces": broken,
    }


def repair_armor(actor: Dict, amount: int | None = None) -> Dict:
    equipped = actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"), dict) else {}
    before = armor_totals(equipped)["armor"]
    remaining = None if amount is None else max(0, int(amount))
    repaired = 0
    for slot in ARMOR_SLOTS:
        piece = equipped.get(slot)
        if not isinstance(piece, dict): continue
        current = max(0, _safe_int(piece.get("armor_hp", 0), 0))
        maximum = max(current, _safe_int(piece.get("max_armor_hp", current), current))
        missing = maximum - current
        add = missing if remaining is None else min(missing, remaining)
        piece["armor_hp"] = current + add
        repaired += add
        if remaining is not None:
            remaining -= add
            if remaining <= 0: break
    sync_armor_summary(actor)
    return {"repaired": repaired, "armor_before": before, "armor_after": actor.get("armor", 0), "max_armor": actor.get("max_armor", 0)}


def _fallback_sets(description: str = "") -> List[Dict]:
    return [
        {"name": "Mobile Starter Set", "description": description or "Light protection built for movement.", "pieces": [
            {"name":"Light Headgear","slot":"helmet","armor_hp":2,"weight":1,"effects":[]},
            {"name":"Light Body Armor","slot":"breastplate","armor_hp":5,"weight":2,"effects":[]},
            {"name":"Flexible Leg Armor","slot":"pants","armor_hp":3,"weight":1,"effects":[]},
            {"name":"Grip Gloves","slot":"gloves","armor_hp":2,"weight":1,"effects":[]},
            {"name":"Runner Boots","slot":"boots","armor_hp":2,"weight":1,"effects":["+1 movement square"]},
        ]},
        {"name": "Balanced Starter Set", "description": description or "Balanced beginner protection.", "pieces": [
            {"name":"Guard Helmet","slot":"helmet","armor_hp":3,"weight":1,"effects":[]},
            {"name":"Guard Breastplate","slot":"breastplate","armor_hp":7,"weight":3,"effects":[]},
            {"name":"Guard Pants","slot":"pants","armor_hp":3,"weight":1,"effects":[]},
            {"name":"Guard Gloves","slot":"gloves","armor_hp":2,"weight":1,"effects":[]},
            {"name":"Guard Boots","slot":"boots","armor_hp":2,"weight":1,"effects":[]},
        ]},
        {"name": "Heavy Starter Set", "description": description or "Tough beginner protection with extra weight.", "pieces": [
            {"name":"Heavy Helmet","slot":"helmet","armor_hp":3,"weight":2,"effects":[]},
            {"name":"Heavy Breastplate","slot":"breastplate","armor_hp":8,"weight":5,"effects":[]},
            {"name":"Heavy Pants","slot":"pants","armor_hp":4,"weight":3,"effects":[]},
            {"name":"Heavy Gloves","slot":"gloves","armor_hp":2,"weight":2,"effects":[]},
            {"name":"Heavy Boots","slot":"boots","armor_hp":3,"weight":3,"effects":["-1 movement square"]},
        ]},
    ]


def _normalize_set(raw: Dict, target_total: int) -> Dict:
    result = deepcopy(raw) if isinstance(raw, dict) else {}
    pieces_raw = result.get("pieces", []) if isinstance(result.get("pieces"), list) else []
    by_slot = {str(p.get("slot", "")).lower(): normalize_armor_piece(p) for p in pieces_raw if isinstance(p, dict)}
    pieces = []
    for slot in ARMOR_SLOTS:
        p = by_slot.get(slot, normalize_armor_piece({"name": slot.title(), "slot": slot, "armor_hp": 0, "weight": 0, "effects": []}))
        pieces.append(p)
    target_total = max(STARTING_ARMOR_MIN, min(STARTING_ARMOR_MAX, int(target_total)))
    current = sum(p["armor_hp"] for p in pieces)
    if current <= 0:
        pieces[1]["armor_hp"] = target_total
    elif current != target_total:
        scaled = [max(0, round(p["armor_hp"] * target_total / current)) for p in pieces]
        diff = target_total - sum(scaled)
        scaled[1] += diff
        for p, hp in zip(pieces, scaled): p["armor_hp"] = max(0, hp)
    for p in pieces: p["max_armor_hp"] = p["armor_hp"]
    result["pieces"] = pieces
    result["total_armor"] = sum(p["armor_hp"] for p in pieces)
    result["tier"] = "beginner"
    return result


def generate_starting_armor(provider, world: Dict, player: Dict, request: str = "", custom: bool = False) -> List[Dict]:
    client = getattr(provider, "client", None); model = getattr(provider, "model", None)
    if client is None or not model:
        sets = _fallback_sets(request)
        return [_normalize_set(s, total) for s, total in zip(sets, (14,17,20))]
    instructions = """Return ONLY JSON. Generate beginner armor for a genre-neutral RPG using the confirmed world and character. Armor NEVER adds AC. Armor is a separate health bar that absorbs damage before HP. There are exactly five slots: helmet, breastplate, pants, gloves, boots. A full STARTING set must total only 10-20 Armor HP so beginner armor is not overpowered. Breastplate usually provides the most Armor HP. Pieces may have small thematic effects such as +1 movement square or 5-15% resistance to one damage type, but beginner effects must be weak. Heavier protection may have movement penalties. Every piece needs name, slot, armor_hp, weight, effects. IMPORTANT: armor_hp and weight MUST be JSON integers, never labels or words such as Light, Medium, or Heavy. Use small numeric weights such as 1-8 per piece. Do not add permanent core-stat increases. If custom_request is supplied, honor its appearance/theme but BALANCE its mechanics to beginner strength. If custom_mode=true return exactly 1 set. Otherwise return exactly 3 meaningfully different choices. Top-level JSON: {\"sets\":[{\"name\":...,\"description\":...,\"pieces\":[...]}]}."""
    payload = {"world": world, "player": {"class": player.get("class"), "stats": player.get("stats"), "appearance": player.get("appearance")}, "custom_mode": custom, "custom_request": request}
    response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, default=str))
    try: data = json.loads(response.output_text.strip())
    except Exception: data = {}
    sets = data.get("sets", []) if isinstance(data, dict) else []
    if not isinstance(sets, list) or len(sets) != (1 if custom else 3):
        sets = _fallback_sets(request)[:1] if custom else _fallback_sets()
    targets = [15] if custom else [14,17,20]
    return [_normalize_set(s, targets[min(i, len(targets)-1)]) for i, s in enumerate(sets)]


def print_armor(actor: Dict) -> None:
    equipped = actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"), dict) else {}
    totals = sync_armor_summary(actor)
    print(f"\nARMOR — {actor.get('armor_set_name') or 'Mixed Set'}")
    print(f"Armor HP: {totals['armor']}/{totals['max_armor']} | Weight: {totals['weight']}")
    effects = armor_effects(equipped)
    penalty = armor_weight_movement_penalty(totals["weight"])
    print(f"Movement from armor: {effects['movement_bonus']:+d} effect, -{penalty} from weight")
    for slot in ARMOR_SLOTS:
        p = equipped.get(slot)
        if not isinstance(p, dict):
            print(f"  {slot.title():<12} Empty")
            continue
        fx = ", ".join(str(x) for x in p.get("effects", [])) or "none"
        status = "BROKEN" if _safe_int(p.get("armor_hp", 0), 0) <= 0 else "active"
        print(f"  {slot.title():<12} {p.get('name')} | {p.get('armor_hp',0)}/{p.get('max_armor_hp',0)} Armor | Weight {p.get('weight',0)} | {status} | {fx}")


def _print_set(armor_set: Dict) -> None:
    print(f"{armor_set.get('name')} — {armor_set.get('description','')} | TOTAL ARMOR {armor_set.get('total_armor',0)}")
    for p in armor_set.get("pieces", []):
        effects = ", ".join(str(x) for x in p.get("effects", [])) or "none"
        print(f"    {p['slot'].title():<12} {p.get('name')} | Armor {p.get('armor_hp')} | Weight {p.get('weight')} | Effects: {effects}")


def run_starting_armor_creation(game_master) -> Dict:
    player = game_master.state.data.setdefault("player", {})
    world = game_master.state.data.get("world_profile") or game_master.state.data.get("world") or {}
    print("\n" + "="*48 + "\nSTARTING ARMOR\n" + "="*48)
    print("Armor is a separate health bar and does NOT increase AC. Beginner armor totals only 10-20 Armor HP.")
    print("Slots: Helmet, Breastplate, Pants, Gloves, Boots. Broken pieces stop giving effects until repaired.\n")
    while True:
        mode = input("1. Describe your own armor\n2. Let the AI give you 3 armor options\nChoose 1 or 2: ").strip()
        if mode in {"1","2"}: break
    if mode == "1":
        request = input("Describe what you want your armor to look like and do: ").strip()
        choices = generate_starting_armor(game_master.provider, world, player, request=request, custom=True)
    else:
        choices = generate_starting_armor(game_master.provider, world, player, custom=False)
    print("\nBEGINNER ARMOR OPTIONS")
    for i, choice in enumerate(choices, 1):
        print(f"\n{i}."); _print_set(choice)
    if len(choices) == 1:
        chosen = choices[0]
        print("\nYour description was converted to balanced Beginner armor.")
    else:
        while True:
            try: idx = int(input("\nChoose an armor option: ").strip()) - 1
            except ValueError: idx = -1
            if 0 <= idx < len(choices): chosen = choices[idx]; break
    equipped = {p["slot"]: deepcopy(p) for p in chosen["pieces"]}
    player["equipped_armor"] = equipped
    player["armor_set_name"] = chosen.get("name")
    sync_armor_summary(player)
    base_movement = int(player.get("movement", 1) or 1)
    player["base_movement_without_armor"] = base_movement
    player["movement"] = effective_movement(base_movement, equipped)
    player.setdefault("inventory", []).extend(deepcopy(chosen["pieces"]))
    game_master.state.save()
    print(f"\nEquipped {chosen.get('name')}: Armor {player['armor']}/{player['max_armor']} | Weight {player['armor_weight']} | Movement {player['movement']}")
    return deepcopy(chosen)