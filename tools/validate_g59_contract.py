#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G59_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/G59_VERSIONING_RELEASE_CONTRACT_QUALITY.md",
    "docs/VERSIONING_RELEASE_CONTRACT.md",
    "tools/g59_versioning_release_contract_quality.py",
    "tools/validate_g59_contract.py",
]

REQUIRED_PHRASES = {
    "docs/G59_VERSIONING_RELEASE_CONTRACT_QUALITY.md": (
        "WT_VALIDATION_G59_CONTRACT_PASS",
        "WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_PASS",
        "WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_SMOKE_PASS",
    ),
    "docs/VERSIONING_RELEASE_CONTRACT.md": (
        "## Versioning",
        "## Compatibility",
        "## Migration policy",
        "## License boundary",
        "## Source/reference policy",
        "## Release checklist",
        "Godot 4.6.3 stable",
        "Godot 4.7 stable",
        "MIT-licensed Transvoxel reference code",
    ),
    "tools/g59_versioning_release_contract_quality.py": (
        "WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_SMOKE_PASS",
        "VERSIONING_RELEASE_CONTRACT.md",
        "0BSD replacement backend is not the default",
    ),
    "README.md": (
        "G59 is the latest completed versioning release contract quality gate",
        "WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_SMOKE_PASS",
        "Next terrain work is G60 Terrain 1.0 release candidate quality",
    ),
    "docs/ROADMAP.md": (
        "## G59 - Versioning release contract quality",
        "WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_SMOKE_PASS",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G59",
        "The next milestone after G59 is G60",
        "G59 - Versioning release contract quality",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "Current claim boundary after G59",
        "G59 locked the versioning release contract",
        "immediate direction after G59 is G60",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G59 is the latest completed versioning release contract quality gate",
        "Next terrain work is G60 Terrain 1.0 release candidate quality",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G59 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G59 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text and phrase not in " ".join(text.split()):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".py", ".gd"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G59 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=versioning_release_contract_quality")


if __name__ == "__main__":
    main()
