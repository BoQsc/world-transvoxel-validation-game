extends RefCounted

const GenerationProfile := preload("res://addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")


static func available_profile_ids() -> Array[StringName]:
	return [
		&"flat_baseline",
		&"flat_8x8",
		&"mountain_8x8",
		&"g8_sparse_2k",
		&"g10_single_viewer_2k",
		&"g11_generated_16x16",
		&"g12_generated_32x32",
		&"g14_generated_64x64",
	]


static func settings(profile_id: StringName) -> Dictionary:
	match str(profile_id):
		"flat_8x8":
			return _grid_8x8_settings(profile_id, Vector3(64, 12, 64), Vector3(64, 8, 64))
		"mountain_8x8":
			return _grid_8x8_settings(profile_id, Vector3(64, 24, 64), Vector3(64, 10, 64))
		"g8_sparse_2k":
			return {
				"viewer_position": Vector3(1000, 10, 1000),
				"player_start_position": Vector3(1000, 12, 1000),
				"camera_follow_offset": Vector3(70, 48, 70),
				"edit_point": Vector3(1000, 8, 1000),
				"fixture_label": "g8_sparse_2k_path",
			}
		"g10_single_viewer_2k":
			return {
				"viewer_position": Vector3(8, 8, 8),
				"player_start_position": Vector3(8, 12, 8),
				"camera_follow_offset": Vector3(70, 48, 70),
				"edit_point": Vector3(1000, 8, 1000),
				"fixture_label": "g10_single_viewer_2k_path",
			}
		"g11_generated_16x16":
			return {
				"viewer_position": Vector3(8, 8, 8),
				"player_start_position": Vector3(8, 22, 8),
				"camera_follow_offset": Vector3(70, 48, 70),
				"edit_point": Vector3(128, 8, 128),
				"fixture_label": "g11_generated_16x16_dense",
			}
		"g12_generated_32x32":
			return {
				"viewer_position": Vector3(8, 8, 8),
				"player_start_position": Vector3(8, 24, 8),
				"camera_follow_offset": Vector3(90, 60, 90),
				"edit_point": Vector3(264, 8, 264),
				"fixture_label": "g12_generated_32x32_dense",
			}
		"g14_generated_64x64":
			return {
				"viewer_position": Vector3(8, 8, 8),
				"player_start_position": Vector3(8, 24, 8),
				"camera_follow_offset": Vector3(120, 70, 120),
				"edit_point": Vector3(520, 8, 520),
				"fixture_label": "g14_generated_64x64_dense",
			}
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
	if str(profile_id) == "mountain_8x8" or _is_sparse_2k(profile_id) or _is_dense_generated(profile_id):
		generation.source_mode = GenerationProfile.SourceMode.BAKED_WORLD
	return generation


static func storage_profile(profile_id: StringName) -> Resource:
	var storage = StorageProfile.new()
	storage.profile_id = profile_id
	var root_path := "res://build/production-lifecycle-fixture"
	if _is_grid_8x8(profile_id):
		root_path = "res://build/g3-generation-fixtures/%s" % str(profile_id)
	elif _is_generated_16x16(profile_id):
		root_path = "res://build/g11-generated-fixture/%s" % str(profile_id)
	elif _is_generated_32x32(profile_id):
		root_path = "res://build/g12-generated-fixture/%s" % str(profile_id)
	elif _is_generated_64x64(profile_id):
		root_path = "res://build/g14-generated-fixture/%s" % str(profile_id)
	var manifest_name := "streaming.wtworld"
	if _is_grid_8x8(profile_id) or _is_dense_generated(profile_id):
		manifest_name = "world.wtworld"
	elif _is_sparse_2k(profile_id):
		manifest_name = "g8_2000x2000_sparse.wtworld"
	storage.world_manifest_path = "%s/%s" % [root_path, manifest_name]
	storage.object_root_path = root_path
	storage.edit_journal_path = "%s/world.wtedit" % root_path
	storage.snapshot_directory = "%s/snapshots" % root_path
	storage.allow_res_paths_for_test_fixtures = true
	return storage


static func viewer_positions(profile_id: StringName) -> Array[Vector3]:
	if _is_sparse_2k_single_viewer(profile_id) or _is_dense_generated(profile_id):
		return [Vector3(8.0, 8.0, 8.0)]
	if _is_sparse_2k_multi_viewer(profile_id):
		return [
			Vector3(8.0, 8.0, 8.0),
			Vector3(496.0, 8.0, 496.0),
			Vector3(1000.0, 8.0, 1000.0),
			Vector3(1504.0, 8.0, 496.0),
			Vector3(1991.0, 8.0, 1991.0),
		]
	if not _is_grid_8x8(profile_id):
		return [Vector3(8, 8, 8)]
	return [
		Vector3(40.0, 8.0, 40.0),
		Vector3(88.0, 8.0, 40.0),
		Vector3(40.0, 8.0, 88.0),
		Vector3(88.0, 8.0, 88.0),
	]


static func viewer_radius_chunks(profile_id: StringName) -> int:
	return 2 if _is_grid_8x8(profile_id) or _is_sparse_2k(profile_id) or _is_dense_generated(profile_id) else 0


static func expected_resource_count(profile_id: StringName) -> int:
	if _is_sparse_2k_single_viewer(profile_id) or _is_dense_generated(profile_id):
		return 9
	if _is_sparse_2k_multi_viewer(profile_id):
		return 93
	return 64 if _is_grid_8x8(profile_id) else 1


static func fixture_label(profile_id: StringName) -> String:
	return settings(profile_id).get("fixture_label", "8x8_multi_chunk" if _is_grid_8x8(profile_id) else "single_chunk")


static func edit_point(profile_id: StringName) -> Vector3:
	return settings(profile_id).get("edit_point", Vector3(8, 8, 8))


static func _is_grid_8x8(profile_id: StringName) -> bool:
	return str(profile_id) in ["flat_8x8", "mountain_8x8"]


static func _is_sparse_2k(profile_id: StringName) -> bool:
	return _is_sparse_2k_multi_viewer(profile_id) or _is_sparse_2k_single_viewer(profile_id)


static func _is_sparse_2k_multi_viewer(profile_id: StringName) -> bool:
	return str(profile_id) == "g8_sparse_2k"


static func _is_sparse_2k_single_viewer(profile_id: StringName) -> bool:
	return str(profile_id) == "g10_single_viewer_2k"


static func _is_generated_16x16(profile_id: StringName) -> bool:
	return str(profile_id) == "g11_generated_16x16"


static func _is_generated_32x32(profile_id: StringName) -> bool:
	return str(profile_id) == "g12_generated_32x32"


static func _is_generated_64x64(profile_id: StringName) -> bool:
	return str(profile_id) == "g14_generated_64x64"


static func _is_dense_generated(profile_id: StringName) -> bool:
	return _is_generated_16x16(profile_id) or _is_generated_32x32(profile_id) or _is_generated_64x64(profile_id)


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
