extends SceneTree


const MARKER := "WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const CAPTURE_ROOT := "res://artifacts/g40_edit_visual_material_feedback_quality"
const EXPECTED_ACTIVE_RESOURCES := 25
const MIN_CHANGED_SAMPLES := 200
const MIN_COLORED_SAMPLES := 1000
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted
var _sample_results := {}
var _sample_failures := {}


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G40 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain")
	_connect_backend(backend)
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var edit_point := Vector3(1032, 8, 1032)
	if not _helpers.move_player_to(scene, edit_point):
		return
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g40_edit_site", 1, _chunk_for(edit_point), EXPECTED_ACTIVE_RESOURCES):
		return
	var initial_material := await _wait_for_material_stability(materializer, 1, "initial")
	if initial_material.is_empty():
		return
	var before := await _capture_patch(scene, "before_edit", edit_point)
	if before.is_empty():
		return
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var carve := await _submit_edit(scene, terrain_world, backend, &"carve", edit_point, -1, 1.0)
	if carve.is_empty():
		return
	var construct_point := edit_point + Vector3(5, 0, 0)
	var construct := await _submit_edit(scene, terrain_world, backend, &"construct", construct_point, 4, -1.0)
	if construct.is_empty():
		return
	var after_material := await _wait_for_material_stability(
		materializer,
		int(initial_material.get("auto_apply_count", 0)) + 1,
		"after_edits"
	)
	if after_material.is_empty():
		return
	var after := await _capture_patch(scene, "after_edit", edit_point)
	if after.is_empty():
		return
	var diff := _image_difference(before["image"], after["image"])
	if int(diff.get("changed_samples", 0)) < MIN_CHANGED_SAMPLES:
		_helpers.fail("G40 edit did not produce enough visual image delta: %s" % str(diff))
		return
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var material_delta := int(after_material.get("auto_apply_count", 0)) - int(initial_material.get("auto_apply_count", 0))
	if int(final_metrics.get("render_fading_resources", 0)) != 0 or int(final_metrics.get("pending_chunk_retirements", 0)) != 0:
		_helpers.fail("G40 final runtime not settled: %s" % str(final_metrics))
		return
	if not _helpers.assert_no_dense_files("g40_finish"):
		return
	print("%s profile=%s edits=2 changed_samples=%d before_colored_samples=%d after_colored_samples=%d material_auto_apply_delta=%d max_commit_frames=%d max_settle_frames=%d max_render_resources=%d max_collision_resources=%d edit_replacement_delta=%d dense_world_files=0" % [
		MARKER, str(PROFILE_ID), int(diff.get("changed_samples", 0)),
		int(before.get("colored_samples", 0)), int(after.get("colored_samples", 0)),
		material_delta, max(int(carve.get("commit_frames", 0)), int(construct.get("commit_frames", 0))),
		max(int(carve.get("settle_frames", 0)), int(construct.get("settle_frames", 0))),
		int(final_metrics.get("render_resources", 0)), int(final_metrics.get("collision_resources", 0)),
		int(final_metrics.get("edit_replacements", 0)) - int(before_metrics.get("edit_replacements", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _submit_edit(scene: Node, terrain_world: Node, backend: Node, mode: StringName, point: Vector3, material: int, density: float) -> Dictionary:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var start_frame := Engine.get_physics_frames()
	if not bool(interactor.call("submit_sphere_edit", mode, point, 1.8, material, 1.0)):
		_helpers.fail("G40 edit submission failed: %s" % str(interactor.call("get_last_submission")))
		return {}
	if not await _helpers.wait_for_revision(terrain_world, before_revision + 1):
		return {}
	var commit_frames := Engine.get_physics_frames() - start_frame
	var settle_start := Engine.get_physics_frames()
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g40_after_%s" % str(mode), 1, _chunk_for(point), EXPECTED_ACTIVE_RESOURCES):
		return {}
	var settle_frames := Engine.get_physics_frames() - settle_start
	if not await _verify_sample(backend, Vector3i(point), density, material):
		return {}
	return {"commit_frames": commit_frames, "settle_frames": settle_frames}


func _capture_patch(scene: Node, label: String, target: Vector3) -> Dictionary:
	_set_overlays_visible(scene, false)
	scene.set_player_visual_visible(false)
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 72.0
	camera.far = 500.0
	camera.global_position = target + Vector3(0, 120, 0)
	camera.look_at(target, Vector3.FORWARD)
	for _frame in range(30):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_helpers.fail("G40 empty capture: %s" % label)
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var path := "%s/%s.png" % [CAPTURE_ROOT, label]
	var absolute_path := ProjectSettings.globalize_path(path)
	if image.save_png(absolute_path) != OK or not FileAccess.file_exists(absolute_path):
		_helpers.fail("G40 failed to save capture: %s" % label)
		return {}
	var metrics := _image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < MIN_COLORED_SAMPLES:
		_helpers.fail("G40 capture lacks colored terrain at %s: %s" % [label, str(metrics)])
		return {}
	metrics["image"] = image
	metrics["path"] = path
	_set_overlays_visible(scene, true)
	return metrics


func _wait_for_material_stability(materializer: Node, min_auto_count: int, label: String) -> Dictionary:
	if materializer == null:
		_helpers.fail("G40 materializer missing")
		return {}
	var last_count := -1
	var stable_frames := 0
	for _frame in range(420):
		var summary: Dictionary = materializer.call("get_material_summary")
		var auto_count := int(summary.get("auto_apply_count", 0))
		if bool(summary.get("applied", false)) and int(summary.get("materialized_instances", 0)) >= EXPECTED_ACTIVE_RESOURCES and auto_count >= min_auto_count:
			if auto_count == last_count:
				stable_frames += 1
				if stable_frames >= 30:
					return summary
			else:
				last_count = auto_count
				stable_frames = 0
		await process_frame
	_helpers.fail("G40 materials did not stabilize at %s: %s" % [label, str(materializer.call("get_material_summary"))])
	return {}


func _verify_sample(backend: Node, point: Vector3i, expected_density: float, expected_material: int) -> bool:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(backend.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_helpers.fail("G40 authoritative sample query failed at %s" % str(point))
		return false
	var sample: RefCounted = _sample_results[request_id]
	if absf(float(sample.call("get_density")) - expected_density) > 0.001:
		_helpers.fail("G40 density mismatch at %s" % str(point))
		return false
	if expected_material > 0 and int(sample.call("get_material")) != expected_material:
		_helpers.fail("G40 material mismatch at %s" % str(point))
		return false
	return true


func _wait_for_sample(request_id: int) -> bool:
	for _frame in range(900):
		if _sample_results.has(request_id):
			return true
		if _sample_failures.has(request_id):
			return false
		await process_frame
	return false


func _image_metrics(image: Image) -> Dictionary:
	var colored := 0
	for y in range(0, image.get_height(), 2):
		for x in range(0, image.get_width(), 2):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.06 and color.g > 0.18 and color.r > 0.14:
				colored += 1
	return {"colored_samples": colored, "width": image.get_width(), "height": image.get_height()}


func _image_difference(before: Image, after: Image) -> Dictionary:
	var changed := 0
	for y in range(0, min(before.get_height(), after.get_height()), 2):
		for x in range(0, min(before.get_width(), after.get_width()), 2):
			var a := before.get_pixel(x, y)
			var b := after.get_pixel(x, y)
			if absf(a.r - b.r) + absf(a.g - b.g) + absf(a.b - b.b) > 0.10:
				changed += 1
	return {"changed_samples": changed}


func _set_overlays_visible(scene: Node, visible: bool) -> void:
	for child in scene.get_children():
		if child is CanvasLayer:
			(child as CanvasLayer).visible = visible
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference != null:
		var debug_overlay := reference.get_node_or_null("DebugOverlay") as CanvasLayer
		if debug_overlay != null:
			debug_overlay.visible = visible


func _connect_backend(backend: Node) -> void:
	if not backend.authoritative_sample_ready.is_connected(_on_sample_ready):
		backend.connect("authoritative_sample_ready", _on_sample_ready)
	if not backend.authoritative_sample_failed.is_connected(_on_sample_failed):
		backend.connect("authoritative_sample_failed", _on_sample_failed)


func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample


func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))
