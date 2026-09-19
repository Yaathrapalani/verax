import React, { useState } from 'react';
import { UploadCloud, FileText, ShieldAlert, AlertCircle } from 'lucide-react';

interface IndustrialIntakeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const IndustrialIntakeModal: React.FC<IndustrialIntakeModalProps> = ({ isOpen, onClose }) => {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isHovered, setIsHovered] = useState(false);

  if (!isOpen) return null;

  const handleSimulatedDrop = (fileType: string) => {
    if (!uploadedFiles.includes(fileType)) {
      setUploadedFiles((prev) => [...prev, fileType]);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#071018] border border-[#15212d] w-full max-w-4xl rounded shadow-2xl overflow-hidden flex flex-col max-h-[90vh] font-mono text-xs">
        {/* Header */}
        <div className="p-4 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-[#27b7e8]" />
            <div>
              <h2 className="font-extrabold uppercase text-white text-sm tracking-wider">
                INDUSTRIAL PLANT DATA & EVIDENCE INTAKE PORTAL
              </h2>
              <p className="text-[10px] text-[#6b7280]">
                Platform Architecture — Ingesting plant records as evidence without model retraining leakage.
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
          {/* Explicit Scientific Boundary Banner */}
          <div className="bg-[#0b1622] p-4 rounded border border-[#1b2a3a] space-y-2">
            <div className="flex items-center gap-2 text-[#fbbf24] font-bold text-xs uppercase">
              <ShieldAlert className="w-4 h-4" />
              <span>CORE DATA & TRAINING BOUNDARY DISCLAIMER</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px]">
              <div className="bg-[#071018] p-3 rounded border border-[#15212d]">
                <span className="text-[#27b7e8] font-bold block uppercase mb-1">CURRENT MODEL BENCHMARK</span>
                <p className="text-[#d1d5db]">
                  1 validated dataset: <code className="text-[#34d399] font-mono">data/raw/heat_exchanger_fouling_dataset.csv</code>
                  <br />
                  Synthetic physics-based heat-exchanger fouling benchmark (64,000 hourly rows). SHA-256 verified.
                </p>
              </div>

              <div className="bg-[#071018] p-3 rounded border border-[#15212d]">
                <span className="text-[#fbbf24] font-bold block uppercase mb-1">INDUSTRIAL INTAKE</span>
                <p className="text-[#d1d5db]">
                  Additional plant files may be ingested as evidence/context. They are <strong className="text-white">NOT</strong> automatically used for model training.
                </p>
              </div>
            </div>
          </div>

          {/* Drag & Drop Visual Area */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsHovered(true);
            }}
            onDragLeave={() => setIsHovered(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsHovered(false);
              handleSimulatedDrop('Plant_Historian_Export_2026.csv');
            }}
            className={`border-2 border-dashed p-8 rounded-lg flex flex-col items-center justify-center text-center transition-all ${
              isHovered ? 'bg-[#0f1d2a] border-[#27b7e8]' : 'bg-[#050b11] border-[#1b2a3a]'
            }`}
          >
            <UploadCloud className="w-10 h-10 text-[#27b7e8] mb-2 animate-bounce" />
            <h3 className="font-extrabold text-white text-sm uppercase tracking-wider">
              DROP / IMPORT INDUSTRIAL DATA
            </h3>
            <p className="text-[11px] text-[#6b7280] max-w-md mt-1 mb-4">
              Attach historian telemetry, P&IDs, equipment datasheets, maintenance logs, or process reports as scientific evidence context.
            </p>

            {/* Quick Demo Sample Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-2">
              {[
                'CSV Telemetry',
                'XLSX Historian',
                'JSON Stream',
                'Parquet Data',
                'PDF Datasheet',
                'PFD Blueprint',
                'P&ID Drawing',
                'Maintenance Log',
              ].map((fmt) => (
                <button
                  key={fmt}
                  onClick={() => handleSimulatedDrop(fmt)}
                  className="px-2.5 py-1 bg-[#0b1118] hover:bg-[#15212d] border border-[#1b2a3a] text-[#27b7e8] rounded text-[10px] font-bold cursor-pointer transition"
                >
                  + Add {fmt}
                </button>
              ))}
            </div>
          </div>

          {/* Ingestion Pipeline Architecture */}
          <div className="bg-[#090e15] p-4 rounded border border-[#15212d] space-y-3">
            <span className="text-[10px] text-[#6b7280] font-bold uppercase tracking-wider block">
              INTAKE PIPELINE STAGES
            </span>

            <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-center text-[10px]">
              {[
                { stage: '1. INGEST', desc: 'Raw Format Ingestion' },
                { stage: '2. IDENTIFY', desc: 'Asset Tag Extraction' },
                { stage: '3. VALIDATE', desc: 'Schema & Bounds Check' },
                { stage: '4. MAP', desc: 'Canonical Mapping' },
                { stage: '5. MODEL', desc: 'Process Graph Sync' },
                { stage: '6. CONTEXT', desc: 'Evidence Integration' },
              ].map((s) => (
                <div key={s.stage} className="bg-[#0b1118] p-2 rounded border border-[#15212d]">
                  <span className="font-bold text-[#27b7e8] block">{s.stage}</span>
                  <span className="text-[#9ca3af] text-[9px]">{s.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Ingested Files Status */}
          <div className="space-y-2">
            <span className="text-[10px] text-[#6b7280] font-bold uppercase tracking-wider block">
              EVIDENCE INTAKE STATUS
            </span>

            {uploadedFiles.length === 0 ? (
              <div className="bg-[#090e15] p-4 rounded border border-[#15212d] text-center text-[#6b7280]">
                "Awaiting plant evidence — No additional files attached for current session"
              </div>
            ) : (
              <div className="space-y-2">
                {uploadedFiles.map((file, i) => (
                  <div
                    key={i}
                    className="bg-[#0b1118] p-3 rounded border border-[#15212d] flex flex-col md:flex-row md:items-center justify-between gap-2 text-[11px]"
                  >
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-[#27b7e8]" />
                      <span className="font-bold text-white">{file}</span>
                      <span className="px-1.5 py-0.5 rounded bg-[#064e3b] text-[#6ee7b7] text-[9px] font-bold">
                        INGESTED AS EVIDENCE
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-[10px] text-[#9ca3af]">
                      <span>Source: User Attach</span>
                      <span>Confidence: 1.00</span>
                      <span className="text-[#fbbf24] font-bold flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        UNRESOLVED — ENGINEERING MAPPING REQUIRED
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
