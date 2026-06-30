extends SceneTree

const MARKER := "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_COMPACTION_PASS"
const PROFILE_ID := &"g8_sparse_2k"
const OUTPUT_DIR := "res://build/production-lifecycle-fixture/g45_compacted_snapshot"
const EXPECTED_SOURCE_REVISION := 8101
const EXPECTED_COMPACTED_SOURCE_REVISION := 8102
const EXPECTED_PAGE_COUNT := 93
const EXPECTED_ACTIVE_RESOURCES := 25
const EDIT_POINT := Vector3(1000, 8, 1000)
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ReferenceScene := preload("res://addons/world_transvoxel_terrain/debug/wt_terrain_reference_scene.tscn")
const GenerationProfile := preload("res://addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")
const EditOperation := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_operation.gd")
const EditBatch := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_batch.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

var _helpers: RefCounted
var _sample_results: Dictionary = {}
var _sample_failures: Dictionary = {}
var _snapshot_results: Dictionary = {}
var _snapshot_failures: Dictionary = {}
var _edit_failures: Array[String] = []

func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_COMPACTION_FAIL")
	call_deferred("_run_test")

func _run_test() -> void:
	var reference := await _start_reference(PROFILE_ID, "g45_compaction_initial", EDIT_POINT, EXPECTED_ACTIVE_RESOURCES)
	if reference == null:
		return
	var terrain_world: Node = reference.call("get_terrain_world")
	var backend: Node = terrain_world.call("get_backend_terrain")
	_connect_backend(backend)
	_connect_snapshot_signals(terrain_world)
	if int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT or int(backend.call("get_world_source_revision")) != EXPECTED_SOURCE_REVISION:
		_helpers.fail("G45 compaction metadata mismatch")
		return
	if not await _submit_edit_and_verify(terrain_world, backend):
		return
	_snapshot_results.clear()
	_snapshot_failures.clear()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT_DIR.get_base_dir()))
	var request_id := int(terrain_world.call("request_world_compaction", OUTPUT_DIR, EXPECTED_COMPACTED_SOURCE_REVISION))
	if request_id <= 0:
		_helpers.fail("G45 compaction request rejected: %s" % str(terrain_world.call("get_last_error")))
		return
	if not await _wait_for_snapshot(request_id):
		return
	var snapshot: Dictionary = _snapshot_results[request_id]
	if int(snapshot.get("source_revision", 0)) != EXPECTED_COMPACTED_SOURCE_REVISION or int(snapshot.get("page_count", 0)) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G45 snapshot metadata mismatch: %s" % str(snapshot))
		return
	var manifest_path := str(snapshot.get("manifest_path", ""))
	var output_root := manifest_path.get_base_dir()
	if not FileAccess.file_exists(manifest_path) or FileAccess.file_exists("%s/world.wtedit" % output_root):
		_helpers.fail("G45 compacted output invalid: %s" % manifest_path)
		return
	var reopened := await _start_compacted_reference(manifest_path, output_root)
	if reopened == null:
		return
	var reopened_world: Node = reopened.call("get_terrain_world")
	var reopened_backend: Node = reopened_world.call("get_backend_terrain")
	_connect_backend(reopened_backend)
	if int(reopened_backend.call("get_world_source_revision")) != EXPECTED_COMPACTED_SOURCE_REVISION or int(reopened_backend.call("get_world_revision")) != int(snapshot.get("world_revision", 0)):
		_helpers.fail("G45 reopened revision mismatch")
		return
	if not await _verify_sample(reopened_backend, Vector3i(EDIT_POINT), -1.0, 4):
		return
	var metrics: Dictionary = reopened_world.call("get_runtime_metrics")
	print("%s compaction_profile=%s compacted_pages=%d compacted_source_revision=%d compacted_world_revision=%d compacted_reopened=1 compacted_journal_exists=false render_resources=%d collision_resources=%d active_records=%d dense_world_files=0" % [
		MARKER, str(PROFILE_ID), int(snapshot.get("page_count", 0)), int(snapshot.get("source_revision", 0)),
		int(snapshot.get("world_revision", 0)), int(metrics.get("render_resources", 0)),
		int(metrics.get("collision_resources", 0)), int(metrics.get("active_chunk_records", 0)),
	])
	reference.queue_free()
	reopened.queue_free()
	await process_frame
	quit(0)

func _start_reference(profile_id: StringName, label: String, viewer_position: Vector3, expected_resources: int) -> Node:
	var reference = ReferenceScene.instantiate()
	root.add_child(reference)
	await process_frame
	reference.call("ensure_reference_defaults")
	var terrain_world: Node = reference.call("get_terrain_world")
	terrain_world.set("generation_profile", ProfileCatalog.generation_profile(profile_id))
	terrain_world.set("storage_profile", ProfileCatalog.storage_profile(profile_id))
	if not bool(reference.call("start_reference_backend_world")):
		_helpers.fail("G45 failed to start reference world %s: %s" % [label, str(terrain_world.call("get_last_error"))])
		return null
	return await _finish_reference_start(reference, terrain_world, label, viewer_position, expected_resources)

func _start_compacted_reference(manifest_path: String, object_root: String) -> Node:
	var reference = ReferenceScene.instantiate()
	root.add_child(reference)
	await process_frame
	reference.call("ensure_reference_defaults")
	var terrain_world: Node = reference.call("get_terrain_world")
	var generation = GenerationProfile.new()
	generation.profile_id = &"g45_compacted_reopen"
	generation.source_mode = GenerationProfile.SourceMode.BAKED_WORLD
	var storage = StorageProfile.new()
	storage.profile_id = &"g45_compacted_reopen"
	storage.world_manifest_path = manifest_path
	storage.object_root_path = object_root
	storage.edit_journal_path = "%s/world.wtedit" % object_root
	storage.snapshot_directory = "%s/snapshots" % object_root
	terrain_world.set("generation_profile", generation)
	terrain_world.set("storage_profile", storage)
	if not bool(reference.call("start_reference_backend_world")):
		_helpers.fail("G45 failed to reopen compacted world: %s" % str(terrain_world.call("get_last_error")))
		return null
	return await _finish_reference_start(reference, terrain_world, "g45_compacted_reopen", EDIT_POINT, EXPECTED_ACTIVE_RESOURCES)

func _finish_reference_start(reference: Node, terrain_world: Node, label: String, viewer_position: Vector3, expected_resources: int) -> Node:
	if not await _wait_for_running(terrain_world, label):
		return null
	if not bool(reference.call("update_reference_viewer", 1, 1, viewer_position, 2, 0)):
		_helpers.fail("G45 viewer update failed")
		return null
	if not await _helpers.wait_for_window(terrain_world, expected_resources, label, 1, _chunk_for(viewer_position), expected_resources):
		return null
	return reference

func _submit_edit_and_verify(terrain_world: Node, backend: Node) -> bool:
	_edit_failures.clear()
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var batch = EditBatch.new()
	var operation = EditOperation.new()
	operation.mode = EditOperation.Mode.CONSTRUCT
	operation.brush_shape = EditOperation.BrushShape.SPHERE
	operation.center = EDIT_POINT
	operation.radius = 1.8
	operation.material_id = 4
	operation.density_value = 1.0
	if not batch.add_operation(operation) or not bool(terrain_world.call("submit_edit_batch", batch, 45045)):
		_helpers.fail("G45 compaction edit submission failed")
		return false
	if not await _wait_for_revision_or_failure(terrain_world, before_revision + 1):
		_helpers.fail("G45 compaction edit did not commit")
		return false
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g45_after_compaction_edit", 0, _chunk_for(EDIT_POINT), EXPECTED_ACTIVE_RESOURCES):
		return false
	return await _verify_sample(backend, Vector3i(EDIT_POINT), -1.0, 4)

func _verify_sample(backend: Node, point: Vector3i, expected_density: float, expected_material: int) -> bool:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(backend.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_helpers.fail("G45 authoritative sample query failed at %s" % str(point))
		return false
	var sample: RefCounted = _sample_results[request_id]
	if absf(float(sample.call("get_density")) - expected_density) > 0.001 or int(sample.call("get_material")) != expected_material:
		_helpers.fail("G45 sample mismatch at %s" % str(point))
		return false
	return true

func _connect_backend(backend: Node) -> void:
	if not backend.edit_failed.is_connected(_on_edit_failed):
		backend.connect("edit_failed", _on_edit_failed)
	if not backend.authoritative_sample_ready.is_connected(_on_sample_ready):
		backend.connect("authoritative_sample_ready", _on_sample_ready)
	if not backend.authoritative_sample_failed.is_connected(_on_sample_failed):
		backend.connect("authoritative_sample_failed", _on_sample_failed)

func _connect_snapshot_signals(terrain_world: Node) -> void:
	var ready := Callable(self, "_on_snapshot_ready")
	if terrain_world.has_signal("world_snapshot_ready") and not terrain_world.is_connected("world_snapshot_ready", ready):
		terrain_world.connect("world_snapshot_ready", ready)
	var failed := Callable(self, "_on_snapshot_failed")
	if terrain_world.has_signal("world_snapshot_failed") and not terrain_world.is_connected("world_snapshot_failed", failed):
		terrain_world.connect("world_snapshot_failed", failed)

func _wait_for_running(terrain_world: Node, label: String) -> bool:
	for _frame in range(900):
		if str(terrain_world.call("get_backend_world_state_name")) == "running":
			return true
		await process_frame
	_helpers.fail("G45 world did not reach running state: %s" % label)
	return false

func _wait_for_revision_or_failure(terrain_world: Node, revision: int) -> bool:
	for _frame in range(1800):
		if int(terrain_world.call("get_backend_world_revision")) >= revision:
			return true
		if not _edit_failures.is_empty():
			return false
		await process_frame
	return false

func _wait_for_sample(request_id: int) -> bool:
	for _frame in range(900):
		if _sample_results.has(request_id):
			return true
		if _sample_failures.has(request_id):
			return false
		await process_frame
	return false

func _wait_for_snapshot(request_id: int) -> bool:
	for _frame in range(3600):
		if _snapshot_results.has(request_id):
			return true
		if _snapshot_failures.has(request_id):
			_helpers.fail("G45 snapshot failed: %s" % str(_snapshot_failures[request_id]))
			return false
		await process_frame
	_helpers.fail("G45 snapshot request timed out")
	return false

func _chunk_for(point: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(point.x / 16.0)), 0, 127), 0, clamp(int(floor(point.z / 16.0)), 0, 127))

func _on_edit_failed(error: String) -> void:
	_edit_failures.push_back(error)

func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample

func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error

func _on_snapshot_ready(request_id: int, manifest_path: String, source_revision: int, world_revision: int, page_count: int) -> void:
	_snapshot_results[request_id] = {"manifest_path": manifest_path, "source_revision": source_revision, "world_revision": world_revision, "page_count": page_count}

func _on_snapshot_failed(request_id: int, error: String) -> void:
	_snapshot_failures[request_id] = error
