# G60 - Terrain 1.0 release candidate quality

Status: complete when `WT_VALIDATION_G60_CONTRACT_PASS` and
`WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_SMOKE_PASS` both pass.

G60 is the Terrain 1.0 finish line. It runs the bounded G41-G59 release
candidate suite and requires zero known critical blockers.

Passing G60 means Terrain 1.0 release-candidate quality is reached for the
validated compact 2K terrain stack. It does not claim post-1.0 systems such as
water, lava, vegetation, voxel buildings, planets, multiplayer, massive worlds
beyond the compact 2K target, or compute/GPU acceleration.

Expected release-candidate marker:

```text
WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_PASS validators=22 runtime_gates=19 critical_blockers=0
```

Expected smoke marker:

```text
WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_SMOKE_PASS validators=22 runtime_gates=19 critical_blockers=0 report=artifacts/g60_terrain_1_0_release_candidate_quality/g60_terrain_1_0_release_candidate_quality_report.json
```

Validator marker:

```text
WT_VALIDATION_G60_CONTRACT_PASS implementation=terrain_1_0_release_candidate_quality
```
