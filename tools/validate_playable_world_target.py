#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PHRASES = {
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "first-person player with crosshair",
        "flat terrain baseline",
        "mountain/large-terrain generation mode",
        "digging and placing",
        "textured terrain material path",
        "future game-world addon name is undecided",
        "GDScript limited to scene scaffolding",
    ),
    "docs/ROADMAP.md": (
        "## G2 - First-person playable baseline",
        "## G3 - Terrain generation modes",
        "## G4 - Terrain edit interaction",
        "## G5 - Material and performance baseline",
    ),
    "README.md": (
        "docs/PLAYABLE_WORLD_TARGET.md",
        "larger playable-world validation remains active",
        "python tools/validate_playable_world_target.py",
        "WT_VALIDATION_PLAYABLE_WORLD_TARGET_PASS",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing playable-world file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in phrases:
            if phrase not in text and phrase not in normalized:
                errors.append(f"{relative} missing phrase: {phrase}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_PLAYABLE_WORLD_TARGET_PASS next=g3_terrain_generation_modes")


if __name__ == "__main__":
    main()
