"""Selective prediction and risk-coverage curve evaluator."""

from typing import List, Tuple, Dict, Any
import numpy as np
from src.plantx.trust.schemas import RiskCoveragePoint


class SelectivePredictionEvaluator:
    """Evaluates selective prediction trade-offs and generates risk-coverage curves."""

    @staticmethod
    def evaluate_risk_coverage_curve(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        uncertainty_scores: np.ndarray,
        thresholds: List[float],
    ) -> List[RiskCoveragePoint]:
        """
        Calculates coverage and risk (MAE) as acceptance threshold for uncertainty changes.
        Lower uncertainty score indicates higher confidence/acceptance.
        """
        results = []
        total_cnt = len(y_true)
        if total_cnt == 0:
            return results

        abs_errors = np.abs(y_true - y_pred)

        for thresh in sorted(thresholds):
            accepted_mask = uncertainty_scores <= thresh
            accepted_cnt = int(np.sum(accepted_mask))
            coverage = float(accepted_cnt / total_cnt)
            
            if accepted_cnt > 0:
                risk_mae = float(np.mean(abs_errors[accepted_mask]))
            else:
                risk_mae = 0.0

            results.append(
                RiskCoveragePoint(
                    threshold=float(thresh),
                    coverage=coverage,
                    risk_mae=risk_mae,
                    accepted_count=accepted_cnt,
                    total_count=total_cnt,
                )
            )
        return results
