/**
 * PLANT-X / FOUL-X DETERMINISTIC JUDGE WALKTHROUGH OVERLAY
 * 
 * Interactive HUD for judges and presenters displaying:
 * - Current Step (X / 19), title, and technical objective
 * - Live verification check: actual workstation state vs expected state
 * - Grounded narration script (zero LLM improvisations)
 * - Walkthrough controls: Start, Pause, Resume, Next, Previous, Skip, Abort, Restart
 * - Voice command prompt for presenter-driven navigation
 */

import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Square,
  CheckCircle2,
  AlertCircle,
  Clock,
  Mic,
  Volume2,
} from 'lucide-react';
import {
  judgeModeController,
  type JudgeModeStatus,
  type JudgeStep,
  type StepVerification,
} from '../../agent/judging/JudgeModeController';

export const JudgeModeOverlay: React.FC = () => {
  const [status, setStatus] = useState<JudgeModeStatus>(judgeModeController.getStatus());
  const [currentStep, setCurrentStep] = useState<JudgeStep | null>(judgeModeController.getCurrentStep());
  const [stepIndex, setStepIndex] = useState<number>(judgeModeController.getCurrentStepIndex());
  const [totalSteps] = useState<number>(judgeModeController.getTotalSteps());
  const [verification, setVerification] = useState<StepVerification | undefined>(undefined);

  useEffect(() => {
    const unsub = judgeModeController.subscribe(() => {
      const newStatus = judgeModeController.getStatus();
      setStatus(newStatus);
      const step = judgeModeController.getCurrentStep();
      setCurrentStep(step);
      setStepIndex(judgeModeController.getCurrentStepIndex());
      if (step) {
        setVerification(judgeModeController.getStepVerification(step.id));
      }
    });

    return () => {
      unsub();
    };
  }, []);

  if (status === 'IDLE') {
    return null;
  }

  const isCompleted = status === 'COMPLETED';
  const isFailed = status === 'FAILED';
  const isPaused = status === 'PAUSED';
  const isVerifying = status === 'STEP_VERIFYING';

  return (
    <aside aria-label="Judge Walkthrough" className="fixed top-14 left-1/2 -translate-x-1/2 z-40 w-full max-w-2xl bg-[#0b131f]/95 border border-cyan-500/50 rounded-lg shadow-2xl backdrop-blur-md font-mono text-gray-200 overflow-hidden select-none">
      {/* Top Header */}
      <div className="bg-[#070d15] px-4 py-2 border-b border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
            PLANT-X Judge Walkthrough [{stepIndex + 1} / {totalSteps}]
          </span>
          <span
            className={`px-1.5 py-0.2 text-[9px] font-bold rounded border ${
              isCompleted
                ? 'bg-emerald-950 text-emerald-300 border-emerald-600'
                : isFailed
                ? 'bg-rose-950 text-rose-300 border-rose-600'
                : isPaused
                ? 'bg-amber-950 text-amber-300 border-amber-600'
                : isVerifying
                ? 'bg-blue-950 text-blue-300 border-blue-600'
                : 'bg-cyan-950 text-cyan-300 border-cyan-700'
            }`}
          >
            {status}
          </span>
        </div>

        {/* Presenter Voice Prompt Hint */}
        <div className="hidden sm:flex items-center gap-1.5 text-[10px] text-gray-400">
          <Mic className="w-3 h-3 text-cyan-400" />
          <span>Voice: "Next", "Pause", "Resume", "Skip", "Abort"</span>
        </div>
      </div>

      {/* Main Step Body */}
      {currentStep && (
        <div className="p-3.5 space-y-2.5 text-xs">
          {/* Title & Description */}
          <div>
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-sm">
                Step {currentStep.stepNumber}: {currentStep.title}
              </h3>
              <span className="text-[10px] text-gray-400 font-normal">Route: {currentStep.route}</span>
            </div>
            <p className="text-[11px] text-gray-400 mt-0.5">{currentStep.description}</p>
          </div>

          {/* Narration Script */}
          <div className="bg-[#071018] p-2 rounded border border-[#1e293b] flex items-start gap-2">
            <Volume2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div className="text-[11px] text-cyan-200 italic leading-relaxed">
              "{currentStep.narration}"
            </div>
          </div>

          {/* Live Verification Box (Expected vs Actual State) */}
          <div className="bg-[#070d15] p-2 rounded border border-[#1e293b] flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-2">
              {verification?.passed ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : isVerifying ? (
                <Clock className="w-4 h-4 text-amber-400 animate-spin shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              )}
              <span className="text-gray-300">
                <span className="font-bold text-gray-400">STATE VERIFICATION:</span>{' '}
                {verification?.message || 'Inspecting workstation state...'}
              </span>
            </div>

            {verification && (
              <span
                className={`px-1.5 py-0.5 rounded font-bold text-[10px] ${
                  verification.passed
                    ? 'bg-emerald-900 text-emerald-200 border border-emerald-600'
                    : 'bg-rose-950 text-rose-300 border border-rose-700'
                }`}
              >
                {verification.passed ? 'PASSED' : 'VERIFICATION PENDING'}
              </span>
            )}
          </div>

          {/* Controls Bar */}
          <div className="flex items-center justify-between pt-1 border-t border-[#1e293b]">
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => judgeModeController.previousStep()}
                disabled={stepIndex <= 0}
                className="px-2 py-1 bg-[#1e293b] hover:bg-[#334155] disabled:opacity-40 rounded text-[10px] font-bold text-gray-200 cursor-pointer"
              >
                Back
              </button>
              <button
                onClick={() => judgeModeController.repeat()}
                className="flex items-center gap-1 px-2 py-1 bg-[#1e293b] hover:bg-[#334155] rounded text-[10px] font-bold text-gray-200 cursor-pointer"
                title="Repeat step"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Repeat</span>
              </button>
              {isPaused ? (
                <button
                  onClick={() => judgeModeController.resume()}
                  className="flex items-center gap-1 px-2.5 py-1 bg-emerald-900 hover:bg-emerald-800 text-emerald-200 rounded text-[10px] font-bold cursor-pointer"
                >
                  <Play className="w-3 h-3 fill-emerald-200" />
                  <span>Resume</span>
                </button>
              ) : (
                <button
                  onClick={() => judgeModeController.pause()}
                  className="flex items-center gap-1 px-2.5 py-1 bg-amber-950 hover:bg-amber-900 text-amber-200 rounded text-[10px] font-bold cursor-pointer"
                >
                  <Pause className="w-3 h-3" />
                  <span>Pause</span>
                </button>
              )}
              <button
                onClick={() => judgeModeController.skip()}
                disabled={stepIndex >= totalSteps - 1}
                className="flex items-center gap-1 px-2 py-1 bg-[#1e293b] hover:bg-[#334155] disabled:opacity-40 rounded text-[10px] font-bold text-gray-200 cursor-pointer"
              >
                <SkipForward className="w-3 h-3" />
                <span>Skip</span>
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => judgeModeController.nextStep()}
                disabled={stepIndex >= totalSteps - 1}
                className="px-3 py-1 bg-cyan-900 hover:bg-cyan-800 disabled:opacity-40 text-cyan-200 rounded text-[10px] font-bold cursor-pointer border border-cyan-600"
              >
                Next Step →
              </button>
              <button
                onClick={() => judgeModeController.abort()}
                className="flex items-center gap-1 px-2 py-1 bg-rose-950 hover:bg-rose-900 text-rose-300 rounded text-[10px] font-bold cursor-pointer border border-rose-800"
                title="Abort Walkthrough"
              >
                <Square className="w-2.5 h-2.5 fill-rose-300" />
                <span>Abort</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Completion Banner */}
      {isCompleted && (
        <div className="p-4 text-center space-y-2 bg-[#064e3b]/30">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
          <h3 className="font-bold text-white text-sm uppercase tracking-wide">
            Judge Walkthrough Fully Verified
          </h3>
          <p className="text-xs text-gray-300">
            All 19 steps executed with verified workstation state, causal evidence, and reliability gating.
          </p>
          <div className="pt-2 flex justify-center gap-2">
            <button
              onClick={() => judgeModeController.restart()}
              className="px-3 py-1.5 bg-emerald-800 hover:bg-emerald-700 text-white rounded text-xs font-bold cursor-pointer"
            >
              Restart Walkthrough
            </button>
            <button
              onClick={() => judgeModeController.abort()}
              className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-gray-300 rounded text-xs font-bold cursor-pointer"
            >
              Close HUD
            </button>
          </div>
        </div>
      )}
    </aside>
  );
};
