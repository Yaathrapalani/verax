"""
Gate 15: FOUL-X Reliability Gate & Decision Fallback Reconciliation
"""

import sys
from src.foulx.gate.schemas import GateStatus
from src.foulx.decision.schemas import DecisionState
from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService

def test_gate15():
    print("=== GATE 15: FOUL-X RELIABILITY GATE & FALLBACK ===")
    service = ReplayService()

    # 1. Supported Case (NORMAL mode, E01 at t=100.0)
    normal_snap = service.get_snapshot(100.0, "E01", ReplayMode.NORMAL).to_dict()
    print("1. Supported Case (E01, t=100.0, NORMAL):")
    print(f"   - Current Rf: {normal_snap['physics_state']['fouling']['rf_derived']:.4e} m²K/W")
    print(f"   - Forecast prediction: {normal_snap['reliability_state']['forecast_reference']['prediction']:.4e}")
    print(f"   - Reliability Gate Status: {normal_snap['reliability_state']['status']}")
    print(f"   - Decision: {normal_snap['decision_state']['decision']}")
    
    assert normal_snap['reliability_state']['status'] == GateStatus.PASS, f"Expected PASS, got {normal_snap['reliability_state']['status']}"
    assert normal_snap['decision_state']['decision'] == DecisionState.OPERATE, "Supported case should produce OPERATE"
    print("   -> Supported Case: PASS")

    # 2. +6σ Shifted Case (SHIFTED mode, E01 at t=100.0)
    shifted_snap = service.get_snapshot(100.0, "E01", ReplayMode.SHIFTED).to_dict()
    print("\n2. +6σ Shifted Case (E01, t=100.0, SHIFTED):")
    print(f"   - Reliability Gate Status: {shifted_snap['reliability_state']['status']}")
    print(f"   - Reason Codes: {shifted_snap['reliability_state'].get('reason_codes')}")
    print(f"   - Decision: {shifted_snap['decision_state']['decision']}")
    print(f"   - Decision Reason Codes: {shifted_snap['decision_state'].get('reason_codes')}")
    
    assert shifted_snap['reliability_state']['status'] == GateStatus.ABSTAIN, f"Gate must ABSTAIN on +6σ shift, got {shifted_snap['reliability_state']['status']}"
    assert shifted_snap['decision_state']['decision'] == DecisionState.ABSTAIN, f"Decision must ABSTAIN on gate failure, got {shifted_snap['decision_state']['decision']}"
    assert "REGIME_OOD" in str(shifted_snap['reliability_state']['reason_codes']), "Must cite REGIME_OOD in reason codes"
    print("   -> +6σ Shifted Case: ABSTAIN with Fixed-Policy Fallback verified: PASS")

    print("\nGate 15 FOUL-X: VERIFIED PASS")

if __name__ == '__main__':
    test_gate15()
