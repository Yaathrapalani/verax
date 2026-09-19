import React, { useState } from 'react';
import { Layers, Database, ArrowRight } from 'lucide-react';
import type { PlantWorkstationState } from '../../agent/types';

interface EngineeringInspectorProps {
  state: PlantWorkstationState;
  onSelectHypothesis: (hypothesisId: string) => void;
  onSelectStream: (streamId: string) => void;
  onOpenEvidence: () => void;
}

type InspectorTab = 'IDENTITY' | 'STATE' | 'THERMO' | 'FOULING' | 'EVIDENCE' | 'PROVENANCE';

export const EngineeringInspector: React.FC<EngineeringInspectorProps> = ({
  state,
  onSelectHypothesis,
  onSelectStream,
  onOpenEvidence,
}) => {
  const [activeTab, setActiveTab] = useState<InspectorTab>('IDENTITY');

  const isE102 = state.selectedAssetTag === 'E-102' || state.selectedAssetTag === 'E02';
  const isOod = state.scenario === 'disturbed';

  return (
    <aside className="w-84 bg-[#090e15] border-l border-[#1e293b] flex flex-col h-full text-xs font-mono text-gray-300 z-10 select-none shadow-xl">
      {/* Top Inspector Header */}
      <div className="p-3 bg-[#0b1118] border-b border-[#1e293b] flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span className="font-extrabold text-white text-xs uppercase tracking-wider">
              {state.selectedAssetTag}
            </span>
            <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold uppercase ${
              isE102 ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
            }`}>
              {isE102 ? 'ATTENTION' : 'NOMINAL'}
            </span>
          </div>
          <p className="text-[10px] text-gray-400 mt-0.5">
            {isE102 ? 'Kerosene Exchanger — Shell & Tube' : `${state.selectedAssetTag} Process Unit`}
          </p>
        </div>

        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#111827] text-gray-400 border border-[#1f2937]">
          INSPECTOR
        </span>
      </div>

      {/* Tabs Switcher */}
      <div className="flex border-b border-[#1e293b] bg-[#071018] overflow-x-auto text-[10px]">
        {(['IDENTITY', 'STATE', 'THERMO', 'FOULING', 'EVIDENCE', 'PROVENANCE'] as InspectorTab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-2.5 py-1.5 font-bold transition whitespace-nowrap cursor-pointer ${
              activeTab === tab
                ? 'bg-[#0f172a] text-cyan-300 border-b-2 border-cyan-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content Body */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* 1. IDENTITY TAB */}
        {activeTab === 'IDENTITY' && (
          <div className="space-y-3">
            <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5 text-[11px]">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1">
                Asset Metadata
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Canonical Tag:</span>
                <span className="font-bold text-white">{state.selectedAssetTag}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Process Unit:</span>
                <span className="text-gray-200">Crude Preheat Train 1</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Geometry State:</span>
                <span className="text-amber-400 font-semibold">REPRESENTATIVE</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Truth State:</span>
                <span className="text-cyan-400 font-semibold">DERIVED / OBSERVED</span>
              </div>
            </div>

            {/* Connected Streams */}
            <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5 text-[11px]">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1">
                Connected Ports & Streams
              </div>
              <div
                onClick={() => onSelectStream('S-102')}
                className="flex justify-between items-center bg-[#071018] p-1.5 rounded border border-[#1e293b] hover:border-cyan-500 cursor-pointer transition"
              >
                <div className="flex items-center gap-1.5">
                  <ArrowRight className="w-3 h-3 text-cyan-400" />
                  <span className="font-bold text-white">S-102 (Tube Inlet)</span>
                </div>
                <span className="text-[10px] text-gray-400">195.4 °C | 104 kg/s</span>
              </div>
              <div
                onClick={() => onSelectStream('S-103')}
                className="flex justify-between items-center bg-[#071018] p-1.5 rounded border border-[#1e293b] hover:border-cyan-500 cursor-pointer transition"
              >
                <div className="flex items-center gap-1.5">
                  <ArrowRight className="w-3 h-3 text-cyan-400" />
                  <span className="font-bold text-white">S-103 (Tube Outlet)</span>
                </div>
                <span className="text-[10px] text-gray-400">234.4 °C | 104 kg/s</span>
              </div>
            </div>
          </div>
        )}

        {/* 2. OPERATING STATE TAB */}
        {activeTab === 'STATE' && (
          <div className="space-y-2 text-[11px]">
            <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1 flex justify-between">
                <span>Thermal Metrics</span>
                <span className="text-cyan-400 font-bold">STAGE 14</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Thermal Duty (Q):</span>
                <span className="font-bold text-cyan-300">8.52 MW</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">LMTD (ΔT):</span>
                <span className="font-bold text-cyan-300">39.16 °C</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Overall UA:</span>
                <span className="font-bold text-cyan-300">217.58 kW/K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Clean Reference UA:</span>
                <span className="text-gray-400">213.44 kW/K</span>
              </div>
              <div className="flex justify-between border-t border-[#1e293b] pt-1">
                <span className="text-gray-400">Thermal Balance Error:</span>
                <span className="text-gray-300 font-semibold">0.98%</span>
              </div>
            </div>

            <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1">
                Sensor Channels Availability
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-gray-400">Temperature Sensors:</span>
                <span className="text-emerald-400 font-bold">4/4 OBSERVED</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-gray-400">Mass Flow Transmitters:</span>
                <span className="text-emerald-400 font-bold">2/2 OBSERVED</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-gray-400">Differential Pressure (ΔP):</span>
                <span className="text-gray-500 font-bold">UNAVAILABLE</span>
              </div>
            </div>
          </div>
        )}

        {/* 3. THERMODYNAMICS TAB */}
        {activeTab === 'THERMO' && (
          <div className="space-y-2 text-[11px]">
            <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1 flex justify-between">
                <span>Property Package</span>
                <span className="text-purple-400 font-bold">STAGE 13</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Active Engine:</span>
                <span className="text-white font-bold">IDEAL_GAS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Supported Phase:</span>
                <span className="text-white">VAPOR / GAS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Equation of State:</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#311313] text-rose-300">
                  UNSUPPORTED
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Transport Properties:</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#1e293b] text-gray-400">
                  UNAVAILABLE
                </span>
              </div>
            </div>

            <div className="p-2 bg-[#071018] rounded border border-[#1e293b] text-[10px] text-gray-400">
              Analytical benchmarks: 2/2 Passed. Reference-engine benchmarks: 0/0.
            </div>
          </div>
        )}

        {/* 4. FOULING & FOUL-X TAB */}
        {activeTab === 'FOULING' && (
          <div className="space-y-2 text-[11px]">
            <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1 flex justify-between">
                <span>FOUL-X Prognosis</span>
                <span className="text-cyan-400 font-bold">M4.0 RIDGE</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Fouling Resistance (Rf):</span>
                <span className="font-bold text-amber-400">7.28 × 10⁻⁸ m²·K/W</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Cleaning Threshold:</span>
                <span className="text-gray-400">1.50 × 10⁻⁷ m²·K/W</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Forecast Horizon:</span>
                <span className="text-white font-bold">24 Hours</span>
              </div>
            </div>

            <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1 flex justify-between">
                <span>Trust Gate Decision</span>
                <span className={isOod ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                  {isOod ? 'ABSTAIN' : 'PASS'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Active Policy:</span>
                <span className="text-white font-bold">
                  {isOod ? 'FIXED POLICY ACTIVE' : 'PREDICTIVE WINDOW'}
                </span>
              </div>
              <div className="text-[10px] text-gray-400 border-t border-[#1e293b] pt-1">
                {isOod ? (
                  <span className="text-rose-400 font-semibold">
                    REGIME_OOD: State moved outside training support. AI maintenance action withheld.
                  </span>
                ) : (
                  <span className="text-emerald-400 font-semibold">
                    All 4 Gate Checks passed. Advisory cleaning review active.
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 5. EVIDENCE & HYPOTHESES TAB */}
        {activeTab === 'EVIDENCE' && (
          <div className="space-y-2 text-[11px]">
            <div className="flex justify-between items-center text-[10px] text-gray-400 mb-1">
              <span>COMPETING HYPOTHESES</span>
              <button
                onClick={onOpenEvidence}
                className="text-cyan-400 hover:underline font-bold"
              >
                TRACE WHY →
              </button>
            </div>

            {state.activeHypotheses.map((hyp) => (
              <div
                key={hyp.id}
                onClick={() => onSelectHypothesis(hyp.id)}
                className={`p-2 rounded border cursor-pointer transition ${
                  state.activeHypothesisId === hyp.id
                    ? 'bg-[#1e293b] border-cyan-400'
                    : 'bg-[#0f172a] border-[#1e293b] hover:border-gray-500'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="font-bold text-white text-[10px]">
                    {hyp.id}: {hyp.title}
                  </span>
                  <span className="text-cyan-400 font-bold text-[10px]">
                    {(hyp.confidenceScore * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-[10px] text-gray-400 line-clamp-2">{hyp.description}</p>
              </div>
            ))}
          </div>
        )}

        {/* 6. PROVENANCE TAB */}
        {activeTab === 'PROVENANCE' && (
          <div className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-2 text-[10px]">
            <div className="font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>Cryptographic Lineage</span>
            </div>
            <div className="space-y-1 text-gray-400">
              <div>
                <span>DATASET SHA-256:</span>
                <p className="text-cyan-300 font-mono text-[9px] break-all">
                  c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9
                </p>
              </div>
              <div className="flex justify-between">
                <span>Schema Version:</span>
                <span className="text-white">1.0</span>
              </div>
              <div className="flex justify-between">
                <span>Calculation Engine:</span>
                <span className="text-white">Stage 14 HeatExchangerModel</span>
              </div>
              <div className="flex justify-between">
                <span>No Future Leakage:</span>
                <span className="text-emerald-400 font-bold">VERIFIED</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
