/**
 * PLANT-X Voice-First Engineering Workstation — Canonical Domain & Agent Types
 */

export type WorkstationView = 'PROCESS' | 'PND' | '3D' | 'TRENDS' | 'SIMULATION' | 'EVIDENCE' | 'CHEMISTRY';

export type TruthState =
  | 'OBSERVED'
  | 'DERIVED'
  | 'INFERRED'
  | 'ASSUMED'
  | 'REPRESENTATIVE'
  | 'SIMULATED'
  | 'UNRESOLVED'
  | 'UNAVAILABLE';

export type ValidationState =
  | 'VALID'
  | 'VALID_WITH_WARNINGS'
  | 'INVALID'
  | 'OUT_OF_SCOPE'
  | 'UNAVAILABLE';

export type TrustState = 'PASS' | 'ABSTAIN';

export type AgentStatus = 'READY' | 'LISTENING' | 'THINKING' | 'EXECUTING' | 'SPEAKING' | 'CANCELLED';

export interface TimerState {
  isActive: boolean;
  totalSeconds: number;
  remainingSeconds: number;
  targetAction: string;
  targetParams: Record<string, any>;
  scheduledAtTimestamp: number;
  validationContext: {
    expectedAssetTag: string;
    expectedScenario: string;
  };
}

export interface Hypothesis {
  id: string; // e.g. 'H1'
  title: string;
  description: string;
  confidenceScore: number; // 0.0 to 1.0
  supportingEvidence: string[];
  contradictingEvidence: string[];
  discriminatingObservations: string[];
  nextRecommendedTest: string;
  truthState: TruthState;
}

export interface ProactiveSuggestion {
  id: string;
  timestamp: string;
  severity: 'INFO' | 'WARNING' | 'ALERT';
  message: string;
  evidenceAnchor: string;
  dismissed: boolean;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  transcript?: string;
  intent: string;
  entities: Record<string, any>;
  context: {
    selectedAssetTag: string;
    activeView: WorkstationView;
    scenario: string;
  };
  toolName: string;
  parameters: Record<string, any>;
  executionStatus: 'SUCCESS' | 'FAILURE' | 'CANCELLED' | 'ABSTAINED';
  resultSummary: string;
  stateDelta?: Record<string, any>;
}

export interface ChemicalComponent {
  id: string;
  name: string;
  formula: string;
  fraction: number; // 0.0 to 1.0
}

export interface ChemicalStream {
  streamId: string;
  name: string;
  phase: 'LIQUID' | 'VAPOR' | 'TWO_PHASE' | 'UNKNOWN';
  compositionBasis: 'MOLE_FRACTION' | 'MASS_FRACTION';
  components: ChemicalComponent[];
  temperatureK: number;
  pressureBar: number;
  massFlowKgH: number;
  originPort: string;
  destPort: string;
  unsupportedProperties: string[];
}

export interface PlantWorkstationState {
  // Navigation & Spatial Hierarchy
  activeView: WorkstationView;
  selectedAssetTag: string; // Canonical e.g. 'E-102' or 'E02'
  selectedStreamId: string; // e.g. 'S-102'
  highlightedPath: string[]; // List of equipment and stream IDs in active trace
  cameraFocusTag: string | null;

  // Plant & Simulation State
  scenario: 'normal' | 'disturbed';
  timeHr: number;
  isPlaying: boolean;
  foulingThresholdRf: number;
  currentRf: number;
  trustGateStatus: TrustState;
  activePolicy: 'PREDICTIVE_CLEANING_WINDOW' | 'FIXED_INTERVAL_FALLBACK';

  // Streams & Chemistry
  activeStream: ChemicalStream;

  // Timer & Scheduled Execution
  timer: TimerState;

  // Agent & Voice Interaction
  agentStatus: AgentStatus;
  lastTranscript: string;
  lastAgentResponse: string;
  isVoiceActive: boolean;
  isTtsSpeaking: boolean;

  // Investigation & Evidence
  activeHypotheses: Hypothesis[];
  activeHypothesisId: string | null;
  investigationRecommendation: string;

  // Proactive Intelligence & Auditing
  proactiveSuggestions: ProactiveSuggestion[];
  auditLog: AuditLogEntry[];
}

export interface ToolResult {
  success: boolean;
  message: string;
  stateDelta?: Partial<PlantWorkstationState>;
  auditDetails?: Record<string, any>;
}

export interface AgentTool {
  id: string;
  name: string;
  description: string;
  category: 'NAVIGATION' | 'SELECTION' | 'VISUALIZATION' | 'SIMULATION' | 'INVESTIGATION' | 'TIMER' | 'SYSTEM';
  inputSchema: Record<string, string>;
  execute: (params: Record<string, any>, currentState: PlantWorkstationState) => Promise<ToolResult> | ToolResult;
}
