# Digital Shadow Audit Report

## UI Exposure Verification
1. **Asset Identity**: E-102 Crude/Preheat Shell-and-Tube Heat Exchanger clearly labeled with operational status.
2. **Measurements Exposure**: Live telemetry stream (inlet/outlet temperatures, mass flow rates, differential pressure $\Delta P$).
3. **Truth States**:
   - `OBSERVED`: Raw sensor telemetry (temperatures, pressure).
   - `SIMULATED`: Scenario counterfactual predictions.
   - `REPRESENTATIVE`: Economic estimation parameters.
   - `ASSUMED`: Ideal gas thermodynamic state bounds.
4. **Topology & Geometry**: 3D interactive viewport renders physical shell, tube bundle, baffles, and nozzles using React Three Fiber.
5. **Truth Source Boundary**:
   - The 3D viewport acts purely as a visual renderer (`UI_ONLY` representation).
   - The 3D scene is explicitly decoupled from data truth; physics calculations derive from backend engineering state.
