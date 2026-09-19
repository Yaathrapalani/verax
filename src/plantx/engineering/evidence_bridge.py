"""Evidence Graph bridge connecting EngineeringState to Stage 4 lineage graphs."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance
from src.plantx.evidence_graph import (
    EvidenceGraphEngine,
    GraphNodeType,
    GraphEdgeType,
)
from src.plantx.engineering.state import EngineeringState


class EngineeringEvidenceBridge:
    """Bridge attaching Stage 5 EngineeringState calculations to EvidenceGraph Engine."""

    @classmethod
    def attach_engineering_state_to_graph(
        cls,
        graph_engine: EvidenceGraphEngine,
        state: EngineeringState,
        source_evidence_id: str,
    ) -> None:
        # 1. Attach engineering computation node
        comp_node_id = f"comp-state-{state.asset_id}-{int(state.timestamp)}"
        graph_engine.add_node(
            node_id=comp_node_id,
            node_type=GraphNodeType.ENGINEERING_COMPUTATION,
            truth_state=TruthState.INFERRED,
            provenance=state.provenance,
            observed_at=state.timestamp,
            payload={
                "asset_id": state.asset_id,
                "validity": state.validity,
                "calculations": state.calculations_executed,
            },
        )

        # 2. Attach link from source evidence
        if source_evidence_id in graph_engine.nodes:
            graph_engine.add_edge(
                edge_id=f"edge-src-comp-{int(state.timestamp)}",
                source_id=source_evidence_id,
                target_id=comp_node_id,
                edge_type=GraphEdgeType.USES_INPUT,
            )

        # 3. Attach calculated quantities
        for name, qty in state.quantities.items():
            qty_node_id = f"qty-node-{name}-{int(state.timestamp)}"
            graph_engine.add_node(
                node_id=qty_node_id,
                node_type=GraphNodeType.ENGINEERING_COMPUTATION if qty.truth_state == TruthState.INFERRED else GraphNodeType.MEASUREMENT,
                truth_state=qty.truth_state,
                provenance=qty.provenance,
                observed_at=state.timestamp,
                payload={"value": qty.normalized_value, "unit": qty.normalized_unit},
            )
            graph_engine.add_edge(
                edge_id=f"edge-comp-qty-{name}-{int(state.timestamp)}",
                source_id=comp_node_id,
                target_id=qty_node_id,
                edge_type=GraphEdgeType.PRODUCES,
            )

        # 4. Attach explicit assumptions
        for idx, asm in enumerate(state.assumptions):
            asm_node_id = f"asm-node-{idx}-{int(state.timestamp)}"
            if asm_node_id not in graph_engine.nodes:
                graph_engine.add_node(
                    node_id=asm_node_id,
                    node_type=GraphNodeType.ASSUMPTION,
                    truth_state=TruthState.REPRESENTATIVE,
                    provenance=state.provenance,
                    observed_at=state.timestamp,
                    payload={"assumption_name": asm},
                )
                graph_engine.add_edge(
                    edge_id=f"edge-asm-comp-{idx}-{int(state.timestamp)}",
                    source_id=asm_node_id,
                    target_id=comp_node_id,
                    edge_type=GraphEdgeType.USES_ASSUMPTION,
                )
                if source_evidence_id in graph_engine.nodes:
                    graph_engine.add_edge(
                        edge_id=f"edge-src-asm-{idx}-{int(state.timestamp)}",
                        source_id=source_evidence_id,
                        target_id=asm_node_id,
                        edge_type=GraphEdgeType.EXTRACTED_FROM,
                    )
