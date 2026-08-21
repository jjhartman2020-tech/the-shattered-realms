"""Five-slot armor system and starting armor creation."""
from __future__ import annotations
from copy import deepcopy
import json
from typing import Dict, List

ARMOR_SLOTS = ("helmet", "breastplate", "pants", "gloves", "boots")
STARTING_ARMOR_MIN = 10
STARTING_ARMOR_MAX = 20


def normalize_armor_piece(raw: Dict) -> Dict:
    piece = deepcopy(raw) if isinstance(raw, dict) else {}
    slot = str(piece.get("slot") or "").strip().lower()
    if slot not in ARMOR_SLOTS:
        slot = "breastplate"
    piece["slot"] = slot
    piece["type"] = "armor"
    piece["armor_hp"] = max(0, int(piece.get("armor_hp", 0) or 0))
    piece["max_armor_hp"] = piece["armor_hp"]
    piece["weight"] = max(0, int(piece.get("weight", 0) or 0))
    effects = piece.get("effects", [])
    piece["effects"] = effects if isinstance(effects, list) else ([str(effects)] if effects else [])
    piece.pop("armor_bonus", None)  # Armor never adds AC in this ruleset.
    return piece


def armor_totals(equipped: Dict) -> Dict:
    pieces = [p for p in (equipped or {}).values() if isinstance(p, dict)]
    return {
        "armor": sum(max(0, int(p.get("armor_hp", 0) or 0)) for p in pieces),
        "max_armor": sum(max(0, int(p.get("max_armor_hp", p.get("armor_hp", 0)) or 0)) for p in pieces),
        "weight": sum(max(0, int(p.get("weight", 0) or 0)) for p in pieces),
    }


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
    # Hard beginner balance guard: whole starting set must total 10-20 Armor HP.
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
    instructions = """Return ONLY JSON. Generate beginner armor for a genre-neutral RPG using the confirmed world and character. Armor NEVER adds AC. Armor is a separate health bar that absorbs damage before HP. There are exactly five slots: helmet, breastplate, pants, gloves, boots. A full STARTING set must total only 10-20 Armor HP so beginner armor is not overpowered. Breastplate usually provides the most Armor HP. Pieces may have small thematic effects such as +1 movement square or modest resistance, but beginner effects must be weak. Heavier protection may have movement penalties. Every piece needs name, slot, armor_hp, weight, effects. Do not add permanent core-stat increases. If custom_request is supplied, honor its appearance/theme but BALANCE its mechanics to beginner strength. If custom_mode=true return exactly 1 set. Otherwise return exactly 3 meaningfully different choices. Top-level JSON: {\"sets\":[{\"name\":...,\"description\":...,\"pieces\":[...]}]}."""
    payload = {"world": world, "player": {"class": player.get("class"), "stats": player.get("stats"), "appearance": player.get("appearance")}, "custom_mode": custom, "custom_request": request}
    response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, default=str))
    try: data = json.loads(response.output_text.strip())
    except Exception: data = {}
    sets = data.get("sets", []) if isinstance(data, dict) else []
    if not isinstance(sets, list) or len(sets) != (1 if custom else 3):
        sets = _fallback_sets(request)[:1] if custom else _fallback_sets()
    targets = [15] if custom else [14,17,20]
    return [_normalize_set(s, targets[min(i, len(targets)-1)]) for i, s in enumerate(sets)]


def _print_set(armor_set: Dict) -> None:
    print(f"{armor_set.get('name')} — {armor_set.get('description','')} | TOTAL ARMOR {armor_set.get('total_armor',0)}")
    for p in armor_set.get("pieces", []):
        effects = ", ".join(str(x) for x in p.get("effects", [])) or "none"
        print(f"    {p['slot'].title():<12} {p.get('name')} | Armor {p.get('armor_hp')} | Weight {p.get('weight')} | Effects: {effects}")


def run_starting_armor_creation(game_master) -> Dict:
    player = game_master.state.data.setdefault("player", {})
    world = game_master.state.data.get("world_profile") or game_master.state.data.get("world") or {}
    print("\n" + "="*48 + "\nSTARTING ARMOR\n" + "="*48)
    print("Armor is a separate health bar and does NOT increase AC. Your beginner armor will total only 10-20 Armor HP.")
    print("Slots: Helmet, Breastplate, Pants, Gloves, Boots.\n")
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
    totals = armor_totals(equipped)
    player["equipped_armor"] = equipped
    player["armor_set_name"] = chosen.get("name")
    player["armor"] = totals["armor"]
    player["max_armor"] = totals["max_armor"]
    player["armor_weight"] = totals["weight"]
    player.setdefault("inventory", []).extend(deepcopy(chosen["pieces"]))
    game_master.state.save()
    print(f"\nEquipped {chosen.get('name')}: Armor {player['armor']}/{player['max_armor']} | Total Weight {player['armor_weight']}")
    return deepcopy(chosen)
