extends Node

const EditOperation := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_operation.gd")
const EditBatch := preload("res://addons/world_transvoxel_terrain/edit/wt_terrain_edit_batch.gd")

@export var enabled: bool = true
@export var interaction_distance: float = 12.0
@export var dig_radius: float = 1.8
@export var place_radius: float = 1.8
@export_range(1, 65535, 1) var place_material_id: int = 4
@export var alternate_shape_toggles_enabled: bool = false

var _last_submission: Dictionary = {}


func get_last_submission() -> Dictionary:
	return _last_submission


func get_edit_policy_summary() -> Dictionary:
	return {
		"default_brush_shape": "sphere",
		"dig_radius": dig_radius,
		"place_radius": place_radius,
		"place_material_id": place_material_id,
		"alternate_shape_toggles_enabled": alternate_shape_toggles_enabled,
	}


func _input(event: InputEvent) -> void:
	_unhandled_input(event)


func submit_sphere_edit(
	mode_name: StringName,
	center: Vector3,
	radius: float,
	material_id: int = 1,
	density_value: float = 1.0
) -> bool:
	var terrain_world := _terrain_world()
	if terrain_world == null:
		_last_submission = {"accepted": false, "error": "terrain world unavailable"}
		return false
	var operation = EditOperation.new()
	operation.mode = _operation_mode(mode_name)
	operation.brush_shape = EditOperation.BrushShape.SPHERE
	operation.center = center
	operation.radius = radius
	operation.material_id = material_id
	operation.density_value = density_value
	var batch = EditBatch.new()
	batch.add_operation(operation)
	var accepted := bool(terrain_world.call("submit_edit_batch", batch, 404))
	_last_submission = {
		"accepted": accepted,
		"mode": str(mode_name),
		"center": center,
		"radius": radius,
		"material_id": material_id,
		"terrain_summary": terrain_world.call("get_last_edit_submission_summary"),
		"error": str(terrain_world.call("get_last_error")),
	}
	return accepted


func _unhandled_input(event: InputEvent) -> void:
	if not enabled or not _human_input_enabled() or Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		return
	if event is InputEventMouseButton and event.pressed:
		if _should_ignore_mouse_button_event():
			return
		if event.button_index == MOUSE_BUTTON_LEFT:
			submit_sphere_edit(&"carve", _target_point(), dig_radius, 1, 1.0)
			get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			submit_sphere_edit(&"construct", _target_point(), place_radius, place_material_id, 1.0)
			get_viewport().set_input_as_handled()


func _operation_mode(mode_name: StringName) -> int:
	match mode_name:
		&"carve":
			return EditOperation.Mode.CARVE
		&"construct", &"place":
			return EditOperation.Mode.CONSTRUCT
		&"fill":
			return EditOperation.Mode.FILL
		&"paint":
			return EditOperation.Mode.PAINT
		&"restore_to_base":
			return EditOperation.Mode.RESTORE_TO_BASE
		_:
			return EditOperation.Mode.CARVE


func _target_point() -> Vector3:
	var camera := _camera()
	if camera == null:
		return Vector3.ZERO
	var origin := camera.global_position
	var direction := -camera.global_transform.basis.z.normalized()
	var space := camera.get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(origin, origin + direction * interaction_distance)
	var hit := space.intersect_ray(query)
	if not hit.is_empty() and hit.has("position"):
		return hit["position"]
	return origin + direction * interaction_distance


func _terrain_world() -> Node:
	var parent := get_parent()
	if parent == null:
		return null
	var reference := parent.get_node_or_null("WtTerrainReferenceScene")
	if reference == null or not reference.has_method("get_terrain_world"):
		return null
	return reference.call("get_terrain_world")


func _camera() -> Camera3D:
	var parent := get_parent()
	if parent == null:
		return null
	return parent.get_node_or_null("Camera3D") as Camera3D


func _human_input_enabled() -> bool:
	var parent := get_parent()
	if parent == null:
		return false
	return bool(parent.get("human_input_enabled"))


func _should_ignore_mouse_button_event() -> bool:
	var parent := get_parent()
	return parent != null and parent.has_method("should_ignore_mouse_button_event") and \
			bool(parent.call("should_ignore_mouse_button_event"))
