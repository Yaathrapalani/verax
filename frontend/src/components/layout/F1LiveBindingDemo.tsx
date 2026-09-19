import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, AlertTriangle, ShieldCheck, Server } from 'lucide-react';
import { apiClient } from '../../api/client';
import type { ReplaySnapshotDTO, ApiStatus } from '../../api/types';

export const F1LiveBindingDemo: React.FC = () => {
  const [timeHr, setTimeHr] = useState<number>(63241);
  const [exchangerId, setExchangerId] = useState<string>('E02');
  const [scenario, setScenario] = useState<'NORMAL' | 'SHIFTED'>('NORMAL');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  
  const [apiStatus, setApiStatus] = useState<ApiStatus>('LOADING');
  const [snapshot, setSnapshot] = useState<ReplaySnapshotDTO | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [datasetSha, setDatasetSha] = useState<string>('c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9');

  // Hydrate state from FastAPI backend endpoint
  const loadBackendSnapshot = async (tHr: number, exId: string, scen: 'NORMAL' | 'SHIFTED') => {
    setApiStatus('LOADING');
    const res = await apiClient.fetchSnapshot(tHr, exId, scen);
    if (res.status === 'SUCCESS' && res.data) {
      setSnapshot(res.data);
      setApiStatus('SUCCESS');
      setErrorMessage(null);
      if (res.data.provenance?.dataset_checksum) {
        setDatasetSha(res.data.provenance.dataset_checksum);
      }
    } else {
      setSnapshot(null);
      setApiStatus(res.status);
      setErrorMessage(res.error || 'Failed to connect to backend server');
    }
  };

  useEffect(() => {
    loadBackendSnapshot(timeHr, exchangerId, scenario);
  }, [timeHr, exchangerId, scenario]);

  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimeHr((prev) => (prev >= 63300 ? 63200 : prev + 1));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="bg-[#0b1019] border border-[#1e293b] rounded-sm p-4 text-[#d1d5db] font-mono select-none">
      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1e293b] pb-3 mb-4 text-xs">
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-[#38bdf8]" />
          <span className="font-bold text-white uppercase tracking-wider">F1 Live Computational Plant Binding</span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
            apiStatus === 'SUCCESS' ? 'bg-[#064e3b] text-[#34d399] border border-[#059669]' :
            apiStatus === 'LOADING' ? 'bg-[#1e293b] text-[#94a3b8]' :
            'bg-[#7f1d1d] text-[#fca5a5] border border-[#dc2626]'
          }`}>
            {apiStatus === 'SUCCESS' ? 'LIVE BACKEND CONNECTED' : apiStatus}
          </span>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center gap-1 bg-[#1e293b] hover:bg-[#334155] text-white px-2.5 py-1 rounded text-xs border border-[#475569] transition"
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5 text-amber-400" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
            {isPlaying ? 'PAUSE' : 'REPLAY'}
          </button>
          
          <button
            onClick={() => { setTimeHr(63241); setScenario('NORMAL'); }}
            className="flex items-center gap-1 bg-[#1e293b] hover:bg-[#334155] text-gray-300 px-2 py-1 rounded text-xs border border-[#475569]"
          >
            <RotateCcw className="w-3.5 h-3.5" /> RESET
          </button>

          <select
            value={exchangerId}
            onChange={(e) => setExchangerId(e.target.value)}
            className="bg-[#0f172a] border border-[#334155] text-white px-2 py-1 rounded text-xs"
          >
            <option value="E01">E-101 (Heavy Naphtha)</option>
            <option value="E02">E-102 (Kerosene)</option>
            <option value="E03">E-103 (Light Diesel)</option>
            <option value="E04">E-104 (LVGO)</option>
            <option value="E05">E-105 (Heavy Diesel)</option>
          </select>

          <button
            onClick={() => setScenario(scenario === 'NORMAL' ? 'SHIFTED' : 'NORMAL')}
            className={`px-2.5 py-1 rounded text-xs font-bold border transition ${
              scenario === 'SHIFTED'
                ? 'bg-[#7f1d1d] text-white border-[#ef4444]'
                : 'bg-[#064e3b] text-emerald-200 border-[#10b981]'
            }`}
          >
            {scenario === 'SHIFTED' ? '+6σ REGIME SHIFT' : 'NORMAL REGIME'}
          </button>
        </div>
      </div>

      {/* Snapshot Content Grid */}
      {apiStatus === 'SUCCESS' && snapshot ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Col 1: Physics State */}
          <div className="bg-[#0f172a] border border-[#1e293b] p-3 rounded">
            <div className="text-[11px] font-bold text-[#94a3b8] uppercase mb-2 border-b border-[#1e293b] pb-1 flex justify-between">
              <span>Stage 14 Heat Exchanger Physics</span>
              <span className="text-emerald-400">OBSERVED / DERIVED</span>
            </div>
            <div className="space-y-1.5 text-gray-300">
              <div className="flex justify-between">
                <span className="text-gray-400">Exchanger Tag:</span>
                <span className="font-bold text-white">{snapshot.exchanger_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Duty Q:</span>
                <span className="font-bold text-cyan-400">{(snapshot.physics_state.thermal.q_tube / 1e6).toFixed(2)} MW</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">LMTD ΔT:</span>
                <span className="font-bold text-cyan-400">{snapshot.physics_state.thermal.lmtd.toFixed(1)} °C</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">UA Coefficient:</span>
                <span className="font-bold text-cyan-400">{(snapshot.physics_state.thermal.ua / 1e3).toFixed(1)} kW/K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Fouling Resistance (Rf):</span>
                <span className="font-bold text-amber-400">{(snapshot.physics_state.fouling.rf_derived * 1e4).toFixed(4)} × 10⁻⁴ m²K/W</span>
              </div>
              <div className="flex justify-between border-t border-[#1e293b] pt-1">
                <span className="text-gray-400">Thermal Error:</span>
                <span className="text-gray-300">{(snapshot.physics_state.thermal.thermal_balance_error * 100).toFixed(2)}%</span>
              </div>
            </div>
          </div>

          {/* Col 2: FOUL-X Trust Gate */}
          <div className="bg-[#0f172a] border border-[#1e293b] p-3 rounded">
            <div className="text-[11px] font-bold text-[#94a3b8] uppercase mb-2 border-b border-[#1e293b] pb-1 flex justify-between">
              <span>Stage 7 Reliability Gate</span>
              <span className={snapshot.reliability_state.status === 'PASS' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
                {snapshot.reliability_state.status}
              </span>
            </div>
            <div className="space-y-1.5 text-gray-300">
              <div className="flex justify-between">
                <span className="text-gray-400">Gate Decision:</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  snapshot.reliability_state.status === 'PASS'
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    : 'bg-amber-950 text-amber-300 border border-amber-700'
                }`}>
                  {snapshot.reliability_state.status === 'PASS' ? 'PASS — TRUSTED' : 'ABSTAIN — OOD DETECTED'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Active Policy:</span>
                <span className="text-gray-200 font-semibold">
                  {snapshot.reliability_state.status === 'PASS' ? 'PREDICTIVE CLEANING' : 'FIXED POLICY ACTIVE'}
                </span>
              </div>
              <div className="text-[10px] text-gray-400 border-t border-[#1e293b] pt-1 mt-2">
                {snapshot.reliability_state.status === 'PASS' ? (
                  <span className="text-emerald-400 flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5" /> All 4 Gate Checks PASSED cleanly</span>
                ) : (
                  <span className="text-amber-400 flex items-center gap-1"><AlertTriangle className="w-3.5 h-3.5" /> REGIME_OOD: AI Recommendation Withheld</span>
                )}
              </div>
            </div>
          </div>

          {/* Col 3: Stage 13 Thermo & System Provenance */}
          <div className="bg-[#0f172a] border border-[#1e293b] p-3 rounded">
            <div className="text-[11px] font-bold text-[#94a3b8] uppercase mb-2 border-b border-[#1e293b] pb-1 flex justify-between">
              <span>Stage 13 Thermo & Lineage</span>
              <span className="text-purple-400 font-bold">IDEAL_GAS</span>
            </div>
            <div className="space-y-1.5 text-gray-300">
              <div className="flex justify-between">
                <span className="text-gray-400">Property Package:</span>
                <span className="text-white">IDEAL_GAS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Equation of State:</span>
                <span className="text-gray-500 font-bold">UNSUPPORTED</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Transport Props:</span>
                <span className="text-gray-500 font-bold">UNAVAILABLE</span>
              </div>
              <div className="flex justify-between border-t border-[#1e293b] pt-1">
                <span className="text-gray-400">Dataset SHA-256:</span>
                <span className="text-xs font-mono text-cyan-400">{datasetSha.slice(0, 12)}...</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-6 bg-[#0f172a] border border-red-900 rounded text-center text-red-400 text-xs">
          <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-red-400" />
          <p className="font-bold mb-1">Backend Connection Error</p>
          <p className="text-gray-400">{errorMessage || 'Ensure FastAPI backend is running on http://localhost:8000'}</p>
        </div>
      )}
    </div>
  );
};
