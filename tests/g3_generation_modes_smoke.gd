extends SceneTree

const MARKER := "WT_VALIDATION_G3_GODOT_PASS"
const ReferenceScene := preload("res://addons/world_transvoxel_terrain/debug/wt_terrain_reference_scene.tscn")
const GenerationProfile := preload("res://addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")

const MODES := [
	{
		"id": "flat_8x8",
		"source_mode": "FLAT",
		"world_path": "res://build/g3-generation-fixtures/flat_8x8/world.wtworld",
		"root_path": "res://build/g3-generation-fixtures/flat_8x8",
		"capture_path": "res://artifacts/g3_generation_modes/flat_8x8.png",
	},
	{
		"id": "mountain_8x8",
		"source_mode": "BAKED_WORLD",
		"world_path": "res://build/g3-generation-fixtures/mountain_8x8/world.wtworld",
		"root_path": "res://build/g3-generation-fixtures/mountain_8x8",
		"capture_path": "res://artifacts/g3_generation_modes/mountain_8x8.png",
	},
]


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var results: Array[Dictionary] = []
	for mode in MODES:
		var result := await _run_mode(Dictionary(mode))
		if result.is_empty():
			return
		results.append(result)
	if float(results[1].get("vertical_span", 0.0)) <= float(results[0].get("vertical_span", 0.0)) + 1.0:
		_fail("mountain profile did not exceed flat vertical span: %s" % str(results))
		return
	print("%s profiles=%d flat_triangles=%d mountain_triangles=%d mountain_span=%.3f" % [
		MARKER,
		results.size(),
		int(results[0].get("triangles", 0)),
		int(results[1].get("triangles", 0)),
		float(results[1].get("vertical_span", 0.0)),
	])
	quit(0)


func _run_mode(mode: Dictionary) -> Dictionary:
	var packed: PackedScene = ReferenceScene
	var scene: Node3D = packed.instantiate()
	root.add_child(scene)
	_configure_view(scene)
	var terrain_world = scene.call("get_terrain_world")
	terrain_world.set("generation_profile", _generation_profile(mode))
	terrain_world.set("storage_profile", _storage_profile(mode))
	if not scene.call("start_reference_backend_world"):
		_fail("backend start failed for %s" % str(mode.get("id", "")))
		return {}
	if not await _wait_for_state(terrain_world, "running"):
		_fail("backend did not start for %s" % str(mode.get("id", "")))
		return {}
	if not _submit_profile_viewers(scene, str(mode.get("id", ""))):
		return {}
	var metrics := await _wait_for_cold_idle(terrain_world)
	if metrics.is_empty():
		_fail("profile did not reach cold idle: %s" % str(mode.get("id", "")))
		return {}
	var stats := _mesh_stats(terrain_world.call("get_backend_terrain"))
	if int(stats.get("triangles", 0)) <= 0:
		_fail("profile has no terrain triangles: %s" % str(mode.get("id", "")))
		return {}
	if int(metrics.get("render_resources", 0)) < 64 or int(metrics.get("collision_resources", 0)) < 64:
		_fail("profile missing render/collision resources: %s %s" % [str(mode.get("id", "")), str(metrics)])
		return {}
	if not await _capture(str(mode.get("capture_path", ""))):
		return {}
	scene.queue_free()
	await process_frame
	return {
		"id": str(mode.get("id", "")),
		"triangles": int(stats.get("triangles", 0)),
		"vertical_span": float(stats.get("vertical_span", 0.0)),
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
	}


func _submit_profile_viewers(scene: Node, mode_id: String) -> bool:
	var viewer_id := 1
	for position in [
		Vector3(40.0, 8.0, 40.0),
		Vector3(88.0, 8.0, 40.0),
		Vector3(40.0, 8.0, 88.0),
		Vector3(88.0, 8.0, 88.0),
	]:
		if not scene.call("update_reference_viewer", viewer_id, 1, position, 2, 0):
			_fail("viewer update failed for %s at %s" % [mode_id, str(position)])
			return false
		viewer_id += 1
	return true


func _generation_profile(mode: Dictionary) -> Resource:
	var profile = GenerationProfile.new()
	profile.profile_id = StringName(str(mode.get("id", "")))
	if str(mode.get("source_mode", "")) == "FLAT":
		profile.source_mode = GenerationProfile.SourceMode.FLAT
	else:
		profile.source_mode = GenerationProfile.SourceMode.BAKED_WORLD
	profile.seed = 3003
	return profile


func _storage_profile(mode: Dictionary) -> Resource:
	var storage = StorageProfile.new()
	storage.profile_id = StringName(str(mode.get("id", "")))
	storage.world_manifest_path = str(mode.get("world_path", ""))
	storage.object_root_path = str(mode.get("root_path", ""))
	storage.edit_journal_path = "%s/world.wtedit" % str(mode.get("root_path", ""))
	storage.snapshot_directory = "%s/snapshots" % str(mode.get("root_path", ""))
	storage.allow_res_paths_for_test_fixtures = true
	return storage


func _configure_view(scene: Node3D) -> void:
	var camera := Camera3D.new()
	camera.name = "G3CaptureCamera"
	camera.current = true
	camera.position = Vector3(74, 42, 86)
	scene.add_child(camera)
	camera.look_at(Vector3(32, 8, 32), Vector3.UP)
	var light := DirectionalLight3D.new()
	light.name = "G3CaptureLight"
	light.light_energy = 2.0
	light.rotation_degrees = Vector3(-45, 35, 0)
	scene.add_child(light)


func _wait_for_state(terrain_world: Node, expected: String) -> bool:
	for _frame in range(900):
		if terrain_world.call("get_backend_world_state_name") == expected:
			await process_frame
			return true
		await process_frame
	return false


func _wait_for_cold_idle(terrain_world: Node) -> Dictionary:
	for _frame in range(900):
		var summary: Dictionary = terrain_world.call("get_cold_idle_summary")
		if bool(summary.get("cold_idle", false)) and int(summary.get("render_resources", 0)) > 0:
			await process_frame
			return summary
		await process_frame
	return {}


func _mesh_stats(node: Node) -> Dictionary:
	var stats := {
		"triangles": 0,
		"min_y": INF,
		"max_y": -INF,
	}
	_accumulate_mesh_stats(node, stats)
	stats["vertical_span"] = float(stats.get("max_y", 0.0)) - float(stats.get("min_y", 0.0))
	return stats


func _accumulate_mesh_stats(node: Node, stats: Dictionary) -> void:
	if node is MeshInstance3D:
		var instance := node as MeshInstance3D
		if instance.mesh != null:
			var faces := instance.mesh.get_faces()
			stats["triangles"] = int(stats.get("triangles", 0)) + int(faces.size() / 3)
			for vertex in faces:
				var world_vertex: Vector3 = instance.global_transform * vertex
				stats["min_y"] = min(float(stats.get("min_y", INF)), world_vertex.y)
				stats["max_y"] = max(float(stats.get("max_y", -INF)), world_vertex.y)
	for child in node.get_children():
		if child is Node:
			_accumulate_mesh_stats(child, stats)


func _capture(path: String) -> bool:
	for _frame in range(30):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("capture image is empty")
		return false
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://artifacts/g3_generation_modes"))
	if image.save_png(path) != OK:
		_fail("failed to save capture: %s" % path)
		return false
	return true


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G3_GODOT_FAIL: " + message)
	quit(1)
