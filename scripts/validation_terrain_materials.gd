extends Node

const TERRAIN_SHADER := preload("res://materials/validation_terrain_palette.gdshader")

@export var auto_apply: bool = true
@export_range(2, 64, 1) var texture_resolution: int = 16

var _summary := {
	"applied": false,
	"materialized_instances": 0,
	"reapplied_instances": 0,
	"texture_resolution": 0,
	"shader_mode": "validation_uv2_checker",
	"profile_id": "",
}
var _material: ShaderMaterial


func _ready() -> void:
	set_process(auto_apply)


func _process(_delta: float) -> void:
	var parent := get_parent()
	if parent != null and parent.has_method("get_validation_state") and \
			parent.call("get_validation_state") == "ready":
		apply_materials_now()


func get_material_summary() -> Dictionary:
	return _summary.duplicate()


func apply_materials_now() -> Dictionary:
	var backend := _backend_terrain()
	if backend == null:
		_summary["applied"] = false
		return get_material_summary()
	var result := _apply_to_meshes(backend, _material_instance())
	var profile := _material_profile_summary()
	_summary = {
		"applied": int(result.get("checked", 0)) > 0,
		"materialized_instances": int(result.get("checked", 0)),
		"reapplied_instances": int(result.get("updated", 0)),
		"texture_resolution": texture_resolution,
		"shader_mode": "validation_uv2_checker",
		"profile_id": str(profile.get("profile_id", "unknown")),
		"material_profile_configured": bool(profile.get("configured", false)),
	}
	return get_material_summary()


func _material_instance() -> ShaderMaterial:
	if _material == null:
		_material = _build_material()
	return _material


func _build_material() -> ShaderMaterial:
	var shader_material := ShaderMaterial.new()
	shader_material.shader = TERRAIN_SHADER
	shader_material.set_shader_parameter("checker_texture", _checker_texture())
	return shader_material


func _checker_texture() -> Texture2D:
	var image := Image.create(texture_resolution, texture_resolution, false, Image.FORMAT_RGBA8)
	for y in range(texture_resolution):
		for x in range(texture_resolution):
			var bright := ((x / 4) + (y / 4)) % 2 == 0
			var value := 1.0 if bright else 0.62
			image.set_pixel(x, y, Color(value, value, value, 1.0))
	return ImageTexture.create_from_image(image)


func _apply_to_meshes(node: Node, material: Material) -> Dictionary:
	var result := {"checked": 0, "updated": 0}
	_apply_to_meshes_recursive(node, material, result)
	return result


func _apply_to_meshes_recursive(node: Node, material: Material, result: Dictionary) -> void:
	if node is MeshInstance3D:
		var instance := node as MeshInstance3D
		if instance.mesh != null:
			result["checked"] = int(result.get("checked", 0)) + 1
			if instance.material_override != material:
				instance.material_override = material
				result["updated"] = int(result.get("updated", 0)) + 1
	for child in node.get_children():
		if child is Node:
			_apply_to_meshes_recursive(child, material, result)


func _backend_terrain() -> Node:
	var terrain_world := _terrain_world()
	if terrain_world == null or not terrain_world.has_method("get_backend_terrain"):
		return null
	return terrain_world.call("get_backend_terrain")


func _terrain_world() -> Node:
	var parent := get_parent()
	if parent == null:
		return null
	var reference := parent.get_node_or_null("WtTerrainReferenceScene")
	if reference == null or not reference.has_method("get_terrain_world"):
		return null
	return reference.call("get_terrain_world")


func _material_profile_summary() -> Dictionary:
	var terrain_world := _terrain_world()
	if terrain_world == null:
		return {}
	var profile = terrain_world.get("material_profile")
	if profile != null and profile.has_method("get_contract_summary"):
		var summary := Dictionary(profile.call("get_contract_summary"))
		summary["configured"] = true
		return summary
	return {}
