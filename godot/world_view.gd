extends Control

const API_BASE := "http://127.0.0.1:8765"
const WORLD_COLS := 48
const WORLD_ROWS := 34
const TILE := 32.0
const BATTLE_COLS := 12
const BATTLE_ROWS := 8

const INK := Color("#f2f0cf")
const MUTED := Color("#b6c69e")
const DARK := Color("#101a19")
const OUTLINE := Color("#172723")
const PANEL := Color("#20352d")
const PLAYER_COLOR := Color("#f2d36b")
const ALLY_COLOR := Color("#65c3a0")
const ENEMY_COLOR := Color("#dc675f")
const MOVE_COLOR := Color(0.28, 0.86, 0.73, 0.3)
const HOLD_FIRST_DELAY := 0.20
const HOLD_STEP_DELAY := 0.115

var main_controller: Control
var http: HTTPRequest
var game_state: Dictionary = {}
var mode: String = "explore"
var request_mode: String = ""
var busy: bool = false

var player_tile := Vector2i(24, 23)
var player_visual := Vector2(24, 23)
var facing := Vector2i(0, -1)
var npc_tile := Vector2i(28, 21)
var primary_door := Vector2i(34, 18)
var secondary_door := Vector2i(18, 10)
var moving: bool = false
var walk_frame: int = 0
var blocked: Dictionary = {}
var tree_tiles: Array[Vector2i] = []
var rock_tiles: Array[Vector2i] = []
var flower_tiles: Array[Vector2i] = []
var lamp_tiles: Array[Vector2i] = []
var tech_world: bool = false
var current_area: Dictionary = {}
var area_landmarks: Array = []
var area_npcs: Array = []
var landmark_doors: Dictionary = {}
var area_palette: String = "lush"
var ground_style: String = "grass"
var visual_features: Array = []
var area_loaded: bool = false
var pending_exit_direction: String = ""
var area_coord := Vector2i.ZERO
var loaded_areas: Dictionary = {}
var area_render_cache: Dictionary = {}
var pending_step_direction := Vector2i.ZERO
var player_position_initialized: bool = false
var loaded_world_signature: String = ""
var held_direction := Vector2i.ZERO
var held_move_timer: float = 0.0

var title_label: Label
var subtitle_label: Label
var hint_label: Label
var dialogue_panel: PanelContainer
var dialogue_label: RichTextLabel
var dialogue_choices: VBoxContainer
var suggestion_row: HBoxContainer
var custom_action_input: LineEdit
var custom_action_button: Button
var suggestion_buttons: Array[Button] = []
var character_button: Button
var character_panel: PanelContainer
var character_text: RichTextLabel
var character_section: String = "stats"
var character_tab_buttons: Array[Button] = []
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
	_build_world()
	http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_request_completed)
	set_process_unhandled_input(true)
	visible = false


func bind_main(value: Control) -> void:
	main_controller = value


func _process(delta: float) -> void:
	if moving:
		queue_redraw()
	_process_held_movement(delta)


func _process_held_movement(delta: float) -> void:
	if not visible or mode != "explore" or busy or character_panel.visible:
		held_direction = Vector2i.ZERO
		held_move_timer = 0.0
		return
	var focused: Control = get_viewport().gui_get_focus_owner()
	if focused is LineEdit or focused is TextEdit:
		held_direction = Vector2i.ZERO
		held_move_timer = 0.0
		return
	var direction: Vector2i = _held_movement_direction()
	if direction == Vector2i.ZERO:
		held_direction = Vector2i.ZERO
		held_move_timer = 0.0
		return
	if direction != held_direction:
		held_direction = direction
		held_move_timer = HOLD_FIRST_DELAY
		if not moving:
			_hide_dialogue()
			_move_player(direction)
		return
	held_move_timer = maxf(0.0, held_move_timer - delta)
	if held_move_timer <= 0.0 and not moving:
		held_move_timer = HOLD_STEP_DELAY
		_hide_dialogue()
		_move_player(direction)


func _held_movement_direction() -> Vector2i:
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W):
		return Vector2i(0, -1)
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S):
		return Vector2i(0, 1)
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A):
		return Vector2i(-1, 0)
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D):
		return Vector2i(1, 0)
	return Vector2i.ZERO


func show_from_payload(payload: Dictionary = {}) -> void:
	if payload.get("state") is Dictionary:
		game_state = payload.get("state", {})
	elif not payload.is_empty() and payload.get("player") is Dictionary:
		game_state = payload
	_load_discovered_areas()
	_apply_area_from_state()
	_update_world_theme()
	var combat: Dictionary = _combat()
	mode = "battle" if bool(combat.get("active", false)) else "explore"
	visible = true
	player_visual = Vector2(player_tile)
	_update_header()
	_refresh_character_sheet()
	_refresh_mode_interface()
	var narration: String = str(payload.get("narration", "")).strip_edges()
	if not narration.is_empty():
		_set_message(narration, payload.get("suggested_actions", []))
	elif mode == "explore":
		_hide_dialogue()
	if mode == "explore" and not area_loaded and not busy:
		call_deferred("_request_world_area", "current")
	queue_redraw()


func hide_view() -> void:
	visible = false


func _build_interface() -> void:
	title_label = Label.new()
	title_label.position = Vector2(24, 18)
	title_label.size = Vector2(760, 34)
	title_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	title_label.add_theme_font_size_override("font_size", 24)
	title_label.add_theme_color_override("font_color", INK)
	title_label.add_theme_color_override("font_shadow_color", DARK)
	title_label.add_theme_constant_override("shadow_offset_x", 2)
	title_label.add_theme_constant_override("shadow_offset_y", 2)
	add_child(title_label)

	subtitle_label = Label.new()
	subtitle_label.position = Vector2(26, 51)
	subtitle_label.size = Vector2(760, 24)
	subtitle_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	subtitle_label.add_theme_font_size_override("font_size", 14)
	subtitle_label.add_theme_color_override("font_color", MUTED)
	subtitle_label.add_theme_color_override("font_shadow_color", DARK)
	subtitle_label.add_theme_constant_override("shadow_offset_x", 1)
	subtitle_label.add_theme_constant_override("shadow_offset_y", 1)
	add_child(subtitle_label)

	hint_label = Label.new()
	hint_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hint_label.position = Vector2(-760, 61)
	hint_label.size = Vector2(420, 24)
	hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hint_label.text = "MOVE  WASD / ARROWS     INTERACT  E / SPACE     CHARACTER  C"
	hint_label.add_theme_font_size_override("font_size", 12)
	hint_label.add_theme_color_override("font_color", MUTED)
	add_child(hint_label)

	character_button = _action_button("CHARACTER", _toggle_character_panel, 132)
	character_button.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	character_button.offset_left = -296.0
	character_button.offset_top = 18.0
	character_button.offset_right = -156.0
	character_button.offset_bottom = 58.0
	character_button.z_index = 2000
	character_button.mouse_filter = Control.MOUSE_FILTER_STOP
	character_button.process_mode = Node.PROCESS_MODE_ALWAYS
	character_button.tooltip_text = "Open stats, inventory, gear, and abilities (C)"
	add_child(character_button)

	character_panel = PanelContainer.new()
	character_panel.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	character_panel.offset_left = -470.0
	character_panel.offset_top = 78.0
	character_panel.offset_right = -24.0
	character_panel.offset_bottom = -24.0
	character_panel.z_index = 1990
	character_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	character_panel.process_mode = Node.PROCESS_MODE_ALWAYS
	character_panel.add_theme_stylebox_override("panel", _panel_style(Color("#182a31"), _palette_color("accent"), 3))
	add_child(character_panel)
	var sheet_margin := MarginContainer.new()
	sheet_margin.add_theme_constant_override("margin_left", 18)
	sheet_margin.add_theme_constant_override("margin_top", 16)
	sheet_margin.add_theme_constant_override("margin_right", 18)
	sheet_margin.add_theme_constant_override("margin_bottom", 16)
	character_panel.add_child(sheet_margin)
	var sheet_stack := VBoxContainer.new()
	sheet_stack.add_theme_constant_override("separation", 10)
	sheet_margin.add_child(sheet_stack)
	var sheet_heading := Label.new()
	sheet_heading.text = "CHARACTER"
	sheet_heading.add_theme_font_size_override("font_size", 24)
	sheet_heading.add_theme_color_override("font_color", INK)
	sheet_stack.add_child(sheet_heading)
	var tab_row := HBoxContainer.new()
	tab_row.add_theme_constant_override("separation", 6)
	sheet_stack.add_child(tab_row)
	var tab_sections: Array[String] = ["stats", "inventory", "equipment", "abilities"]
	var tab_labels: Array[String] = ["STATS", "INVENTORY", "GEAR", "ABILITIES"]
	for index in range(tab_sections.size()):
		var tab_button := _action_button(tab_labels[index], _set_character_section.bind(tab_sections[index]))
		tab_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tab_button.custom_minimum_size.y = 38
		tab_button.set_meta("section", tab_sections[index])
		tab_button.set_meta("base_label", tab_labels[index])
		character_tab_buttons.append(tab_button)
		tab_row.add_child(tab_button)
	character_text = RichTextLabel.new()
	character_text.bbcode_enabled = true
	character_text.scroll_active = true
	character_text.fit_content = false
	character_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	character_text.add_theme_font_size_override("normal_font_size", 16)
	character_text.add_theme_font_size_override("bold_font_size", 18)
	character_text.add_theme_color_override("default_color", INK)
	sheet_stack.add_child(character_text)
	var close_sheet_button := _action_button("CLOSE", _toggle_character_panel)
	close_sheet_button.custom_minimum_size.y = 42
	sheet_stack.add_child(close_sheet_button)
	character_panel.visible = false

	dialogue_panel = PanelContainer.new()
	dialogue_panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	dialogue_panel.offset_left = 72.0
	dialogue_panel.offset_top = -228.0
	dialogue_panel.offset_right = -72.0
	dialogue_panel.offset_bottom = -24.0
	dialogue_panel.add_theme_stylebox_override("panel", _panel_style(Color("#16251f"), INK, 4))
	add_child(dialogue_panel)
	var dialogue_margin := MarginContainer.new()
	dialogue_margin.add_theme_constant_override("margin_left", 18)
	dialogue_margin.add_theme_constant_override("margin_top", 14)
	dialogue_margin.add_theme_constant_override("margin_right", 18)
	dialogue_margin.add_theme_constant_override("margin_bottom", 12)
	dialogue_panel.add_child(dialogue_margin)
	var dialogue_stack := VBoxContainer.new()
	dialogue_stack.add_theme_constant_override("separation", 8)
	dialogue_margin.add_child(dialogue_stack)
	dialogue_label = RichTextLabel.new()
	dialogue_label.custom_minimum_size = Vector2(0, 72)
	dialogue_label.bbcode_enabled = true
	dialogue_label.fit_content = false
	dialogue_label.scroll_active = true
	dialogue_label.add_theme_font_size_override("normal_font_size", 17)
	dialogue_label.add_theme_color_override("default_color", INK)
	dialogue_stack.add_child(dialogue_label)
	dialogue_choices = VBoxContainer.new()
	dialogue_choices.add_theme_constant_override("separation", 8)
	dialogue_stack.add_child(dialogue_choices)
	suggestion_row = HBoxContainer.new()
	suggestion_row.alignment = BoxContainer.ALIGNMENT_CENTER
	suggestion_row.add_theme_constant_override("separation", 8)
	dialogue_choices.add_child(suggestion_row)
	for index in range(3):
		var suggestion := _action_button("OPTION %d" % (index + 1), _choose_suggestion.bind(index))
		suggestion.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		suggestion.custom_minimum_size.y = 42
		suggestion_buttons.append(suggestion)
		suggestion_row.add_child(suggestion)
	var custom_row := HBoxContainer.new()
	custom_row.add_theme_constant_override("separation", 8)
	dialogue_choices.add_child(custom_row)
	custom_action_input = LineEdit.new()
	custom_action_input.placeholder_text = "Or type anything you want to do..."
	custom_action_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	custom_action_input.custom_minimum_size.y = 40
	custom_action_input.text_submitted.connect(_submit_custom_action)
	custom_row.add_child(custom_action_input)
	custom_action_button = _action_button("DO IT", _submit_custom_action_from_button, 120)
	custom_row.add_child(custom_action_button)
	custom_row.add_child(_action_button("CLOSE", _hide_dialogue, 100))
	dialogue_panel.visible = false
	dialogue_choices.visible = false

	battle_panel = PanelContainer.new()
	battle_panel.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	battle_panel.offset_left = -390.0
	battle_panel.offset_top = 100.0
	battle_panel.offset_right = -28.0
	battle_panel.offset_bottom = -28.0
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
	battle_panel.visible = false


func _panel_style(color: Color, border_color: Color, width: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = border_color
	style.set_border_width_all(width)
	style.corner_radius_top_left = 2
	style.corner_radius_top_right = 2
	style.corner_radius_bottom_left = 2
	style.corner_radius_bottom_right = 2
	return style


func _action_button(label_text: String, callback: Callable, minimum_width: int = 0) -> Button:
	var button := Button.new()
	button.text = label_text
	button.focus_mode = Control.FOCUS_NONE
	button.custom_minimum_size = Vector2(minimum_width, 38)
	button.add_theme_font_size_override("font_size", 14)
	button.add_theme_color_override("font_color", INK)
	button.add_theme_stylebox_override("normal", _panel_style(Color("#2c493c"), Color("#53735d"), 2))
	button.add_theme_stylebox_override("hover", _panel_style(Color("#3c6250"), INK, 2))
	button.pressed.connect(callback)
	return button


func _build_world() -> void:
	if current_area.is_empty():
		current_area = {
			"x": 0,
			"y": 0,
			"seed": 1337,
			"name": "Generating Area",
			"palette": "lush",
			"ground_style": "grass",
			"visual_features": ["trees", "flowers", "rocks", "water"],
			"landmarks": [
				{"name": "Waypoint", "type": "station", "x": 30, "y": 12, "width": 9, "height": 7, "interaction_prompt": "I inspect the waypoint."},
				{"name": "Supply Post", "type": "shop", "x": 15, "y": 6, "width": 7, "height": 5, "interaction_prompt": "I inspect the supply post."},
			],
			"npcs": [
				{"name": "Local Guide", "role": "guide", "x": 28, "y": 21, "look": "friendly local clothing"},
			],
		}
	area_coord = Vector2i(int(current_area.get("x", area_coord.x)), int(current_area.get("y", area_coord.y)))
	var key: String = _area_key(area_coord)
	loaded_areas[key] = current_area.duplicate(true)
	var cache: Dictionary = _build_area_cache(current_area)
	area_render_cache[key] = cache
	_apply_area_cache(current_area, cache)


func _build_area_cache(area: Dictionary) -> Dictionary:
	var features: Array = area.get("visual_features", []) if area.get("visual_features") is Array else []
	var landmarks: Array = area.get("landmarks", []) if area.get("landmarks") is Array else []
	var npcs: Array = area.get("npcs", []) if area.get("npcs") is Array else []
	var trees: Array[Vector2i] = []
	var rocks: Array[Vector2i] = []
	var flowers: Array[Vector2i] = []
	var lamps: Array[Vector2i] = []
	var doors: Dictionary = {}
	var area_blocked: Dictionary = {}

	for landmark_value in landmarks:
		if not landmark_value is Dictionary:
			continue
		var landmark: Dictionary = landmark_value
		var left: int = int(landmark.get("x", 30))
		var top: int = int(landmark.get("y", 11))
		var width: int = maxi(5, int(landmark.get("width", 8)))
		var height: int = maxi(4, int(landmark.get("height", 6)))
		for y in range(top, mini(WORLD_ROWS, top + height)):
			for x in range(left, mini(WORLD_COLS, left + width)):
				area_blocked[Vector2i(x, y)] = true
		var door := Vector2i(left + int(width / 2), top + height - 1)
		doors[door] = landmark

	if _feature_in(features, "water") or _feature_in(features, "river") or _feature_in(features, "pond"):
		for y in range(5, 12):
			for x in range(4, 14):
				if not ((x == 4 or x == 13) and (y == 5 or y == 11)):
					area_blocked[Vector2i(x, y)] = true

	var rng := RandomNumberGenerator.new()
	rng.seed = int(area.get("seed", 1337))
	var tree_count: int = 42 if _feature_in(features, "trees") or _feature_in(features, "snow_pines") else 10
	var rock_count: int = 12 if _feature_in(features, "rocks") or _feature_in(features, "crystals") or _feature_in(features, "cactus") else 5
	var flower_count: int = 24 if _feature_in(features, "flowers") or _feature_in(features, "coral") else 7
	var lamp_count: int = 12 if _feature_in(features, "street_lights") or _feature_in(features, "holograms") else 0
	_scatter_area_tiles(rng, trees, tree_count, true, area_blocked, doors, npcs, trees, rocks, flowers, lamps)
	_scatter_area_tiles(rng, rocks, rock_count, true, area_blocked, doors, npcs, trees, rocks, flowers, lamps)
	_scatter_area_tiles(rng, flowers, flower_count, false, area_blocked, doors, npcs, trees, rocks, flowers, lamps)
	_scatter_area_tiles(rng, lamps, lamp_count, false, area_blocked, doors, npcs, trees, rocks, flowers, lamps)
	for tile in trees:
		area_blocked[tile] = true
	for tile in rocks:
		area_blocked[tile] = true
	return {"trees": trees, "rocks": rocks, "flowers": flowers, "lamps": lamps, "doors": doors, "blocked": area_blocked}


func _scatter_area_tiles(rng: RandomNumberGenerator, target: Array[Vector2i], count: int, needs_clear_space: bool, area_blocked: Dictionary, doors: Dictionary, npcs: Array, trees: Array[Vector2i], rocks: Array[Vector2i], flowers: Array[Vector2i], lamps: Array[Vector2i]) -> void:
	var attempts: int = 0
	while target.size() < count and attempts < count * 30 + 30:
		attempts += 1
		var tile := Vector2i(rng.randi_range(2, WORLD_COLS - 3), rng.randi_range(2, WORLD_ROWS - 3))
		if _is_path_for(tile, doors) or area_blocked.has(tile) or _npc_in_list(npcs, tile):
			continue
		if needs_clear_space and _near_map_exit(tile):
			continue
		if tile in trees or tile in rocks or tile in flowers or tile in lamps:
			continue
		target.append(tile)


func _npc_in_list(npcs: Array, tile: Vector2i) -> bool:
	for npc_value in npcs:
		if npc_value is Dictionary and Vector2i(int(npc_value.get("x", -100)), int(npc_value.get("y", -100))) == tile:
			return true
	return false


func _feature_in(features: Array, feature_name: String) -> bool:
	return feature_name in features


func _apply_area_cache(area: Dictionary, cache: Dictionary) -> void:
	area_palette = str(area.get("palette", "lush")).to_lower()
	ground_style = str(area.get("ground_style", "grass")).to_lower()
	visual_features = area.get("visual_features", []) if area.get("visual_features") is Array else []
	area_landmarks = area.get("landmarks", []) if area.get("landmarks") is Array else []
	area_npcs = area.get("npcs", []) if area.get("npcs") is Array else []
	tree_tiles.assign(cache.get("trees", []))
	rock_tiles.assign(cache.get("rocks", []))
	flower_tiles.assign(cache.get("flowers", []))
	lamp_tiles.assign(cache.get("lamps", []))
	landmark_doors = cache.get("doors", {}).duplicate(true)
	blocked = cache.get("blocked", {}).duplicate(true)
	if not area_npcs.is_empty() and area_npcs[0] is Dictionary:
		npc_tile = Vector2i(int(area_npcs[0].get("x", 28)), int(area_npcs[0].get("y", 21)))
	_update_world_theme(area)


func _near_map_exit(tile: Vector2i) -> bool:
	var center_x: int = int(WORLD_COLS / 2)
	var center_y: int = 21
	return ((tile.x <= 3 or tile.x >= WORLD_COLS - 4) and absi(tile.y - center_y) <= 3) or ((tile.y <= 3 or tile.y >= WORLD_ROWS - 4) and absi(tile.x - center_x) <= 3)


func _feature_enabled(feature_name: String) -> bool:
	return feature_name in visual_features


func _area_key(coord: Vector2i) -> String:
	return "%d,%d" % [coord.x, coord.y]


func _area_coord_from_world_tile(tile: Vector2i) -> Vector2i:
	return Vector2i(floori(float(tile.x) / float(WORLD_COLS)), floori(float(tile.y) / float(WORLD_ROWS)))


func _area_world_origin(coord: Vector2i) -> Vector2i:
	return Vector2i(coord.x * WORLD_COLS, coord.y * WORLD_ROWS)


func _local_tile(world_tile: Vector2i) -> Vector2i:
	return world_tile - _area_world_origin(area_coord)


func _load_discovered_areas() -> void:
	var signature: String = JSON.stringify(game_state.get("world_profile", {}))
	if signature != loaded_world_signature:
		loaded_world_signature = signature
		loaded_areas.clear()
		area_render_cache.clear()
		player_position_initialized = false
		area_loaded = false
	var exploration: Dictionary = game_state.get("exploration", {}) if game_state.get("exploration") is Dictionary else {}
	var saved_areas: Dictionary = exploration.get("areas", {}) if exploration.get("areas") is Dictionary else {}
	for area_value in saved_areas.values():
		if not area_value is Dictionary:
			continue
		var saved: Dictionary = area_value
		var coord := Vector2i(int(saved.get("x", 0)), int(saved.get("y", 0)))
		var key: String = _area_key(coord)
		loaded_areas[key] = saved.duplicate(true)
		if not area_render_cache.has(key):
			area_render_cache[key] = _build_area_cache(saved)
	area_coord = Vector2i(int(exploration.get("current_x", 0)), int(exploration.get("current_y", 0)))
	if not player_position_initialized:
		player_tile = _area_world_origin(area_coord) + Vector2i(24, 23)
		player_visual = Vector2(player_tile)
		player_position_initialized = true


func _apply_area_from_state() -> void:
	var exploration: Dictionary = game_state.get("exploration", {}) if game_state.get("exploration") is Dictionary else {}
	var saved_area: Dictionary = exploration.get("current_area", {}) if exploration.get("current_area") is Dictionary else {}
	if not saved_area.is_empty():
		_apply_area(saved_area)


func _apply_area(area: Dictionary) -> void:
	current_area = area.duplicate(true)
	area_coord = Vector2i(int(current_area.get("x", area_coord.x)), int(current_area.get("y", area_coord.y)))
	area_loaded = true
	_build_world()
	_update_header()
	queue_redraw()


func _update_world_theme(area: Dictionary = {}) -> void:
	var source: Dictionary = current_area if area.is_empty() else area
	area_palette = str(source.get("palette", area_palette)).to_lower()
	ground_style = str(source.get("ground_style", ground_style)).to_lower()
	var world_text: String = JSON.stringify(game_state.get("world_profile", {})).to_lower()
	tech_world = area_palette in ["neon", "cosmic", "urban"] or ground_style in ["metal", "pavement"]
	if not tech_world:
		for word in ["cyber", "sci-fi", "science fiction", "space", "neon", "future", "technology", "starship"]:
			if world_text.contains(word):
				tech_world = true
				break


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), DARK)
	if mode == "battle":
		_draw_battle()
	else:
		_draw_overworld()


func _camera_origin() -> Vector2:
	var target := Vector2(size.x * 0.5, size.y * 0.5) - (player_visual + Vector2(0.5, 0.5)) * TILE
	return Vector2(round(target.x), round(target.y))


func _world_rect(tile: Vector2i, origin: Vector2, grow: float = 0.0) -> Rect2:
	return Rect2(origin + Vector2(tile) * TILE, Vector2(TILE, TILE)).grow(grow)


func _draw_overworld() -> void:
	var camera_origin: Vector2 = _camera_origin()
	var visible_rect := Rect2(Vector2(-TILE, -TILE), size + Vector2(TILE * 2.0, TILE * 2.0))
	for area_value in loaded_areas.values():
		if not area_value is Dictionary:
			continue
		var area: Dictionary = area_value
		var coord := Vector2i(int(area.get("x", 0)), int(area.get("y", 0)))
		var key: String = _area_key(coord)
		var chunk_origin: Vector2 = camera_origin + Vector2(_area_world_origin(coord)) * TILE
		var chunk_rect := Rect2(chunk_origin, Vector2(float(WORLD_COLS) * TILE, float(WORLD_ROWS) * TILE))
		if not chunk_rect.intersects(visible_rect):
			continue
		if not area_render_cache.has(key):
			area_render_cache[key] = _build_area_cache(area)
		var cache: Dictionary = area_render_cache[key]
		_apply_area_cache(area, cache)
		_draw_area_chunk(area, chunk_origin)
	var current_key: String = _area_key(area_coord)
	if loaded_areas.has(current_key) and area_render_cache.has(current_key):
		_apply_area_cache(loaded_areas[current_key], area_render_cache[current_key])
	_draw_character(Vector2i.ZERO, camera_origin, true)


func _draw_area_chunk(_area: Dictionary, origin: Vector2) -> void:
	for y in range(WORLD_ROWS):
		for x in range(WORLD_COLS):
			_draw_ground(Vector2i(x, y), origin)
	for landmark_value in area_landmarks:
		if not landmark_value is Dictionary:
			continue
		var landmark: Dictionary = landmark_value
		var landmark_tile := Vector2i(int(landmark.get("x", 30)), int(landmark.get("y", 11)))
		var footprint := Vector2i(int(landmark.get("width", 8)), int(landmark.get("height", 6)))
		_draw_building(landmark_tile, footprint, origin, str(landmark.get("name", "LANDMARK")), str(landmark.get("type", "house")))
	for tile in flower_tiles:
		_draw_flower(tile, origin)
	for tile in rock_tiles:
		_draw_rock(tile, origin)
	for tile in lamp_tiles:
		_draw_lamp(tile, origin)
	for tile in tree_tiles:
		_draw_tree(tile, origin)
	var npc_index: int = 0
	for npc_value in area_npcs:
		if not npc_value is Dictionary:
			continue
		var npc: Dictionary = npc_value
		_draw_character(Vector2i(int(npc.get("x", 28)), int(npc.get("y", 21))), origin, false, npc_index)
		npc_index += 1


func _draw_ground(tile: Vector2i, origin: Vector2) -> void:
	var rect: Rect2 = _world_rect(tile, origin)
	if _is_water(tile):
		draw_rect(rect, _palette_color("water"))
		var wave_shift: float = float((tile.x * 7 + tile.y * 11) % 13)
		draw_rect(Rect2(rect.position + Vector2(4 + wave_shift * 0.25, 9), Vector2(12, 3)), _palette_color("water_light"))
		draw_rect(Rect2(rect.position + Vector2(14 - wave_shift * 0.2, 22), Vector2(10, 2)), _palette_color("water").darkened(0.18))
		return
	if _is_path(tile):
		var path_color: Color = _palette_color("path")
		draw_rect(rect, path_color)
		var grit: Color = _palette_color("path_detail")
		if (tile.x * 5 + tile.y * 3) % 4 == 0:
			draw_circle(rect.position + Vector2(7, 9), 2.0, grit)
			draw_circle(rect.position + Vector2(24, 24), 1.5, grit)
		if ground_style in ["metal", "pavement"]:
			draw_rect(Rect2(rect.position + Vector2(0, 2), Vector2(TILE, 2)), grit.lightened(0.12))
		return
	var ground: Color = _palette_color("ground_a") if (tile.x + tile.y) % 2 == 0 else _palette_color("ground_b")
	draw_rect(rect, ground)
	var detail: Color = ground.darkened(0.1)
	var seed: int = (tile.x * 29 + tile.y * 47) % 17
	if ground_style in ["metal", "pavement"]:
		draw_line(rect.position + Vector2(0, 31), rect.position + Vector2(32, 31), detail, 1.0)
		draw_line(rect.position + Vector2(31, 0), rect.position + Vector2(31, 32), detail, 1.0)
		if seed in [3, 9]:
			draw_circle(rect.position + Vector2(7, 7), 2.0, _palette_color("accent"))
	elif seed in [1, 6, 12]:
		draw_rect(Rect2(rect.position + Vector2(7, 10), Vector2(2, 5)), detail)
		draw_rect(Rect2(rect.position + Vector2(5, 12), Vector2(2, 2)), detail)
	elif seed in [3, 9]:
		draw_rect(Rect2(rect.position + Vector2(22, 23), Vector2(5, 2)), detail)


func _is_path(tile: Vector2i) -> bool:
	return _is_path_for(tile, landmark_doors)


func _is_path_for(tile: Vector2i, doors: Dictionary) -> bool:
	if tile.y >= 20 and tile.y <= 22:
		return true
	if tile.x >= 24 and tile.x <= 26:
		return true
	if tile.x >= 27 and tile.x <= 40 and tile.y >= 18 and tile.y <= 22:
		return true
	if tile.x >= 12 and tile.x <= 23 and tile.y >= 18 and tile.y <= 20:
		return true
	for door_value in doors.keys():
		if not door_value is Vector2i:
			continue
		var door: Vector2i = door_value
		var walkway_y: int = mini(WORLD_ROWS - 2, door.y + 1)
		if tile.y == walkway_y and tile.x >= mini(door.x, 25) and tile.x <= maxi(door.x, 25):
			return true
		if tile.x == door.x and tile.y >= mini(walkway_y, 21) and tile.y <= maxi(walkway_y, 21):
			return true
	return false


func _is_water(tile: Vector2i) -> bool:
	if not (_feature_enabled("water") or _feature_enabled("river") or _feature_enabled("pond") or _feature_enabled("coral")):
		return false
	if tile.x < 4 or tile.x > 13 or tile.y < 5 or tile.y > 11:
		return false
	return not ((tile.x == 4 or tile.x == 13) and (tile.y == 5 or tile.y == 11))


func _palette_color(role: String) -> Color:
	var palette: Dictionary = {
		"lush": {"ground_a": "#72c95a", "ground_b": "#7ed665", "path": "#f0c96f", "path_detail": "#cf9e52", "water": "#45a8df", "water_light": "#8ee8ed", "roof": "#ef6f61", "wall": "#ffe0a1", "accent": "#fff179", "leaf_dark": "#218c55", "leaf_light": "#47c96d", "flower": "#ff76a8"},
		"bright": {"ground_a": "#75c86c", "ground_b": "#86d67c", "path": "#e8c580", "path_detail": "#c89b5d", "water": "#42a9df", "water_light": "#9cebf1", "roof": "#ef6767", "wall": "#f8dfb1", "accent": "#ffe46b", "leaf_dark": "#278a57", "leaf_light": "#55c875", "flower": "#f576ba"},
		"desert": {"ground_a": "#efbd65", "ground_b": "#f5ca72", "path": "#d9964d", "path_detail": "#b9703b", "water": "#36a6c9", "water_light": "#8be3dc", "roof": "#d85d47", "wall": "#f2d39b", "accent": "#ffd96a", "leaf_dark": "#3d9258", "leaf_light": "#69bc60", "flower": "#f05d87"},
		"ice": {"ground_a": "#c8eff1", "ground_b": "#ddf7f4", "path": "#9fc8d3", "path_detail": "#74aab9", "water": "#428dd0", "water_light": "#9cecff", "roof": "#755fd4", "wall": "#e9f6f4", "accent": "#76f3ee", "leaf_dark": "#357a91", "leaf_light": "#63b6bd", "flower": "#d887e8"},
		"urban": {"ground_a": "#7ca46d", "ground_b": "#88b477", "path": "#9aa3a7", "path_detail": "#747e84", "water": "#3f8fb2", "water_light": "#76cfda", "roof": "#e36355", "wall": "#d8d0b9", "accent": "#ffcf57", "leaf_dark": "#276c4c", "leaf_light": "#4da66b", "flower": "#ef779d"},
		"neon": {"ground_a": "#384f54", "ground_b": "#425d60", "path": "#58656d", "path_detail": "#29d9c2", "water": "#256fa4", "water_light": "#49e5d1", "roof": "#7d4fd4", "wall": "#465b69", "accent": "#f36bdc", "leaf_dark": "#17795c", "leaf_light": "#29c983", "flower": "#ff67d3"},
		"cosmic": {"ground_a": "#313754", "ground_b": "#394263", "path": "#59647c", "path_detail": "#6ce5e0", "water": "#426fc4", "water_light": "#82e9ff", "roof": "#804cce", "wall": "#6f7895", "accent": "#f5dc66", "leaf_dark": "#257b72", "leaf_light": "#42d1ae", "flower": "#f46fe2"},
		"ocean": {"ground_a": "#58c6aa", "ground_b": "#64d3b2", "path": "#f2d385", "path_detail": "#cca95d", "water": "#258ed0", "water_light": "#75e3ee", "roof": "#ef7258", "wall": "#f2e0b1", "accent": "#fff073", "leaf_dark": "#147d61", "leaf_light": "#39b982", "flower": "#ff807c"},
		"volcanic": {"ground_a": "#5a4b4b", "ground_b": "#665454", "path": "#77615b", "path_detail": "#e85f3f", "water": "#e64f38", "water_light": "#ffb34d", "roof": "#702f3d", "wall": "#a47b68", "accent": "#ffca4b", "leaf_dark": "#46533e", "leaf_light": "#718056", "flower": "#ff754e"},
	}
	var selected: Dictionary = palette.get(area_palette, palette["lush"])
	return Color(str(selected.get(role, "#ffffff")))


func _draw_building(top_left: Vector2i, footprint: Vector2i, origin: Vector2, sign_text: String, landmark_type: String = "house") -> void:
	var pos: Vector2 = origin + Vector2(top_left) * TILE
	var building_size := Vector2(float(footprint.x) * TILE, float(footprint.y) * TILE)
	var roof_color := _palette_color("roof")
	var roof_light: Color = roof_color.lightened(0.18)
	var wall_color := _palette_color("wall")
	draw_rect(Rect2(pos + Vector2(3, 6), building_size - Vector2(6, 6)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(7, 46), building_size - Vector2(14, 53)), wall_color)
	draw_rect(Rect2(pos, Vector2(building_size.x, 52)), roof_color)
	draw_rect(Rect2(pos + Vector2(6, 6), Vector2(building_size.x - 12, 8)), roof_light)
	for x in range(16, int(building_size.x) - 12, 32):
		draw_rect(Rect2(pos + Vector2(x, 22), Vector2(18, 5)), roof_light.darkened(0.15))
	for x in range(26, int(building_size.x) - 30, 62):
		var window_color := Color("#73e0cb") if tech_world else Color("#9bc2b0")
		draw_rect(Rect2(pos + Vector2(x, 72), Vector2(28, 24)), OUTLINE)
		draw_rect(Rect2(pos + Vector2(x + 3, 75), Vector2(22, 18)), window_color)
	var door_x: float = building_size.x * 0.5 - 15.0
	draw_rect(Rect2(pos + Vector2(door_x, building_size.y - 42), Vector2(30, 42)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(door_x + 4, building_size.y - 38), Vector2(22, 38)), Color("#d1b45f") if tech_world else Color("#704838"))
	if tech_world:
		draw_rect(Rect2(pos + Vector2(door_x + 8, building_size.y - 31), Vector2(14, 3)), Color("#75e3d4"))
	var sign_width: float = minf(building_size.x - 50.0, float(sign_text.length()) * 11.0 + 22.0)
	draw_rect(Rect2(pos + Vector2(building_size.x * 0.5 - sign_width * 0.5, 48), Vector2(sign_width, 26)), OUTLINE)
	draw_string(ThemeDB.fallback_font, pos + Vector2(building_size.x * 0.5 - sign_width * 0.5 + 10, 67), sign_text.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, sign_width - 20.0, 13, _palette_color("accent"))
	var emblem_center := pos + Vector2(building_size.x - 30, 32)
	draw_circle(emblem_center, 13.0, OUTLINE)
	draw_circle(emblem_center, 9.0, _palette_color("accent"))
	var emblem: String = "✦" if landmark_type in ["starport", "hangar", "station"] else "●"
	draw_string(ThemeDB.fallback_font, emblem_center + Vector2(-5, 5), emblem, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, OUTLINE)


func _draw_tree(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	draw_circle(pos + Vector2(16, 29), 9.0, Color(0.06, 0.12, 0.1, 0.26))
	draw_rect(Rect2(pos + Vector2(13, 17), Vector2(7, 15)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(15, 18), Vector2(4, 14)), Color("#8a5638"))
	var leaf_dark: Color = _palette_color("leaf_dark")
	var leaf_light: Color = _palette_color("leaf_light")
	if _feature_enabled("snow_pines"):
		draw_colored_polygon(PackedVector2Array([pos + Vector2(16, 1), pos + Vector2(3, 22), pos + Vector2(29, 22)]), OUTLINE)
		draw_colored_polygon(PackedVector2Array([pos + Vector2(16, 4), pos + Vector2(6, 20), pos + Vector2(26, 20)]), leaf_dark)
		draw_colored_polygon(PackedVector2Array([pos + Vector2(16, 5), pos + Vector2(11, 13), pos + Vector2(22, 13)]), Color("#eefcfa"))
		return
	draw_circle(pos + Vector2(10, 14), 9.0, OUTLINE)
	draw_circle(pos + Vector2(22, 13), 10.0, OUTLINE)
	draw_circle(pos + Vector2(16, 8), 10.0, OUTLINE)
	draw_circle(pos + Vector2(10, 14), 6.5, leaf_dark)
	draw_circle(pos + Vector2(22, 13), 7.5, leaf_dark)
	draw_circle(pos + Vector2(16, 8), 7.5, leaf_light)
	draw_circle(pos + Vector2(13, 7), 2.5, leaf_light.lightened(0.25))


func _draw_rock(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	draw_circle(pos + Vector2(16, 27), 10.0, Color(0.06, 0.1, 0.1, 0.2))
	if _feature_enabled("cactus"):
		draw_rect(Rect2(pos + Vector2(12, 5), Vector2(10, 25)), OUTLINE)
		draw_rect(Rect2(pos + Vector2(15, 7), Vector2(5, 22)), _palette_color("leaf_light"))
		draw_rect(Rect2(pos + Vector2(6, 13), Vector2(10, 7)), OUTLINE)
		draw_rect(Rect2(pos + Vector2(8, 14), Vector2(7, 4)), _palette_color("leaf_light"))
		draw_circle(pos + Vector2(17, 7), 5.0, _palette_color("leaf_light"))
		return
	if _feature_enabled("crystals"):
		draw_colored_polygon(PackedVector2Array([pos + Vector2(5, 27), pos + Vector2(11, 8), pos + Vector2(17, 27)]), OUTLINE)
		draw_colored_polygon(PackedVector2Array([pos + Vector2(8, 25), pos + Vector2(11, 11), pos + Vector2(14, 25)]), _palette_color("accent"))
		draw_colored_polygon(PackedVector2Array([pos + Vector2(13, 28), pos + Vector2(22, 5), pos + Vector2(28, 28)]), OUTLINE)
		draw_colored_polygon(PackedVector2Array([pos + Vector2(17, 26), pos + Vector2(22, 9), pos + Vector2(25, 26)]), _palette_color("water_light"))
		return
	if _feature_enabled("metal_crates"):
		draw_rect(Rect2(pos + Vector2(5, 8), Vector2(24, 22)), OUTLINE)
		draw_rect(Rect2(pos + Vector2(8, 11), Vector2(18, 16)), _palette_color("wall"))
		draw_line(pos + Vector2(9, 12), pos + Vector2(25, 26), _palette_color("accent"), 3.0)
		draw_line(pos + Vector2(25, 12), pos + Vector2(9, 26), _palette_color("accent"), 3.0)
		return
	draw_circle(pos + Vector2(16, 21), 11.0, OUTLINE)
	draw_circle(pos + Vector2(16, 20), 8.0, Color("#87969a"))
	draw_circle(pos + Vector2(13, 16), 3.0, Color("#bbc5c2"))


func _draw_flower(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	var bloom: Color = _palette_color("flower")
	draw_rect(Rect2(pos + Vector2(15, 15), Vector2(2, 9)), Color("#315b3c"))
	draw_circle(pos + Vector2(12, 13), 4.0, bloom)
	draw_circle(pos + Vector2(20, 13), 4.0, bloom)
	draw_circle(pos + Vector2(16, 9), 4.0, bloom.lightened(0.15))
	draw_circle(pos + Vector2(16, 14), 3.0, _palette_color("accent"))


func _draw_lamp(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	draw_rect(Rect2(pos + Vector2(14, 10), Vector2(4, 22)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(9, 7), Vector2(14, 8)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(11, 9), Vector2(10, 4)), Color("#82ebd6") if tech_world else Color("#f2d36b"))


func _draw_character(tile: Vector2i, origin: Vector2, is_player: bool, variant: int = 0) -> void:
	var world_position: Vector2 = player_visual if is_player else Vector2(tile)
	var pos: Vector2 = origin + world_position * TILE
	var npc_colors: Array[Color] = [Color("#e9576f"), Color("#4e8ee8"), Color("#a864d8"), Color("#e89a45")]
	var npc_hair_colors: Array[Color] = [Color("#593b34"), Color("#29364f"), Color("#70484d"), Color("#d6b058")]
	var npc_skin_colors: Array[Color] = [Color("#e2aa78"), Color("#bd7b58"), Color("#f0c498"), Color("#8f5d4a")]
	var body_color: Color = Color("#35a6d8") if is_player else npc_colors[variant % npc_colors.size()]
	var body_light: Color = body_color.lightened(0.24)
	var hair_color: Color = _player_hair_color() if is_player else npc_hair_colors[variant % npc_hair_colors.size()]
	var skin_color: Color = npc_skin_colors[variant % npc_skin_colors.size()]
	draw_circle(pos + Vector2(16, 28), 10.0, Color(0.05, 0.1, 0.08, 0.35))
	var leg_shift: int = 2 if is_player and walk_frame == 1 else 0
	draw_rect(Rect2(pos + Vector2(10 - leg_shift, 22), Vector2(5, 7)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(18 + leg_shift, 22), Vector2(5, 7)), OUTLINE)
	draw_circle(pos + Vector2(16, 19), 10.0, OUTLINE)
	draw_circle(pos + Vector2(16, 19), 7.0, body_color)
	draw_rect(Rect2(pos + Vector2(10, 13), Vector2(5, 8)), body_light)
	draw_circle(pos + Vector2(17, 9), 9.0, OUTLINE)
	draw_circle(pos + Vector2(17, 9), 6.0, skin_color)
	if facing.y < 0 and is_player:
		draw_circle(pos + Vector2(17, 8), 7.0, hair_color)
	else:
		draw_rect(Rect2(pos + Vector2(11, 3), Vector2(12, 5)), hair_color)
		draw_circle(pos + Vector2(13, 7), 4.0, hair_color)
		if not (is_player and facing.y < 0):
			draw_circle(pos + Vector2(15, 10), 1.5, OUTLINE)
			draw_circle(pos + Vector2(20, 10), 1.5, OUTLINE)
			draw_rect(Rect2(pos + Vector2(16, 13), Vector2(4, 1)), Color("#8f4d54"))
	if not is_player:
		draw_circle(pos + Vector2(28, 4), 5.0, OUTLINE)
		draw_circle(pos + Vector2(28, 4), 3.0, _palette_color("accent"))


func _player_hair_color() -> Color:
	var player: Dictionary = game_state.get("player", {}) if game_state.get("player") is Dictionary else {}
	var appearance: String = str(player.get("appearance", "")).to_lower()
	if appearance.contains("black hair"):
		return Color("#252936")
	if appearance.contains("blond") or appearance.contains("blonde") or appearance.contains("gold hair"):
		return Color("#e4ca68")
	if appearance.contains("red hair"):
		return Color("#a94f3f")
	if appearance.contains("brown hair"):
		return Color("#684938")
	return Color("#c6ccd0")


func _unhandled_input(event: InputEvent) -> void:
	if not visible or busy or moving or not event is InputEventKey:
		return
	var key_event := event as InputEventKey
	if not key_event.pressed or key_event.echo:
		return
	if mode == "explore":
		if character_panel.visible:
			if key_event.keycode in [KEY_ESCAPE, KEY_C]:
				_toggle_character_panel()
			return
		match key_event.keycode:
			KEY_E, KEY_SPACE:
				if dialogue_panel.visible and not dialogue_choices.visible:
					_hide_dialogue()
				else:
					_interact()
			KEY_ESCAPE:
				_hide_dialogue()
			KEY_C:
				_toggle_character_panel()
	else:
		if key_event.keycode == KEY_ESCAPE:
			action_mode = ""
			chosen_ability.clear()
			_set_message("Choose a tactical command.")
			queue_redraw()


func _move_player(direction: Vector2i) -> void:
	facing = direction
	var destination: Vector2i = player_tile + direction
	var destination_coord: Vector2i = _area_coord_from_world_tile(destination)
	if destination_coord != area_coord:
		pending_step_direction = direction
		_request_world_area(_direction_name(direction))
		return
	_begin_player_step(direction)


func _direction_name(direction: Vector2i) -> String:
	if direction.x < 0:
		return "west"
	if direction.x > 0:
		return "east"
	if direction.y < 0:
		return "north"
	return "south"


func _begin_player_step(direction: Vector2i) -> void:
	var destination: Vector2i = player_tile + direction
	var local_destination: Vector2i = _local_tile(destination)
	if _is_blocked(local_destination) or not _npc_at(local_destination).is_empty():
		queue_redraw()
		return
	player_tile = destination
	moving = true
	walk_frame = 1 - walk_frame
	var tween := create_tween()
	tween.set_trans(Tween.TRANS_LINEAR)
	tween.tween_property(self, "player_visual", Vector2(player_tile), 0.11)
	tween.tween_callback(_finish_step)


func _finish_step() -> void:
	moving = false
	queue_redraw()


func _is_blocked(tile: Vector2i) -> bool:
	return blocked.has(tile)


func _npc_at(tile: Vector2i) -> Dictionary:
	for npc_value in area_npcs:
		if not npc_value is Dictionary:
			continue
		var npc: Dictionary = npc_value
		if Vector2i(int(npc.get("x", -100)), int(npc.get("y", -100))) == tile:
			return npc
	return {}


func _nearby_npc() -> Dictionary:
	var local_player: Vector2i = _local_tile(player_tile)
	var front_npc: Dictionary = _npc_at(local_player + facing)
	if not front_npc.is_empty():
		return front_npc
	for npc_value in area_npcs:
		if not npc_value is Dictionary:
			continue
		var npc: Dictionary = npc_value
		var tile := Vector2i(int(npc.get("x", -100)), int(npc.get("y", -100)))
		if _tile_distance(local_player, tile) <= 1:
			return npc
	return {}


func _request_world_area(direction: String) -> void:
	if busy:
		return
	pending_exit_direction = direction
	_post("/world/area/generate", {"direction": direction}, "world_area", false)


func _interact() -> void:
	if busy:
		return
	var local_player: Vector2i = _local_tile(player_tile)
	var front: Vector2i = local_player + facing
	var npc: Dictionary = _nearby_npc()
	if not npc.is_empty():
		var npc_name: String = str(npc.get("name", "the nearby person"))
		var npc_role: String = str(npc.get("role", "local"))
		_request_story("I speak with %s, a %s in %s. Give their short opening line, then three setting-appropriate things I could say or do next. Do not reveal hidden lore or distant events." % [npc_name, npc_role, str(current_area.get("name", "this area"))])
		return
	if landmark_doors.has(front):
		var landmark: Dictionary = landmark_doors[front]
		var prompt: String = str(landmark.get("interaction_prompt", "I inspect and enter this place if possible."))
		_request_story("%s Describe only what is immediately visible, then give three sensible things I can do. Keep secrets and distant locations hidden." % prompt)
		return
	if front in tree_tiles or front in rock_tiles or front in flower_tiles or front in lamp_tiles:
		_request_story("I inspect the object directly in front of me in %s. Describe only what I can immediately notice, then give three sensible interactions that fit this world's rules." % str(current_area.get("name", "this area")))
		return
	_set_message("Nothing nearby demands your attention. Explore the paths and speak to people you meet.")


func _tile_distance(a: Vector2i, b: Vector2i) -> int:
	return absi(a.x - b.x) + absi(a.y - b.y)


func _request_story(action_text: String) -> void:
	_post("/action", {"action": action_text}, "story")


func _choose_suggestion(index: int) -> void:
	if index < 0 or index >= suggestion_buttons.size():
		return
	var action_text: String = str(suggestion_buttons[index].get_meta("action_text", "")).strip_edges()
	if not action_text.is_empty():
		_request_story(action_text)


func _submit_custom_action(text: String) -> void:
	var clean: String = text.strip_edges()
	if clean.is_empty() or busy:
		return
	custom_action_input.clear()
	_request_story(clean)


func _submit_custom_action_from_button() -> void:
	_submit_custom_action(custom_action_input.text)


func _start_training_battle() -> void:
	_post("/prototype/battle/start", {}, "battle_start")


func _hide_dialogue() -> void:
	dialogue_panel.visible = false
	dialogue_choices.visible = false
	custom_action_input.release_focus()


func _battle_origin() -> Vector2:
	return Vector2(28, 108)


func _battle_tile_size() -> float:
	return floor(minf((size.x - 430.0) / float(BATTLE_COLS), (size.y - 300.0) / float(BATTLE_ROWS)))


func _draw_battle() -> void:
	var origin: Vector2 = _battle_origin()
	var tile_size: float = _battle_tile_size()
	var board_rect := Rect2(origin - Vector2(6, 6), Vector2(BATTLE_COLS, BATTLE_ROWS) * tile_size + Vector2(12, 12))
	draw_rect(board_rect, OUTLINE)
	for y in range(BATTLE_ROWS):
		for x in range(BATTLE_COLS):
			var rect := Rect2(origin + Vector2(x, y) * tile_size, Vector2(tile_size, tile_size))
			var color := Color("#405548") if (x + y) % 2 == 0 else Color("#35483d")
			draw_rect(rect, color)
			draw_rect(rect, Color("#5d7464"), false, 1.0)
	var player: Dictionary = _player_combatant()
	if action_mode == "move" and not player.is_empty():
		var remaining: int = maxi(0, int(player.get("movement", 0)) - int(player.get("movement_used", 0)))
		var start := _actor_tile(player)
		for y in range(BATTLE_ROWS):
			for x in range(BATTLE_COLS):
				var candidate := Vector2i(x, y)
				var distance: int = absi(candidate.x - start.x) + absi(candidate.y - start.y)
				if distance <= remaining and not _battle_tile_occupied(candidate):
					draw_rect(Rect2(origin + Vector2(candidate) * tile_size, Vector2(tile_size, tile_size)).grow(-2.0), MOVE_COLOR)
	for actor_value in _combatants():
		if not actor_value is Dictionary:
			continue
		var actor: Dictionary = actor_value
		if int(actor.get("hp", 0)) <= 0:
			continue
		var tile: Vector2i = _actor_tile(actor)
		if tile.x < 0 or tile.x >= BATTLE_COLS or tile.y < 0 or tile.y >= BATTLE_ROWS:
			continue
		var rect: Rect2 = Rect2(origin + Vector2(tile) * tile_size, Vector2(tile_size, tile_size)).grow(-tile_size * 0.12)
		var team_color: Color = ALLY_COLOR if str(actor.get("team", "enemy")) == "player" else ENEMY_COLOR
		draw_rect(rect, OUTLINE)
		draw_rect(rect.grow(-3.0), team_color)
		var short_name: String = str(actor.get("name", "Actor")).left(8)
		draw_string(ThemeDB.fallback_font, rect.position + Vector2(4, tile_size * 0.45), short_name, HORIZONTAL_ALIGNMENT_LEFT, tile_size - 8.0, int(maxf(10.0, tile_size * 0.2)), OUTLINE)
		var hp_text := "%d/%d" % [int(actor.get("hp", 0)), int(actor.get("max_hp", 0))]
		draw_string(ThemeDB.fallback_font, rect.position + Vector2(4, tile_size * 0.78), hp_text, HORIZONTAL_ALIGNMENT_LEFT, tile_size - 8.0, int(maxf(10.0, tile_size * 0.18)), OUTLINE)
		if str(actor.get("name", "")) == str(_combat().get("current_actor", "")):
			draw_rect(rect.grow(3.0), PLAYER_COLOR, false, 3.0)
	if action_mode in ["attack", "ability"]:
		draw_string(ThemeDB.fallback_font, origin + Vector2(0, -12), "SELECT A TARGET SQUARE", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, PLAYER_COLOR)


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
	if _can_act():
		_post("/combat/defend", {}, "combat")


func _end_turn() -> void:
	if _can_act():
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


func _post(path: String, body: Dictionary, next_request_mode: String, show_thinking: bool = true) -> void:
	if busy:
		return
	busy = true
	request_mode = next_request_mode
	action_mode = ""
	chosen_ability.clear()
	_set_buttons_disabled(true)
	if show_thinking:
		_set_message("Thinking...")
	else:
		hint_label.text = "GENERATING THE NEXT AREA..."
	var headers := PackedStringArray(["Content-Type: application/json"])
	var error: int = http.request(API_BASE + path, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	if error != OK:
		busy = false
		_set_buttons_disabled(false)
		_request_failed("Could not reach the local game server. Make sure python -m backend.api is running.")


func _request_failed(message: String) -> void:
	if request_mode == "world_area":
		pending_step_direction = Vector2i.ZERO
		pending_exit_direction = ""
		_update_header()
		hint_label.text = "AREA GENERATION FAILED — TRY THE EDGE AGAIN"
		request_mode = ""
		return
	_set_message(message)


func _on_request_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	busy = false
	_set_buttons_disabled(false)
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if not parsed is Dictionary:
		_request_failed("The game server returned an unreadable response.")
		return
	var payload: Dictionary = parsed
	if response_code < 200 or response_code >= 300 or not bool(payload.get("ok", true)):
		_request_failed(str(payload.get("error", "The action could not be completed.")))
		return
	if payload.get("state") is Dictionary:
		game_state = payload.get("state", {})
	if request_mode == "world_area":
		if not payload.get("area") is Dictionary:
			_request_failed("The generated area was missing from the server response.")
			return
		_apply_area(payload.get("area", {}))
		pending_exit_direction = ""
		_update_main_controller(payload)
		_refresh_character_sheet()
		_update_header()
		_hide_dialogue()
		var crossing_step: Vector2i = pending_step_direction
		pending_step_direction = Vector2i.ZERO
		request_mode = ""
		if crossing_step != Vector2i.ZERO:
			_begin_player_step(crossing_step)
		queue_redraw()
		return
	var combat: Dictionary = _combat()
	var was_battle: bool = mode == "battle" or request_mode in ["battle_start", "combat"]
	if bool(combat.get("active", false)):
		mode = "battle"
	elif was_battle:
		mode = "explore"
	_update_world_theme()
	_update_main_controller(payload)
	_refresh_character_sheet()
	_update_header()
	_refresh_mode_interface()
	var narration: String = str(payload.get("narration", "")).strip_edges()
	if narration.is_empty():
		narration = "Action complete."
	_set_message(narration, payload.get("suggested_actions", []))
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
		hint_label.text = "CLICK A COMMAND, THEN CHOOSE A SQUARE"
	else:
		var world: Dictionary = game_state.get("world_profile", {}) if game_state.get("world_profile") is Dictionary else {}
		var campaign: Dictionary = game_state.get("campaign", {}) if game_state.get("campaign") is Dictionary else {}
		var world_name: String = str(world.get("name", campaign.get("name", "THE SHATTERED REALMS")))
		var location: String = str(game_state.get("current_location", "Frontier Outpost"))
		var biome: String = str(current_area.get("biome", "")).strip_edges()
		title_label.text = str(current_area.get("name", location)).to_upper()
		subtitle_label.text = world_name
		if not biome.is_empty():
			subtitle_label.text += "  •  " + biome.capitalize()
		var links: Array = current_area.get("travel_links", []) if current_area.get("travel_links") is Array else []
		if not links.is_empty() and links[0] is Dictionary:
			var first_link: Dictionary = links[0]
			subtitle_label.text += "  •  %s travel nearby (coming later)" % str(first_link.get("mode", "Transport")).capitalize()
		hint_label.text = "MOVE  WASD / ARROWS     INTERACT  E / SPACE     CHARACTER  C"


func _toggle_character_panel() -> void:
	character_panel.visible = not character_panel.visible
	character_button.text = "CLOSE SHEET" if character_panel.visible else "CHARACTER"
	if character_panel.visible:
		_refresh_character_sheet()


func _set_character_section(section: String) -> void:
	if section not in ["stats", "inventory", "equipment", "abilities"]:
		return
	character_section = section
	_refresh_character_sheet()


func _refresh_character_sheet() -> void:
	if character_text == null:
		return
	var player: Dictionary = game_state.get("player", {}) if game_state.get("player") is Dictionary else {}
	var stats: Dictionary = player.get("stats", {}) if player.get("stats") is Dictionary else {}
	for button in character_tab_buttons:
		var is_selected: bool = str(button.get_meta("section", "")) == character_section
		button.disabled = false
		button.text = ("• " if is_selected else "") + str(button.get_meta("base_label", button.text))
	var lines: Array[String] = []
	lines.append("[font_size=24][b]%s[/b][/font_size]" % _sheet_safe(str(player.get("name", "Traveler"))))
	lines.append("%s  •  Level %d" % [_sheet_safe(str(player.get("class", "Unassigned"))), int(player.get("level", 1))])
	lines.append("")
	match character_section:
		"inventory":
			lines.append("[b]INVENTORY[/b]")
			lines.append("Money: " + _sheet_money(player))
			lines.append("")
			var inventory: Array = player.get("inventory", []) if player.get("inventory") is Array else []
			if inventory.is_empty():
				lines.append("Inventory is empty.")
			else:
				for item_value in inventory:
					if not item_value is Dictionary:
						continue
					var item: Dictionary = item_value
					var quantity: int = maxi(1, int(item.get("quantity", 1)))
					var rarity: String = str(item.get("rarity", "common")).capitalize()
					var quantity_text: String = " x%d" % quantity if quantity > 1 else ""
					lines.append("[b]• %s%s[/b]  [%s]" % [_sheet_safe(str(item.get("name", "Item"))), quantity_text, rarity])
					var description: String = str(item.get("description", "")).strip_edges()
					if not description.is_empty():
						lines.append("  " + _sheet_safe(description))
		"equipment":
			lines.append("[b]EQUIPMENT & ARMOR[/b]")
			lines.append("Armor %d/%d  •  Weight %d  •  Movement %d" % [int(player.get("armor", 0)), int(player.get("max_armor", 0)), int(player.get("armor_weight", 0)), int(player.get("movement", 0))])
			var weapon = player.get("equipped_weapon", {})
			if weapon is Dictionary and not weapon.is_empty():
				lines.append("Weapon: " + _sheet_safe(str(weapon.get("name", "Equipped weapon"))))
			elif not str(weapon).strip_edges().is_empty() and str(weapon) != "{}" and str(weapon) != "<null>":
				lines.append("Weapon: " + _sheet_safe(str(weapon)))
			else:
				lines.append("Weapon: None equipped")
			lines.append("Armor set: " + _sheet_safe(str(player.get("armor_set_name", "Mixed set"))))
			var equipped_armor: Dictionary = player.get("equipped_armor", {}) if player.get("equipped_armor") is Dictionary else {}
			for slot in ["helmet", "breastplate", "pants", "gloves", "boots"]:
				var piece: Dictionary = equipped_armor.get(slot, {}) if equipped_armor.get(slot) is Dictionary else {}
				if piece.is_empty():
					continue
				lines.append("[b]%s[/b]: %s" % [str(slot).capitalize(), _sheet_safe(str(piece.get("name", slot)))])
				lines.append("  Armor %d/%d  •  Weight %d" % [int(piece.get("armor_hp", 0)), int(piece.get("max_armor_hp", piece.get("armor_hp", 0))), int(piece.get("weight", 0))])
		"abilities":
			lines.append("[b]EQUIPPED ABILITIES[/b]")
			var abilities: Array = player.get("equipped_abilities", []) if player.get("equipped_abilities") is Array else []
			if abilities.is_empty():
				lines.append("None equipped")
			else:
				for ability_value in abilities:
					if not ability_value is Dictionary:
						continue
					lines.append("[b]• %s[/b] — Cost %d" % [_sheet_safe(str(ability_value.get("name", "Ability"))), int(ability_value.get("resource_cost", 0))])
					var ability_description: String = str(ability_value.get("description", "")).strip_edges()
					if not ability_description.is_empty():
						lines.append("  " + _sheet_safe(ability_description))
			var features: Array = player.get("features", []) if player.get("features") is Array else []
			if not features.is_empty():
				lines.append("")
				lines.append("[b]FEATURES[/b]")
				for feature in features:
					lines.append("• " + _sheet_safe(str(feature)))
		_:
			lines.append("[b]VITALS[/b]")
			lines.append("HP  %d / %d" % [int(player.get("hp", 0)), int(player.get("max_hp", 0))])
			lines.append("Armor  %d / %d  •  Weight %d" % [int(player.get("armor", 0)), int(player.get("max_armor", 0)), int(player.get("armor_weight", 0))])
			lines.append("%s  %d / %d" % [_sheet_safe(str(player.get("resource_name", "Resource"))), int(player.get("resource", player.get("mana", 0))), int(player.get("max_resource", player.get("max_mana", 0)))])
			lines.append("AC %d  •  Movement %d  •  Initiative %d" % [int(player.get("armor_class", 10)), int(player.get("movement", 0)), int(player.get("initiative_bonus", 0))])
			lines.append("XP %d/%d  •  SP %d  •  AP %d" % [int(player.get("xp_orbs", 0)), int(player.get("xp_to_next_level", 0)), int(player.get("skill_points_unspent", 0)), int(player.get("ability_points", 0))])
			lines.append("")
			lines.append("[b]CORE STATS[/b]")
			var stat_names: Array[String] = ["health", "resource", "strength", "dexterity", "agility", "constitution", "intelligence", "wisdom", "charisma", "speed", "defense", "luck", "magic"]
			for index in range(0, stat_names.size(), 2):
				var left_name: String = stat_names[index]
				var stat_line: String = "%s %d" % [left_name.capitalize(), int(stats.get(left_name, 0))]
				if index + 1 < stat_names.size():
					var right_name: String = stat_names[index + 1]
					stat_line += "     %s %d" % [right_name.capitalize(), int(stats.get(right_name, 0))]
				lines.append(stat_line)
	character_text.text = "\n".join(lines)
	character_text.scroll_to_line(0)


func _sheet_safe(value: String) -> String:
	return value.replace("[", "(").replace("]", ")")


func _sheet_money(player: Dictionary) -> String:
	var wallet: Dictionary = player.get("wallet", {}) if player.get("wallet") is Dictionary else {}
	if not wallet.is_empty():
		var amount: int = int(wallet.get("amount", 0))
		var symbol: String = str(wallet.get("symbol", ""))
		var currency_name: String = str(wallet.get("name", "currency"))
		if not symbol.is_empty() and bool(wallet.get("prefix", false)):
			return "%s%d" % [symbol, amount]
		if not symbol.is_empty():
			return "%d%s" % [amount, symbol]
		return "%d %s" % [amount, _sheet_safe(currency_name)]
	var currency: Dictionary = player.get("currency", {}) if player.get("currency") is Dictionary else {}
	var parts: Array[String] = []
	for key in currency.keys():
		var coin_amount: int = int(currency.get(key, 0))
		if coin_amount > 0:
			parts.append("%d %s" % [coin_amount, str(key)])
	return ", ".join(parts) if not parts.is_empty() else "0"


func _refresh_mode_interface() -> void:
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
	var abilities: Array = player.get("abilities", []) if player.get("abilities") is Array else []
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


func _set_message(text: String, suggested_actions = []) -> void:
	dialogue_panel.visible = true
	dialogue_label.text = text
	var actions: Array[String] = []
	if suggested_actions is Array:
		for item in suggested_actions:
			var action_text: String = ""
			if item is Dictionary:
				action_text = str(item.get("text", "")).strip_edges()
			else:
				action_text = str(item).strip_edges()
			if not action_text.is_empty():
				actions.append(action_text)
			if actions.size() == 3:
				break
	dialogue_choices.visible = not actions.is_empty()
	if actions.is_empty():
		return
	var defaults: Array[String] = ["Look around carefully", "Ask a question", "Step away"]
	while actions.size() < 3:
		actions.append(defaults[actions.size()])
	for index in range(suggestion_buttons.size()):
		var button: Button = suggestion_buttons[index]
		button.text = actions[index]
		button.set_meta("action_text", actions[index])
		button.visible = true


func _set_buttons_disabled(disabled: bool) -> void:
	for button in suggestion_buttons:
		button.disabled = disabled
	custom_action_button.disabled = disabled
	custom_action_input.editable = not disabled
	for child in battle_actions.get_children():
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
	var origin: Vector2 = _battle_origin()
	var tile_size: float = _battle_tile_size()
	var local_point: Vector2 = point - origin
	if local_point.x < 0.0 or local_point.y < 0.0:
		return Vector2i(-1, -1)
	var tile := Vector2i(int(floor(local_point.x / tile_size)), int(floor(local_point.y / tile_size)))
	if tile.x >= BATTLE_COLS or tile.y >= BATTLE_ROWS:
		return Vector2i(-1, -1)
	return tile
