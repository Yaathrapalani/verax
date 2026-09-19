# Model Promotion Specification

## States
- `CANDIDATE`: Newly trained model undergoing validation.
- `BENCHMARKED`: Standard baseline or baseline model (e.g. Ridge).
- `CHALLENGER`: Proposed new baseline candidate.
- `PROMOTED`: Validated and promoted model.
- `REJECTED`: Rejected candidate.

## Rule
A candidate model is `PROMOTED` if and only if its Validation MAE strictly improves over the benchmark model without degrading stability or multi-exchanger safety. Selection on test split immediately causes status = `REJECTED`.
