extends Control

signal closed
signal api_request(endpoint: String, payload: Dictionary, mode: String)

const PANEL := Color("151b26")
const PANEL_ALT := Color("101621")
const BORDER := Color("2b3547")
const TEXT := Color("edf2f7")
const MUTED := Color("94a3b8")
const ACCENT := Color("8b5cf6")
const ACCENT_HOVER := Color("a78bfa")
const SUCCESS := Color("34d399")
const DANGER := Color("fb7185")

const CORE_STATS: Array[String] = [
	"health", "resource", "strength", "dexterity", "agility", "constitution",
	"intelligence", "wisdom", "charisma", "speed", "defense", "luck", "magic",
]
const ARMOR_SLOTS: Array[String] = ["helmet", "breastplate", "pants", "gloves", "boots"]
const STAT_DESCRIPTIONS := {
	"health": "Each point adds 5 maximum HP.",
	"resource": "Each point adds 5 maximum class Resource. Every complete 3 points also adds +1 Resource regeneration per round.",
	"strength": "Every complete 3 points adds +1 to Strength checks and melee accuracy. Every 6 points adds +1 melee damage.",
	"dexterity": "Every complete 3 points adds +1 to Dexterity checks, aiming, precision, lockpicking, and ranged accuracy.",
	"agility": "Every complete 3 points adds +1 to Agility checks such as stealth, acrobatics, and evasion. It also contributes to passive AC.",
	"constitution": "Every complete 3 points adds +1 to Constitution checks. It also improves physical/status resistance and contributes to passive AC.",
	"intelligence": "Every complete 3 points adds +1 to Intelligence checks such as investigation, engineering, research, and technical work.",
	"wisdom": "Every complete 3 points adds +1 to Wisdom checks such as perception, insight, survival, and medicine.",
	"charisma": "Every complete 3 points adds +1 to Charisma checks such as persuasion, deception, intimidation, and haggling.",
	"speed": "Adds movement gradually, and every complete 3 points adds +1 initiative. It also contributes to passive AC.",
	"defense": "Every complete 3 points adds +1 AC while using the Defend action.",
	"luck": "Every complete 3 points adds +1% critical-hit chance and +1 to Luck checks.",
	"magic": "Every complete 3 points adds +1 to Magic checks and magical-attack accuracy.",
}

var game_state: Dictionary = {}
var ability_choices: Array = []
var active_tab := "abilities"
var header_name: Label
var point_summary: Label
var status_label: Label
var content_box: VBoxContainer
var tab_buttons: Dictionary = {}
var portrait_texture: ImageTexture


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 100
	_build()


func open_with_state(new_state: Dictionary) -> void:
	game_state = new_state.duplicate(true)
	visible = true
	_render()
	if portrait_texture == null:
		call_deferred("_request", "/character/portrait/load", {}, "character_portrait")


func apply_payload(payload: Dictionary) -> void:
	var raw_state = payload.get("state", {})
	if raw_state is Dictionary:
		game_state = raw_state.duplicate(true)
	var raw_choices = payload.get("ability_choices")
	if raw_choices is Array:
		ability_choices = raw_choices.duplicate(true)
	var portrait_base64 := str(payload.get("portrait_base64", ""))
	if not portrait_base64.is_empty():
		_load_portrait_texture(portrait_base64)
	elif "portrait_available" in payload and not bool(payload.get("portrait_available", false)):
		portrait_texture = null
	var message := str(payload.get("message", ""))
	set_status(message, false)
	_render()
	var equipment_change = payload.get("equipment_change")
	if equipment_change is Dictionary:
		var changed_slot := str(equipment_change.get("slot", ""))
		var change_type := "unequip" if equipment_change.has("unequipped") else "equip"
		if changed_slot.is_empty():
			var equipped_piece = equipment_change.get("equipped")
			if equipped_piece is Dictionary:
				changed_slot = str(equipped_piece.get("slot", ""))
		call_deferred("_refresh_art_after_armor_change", changed_slot, change_type)


func set_status(message: String, is_error: bool = false) -> void:
	if not is_instance_valid(status_label):
		return
	status_label.text = message
	status_label.add_theme_color_override("font_color", DANGER if is_error else SUCCESS)


func _build() -> void:
	var shade := ColorRect.new()
	shade.color = Color(0.01, 0.02, 0.04, 0.97)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(shade)

	var outer := MarginContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.add_theme_constant_override("margin_left", 34)
	outer.add_theme_constant_override("margin_right", 34)
	outer.add_theme_constant_override("margin_top", 26)
	outer.add_theme_constant_override("margin_bottom", 26)
	add_child(outer)

	var panel := _panel(PANEL_ALT)
	outer.add_child(panel)
	var margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		margin.add_theme_constant_override(side, 20)
	panel.add_child(margin)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 12)
	margin.add_child(root)

	var header := HBoxContainer.new()
	header.custom_minimum_size.y = 52
	root.add_child(header)
	header_name = _label("CHARACTER HUB", 25, TEXT)
	header.add_child(header_name)
	var header_spacer := Control.new()
	header_spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(header_spacer)
	point_summary = _label("SP 0  •  AP 0", 16, ACCENT_HOVER)
	header.add_child(point_summary)
	var close_button := _button("CLOSE", false)
	close_button.custom_minimum_size = Vector2(110, 40)
	close_button.pressed.connect(_close)
	header.add_child(close_button)

	var tabs := HBoxContainer.new()
	tabs.add_theme_constant_override("separation", 8)
	root.add_child(tabs)
	for entry in [["ABILITIES", "abilities"], ["STATS & SKILLS", "stats"], ["ARMOR", "armor"]]:
		var tab := _button(str(entry[0]), false)
		tab.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tab.custom_minimum_size.y = 42
		tab.pressed.connect(_select_tab.bind(str(entry[1])))
		tabs.add_child(tab)
		tab_buttons[str(entry[1])] = tab

	status_label = _label("", 14, SUCCESS)
	status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	root.add_child(status_label)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	root.add_child(scroll)
	content_box = VBoxContainer.new()
	content_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content_box.add_theme_constant_override("separation", 12)
	scroll.add_child(content_box)


func _close() -> void:
	visible = false
	closed.emit()


func _select_tab(tab_name: String) -> void:
	active_tab = tab_name
	set_status("")
	_render()


func _render() -> void:
	if not is_instance_valid(content_box):
		return
	for child in content_box.get_children():
		child.queue_free()
	var player: Dictionary = game_state.get("player", {}) if game_state.get("player", {}) is Dictionary else {}
	header_name.text = "%s  •  CHARACTER HUB" % str(player.get("name", "Traveler")).to_upper()
	point_summary.text = "SP %d   •   AP %d   •   LEVEL %d" % [
		int(player.get("skill_points_unspent", 0)), int(player.get("ability_points", 0)), int(player.get("level", 1))
	]
	for tab_name in tab_buttons:
		var button: Button = tab_buttons[tab_name]
		button.add_theme_color_override("font_color", ACCENT_HOVER if tab_name == active_tab else TEXT)
	match active_tab:
		"stats":
			_render_stats(player)
		"armor":
			_render_armor(player)
		_:
			_render_abilities(player)


func _render_abilities(player: Dictionary) -> void:
	_add_section_heading("EQUIPPED ABILITIES", "Abilities are ready for combat. You can equip up to four; learning a fifth requires replacing one.")
	var equipped = player.get("equipped_abilities", [])
	if not equipped is Array or equipped.is_empty():
		content_box.add_child(_muted("No abilities are equipped."))
	else:
		for ability in equipped:
			if ability is Dictionary:
				content_box.add_child(_ability_card(ability, false, -1, player))

	var divider := HSeparator.new()
	content_box.add_child(divider)
	_add_section_heading("SPEND AP", "AP is stored until you choose an ability. Generated choices match your class, world, level, and build.")
	var combat_locked := _combat_active()
	var generate := _button("GENERATE 6 ABILITY OPTIONS", true)
	generate.custom_minimum_size.y = 46
	generate.disabled = combat_locked
	generate.pressed.connect(_request.bind("/character/abilities/generate", {}, "character_abilities"))
	content_box.add_child(generate)
	if combat_locked:
		content_box.add_child(_warning("Ability changes are locked during combat."))
	if ability_choices.is_empty():
		content_box.add_child(_muted("Generate options when you are ready to spend AP."))
	else:
		for index in range(ability_choices.size()):
			var choice = ability_choices[index]
			if choice is Dictionary:
				content_box.add_child(_ability_card(choice, true, index, player))


func _ability_card(ability: Dictionary, learnable: bool, choice_index: int, player: Dictionary) -> PanelContainer:
	var card := _panel(PANEL)
	var margin := _card_margin()
	card.add_child(margin)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 7)
	margin.add_child(box)
	var top := HBoxContainer.new()
	box.add_child(top)
	var ability_name_label := _label(str(ability.get("name", "Ability")), 18, TEXT)
	ability_name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(ability_name_label)
	var tier := str(ability.get("tier", "beginner")).capitalize()
	var ap_cost := int(ability.get("ability_point_cost", 1))
	top.add_child(_label("%s  •  %d AP" % [tier, ap_cost], 14, ACCENT_HOVER))
	var description := _label(str(ability.get("description", "")), 14, MUTED)
	description.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(description)
	box.add_child(_label(_ability_mechanics(ability, str(player.get("resource_name", "Resource"))), 14, TEXT))
	if learnable:
		var controls := HBoxContainer.new()
		controls.add_theme_constant_override("separation", 8)
		box.add_child(controls)
		var replacement := OptionButton.new()
		replacement.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var equipped = player.get("equipped_abilities", [])
		if equipped is Array and equipped.size() >= 4:
			replacement.add_item("Choose an equipped ability to replace", -1)
			for index in range(equipped.size()):
				var current = equipped[index]
				if current is Dictionary:
					replacement.add_item("Replace %s" % str(current.get("name", "Ability")), index)
		else:
			replacement.add_item("Open ability slot", -1)
		controls.add_child(replacement)
		var learn := _button("LEARN", true)
		learn.custom_minimum_size = Vector2(120, 40)
		learn.disabled = int(player.get("ability_points", 0)) < ap_cost or _combat_active()
		learn.pressed.connect(_learn_choice.bind(choice_index, replacement))
		controls.add_child(learn)
	return card


func _ability_mechanics(ability: Dictionary, resource_name: String) -> String:
	var parts: Array[String] = []
	for entry in [
		["damage", "Damage"], ["healing", "Healing"], ["shield", "Shield"],
		["movement_squares", "Move"], ["target_count", "Targets"],
		["area", "Area"], ["duration", "Duration"], ["status_effect", "Status"],
		["stat_modifier", "Modifier"],
	]:
		var value = ability.get(str(entry[0]))
		if value not in [null, "", 0, "0"]:
			parts.append("%s %s" % [str(entry[1]), str(value)])
	parts.append("Target %s" % str(ability.get("target", "self")).capitalize())
	parts.append("Range %d" % int(ability.get("range", 0)))
	parts.append("Cost %d %s" % [int(ability.get("resource_cost", 0)), resource_name])
	if bool(ability.get("requires_attack_roll", false)):
		parts.append("Attack roll: %s" % str(ability.get("attack_attribute", "core stat")).capitalize())
	return "  •  ".join(parts)


func _learn_choice(choice_index: int, replacement: OptionButton) -> void:
	var forget_index: int = replacement.get_selected_id()
	_request("/character/abilities/learn", {"choice_index": choice_index, "forget_index": forget_index}, "character_abilities")


func _render_stats(player: Dictionary) -> void:
	var sp := int(player.get("skill_points_unspent", 0))
	_add_section_heading("CORE STATS  •  %d SP AVAILABLE" % sp, "Spend one SP at a time. Every 3 points normally adds +1 to checks; some stats also improve HP, movement, initiative, resources, or combat rules.")
	var stats: Dictionary = player.get("stats", {}) if player.get("stats", {}) is Dictionary else {}
	var armor_bonuses: Dictionary = player.get("armor_stat_bonuses", {}) if player.get("armor_stat_bonuses", {}) is Dictionary else {}
	for stat in CORE_STATS:
		var row := _panel(PANEL)
		var margin := _card_margin()
		row.add_child(margin)
		var horizontal := HBoxContainer.new()
		horizontal.add_theme_constant_override("separation", 12)
		margin.add_child(horizontal)
		var text_box := VBoxContainer.new()
		text_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		horizontal.add_child(text_box)
		var value := int(stats.get(stat, 0))
		var armor_bonus := int(armor_bonuses.get(stat, 0))
		var effective_value := value + armor_bonus
		var armor_note := "  (+%d ARMOR)" % armor_bonus if armor_bonus > 0 else ""
		text_box.add_child(_label("%s  %d%s   •   CHECK BONUS %s" % [stat.to_upper(), value, armor_note, _signed(_attribute_bonus(effective_value))], 16, TEXT))
		var description := _label(str(STAT_DESCRIPTIONS.get(stat, "Core character stat.")), 13, MUTED)
		description.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		text_box.add_child(description)
		var add_button := _button("+1 SP", true)
		add_button.custom_minimum_size = Vector2(90, 42)
		add_button.disabled = sp <= 0 or value >= 100 or _combat_active()
		add_button.pressed.connect(_request.bind("/character/stats/spend", {"stat": stat, "amount": 1}, "character_stats"))
		horizontal.add_child(add_button)

	var divider := HSeparator.new()
	content_box.add_child(divider)
	_add_section_heading("TRAINED SKILLS", "These bonuses are added on top of the governing core-stat bonus whenever that skill is used.")
	var skills: Dictionary = player.get("skills", {}) if player.get("skills", {}) is Dictionary else {}
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	content_box.add_child(grid)
	var skill_names: Array = skills.keys()
	skill_names.sort()
	for skill_name in skill_names:
		var skill_card := _panel(PANEL)
		skill_card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var skill_margin := MarginContainer.new()
		for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
			skill_margin.add_theme_constant_override(side, 10)
		skill_card.add_child(skill_margin)
		skill_margin.add_child(_label("%s   %s" % [str(skill_name).replace("_", " ").capitalize(), _signed(int(skills.get(skill_name, 0)))], 13, TEXT))
		grid.add_child(skill_card)


func _render_armor(player: Dictionary) -> void:
	var equipped: Dictionary = player.get("equipped_armor", {}) if player.get("equipped_armor", {}) is Dictionary else {}
	var armor := int(player.get("armor", 0))
	var max_armor := int(player.get("max_armor", armor))
	var weight := int(player.get("armor_weight", 0))
	var penalty := 3 if weight >= 30 else (2 if weight >= 22 else (1 if weight >= 14 else 0))
	_add_section_heading("ARMOR LOADOUT", "Armor absorbs damage before HP. Heavier protection can reduce movement, and broken pieces stop granting stat bonuses.")
	content_box.add_child(_label("ARMOR %d/%d   •   WEIGHT %d   •   MOVEMENT %d   •   WEIGHT PENALTY -%d" % [armor, max_armor, weight, int(player.get("movement", 1)), penalty], 16, ACCENT_HOVER))

	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 14)
	content_box.add_child(columns)
	var profile := _panel(PANEL)
	profile.custom_minimum_size.x = 390
	columns.add_child(profile)
	var profile_margin := _card_margin()
	profile.add_child(profile_margin)
	var profile_box := VBoxContainer.new()
	profile_box.add_theme_constant_override("separation", 9)
	profile_margin.add_child(profile_box)
	profile_box.add_child(_label("CHARACTER VISUAL PROFILE", 17, TEXT))
	var appearance := str(player.get("appearance", "No appearance description saved.")).strip_edges()
	if portrait_texture != null:
		var portrait_image := TextureRect.new()
		portrait_image.texture = portrait_texture
		portrait_image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		portrait_image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		portrait_image.custom_minimum_size.y = 330
		profile_box.add_child(portrait_image)
	else:
		var portrait_placeholder := ColorRect.new()
		portrait_placeholder.color = Color("0d1420")
		portrait_placeholder.custom_minimum_size.y = 260
		profile_box.add_child(portrait_placeholder)
		var portrait_text := _label("%s\n%s  •  %s\n\n%s" % [
			str(player.get("name", "Traveler")).to_upper(), str(player.get("species", "Unknown species")),
			str(player.get("class", "Unassigned")), appearance
		], 15, TEXT)
		portrait_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		portrait_text.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		portrait_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		portrait_text.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_MINSIZE, 12)
		portrait_placeholder.add_child(portrait_text)
	var art_button := _button("REFRESH CHARACTER ART" if portrait_texture != null else "GENERATE CHARACTER ART", true)
	art_button.custom_minimum_size.y = 44
	art_button.pressed.connect(_request.bind("/character/portrait/generate", {}, "character_portrait"))
	profile_box.add_child(art_button)
	profile_box.add_child(_muted("Art uses the saved appearance, world, class, and currently equipped armor. It only calls image generation when you press the button."))
	for slot in ARMOR_SLOTS:
		var piece = equipped.get(slot)
		var slot_row := HBoxContainer.new()
		slot_row.add_theme_constant_override("separation", 8)
		profile_box.add_child(slot_row)
		var slot_text := "%s: EMPTY" % slot.to_upper()
		if piece is Dictionary:
			slot_text = "%s: %s  •  %d/%d" % [slot.to_upper(), str(piece.get("name", "Armor")), int(piece.get("armor_hp", 0)), int(piece.get("max_armor_hp", piece.get("armor_hp", 0)))]
		var slot_label := _label(slot_text, 13, TEXT)
		slot_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		slot_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		slot_row.add_child(slot_label)
		if piece is Dictionary:
			var unequip := _button("UNEQUIP", false)
			unequip.disabled = _combat_active()
			unequip.pressed.connect(_request.bind("/character/armor/unequip", {"slot": slot}, "character_armor"))
			slot_row.add_child(unequip)

	var inventory_column := VBoxContainer.new()
	inventory_column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	inventory_column.add_theme_constant_override("separation", 9)
	columns.add_child(inventory_column)
	inventory_column.add_child(_label("OWNED ARMOR", 17, TEXT))
	var inventory = player.get("inventory", [])
	var found_armor := false
	if inventory is Array:
		for index in range(inventory.size()):
			var item = inventory[index]
			if not item is Dictionary or str(item.get("type", "")).to_lower() != "armor":
				continue
			found_armor = true
			inventory_column.add_child(_armor_item_card(item, index, equipped))
	if not found_armor:
		inventory_column.add_child(_muted("You do not own any armor pieces yet."))
	if _combat_active():
		inventory_column.add_child(_warning("Armor cannot be changed during combat."))


func _armor_item_card(item: Dictionary, inventory_index: int, equipped: Dictionary) -> PanelContainer:
	var card := _panel(PANEL)
	var margin := _card_margin()
	card.add_child(margin)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	margin.add_child(row)
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(info)
	var slot := str(item.get("slot", "breastplate")).to_lower()
	var current = equipped.get(slot)
	var is_equipped := current is Dictionary and str(current.get("name", "")) == str(item.get("name", ""))
	var display_item: Dictionary = current if is_equipped else item
	var rarity := str(display_item.get("rarity", "common")).capitalize()
	info.add_child(_label("%s  [%s]" % [str(display_item.get("name", "Armor")), rarity], 15, TEXT))
	var mechanics := "Slot %s  •  Armor %d/%d  •  Weight %d" % [
		slot.capitalize(), int(display_item.get("armor_hp", 0)), int(display_item.get("max_armor_hp", display_item.get("armor_hp", 0))), int(display_item.get("weight", 0))
	]
	var bonus = display_item.get("stat_bonus")
	if bonus is Dictionary:
		mechanics += "  •  +%d %s" % [int(bonus.get("amount", 0)), str(bonus.get("stat", "stat")).capitalize()]
	info.add_child(_label(mechanics, 13, MUTED))
	var item_description := str(display_item.get("description", "")).strip_edges()
	if not item_description.is_empty():
		var description_label := _label(item_description, 13, MUTED)
		description_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		info.add_child(description_label)
	var equip := _button("EQUIPPED" if is_equipped else "EQUIP", not is_equipped)
	equip.custom_minimum_size = Vector2(105, 42)
	equip.disabled = is_equipped or _combat_active()
	equip.pressed.connect(_request.bind("/character/armor/equip", {"inventory_index": inventory_index}, "character_armor"))
	row.add_child(equip)
	return card


func _request(endpoint: String, payload: Dictionary, mode: String) -> void:
	set_status("Working...", false)
	api_request.emit(endpoint, payload, mode)


func _load_portrait_texture(encoded: String) -> void:
	var image_bytes: PackedByteArray = Marshalls.base64_to_raw(encoded)
	if image_bytes.is_empty():
		return
	var generated_image := Image.new()
	if generated_image.load_png_from_buffer(image_bytes) != OK:
		set_status("The generated character art could not be displayed.", true)
		return
	portrait_texture = ImageTexture.create_from_image(generated_image)


func _refresh_art_after_armor_change(changed_slot: String, change_type: String) -> void:
	set_status("Armor changed. Updating the character picture...", false)
	_request(
		"/character/portrait/generate",
		{"changed_slot": changed_slot, "change_type": change_type},
		"character_portrait"
	)


func _combat_active() -> bool:
	var combat = game_state.get("combat", {})
	return combat is Dictionary and bool(combat.get("active", false))


func _attribute_bonus(score: int) -> int:
	if score <= 30:
		return int(score / 3)
	return int(10 + (score - 30) / 10)


func _signed(value: int) -> String:
	return "+%d" % value if value >= 0 else str(value)


func _add_section_heading(title: String, description: String) -> void:
	content_box.add_child(_label(title, 19, TEXT))
	var subtitle := _label(description, 14, MUTED)
	subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	content_box.add_child(subtitle)


func _warning(text_value: String) -> Label:
	var label := _label(text_value, 14, DANGER)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return label


func _muted(text_value: String) -> Label:
	var label := _label(text_value, 14, MUTED)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return label


func _label(text_value: String, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text_value
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	return label


func _button(text_value: String, primary: bool) -> Button:
	var button := Button.new()
	button.text = text_value
	button.focus_mode = Control.FOCUS_ALL
	var normal := StyleBoxFlat.new()
	normal.bg_color = ACCENT if primary else PANEL_ALT
	normal.border_color = ACCENT if primary else BORDER
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(8)
	var hover: StyleBoxFlat = normal.duplicate()
	hover.bg_color = ACCENT_HOVER if primary else Color("1d2635")
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", hover)
	button.add_theme_color_override("font_color", TEXT)
	button.add_theme_font_size_override("font_size", 14)
	return button


func _panel(color: Color) -> PanelContainer:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = BORDER
	style.set_border_width_all(1)
	style.set_corner_radius_all(10)
	panel.add_theme_stylebox_override("panel", style)
	return panel


func _card_margin() -> MarginContainer:
	var margin := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		margin.add_theme_constant_override(side, 13)
	return margin
