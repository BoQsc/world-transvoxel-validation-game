extends SceneTree


const MARKER := "WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const JOURNAL_PATH := "res://build/g19-compact-on-demand/g19_compact_2k_on_demand/world.wtedit"
const MAX_ACTIVE_RESOURCES := 25
const MAX_COMMIT_FRAMES := 180
const MAX_SETTLE_FRAMES := 300
const MAX_COMMIT_MS := 3000
const MAX_SETTLE_MS := 5000
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

var _helpers: RefCounted
var _committed_revisions: Array[int] = []
var _edit_failures: Array[String] = []
var _sample_results: Dictionary = {}
var _sample_failures: Dictionary = {}


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	if FileAccess.file_exists(JOURNAL_PATH):
		_helpers.fail("G34 must start from a clean edit journal")
		return
	var scene := await _load_ready_scene("edit_pass")
	if scene == null:
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null:
		_helpers.fail("G34 backend missing")
		return
	_connect_backend(backend)
	var edit_point: Vector3 = ProfileCatalog.edit_point(PROFILE_ID)
	var carve := await _submit_and_verify(scene, terrain_world, backend, &"carve", edit_point, -1, 1.0)
	if carve.is_empty():
		return
	var place_point := edit_point + Vector3(4, 0, 0)
	var construct := await _submit_and_verify(scene, terrain_world, backend, &"construct", place_point, 4, -1.0)
	if construct.is_empty():
		return
	var journal_bytes := _assert_journal()
	if journal_bytes <= 0:
		return
	scene.queue_free()
	await process_frame
	var replay_scene := await _load_ready_scene("replay_pass")
	if replay_scene == null:
		return
	var replay_world: Node = _helpers.terrain_world(replay_scene)
	var replay_backend: Node = replay_world.call("get_backend_terrain") if replay_world != null else null
	if replay_backend == null:
		_helpers.fail("G34 replay backend missing")
		return
	_connect_backend(replay_backend)
	if not await _verify_replayed_sample(replay_backend, Vector3i(edit_point), 1.0, -1):
		return
	if not await _verify_replayed_sample(replay_backend, Vector3i(place_point), -1.0, 4):
		return
	var final_metrics: Dictionary = replay_world.call("get_runtime_metrics")
	if int(final_metrics.get("render_fading_resources", 0)) != 0 or \
			int(final_metrics.get("pending_chunk_retirements", 0)) != 0:
		_helpers.fail("G34 replay scene did not settle cleanly: %s" % str(final_metrics))
		return
	var max_commit_frames = max(int(carve["commit_frames"]), int(construct["commit_frames"]))
	var max_settle_frames = max(int(carve["settle_frames"]), int(construct["settle_frames"]))
	var max_commit_ms = max(int(carve["commit_ms"]), int(construct["commit_ms"]))
	var max_settle_ms = max(int(carve["settle_ms"]), int(construct["settle_ms"]))
	print("%s profile=%s edits=2 replayed=2 max_commit_frames=%d max_settle_frames=%d max_commit_ms=%d max_settle_ms=%d journal_bytes=%d max_render_resources=%d max_collision_resources=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		max_commit_frames,
		max_settle_frames,
		max_commit_ms,
		max_settle_ms,
		journal_bytes,
		int(final_metrics.get("render_resources", 0)),
		int(final_metrics.get("collision_resources", 0)),
	])
	replay_scene.queue_free()
	await process_frame
	quit(0)


func _load_ready_scene(label: String) -> Node:
	var packed := load(SCENE_PATH)
	if packed == null:
		_helpers.fail("G34 scene did not load: %s" % label)
		return null
	var scene = packed.instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G34 scene did not become playable: %s %s" % [label, str(scene.get_validation_summary())])
		return null
	var terrain_world: Node = _helpers.terrain_world(scene)
	if terrain_world == null:
		_helpers.fail("G34 terrain world missing: %s" % label)
		return null
	if not await _helpers.wait_for_window(
		terrain_world,
		MAX_ACTIVE_RESOURCES,
		label,
		0,
		Vector3i(64, 0, 64),
		MAX_ACTIVE_RESOURCES
	):
		return null
	return scene


func _submit_and_verify(
	scene: Node,
	terrain_world: Node,
	backend: Node,
	mode_name: StringName,
	center: Vector3,
	expected_material: int,
	expected_density: float
) -> Dictionary:
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if interactor == null:
		_helpers.fail("G34 terrain interactor missing")
		return {}
	_committed_revisions.clear()
	_edit_failures.clear()
	_sample_results.clear()
	_sample_failures.clear()
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var start_frame := Engine.get_physics_frames()
	var start_ms := Time.get_ticks_msec()
	if not bool(interactor.call("submit_sphere_edit", mode_name, center, 1.8, expected_material, 1.0)):
		_helpers.fail("G34 edit submission failed: %s" % str(interactor.call("get_last_submission")))
		return {}
	var target_revision := before_revision + 1
	if not await _wait_for_commit(terrain_world, target_revision):
		_helpers.fail("G34 edit did not commit revision %d" % target_revision)
		return {}
	var commit_frames := Engine.get_physics_frames() - start_frame
	var commit_ms := Time.get_ticks_msec() - start_ms
	var settle_frame := Engine.get_physics_frames()
	var settle_ms_start := Time.get_ticks_msec()
	var cold_idle: bool = await _helpers.wait_for_window(
		terrain_world,
		MAX_ACTIVE_RESOURCES,
		"after_%s" % str(mode_name),
		int(before_metrics.get("viewer_updates", 0)),
		Vector3i(clamp(int(floor(center.x / 16.0)), 0, 127), 0, clamp(int(floor(center.z / 16.0)), 0, 127)),
		MAX_ACTIVE_RESOURCES
	)
	if not cold_idle:
		return {}
	var settle_frames := Engine.get_physics_frames() - settle_frame
	var settle_ms := Time.get_ticks_msec() - settle_ms_start
	if commit_frames > MAX_COMMIT_FRAMES or settle_frames > MAX_SETTLE_FRAMES or \
			commit_ms > MAX_COMMIT_MS or settle_ms > MAX_SETTLE_MS:
		_helpers.fail("G34 edit latency exceeded budget: commit=%df/%dms settle=%df/%dms" % [
			commit_frames, commit_ms, settle_frames, settle_ms,
		])
		return {}
	if not await _verify_replayed_sample(backend, Vector3i(center), expected_density, expected_material):
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("edit_replacements", 0)) <= int(before_metrics.get("edit_replacements", 0)) or \
			int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G34 edit replacement/fade metrics invalid: %s" % str(metrics))
		return {}
	return {
		"commit_frames": commit_frames,
		"settle_frames": settle_frames,
		"commit_ms": commit_ms,
		"settle_ms": settle_ms,
	}


func _verify_replayed_sample(backend: Node, point: Vector3i, expected_density: float, expected_material: int) -> bool:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(backend.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_helpers.fail("G34 authoritative sample query failed at %s" % str(point))
		return false
	var sample: RefCounted = _sample_results[request_id]
	if absf(float(sample.call("get_density")) - expected_density) > 0.001:
		_helpers.fail("G34 density mismatch at %s: %.4f" % [str(point), float(sample.call("get_density"))])
		return false
	if expected_material > 0 and int(sample.call("get_material")) != expected_material:
		_helpers.fail("G34 material mismatch at %s: %d" % [str(point), int(sample.call("get_material"))])
		return false
	return true


func _assert_journal() -> int:
	if not FileAccess.file_exists(JOURNAL_PATH):
		_helpers.fail("G34 edit journal was not created")
		return 0
	var absolute_path := ProjectSettings.globalize_path(JOURNAL_PATH)
	var bytes := FileAccess.get_file_as_bytes(absolute_path).size()
	if bytes < 128 or bytes > 1024 * 1024:
		_helpers.fail("G34 edit journal size outside quality bounds: %d" % bytes)
		return 0
	return bytes


func _connect_backend(backend: Node) -> void:
	if not backend.edit_committed.is_connected(_on_edit_committed):
		backend.connect("edit_committed", _on_edit_committed)
	if not backend.edit_failed.is_connected(_on_edit_failed):
		backend.connect("edit_failed", _on_edit_failed)
	if not backend.authoritative_sample_ready.is_connected(_on_sample_ready):
		backend.connect("authoritative_sample_ready", _on_sample_ready)
	if not backend.authoritative_sample_failed.is_connected(_on_sample_failed):
		backend.connect("authoritative_sample_failed", _on_sample_failed)


func _wait_for_commit(terrain_world: Node, revision: int) -> bool:
	for _frame in range(900):
		if _committed_revisions.has(revision) and int(terrain_world.call("get_backend_world_revision")) >= revision:
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


func _on_edit_committed(world_revision: int) -> void:
	_committed_revisions.push_back(world_revision)


func _on_edit_failed(error: String) -> void:
	_edit_failures.push_back(error)


func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample


func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error
