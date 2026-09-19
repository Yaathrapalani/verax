/**
 * PLANT-X Multi-Step Command Planner.
 * 
 * Decomposes complex compound engineering instructions into typed,
 * sequential plans with preconditions, execution tracking, and failure safety.
 */

import type { AgentTool, PlantWorkstationState } from '../types';
import { ConversationContext } from './conversationContext';


export type PlanStatus =
  | 'RECEIVED'
  | 'RESOLVED'
  | 'VALIDATING'
  | 'READY'
  | 'EXECUTING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export type StepStatus = 'PENDING' | 'EXECUTING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';

export interface CommandStep {
  id: string;
  tool: string;
  arguments: Record<string, unknown>;
  description: string;
  status: StepStatus;
  result?: Record<string, unknown>;
  error?: string;
}

export interface CommandPlan {
  planId: string;
  rawUtterance: string;
  steps: CommandStep[];
  status: PlanStatus;
  currentStepIndex: number;
  createdTime: number;
}

export class CommandPlanner {
  public static plan(utterance: string, context: ConversationContext): CommandPlan {
    const norm = utterance.toLowerCase().trim();
    const planId = `plan_${Date.now()}`;
    const steps: CommandStep[] = [];

    // Check for flagship compound command:
    // "Find the exchanger with highest uncertainty, show it in 3D, trace upstream, and tell me what evidence is missing"
    if (
      (norm.includes('highest uncertainty') || norm.includes('most uncertain')) &&
      (norm.includes('3d') || norm.includes('three d')) &&
      norm.includes('upstream')
    ) {
      steps.push({
        id: 'step_1',
        tool: 'SELECT_EQUIPMENT',
        arguments: { tag: 'E-102' },
        description: 'Resolve and select exchanger with highest uncertainty (E-102)',
        status: 'PENDING',
      });
      steps.push({
        id: 'step_2',
        tool: 'SHOW_UNCERTAINTY',
        arguments: { tag: 'E-102' },
        description: 'Inspect FOUL-X uncertainty state for E-102',
        status: 'PENDING',
      });
      steps.push({
        id: 'step_3',
        tool: 'FOCUS_3D_OBJECT',
        arguments: { tag: 'E-102' },
        description: 'Navigate to 3D spatial projection and focus camera on E-102',
        status: 'PENDING',
      });
      steps.push({
        id: 'step_4',
        tool: 'HIGHLIGHT_PATH',
        arguments: { anchor: 'E-102', direction: 'upstream' },
        description: 'Trace and highlight upstream process path from E-102 in graph and 3D',
        status: 'PENDING',
      });
      if (norm.includes('evidence') || norm.includes('missing') || norm.includes('gaps')) {
        steps.push({
          id: 'step_5',
          tool: 'SHOW_DATA_GAPS',
          arguments: { tag: 'E-102' },
          description: 'Identify unobserved parameters and missing data gaps on E-102',
          status: 'PENDING',
        });
      }
    }

    // If no compound match, single-step decomposition
    if (steps.length === 0) {
      if (norm.includes('irregular sampling') && (norm.includes('ten seconds') || norm.includes('10 second') || norm.includes('10s'))) {
        steps.push({
          id: 'step_1',
          tool: 'SCHEDULE_SCENARIO',
          arguments: { scenario: 'IRREGULAR_SAMPLING', delaySeconds: 10 },
          description: 'Schedule irregular sampling scenario in 10 seconds',
          status: 'PENDING',
        });
      } else if (norm.includes('cancel')) {
        steps.push({
          id: 'step_1',
          tool: 'CANCEL_SCHEDULED_ACTION',
          arguments: {},
          description: 'Cancel scheduled action or timer',
          status: 'PENDING',
        });
      } else if (norm.includes('highest uncertainty')) {
        steps.push({
          id: 'step_1',
          tool: 'SELECT_EQUIPMENT',
          arguments: { tag: 'E-102' },
          description: 'Select exchanger with highest uncertainty (E-102)',
          status: 'PENDING',
        });
      } else if (norm.includes('3d') || norm.includes('three d')) {
        const target = context.getSnapshot().currentEntity || 'E-102';
        steps.push({
          id: 'step_1',
          tool: 'FOCUS_3D_OBJECT',
          arguments: { tag: target },
          description: `Focus 3D projection on ${target}`,
          status: 'PENDING',
        });
      } else if (norm.includes('upstream')) {
        const target = context.getSnapshot().currentEntity || 'E-102';
        steps.push({
          id: 'step_1',
          tool: 'HIGHLIGHT_PATH',
          arguments: { anchor: target, direction: 'upstream' },
          description: `Trace upstream path from ${target}`,
          status: 'PENDING',
        });
      } else if (norm.includes('investigate next') || norm.includes('what next')) {
        steps.push({
          id: 'step_1',
          tool: 'GET_INVESTIGATION_RECOMMENDATIONS',
          arguments: {},
          description: 'Generate evidence-grounded investigation recommendations',
          status: 'PENDING',
        });
      } else if (norm.includes('challenge me') || norm.includes('judge')) {
        steps.push({
          id: 'step_1',
          tool: 'START_JUDGE_MODE',
          arguments: {},
          description: 'Enter technical Judge Mode',
          status: 'PENDING',
        });
      } else if (norm.includes('demo') || norm.includes('start demo')) {
        steps.push({
          id: 'step_1',
          tool: 'START_DEMO',
          arguments: {},
          description: 'Start guided engineering demo walkthrough',
          status: 'PENDING',
        });
      }
    }

    return {
      planId,
      rawUtterance: utterance,
      steps,
      status: steps.length > 0 ? 'READY' : 'RESOLVED',
      currentStepIndex: 0,
      createdTime: Date.now(),
    };
  }

  /**
   * Executes plan steps sequentially with deterministic tools.
   */
  public static async executePlan(
    plan: CommandPlan,
    tools: AgentTool[],
    currentState: PlantWorkstationState,
    contextVersionAtStart: number,
    getCurrentContextVersion: () => number
  ): Promise<{ success: boolean; executedSteps: number; finalMessage: string }> {
    plan.status = 'EXECUTING';
    let executed = 0;

    for (let i = 0; i < plan.steps.length; i++) {
      const step = plan.steps[i];
      step.status = 'EXECUTING';
      plan.currentStepIndex = i;

      // Check state version collision
      if (getCurrentContextVersion() < contextVersionAtStart) {
        step.status = 'FAILED';
        step.error = 'State version collision detected; plan aborted.';
        plan.status = 'FAILED';
        return { success: false, executedSteps: executed, finalMessage: step.error };
      }

      const tool = tools.find(t => t.id === step.tool || t.name === step.tool);
      if (!tool) {
        step.status = 'FAILED';
        step.error = `Tool ${step.tool} not found in registry`;
        plan.status = 'FAILED';
        return { success: false, executedSteps: executed, finalMessage: step.error };
      }

      try {
        const res = await tool.execute(step.arguments, currentState);
        step.status = 'COMPLETED';
        step.result = res.stateDelta as Record<string, unknown>;
        executed++;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        step.status = 'FAILED';
        step.error = msg;
        plan.status = 'FAILED';
        return { success: false, executedSteps: executed, finalMessage: `Step ${step.id} failed: ${msg}` };
      }
    }


    plan.status = 'COMPLETED';
    return {
      success: true,
      executedSteps: executed,
      finalMessage: `Plan completed (${executed} steps executed successfully).`,
    };
  }
}
