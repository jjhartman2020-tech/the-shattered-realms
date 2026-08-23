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

var title_label: Label
var subtitle_label: Label
var hint_label: Label
var dialogue_panel: PanelContainer
var dialogue_label: RichTextLabel
var dialogue_choices: HBoxContainer
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


func _process(_delta: float) -> void:
	if moving:
		queue_redraw()


func show_from_payload(payload: Dictionary = {}) -> void:
	if payload.get("state") is Dictionary:
		game_state = payload.get("state", {})
	elif not payload.is_empty() and payload.get("player") is Dictionary:
		game_state = payload
	_update_world_theme()
	var combat: Dictionary = _combat()
	mode = "battle" if bool(combat.get("active", false)) else "explore"
	visible = true
	player_visual = Vector2(player_tile)
	_update_header()
	_refresh_mode_interface()
	var narration: String = str(payload.get("narration", "")).strip_edges()
	if not narration.is_empty():
		_set_message(narration)
	elif mode == "explore":
		_hide_dialogue()
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
	hint_label.position = Vector2(-500, 61)
	hint_label.size = Vector2(360, 24)
	hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hint_label.text = "MOVE  WASD / ARROWS     INTERACT  E / SPACE"
	hint_label.add_theme_font_size_override("font_size", 12)
	hint_label.add_theme_color_override("font_color", MUTED)
	add_child(hint_label)

	dialogue_panel = PanelContainer.new()
	dialogue_panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	dialogue_panel.offset_left = 72.0
	dialogue_panel.offset_top = -172.0
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
	dialogue_label.custom_minimum_size = Vector2(0, 70)
	dialogue_label.bbcode_enabled = true
	dialogue_label.fit_content = false
	dialogue_label.scroll_active = true
	dialogue_label.add_theme_font_size_override("normal_font_size", 17)
	dialogue_label.add_theme_color_override("default_color", INK)
	dialogue_stack.add_child(dialogue_label)
	dialogue_choices = HBoxContainer.new()
	dialogue_choices.alignment = BoxContainer.ALIGNMENT_CENTER
	dialogue_choices.add_theme_constant_override("separation", 10)
	dialogue_stack.add_child(dialogue_choices)
	dialogue_choices.add_child(_action_button("ASK ABOUT HERE", _ask_about_place, 190))
	dialogue_choices.add_child(_action_button("ASK FOR WORK", _ask_for_work, 170))
	dialogue_choices.add_child(_action_button("TRAIN", _start_training_battle, 130))
	dialogue_choices.add_child(_action_button("CLOSE", _hide_dialogue, 120))
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
	tree_tiles = [
		Vector2i(2, 3), Vector2i(3, 3), Vector2i(4, 3), Vector2i(14, 3), Vector2i(15, 3),
		Vector2i(2, 4), Vector2i(14, 4), Vector2i(42, 4), Vector2i(43, 4), Vector2i(44, 4),
		Vector2i(16, 5), Vector2i(24, 5), Vector2i(42, 5), Vector2i(45, 5),
		Vector2i(16, 6), Vector2i(24, 6), Vector2i(40, 7), Vector2i(41, 7), Vector2i(45, 7),
		Vector2i(3, 14), Vector2i(4, 14), Vector2i(7, 14), Vector2i(12, 15), Vector2i(13, 15),
		Vector2i(3, 16), Vector2i(44, 15), Vector2i(45, 15), Vector2i(5, 25), Vector2i(6, 25),
		Vector2i(9, 27), Vector2i(10, 27), Vector2i(15, 29), Vector2i(16, 29), Vector2i(38, 27),
		Vector2i(39, 27), Vector2i(43, 28), Vector2i(44, 28), Vector2i(45, 28),
	]
	rock_tiles = [Vector2i(14, 12), Vector2i(43, 11), Vector2i(8, 24), Vector2i(41, 25)]
	flower_tiles = [Vector2i(20, 15), Vector2i(22, 17), Vector2i(11, 19), Vector2i(39, 21), Vector2i(19, 25), Vector2i(29, 26)]
	lamp_tiles = [Vector2i(22, 19), Vector2i(28, 19), Vector2i(30, 22), Vector2i(38, 22)]
	blocked.clear()
	for x in range(WORLD_COLS):
		blocked[Vector2i(x, 0)] = true
		blocked[Vector2i(x, WORLD_ROWS - 1)] = true
	for y in range(WORLD_ROWS):
		blocked[Vector2i(0, y)] = true
		blocked[Vector2i(WORLD_COLS - 1, y)] = true
	for y in range(5, 12):
		for x in range(4, 14):
			if not ((x == 4 or x == 13) and (y == 5 or y == 11)):
				blocked[Vector2i(x, y)] = true
	for y in range(12, 19):
		for x in range(30, 39):
			blocked[Vector2i(x, y)] = true
	for y in range(6, 11):
		for x in range(15, 22):
			blocked[Vector2i(x, y)] = true
	for tile in tree_tiles:
		blocked[tile] = true
	for tile in rock_tiles:
		blocked[tile] = true


func _update_world_theme() -> void:
	var world_text: String = JSON.stringify(game_state.get("world_profile", {})).to_lower()
	tech_world = false
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
	var minimum_x: float = minf(0.0, size.x - float(WORLD_COLS) * TILE)
	var minimum_y: float = minf(0.0, size.y - float(WORLD_ROWS) * TILE)
	return Vector2(round(clampf(target.x, minimum_x, 0.0)), round(clampf(target.y, minimum_y, 0.0)))


func _world_rect(tile: Vector2i, origin: Vector2, grow: float = 0.0) -> Rect2:
	return Rect2(origin + Vector2(tile) * TILE, Vector2(TILE, TILE)).grow(grow)


func _draw_overworld() -> void:
	var origin: Vector2 = _camera_origin()
	var start_x: int = maxi(0, int(floor(-origin.x / TILE)) - 1)
	var start_y: int = maxi(0, int(floor(-origin.y / TILE)) - 1)
	var end_x: int = mini(WORLD_COLS, start_x + int(ceil(size.x / TILE)) + 3)
	var end_y: int = mini(WORLD_ROWS, start_y + int(ceil(size.y / TILE)) + 3)
	for y in range(start_y, end_y):
		for x in range(start_x, end_x):
			_draw_ground(Vector2i(x, y), origin)
	_draw_building(Vector2i(30, 12), Vector2i(9, 7), origin, "WAYPOINT")
	_draw_building(Vector2i(15, 6), Vector2i(7, 5), origin, "SUPPLY")
	for tile in flower_tiles:
		_draw_flower(tile, origin)
	for tile in rock_tiles:
		_draw_rock(tile, origin)
	for tile in lamp_tiles:
		_draw_lamp(tile, origin)
	for tile in tree_tiles:
		_draw_tree(tile, origin)
	_draw_character(npc_tile, origin, false)
	_draw_character(Vector2i.ZERO, origin, true)


func _draw_ground(tile: Vector2i, origin: Vector2) -> void:
	var rect: Rect2 = _world_rect(tile, origin)
	if _is_water(tile):
		draw_rect(rect, Color("#3f7480") if tech_world else Color("#4d8292"))
		var wave_shift: float = float((tile.x * 7 + tile.y * 11) % 13)
		draw_rect(Rect2(rect.position + Vector2(4 + wave_shift * 0.25, 9), Vector2(12, 2)), Color("#77a8a2"))
		draw_rect(Rect2(rect.position + Vector2(14 - wave_shift * 0.2, 22), Vector2(10, 2)), Color("#315d69"))
		return
	if _is_path(tile):
		var path_color := Color("#a9a06a") if tech_world else Color("#b6a36b")
		draw_rect(rect, path_color)
		var grit: Color = path_color.darkened(0.13)
		if (tile.x * 5 + tile.y * 3) % 4 == 0:
			draw_rect(Rect2(rect.position + Vector2(6, 8), Vector2(3, 2)), grit)
			draw_rect(Rect2(rect.position + Vector2(23, 24), Vector2(2, 2)), grit)
		if tech_world and tile.y in [20, 22]:
			draw_rect(Rect2(rect.position + Vector2(0, 1 if tile.y == 20 else 29), Vector2(TILE, 2)), Color("#7c8362"))
		return
	var grass := Color("#668d52") if (tile.x + tile.y) % 2 == 0 else Color("#6f9658")
	if tech_world:
		grass = Color("#557a55") if (tile.x + tile.y) % 2 == 0 else Color("#5e835d")
	draw_rect(rect, grass)
	var detail: Color = grass.darkened(0.12)
	var seed: int = (tile.x * 29 + tile.y * 47) % 17
	if seed in [1, 6, 12]:
		draw_rect(Rect2(rect.position + Vector2(7, 10), Vector2(2, 5)), detail)
		draw_rect(Rect2(rect.position + Vector2(5, 12), Vector2(2, 2)), detail)
	if seed in [3, 9]:
		draw_rect(Rect2(rect.position + Vector2(22, 23), Vector2(5, 2)), detail)


func _is_path(tile: Vector2i) -> bool:
	if tile.y >= 20 and tile.y <= 22:
		return true
	if tile.x >= 24 and tile.x <= 26 and tile.y >= 10:
		return true
	if tile.x >= 27 and tile.x <= 40 and tile.y >= 18 and tile.y <= 22:
		return true
	if tile.x >= 12 and tile.x <= 23 and tile.y >= 18 and tile.y <= 20:
		return true
	return false


func _is_water(tile: Vector2i) -> bool:
	if tile.x < 4 or tile.x > 13 or tile.y < 5 or tile.y > 11:
		return false
	return not ((tile.x == 4 or tile.x == 13) and (tile.y == 5 or tile.y == 11))


func _draw_building(top_left: Vector2i, footprint: Vector2i, origin: Vector2, sign_text: String) -> void:
	var pos: Vector2 = origin + Vector2(top_left) * TILE
	var building_size := Vector2(float(footprint.x) * TILE, float(footprint.y) * TILE)
	var roof_color := Color("#35495c") if tech_world else Color("#765049")
	var roof_light := Color("#49647b") if tech_world else Color("#92675a")
	var wall_color := Color("#536d70") if tech_world else Color("#c09b70")
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
	draw_string(ThemeDB.fallback_font, pos + Vector2(building_size.x * 0.5 - sign_width * 0.5 + 10, 67), sign_text, HORIZONTAL_ALIGNMENT_LEFT, sign_width - 20.0, 13, Color("#7ff0d8") if tech_world else INK)


func _draw_tree(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	draw_rect(Rect2(pos + Vector2(13, 19), Vector2(7, 13)), Color("#5b4531"))
	draw_rect(Rect2(pos + Vector2(7, 6), Vector2(19, 20)), OUTLINE)
	var leaf_dark := Color("#1d4d3c") if tech_world else Color("#28563a")
	var leaf_light := Color("#34705a") if tech_world else Color("#3f7445")
	draw_rect(Rect2(pos + Vector2(9, 4), Vector2(15, 5)), leaf_dark)
	draw_rect(Rect2(pos + Vector2(5, 9), Vector2(23, 13)), leaf_dark)
	draw_rect(Rect2(pos + Vector2(9, 8), Vector2(11, 8)), leaf_light)
	draw_rect(Rect2(pos + Vector2(22, 12), Vector2(4, 6)), leaf_light)


func _draw_rock(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	draw_rect(Rect2(pos + Vector2(7, 14), Vector2(20, 13)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(10, 11), Vector2(14, 13)), Color("#6f8179"))
	draw_rect(Rect2(pos + Vector2(12, 13), Vector2(7, 3)), Color("#93a094"))


func _draw_flower(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	var bloom := Color("#db7479") if tech_world else Color("#f0cc6b")
	draw_rect(Rect2(pos + Vector2(15, 15), Vector2(2, 9)), Color("#315b3c"))
	draw_rect(Rect2(pos + Vector2(11, 11), Vector2(5, 5)), bloom)
	draw_rect(Rect2(pos + Vector2(17, 11), Vector2(5, 5)), bloom)
	draw_rect(Rect2(pos + Vector2(14, 9), Vector2(5, 5)), bloom)


func _draw_lamp(tile: Vector2i, origin: Vector2) -> void:
	var pos: Vector2 = origin + Vector2(tile) * TILE
	draw_rect(Rect2(pos + Vector2(14, 10), Vector2(4, 22)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(9, 7), Vector2(14, 8)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(11, 9), Vector2(10, 4)), Color("#82ebd6") if tech_world else Color("#f2d36b"))


func _draw_character(tile: Vector2i, origin: Vector2, is_player: bool) -> void:
	var world_position: Vector2 = player_visual if is_player else Vector2(tile)
	var pos: Vector2 = origin + world_position * TILE
	var body_color := Color("#304f65") if is_player else Color("#a44f4b")
	var body_light := Color("#4f7790") if is_player else Color("#cf6b5e")
	var hair_color := _player_hair_color() if is_player else Color("#50352d")
	var skin_color := Color("#d8a775")
	draw_rect(Rect2(pos + Vector2(7, 26), Vector2(18, 5)), Color(0.05, 0.1, 0.08, 0.45))
	var leg_shift: int = 2 if is_player and walk_frame == 1 else 0
	draw_rect(Rect2(pos + Vector2(10 - leg_shift, 22), Vector2(5, 7)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(18 + leg_shift, 22), Vector2(5, 7)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(7, 12), Vector2(19, 13)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(9, 13), Vector2(15, 11)), body_color)
	draw_rect(Rect2(pos + Vector2(10, 13), Vector2(5, 8)), body_light)
	draw_rect(Rect2(pos + Vector2(9, 3), Vector2(16, 12)), OUTLINE)
	draw_rect(Rect2(pos + Vector2(11, 5), Vector2(12, 9)), skin_color)
	if facing.y < 0 and is_player:
		draw_rect(Rect2(pos + Vector2(10, 4), Vector2(14, 9)), hair_color)
	else:
		draw_rect(Rect2(pos + Vector2(10, 3), Vector2(14, 5)), hair_color)
		draw_rect(Rect2(pos + Vector2(10, 7), Vector2(3, 5)), hair_color)
		if not (is_player and facing.y < 0):
			draw_rect(Rect2(pos + Vector2(15, 9), Vector2(2, 2)), Color("#5d2b31") if is_player else OUTLINE)
			draw_rect(Rect2(pos + Vector2(20, 9), Vector2(2, 2)), Color("#5d2b31") if is_player else OUTLINE)
	if not is_player:
		draw_rect(Rect2(pos + Vector2(27, 1), Vector2(4, 12)), OUTLINE)
		draw_rect(Rect2(pos + Vector2(28, 2), Vector2(2, 9)), Color("#f1d66c"))


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
				if dialogue_panel.visible and not dialogue_choices.visible:
					_hide_dialogue()
				else:
					_interact()
			KEY_ESCAPE:
				_hide_dialogue()
		if direction != Vector2i.ZERO:
			_hide_dialogue()
			_move_player(direction)
	else:
		if key_event.keycode == KEY_ESCAPE:
			action_mode = ""
			chosen_ability.clear()
			_set_message("Choose a tactical command.")
			queue_redraw()


func _move_player(direction: Vector2i) -> void:
	facing = direction
	var destination: Vector2i = player_tile + direction
	if _is_blocked(destination) or destination == npc_tile:
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


func _interact() -> void:
	if busy:
		return
	var front: Vector2i = player_tile + facing
	if front == npc_tile or _tile_distance(player_tile, npc_tile) <= 1:
		_set_message("The local guide looks ready to talk. What do you want to ask?", true)
		return
	if front == primary_door or front == secondary_door:
		_request_story("I open the door directly in front of me and enter. Describe only the first room and what is immediately visible. Keep secrets and distant locations hidden.")
		return
	_set_message("Nothing nearby demands your attention. Explore the paths and speak to people you meet.")


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
	_set_message("You need to stand next to the local guide first.")
	return false


func _tile_distance(a: Vector2i, b: Vector2i) -> int:
	return absi(a.x - b.x) + absi(a.y - b.y)


func _request_story(action_text: String) -> void:
	_post("/action", {"action": action_text}, "story")


func _start_training_battle() -> void:
	_post("/prototype/battle/start", {}, "battle_start")


func _hide_dialogue() -> void:
	dialogue_panel.visible = false
	dialogue_choices.visible = false


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
	_update_world_theme()
	_update_main_controller(payload)
	_update_header()
	_refresh_mode_interface()
	var narration: String = str(payload.get("narration", "")).strip_edges()
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
		hint_label.text = "CLICK A COMMAND, THEN CHOOSE A SQUARE"
	else:
		var world: Dictionary = game_state.get("world_profile", {}) if game_state.get("world_profile") is Dictionary else {}
		var campaign: Dictionary = game_state.get("campaign", {}) if game_state.get("campaign") is Dictionary else {}
		var world_name: String = str(world.get("name", campaign.get("name", "THE SHATTERED REALMS")))
		var location: String = str(game_state.get("current_location", "Frontier Outpost"))
		title_label.text = world_name.to_upper()
		subtitle_label.text = location
		hint_label.text = "MOVE  WASD / ARROWS     INTERACT  E / SPACE"


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


func _set_message(text: String, show_choices: bool = false) -> void:
	dialogue_panel.visible = true
	dialogue_choices.visible = show_choices
	dialogue_label.text = text


func _set_buttons_disabled(disabled: bool) -> void:
	for child in dialogue_choices.get_children():
		if child is Button:
			(child as Button).disabled = disabled
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
