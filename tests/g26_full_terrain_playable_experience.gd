extends SceneTree

const MARKER := "WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_PAGE_COUNT := 16384
const MAP_BLOCKS := 2048
const MAX_ACTIVE_RESOURCES := 25
const CAPTURE_ROOT := "res://artifacts/g26_full_terrain_playable_experience"
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

const ROUTE := [
	{"label": "origin_to_center", "position": Vector3(40, 8, 40), "target": Vector3(1024, 8, 1024)},
	{"label": "center_to_far", "position": Vector3(1032, 8, 1032), "target": Vector3(1900, 8, 1900)},
	{"label": "far_to_center", "position": Vector3(1960, 8, 1960), "target": Vector3(1024, 8, 1024)},
]

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G26 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G26 backend page count mismatch")
		return
	var full_visual := await _wait_for_full_visual(scene)
	if full_visual == null:
		return
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var captures: Array[Dictionary] = []
	var max_render := 0
	var max_collision := 0
	var stream_updates := 0
	for sample in ROUTE:
		var result := await _verify_playable_sample(scene, terrain_world, materializer, sample)
		if result.is_empty():
			return
		max_render = max(max_render, int(result.get("render_resources", 0)))
		max_collision = max(max_collision, int(result.get("collision_resources", 0)))
		stream_updates += int(result.get("stream_updates", 0))
		captures.append(result.get("capture", {}))
	if max_render > MAX_ACTIVE_RESOURCES or max_collision > MAX_ACTIVE_RESOURCES:
		_helpers.fail("G26 local detail active budget exceeded")
		return
	if not await _verify_edit(scene, terrain_world):
		return
	if not _helpers.assert_no_dense_files("g26_finish"):
		return
	print("%s profile=%s pages=%d map_blocks=%d captures=%d player_stream_updates=%d max_render_resources=%d max_collision_resources=%d full_visual_visible=true dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		EXPECTED_PAGE_COUNT,
		MAP_BLOCKS,
		captures.size(),
		stream_updates,
		max_render,
		max_collision,
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _wait_for_full_visual(scene: Node) -> MeshInstance3D:
	for _frame in range(180):
		var node := scene.get_node_or_null("ValidationFullTerrainVisual") as MeshInstance3D
		if node != null and node.visible and node.mesh != null:
			var summary: Dictionary = node.call("get_full_terrain_visual_summary")
			if bool(summary.get("enabled", false)) and int(summary.get("coverage_blocks_x", 0)) == MAP_BLOCKS:
				return node
		await process_frame
	_helpers.fail("G26 full terrain visual did not build")
	return null


func _verify_playable_sample(scene: Node, terrain_world: Node, materializer: Node, sample: Dictionary) -> Dictionary:
	var label := str(sample["label"])
	var position: Vector3 = sample["position"]
	var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
	if not _helpers.move_player_to(scene, position):
		return {}
	await process_frame
	var center_chunk := _chunk_for(position)
	var expected_chunks := _expected_chunks(center_chunk)
	if not await _helpers.wait_for_window(terrain_world, expected_chunks, label, before_updates + 1, center_chunk, MAX_ACTIVE_RESOURCES):
		return {}
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G26 player did not settle at %s" % label)
		return {}
	if materializer != null:
		materializer.call("apply_materials_now")
	var capture := await _capture_first_person(scene, label, sample["target"])
	if capture.is_empty():
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	return {
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
		"stream_updates": int(metrics.get("viewer_updates", 0)) - before_updates,
		"capture": capture,
	}


func _capture_first_person(scene: Node, label: String, target: Vector3) -> Dictionary:
	_set_capture_overlays_visible(scene, false)
	scene.set_player_visual_visible(false)
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	if camera == null:
		_helpers.fail("G26 camera missing")
		return {}
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 70.0
	camera.far = 5000.0
	var player_position: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	scene.set_manual_camera_view(player_position + Vector3(0, 1.55, 0), target)
	for _frame in range(30):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_helpers.fail("G26 empty capture at %s" % label)
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var res_path := "%s/%s.png" % [CAPTURE_ROOT, label]
	var absolute_path := ProjectSettings.globalize_path(res_path)
	if image.save_png(absolute_path) != OK or not FileAccess.file_exists(absolute_path):
		_helpers.fail("G26 failed to save capture at %s" % label)
		return {}
	var metrics := _image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < 800:
		_helpers.fail("G26 first-person capture lacks terrain at %s: %s" % [label, str(metrics)])
		return {}
	metrics["path"] = res_path
	metrics["absolute_path"] = absolute_path
	scene.set_player_visual_visible(true)
	_set_capture_overlays_visible(scene, true)
	return metrics


func _verify_edit(scene: Node, terrain_world: Node) -> bool:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if interactor == null:
		_helpers.fail("G26 missing terrain interactor")
		return false
	var revision := int(terrain_world.call("get_backend_world_revision"))
	var point: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	if not bool(interactor.call("submit_sphere_edit", &"carve", point, 1.8, -1, 1.0)):
		_helpers.fail("G26 carve was rejected")
		return false
	return await _helpers.wait_for_revision(terrain_world, revision + 1)


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
