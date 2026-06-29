extends SceneTree

const MARKER := "WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_PAGE_COUNT := 16384
const MAP_BLOCKS := 2048
const MAX_ACTIVE_RESOURCES := 25
const CAPTURE_ROOT := "res://artifacts/g24_autonomous_large_terrain_acceptance"
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

const ROUTE := [
	{"label": "origin_edge", "position": Vector3(8, 8, 8), "motion": Vector3(1, 0, 1)},
	{"label": "northwest_interior", "position": Vector3(264, 8, 264), "motion": Vector3(1, 0, 0)},
	{"label": "center", "position": Vector3(1032, 8, 1032), "motion": Vector3(1, 0, 0)},
	{"label": "southeast_interior", "position": Vector3(1784, 8, 1784), "motion": Vector3(-1, 0, 0)},
	{"label": "far_corner_edge", "position": Vector3(2040, 8, 2040), "motion": Vector3(-1, 0, -1)},
]

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = true
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G24 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G24 page count mismatch")
		return
	if not _helpers.assert_no_dense_files("g24_start"):
		return
	var camera_delta := await _verify_camera(scene)
	if camera_delta <= 0.001:
		return
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var max_render := 0
	var max_collision := 0
	var stream_updates := 0
	var captures: Array[Dictionary] = []
	for sample in ROUTE:
		var result := await _verify_sample(scene, terrain_world, materializer, sample)
		if result.is_empty():
			return
		max_render = max(max_render, int(result.get("render_resources", 0)))
		max_collision = max(max_collision, int(result.get("collision_resources", 0)))
		stream_updates += int(result.get("stream_updates", 0))
		captures.append(result.get("capture", {}))
	var click_edits := await _verify_click_edits(scene, terrain_world)
	if click_edits != 2:
		return
	if max_render > MAX_ACTIVE_RESOURCES or max_collision > MAX_ACTIVE_RESOURCES:
		_helpers.fail("G24 active resource budget exceeded")
		return
	if not _helpers.assert_no_dense_files("g24_finish"):
		return
	print("%s profile=%s samples=%d pages=%d map_blocks=%d max_render_resources=%d max_collision_resources=%d player_stream_updates=%d camera_delta=%.4f click_edits=%d captures=%d dense_world_files=0" % [
		MARKER, str(PROFILE_ID), ROUTE.size(), EXPECTED_PAGE_COUNT, MAP_BLOCKS,
		max_render, max_collision, stream_updates, camera_delta, click_edits, captures.size(),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _verify_camera(scene: Node) -> float:
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.pressed = true
		root.push_input(click)
		await process_frame
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	var before := camera.rotation
	var motion := InputEventMouseMotion.new()
	motion.relative = Vector2(160.0, -80.0)
	root.push_input(motion)
	await process_frame
	await process_frame
	var delta := before.distance_to(camera.rotation)
	if delta <= 0.001:
		_helpers.fail("G24 camera did not rotate from autonomous input")
	return delta


func _verify_sample(scene: Node, terrain_world: Node, materializer: Node, sample: Dictionary) -> Dictionary:
	var position: Vector3 = sample["position"]
	var label := str(sample["label"])
	var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
	if not _helpers.move_player_to(scene, position):
		return {}
	await process_frame
	var start_chunk := _chunk_for(position)
	var expected_start := _expected_chunks(start_chunk)
	if not await _helpers.wait_for_window(terrain_world, expected_start, label, before_updates + 1, start_chunk, 25):
		return {}
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G24 player did not settle at %s" % label)
		return {}
	var moved := await _move_locally(scene, terrain_world, sample["motion"], before_updates + 2)
	if moved <= 8.0:
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("render_fading_resources", 0)) != 0 or int(metrics.get("pending_chunk_retirements", 0)) != 0:
		_helpers.fail("G24 unsettled metrics at %s: %s" % [label, str(metrics)])
		return {}
	if materializer != null:
		materializer.call("apply_materials_now")
	var capture := await _capture_sample(scene, label)
	return {
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
		"stream_updates": int(metrics.get("viewer_updates", 0)) - before_updates,
		"capture": capture,
	}


func _move_locally(scene: Node, terrain_world: Node, direction: Vector3, min_updates: int) -> float:
	var before: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	scene.set_camera_mode(&"first_person")
	scene.set_player_test_motion(direction)
	for _frame in range(150):
		await physics_frame
		await process_frame
	scene.clear_player_test_motion()
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G24 player did not settle after local movement")
		return 0.0
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var center_chunk := _chunk_for(after)
	if not await _helpers.wait_for_window(
		terrain_world, _expected_chunks(center_chunk), "after_move", min_updates, center_chunk, 25
	):
		return 0.0
	var moved := before.distance_to(after)
	if moved <= 8.0:
		_helpers.fail("G24 local player motion too small: %.3f" % moved)
	return moved


func _verify_click_edits(scene: Node, terrain_world: Node) -> int:
	var accepted := 0
	var start_revision := int(terrain_world.call("get_backend_world_revision"))
	for button in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		var click := InputEventMouseButton.new()
		click.button_index = button
		click.pressed = true
		root.push_input(click)
		await process_frame
		if await _helpers.wait_for_revision(terrain_world, start_revision + accepted + 1):
			accepted += 1
	if accepted != 2:
		_helpers.fail("G24 click edit count mismatch: %d" % accepted)
	return accepted


func _capture_sample(scene: Node, label: String) -> Dictionary:
	_set_capture_overlays_visible(scene, false)
	scene.set_player_visual_visible(false)
	var player_position: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	scene.set_manual_camera_view(player_position + Vector3(0, 26, -28), player_position)
	for _frame in range(20):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_helpers.fail("G24 empty capture at %s" % label)
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var res_path := "%s/%s.png" % [CAPTURE_ROOT, label]
	var absolute_path := ProjectSettings.globalize_path(res_path)
	if image.save_png(absolute_path) != OK or not FileAccess.file_exists(absolute_path):
		_helpers.fail("G24 failed to save capture: %s" % absolute_path)
		return {}
	var metrics := _image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < 100:
		_helpers.fail("G24 capture lacks colored terrain at %s: %s" % [label, str(metrics)])
		return {}
	scene.set_player_visual_visible(true)
	_set_capture_overlays_visible(scene, true)
	scene.set_camera_mode(&"first_person")
	metrics["path"] = res_path
	metrics["absolute_path"] = absolute_path
	return metrics


func _set_capture_overlays_visible(scene: Node, overlay_visible: bool) -> void:
	for child in scene.get_children():
		if child is CanvasLayer:
			(child as CanvasLayer).visible = overlay_visible
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference != null:
		var debug_overlay := reference.get_node_or_null("DebugOverlay") as CanvasLayer
		if debug_overlay != null:
			debug_overlay.visible = overlay_visible


func _image_metrics(image: Image) -> Dictionary:
	var colored := 0
	for y in range(0, image.get_height(), 2):
		for x in range(0, image.get_width(), 2):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.06 and color.g > 0.18 and color.r > 0.14:
				colored += 1
	return {"colored_samples": colored, "width": image.get_width(), "height": image.get_height()}


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))


func _expected_chunks(center_chunk: Vector3i) -> int:
	var min_x = max(center_chunk.x - 2, 0)
	var max_x = min(center_chunk.x + 2, 127)
	var min_z = max(center_chunk.z - 2, 0)
	var max_z = min(center_chunk.z + 2, 127)
	return (max_x - min_x + 1) * (max_z - min_z + 1)
