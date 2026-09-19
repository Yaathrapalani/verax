# FOUL-X Live Audit Report

## Flow Verification
1. **Current Fouling State**: Displayed as $R_f = 0.00042 \text{ m}^2\text{K/W}$ (Threshold: $0.00080 \text{ m}^2\text{K/W}$).
2. **Forecast Curve**: RUL curve rendered via Canvas in `PlantProcessOverlay.tsx` showing predicted degradation trajectory over a 30-day horizon.
3. **Reliability Gate Status**:
   - Standard Regime: Displays `PASS` badge (Green).
   - OOD Triggered (+6σ Stress Test): Instantly transitions to `ABSTAIN` badge (Amber/Red) and sets `REGIME_OOD`.
4. **Fixed-Policy Fallback Verification**:
   - When Trust Gate is `ABSTAIN`, AI action recommendations are suppressed.
   - Interface clearly presents: `FIXED POLICY ACTIVE (180-day calendar maintenance interval)`.
   - **Critical Thesis Rule Verified**: A `FAILED AI GATE` does **NOT** generate an AI maintenance action; it explicitly falls back to the advisory fixed policy.
5. **Human Approval Barrier**:
   - All maintenance actions present an explicit `REQUIRE HUMAN APPROVAL` advisory barrier. No autonomous control or write commands are permitted.
