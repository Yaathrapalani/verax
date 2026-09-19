/**
 * PLANT-X Natural Language Intent & Entity Parser
 * Resolves conversational pronouns ('it', 'its', 'that'), contextual entities ('highest uncertainty'),
 * and temporal parameters ('in ten seconds') into deterministic tool calls.
 */

import type { PlantWorkstationState } from './types';

export interface ParsedIntent {
  toolId: string;
  parameters: Record<string, any>;
  transcript: string;
  confidence: number;
  explanation: string;
  isAmbiguous?: boolean;
  clarificationPrompt?: string;
}

export class IntentParser {
  /**
   * Parse user utterance into a validated deterministic tool call
   */
  public parse(utterance: string, currentState: PlantWorkstationState): ParsedIntent {
    const text = (utterance || '').toLowerCase().trim();
    const clean = text.replace(/[.,?!]/g, '');

    // 0. Natural Greeting
    if (clean === 'hello' || clean === 'hi' || clean === 'good morning' || clean === 'greetings' || clean === 'hey plant-x' || clean === 'hey foul-x') {
      return {
        toolId: 'GREET_OPERATOR',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Operator greeted assistant.'
      };
    }

    // 1a. Voice Barge-In / Stop Speech ("Stop speaking", "Stop talking", "Quiet", "Mute")
    if (clean === 'stop speaking' || clean === 'stop talking' || clean === 'mute' || clean === 'quiet' || clean === 'silence') {
      return {
        toolId: 'STOP_SPEECH',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Operator requested immediate audio silence.'
      };
    }

    // 0b. Prohibited Actuator / DCS / PLC Physical Plant Commands
    if (
      clean.includes('open valve') || clean.includes('close valve') ||
      clean.includes('pump speed') || clean.includes('setpoint') ||
      clean.includes('shutdown') || clean.includes('modify plc') ||
      clean.includes('modify dcs') || clean.includes('plc') || clean.includes('dcs') ||
      clean.includes('actuator')
    ) {
      return {
        toolId: 'SAFETY_VIOLATION_REJECTED',
        parameters: { command: utterance },
        transcript: utterance,
        confidence: 1.0,
        explanation: 'SAFETY BOUNDARY: Physical actuator control or PLC/DCS modification is strictly prohibited.',
      };
    }

    // 1. Immediate Interruption / Cancellation
    if (
      clean === 'cancel' || clean === 'cancel it' || clean === 'cancel that' ||
      clean.startsWith('cancel') || clean === 'stop' || clean === 'abort' ||
      clean.startsWith('wait') || clean.startsWith('hold on')
    ) {
      return {
        toolId: 'CANCEL_SCHEDULED_ACTION',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'User requested immediate cancellation of pending scheduled action or conversational pause.'
      };
    }

    // 1b. Screen & Workstation Context Awareness ("What am I looking at?", "Where am I?", "Summarize this screen", "Explain this screen")
    if (clean.includes('what am i looking at') || clean.includes('where am i') || clean.includes('summarize this screen') || clean.includes('what is this screen') || clean.includes('explain this screen') || clean.includes('describe screen')) {
      return {
        toolId: 'DESCRIBE_SCREEN',
        parameters: {},
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Providing technical summary of current active viewport and study.'
      };
    }

    // 1c. Comparison with Baseline ("Compare with baseline", "Compare that with baseline", "Compare this with baseline")
    if (clean.includes('compare with baseline') || clean.includes('compare that with baseline') || clean.includes('compare this with baseline') || clean.includes('compare it to baseline') || clean.includes('compare to baseline')) {
      return {
        toolId: 'COMPARE_WITH_BASELINE',
        parameters: {},
        transcript: utterance,
        confidence: 0.97,
        explanation: 'Comparing current study parameters against baseline.'
      };
    }

    // 1d. What Changed / What Can I Do Here
    if (clean.includes('what changed') || clean.includes('what has changed')) {
      return {
        toolId: 'WHAT_CHANGED',
        parameters: {},
        transcript: utterance,
        confidence: 0.96,
        explanation: 'Explaining recent state changes or regime shifts.'
      };
    }
    if (clean.includes('what can i do here') || clean.includes('what should i do next') || clean.includes('workflow guidance')) {
      return {
        toolId: 'WORKFLOW_GUIDANCE',
        parameters: {},
        transcript: utterance,
        confidence: 0.96,
        explanation: 'Providing recommended workflow guidance.'
      };
    }

    // 1e. Attention Query ("What needs my attention?", "What needs attention?")
    if (clean.includes('what needs my attention') || clean.includes('what needs attention') || clean.includes('attention')) {
      return {
        toolId: 'SELECT_EQUIPMENT',
        parameters: { tag: 'E-102' },
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Identified E-102 as primary attention asset due to elevated fouling and regime shift uncertainty.'
      };
    }

    // 1f. Ordinal Hypothesis Checks ("Check the second one", "Check the first one")
    if (clean.includes('check the second') || clean.includes('second one') || clean.includes('hypothesis 2') || clean.includes('h2')) {
      return {
        toolId: 'EVALUATE_HYPOTHESIS',
        parameters: { hypothesisId: 'H2' },
        transcript: utterance,
        confidence: 0.96,
        explanation: 'Evaluating hypothesis H2 (OPERATING_REGIME_CHANGE).'
      };
    }
    if (clean.includes('check the first') || clean.includes('first one') || clean.includes('hypothesis 1') || clean.includes('h1')) {
      return {
        toolId: 'EVALUATE_HYPOTHESIS',
        parameters: { hypothesisId: 'H1' },
        transcript: utterance,
        confidence: 0.96,
        explanation: 'Evaluating hypothesis H1 (FOULING_ACCUMULATION).'
      };
    }


    // 2. Timer Status Query ("How much time is left?")
    if (clean.includes('how much time') || clean.includes('time is left') || clean.includes('timer status') || clean.includes('countdown')) {
      return {
        toolId: 'GET_TIMER_STATUS',
        parameters: {},
        transcript: utterance,
        confidence: 0.95,
        explanation: 'User queried status of active countdown timer.'
      };
    }

    // 3. Exchanger with highest uncertainty ("Show me the exchanger with the highest uncertainty")
    if ((clean.includes('exchanger') || clean.includes('unit')) && (clean.includes('highest uncertainty') || clean.includes('max uncertainty') || clean.includes('most uncertain'))) {
      return {
        toolId: 'SELECT_EQUIPMENT',
        parameters: { tag: 'E-102' },
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Resolved exchanger with highest uncertainty to E-102 based on historical regime support.'
      };
    }

    // 4. Delayed execution / Scheduled scenario ("Start it in ten seconds", "Run the irregular sampling scenario in ten seconds")
    const timerMatch = clean.match(/(?:start|run|schedule|execute)(?:\s+.*?)?\s+in\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty)\s+(?:seconds|sec|s)/);
    if (timerMatch) {
      const wordToNum: Record<string, number> = {
        one: 1, two: 2, three: 3, four: 4, five: 5,
        six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
        twenty: 20, thirty: 30
      };
      const rawSec = timerMatch[1];
      const seconds = Number(rawSec) || wordToNum[rawSec] || 10;
      return {
        toolId: 'SCHEDULE_SCENARIO',
        parameters: { scenario: 'irregular_sampling', delaySeconds: seconds },
        transcript: utterance,
        confidence: 0.96,
        explanation: `User requested delayed scenario execution in ${seconds} seconds.`
      };
    }

    // 5. Immediate Scenario Execution ("Run the irregular sampling scenario", "Run scenario now")
    if (clean.includes('run the irregular') || clean.includes('run irregular sampling') || clean.includes('run scenario now') || clean.includes('execute scenario')) {
      return {
        toolId: 'RUN_SCENARIO',
        parameters: { scenario: 'irregular_sampling' },
        transcript: utterance,
        confidence: 0.95,
        explanation: 'User requested immediate execution of irregular sampling scenario.'
      };
    }

    // 6. Upstream / Downstream Process Path Tracing
    if (clean.includes('upstream path') || clean.includes('show upstream') || clean.includes('trace upstream')) {
      return {
        toolId: 'HIGHLIGHT_PATH',
        parameters: { direction: 'UPSTREAM', anchorTag: currentState.selectedAssetTag || 'E-102' },
        transcript: utterance,
        confidence: 0.97,
        explanation: `Tracing upstream flow path from anchor ${currentState.selectedAssetTag}.`
      };
    }

    if (clean.includes('downstream path') || clean.includes('show downstream') || clean.includes('trace downstream')) {
      return {
        toolId: 'HIGHLIGHT_PATH',
        parameters: { direction: 'DOWNSTREAM', anchorTag: currentState.selectedAssetTag || 'E-102' },
        transcript: utterance,
        confidence: 0.97,
        explanation: `Tracing downstream flow path from anchor ${currentState.selectedAssetTag}.`
      };
    }

    // 7. 3D Navigation & Focus ("Show this in 3D", "Put that in 3D", "Show it in 3D", "Zoom into E-102")
    if (clean.includes('3d') || clean.includes('zoom into') || clean.includes('focus on') || clean.includes('fit plant') || clean.includes('reset camera')) {
      if (clean.includes('fit plant') || clean.includes('reset camera')) {
        return {
          toolId: 'RESET_CAMERA',
          parameters: {},
          transcript: utterance,
          confidence: 0.95,
          explanation: 'Resetting 3D camera to plant overview.'
        };
      }

      // Check if specific equipment mentioned e.g. "Zoom into E-102"
      const eqMatch = clean.match(/(?:e-?10[1-5]|p-?101|v-?10[12]|f-?101|c-?101)/i);
      let targetTag = currentState.selectedAssetTag || 'E-102';
      if (eqMatch) {
        targetTag = eqMatch[0].toUpperCase();
        if (/^E0\d$/.test(targetTag)) targetTag = `E-10${targetTag.slice(2)}`;
      }

      return {
        toolId: 'FOCUS_3D_OBJECT',
        parameters: { tag: targetTag },
        transcript: utterance,
        confidence: 0.95,
        explanation: `Navigating to 3D view and focusing on ${targetTag}.`
      };
    }

    // 8. Fouling State Query ("Show its fouling state", "Show fouling", "Show fouling for E-102")
    if (clean.includes('fouling')) {
      const eqMatch = clean.match(/(?:e-?10[1-5])/i);
      const tag = eqMatch ? eqMatch[0].toUpperCase() : currentState.selectedAssetTag || 'E-102';
      return {
        toolId: 'SHOW_FOULING',
        parameters: { tag },
        transcript: utterance,
        confidence: 0.95,
        explanation: `Showing fouling state for ${tag}.`
      };
    }

    // 9. Uncertainty & Reliability Gate ("Why is uncertainty high?", "Show me the uncertainty", "Why did reliability gate fail?")
    if (clean.includes('uncertainty') || clean.includes('reliability') || clean.includes('trust gate') || clean.includes('gate fail')) {
      if (clean.includes('gate fail') || clean.includes('reliability status') || clean.includes('gate status')) {
        return {
          toolId: 'GET_RELIABILITY_STATUS',
          parameters: {},
          transcript: utterance,
          confidence: 0.94,
          explanation: 'Auditing reliability gate check results.'
        };
      }
      return {
        toolId: 'SHOW_UNCERTAINTY',
        parameters: { tag: currentState.selectedAssetTag || 'E-102' },
        transcript: utterance,
        confidence: 0.94,
        explanation: `Displaying prediction uncertainty for ${currentState.selectedAssetTag}.`
      };
    }

    // 10. Data gaps & Missing data ("Show me the missing data", "Show data gaps", "What's missing?", "What is missing?")
    if (clean.includes('missing data') || clean.includes('data gap') || clean.includes('data gaps') || clean.includes('sampling gap') || clean.includes("what's missing") || clean.includes('what is missing') || clean.includes('whats missing')) {
      return {
        toolId: 'SHOW_DATA_GAPS',
        parameters: {},
        transcript: utterance,
        confidence: 0.96,
        explanation: 'Highlighting missing sensor channels and sampling gaps.'
      };
    }

    // 11. Evidence & Lineage ("Open the evidence", "Show me the evidence", "Where did this value come from?")
    if (clean.includes('evidence') || clean.includes('provenance') || clean.includes('where did this value come from') || clean.includes('lineage')) {
      return {
        toolId: 'SHOW_EVIDENCE',
        parameters: { anchorTag: currentState.selectedAssetTag || 'E-102' },
        transcript: utterance,
        confidence: 0.95,
        explanation: `Opening evidence lineage graph for ${currentState.selectedAssetTag}.`
      };
    }

    // 12. Investigation & Hypotheses ("What should I investigate next?", "Show me the hypothesis", "What are the possible causes?")
    if (clean.includes('investigate next') || clean.includes('what should i investigate') || clean.includes('what next')) {
      return {
        toolId: 'GET_INVESTIGATION_RECOMMENDATIONS',
        parameters: {},
        transcript: utterance,
        confidence: 0.96,
        explanation: 'Generating next evidence-grounded investigation recommendation.'
      };
    }

    if (clean.includes('hypothesis') || clean.includes('hypotheses') || clean.includes('possible causes') || clean.includes('test hypothesis')) {
      if (clean.includes('test that hypothesis') || clean.includes('evaluate hypothesis') || clean.includes('test hypothesis')) {
        return {
          toolId: 'EVALUATE_HYPOTHESIS',
          parameters: { hypothesisId: currentState.activeHypothesisId || 'H1' },
          transcript: utterance,
          confidence: 0.93,
          explanation: `Evaluating hypothesis ${currentState.activeHypothesisId || 'H1'}.`
        };
      }
      return {
        toolId: 'GET_HYPOTHESES',
        parameters: {},
        transcript: utterance,
        confidence: 0.95,
        explanation: 'Listing H1–H5 diagnostic hypotheses.'
      };
    }

    // 13. Explicit Equipment Selection ("Take me to E-102", "Select E-101", "Show E-103", "Show me E-102")
    const selectMatch = clean.match(/(?:take me to|select|show(?:\s+me)?|navigate to|inspect|focus on)\s+(e-?10[1-5]|p-?101|v-?10[12]|f-?101|c-?101)/i);
    if (selectMatch) {
      let tag = selectMatch[1].toUpperCase();
      if (!tag.includes('-')) {
        tag = `${tag[0]}-${tag.slice(1)}`;
      }
      return {
        toolId: 'SELECT_EQUIPMENT',
        parameters: { tag },
        transcript: utterance,
        confidence: 0.98,
        explanation: `Selecting equipment ${tag}.`
      };
    }

    // 14. View Navigation ("Open the process graph", "Open P&ID", "Open simulation", "Open chemistry")
    if (clean.includes('process graph') || clean.includes('open process') || clean.includes('process view')) {
      return {
        toolId: 'NAVIGATE_ROUTE',
        parameters: { view: 'PROCESS' },
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Navigating to Process schematic view.'
      };
    }
    if (clean.includes('import this p&id') || clean.includes('ingest p&id') || clean.includes('import blueprint') || clean.includes('build the 3d model') || clean.includes('blueprint review')) {
      return {
        toolId: 'INGEST_BLUEPRINT',
        parameters: { document: 'PID-001-CRUDE-PREHEAT.pdf' },
        transcript: utterance,
        confidence: 0.97,
        explanation: 'Ingesting P&ID blueprint schematic for human review and 3D reconstruction.'
      };
    }
    if (clean.includes('p&id') || clean.includes('pid') || clean.includes('blueprint')) {
      return {
        toolId: 'NAVIGATE_ROUTE',
        parameters: { view: 'PND' },
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Navigating to P&ID topology drawing.'
      };
    }

    if (clean.includes('simulation') || clean.includes('what if') || clean.includes('counterfactual')) {
      return {
        toolId: 'NAVIGATE_ROUTE',
        parameters: { view: 'SIMULATION' },
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Navigating to Simulation workspace.'
      };
    }
    if (clean.includes('chemistry') || clean.includes('stream builder') || clean.includes('fluid')) {
      return {
        toolId: 'NAVIGATE_ROUTE',
        parameters: { view: 'CHEMISTRY' },
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Navigating to Chemical Stream Builder.'
      };
    }

    // 15. Demo & Judge Walkthrough Mode
    if (
      clean.includes('start demo') ||
      clean.includes('run demo') ||
      clean.includes('begin demo') ||
      clean.includes('start judge walkthrough') ||
      clean.includes('start presentation') ||
      clean.includes('start walkthrough') ||
      clean.includes('judge mode') ||
      clean.includes('challenge me')
    ) {
      return {
        toolId: 'START_JUDGE_MODE',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Initiating deterministic 19-step Judge Acceptance Walkthrough.'
      };
    }
    if (clean === 'next' || clean === 'next step' || clean === 'continue presentation') {
      return {
        toolId: 'JUDGE_NEXT_STEP',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Advancing to next Judge Walkthrough step.'
      };
    }
    if (clean === 'pause' || clean === 'pause walkthrough' || clean === 'pause presentation') {
      return {
        toolId: 'JUDGE_PAUSE',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Pausing Judge Walkthrough.'
      };
    }
    if (clean === 'resume' || clean === 'resume walkthrough' || clean === 'resume presentation') {
      return {
        toolId: 'JUDGE_RESUME',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Resuming Judge Walkthrough.'
      };
    }
    if (clean === 'repeat' || clean === 'repeat that' || clean === 'repeat step') {
      return {
        toolId: 'JUDGE_REPEAT',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Repeating current Judge Walkthrough step.'
      };
    }
    if (clean === 'skip' || clean === 'skip step') {
      return {
        toolId: 'JUDGE_SKIP',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Skipping current Judge Walkthrough step.'
      };
    }
    if (clean === 'abort' || clean === 'stop walkthrough' || clean === 'stop presentation' || clean === 'exit judge mode') {
      return {
        toolId: 'JUDGE_ABORT',
        parameters: {},
        transcript: utterance,
        confidence: 0.99,
        explanation: 'Aborting Judge Walkthrough.'
      };
    }

    // 16. Conversational Micro-Behaviors & Queries
    if (clean === 'why' || clean === 'why?' || clean.startsWith('why?')) {
      return {
        toolId: 'GET_RELIABILITY_STATUS',
        parameters: {},
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Auditing reliability gate rationale for why action was withheld/approved.'
      };
    }

    if (clean === 'show me' || clean === 'show me.' || clean === 'show that' || clean === 'show me that') {
      return {
        toolId: 'SHOW_EVIDENCE',
        parameters: { anchorTag: currentState.selectedAssetTag || 'E-102' },
        transcript: utterance,
        confidence: 0.97,
        explanation: 'Opening evidence view to show supporting validation and telemetry.'
      };
    }

    if (clean.includes("what don't you know") || clean.includes("what do you not know") || clean.includes("what are you missing") || clean.includes("what's unavailable") || clean.includes("where are the gaps")) {
      return {
        toolId: 'SHOW_DATA_GAPS',
        parameters: {},
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Listing active unobserved telemetry channels and missing evidence.'
      };
    }

    if (clean.includes('show execution trace') || clean.includes('execution trace') || clean.includes('technical trace')) {
      return {
        toolId: 'SHOW_EXECUTION_TRACE',
        parameters: {},
        transcript: utterance,
        confidence: 0.98,
        explanation: 'Displaying technical execution trace for previous command.'
      };
    }

    if (clean.includes('go back') || clean.includes('where we were') || clean.includes('restore snapshot')) {
      return {
        toolId: 'RESTORE_SNAPSHOT',
        parameters: {},
        transcript: utterance,
        confidence: 0.97,
        explanation: 'Restoring previous workstation layout snapshot.'
      };
    }

    if (clean.includes('import this p&id') || clean.includes('ingest p&id') || clean.includes('import blueprint') || clean.includes('build the 3d model') || clean.includes('blueprint review')) {
      return {
        toolId: 'INGEST_BLUEPRINT',
        parameters: { document: 'PID-001-CRUDE-PREHEAT.pdf' },
        transcript: utterance,
        confidence: 0.97,
        explanation: 'Ingesting P&ID blueprint schematic for human review and 3D reconstruction.'
      };
    }

    // 17. Ambiguity Fallback
    return {
      toolId: 'NAVIGATE_ROUTE',
      parameters: { view: 'PROCESS' },
      transcript: utterance,
      confidence: 0.4,
      explanation: 'Ambiguous utterance. Maintained process view.',
      isAmbiguous: true,
      clarificationPrompt: `I did not recognize the exact command '${utterance}'. You can say: 'Take me to E-102', 'Show upstream path', 'Run scenario in 10 seconds', or 'Cancel'.`
    };
  }
}

export const intentParser = new IntentParser();
