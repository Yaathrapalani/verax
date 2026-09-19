# Freshness Policy Specification

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  

---

## Observation Freshness Evaluation

Observation age is calculated as:
$$\text{Age} = T_{\text{target}} - t_{\text{observed}}$$

### Classification
- **`FRESH`**: $\text{Age} \le \text{max\_acceptable\_age\_hours}$ configured in `FreshnessPolicy`.
- **`STALE`**: $\text{Age} > \text{max\_acceptable\_age\_hours}$. Causes `usability` to drop to `CONDITIONALLY_USABLE` or `UNAVAILABLE`.
- **`FRESHNESS_UNSPECIFIED`**: No age limit configured in policy.
