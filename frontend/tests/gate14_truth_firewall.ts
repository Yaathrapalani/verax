/**
 * Gate 14: Truth Firewall Verification
 * 
 * Verifies strict rejection of unauthorized truth-state escalations:
 * - INFERRED -> OBSERVED: BLOCKED
 * - SIMULATED -> OBSERVED: BLOCKED
 * - UNAVAILABLE -> OBSERVED: BLOCKED
 * - REPRESENTATIVE -> AS-BUILT CAD / OBSERVED: BLOCKED
 * - Unmeasured properties (viscosity, delta-P, two-phase equilibrium): BLOCKED
 */

import assert from 'node:assert/strict';
import { TruthFirewall } from '../src/agent/runtime/truthFirewall.ts';

async function testGate14TruthFirewall() {
  console.log('=== GATE 14: TRUTH FIREWALL VERIFICATION ===');

  // 1. INFERRED -> OBSERVED
  const inferredEscalation = TruthFirewall.validateClaim(
    { entityId: 'E-102', property: 'fouling_resistance_Rf', value: 7.28e-8, truthState: 'OBSERVED' },
    'INFERRED'
  );
  assert.equal(inferredEscalation.approved, false, 'INFERRED -> OBSERVED escalation must be BLOCKED');
  assert.equal(inferredEscalation.assignedState, 'INFERRED');
  console.log('1. INFERRED -> OBSERVED: BLOCKED (PASS)');

  // 2. SIMULATED -> OBSERVED
  const simulatedEscalation = TruthFirewall.validateClaim(
    { entityId: 'E-102', property: 'outlet_temperature', value: 432.5, truthState: 'OBSERVED' },
    'SIMULATED'
  );
  assert.equal(simulatedEscalation.approved, false, 'SIMULATED -> OBSERVED escalation must be BLOCKED');
  assert.equal(simulatedEscalation.assignedState, 'SIMULATED');
  console.log('2. SIMULATED -> OBSERVED: BLOCKED (PASS)');

  // 3. UNAVAILABLE -> OBSERVED
  const unavailableEscalation = TruthFirewall.validateClaim(
    { entityId: 'E-102', property: 'differential_pressure', value: 45.2, truthState: 'OBSERVED' },
    'UNAVAILABLE'
  );
  assert.equal(unavailableEscalation.approved, false, 'UNAVAILABLE -> OBSERVED escalation must be BLOCKED');
  assert.equal(unavailableEscalation.assignedState, 'UNAVAILABLE');
  console.log('3. UNAVAILABLE -> OBSERVED: BLOCKED (PASS)');

  // 4. REPRESENTATIVE -> AS-BUILT CAD / OBSERVED
  const repEscalation = TruthFirewall.validateClaim(
    { entityId: 'E-102', property: 'cad_geometry_mesh', value: 'as_built_mesh.step', truthState: 'OBSERVED' },
    'REPRESENTATIVE'
  );
  assert.equal(repEscalation.approved, false, 'REPRESENTATIVE -> AS-BUILT CAD / OBSERVED must be BLOCKED');
  assert.equal(repEscalation.assignedState, 'REPRESENTATIVE');
  console.log('4. REPRESENTATIVE -> AS-BUILT CAD: BLOCKED (PASS)');

  // 5. Unmeasured properties (differential_pressure, liquid_viscosity) without prior state
  const fakeViscosity = TruthFirewall.validateClaim({
    entityId: 'E-102',
    property: 'liquid_viscosity',
    value: 0.0035,
    truthState: 'OBSERVED',
  });
  assert.equal(fakeViscosity.approved, false, 'Fabricated liquid_viscosity as OBSERVED must be BLOCKED');
  assert.equal(fakeViscosity.assignedState, 'UNAVAILABLE');
  console.log('5a. Fake liquid_viscosity as OBSERVED: BLOCKED (PASS)');

  const fakeDeltaP = TruthFirewall.validateClaim({
    entityId: 'E-102',
    property: 'differential_pressure',
    value: 82.1,
    truthState: 'OBSERVED',
  });
  assert.equal(fakeDeltaP.approved, false, 'Fabricated differential_pressure as OBSERVED must be BLOCKED');
  assert.equal(fakeDeltaP.assignedState, 'UNAVAILABLE');
  console.log('5b. Fake differential_pressure as OBSERVED: BLOCKED (PASS)');

  // 6. Valid non-escalated claims should pass
  const validInferred = TruthFirewall.validateClaim(
    { entityId: 'E-102', property: 'fouling_resistance_Rf', value: 7.28e-8, truthState: 'INFERRED' },
    'INFERRED'
  );
  assert.equal(validInferred.approved, true, 'Consistent INFERRED claim should be APPROVED');

  const validSimulated = TruthFirewall.validateClaim(
    { entityId: 'E-102', property: 'outlet_temp', value: 432.5, truthState: 'SIMULATED' },
    'SIMULATED'
  );
  assert.equal(validSimulated.approved, true, 'Consistent SIMULATED claim should be APPROVED');

  console.log('Gate 14 Truth Firewall: ALL ESCALATION ATTEMPTS REJECTED (VERIFIED PASS)\n');
}

testGate14TruthFirewall().catch(err => {
  console.error('Gate 14 Failed:', err);
  process.exit(1);
});
