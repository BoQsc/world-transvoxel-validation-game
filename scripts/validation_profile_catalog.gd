extends RefCounted

const GenerationProfile := preload("res://addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")


static func available_profile_ids() -> Array[StringName]:
	return [&"flat_baseline", &"flat_8x8", &"mountain_8x8"]


static func settings(profile_id: StringName) -> Dictionary:
	match str(profile_id):
		"flat_8x8":
			return _grid_8x8_settings(profile_id, Vector3(64, 12, 64), Vector3(64, 8, 64))
		"mountain_8x8":
			return _grid_8x8_settings(profile_id, Vector3(64, 24, 64), Vector3(64, 10, 64))
		_:
			return {
				"viewer_position": Vector3(8, 8, 8),
				"player_start_position": Vector3(8, 12, 8),
				"camera_follow_offset": Vector3(22, 14, 24),
				"edit_point": Vector3(8, 8, 8),
			}


static func generation_profile(profile_id: StringName) -> Resource:
	var generation = GenerationProfile.new()
	generation.profile_id = profile_id
	generation.seed = 3003 if _is_grid_8x8(profile_id) else 1
	generation.source_mode = GenerationProfile.SourceMode.FLAT
	if str(profile_id) == "mountain_8x8":
		generation.source_mode = GenerationProfile.SourceMode.BAKED_WORLD
	return generation


static func storage_profile(profile_id: StringName) -> Resource:
	var storage = StorageProfile.new()
	storage.profile_id = profile_id
	var root_path := "res://build/production-lifecycle-fixture"
	if _is_grid_8x8(profile_id):
		root_path = "res://build/g3-generation-fixtures/%s" % str(profile_id)
	storage.world_manifest_path = "%s/%s" % [root_path, "world.wtworld" if _is_grid_8x8(profile_id) else "streaming.wtworld"]
	storage.object_root_path = root_path
	storage.edit_journal_path = "%s/world.wtedit" % root_path
	storage.snapshot_directory = "%s/snapshots" % root_path
	storage.allow_res_paths_for_test_fixtures = true
	return storage


static func viewer_positions(profile_id: StringName) -> Array[Vector3]:
	if not _is_grid_8x8(profile_id):
		return [Vector3(8, 8, 8)]
	return [
		Vector3(40.0, 8.0, 40.0),
		Vector3(88.0, 8.0, 40.0),
		Vector3(40.0, 8.0, 88.0),
		Vector3(88.0, 8.0, 88.0),
	]


static func viewer_radius_chunks(profile_id: StringName) -> int:
	return 2 if _is_grid_8x8(profile_id) else 0


static func expected_resource_count(profile_id: StringName) -> int:
	return 64 if _is_grid_8x8(profile_id) else 1


static func edit_point(profile_id: StringName) -> Vector3:
	return settings(profile_id).get("edit_point", Vector3(8, 8, 8))


static func _is_grid_8x8(profile_id: StringName) -> bool:
	return str(profile_id) in ["flat_8x8", "mountain_8x8"]


static func _grid_8x8_settings(
	profile_id: StringName,
	player_position: Vector3,
	edit_position: Vector3
) -> Dictionary:
	return {
		"viewer_position": Vector3(64, 10, 64),
		"player_start_position": player_position,
		"camera_follow_offset": Vector3(48, 34, 52),
		"edit_point": edit_position,
	}
