import React, { useState, useEffect } from 'react';
import type { InspectionMode, IntelligenceCopilotState } from './types/plant';
import { PlantHeader } from './components/layout/PlantHeader';
import { PlantScene3D } from './components/scene/PlantScene3D';
import { PlantProcessOverlay } from './components/process/PlantProcessOverlay';
import { FoulXCopilot } from './components/copilot/FoulXCopilot';
import { EvidenceOverlay } from './components/evidence/EvidenceOverlay';
import { TrustGateModal } from './components/judging/TrustGateModal';
import { IndustrialIntakeModal } from './components/judging/IndustrialIntakeModal';
import { BlueprintModal } from './components/judging/BlueprintModal';
import { ProvenanceModal } from './components/judging/ProvenanceModal';
import { BenchmarkModal } from './components/judging/BenchmarkModal';
import { ChemistryModal } from './components/judging/ChemistryModal';
import { TRANSLATIONS } from './data/translations';
import type { Language } from './data/translations';

export const App: React.FC = () => {
  const [selectedAssetTag, setSelectedAssetTag] = useState<string>('E02');
  const [inspectionMode, setInspectionMode] = useState<InspectionMode>('NORMAL');
  const [scenario, setScenario] = useState<'normal' | 'disturbed'>('normal');
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [timeHr, setTimeHr] = useState<number>(63241);
  const [lang, setLang] = useState<Language>('en');

  // Modals state for Judging Features
  const [isEvidenceOpen, setIsEvidenceOpen] = useState<boolean>(false);
  const [isTrustGateOpen, setIsTrustGateOpen] = useState<boolean>(false);
  const [isIntakeOpen, setIsIntakeOpen] = useState<boolean>(false);
  const [isBlueprintOpen, setIsBlueprintOpen] = useState<boolean>(false);
  const [isProvenanceOpen, setIsProvenanceOpen] = useState<boolean>(false);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState<boolean>(false);
  const [isChemistryOpen, setIsChemistryOpen] = useState<boolean>(false);

  // Replay timer loop
  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimeHr((prev) => (prev >= 64000 ? 44800 : prev + 1));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  const resetReplay = () => {
    setTimeHr(44800);
    setIsPlaying(false);
    setScenario('normal');
  };

  // Keyboard shortcuts for Judging Demo
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in input/textarea
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) return;

      if (e.key === '1') {
        setScenario('normal');
      } else if (e.key === '2') {
        setScenario('normal');
        setSelectedAssetTag('E02');
      } else if (e.key === '3') {
        setScenario('disturbed');
      } else if (e.key.toLowerCase() === 'r') {
        resetReplay();
      } else if (e.code === 'Space') {
        e.preventDefault();
        setIsPlaying((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Copilot Assistant State
  const [copilotState, setCopilotState] = useState<IntelligenceCopilotState>({
    currentAssetTag: selectedAssetTag,
    activeScenario: scenario,
    isListening: false,
    isAnalyzing: false,
    transcript: '',
    copilotResponse: '',
    copilotHistory: [
      {
        sender: 'FOUL-X',
        text: 'FOUL-X Intelligence Engine online. Monitoring crude preheat train assets E-101 through E-105.',
        timestamp: '12:34:00',
      },
      {
        sender: 'FOUL-X',
        text: 'E-102 is currently flagged with ATTENTION due to an increasing thermal fouling trajectory.',
        timestamp: '12:34:05',
      },
    ],
  });

  // Handle Copilot user messages
  const handleCopilotMessage = (text: string) => {
    const timeStr = new Date().toLocaleTimeString();
    const userMsg = { sender: 'USER' as const, text, timestamp: timeStr };

    let botReplyText = '';
    const q = text.toLowerCase();

    if (q.includes('e-102') || q.includes('e02')) {
      setSelectedAssetTag('E02');
      botReplyText = `Selecting E-102 (Kerosene Exchanger). Current derived fouling resistance R_f = 1.14e-7 m²·K/W. M2 physics state is VALID.`;
    } else if (q.includes('stress test') || q.includes('shifted') || q.includes('switch to stress') || q.includes('disturbed')) {
      setScenario('disturbed');
      botReplyText = `Switching to SYNTHETIC REGIME-SHIFT STRESS TEST (+6σ). Operating state moved outside historical training support. M5 Reliability Gate triggered REGIME_OOD -> ABSTAIN.`;
    } else if (q.includes('normal') || q.includes('switch to normal')) {
      setScenario('normal');
      botReplyText = `Restoring NORMAL operating mode. Current operating state within historical training support. M5 Reliability Gate status: PASS.`;
    } else if (q.includes('why') || q.includes('degrading')) {
      botReplyText = `E-102 shows progressive thermal fouling trajectory. Current R_f = 1.14e-7 m²·K/W approaching threshold 1.5e-7 m²·K/W. M4.0 Ridge prognosis predicts threshold crossing within 24h.`;
    } else if (q.includes('reliability') || q.includes('gate') || q.includes('trust')) {
      if (scenario === 'normal') {
        botReplyText = `Reliability Gate Status: PASS. All 4 checks (Data Completeness, Sensor Validity, Physics Consistency, Regime Support) passed cleanly.`;
      } else {
        botReplyText = `Reliability Gate Status: ABSTAIN. Check 4 (Historical Regime Support) failed with REGIME_OOD. FOUL-X is withholding AI recommendation and falling back to configured FIXED policy.`;
      }
    } else if (q.includes('evidence') || q.includes('trace') || q.includes('show evidence')) {
      setIsEvidenceOpen(true);
      botReplyText = `Opening scientific evidence trace overlay. Provenance verified from raw historian measurements to decision support.`;
    } else if (q.includes('intake') || q.includes('upload') || q.includes('ingest')) {
      setIsIntakeOpen(true);
      botReplyText = `Opening Industrial Data Intake portal. Plant evidence files can be attached as context; model training dataset remains unchanged.`;
    } else if (q.includes('chemistry') || q.includes('reaction') || q.includes('asphaltene')) {
      setIsChemistryOpen(true);
      botReplyText = `Opening Bounded Process Chemistry & Simulation module. Thermal coking deposition mechanism displayed.`;
    } else {
      botReplyText = `Processing request for asset ${selectedAssetTag}. Current overall heat transfer coefficient UA = 189,200 W/K against clean reference 198,450 W/K. M4.0 Ridge prognosis active.`;
    }

    const botMsg = { sender: 'FOUL-X' as const, text: botReplyText, timestamp: new Date().toLocaleTimeString() };

    setCopilotState((prev) => ({
      ...prev,
      copilotHistory: [...prev.copilotHistory, userMsg, botMsg],
    }));
  };

  const t = TRANSLATIONS[lang];

  return (
    <div className="min-h-screen bg-[#071018] text-[#d1d5db] font-mono flex flex-col overflow-hidden select-none">
      {/* Top Command Bar */}
      <PlantHeader
        selectedAssetTag={selectedAssetTag}
        inspectionMode={inspectionMode}
        setInspectionMode={setInspectionMode}
        scenario={scenario}
        setScenario={setScenario}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        timeHr={timeHr}
        resetReplay={resetReplay}
        openTrustGate={() => setIsTrustGateOpen(true)}
        openIntake={() => setIsIntakeOpen(true)}
        openBlueprint={() => setIsBlueprintOpen(true)}
        openProvenance={() => setIsProvenanceOpen(true)}
        openBenchmark={() => setIsBenchmarkOpen(true)}
        openChemistry={() => setIsChemistryOpen(true)}
        lang={lang}
        setLang={setLang}
      />

      {/* Primary Banner Message: Critical Product Message */}
      <div className="bg-[#0b1622] border-b border-[#15212d] px-4 py-1.5 flex items-center justify-between text-[11px]">
        <div className="flex items-center gap-2">
          <span className="px-1.5 py-0.5 rounded bg-[#1e293b] text-[#27b7e8] font-bold text-[10px]">
            CORE THESIS
          </span>
          <span className="text-white font-semibold">
            {t.coreThesis}
          </span>
          <span className="text-[#9ca3af] hidden md:inline">
            — {t.coreThesisSecondary}
          </span>
        </div>

        <div className="flex items-center gap-3 text-[10px] text-[#6b7280]">
          <span className="hidden lg:inline">KEYBOARD SHORTCUTS: <kbd className="bg-[#15212d] px-1 text-white">1</kbd> NORMAL | <kbd className="bg-[#15212d] px-1 text-white">3</kbd> +6σ STRESS | <kbd className="bg-[#15212d] px-1 text-white">R</kbd> RESET</span>
        </div>
      </div>

      {/* Main Viewport Container */}
      <div className="flex-1 flex relative overflow-hidden">
        {/* 3D WebGL Process Scene & HUD */}
        <div className="flex-1 relative">
          <PlantScene3D
            selectedAssetTag={selectedAssetTag}
            setSelectedAssetTag={setSelectedAssetTag}
            inspectionMode={inspectionMode}
            scenario={scenario}
          />

          <PlantProcessOverlay
            selectedAssetTag={selectedAssetTag}
            setSelectedAssetTag={setSelectedAssetTag}
            inspectionMode={inspectionMode}
            scenario={scenario}
            timeHr={timeHr}
            openEvidenceOverlay={() => setIsEvidenceOpen(true)}
            openTrustGateModal={() => setIsTrustGateOpen(true)}
            openIntakeModal={() => setIsIntakeOpen(true)}
          />
        </div>

        {/* Persistent FOUL-X Copilot Side Drawer */}
        <FoulXCopilot
          state={copilotState}
          selectedAssetTag={selectedAssetTag}
          scenario={scenario}
          onSendMessage={handleCopilotMessage}
          openEvidenceOverlay={() => setIsEvidenceOpen(true)}
        />
      </div>

      {/* Modals & Judging Overlays */}
      <EvidenceOverlay
        isOpen={isEvidenceOpen}
        onClose={() => setIsEvidenceOpen(false)}
        scenario={scenario}
        selectedAssetTag={selectedAssetTag}
      />

      <TrustGateModal
        isOpen={isTrustGateOpen}
        onClose={() => setIsTrustGateOpen(false)}
        scenario={scenario}
        setScenario={setScenario}
      />

      <IndustrialIntakeModal
        isOpen={isIntakeOpen}
        onClose={() => setIsIntakeOpen(false)}
      />

      <BlueprintModal
        isOpen={isBlueprintOpen}
        onClose={() => setIsBlueprintOpen(false)}
      />

      <ProvenanceModal
        isOpen={isProvenanceOpen}
        onClose={() => setIsProvenanceOpen(false)}
      />

      <BenchmarkModal
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
      />

      <ChemistryModal
        isOpen={isChemistryOpen}
        onClose={() => setIsChemistryOpen(false)}
      />
    </div>
  );
};

export default App;
