extends RefCounted


static func add_status_overlay(parent: Node, initial_text: String) -> Label:
	var layer := CanvasLayer.new()
	layer.name = "ValidationStatusOverlay"
	parent.add_child(layer)
	var panel := PanelContainer.new()
	panel.name = "Panel"
	panel.set_anchors_preset(Control.PRESET_TOP_WIDE)
	panel.offset_left = 12.0
	panel.offset_top = 160.0
	panel.offset_right = -12.0
	panel.offset_bottom = 238.0
	layer.add_child(panel)
	var label := Label.new()
	label.name = "StatusLabel"
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.text = initial_text
	panel.add_child(label)
	return label


static func add_crosshair(parent: Node) -> CanvasLayer:
	var layer := CanvasLayer.new()
	layer.name = "ValidationCrosshair"
	parent.add_child(layer)
	var horizontal := _crosshair_rect("Horizontal", -9.0, -1.0, 9.0, 1.0)
	var vertical := _crosshair_rect("Vertical", -1.0, -9.0, 1.0, 9.0)
	layer.add_child(horizontal)
	layer.add_child(vertical)
	return layer


static func add_orientation_markers(parent: Node, viewer_position: Vector3) -> Node3D:
	var markers := Node3D.new()
	markers.name = "ValidationMarkers"
	parent.add_child(markers)
	_add_box_marker(markers, "AxisXRed", Vector3(8, 0.05, 0), Vector3(16, 0.1, 0.1), Color.RED)
	_add_box_marker(markers, "AxisYGreen", Vector3(0.05, 8, 0), Vector3(0.1, 16, 0.1), Color.GREEN)
	_add_box_marker(markers, "AxisZBlue", Vector3(0, 0.05, 8), Vector3(0.1, 0.1, 16), Color.BLUE)
	_add_box_marker(markers, "ViewerYellow", viewer_position, Vector3(0.8, 0.8, 0.8), Color.YELLOW)
	return markers


static func _crosshair_rect(name: String, left: float, top: float, right: float, bottom: float) -> ColorRect:
	var rect := ColorRect.new()
	rect.name = name
	rect.color = Color(1.0, 1.0, 1.0, 0.85)
	rect.set_anchors_preset(Control.PRESET_CENTER)
	rect.offset_left = left
	rect.offset_top = top
	rect.offset_right = right
	rect.offset_bottom = bottom
	return rect


static func _add_box_marker(parent: Node, marker_name: String, position: Vector3, size: Vector3, color: Color) -> void:
	var mesh := BoxMesh.new()
	mesh.size = size
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	var instance := MeshInstance3D.new()
	instance.name = marker_name
	instance.mesh = mesh
	instance.material_override = material
	instance.position = position
	parent.add_child(instance)
