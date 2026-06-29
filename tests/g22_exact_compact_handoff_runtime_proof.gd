extends SceneTree


const MARKER := "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const EXPECTED_PAGE_COUNT := 16384
const MAX_ACTIVE_RESOURCES := 25
const MIN_INITIAL_TRIANGLES := 1000
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const PATH_SAMPLES := [
	{
		"label": "origin",
		"position": Vector3(8, 8, 8),
		"expected_chunks": 9,
		"center_chunk": Vector3i(0, 0, 0),
	},
	{
		"label": "center",
		"position": Vector3(1032, 8, 1032),
		"expected_chunks": 25,
		"center_chunk": Vector3i(64, 0, 64),
	},
	{
		"label": "far_corner",
		"position": Vector3(2040, 8, 2040),
		"expected_chunks": 9,
		"center_chunk": Vector3i(127, 0, 127),
	},
]

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self)
	call_deferred("_run_test")


func _run_test() -> void:
	if not _helpers.assert_no_dense_files("before_start"):
		return
	var packed := load(SCENE_PATH)
	if packed == null:
		_helpers.fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene):
		_helpers.fail("G22 handoff project did not become ready: %s" % str(scene.get_validation_summary()))
		return
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G22 player did not settle on initial terrain: %s" % str(scene.get_validation_summary()))
		return
	if not _helpers.assert_no_dense_files("after_start"):
		return
	var summary: Dictionary = scene.get_validation_summary()
	if not _summary_is_initial_playable(summary):
		_helpers.fail("G22 initial playable summary mismatch: %s" % str(summary))
		return

	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	var terrain_world: Node = _helpers.terrain_world(scene)
	if reference == null or terrain_world == null:
		_helpers.fail("G22 missing reference scene or terrain world")
		return
	var backend_terrain: Node = terrain_world.call("get_backend_terrain")
	if backend_terrain == null or not backend_terrain.has_method("get_world_page_count"):
		_helpers.fail("G22 backend terrain cannot report world page count")
		return
	var page_count := int(backend_terrain.call("get_world_page_count"))
	if page_count != EXPECTED_PAGE_COUNT:
		_helpers.fail("G22 page count mismatch: %d" % page_count)
		return

	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var max_render_resources := 0
	var max_collision_resources := 0
	var capture_results: Array[Dictionary] = []
	var movement_verified := false
	var construct_verified := false
	var revision := 2
	for sample in PATH_SAMPLES:
		var sample_result := await _run_sample(
			scene, reference, terrain_world, materializer, sample, revision, capture_results
		)
		if sample_result.is_empty():
			return
		max_render_resources = max(max_render_resources, int(sample_result.get("render_resources", 0)))
		max_collision_resources = max(max_collision_resources, int(sample_result.get("collision_resources", 0)))
		movement_verified = movement_verified or bool(sample_result.get("movement_verified", false))
		construct_verified = construct_verified or bool(sample_result.get("construct_verified", false))
		revision += 1

	if not _final_assertions(terrain_world, movement_verified, construct_verified, max_render_resources, max_collision_resources):
		return
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	_helpers.write_runtime_metrics({
		"profile": str(PROFILE_ID),
		"page_count": page_count,
		"samples": PATH_SAMPLES.size(),
		"capture_count": capture_results.size(),
		"captures": capture_results,
		"movement_verified": movement_verified,
		"construct_verified": construct_verified,
		"max_render_resources": max_render_resources,
		"max_collision_resources": max_collision_resources,
		"edit_replacements": int(final_metrics.get("edit_replacements", 0)),
		"final_pending_chunk_retirements": int(final_metrics.get("pending_chunk_retirements", 0)),
		"final_render_fading_resources": int(final_metrics.get("render_fading_resources", 0)),
	})
	print("%s profile=%s captures=%d pages=%d max_render_resources=%d max_collision_resources=%d edit_replacements=%d construct_verified=1 pending_retirements=0 render_fading_resources=0 dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		capture_results.size(),
		EXPECTED_PAGE_COUNT,
		max_render_resources,
		max_collision_resources,
		int(final_metrics.get("edit_replacements", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _run_sample(
	scene: Node,
	reference: Node,
	terrain_world: Node,
	materializer: Node,
	sample: Dictionary,
	revision: int,
	capture_results: Array[Dictionary]
) -> Dictionary:
	scene.set("viewer_position", sample["position"])
	if not reference.call("update_reference_viewer", 1, revision, sample["position"], 2, 0):
		_helpers.fail("G22 viewer event rejected at %s" % sample["label"])
		return {}
	if not await _helpers.wait_for_window(
		terrain_world, int(sample["expected_chunks"]), sample["label"], revision,
		sample["center_chunk"], MAX_ACTIVE_RESOURCES
	):
		return {}
	if not _helpers.move_player_to(scene, sample["position"]):
		return {}
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G22 player did not settle at %s: %s" % [sample["label"], str(scene.get_validation_summary())])
		return {}
	if not await _helpers.verify_materials(materializer, int(sample["expected_chunks"]), sample["label"]):
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var result := {
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
	}
	if str(sample["label"]) == "origin":
		capture_results.append(await _helpers.capture_overview(scene, "origin_overview", 250))
	elif str(sample["label"]) == "center":
		if not await _helpers.verify_player_motion(scene, scene.get_validation_summary()):
			return {}
		capture_results.append(await _helpers.capture_oblique(scene, "center_oblique", 100))
		var edit_result: Dictionary = await _helpers.verify_carve_and_construct(
			scene, terrain_world, materializer, revision, sample["center_chunk"]
		)
		if edit_result.is_empty():
			return {}
		capture_results.append(await _helpers.capture_overview(scene, "center_after_construct_overview", 250))
		var after_edit_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		result["render_resources"] = max(int(result["render_resources"]), int(after_edit_metrics.get("render_resources", 0)))
		result["collision_resources"] = max(int(result["collision_resources"]), int(after_edit_metrics.get("collision_resources", 0)))
		result["movement_verified"] = true
		result["construct_verified"] = bool(edit_result.get("construct_verified", false))
	return result


func _summary_is_initial_playable(summary: Dictionary) -> bool:
	return str(summary.get("playtest_profile_id", "")) == str(PROFILE_ID) and \
			str(summary.get("fixture_label", "")) == "g19_compact_2k_on_demand" and \
			int(summary.get("viewer_count", 0)) == 1 and \
			int(summary.get("expected_resource_count", 0)) == 25 and \
			int(summary.get("render_resources", 0)) == 25 and \
			int(summary.get("collision_resources", 0)) == 25 and \
			int(summary.get("terrain_triangles", 0)) >= MIN_INITIAL_TRIANGLES and \
			bool(summary.get("player_present", false)) and \
			bool(summary.get("player_camera_current", false)) and \
			bool(summary.get("crosshair_present", false)) and \
			not bool(summary.get("player_human_input_enabled", true))


func _final_assertions(
	terrain_world: Node,
	movement_verified: bool,
	construct_verified: bool,
	max_render_resources: int,
	max_collision_resources: int
) -> bool:
	if not movement_verified:
		_helpers.fail("G22 did not verify scripted player movement")
		return false
	if not construct_verified:
		_helpers.fail("G22 did not verify construct/place")
		return false
	if not _helpers.assert_no_dense_files("after_runtime"):
		return false
	if max_render_resources > MAX_ACTIVE_RESOURCES or max_collision_resources > MAX_ACTIVE_RESOURCES:
		_helpers.fail("G22 exceeded active resource budget: render=%d collision=%d" % [
			max_render_resources, max_collision_resources
		])
		return false
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(final_metrics.get("pending_chunk_retirements", 0)) != 0 or \
			int(final_metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G22 final runtime not settled: %s" % str(final_metrics))
		return false
	return true
