/**
 * PLANT-X Audit Logger
 * Maintains an immutable chronological audit trail of voice commands, tool executions, and state deltas.
 */

import type { AuditLogEntry, PlantWorkstationState } from './types';

export class AuditLogger {
  private entries: AuditLogEntry[] = [];

  public logAction(
    transcript: string | undefined,
    intent: string,
    entities: Record<string, any>,
    contextState: PlantWorkstationState,
    toolName: string,
    parameters: Record<string, any>,
    executionStatus: 'SUCCESS' | 'FAILURE' | 'CANCELLED' | 'ABSTAINED',
    resultSummary: string,
    stateDelta?: Record<string, any>
  ): AuditLogEntry {
    const entry: AuditLogEntry = {
      id: `audit-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      timestamp: new Date().toISOString(),
      transcript,
      intent,
      entities,
      context: {
        selectedAssetTag: contextState.selectedAssetTag,
        activeView: contextState.activeView,
        scenario: contextState.scenario
      },
      toolName,
      parameters,
      executionStatus,
      resultSummary,
      stateDelta
    };

    this.entries.unshift(entry); // Prepend for latest-first
    return entry;
  }

  public getEntries(): AuditLogEntry[] {
    return [...this.entries];
  }

  public clear() {
    this.entries = [];
  }
}

export const auditLogger = new AuditLogger();
