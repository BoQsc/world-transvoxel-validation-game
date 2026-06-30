extends SceneTree

const MARKER := "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_PASS"
const PROCEDURAL_PROFILE_ID := &"g19_compact_2k_on_demand"
const FLAT_PROFILE_ID := &"flat_baseline"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_PROCEDURAL_RESOURCES := 25
const EXPECTED_FLAT_RESOURCES := 1
const PROCEDURAL_POINTS := [
	Vector3i(1032, 0, 1032),
	Vector3i(1032, 4, 1032),
	Vector3i(1032, 8, 1032),
	Vector3i(1032, 10, 1032),
]
const FLAT_POINTS := [
	Vector3i(8, 0, 8),
	Vector3i(8, 8, 8),
	Vector3i(8, 10, 8),
]
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted
var _sample_batch_results: Dictionary = {}
var _sample_batch_failures: Dictionary = {}


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var procedural_scene := await _load_scene(
		PROCEDURAL_PROFILE_ID, "procedural_strata", EXPECTED_PROCEDURAL_RESOURCES
	)
	if procedural_scene == null:
		return
	var procedural_result := await _verify_procedural_strata(procedural_scene)
	if procedural_result.is_empty():
		return
	procedural_scene.queue_free()
	await process_frame
	var flat_scene := await _load_scene(FLAT_PROFILE_ID, "flat_volume", EXPECTED_FLAT_RESOURCES)
	if flat_scene == null:
		return
	var flat_result := await _verify_flat_volume(flat_scene)
	if flat_result.is_empty():
		return
	if not _helpers.assert_no_dense_files("g52_finish"):
		return
	print("%s profile=%s flat_profile=%s strata_samples=%d flat_volume_samples=%d density_ordered=1 strata_materials=%s flat_material=%d edit_localized=1 carved_density=%.3f max_render_resources=%d max_collision_resources=%d dense_world_files=0" % [
		MARKER,
		str(PROCEDURAL_PROFILE_ID),
		str(FLAT_PROFILE_ID),
		int(procedural_result.get("strata_samples", 0)),
		int(flat_result.get("flat_volume_samples", 0)),
		str(procedural_result.get("strata_materials", "")),
		int(flat_result.get("flat_material", 0)),
		float(procedural_result.get("carved_density", 0.0)),
		max(int(procedural_result.get("render_resources", 0)), int(flat_result.get("render_resources", 0))),
		max(int(procedural_result.get("collision_resources", 0)), int(flat_result.get("collision_resources", 0))),
	])
	flat_scene.queue_free()
	await process_frame
	quit(0)


func _load_scene(profile_id: StringName, label: String, expected_resources: int) -> Node:
	var packed: PackedScene = load(SCENE_PATH)
	if packed == null:
		_helpers.fail("G52 scene did not load: %s" % label)
		return null
	var scene: Node = packed.instantiate()
	scene.set("human_input_enabled", false)
	scene.set("player_driven_viewer_enabled", false)
	scene.call("configure_playtest_profile", profile_id)
	scene.call("set_camera_mode", &"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G52 scene did not become ready: %s %s" % [label, str(scene.call("get_validation_summary"))])
		return null
	var terrain_world: Node = _helpers.terrain_world(scene)
	if terrain_world == null:
		_helpers.fail("G52 terrain world missing: %s" % label)
		return null
	if not await _helpers.wait_for_window(
			terrain_world, expected_resources, label, 0,
			_chunk_for(Vector3(PROCEDURAL_POINTS[0]) if profile_id == PROCEDURAL_PROFILE_ID else Vector3(FLAT_POINTS[0])),
			expected_resources):
		return null
	_connect_public_batch_samples(terrain_world)
	return scene


func _verify_procedural_strata(scene: Node) -> Dictionary:
	var terrain_world: Node = _helpers.terrain_world(scene)
	if not _verify_generation_contract(terrain_world):
		return {}
	var samples: Array = await _request_samples(terrain_world, PROCEDURAL_POINTS, "procedural_strata")
	if samples.is_empty():
		return {}
	var deep: Dictionary = samples[0]
	var mid: Dictionary = samples[1]
	var shallow: Dictionary = samples[2]
	var air: Dictionary = samples[3]
	if not _density_ordered([deep, mid, shallow, air]) or \
			float(shallow.get("density", 0.0)) >= 0.0 or float(air.get("density", 0.0)) <= 0.0:
		_helpers.fail("G52 procedural density ordering/sign mismatch: %s" % str(samples))
		return {}
	if int(deep.get("material", 0)) != 1 or int(mid.get("material", 0)) != 7 or \
			int(shallow.get("material", 0)) != 4:
		_helpers.fail("G52 procedural strata material mismatch: %s" % str(samples))
		return {}
	var edit_result := await _verify_localized_underground_carve(scene, deep, mid)
	if edit_result.is_empty():
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	return {
		"strata_samples": 3,
		"strata_materials": "1,7,4",
		"carved_density": float(edit_result.get("carved_density", 0.0)),
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
	}


func _verify_generation_contract(terrain_world: Node) -> bool:
	var summaries: Dictionary = terrain_world.call("get_profile_summaries")
	var generation := Dictionary(summaries.get("generation", {}))
	var ids := Array(generation.get("underground_strata_material_ids", []))
	if not bool(generation.get("supports_underground_volume", false)) or \
			str(generation.get("underground_model", "")) != "density_volume_vertical_strata_v1" or \
			not ids.has(1) or not ids.has(7) or not ids.has(4):
		_helpers.fail("G52 generation underground contract mismatch: %s" % str(generation))
		return false
	return true


func _verify_localized_underground_carve(scene: Node, deep: Dictionary, mid: Dictionary) -> Dictionary:
	var terrain_world: Node = _helpers.terrain_world(scene)
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if interactor == null:
		_helpers.fail("G52 interactor missing")
		return {}
	var before_revision := int(terrain_world.call("get_world_revision"))
	if not bool(interactor.call("submit_sphere_edit", &"carve", Vector3(1032, 8, 1032), 1.8, 1, 1.0)):
		_helpers.fail("G52 underground carve was rejected")
		return {}
	if not await _helpers.wait_for_revision(terrain_world, before_revision + 1):
		return {}
	if not await _helpers.wait_for_window(
			terrain_world, EXPECTED_PROCEDURAL_RESOURCES, "g52_after_carve", 1,
			_chunk_for(Vector3(1032, 8, 1032)), EXPECTED_PROCEDURAL_RESOURCES):
		return {}
	var after: Array = await _request_samples(
		terrain_world,
		[Vector3i(1032, 0, 1032), Vector3i(1032, 4, 1032), Vector3i(1032, 8, 1032)],
		"after_underground_carve"
	)
	if after.is_empty():
		return {}
	var after_deep: Dictionary = after[0]
	var after_mid: Dictionary = after[1]
	var after_carved: Dictionary = after[2]
	if absf(float(after_deep.get("density", 999.0)) - float(deep.get("density", -999.0))) > 0.001 or \
			absf(float(after_mid.get("density", 999.0)) - float(mid.get("density", -999.0))) > 0.001 or \
			int(after_deep.get("material", 0)) != 1 or int(after_mid.get("material", 0)) != 7:
		_helpers.fail("G52 underground carve changed unaffected strata: %s" % str(after))
		return {}
	if absf(float(after_carved.get("density", 0.0)) - 1.0) > 0.001:
		_helpers.fail("G52 underground carve did not update target voxel density: %s" % str(after_carved))
		return {}
	return {"carved_density": float(after_carved.get("density", 0.0))}


func _verify_flat_volume(scene: Node) -> Dictionary:
	var terrain_world: Node = _helpers.terrain_world(scene)
	if not _verify_generation_contract(terrain_world):
		return {}
	var samples: Array = await _request_samples(terrain_world, FLAT_POINTS, "flat_volume")
	if samples.is_empty():
		return {}
	var low: Dictionary = samples[0]
	var surface: Dictionary = samples[1]
	var air: Dictionary = samples[2]
	if not _density_ordered([low, surface, air]) or \
			float(surface.get("density", 0.0)) >= 0.0 or float(air.get("density", 0.0)) <= 0.0:
		_helpers.fail("G52 flat density volume mismatch: %s" % str(samples))
		return {}
	if int(low.get("material", 0)) != 7 or int(surface.get("material", 0)) != 7:
		_helpers.fail("G52 flat material volume mismatch: %s" % str(samples))
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	return {
		"flat_volume_samples": 3,
		"flat_material": 7,
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
	}


func _request_samples(terrain_world: Node, points: Array, label: String) -> Array:
	_sample_batch_results.clear()
	_sample_batch_failures.clear()
	var request_id := int(terrain_world.call("request_authoritative_samples", points, 0))
	if request_id <= 0:
		_helpers.fail("G52 sample batch rejected at %s" % label)
		return []
	for _frame in range(900):
		if _sample_batch_results.has(request_id):
			return _samples_to_dicts(Array(_sample_batch_results[request_id]))
		if _sample_batch_failures.has(request_id):
			break
		await process_frame
	_helpers.fail("G52 sample batch failed at %s: %s" % [label, str(_sample_batch_failures)])
	return []


func _samples_to_dicts(samples: Array) -> Array:
	var results: Array = []
	for sample in samples:
		var ref: RefCounted = sample
		var point: Vector3i = ref.call("get_grid_point")
		results.append({
			"point": point,
			"density": float(ref.call("get_density")),
			"material": int(ref.call("get_material")),
			"agreeing_pages": int(ref.call("get_agreeing_page_count")),
		})
	return results


func _density_ordered(samples: Array) -> bool:
	for index in range(1, samples.size()):
		var previous := Dictionary(samples[index - 1])
		var current := Dictionary(samples[index])
		if float(previous.get("density", 0.0)) >= float(current.get("density", 0.0)):
			return false
	return true


func _connect_public_batch_samples(terrain_world: Node) -> void:
	if not terrain_world.authoritative_samples_ready.is_connected(_on_samples_ready):
		terrain_world.connect("authoritative_samples_ready", _on_samples_ready)
	if not terrain_world.authoritative_samples_failed.is_connected(_on_samples_failed):
		terrain_world.connect("authoritative_samples_failed", _on_samples_failed)


func _on_samples_ready(request_id: int, samples: Array) -> void:
	_sample_batch_results[request_id] = samples


func _on_samples_failed(request_id: int, error: String) -> void:
	_sample_batch_failures[request_id] = error


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(
		clamp(int(floor(position.x / 16.0)), 0, 127),
		clamp(int(floor(position.y / 16.0)), 0, 0),
		clamp(int(floor(position.z / 16.0)), 0, 127)
	)
