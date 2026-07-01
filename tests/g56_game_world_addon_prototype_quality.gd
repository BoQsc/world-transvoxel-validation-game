extends SceneTree

const MARKER := "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const EXPECTED_RESOURCES := 25
const GameWorldNode := preload("res://addons/world_transvoxel_game_world/wt_game_world_node.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")
const PlayerFactory := preload("res://scripts/validation_player_factory.gd")
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	if not _helpers.assert_no_dense_files("before_start"):
		return
	var game_world = GameWorldNode.new()
	game_world.name = "WorldTransvoxelGameWorld"
	root.add_child(game_world)
	var settings := ProfileCatalog.settings(PROFILE_ID)
	var start_position: Vector3 = settings.get("player_start_position", Vector3.ZERO)
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
		_helpers.fail("G56 game-world prototype did not start: %s" % game_world.get_last_error())
		return
	var terrain_world: Node = game_world.get_terrain_world()
	if terrain_world == null:
		_helpers.fail("G56 game-world prototype did not expose terrain world")
		return
	if not _verify_summary(game_world.get_game_world_summary(), "initial"):
		return
	player.global_position += Vector3(32.0, 0.0, 0.0)
	if not bool(game_world.update_player_viewer(true)):
		_helpers.fail("G56 player viewer integration did not accept forced update")
		return
	if not await game_world.wait_for_cold_idle(EXPECTED_RESOURCES, EXPECTED_RESOURCES):
		_helpers.fail("G56 terrain did not settle after player viewer update")
		return
	var before_revision := int(terrain_world.call("get_backend_world_revision"))
	if not bool(game_world.submit_sphere_edit(&"carve", ProfileCatalog.edit_point(PROFILE_ID), 1.8, -1, 1.0)):
		_helpers.fail("G56 game-world edit bridge rejected carve: %s" % str(game_world.get_last_edit_summary()))
		return
	if not await game_world.wait_for_world_revision(before_revision + 1):
		_helpers.fail("G56 game-world edit bridge did not commit")
		return
	if not await game_world.wait_for_cold_idle(EXPECTED_RESOURCES, EXPECTED_RESOURCES):
		_helpers.fail("G56 terrain did not settle after game-world edit")
		return
	var summary: Dictionary = game_world.get_game_world_summary()
	if not _verify_summary(summary, "final"):
		return
	if int(summary.get("player_viewer_updates", 0)) < 2 or int(summary.get("edit_replacements", 0)) <= 0:
		_helpers.fail("G56 integration counters invalid: %s" % str(summary))
		return
	if not _helpers.assert_no_dense_files("after_game_world"):
		return
	print("%s addon=%s api_version=%d standard_world_node=1 terrain_node_ready=1 player_attached=1 player_viewer_updates=%d edit_replacements=%d render_resources=%d collision_resources=%d active_records=%d dense_world_files=0" % [
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


func _verify_summary(summary: Dictionary, label: String) -> bool:
	if str(summary.get("addon_id", "")) != "world_transvoxel_game_world" or int(summary.get("api_version", 0)) != 1:
		_helpers.fail("G56 addon identity invalid at %s: %s" % [label, str(summary)])
		return false
	if not bool(summary.get("standard_world_node", false)) or not bool(summary.get("terrain_node_ready", false)):
		_helpers.fail("G56 standard world/terrain setup invalid at %s: %s" % [label, str(summary)])
		return false
	if not bool(summary.get("player_attached", false)) or bool(summary.get("player_human_input_enabled", true)):
		_helpers.fail("G56 player integration invalid at %s: %s" % [label, str(summary)])
		return false
	for key in ["active_chunk_records", "render_resources", "collision_resources"]:
		if int(summary.get(key, 0)) != EXPECTED_RESOURCES:
			_helpers.fail("G56 resource mismatch at %s: %s" % [label, str(summary)])
			return false
	for key in ["queued_render", "queued_collision", "pending_chunk_retirements", "render_fading_resources"]:
		if int(summary.get(key, 0)) != 0:
			_helpers.fail("G56 unsettled runtime state at %s: %s" % [label, str(summary)])
			return false
	return true
