# Fouling State Specification

## Overview
`FoulingState` represents the canonical engineering fouling state for an asset at evaluation timestamp \(T\).

## Schema
- `asset_id`: String identifier (e.g. `E01`).
- `timestamp`: Float timestamp in hours (\(T\)).
- `current_rf_derived`: SI-normalized thermal fouling resistance (\(\text{m}^2\text{K/W}\)).
- `recent_delta_rf`: Difference in \(R_f\) over historical window (168 hours).
- `recent_growth_rate`: Observed rate of \(R_f\) change (\(\text{m}^2\text{K/W per hour}\)).
- `historical_context_hours`: Window depth (default: 168h).
- `status`: Validity status (`VALID` or `UNAVAILABLE`).
- `truth_state`: Truth classification (`INFERRED` or `UNRESOLVED`).
- `provenance`: Immutable calculation provenance.
