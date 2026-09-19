/**
 * PLANT-X Tool Safety Policy.
 * 
 * Classifies tool execution safety:
 * - READ_ONLY: Safe query, immediate execution.
 * - ANALYSIS: Deterministic analytical calculation.
 * - SIMULATION: Counterfactual scenario simulation.
 * - SCHEDULED_ANALYSIS: Delayed execution requiring pre-execution revalidation.
 * - REQUIRES_CONFIRMATION: Operator approval required before state mutation.
 * - PROHIBITED: Hard boundary (e.g. physical plant control).
 */

export type ToolSafetyClass =
  | 'READ_ONLY'
  | 'ANALYSIS'
  | 'SIMULATION'
  | 'SCHEDULED_ANALYSIS'
  | 'REQUIRES_CONFIRMATION'
  | 'PROHIBITED';

export class SafetyPolicyRegistry {
  private static readonly POLICY_MAP: Record<string, ToolSafetyClass> = {
    NAVIGATE_ROUTE: 'READ_ONLY',
    SELECT_EQUIPMENT: 'READ_ONLY',
    SELECT_STREAM: 'READ_ONLY',
    FOCUS_3D_OBJECT: 'READ_ONLY',
    HIGHLIGHT_PATH: 'READ_ONLY',
    RESET_CAMERA: 'READ_ONLY',
    SHOW_FOULING: 'READ_ONLY',
    SHOW_UNCERTAINTY: 'READ_ONLY',
    SHOW_DATA_GAPS: 'READ_ONLY',
    SHOW_EVIDENCE: 'READ_ONLY',
    GET_TIMER_STATUS: 'READ_ONLY',
    GET_RELIABILITY_STATUS: 'READ_ONLY',
    GET_HYPOTHESES: 'READ_ONLY',
    EVALUATE_HYPOTHESIS: 'ANALYSIS',
    GET_INVESTIGATION_RECOMMENDATIONS: 'ANALYSIS',
    RUN_SCENARIO: 'SIMULATION',
    SCHEDULE_SCENARIO: 'SCHEDULED_ANALYSIS',
    CANCEL_SCHEDULED_ACTION: 'READ_ONLY',
    START_DEMO: 'READ_ONLY',
    START_JUDGE_MODE: 'READ_ONLY',
    PLC_ACTUATE: 'PROHIBITED',
    DCS_WRITE: 'PROHIBITED',
  };

  public static getSafetyClass(toolName: string): ToolSafetyClass {
    return this.POLICY_MAP[toolName] || 'REQUIRES_CONFIRMATION';
  }

  public static isExecutable(toolName: string): boolean {
    const safety = this.getSafetyClass(toolName);
    return safety !== 'PROHIBITED';
  }
}
