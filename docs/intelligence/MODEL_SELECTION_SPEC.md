# Model Selection Specification

## Overview
Model selection determines which predictive model is selected for production benchmark status.

## Rule
1. Models must be evaluated strictly on the **Validation Split** (\(t = 44,800 \dots 54,399\)).
2. Under no circumstances may Test split (\(t = 54,400 \dots 63,999\)) performance be used for model selection.
3. Candidate models are evaluated across all operational horizons (1h, 6h, 24h) and exchangers (\(\text{E01} \dots \text{E05}\)).
