import React, { useEffect, useState } from 'react';
import type { ReliabilityState, ScenarioMode } from '../../types/foulx';
import { apiService } from '../../services/api';
import { ShieldCheck, ShieldAlert, CheckCircle2, XCircle, Lock, Shield } from 'lucide-react';

interface ReliabilityPageProps {
  scenario: ScenarioMode;
  setScenario: (scenario: ScenarioMode) => void;
}

export const ReliabilityPage: React.FC<ReliabilityPageProps> = ({ scenario, setScenario }) => {
  const [relState, setRelState] = useState<ReliabilityState | null>(null);

  useEffect(() => {
    apiService.setScenario(scenario);
    apiService.getReliabilityState().then(setRelState);
  }, [scenario]);

  if (!relState) return <div className="p-8 text-center text-[#9ca3af]">Loading Reliability Gate...</div>;

  return (
    <div className="space-y-6 text-xs">
      {/* Top Banner Notice */}
      <div className="bg-[#11151e] p-4 rounded border border-[#1e2638] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-[#fbbf24]" />
            <h1 className="text-base font-bold text-white uppercase tracking-wider">
              FOUL-X TRUST-GATE & RELIABILITY LAYER
            </h1>
            <span className="px-2 py-0.5 rounded bg-[#1f293d] text-[#fbbf24] text-[10px] font-bold border border-[#374151]">
              DEMO STATE DATA
            </span>
          </div>
          <p className="text-xs text-[#9ca3af] mt-1">
            Evaluates data integrity, physical thermal consistency, historical manifold coverage, and variance calibration before permitting predictive decision support.
          </p>
        </div>

        {/* Interactive Scenario Buttons */}
        <div className="flex items-center gap-2 bg-[#161c28] p-1.5 rounded border border-[#232c3d]">
          <button
            onClick={() => setScenario('normal')}
            className={`px-3 py-1.5 rounded font-bold transition cursor-pointer ${
              scenario === 'normal'
                ? 'bg-[#065f46] text-[#6ee7b7] border border-[#10b981]'
                : 'text-[#9ca3af] hover:text-white'
            }`}
          >
            NORMAL / TRUSTED
          </button>
          <button
            onClick={() => setScenario('disturbed')}
            className={`px-3 py-1.5 rounded font-bold transition cursor-pointer ${
              scenario === 'disturbed'
                ? 'bg-[#7f1d1d] text-[#fca5a5] border border-[#ef4444]'
                : 'bg-[#161c28] text-[#9ca3af] hover:text-white'
            }`}
          >
            DISTURBED / ABSTAIN
          </button>
        </div>
      </div>

      {/* Main Abstention / Policy Banner */}
      {relState.abstain ? (
        <div className="bg-[#240e0e] p-5 rounded border-2 border-[#ef4444] space-y-3">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-[#ef4444]" />
            <div>
              <h2 className="text-sm font-extrabold uppercase tracking-widest text-[#fca5a5]">
                FOUL-X ABSTAINED — RELIABILITY GATE TRIGGERED
              </h2>
              <p className="text-xs text-[#fecaca] mt-0.5">
                "Forecast remains available, but the maintenance recommendation has been withheld."
              </p>
            </div>
          </div>

          <div className="pt-3 border-t border-[#7f1d1d] flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-white">
              <Lock className="w-4 h-4 text-[#f87171]" />
              <span>FALLBACK POLICY: Fixed cleaning policy remains active.</span>
            </div>
            <span className="text-[11px] text-[#fca5a5] italic">
              Reason: {relState.abstainReason}
            </span>
          </div>
        </div>
      ) : (
        <div className="bg-[#0c261a] p-5 rounded border-2 border-[#10b981] space-y-2">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-6 h-6 text-[#34d399]" />
            <div>
              <h2 className="text-sm font-extrabold uppercase tracking-widest text-[#6ee7b7]">
                RELIABILITY GATE PASSED — DECISION SUPPORT ELIGIBLE
              </h2>
              <p className="text-xs text-[#a7f3d0] mt-0.5">
                All 4 safety checks verified. Forecast eligible for predictive cleaning window recommendation.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 4 Reliability Checks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {relState.checks.map((chk) => {
          const isPass = chk.status === 'PASS';
          return (
            <div 
              key={chk.id}
              className={`p-4 rounded border space-y-2 ${
                isPass
                  ? 'bg-[#111622] border-[#1e293b]'
                  : 'bg-[#1e1212] border-[#7f1d1d]'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {isPass ? (
                    <CheckCircle2 className="w-4 h-4 text-[#34d399]" />
                  ) : (
                    <XCircle className="w-4 h-4 text-[#f87171]" />
                  )}
                  <h3 className="font-bold text-white text-xs">{chk.name}</h3>
                </div>

                <div className="flex items-center gap-2">
                  {chk.isSimulatedDemo && (
                    <span className="text-[9px] uppercase font-mono font-semibold px-1.5 py-0.5 rounded bg-[#1e293b] text-[#fbbf24]">
                      SIMULATED DEMO
                    </span>
                  )}
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono border ${
                    isPass ? 'bg-[#065f46] text-[#6ee7b7] border-[#10b981]' : 'bg-[#7f1d1d] text-[#fca5a5] border-[#ef4444]'
                  }`}>
                    {chk.status}
                  </span>
                </div>
              </div>

              <p className="text-xs text-[#9ca3af]">{chk.description}</p>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[#1e2638] font-mono text-[11px]">
                <div>
                  <span className="text-[#6b7280] block text-[9px] uppercase">OBSERVED VALUE</span>
                  <span className={`font-bold ${isPass ? 'text-white' : 'text-[#f87171]'}`}>{chk.value}</span>
                </div>
                <div>
                  <span className="text-[#6b7280] block text-[9px] uppercase">SAFETY THRESHOLD</span>
                  <span className="font-bold text-[#9ca3af]">{chk.threshold}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
