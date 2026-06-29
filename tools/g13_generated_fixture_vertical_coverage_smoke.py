#!/usr/bin/env python3

from __future__ import annotations

import json

from compose_validation_project import ROOT
from g11_generated_16x16_playable_streaming_smoke import (
    PROFILE_ID as G11_PROFILE_ID,
    SOURCE_REVISION as G11_SOURCE_REVISION,
    vertical_coverage as g11_vertical_coverage,
)
from g12_generated_32x32_playable_streaming_smoke import (
    PROFILE_ID as G12_PROFILE_ID,
    SOURCE_REVISION as G12_SOURCE_REVISION,
    vertical_coverage as g12_vertical_coverage,
)
from g14_generated_64x64_playable_streaming_smoke import (
    PROFILE_ID as G14_PROFILE_ID,
    SOURCE_REVISION as G14_SOURCE_REVISION,
    vertical_coverage as g14_vertical_coverage,
)
from generated_fixture_vertical_coverage import (
    ACTIVE_VERTICAL_MAX,
    ACTIVE_VERTICAL_MIN,
    REQUIRED_LOWER_MARGIN,
    REQUIRED_UPPER_MARGIN,
)


ARTIFACT_ROOT = ROOT / "artifacts" / "g13_generated_fixture_vertical_coverage"
MARKER = "WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS"


def main() -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    profiles = [
        {
            "profile": G11_PROFILE_ID,
            "source_revision": G11_SOURCE_REVISION,
            "coverage": g11_vertical_coverage(),
        },
        {
            "profile": G12_PROFILE_ID,
            "source_revision": G12_SOURCE_REVISION,
            "coverage": g12_vertical_coverage(),
        },
        {
            "profile": G14_PROFILE_ID,
            "source_revision": G14_SOURCE_REVISION,
            "coverage": g14_vertical_coverage(),
        },
    ]
    report_path = ARTIFACT_ROOT / "g13_generated_fixture_vertical_coverage_report.json"
    report_path.write_text(
        json.dumps(
            {
                "active_vertical_min_y": ACTIVE_VERTICAL_MIN,
                "active_vertical_max_y": ACTIVE_VERTICAL_MAX,
                "required_lower_margin": REQUIRED_LOWER_MARGIN,
                "required_upper_margin": REQUIRED_UPPER_MARGIN,
                "profiles": profiles,
                "implementation": "generated_fixture_vertical_coverage_guard",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{MARKER} profiles={len(profiles)} "
        f"active_y={ACTIVE_VERTICAL_MIN:.1f}..{ACTIVE_VERTICAL_MAX:.1f} "
        f"required_lower_margin={REQUIRED_LOWER_MARGIN:.2f} "
        f"required_upper_margin={REQUIRED_UPPER_MARGIN:.2f} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
