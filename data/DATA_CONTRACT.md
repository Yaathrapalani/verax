# FOUL-X M1-B Data Contract Specification

**Contract Version:** 1.1 (M1-B Correction)  
**Effective Date:** 2026-09-16  

## 1. Primary Ingestion Schema

### 1.1 Time Variable (`TIME`)
- `Time_hr`: Continuous hourly simulation timestamp ($t \in [0.0, 63999.0]$).

### 1.2 Measured Input Variables (`MEASURED_INPUT`)
- **Global Crude Properties**:
  - `Crude_API`: Inlet crude API gravity.
  - `Crude_Chlorides`: Inlet crude chloride content (ppm).
  - `Crude_TAN`: Inlet crude Total Acid Number (mg KOH/g).
- **Per-Exchanger Sensor Measurements** (for Exchangers `E01`, `E02`, `E03`, `E04`, `E05`):
  - `[HEx]_Crude_Tube_T_In_degC`: Measured crude tube inlet temperature (°C).
  - `[HEx]_Crude_Tube_T_Out_degC`: Measured crude tube outlet temperature (°C).
  - `[HEx]_Crude_Tube_m_kg_s`: Measured crude tube mass flow rate (kg/s).
  - `[HEx]_[Product]_Shell_T_In_degC`: Measured shell inlet temperature (°C).
  - `[HEx]_[Product]_Shell_T_Out_degC`: Measured shell outlet temperature (°C).
  - `[HEx]_[Product]_Shell_m_kg_s`: Measured shell mass flow rate (kg/s).

### 1.3 Metadata / Design Constants (`METADATA`)
- `[HEx]_Crude_Tube_Cp_J_kgK`: Crude specific heat capacity (J/kg·K).
- `[HEx]_[Product]_Shell_Cp_J_kgK`: Shell product specific heat capacity (J/kg·K).
- `[HEx]_Design_Duty_W`: Design clean heat duty (Watts).

### 1.4 Derived Physical Variables (`DERIVED_INPUT`)
- `Q_tube`: Tube thermal duty ($W$).
- `Q_shell`: Shell thermal duty ($W$).
- `LMTD`: Logarithmic Mean Temperature Difference ($K$).
- `UA`: Overall heat transfer conductance ($W/K$).

### 1.5 Target Variable (`TARGET`)
- `R_fouling_derived`: Derived fouling resistance ($m^2 \cdot K / W$).

### 1.6 Ground-Truth Inventory (`HIDDEN_GROUND_TRUTH`)
- **Present Ground-Truth Columns**: `HIDDEN_GROUND_TRUTH = 0` columns present in `data/raw/heat_exchanger_fouling_dataset.csv`.
- **Forbidden Ground-Truth Patterns**: Any simulation ground-truth column matching `*_True` or `*_True_*` (e.g. `R_fouling_True`, `U_fouled_True`, `Q_actual_True`, `T_wall_avg_True_C`) in present or future datasets is STRICTLY FORBIDDEN from entering model input schemas.

### 1.7 Missing / Unavailable Variables (`NOT_AVAILABLE`)
- Pressure ($P$) and Differential Pressure ($\Delta P$).
- Reynolds Number ($Re$) and Fluid Viscosity ($\mu$).
- Tube Wall Temperatures ($T_{wall}$).
- Explicit Cleaning Event Flags / Reset Timestamps.
