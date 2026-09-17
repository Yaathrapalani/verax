import pytest
import pandas as pd
from src.foulx.evaluation.perturbations import SyntheticRegimeShiftPerturber

def test_perturbation_does_not_mutate_original():
    perturber = SyntheticRegimeShiftPerturber(shift_factor=6.0)
    raw = {"E01_Crude_Tube_T_In_degC": 150.0, "E01_Crude_Tube_m_kg_s": 50.0}
    perturbed = perturber.perturb_raw_record(raw, tag="E01")
    
    assert raw["E01_Crude_Tube_T_In_degC"] == 150.0
    assert perturbed["E01_Crude_Tube_T_In_degC"] > 150.0

def test_feature_vector_perturbation():
    perturber = SyntheticRegimeShiftPerturber(shift_factor=6.0)
    feat = pd.Series({"T_In": 150.0, "other_feat": 1.0})
    perturbed_feat = perturber.perturb_feature_vector(feat)

    assert feat["T_In"] == 150.0
    assert perturbed_feat["T_In"] > 150.0
    assert perturber.get_spec()["canonical_data_mutated"] is False
