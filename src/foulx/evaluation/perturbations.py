"""
Deterministic Synthetic Regime-Shift Perturbation Module for FOUL-X M7.0.

Provides controlled, reproducible synthetic perturbations to move operating state
outside historical training support (t <= 44,799) without modifying raw dataset files.
"""

from typing import Dict, Any, List, Optional
import pandas as pd


class SyntheticRegimeShiftPerturber:
    """
    Deterministic Synthetic Regime-Shift Stress Test Perturber.

    DOES NOT represent real industrial physical plant failure.
    Label: synthetic regime-shift stress test.

    PURPOSE:
    Test whether M5 Reliability Gate regime-support check detects state outside
    historical training support and forces GATED policy to fall back to FIXED policy.
    """

    def __init__(self, shift_factor: float = 6.0, shifted_features: Optional[List[str]] = None):
        self.shift_factor = shift_factor
        self.shifted_features = shifted_features or [
            "Crude_Tube_T_In_degC",
            "Crude_Tube_m_kg_s",
            "Shell_T_In_degC",
        ]

    def perturb_raw_record(self, raw_record: Dict[str, Any], tag: str = "E01") -> Dict[str, Any]:
        """
        Applies deterministic shift factor to selected process variables in raw record.
        Returns a NEW record dict without mutating the original.
        """
        perturbed = dict(raw_record)
        # Shift target variables by adding shift_factor std-like offsets or scaling
        for feature in self.shifted_features:
            full_key = f"{tag}_{feature}"
            if full_key in perturbed and isinstance(perturbed[full_key], (int, float)):
                # Multiply input by shift_factor or shift by significant physical delta
                perturbed[full_key] = float(perturbed[full_key]) * (1.0 + 0.15 * self.shift_factor)
            elif feature in perturbed and isinstance(perturbed[feature], (int, float)):
                perturbed[feature] = float(perturbed[feature]) * (1.0 + 0.15 * self.shift_factor)
        return perturbed

    def perturb_feature_vector(self, feature_vector: pd.Series) -> pd.Series:
        """
        Applies deterministic shift to feature vector evaluated by M5 regime checker.
        Returns a NEW pd.Series without mutating the original.
        """
        perturbed = feature_vector.copy()
        for col in perturbed.index:
            # Shift operating temperature or flow channels
            if any(target in col for target in ["T_In", "m_kg_s", "Q_tube", "Crude_API"]):
                perturbed[col] = float(perturbed[col]) + self.shift_factor * 1.5
        return perturbed

    def get_spec(self) -> Dict[str, Any]:
        """Returns deterministic specification of the perturbation."""
        return {
            "label": "synthetic regime-shift stress test",
            "shift_factor": self.shift_factor,
            "shifted_features": self.shifted_features,
            "method": "deterministic additive/multiplicative feature offset outside 4.0 std training support",
            "isolated": True,
            "canonical_data_mutated": False,
        }
