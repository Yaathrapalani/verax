/**
 * PLANT-X Procedural Equipment Library.
 * 
 * Defines parameterized canonical 3D models for process equipment classes:
 * HeatExchanger, Pump, Valve, Tank, Vessel, Column, Filter, Compressor, Pipe, Instrument.
 * Models carry ports, LOD boundaries, and explicit representative truth states.
 */

export interface ProceduralGeometryParams {
  type: string;
  tag: string;
  dimensions: {
    length?: number;
    diameter?: number;
    height?: number;
    width?: number;
  };
  color: string;
  truthState: string;
}

export class ProceduralEquipmentLibrary {
  public static getEquipmentGeometry(type: string, tag: string): ProceduralGeometryParams {
    switch (type.toUpperCase()) {
      case 'HEAT_EXCHANGER':
        return {
          type: 'HEAT_EXCHANGER',
          tag,
          dimensions: { length: 3.2, diameter: 1.1 },
          color: '#3b82f6', // industrial blue
          truthState: 'REPRESENTATIVE',
        };

      case 'PUMP':
        return {
          type: 'PUMP',
          tag,
          dimensions: { length: 1.4, width: 1.0, height: 0.9 },
          color: '#10b981', // industrial green
          truthState: 'REPRESENTATIVE',
        };

      case 'VESSEL':
      case 'TANK':
        return {
          type: 'VESSEL',
          tag,
          dimensions: { diameter: 2.2, height: 4.8 },
          color: '#64748b', // industrial slate
          truthState: 'REPRESENTATIVE',
        };

      case 'COLUMN':
        return {
          type: 'COLUMN',
          tag,
          dimensions: { diameter: 2.0, height: 12.0 },
          color: '#475569',
          truthState: 'REPRESENTATIVE',
        };

      case 'VALVE':
        return {
          type: 'VALVE',
          tag,
          dimensions: { width: 0.6, height: 0.8 },
          color: '#f59e0b',
          truthState: 'REPRESENTATIVE',
        };

      default:
        return {
          type: 'GENERIC_EQUIPMENT',
          tag,
          dimensions: { width: 1.5, height: 1.5, length: 1.5 },
          color: '#94a3b8',
          truthState: 'REPRESENTATIVE',
        };
    }
  }
}
