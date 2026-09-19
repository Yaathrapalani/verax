/**
 * PLANT-X Application Timer & Delayed Execution Engine
 * Provides validated scheduling, countdown ticking, state revalidation, and immediate cancellation.
 */

import type { PlantWorkstationState, ToolResult } from './types';
import { TOOL_REGISTRY } from './tools';

export type TimerTickCallback = (remainingSeconds: number) => void;
export type TimerCompleteCallback = (result: ToolResult, explanation: string) => void;
export type TimerCancelCallback = (reason: string) => void;

export class TimerService {
  private intervalId: any = null;
  private remainingSeconds: number = 0;
  private totalSeconds: number = 0;
  private targetAction: string = '';
  private targetParams: Record<string, any> = {};
  private validationContext: {
    expectedAssetTag: string;
    expectedScenario: string;
  } = { expectedAssetTag: '', expectedScenario: '' };

  private onTickCallbacks: TimerTickCallback[] = [];
  private onCompleteCallbacks: TimerCompleteCallback[] = [];
  private onCancelCallbacks: TimerCancelCallback[] = [];

  public isRunning(): boolean {
    return this.intervalId !== null;
  }

  public getRemainingSeconds(): number {
    return this.remainingSeconds;
  }

  public getTotalSeconds(): number {
    return this.totalSeconds;
  }

  public onTick(cb: TimerTickCallback): () => void {
    this.onTickCallbacks.push(cb);
    return () => {
      this.onTickCallbacks = this.onTickCallbacks.filter(c => c !== cb);
    };
  }

  public onComplete(cb: TimerCompleteCallback): () => void {
    this.onCompleteCallbacks.push(cb);
    return () => {
      this.onCompleteCallbacks = this.onCompleteCallbacks.filter(c => c !== cb);
    };
  }

  public onCancel(cb: TimerCancelCallback): () => void {
    this.onCancelCallbacks.push(cb);
    return () => {
      this.onCancelCallbacks = this.onCancelCallbacks.filter(c => c !== cb);
    };
  }

  /**
   * Schedule delayed action with pre-validation and state snapshot
   */
  public schedule(
    delaySeconds: number,
    targetAction: string,
    targetParams: Record<string, any>,
    currentState: PlantWorkstationState,
    getStateFn?: () => PlantWorkstationState
  ): boolean {
    this.cancel('Replaced by new timer schedule');

    if (delaySeconds <= 0) {
      return false;
    }

    this.totalSeconds = delaySeconds;
    this.remainingSeconds = delaySeconds;
    this.targetAction = targetAction;
    this.targetParams = targetParams;
    this.validationContext = {
      expectedAssetTag: currentState.selectedAssetTag,
      expectedScenario: currentState.scenario
    };

    const stepMs = 50;
    this.intervalId = setInterval(async () => {
      this.remainingSeconds = Math.max(0, this.remainingSeconds - stepMs / 1000);
      this.onTickCallbacks.forEach(cb => cb(this.remainingSeconds));

      if (this.remainingSeconds <= 0) {
        clearInterval(this.intervalId);
        this.intervalId = null;
        const latestState = getStateFn ? getStateFn() : currentState;
        await this.handleExecution(latestState);
      }
    }, stepMs);

    return true;
  }

  /**
   * Immediate cancellation
   */
  public cancel(reason: string = 'User cancelled'): boolean {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.remainingSeconds = 0;
      this.onCancelCallbacks.forEach(cb => cb(reason));
      return true;
    }
    return false;
  }

  /**
   * Pre-execution validation & tool dispatch
   */
  private async handleExecution(latestState: PlantWorkstationState) {
    // 1. Revalidate Project State Integrity
    if (
      this.validationContext.expectedScenario &&
      latestState.scenario !== this.validationContext.expectedScenario
    ) {
      const abortMsg = `Scheduled execution aborted: Project scenario changed from '${this.validationContext.expectedScenario}' to '${latestState.scenario}' during countdown.`;
      this.onCompleteCallbacks.forEach(cb => cb({ success: false, message: abortMsg }, abortMsg));
      return;
    }

    // 2. Dispatch Target Tool
    const tool = TOOL_REGISTRY[this.targetAction];
    if (!tool) {
      const err = `Execution error: Tool '${this.targetAction}' not found in registry.`;
      this.onCompleteCallbacks.forEach(cb => cb({ success: false, message: err }, err));
      return;
    }

    const result = await tool.execute(this.targetParams, latestState);
    const expl = `Scheduled action '${tool.name}' completed: ${result.message}`;
    this.onCompleteCallbacks.forEach(cb => cb(result, expl));
  }
}

export const timerService = new TimerService();
