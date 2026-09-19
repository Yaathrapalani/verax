# Frontend Data Model

## `PlantClientState` Interface Definition

```typescript
export interface PlantClientState {
  plant: {
    id: string;
    name: string;
    units: ProcessUnit[];
    streams: ProcessStream[];
  };
  selectedAssetTag: string; // Persistent across all views
  currentView: 'PROCESS' | 'PND' | '3D' | 'TRENDS' | 'SIMULATION' | 'EVIDENCE';
  simulationCase: {
    activeScenario: 'normal' | 'disturbed';
    tempOffset: number;
    flowOffset: number;
    simulatedMetrics: Record<string, number>;
  };
  trustGate: {
    status: 'PASS' | 'ABSTAIN';
    stressSigma: number;
    regime: 'HISTORICAL' | 'REGIME_OOD';
    fallbackActive: boolean;
  };
  evidenceGraph: {
    activeHypothesisId: string;
    nodes: EvidenceNode[];
  };
  thermodynamics: {
    propertyPackage: 'IDEAL_GAS';
    eosStatus: 'UNSUPPORTED';
    phase: 'VAPOR_GAS';
    transportStatus: 'UNAVAILABLE';
  };
}
```
