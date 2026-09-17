import pytest
from src.foulx.replay.resolver import HistoricalStateResolver, VALID_EXCHANGERS

def test_resolver_min_max_timestamps():
    resolver = HistoricalStateResolver()
    min_t, max_t = resolver.get_min_max_timestamps()
    assert min_t == 0.0
    assert max_t == 63999.0

def test_resolver_raw_record_retrieval():
    resolver = HistoricalStateResolver()
    record, idx = resolver.resolve_raw_record(45000.0)
    assert record["Time_hr"] == 45000.0
    assert idx == 45000

def test_resolver_causal_history_no_future_leakage():
    resolver = HistoricalStateResolver()
    hist_df = resolver.resolve_causal_history(45000.0, window_hours=168)
    assert hist_df["Time_hr"].max() == 45000.0
    assert hist_df["Time_hr"].min() == 45000.0 - 168.0
    assert (hist_df["Time_hr"] > 45000.0).sum() == 0

def test_resolver_out_of_range():
    resolver = HistoricalStateResolver()
    with pytest.raises(ValueError, match="not found"):
        resolver.resolve_raw_record(99999.0)
