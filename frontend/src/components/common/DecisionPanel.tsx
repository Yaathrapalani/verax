import React from 'react';
import type { DecisionRecommendation, ScenarioMode } from '../../types/foulx';
import { ShieldCheck, UserCheck, Clock, ShieldAlert } from 'lucide-react';

interface DecisionPanelProps {
  scenario: ScenarioMode;
}

export const DecisionPanel: React.FC<DecisionPanelProps> = ({ scenario }) => {
  const isNormal = scenario === 'normal';

  const recommendation: DecisionRecommendation = isNormal
    ? {
        status: 'CLEANING_RECOMMENDED',
        title: 'CLEANING WINDOW — ENGINEERING REVIEW',
        subtitle: 'Proactive fouling prognosis indicates optimal cleaning window in 14 days.',
        targetExchanger: 'E02 (Kerosene Exchanger)',
        recommendedWindowDays: 14,
        estimatedCleaningCostUSD: 45000,
        estimatedFuelPenaltyPerDayUSD: 1250,
        humanApprovalRequired: true,
        requiresReview: true,
      }
    : {
        status: 'ABSTAIN_FIXED_POLICY',
        title: 'FOUL-X ABSTAINED — FIXED POLICY ACTIVE',
        subtitle: 'Forecast remains available, but the maintenance recommendation has been withheld.',
        targetExchanger: 'Plant Heat Exchanger Train',
        recommendedWindowDays: 90,
        estimatedCleaningCostUSD: 45000,
        estimatedFuelPenaltyPerDayUSD: 0,
        humanApprovalRequired: true,
        requiresReview: true,
      };

  return (
    <div className={`p-4 rounded border ${
      isNormal
        ? 'bg-[#0f172a] border-[#1e3a8a] text-[#bfdbfe]'
        : 'bg-[#1e1313] border-[#7f1d1d] text-[#fecaca]'
    }`}>
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Title & Status */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            {isNormal ? (
              <ShieldCheck className="w-5 h-5 text-[#38bdf8]" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-[#f87171]" />
            )}
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              {recommendation.title}
            </h3>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded uppercase tracking-wider bg-[#1e293b] text-[#94a3b8] border border-[#334155]">
              DEMO MODE
            </span>
          </div>
          <p className="text-xs text-[#94a3b8]">{recommendation.subtitle}</p>
        </div>

        {/* Advisory Warning Badge */}
        <div className="flex items-center gap-2 bg-[#172033] px-3 py-1.5 rounded border border-[#2b3954] text-xs font-semibold text-[#f59e0b]">
          <UserCheck className="w-4 h-4 text-[#f59e0b]" />
          <span>ADVISORY — Human approval required.</span>
        </div>
      </div>

      {/* Detail Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 pt-3 border-t border-[#1e293b] text-xs">
        <div>
          <span className="text-[#64748b] block text-[10px] uppercase font-bold">Target Exchanger</span>
          <span className="font-bold text-white">{recommendation.targetExchanger}</span>
        </div>

        <div>
          <span className="text-[#64748b] block text-[10px] uppercase font-bold">Policy Status</span>
          <span className={`font-bold ${isNormal ? 'text-[#38bdf8]' : 'text-[#f87171]'}`}>
            {isNormal ? 'Predictive Window Active' : 'Fixed Cleaning Policy Active'}
          </span>
        </div>

        <div>
          <span className="text-[#64748b] block text-[10px] uppercase font-bold">Suggested Interval</span>
          <span className="font-bold text-white font-mono">{recommendation.recommendedWindowDays} Days</span>
        </div>

        <div>
          <span className="text-[#64748b] block text-[10px] uppercase font-bold">Decision Safety</span>
          <span className="font-bold text-[#10b981] flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Advisory Only
          </span>
        </div>
      </div>
    </div>
  );
};
