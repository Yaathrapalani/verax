/**
 * Gate 10: Interruption & Barge-In Verification
 */

import assert from 'node:assert/strict';
import { voiceAssistantController } from '../src/agent/voice/VoiceAssistantController.ts';
import { RealtimeAudioController } from '../src/agent/voice/RealtimeAudio.ts';
import { TimerService } from '../src/agent/timerService.ts';
import type { PlantWorkstationState } from '../src/agent/types.ts';

if (typeof (global as any).window === 'undefined') {
  (global as any).SpeechSynthesisUtterance = class {
    text: string;
    rate = 1;
    pitch = 1;
    onend: any = null;
    onerror: any = null;
    constructor(text: string) { this.text = text; }
  };
  (global as any).window = {
    speechSynthesis: {
      speak: (_utt: any) => { /* mock */ },
      cancel: () => { /* mock */ },
    },
    SpeechSynthesisUtterance: (global as any).SpeechSynthesisUtterance,
  };
}

async function testGate10Interruption() {
  const baseState: PlantWorkstationState = {
    activeView: 'PROCESS',
    selectedAssetTag: 'E-102',
    selectedStreamId: 'S-102',
    highlightedPath: ['E-102'],
    cameraFocusTag: 'E-102',
    scenario: 'normal',
    timeHr: 63241,
    isPlaying: false,
    foulingThresholdRf: 1.5e-7,
    currentRf: 7.28e-8,
    trustGateStatus: 'PASS',
    activePolicy: 'PREDICTIVE_CLEANING_WINDOW',
    activeStream: {} as any,
    timer: { isActive: true, totalSeconds: 30, remainingSeconds: 30, targetAction: 'RUN_SCENARIO', targetParams: {}, scheduledAtTimestamp: Date.now(), validationContext: { expectedAssetTag: 'E-102', expectedScenario: 'normal' } },
    agentStatus: 'READY',
    lastTranscript: '',
    lastAgentResponse: '',
    isVoiceActive: false,
    isTtsSpeaking: false,
    activeHypotheses: [],
    activeHypothesisId: 'H1',
    investigationRecommendation: '',
    proactiveSuggestions: [],
    auditLog: [],
  };

  voiceAssistantController.registerWorkstation(baseState, () => {});

  // 1. Spoken Operator Interruption (VAD Barge-In)
  const audio = new RealtimeAudioController();
  const timer = new TimerService();
  timer.schedule(30, 'RUN_SCENARIO', {}, baseState);
  assert.equal(timer.isRunning(), true);

  audio.setTurnState('MODEL_SPEAKING');
  assert.equal(audio.getTurnState(), 'MODEL_SPEAKING');

  const tStartBarge = performance.now();
  // Simulate operator speech triggering VAD (2 consecutive frames needed by debounce filter)
  audio.handleIncomingUserAudio(new Float32Array(512).fill(0.08));
  audio.handleIncomingUserAudio(new Float32Array(512).fill(0.08));
  const stopLatencyMs = performance.now() - tStartBarge;

  assert.equal(audio.getTurnState(), 'USER_INTERRUPTED');
  // Background task survives!
  assert.equal(timer.isRunning(), true);
  console.log(`1. VAD Barge-In: Speech stopped in ${stopLatencyMs.toFixed(3)}ms, background timer intact. PASS`);

  // 2. Explicit INTERRUPT control (stopSpeaking)
  voiceAssistantController.speak('This is a very long thermodynamic simulation description of the crude preheat train.');
  assert.equal(voiceAssistantController.getIsSpeaking(), true);

  const tStartManual = performance.now();
  voiceAssistantController.stopSpeaking();
  const manualStopLatencyMs = performance.now() - tStartManual;

  assert.equal(voiceAssistantController.getIsSpeaking(), false);
  // Background task still intact!
  assert.equal(timer.isRunning(), true);
  console.log(`2. Explicit INTERRUPT button: Stopped in ${manualStopLatencyMs.toFixed(3)}ms, timer intact. PASS`);

  timer.cancel();
  audio.dispose();
  console.log('\nGate 10 Interruption: VERIFIED PASS');
}

testGate10Interruption();
