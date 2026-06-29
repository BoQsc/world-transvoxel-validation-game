extends SceneTree

const MARKER := "WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_PAGE_COUNT := 16384
const MAP_BLOCKS := 2048
const CAPTURE_ROOT := "res://artifacts/g25_full_terrain_visual_baseline"
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted
var _batch_results := {}
var _batch_failures := {}


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"overview")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G25 scene did not become autonomously playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G25 backend page count mismatch")
		return
	var full_visual := await _wait_for_full_visual(scene)
	if full_visual == null:
		return
	var summary: Dictionary = full_visual.call("get_full_terrain_visual_summary")
	if not _assert_full_visual_summary(full_visual, summary):
		return
	if not await _verify_backend_height_match(backend, full_visual):
		return
	var capture := await _capture_full_map(scene)
	if capture.is_empty():
		return
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not _helpers.assert_no_dense_files("g25_finish"):
		return
	print("%s profile=%s pages=%d map_blocks=%d full_visual_blocks=%dx%d full_visual_vertices=%d full_visual_triangles=%d native_render_resources=%d native_collision_resources=%d capture_colored_samples=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		EXPECTED_PAGE_COUNT,
		MAP_BLOCKS,
		int(summary.get("coverage_blocks_x", 0)),
		int(summary.get("coverage_blocks_z", 0)),
		int(summary.get("vertices", 0)),
		int(summary.get("triangles", 0)),
		int(metrics.get("render_resources", 0)),
		int(metrics.get("collision_resources", 0)),
		int(capture.get("colored_samples", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _wait_for_full_visual(scene: Node) -> MeshInstance3D:
	for _frame in range(180):
		var node := scene.get_node_or_null("ValidationFullTerrainVisual") as MeshInstance3D
		if node != null and node.visible and node.mesh != null:
			var summary: Dictionary = node.call("get_full_terrain_visual_summary")
			if bool(summary.get("enabled", false)):
				return node
		await process_frame
	_helpers.fail("G25 full terrain visual did not build")
	return null


func _assert_full_visual_summary(full_visual: MeshInstance3D, summary: Dictionary) -> bool:
	var aabb := full_visual.get_aabb()
	if not bool(summary.get("enabled", false)) or \
			str(summary.get("profile_id", "")) != str(PROFILE_ID) or \
			int(summary.get("coverage_blocks_x", 0)) != MAP_BLOCKS or \
			int(summary.get("coverage_blocks_z", 0)) != MAP_BLOCKS or \
			int(summary.get("vertices", 0)) <= 0 or \
			int(summary.get("triangles", 0)) <= 0 or \
			aabb.size.x < float(MAP_BLOCKS) - 0.5 or \
			aabb.size.z < float(MAP_BLOCKS) - 0.5 or \
			not bool(summary.get("active_window_is_detail_layer_only", false)):
		_helpers.fail("G25 full visual coverage invalid: summary=%s aabb=%s" % [str(summary), str(aabb)])
		return false
	return true


func _verify_backend_height_match(backend: Node, full_visual: Node) -> bool:
	backend.connect("authoritative_samples_ready", _on_authoritative_samples_ready)
	backend.connect("authoritative_samples_failed", _on_authoritative_samples_failed)
	var xz_points := [
		Vector2i(0, 0),
		Vector2i(512, 512),
		Vector2i(1024, 1024),
		Vector2i(1536, 1536),
		Vector2i(2047, 2047),
	]
	var grid_points := []
	for point in xz_points:
		grid_points.append(Vector3i(point.x, 8, point.y))
	var request_id := int(backend.call("request_authoritative_samples", grid_points, 0))
	if request_id <= 0:
		_helpers.fail("G25 authoritative sample batch was rejected")
		return false
	var samples := await _wait_for_sample_batch(request_id)
	if samples.size() != xz_points.size():
		return false
	for index in range(samples.size()):
		var sample: RefCounted = samples[index]
		var point: Vector2i = xz_points[index]
		var backend_surface := 8.0 - float(sample.call("get_density"))
		var visual_surface := float(full_visual.call("sample_surface_height", float(point.x), float(point.y)))
		if abs(backend_surface - visual_surface) > 0.05:
			_helpers.fail("G25 visual/backend height mismatch at %s: %.4f vs %.4f" % [
				str(point),
				visual_surface,
				backend_surface,
			])
			return false
	return true


func _wait_for_sample_batch(request_id: int) -> Array:
	for _frame in range(300):
		if _batch_results.has(request_id):
			return _batch_results[request_id]
		if _batch_failures.has(request_id):
			_helpers.fail("G25 authoritative sample failed: %s" % str(_batch_failures[request_id]))
			return []
		await process_frame
	_helpers.fail("G25 authoritative sample batch timed out")
	return []


func _capture_full_map(scene: Node) -> Dictionary:
	_set_capture_overlays_visible(scene, false)
	scene.set_player_visual_visible(false)
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	if camera == null:
		_helpers.fail("G25 camera missing")
		return {}
	scene.set_camera_mode(&"manual")
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2200.0
	camera.far = 6000.0
	camera.global_position = Vector3(1024, 1800, 1024)
	camera.look_at(Vector3(1024, 6, 1024), Vector3.FORWARD)
	for _frame in range(30):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_helpers.fail("G25 full-map capture is empty")
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var res_path := "%s/full_map_overview.png" % CAPTURE_ROOT
	var absolute_path := ProjectSettings.globalize_path(res_path)
	if image.save_png(absolute_path) != OK or not FileAccess.file_exists(absolute_path):
		_helpers.fail("G25 failed to save full-map capture")
		return {}
	var metrics := _image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < 1000:
		_helpers.fail("G25 full-map capture lacks colored terrain: %s" % str(metrics))
		return {}
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


func _on_authoritative_samples_ready(request_id: int, samples: Array) -> void:
	_batch_results[request_id] = samples


func _on_authoritative_samples_failed(request_id: int, error: String) -> void:
	_batch_failures[request_id] = error
