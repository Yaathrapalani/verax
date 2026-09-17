import React from 'react';
import { Database, AlertTriangle } from 'lucide-react';

interface ProvenanceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ProvenanceModal: React.FC<ProvenanceModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#071018] border border-[#15212d] w-full max-w-4xl rounded shadow-2xl overflow-hidden flex flex-col max-h-[90vh] font-mono text-xs">
        {/* Header */}
        <div className="p-4 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-[#fbbf24]" />
            <div>
              <h2 className="font-extrabold uppercase text-white text-sm tracking-wider">
                FOUL-X MODEL PROVENANCE & DATASET TRANSPARENCY
              </h2>
              <p className="text-[10px] text-[#6b7280]">
                Strict data boundary and cryptographic verification of the validated benchmark dataset.
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
          {/* Main Provenance Card */}
          <div className="bg-[#0b1622] p-5 rounded border border-[#1b2a3a] space-y-4">
            <div className="flex items-center justify-between border-b border-[#15212d] pb-3">
              <div>
                <span className="text-[10px] text-[#27b7e8] font-bold uppercase tracking-wider block">TRAINING & BENCHMARK DATASET</span>
                <h3 className="font-extrabold text-white text-base">Synthetic Physics-Based Heat-Exchanger Fouling Benchmark</h3>
              </div>
              <span className="px-2.5 py-1 rounded bg-[#064e3b] text-[#6ee7b7] font-bold text-[10px] border border-[#10b981]">
                ✓ VERIFIED IMMUTABLE
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px]">
              <div className="space-y-2">
                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Dataset Relative Path:</span>
                  <span className="text-[#34d399] font-bold">data/raw/heat_exchanger_fouling_dataset.csv</span>
                </div>

                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Total Row Count:</span>
                  <span className="text-white font-bold">64,000 hourly rows</span>
                </div>

                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Monitored Exchangers:</span>
                  <span className="text-white font-bold">E01, E02, E03, E04, E05</span>
                </div>

                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Sampling Frequency:</span>
                  <span className="text-white font-bold">1.0 hour</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Training Split (t):</span>
                  <span className="text-white font-bold">t = 0 to 44,799 (44,800 h)</span>
                </div>

                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Validation Split (t):</span>
                  <span className="text-white font-bold">t = 44,800 to 54,399 (9,600 h)</span>
                </div>

                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Test Split (t):</span>
                  <span className="text-white font-bold">t = 54,400 to 63,999 (9,600 h)</span>
                </div>

                <div className="flex justify-between bg-[#071018] p-2 rounded border border-[#15212d]">
                  <span className="text-[#6b7280]">Temporal Integrity:</span>
                  <span className="text-[#34d399] font-bold">Strict Time Order (No Random Split)</span>
                </div>
              </div>
            </div>

            {/* SHA-256 Cryptographic Checksum Box */}
            <div className="bg-[#050b11] p-3 rounded border border-[#15212d] space-y-1">
              <span className="text-[10px] text-[#fbbf24] font-bold uppercase block">CRYPTOGRAPHIC CHECKSUM (SHA-256)</span>
              <code className="text-[#34d399] font-bold text-xs break-all block bg-[#071018] p-2 rounded border border-[#1b2a3a]">
                c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9
              </code>
            </div>
          </div>

          {/* Important Scientific Assertion */}
          <div className="bg-[#240e0e] border border-[#ef4444] p-4 rounded text-[#fca5a5] space-y-1">
            <div className="flex items-center gap-2 font-bold text-xs uppercase">
              <AlertTriangle className="w-4 h-4 text-[#ef4444]" />
              <span>NON-NEGOTIABLE SCIENTIFIC BOUNDARY</span>
            </div>
            <p className="text-[11px] text-[#fecaca]">
              Current model is trained and benchmarked ONLY on this single validated dataset. Attached plant files or ingested evidence are strictly excluded from automated model retraining.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
