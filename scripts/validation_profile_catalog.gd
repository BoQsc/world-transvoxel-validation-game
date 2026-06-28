extends RefCounted

const GenerationProfile := preload("res://addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")


static func available_profile_ids() -> Array[StringName]:
	return [&"flat_baseline", &"flat_large", &"mountain_large"]


static func settings(profile_id: StringName) -> Dictionary:
	match str(profile_id):
		"flat_large":
			return _large_settings(profile_id, Vector3(32, 12, 32), Vector3(32, 8, 32))
		"mountain_large":
			return _large_settings(profile_id, Vector3(32, 24, 32), Vector3(32, 9, 32))
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
	generation.seed = 3003 if str(profile_id).ends_with("_large") else 1
	generation.source_mode = GenerationProfile.SourceMode.FLAT
	if str(profile_id) == "mountain_large":
		generation.source_mode = GenerationProfile.SourceMode.BAKED_WORLD
	return generation


static func storage_profile(profile_id: StringName) -> Resource:
	var storage = StorageProfile.new()
	storage.profile_id = profile_id
	var root_path := "res://build/production-lifecycle-fixture"
	if str(profile_id).ends_with("_large"):
		root_path = "res://build/g3-generation-fixtures/%s" % str(profile_id)
	storage.world_manifest_path = "%s/%s" % [root_path, "world.wtworld" if str(profile_id).ends_with("_large") else "streaming.wtworld"]
	storage.object_root_path = root_path
	storage.edit_journal_path = "%s/world.wtedit" % root_path
	storage.snapshot_directory = "%s/snapshots" % root_path
	storage.allow_res_paths_for_test_fixtures = true
	return storage


static func viewer_positions(profile_id: StringName) -> Array[Vector3]:
	if not str(profile_id).ends_with("_large"):
		return [Vector3(8, 8, 8)]
	var positions: Array[Vector3] = []
	for z in range(4):
		for x in range(4):
			positions.append(Vector3(float(x * 16 + 8), 8.0, float(z * 16 + 8)))
	return positions


static func expected_resource_count(profile_id: StringName) -> int:
	return 8 if str(profile_id).ends_with("_large") else 1


static func edit_point(profile_id: StringName) -> Vector3:
	return settings(profile_id).get("edit_point", Vector3(8, 8, 8))


static func _large_settings(
	profile_id: StringName,
	player_position: Vector3,
	edit_position: Vector3
) -> Dictionary:
	return {
		"viewer_position": Vector3(32, 10, 32),
		"player_start_position": player_position,
		"camera_follow_offset": Vector3(48, 34, 52),
		"edit_point": edit_position,
	}
