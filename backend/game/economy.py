"""World-aware economy, shops, and Charisma haggling."""
from __future__ import annotations
from copy import deepcopy
import json, math, random, re
from typing import Dict, List

from .attributes import attribute_check_bonus, normalize_attributes
from .checks import resolve_check
from .loot import scale_item_for_rarity

SHOP_RARITY_TABLES = {
    "ordinary": {"common":82.0,"uncommon":16.0,"rare":2.0,"epic":0.0,"legendary":0.0},
    "quality": {"common":65.0,"uncommon":27.0,"rare":7.0,"epic":1.0,"legendary":0.0},
    "elite": {"common":40.0,"uncommon":35.0,"rare":20.0,"epic":5.0,"legendary":0.0},
    "special": {"common":20.0,"uncommon":30.0,"rare":30.0,"epic":18.0,"legendary":2.0},
}
SHOP_RARITIES = ("common","uncommon","rare","epic","legendary")
HAGGLE_MAX_DISCOUNT = 50

def _safe_int(v, d=0):
    try: return int(v)
    except (TypeError, ValueError): return int(d)

def currency_profile(world):
    world = world if isinstance(world,dict) else {}
    name, symbol = str(world.get("currency_name") or "").strip(), str(world.get("currency_symbol") or "").strip()
    if name: return {"name":name,"symbol":symbol,"prefix":bool(symbol)}
    economy = str(world.get("economy") or "")
    text = f"{economy} {world.get('genre','')} {world.get('era','')} {world.get('technology_level','')}".lower()
    if "$" in economy or any(x in text for x in ("dollar","usd","modern","contemporary")): return {"name":"dollars","symbol":"$","prefix":True}
    if any(x in text for x in ("credit","cyberpunk","space opera","futuristic","sci-fi","science fiction")): return {"name":"credits","symbol":"","prefix":False}
    if any(x in text for x in ("gold","medieval","fantasy")): return {"name":"gold","symbol":"","prefix":False}
    m = re.search(r"(?:currency|money|paid in|uses?)\s*(?:is|:|=)?\s*([A-Za-z][A-Za-z -]{1,24})", economy, re.I)
    return {"name":m.group(1).strip().rstrip(".,;") if m else "currency","symbol":"","prefix":False}

def format_money(amount, world_or_profile):
    amount=max(0,_safe_int(amount))
    p=world_or_profile if isinstance(world_or_profile,dict) and "prefix" in world_or_profile else currency_profile(world_or_profile)
    if p.get("symbol") and p.get("prefix"): return f"{p['symbol']}{amount:,}"
    name=str(p.get("name") or "currency")
    if amount==1 and name.endswith("s"): name=name[:-1]
    return f"{amount:,} {name}"

def ensure_wallet(game_master, *, grant_starting_funds=False):
    player=game_master.state.data.setdefault("player",{}); profile=currency_profile(game_master.state.data.get("world_profile",{}))
    wallet=player.get("wallet") if isinstance(player.get("wallet"),dict) else None
    if wallet is None:
        legacy=player.get("currency") if isinstance(player.get("currency"),dict) else {}
        amount=sum(max(0,_safe_int(v)) for v in legacy.values()) if legacy else 0
        if amount<=0 and grant_starting_funds and player.get("character_creation_complete"): amount=20
        wallet={"amount":amount,**profile}; player["wallet"]=wallet
    else:
        wallet["amount"]=max(0,_safe_int(wallet.get("amount"))); wallet.update(profile)
    game_master.state.save(); return wallet

def wallet_text(game_master): return format_money(ensure_wallet(game_master).get("amount",0),ensure_wallet(game_master))

def _normalize_shop_quality(raw, level, hint=""):
    q=str(raw or "ordinary").lower().replace(" ","_")
    q={"normal":"ordinary","common":"ordinary","good":"quality","premium":"elite","legendary":"special","mythic":"special"}.get(q,q)
    if q not in SHOP_RARITY_TABLES: q="ordinary"
    hint=str(hint).lower(); exceptional=any(x in hint for x in ("legendary","special","master","auction","black market","secret","elite","royal","military prototype"))
    if q=="special" and level<70 and not exceptional: q="elite" if level>=30 else "quality"
    if q=="elite" and level<20 and not exceptional: q="quality"
    return q

def roll_shop_rarity(quality, level=1):
    table=SHOP_RARITY_TABLES[_normalize_shop_quality(quality,level)]
    r=random.random()*100; c=0
    for rarity in SHOP_RARITIES:
        c+=table[rarity]
        if r<c: return rarity
    return "common"

def _base_value(item):
    v=max(0,_safe_int(item.get("sell_value")))
    if v: return v
    return {"weapon":10,"shield":8,"armor":8,"consumable":4,"ammo":2,"material":2,"utility":4,"tool":5,"accessory":8,"relic":12}.get(str(item.get("type") or "misc").lower(),3)

def _stock_item(raw, quality, level):
    item=deepcopy(raw) if isinstance(raw,dict) else {}
    item.update({"name":str(item.get("name") or "Unnamed Item").strip() or "Unnamed Item","type":str(item.get("type") or "misc").lower(),"quantity":max(1,min(99,_safe_int(item.get("quantity"),1))),"sell_value":_base_value(item)})
    scale_item_for_rarity(item,roll_shop_rarity(quality,level))
    item["buy_price"]=max(1,math.ceil(max(1,_safe_int(item.get("sell_value"),1))*2))
    item["original_buy_price"]=item["buy_price"]; item["haggle_attempted"]=False; item["haggle_discount_percent"]=0
    return item

def _fallback_stock(world):
    names=world.get("common_weapons_and_gear") if isinstance(world.get("common_weapons_and_gear"),list) else []
    if names: return [{"name":str(n),"type":"utility","description":"Common setting-appropriate gear.","quantity":1,"sell_value":5} for n in names[:6]]
    return [{"name":"Basic Supply Kit","type":"utility","description":"Ordinary supplies appropriate to this world.","quantity":1,"sell_value":5},
            {"name":"Basic Healing Supply","type":"consumable","description":"A modest healing item appropriate to this world.","quantity":2,"sell_value":4,"healing":"1d4"}]

def generate_merchant(game_master, store_hint):
    snap=game_master.state.snapshot(); world=snap.get("world_profile",{}); player=snap.get("player",{})
    level=max(1,_safe_int(player.get("level"),1)); hint=str(store_hint or "local general merchant"); location=str(player.get("location") or "unknown")
    data={}; client=getattr(game_master.provider,"client",None); model=getattr(game_master.provider,"model",None)
    if client is not None and model:
        instructions="""Return ONLY JSON for a merchant in this universal RPG. The merchant and every item must fit the confirmed world, location, technology, powers, culture, and requested store type. Return merchant_name, store_type, quality, description, stock. quality is ordinary, quality, elite, or special. stock has 6-10 BASE items. Python owns rarity. Each item includes name,type,description,quantity,sell_value and exact mechanics when relevant. Keep stock progression-appropriate."""
        try:
            out=client.responses.create(model=model,instructions=instructions,input=json.dumps({"world":world,"location":location,"player_level":level,"store_request":hint},ensure_ascii=False))
            parsed=json.loads(out.output_text.strip()); data=parsed if isinstance(parsed,dict) else {}
        except Exception: data={}
    quality=_normalize_shop_quality(data.get("quality","ordinary"),level,hint)
    raw=data.get("stock") if isinstance(data.get("stock"),list) else _fallback_stock(world)
    stock=[_stock_item(x,quality,level) for x in raw[:10] if isinstance(x,dict)] or [_stock_item(x,quality,level) for x in _fallback_stock(world)]
    merchant={"merchant_name":str(data.get("merchant_name") or "Local Merchant"),"store_type":str(data.get("store_type") or hint),"quality":quality,"description":str(data.get("description") or ""),"location":location,"stock":stock}
    game_master.state.data.setdefault("world_flags",{})["active_merchant"]=merchant; game_master.state.save(); return merchant

def active_merchant(game_master):
    m=game_master.state.data.get("world_flags",{}).get("active_merchant")
    return m if isinstance(m,dict) and isinstance(m.get("stock"),list) else None

def clear_active_merchant(game_master):
    game_master.state.data.setdefault("world_flags",{}).pop("active_merchant",None); game_master.state.save()

def _mechanics(item):
    k=str(item.get("type") or "misc").lower(); p=[]
    if k=="weapon":
        if item.get("damage"): p.append(f"Damage {item['damage']}")
        if item.get("range") is not None: p.append(f"Range {item['range']}")
        if item.get("attack_attribute"): p.append(str(item["attack_attribute"]).title())
    elif k=="shield": p.append(f"Shield HP {_safe_int(item.get('shield',item.get('max_shield_hp',0)))}")
    elif k=="armor":
        p.append(f"Armor HP {_safe_int(item.get('max_armor_hp',item.get('armor_hp',0)))}")
        if item.get("slot"): p.append(str(item["slot"]).title())
        if item.get("weight") is not None: p.append(f"Weight {_safe_int(item['weight'])}")
        b=item.get("stat_bonus") if isinstance(item.get("stat_bonus"),dict) else None
        if b: p.append(f"+{_safe_int(b.get('amount'))} {str(b.get('stat') or '').title()}")
    elif item.get("healing"): p.append(f"Healing {item['healing']}")
    if item.get("effect"): p.append(str(item["effect"]))
    return " | ".join(p) if p else "Utility / story item"

def _same(a,b):
    return isinstance(a,dict) and isinstance(b,dict) and str(a.get("name","")).lower()==str(b.get("name","")).lower() and str(a.get("type","")).lower()==str(b.get("type","")).lower()

def _equipped(player,item):
    if _same(player.get("equipped_weapon"),item) or _same(player.get("equipped_shield"),item): return True
    return any(_same(x,item) for x in (player.get("equipped_armor",{}) or {}).values() if isinstance(x,dict))

def _comparison(player,item):
    k=str(item.get("type") or "").lower(); cur=None
    if k=="weapon": cur=player.get("equipped_weapon")
    elif k=="shield": cur=player.get("equipped_shield")
    elif k=="armor": cur=(player.get("equipped_armor",{}) or {}).get(str(item.get("slot") or "").lower())
    return "Currently equipped: nothing comparable." if not isinstance(cur,dict) else f"Currently equipped: {cur.get('name','Item')} [{str(cur.get('rarity') or 'common').title()}] — {_mechanics(cur)}"

def _haggle_dc(percent):
    band=math.ceil(max(5,min(50,int(percent)))/5)
    if band==1: return 8
    if band>=10: return 25
    return 8+(band-1)*2

def haggle_item(game_master,index,percent):
    merchant=active_merchant(game_master)
    if not merchant: return "No merchant is currently open."
    stock=merchant["stock"]
    if not 1<=index<=len(stock): return f"Choose a shop item from 1-{len(stock)}."
    if not 5<=percent<=50: return "Choose a discount from 5% to 50%."
    item=stock[index-1]
    if item.get("haggle_attempted"):
        d=_safe_int(item.get("haggle_discount_percent"))
        return f"You already negotiated this item down by {d}%." if d else "You already tried to haggle over this item. The merchant is sticking to the price."
    stats=normalize_attributes(game_master.state.data.get("player",{}).get("stats",{}))
    charisma=_safe_int(stats.get("charisma")); bonus=attribute_check_bonus(charisma); dc=_haggle_dc(percent)
    check=resolve_check(reason=f"Haggle {percent}% off {item.get('name','item')}",dc=dc,modifier=bonus)
    original=max(1,_safe_int(item.get("original_buy_price",item.get("buy_price",1)),1))
    item.update({"original_buy_price":original,"haggle_attempted":True,"haggle_dc":dc,"haggle_roll":check})
    rolled=check["rolls"][0] if check.get("rolls") else check.get("base_total",0)
    header=f"🎲 HAGGLE — asking for {percent}% off\n" f"d20: {rolled} + {bonus} (Charisma {charisma}) = {check.get('total')} vs DC {dc}"
    if check.get("success"):
        new=max(1,math.ceil(original*(100-percent)/100)); item["buy_price"]=new; item["haggle_discount_percent"]=percent
        msg=f"{header}\nSUCCESS — {item.get('name')} drops from {format_money(original,ensure_wallet(game_master))} to {format_money(new,ensure_wallet(game_master))}."
    else:
        item["buy_price"]=original; item["haggle_discount_percent"]=0; msg=f"{header}\nFAILURE — the merchant keeps the original price."
    game_master.state.save(); return msg

def show_shop(game_master,merchant=None):
    merchant=merchant or active_merchant(game_master)
    if not merchant: print("\nNo merchant is currently open."); return
    wallet=ensure_wallet(game_master); world=game_master.state.data.get("world_profile",{})
    print("\n"+"="*56); print(f"🏪 {merchant.get('merchant_name','MERCHANT')} — {merchant.get('store_type','Shop')}"); print("="*56)
    if merchant.get("description"): print(merchant["description"])
    print(f"Shop quality: {str(merchant.get('quality','ordinary')).title()} | Your balance: {format_money(wallet.get('amount',0),wallet)}")
    if not merchant["stock"]: print("This merchant is out of stock."); return
    print("\nFOR SALE")
    for i,item in enumerate(merchant["stock"],1):
        q=max(1,_safe_int(item.get("quantity"),1)); suffix=f" x{q}" if q>1 else ""; d=_safe_int(item.get("haggle_discount_percent"))
        h=f" | Haggled {d}% off" if d else (" | Haggle failed" if item.get("haggle_attempted") else "")
        print(f"  {i}. {item.get('name','Item')}{suffix} [{str(item.get('rarity') or 'common').title()}] — {_mechanics(item)}")
        print(f"     Buy Price: {format_money(item.get('buy_price',1),world)} | Sell Value: {format_money(item.get('sell_value',0),world)}{h}")
    print("\nCommands: buy <number> | compare <number> | haggle <number> <percent> | sell | refresh | leave")
    print("Haggle roll = d20 + Charisma bonus. The more % you ask off, the higher the DC.")

def buy_item(game_master,index):
    m=active_merchant(game_master)
    if not m: return "No merchant is currently open."
    if not 1<=index<=len(m["stock"]): return f"Choose a shop item from 1-{len(m['stock'])}."
    item=m["stock"][index-1]; wallet=ensure_wallet(game_master); price=max(1,_safe_int(item.get("buy_price"),1)); balance=_safe_int(wallet.get("amount"))
    if balance<price: return f"You need {format_money(price,wallet)}, but you only have {format_money(balance,wallet)}."
    purchased=deepcopy(item)
    for k in ("buy_price","original_buy_price","haggle_attempted","haggle_discount_percent","haggle_dc","haggle_roll"): purchased.pop(k,None)
    purchased["quantity"]=1; wallet["amount"]=balance-price
    game_master.state._add_inventory_item(game_master.state.data.setdefault("player",{}),purchased)
    q=max(1,_safe_int(item.get("quantity"),1))
    if q<=1: del m["stock"][index-1]
    else:
        item["quantity"]=q-1; item["buy_price"]=max(1,_safe_int(item.get("original_buy_price",item.get("buy_price",1)),1)); item["original_buy_price"]=item["buy_price"]; item["haggle_attempted"]=False; item["haggle_discount_percent"]=0; item.pop("haggle_dc",None); item.pop("haggle_roll",None)
    game_master.state.save(); return f"Bought {purchased.get('name')} for {format_money(price,wallet)}. Balance: {format_money(wallet.get('amount'),wallet)}."

def sell_item(game_master,index):
    player=game_master.state.data.setdefault("player",{})
    from .inventory import ensure_inventory_sell_values
    ensure_inventory_sell_values(player); inv=player.get("inventory",[])
    if not 1<=index<=len(inv): return f"Choose an inventory item from 1-{len(inv)}."
    item=inv[index-1]
    if not isinstance(item,dict): return "That inventory entry cannot be sold."
    if _equipped(player,item): return "Unequip that item before selling it."
    value=max(0,_safe_int(item.get("sell_value")))
    if value<=0: return f"{item.get('name','That item')} is unsellable."
    name=str(item.get("name") or "Item"); q=max(1,_safe_int(item.get("quantity"),1)); sold=deepcopy(item); sold["quantity"]=1
    if q==1: del inv[index-1]
    else: item["quantity"]=q-1
    wallet=ensure_wallet(game_master); wallet["amount"]=_safe_int(wallet.get("amount"))+value
    m=active_merchant(game_master)
    if m:
        sold["buy_price"]=max(1,math.ceil(value*2)); sold["original_buy_price"]=sold["buy_price"]; sold["haggle_attempted"]=False; sold["haggle_discount_percent"]=0; m["stock"].append(sold)
    game_master.state.save(); return f"Sold {name} for {format_money(value,wallet)}. Balance: {format_money(wallet.get('amount'),wallet)}."

def _show_sell_inventory(game_master):
    player=game_master.state.data.get("player",{})
    from .inventory import ensure_inventory_sell_values
    ensure_inventory_sell_values(player); inv=player.get("inventory",[]); world=game_master.state.data.get("world_profile",{})
    print("\nSELL ITEMS")
    if not inv: print("Your inventory is empty."); return
    for i,item in enumerate(inv,1):
        if not isinstance(item,dict): continue
        v=max(0,_safe_int(item.get("sell_value"))); text="Unsellable" if v<=0 else format_money(v,world); eq=" [EQUIPPED — CANNOT SELL]" if _equipped(player,item) else ""
        print(f"  {i}. {item.get('name','Item')} [{str(item.get('rarity') or 'common').title()}] — {text}{eq}")

def run_shop_screen(game_master):
    if isinstance(game_master.state.data.get("combat"),dict) and game_master.state.data["combat"].get("active"): print("\nYou cannot shop during active combat."); return
    ensure_wallet(game_master,grant_starting_funds=True); merchant=active_merchant(game_master)
    if not merchant:
        hint=input("\nWhat kind of merchant/store are you visiting? (or 'back'): ").strip()
        if hint.lower() in {"back","b","cancel","exit"}: return
        merchant=generate_merchant(game_master,hint or "local general merchant")
    while True:
        show_shop(game_master,merchant); raw=input("\nShop> ").strip(); low=raw.lower()
        if low in {"leave","back","b","exit","close"}: clear_active_merchant(game_master); print("You leave the shop."); return
        if low in {"refresh","show","shop","stock"}: merchant=active_merchant(game_master) or merchant; continue
        if low=="sell":
            _show_sell_inventory(game_master); c=input("Sell which inventory number? (or 'back'): ").strip().lower()
            if c in {"back","b","cancel"}: continue
            try: print(sell_item(game_master,int(c)))
            except ValueError: print("Enter an inventory number.")
            continue
        if low.startswith("buy "):
            try: print(buy_item(game_master,int(low.split(maxsplit=1)[1])))
            except ValueError: print("Use: buy <number>")
            continue
        if low.startswith("compare "):
            try: i=int(low.split(maxsplit=1)[1])
            except ValueError: print("Use: compare <number>"); continue
            if not 1<=i<=len(merchant["stock"]): print(f"Choose a shop item from 1-{len(merchant['stock'])}."); continue
            item=merchant["stock"][i-1]; print(f"\n{item.get('name')} [{str(item.get('rarity') or 'common').title()}] — {_mechanics(item)}"); print(_comparison(game_master.state.data.get("player",{}),item)); continue
        if low.startswith("haggle "):
            parts=low.split()
            if len(parts)!=3: print("Use: haggle <item number> <percent>. Example: haggle 3 20"); continue
            try: print(haggle_item(game_master,int(parts[1]),int(parts[2].rstrip("%"))))
            except ValueError: print("Use: haggle <item number> <percent>. Example: haggle 3 20")
            continue
        print("Use: buy <number>, compare <number>, haggle <number> <percent>, sell, refresh, or leave.")