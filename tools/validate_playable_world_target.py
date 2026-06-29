#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PHRASES = {
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "first-person player with crosshair",
        "flat terrain baseline",
        "mountain/8 by 8 multi-chunk generation mode",
        "digging and placing",
        "textured terrain material path",
        "future game-world addon name is undecided",
        "GDScript limited to scene scaffolding",
        "Map scale vocabulary",
        "2000×2000",
        "2000 blocks by 2000 blocks",
        "1 block = 1 meter",
        "4,000,000 m²",
        "4 km²",
        "93 active sparse path resources",
        "single-viewer playable streaming with a 25-resource active window",
        "dense generated 16 by 16 fixture with 256 generated pages",
    ),
    "docs/ROADMAP.md": (
        "## G2 - First-person playable baseline",
        "## G3 - Terrain generation modes",
        "## G4 - Terrain edit interaction",
        "## G5 - Material and performance baseline",
        "## G6 - Profile-selectable playable world",
        "## G7 - Human visual verification",
        "## G8 - 2000×2000 bounded streaming",
        "## G9 - Sparse 2K playable profile",
        "## G10 - Single-viewer 2K playable streaming",
        "## G11 - Generated 16x16 playable streaming",
    ),
    "README.md": (
        "docs/PLAYABLE_WORLD_TARGET.md",
        "G7 human visual verification handoff is reproducible",
        "final human profile review remains pending",
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
    print("WT_VALIDATION_PLAYABLE_WORLD_TARGET_PASS next=human_visual_verification")


if __name__ == "__main__":
    main()
