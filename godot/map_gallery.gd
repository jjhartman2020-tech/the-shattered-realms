extends Control

signal api_request(endpoint: String, payload: Dictionary, mode: String)

const BG := Color("080c13")
const PANEL := Color("151b26")
const PANEL_ALT := Color("101621")
const BORDER := Color("2b3547")
const TEXT := Color("edf2f7")
const MUTED := Color("94a3b8")
const ACCENT := Color("8b5cf6")
const ACCENT_HOVER := Color("a78bfa")
const SUCCESS := Color("34d399")
const DANGER := Color("fb7185")

var maps: Array = []
var current_filter := "all"
var selected_map_id := ""
var current_location := "Unknown"

var search_input: LineEdit
var map_list_box: VBoxContainer
var count_label: Label
var map_title: Label
var map_meta: Label
var map_image: TextureRect
var map_description: Label
var status_label: Label
var filter_buttons: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	z_index = 2400
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false
	_build_ui()


func open_with_state(state: Dictionary) -> void:
	visible = true
	move_to_front()
	current_location = str(state.get("player", {}).get("location", "Unknown")) if state.get("player", {}) is Dictionary else "Unknown"
	var gallery = state.get("map_gallery")
	if gallery is Dictionary:
		maps = gallery.get("maps", []) if gallery.get("maps", []) is Array else []
		selected_map_id = str(gallery.get("selected_map_id") or "")
	_rebuild_map_list()
	_set_status("Loading your saved maps...", false)
	api_request.emit("/maps/list", {}, "map_list")


func close() -> void:
	visible = false


func set_status(message: String, is_error: bool = false) -> void:
	_set_status(message, is_error)


func apply_payload(payload: Dictionary, mode: String) -> void:
	if mode == "map_list":
		maps = payload.get("maps", []) if payload.get("maps", []) is Array else []
		current_location = str(payload.get("current_location", current_location))
		var saved_id := str(payload.get("selected_map_id") or selected_map_id)
		_rebuild_map_list()
		if maps.is_empty():
			_show_empty_preview()
			_set_status("No maps discovered yet. Your first world map is created with your world.", false)
			return
		var preferred := _preferred_map_id(saved_id)
		_request_map(preferred)
		return

	if mode == "map_load":
		var record = payload.get("map")
		if not record is Dictionary:
			_set_status("The backend returned an invalid map.", true)
			return
		selected_map_id = str(record.get("id") or "")
		_show_record(record)
		var encoded := str(payload.get("map_base64") or "")
		if encoded.is_empty():
			map_image.texture = null
			_set_status("This map image could not be loaded.", true)
			return
		var raw := Marshalls.base64_to_raw(encoded)
		var image := Image.new()
		var load_error := image.load_png_from_buffer(raw)
		if load_error != OK:
			load_error = image.load_jpg_from_buffer(raw)
		if load_error != OK:
			map_image.texture = null
			_set_status("This map image could not be read.", true)
			return
		map_image.texture = ImageTexture.create_from_image(image)
		_set_status("Map ready. New places will be added as you discover them.", false)
		_rebuild_map_list()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = BG
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)

	var outer := MarginContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.add_theme_constant_override("margin_left", 32)
	outer.add_theme_constant_override("margin_right", 32)
	outer.add_theme_constant_override("margin_top", 24)
	outer.add_theme_constant_override("margin_bottom", 24)
	add_child(outer)

	var panel := _panel(PANEL_ALT)
	outer.add_child(panel)
	var margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		margin.add_theme_constant_override(side, 22)
	panel.add_child(margin)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 12)
	margin.add_child(root)

	var header := HBoxContainer.new()
	header.add_theme_constant_override("separation", 10)
	root.add_child(header)
	var heading := Label.new()
	heading.text = "MAP GALLERY"
	heading.add_theme_font_size_override("font_size", 28)
	heading.add_theme_color_override("font_color", TEXT)
	header.add_child(heading)
	count_label = _muted("0 MAPS")
	count_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	header.add_child(count_label)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(spacer)
	var close_button := _button("CLOSE", false)
	close_button.custom_minimum_size = Vector2(120, 42)
	close_button.pressed.connect(close)
	header.add_child(close_button)

	var tools := HBoxContainer.new()
	tools.add_theme_constant_override("separation", 8)
	root.add_child(tools)
	search_input = LineEdit.new()
	search_input.placeholder_text = "Search map titles or locations..."
	search_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	search_input.custom_minimum_size.y = 44
	search_input.text_changed.connect(_on_search_changed)
	tools.add_child(search_input)
	for filter_name in ["all", "universe", "world", "town"]:
		var filter_button := _button(filter_name.to_upper() if filter_name != "town" else "TOWNS", false)
		filter_button.custom_minimum_size = Vector2(118, 44)
		filter_button.toggle_mode = true
		filter_button.button_pressed = filter_name == current_filter
		filter_button.pressed.connect(_set_filter.bind(filter_name))
		filter_buttons[filter_name] = filter_button
		tools.add_child(filter_button)

	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 12)
	root.add_child(body)

	var library_panel := _panel(PANEL)
	library_panel.custom_minimum_size.x = 355
	body.add_child(library_panel)
	var library_margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		library_margin.add_theme_constant_override(side, 14)
	library_panel.add_child(library_margin)
	var library_root := VBoxContainer.new()
	library_root.add_theme_constant_override("separation", 9)
	library_margin.add_child(library_root)
	var library_heading := _label("DISCOVERED MAPS")
	library_root.add_child(library_heading)
	var map_scroll := ScrollContainer.new()
	map_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	map_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	library_root.add_child(map_scroll)
	map_list_box = VBoxContainer.new()
	map_list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	map_list_box.add_theme_constant_override("separation", 8)
	map_scroll.add_child(map_list_box)

	var preview_panel := _panel(PANEL)
	preview_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(preview_panel)
	var preview_margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		preview_margin.add_theme_constant_override(side, 16)
	preview_panel.add_child(preview_margin)
	var preview_root := VBoxContainer.new()
	preview_root.add_theme_constant_override("separation", 8)
	preview_margin.add_child(preview_root)
	map_title = Label.new()
	map_title.text = "SELECT A MAP"
	map_title.add_theme_font_size_override("font_size", 24)
	map_title.add_theme_color_override("font_color", TEXT)
	map_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	preview_root.add_child(map_title)
	map_meta = _muted("")
	preview_root.add_child(map_meta)
	map_image = TextureRect.new()
	map_image.custom_minimum_size = Vector2(0, 430)
	map_image.size_flags_vertical = Control.SIZE_EXPAND_FILL
	map_image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	map_image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	map_image.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	preview_root.add_child(map_image)
	map_description = _label("Your maps will appear here as the adventure reveals them.")
	map_description.add_theme_color_override("font_color", MUTED)
	preview_root.add_child(map_description)

	status_label = _muted("")
	root.add_child(status_label)


func _set_filter(filter_name: String) -> void:
	current_filter = filter_name
	for key in filter_buttons:
		filter_buttons[key].button_pressed = str(key) == current_filter
	_rebuild_map_list()


func _on_search_changed(_value: String) -> void:
	_rebuild_map_list()


func _rebuild_map_list() -> void:
	if not is_instance_valid(map_list_box):
		return
	for child in map_list_box.get_children():
		child.queue_free()
	var query := search_input.text.strip_edges().to_lower() if is_instance_valid(search_input) else ""
	var shown := 0
	for raw in maps:
		if not raw is Dictionary:
			continue
		var map_type := str(raw.get("map_type", "town")).to_lower()
		if current_filter != "all" and map_type != current_filter:
			continue
		var searchable := "%s %s %s" % [str(raw.get("title", "")), str(raw.get("location", "")), str(raw.get("description", ""))]
		if not query.is_empty() and searchable.to_lower().find(query) < 0:
			continue
		shown += 1
		var button := _button("%s\n%s  •  %s" % [
			str(raw.get("title", "Untitled Map")), map_type.to_upper(), str(raw.get("location", "Unknown"))
		], str(raw.get("id", "")) == selected_map_id)
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.custom_minimum_size.y = 64
		button.pressed.connect(_request_map.bind(str(raw.get("id", ""))))
		map_list_box.add_child(button)
	if shown == 0:
		map_list_box.add_child(_muted("No maps match this search."))
	if is_instance_valid(count_label):
		count_label.text = "%d MAP%s" % [maps.size(), "" if maps.size() == 1 else "S"]


func _preferred_map_id(saved_id: String) -> String:
	if not saved_id.is_empty() and _record_for_id(saved_id) != null:
		return saved_id
	for raw in maps:
		if raw is Dictionary and str(raw.get("location", "")).to_lower() == current_location.to_lower():
			return str(raw.get("id", ""))
	for raw in maps:
		if raw is Dictionary and str(raw.get("map_type", "")) == "world":
			return str(raw.get("id", ""))
	return str(maps[0].get("id", "")) if maps[0] is Dictionary else ""


func _record_for_id(map_id: String):
	for raw in maps:
		if raw is Dictionary and str(raw.get("id", "")) == map_id:
			return raw
	return null


func _request_map(map_id: String) -> void:
	if map_id.is_empty():
		return
	selected_map_id = map_id
	var record = _record_for_id(map_id)
	if record is Dictionary:
		_show_record(record)
		map_image.texture = null
		_set_status("Generating this map..." if str(record.get("image_status", "pending")) != "ready" else "Loading map...", false)
	_rebuild_map_list()
	api_request.emit("/maps/load", {"map_id": map_id}, "map_load")


func _show_record(record: Dictionary) -> void:
	map_title.text = str(record.get("title", "Untitled Map")).to_upper()
	map_meta.text = "%s MAP  •  %s  •  DISCOVERED TURN %d" % [
		str(record.get("map_type", "town")).to_upper(),
		str(record.get("location", "Unknown")),
		int(record.get("discovered_turn", 0))
	]
	map_description.text = str(record.get("description", ""))


func _show_empty_preview() -> void:
	selected_map_id = ""
	map_title.text = "NO MAPS YET"
	map_meta.text = ""
	map_image.texture = null
	map_description.text = "Create a world to receive your first world map. Town maps will be added as you discover new places."


func _set_status(message: String, is_error: bool) -> void:
	if not is_instance_valid(status_label):
		return
	status_label.text = message
	status_label.add_theme_color_override("font_color", DANGER if is_error else (SUCCESS if message.begins_with("Map ready") else MUTED))


func _panel(color: Color) -> PanelContainer:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = BORDER
	style.set_border_width_all(1)
	style.set_corner_radius_all(12)
	panel.add_theme_stylebox_override("panel", style)
	return panel


func _button(value: String, primary: bool) -> Button:
	var button := Button.new()
	button.text = value
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


func _label(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 15)
	label.add_theme_color_override("font_color", TEXT)
	return label


func _muted(value: String) -> Label:
	var label := _label(value)
	label.add_theme_color_override("font_color", MUTED)
	label.add_theme_font_size_override("font_size", 14)
	return label
