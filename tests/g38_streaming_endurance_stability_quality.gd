extends SceneTree


const MARKER := "WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_PAGE_COUNT := 16384
const EXPECTED_ACTIVE_RESOURCES := 25
const MAX_TRANSITION_RESOURCES := 50
const MAX_SETTLE_FRAMES := 480
const ROUTE_CYCLES := 2
const LOCAL_MOTION_FRAMES := 48
const MIN_TOTAL_MOTION_METERS := 50.0
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
	_helpers = Helpers.new(self, "WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G38 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G38 backend page count mismatch")
		return
	var start_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var totals := _new_totals()
	for cycle in range(ROUTE_CYCLES):
		for sample in ROUTE:
			var result := await _run_sample(scene, terrain_world, sample, cycle)
			if result.is_empty():
				return
			_merge_totals(totals, result)
	var final_settle := await _wait_for_window(terrain_world, "final_cold_idle", int(start_metrics.get("viewer_updates", 0)) + 1, _chunk_for(scene.get_validation_summary().get("player_position", Vector3.ZERO)))
	if final_settle.is_empty():
		return
	_merge_totals(totals, final_settle)
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var final_cold: Dictionary = terrain_world.call("get_cold_idle_summary")
	if not bool(final_cold.get("cold_idle", false)) or \
			int(final_metrics.get("render_resources", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			int(final_metrics.get("collision_resources", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			int(final_metrics.get("active_chunk_records", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			int(final_metrics.get("pending_chunk_retirements", 0)) != 0:
		_helpers.fail("G38 final cold-idle leak check failed: metrics=%s cold=%s" % [str(final_metrics), str(final_cold)])
		return
	if float(totals.get("total_player_motion", 0.0)) < MIN_TOTAL_MOTION_METERS:
		_helpers.fail("G38 total local motion too small: %.3f" % float(totals.get("total_player_motion", 0.0)))
		return
	if not _helpers.assert_no_dense_files("g38_finish"):
		return
	print("%s profile=%s route_cycles=%d route_samples=%d local_motion_samples=%d total_player_motion=%.3f viewer_updates_delta=%d max_settle_frames=%d max_render_resources=%d max_collision_resources=%d max_active_records=%d max_pending_retirements=%d max_render_fading_resources=%d final_render_resources=%d final_collision_resources=%d final_active_records=%d final_cold_idle=true dense_world_files=0" % [
		MARKER, str(PROFILE_ID), ROUTE_CYCLES, ROUTE_CYCLES * ROUTE.size(),
		int(totals.get("local_motion_samples", 0)), float(totals.get("total_player_motion", 0.0)),
		int(final_metrics.get("viewer_updates", 0)) - int(start_metrics.get("viewer_updates", 0)),
		int(totals.get("max_settle_frames", 0)), int(totals.get("max_render_resources", 0)),
		int(totals.get("max_collision_resources", 0)), int(totals.get("max_active_records", 0)),
		int(totals.get("max_pending_retirements", 0)), int(totals.get("max_render_fading_resources", 0)),
		int(final_metrics.get("render_resources", 0)), int(final_metrics.get("collision_resources", 0)),
		int(final_metrics.get("active_chunk_records", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _run_sample(scene: Node, terrain_world: Node, sample: Dictionary, cycle: int) -> Dictionary:
	var label := "cycle_%d_%s" % [cycle + 1, str(sample["label"])]
	var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
	if not _helpers.move_player_to(scene, sample["position"]):
		return {}
	await process_frame
	var teleport := await _wait_for_window(terrain_world, label + "_teleport", before_updates + 1, _chunk_for(sample["position"]))
	if teleport.is_empty():
		return {}
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G38 player did not settle after teleport at %s" % label)
		return {}
	var moved := await _move_locally(scene, terrain_world, sample["motion"], label)
	if moved.is_empty():
		return {}
	return _merged(teleport, moved)


func _move_locally(scene: Node, terrain_world: Node, direction: Vector3, label: String) -> Dictionary:
	var before: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
	scene.set_camera_mode(&"first_person")
	scene.set_player_test_motion(direction)
	var tracked := _new_metrics()
	for frame in range(LOCAL_MOTION_FRAMES):
		await physics_frame
		await process_frame
		if not _track_or_fail(tracked, terrain_world.call("get_runtime_metrics"), "%s_motion_%d" % [label, frame]):
			scene.clear_player_test_motion()
			return {}
	scene.clear_player_test_motion()
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G38 player did not settle after local movement at %s" % label)
		return {}
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var settle := await _wait_for_window(terrain_world, label + "_settle", before_updates, _chunk_for(after))
	if settle.is_empty():
		return {}
	var result := _merged(tracked, settle)
	result["total_player_motion"] = _xz_distance(before, after)
	result["local_motion_samples"] = 1
	return result


func _wait_for_window(terrain_world: Node, label: String, minimum_viewer_updates: int, center_chunk: Vector3i) -> Dictionary:
	var tracked := _new_metrics()
	for frame in range(MAX_SETTLE_FRAMES):
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		if not _track_or_fail(tracked, metrics, "%s_%d" % [label, frame]):
			return {}
		var active_records := int(metrics.get("active_chunk_records", 0))
		if active_records == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("render_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("collision_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and \
				bool(_helpers.is_ready_snapshot(terrain_world.call("query_chunk_state", center_chunk, 0))) and \
				int(metrics.get("queued_render", 0)) == 0 and \
				int(metrics.get("queued_collision", 0)) == 0 and \
				int(metrics.get("fully_ready_chunk_records", -1)) == active_records and \
				int(metrics.get("pending_chunk_retirements", 0)) == 0:
			tracked["max_settle_frames"] = max(int(tracked.get("max_settle_frames", 0)), frame + 1)
			return tracked
		await process_frame
	_helpers.fail("G38 window did not settle at %s: %s" % [label, str(terrain_world.call("get_runtime_metrics"))])
	return {}


func _track_or_fail(tracked: Dictionary, metrics: Dictionary, label: String) -> bool:
	tracked["max_render_resources"] = max(int(tracked.get("max_render_resources", 0)), int(metrics.get("render_resources", 0)))
	tracked["max_collision_resources"] = max(int(tracked.get("max_collision_resources", 0)), int(metrics.get("collision_resources", 0)))
	tracked["max_active_records"] = max(int(tracked.get("max_active_records", 0)), int(metrics.get("active_chunk_records", 0)))
	tracked["max_pending_retirements"] = max(int(tracked.get("max_pending_retirements", 0)), int(metrics.get("pending_chunk_retirements", 0)))
	tracked["max_render_fading_resources"] = max(int(tracked.get("max_render_fading_resources", 0)), int(metrics.get("render_fading_resources", 0)))
	if int(metrics.get("render_resources", 0)) > MAX_TRANSITION_RESOURCES or \
			int(metrics.get("collision_resources", 0)) > MAX_TRANSITION_RESOURCES or \
			int(metrics.get("active_chunk_records", 0)) > MAX_TRANSITION_RESOURCES or \
			int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G38 resource/fade spike at %s: %s" % [label, str(metrics)])
		return false
	return true


func _new_metrics() -> Dictionary:
	return {"max_settle_frames": 0, "max_render_resources": 0, "max_collision_resources": 0, "max_active_records": 0, "max_pending_retirements": 0, "max_render_fading_resources": 0}


func _new_totals() -> Dictionary:
	var totals := _new_metrics()
	totals["total_player_motion"] = 0.0
	totals["local_motion_samples"] = 0
	return totals


func _merge_totals(totals: Dictionary, metrics: Dictionary) -> void:
	for key in _new_metrics().keys():
		totals[key] = max(int(totals.get(key, 0)), int(metrics.get(key, 0)))
	totals["total_player_motion"] = float(totals.get("total_player_motion", 0.0)) + float(metrics.get("total_player_motion", 0.0))
	totals["local_motion_samples"] = int(totals.get("local_motion_samples", 0)) + int(metrics.get("local_motion_samples", 0))


func _merged(a: Dictionary, b: Dictionary) -> Dictionary:
	var result := _new_totals()
	_merge_totals(result, a)
	_merge_totals(result, b)
	return result


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))


func _xz_distance(a: Vector3, b: Vector3) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()
