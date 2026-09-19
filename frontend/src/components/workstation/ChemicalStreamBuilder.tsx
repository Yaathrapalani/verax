import React, { useState } from 'react';
import { FlaskConical, Trash2, Info } from 'lucide-react';
import type { ChemicalStream, ChemicalComponent } from '../../agent/types';

interface ChemicalStreamBuilderProps {
  stream: ChemicalStream;
  onUpdateStream: (updated: ChemicalStream) => void;
}

const REFERENCE_COMPONENTS = [
  { id: 'H2O', name: 'Water', formula: 'H2O' },
  { id: 'EtOH', name: 'Ethanol', formula: 'C2H5OH' },
  { id: 'CH4', name: 'Methane', formula: 'CH4' },
  { id: 'C3H8', name: 'Propane', formula: 'C3H8' },
  { id: 'C7H8', name: 'Toluene', formula: 'C7H8' },
];

export const ChemicalStreamBuilder: React.FC<ChemicalStreamBuilderProps> = ({
  stream,
  onUpdateStream,
}) => {
  const [streamId, setStreamId] = useState(stream.streamId);
  const [phase, setPhase] = useState(stream.phase);
  const [basis, setBasis] = useState(stream.compositionBasis);
  const [components, setComponents] = useState<ChemicalComponent[]>(stream.components);
  const [tempK, setTempK] = useState(stream.temperatureK);
  const [pressureBar, setPressureBar] = useState(stream.pressureBar);
  const [flowKgH, setFlowKgH] = useState(stream.massFlowKgH);

  // Validation
  const fractionSum = components.reduce((acc, c) => acc + c.fraction, 0);
  const isFractionValid = Math.abs(fractionSum - 1.0) < 0.001;
  const isStateValid = tempK > 0 && pressureBar > 0 && flowKgH >= 0;

  const handleFractionChange = (idx: number, val: number) => {
    const next = [...components];
    next[idx].fraction = val;
    setComponents(next);
  };

  const handleAddComponent = (comp: { id: string; name: string; formula: string }) => {
    if (components.some((c) => c.id === comp.id)) return;
    setComponents([...components, { ...comp, fraction: 0 }]);
  };

  const handleRemoveComponent = (idx: number) => {
    setComponents(components.filter((_, i) => i !== idx));
  };

  const handleApply = () => {
    onUpdateStream({
      ...stream,
      streamId,
      phase,
      compositionBasis: basis,
      components,
      temperatureK: tempK,
      pressureBar,
      massFlowKgH: flowKgH,
    });
  };

  return (
    <div className="bg-[#0b1019] border border-[#1e293b] rounded p-4 font-mono text-xs text-gray-300 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
        <div className="flex items-center gap-2">
          <FlaskConical className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-white uppercase tracking-wider">
            Chemical Stream Builder — {streamId}
          </span>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#1e293b] text-cyan-300 border border-[#334155]">
          STAGE 13 INTERACTION BOUNDARY
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Stream Definition Inputs */}
        <div className="space-y-3 bg-[#0f172a] p-3 rounded border border-[#1e293b]">
          <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1">
            Stream Parameters (USER_DEFINED_INPUT)
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[10px] text-gray-400 block mb-1">STREAM ID</label>
              <input
                type="text"
                value={streamId}
                onChange={(e) => setStreamId(e.target.value.toUpperCase())}
                className="w-full bg-[#0b1019] border border-[#334155] rounded px-2 py-1 text-white text-xs font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-400 block mb-1">PHASE SPECIFICATION</label>
              <select
                value={phase}
                onChange={(e) => setPhase(e.target.value as any)}
                className="w-full bg-[#0b1019] border border-[#334155] rounded px-2 py-1 text-white text-xs font-mono"
              >
                <option value="LIQUID">LIQUID</option>
                <option value="VAPOR">VAPOR</option>
                <option value="TWO_PHASE">TWO_PHASE</option>
                <option value="UNKNOWN">UNKNOWN</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-[10px] text-gray-400 block mb-1">TEMPERATURE (K)</label>
              <input
                type="number"
                step="0.1"
                value={tempK}
                onChange={(e) => setTempK(Number(e.target.value))}
                className="w-full bg-[#0b1019] border border-[#334155] rounded px-2 py-1 text-white text-xs font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-gray-400 block mb-1">PRESSURE (bar)</label>
              <input
                type="number"
                step="0.05"
                value={pressureBar}
                onChange={(e) => setPressureBar(Number(e.target.value))}
                className="w-full bg-[#0b1019] border border-[#334155] rounded px-2 py-1 text-white text-xs font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-gray-400 block mb-1">MASS FLOW (kg/h)</label>
              <input
                type="number"
                step="10"
                value={flowKgH}
                onChange={(e) => setFlowKgH(Number(e.target.value))}
                className="w-full bg-[#0b1019] border border-[#334155] rounded px-2 py-1 text-white text-xs font-mono"
              />
            </div>
          </div>

          {/* Composition Basis */}
          <div>
            <label className="text-[10px] text-gray-400 block mb-1">COMPOSITION BASIS</label>
            <div className="flex gap-2">
              {(['MOLE_FRACTION', 'MASS_FRACTION'] as const).map((b) => (
                <button
                  key={b}
                  onClick={() => setBasis(b)}
                  className={`flex-1 py-1 text-[10px] font-bold rounded border transition ${
                    basis === b
                      ? 'bg-[#1e293b] text-cyan-300 border-cyan-500'
                      : 'bg-[#0b1019] text-gray-400 border-[#334155]'
                  }`}
                >
                  {b.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Component Selection & Fractions */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-[10px] text-gray-400">
              <span>CHEMICAL COMPONENTS</span>
              <span className={isFractionValid ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                Σ Fraction: {fractionSum.toFixed(3)} / 1.000
              </span>
            </div>

            {components.map((comp, idx) => (
              <div key={comp.id} className="flex items-center gap-2 bg-[#0b1019] p-1.5 rounded border border-[#1e293b]">
                <span className="w-16 font-bold text-white text-[11px]">{comp.id}</span>
                <span className="text-[10px] text-gray-400 flex-1">{comp.name}</span>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={comp.fraction}
                  onChange={(e) => handleFractionChange(idx, Number(e.target.value))}
                  className="w-20 bg-[#0f172a] border border-[#334155] rounded px-1.5 py-0.5 text-white text-xs font-mono text-right"
                />
                <button
                  onClick={() => handleRemoveComponent(idx)}
                  className="text-gray-500 hover:text-rose-400 p-0.5"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}

            {/* Quick Add Component */}
            <div className="flex flex-wrap gap-1 mt-2">
              <span className="text-[10px] text-gray-500 mr-1 flex items-center">Add:</span>
              {REFERENCE_COMPONENTS.map((rc) => (
                <button
                  key={rc.id}
                  onClick={() => handleAddComponent(rc)}
                  disabled={components.some((c) => c.id === rc.id)}
                  className="px-2 py-0.5 bg-[#0b1019] hover:bg-[#1e293b] disabled:opacity-40 border border-[#334155] rounded text-[10px] text-gray-300 font-mono"
                >
                  +{rc.id}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleApply}
            disabled={!isFractionValid || !isStateValid}
            className="w-full py-1.5 bg-[#1e293b] hover:bg-[#334155] disabled:opacity-40 text-cyan-300 border border-cyan-500/50 rounded font-bold text-xs uppercase tracking-wider transition"
          >
            Apply Stream Definition
          </button>
        </div>

        {/* Thermodynamic Calculation State & Honesty Inspection */}
        <div className="space-y-3 bg-[#0f172a] p-3 rounded border border-[#1e293b]">
          <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wide border-b border-[#1e293b] pb-1 flex justify-between">
            <span>Thermodynamic State (CALCULATED_PROPERTY)</span>
            <span className="text-purple-400 font-bold">STAGE 13</span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center bg-[#0b1019] p-2 rounded border border-[#1e293b]">
              <span className="text-gray-400">Stream Phase:</span>
              <span className="font-bold text-white">{phase}</span>
            </div>

            <div className="flex justify-between items-center bg-[#0b1019] p-2 rounded border border-[#1e293b]">
              <span className="text-gray-400">Property Package:</span>
              <span className="text-cyan-400 font-semibold">IDEAL_GAS (Vapor only)</span>
            </div>

            <div className="flex justify-between items-center bg-[#0b1019] p-2 rounded border border-[#1e293b]">
              <span className="text-gray-400">Density ($ρ$):</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#1e293b] text-gray-400">
                UNAVAILABLE
              </span>
            </div>

            <div className="flex justify-between items-center bg-[#0b1019] p-2 rounded border border-[#1e293b]">
              <span className="text-gray-400">Viscosity ($μ$):</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#1e293b] text-gray-400">
                UNAVAILABLE
              </span>
            </div>

            <div className="flex justify-between items-center bg-[#0b1019] p-2 rounded border border-[#1e293b]">
              <span className="text-gray-400">Enthalpy ($h$):</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#1e293b] text-gray-400">
                UNAVAILABLE
              </span>
            </div>

            <div className="flex justify-between items-center bg-[#0b1019] p-2 rounded border border-[#1e293b]">
              <span className="text-gray-400">Equation of State:</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#311313] text-rose-300 border border-rose-800">
                UNSUPPORTED
              </span>
            </div>
          </div>

          <div className="p-2.5 bg-[#0b1019] rounded border border-amber-900/50 text-amber-300/90 text-[10px] space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-amber-400">
              <Info className="w-3.5 h-3.5 shrink-0" />
              <span>Scientific Integrity Notice</span>
            </div>
            <p>
              PLANT-X Stage 13 only supports analytical IDEAL_GAS state properties for vapor mixtures.
              Real-fluid liquid density, viscosity, and enthalpy are intentionally flagged as UNAVAILABLE
              rather than approximated with unvalidated equations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
