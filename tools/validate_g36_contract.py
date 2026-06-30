#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G36_COLD_IDLE_PERFORMANCE_QUALITY.md",
    "tests/g36_cold_idle_performance_quality.gd",
    "tools/g36_cold_idle_performance_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G36_COLD_IDLE_PERFORMANCE_QUALITY.md": (
        "WT_VALIDATION_G36_CONTRACT_PASS",
        "WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_PASS",
        "WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_SMOKE_PASS",
        "cold-idle performance stability",
        "active runtime terrain quality gate",
    ),
    "tests/g36_cold_idle_performance_quality.gd": (
        "WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_PASS",
        "IDLE_FRAMES",
        "viewer_update_delta",
        "material_auto_apply_delta",
        "_audit_idle_window",
    ),
    "tools/g36_cold_idle_performance_quality.py": (
        "WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_SMOKE_PASS",
        "cold_idle_performance_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G36 is the active cold-idle performance quality gate",
        "python tools/g36_cold_idle_performance_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G36 - Cold idle performance quality",
        "cold-idle performance stability",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G36 is the active cold-idle performance quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G36 file: {relative}")
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
    for rel in (
        "tests/g36_cold_idle_performance_quality.gd",
        "tools/g36_cold_idle_performance_quality.py",
        "tools/validate_g36_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 320:
            errors.append(f"source file exceeds G36 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G36_CONTRACT_PASS implementation=cold_idle_performance_quality")


if __name__ == "__main__":
    main()
