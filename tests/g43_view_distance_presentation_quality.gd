extends SceneTree


const MARKER := "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const CAPTURE_ROOT := "res://artifacts/g43_view_distance_presentation_quality"
const MAP_BLOCKS := 2048
const EXPECTED_ACTIVE_RESOURCES := 25
const MIN_COLORED_SAMPLES := 800
const MIN_HORIZONTAL_BINS := 8
const MIN_VERTICAL_BINS := 3
const MIN_MID_BAND_SAMPLES := 120
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

const VIEWS := [
	{"label": "center_to_far", "position": Vector3(1032, 8, 1032), "target": Vector3(1900, 8, 1900)},
	{"label": "northwest_to_southeast", "position": Vector3(264, 8, 264), "target": Vector3(1784, 8, 1784)},
	{"label": "far_to_center", "position": Vector3(1960, 8, 1960), "target": Vector3(1024, 8, 1024)},
]

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G43 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var full_visual := await _wait_for_full_visual(scene)
	if full_visual == null:
		return
	var full_summary: Dictionary = full_visual.call("get_full_terrain_visual_summary")
	var min_colored := 999999999
	var min_horizontal_bins := 999999999
	var min_vertical_bins := 999999999
	var min_mid_band := 999999999
	var max_render := 0
	var max_collision := 0
	var max_fading := 0
	for view in VIEWS:
		var result := await _capture_view(scene, terrain_world, view)
		if result.is_empty():
			return
		min_colored = min(min_colored, int(result.get("colored_samples", 0)))
		min_horizontal_bins = min(min_horizontal_bins, int(result.get("horizontal_bins", 0)))
		min_vertical_bins = min(min_vertical_bins, int(result.get("vertical_bins", 0)))
		min_mid_band = min(min_mid_band, int(result.get("mid_band_samples", 0)))
		max_render = max(max_render, int(result.get("render_resources", 0)))
		max_collision = max(max_collision, int(result.get("collision_resources", 0)))
		max_fading = max(max_fading, int(result.get("render_fading_resources", 0)))
	if not _helpers.assert_no_dense_files("g43_finish"):
		return
	print("%s profile=%s captures=%d full_visual_blocks=%dx%d min_colored_samples=%d min_horizontal_bins=%d min_vertical_bins=%d min_mid_band_samples=%d max_render_resources=%d max_collision_resources=%d max_render_fading_resources=%d dense_world_files=0" % [
		MARKER, str(PROFILE_ID), VIEWS.size(),
		int(full_summary.get("coverage_blocks_x", 0)), int(full_summary.get("coverage_blocks_z", 0)),
		min_colored, min_horizontal_bins, min_vertical_bins, min_mid_band,
		max_render, max_collision, max_fading,
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _capture_view(scene: Node, terrain_world: Node, view: Dictionary) -> Dictionary:
	var position: Vector3 = view["position"]
	var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
	var before_position: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var horizontal_delta := Vector2(position.x - before_position.x, position.z - before_position.z).length()
	var required_updates := before_updates + (1 if horizontal_delta >= 8.0 else 0)
	if not _helpers.move_player_to(scene, position):
		return {}
	if not await _wait_for_settled_window(terrain_world, str(view["label"]), required_updates):
		return {}
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G43 player did not settle at %s" % str(view["label"]))
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var capture := await _capture_first_person(scene, str(view["label"]), view["target"])
	if capture.is_empty():
		return {}
	capture["render_resources"] = int(metrics.get("render_resources", 0))
	capture["collision_resources"] = int(metrics.get("collision_resources", 0))
	capture["render_fading_resources"] = int(metrics.get("render_fading_resources", 0))
	return capture


func _wait_for_settled_window(terrain_world: Node, label: String, minimum_viewer_updates: int) -> bool:
	for _frame in range(900):
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		var active_records := int(metrics.get("active_chunk_records", 0))
		if active_records == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("render_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("collision_resources", 0)) == EXPECTED_ACTIVE_RESOURCES and \
				int(metrics.get("fully_ready_chunk_records", -1)) == active_records and \
				int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and \
				int(metrics.get("queued_render", 0)) == 0 and \
				int(metrics.get("queued_collision", 0)) == 0 and \
				int(metrics.get("pending_chunk_retirements", 0)) == 0 and \
				int(metrics.get("render_fading_resources", 0)) == 0:
			return true
		await process_frame
	_helpers.fail("G43 window did not settle at %s: %s" % [label, str(terrain_world.call("get_runtime_metrics"))])
	return false


func _wait_for_full_visual(scene: Node) -> MeshInstance3D:
	for _frame in range(180):
		var node := scene.get_node_or_null("ValidationFullTerrainVisual") as MeshInstance3D
		if node != null and node.visible and node.mesh != null:
			var summary: Dictionary = node.call("get_full_terrain_visual_summary")
			if bool(summary.get("enabled", false)) and int(summary.get("coverage_blocks_x", 0)) == MAP_BLOCKS and int(summary.get("coverage_blocks_z", 0)) == MAP_BLOCKS:
				return node
		await process_frame
	_helpers.fail("G43 full terrain visual did not build")
	return null


func _capture_first_person(scene: Node, label: String, target: Vector3) -> Dictionary:
	_set_capture_overlays_visible(scene, false)
	scene.set_player_visual_visible(false)
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	if camera == null:
		_helpers.fail("G43 camera missing")
		return {}
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 75.0
	camera.far = 5000.0
	var player_position: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	scene.set_manual_camera_view(player_position + Vector3(0, 1.55, 0), target)
	for _frame in range(30):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_helpers.fail("G43 empty capture at %s" % label)
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var res_path := "%s/%s.png" % [CAPTURE_ROOT, label]
	var absolute_path := ProjectSettings.globalize_path(res_path)
	if image.save_png(absolute_path) != OK or not FileAccess.file_exists(absolute_path):
		_helpers.fail("G43 failed to save capture at %s" % label)
		return {}
	var metrics := _image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < MIN_COLORED_SAMPLES or int(metrics.get("horizontal_bins", 0)) < MIN_HORIZONTAL_BINS or int(metrics.get("vertical_bins", 0)) < MIN_VERTICAL_BINS or int(metrics.get("mid_band_samples", 0)) < MIN_MID_BAND_SAMPLES:
		_helpers.fail("G43 capture lacks view-distance coverage at %s: %s" % [label, str(metrics)])
		return {}
	metrics["path"] = res_path
	scene.set_player_visual_visible(true)
	_set_capture_overlays_visible(scene, true)
	return metrics


func _image_metrics(image: Image) -> Dictionary:
	var colored := 0
	var mid_band := 0
	var x_bins := {}
	var y_bins := {}
	var width := image.get_width()
	var height := image.get_height()
	for y in range(0, height, 2):
		for x in range(0, width, 2):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.06 and color.g > 0.18 and color.r > 0.14:
				colored += 1
				x_bins[int(floor(float(x) / float(width) * 16.0))] = true
				y_bins[int(floor(float(y) / float(height) * 12.0))] = true
				if y > int(float(height) * 0.18) and y < int(float(height) * 0.68):
					mid_band += 1
	return {"colored_samples": colored, "horizontal_bins": x_bins.size(), "vertical_bins": y_bins.size(), "mid_band_samples": mid_band, "width": width, "height": height}


func _set_capture_overlays_visible(scene: Node, overlay_visible: bool) -> void:
	for child in scene.get_children():
		if child is CanvasLayer:
			(child as CanvasLayer).visible = overlay_visible
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference != null:
		var debug_overlay := reference.get_node_or_null("DebugOverlay") as CanvasLayer
		if debug_overlay != null:
			debug_overlay.visible = overlay_visible
