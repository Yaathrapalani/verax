import React, { useState } from 'react';
import type { IntelligenceCopilotState } from '../../types/plant';
import { Mic, MicOff, Send, Cpu, Bot, User } from 'lucide-react';

interface FoulXCopilotProps {
  state: IntelligenceCopilotState;
  selectedAssetTag: string;
  scenario: 'normal' | 'disturbed';
  onSendMessage: (text: string) => void;
  openEvidenceOverlay: () => void;
}

export const FoulXCopilot: React.FC<FoulXCopilotProps> = ({
  state,
  selectedAssetTag,
  scenario,
  onSendMessage,
  openEvidenceOverlay,
}) => {
  const [inputText, setInputText] = useState('');
  const [isVoiceActive, setIsVoiceActive] = useState(false);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Browser Speech Recognition not available on this environment. Voice fallback enabled for typing.');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    if (!isVoiceActive) {
      setIsVoiceActive(true);
      recognition.start();
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setIsVoiceActive(false);
        onSendMessage(transcript);
      };
      recognition.onerror = () => setIsVoiceActive(false);
      recognition.onend = () => setIsVoiceActive(false);
    } else {
      setIsVoiceActive(false);
      recognition.stop();
    }
  };

  const predefinedPrompts = [
    'Why is E-102 being flagged?',
    'Show current fouling state.',
    'Can I trust this forecast?',
    'Show me the evidence.',
  ];

  return (
    <aside className="w-80 bg-[#071018] border-l border-[#15212d] flex flex-col h-full text-xs z-10 shadow-2xl">
      {/* Copilot Header */}
      <div className="p-3 bg-[#0b1118] border-b border-[#15212d] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-[#27b7e8]" />
          <div>
            <h2 className="font-extrabold uppercase text-white tracking-wider text-xs">FOUL-X COPILOT</h2>
            <p className="text-[10px] text-[#6b7280]">Plant-Aware Engineering Assistant</p>
          </div>
        </div>

        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase bg-[#101923] text-[#27b7e8] border border-[#1b2a3a]">
          M4.0 RIDGE
        </span>
      </div>

      {/* Asset & Context Badge */}
      <div className="p-3 bg-[#090e15] border-b border-[#15212d] grid grid-cols-2 gap-2 text-[10px] font-mono">
        <div>
          <span className="text-[#6b7280] block uppercase">CURRENT ASSET</span>
          <span className="font-bold text-white">{selectedAssetTag}</span>
        </div>
        <div>
          <span className="text-[#6b7280] block uppercase">TRUST GATE</span>
          <span className={`font-bold ${scenario === 'normal' ? 'text-[#34d399]' : 'text-[#f87171]'}`}>
            {scenario === 'normal' ? '✓ SUPPORTED' : '✕ ABSTAINED'}
          </span>
        </div>
      </div>

      {/* Microphone / Voice Control Card */}
      <div className="p-3 border-b border-[#15212d] bg-[#0b1118]">
        <div className="flex items-center justify-between bg-[#101923] p-2.5 rounded border border-[#1b2a3a]">
          <div className="flex items-center gap-2">
            <button
              onClick={toggleVoice}
              className={`p-2 rounded-full transition cursor-pointer ${
                isVoiceActive
                  ? 'bg-[#ef4444] text-white animate-pulse shadow-lg'
                  : 'bg-[#1e293b] text-[#27b7e8] hover:bg-[#283850]'
              }`}
            >
              {isVoiceActive ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
            <div>
              <span className="font-bold text-white block text-[11px]">
                {isVoiceActive ? 'LISTENING...' : 'VOICE ASSISTANT'}
              </span>
              <span className="text-[9px] text-[#6b7280]">Tap mic to speak</span>
            </div>
          </div>

          {scenario === 'disturbed' && (
            <button
              onClick={openEvidenceOverlay}
              className="px-2 py-1 bg-[#1e293b] hover:bg-[#2d3f5e] text-[#27b7e8] font-bold rounded text-[10px] border border-[#27b7e8] cursor-pointer"
            >
              EVIDENCE
            </button>
          )}
        </div>
      </div>

      {/* Chat / Response History */}
      <div className="flex-1 p-3 overflow-y-auto space-y-3">
        {state.copilotHistory.map((item, idx) => (
          <div
            key={idx}
            className={`p-2.5 rounded text-xs space-y-1 ${
              item.sender === 'USER'
                ? 'bg-[#15212d] text-white ml-4 border border-[#1f2f40]'
                : 'bg-[#0b131c] text-[#d1d5db] mr-4 border border-[#162332]'
            }`}
          >
            <div className="flex items-center justify-between text-[9px] text-[#6b7280]">
              <span className="font-bold uppercase flex items-center gap-1">
                {item.sender === 'USER' ? <User className="w-3 h-3 text-[#94a3b8]" /> : <Bot className="w-3 h-3 text-[#27b7e8]" />}
                {item.sender}
              </span>
              <span>{item.timestamp}</span>
            </div>
            <p className="leading-relaxed">{item.text}</p>
          </div>
        ))}
      </div>

      {/* Suggested Prompts */}
      <div className="p-2 bg-[#090e15] border-t border-[#15212d] flex flex-wrap gap-1">
        {predefinedPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => onSendMessage(prompt)}
            className="text-[10px] bg-[#101923] hover:bg-[#182636] text-[#9ca3af] hover:text-white px-2 py-1 rounded border border-[#1b2a3a] transition cursor-pointer"
          >
            "{prompt}"
          </button>
        ))}
      </div>

      {/* Text Input Form */}
      <form onSubmit={handleSend} className="p-3 bg-[#071018] border-t border-[#15212d] flex items-center gap-2">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask FOUL-X about this asset..."
          className="flex-1 bg-[#0b1118] border border-[#15212d] rounded px-3 py-1.5 text-xs text-white placeholder-[#4b5563] focus:outline-none focus:border-[#27b7e8]"
        />
        <button
          type="submit"
          className="p-1.5 bg-[#1b2a3a] hover:bg-[#27b7e8] text-[#27b7e8] hover:text-black font-bold rounded transition cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </aside>
  );
};
