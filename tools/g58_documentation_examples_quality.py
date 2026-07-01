#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from compose_validation_project import REPOSITORY_ROOT, ROOT


ARTIFACT_ROOT = ROOT / "artifacts" / "g58_documentation_examples_quality"
MARKER = "WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS"
EXAMPLES = ROOT / "docs" / "TERRAIN_ADOPTION_EXAMPLES.md"
INTEGRATION_README = REPOSITORY_ROOT / "world-transvoxel-integration-game" / "README.md"
SECTIONS = (
    "## Installation",
    "## Profile setup",
    "## Terrain editing",
    "## Storage",
    "## Telemetry",
    "## Troubleshooting",
)
REQUIRED_PHRASES = (
    "world_transvoxel",
    "world_transvoxel_terrain",
    "world_transvoxel_game_world",
    "configure_game_world",
    "submit_sphere_edit",
    "get_game_world_summary",
    "WtTerrainGenerationProfile",
    "WtTerrainStorageProfile",
    "res://build/<game>/<profile>/",
    "WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS",
)


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"missing documentation file: {path}")
    return path.read_text(encoding="utf-8")


def audit_text() -> dict[str, object]:
    text = read(EXAMPLES)
    missing = [section for section in SECTIONS if section not in text]
    missing += [phrase for phrase in REQUIRED_PHRASES if not normalized_contains(text, phrase)]
    forbidden = [phrase for phrase in ("TODO", "TBD", "figure out later") if phrase in text]
    if missing or forbidden:
        raise RuntimeError(f"G58 examples invalid missing={missing} forbidden={forbidden}")
    code_blocks = text.count("```")
    if code_blocks < 8 or "|" not in text:
        raise RuntimeError("G58 examples need code blocks and troubleshooting table")
    readme_text = read(INTEGRATION_README)
    for section in SECTIONS:
        if section not in readme_text:
            raise RuntimeError(f"integration README missing section: {section}")
    if "world-transvoxel-validation-game" in readme_text:
        raise RuntimeError("integration README must not name validation-game internals")
    return {
        "sections": len(SECTIONS),
        "code_blocks": code_blocks,
        "integration_readme": True,
        "examples": str(EXAMPLES),
        "integration_readme_path": str(INTEGRATION_README),
    }


def main() -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = audit_text()
    report_path = ARTIFACT_ROOT / "g58_documentation_examples_quality_report.json"
    report_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} sections={audit['sections']} code_blocks={audit['code_blocks']} "
        "integration_readme=1"
    )
    print(
        f"{SUMMARY_MARKER} sections={audit['sections']} code_blocks={audit['code_blocks']} "
        f"integration_readme=1 report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
