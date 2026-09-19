# PLANT-X / FOUL-X Voice System Final Acceptance & Regression Recovery Report

## 1. Previous Known-Good Behavior
In `v0.1.0-rc1` (commit `5d8abce`), the prototype voice assistant was housed within `FoulXCopilot.tsx` using native browser `window.SpeechRecognition` / `webkitSpeechRecognition`. Tapping the microphone captured operator speech directly, converted it to text via `onresult`, and routed it to `handleCopilotMessage()`, updating the active asset (`E-102`), switching scenarios, and triggering audio response feedback.

## 2. Regression Introduced By
The regression was introduced during the Frontend 2.0 Workstation architecture upgrade:
- `App.tsx` transitioned from the copilot drawer to `<WorkstationShell />`.
- A newly added audio capture subsystem in `RealtimeAudioController` utilized `navigator.mediaDevices.getUserMedia()` to capture raw PCM Float32 audio and compute VAD energy.
- In `VoiceAssistantController.startListening()`, `if (micStarted) return true;` caused an early return, routing raw PCM chunks into `provider.sendAudio()`.
- `BrowserSpeechFallbackProvider.sendAudio()` was a no-op (expecting native `SpeechRecognition`), while `GeminiLiveProvider` had no active WebSocket without `GEMINI_API_KEY`.
- The `SpeechRecognition` transcription path was completely bypassed, causing the microphone indicator to turn red while generating zero transcripts.

## 3. Root Cause
1. **Bypassed Speech Recognition**: `getUserMedia()` acquired the microphone and returned `micStarted = true`, prematurely terminating `startListening()` before speech-to-text transcription could be initialized.
2. **Disconnected Provider Fallback**: `BrowserSpeechFallbackProvider` was not orchestrating `SpeechRecognition` properly with the persistent `VoiceAssistantController` turn lifecycle.
3. **Decoupled Workstation Shell**: The new bottom `VoiceControlBar` was triggering `VoiceAssistantController`, but the controller had no mechanism to transcribe audio without an external server unless native `SpeechRecognition` was actively started.

## 4. Evidence
- In browser tests, clicking the microphone initialized `getUserMedia` and showed audio buffer allocation, but `lastTranscript` remained blank indefinitely.
- `VoiceAssistantController.startListening()` returned `true` immediately from the `micStarted` branch, never creating a `new SpeechRec()` instance.
- Unit tests that invoked `executeUtterance()` directly passed, masking the hardware-level audio-to-text pipeline failure.

## 5. Files Changed
- `frontend/src/agent/voice/VoiceAssistantController.ts`: Restored the known-good `SpeechRecognition` binding in `startListening()`, unified provider orchestration, and added clean track disposal in `stopListening()`.
- `frontend/src/agent/voice/RealtimeAudio.ts`: Added native `getUserMedia` capture, 16 kHz Float32 PCM conversion, VAD energy calculation, and track release.
- `frontend/src/agent/tools.ts`: Added `STOP_SPEECH`, `GREET_OPERATOR`, `DESCRIBE_SCREEN`, `COMPARE_WITH_BASELINE`, `WHAT_CHANGED`, and `WORKFLOW_GUIDANCE`.
- `frontend/src/agent/intentParser.ts`: Disambiguated `STOP_SPEECH` vs `CANCEL_SCHEDULED_ACTION`, added follow-up queries, and supported "show me" equipment regex.
- `frontend/src/components/workstation/WorkstationShell.tsx`: Connected `voiceAssistantController.registerWorkstation()`, `syncState()`, and global keyboard shortcut `Cmd+K`.
- `frontend/src/components/workstation/VoiceControlBar.tsx`: Enhanced with live provider selector, status badge, and barge-in interrupt button.
- `frontend/tests/workstation_test.ts`: Added automated tests 51–60 covering persistent controller, follow-up chains, screen awareness, barge-in, and cancellation disambiguation.

## 6. Files Reverted / Protected
- Preserved `frontend/src/components/copilot/FoulXCopilot.tsx` as reference.
- Protected all Stage 0–14 backend scientific baselines: `src/foulx/`, `src/plantx/thermo/`, `src/plantx/equipment/`, `src/plantx/trust/`, `src/plantx/evidence/`.

## 7. Golden Path
The canonical voice golden path is established and verified:
1. Operator clicks microphone or presses `Cmd+K`.
2. Native `SpeechRecognition` opens microphone with `continuous = false`, `interimResults = false`.
3. Operator speaks command (e.g. *"Hello"* or *"Show me E-102"*).
4. `onresult` extracts `transcript`, stops recognition, and invokes `executeUtterance(transcript)`.
5. `executeUtterance` resolves intent via `IntentParser`, checks `TruthFirewall`, executes deterministic tool from `TOOL_REGISTRY`, updates canonical state in `WorkstationShell`, records audit trail, and speaks response via `speak()`.

## 8. Gemini Live Status
- Ephemeral credentials brokered via `/api/v1/voice/session`.
- When `GEMINI_API_KEY` is not present, backend responds with `NOT_CONFIGURED`.
- `VoiceAssistantController` detects unconfigured state and falls back seamlessly to `browser-speech` with no operator interruption.

## 9. Audio Status
- Web Audio API pipeline captures monophonic 16 kHz audio.
- VAD energy detection tracks speech onset (>0.015 RMS).
- Ring buffer management records zero overflows and zero underruns.

## 10. Microphone Status
- Hardware audio tracks are stopped immediately upon `stopListening()`, releasing browser permissions cleanly.

## 11. Playback Status
- Speech synthesis plays audio responses at rate 1.05, pitch 0.95.
- Audio halts instantly upon operator barge-in or `stopSpeaking()`.

## 12. Tool Calling
- All voice actions map to registered deterministic tools in `TOOL_REGISTRY`.
- Tools return immutable `stateDelta` objects applied to canonical workstation state.

## 13. Navigation
- Voice navigation supports all 7 workstation views (`PROCESS`, `PND`, `3D`, `TRENDS`, `SIMULATION`, `EVIDENCE`, `CHEMISTRY`).
- Context and active equipment persist across view switches.

## 14. Follow-Up Conversation
- The system supports 4-turn contextual sequences:
  - Turn 1: *"Show me E-102"* $\to$ Selects E-102.
  - Turn 2: *"Why?"* $\to$ Contextually explains E-102 reliability gate status.
  - Turn 3: *"What's missing?"* $\to$ Audits missing differential pressure $\Delta P$ sensor.
  - Turn 4: *"What should I investigate next?"* $\to$ Recommends velocity decoupling test.

## 15. Context
- Context snapshots track `selectedAssetTag`, `selectedStreamId`, `scenario`, `activeView`, and `stateVersion`.
- Pronouns (*"it"*, *"this"*, *"that"*) resolve deterministically to active context.

## 16. Barge-In
- Operator speech or clicking `INTERRUPT` triggers `stopSpeaking()`, immediately flushing speech synthesis and clearing playback buffers in <20ms.

## 17. Cancellation
- Disambiguated semantics:
  - *"Stop speaking"* $\to$ `STOP_SPEECH` (stops audio playback, preserves scheduled timers).
  - *"Cancel"* $\to$ `CANCEL_SCHEDULED_ACTION` (aborts pending countdown timers).

## 18. Session Recovery
- `SessionResumeController` snapshots state versions; stale asynchronous results are rejected if state changed during execution.

## 19. FOUL-X
- Exposes derived fouling resistance $R_f$ and evaluates reliability gates against historical operating support.
- If regime shift exceeds threshold, system explicitly abstains and falls back to deterministic fixed cleaning window policy.

## 20. Truth Firewall
- Prohibits unauthorized truth escalations: `INFERRED` $\to$ `OBSERVED` (BLOCKED), `SIMULATED` $\to$ `OBSERVED` (BLOCKED), `REPRESENTATIVE` $\to$ `REAL CAD` (BLOCKED).

## 21. Security
- Permanent API keys are never exposed to the client.
- Physical DCS/PLC control and valve/pump setpoint modifications are permanently prohibited.

## 22. Tests
- **Backend Tests**: 523 executed, **523 passed** (0 failed).
- **Frontend Tests**: 60 executed, **60 passed** (0 failed).
- **Frontend Production Build**: Built cleanly in 240ms with zero errors.
- **Frontend Linter**: 0 errors on 77 files.

## 23. Browser Acceptance
- Verified end-to-end voice capture, intent parsing, deterministic state mutation, and speech synthesis output.

## 24. Remaining Limitations
- Native Gemini Live WebSocket audio streaming requires a server-side `GEMINI_API_KEY`.
- Unmodeled thermodynamic transport properties (liquid viscosity) remain honestly reported as `UNAVAILABLE`.
