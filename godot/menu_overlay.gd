extends Control

const API_BASE := "http://127.0.0.1:8765"
const BG := Color("0b0f17")
const PANEL := Color("151b26")
const PANEL_ALT := Color("101621")
const BORDER := Color("2b3547")
const TEXT := Color("edf2f7")
const MUTED := Color("94a3b8")
const ACCENT := Color("8b5cf6")
const ACCENT_HOVER := Color("a78bfa")
const DANGER := Color("fb7185")

var menu_button: Button
var backdrop: ColorRect
var menu_panel: PanelContainer
var new_game_confirm: ConfirmationDialog
var http: HTTPRequest
var large_text := false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	call_deferred("_build_menu")


func _build_menu() -> void:
	var parent = get_parent()
	if parent == null:
		return

	menu_button = _button("☰  MENU", false)
	menu_button.custom_minimum_size = Vector2(120, 40)
	menu_button.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	menu_button.position = Vector2(-145, 18)
	menu_button.mouse_filter = Control.MOUSE_FILTER_STOP
	menu_button.pressed.connect(_open_menu)
	add_child(menu_button)

	backdrop = ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.72)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_STOP
	backdrop.hide()
	add_child(backdrop)

	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.add_child(center)

	menu_panel = _panel(PANEL)
	menu_panel.custom_minimum_size = Vector2(690, 650)
	center.add_child(menu_panel)

	var margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		margin.add_theme_constant_override(side, 24)
	menu_panel.add_child(margin)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 16)
	margin.add_child(root)

	var header := HBoxContainer.new()
	root.add_child(header)
	var title := Label.new()
	title.text = "GAME MENU"
	title.add_theme_font_size_override("font_size", 28)
	title.add_theme_color_override("font_color", TEXT)
	header.add_child(title)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(spacer)
	var close := _button("✕", false)
	close.custom_minimum_size = Vector2(44, 40)
	close.pressed.connect(_close_menu)
	header.add_child(close)

	var sub := Label.new()
	sub.text = "Open game screens directly instead of typing commands."
	sub.add_theme_color_override("font_color", MUTED)
	sub.add_theme_font_size_override("font_size", 15)
	root.add_child(sub)

	root.add_child(HSeparator.new())

	var game_heading := _section_label("GAME")
	root.add_child(game_heading)
	var game_grid := GridContainer.new()
	game_grid.columns = 2
	game_grid.add_theme_constant_override("h_separation", 10)
	game_grid.add_theme_constant_override("v_separation", 10)
	root.add_child(game_grid)
	_add_nav_button(game_grid, "PLAYER", "player")
	_add_nav_button(game_grid, "INVENTORY", "inventory")
	_add_nav_button(game_grid, "EQUIPMENT", "equipment")
	_add_nav_button(game_grid, "ABILITIES", "abilities")
	_add_nav_button(game_grid, "PROGRESSION", "progression")
	_add_nav_button(game_grid, "WALLET", "wallet")
	_add_nav_button(game_grid, "MAP", "map")
	_add_nav_button(game_grid, "PARTY", "party")
	_add_nav_button(game_grid, "CAMPAIGN SUMMARY", "summary")
	_add_nav_button(game_grid, "GALLERY", "gallery")

	root.add_child(HSeparator.new())
	root.add_child(_section_label("DISPLAY / APP"))
	var utility_grid := GridContainer.new()
	utility_grid.columns = 2
	utility_grid.add_theme_constant_override("h_separation", 10)
	utility_grid.add_theme_constant_override("v_separation", 10)
	root.add_child(utility_grid)

	var text_button := _button("TOGGLE LARGE TEXT", false)
	text_button.custom_minimum_size = Vector2(310, 42)
	text_button.pressed.connect(_toggle_large_text)
	utility_grid.add_child(text_button)

	var refresh := _button("REFRESH GAME STATE", false)
	refresh.custom_minimum_size = Vector2(310, 42)
	refresh.pressed.connect(_refresh_state)
	utility_grid.add_child(refresh)

	var return_button := _button("RETURN TO GAME", true)
	return_button.custom_minimum_size = Vector2(310, 42)
	return_button.pressed.connect(_close_menu)
	utility_grid.add_child(return_button)

	var new_game := _button("NEW GAME", false)
	new_game.custom_minimum_size = Vector2(310, 42)
	new_game.add_theme_color_override("font_color", DANGER)
	new_game.pressed.connect(_ask_new_game)
	utility_grid.add_child(new_game)

	var note := Label.new()
	note.text = "New Game clears the current saved campaign and AI campaign memory. You will always get a confirmation first."
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	note.add_theme_color_override("font_color", MUTED)
	note.add_theme_font_size_override("font_size", 13)
	root.add_child(note)

	new_game_confirm = ConfirmationDialog.new()
	new_game_confirm.title = "Start a New Game?"
	new_game_confirm.dialog_text = "This will erase the current campaign state and campaign memory on this device. Continue?"
	new_game_confirm.ok_button_text = "START NEW GAME"
	new_game_confirm.cancel_button_text = "CANCEL"
	new_game_confirm.confirmed.connect(_start_new_game)
	add_child(new_game_confirm)

	http = HTTPRequest.new()
	http.request_completed.connect(_on_new_game_completed)
	add_child(http)


func _section_label(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_color_override("font_color", MUTED)
	label.add_theme_font_size_override("font_size", 13)
	return label


func _panel(color: Color) -> PanelContainer:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = BORDER
	style.set_border_width_all(1)
	style.set_corner_radius_all(14)
	panel.add_theme_stylebox_override("panel", style)
	return panel


func _button(value: String, primary: bool) -> Button:
	var button := Button.new()
	button.text = value
	var normal := StyleBoxFlat.new()
	normal.bg_color = ACCENT if primary else PANEL_ALT
	normal.border_color = ACCENT if primary else BORDER
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(8)
	var hover := normal.duplicate()
	hover.bg_color = ACCENT_HOVER if primary else Color("1d2635")
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", hover)
	button.add_theme_color_override("font_color", TEXT)
	button.add_theme_font_size_override("font_size", 14)
	return button


func _add_nav_button(grid: GridContainer, label: String, kind: String) -> void:
	var button := _button(label, false)
	button.custom_minimum_size = Vector2(310, 42)
	button.pressed.connect(_open_screen.bind(kind))
	grid.add_child(button)


func _open_menu() -> void:
	backdrop.show()
	menu_button.hide()
	mouse_filter = Control.MOUSE_FILTER_STOP


func _close_menu() -> void:
	backdrop.hide()
	menu_button.show()
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _open_screen(kind: String) -> void:
	var parent = get_parent()
	if parent == null:
		return
	match kind:
		"equipment":
			parent.context_title.text = "EQUIPMENT"
			parent.context_text.text = _equipment_text(parent.latest_state)
		"abilities":
			parent.context_title.text = "ABILITIES"
			parent.context_text.text = _abilities_text(parent.latest_state)
		"progression":
			parent.context_title.text = "PROGRESSION"
			parent.context_text.text = _progression_text(parent.latest_state)
		"wallet":
			parent.context_title.text = "WALLET"
			var player: Dictionary = parent.latest_state.get("player", {}) if parent.latest_state.get("player", {}) is Dictionary else {}
			parent.context_text.text = "Current balance:\n\n" + parent._money_text(player)
		_:
			parent._show_context(kind)
	_close_menu()


func _equipment_text(state: Dictionary) -> String:
	var player: Dictionary = state.get("player", {}) if state.get("player", {}) is Dictionary else {}
	var lines: Array[String] = []
	var weapon = player.get("equipped_weapon")
	lines.append("WEAPON\n" + _item_line(weapon))
	var shield = player.get("equipped_shield")
	lines.append("SHIELD\n" + _item_line(shield))
	lines.append("ARMOR")
	var armor = player.get("equipped_armor")
	if armor is Dictionary and not armor.is_empty():
		for slot in ["helmet", "breastplate", "pants", "gloves", "boots"]:
			lines.append("%s: %s" % [slot.capitalize(), _item_line(armor.get(slot))])
	else:
		lines.append("No armor equipped.")
	return "\n\n".join(lines)


func _item_line(item) -> String:
	if not item is Dictionary:
		return "None"
	var rarity := str(item.get("rarity", "common")).capitalize()
	var detail := ""
	if item.get("damage"):
		detail = " • Damage " + str(item.get("damage"))
	elif item.get("shield"):
		detail = " • Shield HP " + str(item.get("shield"))
	elif item.get("max_armor_hp"):
		detail = " • Armor HP " + str(item.get("max_armor_hp"))
	return "%s [%s]%s" % [str(item.get("name", "Item")), rarity, detail]


func _abilities_text(state: Dictionary) -> String:
	var player: Dictionary = state.get("player", {}) if state.get("player", {}) is Dictionary else {}
	var equipped = player.get("equipped_abilities")
	var unlocked = player.get("unlocked_abilities")
	var lines: Array[String] = ["EQUIPPED (max 4)"]
	if equipped is Array and not equipped.is_empty():
		for ability in equipped:
			if ability is Dictionary:
				lines.append("• %s — Cost %s %s" % [str(ability.get("name", "Ability")), str(ability.get("resource_cost", 0)), str(player.get("resource_name", "Resource"))])
	else:
		lines.append("None equipped.")
	lines.append("\nUNLOCKED")
	if unlocked is Array and not unlocked.is_empty():
		for ability in unlocked:
			if ability is Dictionary:
				lines.append("• %s [%s]" % [str(ability.get("name", "Ability")), str(ability.get("tier", "beginner")).capitalize()])
	else:
		lines.append("No unlocked abilities.")
	return "\n".join(lines)


func _progression_text(state: Dictionary) -> String:
	var player: Dictionary = state.get("player", {}) if state.get("player", {}) is Dictionary else {}
	return "Level %d / 100\nXP Orbs: %d / %d\n\nStored SP: %d\nStored AP: %d" % [
		int(player.get("level", 1)),
		int(player.get("xp_orbs", 0)),
		int(player.get("xp_to_next_level", 0)),
		int(player.get("skill_points_unspent", 0)),
		int(player.get("ability_points", 0))
	]


func _toggle_large_text() -> void:
	large_text = not large_text
	var parent = get_parent()
	if parent == null:
		return
	parent.story_text.add_theme_font_size_override("normal_font_size", 23 if large_text else 19)
	parent.context_text.add_theme_font_size_override("normal_font_size", 19 if large_text else 16)


func _refresh_state() -> void:
	var parent = get_parent()
	_close_menu()
	if parent != null:
		parent._load_session()


func _ask_new_game() -> void:
	new_game_confirm.popup_centered(Vector2i(520, 190))


func _start_new_game() -> void:
	_close_menu()
	menu_button.disabled = true
	var headers := PackedStringArray(["Content-Type: application/json"])
	var error := http.request(API_BASE + "/new_game", headers, HTTPClient.METHOD_POST, "{}")
	if error != OK:
		menu_button.disabled = false
		var parent = get_parent()
		if parent != null:
			parent._set_connection_error("Could not start new game")


func _on_new_game_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	menu_button.disabled = false
	var parent = get_parent()
	if parent == null:
		return
	if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300:
		parent._set_connection_error("New Game request failed")
		return
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if not parsed is Dictionary or not parsed.get("ok", false):
		parent._set_connection_error("New Game returned invalid data")
		return
	parent.latest_state = parsed.get("state", {}) if parsed.get("state", {}) is Dictionary else {}
	parent.story_history.clear()
	var narration := str(parsed.get("narration", "New campaign started."))
	parent.story_history.append("GM: " + narration)
	parent._update_player_panel()
	parent._refresh_story()
	parent._set_suggestions(parsed.get("suggested_actions", []))
	parent._show_context("player")
	parent.connection_label.text = "● BACKEND CONNECTED"
