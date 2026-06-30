extends SceneTree

const MARKER := "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const EXPECTED_ACTIVE_RESOURCES := 25
const HOT_PATHS := ["generation", "meshing", "streaming", "edit_application", "storage"]
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")
const EditOperation := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_operation.gd")
const EditBatch := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_batch.gd")

var _helpers: RefCounted

func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_FAIL")
	call_deferred("_run_test")

func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene):
		_helpers.fail("G48 scene did not become ready: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	if terrain_world == null or not terrain_world.has_method("get_hot_path_boundary_summary"):
		_helpers.fail("G48 terrain world missing hot-path boundary API")
		return
	var viewer_position: Vector3 = ProfileCatalog.viewer_positions(PROFILE_ID)[0]
	if not await _helpers.wait_for_window(
			terrain_world, EXPECTED_ACTIVE_RESOURCES, "g48_initial_window",
			1, _chunk_for(viewer_position), EXPECTED_ACTIVE_RESOURCES):
		return
	var before_revision := int(terrain_world.call("get_world_revision"))
	var edit_point: Vector3 = ProfileCatalog.edit_point(PROFILE_ID) + Vector3(9, 0, 0)
	if not await _submit_public_construct_edit(terrain_world, edit_point):
		return
	if not await _wait_for_revision(terrain_world, before_revision + 1):
		return
	if not await _helpers.wait_for_window(
			terrain_world, EXPECTED_ACTIVE_RESOURCES, "g48_after_edit",
			1, _chunk_for(edit_point), EXPECTED_ACTIVE_RESOURCES):
		return
	var boundary: Dictionary = terrain_world.call("get_hot_path_boundary_summary")
	if not _verify_boundary(boundary):
		return
	var api: Dictionary = terrain_world.call("get_terrain_api_contract_summary")
	var debug_methods := Array(Dictionary(api.get("stable_groups", {})).get("debug", []))
	if not debug_methods.has("get_hot_path_boundary_summary"):
		_helpers.fail("G48 public API summary omits hot-path boundary method: %s" % str(api))
		return
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not _helpers.assert_no_dense_files("g48_finish"):
		return
	print("%s profile=%s hot_paths=%d native_owned=%d gdscript_hot_loops=0 edit_committed=1 max_render_resources=%d max_collision_resources=%d max_active_records=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		HOT_PATHS.size(),
		HOT_PATHS.size(),
		int(metrics.get("render_resources", 0)),
		int(metrics.get("collision_resources", 0)),
		int(metrics.get("active_chunk_records", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)

func _verify_boundary(boundary: Dictionary) -> bool:
	if str(boundary.get("implementation", "")) != "terrain_addon_native_hot_path_boundary_v1":
		_helpers.fail("G48 boundary implementation mismatch: %s" % str(boundary))
		return false
	var paths := Dictionary(boundary.get("normal_runtime_hot_paths", {}))
	for path_name in HOT_PATHS:
		var section := Dictionary(paths.get(path_name, {}))
		if str(section.get("owner", "")) != "world_transvoxel_native_backend":
			_helpers.fail("G48 hot path is not native/backend owned: %s %s" % [path_name, str(section)])
			return false
		if str(section.get("gdscript_role", "")).is_empty():
			_helpers.fail("G48 hot path missing bounded GDScript role: %s" % path_name)
			return false
	var forbidden := Array(boundary.get("forbidden_gdscript_runtime_roles", []))
	if forbidden.size() < 5 or not forbidden.has("terrain_mesh_build_loop"):
		_helpers.fail("G48 forbidden runtime roles incomplete: %s" % str(boundary))
		return false
	return true

func _submit_public_construct_edit(terrain_world: Node, point: Vector3) -> bool:
	var batch = EditBatch.new()
	var operation = EditOperation.new()
	operation.mode = EditOperation.Mode.CONSTRUCT
	operation.brush_shape = EditOperation.BrushShape.SPHERE
	operation.center = point
	operation.radius = 1.8
	operation.material_id = 4
	operation.density_value = 1.0
	if not batch.add_operation(operation):
		_helpers.fail("G48 edit batch rejected operation")
		return false
	if not bool(terrain_world.call("submit_edit_batch", batch, 48048)):
		_helpers.fail("G48 submit_edit_batch failed: %s" % str(terrain_world.call("get_last_error")))
		return false
	return true

func _wait_for_revision(terrain_world: Node, revision: int) -> bool:
	for _frame in range(1800):
		if int(terrain_world.call("get_world_revision")) >= revision:
			return true
		await process_frame
	_helpers.fail("G48 world revision did not reach %d" % revision)
	return false

func _chunk_for(point: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(point.x / 16.0)), 0, 127), 0, clamp(int(floor(point.z / 16.0)), 0, 127))
