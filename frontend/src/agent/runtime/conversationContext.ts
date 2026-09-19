/**
 * PLANT-X Structured Conversation Context.
 * 
 * Tracks conversational anchors, entity stacks, hypotheses, and modes.
 * Avoids dumping raw transcript strings; resolves pronouns through structured state.
 */

export type ConversationalMode =
  | 'NAVIGATION'
  | 'INVESTIGATION'
  | 'EXPLANATION'
  | 'SIMULATION'
  | 'DESIGN'
  | 'DEBUGGING'
  | 'DEMONSTRATION'
  | 'JUDGE'
  | 'TEACHING'
  | 'REVIEW';

export interface ConversationContextData {
  currentEntity: string | null;
  previousEntities: string[];
  activeStream: string | null;
  activeScenario: string | null;
  activeStudy: string | null;
  activeHypothesis: string | null;
  activeEvidence: string | null;
  lastAction: string | null;
  lastResult: string | null;
  pendingAction: string | null;
  pendingTimer: { scenario: string; secondsRemaining: number } | null;
  unresolvedReferences: string[];
  conversationMode: ConversationalMode;
  contextVersion: number;
}

export class ConversationContext {
  private data: ConversationContextData = {
    currentEntity: 'E-102',
    previousEntities: [],
    activeStream: null,
    activeScenario: null,
    activeStudy: null,
    activeHypothesis: 'H1',
    activeEvidence: null,
    lastAction: null,
    lastResult: null,
    pendingAction: null,
    pendingTimer: null,
    unresolvedReferences: [],
    conversationMode: 'NAVIGATION',
    contextVersion: 1,
  };

  public getSnapshot(): Readonly<ConversationContextData> {
    return { ...this.data, previousEntities: [...this.data.previousEntities] };
  }

  public getVersion(): number {
    return this.data.contextVersion;
  }

  public setEntity(entityId: string) {
    if (this.data.currentEntity && this.data.currentEntity !== entityId) {
      this.data.previousEntities.unshift(this.data.currentEntity);
      if (this.data.previousEntities.length > 5) {
        this.data.previousEntities.pop();
      }
    }
    this.data.currentEntity = entityId;
    this.data.contextVersion++;
  }

  public resolvePronoun(pronoun: 'its' | 'this' | 'that' | 'the other one'): string | null {
    if (pronoun === 'its' || pronoun === 'this' || pronoun === 'that') {
      return this.data.currentEntity;
    }
    if (pronoun === 'the other one') {
      return this.data.previousEntities[0] || (this.data.currentEntity === 'E-102' ? 'E-101' : 'E-102');
    }
    return null;
  }

  public setMode(mode: ConversationalMode) {
    this.data.conversationMode = mode;
    this.data.contextVersion++;
  }

  public setScenario(scenario: string | null) {
    this.data.activeScenario = scenario;
    this.data.contextVersion++;
  }

  public setHypothesis(hId: string | null) {
    this.data.activeHypothesis = hId;
    this.data.contextVersion++;
  }

  public setPendingTimer(timer: { scenario: string; secondsRemaining: number } | null) {
    this.data.pendingTimer = timer;
    this.data.contextVersion++;
  }

  public recordAction(action: string, result?: string) {
    this.data.lastAction = action;
    if (result) this.data.lastResult = result;
    this.data.contextVersion++;
  }

  public inferModeFromUtterance(text: string): ConversationalMode {
    const lower = text.toLowerCase();
    if (/^(what is|who is|explain|describe|tell me about)/.test(lower)) return 'EXPLANATION';
    if (/^(why|what caused|investigate|hypothes|evidence|gap|diagnos)/.test(lower)) return 'INVESTIGATION';
    if (/^(simulate|what happens if|scenario|perturb|what if)/.test(lower)) return 'SIMULATION';
    if (/^(challenge me|quiz|judge|test me)/.test(lower)) return 'JUDGE';
    if (/^(demo|demonstrate|show me everything|walkthrough)/.test(lower)) return 'DEMONSTRATION';
    if (/^(blueprint|p&id|extract|ingest|review)/.test(lower)) return 'REVIEW';
    if (/^(show|go to|take me to|select|focus|trace|zoom|open)/.test(lower)) return 'NAVIGATION';
    return this.data.conversationMode;
  }
}
