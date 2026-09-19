# Intake Security Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Security Invariants & File Protection

`IntakeSecurityGuard` enforces file safety, preventing malicious file execution or system disruption.

### Enforced Limits
- **Max File Size:** 50 MB (`MAX_FILE_SIZE_BYTES`).
- **Path Traversal Protection:** Filenames containing `..`, `/`, or `\` raise `SecurityViolationError`.
- **Executable Blocking:** Prohibits `.exe`, `.sh`, `.bat`, `.cmd`, `.vbs`, `.js`, `.py`, `.dll`, `.so`.
- **Data Governance:** Uploaded files carry `training_eligible: False` by default.
