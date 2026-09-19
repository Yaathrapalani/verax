import React from 'react';
import { Timer, XCircle } from 'lucide-react';
import type { TimerState } from '../../agent/types';

interface TimerStatusBannerProps {
  timer: TimerState;
  onCancelTimer: () => void;
}

export const TimerStatusBanner: React.FC<TimerStatusBannerProps> = ({
  timer,
  onCancelTimer,
}) => {
  if (!timer.isActive) return null;

  return (
    <div className="bg-[#1e1b4b] border-b border-[#4338ca] px-4 py-1.5 flex items-center justify-between text-xs font-mono text-indigo-200 select-none shadow-md">
      <div className="flex items-center gap-2">
        <Timer className="w-4 h-4 text-indigo-400 animate-spin" />
        <span className="font-bold text-white uppercase tracking-wider">
          SCHEDULED TASK ACTIVE:
        </span>
        <span className="font-bold text-cyan-300">
          {timer.targetParams?.scenario ? timer.targetParams.scenario.toUpperCase() : timer.targetAction}
        </span>
        <span className="text-gray-400">
          STARTING IN <strong className="text-amber-300 text-sm">{timer.remainingSeconds.toFixed(1)} s</strong>
        </span>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-[10px] text-indigo-300 hidden md:inline">
          Context check: {timer.validationContext.expectedAssetTag} | {timer.validationContext.expectedScenario}
        </span>
        <button
          onClick={onCancelTimer}
          className="flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-bold bg-[#7f1d1d] hover:bg-[#991b1b] text-white border border-[#dc2626] transition cursor-pointer"
        >
          <XCircle className="w-3.5 h-3.5" />
          <span>CANCEL (VOICE: "CANCEL")</span>
        </button>
      </div>
    </div>
  );
};
