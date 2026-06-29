extends RefCounted


const PROFILE_ID := &"g19_compact_2k_on_demand"
const CAPTURE_ROOT := "res://artifacts/g22_exact_compact_handoff_runtime_proof"
const METRICS_PATH := CAPTURE_ROOT + "/runtime_metrics.json"
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")
const FORBIDDEN_DENSE_FILES := [
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/world.wtworld",
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/streaming.wtworld",
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/procedural.wtseed",
]

var _tree: SceneTree


func _init(tree: SceneTree) -> void:
	_tree = tree


func fail(message: String) -> void:
	push_error("WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_FAIL: " + message)
	_tree.quit(1)


func assert_no_dense_files(stage: String) -> bool:
	for path in FORBIDDEN_DENSE_FILES:
		if FileAccess.file_exists(path):
			fail("G22 dense file exists at %s: %s" % [stage, path])
			return false
	return true


func terrain_world(scene: Node) -> Node:
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference == null:
		return null
	return reference.call("get_terrain_world")


func move_player_to(scene: Node, viewer_sample_position: Vector3) -> bool:
	var player := scene.get_node_or_null("ValidationPlayer") as CharacterBody3D
	if player == null:
		fail("G22 validation player missing")
		return false
	scene.clear_player_test_motion()
	player.global_position = Vector3(viewer_sample_position.x, 26.0, viewer_sample_position.z)
	player.velocity = Vector3.ZERO
	return true


func verify_player_motion(scene: Node, summary: Dictionary) -> bool:
	var before: Vector3 = summary.get("player_position", Vector3.ZERO)
	scene.set_player_test_motion(Vector3(1, 0, 0))
	for _frame in range(45):
		await _tree.physics_frame
	scene.clear_player_test_motion()
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	if before.distance_to(after) < 0.25:
		fail("G22 scripted player motion did not move: before=%s after=%s" % [str(before), str(after)])
		return false
	return true


func verify_carve_and_construct(
	scene: Node,
	terrain_world_node: Node,
	materializer: Node,
	revision: int,
	center_chunk: Vector3i
) -> Dictionary:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if interactor == null:
		fail("G22 missing terrain interactor")
		return {}
	var start_world_revision := int(terrain_world_node.call("get_backend_world_revision"))
	var point := ProfileCatalog.edit_point(PROFILE_ID)
	if not bool(interactor.call("submit_sphere_edit", &"carve", point, 1.8, -1, 1.0)):
		fail("G22 active-center carve was rejected")
		return {}
	if not await wait_for_revision(terrain_world_node, start_world_revision + 1):
		fail("G22 active-center carve did not commit")
		return {}
	if not await wait_for_window(terrain_world_node, 25, "center_after_carve", revision, center_chunk, 25):
		return {}
	if materializer != null:
		materializer.call("apply_materials_now")
	var after_carve_metrics: Dictionary = terrain_world_node.call("get_runtime_metrics")
	if int(after_carve_metrics.get("render_fading_resources", 0)) != 0:
		fail("G22 carve created render fade blink resources: %s" % str(after_carve_metrics))
		return {}
	if not bool(interactor.call("submit_sphere_edit", &"construct", point, 1.8, 4, 1.0)):
		fail("G22 active-center construct/place was rejected")
		return {}
	if not await wait_for_revision(terrain_world_node, start_world_revision + 2):
		fail("G22 active-center construct/place did not commit")
		return {}
	if not await wait_for_window(terrain_world_node, 25, "center_after_construct", revision, center_chunk, 25):
		return {}
	if materializer != null:
		materializer.call("apply_materials_now")
	var after_construct_metrics: Dictionary = terrain_world_node.call("get_runtime_metrics")
	if int(after_construct_metrics.get("render_fading_resources", 0)) != 0:
		fail("G22 construct/place created render fade blink resources: %s" % str(after_construct_metrics))
		return {}
	if int(after_construct_metrics.get("edit_replacements", 0)) <= 0:
		fail("G22 edits did not replace render resources: %s" % str(after_construct_metrics))
		return {}
	return {"construct_verified": true}


func verify_materials(materializer: Node, expected_chunks: int, label: String) -> bool:
	if materializer == null:
		fail("G22 materializer missing")
		return false
	var summary: Dictionary = materializer.call("apply_materials_now")
	if int(summary.get("materialized_instances", 0)) < expected_chunks:
		fail("G22 materials did not cover %s: %s" % [label, str(summary)])
		return false
	return true


func capture_oblique(scene: Node, label: String, minimum_colored: int) -> Dictionary:
	var player_position: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	scene.set_player_visual_visible(false)
	scene.set_manual_camera_view(
		player_position + Vector3(0.0, 9.0, -16.0),
		player_position + Vector3(16.0, -1.0, 16.0)
	)
	return await capture(scene, label, minimum_colored)


func capture_overview(scene: Node, label: String, minimum_colored: int) -> Dictionary:
	scene.set_player_visual_visible(true)
	scene.set_camera_mode(&"overview")
	return await capture(scene, label, minimum_colored)


func capture(scene: Node, label: String, minimum_colored: int) -> Dictionary:
	_set_capture_overlays_visible(scene, false)
	for _frame in range(30):
		await _tree.process_frame
	var image := _tree.root.get_texture().get_image()
	if image == null or image.is_empty():
		fail("G22 capture image is empty: %s" % label)
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var path := "%s/%s.png" % [CAPTURE_ROOT, label]
	if image.save_png(path) != OK:
		fail("G22 failed to save capture: %s" % path)
		return {}
	var metrics := image_metrics(image)
	if int(metrics.get("colored_samples", 0)) < minimum_colored:
		fail("G22 capture lacks enough colored terrain at %s: %s" % [label, str(metrics)])
		return {}
	metrics["label"] = label
	metrics["path"] = path
	_set_capture_overlays_visible(scene, true)
	return metrics


func image_metrics(image: Image) -> Dictionary:
	var colored_samples := 0
	var non_gray_samples := 0
	for y in range(0, image.get_height(), 2):
		for x in range(0, image.get_width(), 2):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.05:
				non_gray_samples += 1
			if spread > 0.06 and color.g > 0.18 and color.r > 0.14:
				colored_samples += 1
	return {
		"width": image.get_width(),
		"height": image.get_height(),
		"colored_samples": colored_samples,
		"non_gray_samples": non_gray_samples,
	}


func write_runtime_metrics(metrics: Dictionary) -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	var file := FileAccess.open(METRICS_PATH, FileAccess.WRITE)
	if file == null:
		fail("G22 failed to open runtime metrics for write")
		return
	file.store_string(JSON.stringify(metrics, "\t"))
	file.store_string("\n")
	file.close()


func wait_for_ready(scene: Node) -> bool:
	for _frame in range(1800):
		if scene.has_method("get_validation_state") and scene.get_validation_state() == "ready":
			await _tree.process_frame
			return true
		await _tree.process_frame
	return false


func wait_for_player_floor(scene: Node) -> bool:
	for _frame in range(360):
		var summary: Dictionary = scene.get_validation_summary()
		if bool(summary.get("player_on_floor", false)):
			return true
		await _tree.physics_frame
	return false


func wait_for_revision(terrain_world_node: Node, revision: int) -> bool:
	for _frame in range(1800):
		if int(terrain_world_node.call("get_backend_world_revision")) >= revision:
			return true
		await _tree.process_frame
	return false


func wait_for_window(
	terrain_world_node: Node,
	expected_chunks: int,
	label: String,
	minimum_viewer_updates: int,
	center_chunk: Variant,
	max_active_resources: int
) -> bool:
	for _frame in range(2400):
		var metrics: Dictionary = terrain_world_node.call("get_runtime_metrics")
		var active_records := int(metrics.get("active_chunk_records", 0))
		var render_resources := int(metrics.get("render_resources", 0))
		var collision_resources := int(metrics.get("collision_resources", 0))
		var center_ready := true
		if center_chunk != null:
			center_ready = is_ready_snapshot(terrain_world_node.call("query_chunk_state", center_chunk, 0))
		if active_records == expected_chunks and \
				render_resources == expected_chunks and \
				collision_resources == expected_chunks and \
				int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and \
				center_ready and \
				int(metrics.get("queued_render", 0)) == 0 and \
				int(metrics.get("queued_collision", 0)) == 0 and \
				int(metrics.get("fully_ready_chunk_records", -1)) == active_records and \
				int(metrics.get("pending_chunk_retirements", 0)) == 0 and \
				int(metrics.get("render_fading_resources", 0)) == 0 and \
				active_records <= max_active_resources:
			return true
		await _tree.process_frame
	fail("G22 window did not settle at %s expected=%d metrics=%s" % [
		label,
		expected_chunks,
		str(terrain_world_node.call("get_runtime_metrics")),
	])
	return false


func is_ready_snapshot(snapshot: RefCounted) -> bool:
	return snapshot != null and snapshot.call("is_present") and \
			snapshot.call("is_visual_ready") and \
			snapshot.call("is_collision_required") and \
			snapshot.call("is_collision_ready") and \
			snapshot.call("is_fully_ready")


func _set_capture_overlays_visible(scene: Node, overlay_visible: bool) -> void:
	for child in scene.get_children():
		if child is CanvasLayer:
			(child as CanvasLayer).visible = overlay_visible
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference != null:
		var debug_overlay := reference.get_node_or_null("DebugOverlay") as CanvasLayer
		if debug_overlay != null:
			debug_overlay.visible = overlay_visible
