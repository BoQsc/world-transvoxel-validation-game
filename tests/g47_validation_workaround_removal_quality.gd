extends SceneTree

const MARKER := "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_ACTIVE_RESOURCES := 25
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted

func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_FAIL")
	call_deferred("_run_test")

func _run_test() -> void:
	for path in [
		"res://scripts/validation_terrain_materials.gd",
		"res://scripts/validation_mesh_stats.gd",
		"res://materials/validation_terrain_palette.gdshader",
	]:
		if FileAccess.file_exists(path):
			_helpers.fail("G47 local terrain workaround still exists: %s" % path)
			return
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene):
		_helpers.fail("G47 scene did not become ready: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	if terrain_world == null or materializer == null:
		_helpers.fail("G47 terrain world or material applicator missing")
		return
	var material_script := str(materializer.get_script().resource_path)
	if not material_script.ends_with("addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd"):
		_helpers.fail("G47 material applicator is not addon-owned: %s" % material_script)
		return
	var material_summary := await _wait_for_material_summary(materializer)
	if material_summary.is_empty():
		return
	var summary: Dictionary = scene.get_validation_summary()
	if str(summary.get("terrain_mesh_stats_implementation", "")) != "terrain_addon_mesh_stats":
		_helpers.fail("G47 mesh stats are not addon-owned: %s" % str(summary))
		return
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not _helpers.assert_no_dense_files("g47_finish"):
		return
	print("%s profile=%s moved_helpers=2 local_workaround_files=0 material_impl=%s mesh_stats_impl=%s materialized=%d max_render_resources=%d max_collision_resources=%d max_active_records=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		str(material_summary.get("implementation", "")),
		str(summary.get("terrain_mesh_stats_implementation", "")),
		int(material_summary.get("materialized_instances", 0)),
		int(metrics.get("render_resources", 0)),
		int(metrics.get("collision_resources", 0)),
		int(metrics.get("active_chunk_records", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)

func _wait_for_material_summary(materializer: Node) -> Dictionary:
	for _frame in range(240):
		var summary: Dictionary = materializer.call("get_material_summary")
		if bool(summary.get("applied", false)) and \
				int(summary.get("materialized_instances", 0)) >= EXPECTED_ACTIVE_RESOURCES and \
				str(summary.get("implementation", "")) == "terrain_addon_material_applicator":
			return summary
		await process_frame
	_helpers.fail("G47 addon material applicator did not apply: %s" % str(materializer.call("get_material_summary")))
	return {}
