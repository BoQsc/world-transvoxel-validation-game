extends RefCounted

var _ignore_mouse_button_frame := -1


func capture_if_enabled(enabled: bool) -> void:
	if enabled:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func handle_capture_event(event: InputEvent) -> bool:
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		return true
	if event is InputEventMouseButton and event.pressed and \
			Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		_ignore_mouse_button_frame = Engine.get_process_frames()
		return true
	return false


func should_ignore_mouse_button_event() -> bool:
	return Engine.get_process_frames() == _ignore_mouse_button_frame
