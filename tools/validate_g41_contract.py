#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G41_RUNTIME_FRAME_BUDGET_TELEMETRY_QUALITY.md",
    "tests/g41_runtime_frame_budget_telemetry_quality.gd",
    "tools/g41_runtime_frame_budget_telemetry_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G41_RUNTIME_FRAME_BUDGET_TELEMETRY_QUALITY.md": (
        "WT_VALIDATION_G41_CONTRACT_PASS",
        "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_PASS",
        "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_SMOKE_PASS",
        "runtime frame budget telemetry quality",
        "active runtime terrain quality gate",
    ),
    "tests/g41_runtime_frame_budget_telemetry_quality.gd": (
        "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_PASS",
        "MAX_AVG_FRAME_MS",
        "MAX_FRAME_SPIKE_MS",
        "TELEMETRY_PATH",
        "_record_frame",
        "_write_telemetry",
    ),
    "tools/g41_runtime_frame_budget_telemetry_quality.py": (
        "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_SMOKE_PASS",
        "runtime_frame_budget_telemetry_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G41 is the latest completed runtime frame budget telemetry quality gate",
        "python tools/g41_runtime_frame_budget_telemetry_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G41 - Runtime frame budget telemetry quality",
        "runtime frame budget telemetry quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G41 is the latest completed runtime frame budget telemetry quality gate",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "G41 - Runtime frame budget telemetry quality",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G41 file: {relative}")
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
        "tests/g41_runtime_frame_budget_telemetry_quality.gd",
        "tools/g41_runtime_frame_budget_telemetry_quality.py",
        "tools/validate_g41_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 360:
            errors.append(f"source file exceeds G41 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G41_CONTRACT_PASS implementation=runtime_frame_budget_telemetry_quality")


if __name__ == "__main__":
    main()
