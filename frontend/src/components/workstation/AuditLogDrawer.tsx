import React from 'react';
import { ScrollText, X } from 'lucide-react';
import type { AuditLogEntry } from '../../agent/types';

interface AuditLogDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  entries: AuditLogEntry[];
}

export const AuditLogDrawer: React.FC<AuditLogDrawerProps> = ({
  isOpen,
  onClose,
  entries,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-[#071018] border-l border-[#1e293b] shadow-2xl z-50 flex flex-col font-mono text-xs text-gray-300">
      {/* Header */}
      <div className="p-3 bg-[#0b1118] border-b border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ScrollText className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-white uppercase tracking-wider">
            Agent Audit Trail ({entries.length})
          </span>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Log list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {entries.length === 0 ? (
          <div className="text-center text-gray-500 py-8 italic">
            No agent actions recorded yet.
          </div>
        ) : (
          entries.map((e) => (
            <div
              key={e.id}
              className="bg-[#0f172a] p-2.5 rounded border border-[#1e293b] space-y-1.5 text-[11px]"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-cyan-400">{e.toolName}</span>
                <span
                  className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                    e.executionStatus === 'SUCCESS'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      : e.executionStatus === 'CANCELLED'
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-rose-950 text-rose-300 border border-rose-800'
                  }`}
                >
                  {e.executionStatus}
                </span>
              </div>

              {e.transcript && (
                <div className="text-gray-400 italic">
                  "{e.transcript}"
                </div>
              )}

              <p className="text-white">{e.resultSummary}</p>

              <div className="text-[10px] text-gray-500 flex justify-between border-t border-[#1e293b] pt-1">
                <span>{new Date(e.timestamp).toLocaleTimeString()}</span>
                <span>Context: {e.context.selectedAssetTag} | {e.context.activeView}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
