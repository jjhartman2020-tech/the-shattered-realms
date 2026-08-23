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
const SUCCESS := Color("34d399")
const DANGER := Color("fb7185")

var http: HTTPRequest
var request_mode := "session"
var latest_state: Dictionary = {}
var story_history: Array[String] = []
var busy := false

var connection_label: Label
var player_name_label: Label
var class_label: Label
var hp_label: Label
var shield_label: Label
var armor_label: Label
var resource_label: Label
var level_label: Label
var money_label: Label
var location_label: Label
var weapon_label: Label
var story_text: RichTextLabel
var suggestions_box: VBoxContainer
var action_input: LineEdit
var send_button: Button
var context_title: Label
var context_text: RichTextLabel


func _ready() -> void:
	_build_ui()
	http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_request_completed)
	_load_session()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = BG
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	var outer := MarginContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.add_theme_constant_override("margin_left", 22)
	outer.add_theme_constant_override("margin_right", 22)
	outer.add_theme_constant_override("margin_top", 18)
	outer.add_theme_constant_override("margin_bottom", 18)
	add_child(outer)

	var root_v := VBoxContainer.new()
	root_v.add_theme_constant_override("separation", 14)
	outer.add_child(root_v)

	var header := HBoxContainer.new()
	header.custom_minimum_size.y = 54
	root_v.add_child(header)

	var title := Label.new()
	title.text = "THE SHATTERED REALMS"
	title.add_theme_font_size_override("font_size", 28)
	title.add_theme_color_override("font_color", TEXT)
	header.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "  AI RPG"
	subtitle.add_theme_font_size_override("font_size", 15)
	subtitle.add_theme_color_override("font_color", MUTED)
	header.add_child(subtitle)

	var header_spacer := Control.new()
	header_spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(header_spacer)

	connection_label = Label.new()
	connection_label.text = "Connecting..."
	connection_label.add_theme_color_override("font_color", MUTED)
	header.add_child(connection_label)

	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 14)
	root_v.add_child(body)

	body.add_child(_build_player_panel())
	body.add_child(_build_story_panel())
	body.add_child(_build_context_panel())

	var nav := HBoxContainer.new()
	nav.alignment = BoxContainer.ALIGNMENT_CENTER
	nav.add_theme_constant_override("separation", 10)
	root_v.add_child(nav)
	for entry in [
		["PLAYER", "player"], ["INVENTORY", "inventory"], ["MAP", "map"],
		["PARTY", "party"], ["SUMMARY", "summary"], ["GALLERY", "gallery"]
	]:
		var button := _make_button(entry[0], false)
		button.custom_minimum_size = Vector2(150, 42)
		button.pressed.connect(_show_context.bind(entry[1]))
		nav.add_child(button)


func _build_player_panel() -> PanelContainer:
	var panel := _panel(PANEL)
	panel.custom_minimum_size.x = 285
	var margin := _panel_margin()
	panel.add_child(margin)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 9)
	margin.add_child(box)

	var heading := Label.new()
	heading.text = "PLAYER"
	heading.add_theme_font_size_override("font_size", 14)
	heading.add_theme_color_override("font_color", MUTED)
	box.add_child(heading)

	var portrait := ColorRect.new()
	portrait.color = PANEL_ALT
	portrait.custom_minimum_size = Vector2(0, 128)
	box.add_child(portrait)

	player_name_label = _big_label("Traveler")
	box.add_child(player_name_label)
	class_label = _muted_label("Unassigned")
	box.add_child(class_label)
	box.add_child(HSeparator.new())

	hp_label = _stat_label("HP: --")
	shield_label = _stat_label("Shield: --")
	armor_label = _stat_label("Armor: --")
	resource_label = _stat_label("Resource: --")
	level_label = _stat_label("Level: --")
	money_label = _stat_label("Money: --")
	location_label = _muted_label("Location: --")
	weapon_label = _muted_label("Weapon: --")
	for node in [hp_label, shield_label, armor_label, resource_label, level_label, money_label, location_label, weapon_label]:
		box.add_child(node)

	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.add_child(spacer)

	var refresh := _make_button("REFRESH STATE", false)
	refresh.pressed.connect(_load_session)
	box.add_child(refresh)
	return panel


func _build_story_panel() -> PanelContainer:
	var panel := _panel(PANEL_ALT)
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var margin := _panel_margin()
	panel.add_child(margin)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	margin.add_child(box)

	var top := HBoxContainer.new()
	box.add_child(top)
	var heading := Label.new()
	heading.text = "GAME MASTER"
	heading.add_theme_font_size_override("font_size", 15)
	heading.add_theme_color_override("font_color", MUTED)
	top.add_child(heading)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(spacer)
	var live := Label.new()
	live.text = "● LIVE"
	live.add_theme_color_override("font_color", SUCCESS)
	top.add_child(live)

	story_text = RichTextLabel.new()
	story_text.bbcode_enabled = false
	story_text.fit_content = false
	story_text.scroll_active = true
	story_text.scroll_following = true
	story_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	story_text.add_theme_font_size_override("normal_font_size", 19)
	story_text.add_theme_color_override("default_color", TEXT)
	box.add_child(story_text)

	var divider := HSeparator.new()
	box.add_child(divider)

	var suggestions_heading := Label.new()
	suggestions_heading.text = "SUGGESTED ACTIONS"
	suggestions_heading.add_theme_font_size_override("font_size", 13)
	suggestions_heading.add_theme_color_override("font_color", MUTED)
	box.add_child(suggestions_heading)

	suggestions_box = VBoxContainer.new()
	suggestions_box.add_theme_constant_override("separation", 8)
	box.add_child(suggestions_box)
	_set_suggestions([])

	var input_row := HBoxContainer.new()
	input_row.add_theme_constant_override("separation", 8)
	box.add_child(input_row)
	action_input = LineEdit.new()
	action_input.placeholder_text = "Type anything your character tries to do..."
	action_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	action_input.custom_minimum_size.y = 46
	action_input.text_submitted.connect(_send_action)
	input_row.add_child(action_input)
	send_button = _make_button("SEND", true)
	send_button.custom_minimum_size = Vector2(110, 46)
	send_button.pressed.connect(_send_from_input)
	input_row.add_child(send_button)
	return panel


func _build_context_panel() -> PanelContainer:
	var panel := _panel(PANEL)
	panel.custom_minimum_size.x = 315
	var margin := _panel_margin()
	panel.add_child(margin)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	margin.add_child(box)
	context_title = Label.new()
	context_title.text = "QUICK VIEW"
	context_title.add_theme_font_size_override("font_size", 15)
	context_title.add_theme_color_override("font_color", MUTED)
	box.add_child(context_title)
	context_text = RichTextLabel.new()
	context_text.bbcode_enabled = false
	context_text.fit_content = false
	context_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	context_text.add_theme_font_size_override("normal_font_size", 16)
	context_text.add_theme_color_override("default_color", TEXT)
	context_text.text = "Your inventory, party, map, and campaign summary will appear here."
	box.add_child(context_text)
	return panel


func _panel(color: Color) -> PanelContainer:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = BORDER
	style.set_border_width_all(1)
	style.set_corner_radius_all(12)
	panel.add_theme_stylebox_override("panel", style)
	return panel


func _panel_margin() -> MarginContainer:
	var margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		margin.add_theme_constant_override(side, 18)
	return margin


func _make_button(text_value: String, primary: bool) -> Button:
	var button := Button.new()
	button.text = text_value
	button.focus_mode = Control.FOCUS_ALL
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


func _big_label(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_font_size_override("font_size", 24)
	label.add_theme_color_override("font_color", TEXT)
	return label


func _muted_label(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 14)
	label.add_theme_color_override("font_color", MUTED)
	return label


func _stat_label(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_font_size_override("font_size", 16)
	label.add_theme_color_override("font_color", TEXT)
	return label


func _load_session() -> void:
	if busy:
		return
	busy = true
	request_mode = "session"
	connection_label.text = "Connecting..."
	connection_label.add_theme_color_override("font_color", MUTED)
	var err := http.request(API_BASE + "/session")
	if err != OK:
		busy = false
		_set_connection_error("Could not start request")


func _send_from_input() -> void:
	_send_action(action_input.text)


func _send_action(action: String) -> void:
	var clean := action.strip_edges()
	if clean.is_empty() or busy:
		return
	story_history.append("YOU: " + clean)
	_refresh_story()
	action_input.clear()
	busy = true
	_set_inputs_enabled(false)
	request_mode = "action"
	connection_label.text = "GM thinking..."
	connection_label.add_theme_color_override("font_color", MUTED)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var body := JSON.stringify({"action": clean})
	var err := http.request(API_BASE + "/action", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		busy = false
		_set_inputs_enabled(true)
		_set_connection_error("Could not send action")


func _on_request_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	busy = false
	_set_inputs_enabled(true)
	if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300:
		_set_connection_error("Backend unavailable — run: python -m backend.api")
		return
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if not parsed is Dictionary:
		_set_connection_error("Backend returned invalid data")
		return
	var payload: Dictionary = parsed
	if not payload.get("ok", false):
		_set_connection_error(str(payload.get("error", "Unknown backend error")))
		return
	connection_label.text = "● BACKEND CONNECTED"
	connection_label.add_theme_color_override("font_color", SUCCESS)
	latest_state = payload.get("state", {}) if payload.get("state", {}) is Dictionary else {}
	_update_player_panel()
	if request_mode == "session":
		story_history.clear()
	var narration := str(payload.get("narration", "")).strip_edges()
	if not narration.is_empty():
		story_history.append("GM: " + narration)
	_refresh_story()
	_set_suggestions(payload.get("suggested_actions", []))
	_show_context("player")


func _set_connection_error(message: String) -> void:
	connection_label.text = "● " + message
	connection_label.add_theme_color_override("font_color", DANGER)
	story_history.append("SYSTEM: " + message)
	_refresh_story()


func _set_inputs_enabled(enabled: bool) -> void:
	action_input.editable = enabled
	send_button.disabled = not enabled


func _refresh_story() -> void:
	story_text.text = "\n\n".join(story_history)
	await get_tree().process_frame
	story_text.scroll_to_line(max(0, story_text.get_line_count() - 1))


func _set_suggestions(raw) -> void:
	for child in suggestions_box.get_children():
		child.queue_free()
	var suggestions: Array = raw if raw is Array else []
	if suggestions.is_empty():
		var label := _muted_label("Suggestions will appear after the Game Master responds. You can always type anything.")
		suggestions_box.add_child(label)
		return
	for i in range(min(3, suggestions.size())):
		var item = suggestions[i]
		var text_value := ""
		var suffix := ""
		if item is Dictionary:
			text_value = str(item.get("text", "Action"))
			if bool(item.get("requires_roll", false)):
				suffix = "   [ROLL: %s]" % str(item.get("skill", "Core Stat")).to_upper()
			else:
				suffix = "   [NO ROLL EXPECTED]"
		else:
			text_value = str(item)
		var button := _make_button("%d. %s%s" % [i + 1, text_value, suffix], false)
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.custom_minimum_size.y = 42
		button.pressed.connect(_send_action.bind(text_value))
		suggestions_box.add_child(button)


func _update_player_panel() -> void:
	var player: Dictionary = latest_state.get("player", {}) if latest_state.get("player", {}) is Dictionary else {}
	player_name_label.text = str(player.get("name", "Traveler"))
	class_label.text = "%s  •  Level %d" % [str(player.get("class", "Unassigned")), int(player.get("level", 1))]
	var hp := int(player.get("hp", 0))
	var max_hp := int(player.get("max_hp", hp))
	hp_label.text = "HP: %d / %d" % [hp, max_hp]
	var shield := int(player.get("shield_hp", 0))
	var max_shield := int(player.get("max_shield_hp", 0))
	shield_label.text = "Shield: %d / %d" % [shield, max_shield]
	var armor := int(player.get("armor", 0))
	var max_armor := int(player.get("max_armor", 0))
	armor_label.text = "Armor: %d / %d" % [armor, max_armor]
	var resource_name := str(player.get("resource_name", "Resource"))
	var resource := int(player.get("resource", player.get("mana", 0)))
	var max_resource := int(player.get("max_resource", player.get("max_mana", resource)))
	resource_label.text = "%s: %d / %d" % [resource_name, resource, max_resource]
	level_label.text = "XP: %d / %d   •   SP %d   •   AP %d" % [
		int(player.get("xp_orbs", 0)), int(player.get("xp_to_next_level", 0)),
		int(player.get("skill_points_unspent", 0)), int(player.get("ability_points", 0))
	]
	money_label.text = "Money: " + _money_text(player)
	location_label.text = "Location: " + str(player.get("location", "Unknown"))
	var weapon = player.get("equipped_weapon")
	if weapon is Dictionary:
		weapon_label.text = "Weapon: %s  •  %s" % [str(weapon.get("name", "Weapon")), str(weapon.get("damage", "?"))]
	else:
		weapon_label.text = "Weapon: None"


func _money_text(player: Dictionary) -> String:
	var wallet = player.get("wallet")
	if not wallet is Dictionary:
		return "0"
	var amount := int(wallet.get("amount", 0))
	var symbol := str(wallet.get("symbol", ""))
	var name := str(wallet.get("name", "currency"))
	if not symbol.is_empty() and bool(wallet.get("prefix", false)):
		return "%s%d" % [symbol, amount]
	return "%d %s" % [amount, name]


func _show_context(kind: String) -> void:
	var player: Dictionary = latest_state.get("player", {}) if latest_state.get("player", {}) is Dictionary else {}
	match kind:
		"inventory":
			context_title.text = "INVENTORY"
			context_text.text = _inventory_text(player)
		"map":
			context_title.text = "MAP / LOCATION"
			context_text.text = "Current location:\n%s\n\nVisual map support is coming in the next UI passes." % str(player.get("location", "Unknown"))
		"party":
			context_title.text = "PARTY"
			context_text.text = _party_text()
		"summary":
			context_title.text = "CAMPAIGN SUMMARY"
			context_text.text = _summary_text(player)
		"gallery":
			context_title.text = "GALLERY"
			context_text.text = "Generated scene images and videos will live here later."
		_:
			context_title.text = "PLAYER DETAILS"
			context_text.text = _player_details(player)


func _inventory_text(player: Dictionary) -> String:
	var inventory = player.get("inventory")
	if not inventory is Array or inventory.is_empty():
		return "Inventory is empty."
	var lines: Array[String] = []
	for item in inventory:
		if item is Dictionary:
			var qty := int(item.get("quantity", 1))
			var qty_text := " x%d" % qty if qty > 1 else ""
			lines.append("• %s%s [%s]\n  %s" % [
				str(item.get("name", "Item")), qty_text,
				str(item.get("rarity", "common")).capitalize(), str(item.get("description", ""))
			])
		else:
			lines.append("• " + str(item))
	return "\n\n".join(lines)


func _party_text() -> String:
	var party = latest_state.get("party")
	if not party is Array or party.is_empty():
		return "You are currently traveling alone."
	var lines: Array[String] = []
	for member in party:
		if member is Dictionary:
			lines.append("• %s — %s" % [str(member.get("name", "Companion")), str(member.get("role", member.get("class", "Companion")))])
		else:
			lines.append("• " + str(member))
	return "\n".join(lines)


func _summary_text(player: Dictionary) -> String:
	var campaign = latest_state.get("campaign") if latest_state.get("campaign") is Dictionary else {}
	return "%s\n\nDay %d • %s\n\nLocation: %s\nLevel: %d\nHP: %d/%d\nMoney: %s" % [
		str(campaign.get("name", "Untitled Campaign")), int(campaign.get("day", 1)), str(campaign.get("time", "")),
		str(player.get("location", "Unknown")), int(player.get("level", 1)), int(player.get("hp", 0)), int(player.get("max_hp", 0)), _money_text(player)
	]


func _player_details(player: Dictionary) -> String:
	var stats = player.get("stats") if player.get("stats") is Dictionary else {}
	var lines: Array[String] = [
		"%s\n%s\n" % [str(player.get("name", "Traveler")), str(player.get("class", "Unassigned"))]
	]
	for stat in ["health", "resource", "strength", "dexterity", "agility", "constitution", "intelligence", "wisdom", "charisma", "speed", "defense", "luck", "magic"]:
		lines.append("%s: %d" % [stat.capitalize(), int(stats.get(stat, 0))])
	return "\n".join(lines)
