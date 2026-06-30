extends SceneTree

const MARKER := "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const TELEMETRY_PATH := "res://artifacts/g49_debug_telemetry_ui_quality/debug_telemetry.json"
const EXPECTED_ACTIVE_RESOURCES := 25
const CATEGORIES := [
	"active_chunks",
	"queues",
	"frame_update",
	"edit_state",
	"material_state",
	"storage_state",
]
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

var _helpers: RefCounted

func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_FAIL")
	call_deferred("_run_test")

func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene):
		_helpers.fail("G49 scene did not become ready: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var overlay: Node = scene.get_node_or_null("ValidationDebugTelemetryOverlay")
	if terrain_world == null or overlay == null or not overlay.has_method("get_telemetry_summary"):
		_helpers.fail("G49 terrain world or debug telemetry overlay missing")
		return
	var edit_point: Vector3 = ProfileCatalog.edit_point(PROFILE_ID) + Vector3(13, 0, 0)
	if not await _helpers.wait_for_window(
			terrain_world, EXPECTED_ACTIVE_RESOURCES, "g49_initial_window",
			1, _chunk_for(edit_point), EXPECTED_ACTIVE_RESOURCES):
		return
	var before := await _settled_summary(overlay)
	if not _verify_summary(before, false):
		return
	var before_revision := int(terrain_world.call("get_world_revision"))
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if interactor == null or not bool(interactor.call("submit_sphere_edit", &"construct", edit_point, 1.8, 4, 1.0)):
		_helpers.fail("G49 public edit submission failed")
		return
	if not await _helpers.wait_for_revision(terrain_world, before_revision + 1):
		return
	if not await _helpers.wait_for_window(
			terrain_world, EXPECTED_ACTIVE_RESOURCES, "g49_after_edit",
			1, _chunk_for(edit_point), EXPECTED_ACTIVE_RESOURCES):
		return
	var after := await _settled_summary(overlay)
	if not _verify_summary(after, true):
		return
	if not bool(overlay.call("export_debug_telemetry", TELEMETRY_PATH)) or not FileAccess.file_exists(TELEMETRY_PATH):
		_helpers.fail("G49 telemetry export failed: %s" % TELEMETRY_PATH)
		return
	if not _helpers.assert_no_dense_files("g49_finish"):
		return
	var active := Dictionary(after.get("active_chunks", {}))
	var frame := Dictionary(after.get("frame_update", {}))
	var material := Dictionary(after.get("material_state", {}))
	print("%s profile=%s categories=%d overlay=1 exported=1 active_chunks=%d queued_render=%d queued_collision=%d frame_samples=%d edit_committed=1 materialized=%d storage_visible=1 dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		CATEGORIES.size(),
		int(active.get("active_chunk_records", 0)),
		int(Dictionary(after.get("queues", {})).get("queued_render", 0)),
		int(Dictionary(after.get("queues", {})).get("queued_collision", 0)),
		int(frame.get("frames", 0)),
		int(material.get("materialized_instances", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)

func _settled_summary(overlay: Node) -> Dictionary:
	for _frame in range(30):
		overlay.call("refresh_telemetry")
		await process_frame
	return Dictionary(overlay.call("get_telemetry_summary"))

func _verify_summary(summary: Dictionary, require_edit: bool) -> bool:
	if str(summary.get("implementation", "")) != "validation_debug_telemetry_overlay_v1":
		_helpers.fail("G49 implementation mismatch: %s" % str(summary))
		return false
	for category in CATEGORIES:
		if not Array(summary.get("categories", [])).has(category) or not summary.has(category):
			_helpers.fail("G49 missing telemetry category %s: %s" % [category, str(summary)])
			return false
	var active := Dictionary(summary.get("active_chunks", {}))
	var queues := Dictionary(summary.get("queues", {}))
	var frame := Dictionary(summary.get("frame_update", {}))
	var edit := Dictionary(summary.get("edit_state", {}))
	var material := Dictionary(summary.get("material_state", {}))
	var storage := Dictionary(summary.get("storage_state", {}))
	var text := str(root.get_node("ValidationPlaytest/ValidationDebugTelemetryOverlay").call("get_debug_text"))
	for header in ["[active_chunks]", "[queues]", "[frame_update]", "[edit_state]", "[material_state]", "[storage_state]"]:
		if not text.contains(header):
			_helpers.fail("G49 overlay text missing header %s: %s" % [header, text])
			return false
	if int(active.get("active_chunk_records", 0)) != EXPECTED_ACTIVE_RESOURCES:
		_helpers.fail("G49 active chunk telemetry mismatch: %s" % str(active))
		return false
	if int(queues.get("queued_render", -1)) != 0 or int(queues.get("queued_collision", -1)) != 0:
		_helpers.fail("G49 queue telemetry not settled: %s" % str(queues))
		return false
	if int(frame.get("frames", 0)) < 10 or float(frame.get("max_frame_ms", 0.0)) <= 0.0:
		_helpers.fail("G49 frame telemetry missing samples: %s" % str(frame))
		return false
	if require_edit and int(edit.get("edit_replacements", 0)) <= 0:
		_helpers.fail("G49 edit telemetry did not observe replacement: %s" % str(edit))
		return false
	if int(material.get("materialized_instances", 0)) < EXPECTED_ACTIVE_RESOURCES:
		_helpers.fail("G49 material telemetry incomplete: %s" % str(material))
		return false
	if str(storage.get("profile_id", "")).is_empty() or int(storage.get("page_count", 0)) <= 0:
		_helpers.fail("G49 storage telemetry incomplete: %s" % str(storage))
		return false
	return true

func _chunk_for(point: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(point.x / 16.0)), 0, 127), 0, clamp(int(floor(point.z / 16.0)), 0, 127))
