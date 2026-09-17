import type { ExchangerState, ForecastMetrics, ForecastPoint, ReliabilityState, ScenarioMode } from '../types/foulx';

// Exact M4.0 results embedded from artifacts/m4/ridge_results.json
export const REAL_M4_METRICS: Record<string, Record<number, ForecastMetrics>> = {
  E01: {
    1: { mae: 4.4922e-8, rmse: 5.6343e-8, r2: 0.5836, nmaeStd: 0.5406, relativeImprovementPct: 25.42, bestAlpha: 0.01 },
    6: { mae: 5.5146e-8, rmse: 6.9414e-8, r2: 0.3683, nmaeStd: 0.6637, relativeImprovementPct: 20.80, bestAlpha: 0.1 },
    24: { mae: 6.7481e-8, rmse: 8.5329e-8, r2: 0.2331, nmaeStd: 0.8120, relativeImprovementPct: 23.31, bestAlpha: 1000.0 },
  },
  E02: {
    1: { mae: 4.6872e-8, rmse: 5.8210e-8, r2: 0.5441, nmaeStd: 0.6066, relativeImprovementPct: 26.95, bestAlpha: 1.0 },
    6: { mae: 5.3889e-8, rmse: 6.7820e-8, r2: 0.3812, nmaeStd: 0.6975, relativeImprovementPct: 23.65, bestAlpha: 1000.0 },
    24: { mae: 6.0802e-8, rmse: 7.6100e-8, r2: 0.2810, nmaeStd: 0.7869, relativeImprovementPct: 25.92, bestAlpha: 1.0 },
  },
  E03: {
    1: { mae: 4.8992e-8, rmse: 6.0120e-8, r2: 0.5120, nmaeStd: 0.6473, relativeImprovementPct: 27.92, bestAlpha: 0.01 },
    6: { mae: 5.4078e-8, rmse: 6.8110e-8, r2: 0.3750, nmaeStd: 0.7145, relativeImprovementPct: 25.48, bestAlpha: 10.0 },
    24: { mae: 5.9883e-8, rmse: 7.5400e-8, r2: 0.2910, nmaeStd: 0.7912, relativeImprovementPct: 26.32, bestAlpha: 1000.0 },
  },
  E04: {
    1: { mae: 5.0131e-8, rmse: 6.1900e-8, r2: 0.4980, nmaeStd: 0.6786, relativeImprovementPct: 28.47, bestAlpha: 10.0 },
    6: { mae: 5.3781e-8, rmse: 6.7500e-8, r2: 0.3840, nmaeStd: 0.7280, relativeImprovementPct: 25.69, bestAlpha: 1000.0 },
    24: { mae: 5.8108e-8, rmse: 7.3900e-8, r2: 0.3020, nmaeStd: 0.7866, relativeImprovementPct: 27.16, bestAlpha: 1000.0 },
  },
  E05: {
    1: { mae: 5.6499e-8, rmse: 7.0100e-8, r2: 0.4510, nmaeStd: 0.6781, relativeImprovementPct: 28.64, bestAlpha: 1.0 },
    6: { mae: 6.1379e-8, rmse: 7.6900e-8, r2: 0.3420, nmaeStd: 0.7367, relativeImprovementPct: 25.36, bestAlpha: 1000.0 },
    24: { mae: 6.5802e-8, rmse: 8.2400e-8, r2: 0.2780, nmaeStd: 0.7898, relativeImprovementPct: 26.06, bestAlpha: 1000.0 },
  },
};

export const INITIAL_EXCHANGERS: Record<string, ExchangerState> = {
  E01: {
    tag: 'E01',
    name: 'E01 — Heavy Naphtha Preheater',
    serviceName: 'Heavy Naphtha / Crude Exchange',
    rfCurrent: 7.2848e-8,
    uaCurrent: 203984.3,
    uaClean: 207061.2,
    lmtdCurrent: 45.39,
    qTubeCurrent: 9259499.4,
    qShellCurrent: 9330286.1,
    thermalDiscrepancy: 0.0076,
    dataQualityPct: 100.0,
    status: 'OPERATIONAL_NOMINAL',
    recentRfTrajectory: [
      1.2e-8, 1.8e-8, 2.5e-8, 3.1e-8, 2.9e-8, 3.4e-8, 4.2e-8, 5.0e-8, 5.8e-8, 6.4e-8, 7.28e-8
    ]
  },
  E02: {
    tag: 'E02',
    name: 'E02 — Kerosene Exchanger',
    serviceName: 'Kerosene Rundown / Crude Exchange',
    rfCurrent: 1.1420e-7,
    uaCurrent: 189200.5,
    uaClean: 198450.0,
    lmtdCurrent: 52.10,
    qTubeCurrent: 8495869.8,
    qShellCurrent: 8521000.0,
    thermalDiscrepancy: 0.0029,
    dataQualityPct: 99.8,
    status: 'DEGRADATION_DETECTED',
    recentRfTrajectory: [
      4.1e-8, 5.0e-8, 6.2e-8, 7.5e-8, 8.1e-8, 9.2e-8, 1.01e-7, 1.08e-7, 1.14e-7
    ]
  },
  E03: {
    tag: 'E03',
    name: 'E03 — Light Diesel Exchanger',
    serviceName: 'Light Diesel / Crude Exchange',
    rfCurrent: 1.2928e-8,
    uaCurrent: 215400.0,
    uaClean: 218200.0,
    lmtdCurrent: 38.60,
    qTubeCurrent: 7740412.5,
    qShellCurrent: 7789000.0,
    thermalDiscrepancy: 0.0062,
    dataQualityPct: 100.0,
    status: 'OPERATIONAL_NOMINAL',
    recentRfTrajectory: [
      -1.0e-8, -0.5e-8, 0.2e-8, 0.5e-8, 0.8e-8, 1.1e-8, 1.29e-8
    ]
  },
  E04: {
    tag: 'E04',
    name: 'E04 — LVGO Heat Exchanger',
    serviceName: 'Light Vacuum Gas Oil / Crude Exchange',
    rfCurrent: -1.1228e-8,
    uaCurrent: 221000.0,
    uaClean: 220500.0,
    lmtdCurrent: 41.20,
    qTubeCurrent: 7274232.4,
    qShellCurrent: 7291000.0,
    thermalDiscrepancy: 0.0023,
    dataQualityPct: 100.0,
    status: 'OPERATIONAL_NOMINAL',
    recentRfTrajectory: [
      -2.5e-8, -2.0e-8, -1.8e-8, -1.5e-8, -1.2e-8, -1.12e-8
    ]
  },
  E05: {
    tag: 'E05',
    name: 'E05 — Heavy Diesel Exchanger',
    serviceName: 'Heavy Diesel Rundown / Crude Exchange',
    rfCurrent: -1.4703e-8,
    uaCurrent: 212500.0,
    uaClean: 211800.0,
    lmtdCurrent: 48.90,
    qTubeCurrent: 6524622.6,
    qShellCurrent: 6542000.0,
    thermalDiscrepancy: 0.0026,
    dataQualityPct: 100.0,
    status: 'OPERATIONAL_NOMINAL',
    recentRfTrajectory: [
      -3.0e-8, -2.5e-8, -2.1e-8, -1.8e-8, -1.6e-8, -1.47e-8
    ]
  }
};

export const generateTrajectory = (exchangerId: string, horizonHours: number): ForecastPoint[] => {
  const points: ForecastPoint[] = [];
  const baseState = INITIAL_EXCHANGERS[exchangerId] || INITIAL_EXCHANGERS.E01;
  const currentRf = baseState.rfCurrent;

  // 12 historical points
  for (let i = 12; i >= 0; i--) {
    const h = -i;
    const noise = (Math.sin(i * 0.8) * 0.5e-8);
    const histVal = currentRf - (i * 0.4e-8) + noise;
    points.push({
      timestamp: `t-${i}h`,
      hour: h,
      historicalRf: histVal,
    });
  }

  // Future points up to horizon
  const stepCount = horizonHours === 1 ? 4 : horizonHours === 6 ? 6 : 12;
  const stepHours = horizonHours / stepCount;

  for (let i = 1; i <= stepCount; i++) {
    const futureHour = i * stepHours;
    const slope = 0.55e-8; // simulated drift
    const ridgeVal = currentRf + (slope * futureHour);
    const persVal = currentRf; // persistence = constant
    const stdErr = 0.15e-8 * Math.sqrt(futureHour);

    points.push({
      timestamp: `t+${futureHour.toFixed(1)}h`,
      hour: futureHour,
      ridgeForecast: ridgeVal,
      persistenceBaseline: persVal,
      lowerBound: ridgeVal - stdErr,
      upperBound: ridgeVal + stdErr,
    });
  }

  return points;
};

export const getReliabilityState = (scenario: ScenarioMode): ReliabilityState => {
  if (scenario === 'normal') {
    return {
      scenario: 'normal',
      gatePassed: true,
      abstain: false,
      activePolicy: 'PREDICTIVE_CLEANING_WINDOW',
      timestamp: new Date().toISOString(),
      checks: [
        {
          id: 'CHK_01',
          name: 'Data Integrity & Completeness',
          description: 'Validates zero missing historian values, sensor bounds, and monotonic time indices.',
          status: 'PASS',
          value: '100% Complete',
          threshold: 'Min 98.0%',
          isSimulatedDemo: true,
        },
        {
          id: 'CHK_02',
          name: 'Physical Thermodynamic Consistency',
          description: 'Validates heat balance error |Q_tube - Q_shell| / max(Q) <= 0.05 and non-negative LMTD.',
          status: 'PASS',
          value: '0.76% Error',
          threshold: 'Max 5.0%',
          isSimulatedDemo: false,
        },
        {
          id: 'CHK_03',
          name: 'Historical Operating Domain Support',
          description: 'Audits feature vector against convex hull of historical training operating envelope.',
          status: 'PASS',
          value: '0.12 Mahalanobis Dist',
          threshold: 'Max 3.0 Dist',
          isSimulatedDemo: true,
        },
        {
          id: 'CHK_04',
          name: 'Forecast Variance & Uncertainty Gate',
          description: 'Verifies Ridge prediction error variance and residual calibration bounds.',
          status: 'PASS',
          value: '0.54 NMAE',
          threshold: 'Max 0.90 NMAE',
          isSimulatedDemo: true,
        },
      ],
    };
  } else {
    return {
      scenario: 'disturbed',
      gatePassed: false,
      abstain: true,
      abstainReason: 'Process transient detected outside training manifold. Reliability Gate triggered abstention.',
      activePolicy: 'FIXED_INTERVAL_FALLBACK',
      timestamp: new Date().toISOString(),
      checks: [
        {
          id: 'CHK_01',
          name: 'Data Integrity & Completeness',
          description: 'Validates zero missing historian values, sensor bounds, and monotonic time indices.',
          status: 'PASS',
          value: '100% Complete',
          threshold: 'Min 98.0%',
          isSimulatedDemo: true,
        },
        {
          id: 'CHK_02',
          name: 'Physical Thermodynamic Consistency',
          description: 'Validates heat balance error |Q_tube - Q_shell| / max(Q) <= 0.05 and non-negative LMTD.',
          status: 'PASS',
          value: '1.24% Error',
          threshold: 'Max 5.0%',
          isSimulatedDemo: false,
        },
        {
          id: 'CHK_03',
          name: 'Historical Operating Domain Support',
          description: 'Audits feature vector against convex hull of historical training operating envelope.',
          status: 'FAIL',
          value: '4.85 Mahalanobis Dist (OOD)',
          threshold: 'Max 3.0 Dist',
          isSimulatedDemo: true,
        },
        {
          id: 'CHK_04',
          name: 'Forecast Variance & Uncertainty Gate',
          description: 'Verifies Ridge prediction error variance and residual calibration bounds.',
          status: 'FAIL',
          value: '1.42 NMAE (High Variance)',
          threshold: 'Max 0.90 NMAE',
          isSimulatedDemo: true,
        },
      ],
    };
  }
};
