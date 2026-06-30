extends SceneTree

const MARKER := "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const EXPECTED_ACTIVE_RESOURCES := 25
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ReferenceScene := preload("res://addons/world_transvoxel_terrain/debug/wt_terrain_reference_scene.tscn")
const EditOperation := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_operation.gd")
const EditBatch := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_batch.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

const PUBLIC_METHODS := [
	"get_terrain_api_contract_summary", "get_profile_summaries", "start_world",
	"stop_world", "is_world_running", "get_world_state_name", "get_world_revision",
	"get_world_source_revision", "get_world_page_count", "update_viewer",
	"remove_viewer", "query_chunk_state", "submit_edit_batch",
	"get_last_edit_submission_summary", "request_authoritative_sample",
	"request_authoritative_samples", "request_world_compaction",
	"request_world_migration", "get_runtime_metrics", "is_cold_idle",
	"get_cold_idle_summary", "get_debug_snapshot",
]
const PUBLIC_GROUPS := ["profiles", "lifecycle", "streaming", "editing", "storage", "telemetry", "debug"]

var _helpers: RefCounted
var _sample_results: Dictionary = {}
var _sample_failures: Dictionary = {}
var _sample_batch_results: Dictionary = {}
var _sample_batch_failures: Dictionary = {}

func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_FAIL")
	call_deferred("_run_test")

func _run_test() -> void:
	var reference = ReferenceScene.instantiate()
	root.add_child(reference)
	await process_frame
	reference.call("ensure_reference_defaults")
	var terrain_world: Node = reference.call("get_terrain_world")
	terrain_world.set("generation_profile", ProfileCatalog.generation_profile(PROFILE_ID))
	terrain_world.set("storage_profile", ProfileCatalog.storage_profile(PROFILE_ID))
	if not _verify_public_surface(terrain_world):
		return
	_connect_public_sample_signals(terrain_world)
	if not bool(terrain_world.call("start_world")):
		_helpers.fail("G46 start_world failed: %s" % str(terrain_world.call("get_last_error")))
		return
	if not await _wait_for_world_state(terrain_world, "running"):
		return
	var viewer_position: Vector3 = ProfileCatalog.viewer_positions(PROFILE_ID)[0]
	if not bool(terrain_world.call("update_viewer", 46, 1, viewer_position, 2, 0)):
		_helpers.fail("G46 update_viewer failed: %s" % str(terrain_world.call("get_last_error")))
		return
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g46_public_viewer", 1, _chunk_for(viewer_position), EXPECTED_ACTIVE_RESOURCES):
		return
	var before_revision := int(terrain_world.call("get_world_revision"))
	var edit_point: Vector3 = ProfileCatalog.edit_point(PROFILE_ID) + Vector3(7, 0, 0)
	if not await _submit_public_construct_edit(terrain_world, edit_point):
		return
	if not await _wait_for_revision(terrain_world, before_revision + 1):
		return
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g46_after_public_edit", 1, _chunk_for(edit_point), EXPECTED_ACTIVE_RESOURCES):
		return
	var sample := await _public_sample(terrain_world, Vector3i(edit_point))
	if sample.is_empty():
		return
	var batch_sample_count := await _public_batch_sample_count(terrain_world, Vector3i(edit_point))
	if batch_sample_count < 2:
		return
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var debug_snapshot: Dictionary = terrain_world.call("get_debug_snapshot")
	var api: Dictionary = terrain_world.call("get_terrain_api_contract_summary")
	if int(sample.get("material", 0)) != 4 or float(sample.get("density", 0.0)) > -0.99:
		_helpers.fail("G46 public sample did not observe edit: %s" % str(sample))
		return
	if str(debug_snapshot.get("implementation", "")) != "debug_snapshot_contract":
		_helpers.fail("G46 debug snapshot contract mismatch: %s" % str(debug_snapshot))
		return
	if not _helpers.assert_no_dense_files("g46_finish"):
		return
	print("%s profile=%s api_version=%d public_methods=%d stable_groups=%d lifecycle=1 streaming=1 edits=1 storage=1 telemetry=1 debug=1 samples=%d edit_committed=1 world_revision_delta=%d max_render_resources=%d max_collision_resources=%d max_active_records=%d direct_backend_calls=0 dense_world_files=0" % [
		MARKER, str(PROFILE_ID), int(api.get("api_version", 0)), PUBLIC_METHODS.size(),
		PUBLIC_GROUPS.size(), batch_sample_count + 1, int(terrain_world.call("get_world_revision")) - before_revision,
		int(metrics.get("render_resources", 0)), int(metrics.get("collision_resources", 0)),
		int(metrics.get("active_chunk_records", 0)),
	])
	reference.queue_free()
	await process_frame
	quit(0)

func _verify_public_surface(terrain_world: Node) -> bool:
	for method in PUBLIC_METHODS:
		if not terrain_world.has_method(method):
			_helpers.fail("G46 missing public method: %s" % method)
			return false
	for signal_name in ["authoritative_sample_ready", "authoritative_sample_failed", "authoritative_samples_ready", "authoritative_samples_failed", "world_snapshot_ready", "world_snapshot_failed"]:
		if not terrain_world.has_signal(signal_name):
			_helpers.fail("G46 missing public signal: %s" % signal_name)
			return false
	var api: Dictionary = terrain_world.call("get_terrain_api_contract_summary")
	var groups := Dictionary(api.get("stable_groups", {}))
	for group in PUBLIC_GROUPS:
		if not groups.has(group) or Array(groups[group]).is_empty():
			_helpers.fail("G46 missing API group: %s in %s" % [group, str(api)])
			return false
	var profiles: Dictionary = terrain_world.call("get_profile_summaries")
	for key in ["generation", "storage", "material"]:
		if not bool(Dictionary(profiles.get(key, {})).get("assigned", false)):
			_helpers.fail("G46 profile summary missing %s: %s" % [key, str(profiles)])
			return false
	return int(api.get("api_version", 0)) == 1

func _submit_public_construct_edit(terrain_world: Node, point: Vector3) -> bool:
	var batch = EditBatch.new()
	var operation = EditOperation.new()
	operation.mode = EditOperation.Mode.CONSTRUCT
	operation.brush_shape = EditOperation.BrushShape.SPHERE
	operation.center = point
	operation.radius = 1.8
	operation.material_id = 4
	operation.density_value = 1.0
	if not batch.add_operation(operation) or not bool(terrain_world.call("submit_edit_batch", batch, 46046)):
		_helpers.fail("G46 submit_edit_batch failed: %s" % str(terrain_world.call("get_last_error")))
		return false
	return true

func _public_sample(terrain_world: Node, point: Vector3i) -> Dictionary:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(terrain_world.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_helpers.fail("G46 request_authoritative_sample failed at %s" % str(point))
		return {}
	var sample: RefCounted = _sample_results[request_id]
	return {"density": float(sample.call("get_density")), "material": int(sample.call("get_material"))}

func _public_batch_sample_count(terrain_world: Node, point: Vector3i) -> int:
	_sample_batch_results.clear()
	_sample_batch_failures.clear()
	var request_id := int(terrain_world.call("request_authoritative_samples", [point, point + Vector3i(1, 0, 0)], 0))
	if request_id <= 0 or not await _wait_for_sample_batch(request_id):
		_helpers.fail("G46 request_authoritative_samples failed at %s" % str(point))
		return 0
	return Array(_sample_batch_results[request_id]).size()

func _connect_public_sample_signals(terrain_world: Node) -> void:
	for pair in [["authoritative_sample_ready", "_on_sample_ready"], ["authoritative_sample_failed", "_on_sample_failed"], ["authoritative_samples_ready", "_on_samples_ready"], ["authoritative_samples_failed", "_on_samples_failed"]]:
		var callable := Callable(self, pair[1])
		if not terrain_world.is_connected(pair[0], callable):
			terrain_world.connect(pair[0], callable)

func _wait_for_world_state(terrain_world: Node, expected: String) -> bool:
	for _frame in range(900):
		if str(terrain_world.call("get_world_state_name")) == expected:
			return true
		await process_frame
	_helpers.fail("G46 world did not reach state %s" % expected)
	return false

func _wait_for_revision(terrain_world: Node, revision: int) -> bool:
	for _frame in range(1800):
		if int(terrain_world.call("get_world_revision")) >= revision:
			return true
		await process_frame
	_helpers.fail("G46 world revision did not reach %d" % revision)
	return false

func _wait_for_sample(request_id: int) -> bool:
	for _frame in range(900):
		if _sample_results.has(request_id):
			return true
		if _sample_failures.has(request_id):
			return false
		await process_frame
	return false

func _wait_for_sample_batch(request_id: int) -> bool:
	for _frame in range(900):
		if _sample_batch_results.has(request_id):
			return true
		if _sample_batch_failures.has(request_id):
			return false
		await process_frame
	return false

func _chunk_for(point: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(point.x / 16.0)), 0, 127), 0, clamp(int(floor(point.z / 16.0)), 0, 127))

func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample

func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error

func _on_samples_ready(request_id: int, samples: Array) -> void:
	_sample_batch_results[request_id] = samples

func _on_samples_failed(request_id: int, error: String) -> void:
	_sample_batch_failures[request_id] = error
