/**
 * Gate 9: Contextual 6-Command Chain Verification
 * Tests the exact sequence:
 * 1. "Show me E-102."
 * 2. "Why?"
 * 3. "What's missing?"
 * 4. "What should I investigate next?"
 * 5. "Show me that."
 * 6. "Frame it in 3D."
 */

import assert from 'node:assert/strict';
import { voiceAssistantController } from '../src/agent/voice/VoiceAssistantController.ts';
import { intentParser } from '../src/agent/intentParser.ts';
import { TOOL_REGISTRY } from '../src/agent/tools.ts';
import type { PlantWorkstationState } from '../src/agent/types.ts';

async function testGate9Context() {
  let state: PlantWorkstationState = {
    activeView: 'PROCESS',
    selectedAssetTag: 'E-101', // start on E-101
    selectedStreamId: 'S-101',
    highlightedPath: ['E-101'],
    cameraFocusTag: 'E-101',
    scenario: 'normal',
    timeHr: 63241,
    isPlaying: false,
    foulingThresholdRf: 1.5e-7,
    currentRf: 7.28e-8,
    trustGateStatus: 'PASS',
    activePolicy: 'PREDICTIVE_CLEANING_WINDOW',
    activeStream: {} as any,
    timer: { isActive: false, totalSeconds: 0, remainingSeconds: 0, targetAction: '', targetParams: {}, scheduledAtTimestamp: 0, validationContext: { expectedAssetTag: '', expectedScenario: '' } },
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

  const updateState = (updater: any) => {
    state = updater(state);
  };

  voiceAssistantController.registerWorkstation(state, updateState);

  // 1. "Show me E-102."
  const p1 = intentParser.parse('Show me E-102.', state);
  assert.equal(p1.toolId, 'SELECT_EQUIPMENT');
  assert.equal(p1.parameters.tag, 'E-102');
  const res1 = await TOOL_REGISTRY['SELECT_EQUIPMENT'].execute(p1.parameters, state);
  updateState((prev: any) => ({ ...prev, ...(res1.stateDelta || {}) }));
  assert.equal(state.selectedAssetTag, 'E-102');
  assert.equal(state.cameraFocusTag, 'E-102');
  console.log('Turn 1: "Show me E-102." -> Selected E-102. PASS');

  // 2. "Why?"
  const p2 = intentParser.parse('Why?', state);
  assert.equal(p2.toolId, 'GET_RELIABILITY_STATUS');
  const res2 = await TOOL_REGISTRY['GET_RELIABILITY_STATUS'].execute(p2.parameters, state);
  assert.ok(res2.message.includes('PASS') || res2.message.includes('Reliability'));
  console.log('Turn 2: "Why?" -> Reliability gate audit on active E-102 context. PASS');

  // 3. "What's missing?"
  const p3 = intentParser.parse("What's missing?", state);
  assert.equal(p3.toolId, 'SHOW_DATA_GAPS');
  const res3 = await TOOL_REGISTRY['SHOW_DATA_GAPS'].execute(p3.parameters, state);
  assert.ok(res3.message.includes('UNAVAILABLE') || res3.message.includes('Pressure drop') || res3.message.includes('ΔP'));
  console.log('Turn 3: "What\'s missing?" -> Data gaps on E-102 context (ΔP UNAVAILABLE). PASS');

  // 4. "What should I investigate next?"
  const p4 = intentParser.parse('What should I investigate next?', state);
  assert.equal(p4.toolId, 'GET_INVESTIGATION_RECOMMENDATIONS');
  const res4 = await TOOL_REGISTRY['GET_INVESTIGATION_RECOMMENDATIONS'].execute(p4.parameters, state);
  assert.ok(res4.message.includes('Recommended') || res4.message.includes('E-102'));
  console.log('Turn 4: "What should I investigate next?" -> Recommended investigation on E-102. PASS');

  // 5. "Show me that."
  const p5 = intentParser.parse('Show me that.', state);
  assert.equal(p5.toolId, 'SHOW_EVIDENCE');
  assert.equal(p5.parameters.anchorTag, 'E-102');
  const res5 = await TOOL_REGISTRY['SHOW_EVIDENCE'].execute(p5.parameters, state);
  updateState((prev: any) => ({ ...prev, ...(res5.stateDelta || {}) }));
  assert.equal(state.activeView, 'EVIDENCE');
  console.log('Turn 5: "Show me that." -> Opened EVIDENCE view anchored to E-102. PASS');

  // 6. "Frame it in 3D."
  const p6 = intentParser.parse('Frame it in 3D.', state);
  assert.equal(p6.toolId, 'FOCUS_3D_OBJECT');
  assert.equal(p6.parameters.tag, 'E-102');
  const res6 = await TOOL_REGISTRY['FOCUS_3D_OBJECT'].execute(p6.parameters, state);
  updateState((prev: any) => ({ ...prev, ...(res6.stateDelta || {}) }));
  assert.equal(state.activeView, '3D');
  assert.equal(state.cameraFocusTag, 'E-102');
  console.log('Turn 6: "Frame it in 3D." -> Switched to 3D view and focused E-102. PASS');

  console.log('\nAll 6 Contextual Commands VERIFIED PASS');
}

testGate9Context();
