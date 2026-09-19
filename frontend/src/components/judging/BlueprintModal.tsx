import React, { useState } from 'react';
import { FileCode, Layers, Info } from 'lucide-react';

interface BlueprintModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BlueprintModal: React.FC<BlueprintModalProps> = ({ isOpen, onClose }) => {
  const [activeDoc, setActiveDoc] = useState<'PFD' | 'PID' | 'DATASHEET'>('PFD');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#071018] border border-[#15212d] w-full max-w-4xl rounded shadow-2xl overflow-hidden flex flex-col max-h-[90vh] font-mono text-xs">
        {/* Header */}
        <div className="p-4 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-[#a78bfa]" />
            <div>
              <h2 className="font-extrabold uppercase text-white text-sm tracking-wider">
                BLUEPRINT & PROCESS DOCUMENTATION CONTEXT
              </h2>
              <p className="text-[10px] text-[#6b7280]">
                Conceptual visualization of PFD, P&ID, and equipment datasheets mapped to the canonical plant model.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="px-2.5 py-1 bg-[#15212d] hover:bg-[#1f2d3d] text-white rounded text-[11px] font-bold cursor-pointer transition"
          >
            CLOSE [ESC]
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Document Type Selector */}
          <div className="flex items-center gap-2 border-b border-[#15212d] pb-3">
            {[
              { id: 'PFD', label: 'PROCESS FLOW DIAGRAM (PFD-CDU-01)' },
              { id: 'PID', label: 'PIPING & INSTRUMENTATION (P&ID-E102-04)' },
              { id: 'DATASHEET', label: 'EQUIPMENT DATASHEET (DS-E102)' },
            ].map((doc) => (
              <button
                key={doc.id}
                onClick={() => setActiveDoc(doc.id as any)}
                className={`px-3 py-1.5 rounded text-xs font-bold border transition cursor-pointer ${
                  activeDoc === doc.id
                    ? 'bg-[#1e1b4b] border-[#a78bfa] text-[#c4b5fd]'
                    : 'bg-[#090e15] border-[#15212d] text-[#6b7280] hover:text-white'
                }`}
              >
                {doc.label}
              </button>
            ))}
          </div>

          {/* Conceptual Blueprint Visual Box */}
          <div className="bg-[#050b11] border border-[#1b2a3a] p-6 rounded relative flex flex-col items-center justify-center min-h-[250px]">
            <div className="absolute top-3 left-3 text-[10px] text-[#6b7280] flex items-center gap-1 font-bold">
              <Layers className="w-3.5 h-3.5 text-[#a78bfa]" />
              <span>CANONICAL REPRESENTATIVE BLUEPRINT VIEW</span>
            </div>

            {/* Document Content Display */}
            {activeDoc === 'PFD' && (
              <div className="w-full space-y-4 text-center">
                <div className="p-4 bg-[#090e15] border border-[#15212d] rounded text-[#d1d5db]">
                  <span className="font-bold text-white block text-sm">CRUDE PREHEAT TRAIN PROCESS TOPOLOGY</span>
                  <p className="text-[11px] text-[#9ca3af] mt-1">
                    CRUDE FEED → P-101 → E-101 → E-102 (ATTN) → E-103 → DESALTER → E-104 → E-105 → PRE-FLASH → F-101 → C-101
                  </p>
                </div>

                <div className="grid grid-cols-4 gap-2 text-[10px]">
                  <div className="p-2 bg-[#0b1118] border border-[#15212d] rounded">
                    <span className="text-[#34d399] font-bold block">OBSERVED FROM SOURCE</span>
                    <span>Thermal Telemetry (T, m)</span>
                  </div>
                  <div className="p-2 bg-[#0b1118] border border-[#15212d] rounded">
                    <span className="text-[#a78bfa] font-bold block">INFERRED</span>
                    <span>Fouling Resistance R_f</span>
                  </div>
                  <div className="p-2 bg-[#0b1118] border border-[#15212d] rounded">
                    <span className="text-[#27b7e8] font-bold block">REPRESENTATIVE</span>
                    <span>3D Geometry Layout</span>
                  </div>
                  <div className="p-2 bg-[#0b1118] border border-[#15212d] rounded">
                    <span className="text-[#6b7280] font-bold block">UNAVAILABLE</span>
                    <span>DP Pressure Sensors</span>
                  </div>
                </div>
              </div>
            )}

            {activeDoc === 'PID' && (
              <div className="w-full space-y-3 font-mono text-[11px]">
                <div className="p-3 bg-[#090e15] border border-[#15212d] rounded space-y-1">
                  <span className="font-bold text-[#c4b5fd]">P&ID TAG MAPPING (E-102 KEROSENE EXCHANGER)</span>
                  <div className="grid grid-cols-2 gap-2 pt-2 text-[#9ca3af]">
                    <div>Tube In Temp Sensor: <span className="text-white font-bold">TI-102A (Crude)</span></div>
                    <div>Tube Out Temp Sensor: <span className="text-white font-bold">TI-102B (Crude)</span></div>
                    <div>Shell In Temp Sensor: <span className="text-white font-bold">TI-102C (Kero)</span></div>
                    <div>Shell Out Temp Sensor: <span className="text-white font-bold">TI-102D (Kero)</span></div>
                  </div>
                </div>
              </div>
            )}

            {activeDoc === 'DATASHEET' && (
              <div className="w-full space-y-3 font-mono text-[11px]">
                <div className="p-3 bg-[#090e15] border border-[#15212d] rounded space-y-1">
                  <span className="font-bold text-[#fbbf24]">EQUIPMENT SPECIFICATION (E-102)</span>
                  <div className="grid grid-cols-2 gap-2 pt-2 text-[#9ca3af]">
                    <div>Clean UA Reference: <span className="text-white font-bold">207,061 W/K</span></div>
                    <div>Surface Area A: <span className="text-white font-bold">450 m²</span></div>
                    <div>Shell Service: <span className="text-white font-bold">Kerosene Rundown</span></div>
                    <div>Tube Service: <span className="text-white font-bold">Raw Crude Oil</span></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Scientific Disclaimer */}
          <div className="bg-[#090e15] p-3 rounded border border-[#15212d] flex items-center gap-3">
            <Info className="w-4 h-4 text-[#27b7e8] shrink-0" />
            <p className="text-[10px] text-[#9ca3af]">
              The representative refinery topology remains the canonical demo blueprint. FOUL-X does not claim automatic 3D reconstruction from unmapped CAD/P&ID files.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
