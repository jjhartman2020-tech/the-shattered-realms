"""Ability learning, tier gates, AI-generated choices, and four-slot loadout rules."""
from copy import deepcopy
import json
from typing import Dict, List

from .dice import normalize_damage_expression
from .progression import ABILITY_TIER_COSTS

MAX_ABILITY_SLOTS = 4
ABILITY_TIER_LEVELS = {"beginner": 1, "novice": 3, "expert": 10, "master": 25, "legendary": 50}
TIER_ORDER = ("beginner", "novice", "expert", "master", "legendary")


def normalize_tier(tier: str | None) -> str:
    value = str(tier or "beginner").strip().lower()
    return value if value in ABILITY_TIER_COSTS else "beginner"


def highest_unlocked_tier(level: int) -> str:
    level = max(1, int(level or 1)); unlocked = "beginner"
    for tier in TIER_ORDER:
        if level >= ABILITY_TIER_LEVELS[tier]: unlocked = tier
    return unlocked


def tier_is_unlocked(level: int, tier: str) -> bool:
    tier = normalize_tier(tier)
    return int(level or 1) >= ABILITY_TIER_LEVELS[tier]


def ability_ap_cost(ability: Dict) -> int:
    return ABILITY_TIER_COSTS[normalize_tier(ability.get("tier"))]


def _tier_resource_cost(tier: str) -> int:
    return {"beginner": 10, "novice": 20, "expert": 35, "master": 55, "legendary": 80}[tier]


def _fallback_library(player: Dict) -> List[Dict]:
    level = int(player.get("level", 1) or 1)
    available_tiers = [tier for tier in TIER_ORDER if tier_is_unlocked(level, tier)]
    names = {"beginner": ("Driving Blow", "Quick Guard"), "novice": ("Relentless Rush", "Focused Burst"),
             "expert": ("Crushing Arc", "Phantom Advance"), "master": ("Dominion Strike", "Impossible Step"),
             "legendary": ("Worldsplitter", "Untouchable Moment")}
    results = []
    for tier in available_tiers:
        base_cost = _tier_resource_cost(tier)
        for index, name in enumerate(names[tier]):
            ability = {"name": name, "description": f"A {tier} technique shaped by the character's class.",
                       "type": "active", "category": "offensive" if index == 0 else "mobility",
                       "tier": tier, "ability_point_cost": ABILITY_TIER_COSTS[tier], "resource": "class",
                       "resource_cost": base_cost, "target": "enemy" if index == 0 else "self",
                       "range": 1 if index == 0 else 0}
            if index == 0:
                ability.update({"damage": {"beginner":"1d6","novice":"1d8","expert":"2d6","master":"3d6","legendary":"4d8"}[tier],
                                "attack_attribute":"strength", "requires_attack_roll":True})
            else:
                ability.update({"movement_squares": {"beginner":2,"novice":3,"expert":5,"master":7,"legendary":10}[tier],
                                "requires_attack_roll":False})
            results.append(ability)
    return results[-6:]


def _normalize_generated(raw: List[Dict], level: int) -> List[Dict]:
    result = []
    aliases = {
        "heal": "healing", "healing_amount": "healing",
        "shield_amount": "shield", "shielding": "shield",
        "move": "movement_squares", "movement": "movement_squares", "movement_distance": "movement_squares",
        "targets": "target_count", "number_of_targets": "target_count",
        "aoe": "area", "area_size": "area",
    }
    for entry in raw:
        if not isinstance(entry, dict): continue
        ability = deepcopy(entry)
        for old_key, new_key in aliases.items():
            if new_key not in ability and old_key in ability:
                ability[new_key] = ability[old_key]
        tier = normalize_tier(ability.get("tier"))
        if not tier_is_unlocked(level, tier): continue
        ability["tier"] = tier
        ability["ability_point_cost"] = ABILITY_TIER_COSTS[tier]
        ability["type"] = "active"
        ability["resource"] = "class"
        default_cost = _tier_resource_cost(tier)
        ability["resource_cost"] = max(5, int(round(max(5, int(ability.get("resource_cost", default_cost) or default_cost)) / 5.0)) * 5)
        ability.setdefault("target", "enemy")
        ability.setdefault("range", 1)
        if ability.get("damage") not in (None, "", 0, "0"):
            ability["damage"] = normalize_damage_expression(ability.get("damage"), "1d4")
        if ability.get("healing") not in (None, "", 0, "0"):
            ability["healing"] = normalize_damage_expression(ability.get("healing"), "1d4")
        result.append(ability)
    return result[:6]


def generate_ability_choices(provider, player: Dict) -> List[Dict]:
    level = int(player.get("level", 1) or 1)
    client = getattr(provider, "client", None); model = getattr(provider, "model", None)
    if client is None or not model: return _fallback_library(player)
    available_tiers = [tier for tier in TIER_ORDER if tier_is_unlocked(level, tier)]
    instructions = """Generate exactly 6 learnable active abilities for The Shattered Realms. Return ONLY a JSON array.
Use the supplied custom class, backstory, stats, level, resource name, and current abilities as inspiration. Do not repeat an ability the player already knows.
Only use tiers listed in unlocked_tiers. Tier AP costs are fixed: Beginner=1, Novice=3, Expert=6, Master=10, Legendary=15.
Power must meaningfully rise by tier. Stronger abilities should generally have higher Resource costs and stronger exact effects.
EVERY ability must expose its exact gameplay numbers. If it deals damage include `damage`; if it heals include `healing`; if it shields include `shield`; if it moves the user/target include `movement_squares`; if it lasts include `duration`; if it affects multiple targets include `target_count`; if it has an area include `area`; if it modifies a stat include the exact numeric modifier. Never hide these values only inside description/effect prose.
Damage and healing MUST use dice notation such as 1d4, 1d6, 1d8, 2d6, 2d8, or 3d6. Never output a fixed damage number like 4, 6, or 10.
Every ability must also include: name, description, type='active', category, tier, resource_cost, target, range, requires_attack_roll.
Resource costs must be positive multiples of 5. An ability may cost more Resource than the player's current maximum; that is allowed. The player can learn/equip it but cannot use it until they can pay the full Resource cost.
Do not use cooldowns. Do not create basic weapon attacks; these are abilities."""
    payload = {"name": player.get("name"), "class": player.get("class"), "backstory": player.get("background"),
               "level": level, "stats": player.get("stats", {}), "resource_name": player.get("resource_name"),
               "max_resource": player.get("max_resource", 0), "unlocked_tiers": available_tiers,
               "known_abilities": [a.get("name") for a in player.get("equipped_abilities", []) if isinstance(a, dict)]}
    response = client.responses.create(model=model, instructions=instructions, input=json.dumps(payload, ensure_ascii=False, indent=2))
    try: parsed = json.loads(response.output_text.strip())
    except json.JSONDecodeError: parsed = []
    choices = _normalize_generated(parsed if isinstance(parsed, list) else [], level)
    return choices if len(choices) >= 3 else _fallback_library(player)


def available_to_learn(player: Dict, abilities: List[Dict]) -> List[Dict]:
    known = {str(a.get("name", "")).strip().lower() for a in player.get("equipped_abilities", []) if isinstance(a, dict)}
    level = int(player.get("level", 1) or 1); result = []
    for raw in abilities:
        if not isinstance(raw, dict): continue
        ability = deepcopy(raw); tier = normalize_tier(ability.get("tier")); ability["tier"] = tier
        if str(ability.get("name", "")).strip().lower() in known or not tier_is_unlocked(level, tier): continue
        ability["ability_point_cost"] = ability_ap_cost(ability); result.append(ability)
    return result


def learn_ability(player: Dict, ability: Dict, forget_index: int | None = None) -> Dict:
    if not isinstance(ability, dict) or not str(ability.get("name", "")).strip(): raise ValueError("Invalid ability")
    level = int(player.get("level", 1) or 1); tier = normalize_tier(ability.get("tier"))
    if not tier_is_unlocked(level, tier): raise ValueError(f"{tier.title()} abilities unlock at Level {ABILITY_TIER_LEVELS[tier]}")
    cost = ability_ap_cost(ability); ap = int(player.get("ability_points", 0) or 0)
    if ap < cost: raise ValueError(f"You need {cost} AP but only have {ap}")
    equipped = player.get("equipped_abilities")
    if not isinstance(equipped, list): equipped = []
    if any(isinstance(a, dict) and str(a.get("name", "")).strip().lower() == str(ability.get("name", "")).strip().lower() for a in equipped):
        raise ValueError("You already know that ability")
    forgotten = None
    if len(equipped) >= MAX_ABILITY_SLOTS:
        if forget_index is None or not 0 <= int(forget_index) < len(equipped):
            raise ValueError("All 4 ability slots are full; choose one current ability to forget")
        forgotten = equipped.pop(int(forget_index))
    learned = deepcopy(ability); learned["tier"] = tier; learned["ability_point_cost"] = cost
    equipped.append(learned); player["equipped_abilities"] = equipped; player["unlocked_abilities"] = deepcopy(equipped)
    player["ability_points"] = ap - cost
    return {"learned": deepcopy(learned), "forgotten": deepcopy(forgotten), "ability_points_remaining": player["ability_points"]}


def _effect_text(ability: Dict, resource_name: str) -> str:
    parts = [f"{normalize_tier(ability.get('tier')).title()} — {ability_ap_cost(ability)} AP"]
    fields = (("damage", "Damage", ""), ("healing", "Heal", ""), ("shield", "Shield", ""),
              ("movement_squares", "Move", " squares"), ("target_count", "Targets", ""),
              ("area", "Area", ""), ("duration", "Duration", " rounds"))
    for key, label, suffix in fields:
        value = ability.get(key)
        if value not in (None, "", 0, "0"):
            if key in {"damage", "healing"}:
                value = normalize_damage_expression(value, "1d4")
            text = str(value)
            if key == "duration" and any(word in text.lower() for word in ("round", "turn", "second", "minute")):
                suffix = ""
            parts.append(f"{label} {text}{suffix}")
    if ability.get("range") is not None: parts.append(f"Range {ability.get('range')} squares")
    if ability.get("attack_attribute"): parts.append(f"Uses {str(ability.get('attack_attribute')).title()}")
    parts.append(f"Cost {int(ability.get('resource_cost', 0) or 0)} {resource_name}")
    if ability.get("status_effect"): parts.append(f"Status {ability.get('status_effect')}")
    if ability.get("stat_modifier"): parts.append(f"Modifier {ability.get('stat_modifier')}")
    if ability.get("effect"): parts.append(str(ability.get("effect")))
    return " | ".join(parts)


def run_ap_spending_screen(game_master) -> Dict:
    state = game_master.state; player = state.data.setdefault("player", {})
    if state.data.get("combat", {}).get("active"):
        print("You cannot learn or forget abilities during combat."); return deepcopy(player)
    if not player.get("character_creation_complete"):
        print("Finish character creation before learning new abilities."); return deepcopy(player)
    while True:
        level = int(player.get("level", 1) or 1); ap = int(player.get("ability_points", 0) or 0)
        resource_name = str(player.get("resource_name") or "Resource")
        print("\n" + "=" * 56); print("ABILITY LEARNING")
        print(f"Level {level} | Stored AP: {ap} | Highest Tier: {highest_unlocked_tier(level).title()}")
        print("AP never expires. You can leave now and save every point for later.")
        print("Known abilities:")
        known = player.get("equipped_abilities", []) if isinstance(player.get("equipped_abilities"), list) else []
        for i, ability in enumerate(known, 1): print(f"  {i}. {ability.get('name')} [{_effect_text(ability, resource_name)}]")
        print(f"Slots: {len(known)}/{MAX_ABILITY_SLOTS}\n")
        choices = available_to_learn(player, generate_ability_choices(game_master.provider, player))
        if not choices:
            print("No new abilities were generated right now. Your AP remains saved."); return deepcopy(player)
        print("AVAILABLE ABILITIES")
        for i, ability in enumerate(choices, 1):
            afford = "" if ap >= ability_ap_cost(ability) else " [NOT ENOUGH AP YET]"
            resource_warning = " [RESOURCE TOO LOW TO USE YET]" if int(ability.get("resource_cost", 0) or 0) > int(player.get("max_resource", 0) or 0) else ""
            print(f"{i}. {ability.get('name')} — {ability.get('description', '')}")
            print(f"   {_effect_text(ability, resource_name)}{afford}{resource_warning}")
        answer = input("\nChoose an ability number, 'refresh' for new choices, or 'leave' to save AP: ").strip().lower()
        if answer in {"leave", "exit", "back", "done", "save"}:
            state.save(); print(f"Saved {int(player.get('ability_points', 0) or 0)} AP for later."); return deepcopy(player)
        if answer == "refresh": continue
        try: index = int(answer) - 1
        except ValueError: index = -1
        if not 0 <= index < len(choices): print("Invalid choice."); continue
        selected = choices[index]; cost = ability_ap_cost(selected)
        if ap < cost:
            print(f"You only have {ap} AP. {selected.get('name')} costs {cost} AP. Nothing was spent."); continue
        forget_index = None
        if len(known) >= MAX_ABILITY_SLOTS:
            print("\nAll 4 ability slots are full. Learning this ability permanently forgets one current ability.")
            for i, ability in enumerate(known, 1): print(f"  {i}. {ability.get('name')} — {_effect_text(ability, resource_name)}")
            raw = input("Choose the ability to forget, or type 'cancel': ").strip().lower()
            if raw == "cancel": continue
            try: forget_index = int(raw) - 1
            except ValueError: forget_index = -1
            if not 0 <= forget_index < len(known): print("Invalid choice. Nothing changed."); continue
            forgotten_name = known[forget_index].get("name")
            confirm = input(f"Forget {forgotten_name} and learn {selected.get('name')} for {cost} AP? (yes/no): ").strip().lower()
        else:
            confirm = input(f"Learn {selected.get('name')} for {cost} AP? (yes/no): ").strip().lower()
        if confirm not in {"yes", "y"}: print("Cancelled. Nothing was spent."); continue
        result = learn_ability(player, selected, forget_index); state.save()
        print(f"\nLearned {result['learned'].get('name')}! AP remaining: {result['ability_points_remaining']}")
        if result.get("forgotten"): print(f"Forgot {result['forgotten'].get('name')} permanently.")
        if int(player.get("ability_points", 0) or 0) <= 0: return deepcopy(player)
