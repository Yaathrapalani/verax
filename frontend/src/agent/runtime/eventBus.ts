/**
 * PLANT-X Strongly Typed Workstation Event Bus.
 * 
 * Synchronizes Process, 3D, Inspector, Evidence, and Agent projections
 * without allowing any projection to become an authoritative source of truth.
 */

export type WorkstationEventType =
  | 'VOICE_COMMAND_RECEIVED'
  | 'VOICE_STARTED'
  | 'VOICE_INTERRUPTED'
  | 'COMMAND_RESOLVED'
  | 'COMMAND_STARTED'
  | 'COMMAND_COMPLETED'
  | 'COMMAND_FAILED'
  | 'ROUTE_CHANGED'
  | 'EQUIPMENT_SELECTED'
  | 'STREAM_SELECTED'
  | 'GRAPH_SELECTED'
  | 'CAMERA_FOCUSED'
  | 'PATH_HIGHLIGHTED'
  | 'FOULING_UPDATED'
  | 'PREDICTION_UPDATED'
  | 'UNCERTAINTY_UPDATED'
  | 'RELIABILITY_CHANGED'
  | 'SCENARIO_SCHEDULED'
  | 'TIMER_STARTED'
  | 'TIMER_TICK'
  | 'TIMER_COMPLETED'
  | 'TIMER_CANCELLED'
  | 'TASK_STARTED'
  | 'TASK_COMPLETED'
  | 'TASK_CANCELLED'
  | 'HYPOTHESIS_UPDATED'
  | 'INVESTIGATION_UPDATED'
  | 'PROACTIVE_SUGGESTION_CREATED'
  | 'PROACTIVE_SUGGESTION_DISMISSED'
  | 'EVIDENCE_OPENED'
  | 'PROVENANCE_OPENED';

export interface WorkstationEvent<T = unknown> {
  id: string;
  type: WorkstationEventType;
  timestamp: number;
  payload: T;
  version: number;
}

export class WorkstationEventBus {
  private static instance: WorkstationEventBus;
  private listeners: Map<WorkstationEventType, Array<(event: WorkstationEvent) => void>> = new Map();
  private history: WorkstationEvent[] = [];
  private eventVersion = 1;

  public static getInstance(): WorkstationEventBus {
    if (!WorkstationEventBus.instance) {
      WorkstationEventBus.instance = new WorkstationEventBus();
    }
    return WorkstationEventBus.instance;
  }

  public emit<T = unknown>(type: WorkstationEventType, payload: T): WorkstationEvent<T> {
    const event: WorkstationEvent<T> = {
      id: `evt_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      type,
      timestamp: Date.now(),
      payload,
      version: this.eventVersion++,
    };

    this.history.push(event as WorkstationEvent);
    if (this.history.length > 500) this.history.shift();

    const subs = this.listeners.get(type);
    if (subs) {
      for (const sub of subs) {
        try {
          sub(event as WorkstationEvent);
        } catch { /* ignore subscriber error */ }
      }
    }

    return event;
  }

  public on(type: WorkstationEventType, handler: (event: WorkstationEvent) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(handler);
    return () => {
      const subs = this.listeners.get(type);
      if (subs) {
        this.listeners.set(type, subs.filter(s => s !== handler));
      }
    };
  }

  public getRecentEvents(count: number = 50): WorkstationEvent[] {
    return this.history.slice(-count);
  }
}
