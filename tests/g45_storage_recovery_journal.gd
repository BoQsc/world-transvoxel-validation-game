extends SceneTree

const MARKER := "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_JOURNAL_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const JOURNAL_PATH := "res://build/g19-compact-on-demand/g19_compact_2k_on_demand/world.wtedit"
const EXPECTED_SOURCE_REVISION := 190019
const EXPECTED_ACTIVE_RESOURCES := 25
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ReferenceScene := preload("res://addons/world_transvoxel_terrain/debug/wt_terrain_reference_scene.tscn")
const EditOperation := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_operation.gd")
const EditBatch := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_batch.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

var _helpers: RefCounted
var _sample_results: Dictionary = {}
var _sample_failures: Dictionary = {}
var _edit_failures: Array[String] = []

func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_JOURNAL_FAIL")
	call_deferred("_run_test")

func _run_test() -> void:
	if FileAccess.file_exists(JOURNAL_PATH):
		_helpers.fail("G45 journal phase must start from a clean edit journal")
		return
	var reference := await _start_reference("g45_compact_2k_initial")
	if reference == null:
		return
	var terrain_world: Node = reference.call("get_terrain_world")
	var backend: Node = terrain_world.call("get_backend_terrain")
	_connect_backend(backend)
	if not _verify_storage_profile(terrain_world):
		return
	var edits := [
		{"point": Vector3(1032, 8, 1032), "mode": &"carve", "material": -1, "density": 1.0},
		{"point": Vector3(1037, 8, 1032), "mode": &"construct", "material": 4, "density": -1.0},
		{"point": Vector3(1042, 8, 1032), "mode": &"carve", "material": -1, "density": 1.0},
	]
	for edit in edits:
		if not await _submit_edit_and_verify(terrain_world, backend, edit):
			return
	var journal := _assert_wtedit_journal()
	if journal.is_empty():
		return
	reference.queue_free()
	await process_frame
	var corrupted_size := _append_truncated_wtedit_tail()
	if corrupted_size <= int(journal["bytes"]):
		_helpers.fail("G45 failed to append truncated journal tail")
		return
	var recovered := await _start_reference("g45_compact_2k_recovered")
	if recovered == null:
		return
	var recovered_world: Node = recovered.call("get_terrain_world")
	var recovered_backend: Node = recovered_world.call("get_backend_terrain")
	_connect_backend(recovered_backend)
	var recovered_bytes := _journal_size()
	if recovered_bytes != int(journal["bytes"]):
		_helpers.fail("G45 journal recovery did not truncate tail: before=%d corrupted=%d recovered=%d" % [int(journal["bytes"]), corrupted_size, recovered_bytes])
		return
	var replayed := 0
	for edit in edits:
		if not await _verify_sample(recovered_backend, Vector3i(edit["point"]), float(edit["density"]), int(edit["material"])):
			return
		replayed += 1
	var metrics: Dictionary = recovered_world.call("get_runtime_metrics")
	if not _helpers.assert_no_dense_files("g45_journal_finish"):
		return
	print("%s profile=%s compact_2k_edits=%d compact_2k_replayed=%d compact_2k_recovered=%d journal_magic=%s journal_format_version=%d journal_source_revision=%d journal_bytes=%d truncated_tail_bytes=%d recovery_truncated_to_bytes=%d render_resources=%d collision_resources=%d active_records=%d dense_world_files=0" % [
		MARKER, str(PROFILE_ID), edits.size(), replayed, replayed, str(journal["magic"]),
		int(journal["format_major"]), int(journal["source_revision"]), int(journal["bytes"]),
		corrupted_size - int(journal["bytes"]), recovered_bytes,
		int(metrics.get("render_resources", 0)), int(metrics.get("collision_resources", 0)),
		int(metrics.get("active_chunk_records", 0)),
	])
	recovered.queue_free()
	await process_frame
	quit(0)

func _start_reference(label: String) -> Node:
	var reference = ReferenceScene.instantiate()
	root.add_child(reference)
	await process_frame
	reference.call("ensure_reference_defaults")
	var terrain_world: Node = reference.call("get_terrain_world")
	terrain_world.set("generation_profile", ProfileCatalog.generation_profile(PROFILE_ID))
	terrain_world.set("storage_profile", ProfileCatalog.storage_profile(PROFILE_ID))
	if not bool(reference.call("start_reference_backend_world")):
		_helpers.fail("G45 failed to start reference world %s: %s" % [label, str(terrain_world.call("get_last_error"))])
		return null
	if not await _wait_for_running(terrain_world, label):
		return null
	var viewer_position: Vector3 = ProfileCatalog.viewer_positions(PROFILE_ID)[0]
	if not bool(reference.call("update_reference_viewer", 1, 1, viewer_position, 2, 0)):
		_helpers.fail("G45 viewer update failed")
		return null
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, label, 1, _chunk_for(viewer_position), EXPECTED_ACTIVE_RESOURCES):
		return null
	return reference

func _submit_edit_and_verify(terrain_world: Node, backend: Node, edit: Dictionary) -> bool:
	_edit_failures.clear()
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var batch = EditBatch.new()
	var operation = EditOperation.new()
	operation.mode = EditOperation.Mode.CONSTRUCT if edit["mode"] == &"construct" else EditOperation.Mode.CARVE
	operation.brush_shape = EditOperation.BrushShape.SPHERE
	operation.center = edit["point"]
	operation.radius = 1.8
	operation.material_id = max(1, int(edit["material"]))
	operation.density_value = 1.0
	if not batch.add_operation(operation) or not bool(terrain_world.call("submit_edit_batch", batch, 45045)):
		_helpers.fail("G45 edit submission failed: %s" % str(terrain_world.call("get_last_error")))
		return false
	if not await _wait_for_revision_or_failure(terrain_world, before_revision + 1):
		_helpers.fail("G45 edit did not commit: %s" % str(edit))
		return false
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, "g45_after_edit", 0, _chunk_for(edit["point"]), EXPECTED_ACTIVE_RESOURCES):
		return false
	return await _verify_sample(backend, Vector3i(edit["point"]), float(edit["density"]), int(edit["material"]))

func _verify_storage_profile(terrain_world: Node) -> bool:
	var storage: Resource = terrain_world.get("storage_profile")
	var summary := Dictionary(storage.call("get_contract_summary")) if storage != null and storage.has_method("get_contract_summary") else {}
	if str(summary.get("profile_id", "")) != str(PROFILE_ID) or not str(summary.get("world_manifest_path", "")).ends_with("procedural.wtseed") or int(summary.get("journal_format_version", 0)) != 1 or not bool(summary.get("persist_edits", false)):
		_helpers.fail("G45 storage profile contract mismatch: %s" % str(summary))
		return false
	return true

func _assert_wtedit_journal() -> Dictionary:
	if not FileAccess.file_exists(JOURNAL_PATH):
		_helpers.fail("G45 edit journal missing")
		return {}
	var bytes := FileAccess.get_file_as_bytes(ProjectSettings.globalize_path(JOURNAL_PATH))
	var magic := "WTEDIT" if _has_wtedit_magic(bytes) else "invalid"
	var major := _u16_le(bytes, 8)
	var minor := _u16_le(bytes, 10)
	var source_revision := _u64_le(bytes, 24)
	if bytes.size() < 128 or bytes.size() > 4 * 1024 * 1024 or magic != "WTEDIT" or major != 1 or minor != 0 or _u32_le(bytes, 12) != 80 or source_revision != EXPECTED_SOURCE_REVISION:
		_helpers.fail("G45 WTEDIT header mismatch magic=%s major=%d minor=%d source=%d bytes=%d" % [magic, major, minor, source_revision, bytes.size()])
		return {}
	return {"magic": magic, "format_major": major, "source_revision": source_revision, "bytes": bytes.size()}

func _append_truncated_wtedit_tail() -> int:
	var file := FileAccess.open(ProjectSettings.globalize_path(JOURNAL_PATH), FileAccess.READ_WRITE)
	if file == null:
		_helpers.fail("G45 could not open journal for interrupted-write simulation")
		return 0
	file.seek_end()
	file.store_buffer(PackedByteArray([87, 84, 69, 68, 73, 84, 0, 0, 1, 0, 0, 0]))
	file.flush()
	file.close()
	return _journal_size()

func _verify_sample(backend: Node, point: Vector3i, expected_density: float, expected_material: int) -> bool:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(backend.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_helpers.fail("G45 authoritative sample query failed at %s" % str(point))
		return false
	var sample: RefCounted = _sample_results[request_id]
	if absf(float(sample.call("get_density")) - expected_density) > 0.001:
		_helpers.fail("G45 density mismatch at %s" % str(point))
		return false
	if expected_material > 0 and int(sample.call("get_material")) != expected_material:
		_helpers.fail("G45 material mismatch at %s" % str(point))
		return false
	return true

func _connect_backend(backend: Node) -> void:
	if not backend.edit_failed.is_connected(_on_edit_failed):
		backend.connect("edit_failed", _on_edit_failed)
	if not backend.authoritative_sample_ready.is_connected(_on_sample_ready):
		backend.connect("authoritative_sample_ready", _on_sample_ready)
	if not backend.authoritative_sample_failed.is_connected(_on_sample_failed):
		backend.connect("authoritative_sample_failed", _on_sample_failed)

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

func _journal_size() -> int:
	return FileAccess.get_file_as_bytes(ProjectSettings.globalize_path(JOURNAL_PATH)).size()

func _chunk_for(point: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(point.x / 16.0)), 0, 127), 0, clamp(int(floor(point.z / 16.0)), 0, 127))

func _u16_le(bytes: PackedByteArray, offset: int) -> int:
	return int(bytes[offset]) | (int(bytes[offset + 1]) << 8)

func _u32_le(bytes: PackedByteArray, offset: int) -> int:
	return int(bytes[offset]) | (int(bytes[offset + 1]) << 8) | (int(bytes[offset + 2]) << 16) | (int(bytes[offset + 3]) << 24)

func _u64_le(bytes: PackedByteArray, offset: int) -> int:
	var value := 0
	for index in range(8):
		value |= int(bytes[offset + index]) << (index * 8)
	return value

func _has_wtedit_magic(bytes: PackedByteArray) -> bool:
	return bytes.size() >= 8 and int(bytes[0]) == 87 and int(bytes[1]) == 84 and int(bytes[2]) == 69 and int(bytes[3]) == 68 and int(bytes[4]) == 73 and int(bytes[5]) == 84 and int(bytes[6]) == 0 and int(bytes[7]) == 0

func _on_edit_failed(error: String) -> void:
	_edit_failures.push_back(error)

func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample

func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error
