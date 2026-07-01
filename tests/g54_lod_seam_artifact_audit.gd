extends RefCounted


var boundary_epsilon := 0.15
var boundary_match_distance := 2.25
var max_boundary_y_gap := 0.75
var max_triangle_edge := 40.0
var _last_error := ""


func get_last_error() -> String:
	return _last_error


func audit_render_meshes(terrain: Node, label: String) -> Dictionary:
	_last_error = ""
	var records: Array = []
	_collect_records(terrain, records)
	var lod0 := 0
	var lod1 := 0
	var triangles := 0
	var diagonal_edges := 0
	var max_edge := 0.0
	for record in records:
		lod0 += 1 if int(record["lod"]) == 0 else 0
		lod1 += 1 if int(record["lod"]) == 1 else 0
		var quality := _mesh_quality(record)
		if quality.is_empty():
			return _set_error("G54 invalid mesh quality at %s for %s" % [label, str(record["name"])])
		triangles += int(quality["triangles"])
		diagonal_edges += int(quality["diagonal_edges"])
		max_edge = max(max_edge, float(quality["max_edge"]))
	if lod0 <= 0 or lod1 <= 0 or triangles <= 0 or diagonal_edges <= 0 or max_edge > max_triangle_edge:
		return _set_error("G54 mesh topology invalid at %s lod0=%d lod1=%d triangles=%d diagonal_edges=%d max_edge=%.3f" % [label, lod0, lod1, triangles, diagonal_edges, max_edge])
	var seam := _audit_lod_seams(records)
	if seam.is_empty():
		return {}
	return {
		"lod0": lod0,
		"lod1": lod1,
		"triangles": triangles,
		"diagonal_edges": diagonal_edges,
		"seam_pairs": int(seam["pairs"]),
		"max_boundary_gap": float(seam["max_gap"]),
	}


func _collect_records(node: Node, records: Array) -> void:
	if node is MeshInstance3D:
		var instance := node as MeshInstance3D
		var parsed := _parse_render_name(str(instance.name))
		if not parsed.is_empty() and instance.visible and instance.mesh != null:
			records.append({
				"name": str(instance.name),
				"x": int(parsed["x"]), "y": int(parsed["y"]), "z": int(parsed["z"]), "lod": int(parsed["lod"]),
				"vertices": _world_vertices(instance),
				"indices": _mesh_indices(instance),
			})
	for child in node.get_children():
		if child is Node:
			_collect_records(child, records)


func _parse_render_name(name: String) -> Dictionary:
	if not name.begins_with("WT_Render_") or name.contains("_retiring_"):
		return {}
	var parts := name.substr(10).split("_L")
	if parts.size() != 2:
		return {}
	var coords := String(parts[0]).split("_")
	if coords.size() != 3:
		return {}
	return {"x": int(coords[0]), "y": int(coords[1]), "z": int(coords[2]), "lod": int(parts[1])}


func _world_vertices(instance: MeshInstance3D) -> Array[Vector3]:
	var output: Array[Vector3] = []
	for surface in range(instance.mesh.get_surface_count()):
		var arrays: Array = instance.mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		for vertex in vertices:
			output.append(instance.global_transform * vertex)
	return output


func _mesh_indices(instance: MeshInstance3D) -> PackedInt32Array:
	var output := PackedInt32Array()
	for surface in range(instance.mesh.get_surface_count()):
		var arrays: Array = instance.mesh.surface_get_arrays(surface)
		output.append_array(arrays[Mesh.ARRAY_INDEX])
	return output


func _mesh_quality(record: Dictionary) -> Dictionary:
	var vertices: Array = record["vertices"]
	var indices: PackedInt32Array = record["indices"]
	var max_edge := 0.0
	var diagonal_edges := 0
	for i in range(0, indices.size(), 3):
		if i + 2 >= indices.size():
			return {}
		var a: Vector3 = vertices[int(indices[i])]
		var b: Vector3 = vertices[int(indices[i + 1])]
		var c: Vector3 = vertices[int(indices[i + 2])]
		for edge in [[a, b], [b, c], [c, a]]:
			var delta: Vector3 = edge[0] - edge[1]
			var length := delta.length()
			if length <= 0.0001 or length > max_triangle_edge:
				return {}
			max_edge = max(max_edge, length)
			diagonal_edges += 1 if absf(delta.x) > 0.01 and absf(delta.z) > 0.01 else 0
	return {"triangles": indices.size() / 3, "diagonal_edges": diagonal_edges, "max_edge": max_edge}


func _audit_lod_seams(records: Array) -> Dictionary:
	var pairs := 0
	var max_gap := 0.0
	for a_index in range(records.size()):
		for b_index in range(a_index + 1, records.size()):
			var a: Dictionary = records[a_index]
			var b: Dictionary = records[b_index]
			if abs(int(a["lod"]) - int(b["lod"])) != 1:
				continue
			var seam := _horizontal_face_seam(a, b)
			if seam.is_empty():
				continue
			var gap := _boundary_y_gap(a, b, int(seam["axis"]), float(seam["boundary"]))
			if gap < 0.0 or gap > max_boundary_y_gap:
				return _set_error("G54 LOD boundary gap invalid: gap=%.4f seam=%s a=%s b=%s" % [gap, str(seam), str(a["name"]), str(b["name"])])
			pairs += 1
			max_gap = max(max_gap, gap)
	if pairs <= 0:
		return _set_error("G54 found no horizontal LOD seam pairs")
	return {"pairs": pairs, "max_gap": max_gap}


func _horizontal_face_seam(a: Dictionary, b: Dictionary) -> Dictionary:
	for axis in [0, 2]:
		var a_min := _bounds_min(a, axis)
		var a_max := _bounds_max(a, axis)
		var b_min := _bounds_min(b, axis)
		var b_max := _bounds_max(b, axis)
		var overlap_axis := 2 if axis == 0 else 0
		if absf(a_max - b_min) <= 0.001 and _bounds_overlap(a, b, 1) and _bounds_overlap(a, b, overlap_axis):
			return {"axis": axis, "boundary": a_max}
		if absf(b_max - a_min) <= 0.001 and _bounds_overlap(a, b, 1) and _bounds_overlap(a, b, overlap_axis):
			return {"axis": axis, "boundary": b_max}
	return {}


func _boundary_y_gap(a: Dictionary, b: Dictionary, axis: int, boundary: float) -> float:
	var av := _boundary_vertices(a, axis, boundary)
	var bv := _boundary_vertices(b, axis, boundary)
	if av.is_empty() or bv.is_empty():
		return -1.0
	var max_gap := 0.0
	for va in av:
		var best_distance := INF
		var best_gap := INF
		for vb in bv:
			var distance := absf((va.z if axis == 0 else va.x) - (vb.z if axis == 0 else vb.x))
			if distance < best_distance:
				best_distance = distance
				best_gap = absf(va.y - vb.y)
		if best_distance <= boundary_match_distance:
			max_gap = max(max_gap, best_gap)
	return max_gap


func _boundary_vertices(record: Dictionary, axis: int, boundary: float) -> Array[Vector3]:
	var output: Array[Vector3] = []
	for vertex in Array(record["vertices"]):
		if absf((vertex.x if axis == 0 else vertex.z) - boundary) <= boundary_epsilon:
			output.append(vertex)
	return output


func _extent(record: Dictionary) -> float:
	return 16.0 * pow(2.0, float(record["lod"]))


func _bounds_min(record: Dictionary, axis: int) -> float:
	var coordinate := int(record["x"] if axis == 0 else record["y"] if axis == 1 else record["z"])
	return float(coordinate) * _extent(record)


func _bounds_max(record: Dictionary, axis: int) -> float:
	return _bounds_min(record, axis) + _extent(record)


func _bounds_overlap(a: Dictionary, b: Dictionary, axis: int) -> bool:
	return min(_bounds_max(a, axis), _bounds_max(b, axis)) - max(_bounds_min(a, axis), _bounds_min(b, axis)) > 0.001


func _set_error(message: String) -> Dictionary:
	_last_error = message
	return {}
