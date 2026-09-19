# Simulation Contract Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Process Simulation Adapter Contract

PLANT-X defines an adapter boundary to allow future third-party industrial process simulators (e.g. Aspen Plus, Aspen HYSYS, DWSIM, IDAES, Cantera) to project expected plant states.

### Adapter Interface Bounds
- **`input_mapping`**: Sensor and stream parameter mapping to simulation inlet/outlet blocks.
- **`simulation_request`**: Normalised job payload.
- **`result_normalization`**: Standardized converter transforming simulation results into `CanonicalExchangerState` or `Measurement` entities.
- **`assumptions`**: Documented thermodynamic property packages (e.g., Peng-Robinson, NRTL) and boundary conditions.
- **`validation_status`**: Convergence status flag.
