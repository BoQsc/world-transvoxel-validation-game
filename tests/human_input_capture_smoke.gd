extends SceneTree

const MARKER := "WT_VALIDATION_HUMAN_INPUT_CAPTURE_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var packed := load(SCENE_PATH)
	if packed == null:
		_fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	scene.auto_start = false
	scene.human_input_enabled = true
	root.add_child(scene)
	await process_frame
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		_fail("human playtest did not capture mouse on start")
		return
	_assert_mouse_transparent_overlay(scene)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	scene.call("_unhandled_input", click)
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		_fail("click did not recapture mouse")
		return
	if not bool(scene.call("should_ignore_mouse_button_event")):
		_fail("capture click was not suppressed for terrain interaction")
		return
	print("%s mouse_mode=captured overlay_mouse_filter=ignore" % MARKER)
	scene.queue_free()
	await process_frame
	quit(0)


func _assert_mouse_transparent_overlay(scene: Node) -> void:
	var panel = scene.get_node_or_null("ValidationStatusOverlay/Panel")
	var crosshair_h = scene.get_node_or_null("ValidationCrosshair/Horizontal")
	var crosshair_v = scene.get_node_or_null("ValidationCrosshair/Vertical")
	for node in [panel, crosshair_h, crosshair_v]:
		if node == null or int(node.mouse_filter) != Control.MOUSE_FILTER_IGNORE:
			_fail("overlay mouse filter is not ignore")


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_HUMAN_INPUT_CAPTURE_FAIL: " + message)
	quit(1)
