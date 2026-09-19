"""Evidence Graph bridge connecting Stage 13 ThermodynamicState backward to Stage 4 Evidence Graph."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.thermo.schemas import ThermodynamicState


class ThermoEvidenceBridge:
    """Connects ThermodynamicState nodes backward to Stage 4 Evidence Graph."""

    @staticmethod
    def attach_thermo_state_to_evidence_graph(
        evidence_graph: EvidenceGraph,
        thermo_state: ThermodynamicState,
        origin_node_id: str,
    ) -> str:
        state_node_id = f"thermo-state-{thermo_state.state_id}"
        evidence_graph.add_node(
            node_id=state_node_id,
            node_type="ThermodynamicState",
            truth_state=thermo_state.truth_state.value,
            payload={
                "state_id": thermo_state.state_id,
                "temperature": thermo_state.temperature,
                "pressure": thermo_state.pressure,
                "density": thermo_state.density,
                "result_hash": thermo_state.result_hash,
            },
        )
        evidence_graph.add_edge(
            source_id=origin_node_id,
            target_id=state_node_id,
            edge_type=EvidenceEdgeType.DERIVED_FROM,
        )
        return state_node_id
