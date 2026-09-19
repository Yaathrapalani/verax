# Simulation Workspace Specification

The Simulation Workspace supports Stage 9 What-If counterfactual analysis and Stage 14 Equipment Simulation.

## Components & Flow
- **Case Management**: Base Case vs Scenario Case comparison.
- **Inputs**: Mass flow rate slider, inlet temperature slider, fouling resistance adjustment.
- **Outputs**: Delta metrics ($\Delta Q$, $\Delta U$, $\Delta T$) with explicit `SIMULATED` truth state badges.
- **Validation Panel**: Mass and energy balance conservation checks ($Q_{\text{hot}} = Q_{\text{cold}}$ within tolerance).
