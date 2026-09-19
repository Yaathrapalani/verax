import React, { useState } from 'react';
import { FolderTree, ChevronRight, ChevronDown, ArrowRight, Layers } from 'lucide-react';
import { REPRESENTATIVE_CDU_EQUIPMENT } from '../../data/representativePlant';

interface PlantExplorerProps {
  selectedAssetTag: string;
  selectedStreamId: string;
  onSelectEquipment: (tag: string) => void;
  onSelectStream: (streamId: string) => void;
}

const STREAMS = [
  { id: 'S-101', name: 'Raw Crude Supply (P-101 -> E-101)' },
  { id: 'S-102', name: 'Preheated Crude 1 (E-101 -> E-102)' },
  { id: 'S-103', name: 'Preheated Crude 2 (E-102 -> E-103)' },
  { id: 'S-104', name: 'Preheated Crude 3 (E-103 -> V-101)' },
  { id: 'S-105', name: 'Desalted Crude (V-101 -> E-104)' },
  { id: 'S-106', name: 'Hot Crude 1 (E-104 -> E-105)' },
  { id: 'S-107', name: 'Hot Crude 2 (E-105 -> F-101)' },
  { id: 'S-108', name: 'Furnace Feed to CDU (F-101 -> C-101)' },
];

export const PlantExplorer: React.FC<PlantExplorerProps> = ({
  selectedAssetTag,
  selectedStreamId,
  onSelectEquipment,
  onSelectStream,
}) => {
  const [isUnitsOpen, setIsUnitsOpen] = useState(true);
  const [isStreamsOpen, setIsStreamsOpen] = useState(true);

  return (
    <nav aria-label="Plant Explorer" className="w-64 bg-[#090e15] border-r border-[#1e293b] flex flex-col h-full text-xs font-mono text-gray-300 select-none shadow-md">
      {/* Explorer Header */}
      <div className="p-3 bg-[#0b1118] border-b border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FolderTree className="w-4 h-4 text-cyan-400" />
          <span className="font-extrabold text-white uppercase tracking-wider text-xs">
            PLANT EXPLORER
          </span>
        </div>
        <span className="text-[10px] text-gray-500">CDU-1</span>
      </div>

      {/* Tree Content */}
      <div className="flex-1 overflow-y-auto p-2 space-y-3">
        {/* Plant Root Node */}
        <div>
          <div className="flex items-center gap-1.5 font-bold text-white text-[11px] px-1 py-0.5">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>Refinery Unit 04 — CDU</span>
          </div>

          {/* Process Units Subtree */}
          <div className="ml-2 mt-1 border-l border-[#1e293b] pl-2 space-y-0.5">
            <div
              onClick={() => setIsUnitsOpen(!isUnitsOpen)}
              className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-white cursor-pointer py-1 font-semibold"
            >
              {isUnitsOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              <span>PROCESS EQUIPMENT ({REPRESENTATIVE_CDU_EQUIPMENT.length})</span>
            </div>

            {isUnitsOpen && (
              <div className="space-y-0.5 ml-2">
                {REPRESENTATIVE_CDU_EQUIPMENT.map((eq) => {
                  const isSelected = selectedAssetTag === eq.datasetTag || selectedAssetTag === eq.tag;
                  const isAttn = eq.datasetTag === 'E02' || eq.tag === 'E-102';
                  return (
                    <div
                      key={eq.tag}
                      onClick={() => onSelectEquipment(eq.tag)}
                      className={`px-2 py-1 rounded text-[11px] flex items-center justify-between cursor-pointer transition ${
                        isSelected
                          ? 'bg-[#1e293b] text-cyan-300 font-bold border border-cyan-500/40'
                          : 'text-gray-400 hover:bg-[#0f172a] hover:text-gray-200'
                      }`}
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400/60"></span>
                        <span className="truncate">{eq.tag}</span>
                      </div>
                      {isAttn && (
                        <span className="w-2 h-2 rounded-full bg-rose-400 animate-pulse"></span>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Process Streams Subtree */}
            <div
              onClick={() => setIsStreamsOpen(!isStreamsOpen)}
              className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-white cursor-pointer py-1 font-semibold mt-2"
            >
              {isStreamsOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              <span>PROCESS STREAMS ({STREAMS.length})</span>
            </div>

            {isStreamsOpen && (
              <div className="space-y-0.5 ml-2">
                {STREAMS.map((st) => {
                  const isSelected = selectedStreamId === st.id;
                  return (
                    <div
                      key={st.id}
                      onClick={() => onSelectStream(st.id)}
                      className={`px-2 py-1 rounded text-[11px] flex items-center justify-between cursor-pointer transition ${
                        isSelected
                          ? 'bg-[#1e293b] text-cyan-300 font-bold border border-cyan-500/40'
                          : 'text-gray-400 hover:bg-[#0f172a] hover:text-gray-200'
                      }`}
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <ArrowRight className="w-3 h-3 text-cyan-500" />
                        <span className="truncate">{st.id}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer System Mode */}
      <div className="p-2 border-t border-[#1e293b] bg-[#071018] text-[10px] text-gray-500 flex justify-between">
        <span>TOPOLOGY: CANONICAL</span>
        <span className="text-emerald-400 font-semibold">SYNCHRONIZED</span>
      </div>
    </nav>
  );
};
