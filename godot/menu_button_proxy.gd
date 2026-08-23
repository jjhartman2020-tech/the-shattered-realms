extends Button

const PANEL_ALT := Color("101621")
const BORDER := Color("2b3547")
const TEXT := Color("edf2f7")
const HOVER := Color("1d2635")

var overlay: Control


func _ready() -> void:
	text = "☰  MENU"
	focus_mode = Control.FOCUS_ALL
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 1000
	set_anchors_preset(Control.PRESET_TOP_RIGHT)
	offset_left = -145.0
	offset_right = -25.0
	offset_top = 18.0
	offset_bottom = 58.0

	var normal := StyleBoxFlat.new()
	normal.bg_color = PANEL_ALT
	normal.border_color = BORDER
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(8)
	var hover := normal.duplicate()
	hover.bg_color = HOVER
	add_theme_stylebox_override("normal", normal)
	add_theme_stylebox_override("hover", hover)
	add_theme_stylebox_override("pressed", hover)
	add_theme_color_override("font_color", TEXT)
	add_theme_font_size_override("font_size", 14)

	overlay = get_parent().get_node_or_null("MenuOverlay")
	pressed.connect(_open_menu)
	# Listen at the viewport input level too. This makes the menu reliable even
	# when Godot's embedded-game viewport or another full-screen Control consumes
	# the normal GUI button event before it reaches this Button.
	set_process_input(true)


func _process(_delta: float) -> void:
	if overlay == null:
		overlay = get_parent().get_node_or_null("MenuOverlay")
	if overlay != null and overlay.backdrop != null:
		visible = not overlay.backdrop.visible


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventMouseButton:
		var mouse_event := event as InputEventMouseButton
		if mouse_event.button_index == MOUSE_BUTTON_LEFT and mouse_event.pressed:
			if get_global_rect().has_point(mouse_event.position):
				_open_menu()
				get_viewport().set_input_as_handled()
	elif event is InputEventKey:
		var key_event := event as InputEventKey
		if key_event.pressed and not key_event.echo and key_event.keycode == KEY_M:
			_open_menu()
			get_viewport().set_input_as_handled()


func _open_menu() -> void:
	if overlay == null:
		overlay = get_parent().get_node_or_null("MenuOverlay")
	if overlay == null:
		return
	# The overlay intentionally ignores mouse input while closed so it does not
	# block the main game. Enable it before opening the modal menu.
	overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	overlay._open_menu()
