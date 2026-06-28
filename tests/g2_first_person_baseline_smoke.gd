extends SceneTree

const MARKER := "WT_VALIDATION_G2_GODOT_PASS"
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
	if str(summary.get("camera_mode", "")) != "first_person":
		_fail("G2 default camera is not first-person")
		return
	if not bool(summary.get("crosshair_present", false)):
		_fail("G2 crosshair is missing")
		return
	if bool(summary.get("player_human_input_enabled", true)):
		_fail("G2 autonomous smoke left human input enabled")
		return
	if int(summary.get("terrain_triangles", 0)) <= 0:
		_fail("G2 terrain mesh has no triangles")
		return
	if int(summary.get("collision_resources", 0)) <= 0:
		_fail("G2 terrain collision resources are missing")
		return
	var generation := _generation_summary(scene)
	if str(generation.get("profile_id", "")) != "flat_baseline":
		_fail("G2 default generation profile id is not flat_baseline: %s" % str(generation))
		return
	if str(generation.get("source_mode", "")) != "FLAT":
		_fail("G2 default generation profile is not FLAT: %s" % str(generation))
		return
	if int(generation.get("seed", -1)) != 1:
		_fail("G2 flat generation seed is not deterministic: %s" % str(generation))
		return
	var walk_motion := await _run_player_motion_probe(scene, summary)
	if walk_motion < 0.2:
		_fail("G2 scripted walk did not move the player")
		return
	var jump_height := await _run_player_jump_probe(scene)
	if jump_height < 0.05:
		_fail("G2 scripted jump did not lift the player")
		return
	print("%s generation=FLAT terrain_triangles=%d walk_motion=%.3f jump_height=%.3f" % [
		MARKER,
		int(summary.get("terrain_triangles", 0)),
		walk_motion,
		jump_height,
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _generation_summary(scene: Node) -> Dictionary:
	var reference := scene.get_node_or_null("WtTerrainReferenceScene")
	if reference == null or not reference.has_method("get_terrain_world"):
		return {}
	var terrain_world = reference.call("get_terrain_world")
	if terrain_world == null:
		return {}
	var generation = terrain_world.get("generation_profile")
	if generation != null and generation.has_method("get_contract_summary"):
		return Dictionary(generation.call("get_contract_summary"))
	return {}


func _wait_for_ready(scene: Node) -> bool:
	for _frame in range(900):
		if scene.has_method("get_validation_state") and scene.get_validation_state() == "ready":
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


func _run_player_jump_probe(scene: Node) -> float:
	var player := scene.get_node_or_null("ValidationPlayer")
	if player == null or not player.has_method("request_test_jump"):
		return 0.0
	var before_summary: Dictionary = scene.get_validation_summary()
	var start_y := float((before_summary.get("player_position", Vector3.ZERO) as Vector3).y)
	player.call("request_test_jump")
	var max_y := start_y
	for _frame in range(20):
		await physics_frame
		var summary: Dictionary = scene.get_validation_summary()
		var position: Vector3 = summary.get("player_position", Vector3.ZERO)
		max_y = max(max_y, position.y)
	return max_y - start_y


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G2_GODOT_FAIL: " + message)
	quit(1)
