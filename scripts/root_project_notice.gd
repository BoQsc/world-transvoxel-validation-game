extends Control


func _ready() -> void:
	var label := Label.new()
	label.name = "RootProjectNotice"
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.text = "This root project does not vendor the addons.\n\n"
	label.text += "Run python tools/g1_visible_playtest_smoke.py, then open:\n"
	label.text += "artifacts/g1_visible_playtest/project/project.godot\n\n"
	label.text += "Opening this root project for terrain playtest is invalid."
	add_child(label)
