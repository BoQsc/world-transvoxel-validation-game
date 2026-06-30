# G30 - Compact 2K review bundle

Status: complete when `WT_VALIDATION_G30_CONTRACT_PASS` and
`WT_VALIDATION_G30_COMPACT_2K_REVIEW_BUNDLE_PASS` both pass.

G30 packages the human-ready compact 2K handoff into a review bundle. G29
creates the project; G30 makes the evidence easier to audit by copying the
human-ready project, prerequisite reports, Godot logs, hashes, and review index
into one artifact directory.

Exit:

- No human validation is requested until this gate passes;
- `project/project.godot` exists inside the bundle;
- bundled project is pinned to `g19_compact_2k_on_demand`;
- bundled project keeps `human_input_enabled = true`;
- bundled `project/HUMAN_REVIEW.md` exists;
- `REVIEW_INDEX.md` describes what to open and where evidence lives;
- `HANDOFF_MANIFEST.json` records source commits, SHA-256 hashes, project
  budget, evidence budget, and prerequisite evidence files;
- G27, G28, and G29 reports/logs are copied into `evidence/`;
- dense near-2K source/world files are not reintroduced.

Run:

```console
python tools/validate_g30_contract.py
python tools/g30_compact_2k_review_bundle.py
```

Expected markers:

```text
WT_VALIDATION_G30_CONTRACT_PASS implementation=compact_2k_review_bundle
WT_VALIDATION_G30_COMPACT_2K_REVIEW_BUNDLE_PASS profile=g19_compact_2k_on_demand project=project/project.godot manifest=HANDOFF_MANIFEST.json index=REVIEW_INDEX.md evidence_files=... project_files=... total_bytes=... dense_world_files=0
```

Boundary:

- this prepares an auditable review bundle; it does not mean human approval,
  final terrain art, seamless dynamic LOD, water, biomes, vegetation, buildings,
  GPU compute, multiplayer, or a separate game repository is complete.
