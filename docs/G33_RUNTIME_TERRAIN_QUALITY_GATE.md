# G33 - Runtime terrain quality gate

Status: complete when `WT_VALIDATION_G33_CONTRACT_PASS` and
`WT_VALIDATION_G33_RUNTIME_TERRAIN_QUALITY_PASS` both pass.

G33 is the active runtime terrain quality gate. It is not another human review
package. It audits the G32 exact-bundle runtime evidence and rejects the project
if the terrain evidence does not meet concrete runtime-quality thresholds.

Exit:

- this is the active runtime terrain quality gate;
- this is not another human review package;
- G32 exact review-bundle runtime proof exists and uses the compact 2K profile;
- G25 evidence proves full 2048 by 2048 terrain visual coverage;
- G25 evidence proves visible colored terrain samples in the full-map capture;
- G26 evidence proves first-person playable route captures and player-driven
  streaming updates;
- G27 evidence proves material application, first-person captures, local edit
  commit behavior, and automation-safe input;
- every runtime script stays below the 30 second quality ceiling;
- every runtime check keeps the bounded 25-resource native detail window;
- copied PNG evidence exists on disk and is non-empty;
- generated compact storage remains below the 50 MB file and 100 MB total
  terrain budget;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G33 is a baseline quality gate for the current CPU/native addon path. It does
  not claim final terrain art, seamless dynamic LOD, GPU/compute generation,
  fluids, biomes, vegetation, buildings, multiplayer, or a separate game
  repository.

Run:

```console
python tools/g33_runtime_terrain_quality_gate.py
```

Expected markers:

```text
WT_VALIDATION_G33_CONTRACT_PASS implementation=runtime_terrain_quality_gate
WT_VALIDATION_G33_RUNTIME_TERRAIN_QUALITY_PASS profile=g19_compact_2k_on_demand engines=... g25=... g26=... g27=... map_blocks=2048 max_active_resources=25 max_script_seconds=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g33_runtime_terrain_quality_gate/g33_runtime_terrain_quality_gate_report.json
```
