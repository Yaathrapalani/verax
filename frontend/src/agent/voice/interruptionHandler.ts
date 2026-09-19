/**
 * PLANT-X Interruption & Cancellation Handler.
 * 
 * Accurately distinguishes between conversational interruptions:
 * - STOP_SPEECH: Halts current TTS/audio stream without cancelling active tasks.
 * - CANCEL_COMMAND: Cancels in-flight cancellable command.
 * - CANCEL_TASK: Cancels background scenario or computational task.
 * - CANCEL_TIMER: Cancels pending delayed countdown.
 * - PAUSE_TASK: Pauses pausable active task.
 * - STOP_LISTENING: Closes mic capture.
 * - END_VOICE_SESSION: Disconnects provider session.
 */

import type { InterruptionType } from './providerTypes';

export interface InterruptionCallbacks {
  onStopSpeech?: () => void;
  onCancelCommand?: () => void;
  onCancelTask?: (taskId?: string) => void;
  onCancelTimer?: () => void;
  onPauseTask?: (taskId?: string) => void;
  onStopListening?: () => void;
  onEndVoiceSession?: () => void;
}

export class InterruptionHandler {
  private callbacks: InterruptionCallbacks = {};

  constructor(callbacks: InterruptionCallbacks = {}) {
    this.callbacks = callbacks;
  }

  public setCallbacks(callbacks: Partial<InterruptionCallbacks>) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  public routeInterruption(type: InterruptionType, targetId?: string): { handled: boolean; action: string } {
    switch (type) {
      case 'STOP_SPEECH':
        this.callbacks.onStopSpeech?.();
        return { handled: true, action: 'Audio output halted; microphone remains active' };

      case 'CANCEL_COMMAND':
        this.callbacks.onCancelCommand?.();
        return { handled: true, action: 'Pending voice command execution cancelled' };

      case 'CANCEL_TASK':
        this.callbacks.onCancelTask?.(targetId);
        return { handled: true, action: `Task ${targetId ?? 'active'} cancelled` };

      case 'CANCEL_TIMER':
        this.callbacks.onCancelTimer?.();
        return { handled: true, action: 'Scheduled countdown timer cancelled' };

      case 'PAUSE_TASK':
        this.callbacks.onPauseTask?.(targetId);
        return { handled: true, action: `Task ${targetId ?? 'active'} paused` };

      case 'STOP_LISTENING':
        this.callbacks.onStopListening?.();
        return { handled: true, action: 'Microphone stream suspended' };

      case 'END_VOICE_SESSION':
        this.callbacks.onEndVoiceSession?.();
        return { handled: true, action: 'Conversational voice session terminated' };

      default:
        return { handled: false, action: 'Unknown interruption type' };
    }
  }

  /**
   * Evaluates natural utterance to classify interruption intent.
   */
  public classifyInterruptionText(text: string): InterruptionType | null {
    const norm = text.trim().toLowerCase();
    if (/^(stop talking|be quiet|silence|shh|shut up)$/i.test(norm)) {
      return 'STOP_SPEECH';
    }
    if (/^(cancel the timer|stop the timer|abort timer)$/i.test(norm)) {
      return 'CANCEL_TIMER';
    }
    if (/^(cancel task|stop task|abort run|abort scenario)$/i.test(norm)) {
      return 'CANCEL_TASK';
    }
    if (/^(pause|pause task|hold on a second|wait a second)$/i.test(norm)) {
      return 'PAUSE_TASK';
    }
    if (/^(stop listening|mute mic|turn off microphone)$/i.test(norm)) {
      return 'STOP_LISTENING';
    }
    if (/^(cancel|cancel that|abort|wait|never mind|stop)$/i.test(norm)) {
      return 'CANCEL_COMMAND';
    }
    return null;
  }
}
