extends SceneTree


const MARKER := "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_PASS"
const PROFILE_ID := &"g8_sparse_2k"
const EXPECTED_RESOURCES := 93
const MIN_TRIANGLES := 30000
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var packed := load(SCENE_PATH)
	if packed == null:
		_fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _wait_for_ready(scene):
		_fail("G9 sparse 2K profile did not become ready: %s" % str(scene.get_validation_summary()))
		return
	if not await _wait_for_player_floor(scene):
		_fail("G9 sparse 2K player did not settle on terrain: %s" % str(scene.get_validation_summary()))
		return
	var summary: Dictionary = scene.get_validation_summary()
	if not _summary_is_sparse_2k_playable(summary):
		_fail("G9 sparse 2K summary mismatch: %s" % str(summary))
		return
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var material_summary := await _wait_for_materials(materializer)
	if int(material_summary.get("materialized_instances", 0)) < EXPECTED_RESOURCES:
		_fail("G9 sparse 2K materializer did not cover resources: %s" % str(material_summary))
		return
	if not await _verify_player_motion(scene, summary):
		return
	if not await _verify_edit(scene):
		return
	var terrain_world := _terrain_world(scene)
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	print("%s profile=%s resources=%d viewers=%d triangles=%d materialized=%d edit_replacements=%d" % [
		MARKER,
		str(PROFILE_ID),
		int(metrics.get("render_resources", 0)),
		int(summary.get("viewer_count", 0)),
		int(summary.get("terrain_triangles", 0)),
		int(material_summary.get("materialized_instances", 0)),
		int(metrics.get("edit_replacements", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _summary_is_sparse_2k_playable(summary: Dictionary) -> bool:
	return str(summary.get("playtest_profile_id", "")) == str(PROFILE_ID) and \
			str(summary.get("fixture_label", "")) == "g8_sparse_2k_path" and \
			int(summary.get("viewer_count", 0)) == 5 and \
			int(summary.get("expected_resource_count", 0)) == EXPECTED_RESOURCES and \
			int(summary.get("render_resources", 0)) >= EXPECTED_RESOURCES and \
			int(summary.get("collision_resources", 0)) >= EXPECTED_RESOURCES and \
			int(summary.get("terrain_triangles", 0)) >= MIN_TRIANGLES and \
			bool(summary.get("player_present", false)) and \
			bool(summary.get("player_camera_current", false)) and \
			bool(summary.get("crosshair_present", false)) and \
			not bool(summary.get("player_human_input_enabled", true))


func _verify_player_motion(scene: Node, summary: Dictionary) -> bool:
	var before: Vector3 = summary.get("player_position", Vector3.ZERO)
	scene.set_player_test_motion(Vector3(1, 0, 0))
	for _frame in range(45):
		await physics_frame
	scene.clear_player_test_motion()
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	if before.distance_to(after) < 0.25:
		_fail("G9 sparse 2K scripted player motion did not move: before=%s after=%s" % [str(before), str(after)])
		return false
	return true


func _verify_edit(scene: Node) -> bool:
	var terrain_world := _terrain_world(scene)
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if terrain_world == null or interactor == null:
		_fail("G9 sparse 2K missing terrain world or interactor")
		return false
	var start_revision := int(terrain_world.call("get_backend_world_revision"))
	var point := ProfileCatalog.edit_point(PROFILE_ID)
	if not bool(interactor.call("submit_sphere_edit", &"carve", point, 1.8, -1, 1.0)):
		_fail("G9 sparse 2K carve was rejected")
		return false
	if not await _wait_for_revision(terrain_world, start_revision + 1):
		_fail("G9 sparse 2K carve did not commit")
		return false
	if not await _wait_for_cold_idle(terrain_world):
		_fail("G9 sparse 2K carve did not return cold idle")
		return false
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("render_fading_resources", 0)) != 0:
		_fail("G9 sparse 2K edit created render fade blink resources: %s" % str(metrics))
		return false
	return int(metrics.get("edit_replacements", 0)) > 0


func _terrain_world(scene: Node) -> Node:
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference == null:
		return null
	return reference.call("get_terrain_world")


func _wait_for_ready(scene: Node) -> bool:
	for _frame in range(1200):
		if scene.has_method("get_validation_state") and scene.get_validation_state() == "ready":
			await process_frame
			return true
		await process_frame
	return false


func _wait_for_player_floor(scene: Node) -> bool:
	for _frame in range(240):
		var summary: Dictionary = scene.get_validation_summary()
		if bool(summary.get("player_on_floor", false)):
			return true
		await physics_frame
	return false


func _wait_for_materials(materializer: Node) -> Dictionary:
	if materializer == null:
		return {}
	for _frame in range(180):
		var summary: Dictionary = materializer.call("get_material_summary")
		if bool(summary.get("applied", false)):
			return summary
		await process_frame
	return materializer.call("apply_materials_now")


func _wait_for_revision(terrain_world: Node, revision: int) -> bool:
	for _frame in range(1200):
		if int(terrain_world.call("get_backend_world_revision")) >= revision:
			return true
		await process_frame
	return false


func _wait_for_cold_idle(terrain_world: Node) -> bool:
	for _frame in range(1200):
		if bool(Dictionary(terrain_world.call("get_cold_idle_summary")).get("cold_idle", false)):
			await process_frame
			return true
		await process_frame
	return false


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_FAIL: " + message)
	quit(1)
