extends SceneTree


const MARKER := "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const TELEMETRY_PATH := "res://artifacts/g41_runtime_frame_budget_telemetry_quality/frame_telemetry.json"
const EXPECTED_ACTIVE_RESOURCES := 25
const MAX_TRANSIENT_RESOURCES := 50
const MAX_SETTLE_FRAMES := 480
const MAX_RELOAD_FRAMES := 1800
const MAX_AVG_FRAME_MS := 80.0
const MAX_FRAME_SPIKE_MS := 1000.0
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

const ROUTE := [
	{"label": "northwest", "position": Vector3(264, 8, 264), "motion": Vector3(1, 0, 0)},
	{"label": "southeast", "position": Vector3(1784, 8, 1784), "motion": Vector3(-1, 0, 0)},
]

var _helpers: RefCounted
var _phases: Array[Dictionary] = []


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene := await _create_ready_scene("initial")
	if scene == null:
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	if not await _wait_for_material_stability(materializer, 1, "initial"):
		return
	var start_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var idle := _begin_phase("idle_settled", terrain_world, materializer)
	for _frame in range(120):
		await _record_frame(idle, terrain_world, materializer, false)
		if not _assert_cold_idle(terrain_world, "idle"):
			return
	_finish_phase(idle, terrain_world, materializer)
	for sample in ROUTE:
		if not await _measure_route_sample(scene, terrain_world, materializer, sample):
			return
	var edit_point := Vector3(1032, 8, 1032)
	if not _helpers.move_player_to(scene, edit_point):
		return
	if not await _wait_for_window_measured("edit_site_stream", terrain_world, materializer, 1, _chunk_for(edit_point)):
		return
	var before_edit_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not await _submit_edit_measured(scene, terrain_world, materializer, &"carve", edit_point):
		return
	if not await _submit_edit_measured(scene, terrain_world, materializer, &"construct", edit_point + Vector3(5, 0, 0)):
		return
	var after_edit_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	scene.queue_free()
	await process_frame
	var reload_scene := await _create_ready_scene("reload_after_edits")
	if reload_scene == null:
		return
	var reload_terrain: Node = _helpers.terrain_world(reload_scene)
	var reload_materializer: Node = reload_scene.get_node_or_null("ValidationTerrainMaterials")
	if not await _wait_for_material_stability(reload_materializer, 1, "reload"):
		return
	if not await _wait_for_window_measured("reload_settle", reload_terrain, reload_materializer, 1, _chunk_for(edit_point)):
		return
	if not _helpers.assert_no_dense_files("g41_finish"):
		return
	var summary := _summarize_phases()
	var edit_delta := int(after_edit_metrics.get("edit_replacements", 0)) - int(before_edit_metrics.get("edit_replacements", 0))
	var viewer_delta := int(after_edit_metrics.get("viewer_updates", 0)) - int(start_metrics.get("viewer_updates", 0))
	if edit_delta < 2:
		_helpers.fail("G41 edits did not replace terrain resources enough: delta=%d" % edit_delta)
		return
	if float(summary.get("max_avg_frame_ms", 9999.0)) > MAX_AVG_FRAME_MS or float(summary.get("max_frame_ms", 9999.0)) > MAX_FRAME_SPIKE_MS:
		_helpers.fail("G41 frame budget exceeded: %s" % str(summary))
		return
	if not _write_telemetry(summary):
		return
	print("%s profile=%s phases=%d total_frames=%d max_frame_ms=%.3f max_avg_frame_ms=%.3f movement_samples=%d edits=2 reload_ready_frames=%d viewer_update_delta=%d edit_replacement_delta=%d max_render_resources=%d max_collision_resources=%d max_active_records=%d max_queued_render=%d max_queued_collision=%d max_pending_retirements=%d max_render_fading_resources=%d dense_world_files=0 telemetry=%s" % [
		MARKER, str(PROFILE_ID), int(summary.get("phases", 0)), int(summary.get("total_frames", 0)),
		float(summary.get("max_frame_ms", 0.0)), float(summary.get("max_avg_frame_ms", 0.0)),
		ROUTE.size(), int(summary.get("reload_ready_frames", 0)), viewer_delta, edit_delta,
		int(summary.get("max_render_resources", 0)), int(summary.get("max_collision_resources", 0)),
		int(summary.get("max_active_records", 0)), int(summary.get("max_queued_render", 0)),
		int(summary.get("max_queued_collision", 0)), int(summary.get("max_pending_retirements", 0)),
		int(summary.get("max_render_fading_resources", 0)), TELEMETRY_PATH,
	])
	reload_scene.queue_free()
	await process_frame
	quit(0)


func _create_ready_scene(label: String) -> Node:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	var terrain_world: Node = _helpers.terrain_world(scene)
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var phase := _begin_phase("%s_ready" % label, terrain_world, materializer)
	for frame in range(MAX_RELOAD_FRAMES):
		await _record_frame(phase, terrain_world, materializer, false)
		if scene.has_method("get_validation_state") and scene.get_validation_state() == "ready":
			phase["ready_frames"] = frame + 1
			if label.begins_with("reload"):
				phase["reload_ready_frames"] = frame + 1
			_finish_phase(phase, terrain_world, materializer)
			if await _helpers.wait_for_player_floor(scene):
				return scene
			_helpers.fail("G41 player did not reach floor at %s" % label)
			return null
	_finish_phase(phase, terrain_world, materializer)
	_helpers.fail("G41 scene did not become ready at %s: %s" % [label, str(scene.get_validation_summary())])
	return null


func _measure_route_sample(scene: Node, terrain_world: Node, materializer: Node, sample: Dictionary) -> bool:
	var label := str(sample["label"])
	var position: Vector3 = sample["position"]
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not _helpers.move_player_to(scene, position):
		return false
	if not await _wait_for_window_measured(label + "_stream", terrain_world, materializer, int(before_metrics.get("viewer_updates", 0)) + 1, _chunk_for(position)):
		return false
	scene.set_player_test_motion(sample["motion"])
	var phase := _begin_phase(label + "_local_motion", terrain_world, materializer)
	for _frame in range(96):
		await _record_frame(phase, terrain_world, materializer, true)
	scene.clear_player_test_motion()
	_finish_phase(phase, terrain_world, materializer)
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G41 player did not settle after route sample %s" % label)
		return false
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	return await _wait_for_window_measured(label + "_local_settle", terrain_world, materializer, int(before_metrics.get("viewer_updates", 0)) + 1, _chunk_for(after))


func _submit_edit_measured(scene: Node, terrain_world: Node, materializer: Node, mode: StringName, point: Vector3) -> bool:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var phase := _begin_phase("edit_%s_commit" % str(mode), terrain_world, materializer)
	if not bool(interactor.call("submit_sphere_edit", mode, point, 1.8, 4, 1.0)):
		_helpers.fail("G41 edit submission failed: %s" % str(interactor.call("get_last_submission")))
		return false
	for _frame in range(MAX_SETTLE_FRAMES):
		await _record_frame(phase, terrain_world, materializer, false)
		if int(terrain_world.call("get_backend_world_revision")) >= before_revision + 1:
			_finish_phase(phase, terrain_world, materializer)
			return await _wait_for_window_measured("edit_%s_settle" % str(mode), terrain_world, materializer, 1, _chunk_for(point))
	_finish_phase(phase, terrain_world, materializer)
	_helpers.fail("G41 edit did not commit: %s" % str(mode))
	return false


func _wait_for_window_measured(label: String, terrain_world: Node, materializer: Node, minimum_viewer_updates: int, center_chunk: Vector3i) -> bool:
	var phase := _begin_phase(label, terrain_world, materializer)
	for _frame in range(MAX_SETTLE_FRAMES):
		await _record_frame(phase, terrain_world, materializer, false)
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		var active_records := int(metrics.get("active_chunk_records", 0))
		var center_ready := bool(_helpers.is_ready_snapshot(terrain_world.call("query_chunk_state", center_chunk, 0)))
		if active_records == EXPECTED_ACTIVE_RESOURCES and int(metrics.get("render_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and int(metrics.get("collision_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and center_ready and int(metrics.get("queued_render", 0)) == 0 and int(metrics.get("queued_collision", 0)) == 0 and int(metrics.get("pending_chunk_retirements", 0)) == 0:
			_finish_phase(phase, terrain_world, materializer)
			return true
	_finish_phase(phase, terrain_world, materializer)
	_helpers.fail("G41 window did not settle at %s: %s" % [label, str(terrain_world.call("get_runtime_metrics"))])
	return false


func _begin_phase(label: String, terrain_world: Node, materializer: Node) -> Dictionary:
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics") if terrain_world != null else {}
	var material: Dictionary = materializer.call("get_material_summary") if materializer != null else {}
	return {"label": label, "frames": 0, "total_us": 0, "max_us": 0, "start_viewer_updates": int(metrics.get("viewer_updates", 0)), "start_edit_replacements": int(metrics.get("edit_replacements", 0)), "start_material_auto_apply": int(material.get("auto_apply_count", 0)), "max_render_resources": 0, "max_collision_resources": 0, "max_active_records": 0, "max_queued_render": 0, "max_queued_collision": 0, "max_pending_retirements": 0, "max_render_fading_resources": 0}


func _record_frame(phase: Dictionary, terrain_world: Node, materializer: Node, include_physics: bool) -> void:
	var start_us := Time.get_ticks_usec()
	if include_physics:
		await physics_frame
	await process_frame
	var elapsed_us := Time.get_ticks_usec() - start_us
	phase["frames"] = int(phase.get("frames", 0)) + 1
	phase["total_us"] = int(phase.get("total_us", 0)) + elapsed_us
	phase["max_us"] = max(int(phase.get("max_us", 0)), elapsed_us)
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics") if terrain_world != null else {}
	phase["max_render_resources"] = max(int(phase.get("max_render_resources", 0)), int(metrics.get("render_resources", 0)))
	phase["max_collision_resources"] = max(int(phase.get("max_collision_resources", 0)), int(metrics.get("collision_resources", 0)))
	phase["max_active_records"] = max(int(phase.get("max_active_records", 0)), int(metrics.get("active_chunk_records", 0)))
	phase["max_queued_render"] = max(int(phase.get("max_queued_render", 0)), int(metrics.get("queued_render", 0)))
	phase["max_queued_collision"] = max(int(phase.get("max_queued_collision", 0)), int(metrics.get("queued_collision", 0)))
	phase["max_pending_retirements"] = max(int(phase.get("max_pending_retirements", 0)), int(metrics.get("pending_chunk_retirements", 0)))
	phase["max_render_fading_resources"] = max(int(phase.get("max_render_fading_resources", 0)), int(metrics.get("render_fading_resources", 0)))


func _finish_phase(phase: Dictionary, terrain_world: Node, materializer: Node) -> void:
	var frames: int = max(1, int(phase.get("frames", 0)))
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics") if terrain_world != null else {}
	var material: Dictionary = materializer.call("get_material_summary") if materializer != null else {}
	phase["avg_ms"] = float(phase.get("total_us", 0)) / float(frames) / 1000.0
	phase["max_frame_ms"] = float(phase.get("max_us", 0)) / 1000.0
	phase["viewer_update_delta"] = int(metrics.get("viewer_updates", 0)) - int(phase.get("start_viewer_updates", 0))
	phase["edit_replacement_delta"] = int(metrics.get("edit_replacements", 0)) - int(phase.get("start_edit_replacements", 0))
	phase["material_auto_apply_delta"] = int(material.get("auto_apply_count", 0)) - int(phase.get("start_material_auto_apply", 0))
	_phases.append(phase)


func _summarize_phases() -> Dictionary:
	var summary := {"phases": _phases.size(), "total_frames": 0, "max_frame_ms": 0.0, "max_avg_frame_ms": 0.0, "max_render_resources": 0, "max_collision_resources": 0, "max_active_records": 0, "max_queued_render": 0, "max_queued_collision": 0, "max_pending_retirements": 0, "max_render_fading_resources": 0, "reload_ready_frames": 0}
	for phase in _phases:
		summary["total_frames"] = int(summary["total_frames"]) + int(phase.get("frames", 0))
		summary["max_frame_ms"] = max(float(summary["max_frame_ms"]), float(phase.get("max_frame_ms", 0.0)))
		summary["max_avg_frame_ms"] = max(float(summary["max_avg_frame_ms"]), float(phase.get("avg_ms", 0.0)))
		for key in ["max_render_resources", "max_collision_resources", "max_active_records", "max_queued_render", "max_queued_collision", "max_pending_retirements", "max_render_fading_resources"]:
			summary[key] = max(int(summary[key]), int(phase.get(key, 0)))
		summary["reload_ready_frames"] = max(int(summary["reload_ready_frames"]), int(phase.get("reload_ready_frames", 0)))
	return summary


func _wait_for_material_stability(materializer: Node, min_auto_count: int, label: String) -> bool:
	if materializer == null:
		_helpers.fail("G41 materializer missing")
		return false
	var last_count := -1
	var stable_frames := 0
	for _frame in range(420):
		var summary: Dictionary = materializer.call("get_material_summary")
		var auto_count := int(summary.get("auto_apply_count", 0))
		if bool(summary.get("applied", false)) and int(summary.get("materialized_instances", 0)) >= EXPECTED_ACTIVE_RESOURCES and auto_count >= min_auto_count:
			if auto_count == last_count:
				stable_frames += 1
				if stable_frames >= 30:
					return true
			else:
				last_count = auto_count
				stable_frames = 0
		await process_frame
	_helpers.fail("G41 materials did not stabilize at %s: %s" % [label, str(materializer.call("get_material_summary"))])
	return false


func _assert_cold_idle(terrain_world: Node, label: String) -> bool:
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var cold: Dictionary = terrain_world.call("get_cold_idle_summary")
	if not bool(cold.get("cold_idle", false)) or int(metrics.get("render_fading_resources", 0)) != 0 or int(metrics.get("pending_chunk_retirements", 0)) != 0:
		_helpers.fail("G41 not cold idle at %s: metrics=%s cold=%s" % [label, str(metrics), str(cold)])
		return false
	return true


func _write_telemetry(summary: Dictionary) -> bool:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://artifacts/g41_runtime_frame_budget_telemetry_quality"))
	var file := FileAccess.open(TELEMETRY_PATH, FileAccess.WRITE)
	if file == null:
		_helpers.fail("G41 failed to write telemetry JSON")
		return false
	file.store_string(JSON.stringify({"summary": summary, "phases": _phases}, "\t"))
	file.store_string("\n")
	file.close()
	return true


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))
