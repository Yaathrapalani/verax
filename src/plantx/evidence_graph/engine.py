"""In-process Stage 4 Evidence Graph Engine with forward/backward tracing and validation."""

import hashlib
import json
from typing import Dict, List, Any, Optional, Set
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.evidence_graph.schemas import (
    GraphNodeType,
    GraphEdgeType,
    SufficiencyStatus,
    EvidenceNodeV2,
    EvidenceEdgeV2,
    LineagePath,
    ClaimExplanation,
    ImpactAnalysis,
)


class TemporalLineageViolationError(Exception):
    """Raised when an illegal future observation is attempted in historical lineage."""
    pass


class EvidenceGraphEngine:
    """In-process, deterministic Stage 4 Evidence Graph Engine."""

    def __init__(self):
        self.nodes: Dict[str, EvidenceNodeV2] = {}
        self.edges: Dict[str, EvidenceEdgeV2] = {}
        # Adjacency maps for efficient O(1) lookup:
        self._outgoing: Dict[str, List[EvidenceEdgeV2]] = {}
        self._incoming: Dict[str, List[EvidenceEdgeV2]] = {}

    def add_node(
        self,
        node_id: str,
        node_type: GraphNodeType,
        truth_state: TruthState,
        provenance: Provenance,
        observed_at: Optional[float] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> EvidenceNodeV2:
        node = EvidenceNodeV2(
            node_id=node_id,
            node_type=node_type,
            truth_state=truth_state,
            observed_at=observed_at,
            payload=payload or {},
            provenance=provenance,
        )
        self.nodes[node_id] = node
        if node_id not in self._outgoing:
            self._outgoing[node_id] = []
        if node_id not in self._incoming:
            self._incoming[node_id] = []
        return node

    def add_edge(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        edge_type: GraphEdgeType,
        valid_at: Optional[float] = None,
        provenance: Optional[Provenance] = None,
    ) -> EvidenceEdgeV2:
        if source_id not in self.nodes:
            raise ValueError(f"Source node '{source_id}' does not exist in graph.")
        if target_id not in self.nodes:
            raise ValueError(f"Target node '{target_id}' does not exist in graph.")

        edge = EvidenceEdgeV2(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            valid_at=valid_at,
            provenance=provenance,
        )
        self.edges[edge_id] = edge
        self._outgoing[source_id].append(edge)
        self._incoming[target_id].append(edge)
        return edge

    def get_node(self, node_id: str) -> Optional[EvidenceNodeV2]:
        return self.nodes.get(node_id)

    def trace_backward(self, start_node_id: str, max_depth: int = 50) -> LineagePath:
        """Traces computational lineage backward (Why does start_node exist?)."""
        if start_node_id not in self.nodes:
            raise ValueError(f"Node '{start_node_id}' not found.")

        start_node = self.nodes[start_node_id]
        visited_nodes: List[EvidenceNodeV2] = []
        visited_edges: List[EvidenceEdgeV2] = []
        visited_ids: Set[str] = set()
        missing_evidence: List[str] = []
        assumptions: List[str] = []
        model_versions: List[str] = []
        calc_versions: List[str] = []

        stack = [(start_node_id, 0)]
        target_time = start_node.observed_at

        while stack:
            curr_id, depth = stack.pop()
            if curr_id in visited_ids or depth > max_depth:
                continue

            visited_ids.add(curr_id)
            curr_node = self.nodes[curr_id]
            visited_nodes.append(curr_node)

            # Check temporal constraint violation (t_observed <= target_time)
            if target_time is not None and curr_node.observed_at is not None:
                if curr_node.observed_at > target_time:
                    raise TemporalLineageViolationError(
                        f"TEMPORAL LINEAGE VIOLATION: Upstream node '{curr_id}' at t={curr_node.observed_at} "
                        f"exceeds target claim time T={target_time}."
                    )

            if curr_node.node_type == GraphNodeType.ASSUMPTION:
                assumptions.append(curr_node.payload.get("assumption_name", curr_node.node_id))
            if "model_version" in curr_node.payload:
                model_versions.append(curr_node.payload["model_version"])
            if "calculation_version" in curr_node.payload:
                calc_versions.append(curr_node.payload["calculation_version"])

            # Incoming edges point to curr_id (i.e. source_id -> curr_id)
            in_edges = self._incoming.get(curr_id, [])
            if not in_edges and curr_node.node_type not in {GraphNodeType.EVIDENCE_SOURCE, GraphNodeType.EVIDENCE_RECORD}:
                missing_evidence.append(f"Missing upstream source for {curr_id}")

            for edge in in_edges:
                visited_edges.append(edge)
                stack.append((edge.source_id, depth + 1))

        status = SufficiencyStatus.SUPPORTED
        if missing_evidence:
            status = SufficiencyStatus.PARTIALLY_SUPPORTED
        if start_node.truth_state == TruthState.UNRESOLVED:
            status = SufficiencyStatus.UNRESOLVED

        return LineagePath(
            root_node_id=visited_nodes[-1].node_id if visited_nodes else start_node_id,
            terminal_node_id=start_node_id,
            nodes=visited_nodes,
            edges=visited_edges,
            path_status=status,
            missing_evidence=missing_evidence,
            assumptions=assumptions,
            model_versions=model_versions,
            calculation_versions=calc_versions,
        )

    def trace_forward(self, start_node_id: str, max_depth: int = 50) -> LineagePath:
        """Traces downstream impact forward (What depends on start_node?)."""
        if start_node_id not in self.nodes:
            raise ValueError(f"Node '{start_node_id}' not found.")

        visited_nodes: List[EvidenceNodeV2] = []
        visited_edges: List[EvidenceEdgeV2] = []
        visited_ids: Set[str] = set()

        stack = [(start_node_id, 0)]
        while stack:
            curr_id, depth = stack.pop()
            if curr_id in visited_ids or depth > max_depth:
                continue

            visited_ids.add(curr_id)
            curr_node = self.nodes[curr_id]
            visited_nodes.append(curr_node)

            out_edges = self._outgoing.get(curr_id, [])
            for edge in out_edges:
                visited_edges.append(edge)
                stack.append((edge.target_id, depth + 1))

        return LineagePath(
            root_node_id=start_node_id,
            terminal_node_id=visited_nodes[-1].node_id if visited_nodes else start_node_id,
            nodes=visited_nodes,
            edges=visited_edges,
            path_status=SufficiencyStatus.SUPPORTED,
        )

    def explain_claim(self, claim_id: str) -> ClaimExplanation:
        """High-level API answering: 'WHY does PLANT-X believe this claim?'"""
        lineage = self.trace_backward(claim_id)
        claim_node = self.nodes[claim_id]

        sources = [n.node_id for n in lineage.nodes if n.node_type in {GraphNodeType.EVIDENCE_SOURCE, GraphNodeType.EVIDENCE_RECORD, GraphNodeType.MEASUREMENT}]
        models = [n.payload.get("model_id", "UNKNOWN") for n in lineage.nodes if n.node_type == GraphNodeType.MODEL_EXECUTION]

        return ClaimExplanation(
            claim_id=claim_id,
            status=lineage.path_status,
            lineage=lineage,
            supporting_evidence=sources,
            models=models,
            versions=lineage.model_versions + lineage.calculation_versions,
            assumptions=lineage.assumptions,
            temporal_scope=claim_node.observed_at,
        )

    def impact_analysis(self, node_id: str) -> ImpactAnalysis:
        """High-level API answering: 'What downstream states depend on this node?'"""
        lineage = self.trace_forward(node_id)
        
        comps = [n.node_id for n in lineage.nodes if n.node_type == GraphNodeType.ENGINEERING_COMPUTATION]
        preds = [n.node_id for n in lineage.nodes if n.node_type == GraphNodeType.PREDICTION]
        decs = [n.node_id for n in lineage.nodes if n.node_type == GraphNodeType.DECISION]
        apps = [n.node_id for n in lineage.nodes if n.node_type == GraphNodeType.HUMAN_APPROVAL]
        outs = [n.node_id for n in lineage.nodes if n.node_type == GraphNodeType.OUTCOME]

        return ImpactAnalysis(
            node_id=node_id,
            dependent_computations=comps,
            dependent_predictions=preds,
            dependent_decisions=decs,
            dependent_approvals=apps,
            dependent_outcomes=outs,
            downstream_paths=[lineage],
        )

    def validate_graph(self) -> List[str]:
        """Validates graph consistency (orphan detection, invalid endpoints)."""
        errors = []
        for edge_id, edge in self.edges.items():
            if edge.source_id not in self.nodes:
                errors.append(f"Edge '{edge_id}' references non-existent source node '{edge.source_id}'")
            if edge.target_id not in self.nodes:
                errors.append(f"Edge '{edge_id}' references non-existent target node '{edge.target_id}'")
        return errors

    def to_deterministic_hash(self) -> str:
        """Computes deterministic SHA-256 hash of graph structure."""
        nodes_data = sorted([{"id": k, "type": v.node_type.value, "ts": v.observed_at} for k, v in self.nodes.items()], key=lambda x: x["id"])
        edges_data = sorted([{"id": k, "src": v.source_id, "tgt": v.target_id, "type": v.edge_type.value} for k, v in self.edges.items()], key=lambda x: x["id"])
        payload = json.dumps({"nodes": nodes_data, "edges": edges_data}, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
