# Validation Plan

## Main experiment
Evaluate three policies on held-out historical/synthetic time periods:

1. Fixed-policy baseline
2. Ungated forecast-driven policy
3. FOUL-X gated policy

## Required segmentation
- normal/in-distribution periods
- labelled cleaning-cycle transitions where available
- synthetically perturbed/OOD periods

## Primary measures
- useful recommendation rate
- harmful/false recommendation rate
- abstention rate
- decision consequence relative to fixed policy

## Secondary measures
- forecast error
- interval calibration if implemented
- inference latency
- reproducibility

## Red-team cases
- missing sensor values
- impossible/range-violating values
- abrupt sensor drift
- unseen operating regime
- cleaning event discontinuity
- insufficient history
- unstable forecast

## Acceptance principle
A more accurate forecast is not sufficient if it produces more harmful decisions. The gated system must be evaluated as a decision policy.
