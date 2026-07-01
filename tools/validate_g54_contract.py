#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G54_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/G54_LOD_SEAM_ARTIFACT_QUALITY.md",
    "tests/g54_lod_seam_artifact_audit.gd",
    "tests/g54_lod_seam_artifact_quality.gd",
    "tools/g54_lod_seam_artifact_quality.py",
    "tools/validate_g54_contract.py",
]

REQUIRED_PHRASES = {
    "docs/G54_LOD_SEAM_ARTIFACT_QUALITY.md": (
        "WT_VALIDATION_G54_CONTRACT_PASS",
        "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_PASS",
        "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS",
        "mixed LOD transition fixture",
        "edited seam",
    ),
    "tests/g54_lod_seam_artifact_quality.gd": (
        "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_PASS",
        "transition.wtworld",
        "MAX_BOUNDARY_Y_GAP",
        "_submit_seam_edit",
    ),
    "tests/g54_lod_seam_artifact_audit.gd": (
        "_audit_lod_seams",
        "boundary_epsilon",
        "max_boundary_y_gap",
        "diagonal_edges",
    ),
    "tools/g54_lod_seam_artifact_quality.py": (
        "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS",
        "PRODUCTION_LOD_STREAMING_PASS",
        "transition.wtworld",
        "static_audit",
    ),
    "README.md": (
        "G54 is the latest completed LOD seam and artifact quality gate",
        "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS",
        "Next terrain work is G55 map generator budget quality",
    ),
    "docs/ROADMAP.md": (
        "## G54 - LOD seam and artifact quality",
        "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G54",
        "The next milestone after G54 is G55",
        "G54 - LOD seam and artifact quality",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "Current claim boundary after G54",
        "G54 locked mixed LOD seam and edited artifact behavior",
        "immediate direction after G54 is G55",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G54 is the latest completed LOD seam and artifact quality gate",
        "Next terrain work is G55 map generator budget quality",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G54 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G54 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".gd", ".py"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 380:
            errors.append(f"source file exceeds G54 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=lod_seam_artifact_quality")


if __name__ == "__main__":
    main()
