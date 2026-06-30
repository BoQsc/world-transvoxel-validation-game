# Active track guardrails

The active project direction is runtime terrain quality. Human-visible review is
a final sanity check, not the active project direction.

These guardrails exist to prevent another drift into repeated review, handoff,
bundle, or launch-packaging milestones.

## Non-drift rules

- Post-G33 milestones must not be review, handoff, package, bundle, launch, or
  human-review milestones.
- Post-G33 milestones must improve measured terrain behavior, terrain
  correctness, edit latency or persistence, material quality, performance,
  storage, collision, streaming, LOD behavior, or addon API stability.
- Every new milestone must name its evidence command, expected marker, concrete
  thresholds, and failure boundary.
- A human-visible sanity check can remain available, but it must not replace
  automated terrain evidence.
- If a packaging or launch issue appears, fix it inside the current terrain
  quality milestone unless it blocks all runtime evidence.
- Do not add fluids, vegetation, buildings, multiplayer, planets, or GPU compute
  as active work before the terrain quality gate for the current CPU/native path
  remains stable.

## Preferred next milestone families

- edit latency and edit persistence;
- terrain correctness and artifact detection;
- material/texture quality with measured runtime cost;
- cold-idle and performance-budget stability;
- addon public API stability for game use;
- LOD/streaming correctness and popping detection.

Run:

```console
python tools/validate_active_track_guardrails.py
```

Expected marker:

```text
WT_VALIDATION_ACTIVE_TRACK_GUARDRAILS_PASS active=runtime_terrain_quality post_g33_review_milestones=0
```
