extends SceneTree

const MARKER := "WT_VALIDATION_G5_GODOT_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const CAPTURE_PATH := "res://artifacts/g5_material_performance/material_capture.png"


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var packed := load(SCENE_PATH)
	if packed == null:
		_fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	scene.set_camera_mode(&"overview")
	root.add_child(scene)
	if not await _wait_for_ready(scene):
		_fail("validation playtest scene did not become ready")
		return
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	if materializer == null:
		_fail("validation terrain materializer missing")
		return
	var material_summary := await _wait_for_materials(materializer)
	if int(material_summary.get("materialized_instances", 0)) <= 0:
		_fail("no terrain meshes were materialized: %s" % str(material_summary))
		return
	if not await _verify_material_reapply(scene, materializer):
		return
	var frame_metrics := await _measure_frames(scene, 180)
	if float(frame_metrics.get("avg_ms", 999.0)) > 40.0 or \
			float(frame_metrics.get("max_ms", 999.0)) > 250.0:
		_fail("G5 frame baseline exceeded guard: %s" % str(frame_metrics))
		return
	var image_metrics := await _capture_metrics()
	if int(image_metrics.get("colored_samples", 0)) < 500:
		_fail("material capture does not show enough colored terrain: %s" % str(image_metrics))
		return
	print("%s materialized=%d texture=%d avg_ms=%.3f max_ms=%.3f colored_samples=%d" % [
		MARKER,
		int(material_summary.get("materialized_instances", 0)),
		int(material_summary.get("texture_resolution", 0)),
		float(frame_metrics.get("avg_ms", 0.0)),
		float(frame_metrics.get("max_ms", 0.0)),
		int(image_metrics.get("colored_samples", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _wait_for_ready(scene: Node) -> bool:
	for _frame in range(900):
		if scene.has_method("get_validation_state") and scene.get_validation_state() == "ready":
			await process_frame
			return true
		await process_frame
	return false


func _wait_for_materials(materializer: Node) -> Dictionary:
	for _frame in range(120):
		var summary: Dictionary = materializer.call("get_material_summary")
		if bool(summary.get("applied", false)):
			return summary
		await process_frame
	return materializer.call("apply_materials_now")


func _verify_material_reapply(scene: Node, materializer: Node) -> bool:
	var mesh_instance := _first_terrain_mesh(scene)
	if mesh_instance == null:
		_fail("no terrain mesh found for material reapply check")
		return false
	mesh_instance.material_override = null
	for _frame in range(5):
		await process_frame
		if mesh_instance.material_override != null:
			var summary: Dictionary = materializer.call("get_material_summary")
			if int(summary.get("reapplied_instances", 0)) >= 0:
				return true
	_fail("terrain material was not restored after replacement-style clear")
	return false


func _first_terrain_mesh(scene: Node) -> MeshInstance3D:
	var terrain_world = scene.get_node("WtTerrainReferenceScene").call("get_terrain_world")
	var backend = terrain_world.call("get_backend_terrain")
	return _find_mesh(backend)


func _find_mesh(node: Node) -> MeshInstance3D:
	if node is MeshInstance3D and node.mesh != null:
		return node as MeshInstance3D
	for child in node.get_children():
		if child is Node:
			var found := _find_mesh(child)
			if found != null:
				return found
	return null


func _measure_frames(scene: Node, frame_count: int) -> Dictionary:
	var terrain_world = scene.get_node("WtTerrainReferenceScene").call("get_terrain_world")
	var total_us := 0
	var max_us := 0
	for _frame in range(frame_count):
		var start := Time.get_ticks_usec()
		await process_frame
		var elapsed := Time.get_ticks_usec() - start
		total_us += elapsed
		max_us = max(max_us, elapsed)
	var cold_idle: Dictionary = terrain_world.call("get_cold_idle_summary")
	if not bool(cold_idle.get("cold_idle", false)):
		_fail("terrain did not remain cold idle during G5 measurement")
	return {
		"avg_ms": float(total_us) / float(frame_count) / 1000.0,
		"max_ms": float(max_us) / 1000.0,
		"render_resources": int(cold_idle.get("render_resources", 0)),
		"collision_resources": int(cold_idle.get("collision_resources", 0)),
	}


func _capture_metrics() -> Dictionary:
	for _frame in range(20):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		return {"colored_samples": 0}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://artifacts/g5_material_performance"))
	if image.save_png(CAPTURE_PATH) != OK:
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
	push_error("WT_VALIDATION_G5_GODOT_FAIL: " + message)
	quit(1)
