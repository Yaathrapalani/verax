/**
 * PLANT-X Capability Registry.
 * 
 * Explicitly records supported vs unavailable engineering capabilities.
 * The conversational agent runtime must check this registry before claiming
 * that an operation is possible.
 */

export type PlantCapability =
  | 'FOULING_PREDICTION'
  | 'FOULING_RELIABILITY'
  | 'PROCESS_GRAPH'
  | 'UPSTREAM_TRACE'
  | 'DOWNSTREAM_TRACE'
  | 'HEAT_EXCHANGER_SIMULATION'
  | 'IDEAL_GAS_THERMODYNAMICS'
  | 'SCENARIO_EXECUTION'
  | '3D_PROJECTION'
  | 'EVIDENCE_TRACE'
  | 'PROVENANCE'
  | 'CHEMICAL_STREAMS'
  | 'BLUEPRINT_RECONSTRUCTION'
  | 'PROCEDURAL_3D'
  | 'INVESTIGATION_PLANNER'
  | 'STATE_SNAPSHOTS';

export type UnavailableCapability =
  | 'LIQUID_EOS'
  | 'TWO_PHASE_FLASH'
  | 'TRANSPORT_PROPERTIES'
  | 'PUMP_CURVES'
  | 'VALVE_CV'
  | 'PLC_CONTROL'
  | 'DCS_CONTROL'
  | 'REAL_PLANT_ACTUATION';

export class CapabilityRegistry {
  private static readonly SUPPORTED: Set<PlantCapability> = new Set([
    'FOULING_PREDICTION',
    'FOULING_RELIABILITY',
    'PROCESS_GRAPH',
    'UPSTREAM_TRACE',
    'DOWNSTREAM_TRACE',
    'HEAT_EXCHANGER_SIMULATION',
    'IDEAL_GAS_THERMODYNAMICS',
    'SCENARIO_EXECUTION',
    '3D_PROJECTION',
    'EVIDENCE_TRACE',
    'PROVENANCE',
    'CHEMICAL_STREAMS',
    'BLUEPRINT_RECONSTRUCTION',
    'PROCEDURAL_3D',
    'INVESTIGATION_PLANNER',
    'STATE_SNAPSHOTS',
  ]);

  private static readonly UNAVAILABLE: Record<UnavailableCapability, string> = {
    LIQUID_EOS: 'Real-fluid liquid equation of state is not implemented; Stage 13 is bounded to ideal gas.',
    TWO_PHASE_FLASH: 'Rigorous vapor-liquid equilibrium flash solver is unsupported in current prototype.',
    TRANSPORT_PROPERTIES: 'Viscosity and thermal conductivity transport property models are uncalibrated.',
    PUMP_CURVES: 'Dynamic centrifugal pump head-capacity curves are unavailable.',
    VALVE_CV: 'Non-linear valve Cv hydraulic sizing coefficients are unobserved.',
    PLC_CONTROL: 'Autonomous PLC setpoint actuation is prohibited; decision support only.',
    DCS_CONTROL: 'Distributed control system writing is prohibited; read-only telemetry shadow.',
    REAL_PLANT_ACTUATION: 'Real plant actuation is prohibited by engineering safety constitution.',
  };

  public static isSupported(capability: string): boolean {
    return this.SUPPORTED.has(capability as PlantCapability);
  }

  public static getUnavailableReason(cap: string): string | null {
    if (cap in this.UNAVAILABLE) {
      return this.UNAVAILABLE[cap as UnavailableCapability];
    }
    return null;
  }
}
