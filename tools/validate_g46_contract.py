#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERRAIN_ROOT = ROOT.parent / "world-transvoxel-terrain"

REQUIRED_FILES = [
    "docs/G46_TERRAIN_ADDON_API_CONTRACT_QUALITY.md",
    "tests/g46_terrain_addon_api_contract_quality.gd",
    "tools/g46_terrain_addon_api_contract_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G46_TERRAIN_ADDON_API_CONTRACT_QUALITY.md": (
        "WT_VALIDATION_G46_CONTRACT_PASS",
        "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_PASS",
        "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_SMOKE_PASS",
        "terrain addon API contract quality",
        "direct backend calls",
    ),
    "tests/g46_terrain_addon_api_contract_quality.gd": (
        "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_PASS",
        "get_terrain_api_contract_summary",
        "request_authoritative_sample",
        "request_authoritative_samples",
        "direct_backend_calls=0",
    ),
    "tools/g46_terrain_addon_api_contract_quality.py": (
        "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_SMOKE_PASS",
        "terrain_addon_api_contract_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G46 is the latest completed terrain addon API contract quality gate",
        "python tools/g46_terrain_addon_api_contract_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G46 - Terrain addon API contract quality",
        "Terrain addon API contract quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G46 is the latest completed terrain addon API contract quality gate",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G46",
        "The next milestone after G46 is G47",
    ),
}

TERRAIN_REQUIRED_PHRASES = (
    "func start_world()",
    "func get_world_revision()",
    "func get_world_page_count()",
    "func request_authoritative_sample",
    "func request_authoritative_samples",
    "func get_terrain_api_contract_summary()",
    "terrain_addon_api_contract_v1",
)


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G46 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in phrases:
            if phrase not in text and phrase not in normalized:
                errors.append(f"{relative} missing phrase: {phrase}")
    terrain_world = TERRAIN_ROOT / "addons/world_transvoxel_terrain/runtime/wt_terrain_world.gd"
    if not terrain_world.is_file():
        errors.append(f"missing terrain addon API file: {terrain_world}")
    else:
        text = terrain_world.read_text(encoding="utf-8")
        for phrase in TERRAIN_REQUIRED_PHRASES:
            if phrase not in text:
                errors.append(f"terrain addon API missing phrase: {phrase}")
    test_text = (ROOT / "tests/g46_terrain_addon_api_contract_quality.gd").read_text(encoding="utf-8")
    for forbidden in ("get_backend_terrain", "request_world_compaction("):
        if forbidden in test_text:
            errors.append(f"G46 public-path test contains forbidden direct/internal call: {forbidden}")
    for rel in (
        "tests/g46_terrain_addon_api_contract_quality.gd",
        "tools/g46_terrain_addon_api_contract_quality.py",
        "tools/validate_g46_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G46 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G46_CONTRACT_PASS implementation=terrain_addon_api_contract_quality")


if __name__ == "__main__":
    main()
