extends RefCounted

const ValidationPlayerScript := preload("res://scripts/validation_player.gd")


static func create(start_position: Vector3, human_input_enabled: bool) -> CharacterBody3D:
	var player := CharacterBody3D.new()
	player.name = "ValidationPlayer"
	player.set_script(ValidationPlayerScript)
	player.position = start_position
	player.call("set_human_input_enabled", human_input_enabled)
	player.add_child(_collision_shape())
	player.add_child(_visible_body())
	return player


static func _collision_shape() -> CollisionShape3D:
	var shape := CapsuleShape3D.new()
	shape.radius = 0.45
	shape.height = 1.8
	var collision := CollisionShape3D.new()
	collision.name = "PlayerCollision"
	collision.shape = shape
	return collision


static func _visible_body() -> MeshInstance3D:
	var mesh := CapsuleMesh.new()
	mesh.radius = 0.45
	mesh.height = 1.8
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.05, 0.85, 1.0)
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	var body := MeshInstance3D.new()
	body.name = "PlayerVisibleBody"
	body.mesh = mesh
	body.material_override = material
	return body
