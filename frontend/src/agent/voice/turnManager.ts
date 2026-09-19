/**
 * PLANT-X Turn Management State Machine.
 * 
 * Deterministic state transitions supporting conversational turn-taking,
 * self-corrections, pauses, and instant barge-in.
 */

import type { TurnState } from './providerTypes';

export type TurnEvent =
  | 'USER_START_SPEAK'
  | 'USER_PAUSE'
  | 'USER_RESUME_SPEAK'
  | 'USER_FINISH_SPEAK'
  | 'MODEL_START_THINK'
  | 'MODEL_START_SPEAK'
  | 'MODEL_FINISH_SPEAK'
  | 'BARGE_IN_TRIGGERED'
  | 'RESET_IDLE'
  | 'CONNECTION_LOST';

export class TurnManager {
  private currentState: TurnState = 'IDLE';
  private listeners: Array<(state: TurnState, prev: TurnState) => void> = [];
  private pauseTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly pauseThresholdMs: number = 800;


  constructor(initialState: TurnState = 'IDLE') {
    this.currentState = initialState;
  }

  public getState(): TurnState {
    return this.currentState;
  }

  public onStateChange(listener: (state: TurnState, prev: TurnState) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private transition(nextState: TurnState) {
    if (this.currentState === nextState) return;
    const prev = this.currentState;
    this.currentState = nextState;
    for (const listener of this.listeners) {
      listener(nextState, prev);
    }
  }

  public handleEvent(event: TurnEvent): TurnState {
    if (this.pauseTimer) {
      clearTimeout(this.pauseTimer);
      this.pauseTimer = null;
    }

    switch (event) {
      case 'USER_START_SPEAK':
        if (this.currentState === 'MODEL_SPEAKING' || this.currentState === 'MODEL_THINKING') {
          this.transition('USER_INTERRUPTED');
        } else {
          this.transition('USER_SPEAKING');
        }
        break;

      case 'USER_PAUSE':
        if (this.currentState === 'USER_SPEAKING' || this.currentState === 'USER_INTERRUPTED') {
          this.transition('USER_PAUSED');
          this.pauseTimer = setTimeout(() => {
            if (this.currentState === 'USER_PAUSED') {
              this.handleEvent('USER_FINISH_SPEAK');
            }
          }, this.pauseThresholdMs);
        }
        break;

      case 'USER_RESUME_SPEAK':
        if (this.currentState === 'USER_PAUSED') {
          this.transition('USER_SPEAKING');
        }
        break;

      case 'USER_FINISH_SPEAK':
        this.transition('MODEL_THINKING');
        break;

      case 'MODEL_START_THINK':
        this.transition('MODEL_THINKING');
        break;

      case 'MODEL_START_SPEAK':
        this.transition('MODEL_SPEAKING');
        break;

      case 'MODEL_FINISH_SPEAK':
        this.transition('IDLE');
        break;

      case 'BARGE_IN_TRIGGERED':
        this.transition('USER_INTERRUPTED');
        break;

      case 'RESET_IDLE':
        this.transition('IDLE');
        break;

      case 'CONNECTION_LOST':
        this.transition('DISCONNECTED');
        break;
    }

    return this.currentState;
  }
}
