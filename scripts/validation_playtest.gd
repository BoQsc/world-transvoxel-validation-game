extends Node3D

const ReferenceScene := preload("res://addons/world_transvoxel_terrain/debug/wt_terrain_reference_scene.tscn")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")

@export var auto_start: bool = true
@export var viewer_position: Vector3 = Vector3(8, 8, 8)
@export var camera_position: Vector3 = Vector3(30, 24, 34)

var _reference_scene: Node
var _status_label: Label
var _validation_state := "initializing"
var _status_text := "initializing validation playtest"


func _ready() -> void:
	_configure_camera()
	_add_status_overlay()
	_add_orientation_markers()
	_reference_scene = ReferenceScene.instantiate()
	add_child(_reference_scene)
	_reference_scene.ensure_reference_defaults()
	_reference_scene.get_terrain_world().storage_profile = _fixture_storage_profile()
	_set_status("STARTING: terrain world not settled yet")
	if auto_start:
		call_deferred("_start_validation_viewer")


func _start_validation_viewer() -> void:
	if not _reference_scene.start_reference_backend_world():
		_fail("backend start failed")
		return
	if not await _wait_for_backend_state("running"):
		_fail("backend did not reach running state")
		return
	if not _reference_scene.update_reference_viewer(1, 1, viewer_position, 0, 0):
		_fail("viewer update failed")
		return
	if not await _wait_for_cold_idle(1, 1):
		_fail("terrain did not settle")
		return
	var terrain_meshes := _count_terrain_mesh_instances()
	if terrain_meshes <= 0:
		_fail("no visible terrain MeshInstance3D was found")
		return
	_validation_state = "ready"
	_set_status("READY: terrain_meshes=%d viewer=%s camera_target=%s" % [
		terrain_meshes, str(viewer_position), str(viewer_position)
	])
	print("WT_VALIDATION_PLAYTEST_READY scene=validation_playtest viewer=settled")


func get_validation_state() -> String:
	return _validation_state


func get_validation_summary() -> Dictionary:
	var terrain_world = _reference_scene.get_terrain_world() if _reference_scene != null else null
	var metrics: Dictionary = {}
	if terrain_world != null:
		metrics = terrain_world.get_runtime_metrics()
	return {
		"state": _validation_state,
		"status_text": _status_text,
		"terrain_mesh_instances": _count_terrain_mesh_instances(),
		"render_resources": int(metrics.get("render_resources", 0)),
		"collision_resources": int(metrics.get("collision_resources", 0)),
		"viewer_position": viewer_position,
		"camera_position": camera_position,
	}


func _configure_camera() -> void:
	var camera := get_node_or_null("Camera3D") as Camera3D
	if camera == null:
		return
	camera.position = camera_position
	camera.current = true
	camera.fov = 55.0
	camera.look_at(viewer_position, Vector3.UP)


func _add_status_overlay() -> void:
	var layer := CanvasLayer.new()
	layer.name = "ValidationStatusOverlay"
	add_child(layer)
	var panel := PanelContainer.new()
	panel.name = "Panel"
	panel.set_anchors_preset(Control.PRESET_TOP_WIDE)
	panel.offset_left = 12.0
	panel.offset_top = 160.0
	panel.offset_right = -12.0
	panel.offset_bottom = 238.0
	layer.add_child(panel)
	_status_label = Label.new()
	_status_label.name = "StatusLabel"
	_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status_label.text = _status_text
	panel.add_child(_status_label)


func _add_orientation_markers() -> void:
	var markers := Node3D.new()
	markers.name = "ValidationMarkers"
	add_child(markers)
	_add_box_marker(markers, "AxisXRed", Vector3(8, 0.05, 0), Vector3(16, 0.1, 0.1), Color.RED)
	_add_box_marker(markers, "AxisYGreen", Vector3(0.05, 8, 0), Vector3(0.1, 16, 0.1), Color.GREEN)
	_add_box_marker(markers, "AxisZBlue", Vector3(0, 0.05, 8), Vector3(0.1, 0.1, 16), Color.BLUE)
	_add_box_marker(markers, "ViewerYellow", viewer_position, Vector3(0.8, 0.8, 0.8), Color.YELLOW)


func _add_box_marker(parent: Node, marker_name: String, position: Vector3, size: Vector3, color: Color) -> void:
	var mesh := BoxMesh.new()
	mesh.size = size
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	var instance := MeshInstance3D.new()
	instance.name = marker_name
	instance.mesh = mesh
	instance.material_override = material
	instance.position = position
	parent.add_child(instance)


func _fixture_storage_profile() -> Resource:
	var storage = StorageProfile.new()
	storage.world_manifest_path = "res://build/production-lifecycle-fixture/streaming.wtworld"
	storage.object_root_path = "res://build/production-lifecycle-fixture"
	storage.edit_journal_path = "res://build/production-lifecycle-fixture/world.wtedit"
	storage.snapshot_directory = "res://build/production-lifecycle-fixture/snapshots"
	storage.allow_res_paths_for_test_fixtures = true
	return storage


func _count_terrain_mesh_instances() -> int:
	if _reference_scene == null:
		return 0
	var terrain_world = _reference_scene.get_terrain_world()
	if terrain_world == null:
		return 0
	var backend = terrain_world.get_backend_terrain()
	if backend == null:
		return 0
	return _count_mesh_instances(backend)


func _count_mesh_instances(node: Node) -> int:
	var count := 1 if node is MeshInstance3D else 0
	for child in node.get_children():
		if child is Node:
			count += _count_mesh_instances(child)
	return count


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
				int(summary.get("render_resources", -1)) == render_count and \
				int(summary.get("collision_resources", -1)) == collision_count:
			await get_tree().process_frame
			return true
		await get_tree().process_frame
	return false
