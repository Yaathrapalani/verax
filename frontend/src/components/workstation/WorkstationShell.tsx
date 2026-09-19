import React, { useState, useEffect, useCallback } from 'react';
import type {
  PlantWorkstationState,
  WorkstationView,
  ChemicalStream,
} from '../../agent/types';
import { INITIAL_HYPOTHESES } from '../../agent/tools';
import { timerService } from '../../agent/timerService';
import { voiceAssistantController } from '../../agent/voice/VoiceAssistantController';
import { proactiveEngine } from '../../agent/proactiveEngine';
import { auditLogger } from '../../agent/auditLogger';

import { PlantExplorer } from './PlantExplorer';
import { EngineeringInspector } from './EngineeringInspector';
import { ViewSwitcher } from './ViewSwitcher';
import { VoiceControlBar } from './VoiceControlBar';
import { TimerStatusBanner } from './TimerStatusBanner';
import { ChemicalStreamBuilder } from './ChemicalStreamBuilder';
import { AuditLogDrawer } from './AuditLogDrawer';

import { PlantScene3D } from '../scene/PlantScene3D';
import { PlantProcessOverlay } from '../process/PlantProcessOverlay';
import { EvidenceOverlay } from '../evidence/EvidenceOverlay';
import { EvidencePage } from '../evidence/EvidencePage';
import { TrustGateModal } from '../judging/TrustGateModal';
import { IndustrialIntakeModal } from '../judging/IndustrialIntakeModal';
import { BlueprintReviewModal } from '../blueprint/BlueprintReviewModal';
import { ProvenanceModal } from '../judging/ProvenanceModal';
import { BenchmarkModal } from '../judging/BenchmarkModal';
import { ChemistryModal } from '../judging/ChemistryModal';
import { F1LiveBindingDemo } from '../layout/F1LiveBindingDemo';
import { VoiceDiagnosticsModal } from '../diagnostics/VoiceDiagnosticsModal';
import { JudgeModeOverlay } from '../judging/JudgeModeOverlay';
import { judgeModeController } from '../../agent/judging/JudgeModeController';

import { Cpu, ShieldCheck, ShieldAlert, Eye, AlertTriangle, ScrollText, Radio, Play } from 'lucide-react';

const INITIAL_STREAM: ChemicalStream = {
  streamId: 'S-102',
  name: 'Preheated Crude Feed to E-102',
  phase: 'LIQUID',
  compositionBasis: 'MOLE_FRACTION',
  components: [
    { id: 'H2O', name: 'Water', formula: 'H2O', fraction: 0.05 },
    { id: 'CH4', name: 'Methane (Dissolved)', formula: 'CH4', fraction: 0.15 },
    { id: 'C3H8', name: 'Propane', formula: 'C3H8', fraction: 0.30 },
    { id: 'C7H8', name: 'Toluene / Naphtha', formula: 'C7H8', fraction: 0.50 },
  ],
  temperatureK: 468.55, // 195.4 °C
  pressureBar: 8.5,
  massFlowKgH: 374400, // 104 kg/s
  originPort: 'E-101 Tube Outlet',
  destPort: 'E-102 Tube Inlet',
  unsupportedProperties: ['Density', 'Viscosity', 'Enthalpy'],
};

export const WorkstationShell: React.FC = () => {
  const [state, setState] = useState<PlantWorkstationState>({
    activeView: 'PROCESS',
    selectedAssetTag: 'E-102',
    selectedStreamId: 'S-102',
    highlightedPath: ['E-102'],
    cameraFocusTag: 'E-102',

    scenario: 'normal',
    timeHr: 63241,
    isPlaying: false,
    foulingThresholdRf: 1.5e-7,
    currentRf: 7.28e-8,
    trustGateStatus: 'PASS',
    activePolicy: 'PREDICTIVE_CLEANING_WINDOW',

    activeStream: INITIAL_STREAM,

    timer: {
      isActive: false,
      totalSeconds: 0,
      remainingSeconds: 0,
      targetAction: '',
      targetParams: {},
      scheduledAtTimestamp: 0,
      validationContext: { expectedAssetTag: '', expectedScenario: '' },
    },

    agentStatus: 'READY',
    lastTranscript: '',
    lastAgentResponse: 'Workstation ready. Listening for engineering commands.',
    isVoiceActive: false,
    isTtsSpeaking: false,

    activeHypotheses: INITIAL_HYPOTHESES,
    activeHypothesisId: 'H1',
    investigationRecommendation: '',

    proactiveSuggestions: [],
    auditLog: [],
  });

  // Modal Overlay States
  const [isEvidenceModalOpen, setIsEvidenceModalOpen] = useState(false);
  const [isTrustGateModalOpen, setIsTrustGateModalOpen] = useState(false);
  const [isIntakeModalOpen, setIsIntakeModalOpen] = useState(false);
  const [isBlueprintModalOpen, setIsBlueprintModalOpen] = useState(false);
  const [isProvenanceModalOpen, setIsProvenanceModalOpen] = useState(false);
  const [isBenchmarkModalOpen, setIsBenchmarkModalOpen] = useState(false);
  const [isChemistryModalOpen, setIsChemistryModalOpen] = useState(false);
  const [isAuditDrawerOpen, setIsAuditDrawerOpen] = useState(false);
  const [isVoiceDiagnosticsOpen, setIsVoiceDiagnosticsOpen] = useState(false);

  // Synchronize Timer Service
  useEffect(() => {
    const unsubTick = timerService.onTick((remaining) => {
      setState((prev) => ({
        ...prev,
        timer: { ...prev.timer, remainingSeconds: remaining },
      }));
    });

    const unsubComplete = timerService.onComplete((result, explanation) => {
      setState((prev) => {
        const next = {
          ...prev,
          timer: {
            isActive: false,
            totalSeconds: 0,
            remainingSeconds: 0,
            targetAction: '',
            targetParams: {},
            scheduledAtTimestamp: 0,
            validationContext: { expectedAssetTag: '', expectedScenario: '' },
          },
          lastAgentResponse: explanation,
          ...(result.stateDelta || {}),
        };
        // Log to audit
        auditLogger.logAction(
          'Scheduled Execution Timer Finished',
          'TIMER_EXECUTED',
          {},
          prev,
          prev.timer.targetAction,
          prev.timer.targetParams,
          result.success ? 'SUCCESS' : 'FAILURE',
          result.message,
          result.stateDelta
        );
        next.auditLog = auditLogger.getEntries();
        return next;
      });

      voiceAssistantController.speak(explanation);
    });

    const unsubCancel = timerService.onCancel((reason) => {
      setState((prev) => ({
        ...prev,
        timer: {
          isActive: false,
          totalSeconds: 0,
          remainingSeconds: 0,
          targetAction: '',
          targetParams: {},
          scheduledAtTimestamp: 0,
          validationContext: { expectedAssetTag: '', expectedScenario: '' },
        },
        lastAgentResponse: `Timer cancelled: ${reason}`,
      }));
      voiceAssistantController.speak('Scheduled action cancelled.');
    });

    return () => {
      unsubTick();
      unsubComplete();
      unsubCancel();
    };
  }, []);

  // Synchronize Proactive Suggestions
  useEffect(() => {
    const suggestions = proactiveEngine.evaluate(state);
    setState((prev) => ({ ...prev, proactiveSuggestions: suggestions }));
  }, [state.scenario, state.selectedAssetTag, state.activeView, state.currentRf]);

  // Execute Agent Command (Voice or Text)
  // Register workstation state with persistent assistant controller
  useEffect(() => {
    voiceAssistantController.registerWorkstation(state, setState);
    const unsub = voiceAssistantController.subscribe(() => {
      setState((prev) => ({
        ...prev,
        agentStatus: voiceAssistantController.getStatus(),
        isVoiceActive: voiceAssistantController.getIsListening(),
        isTtsSpeaking: voiceAssistantController.getIsSpeaking(),
        lastTranscript: voiceAssistantController.getLastTranscript(),
        lastAgentResponse: voiceAssistantController.getLastResponse(),
      }));
    });

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        voiceAssistantController.toggleVoice();
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      unsub();
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Sync state to controller on updates
  useEffect(() => {
    voiceAssistantController.syncState(state);
    judgeModeController.registerWorkstation(() => state, setState);
  }, [state]);

  // Execute Agent Command (Voice or Text)
  const handleExecuteCommand = useCallback(
    async (utterance: string) => {
      await voiceAssistantController.executeUtterance(utterance);
    },
    []
  );

  // View & Entity Selection handlers
  const handleSelectEquipment = (tag: string) => {
    handleExecuteCommand(`Select ${tag}`);
  };

  const handleSelectStream = (streamId: string) => {
    handleExecuteCommand(`Select stream ${streamId}`);
  };

  const handleChangeView = (view: WorkstationView) => {
    handleExecuteCommand(`Open ${view.toLowerCase()}`);
  };

  const handleCancelTimer = () => {
    handleExecuteCommand('Cancel');
  };

  const handleToggleVoice = () => {
    voiceAssistantController.toggleVoice();
  };

  const handleStopSpeaking = () => {
    voiceAssistantController.stopSpeaking();
  };

  return (
    <div className="min-h-screen bg-[#071018] text-[#d1d5db] font-mono flex flex-col overflow-hidden select-none">
      {/* 1. TOP APPLICATION BAR */}
      <header className="bg-[#0b1019] border-b border-[#1e293b] px-4 py-2 flex flex-wrap items-center justify-between gap-3 text-xs z-20 shadow-md">
        {/* Plant System Title & Identity */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-[#071018] px-2.5 py-1 rounded border border-[#1e293b]">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <div className="flex flex-col">
              <span className="font-extrabold tracking-widest text-white text-xs leading-none">PLANT-X</span>
              <span className="text-[9px] text-cyan-400 font-mono leading-none mt-0.5 uppercase">ENGINEERING WORKSTATION</span>
            </div>
          </div>

          <div className="hidden lg:block border-l border-[#1e293b] pl-3">
            <h1 className="text-xs font-bold text-white tracking-wide uppercase flex items-center gap-2">
              <span>Crude Preheat Train 1</span>
              <span className="text-gray-500 font-normal text-[10px]">Study: Base Case (63,241 h)</span>
            </h1>
            <p className="text-[9px] text-gray-500">
              REPRESENTATIVE PROCESS TOPOLOGY — NOT A PROPRIETARY PLANT BLUEPRINT
            </p>
          </div>
        </div>

        {/* View Switcher in Top Bar */}
        <ViewSwitcher activeView={state.activeView} onChangeView={handleChangeView} />

        {/* Action / Judging Buttons & Audit Drawer Trigger */}
        <div className="flex items-center gap-2">
          {/* Trust Gate Status Badge / Button */}
          <button
            onClick={() => setIsTrustGateModalOpen(true)}
            className={`px-2.5 py-1 rounded text-[10px] font-bold border flex items-center gap-1.5 transition cursor-pointer ${
              state.trustGateStatus === 'PASS'
                ? 'bg-emerald-950/80 border-emerald-700 text-emerald-300 hover:bg-emerald-900'
                : 'bg-amber-950/80 border-amber-700 text-amber-300 hover:bg-amber-900'
            }`}
          >
            {state.trustGateStatus === 'PASS' ? (
              <>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>GATE: PASS</span>
              </>
            ) : (
              <>
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                <span>GATE: ABSTAIN</span>
              </>
            )}
          </button>

          {/* Audit Log Trigger */}
          <button
            onClick={() => setIsAuditDrawerOpen(true)}
            className="flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold bg-[#1e293b] hover:bg-[#334155] text-cyan-300 border border-[#334155]"
            title="Inspect Agent Audit Trail"
          >
            <ScrollText className="w-3.5 h-3.5" />
            <span>AUDIT ({state.auditLog.length})</span>
          </button>

          {/* Voice Diagnostics Trigger (/diagnostics/voice) */}
          <button
            onClick={() => setIsVoiceDiagnosticsOpen(true)}
            className="flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold bg-[#091522] hover:bg-[#12283f] text-cyan-400 border border-cyan-500/40 cursor-pointer"
            title="Realtime Voice & Audio Diagnostics (/diagnostics/voice)"
          >
            <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span>DIAGNOSTICS</span>
          </button>

          {/* Judge Acceptance Walkthrough Trigger */}
          <button
            onClick={() => judgeModeController.startWalkthrough()}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] font-bold bg-cyan-950/90 hover:bg-cyan-900 text-cyan-200 border border-cyan-400/80 shadow transition cursor-pointer"
            title="Start Deterministic 19-Step Acceptance Walkthrough for Judges"
          >
            <Play className="w-3.5 h-3.5 fill-cyan-400 text-cyan-400" />
            <span>JUDGE WALKTHROUGH</span>
          </button>

          <button
            onClick={() => setIsBlueprintModalOpen(true)}
            className="hidden sm:inline px-2 py-1 bg-[#0f172a] hover:bg-[#1e293b] border border-[#38bdf8]/40 text-cyan-300 hover:text-white rounded text-[10px] font-bold"
            title="Blueprint P&ID Ingestion & Procedural 3D Reconstruction"
          >
            BLUEPRINT P&ID
          </button>
          <button
            onClick={() => setIsIntakeModalOpen(true)}
            className="hidden sm:inline px-2 py-1 bg-[#071018] hover:bg-[#1e293b] border border-[#1e293b] text-gray-400 hover:text-white rounded text-[10px]"
          >
            INTAKE
          </button>
          <button
            onClick={() => setIsBenchmarkModalOpen(true)}
            className="hidden sm:inline px-2 py-1 bg-[#071018] hover:bg-[#1e293b] border border-[#1e293b] text-gray-400 hover:text-white rounded text-[10px]"
          >
            BENCHMARKS
          </button>
          <button
            onClick={() => setIsProvenanceModalOpen(true)}
            className="hidden sm:inline px-2 py-1 bg-[#071018] hover:bg-[#1e293b] border border-[#1e293b] text-gray-400 hover:text-white rounded text-[10px]"
          >
            PROVENANCE
          </button>
        </div>
      </header>


      {/* F1 Live Backend Binding Status Demo */}
      <div className="px-4 py-1.5 bg-[#090d16] border-b border-[#1e293b]">
        <F1LiveBindingDemo />
      </div>

      {/* Timer Status Countdown Banner (when active) */}
      <TimerStatusBanner timer={state.timer} onCancelTimer={handleCancelTimer} />

      {/* Proactive Intelligence Banner (if alert exists) */}
      {state.proactiveSuggestions.filter((s) => !s.dismissed).length > 0 && (
        <div className="bg-[#181309] border-b border-[#78350f] px-4 py-1 flex items-center justify-between text-[11px] text-amber-200">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span className="font-bold text-amber-400 uppercase">PROACTIVE OBSERVATION:</span>
            <span>{state.proactiveSuggestions.find((s) => !s.dismissed)?.message}</span>
          </div>
          <button
            onClick={() =>
              setState((prev) => ({
                ...prev,
                proactiveSuggestions: prev.proactiveSuggestions.map((s) => ({ ...s, dismissed: true })),
              }))
            }
            className="text-gray-400 hover:text-white text-[10px]"
          >
            DISMISS
          </button>
        </div>
      )}

      {/* 2. MAIN 3-COLUMN WORKSPACE CONTAINER */}
      <div className="flex-1 flex relative overflow-hidden">
        {/* Left Column: Plant Explorer Tree */}
        <PlantExplorer
          selectedAssetTag={state.selectedAssetTag}
          selectedStreamId={state.selectedStreamId}
          onSelectEquipment={handleSelectEquipment}
          onSelectStream={handleSelectStream}
        />

        {/* Center Column: Active Engineering Viewport */}
        <main className="flex-1 relative flex flex-col overflow-hidden bg-[#071018]">
          {/* View 1: PROCESS SCHEMATIC VIEW */}
          {state.activeView === 'PROCESS' && (
            <div className="w-full h-full relative">
              <PlantScene3D
                selectedAssetTag={state.selectedAssetTag}
                setSelectedAssetTag={handleSelectEquipment}
                inspectionMode="NORMAL"
                scenario={state.scenario}
                highlightedPath={state.highlightedPath}
                cameraFocusTag={state.cameraFocusTag}
              />
              <PlantProcessOverlay
                selectedAssetTag={state.selectedAssetTag}
                setSelectedAssetTag={handleSelectEquipment}
                inspectionMode="NORMAL"
                scenario={state.scenario}
                timeHr={state.timeHr}
                openEvidenceOverlay={() => setIsEvidenceModalOpen(true)}
                openTrustGateModal={() => setIsTrustGateModalOpen(true)}
                openIntakeModal={() => setIsIntakeModalOpen(true)}
              />
            </div>
          )}

          {/* View 2: 3D SPATIAL VIEW */}
          {state.activeView === '3D' && (
            <div className="w-full h-full relative">
              <PlantScene3D
                selectedAssetTag={state.selectedAssetTag}
                setSelectedAssetTag={handleSelectEquipment}
                inspectionMode="NORMAL"
                scenario={state.scenario}
                highlightedPath={state.highlightedPath}
                cameraFocusTag={state.cameraFocusTag}
              />
            </div>
          )}

          {/* View 3: P&ID SCHEMATIC VIEW */}
          {state.activeView === 'PND' && (
            <div className="w-full h-full p-6 overflow-auto">
              <div className="bg-[#0b1019] border border-[#1e293b] p-6 rounded text-center space-y-4 max-w-4xl mx-auto">
                <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
                  Piping & Instrumentation Diagram (P&ID) — Crude Preheat Train
                </div>
                <div className="p-8 border border-dashed border-[#334155] rounded flex flex-col items-center justify-center space-y-3">
                  <Eye className="w-10 h-10 text-cyan-500" />
                  <p className="text-sm font-bold text-white">Canonical Process Graph Topology Projection</p>
                  <p className="text-xs text-gray-400 max-w-lg">
                    Equipment nodes: P-101, E-101, E-102, E-103, V-101, E-104, E-105, F-101, C-101.
                    Streams: S-101 through S-108. All node selections persist globally across 3D, Inspector, and Simulation workspaces.
                  </p>
                  <button
                    onClick={() => setIsBlueprintModalOpen(true)}
                    className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-cyan-300 border border-cyan-500/40 rounded text-xs font-bold"
                  >
                    Open Interactive Blueprint Diagram →
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* View 4: SIMULATION WORKBENCH */}
          {state.activeView === 'SIMULATION' && (
            <div className="w-full h-full p-6 overflow-auto">
              <div className="bg-[#0b1019] border border-[#1e293b] p-6 rounded space-y-4 max-w-4xl mx-auto">
                <div className="flex justify-between items-center border-b border-[#1e293b] pb-2">
                  <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
                    Stage 9 What-If Counterfactual Simulation Workbench
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#1e293b] text-purple-300 border border-purple-800">
                    SIMULATED TRUTH STATE
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="bg-[#0f172a] p-4 rounded border border-[#1e293b] space-y-3">
                    <span className="font-bold text-white block">Scenario Controls</span>
                    <button
                      onClick={() => handleExecuteCommand('Run the irregular sampling scenario in ten seconds')}
                      className="w-full py-2 bg-[#1e293b] hover:bg-[#334155] text-cyan-300 border border-cyan-500/50 rounded font-bold text-xs"
                    >
                      Schedule Irregular Sampling in 10s (VOICE-TRIGGERED)
                    </button>
                    <button
                      onClick={() => handleExecuteCommand(state.scenario === 'normal' ? 'Run disturbed scenario' : 'Run normal scenario')}
                      className={`w-full py-2 font-bold text-xs rounded border transition ${
                        state.scenario === 'disturbed'
                          ? 'bg-[#7f1d1d] text-white border-rose-500'
                          : 'bg-[#064e3b] text-emerald-200 border-emerald-500'
                      }`}
                    >
                      Toggle Regime Shift (+6σ Stress Test)
                    </button>
                  </div>

                  <div className="bg-[#0f172a] p-4 rounded border border-[#1e293b] space-y-2">
                    <span className="font-bold text-white block">Simulation Results</span>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Target Exchanger:</span>
                      <span className="text-white font-bold">{state.selectedAssetTag}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Current State:</span>
                      <span className={state.scenario === 'disturbed' ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                        {state.scenario.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Reliability Gate:</span>
                      <span className="text-amber-400 font-bold">{state.trustGateStatus}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* View 5: EVIDENCE GRAPH VIEW */}
          {state.activeView === 'EVIDENCE' && (
            <div className="w-full h-full p-6 overflow-auto">
              <EvidencePage />
            </div>
          )}

          {/* View 6: CHEMISTRY & STREAM BUILDER */}
          {state.activeView === 'CHEMISTRY' && (
            <div className="w-full h-full p-6 overflow-auto">
              <ChemicalStreamBuilder
                stream={state.activeStream}
                onUpdateStream={(updated) => setState((prev) => ({ ...prev, activeStream: updated }))}
              />
            </div>
          )}

          {/* View 7: TRENDS VIEW */}
          {state.activeView === 'TRENDS' && (
            <div className="w-full h-full p-6 overflow-auto text-xs text-gray-400 text-center">
              <div className="p-8 bg-[#0b1019] border border-[#1e293b] rounded max-w-xl mx-auto space-y-2">
                <span className="font-bold text-white text-sm">Multi-Sensor Temporal Trend Plot</span>
                <p>Telemetry stream synchronized across 63,241 hours of continuous plant operation.</p>
              </div>
            </div>
          )}
        </main>

        {/* Right Column: Universal Engineering Inspector */}
        <EngineeringInspector
          state={state}
          onSelectHypothesis={(hId) => handleExecuteCommand(`Evaluate hypothesis ${hId}`)}
          onSelectStream={handleSelectStream}
          onOpenEvidence={() => setIsEvidenceModalOpen(true)}
        />
      </div>

      {/* 3. BOTTOM VOICE CONTROL BAR */}
      <VoiceControlBar
        agentStatus={state.agentStatus}
        isListening={state.isVoiceActive}
        isSpeaking={state.isTtsSpeaking}
        lastTranscript={state.lastTranscript}
        lastResponse={state.lastAgentResponse}
        onToggleVoice={handleToggleVoice}
        onStopSpeaking={handleStopSpeaking}
        onSubmitText={handleExecuteCommand}
        voiceSupported={true}
      />

      {/* 4. MODALS & JUDGING OVERLAYS */}
      <EvidenceOverlay
        isOpen={isEvidenceModalOpen}
        onClose={() => setIsEvidenceModalOpen(false)}
        scenario={state.scenario}
        selectedAssetTag={state.selectedAssetTag}
      />

      <TrustGateModal
        isOpen={isTrustGateModalOpen}
        onClose={() => setIsTrustGateModalOpen(false)}
        scenario={state.scenario}
        setScenario={(scen) => handleExecuteCommand(scen === 'disturbed' ? 'Run disturbed scenario' : 'Run normal scenario')}
      />

      <IndustrialIntakeModal
        isOpen={isIntakeModalOpen}
        onClose={() => setIsIntakeModalOpen(false)}
      />

      <BlueprintReviewModal
        isOpen={isBlueprintModalOpen}
        onClose={() => setIsBlueprintModalOpen(false)}
        onSceneCompiled={(notice) => {
          setState((prev) => ({
            ...prev,
            activeView: '3D',
            cameraFocusTag: 'E-102',
            lastAgentResponse: notice,
          }));
          setIsBlueprintModalOpen(false);
        }}
      />


      <ProvenanceModal
        isOpen={isProvenanceModalOpen}
        onClose={() => setIsProvenanceModalOpen(false)}
      />

      <BenchmarkModal
        isOpen={isBenchmarkModalOpen}
        onClose={() => setIsBenchmarkModalOpen(false)}
      />

      <ChemistryModal
        isOpen={isChemistryModalOpen}
        onClose={() => setIsChemistryModalOpen(false)}
      />

      <AuditLogDrawer
        isOpen={isAuditDrawerOpen}
        onClose={() => setIsAuditDrawerOpen(false)}
        entries={state.auditLog}
      />

      <VoiceDiagnosticsModal
        isOpen={isVoiceDiagnosticsOpen}
        onClose={() => setIsVoiceDiagnosticsOpen(false)}
      />

      {/* 5. DETERMINISTIC JUDGE WALKTHROUGH OVERLAY */}
      <JudgeModeOverlay />
    </div>
  );
};
