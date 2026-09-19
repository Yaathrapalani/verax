"""Evidence Graph bridge connecting Stage 10 DecisionCase backward to Stage 4 Evidence Graph."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.decision.schemas import DecisionCase


class DecisionEvidenceBridge:
    """Connects DecisionCase backward to Stage 4 Evidence Graph."""

    @staticmethod
    def attach_decision_to_graph(
        graph: EvidenceGraph,
        decision_case: DecisionCase,
        origin_node_id: str,
    ) -> str:
        dec_node_id = decision_case.decision_id
        graph.add_node(
            node_id=dec_node_id,
            node_type="Decision",
            truth_state=TruthState.INFERRED.value,
            payload=decision_case.model_dump(),
        )
        graph.add_edge(
            source_id=origin_node_id,
            target_id=dec_node_id,
            edge_type=EvidenceEdgeType.RECOMMENDS,
        )
        return dec_node_id
