extends Control

const API_BASE := "http://127.0.0.1:8765"
const EXPLORE_COLS := 20
const EXPLORE_ROWS := 14
const BATTLE_COLS := 12
const BATTLE_ROWS := 8

const INK := Color("#e8f4d4")
const MUTED := Color("#a9bc9a")
const OUTLINE := Color("#17251f")
const PANEL := Color("#263b32")
const GRASS_A := Color("#6b8f4e")
const GRASS_B := Color("#789d58")
const PATH := Color("#b7a36a")
const WATER := Color("#467887")
const TREE := Color("#315b3a")
const BUILDING := Color("#74584a")
const PLAYER_COLOR := Color("#e8d66d")
const ALLY_COLOR := Color("#74c7a5")
const ENEMY_COLOR := Color("#d66b61")
const MOVE_COLOR := Color(0.35, 0.78, 0.72, 0.32)

var main_controller: Control
var http: HTTPRequest
var game_state: Dictionary = {}
var mode: String = "explore"
var request_mode: String = ""
var busy: bool = false

var player_tile := Vector2i(4, 9)
var facing := Vector2i(0, -1)
var npc_tile := Vector2i(10, 8)
var blocked: Dictionary = {}

var title_label: Label
var subtitle_label: Label
var message_panel: PanelContainer
var message_label: RichTextLabel
var explore_panel: PanelContainer
var explore_actions: VBoxContainer
var battle_panel: PanelContainer
var battle_actions: VBoxContainer
var status_label: Label
var ability_box: VBoxContainer
var action_mode: String = ""
var chosen_ability: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_build_interface()
	_build_collision()
	http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_request_completed)
	set_process_unhandled_input(true)
	visible = false


func bind_main(value: Control) -> void:
	main_controller = value


func show_from_payload(payload: Dictionary = {}) -> void:
	if payload.get("state") is Dictionary:
		game_state = payload.get("state", {})
	elif not payload.is_empty() and payload.get("player") is Dictionary:
		game_state = payload
	var combat: Dictionary = _combat()
	mode = "battle" if bool(combat.get("active", false)) else "explore"
	visible = true
	_update_header()
	_refresh_mode_interface()
	var narration: String = str(payload.get("narration", ""))
	if narration.is_empty():
		narration = "Use WASD or the arrow keys to explore. Press E or Space to interact."
	_set_message(narration)
	queue_redraw()


func hide_view() -> void:
	visible = false


func _build_interface() -> void:
	title_label = Label.new()
	title_label.position = Vector2(28, 18)
	title_label.add_theme_font_size_override("font_size", 28)
	title_label.add_theme_color_override("font_color", INK)
	add_child(title_label)

	subtitle_label = Label.new()
	subtitle_label.position = Vector2(30, 55)
	subtitle_label.add_theme_font_size_override("font_size", 14)
	subtitle_label.add_theme_color_override("font_color", MUTED)
	add_child(subtitle_label)

	message_panel = PanelContainer.new()
	message_panel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	message_panel.position = Vector2(28, -154)
	message_panel.size = Vector2(790, 126)
	message_panel.add_theme_stylebox_override("panel", _panel_style(Color("#1b2b25"), INK, 3))
	add_child(message_panel)
	var message_margin := MarginContainer.new()
	message_margin.add_theme_constant_override("margin_left", 16)
	message_margin.add_theme_constant_override("margin_top", 12)
	message_margin.add_theme_constant_override("margin_right", 16)
	message_margin.add_theme_constant_override("margin_bottom", 12)
	message_panel.add_child(message_margin)
	message_label = RichTextLabel.new()
	message_label.bbcode_enabled = true
	message_label.fit_content = false
	message_label.scroll_active = true
	message_label.add_theme_font_size_override("normal_font_size", 16)
	message_label.add_theme_color_override("default_color", INK)
	message_margin.add_child(message_label)

	explore_panel = PanelContainer.new()
	explore_panel.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	explore_panel.offset_left = -420.0
	explore_panel.offset_top = 90.0
	explore_panel.offset_right = -30.0
	explore_panel.offset_bottom = -118.0
	explore_panel.add_theme_stylebox_override("panel", _panel_style(PANEL, OUTLINE, 3))
	add_child(explore_panel)
	var explore_margin := MarginContainer.new()
	explore_margin.add_theme_constant_override("margin_left", 16)
	explore_margin.add_theme_constant_override("margin_top", 16)
	explore_margin.add_theme_constant_override("margin_right", 16)
	explore_margin.add_theme_constant_override("margin_bottom", 16)
	explore_panel.add_child(explore_margin)
	explore_actions = VBoxContainer.new()
	explore_actions.add_theme_constant_override("separation", 10)
	explore_margin.add_child(explore_actions)
	var explore_heading := Label.new()
	explore_heading.text = "FIELD COMMANDS"
	explore_heading.add_theme_font_size_override("font_size", 20)
	explore_heading.add_theme_color_override("font_color", INK)
	explore_actions.add_child(explore_heading)
	var explore_help := Label.new()
	explore_help.text = "Move: WASD / Arrow keys\nInteract: E / Space\nMenu: M"
	explore_help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	explore_help.add_theme_color_override("font_color", MUTED)
	explore_actions.add_child(explore_help)
	explore_actions.add_child(_action_button("INTERACT", _interact))
	explore_actions.add_child(_action_button("ASK ABOUT THIS PLACE", _ask_about_place))
	explore_actions.add_child(_action_button("ASK FOR WORK", _ask_for_work))
	explore_actions.add_child(_action_button("TRAINING BATTLE", _start_training_battle))
	var discovery_note := Label.new()
	discovery_note.text = "The AI reveals the world as you explore. Hidden places and events stay hidden until you discover them."
	discovery_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	discovery_note.add_theme_color_override("font_color", MUTED)
	explore_actions.add_child(discovery_note)

	battle_panel = PanelContainer.new()
	battle_panel.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	battle_panel.offset_left = -420.0
	battle_panel.offset_top = 90.0
	battle_panel.offset_right = -30.0
	battle_panel.offset_bottom = -118.0
	battle_panel.add_theme_stylebox_override("panel", _panel_style(PANEL, OUTLINE, 3))
	add_child(battle_panel)
	var battle_margin := MarginContainer.new()
	battle_margin.add_theme_constant_override("margin_left", 16)
	battle_margin.add_theme_constant_override("margin_top", 16)
	battle_margin.add_theme_constant_override("margin_right", 16)
	battle_margin.add_theme_constant_override("margin_bottom", 16)
	battle_panel.add_child(battle_margin)
	battle_actions = VBoxContainer.new()
	battle_actions.add_theme_constant_override("separation", 8)
	battle_margin.add_child(battle_actions)
	var battle_heading := Label.new()
	battle_heading.text = "TACTICAL COMMANDS"
	battle_heading.add_theme_font_size_override("font_size", 20)
	battle_heading.add_theme_color_override("font_color", INK)
	battle_actions.add_child(battle_heading)
	status_label = Label.new()
	status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	status_label.add_theme_color_override("font_color", MUTED)
	battle_actions.add_child(status_label)
	battle_actions.add_child(_action_button("MOVE", _select_move))
	battle_actions.add_child(_action_button("BASIC ATTACK", _select_attack))
	battle_actions.add_child(_action_button("DEFEND", _defend))
	battle_actions.add_child(_action_button("END TURN", _end_turn))
	var ability_heading := Label.new()
	ability_heading.text = "ABILITIES"
	ability_heading.add_theme_color_override("font_color", INK)
	battle_actions.add_child(ability_heading)
	ability_box = VBoxContainer.new()
	ability_box.add_theme_constant_override("separation", 6)
	battle_actions.add_child(ability_box)


func _panel_style(color: Color, border_color: Color, width: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = border_color
	style.set_border_width_all(width)
	style.corner_radius_top_left = 3
	style.corner_radius_top_right = 3
	style.corner_radius_bottom_left = 3
	style.corner_radius_bottom_right = 3
	return style


func _action_button(label_text: String, callback: Callable) -> Button:
	var button := Button.new()
	button.text = label_text
	button.focus_mode = Control.FOCUS_NONE
	button.custom_minimum_size = Vector2(0, 42)
	button.add_theme_font_size_override("font_size", 15)
	button.add_theme_color_override("font_color", INK)
	button.add_theme_stylebox_override("normal", _panel_style(Color("#30493d"), Color("#54705d"), 2))
	button.add_theme_stylebox_override("hover", _panel_style(Color("#3c5a49"), INK, 2))
	button.pressed.connect(callback)
	return button


func _build_collision() -> void:
	blocked.clear()
	for x in range(EXPLORE_COLS):
		blocked[Vector2i(x, 0)] = true
		blocked[Vector2i(x, EXPLORE_ROWS - 1)] = true
	for y in range(EXPLORE_ROWS):
		blocked[Vector2i(0, y)] = true
		blocked[Vector2i(EXPLORE_COLS - 1, y)] = true
	for x in range(2, 9):
		blocked[Vector2i(x, 2)] = true
	for tree in [Vector2i(2, 5), Vector2i(3, 5), Vector2i(7, 5), Vector2i(12, 3), Vector2i(12, 4), Vector2i(5, 11), Vector2i(6, 11), Vector2i(12, 11)]:
		blocked[tree] = true
	for y in range(2, 6):
		for x in range(14, 19):
			blocked[Vector2i(x, y)] = true
	blocked.erase(Vector2i(16, 5))


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color("#101915"))
	if mode == "battle":
		_draw_battle()
	else:
		_draw_exploration()


func _grid_origin() -> Vector2:
	return Vector2(28, 92)


func _explore_tile_size() -> float:
	return floor(minf((size.x - 450.0) / float(EXPLORE_COLS), (size.y - 270.0) / float(EXPLORE_ROWS)))


func _battle_tile_size() -> float:
	return floor(minf((size.x - 450.0) / float(BATTLE_COLS), (size.y - 270.0) / float(BATTLE_ROWS)))


func _draw_exploration() -> void:
	var origin: Vector2 = _grid_origin()
	var tile_size: float = _explore_tile_size()
	for y in range(EXPLORE_ROWS):
		for x in range(EXPLORE_COLS):
			var tile := Vector2i(x, y)
			var color: Color = GRASS_A if (x + y) % 2 == 0 else GRASS_B
			if y >= 7 and y <= 9:
				color = PATH
			if x >= 2 and x <= 8 and y == 2:
				color = WATER
			if x >= 14 and x <= 18 and y >= 2 and y <= 5:
				color = BUILDING
			if _is_tree(tile):
				color = TREE
			var rect := Rect2(origin + Vector2(x, y) * tile_size, Vector2(tile_size, tile_size))
			draw_rect(rect, color)
			draw_rect(rect, Color(0.06, 0.1, 0.08, 0.28), false, 1.0)
			if _is_tree(tile):
				draw_circle(rect.get_center(), tile_size * 0.28, Color("#24482f"))
	var door_rect := _tile_rect(Vector2i(16, 5), origin, tile_size)
	draw_rect(door_rect.grow(-tile_size * 0.18), Color("#d2b778"))
	_draw_field_actor(npc_tile, ENEMY_COLOR, "!", origin, tile_size)
	_draw_field_actor(player_tile, PLAYER_COLOR, "", origin, tile_size)
	var player_rect := _tile_rect(player_tile, origin, tile_size)
	var face_point: Vector2 = player_rect.get_center() + Vector2(facing) * tile_size * 0.28
	draw_circle(face_point, maxf(2.0, tile_size * 0.07), OUTLINE)


func _is_tree(tile: Vector2i) -> bool:
	return tile in [Vector2i(2, 5), Vector2i(3, 5), Vector2i(7, 5), Vector2i(12, 3), Vector2i(12, 4), Vector2i(5, 11), Vector2i(6, 11), Vector2i(12, 11)]


func _tile_rect(tile: Vector2i, origin: Vector2, tile_size: float) -> Rect2:
	return Rect2(origin + Vector2(tile) * tile_size, Vector2(tile_size, tile_size))


func _draw_field_actor(tile: Vector2i, color: Color, symbol: String, origin: Vector2, tile_size: float) -> void:
	var rect: Rect2 = _tile_rect(tile, origin, tile_size).grow(-tile_size * 0.18)
	draw_rect(rect, OUTLINE)
	draw_rect(rect.grow(-2.0), color)
	if not symbol.is_empty():
		draw_string(ThemeDB.fallback_font, rect.position + Vector2(tile_size * 0.18, tile_size * 0.58), symbol, HORIZONTAL_ALIGNMENT_LEFT, -1, int(maxf(14.0, tile_size * 0.42)), INK)


func _draw_battle() -> void:
	var origin: Vector2 = _grid_origin()
	var tile_size: float = _battle_tile_size()
	var player: Dictionary = _player_combatant()
	if action_mode == "move" and not player.is_empty():
		var remaining: int = maxi(0, int(player.get("movement", 0)) - int(player.get("movement_used", 0)))
		var start := _actor_tile(player)
		for y in range(BATTLE_ROWS):
			for x in range(BATTLE_COLS):
				var candidate := Vector2i(x, y)
				var distance: int = absi(candidate.x - start.x) + absi(candidate.y - start.y)
				if distance <= remaining and not _battle_tile_occupied(candidate):
					draw_rect(_tile_rect(candidate, origin, tile_size), MOVE_COLOR)
	for y in range(BATTLE_ROWS):
		for x in range(BATTLE_COLS):
			var rect := Rect2(origin + Vector2(x, y) * tile_size, Vector2(tile_size, tile_size))
			var color := Color("#314238") if (x + y) % 2 == 0 else Color("#3a4e41")
			draw_rect(rect, color, false, 1.0)
	for actor_value in _combatants():
		if not actor_value is Dictionary:
			continue
		var actor: Dictionary = actor_value
		if int(actor.get("hp", 0)) <= 0:
			continue
		var tile: Vector2i = _actor_tile(actor)
		if tile.x < 0 or tile.x >= BATTLE_COLS or tile.y < 0 or tile.y >= BATTLE_ROWS:
			continue
		var rect: Rect2 = _tile_rect(tile, origin, tile_size).grow(-tile_size * 0.12)
		var team_color: Color = ALLY_COLOR if str(actor.get("team", "enemy")) == "player" else ENEMY_COLOR
		draw_rect(rect, OUTLINE)
		draw_rect(rect.grow(-3.0), team_color)
		var name_text: String = str(actor.get("name", "Actor"))
		var short_name: String = name_text.left(8)
		draw_string(ThemeDB.fallback_font, rect.position + Vector2(4, tile_size * 0.45), short_name, HORIZONTAL_ALIGNMENT_LEFT, tile_size - 8.0, int(maxf(10.0, tile_size * 0.2)), OUTLINE)
		var hp_text := "%d/%d" % [int(actor.get("hp", 0)), int(actor.get("max_hp", 0))]
		draw_string(ThemeDB.fallback_font, rect.position + Vector2(4, tile_size * 0.78), hp_text, HORIZONTAL_ALIGNMENT_LEFT, tile_size - 8.0, int(maxf(10.0, tile_size * 0.18)), OUTLINE)
		if str(actor.get("name", "")) == str(_combat().get("current_actor", "")):
			draw_rect(rect.grow(3.0), PLAYER_COLOR, false, 3.0)
	if action_mode in ["attack", "ability"]:
		draw_string(ThemeDB.fallback_font, origin + Vector2(0, -10), "SELECT A TARGET SQUARE", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, PLAYER_COLOR)


func _unhandled_input(event: InputEvent) -> void:
	if not visible or busy or not event is InputEventKey:
		return
	var key_event := event as InputEventKey
	if not key_event.pressed or key_event.echo:
		return
	if mode == "explore":
		var direction := Vector2i.ZERO
		match key_event.keycode:
			KEY_W, KEY_UP:
				direction = Vector2i(0, -1)
			KEY_S, KEY_DOWN:
				direction = Vector2i(0, 1)
			KEY_A, KEY_LEFT:
				direction = Vector2i(-1, 0)
			KEY_D, KEY_RIGHT:
				direction = Vector2i(1, 0)
			KEY_E, KEY_SPACE:
				_interact()
		if direction != Vector2i.ZERO:
			_move_player(direction)
	else:
		if key_event.keycode == KEY_ESCAPE:
			action_mode = ""
			chosen_ability.clear()
			_set_message("Choose a tactical command.")
			queue_redraw()


func _gui_input(event: InputEvent) -> void:
	if not visible or busy or mode != "battle" or action_mode.is_empty():
		return
	if not event is InputEventMouseButton:
		return
	var mouse_event := event as InputEventMouseButton
	if mouse_event.button_index != MOUSE_BUTTON_LEFT or not mouse_event.pressed:
		return
	var tile: Vector2i = _battle_tile_from_point(mouse_event.position)
	if tile.x < 0:
		return
	if action_mode == "move":
		_post("/combat/move", {"x": tile.x, "y": tile.y}, "combat")
		return
	var target: Dictionary = _actor_at(tile)
	if target.is_empty():
		_set_message("Choose a square occupied by a target.")
		return
	if action_mode == "attack":
		_post("/combat/attack", {"target": str(target.get("name", ""))}, "combat")
	elif action_mode == "ability":
		_post("/combat/ability", {"ability": str(chosen_ability.get("name", "")), "target": str(target.get("name", ""))}, "combat")


func _move_player(direction: Vector2i) -> void:
	facing = direction
	var destination: Vector2i = player_tile + direction
	if blocked.has(destination) or destination == npc_tile:
		queue_redraw()
		return
	player_tile = destination
	if destination == Vector2i(16, 5):
		_request_story("I enter the nearby building and look for what is immediately visible. Keep secrets and distant locations hidden.")
	queue_redraw()


func _interact() -> void:
	if busy:
		return
	var front: Vector2i = player_tile + facing
	var near_npc: bool = front == npc_tile or _tile_distance(player_tile, npc_tile) <= 1
	if near_npc:
		_request_story("I speak to the nearby local. Give one short in-world reply and at most one immediate lead. Do not reveal undiscovered secrets, locations, factions, or events.")
	else:
		_request_story("I inspect my immediate surroundings. Describe only what I can currently see or notice here, in two or three short sentences. Do not reveal undiscovered secrets.")


func _ask_about_place() -> void:
	if not _require_near_npc():
		return
	_request_story("I ask the nearby local about this immediate area. Give a brief useful answer without revealing hidden locations, future events, secret factions, or major surprises.")


func _ask_for_work() -> void:
	if not _require_near_npc():
		return
	_request_story("I ask the nearby local if there is one small problem close by that I could help with. Give one concise quest hook and keep all larger mysteries hidden.")


func _require_near_npc() -> bool:
	if _tile_distance(player_tile, npc_tile) <= 1:
		return true
	_set_message("Walk next to the marked character before speaking with them.")
	return false


func _tile_distance(a: Vector2i, b: Vector2i) -> int:
	return absi(a.x - b.x) + absi(a.y - b.y)


func _request_story(action_text: String) -> void:
	_post("/action", {"action": action_text}, "story")


func _start_training_battle() -> void:
	_post("/prototype/battle/start", {}, "battle_start")


func _select_move() -> void:
	if not _can_act():
		return
	action_mode = "move"
	chosen_ability.clear()
	_set_message("Select a highlighted square. Movement uses your remaining movement for this turn.")
	queue_redraw()


func _select_attack() -> void:
	if not _can_act():
		return
	action_mode = "attack"
	chosen_ability.clear()
	_set_message("Select an enemy in range. A basic attack ends your turn.")
	queue_redraw()


func _defend() -> void:
	if not _can_act():
		return
	_post("/combat/defend", {}, "combat")


func _end_turn() -> void:
	if not _can_act():
		return
	_post("/combat/end_turn", {}, "combat")


func _select_ability(ability: Dictionary) -> void:
	if not _can_act():
		return
	chosen_ability = ability
	if str(ability.get("target", "enemy")) == "self":
		_post("/combat/ability", {"ability": str(ability.get("name", "")), "target": str(_player_combatant().get("name", ""))}, "combat")
		return
	action_mode = "ability"
	_set_message("Select a target for %s." % str(ability.get("name", "this ability")))
	queue_redraw()


func _can_act() -> bool:
	var player: Dictionary = _player_combatant()
	if player.is_empty():
		_set_message("No active player combatant was found.")
		return false
	if str(_combat().get("current_actor", "")) != str(player.get("name", "")):
		_set_message("It is not your turn yet.")
		return false
	return true


func _post(path: String, body: Dictionary, next_request_mode: String) -> void:
	if busy:
		return
	busy = true
	request_mode = next_request_mode
	action_mode = ""
	chosen_ability.clear()
	_set_buttons_disabled(true)
	_set_message("Thinking...")
	var headers := PackedStringArray(["Content-Type: application/json"])
	var error: int = http.request(API_BASE + path, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	if error != OK:
		busy = false
		_set_buttons_disabled(false)
		_set_message("Could not reach the local game server. Make sure python -m backend.api is running.")


func _on_request_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	busy = false
	_set_buttons_disabled(false)
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if not parsed is Dictionary:
		_set_message("The game server returned an unreadable response.")
		return
	var payload: Dictionary = parsed
	if response_code < 200 or response_code >= 300 or not bool(payload.get("ok", true)):
		_set_message(str(payload.get("error", "The action could not be completed.")))
		return
	if payload.get("state") is Dictionary:
		game_state = payload.get("state", {})
	var combat: Dictionary = _combat()
	var was_battle: bool = mode == "battle" or request_mode in ["battle_start", "combat"]
	if bool(combat.get("active", false)):
		mode = "battle"
	elif was_battle:
		mode = "explore"
	_update_main_controller(payload)
	_update_header()
	_refresh_mode_interface()
	var narration: String = str(payload.get("narration", ""))
	if narration.is_empty():
		narration = "Action complete."
	_set_message(narration)
	request_mode = ""
	queue_redraw()


func _update_main_controller(payload: Dictionary) -> void:
	if main_controller == null:
		return
	main_controller.set("latest_state", game_state)
	if main_controller.has_method("_update_player_panel"):
		main_controller.call("_update_player_panel")
	if main_controller.has_method("_set_narration") and not str(payload.get("narration", "")).is_empty():
		main_controller.call("_set_narration", str(payload.get("narration", "")))


func _update_header() -> void:
	if mode == "battle":
		title_label.text = "TACTICAL ENCOUNTER"
		var combat: Dictionary = _combat()
		subtitle_label.text = "Round %d  •  Current turn: %s" % [int(combat.get("round", 1)), str(combat.get("current_actor", "Unknown"))]
	else:
		var world: Dictionary = game_state.get("world_profile", {}) if game_state.get("world_profile") is Dictionary else {}
		var campaign: Dictionary = game_state.get("campaign", {}) if game_state.get("campaign") is Dictionary else {}
		var world_name: String = str(world.get("name", campaign.get("name", "THE SHATTERED REALMS")))
		var location: String = str(game_state.get("current_location", "Frontier Outpost"))
		title_label.text = world_name.to_upper()
		subtitle_label.text = location + "  •  Explore to uncover the story"


func _refresh_mode_interface() -> void:
	explore_panel.visible = mode == "explore"
	battle_panel.visible = mode == "battle"
	if mode == "battle":
		_refresh_battle_status()
		_refresh_abilities()


func _refresh_battle_status() -> void:
	var player: Dictionary = _player_combatant()
	if player.is_empty():
		status_label.text = "Waiting for combat data..."
		return
	var remaining: int = maxi(0, int(player.get("movement", 0)) - int(player.get("movement_used", 0)))
	status_label.text = "%s\nHP %d/%d  •  Resource %d/%d\nMovement left: %d squares" % [
		str(player.get("name", "Player")),
		int(player.get("hp", 0)),
		int(player.get("max_hp", 0)),
		int(player.get("resource", 0)),
		int(player.get("max_resource", 0)),
		remaining,
	]


func _refresh_abilities() -> void:
	for child in ability_box.get_children():
		child.queue_free()
	var player: Dictionary = _player_combatant()
	var abilities = player.get("abilities", [])
	if not abilities is Array or abilities.is_empty():
		var empty_label := Label.new()
		empty_label.text = "No equipped abilities"
		empty_label.add_theme_color_override("font_color", MUTED)
		ability_box.add_child(empty_label)
		return
	for ability_value in abilities:
		if not ability_value is Dictionary:
			continue
		var ability: Dictionary = ability_value
		var label_text := "%s  [%d]" % [str(ability.get("name", "Ability")), int(ability.get("resource_cost", 0))]
		var button := _action_button(label_text, _select_ability.bind(ability))
		button.tooltip_text = str(ability.get("description", ""))
		ability_box.add_child(button)


func _set_message(text: String) -> void:
	message_label.text = text


func _set_buttons_disabled(disabled: bool) -> void:
	for panel in [explore_actions, battle_actions]:
		if panel == null:
			continue
		for child in panel.get_children():
			if child is Button:
				(child as Button).disabled = disabled
	for child in ability_box.get_children():
		if child is Button:
			(child as Button).disabled = disabled


func _combat() -> Dictionary:
	var value = game_state.get("combat", {})
	return value if value is Dictionary else {}


func _combatants() -> Array:
	var value = _combat().get("combatants", [])
	return value if value is Array else []


func _player_combatant() -> Dictionary:
	for actor_value in _combatants():
		if actor_value is Dictionary and str(actor_value.get("team", "")) == "player":
			return actor_value
	return {}


func _actor_tile(actor: Dictionary) -> Vector2i:
	var position_value = actor.get("position", {})
	if position_value is Dictionary:
		return Vector2i(int(position_value.get("x", 0)), int(position_value.get("y", 0)))
	return Vector2i.ZERO


func _battle_tile_occupied(tile: Vector2i) -> bool:
	return not _actor_at(tile).is_empty()


func _actor_at(tile: Vector2i) -> Dictionary:
	for actor_value in _combatants():
		if actor_value is Dictionary and int(actor_value.get("hp", 0)) > 0 and _actor_tile(actor_value) == tile:
			return actor_value
	return {}


func _battle_tile_from_point(point: Vector2) -> Vector2i:
	var origin: Vector2 = _grid_origin()
	var tile_size: float = _battle_tile_size()
	var local: Vector2 = point - origin
	if local.x < 0.0 or local.y < 0.0:
		return Vector2i(-1, -1)
	var tile := Vector2i(int(floor(local.x / tile_size)), int(floor(local.y / tile_size)))
	if tile.x >= BATTLE_COLS or tile.y >= BATTLE_ROWS:
		return Vector2i(-1, -1)
	return tile
