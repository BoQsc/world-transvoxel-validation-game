extends SceneTree


const MARKER := "WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_ACTIVE_RESOURCES := 25
const IDLE_FRAMES := 300
const MATERIAL_STABLE_FRAMES := 60
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G36 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	if terrain_world == null:
		_helpers.fail("G36 terrain world missing")
		return
	if not await _helpers.wait_for_window(
		terrain_world,
		EXPECTED_ACTIVE_RESOURCES,
		"initial_cold_idle",
		0,
		Vector3i(64, 0, 64),
		EXPECTED_ACTIVE_RESOURCES
	):
		return
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var material_summary := await _wait_for_material_stability(materializer, "initial")
	if material_summary.is_empty():
		return
	var baseline_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var baseline_cold: Dictionary = terrain_world.call("get_cold_idle_summary")
	if not _assert_settled_metrics("baseline", baseline_metrics, baseline_cold):
		return
	var idle := await _audit_idle_window(terrain_world, materializer, baseline_metrics, material_summary)
	if idle.is_empty():
		return
	if not _helpers.assert_no_dense_files("g36_finish"):
		return
	print("%s profile=%s idle_frames=%d viewer_update_delta=%d edit_replacement_delta=%d material_auto_apply_delta=%d max_render_resources=%d max_collision_resources=%d max_active_records=%d max_queued_render=%d max_queued_collision=%d max_pending_retirements=%d max_render_fading_resources=%d cold_idle=true dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		IDLE_FRAMES,
		int(idle.get("viewer_update_delta", -1)),
		int(idle.get("edit_replacement_delta", -1)),
		int(idle.get("material_auto_apply_delta", -1)),
		int(idle.get("max_render_resources", -1)),
		int(idle.get("max_collision_resources", -1)),
		int(idle.get("max_active_records", -1)),
		int(idle.get("max_queued_render", -1)),
		int(idle.get("max_queued_collision", -1)),
		int(idle.get("max_pending_retirements", -1)),
		int(idle.get("max_render_fading_resources", -1)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _wait_for_material_stability(materializer: Node, label: String) -> Dictionary:
	if materializer == null:
		_helpers.fail("G36 materializer missing")
		return {}
	var last_count := -1
	var stable_frames := 0
	for _frame in range(600):
		var summary: Dictionary = materializer.call("get_material_summary")
		var auto_count := int(summary.get("auto_apply_count", 0))
		if bool(summary.get("applied", false)) and \
				int(summary.get("materialized_instances", 0)) >= EXPECTED_ACTIVE_RESOURCES and \
				auto_count > 0:
			if auto_count == last_count:
				stable_frames += 1
				if stable_frames >= MATERIAL_STABLE_FRAMES:
					return summary
			else:
				last_count = auto_count
				stable_frames = 0
		await process_frame
	_helpers.fail("G36 materials did not become stable at %s: %s" % [
		label,
		str(materializer.call("get_material_summary")),
	])
	return {}


func _audit_idle_window(
	terrain_world: Node,
	materializer: Node,
	baseline_metrics: Dictionary,
	baseline_material: Dictionary
) -> Dictionary:
	var baseline_viewer_updates := int(baseline_metrics.get("viewer_updates", 0))
	var baseline_edit_replacements := int(baseline_metrics.get("edit_replacements", 0))
	var baseline_auto_apply := int(baseline_material.get("auto_apply_count", 0))
	var max_render_resources := 0
	var max_collision_resources := 0
	var max_active_records := 0
	var max_queued_render := 0
	var max_queued_collision := 0
	var max_pending_retirements := 0
	var max_render_fading_resources := 0
	for frame in range(IDLE_FRAMES):
		await process_frame
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		var cold: Dictionary = terrain_world.call("get_cold_idle_summary")
		if not _assert_settled_metrics("idle_frame_%d" % frame, metrics, cold):
			return {}
		max_render_resources = max(max_render_resources, int(metrics.get("render_resources", 0)))
		max_collision_resources = max(max_collision_resources, int(metrics.get("collision_resources", 0)))
		max_active_records = max(max_active_records, int(metrics.get("active_chunk_records", 0)))
		max_queued_render = max(max_queued_render, int(metrics.get("queued_render", 0)))
		max_queued_collision = max(max_queued_collision, int(metrics.get("queued_collision", 0)))
		max_pending_retirements = max(max_pending_retirements, int(metrics.get("pending_chunk_retirements", 0)))
		max_render_fading_resources = max(max_render_fading_resources, int(metrics.get("render_fading_resources", 0)))
		var material_summary: Dictionary = materializer.call("get_material_summary")
		if int(material_summary.get("auto_apply_count", 0)) != baseline_auto_apply:
			_helpers.fail("G36 material auto-apply churn during idle: baseline=%d current=%s" % [
				baseline_auto_apply,
				str(material_summary),
			])
			return {}
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var final_material: Dictionary = materializer.call("get_material_summary")
	var viewer_delta := int(final_metrics.get("viewer_updates", 0)) - baseline_viewer_updates
	var edit_delta := int(final_metrics.get("edit_replacements", 0)) - baseline_edit_replacements
	var material_delta := int(final_material.get("auto_apply_count", 0)) - baseline_auto_apply
	if viewer_delta != 0 or edit_delta != 0 or material_delta != 0:
		_helpers.fail("G36 idle counters changed: viewer=%d edit=%d material=%d final_metrics=%s final_material=%s" % [
			viewer_delta,
			edit_delta,
			material_delta,
			str(final_metrics),
			str(final_material),
		])
		return {}
	return {
		"viewer_update_delta": viewer_delta,
		"edit_replacement_delta": edit_delta,
		"material_auto_apply_delta": material_delta,
		"max_render_resources": max_render_resources,
		"max_collision_resources": max_collision_resources,
		"max_active_records": max_active_records,
		"max_queued_render": max_queued_render,
		"max_queued_collision": max_queued_collision,
		"max_pending_retirements": max_pending_retirements,
		"max_render_fading_resources": max_render_fading_resources,
	}


func _assert_settled_metrics(label: String, metrics: Dictionary, cold: Dictionary) -> bool:
	var active_records := int(metrics.get("active_chunk_records", 0))
	if not bool(cold.get("cold_idle", false)) or \
			active_records != EXPECTED_ACTIVE_RESOURCES or \
			int(metrics.get("fully_ready_chunk_records", -1)) != active_records or \
			int(metrics.get("render_resources", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			int(metrics.get("collision_resources", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			int(metrics.get("queued_render", 0)) != 0 or \
			int(metrics.get("queued_collision", 0)) != 0 or \
			int(metrics.get("pending_chunk_retirements", 0)) != 0 or \
			int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G36 runtime not cold-idle at %s: metrics=%s cold=%s" % [
			label,
			str(metrics),
			str(cold),
		])
		return false
	return true
