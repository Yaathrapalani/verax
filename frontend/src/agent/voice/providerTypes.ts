/**
 * PLANT-X Conversational Voice Provider Types.
 * 
 * Defines the clean provider abstraction supporting Gemini 3.8 Live,
 * browser fallback, text-only, and demo modes.
 */

export type VoiceProviderType = 'gemini-live' | 'browser-speech' | 'text-only' | 'demo';

export type VoiceSessionStatus =
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'CONNECTED'
  | 'RECONNECTING'
  | 'ERROR';

export type TurnState =
  | 'IDLE'
  | 'USER_SPEAKING'
  | 'USER_PAUSED'
  | 'MODEL_THINKING'
  | 'MODEL_SPEAKING'
  | 'USER_INTERRUPTED'
  | 'MODEL_INTERRUPTED'
  | 'RESUMING'
  | 'ERROR'
  | 'DISCONNECTED';

export type InterruptionType =
  | 'STOP_SPEECH'
  | 'CANCEL_COMMAND'
  | 'CANCEL_TASK'
  | 'CANCEL_TIMER'
  | 'PAUSE_TASK'
  | 'STOP_LISTENING'
  | 'END_VOICE_SESSION';

export type VoicePersonality = 'ENGINEER' | 'EXPLAINER';

export type InteractionMode = 'PUSH_TO_TALK' | 'TAP_TO_TALK' | 'CONTINUOUS_LISTENING';

export interface VoiceSessionConfig {
  providerType: VoiceProviderType;
  model: 'gemini-3.8-live' | 'gemini-3.8-live-extended-thinking';
  personality: VoicePersonality;
  mode: InteractionMode;
  ephemeralToken?: string;
  sampleRate?: number;
}

export interface VoiceCapabilities {
  nativeAudioStreaming: boolean;
  bidirectionalToolCalling: boolean;
  extendedThinking: boolean;
  bargeInSupport: boolean;
  offlineSupport: boolean;
}

export interface ToolCallRequest {
  callId: string;
  toolName: string;
  arguments: Record<string, unknown>;
}

export interface ToolCallResponse {
  callId: string;
  result: Record<string, unknown>;
  truthState?: string;
  isError?: boolean;
}

export interface ConversationalVoiceProvider {
  readonly providerType: VoiceProviderType;
  getStatus(): VoiceSessionStatus;
  getTurnState(): TurnState;
  getCapabilities(): VoiceCapabilities;
  
  connect(config: VoiceSessionConfig): Promise<void>;
  disconnect(): Promise<void>;
  
  sendAudio(chunk: Float32Array | Int16Array): void;
  sendText(text: string): void;
  sendToolResponse(response: ToolCallResponse): void;
  
  interrupt(type: InterruptionType): void;
  configureSession(config: Partial<VoiceSessionConfig>): void;
  
  on(event: 'audio', handler: (chunk: ArrayBuffer) => void): () => void;
  on(event: 'transcript', handler: (text: string, isUser: boolean, isFinal: boolean) => void): () => void;
  on(event: 'toolCall', handler: (call: ToolCallRequest) => void): () => void;
  on(event: 'statusChange', handler: (status: VoiceSessionStatus, message?: string) => void): () => void;
  on(event: 'turnStateChange', handler: (turn: TurnState) => void): () => void;
}
