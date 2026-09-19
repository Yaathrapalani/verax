/**
 * PLANT-X F1 Typed API Client Interfaces & State Containers
 */

export type ApiStatus = 'LOADING' | 'SUCCESS' | 'ERROR' | 'UNAVAILABLE';

export interface ApiState<T> {
  status: ApiStatus;
  data: T | null;
  error: string | null;
  timestamp: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  artifacts_loaded: boolean;
  configuration_loaded: boolean;
  core_ready: boolean;
  plant_connectivity: string;
  representation: string;
  dataset_checksum: string;
  timestamp_range: {
    min_time_hr: number;
    max_time_hr: number;
  };
}

export interface ReplayManifestResponse {
  dataset_checksum: string;
  min_timestamp: number;
  max_timestamp: number;
  total_records: number;
  exchangers: string[];
}

export interface PhysicsStateDTO {
  timestamp: number;
  exchanger_id: string;
  thermal: {
    q_tube: number;
    q_shell: number;
    thermal_balance_error: number;
    delta_t_1: number;
    delta_t_2: number;
    lmtd: number;
    ua: number;
    ua_clean_reference: number;
  };
  fouling: {
    rf_derived: number;
    rf_relative_to_reference: number;
  };
  data_quality: {
    valid_input_count: number;
    invalid_input_count: number;
    primary_status: string;
    reasons: string[];
  };
  availability: {
    pressure_available: boolean;
    delta_p_available: boolean;
    cleaning_event_available: boolean;
  };
  provenance: {
    source_variables: string[];
    state_schema_version: string;
    calculation_version: string;
  };
}

export interface ReliabilityStateDTO {
  timestamp: number;
  exchanger_id: string;
  status: 'PASS' | 'ABSTAIN';
  checks: Array<{
    check_name: string;
    status: 'PASS' | 'FAIL' | 'WARN';
    reason_code: string | null;
    evidence: Record<string, any>;
  }>;
  reason_codes: string[];
  evidence: Record<string, any>;
}

export interface DecisionStateDTO {
  timestamp: number;
  exchanger_id: string;
  decision: string;
  reliability_status: string;
  current_rf_derived: number;
  forecast_horizon_hours: number;
  threshold_rf: number;
  threshold_crossing: boolean;
  reason_codes: string[];
  provenance: {
    human_approval_required: boolean;
    [key: string]: any;
  };
}

export interface ReplaySnapshotDTO {
  timestamp: number;
  exchanger_id: string;
  scenario_mode: 'NORMAL' | 'SHIFTED';
  telemetry: Record<string, number>;
  physics_state: PhysicsStateDTO;
  forecast_state: Array<{
    exchanger_id: string;
    timestamp: number;
    horizon_hours: number;
    prediction: number;
    method: string;
  }>;
  reliability_state: ReliabilityStateDTO;
  decision_state: DecisionStateDTO;
  evidence_reference: Record<string, any>;
  provenance: {
    dataset_checksum: string;
    no_future_leakage: boolean;
    [key: string]: any;
  };
}
