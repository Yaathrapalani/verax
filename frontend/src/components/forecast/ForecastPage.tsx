import React, { useEffect, useState } from 'react';
import type { ForecastMetrics, ForecastPoint, HorizonHours, ScenarioMode } from '../../types/foulx';
import { apiService } from '../../services/api';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { TrendingUp, Clock } from 'lucide-react';

interface ForecastPageProps {
  selectedExchanger: string;
  setSelectedExchanger: (tag: string) => void;
  scenario: ScenarioMode;
}

export const ForecastPage: React.FC<ForecastPageProps> = ({ selectedExchanger, setSelectedExchanger, scenario }) => {
  const [horizon, setHorizon] = useState<HorizonHours>(24);
  const [trajectory, setTrajectory] = useState<ForecastPoint[]>([]);
  const [metrics, setMetrics] = useState<ForecastMetrics | null>(null);

  useEffect(() => {
    apiService.setScenario(scenario);
    apiService.getForecastTrajectory(selectedExchanger, horizon).then(setTrajectory);
    apiService.getForecastMetrics(selectedExchanger, horizon).then(setMetrics);
  }, [selectedExchanger, horizon, scenario]);

  const tagList = ['E01', 'E02', 'E03', 'E04', 'E05'];

  return (
    <div className="space-y-6 text-xs">
      {/* Selector Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#11151e] p-3 rounded border border-[#1e2638]">
        {/* Exchanger selector */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#6b7280]">EXCHANGER:</span>
          <div className="flex items-center gap-1">
            {tagList.map((tag) => (
              <button
                key={tag}
                onClick={() => setSelectedExchanger(tag)}
                className={`px-2.5 py-1 rounded font-mono font-bold transition cursor-pointer ${
                  selectedExchanger === tag
                    ? 'bg-[#1e293b] text-[#38bdf8] border border-[#0284c7]'
                    : 'bg-[#161c28] text-[#9ca3af] hover:text-white border border-[#232c3d]'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Horizon selector */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#6b7280] flex items-center gap-1">
            <Clock className="w-3 h-3 text-[#38bdf8]" />
            FORECAST HORIZON:
          </span>
          <div className="flex items-center gap-1">
            {([1, 6, 24] as HorizonHours[]).map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`px-3 py-1 rounded font-mono font-bold transition cursor-pointer ${
                  horizon === h
                    ? 'bg-[#0284c7] text-white shadow'
                    : 'bg-[#161c28] text-[#9ca3af] hover:text-white border border-[#232c3d]'
                }`}
              >
                {h}h
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Model Spec & Evaluation Metrics Banner */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 bg-[#11151e] p-4 rounded border border-[#1e2638]">
          <div>
            <span className="text-[10px] text-[#6b7280] uppercase font-bold block">MODEL ARCHITECTURE</span>
            <span className="font-mono font-bold text-white text-xs">StandardScaler + Ridge</span>
          </div>

          <div>
            <span className="text-[10px] text-[#6b7280] uppercase font-bold block">VALIDATION MAE</span>
            <span className="font-mono font-bold text-[#38bdf8] text-xs">{metrics.mae.toExponential(4)}</span>
          </div>

          <div>
            <span className="text-[10px] text-[#6b7280] uppercase font-bold block">PERSISTENCE IMPR.</span>
            <span className="font-mono font-bold text-[#34d399] text-xs">+{metrics.relativeImprovementPct.toFixed(2)}%</span>
          </div>

          <div>
            <span className="text-[10px] text-[#6b7280] uppercase font-bold block">BEST ALPHA (α)</span>
            <span className="font-mono font-bold text-white text-xs">{metrics.bestAlpha}</span>
          </div>

          <div>
            <span className="text-[10px] text-[#6b7280] uppercase font-bold block">DETERMINISTIC EVAL</span>
            <span className="font-mono font-bold text-[#a78bfa] text-xs">NMAE = {metrics.nmaeStd.toFixed(3)}</span>
          </div>
        </div>
      )}

      {/* Trajectory Forecast Chart */}
      <div className="bg-[#11151e] p-5 rounded border border-[#1e2638] space-y-4">
        <div className="flex items-center justify-between border-b border-[#182030] pb-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[#38bdf8]" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-white">
              FOULING RESISTANCE FORECAST TRAJECTORY ({selectedExchanger} — {horizon}H HORIZON)
            </h2>
          </div>
          <span className="text-[10px] text-[#6b7280]">Real M4.0 Evaluated Model Metadata</span>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trajectory} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
              <XAxis dataKey="timestamp" stroke="#6b7280" tick={{ fontSize: 10 }} />
              <YAxis 
                stroke="#6b7280" 
                tick={{ fontSize: 10 }}
                tickFormatter={(val) => val.toExponential(1)}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f1218', borderColor: '#1f293d', fontSize: '11px' }} 
                formatter={(value: any) => [typeof value === 'number' ? value.toExponential(4) : value, '']}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />

              <Line 
                type="monotone" 
                dataKey="historicalRf" 
                name="Historical R_f(t)" 
                stroke="#94a3b8" 
                strokeWidth={2} 
                dot={{ r: 2 }}
              />

              <Line 
                type="monotone" 
                dataKey="ridgeForecast" 
                name="M4.0 Ridge Forecast R_f(t+h)" 
                stroke="#38bdf8" 
                strokeWidth={2.5} 
                dot={{ r: 3 }}
              />

              <Line 
                type="monotone" 
                dataKey="persistenceBaseline" 
                name="Persistence Baseline R_f(t)" 
                stroke="#f59e0b" 
                strokeDasharray="4 4" 
                strokeWidth={1.5}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
