extends RefCounted

var _reference_scene: Node
var _viewer_id := 1
var _revision := 1000
var _radius_chunks := 2
var _minimum_xz_delta := 8.0
var _last_position := Vector3(INF, INF, INF)
var _accepted_updates := 0


func configure(reference_scene: Node, radius_chunks: int, minimum_xz_delta: float) -> void:
	_reference_scene = reference_scene
	_radius_chunks = radius_chunks
	_minimum_xz_delta = minimum_xz_delta
	_last_position = Vector3(INF, INF, INF)
	_accepted_updates = 0


func update_from_player(player: Node) -> bool:
	if _reference_scene == null or player == null:
		return false
	var position: Vector3 = player.get("global_position")
	if not _should_update(position):
		return false
	_revision += 1
	if not bool(_reference_scene.call(
		"update_reference_viewer", _viewer_id, _revision, position, _radius_chunks, 0
	)):
		return false
	_last_position = position
	_accepted_updates += 1
	return true


func accepted_updates() -> int:
	return _accepted_updates


func current_revision() -> int:
	return _revision


func _should_update(position: Vector3) -> bool:
	if is_inf(_last_position.x):
		return true
	var delta := Vector2(position.x - _last_position.x, position.z - _last_position.z)
	return delta.length() >= _minimum_xz_delta
