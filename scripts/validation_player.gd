extends CharacterBody3D


@export var human_input_enabled: bool = true
@export var simulation_enabled: bool = false
@export var move_speed: float = 7.0
@export var jump_velocity: float = 7.0
@export var gravity: float = 24.0

var _test_motion_direction := Vector3.ZERO


func set_human_input_enabled(enabled: bool) -> void:
	human_input_enabled = enabled


func set_simulation_enabled(enabled: bool) -> void:
	simulation_enabled = enabled
	if not enabled:
		velocity = Vector3.ZERO


func set_test_motion_direction(direction: Vector3) -> void:
	_test_motion_direction = direction.normalized()


func clear_test_motion_direction() -> void:
	_test_motion_direction = Vector3.ZERO


func get_player_summary() -> Dictionary:
	return {
		"present": true,
		"position": global_position,
		"on_floor": is_on_floor(),
		"human_input_enabled": human_input_enabled,
		"simulation_enabled": simulation_enabled,
		"test_motion_enabled": _test_motion_direction.length() > 0.0,
	}


func _physics_process(delta: float) -> void:
	if not simulation_enabled:
		return
	var direction := _test_motion_direction
	if direction.length() <= 0.0 and human_input_enabled:
		direction = _human_direction()
	velocity.x = direction.x * move_speed
	velocity.z = direction.z * move_speed
	if not is_on_floor():
		velocity.y -= gravity * delta
	elif human_input_enabled and Input.is_key_pressed(KEY_SPACE):
		velocity.y = jump_velocity
	else:
		velocity.y = 0.0
	move_and_slide()


func _human_direction() -> Vector3:
	var direction := Vector3.ZERO
	if Input.is_key_pressed(KEY_W):
		direction.z -= 1.0
	if Input.is_key_pressed(KEY_S):
		direction.z += 1.0
	if Input.is_key_pressed(KEY_A):
		direction.x -= 1.0
	if Input.is_key_pressed(KEY_D):
		direction.x += 1.0
	return direction.normalized()
