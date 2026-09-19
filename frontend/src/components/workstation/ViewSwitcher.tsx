import React from 'react';
import { Eye, Network, Box, Cpu, GitPullRequest, FlaskConical } from 'lucide-react';
import type { WorkstationView } from '../../agent/types';

interface ViewSwitcherProps {
  activeView: WorkstationView;
  onChangeView: (view: WorkstationView) => void;
}

const VIEWS: Array<{ id: WorkstationView; label: string; icon: React.FC<{ className?: string }> }> = [
  { id: 'PROCESS', label: 'PROCESS', icon: Network },
  { id: '3D', label: '3D SPATIAL', icon: Box },
  { id: 'PND', label: 'P&ID SCHEMATIC', icon: Eye },
  { id: 'SIMULATION', label: 'SIMULATION', icon: Cpu },
  { id: 'EVIDENCE', label: 'EVIDENCE GRAPH', icon: GitPullRequest },
  { id: 'CHEMISTRY', label: 'CHEMISTRY', icon: FlaskConical },
];

export const ViewSwitcher: React.FC<ViewSwitcherProps> = ({
  activeView,
  onChangeView,
}) => {
  return (
    <div className="flex items-center bg-[#071018] p-1 rounded border border-[#1e293b] gap-1 select-none">
      {VIEWS.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => onChangeView(id)}
          className={`flex items-center gap-1 px-2.5 py-1 text-[10px] font-bold font-mono rounded transition cursor-pointer ${
            activeView === id
              ? 'bg-[#1e293b] text-cyan-300 border border-cyan-500/50 shadow-sm'
              : 'text-gray-400 hover:text-white hover:bg-[#0f172a]'
          }`}
        >
          <Icon className="w-3 h-3" />
          <span>{label}</span>
        </button>
      ))}
    </div>
  );
};
