"""Evidence Graph bridge connecting Stage 7 ReliabilityAssessment backward to Stage 4 Evidence Graph."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.trust.schemas import ReliabilityAssessment


class TrustEvidenceBridge:
    """Connects ReliabilityAssessment backward to Evidence Graph."""

    @staticmethod
    def attach_assessment_to_graph(
        graph: EvidenceGraph,
        assessment: ReliabilityAssessment,
        forecast_node_id: str,
    ) -> str:
        assess_node_id = assessment.assessment_id
        graph.add_node(
            node_id=assess_node_id,
            node_type="Reliability",
            truth_state=TruthState.INFERRED.value,
            payload=assessment.model_dump(),
        )
        graph.add_edge(
            source_id=forecast_node_id,
            target_id=assess_node_id,
            edge_type=EvidenceEdgeType.EVALUATES_RELIABILITY,
        )
        return assess_node_id
