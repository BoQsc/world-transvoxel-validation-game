extends SceneTree


const MARKER := "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const MAP_BLOCKS := 2048
const EXPECTED_PAGE_COUNT := 16384
const MAX_ACTIVE_RESOURCES := 25
const MAX_BACKEND_HEIGHT_ERROR := 0.05
const MAX_NEIGHBOR_HEIGHT_DELTA := 4.0
const MAX_DIAGONAL_PAIR_DELTA := 2.0
const MIN_CAPTURE_COLORED_SAMPLES := 50000
const CAPTURE_ROOT := "res://artifacts/g35_terrain_correctness_artifact_quality"
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted
var _batch_results := {}
var _batch_failures := {}


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"overview")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G35 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G35 backend page count mismatch")
		return
	var full_visual := await _wait_for_full_visual(scene)
	if full_visual == null:
		return
	var summary: Dictionary = full_visual.call("get_full_terrain_visual_summary")
	if not _assert_visual_summary(full_visual, summary):
		return
	var surface_audit := _audit_surface(full_visual)
	if surface_audit.is_empty():
		return
	var backend_audit := await _audit_backend_agreement(backend, full_visual)
	if backend_audit.is_empty():
		return
	var capture := await _capture_full_map(scene)
	if capture.is_empty():
		return
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("render_resources", 0)) > MAX_ACTIVE_RESOURCES or \
			int(metrics.get("collision_resources", 0)) > MAX_ACTIVE_RESOURCES or \
			int(metrics.get("render_fading_resources", 0)) != 0 or \
			int(metrics.get("pending_chunk_retirements", 0)) != 0:
		_helpers.fail("G35 runtime metrics outside correctness bounds: %s" % str(metrics))
		return
	if not _helpers.assert_no_dense_files("g35_finish"):
		return
	print("%s profile=%s map_blocks=%d surface_samples=%d backend_samples=%d max_backend_height_error=%.4f min_height=%.3f max_height=%.3f max_neighbor_delta=%.3f max_diagonal_pair_delta=%.3f material_ids=%s capture_colored_samples=%d max_render_resources=%d max_collision_resources=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		MAP_BLOCKS,
		int(surface_audit.get("surface_samples", 0)),
		int(backend_audit.get("backend_samples", 0)),
		float(backend_audit.get("max_backend_height_error", 0.0)),
		float(surface_audit.get("min_height", 0.0)),
		float(surface_audit.get("max_height", 0.0)),
		float(surface_audit.get("max_neighbor_delta", 0.0)),
		float(surface_audit.get("max_diagonal_pair_delta", 0.0)),
		str(surface_audit.get("material_ids", "")),
		int(capture.get("colored_samples", 0)),
		int(metrics.get("render_resources", 0)),
		int(metrics.get("collision_resources", 0)),
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
	_helpers.fail("G35 full terrain visual did not build")
	return null


func _assert_visual_summary(full_visual: MeshInstance3D, summary: Dictionary) -> bool:
	var aabb := full_visual.get_aabb()
	if str(summary.get("profile_id", "")) != str(PROFILE_ID) or \
			int(summary.get("coverage_blocks_x", 0)) != MAP_BLOCKS or \
			int(summary.get("coverage_blocks_z", 0)) != MAP_BLOCKS or \
			int(summary.get("vertices", 0)) != 16641 or \
			int(summary.get("triangles", 0)) != 32768 or \
			aabb.size.x < float(MAP_BLOCKS) - 0.5 or \
			aabb.size.z < float(MAP_BLOCKS) - 0.5 or \
			not bool(summary.get("active_window_is_detail_layer_only", false)):
		_helpers.fail("G35 visual summary invalid: summary=%s aabb=%s" % [str(summary), str(aabb)])
		return false
	return true


func _audit_surface(full_visual: Node) -> Dictionary:
	var min_height := INF
	var max_height := -INF
	var max_neighbor_delta := 0.0
	var material_ids := {}
	var last_height_by_z := {}
	var sample_count := 0
	for z in range(0, MAP_BLOCKS + 1, 128):
		var previous_x_height := INF
		for x in range(0, MAP_BLOCKS + 1, 128):
			var surface := float(full_visual.call("sample_surface_height", float(x), float(z)))
			if surface != surface or absf(surface) > 1000.0:
				_helpers.fail("G35 non-finite or unreasonable surface at %d,%d: %.4f" % [x, z, surface])
				return {}
			if surface < 2.0 or surface > 14.5:
				_helpers.fail("G35 surface outside vertical expectation at %d,%d: %.4f" % [x, z, surface])
				return {}
			var material_id := int(full_visual.call("sample_material_id", float(x), float(z)))
			if not [2, 3, 4, 5].has(material_id):
				_helpers.fail("G35 unexpected material id at %d,%d: %d" % [x, z, material_id])
				return {}
			material_ids[material_id] = true
			min_height = min(min_height, surface)
			max_height = max(max_height, surface)
			if previous_x_height != INF:
				max_neighbor_delta = max(max_neighbor_delta, absf(surface - previous_x_height))
			if last_height_by_z.has(x):
				max_neighbor_delta = max(max_neighbor_delta, absf(surface - float(last_height_by_z[x])))
			last_height_by_z[x] = surface
			previous_x_height = surface
			sample_count += 1
	var diagonal_delta := _audit_diagonal_symmetry(full_visual)
	if diagonal_delta < 0.0:
		return {}
	if max_neighbor_delta > MAX_NEIGHBOR_HEIGHT_DELTA:
		_helpers.fail("G35 neighbor height discontinuity too large: %.4f" % max_neighbor_delta)
		return {}
	return {
		"surface_samples": sample_count,
		"min_height": min_height,
		"max_height": max_height,
		"max_neighbor_delta": max_neighbor_delta,
		"max_diagonal_pair_delta": diagonal_delta,
		"material_ids": ",".join(PackedStringArray(_sorted_keys(material_ids))),
	}


func _audit_diagonal_symmetry(full_visual: Node) -> float:
	var max_delta := 0.0
	for center in range(256, 1793, 256):
		var a := float(full_visual.call("sample_surface_height", float(center + 32), float(center - 32)))
		var b := float(full_visual.call("sample_surface_height", float(center - 32), float(center + 32)))
		var delta := absf(a - b)
		if delta > MAX_DIAGONAL_PAIR_DELTA:
			_helpers.fail("G35 diagonal pair discontinuity too large at %d: %.4f" % [center, delta])
			return -1.0
		max_delta = max(max_delta, delta)
	return max_delta


func _audit_backend_agreement(backend: Node, full_visual: Node) -> Dictionary:
	if not backend.authoritative_samples_ready.is_connected(_on_authoritative_samples_ready):
		backend.connect("authoritative_samples_ready", _on_authoritative_samples_ready)
	if not backend.authoritative_samples_failed.is_connected(_on_authoritative_samples_failed):
		backend.connect("authoritative_samples_failed", _on_authoritative_samples_failed)
	var xz_points := [
		Vector2i(0, 0), Vector2i(256, 256), Vector2i(512, 512),
		Vector2i(768, 1024), Vector2i(1024, 1024), Vector2i(1280, 768),
		Vector2i(1536, 1536), Vector2i(1792, 512), Vector2i(2047, 2047),
	]
	var grid_points := []
	for point in xz_points:
		grid_points.append(Vector3i(point.x, 8, point.y))
	_batch_results.clear()
	_batch_failures.clear()
	var request_id := int(backend.call("request_authoritative_samples", grid_points, 0))
	if request_id <= 0:
		_helpers.fail("G35 authoritative sample batch rejected")
		return {}
	var samples := await _wait_for_sample_batch(request_id)
	if samples.size() != xz_points.size():
		_helpers.fail("G35 authoritative sample count mismatch")
		return {}
	var max_error := 0.0
	for index in range(samples.size()):
		var sample: RefCounted = samples[index]
		var point: Vector2i = xz_points[index]
		var backend_surface := 8.0 - float(sample.call("get_density"))
		var visual_surface := float(full_visual.call("sample_surface_height", float(point.x), float(point.y)))
		var error := absf(backend_surface - visual_surface)
		if error > MAX_BACKEND_HEIGHT_ERROR:
			_helpers.fail("G35 backend/visual mismatch at %s: %.4f" % [str(point), error])
			return {}
		max_error = max(max_error, error)
	return {"backend_samples": samples.size(), "max_backend_height_error": max_error}


func _wait_for_sample_batch(request_id: int) -> Array:
	for _frame in range(300):
		if _batch_results.has(request_id):
			return _batch_results[request_id]
		if _batch_failures.has(request_id):
			_helpers.fail("G35 authoritative sample failed: %s" % str(_batch_failures[request_id]))
			return []
		await process_frame
	_helpers.fail("G35 authoritative sample batch timed out")
	return []


func _capture_full_map(scene: Node) -> Dictionary:
	for child in scene.get_children():
		if child is CanvasLayer:
			(child as CanvasLayer).visible = false
	scene.set_player_visual_visible(false)
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	if camera == null:
		_helpers.fail("G35 camera missing")
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
		_helpers.fail("G35 capture is empty")
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var res_path := "%s/full_map_correctness.png" % CAPTURE_ROOT
	var absolute_path := ProjectSettings.globalize_path(res_path)
	if image.save_png(absolute_path) != OK or not FileAccess.file_exists(absolute_path):
		_helpers.fail("G35 failed to save capture")
		return {}
	var metrics := _image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < MIN_CAPTURE_COLORED_SAMPLES:
		_helpers.fail("G35 capture lacks colored terrain: %s" % str(metrics))
		return {}
	return metrics


func _image_metrics(image: Image) -> Dictionary:
	var colored := 0
	for y in range(0, image.get_height(), 2):
		for x in range(0, image.get_width(), 2):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.06 and color.g > 0.18 and color.r > 0.14:
				colored += 1
	return {"colored_samples": colored, "width": image.get_width(), "height": image.get_height()}


func _sorted_keys(values: Dictionary) -> Array[String]:
	var keys: Array[int] = []
	for key in values.keys():
		keys.append(int(key))
	keys.sort()
	var output: Array[String] = []
	for key in keys:
		output.append(str(key))
	return output


func _on_authoritative_samples_ready(request_id: int, samples: Array) -> void:
	_batch_results[request_id] = samples


func _on_authoritative_samples_failed(request_id: int, error: String) -> void:
	_batch_failures[request_id] = error
