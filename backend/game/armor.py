"""Five-slot armor system and starting armor creation."""
from __future__ import annotations
from copy import deepcopy
import json
import re
from typing import Dict, List

ARMOR_SLOTS = ("helmet", "breastplate", "pants", "gloves", "boots")
CORE_STATS = ("health", "resource", "strength", "dexterity", "agility", "constitution", "intelligence", "wisdom", "charisma", "speed", "defense", "luck", "magic")
STARTING_ARMOR_MIN = 10
STARTING_ARMOR_MAX = 20
STARTING_STAT_BONUS_BUDGET = 3


def _safe_int(value, default: int = 0) -> int:
    if isinstance(value, bool): return int(value)
    if isinstance(value, (int, float)): return int(value)
    text = str(value or "").strip().lower()
    if not text: return int(default)
    words = {"very light":1,"ultralight":1,"light":2,"lightweight":2,"medium":3,"moderate":3,"balanced":3,"heavy":5,"very heavy":7,"super heavy":8}
    if text in words: return words[text]
    match = re.search(r"-?\d+", text)
    return int(match.group(0)) if match else int(default)


def normalize_armor_piece(raw: Dict) -> Dict:
    piece = deepcopy(raw) if isinstance(raw, dict) else {}
    slot = str(piece.get("slot") or "").strip().lower()
    if slot not in ARMOR_SLOTS: slot = "breastplate"
    piece["slot"] = slot; piece["type"] = "armor"
    piece["armor_hp"] = max(0, _safe_int(piece.get("armor_hp", 0), 0))
    piece["max_armor_hp"] = max(piece["armor_hp"], _safe_int(piece.get("max_armor_hp", piece["armor_hp"]), piece["armor_hp"]))
    piece["weight"] = max(0, _safe_int(piece.get("weight", 0), 0))

    # Armor has NO mini abilities. It may only grant a passive bonus to one core stat.
    raw_bonus = piece.get("stat_bonus") if isinstance(piece.get("stat_bonus"), dict) else {}
    stat = str(raw_bonus.get("stat") or "").strip().lower()
    amount = max(0, min(3, _safe_int(raw_bonus.get("amount", 0), 0)))
    piece["stat_bonus"] = {"stat": stat, "amount": amount} if stat in CORE_STATS and amount > 0 else None
    piece.pop("effects", None)
    piece.pop("effect", None)
    piece.pop("armor_bonus", None)
    return piece


def armor_totals(equipped: Dict) -> Dict:
    pieces = [p for p in (equipped or {}).values() if isinstance(p, dict)]
    return {"armor":sum(max(0,_safe_int(p.get("armor_hp",0),0)) for p in pieces), "max_armor":sum(max(0,_safe_int(p.get("max_armor_hp",p.get("armor_hp",0)),0)) for p in pieces), "weight":sum(max(0,_safe_int(p.get("weight",0),0)) for p in pieces)}


def armor_stat_bonuses(equipped: Dict) -> Dict[str, int]:
    bonuses = {stat: 0 for stat in CORE_STATS}
    for piece in (equipped or {}).values():
        if not isinstance(piece, dict) or _safe_int(piece.get("armor_hp", 0), 0) <= 0: continue
        bonus = piece.get("stat_bonus") if isinstance(piece.get("stat_bonus"), dict) else {}
        stat = str(bonus.get("stat") or "").lower()
        amount = max(0, min(3, _safe_int(bonus.get("amount", 0), 0)))
        if stat in bonuses: bonuses[stat] += amount
    return {k:v for k,v in bonuses.items() if v}


def apply_armor_stat_bonuses(base_stats: Dict, equipped: Dict) -> Dict:
    result = deepcopy(base_stats) if isinstance(base_stats, dict) else {}
    for stat in CORE_STATS: result[stat] = max(0, min(100, _safe_int(result.get(stat, 0), 0)))
    for stat, amount in armor_stat_bonuses(equipped).items(): result[stat] = min(100, result[stat] + amount)
    return result


def armor_weight_movement_penalty(weight: int) -> int:
    weight = max(0, _safe_int(weight, 0))
    if weight >= 30: return 3
    if weight >= 22: return 2
    if weight >= 14: return 1
    return 0


def effective_movement(base_movement: int, equipped: Dict) -> int:
    return max(1, int(base_movement) - armor_weight_movement_penalty(armor_totals(equipped)["weight"]))


def sync_armor_summary(actor: Dict) -> Dict:
    equipped = actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"), dict) else {}
    totals = armor_totals(equipped)
    actor["armor"] = totals["armor"]; actor["max_armor"] = totals["max_armor"]; actor["armor_weight"] = totals["weight"]
    actor["armor_stat_bonuses"] = armor_stat_bonuses(equipped)
    return totals


def apply_damage_to_armor(actor: Dict, damage: int, *, damage_type: str | None = None) -> Dict:
    incoming = max(0, int(damage or 0)); equipped = actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"), dict) else {}
    sync_armor_summary(actor); armor_before = int(actor.get("armor",0) or 0); hp_before = int(actor.get("hp",0) or 0)
    absorbed = min(armor_before, incoming); overflow = incoming - absorbed; remaining = absorbed
    pieces = sorted([p for p in equipped.values() if isinstance(p,dict)], key=lambda p:(str(p.get("slot"))!="breastplate", -_safe_int(p.get("armor_hp",0),0)))
    broken=[]
    for piece in pieces:
        if remaining<=0: break
        current=max(0,_safe_int(piece.get("armor_hp",0),0)); take=min(current,remaining); piece["armor_hp"]=current-take; remaining-=take
        if current>0 and piece["armor_hp"]==0: broken.append(str(piece.get("name") or piece.get("slot") or "Armor piece"))
    actor["hp"] = max(0, hp_before-overflow); actor["defeated"] = actor["hp"]<=0; sync_armor_summary(actor)
    return {"incoming_damage":int(damage or 0),"resisted_damage":0,"armor_absorbed":absorbed,"hp_damage":overflow,"armor_before":armor_before,"armor_after":int(actor.get("armor",0)),"max_armor":int(actor.get("max_armor",0)),"hp_before":hp_before,"hp_after":int(actor.get("hp",0)),"broken_pieces":broken}


def repair_armor(actor: Dict, amount: int | None = None) -> Dict:
    equipped=actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"),dict) else {}; before=armor_totals(equipped)["armor"]; remaining=None if amount is None else max(0,int(amount)); repaired=0
    for slot in ARMOR_SLOTS:
        piece=equipped.get(slot)
        if not isinstance(piece,dict): continue
        current=max(0,_safe_int(piece.get("armor_hp",0),0)); maximum=max(current,_safe_int(piece.get("max_armor_hp",current),current)); missing=maximum-current; add=missing if remaining is None else min(missing,remaining); piece["armor_hp"]=current+add; repaired+=add
        if remaining is not None:
            remaining-=add
            if remaining<=0: break
    sync_armor_summary(actor); return {"repaired":repaired,"armor_before":before,"armor_after":actor.get("armor",0),"max_armor":actor.get("max_armor",0)}


def _fallback_sets(description: str = "") -> List[Dict]:
    return [
        {"name":"Mobile Starter Set","description":description or "Light protection built for mobility.","pieces":[{"name":"Light Headgear","slot":"helmet","armor_hp":2,"weight":1,"stat_bonus":None},{"name":"Light Body Armor","slot":"breastplate","armor_hp":5,"weight":2,"stat_bonus":None},{"name":"Flexible Leg Armor","slot":"pants","armor_hp":3,"weight":1,"stat_bonus":{"stat":"agility","amount":1}},{"name":"Grip Gloves","slot":"gloves","armor_hp":2,"weight":1,"stat_bonus":{"stat":"dexterity","amount":1}},{"name":"Runner Boots","slot":"boots","armor_hp":2,"weight":1,"stat_bonus":{"stat":"speed","amount":1}}]},
        {"name":"Balanced Starter Set","description":description or "Balanced beginner protection.","pieces":[{"name":"Guard Helmet","slot":"helmet","armor_hp":3,"weight":1,"stat_bonus":{"stat":"wisdom","amount":1}},{"name":"Guard Breastplate","slot":"breastplate","armor_hp":7,"weight":3,"stat_bonus":{"stat":"defense","amount":1}},{"name":"Guard Pants","slot":"pants","armor_hp":3,"weight":1,"stat_bonus":None},{"name":"Guard Gloves","slot":"gloves","armor_hp":2,"weight":1,"stat_bonus":{"stat":"strength","amount":1}},{"name":"Guard Boots","slot":"boots","armor_hp":2,"weight":1,"stat_bonus":None}]},
        {"name":"Heavy Starter Set","description":description or "Tough beginner protection with extra weight.","pieces":[{"name":"Heavy Helmet","slot":"helmet","armor_hp":3,"weight":2,"stat_bonus":None},{"name":"Heavy Breastplate","slot":"breastplate","armor_hp":8,"weight":5,"stat_bonus":{"stat":"constitution","amount":2}},{"name":"Heavy Pants","slot":"pants","armor_hp":4,"weight":3,"stat_bonus":None},{"name":"Heavy Gloves","slot":"gloves","armor_hp":2,"weight":2,"stat_bonus":{"stat":"strength","amount":1}},{"name":"Heavy Boots","slot":"boots","armor_hp":3,"weight":3,"stat_bonus":None}]}
    ]


def _starting_weight_target(total_armor: int) -> int:
    """Tie protection to a meaningful movement tradeoff for starting armor."""
    total_armor = max(STARTING_ARMOR_MIN, min(STARTING_ARMOR_MAX, int(total_armor)))
    if total_armor <= 12:
        return 7   # Light: no movement penalty.
    if total_armor <= 16:
        return 12  # Balanced: heavier, but still no movement penalty.
    if total_armor <= 19:
        return 17  # Protective: -1 Movement.
    return 23      # Maximum starter protection: -2 Movement.


def _rebalance_piece_weights(pieces: List[Dict], target_weight: int) -> None:
    """Scale piece weights to an exact set total while keeping every real piece believable."""
    minimums = [1 if int(piece.get("armor_hp", 0) or 0) > 0 else 0 for piece in pieces]
    raw_weights = [max(minimums[i], int(piece.get("weight", 0) or 0)) for i, piece in enumerate(pieces)]
    if sum(raw_weights) <= 0:
        raw_weights = [max(minimums[i], int(piece.get("armor_hp", 0) or 0)) for i, piece in enumerate(pieces)]

    raw_total = max(1, sum(raw_weights))
    scaled = [max(minimums[i], round(raw_weights[i] * target_weight / raw_total)) for i in range(len(pieces))]
    difference = target_weight - sum(scaled)
    adjustment_order = [1, 2, 0, 4, 3]  # Breastplate and pants carry most weight.
    cursor = 0
    while difference != 0 and cursor < 500:
        index = adjustment_order[cursor % len(adjustment_order)]
        if difference > 0:
            scaled[index] += 1
            difference -= 1
        elif scaled[index] > minimums[index]:
            scaled[index] -= 1
            difference += 1
        cursor += 1

    for piece, weight in zip(pieces, scaled):
        piece["weight"] = max(0, int(weight))


def _custom_armor_target(request: str) -> int:
    text = str(request or "").lower()
    if any(word in text for word in ("heavy", "tank", "fortress", "reinforced", "full plate", "maximum protection")):
        return 20
    if any(word in text for word in ("light", "lightweight", "stealth", "ninja", "scout", "mobile", "speed", "flexible")):
        return 11
    return 15


def _normalize_set(raw: Dict, target_total: int) -> Dict:
    result=deepcopy(raw) if isinstance(raw,dict) else {}; pieces_raw=result.get("pieces",[]) if isinstance(result.get("pieces"),list) else []
    by_slot={str(p.get("slot","")).lower():normalize_armor_piece(p) for p in pieces_raw if isinstance(p,dict)}; pieces=[]
    for slot in ARMOR_SLOTS: pieces.append(by_slot.get(slot,normalize_armor_piece({"name":slot.title(),"slot":slot,"armor_hp":0,"weight":0,"stat_bonus":None})))
    target_total=max(STARTING_ARMOR_MIN,min(STARTING_ARMOR_MAX,int(target_total))); current=sum(p["armor_hp"] for p in pieces)
    if current<=0: pieces[1]["armor_hp"]=target_total
    elif current!=target_total:
        scaled=[max(0,round(p["armor_hp"]*target_total/current)) for p in pieces]; diff=target_total-sum(scaled); scaled[1]+=diff
        for p,hp in zip(pieces,scaled): p["armor_hp"]=max(0,hp)
    _rebalance_piece_weights(pieces, _starting_weight_target(target_total))
    # Beginner armor gets only a small passive stat-bonus budget across the whole set.
    budget=STARTING_STAT_BONUS_BUDGET
    for p in pieces:
        bonus=p.get("stat_bonus") if isinstance(p.get("stat_bonus"),dict) else None
        if not bonus or budget<=0: p["stat_bonus"]=None; continue
        amount=min(max(1,_safe_int(bonus.get("amount",1),1)),3,budget); p["stat_bonus"]={"stat":bonus["stat"],"amount":amount}; budget-=amount
    for p in pieces: p["max_armor_hp"]=p["armor_hp"]
    result["pieces"]=pieces; result["total_armor"]=sum(p["armor_hp"] for p in pieces); result["total_weight"]=sum(p["weight"] for p in pieces); result["tier"]="beginner"; return result


def generate_starting_armor(provider, world: Dict, player: Dict, request: str = "", custom: bool = False) -> List[Dict]:
    client=getattr(provider,"client",None); model=getattr(provider,"model",None)
    if client is None or not model:
        sets=_fallback_sets(request)
        targets=[_custom_armor_target(request)] if custom else [11,15,20]
        return [_normalize_set(s,targets[min(i,len(targets)-1)]) for i,s in enumerate(sets[:len(targets)])]
    instructions="""Return ONLY JSON. Generate beginner armor using the confirmed world and character. Armor NEVER adds AC. Armor is a separate health bar that absorbs damage before HP. There are exactly five slots: helmet, breastplate, pants, gloves, boots. Protection and weight MUST rise together: light armor is about 11 Armor HP and Weight 7; balanced armor is about 15 Armor HP and Weight 12; maximum-protection starter armor is 20 Armor HP and Weight 23, which costs -2 Movement. Never describe high-protection armor as lightweight. Breastplate usually provides the most Armor HP and weight. Python enforces the final totals.
If custom_mode=false, return exactly three sets in this order: LIGHT, BALANCED, HEAVY. If custom_mode=true, match the requested protection style; stealth, ninja, scout, mobile, or lightweight concepts should be light rather than receiving maximum Armor HP.
ARMOR PIECES DO NOT HAVE MINI-ABILITIES, ACTIVE POWERS, MOVEMENT EFFECTS, RESISTANCES, SHIELDS, ATTACKS, HEALING, JET-PACK ACTIONS, OR OTHER SPECIAL MECHANICS. Their ONLY bonus beyond Armor HP is an optional passive stat_bonus to ONE of the 13 core stats: health, resource, strength, dexterity, agility, constitution, intelligence, wisdom, charisma, speed, defense, luck, magic. stat_bonus.amount must be an integer from 1 to 3. Beginner sets should be modest; do not put bonuses on every piece and keep the total bonus small. If the player describes something like a jet pack, powered gloves, targeting visor, flame lining, etc., preserve that in the LOOK/DESCRIPTION but translate the mechanical benefit ONLY into an appropriate stat bonus, e.g. speed, agility, dexterity, defense, or constitution.
Every piece needs name, slot, armor_hp, weight, stat_bonus. armor_hp and weight MUST be JSON integers. stat_bonus must be null or {\"stat\":\"speed\",\"amount\":1}. If custom_request is supplied, honor its appearance/theme but balance it to Beginner strength. If custom_mode=true return exactly 1 set; otherwise exactly 3 choices. Top-level JSON: {\"sets\":[{\"name\":...,\"description\":...,\"pieces\":[...]}]}."""
    payload={"world":world,"player":{"class":player.get("class"),"stats":player.get("stats"),"appearance":player.get("appearance")},"custom_mode":custom,"custom_request":request}
    response=client.responses.create(model=model,instructions=instructions,input=json.dumps(payload,ensure_ascii=False,default=str))
    try: data=json.loads(response.output_text.strip())
    except Exception: data={}
    sets=data.get("sets",[]) if isinstance(data,dict) else []
    if not isinstance(sets,list) or len(sets)!=(1 if custom else 3): sets=_fallback_sets(request)[:1] if custom else _fallback_sets()
    targets=[_custom_armor_target(request)] if custom else [11,15,20]
    return [_normalize_set(s,targets[min(i,len(targets)-1)]) for i,s in enumerate(sets)]


def _bonus_text(piece: Dict) -> str:
    bonus=piece.get("stat_bonus") if isinstance(piece.get("stat_bonus"),dict) else None
    return f"+{bonus['amount']} {str(bonus['stat']).title()}" if bonus else "none"


def print_armor(actor: Dict) -> None:
    equipped=actor.get("equipped_armor") if isinstance(actor.get("equipped_armor"),dict) else {}; totals=sync_armor_summary(actor)
    print(f"\nARMOR — {actor.get('armor_set_name') or 'Mixed Set'}"); print(f"Armor HP: {totals['armor']}/{totals['max_armor']} | Weight: {totals['weight']} | Weight movement penalty: -{armor_weight_movement_penalty(totals['weight'])}")
    bonuses=armor_stat_bonuses(equipped); print("Active stat bonuses: "+(", ".join(f"+{v} {k.title()}" for k,v in bonuses.items()) if bonuses else "none"))
    for slot in ARMOR_SLOTS:
        p=equipped.get(slot)
        if not isinstance(p,dict): print(f"  {slot.title():<12} Empty"); continue
        status="BROKEN" if _safe_int(p.get("armor_hp",0),0)<=0 else "active"
        print(f"  {slot.title():<12} {p.get('name')} | {p.get('armor_hp',0)}/{p.get('max_armor_hp',0)} Armor | Weight {p.get('weight',0)} | {status} | Bonus: {_bonus_text(p)}")


def _print_set(armor_set: Dict) -> None:
    print(f"{armor_set.get('name')} — {armor_set.get('description','')} | TOTAL ARMOR {armor_set.get('total_armor',0)}")
    for p in armor_set.get("pieces",[]): print(f"    {p['slot'].title():<12} {p.get('name')} | Armor {p.get('armor_hp')} | Weight {p.get('weight')} | Bonus: {_bonus_text(p)}")


def run_starting_armor_creation(game_master) -> Dict:
    player=game_master.state.data.setdefault("player",{}); world=game_master.state.data.get("world_profile") or game_master.state.data.get("world") or {}
    print("\n"+"="*48+"\nSTARTING ARMOR\n"+"="*48); print("Armor is a separate health bar and does NOT increase AC. Beginner armor totals only 10-20 Armor HP."); print("Slots: Helmet, Breastplate, Pants, Gloves, Boots. Pieces can only give small passive +1/+2/+3 bonuses to core stats. Broken pieces lose their stat bonus until repaired.\n")
    while True:
        mode=input("1. Describe your own armor\n2. Let the AI give you 3 armor options\nChoose 1 or 2: ").strip()
        if mode in {"1","2"}: break
    if mode=="1":
        request=input("Describe what you want your armor to look like and what kind of build it should support: ").strip(); choices=generate_starting_armor(game_master.provider,world,player,request=request,custom=True)
    else: choices=generate_starting_armor(game_master.provider,world,player,custom=False)
    print("\nBEGINNER ARMOR OPTIONS")
    for i,choice in enumerate(choices,1): print(f"\n{i}."); _print_set(choice)
    if len(choices)==1: chosen=choices[0]; print("\nYour description was converted to balanced Beginner armor.")
    else:
        while True:
            try: idx=int(input("\nChoose an armor option: ").strip())-1
            except ValueError: idx=-1
            if 0<=idx<len(choices): chosen=choices[idx]; break
    equipped={p["slot"]:deepcopy(p) for p in chosen["pieces"]}; player["equipped_armor"]=equipped; player["armor_set_name"]=chosen.get("name"); sync_armor_summary(player)
    base_movement=int(player.get("movement",1) or 1); player["base_movement_without_armor"]=base_movement; player["movement"]=effective_movement(base_movement,equipped)
    player.setdefault("inventory",[]).extend(deepcopy(chosen["pieces"])); game_master.state.save()
    print(f"\nEquipped {chosen.get('name')}: Armor {player['armor']}/{player['max_armor']} | Weight {player['armor_weight']} | Movement {player['movement']}"); return deepcopy(chosen)
