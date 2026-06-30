extends SceneTree


const MARKER := "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const VIEWER_POSITION := Vector3(1032.0, 8.0, 1032.0)
const CENTER_CHUNK := Vector3i(64, 0, 64)
const CHUNK_SIZE := 16.0
const ACTIVE_RESOURCE_CAPACITY := 256
const RADIUS_STEPS := [
	{"label": "radius_1", "radius": 1, "expected": 9},
	{"label": "radius_2", "radius": 2, "expected": 25},
	{"label": "radius_4", "radius": 4, "expected": 81},
	{"label": "radius_6", "radius": 6, "expected": 169},
]
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")

var _helpers: RefCounted


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene: Node = load(SCENE_PATH).instantiate()
	scene.set("human_input_enabled", false)
	scene.set("player_driven_viewer_enabled", false)
	scene.call("configure_playtest_profile", PROFILE_ID)
	scene.call("set_camera_mode", &"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G53 scene did not become ready: %s" % str(scene.call("get_validation_summary")))
		return
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	var terrain_world: Node = _helpers.terrain_world(scene)
	if reference == null or terrain_world == null:
		_helpers.fail("G53 reference scene or terrain world missing")
		return

	var revision := 2
	var max_resources := 0
	var min_span_x := 999999.0
	var max_span_x := 0.0
	var min_span_z := 999999.0
	var max_span_z := 0.0
	var inside_ready_count := 0
	var outside_absent_count := 0
	var previous_span_x := 0.0
	for step in RADIUS_STEPS:
		var radius := int(step["radius"])
		var expected := int(step["expected"])
		if not bool(reference.call("update_reference_viewer", 1, revision, VIEWER_POSITION, radius, 0)):
			_helpers.fail("G53 viewer radius update rejected: radius=%d revision=%d" % [radius, revision])
			return
		if not await _wait_for_radius_window(
				terrain_world, expected, str(step["label"]), revision, CENTER_CHUNK,
				ACTIVE_RESOURCE_CAPACITY):
			return
		if not _verify_radius_boundary(terrain_world, radius):
			return
		inside_ready_count += 4
		outside_absent_count += 4
		var spread := _visible_mesh_spread(terrain_world)
		var span_x := float(spread.get("span_x", 0.0))
		var span_z := float(spread.get("span_z", 0.0))
		var minimum_span := float(radius * 2) * CHUNK_SIZE
		if int(spread.get("instances", 0)) != expected or span_x < minimum_span or span_z < minimum_span:
			_helpers.fail("G53 draw-distance spread invalid radius=%d expected=%d spread=%s" % [radius, expected, str(spread)])
			return
		if span_x + 0.001 < previous_span_x:
			_helpers.fail("G53 visible span shrank while radius grew: radius=%d previous=%.3f current=%.3f" % [radius, previous_span_x, span_x])
			return
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		max_resources = max(max_resources, int(metrics.get("render_resources", 0)))
		max_resources = max(max_resources, int(metrics.get("collision_resources", 0)))
		min_span_x = min(min_span_x, span_x)
		max_span_x = max(max_span_x, span_x)
		min_span_z = min(min_span_z, span_z)
		max_span_z = max(max_span_z, span_z)
		previous_span_x = span_x
		revision += 1

	if not _helpers.assert_no_dense_files("g53_finish"):
		return
	print("%s profile=%s radii=%s expected_resources=%s max_active_resources=%d active_capacity=%d inside_edge_ready=%d outside_radius_absent=%d min_span_x=%.3f max_span_x=%.3f min_span_z=%.3f max_span_z=%.3f dense_world_files=0" % [
		MARKER, str(PROFILE_ID), _radius_csv(), _expected_csv(), max_resources,
		ACTIVE_RESOURCE_CAPACITY, inside_ready_count, outside_absent_count,
		min_span_x, max_span_x, min_span_z, max_span_z,
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _verify_radius_boundary(terrain_world: Node, radius: int) -> bool:
	for chunk in [
		CENTER_CHUNK + Vector3i(radius, 0, 0),
		CENTER_CHUNK + Vector3i(-radius, 0, 0),
		CENTER_CHUNK + Vector3i(0, 0, radius),
		CENTER_CHUNK + Vector3i(0, 0, -radius),
	]:
		if not _helpers.is_ready_snapshot(terrain_world.call("query_chunk_state", chunk, 0)):
			_helpers.fail("G53 inside edge chunk not ready: radius=%d chunk=%s" % [radius, str(chunk)])
			return false
	var outside := radius + 1
	for chunk in [
		CENTER_CHUNK + Vector3i(outside, 0, 0),
		CENTER_CHUNK + Vector3i(-outside, 0, 0),
		CENTER_CHUNK + Vector3i(0, 0, outside),
		CENTER_CHUNK + Vector3i(0, 0, -outside),
	]:
		var snapshot: RefCounted = terrain_world.call("query_chunk_state", chunk, 0)
		if snapshot != null and bool(snapshot.call("is_present")):
			_helpers.fail("G53 outside radius chunk still present: radius=%d chunk=%s" % [radius, str(chunk)])
			return false
	return true


func _wait_for_radius_window(
	terrain_world: Node,
	expected_chunks: int,
	label: String,
	minimum_viewer_updates: int,
	center_chunk: Vector3i,
	max_active_resources: int
) -> bool:
	for _frame in range(2400):
		var metrics: Dictionary = terrain_world.call("get_runtime_metrics")
		var active_records := int(metrics.get("active_chunk_records", 0))
		var render_resources := int(metrics.get("render_resources", 0))
		var collision_resources := int(metrics.get("collision_resources", 0))
		if active_records == expected_chunks and \
				render_resources == expected_chunks and \
				collision_resources > 0 and \
				collision_resources <= expected_chunks and \
				int(metrics.get("viewer_updates", 0)) >= minimum_viewer_updates and \
				_helpers.is_ready_snapshot(terrain_world.call("query_chunk_state", center_chunk, 0)) and \
				int(metrics.get("queued_render", 0)) == 0 and \
				int(metrics.get("queued_collision", 0)) == 0 and \
				int(metrics.get("fully_ready_chunk_records", -1)) == active_records and \
				int(metrics.get("pending_chunk_retirements", 0)) == 0 and \
				int(metrics.get("render_fading_resources", 0)) == 0 and \
				active_records <= max_active_resources:
			return true
		await process_frame
	_helpers.fail("G53 radius window did not settle at %s expected=%d metrics=%s" % [
		label,
		expected_chunks,
		str(terrain_world.call("get_runtime_metrics")),
	])
	return false


func _visible_mesh_spread(terrain_world: Node) -> Dictionary:
	var backend: Node = terrain_world.call("get_backend_terrain")
	var stats := {"instances": 0, "min_x": 999999.0, "max_x": -999999.0, "min_z": 999999.0, "max_z": -999999.0}
	_accumulate_visible_mesh_spread(backend, stats)
	stats["span_x"] = float(stats["max_x"]) - float(stats["min_x"]) if int(stats["instances"]) > 0 else 0.0
	stats["span_z"] = float(stats["max_z"]) - float(stats["min_z"]) if int(stats["instances"]) > 0 else 0.0
	return stats


func _accumulate_visible_mesh_spread(node: Node, stats: Dictionary) -> void:
	if node == null:
		return
	if node is MeshInstance3D:
		var instance := node as MeshInstance3D
		if instance.visible and instance.mesh != null:
			var world_aabb: AABB = instance.global_transform * instance.mesh.get_aabb()
			stats["instances"] = int(stats["instances"]) + 1
			stats["min_x"] = min(float(stats["min_x"]), world_aabb.position.x)
			stats["max_x"] = max(float(stats["max_x"]), world_aabb.position.x + world_aabb.size.x)
			stats["min_z"] = min(float(stats["min_z"]), world_aabb.position.z)
			stats["max_z"] = max(float(stats["max_z"]), world_aabb.position.z + world_aabb.size.z)
	for child in node.get_children():
		if child is Node:
			_accumulate_visible_mesh_spread(child, stats)


func _radius_csv() -> String:
	var values: Array[String] = []
	for step in RADIUS_STEPS:
		values.append(str(int(step["radius"])))
	return ",".join(values)


func _expected_csv() -> String:
	var values: Array[String] = []
	for step in RADIUS_STEPS:
		values.append(str(int(step["expected"])))
	return ",".join(values)
