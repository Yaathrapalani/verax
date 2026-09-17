"""
Typed Pydantic Schemas for FOUL-X M4.0 Models and Features.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FeatureConfig(BaseModel):
    """Configuration for causal feature generation."""
    window_sizes: List[int] = Field(default_factory=lambda: [6, 24, 72, 168], description="Causal window sizes in hours")
    include_operating_variables: bool = Field(True, description="Include Crude_API, Crude_TAN, Crude_Chlorides")
    include_current_physics_state: bool = Field(True, description="Include R_f, UA, LMTD, Q_tube, Q_shell, thermal_discrepancy")


class TrainingConfig(BaseModel):
    """Configuration for model training and splits."""
    train_end_hour: float = Field(44799.0, description="End timestamp for training set")
    val_start_hour: float = Field(44800.0, description="Start timestamp for validation set")
    val_end_hour: float = Field(54399.0, description="End timestamp for validation set")
    test_start_hour: float = Field(54400.0, description="Start timestamp for test set")
    test_end_hour: float = Field(63999.0, description="End timestamp for test set")
    candidate_alphas: List[float] = Field(default_factory=lambda: [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0], description="Ridge alpha hyperparameters")
    random_seed: int = Field(42, description="Random seed for reproducibility")


class ModelPrediction(BaseModel):
    """Output prediction object from Ridge forecaster."""
    exchanger_id: str
    timestamp: float
    horizon_hours: int
    prediction: float
    model_name: str = "RidgeRegression"
    alpha: float
