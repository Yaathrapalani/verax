import React, { useEffect, useState } from 'react';
import type { ExchangerState, ScenarioMode } from '../../types/foulx';
import { apiService } from '../../services/api';
import { Thermometer } from 'lucide-react';

interface ExchangersPageProps {
  selectedExchanger: string;
  setSelectedExchanger: (tag: string) => void;
  scenario: ScenarioMode;
}

export const ExchangersPage: React.FC<ExchangersPageProps> = ({ selectedExchanger, setSelectedExchanger, scenario }) => {
  const [exchangers, setExchangers] = useState<Record<string, ExchangerState>>({});

  useEffect(() => {
    apiService.setScenario(scenario);
    apiService.getExchangers().then(setExchangers);
  }, [scenario]);

  const currentExchanger = exchangers[selectedExchanger] || exchangers.E01;

  if (!currentExchanger) {
    return <div className="p-8 text-center text-[#9ca3af]">Loading Exchanger State...</div>;
  }

  const tagList = ['E01', 'E02', 'E03', 'E04', 'E05'];

  return (
    <div className="space-y-6 text-xs">
      {/* Exchanger Selector Tabs */}
      <div className="flex items-center gap-2 bg-[#11151e] p-2 rounded border border-[#1e2638] overflow-x-auto">
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#6b7280] px-2">SELECT EXCHANGER:</span>
        {tagList.map((tag) => {
          const isSelected = selectedExchanger === tag;
          const ex = exchangers[tag];
          const isDegraded = ex?.status === 'DEGRADATION_DETECTED';
          return (
            <button
              key={tag}
              onClick={() => setSelectedExchanger(tag)}
              className={`px-3 py-1.5 rounded font-mono font-bold transition cursor-pointer flex items-center gap-2 ${
                isSelected
                  ? 'bg-[#1e293b] text-[#38bdf8] border border-[#0284c7]'
                  : 'bg-[#161c28] text-[#9ca3af] hover:text-white border border-[#232c3d]'
              }`}
            >
              <span>{tag}</span>
              {isDegraded && <span className="w-2 h-2 rounded-full bg-[#f87171] animate-pulse"></span>}
            </button>
          );
        })}
      </div>

      {/* Main Exchanger Header Detail */}
      <div className="bg-[#11151e] p-5 rounded border border-[#1e2638] space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#182030] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-[#1c273c] text-[#38bdf8] font-mono font-bold text-xs border border-[#2d3f60]">
                {currentExchanger.tag}
              </span>
              <h1 className="text-base font-bold text-white">{currentExchanger.name}</h1>
            </div>
            <p className="text-xs text-[#6b7280] mt-1">{currentExchanger.serviceName}</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-[#6b7280]">STATUS:</span>
            <span className={`px-3 py-1 rounded text-xs font-bold uppercase tracking-wider border ${
              currentExchanger.status === 'DEGRADATION_DETECTED'
                ? 'bg-[#311313] text-[#f87171] border-[#7f1d1d]'
                : 'bg-[#102a1d] text-[#34d399] border-[#065f46]'
            }`}>
              {currentExchanger.status}
            </span>
          </div>
        </div>

        {/* Core Thermodynamic Telemetry Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-[#161c28] p-3.5 rounded border border-[#212b3e] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#6b7280]">DERIVED FOULING (R_f)</span>
            <div className="text-lg font-bold font-mono text-white">
              {currentExchanger.rfCurrent.toExponential(4)}
            </div>
            <span className="text-[10px] text-[#6b7280]">m²·K/W (Derived State)</span>
          </div>

          <div className="bg-[#161c28] p-3.5 rounded border border-[#212b3e] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#6b7280]">OVERALL HEAT TRANSFER (UA)</span>
            <div className="text-lg font-bold font-mono text-white">
              {currentExchanger.uaCurrent.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </div>
            <span className="text-[10px] text-[#34d399]">Clean Baseline: {currentExchanger.uaClean.toLocaleString(undefined, { maximumFractionDigits: 0 })} W/K</span>
          </div>

          <div className="bg-[#161c28] p-3.5 rounded border border-[#212b3e] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#6b7280]">LMTD (ΔT_lm)</span>
            <div className="text-lg font-bold font-mono text-white">
              {currentExchanger.lmtdCurrent.toFixed(2)} °C
            </div>
            <span className="text-[10px] text-[#6b7280]">Counter-Current Verified</span>
          </div>

          <div className="bg-[#161c28] p-3.5 rounded border border-[#212b3e] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#6b7280]">HEAT DUTY (Q_tube)</span>
            <div className="text-lg font-bold font-mono text-[#38bdf8]">
              {(currentExchanger.qTubeCurrent / 1e6).toFixed(3)} MW
            </div>
            <span className="text-[10px] text-[#34d399]">Thermal Err: {(currentExchanger.thermalDiscrepancy * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>

      {/* Stream Process Conditions & Design Parameters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#11151e] p-4 rounded border border-[#1e2638] space-y-3">
          <div className="flex items-center gap-2 border-b border-[#182030] pb-2 text-[#38bdf8]">
            <Thermometer className="w-4 h-4" />
            <h3 className="font-bold uppercase tracking-wider text-xs text-white">TUBE-SIDE PROCESS STREAM (CRUDE)</h3>
          </div>
          <div className="grid grid-cols-2 gap-4 font-mono">
            <div>
              <span className="text-[#6b7280] block text-[10px]">TUBE INLET TEMP</span>
              <span className="font-bold text-white">150.8 °C</span>
            </div>
            <div>
              <span className="text-[#6b7280] block text-[10px]">TUBE OUTLET TEMP</span>
              <span className="font-bold text-white">195.6 °C</span>
            </div>
            <div>
              <span className="text-[#6b7280] block text-[10px]">MASS FLOW RATE</span>
              <span className="font-bold text-white">98.63 kg/s</span>
            </div>
            <div>
              <span className="text-[#6b7280] block text-[10px]">HEAT CAPACITY (Cp)</span>
              <span className="font-bold text-white">2100 J/(kg·K)</span>
            </div>
          </div>
        </div>

        <div className="bg-[#11151e] p-4 rounded border border-[#1e2638] space-y-3">
          <div className="flex items-center gap-2 border-b border-[#182030] pb-2 text-[#fbbf24]">
            <Thermometer className="w-4 h-4" />
            <h3 className="font-bold uppercase tracking-wider text-xs text-white">SHELL-SIDE PROCESS STREAM ({currentExchanger.serviceName.split('/')[0].toUpperCase()})</h3>
          </div>
          <div className="grid grid-cols-2 gap-4 font-mono">
            <div>
              <span className="text-[#6b7280] block text-[10px]">SHELL INLET TEMP</span>
              <span className="font-bold text-white">249.5 °C</span>
            </div>
            <div>
              <span className="text-[#6b7280] block text-[10px]">SHELL OUTLET TEMP</span>
              <span className="font-bold text-white">188.2 °C</span>
            </div>
            <div>
              <span className="text-[#6b7280] block text-[10px]">MASS FLOW RATE</span>
              <span className="font-bold text-white">80.27 kg/s</span>
            </div>
            <div>
              <span className="text-[#6b7280] block text-[10px]">HEAT CAPACITY (Cp)</span>
              <span className="font-bold text-white">1900 J/(kg·K)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
