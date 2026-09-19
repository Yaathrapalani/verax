# PLANT-X Voice Safety & Epistemic Boundaries

## 1. Safety Firewalls & Prohibitions

1. **Strict Separation of Interface from Truth**:
   - The voice agent is an interaction interface. It is NEVER the authority on thermodynamic models, fouling rates, or maintenance decisions.
   - LLMs or voice models are prohibited from directly mutating simulation states, generating arbitrary sensor values, or claiming predictive certainty when the reliability gate abstains.
2. **Industrial Control System Prohibitions**:
   - The voice interface cannot command real actuators, adjust physical valve setpoints, throttle pumps, or communicate with DCS/PLC networks without human physical sign-off and multi-layered hardware interlocks.
   - Any voice command requesting physical actuation is intercepted and rejected by the policy gateway as unauthorized.
3. **Epistemic Classification**:
   - Claims must be categorized according to the Epistemic Truth Hierarchy:
     - `OBSERVED`: Raw sensor telemetry.
     - `DERIVED`: Deterministic thermodynamics ($Q, U, R_f$).
     - `INFERRED`: FOUL-X predictive models.
     - `SIMULATED`: Counterfactual equipment runtime.
     - `REPRESENTATIVE`: Visual L4 procedural 3D geometry.
     - `UNAVAILABLE`: Missing physical telemetry or unmodeled fluid transport properties.
   - The Truth Firewall automatically blocks unauthorized escalation (e.g., preventing an inferred ML prediction from being displayed as an observed ground truth).
4. **Reliability Gate & Fixed-Policy Fallback**:
   - When operational conditions exhibit significant regime shift ($>3.0\sigma$) or high residual variance, the FOUL-X reliability gate issues `ABSTAIN`.
   - The voice assistant explicitly communicates this abstention to the operator: *"The forecast is available, but the reliability gate is not satisfied. The system is abstaining and falling back to the deterministic fixed cleaning policy."*

## 2. Privacy & Audio Capture Safeguards

- **Always Available, Never Silently Listening**: The microphone is only active when the operator explicitly clicks the microphone button, presses `Cmd+K`, or enters command mode.
- **Immediate Hardware Track Release**: Stopping or pausing voice closes all active browser `MediaStreamTrack`s immediately to turn off the hardware microphone indicator.
- **No Long-Term Audio Storage**: Raw audio buffers are processed in memory and discarded immediately; only transcribed commands and deterministic tool traces are retained in the immutable audit log.
