"""Evidence Graph and Digital Shadow integration bridges for Stage 11 Process Model."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.process.schemas import PlantModel


class ProcessEvidenceBridge:
    """Connects Stage 11 PlantModel entity nodes backward to Stage 4 Evidence Graph."""

    @staticmethod
    def attach_plant_model_to_evidence_graph(
        evidence_graph: EvidenceGraph,
        plant_model: PlantModel,
        origin_evidence_node_id: str,
    ) -> str:
        plant_node_id = f"process-plant-{plant_model.plant_id}"
        evidence_graph.add_node(
            node_id=plant_node_id,
            node_type="ProcessPlantModel",
            truth_state=plant_model.truth_state.value,
            payload={
                "plant_id": plant_model.plant_id,
                "graph_hash": plant_model.graph_hash,
                "equipment_count": len(plant_model.equipment),
                "stream_count": len(plant_model.streams),
            },
        )
        evidence_graph.add_edge(
            source_id=origin_evidence_node_id,
            target_id=plant_node_id,
            edge_type=EvidenceEdgeType.DERIVED_FROM,
        )
        return plant_node_id
