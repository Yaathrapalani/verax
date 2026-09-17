export type PageView = 'overview' | 'exchangers' | 'forecast' | 'reliability' | 'evidence';
export type HorizonHours = 1 | 6 | 24;
export type ScenarioMode = 'normal' | 'disturbed';

export interface ExchangerState {
  tag: string;
  name: string;
  serviceName: string;
  rfCurrent: number;
  uaCurrent: number;
  uaClean: number;
  lmtdCurrent: number;
  qTubeCurrent: number;
  qShellCurrent: number;
  thermalDiscrepancy: number;
  dataQualityPct: number;
  status: 'OPERATIONAL_NOMINAL' | 'DEGRADATION_DETECTED' | 'MAINTENANCE_RECOMMENDED';
  recentRfTrajectory: number[];
}

export interface ForecastPoint {
  timestamp: string;
  hour: number;
  historicalRf?: number;
  ridgeForecast?: number;
  persistenceBaseline?: number;
  lowerBound?: number;
  upperBound?: number;
}

export interface ForecastMetrics {
  mae: number;
  rmse: number;
  r2: number;
  nmaeStd: number;
  relativeImprovementPct: number;
  bestAlpha: number;
}

export interface ReliabilityCheck {
  id: string;
  name: string;
  description: string;
  status: 'PASS' | 'FAIL' | 'WARN';
  value: string;
  threshold: string;
  isSimulatedDemo?: boolean;
}

export interface ReliabilityState {
  scenario: ScenarioMode;
  gatePassed: boolean;
  abstain: boolean;
  abstainReason?: string;
  activePolicy: 'PREDICTIVE_CLEANING_WINDOW' | 'FIXED_INTERVAL_FALLBACK';
  checks: ReliabilityCheck[];
  timestamp: string;
}

export interface DecisionRecommendation {
  status: 'CLEANING_RECOMMENDED' | 'ABSTAIN_FIXED_POLICY' | 'NOMINAL_MONITORING';
  title: string;
  subtitle: string;
  targetExchanger: string;
  recommendedWindowDays: number;
  estimatedCleaningCostUSD: number;
  estimatedFuelPenaltyPerDayUSD: number;
  humanApprovalRequired: true;
  requiresReview: boolean;
}

export interface EvidenceTraceStep {
  stepNumber: number;
  title: string;
  subtitle: string;
  status: 'VALIDATED' | 'AUDITED' | 'SIMULATED_DEMO' | 'ACTIVE';
  provenance: string;
  technicalSummary: string;
  keyMetrics: Record<string, string | number>;
}
