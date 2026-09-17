import React from 'react';
import type { PageView, ScenarioMode } from '../../types/foulx';
import { Shield, Cpu, HelpCircle } from 'lucide-react';

interface HeaderProps {
  activePage: PageView;
  setActivePage: (page: PageView) => void;
  scenario: ScenarioMode;
  setScenario: (scenario: ScenarioMode) => void;
}

export const Header: React.FC<HeaderProps> = ({ activePage, setActivePage, scenario, setScenario }) => {
  const navItems: { id: PageView; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'exchangers', label: 'Exchangers' },
    { id: 'forecast', label: 'Forecast' },
    { id: 'reliability', label: 'Reliability' },
    { id: 'evidence', label: 'Evidence' },
  ];

  return (
    <header className="bg-[#0f1218] border-b border-[#1f293d] sticky top-0 z-50">
      {/* Top Banner Status Bar */}
      <div className="max-w-[1600px] mx-auto px-4 py-2 flex flex-wrap items-center justify-between gap-4 text-xs border-b border-[#181e2b]">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-[#182030] px-2.5 py-1 rounded border border-[#2d3a54]">
            <Cpu className="w-4 h-4 text-[#38bdf8]" />
            <span className="font-bold tracking-wider text-white">FOUL-X</span>
            <span className="text-[10px] text-[#6b7280] border-l border-[#374151] pl-2">v0.1 PROTO</span>
          </div>
          <span className="hidden sm:inline text-[#9ca3af] font-medium">Fouling Intelligence & Decision Support</span>
        </div>

        {/* System Status Indicators */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-[#6b7280]">SYSTEM STATUS:</span>
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#102a1d] text-[#34d399] border border-[#065f46] font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-[#34d399] animate-pulse"></span>
              ONLINE / MONITORING
            </span>
          </div>

          <div className="hidden md:flex items-center gap-2">
            <span className="text-[#6b7280]">POLICY:</span>
            <span className={`px-2 py-0.5 rounded font-mono font-semibold ${
              scenario === 'normal' 
                ? 'bg-[#1e293b] text-[#38bdf8] border border-[#0284c7]' 
                : 'bg-[#311313] text-[#f87171] border border-[#991b1b]'
            }`}>
              {scenario === 'normal' ? 'PREDICTIVE_WINDOW' : 'FIXED_POLICY_FALLBACK'}
            </span>
          </div>

          {/* Ask FOUL-X Button Placeholder */}
          <button 
            onClick={() => alert('Ask FOUL-X Assistant (RAG Pipeline Placeholder) — Interface Ready.')}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#1e293b] hover:bg-[#334155] text-[#93c5fd] border border-[#3b82f6] transition cursor-pointer text-xs font-semibold"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>ASK FOUL-X</span>
          </button>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-[1600px] mx-auto px-4 flex items-center justify-between h-12">
        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`px-4 py-1.5 text-xs font-bold uppercase tracking-wider rounded transition cursor-pointer ${
                  isActive
                    ? 'bg-[#1d283a] text-[#38bdf8] border-b-2 border-[#38bdf8] shadow-sm'
                    : 'text-[#9ca3af] hover:text-white hover:bg-[#151b26]'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Demo Controls Bar */}
        <div className="flex items-center gap-2 bg-[#131722] px-3 py-1 rounded border border-[#21293a]">
          <span className="text-[10px] font-bold uppercase tracking-widest text-[#6b7280] flex items-center gap-1">
            <Shield className="w-3 h-3 text-[#fbbf24]" />
            DEMO CONTROLS:
          </span>
          
          <button
            onClick={() => setScenario('normal')}
            className={`px-2 py-0.5 text-[11px] font-bold rounded transition cursor-pointer ${
              scenario === 'normal'
                ? 'bg-[#065f46] text-[#6ee7b7] border border-[#10b981]'
                : 'bg-[#1c2433] text-[#9ca3af] hover:text-white'
            }`}
          >
            [Normal Scenario]
          </button>

          <button
            onClick={() => setScenario('disturbed')}
            className={`px-2 py-0.5 text-[11px] font-bold rounded transition cursor-pointer ${
              scenario === 'disturbed'
                ? 'bg-[#7f1d1d] text-[#fca5a5] border border-[#ef4444]'
                : 'bg-[#1c2433] text-[#9ca3af] hover:text-white'
            }`}
          >
            [Simulate Disturbance]
          </button>

          <button
            onClick={() => setScenario('normal')}
            className="px-2 py-0.5 text-[11px] font-semibold text-[#9ca3af] hover:text-white bg-[#1c2433] hover:bg-[#283246] rounded transition cursor-pointer"
          >
            [Reset]
          </button>
        </div>
      </div>
    </header>
  );
};
