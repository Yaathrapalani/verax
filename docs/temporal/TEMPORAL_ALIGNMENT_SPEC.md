# Temporal Alignment Specification

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  

---

## Causal Alignment & Anti-Leakage Invariant

`TemporalEvidenceEngine.align_causally()` strictly filters observations to include only those where:
$$t_{\text{observed}} \le T_{\text{target}}$$

### Zero-Leakage Guarantee
Passing future observations ($t > T$) with `strict_causal=True` immediately raises a `CausalTemporalLeakageError`. Future observations $T+1, T+5, T+30$ can NEVER influence state estimation at $T$.
