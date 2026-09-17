import React from 'react';
import { BarChart3, TrendingUp, ShieldCheck } from 'lucide-react';

interface BenchmarkModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BenchmarkModal: React.FC<BenchmarkModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#071018] border border-[#15212d] w-full max-w-4xl rounded shadow-2xl overflow-hidden flex flex-col max-h-[90vh] font-mono text-xs">
        {/* Header */}
        <div className="p-4 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-[#34d399]" />
            <div>
              <h2 className="font-extrabold uppercase text-white text-sm tracking-wider">
                VALIDATED BENCHMARK & EXPERIMENT RESULTS
              </h2>
              <p className="text-[10px] text-[#6b7280]">
                Scientific evaluation of M4.0 Causal Ridge prognosis and M7.0 Policy Stress Experiment.
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
          {/* Panel 1: M4.0 Causal Ridge vs Persistence */}
          <div className="bg-[#0b1622] p-5 rounded border border-[#1b2a3a] space-y-3">
            <div className="flex items-center justify-between border-b border-[#15212d] pb-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-[#27b7e8]" />
                <h3 className="font-bold text-white text-sm uppercase">1. M4.0 CAUSAL RIDGE PROGNOSIS BENCHMARK</h3>
              </div>
              <span className="text-[10px] text-[#34d399] font-bold bg-[#064e3b] px-2 py-0.5 rounded border border-[#10b981]">
                VALIDATED ON SYNTHETIC BENCHMARK
              </span>
            </div>

            <p className="text-[11px] text-[#d1d5db]">
              Evaluating M4.0 Causal Ridge model against the baseline Persistence model across operational horizons (1h, 6h, 24h) on exchangers E01-E05.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
              <div className="bg-[#071018] p-3 rounded border border-[#15212d] text-center">
                <span className="text-[10px] text-[#6b7280] block font-bold">1-HOUR HORIZON</span>
                <span className="text-lg font-black text-[#34d399]">+21.4%</span>
                <span className="text-[10px] text-[#9ca3af] block">MAE Improvement vs Persistence</span>
              </div>

              <div className="bg-[#071018] p-3 rounded border border-[#15212d] text-center">
                <span className="text-[10px] text-[#6b7280] block font-bold">6-HOUR HORIZON</span>
                <span className="text-lg font-black text-[#34d399]">+23.3%</span>
                <span className="text-[10px] text-[#9ca3af] block">MAE Improvement vs Persistence</span>
              </div>

              <div className="bg-[#071018] p-3 rounded border border-[#15212d] text-center">
                <span className="text-[10px] text-[#6b7280] block font-bold">24-HOUR HORIZON</span>
                <span className="text-lg font-black text-[#34d399]">+28.9%</span>
                <span className="text-[10px] text-[#9ca3af] block">MAE Improvement vs Persistence</span>
              </div>
            </div>

            <div className="text-[10px] text-[#6b7280] italic text-right pt-1">
              * Validation result on current synthetic physics-based benchmark. (Not claimed as real refinery monetary savings).
            </div>
          </div>

          {/* Panel 2: M7.0 Controlled Policy Stress Experiment */}
          <div className="bg-[#0b1622] p-5 rounded border border-[#1b2a3a] space-y-3">
            <div className="flex items-center justify-between border-b border-[#15212d] pb-2">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-[#fbbf24]" />
                <h3 className="font-bold text-white text-sm uppercase">2. M7.0 POLICY STRESS EXPERIMENT (FIXED vs UNGATED vs GATED)</h3>
              </div>
              <span className="text-[10px] text-[#fbbf24] font-bold bg-[#451a03] px-2 py-0.5 rounded border border-[#b45309]">
                CONTROLLED SYNTHETIC STRESS TEST
              </span>
            </div>

            <p className="text-[11px] text-[#d1d5db]">
              Testing reliability-gated AI safety against un-gated AI predictions under $+6\sigma$ operational regime shift perturbations.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
              <div className="bg-[#071018] p-3 rounded border border-[#15212d] space-y-2">
                <span className="font-bold text-[#34d399] block text-xs border-b border-[#15212d] pb-1">
                  SUPPORTED REGIME (PASS)
                </span>
                <p className="text-[11px] text-[#9ca3af]">
                  AI-assisted maintenance recommendation available when M5 gate passes. Proactive 14-day cleaning window recommended safely.
                </p>
              </div>

              <div className="bg-[#071018] p-3 rounded border border-[#15212d] space-y-2">
                <span className="font-bold text-[#ef4444] block text-xs border-b border-[#15212d] pb-1">
                  CONTROLLED +6σ REGIME SHIFT (ABSTAIN)
                </span>
                <p className="text-[11px] text-[#9ca3af]">
                  <strong className="text-white">200 / 200</strong> gated cases abstained. <strong className="text-[#34d399]">0 harmful</strong> gated recommendations under the defined synthetic perturbation experiment.
                </p>
              </div>
            </div>

            <div className="text-[10px] text-[#6b7280] italic text-right pt-1">
              * Controlled synthetic stress test. Evaluates safety invariants under distributional shift.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
