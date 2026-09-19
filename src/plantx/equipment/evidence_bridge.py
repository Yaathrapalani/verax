"""Evidence Graph bridge connecting Stage 14 EquipmentExecution backward to Stage 4 Evidence Graph."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.equipment.schemas import EquipmentExecution


class EquipmentEvidenceBridge:
    """Connects EquipmentExecution nodes backward to Stage 4 Evidence Graph."""

    @staticmethod
    def attach_equipment_execution_to_evidence_graph(
        evidence_graph: EvidenceGraph,
        execution: EquipmentExecution,
        origin_node_id: str,
    ) -> str:
        exec_node_id = f"equipment-exec-{execution.execution_id}"
        evidence_graph.add_node(
            node_id=exec_node_id,
            node_type="EquipmentExecution",
            truth_state=execution.truth_state.value,
            payload={
                "execution_id": execution.execution_id,
                "equipment_id": execution.equipment_id,
                "model_id": execution.model_id,
                "solver_status": execution.solver_status.value,
                "result_hash": execution.result_hash,
            },
        )
        evidence_graph.add_edge(
            source_id=origin_node_id,
            target_id=exec_node_id,
            edge_type=EvidenceEdgeType.PREDICTS,
        )
        return exec_node_id
