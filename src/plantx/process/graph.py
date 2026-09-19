"""Stage 11 Computational Plant Graph, Validation, Hashing, and Traversal."""

import hashlib
import json
from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel, Field

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance
from src.plantx.process.schemas import (
    PlantModel,
    GraphNode,
    GraphEdge,
    NodeKind,
    EdgeRelation,
    EquipmentType,
    EntityResolutionState,
)
from src.plantx.process.errors import (
    TopologyValidationError,
    TemporalProcessGraphViolation,
    ProcessSourceMutation,
    AutonomousControlViolationError,
)


class PlantGraph(BaseModel):
    """Canonical Computational Plant Graph representing nodes, edges, and topology."""

    plant_id: str
    nodes: Dict[str, GraphNode] = Field(default_factory=dict)
    edges: List[GraphEdge] = Field(default_factory=list)

    def add_node(self, node: GraphNode) -> None:
        if node.node_id in self.nodes:
            raise TopologyValidationError(f"Duplicate node ID registered: {node.node_id}")
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source_id not in self.nodes:
            raise TopologyValidationError(f"Edge source ID missing in graph: {edge.source_id}")
        if edge.target_id not in self.nodes:
            raise TopologyValidationError(f"Edge target ID missing in graph: {edge.target_id}")
        self.edges.append(edge)

    def compute_graph_hash(self) -> str:
        """Computes deterministic SHA-256 hash of serialized canonical plant graph."""
        sorted_nodes = sorted(
            [{"id": k, "kind": v.node_kind.value, "truth": v.truth_state.value} for k, v in self.nodes.items()],
            key=lambda x: x["id"],
        )
        sorted_edges = sorted(
            [{"src": e.source_id, "tgt": e.target_id, "rel": e.relation.value} for e in self.edges],
            key=lambda x: (x["src"], x["tgt"], x["rel"]),
        )
        canonical_repr = json.dumps({"nodes": sorted_nodes, "edges": sorted_edges}, sort_keys=True)
        return hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()

    def upstream(self, entity_id: str) -> List[str]:
        """Returns upstream entity IDs directly feeding or connected to entity_id."""
        if entity_id not in self.nodes:
            raise ValueError(f"Entity ID {entity_id} not found in graph.")
        return [e.source_id for e in self.edges if e.target_id == entity_id]

    def downstream(self, entity_id: str) -> List[str]:
        """Returns downstream entity IDs directly fed by or connected from entity_id."""
        if entity_id not in self.nodes:
            raise ValueError(f"Entity ID {entity_id} not found in graph.")
        return [e.target_id for e in self.edges if e.source_id == entity_id]

    def neighbors(self, entity_id: str) -> List[str]:
        """Returns all directly connected neighbor entity IDs."""
        up = self.upstream(entity_id)
        down = self.downstream(entity_id)
        return sorted(list(set(up + down)))

    def find_process_paths(self, source_id: str, destination_id: str) -> List[List[str]]:
        """Finds all deterministic simple paths from source_id to destination_id."""
        if source_id not in self.nodes or destination_id not in self.nodes:
            raise ValueError(f"Source {source_id} or destination {destination_id} missing in graph.")

        paths = []
        stack = [(source_id, [source_id])]

        while stack:
            (curr, path) = stack.pop()
            if curr == destination_id:
                paths.append(path)
                continue

            for next_node in self.downstream(curr):
                if next_node not in path:
                    stack.append((next_node, path + [next_node]))

        return sorted(paths)

    def validate_topology(self) -> List[str]:
        """Validates graph topological consistency and returns warning/error summary."""
        errors = []
        # 1. Orphan check for streams & equipment
        connected_ids = set()
        for e in self.edges:
            connected_ids.add(e.source_id)
            connected_ids.add(e.target_id)

        for n_id, n in self.nodes.items():
            if n.node_kind in [NodeKind.EQUIPMENT, NodeKind.STREAM] and n_id not in connected_ids:
                errors.append(f"Orphan entity detected: {n_id} ({n.node_kind.value})")

        return errors


class GraphEngine:
    """Builds and validates PlantGraph from PlantModel."""

    @staticmethod
    def build_graph_from_model(model: PlantModel) -> PlantGraph:
        pg = PlantGraph(plant_id=model.plant_id)

        # 1. Add Plant Node
        pg.add_node(
            GraphNode(
                node_id=model.plant_id,
                node_kind=NodeKind.PLANT,
                name=model.name,
                truth_state=model.truth_state,
                payload={"description": model.description},
            )
        )

        # 2. Add Process Units
        for u_id, unit in model.units.items():
            pg.add_node(
                GraphNode(
                    node_id=u_id,
                    node_kind=NodeKind.PROCESS_UNIT,
                    name=unit.name,
                    truth_state=unit.truth_state,
                )
            )
            pg.add_edge(
                GraphEdge(
                    edge_id=f"edge-contains-{model.plant_id}-{u_id}",
                    source_id=model.plant_id,
                    target_id=u_id,
                    relation=EdgeRelation.CONTAINS,
                )
            )

        # 3. Add Equipment
        for eq_id, eq in model.equipment.items():
            pg.add_node(
                GraphNode(
                    node_id=eq_id,
                    node_kind=NodeKind.EQUIPMENT,
                    name=eq.name,
                    truth_state=eq.truth_state,
                    payload={"type": eq.equipment_type.value},
                )
            )
            if eq.unit_id and eq.unit_id in pg.nodes:
                pg.add_edge(
                    GraphEdge(
                        edge_id=f"edge-unit-{eq.unit_id}-{eq_id}",
                        source_id=eq.unit_id,
                        target_id=eq_id,
                        relation=EdgeRelation.CONTAINS,
                    )
                )

        # 4. Add Streams & Connections
        for st_id, st in model.streams.items():
            pg.add_node(
                GraphNode(
                    node_id=st_id,
                    node_kind=NodeKind.STREAM,
                    name=st.name,
                    truth_state=st.truth_state,
                    payload={"phase": st.phase.value},
                )
            )
            if st.source_equipment_id and st.source_equipment_id in pg.nodes:
                pg.add_edge(
                    GraphEdge(
                        edge_id=f"edge-feeds-{st.source_equipment_id}-{st_id}",
                        source_id=st.source_equipment_id,
                        target_id=st_id,
                        relation=EdgeRelation.FEEDS,
                    )
                )
            if st.destination_equipment_id and st.destination_equipment_id in pg.nodes:
                pg.add_edge(
                    GraphEdge(
                        edge_id=f"edge-receives-{st_id}-{st.destination_equipment_id}",
                        source_id=st_id,
                        target_id=st.destination_equipment_id,
                        relation=EdgeRelation.RECEIVES,
                    )
                )

        # 5. Add Measurement Bindings
        for mb in model.measurements:
            mb_node_id = f"meas-{mb.binding_id}"
            pg.add_node(
                GraphNode(
                    node_id=mb_node_id,
                    node_kind=NodeKind.MEASUREMENT,
                    name=mb.variable,
                    truth_state=mb.truth_state,
                )
            )
            if mb.entity_id in pg.nodes:
                pg.add_edge(
                    GraphEdge(
                        edge_id=f"edge-meas-{mb_node_id}-{mb.entity_id}",
                        source_id=mb_node_id,
                        target_id=mb.entity_id,
                        relation=EdgeRelation.MEASURED_BY,
                    )
                )

        # Update model graph hash
        model.graph_hash = pg.compute_graph_hash()
        return pg
