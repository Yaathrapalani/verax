import pytest
from src.foulx.decision.schemas import (
    DecisionResult,
    DecisionState,
    DecisionProvenance,
)
from src.foulx.decision.reason_codes import DecisionReasonCode
from src.foulx.gate.schemas import GateStatus

def test_decision_result_serialization():
    res = DecisionResult(
        timestamp=45000.0,
        exchanger_id="E01",
        decision=DecisionState.OPERATE,
        reliability_status=GateStatus.PASS,
        current_rf_derived=7.2e-8,
        forecast_horizon_hours=24,
        threshold_rf=1.5e-7,
        threshold_crossing=False,
        estimated_crossing_horizon_hours=None,
        reason_codes=[DecisionReasonCode.THRESHOLD_NOT_REACHED],
        evidence={"threshold_crossed": False},
        provenance=DecisionProvenance(),
    )

    res_dict = res.to_dict()
    assert res_dict["decision"] == "OPERATE"
    assert res_dict["reliability_status"] == "PASS"
    assert res_dict["provenance"]["human_approval_required"] is True

    # Round-trip deserialization
    res_reconstructed = DecisionResult.model_validate(res_dict)
    assert res_reconstructed == res
