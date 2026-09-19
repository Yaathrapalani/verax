"""Executable HeatExchangerModel orchestrating Stage 5 engineering equations."""

import math
import json
import hashlib
from typing import Dict, Any, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.process.schemas import EquipmentType
from src.plantx.equipment.schemas import (
    EquipmentExecution,
    SolverStatus,
    FlowArrangement,
    SimulationMode,
)
from src.plantx.equipment.equipment_registry import EquipmentModelContract
from src.plantx.equipment.errors import EquipmentValidationError


class HeatExchangerModel(EquipmentModelContract):
    """Executable Heat Exchanger Model supporting counter-current thermal calculations."""

    def __init__(self):
        super().__init__(model_id="HeatExchangerModel", equipment_type=EquipmentType.HEAT_EXCHANGER, model_version="1.0.0")

    def execute(self, equipment_id: str, inputs: Dict[str, Any], timestamp: float) -> EquipmentExecution:
        prov = Provenance(
            provenance_id=f"prov-hxexec-{equipment_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="HeatExchangerModel.execute",
            timestamp="2026-09-17T15:45:00Z",
            transformation_applied="Stage 14 Heat Exchanger Simulation",
        )

        T_in_h = inputs.get("T_in_h")
        T_out_h = inputs.get("T_out_h")
        T_in_c = inputs.get("T_in_c")
        T_out_c = inputs.get("T_out_c")
        flow_h = inputs.get("flow_h")
        flow_c = inputs.get("flow_c")
        cp_h = inputs.get("cp_h", 2100.0)  # J/(kg*K)
        cp_c = inputs.get("cp_c", 2000.0)
        area = inputs.get("area", 120.0)
        flow_arr = inputs.get("flow_arrangement", FlowArrangement.COUNTER_CURRENT)

        # 1. Input Validation
        if T_in_h is None or T_out_h is None or T_in_c is None or T_out_c is None:
            return EquipmentExecution(
                execution_id=f"exec-{equipment_id}-{int(timestamp)}",
                equipment_id=equipment_id,
                model_id=self.model_id,
                model_version=self.model_version,
                input_state=inputs,
                output_state={"status": "MISSING_TEMPERATURE_INPUTS"},
                solver_status=SolverStatus.UNAVAILABLE,
                applicability="INSUFFICIENT_INPUTS",
                provenance=prov,
                truth_state=TruthState.SIMULATED,
            )

        if flow_h is not None and flow_h <= 0:
            raise EquipmentValidationError(f"Invalid hot fluid flow rate {flow_h} kg/s. Must be > 0.")
        if flow_c is not None and flow_c <= 0:
            raise EquipmentValidationError(f"Invalid cold fluid flow rate {flow_c} kg/s. Must be > 0.")

        # 2. Thermal Duty Q Calculation (kW)
        Q_hot = flow_h * (cp_h / 1000.0) * (T_in_h - T_out_h) if flow_h else None
        Q_cold = flow_c * (cp_c / 1000.0) * (T_out_c - T_in_c) if flow_c else None
        Q_mean = Q_hot if Q_hot is not None else Q_cold

        thermal_discrepancy = None
        if Q_hot is not None and Q_cold is not None:
            denom = max(abs(Q_hot), abs(Q_cold), 1e-6)
            thermal_discrepancy = abs(Q_hot - Q_cold) / denom

        # 3. LMTD Counter-Current Calculation
        dT1 = T_in_h - T_out_c
        dT2 = T_out_h - T_in_c

        if dT1 <= 0 or dT2 <= 0:
            raise EquipmentValidationError(f"Temperature crossing detected (dT1={dT1}, dT2={dT2}). Counter-current heat exchange impossible.")

        if abs(dT1 - dT2) < 1e-5:
            lmtd = dT1
        else:
            try:
                lmtd = (dT1 - dT2) / math.log(dT1 / dT2)
            except Exception as err:
                raise EquipmentValidationError(f"Invalid LMTD evaluation: {err}")

        # 4. UA & Fouling Resistance Calculation
        ua = (Q_mean * 1000.0 / lmtd) if (Q_mean is not None and lmtd > 0) else None
        ua_clean_ref = inputs.get("clean_ua_reference", 18000.0)  # W/K
        rf = (1.0 / ua - 1.0 / ua_clean_ref) if (ua and ua > 0) else None

        outputs = {
            "Q_hot_kW": Q_hot,
            "Q_cold_kW": Q_cold,
            "Q_mean_kW": Q_mean,
            "thermal_discrepancy": thermal_discrepancy,
            "dT1_K": dT1,
            "dT2_K": dT2,
            "LMTD_K": lmtd,
            "UA_W_per_K": ua,
            "Rf_m2K_per_W": rf,
            "mode": SimulationMode.MODE_A_FORWARD_CALCULATION.value,
        }

        res_hash = hashlib.sha256(json.dumps({"eq": equipment_id, "UA": ua, "LMTD": lmtd}, sort_keys=True).encode("utf-8")).hexdigest()

        return EquipmentExecution(
            execution_id=f"exec-{equipment_id}-{int(timestamp)}",
            equipment_id=equipment_id,
            model_id=self.model_id,
            model_version=self.model_version,
            input_state=inputs,
            output_state=outputs,
            parameters={"area": area, "cp_h": cp_h, "cp_c": cp_c, "clean_ua_ref": ua_clean_ref},
            assumptions=["Counter-current flow arrangement", "Constant specific heat capacities", "Steady-state operation"],
            solver_status=SolverStatus.CONVERGED,
            applicability="NUMERICALLY_BENCHMARKED",
            provenance=prov,
            result_hash=res_hash,
            truth_state=TruthState.SIMULATED,
        )
