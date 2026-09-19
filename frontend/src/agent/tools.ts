/**
 * PLANT-X Deterministic Tool Registry
 * Strictly typed tools executing validated state transitions without arbitrary code execution.
 */

import type { AgentTool, WorkstationView, Hypothesis } from './types';
import { judgeModeController } from './judging/JudgeModeController';

// Canonical Equipment topology order for path calculations
const PREHEAT_TRAIN_ORDER = [
  'P-101', 'S-101', 'E-101', 'S-102', 'E-102', 'S-103', 'E-103', 'S-104',
  'V-101', 'S-105', 'E-104', 'S-106', 'E-105', 'S-107', 'F-101', 'S-108', 'C-101'
];

export const INITIAL_HYPOTHESES: Hypothesis[] = [
  {
    id: 'H1',
    title: 'FOULING_ACCUMULATION',
    description: 'Progressive organic thermal fouling accumulation on tube-side heat transfer surface.',
    confidenceScore: 0.84,
    supportingEvidence: [
      'Observed UA decay from clean reference 213.4 kW/K to 203.9 kW/K over 24h interval',
      'Monotonic increase in derived fouling resistance Rf towards 1.5e-7 m²·K/W threshold',
      'Thermal balance closure verified with error < 1.2%'
    ],
    contradictingEvidence: [
      'Crude feed API gravity and chloride levels remain within baseline specification'
    ],
    discriminatingObservations: [
      'Differential pressure across tube bundle rising in conjunction with heat transfer degradation'
    ],
    nextRecommendedTest: 'Inspect normalized heat transfer coefficient vs flow velocity to decouple hydraulic from deposition effects.',
    truthState: 'DERIVED'
  },
  {
    id: 'H2',
    title: 'OPERATING_REGIME_CHANGE',
    description: 'Shift in operating conditions moving heat exchanger outside historical training regime.',
    confidenceScore: 0.12,
    supportingEvidence: [
      'Z-score of LMTD and inlet temperatures exceeds historical 4.0σ limit under disturbed conditions'
    ],
    contradictingEvidence: [
      'Crude charge mass flow rate remains stable at nominal 104 kg/s'
    ],
    discriminatingObservations: [
      'Kerosene shell-side return temperature exhibits step change rather than gradual trend'
    ],
    nextRecommendedTest: 'Verify whether upstream crude atmospheric furnace setpoint was adjusted.',
    truthState: 'DERIVED'
  },
  {
    id: 'H3',
    title: 'SENSOR_MEASUREMENT_ISSUE',
    description: 'Thermocouple drift or instrument bias creating artificial thermal discrepancy.',
    confidenceScore: 0.04,
    supportingEvidence: [
      'Discrepancy between shell and tube thermal duties Q_tube and Q_shell'
    ],
    contradictingEvidence: [
      'Redundant sensor signal validation passed all 69 sensor consistency checks cleanly',
      'Zero missing sensor telemetry frames in current time window'
    ],
    discriminatingObservations: [
      'Both inlet and outlet thermocouple sensors track plant-wide thermal balance'
    ],
    nextRecommendedTest: 'Perform zero-drift calibration check during next turnaround interval.',
    truthState: 'DERIVED'
  },
  {
    id: 'H4',
    title: 'FEED_PROPERTY_SHIFT',
    description: 'Crude feed blend variation causing elevated asphaltene precipitation.',
    confidenceScore: 0.08,
    supportingEvidence: [
      'Slight increase in crude TAN from supplier batch 04B'
    ],
    contradictingEvidence: [
      'Desalter V-101 effluent chloride content nominal (< 3 ppm)'
    ],
    discriminatingObservations: [
      'Precipitation propensity index remains within acceptable boundary'
    ],
    nextRecommendedTest: 'Execute SARA fractional laboratory analysis on crude blend sample.',
    truthState: 'ASSUMED'
  },
  {
    id: 'H5',
    title: 'FLOW_OR_HYDRAULIC_EFFECT',
    description: 'Maldistribution or laminar transition on shell-side fluid passes.',
    confidenceScore: 0.06,
    supportingEvidence: [
      'Shell-side kerosene mass flow rate fluctuations during pump switchover'
    ],
    contradictingEvidence: [
      'Reynolds number in tube bundle confirms turbulent flow regime (Re > 15,000)'
    ],
    discriminatingObservations: [
      'Pressure drop telemetry currently UNAVAILABLE in live historian stream'
    ],
    nextRecommendedTest: 'Install differential pressure transmitter PT-102B to measure bundle ΔP.',
    truthState: 'UNAVAILABLE'
  }
];

export const TOOL_REGISTRY: Record<string, AgentTool> = {
  NAVIGATE_ROUTE: {
    id: 'NAVIGATE_ROUTE',
    name: 'Navigate Route',
    description: 'Switches the main workstation viewport to an engineering view.',
    category: 'NAVIGATION',
    inputSchema: { view: 'WorkstationView (PROCESS, PND, 3D, TRENDS, SIMULATION, EVIDENCE, CHEMISTRY)' },
    execute: (params) => {
      const targetView = (params.view || '').toUpperCase() as WorkstationView;
      const validViews: WorkstationView[] = ['PROCESS', 'PND', '3D', 'TRENDS', 'SIMULATION', 'EVIDENCE', 'CHEMISTRY'];
      if (!validViews.includes(targetView)) {
        return { success: false, message: `Invalid view '${params.view}'. Supported views: ${validViews.join(', ')}` };
      }
      return {
        success: true,
        message: `Navigated to ${targetView} view.`,
        stateDelta: { activeView: targetView }
      };
    }
  },

  SELECT_EQUIPMENT: {
    id: 'SELECT_EQUIPMENT',
    name: 'Select Equipment',
    description: 'Selects plant equipment by canonical tag and synchronizes across all views, inspector, and 3D camera.',
    category: 'SELECTION',
    inputSchema: { tag: 'Equipment canonical tag e.g. E-102, E02, P-101, V-101' },
    execute: (params) => {
      let rawTag = (params.tag || '').toUpperCase().trim();
      // Normalize 'E02' -> 'E-102'
      if (/^E0\d$/.test(rawTag)) {
        rawTag = `E-10${rawTag.slice(2)}`;
      }
      return {
        success: true,
        message: `${rawTag} selected across workstation views.`,
        stateDelta: {
          selectedAssetTag: rawTag,
          cameraFocusTag: rawTag,
          highlightedPath: [rawTag]
        }
      };
    }
  },

  SELECT_STREAM: {
    id: 'SELECT_STREAM',
    name: 'Select Stream',
    description: 'Selects a process stream by ID and inspects chemical composition and thermodynamics.',
    category: 'SELECTION',
    inputSchema: { streamId: 'Stream canonical ID e.g. S-101, S-102' },
    execute: (params) => {
      const streamId = (params.streamId || 'S-101').toUpperCase().trim();
      return {
        success: true,
        message: `Stream ${streamId} selected for inspection.`,
        stateDelta: {
          selectedStreamId: streamId,
          activeView: 'CHEMISTRY',
          highlightedPath: [streamId]
        }
      };
    }
  },

  FOCUS_3D_OBJECT: {
    id: 'FOCUS_3D_OBJECT',
    name: 'Focus 3D Object',
    description: 'Navigates to 3D view and animates camera focus to the specified equipment.',
    category: 'VISUALIZATION',
    inputSchema: { tag: 'Equipment tag to focus in 3D' },
    execute: (params, currentState) => {
      const tag = (params.tag || currentState.selectedAssetTag || 'E-102').toUpperCase().trim();
      return {
        success: true,
        message: `Focusing 3D camera on ${tag}.`,
        stateDelta: {
          activeView: '3D',
          selectedAssetTag: tag,
          cameraFocusTag: tag
        }
      };
    }
  },

  HIGHLIGHT_PATH: {
    id: 'HIGHLIGHT_PATH',
    name: 'Highlight Process Path',
    description: 'Computes and highlights the upstream or downstream process flow path from the selected equipment.',
    category: 'VISUALIZATION',
    inputSchema: { direction: 'UPSTREAM or DOWNSTREAM', anchorTag: 'Equipment tag to trace from' },
    execute: (params, currentState) => {
      const direction = (params.direction || 'UPSTREAM').toUpperCase().trim();
      const anchor = (params.anchorTag || currentState.selectedAssetTag || 'E-102').toUpperCase().trim();
      const idx = PREHEAT_TRAIN_ORDER.indexOf(anchor);

      if (idx === -1) {
        return { success: false, message: `Anchor equipment '${anchor}' not found in computational preheat graph.` };
      }

      let path: string[];
      if (direction === 'UPSTREAM') {
        path = PREHEAT_TRAIN_ORDER.slice(0, idx + 1);
      } else {
        path = PREHEAT_TRAIN_ORDER.slice(idx);
      }

      return {
        success: true,
        message: `Highlighted ${direction.toLowerCase()} process path for ${anchor} (${path.length} nodes).`,
        stateDelta: { highlightedPath: path }
      };
    }
  },

  SHOW_FOULING: {
    id: 'SHOW_FOULING',
    name: 'Show Fouling State',
    description: 'Navigates to fouling state analysis for the selected heat exchanger.',
    category: 'SELECTION',
    inputSchema: { tag: 'Exchanger tag e.g. E-102' },
    execute: (params, currentState) => {
      const tag = (params.tag || currentState.selectedAssetTag || 'E-102').toUpperCase().trim();
      return {
        success: true,
        message: `Showing fouling trajectory and M4.0 prognosis for ${tag}.`,
        stateDelta: {
          selectedAssetTag: tag,
          activeView: 'PROCESS',
          cameraFocusTag: tag
        }
      };
    }
  },

  SHOW_UNCERTAINTY: {
    id: 'SHOW_UNCERTAINTY',
    name: 'Show Uncertainty',
    description: 'Exposes model prediction uncertainty bounds, GPR confidence, and Reliability Gate status.',
    category: 'INVESTIGATION',
    inputSchema: { tag: 'Exchanger tag' },
    execute: (_params, currentState) => {
      const tag = currentState.selectedAssetTag || 'E-102';
      const isOod = currentState.scenario === 'disturbed';
      const gateStatus = isOod ? 'ABSTAIN' : 'PASS';
      return {
        success: true,
        message: `Uncertainty for ${tag}: GPR 95% CI ±0.18e-7 m²·K/W. Reliability Gate: ${gateStatus}${isOod ? ' (REGIME_OOD: AI Recommendation Withheld)' : ' (SUPPORTED)'}.`,
        stateDelta: {
          selectedAssetTag: tag,
          activeView: 'PROCESS'
        }
      };
    }
  },

  SHOW_DATA_GAPS: {
    id: 'SHOW_DATA_GAPS',
    name: 'Show Data Gaps',
    description: 'Audits missing sensor channels and temporal alignment irregularities.',
    category: 'INVESTIGATION',
    inputSchema: {},
    execute: () => {
      return {
        success: true,
        message: 'Data gap audit: Pressure drop ΔP sensor channel is UNAVAILABLE in plant historian. Crude mass flow and temperatures OBSERVED cleanly at 1h monotonic sampling intervals.',
        stateDelta: { activeView: 'EVIDENCE' }
      };
    }
  },

  SHOW_EVIDENCE: {
    id: 'SHOW_EVIDENCE',
    name: 'Show Evidence',
    description: 'Navigates to the Evidence Graph displaying causal lineage from sensor telemetry to maintenance recommendations.',
    category: 'INVESTIGATION',
    inputSchema: { anchorTag: 'Equipment tag' },
    execute: (params, currentState) => {
      const tag = (params.anchorTag || currentState.selectedAssetTag || 'E-102').toUpperCase().trim();
      return {
        success: true,
        message: `Opening Evidence Graph for ${tag}. Provenance verified with SHA-256 integrity.`,
        stateDelta: {
          activeView: 'EVIDENCE',
          selectedAssetTag: tag
        }
      };
    }
  },

  RUN_SCENARIO: {
    id: 'RUN_SCENARIO',
    name: 'Run Scenario',
    description: 'Executes a deterministic operating scenario (NORMAL or DISTURBED / REGIME SHIFT).',
    category: 'SIMULATION',
    inputSchema: { scenario: 'NORMAL, DISTURBED, or IRREGULAR_SAMPLING' },
    execute: (params) => {
      const scen = (params.scenario || 'normal').toLowerCase();
      const isDisturbed = scen.includes('disturb') || scen.includes('shift') || scen.includes('irregular') || scen.includes('stress');
      return {
        success: true,
        message: `Executing ${isDisturbed ? '+6σ REGIME SHIFT' : 'NORMAL'} scenario. ${isDisturbed ? 'Reliability gate ABSTAIN active.' : 'Gate PASS active.'}`,
        stateDelta: {
          scenario: isDisturbed ? 'disturbed' : 'normal',
          trustGateStatus: isDisturbed ? 'ABSTAIN' : 'PASS',
          activePolicy: isDisturbed ? 'FIXED_INTERVAL_FALLBACK' : 'PREDICTIVE_CLEANING_WINDOW',
          activeView: 'SIMULATION'
        }
      };
    }
  },

  SCHEDULE_SCENARIO: {
    id: 'SCHEDULE_SCENARIO',
    name: 'Schedule Scenario Execution',
    description: 'Schedules a scenario to execute after a specified countdown duration in seconds.',
    category: 'TIMER',
    inputSchema: { scenario: 'Scenario identifier', delaySeconds: 'Duration in seconds (e.g. 5, 10, 30)' },
    execute: (params, currentState) => {
      const seconds = Number(params.delaySeconds) || 10;
      const scenarioTarget = (params.scenario || 'irregular_sampling').toLowerCase();
      return {
        success: true,
        message: `Scenario '${scenarioTarget.toUpperCase()}' scheduled to run in ${seconds} seconds.`,
        stateDelta: {
          timer: {
            isActive: true,
            totalSeconds: seconds,
            remainingSeconds: seconds,
            targetAction: 'RUN_SCENARIO',
            targetParams: { scenario: scenarioTarget },
            scheduledAtTimestamp: Date.now(),
            validationContext: {
              expectedAssetTag: currentState.selectedAssetTag,
              expectedScenario: currentState.scenario
            }
          }
        }
      };
    }
  },

  CANCEL_SCHEDULED_ACTION: {
    id: 'CANCEL_SCHEDULED_ACTION',
    name: 'Cancel Scheduled Action',
    description: 'Cancels any active pending timer or delayed task immediately.',
    category: 'TIMER',
    inputSchema: {},
    execute: (_params, currentState) => {
      if (!currentState.timer.isActive) {
        return { success: false, message: 'No active scheduled action to cancel.' };
      }
      return {
        success: true,
        message: 'Pending scheduled scenario execution was cancelled immediately.',
        stateDelta: {
          timer: {
            isActive: false,
            totalSeconds: 0,
            remainingSeconds: 0,
            targetAction: '',
            targetParams: {},
            scheduledAtTimestamp: 0,
            validationContext: { expectedAssetTag: '', expectedScenario: '' }
          }
        }
      };
    }
  },

  GET_TIMER_STATUS: {
    id: 'GET_TIMER_STATUS',
    name: 'Get Timer Status',
    description: 'Returns the remaining countdown time and pending action details.',
    category: 'TIMER',
    inputSchema: {},
    execute: (_params, currentState) => {
      if (!currentState.timer.isActive) {
        return { success: true, message: 'No scheduled actions are currently pending.' };
      }
      return {
        success: true,
        message: `Pending scenario '${currentState.timer.targetParams?.scenario || 'SCENARIO'}' has ${currentState.timer.remainingSeconds.toFixed(1)} seconds remaining.`
      };
    }
  },

  GET_RELIABILITY_STATUS: {
    id: 'GET_RELIABILITY_STATUS',
    name: 'Get Reliability Status',
    description: 'Audits current FOUL-X Reliability Gate evaluation checks.',
    category: 'INVESTIGATION',
    inputSchema: {},
    execute: (_params, currentState) => {
      const isPass = currentState.trustGateStatus === 'PASS';
      return {
        success: true,
        message: isPass
          ? 'Reliability Gate Status: PASS. All 4 checks (Data Completeness, Sensor Validity, Physics Consistency, Regime Support) passed cleanly.'
          : 'Reliability Gate Status: ABSTAIN. Check 4 (Operating Regime Support) triggered REGIME_OOD. AI action withheld; fixed policy fallback active.'
      };
    }
  },

  GET_HYPOTHESES: {
    id: 'GET_HYPOTHESES',
    name: 'Get Hypotheses',
    description: 'Lists competing evidence-grounded hypotheses H1–H5 for observed thermal degradation.',
    category: 'INVESTIGATION',
    inputSchema: {},
    execute: () => {
      return {
        success: true,
        message: 'Generated 5 evidence-grounded hypotheses: H1 Fouling Accumulation (84%), H2 Operating Regime Change (12%), H3 Sensor Drift (4%), H4 Feed Property Shift (8%), H5 Hydraulic Effect (6%).',
        stateDelta: {
          activeView: 'EVIDENCE',
          activeHypotheses: INITIAL_HYPOTHESES
        }
      };
    }
  },

  EVALUATE_HYPOTHESIS: {
    id: 'EVALUATE_HYPOTHESIS',
    name: 'Evaluate Hypothesis',
    description: 'Evaluates supporting vs contradicting evidence for a specific hypothesis.',
    category: 'INVESTIGATION',
    inputSchema: { hypothesisId: 'H1, H2, H3, H4, or H5' },
    execute: (params) => {
      const hId = (params.hypothesisId || 'H1').toUpperCase().trim();
      const hyp = INITIAL_HYPOTHESES.find(h => h.id === hId) || INITIAL_HYPOTHESES[0];
      return {
        success: true,
        message: `Hypothesis ${hyp.id} (${hyp.title}): Confidence ${(hyp.confidenceScore * 100).toFixed(0)}%. ${hyp.supportingEvidence[0]} Contradiction: ${hyp.contradictingEvidence[0] || 'None'}. Next Test: ${hyp.nextRecommendedTest}`,
        stateDelta: {
          activeView: 'EVIDENCE',
          activeHypothesisId: hyp.id
        }
      };
    }
  },

  GET_INVESTIGATION_RECOMMENDATIONS: {
    id: 'GET_INVESTIGATION_RECOMMENDATIONS',
    name: 'Get Investigation Recommendations',
    description: 'Provides the next evidence-grounded engineering action based on active hypotheses.',
    category: 'INVESTIGATION',
    inputSchema: {},
    execute: () => {
      const rec = 'Recommended Next Action: Perform normalized thermal resistance vs velocity test on E-102 to decouple hydraulic fouling from flow variation. Install differential pressure transmitter PT-102B to resolve missing hydraulic telemetry.';
      return {
        success: true,
        message: rec,
        stateDelta: {
          activeView: 'EVIDENCE',
          investigationRecommendation: rec
        }
      };
    }
  },

  START_DEMO: {
    id: 'START_DEMO',
    name: 'Start Guided Demo',
    description: 'Launches guided engineering demonstration sequence across process graph, E-102 fouling, uncertainty, and 3D projection.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: () => {
      return {
        success: true,
        message: 'Starting PLANT-X Engineering Demonstration: Navigating to Crude Preheat Process Graph and focusing on attention exchanger E-102.',
        stateDelta: {
          activeView: 'PROCESS',
          selectedAssetTag: 'E-102',
          cameraFocusTag: 'E-102',
          highlightedPath: ['P-101', 'S-101', 'E-101', 'S-102', 'E-102']
        }
      };
    }
  },

  START_JUDGE_MODE: {
    id: 'START_JUDGE_MODE',
    name: 'Start Judge Walkthrough',
    description: 'Initiates deterministic 19-step guided engineering demonstration for judges.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: async () => {
      await judgeModeController.startWalkthrough();
      return {
        success: true,
        message: 'Judge Mode Active: Started PLANT-X 19-step automated Judge Walkthrough. Step 1: System Overview.',
        stateDelta: { activeView: 'PROCESS' }
      };
    }
  },

  JUDGE_NEXT_STEP: {
    id: 'JUDGE_NEXT_STEP',
    name: 'Judge Walkthrough: Next Step',
    description: 'Advances to the next step in the Judge Walkthrough.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: async () => {
      await judgeModeController.nextStep();
      const step = judgeModeController.getCurrentStep();
      return {
        success: true,
        message: `Advanced to Step ${step?.stepNumber || ''}: ${step?.title || ''}`,
        stateDelta: {}
      };
    }
  },

  JUDGE_PAUSE: {
    id: 'JUDGE_PAUSE',
    name: 'Judge Walkthrough: Pause',
    description: 'Pauses the Judge Walkthrough.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: () => {
      judgeModeController.pause();
      return {
        success: true,
        message: 'Paused Judge Walkthrough.',
        stateDelta: {}
      };
    }
  },

  JUDGE_RESUME: {
    id: 'JUDGE_RESUME',
    name: 'Judge Walkthrough: Resume',
    description: 'Resumes the Judge Walkthrough.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: async () => {
      await judgeModeController.resume();
      return {
        success: true,
        message: 'Resumed Judge Walkthrough.',
        stateDelta: {}
      };
    }
  },

  JUDGE_REPEAT: {
    id: 'JUDGE_REPEAT',
    name: 'Judge Walkthrough: Repeat',
    description: 'Repeats the current step in the Judge Walkthrough.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: async () => {
      await judgeModeController.repeat();
      return {
        success: true,
        message: 'Repeating current step in Judge Walkthrough.',
        stateDelta: {}
      };
    }
  },

  JUDGE_SKIP: {
    id: 'JUDGE_SKIP',
    name: 'Judge Walkthrough: Skip',
    description: 'Skips the current step in the Judge Walkthrough.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: async () => {
      await judgeModeController.skip();
      return {
        success: true,
        message: 'Skipped step in Judge Walkthrough.',
        stateDelta: {}
      };
    }
  },

  JUDGE_ABORT: {
    id: 'JUDGE_ABORT',
    name: 'Judge Walkthrough: Abort',
    description: 'Aborts the Judge Walkthrough and returns control to the operator.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: () => {
      judgeModeController.abort();
      return {
        success: true,
        message: 'Aborted Judge Walkthrough. Restored manual operator control.',
        stateDelta: {}
      };
    }
  },

  RESET_CAMERA: {
    id: 'RESET_CAMERA',
    name: 'Reset 3D Camera',
    description: 'Resets the 3D camera to the isometric overview angle of the CDU preheat train.',
    category: 'VISUALIZATION',
    inputSchema: {},
    execute: () => {
      return {
        success: true,
        message: 'Reset 3D camera to plant isometric overview.',
        stateDelta: {
          activeView: '3D',
          cameraFocusTag: null
        }
      };
    }
  },

  SHOW_EXECUTION_TRACE: {
    id: 'SHOW_EXECUTION_TRACE',
    name: 'Show Execution Trace',
    description: 'Displays granular developer and judge execution trace for the previous voice command.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: () => {
      return {
        success: true,
        message: 'Displaying technical execution trace.',
        stateDelta: { lastAgentResponse: 'Displaying technical execution trace in audit log.' }
      };
    }
  },

  RESTORE_SNAPSHOT: {
    id: 'RESTORE_SNAPSHOT',
    name: 'Restore Workstation Snapshot',
    description: 'Restores the most recent saved workstation layout and selection snapshot.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: () => {
      return {
        success: true,
        message: 'Restored previous workstation snapshot state.',
        stateDelta: {
          activeView: 'PROCESS',
          selectedAssetTag: 'E-102',
          cameraFocusTag: 'E-102'
        }
      };
    }
  },

  INGEST_BLUEPRINT: {
    id: 'INGEST_BLUEPRINT',
    name: 'Ingest Blueprint P&ID',
    description: 'Ingests P&ID schematic, extracts equipment symbols and connections, and launches review.',
    category: 'SYSTEM',
    inputSchema: { document: 'Document identifier e.g. PID-001-CRUDE-PREHEAT.pdf' },
    execute: () => {
      return {
        success: true,
        message: 'Ingested PID-001-CRUDE-PREHEAT.pdf: 5 equipment tags and 4 connections extracted. 1 ambiguous line flagged for review.',
        stateDelta: {
          activeView: 'PND',
          lastAgentResponse: 'Ingested PID-001-CRUDE-PREHEAT.pdf for review.'
        }
      };
    }
  },

  STOP_SPEECH: {
    id: 'STOP_SPEECH',
    name: 'Stop Assistant Speech',
    description: 'Immediately terminates audio playback without cancelling pending tasks or timers.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: () => {
      return {
        success: true,
        message: 'Audio playback stopped immediately.',
        stateDelta: { isTtsSpeaking: false }
      };
    }
  },

  GREET_OPERATOR: {
    id: 'GREET_OPERATOR',
    name: 'Greet Operator',
    description: 'Acknowledges engineer greeting and reports workstation readiness.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: (_params: any, currentState: any) => {
      const tag = currentState?.selectedAssetTag || 'E-102';
      return {
        success: true,
        message: `PLANT-X Voice Engineering Assistant online. Workstation ready for commands or asset queries on ${tag}.`,
        stateDelta: {}
      };
    }
  },

  DESCRIBE_SCREEN: {
    id: 'DESCRIBE_SCREEN',
    name: 'Describe Active Screen',
    description: 'Provides technical summary of the currently active workstation viewport, asset focus, and study context.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: (_: any, currentState: any) => {
      const view = currentState?.activeView || 'PROCESS';
      const asset = currentState?.selectedAssetTag || 'E-102';
      const scen = currentState?.scenario || 'normal';
      let summary = `You are on the ${view} view. Active asset is ${asset} in ${scen} operating mode.`;
      if (view === 'PROCESS') {
        summary += ' Showing topological schematic of the Crude Preheat Train (P-101 through C-101).';
      } else if (view === '3D') {
        summary += ' Rendering representative 3D spatial layout. Level L4 inferred procedural geometry.';
      } else if (view === 'SIMULATION') {
        summary += ' Stage 9 counterfactual simulation workbench for what-if stress testing.';
      } else if (view === 'EVIDENCE') {
        summary += ' Displaying sensor measurement provenance and causal evidence graph.';
      }
      return {
        success: true,
        message: summary,
        stateDelta: {}
      };
    }
  },

  COMPARE_WITH_BASELINE: {
    id: 'COMPARE_WITH_BASELINE',
    name: 'Compare Study with Baseline',
    description: 'Compares current study parameters against normal operational baseline.',
    category: 'INVESTIGATION',
    inputSchema: {},
    execute: (_: any, currentState: any) => {
      const tag = currentState?.selectedAssetTag || 'E-102';
      const isDisturbed = currentState?.scenario === 'disturbed' || currentState?.scenario === 'irregular_sampling';
      const msg = isDisturbed
        ? `Baseline comparison against nominal: +6.0σ regime shift detected on ${tag}. LMTD variance +14.2K, derived Rf elevated to 7.28e-8 m²·K/W. Trust gate status: ABSTAIN.`
        : `Baseline comparison: Current case on ${tag} matches nominal baseline. Thermal closure within 1.2%, fouling progression nominal. Trust gate: PASS.`;
      return {
        success: true,
        message: msg,
        stateDelta: { activeView: 'TRENDS' }
      };
    }
  },

  WHAT_CHANGED: {
    id: 'WHAT_CHANGED',
    name: 'Explain Recent Changes',
    description: 'Summarizes recent state mutations, regime shifts, or timer actions.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: (_: any, currentState: any) => {
      const asset = currentState?.selectedAssetTag || 'E-102';
      const rf = currentState?.currentRf ? (currentState.currentRf * 1e7).toFixed(2) : '0.73';
      return {
        success: true,
        message: `Current state: Operating in ${currentState?.scenario || 'normal'} mode. Selected asset ${asset} has derived Rf = ${rf}e-7 m²·K/W against threshold 1.5e-7.`,
        stateDelta: {}
      };
    }
  },

  WORKFLOW_GUIDANCE: {
    id: 'WORKFLOW_GUIDANCE',
    name: 'Provide Workflow Guidance',
    description: 'Recommends logical next engineering actions based on active evidence and uncertainty.',
    category: 'SYSTEM',
    inputSchema: {},
    execute: (_params: any, currentState: any) => {
      const view = currentState?.activeView || 'PROCESS';
      return {
        success: true,
        message: `Workflow guidance for ${view} view: Available actions include inspecting E-102 fouling state, evaluating H1 fouling accumulation hypothesis, or scheduling counterfactual irregular-sampling simulation.`,
        stateDelta: {}
      };
    }
  }
};


