extends SceneTree

const MARKER := "WT_VALIDATION_G6_GODOT_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

const PROFILES := [&"flat_large", &"mountain_large"]


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var results: Array[Dictionary] = []
	for profile_id in PROFILES:
		var result := await _run_profile(profile_id)
		if result.is_empty():
			return
		results.append(result)
	print("%s profiles=%d flat_triangles=%d mountain_triangles=%d captures=%d" % [
		MARKER,
		results.size(),
		int(results[0].get("triangles", 0)),
		int(results[1].get("triangles", 0)),
		results.size(),
	])
	quit(0)


func _run_profile(profile_id: StringName) -> Dictionary:
	var packed := load(SCENE_PATH)
	if packed == null:
		_fail("validation playtest scene did not load")
		return {}
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	scene.configure_playtest_profile(profile_id)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _wait_for_ready(scene):
		_fail("%s did not become ready: %s" % [str(profile_id), str(scene.get_validation_summary())])
		return {}
	if not await _wait_for_player_floor(scene):
		_fail("%s player did not settle on floor: %s" % [str(profile_id), str(scene.get_validation_summary())])
		return {}
	var summary: Dictionary = scene.get_validation_summary()
	if not _summary_is_multi_chunk_playable(summary):
		_fail("%s summary is not multi-chunk playable: %s" % [str(profile_id), str(summary)])
		return {}
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var material_summary := await _wait_for_materials(materializer)
	if int(material_summary.get("materialized_instances", 0)) <= 0:
		_fail("%s materializer did not apply: %s" % [str(profile_id), str(material_summary)])
		return {}
	if not await _verify_edits(scene, profile_id):
		return {}
	scene.set_camera_mode(&"first_person")
	var player_position: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	scene.set_player_visual_visible(false)
	scene.set_manual_camera_view(
		player_position + Vector3(0.0, 1.55, 0.0),
		player_position + Vector3(3.0, -8.0, 3.0)
	)
	var first_person_metrics := await _capture(profile_id, &"first_person")
	if int(first_person_metrics.get("colored_samples", 0)) < 50:
		_fail("%s first-person capture lacks colored terrain: %s summary=%s" % [
			str(profile_id),
			str(first_person_metrics),
			str(scene.get_validation_summary()),
		])
		return {}
	scene.set_player_visual_visible(true)
	scene.set_camera_mode(&"overview")
	var image_metrics := await _capture(profile_id, &"overview")
	if int(image_metrics.get("colored_samples", 0)) < 500:
		_fail("%s capture lacks colored terrain: %s" % [str(profile_id), str(image_metrics)])
		return {}
	scene.queue_free()
	await process_frame
	return {
		"profile": str(profile_id),
		"triangles": int(summary.get("terrain_triangles", 0)),
		"materialized": int(material_summary.get("materialized_instances", 0)),
		"colored_samples": int(image_metrics.get("colored_samples", 0)),
	}


func _summary_is_multi_chunk_playable(summary: Dictionary) -> bool:
	return int(summary.get("viewer_count", 0)) >= 16 and \
			int(summary.get("terrain_triangles", 0)) >= 3000 and \
			int(summary.get("render_resources", 0)) >= 8 and \
			int(summary.get("collision_resources", 0)) >= 8 and \
			bool(summary.get("player_present", false)) and \
			bool(summary.get("player_camera_current", false)) and \
			bool(summary.get("crosshair_present", false))


func _verify_edits(scene: Node, profile_id: StringName) -> bool:
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if reference == null or interactor == null:
		_fail("missing terrain reference or interactor")
		return false
	var terrain_world = reference.call("get_terrain_world")
	var start_revision := int(terrain_world.call("get_backend_world_revision"))
	var point := ProfileCatalog.edit_point(profile_id)
	if not bool(interactor.call("submit_sphere_edit", &"carve", point, 1.8, -1, 1.0)):
		_fail("%s carve was rejected" % str(profile_id))
		return false
	if not await _wait_for_revision(terrain_world, start_revision + 1):
		_fail("%s carve did not commit" % str(profile_id))
		return false
	if not await _wait_for_cold_idle(terrain_world):
		_fail("%s carve did not settle" % str(profile_id))
		return false
	if not bool(interactor.call("submit_sphere_edit", &"construct", point, 1.8, 4, 1.0)):
		_fail("%s construct was rejected" % str(profile_id))
		return false
	if not await _wait_for_revision(terrain_world, start_revision + 2):
		_fail("%s construct did not commit" % str(profile_id))
		return false
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	return int(metrics.get("edit_replacements", 0)) > 0 and int(metrics.get("collision_resources", 0)) > 0


func _wait_for_ready(scene: Node) -> bool:
	for _frame in range(900):
		if scene.has_method("get_validation_state") and scene.get_validation_state() == "ready":
			await process_frame
			return true
		await process_frame
	return false


func _wait_for_player_floor(scene: Node) -> bool:
	for _frame in range(180):
		var summary: Dictionary = scene.get_validation_summary()
		if bool(summary.get("player_on_floor", false)):
			return true
		await physics_frame
	return false


func _wait_for_materials(materializer: Node) -> Dictionary:
	if materializer == null:
		return {}
	for _frame in range(120):
		var summary: Dictionary = materializer.call("get_material_summary")
		if bool(summary.get("applied", false)):
			return summary
		await process_frame
	return materializer.call("apply_materials_now")


func _wait_for_revision(terrain_world: Node, revision: int) -> bool:
	for _frame in range(900):
		if int(terrain_world.call("get_backend_world_revision")) >= revision:
			return true
		await process_frame
	return false


func _wait_for_cold_idle(terrain_world: Node) -> bool:
	for _frame in range(900):
		if bool(Dictionary(terrain_world.call("get_cold_idle_summary")).get("cold_idle", false)):
			await process_frame
			return true
		await process_frame
	return false


func _capture(profile_id: StringName, view_id: StringName) -> Dictionary:
	for _frame in range(30):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		return {"colored_samples": 0}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://artifacts/g6_profile_selectable_playable_world"))
	var path := "res://artifacts/g6_profile_selectable_playable_world/%s_%s.png" % [
		str(profile_id),
		str(view_id),
	]
	if image.save_png(path) != OK:
		return {"colored_samples": 0}
	var colored := 0
	for y in range(0, image.get_height(), 2):
		for x in range(0, image.get_width(), 2):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.07 and color.g > color.b:
				colored += 1
	return {"colored_samples": colored}


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G6_GODOT_FAIL: " + message)
	quit(1)
