"""Adapter translating FOUL-X outputs into PLANT-X canonical domain entities and evidence graph."""

from typing import Dict, Any, List
from src.plantx.domain import (
    Plant,
    Asset,
    Measurement,
    Stream,
    TruthState,
    Provenance,
    ProvenanceType,
    Prediction,
    Uncertainty,
    Decision,
    HumanApproval,
)
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.foulx.replay import ReplaySnapshot, ReplayService


class FoulXAdapter:
    """Zero-side-effect adapter mapping FOUL-X historical replay snapshot to PLANT-X contracts."""

    @classmethod
    def to_plantx_domain(cls, snapshot: ReplaySnapshot) -> Dict[str, Any]:
        timestamp_str = str(snapshot.timestamp)
        step_id = int(snapshot.timestamp)
        prov = Provenance(
            provenance_id=f"prov-foulx-{step_id}",
            provenance_type=ProvenanceType.HISTORIAN,
            source_reference="data/raw/heat_exchanger_fouling_dataset.csv",
            agent_id="FOUL-X-ReplayEngine",
            timestamp=timestamp_str,
            transformation_applied="M2 Physics + M4 Prognosis + M5 Gate + M6 Decision",
        )

        plant = Plant(
            plant_id="PLANT-01",
            name="Crude Refining Unit A",
            location="Gulf Coast Facility",
            truth_state=TruthState.OBSERVED,
            provenance=prov,
            asset_ids=["HX-101"],
            stream_ids=["STRM-HOT-IN", "STRM-COLD-IN"],
        )

        asset = Asset(
            asset_id="HX-101",
            plant_id="PLANT-01",
            name="Shell & Tube Heat Exchanger HX-101",
            asset_type="HEAT_EXCHANGER",
            truth_state=TruthState.OBSERVED,
            provenance=prov,
        )

        state = snapshot.physics_state
        raw = snapshot.raw_state_reference
        measurements = [
            Measurement(
                measurement_id=f"m-thi-{step_id}",
                sensor_id="TI-101",
                stream_id="STRM-HOT-IN",
                parameter_name="T_hot_in",
                value=float(raw.get("E01_Crude_Tube_T_In_degC", raw.get("T_hot_in", 300.0))),
                unit="C",
                truth_state=TruthState.OBSERVED,
                provenance=prov,
            ),
            Measurement(
                measurement_id=f"m-tho-{step_id}",
                sensor_id="TI-102",
                stream_id="STRM-HOT-OUT",
                parameter_name="T_hot_out",
                value=float(raw.get("E01_Crude_Tube_T_Out_degC", raw.get("T_hot_out", 250.0))),
                unit="C",
                truth_state=TruthState.OBSERVED,
                provenance=prov,
            ),
            Measurement(
                measurement_id=f"m-rf-{step_id}",
                sensor_id="CALC-RF",
                stream_id="UNASSIGNED",
                parameter_name="foul_resistance_rf",
                value=float(state.fouling.rf_derived) if state.fouling.rf_derived is not None else 0.0,
                unit="m2K/W",
                truth_state=TruthState.INFERRED,
                provenance=prov,
            ),
        ]

        pred = None
        unc = None
        if snapshot.forecast_state and len(snapshot.forecast_state) > 0:
            fc = snapshot.forecast_state[0]
            pred = Prediction(
                prediction_id=f"pred-{step_id}",
                model_id="FOULX-M4-CAUSAL-RIDGE",
                asset_id="HX-101",
                target_parameter="foul_resistance_rf",
                predicted_value=float(fc.prediction) if fc.prediction is not None else 0.0,
                horizon_hours=float(fc.horizon_hours),
                truth_state=TruthState.INFERRED,
                provenance=prov,
            )
            unc = Uncertainty(
                uncertainty_id=f"unc-{step_id}",
                prediction_id=pred.prediction_id,
                lower_bound=0.0,
                upper_bound=0.0,
                truth_state=TruthState.INFERRED,
                provenance=prov,
            )

        dec = Decision(
            decision_id=f"dec-{step_id}",
            asset_id="HX-101",
            evidence_ids=[m.measurement_id for m in measurements],
            prediction_id=pred.prediction_id if pred else None,
            uncertainty_id=unc.uncertainty_id if unc else None,
            recommendation=snapshot.decision_state.decision.value if snapshot.decision_state else "ABSTAIN",
            abstention=(snapshot.reliability_state.status.value == "ABSTAIN") if snapshot.reliability_state else True,
            reason=", ".join([rc.value for rc in snapshot.decision_state.reason_codes]) if snapshot.decision_state else "No gate evaluation",
            truth_state=TruthState.INFERRED,
            provenance=prov,
        )

        egraph = EvidenceGraph()
        egraph.add_node(dec.decision_id, "Decision", dec.truth_state.value, {"recommendation": dec.recommendation})
        for m in measurements:
            egraph.add_node(m.measurement_id, "Measurement", m.truth_state.value, {"value": m.value, "unit": m.unit})
            egraph.add_edge(m.measurement_id, dec.decision_id, EvidenceEdgeType.SUPPORTED_BY)

        if pred:
            egraph.add_node(pred.prediction_id, "Prediction", pred.truth_state.value, {"predicted_value": pred.predicted_value})
            egraph.add_edge(pred.prediction_id, dec.decision_id, EvidenceEdgeType.PREDICTS)

        return {
            "plant": plant,
            "asset": asset,
            "measurements": measurements,
            "prediction": pred,
            "uncertainty": unc,
            "decision": dec,
            "evidence_graph": egraph,
        }
