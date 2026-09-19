"""Master Scenario Engine for Stage 9."""

import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.engineering.state import EngineeringState
from src.plantx.intelligence.schemas import FoulingPrognosis
from src.plantx.trust.schemas import ReliabilityAssessment
from src.plantx.investigation.schemas import InvestigationCase
from src.plantx.scenario.schemas import (
    ScenarioCase,
    ScenarioType,
    ScenarioParameter,
    ScenarioStatus,
    ApplicabilityClassification,
)
from src.plantx.scenario.validation import ScenarioValidator
from src.plantx.scenario.propagation import ScenarioPropagationEngine
from src.plantx.scenario.comparison import ScenarioComparisonEngine
from src.plantx.scenario.applicability import ScenarioApplicabilityEngine
from src.plantx.scenario.errors import (
    TemporalScenarioViolation,
    ScenarioSourceMutation,
    ScenarioStage10BoundaryViolation,
)
from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING


class ScenarioEngine:
    """Master Stage 9 Scenario / What-If Engine."""

    def __init__(self, physics_estimator: Optional[PhysicsStateEstimator] = None):
        self.propagation_engine = ScenarioPropagationEngine(physics_estimator)

    def execute_scenario(
        self,
        raw_record: Dict[str, Any],
        asset_id: str,
        scenario_type: ScenarioType,
        perturbation_magnitude: float = 0.15,
        trust_assessment: Optional[ReliabilityAssessment] = None,
        investigation_case: Optional[InvestigationCase] = None,
        prognosis: Optional[FoulingPrognosis] = None,
        baseline_max_time: float = 63999.0,
        data_path: Path = Path("data/raw/heat_exchanger_fouling_dataset.csv"),
        allow_autonomous_maintenance: bool = False,
    ) -> ScenarioCase:
        # Check Stage 10 boundary violation
        if allow_autonomous_maintenance:
            raise ScenarioStage10BoundaryViolation("Autonomous maintenance or Stage 10 decision optimization is strictly prohibited in Stage 9.")

        # Source immutability check before execution
        h_before = hashlib.sha256(data_path.read_bytes()).hexdigest()

        timestamp = float(raw_record.get("Time_hr", 0.0))
        if timestamp > baseline_max_time:
            raise TemporalScenarioViolation(f"Scenario timestamp {timestamp} exceeds baseline max time {baseline_max_time}")

        # 1. Validate parameter perturbation
        ScenarioValidator.validate_perturbation(scenario_type, perturbation_magnitude)

        shell_name = EXCHANGER_MAPPING.get(asset_id, "HeavyNaphtha")
        prov = Provenance(
            provenance_id=f"prov-scencase-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.SIMULATION,
            source_reference="ScenarioEngine.execute_scenario",
            timestamp="2026-09-17T14:32:00Z",
            transformation_applied=f"Stage 9 Scenario Execution ({scenario_type.value})",
        )

        # 2. Construct perturbed record and parameter models
        perturbed_rec = raw_record.copy()
        params: List[ScenarioParameter] = []

        if scenario_type in (ScenarioType.FLOW_INCREASE, ScenarioType.FLOW_DECREASE):
            tube_m_key = f"{asset_id}_Crude_Tube_m_kg_s"
            shell_m_key = f"{asset_id}_{shell_name}_Shell_m_kg_s"
            
            orig_tube_m = float(raw_record.get(tube_m_key, 50.0))
            new_tube_m = orig_tube_m * (1.0 + perturbation_magnitude)
            perturbed_rec[tube_m_key] = new_tube_m

            orig_shell_m = float(raw_record.get(shell_m_key, 40.0))
            new_shell_m = orig_shell_m * (1.0 + perturbation_magnitude)
            perturbed_rec[shell_m_key] = new_shell_m

            params.append(
                ScenarioParameter(
                    parameter_id=f"param-m-{asset_id}-{int(timestamp)}",
                    variable="m_kg_s",
                    asset_id=asset_id,
                    baseline_value=orig_tube_m,
                    baseline_unit="kg/s",
                    scenario_value=new_tube_m,
                    scenario_unit="kg/s",
                    perturbation_type="RELATIVE_PERCENT",
                    perturbation_magnitude=perturbation_magnitude,
                    provenance=prov,
                )
            )

        elif scenario_type == ScenarioType.HEAT_TRANSFER_DEGRADATION:
            # Heat transfer UA degradation assumption
            params.append(
                ScenarioParameter(
                    parameter_id=f"param-ua-{asset_id}-{int(timestamp)}",
                    variable="UA",
                    asset_id=asset_id,
                    baseline_value=200000.0,
                    baseline_unit="W/K",
                    scenario_value=200000.0 * (1.0 - perturbation_magnitude),
                    scenario_unit="W/K",
                    perturbation_type="ASSUMED_FRACTION",
                    perturbation_magnitude=perturbation_magnitude,
                    provenance=prov,
                )
            )

        # 3. Baseline Stage 5 calculation
        baseline_canonical, baseline_eng = self.propagation_engine.propagate_scenario(raw_record, asset_id, raw_record)

        # 4. Propagate scenario through Stage 5 calculations
        scenario_canonical, scenario_eng = self.propagation_engine.propagate_scenario(raw_record, asset_id, perturbed_rec)

        # 5. Evaluate applicability
        applicability = ScenarioApplicabilityEngine.evaluate_applicability(scenario_type, trust_assessment, pressure_available=False)

        # 6. Comparative evaluation (deltas & relative deltas)
        results = {}
        for var_name in ["Q_tube", "LMTD", "UA", "Rf_derived"]:
            b_qty = baseline_eng.quantities.get(var_name)
            s_qty = scenario_eng.quantities.get(var_name)
            b_val = b_qty.normalized_value if b_qty else None
            s_val = s_qty.normalized_value if s_qty else None
            unit = b_qty.normalized_unit if b_qty else "UNKNOWN"

            comp_res = ScenarioComparisonEngine.compare_variable(
                var_name=var_name,
                baseline_val=b_val,
                scenario_val=s_val,
                unit=unit,
                asset_id=asset_id,
                timestamp=timestamp,
                applicability=applicability.thermal_support,
            )
            results[var_name] = comp_res

        # Source immutability check after execution
        h_after = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if h_before != h_after:
            raise ScenarioSourceMutation("Raw source dataset was mutated during scenario execution!")

        impact_summary = {
            "delta_q_tube": results["Q_tube"].delta if "Q_tube" in results else None,
            "delta_ua": results["UA"].delta if "UA" in results else None,
            "delta_rf": results["Rf_derived"].delta if "Rf_derived" in results else None,
        }

        # Handle Stage 8 investigation boundary integration note
        assumptions_list = [
            f"Perturbation magnitude = {perturbation_magnitude:+.2%}",
            "Prototype scenario bound — not a site-specific operating limit",
            "Thermal propagation executed cleanly via Stage 5 Engineering Core",
            "Hydraulic ΔP measurements unavailable",
        ]
        if investigation_case:
            assumptions_list.append("Scenario analysis tests a hypothetical condition; it cannot establish which hypothesis explains observed plant behavior.")

        return ScenarioCase(
            scenario_id=f"scen-{asset_id}-{int(timestamp)}-{scenario_type.value.lower()}",
            asset_id=asset_id,
            created_at="2026-09-17T14:32:00Z",
            baseline_timestamp=timestamp,
            scenario_type=scenario_type,
            description=f"Stage 9 scenario simulation ({scenario_type.value}) for {asset_id} at t={timestamp}",
            parameters=params,
            assumptions=assumptions_list,
            constraints=[],
            applicability=applicability,
            propagation_path=["Stage 5 Engineering Core", "PhysicsStateEstimator", "M2_PHYSICS_RECALCULATION"],
            baseline_state={k: v.normalized_value for k, v in baseline_eng.quantities.items()},
            scenario_state={k: v.normalized_value for k, v in scenario_eng.quantities.items()},
            results=results,
            impact_summary=impact_summary,
            uncertainty_reference="NOT_STATISTICALLY_JUSTIFIED",
            evidence_reference={
                "baseline_timestamp": timestamp,
                "trust_assessment_status": trust_assessment.overall_state if trust_assessment else "UNCHECKED",
            },
            provenance=prov,
            human_review_required=True,
            status=ScenarioStatus.EXECUTED,
        )
