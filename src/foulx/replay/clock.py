"""
Deterministic Replay Clock Engine for FOUL-X M9.0.

Provides deterministic clock state operations over dataset timestamps (t = 0..63999).
Wall-clock time does NOT control engineering state.
"""

from typing import Dict, Any, List, Optional


class ReplayClock:
    """
    Deterministic Replay Clock Engine.
    Operates over explicit discrete dataset timestamps (t_min=0.0, t_max=63999.0, step=1.0).
    """

    def __init__(
        self,
        min_timestamp: float = 0.0,
        max_timestamp: float = 63999.0,
        step_hours: float = 1.0,
        initial_timestamp: Optional[float] = None,
    ):
        self.min_timestamp = float(min_timestamp)
        self.max_timestamp = float(max_timestamp)
        self.step_hours = float(step_hours)
        self.current_timestamp = float(initial_timestamp if initial_timestamp is not None else self.min_timestamp)
        self.is_playing = False

    def seek(self, timestamp: float) -> float:
        """Seeks strictly to requested timestamp if within bounds."""
        t_val = float(timestamp)
        if t_val < self.min_timestamp or t_val > self.max_timestamp:
            raise ValueError(
                f"Requested timestamp {t_val} out of valid dataset range [{self.min_timestamp}, {self.max_timestamp}]!"
            )
        self.current_timestamp = t_val
        return self.current_timestamp

    def step_forward(self) -> float:
        """Increments current timestamp by step_hours."""
        next_t = self.current_timestamp + self.step_hours
        if next_t > self.max_timestamp:
            next_t = self.max_timestamp
        self.current_timestamp = next_t
        return self.current_timestamp

    def step_backward(self) -> float:
        """Decrements current timestamp by step_hours."""
        prev_t = self.current_timestamp - self.step_hours
        if prev_t < self.min_timestamp:
            prev_t = self.min_timestamp
        self.current_timestamp = prev_t
        return self.current_timestamp

    def reset(self, start_timestamp: Optional[float] = None) -> float:
        """Resets clock to initial or specified start timestamp."""
        self.is_playing = False
        target = start_timestamp if start_timestamp is not None else self.min_timestamp
        return self.seek(target)

    def start(self):
        """Sets playback state to playing."""
        self.is_playing = True

    def pause(self):
        """Sets playback state to paused."""
        self.is_playing = False
