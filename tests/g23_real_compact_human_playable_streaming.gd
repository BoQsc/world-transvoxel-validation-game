extends SceneTree

const MARKER := "WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var packed := load(SCENE_PATH)
	if packed == null:
		_helpers.fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	scene.human_input_enabled = true
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene):
		_helpers.fail("G23 scene did not become ready: %s" % str(scene.get_validation_summary()))
		return
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G23 player did not settle on terrain: %s" % str(scene.get_validation_summary()))
		return
	if not _assert_initial_human_playable(scene):
		return

	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	var terrain_world: Node = _helpers.terrain_world(scene)
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if reference == null or terrain_world == null or interactor == null:
		_helpers.fail("G23 missing reference, terrain world, or interactor")
		return
	var start_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var start_viewer_updates := int(start_metrics.get("viewer_updates", 0))
	var camera_delta := await _verify_mouse_camera(scene)
	if camera_delta <= 0.001:
		return
	var player_motion := await _move_player_and_wait_for_streaming(scene, terrain_world, start_viewer_updates)
	if player_motion <= 8.0:
		return
	var click_edits := await _verify_click_edits(scene, terrain_world, interactor)
	if click_edits != 2:
		return
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	var pending_retirements := int(final_metrics.get("pending_chunk_retirements", 0))
	var render_fading := int(final_metrics.get("render_fading_resources", 0))
	if pending_retirements != 0 or render_fading != 0:
		_helpers.fail("G23 final terrain window not settled: %s" % str(final_metrics))
		return
	print("%s profile=%s initial_resources=25 viewer_updates_delta=%d player_motion=%.3f camera_delta=%.4f click_edits=%d pending_retirements=%d render_fading_resources=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		int(scene.get_validation_summary().get("player_viewer_updates", 0)),
		player_motion,
		camera_delta,
		click_edits,
		pending_retirements,
		render_fading,
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _assert_initial_human_playable(scene: Node) -> bool:
	var summary: Dictionary = scene.get_validation_summary()
	if str(summary.get("playtest_profile_id", "")) != str(PROFILE_ID) or \
			not bool(summary.get("player_human_input_enabled", false)) or \
			int(summary.get("expected_resource_count", 0)) != 25 or \
			int(summary.get("render_resources", 0)) != 25 or \
			int(summary.get("collision_resources", 0)) != 25:
		_helpers.fail("G23 initial scene is not human-playable compact center: %s" % str(summary))
		return false
	if not _helpers.assert_no_dense_files("g23_initial"):
		return false
	return true


func _verify_mouse_camera(scene: Node) -> float:
	var camera := scene.get_node_or_null("Camera3D") as Camera3D
	if camera == null:
		_helpers.fail("G23 camera missing")
		return 0.0
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		var capture_click := InputEventMouseButton.new()
		capture_click.button_index = MOUSE_BUTTON_LEFT
		capture_click.pressed = true
		root.push_input(capture_click)
		await process_frame
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		_helpers.fail("G23 click did not capture mouse for camera control")
		return 0.0
	var before := camera.rotation
	var yaw_before := float(scene.get("_camera_yaw"))
	var motion := InputEventMouseMotion.new()
	motion.relative = Vector2(240.0, -120.0)
	root.push_input(motion)
	await process_frame
	await process_frame
	var yaw_after := float(scene.get("_camera_yaw"))
	var delta := before.distance_to(camera.rotation)
	if delta <= 0.001:
		_helpers.fail("G23 mouse motion did not change camera rotation: mouse_mode=%d camera_mode=%s yaw_before=%.4f yaw_after=%.4f before=%s after=%s" % [
			Input.mouse_mode,
			str(scene.get("camera_mode")),
			yaw_before,
			yaw_after,
			str(before),
			str(camera.rotation),
		])
	return delta


func _move_player_and_wait_for_streaming(scene: Node, terrain_world: Node, start_viewer_updates: int) -> float:
	var before: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	scene.set_player_test_motion(Vector3(1, 0, 0))
	for _frame in range(180):
		await physics_frame
		await process_frame
	scene.clear_player_test_motion()
	if not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G23 player did not settle after movement")
		return 0.0
	var after: Vector3 = scene.get_validation_summary().get("player_position", Vector3.ZERO)
	var moved := before.distance_to(after)
	var center_chunk := Vector3i(int(floor(after.x / 16.0)), 0, int(floor(after.z / 16.0)))
	if not await _helpers.wait_for_window(
		terrain_world, 25, "g23_player_driven_streaming",
		start_viewer_updates + 1, center_chunk, 25
	):
		return 0.0
	if int(scene.get_validation_summary().get("player_viewer_updates", 0)) <= 0:
		_helpers.fail("G23 player movement did not drive viewer updates")
		return 0.0
	return moved


func _verify_click_edits(scene: Node, terrain_world: Node, interactor: Node) -> int:
	var start_revision := int(terrain_world.call("get_backend_world_revision"))
	var accepted := 0
	if await _send_click(scene, interactor, MOUSE_BUTTON_LEFT, start_revision + 1):
		accepted += 1
	if await _send_click(scene, interactor, MOUSE_BUTTON_RIGHT, start_revision + 2):
		accepted += 1
	var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if int(metrics.get("render_fading_resources", 0)) != 0:
		_helpers.fail("G23 click edit left render fading resources: %s" % str(metrics))
		return 0
	return accepted


func _send_click(scene: Node, interactor: Node, button: MouseButton, revision: int) -> bool:
	var click := InputEventMouseButton.new()
	click.button_index = button
	click.pressed = true
	root.push_input(click)
	await process_frame
	if not await _helpers.wait_for_revision(_helpers.terrain_world(scene), revision):
		_helpers.fail("G23 click did not commit revision %d" % revision)
		return false
	if not await _helpers.wait_for_window(
		_helpers.terrain_world(scene), 25, "g23_click_settle", revision,
		null, 25
	):
		return false
	var submission: Dictionary = interactor.call("get_last_submission")
	if not bool(submission.get("accepted", false)):
		_helpers.fail("G23 click submission was not accepted: %s" % str(submission))
		return false
	return true
