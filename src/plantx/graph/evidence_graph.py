"""Evidence Graph contract supporting full backward traceability."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceEdgeType(str, Enum):
    SUPPORTED_BY = "SUPPORTED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    PREDICTS = "PREDICTS"
    EVALUATES_RELIABILITY = "EVALUATES_RELIABILITY"
    RECOMMENDS = "RECOMMENDS"


class EvidenceNode(BaseModel):
    node_id: str
    node_type: str  # Evidence, Calculation, State, Prediction, Reliability, Decision
    truth_state: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class EvidenceEdge(BaseModel):
    source_id: str
    target_id: str
    edge_type: EvidenceEdgeType


class EvidenceGraph(BaseModel):
    nodes: Dict[str, EvidenceNode] = Field(default_factory=dict)
    edges: List[EvidenceEdge] = Field(default_factory=list)

    def add_node(self, node_id: str, node_type: str, truth_state: str, payload: Dict[str, Any] = None) -> None:
        self.nodes[node_id] = EvidenceNode(
            node_id=node_id,
            node_type=node_type,
            truth_state=truth_state,
            payload=payload or {},
        )

    def add_edge(self, source_id: str, target_id: str, edge_type: EvidenceEdgeType) -> None:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError(f"Nodes {source_id} or {target_id} missing in Evidence Graph.")
        self.edges.append(EvidenceEdge(source_id=source_id, target_id=target_id, edge_type=edge_type))

    def trace_backward(self, start_node_id: str) -> List[str]:
        """Returns ordered list of upstream nodes supporting the given decision/node."""
        visited = []
        stack = [start_node_id]

        while stack:
            curr = stack.pop()
            if curr not in visited:
                visited.append(curr)
                # Find edges where curr is the target (downstream)
                parents = [e.source_id for e in self.edges if e.target_id == curr]
                stack.extend(parents)
        return visited
