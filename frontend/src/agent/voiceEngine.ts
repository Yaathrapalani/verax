/**
 * PLANT-X Natural Voice Engine
 * Handles Speech-to-Text (STT) and Speech-to-Text (TTS) with instant Barge-in / Interruption support.
 */

export type VoiceState = 'IDLE' | 'LISTENING' | 'SPEAKING' | 'ERROR';

export class VoiceEngine {
  private recognition: any = null;
  private isListening: boolean = false;
  private isSpeaking: boolean = false;
  private onTranscriptCallback: ((text: string) => void) | null = null;
  private onStateChangeCallback: ((state: VoiceState) => void) | null = null;

  public isCurrentlySpeaking(): boolean {
    return this.isSpeaking;
  }

  constructor() {
    this.initRecognition();
  }

  private initRecognition() {
    if (typeof window === 'undefined') return;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'en-US';
      this.recognition.interimResults = false;
      this.recognition.continuous = false;

      this.recognition.onstart = () => {
        this.isListening = true;
        this.notifyState('LISTENING');
      };

      this.recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        this.isListening = false;
        this.notifyState('IDLE');
        if (this.onTranscriptCallback) {
          this.onTranscriptCallback(transcript);
        }
      };

      this.recognition.onerror = () => {
        this.isListening = false;
        this.notifyState('ERROR');
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.notifyState('IDLE');
      };
    }
  }

  public setOnTranscript(cb: (text: string) => void) {
    this.onTranscriptCallback = cb;
  }

  public setOnStateChange(cb: (state: VoiceState) => void) {
    this.onStateChangeCallback = cb;
  }

  private notifyState(state: VoiceState) {
    if (this.onStateChangeCallback) {
      this.onStateChangeCallback(state);
    }
  }

  public startListening(): boolean {
    // Barge-in: If agent is speaking, stop immediately when user begins speaking
    this.stopSpeaking();

    if (!this.recognition) {
      return false;
    }

    try {
      this.recognition.start();
      return true;
    } catch {
      return false;
    }
  }

  public stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
      this.notifyState('IDLE');
    }
  }

  /**
   * Natural speech synthesis with Barge-in
   */
  public speak(text: string, onEnd?: () => void) {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      if (onEnd) onEnd();
      return;
    }

    // Cancel any ongoing speech (Barge-in / interruption)
    this.stopSpeaking();

    if (!text.trim()) {
      if (onEnd) onEnd();
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05; // Calm, professional cadence
    utterance.pitch = 0.95; // Technical, serious tone
    utterance.lang = 'en-US';

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.notifyState('SPEAKING');
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.notifyState('IDLE');
      if (onEnd) onEnd();
    };

    utterance.onerror = () => {
      this.isSpeaking = false;
      this.notifyState('IDLE');
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  }

  /**
   * Immediate Barge-in interruption
   */
  public stopSpeaking() {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    this.isSpeaking = false;
  }

  public isVoiceSupported(): boolean {
    return typeof window !== 'undefined' && Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
  }
}

export const voiceEngine = new VoiceEngine();
