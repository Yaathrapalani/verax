import pytest
from src.foulx.gate.schemas import (
    ReliabilityResult,
    GateStatus,
    CheckStatus,
    CheckResult,
    ForecastReference,
    GateProvenance,
)
from src.foulx.gate.reason_codes import ReliabilityReasonCode

def test_reliability_result_serialization():
    forecast_ref = ForecastReference(
        exchanger_id="E01",
        timestamp=45000.0,
        horizon_hours=24,
        prediction=1.2e-7,
        model_method="RidgeRegression",
    )
    
    chk_data = CheckResult(
        check_name="DATA_COMPLETENESS",
        status=CheckStatus.PASS,
        reason_code=None,
        evidence={"missing_count": 0},
    )
    
    res = ReliabilityResult(
        timestamp=45000.0,
        exchanger_id="E01",
        status=GateStatus.PASS,
        checks=[chk_data],
        reason_codes=[],
        evidence={"gate_decision": "PASS"},
        forecast_reference=forecast_ref,
        provenance=GateProvenance(),
    )
    
    res_dict = res.to_dict()
    assert res_dict["status"] == "PASS"
    assert res_dict["exchanger_id"] == "E01"
    assert res_dict["forecast_reference"]["prediction"] == 1.2e-7
    
    # Round-trip deserialization
    res_reconstructed = ReliabilityResult.model_validate(res_dict)
    assert res_reconstructed == res
