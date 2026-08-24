extends Control

const BG := Color("05070bd9")
const PANEL := Color("101621")
const BORDER := Color("354158")
const TEXT := Color("edf2f7")
const MUTED := Color("94a3b8")
const ACCENT := Color("8b5cf6")
const ACCENT_HOVER := Color("a78bfa")

var current_texture: Texture2D
var zoom_level := 1.0
var title_label: Label
var zoom_label: Label
var viewer_scroll: ScrollContainer
var viewer_canvas: CenterContainer
var viewer_image: TextureRect


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	z_index = 5000
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false
	_build_ui()
	resized.connect(_apply_zoom)


func open_map(texture: Texture2D, map_title: String) -> void:
	current_texture = texture
	viewer_image.texture = texture
	title_label.text = map_title
	zoom_level = 1.0
	visible = true
	move_to_front()
	call_deferred("_apply_zoom")


func close() -> void:
	visible = false


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = BG
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(background)

	var outer := MarginContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.add_theme_constant_override("margin_left", 22)
	outer.add_theme_constant_override("margin_right", 22)
	outer.add_theme_constant_override("margin_top", 18)
	outer.add_theme_constant_override("margin_bottom", 18)
	add_child(outer)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 10)
	outer.add_child(root)

	var toolbar := HBoxContainer.new()
	toolbar.add_theme_constant_override("separation", 8)
	root.add_child(toolbar)
	title_label = Label.new()
	title_label.text = "MAP"
	title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	title_label.add_theme_font_size_override("font_size", 23)
	title_label.add_theme_color_override("font_color", TEXT)
	toolbar.add_child(title_label)
	zoom_label = Label.new()
	zoom_label.text = "FIT"
	zoom_label.custom_minimum_size.x = 72
	zoom_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	zoom_label.add_theme_color_override("font_color", MUTED)
	toolbar.add_child(zoom_label)
	var zoom_out := _button("−", false)
	zoom_out.tooltip_text = "Zoom out"
	zoom_out.pressed.connect(_zoom_by.bind(0.8))
	toolbar.add_child(zoom_out)
	var reset := _button("FIT", false)
	reset.tooltip_text = "Fit the entire map"
	reset.pressed.connect(_reset_zoom)
	toolbar.add_child(reset)
	var zoom_in := _button("+", false)
	zoom_in.tooltip_text = "Zoom in"
	zoom_in.pressed.connect(_zoom_by.bind(1.25))
	toolbar.add_child(zoom_in)
	var close_button := _button("CLOSE", true)
	close_button.custom_minimum_size.x = 110
	close_button.pressed.connect(close)
	toolbar.add_child(close_button)

	var hint := Label.new()
	hint.text = "Mouse wheel or + / − to zoom. Use the scrollbars to move around the map. Press Esc to close."
	hint.add_theme_font_size_override("font_size", 13)
	hint.add_theme_color_override("font_color", MUTED)
	root.add_child(hint)

	var frame := PanelContainer.new()
	frame.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var frame_style := StyleBoxFlat.new()
	frame_style.bg_color = PANEL
	frame_style.border_color = BORDER
	frame_style.set_border_width_all(1)
	frame_style.set_corner_radius_all(10)
	frame.add_theme_stylebox_override("panel", frame_style)
	root.add_child(frame)

	viewer_scroll = ScrollContainer.new()
	viewer_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	viewer_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	viewer_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	viewer_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	viewer_scroll.gui_input.connect(_on_viewer_input)
	frame.add_child(viewer_scroll)

	viewer_canvas = CenterContainer.new()
	viewer_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer_scroll.add_child(viewer_canvas)
	viewer_image = TextureRect.new()
	viewer_image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	viewer_image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	viewer_image.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	viewer_image.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer_canvas.add_child(viewer_image)


func _on_viewer_input(event: InputEvent) -> void:
	if not event is InputEventMouseButton:
		return
	var mouse_event := event as InputEventMouseButton
	if not mouse_event.pressed:
		return
	if mouse_event.button_index == MOUSE_BUTTON_WHEEL_UP:
		_zoom_by(1.2)
		viewer_scroll.accept_event()
	elif mouse_event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		_zoom_by(1.0 / 1.2)
		viewer_scroll.accept_event()


func _unhandled_key_input(event: InputEvent) -> void:
	if not visible or not event is InputEventKey:
		return
	var key_event := event as InputEventKey
	if key_event.pressed and not key_event.echo and key_event.keycode == KEY_ESCAPE:
		close()
		get_viewport().set_input_as_handled()


func _reset_zoom() -> void:
	zoom_level = 1.0
	_apply_zoom()


func _zoom_by(multiplier: float) -> void:
	zoom_level = clampf(zoom_level * multiplier, 0.5, 5.0)
	_apply_zoom()


func _apply_zoom() -> void:
	if current_texture == null or not is_instance_valid(viewer_scroll):
		return
	var available := viewer_scroll.size - Vector2(28, 28)
	if available.x < 40.0 or available.y < 40.0:
		call_deferred("_apply_zoom")
		return
	var texture_size := current_texture.get_size()
	if texture_size.x <= 0.0 or texture_size.y <= 0.0:
		return
	var fit_scale: float = minf(available.x / texture_size.x, available.y / texture_size.y)
	var display_size := texture_size * fit_scale * zoom_level
	viewer_image.custom_minimum_size = display_size
	viewer_canvas.custom_minimum_size = Vector2(maxf(available.x, display_size.x), maxf(available.y, display_size.y))
	zoom_label.text = "FIT" if is_equal_approx(zoom_level, 1.0) else "%d%%" % int(round(zoom_level * 100.0))


func _button(value: String, primary: bool) -> Button:
	var button := Button.new()
	button.text = value
	button.custom_minimum_size = Vector2(52, 40)
	var normal := StyleBoxFlat.new()
	normal.bg_color = ACCENT if primary else PANEL
	normal.border_color = ACCENT if primary else BORDER
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(7)
	var hover := normal.duplicate()
	hover.bg_color = ACCENT_HOVER if primary else Color("1d2635")
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", hover)
	button.add_theme_color_override("font_color", TEXT)
	button.add_theme_font_size_override("font_size", 14)
	return button
