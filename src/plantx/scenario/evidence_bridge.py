"""Evidence Graph bridge connecting Stage 9 ScenarioCase backward to Stage 4 Evidence Graph."""

from src.plantx.domain.truth_state import TruthState
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.scenario.schemas import ScenarioCase


class ScenarioEvidenceBridge:
    """Connects ScenarioCase backward into Evidence Graph."""

    @staticmethod
    def attach_scenario_to_graph(
        graph: EvidenceGraph,
        scenario_case: ScenarioCase,
        baseline_node_id: str,
    ) -> str:
        scen_node_id = scenario_case.scenario_id
        graph.add_node(
            node_id=scen_node_id,
            node_type="Scenario",
            truth_state=TruthState.SIMULATED.value,
            payload=scenario_case.model_dump(),
        )
        graph.add_edge(
            source_id=baseline_node_id,
            target_id=scen_node_id,
            edge_type=EvidenceEdgeType.DERIVED_FROM,
        )
        return scen_node_id
