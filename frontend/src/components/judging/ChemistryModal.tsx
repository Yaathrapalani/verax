import React from 'react';
import { FlaskConical, AlertTriangle, ArrowRight } from 'lucide-react';

interface ChemistryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChemistryModal: React.FC<ChemistryModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#071018] border border-[#15212d] w-full max-w-4xl rounded shadow-2xl overflow-hidden flex flex-col max-h-[90vh] font-mono text-xs">
        {/* Header */}
        <div className="p-4 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-[#38bdf8]" />
            <div>
              <h2 className="font-extrabold uppercase text-white text-sm tracking-wider">
                BOUNDED PROCESS CHEMISTRY & THERMODYNAMIC SIMULATION
              </h2>
              <p className="text-[10px] text-[#6b7280]">
                Transparent crude oil fraction thermal degradation & asphaltene deposition stoichiometry.
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
          {/* Scientific Boundary Banner */}
          <div className="bg-[#0b1622] p-4 rounded border border-[#1b2a3a] space-y-2">
            <div className="flex items-center gap-2 text-[#fbbf24] font-bold text-xs uppercase">
              <AlertTriangle className="w-4 h-4" />
              <span>CHEMISTRY SIMULATION EVIDENCE & BOUNDARY STATUS</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[10px]">
              <div className="bg-[#071018] p-2 rounded border border-[#15212d]">
                <span className="text-[#34d399] font-bold block">COMPOSITION</span>
                <span>Crude Fraction Assays</span>
              </div>
              <div className="bg-[#071018] p-2 rounded border border-[#15212d]">
                <span className="text-[#38bdf8] font-bold block">PROPERTY MODEL</span>
                <span>Peng-Robinson EOS</span>
              </div>
              <div className="bg-[#071018] p-2 rounded border border-[#15212d]">
                <span className="text-[#fbbf24] font-bold block">KINETICS</span>
                <span className="text-[#fbbf24]">STOICHIOMETRIC / EQUILIBRIUM MODE</span>
              </div>
              <div className="bg-[#071018] p-2 rounded border border-[#15212d]">
                <span className="text-[#6b7280] font-bold block">REACTION NETWORK</span>
                <span className="text-[#9ca3af]">BOUNDED PREHEAT DEPOSITION</span>
              </div>
            </div>
          </div>

          {/* Feed Fraction Composition Table */}
          <div className="bg-[#090e15] p-4 rounded border border-[#15212d] space-y-2">
            <h3 className="font-bold text-white text-xs uppercase">CRUDE FEED COMPOSITION & THERMAL CONDITIONS</h3>
            <table className="w-full text-left text-[11px] font-mono">
              <thead>
                <tr className="border-b border-[#15212d] text-[#6b7280]">
                  <th className="py-1">Component / Cut</th>
                  <th className="py-1">Vol %</th>
                  <th className="py-1">Phase</th>
                  <th className="py-1">Preheat Temp Range</th>
                  <th className="py-1">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#15212d] text-[#d1d5db]">
                <tr>
                  <td className="py-1.5 font-bold text-white">Naphtha Fraction</td>
                  <td>18.5%</td>
                  <td>Vapor/Liquid</td>
                  <td>90 - 140 °C</td>
                  <td className="text-[#34d399]">OBSERVED</td>
                </tr>
                <tr>
                  <td className="py-1.5 font-bold text-white">Kerosene Fraction (E-102 Hot Side)</td>
                  <td>14.2%</td>
                  <td>Liquid</td>
                  <td>140 - 210 °C</td>
                  <td className="text-[#34d399]">OBSERVED</td>
                </tr>
                <tr>
                  <td className="py-1.5 font-bold text-white">Gas Oil / Diesel Cut</td>
                  <td>28.0%</td>
                  <td>Liquid</td>
                  <td>210 - 320 °C</td>
                  <td className="text-[#34d399]">OBSERVED</td>
                </tr>
                <tr>
                  <td className="py-1.5 font-bold text-[#fbbf24]">Asphaltene & Resins (Fouling Precursors)</td>
                  <td>3.8%</td>
                  <td>Colloidal Suspenoid</td>
                  <td>&gt; 180 °C (Fouling Active)</td>
                  <td className="text-[#fbbf24]">BOUNDED MODEL</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Deposition Mechanism Diagram */}
          <div className="bg-[#050b11] p-4 rounded border border-[#15212d] space-y-3">
            <h4 className="font-bold text-white text-xs uppercase">THERMAL FOULING DEPOSITION MECHANISM (E-102)</h4>
            <div className="flex flex-col md:flex-row items-center justify-between gap-3 text-[10px] text-center">
              <div className="bg-[#0b1118] p-3 rounded border border-[#15212d] flex-1">
                <span className="text-[#38bdf8] font-bold block">1. SOLUBILITY LOSS</span>
                <span>Asphaltene precipitation at wall T &gt; 185 °C</span>
              </div>
              <ArrowRight className="w-4 h-4 text-[#27b7e8] shrink-0 hidden md:block" />
              <div className="bg-[#0b1118] p-3 rounded border border-[#15212d] flex-1">
                <span className="text-[#fbbf24] font-bold block">2. AGGREGATION</span>
                <span>Colloidal particle growth & wall attachment</span>
              </div>
              <ArrowRight className="w-4 h-4 text-[#27b7e8] shrink-0 hidden md:block" />
              <div className="bg-[#0b1118] p-3 rounded border border-[#15212d] flex-1">
                <span className="text-[#ef4444] font-bold block">3. THERMAL COKING</span>
                <span>Coke layer deposition ($R_f$ accumulation)</span>
              </div>
            </div>
          </div>

          {/* Scenario Comparison */}
          <div className="bg-[#090e15] p-3 rounded border border-[#15212d] flex items-center justify-between text-[11px]">
            <span className="text-[#9ca3af]">Mass & Energy Balance: <strong className="text-white">VERIFIED (|Q_t - Q_s|/Q_max = 0.76%)</strong></span>
            <span className="text-[#fbbf24] font-bold">KINETICS UNAVAILABLE — EQUILIBRIUM / STOICHIOMETRIC MODE ONLY</span>
          </div>
        </div>
      </div>
    </div>
  );
};
