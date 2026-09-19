# Engineering Inspector Specification

The `EngineeringInspector` resides in the right-hand panel of the workstation shell.

## Inspector Tabs & Content
1. **Identity**: Tag (`E-102`), Name (`Kerosene Exchanger`), Type (`SHELL_AND_TUBE`), Unit (`CRUDE_PREHEAT_TRAIN_1`).
2. **State & Measurements**: $T_{\text{in}}$, $T_{\text{out}}$, $P_{\text{in}}$, $P_{\text{out}}$, $\dot{m}$, with truth badges (`OBSERVED`, `DERIVED`).
3. **Performance**: Duty $Q$, LMTD, $UA$, $R_f$, $Q_{\text{discrepancy}}$.
4. **Fouling & FOUL-X**: Current $R_f$, threshold, RUL, Trust Gate status (`PASS` / `ABSTAIN`), Fixed Policy state.
5. **Thermodynamics**: Property package (`IDEAL_GAS`), EOS status (`UNSUPPORTED`), Phase (`VAPOR/GAS`), Transport status (`UNAVAILABLE`).
6. **Evidence**: Linked hypotheses, supporting/contradicting metrics, "Trace Why" trigger.
7. **Provenance**: SHA-256 data hash, timestamp, record ID.
