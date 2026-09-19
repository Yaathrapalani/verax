/**
 * PLANT-X Proactive Intelligence Engine
 * Evaluates current plant state and surfaces evidence-grounded, non-invasive observations.
 */

import type { PlantWorkstationState, ProactiveSuggestion } from './types';

export class ProactiveEngine {
  public evaluate(state: PlantWorkstationState): ProactiveSuggestion[] {
    const suggestions: ProactiveSuggestion[] = [];
    const timestamp = new Date().toLocaleTimeString();

    // 1. Regime Shift Alert
    if (state.scenario === 'disturbed' || state.trustGateStatus === 'ABSTAIN') {
      suggestions.push({
        id: 'sug-regime-ood',
        timestamp,
        severity: 'ALERT',
        message: 'Current operating state shifted outside historical training support. M5 Reliability Gate ABSTAIN active.',
        evidenceAnchor: 'M5_REGIME_SUPPORT_CHECK',
        dismissed: false
      });
    }

    // 2. Fouling Threshold Proximity for E-102
    if (state.selectedAssetTag === 'E-102' && state.currentRf > 0.8 * state.foulingThresholdRf) {
      suggestions.push({
        id: 'sug-fouling-threshold',
        timestamp,
        severity: 'WARNING',
        message: 'E-102 derived fouling resistance Rf is within 20% of 1.5e-7 m²·K/W cleaning threshold.',
        evidenceAnchor: 'E02_M4_RIDGE_TRAJECTORY',
        dismissed: false
      });
    }

    // 3. Unresolved Data Gap
    if (state.activeView === 'EVIDENCE' || state.activeView === 'PROCESS') {
      suggestions.push({
        id: 'sug-pressure-gap',
        timestamp,
        severity: 'INFO',
        message: 'Differential pressure ΔP sensor telemetry is UNAVAILABLE in historian stream. Hydraulic hypothesis H5 remains unvalidated.',
        evidenceAnchor: 'HISTORIAN_CHANNEL_AUDIT',
        dismissed: false
      });
    }

    return suggestions;
  }
}

export const proactiveEngine = new ProactiveEngine();
