# PLANT-X Voice Runtime & Pipeline Specification

## 1. End-to-End Audio & Command Pipeline

```
Operator Utterance
  │
  ▼
[1] Microphone Capture (Web Audio API / navigator.mediaDevices.getUserMedia)
    • Channel: 1 (mono)
    • Sample Rate: 16,000 Hz (downsampled if hardware is 44.1k/48k)
    • Audio Processing: echoCancellation: true, noiseSuppression: true
    • Buffer: 4096-sample chunks via ScriptProcessorNode / AudioWorklet
  │
  ▼
[2] Voice Activity Detection (VAD) & Energy Computation
    • Energy: Root Mean Square (RMS) calculation over PCM Float32 buffer
    • Threshold: 0.015 RMS for speech onset detection
    • Speech Start -> triggers TurnState: USER_SPEAKING
    • Speech Stop -> triggers TurnState: IDLE / PROCESSING
  │
  ▼
[3] Barge-In Interruption Handler
    • If TurnState is MODEL_SPEAKING and user energy > threshold:
      Immediately invoke stopSpeech() and clear Web Audio playback buffer
  │
  ▼
[4] Voice Provider Dispatch
    • GeminiLiveProvider (Websocket bidirectional stream, ephemeral tokens)
    • BrowserSpeechFallbackProvider (Web Speech API SpeechRecognition / SpeechSynthesis)
    • TextOnlyProvider (Command prompt fallback)
    • DemoVoiceProvider (Offline pre-recorded voice simulation)
  │
  ▼
[5] Intent Resolution & Structured Context Parser
    • IntentParser.parse(utterance, state)
    • Resolves pronouns ("it", "that exchanger", "its fouling state")
    • Matches canonical tags (E-102, E02 -> E-102)
    • Identifies follow-up questions ("Why?", "What's missing?", "What should I investigate next?")
    • Identifies screen-aware queries ("What am I looking at?", "What can I do here?")
  │
  ▼
[6] Epistemic Safety & Truth Firewall
    • Validates claim truth state before committing to output
    • Rejects hallucinated capabilities or direct actuator setpoint modifications
  │
  ▼
[7] Deterministic Tool Execution
    • ToolRegistry execution with state delta generation
    • State version validation to reject stale asynchronous results
  │
  ▼
[8] Synchronous State Projection & Response Generation
    • State updater updates WorkstationShell state
    • Audio playback response synthesized / streamed to operator
```

## 2. Session Lifecycle & Resumption

1. **Initialization**: On application mount, `VoiceAssistantController` registers the authoritative workstation state and binds keyboard shortcut `Ctrl/Cmd + K`.
2. **Audio Capture**: Initiated explicitly by clicking the microphone button or pressing `Cmd+K`. The assistant is **always available, never secretly recording**.
3. **Disconnection Recovery**: If a WebSocket or network connection drops, the session controller caches recent turn history, active asset tag, and scenario version, allowing seamless reconnect without replaying stale commands.
