#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G33_RUNTIME_TERRAIN_QUALITY_GATE.md",
    "tools/g33_runtime_terrain_quality_gate.py",
]

REQUIRED_PHRASES = {
    "docs/G33_RUNTIME_TERRAIN_QUALITY_GATE.md": (
        "WT_VALIDATION_G33_CONTRACT_PASS",
        "WT_VALIDATION_G33_RUNTIME_TERRAIN_QUALITY_PASS",
        "active runtime terrain quality gate",
        "not another human review package",
        "full 2048 by 2048 terrain visual coverage",
        "bounded 25-resource native detail window",
    ),
    "tools/g33_runtime_terrain_quality_gate.py": (
        "WT_VALIDATION_G33_RUNTIME_TERRAIN_QUALITY_PASS",
        "runtime_terrain_quality_gate",
        "MIN_FULL_MAP_COLORED_SAMPLES",
        "MAX_SCRIPT_SECONDS",
        "MAX_ACTIVE_RESOURCES",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G33 is the active runtime terrain quality gate",
        "python tools/g33_runtime_terrain_quality_gate.py",
        "not the active project direction",
    ),
    "docs/ROADMAP.md": (
        "## G33 - Runtime terrain quality gate",
        "active runtime terrain quality gate",
        "not another human review package",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G33 is the active runtime terrain quality gate",
        "quality gates are the active direction",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G33 file: {relative}")
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
    for rel in ("tools/g33_runtime_terrain_quality_gate.py", "tools/validate_g33_contract.py"):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G33 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G33_CONTRACT_PASS implementation=runtime_terrain_quality_gate")


if __name__ == "__main__":
    main()
