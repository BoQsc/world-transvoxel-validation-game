# G18 - Production terrain budget pivot

Status: complete when `WT_VALIDATION_G18_CONTRACT_PASS` and
`WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS` both pass.

G18 changes the direction of the validation game after the G16/G17 stress run.
G16 proved that the active-window runtime can move across a near-2K generated
terrain without loading every chunk, but it also proved that dense pre-baked
world-source files are the wrong default architecture for a game.

G16 and G17 are stress-only evidence, not production terrain architecture.

Production/default terrain budgets:

- 100 MiB hard per-file ceiling for normal terrain/world files;
- 50 MiB target per-file ceiling for normal terrain/world files;
- 100 MiB hard base-world data ceiling before user edits;
- 30 seconds load-to-play ceiling;
- no normal game path may require raw dense source files;
- raw dense source files are transient stress artifacts only;
- large terrain must use deterministic-on-demand generation or compact
  seed/config plus edit journals;
- pre-baked dense fixtures may remain only as bounded regression/stress tests.

Exit:

- oversized dense G14/G16 artifacts are explicitly classified as stress-only;
- the repository has a guard that checks committed file sizes and budget policy;
- the roadmap no longer treats larger dense pre-baked fixtures as the next
  useful direction;
- ignored stress artifacts can be cleaned without deleting committed evidence.

Commands:

```console
python tools/validate_g18_contract.py
python tools/g18_world_budget_guard.py
python tools/cleanup_stress_artifacts.py
```

Optional local cleanup:

```console
python tools/cleanup_stress_artifacts.py --execute
```

Expected markers:

```text
WT_VALIDATION_G18_CONTRACT_PASS implementation=production_terrain_budget_pivot
WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS production_ready=false max_file_mb=100 target_file_mb=50 load_to_play_seconds=30 oversized_stress_artifacts=... report=artifacts/g18_world_budget_guard/g18_world_budget_guard_report.json
WT_VALIDATION_STRESS_ARTIFACT_CLEANUP_PASS executed=false reclaimable_mb=... removed_mb=0.00 report=artifacts/stress_artifact_cleanup/stress_artifact_cleanup_report.json
```
