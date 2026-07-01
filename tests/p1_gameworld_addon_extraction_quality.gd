extends SceneTree

const MARKER := "WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_PASS"
const ADDON_ID := "world_transvoxel_gameworld"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const EXPECTED_RESOURCES := 25
const GameWorldNode := preload("res://addons/world_transvoxel_gameworld/wt_game_world_node.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")
const PlayerFactory := preload("res://scripts/validation_player_factory.gd")
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	if not _helpers.assert_no_dense_files("before_start"):
		return
	var game_world = GameWorldNode.new()
	game_world.name = "WtGameWorld"
	root.add_child(game_world)
	var start_position: Vector3 = ProfileCatalog.settings(PROFILE_ID).get("player_start_position", Vector3.ZERO)
	var player := PlayerFactory.create(start_position, false)
	game_world.configure_game_world(
		PROFILE_ID,
		ProfileCatalog.generation_profile(PROFILE_ID),
		ProfileCatalog.storage_profile(PROFILE_ID),
		ProfileCatalog.viewer_positions(PROFILE_ID),
		ProfileCatalog.viewer_radius_chunks(PROFILE_ID),
		EXPECTED_RESOURCES,
		start_position
	)
	game_world.attach_player(player, start_position)
	if not await game_world.start_world():
		_helpers.fail("P1 gameworld addon did not start: %s" % game_world.get_last_error())
		return
	var terrain_world: Node = game_world.get_terrain_world()
	if terrain_world == null:
		_helpers.fail("P1 gameworld addon did not expose terrain world")
		return
	player.global_position += Vector3(32.0, 0.0, 0.0)
	if not bool(game_world.update_player_viewer(true)):
		_helpers.fail("P1 player viewer integration did not accept forced update")
		return
	if not await game_world.wait_for_cold_idle(EXPECTED_RESOURCES, EXPECTED_RESOURCES):
		_helpers.fail("P1 terrain did not settle after player viewer update")
		return
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	if not bool(game_world.submit_sphere_edit(&"carve", ProfileCatalog.edit_point(PROFILE_ID), 1.8, -1, 1.0)):
		_helpers.fail("P1 edit bridge rejected carve: %s" % str(game_world.get_last_edit_summary()))
		return
	if not await game_world.wait_for_world_revision(before_revision + 1):
		_helpers.fail("P1 edit bridge did not commit")
		return
	if not await game_world.wait_for_cold_idle(EXPECTED_RESOURCES, EXPECTED_RESOURCES):
		_helpers.fail("P1 terrain did not settle after edit")
		return
	var summary: Dictionary = game_world.get_game_world_summary()
	if not _verify_summary(summary):
		return
	if not _helpers.assert_no_dense_files("after_gameworld"):
		return
	print("%s addon=%s api_version=%d standard_world_node=1 terrain_node_ready=1 player_attached=1 player_viewer_updates=%d edit_replacements=%d render_resources=%d collision_resources=%d active_records=%d validation_internals=0 dense_world_files=0" % [
		MARKER,
		str(summary.get("addon_id", "")),
		int(summary.get("api_version", 0)),
		int(summary.get("player_viewer_updates", 0)),
		int(summary.get("edit_replacements", 0)),
		int(summary.get("render_resources", 0)),
		int(summary.get("collision_resources", 0)),
		int(summary.get("active_chunk_records", 0)),
	])
	await process_frame
	quit(0)


func _verify_summary(summary: Dictionary) -> bool:
	if str(summary.get("addon_id", "")) != ADDON_ID or int(summary.get("api_version", 0)) != 1:
		_helpers.fail("P1 addon identity invalid: %s" % str(summary))
		return false
	if not bool(summary.get("standard_world_node", false)) or not bool(summary.get("terrain_node_ready", false)):
		_helpers.fail("P1 standard world setup invalid: %s" % str(summary))
		return false
	if not bool(summary.get("player_attached", false)) or bool(summary.get("player_human_input_enabled", true)):
		_helpers.fail("P1 player bridge invalid: %s" % str(summary))
		return false
	for key in ["active_chunk_records", "render_resources", "collision_resources"]:
		if int(summary.get(key, 0)) != EXPECTED_RESOURCES:
			_helpers.fail("P1 resource mismatch: %s" % str(summary))
			return false
	for key in ["queued_render", "queued_collision", "pending_chunk_retirements", "render_fading_resources"]:
		if int(summary.get(key, 0)) != 0:
			_helpers.fail("P1 unsettled terrain: %s" % str(summary))
			return false
	return int(summary.get("player_viewer_updates", 0)) >= 2 and int(summary.get("edit_replacements", 0)) > 0
