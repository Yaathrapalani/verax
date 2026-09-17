import React from 'react';
import type { InspectionMode } from '../../types/plant';
import { REPRESENTATIVE_CDU_EQUIPMENT } from '../../data/representativePlant';
import { ArrowRight } from 'lucide-react';

interface PlantProcessOverlayProps {
  selectedAssetTag: string;
  setSelectedAssetTag: (tag: string) => void;
  inspectionMode: InspectionMode;
  scenario: 'normal' | 'disturbed';
  timeHr: number;
  openEvidenceOverlay: () => void;
  openTrustGateModal: () => void;
  openIntakeModal: () => void;
}

export const PlantProcessOverlay: React.FC<PlantProcessOverlayProps> = ({
  selectedAssetTag,
  scenario,
  openEvidenceOverlay,
  openTrustGateModal,
  openIntakeModal,
}) => {
  const isNormal = scenario === 'normal';
  const selectedEquipment = REPRESENTATIVE_CDU_EQUIPMENT.find(
    (e) => e.datasetTag === selectedAssetTag || e.tag === selectedAssetTag
  ) || REPRESENTATIVE_CDU_EQUIPMENT[2]; // Default E-102

  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-4 z-10 font-mono text-xs">
      {/* Top Process Flow Header Trace */}
      <div className="bg-[#071018]/90 backdrop-blur border border-[#15212d] p-2.5 rounded pointer-events-auto flex items-center justify-between gap-4 overflow-x-auto">
        <div className="flex items-center gap-2 text-[11px] font-bold text-white shrink-0">
          <span className="w-2 h-2 rounded-full bg-[#34d399] animate-pulse"></span>
          <span>CRUDE PREHEAT PROCESS FLOW:</span>
          <button
            onClick={openIntakeModal}
            className="ml-2 px-1.5 py-0.5 bg-[#101923] hover:bg-[#1b2a3a] border border-[#1b2a3a] text-[#27b7e8] rounded text-[9px] cursor-pointer transition font-bold"
          >
            + INGEST EVIDENCE
          </button>
        </div>

        <div className="flex items-center gap-2 text-[10px] text-[#9ca3af] whitespace-nowrap">
          <span>CRUDE FEED</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span>P-101</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span className={`px-1.5 py-0.5 rounded font-bold ${selectedAssetTag === 'E01' ? 'bg-[#0284c7] text-white' : 'bg-[#101923]'}`}>E-101</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span className={`px-1.5 py-0.5 rounded font-bold ${selectedAssetTag === 'E02' ? 'bg-[#7f1d1d] text-[#fca5a5] border border-[#ef4444]' : 'bg-[#101923]'}`}>E-102 (ATTN)</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span className={`px-1.5 py-0.5 rounded font-bold ${selectedAssetTag === 'E03' ? 'bg-[#0284c7] text-white' : 'bg-[#101923]'}`}>E-103</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span>V-101 DESALTER</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span className={`px-1.5 py-0.5 rounded font-bold ${selectedAssetTag === 'E04' ? 'bg-[#0284c7] text-white' : 'bg-[#101923]'}`}>E-104</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span className={`px-1.5 py-0.5 rounded font-bold ${selectedAssetTag === 'E05' ? 'bg-[#0284c7] text-white' : 'bg-[#101923]'}`}>E-105</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span>F-101 HEATER</span>
          <ArrowRight className="w-3 h-3 text-[#27b7e8]" />
          <span>C-101 CDU</span>
        </div>
      </div>

      {/* Selected Equipment Contextual Intelligence Card */}
      <div className="self-start mt-4 pointer-events-auto w-80 bg-[#071018]/95 backdrop-blur border border-[#15212d] p-4 rounded shadow-2xl space-y-3">
        <div className="flex items-center justify-between border-b border-[#15212d] pb-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-[#101923] text-[#27b7e8] font-bold text-xs border border-[#1b2a3a]">
                {selectedEquipment.tag}
              </span>
              <h3 className="font-bold text-white text-xs">{selectedEquipment.name}</h3>
            </div>
            <p className="text-[10px] text-[#6b7280] mt-0.5">{selectedEquipment.serviceName}</p>
          </div>

          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
            selectedEquipment.tag === 'E-102' || selectedAssetTag === 'E02'
              ? 'bg-[#311313] text-[#f87171] border-[#7f1d1d]'
              : 'bg-[#102a1d] text-[#34d399] border-[#065f46]'
          }`}>
            {selectedEquipment.tag === 'E-102' ? '● ATTENTION' : '● NOMINAL'}
          </span>
        </div>

        {/* Fouling & Thermal State Metrics */}
        <div className="space-y-2 text-[11px]">
          <div className="flex justify-between items-center bg-[#090e15] p-2 rounded border border-[#15212d]">
            <span className="text-[#6b7280] uppercase">FOULING STATE</span>
            <span className={`font-bold font-mono ${selectedAssetTag === 'E02' ? 'text-[#f87171]' : 'text-white'}`}>
              {selectedAssetTag === 'E02' ? 'Increasing (7.28e-8 m²·K/W)' : 'Nominal (< 1.5e-8)'}
            </span>
          </div>

          <div className="flex justify-between items-center bg-[#090e15] p-2 rounded border border-[#15212d]">
            <span className="text-[#6b7280] uppercase">THERMAL STATE</span>
            <span className="font-bold text-white font-mono">UA: 203,984 W/K (Clean 207,061)</span>
          </div>

          <div className="flex justify-between items-center bg-[#090e15] p-2 rounded border border-[#15212d]">
            <span className="text-[#6b7280] uppercase">M4.0 FORECAST</span>
            <span className="font-bold text-[#34d399] font-mono">+23.3% Impr. vs Pers.</span>
          </div>

          <div className="flex justify-between items-center bg-[#090e15] p-2 rounded border border-[#15212d]">
            <span className="text-[#6b7280] uppercase">RELIABILITY GATE</span>
            <span className={`font-bold font-mono ${isNormal ? 'text-[#34d399]' : 'text-[#f87171]'}`}>
              {isNormal ? '✓ Supported' : '✕ Abstained'}
            </span>
          </div>
        </div>

        {/* Decision Action Banner */}
        <div className={`p-2.5 rounded border text-[11px] space-y-1 ${
          isNormal
            ? 'bg-[#0c261a] border-[#10b981] text-[#a7f3d0]'
            : 'bg-[#240e0e] border-[#ef4444] text-[#fca5a5]'
        }`}>
          <div className="font-bold uppercase tracking-wider text-xs flex items-center justify-between">
            <span>{isNormal ? 'CLEANING WINDOW — REVIEW' : 'FOUL-X ABSTAINED'}</span>
            <div className="flex items-center gap-2">
              <button
                onClick={openTrustGateModal}
                className="text-[10px] underline hover:text-white cursor-pointer text-[#27b7e8]"
              >
                TRUST GATE
              </button>
              <button
                onClick={openEvidenceOverlay}
                className="text-[10px] underline hover:text-white cursor-pointer"
              >
                WHY?
              </button>
            </div>
          </div>
          <p className="text-[10px]">
            {isNormal
              ? 'Proactive 14-day cleaning window recommended for engineering approval.'
              : '"Forecast remains available, but maintenance recommendation has been withheld. Fixed cleaning policy active."'}
          </p>
        </div>
      </div>
    </div>
  );
};
