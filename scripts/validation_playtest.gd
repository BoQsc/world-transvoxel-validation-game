extends Node3D

const ReferenceScene := preload("res://addons/world_transvoxel_terrain/debug/wt_terrain_reference_scene.tscn")
const MeshStats := preload("res://scripts/validation_mesh_stats.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")
const InputCapture := preload("res://scripts/validation_input_capture.gd")
const ValidationPlayerFactory := preload("res://scripts/validation_player_factory.gd")
const PlayerViewerDriver := preload("res://scripts/validation_player_viewer_driver.gd")
const ValidationViewHelpers := preload("res://scripts/validation_view_helpers.gd")

@export var auto_start: bool = true
@export var human_input_enabled: bool = true
@export var camera_mode: StringName = &"first_person"
@export var playtest_profile_id: StringName = &"flat_baseline"
@export var mouse_look_enabled: bool = true
@export var mouse_sensitivity: float = 0.0025
@export var player_driven_viewer_enabled: bool = true
@export var player_viewer_update_distance: float = 8.0
@export var viewer_position: Vector3 = Vector3(8, 8, 8)
@export var player_start_position: Vector3 = Vector3(8, 12, 8)
@export var first_person_eye_height: float = 1.55
@export var camera_follow_offset: Vector3 = Vector3(22, 14, 24)

var _reference_scene: Node
var _player: CharacterBody3D
var _camera: Camera3D
var _status_label: Label
var _validation_state := "initializing"
var _status_text := "initializing validation playtest"
var _camera_yaw := -0.78
var _camera_pitch := -0.18
var _input_capture := InputCapture.new()
var _player_viewer_driver := PlayerViewerDriver.new()

func _ready() -> void:
	_apply_profile_settings()
	_add_validation_player()
	_configure_camera()
	_status_label = ValidationViewHelpers.add_status_overlay(self, _status_text)
	ValidationViewHelpers.add_crosshair(self)
	ValidationViewHelpers.add_orientation_markers(self, viewer_position)
	_reference_scene = ReferenceScene.instantiate()
	add_child(_reference_scene)
	_reference_scene.ensure_reference_defaults()
	_configure_player_viewer_driver()
	_apply_profile_resources()
	_set_status("STARTING: terrain world not settled yet")
	_input_capture.capture_if_enabled(human_input_enabled)
	if auto_start:
		call_deferred("_start_validation_viewer")

func _process(_delta: float) -> void:
	_update_camera()
	if _validation_state == "ready" and player_driven_viewer_enabled:
		_player_viewer_driver.update_from_player(_player)

func _input(event: InputEvent) -> void:
	_unhandled_input(event)
func _unhandled_input(event: InputEvent) -> void:
	if not human_input_enabled:
		return
	if _input_capture.handle_capture_event(event):
		get_viewport().set_input_as_handled()
		return
	if event is InputEventMouseMotion and mouse_look_enabled and camera_mode == &"first_person" and \
			Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		_camera_yaw -= event.relative.x * mouse_sensitivity
		_camera_pitch = clamp(_camera_pitch - event.relative.y * mouse_sensitivity, -1.35, 1.35)
		get_viewport().set_input_as_handled()

func set_human_input_enabled(enabled: bool) -> void:
	human_input_enabled = enabled
	if not enabled:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if _player != null and _player.has_method("set_human_input_enabled"):
		_player.call("set_human_input_enabled", enabled)

func set_camera_mode(mode: StringName) -> void:
	camera_mode = mode
	_update_camera()

func should_ignore_mouse_button_event() -> bool:
	return _input_capture.should_ignore_mouse_button_event()

func set_manual_camera_view(position: Vector3, target: Vector3) -> void:
	camera_mode = &"manual"
	if _camera != null:
		_camera.global_position = position
		_camera.look_at(target, Vector3.UP)

func set_player_visual_visible(visible: bool) -> void:
	if _player != null:
		_player.visible = visible
		var body := _player.get_node_or_null("PlayerVisibleBody") as Node3D
		if body != null:
			body.visible = visible

func set_player_test_motion(direction: Vector3) -> void:
	if _player != null and _player.has_method("set_test_motion_direction"):
		_player.call("set_test_motion_direction", direction)

func configure_playtest_profile(profile_id: StringName) -> void:
	playtest_profile_id = profile_id
	_apply_profile_settings()
	if _reference_scene != null:
		_apply_profile_resources()
		_configure_player_viewer_driver()
	if _player != null:
		_player.global_position = player_start_position

func clear_player_test_motion() -> void:
	if _player != null and _player.has_method("clear_test_motion_direction"):
		_player.call("clear_test_motion_direction")

func _start_validation_viewer() -> void:
	if not _reference_scene.start_reference_backend_world():
		_fail("backend start failed")
		return
	if not await _wait_for_backend_state("running"):
		_fail("backend did not reach running state")
		return
	var viewer_count := _submit_profile_viewers()
	if viewer_count <= 0:
		return
	var resource_count := ProfileCatalog.expected_resource_count(playtest_profile_id)
	if not await _wait_for_cold_idle(resource_count, resource_count):
		_fail("terrain did not settle")
		return
	var terrain_stats := _terrain_mesh_stats()
	if int(terrain_stats.get("instances", 0)) <= 0:
		_fail("no visible terrain MeshInstance3D was found")
		return
	if int(terrain_stats.get("triangles", 0)) <= 0:
		_fail("terrain MeshInstance3D has no drawable triangles: %s" % str(terrain_stats))
		return
	_enable_player_simulation()
	_validation_state = "ready"
	_set_status(
		"READY: profile=%s fixture=%s resources=%d viewers=%d meshes=%d triangles=%d player_start=%s" % [
			str(playtest_profile_id),
			ProfileCatalog.fixture_label(playtest_profile_id),
			resource_count,
			viewer_count,
			int(terrain_stats.get("instances", 0)),
			int(terrain_stats.get("triangles", 0)),
			str(_player.global_position if _player != null else Vector3.ZERO),
		]
	)
	print("WT_VALIDATION_PLAYTEST_READY scene=validation_playtest viewer=settled")


func get_validation_state() -> String:
	return _validation_state


func get_validation_summary() -> Dictionary:
	var terrain_world = _reference_scene.get_terrain_world() if _reference_scene != null else null
	var metrics: Dictionary = {}
	if terrain_world != null:
		metrics = terrain_world.get_runtime_metrics()
	var terrain_stats := _terrain_mesh_stats()
	var player_stats := _player_summary()
	return {
		"state": _validation_state,
		"playtest_profile_id": str(playtest_profile_id),
		"status_text": _status_text,
		"terrain_mesh_instances": int(terrain_stats.get("instances", 0)),
		"terrain_mesh_surfaces": int(terrain_stats.get("surfaces", 0)),
		"terrain_face_vertices": int(terrain_stats.get("face_vertices", 0)),
		"terrain_triangles": int(terrain_stats.get("triangles", 0)),
		"terrain_max_extent": float(terrain_stats.get("max_extent", 0.0)),
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
		"viewer_position": viewer_position,
		"fixture_label": ProfileCatalog.fixture_label(playtest_profile_id),
		"viewer_count": ProfileCatalog.viewer_positions(playtest_profile_id).size(),
		"expected_resource_count": ProfileCatalog.expected_resource_count(playtest_profile_id),
		"camera_position": _camera.global_position if _camera != null else Vector3.ZERO,
		"player_present": bool(player_stats.get("present", false)),
		"player_position": player_stats.get("position", Vector3.ZERO),
		"player_on_floor": bool(player_stats.get("on_floor", false)),
		"player_human_input_enabled": bool(player_stats.get("human_input_enabled", false)),
		"player_simulation_enabled": bool(player_stats.get("simulation_enabled", false)),
		"player_viewer_updates": _player_viewer_driver.accepted_updates(),
		"player_camera_current": _camera != null and _camera.current,
		"camera_mode": camera_mode,
		"crosshair_present": get_node_or_null("ValidationCrosshair") != null,
	}


func _add_validation_player() -> void:
	_player = ValidationPlayerFactory.create(player_start_position, human_input_enabled)
	add_child(_player)


func _configure_camera() -> void:
	_camera = get_node_or_null("Camera3D") as Camera3D
	if _camera == null:
		return
	_camera.current = true
	_camera.fov = 55.0
	_update_camera()


func _update_camera() -> void:
	if _camera == null or _player == null:
		return
	if camera_mode == &"manual":
		return
	if _player.has_method("set_view_yaw"):
		_player.call("set_view_yaw", _camera_yaw)
	if camera_mode == &"overview":
		_camera.global_position = _player.global_position + camera_follow_offset
		_camera.look_at(_player.global_position + Vector3(0, 1, 0), Vector3.UP)
		return
	_camera.global_position = _player.global_position + Vector3(0, first_person_eye_height, 0)
	_camera.rotation = Vector3(_camera_pitch, _camera_yaw, 0)


func _apply_profile_settings() -> void:
	var profile_settings := ProfileCatalog.settings(playtest_profile_id)
	viewer_position = profile_settings.get("viewer_position", viewer_position)
	player_start_position = profile_settings.get("player_start_position", player_start_position)
	camera_follow_offset = profile_settings.get("camera_follow_offset", camera_follow_offset)


func _apply_profile_resources() -> void:
	var terrain_world = _reference_scene.get_terrain_world()
	terrain_world.generation_profile = ProfileCatalog.generation_profile(playtest_profile_id)
	terrain_world.storage_profile = ProfileCatalog.storage_profile(playtest_profile_id)


func _configure_player_viewer_driver() -> void:
	if _reference_scene == null:
		return
	_player_viewer_driver.configure(
		_reference_scene,
		ProfileCatalog.viewer_radius_chunks(playtest_profile_id),
		player_viewer_update_distance
	)


func _terrain_mesh_stats() -> Dictionary:
	return MeshStats.collect(_reference_scene)

func _submit_profile_viewers() -> int:
	var viewer_id := 1
	var radius_chunks := ProfileCatalog.viewer_radius_chunks(playtest_profile_id)
	for position in ProfileCatalog.viewer_positions(playtest_profile_id):
		if not _reference_scene.update_reference_viewer(viewer_id, 1, position, radius_chunks, 0):
			_fail("viewer update failed at %s" % str(position))
			return 0
		viewer_id += 1
	return viewer_id - 1


func _enable_player_simulation() -> void:
	if _player != null and _player.has_method("set_simulation_enabled"):
		_player.call("set_simulation_enabled", true)


func _player_summary() -> Dictionary:
	if _player == null or not _player.has_method("get_player_summary"):
		return {"present": false}
	return Dictionary(_player.call("get_player_summary"))


func _wait_for_backend_state(expected: String) -> bool:
	var terrain_world = _reference_scene.get_terrain_world()
	for _frame in range(900):
		if terrain_world.get_backend_world_state_name() == expected:
			await get_tree().process_frame
			return true
		await get_tree().process_frame
	return false


func _set_status(text: String) -> void:
	_status_text = text
	if _status_label != null:
		_status_label.text = text


func _fail(message: String) -> void:
	_validation_state = "failed"
	_set_status("FAILED: %s" % message)
	push_error("WT_VALIDATION_PLAYTEST_FAIL: " + message)


func _wait_for_cold_idle(render_count: int, collision_count: int) -> bool:
	var terrain_world = _reference_scene.get_terrain_world()
	for _frame in range(900):
		var summary: Dictionary = terrain_world.get_cold_idle_summary()
		if bool(summary.get("cold_idle", false)) and \
				int(summary.get("render_resources", -1)) >= render_count and \
				int(summary.get("collision_resources", -1)) >= collision_count:
			await get_tree().process_frame
			return true
		await get_tree().process_frame
	return false
