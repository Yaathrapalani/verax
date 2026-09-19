import type {
  ApiState,
  HealthCheckResponse,
  ReplayManifestResponse,
  ReplaySnapshotDTO,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class PlantApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  public async fetchHealth(): Promise<ApiState<HealthCheckResponse>> {
    const timestamp = new Date().toISOString();
    try {
      const res = await fetch(`${this.baseUrl}/health`);
      if (!res.ok) {
        return {
          status: 'ERROR',
          data: null,
          error: `HTTP Error ${res.status}: ${res.statusText}`,
          timestamp,
        };
      }
      const data = await res.json();
      return { status: 'SUCCESS', data, error: null, timestamp };
    } catch (err: any) {
      return {
        status: 'UNAVAILABLE',
        data: null,
        error: err?.message || 'Backend API unreachable',
        timestamp,
      };
    }
  }

  public async fetchManifest(): Promise<ApiState<ReplayManifestResponse>> {
    const timestamp = new Date().toISOString();
    try {
      const res = await fetch(`${this.baseUrl}/api/manifest`);
      if (!res.ok) {
        return {
          status: 'ERROR',
          data: null,
          error: `HTTP Error ${res.status}`,
          timestamp,
        };
      }
      const data = await res.json();
      return { status: 'SUCCESS', data, error: null, timestamp };
    } catch (err: any) {
      return {
        status: 'UNAVAILABLE',
        data: null,
        error: err?.message || 'Backend API unreachable',
        timestamp,
      };
    }
  }

  public async fetchExchangers(): Promise<ApiState<Record<string, string>>> {
    const timestamp = new Date().toISOString();
    try {
      const res = await fetch(`${this.baseUrl}/api/exchangers`);
      if (!res.ok) {
        return {
          status: 'ERROR',
          data: null,
          error: `HTTP Error ${res.status}`,
          timestamp,
        };
      }
      const data = await res.json();
      return { status: 'SUCCESS', data, error: null, timestamp };
    } catch (err: any) {
      return {
        status: 'UNAVAILABLE',
        data: null,
        error: err?.message || 'Backend API unreachable',
        timestamp,
      };
    }
  }

  public async fetchSnapshot(
    timeHr: number,
    exchangerId: string = 'E02',
    scenario: 'NORMAL' | 'SHIFTED' = 'NORMAL'
  ): Promise<ApiState<ReplaySnapshotDTO>> {
    const timestamp = new Date().toISOString();
    try {
      const url = `${this.baseUrl}/api/replay/snapshot?time_hr=${timeHr}&exchanger_id=${exchangerId}&scenario=${scenario}`;
      const res = await fetch(url);
      if (!res.ok) {
        return {
          status: 'ERROR',
          data: null,
          error: `HTTP Error ${res.status}: ${res.statusText}`,
          timestamp,
        };
      }
      const data = await res.json();
      return { status: 'SUCCESS', data, error: null, timestamp };
    } catch (err: any) {
      return {
        status: 'UNAVAILABLE',
        data: null,
        error: err?.message || 'Backend API unreachable',
        timestamp,
      };
    }
  }
}

export const apiClient = new PlantApiClient();
