"""Plant Graph contract for topological plant representation."""

from enum import Enum
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field


class PlantEdgeType(str, Enum):
    CONNECTED_TO = "CONNECTED_TO"
    FEEDS = "FEEDS"
    RECEIVES = "RECEIVES"
    MEASURES = "MEASURES"
    HAS_EVENT = "HAS_EVENT"
    DEPENDS_ON = "DEPENDS_ON"


class GraphNode(BaseModel):
    node_id: str
    node_type: str  # Asset, Stream, Measurement, Event
    attributes: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    edge_type: PlantEdgeType
    attributes: Dict[str, Any] = Field(default_factory=dict)


class PlantGraph(BaseModel):
    nodes: Dict[str, GraphNode] = Field(default_factory=dict)
    edges: List[GraphEdge] = Field(default_factory=list)

    def add_node(self, node_id: str, node_type: str, attributes: Dict[str, Any] = None) -> None:
        self.nodes[node_id] = GraphNode(
            node_id=node_id,
            node_type=node_type,
            attributes=attributes or {},
        )

    def add_edge(self, source_id: str, target_id: str, edge_type: PlantEdgeType) -> None:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError(f"Cannot add edge {source_id} -> {target_id}: node missing.")
        self.edges.append(GraphEdge(source_id=source_id, target_id=target_id, edge_type=edge_type))
