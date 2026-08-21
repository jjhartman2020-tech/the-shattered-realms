"""AI-first Game Master runtime for The Shattered Realms."""

from copy import deepcopy
from typing import Dict, List

from .context import ContextBuilder
from .memory import CampaignMemory
from .provider import provider_from_environment
from .rules import RuleLibrary
from backend.game.abilities import resolve_ability
from backend.game.attributes import SKILL_ATTRIBUTE, attribute_check_bonus, build_combatant, normalize_attributes
from backend.game.checks import resolve_check
from backend.game.combat import current_actor, defend_actor, end_turn, move_actor, resolve_attack, start_combat
from backend.game.resources import resource_key, resource_name_for_class
from backend.game.state import GameState
from backend.game.world import WorldSimulator

SKILL_ALIASES = {
    "acrobatics": "acrobatics", "animal handling": "animal_handling", "arcana": "arcana",
    "athletics": "athletics", "strength": "athletics", "stealth": "stealth", "sneak": "stealth",
    "sleight of hand": "sleight_of_hand", "sleight_of_hand": "sleight_of_hand", "pickpocket": "sleight_of_hand",
    "perception": "perception", "investigation": "investigation", "survival": "survival",
    "persuasion": "persuasion", "persuade": "persuasion", "deception": "deception", "deceive": "deception",
    "intimidation": "intimidation", "intimidate": "intimidation", "insight": "insight", "medicine": "medicine",
    "nature": "nature", "performance": "performance", "religion": "religion", "history": "history",
}
ATTRIBUTE_ALIASES = {k: k for k in ("health", "mana", "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma", "speed", "defense")}
ATTRIBUTE_ALIASES.update({"agility": "dexterity", "durability": "constitution"})
ATTRIBUTE_REASON_HINTS = {
    "strength": ("force", "lift", "break", "shove", "grapple", "overpower", "push", "pull"),
    "dexterity": ("dodge", "balance", "jump", "reflex", "aim", "precise", "finesse"),
    "constitution": ("endure", "resist poison", "hold breath", "tough", "fatigue", "pain"),
    "intelligence": ("recall", "decode", "analyze", "research", "arcane", "solve"),
    "wisdom": ("notice", "sense", "track", "intuition", "heal", "survive"),
    "charisma": ("convince", "persuade", "deceive", "intimidate", "perform", "negotiate"),
    "speed": ("sprint", "race", "outrun", "react quickly", "catch up"),
    "defense": ("defend", "guard", "brace", "block", "protect"),
}


def _skill_for_check(request: Dict, reason: str) -> str | None:
    requested = str(request.get("skill") or "").strip().lower().replace("-", " ")
    if requested in SKILL_ALIASES:
        return SKILL_ALIASES[requested]
    text = reason.lower()
    for phrase, skill in SKILL_ALIASES.items():
        if phrase.replace("_", " ") in text:
            return skill
    return None


def _attribute_for_check(request: Dict, reason: str, skill: str | None) -> str | None:
    requested = str(request.get("attribute") or "").strip().lower().replace("-", " ")
    if requested in ATTRIBUTE_ALIASES:
        return ATTRIBUTE_ALIASES[requested]
    if skill and skill in SKILL_ATTRIBUTE:
        return SKILL_ATTRIBUTE[skill]
    text = reason.lower()
    for attribute, hints in ATTRIBUTE_REASON_HINTS.items():
        if any(hint in text for hint in hints):
            return attribute
    return None


class GameMaster:
    def __init__(self, provider=None, state: GameState | None = None, memory: CampaignMemory | None = None, rules: RuleLibrary | None = None) -> None:
        self.provider = provider or provider_from_environment()
        self.state = state or GameState()
        self.memory = memory or CampaignMemory()
        self.rules = rules or RuleLibrary()
        self.context_builder = ContextBuilder()
        self.world = WorldSimulator()
        self.ready = True

    def handle_action(self, player_action: str) -> Dict:
        action = player_action.strip()
        if not action:
            return {"narration": "Tell the Game Master what you want to do.", "state": self.state.snapshot()}

        snapshot = self.state.snapshot()
        context = self.context_builder.build(player_action=action, game_state=snapshot, memories=self.memory.context_for(action), rules=self.rules.retrieve(action))
        active_combat = snapshot.get("combat")
        if isinstance(active_combat, dict) and active_combat.get("active"):
            context["active_combat"] = active_combat
            actor = current_actor(active_combat)
            context["current_combat_actor"] = actor.get("name") if actor else None

        result = self.provider.respond(context)
        mechanical_result = None
        combat_results: List[Dict] = []
        combat_request = result.get("combat_request")

        if isinstance(combat_request, dict):
            request_type = str(combat_request.get("type") or "").lower()
            if request_type == "start" and not (isinstance(active_combat, dict) and active_combat.get("active")):
                active_combat = self._start_combat(combat_request)
                combat_results.append({"type": "combat_start", "order": active_combat.get("order", []), "initiative": active_combat.get("initiative", [])})
                combat_results.extend(self._run_enemy_turns(active_combat))
                self._persist_combat(active_combat)

            elif request_type in {"attack", "move", "move_attack", "ability", "defend", "end_turn", "pass"} and isinstance(active_combat, dict) and active_combat.get("active"):
                actor = current_actor(active_combat)
                player_name = str(snapshot.get("player", {}).get("name") or "Traveler")
                if not actor or actor.get("name") != player_name:
                    combat_results.append({"type": "invalid", "reason": "It is not the player's turn."})
                else:
                    before_action = deepcopy(active_combat)
                    try:
                        if request_type in {"move", "move_attack"}:
                            movement = move_actor(active_combat, player_name, int(combat_request.get("x")), int(combat_request.get("y")), enforce_turn=True)
                            combat_results.append({"type": "player_move", **movement})
                        if request_type in {"attack", "move_attack"}:
                            target = str(combat_request.get("target") or "").strip()
                            attack_attribute = str(combat_request.get("attack_attribute") or "strength").lower()
                            if attack_attribute not in {"strength", "dexterity"}:
                                attack_attribute = "strength"
                            attack_result = resolve_attack(active_combat, player_name, target, attack_attribute=attack_attribute, enforce_turn=True)
                            combat_results.append({"type": "player_attack", **attack_result})
                        elif request_type == "ability":
                            ability_name = str(combat_request.get("ability") or "").strip()
                            target = str(combat_request.get("target") or "").strip() or None
                            ability_result = resolve_ability(active_combat, player_name, ability_name, target, enforce_turn=True)
                            combat_results.append({"type": "player_ability", **ability_result})
                        elif request_type == "defend":
                            defense = defend_actor(active_combat, player_name, enforce_turn=True)
                            combat_results.append({"type": "player_defend", **defense})
                        elif request_type in {"end_turn", "pass"}:
                            combat_results.append({"type": "player_end_turn", "actor": player_name})
                            end_turn(active_combat)
                            combat_results.extend(self._run_enemy_turns(active_combat))
                    except (TypeError, ValueError) as exc:
                        active_combat.clear()
                        active_combat.update(before_action)
                        combat_results = [{"type": "invalid", "reason": str(exc)}]
                    self._persist_combat(active_combat)

        if combat_results:
            resolved_context = dict(context)
            resolved_context["active_combat"] = active_combat
            resolved_context["combat_result"] = combat_results
            resolved_context["mechanical_instruction"] = (
                "Python has resolved combat. Narrate movement, remaining movement, primary-action use, abilities, class-resource costs, defending, initiative, attacks, range, damage, HP, critical results, defeats, and turn progression exactly. "
                "Positions, resources, action availability, defense state, and distances in active_combat are authoritative. Do not reroll, move characters again, alter positions, resources, or alter the results."
            )
            narrated = self.provider.respond(resolved_context)
            narrated["combat_request"] = None
            narrated["combat"] = active_combat
            narrated["combat_results"] = combat_results
            result = narrated

        elif result.get("requires_roll"):
            request = result.get("roll") or {}
            if not isinstance(request, dict):
                request = {}
            reason = str(request.get("reason") or action).strip()
            difficulty = str(request.get("difficulty") or "standard").strip().lower()
            if difficulty not in {"trivial", "easy", "standard", "hard", "very_hard", "extreme"}:
                difficulty = "standard"
            skill = _skill_for_check(request, reason)
            player = self.state.snapshot().get("player", {})
            skills = player.get("skills", {}) if isinstance(player, dict) else {}
            raw_stats = player.get("stats") or player.get("attributes") or {} if isinstance(player, dict) else {}
            attributes = normalize_attributes(raw_stats)
            skill_bonus = int(skills.get(skill, 0)) if skill else 0
            attribute = _attribute_for_check(request, reason, skill)
            attribute_value = int(attributes.get(attribute, 0)) if attribute else 0
            attribute_bonus = int(attribute_check_bonus(attribute_value)) if attribute else 0
            modifier = skill_bonus + attribute_bonus
            mechanical_result = resolve_check(reason=reason, difficulty=difficulty, modifier=modifier)
            mechanical_result.update({"skill": skill, "attribute": attribute, "attribute_value": attribute_value, "skill_bonus": skill_bonus, "attribute_bonus": attribute_bonus})
            resolved_context = dict(context)
            resolved_context["mechanical_result"] = mechanical_result
            resolved_context["mechanical_instruction"] = "The rules engine resolved this check using canonical 0-30 attributes. Obey it exactly and do not reroll."
            result = self.provider.respond(resolved_context)
            result["requires_roll"] = False
            result["roll"] = mechanical_result

        self.state.apply_changes(result.get("state_changes", []))
        for memory in result.get("memories", []):
            self._store_memory(memory, "event")
        for note in result.get("world_notes", []):
            self._store_memory(note, "world")
        narration = str(result.get("narration", "")).strip()
        if narration:
            turn_record = f"Player action: {action}\nGame Master result: {narration}"
            if mechanical_result:
                turn_record += f"\nMechanical check: {mechanical_result}"
            if combat_results:
                turn_record += f"\nCombat results: {combat_results}"
            self.memory.remember(turn_record, category="turn", importance=1, confirmed=True)
        result["state"] = self.state.snapshot()
        result["memory_count"] = len(self.memory.all())
        return result

    def _fresh_template_actor(self, raw_actor: Dict) -> Dict:
        actor = deepcopy(raw_actor)
        max_hp = max(0, int(actor.get("max_hp", actor.get("hp", 0)) or 0))
        max_resource = max(0, int(actor.get("max_resource", actor.get("max_mana", 0)) or 0))
        actor["hp"] = max_hp
        actor["max_hp"] = max_hp
        actor["resource"] = max_resource
        actor["max_resource"] = max_resource
        actor["mana"] = max_resource
        actor["max_mana"] = max_resource
        actor["movement_used"] = 0
        actor["primary_action_used"] = False
        actor["defending"] = False
        actor["active_defense_ac_bonus"] = 0
        actor.pop("ability_cooldowns", None)
        actor["defeated"] = False
        return actor

    def _build_enemy_from_spec(self, raw_enemy: Dict) -> Dict:
        resource_name = str(raw_enemy.get("resource_name") or resource_name_for_class(raw_enemy.get("class")))
        overrides = {
            "armor_class": int(raw_enemy.get("armor_class", 10)),
            "damage": str(raw_enemy.get("damage", "1d4")),
            "attack_attribute": str(raw_enemy.get("attack_attribute", "strength")),
            "role": str(raw_enemy.get("role", "fighter")),
            "attack_bonus": int(raw_enemy.get("attack_bonus", 0)),
            "class": str(raw_enemy.get("class") or "unassigned"),
            "resource_name": resource_name,
            "resource_type": resource_key(resource_name),
        }
        if raw_enemy.get("position") is not None:
            overrides["position"] = raw_enemy.get("position")
        if raw_enemy.get("attack_range") is not None:
            overrides["attack_range"] = int(raw_enemy.get("attack_range"))
        if isinstance(raw_enemy.get("abilities"), list):
            overrides["abilities"] = deepcopy(raw_enemy.get("abilities"))
        enemy_hp = int(raw_enemy.get("hp", 0)) if int(raw_enemy.get("hp", 0)) > 0 else None
        if enemy_hp is not None:
            overrides["max_hp"] = enemy_hp
        actor = build_combatant(
            str(raw_enemy.get("name") or "Enemy"),
            "enemy",
            normalize_attributes(raw_enemy.get("attributes") or {}),
            level=int(raw_enemy.get("level", 1)),
            hp=enemy_hp,
            overrides=overrides,
        )
        if raw_enemy.get("resource") is not None:
            actor["resource"] = max(0, min(int(actor.get("max_resource", 0)), int(raw_enemy.get("resource"))))
            actor["mana"] = actor["resource"]
        return actor

    def _start_combat(self, request: Dict) -> Dict:
        snapshot = self.state.snapshot()
        player = snapshot.get("player", {})
        player_name = str(player.get("name") or "Traveler")
        attributes = normalize_attributes(player.get("stats") or player.get("attributes") or {})
        resource_name = str(player.get("resource_name") or resource_name_for_class(player.get("class")))
        player_actor = build_combatant(player_name, "player", attributes, level=int(player.get("level", 1)), hp=int(player.get("hp", 0)) if int(player.get("hp", 0)) > 0 else None, overrides={
            "armor_class": int(player.get("armor_class", 10)),
            "damage": str(player.get("damage", "1d6")),
            "attack_bonus": int(player.get("attack_bonus", 0)),
            "position": player.get("combat_position", {"x": 0, "y": 0}),
            "abilities": deepcopy(player.get("equipped_abilities", [])) if isinstance(player.get("equipped_abilities"), list) else [],
            "class": str(player.get("class") or "unassigned"),
            "resource_name": resource_name,
            "resource_type": str(player.get("resource_type") or resource_key(resource_name)),
            "resource": int(player.get("resource", player.get("mana", 0)) or 0),
            "max_resource": int(player.get("max_resource", player.get("max_mana", 0)) or 0),
        })
        player_actor["mana"] = int(player_actor.get("resource", 0))
        player_actor["max_mana"] = int(player_actor.get("max_resource", 0))
        combatants = [player_actor]

        reset_pending = bool(snapshot.get("encounter_reset_pending"))
        template = snapshot.get("encounter_template") if isinstance(snapshot.get("encounter_template"), dict) else {}
        template_enemies = [
            self._fresh_template_actor(actor)
            for actor in template.get("combatants", [])
            if isinstance(actor, dict) and actor.get("team") == "enemy"
        ]
        pending_specs = [
            enemy for enemy in snapshot.get("pending_encounter_enemies", [])
            if isinstance(enemy, dict)
        ] if isinstance(snapshot.get("pending_encounter_enemies"), list) else []
        request_specs = [enemy for enemy in request.get("enemies", []) if isinstance(enemy, dict)]

        if reset_pending and pending_specs:
            combatants.extend(self._build_enemy_from_spec(enemy) for enemy in pending_specs)
        elif reset_pending and template_enemies:
            combatants.extend(template_enemies)
        else:
            combatants.extend(self._build_enemy_from_spec(enemy) for enemy in request_specs)

        if len(combatants) == 1:
            raise ValueError("Combat start requires at least one enemy")

        combat = start_combat(combatants)
        pristine = deepcopy(combat)
        for actor in pristine.get("combatants", []):
            actor["hp"] = int(actor.get("max_hp", actor.get("hp", 0)))
            max_resource = int(actor.get("max_resource", actor.get("max_mana", 0)) or 0)
            actor["resource"] = max_resource
            actor["max_resource"] = max_resource
            actor["mana"] = max_resource
            actor["max_mana"] = max_resource
            actor["movement_used"] = 0
            actor["primary_action_used"] = False
            actor["defending"] = False
            actor["active_defense_ac_bonus"] = 0
            actor.pop("ability_cooldowns", None)
            actor["defeated"] = False
        self.state.set_path("encounter_template", {"combatants": pristine.get("combatants", []), "grid": pristine.get("grid", {})}, save=False)
        self.state.set_path("encounter_reset_pending", False, save=False)
        self.state.set_path("pending_encounter_enemies", [], save=False)
        self.state.save()
        return combat

    def _run_enemy_turns(self, combat: Dict) -> List[Dict]:
        results: List[Dict] = []
        safety = 0
        while combat.get("active") and safety < 20:
            safety += 1
            actor = current_actor(combat)
            if not actor or actor.get("team") != "enemy":
                break
            snapshot = self.state.snapshot()
            player_name = str(snapshot.get("player", {}).get("name") or "Traveler")
            enemy_context = self.context_builder.build(player_action=f"Enemy turn: {actor.get('name')}", game_state=snapshot, memories=self.memory.context_for(str(actor.get("name"))), rules=self.rules.retrieve("enemy combat tactics target selection positioning movement defend abilities resources"))
            enemy_context["active_combat"] = combat
            enemy_context["enemy_turn"] = {"actor": actor, "instruction": "Choose a legal tactical action using only information this enemy could know."}
            decision = self.provider.respond(enemy_context)
            request = decision.get("combat_request") or {}
            request_type = str(request.get("type") or "").lower() if isinstance(request, dict) else ""
            before_action = deepcopy(combat)
            try:
                if request_type in {"move", "move_attack"}:
                    movement = move_actor(combat, str(actor.get("name")), int(request.get("x")), int(request.get("y")), enforce_turn=True)
                    results.append({"type": "enemy_move", **movement})
                if request_type in {"attack", "move_attack"}:
                    target = str(request.get("target") or player_name)
                    attack_attribute = str(request.get("attack_attribute") or actor.get("attack_attribute", "strength")).lower()
                    if attack_attribute not in {"strength", "dexterity"}:
                        attack_attribute = "strength"
                    attack = resolve_attack(combat, str(actor.get("name")), target, attack_attribute=attack_attribute, enforce_turn=True)
                    results.append({"type": "enemy_attack", **attack})
                elif request_type == "ability":
                    ability_name = str(request.get("ability") or "").strip()
                    target = str(request.get("target") or player_name).strip() or None
                    ability_result = resolve_ability(combat, str(actor.get("name")), ability_name, target, enforce_turn=True)
                    results.append({"type": "enemy_ability", **ability_result})
                elif request_type == "defend":
                    defense = defend_actor(combat, str(actor.get("name")), enforce_turn=True)
                    results.append({"type": "enemy_defend", **defense})
                elif request_type not in {"move"}:
                    results.append({"type": "enemy_pass", "actor": actor.get("name")})
            except (TypeError, ValueError) as exc:
                combat.clear()
                combat.update(before_action)
                results.append({"type": "enemy_invalid", "actor": actor.get("name"), "reason": str(exc)})
            if combat.get("active"):
                end_turn(combat)
        return results

    def _persist_combat(self, combat: Dict) -> None:
        self.state.set_path("combat", combat, save=False)
        player_name = str(self.state.snapshot().get("player", {}).get("name") or "Traveler")
        for actor in combat.get("combatants", []):
            if actor.get("name") == player_name:
                self.state.set_path("player.hp", int(actor.get("hp", 0)), save=False)
                self.state.set_path("player.max_hp", int(actor.get("max_hp", 0)), save=False)
                resource = int(actor.get("resource", actor.get("mana", 0)) or 0)
                max_resource = int(actor.get("max_resource", actor.get("max_mana", 0)) or 0)
                self.state.set_path("player.resource_name", str(actor.get("resource_name") or "Mana"), save=False)
                self.state.set_path("player.resource_type", str(actor.get("resource_type") or "mana"), save=False)
                self.state.set_path("player.resource", resource, save=False)
                self.state.set_path("player.max_resource", max_resource, save=False)
                self.state.set_path("player.mana", resource, save=False)
                self.state.set_path("player.max_mana", max_resource, save=False)
                self.state.set_path("player.combat_position", actor.get("position", {"x": 0, "y": 0}), save=False)
                break
        self.state.save()

    def _store_memory(self, memory, default_category: str) -> None:
        if isinstance(memory, str):
            self.memory.remember(memory, category=default_category, importance=2)
        elif isinstance(memory, dict):
            self.memory.remember(memory.get("text", ""), category=memory.get("category", default_category), importance=memory.get("importance", 2), confirmed=memory.get("confirmed", True))

    def advance_world(self, elapsed_days: int) -> Dict:
        events = self.world.advance(self.state.snapshot(), elapsed_days)
        self.state.apply_changes([event["state_change"] for event in events if "state_change" in event])
        for event in events:
            if event.get("summary"):
                self.memory.remember(event["summary"], category="world", importance=2)
        return {"events": events, "state": self.state.snapshot()}
