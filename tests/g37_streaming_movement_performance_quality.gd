extends SceneTree


const MARKER := "WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_PAGE_COUNT := 16384
const EXPECTED_ACTIVE_RESOURCES := 25
const MAX_TRANSITION_RESOURCES := 50
const MAX_SETTLE_FRAMES := 480
const LOCAL_MOTION_FRAMES := 96
const MIN_LOCAL_MOTION_METERS := 8.0
const MAX_MATERIAL_APPLIES_PER_SAMPLE := 4
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

const ROUTE := [
	{"label": "northwest", "position": Vector3(264, 8, 264), "motion": Vector3(1, 0, 0)},
	{"label": "northeast", "position": Vector3(1784, 8, 264), "motion": Vector3(0, 0, 1)},
	{"label": "southeast", "position": Vector3(1784, 8, 1784), "motion": Vector3(-1, 0, 0)},
	{"label": "southwest", "position": Vector3(264, 8, 1784), "motion": Vector3(0, 0, -1)},
	{"label": "center_return", "position": Vector3(1032, 8, 1032), "motion": Vector3(1, 0, 0)},
]

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G37 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G37 backend page count mismatch")
		return
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var material_summary := await _wait_for_material_stability(materializer, 1, "initial")
	if material_summary.is_empty():
		return
	var start_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var max_settle_frames := 0
	var max_render_resources := 0
	var max_collision_resources := 0
	var max_active_records := 0
	var max_queued_render := 0
	var max_queued_collision := 0
	var max_pending_retirements := 0
	var max_render_fading_resources := 0
	var max_material_auto_delta := 0
	var total_player_motion := 0.0
	var local_motion_samples := 0
	for sample in ROUTE:
		var result := await _verify_route_sample(scene, terrain_world, materializer, sample)
		if result.is_empty():
			return
		max_settle_frames = max(max_settle_frames, int(result.get("max_settle_frames", 0)))
		max_render_resources = max(max_render_resources, int(result.get("max_render_resources", 0)))
		max_collision_resources = max(max_collision_resources, int(result.get("max_collision_resources", 0)))
		max_active_records = max(max_active_records, int(result.get("max_active_records", 0)))
		max_queued_render = max(max_queued_render, int(result.get("max_queued_render", 0)))
		max_queued_collision = max(max_queued_collision, int(result.get("max_queued_collision", 0)))
		max_pending_retirements = max(max_pending_retirements, int(result.get("max_pending_retirements", 0)))
		max_render_fading_resources = max(max_render_fading_resources, int(result.get("max_render_fading_resources", 0)))
		max_material_auto_delta = max(max_material_auto_delta, int(result.get("material_auto_delta", 0)))
		total_player_motion += float(result.get("local_motion_meters", 0.0))
		local_motion_samples += 1
	if not _helpers.assert_no_dense_files("g37_finish"):
		return
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	print("%s profile=%s route_samples=%d local_motion_samples=%d total_player_motion=%.3f viewer_updates_delta=%d max_settle_frames=%d max_render_resources=%d max_collision_resources=%d max_active_records=%d max_queued_render=%d max_queued_collision=%d max_pending_retirements=%d max_render_fading_resources=%d max_material_auto_apply_delta=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		ROUTE.size(),
		local_motion_samples,
		total_player_motion,
		int(final_metrics.get("viewer_updates", 0)) - int(start_metrics.get("viewer_updates", 0)),
		max_settle_frames,
		max_render_resources,
		max_collision_resources,
		max_active_records,
		max_queued_render,
		max_queued_collision,
		max_pending_retirements,
		max_render_fading_resources,
		max_material_auto_delta,
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _verify_route_sample(scene: Node, terrain_world: Node, materializer: Node, sample: Dictionary) -> Dictionary:
	var label := str(sample["label"])
	var position: Vector3 = sample["position"]
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var before_material: Dictionary = materializer.call("get_material_summary")
	if not _helpers.move_player_to(scene, position):
		return {}
	await process_frame
	var center_chunk := _chunk_for(position)
	var teleport := await _wait_for_window_timed(
		terrain_world,
		label + "_teleport",
		int(before_metrics.get("viewer_updates", 0)) + 1,
		center_chunk
	)
	if teleport.is_empty() or not await _helpers.wait_for_player_floor(scene):
		return {}
	var teleport_material := await _wait_for_material_stability(
		materializer,
		int(before_material.get("auto_apply_count", 0)) + 1,
		label + "_teleport"
	)
	if teleport_material.is_empty():
		return {}
	var moved := await _move_locally(scene, terrain_world, sample["motion"], label)
	if moved.is_empty():
		return {}
	var final_material := await _wait_for_material_stability(
		materializer,
		int(teleport_material.get("auto_apply_count", 0)) + 1,
		label + "_local_motion"
	)
	if final_material.is_empty():
		return {}
	var material_delta := int(final_material.get("auto_apply_count", 0)) - int(before_material.get("auto_apply_count", 0))
	if material_delta > MAX_MATERIAL_APPLIES_PER_SAMPLE:
		_helpers.fail("G37 material auto-apply churn at %s: delta=%d summary=%s" % [
			label,
			material_delta,
			str(final_material),
		])
		return {}
	return _merge_transition_metrics(teleport, moved, material_delta)


func _move_locally(scene: Node, terrain_world: Node, direction: Vector3, label: String) -> Dictionary:
	var before: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
	scene.set_camera_mode(&"first_person")
	scene.set_player_test_motion(direction)
	var motion_metrics := _new_transition_metrics()
	for frame in range(LOCAL_MOTION_FRAMES):
		await physics_frame
		await process_frame
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		if not _track_metrics_or_fail(motion_metrics, metrics, "%s_motion_%d" % [label, frame]):
			scene.clear_player_test_motion()
			return {}
	scene.clear_player_test_motion()
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G37 player did not settle after local movement at %s" % label)
		return {}
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var moved := before.distance_to(after)
	if moved < MIN_LOCAL_MOTION_METERS:
		_helpers.fail("G37 local player motion too small at %s: %.3f" % [label, moved])
		return {}
	var center_chunk := _chunk_for(after)
	var settle := await _wait_for_window_timed(terrain_world, label + "_local_settle", before_updates + 1, center_chunk)
	if settle.is_empty():
		return {}
	var result := _merge_transition_metrics(motion_metrics, settle, 0)
	result["local_motion_meters"] = moved
	return result


func _wait_for_window_timed(
	terrain_world: Node,
	label: String,
	minimum_viewer_updates: int,
	center_chunk: Vector3i
) -> Dictionary:
	var tracked := _new_transition_metrics()
	var last_center_ready := false
	for frame in range(MAX_SETTLE_FRAMES):
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		if not _track_metrics_or_fail(tracked, metrics, "%s_%d" % [label, frame]):
			return {}
		var active_records := int(metrics.get("active_chunk_records", 0))
		var center_ready := bool(_helpers.is_ready_snapshot(terrain_world.call("query_chunk_state", center_chunk, 0)))
		last_center_ready = center_ready
		if active_records == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("render_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("collision_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and \
				center_ready and \
				int(metrics.get("queued_render", 0)) == 0 and \
				int(metrics.get("queued_collision", 0)) == 0 and \
				int(metrics.get("fully_ready_chunk_records", -1)) == active_records and \
				int(metrics.get("pending_chunk_retirements", 0)) == 0:
			tracked["max_settle_frames"] = max(int(tracked.get("max_settle_frames", 0)), frame + 1)
			return tracked
		await process_frame
	_helpers.fail("G37 movement window did not settle at %s center=%s center_ready=%s metrics=%s" % [
		label,
		str(center_chunk),
		str(last_center_ready),
		str(terrain_world.call("get_runtime_metrics")),
	])
	return {}


func _track_metrics_or_fail(tracked: Dictionary, metrics: Dictionary, label: String) -> bool:
	tracked["max_render_resources"] = max(int(tracked.get("max_render_resources", 0)), int(metrics.get("render_resources", 0)))
	tracked["max_collision_resources"] = max(int(tracked.get("max_collision_resources", 0)), int(metrics.get("collision_resources", 0)))
	tracked["max_active_records"] = max(int(tracked.get("max_active_records", 0)), int(metrics.get("active_chunk_records", 0)))
	tracked["max_queued_render"] = max(int(tracked.get("max_queued_render", 0)), int(metrics.get("queued_render", 0)))
	tracked["max_queued_collision"] = max(int(tracked.get("max_queued_collision", 0)), int(metrics.get("queued_collision", 0)))
	tracked["max_pending_retirements"] = max(int(tracked.get("max_pending_retirements", 0)), int(metrics.get("pending_chunk_retirements", 0)))
	tracked["max_render_fading_resources"] = max(int(tracked.get("max_render_fading_resources", 0)), int(metrics.get("render_fading_resources", 0)))
	if int(metrics.get("render_resources", 0)) > MAX_TRANSITION_RESOURCES or \
			int(metrics.get("collision_resources", 0)) > MAX_TRANSITION_RESOURCES or \
			int(metrics.get("active_chunk_records", 0)) > MAX_TRANSITION_RESOURCES or \
			int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G37 resource or fade spike at %s: %s" % [label, str(metrics)])
		return false
	return true


func _wait_for_material_stability(materializer: Node, min_auto_count: int, label: String) -> Dictionary:
	if materializer == null:
		_helpers.fail("G37 materializer missing")
		return {}
	var last_count := -1
	var stable_frames := 0
	for _frame in range(420):
		var summary: Dictionary = materializer.call("get_material_summary")
		var auto_count := int(summary.get("auto_apply_count", 0))
		if bool(summary.get("applied", false)) and \
				int(summary.get("materialized_instances", 0)) >= EXPECTED_ACTIVE_RESOURCES and \
				auto_count >= min_auto_count:
			if auto_count == last_count:
				stable_frames += 1
				if stable_frames >= 30:
					return summary
			else:
				last_count = auto_count
				stable_frames = 0
		await process_frame
	_helpers.fail("G37 materials did not become stable at %s: %s" % [
		label,
		str(materializer.call("get_material_summary")),
	])
	return {}


func _new_transition_metrics() -> Dictionary:
	return {
		"max_settle_frames": 0,
		"max_render_resources": 0,
		"max_collision_resources": 0,
		"max_active_records": 0,
		"max_queued_render": 0,
		"max_queued_collision": 0,
		"max_pending_retirements": 0,
		"max_render_fading_resources": 0,
	}


func _merge_transition_metrics(a: Dictionary, b: Dictionary, material_delta: int) -> Dictionary:
	var result := _new_transition_metrics()
	for key in result.keys():
		result[key] = max(int(a.get(key, 0)), int(b.get(key, 0)))
	result["material_auto_delta"] = max(
		material_delta,
		max(int(a.get("material_auto_delta", 0)), int(b.get("material_auto_delta", 0)))
	)
	result["local_motion_meters"] = max(float(a.get("local_motion_meters", 0.0)), float(b.get("local_motion_meters", 0.0)))
	return result


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(
		clamp(int(floor(position.x / 16.0)), 0, 127),
		0,
		clamp(int(floor(position.z / 16.0)), 0, 127)
	)
