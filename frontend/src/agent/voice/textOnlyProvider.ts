/**
 * PLANT-X Text Only and Demo Voice Providers.
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


export class TextOnlyProvider implements ConversationalVoiceProvider {
  public readonly providerType: VoiceProviderType = 'text-only';
  private status: VoiceSessionStatus = 'DISCONNECTED';
  private turnState: TurnState = 'IDLE';

  private transcriptListeners: Array<(text: string, isUser: boolean, isFinal: boolean) => void> = [];
  private statusListeners: Array<(status: VoiceSessionStatus, message?: string) => void> = [];
  private turnStateListeners: Array<(turn: TurnState) => void> = [];

  public getStatus(): VoiceSessionStatus { return this.status; }
  public getTurnState(): TurnState { return this.turnState; }
  public getCapabilities(): VoiceCapabilities {
    return {
      nativeAudioStreaming: false,
      bidirectionalToolCalling: false,
      extendedThinking: false,
      bargeInSupport: true,
      offlineSupport: true,
    };
  }

  public async connect(_config: VoiceSessionConfig): Promise<void> {
    this.status = 'CONNECTED';
    for (const l of this.statusListeners) l('CONNECTED', 'Text-only workstation mode active');
  }

  public async disconnect(): Promise<void> {
    this.status = 'DISCONNECTED';
    this.turnState = 'IDLE';
    for (const l of this.statusListeners) l('DISCONNECTED');
  }

  public sendAudio(_chunk: Float32Array | Int16Array): void { /* no-op */ }
  public sendText(text: string): void {
    for (const l of this.transcriptListeners) l(text, true, true);
    this.turnState = 'MODEL_THINKING';
  }
  public sendToolResponse(_response: ToolCallResponse): void { /* no-op */ }
  public interrupt(_type: InterruptionType): void {
    this.turnState = 'IDLE';
    for (const l of this.turnStateListeners) l('IDLE');
  }
  public configureSession(_config: Partial<VoiceSessionConfig>): void { /* no-op */ }

  public on(event: 'audio', handler: (chunk: ArrayBuffer) => void): () => void;
  public on(event: 'transcript', handler: (text: string, isUser: boolean, isFinal: boolean) => void): () => void;
  public on(event: 'toolCall', handler: (call: ToolCallRequest) => void): () => void;
  public on(event: 'statusChange', handler: (status: VoiceSessionStatus, message?: string) => void): () => void;
  public on(event: 'turnStateChange', handler: (turn: TurnState) => void): () => void;
  public on(event: string, handler: unknown): () => void {
    if (event === 'transcript') {
      const h = handler as (text: string, isUser: boolean, isFinal: boolean) => void;
      this.transcriptListeners.push(h);
      return () => { this.transcriptListeners = this.transcriptListeners.filter(l => l !== h); };
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

export class DemoVoiceProvider implements ConversationalVoiceProvider {
  public readonly providerType: VoiceProviderType = 'demo';
  private status: VoiceSessionStatus = 'DISCONNECTED';
  private turnState: TurnState = 'IDLE';

  private transcriptListeners: Array<(text: string, isUser: boolean, isFinal: boolean) => void> = [];
  private toolCallListeners: Array<(call: ToolCallRequest) => void> = [];
  private statusListeners: Array<(status: VoiceSessionStatus, message?: string) => void> = [];
  private turnStateListeners: Array<(turn: TurnState) => void> = [];

  public getStatus(): VoiceSessionStatus { return this.status; }
  public getTurnState(): TurnState { return this.turnState; }
  public getCapabilities(): VoiceCapabilities {
    return {
      nativeAudioStreaming: false,
      bidirectionalToolCalling: true,
      extendedThinking: false,
      bargeInSupport: true,
      offlineSupport: true,
    };
  }

  public async connect(_config: VoiceSessionConfig): Promise<void> {
    this.status = 'CONNECTED';
    for (const l of this.statusListeners) l('CONNECTED', 'Demo voice provider active (simulated script)');
  }

  public async disconnect(): Promise<void> {
    this.status = 'DISCONNECTED';
    this.turnState = 'IDLE';
    for (const l of this.statusListeners) l('DISCONNECTED');
  }

  public sendAudio(_chunk: Float32Array | Int16Array): void { /* no-op */ }
  public sendText(text: string): void {
    for (const l of this.transcriptListeners) l(text, true, true);
    this.turnState = 'MODEL_THINKING';
  }
  public sendToolResponse(_response: ToolCallResponse): void { /* no-op */ }
  public interrupt(_type: InterruptionType): void {
    this.turnState = 'IDLE';
    for (const l of this.turnStateListeners) l('IDLE');
  }
  public configureSession(_config: Partial<VoiceSessionConfig>): void { /* no-op */ }

  public on(event: 'audio', handler: (chunk: ArrayBuffer) => void): () => void;
  public on(event: 'transcript', handler: (text: string, isUser: boolean, isFinal: boolean) => void): () => void;
  public on(event: 'toolCall', handler: (call: ToolCallRequest) => void): () => void;
  public on(event: 'statusChange', handler: (status: VoiceSessionStatus, message?: string) => void): () => void;
  public on(event: 'turnStateChange', handler: (turn: TurnState) => void): () => void;
  public on(event: string, handler: unknown): () => void {
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
