# PLANT-X / FOUL-X Voice Regression Forensics Report

## 1. Executive Summary & Timeline

This document provides the forensic investigation into the voice regression in PLANT-X / FOUL-X following the transition from the prototype copilot to the Frontend 2.0 Workstation architecture.

- **KNOWN_GOOD_STATE**: Git commit `5d8abce` (`v0.1.0-rc1`).
  - Voice operated via `FoulXCopilot.tsx` mounted in `App.tsx`, utilizing `window.SpeechRecognition` / `webkitSpeechRecognition`.
  - Spoken queries directly triggered `recognition.onresult`, forwarding transcripts to `handleCopilotMessage()` which updated plant state and produced speech feedback.
- **REGRESSION_POINT**: Integration of `WorkstationShell.tsx` and the multi-provider voice architecture (`VoiceAssistantController`, `RealtimeAudioController`, `GeminiLiveProvider`, `BrowserSpeechFallbackProvider`).
  - The microphone capture was separated into `RealtimeAudioController.startMicrophoneCapture()` using `navigator.mediaDevices.getUserMedia()`.
  - `VoiceAssistantController.startListening()` checked `if (micStarted) return true;` and sent raw PCM chunks to `provider.sendAudio()`.
  - Neither `BrowserSpeechFallbackProvider` nor `GeminiLiveProvider` (unconnected) performed local speech-to-text on those raw PCM chunks.
  - The `SpeechRecognition` fallback branch was bypassed entirely whenever `getUserMedia()` succeeded.
  - As a result, the browser microphone indicator turned on, but speech was never transcribed, resulting in total voice unresponsiveness.
- **CURRENT_STATE**:
  - The root cause is isolated to the audio-to-transcript binding in `VoiceAssistantController` and the lifecycle coordination with `BrowserSpeechFallbackProvider` and `GeminiLiveProvider`.
  - Backend regression tests remain at 523/523 PASS.
  - Frontend test suite contains 60 passing tests.

---

## 2. Voice Diff Map

| File | Before (`5d8abce`) | After (Current State) | Risk Level | Regression Evidence |
| :--- | :--- | :--- | :--- | :--- |
| `frontend/src/App.tsx` | Mounted `FoulXCopilot` directly with `handleCopilotMessage()`. | Replaced by `<WorkstationShell />`. Voice moved to shell level. | HIGH | Decoupled UI from original direct speech callback. |
| `frontend/src/components/copilot/FoulXCopilot.tsx` | Directly invoked `SpeechRecognition.start()` and passed `event.results[0][0].transcript`. | Retained in codebase, but no longer rendered in main layout. | MEDIUM | Known-good voice path was left dormant in unused component. |
| `frontend/src/agent/voiceEngine.ts` | Wrapper around `SpeechRecognition` with basic barge-in. | Superseded by `VoiceAssistantController` without complete STT binding. | HIGH | Callbacks were not receiving transcripts from microphone capture. |
| `frontend/src/agent/voice/RealtimeAudio.ts` | Did not exist. | Implemented Web Audio API, 16 kHz Float32 capture, VAD energy, and barge-in. | HIGH | `getUserMedia` acquired mic stream, but only buffered PCM for streaming, leaving STT unhandled in fallback mode. |
| `frontend/src/agent/voice/VoiceAssistantController.ts` | Did not exist. | Persistent workstation-wide singleton managing turns, intent parsing, tools, and audio. | HIGH | `startListening()` returned early on `micStarted == true`, bypassing speech recognition. |
| `frontend/src/agent/voice/geminiLiveProvider.ts` | Did not exist. | Provider for Gemini Live WebSocket streaming. | MEDIUM | Does not establish raw WebSocket when `GEMINI_API_KEY` is not present; audio sent to null socket. |
| `frontend/src/agent/voice/browserSpeechFallbackProvider.ts` | Did not exist. | Implemented `SpeechRecognition` listener. | MEDIUM | `sendAudio()` is a no-op; was not coordinated with `VoiceAssistantController` mic capture. |
| `src/plantx/voice/session.py` | Did not exist. | FastAPI router for `/api/v1/voice/session` issuing ephemeral tokens. | LOW | Correctly reports `NOT_CONFIGURED` when `GEMINI_API_KEY` is omitted. |

---

## 3. First Broken Transition in Runtime Pipeline

```
USER SPEAKS
  │
  ▼
[MIC_REQUEST] ───────────────► SUCCESS (navigator.mediaDevices.getUserMedia)
  │
  ▼
[MIC_GRANTED] ───────────────► SUCCESS (Hardware audio indicator turns red)
  │
  ▼
[AUDIO_CONTEXT_RUNNING] ─────► SUCCESS (AudioContext state: 'running')
  │
  ▼
[PCM_CAPTURE_STARTED] ───────► SUCCESS (4096-sample Float32 frames emitted)
  │
  ▼
[VAD_SPEECH_START] ──────────► SUCCESS (Energy > 0.015 RMS detected)
  │
  ▼
[TRANSCRIPT_GENERATION] ─────► ❌ BROKEN TRANSITION
```

**Root Cause Detail**:
In `VoiceAssistantController.startListening()`:
```typescript
const micStarted = await realtimeAudioController.startMicrophoneCapture();
if (micStarted) {
  realtimeAudioController.setOnAudioChunk((pcmChunk) => {
    const provider = VoiceProviderRegistry.getInstance().getProvider();
    provider.sendAudio(pcmChunk);
  });
  return true; // <--- EXITS HERE! Never initiates SpeechRecognition!
}
```
When `provider` is `browser-speech`, `sendAudio` is intentionally a no-op because Web Speech API requires its own internal microphone capture. By capturing audio with `getUserMedia` and returning early, the controller never started `SpeechRecognition`, leaving the speech un-transcribed.

---

## 4. Restoration Plan (Phase 7 & 8)

1. **Restore Known-Good Speech Capture**:
   - In `BrowserSpeechFallbackProvider` / `VoiceAssistantController`: When running on browser speech fallback, use the browser's native `SpeechRecognition` instance to capture and transcribe speech directly, exactly as in the known-good state.
   - When running on `GeminiLiveProvider` with an active server WebSocket connection, stream the 16 kHz Float32 PCM chunks directly over the live WebSocket.
2. **Harmonize VAD and Speech Recognition**:
   - Ensure `SpeechRecognition` and `getUserMedia` do not conflict over microphone hardware.
3. **Preserve Workstation-Wide Continuity**:
   - Connect the transcribed output directly to `executeUtterance()`, triggering intent resolution, truth firewall validation, deterministic tool execution, and voice output.
4. **Establish the Golden Path**:
   - Input: Operator says *"Hello"* $\to$ Transcribed $\to$ Assistant greets with workstation readiness.
   - Query: Operator says *"Show me E-102"* $\to$ E-102 selected across all views $\to$ Assistant confirms.
   - Follow-up: Operator says *"Why?"* $\to$ Contextual explanation of E-102 reliability gate status.
