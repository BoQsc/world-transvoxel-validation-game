#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_PRODUCTION_GAP_AUDIT_PASS"

REQUIRED_PHRASES = {
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "automated validation-grade compact 2K terrain runtime, not production-ready large-world terrain",
        "Expected final world/terrain target",
        "Proven by the current validation track",
        "Not production-ready yet",
        "Runtime frame budget telemetry is not yet a production performance contract",
        "Player collision traversal is not yet a long-route stability contract",
        "Human-facing playable view distance is not yet a production presentation contract",
        "The public terrain addon API is not yet locked as a game-facing contract",
        "The material/texture pipeline is not yet production quality",
        "Storage/recovery is not yet a long-term schema contract",
        "Gap closure ladder",
        "G41 - Runtime frame budget telemetry quality",
        "G42 - Collision traversal stability quality",
        "G43 - Terrain addon API contract quality",
        "G44 - Material texture pipeline quality",
        "G45 - Storage recovery schema quality",
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
    print(f"{MARKER} next=runtime_frame_budget_telemetry_quality")


if __name__ == "__main__":
    main()
