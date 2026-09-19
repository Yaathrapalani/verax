# Stage 1 — Intake Failure Modes

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Failure Modes & Handling

| Trigger | Handling | Result Status |
| :--- | :--- | :--- |
| **Path Traversal Attempt** | `IntakeSecurityGuard` raises `SecurityViolationError` | Security Exception |
| **Prohibited Executable** | `IntakeSecurityGuard` raises `SecurityViolationError` | Security Exception |
| **Unsupported Format** | Returns `ExtractionBundle` with `UNSUPPORTED_FORMAT` | Graceful Manifest Fallback |
| **Conflicting Source Claims** | `ConservativeEntityResolver` flags `CONFLICT` | Operator Review Required |
| **Unresolved Equipment Tag** | Anti-hallucination rule emits `UNRESOLVED` | `truth_state=UNRESOLVED` |
| **Ambiguous Unit String** | `UnitNormalizer` flags `UNIT_UNRESOLVED` | `unit_status=UNIT_UNRESOLVED` |
