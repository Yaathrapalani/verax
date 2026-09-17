export type InspectionMode = 'NORMAL' | 'CUTAWAY' | 'PROCESS';

export interface PlantEquipment {
  tag: string;
  name: string;
  category: 'EXCHANGER' | 'PUMP' | 'DESALTER' | 'FLASH_DRUM' | 'FURNACE' | 'COLUMN';
  serviceName: string;
  position: [number, number, number]; // [x, y, z] in 3D scene space
  scale?: [number, number, number];
  status: 'NOMINAL' | 'ATTENTION' | 'CRITICAL';
  isMonitoredByFoulX: boolean;
  datasetTag?: string; // E.g., 'E01'...'E05'
}

export interface ReplayFrame {
  timestampIndex: number;
  timeHr: number;
  formattedTimestamp: string;
  currentRf: number;
  uaCurrent: number;
  thermalDiscrepancy: number;
  isAttentionState: boolean;
}

export interface IntelligenceCopilotState {
  currentAssetTag: string;
  activeScenario: 'normal' | 'disturbed';
  isListening: boolean;
  isAnalyzing: boolean;
  transcript: string;
  copilotResponse: string;
  copilotHistory: Array<{ sender: 'USER' | 'FOUL-X'; text: string; timestamp: string }>;
}
