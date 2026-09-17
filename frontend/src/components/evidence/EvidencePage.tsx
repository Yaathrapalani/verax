import React from 'react';
import type { EvidenceTraceStep } from '../../types/foulx';
import { Database, Gauge, Activity, TrendingUp, ShieldCheck, UserCheck, ArrowDown } from 'lucide-react';

export const EvidencePage: React.FC = () => {
  const steps: (EvidenceTraceStep & { icon: React.ReactNode })[] = [
    {
      stepNumber: 1,
      title: 'Measurements (Historian Telemetry)',
      subtitle: 'Raw plant sensor inputs from heat exchanger train',
      status: 'AUDITED',
      provenance: 'data/raw/heat_exchanger_fouling_dataset.csv (SHA-256 Verified)',
      technicalSummary: '64,000 hourly historian readings across temperatures (T_in, T_out), mass flows (m_tube, m_shell), and crude composition parameters.',
      keyMetrics: {
        'Raw Rows': '64,000',
        'Checksum SHA-256': 'c8ed7d...b4d9',
        'Pressure Drop Data': 'ABSENT (Confirmed)',
        'Hidden True Cols': '0 Present',
      },
      icon: <Database className="w-5 h-5 text-[#38bdf8]" />,
    },
    {
      stepNumber: 2,
      title: 'Physics State Estimator (M2)',
      subtitle: 'Deterministic thermodynamic calculations',
      status: 'VALIDATED',
      provenance: 'src/physics/state_estimator.py',
      technicalSummary: 'Computes heat duties (Q_tube, Q_shell), LMTD under counter-current flow arrangement, overall heat transfer coefficient (UA), and thermal discrepancy error.',
      keyMetrics: {
        'UA Clean Window': 'First 100 Hours',
        'Thermal Error Limit': '|Q_t - Q_s| / max(Q) <= 0.05',
        'Flow Arrangement': 'Counter-Current',
        'Determinism': '100% Exact',
      },
      icon: <Gauge className="w-5 h-5 text-[#fbbf24]" />,
    },
    {
      stepNumber: 3,
      title: 'Fouling State Derivation',
      subtitle: 'Derived fouling resistance proxy calculation',
      status: 'VALIDATED',
      provenance: 'data/PHYSICS_STATE_SPEC.md',
      technicalSummary: 'Calculates R_f,derived(t) = (1/UA(t)) - (1/UA_clean_ref) representing thermal fouling accumulation in m²·K/W.',
      keyMetrics: {
        'Target Symbol': 'R_f,derived',
        'Unit': 'm²·K/W',
        'Primary Scale (Std)': '1.05e-7 m²·K/W',
        'Zero Imputation': 'Forbidden',
      },
      icon: <Activity className="w-5 h-5 text-[#a78bfa]" />,
    },
    {
      stepNumber: 4,
      title: 'Causal Ridge Prognosis Engine (M4.0)',
      subtitle: 'Machine learning forecasting model for R_f(t+h)',
      status: 'VALIDATED',
      provenance: 'src/models/ridge_forecaster.py',
      technicalSummary: 'StandardScaler fit strictly on Train set. Ridge regression regularized via validation grid search. Evaluates 1h, 6h, 24h horizons.',
      keyMetrics: {
        'Validation MAE (24h)': '6.7481e-8 m²·K/W',
        'Persistence Impr.': '+23.31% over Persistence',
        'Scaler Calibration': 'Train-Only (t <= 44,799)',
        'Causality Guarantee': 'Right-Closed Windows',
      },
      icon: <TrendingUp className="w-5 h-5 text-[#34d399]" />,
    },
    {
      stepNumber: 5,
      title: 'Reliability Gate (Trust Layer)',
      subtitle: 'Multi-criteria safety and domain validation checks',
      status: 'SIMULATED_DEMO',
      provenance: 'src/reliability/gate.py (M5 Spec)',
      technicalSummary: 'Evaluates 4 checks: Data Integrity, Physical Consistency, Historical Operating Envelope, and Error Variance bounds. Triggers explicit fallback if violated.',
      keyMetrics: {
        'Abstention Policy': 'Explicit Fixed Policy Fallback',
        'Convex Hull Check': 'Mahalanobis Outlier Detection',
        'Variance Gate': 'NMAE <= 0.90 Threshold',
        'Gate Status': 'Active Monitoring',
      },
      icon: <ShieldCheck className="w-5 h-5 text-[#f59e0b]" />,
    },
    {
      stepNumber: 6,
      title: 'Decision Support & Human Review',
      subtitle: 'Advisory maintenance window recommendations',
      status: 'ACTIVE',
      provenance: 'AGENTS.md Engineering Constitution Rule 5',
      technicalSummary: 'Recommends cleaning window for plant review. Strictly advisory; requires human engineering approval before execution.',
      keyMetrics: {
        'Recommendation Title': 'CLEANING WINDOW — ENGINEERING REVIEW',
        'Human Approval': 'MANDATORY',
        'Autonomous Action': 'STRICTLY FORBIDDEN',
        'Fallback Mode': 'Fixed Policy Active',
      },
      icon: <UserCheck className="w-5 h-5 text-[#38bdf8]" />,
    },
  ];

  return (
    <div className="space-y-6 text-xs">
      <div className="bg-[#11151e] p-4 rounded border border-[#1e2638]">
        <h1 className="text-base font-bold text-white uppercase tracking-wider">
          FOUL-X SCIENTIFIC & AUDIT EVIDENCE TRACE
        </h1>
        <p className="text-xs text-[#9ca3af] mt-1">
          Complete end-to-end evidence lineage from raw historian measurements to human-in-the-loop decision support.
        </p>
      </div>

      <div className="space-y-4">
        {steps.map((step, idx) => (
          <React.Fragment key={step.stepNumber}>
            <div className="bg-[#11151e] p-5 rounded border border-[#1e2638] space-y-3">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-[#182030] pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-[#161c28] border border-[#212b3e]">
                    {step.icon}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-[#38bdf8]">STEP 0{step.stepNumber}</span>
                      <h2 className="text-sm font-bold text-white">{step.title}</h2>
                    </div>
                    <p className="text-xs text-[#6b7280]">{step.subtitle}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-1 rounded text-[10px] font-mono font-bold uppercase tracking-wider border ${
                    step.status === 'VALIDATED' || step.status === 'AUDITED'
                      ? 'bg-[#102a1d] text-[#34d399] border-[#065f46]'
                      : step.status === 'SIMULATED_DEMO'
                      ? 'bg-[#261e0b] text-[#fbbf24] border-[#78350f]'
                      : 'bg-[#1a2333] text-[#38bdf8] border-[#2563eb]'
                  }`}>
                    {step.status}
                  </span>
                </div>
              </div>

              <div className="text-xs text-[#d1d5db]">
                <p><strong className="text-[#9ca3af]">Provenance / Source:</strong> <code className="text-[#93c5fd] font-mono bg-[#161c28] px-1.5 py-0.5 rounded">{step.provenance}</code></p>
                <p className="mt-1"><strong className="text-[#9ca3af]">Technical Explanation:</strong> {step.technicalSummary}</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-3 border-t border-[#182030] font-mono text-[11px]">
                {Object.entries(step.keyMetrics).map(([k, v]) => (
                  <div key={k} className="bg-[#161c28] p-2 rounded border border-[#212b3e]">
                    <span className="text-[9px] text-[#6b7280] uppercase block">{k}</span>
                    <span className="font-bold text-white">{v}</span>
                  </div>
                ))}
              </div>
            </div>

            {idx < steps.length - 1 && (
              <div className="flex justify-center my-1">
                <ArrowDown className="w-5 h-5 text-[#3b82f6] animate-bounce" />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
