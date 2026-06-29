#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G18_PRODUCTION_TERRAIN_BUDGET_PIVOT.md",
    "tools/g18_world_budget_guard.py",
    "tools/cleanup_stress_artifacts.py",
    "tools/validate_g18_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G18_PRODUCTION_TERRAIN_BUDGET_PIVOT.md": (
        "WT_VALIDATION_G18_CONTRACT_PASS",
        "WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS",
        "G16 and G17 are stress-only evidence, not production terrain architecture",
        "100 MiB hard per-file ceiling",
        "50 MiB target per-file ceiling",
        "30 seconds load-to-play ceiling",
        "deterministic-on-demand generation",
        "compact seed/config plus edit journals",
    ),
    "tools/g18_world_budget_guard.py": (
        "WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS",
        "MAX_PRODUCTION_FILE_BYTES = 100 * 1024 * 1024",
        "TARGET_PRODUCTION_FILE_BYTES = 50 * 1024 * 1024",
        "MAX_LOAD_TO_PLAY_SECONDS = 30",
        "production_ready",
        "stress_only",
    ),
    "tools/cleanup_stress_artifacts.py": (
        "WT_VALIDATION_STRESS_ARTIFACT_CLEANUP_PASS",
        "CLEANUP_PATHS",
        "safe_resolve",
        "--execute",
    ),
    "README.md": (
        "G18 production budget pivot",
        "python tools/validate_g18_contract.py",
        "python tools/g18_world_budget_guard.py",
        "WT_VALIDATION_G18_CONTRACT_PASS",
        "WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G18 - Production terrain budget pivot",
        "WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS",
        "raw dense source files are transient stress artifacts only",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G18 file: {relative}")
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
    print("WT_VALIDATION_G18_CONTRACT_PASS implementation=production_terrain_budget_pivot")


if __name__ == "__main__":
    main()
