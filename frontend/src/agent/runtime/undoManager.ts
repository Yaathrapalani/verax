/**
 * PLANT-X Reversible Workstation Undo & Snapshot Managers.
 * 
 * Supports undoing reversible UI/workstation actions (selection, route, camera focus,
 * highlighted path, inspector tab) and saving/restoring full workstation snapshots
 * without rewinding authoritative engineering truth.
 */

import type { WorkstationView } from '../types';

export interface WorkstationSnapshot {
  snapshotId: string;
  timestamp: number;
  label: string;
  route: WorkstationView;
  selectedEquipment: string;
  selectedStream: string | null;
  cameraFocusTag: string;
  highlightedPath: string[];
  activeScenario: string | null;
  activeHypothesis: string;
}

export class SnapshotManager {
  private static snapshots: Map<string, WorkstationSnapshot> = new Map();

  public static saveSnapshot(
    label: string,
    state: {
      route: WorkstationView;
      selectedEquipment: string;
      selectedStream: string | null;
      cameraFocusTag: string;
      highlightedPath: string[];
      activeScenario: string | null;
      activeHypothesis: string;
    }
  ): WorkstationSnapshot {
    const snap: WorkstationSnapshot = {
      snapshotId: `snap_${Date.now()}`,
      timestamp: Date.now(),
      label,
      ...state,
      highlightedPath: [...state.highlightedPath],
    };
    this.snapshots.set(snap.snapshotId, snap);
    return snap;
  }

  public static getSnapshot(id: string): WorkstationSnapshot | undefined {
    return this.snapshots.get(id);
  }

  public static getLatestSnapshot(): WorkstationSnapshot | undefined {
    const list = Array.from(this.snapshots.values());
    return list[list.length - 1];
  }
}

export interface ReversibleAction {
  id: string;
  description: string;
  undo: () => void;
  redo?: () => void;
}

export class UndoManager {
  private undoStack: ReversibleAction[] = [];
  private redoStack: ReversibleAction[] = [];

  public pushAction(action: ReversibleAction) {
    this.undoStack.push(action);
    if (this.undoStack.length > 30) this.undoStack.shift();
    this.redoStack = [];
  }

  public undo(): boolean {
    const action = this.undoStack.pop();
    if (!action) return false;
    action.undo();
    this.redoStack.push(action);
    return true;
  }

  public canUndo(): boolean {
    return this.undoStack.length > 0;
  }
}
