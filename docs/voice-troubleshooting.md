# PLANT-X Voice System Troubleshooting & Diagnostic Guide

## 1. Common Operational Faults and Remediations

| Symptom | Probable Cause | Remediation / System Behavior |
| :--- | :--- | :--- |
| **Microphone Permission Denied** | User blocked audio permissions in browser settings. | System displays error modal and falls back to text command bar (`Ctrl+K`). Check browser permissions for `localhost` or workstation domain. |
| **Voice Backend Not Configured** | `GEMINI_API_KEY` is not set in backend environment. | System displays `VOICE BACKEND NOT CONFIGURED` and seamlessly transitions to `BrowserSpeechFallbackProvider` or `DemoVoiceProvider`. Ephemeral tokens are not minted. |
| **Speech Recognition Hangs** | Browser's remote Web Speech API service unreachable or disabled. | Switch to `TextOnlyProvider` or `DemoVoiceProvider` using the provider dropdown in the persistent control bar. |
| **Audio Playback Not Hearing** | Browser AudioContext suspended due to autoplay policy. | AudioContext resumes automatically upon user gesture (`Cmd+K` or Mic click). |
| **Stale State Overwrite on Delayed Action** | Scenario timer completed after user manually switched equipment tag. | State Versioning & Pre-Execution Revalidation: `TimerService` detects asset tag mismatch and cancels execution safely to prevent overwriting new context. |
| **Pronoun Ambiguity** | User says "Focus on it" before selecting any equipment. | System returns clarification prompt: *"Please select an equipment asset or specify tag (e.g., E-102)."* |

## 2. Developer Diagnostic Panel

The workstation voice controller exposes real-time telemetry:
- **Audio Telemetry**: Input RMS energy, Output RMS energy, Buffer underrun/overflow counters, Capture latency (~20ms).
- **VAD State**: Speech start timestamp, speech end timestamp, active speech status.
- **Provider Status**: Active provider (`gemini-live`, `browser-speech`, `text-only`, `demo`), WebSocket connection state, token expiry latency.
- **Turn Inspector**: Recent turns with full utterance, resolved tool, parameter payload, execution latency, and truth state.
