# Safety Contract Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Advisory Principle & Operational Prohibitions

PLANT-X is strictly an advisory intelligence platform. Autonomous manipulation of industrial plant operations is strictly prohibited by software safety contracts.

### Prohibited Autonomous Actions
1. **`SHUTDOWN`**
2. **`SETPOINT_CHANGE`**
3. **`MAINTENANCE_EXECUTION`**
4. **`CHEMICAL_DOSING`**
5. **`VALVE_MANIPULATION`**
6. **`PROCESS_MANIPULATION`**

### Enforcement Mechanism
The `SafetyContract.validate_action()` validator raises a `SafetyViolationError` if any prohibited action lacks an explicit `human_approved=True` record signed by a verified operator.
