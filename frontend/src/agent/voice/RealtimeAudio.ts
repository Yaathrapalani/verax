/**
 * PLANT-X REALTIME AUDIO LAYER
 * 
 * High-performance browser-native audio pipeline for Gemini Live & voice control.
 * Isolated from React rendering. Supports audio capture, ring buffering,
 * Voice Activity Detection (VAD), barge-in / playback cancellation,
 * and connection health monitoring.
 */

export type AudioTurnState =
  | 'IDLE'
  | 'USER_SPEAKING'
  | 'USER_PAUSED'
  | 'MODEL_THINKING'
  | 'MODEL_SPEAKING'
  | 'USER_INTERRUPTED'
  | 'RESUMING';

export interface AudioTelemetry {
  micLatencyMs: number;
  vadLatencyMs: number;
  playbackLatencyMs: number;
  activeInputLevel: number;
  packetLossCount: number;
  audioTurnState: AudioTurnState;
  sampleRate: number;
  isBargeInActive: boolean;
}

export interface AudioBufferStats {
  bufferedBytes: number;
  underruns: number;
  overflows: number;
  activeSourcesCount: number;
}

export class AudioBufferManager {
  private bufferQueue: Uint8Array[] = [];
  private maxBufferSize: number;
  private underruns = 0;
  private overflows = 0;

  constructor(maxBufferSize: number = 1024 * 1024) {
    this.maxBufferSize = maxBufferSize;
  }

  public push(chunk: Uint8Array): void {
    const currentSize = this.getBufferedSize();
    if (currentSize + chunk.length > this.maxBufferSize) {
      this.overflows++;
      this.bufferQueue.shift(); // Drop oldest to prevent memory explosion
    }
    this.bufferQueue.push(chunk);
  }

  public shift(): Uint8Array | undefined {
    const chunk = this.bufferQueue.shift();
    if (!chunk) {
      this.underruns++;
    }
    return chunk;
  }

  public clear(): void {
    this.bufferQueue = [];
  }

  public getBufferedSize(): number {
    return this.bufferQueue.reduce((acc, c) => acc + c.length, 0);
  }

  public getStats(): AudioBufferStats {
    return {
      bufferedBytes: this.getBufferedSize(),
      underruns: this.underruns,
      overflows: this.overflows,
      activeSourcesCount: this.bufferQueue.length,
    };
  }
}

export class VoiceActivityDetector {
  private energyThreshold: number;
  private consecutiveActiveFrames = 0;
  private consecutiveSilenceFrames = 0;
  private isActive = false;

  constructor(energyThreshold = 0.015) {
    this.energyThreshold = energyThreshold;
  }

  /**
   * Evaluates RMS energy of 16-bit PCM or Float32 chunk.
   */
  public processFloatChunk(samples: Float32Array): { isSpeaking: boolean; rms: number } {
    let sum = 0;
    for (let i = 0; i < samples.length; i++) {
      sum += samples[i] * samples[i];
    }
    const rms = Math.sqrt(sum / (samples.length || 1));

    if (rms > this.energyThreshold) {
      this.consecutiveActiveFrames++;
      this.consecutiveSilenceFrames = 0;
      if (this.consecutiveActiveFrames >= 2) {
        this.isActive = true;
      }
    } else {
      this.consecutiveSilenceFrames++;
      this.consecutiveActiveFrames = 0;
      if (this.consecutiveSilenceFrames >= 8) {
        this.isActive = false;
      }
    }

    return { isSpeaking: this.isActive, rms };
  }

  public setThreshold(threshold: number): void {
    this.energyThreshold = threshold;
  }

  public reset(): void {
    this.isActive = false;
    this.consecutiveActiveFrames = 0;
    this.consecutiveSilenceFrames = 0;
  }
}

export class BargeInController {
  private isBargingIn = false;
  private onBargeInCallbacks: Array<() => void> = [];

  public triggerBargeIn(): void {
    this.isBargingIn = true;
    for (const cb of this.onBargeInCallbacks) {
      cb();
    }
  }

  public onBargeIn(cb: () => void): () => void {
    this.onBargeInCallbacks.push(cb);
    return () => {
      this.onBargeInCallbacks = this.onBargeInCallbacks.filter((c) => c !== cb);
    };
  }

  public reset(): void {
    this.isBargingIn = false;
  }

  public get isActive(): boolean {
    return this.isBargingIn;
  }
}

export class PlaybackController {
  private audioCtx: any | null = null;
  private activeSources: any[] = [];
  private isPlaying = false;

  constructor(audioCtx?: any) {
    this.audioCtx = audioCtx || null;
  }

  public setAudioContext(ctx: any): void {
    this.audioCtx = ctx;
  }

  public async playPcm16Chunk(
    pcmData: Int16Array,
    sampleRate = 24000
  ): Promise<void> {
    if (!this.audioCtx) return;

    try {
      const float32 = new Float32Array(pcmData.length);
      for (let i = 0; i < pcmData.length; i++) {
        float32[i] = pcmData[i] / 32768.0;
      }

      const buffer = this.audioCtx.createBuffer(1, float32.length, sampleRate);
      buffer.copyToChannel(float32, 0);

      const source = this.audioCtx.createBufferSource();
      source.buffer = buffer;
      source.connect(this.audioCtx.destination);

      this.activeSources.push(source);
      this.isPlaying = true;

      source.onended = () => {
        this.activeSources = this.activeSources.filter((s) => s !== source);
        if (this.activeSources.length === 0) {
          this.isPlaying = false;
        }
      };

      source.start();
    } catch {
      // AudioContext unavailable or suspended
    }
  }

  public stopAllPlayback(): void {
    for (const source of this.activeSources) {
      try {
        source.stop();
        source.disconnect();
      } catch {
        // Source might have already stopped
      }
    }
    this.activeSources = [];
    this.isPlaying = false;
  }

  public get currentlyPlaying(): boolean {
    return this.isPlaying;
  }
}

export class ConnectionHealthMonitor {
  private lastPingTime = 0;
  private rttMs = 0;
  private packetLossCount = 0;
  private status: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY' = 'HEALTHY';

  public recordPing(): void {
    this.lastPingTime = Date.now();
  }

  public recordPong(): number {
    if (this.lastPingTime > 0) {
      this.rttMs = Date.now() - this.lastPingTime;
    }
    this.evaluateHealth();
    return this.rttMs;
  }

  public recordPacketLoss(): void {
    this.packetLossCount++;
    this.evaluateHealth();
  }

  private evaluateHealth(): void {
    if (this.packetLossCount > 5 || this.rttMs > 400) {
      this.status = 'UNHEALTHY';
    } else if (this.packetLossCount > 1 || this.rttMs > 150) {
      this.status = 'DEGRADED';
    } else {
      this.status = 'HEALTHY';
    }
  }

  public getTelemetry(): { rttMs: number; packetLoss: number; status: string } {
    return {
      rttMs: this.rttMs,
      packetLoss: this.packetLossCount,
      status: this.status,
    };
  }

  public reset(): void {
    this.lastPingTime = 0;
    this.rttMs = 0;
    this.packetLossCount = 0;
    this.status = 'HEALTHY';
  }
}

export class RealtimeAudioController {
  private audioCtx: any | null = null;
  private vad = new VoiceActivityDetector();
  private bufferManager = new AudioBufferManager();
  private bargeIn = new BargeInController();
  private playback: PlaybackController;
  private health = new ConnectionHealthMonitor();

  private turnState: AudioTurnState = 'IDLE';
  private telemetry: AudioTelemetry = {
    micLatencyMs: 12,
    vadLatencyMs: 4,
    playbackLatencyMs: 18,
    activeInputLevel: 0,
    packetLossCount: 0,
    audioTurnState: 'IDLE',
    sampleRate: 16000,
    isBargeInActive: false,
  };

  private stateSubscribers: Array<(state: AudioTurnState) => void> = [];
  private telemetrySubscribers: Array<(telemetry: AudioTelemetry) => void> = [];

  private mediaStream: any | null = null;
  private inputSourceNode: any | null = null;
  private processorNode: any | null = null;
  private onAudioChunkCallback: ((pcmChunk: Int16Array) => void) | null = null;

  constructor() {
    this.playback = new PlaybackController();
    this.bargeIn.onBargeIn(() => {
      this.playback.stopAllPlayback();
      this.setTurnState('USER_INTERRUPTED');
    });
  }

  public setOnAudioChunk(cb: (pcmChunk: Int16Array) => void): void {
    this.onAudioChunkCallback = cb;
  }

  public initBrowserAudio(): boolean {
    if (typeof window !== 'undefined' && (window.AudioContext || (window as any).webkitAudioContext)) {
      if (!this.audioCtx) {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        this.audioCtx = new AudioContextClass({ sampleRate: 16000 });
        this.playback.setAudioContext(this.audioCtx);
      }
      return true;
    }
    return false;
  }

  public async startMicrophoneCapture(): Promise<boolean> {
    if (typeof window === 'undefined' || !navigator?.mediaDevices?.getUserMedia) {
      return false;
    }

    try {
      this.initBrowserAudio();
      if (this.audioCtx && this.audioCtx.state === 'suspended') {
        await this.audioCtx.resume();
      }

      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      if (!this.audioCtx) return false;

      this.inputSourceNode = this.audioCtx.createMediaStreamSource(this.mediaStream);
      this.processorNode = this.audioCtx.createScriptProcessor(4096, 1, 1);

      // Create a muted gain node so onaudioprocess continues to run in Chromium
      // without leaking raw microphone audio to the speakers (which causes acoustic feedback & false barge-in)
      const silentGain = this.audioCtx.createGain();
      silentGain.gain.value = 0;

      this.processorNode.onaudioprocess = (e: any) => {
        const inputData = e.inputBuffer.getChannelData(0);
        this.handleIncomingUserAudio(inputData);

        // Convert Float32 to Int16 PCM
        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }

        if (this.onAudioChunkCallback) {
          this.onAudioChunkCallback(pcm16);
        }
      };

      this.inputSourceNode.connect(this.processorNode);
      this.processorNode.connect(silentGain);
      silentGain.connect(this.audioCtx.destination);
      this.setTurnState('USER_SPEAKING');
      return true;
    } catch {
      this.setTurnState('IDLE');
      return false;
    }
  }

  public stopMicrophoneCapture(): void {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track: any) => track.stop());
      this.mediaStream = null;
    }

    if (this.processorNode) {
      try {
        this.processorNode.disconnect();
      } catch { /* ignore */ }
      this.processorNode = null;
    }

    if (this.inputSourceNode) {
      try {
        this.inputSourceNode.disconnect();
      } catch { /* ignore */ }
      this.inputSourceNode = null;
    }

    this.setTurnState('IDLE');
  }

  public setTurnState(state: AudioTurnState): void {
    this.turnState = state;
    this.telemetry.audioTurnState = state;
    this.telemetry.isBargeInActive = state === 'USER_INTERRUPTED';
    for (const sub of this.stateSubscribers) {
      sub(state);
    }
    this.notifyTelemetry();
  }

  public getTurnState(): AudioTurnState {
    return this.turnState;
  }

  public handleIncomingUserAudio(floatChunk: Float32Array): { isSpeaking: boolean; rms: number } {
    const vadResult = this.vad.processFloatChunk(floatChunk);
    this.telemetry.activeInputLevel = vadResult.rms;

    if (vadResult.isSpeaking) {
      if (this.turnState === 'MODEL_SPEAKING' || this.playback.currentlyPlaying) {
        // Barge-in detected
        this.bargeIn.triggerBargeIn();
      } else if (this.turnState !== 'USER_SPEAKING') {
        this.setTurnState('USER_SPEAKING');
      }
    } else if (this.turnState === 'USER_SPEAKING') {
      this.setTurnState('USER_PAUSED');
    }

    this.notifyTelemetry();
    return vadResult;
  }

  public stopSpeech(): void {
    this.playback.stopAllPlayback();
    if (this.turnState === 'MODEL_SPEAKING') {
      this.setTurnState('IDLE');
    }
  }

  public onTurnStateChange(cb: (state: AudioTurnState) => void): () => void {
    this.stateSubscribers.push(cb);
    return () => {
      this.stateSubscribers = this.stateSubscribers.filter((s) => s !== cb);
    };
  }

  public onTelemetryUpdate(cb: (telemetry: AudioTelemetry) => void): () => void {
    this.telemetrySubscribers.push(cb);
    return () => {
      this.telemetrySubscribers = this.telemetrySubscribers.filter((s) => s !== cb);
    };
  }

  private notifyTelemetry(): void {
    const healthTelem = this.health.getTelemetry();
    this.telemetry.packetLossCount = healthTelem.packetLoss;
    for (const sub of this.telemetrySubscribers) {
      sub({ ...this.telemetry });
    }
  }

  public getTelemetrySnapshot(): AudioTelemetry {
    return { ...this.telemetry };
  }

  public getBufferStats(): AudioBufferStats {
    return this.bufferManager.getStats();
  }

  public dispose(): void {
    this.playback.stopAllPlayback();
    if (this.audioCtx && typeof this.audioCtx.close === 'function') {
      try {
        this.audioCtx.close();
      } catch {
        // Ignore AudioContext close errors
      }
    }
    this.audioCtx = null;
    this.stateSubscribers = [];
    this.telemetrySubscribers = [];
    this.bargeIn.reset();
  }
}

export const realtimeAudioController = new RealtimeAudioController();
