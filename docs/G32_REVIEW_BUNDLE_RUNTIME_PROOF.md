# G32 - Review bundle runtime proof

Status: complete when `WT_VALIDATION_G32_CONTRACT_PASS` and
`WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_SMOKE_PASS` both pass.

G32 is the exact review-bundle autonomous runtime proof. It does not ask for
human validation. It copies the G30 review bundle, disables human input only in
the automation copy, imports that copied project, and runs the existing
large-terrain runtime proofs from inside the copied bundle.

Exit:

- No human validation is requested until this gate passes;
- this is the exact review-bundle autonomous runtime proof gate;
- the source G30 bundle remains `human_input_enabled = true`;
- `bundle_runtime_copy` is created as a separate automation runtime copy;
- stale Godot import cache from the runtime copy is removed before import;
- automation disables human input only in the runtime copy;
- Godot import passes for the runtime copy;
- G25 full-terrain visual baseline passes from the runtime copy;
- G26 full-terrain playable experience passes from the runtime copy;
- G27 full-terrain handoff preflight passes from the runtime copy;
- runtime proof captures and logs are copied into G32 evidence;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G32 proves that the current review bundle can autonomously reproduce the
  full-terrain visual, first-person route, material stability, and edit/runtime
  checks. It does not claim human approval, final terrain art, seamless dynamic
  LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

Run:

```console
python tools/g32_review_bundle_runtime_proof.py
```

Expected markers:

```text
WT_VALIDATION_G32_CONTRACT_PASS implementation=review_bundle_runtime_proof
WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_PASS profile=g19_compact_2k_on_demand engines=... scripts=... exact_review_bundle=true g25=true g26=true g27=true map_blocks=2048 max_script_seconds=... runtime_copy_human_input=false source_bundle_human_input=true dense_world_files=0
WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_SMOKE_PASS engines=... scripts=... max_script_seconds=... report=artifacts/g32_review_bundle_runtime_proof/g32_review_bundle_runtime_proof_report.json
```
