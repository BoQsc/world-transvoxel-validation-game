extends SceneTree


const MARKER := "WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const JOURNAL_PATH := "res://build/g19-compact-on-demand/g19_compact_2k_on_demand/world.wtedit"
const EXPECTED_PAGE_COUNT := 16384
const EXPECTED_ACTIVE_RESOURCES := 25
const EDIT_SITES := 4
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

const EDITS := [
	{"label": "northwest_carve", "point": Vector3(264, 8, 264), "mode": &"carve", "material": -1, "density": 1.0},
	{"label": "northeast_construct", "point": Vector3(1784, 8, 264), "mode": &"construct", "material": 4, "density": -1.0},
	{"label": "southeast_carve", "point": Vector3(1784, 8, 1784), "mode": &"carve", "material": -1, "density": 1.0},
	{"label": "southwest_construct", "point": Vector3(264, 8, 1784), "mode": &"construct", "material": 4, "density": -1.0},
]

var _helpers: RefCounted
var _sample_results := {}
var _sample_failures := {}
var _edit_failures: Array[String] = []


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	if FileAccess.file_exists(JOURNAL_PATH):
		_helpers.fail("G39 must start from a clean edit journal")
		return
	var scene := await _load_scene("edit_pass")
	if scene == null:
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain")
	_connect_backend(backend)
	var max_commit_frames := 0
	var max_settle_frames := 0
	var max_render_resources := 0
	var max_collision_resources := 0
	for edit in EDITS:
		var result := await _stream_edit_and_verify(scene, terrain_world, backend, edit)
		if result.is_empty():
			return
		max_commit_frames = max(max_commit_frames, int(result.get("commit_frames", 0)))
		max_settle_frames = max(max_settle_frames, int(result.get("settle_frames", 0)))
		max_render_resources = max(max_render_resources, int(result.get("render_resources", 0)))
		max_collision_resources = max(max_collision_resources, int(result.get("collision_resources", 0)))
	var journal_bytes := _assert_journal()
	if journal_bytes <= 0:
		return
	scene.queue_free()
	await process_frame
	var replay_scene := await _load_scene("replay_pass")
	if replay_scene == null:
		return
	var replay_world: Node = _helpers.terrain_world(replay_scene)
	var replay_backend: Node = replay_world.call("get_backend_terrain")
	_connect_backend(replay_backend)
	var replayed := 0
	for edit in EDITS:
		if not await _verify_sample(replay_backend, Vector3i(edit["point"]), float(edit["density"]), int(edit["material"])):
			return
		replayed += 1
	var final_metrics: Dictionary = replay_world.call("get_runtime_metrics")
	var final_cold: Dictionary = replay_world.call("get_cold_idle_summary")
	if not bool(final_cold.get("cold_idle", false)) or \
			int(final_metrics.get("render_resources", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			int(final_metrics.get("collision_resources", 0)) != EXPECTED_ACTIVE_RESOURCES or \
			int(final_metrics.get("render_fading_resources", 0)) != 0 or \
			int(final_metrics.get("pending_chunk_retirements", 0)) != 0:
		_helpers.fail("G39 final replay scene not cold idle: metrics=%s cold=%s" % [str(final_metrics), str(final_cold)])
		return
	if not _helpers.assert_no_dense_files("g39_finish"):
		return
	print("%s profile=%s edit_sites=%d replayed=%d max_commit_frames=%d max_settle_frames=%d journal_bytes=%d max_render_resources=%d max_collision_resources=%d final_render_resources=%d final_collision_resources=%d final_cold_idle=true dense_world_files=0" % [
		MARKER, str(PROFILE_ID), EDIT_SITES, replayed, max_commit_frames, max_settle_frames,
		journal_bytes, max_render_resources, max_collision_resources,
		int(final_metrics.get("render_resources", 0)), int(final_metrics.get("collision_resources", 0)),
	])
	replay_scene.queue_free()
	await process_frame
	quit(0)


func _load_scene(label: String) -> Node:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G39 scene did not become playable: %s %s" % [label, str(scene.get_validation_summary())])
		return null
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain") if terrain_world != null else null
	if backend == null or int(backend.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G39 backend page count mismatch: %s" % label)
		return null
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, label, 0, Vector3i(64, 0, 64), EXPECTED_ACTIVE_RESOURCES):
		return null
	return scene


func _stream_edit_and_verify(scene: Node, terrain_world: Node, backend: Node, edit: Dictionary) -> Dictionary:
	var point: Vector3 = edit["point"]
	var before_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not _helpers.move_player_to(scene, point):
		return {}
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, str(edit["label"]), int(before_metrics.get("viewer_updates", 0)) + 1, _chunk_for(point), EXPECTED_ACTIVE_RESOURCES):
		return {}
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G39 player did not settle before edit at %s" % str(edit["label"]))
		return {}
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	var before_replacements := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("edit_replacements", 0))
	var start_frame := Engine.get_physics_frames()
	if not bool(interactor.call("submit_sphere_edit", edit["mode"], point, 1.8, int(edit["material"]), 1.0)):
		_helpers.fail("G39 edit submission failed at %s: %s" % [str(edit["label"]), str(interactor.call("get_last_submission"))])
		return {}
	if not await _wait_for_revision(terrain_world, before_revision + 1):
		_helpers.fail("G39 edit did not commit at %s" % str(edit["label"]))
		return {}
	var commit_frames := Engine.get_physics_frames() - start_frame
	var settle_start := Engine.get_physics_frames()
	if not await _helpers.wait_for_window(terrain_world, EXPECTED_ACTIVE_RESOURCES, str(edit["label"]) + "_after_edit", int(before_metrics.get("viewer_updates", 0)), _chunk_for(point), EXPECTED_ACTIVE_RESOURCES):
		return {}
	var settle_frames := Engine.get_physics_frames() - settle_start
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("edit_replacements", 0)) <= before_replacements or int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G39 edit replacement/fade invalid at %s: %s" % [str(edit["label"]), str(metrics)])
		return {}
	if not await _verify_sample(backend, Vector3i(point), float(edit["density"]), int(edit["material"])):
		return {}
	return {"commit_frames": commit_frames, "settle_frames": settle_frames, "render_resources": int(metrics.get("render_resources", 0)), "collision_resources": int(metrics.get("collision_resources", 0))}


func _verify_sample(backend: Node, point: Vector3i, expected_density: float, expected_material: int) -> bool:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(backend.call("request_authoritative_sample", point, 0))
	if request_id <= 0 or not await _wait_for_sample(request_id):
		_helpers.fail("G39 authoritative sample query failed at %s" % str(point))
		return false
	var sample: RefCounted = _sample_results[request_id]
	if absf(float(sample.call("get_density")) - expected_density) > 0.001:
		_helpers.fail("G39 density mismatch at %s: %.4f" % [str(point), float(sample.call("get_density"))])
		return false
	if expected_material > 0 and int(sample.call("get_material")) != expected_material:
		_helpers.fail("G39 material mismatch at %s: %d" % [str(point), int(sample.call("get_material"))])
		return false
	return true


func _assert_journal() -> int:
	if not FileAccess.file_exists(JOURNAL_PATH):
		_helpers.fail("G39 edit journal was not created")
		return 0
	var bytes := FileAccess.get_file_as_bytes(ProjectSettings.globalize_path(JOURNAL_PATH)).size()
	if bytes < 256 or bytes > 1024 * 1024:
		_helpers.fail("G39 journal size outside bounds: %d" % bytes)
		return 0
	return bytes


func _connect_backend(backend: Node) -> void:
	_edit_failures.clear()
	if not backend.edit_failed.is_connected(_on_edit_failed):
		backend.connect("edit_failed", _on_edit_failed)
	if not backend.authoritative_sample_ready.is_connected(_on_sample_ready):
		backend.connect("authoritative_sample_ready", _on_sample_ready)
	if not backend.authoritative_sample_failed.is_connected(_on_sample_failed):
		backend.connect("authoritative_sample_failed", _on_sample_failed)


func _wait_for_revision(terrain_world: Node, revision: int) -> bool:
	for _frame in range(900):
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


func _on_edit_failed(error: String) -> void:
	_edit_failures.push_back(error)


func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample


func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))
