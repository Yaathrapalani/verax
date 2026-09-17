import type { ExchangerState, ForecastMetrics, ForecastPoint, HorizonHours, ReliabilityState, ScenarioMode } from '../types/foulx';
import { INITIAL_EXCHANGERS, REAL_M4_METRICS, generateTrajectory, getReliabilityState } from '../data/demoData';

export class FoulXApiService {
  private activeScenario: ScenarioMode = 'normal';

  public setScenario(scenario: ScenarioMode): void {
    this.activeScenario = scenario;
  }

  public getScenario(): ScenarioMode {
    return this.activeScenario;
  }

  public async getExchangers(): Promise<Record<string, ExchangerState>> {
    const copy = { ...INITIAL_EXCHANGERS };
    if (this.activeScenario === 'disturbed') {
      copy.E02 = {
        ...copy.E02,
        status: 'DEGRADATION_DETECTED',
        thermalDiscrepancy: 0.048,
      };
    }
    return copy;
  }

  public async getExchangerState(exchangerId: string): Promise<ExchangerState> {
    const exchangers = await this.getExchangers();
    return exchangers[exchangerId] || exchangers.E01;
  }

  public async getForecastTrajectory(exchangerId: string, horizonHours: HorizonHours): Promise<ForecastPoint[]> {
    return generateTrajectory(exchangerId, horizonHours);
  }

  public async getForecastMetrics(exchangerId: string, horizonHours: HorizonHours): Promise<ForecastMetrics> {
    const exMetrics = REAL_M4_METRICS[exchangerId] || REAL_M4_METRICS.E01;
    return exMetrics[horizonHours] || exMetrics[1];
  }

  public async getReliabilityState(): Promise<ReliabilityState> {
    return getReliabilityState(this.activeScenario);
  }
}

export const apiService = new FoulXApiService();
