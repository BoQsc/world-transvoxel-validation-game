extends SceneTree

const MARKER := "WT_VALIDATION_G4_GODOT_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"

var committed_revisions: Array[int] = []
var edit_failures: Array[String] = []
var sample_results: Dictionary = {}
var sample_failures: Dictionary = {}


func _initialize() -> void:
	call_deferred("_run_test")


func _run_test() -> void:
	var packed := load(SCENE_PATH)
	if packed == null:
		_fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	root.add_child(scene)
	if not await _wait_for_ready(scene) or not await _wait_for_player_floor(scene):
		_fail("validation playtest did not become edit-ready")
		return
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if reference == null or interactor == null:
		_fail("G4 scene missing reference or interactor")
		return
	var terrain_world = reference.call("get_terrain_world")
	var backend = terrain_world.call("get_backend_terrain")
	backend.connect("edit_committed", _on_edit_committed)
	backend.connect("edit_failed", _on_edit_failed)
	backend.connect("authoritative_sample_ready", _on_sample_ready)
	backend.connect("authoritative_sample_failed", _on_sample_failed)
	var carve := await _submit_and_verify(
		interactor, terrain_world, backend, &"carve", Vector3(8, 8, 8), -1, 1.0
	)
	if carve.is_empty():
		return
	var place := await _submit_and_verify(
		interactor, terrain_world, backend, &"construct", Vector3(8, 8, 8), 4, -1.0
	)
	if place.is_empty():
		return
	print("%s carve_commit_frames=%d carve_settle_frames=%d place_commit_frames=%d place_settle_frames=%d replacements=%d" % [
		MARKER,
		int(carve.get("commit_frames", 0)),
		int(carve.get("settle_frames", 0)),
		int(place.get("commit_frames", 0)),
		int(place.get("settle_frames", 0)),
		int(place.get("edit_replacements", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _submit_and_verify(
	interactor: Node,
	terrain_world: Node,
	backend: Object,
	mode_name: StringName,
	center: Vector3,
	expected_material: int,
	expected_density: float
) -> Dictionary:
	committed_revisions.clear()
	edit_failures.clear()
	sample_results.clear()
	sample_failures.clear()
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var start_frame := Engine.get_physics_frames()
	if not bool(interactor.call("submit_sphere_edit", mode_name, center, 1.8, expected_material, 1.0)):
		_fail("edit submission failed: %s" % str(interactor.call("get_last_submission")))
		return {}
	var target_revision := before_revision + 1
	if not await _wait_for_commit(terrain_world, target_revision):
		_fail("edit did not commit revision %d" % target_revision)
		return {}
	var commit_frames := Engine.get_physics_frames() - start_frame
	var settle_start := Engine.get_physics_frames()
	var cold_idle := await _wait_for_cold_idle(terrain_world)
	if cold_idle.is_empty():
		_fail("edit did not settle to cold idle")
		return {}
	var sample := await _query_sample(backend, Vector3i(8, 8, 8))
	if sample == null:
		return {}
	if absf(float(sample.call("get_density")) - expected_density) > 0.001:
		_fail("edited density mismatch for %s" % str(mode_name))
		return {}
	if expected_material > 0 and int(sample.call("get_material")) != expected_material:
		_fail("edited material mismatch for %s" % str(mode_name))
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("edit_replacements", 0)) <= 0 or int(cold_idle.get("collision_resources", 0)) <= 0:
		_fail("edit did not preserve replacement/collision evidence: %s" % str(metrics))
		return {}
	if int(metrics.get("render_fading_resources", 0)) != 0:
		_fail("edit created render fade/blink resources: %s" % str(metrics))
		return {}
	return {
		"commit_frames": commit_frames,
		"settle_frames": Engine.get_physics_frames() - settle_start,
		"edit_replacements": int(metrics.get("edit_replacements", 0)),
	}


func _query_sample(backend: Object, point: Vector3i) -> RefCounted:
	var request_id := int(backend.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_fail("sample query failed at %s" % str(point))
		return null
	return sample_results[request_id]


func _wait_for_ready(scene: Node) -> bool:
	for _frame in range(900):
		if scene.has_method("get_validation_state") and scene.get_validation_state() == "ready":
			await process_frame
			return true
		await process_frame
	return false


func _wait_for_player_floor(scene: Node) -> bool:
	for _frame in range(120):
		var summary: Dictionary = scene.get_validation_summary()
		if bool(summary.get("player_on_floor", false)):
			return true
		await physics_frame
	return false


func _wait_for_commit(terrain_world: Node, revision: int) -> bool:
	for _frame in range(900):
		if committed_revisions.has(revision) and int(terrain_world.call("get_backend_world_revision")) == revision:
			return true
		if not edit_failures.is_empty():
			return false
		await process_frame
	return false


func _wait_for_cold_idle(terrain_world: Node) -> Dictionary:
	for _frame in range(900):
		var summary: Dictionary = terrain_world.call("get_cold_idle_summary")
		if bool(summary.get("cold_idle", false)):
			await process_frame
			return summary
		await process_frame
	return {}


func _wait_for_sample(request_id: int) -> bool:
	for _frame in range(900):
		if sample_results.has(request_id):
			return true
		if sample_failures.has(request_id):
			return false
		await process_frame
	return false


func _on_edit_committed(world_revision: int) -> void:
	committed_revisions.push_back(world_revision)


func _on_edit_failed(error: String) -> void:
	edit_failures.push_back(error)


func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	sample_results[request_id] = sample


func _on_sample_failed(request_id: int, error: String) -> void:
	sample_failures[request_id] = error


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G4_GODOT_FAIL: " + message)
	quit(1)
