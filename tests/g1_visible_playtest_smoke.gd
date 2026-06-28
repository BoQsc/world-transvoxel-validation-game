extends SceneTree

const MARKER := "WT_VALIDATION_G1_GODOT_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var packed := load(SCENE_PATH)
	if packed == null:
		_fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	root.add_child(scene)
	if not await _wait_for_ready(scene):
		_fail("validation playtest scene did not become ready")
		return
	var summary: Dictionary = scene.get_validation_summary()
	if int(summary.get("terrain_mesh_instances", 0)) <= 0:
		_fail("validation playtest has no terrain mesh instances")
		return
	if not str(summary.get("status_text", "")).contains("READY"):
		_fail("validation playtest status text is not ready")
		return
	print("%s state=ready terrain_meshes=%d implementation=human_visible_playtest_guard" %
		[MARKER, int(summary.get("terrain_mesh_instances", 0))])
	scene.queue_free()
	await process_frame
	quit(0)


func _wait_for_ready(scene: Node) -> bool:
	for _frame in range(900):
		if scene.has_method("get_validation_state") and \
				scene.get_validation_state() == "ready":
			await process_frame
			return true
		await process_frame
	return false


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G1_GODOT_FAIL: " + message)
	quit(1)
