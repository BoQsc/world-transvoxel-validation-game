extends Node3D

const ReferenceScene := preload("res://addons/world_transvoxel_terrain/debug/wt_terrain_reference_scene.tscn")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")

@export var auto_start: bool = true
@export var viewer_position: Vector3 = Vector3(8, 8, 8)

var _reference_scene: Node


func _ready() -> void:
	_reference_scene = ReferenceScene.instantiate()
	add_child(_reference_scene)
	_reference_scene.ensure_reference_defaults()
	_reference_scene.get_terrain_world().storage_profile = _fixture_storage_profile()
	if auto_start:
		call_deferred("_start_validation_viewer")


func _start_validation_viewer() -> void:
	if not _reference_scene.start_reference_backend_world():
		push_error("validation playtest backend start failed")
		return
	if not await _wait_for_backend_state("running"):
		push_error("validation playtest backend did not reach running state")
		return
	if not _reference_scene.update_reference_viewer(1, 1, viewer_position, 0, 0):
		push_error("validation playtest viewer update failed")
		return
	if not await _wait_for_cold_idle(1, 1):
		push_error("validation playtest did not settle")
		return
	print("WT_VALIDATION_PLAYTEST_READY scene=validation_playtest viewer=settled")


func _fixture_storage_profile() -> Resource:
	var storage = StorageProfile.new()
	storage.world_manifest_path = "res://build/production-lifecycle-fixture/streaming.wtworld"
	storage.object_root_path = "res://build/production-lifecycle-fixture"
	storage.edit_journal_path = "res://build/production-lifecycle-fixture/world.wtedit"
	storage.snapshot_directory = "res://build/production-lifecycle-fixture/snapshots"
	storage.allow_res_paths_for_test_fixtures = true
	return storage


func _wait_for_backend_state(expected: String) -> bool:
	var terrain_world = _reference_scene.get_terrain_world()
	for _frame in range(900):
		if terrain_world.get_backend_world_state_name() == expected:
			await get_tree().process_frame
			return true
		await get_tree().process_frame
	return false


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
