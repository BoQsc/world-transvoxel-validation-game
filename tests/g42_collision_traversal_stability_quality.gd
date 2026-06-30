extends SceneTree


const MARKER := "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_COMPACT_ACTIVE := 25
const MAX_ACTIVE_RESOURCES := 64
const MIN_FLOOR_CONTACT_RATIO := 0.72
const MAX_OFF_FLOOR_STREAK := 36
const MIN_SEGMENT_MOTION := 4.0
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

const CASES := [
	{
		"label": "flat",
		"profile": &"flat_8x8",
		"start": Vector3(64, 12, 64),
		"segments": [Vector3(1, 0, 0), Vector3(0, 0, 1)],
		"frames": 90,
		"edit": false,
	},
	{
		"label": "mountain",
		"profile": &"mountain_8x8",
		"start": Vector3(64, 24, 64),
		"segments": [Vector3(1, 0, 0), Vector3(0, 0, -1)],
		"frames": 90,
		"edit": false,
	},
	{
		"label": "compact_edited",
		"profile": &"g19_compact_2k_on_demand",
		"start": Vector3(1032, 24, 1032),
		"segments": [Vector3(1, 0, 0), Vector3(0, 0, 1)],
		"frames": 120,
		"edit": true,
	},
]

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var aggregate := _new_aggregate()
	for case in CASES:
		var result := await _run_case(case)
		if result.is_empty():
			return
		_merge_aggregate(aggregate, result)
	if not _helpers.assert_no_dense_files("g42_finish"):
		return
	print("%s profile_cases=%d route_segments=%d edited_segments=%d total_motion=%.3f min_floor_contact_ratio=%.3f max_off_floor_streak=%d min_player_y=%.3f max_abs_vertical_velocity=%.3f max_render_resources=%d max_collision_resources=%d max_active_records=%d max_render_fading_resources=%d dense_world_files=0" % [
		MARKER,
		CASES.size(),
		int(aggregate.get("route_segments", 0)),
		int(aggregate.get("edited_segments", 0)),
		float(aggregate.get("total_motion", 0.0)),
		float(aggregate.get("min_floor_contact_ratio", 1.0)),
		int(aggregate.get("max_off_floor_streak", 0)),
		float(aggregate.get("min_player_y", 0.0)),
		float(aggregate.get("max_abs_vertical_velocity", 0.0)),
		int(aggregate.get("max_render_resources", 0)),
		int(aggregate.get("max_collision_resources", 0)),
		int(aggregate.get("max_active_records", 0)),
		int(aggregate.get("max_render_fading_resources", 0)),
	])
	quit(0)


func _run_case(case: Dictionary) -> Dictionary:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(case["profile"])
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _wait_for_stable_floor(scene, str(case["label"]) + "_ready"):
		_helpers.fail("G42 scene did not become playable for %s: %s" % [str(case["label"]), str(scene.get_validation_summary())])
		return {}
	var terrain_world: Node = _helpers.terrain_world(scene)
	if not _helpers.move_player_to(scene, case["start"]) or not await _wait_for_stable_floor(scene, str(case["label"]) + "_start"):
		_helpers.fail("G42 player did not settle at case start: %s" % str(case["label"]))
		return {}
	if bool(case.get("edit", false)) and not await _submit_stability_edit(scene, terrain_world, case["start"]):
		return {}
	var result := _new_case_result()
	for direction in Array(case["segments"]):
		var segment := await _run_traversal_segment(scene, terrain_world, direction, int(case["frames"]), str(case["label"]))
		if segment.is_empty():
			return {}
		_merge_case_result(result, segment)
		result["route_segments"] = int(result.get("route_segments", 0)) + 1
		if bool(case.get("edit", false)):
			result["edited_segments"] = int(result.get("edited_segments", 0)) + 1
	scene.queue_free()
	await process_frame
	return result


func _run_traversal_segment(scene: Node, terrain_world: Node, direction: Vector3, frames: int, label: String) -> Dictionary:
	var before: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var result := _new_case_result()
	var floor_hits := 0
	var off_floor_streak := 0
	var max_streak := 0
	scene.set_player_test_motion(direction)
	for _frame in range(frames):
		await physics_frame
		await process_frame
		var summary: Dictionary = scene.get_validation_summary()
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		if bool(summary.get("player_human_input_enabled", true)) or not bool(summary.get("player_simulation_enabled", false)) or not bool(summary.get("player_camera_current", false)):
			scene.clear_player_test_motion()
			_helpers.fail("G42 control state invalid at %s: %s" % [label, str(summary)])
			return {}
		if bool(summary.get("player_on_floor", false)):
			floor_hits += 1
			off_floor_streak = 0
		else:
			off_floor_streak += 1
			max_streak = max(max_streak, off_floor_streak)
		var position: Vector3 = summary.get("player_position", Vector3.ZERO)
		result["min_player_y"] = min(float(result.get("min_player_y", 9999.0)), position.y)
		result["max_abs_vertical_velocity"] = max(float(result.get("max_abs_vertical_velocity", 0.0)), absf(float(summary.get("vertical_velocity", 0.0))))
		_track_resources(result, metrics, label)
		if position.y < -10.0 or off_floor_streak > MAX_OFF_FLOOR_STREAK:
			scene.clear_player_test_motion()
			_helpers.fail("G42 traversal lost floor/contact at %s: position=%s streak=%d" % [label, str(position), off_floor_streak])
			return {}
	scene.clear_player_test_motion()
	for _frame in range(20):
		await physics_frame
	if not await _wait_for_stable_floor(scene, label + "_after_segment"):
		return {}
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var moved := before.distance_to(after)
	var ratio := float(floor_hits) / float(max(1, frames))
	if moved < MIN_SEGMENT_MOTION or ratio < MIN_FLOOR_CONTACT_RATIO:
		_helpers.fail("G42 weak traversal at %s: moved=%.3f floor_ratio=%.3f" % [label, moved, ratio])
		return {}
	result["total_motion"] = moved
	result["min_floor_contact_ratio"] = ratio
	result["max_off_floor_streak"] = max_streak
	return result


func _wait_for_stable_floor(scene: Node, label: String) -> bool:
	var stable_frames := 0
	for _frame in range(360):
		var summary: Dictionary = scene.get_validation_summary()
		if bool(summary.get("player_on_floor", false)) and absf(float(summary.get("vertical_velocity", 0.0))) < 0.05:
			stable_frames += 1
			if stable_frames >= 20:
				return true
		else:
			stable_frames = 0
		await physics_frame
	_helpers.fail("G42 stable floor not reached at %s: %s" % [label, str(scene.get_validation_summary())])
	return false


func _submit_stability_edit(scene: Node, terrain_world: Node, start: Vector3) -> bool:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	var revision := int(terrain_world.call("get_backend_world_revision"))
	var edit_point := start + Vector3(8, -1, 0)
	if not bool(interactor.call("submit_sphere_edit", &"construct", edit_point, 1.8, 4, 1.0)):
		_helpers.fail("G42 stability edit rejected: %s" % str(interactor.call("get_last_submission")))
		return false
	if not await _helpers.wait_for_revision(terrain_world, revision + 1):
		return false
	return await _helpers.wait_for_window(terrain_world, EXPECTED_COMPACT_ACTIVE, "g42_after_edit", 1, _chunk_for(start), EXPECTED_COMPACT_ACTIVE)


func _track_resources(result: Dictionary, metrics: Dictionary, label: String) -> void:
	result["max_render_resources"] = max(int(result.get("max_render_resources", 0)), int(metrics.get("render_resources", 0)))
	result["max_collision_resources"] = max(int(result.get("max_collision_resources", 0)), int(metrics.get("collision_resources", 0)))
	result["max_active_records"] = max(int(result.get("max_active_records", 0)), int(metrics.get("active_chunk_records", 0)))
	result["max_render_fading_resources"] = max(int(result.get("max_render_fading_resources", 0)), int(metrics.get("render_fading_resources", 0)))
	if int(result.get("max_render_resources", 0)) > MAX_ACTIVE_RESOURCES or int(result.get("max_collision_resources", 0)) > MAX_ACTIVE_RESOURCES or int(result.get("max_active_records", 0)) > MAX_ACTIVE_RESOURCES or int(result.get("max_render_fading_resources", 0)) != 0:
		_helpers.fail("G42 resource/fade instability at %s: %s" % [label, str(metrics)])


func _new_case_result() -> Dictionary:
	return {"route_segments": 0, "edited_segments": 0, "total_motion": 0.0, "min_floor_contact_ratio": 1.0, "max_off_floor_streak": 0, "min_player_y": 9999.0, "max_abs_vertical_velocity": 0.0, "max_render_resources": 0, "max_collision_resources": 0, "max_active_records": 0, "max_render_fading_resources": 0}


func _new_aggregate() -> Dictionary:
	return _new_case_result()


func _merge_case_result(result: Dictionary, segment: Dictionary) -> void:
	_merge_aggregate(result, segment)


func _merge_aggregate(aggregate: Dictionary, result: Dictionary) -> void:
	aggregate["route_segments"] = int(aggregate.get("route_segments", 0)) + int(result.get("route_segments", 0))
	aggregate["edited_segments"] = int(aggregate.get("edited_segments", 0)) + int(result.get("edited_segments", 0))
	aggregate["total_motion"] = float(aggregate.get("total_motion", 0.0)) + float(result.get("total_motion", 0.0))
	aggregate["min_floor_contact_ratio"] = min(float(aggregate.get("min_floor_contact_ratio", 1.0)), float(result.get("min_floor_contact_ratio", 1.0)))
	aggregate["max_off_floor_streak"] = max(int(aggregate.get("max_off_floor_streak", 0)), int(result.get("max_off_floor_streak", 0)))
	aggregate["min_player_y"] = min(float(aggregate.get("min_player_y", 9999.0)), float(result.get("min_player_y", 9999.0)))
	aggregate["max_abs_vertical_velocity"] = max(float(aggregate.get("max_abs_vertical_velocity", 0.0)), float(result.get("max_abs_vertical_velocity", 0.0)))
	for key in ["max_render_resources", "max_collision_resources", "max_active_records", "max_render_fading_resources"]:
		aggregate[key] = max(int(aggregate.get(key, 0)), int(result.get(key, 0)))


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))
