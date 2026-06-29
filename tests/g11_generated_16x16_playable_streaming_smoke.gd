extends SceneTree


const MARKER := "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_PASS"
const PROFILE_ID := &"g11_generated_16x16"
const EXPECTED_PAGE_COUNT := 256
const MAX_ACTIVE_RESOURCES := 25
const MIN_INITIAL_TRIANGLES := 1000
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")
const PATH_SAMPLES := [
	{
		"label": "origin",
		"position": Vector3(8, 8, 8),
		"expected_chunks": 9,
		"center_chunk": Vector3i(0, 0, 0),
	},
	{
		"label": "near_mid",
		"position": Vector3(64, 8, 64),
		"expected_chunks": 25,
		"center_chunk": Vector3i(4, 0, 4),
	},
	{
		"label": "center",
		"position": Vector3(128, 8, 128),
		"expected_chunks": 25,
		"center_chunk": Vector3i(8, 0, 8),
	},
	{
		"label": "far_mid",
		"position": Vector3(192, 8, 64),
		"expected_chunks": 25,
		"center_chunk": Vector3i(12, 0, 4),
	},
	{
		"label": "far_corner",
		"position": Vector3(247, 8, 247),
		"expected_chunks": 9,
		"center_chunk": Vector3i(15, 0, 15),
	},
]


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
	print("WT_VALIDATION_G11_PROGRESS step=wait_ready")
	if not await _wait_for_ready(scene):
		_fail("G11 profile did not become ready: %s" % str(scene.get_validation_summary()))
		return
	print("WT_VALIDATION_G11_PROGRESS step=wait_initial_floor")
	if not await _wait_for_player_floor(scene):
		_fail("G11 player did not settle on initial terrain: %s" % str(scene.get_validation_summary()))
		return
	var summary: Dictionary = scene.get_validation_summary()
	if not _summary_is_initial_playable(summary):
		_fail("G11 initial playable summary mismatch: %s" % str(summary))
		return

	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	var terrain_world := _terrain_world(scene)
	if reference == null or terrain_world == null:
		_fail("G11 missing reference scene or terrain world")
		return
	var backend_terrain: Node = terrain_world.call("get_backend_terrain")
	if backend_terrain == null or not backend_terrain.has_method("get_world_page_count"):
		_fail("G11 backend terrain cannot report world page count")
		return
	if int(backend_terrain.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_fail("G11 page count mismatch: %s" % str(backend_terrain.call("get_world_page_count")))
		return

	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var max_render_resources := 0
	var max_collision_resources := 0
	var edit_verified := false
	var revision := 2
	for sample in PATH_SAMPLES:
		print("WT_VALIDATION_G11_PROGRESS step=move label=%s revision=%d" % [sample["label"], revision])
		if not _move_player_to(scene, sample["position"]):
			return
		scene.set("viewer_position", sample["position"])
		if not reference.call("update_reference_viewer", 1, revision, sample["position"], 2, 0):
			_fail("G11 viewer event rejected at %s" % sample["label"])
			return
		if not await _wait_for_window(
			terrain_world,
			int(sample["expected_chunks"]),
			sample["label"],
			revision,
			sample["center_chunk"]
		):
			return
		print("WT_VALIDATION_G11_PROGRESS step=window_ready label=%s" % sample["label"])
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		max_render_resources = max(max_render_resources, int(metrics.get("render_resources", 0)))
		max_collision_resources = max(max_collision_resources, int(metrics.get("collision_resources", 0)))
		if not await _verify_materials(materializer, int(sample["expected_chunks"]), sample["label"]):
			return
		if str(sample["label"]) == "center":
			if not await _wait_for_player_floor(scene):
				_fail("G11 player did not settle on center generated terrain: %s" % str(scene.get_validation_summary()))
				return
			if not await _verify_player_motion(scene, scene.get_validation_summary()):
				return
			if not await _verify_edit(scene, terrain_world, revision, sample["center_chunk"]):
				return
			edit_verified = true
		revision += 1

	if not edit_verified:
		_fail("G11 did not exercise active-center edit")
		return
	if max_render_resources > MAX_ACTIVE_RESOURCES or max_collision_resources > MAX_ACTIVE_RESOURCES:
		_fail("G11 exceeded active resource budget: render=%d collision=%d" % [
			max_render_resources,
			max_collision_resources,
		])
		return
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	print("%s profile=%s samples=%d pages=%d max_render_resources=%d max_collision_resources=%d edit_replacements=%d" % [
		MARKER,
		str(PROFILE_ID),
		PATH_SAMPLES.size(),
		EXPECTED_PAGE_COUNT,
		max_render_resources,
		max_collision_resources,
		int(final_metrics.get("edit_replacements", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _summary_is_initial_playable(summary: Dictionary) -> bool:
	return str(summary.get("playtest_profile_id", "")) == str(PROFILE_ID) and \
			str(summary.get("fixture_label", "")) == "g11_generated_16x16_dense" and \
			int(summary.get("viewer_count", 0)) == 1 and \
			int(summary.get("expected_resource_count", 0)) == 9 and \
			int(summary.get("render_resources", 0)) == 9 and \
			int(summary.get("collision_resources", 0)) == 9 and \
			int(summary.get("terrain_triangles", 0)) >= MIN_INITIAL_TRIANGLES and \
			bool(summary.get("player_present", false)) and \
			bool(summary.get("player_camera_current", false)) and \
			bool(summary.get("crosshair_present", false)) and \
			not bool(summary.get("player_human_input_enabled", true))


func _move_player_to(scene: Node, viewer_sample_position: Vector3) -> bool:
	var player := scene.get_node_or_null("ValidationPlayer") as CharacterBody3D
	if player == null:
		_fail("G11 validation player missing")
		return false
	scene.clear_player_test_motion()
	player.global_position = Vector3(viewer_sample_position.x, 24.0, viewer_sample_position.z)
	player.velocity = Vector3.ZERO
	return true


func _verify_player_motion(scene: Node, summary: Dictionary) -> bool:
	var before: Vector3 = summary.get("player_position", Vector3.ZERO)
	scene.set_player_test_motion(Vector3(1, 0, 0))
	for _frame in range(45):
		await physics_frame
	scene.clear_player_test_motion()
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	if before.distance_to(after) < 0.25:
		_fail("G11 scripted player motion did not move: before=%s after=%s" % [str(before), str(after)])
		return false
	return true


func _verify_edit(scene: Node, terrain_world: Node, revision: int, center_chunk: Vector3i) -> bool:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if interactor == null:
		_fail("G11 missing terrain interactor")
		return false
	var start_world_revision := int(terrain_world.call("get_backend_world_revision"))
	var start_replacements := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("edit_replacements", 0))
	var point := ProfileCatalog.edit_point(PROFILE_ID)
	if not bool(interactor.call("submit_sphere_edit", &"carve", point, 1.8, -1, 1.0)):
		_fail("G11 active-center carve was rejected")
		return false
	if not await _wait_for_revision(terrain_world, start_world_revision + 1):
		_fail("G11 active-center carve did not commit")
		return false
	if not await _wait_for_window(terrain_world, 25, "center_after_edit", revision, center_chunk):
		return false
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("edit_replacements", 0)) <= start_replacements:
		_fail("G11 active-center carve did not replace any render resource: %s" % str(metrics))
		return false
	return true


func _verify_materials(materializer: Node, expected_chunks: int, label: String) -> bool:
	if materializer == null:
		_fail("G11 materializer missing")
		return false
	var summary: Dictionary = materializer.call("apply_materials_now")
	if int(summary.get("materialized_instances", 0)) < expected_chunks:
		_fail("G11 materials did not cover %s: %s" % [label, str(summary)])
		return false
	return true


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
	for _frame in range(360):
		var summary: Dictionary = scene.get_validation_summary()
		if bool(summary.get("player_on_floor", false)):
			return true
		await physics_frame
	return false


func _wait_for_revision(terrain_world: Node, revision: int) -> bool:
	for _frame in range(1200):
		if int(terrain_world.call("get_backend_world_revision")) >= revision:
			return true
		await process_frame
	return false


func _wait_for_window(
	terrain_world: Node,
	expected_chunks: int,
	label: String,
	minimum_viewer_updates: int,
	center_chunk: Variant
) -> bool:
	for _frame in range(1500):
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		var active_records := int(metrics.get("active_chunk_records", 0))
		var render_resources := int(metrics.get("render_resources", 0))
		var collision_resources := int(metrics.get("collision_resources", 0))
		var center_ready := true
		if center_chunk != null:
			center_ready = _is_ready_snapshot(terrain_world.call("query_chunk_state", center_chunk, 0))
		if active_records == expected_chunks and \
				render_resources == expected_chunks and \
				collision_resources == expected_chunks and \
				int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and \
				center_ready and \
				int(metrics.get("queued_render", 0)) == 0 and \
				int(metrics.get("queued_collision", 0)) == 0 and \
				int(metrics.get("fully_ready_chunk_records", -1)) == active_records and \
				int(metrics.get("pending_chunk_retirements", 0)) == 0 and \
				int(metrics.get("render_fading_resources", 0)) == 0 and \
				active_records <= MAX_ACTIVE_RESOURCES:
			return true
		await process_frame
	_fail("G11 window did not settle at %s expected=%d metrics=%s" % [
		label,
		expected_chunks,
		str(terrain_world.call("get_runtime_metrics")),
	])
	return false


func _is_ready_snapshot(snapshot: RefCounted) -> bool:
	return snapshot != null and snapshot.call("is_present") and \
			snapshot.call("is_visual_ready") and \
			snapshot.call("is_collision_required") and \
			snapshot.call("is_collision_ready") and \
			snapshot.call("is_fully_ready")


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_FAIL: " + message)
	quit(1)
