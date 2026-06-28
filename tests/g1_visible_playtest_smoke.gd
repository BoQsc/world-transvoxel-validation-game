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
	scene.set_human_input_enabled(false)
	root.add_child(scene)
	if not await _wait_for_ready(scene):
		_fail("validation playtest scene did not become ready")
		return
	if not await _wait_for_player_floor(scene):
		_fail("validation player did not settle onto terrain collision")
		return
	var summary: Dictionary = scene.get_validation_summary()
	if bool(summary.get("player_human_input_enabled", true)):
		_fail("autonomous smoke left human input enabled")
		return
	if not bool(summary.get("player_present", false)):
		_fail("validation playtest has no player body")
		return
	if not bool(summary.get("player_camera_current", false)):
		_fail("validation playtest camera is not attached to player view")
		return
	if str(summary.get("camera_mode", "")) != "first_person":
		_fail("validation playtest default camera is not first-person")
		return
	if not bool(summary.get("crosshair_present", false)):
		_fail("validation playtest has no crosshair")
		return
	if not bool(summary.get("player_simulation_enabled", false)):
		_fail("validation player simulation is not enabled after terrain readiness")
		return
	if int(summary.get("terrain_mesh_instances", 0)) <= 0:
		_fail("validation playtest has no terrain mesh instances")
		return
	if int(summary.get("terrain_triangles", 0)) <= 0:
		_fail("validation playtest terrain mesh has no triangles")
		return
	if int(summary.get("collision_resources", 0)) <= 0:
		_fail("validation playtest has no terrain collision resources")
		return
	if not str(summary.get("status_text", "")).contains("READY"):
		_fail("validation playtest status text is not ready")
		return
	var moved := await _run_player_motion_probe(scene, summary)
	if moved < 0.2:
		_fail("validation player did not move under scripted test motion")
		return
	print("%s state=ready terrain_meshes=%d terrain_triangles=%d player_motion=%.3f implementation=human_visible_playtest_guard" %
		[
			MARKER,
			int(summary.get("terrain_mesh_instances", 0)),
			int(summary.get("terrain_triangles", 0)),
			moved,
		])
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


func _wait_for_player_floor(scene: Node) -> bool:
	for _frame in range(120):
		var summary: Dictionary = scene.get_validation_summary()
		if bool(summary.get("player_on_floor", false)):
			return true
		await physics_frame
	return false


func _run_player_motion_probe(scene: Node, summary: Dictionary) -> float:
	var before: Vector3 = summary.get("player_position", Vector3.ZERO)
	scene.set_player_test_motion(Vector3(1, 0, 0))
	for _frame in range(24):
		await physics_frame
	scene.clear_player_test_motion()
	await physics_frame
	var after_summary: Dictionary = scene.get_validation_summary()
	var after: Vector3 = after_summary.get("player_position", Vector3.ZERO)
	return Vector2(before.x, before.z).distance_to(Vector2(after.x, after.z))


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G1_GODOT_FAIL: " + message)
	quit(1)
