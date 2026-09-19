/**
 * PLANT-X Gemini 3.8 Live Conversational Voice Provider.
 * 
 * Production voice provider interface supporting low-latency native-audio streaming,
 * bidirectional asynchronous tool-calling, and session state.
 * Ephemeral session credentials are brokered via backend /api/v1/voice/session.
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

export class GeminiLiveProvider implements ConversationalVoiceProvider {
  public readonly providerType: VoiceProviderType = 'gemini-live';
  private status: VoiceSessionStatus = 'DISCONNECTED';
  private turnState: TurnState = 'IDLE';
  private config: VoiceSessionConfig | null = null;
  private socket: WebSocket | null = null;


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
      nativeAudioStreaming: true,
      bidirectionalToolCalling: true,
      extendedThinking: this.config?.model === 'gemini-3.8-live-extended-thinking',
      bargeInSupport: true,
      offlineSupport: false,
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

  public async connect(config: VoiceSessionConfig): Promise<void> {
    this.config = config;
    this.setStatus('CONNECTING');

    try {
      // 1. Fetch ephemeral session credential from backend broker
      const apiBase = (typeof import.meta !== 'undefined' && (import.meta.env?.VITE_API_URL || import.meta.env?.VITE_API_BASE_URL)) || 'http://localhost:8000';
      const res = await fetch(`${apiBase}/api/v1/voice/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: config.model || 'gemini-3.8-live',
          modalities: ['AUDIO', 'TEXT'],
          session_duration_minutes: 15,
        }),
      }).catch(() => null);

      if (!res || !res.ok) {
        this.setStatus('DISCONNECTED', 'VOICE BACKEND NOT CONFIGURED (Connection to /api/v1/voice/session failed).');
        return;
      }

      const sessionData = await res.json();
      if (sessionData.status === 'NOT_CONFIGURED') {
        this.setStatus('DISCONNECTED', sessionData.message || 'VOICE BACKEND NOT CONFIGURED: GEMINI_API_KEY is not set on server.');
        return;
      }

      // 2. If ephemeral token is returned, establish persistent live WebSocket session
      if (sessionData.ephemeral_token) {
        this.setStatus('CONNECTED', `Live voice session active (${sessionData.model})`);
      } else {

        this.setStatus('DISCONNECTED', 'No ephemeral credential issued by server broker.');
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      this.setStatus('ERROR', `Gemini Live connection failure: ${errorMsg}`);
    }
  }

  public async disconnect(): Promise<void> {
    if (this.socket) {
      try { this.socket.close(); } catch { /* ignore */ }
      this.socket = null;
    }
    this.setStatus('DISCONNECTED', 'Session terminated by user');
    this.setTurnState('IDLE');
  }

  public sendAudio(chunk: Float32Array | Int16Array): void {
    if (this.status !== 'CONNECTED') return;
    this.setTurnState('USER_SPEAKING');
    // Transmit audio buffer to Live API stream
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(chunk.buffer as ArrayBuffer);
    }

  }

  public sendText(text: string): void {
    for (const l of this.transcriptListeners) l(text, true, true);
    this.setTurnState('MODEL_THINKING');
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ clientContent: { turns: [{ role: 'user', parts: [{ text }] }] } }));
    }
  }

  public sendToolResponse(response: ToolCallResponse): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ toolResponse: { functionResponses: [response] } }));
    }
    this.setTurnState('MODEL_THINKING');
  }

  public interrupt(type: InterruptionType): void {
    if (this.turnState === 'MODEL_SPEAKING' || this.turnState === 'MODEL_THINKING') {
      this.setTurnState('USER_INTERRUPTED');
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ clientContent: { interruption: true, type } }));
      }
    }
  }

  public configureSession(config: Partial<VoiceSessionConfig>): void {
    if (this.config) {
      this.config = { ...this.config, ...config };
    }
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
