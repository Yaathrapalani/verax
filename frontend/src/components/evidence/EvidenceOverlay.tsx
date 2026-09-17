import React from 'react';
import { ShieldCheck, ShieldAlert, X, Database, Gauge, Activity, TrendingUp, UserCheck, Lock, ArrowDown } from 'lucide-react';

interface EvidenceOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  scenario: 'normal' | 'disturbed';
  selectedAssetTag: string;
}

export const EvidenceOverlay: React.FC<EvidenceOverlayProps> = ({ isOpen, onClose, scenario, selectedAssetTag }) => {
  if (!isOpen) return null;

  const isNormal = scenario === 'normal';

  const chainSteps = [
    {
      step: 1,
      title: 'Historian Measurements',
      status: 'VALIDATED',
      desc: 'Raw stream temperatures (T_in, T_out), mass flows (m_tube, m_shell), and crude properties.',
      detail: '64,000 hourly historian readings (SHA-256 Verified). Zero pressure drop columns.',
      icon: <Database className="w-4 h-4 text-[#27b7e8]" />,
    },
    {
      step: 2,
      title: 'M2 Physics State Estimator',
      status: 'VALIDATED',
      desc: 'Deterministic counter-current LMTD, heat duties (Q_tube, Q_shell), and overall heat transfer (UA).',
      detail: 'Thermal error |Q_t - Q_s| / max(Q) = 0.76% (Limit <= 5.0%). Clean window: 100h.',
      icon: <Gauge className="w-4 h-4 text-[#fbbf24]" />,
    },
    {
      step: 3,
      title: 'Fouling State Derivation',
      status: 'VALIDATED',
      desc: 'R_f,derived(t) = (1/UA(t)) - (1/UA_clean_ref). Derived fouling resistance proxy.',
      detail: 'Unit: m²·K/W. Target scale std: 1.05e-7 m²·K/W. Zero silent imputation.',
      icon: <Activity className="w-4 h-4 text-[#a78bfa]" />,
    },
    {
      step: 4,
      title: 'M4.0 Causal Ridge Prognosis',
      status: 'VALIDATED',
      desc: 'Causal feature matrix (rolling W in 6h, 24h, 72h, 168h). Scaler fit strictly on Train set.',
      detail: 'Validation MAE: 6.7481e-8 m²·K/W (+23.31% relative improvement over Persistence baseline).',
      icon: <TrendingUp className="w-4 h-4 text-[#34d399]" />,
    },
    {
      step: 5,
      title: 'Reliability Gate (Trust Layer)',
      status: isNormal ? 'PASS' : 'FAIL_ABSTAIN',
      desc: isNormal
        ? 'All 4 safety checks passed. Historical convex hull and error variance within limits.'
        : 'Process transient outside historical training manifold (OOD). Reliability gate triggered abstention.',
      detail: isNormal ? 'Gate status: SUPPORTED' : 'Result: FOUL-X ABSTAINED — Forecast withheld from decision support',
      icon: isNormal ? <ShieldCheck className="w-4 h-4 text-[#34d399]" /> : <ShieldAlert className="w-4 h-4 text-[#ef4444]" />,
    },
    {
      step: 6,
      title: 'Decision Support & Fallback Policy',
      status: isNormal ? 'RECOMMENDED' : 'FIXED_POLICY_ACTIVE',
      desc: isNormal
        ? 'CLEANING WINDOW — ENGINEERING REVIEW (Proactive 14-day window).'
        : 'Fixed interval cleaning policy remains active (90 days).',
      detail: 'Human engineering approval MANDATORY.',
      icon: <UserCheck className="w-4 h-4 text-[#27b7e8]" />,
    },
  ];

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#071018] border border-[#15212d] w-full max-w-3xl rounded shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-4 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-[#27b7e8]" />
            <h2 className="font-extrabold uppercase text-white text-sm tracking-wider">
              FOUL-X SCIENTIFIC & RELIABILITY EVIDENCE TRACE ({selectedAssetTag})
            </h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-[#15212d] text-[#9ca3af] hover:text-white rounded transition cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chain Steps */}
        <div className="p-5 overflow-y-auto space-y-3 font-mono text-xs">
          {!isNormal && (
            <div className="p-3 bg-[#240e0e] border border-[#ef4444] rounded text-[#fca5a5] space-y-1">
              <div className="flex items-center gap-2 font-bold text-xs uppercase">
                <ShieldAlert className="w-4 h-4 text-[#ef4444]" />
                <span>FOUL-X ABSTAINED — FORECAST WITHHELD</span>
              </div>
              <p className="text-[11px] text-[#fecaca]">
                "The forecast remains available, but the maintenance recommendation has been withheld because the current operating regime is outside the supported historical context."
              </p>
              <div className="text-[11px] font-bold text-white flex items-center gap-1 pt-1">
                <Lock className="w-3.5 h-3.5 text-[#f87171]" />
                <span>FALLBACK: Fixed cleaning policy remains active. Human approval required.</span>
              </div>
            </div>
          )}

          {chainSteps.map((step, idx) => (
            <React.Fragment key={step.step}>
              <div className={`p-3.5 rounded border space-y-1.5 ${
                step.status.includes('FAIL')
                  ? 'bg-[#1e1010] border-[#7f1d1d]'
                  : 'bg-[#0b121b] border-[#162332]'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded bg-[#101923] border border-[#1b2a3a]">{step.icon}</div>
                    <span className="font-bold text-white text-xs">
                      STEP 0{step.step}: {step.title}
                    </span>
                  </div>

                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                    step.status === 'VALIDATED' || step.status === 'PASS' || step.status === 'RECOMMENDED'
                      ? 'bg-[#065f46] text-[#6ee7b7] border-[#10b981]'
                      : 'bg-[#7f1d1d] text-[#fca5a5] border-[#ef4444]'
                  }`}>
                    {step.status}
                  </span>
                </div>

                <p className="text-[#9ca3af] text-[11px]">{step.desc}</p>
                <div className="text-[10px] text-[#38bdf8] bg-[#080d14] p-2 rounded border border-[#141f2c]">
                  {step.detail}
                </div>
              </div>

              {idx < chainSteps.length - 1 && (
                <div className="flex justify-center my-0.5">
                  <ArrowDown className="w-4 h-4 text-[#27b7e8]" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Modal Footer */}
        <div className="p-3 bg-[#090e15] border-t border-[#15212d] flex justify-between items-center text-[10px] text-[#6b7280]">
          <span>Representative engineering evidence chain</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-[#1b2a3a] hover:bg-[#27b7e8] text-[#27b7e8] hover:text-black font-bold rounded transition cursor-pointer"
          >
            CLOSE TRACE
          </button>
        </div>
      </div>
    </div>
  );
};
