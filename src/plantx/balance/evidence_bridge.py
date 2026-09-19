"""Evidence Graph bridge connecting Stage 12 BalanceCase backward to Stage 4 Evidence Graph."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.balance.schemas import BalanceCase


class BalanceEvidenceBridge:
    """Connects BalanceCase nodes backward to Stage 4 Evidence Graph."""

    @staticmethod
    def attach_balance_case_to_evidence_graph(
        evidence_graph: EvidenceGraph,
        balance_case: BalanceCase,
        origin_node_id: str,
    ) -> str:
        bal_node_id = f"balance-case-{balance_case.balance_id}"
        evidence_graph.add_node(
            node_id=bal_node_id,
            node_type="BalanceCase",
            truth_state=TruthState.INFERRED.value,
            payload={
                "balance_id": balance_case.balance_id,
                "scope_id": balance_case.scope_id,
                "status": balance_case.status.value,
                "result_hash": balance_case.result_hash,
            },
        )
        evidence_graph.add_edge(
            source_id=origin_node_id,
            target_id=bal_node_id,
            edge_type=EvidenceEdgeType.DERIVED_FROM,
        )
        return bal_node_id
