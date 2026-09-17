import React, { useEffect, useState } from 'react';
import type { ExchangerState, PageView, ScenarioMode } from '../../types/foulx';
import { apiService } from '../../services/api';
import { DecisionPanel } from '../common/DecisionPanel';
import { Activity, ArrowRight, Layers, Gauge, Database } from 'lucide-react';

interface OverviewPageProps {
  setActivePage: (page: PageView) => void;
  setSelectedExchanger: (tag: string) => void;
  scenario: ScenarioMode;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ setActivePage, setSelectedExchanger, scenario }) => {
  const [exchangers, setExchangers] = useState<Record<string, ExchangerState>>({});

  useEffect(() => {
    apiService.setScenario(scenario);
    apiService.getExchangers().then(setExchangers);
  }, [scenario]);

  const list = Object.values(exchangers);

  return (
    <div className="space-y-6">
      {/* Top Banner / Decision Panel */}
      <DecisionPanel scenario={scenario} />

      {/* Control Room Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
        <div className="bg-[#11151e] p-3.5 rounded border border-[#1e2638] space-y-1">
          <div className="flex items-center justify-between text-[#6b7280]">
            <span className="uppercase font-bold tracking-wider text-[10px]">MONITORED EXCHANGERS</span>
            <Layers className="w-4 h-4 text-[#38bdf8]" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">5 / 5</div>
          <div className="text-[11px] text-[#34d399]">100% Telemetry Online</div>
        </div>

        <div className="bg-[#11151e] p-3.5 rounded border border-[#1e2638] space-y-1">
          <div className="flex items-center justify-between text-[#6b7280]">
            <span className="uppercase font-bold tracking-wider text-[10px]">DATA QUALITY INDEX</span>
            <Database className="w-4 h-4 text-[#10b981]" />
          </div>
          <div className="text-2xl font-bold font-mono text-[#34d399]">99.96%</div>
          <div className="text-[11px] text-[#9ca3af]">0 Missing Historian Values</div>
        </div>

        <div className="bg-[#11151e] p-3.5 rounded border border-[#1e2638] space-y-1">
          <div className="flex items-center justify-between text-[#6b7280]">
            <span className="uppercase font-bold tracking-wider text-[10px]">PHYSICS STATE VERIFIED</span>
            <Gauge className="w-4 h-4 text-[#fbbf24]" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">VALIDATED</div>
          <div className="text-[11px] text-[#9ca3af]">Deterministic LMTD & UA Estimator</div>
        </div>

        <div className="bg-[#11151e] p-3.5 rounded border border-[#1e2638] space-y-1">
          <div className="flex items-center justify-between text-[#6b7280]">
            <span className="uppercase font-bold tracking-wider text-[10px]">FORECAST ENGINE</span>
            <Activity className="w-4 h-4 text-[#a78bfa]" />
          </div>
          <div className="text-2xl font-bold font-mono text-[#a78bfa]">M4.0 RIDGE</div>
          <div className="text-[11px] text-[#38bdf8]">+25.4% MAE Impr. vs Pers.</div>
        </div>
      </div>

      {/* Heat Exchanger Train Grid */}
      <div className="bg-[#11151e] rounded border border-[#1e2638] overflow-hidden">
        <div className="px-4 py-3 bg-[#161c28] border-b border-[#1e2638] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#38bdf8]" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-white">
              CRUDE PREHEAT TRAIN FOULING OVERVIEW (E01 – E05)
            </h2>
          </div>
          <span className="text-[10px] text-[#6b7280]">Click any exchanger to view deep telemetry & forecast</span>
        </div>

        <div className="divide-y divide-[#182030] text-xs">
          {list.map((ex) => {
            const isDegraded = ex.status === 'DEGRADATION_DETECTED';
            return (
              <div 
                key={ex.tag}
                onClick={() => {
                  setSelectedExchanger(ex.tag);
                  setActivePage('exchangers');
                }}
                className="p-4 hover:bg-[#161e2e] transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                {/* Exchanger Header */}
                <div className="flex items-start gap-3 md:w-1/3">
                  <div className={`p-2 rounded border font-mono font-bold text-xs ${
                    isDegraded 
                      ? 'bg-[#311313] border-[#7f1d1d] text-[#f87171]' 
                      : 'bg-[#152238] border-[#253552] text-[#38bdf8]'
                  }`}>
                    {ex.tag}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-xs">{ex.name}</h3>
                    <p className="text-[11px] text-[#6b7280]">{ex.serviceName}</p>
                  </div>
                </div>

                {/* Thermodynamic Metrics */}
                <div className="grid grid-cols-3 gap-6 md:w-1/3 font-mono">
                  <div>
                    <span className="text-[10px] text-[#6b7280] block">CURRENT R_f</span>
                    <span className={`font-bold ${ex.rfCurrent > 1e-7 ? 'text-[#f87171]' : 'text-white'}`}>
                      {ex.rfCurrent.toExponential(4)}
                    </span>
                  </div>

                  <div>
                    <span className="text-[10px] text-[#6b7280] block">UA (W/K)</span>
                    <span className="font-bold text-white">{ex.uaCurrent.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                  </div>

                  <div>
                    <span className="text-[10px] text-[#6b7280] block">THERMAL ERR</span>
                    <span className="font-bold text-[#34d399]">{(ex.thermalDiscrepancy * 100).toFixed(2)}%</span>
                  </div>
                </div>

                {/* Status & CTA */}
                <div className="flex items-center justify-between md:justify-end gap-4 md:w-1/3">
                  <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider border ${
                    isDegraded
                      ? 'bg-[#311313] text-[#f87171] border-[#7f1d1d]'
                      : 'bg-[#102a1d] text-[#34d399] border-[#065f46]'
                  }`}>
                    {ex.status}
                  </span>

                  <button className="flex items-center gap-1 text-[11px] text-[#38bdf8] font-bold hover:underline">
                    <span>INSPECT</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
