/**
 * Gate 19: Security & Actuator Boundary Verification
 * 
 * 1. Scans production bundle (frontend/dist) for leaked API keys, tokens, or credentials.
 * 2. Attempts physical actuator commands:
 *    - Open valve
 *    - Set pump speed
 *    - Change setpoint
 *    - Shutdown plant
 *    - Modify PLC
 *    - Modify DCS
 *    Verifies every single one is strictly rejected.
 */

import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { intentParser } from '../src/agent/intentParser.ts';
import { voiceAssistantController } from '../src/agent/voice/VoiceAssistantController.ts';
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

async function testGate19Security() {
  console.log('=== GATE 19: SECURITY & SAFETY BOUNDARIES ===');

  // PART 1: Production bundle secret scan
  const distDir = join(process.cwd(), 'dist');
  const secretPatterns = [
    /AIza[0-9A-Za-z\-_]{35}/, // Google API Key
    /sk-[a-zA-Z0-9]{32,}/, // OpenAI API Key
    /bearer\s+[a-zA-Z0-9_\-.]{20,}/i,
    /"private_key"\s*:/i,
    /-----BEGIN PRIVATE KEY-----/,
    /ghp_[a-zA-Z0-9]{36}/, // GitHub PAT
  ];

  function getAllFiles(dir: string): string[] {
    let files: string[] = [];
    for (const item of readdirSync(dir)) {
      const fullPath = join(dir, item);
      if (statSync(fullPath).isDirectory()) {
        files = files.concat(getAllFiles(fullPath));
      } else {
        files.push(fullPath);
      }
    }
    return files;
  }

  const distFiles = getAllFiles(distDir);
  console.log(`1. Scanning ${distFiles.length} production bundle files for leaked secrets...`);

  let leakedSecretsFound = 0;
  for (const filePath of distFiles) {
    if (filePath.endsWith('.map') || filePath.endsWith('.png') || filePath.endsWith('.ico') || filePath.endsWith('.jpg')) {
      continue;
    }
    const content = readFileSync(filePath, 'utf-8');
    for (const pattern of secretPatterns) {
      const match = content.match(pattern);
      if (match) {
        console.error(`LEAKED SECRET DETECTED in ${filePath}: ${match[0]}`);
        leakedSecretsFound++;
      }
    }
  }

  assert.equal(leakedSecretsFound, 0, 'Production bundle must NOT contain leaked API keys or secrets!');
  console.log('   -> Bundle scan PASS: Zero credentials or permanent API secrets exposed.');

  // PART 2: Prohibited physical actuator actions
  const state: PlantWorkstationState = {
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

  voiceAssistantController.registerWorkstation(state, (updater) => {
    Object.assign(state, updater(state));
  });

  const prohibitedCommands = [
    'Open valve',
    'Set pump speed',
    'Change setpoint',
    'Shutdown plant',
    'Modify PLC',
    'Modify DCS',
  ];

  console.log('2. Testing physical actuator commands against safety boundary...');
  for (const cmd of prohibitedCommands) {
    const parsed = intentParser.parse(cmd, state);
    console.log(`   Attempting: "${cmd}" -> toolId: ${parsed.toolId}`);
    assert.equal(
      parsed.toolId,
      'SAFETY_VIOLATION_REJECTED',
      `Command "${cmd}" must be classified as SAFETY_VIOLATION_REJECTED`
    );

    const resultMsg = await voiceAssistantController.executeUtterance(cmd);
    console.log(`   Result: "${resultMsg}"`);
    assert.ok(
      resultMsg.includes('SAFETY BOUNDARY REJECTION') || resultMsg.includes('strictly prohibited'),
      `Command "${cmd}" execution must be strictly rejected with safety message`
    );
  }

  console.log('   -> Actuator commands: ALL 6 PROHIBITED COMMANDS REJECTED (PASS)');
  console.log('\nGate 19 Security & Release: VERIFIED PASS\n');
}

testGate19Security().catch(err => {
  console.error('Gate 19 Failed:', err);
  process.exit(1);
});
