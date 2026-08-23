extends Control

const API_BASE := "http://127.0.0.1:8765"
const PANEL := Color("151b26")
const PANEL_ALT := Color("101621")
const BORDER := Color("2b3547")
const TEXT := Color("edf2f7")
const MUTED := Color("94a3b8")
const ACCENT := Color("8b5cf6")
const ACCENT_HOVER := Color("a78bfa")
const DANGER := Color("fb7185")

var new_game_confirm: ConfirmationDialog
var http: HTTPRequest
var large_text := false
var large_text_button: Button


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	z_index = 100
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false
	_build_menu()


func _build_menu() -> void:
	# The dark backdrop is visual only. It deliberately ignores mouse input so
	# clicks can reach the actual menu controls above it.
	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.72)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(backdrop)

	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	center.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(center)

	var menu_panel := _panel(PANEL)
	menu_panel.custom_minimum_size = Vector2(560, 390)
	menu_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	center.add_child(menu_panel)

	var margin := MarginContainer.new()
	margin.mouse_filter = Control.MOUSE_FILTER_PASS
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		margin.add_theme_constant_override(side, 28)
	menu_panel.add_child(margin)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 18)
	root.mouse_filter = Control.MOUSE_FILTER_PASS
	margin.add_child(root)

	var header := HBoxContainer.new()
	header.mouse_filter = Control.MOUSE_FILTER_PASS
	root.add_child(header)

	var title := Label.new()
	title.text = "SETTINGS"
	title.add_theme_font_size_override("font_size", 28)
	title.add_theme_color_override("font_color", TEXT)
	header.add_child(title)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	header.add_child(spacer)

	var close := _button("✕", false)
	close.custom_minimum_size = Vector2(48, 42)
	close.pressed.connect(_close_menu)
	header.add_child(close)

	var sub := Label.new()
	sub.text = "Game settings and campaign controls."
	sub.add_theme_color_override("font_color", MUTED)
	sub.add_theme_font_size_override("font_size", 15)
	root.add_child(sub)

	root.add_child(HSeparator.new())
	root.add_child(_section_label("DISPLAY"))

	large_text_button = _button("LARGE TEXT: OFF", false)
	large_text_button.custom_minimum_size = Vector2(0, 48)
	large_text_button.pressed.connect(_toggle_large_text)
	root.add_child(large_text_button)

	root.add_child(HSeparator.new())
	root.add_child(_section_label("CAMPAIGN"))

	var new_game := _button("START NEW GAME", false)
	new_game.custom_minimum_size = Vector2(0, 52)
	new_game.add_theme_color_override("font_color", DANGER)
	new_game.pressed.connect(_ask_new_game)
	root.add_child(new_game)

	var note := Label.new()
	note.text = "Starting a new game clears the current campaign state and AI campaign memory on this device."
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
	button.focus_mode = Control.FOCUS_ALL
	button.mouse_filter = Control.MOUSE_FILTER_STOP
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


func _open_menu() -> void:
	visible = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	move_to_front()


func _close_menu() -> void:
	visible = false


func _toggle_large_text() -> void:
	large_text = not large_text
	large_text_button.text = "LARGE TEXT: ON" if large_text else "LARGE TEXT: OFF"
	var parent = get_parent()
	if parent == null:
		return
	parent.story_text.add_theme_font_size_override("normal_font_size", 23 if large_text else 19)
	parent.context_text.add_theme_font_size_override("normal_font_size", 19 if large_text else 16)


func _ask_new_game() -> void:
	new_game_confirm.popup_centered(Vector2i(520, 190))


func _start_new_game() -> void:
	var headers := PackedStringArray(["Content-Type: application/json"])
	var error := http.request(API_BASE + "/new_game", headers, HTTPClient.METHOD_POST, "{}")
	if error != OK:
		var parent = get_parent()
		if parent != null:
			parent._set_connection_error("Could not start new game")
		return
	_close_menu()


func _on_new_game_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
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
	parent.story_history.append("GM: " + str(parsed.get("narration", "New campaign started.")))
	parent._update_player_panel()
	parent._refresh_story()
	parent._set_suggestions(parsed.get("suggested_actions", []))
	parent._show_context("player")
	parent.connection_label.text = "● BACKEND CONNECTED"
