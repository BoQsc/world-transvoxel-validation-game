extends SceneTree

const MARKER := "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_PASS"
const PROFILE_ID := &"g19_compact_2k_on_demand"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const CAPTURE_ROOT := "res://artifacts/g51_material_texture_pipeline_quality"
const EXPECTED_ACTIVE_RESOURCES := 25
const MAX_TEXTURE_RESOLUTION := 16
const MAX_TEXTURE_BYTES := 4 * 1024
const MIN_COLORED_SAMPLES := 1000
const MATERIAL_IDS := [1, 2, 3, 4, 7]
const STREAM_SAMPLES := [
	Vector3(520, 8, 520),
	Vector3(1544, 8, 520),
]
const Helpers := preload("res://tests/g22_exact_compact_handoff_runtime_helpers.gd")
const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

var _helpers: RefCounted
var _sample_results := {}
var _sample_failures := {}


func _initialize() -> void:
	_helpers = Helpers.new(self, "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_FAIL")
	call_deferred("_run_test")


func _run_test() -> void:
	var scene = load(SCENE_PATH).instantiate()
	scene.human_input_enabled = false
	scene.set("player_driven_viewer_enabled", false)
	scene.configure_playtest_profile(PROFILE_ID)
	scene.set_camera_mode(&"first_person")
	root.add_child(scene)
	if not await _helpers.wait_for_ready(scene) or not await _helpers.wait_for_player_floor(scene):
		_helpers.fail("G51 scene did not become ready: %s" % str(scene.get_validation_summary()))
		return
	var terrain_world: Node = _helpers.terrain_world(scene)
	var reference: Node = scene.get_node_or_null("WtTerrainReferenceScene")
	var materializer: Node = scene.get_node_or_null("ValidationTerrainMaterials")
	var interactor: Node = scene.get_node_or_null("ValidationTerrainInteractor")
	if terrain_world == null or reference == null or materializer == null or interactor == null:
		_helpers.fail("G51 required scene nodes are missing")
		return
	_connect_public_samples(terrain_world)
	var initial_material := await _wait_for_material_quality(materializer, 1, "initial")
	if initial_material.is_empty():
		return
	var initial_signature := _mesh_material_signature(scene)
	if not _verify_mesh_material_signature(initial_signature, 0, "initial"):
		return
	var capture := await _capture_material_view(scene, ProfileCatalog.edit_point(PROFILE_ID), "initial_material")
	if capture.is_empty():
		return
	var edit_result := await _verify_edit_material_stability(scene, terrain_world, materializer, interactor, initial_material)
	if edit_result.is_empty():
		return
	var stream_result := await _verify_streaming_material_stability(
		scene, reference, terrain_world, materializer, initial_signature
	)
	if stream_result.is_empty():
		return
	var final_material: Dictionary = stream_result.get("material", {})
	var final_metrics: Dictionary = terrain_world.call("get_runtime_metrics")
	if not _helpers.assert_no_dense_files("g51_finish"):
		return
	print("%s profile=%s materialized_initial=%d materialized_after_edit=%d materialized_after_stream=%d texture_resolution=%d texture_bytes=%d texture_checksum=%d palette_ids=%s deterministic=1 shader_mode=%s edit_material=4 material_instance_stable=1 stream_windows=%d capture_colored_samples=%d material_auto_apply_delta=%d max_render_resources=%d max_collision_resources=%d dense_world_files=0" % [
		MARKER,
		str(PROFILE_ID),
		int(initial_material.get("materialized_instances", 0)),
		int(edit_result.get("materialized_instances", 0)),
		int(final_material.get("materialized_instances", 0)),
		int(final_material.get("texture_resolution", 0)),
		int(final_material.get("texture_bytes", 0)),
		int(final_material.get("texture_checksum", 0)),
		_material_ids_csv(final_material),
		str(final_material.get("shader_mode", "")),
		int(stream_result.get("stream_windows", 0)),
		int(capture.get("colored_samples", 0)),
		int(final_material.get("auto_apply_count", 0)) - int(initial_material.get("auto_apply_count", 0)),
		int(final_metrics.get("render_resources", 0)),
		int(final_metrics.get("collision_resources", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _verify_edit_material_stability(
	scene: Node,
	terrain_world: Node,
	materializer: Node,
	interactor: Node,
	initial_material: Dictionary
) -> Dictionary:
	var point: Vector3 = ProfileCatalog.edit_point(PROFILE_ID) + Vector3(11, 0, 0)
	var before_revision := int(terrain_world.call("get_world_revision"))
	if not bool(interactor.call("submit_sphere_edit", &"construct", point, 1.8, 4, 1.0)):
		_helpers.fail("G51 construct edit was rejected")
		return {}
	if not await _helpers.wait_for_revision(terrain_world, before_revision + 1):
		return {}
	if not await _helpers.wait_for_window(
			terrain_world, EXPECTED_ACTIVE_RESOURCES, "g51_after_edit", 1,
			_chunk_for(point), EXPECTED_ACTIVE_RESOURCES):
		return {}
	if not await _verify_authoritative_material(terrain_world, Vector3i(point), 4):
		return {}
	var material := await _wait_for_material_quality(
		materializer, int(initial_material.get("auto_apply_count", 0)) + 1, "after_edit"
	)
	return material


func _verify_streaming_material_stability(
	scene: Node,
	reference: Node,
	terrain_world: Node,
	materializer: Node,
	initial_signature: Dictionary
) -> Dictionary:
	var last_material: Dictionary = materializer.call("get_material_quality_summary")
	var stream_windows := 0
	var revision := 510
	for position in STREAM_SAMPLES:
		var before_updates := int(Dictionary(terrain_world.call("get_runtime_metrics")).get("viewer_updates", 0))
		scene.set("viewer_position", position)
		if not bool(reference.call("update_reference_viewer", 1, revision, position, 2, 0)):
			_helpers.fail("G51 viewer update rejected at %s" % str(position))
			return {}
		if not await _helpers.wait_for_window(
				terrain_world, EXPECTED_ACTIVE_RESOURCES, "g51_stream_%d" % revision,
				before_updates + 1, _chunk_for(position), EXPECTED_ACTIVE_RESOURCES):
			return {}
		var material := await _wait_for_material_quality(
			materializer, int(last_material.get("auto_apply_count", 0)) + 1,
			"stream_%d" % revision
		)
		if material.is_empty():
			return {}
		var signature := _mesh_material_signature(scene)
		if not _verify_mesh_material_signature(signature, int(initial_signature.get("material_instance_id", 0)), "stream"):
			return {}
		last_material = material
		stream_windows += 1
		revision += 1
	return {"material": last_material, "stream_windows": stream_windows}


func _wait_for_material_quality(materializer: Node, min_auto_count: int, label: String) -> Dictionary:
	var stable_frames := 0
	var last_count := -1
	for _frame in range(600):
		var summary: Dictionary = materializer.call("get_material_quality_summary")
		var auto_count := int(summary.get("auto_apply_count", 0))
		if _material_quality_ready(summary, min_auto_count):
			if auto_count == last_count:
				stable_frames += 1
				if stable_frames >= 20:
					return summary
			else:
				last_count = auto_count
				stable_frames = 0
		await process_frame
	_helpers.fail("G51 material quality did not stabilize at %s: %s" % [
		label,
		str(materializer.call("get_material_quality_summary")),
	])
	return {}


func _material_quality_ready(summary: Dictionary, min_auto_count: int) -> bool:
	return bool(summary.get("applied", false)) and \
			int(summary.get("materialized_instances", 0)) >= EXPECTED_ACTIVE_RESOURCES and \
			int(summary.get("texture_resolution", 999)) <= MAX_TEXTURE_RESOLUTION and \
			int(summary.get("texture_bytes", 999999)) <= MAX_TEXTURE_BYTES and \
			int(summary.get("texture_checksum", 0)) > 0 and \
			bool(summary.get("deterministic_texture", false)) and \
			str(summary.get("quality_implementation", "")) == "terrain_material_texture_pipeline_v1" and \
			_has_expected_material_ids(summary) and \
			int(summary.get("auto_apply_count", 0)) >= min_auto_count


func _mesh_material_signature(scene: Node) -> Dictionary:
	var terrain_world: Node = _helpers.terrain_world(scene)
	var backend: Node = terrain_world.call("get_backend_terrain")
	var result := {"meshes": 0, "missing_materials": 0, "material_instance_id": 0, "unique_materials": {}}
	_collect_mesh_materials(backend, result)
	result["unique_material_count"] = Dictionary(result.get("unique_materials", {})).size()
	return result


func _collect_mesh_materials(node: Node, result: Dictionary) -> void:
	if node is MeshInstance3D:
		var instance := node as MeshInstance3D
		if instance.mesh != null:
			result["meshes"] = int(result.get("meshes", 0)) + 1
			if instance.material_override == null:
				result["missing_materials"] = int(result.get("missing_materials", 0)) + 1
			else:
				var instance_id := instance.material_override.get_instance_id()
				result["material_instance_id"] = instance_id
				var unique := Dictionary(result.get("unique_materials", {}))
				unique[instance_id] = true
				result["unique_materials"] = unique
	for child in node.get_children():
		if child is Node:
			_collect_mesh_materials(child, result)


func _verify_mesh_material_signature(signature: Dictionary, expected_material_id: int, label: String) -> bool:
	if int(signature.get("meshes", 0)) < EXPECTED_ACTIVE_RESOURCES or \
			int(signature.get("missing_materials", 0)) != 0 or \
			int(signature.get("unique_material_count", 0)) != 1:
		_helpers.fail("G51 mesh material signature invalid at %s: %s" % [label, str(signature)])
		return false
	if expected_material_id > 0 and int(signature.get("material_instance_id", 0)) != expected_material_id:
		_helpers.fail("G51 material instance changed at %s: %s" % [label, str(signature)])
		return false
	return true


func _verify_authoritative_material(terrain_world: Node, point: Vector3i, expected_material: int) -> bool:
	_sample_results.clear()
	_sample_failures.clear()
	var request_id := int(terrain_world.call("request_authoritative_sample", point, 0))
	for _frame in range(900):
		if _sample_results.has(request_id):
			var sample: RefCounted = _sample_results[request_id]
			return int(sample.call("get_material")) == expected_material
		if _sample_failures.has(request_id):
			break
		await process_frame
	_helpers.fail("G51 authoritative material sample failed at %s" % str(point))
	return false


func _capture_material_view(scene: Node, target: Vector3, label: String) -> Dictionary:
	scene.set_player_visual_visible(false)
	scene.set_manual_camera_view(target + Vector3(0, 72, 0), target + Vector3(1, 0, 1))
	for _frame in range(30):
		await process_frame
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_helpers.fail("G51 empty material capture")
		return {}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CAPTURE_ROOT))
	image.save_png("%s/%s.png" % [CAPTURE_ROOT, label])
	var colored := 0
	for y in range(0, image.get_height(), 2):
		for x in range(0, image.get_width(), 2):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.06 and color.g > 0.18 and color.r > 0.14:
				colored += 1
	if colored < MIN_COLORED_SAMPLES:
		_helpers.fail("G51 material capture lacks colored terrain: %d" % colored)
		return {}
	return {"colored_samples": colored}


func _has_expected_material_ids(summary: Dictionary) -> bool:
	var ids := Array(summary.get("material_ids", []))
	for id in MATERIAL_IDS:
		if not ids.has(id):
			return false
	return true


func _material_ids_csv(summary: Dictionary) -> String:
	var ids := Array(summary.get("material_ids", []))
	var strings := PackedStringArray()
	for id in ids:
		strings.append(str(id))
	return ",".join(strings)


func _connect_public_samples(terrain_world: Node) -> void:
	if not terrain_world.authoritative_sample_ready.is_connected(_on_sample_ready):
		terrain_world.connect("authoritative_sample_ready", _on_sample_ready)
	if not terrain_world.authoritative_sample_failed.is_connected(_on_sample_failed):
		terrain_world.connect("authoritative_sample_failed", _on_sample_failed)


func _on_sample_ready(request_id: int, sample: RefCounted) -> void:
	_sample_results[request_id] = sample


func _on_sample_failed(request_id: int, error: String) -> void:
	_sample_failures[request_id] = error


func _chunk_for(position: Vector3) -> Vector3i:
	return Vector3i(clamp(int(floor(position.x / 16.0)), 0, 127), 0, clamp(int(floor(position.z / 16.0)), 0, 127))
