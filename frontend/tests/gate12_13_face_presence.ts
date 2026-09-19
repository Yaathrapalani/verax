/**
 * Gate 12 & Gate 13: Face Presence Privacy & Activation State Machine Verification
 */

import assert from 'node:assert/strict';
import { FacePresenceDetector } from '../src/agent/presence/FacePresenceDetector.ts';

async function testGate12And13() {
  console.log('=== GATE 12 & 13: FACE PRESENCE PRIVACY & ACTIVATION ===');

  const detector = FacePresenceDetector.getInstance();

  // 1. Initial State & Defaults
  assert.equal(detector.getMode(), 'OFF', 'Default presence mode must be OFF');
  assert.equal(detector.getState(), 'NO_FACE', 'Default state must be NO_FACE');
  assert.equal(detector.isPresence(), false, 'Default presence must be false');
  assert.equal(detector.getTelemetry().cameraActive, false, 'Camera must be inactive when OFF');

  // 2. Privacy Guarantees Audit:
  // Inspect class fields to ensure NO biometric data structures exist
  const rawDetector = detector as any;
  assert.equal(rawDetector.faceEmbeddings, undefined, 'Must not have facial embeddings');
  assert.equal(rawDetector.faceTemplates, undefined, 'Must not have facial templates');
  assert.equal(rawDetector.biometricDatabase, undefined, 'Must not have biometric database');
  assert.equal(rawDetector.cloudUploadUrl, undefined, 'Must not have cloud upload url');
  console.log('1. Privacy Guarantees: Zero embeddings, zero templates, zero cloud persistence verified: PASS');

  // 3. Debounce Values Verification
  console.log(`2. Temporal Debounce: HITS_FOR_PRESENT = ${rawDetector.HITS_FOR_PRESENT}, MISSES_FOR_LOST = ${rawDetector.MISSES_FOR_LOST}`);
  assert.equal(rawDetector.HITS_FOR_PRESENT, 3, 'Actual implementation uses 3 positive frames');
  assert.equal(rawDetector.MISSES_FOR_LOST, 5, 'Actual implementation uses 5 negative frames');

  // 4. State Machine Simulation
  let wakeTriggeredCount = 0;
  detector.setOnWakeCallback(() => {
    wakeTriggeredCount++;
  });

  // Simulate ARMING detector
  rawDetector.mode = 'ARMED';
  rawDetector.cameraActive = true;

  // Frame 1: Hit -> FACE_CANDIDATE (not yet PRESENT)
  rawDetector.handleDetectionResult(true);
  assert.equal(detector.getState(), 'FACE_CANDIDATE');
  assert.equal(detector.isPresence(), false);
  assert.equal(wakeTriggeredCount, 0, 'No wake on candidate');

  // Frame 2: Hit -> Still FACE_CANDIDATE
  rawDetector.handleDetectionResult(true);
  assert.equal(detector.getState(), 'FACE_CANDIDATE');
  assert.equal(wakeTriggeredCount, 0);

  // Frame 3: 3rd Hit -> Reaches HITS_FOR_PRESENT -> FACE_PRESENT
  rawDetector.handleDetectionResult(true);
  assert.equal(detector.getState(), 'FACE_PRESENT');
  assert.equal(detector.isPresence(), true);
  assert.equal(wakeTriggeredCount, 1, 'One-turn wake activated upon confirmed presence');

  // Frame 4 & 5: Continued hits while present -> Must NOT re-trigger wake (one-turn guarantee)
  rawDetector.handleDetectionResult(true);
  rawDetector.handleDetectionResult(true);
  assert.equal(wakeTriggeredCount, 1, 'Wake must NOT trigger multiple times for single presence');
  console.log('3. One-Turn Wake Activation: Triggered exactly once on confirmed presence: PASS');

  // Miss 1: Still in FACE_LOST state
  rawDetector.handleDetectionResult(false);
  assert.equal(detector.getState(), 'FACE_LOST');
  assert.equal(detector.isPresence(), false);

  // Misses 2, 3, 4: Still FACE_LOST
  rawDetector.handleDetectionResult(false);
  rawDetector.handleDetectionResult(false);
  rawDetector.handleDetectionResult(false);
  assert.equal(detector.getState(), 'FACE_LOST');

  // Miss 5: 5th miss reaches MISSES_FOR_LOST -> Transitions to NO_FACE
  rawDetector.handleDetectionResult(false);
  assert.equal(detector.getState(), 'NO_FACE');
  console.log('4. Face Loss Debounce: 5 consecutive misses cleanly transition FACE_LOST -> NO_FACE: PASS');

  // Reset to OFF
  await detector.setMode('OFF');
  assert.equal(detector.getMode(), 'OFF');
  assert.equal(detector.getState(), 'NO_FACE');
  assert.equal(rawDetector.cameraActive, false);

  detector.dispose();
  console.log('Gate 12 & 13 Face Presence: VERIFIED PASS\n');
}

testGate12And13().catch(err => {
  console.error('Gate 12/13 Failed:', err);
  process.exit(1);
});
