extends Control

const API_BASE := "http://127.0.0.1:8765"
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

const STATS := [
	"health", "resource", "strength", "dexterity", "agility", "constitution",
	"intelligence", "wisdom", "charisma", "speed", "defense", "luck", "magic"
]
const STAT_EFFECTS := {
	"health": "1 SP = +5 Max HP. More HP lets you take more damage before going down.",
	"resource": "1 SP = +5 Max Resource. Every 3 SP also gives +1 Resource recovery each combat round.",
	"strength": "Each SP builds physical power. Every 3 SP = +1 Strength checks and melee accuracy; every 6 SP = +1 melee damage.",
	"dexterity": "Each SP builds precision. Every 3 SP = +1 aiming, lockpicking, pickpocketing, ranged and finesse accuracy.",
	"agility": "Each SP builds mobility. Every 3 SP = +1 stealth, dodging and acrobatics; every 9 SP = +1 passive Armor Class.",
	"constitution": "Each SP builds toughness. Every 3 SP = +1 endurance checks; every 5 SP = +1% physical resistance; every 4 SP = +1% status resistance.",
	"intelligence": "Each SP builds reasoning. Every 3 SP = +1 investigation, engineering, hacking and knowledge checks.",
	"wisdom": "Each SP builds awareness. Every 3 SP = +1 perception, insight, survival and medicine checks.",
	"charisma": "Each SP builds social ability. Every 3 SP = +1 persuasion, deception, intimidation, leadership and trading checks.",
	"speed": "1 SP = +0.5 movement squares up to 30 SP, then +0.1. Every 3 SP = +1 initiative and Speed checks.",
	"defense": "Each SP strengthens guarding. Every 3 SP = +1 Armor Class while using the Defend action.",
	"luck": "Each SP builds toward fortunate outcomes. Every 3 SP = +1 Luck checks and +1% critical chance above the base 5%.",
	"magic": "Each SP builds magical control. Every 3 SP = +1 spell, power and Magic attack accuracy."
}

var http: HTTPRequest
var request_mode := ""
var busy := false

var shell_title: Label
var shell_subtitle: Label
var content: VBoxContainer
var scroll_view: ScrollContainer
var status_label: Label

var world_input: TextEdit
var name_input: LineEdit
var appearance_input: TextEdit
var ai_build_input: LineEdit
var remaining_label: Label
var derived_label: Label
var stat_controls: Dictionary = {}
var ability_checks: Array = []
var equipment_checks: Array = []
var kit_select: OptionButton
var kit_details: RichTextLabel
var armor_buttons: Array = []
var custom_armor_input: LineEdit
var finish_button: Button
var updating_stat_controls := false

var draft_world: Dictionary = {}
var draft_maps: Array = []
var draft_world_map_base64 := ""
var package: Dictionary = {}
var derived: Dictionary = {}
var draft_name := ""
var draft_appearance := ""
var draft_build_request := ""
var draft_stats: Dictionary = {}
var selected_ability_indexes: Array = []
var selected_equipment_indexes: Array = []
var selected_kit_index := 0
var armor_options: Array = []
var selected_armor_index := -1


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	z_index = 2000
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false
	_build_shell()
	http = HTTPRequest.new()
	http.request_completed.connect(_on_request_completed)
	add_child(http)


func begin_new_game(_state: Dictionary = {}) -> void:
	draft_world = {}
	draft_maps = []
	draft_world_map_base64 = ""
	package = {}
	derived = {}
	draft_name = ""
	draft_appearance = ""
	draft_build_request = ""
	draft_stats = {}
	selected_ability_indexes = []
	selected_equipment_indexes = []
	selected_kit_index = 0
	armor_options = []
	selected_armor_index = -1
	visible = true
	move_to_front()
	_show_world_prompt()


func _build_shell() -> void:
	var background := ColorRect.new()
	background.color = BG
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)

	var outer := MarginContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.add_theme_constant_override("margin_left", 38)
	outer.add_theme_constant_override("margin_right", 38)
	outer.add_theme_constant_override("margin_top", 28)
	outer.add_theme_constant_override("margin_bottom", 28)
	outer.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(outer)

	var panel := _panel(PANEL)
	outer.add_child(panel)

	var margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		margin.add_theme_constant_override(side, 28)
	margin.mouse_filter = Control.MOUSE_FILTER_PASS
	panel.add_child(margin)

	var root := VBoxContainer.new()
	root.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_theme_constant_override("separation", 10)
	root.mouse_filter = Control.MOUSE_FILTER_PASS
	margin.add_child(root)

	shell_title = Label.new()
	shell_title.text = "NEW ADVENTURE"
	shell_title.add_theme_font_size_override("font_size", 30)
	shell_title.add_theme_color_override("font_color", TEXT)
	root.add_child(shell_title)

	shell_subtitle = Label.new()
	shell_subtitle.add_theme_font_size_override("font_size", 15)
	shell_subtitle.add_theme_color_override("font_color", MUTED)
	root.add_child(shell_subtitle)
	root.add_child(HSeparator.new())

	var scroll := ScrollContainer.new()
	scroll_view = scroll
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.follow_focus = false
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	root.add_child(scroll)

	content = VBoxContainer.new()
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("separation", 12)
	content.mouse_filter = Control.MOUSE_FILTER_PASS
	scroll.add_child(content)

	root.add_child(HSeparator.new())
	status_label = Label.new()
	status_label.text = ""
	status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	status_label.add_theme_font_size_override("font_size", 14)
	status_label.add_theme_color_override("font_color", MUTED)
	root.add_child(status_label)


func _clear_content() -> void:
	for child in content.get_children():
		content.remove_child(child)
		child.queue_free()
	status_label.text = ""
	status_label.add_theme_color_override("font_color", MUTED)
	call_deferred("_scroll_to_top")


func _scroll_to_top() -> void:
	if scroll_view != null:
		scroll_view.scroll_vertical = 0


func _show_world_prompt() -> void:
	_clear_content()
	shell_title.text = "CREATE YOUR WORLD"
	shell_subtitle.text = "Step 1 of 4  •  The confirmed world controls the story, classes, powers, gear, enemies and economy."

	content.add_child(_heading("What kind of world do you want to play in?"))
	content.add_child(_muted("Describe anything you want: fantasy, modern crime, sci-fi, superhero, historical, post-apocalyptic, or something completely original."))

	world_input = TextEdit.new()
	world_input.custom_minimum_size = Vector2(0, 210)
	world_input.placeholder_text = "Example: A cyberpunk city controlled by rival megacorporations where illegal augmented fighters work as mercenaries..."
	world_input.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	world_input.add_theme_font_size_override("font_size", 17)
	content.add_child(world_input)

	var generate := _button("GENERATE WORLD", true)
	generate.custom_minimum_size.y = 50
	generate.pressed.connect(_generate_world)
	content.add_child(generate)


func _generate_world() -> void:
	if busy:
		return
	var prompt := world_input.text.strip_edges()
	if prompt.is_empty():
		_set_error("Describe the world you want first.")
		return
	_set_status("Generating your world and its first world map...")
	_post("/creation/world/generate", {"prompt": prompt}, "world_generate")


func _show_world_review() -> void:
	_clear_content()
	shell_title.text = "YOUR WORLD"
	shell_subtitle.text = "Step 1 of 4  •  Review the generated world before it becomes campaign canon."

	var summary := RichTextLabel.new()
	summary.fit_content = true
	summary.bbcode_enabled = false
	summary.add_theme_font_size_override("normal_font_size", 17)
	summary.add_theme_color_override("default_color", TEXT)
	summary.text = _world_text(draft_world)
	content.add_child(summary)

	content.add_child(HSeparator.new())
	content.add_child(_heading("YOUR FIRST WORLD MAP"))
	content.add_child(_muted("This shows known geography only. Hidden places and future discoveries stay secret."))
	if not draft_world_map_base64.is_empty():
		var map_preview := TextureRect.new()
		map_preview.custom_minimum_size = Vector2(0, 420)
		map_preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		map_preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		map_preview.texture = _texture_from_base64(draft_world_map_base64)
		content.add_child(map_preview)
	else:
		content.add_child(_muted("The map preview is not available, but the map will still be saved in your Map Gallery."))
	if draft_maps.size() > 1:
		content.add_child(_muted("This spacefaring world also includes a Universe Map in your Map Gallery."))

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	content.add_child(row)
	var change := _button("CHANGE DESCRIPTION", false)
	change.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	change.custom_minimum_size.y = 48
	change.pressed.connect(_show_world_prompt)
	row.add_child(change)
	var confirm := _button("USE THIS WORLD", true)
	confirm.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	confirm.custom_minimum_size.y = 48
	confirm.pressed.connect(_confirm_world)
	row.add_child(confirm)


func _confirm_world() -> void:
	if busy:
		return
	_set_status("Locking this world in as campaign canon...")
	_post("/creation/world/confirm", {}, "world_confirm")


func _show_identity() -> void:
	_clear_content()
	shell_title.text = "CREATE YOUR CHARACTER"
	shell_subtitle.text = "Step 2 of 4  •  Choose your identity and spend all 42 starting SP."

	var identity_grid := GridContainer.new()
	identity_grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	identity_grid.columns = 2
	identity_grid.add_theme_constant_override("h_separation", 14)
	identity_grid.add_theme_constant_override("v_separation", 10)
	content.add_child(identity_grid)

	var name_label := _label("Character name")
	name_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	name_label.custom_minimum_size.x = 160
	identity_grid.add_child(name_label)
	name_input = LineEdit.new()
	name_input.text = draft_name
	name_input.placeholder_text = "Traveler"
	name_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	name_input.custom_minimum_size.y = 42
	name_input.caret_blink = true
	identity_grid.add_child(name_input)

	content.add_child(_label("Appearance"))
	appearance_input = TextEdit.new()
	appearance_input.text = draft_appearance
	appearance_input.placeholder_text = "Describe what your character looks like..."
	appearance_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	appearance_input.custom_minimum_size = Vector2(0, 90)
	appearance_input.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	appearance_input.scroll_fit_content_height = false
	content.add_child(appearance_input)

	content.add_child(HSeparator.new())
	content.add_child(_heading("LET AI BUILD YOUR STATS (OPTIONAL)"))
	content.add_child(_muted("Describe the playstyle you want and the AI will spend exactly 42 SP for you. You can still adjust the result afterward."))
	var ai_row := HBoxContainer.new()
	ai_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ai_row.add_theme_constant_override("separation", 10)
	content.add_child(ai_row)
	ai_build_input = LineEdit.new()
	ai_build_input.text = draft_build_request
	ai_build_input.placeholder_text = "Example: a fast stealth fighter who uses precise ranged attacks"
	ai_build_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ai_build_input.custom_minimum_size.y = 44
	ai_row.add_child(ai_build_input)
	var ai_build := _button("BUILD MY STATS", false)
	ai_build.custom_minimum_size = Vector2(190, 44)
	ai_build.pressed.connect(_generate_ai_stats)
	ai_row.add_child(ai_build)

	content.add_child(HSeparator.new())
	var sp_row := HBoxContainer.new()
	sp_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_child(sp_row)
	var core_stats_heading := _heading("CORE STATS")
	core_stats_heading.autowrap_mode = TextServer.AUTOWRAP_OFF
	core_stats_heading.custom_minimum_size.x = 180
	sp_row.add_child(core_stats_heading)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sp_row.add_child(spacer)
	remaining_label = _heading("42 SP REMAINING")
	remaining_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	remaining_label.custom_minimum_size.x = 210
	remaining_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	sp_row.add_child(remaining_label)

	content.add_child(_muted("Most check bonuses gain about +1 for every 3 stat points early on. Natural stat cap is 100."))

	stat_controls.clear()
	var stat_list := VBoxContainer.new()
	stat_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	stat_list.add_theme_constant_override("separation", 8)
	content.add_child(stat_list)

	var stat_header := HBoxContainer.new()
	stat_header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	stat_header.add_theme_constant_override("separation", 14)
	stat_list.add_child(stat_header)
	var stat_header_name := _muted("STAT")
	stat_header_name.autowrap_mode = TextServer.AUTOWRAP_OFF
	stat_header_name.custom_minimum_size.x = 150
	stat_header.add_child(stat_header_name)
	var stat_header_sp := _muted("SP")
	stat_header_sp.autowrap_mode = TextServer.AUTOWRAP_OFF
	stat_header_sp.custom_minimum_size.x = 110
	stat_header.add_child(stat_header_sp)
	var stat_header_effect := _muted("EXACT EFFECT")
	stat_header_effect.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	stat_header.add_child(stat_header_effect)

	for stat in STATS:
		var stat_row := HBoxContainer.new()
		stat_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		stat_row.add_theme_constant_override("separation", 14)
		stat_list.add_child(stat_row)
		var stat_name := _label(stat.capitalize())
		stat_name.autowrap_mode = TextServer.AUTOWRAP_OFF
		stat_name.custom_minimum_size.x = 150
		stat_row.add_child(stat_name)
		var spin := SpinBox.new()
		spin.min_value = 0
		spin.max_value = 42
		spin.step = 1
		spin.allow_greater = false
		spin.custom_minimum_size = Vector2(110, 42)
		spin.value = int(draft_stats.get(stat, 0))
		spin.value_changed.connect(_on_stats_changed.bind(stat))
		stat_controls[stat] = spin
		stat_row.add_child(spin)
		var effect := _muted(str(STAT_EFFECTS.get(stat, "Every 3 SP improves this stat's checks by +1.")))
		effect.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		effect.custom_minimum_size.y = 42
		stat_row.add_child(effect)
		stat_list.add_child(HSeparator.new())

	derived_label = _muted("")
	content.add_child(derived_label)
	_update_stat_summary()

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	content.add_child(row)
	var back := _button("BACK TO WORLD", false)
	back.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	back.custom_minimum_size.y = 48
	back.pressed.connect(_show_world_review)
	row.add_child(back)
	var generate := _button("GENERATE CLASS & GEAR", true)
	generate.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	generate.custom_minimum_size.y = 48
	generate.pressed.connect(_generate_character)
	row.add_child(generate)


func _on_stats_changed(value: float, changed_stat: String) -> void:
	if updating_stat_controls:
		return
	var stats := _read_stats()
	var spent := 0
	for stat in STATS:
		spent += int(stats.get(stat, 0))
	if spent > 42:
		var changed_spin = stat_controls.get(changed_stat)
		if changed_spin != null:
			updating_stat_controls = true
			changed_spin.value = maxi(0, int(value) - (spent - 42))
			updating_stat_controls = false
	_update_stat_summary()


func _generate_ai_stats() -> void:
	if busy:
		return
	draft_build_request = ai_build_input.text.strip_edges()
	if draft_build_request.is_empty():
		_set_error("Describe the build you want the AI to make first.")
		return
	_set_status("The AI is building a legal 42-SP stat setup for your playstyle...")
	_post("/creation/stats/generate", {"description": draft_build_request}, "stats_generate")


func _read_stats() -> Dictionary:
	var result: Dictionary = {}
	for stat in STATS:
		var spin = stat_controls.get(stat)
		result[stat] = int(spin.value) if spin != null else 0
	return result


func _update_stat_summary() -> void:
	if remaining_label == null:
		return
	var stats := _read_stats()
	var spent := 0
	for stat in STATS:
		spent += int(stats.get(stat, 0))
	var remaining: int = maxi(0, 42 - spent)
	remaining_label.text = "%d SP REMAINING" % remaining
	remaining_label.add_theme_color_override("font_color", SUCCESS if remaining == 0 else TEXT)
	updating_stat_controls = true
	for stat in STATS:
		var spin = stat_controls.get(stat)
		if spin != null:
			spin.max_value = mini(42, int(spin.value) + remaining)
	updating_stat_controls = false
	if derived_label != null:
		var hp: int = maxi(1, int(stats.get("health", 0)) * 5)
		var resource := int(stats.get("resource", 0)) * 5
		derived_label.text = "Current preview:  %d Max HP  •  %d Max Resource  •  Crit starts at %d%%+  •  Speed controls movement/initiative" % [hp, resource, 5 + int(stats.get("luck", 0)) / 3]


func _generate_character() -> void:
	if busy:
		return
	draft_name = name_input.text.strip_edges()
	if draft_name.is_empty():
		draft_name = "Traveler"
	draft_appearance = appearance_input.text.strip_edges()
	draft_stats = _read_stats()
	var spent := 0
	for value in draft_stats.values():
		spent += int(value)
	if spent != 42:
		_set_error("Spend exactly 42 SP before continuing. You currently spent %d." % spent)
		return
	_set_status("Generating a world-fitting class, backstory, 6 Beginner abilities, starter kits and special gear...")
	_post("/creation/character/generate", {
		"name": draft_name,
		"appearance": draft_appearance,
		"stats": draft_stats
	}, "character_generate")


func _show_choices() -> void:
	_clear_content()
	shell_title.text = str(package.get("class_name", "YOUR CHARACTER")).to_upper()
	shell_subtitle.text = "Step 3 of 4  •  Choose 2 Beginner abilities, 1 starter kit, and 2 special equipment items."

	content.add_child(_heading("%s  •  Resource: %s" % [draft_name, str(package.get("resource_name", "Resource"))]))
	var backstory := _muted(str(package.get("backstory", "")))
	backstory.add_theme_font_size_override("font_size", 16)
	content.add_child(backstory)
	if not derived.is_empty():
		content.add_child(_muted("Max HP %d  •  Max %s %d  •  Regen %d/round  •  Movement %d" % [
			int(derived.get("max_hp", 0)), str(package.get("resource_name", "Resource")),
			int(derived.get("max_resource", 0)), int(derived.get("resource_regen", 0)), int(derived.get("movement", 0))
		]))

	content.add_child(HSeparator.new())
	content.add_child(_heading("BEGINNER ABILITIES — CHOOSE 2"))
	ability_checks.clear()
	var abilities = package.get("abilities") if package.get("abilities") is Array else []
	for i in range(abilities.size()):
		var ability = abilities[i]
		var check := CheckBox.new()
		check.text = _ability_text(ability)
		check.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		check.custom_minimum_size.y = 44
		check.button_pressed = selected_ability_indexes.has(i)
		ability_checks.append(check)
		content.add_child(check)

	content.add_child(HSeparator.new())
	content.add_child(_heading("STARTER KIT — CHOOSE 1"))
	kit_select = OptionButton.new()
	kit_select.custom_minimum_size.y = 44
	var kits = package.get("starter_kits") if package.get("starter_kits") is Array else []
	for i in range(kits.size()):
		var kit = kits[i]
		kit_select.add_item("%s  •  Starts with %s" % [str(kit.get("name", "Kit")), _kit_money_text(kit)])
	kit_select.select(clamp(selected_kit_index, 0, max(0, kits.size() - 1)))
	kit_select.item_selected.connect(_on_kit_selected)
	content.add_child(kit_select)
	kit_details = RichTextLabel.new()
	kit_details.fit_content = true
	kit_details.bbcode_enabled = false
	kit_details.add_theme_font_size_override("normal_font_size", 15)
	kit_details.add_theme_color_override("default_color", MUTED)
	content.add_child(kit_details)
	_update_kit_details(kit_select.selected)

	content.add_child(HSeparator.new())
	content.add_child(_heading("SPECIAL STARTER EQUIPMENT — CHOOSE 2"))
	equipment_checks.clear()
	var equipment = package.get("special_equipment") if package.get("special_equipment") is Array else []
	for i in range(equipment.size()):
		var item = equipment[i]
		var check := CheckBox.new()
		check.text = _item_text(item)
		check.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		check.custom_minimum_size.y = 42
		check.button_pressed = selected_equipment_indexes.has(i)
		equipment_checks.append(check)
		content.add_child(check)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	content.add_child(row)
	var back := _button("BACK TO STATS", false)
	back.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	back.custom_minimum_size.y = 48
	back.pressed.connect(_show_identity)
	row.add_child(back)
	var armor := _button("CONTINUE TO ARMOR", true)
	armor.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	armor.custom_minimum_size.y = 48
	armor.pressed.connect(_continue_to_armor)
	row.add_child(armor)


func _on_kit_selected(index: int) -> void:
	selected_kit_index = index
	_update_kit_details(index)


func _update_kit_details(index: int) -> void:
	if kit_details == null:
		return
	var kits = package.get("starter_kits") if package.get("starter_kits") is Array else []
	if index < 0 or index >= kits.size():
		kit_details.text = ""
		return
	var kit = kits[index]
	var lines: Array[String] = []
	for item in kit.get("items", []):
		lines.append("• " + _item_text(item))
	kit_details.text = "\n".join(lines)


func _continue_to_armor() -> void:
	if busy:
		return
	selected_ability_indexes.clear()
	for i in range(ability_checks.size()):
		if ability_checks[i].button_pressed:
			selected_ability_indexes.append(i)
	selected_equipment_indexes.clear()
	for i in range(equipment_checks.size()):
		if equipment_checks[i].button_pressed:
			selected_equipment_indexes.append(i)
	selected_kit_index = kit_select.selected
	if selected_ability_indexes.size() != 2:
		_set_error("Choose exactly 2 Beginner abilities.")
		return
	if selected_equipment_indexes.size() != 2:
		_set_error("Choose exactly 2 special equipment items.")
		return
	_set_status("Generating three Beginner armor sets that fit your world and character...")
	_post("/creation/armor/generate", {}, "armor_generate")


func _show_armor() -> void:
	_clear_content()
	shell_title.text = "STARTING ARMOR"
	shell_subtitle.text = "Step 4 of 4  •  Armor is a separate health bar. Starting sets total only 10–20 Armor HP."
	content.add_child(_muted("Choose one AI-generated set, or describe a custom look/build below. Custom armor is still balanced to Beginner strength."))
	content.add_child(_muted("ARMOR WEIGHT: 0–13 has no movement penalty, 14–21 gives -1 Movement, 22–29 gives -2, and 30+ gives -3. Weight does not change Armor HP or Armor Class."))

	armor_buttons.clear()
	var group := ButtonGroup.new()
	for i in range(armor_options.size()):
		var armor = armor_options[i]
		var button := CheckBox.new()
		button.button_group = group
		button.text = _armor_text(armor)
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.custom_minimum_size.y = 76
		button.button_pressed = i == selected_armor_index
		button.pressed.connect(_select_armor.bind(i))
		armor_buttons.append(button)
		content.add_child(button)

	content.add_child(HSeparator.new())
	content.add_child(_heading("CUSTOM ARMOR (OPTIONAL)"))
	custom_armor_input = LineEdit.new()
	custom_armor_input.placeholder_text = "Example: lightweight black tactical armor built for speed and stealth"
	custom_armor_input.custom_minimum_size.y = 42
	content.add_child(custom_armor_input)
	var custom_row := HBoxContainer.new()
	custom_row.add_theme_constant_override("separation", 10)
	content.add_child(custom_row)
	var custom := _button("GENERATE CUSTOM ARMOR", false)
	custom.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	custom.custom_minimum_size.y = 44
	custom.pressed.connect(_generate_custom_armor)
	custom_row.add_child(custom)
	var three := _button("SHOW 3 AI OPTIONS", false)
	three.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	three.custom_minimum_size.y = 44
	three.pressed.connect(_generate_three_armor)
	custom_row.add_child(three)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	content.add_child(row)
	var back := _button("BACK TO GEAR", false)
	back.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	back.custom_minimum_size.y = 48
	back.pressed.connect(_show_choices)
	row.add_child(back)
	finish_button = _button("BEGIN ADVENTURE", true)
	finish_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	finish_button.custom_minimum_size.y = 48
	finish_button.visible = selected_armor_index >= 0
	finish_button.pressed.connect(_finalize_character)
	row.add_child(finish_button)


func _select_armor(index: int) -> void:
	selected_armor_index = index
	if finish_button != null:
		finish_button.visible = true


func _generate_custom_armor() -> void:
	if busy:
		return
	var request := custom_armor_input.text.strip_edges()
	if request.is_empty():
		_set_error("Describe the custom armor you want first.")
		return
	selected_armor_index = -1
	_set_status("Turning your description into balanced Beginner armor...")
	_post("/creation/armor/generate", {"custom_request": request}, "armor_generate")


func _generate_three_armor() -> void:
	if busy:
		return
	selected_armor_index = -1
	_set_status("Generating three Beginner armor choices...")
	_post("/creation/armor/generate", {}, "armor_generate")


func _finalize_character() -> void:
	if busy:
		return
	if armor_options.is_empty() or selected_armor_index < 0 or selected_armor_index >= armor_options.size():
		_set_error("Choose your starting armor before beginning the adventure.")
		return
	_set_status("Finishing your character and generating the opening scene...")
	_post("/creation/finalize", {
		"ability_indexes": selected_ability_indexes,
		"kit_index": selected_kit_index,
		"equipment_indexes": selected_equipment_indexes,
		"armor_index": selected_armor_index
	}, "finalize")


func _post(path: String, body: Dictionary, mode: String) -> void:
	if busy:
		return
	busy = true
	request_mode = mode
	var headers := PackedStringArray(["Content-Type: application/json"])
	var error := http.request(API_BASE + path, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	if error != OK:
		busy = false
		_set_error("Could not contact the backend.")


func _on_request_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	busy = false
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if result != HTTPRequest.RESULT_SUCCESS:
		_set_error("Backend request failed.")
		return
	if not parsed is Dictionary:
		_set_error("Backend returned invalid data.")
		return
	var payload: Dictionary = parsed
	if response_code < 200 or response_code >= 300 or not payload.get("ok", false):
		_set_error(str(payload.get("error", "Character creation request failed.")))
		return

	match request_mode:
		"world_generate":
			draft_world = payload.get("world", {}) if payload.get("world", {}) is Dictionary else {}
			draft_maps = payload.get("maps", []) if payload.get("maps", []) is Array else []
			var map_value = payload.get("world_map_base64")
			draft_world_map_base64 = "" if map_value == null else str(map_value)
			_show_world_review()
		"world_confirm":
			_show_identity()
		"stats_generate":
			var allocation = payload.get("stats", {}) if payload.get("stats", {}) is Dictionary else {}
			updating_stat_controls = true
			for stat in STATS:
				var spin = stat_controls.get(stat)
				if spin != null:
					spin.max_value = 42
			for stat in STATS:
				var spin = stat_controls.get(stat)
				if spin != null:
					spin.value = int(allocation.get(stat, 0))
			updating_stat_controls = false
			draft_stats = _read_stats()
			_update_stat_summary()
			_set_status("AI build applied. All 42 SP are spent, and you can still adjust the stats.")
		"character_generate":
			package = payload.get("package", {}) if payload.get("package", {}) is Dictionary else {}
			derived = payload.get("derived", {}) if payload.get("derived", {}) is Dictionary else {}
			selected_ability_indexes = []
			selected_equipment_indexes = []
			selected_kit_index = 0
			_show_choices()
		"armor_generate":
			armor_options = payload.get("armor_options", []) if payload.get("armor_options", []) is Array else []
			selected_armor_index = -1
			_show_armor()
		"finalize":
			_finish_into_game(payload)


func _finish_into_game(payload: Dictionary) -> void:
	var parent = get_parent()
	if parent == null:
		return
	parent.latest_state = payload.get("state", {}) if payload.get("state", {}) is Dictionary else {}
	parent.story_history.clear()
	parent.story_history.append("GM: " + str(payload.get("narration", "Your adventure begins.")))
	parent._update_player_panel()
	parent._refresh_story()
	parent._set_suggestions(payload.get("suggested_actions", []))
	parent._show_context("player")
	parent.connection_label.text = "● BACKEND CONNECTED"
	parent.connection_label.add_theme_color_override("font_color", SUCCESS)
	if parent.has_method("_enter_world_mode"):
		parent.call("_enter_world_mode", payload)
	visible = false


func _set_status(message: String) -> void:
	status_label.text = message
	status_label.add_theme_color_override("font_color", MUTED)


func _set_error(message: String) -> void:
	status_label.text = "⚠ " + message
	status_label.add_theme_color_override("font_color", DANGER)


func _world_text(world: Dictionary) -> String:
	var lines: Array[String] = []
	lines.append(str(world.get("name", "Untitled World")).to_upper())
	var premise := str(world.get("premise", "")).strip_edges()
	if not premise.is_empty():
		lines.append(premise)
	var details: Array[String] = []
	for pair in [["Genre", "genre"], ["Era", "era"], ["Tone", "tone"]]:
		var value = world.get(pair[1])
		if value != null and not str(value).is_empty():
			details.append("%s: %s" % [pair[0], str(value)])
	if not details.is_empty():
		lines.append("\n" + "  •  ".join(details))
	lines.append("\nLocations, factions, conflicts, and secrets will be discovered during the adventure.")
	return "\n".join(lines)


func _texture_from_base64(encoded: String) -> ImageTexture:
	if encoded.is_empty():
		return null
	var raw := Marshalls.base64_to_raw(encoded)
	if raw.size() < 4:
		return null
	var image := Image.new()
	var error := ERR_FILE_UNRECOGNIZED
	if raw.size() >= 8 and raw[0] == 0x89 and raw[1] == 0x50 and raw[2] == 0x4e and raw[3] == 0x47:
		error = image.load_png_from_buffer(raw)
	elif raw[0] == 0xff and raw[1] == 0xd8 and raw[2] == 0xff:
		error = image.load_jpg_from_buffer(raw)
	elif raw.size() >= 12 and raw[0] == 0x52 and raw[1] == 0x49 and raw[2] == 0x46 and raw[3] == 0x46 and raw[8] == 0x57 and raw[9] == 0x45 and raw[10] == 0x42 and raw[11] == 0x50:
		error = image.load_webp_from_buffer(raw)
	if error != OK:
		return null
	return ImageTexture.create_from_image(image)


func _ability_text(ability) -> String:
	if not ability is Dictionary:
		return str(ability)
	var parts: Array[String] = [str(ability.get("name", "Ability"))]
	var desc := str(ability.get("description", ""))
	if not desc.is_empty():
		parts.append(desc)
	if ability.get("damage"):
		parts.append("Damage " + str(ability.get("damage")))
	if ability.get("healing"):
		parts.append("Healing " + str(ability.get("healing")))
	if ability.get("shield"):
		parts.append("Shield " + str(ability.get("shield")))
	if ability.get("movement_squares"):
		parts.append("Move " + str(ability.get("movement_squares")))
	parts.append("Range " + str(ability.get("range", 0)))
	parts.append("Cost %s %s" % [str(ability.get("resource_cost", 0)), str(package.get("resource_name", "Resource"))])
	return " — ".join(parts)


func _item_text(item) -> String:
	if not item is Dictionary:
		return str(item)
	var parts: Array[String] = [str(item.get("name", "Item"))]
	var desc := str(item.get("description", ""))
	if not desc.is_empty():
		parts.append(desc)
	if item.get("damage"):
		parts.append("Damage " + str(item.get("damage")))
	if item.get("shield"):
		parts.append("Shield HP " + str(item.get("shield")))
	if item.get("healing"):
		parts.append("Healing " + str(item.get("healing")))
	if item.get("range") != null:
		parts.append("Range " + str(item.get("range")))
	if item.get("effect"):
		parts.append(str(item.get("effect")))
	return " — ".join(parts)


func _kit_money_text(kit: Dictionary) -> String:
	var amount := int(kit.get("starting_currency", 20))
	var world_currency := str(draft_world.get("currency_name", "currency"))
	var symbol := str(draft_world.get("currency_symbol", ""))
	if not symbol.is_empty():
		return "%s%d" % [symbol, amount]
	return "%d %s" % [amount, world_currency]


func _armor_text(armor) -> String:
	if not armor is Dictionary:
		return str(armor)
	var pieces_text: Array[String] = []
	for piece in armor.get("pieces", []):
		if not piece is Dictionary:
			continue
		var bonus := ""
		var stat_bonus = piece.get("stat_bonus")
		if stat_bonus is Dictionary:
			bonus = " +%s %s" % [str(stat_bonus.get("amount", 0)), str(stat_bonus.get("stat", "")).capitalize()]
		pieces_text.append("%s %s Armor%s" % [str(piece.get("slot", "")).capitalize(), str(piece.get("armor_hp", 0)), bonus])
	var total_weight := _armor_weight(armor)
	return "%s — %s\nTotal Armor %s  •  Weight %s (%s)\n%s" % [
		str(armor.get("name", "Armor Set")), str(armor.get("description", "")),
		str(armor.get("total_armor", 0)), total_weight, _armor_weight_effect(total_weight), "  |  ".join(pieces_text)
	]


func _armor_weight_effect(weight: int) -> String:
	if weight >= 30:
		return "-3 Movement"
	if weight >= 22:
		return "-2 Movement"
	if weight >= 14:
		return "-1 Movement"
	return "No Movement penalty"


func _armor_weight(armor: Dictionary) -> int:
	var total := 0
	for piece in armor.get("pieces", []):
		if piece is Dictionary:
			total += int(piece.get("weight", 0))
	return total


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


func _heading(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 19)
	label.add_theme_color_override("font_color", TEXT)
	return label


func _label(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 15)
	label.add_theme_color_override("font_color", TEXT)
	return label


func _muted(value: String) -> Label:
	var label := Label.new()
	label.text = value
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 14)
	label.add_theme_color_override("font_color", MUTED)
	return label
