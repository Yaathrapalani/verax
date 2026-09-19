/**
 * PLANT-X Engineering Truth Firewall.
 * 
 * Enforces strict scientific boundaries on conversational output.
 * Prevents unauthorized upgrades of truth states (e.g. INFERRED -> OBSERVED,
 * SIMULATED -> OBSERVED, REPRESENTATIVE -> REAL, UNAVAILABLE -> AVAILABLE).
 * If a claim cannot be verified against canonical state or evidence, forces ABSTAIN.
 */

import type { TruthState } from '../types';

export interface EngineeringClaim {
  entityId: string;
  property: string;
  value: unknown;
  truthState: TruthState;
  sourceDoc?: string;
  provenanceMethod?: string;
}

export class TruthFirewall {
  private static readonly VALID_TRUTH_STATES: Set<TruthState> = new Set([
    'OBSERVED',
    'DERIVED',
    'INFERRED',
    'ASSUMED',
    'REPRESENTATIVE',
    'SIMULATED',
    'UNRESOLVED',
    'UNAVAILABLE',
  ]);

  /**
   * Validates claim and prevents silent truth state escalation.
   */
  public static validateClaim(claim: EngineeringClaim, originalState?: TruthState): {
    approved: boolean;
    assignedState: TruthState;
    abstainReason?: string;
  } {
    if (!this.VALID_TRUTH_STATES.has(claim.truthState)) {
      return {
        approved: false,
        assignedState: 'UNRESOLVED',
        abstainReason: `Invalid truth state '${claim.truthState}' rejected by firewall.`,
      };
    }

    if (originalState) {
      // Escalation rules: Cannot upgrade simulated/inferred/unavailable to observed
      if (
        (originalState === 'SIMULATED' || originalState === 'INFERRED' || originalState === 'UNAVAILABLE' || originalState === 'REPRESENTATIVE') &&
        claim.truthState === 'OBSERVED'
      ) {
        return {
          approved: false,
          assignedState: originalState,
          abstainReason: `Truth Firewall Violation: Attempted to upgrade ${originalState} property '${claim.property}' to OBSERVED.`,
        };
      }
    }

    // Explicitly unmanufactured physical properties must remain UNAVAILABLE
    const unmanufacturedProps = ['liquid_viscosity', 'liquid_thermal_conductivity', 'two_phase_flash_equilibrium', 'differential_pressure'];
    if (unmanufacturedProps.includes(claim.property.toLowerCase()) && claim.value !== null && claim.value !== undefined && claim.truthState === 'OBSERVED') {
      return {
        approved: false,
        assignedState: 'UNAVAILABLE',
        abstainReason: `Property '${claim.property}' is unmeasured in current evidence set; cannot be presented as OBSERVED.`,
      };
    }

    return {
      approved: true,
      assignedState: claim.truthState,
    };
  }

  /**
   * Generates a scientifically honest explanation when property is unavailable or gate abstains.
   */
  public static formatTruthBoundaryExplanation(property: string, entityId: string, truthState: TruthState): string {
    switch (truthState) {
      case 'UNAVAILABLE':
        return `No validated measurement for ${property} on ${entityId} exists in the active evidence set. Value is UNAVAILABLE.`;
      case 'SIMULATED':
        return `The reported ${property} on ${entityId} is a SIMULATED value from the Stage 14 runtime, not an observed plant measurement.`;
      case 'REPRESENTATIVE':
        return `Spatial layout and geometry for ${entityId} are REPRESENTATIVE process topology, not measured plant CAD.`;
      case 'INFERRED':
        return `The ${property} on ${entityId} is INFERRED via heuristic bounds; hydraulic causality cannot be confirmed.`;
      default:
        return `Truth state for ${property} on ${entityId}: ${truthState}.`;
    }
  }
}
