#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G20_COMPACT_TERRAIN_RESOLUTION.md",
    "tools/g20_compact_terrain_resolution.py",
    "tools/validate_g20_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G20_COMPACT_TERRAIN_RESOLUTION.md": (
        "WT_VALIDATION_G20_CONTRACT_PASS",
        "WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS",
        "dense source files",
        "baked dense world manifest",
        "unmeasured startup time",
        "g19_compact_2k_on_demand",
        "30 second load-to-play ceiling",
        "Still outside this resolution",
        "final terrain art quality",
        "GPU/compute generation",
    ),
    "tools/g20_compact_terrain_resolution.py": (
        "WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS",
        "G19_REPORT",
        "G18_REPORT",
        "compact_path_resolved=true",
        "MAX_GENERATED_FILE_BYTES = 50 * 1024 * 1024",
        "MAX_GENERATED_TOTAL_BYTES = 100 * 1024 * 1024",
        "MAX_LOAD_TO_PLAY_SECONDS = 30.0",
        "max_engine_ms",
    ),
    "README.md": (
        "G20 closes the compact terrain storage/load-shape issue",
        "30 second load-to-play ceiling",
        "python tools/validate_g20_contract.py",
        "python tools/g20_compact_terrain_resolution.py",
        "WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G20 - Compact terrain resolution gate",
        "WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS",
        "compact near-2K terrain storage/load-shape problem is resolved",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G20 closes the compact terrain storage/load-shape issue",
        "dense near-2K source/world-file problem is resolved",
        "explicit 30 second timing evidence",
        "not final terrain art",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G20 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G20_CONTRACT_PASS implementation=compact_terrain_resolution")


if __name__ == "__main__":
    main()
