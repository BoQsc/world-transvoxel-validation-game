extends SceneTree


const MARKER := "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_ACTIVE_RESOURCES := 25
const EXPECTED_RADIUS := 1.8
const EXPECTED_PLACE_MATERIAL := 4
const REPEATED_EDITS := 6
const MAX_COMMIT_FRAMES := 180
const MAX_SETTLE_FRAMES := 480
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted
var _sample_results: Dictionary = {}
var _sample_failures: Dictionary = {}


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G44 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if backend == null or interactor == null:
		_helpers.fail("G44 backend or interactor missing")
		return
	_connect_backend(backend)
	var policy := _verify_policy_summary(interactor)
	if policy.is_empty():
		return
	var edit_origin := Vector3(1032, 8, 1032)
	if not _helpers.move_player_to(scene, edit_origin):
		return
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g44_edit_site", 1, _chunk_for(edit_origin), EXPECTED_ACTIVE_RESOURCES):
		return
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var aggregate := _new_aggregate()
	for index in range(REPEATED_EDITS):
		var mode := &"carve" if index % 2 == 0 else &"construct"
		var center := edit_origin + Vector3(index * 5, 0, 0)
		var result := await _submit_policy_edit(interactor, terrain_world, backend, mode, center)
		if result.is_empty():
			return
		_merge_aggregate(aggregate, result)
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not _helpers.assert_no_dense_files("g44_finish"):
		return
	var edit_delta := int(final_metrics.get("edit_replacements", 0)) - int(before_metrics.get("edit_replacements", 0))
	if edit_delta < REPEATED_EDITS:
		_helpers.fail("G44 edit replacement delta too small: %d metrics=%s" % [edit_delta, str(final_metrics)])
		return
	print("%s profile=%s default_shape=%s dig_radius=%.3f place_radius=%.3f place_material=%d alternate_shape_toggles=%s edits=%d inside_samples=%d outside_unchanged_samples=%d max_commit_frames=%d max_settle_frames=%d edit_replacement_delta=%d max_render_resources=%d max_collision_resources=%d max_active_records=%d max_pending_retirements=%d max_render_fading_resources=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		str(policy.get("default_brush_shape", "")),
		float(policy.get("dig_radius", 0.0)),
		float(policy.get("place_radius", 0.0)),
		int(policy.get("place_material_id", 0)),
		str(policy.get("alternate_shape_toggles_enabled", true)).to_lower(),
		REPEATED_EDITS,
		int(aggregate.get("inside_samples", 0)),
		int(aggregate.get("outside_unchanged_samples", 0)),
		int(aggregate.get("max_commit_frames", 0)),
		int(aggregate.get("max_settle_frames", 0)),
		edit_delta,
		int(aggregate.get("max_render_resources", 0)),
		int(aggregate.get("max_collision_resources", 0)),
		int(aggregate.get("max_active_records", 0)),
		int(aggregate.get("max_pending_retirements", 0)),
		int(aggregate.get("max_render_fading_resources", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _verify_policy_summary(interactor: Node) -> Dictionary:
	var policy: Dictionary = interactor.call("get_edit_policy_summary")
	if str(policy.get("default_brush_shape", "")) != "sphere" or \
			absf(float(policy.get("dig_radius", 0.0)) - EXPECTED_RADIUS) > 0.001 or \
			absf(float(policy.get("place_radius", 0.0)) - EXPECTED_RADIUS) > 0.001 or \
			int(policy.get("place_material_id", 0)) != EXPECTED_PLACE_MATERIAL or \
			bool(policy.get("alternate_shape_toggles_enabled", true)):
		_helpers.fail("G44 edit policy mismatch: %s" % str(policy))
		return {}
	return policy


func _submit_policy_edit(interactor: Node, terrain_world: Node, backend: Node, mode: StringName, center: Vector3) -> Dictionary:
	var expected_density := 1.0 if mode == &"carve" else -1.0
	var expected_material := -1 if mode == &"carve" else EXPECTED_PLACE_MATERIAL
	var outside_point := Vector3i(center + Vector3(3, 0, 0))
	var outside_before := await _sample(backend, outside_point)
	if outside_before.is_empty():
		return {}
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var start_frame := Engine.get_physics_frames()
	if not bool(interactor.call("submit_sphere_edit", mode, center, EXPECTED_RADIUS, expected_material, 1.0)):
		_helpers.fail("G44 edit submission failed: %s" % str(interactor.call("get_last_submission")))
		return {}
	var submission: Dictionary = interactor.call("get_last_submission")
	if str(submission.get("mode", "")) != str(mode) or absf(float(submission.get("radius", 0.0)) - EXPECTED_RADIUS) > 0.001:
		_helpers.fail("G44 submission policy mismatch: %s" % str(submission))
		return {}
	if not await _helpers.wait_for_revision(terrain_world, before_revision + 1):
		return {}
	var commit_frames := Engine.get_physics_frames() - start_frame
	var settle_start := Engine.get_physics_frames()
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g44_after_%s" % str(mode), int(before_metrics.get("viewer_updates", 0)), _chunk_for(center), EXPECTED_ACTIVE_RESOURCES):
		return {}
	var settle_frames := Engine.get_physics_frames() - settle_start
	if commit_frames > MAX_COMMIT_FRAMES or settle_frames > MAX_SETTLE_FRAMES:
		_helpers.fail("G44 edit latency exceeded budget: commit=%d settle=%d" % [commit_frames, settle_frames])
		return {}
	var inside_count := await _verify_inside_samples(backend, center, expected_density, expected_material)
	if inside_count <= 0:
		return {}
	if not await _verify_outside_unchanged(backend, outside_point, outside_before):
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("pending_chunk_retirements", 0)) != 0 or int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G44 post-edit churn/fade not settled: %s" % str(metrics))
		return {}
	return {
		"inside_samples": inside_count,
		"outside_unchanged_samples": 1,
		"max_commit_frames": commit_frames,
		"max_settle_frames": settle_frames,
		"max_render_resources": int(metrics.get("render_resources", 0)),
		"max_collision_resources": int(metrics.get("collision_resources", 0)),
		"max_active_records": int(metrics.get("active_chunk_records", 0)),
		"max_pending_retirements": int(metrics.get("pending_chunk_retirements", 0)),
		"max_render_fading_resources": int(metrics.get("render_fading_resources", 0)),
	}


func _verify_inside_samples(backend: Node, center: Vector3, expected_density: float, expected_material: int) -> int:
	var offsets := [Vector3i.ZERO, Vector3i(1, 0, 0), Vector3i(-1, 0, 0), Vector3i(0, 0, 1)]
	var verified := 0
	for offset in offsets:
		var point: Vector3i = Vector3i(center) + offset
		var sample := await _sample(backend, point)
		if sample.is_empty():
			return 0
		if absf(float(sample.get("density", 999.0)) - expected_density) > 0.001:
			_helpers.fail("G44 inside density mismatch at %s expected=%.3f sample=%s" % [str(point), expected_density, str(sample)])
			return 0
		if expected_material > 0 and int(sample.get("material", 0)) != expected_material:
			_helpers.fail("G44 inside material mismatch at %s expected=%d sample=%s" % [str(point), expected_material, str(sample)])
			return 0
		verified += 1
	return verified


func _verify_outside_unchanged(backend: Node, point: Vector3i, before: Dictionary) -> bool:
	var after := await _sample(backend, point)
	if after.is_empty():
		return false
	if absf(float(after.get("density", 0.0)) - float(before.get("density", 0.0))) > 0.001 or int(after.get("material", 0)) != int(before.get("material", 0)):
		_helpers.fail("G44 outside-radius sample changed at %s before=%s after=%s" % [str(point), str(before), str(after)])
		return false
	return true


func _sample(backend: Node, point: Vector3i) -> Dictionary:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(backend.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_helpers.fail("G44 authoritative sample query failed at %s" % str(point))
		return {}
	var sample: RefCounted = _sample_results[request_id]
	return {"density": float(sample.call("get_density")), "material": int(sample.call("get_material"))}


func _wait_for_sample(request_id: int) -> bool:
	for _frame in range(900):
		if _sample_results.has(request_id):
			return true
		if _sample_failures.has(request_id):
			return false
		await process_frame
	return false


func _connect_backend(backend: Node) -> void:
	if not backend.authoritative_sample_ready.is_connected(_on_sample_ready):
		backend.connect("authoritative_sample_ready", _on_sample_ready)
	if not backend.authoritative_sample_failed.is_connected(_on_sample_failed):
		backend.connect("authoritative_sample_failed", _on_sample_failed)


func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample


func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error


func _new_aggregate() -> Dictionary:
	return {"inside_samples": 0, "outside_unchanged_samples": 0, "max_commit_frames": 0, "max_settle_frames": 0, "max_render_resources": 0, "max_collision_resources": 0, "max_active_records": 0, "max_pending_retirements": 0, "max_render_fading_resources": 0}


func _merge_aggregate(aggregate: Dictionary, result: Dictionary) -> void:
	aggregate["inside_samples"] = int(aggregate.get("inside_samples", 0)) + int(result.get("inside_samples", 0))
	aggregate["outside_unchanged_samples"] = int(aggregate.get("outside_unchanged_samples", 0)) + int(result.get("outside_unchanged_samples", 0))
	for key in ["max_commit_frames", "max_settle_frames", "max_render_resources", "max_collision_resources", "max_active_records", "max_pending_retirements", "max_render_fading_resources"]:
		aggregate[key] = max(int(aggregate.get(key, 0)), int(result.get(key, 0)))


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))
