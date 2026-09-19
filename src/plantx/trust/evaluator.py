"""False Positive and False Negative evaluation support."""

from typing import Dict, Any, List
import numpy as np


class BinaryClassificationEvaluator:
    """Evaluates maintenance threshold outcome metrics (TP, FP, TN, FN, Precision, Recall, Specificity, F1)."""

    @staticmethod
    def evaluate_outcomes(
        realized_events: np.ndarray,
        predicted_interventions: np.ndarray,
    ) -> Dict[str, Any]:
        """
        realized_events: boolean array (True if future degradation exceeded maintenance threshold)
        predicted_interventions: boolean array (True if model recommended intervention)
        """
        tp = int(np.sum(realized_events & predicted_interventions))
        fp = int(np.sum((~realized_events) & predicted_interventions))
        fn = int(np.sum(realized_events & (~predicted_interventions)))
        tn = int(np.sum((~realized_events) & (~predicted_interventions)))

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "TP": tp,
            "FP": fp,
            "TN": tn,
            "FN": fn,
            "precision": precision,
            "recall": recall,
            "specificity": specificity,
            "FPR": fpr,
            "FNR": fnr,
            "F1": f1,
            "missed_event_count": fn,
            "unnecessary_intervention_count": fp,
        }
