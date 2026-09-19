"""
Deterministic Fouling Lifecycle Simulator for FOUL-X.

Orchestrates actual dataset timestamps and calls M2-M6/M9 pipeline without modifying source data or retraining models.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

from src.foulx.replay.service import ReplayService
from src.foulx.replay.schemas import ReplayMode, ReplaySnapshot
from src.foulx.decision.schemas import DecisionState
from src.foulx.gate.schemas import GateStatus
from src.foulx.simulation.schemas import (
    SimulationScenarioId,
    SimulationEventType,
    SimulationEventLogEntry,
    SimulationFrame,
    SimulationSummary,
)


class FoulingLifecycleSimulator:
    """
    FOUL-X Deterministic Fouling Lifecycle Simulator.
    Orchestrates sequential dataset evaluation and demo resets over real Time_hr rows.
    """

    def __init__(self, replay_service: Optional[ReplayService] = None):
        self.replay_service = replay_service or ReplayService()
        self.reset_simulated_state()

    def reset_simulated_state(self):
        """Resets active simulation memory to initial state."""
        self.active_scenario = SimulationScenarioId.FULL_END_TO_END
        self.frame_counter = 0
        self.event_counter = 0
        self.event_logs: List[SimulationEventLogEntry] = []
        self.is_simulated_cleaning_active = False
        self.simulated_rf_offset = 0.0

    def add_event(
        self,
        timestamp_hr: float,
        event_type: SimulationEventType,
        message: str,
        gate_status: GateStatus,
        decision: DecisionState,
        is_simulated: bool = False,
    ):
        """Appends deterministic event to simulation log."""
        self.event_counter += 1
        entry = SimulationEventLogEntry(
            sequence_id=self.event_counter,
            timestamp_hr=timestamp_hr,
            event_type=event_type,
            message=message,
            gate_status=gate_status,
            decision=decision,
            is_simulated_event=is_simulated,
        )
        self.event_logs.append(entry)

    def trigger_simulated_cleaning(self, current_timestamp_hr: float, exchanger_id: str = "E02") -> SimulationFrame:
        """
        Executes DEMO-ONLY simulated cleaning reset.
        Does NOT mutate source dataset or baseline model weights.
        """
        self.is_simulated_cleaning_active = True
        self.simulated_rf_offset = -1.0e-7  # Derived demo reset offset

        self.add_event(
            timestamp_hr=current_timestamp_hr,
            event_type=SimulationEventType.SIMULATED_CLEANING_RESET,
            message="SIMULATED CLEANING EVENT — DEMO RESET APPLIED (NOT OBSERVED HISTORICAL DATA)",
            gate_status=GateStatus.PASS,
            decision=DecisionState.OPERATE,
            is_simulated=True,
        )

        return self.get_frame_at_timestamp(
            timestamp_hr=current_timestamp_hr,
            exchanger_id=exchanger_id,
            scenario_id=self.active_scenario,
            mode=ReplayMode.NORMAL,
        )

    def get_frame_at_timestamp(
        self,
        timestamp_hr: float,
        exchanger_id: str = "E02",
        scenario_id: SimulationScenarioId = SimulationScenarioId.FULL_END_TO_END,
        mode: ReplayMode = ReplayMode.NORMAL,
    ) -> SimulationFrame:
        """
        Generates single SimulationFrame calling real M2-M6 pipeline via ReplayService.
        """
        snapshot = self.replay_service.get_snapshot(
            timestamp=timestamp_hr,
            exchanger_id=exchanger_id,
            scenario_mode=mode,
        )

        gate_status = snapshot.reliability_state.status
        decision = snapshot.decision_state.decision

        # Log significant event transitions deterministically
        if mode == ReplayMode.SHIFTED:
            self.add_event(
                timestamp_hr=timestamp_hr,
                event_type=SimulationEventType.REGIME_SHIFT_OOD,
                message="+6σ REGIME SHIFT TRIGGERED — M5 GATE ABSTAIN (REGIME_OOD) -> AI ACTION WITHHELD",
                gate_status=gate_status,
                decision=decision,
            )
        elif decision == DecisionState.CLEANING_REVIEW:
            self.add_event(
                timestamp_hr=timestamp_hr,
                event_type=SimulationEventType.CLEANING_REVIEW_TRIGGERED,
                message=f"CLEANING REVIEW TRIGGERED — {exchanger_id} Forecast Crosses Threshold Within Planning Horizon",
                gate_status=gate_status,
                decision=decision,
            )

        frame = SimulationFrame(
            frame_index=self.frame_counter,
            timestamp_hr=timestamp_hr,
            exchanger_id=exchanger_id,
            scenario_id=scenario_id,
            replay_snapshot=snapshot,
            is_simulated_cleaning_active=self.is_simulated_cleaning_active,
            simulated_rf_offset=self.simulated_rf_offset,
            event_logs=list(self.event_logs),
        )
        self.frame_counter += 1
        return frame

    def run_sequence(
        self,
        start_time_hr: float = 63200.0,
        end_time_hr: float = 63250.0,
        exchanger_id: str = "E02",
        scenario_id: SimulationScenarioId = SimulationScenarioId.FULL_END_TO_END,
    ) -> List[SimulationFrame]:
        """Runs a contiguous sequence of real dataset timestamps."""
        self.reset_simulated_state()
        self.active_scenario = scenario_id
        frames = []

        self.add_event(
            timestamp_hr=start_time_hr,
            event_type=SimulationEventType.SYSTEM_INIT,
            message="PLANT-X / FOUL-X DEMO SIMULATION INITIALIZED",
            gate_status=GateStatus.PASS,
            decision=DecisionState.OPERATE,
        )

        curr_t = start_time_hr
        while curr_t <= end_time_hr:
            mode = ReplayMode.NORMAL
            # If scenario is OOD_REGIME_SHIFT or in final frames of FULL_END_TO_END demo
            if scenario_id == SimulationScenarioId.OOD_REGIME_SHIFT or (scenario_id == SimulationScenarioId.FULL_END_TO_END and curr_t >= end_time_hr - 2):
                mode = ReplayMode.SHIFTED

            frame = self.get_frame_at_timestamp(curr_t, exchanger_id, scenario_id, mode)
            frames.append(frame)
            curr_t += 1.0

        return frames
