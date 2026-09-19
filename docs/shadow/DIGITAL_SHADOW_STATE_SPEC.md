# Digital Shadow State Specification

**Version:** 1.0.0  
**Status:** Approved Stage 3 Baseline  

---

## Digital Shadow Snapshot at T

`DigitalShadowSnapshot` answers: "What did PLANT-X know about this plant at T?"

### Key Attributes
- **`snapshot_id`**: Unique snapshot identifier.
- **`plant_id`**: Target facility identifier (`PLANT-01`).
- **`target_time`**: Evaluation timestamp $T$.
- **`asset_shadows`**: Dictionary of `AssetState` entities indexed by asset ID.
- **`topology`**: List of `TopologyRelation` process edges.
- **`temporal_state`**: Stage 2 `TemporalEvidenceState`.
- **`issues`**: List of structured `ShadowIssue` flags.
- **`provenance`**: `ShadowProvenance` metadata containing deterministic payload hash.
