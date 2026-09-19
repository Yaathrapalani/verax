/**
 * Gate 16: Cross-View Synchronization & Geometry Truth Verification
 */

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { TOOL_REGISTRY } from '../src/agent/tools.ts';
import type { PlantWorkstationState } from '../src/agent/types.ts';

async function testGate16Sync() {
  console.log('=== GATE 16: 2D / GRAPH / 3D SYNCHRONIZATION & GEOMETRY TRUTH ===');

  let state: PlantWorkstationState = {
    activeView: 'PROCESS',
    selectedAssetTag: 'E-101',
    selectedStreamId: 'S-101',
    highlightedPath: ['E-101'],
    cameraFocusTag: 'E-101',
    scenario: 'normal',
    timeHr: 63241,
    isPlaying: false,
    foulingThresholdRf: 1.5e-7,
    currentRf: 5.2e-8,
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

  // 1. Select E-102 in workstation
  const navRes = TOOL_REGISTRY['SELECT_EQUIPMENT'].execute({ tag: 'E-102' }, state);
  assert.equal(navRes.success, true);
  state = { ...state, ...navRes.stateDelta };

  assert.equal(state.selectedAssetTag, 'E-102', 'P&ID / canonical selection must be E-102');
  assert.equal(state.cameraFocusTag, 'E-102', '3D focus must be synchronized to E-102');
  console.log('1. Selection of E-102 across P&ID, Graph, 3D synchronized: PASS');

  // Frame in 3D
  const frameRes = TOOL_REGISTRY['FOCUS_3D_OBJECT'].execute({ tag: 'E-102' }, state);
  assert.equal(frameRes.success, true);
  state = { ...state, ...frameRes.stateDelta };
  assert.equal(state.activeView, '3D');
  assert.equal(state.cameraFocusTag, 'E-102');
  console.log('2. 3D View projection and camera framing synchronized: PASS');

  // 2. Select another asset (E-103) - Verify stale selection does not survive
  const switchRes = TOOL_REGISTRY['SELECT_EQUIPMENT'].execute({ tag: 'E-103' }, state);
  assert.equal(switchRes.success, true);
  state = { ...state, ...switchRes.stateDelta };

  assert.equal(state.selectedAssetTag, 'E-103', 'Canonical selection updated to E-103');
  assert.notEqual(state.selectedAssetTag, 'E-102', 'Stale selection E-102 must not survive');
  assert.equal(state.cameraFocusTag, 'E-103', 'Camera focus updated to E-103');
  assert.notEqual(state.cameraFocusTag, 'E-102', 'Stale 3D focus E-102 must not survive');
  console.log('3. Asset switch to E-103 completely purges stale selection: PASS');

  // 3. Verify Geometry Truth Disclaimers in 3D scene code
  const sceneFile = readFileSync(join(process.cwd(), 'src/components/scene/PlantScene3D.tsx'), 'utf-8');
  assert.ok(
    sceneFile.includes('Representative Inferred Geometry — Not As-Built CAD'),
    'Explicit disclaimer "Representative Inferred Geometry — Not As-Built CAD" must be present'
  );
  assert.ok(
    sceneFile.includes('CAD SOURCE: <span className="text-rose-400 font-semibold">UNAVAILABLE</span>'),
    'CAD source must be marked UNAVAILABLE'
  );
  console.log('4. Truth Firewall & Geometry Provenance Banner verified in 3D component: PASS');

  console.log('Gate 16 Cross-View Synchronization: VERIFIED PASS\n');
}

testGate16Sync().catch(err => {
  console.error('Gate 16 Failed:', err);
  process.exit(1);
});
