/**
 * PLANT-X Conversational Voice Provider Registry.
 * 
 * Factory and runtime registry for pluggable voice providers.
 */

import type { ConversationalVoiceProvider, VoiceProviderType } from './providerTypes';
import { GeminiLiveProvider } from './geminiLiveProvider';
import { BrowserSpeechFallbackProvider } from './browserSpeechFallbackProvider';
import { TextOnlyProvider, DemoVoiceProvider } from './textOnlyProvider';

export class VoiceProviderRegistry {
  private static instance: VoiceProviderRegistry;
  private currentProvider: ConversationalVoiceProvider;

  private constructor() {
    // Default to BrowserSpeechFallbackProvider or GeminiLiveProvider
    this.currentProvider = new BrowserSpeechFallbackProvider();
  }

  public static getInstance(): VoiceProviderRegistry {
    if (!VoiceProviderRegistry.instance) {
      VoiceProviderRegistry.instance = new VoiceProviderRegistry();
    }
    return VoiceProviderRegistry.instance;
  }

  public getProvider(): ConversationalVoiceProvider {
    return this.currentProvider;
  }

  public setProvider(type: VoiceProviderType): ConversationalVoiceProvider {
    if (this.currentProvider.providerType === type) {
      return this.currentProvider;
    }

    // Disconnect existing
    try {
      this.currentProvider.disconnect();
    } catch { /* ignore */ }

    switch (type) {
      case 'gemini-live':
        this.currentProvider = new GeminiLiveProvider();
        break;
      case 'browser-speech':
        this.currentProvider = new BrowserSpeechFallbackProvider();
        break;
      case 'text-only':
        this.currentProvider = new TextOnlyProvider();
        break;
      case 'demo':
        this.currentProvider = new DemoVoiceProvider();
        break;
      default:
        this.currentProvider = new BrowserSpeechFallbackProvider();
    }

    return this.currentProvider;
  }
}
