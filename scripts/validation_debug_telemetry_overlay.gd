extends CanvasLayer

const IMPLEMENTATION := "validation_debug_telemetry_overlay_v1"
const CATEGORY_ORDER := [
	"active_chunks",
	"queues",
	"frame_update",
	"edit_state",
	"material_state",
	"storage_state",
]
const CATEGORY_KEYS := {
	"active_chunks": [
		"active_chunk_records",
		"render_resources",
		"collision_resources",
		"fully_ready_chunk_records",
	],
	"queues": [
		"queued_render",
		"queued_collision",
		"pending_chunk_retirements",
		"render_fading_resources",
	],
	"frame_update": ["frames", "last_frame_ms", "avg_frame_ms", "max_frame_ms"],
	"edit_state": ["world_revision", "edit_commits", "edit_rejections", "edit_replacements"],
	"material_state": ["applied", "materialized_instances", "auto_apply_count", "profile_id"],
	"storage_state": ["profile_id", "world_manifest_path", "object_root_path", "page_count"],
}

var _summary: Dictionary = {}
var _label: Label
var _frames := 0
var _last_frame_ms := 0.0
var _total_frame_ms := 0.0
var _max_frame_ms := 0.0

func _ready() -> void:
	_build_overlay()
	refresh_telemetry()

func _process(delta: float) -> void:
	_record_frame(delta)
	refresh_telemetry()

func refresh_telemetry() -> Dictionary:
	_summary = _capture_summary()
	if _label != null:
		_label.text = format_telemetry(_summary)
	return get_telemetry_summary()

func get_telemetry_summary() -> Dictionary:
	return _summary.duplicate(true)

func get_debug_text() -> String:
	return format_telemetry(_summary)

func export_debug_telemetry(path: String) -> bool:
	var absolute := ProjectSettings.globalize_path(path)
	DirAccess.make_dir_recursive_absolute(absolute.get_base_dir())
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return false
	file.store_string(JSON.stringify(_summary, "\t"))
	file.store_string("\n")
	file.close()
	return true

func format_telemetry(summary: Dictionary) -> String:
	var lines := [
		"World Transvoxel Debug Telemetry",
		"implementation=%s" % str(summary.get("implementation", "")),
	]
	for category in CATEGORY_ORDER:
		lines.append("[%s]" % category)
		var data := Dictionary(summary.get(category, {}))
		for key in CATEGORY_KEYS.get(category, []):
			lines.append("%s=%s" % [key, str(data.get(key, "n/a"))])
	return "\n".join(lines)

func _build_overlay() -> void:
	name = "ValidationDebugTelemetryOverlay"
	var panel := PanelContainer.new()
	panel.name = "Panel"
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	panel.offset_left = -420.0
	panel.offset_top = 12.0
	panel.offset_right = -12.0
	panel.offset_bottom = 300.0
	add_child(panel)
	_label = Label.new()
	_label.name = "TelemetryLabel"
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	panel.add_child(_label)

func _capture_summary() -> Dictionary:
	var terrain := _terrain_world()
	var metrics := _runtime_metrics(terrain)
	var material := _material_summary()
	var storage := _storage_summary(terrain)
	return {
		"implementation": IMPLEMENTATION,
		"categories": CATEGORY_ORDER.duplicate(),
		"active_chunks": {
			"active_chunk_records": int(metrics.get("active_chunk_records", 0)),
			"render_resources": int(metrics.get("render_resources", 0)),
			"collision_resources": int(metrics.get("collision_resources", 0)),
			"fully_ready_chunk_records": int(metrics.get("fully_ready_chunk_records", 0)),
			"visual_ready_chunk_records": int(metrics.get("visual_ready_chunk_records", 0)),
		},
		"queues": {
			"queued_render": int(metrics.get("queued_render", 0)),
			"queued_collision": int(metrics.get("queued_collision", 0)),
			"pending_chunk_retirements": int(metrics.get("pending_chunk_retirements", 0)),
			"render_fading_resources": int(metrics.get("render_fading_resources", 0)),
		},
		"frame_update": {
			"frames": _frames,
			"last_frame_ms": _last_frame_ms,
			"avg_frame_ms": _total_frame_ms / float(max(1, _frames)),
			"max_frame_ms": _max_frame_ms,
		},
		"edit_state": {
			"world_revision": _world_revision(terrain),
			"edit_commits": int(metrics.get("edit_commits", 0)),
			"edit_rejections": int(metrics.get("edit_rejections", 0)),
			"edit_replacements": int(metrics.get("edit_replacements", 0)),
			"last_submission": _last_edit_submission(terrain),
		},
		"material_state": material,
		"storage_state": storage,
	}

func _record_frame(delta: float) -> void:
	_frames += 1
	_last_frame_ms = max(0.0, delta * 1000.0)
	_total_frame_ms += _last_frame_ms
	_max_frame_ms = max(_max_frame_ms, _last_frame_ms)

func _runtime_metrics(terrain: Node) -> Dictionary:
	if terrain != null and terrain.has_method("get_runtime_metrics"):
		return Dictionary(terrain.call("get_runtime_metrics"))
	return {}

func _storage_summary(terrain: Node) -> Dictionary:
	var summaries := {}
	if terrain != null and terrain.has_method("get_profile_summaries"):
		summaries = Dictionary(terrain.call("get_profile_summaries"))
	var storage := Dictionary(summaries.get("storage", {}))
	storage["page_count"] = _world_page_count(terrain)
	storage["source_revision"] = _world_source_revision(terrain)
	return storage

func _material_summary() -> Dictionary:
	var materializer := _materializer()
	if materializer != null and materializer.has_method("get_material_summary"):
		return Dictionary(materializer.call("get_material_summary"))
	return {"applied": false}

func _last_edit_submission(terrain: Node) -> Dictionary:
	if terrain != null and terrain.has_method("get_last_edit_submission_summary"):
		return Dictionary(terrain.call("get_last_edit_submission_summary"))
	return {}

func _terrain_world() -> Node:
	var reference := get_parent().get_node_or_null("WtTerrainReferenceScene")
	if reference != null and reference.has_method("get_terrain_world"):
		return reference.call("get_terrain_world")
	return null

func _materializer() -> Node:
	return get_parent().get_node_or_null("ValidationTerrainMaterials")

func _world_revision(terrain: Node) -> int:
	if terrain != null and terrain.has_method("get_world_revision"):
		return int(terrain.call("get_world_revision"))
	return 0

func _world_page_count(terrain: Node) -> int:
	if terrain != null and terrain.has_method("get_world_page_count"):
		return int(terrain.call("get_world_page_count"))
	return 0

func _world_source_revision(terrain: Node) -> int:
	if terrain != null and terrain.has_method("get_world_source_revision"):
		return int(terrain.call("get_world_source_revision"))
	return 0
