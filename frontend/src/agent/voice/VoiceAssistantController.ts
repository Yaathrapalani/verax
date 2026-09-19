/**
 * PLANT-X PERSISTENT WORKSTATION VOICE ASSISTANT CONTROLLER
 * 
 * Workstation-wide persistent assistant orchestrating conversational voice,
 * multi-turn context, intent resolution, command planning, safety policy,
 * truth firewall, deterministic tool execution, and audio playback.
 * 
 * Operates across all views (Process, P&ID, 3D, Evidence, Simulation, Chemistry, Trends).
 * The voice assistant is an interface to the workstation; it is never the source of truth.
 */

import type {
  PlantWorkstationState,
  WorkstationView,
  AgentStatus,
} from '../types';
import { TOOL_REGISTRY } from '../tools';
import { intentParser } from '../intentParser';
import { timerService } from '../timerService';
import { auditLogger } from '../auditLogger';
import { ExecutionTracer } from '../runtime/executionTracer';
import { TruthFirewall } from '../runtime/truthFirewall';
import { realtimeAudioController } from './RealtimeAudio';
import { VoiceProviderRegistry } from './providerRegistry';
import type { VoiceProviderType, TurnState } from './providerTypes';
import { facePresenceDetector } from '../presence/FacePresenceDetector';

export type ExplicitVoiceState =
  | 'GEMINI LIVE — CONNECTED'
  | 'BROWSER SPEECH — ACTIVE'
  | 'TEXT MODE — ACTIVE'
  | 'DEMO VOICE — ACTIVE'
  | 'VOICE BACKEND — NOT CONFIGURED'
  | 'MICROPHONE — BLOCKED'
  | 'VOICE — ERROR';

export interface AssistantTurn {
  id: string;
  timestamp: number;
  speaker: 'USER' | 'ASSISTANT';
  text: string;
  toolUsed?: string;
  truthState?: string;
}

export interface AssistantContextSnapshot {
  currentView: WorkstationView;
  selectedEquipment: string;
  selectedStreamId: string;
  scenario: string;
  activeHypothesisId: string | null;
  lastCommand: string | null;
  lastResponse: string | null;
  stateVersion: number;
  recentTurns: AssistantTurn[];
}

export class VoiceAssistantController {
  private static instance: VoiceAssistantController;

  private state: PlantWorkstationState | null = null;
  private onStateUpdateCallback: ((updater: (prev: PlantWorkstationState) => PlantWorkstationState) => void) | null = null;

  private status: AgentStatus = 'READY';
  private turns: AssistantTurn[] = [];
  private activeProviderType: VoiceProviderType = 'browser-speech';
  private isListening = false;
  private isSpeaking = false;
  private lastTranscript = '';
  private lastResponse = 'Workstation ready. Listening for engineering commands.';
  private subscribers: Array<() => void> = [];
  private activeRecognition: any = null;
  private microphoneBlocked = false;
  private voiceError = false;

  private constructor() {
    // Listen for RealtimeAudio barge-in
    realtimeAudioController.onTurnStateChange((turnState: TurnState) => {
      if (turnState === 'USER_INTERRUPTED') {
        this.stopSpeaking();
      }
    });

    // Wire Privacy-Preserving Face Presence Voice Wake
    facePresenceDetector.setOnWakeCallback(() => {
      if (!this.isListening && !this.isSpeaking) {
        this.startListening();
      }
    });
  }

  public static getInstance(): VoiceAssistantController {
    if (!VoiceAssistantController.instance) {
      VoiceAssistantController.instance = new VoiceAssistantController();
    }
    return VoiceAssistantController.instance;
  }

  public registerWorkstation(
    state: PlantWorkstationState,
    updateState: (updater: (prev: PlantWorkstationState) => PlantWorkstationState) => void
  ): void {
    this.state = state;
    this.onStateUpdateCallback = updateState;
  }

  public syncState(state: PlantWorkstationState): void {
    this.state = state;
  }

  public subscribe(cb: () => void): () => void {
    this.subscribers.push(cb);
    return () => {
      this.subscribers = this.subscribers.filter((s) => s !== cb);
    };
  }

  private notify(): void {
    for (const sub of this.subscribers) {
      sub();
    }
  }

  // Status & Telemetry Getters
  public getStatus(): AgentStatus {
    return this.status;
  }

  public getIsListening(): boolean {
    return this.isListening;
  }

  public getIsSpeaking(): boolean {
    return this.isSpeaking;
  }

  public getLastTranscript(): string {
    return this.lastTranscript;
  }

  public getLastResponse(): string {
    return this.lastResponse;
  }

  public getTurns(): AssistantTurn[] {
    return [...this.turns];
  }

  public getActiveProviderType(): VoiceProviderType {
    return this.activeProviderType;
  }

  public setProvider(type: VoiceProviderType): void {
    this.activeProviderType = type;
    VoiceProviderRegistry.getInstance().setProvider(type);
    this.notify();
  }

  public getExplicitVoiceState(): ExplicitVoiceState {
    if (this.microphoneBlocked) {
      return 'MICROPHONE — BLOCKED';
    }
    if (this.activeProviderType === 'text-only') {
      return 'TEXT MODE — ACTIVE';
    }
    if (this.activeProviderType === 'demo') {
      return 'DEMO VOICE — ACTIVE';
    }
    if (this.activeProviderType === 'gemini-live') {
      const provider = VoiceProviderRegistry.getInstance().getProvider();
      if (provider.getStatus() === 'CONNECTED') {
        return 'GEMINI LIVE — CONNECTED';
      }
      return 'VOICE BACKEND — NOT CONFIGURED';
    }
    if (this.voiceError) {
      return 'VOICE — ERROR';
    }
    return 'BROWSER SPEECH — ACTIVE';
  }

  /**
   * Main Voice/Text command execution pipeline
   */
  public async executeUtterance(rawUtterance: string): Promise<string> {
    const utterance = rawUtterance.trim();
    if (!utterance) return '';

    // 1. Barge-in / stop any ongoing speech
    this.stopSpeaking();

    this.lastTranscript = utterance;
    this.status = 'THINKING';
    this.notify();

    // 2. Add user turn to conversation history
    this.turns.push({
      id: `turn-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      timestamp: Date.now(),
      speaker: 'USER',
      text: utterance,
    });

    if (!this.state) {
      this.status = 'READY';
      this.notify();
      return 'Error: Workstation state not bound.';
    }

    const currentState = this.state;
    const startExecutionTime = Date.now();

    // 3. Structured Intent & Context Resolution
    const parsed = intentParser.parse(utterance, currentState);

    // Handle Ambiguity
    if (parsed.isAmbiguous && parsed.clarificationPrompt) {
      this.status = 'READY';
      this.lastResponse = parsed.clarificationPrompt;
      this.speak(parsed.clarificationPrompt);
      this.turns.push({
        id: `turn-${Date.now()}`,
        timestamp: Date.now(),
        speaker: 'ASSISTANT',
        text: parsed.clarificationPrompt,
        truthState: 'UNRESOLVED',
      });
      this.notify();
      return parsed.clarificationPrompt;
    }

    // Handle Safety Boundary Rejection
    if (parsed.toolId === 'SAFETY_VIOLATION_REJECTED') {
      const msg = `SAFETY BOUNDARY REJECTION: Physical actuator control, PLC setpoints, or DCS commands are strictly prohibited. PLANT-X is an advisory workstation only.`;
      this.status = 'READY';
      this.lastResponse = msg;
      this.speak(msg);
      this.turns.push({
        id: `turn-${Date.now()}`,
        timestamp: Date.now(),
        speaker: 'ASSISTANT',
        text: msg,
        truthState: 'ABSTAINED',
      });
      this.notify();
      return msg;
    }

    // 4. Resolve Tool from Registry
    const tool = TOOL_REGISTRY[parsed.toolId];
    if (!tool) {
      const msg = `Unsupported tool command: '${parsed.toolId}'. Unknown or prohibited action.`;
      this.status = 'READY';
      this.lastResponse = msg;
      this.speak(msg);
      this.notify();
      return msg;
    }

    // 5. Truth Firewall Gate Check
    const firewallCheck = TruthFirewall.validateClaim({
      entityId: currentState.selectedAssetTag,
      property: tool.name,
      value: parsed.parameters,
      truthState: 'INFERRED',
    });

    if (!firewallCheck.approved) {
      const msg = `TRUTH FIREWALL ABSTENTION: ${firewallCheck.abstainReason || 'Escalation rejected by firewall policy'}`;
      this.status = 'READY';
      this.lastResponse = msg;
      this.speak(msg);
      this.turns.push({
        id: `turn-${Date.now()}`,
        timestamp: Date.now(),
        speaker: 'ASSISTANT',
        text: msg,
        truthState: 'ABSTAINED',
      });
      this.notify();
      return msg;
    }

    // 6. Execute Deterministic Tool Runtime
    this.status = 'EXECUTING';
    this.notify();

    let result: any;
    try {
      result = await tool.execute(parsed.parameters, currentState);
    } catch (err: any) {
      result = {
        success: false,
        message: `Execution error: ${err.message || 'Unknown tool failure'}`,
        stateDelta: {},
      };
    }

    const durationMs = Date.now() - startExecutionTime;

    // 7. Audit & Execution Trace Recording
    auditLogger.logAction(
      utterance,
      parsed.toolId,
      parsed.parameters,
      currentState,
      tool.name,
      parsed.parameters,
      result.success ? 'SUCCESS' : 'FAILURE',
      result.message,
      result.stateDelta
    );

    ExecutionTracer.recordTrace({
      traceId: `trace-${Date.now()}`,
      timestamp: Date.now(),
      utterance,
      resolvedIntent: parsed.toolId,
      contextSnapshot: {
        activeView: currentState.activeView,
        selectedAssetTag: currentState.selectedAssetTag,
        scenario: currentState.scenario,
      },
      plannedSteps: [{ tool: tool.name, args: parsed.parameters }],
      executedTools: [
        {
          tool: tool.name,
          args: parsed.parameters,
          status: result.success ? 'SUCCESS' : 'FAILED',
          durationMs,
          resultSummary: result.message,
        },
      ],
      validationChecks: {
        safetyPolicy: 'PERMITTED_READ_OR_SIMULATION',
        capabilitiesChecked: ['FOUL_X', 'GRAPH_TRAVERSAL', 'EQUIPMENT_SIM'],
        truthFirewallApproved: true,
      },
      stateDeltas: result.stateDelta || {},
      totalLatencyMs: durationMs,
    });

    // 8. Commit to Authoritative Workstation State
    if (this.onStateUpdateCallback) {
      this.onStateUpdateCallback((prev) => {
        if (parsed.toolId === 'SCHEDULE_SCENARIO' && result.stateDelta?.timer) {
          timerService.schedule(
            result.stateDelta.timer.totalSeconds,
            result.stateDelta.timer.targetAction,
            result.stateDelta.timer.targetParams,
            prev
          );
        } else if (parsed.toolId === 'CANCEL_SCHEDULED_ACTION') {
          timerService.cancel('Cancelled by user command');
        } else if (parsed.toolId === 'STOP_SPEECH') {
          this.stopSpeaking();
        }

        const next = {
          ...prev,
          ...(result.stateDelta || {}),
          lastTranscript: utterance,
          lastAgentResponse: result.message,
          agentStatus: 'READY' as AgentStatus,
          auditLog: auditLogger.getEntries(),
        };
        this.state = next;
        return next;
      });
    }

    // 9. Update Assistant Turn History & Voice Feedback
    this.status = 'READY';
    this.lastResponse = result.message;
    this.turns.push({
      id: `turn-${Date.now()}`,
      timestamp: Date.now(),
      speaker: 'ASSISTANT',
      text: result.message,
      toolUsed: tool.name,
      truthState: 'DERIVED',
    });

    if (parsed.toolId === 'STOP_SPEECH') {
      this.stopSpeaking();
    } else {
      this.speak(result.message);
    }
    this.notify();
    return result.message;
  }

  /**
   * Spoken audio output with interruption capability
   */
  public speak(text: string): void {
    if (typeof window === 'undefined') return;

    this.stopSpeaking();
    this.isSpeaking = true;
    this.status = 'SPEAKING';
    realtimeAudioController.setTurnState('MODEL_SPEAKING');
    this.notify();

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05;
      utterance.pitch = 0.95;

      utterance.onend = () => {
        this.isSpeaking = false;
        if (this.status === 'SPEAKING') {
          this.status = 'READY';
        }
        realtimeAudioController.setTurnState('IDLE');
        this.notify();
      };

      utterance.onerror = () => {
        this.isSpeaking = false;
        if (this.status === 'SPEAKING') {
          this.status = 'READY';
        }
        realtimeAudioController.setTurnState('IDLE');
        this.notify();
      };

      window.speechSynthesis.speak(utterance);
    } else {
      this.isSpeaking = false;
      this.status = 'READY';
      realtimeAudioController.setTurnState('IDLE');
      this.notify();
    }
  }

  public stopSpeaking(): void {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    realtimeAudioController.stopSpeech();
    realtimeAudioController.setTurnState('IDLE');
    this.isSpeaking = false;
    if (this.status === 'SPEAKING') {
      this.status = 'READY';
    }
    this.notify();
  }

  public async startListening(): Promise<boolean> {
    this.stopSpeaking();

    // 1. If Gemini Live is selected and configured
    if (this.activeProviderType === 'gemini-live') {
      const provider = VoiceProviderRegistry.getInstance().getProvider();
      await provider.connect({
        providerType: 'gemini-live',
        model: 'gemini-3.8-live',
        personality: 'ENGINEER',
        mode: 'TAP_TO_TALK',
        sampleRate: 16000,
      });

      if (provider.getStatus() === 'CONNECTED') {
        this.isListening = true;
        this.status = 'LISTENING';
        this.notify();

        const micStarted = await realtimeAudioController.startMicrophoneCapture();
        if (micStarted) {
          realtimeAudioController.setOnAudioChunk((pcmChunk) => {
            provider.sendAudio(pcmChunk);
          });
          provider.on('transcript', (text, isUser, isFinal) => {
            if (isFinal && isUser) {
              this.stopListening();
              this.executeUtterance(text);
            }
          });
          return true;
        }
      } else {
        // Fallback cleanly to browser speech if backend is unconfigured
        console.warn('Gemini Live backend unavailable. Falling back to Browser Speech Recognition.');
        this.setProvider('browser-speech');
      }
    }

    // 2. Known-Good Path: Browser Speech Recognition (Web Speech API)
    if (typeof window !== 'undefined') {
      const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRec) {
        try {
          if (this.activeRecognition) {
            try { this.activeRecognition.abort(); } catch {}
          }
          const rec = new SpeechRec();
          rec.lang = 'en-US';
          rec.interimResults = false;
          rec.continuous = false;

          rec.onstart = () => {
            this.isListening = true;
            this.microphoneBlocked = false;
            this.voiceError = false;
            this.status = 'LISTENING';
            this.notify();
          };

          rec.onresult = (event: any) => {
            const transcript = event.results[0]?.[0]?.transcript || '';
            this.stopListening();
            if (transcript.trim()) {
              this.executeUtterance(transcript);
            }
          };

          rec.onerror = (err: any) => {
            console.warn('SpeechRecognition error:', err);
            if (err?.error === 'not-allowed' || err?.error === 'service-not-allowed') {
              this.microphoneBlocked = true;
            } else {
              this.voiceError = true;
            }
            this.stopListening();
          };

          rec.onend = () => {
            this.stopListening();
          };

          this.activeRecognition = rec;
          rec.start();

          this.isListening = true;
          this.status = 'LISTENING';
          this.notify();
          return true;
        } catch (err) {
          console.error('SpeechRecognition start failed:', err);
          this.voiceError = true;
          this.stopListening();
          return false;
        }
      }
    }

    this.stopListening();
    return false;
  }

  public stopListening(): void {
    if (this.activeRecognition) {
      try {
        this.activeRecognition.stop();
      } catch {}
      this.activeRecognition = null;
    }
    realtimeAudioController.stopMicrophoneCapture();
    this.isListening = false;
    if (this.status === 'LISTENING') {
      this.status = 'READY';
    }
    this.notify();
  }

  public toggleVoice(): void {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  /**
   * Generates a context snapshot for telemetry & diagnostics
   */
  public getContextSnapshot(): AssistantContextSnapshot {
    return {
      currentView: this.state?.activeView || 'PROCESS',
      selectedEquipment: this.state?.selectedAssetTag || 'E-102',
      selectedStreamId: this.state?.selectedStreamId || 'S-102',
      scenario: this.state?.scenario || 'normal',
      activeHypothesisId: this.state?.activeHypothesisId || 'H1',
      lastCommand: this.lastTranscript,
      lastResponse: this.lastResponse,
      stateVersion: (this.state as any)?.stateVersion ?? 1,
      recentTurns: this.turns.slice(-10),
    };
  }
}

export const voiceAssistantController = VoiceAssistantController.getInstance();
