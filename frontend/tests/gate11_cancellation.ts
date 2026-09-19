/**
 * Gate 11: Cancellation Semantics Reconciliation
 * 
 * Verifies strict distinction between:
 * 1. "Cancel." -> CANCEL_SCHEDULED_ACTION (cancels pending task/timer)
 * 2. "Stop speaking." -> STOP_SPEECH (stops audio playback, preserves pending task/timer)
 */

import assert from 'node:assert/strict';
import { voiceAssistantController } from '../src/agent/voice/VoiceAssistantController.ts';
import { timerService } from '../src/agent/timerService.ts';
import { intentParser } from '../src/agent/intentParser.ts';
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
      speak: (_utt: any) => {},
      cancel: () => {},
    },
    SpeechSynthesisUtterance: (global as any).SpeechSynthesisUtterance,
  };
}

async function testGate11Cancellation() {
  console.log('=== GATE 11: CANCELLATION SEMANTICS ===');

  let workstationState: PlantWorkstationState = {
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
    timer: { isActive: false, totalSeconds: 0, remainingSeconds: 0, targetAction: '', targetParams: {}, scheduledAtTimestamp: 0 },
    agentStatus: 'READY',
    lastTranscript: '',
    lastAgentResponse: '',
    isVoiceActive: false,
    proactiveSuggestions: [],
    auditLog: [],
  };

  voiceAssistantController.registerWorkstation(workstationState, (updater) => {
    workstationState = updater(workstationState);
  });

  // Intent parsing check: ensure no ambiguity
  const parsedCancel = intentParser.parse('Cancel.', workstationState);
  assert.equal(parsedCancel.toolId, 'CANCEL_SCHEDULED_ACTION');

  const parsedStopSpeech = intentParser.parse('Stop speaking.', workstationState);
  assert.equal(parsedStopSpeech.toolId, 'STOP_SPEECH');
  assert.notEqual(parsedCancel.toolId, parsedStopSpeech.toolId, 'Commands must NOT map to same tool');

  // Part 1: Start delayed scenario execution
  timerService.schedule(30, 'RUN_SCENARIO', { scenarioName: 'rapid_fouling' }, workstationState);
  workstationState.timer.isActive = true;
  assert.equal(timerService.isRunning(), true, 'Timer should be active before Cancel');

  // Say: "Cancel."
  await voiceAssistantController.executeUtterance('Cancel.');
  assert.equal(timerService.isRunning(), false, 'Scheduled action must be cancelled');
  console.log('1. "Cancel." -> Scheduled action cancelled: PASS');

  // Part 2: Start delayed scenario again, start speech, then say "Stop speaking."
  timerService.schedule(45, 'RUN_SCENARIO', { scenarioName: 'rapid_fouling' }, workstationState);
  workstationState.timer.isActive = true;
  assert.equal(timerService.isRunning(), true, 'Timer should be running before speech test');

  voiceAssistantController.speak('Reviewing fouling prognosis across feed preheat train units.');
  assert.equal(voiceAssistantController.getIsSpeaking(), true, 'Assistant should be speaking');

  // Say: "Stop speaking."
  await voiceAssistantController.executeUtterance('Stop speaking.');

  // Verify only speech stops; scheduled action survives!
  assert.equal(voiceAssistantController.getIsSpeaking(), false, 'Speech playback must stop');
  assert.equal(timerService.isRunning(), true, 'Scheduled action MUST NOT be cancelled by "Stop speaking"');
  console.log('2. "Stop speaking." -> Speech stopped, scheduled action survived: PASS');

  timerService.cancel('Test completed');
  console.log('Gate 11 Cancellation Semantics: VERIFIED PASS\n');
}

testGate11Cancellation().catch(err => {
  console.error('Gate 11 Failed:', err);
  process.exit(1);
});
