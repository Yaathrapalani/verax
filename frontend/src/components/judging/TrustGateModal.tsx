import React from 'react';
import { ShieldCheck, ShieldAlert, ArrowDown, Lock, AlertTriangle } from 'lucide-react';

interface TrustGateModalProps {
  isOpen: boolean;
  onClose: () => void;
  scenario: 'normal' | 'disturbed';
  setScenario: (scen: 'normal' | 'disturbed') => void;
}

export const TrustGateModal: React.FC<TrustGateModalProps> = ({
  isOpen,
  onClose,
  scenario,
  setScenario,
}) => {
  if (!isOpen) return null;

  const isNormal = scenario === 'normal';

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#071018] border border-[#15212d] w-full max-w-4xl rounded shadow-2xl overflow-hidden flex flex-col max-h-[90vh] font-mono text-xs">
        {/* Header */}
        <div className="p-4 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-[#27b7e8]" />
            <div>
              <h2 className="font-extrabold uppercase text-white text-sm tracking-wider">
                FOUL-X DOMINANT VISUAL ARCHITECTURE — THE TRUST GATE
              </h2>
              <p className="text-[10px] text-[#6b7280]">
                Demonstrating reliability-gated maintenance support vs un-gated AI predictions under regime shifts.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="px-2.5 py-1 bg-[#15212d] hover:bg-[#1f2d3d] text-white rounded text-[11px] font-bold cursor-pointer transition"
          >
            CLOSE [ESC]
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Interactive Trigger Control */}
          <div className="bg-[#0b1622] p-4 rounded border border-[#1b2a3a] flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <span className="text-[10px] text-[#27b7e8] font-bold uppercase tracking-wider block">INTERACTIVE STRESS DEMO</span>
              <h3 className="font-bold text-white text-sm">WHAT IF OPERATING CONDITIONS SHIFT?</h3>
              <p className="text-[11px] text-[#9ca3af] mt-0.5">
                Toggle between normal operating regime and +6σ synthetic regime shift perturbation.
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => setScenario('normal')}
                className={`px-3 py-2 rounded text-xs font-bold border transition cursor-pointer flex items-center gap-1.5 ${
                  isNormal
                    ? 'bg-[#065f46] text-[#6ee7b7] border-[#10b981] shadow-lg shadow-[#10b981]/20'
                    : 'bg-[#090e15] text-[#6b7280] border-[#15212d] hover:text-white'
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                <span>NORMAL REGIME</span>
              </button>

              <button
                onClick={() => setScenario('disturbed')}
                className={`px-3 py-2 rounded text-xs font-bold border transition cursor-pointer flex items-center gap-1.5 ${
                  !isNormal
                    ? 'bg-[#7f1d1d] text-[#fca5a5] border-[#ef4444] shadow-lg shadow-[#ef4444]/20'
                    : 'bg-[#090e15] text-[#6b7280] border-[#15212d] hover:text-white'
                }`}
              >
                <ShieldAlert className="w-4 h-4" />
                <span>+6σ REGIME SHIFT</span>
              </button>
            </div>
          </div>

          {/* Dominant Flow Visual Diagram */}
          <div className="bg-[#050b11] p-6 rounded border border-[#15212d] flex flex-col items-center justify-center relative min-h-[300px]">
            {/* Flow Step 1: Forecast */}
            <div className="bg-[#0b1118] border border-[#1b2a3a] px-6 py-2.5 rounded text-center w-64 shadow-md">
              <span className="text-[10px] text-[#6b7280] block font-bold">M4.0 CAUSAL RIDGE</span>
              <span className="font-extrabold text-white text-xs">FOULING FORECAST</span>
            </div>

            {/* Connector */}
            <div className="my-2 flex flex-col items-center">
              <div className="h-6 w-0.5 bg-[#27b7e8]"></div>
              <ArrowDown className="w-4 h-4 text-[#27b7e8] -mt-1" />
            </div>

            {/* Flow Step 2: The Trust Gate Box */}
            <div
              className={`border-2 px-8 py-4 rounded-lg text-center w-80 shadow-2xl transition-all duration-300 ${
                isNormal
                  ? 'bg-[#064e3b]/30 border-[#10b981] text-[#6ee7b7]'
                  : 'bg-[#7f1d1d]/40 border-[#ef4444] text-[#fca5a5] animate-pulse'
              }`}
            >
              <div className="flex items-center justify-center gap-2 mb-1">
                {isNormal ? <ShieldCheck className="w-5 h-5 text-[#34d399]" /> : <ShieldAlert className="w-5 h-5 text-[#ef4444]" />}
                <span className="text-xs font-bold uppercase tracking-wider">M5 RELIABILITY GATE</span>
              </div>

              <div className="text-xl font-black font-mono tracking-widest my-1">
                {isNormal ? 'GATE: PASS' : 'GATE: ABSTAIN'}
              </div>

              <p className="text-[11px] font-mono opacity-90 mt-1">
                {isNormal ? '✓ All 4 Checks Passed (Data, Sensor, Physics, Support)' : '✕ REGIME SUPPORT: REGIME_OOD'}
              </p>
            </div>

            {/* Connector */}
            <div className="my-2 flex flex-col items-center">
              <div className={`h-6 w-0.5 ${isNormal ? 'bg-[#10b981]' : 'bg-[#ef4444]'}`}></div>
              <ArrowDown className={`w-4 h-4 -mt-1 ${isNormal ? 'text-[#10b981]' : 'text-[#ef4444]'}`} />
            </div>

            {/* Flow Step 3: Decision Support Output */}
            <div
              className={`border px-6 py-3 rounded text-center w-96 shadow-lg ${
                isNormal
                  ? 'bg-[#0b1622] border-[#27b7e8] text-white'
                  : 'bg-[#240e0e] border-[#ef4444] text-[#fca5a5]'
              }`}
            >
              <span className="text-[10px] text-[#9ca3af] block font-bold uppercase">M6 DECISION ENGINE RESULT</span>

              {isNormal ? (
                <div>
                  <div className="font-extrabold text-sm text-[#34d399] tracking-wider my-0.5">
                    CLEANING WINDOW — ENGINEERING REVIEW
                  </div>
                  <p className="text-[10px] text-[#9ca3af]">
                    Proactive maintenance recommendation generated. Human engineering approval required.
                  </p>
                </div>
              ) : (
                <div>
                  <div className="font-extrabold text-sm text-[#ef4444] tracking-wider my-0.5 flex items-center justify-center gap-1.5">
                    <Lock className="w-4 h-4 text-[#ef4444]" />
                    <span>AI ACTION WITHHELD — FIXED POLICY ACTIVE</span>
                  </div>
                  <p className="text-[10px] text-[#fecaca] mt-0.5">
                    Fallback policy active (Fixed 90-day maintenance interval). Recommendation withheld.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Explanation Box */}
          <div className="bg-[#090e15] p-4 rounded border border-[#15212d] space-y-2">
            <h4 className="font-bold text-white text-xs uppercase flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-[#fbbf24]" />
              <span>SAFETY INVARIANT & EXPLANATION</span>
            </h4>

            <p className="text-[11px] text-[#d1d5db] leading-relaxed">
              {!isNormal
                ? '"The current operating state is outside the validated support of the prognosis model. FOUL-X withholds the AI-assisted maintenance recommendation and retains the fixed-policy fallback."'
                : 'Current operating state is within the historical convex hull and error variance bounds of the trained prognosis model. Maintenance decision support is safely enabled.'}
            </p>

            <div className="pt-2 border-t border-[#15212d] grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px] text-[#9ca3af]">
              <div>
                <span className="text-white font-bold block">Scientific Boundary:</span>
                FOUL-X does not claim zero-risk or absolute precision. It explicit gates predictions based on historical manifold support.
              </div>
              <div>
                <span className="text-white font-bold block">Deterministic Fallback:</span>
                Under ABSTAIN, the system defaults cleanly to existing fixed plant policy without interrupting operations.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
