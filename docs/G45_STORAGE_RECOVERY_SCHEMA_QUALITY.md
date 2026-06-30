# G45 - Storage recovery schema quality

Status: complete when `WT_VALIDATION_G45_CONTRACT_PASS` and
`WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_SMOKE_PASS` both pass.

G45 is the runtime terrain quality gate for storage recovery schema
quality. It verifies the validation-game storage path through real backend
storage behavior instead of only documenting intended persistence semantics.

Exit:

- the compact 2K procedural profile uses a compact descriptor plus `world.wtedit`
  journal path, not dense near-2K world files;
- the storage profile exposes journal format version `1` and persistent edits;
- the physical journal starts with the schema-1 `WTEDIT` container header and the
  expected source revision;
- at least three compact 2K edits commit, reload, and replay from the journal;
- a simulated interrupted write appends a truncated `WTEDIT` tail, then reopening
  the world recovers by truncating to the last complete transaction prefix;
- `WtTerrainWorld` exposes game-facing snapshot request wrappers instead of
  requiring validation code to call the backend directly;
- the existing sparse 2K baked fixture writes a side-by-side compacted world
  snapshot, reopens it, and verifies the edited authoritative sample;
- compacted output starts without a carried edit journal because the edit state is
  baked into the new source revision;
- active resources return to the 25-resource compact detail window;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G45 proves compact 2K journal/reload/truncated-tail recovery and proves
  compaction/reopen through the existing sparse 2K baked fixture. It does not
  claim final save UI, cloud sync, massive world compaction, procedural-world
  compaction, public terrain API stability, materials/textures, LOD seam quality,
  water, vegetation, buildings, multiplayer, or a separate game repository.

Run:

```console
python tools/g45_storage_recovery_schema_quality.py
```

Expected markers:

```text
WT_VALIDATION_G45_CONTRACT_PASS implementation=storage_recovery_schema_quality
WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_PASS profile=g19_compact_2k_on_demand compact_2k_edits=3 compact_2k_replayed=3 compact_2k_recovered=3 journal_magic=WTEDIT journal_format_version=1 journal_source_revision=190019 journal_bytes=... truncated_tail_bytes=... recovery_truncated_to_bytes=... compaction_profile=g8_sparse_2k compacted_pages=93 compacted_source_revision=8102 compacted_world_revision=... compacted_reopened=1 compacted_journal_exists=false max_render_resources=25 max_collision_resources=25 max_active_records=25 dense_world_files=0
WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... compact_2k_edits=3 compact_2k_replayed=3 compact_2k_recovered=3 compaction_profile=g8_sparse_2k compacted_pages=93 compacted_reopened=1 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g45_storage_recovery_schema_quality/g45_storage_recovery_schema_quality_report.json
```
