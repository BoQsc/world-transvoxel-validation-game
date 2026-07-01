extends SceneTree


const MARKER := "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_PASS"
const FIXTURE_ROOT := "res://build/production-lifecycle-fixture"
const ACTIVE_CHUNK_BUDGET := 40
const EXPECTED_PAGE_COUNT := 28
const EXPECTED_INITIAL_ACTIVE := 9
const EXPECTED_TWO_VIEWER_ACTIVE := 18
const MAXIMUM_LOD := 1 # Explicit maximum_lod contract for G54 mixed-LOD validation.
const BOUNDARY_EPSILON := 0.15
const BOUNDARY_MATCH_DISTANCE := 2.25
const MAX_BOUNDARY_Y_GAP := 0.75
const MAX_TRIANGLE_EDGE := 40.0
const MeshAudit := preload("res://tests/g54_lod_seam_artifact_audit.gd")


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var config: Resource = ClassDB.instantiate("WorldTransvoxelConfig")
	var terrain: Node = ClassDB.instantiate("WorldTransvoxelTerrain")
	if config == null or terrain == null:
		_fail("G54 runtime classes could not be instantiated")
		return
	_configure_runtime(config)
	if not config.call("is_valid"):
		_fail("G54 runtime configuration invalid: %s" % config.call("get_validation_error"))
		return
	root.add_child(terrain)
	terrain.set("configuration", config)
	if not terrain.call("start_world", FIXTURE_ROOT + "/transition.wtworld", FIXTURE_ROOT):
		_fail("G54 transition fixture startup was rejected: %s" % terrain.call("get_world_error"))
		return
	if not await _wait_for_state(terrain, "running"):
		_fail("G54 transition world did not reach running")
		return
	if int(terrain.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_fail("G54 transition page count mismatch: %s" % terrain.call("get_world_page_count"))
		return
	if not bool(terrain.call("update_viewer", 1, 1, Vector3(8, 8, 8), 1, MAXIMUM_LOD)):
		_fail("G54 mixed-LOD viewer update rejected")
		return
	if not await _wait_for_window(terrain, EXPECTED_INITIAL_ACTIVE, 1, "initial_mixed_lod"):
		return
	if not _is_ready_snapshot(terrain.call("query_chunk_state", Vector3i(1, 0, 0), 1)):
		_fail("G54 coarse transition bridge chunk is not fully ready")
		return
	if not _is_ready_snapshot(terrain.call("query_chunk_state", Vector3i(1, 0, 0), 0)):
		_fail("G54 fine seam-neighbor chunk is not fully ready")
		return
	var auditor := _make_auditor()
	var initial_audit := _audit_render_meshes(auditor, terrain, "initial")
	if initial_audit.is_empty():
		return
	var before_metrics: Dictionary = terrain.call("get_runtime_metrics")
	var before_transition_completions := int(before_metrics.get("transition_mesh_completions", 0))
	if before_transition_completions <= 0:
		_fail("G54 did not produce transition mesh completions before edit: %s" % str(before_metrics))
		return
	if not await _submit_seam_edit(terrain):
		return
	if not await _wait_for_window(terrain, EXPECTED_INITIAL_ACTIVE, 1, "after_seam_edit"):
		return
	var edited_audit := _audit_render_meshes(auditor, terrain, "after_edit")
	if edited_audit.is_empty():
		return
	var edit_metrics: Dictionary = terrain.call("get_runtime_metrics")
	if int(edit_metrics.get("edit_replacements", 0)) <= 0:
		_fail("G54 seam edit did not replace active mesh resources: %s" % str(edit_metrics))
		return
	if not bool(terrain.call("update_viewer", 2, 2, Vector3(80, 8, 8), 1, MAXIMUM_LOD)):
		_fail("G54 post-edit mixed-LOD topology update rejected")
		return
	if not await _wait_for_window(terrain, EXPECTED_TWO_VIEWER_ACTIVE, 2, "post_edit_topology_change"):
		return
	var post_topology_audit := _audit_render_meshes(auditor, terrain, "post_edit_topology_change")
	if post_topology_audit.is_empty():
		return
	var metrics: Dictionary = terrain.call("get_runtime_metrics")
	if int(metrics.get("transition_mesh_completions", 0)) <= before_transition_completions:
		_fail("G54 post-edit topology change did not remesh transition geometry: %s" % str(metrics))
		return
	if int(metrics.get("render_fading_resources", 0)) != 0 or int(metrics.get("pending_chunk_retirements", 0)) != 0:
		_fail("G54 edited LOD seam did not settle cleanly: %s" % str(metrics))
		return
	if not terrain.call("stop_world") or not await _wait_for_state(terrain, "stopped"):
		_fail("G54 transition world did not stop cleanly")
		return
	print("%s pages=%d active_records=%d render_resources=%d collision_resources=%d lod0=%d lod1=%d seam_pairs=%d edited_seam_pairs=%d diagonal_edges=%d edited_diagonal_edges=%d max_boundary_gap=%.4f edited_boundary_gap=%.4f transition_completions=%d edit_replacements=%d dense_world_files=0" % [
		MARKER,
		EXPECTED_PAGE_COUNT,
		int(metrics.get("active_chunk_records", 0)),
		int(metrics.get("render_resources", 0)),
		int(metrics.get("collision_resources", 0)),
		int(initial_audit.get("lod0", 0)),
		int(initial_audit.get("lod1", 0)),
		int(initial_audit.get("seam_pairs", 0)),
		int(post_topology_audit.get("seam_pairs", 0)),
		int(initial_audit.get("diagonal_edges", 0)),
		int(post_topology_audit.get("diagonal_edges", 0)),
		float(initial_audit.get("max_boundary_gap", 0.0)),
		max(float(edited_audit.get("max_boundary_gap", 0.0)), float(post_topology_audit.get("max_boundary_gap", 0.0))),
		int(metrics.get("transition_mesh_completions", 0)),
		int(metrics.get("edit_replacements", 0)),
	])
	terrain.queue_free()
	await process_frame
	quit(0)


func _configure_runtime(config: Resource) -> void:
	for key in [
		"active_chunk_capacity", "storage_request_capacity", "storage_completion_capacity",
		"encoded_page_entry_capacity", "decoded_page_entry_capacity", "mesh_entry_capacity",
		"render_entry_capacity", "collision_entry_capacity",
	]:
		config.set(key, ACTIVE_CHUNK_BUDGET)
	config.set("viewer_capacity", 2)
	config.set("demand_capacity_per_viewer", 125)
	config.set("render_apply_budget", 128)
	config.set("collision_apply_budget", 128)
	config.set("render_transition_frames", 0)


func _submit_seam_edit(terrain: Node) -> bool:
	var before_revision := int(terrain.call("get_world_revision"))
	var transaction: RefCounted = terrain.call("begin_edit_transaction", 54054)
	if transaction == null:
		_fail("G54 could not begin edit transaction: %s" % terrain.call("get_world_error"))
		return false
	if not bool(transaction.call("set_density_sphere", Vector3(32, 8, 8), 2.2, 1.0)):
		_fail("G54 seam edit command rejected: %s" % transaction.call("get_error"))
		return false
	if not bool(terrain.call("commit_edit_transaction", transaction)):
		_fail("G54 seam edit commit rejected: %s" % terrain.call("get_world_error"))
		return false
	for _frame in range(900):
		if int(terrain.call("get_world_revision")) >= before_revision + 1:
			return true
		await process_frame
	_fail("G54 seam edit did not commit")
	return false


func _make_auditor() -> RefCounted:
	var auditor: RefCounted = MeshAudit.new()
	auditor.set("boundary_epsilon", BOUNDARY_EPSILON)
	auditor.set("boundary_match_distance", BOUNDARY_MATCH_DISTANCE)
	auditor.set("max_boundary_y_gap", MAX_BOUNDARY_Y_GAP)
	auditor.set("max_triangle_edge", MAX_TRIANGLE_EDGE)
	return auditor


func _audit_render_meshes(auditor: RefCounted, terrain: Node, label: String) -> Dictionary:
	var result: Dictionary = auditor.call("audit_render_meshes", terrain, label)
	if result.is_empty():
		_fail(str(auditor.call("get_last_error")))
	return result


func _wait_for_state(terrain: Node, expected: String) -> bool:
	for _frame in range(900):
		if terrain.call("get_world_state_name") == expected:
			await process_frame
			return true
		await process_frame
	return false


func _wait_for_window(terrain: Node, expected_chunks: int, minimum_viewer_updates: int, label: String) -> bool:
	for _frame in range(1800):
		var metrics: Dictionary = terrain.call("get_runtime_metrics")
		var active_records := int(metrics.get("active_chunk_records", 0))
		if active_records == expected_chunks and int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and \
				int(metrics.get("render_resources", 0)) > 0 and int(metrics.get("collision_resources", 0)) > 0 and \
				int(metrics.get("queued_render", 0)) == 0 and int(metrics.get("queued_collision", 0)) == 0 and \
				int(metrics.get("fully_ready_chunk_records", -1)) == active_records and \
				int(metrics.get("pending_chunk_retirements", 0)) == 0 and int(metrics.get("render_fading_resources", 0)) == 0:
			return true
		await process_frame
	_fail("G54 window did not settle at %s expected=%d metrics=%s" % [label, expected_chunks, str(terrain.call("get_runtime_metrics"))])
	return false


func _is_ready_snapshot(snapshot: RefCounted) -> bool:
	return snapshot != null and snapshot.call("is_present") and snapshot.call("is_visual_ready") and snapshot.call("is_collision_ready") and snapshot.call("is_fully_ready")


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_FAIL: " + message)
	quit(1)
