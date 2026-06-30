# G31 - Review bundle launch preflight

Status: complete when `WT_VALIDATION_G31_CONTRACT_PASS` and
`WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_SMOKE_PASS` both pass.

G31 proves the G30 review bundle can be copied and launched from the copied
artifact. It keeps the original bundle human-ready, disables human input only in
the automation launch copy, reimports the copied project from a clean Godot
cache, and launches through `project.godot`.

Exit:

- No human validation is requested until this gate passes;
- the source G30 bundle remains `human_input_enabled = true`;
- a separate launch copy is created under G31 artifacts;
- stale `.godot` import cache is removed from the launch copy before import;
- automation disables human input only in the launch copy;
- Godot import passes for the launch copy;
- Godot launches the copied bundle project with `--path`, not `--script`;
- the copied bundle reaches `WT_VALIDATION_PLAYTEST_READY` within the 30 second
  ready ceiling;
- the copied bundle launch logs no Godot errors;
- dense near-2K source/world files are not reintroduced.

Run:

```console
python tools/validate_g31_contract.py
python tools/g31_review_bundle_launch_preflight.py
```

Expected markers:

```text
WT_VALIDATION_G31_CONTRACT_PASS implementation=review_bundle_launch_preflight
WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_PASS profile=g19_compact_2k_on_demand engines=2 max_ready_seconds=... launch_copy_human_input=false source_bundle_human_input=true dense_world_files=0
WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_SMOKE_PASS engines=2 max_ready_seconds=... report=artifacts/g31_review_bundle_launch_preflight/g31_review_bundle_launch_preflight_report.json
```

Boundary:

- this proves copied-bundle launch readiness for review; it does not mean human
  approval, final terrain art, seamless dynamic LOD, water, biomes, vegetation,
  buildings, GPU compute, multiplayer, or a separate game repository is
  complete.
