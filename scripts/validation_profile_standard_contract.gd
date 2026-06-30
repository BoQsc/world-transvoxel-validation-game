extends RefCounted

const ProfileCatalog := preload("res://scripts/validation_profile_catalog.gd")

const IMPLEMENTATION := "terrain_profile_standard_contract_v1"
const MAX_LOAD_TO_PLAY_SECONDS := 30.0
const TARGET_FILE_BYTES := 50 * 1024 * 1024
const MAX_FILE_BYTES := 100 * 1024 * 1024
const MAX_TOTAL_BYTES := 100 * 1024 * 1024


static func standard_profile_ids() -> Array[StringName]:
	return [
		&"flat_baseline",
		&"mountain_8x8",
		&"g19_compact_2k_on_demand",
		&"g50_seeded_procedural_2k",
	]


static func get_standard_summary() -> Dictionary:
	var profiles: Array[Dictionary] = []
	for profile_id in standard_profile_ids():
		profiles.append(profile_standard(profile_id))
	return {
		"implementation": IMPLEMENTATION,
		"terrain_1_0_gate": "G50",
		"profile_count": profiles.size(),
		"deterministic_profiles": _count_key(profiles, "deterministic", true),
		"budgeted_profiles": _count_key(profiles, "storage_budget_required", true),
		"load_budget_seconds": MAX_LOAD_TO_PLAY_SECONDS,
		"target_file_bytes": TARGET_FILE_BYTES,
		"max_file_bytes": MAX_FILE_BYTES,
		"max_total_bytes": MAX_TOTAL_BYTES,
		"profiles": profiles,
		"determinism_key": determinism_key(profiles),
	}


static func profile_standard(profile_id: StringName) -> Dictionary:
	var generation: Resource = ProfileCatalog.generation_profile(profile_id)
	var storage: Resource = ProfileCatalog.storage_profile(profile_id)
	var generation_summary := Dictionary(generation.call("get_contract_summary"))
	var storage_summary := Dictionary(storage.call("get_contract_summary"))
	return {
		"profile_id": str(profile_id),
		"standard_role": _standard_role(profile_id),
		"deterministic": true,
		"source_mode": str(generation_summary.get("source_mode", "")),
		"seed": int(generation_summary.get("seed", 0)),
		"source_revision": int(generation_summary.get("source_revision", 0)),
		"world_chunk_count_x": int(generation_summary.get("world_chunk_count_x", 0)),
		"world_chunk_count_z": int(generation_summary.get("world_chunk_count_z", 0)),
		"supports_underground_volume": bool(generation_summary.get("supports_underground_volume", false)),
		"storage_manifest": str(storage_summary.get("world_manifest_path", "")),
		"storage_root": str(storage_summary.get("object_root_path", "")),
		"storage_valid": bool(storage_summary.get("valid", false)),
		"expected_active_resources": ProfileCatalog.expected_resource_count(profile_id),
		"viewer_radius_chunks": ProfileCatalog.viewer_radius_chunks(profile_id),
		"fixture_label": ProfileCatalog.fixture_label(profile_id),
		"load_budget_seconds": MAX_LOAD_TO_PLAY_SECONDS,
		"target_file_bytes": TARGET_FILE_BYTES,
		"max_file_bytes": MAX_FILE_BYTES,
		"max_total_bytes": MAX_TOTAL_BYTES,
		"storage_budget_required": true,
		"generation": generation_summary,
		"storage": storage_summary,
		"determinism_key": _profile_determinism_key(generation_summary, storage_summary),
	}


static func validate_standard_summary(summary: Dictionary) -> Array[String]:
	var errors: Array[String] = []
	if str(summary.get("implementation", "")) != IMPLEMENTATION:
		errors.append("implementation mismatch")
	var profiles := Array(summary.get("profiles", []))
	if profiles.size() != standard_profile_ids().size():
		errors.append("standard profile count mismatch")
	var seen: Array[String] = []
	for profile in profiles:
		_validate_profile(Dictionary(profile), seen, errors)
	for profile_id in standard_profile_ids():
		if not seen.has(str(profile_id)):
			errors.append("missing standard profile: %s" % str(profile_id))
	return errors


static func determinism_key(profiles: Array[Dictionary]) -> String:
	var keys: Array[String] = []
	for profile in profiles:
		keys.append(str(profile.get("determinism_key", "")))
	keys.sort()
	return "|".join(keys)


static func _validate_profile(profile: Dictionary, seen: Array[String], errors: Array[String]) -> void:
	var profile_id := str(profile.get("profile_id", ""))
	seen.append(profile_id)
	if not bool(profile.get("deterministic", false)):
		errors.append("%s is not marked deterministic" % profile_id)
	if not bool(profile.get("storage_valid", false)):
		errors.append("%s storage profile is invalid" % profile_id)
	if int(profile.get("expected_active_resources", 0)) <= 0:
		errors.append("%s has no expected active-resource budget" % profile_id)
	if float(profile.get("load_budget_seconds", 0.0)) > MAX_LOAD_TO_PLAY_SECONDS:
		errors.append("%s load budget exceeds G50 ceiling" % profile_id)
	if str(profile.get("source_mode", "")) != _expected_source_mode(profile_id):
		errors.append("%s source mode mismatch" % profile_id)
	if profile_id == "g19_compact_2k_on_demand":
		_validate_procedural(profile, 19019, 190019, errors)
	elif profile_id == "g50_seeded_procedural_2k":
		_validate_procedural(profile, 50050, 50050, errors)


static func _validate_procedural(
	profile: Dictionary,
	expected_seed: int,
	expected_revision: int,
	errors: Array[String]
) -> void:
	var profile_id := str(profile.get("profile_id", ""))
	if int(profile.get("seed", 0)) != expected_seed:
		errors.append("%s seed mismatch" % profile_id)
	if int(profile.get("source_revision", 0)) != expected_revision:
		errors.append("%s source revision mismatch" % profile_id)
	if int(profile.get("world_chunk_count_x", 0)) != 128 or int(profile.get("world_chunk_count_z", 0)) != 128:
		errors.append("%s procedural chunk dimensions must be 128 by 128" % profile_id)
	if int(profile.get("expected_active_resources", 0)) != 25:
		errors.append("%s active-resource budget must be 25" % profile_id)
	if not str(profile.get("storage_manifest", "")).ends_with("procedural.wtseed"):
		errors.append("%s must use procedural descriptor storage semantics" % profile_id)


static func _expected_source_mode(profile_id: String) -> String:
	match profile_id:
		"flat_baseline":
			return "FLAT"
		"mountain_8x8":
			return "BAKED_WORLD"
		"g19_compact_2k_on_demand", "g50_seeded_procedural_2k":
			return "DETERMINISTIC_REFERENCE"
		_:
			return ""


static func _standard_role(profile_id: StringName) -> String:
	match str(profile_id):
		"flat_baseline":
			return "default_flat_baseline"
		"mountain_8x8":
			return "default_mountain_fixture"
		"g19_compact_2k_on_demand":
			return "compact_2k_on_demand"
		"g50_seeded_procedural_2k":
			return "seeded_procedural_2k"
		_:
			return "unknown"


static func _profile_determinism_key(generation: Dictionary, storage: Dictionary) -> String:
	return "%s:%s:%d:%d:%d:%d:%s" % [
		str(generation.get("profile_id", "")),
		str(generation.get("source_mode", "")),
		int(generation.get("seed", 0)),
		int(generation.get("source_revision", 0)),
		int(generation.get("world_chunk_count_x", 0)),
		int(generation.get("world_chunk_count_z", 0)),
		str(storage.get("world_manifest_path", "")),
	]


static func _count_key(profiles: Array[Dictionary], key: String, expected: Variant) -> int:
	var count := 0
	for profile in profiles:
		if profile.get(key) == expected:
			count += 1
	return count
