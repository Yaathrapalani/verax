/**
 * PLANT-X SESSION RESUME CONTROLLER
 * 
 * Ensures voice connection drops never destroy:
 * - selected equipment / stream / graph node
 * - active study / scenario / hypothesis
 * - task state / timer state
 * - evidence context / conversation history
 * - authoritative stateVersion
 * 
 * Re-validates pending operations on reconnect and rejects stale results.
 */

import type { PlantWorkstationState } from '../types';

export interface PreservedSessionSnapshot {
  sessionId: string;
  reconnectedAt: number;
  preservedStateVersion: number;
  selectedAssetTag: string;
  selectedStreamId: string;
  cameraFocusTag: string | null;
  scenario: 'normal' | 'disturbed';
  activeHypothesisId: string | null;
  timerActive: boolean;
  timerRemainingSeconds: number;
  pendingCommand: string | null;
  conversationSummary: string;
  unresolvedReferences: string[];
}

export class SessionResumeController {
  private currentSessionId = 'SESS-' + Date.now().toString(36).toUpperCase();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private isReconnecting = false;

  public captureSnapshot(
    state: PlantWorkstationState,
    conversationSummary: string = '',
    unresolvedReferences: string[] = []
  ): PreservedSessionSnapshot {
    return {
      sessionId: this.currentSessionId,
      reconnectedAt: Date.now(),
      preservedStateVersion: (state as any).stateVersion ?? 1,
      selectedAssetTag: state.selectedAssetTag,
      selectedStreamId: state.selectedStreamId,
      cameraFocusTag: state.cameraFocusTag,
      scenario: state.scenario,
      activeHypothesisId: state.activeHypothesisId,
      timerActive: state.timer.isActive,
      timerRemainingSeconds: state.timer.remainingSeconds,
      pendingCommand: state.agentStatus === 'EXECUTING' ? state.lastTranscript : null,
      conversationSummary,
      unresolvedReferences,
    };
  }

  public beginReconnect(): boolean {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.isReconnecting = false;
      return false; // Exhausted reconnects -> fallback to degraded
    }
    this.isReconnecting = true;
    this.reconnectAttempts++;
    return true;
  }

  public completeReconnect(
    currentState: PlantWorkstationState,
    snapshot: PreservedSessionSnapshot
  ): { restoredState: PlantWorkstationState; rejectedStaleOperations: string[] } {
    this.isReconnecting = false;
    this.reconnectAttempts = 0;

    const rejected: string[] = [];

    // Check if state changed while disconnected
    const currentVersion = (currentState as any).stateVersion ?? 1;
    if (snapshot.pendingCommand && currentVersion !== snapshot.preservedStateVersion) {
      rejected.push(
        `Stale operation '${snapshot.pendingCommand}' rejected: stateVersion changed (${snapshot.preservedStateVersion} -> ${currentVersion})`
      );
    }

    // Preserve all authoritative properties
    const restored: PlantWorkstationState = {
      ...currentState,
      selectedAssetTag: snapshot.selectedAssetTag,
      selectedStreamId: snapshot.selectedStreamId,
      cameraFocusTag: snapshot.cameraFocusTag,
      scenario: snapshot.scenario,
      activeHypothesisId: snapshot.activeHypothesisId,
      agentStatus: 'READY',
      lastAgentResponse: `Session restored. Connected to workstation (v${currentVersion}).`,
    };

    return {
      restoredState: restored,
      rejectedStaleOperations: rejected,
    };
  }

  public getReconnectState(): { isReconnecting: boolean; attempts: number; maxAttempts: number } {
    return {
      isReconnecting: this.isReconnecting,
      attempts: this.reconnectAttempts,
      maxAttempts: this.maxReconnectAttempts,
    };
  }

  public reset(): void {
    this.currentSessionId = 'SESS-' + Date.now().toString(36).toUpperCase();
    this.reconnectAttempts = 0;
    this.isReconnecting = false;
  }
}

export const sessionResumeController = new SessionResumeController();
