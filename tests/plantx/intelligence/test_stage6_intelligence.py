"""Comprehensive test suite for Stage 6 Intelligence Core and 10 Killer Tests."""

import pytest
import hashlib
from pathlib import Path
from src.plantx.domain.truth_state import TruthState
from src.plantx.shadow.reconstructor import DigitalShadowReconstructor
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.intelligence.schemas import (
    FoulingState,
    FoulingPrognosis,
    ForecastStatus,
    ModelStatus,
)
from src.plantx.intelligence.engine import (
    IntelligenceEngine,
    IntelligenceEvidenceBridge,
    ModelEvaluator,
)
from src.foulx.replay import ReplayService, ReplayMode


@pytest.fixture
def replay_service():
    return ReplayService()


@pytest.fixture
def intelligence_engine(replay_service):
    return IntelligenceEngine(replay_service=replay_service)


# 1. FoulingState schema test
def test_fouling_state_schema(intelligence_engine):
    reconstructor = DigitalShadowReconstructor(replay_service=intelligence_engine.replay_service)
    shadow = reconstructor.reconstruct_snapshot(
        target_time=1000.0,
        bundles=[],
        temporal_observations=[],
    )
    state = intelligence_engine.compute_fouling_state("E01", shadow)
    assert isinstance(state, FoulingState)
    assert state.asset_id == "E01"
    assert state.timestamp == 1000.0
    assert state.status == "VALID"


# 2. Forecast contract test
def test_forecast_contract(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    assert isinstance(prog, FoulingPrognosis)
    assert prog.asset_id == "E01"
    assert prog.timestamp == 1000.0
    assert prog.horizon_hours == 24
    assert prog.target_definition == "R_f_derived(t+h)"
    assert prog.uncertainty_status == "NOT_IMPLEMENTED"
    assert prog.mechanism_claim == "NONE"


# 3. Persistence integration
def test_persistence_integration(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Persistence")
    assert prog.model_id == "Persistence"
    assert prog.status == ForecastStatus.AVAILABLE
    assert prog.prediction is not None


# 4. RecentTrend integration
def test_trend_integration(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="RecentTrend")
    assert prog.model_id == "RecentTrend"
    assert prog.status == ForecastStatus.AVAILABLE
    assert prog.prediction is not None


# 5. Ridge integration
def test_ridge_integration(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    assert prog.model_id == "Ridge"
    assert prog.status == ForecastStatus.AVAILABLE
    assert prog.prediction is not None


# Killer Test 1: Full Backward Lineage Trace
def test_killer_1_full_backward_lineage_trace(intelligence_engine):
    graph = EvidenceGraph()
    
    # 1. Temporal Evidence
    graph.add_node("obs-1", "Evidence", TruthState.OBSERVED.value, {"value": 0.00015})
    # 2. Digital Shadow
    graph.add_node("shadow-1", "State", TruthState.OBSERVED.value, {"target_time": 1000.0})
    graph.add_edge("obs-1", "shadow-1", EvidenceEdgeType.SUPPORTED_BY)
    # 3. Engineering State
    graph.add_node("eng-1", "State", TruthState.INFERRED.value, {"Rf_derived": 0.00015})
    graph.add_edge("shadow-1", "eng-1", EvidenceEdgeType.DERIVED_FROM)
    # 4. Fouling State
    graph.add_node("foul-1", "State", TruthState.INFERRED.value, {"current_rf": 0.00015})
    graph.add_edge("eng-1", "foul-1", EvidenceEdgeType.DERIVED_FROM)
    # 5. Prognosis
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    prog_node_id = IntelligenceEvidenceBridge.attach_prognosis_to_graph(graph, prog, "foul-1")

    trace = graph.trace_backward(prog_node_id)
    assert prog_node_id in trace
    assert "foul-1" in trace
    assert "eng-1" in trace
    assert "shadow-1" in trace
    assert "obs-1" in trace


# Killer Test 2: Future Information Leakage Rejection
def test_killer_2_future_leakage_rejection(intelligence_engine):
    # Attempting prediction beyond max timestamp or future data request
    prog = intelligence_engine.forecast("E01", timestamp=999999.0, horizon_hours=24, model_id="Ridge")
    assert prog.status == ForecastStatus.INVALID_INPUT
    assert prog.prediction is None


# Killer Test 3: Insufficient History Handling
def test_killer_3_insufficient_history(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=5.0, horizon_hours=24, model_id="Ridge")
    assert prog.status == ForecastStatus.INSUFFICIENT_HISTORY
    assert prog.prediction is None


# Killer Test 4: Deterministic Forecast
def test_killer_4_deterministic_forecast(intelligence_engine):
    prog1 = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    prog2 = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    assert prog1.model_dump() == prog2.model_dump()


# Killer Test 5: Benchmark Validation Parity
def test_killer_5_benchmark_validation_parity(intelligence_engine):
    df_all = intelligence_engine.replay_service.resolver._get_df()
    val_metrics = ModelEvaluator.evaluate_model_on_split(df_all, "E01", horizon_hours=24, split="validation")
    assert "mae" in val_metrics
    assert "rmse" in val_metrics
    assert val_metrics["mae"] > 0.0


# Killer Test 6: Test Split Promotion Rejection
def test_killer_6_test_split_promotion_rejection():
    status = ModelEvaluator.evaluate_candidate_promotion(
        val_metrics_baseline={"mae": 0.0002},
        val_metrics_candidate={"mae": 0.0001},
        selection_split="test",
    )
    assert status == ModelStatus.REJECTED


# Killer Test 7: Multi-exchanger Trade-off Exposure
def test_killer_7_exchanger_tradeoff_exposure(intelligence_engine):
    df_all = intelligence_engine.replay_service.resolver._get_df()
    m_e01 = ModelEvaluator.evaluate_model_on_split(df_all, "E01", horizon_hours=24, split="validation")
    m_e02 = ModelEvaluator.evaluate_model_on_split(df_all, "E02", horizon_hours=24, split="validation")
    assert m_e01 != m_e02


# Killer Test 8: Trace Model Metadata
def test_killer_8_model_metadata_trace(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    assert prog.model_id == "Ridge"
    assert prog.model_version == "1.0.0"
    assert prog.feature_version == "1.0.0"
    assert prog.training_scope == "synthetic physics-based benchmark"


# Killer Test 9: No Fabricated Uncertainty
def test_killer_9_no_fabricated_uncertainty(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    assert prog.uncertainty_status == "NOT_IMPLEMENTED"


# Killer Test 10: No Mechanism Claim
def test_killer_10_no_mechanism_claim(intelligence_engine):
    prog = intelligence_engine.forecast("E01", timestamp=1000.0, horizon_hours=24, model_id="Ridge")
    assert prog.mechanism_claim == "NONE"


# Source Immutability Check
def test_source_immutability():
    dataset_path = Path("data/raw/heat_exchanger_fouling_dataset.csv")
    h_before = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    
    # Run engine instantiation and forecast
    engine = IntelligenceEngine()
    engine.forecast("E01", timestamp=1000.0, horizon_hours=24)
    
    h_after = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    assert h_before == h_after
    assert h_before == "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"
