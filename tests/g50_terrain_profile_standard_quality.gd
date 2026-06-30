extends SceneTree

const MARKER := "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const MAX_LOAD_MS := 30000
const EXPECTED_PROCEDURAL_PAGE_COUNT := 16384
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")
const ProfileStandard := preload("res://scripts/validation_profile_standard_contract.gd")
const FORBIDDEN_DENSE_FILES := [
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/world.wtworld",
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/streaming.wtworld",
	"res://build/g19-compact-on-demand/g19_compact_2k_on_demand/procedural.wtseed",
	"res://build/g50-seeded-procedural/g50_seeded_procedural_2k/world.wtworld",
	"res://build/g50-seeded-procedural/g50_seeded_procedural_2k/streaming.wtworld",
	"res://build/g50-seeded-procedural/g50_seeded_procedural_2k/procedural.wtseed",
]

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var contract := ProfileStandard.get_standard_summary()
	var errors := ProfileStandard.validate_standard_summary(contract)
	if not errors.is_empty():
		_helpers.fail("G50 profile standard contract failed: %s" % str(errors))
		return
	if ProfileStandard.get_standard_summary().get("determinism_key", "") != contract.get("determinism_key", ""):
		_helpers.fail("G50 profile standard determinism key changed between reads")
		return
	if not _assert_no_dense_files("before_start"):
		return
	var results: Array[Dictionary] = []
	for profile_id in ProfileStandard.standard_profile_ids():
		var result := await _run_profile(profile_id)
		if result.is_empty():
			return
		results.append(result)
	if not _assert_no_dense_files("after_profiles"):
		return
	print("%s profiles=%d runtime_profiles=%d deterministic=%d budgets=%d flat_resources=%d mountain_resources=%d compact_resources=%d seeded_resources=%d compact_seed=19019 seeded_seed=50050 max_profile_load_ms=%d dense_world_files=0" % [
		MARKER,
		int(contract.get("profile_count", 0)),
		results.size(),
		int(contract.get("deterministic_profiles", 0)),
		int(contract.get("budgeted_profiles", 0)),
		int(results[0].get("active_resources", 0)),
		int(results[1].get("active_resources", 0)),
		int(results[2].get("active_resources", 0)),
		int(results[3].get("active_resources", 0)),
		_max_load_ms(results),
	])
	await process_frame
	quit(0)


func _run_profile(profile_id: StringName) -> Dictionary:
	var packed := load(SCENE_PATH)
	if packed == null:
		_helpers.fail("G50 validation playtest scene did not load")
		return {}
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	scene.set("player_driven_viewer_enabled", false)
	scene.configure_playtest_profile(profile_id)
	scene.set_camera_mode(&"first_person")
	var started_ms := Time.get_ticks_msec()
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene):
		_helpers.fail("G50 profile did not become ready: %s %s" % [
			str(profile_id),
			str(scene.get_validation_summary()),
		])
		return {}
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G50 player did not settle on floor: %s %s" % [
			str(profile_id),
			str(scene.get_validation_summary()),
		])
		return {}
	var load_ms := Time.get_ticks_msec() - started_ms
	if load_ms > MAX_LOAD_MS:
		_helpers.fail("G50 profile load budget exceeded: %s load_ms=%d" % [str(profile_id), load_ms])
		return {}
	var summary: Dictionary = scene.get_validation_summary()
	var terrain_world: Node = _helpers.terrain_world(scene)
	if terrain_world == null:
		_helpers.fail("G50 terrain world missing for %s" % str(profile_id))
		return {}
	if not _verify_runtime_profile(profile_id, summary, terrain_world):
		return {}
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var active := int(metrics.get("active_chunk_records", 0))
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	if reference != null and reference.has_method("stop_reference_backend_world"):
		reference.call("stop_reference_backend_world")
	scene.queue_free()
	await process_frame
	return {
		"profile": str(profile_id),
		"load_ms": load_ms,
		"active_resources": active,
	}


func _verify_runtime_profile(profile_id: StringName, summary: Dictionary, terrain_world: Node) -> bool:
	var expected := ProfileCatalog.expected_resource_count(profile_id)
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var cold_idle: Dictionary = terrain_world.call("get_cold_idle_summary")
	if str(summary.get("playtest_profile_id", "")) != str(profile_id):
		_helpers.fail("G50 summary profile mismatch: %s" % str(summary))
		return false
	if int(summary.get("expected_resource_count", 0)) != expected:
		_helpers.fail("G50 expected resource summary mismatch: %s" % str(summary))
		return false
	for key in ["active_chunk_records", "render_resources", "collision_resources"]:
		if int(metrics.get(key, 0)) != expected:
			_helpers.fail("G50 %s mismatch for %s: %s" % [key, str(profile_id), str(metrics)])
			return false
	if not bool(cold_idle.get("cold_idle", false)):
		_helpers.fail("G50 profile is not cold idle: %s %s" % [str(profile_id), str(cold_idle)])
		return false
	if int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G50 profile has render fade blink resources: %s %s" % [str(profile_id), str(metrics)])
		return false
	if _is_procedural(profile_id) and int(terrain_world.call("get_world_page_count")) != EXPECTED_PROCEDURAL_PAGE_COUNT:
		_helpers.fail("G50 procedural page count mismatch: %s count=%d" % [
			str(profile_id),
			int(terrain_world.call("get_world_page_count")),
		])
		return false
	var profiles: Dictionary = terrain_world.call("get_profile_summaries")
	var generation := Dictionary(profiles.get("generation", {}))
	var expected_standard := ProfileStandard.profile_standard(profile_id)
	if str(generation.get("source_mode", "")) != str(expected_standard.get("source_mode", "")):
		_helpers.fail("G50 source mode mismatch: %s %s" % [str(profile_id), str(generation)])
		return false
	if int(generation.get("seed", 0)) != int(expected_standard.get("seed", 0)):
		_helpers.fail("G50 seed mismatch: %s %s" % [str(profile_id), str(generation)])
		return false
	return true


func _assert_no_dense_files(stage: String) -> bool:
	for path in FORBIDDEN_DENSE_FILES:
		if FileAccess.file_exists(path):
			_helpers.fail("G50 dense/procedural descriptor file exists at %s: %s" % [stage, path])
			return false
	return true


func _is_procedural(profile_id: StringName) -> bool:
	return str(profile_id) in ["g19_compact_2k_on_demand", "g50_seeded_procedural_2k"]


func _max_load_ms(results: Array[Dictionary]) -> int:
	var result := 0
	for profile in results:
		result = max(result, int(profile.get("load_ms", 0)))
	return result
