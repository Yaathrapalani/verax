/**
 * PLANT-X Technical Execution Tracer.
 * 
 * Records granular technical traces of intent resolution, planning,
 * tool execution, validation states, and latency metrics for judges and engineers.
 */

export interface ExecutionTraceEntry {
  traceId: string;
  timestamp: number;
  utterance: string;
  resolvedIntent: string;
  contextSnapshot: Record<string, unknown>;
  plannedSteps: Array<{ tool: string; args: Record<string, unknown> }>;
  executedTools: Array<{
    tool: string;
    args: Record<string, unknown>;
    status: 'SUCCESS' | 'FAILED' | 'REJECTED';
    durationMs: number;
    resultSummary: string;
  }>;
  validationChecks: {
    safetyPolicy: string;
    capabilitiesChecked: string[];
    truthFirewallApproved: boolean;
  };
  stateDeltas: Record<string, unknown>;
  totalLatencyMs: number;
}

export class ExecutionTracer {
  private static traces: ExecutionTraceEntry[] = [];

  public static recordTrace(entry: ExecutionTraceEntry) {
    this.traces.push(entry);
    if (this.traces.length > 100) this.traces.shift();
  }

  public static getLatestTrace(): ExecutionTraceEntry | undefined {
    return this.traces[this.traces.length - 1];
  }

  public static getAllTraces(): ExecutionTraceEntry[] {
    return [...this.traces];
  }

  public static formatTraceReport(trace?: ExecutionTraceEntry): string {
    const t = trace || this.getLatestTrace();
    if (!t) return 'No execution trace available.';

    return `TECHNICAL EXECUTION TRACE [${t.traceId}]
Timestamp: ${new Date(t.timestamp).toISOString()}
Utterance: "${t.utterance}"
Resolved Intent: ${t.resolvedIntent}
Total Latency: ${t.totalLatencyMs.toFixed(1)} ms

VALIDATION & FIREWALL:
- Safety Policy: ${t.validationChecks.safetyPolicy}
- Capabilities Checked: ${t.validationChecks.capabilitiesChecked.join(', ')}
- Truth Firewall Approved: ${t.validationChecks.truthFirewallApproved ? 'PASS' : 'REJECTED/ABSTAIN'}

PLANNED STEPS (${t.plannedSteps.length}):
${t.plannedSteps.map((s, idx) => `  ${idx + 1}. ${s.tool}(${JSON.stringify(s.args)})`).join('\n')}

EXECUTED TOOLS:
${t.executedTools.map(e => `  - [${e.status}] ${e.tool} (${e.durationMs.toFixed(1)}ms): ${e.resultSummary}`).join('\n')}

STATE MUTATIONS:
${JSON.stringify(t.stateDeltas, null, 2)}
`;
  }
}
