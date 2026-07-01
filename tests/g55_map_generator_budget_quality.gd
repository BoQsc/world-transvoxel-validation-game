extends SceneTree


const MARKER := "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const MAX_LOAD_MS := 30000
const EXPECTED_PAGE_COUNT := 16384
const EXPECTED_RESOURCES := 25
const PROFILES := [
	&"g19_compact_2k_on_demand",
	&"g50_seeded_procedural_2k",
]
const FORBIDDEN_DENSE_FILES := [
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/world.wtworld",
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/streaming.wtworld",
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/procedural.wtseed",
	"res://build/g50-seeded-procedural/g50_seeded_procedural_2k/world.wtworld",
	"res://build/g50-seeded-procedural/g50_seeded_procedural_2k/streaming.wtworld",
	"res://build/g50-seeded-procedural/g50_seeded_procedural_2k/procedural.wtseed",
]
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	if not _assert_no_dense_files("before_start"):
		return
	var results: Array[Dictionary] = []
	for profile_id in PROFILES:
		var result := await _run_profile(profile_id)
		if result.is_empty():
			return
		results.append(result)
	if not _assert_no_dense_files("after_profiles"):
		return
	print("%s profiles=%d map_blocks=2048 pages=%d max_load_ms=%d max_render_resources=%d max_collision_resources=%d generator_modes=%s seeds=%s dense_world_files=0" % [
		MARKER,
		results.size(),
		EXPECTED_PAGE_COUNT,
		_max_int(results, "load_ms"),
		_max_int(results, "render_resources"),
		_max_int(results, "collision_resources"),
		_join_values(results, "source_mode"),
		_join_values(results, "seed"),
	])
	await process_frame
	quit(0)


func _run_profile(profile_id: StringName) -> Dictionary:
	var packed := load(SCENE_PATH)
	if packed == null:
		_helpers.fail("G55 validation playtest scene did not load")
		return {}
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	scene.set("player_driven_viewer_enabled", false)
	scene.configure_playtest_profile(profile_id)
	scene.set_camera_mode(&"first_person")
	var started_ms := Time.get_ticks_msec()
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G55 profile did not become playable: %s %s" % [str(profile_id), str(scene.get_validation_summary())])
		return {}
	var load_ms := Time.get_ticks_msec() - started_ms
	if load_ms > MAX_LOAD_MS:
		_helpers.fail("G55 load-to-play exceeded budget: %s load_ms=%d" % [str(profile_id), load_ms])
		return {}
	var terrain_world: Node = _helpers.terrain_world(scene)
	if terrain_world == null:
		_helpers.fail("G55 terrain world missing: %s" % str(profile_id))
		return {}
	var result := _verify_profile(profile_id, terrain_world, load_ms)
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference != null and reference.has_method("stop_reference_backend_world"):
		reference.call("stop_reference_backend_world")
	scene.queue_free()
	await process_frame
	return result


func _verify_profile(profile_id: StringName, terrain_world: Node, load_ms: int) -> Dictionary:
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var profiles: Dictionary = terrain_world.call("get_profile_summaries")
	var generation := Dictionary(profiles.get("generation", {}))
	if int(terrain_world.call("get_world_page_count")) != EXPECTED_PAGE_COUNT:
		_helpers.fail("G55 page count mismatch: %s count=%d" % [str(profile_id), int(terrain_world.call("get_world_page_count"))])
		return {}
	var source_mode := str(generation.get("source_mode", "")).to_lower()
	if source_mode != "deterministic_reference":
		_helpers.fail("G55 profile is not deterministic_reference: %s %s" % [str(profile_id), str(generation)])
		return {}
	for key in ["active_chunk_records", "render_resources", "collision_resources"]:
		if int(metrics.get(key, 0)) != EXPECTED_RESOURCES:
			_helpers.fail("G55 %s mismatch for %s: %s" % [key, str(profile_id), str(metrics)])
			return {}
	if int(metrics.get("queued_render", 0)) != 0 or int(metrics.get("queued_collision", 0)) != 0 or \
			int(metrics.get("pending_chunk_retirements", 0)) != 0 or int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G55 profile did not settle cleanly: %s %s" % [str(profile_id), str(metrics)])
		return {}
	return {
		"profile": str(profile_id),
		"load_ms": load_ms,
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
		"source_mode": source_mode,
		"seed": int(generation.get("seed", 0)),
	}


func _assert_no_dense_files(stage: String) -> bool:
	for path in FORBIDDEN_DENSE_FILES:
		if FileAccess.file_exists(path):
			_helpers.fail("G55 dense/procedural descriptor exists at %s: %s" % [stage, path])
			return false
	return true


func _max_int(results: Array[Dictionary], key: String) -> int:
	var value := 0
	for result in results:
		value = max(value, int(result.get(key, 0)))
	return value


func _join_values(results: Array[Dictionary], key: String) -> String:
	var values: Array[String] = []
	for result in results:
		values.append(str(result.get(key, "")))
	return ",".join(values)
