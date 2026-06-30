#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G5_MATERIAL_PERFORMANCE_BASELINE.md",
    "materials/validation_terrain_palette.gdshader",
    "scripts/validation_terrain_materials.gd",
    "tests/g5_material_performance_smoke.gd",
    "tools/g5_material_performance_smoke.py",
    "tools/validate_g5_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G5_MATERIAL_PERFORMANCE_BASELINE.md": (
        "WT_VALIDATION_G5_CONTRACT_PASS",
        "WT_VALIDATION_G5_SMOKE_PASS",
        "UV2.x",
        "GPU watts",
        "Not claimed",
    ),
    "materials/validation_terrain_palette.gdshader": (
        "shader_type spatial",
        "checker_texture",
        "UV2.x",
    ),
    "scripts/validation_terrain_materials.gd": (
        "validation_uv2_checker",
        "ImageTexture.create_from_image",
        "material_override",
    ),
    "tests/g5_material_performance_smoke.gd": (
        "WT_VALIDATION_G5_GODOT_PASS",
        "set_human_input_enabled(false)",
        "avg_ms",
        "max_ms",
        "colored_samples",
    ),
    "tools/g5_material_performance_smoke.py": (
        "WT_VALIDATION_G5_SMOKE_PASS",
        "nvidia-smi",
        "gpu_power_avg_watts",
    ),
    "README.md": (
        "python tools/validate_g5_contract.py",
        "python tools/g5_material_performance_smoke.py --windowed",
        "WT_VALIDATION_G5_CONTRACT_PASS",
        "WT_VALIDATION_G5_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G5 - Material and performance baseline",
        "Status: complete",
        "WT_VALIDATION_G5_SMOKE_PASS",
        "## G6 - Profile-selectable playable world",
        "Status: complete by `WT_VALIDATION_G6_CONTRACT_PASS`",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G5 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        rel = relative.as_posix()
        if ".git" in relative.parts or rel.startswith("artifacts/"):
            continue
        if path.is_file() and path.suffix in {".gd", ".py", ".gdshader"}:
            if len(path.read_text(encoding="utf-8", errors="replace").splitlines()) > 300:
                errors.append(f"source file exceeds G5 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        "WT_VALIDATION_G5_CONTRACT_PASS "
        "implementation=materialized_performance_baseline "
        "next=g6_profile_selectable_playable_world"
    )


if __name__ == "__main__":
    main()
