"""Evidence Graph bridge connecting Stage 8 InvestigationCase backward to Stage 4 Evidence Graph."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.investigation.schemas import InvestigationCase


class InvestigationEvidenceBridge:
    """Connects InvestigationCase backward to Evidence Graph."""

    @staticmethod
    def attach_case_to_graph(
        graph: EvidenceGraph,
        case: InvestigationCase,
        origin_node_id: str,
    ) -> str:
        case_node_id = case.case_id
        graph.add_node(
            node_id=case_node_id,
            node_type="Investigation",
            truth_state=TruthState.INFERRED.value,
            payload=case.model_dump(),
        )
        graph.add_edge(
            source_id=origin_node_id,
            target_id=case_node_id,
            edge_type=EvidenceEdgeType.SUPPORTED_BY,
        )
        return case_node_id
