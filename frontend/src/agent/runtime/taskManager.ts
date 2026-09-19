/**
 * PLANT-X Unified Task Manager.
 * 
 * Manages the lifecycle of delayed operations, scenarios, investigations,
 * and computational tasks with strict pre-execution revalidation.
 */

export type TaskLifecycleState =
  | 'QUEUED'
  | 'RUNNING'
  | 'PAUSED'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'FAILED'
  | 'ABORTED'
  | 'EXPIRED';

export interface WorkstationTask {
  id: string;
  type: 'TIMER' | 'SCENARIO' | 'INVESTIGATION' | 'BENCHMARK' | 'DEMO';
  description: string;
  state: TaskLifecycleState;
  startTime: number;
  scheduledExecuteTime?: number;
  expectedStateSnapshot?: Record<string, unknown>;
  progressPercent: number;
  cancellable: boolean;
  cancelReason?: string;
  result?: Record<string, unknown>;
  error?: string;
}

export class TaskManager {
  private tasks: Map<string, WorkstationTask> = new Map();
  private listeners: Array<(tasks: WorkstationTask[]) => void> = [];

  public getTasks(): WorkstationTask[] {
    return Array.from(this.tasks.values());
  }

  public getTask(id: string): WorkstationTask | undefined {
    return this.tasks.get(id);
  }

  public onTasksChange(listener: (tasks: WorkstationTask[]) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify() {
    const list = this.getTasks();
    for (const l of this.listeners) l(list);
  }

  public createTask(task: Omit<WorkstationTask, 'progressPercent' | 'state'>): WorkstationTask {
    const newTask: WorkstationTask = {
      ...task,
      state: 'QUEUED',
      progressPercent: 0,
    };
    this.tasks.set(newTask.id, newTask);
    this.notify();
    return newTask;
  }

  public updateTask(id: string, updates: Partial<WorkstationTask>): WorkstationTask | undefined {
    const existing = this.tasks.get(id);
    if (!existing) return undefined;
    const updated = { ...existing, ...updates };
    this.tasks.set(id, updated);
    this.notify();
    return updated;
  }

  public cancelTask(id: string, reason: string = 'User cancellation'): boolean {
    const task = this.tasks.get(id);
    if (!task) return false;
    if (!task.cancellable) return false;
    if (task.state === 'COMPLETED' || task.state === 'CANCELLED' || task.state === 'FAILED') return false;

    task.state = 'CANCELLED';
    task.cancelReason = reason;
    this.notify();
    return true;
  }

  /**
   * Revalidates snapshot context prior to executing delayed task.
   * If current project state deviated from expected state, aborts execution.
   */
  public validateBeforeExecution(id: string, currentState: Record<string, unknown>): { valid: boolean; abortReason?: string } {
    const task = this.tasks.get(id);
    if (!task) return { valid: false, abortReason: 'Task not found' };
    if (!task.expectedStateSnapshot) return { valid: true };

    for (const [key, val] of Object.entries(task.expectedStateSnapshot)) {
      if (currentState[key] !== val) {
        task.state = 'ABORTED';
        task.cancelReason = `Pre-execution validation failed: ${key} changed from ${val} to ${currentState[key]}.`;
        this.notify();
        return {
          valid: false,
          abortReason: task.cancelReason,
        };
      }
    }

    return { valid: true };
  }
}
