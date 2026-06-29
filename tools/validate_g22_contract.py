#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G22_EXACT_COMPACT_HANDOFF_RUNTIME_PROOF.md",
    "tools/g22_exact_compact_handoff_runtime_proof.py",
    "tools/validate_g22_contract.py",
    "tests/g22_exact_compact_handoff_runtime_proof.gd",
    "tests/g22_exact_compact_handoff_runtime_proof.gd.uid",
    "tests/g22_exact_compact_handoff_runtime_helpers.gd",
    "tests/g22_exact_compact_handoff_runtime_helpers.gd.uid",
)

REQUIRED_PHRASES = {
    "docs/G22_EXACT_COMPACT_HANDOFF_RUNTIME_PROOF.md": (
        "WT_VALIDATION_G22_CONTRACT_PASS",
        "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_PASS",
        "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS",
        "same G21 compact handoff path",
        "human input from startup",
        "carve, and construct/place",
        "render_fading_resources = 0",
        "pending_chunk_retirements = 0",
        "25-resource budget",
    ),
    "tools/g22_exact_compact_handoff_runtime_proof.py": (
        "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS",
        "prepare_project",
        "assert_compact_project_budget",
        "MAX_LOAD_TO_PLAY_SECONDS = 30.0",
        "capture_count",
        "exact_compact_handoff_runtime_proof",
    ),
    "tests/g22_exact_compact_handoff_runtime_proof.gd": (
        "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_PASS",
        "g22_exact_compact_handoff_runtime_helpers.gd",
        "set_human_input_enabled(false)",
        "capture_oblique",
        "verify_carve_and_construct",
        "dense_world_files=0",
    ),
    "tests/g22_exact_compact_handoff_runtime_helpers.gd": (
        "PROFILE_ID := &\"g19_compact_2k_on_demand\"",
        "submit_sphere_edit",
        "&\"construct\"",
        "render_fading_resources",
        "pending_chunk_retirements",
    ),
    "README.md": (
        "G22 runs the exact compact G21 handoff project",
        "python tools/validate_g22_contract.py",
        "python tools/g22_exact_compact_handoff_runtime_proof.py --skip-build",
        "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G22 - Exact compact handoff runtime proof",
        "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS",
        "origin, center, and far-corner",
        "render_fading_resources = 0",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G22 runs the exact compact G21 handoff project",
        "automated PNG evidence",
        "carve and construct/place",
        "does not claim final terrain art",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G22 file: {relative}")
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
    for relative in REQUIRED_FILES:
        if relative.endswith((".py", ".gd")):
            path = ROOT / relative
            if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
                errors.append(f"source file exceeds G22 line limit: {relative}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G22_CONTRACT_PASS implementation=exact_compact_handoff_runtime_proof")


if __name__ == "__main__":
    main()
