"""
FOUL-X M10.0 FastAPI Backend Service Application.
Exposes read-only health, manifest, exchangers, and deterministic replay endpoints.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Robustly resolve project root and load root .env if present (without overriding process env)
try:
    from dotenv import load_dotenv
    root_env = Path(__file__).resolve().parents[3] / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env, override=False)
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.foulx.replay.service import ReplayService
from src.foulx.replay.schemas import ReplayMode, ReplaySnapshot, ReplayManifest
from src.foulx.replay.resolver import VALID_EXCHANGERS
from src.foulx.simulation.lifecycle import FoulingLifecycleSimulator
from src.foulx.simulation.schemas import SimulationScenarioId
from src.plantx.voice.session import router as voice_router

app = FastAPI(
    title="FOUL-X Industrial Intelligence API",
    description="Trust-Gated Heat Exchanger Fouling Prognosis & Deterministic Replay Engine",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Voice Infrastructure Router
app.include_router(voice_router)

# Global replay service instance (singleton)
replay_service: Optional[ReplayService] = None
simulator_service: Optional[FoulingLifecycleSimulator] = None


def get_replay_service() -> ReplayService:
    global replay_service
    if replay_service is None:
        replay_service = ReplayService()
    return replay_service


def get_simulator() -> FoulingLifecycleSimulator:
    global simulator_service
    if simulator_service is None:
        simulator_service = FoulingLifecycleSimulator()
    return simulator_service


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    Reports service availability, artifact status, and readiness.
    Does NOT claim live plant connectivity.
    """
    srv = get_replay_service()
    manifest = srv.get_manifest()

    return {
        "status": "healthy",
        "service": "foulx-api",
        "version": "1.0.0",
        "artifacts_loaded": True,
        "configuration_loaded": True,
        "core_ready": True,
        "plant_connectivity": "DISCONNECTED_PROTOTYPE_MODE",
        "representation": "INDUSTRIAL DIGITAL SHADOW — PROTOTYPE",
        "dataset_checksum": manifest.dataset_checksum,
        "timestamp_range": {
            "min_time_hr": manifest.min_timestamp,
            "max_time_hr": manifest.max_timestamp,
        },
    }


@app.get("/api/manifest")
def get_manifest() -> Dict[str, Any]:
    """Returns replay manifest metadata."""
    srv = get_replay_service()
    return srv.get_manifest().to_dict()


@app.get("/api/exchangers")
def get_exchangers() -> Dict[str, str]:
    """Returns supported exchanger IDs and names."""
    return VALID_EXCHANGERS


@app.get("/api/replay/snapshot", response_model=None)
def get_replay_snapshot(
    time_hr: float = Query(..., description="Timestamp in hours (Time_hr)"),
    exchanger_id: str = Query("E01", description="Target exchanger ID"),
    scenario: str = Query("NORMAL", description="Scenario mode: NORMAL or SHIFTED"),
) -> Dict[str, Any]:
    """
    Constructs deterministic ReplaySnapshot for given timestamp, exchanger, and scenario.
    Guarantees ZERO future data leakage.
    """
    srv = get_replay_service()
    
    mode_upper = scenario.upper()
    if mode_upper not in ["NORMAL", "SHIFTED"]:
        raise HTTPException(status_code=400, detail=f"Invalid scenario mode '{scenario}'. Must be NORMAL or SHIFTED.")

    scen_mode = ReplayMode.NORMAL if mode_upper == "NORMAL" else ReplayMode.SHIFTED

    try:
        snapshot = srv.get_snapshot(
            timestamp=time_hr,
            exchanger_id=exchanger_id,
            scenario_mode=scen_mode,
        )
        return snapshot.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/simulation/frame")
def get_simulation_frame(
    time_hr: float = Query(63241.0, description="Timestamp in hours"),
    exchanger_id: str = Query("E02", description="Target exchanger ID"),
    scenario: str = Query("FULL_END_TO_END", description="Simulation scenario"),
    shifted: bool = Query(False, description="True to force +6σ regime shift"),
) -> Dict[str, Any]:
    """Generates a deterministic simulation frame at timestamp time_hr."""
    sim = get_simulator()
    mode = ReplayMode.SHIFTED if shifted else ReplayMode.NORMAL
    scen_id = SimulationScenarioId.FULL_END_TO_END
    if scenario in SimulationScenarioId.__members__:
        scen_id = SimulationScenarioId[scenario]

    frame = sim.get_frame_at_timestamp(
        timestamp_hr=time_hr,
        exchanger_id=exchanger_id,
        scenario_id=scen_id,
        mode=mode,
    )
    return frame.model_dump()


@app.post("/api/simulation/clean")
def trigger_simulated_clean(
    time_hr: float = Query(63241.0, description="Current timestamp in hours"),
    exchanger_id: str = Query("E02", description="Target exchanger ID"),
) -> Dict[str, Any]:
    """Triggers demo-only simulated cleaning reset."""
    sim = get_simulator()
    frame = sim.trigger_simulated_cleaning(current_timestamp_hr=time_hr, exchanger_id=exchanger_id)
    return frame.model_dump()
