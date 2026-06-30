extends SceneTree

const MARKER := "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_PAGE_COUNT := 16384
const MAP_BLOCKS := 2048
const EXPECTED_ACTIVE_RESOURCES := 25
const CAPTURE_ROOT := "res://artifacts/g27_full_terrain_handoff_preflight"
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G27 scene did not become playable: %s" % str(scene.get_validation_summary()))
		return
	if not _assert_handoff_scene(scene):
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G27 backend page count mismatch")
		return
	var full_visual := await _wait_for_full_visual(scene)
	if full_visual == null:
		return
	for _frame in range(60):
		await process_frame
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var initial_materials := await _wait_for_materials(materializer, 1, "initial")
	if initial_materials.is_empty() or not await _assert_materials_stable(materializer, "initial"):
		return
	var opening_capture := await _capture_first_person(scene, "opening_first_person", Vector3(1900, 8, 1900))
	if opening_capture.is_empty():
		return
	var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
	var far_position := Vector3(1960, 8, 1960)
	if not _helpers.move_player_to(scene, far_position):
		return
	var far_chunk := _chunk_for(far_position)
	if not await _helpers.wait_for_window(terrain_world, _expected_chunks(far_chunk), "far_handoff", before_updates + 1, far_chunk, EXPECTED_ACTIVE_RESOURCES):
		return
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G27 player did not settle after streaming move")
		return
	var moved_materials := await _wait_for_materials(
		materializer,
		int(initial_materials.get("auto_apply_count", 0)) + 1,
		"after_streaming_move"
	)
	if moved_materials.is_empty() or not await _assert_materials_stable(materializer, "after_streaming_move"):
		return
	var far_capture := await _capture_first_person(scene, "far_first_person", Vector3(1024, 8, 1024))
	if far_capture.is_empty():
		return
	if not await _verify_edit(scene, terrain_world):
		return
	var after_edit := await _wait_for_materials(
		materializer,
		int(moved_materials.get("auto_apply_count", 0)) + 1,
		"after_edit"
	)
	if after_edit.is_empty() or not await _assert_materials_stable(materializer, "after_edit"):
		return
	if not _helpers.assert_no_dense_files("g27_finish"):
		return
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	print("%s profile=%s pages=%d map_blocks=%d captures=2 material_auto_applies=%d player_stream_updates=%d max_render_resources=%d max_collision_resources=%d human_input=false full_visual_visible=true dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		EXPECTED_PAGE_COUNT,
		MAP_BLOCKS,
		int(after_edit.get("auto_apply_count", 0)),
		int(metrics.get("viewer_updates", 0)) - before_updates,
		int(metrics.get("render_resources", 0)),
		int(metrics.get("collision_resources", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _assert_handoff_scene(scene: Node) -> bool:
	var summary: Dictionary = scene.get_validation_summary()
	if bool(summary.get("player_human_input_enabled", true)) or \
			not bool(summary.get("player_present", false)) or \
			not bool(summary.get("player_camera_current", false)) or \
			not bool(summary.get("crosshair_present", false)) or \
			int(summary.get("expected_resource_count", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			str(summary.get("playtest_profile_id", "")) != str(PROFILE_ID):
		_helpers.fail("G27 normal scene summary is not handoff-ready: %s" % str(summary))
		return false
	if scene.get_node_or_null("ValidationTerrainInteractor") == null:
		_helpers.fail("G27 terrain interactor missing")
		return false
	return true


func _wait_for_full_visual(scene: Node) -> MeshInstance3D:
	for _frame in range(180):
		var node := scene.get_node_or_null("ValidationFullTerrainVisual") as MeshInstance3D
		if node != null and node.visible and node.mesh != null:
			var summary: Dictionary = node.call("get_full_terrain_visual_summary")
			if bool(summary.get("enabled", false)) and \
					int(summary.get("coverage_blocks_x", 0)) == MAP_BLOCKS and \
					int(summary.get("coverage_blocks_z", 0)) == MAP_BLOCKS:
				return node
		await process_frame
	_helpers.fail("G27 full terrain visual did not build")
	return null


func _wait_for_materials(materializer: Node, min_auto_count: int, label: String) -> Dictionary:
	if materializer == null:
		_helpers.fail("G27 materializer missing")
		return {}
	for _frame in range(240):
		var summary: Dictionary = materializer.call("get_material_summary")
		if bool(summary.get("applied", false)) and \
				int(summary.get("materialized_instances", 0)) >= EXPECTED_ACTIVE_RESOURCES and \
				int(summary.get("auto_apply_count", 0)) >= min_auto_count:
			return summary
		await process_frame
	_helpers.fail("G27 materials did not auto-apply at %s: %s" % [
		label,
		str(materializer.call("get_material_summary")),
	])
	return {}


func _assert_materials_stable(materializer: Node, label: String) -> bool:
	var last_count := int(Dictionary(materializer.call("get_material_summary")).get("auto_apply_count", 0))
	var stable_frames := 0
	for _frame in range(120):
		await process_frame
		var current := int(Dictionary(materializer.call("get_material_summary")).get("auto_apply_count", 0))
		if current == last_count:
			stable_frames += 1
			if stable_frames >= 30:
				return true
		else:
			last_count = current
			stable_frames = 0
	_helpers.fail("G27 materials did not become stable at %s" % label)
	return false


func _capture_first_person(scene: Node, label: String, target: Vector3) -> Dictionary:
	_set_capture_overlays_visible(scene, false)
	scene.set_player_visual_visible(false)
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	if camera == null:
		_helpers.fail("G27 camera missing")
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
		_helpers.fail("G27 empty capture at %s" % label)
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var res_path := "%s/%s.png" % [CAPTURE_ROOT, label]
	var absolute_path := ProjectSettings.globalize_path(res_path)
	if image.save_png(absolute_path) != OK or not FileAccess.file_exists(absolute_path):
		_helpers.fail("G27 failed to save capture at %s" % label)
		return {}
	var metrics := _image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < 800:
		_helpers.fail("G27 first-person capture lacks terrain at %s: %s" % [label, str(metrics)])
		return {}
	metrics["path"] = res_path
	metrics["absolute_path"] = absolute_path
	scene.set_player_visual_visible(true)
	_set_capture_overlays_visible(scene, true)
	return metrics


func _verify_edit(scene: Node, terrain_world: Node) -> bool:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if interactor == null:
		_helpers.fail("G27 missing terrain interactor")
		return false
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var revision := int(terrain_world.call("get_backend_world_revision"))
	var point: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	if not bool(interactor.call("submit_sphere_edit", &"carve", point, 1.8, -1, 1.0)):
		_helpers.fail("G27 carve was rejected")
		return false
	if not await _helpers.wait_for_revision(terrain_world, revision + 1):
		return false
	var center_chunk := _chunk_for(point)
	if not await _helpers.wait_for_window(
		terrain_world,
		_expected_chunks(center_chunk),
		"after_edit",
		int(before_metrics.get("viewer_updates", 0)),
		center_chunk,
		EXPECTED_ACTIVE_RESOURCES
	):
		return false
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("edit_replacements", 0)) <= int(before_metrics.get("edit_replacements", 0)):
		_helpers.fail("G27 edit did not replace render resources")
		return false
	return true


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
