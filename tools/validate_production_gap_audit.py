#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_PRODUCTION_GAP_AUDIT_PASS"

REQUIRED_PHRASES = {
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "automated validation-grade compact 2K terrain runtime",
        "Expected final world/terrain target",
        "Proven by the current validation track",
        "Not production-ready yet",
        "minimal public terrain addon API contract",
        "addon-owned material applicator and mesh-stats helpers",
        "native hot-path boundary evidence",
        "G48 locked the native hot-path boundary",
        "debug telemetry UI evidence",
        "G49 added a normal-scene debug telemetry",
        "terrain profile standard evidence",
        "G50 locked the terrain profile standard",
        "material texture pipeline evidence",
        "G51 locked the material texture pipeline",
        "underground density/material variation evidence",
        "G52 locked baseline underground",
        "configurable streaming radius evidence",
        "G53 locked configurable streaming radius behavior",
        "mixed LOD seam/artifact evidence",
        "G54 locked mixed LOD seam",
        "map-generator budget evidence",
        "G55 locked map generator budget behavior",
        "game-world addon prototype evidence",
        "G56 locked the game-world addon prototype boundary",
        "separate game repository integration evidence",
        "G57 locked separate game repository integration",
        "World generation is not yet the final game-world generator",
        "documentation examples quality",
        "Gap closure ladder",
        "finite production roadmap",
        "Terrain 1.0",
        "G60",
        "G41 - Runtime frame budget telemetry quality",
        "G42 - Collision traversal stability quality",
        "G43 - View distance presentation quality",
        "G44 - Edit policy and shape quality",
        "G45 - Storage recovery schema quality",
        "G46 - Terrain addon API contract quality",
        "world-transvoxel",
        "world-transvoxel-terrain",
        "validation game",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "production world/terrain gap audit",
        "automated validation-grade compact 2K terrain runtime",
        "runtime frame budget telemetry quality",
    ),
    "README.md": (
        "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md",
        "docs/FINITE_PRODUCTION_ROADMAP.md",
        "automated validation-grade compact 2K terrain runtime",
        "python tools/validate_production_gap_audit.py",
        "WT_VALIDATION_PRODUCTION_GAP_AUDIT_PASS",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing production gap audit file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(f"{MARKER} next=documentation_examples_quality")


if __name__ == "__main__":
    main()
