import React from 'react';
import type { InspectionMode } from '../../types/plant';
import { ShieldCheck, ShieldAlert, Cpu, Eye, Play, Pause, RotateCcw, FileText, Database, FileCode, BarChart3, FlaskConical, Globe } from 'lucide-react';
import { TRANSLATIONS } from '../../data/translations';
import type { Language } from '../../data/translations';

interface PlantHeaderProps {
  selectedAssetTag: string;
  inspectionMode: InspectionMode;
  setInspectionMode: (mode: InspectionMode) => void;
  scenario: 'normal' | 'disturbed';
  setScenario: (scen: 'normal' | 'disturbed') => void;
  isPlaying: boolean;
  setIsPlaying: (playing: boolean) => void;
  timeHr: number;
  resetReplay: () => void;
  openTrustGate: () => void;
  openIntake: () => void;
  openBlueprint: () => void;
  openProvenance: () => void;
  openBenchmark: () => void;
  openChemistry: () => void;
  lang: Language;
  setLang: (lang: Language) => void;
}

export const PlantHeader: React.FC<PlantHeaderProps> = ({
  inspectionMode,
  setInspectionMode,
  scenario,
  setScenario,
  isPlaying,
  setIsPlaying,
  timeHr,
  resetReplay,
  openTrustGate,
  openIntake,
  openBlueprint,
  openProvenance,
  openBenchmark,
  openChemistry,
  lang,
  setLang,
}) => {
  const t = TRANSLATIONS[lang];
  return (
    <header className="bg-[#071018] border-b border-[#15212d] px-4 py-2 flex flex-col xl:flex-row items-center justify-between gap-3 text-xs z-20 sticky top-0 shadow-lg">
      {/* Brand & System Title */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 bg-[#0b1118] px-2.5 py-1.5 rounded border border-[#1b2a3a]">
          <Cpu className="w-4 h-4 text-[#27b7e8]" />
          <div className="flex flex-col">
            <span className="font-extrabold tracking-widest text-white text-xs leading-none">FOUL-X</span>
            <span className="text-[9px] text-[#27b7e8] font-mono leading-none mt-0.5 uppercase">TRUST-GATED PROGNOSIS</span>
          </div>
        </div>

        <div>
          <h1 className="text-xs font-bold text-white tracking-wide uppercase flex items-center gap-2">
            <span>Industrial Process Intelligence</span>
            <span className="text-[#6b7280] font-normal text-[10px]">— Crude Preheat Train</span>
          </h1>
          <p className="text-[10px] text-[#6b7280]">
            REPRESENTATIVE PROCESS TOPOLOGY — NOT A PROPRIETARY PLANT BLUEPRINT
          </p>
        </div>
      </div>

      {/* Judging & Exploration Toolbar */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Inspection Mode View Selector */}
        <div className="flex items-center bg-[#0b1118] p-1 rounded border border-[#15212d] gap-1">
          <span className="text-[10px] text-[#6b7280] font-bold px-1.5 flex items-center gap-1">
            <Eye className="w-3 h-3 text-[#27b7e8]" /> VIEW:
          </span>
          {(['NORMAL', 'CUTAWAY', 'PROCESS'] as InspectionMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setInspectionMode(mode)}
              className={`px-2 py-0.5 text-[10px] font-bold font-mono rounded transition cursor-pointer ${
                inspectionMode === mode
                  ? 'bg-[#1e293b] text-[#27b7e8] border border-[#27b7e8]'
                  : 'text-[#9ca3af] hover:text-white'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>

        {/* Trust Gate Killer Visual Launcher */}
        <button
          onClick={openTrustGate}
          className={`px-2.5 py-1.5 rounded text-[10px] font-bold font-mono border flex items-center gap-1.5 transition cursor-pointer ${
            scenario === 'normal'
              ? 'bg-[#064e3b]/80 border-[#10b981] text-[#6ee7b7] hover:bg-[#064e3b]'
              : 'bg-[#7f1d1d]/80 border-[#ef4444] text-[#fca5a5] hover:bg-[#7f1d1d]'
          }`}
          title="Open Dominant Trust Gate Flow Visualization"
        >
          {scenario === 'normal' ? <ShieldCheck className="w-3.5 h-3.5 text-[#34d399]" /> : <ShieldAlert className="w-3.5 h-3.5 text-[#ef4444]" />}
          <span>TRUST GATE VISUAL</span>
        </button>

        {/* Industrial Intake Portal */}
        <button
          onClick={openIntake}
          className="px-2.5 py-1.5 bg-[#0b1118] hover:bg-[#15212d] border border-[#1b2a3a] text-white rounded text-[10px] font-bold font-mono flex items-center gap-1.5 transition cursor-pointer"
          title="Open Industrial Plant Evidence Intake Portal"
        >
          <FileText className="w-3.5 h-3.5 text-[#27b7e8]" />
          <span>PLANT INTAKE</span>
        </button>

        {/* Process Blueprint */}
        <button
          onClick={openBlueprint}
          className="px-2.5 py-1.5 bg-[#0b1118] hover:bg-[#15212d] border border-[#1b2a3a] text-white rounded text-[10px] font-bold font-mono flex items-center gap-1.5 transition cursor-pointer"
          title="Open Process Blueprint / P&ID Context"
        >
          <FileCode className="w-3.5 h-3.5 text-[#a78bfa]" />
          <span>BLUEPRINT</span>
        </button>

        {/* Model Provenance */}
        <button
          onClick={openProvenance}
          className="px-2.5 py-1.5 bg-[#0b1118] hover:bg-[#15212d] border border-[#1b2a3a] text-white rounded text-[10px] font-bold font-mono flex items-center gap-1.5 transition cursor-pointer"
          title="Open Model Training & Dataset Provenance Panel"
        >
          <Database className="w-3.5 h-3.5 text-[#fbbf24]" />
          <span>PROVENANCE</span>
        </button>

        {/* Chemistry Demo */}
        <button
          onClick={openChemistry}
          className="px-2.5 py-1.5 bg-[#0b1118] hover:bg-[#15212d] border border-[#1b2a3a] text-[#38bdf8] rounded text-[10px] font-bold font-mono flex items-center gap-1.5 transition cursor-pointer"
          title="Open Process Chemistry & Thermodynamic Simulation"
        >
          <FlaskConical className="w-3.5 h-3.5 text-[#38bdf8]" />
          <span>{t.chemistryDemo}</span>
        </button>

        {/* Benchmark Results */}
        <button
          onClick={openBenchmark}
          className="px-2.5 py-1.5 bg-[#0b1118] hover:bg-[#15212d] border border-[#1b2a3a] text-white rounded text-[10px] font-bold font-mono flex items-center gap-1.5 transition cursor-pointer"
          title="Open Validated M4.0 & M7 Benchmark Panel"
        >
          <BarChart3 className="w-3.5 h-3.5 text-[#34d399]" />
          <span>{t.benchmark}</span>
        </button>

        {/* Language Switcher */}
        <div className="flex items-center bg-[#0b1118] px-2 py-1 rounded border border-[#1b2a3a] gap-1.5 text-[10px] font-bold font-mono text-[#27b7e8]">
          <Globe className="w-3.5 h-3.5 text-[#27b7e8]" />
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as Language)}
            className="bg-transparent text-white font-bold cursor-pointer outline-none text-[10px]"
          >
            <option value="en" className="bg-[#071018] text-white">English (EN)</option>
            <option value="ta" className="bg-[#071018] text-white">தமிழ் (TA)</option>
            <option value="hi" className="bg-[#071018] text-white">हिन्दी (HI)</option>
          </select>
        </div>

        {/* Replay Controls */}
        <div className="flex items-center bg-[#0b1118] px-2 py-1 rounded border border-[#15212d] gap-2 font-mono text-[11px]">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-1 rounded hover:bg-[#1b2a3a] text-[#27b7e8] cursor-pointer transition"
            title={isPlaying ? 'Pause Replay' : 'Play Replay'}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={resetReplay}
            className="p-1 rounded hover:bg-[#1b2a3a] text-[#9ca3af] cursor-pointer transition"
            title="Reset Replay"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <span className="text-[#6b7280]">TIME:</span>
          <span className="font-bold text-white">{timeHr.toLocaleString()} h</span>
        </div>

        {/* Scenario Toggle */}
        <div className="flex items-center bg-[#0b1118] p-1 rounded border border-[#15212d] gap-1">
          <button
            onClick={() => setScenario('normal')}
            className={`px-2 py-1 text-[10px] font-bold font-mono rounded transition cursor-pointer flex items-center gap-1 ${
              scenario === 'normal'
                ? 'bg-[#065f46] text-[#6ee7b7] border border-[#10b981]'
                : 'text-[#6b7280] hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3 h-3" />
            NORMAL
          </button>

          <button
            onClick={() => setScenario('disturbed')}
            className={`px-2 py-1 text-[10px] font-bold font-mono rounded transition cursor-pointer flex items-center gap-1 ${
              scenario === 'disturbed'
                ? 'bg-[#7f1d1d] text-[#fca5a5] border border-[#ef4444]'
                : 'text-[#6b7280] hover:text-white'
            }`}
          >
            <ShieldAlert className="w-3 h-3" />
            +6σ STRESS
          </button>
        </div>
      </div>
    </header>
  );
};
