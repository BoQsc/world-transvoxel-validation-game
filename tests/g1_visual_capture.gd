extends SceneTree

const MARKER := "WT_VALIDATION_G1_VISUAL_CAPTURE_PASS"
const SCENE_PATH := "res://scenes/validation_playtest.tscn"
const CAPTURE_PATH := "res://artifacts/g1_visual_capture/capture.png"


func _initialize() -> void:
	call_deferred("_run_capture")


func _run_capture() -> void:
	var packed := load(SCENE_PATH)
	if packed == null:
		_fail("validation playtest scene did not load")
		return
	var scene = packed.instantiate()
	scene.set_human_input_enabled(false)
	scene.set_camera_mode(&"overview")
	root.add_child(scene)
	if not await _wait_for_ready(scene):
		_fail("validation playtest scene did not become ready")
		return
	for _frame in range(30):
		await physics_frame
	var viewport := root
	var image := viewport.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport image is empty")
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://artifacts/g1_visual_capture"))
	var error := image.save_png(CAPTURE_PATH)
	if error != OK:
		_fail("failed to save capture: %s" % error_string(error))
		return
	var metrics := _image_metrics(image)
	if int(metrics.get("non_gray_samples", 0)) < 50:
		_fail("capture lacks enough non-gray samples: %s" % str(metrics))
		return
	if int(metrics.get("center_bright_samples", 0)) < 1000:
		_fail("capture lacks enough centered terrain-bright samples: %s" % str(metrics))
		return
	if int(metrics.get("player_cyan_samples", 0)) < 20:
		_fail("capture lacks enough visible player cyan samples: %s" % str(metrics))
		return
	var summary: Dictionary = scene.get_validation_summary()
	if int(summary.get("terrain_triangles", 0)) <= 0:
		_fail("captured scene terrain mesh has no triangles")
		return
	if not bool(summary.get("player_present", false)):
		_fail("captured scene has no validation player")
		return
	print("%s path=%s size=%dx%d non_gray_samples=%d center_bright_samples=%d player_cyan_samples=%d terrain_triangles=%d" % [
		MARKER,
		CAPTURE_PATH,
		image.get_width(),
		image.get_height(),
		int(metrics.get("non_gray_samples", 0)),
		int(metrics.get("center_bright_samples", 0)),
		int(metrics.get("player_cyan_samples", 0)),
		int(summary.get("terrain_triangles", 0)),
	])
	scene.queue_free()
	await process_frame
	quit(0)


func _wait_for_ready(scene: Node) -> bool:
	for _frame in range(900):
		if scene.has_method("get_validation_state") and \
				scene.get_validation_state() == "ready":
			await process_frame
			return true
		await process_frame
	return false


func _image_metrics(image: Image) -> Dictionary:
	var non_gray_samples := 0
	var center_bright_samples := 0
	var player_cyan_samples := 0
	var sample_count := 0
	var width := image.get_width()
	var height := image.get_height()
	var step_x = 1
	var step_y = 1
	var center_min_x := int(width * 0.25)
	var center_max_x := int(width * 0.85)
	var center_min_y := int(height * 0.2)
	var center_max_y := int(height * 0.8)
	for y in range(0, height, step_y):
		for x in range(0, width, step_x):
			var color := image.get_pixel(x, y)
			var spread = max(color.r, max(color.g, color.b)) - min(color.r, min(color.g, color.b))
			if spread > 0.08:
				non_gray_samples += 1
			if color.r < 0.32 and color.g > 0.25 and color.b > 0.30 and \
					max(color.g, color.b) - color.r > 0.14:
				player_cyan_samples += 1
			var luminance = (color.r + color.g + color.b) / 3.0
			if x >= center_min_x and x < center_max_x and \
					y >= center_min_y and y < center_max_y and \
					luminance > 0.45:
				center_bright_samples += 1
			sample_count += 1
	return {
		"sample_count": sample_count,
		"non_gray_samples": non_gray_samples,
		"center_bright_samples": center_bright_samples,
		"player_cyan_samples": player_cyan_samples,
	}


func _fail(message: String) -> void:
	push_error("WT_VALIDATION_G1_VISUAL_CAPTURE_FAIL: " + message)
	quit(1)
