"""Benchmark Runtime & Data Augmentation Engine for Stage 13."""

import hashlib
import json
import math
from typing import List, Dict, Any, Tuple
from pathlib import Path

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.thermo.schemas import (
    BenchmarkCase,
    BenchmarkResult,
    BenchmarkMetrics,
    BenchmarkDomain,
    EngineeringValidationLabel,
    ThermodynamicInput,
    PropertyPackageType,
    CompositionBasis,
)
from src.plantx.thermo.property_package import IdealGasPackage
from src.plantx.thermo.errors import (
    TemporalThermoViolation,
    ThermoSourceMutation,
    AutonomousControlViolationError,
)


class BenchmarkRuntime:
    """Master Stage 13 Benchmark Runtime and Analytical Validation Engine."""

    @staticmethod
    def run_analytical_suite(
        eval_timestamp: float = 1000.0,
        baseline_max_time: float = 63999.0,
        data_path: Path = Path("data/raw/heat_exchanger_fouling_dataset.csv"),
        allow_autonomous_control: bool = False,
    ) -> Tuple[BenchmarkResult, List[BenchmarkCase]]:
        if allow_autonomous_control:
            raise AutonomousControlViolationError("Autonomous control strictly forbidden.")

        # Source immutability check
        h_before = hashlib.sha256(data_path.read_bytes()).hexdigest()

        if eval_timestamp > baseline_max_time:
            raise TemporalThermoViolation(f"Timestamp {eval_timestamp} exceeds baseline max time {baseline_max_time}")

        prov = Provenance(
            provenance_id=f"prov-bench-{int(eval_timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="BenchmarkRuntime.run_analytical_suite",
            timestamp="2026-09-17T15:35:00Z",
            transformation_applied="Stage 13 Scientific Benchmark Execution",
        )

        cases = []
        # Case 1: Ideal Gas Law STP
        cases.append(
            BenchmarkCase(
                benchmark_id="bench-01-stp",
                domain=BenchmarkDomain.THERMODYNAMIC_STATE,
                description="Ideal Gas STP Density Evaluation",
                inputs={"T": 273.15, "P": 101325.0},
                expected_outputs={"rho": 1.292},  # kg/m3 for air at STP
                reference_source="NIST Standard Reference Data",
                provenance=prov,
            )
        )

        # Case 2: Sensible Enthalpy Delta
        cases.append(
            BenchmarkCase(
                benchmark_id="bench-02-enthalpy",
                domain=BenchmarkDomain.ENERGY,
                description="Sensible Enthalpy Calculation Delta",
                inputs={"T": 373.15, "P": 101325.0},
                expected_outputs={"dh": 100500.0},  # Cp * Delta_T = 1005 * 100 K
                reference_source="Analytical Energy Balance Formula",
                provenance=prov,
            )
        )

        valid_cnt = 0
        err_list = []

        for bcase in cases:
            t = bcase.inputs["T"]
            p = bcase.inputs["P"]
            inp = ThermodynamicInput(temperature=t, pressure=p, provenance=prov)
            res = IdealGasPackage.evaluate_state(inp)

            if "rho" in bcase.expected_outputs:
                exp_rho = bcase.expected_outputs["rho"]
                rel_err = abs(res.density - exp_rho) / exp_rho
                err_list.append(rel_err)
                if rel_err <= bcase.tolerance:
                    valid_cnt += 1
            elif "dh" in bcase.expected_outputs:
                exp_dh = bcase.expected_outputs["dh"]
                dh_calc = res.enthalpy - (1005.0 * 273.15)
                rel_err = abs(dh_calc - exp_dh) / exp_dh
                err_list.append(rel_err)
                if rel_err <= bcase.tolerance:
                    valid_cnt += 1

        mae = sum(err_list) / len(err_list) if err_list else 0.0
        rmse = math.sqrt(sum(e**2 for e in err_list) / len(err_list)) if err_list else 0.0

        metrics = BenchmarkMetrics(
            mae=mae,
            rmse=rmse,
            max_relative_error=max(err_list) if err_list else 0.0,
            bias=0.0,
            valid_cases=valid_cnt,
            failed_cases=len(cases) - valid_cnt,
            unsupported_cases=0,
        )

        h_after = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if h_before != h_after:
            raise ThermoSourceMutation("Source dataset mutated during benchmark execution!")

        res_hash = hashlib.sha256(json.dumps({"valid": valid_cnt, "mae": mae}, sort_keys=True).encode("utf-8")).hexdigest()

        b_result = BenchmarkResult(
            benchmark_id=f"bench-run-{int(eval_timestamp)}",
            implementation="IdealGasPackage.1.0.0",
            case_count=len(cases),
            valid_count=valid_cnt,
            failed_count=len(cases) - valid_cnt,
            unsupported_count=0,
            metrics=metrics,
            validation_label=EngineeringValidationLabel.NUMERICALLY_BENCHMARKED,
            pass_status=(valid_cnt == len(cases)),
            provenance=prov,
            result_hash=res_hash,
        )

        return b_result, cases
