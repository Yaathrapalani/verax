import React, { useState, useEffect } from 'react';
import { Mic, Square, CornerDownLeft, Camera, Eye, VideoOff } from 'lucide-react';
import type { AgentStatus } from '../../agent/types';
import { VoiceProviderRegistry } from '../../agent/voice/providerRegistry';
import type { VoiceProviderType } from '../../agent/voice/providerTypes';
import { voiceAssistantController, type ExplicitVoiceState } from '../../agent/voice/VoiceAssistantController';
import { facePresenceDetector, type PresenceMode, type PresenceState } from '../../agent/presence/FacePresenceDetector';

interface VoiceControlBarProps {
  agentStatus: AgentStatus;
  isListening: boolean;
  isSpeaking: boolean;
  lastTranscript: string;
  lastResponse: string;
  onToggleVoice: () => void;
  onStopSpeaking: () => void;
  onSubmitText: (text: string) => void;
  voiceSupported: boolean;
}

export const VoiceControlBar: React.FC<VoiceControlBarProps> = ({
  agentStatus,
  isListening,
  isSpeaking,
  lastTranscript,
  lastResponse,
  onToggleVoice,
  onStopSpeaking,
  onSubmitText,
  voiceSupported,
}) => {
  const [inputText, setInputText] = useState('');
  const [activeProvider, setActiveProvider] = useState<VoiceProviderType>(
    () => VoiceProviderRegistry.getInstance().getProvider().providerType
  );
  const [explicitState, setExplicitState] = useState<ExplicitVoiceState>(
    () => voiceAssistantController.getExplicitVoiceState()
  );

  // Presence State
  const [presenceMode, setPresenceMode] = useState<PresenceMode>(() => facePresenceDetector.getMode());
  const [presenceState, setPresenceState] = useState<PresenceState>(() => facePresenceDetector.getState());
  const [isCameraActive, setIsCameraActive] = useState(() => facePresenceDetector.getTelemetry().cameraActive);

  useEffect(() => {
    const unsubVoice = voiceAssistantController.subscribe(() => {
      setExplicitState(voiceAssistantController.getExplicitVoiceState());
    });

    const unsubPresence = facePresenceDetector.onStateChange((st) => {
      setPresenceState(st);
      setIsCameraActive(facePresenceDetector.getTelemetry().cameraActive);
    });

    const unsubPresenceTelem = facePresenceDetector.onTelemetry((t) => {
      setPresenceMode(t.mode);
      setIsCameraActive(t.cameraActive);
    });

    return () => {
      unsubVoice();
      unsubPresence();
      unsubPresenceTelem();
    };
  }, []);

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value as VoiceProviderType;
    VoiceProviderRegistry.getInstance().setProvider(val);
    setActiveProvider(val);
    voiceAssistantController.setProvider(val);
    setExplicitState(voiceAssistantController.getExplicitVoiceState());
  };

  const handlePresenceModeChange = async (newMode: PresenceMode) => {
    await facePresenceDetector.setMode(newMode);
    setPresenceMode(newMode);
    setIsCameraActive(facePresenceDetector.getTelemetry().cameraActive);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSubmitText(inputText);
    setInputText('');
  };

  const isPresenceDetected = presenceState === 'FACE_PRESENT';

  return (
    <div className="bg-[#0b1019] border-t border-[#1e293b] px-4 py-2 text-xs font-mono text-gray-300 flex flex-wrap items-center justify-between gap-3 shadow-lg select-none">
      {/* Left: Microphone / Agent Status */}
      <div className="flex items-center gap-2.5">
        <button
          onClick={onToggleVoice}
          title={isListening ? 'Click to stop listening' : 'Click to speak voice command (Ctrl+K)'}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-bold border transition cursor-pointer ${
            isListening
              ? 'bg-[#7f1d1d] text-white border-[#ef4444] animate-pulse'
              : 'bg-[#1e293b] hover:bg-[#334155] text-cyan-300 border-[#38bdf8]/40'
          }`}
        >
          {isListening ? <Mic className="w-3.5 h-3.5 text-rose-400" /> : <Mic className="w-3.5 h-3.5 text-cyan-400" />}
          <span>{isListening ? 'LISTENING...' : voiceSupported ? 'MIC' : 'MIC (OFFLINE)'}</span>
          <span className="text-[9px] text-gray-400 font-normal ml-0.5">^K</span>
        </button>

        {/* Barge-In / Stop Speaking Button */}
        {isSpeaking && (
          <button
            onClick={onStopSpeaking}
            title="Barge-in / Stop agent speech immediately"
            className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-bold bg-[#311313] hover:bg-[#7f1d1d] text-rose-300 border border-rose-700 transition cursor-pointer"
          >
            <Square className="w-3 h-3 fill-rose-300" />
            <span>INTERRUPT</span>
          </button>
        )}

        {/* Agent State Badge */}
        <div className="flex items-center gap-1.5 text-[11px]">
          <span
            className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
              agentStatus === 'SPEAKING'
                ? 'bg-[#064e3b] text-emerald-300 border border-[#059669]'
                : agentStatus === 'LISTENING'
                ? 'bg-[#7f1d1d] text-rose-300 border border-[#dc2626]'
                : agentStatus === 'THINKING' || agentStatus === 'EXECUTING'
                ? 'bg-[#1e293b] text-amber-300 border border-[#d97706]'
                : 'bg-[#111827] text-gray-400 border border-[#1f2937]'
            }`}
          >
            {agentStatus}
          </span>
        </div>

        {/* Explicit Provider Status (Section 3 Requirement) */}
        <div className="flex items-center gap-1">
          <span
            className={`font-bold px-2 py-0.5 rounded text-[10px] border ${
              explicitState === 'GEMINI LIVE — CONNECTED'
                ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500'
                : explicitState === 'BROWSER SPEECH — ACTIVE'
                ? 'bg-blue-950/80 text-blue-300 border-blue-500'
                : explicitState === 'TEXT MODE — ACTIVE'
                ? 'bg-gray-900 text-gray-300 border-gray-700'
                : explicitState === 'DEMO VOICE — ACTIVE'
                ? 'bg-purple-950/80 text-purple-300 border-purple-500'
                : explicitState === 'MICROPHONE — BLOCKED'
                ? 'bg-rose-950/80 text-rose-300 border-rose-600 animate-pulse'
                : explicitState === 'VOICE BACKEND — NOT CONFIGURED'
                ? 'bg-amber-950/80 text-amber-300 border-amber-600'
                : 'bg-rose-950/80 text-rose-300 border-rose-700'
            }`}
          >
            {explicitState}
          </span>
        </div>

        {/* Provider Selector */}
        <div className="hidden sm:flex items-center gap-1 border-l border-[#1e293b] pl-2">
          <select
            value={activeProvider}
            onChange={handleProviderChange}
            className="bg-[#071018] border border-[#1e293b] text-gray-400 hover:text-white rounded px-1.5 py-0.5 text-[10px] focus:outline-none focus:border-cyan-500"
            title="Switch Conversational Voice Provider"
          >
            <option value="browser-speech">PROVIDER: BROWSER SPEECH</option>
            <option value="gemini-live">PROVIDER: GEMINI 3.8 LIVE</option>
            <option value="text-only">PROVIDER: TEXT-ONLY</option>
            <option value="demo">PROVIDER: DEMO VOICE</option>
          </select>
        </div>

        {/* Privacy-Preserving Face Presence Voice Activation Control (Gate L) */}
        <div className="hidden md:flex items-center gap-1.5 border-l border-[#1e293b] pl-2 text-[10px]">
          <span className="text-gray-400 font-semibold flex items-center gap-1">
            {isCameraActive ? (
              <Camera className="w-3 h-3 text-emerald-400" />
            ) : (
              <VideoOff className="w-3 h-3 text-gray-500" />
            )}
            <span>PRESENCE:</span>
          </span>
          <div className="flex bg-[#071018] border border-[#1e293b] rounded p-0.5">
            {(['OFF', 'ARMED', 'ACTIVE'] as PresenceMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => handlePresenceModeChange(mode)}
                className={`px-1.5 py-0.5 rounded text-[9px] font-bold transition cursor-pointer ${
                  presenceMode === mode
                    ? mode === 'OFF'
                      ? 'bg-[#1e293b] text-gray-300'
                      : 'bg-cyan-900 text-cyan-200 border border-cyan-600'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>

          {/* Real-time Presence Indicators */}
          {presenceMode !== 'OFF' && (
            <div className="flex items-center gap-1 text-[9px]">
              <span
                className={`px-1 py-0.5 rounded font-bold ${
                  isCameraActive ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-gray-900 text-gray-400'
                }`}
              >
                {isCameraActive ? 'CAMERA: ACTIVE' : 'CAMERA: OFF'}
              </span>

              {presenceMode === 'ARMED' && (
                <span className="px-1 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold">
                  VOICE PRESENCE: ARMED
                </span>
              )}

              <span
                className={`px-1 py-0.5 rounded font-bold flex items-center gap-0.5 ${
                  isPresenceDetected
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-600 animate-pulse'
                    : 'bg-gray-900 text-gray-500 border border-gray-800'
                }`}
              >
                <Eye className="w-2.5 h-2.5" />
                {isPresenceDetected ? 'PRESENCE DETECTED' : 'NO OPERATOR'}
              </span>

              {isPresenceDetected && (
                <span className="px-1 py-0.5 rounded bg-emerald-900 text-emerald-100 font-bold">
                  VOICE READY
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Center: Live Transcript & Agent Concise Feedback */}
      <div className="flex-1 max-w-2xl min-w-[240px] bg-[#071018] border border-[#1e293b] px-3 py-1 rounded flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 truncate text-[11px]">
          {lastTranscript ? (
            <span className="text-gray-400 truncate">
              <span className="text-cyan-400 font-bold">USER:</span> "{lastTranscript}"
            </span>
          ) : (
            <span className="text-gray-500 italic truncate">
              Voice: "Show me E-102", "Why?", "What's missing?", "What am I looking at?"...
            </span>
          )}
        </div>

        {lastResponse && (
          <div className="text-emerald-400 truncate font-semibold text-[11px] border-l border-[#1e293b] pl-2 max-w-[320px]">
            {lastResponse}
          </div>
        )}
      </div>

      {/* Right: Quick text input fallback */}
      <form onSubmit={handleSubmit} className="flex items-center gap-1.5">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Command workstation..."
          className="bg-[#071018] border border-[#334155] rounded px-2.5 py-1 text-xs text-white placeholder-gray-500 w-40 focus:w-56 transition-all focus:border-cyan-500 focus:outline-none"
        />
        <button
          type="submit"
          className="p-1 bg-[#1e293b] hover:bg-[#334155] text-cyan-400 border border-[#334155] rounded cursor-pointer"
          title="Send command"
        >
          <CornerDownLeft className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
