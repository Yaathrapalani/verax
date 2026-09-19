/**
 * PLANT-X Browser Speech Fallback Provider.
 * 
 * Implements ConversationalVoiceProvider using standard browser Web Speech API
 * (SpeechRecognition + SpeechSynthesis) for deterministic offline and client-only fallback.
 */

import type {
  ConversationalVoiceProvider,
  VoiceProviderType,
  VoiceSessionConfig,
  VoiceSessionStatus,
  VoiceCapabilities,
  TurnState,
  InterruptionType,
  ToolCallRequest,
  ToolCallResponse,
} from './providerTypes';


// Extend window for webkitSpeechRecognition
interface SpeechRecognitionEventLike {
  results: {
    [index: number]: {
      [index: number]: { transcript: string };
      isFinal: boolean;
    };
  };
}

interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: unknown) => void) | null;
  onend: (() => void) | null;
}

export class BrowserSpeechFallbackProvider implements ConversationalVoiceProvider {
  public readonly providerType: VoiceProviderType = 'browser-speech';
  private status: VoiceSessionStatus = 'DISCONNECTED';
  private turnState: TurnState = 'IDLE';
  private recognition: SpeechRecognitionLike | null = null;
  private currentUtterance: SpeechSynthesisUtterance | null = null;

  private audioListeners: Array<(chunk: ArrayBuffer) => void> = [];
  private transcriptListeners: Array<(text: string, isUser: boolean, isFinal: boolean) => void> = [];
  private toolCallListeners: Array<(call: ToolCallRequest) => void> = [];
  private statusListeners: Array<(status: VoiceSessionStatus, message?: string) => void> = [];
  private turnStateListeners: Array<(turn: TurnState) => void> = [];

  public getStatus(): VoiceSessionStatus {
    return this.status;
  }

  public getTurnState(): TurnState {
    return this.turnState;
  }

  public getCapabilities(): VoiceCapabilities {
    return {
      nativeAudioStreaming: false,
      bidirectionalToolCalling: false,
      extendedThinking: false,
      bargeInSupport: true,
      offlineSupport: true,
    };
  }

  private setStatus(newStatus: VoiceSessionStatus, message?: string) {
    this.status = newStatus;
    for (const l of this.statusListeners) l(newStatus, message);
  }

  private setTurnState(newState: TurnState) {
    this.turnState = newState;
    for (const l of this.turnStateListeners) l(newState);
  }

  public async connect(_config: VoiceSessionConfig): Promise<void> {
    this.setStatus('CONNECTING');
    if (typeof window !== 'undefined') {
      const SpeechRec = (window as unknown as { SpeechRecognition?: new () => SpeechRecognitionLike; webkitSpeechRecognition?: new () => SpeechRecognitionLike }).SpeechRecognition ||
        (window as unknown as { webkitSpeechRecognition?: new () => SpeechRecognitionLike }).webkitSpeechRecognition;

      if (SpeechRec) {
        this.recognition = new SpeechRec();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onresult = (event: SpeechRecognitionEventLike) => {
          let interim = '';
          for (let i = 0; i < 50; i++) {
            const item = event.results[i];
            if (!item) break;
            const transcript = item[0]?.transcript || '';
            if (item.isFinal) {
              for (const l of this.transcriptListeners) l(transcript, true, true);
              this.setTurnState('MODEL_THINKING');
            } else {
              interim += transcript;
            }
          }
          if (interim) {
            for (const l of this.transcriptListeners) l(interim, true, false);
            this.setTurnState('USER_SPEAKING');
          }
        };

        this.recognition.onerror = () => {
          this.setTurnState('IDLE');
        };

        try {
          this.recognition.start();
        } catch { /* ignore */ }
      }
    }
    this.setStatus('CONNECTED', 'Browser speech fallback active (Web Speech API)');
    this.setTurnState('IDLE');
  }

  public async disconnect(): Promise<void> {
    if (this.recognition) {
      try { this.recognition.stop(); } catch { /* ignore */ }
      this.recognition = null;
    }
    this.interrupt('STOP_SPEECH');
    this.setStatus('DISCONNECTED');
    this.setTurnState('IDLE');
  }

  public sendAudio(_chunk: Float32Array | Int16Array): void {
    // Browser speech API captures audio directly via SpeechRecognition microphone stream
  }

  public sendText(text: string): void {
    for (const l of this.transcriptListeners) l(text, true, true);
    this.setTurnState('MODEL_THINKING');
  }

  public sendToolResponse(_response: ToolCallResponse): void {
    // Handled locally in agent runtime
  }

  public interrupt(type: InterruptionType): void {
    if (this.currentUtterance && typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    this.currentUtterance = null;

    if (type === 'STOP_LISTENING' && this.recognition) {
      try { this.recognition.stop(); } catch { /* ignore */ }
    }
    this.setTurnState('IDLE');
  }

  public speakText(text: string, onEnd?: () => void): void {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      onEnd?.();
      return;
    }
    this.interrupt('STOP_SPEECH');
    this.setTurnState('MODEL_SPEAKING');
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 0.95;
    utterance.onend = () => {
      this.currentUtterance = null;
      this.setTurnState('IDLE');
      onEnd?.();
    };
    utterance.onerror = () => {
      this.currentUtterance = null;
      this.setTurnState('IDLE');
      onEnd?.();
    };
    this.currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
    for (const l of this.transcriptListeners) l(text, false, true);
  }

  public configureSession(_config: Partial<VoiceSessionConfig>): void {
    // browser speech fallback has fixed parameters
  }

  public on(event: 'audio', handler: (chunk: ArrayBuffer) => void): () => void;
  public on(event: 'transcript', handler: (text: string, isUser: boolean, isFinal: boolean) => void): () => void;
  public on(event: 'toolCall', handler: (call: ToolCallRequest) => void): () => void;
  public on(event: 'statusChange', handler: (status: VoiceSessionStatus, message?: string) => void): () => void;
  public on(event: 'turnStateChange', handler: (turn: TurnState) => void): () => void;
  public on(event: string, handler: unknown): () => void {
    if (event === 'audio') {
      const h = handler as (chunk: ArrayBuffer) => void;
      this.audioListeners.push(h);
      return () => { this.audioListeners = this.audioListeners.filter(l => l !== h); };
    }
    if (event === 'transcript') {
      const h = handler as (text: string, isUser: boolean, isFinal: boolean) => void;
      this.transcriptListeners.push(h);
      return () => { this.transcriptListeners = this.transcriptListeners.filter(l => l !== h); };
    }
    if (event === 'toolCall') {
      const h = handler as (call: ToolCallRequest) => void;
      this.toolCallListeners.push(h);
      return () => { this.toolCallListeners = this.toolCallListeners.filter(l => l !== h); };
    }
    if (event === 'statusChange') {
      const h = handler as (status: VoiceSessionStatus, message?: string) => void;
      this.statusListeners.push(h);
      return () => { this.statusListeners = this.statusListeners.filter(l => l !== h); };
    }
    if (event === 'turnStateChange') {
      const h = handler as (turn: TurnState) => void;
      this.turnStateListeners.push(h);
      return () => { this.turnStateListeners = this.turnStateListeners.filter(l => l !== h); };
    }
    return () => {};
  }
}
